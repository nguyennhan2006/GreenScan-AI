from __future__ import annotations

from pathlib import Path

import yaml

from quantum_gw.domain.enums import Severity, VerificationStatus
from quantum_gw.domain.models import RiskAssessment, RiskComponent, VerificationResult
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import normalize_for_match


class RiskScoringAgent:
    def __init__(self, rubric_path: str, audit: AuditLogger):
        path = Path(rubric_path)
        if not path.exists():
            path = Path(__file__).resolve().parents[3] / rubric_path
        self.rubric = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.version = self.rubric["version"]
        self.audit = audit

    def run(self, verification: VerificationResult) -> RiskAssessment:
        claim = verification.claim
        components: list[RiskComponent] = []

        components.append(self._component("specificity", 15 if claim.is_vague else (7 if not claim.metric else 1), "Claim specificity and identifiable metric."))
        components.append(self._component("quantitative_evidence", 15 if not claim.values else 2, "Presence of a quantitative value in the claim."))
        baseline_penalty = 0
        if claim.direction or claim.is_future_commitment:
            baseline_penalty = 10 if not claim.baseline else (5 if not claim.period else 0)
        components.append(self._component("baseline_and_period", baseline_penalty, "Baseline and reporting/target period completeness."))

        evidence_penalty = {
            VerificationStatus.SUPPORTED: 0,
            VerificationStatus.PARTIALLY_SUPPORTED: 8,
            VerificationStatus.UNSUPPORTED: 16,
            VerificationStatus.CONTRADICTED: 20,
            VerificationStatus.INSUFFICIENT_EVIDENCE: 14,
        }[verification.status]
        components.append(self._component("evidence_support", evidence_penalty, f"Verification status: {verification.status}."))

        independent = any(e.source_type.value in {"legal", "external", "standard"} for e in verification.evidence)
        components.append(self._component("independent_assurance", 0 if independent else 10, "Independent/legal/standard source coverage."))
        components.append(self._component("contradiction", 20 if verification.status == VerificationStatus.CONTRADICTED else 0, "Direct contradiction penalty."))

        normalized = normalize_for_match(claim.text)
        vague_terms = ["huong toi", "cam ket manh me", "than thien", "xanh hon", "hang dau", "dang ke", "toan dien"]
        vague_penalty = 10 if any(term in normalized for term in vague_terms) else (6 if claim.is_vague else 0)
        components.append(self._component("vague_or_exaggerated_language", vague_penalty, "Vague or promotional language."))

        risk_score = round(min(100.0, sum(item.score for item in components)), 2)
        severity = self._severity(risk_score)
        requires_review = severity in {Severity.HIGH, Severity.CRITICAL} or any(
            e.source_type.value == "legal" for e in verification.evidence
        ) and verification.status == VerificationStatus.CONTRADICTED
        assessment = RiskAssessment(
            claim_id=claim.claim_id,
            risk_score=risk_score,
            severity=severity,
            components=components,
            requires_human_review=requires_review,
            rubric_version=self.version,
        )
        self.audit.write("risk_scored", assessment.model_dump(mode="json"))
        return assessment

    def _component(self, name: str, score: float, reason: str) -> RiskComponent:
        maximum = float(self.rubric["components"][name]["max_score"])
        return RiskComponent(name=name, score=min(maximum, max(0.0, float(score))), max_score=maximum, reason=reason)

    @staticmethod
    def _severity(score: float) -> Severity:
        if score >= 75:
            return Severity.CRITICAL
        if score >= 50:
            return Severity.HIGH
        if score >= 25:
            return Severity.MEDIUM
        return Severity.LOW
