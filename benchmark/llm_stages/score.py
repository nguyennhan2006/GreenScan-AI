"""Score the llm_stages_v1 sets (silver labels). Company bootstrap (1000 resamples) for every headline number.

    .venv/Scripts/python.exe -I -X utf8 benchmark/llm_stages/score.py s5 rules=- groq=PRED.jsonl q3-4b=PRED.jsonl
    .venv/Scripts/python.exe -I -X utf8 benchmark/llm_stages/score.py s2 rules=- groq=PRED.jsonl
    .venv/Scripts/python.exe -I -X utf8 benchmark/llm_stages/score.py s6 rules=- groq=PRED.jsonl

A prediction file has one row per set row: {"id", "raw", "parsed"} (stage_worker.py / run_api.py output).
`rules=-` scores the product's own answer stored in the set.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from quantum_gw.assist.guards import fold, new_numbers, verbatim  # noqa: E402

ATTRS = ("metric", "value", "period", "baseline", "scope")
MAP = {"SUPPORTS": "S", "CONTRADICTS": "C", "PARTIAL": "P", "CONTEXT": "O"}
SETS = {"s5": "s5_pairs", "s2": "s2_attrs", "s6": "s6_explain"}


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def boot(rows, stat, n=1000, seed=7):
    by = defaultdict(list)
    for r in rows:
        by[r["company"]].append(r)
    comps, rnd, vals = list(by), random.Random(seed), []
    for _ in range(n):
        sample = [r for c in (rnd.choice(comps) for _ in comps) for r in by[c]]
        v = stat(sample)
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)] if vals else None


def f1(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    return p, r, (2 * p * r / (p + r) if p and r else 0.0)


# ---------------------------------------------------------------- S5 stance
def s5_label(row, pred, from_rules):
    if from_rules:
        raw = MAP.get(row.get("rules") or "", "O")
    else:
        rel = str(((pred or {}).get("parsed") or {}).get("relation", "")).strip().upper()
        raw = MAP.get(rel, "FAIL")
    return {"S": "S", "C": "C"}.get(raw, "O"), raw


def s5_stats(rows):
    out = {}
    for c in ("S", "C", "O"):
        tp = sum(r["sys"] == c and r["gold"] == c for r in rows)
        fp = sum(r["sys"] == c and r["gold"] != c for r in rows)
        fn = sum(r["sys"] != c and r["gold"] == c for r in rows)
        out[c] = f1(tp, fp, fn)
    return out


def score_s5(name, data, preds):
    rows = []
    for d in data:
        lab, raw = s5_label(d, (preds or {}).get(d["id"]), preds is None)
        rows.append({**d, "sys": lab, "raw": raw})

    def macro(rs):  # S and O; C has 7 gold pairs and is reported apart
        st = s5_stats(rs)
        return (st["S"][2] + st["O"][2]) / 2

    st = s5_stats(rows)
    false_c = sum(r["sys"] == "C" and r["gold"] != "C" for r in rows)
    return {"system": name, "n": len(rows), "macro_f1_SO": round(macro(rows), 3), "ci95": boot(rows, macro),
            "S_precision": None if st["S"][0] is None else round(st["S"][0], 3),
            "S_recall": None if st["S"][1] is None else round(st["S"][1], 3),
            "false_C_per_100": round(100 * false_c / len(rows), 2), "false_C": false_c,
            "C_found": f"{sum(r['sys'] == 'C' and r['gold'] == 'C' for r in rows)}/{sum(r['gold'] == 'C' for r in rows)}",
            "gold_S_called_S_or_P": f"{sum(r['raw'] in ('S', 'P') and r['gold'] == 'S' for r in rows)}/{sum(r['gold'] == 'S' for r in rows)}",
            "raw_labels": dict(Counter(r["raw"] for r in rows))}


# ---------------------------------------------------------------- S2 attributes
def rules_stated(d):
    a = d.get("rules_attrs") or {}
    return {"metric": bool(a.get("metric")), "value": bool(a.get("values")), "period": bool(a.get("period")),
            "baseline": bool(a.get("baseline")), "scope": bool(a.get("scope"))}


def model_stated(d, pred):
    p = (pred or {}).get("parsed") or {}
    out, invented = {}, 0
    for a in ATTRS:
        v = p.get(a)
        kept = verbatim(v, d["sentence"]) if isinstance(v, str) else None
        invented += bool(isinstance(v, str) and v.strip() and kept is None)
        out[a] = kept is not None
    return out, invented, p.get("is_claim")


def score_s2(name, data, preds):
    rows, invented, nac = [], 0, []
    for d in data:
        if preds is None:
            if d["rules_attrs"] is None:
                continue  # the product no longer extracts this sentence
            stated, inv, isc = rules_stated(d), 0, None
        else:
            stated, inv, isc = model_stated(d, preds.get(d["id"]))
        invented += inv
        nac.append((d["is_claim"], isc))
        if d["is_claim"]:
            rows.append({"company": d["company"], "stated": stated,
                         "gold": {a: d["gold"].get(a) not in (None, "", []) for a in ATTRS}})

    def per_attr(rs):  # the rubric charges a MISSING attribute: score the "missing" call
        res = {}
        for a in ATTRS:
            tp = sum((not r["stated"][a]) and not r["gold"][a] for r in rs)
            fp = sum((not r["stated"][a]) and r["gold"][a] for r in rs)
            fn = sum(r["stated"][a] and not r["gold"][a] for r in rs)
            res[a] = f1(tp, fp, fn)[2]
        return res

    def macro(rs):
        return sum(per_attr(rs).values()) / len(ATTRS) if rs else None

    out = {"system": name, "n_claims": len(rows), "missing_f1_macro": round(macro(rows), 3), "ci95": boot(rows, macro),
           "missing_f1": {a: round(v, 3) for a, v in per_attr(rows).items()}, "non_verbatim_spans_dropped": invented}
    if preds is not None:
        out["not_a_claim"] = {"flagged_right": sum((not g) and p is False for g, p in nac),
                              "true_claims_flagged": sum(g and p is False for g, p in nac),
                              "missed": sum((not g) and p is not False for g, p in nac)}
    return out


# ---------------------------------------------------------------- S6 explanation
def covered(phrase, text):
    words = [w for w in fold(phrase).split() if len(w) > 2]
    return bool(words) and sum(w in fold(text) for w in words) / len(words) >= 0.6


def explanation_text(d, pred):
    if pred is None:
        return d["system_rationale"] or d["rationale"]
    p = pred.get("parsed") or {}
    return " ".join(str(p.get(k, "")) for k in ("explanation", "next_action")).strip()


def score_s6(name, data, preds):
    rows, bad, empty = [], 0, 0
    for d in data:
        text = explanation_text(d, None if preds is None else preds.get(d["id"]))
        empty += not text
        nn = new_numbers(text, d["claim"], d["rationale"], *[f"{e.get('source_name')} {e.get('page')} {e.get('text') or ''}" for e in d["evidence"]])
        bad += bool(nn)
        mm = d["must_mention"]
        rows.append({"company": d["company"], "cov": (sum(covered(m, text) for m in mm) / len(mm)) if mm else None,
                     "words": len(text.split())})

    def cov(rs):
        v = [r["cov"] for r in rs if r["cov"] is not None]
        return sum(v) / len(v) if v else None

    return {"system": name, "n": len(rows), "must_mention_proxy": round(cov(rows), 3), "ci95": boot(rows, cov),
            "with_new_number": bad, "empty": empty, "words_mean": round(sum(r["words"] for r in rows) / len(rows), 1)}


def main():
    stage, specs = sys.argv[1], sys.argv[2:]
    data = jl(HERE / "data" / f"{SETS[stage]}.jsonl")
    on = [s for s in specs if s.startswith("--on=")]   # score every system on the rows one prediction file covers
    if on:
        specs = [s for s in specs if s not in on]
        keep = {r["id"] for r in jl(on[0][5:])}
        data = [d for d in data if d["id"] in keep]
    fn = {"s5": score_s5, "s2": score_s2, "s6": score_s6}[stage]
    out = []
    for spec in specs:
        name, path = spec.split("=", 1)
        out.append(fn(name, data, None if path == "-" else {r["id"]: r for r in jl(path)}))
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
