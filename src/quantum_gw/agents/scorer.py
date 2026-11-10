from __future__ import annotations
from ..labels_vi import SCOPE, VERDICT, vi

from pathlib import Path

import yaml

from quantum_gw.agents.claim_quality import reason_vi
from quantum_gw.domain.enums import Severity, VerificationStatus
from quantum_gw.domain.models import RiskAssessment, RiskComponent, VerificationResult
from quantum_gw.settings import ReviewSettings
from quantum_gw.storage.audit import AuditLogger


class RiskScoringAgent:
    def __init__(self, rubric_path: str, audit: AuditLogger, review: ReviewSettings | None = None):
        path = Path(rubric_path)
        if not path.exists():
            path = Path(__file__).resolve().parents[3] / rubric_path
        self.rubric = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.version = self.rubric["version"]
        self.audit = audit
        self.review = review or ReviewSettings()
        # Severity bands come from the rubric and nowhere else. There used to be
        # three copies of these numbers -- a `severity:` block in the rubric that
        # nothing read, `high_risk_threshold`/`critical_risk_threshold` in
        # ReviewSettings that nothing read either, and the real ones hardcoded
        # here -- so editing the rubric or the config silently changed nothing.
        self.bands = _bands(self.rubric)

    def run(self, verification: VerificationResult) -> RiskAssessment:
        claim = verification.claim
        # A sentence that is probably not a claim (claim-quality-v1) is not
        # scored: every "missing attribute" would be penalised on a table cell
        # or a decree's title, and GS-Eval v2 found exactly that -- 43 non-claims
        # penalised on every component. A contradiction is still scored: it must
        # reach a reviewer whatever the sentence looks like.
        if claim.quality_flag and verification.status != VerificationStatus.CONTRADICTED:
            return self._not_scored(verification)
        components: list[RiskComponent] = []

        components.append(self._component("specificity", 12 if claim.is_vague else (6 if not claim.metric else 1), "Mức cụ thể của tuyên bố và chỉ số xác định được."))
        components.append(self._component("quantitative_evidence", 12 if not claim.values else 2, "Tuyên bố có giá trị định lượng hay không."))
        # Baseline and period are scored separately: they fail independently and
        # a reviewer fixes them differently. A combined component could only say
        # "something about time is missing", which is not actionable.
        #
        # risk-rubric-v3: a base year is needed for a change that is stated with
        # a figure ("giảm 20 %") or set as a target ("giảm … vào 2030"). The v2
        # rule asked for one whenever a trend word appeared ("giảm thiểu tác động
        # môi trường"), which penalised 69 claims that GS-Eval v2 labels say need
        # none; the missing figure there is already scored by quantitative_evidence.
        needs_baseline = bool(claim.direction and (claim.values or claim.is_future_commitment))
        baseline_penalty = 8 if (needs_baseline and not claim.baseline) else 0
        components.append(self._component(
            "baseline", baseline_penalty,
            "Cần năm gốc để so sánh." if needs_baseline
            else "Không nêu mức thay đổi có số liệu hay mục tiêu tăng/giảm nên không cần năm gốc."))

        period_penalty = 8 if not claim.period else 0
        components.append(self._component(
            "period", period_penalty, "Kỳ báo cáo hoặc kỳ mục tiêu của số liệu."))

        # Boundary: one plant, the parent, or the consolidated group. Without it
        # a percentage cannot be checked against any table.
        components.append(self._component(
            "scope_boundary", 0 if claim.scope else 8,
            f"Phạm vi áp dụng: {vi(SCOPE, claim.scope)}." if claim.scope
            else "Không nêu pháp nhân, cơ sở hay phạm vi phát thải."))

        evidence_penalty = {
            VerificationStatus.SUPPORTED: 0,
            VerificationStatus.PARTIALLY_SUPPORTED: 7,
            VerificationStatus.UNSUPPORTED: 14,
            VerificationStatus.CONTRADICTED: 18,
            VerificationStatus.INSUFFICIENT_EVIDENCE: 12,
        }[verification.status]
        components.append(self._component("evidence_support", evidence_penalty, f"Kết quả kiểm chứng: {vi(VERDICT, verification.status)}."))

        independent = any(e.source_type.value in {"legal", "external", "standard"} for e in verification.evidence)
        components.append(self._component("independent_assurance", 0 if independent else 8, "Có nguồn độc lập, văn bản pháp lý hoặc chuẩn mực hay không."))
        components.append(self._component("contradiction", 18 if verification.status == VerificationStatus.CONTRADICTED else 0, "Điểm cộng thêm khi nguồn mâu thuẫn trực tiếp."))

        # Scored from the terms the extractor matched against configs/taxonomy.yaml.
        # This used to be a second, shorter, Vietnamese-only copy of that list
        # living here, so the most vague claim in the corpus -- KLM-2024's "Join
        # us in creating a more sustainable future" -- scored 0 on the component
        # named for exactly that problem.
        vague_reason = (
            "Ngôn ngữ mơ hồ hoặc quảng bá: " + ", ".join(claim.vague_terms_matched[:4])
            if claim.vague_terms_matched
            else "Không thấy ngôn ngữ mơ hồ hoặc quảng bá."
        )
        components.append(self._component(
            "vague_or_exaggerated_language",
            8 if claim.vague_terms_matched else 0,
            vague_reason,
        ))

        risk_score = round(min(100.0, sum(item.score for item in components)), 2)
        evidence_strength = _evidence_strength(verification)
        contradiction_strength = _contradiction_strength(verification)
        severity, cap_reason = self._capped_severity(risk_score, contradiction_strength)
        # A claim contradicted by a legal source is a reviewer's decision even
        # when the arithmetic lands in a low band: the consequence of being wrong
        # is a public accusation against a named company.
        legal_conflict = verification.status == VerificationStatus.CONTRADICTED and any(
            e.source_type.value == "legal" for e in verification.evidence
        )
        # A contradiction is a reviewer's decision whatever the band says. The
        # bands are not calibrated yet (B6: 2 of 4 adjudicated cases land in the
        # expected band), so a numeric contradiction from an external auditor can
        # score 47 and sit in MEDIUM; it must still be looked at.
        requires_review = severity in {Severity.HIGH, Severity.CRITICAL} or (
            legal_conflict and self.review.require_human_for_legal_conflict
        ) or verification.requires_llm_review or contradiction_strength != "none"
        assessment = RiskAssessment(
            claim_id=claim.claim_id,
            risk_score=risk_score,
            severity=severity,
            components=components,
            evidence_strength=evidence_strength,
            contradiction_strength=contradiction_strength,
            materiality="unknown",
            severity_cap_reason=cap_reason,
            requires_human_review=requires_review,
            rubric_version=self.version,
        )
        self.audit.write("risk_scored", assessment.model_dump(mode="json"))
        return assessment

    def _not_scored(self, verification: VerificationResult) -> RiskAssessment:
        claim = verification.claim
        why = reason_vi(claim.quality_flag) or "có dấu hiệu không phải tuyên bố"
        reason = f"Không chấm: câu có thể không phải tuyên bố ({why}); người soát xem trang gốc để quyết định."
        components = [
            RiskComponent(name=name, score=0.0, max_score=float(spec["max_score"]), reason=reason, status="not_applicable")
            for name, spec in self.rubric["components"].items()
        ]
        contradiction_strength = _contradiction_strength(verification)
        assessment = RiskAssessment(
            claim_id=claim.claim_id,
            risk_score=0.0,
            severity=Severity.LOW,
            components=components,
            evidence_strength=_evidence_strength(verification),
            contradiction_strength=contradiction_strength,
            materiality="unknown",
            severity_cap_reason=reason,
            requires_human_review=verification.requires_llm_review or contradiction_strength != "none",
            rubric_version=self.version,
        )
        self.audit.write("risk_scored", assessment.model_dump(mode="json"))
        return assessment

    def _component(self, name: str, score: float, reason: str) -> RiskComponent:
        maximum = float(self.rubric["components"][name]["max_score"])
        return RiskComponent(name=name, score=min(maximum, max(0.0, float(score))), max_score=maximum, reason=reason)

    def _severity(self, score: float) -> Severity:
        for severity, lower in self.bands:
            if score >= lower:
                return severity
        return Severity.LOW

    def _capped_severity(self, score: float, contradiction: str) -> tuple[Severity, str | None]:
        """Band from the score, then capped when nothing contradicts the claim.

        Missing attributes and missing evidence add up to 65 of 100 on their
        own, which put 65 of 181 claims of a control company in HIGH on
        2026-09-22 with no contradiction anywhere. A claim nobody has
        contradicted is a disclosure gap: a reviewer should see it, but not
        before the claims something actually contradicts. The cap holds until
        the bands are calibrated on the gold set (D-2026-09-22-03, RQ8).
        """
        severity = self._severity(score)
        if contradiction in _CONTRADICTION_ABOVE_CAP:
            return severity, None
        cap = Severity(self.review.severity_cap_without_contradiction.upper())
        note = {
            "none": "không có bằng chứng nào bác bỏ tuyên bố",
            "trend_only": "chỉ có xu hướng ngược, không có số liệu đối chiếu",
        }.get(contradiction, contradiction)
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        if order.index(severity) <= order.index(cap):
            return severity, None
        return cap, (
            f"Hạ từ {severity.value} xuống {cap.value}: {note}; "
            "điểm đến từ thuộc tính còn thiếu và mức độ đầy đủ của bằng chứng."
        )


