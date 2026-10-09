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

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, RiskComponent, VerificationResult
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import normalize_text
from quantum_gw.verification.numeric_facts import facts_in

# Who is speaking. A green claim is the reporting entity asserting something about
# itself; these are the words a Vietnamese or English report uses for itself and
# its units. Matched whole-word on the text's own orthography.
_SELF_REFERENCE = (
    "chúng tôi", "chúng ta", "tập đoàn", "công ty", "doanh nghiệp", "nhà máy",
    "khu liên hợp", "tổng công ty", "đơn vị thành viên", "công ty con", "ban lãnh đạo",
    "hội đồng quản trị", "ban điều hành", "ban giám đốc",
    "we", "our", "the company", "the group",
)
# A sentence that leans on the one before it ("Qua đó, lượng CO2 … giảm tương
# ứng") does not say on its own who did what.
_ANAPHORIC_OPENING = re.compile(
    r"^\s*(?:đây là|điều này|qua đó|nhờ đó|ngược lại|quan trọng hơn|biện pháp này"
    r"|giải pháp này|việc này|quy trình này)(?!\w)"
)
# Merged columns: a run of parenthesised acronyms is a logo strip or a table
# header read across, not prose ("VIỆT NAM (VSA) NAM (VCCI) (VAMI) (HUBA) …").
_GARBLED_LAYOUT = re.compile(r"(?:\([A-ZĐ]{2,}\)\s*){3,}")
# "Tập đoàn Hòa Phát", "Công ty Cổ phần Vinamilk": the capitalised words after
# a legal-form prefix are the entity's own name.
_ENTITY_PREFIX = re.compile(
    r"(?:tập đoàn|tổng công ty|công ty cổ phần|công ty cp|công ty tnhh|công ty|ctcp)\s+",
    re.IGNORECASE,
)
_LEGAL_FORM_WORDS = {"cổ", "phần", "cp", "tnhh", "mtv", "một", "thành", "viên"}

# Reasons are read by a Vietnamese auditor and printed on the working paper:
# no enum names, no English metric keys.
_METRIC_VI = {
    "emissions": "phát thải khí nhà kính",
    "renewable_energy": "năng lượng tái tạo",
    "energy": "năng lượng",
    "water": "nước",
    "waste": "chất thải",
    "green_finance": "tài chính xanh",
}
_STATUS_VI = {
    "SUPPORTED": "được ủng hộ",
    "PARTIALLY_SUPPORTED": "ủng hộ một phần",
    "UNSUPPORTED": "chưa được chứng minh trong kho đã kiểm",
    "CONTRADICTED": "mâu thuẫn với nguồn",
    "INSUFFICIENT_EVIDENCE": "chưa đủ bằng chứng",
}


def entity_names(texts: Iterable[str], declared: Iterable[str] = ()) -> list[str]:
    """The reporting entity's own name: declared in metadata, else read from the text.

    The most frequent capitalised name after "Tập đoàn"/"Công ty …" in the claim
    source is taken as the entity ("Hòa Phát" on HPG 2025). Without it, "ESG Hòa
    Phát tích hợp các mục tiêu …" reads as nobody's sentence.
    """
    names = [str(n).strip() for n in declared if str(n or "").strip()]
    counts: Counter = Counter()
    for text in texts:
        for match in _ENTITY_PREFIX.finditer(text):
            words: list[str] = []
            for word in text[match.end(): match.end() + 60].split()[:5]:
                word = word.strip(",.;:()\"“”")
                if not words and word.lower() in _LEGAL_FORM_WORDS:
                    continue  # "Công ty TNHH MTV …": the legal form is not the name
                if not word or not word[0].isupper():
                    break
                words.append(word)
                if len(words) == 3:
                    break
            if words:
                counts[" ".join(words)] += 1
    if counts:
        name, seen = counts.most_common(1)[0]
        if seen >= 3:
            names.append(name)
    return list(dict.fromkeys(names))  # one entry per name, declared first


