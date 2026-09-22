#!/usr/bin/env python3
"""Dataset Audit v2 — lineage, maturity, and split integrity.

Three words that get conflated and must not be:

    unified     physical/schema merge      — folders and IDs reconcile
    audited     integrity checked          — nothing lost, nothing silently dropped
    adjudicated semantically verified      — a human committed to the meaning

v1 established the first two. This tool measures all three separately and
refuses to let the third be inferred from the first two.

    python tools/dataset_audit_v2.py lineage    # merge invariants
    python tools/dataset_audit_v2.py maturity   # L0-L5 census
    python tools/dataset_audit_v2.py split      # company-held-out feasibility
    python tools/dataset_audit_v2.py all

Maturity levels:
    L0 RAW          original PDF/HTML/legal bytes
    L1 PARSED       page/block/table with provenance
    L2 CANDIDATE    pipeline-detected claims and evidence
    L3 CURATED      quality-filtered; annotation-ready, NOT truth
    L4 ADJUDICATED  human-confirmed claim-evidence verdicts
    L5 GOLD         frozen, company-held-out, never used to tune anything
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

VN_DB = REPO / "data/crawl/vn30/raw/metadata.sqlite3"
LEGAL_CASES = REPO / "data/legal_cases/documents.jsonl"
NORMALIZED = REPO / "data/crawl/vn30/normalized"
CURATED = REPO / "data/crawl/vn30/curated"
CLAUSES = REPO / "data/legal/clauses"
REAL_CASES = REPO / "data/real_cases"


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x.strip()]


def ok(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


# ------------------------------------------------------------------ lineage

def cmd_lineage(args) -> int:
    """Check the invariants a merged corpus must satisfy.

    `legal_cases` and `legal_cases_disclosure` were separate roots only because
    the two crawl phases were run apart to avoid SQLite write contention — a
    storage concern, not an ontological one. Merging was correct; merging
    *cleanly* is what this verifies.
    """
    docs = read_jsonl(LEGAL_CASES)
    findings: list[tuple[str, bool, str]] = []

    ids = [d.get("doc_id") for d in docs]
    findings.append(("document_id unique", len(ids) == len(set(ids)),
                     f"{len(ids)} rows, {len(set(ids))} unique"))

    # An id that embeds the old root name would make the merge irreversible and
    # would change if the folder were ever renamed.
    root_leak = [i for i in ids if i and ("legal_cases_disclosure" in i or "phase2" in i)]
    findings.append(("document_id independent of old root", not root_leak,
                     f"{len(root_leak)} id(s) embed a root name"))

    # Same bytes reached by two phases must be visible as one artifact.
    by_sha = defaultdict(list)
    for d in docs:
        if d.get("sha256"):
            by_sha[d["sha256"]].append(d["doc_id"])
    cross = {s: v for s, v in by_sha.items() if len(v) > 1}
    findings.append(("cross-phase content duplicates recorded",
                     all(any(x.get("duplicate_of") for x in docs if x["doc_id"] in v)
                         for v in cross.values()) if cross else True,
                     f"{len(cross)} sha256 group(s) with >1 doc_id"))

    has_phase = sum(1 for d in docs if d.get("ingestion_phase") or d.get("source_partition"))
    findings.append(("ingestion lineage retained", has_phase == len(docs),
                     f"{has_phase}/{len(docs)} carry ingestion_phase"))

    missing_sha = [d["doc_id"] for d in docs if not d.get("sha256")]
    findings.append(("every artifact has a checksum", not missing_sha,
                     f"{len(missing_sha)} without sha256"))

    # A row pointing at a file that is gone is worse than no row: build silently
    # drops it and the count reconciles against nothing.
    dangling = [d["doc_id"] for d in docs
                if d.get("path") and not (REPO / "data/legal_cases" / d["path"]).is_file()]
    findings.append(("no dangling file references", not dangling,
                     f"{len(dangling)} row(s) point at a missing file"))

    reports = (REPO / "data/legal_cases/reports/phase2_disclosure")
    findings.append(("phase-2 audit artifacts preserved", reports.is_dir(),
                     f"{len(list(reports.glob('*'))) if reports.is_dir() else 0} file(s)"))

    orphan_root = (REPO / "data/legal_cases_disclosure").exists()
    findings.append(("no orphaned partition root", not orphan_root,
                     "legal_cases_disclosure still present" if orphan_root else "removed"))

    print("LINEAGE AUDIT — data/legal_cases")
    print("-" * 74)
    for name, passed, detail in findings:
        print(f"  [{ok(passed)}] {name:42} {detail}")
    failed = [f for f in findings if not f[1]]
    print(f"\n  {len(findings) - len(failed)}/{len(findings)} invariants hold")
    if cross:
        print(f"\n  Content-identical groups (same sha256, different doc_id):")
        for sha, group in list(cross.items())[:5]:
            print(f"    {sha[:16]}  {group}")
    return 1 if failed else 0


# ----------------------------------------------------------------- maturity

def cmd_maturity(args) -> int:
    levels: dict[str, dict] = {}

    stored = companies = 0
    if VN_DB.is_file():
        c = sqlite3.connect(f"file:{VN_DB}?mode=ro", uri=True)
        stored = c.execute("select count(*) from documents where status in "
                           "('downloaded','duplicate')").fetchone()[0]
        companies = c.execute("select count(distinct company_id) from documents where "
                              "status in ('downloaded','duplicate')").fetchone()[0]

    legal_docs = len(read_jsonl(LEGAL_CASES))
    clause_files = list(CLAUSES.glob("*.jsonl")) if CLAUSES.is_dir() else []
    clauses = sum(len(read_jsonl(p)) for p in clause_files)

    levels["L0 RAW"] = {
        "vn_documents": stored, "legal_case_documents": legal_docs,
        "legal_instruments_with_text": len(clause_files),
        "usable_for": "parsing, OCR, retrieval development",
        "not_usable_for": "any verdict",
    }
    levels["L1 PARSED"] = {
        "vn_units": len(read_jsonl(NORMALIZED / "units.jsonl")),
        "vn_chunks": len(read_jsonl(NORMALIZED / "chunks.jsonl")),
        "legal_clauses": clauses,
        "usable_for": "retrieval, clause matching",
        "not_usable_for": "clause use without checking effective date and scope",
    }
    levels["L2 CANDIDATE"] = {
        "claim_candidates": len(read_jsonl(NORMALIZED / "claim_candidates.jsonl")),
        "evidence_candidates": len(read_jsonl(NORMALIZED / "evidence_candidates.jsonl")),
        "usable_for": "extraction development, sampling",
        "not_usable_for": "treating every candidate as a real claim",
    }
    levels["L3 CURATED"] = {
        "clean": len(read_jsonl(CURATED / "claim_candidates_clean.jsonl")),
        "annotation_priority": len(read_jsonl(CURATED / "annotation_priority.jsonl")),
        "usable_for": "annotation queue",
        "not_usable_for": "gold labels — filtering is not adjudication",
    }

    adjudicated = 0
    try:
        from quantum_gw.storage.reviews import ReviewStore
        adjudicated = len(ReviewStore().gold_records())
    except Exception:  # noqa: BLE001
        pass
    real_claims = len(read_jsonl(REAL_CASES / "claims/claims.jsonl"))
    real_evidence = len(read_jsonl(REAL_CASES / "evidence/evidence.jsonl"))
    levels["L4 ADJUDICATED"] = {
        "human_adjudicated_reviews": adjudicated,
        "real_case_claims": real_claims, "real_case_evidence": real_evidence,
        "evidence_per_claim": round(real_evidence / real_claims, 2) if real_claims else 0,
        "usable_for": "sanity tests, demo regression",
        "not_usable_for": "any statistical claim about system accuracy",
    }
    frozen = REPO / "data/benchmark/frozen"
    levels["L5 GOLD"] = {
        "frozen_sets": len(list(frozen.glob("*.jsonl"))) if frozen.is_dir() else 0,
        "usable_for": "final reporting only",
        "not_usable_for": "tuning prompts, rules or models — ever",
    }

    print("DATASET MATURITY CENSUS")
    print("=" * 74)
    for name, data in levels.items():
        print(f"\n{name}")
        for k, v in data.items():
            if k in {"usable_for", "not_usable_for"}:
                continue
            print(f"    {k:34} {v:>8,}" if isinstance(v, int) else f"    {k:34} {v:>8}")
        print(f"    -> use for      : {data['usable_for']}")
        print(f"    -> NOT for      : {data['not_usable_for']}")

    l2 = levels["L2 CANDIDATE"]["claim_candidates"]
    l4 = levels["L4 ADJUDICATED"]["real_case_claims"] + adjudicated
    print("\n" + "=" * 74)
    print(f"Supervision ratio: {l4} adjudicated vs {l2:,} candidates "
          f"({l4 / l2:.2%})" if l2 else "no candidates")
    print(f"Corpus breadth   : {companies} companies "
          f"({stored / companies:.0f} docs/company)" if companies else "")
    if l4 < 100:
        print("\nBottleneck is supervision, not volume. Collecting more documents will\n"
              "not move any metric until adjudicated claims reach ~100-200.")
    return 0


# -------------------------------------------------------------------- split

def cmd_split(args) -> int:
    """Company-held-out feasibility.

    A random claim-level split leaks: claim 2024 of company A in test while A's
    2023 and 2025 reports sit in train means the retriever already knows that
    issuer's vocabulary, KPI names and house style. Hold out the *company*
    first, then time within it.
    """
    rows = read_jsonl(CURATED / "annotation_priority.jsonl") or \
        read_jsonl(NORMALIZED / "claim_candidates.jsonl")
    if not rows:
        print("No candidate file found.")
        return 1

    per_company = Counter(r.get("company_id") for r in rows)
    total = sum(per_company.values())
    companies = sorted(per_company.items(), key=lambda x: -x[1])

    print("COMPANY-HELD-OUT SPLIT FEASIBILITY")
    print("-" * 74)
    print(f"  claims: {total:,} across {len(companies)} companies")
    print(f"  largest company holds {companies[0][1] / total:.1%} of claims "
          f"({companies[0][0]})")

    # Fill the test share with as FEW companies as possible: packing it with
    # many tiny issuers hits the percentage but strips train of the diversity
    # the split exists to measure. Largest-that-fits, descending.
    target = total * args.test_fraction
    test, acc = [], 0
    for name, n in companies:                 # descending by claim count
        if acc + n <= target:
            test.append(name)
            acc += n
    train = [c for c, _ in companies if c not in test]
    print(f"\n  proposed held-out companies ({len(test)}): {test}")
    print(f"  test share: {acc / total:.1%} of claims, {len(test)}/{len(companies)} companies")
    print(f"  train companies: {len(train)}")

    if len(companies) < 30:
        print(f"\n  Only {len(companies)} companies. A held-out set of {len(test)} gives a very\n"
              "  wide confidence interval on generalisation — the corpus is deep\n"
              "  (many documents per issuer) but not broad. Report per-company results\n"
              "  rather than a single generalisation number.")
    if args.write:
        out = REPO / "data/crawl/vn30/curated/company_split.json"
        out.write_text(json.dumps(
            {"strategy": "company_held_out_then_temporal",
             "test_companies": sorted(test), "train_companies": sorted(train),
             "test_claim_share": round(acc / total, 4),
             "note": "Hold out the company first; split by year only within train."},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  wrote {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lineage").set_defaults(func=cmd_lineage)
    sub.add_parser("maturity").set_defaults(func=cmd_maturity)
    s = sub.add_parser("split")
    s.add_argument("--test-fraction", type=float, default=0.2)
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_split)
    a = sub.add_parser("all")
    a.set_defaults(func=lambda args: (cmd_lineage(args), print(), cmd_maturity(args),
                                      print(), cmd_split(args))[0])
    a.add_argument("--test-fraction", type=float, default=0.2)
    a.add_argument("--write", action="store_true")
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
