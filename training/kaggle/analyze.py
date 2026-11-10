"""Turn a Kaggle T1 run into numbers you can defend and a page you can show.

Reads training/runs/kaggle_t1/{results.json, preds_cv.jsonl, preds_compare.jsonl}
plus the data that was uploaded, and writes benchmark/t1_kaggle/report.json and
benchmark/t1_kaggle/T1_ket_qua.html (report_template.html with the data inlined).

What it adds to the Kaggle numbers:
  * baselines that need no GPU: the rule extractor (binary; and a 4-class guess:
    kept + figure → QUANTIFIED, kept → QUALITATIVE, else NOT_CLAIM) and gemma
    on the sentences both teachers labelled
  * 95% intervals by **company-cluster bootstrap** on the CV predictions: the 498
    sentences come from 13 companies, so resampling sentences would pretend there
    are 498 independent draws; resampling companies does not
  * paired differences student − baseline on the same resamples (the claim
    "training on domain data helps" is the interval of that difference)
  * slices: language, needs-context, stratum; the most confident errors

Every number is agreement with Claude's labels, not accuracy (see the report).

usage: python training/kaggle/analyze.py [--run training/runs/kaggle_t1]
"""
import argparse
import json
import re
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABELS = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]
SHORT = {"NOT_CLAIM": "NOT", "QUALITATIVE_CLAIM": "QUAL", "QUANTIFIED_CLAIM": "QUANT", "VAGUE": "VAGUE"}
L2I = {l: i for i, l in enumerate(LABELS)}
B = 2000


def read(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def f1s(y, p):
    out = []
    for c in range(4):
        tp = sum(1 for a, b in zip(y, p) if a == b == c)
        fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        out.append({"precision": pr, "recall": rc, "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0,
                    "support": tp + fn})
    return out


def macro(y, p):
    # classes present in the truth or the predictions (scikit-learn's default). On a small slice
    # (39 HPG sentences) a class may be absent: counting it as F1 = 0 would punish nothing real,
    # dropping it while it is predicted would hide false alarms.
    present = sorted(set(y) | set(p))
    per = f1s(y, p)
    return sum(per[c]["f1"] for c in present) / len(present) if present else 0.0


def claim_f1(y, p):
    tp = sum(1 for a, b in zip(y, p) if a > 0 and b > 0)
    fp = sum(1 for a, b in zip(y, p) if a == 0 and b > 0)
    fn = sum(1 for a, b in zip(y, p) if a > 0 and b == 0)
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": pr, "recall": rc, "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0}


