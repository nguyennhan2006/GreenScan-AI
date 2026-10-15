#!/usr/bin/env python3
"""Verified legal catalog (data/legal/catalog/<date>/*.json) → registry candidates.

The catalog is what research agents found and a verifier checked; the live
registry is what rules may bind on. Between them sits this candidates file, in
the registry's own schema so `crawl_legal_sources.py --registry` can harvest it,
but with `review.reviewed_by: null`: nothing here binds a rule until Thảo has
read the signed original.

Kept: laws, decrees, decisions and circulars in force or adopted, relevance
high or medium, with an official URL. Left out, and listed: drafts, checks of
documents already in the registry, evidence lists (they go to the evidence
layer), items about operating GreenScan itself.

    python tools/catalog_to_registry.py --catalog data/legal/catalog/2026-10-13
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
LIVE = REPO / "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
STATUS = {"in_force": "effective", "adopted_not_in_force": "not_yet_effective", "partly_in_force": "effective"}
TYPES = {"QH": "luat", "NĐ-CP": "nghi_dinh", "QĐ-TTg": "quyet_dinh", "TT-": "thong_tu", "QĐ-": "quyet_dinh"}
ISSUES = {"epr_waste": "epr", "ghg_inventory_mrv": "ghg_inventory", "carbon_market_offsets": "carbon_market",
          "advertising_consumer_protection": "advertising_consumer", "product_standards_labeling": "labeling",
          "eco_label_certification": "ecolabel", "taxonomy_green_finance": "green_taxonomy",
          "environmental_monitoring": "emissions", "permitting_eia": "permits", "disclosure_reporting": "disclosure",
          "enforcement_sanctions": "sanctions", "competition": "competition", "inspection": "inspection"}


def registry_id(item: dict) -> str:
    """ND110-2026-ND-CP, TT38-2023-TT-BCT, LUAT-75-2025-QH15 — the live registry's style."""
    num = (item.get("document_number") or "").split()[0]
    m = re.match(r"(\d+)/(\d{4})/([A-Za-zĐ0-9\-]+)", num)
    if not m:
        return re.sub(r"^VN-", "", item["id"])
    n, year, suffix = m.groups()
    suffix = suffix.replace("Đ", "D")
    if suffix.startswith("QH"):
        return f"LUAT-{n}-{year}-{suffix}"
    head = {"ND": "ND", "QD": "QD", "TT": "TT"}.get(suffix.split("-")[0], suffix.split("-")[0])
    return f"{head}{n}-{year}-{suffix}"


def doc_type(number: str) -> str:
    return next((t for k, t in TYPES.items() if k in number), "other")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=REPO / "configs/legal/registry_candidates_2026-10.yaml")
    args = ap.parse_args()
    live = yaml.safe_load(LIVE.read_text(encoding="utf-8"))
    live_ids = {d["id"] for d in live["documents"]}
    live_numbers = {d["document_number"] for d in live["documents"]}

    docs, skipped, ids = [], [], {}
    for f in sorted(args.catalog.glob("*.json")):
        if f.name.endswith(".research.json"):
            continue                       # unverified drafts never become candidates
        for x in json.loads(f.read_text(encoding="utf-8"))["items"]:
            number = (x.get("document_number") or "").split(" (")[0].strip()
            why = None
            if x.get("status") not in STATUS:
                why = f"status {x.get('status')}"
            elif x.get("relevance") not in ("high", "medium"):
                why = "relevance low (product operations, not claims)"
            elif number in live_numbers or "CHECK" in x["id"]:
                why = "already in the live registry (see updates_to_existing)"
            elif not re.match(r"\d+/\d{4}/", number):
                why = "not a numbered legal instrument (evidence list or official letter)"
            elif not x.get("official_url"):
                why = "no official URL"
            if why:
                skipped.append(f"{x['id']}: {why}")
                continue
            rid = registry_id({**x, "document_number": number})
            if rid in live_ids or rid in ids:
                skipped.append(f"{x['id']}: duplicate of {rid}")
                continue
            url = x["official_url"]
            direct = bool(re.search(r"\.(pdf|doc|docx)(\?|$)", url, re.I))
            ids[rid] = x["id"]
            docs.append({
                "id": rid, "document_number": number, "title": x.get("title"), "doc_type": doc_type(number),
                "authority": x.get("authority"), "issued_date": x.get("issued_date") or None,
                "effective_from": x.get("effective_from") or None, "effective_to": None,
                "status": STATUS[x["status"]],
                "legal_issues": sorted({ISSUES[p] for p in x.get("process_types", []) if p in ISSUES}),
                "landing_url": None if direct else url, "original_url": url if direct else None,
                "text_acquisition": "not_attempted",
                "review": {"verification": x.get("verification"), "catalog_id": x["id"], "catalog_file": f.name,
                           "evidence_note": (x.get("evidence_note") or "")[:400], "reviewed_by": None},
                "sectors": x.get("sectors", []), "process_types": x.get("process_types", []),
                "claim_hooks": x.get("claim_hooks", [])[:8],
            })
    out = {
        "version": "legal-source-registry-candidates-2026-10", "generated": "2026-10-13",
        "note": ("Candidates from the verified catalog. Nothing here binds a rule until review.reviewed_by is "
                 "filled after reading the signed original. Harvest: python tools/crawl_legal_sources.py "
                 f"--registry {args.out.relative_to(REPO).as_posix()} --all"),
        "defaults": live["defaults"], "documents": docs,
        "updates_to_existing": [
            {"id": "ND08-2022-ND-CP", "field": "amended_by", "proposed_value": "+ ND110-2026-ND-CP",
             "evidence": "NĐ 110/2026 amends Đ.69.1(b) and repeals Chương VI, Phụ lục XXII–XXIII (EPR) of NĐ 08/2022; "
                         "catalog vn_delta.json ND110-2026-ND-CP (VERIFIED_PRIMARY)"},
        ],
        "skipped": skipped,
    }
    args.out.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    print(f"{len(docs)} candidates -> {args.out.relative_to(REPO)} · skipped {len(skipped)}")
    for s in skipped:
        print("   -", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
