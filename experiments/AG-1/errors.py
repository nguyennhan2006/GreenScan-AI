"""Where an IR reader loses or breaks a B-b verdict (AG-1 error attribution, CPU).

    .venv/Scripts/python.exe -I experiments/AG-1/errors.py NAME=path/to/X_texts.jsonl [...] [--show NAME] [--only-new] [--json out.json]

The bench case carries the gold IR of its claim and its evidence. For each system, every B-b case whose
gold verdict is decisive (S or C) or whose predicted verdict is wrong is put in one bucket:
  ok            right label
  miss_claim    no figure read from the claim
  miss_ev       no figure read from the evidence
  field:<f>     the read figure closest to the gold one differs on field f (first in CHECK order);
                f is a field of the claim IR (c.) or of the evidence IR (e.)
  value         every field equal to gold but the number differs (misread value / multiplier / unit factor)
  other         fields equal but verdict still wrong (several figures in one sentence, mixed steps)
--show NAME prints the wrong-decided cases of that system with both IRs side by side.
"""
from __future__ import annotations

import ast, hashlib, json, os, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from irlib import IR, decide  # noqa: E402

BENCH = Path(os.environ.get("GS_BENCH", "benchmark/gs_bench_v1/gs_bench_v1.jsonl"))
CHECK = ("metric", "value_kind", "status", "period", "scope", "boundary", "baseline_year", "change_direction", "dim")


def key(text):
    return hashlib.sha1(text.encode()).hexdigest()[:16]


def as_obj(v):
    return ast.literal_eval(v) if isinstance(v, str) else v


def irs(figs):
    out = []
    for f in as_obj(figs) or []:
        try:
            ir = IR.from_dict({**f, "value_text": str(f["value_text"])})
            ir.quantity()
            out.append(ir)
        except (TypeError, ValueError, KeyError):
            pass
    return out


def fields(ir):
    try:
        q, _, dim = ir.quantity()
    except ValueError:
        q, dim = None, "?"
    return {**{f: getattr(ir, f) for f in CHECK if f != "dim"}, "dim": dim, "q": q}


def closest(gold, cands):
    """Read figure most like the gold one: same number first, then most equal fields."""
    g = fields(gold)
    def score(ir):
        f = fields(ir)
        same_q = f["q"] is not None and g["q"] is not None and abs(f["q"] - g["q"]) <= 1e-6 * max(1, abs(g["q"]))
        return (same_q, sum(f[k] == g[k] for k in CHECK))
    return max(cands, key=score)


def attribute(case, got, read):
    gold_c, gold_e = IR.from_dict(as_obj(case["claim_ir"])), IR.from_dict(as_obj(case["evidence_ir"]))
    rc, re_ = read.get(key(case["claim"])), read.get(key(case["evidence"]))
    if rc is None or re_ is None:
        return "not_run", None, None
    if got in case["labels"]:
        return "ok", None, None
    if not rc:
        return "miss_claim", None, None
    if not re_:
        return "miss_ev", None, None
    pc, pe = closest(gold_c, rc), closest(gold_e, re_)
    for side, gold, pred in (("c", gold_c, pc), ("e", gold_e, pe)):
        g, p = fields(gold), fields(pred)
        for f in CHECK:
            if f in ("baseline_year", "change_direction") and gold.value_kind != "change":
                continue
            if f == "boundary" and "unspecified" in (g[f], p[f]):
                continue
            if g[f] != p[f]:
                return f"field:{side}.{f}", pc, pe
    for gold, pred in ((gold_c, pc), (gold_e, pe)):
        g, p = fields(gold), fields(pred)
        if g["q"] is None or p["q"] is None or abs(g["q"] - p["q"]) > 1e-6 * max(1, abs(g["q"])):
            return "value", pc, pe
    return "other", pc, pe


def short(ir):
    if ir is None:
        return "-"
    f = fields(ir)
    return (f"{ir.metric}|{ir.value_kind}|{ir.status}|p={ir.period}|sc={ir.scope}|b={ir.boundary}|"
            f"{ir.value_text} {ir.multiplier_text} {ir.unit_text}->{f['q']:g} {f['dim']}" if f["q"] is not None else ir.value_text)


def main():
    bench = [c for c in map(json.loads, BENCH.open(encoding="utf-8")) if c["layer"] == "B-b"]
    if "--only-new" in sys.argv:  # held-out set of agentic_v1_1
        old = {json.loads(line)["id"] for line in Path("experiments/AG-1/kaggle_out/a/out/q3-4b-inst_cases.jsonl").open(encoding="utf-8")}
        bench = [c for c in bench if c["id"] not in old]
    for c in bench:
        c["labels"] = as_obj(c["labels"])
    systems = [a.split("=", 1) for a in sys.argv[1:] if "=" in a and not a.startswith("--")]
    show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None
    res = {}
    for name, path in systems:
        read = {}
        for r in map(json.loads, Path(path).open(encoding="utf-8")):
            read[r["key"]] = irs(r["figures"])
        buckets, by_family, wrong = Counter(), defaultdict(Counter), []
        for c in bench:
            got_irs_c, got_irs_e = read.get(key(c["claim"])), read.get(key(c["evidence"]))
            if got_irs_c is None or got_irs_e is None:
                buckets["not_run"] += 1
                continue
            labels = [decide(x, got_irs_e)[0] for x in got_irs_c] or ["N"]
            got = "C" if "C" in labels else ("S" if all(x == "S" for x in labels) else "N")
            if not ({"S", "C"} & set(c["labels"])) and got == "N":
                continue  # gold N, said N: nothing to attribute
            b, pc, pe = attribute(c, got, read)
            tag = b if got == "N" or b == "ok" else f"WRONG_{got}:{b}"
            buckets[tag] += 1
            by_family[c["family"]][tag] += 1
            if got != "N" and got not in c["labels"]:
                wrong.append((c, got, b, pc, pe))
        res[name] = {"buckets": dict(buckets.most_common()), "by_family": {k: dict(v) for k, v in by_family.items()}}
        print(f"== {name}: " + ", ".join(f"{k} {v}" for k, v in buckets.most_common()))
        if name == show:
            for c, got, b, pc, pe in wrong:
                print(f"\n-- {c['id']} [{c['family']}] gold {c['labels']} got {got} ({b})")
                print(f"   claim: {c['claim'][:220]}")
                print(f"   evid : {c['evidence'][:300]}")
                print(f"   gold c {short(IR.from_dict(as_obj(c['claim_ir'])))}")
                print(f"   read c {short(pc)}")
                print(f"   gold e {short(IR.from_dict(as_obj(c['evidence_ir'])))}")
                print(f"   read e {short(pe)}")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
