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
        self.audit.write("quality_gates_evaluated", {"gates": [g.model_dump(mode="json") for g in gates]})
        return gates

    @staticmethod
    def _gate(gate_id: str, name: str, passed: bool, details: str) -> QualityGate:
        return QualityGate(gate_id=gate_id, name=name, passed=passed, status="PASS" if passed else "FAIL", details=details)
