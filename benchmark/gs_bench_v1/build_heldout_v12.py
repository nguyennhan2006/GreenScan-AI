"""GS-Bench held-out set for registration agentic_v1_2 (31/10/2026): sentences v1.1 did NOT use as evidence.

v1.1 keeps a figure only when the deterministic reader B finds nothing against Claude's reading (build.py).
Here reader A is Qwen3-32B-AWQ (Kaggle run F, candidates_v2, replies held to the sentence by irlib.ground), on the
candidates_v2 sentences that are not evidence of any v1.1 case:
  pair "claude+32b"   Claude read the same figure (metric, number, multiplier, unit, kind, period, baseline, status,
                      scope, direction, boundary); every check of reader B except Claude's own confidence passes
  pair "32b+readerB"  only 32B read it; reader B finds nothing against it (the v1.1 standard, other reader A)
Claims and labels come from the same perturbation families as v1.1 (build.variants), not from irlib.
Amendment agentic_v1_2 22h50: "claude+32b" alone gave 6 figures (33 cases), too few; the union is the held-out set.

Bias: the evidence figure was read right by 32B by construction, so 32B scores on this set are optimistic;
the registered test is q3-4b-inst (and 8B / 14B), which did not choose the figures.
Defect found after run G: 60 / 162 cases rest on figures 32B coded other_env that are not environmental;
a later set built this way must drop other_env (agentic_v1_2.result_held_out_162_run_G).

    .venv/Scripts/python.exe -I benchmark/gs_bench_v1/build_heldout_v12.py
"""
from __future__ import annotations

import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build  # noqa: E402
from irlib import IR, compare, parse_number  # noqa: E402

READS_32B = ROOT / "experiments/AG-1/out/heldout_ef_v12/32b_texts.jsonl"   # rescore.py output: grounded figures
FIELDS = ("metric", "multiplier_text", "value_kind", "period", "baseline_year", "status", "scope", "change_direction", "boundary")
KIND = {"count": "absolute"}


def norm(fig: dict, field: str):
    v = fig.get(field)
    if field == "value_kind":
        v = KIND.get(v, v)
    if field == "boundary" and v in (None, "", "unspecified"):
        v = "group"
    return str(v or "").strip().lower()


def same(a: dict, b: dict) -> bool:
    try:
        if parse_number(a["value_text"]) != parse_number(b["value_text"]):
            return False
    except (ValueError, KeyError, TypeError):
        return False
    if (a.get("unit_text") or "").strip().lower() != (b.get("unit_text") or "").strip().lower():
        return False
    return all(norm(a, f) == norm(b, f) for f in FIELDS)


def main() -> None:
    sentences = {r["id"]: r for r in map(json.loads, (HERE / "candidates_v2.jsonl").open(encoding="utf-8"))}
    claude = [json.loads(line) for line in (HERE / "ir_claude_v2.jsonl").open(encoding="utf-8")]
    read32 = {r["text"]: r["figures"] for r in map(json.loads, READS_32B.open(encoding="utf-8"))}
    used = {c["evidence"] for c in map(json.loads, (HERE / "gs_bench_v1.jsonl").open(encoding="utf-8"))}
    by_text = {}
    for rec in claude:
        by_text.setdefault(sentences[rec["id"]]["text"], []).extend(rec.get("figures") or [])
    why_out, kept = Counter(), []
    for src in sentences.values():
        if src["text"] in used:
            why_out["sentence used in v1.1"] += len(read32.get(src["text"]) or [])
            continue
        seen = []
        for j, fig in enumerate(read32.get(src["text"]) or []):
            if any(same(fig, s) for s in seen):
                why_out["32B listed it twice"] += 1
                continue
            seen.append(fig)
            agree = [c for c in by_text.get(src["text"], []) if same(c, fig)]
            why = build.reader_b({k: v for k, v in (agree[0] if agree else fig).items() if k != "confidence"}, src["text"])
            if why:
                why_out[f"reader B: {why}"] += 1
                continue
            kept.append((src, j, IR.from_dict(fig), "claude+32b" if agree else "32b+readerB"))
    cases, mismatches = [], []
    for src, j, ev, pair in kept:
        for family, label, claim_ir in build.variants(ev, build.h(src["id"], j)):
            claim = build.sentence(claim_ir)
            got, why = compare(claim_ir, ev)
            if got != label:
                mismatches.append({"family": family, "claim": claim, "evidence": src["text"], "irlib": got, "why": why})
            cases.append({"id": f"bh-{src['id']}-{j}-{family.split()[0]}", "layer": "B-b", "company": src["company_id"],
                          "sector": build.SECTOR.get(src["company_id"], "?"), "family": family, "claim": claim,
                          "evidence": src["text"], "labels": [label], "claim_ir": claim_ir.as_dict(),
                          "evidence_ir": ev.as_dict(), "fold": build.h(src["company_id"]) % 5, "set": "heldout_v12", "pair": pair})
    (HERE / "gs_heldout_v12.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
    stats = {"figures_kept": len(kept), "by_pair": dict(Counter(k[3] for k in kept)), "not_kept": dict(why_out.most_common()),
             "cases": len(cases), "sentences": len({k[0]["text"] for k in kept}),
             "by_label": dict(Counter(c["labels"][0] for c in cases)), "by_family": dict(Counter(c["family"] for c in cases)),
             "by_company": dict(Counter(c["company"] for c in cases)), "irlib_vs_family_mismatches": len(mismatches)}
    (HERE / "stats_heldout_v12.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    for m in mismatches[:8]:
        print("  mismatch", m)


if __name__ == "__main__":
    main()
