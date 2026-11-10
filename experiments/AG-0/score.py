"""Score AG-0 (rules only) on GS-Bench v1: the numbers quoted in the Round 2 report, section 3.4.

A case's gold is a list of acceptable answers (S = supported, C = contradicted, N = no firm verdict).
The pipeline output is reduced to one answer per case by run_rules.py. Only firm verdicts (S or C) count
as conclusions: coverage = firm / all, precision = firm verdicts whose answer is acceptable / firm.
A false S or a false C is a firm verdict the gold does not accept -- the errors a reviewer would act on.

usage (repository root), after run_rules.py:
  .venv/Scripts/python.exe -I experiments/AG-0/score.py
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BENCH = Path(os.environ.get("GS_BENCH", "benchmark/gs_bench_v1/gs_bench_v1.jsonl"))
OUT = Path(os.environ.get("GS_RULES_OUT", "experiments/AG-0/out/rules.jsonl"))


def gold_of(case: dict) -> set[str]:
    labels = case["labels"]
    if isinstance(labels, str):
        labels = ast.literal_eval(labels)
    return set(labels)


def main() -> None:
    gold = {c["id"]: gold_of(c) for c in map(json.loads, BENCH.open(encoding="utf-8"))}
    pred = {r["id"]: r["label"] for r in map(json.loads, OUT.open(encoding="utf-8"))}
    missing = sorted(set(gold) - set(pred))
    firm = {i: p for i, p in pred.items() if i in gold and p in {"S", "C"}}
    right = sum(1 for i, p in firm.items() if p in gold[i])
    false_s = sum(1 for i, p in firm.items() if p == "S" and "S" not in gold[i])
    false_c = sum(1 for i, p in firm.items() if p == "C" and "C" not in gold[i])
    n = len(gold)
    print(f"GS-Bench v1: {n} ca; đã chạy {n - len(missing)}")
    print(f"  kết luận dứt khoát (S hoặc C): {len(firm)}  -> tỷ lệ dám kết luận {len(firm) / n:.3f}")
    print(f"  đúng trong số đó: {right}  -> chính xác trên phần kết luận {right / len(firm) if firm else 0:.3f}")
    print(f"  'ủng hộ' sai: {false_s}; 'mâu thuẫn' sai: {false_c}")
    if missing:
        print(f"  thiếu {len(missing)} ca, chạy lại run_rules.py (ví dụ {missing[:3]})")


if __name__ == "__main__":
    main()
