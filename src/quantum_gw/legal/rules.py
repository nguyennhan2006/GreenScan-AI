"""L3 — policy-as-code, and the checker that turns rules into a legal finding.

Two boundaries this module exists to hold:

**Not every clause becomes a rule.** Definitions, procedures and references are
not executable, and forcing them into `if x: compliant = True` produces
confident nonsense. A rule only exists where a clause states a checkable
condition, and every rule names the clause it came from.

**Unknown is a third outcome.** A condition with no evidence is `UNKNOWN`, never
`FAILED`. Collapsing the two would turn "we did not find the document" into "the
company does not comply", which is the single most damaging error this system
could make.

Rules are authored by a human and version-locked. A model may draft one, but the
path to production is: draft -> human review -> unit tests -> rule_pack version.
Nothing here reads a statute and generates its own rule at runtime.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# Condition outcomes.
SATISFIED = "SATISFIED"
NOT_SATISFIED = "NOT_SATISFIED"
UNKNOWN = "UNKNOWN"

# Findings.
MATCH = "MATCH"
PARTIAL_MATCH = "PARTIAL_MATCH"
NOT_MATCH = "NOT_MATCH"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

# Clause taxonomy — only some of these can ever be executed.
CLAUSE_TYPES = (
    "DEFINITION", "OBLIGATION", "PROHIBITION", "PERMISSION", "CONDITION",
    "EXCEPTION", "PROCEDURE", "REPORTING_REQUIREMENT", "THRESHOLD",
    "CLASSIFICATION_CRITERION", "REFERENCE_ONLY",
)
EXECUTABLE_TYPES = {"CONDITION", "THRESHOLD", "CLASSIFICATION_CRITERION",
                    "REPORTING_REQUIREMENT", "PROHIBITION"}


@dataclass
class Condition:
    id: str
    description: str
    source_clause: str
    # How the condition is decided. `manual` means a reviewer must answer it —
    # an honest outcome, and far better than a keyword match pretending to be
    # a legal judgement.
    check: str = "manual"
    requires_evidence: list[str] = field(default_factory=list)
    any_of_terms: list[str] = field(default_factory=list)
    numeric_field: str | None = None
    operator: str | None = None
    threshold: float | None = None


@dataclass
class Rule:
    rule_id: str
    title: str
    source_document: str
    source_clauses: list[str]
    claim_types: list[str]
    legal_issue: str
    conditions: list[Condition]
    effective_from: date | None = None
    effective_to: date | None = None
    # Who the rule governs. A rule that resolves for an issue is *relevant*; it
    # is *applicable* only to the subjects and sectors it names. A banking
    # circular retrieved for an environmental keyword governs banks, not a steel
    # mill, and the difference has to be in the data, not in a reviewer's head.
    applies_to_sectors: list[str] = field(default_factory=list)
    applies_to_subjects: list[str] = field(default_factory=list)
    machine_executable: str = "partial"
    reviewed_by: str = ""
    reviewed_at: str = ""
    notes: str = ""

    def in_force_on(self, when: date) -> bool:
        if self.effective_from and when < self.effective_from:
            return False
        if self.effective_to and when > self.effective_to:
            return False
        return True


class RulePack:
    def __init__(self, version: str, rules: list[Rule], source_registry: str = ""):
        self.version = version
        self.rules = rules
        self.source_registry = source_registry

    @classmethod
    def from_yaml(cls, path: str | Path) -> RulePack:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rules = []
        for r in raw.get("rules", []):
            conditions = [
                Condition(
                    id=c["id"], description=c["description"],
                    source_clause=c["source_clause"], check=c.get("check", "manual"),
                    requires_evidence=list(c.get("requires_evidence") or []),
                    any_of_terms=list(c.get("any_of_terms") or []),
                    numeric_field=c.get("numeric_field"), operator=c.get("operator"),
                    threshold=c.get("threshold"),
                )
                for c in r.get("conditions", [])
            ]
            if not conditions:
                raise ValueError(f"rule {r.get('rule_id')} has no conditions")
            rules.append(Rule(
                rule_id=r["rule_id"], title=r["title"],
                source_document=r["source_document"],
                source_clauses=list(r.get("source_clauses") or []),
                claim_types=list(r.get("claim_types") or []),
                legal_issue=r["legal_issue"], conditions=conditions,
                applies_to_sectors=[str(x).lower() for x in r.get("applies_to_sectors", [])],
                applies_to_subjects=[str(x).lower() for x in r.get("applies_to_subjects", [])],
                effective_from=_date(r.get("effective_from")),
                effective_to=_date(r.get("effective_to")),
                machine_executable=r.get("machine_executable", "partial"),
                reviewed_by=r.get("reviewed_by", ""),
                reviewed_at=r.get("reviewed_at", ""),
                notes=r.get("notes", ""),
            ))
        return cls(raw.get("version", "unversioned"), rules, raw.get("source_registry", ""))

    def for_claim(self, claim_type: str, legal_issue: str, as_of: date) -> list[Rule]:
        return [
            r for r in self.rules
            if r.legal_issue == legal_issue
            and (not r.claim_types or claim_type in r.claim_types)
            and r.in_force_on(as_of)
        ]


def applies_to(rule: Rule, sector: str | None, subject: str | None) -> tuple[bool, str]:
    """Does this rule govern this subject, or is it merely about the same topic?

    An empty list means the rule is silent about that dimension, and silence is
    not a match: it is treated as "governs all", because narrowing a rule that
    never declared its scope would silently drop findings. What is rejected is
    an explicit mismatch.
    """
    if rule.applies_to_sectors and sector:
        if sector.lower() not in rule.applies_to_sectors:
            return False, (
                f"quy tắc áp cho ngành {', '.join(rule.applies_to_sectors)}, "
                f"không áp cho ngành {sector}"
            )
    if rule.applies_to_subjects and subject:
        if subject.lower() not in rule.applies_to_subjects:
            return False, (
                f"quy tắc áp cho đối tượng {', '.join(rule.applies_to_subjects)}, "
                f"không áp cho {subject}"
            )
    return True, ""


def _date(value: Any) -> date | None:
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def evaluate_condition(condition: Condition, evidence: list[dict]) -> dict:
    """Decide one condition against retrieved company evidence.

    Returns UNKNOWN whenever the evidence does not speak to the condition. The
    only way to reach NOT_SATISFIED is for evidence to actually contradict it —
    silence is not refutation.
    """
    texts = [(e.get("text") or "") for e in evidence]
    blob = " ".join(texts).casefold()
    used = [e.get("chunk_id") for e in evidence if e.get("chunk_id")]

    if condition.check == "manual" or not blob.strip():
        return {
            "criterion": condition.description,
            "condition_id": condition.id,
            "source_clause": condition.source_clause,
            "status": UNKNOWN,
            "reason": ("Điều kiện này cần người xem xét quyết định."
                       if condition.check == "manual"
                       else "Không có bằng chứng nào được truy xuất cho điều kiện này."),
            "evidence_ids": [],
        }

    if condition.check == "terms_present":
        hits = [t for t in condition.any_of_terms if t.casefold() in blob]
        if hits:
            matched = [
                e.get("chunk_id") for e in evidence
                if any(t.casefold() in (e.get("text") or "").casefold()
                       for t in condition.any_of_terms)
            ]
            return {
                "criterion": condition.description, "condition_id": condition.id,
                "source_clause": condition.source_clause, "status": SATISFIED,
                "reason": f"Tìm thấy dấu hiệu: {', '.join(hits[:4])}.",
                "evidence_ids": [c for c in matched if c],
            }
        return {
            "criterion": condition.description, "condition_id": condition.id,
            "source_clause": condition.source_clause, "status": UNKNOWN,
            "reason": "Không tìm thấy thông tin về điều kiện này trong tài liệu đã truy xuất.",
            "evidence_ids": [],
        }

    if condition.check == "numeric_threshold":
        numbers = [float(x.replace(",", ".")) for x in
                   re.findall(r"\d+(?:[.,]\d+)?", blob)][:200]
        if not numbers or condition.threshold is None:
            return {
                "criterion": condition.description, "condition_id": condition.id,
                "source_clause": condition.source_clause, "status": UNKNOWN,
                "reason": "Không trích được giá trị số để so với ngưỡng.",
                "evidence_ids": [],
            }
        ops = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
               ">": lambda a, b: a > b, "<": lambda a, b: a < b}
        op = ops.get(condition.operator or ">=")
        if any(op(n, condition.threshold) for n in numbers):
            return {
                "criterion": condition.description, "condition_id": condition.id,
                "source_clause": condition.source_clause, "status": SATISFIED,
                "reason": f"Có giá trị thỏa {condition.operator} {condition.threshold}.",
                "evidence_ids": used[:3],
            }
        return {
            "criterion": condition.description, "condition_id": condition.id,
            "source_clause": condition.source_clause, "status": NOT_SATISFIED,
            "reason": (f"Không giá trị nào thỏa {condition.operator} {condition.threshold} "
                       f"trong bằng chứng đã truy xuất."),
            "evidence_ids": used[:3],
        }

    return {
        "criterion": condition.description, "condition_id": condition.id,
        "source_clause": condition.source_clause, "status": UNKNOWN,
        "reason": f"Kiểu kiểm tra '{condition.check}' chưa được hỗ trợ.",
        "evidence_ids": [],
    }


def combine(conditions: list[dict]) -> str:
    """Aggregate condition outcomes into a legal finding.

    Any refuted condition makes the whole rule NOT_MATCH. Otherwise unknowns
    dominate: a rule is only MATCH when every condition was positively
    established, because "nothing contradicted it" is not the same as "it holds".
    """
    if not conditions:
        return INSUFFICIENT_EVIDENCE
    statuses = [c["status"] for c in conditions]
    if NOT_SATISFIED in statuses:
        return NOT_MATCH
    if all(s == SATISFIED for s in statuses):
        return MATCH
    if all(s == UNKNOWN for s in statuses):
        return INSUFFICIENT_EVIDENCE
    return PARTIAL_MATCH
