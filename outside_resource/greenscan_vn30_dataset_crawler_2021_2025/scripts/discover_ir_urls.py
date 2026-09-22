#!/usr/bin/env python3
"""Find the real investor-relations pages for companies whose start URLs are dead.

The start URLs in ``configs/companies.yml`` were largely written to a guessed
pattern (``https://<domain>/quan-he-co-dong/``). Probing all 30 companies on
2026-08-07 returned 11 straight 404s, which is what a guessed path looks like at
scale. This walks each company's homepage and sitemaps and reports the links
that actually exist and actually mention investor-relations or report keywords.

    python scripts/discover_ir_urls.py --company ctg --company mwg
    python scripts/discover_ir_urls.py --only-broken          # 404 / error ones
    python scripts/discover_ir_urls.py --only-broken --write

``--write`` replaces ``official_start_urls`` for a company only when every one
of its current URLs is dead and at least one candidate was verified as HTTP 200.
Companies whose pages load but render via JavaScript are left alone: a different
URL will not fix those, an adapter with a browser will.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/companies.yml"

HEADERS = {
    "User-Agent": "GreenScanVNResearchBot/1.0 (+replace-with-team-email)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "vi,en;q=0.8",
}

# Ordered best-first: a dedicated report listing beats a generic IR landing page.
KEYWORDS = [
    ("bao-cao-phat-trien-ben-vung", 10), ("phat-trien-ben-vung", 9),
    ("sustainability-report", 10), ("sustainability", 8),
    ("bao-cao-thuong-nien", 10), ("annual-report", 10),
    ("bao-cao-tai-chinh", 9), ("financial-statement", 9), ("financial-report", 9),
    ("bao-cao-quan-tri", 8), ("governance-report", 8),
    ("bao-cao", 6), ("report", 5),
    ("quan-he-co-dong", 7), ("quan-he-nha-dau-tu", 7), ("co-dong", 5),
    ("nha-dau-tu", 5), ("investor-relation", 7), ("investor", 5), ("shareholder", 5),
]
FILE_RE = re.compile(r"""https?://[^\s"'<>\\]+\.(?:pdf|docx?|xlsx?)""", re.I)


def score(url: str, text: str) -> int:
    blob = f"{url} {text}".casefold()
    return sum(weight for kw, weight in KEYWORDS if kw in blob)


def candidates_from(client: httpx.Client, origin: str, domains: list[str]) -> list[tuple[int, str]]:
    try:
        r = client.get(origin)
        r.raise_for_status()
    except Exception:  # noqa: BLE001
        return []
    soup = BeautifulSoup(r.text, "lxml")
    seen: dict[str, int] = {}
    for a in soup.find_all("a", href=True):
        url = urljoin(str(r.url), a["href"]).split("#")[0]
        host = (urlparse(url).hostname or "").lower()
        if not any(host == d or host.endswith("." + d) for d in domains):
            continue
        if urlparse(url).scheme not in {"http", "https"}:
            continue
        s = score(url, " ".join(a.stripped_strings)[:200])
        if s > 0:
            seen[url] = max(seen.get(url, 0), s)
    return sorted(((s, u) for u, s in seen.items()), reverse=True)


def verify(client: httpx.Client, url: str) -> tuple[int | None, int, str]:
    """Return (status, file_link_count, note) for a candidate page."""
    try:
        r = client.get(url)
    except Exception as exc:  # noqa: BLE001
        return None, 0, type(exc).__name__
    if r.status_code != 200:
        return r.status_code, 0, ""
    return 200, len(FILE_RE.findall(r.text)), ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--company", action="append", default=[])
    ap.add_argument("--only-broken", action="store_true",
                    help="Only companies whose every start URL is non-200")
    ap.add_argument("--max-candidates", type=int, default=6)
    ap.add_argument("--delay", type=float, default=0.7)
    ap.add_argument("--write", action="store_true")
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
    with httpx.Client(headers=HEADERS, timeout=35, follow_redirects=True) as client:
        for company in companies:
            domains = list(company.get("official_domains") or [])
            current = [str(u) for u in company.get("official_start_urls") or []]

            alive = []
            for url in current:
                status, files, note = verify(client, url)
                if status == 200:
                    alive.append((url, files))
                time.sleep(args.delay)

            if args.only_broken and alive:
                continue

            print(f"\n=== {company['id']} ({company['ticker']}) ===")
            print(f"  configured: {len(current)} URL(s), {len(alive)} alive")

            found: list[tuple[int, str, int]] = []
            for domain in domains:
                for origin in (f"https://www.{domain}/", f"https://{domain}/"):
                    ranked = candidates_from(client, origin, domains)
                    if not ranked:
                        continue
                    for s, url in ranked[: args.max_candidates]:
                        status, files, note = verify(client, url)
                        time.sleep(args.delay)
                        marker = "OK " if status == 200 else f"{status or note} "
                        print(f"    [{s:>2}] {marker}files={files:<3} {url[:100]}")
                        if status == 200:
                            found.append((s + files * 3, url, files))
                    break
                if found:
                    break

            if not found:
                print("    no reachable candidate found")
                continue

            best = [u for _, u, _ in sorted(found, reverse=True)[:4]]
            if args.write and not alive:
                company["official_start_urls"] = best
                changed += 1
                print(f"    -> official_start_urls := {best}")

    if args.write and changed:
        args.config.write_text(
            yaml.safe_dump(raw, allow_unicode=True, sort_keys=False, width=4096),
            encoding="utf-8",
        )
        print(f"\nUpdated official_start_urls for {changed} companies in {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
