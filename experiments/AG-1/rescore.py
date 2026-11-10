"""Re-derive AG-1 verdicts from the raw replies a Kaggle run already saved, with the current irlib (CPU, no model).

    .venv/Scripts/python.exe -I experiments/AG-1/rescore.py NAME=path/to/X_texts.jsonl [...] [--nogold] [--raw] [--noguard] [--only-new] [--out DIR]

Writes DIR/NAME_cases.jsonl (default DIR experiments/AG-1/out/rescore) for experiments/score.py and
DIR/NAME_texts.jsonl (same rows, figures re-read) for errors.py. --nogold skips the regression check.
--raw scores without ground() (as the runs did before 31/10 14:00); --noguard keeps ground() but drops the v1.2 C-guard. --only-new keeps the cases that v1 (193 ids,
V1_IDS) did not have: the held-out set of registration agentic_v1_1.
Regression check first: every gold IR of GS-Bench must pass irlib.ground against its own sentence unchanged.
"""
from __future__ import annotations

import ast, hashlib, json, os, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ag1_worker import parse, to_irs, verdict  # noqa: E402
from irlib import ground  # noqa: E402

BENCH = Path(os.environ.get("GS_BENCH", "benchmark/gs_bench_v1/gs_bench_v1.jsonl"))
V1_IDS = Path("experiments/AG-1/kaggle_out/a/out/q3-4b-inst_cases.jsonl")  # the 193 cases runs A/B/C read


def key(text):
    return hashlib.sha1(text.encode()).hexdigest()[:16]


def gold_check(cases):
    """Gold IRs (read by Claude, checked by the deterministic checker) must survive ground() as they are."""
    bad = []
    for c in cases:
        for side in ("claim", "evidence"):
            gold = c.get(f"{side}_ir")
            if not gold:
                continue
            gold = ast.literal_eval(gold) if isinstance(gold, str) else gold
            got = ground(gold, c[side])
            fields = ("value_text", "multiplier_text", "period", "baseline_year")
            if got is None or any(str(got.get(f) or "") != str(gold.get(f) or "") for f in fields):
                bad.append((c["id"], side, {f: gold.get(f) for f in fields}, got and {f: got.get(f) for f in fields}))
    return bad


def main():
    cases = [json.loads(line) for line in BENCH.open(encoding="utf-8")]
    if "--only-new" in sys.argv:
        old = {json.loads(line)["id"] for line in V1_IDS.open(encoding="utf-8")}
        cases = [c for c in cases if c["id"] not in old]
        print(f"[only-new] {len(cases)} cases not in v1")
    if "--nogold" not in sys.argv:
        bad = gold_check(cases)
        print(f"[gold] {len(bad)} gold IRs changed by ground()")
        for b in bad[:12]:
            print("  ", b)
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("experiments/AG-1/out/rescore")
    out.mkdir(parents=True, exist_ok=True)
    for name, path in (a.split("=", 1) for a in sys.argv[1:] if "=" in a and not a.startswith("--")):
        irs, rows = {}, []
        for r in map(json.loads, Path(path).open(encoding="utf-8")):
            obj = parse(r["raw"])
            figs = (obj or {}).get("figures") if isinstance((obj or {}).get("figures"), list) else []
            irs[r["key"]] = to_irs(figs, None if "--raw" in sys.argv else r["text"])
            rows.append({**r, "figures": [x.as_dict() for x in irs[r["key"]]]})
        with (out / f"{name}_texts.jsonl").open("w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        n = 0
        with (out / f"{name}_cases.jsonl").open("w", encoding="utf-8") as fh:
            for c in cases:
                kc, ke = key(c["claim"]), key(c["evidence"])
                if kc in irs and ke in irs:
                    label, why = verdict(irs[kc], irs[ke], None if {"--raw", "--noguard"} & set(sys.argv) else c["evidence"])
                    fh.write(json.dumps({"id": c["id"], "label": label, "why": why}, ensure_ascii=False) + "\n")
                    n += 1
        print(f"[{name}] {len(rows)} texts, {n} cases -> {out}")


if __name__ == "__main__":
    main()