# Only a positive contradiction lifts a claim above the cap. `trend_only` -- the
# claim says "giảm" and a passage about the same metric says "tăng", with no
# figure either side -- is a reviewer's flag, not a finding (verifier._status),
# so it is reviewed but not ranked as high risk.
_CONTRADICTION_ABOVE_CAP = frozenset({"numeric", "authoritative_cue", "qualitative_cue", "unspecified"})


def _evidence_strength(verification) -> str:
    """How well the corpus substantiates the claim — read from the verdict and its evidence."""
    status = verification.status
    if status == VerificationStatus.SUPPORTED:
        independent = any(
            e.source_type.value in {"legal", "external", "standard"} for e in verification.evidence
        )
        return "strong" if independent else "moderate"
    if status == VerificationStatus.PARTIALLY_SUPPORTED:
        return "moderate" if verification.evidence else "weak"
    if status == VerificationStatus.CONTRADICTED:
        return "moderate"
    if status == VerificationStatus.UNSUPPORTED:
        return "weak"
    return "none"


def _contradiction_strength(verification) -> str:
    """What positively contradicts the claim, if anything — never "absence of support"."""
    if verification.status != VerificationStatus.CONTRADICTED:
        # A reversed trend with no figure is flagged on the passage, not the verdict.
        if any(e.relation_method == "direction" for e in verification.evidence):
            return "trend_only"
        return "none"
    contradicting = [e for e in verification.evidence if e.relation == "CONTRADICTS"]
    if any(e.relation_method == "numeric" for e in contradicting):
        return "numeric"
    if any(
        e.source_type.value in {"legal", "standard"} or "thẩm quyền" in (e.relation_reason or "")
        for e in contradicting
    ):
        return "authoritative_cue"
    if contradicting:
        return "qualitative_cue"
    # The verdict says contradicted but no passage carries the stance: a fixture,
    # or a caller that built the result by hand. Not "none" -- the cap exists to
    # stop absence of support from looking like a finding, not to soften findings.
    return "unspecified"


def _bands(rubric: dict) -> list[tuple[Severity, float]]:
    """Severity bands from the rubric, highest first.

    Each band is read as a lower bound; the upper bound in the YAML is
    documentation. Raises rather than falling back to defaults, because a rubric
    whose bands cannot be read is a configuration error the operator has to see
    -- silently scoring against different thresholds than the file states is the
    failure this function exists to remove.
    """
    raw = rubric.get("severity")
    if not raw:
        raise ValueError("Rubric is missing the `severity:` bands block.")
    bands: list[tuple[Severity, float]] = []
    for name, bounds in raw.items():
        try:
            bands.append((Severity(name.upper()), float(bounds[0])))
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            raise ValueError(f"Invalid severity band {name!r}: {bounds!r}") from exc
    return sorted(bands, key=lambda item: item[1], reverse=True)