@dataclass
class ReviewPriority:
    # A queue holds two kinds of item: a claim (a sentence to verify) and a
    # disclosed figure (a published number to test). They are ranked together
    # because the auditor's question -- what do I open first -- does not care
    # which kind the answer is.
    item_type: str          # claim | figure
    item_id: str
    text: str
    priority_score: float
    rank: int = 0
    in_queue: bool = False
    components: list[RiskComponent] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    # Points actually available: the weights of the factors that could be
    # computed. Reporting 51.6/100 when 10 of those points can never be earned
    # in this release would overstate how sure the number is.
    max_available: float = 100.0
    not_computed: list[str] = field(default_factory=list)
    policy_version: str = "priority-v1"

    def to_json(self) -> dict:
        return {
            "item_type": self.item_type,
            "item_id": self.item_id,
            "claim_id": self.item_id if self.item_type == "claim" else None,
            "text": self.text,
            "priority_score": self.priority_score,
            "rank": self.rank,
            "in_queue": self.in_queue,
            "components": [c.model_dump(mode="json") for c in self.components],
            "max_available": self.max_available,
            "not_computed": self.not_computed,
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
        figures: list | None = None,
        figure_checks: list | None = None,
        entity: Iterable[str] = (),
    ) -> list[ReviewPriority]:
        self._speakers = [
            re.compile(rf"(?<!\w){re.escape(normalize_text(name).lower())}(?!\w)")
            for name in (*_SELF_REFERENCE, *entity) if name
        ]
        legal_by_claim = {item.get("claim_id"): item for item in (legal_checks or [])}
        scale = _magnitude_scale(
            (v.claim for v in verifications), figures or []
        )

        priorities: list[ReviewPriority] = []
        for verification in verifications:
            claim = verification.claim
            components = [
                self._materiality(claim, scale),
                self._obligation(legal_by_claim.get(claim.claim_id)),
                self._evidence_gap(verification),
                self._anomaly(),
            ]
            priorities.append(self._priority("claim", claim.claim_id, claim.text, components))

        checks_by_figure: dict[str, list] = {}
        for check in figure_checks or []:
            for figure_id in check.figure_ids:
                checks_by_figure.setdefault(figure_id, []).append(check)
        for figure in figures or []:
            components = [
                self._figure_materiality(figure, scale),
                self._figure_obligation(figure),
                self._figure_gap(checks_by_figure.get(figure.figure_id, [])),
                self._anomaly(),
            ]
            label = f"{figure.label}: {figure.value:,.0f} {figure.unit}"
            priorities.append(self._priority("figure", figure.figure_id, label, components))

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

    def _priority(self, kind: str, item_id: str, text: str, components: list[RiskComponent]) -> ReviewPriority:
        computed = [c for c in components if c.status == "computed"]
        return ReviewPriority(
            item_type=kind,
            item_id=item_id,
            text=text,
            priority_score=round(sum(c.score for c in computed), 2),
            components=components,
            max_available=round(sum(c.max_score for c in computed), 2),
            not_computed=[c.name for c in components if c.status != "computed"],
            reasons=[c.reason for c in computed if c.score > 0.35 * c.max_score],
            policy_version=self.version,
        )

    # ------------------------------------------------------- disclosed figures

    def _figure_materiality(self, figure, scale: dict[str, list[float]]) -> RiskComponent:
        """A published figure has a real magnitude, which is the whole point of it."""
        policy = self.policy["materiality"]
        families = policy["metric_family"]
        family_weight = families.get(figure.metric or "unknown", families["unknown"])
        peers = scale.get(figure.unit, [])
        if figure.unit == "%":
            magnitude, note = policy["magnitude"]["percentage_only"], "là tỷ lệ phần trăm"
        elif len(peers) < policy["magnitude"]["minimum_peers"]:
            magnitude = policy["magnitude"]["too_few_peers"]
            note = f"{figure.value:,.0f} {figure.unit}, chưa đủ số cùng đơn vị để so độ lớn"
        else:
            magnitude = _percentile(abs(figure.value), peers)
            note = f"{figure.value:,.0f} {figure.unit}, lớn bằng hoặc hơn {magnitude * 100:.0f}% số cùng đơn vị"
        prominence, prominence_note = _prominence(figure, policy["prominence"])
        blended = policy["magnitude_share"] * magnitude + policy["prominence_share"] * prominence
        total_note = " (là dòng tổng cộng)" if figure.is_total else ""
        return self._component(
            "materiality", family_weight * blended,
            f"Trọng yếu: số liệu công bố{total_note}; {note}; {prominence_note}.",
        )

    def _figure_obligation(self, figure) -> RiskComponent:
        """Read from the metric, not from a rule: the legal layer runs per claim."""
        policy = self.policy["obligation"]
        if figure.metric:
            return self._component(
                "obligation", policy["applicable_instrument"],
                f"Pháp lý: {_METRIC_VI.get(figure.metric, figure.metric)} thuộc nhóm chỉ tiêu phải công bố theo quy định hiện hành.",
            )
        return self._component(
            "obligation", policy["no_instrument"],
            "Pháp lý: chưa gắn được chỉ số này với một nghĩa vụ công bố cụ thể.",
        )

    def _figure_gap(self, checks: list) -> RiskComponent:
        """For a figure the gap is not missing attributes but missing corroboration."""
        policy = self.policy["evidence_gap"]
        if any(c.status == "INCONSISTENT" for c in checks):
            return self._component(
                "evidence_gap", policy["status"]["CONTRADICTED"],
                "Khoảng trống bằng chứng: thủ tục kiểm tra cho kết quả **không nhất quán**.",
            )
        if checks:
            return self._component(
                "evidence_gap", policy["status"]["SUPPORTED"],
                "Khoảng trống bằng chứng: đã qua thủ tục kiểm tra và nhất quán.",
            )
        return self._component(
            "evidence_gap", policy["status"]["INSUFFICIENT_EVIDENCE"],
            "Khoảng trống bằng chứng: chưa có thủ tục nào đối chiếu được số này.",
        )

    def _component(
        self, name: str, fraction: float, reason: str, status: str = "computed"
    ) -> RiskComponent:
        maximum = float(self.weights[name])
        return RiskComponent(
            name=name,
            score=round(min(1.0, max(0.0, fraction)) * maximum, 2),
            max_score=maximum,
            reason=reason,
            status=status,
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
        factor, attribution_note = self._attribution(claim, policy)
        fraction *= factor
        note += attribution_note
        metric = _METRIC_VI.get(claim.metric, claim.metric) if claim.metric else "chưa xác định chỉ số"
        return self._component(
            "materiality",
            fraction,
            f"Trọng yếu: nhóm {metric} (trọng số {family_weight:.2f}); {magnitude_note}; {prominence_note}{note}.",
        )

    def _attribution(self, claim: Claim, policy: dict) -> tuple[float, str]:
        """Is this the entity asserting something about itself?

        Moves a sentence down the queue, never out of the list and never to a
        different verdict: whether it is a claim at all is the reviewer's call,
        and P5 measures that on gold. A stated figure is checkable whoever says
        it, so a sentence with one is never moved.
        """
        text = normalize_text(claim.text)
        if _GARBLED_LAYOUT.search(text):
            return policy["garbled_factor"], (
                "; chữ có dấu hiệu dính cột hoặc lỗi trình bày nên hạ bậc — cần đọc trang gốc"
            )
        if any(fact.unit for fact in _claim_facts(claim)):
            return 1.0, ""
        lowered = text.lower()
        speaks = any(pattern.search(lowered) for pattern in getattr(self, "_speakers", ()))
        if speaks and not _ANAPHORIC_OPENING.search(lowered):
            return 1.0, ""
        return policy["unattributed_factor"], (
            "; không nêu chủ thể là doanh nghiệp và không có số liệu "
            "(câu giải thích hoặc nối ý câu trước) nên hạ bậc"
        )

    def _obligation(self, legal_check: dict | None) -> RiskComponent:
        policy = self.policy["obligation"]
        if not legal_check:
            return self._component(
                "obligation", policy["no_instrument"],
                "Pháp lý: chưa xác định được văn bản nào áp dụng cho loại tuyên bố này.",
            )
        finding = legal_check.get("legal_finding")
        sources = legal_check.get("applicable_sources") or []
        if finding and finding != "INSUFFICIENT_EVIDENCE":
            return self._component(
                "obligation", policy["finding_present"],
                f"Pháp lý: quy tắc kiểm tra nghĩa vụ đã chạy và cho kết quả `{finding}`.",
            )
        if sources:
            names = ", ".join(
                str(s.get("document") or s.get("id")) for s in sources[:2] if isinstance(s, dict)
            )
            return self._component(
                "obligation", policy["applicable_instrument"],
                # Relevance by topic and date, not yet an obligation: no rule has
                # tested this claim's subject (invariant 7, relevance ≠ applicability).
                f"Pháp lý: có văn bản đang hiệu lực cùng chủ đề ({names or 'đã xác định'}); "
                "chưa có quy tắc xác định nghĩa vụ cụ thể.",
            )
        return self._component(
            "obligation", policy["no_instrument"],
            "Pháp lý: không có văn bản nào trong kho điều chỉnh nội dung này.",
        )

    def _evidence_gap(self, verification: VerificationResult) -> RiskComponent:
        from quantum_gw.agents.verifier import missing_attributes

        policy = self.policy["evidence_gap"]
        status = VerificationStatus(verification.status)
        base = policy["status"].get(status.value, 0.5)
        gaps = missing_attributes(verification.claim)
        # Missing attributes may raise the gap but must never lift a claim that
        # nothing contradicts to the ceiling reserved for one that something
        # does: absence of support and positive contradiction are different
        # findings and must stay distinguishable in the score.
        ceiling = (
            1.0 if status == VerificationStatus.CONTRADICTED
            else policy["max_without_contradiction"]
        )
        fraction = min(ceiling, base + policy["per_missing_attribute"] * len(gaps))
        note = f"thiếu {len(gaps)}/5 thuộc tính" if gaps else "đủ năm thuộc tính"
        return self._component(
            "evidence_gap", fraction,
            f"Khoảng trống bằng chứng: kết quả “{_STATUS_VI.get(status.value, status.value)}”, {note}.",
        )

    def _anomaly(self) -> RiskComponent:
        """Departure from prior periods and peers — declared, not yet computed.

        Marked `not_computed` rather than scored 0: a zero here would read as
        "checked the prior years and found nothing unusual", which is the
        opposite of what the system knows. Its weight is excluded from the
        achievable total until the cross-period procedures land (ISSUES P3).
        """
        return self._component(
            "anomaly", 0.0,
            "Bất thường so với kỳ trước: **chưa tính** — thủ tục so sánh chéo kỳ chưa có, "
            "đây không phải kết luận 'không có bất thường'.",
            status="not_computed",
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
                f"Toàn bộ {len(priorities)} mục (tuyên bố và số liệu công bố) đều nằm trong hàng đợi soát của lượt này "
                f"(chính sách `{self.version}`)."
            )
        cut = min((p.priority_score for p in queued), default=0.0)
        top = max((p.priority_score for p in rest), default=0.0)
        return (
            f"Lượt sàng lọc này đưa {len(queued)}/{len(priorities)} mục (tuyên bố và số liệu công bố) vào hàng đợi soát, "
            f"theo chính sách `{self.version}` (ngưỡng chú ý {policy['attention_threshold']}, "
            f"tối đa {policy['max_items']} mục). {len(rest)} mục còn lại **không được soát trong lượt này** "
            f"vì điểm ưu tiên dưới mức cắt ({top:.1f} so với {cut:.1f} của mục thấp nhất trong hàng đợi): "
            f"chúng có độ trọng yếu thấp hơn, không gắn với một nghĩa vụ công bố cụ thể, hoặc đã có bằng chứng "
            f"đối chiếu. Danh sách đầy đủ kèm điểm thành phần nằm trong `result.json`; người soát xét có thể "
            f"hạ ngưỡng để mở rộng phạm vi."
        )


# ------------------------------------------------------------------ helpers


def _claim_facts(claim: Claim):
    return facts_in(claim.text)


def _magnitude_scale(claims, figures=()) -> dict[str, list[float]]:
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
    for figure in figures:
        if figure.unit and figure.unit != "%":
            scale.setdefault(figure.unit, []).append(abs(figure.value))
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
    peers = scale.get(best.unit, [])
    if len(peers) < policy["magnitude"]["minimum_peers"]:
        return policy["magnitude"]["too_few_peers"], (
            f"số liệu {best.value:g} {best.unit}, chưa đủ số cùng đơn vị để so độ lớn"
        )
    rank = _percentile(abs(best.value), peers)
    return rank, f"số liệu {best.value:g} {best.unit} lớn bằng hoặc hơn {rank * 100:.0f}% số cùng đơn vị trong báo cáo"


def _prominence(item, policy: dict) -> tuple[float, str]:
    """Where it sits in the document; works for a claim or a disclosed figure."""
    page = item.source_page
    if page is None:
        return policy["unknown_page"], "không rõ vị trí trong tài liệu"
    if page <= policy["front_pages"]:
        return policy["front_score"], f"nằm ở phần đầu báo cáo (trang {page})"
    return policy["rest_score"], f"nằm ở phần sau báo cáo (trang {page})"
