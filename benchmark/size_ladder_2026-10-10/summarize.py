"""Summarise results_*.json: accuracy with Wilson CI, coverage, selective accuracy,
false-support / false-contradiction counts, and exact McNemar p against GreenScan.

usage: python summarize.py results_clean.json [results_local.json ...]
       (extra files contribute more systems for the same case set)
"""
import json, math, sys
from math import comb

sys.stdout.reconfigure(encoding="utf-8")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


base = json.load(open(sys.argv[1], encoding="utf-8"))
ok = {c["id"]: set(c["ok"]) for c in base["cases"]}
systems = dict(base["systems"])
for extra in sys.argv[2:]:
    data = json.load(open(extra, encoding="utf-8"))
    systems.update(data.get("systems", data))
ref_name = next(iter(systems))
ref = {k: a["label"] in ok[k] for k, a in systems[ref_name].items()}
n = len(ok)
print(f"n = {n} cases\n")
print(f"{'system':32s} {'correct':>8s} {'95% CI':>13s} {'coverage':>9s} {'sel.acc':>8s} {'falseS':>6s} {'falseC':>6s} {'McNemar p vs ' + ref_name[:9]:>22s}")
for name, ans in systems.items():
    right = {k: ans[k]["label"] in ok[k] for k in ok if k in ans}
    k = sum(right.values())
    lo, hi = wilson(k, n)
    decided = [kk for kk in ok if kk in ans and ans[kk]["label"] in ("S", "C")]
    sel = sum(right[kk] for kk in decided)
    fs = sum(ans[kk]["label"] == "S" and "S" not in ok[kk] for kk in ok if kk in ans)
    fc = sum(ans[kk]["label"] == "C" and "C" not in ok[kk] for kk in ok if kk in ans)
    b = sum(right.get(kk, False) and not ref[kk] for kk in ok)
    c = sum(ref[kk] and not right.get(kk, False) for kk in ok)
    p = "—" if name == ref_name else f"{mcnemar_exact(b, c):.4f} ({b}/{c})"
    print(f"{name:32s} {k:3d}/{n:<4d} [{lo:4.0%}–{hi:4.0%}] {len(decided):4d}/{n:<4d} {sel:3d}/{len(decided):<4d} {fs:6d} {fc:6d} {p:>22s}")
