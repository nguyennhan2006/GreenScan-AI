"""GS-Bench v1.3 clean subsets (01/11/2026): drop B-b cases whose evidence figure fails two checks found after run G.

Found reading the 4B misses on the held-out set (experiments/AG-1/README.md, 01/11):
  period_not_dated  the evidence year appears only outside a dating phrase, e.g. the page header
                    "BÁO CÁO THƯỜNG NIÊN 2022" glued to the sentence; reader B only asked that the year occur
                    somewhere, so the gold period was invented and a model answering null was right
  metric_has_digit  the metric phrase holds a number ("tiết giảm được giảm 12%"): the generated claims are garbled
  unit_placeholder  the unit is "đơn vị" / "Đơn vị"
  other_env         held-out only: 32B coded non-environmental figures other_env (registered defect of run G)
No case is relabelled: whole evidence figures are dropped, and the dropped list is written to errata_v13.txt.
B-a cases are kept as they are.

    .venv/Scripts/python.exe -I benchmark/gs_bench_v1/clean_v13.py
"""
from __future__ import annotations

import json, re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETS = {"calib": ("gs_bench_v1.jsonl", False), "heldout": ("gs_heldout_v12.jsonl", True)}
# a dating word up to 25 characters before the year: "năm tài chính 2024", "Tháng 8/2023", "giai đoạn 2020–2025";
# the header "BÁO CÁO THƯỜNG NIÊN 2022" has none
DATED = r"\b(năm|giai đoạn|niên độ|kỳ|đến hết|tính đến|so với|trong|tháng)\b[^\n.;]{0,25}?"


def defect(case: dict, heldout: bool) -> str | None:
    ev, text = case.get("evidence_ir") or {}, case["evidence"]
    if heldout and ev.get("metric") == "other_env":
        return "other_env"
    year = ev.get("period")
    if year and not re.search(DATED + str(year), text, re.I):
        return "period_not_dated"
    if re.search(r"\d", ev.get("metric_text") or ""):
        return "metric_has_digit"
    if (ev.get("unit_text") or "").strip().lower() == "đơn vị":
        return "unit_placeholder"
    return None


def main() -> None:
    errata, stats = [], {}
    for name, (src, heldout) in SETS.items():
        cases = [json.loads(line) for line in (HERE / src).open(encoding="utf-8")]
        kept, why = [], Counter()
        for c in cases:
            d = defect(c, heldout) if c["layer"] == "B-b" else None
            if d:
                why[d] += 1
                errata.append(f"{name}\t{c['id']}\t{d}\t{c['evidence'][:120]}")
            else:
                kept.append(c)
        (HERE / f"gs_bench_v13_{name}.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in kept),
                                                          encoding="utf-8")
        bb = [c for c in kept if c["layer"] == "B-b"]
        stats[name] = {"cases_in": len(cases), "kept": len(kept), "dropped": dict(why), "B-b_kept": len(bb),
                       "B-b_by_label": dict(Counter(c["labels"][0] for c in bb)), "companies": len({c["company"] for c in bb})}
    (HERE / "errata_v13.txt").write_text("\n".join(errata) + "\n", encoding="utf-8")
    (HERE / "stats_v13.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
