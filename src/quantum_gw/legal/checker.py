"""The legal check: claim + evidence + corpus + rule pack -> a legal finding.

The output is a *legal check record*, not a verdict about a company. It says
which instrument was consulted, which clause, which condition held, which was
unknown, and whether a human must look. It never says "doanh nghiệp vi phạm".

Ordering matters and is deliberate: the applicable law is resolved *before* any
rule runs, so a check can fail cleanly at "we could not read the governing
instrument" instead of quietly evaluating against nothing.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from .corpus import CHECK_MODES, CURRENT, LegalCorpus
from .rules import (
    INSUFFICIENT_EVIDENCE,
    MATCH,
    NOT_MATCH,
    PARTIAL_MATCH,
    RulePack,
    combine,
    evaluate_condition,
)

# claim_type -> the legal question it raises.
#
# The keys must be the claim types configs/taxonomy.yaml actually produces. They
# were not: this map was written against a vocabulary (green_project, green_bond,
# ghg_inventory) that the extractor never emits, so five of the eight real claim
# types silently fell through to the `green_taxonomy` default and were checked
# against the wrong instrument. The taxonomy types are listed first below and the
# older keys are kept because the rule pack still references them in its
# `claim_types` filters.
CLAIM_TYPE_TO_ISSUE = {
    # Produced by configs/taxonomy.yaml.
    "emissions_reduction": "emissions",
    "renewable_energy": "green_taxonomy",
    "resource_efficiency": "green_taxonomy",
    "waste_and_circularity": "environmental_protection",
    # Covers both bonds and credit. green_credit resolves to more instruments
    # with extracted text (QĐ 21/2025 plus TT 17/2022), so a check on it is more
    # likely to reach a rule than to stop at "could not read the instrument".
    "green_finance": "green_credit",
    "biodiversity": "environmental_protection",
    # Claims about how the firm works rather than about a physical outcome are a
    # disclosure question, not a green-taxonomy one: what is at issue is whether
    # the description of the process was accurate, which is what BNY-2022 and
    # DWS-2023 were charged under.
    "esg_process_integration": "disclosure",
    "generic_sustainability": "green_taxonomy",
    # Referenced by rule-pack claim_types filters.
    "green_project": "green_taxonomy",
    "green_taxonomy_eligibility": "green_taxonomy",
    "green_bond": "green_bond",
    "green_credit": "green_credit",
    "ghg_inventory": "ghg_inventory",
}

RISK_BY_FINDING = {
    NOT_MATCH: "HIGH",
    PARTIAL_MATCH: "MEDIUM",
    INSUFFICIENT_EVIDENCE: "MEDIUM",
    MATCH: "LOW",
}


@dataclass
class LegalCheckResult:
    legal_check_id: str
    claim_id: str
    issue: str
    check_mode: str
    as_of_date: str
    applicable_sources: list[dict] = field(default_factory=list)
    blocked_sources: list[dict] = field(default_factory=list)
    conditions: list[dict] = field(default_factory=list)
    legal_finding: str = INSUFFICIENT_EVIDENCE
    legal_risk: str = "MEDIUM"
    rule_pack_version: str = ""
    rules_applied: list[str] = field(default_factory=list)
    requires_human_review: bool = True
    notes: str = ""

    def to_json(self) -> dict:
        return asdict(self)


class LegalChecker:
    def __init__(self, corpus: LegalCorpus, rule_pack: RulePack):
        self.corpus = corpus
        self.rule_pack = rule_pack

    def check(
        self,
        *,
        claim: dict[str, Any],
        evidence: list[dict],
        check_mode: str = CURRENT,
        claim_published: date | None = None,
        today: date | None = None,
    ) -> LegalCheckResult:
        if check_mode not in CHECK_MODES:
            raise ValueError(f"Unknown check_mode {check_mode!r}; expected {CHECK_MODES}")
        today = today or datetime.now(UTC).date()
        as_of = self.corpus.resolve_as_of(check_mode, claim_published, today)

        claim_type = claim.get("claim_type") or "generic_sustainability"
        issue = CLAIM_TYPE_TO_ISSUE.get(claim_type, "green_taxonomy")

        result = LegalCheckResult(
            legal_check_id=f"LC-{uuid.uuid4().hex[:10]}",
            claim_id=claim.get("claim_id", ""),
            issue=issue,
            check_mode=check_mode,
            as_of_date=as_of.isoformat(),
            rule_pack_version=self.rule_pack.version,
        )

        usable = self.corpus.applicable(issue, as_of)
        blocked = self.corpus.blocked(issue, as_of)
        result.blocked_sources = [
            {"document": d.document_number, "id": d.id,
             "text_acquisition": d.text_acquisition,
             "reason": d.text_acquisition_note or "Chưa trích được toàn văn."}
            for d in blocked
        ]

        if not usable:
            # The honest terminal state: an instrument governs this issue but we
            # have not read it. Reporting MATCH or NOT_MATCH here would be a
            # claim about law the system never saw.
            result.legal_finding = INSUFFICIENT_EVIDENCE
            result.legal_risk = "MEDIUM"
            result.requires_human_review = True
            result.notes = (
                "Không có văn bản nào vừa có hiệu lực vừa đã trích được toàn văn cho "
                f"vấn đề '{issue}' tại ngày {as_of.isoformat()}. "
                + ("Văn bản đang thiếu toàn văn: "
                   + ", ".join(d.document_number for d in blocked) + ". "
                   if blocked else "")
                + "Không thể kết luận pháp lý khi chưa đọc được văn bản điều chỉnh."
            )
            return result

        # One amending decree commonly appears in the chain of several base
        # instruments, so the same document would be listed two or three times.
        # A reviewer reading that sees more instruments than actually govern the
        # claim, so each is recorded once, keeping the first role it appeared in
        # (a document reached as a base is a base, not an amendment).
        seen_sources: set[str] = set()
        for doc in usable:
            for member in self.corpus.effective_chain(doc.id, as_of):
                if member.id in seen_sources:
                    continue
                seen_sources.add(member.id)
                result.applicable_sources.append({
                    "document": member.document_number,
                    "id": member.id,
                    "title": member.title,
                    "effective_from": member.effective_from.isoformat()
                    if member.effective_from else None,
                    "source_url": member.landing_url or member.original_url,
                    "role": "base" if member.id == doc.id else "amendment_in_force",
                })

        rules = self.rule_pack.for_claim(claim_type, issue, as_of)
        result.rules_applied = [r.rule_id for r in rules]
        if not rules:
            result.legal_finding = INSUFFICIENT_EVIDENCE
            result.notes = (
                f"Có văn bản áp dụng nhưng rule pack '{self.rule_pack.version}' chưa có "
                f"rule nào cho claim_type '{claim_type}' / vấn đề '{issue}'. "
                "Rule phải do người soạn và duyệt, không sinh tự động lúc chạy."
            )
            return result

        for rule in rules:
            for condition in rule.conditions:
                result.conditions.append(evaluate_condition(condition, evidence))

        result.legal_finding = combine(result.conditions)
        result.legal_risk = RISK_BY_FINDING.get(result.legal_finding, "MEDIUM")
        # Always true for anything short of a clean MATCH, and true for MATCH too
        # while rules remain only partially executable.
        result.requires_human_review = (
            result.legal_finding != MATCH
            or any(r.machine_executable != "full" for r in rules)
        )
        unknown = sum(1 for c in result.conditions if c["status"] == "UNKNOWN")
        if unknown:
            result.notes = (
                f"{unknown}/{len(result.conditions)} điều kiện chưa xác định được từ bằng "
                "chứng hiện có. Chưa xác định KHÔNG đồng nghĩa không đáp ứng."
            )
        return result
