"""Local masking: what may leave the machine in partial-offline mode.

Every quantity becomes a slot (<S1>, <E1>, ...) whose value stays here; years,
scope labels, clause numbers and units stay in the text because they carry the
meaning a model needs and are not sensitive. Entity names become
[DOANH_NGHIỆP], [CƠ_SỞ_A] ... Same rules as
benchmark/size_ladder_2026-10-10/run_masked.py (the pilot that measured them);
the product version will live in src/quantum_gw/privacy/ once the design is
accepted.
"""
from __future__ import annotations

import re

import quantum_gw.utils.text as T

_NUM = re.compile(r"(?<![\w./:\-])(\d[\d.,]*\d|\d)(?![\d/])")
_MULT_WORD = re.compile(r"\s*(triệu|tỷ|tỉ|nghìn|ngàn)(?!\w)", re.IGNORECASE)
_MULT = {"triệu": 1e6, "tỷ": 1e9, "tỉ": 1e9, "nghìn": 1e3, "ngàn": 1e3}
_RANGE = re.compile(r"(?<![\w./:])(\d[\d.,]*)\s*[-–]\s*(\d[\d.,]*)(?![\d/])")
_STANDARD_BEFORE = re.compile(r"(iso|tcvn|qcvn|iec|en|astm|gri)\s*$")
_SCOPE_BEFORE = re.compile(r"(pham vi|scope)\s*(?:[123]\s*(?:,|va|and|&|\+)?\s*)*$")
_YEAR = re.compile(r"(19|20|21)\d\d")


def tolerance(raw: str, value: float, mult: float, unit: str | None) -> float:
    """Half of the last published digit; percentages at their written decimals,
    other figures capped at 1% of the value."""
    if unit == "%":
        decimals = len(re.split(r"[.,]", raw.strip(".,"))[1]) if re.search(r"[.,]\d+$", raw) else 0
        return 0.5 * 10 ** (-decimals)
    return min(T._half_unit(raw, mult), 0.01 * abs(value)) or 0.5


def entity_patterns(names: list[str]) -> list[tuple[str, str]]:
    """Regexes for the reporting entity (first name) and its sites (the rest)."""
    out = []
    for i, name in enumerate(n for n in names if n.strip()):
        token = "[DOANH_NGHIỆP]" if i == 0 else f"[CƠ_SỞ_{chr(ord('A') + i - 1)}]"
        # words may be split by any whitespace, line breaks included (PDF text: "Hòa⏎Phát")
        out.append((r"\s+".join(re.escape(w) for w in name.split()), token))
    return out


def mask(text: str, prefix: str, entities: list[tuple[str, str]] = ()) -> tuple[str, dict]:
    """Return (masked text, {slot: {value, unit, half, raw}}). Nothing in the
    returned text is a figure except years and labels."""
    for pattern, token in entities:
        text = re.sub(pattern, token, text, flags=re.IGNORECASE)
    # A range "5.6-6.2%" / "750-900 độ C" is two figures, not an identifier like
    # "ISO 14064-1": space the dash so both numbers are masked.
    text = _RANGE.sub(lambda m: m.group(0) if _STANDARD_BEFORE.search(T.normalize_for_match(text[max(0, m.start() - 12):m.start()]))
                      else f"{m.group(1)} – {m.group(2)}", text)
    slots: dict[str, dict] = {}
    out, last = [], 0
    for m in _NUM.finditer(text):
        raw = m.group(1)
        before_norm = T.normalize_for_match(text[: m.start()][-30:])
        after = text[m.end():]
        if _YEAR.fullmatch(raw):
            continue
        if after[:1] in {"/", "-", ":"} and after[1:2].isdigit():
            continue
        line_start = text.rfind("\n", 0, m.start()) + 1
        if not text[line_start:m.start()].strip() and re.match(r"[.)]\s+\S", after):
            continue                                   # enumerator: "1. Tổng phát thải …"
        if line_start == 0 and not text[:m.start()].strip() and re.fullmatch(r"\d{1,3}", raw) and after[:1] == "\n":
            continue                                   # page number on the first line
        if _SCOPE_BEFORE.search(before_norm) or T._LABEL_RE.search(before_norm[-24:]):
            continue
        value = T._parse_locale_number(raw)
        if value is None:
            continue
        mult_m = _MULT_WORD.match(after)
        mult = _MULT[mult_m.group(1).lower()] if mult_m else 1.0
        end = m.end() + (mult_m.end() if mult_m else 0)
        unit_m = T._UNIT_RE.match(T.normalize_for_match(text[end:end + 20]))
        unit = T._canonical_unit(unit_m.group("unit")) if unit_m and unit_m.group("unit") else None
        name = f"{prefix}{len(slots) + 1}"
        slots[name] = {"value": value * mult, "unit": unit,
                       "half": tolerance(raw, value * mult, mult, unit), "raw": text[m.start():end], "start": m.start(),
                       "before": text[max(0, m.start() - 30):m.start()]}
        out.append(text[last:m.start()])
        out.append(f"<{name}>")
        last = end
    out.append(text[last:])
    return "".join(out), slots


def residual_digits(masked: str) -> list[str]:
    """Digits still present after masking, years excluded — should be labels only."""
    return [d for d in re.findall(r"\d[\d.,]*", masked) if not _YEAR.fullmatch(d)]
