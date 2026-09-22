#!/usr/bin/env python3
"""Repair the two lineage invariants the v1 merge broke.

The v1 merge deduplicated by `doc_id` and dropped everything else on the floor.
Two consequences the audit caught:

1. **Content duplicates were invisible.** `doc_id` is `<target>:<sha16>`, so the
   same ASIC media release collected under Vanguard, Mercer, Black Mountain and
   TLOU produced four distinct ids for one artifact. Nothing recorded that they
   are the same bytes — which is a leakage hazard, because a split could put one
   copy in train and another in test and score the model on a document it has
   already read.

2. **Ingestion lineage was lost.** Phase 1 (authority case packs) and phase 2
   (corporate disclosure) ran as separate jobs; after the merge nothing said
   which row came from which, so a phase-specific bug could not be traced.

This adds `content_group`, `duplicate_of` and `ingestion_phase` without removing
any row. A duplicate is *marked*, never deleted: the second copy carries real
provenance (a different target found it) and deleting it would destroy that.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quantum_gw.utils.jsonl import read_jsonl, write_jsonl  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "data/legal_cases/documents.jsonl"


# source_type is the faithful signal for which crawl phase produced a row:
# phase 1 collected authority artifacts, phase 2 corporate disclosures.
PHASE = {"authority": "phase1_case_pack", "corporate": "phase2_disclosure"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=Path, default=DOCS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = [json.loads(x) for x in args.docs.read_text(encoding="utf-8").split("\n") if x.strip()]

    by_sha: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if r.get("sha256"):
            by_sha[r["sha256"]].append(r)

    groups = marked = phased = 0
    for sha, members in by_sha.items():
        # Stable canonical choice so re-running is idempotent and reviewable.
        members.sort(key=lambda r: (r.get("accessed_at") or "", r["doc_id"]))
        canonical = members[0]["doc_id"]
        if len(members) > 1:
            groups += 1
        for m in members:
            m["content_group"] = f"cg-{sha[:16]}"
            m["duplicate_of"] = None if m["doc_id"] == canonical else canonical
            if m["doc_id"] != canonical:
                marked += 1

    for r in rows:
        r.setdefault("content_group", None)
        r.setdefault("duplicate_of", None)
        r["ingestion_phase"] = PHASE.get(r.get("source_type"), "unknown")
        phased += 1

    print(f"content groups with >1 member : {groups}")
    print(f"rows marked as duplicate_of   : {marked}")
    print(f"rows given ingestion_phase    : {phased}")
    dist: dict[str, int] = defaultdict(int)
    for r in rows:
        dist[r["ingestion_phase"]] += 1
    print(f"phase distribution            : {dict(dist)}")

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return 0

    write_jsonl(args.docs, rows)
    print(f"\nrewrote {len(rows)} rows in {args.docs}")

    # A manifest is what makes the merge provable rather than asserted.
    manifest = args.docs.parent / "MERGE_MANIFEST.json"
    manifest.write_text(json.dumps({
        "documents": len(rows),
        "unique_doc_ids": len({r["doc_id"] for r in rows}),
        "unique_content_hashes": len(by_sha),
        "content_groups_with_duplicates": groups,
        "rows_marked_duplicate": marked,
        "by_ingestion_phase": dict(dist),
        "note": ("union(legal_cases, legal_cases_disclosure) -> one corpus. "
                 "Duplicates are marked, never deleted: a second copy carries "
                 "real provenance from a different target. Any split must group "
                 "by content_group, not doc_id."),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
