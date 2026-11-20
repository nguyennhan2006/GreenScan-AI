"""prompt_router_v1 baseline: the rules scope guard (assist/scope_guard.py) on the router test set, before any model.

    .venv/Scripts/python.exe -X utf8 tools/router_rules_baseline.py [--split test|train]
Writes deploy/vastai_a100/out_kaggle/merged/router_eval/rules_<split>.json (same metrics as the trained router).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "deploy/vastai_a100/gs_train")]
from quantum_gw.assist.scope_guard import rules_route  # noqa: E402
from router_metrics import score  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    src = ROOT / "training/data/claude/router"
    gold = [json.loads(x) for f in (f"{a.split}_in.jsonl", f"{a.split}_out.jsonl") for x in open(src / f, encoding="utf-8")]
    preds = []
    for g in gold:
        r = rules_route(g["request"])
        preds.append({"in_scope": r.status != "out_of_scope", "tasks": r.tasks, "slots": r.slots})
    s = score(gold, preds)
    out = ROOT / "deploy/vastai_a100/out_kaggle/merged/router_eval"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"rules_{a.split}.json").write_text(json.dumps({"systems": {"rules": s}}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: s[k] for k in ("n", "oos_recall", "oos_recall_ci95", "false_refusal", "decision_accuracy",
                                         "task_macro_f1", "slot_claim_exact", "slot_company_exact", "slot_year_exact",
                                         "oos_missed_by_category")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
