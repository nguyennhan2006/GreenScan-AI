"""GS-Mutation v1: one planted error per case, from GS-Bench v1 pairs of real companies.

M0 original (S and N pairs) · M1 figure scaled ×1.6/2/2.5 · M2 direction flipped · M3 base year
moved 3 years back · M4 scope phrase deleted · M5 share or "phần lớn" made absolute · M6 vague
promotional clause appended · M7 evidence swapped for another company's. M0i/M1i put the evidence
inside the claim's own document (a company checking its own report, no outside source).

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_mutation_v1/build.py
writes benchmark/gs_mutation_v1/cases.jsonl
"""
from __future__ import annotations

import json
import re
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "benchmark" / "gs_bench_v1" / "gs_bench_v1.jsonl"
DEV = {"hpg", "ctd", "pow"}
TEST = {"bvh", "dhg", "tra", "vnm", "pnj"}

_NUM = re.compile(r"(?<![\w.,:/-])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w/-]|[.,]\d)")
_DIR = re.compile(r"(?<!\w)(giảm|tăng)(?!\w)")
_BASE = re.compile(r"(so với (?:năm |cùng kỳ năm )?)((?:19|20)\d\d)")
_SCOPE = re.compile(r",?\s*(?:của |cho |tại )?(?:phạm vi [123](?:\s*(?:và|,|\+)\s*[123])*|toàn tập đoàn|toàn công ty|toàn hệ thống)", re.I)
_PCT = re.compile(r"(?<![\w.,])(\d{1,2}(?:,\d+)?)\s?%")
VAGUE = ", khẳng định vị thế doanh nghiệp thân thiện với môi trường hàng đầu"
# v1.1 (15/11/2026, expert review): four patterns common in Vietnamese reports.
_UNIT_SWAPS = [(r"(?<=\d)(\s?)tấn(?!\w)", r"\1kg"), (r"(?<=\d)(\s?)kWh(?!\w)", r"\1MWh"),
               (r"(?<=\d)(\s?)MWh(?!\w)", r"\1GWh"), (r"(?<=\d)(\s?)GWh(?!\w)", r"\1MWh"),
               (r"(?<=\d)(\s)triệu(?=\s)", r"\1nghìn"), (r"(?<=\d)(\s)nghìn(?=\s)", r"\1triệu")]
_FACILITY = re.compile(r"(?:của|tại)\s+(?:các\s+)?(?:nhà máy|khu liên hợp|công ty con|chi nhánh|dự án|tòa nhà|cảng)\b[^,.;]{0,60}?(?=\s(?:là|đạt|giảm|tăng|chiếm|phát|tiêu thụ)\b|[,.;]|$)", re.I)
_TARGET = re.compile(r"(?:đặt\s+)?(?:mục tiêu|phấn đấu|dự kiến|kế hoạch)\s+(?:đến năm \d{4}\s+)?(giảm|đạt|tăng|sử dụng|trồng|tiết kiệm)|sẽ\s+(giảm|đạt|tăng|sử dụng|trồng|tiết kiệm)", re.I)
_INTENSITY = re.compile(r"cường độ phát thải(?:\s+khí nhà kính)?(?:\s+trên\s+(?:mỗi|một)\s+[^,.;]{1,40}?(?=\s(?:của|năm|là|giảm|tăng|đạt)\b))?", re.I)


def _value(token: str) -> float:
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", token):
        return float(token.replace(".", "").replace(",", "."))
    return float(token.replace(",", "."))


def _format(value: float, like: str) -> str:
    decimals = len(like.split(",")[1]) if "," in like else 0
    text = f"{value:,.{decimals}f}"  # 1,234.5
    return text.replace(",", "_").replace(".", ",").replace("_", ".") if ("." in like or decimals or value >= 1000) else text.replace(",", "")


_UNIT_AFTER = re.compile(r"\s?(%|t\b|tấn|tco2|kwh|mwh|gwh|gj|tj|m3|m³|triệu|tỷ|nghìn|lít|kg|ha\b|đồng)", re.I)


def _scaled(claim: str, seed: int) -> str | None:
    """Scale the first measured figure: one followed by a unit, never a year, a scope or a code number."""
    labels = [m.span() for m in re.finditer(r"(?i)(phạm vi|scope|iso|gri)\s*[\d\s,+và\-:.]*\d", claim)]
    candidates = []
    for m in _NUM.finditer(claim):
        token = m.group(1)
        value = _value(token)
        if (1900 <= value <= 2100 and "," not in token) or value == 0:
            continue
        if any(a <= m.start() < b for a, b in labels):
            continue
        candidates.append((not _UNIT_AFTER.match(claim, m.end()), m))
    for _, m in sorted(candidates, key=lambda c: c[0])[:1]:
        token = m.group(1)
        value = _value(token)
        factor = (1.6, 2.0, 2.5)[seed % 3]
        pct = claim[m.end():m.end() + 2].strip().startswith("%")
        new = value * factor
        if pct and new > 100:
            new = value / factor
        if not ("," in token) and not new.is_integer():
            new = round(new)
        return claim[:m.start()] + _format(new, token) + claim[m.end():]
    return None


