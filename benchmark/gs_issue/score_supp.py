"""Score the pipeline on the supplements (run_pipeline_supp.py): risk ordering of twins, verdicts and explanations of C / S.

    python -X utf8 benchmark/gs_issue/score_supp.py      # -> results/score_supp.json (+ printed summary)

Twins: pair-order = share of pairs with priority(mutated) > priority(clean); ties reported apart (a tie means the
scorer did not see the planted issue). Severe codes: share of mutated twins in band high / critical (bands as in
gs_eval_v2/evaluate.band_of). Explain supplement: verdict vs GS-Bench label; for C, the explanation names the claim's
figure AND the evidence's figure (both, as digits).
"""
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def band(s):
    s = round(s)
    return "low" if s <= 24 else "medium" if s <= 49 else "high" if s <= 74 else "critical"


def digits(s):
    return {re.sub(r"[.,]", "", x) for x in re.findall(r"\d+(?:[.,]\d+)*", s or "")}


def main():
    res = {}
    P = [json.loads(line) for line in open(HERE / "out/pipeline_pairs.jsonl", encoding="utf-8")]
    ok = [p for p in P if p["clean"].get("priority") is not None and p["mutated"].get("priority") is not None]
    per = defaultdict(lambda: Counter())
    for p in ok:
        d = p["mutated"]["priority"] - p["clean"]["priority"]
        per[p["code"]]["up" if d > 0.5 else "tie" if abs(d) <= 0.5 else "down"] += 1
        per[p["code"]]["n"] += 1
        per[p["code"]]["verdict_changed"] += p["mutated"]["verdict"] != p["clean"]["verdict"]
        if p["severe"]:
            per[p["code"]]["mut_high"] += band(p["mutated"]["priority"]) in ("high", "critical")
    up = sum(c["up"] for c in per.values())
    res["twins"] = {"pairs": len(P), "scored": len(ok), "errors": len(P) - len(ok),
                    "pair_order_up": round(up / len(ok), 3), "pair_order_ci": wilson(up, len(ok)),
                    "ties": round(sum(c["tie"] for c in per.values()) / len(ok), 3),
                    "severe_mutated_in_high_band": round(sum(c["mut_high"] for c in per.values()) / max(1, sum(c["n"] for k, c in per.items() if k in
                                                         {"ABSOLUTE_CLAIM", "OFFSET_NEUTRALITY", "FUTURE_AS_ACHIEVED", "INTENSITY_VS_ABSOLUTE", "HIDDEN_TRADEOFF"})), 3),
                    "per_code": {k: dict(v) for k, v in per.items()},
                    "mean_priority": {"clean": round(sum(p["clean"]["priority"] for p in ok) / len(ok), 1),
                                      "mutated": round(sum(p["mutated"]["priority"] for p in ok) / len(ok), 1)}}
    gold = {json.loads(line)["item_id"]: json.loads(line) for line in open(HERE / "data/supp_explain.jsonl", encoding="utf-8")}
    E = [json.loads(line) for line in open(HERE / "out/pipeline_explain.jsonl", encoding="utf-8")]
    conf = Counter()
    cite_both, cite_n, cite_any = 0, 0, 0
    for e in E:
        g = gold[e["item_id"]]
        conf[(g["ref_verdict"], e.get("verdict"))] += 1
        if g["ref_verdict"] == "CONTRADICTED":
            cite_n += 1
            ex = digits(e.get("explanation"))
            kc, ke = set(g["key_numbers"]["claim"]), set(g["key_numbers"]["evidence"])
            cite_both += bool(ex & kc) and bool(ex & (ke - kc))
            cite_any += bool(ex & (kc | ke))
    by = defaultdict(dict)
    for (g, s), n in conf.items():
        by[g][s] = n
    hit = {g: sum(n for s, n in v.items() if s == g) for g, v in by.items()}
    tot = {g: sum(v.values()) for g, v in by.items()}
    res["explain_supp"] = {"n": len(E), "confusion": dict(by), "recall": {g: round(hit[g] / tot[g], 3) for g in tot},
                           "recall_ci": {g: wilson(hit[g], tot[g]) for g in tot},
                           "C_explanation_cites_both_figures": round(cite_both / cite_n, 3) if cite_n else None,
                           "C_explanation_cites_any_figure": round(cite_any / cite_n, 3) if cite_n else None,
                           "decisive_wrong": sum(n for (g, s), n in conf.items() if s in ("SUPPORTED", "CONTRADICTED") and s != g)}
    (HERE / "results").mkdir(exist_ok=True)
    json.dump(res, open(HERE / "results/score_supp.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3500])


if __name__ == "__main__":
    main()
