"""Numeric facts and the rule that says when two of them may be compared.

Two figures that differ are not a contradiction until they are known to
measure the same thing. The Hòa Phát baseline run (benchmark/baseline_2026-09-22)
produced eight CONTRADICTED verdicts of which five compared figures that only
shared a unit:

    99% of emissions come from steel      vs  output grew 24%          (share vs change)
    23,474,480 tCO2e for the group        vs  90,846 tCO2e for one plant (group vs facility)
    0.70 tCO2/t steel, scrap-EAF route    vs  1.43, BF-BOF route         (technology)
    4.5% of energy from the grid          vs  0.03% renewable            (variant)

`parse_quantities` gives (value, unit, precision). A `NumericFact` adds the
dimensions along which the four cases differ, read from the sentence the
figure sits in, and `eligibility` decides COMPARABLE / NOT_COMPARABLE /
AMBIGUOUS before any arithmetic happens. Every dimension defaults to
"unknown", and unknown never blocks a comparison on its own: the rule is
"differ when both known", so a sentence that names no boundary is still
compared, and only an explicit mismatch stops it.

The vocabularies here are a first draft (ISSUES_REGISTER N1, RESEARCH_PROGRAM
RQ2). They are meant to be checked against the 50 hand-labelled numeric pairs
in data/gold/queues/, not to be complete.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from quantum_gw.utils.text import emission_scopes, normalize_for_match, parse_quantities

COMPARABLE = "COMPARABLE"
NOT_COMPARABLE = "NOT_COMPARABLE"
AMBIGUOUS = "AMBIGUOUS"

POLICY_ID = "comparison-policy-v2"

# --- measurement basis --------------------------------------------------------
# What a percentage is a percentage *of*. A share of a total and a change over
# a period are different quantities even when both are written "x%".
_CHANGE_RE = re.compile(
    r"(?<!\w)(?:tang|giam|cat giam|tiet kiem|reduc\w*|decreas\w*|increas\w*|cut|lower\w*|"
    r"so voi|compared (?:to|with)|year[- ]on[- ]year|yoy|muc tang|muc giam)(?!\w)"
)
_SHARE_RE = re.compile(
    r"(?<!\w)(?:chiem|ty trong|ty le|tren tong|trong tong|cua tong|tong (?:luong|so|tieu thu)|"
    r"share|proportion|of (?:total|the total)|out of|percent of|la nang luong|den tu|"
    r"duoc cung cap tu|accounts? for)(?!\w)"
)
_TARGET_RE = re.compile(
    r"(?<!\w)(?:muc tieu|target|cam ket|huong toi|huong den|den nam 20\d\d|by 20\d\d|"
    r"phan dau|ke hoach|du kien|se dat|aim|goal|pledge)(?!\w)"
)
_INTENSITY_RE = re.compile(
    r"(?<!\w)(?:cuong do|intensity|per (?:tonne|ton|unit|mwh|kwh)|/\s*(?:tan|t|mwh|kwh|san pham|"
    r"tonne|ton)|tren (?:moi )?(?:tan|don vi|san pham|mwh|kwh)|moi tan)(?!\w)"
)

# --- organisational boundary --------------------------------------------------
# One plant, one subsidiary, or the consolidated group. Ordered from most to
# least specific: a sentence about "nhà máy X của Tập đoàn" is about the plant.
_BOUNDARY_PATTERNS = (
    ("project", re.compile(r"(?<!\w)(?:du an|project)(?!\w)")),
    ("facility", re.compile(
        r"(?<!\w)(?:nha may|khu lien hop|co so san xuat|co so|facility|facilities|plant|site|"
        r"chi nhanh|phan xuong|dung quat|hai duong|kinh mon)(?!\w)"
    )),
    ("subsidiary", re.compile(
        r"(?<!\w)(?:cong ty con|cong ty thanh vien|don vi thanh vien|subsidiary|subsidiaries|"
        r"cong ty tnhh|cong ty co phan|ctcp)(?!\w)"
    )),
    ("group", re.compile(
        r"(?<!\w)(?:tap doan|toan tap doan|hop nhat|toan he thong|group|consolidated|group-wide|"
        r"toan cong ty|cap tap doan)(?!\w)"
    )),
)

# --- production technology ----------------------------------------------------
# Steel routes and power sources: an intensity per tonne is only comparable
# within a route.
_TECHNOLOGY_PATTERNS = (
    ("dri_eaf", re.compile(r"(?<!\w)(?:dri[- ]?eaf|dri)(?!\w)")),
    ("scrap_eaf", re.compile(r"(?<!\w)(?:scrap[- ]?eaf|eaf|lo dien|lo ho quang|electric arc)(?!\w)")),
    ("bf_bof", re.compile(r"(?<!\w)(?:bf[- ]?bof|bof|lo cao|lo thoi|blast furnace|basic oxygen)(?!\w)")),
    ("solar", re.compile(r"(?<!\w)(?:dien mat troi|mat troi|solar|pv)(?!\w)")),
    ("wind", re.compile(r"(?<!\w)(?:dien gio|wind)(?!\w)")),
    ("hydro", re.compile(r"(?<!\w)(?:thuy dien|hydro)(?!\w)")),
    ("biomass", re.compile(r"(?<!\w)(?:sinh khoi|biomass)(?!\w)")),
)

# --- metric variant -----------------------------------------------------------
# Sub-metric within one taxonomy bucket. Energy: what kind of energy the share
# is a share of. Emissions: total vs intensity is handled by `basis`; scopes by
# `scopes`.
_VARIANT_PATTERNS = (
    # waste: hazardous vs not, and what happened to it. "không nguy hại" contains
    # "nguy hại", so the negated form is listed first.
    ("non_hazardous", re.compile(r"(?<!\w)(?:khong nguy hai|non[- ]hazardous)(?!\w)")),
    ("hazardous", re.compile(r"(?<!\w)(?:nguy hai|hazardous)(?!\w)")),
    ("recovered", re.compile(r"(?<!\w)(?:tai che|tai su dung|thu hoi|recycl\w*|reus\w*|recover\w*|diverted)(?!\w)")),
    ("disposed", re.compile(r"(?<!\w)(?:thai bo|tieu huy|chon lap|dot|landfill\w*|incinerat\w*|dispos\w*)(?!\w)")),
    ("renewable", re.compile(r"(?<!\w)(?:tai tao|renewable|nang luong sach|nang luong xanh|re100)(?!\w)")),
    ("grid", re.compile(r"(?<!\w)(?:luoi dien|luoi|grid|evn|dien mua)(?!\w)")),
    ("fossil", re.compile(r"(?<!\w)(?:hoa thach|fossil|than|coal|dau|oil|khi dot|gas)(?!\w)")),
)

# A gap this wide between two figures of the same unit is far more often a
# boundary, sector or unit mismatch than a misstatement (nobody claims 23
# million where the table says 90 thousand). Below MAGNITUDE_GAP_ALWAYS the
# gap only abstains when a dimension is unknown on either side; at or above it
# the pair goes to a reviewer even with every dimension read as equal, because
# the reading is a regex over one sentence and a 100x gap is stronger evidence
# that the reading missed something than that the company did. Both numbers
# are hypotheses to sweep on the numeric-pair gold set (RESEARCH_PROGRAM RQ3).
MAGNITUDE_GAP = 20.0
MAGNITUDE_GAP_ALWAYS = 100.0


@dataclass(frozen=True)
class NumericFact:
    value: float
    unit: str | None
    half: float
    basis: str = "unknown"          # absolute | intensity | percentage_share | percentage_change | unknown
    is_target: bool = False
    boundary: str = "unknown"       # group | subsidiary | facility | project | unknown
    technology: str | None = None
    variant: frozenset[str] = frozenset()   # every variant tag the figure's context names
    scopes: frozenset[int] = frozenset()
    sentence: str = ""

    def as_tuple(self) -> tuple[float, str | None, float]:
        return (self.value, self.unit, self.half)

    def dimensions(self) -> dict:
        return {
            "basis": self.basis,
            "is_target": self.is_target,
            "boundary": self.boundary,
            "technology": self.technology,
            "variant": "+".join(sorted(self.variant)) or None,
            "scopes": "+".join(str(s) for s in sorted(self.scopes)) or None,
        }


def _first(patterns, folded: str) -> str | None:
    for name, pattern in patterns:
        if pattern.search(folded):
            return name
    return None


def _all(patterns, folded: str) -> frozenset[str]:
    """Every tag that matches: a hazardous-waste figure that was recycled carries both."""
    return frozenset(name for name, pattern in patterns if pattern.search(folded))


def _basis(folded: str, unit: str | None, window: str) -> str:
    """Basis of one figure, read from the words around it first, then the sentence."""
    if unit == "%":
        for scope in (window, folded):
            change, share = bool(_CHANGE_RE.search(scope)), bool(_SHARE_RE.search(scope))
            if change and not share:
                return "percentage_change"
            if share and not change:
                return "percentage_share"
            if change and share:
                break  # both in the same span: let the sentence-level reading decide, else unknown
        return "unknown"
    if unit is not None and _INTENSITY_RE.search(folded):
        return "intensity"
    if unit is not None:
        return "absolute"
    return "unknown"


def _window(folded: str, value: float, unit: str | None, width: int = 48) -> str:
    """The words around the first occurrence of the figure, for cues that sit next to it.

    A sentence can carry several figures about several things ("BF-BOF: 2,32
    ... DRI-EAF: 1,43"), so technology, variant and basis are read next to the
    figure first and from the whole sentence only as a fallback.
    """
    if float(value).is_integer():
        digits = str(int(value))
        candidates = [f"{int(value):,}".replace(",", "."), f"{int(value):,}", digits]
    else:
        candidates = [str(value).replace(".", ","), str(value)]
    if unit == "%":
        candidates = [c + "%" for c in candidates] + candidates
    for token in candidates:
        at = folded.find(token)
        if at >= 0:
            return folded[max(0, at - width): at + len(token) + width]
    return folded


def facts_in(sentence: str, drop_years: bool = True) -> list[NumericFact]:
    """Every quantity in one sentence, with the dimensions the sentence states."""
    folded = normalize_for_match(sentence)
    # "Công ty Cổ phần Tập đoàn X" is the group's legal name, not a subsidiary.
    folded = re.sub(r"cong ty co phan tap doan", "tap doan", folded)
    scopes = emission_scopes(sentence)
    is_target = bool(_TARGET_RE.search(folded))
    facts = []
    for value, unit, half in parse_quantities(sentence):
        if drop_years and unit is None and 1900 <= value <= 2100:
            continue
        window = _window(folded, value, unit, width=32)
        facts.append(NumericFact(
            value=value, unit=unit, half=half,
            basis=_basis(folded, unit, window),
            is_target=is_target,
            boundary=_first(_BOUNDARY_PATTERNS, window) or _first(_BOUNDARY_PATTERNS, folded) or "unknown",
            technology=_first(_TECHNOLOGY_PATTERNS, window) or _first(_TECHNOLOGY_PATTERNS, folded),
            variant=_all(_VARIANT_PATTERNS, window) or _all(_VARIANT_PATTERNS, folded),
            scopes=scopes, sentence=sentence,
        ))
    return facts


def _both_known_and_differ(a, b, unknown=("unknown", None)) -> bool:
    return a not in unknown and b not in unknown and a != b


def eligibility(claim: NumericFact, evidence: NumericFact) -> tuple[str, str | None]:
    """(COMPARABLE | NOT_COMPARABLE | AMBIGUOUS, reason).

    Reasons use the labels of the numeric-pair gold set so a mismatch between
    the code and a reviewer's label is a one-line diff:
    different_unit · different_basis · different_boundary · different_technology
    · different_variant · different_scope · target_vs_actual · magnitude_gap.
    """
    if claim.unit is None or evidence.unit is None or claim.unit != evidence.unit:
        return NOT_COMPARABLE, "different_unit"
    if _both_known_and_differ(claim.basis, evidence.basis):
        return NOT_COMPARABLE, "different_basis"
    if _both_known_and_differ(claim.boundary, evidence.boundary):
        return NOT_COMPARABLE, "different_boundary"
    if _both_known_and_differ(claim.technology, evidence.technology):
        return NOT_COMPARABLE, "different_technology"
    if claim.variant and evidence.variant and claim.variant != evidence.variant:
        return NOT_COMPARABLE, "different_variant"
    if claim.scopes and evidence.scopes and claim.scopes != evidence.scopes:
        return NOT_COMPARABLE, "different_scope"
    # A target is not an actual. The claim may itself be a target ("giảm 30%
    # đến 2030"); then a target in the evidence is the right thing to compare.
    if claim.is_target != evidence.is_target:
        return AMBIGUOUS, "target_vs_actual"
    unknown_side = any(
        d in ("unknown", None)
        for d in (claim.basis, evidence.basis, claim.boundary, evidence.boundary)
    )
    ratio = max(abs(claim.value), abs(evidence.value)) / max(min(abs(claim.value), abs(evidence.value)), 1e-9)
    if ratio >= MAGNITUDE_GAP_ALWAYS or (unknown_side and ratio >= MAGNITUDE_GAP):
        return AMBIGUOUS, "magnitude_gap"
    return COMPARABLE, None


REASON_TEXT_VI = {
    "different_unit": "khác đơn vị",
    "different_basis": "khác cơ sở đo (tỷ trọng / mức thay đổi / tuyệt đối / cường độ)",
    "different_boundary": "khác ranh giới tổ chức (tập đoàn / công ty con / nhà máy / dự án)",
    "different_technology": "khác công nghệ sản xuất",
    "different_variant": "khác loại chỉ số con",
    "different_scope": "khác ranh giới phát thải (Scope)",
    "target_vs_actual": "một bên là mục tiêu, một bên là số thực hiện",
    "magnitude_gap": "chênh lệch hàng chục lần trở lên — thường là khác ranh giới, ngành hoặc đơn vị; cần người xem",
}


def describe(reason: str | None) -> str:
    return REASON_TEXT_VI.get(reason or "", reason or "")