def kappa(y, p):
    n = len(y)
    if not n:
        return None
    po = sum(a == b for a, b in zip(y, p)) / n
    ca, cb = Counter(y), Counter(p)
    pe = sum(ca[k] * cb[k] for k in range(4)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def summary(y, p):
    return {"n": len(y), "accuracy": sum(a == b for a, b in zip(y, p)) / len(y) if y else None,
            "macro_f1": macro(y, p), "kappa": kappa(y, p), "claim": claim_f1(y, p),
            "per_class": {LABELS[c]: v for c, v in enumerate(f1s(y, p))},
            "confusion": [[sum(1 for a, b in zip(y, p) if a == i and b == j) for j in range(4)] for i in range(4)]}


def cluster_boot(groups, fn, seed=13):
    """95% interval of fn(indices) when whole groups (companies) are resampled."""
    keys = sorted(groups)
    rng = random.Random(seed)
    vals = []
    for _ in range(B):
        idx = [i for k in (rng.choice(keys) for _ in keys) for i in groups[k]]
        v = fn(idx)
        if v is not None:
            vals.append(v)
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else None


def item_boot(n, fn, seed=13):
    rng = random.Random(seed)
    vals = sorted(v for v in (fn([rng.randrange(n) for _ in range(n)]) for _ in range(B)) if v is not None)
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else None


STUDENTS = ("e5-small", "e5-base", "qwen3-0.6b", "e5-large", "bge-m3", "qwen3-1.7b", "mdeberta-xnli")   # whichever the run trained


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(ROOT / "training/runs/kaggle_t1"))
    ap.add_argument("--prose", help="HTML with <!--CRITIQUE-->, <!--PRINCIPLES-->, <!--NEXT--> parts for the report")
    args = ap.parse_args()
    run = Path(args.run)
    res = json.loads((run / "results.json").read_text(encoding="utf-8"))
    train = read(ROOT / "training/data/kaggle/data/train.jsonl")
    compare = read(ROOT / "training/data/kaggle/data/compare.jsonl")
    claude = {r["id"]: r for r in read(ROOT / "training/data/claude/claude_labels.jsonl")}
    tid = {r["id"]: i for i, r in enumerate(train)}
    cid = {r["id"]: i for i, r in enumerate(compare)}
    y = [L2I[r["label"]] for r in train]
    yc = [L2I[r["label"]] for r in compare]

    preds = defaultdict(dict)          # config -> train index -> predicted class
    probs = defaultdict(dict)
    for x in read(run / "preds_cv.jsonl"):
        i = tid[x["id"]]
        preds[x["config"]][i] = max(range(4), key=lambda c: x["probs"][c])
        probs[x["config"]][i] = max(x["probs"])
    cpreds = defaultdict(dict)
    for x in read(run / "preds_compare.jsonl"):
        cpreds[x["config"]][cid[x["id"]]] = max(range(4), key=lambda c: x["probs"][c])

    # baselines without a GPU
    def rule4(r):
        return 0 if not r["rule_label"] else (2 if r["has_figure"] else 1)
    preds["rules (4 lớp đoán)"] = {i: rule4(r) for i, r in enumerate(train)}
    cpreds["rules (4 lớp đoán)"] = {i: rule4(r) for i, r in enumerate(compare)}

    groups = defaultdict(list)
    for i, r in enumerate(train):
        groups[r["company_id"]].append(i)
    best = res["best"]
    methods = ["rules (4 lớp đoán)", "zero-shot", *STUDENTS]
    methods = [m for m in methods if m in preds]
    out = {"reference": res["reference"], "best": best, "n_train": len(train), "n_companies": len(groups),
           "methods": {}, "ablations": {}, "learning_curve": res.get("learning_curve", {}),
           "timings": res.get("timings", {}), "env": res.get("env", {}), "seed_spread": {}}

    for m in methods:
        p = [preds[m][i] for i in range(len(train))]
        s = summary(y, p)
        s["macro_f1_ci"] = cluster_boot(groups, lambda ix: macro([y[i] for i in ix], [p[i] for i in ix]))
        s["claim_f1_ci"] = cluster_boot(groups, lambda ix: claim_f1([y[i] for i in ix], [p[i] for i in ix])["f1"])
        comp = {}
        for name, ix in (("all", range(len(compare))),
                         ("audit", [i for i, r in enumerate(compare) if r["set"] == "audit"]),
                         ("hpg", [i for i, r in enumerate(compare) if r["set"] == "hpg"])):
            ix = list(ix)
            if m in cpreds and ix:
                yy, pp = [yc[i] for i in ix], [cpreds[m][i] for i in ix]
                cs = summary(yy, pp)
                cs["macro_f1_ci"] = item_boot(len(ix), lambda jx: macro([yy[j] for j in jx], [pp[j] for j in jx]))
                comp[name] = cs
        s["compare"] = comp
        out["methods"][m] = s

    # paired differences on the same company resamples: best student minus each baseline
    pb = [preds[best][i] for i in range(len(train))]
    out["paired"] = {}
    for base in ("rules (4 lớp đoán)", "zero-shot", *(k for k in STUDENTS if k != best and k in preds)):
        if base not in preds:
            continue
        q = [preds[base][i] for i in range(len(train))]
        out["paired"][base] = {
            "delta": macro(y, pb) - macro(y, q),
            "ci": cluster_boot(groups, lambda ix: macro([y[i] for i in ix], [pb[i] for i in ix])
                               - macro([y[i] for i in ix], [q[i] for i in ix]))}

    rules_bin = [1 if r["rule_label"] else 0 for r in train]
    out["rules_binary"] = claim_f1(y, rules_bin)
    out["majority"] = {"macro_f1": macro(y, [0] * len(y)), "claim_f1": 0.0,
                       "note": "đoán mọi câu là NOT_CLAIM: mức sàn của macro-F1"}

    # ablations are paired with the same seed of the masked run (v2: `<best>·masked·s13`)
    ref = f"{best}·masked·s13" if f"{best}·masked·s13" in preds else best
    pref = [preds[ref][i] for i in range(len(train))]
    out["ablation_reference"] = {"config": ref, "macro_f1": macro(y, pref),
                                 "ci": cluster_boot(groups, lambda ix: macro([y[i] for i in ix], [pref[i] for i in ix]))}
    for v in ("raw", "pair"):
        k = next((c for c in (f"{best}·{v}·s13", f"{best}·{v}") if c in preds), None)
        if k:
            p = [preds[k][i] for i in range(len(train))]
            out["ablations"][v] = {"macro_f1": macro(y, p),
                                   "ci": cluster_boot(groups, lambda ix: macro([y[i] for i in ix], [p[i] for i in ix])),
                                   "delta_vs_masked": macro(y, p) - macro(y, pref),
                                   "delta_ci": cluster_boot(groups, lambda ix: macro([y[i] for i in ix], [p[i] for i in ix])
                                                            - macro([y[i] for i in ix], [pref[i] for i in ix]))}
    for key in STUDENTS:
        c = res["configs"].get(key, {})
        if c.get("cv_macro_f1_by_seed"):
            out["seed_spread"][key] = {"cv": c["cv_macro_f1_by_seed"], "compare": c.get("compare_macro_f1_by_seed")}
    retries = res.get("stats", {}).get("retries", {})
    out["retries"] = {m: sum(v for k, v in retries.items() if k.startswith(m)) for m in STUDENTS if m in preds}
    out["version"] = res.get("version", 1)

    # slices of the best student
    sl = {}
    for name, key in (("Ngôn ngữ", lambda r: r.get("lang")), ("Cần ngữ cảnh", lambda r: "có" if r.get("needs_context") else "không"),
                      ("Nhóm lấy mẫu", lambda r: r.get("stratum"))):
        part = defaultdict(list)
        for i, r in enumerate(train):
            part[str(key(r))].append(i)
        sl[name] = {k: {"n": len(ix), "macro_f1": macro([y[i] for i in ix], [pb[i] for i in ix]),
                        "accuracy": sum(y[i] == pb[i] for i in ix) / len(ix)} for k, ix in sorted(part.items())}
    out["slices"] = sl

    # most confident errors of the best student, with Claude's note for context
    errs = sorted((i for i in range(len(train)) if pb[i] != y[i]), key=lambda i: -probs[best][i])
    out["errors"] = [{"id": train[i]["id"], "company": train[i]["company_id"].upper(), "text": train[i]["text"][:260],
                      "claude": SHORT[LABELS[y[i]]], "student": SHORT[LABELS[pb[i]]], "p": round(probs[best][i], 2),
                      "claude_note": (claude.get(train[i]["id"], {}).get("note") or "")[:160]} for i in errs[:14]]
    out["error_pairs"] = dict(Counter(f"{SHORT[LABELS[y[i]]]}→{SHORT[LABELS[pb[i]]]}" for i in errs).most_common(8))
    out["class_counts"] = {SHORT[l]: sum(1 for v in y if v == L2I[l]) for l in LABELS}
    gem = [(L2I[c["label"]], L2I[c["gemma_label"]]) for c in claude.values()
           if c.get("gemma_label") and c["set"] == "train" and c["label"] in L2I]
    out["gemma_vs_claude"] = {"n": len(gem), "agree": sum(a == b for a, b in gem), "kappa": kappa(*zip(*gem)) if gem else None}

    dest = ROOT / "benchmark/t1_kaggle"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "report.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    tpl = (ROOT / "training/kaggle/report_template.html").read_text(encoding="utf-8")
    if args.prose:
        # the reading of the numbers is written by hand for each run, then inlined
        parts = re.split(r"<!--(CRITIQUE|PRINCIPLES|NEXT)-->", Path(args.prose).read_text(encoding="utf-8"))
        for name, html in zip(parts[1::2], parts[2::2]):
            tpl = tpl.replace(f"<!--__{name}__-->", html.strip())
    (dest / "T1_ket_qua.html").write_text(tpl.replace("/*__DATA__*/null", json.dumps(out, ensure_ascii=False)),
                                          encoding="utf-8")
    print("best", best, {m: round(v["macro_f1"], 3) for m, v in out["methods"].items()})
    print("paired", {k: (round(v["delta"], 3), [round(x, 3) for x in v["ci"]]) for k, v in out["paired"].items()})
    print("->", dest / "report.json", "and T1_ket_qua.html")


if __name__ == "__main__":
    main()
