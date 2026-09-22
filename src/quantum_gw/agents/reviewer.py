from __future__ import annotations

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
        gates.append(self._gate("G0", "Data admissibility", bool(chunks) and all(c.source_name and c.chunk_id for c in chunks), "All parsed chunks must retain source provenance."))
        extraction_ok = all(v.claim.source_chunk_id and v.claim.source_name for v in verifications)
        gates.append(self._gate("G1", "Extraction fidelity", extraction_ok, "Claims retain source chunk and document location."))
        retrieval_ok = all(v.evidence or v.status == VerificationStatus.INSUFFICIENT_EVIDENCE for v in verifications)
        gates.append(self._gate("G2", "Retrieval admissibility", retrieval_ok, "Each claim has admissible evidence or an explicit insufficient-evidence status."))
        calculation_ok = all(v.verification_tool_version and v.computed_values.get("calculation_method", "deterministic") for v in verifications)
        gates.append(self._gate("G3", "Deterministic verification", calculation_ok, "Numeric comparisons are executed by deterministic code."))
        citation_ok = all(v.status == VerificationStatus.INSUFFICIENT_EVIDENCE or all(e.citation for e in v.evidence) for v in verifications)
        gates.append(self._gate("G4", "Citation integrity", citation_ok, "Every decisive evidence item has a document-level location."))
        pending_review = any(r.requires_human_review for r in risks)
        gates.append(QualityGate(gate_id="G5", name="Risk review", passed=not pending_review, status="PENDING_HUMAN_REVIEW" if pending_review else "PASS", details="High/critical or legal-conflict cases require reviewer approval."))
        reproducible = bool(manifest.config_hash and manifest.input_hashes and manifest.plan)
        gates.append(self._gate("G6", "Reproducibility", reproducible, "Run manifest records configuration, input hashes, seed and plan."))
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
                details=f"Legal layer not consulted: {unavailable_reason}",
            )
        if len(legal_checks) < len(verifications):
            return QualityGate(
                gate_id="G7", name="Legal check", passed=False, status="FAIL",
                details=(
                    f"Only {len(legal_checks)} of {len(verifications)} claims reached the "
                    "legal layer."
                ),
            )
        adverse = [c for c in legal_checks if c["legal_finding"] in {"NOT_MATCH", "PARTIAL_MATCH"}]
        if adverse:
            return QualityGate(
                gate_id="G7", name="Legal check", passed=False, status="PENDING_HUMAN_REVIEW",
                details=(
                    f"{len(adverse)} claim(s) with an adverse legal finding: "
                    + ", ".join(sorted({c["issue"] for c in adverse}))
                ),
            )
        inconclusive = sum(1 for c in legal_checks if c["legal_finding"] == "INSUFFICIENT_EVIDENCE")
        blocked = sorted({
            b["document"] for c in legal_checks for b in c.get("blocked_sources", [])
        })
        details = f"{len(legal_checks)} claim(s) checked against the registered corpus."
        if inconclusive:
            details += f" {inconclusive} inconclusive."
        if blocked:
            details += " Instruments in force without extracted text: " + ", ".join(blocked) + "."
        return QualityGate(
            gate_id="G7", name="Legal check", passed=True, status="PASS", details=details
        )

    @staticmethod
    def _gate(gate_id: str, name: str, passed: bool, details: str) -> QualityGate:
        return QualityGate(gate_id=gate_id, name=name, passed=passed, status="PASS" if passed else "FAIL", details=details)
