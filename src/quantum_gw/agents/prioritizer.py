"""Order the claims by where an auditor should spend attention first.

The verifier answers "is this claim supported". An auditor asks something
earlier: *of the 156 claims in this report, which do I open first, and why*.
On 2026-09-23 a Hòa Phát run returned 153 PARTIALLY_SUPPORTED and 154 MEDIUM --
each verdict defensible, the set useless as a work list. A screening tool whose
whole output sits in one band screens nothing.

Priority is not risk. Risk asks how bad this claim looks; priority asks how much
it would cost to be wrong about it, which is why an unremarkable-looking claim
about the group's total emissions outranks a contradicted sentence about staff
training. The four factors and every weight live in `configs/priority_v1.yaml`,
and the score is a weighted sum computed here in Python: an auditor must be able
to argue with the order, so nothing about it is learned.

The queue also carries its own boundary. An audit examines enough and records
what it left out; `queue_claims` returns the work list *and* the sentence that
says what was not examined and why, which is the part a working paper needs and
the part a claim-by-claim dump can never provide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, RiskComponent, VerificationResult
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.verification.numeric_facts import facts_in


@dataclass
class ReviewPriority:
    claim_id: str
    priority_score: float
    rank: int = 0
    in_queue: bool = False
    components: list[RiskComponent] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    policy_version: str = "priority-v1"

    def to_json(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "priority_score": self.priority_score,
            "rank": self.rank,
            "in_queue": self.in_queue,
            "components": [c.model_dump(mode="json") for c in self.components],
            "reasons": self.reasons,
            "policy_version": self.policy_version,
        }


def _load(path: str) -> dict:
    resolved = Path(path)
    if not resolved.exists():
        resolved = Path(__file__).resolve().parents[3] / path
    return yaml.safe_load(resolved.read_text(encoding="utf-8"))


class PrioritizationAgent:
    def __init__(self, policy_path: str, audit: AuditLogger):
        self.policy = _load(policy_path)
        self.version = self.policy["version"]
        self.weights = self.policy["weights"]
        self.audit = audit

    # ---------------------------------------------------------------- scoring

    def run(
        self,
        verifications: list[VerificationResult],
        legal_checks: list[dict] | None = None,
    ) -> list[ReviewPriority]:
        legal_by_claim = {item.get("claim_id"): item for item in (legal_checks or [])}
        scale = _magnitude_scale(v.claim for v in verifications)

        priorities: list[ReviewPriority] = []
        for verification in verifications:
            claim = verification.claim
            components = [
                self._materiality(claim, scale),
                self._obligation(legal_by_claim.get(claim.claim_id)),
                self._evidence_gap(verification),
                self._anomaly(),
            ]
            score = round(sum(c.score for c in components), 2)
            priorities.append(
                ReviewPriority(
                    claim_id=claim.claim_id,
                    priority_score=score,
                    components=components,
                    reasons=[c.reason for c in components if c.score > 0.35 * c.max_score],
                    policy_version=self.version,
                )
            )

        # Rank, then cut the queue.
        for rank, priority in enumerate(
            sorted(priorities, key=lambda p: -p.priority_score), start=1
        ):
            priority.rank = rank
        queued = self._queue_size(sorted(priorities, key=lambda p: -p.priority_score))
        for priority in priorities:
            priority.in_queue = priority.rank <= queued

        self.audit.write(
            "claims_prioritised",
            {
                "policy_version": self.version,
                "claims": len(priorities),
                "queued": queued,
                "score_range": [
                    min((p.priority_score for p in priorities), default=0),
                    max((p.priority_score for p in priorities), default=0),
                ],
            },
        )
        return priorities

    def _component(self, name: str, fraction: float, reason: str) -> RiskComponent:
        maximum = float(self.weights[name])
        return RiskComponent(
            name=name,
            score=round(min(1.0, max(0.0, fraction)) * maximum, 2),
            max_score=maximum,
            reason=reason,
        )

    def _materiality(self, claim: Claim, scale: dict[str, list[float]]) -> RiskComponent:
        policy = self.policy["materiality"]
        families = policy["metric_family"]
        family_weight = families.get(claim.metric or "unknown", families["unknown"])

        magnitude, magnitude_note = _magnitude(claim, scale, policy)
        prominence, prominence_note = _prominence(claim, policy["prominence"])
        blended = policy["magnitude_share"] * magnitude + policy["prominence_share"] * prominence
        fraction = family_weight * blended
        note = ""
        if claim.is_vague and not claim.values:
            fraction *= policy["vague_unquantified_factor"]
            note = "; là ngôn từ quảng bá không kèm số liệu nên hạ bậc"
        metric = claim.metric or "chưa xác định chỉ số"
        return self._component(
            "materiality",
            fraction,
            f"Trọng yếu: chỉ số {metric} (hệ số {family_weight:.2f}); {magnitude_note}; {prominence_note}{note}.",
        )

    def _obligation(self, legal_check: dict | None) -> RiskComponent:
        policy = self.policy["obligation"]
        if not legal_check:
            return self._component(
                "obligation", policy["no_instrument"],
                "Nghĩa vụ: chưa xác định được văn bản nào áp dụng cho loại tuyên bố này.",
            )
        finding = legal_check.get("legal_finding")
        sources = legal_check.get("applicable_sources") or []
        if finding and finding != "INSUFFICIENT_EVIDENCE":
            return self._component(
                "obligation", policy["finding_present"],
                f"Nghĩa vụ: quy tắc pháp lý đã chạy và cho kết quả `{finding}`.",
            )
        if sources:
            names = ", ".join(
                str(s.get("document") or s.get("id")) for s in sources[:2] if isinstance(s, dict)
            )
            return self._component(
                "obligation", policy["applicable_instrument"],
                f"Nghĩa vụ: có văn bản đang hiệu lực điều chỉnh ({names or 'đã xác định'}).",
            )
        return self._component(
            "obligation", policy["no_instrument"],
            "Nghĩa vụ: không có văn bản nào trong kho điều chỉnh nội dung này.",
        )

    def _evidence_gap(self, verification: VerificationResult) -> RiskComponent:
        from quantum_gw.agents.verifier import missing_attributes

        policy = self.policy["evidence_gap"]
        status = VerificationStatus(verification.status)
        base = policy["status"].get(status.value, 0.5)
        gaps = missing_attributes(verification.claim)
        fraction = min(1.0, base + policy["per_missing_attribute"] * len(gaps))
        note = f"thiếu {len(gaps)} thuộc tính" if gaps else "đủ năm thuộc tính"
        return self._component(
            "evidence_gap", fraction,
            f"Khoảng trống bằng chứng: kết luận {status.value}, {note}.",
        )

    def _anomaly(self) -> RiskComponent:
        """Departure from prior periods and peers. Reserved: the cross-period
        procedures are the next layer, and scoring it as 0 keeps the scale
        honest rather than quietly redistributing its weight."""
        return self._component(
            "anomaly", 0.0,
            "Bất thường so với kỳ trước: chưa tính (thủ tục so sánh chéo kỳ là lớp kế tiếp).",
        )

    # ------------------------------------------------------------------ queue

    def _queue_size(self, ranked: list[ReviewPriority]) -> int:
        policy = self.policy["queue"]
        above = sum(1 for p in ranked if p.priority_score >= policy["attention_threshold"])
        size = min(max(above, policy["min_items"]), policy["max_items"])
        return min(size, len(ranked))

    def scope_note(self, priorities: list[ReviewPriority]) -> str:
        """What this pass did not examine, and why — the paragraph a working paper needs."""
        policy = self.policy["queue"]
        queued = [p for p in priorities if p.in_queue]
        rest = [p for p in priorities if not p.in_queue]
        if not rest:
            return (
                f"Toàn bộ {len(priorities)} tuyên bố đều nằm trong hàng đợi soát của lượt này "
                f"(chính sách `{self.version}`)."
            )
        cut = min((p.priority_score for p in queued), default=0.0)
        top = max((p.priority_score for p in rest), default=0.0)
        return (
            f"Lượt sàng lọc này đưa {len(queued)}/{len(priorities)} tuyên bố vào hàng đợi soát, "
            f"theo chính sách `{self.version}` (ngưỡng chú ý {policy['attention_threshold']}, "
            f"tối đa {policy['max_items']} mục). {len(rest)} tuyên bố còn lại **không được soát trong lượt này** "
            f"vì điểm ưu tiên dưới mức cắt ({top:.1f} so với {cut:.1f} của mục thấp nhất trong hàng đợi): "
            f"chúng có độ trọng yếu thấp hơn, không gắn với một nghĩa vụ công bố cụ thể, hoặc đã có bằng chứng "
            f"đối chiếu. Danh sách đầy đủ kèm điểm thành phần nằm trong `result.json`; người soát xét có thể "
            f"hạ ngưỡng để mở rộng phạm vi."
        )


# ------------------------------------------------------------------ helpers


def _claim_facts(claim: Claim):
    return facts_in(claim.text)


def _magnitude_scale(claims) -> dict[str, list[float]]:
    """Every figure in the run, grouped by unit, so magnitude is read as a rank.

    "Large" is relative to what this company reports. 23,474,480 tCO2e is the
    group total and 90,846 is one plant; nobody has to hard-code a threshold for
    the first to outrank the second.
    """
    scale: dict[str, list[float]] = {}
    for claim in claims:
        for fact in _claim_facts(claim):
            # Percentages are excluded on purpose: a share is not a quantity, and
            # ranking 99% against 4% would say the wrong thing about materiality.
            if fact.unit and fact.unit != "%":
                scale.setdefault(fact.unit, []).append(abs(fact.value))
    for values in scale.values():
        values.sort()
    return scale


def _percentile(value: float, sorted_values: list[float]) -> float:
    """Share of the run's figures this one is at least as large as.

    Counted with "<=" so the largest figure in the report scores 1.0 and a lone
    disclosed quantity scores 1.0 as well. Counting strictly below would have
    given the single largest number 0.0 -- which it did, sending the group's
    total emissions below a marketing sentence in the first Hòa Phát queue.
    """
    if not sorted_values:
        return 0.5
    at_or_below = sum(1 for item in sorted_values if item <= value)
    return at_or_below / len(sorted_values)


def _magnitude(claim: Claim, scale: dict[str, list[float]], policy: dict) -> tuple[float, str]:
    facts = [f for f in _claim_facts(claim) if f.unit]
    if not facts:
        return policy["magnitude"]["unquantified"], "không nêu số liệu"
    quantities = [f for f in facts if f.unit != "%"]
    if not quantities:
        return policy["magnitude"]["percentage_only"], "chỉ nêu tỷ lệ phần trăm, không có đại lượng tuyệt đối"
    best = max(quantities, key=lambda f: _percentile(abs(f.value), scale.get(f.unit, [])))
    rank = _percentile(abs(best.value), scale.get(best.unit, []))
    return rank, f"số liệu {best.value:g} {best.unit} lớn bằng hoặc hơn {rank * 100:.0f}% số cùng đơn vị trong báo cáo"


def _prominence(claim: Claim, policy: dict) -> tuple[float, str]:
    page = claim.source_page
    if page is None:
        return policy["unknown_page"], "không rõ vị trí trong tài liệu"
    if page <= policy["front_pages"]:
        return policy["front_score"], f"nằm ở phần đầu báo cáo (trang {page})"
    return policy["rest_score"], f"nằm ở phần sau báo cáo (trang {page})"
