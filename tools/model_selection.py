#!/usr/bin/env python3
"""Which model each step uses, decided by the rules registered before measuring.

Reads the measurements and applies configs/measurement_decisions.yaml → model_selection_v2, step by
step. Nothing here chooses by eye: a missing measurement is reported as missing ("chờ …"), never
filled in, and the verdict text quotes the numbers it rests on.

Inputs (whatever exists):
  step 4   training/runs/kaggle_t1_v4/{results.json, preds_cv.jsonl, preds_compare.jsonl}
           training/data/kaggle/data/{train,compare}.jsonl          (the rows the kernel saw)
           benchmark/model_selection/t1_latency_laptop.json        (training/latency_t1.py)
           training/data/claude/crosscheck/<model>.jsonl            (LLM answers, training/llm_t1.py)
  step 6–7 benchmark/model_selection/stage67_report.json           (training/claude_pairs.py report)
Output: benchmark/model_selection/decisions.json and DECISIONS.md

usage: python tools/model_selection.py [--run training/runs/kaggle_t1_v4]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "model_selection"
LABELS = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]
SIZE = {"e5-small": 118, "e5-base": 278, "qwen3-0.6b": 596, "e5-large": 560, "bge-m3": 568, "qwen3-1.7b": 1720}


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()] if path.exists() else []


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _macro(y: list[int], p: list[int]) -> float:
    present = sorted(set(y) | set(p))
    f = []
    for k in present:
        tp = sum(a == k and b == k for a, b in zip(y, p))
        fp = sum(a != k and b == k for a, b in zip(y, p))
        fn = sum(a == k and b != k for a, b in zip(y, p))
        f.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return sum(f) / len(f) if f else 0.0


def _recall_claim(y: list[int], p: list[int]) -> float:
    pos = [b for a, b in zip(y, p) if a != 0]
    return sum(b != 0 for b in pos) / len(pos) if pos else 0.0


def _paired(y, a, b, groups, fn=_macro, samples=1000) -> dict:
    """fn(a) − fn(b) on the same rows, interval from resampling whole companies."""
    by = defaultdict(list)
    for i, g in enumerate(groups):
        by[g].append(i)
    names = sorted(by)
    rng = random.Random(0)
    vals = []
    for _ in range(samples):
        ix = [i for _ in names for i in by[rng.choice(names)]]
        vals.append(fn([y[i] for i in ix], [a[i] for i in ix]) - fn([y[i] for i in ix], [b[i] for i in ix]))
    vals.sort()
    return {"delta": round(fn(y, a) - fn(y, b), 4),
            "ci95": [round(vals[int(0.025 * samples)], 4), round(vals[int(0.975 * samples) - 1], 4)]}


def step4(rules: dict, run: Path) -> dict:
    r = rules["t1_claim_detection"]
    res = _load(run / "results.json")
    lat = (_load(OUT / "t1_latency_laptop.json") or {}).get("models", {})
    if not res:
        return {"status": "chờ", "missing": f"{run.relative_to(ROOT)}/results.json (Kaggle v4)"}
    train = _read(ROOT / "training/data/kaggle/data/train.jsonl")
    compare = _read(ROOT / "training/data/kaggle/data/compare.jsonl")
    tid = {x["id"]: i for i, x in enumerate(train)}
    y = [LABELS.index(x["label"]) for x in train]
    groups = [x["company_id"] for x in train]
    cv = defaultdict(dict)
    for x in _read(run / "preds_cv.jsonl"):
        cv[x["config"]][tid[x["id"]]] = max(range(4), key=lambda c: x["probs"][c])
    preds = {k: [v[i] for i in range(len(train))] for k, v in cv.items() if len(v) == len(train) and "·" not in k}
    preds["rules"] = [0 if not x["rule_label"] else (2 if x["has_figure"] else 1) for x in train]
    students = [k for k in preds if k in r["candidates_offline"] and k not in ("rules", "zero-shot-nli")]
    if not students:
        return {"status": "chờ", "missing": "no student finished in v4"}
    f1 = {k: round(_macro(y, preds[k]), 4) for k in preds}
    best = max(students, key=f1.get)
    rows = {}
    for k in sorted(students, key=lambda k: SIZE.get(k, 9e9)):
        d = _paired(y, preds[best], preds[k], groups) if k != best else {"delta": 0.0, "ci95": [0.0, 0.0]}
        lk = lat.get(k, {})
        fastest = min((v for v in lk.values() if isinstance(v, dict) and "ms_mean" in v),
                      key=lambda v: v["ms_mean"], default=None)
        variant = next((n for n, v in lk.items() if v is fastest), None)
        rows[k] = {"cv_macro_f1": f1[k], "best_minus_this": d,
                   "not_worse": d["ci95"][0] <= 0, "within_0_02": d["delta"] <= 0.02,
                   "laptop_ms": fastest["ms_mean"] if fastest else None, "laptop_variant": variant,
                   "laptop_ram_gb": fastest["ram_peak_delta_gb"] if fastest else None,
                   "kaggle_cpu_ms": res["configs"].get(k, {}).get("cpu_ms_per_sentence_batch1_4threads")}
        rows[k]["fits_laptop"] = (fastest is not None and fastest["ms_mean"] <= r["offline_limits"]["cpu_ms_per_sentence_max"]
                                  and fastest["ram_peak_delta_gb"] <= r["offline_limits"]["ram_gb_max"])
    pick = next((k for k in rows if rows[k]["not_worse"] and rows[k]["within_0_02"] and rows[k]["fits_laptop"]), None)
    eligible = [k for k in rows if rows[k]["not_worse"] and rows[k]["within_0_02"]]
    out = {"best_by_cv": best, "students": rows, "rules_cv_macro_f1": f1["rules"],
           "skipped_or_failed": {**{k: "skipped" for k in res.get("stats", {}).get("skipped", [])},
                                 **res.get("stats", {}).get("failed", {})}}
    chosen = pick or (eligible[0] if eligible else best)
    vs_rules = _paired(y, preds[chosen], preds["rules"], groups)
    recall_gain = _recall_claim(y, preds[chosen]) - _recall_claim(y, preds["rules"])
    out["chosen_offline"] = chosen
    out["chosen_meets_speed"] = bool(pick)
    out["vs_rules"] = {**vs_rules, "claim_recall_gain": round(recall_gain, 4)}
    out["replace_rules"] = vs_rules["ci95"][0] > 0 and recall_gain >= 0.10
    # cloud: an LLM must beat the chosen student on the compare set (paired, same rows)
    cmp = defaultdict(dict)
    cid = {x["id"]: i for i, x in enumerate(compare)}
    for x in _read(run / "preds_compare.jsonl"):
        if x["config"] == chosen:
            cmp[chosen][cid[x["id"]]] = max(range(4), key=lambda c: x["probs"][c])
    yc = {i: LABELS.index(x["label"]) for i, x in enumerate(compare)}
    llm = {}
    for model in r["candidates_cloud"]:
        ans = {x["id"]: x["label"] for x in _read(ROOT / "training/data/claude/crosscheck" / f"{model}.jsonl")}
        ix = [i for i, x in enumerate(compare) if x["id"] in ans and i in cmp[chosen]]
        if len(ix) < 0.9 * len(compare):
            llm[model] = {"status": "chờ", "answered": len(ix), "of": len(compare)}
            continue
        a = [LABELS.index(ans[compare[i]["id"]]) if ans[compare[i]["id"]] in LABELS else 0 for i in ix]
        b = [cmp[chosen][i] for i in ix]
        d = _paired([yc[i] for i in ix], a, b, [compare[i]["company_id"] for i in ix])
        llm[model] = {**d, "use_in_cloud": d["ci95"][0] > 0,
                      "ineligible": model in rules.get("ineligible_for_user_documents", [])}
    out["cloud_llm_vs_chosen"] = llm
    return out


def step6(rules: dict, rep: dict | None) -> dict:
    r = rules["retrieval"]
    if not rep or "retrieval" not in rep:
        return {"status": "chờ", "missing": "stage67_report.json (nhãn cặp)"}
    sys_ = rep["retrieval"]["systems"]
    today = sys_[r["today"]]
    out = {}
    for name, b in sys_.items():
        if name == r["today"]:
            continue
        d = b.get(f"delta_vs_{r['today']}:recall@5", {})
        ratio = b["seconds_per_claim"] / max(today["seconds_per_claim"], 1e-6)
        out[name] = {"recall@5": b.get("recall@5", {}).get("mean"), "delta": d.get("mean"), "ci95": d.get("ci95"),
                     "time_ratio": round(ratio, 2), "offline_ok": name in r["offline_profile_candidates"],
                     "switch": bool(d.get("ci95") and d["mean"] >= 0.10 and d["ci95"][0] > 0 and ratio <= 2.0)}
    for with_rr, without in (("lite+rerank", "lite"), ("hybrid-vn+rerank", "hybrid-vn")):
        if with_rr in sys_ and without in sys_:
            a, b = sys_[with_rr].get("ndcg@5", {}).get("mean"), sys_[without].get("ndcg@5", {}).get("mean")
            out.setdefault("_reranker", {})[with_rr] = {"ndcg@5": a, "without": b,
                                                         "note": "cần Δ ghép cặp; xem stage67_report.json"}
    return {"today": r["today"], "candidates": out,
            "switch_to": [k for k, v in out.items() if isinstance(v, dict) and v.get("switch")]}


def step7(rules: dict, rep: dict | None) -> dict:
    r = rules["stance"]
    if not rep or "stance" not in rep:
        return {"status": "chờ", "missing": "stage67_report.json (nhãn cặp)"}
    st = rep["stance"]
    today = st.get(r["today"], {}).get("all")
    out = {}
    for name, b in st.items():
        a = b.get("all", {})
        if not a:
            continue
        c = a["per_class"]["CONTRADICTS"]
        row = {"n": a["n"], "macro_f1": a["macro_f1"], "ci95": a.get("macro_f1_ci95"),
               "precision_contradicts": c["precision"], "predicted_contradicts": c["predicted"],
               "false_contradicts_per_100": a["false_contradicts_per_100"],
               "precision_supports": a["per_class"]["SUPPORTS"]["precision"],
               "seconds_per_pair": a.get("seconds_per_pair"), "unparsed": a.get("unparsed"),
               "ineligible": name in rules.get("ineligible_for_user_documents", [])}
        d = a.get(f"delta_macro_f1_vs_{r['today']}")
        if d:
            row["delta_vs_today"] = d
            row["better"] = bool(d.get("ci95") and d["ci95"][0] > 0)
            row["not_worse"] = bool(d.get("ci95") and d["ci95"][1] >= 0)
        out[name] = row
    coverage = {k: v["n"] for k, v in out.items()}
    return {"today": r["today"], "today_covered": today["n"] if today else 0, "candidates": out,
            "note": "Chỉ so được trên các cặp mà mô hình hôm nay đã trả lời; xem coverage.", "coverage": coverage}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=str(ROOT / "training/runs/kaggle_t1_v4"))
    args = ap.parse_args()
    rules = yaml.safe_load((ROOT / "configs/measurement_decisions.yaml").read_text(encoding="utf-8"))["model_selection_v2"]
    rep = _load(OUT / "stage67_report.json")
    result = {"rules": "configs/measurement_decisions.yaml → model_selection_v2 (registered "
                       f"{rules['registered']})",
              "step4": step4(rules, Path(args.run)), "step5": {"status": rules["normalization"]["status"]},
              "step6": step6(rules, rep), "step7": step7(rules, rep)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "decisions.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=1)[:6000])
    print(f"-> {(OUT / 'decisions.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
