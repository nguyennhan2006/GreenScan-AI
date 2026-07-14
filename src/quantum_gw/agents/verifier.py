from __future__ import annotations

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence, VerificationResult
from quantum_gw.settings import VerificationSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import normalize_for_match, parse_numbers, tokenize


class VerificationAgent:
    def __init__(self, settings: VerificationSettings, audit: AuditLogger):
        self.settings = settings
        self.audit = audit

    def run(self, claim: Claim, evidence: list[RetrievedEvidence]) -> VerificationResult:
        warnings: list[str] = []
        clean_evidence = []
        for item in evidence:
            if item.suspicious_instruction:
                warnings.append(f"Excluded suspicious document instruction: {item.citation}")
                if self.settings.injection_policy == "exclude":
                    continue
            clean_evidence.append(item)

        if not clean_evidence:
            result = VerificationResult(
                claim=claim,
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                rationale="No admissible evidence passed the retrieval threshold.",
                evidence=[],
                warnings=warnings,
            )
            self._audit(result)
            return result

        best = clean_evidence[0]
        numeric = self._numeric_comparison(claim, clean_evidence)
        contradiction = self._direction_contradiction(claim, clean_evidence) or numeric["contradiction"]
        overlap = self._metric_overlap(claim, clean_evidence)

        if contradiction:
            status = VerificationStatus.CONTRADICTED
            rationale = "Retrieved evidence contains a conflicting direction or materially different quantitative value."
        elif numeric["matched"] and best.score >= self.settings.partial_support_score:
            status = VerificationStatus.SUPPORTED
            rationale = "A retrieved source supports the claim with a quantitatively consistent value."
        elif best.score >= self.settings.strong_support_score and overlap >= 0.30:
            status = VerificationStatus.PARTIALLY_SUPPORTED
            rationale = "Relevant evidence was found, but the claim is not fully verified at the same scope, period or precision."
        elif best.score >= self.settings.partial_support_score and overlap >= 0.18:
            status = VerificationStatus.PARTIALLY_SUPPORTED
            rationale = "Evidence is related but incomplete; additional baseline, scope or assurance is required."
        elif best.score >= self.settings.partial_support_score:
            status = VerificationStatus.UNSUPPORTED
            rationale = "Retrieved material is similar to the claim but does not substantiate it."
        else:
            status = VerificationStatus.INSUFFICIENT_EVIDENCE
            rationale = "The available evidence is too weak to support or contradict the claim."

        result = VerificationResult(
            claim=claim,
            status=status,
            rationale=rationale,
            evidence=clean_evidence,
            computed_values=numeric,
            warnings=warnings,
        )
        self._audit(result)
        return result

    def _numeric_comparison(self, claim: Claim, evidence: list[RetrievedEvidence]) -> dict:
        claim_numbers = [(value, unit) for value, unit in parse_numbers(claim.text) if value < 1900 or value > 2100]
        evidence_numbers = []
        for item in evidence:
            evidence_numbers.extend((value, unit, item.citation) for value, unit in parse_numbers(item.text) if value < 1900 or value > 2100)
        matched = False
        contradiction = False
        closest = None
        for c_value, c_unit in claim_numbers:
            for e_value, e_unit, citation in evidence_numbers:
                if c_unit and e_unit and c_unit != e_unit:
                    continue
                denominator = max(abs(c_value), 1.0)
                relative_error = abs(e_value - c_value) / denominator
                candidate = {"claim": c_value, "evidence": e_value, "relative_error": relative_error, "citation": citation}
                if closest is None or relative_error < closest["relative_error"]:
                    closest = candidate
                if relative_error <= self.settings.numeric_relative_tolerance:
                    matched = True
                elif relative_error >= 0.35 and c_value != 0:
                    contradiction = True
        contradiction = bool(claim_numbers and evidence_numbers and not matched and closest and closest["relative_error"] >= 0.35)
        return {
            "claim_numbers": claim_numbers,
            "evidence_numbers": evidence_numbers[:30],
            "matched": matched,
            "contradiction": contradiction,
            "closest_pair": closest,
            "calculation_method": "deterministic-relative-error",
        }

    @staticmethod
    def _direction_contradiction(claim: Claim, evidence: list[RetrievedEvidence]) -> bool:
        if not claim.direction:
            return False
        text = " ".join(normalize_for_match(item.text) for item in evidence[:3])
        decrease = any(term in text for term in ["giam", "cat giam", "decrease", "reduction", "lower"])
        increase = any(term in text for term in ["tang", "increase", "rose", "grew", "higher"])
        if claim.direction == "decrease" and increase and not decrease:
            return True
        if claim.direction == "increase" and decrease and not increase:
            return True
        return False

    @staticmethod
    def _metric_overlap(claim: Claim, evidence: list[RetrievedEvidence]) -> float:
        claim_tokens = set(tokenize(claim.text))
        evidence_tokens = set(tokenize(" ".join(item.text for item in evidence[:3])))
        return len(claim_tokens & evidence_tokens) / max(1, len(claim_tokens))

    def _audit(self, result: VerificationResult) -> None:
        self.audit.write(
            "claim_verified",
            {
                "claim_id": result.claim.claim_id,
                "status": result.status,
                "citations": [e.citation for e in result.evidence],
                "warnings": result.warnings,
            },
        )
