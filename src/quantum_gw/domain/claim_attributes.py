"""Claim detection split in two: what a model reads, and what a policy decides.

The T1 label (QUANTIFIED_CLAIM / QUALITATIVE_CLAIM / VAGUE / NOT_CLAIM) mixes
two kinds of knowledge:

* **Facts about the sentence** that are the same for every company and every
  user: is it a table cell, who is acting, is there an environmental quantity,
  is it a target with only a year. A model can learn these once.
* **Conventions** that a user may rightly decide differently: does a target
  with only a year count as a claim, does a count of certified plants count as
  a figure, is the company's own ESG process a claim. Codebook v1.1 fixed one
  answer for each (Q6, Q10, Q11, Q12, Q15, Q17), and several are marked "not
  yet agreed by the human team".

When a model is trained on the final label, the conventions are baked into its
weights: a user with another convention can only retrain it, and a reviewer's
company-specific exception, fed back as a label, teaches the model to break the
convention everywhere. Here the model's job ends at `ClaimAttributes`;
`compose_label` turns attributes into a label under a `ClaimPolicy`, in code,
deterministically. Changing a convention is a policy change, testable and
versioned, not a training run.

`ClaimPolicy()` reproduces codebook v1.1, so labels composed with the default
policy are comparable to every label made so far.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

import yaml

# Labels and NOT_CLAIM reasons, as in training/data/claude/CODEBOOK.md.
QUANTIFIED = "QUANTIFIED_CLAIM"
QUALITATIVE = "QUALITATIVE_CLAIM"
VAGUE = "VAGUE"
NOT_CLAIM = "NOT_CLAIM"
LABELS = (QUANTIFIED, QUALITATIVE, VAGUE, NOT_CLAIM)
# Order matters (codebook Q8): when several reasons hold, the earliest wins.
WHY_NOT = ("table_heading", "broken", "other_org", "general_knowledge", "non_env", "other")

# --- the facts a model reads ---------------------------------------------------

FORMS = ("sentence", "table_or_heading", "broken")
# Who acts or whose state the sentence describes. `client_project` is the green
# feature of a project the company only builds for a client (codebook Q15).
SPEAKERS = ("issuer", "other_org", "client_project")
# What kind of statement it is, where the codebook treats kinds differently.
KINDS = (
    "action_or_state",  # a measure, result or present environmental state of the company (Q17 state)
    "esg_process",      # how the company runs ESG: policy, board, inventory, GRI, assurance (Q12)
    "award",            # a sustainability award or ranking of the company (Q11)
    "compliance",       # "we comply with environmental regulations" (Q17)
    "report_meta",      # about the report itself: period, scope, purpose (Q12)
)
# The environmental number in the sentence, if any. Years, standard numbers and
# document numbers are never a quantity (Q7); non-environmental numbers neither.
QUANTITIES = ("none", "measure", "count")  # count: "26 plants certified ISO 14001" (Q10)


class InvalidAttributes(ValueError):
    """Attributes outside their allowed values."""


@dataclass(frozen=True)
class ClaimAttributes:
    form: str = "sentence"
    speaker: str = "issuer"
    environmental: bool = True       # any environmental content (Q14: "bền vững" as business longevity is not)
    general_knowledge: bool = False  # general effect of a technology, not the company's own measure (Q2)
    kind: str = "action_or_state"
    concrete: bool = True            # a checkable action, result or state, not a slogan or value
    quantity: str = "none"
    target: bool = False             # a future target or commitment
    target_year: bool = False        # the target names a year

    def __post_init__(self) -> None:
        problems = [
            f"{name}={value!r} (allowed: {allowed})"
            for name, value, allowed in (
                ("form", self.form, FORMS), ("speaker", self.speaker, SPEAKERS),
                ("kind", self.kind, KINDS), ("quantity", self.quantity, QUANTITIES),
            )
            if value not in allowed
        ]
        if problems:
            raise InvalidAttributes("; ".join(problems))

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ClaimAttributes:
        known = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            raise InvalidAttributes(f"unknown attribute(s): {unknown}")
        return cls(**data)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


# --- the conventions a user may set ----------------------------------------------

@dataclass(frozen=True)
class ClaimPolicy:
    """Conventions, defaulting to codebook v1.1."""

    policy_id: str = "codebook_v1_1"
    year_only_target: str = QUALITATIVE        # Q6: "carbon neutral by 2050"; a user may say VAGUE
    count_is_quantity: bool = True             # Q10
    esg_process_is_claim: bool = True          # Q12 and the "clarification" the humans have not agreed
    award_is_claim: bool = True                # Q11
    compliance_is_claim: bool = True           # Q17; a user may treat bare compliance as VAGUE
    client_project_is_claim: bool = False      # Q15

    def __post_init__(self) -> None:
        if self.year_only_target not in (QUALITATIVE, VAGUE, NOT_CLAIM):
            raise ValueError(f"year_only_target must be QUALITATIVE_CLAIM, VAGUE or NOT_CLAIM, not {self.year_only_target!r}")

    @classmethod
    def load(cls, path: str | Path) -> ClaimPolicy:
        """Read a policy file; unknown keys refuse the file (fail closed, like org packs)."""
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        known = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            raise ValueError(f"{path}: unknown policy key(s) {unknown}; a convention understood halfway is not applied")
        return cls(**data)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComposedLabel:
    label: str
    why_not: str | None
    # Which conventions decided this label, so a reviewer who disagrees can see
    # whether the model misread (an attribute is wrong) or the convention does
    # not fit (a policy key) — the same split as storage/reviews.py.
    decided_by: tuple[str, ...]
    policy_id: str


def compose_label(attrs: ClaimAttributes, policy: ClaimPolicy | None = None) -> ComposedLabel:
    """The T1 label from attributes, under a policy. Pure and deterministic."""
    policy = policy or ClaimPolicy()

    def out(label: str, why_not: str | None = None, *keys: str) -> ComposedLabel:
        return ComposedLabel(label, why_not, tuple(keys), policy.policy_id)

    # NOT_CLAIM reasons, in codebook order (Q8).
    if attrs.form == "table_or_heading":
        return out(NOT_CLAIM, "table_heading")
    if attrs.form == "broken":
        return out(NOT_CLAIM, "broken")
    if attrs.speaker == "other_org":
        return out(NOT_CLAIM, "other_org")
    if attrs.speaker == "client_project" and not policy.client_project_is_claim:
        return out(NOT_CLAIM, "other_org", "client_project_is_claim")
    if attrs.general_knowledge:
        return out(NOT_CLAIM, "general_knowledge")
    if attrs.kind == "report_meta":
        return out(NOT_CLAIM, "other")
    if not attrs.environmental:
        return out(NOT_CLAIM, "non_env")

    keys: list[str] = []
    if attrs.speaker == "client_project":
        keys.append("client_project_is_claim")
    if attrs.kind == "esg_process":
        if not policy.esg_process_is_claim:
            return out(NOT_CLAIM, "other", "esg_process_is_claim")
        keys.append("esg_process_is_claim")
    if attrs.kind == "award":
        if not policy.award_is_claim:
            return out(NOT_CLAIM, "non_env", "award_is_claim")
        keys.append("award_is_claim")
    if attrs.kind == "compliance":
        if not policy.compliance_is_claim:
            return out(VAGUE, None, "compliance_is_claim")
        keys.append("compliance_is_claim")

    # A claim. Which kind: a figure first, then a year-only target, then how concrete.
    if attrs.quantity == "measure":
        return out(QUANTIFIED, None, *keys)
    if attrs.quantity == "count":
        if policy.count_is_quantity:
            return out(QUANTIFIED, None, *keys, "count_is_quantity")
        keys.append("count_is_quantity")
    if attrs.target and attrs.target_year:
        label = policy.year_only_target
        return out(label, "other" if label == NOT_CLAIM else None, *keys, "year_only_target")
    if not attrs.concrete:
        return out(VAGUE, None, *keys)
    return out(QUALITATIVE, None, *keys)
