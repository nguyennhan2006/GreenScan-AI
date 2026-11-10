"""IR of one quantitative environmental figure + deterministic comparison (GreenScan AG-1, GS-Bench v1).

A model may fill the IR; every number, unit, period, scope and boundary check is done here, so the
verdict always points at an arithmetic step (invariants 4-6 of ARCHITECTURE_INVARIANTS.md):
  - one dimension differs (metric, value kind, status, period, scope, boundary, unit) -> N, never C;
  - a target never proves a result;
  - values match within the precision each side was published to.
Pure stdlib so the same file runs on Kaggle and in the product.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

METRICS = {
    "ghg_emissions": "phát thải khí nhà kính",
    "energy_consumption": "tiêu thụ năng lượng",
    "electricity_consumption": "tiêu thụ điện",
    "renewable_energy": "năng lượng tái tạo (sản xuất hoặc sử dụng)",
    "fuel_consumption": "tiêu thụ nhiên liệu (than, dầu, khí, sinh khối)",
    "water_use": "nước khai thác / sử dụng / tiêu thụ",
    "wastewater": "nước thải phát sinh / xử lý / tuần hoàn",
    "waste_generated": "chất thải phát sinh",
    "waste_recycled": "chất thải tái chế / tái sử dụng / thu hồi",
    "hazardous_waste": "chất thải nguy hại",
    "recycled_input": "nguyên liệu tái chế đưa vào sản xuất",
    "air_pollutants": "bụi, SO2, NOx, khí thải khác",
    "land_trees": "trồng cây, diện tích xanh, rừng",
    "other_env": "chỉ số môi trường khác",
}
VALUE_KINDS = ("absolute", "intensity", "share", "change", "count")
STATUSES = ("actual", "target")
SCOPES = ("s1", "s2", "s3", "s1+s2", "s1+s2+s3")
BOUNDARIES = ("group", "parent", "facility", "unspecified")

MULTIPLIERS = {"nghìn": 1e3, "ngàn": 1e3, "ngàn tỷ": 1e12, "nghìn tỷ": 1e12, "triệu": 1e6, "tỷ": 1e9, "tỉ": 1e9,
               "thousand": 1e3, "million": 1e6, "billion": 1e9, "": 1.0}

# unit text -> (dimension, factor to the dimension's base unit)
_UNITS = [
    (r"(kt|nghìn tấn) ?co2", ("ghg_t", 1e3)), (r"kg ?co2", ("ghg_t", 1e-3)), (r"(t|tấn) ?co2", ("ghg_t", 1.0)),
    (r"twh", ("energy_kwh", 1e9)), (r"gwh", ("energy_kwh", 1e6)), (r"mwh", ("energy_kwh", 1e3)), (r"kwh", ("energy_kwh", 1.0)),
    (r"toe", ("energy_kwh", 11_630.0)), (r"\btj\b", ("energy_kwh", 277_777.8)), (r"\bgj\b", ("energy_kwh", 277.7778)),
    (r"\bmwp?\b", ("power_mw", 1.0)), (r"\bkwp?\b", ("power_mw", 1e-3)),
    (r"m3|m³|khối", ("volume_m3", 1.0)), (r"lít|\bl\b", ("volume_m3", 1e-3)),
    (r"tấn|\bt\b|tons?|tonnes?", ("mass_t", 1.0)), (r"\bkg\b", ("mass_t", 1e-3)),
    (r"%|phần trăm", ("percent", 1.0)), (r"\bha\b|hecta|héc", ("area_ha", 1.0)), (r"cây|trees?", ("count_tree", 1.0)),
]


def unit_dimension(unit_text: str) -> tuple[str, float]:
    """Dimension and factor of a unit; an intensity keeps its denominator ('ghg_t/tấn thép')."""
    text = (unit_text or "").strip().lower()
    num, _, den = text.partition("/")
    dim, factor = next(((d, f) for pattern, (d, f) in _UNITS if re.search(pattern, num)), (num or "none", 1.0))
    if den:
        dim += "/" + re.sub(r"\s+", " ", den.strip())
    return dim, factor


def parse_number(text: str) -> tuple[float, float]:
    """Value of a written number and half its last written digit (the published precision).

    Vietnamese writes 22.540.603 and 23,5; some reports use 1,234.5. A separator followed by exactly
    three digits is read as a thousands separator, any other as the decimal mark.
    """
    s = re.sub(r"\s", "", text or "")
    if not re.fullmatch(r"[\d.,]+", s) or not re.search(r"\d", s):
        raise ValueError(f"not a number: {text!r}")
    if "." in s and "," in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        integer, decimals = s.replace("." if dec == "," else ",", "").split(dec)
    elif s.count(".") > 1 or s.count(",") > 1:
        integer, decimals = re.sub(r"[.,]", "", s), ""
    elif "." in s or "," in s:
        integer, decimals = re.split(r"[.,]", s)
        if len(decimals) == 3:
            integer, decimals = integer + decimals, ""
    else:
        integer, decimals = s, ""
    value = float(f"{integer or 0}.{decimals or 0}")
    return value, 0.5 * 10 ** (-len(decimals))


@dataclass
class IR:
    metric: str
    value_text: str
    unit_text: str = ""
    multiplier_text: str = ""
    value_kind: str = "absolute"
    change_direction: str | None = None  # decrease | increase, for value_kind == change
    baseline_year: int | None = None
    period: int | None = None
    status: str = "actual"
    scope: str | None = None
    boundary: str = "unspecified"
    metric_text: str = ""
    subject_text: str = ""
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> IR:
        known = {k: d.get(k) for k in cls.__dataclass_fields__ if k in d and k != "extra"}
        ir = cls(**known)
        ir.boundary = ir.boundary or "unspecified"
        ir.status = ir.status or "actual"
        ir.value_kind = ir.value_kind or "absolute"
        for name in ("period", "baseline_year"):
            v = getattr(ir, name)
            setattr(ir, name, int(v) if v not in (None, "", "null") and str(v).isdigit() else None)
        return ir

    def as_dict(self) -> dict:
        return asdict(self)

    def quantity(self) -> tuple[float, float, str]:
        """Value and tolerance in the dimension's base unit, and the dimension."""
        value, half = parse_number(self.value_text)
        mult = MULTIPLIERS.get((self.multiplier_text or "").strip().lower(), 1.0)
        dim, factor = unit_dimension(self.unit_text)
        return value * mult * factor, half * mult * factor, dim


