#!/usr/bin/env python3
"""Resolve each registered instrument to its Công báo edition.

Why Công báo rather than the issuing portal: the signed PDF on
`datafiles.chinhphu.vn` is frequently a **scan** — 21/2025/QĐ-TTg is 32 pages
with 148 characters of text — while the gazette publishes a typeset edition with
a real text layer. Luật BVMT 2020 from `congbaocdn` parses to 177,001 characters,
94 Điều and 6 Chương with no OCR at all.

Công báo's search and index pages are JS-rendered (both return the homepage to a
plain GET), but `/van-ban/<slug>.htm` is served normally. So this drives the
search in Chromium purely to *discover the slug*, then everything downstream is
an ordinary HTTP fetch of an official URL.

    python tools/resolve_congbao.py --all
    python tools/resolve_congbao.py --id QD21-2025-QD-TTg --write

Nothing here guesses a URL: a document number that the gazette search does not
return is reported unresolved rather than pattern-matched into an id.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
SEARCH = "https://congbao.chinhphu.vn/tim-kiem-van-ban"
UA = "GreenScanResearchBot/1.0 (academic legal-compliance research)"

SLUG_RE = re.compile(r"/van-ban/([a-z0-9\-]+)\.htm")


def normalise_number(number: str) -> list[str]:
    """Search keys for one document number.

    "21/2025/QĐ-TTg" is written several ways across the portal, so a single
    literal query misses. Ordered from most to least specific.
    """
    n = number.strip()
    bare = n.split("/")[0]
    year = next((p for p in n.split("/") if p.isdigit() and len(p) == 4), "")
    return [n, n.replace("/", "-"), f"{bare}/{year}" if year else bare, bare]


def resolve(page, entry: dict, settle_ms: int) -> dict:
    number = entry["document_number"]
    out = {"id": entry["id"], "document_number": number, "congbao_slug": None,
           "congbao_url": None, "candidates": []}

    for key in normalise_number(number):
        try:
            page.goto(SEARCH, wait_until="domcontentloaded", timeout=60_000)
            box = page.locator("input[type='text'], input[type='search']").first
            box.fill(key, timeout=15_000)
            box.press("Enter")
            page.wait_for_timeout(settle_ms)
        except Exception:  # noqa: BLE001 - a failed query is not a failed document
            continue

        html = page.content()
        for slug in dict.fromkeys(SLUG_RE.findall(html)):
            # The slug embeds the number, so match on that rather than trusting
            # result ordering.
            flat = slug.replace("-", "")
            wanted = re.sub(r"[^a-z0-9]", "", number.lower()
                            .replace("đ", "d").replace("Đ", "d"))
            if wanted and wanted[:10] in flat:
                out["congbao_slug"] = slug
                out["congbao_url"] = f"https://congbao.chinhphu.vn/van-ban/{slug}.htm"
                out["matched_query"] = key
                return out
            out["candidates"].append(slug)
        if out["candidates"]:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--id", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--settle-ms", type=int, default=3500)
    ap.add_argument("--write", action="store_true", help="write congbao_url into the registry")
    args = ap.parse_args()

    raw = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
    entries = raw["documents"]
    if args.id:
        entries = [e for e in entries if e["id"] in set(args.id)]
    elif not args.all:
        print("Pass --all or --id <ID>.", file=sys.stderr)
        return 2

    from playwright.sync_api import sync_playwright

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(user_agent=UA, locale="vi-VN")
        page = ctx.new_page()
        for entry in entries:
            r = resolve(page, entry, args.settle_ms)
            results.append(r)
            mark = "OK " if r["congbao_slug"] else "-- "
            print(f"{mark}{r['id']:22} {r['document_number']:18} {r['congbao_slug'] or 'unresolved'}")
        ctx.close()
        browser.close()

    resolved = [r for r in results if r["congbao_slug"]]
    if args.write and resolved:
        by_id = {r["id"]: r for r in resolved}
        for entry in raw["documents"]:
            r = by_id.get(entry["id"])
            if r:
                entry["congbao_url"] = r["congbao_url"]
        args.registry.write_text(
            yaml.safe_dump(raw, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8")
        print(f"\nWrote congbao_url for {len(resolved)} document(s) to {args.registry}")

    print(f"\nResolved {len(resolved)}/{len(results)}")
    return 0 if resolved else 1


if __name__ == "__main__":
    raise SystemExit(main())
