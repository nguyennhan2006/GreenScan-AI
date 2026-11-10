"""Score systems on GS-Bench v1 with the metrics of invariant 8 (no single blended number).

    .venv/Scripts/python.exe -I experiments/score.py NAME=path/to/cases.jsonl [NAME=...] [--json out.json]

Each cases file holds {"id", "label": S|C|N}. Per layer (B-a sạch, B-a trang thật, B-b) and overall:
  right      label in the acceptable set
  decided    S or C given (coverage = decided / n)
  precision  right among decided
  false_S    S where S is not acceptable (a problem waved through)
  false_C    C where C is not acceptable (a company wrongly accused)
B-b also: 95% interval of precision and coverage by company bootstrap (2 000 resamples, seed 0).
"""
from __future__ import annotations

import json, os, random, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BENCH = Path(os.environ.get("GS_BENCH", "benchmark/gs_bench_v1/gs_bench_v1.jsonl"))  # GS_BENCH: another case file (held-out sets)


def metrics(rows):
    n = len(rows)
    decided = [r for r in rows if r["label"] in "SC"]
    right_dec = sum(r["label"] in r["labels"] for r in decided)
    return {
        "n": n, "right": sum(r["label"] in r["labels"] for r in rows), "decided": len(decided),
        "coverage": round(len(decided) / n, 3) if n else None,
        "precision": round(right_dec / len(decided), 3) if decided else None,
        "false_S": sum(r["label"] == "S" and "S" not in r["labels"] for r in rows),
        "false_C": sum(r["label"] == "C" and "C" not in r["labels"] for r in rows),
    }


def bootstrap(rows, key, reps=2000, seed=0):
    by_co = defaultdict(list)
    for r in rows:
        by_co[r["company"]].append(r)
    cos, rng, vals = sorted(by_co), random.Random(seed), []
    for _ in range(reps):
        sample = [r for c in (rng.choice(cos) for _ in cos) for r in by_co[c]]
        v = metrics(sample)[key]
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)] if vals else None


def score(path: str) -> dict:
    bench = {c["id"]: c for c in map(json.loads, BENCH.open(encoding="utf-8"))}
    got = {r["id"]: r["label"] for r in map(json.loads, Path(path).open(encoding="utf-8"))}
    rows = [{**bench[i], "label": got[i]} for i in bench if i in got]
    out = {"missing": len(bench) - len(rows), "all": metrics(rows)}
    for layer in ("B-a sạch", "B-a trang thật", "B-b"):
        out[layer] = metrics([r for r in rows if r["layer"] == layer])
    bb = [r for r in rows if r["layer"] == "B-b"]
    out["B-b"]["precision_ci95"] = bootstrap(bb, "precision")
    out["B-b"]["coverage_ci95"] = bootstrap(bb, "coverage")
    fam = defaultdict(list)
    for r in bb:
        fam[r["family"].split()[0]].append(r)
    out["B-b_by_family_right"] = {f: f"{sum(x['label'] in x['labels'] for x in v)}/{len(v)}" for f, v in sorted(fam.items())}
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if "=" in a and not a.startswith("--")]
    res = {name: score(path) for name, path in (a.split("=", 1) for a in args)}
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, r in res.items():
        print(f"== {name} (missing {r['missing']})")
        for layer in ("all", "B-a sạch", "B-a trang thật", "B-b"):
            print(f"  {layer:<15} {json.dumps(r[layer], ensure_ascii=False)}")
        print(f"  B-b by family  {r['B-b_by_family_right']}")


if __name__ == "__main__":
    main()