def mutate(kind: str, case: dict, others: list[dict], seed: int) -> tuple[str, str] | None:
    claim, evidence = case["claim"], case["evidence"]
    if kind == "M1":
        new = _scaled(claim, seed)
    elif kind == "M2":
        new = _DIR.sub(lambda m: {"giảm": "tăng", "tăng": "giảm"}[m.group(1)], claim, count=1) if _DIR.search(claim) else None
    elif kind == "M3":
        new = _BASE.sub(lambda m: m.group(1) + str(int(m.group(2)) - 3), claim, count=1) if _BASE.search(claim) else None
    elif kind == "M4":
        new = _SCOPE.sub("", claim) if _SCOPE.search(claim) else None
    elif kind == "M5":
        if _PCT.search(claim):
            new = _PCT.sub("100%", claim, count=1)
        elif "phần lớn" in claim:
            new = claim.replace("phần lớn", "toàn bộ", 1)
        else:
            new = None
    elif kind == "M6":
        new = claim.rstrip().rstrip(".") + VAGUE + "."
    elif kind == "M8":
        new = None
        for pattern, repl in _UNIT_SWAPS:
            if re.search(pattern, claim):
                new = re.sub(pattern, repl, claim, count=1)
                break
    elif kind == "M9":
        new = _FACILITY.sub("của toàn Tập đoàn", claim, count=1) if _FACILITY.search(claim) else None
    elif kind == "M10":
        new = _TARGET.sub(lambda m: "đã " + (m.group(1) or m.group(2)), claim, count=1) if _TARGET.search(claim) else None
    elif kind == "M11":
        new = _INTENSITY.sub("tổng lượng phát thải khí nhà kính", claim, count=1) if _INTENSITY.search(claim) else None
    elif kind == "M7":
        pool = [o for o in others if o["company"] != case["company"]]
        return (claim, pool[seed % len(pool)]["evidence"]) if pool else None
    else:
        raise ValueError(kind)
    if not new or new == claim:
        return None
    return new, evidence


def main() -> None:
    rows = [json.loads(line) for line in BENCH.open(encoding="utf-8") if line.strip()]
    real = [r for r in rows if r["company"] in DEV | TEST]
    supported = [r for r in real if r["labels"] == ["S"]]
    cases = []

    def add(base, kind, claim, evidence, expected, layout="two_docs"):
        cases.append({
            "case_id": f"{base['id']}-{kind}", "base_id": base["id"], "company": base["company"],
            "split": "dev" if base["company"] in DEV else "test", "mutation": kind, "layout": layout,
            "base_label": "".join(base["labels"]), "claim_original": base["claim"], "claim": claim,
            "evidence": evidence, "expected": expected,
        })

    for r in real:
        if r["labels"] in (["S"], ["N"]):
            add(r, "M0", r["claim"], r["evidence"], {"not": ["CONTRADICTED"]})
    expected = {
        "M1": {"any": ["CONTRADICTED"]}, "M2": {"any": ["CONTRADICTED"]},
        "M3": {"not": ["SUPPORTED"]}, "M4": {"missing": "scope"}, "M5": {"not": ["SUPPORTED"]},
        "M6": {"vague": True}, "M7": {"not": ["SUPPORTED"]},
        "M8": {"not": ["SUPPORTED"]}, "M9": {"not": ["SUPPORTED"]}, "M10": {"not": ["SUPPORTED"]},
        "M11": {"not": ["SUPPORTED"]},
    }
    for r in supported:
        seed = zlib.crc32(r["id"].encode())
        for kind, exp in expected.items():
            out = mutate(kind, r, supported, seed)
            if out:
                add(r, kind, out[0], out[1], exp)
        add(r, "M0i", r["claim"], r["evidence"], {"not": ["CONTRADICTED"]}, layout="one_doc")
        m1 = mutate("M1", r, supported, seed)
        if m1:
            add(r, "M1i", m1[0], m1[1], {"any": ["CONTRADICTED"], "or_flag": "internal_inconsistency"}, layout="one_doc")

    out = HERE / "cases.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for c in cases:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"[build] {len(cases)} cases -> {out}")
    print("[build]", dict(Counter((c["split"], c["mutation"]) for c in cases)))


if __name__ == "__main__":
    main()
