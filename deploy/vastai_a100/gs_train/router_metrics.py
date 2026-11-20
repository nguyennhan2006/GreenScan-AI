"""Metrics of prompt_router_v1, shared by the gate, the planner and the rules baseline.

A prediction is {"in_scope": bool, "tasks": [...], "slots": {...}} (or None when unparsed: counted as a refusal, the
safe side). Decision of a row: out_of_scope / need_info / ok, with need_info = in scope and a claim-needing task without
a claim. OOS recall = out-of-scope rows predicted out (the safety number); false refusal = in-scope rows predicted out.
"""
from __future__ import annotations

import random

TASKS = ["verify_claim", "extract_claims", "check_attributes", "explain_verdict", "find_evidence", "review_assurance",
         "assess_report_risk"]
NEEDS_CLAIM = {"verify_claim", "check_attributes", "explain_verdict", "find_evidence"}


def decision(p: dict | None) -> str:
    if not p or not p.get("in_scope"):
        return "out_of_scope"
    if any(t in NEEDS_CLAIM for t in p.get("tasks") or []) and not (p.get("slots") or {}).get("claim"):
        return "need_info"
    return "ok"


def _ci(flags: list[bool], groups: list[str], n: int = 1000, seed: int = 7) -> list[float] | None:
    by: dict[str, list[bool]] = {}
    for f, g in zip(flags, groups):
        by.setdefault(g, []).append(f)
    keys = sorted(by)
    if len(keys) < 2:
        return None
    rng, vals = random.Random(seed), []
    for _ in range(n):
        s = [x for _ in keys for x in by[rng.choice(keys)]]
        vals.append(sum(s) / len(s))
    vals.sort()
    return [round(vals[25], 4), round(vals[974], 4)]


def score(gold: list[dict], pred: list[dict | None]) -> dict:
    oos = [(g, p) for g, p in zip(gold, pred) if not g["in_scope"]]
    ins = [(g, p) for g, p in zip(gold, pred) if g["in_scope"]]
    caught = [decision(p) == "out_of_scope" for _, p in oos]
    refused = [decision(p) == "out_of_scope" for _, p in ins]
    grp = lambda g: g.get("oos_category") or (g.get("slots") or {}).get("company") or "-"   # noqa: E731
    out = {"n": len(gold), "n_out": len(oos), "n_in": len(ins),
           "oos_recall": round(sum(caught) / max(1, len(caught)), 4), "oos_recall_ci95": _ci(caught, [grp(g) for g, _ in oos]),
           "false_refusal": round(sum(refused) / max(1, len(refused)), 4),
           "false_refusal_ci95": _ci(refused, [grp(g) for g, _ in ins]),
           "decision_accuracy": round(sum(decision(g) == decision(p) for g, p in zip(gold, pred)) / max(1, len(gold)), 4),
           "unparsed": sum(p is None for p in pred),
           "oos_missed_by_category": {}}
    for g, p in oos:
        if decision(p) != "out_of_scope":
            c = g["oos_category"]
            out["oos_missed_by_category"][c] = out["oos_missed_by_category"].get(c, 0) + 1
    f1s, tp_all, fp_all, fn_all = {}, 0, 0, 0
    for t in TASKS:
        tp = sum(t in (g.get("tasks") or []) and t in ((p or {}).get("tasks") or []) for g, p in ins)
        fp = sum(t not in (g.get("tasks") or []) and t in ((p or {}).get("tasks") or []) for g, p in ins)
        fn = sum(t in (g.get("tasks") or []) and t not in ((p or {}).get("tasks") or []) for g, p in ins)
        tp_all, fp_all, fn_all = tp_all + tp, fp_all + fp, fn_all + fn
        pr, rc = tp / (tp + fp) if tp + fp else 0.0, tp / (tp + fn) if tp + fn else 0.0
        f1s[t] = round(2 * pr * rc / (pr + rc), 4) if pr + rc else 0.0
    out["task_f1"] = f1s
    out["task_macro_f1"] = round(sum(f1s.values()) / len(f1s), 4)
    pr, rc = tp_all / max(1, tp_all + fp_all), tp_all / max(1, tp_all + fn_all)
    out["task_micro_f1"] = round(2 * pr * rc / (pr + rc), 4) if pr + rc else 0.0
    for k in ("claim", "company", "year"):
        rows = [(g, p) for g, p in ins if (g.get("slots") or {}).get(k) is not None]
        em = [str(((p or {}).get("slots") or {}).get(k) or "").strip().lower() == str(g["slots"][k]).strip().lower()
              for g, p in rows]
        out[f"slot_{k}_exact"] = round(sum(em) / max(1, len(em)), 4)
    return out
