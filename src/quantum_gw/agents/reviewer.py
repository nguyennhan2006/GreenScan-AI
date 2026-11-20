from __future__ import annotations

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import (
    EvidenceChunk,
    QualityGate,
    RiskAssessment,
    RunManifest,
    VerificationResult,
)
from quantum_gw.parsers.ocr import LOW_PAGE_CONF
from quantum_gw.storage.audit import AuditLogger

from ..labels_vi import LEGAL_ISSUE, vi


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
        integrity: list[dict] | None = None,
        reading: list[dict] | None = None,
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
        gates.append(self._integrity_gate(integrity or [], verifications))
        gates.append(self._reading_gate(reading or [], verifications))
        self.audit.write("quality_gates_evaluated", {"gates": [g.model_dump(mode="json") for g in gates]})
        return gates

    @staticmethod
    def _integrity_gate(findings: list[dict], verifications: list[VerificationResult]) -> QualityGate:
        """G8 — did any input carry text a reader cannot see, or sentences addressed to the grader.

        Either is an attempt, or at least an opening, to steer an automated
        review; the text has already been kept out of the analysis (hidden text
        removed at parsing, passages excluded from evidence, claims withheld
        from any model), and what remains is for a person to look at the page.
        """
        planted = [f for f in findings if f["kind"] == "instruction"]
        hidden = [f for f in findings if f["kind"] == "hidden_text" and f.get("blocking", True)]
        tiny = [f for f in findings if f["kind"] == "hidden_text" and not f.get("blocking", True)]
        # A claim the model flagged although no pattern did (a phrasing the list lacks).
        model_flagged = 0 if planted else sum(1 for v in verifications if v.suspected_injection)
        if not planted and not hidden and not model_flagged:
            note = (f" Đã loại {len(tiny)} vùng chữ cỡ dưới 2 pt khỏi văn bản phân tích ({_where(tiny)}): thường là "
                    "chữ ký số hoặc trang thu nhỏ, không có lời nhắn tới máy chấm.") if tiny else ""
            return QualityGate(gate_id="G8", name="Toàn vẹn tài liệu", passed=True, status="PASS",
                               details="Không thấy chữ ẩn hay câu nhắn tới hệ thống chấm tự động trong tài liệu đầu vào."
                               + note)
        parts = []
        if planted:
            parts.append(f"{len(planted)} đoạn nhắn tới hệ thống chấm tự động ({_where(planted)})")
        if hidden:
            parts.append(f"{len(hidden)} vùng chữ người đọc không thấy được ({_where(hidden)})")
        if model_flagged:
            parts.append(f"{model_flagged} tuyên bố mà mô hình ngôn ngữ báo có lời nhắn tới nó")
        return QualityGate(
            gate_id="G8", name="Toàn vẹn tài liệu", passed=False, status="PENDING_HUMAN_REVIEW",
            details="Phát hiện " + "; ".join(parts) + ". Chữ ẩn đã bị loại khỏi văn bản phân tích; đoạn có lời nhắn "
                    "bị loại khỏi bằng chứng và không được đưa cho mô hình ngôn ngữ. Người soát mở trang gốc để "
                    "xem doanh nghiệp có cố tác động tới máy chấm hay không.",
        )

    @staticmethod
    def _reading_gate(reading: list[dict], verifications: list[VerificationResult]) -> QualityGate:
        """G9 — how much of the input could be read, and how sure the reading is.

        A scanned page is read by OCR, which gives each word a confidence
        (parsers/ocr.py); a text layer from a legacy Vietnamese font is garbled
        and read by OCR too (parsers/text_quality.py). A person needs to know
        which pages were read that way and how well, which could not be read at
        all, and which findings rest on a number OCR was unsure of. Only the last
        two hold the release: a weak page is reported, and its numbers are
        already kept out of every verdict (agents/verifier.py _unless_misread).
        """
        name = "Chất lượng đọc tài liệu"
        if not reading:
            return QualityGate(gate_id="G9", name=name, passed=True, status="PASS",
                               details="Mọi trang có lớp chữ gốc đọc được; không trang nào phải đọc bằng OCR.")
        ocr_pages = [r for r in reading if r.get("ocr")]
        confidences = [r["ocr_confidence"] for r in ocr_pages if r.get("ocr_confidence") is not None]
        weak = [r for r in ocr_pages if r.get("ocr_confidence") is not None and r["ocr_confidence"] < LOW_PAGE_CONF]
        garbled = [r for r in reading if r.get("native_text_garbled")]
        unread = [r for r in reading if r.get("unread")]
        leaning = [v for v in verifications if v.doubtful_reading]
        parts = []
        if ocr_pages:
            spread = (f", độ tin cậy trung bình mỗi trang từ {min(confidences):.0f} đến {max(confidences):.0f}/100"
                      if confidences else "")
            parts.append(f"{len(ocr_pages)} trang đọc bằng OCR ({_where(ocr_pages)}){spread}")
        if weak:
            parts.append(f"{len(weak)} trang có độ tin cậy dưới {LOW_PAGE_CONF:.0f}/100, chữ có thể bị đọc sai hoặc "
                         f"bỏ sót ({_where(weak)})")
        if garbled:
            parts.append(f"{len(garbled)} trang có lớp chữ lỗi mã do phông chữ tiếng Việt cũ ({_where(garbled)})")
        if unread:
            parts.append(f"{len(unread)} trang là ảnh quét hoặc chữ lỗi mã nhưng chưa đọc được vì OCR chưa bật hoặc "
                         f"chưa cài; nội dung các trang này không có trong phân tích ({_where(unread)})")
        if leaning:
            parts.append(f"{len(leaning)} tuyên bố có số liệu OCR đọc với độ tin cậy thấp; mọi so khớp số liệu dựa "
                         "trên các số đó đã bị hạ xuống khớp một phần")
        held = bool(unread or leaning)
        return QualityGate(
            gate_id="G9", name=name, passed=not held, status="PENDING_HUMAN_REVIEW" if held else "PASS",
            details="; ".join(parts) + "." + (" Người soát đối chiếu các trang trên với tệp gốc." if held else ""),
        )

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


def _where(findings: list[dict]) -> str:
    """"tệp A tr. 3, 5; tệp B tr. 2" — where a reviewer should look, at most six pages per file."""
    pages: dict[str, list[str]] = {}
    for f in findings:
        listed = pages.setdefault(f.get("source_name") or "?", [])
        page = str(f.get("page")) if f.get("page") else "?"
        if page not in listed:
            listed.append(page)
    return "; ".join(
        f"{name} tr. {', '.join(p[:6])}{'…' if len(p) > 6 else ''}" for name, p in pages.items()
    )
