#!/usr/bin/env python3
"""Acceptance benchmark: measure each stage separately, on real reports.

Why per-stage rather than one end-to-end number: retrieval design and document
selection can make a RAG system *worse* while the final answer still looks
plausible. A single output score hides that — if evidence Recall@k is 0.4, every
downstream metric is capped and no amount of prompt work will fix it. So the
report below never collapses to one figure.

Two commands:

    python tools/benchmark.py sample --run-dir .quantum/runs/<id> --n 25
        Writes a labelling template. A human fills the `human_*` fields.

    python tools/benchmark.py score --labels benchmark/<doc>.labels.jsonl
        Computes the metrics, reporting label coverage first.

Labels can also come from the reviewer workflow: `--from-reviews` pulls
adjudicated verdicts out of the decision store so review work counts twice.

This tool never invents a label. Unlabelled fields are reported as coverage
gaps, and a metric with no labels prints "no labels" rather than a number.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from quantum_gw.utils.jsonl import read_jsonl, write_jsonl  # noqa: E402

ATTRIBUTES = ["specific_metric", "baseline", "period", "scope_boundary", "evidence_methodology"]
COMPONENTS = {
    "specific_metric": ["specificity", "quantitative_evidence"],
    "baseline": ["baseline"],
    "period": ["period"],
    "scope_boundary": ["scope_boundary"],
    "evidence_methodology": ["evidence_support", "independent_assurance"],
}
ABSTAIN = {"INSUFFICIENT_EVIDENCE", "UNSUPPORTED"}


def attribute_state(components: dict, key: str) -> str:
    """'present' | 'partial' | 'missing' | 'unknown' for one rubric attribute.

    Components are penalties, so 0 means the attribute is satisfied and a full
    score means it is absent. An attribute backed by several components only
    counts as present when every one of them is satisfied.
    """
    present = [components[c] for c in COMPONENTS[key] if c in components]
    if not present:
        return "unknown"
    ratios = [(c["score"] / c["max_score"]) if c["max_score"] else 0 for c in present]
    if all(r == 0 for r in ratios):
        return "present"
    if all(r >= 0.99 for r in ratios):
        return "missing"
    return "partial"


# ---------------------------------------------------------------- sample

def looks_like_prose(text: str) -> bool:
    """Filter headings and fragments out of the sample.

    31% of extracted candidates are navigation menus and section titles. Spending
    a third of a reviewer's budget labelling "PHÁT TRIỂN BỀN VỮNG" measures the
    extractor's boilerplate rate, which the EDA already reports, instead of the
    pipeline's accuracy.
    """
    stripped = text.strip()
    if len(stripped) < 45:
        return False
    words = stripped.split()
    if len(words) < 8:
        return False
    capitalised = sum(1 for w in words if w[:1].isupper())
    return capitalised / len(words) <= 0.6


def cmd_sample(args: argparse.Namespace) -> int:
    result = json.loads((Path(args.run_dir) / "result.json").read_text(encoding="utf-8"))
    risks = {r["claim_id"]: r for r in result["risks"]}
    verifications = result["verifications"]

    eligible = [v for v in verifications if looks_like_prose(v["claim"]["text"])]
    skipped = len(verifications) - len(eligible)

    # Stratify by verdict so the sample is not all PARTIALLY_SUPPORTED.
    by_status: dict[str, list] = {}
    for v in eligible:
        by_status.setdefault(v["status"], []).append(v)
    rng = random.Random(args.seed)
    for group in by_status.values():
        rng.shuffle(group)

    chosen, i = [], 0
    while len(chosen) < args.n and any(by_status.values()):
        for status in sorted(by_status):
            if by_status[status] and len(chosen) < args.n:
                chosen.append(by_status[status].pop())
        i += 1
        if i > args.n * 2:
            break

    rows = []
    for v in chosen:
        claim = v["claim"]
        components = {c["name"]: c for c in risks.get(claim["claim_id"], {}).get("components", [])}
        rows.append({
            "run_id": result["run_id"],
            "claim_id": claim["claim_id"],
            "claim_text": claim["text"],
            "source_name": claim["source_name"],
            "source_page": claim.get("source_page"),
            # ---- what the system produced ----
            "sys_status": v["status"],
            "sys_attributes": {k: attribute_state(components, k) for k in ATTRIBUTES},
            "sys_evidence": [
                {"chunk_id": e["chunk_id"], "page": e.get("page"),
                 "source_name": e["source_name"], "relation": e.get("relation"),
                 "rank": rank, "preview": (e.get("text") or "")[:180]}
                for rank, e in enumerate(v.get("evidence", []), start=1)
            ],
            # ---- what a human fills in ----
            "human_is_real_claim": None,       # true/false — is this an environmental claim at all
            "human_status": None,              # correct verdict
            "human_attributes": {k: None for k in ATTRIBUTES},   # present|partial|missing
            "human_relevant_chunk_ids": [],    # evidence that SHOULD have been retrieved
            "human_relation": {},              # chunk_id -> SUPPORTS|CONTRADICTS|PARTIAL|CONTEXT
            "human_citation_ok": {},           # chunk_id -> true/false (page/doc correct)
            "human_notes": "",
        })

    out = Path(args.out or REPO / "benchmark" / f"{Path(args.run_dir).name}.labels.jsonl")
    write_jsonl(out, rows)
    print(f"Sampled {len(rows)} claims from {len(verifications)} "
          f"({skipped} skipped as headings/fragments)")
    print(f"Verdict mix: {dict(Counter(r['sys_status'] for r in rows))}")
    print(f"\nTemplate: {out}")
    print("Fill every human_* field. Unfilled fields are reported as coverage gaps,\n"
          "not silently treated as agreement.")
    return 0


# ---------------------------------------------------------------- score

def pct(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.1%} ({numerator}/{denominator})" if denominator else "no labels"


def cmd_score(args: argparse.Namespace) -> int:
    rows = read_jsonl(Path(args.labels))

    if args.from_reviews:
        from quantum_gw.storage.reviews import ReviewStore

        gold = {(g["run_id"], g["claim_id"]): g for g in ReviewStore(args.reviews_file).gold_records()}
        adopted = 0
        for r in rows:
            g = gold.get((r["run_id"], r["claim_id"]))
            if g and r.get("human_status") is None:
                r["human_status"] = g["label"]
                adopted += 1
        print(f"Adopted {adopted} verdict label(s) from the reviewer decision store.\n")

    total = len(rows)
    labelled = [r for r in rows if r.get("human_is_real_claim") is not None]
    report: dict = {"sampled": total, "labelled": len(labelled)}

    if not labelled:
        print(f"{total} claims sampled, 0 labelled.\n")
        print("Nothing can be measured yet. Fill human_* fields in the labels file, or run\n"
              "with --from-reviews after adjudicating claims in the UI.")
        return 1

    # --- stage 1: claim extraction -----------------------------------------
    real = [r for r in labelled if r["human_is_real_claim"]]
    report["claim_precision"] = pct(len(real), len(labelled))

    # --- stage 2: retrieval, measured on its own ---------------------------
    rec_hits = rec_total = 0
    rr: list[float] = []
    for r in real:
        want = set(r.get("human_relevant_chunk_ids") or [])
        if not want:
            continue
        got = [e["chunk_id"] for e in r["sys_evidence"]][: args.k]
        rec_total += 1
        if want & set(got):
            rec_hits += 1
            rr.append(1 / (next(i for i, c in enumerate(got, 1) if c in want)))
        else:
            rr.append(0.0)
    report[f"evidence_recall@{args.k}"] = pct(rec_hits, rec_total)
    report["evidence_mrr"] = f"{statistics.mean(rr):.3f}" if rr else "no labels"

    # --- stage 3: citation --------------------------------------------------
    cite_ok = cite_total = 0
    for r in real:
        for chunk_id, ok in (r.get("human_citation_ok") or {}).items():
            cite_total += 1
            cite_ok += bool(ok)
    report["citation_precision"] = pct(cite_ok, cite_total)

    # --- stage 4: relation --------------------------------------------------
    rel_ok = rel_total = 0
    confusion: Counter = Counter()
    for r in real:
        truth = r.get("human_relation") or {}
        for e in r["sys_evidence"]:
            expected = truth.get(e["chunk_id"])
            if expected is None:
                continue
            rel_total += 1
            rel_ok += e["relation"] == expected
            confusion[f"{expected}->{e['relation']}"] += 1
    report["relation_accuracy"] = pct(rel_ok, rel_total)
    report["relation_confusion"] = dict(confusion.most_common(8))

    # --- stage 5: checklist -------------------------------------------------
    per_attr: dict[str, list[int]] = {k: [] for k in ATTRIBUTES}
    for r in real:
        truth = r.get("human_attributes") or {}
        for k in ATTRIBUTES:
            if truth.get(k) is None:
                continue
            per_attr[k].append(int(truth[k] == r["sys_attributes"].get(k)))
    report["checklist_accuracy"] = {
        k: pct(sum(v), len(v)) for k, v in per_attr.items()
    }
    flat = [x for v in per_attr.values() for x in v]
    report["checklist_accuracy_overall"] = pct(sum(flat), len(flat))

    # --- stage 6: verdict + abstain ----------------------------------------
    with_status = [r for r in real if r.get("human_status")]
    verdict_ok = sum(1 for r in with_status if r["sys_status"] == r["human_status"])
    report["verdict_accuracy"] = pct(verdict_ok, len(with_status))

    sys_abstained = [r for r in with_status if r["sys_status"] in ABSTAIN]
    human_abstained = [r for r in with_status if r["human_status"] in ABSTAIN]
    correct_abstain = sum(1 for r in sys_abstained if r["human_status"] in ABSTAIN)
    missed_abstain = sum(1 for r in human_abstained if r["sys_status"] not in ABSTAIN)
    report["abstain_precision"] = pct(correct_abstain, len(sys_abstained))
    report["abstain_recall"] = pct(len(human_abstained) - missed_abstain, len(human_abstained))

    print(json.dumps(report, ensure_ascii=False, indent=2))

    out = Path(args.out or Path(args.labels).with_suffix(".report.json"))
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")

    if rec_total and rec_hits / rec_total < 0.85:
        print("\nRetrieval is below the 0.85 Recall@k target in docs/04-data-ai/EVALUATION.md.\n"
              "Every downstream metric is capped by this; fix retrieval before prompts.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample", help="write a labelling template from a run")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--n", type=int, default=25)
    s.add_argument("--seed", type=int, default=20260809)
    s.add_argument("--out")
    s.set_defaults(func=cmd_sample)

    c = sub.add_parser("score", help="compute metrics from filled labels")
    c.add_argument("--labels", required=True)
    c.add_argument("--k", type=int, default=5)
    c.add_argument("--from-reviews", action="store_true",
                   help="adopt adjudicated verdicts from the reviewer decision store")
    c.add_argument("--reviews-file", default=None)
    c.add_argument("--out")
    c.set_defaults(func=cmd_score)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