def comparable(claim: IR, evidence: IR) -> tuple[bool, str]:
    """Same metric, value kind, status, period, scope, boundary and unit dimension (invariant 4)."""
    checks = [
        ("chỉ số", claim.metric, evidence.metric),
        ("loại giá trị", claim.value_kind, evidence.value_kind),
        ("thực hiện / mục tiêu", claim.status, evidence.status),
        ("kỳ", claim.period, evidence.period),
        ("phạm vi phát thải", claim.scope, evidence.scope),
    ]
    if claim.value_kind == "change":
        checks.append(("năm gốc", claim.baseline_year, evidence.baseline_year))
    if "unspecified" not in (claim.boundary, evidence.boundary):
        checks.append(("ranh giới tổ chức", claim.boundary, evidence.boundary))
    for name, a, b in checks:
        if a != b:
            return False, f"khác {name}: {a} / {b}"
    try:
        dim_c, dim_e = claim.quantity()[2], evidence.quantity()[2]
    except ValueError as exc:
        return False, f"không đọc được số: {exc}"
    if dim_c != dim_e:
        return False, f"khác đơn vị: {dim_c} / {dim_e}"
    return True, "so được"


def compare(claim: IR, evidence: IR) -> tuple[str, str]:
    """S (khớp), C (mâu thuẫn) or N (không so được), with the arithmetic or the reason."""
    ok, why = comparable(claim, evidence)
    if not ok:
        return "N", why
    if claim.value_kind == "change" and claim.change_direction != evidence.change_direction:
        return "C", f"ngược chiều: {claim.change_direction} / {evidence.change_direction}"
    vc, tc, dim = claim.quantity()
    ve, te, _ = evidence.quantity()
    gap = abs(vc - ve)
    label = "S" if gap <= tc + te else "C"
    return label, f"|{vc:g} − {ve:g}| = {gap:g} {dim}; dung sai {tc + te:g}"


def decide(claim: IR, evidence: list[IR]) -> tuple[str, list[tuple[str, str]]]:
    """Verdict over every evidence figure: S if some comparable figure matches and none conflicts,
    C if comparable figures only conflict, N otherwise (nothing comparable, or mixed: a person reads it)."""
    steps = [compare(claim, e) for e in evidence]
    labels = {label for label, _ in steps if label != "N"}
    return (labels.pop() if len(labels) == 1 else "N"), steps
