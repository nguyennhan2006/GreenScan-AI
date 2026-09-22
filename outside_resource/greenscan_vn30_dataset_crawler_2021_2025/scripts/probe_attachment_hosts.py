#!/usr/bin/env python3
"""Report which hosts actually serve the report files for each configured company.

Vietnamese IR sites almost always put the HTML listing on the corporate domain
and the PDFs on a separate CDN (``d8um25gjecm9v.cloudfront.net`` for Vinamilk,
``cdn.pnj.io`` for PNJ, ``file.hoaphat.com.vn`` for Hoa Phat). ``allowed_host()``
checks ``official_domains + attachment_domains``, so when ``attachment_domains``
is empty the crawler walks the listing, finds every PDF, rejects all of them on
host grounds and finishes reporting success with zero documents.

That failure is silent, which is what makes it expensive. Run this before a
crawl and paste the reported hosts into ``attachment_domains``.

    python scripts/probe_attachment_hosts.py
    python scripts/probe_attachment_hosts.py --company vnm --company pnj
    python scripts/probe_attachment_hosts.py --write   # update companies.yml

``--write`` only ever adds hosts that are not already covered by
``official_domains``; it never removes anything a human put there.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/companies.yml"

FILE_RE = re.compile(r"""https?://[^\s"'<>\\]+\.(?:pdf|docx?|xlsx?|csv)""", re.I)
HEADERS = {
    "User-Agent": "GreenScanVNResearchBot/1.0 (+replace-with-team-email)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def covered(host: str, domains: list[str]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def probe(client: httpx.Client, urls: list[str], delay: float) -> tuple[collections.Counter, list[str]]:
    hosts: collections.Counter[str] = collections.Counter()
    notes: list[str] = []
    for url in urls:
        try:
            r = client.get(url)
        except Exception as exc:  # noqa: BLE001 - a dead URL is a finding, not a crash
            notes.append(f"{url} -> {type(exc).__name__}")
            continue
        if r.status_code != 200:
            notes.append(f"{url} -> HTTP {r.status_code}")
            continue
        found = FILE_RE.findall(r.text)
        if not found:
            notes.append(f"{url} -> 200 but 0 file links ({len(r.text):,} chars; may be JS-rendered)")
        for link in found:
            host = urlparse(link).hostname
            if host:
                hosts[host] += 1
        time.sleep(delay)
    return hosts, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--company", action="append", default=[], help="Company id; repeatable")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--write", action="store_true", help="Write discovered hosts into the config")
    args = ap.parse_args()

    raw = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    companies = raw["companies"]
    if args.company:
        wanted = {c.lower() for c in args.company}
        companies = [c for c in companies if c["id"] in wanted or c["ticker"].lower() in wanted]
    if not companies:
        print("No company matched", file=sys.stderr)
        return 2

    changed = 0
    with httpx.Client(headers=HEADERS, timeout=40, follow_redirects=True) as client:
        for company in companies:
            official = list(company.get("official_domains") or [])
            existing = list(company.get("attachment_domains") or [])
            urls = [str(u) for u in company.get("official_start_urls") or []]

            hosts, notes = probe(client, urls, args.delay)
            new = [h for h, _ in hosts.most_common() if not covered(h, official + existing)]

            print(f"\n=== {company['id']} ({company['ticker']}) ===")
            if hosts:
                print("  file hosts: " + ", ".join(f"{h} x{n}" for h, n in hosts.most_common()))
            else:
                print("  file hosts: NONE FOUND")
            for note in notes:
                print(f"  ! {note}")
            if new:
                print(f"  -> missing from attachment_domains: {new}")
                if args.write:
                    company["attachment_domains"] = existing + new
                    changed += 1

    if args.write and changed:
        args.config.write_text(
            yaml.safe_dump(raw, allow_unicode=True, sort_keys=False, width=4096),
            encoding="utf-8",
        )
        print(f"\nUpdated attachment_domains for {changed} companies in {args.config}")
    elif args.write:
        print("\nNo config changes needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
