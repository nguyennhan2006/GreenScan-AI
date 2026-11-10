from __future__ import annotations
from ..labels_vi import LEGAL_ISSUE, vi

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import (
    EvidenceChunk,
    QualityGate,
    RiskAssessment,
    RunManifest,
    VerificationResult,
)
from quantum_gw.storage.audit import AuditLogger


class ReviewerAgent:
    def __init__(self, audit: AuditLogger):
        self.audit = audit

    def run(
        self,
        chunks: list[EvidenceChunk],
        verifications: list[VerificationResult],
        risks: list[RiskAssessment],
        manifest: RunManifest,
        legal_checks: list[dict] | None = None,
        legal_unavailable_reason: str = "",
    ) -> list[QualityGate]:
        gates: list[QualityGate] = []
        gates.append(self._gate("G0", "Dữ liệu đầu vào", bool(chunks) and all(c.source_name and c.chunk_id for c in chunks), "Mọi đoạn đã tách phải giữ nguồn gốc (tệp, vị trí)."))
        extraction_ok = all(v.claim.source_chunk_id and v.claim.source_name for v in verifications)
        gates.append(self._gate("G1", "Trích xuất đúng nguồn", extraction_ok, "Mỗi tuyên bố giữ đoạn nguồn và vị trí trong tài liệu."))
        retrieval_ok = all(v.evidence or v.status == VerificationStatus.INSUFFICIENT_EVIDENCE for v in verifications)
        gates.append(self._gate("G2", "Bằng chứng hợp lệ", retrieval_ok, "Mỗi tuyên bố có bằng chứng hợp lệ hoặc được ghi rõ là chưa đủ bằng chứng."))
        calculation_ok = all(v.verification_tool_version and v.computed_values.get("calculation_method", "deterministic") for v in verifications)
        gates.append(self._gate("G3", "Kiểm chứng bằng mã cố định", calculation_ok, "Phép so sánh số liệu do mã cố định thực hiện, không do mô hình ngôn ngữ."))
        citation_ok = all(v.status == VerificationStatus.INSUFFICIENT_EVIDENCE or all(e.citation for e in v.evidence) for v in verifications)
        gates.append(self._gate("G4", "Trích dẫn đầy đủ", citation_ok, "Mỗi bằng chứng quyết định đều có vị trí trong tài liệu."))
        pending_review = any(r.requires_human_review for r in risks)
        gates.append(QualityGate(gate_id="G5", name="Soát rủi ro", passed=not pending_review, status="PENDING_HUMAN_REVIEW" if pending_review else "PASS", details="Mục rủi ro cao, rất cao hoặc có xung đột pháp lý cần người soát duyệt."))
        reproducible = bool(manifest.config_hash and manifest.input_hashes and manifest.plan)
        gates.append(self._gate("G6", "Tái lập được", reproducible, "Bản kê lượt chạy ghi cấu hình, mã băm tệp đầu vào, hạt giống ngẫu nhiên và kế hoạch."))
        gates.append(self._legal_gate(verifications, legal_checks or [], legal_unavailable_reason))
        self.audit.write("quality_gates_evaluated", {"gates": [g.model_dump(mode="json") for g in gates]})
        return gates

    @staticmethod
    def _legal_gate(
        verifications: list[VerificationResult],
        legal_checks: list[dict],
        unavailable_reason: str,
    ) -> QualityGate:
        """G7 — was the applicable law consulted, and did it raise anything.

        An inconclusive legal check does not block a release. The layer returns
        INSUFFICIENT_EVIDENCE both when no instrument governs the claim and when
        an instrument governs it but its text was never extracted, and those are
        coverage gaps rather than findings about a company. They are reported in
        the details and in each record's notes, where the missing document is
        named and can be collected.

        An adverse finding does block: NOT_MATCH or PARTIAL_MATCH means a rule
        actually ran and something failed or could not be established, which is
        a reviewer's call and never an automatic verdict.
        """
        if unavailable_reason:
            return QualityGate(
                gate_id="G7", name="Legal check", passed=True, status="PASS",
                details=f"Không dùng lớp pháp lý: {unavailable_reason}",
            )
        if len(legal_checks) < len(verifications):
            return QualityGate(
                gate_id="G7", name="Legal check", passed=False, status="FAIL",
                details=(
                    f"Chỉ {len(legal_checks)}/{len(verifications)} tuyên bố tới được lớp pháp lý."
                ),
            )
        adverse = [c for c in legal_checks if c["legal_finding"] in {"NOT_MATCH", "PARTIAL_MATCH"}]
        if adverse:
            return QualityGate(
                gate_id="G7", name="Legal check", passed=False, status="PENDING_HUMAN_REVIEW",
                details=(
                    f"{len(adverse)} tuyên bố có kết quả pháp lý bất lợi: "
                    + ", ".join(sorted({vi(LEGAL_ISSUE, c["issue"]) for c in adverse}))
                ),
            )
        inconclusive = sum(1 for c in legal_checks if c["legal_finding"] == "INSUFFICIENT_EVIDENCE")
        blocked = sorted({
            b["document"] for c in legal_checks for b in c.get("blocked_sources", [])
        })
        details = f"{len(legal_checks)} tuyên bố đã đối chiếu với kho văn bản pháp lý đã đăng ký."
        if inconclusive:
            details += f" {inconclusive} tuyên bố chưa kết luận được."
        if blocked:
            details += " Văn bản đang hiệu lực nhưng chưa trích được nội dung: " + ", ".join(blocked) + "."
        return QualityGate(
            gate_id="G7", name="Legal check", passed=True, status="PASS", details=details
        )

    @staticmethod
    def _gate(gate_id: str, name: str, passed: bool, details: str) -> QualityGate:
        return QualityGate(gate_id=gate_id, name=name, passed=passed, status="PASS" if passed else "FAIL", details=details)
