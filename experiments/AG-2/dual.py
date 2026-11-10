"""AG-2: rules path + IR path(s) + agreement gate + abstention calibrated out-of-fold by company (CPU).

    .venv/Scripts/python.exe -I experiments/AG-2/dual.py rules=experiments/AG-0/out/rules.jsonl ir4=X_cases.jsonl [ir32=...] \
        [--only-new] [--out experiments/AG-2/out/NAME]

Every path gives S / C / N per case. Proposed label: the decisive labels of all paths if they agree (S or C), else N.
Bucket = the tuple of path labels (e.g. N,S,S): the only thing known at inference time.
For each company, P(proposed label right | bucket) is estimated on the OTHER companies' B-b cases (out of fold),
lower bound = 2.5 % quantile of Beta(k + 1, n - k + 1). Conclude when the bound clears the D1 thresholds
registered in KE_HOACH (C > 0.90, S > 0.80), else N (a person reads it).
Writes OUT_dual_cases.jsonl (for experiments/score.py), OUT_curve.json (coverage / precision as the threshold moves)
and prints the policies side by side. B-a cases get the in-sample bucket table of all B-b (no company to hold out).
"""
from __future__ import annotations

import json, random, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BENCH = Path("benchmark/gs_bench_v1/gs_bench_v1.jsonl")
V1_IDS = Path("experiments/AG-1/kaggle_out/a/out/q3-4b-inst_cases.jsonl")
THRESH = {"C": 0.90, "S": 0.80}


def beta_low(k, n, q=0.025, draws=4000, seed=0):
    """2.5 % quantile of Beta(k + 1, n - k + 1) by sampling (stdlib only)."""
    if n == 0:
        return 0.0
    rng = random.Random(seed * 7919 + n * 131 + k)
    xs = sorted(rng.betavariate(k + 1, n - k + 1) for _ in range(draws))
    return xs[int(q * draws)]


def proposed(labels):
    dec = {x for x in labels if x in "SC"}
    return dec.pop() if len(dec) == 1 else "N"


def main():
    names, paths = [], []
    for a in sys.argv[1:]:
        if "=" in a and not a.startswith("--"):
            n, p = a.split("=", 1); names.append(n); paths.append(p)
    preds = [{r["id"]: r["label"] for r in map(json.loads, Path(p).open(encoding="utf-8"))} for p in paths]
    cases = [c for c in map(json.loads, BENCH.open(encoding="utf-8")) if all(c["id"] in p for p in preds)]
    if "--only-new" in sys.argv:
        old = {json.loads(line)["id"] for line in V1_IDS.open(encoding="utf-8")}
        cases = [c for c in cases if c["id"] not in old]
    for c in cases:
        c["bucket"] = tuple(p[c["id"]] for p in preds)
        c["prop"] = proposed(c["bucket"])
        c["ok"] = c["prop"] in c["labels"]
    bb = [c for c in cases if c["layer"] == "B-b"]
    companies = sorted({c["company"] for c in bb})

    def table(rows):
        t = defaultdict(lambda: [0, 0])
        for r in rows:
            if r["prop"] != "N":
                t[r["bucket"]][0] += r["ok"]; t[r["bucket"]][1] += 1
        return t

    full = table(bb)
    lows = {}
    for g in companies:
        t = table([c for c in bb if c["company"] != g])
        for c in bb:
            if c["company"] == g:
                k, n = t.get(c["bucket"], (0, 0))
                lows[c["id"]] = beta_low(k, n)
    for c in cases:
        if c["layer"] != "B-b":
            k, n = full.get(c["bucket"], (0, 0))
            lows[c["id"]] = beta_low(k, n)

    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("experiments/AG-2/out/dual")
    out.parent.mkdir(parents=True, exist_ok=True)
    with Path(f"{out}_dual_cases.jsonl").open("w", encoding="utf-8") as fh:
        for c in cases:
            lab = c["prop"] if c["prop"] != "N" and lows[c["id"]] > THRESH[c["prop"]] else "N"
            fh.write(json.dumps({"id": c["id"], "label": lab, "bucket": "/".join(c["bucket"]),
                                 "p_low": round(lows[c["id"]], 3)}, ensure_ascii=False) + "\n")
    with Path(f"{out}_agree_cases.jsonl").open("w", encoding="utf-8") as fh:  # no calibration: any decisive agreement
        for c in cases:
            fh.write(json.dumps({"id": c["id"], "label": c["prop"]}, ensure_ascii=False) + "\n")

    curve = []
    for t in [x / 100 for x in range(50, 100, 2)]:
        dec = [c for c in bb if c["prop"] != "N" and lows[c["id"]] > t]
        curve.append({"threshold": t, "coverage": round(len(dec) / len(bb), 3),
                      "precision": round(sum(c["ok"] for c in dec) / len(dec), 3) if dec else None,
                      "false_C": sum(c["prop"] == "C" and "C" not in c["labels"] for c in dec),
                      "false_S": sum(c["prop"] == "S" and "S" not in c["labels"] for c in dec)})
    Path(f"{out}_curve.json").write_text(json.dumps({"paths": names, "n_B-b": len(bb), "curve": curve,
        "buckets": {"/".join(k): {"right": v[0], "n": v[1]} for k, v in sorted(full.items(), key=lambda kv: -kv[1][1])}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"paths {names}; {len(cases)} cases, B-b {len(bb)} on {len(companies)} companies")
    print("buckets (B-b, decisive proposal):", {"/".join(k): f"{v[0]}/{v[1]}" for k, v in sorted(full.items(), key=lambda kv: -kv[1][1])})
    print(f"wrote {out}_dual_cases.jsonl, {out}_agree_cases.jsonl, {out}_curve.json")


if __name__ == "__main__":
    main()
