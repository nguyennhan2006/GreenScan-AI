"""AG-2 v1 (registration agentic_ag2_v1): rules path + IR path(s), calibrated on one set, tested on another (CPU).

    .venv/Scripts/python.exe -I experiments/AG-2/policies.py --cal BENCH rules=X ir4=Y [...] --test BENCH rules=X ir4=Y [...] [--json OUT]

Path names must match between --cal and --test; the path named "rules" is the rules path, every other one an IR path.
Only B-b cases that every path labelled are used. Policies (decisive = S or C; N votes are ignored):
  union          the decisive labels of all paths agree -> that label, else N
  union_noloneS  as union, but an S given by the rules path alone -> N
  bucket         union_noloneS label, kept when P(right | bucket) on the --cal set has a 2.5 % Beta(k+1, n-k+1)
                 bound above 0.90 (C) / 0.80 (S); bucket = (rules label, union label, number of IR paths giving it)
Per set and policy: coverage, precision, false_S, false_C, and the coverage gain over the rules path with a paired
95 % company-bootstrap interval (same resampled companies for both), 2 000 resamples, seed 0.
"""
from __future__ import annotations

import ast, json, random, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dual import beta_low  # noqa: E402

THRESHOLD = {"C": 0.90, "S": 0.80}


def load(spec):
    bench, paths = spec[0], dict(a.split("=", 1) for a in spec[1:])
    cases = [c for c in map(json.loads, Path(bench).open(encoding="utf-8")) if c["layer"] == "B-b"]
    votes = {n: {r["id"]: r["label"] for r in map(json.loads, Path(p).open(encoding="utf-8"))} for n, p in paths.items()}
    cases = [c for c in cases if all(c["id"] in v for v in votes.values())]
    for c in cases:
        c["ok"] = set(ast.literal_eval(c["labels"]) if isinstance(c["labels"], str) else c["labels"])
        c["votes"] = {n: v[c["id"]] for n, v in votes.items()}
    return cases


def union(votes, lone_s=True):
    decisive = {lab for lab in votes.values() if lab in "SC"}
    if len(decisive) != 1:
        return "N"
    lab = decisive.pop()
    if not lone_s and lab == "S" and all(v != "S" for n, v in votes.items() if n != "rules"):
        return "N"
    return lab


def bucket(votes):
    lab = union(votes, lone_s=False)
    return votes.get("rules", "-"), lab, sum(v == lab for n, v in votes.items() if n != "rules")


def metrics(cases, labels):
    n = len(cases)
    dec = [c for c in cases if labels[c["id"]] in "SC"]
    right = sum(labels[c["id"]] in c["ok"] for c in dec)
    return {"n": n, "coverage": round(len(dec) / n, 3) if n else None,
            "precision": round(right / len(dec), 3) if dec else None,
            "false_S": sum(labels[c["id"]] == "S" and "S" not in c["ok"] for c in cases),
            "false_C": sum(labels[c["id"]] == "C" and "C" not in c["ok"] for c in cases)}


def gain_ci(cases, labels, base, draws=2000, seed=0):
    by = {}
    for c in cases:
        by.setdefault(c["company"], []).append(c)
    comps, rng, gains = sorted(by), random.Random(seed), []
    for _ in range(draws):
        pick = [x for _ in comps for x in by[rng.choice(comps)]]
        gains.append(sum((labels[x["id"]] in "SC") - (base[x["id"]] in "SC") for x in pick) / len(pick))
    gains.sort()
    return [round(gains[int(0.025 * draws)], 3), round(gains[int(0.975 * draws) - 1], 3)]


def main():
    argv = sys.argv[1:]
    cut = [i for i, a in enumerate(argv) if a.startswith("--")]
    spec = {argv[i]: argv[i + 1:([j for j in cut if j > i] + [len(argv)])[0]] for i in cut}
    cal, test = load(spec["--cal"]), load(spec["--test"])
    table = {}
    for c in cal:
        b, lab = bucket(c["votes"]), union(c["votes"], lone_s=False)
        if lab in "SC":
            k, n = table.get(b, (0, 0))
            table[b] = (k + (lab in c["ok"]), n + 1)
    keep = {b for b, (k, n) in table.items() if beta_low(k, n) > THRESHOLD[b[1]]}
    res = {"paths": list(cal[0]["votes"]), "n_cal": len(cal), "n_test": len(test),
           "buckets_cal": {"/".join(map(str, b)): f"{k}/{n}" + (" keep" if b in keep else "") for b, (k, n) in sorted(table.items())}}
    for name, cases in (("cal", cal), ("test", test)):
        base = {c["id"]: c["votes"].get("rules", "N") for c in cases}
        pol = {"rules": base,
               "union": {c["id"]: union(c["votes"]) for c in cases},
               "union_noloneS": {c["id"]: union(c["votes"], lone_s=False) for c in cases},
               "bucket": {c["id"]: union(c["votes"], lone_s=False) if bucket(c["votes"]) in keep else "N" for c in cases}}
        res[name] = {}
        for p, labels in pol.items():
            m = metrics(cases, labels)
            if p != "rules":
                m["coverage_gain_ci95"] = gain_ci(cases, labels, base)
            res[name][p] = m
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if "--json" in spec:
        Path(spec["--json"][0]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
