#!/usr/bin/env python3
"""Harvest report files from investor-relations pages that render via JavaScript.

Probing the 30 configured companies on 2026-08-07 found 12 whose IR pages
return HTTP 200 with a full HTML shell and zero document links: the listing is
fetched by client-side script after load. The static crawler cannot see those
documents, and no change of URL fixes it.

This renders those pages in Chromium, waits for the network to settle, scrolls
to trigger lazy loading, then extracts document links and downloads them through
the *same* ``Storage``/``classify``/``filetypes`` code the static crawler uses.
Records therefore land in the same ``metadata.sqlite3`` with the same schema and
``dataset build`` consumes them with no special case.

    python scripts/harvest_js_listings.py --company bid --data-root data/raw --dry-run
    python scripts/harvest_js_listings.py --company bid --company pan --data-root data/raw

Same rules as the static crawler: robots.txt is honoured, rate limits apply, and
nothing bypasses a login, paywall or anti-bot challenge. Rendering a public page
the way a browser would is not an evasion; if a site blocks the crawl, it stays
blocked.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crawler.classify import attributes, classify, preferred_year, relevant  # noqa: E402
from crawler.config import load_companies  # noqa: E402
from crawler.filetypes import infer_extension  # noqa: E402
from crawler.inspect import inspect_pdf  # noqa: E402
from crawler.rate_limit import RateLimiter  # noqa: E402
from crawler.robots import Robots  # noqa: E402
from crawler.storage import Storage  # noqa: E402
from crawler.utils import canonical_url, filename, host_allowed, is_page_asset  # noqa: E402

log = logging.getLogger("harvest_js")

DOC_SUFFIXES = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv")

# Links whose href carries no file extension but which are download endpoints.
HANDLER_HINTS = ("download", "attachment", "file=", ".ashx", "tai-lieu", "document", "getfile")


def render(page, url: str, settle_ms: int) -> tuple[str, list[dict]]:
    """Load a page, let client-side script populate it, return HTML + link records."""
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    try:
        page.wait_for_load_state("networkidle", timeout=settle_ms)
    except Exception:  # noqa: BLE001 - a chatty page never goes idle; its DOM is still usable
        page.wait_for_timeout(settle_ms)

    # Lazy-loaded listings only materialise once scrolled into view.
    for _ in range(6):
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(600)

    links = page.eval_on_selector_all(
        "a[href], [data-href], [data-url], [data-file]",
        """els => els.map(e => ({
             href: e.getAttribute('href') || e.getAttribute('data-href')
                   || e.getAttribute('data-url') || e.getAttribute('data-file') || '',
             text: (e.innerText || e.textContent || '').trim().slice(0, 300),
             context: (e.closest('tr, li, .item, .card, div') || e).innerText
                        ? (e.closest('tr, li, .item, .card, div') || e).innerText.trim().slice(0, 800)
                        : ''
           }))""",
    )
    return page.content(), links


def looks_like_document(url: str, text: str) -> bool:
    path = urlparse(url).path.lower()
    if path.endswith(DOC_SUFFIXES):
        return True
    return any(hint in (url + " " + text).casefold() for hint in HANDLER_HINTS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/companies.yml"))
    ap.add_argument("--company", action="append", default=[], help="Company id or ticker; repeatable")
    ap.add_argument("--data-root", type=Path, default=Path("data/raw"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--settle-ms", type=int, default=6000)
    ap.add_argument("--max-documents", type=int, default=80)
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(levelname)s %(message)s")

    companies = load_companies(args.config)
    if args.company:
        wanted = {c.lower() for c in args.company}
        companies = [c for c in companies if c.id in wanted or c.ticker.lower() in wanted]
    if not companies:
        print("No company matched", file=sys.stderr)
        return 2

    from playwright.sync_api import sync_playwright

    storage = Storage(args.data_root)
    totals = {"discovered": 0, "downloaded": 0, "duplicate": 0, "skipped": 0}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for company in companies:
            policy = company.policy
            domains = company.official_domains + company.attachment_domains
            client = httpx.Client(
                headers={"User-Agent": policy.user_agent, "Accept": "*/*"},
                follow_redirects=True,
                timeout=httpx.Timeout(60, connect=15),
                verify=policy.verify_ssl,
            )
            robots = Robots(client, policy.user_agent, policy.robots_on_missing, policy.robots_on_error)
            limiter = RateLimiter(policy.max_requests_per_minute, policy.delay_seconds)
            run = f"{company.id}-js-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
            stored = 0

            context = browser.new_context(user_agent=policy.user_agent, locale="vi-VN")
            page = context.new_page()
            log.info("=== %s (%s) ===", company.id, company.ticker)

            for start in company.official_start_urls:
                start_url = str(start)
                ok, reason = robots.allowed(start_url)
                if not ok:
                    log.warning("robots denied %s (%s)", start_url, reason)
                    continue
                try:
                    _, links = render(page, start_url, args.settle_ms)
                except Exception as exc:  # noqa: BLE001
                    log.warning("render failed %s: %s", start_url, type(exc).__name__)
                    continue

                seen: set[str] = set()
                for link in links:
                    href = (link.get("href") or "").strip()
                    if not href or href.startswith(("javascript:", "mailto:", "#")):
                        continue
                    url = canonical_url(urljoin(start_url, href))
                    if url in seen or is_page_asset(url):
                        continue
                    seen.add(url)

                    text = f"{link.get('text','')} {link.get('context','')} {url}"
                    if not looks_like_document(url, text):
                        continue
                    if not host_allowed(url, domains):
                        log.debug("host not allowed: %s", url)
                        continue
                    if not relevant(text, company.ticker, company.company, company.years):
                        continue

                    year, found = preferred_year(text, company.years)
                    record = {
                        "document_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{company.id}:{url}")),
                        "company_id": company.id, "ticker": company.ticker,
                        "exchange": company.exchange, "source_kind": "official_js",
                        "source_authority": "official_company", "source_page_url": start_url,
                        "url": url, "title": (link.get("text") or filename(url))[:300],
                        "publication_year": year, "discovered_years": found,
                        "document_type": classify(text), **attributes(text),
                        "metadata": {"context": (link.get("context") or "")[:2000],
                                     "rendered_with": "chromium"},
                    }
                    storage.upsert(record)
                    storage.manifest(run, {"event": "discovered", **record})
                    totals["discovered"] += 1

                    if args.dry_run:
                        log.info("[DRY] %s | %s | %s", record["document_type"], year, url[:95])
                        continue
                    if storage.has(url) or stored >= args.max_documents:
                        totals["skipped"] += 1
                        continue
                    ok, reason = robots.allowed(url)
                    if not ok:
                        storage.update(url, "robots_denied", error_code=reason)
                        continue

                    try:
                        limiter.wait()
                        resp = client.get(url)
                        resp.raise_for_status()
                    except Exception as exc:  # noqa: BLE001
                        storage.update(url, "temporary_error", error_code=type(exc).__name__,
                                       error_message=str(exc)[:500])
                        continue

                    ext = infer_extension(str(resp.url), resp.headers.get("content-type", ""), resp.content)
                    if ext in (None, ".html") or ext not in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv"}:
                        storage.update(url, "invalid_document", error_code=str(ext))
                        continue

                    sha, path, existed = storage.store(resp.content, ext)
                    fields = {"final_url": str(resp.url), "extension": ext,
                              "content_type": resp.headers.get("content-type"),
                              "content_length": len(resp.content), "sha256": sha,
                              "object_path": str(path), "downloaded_at": storage.now()}
                    if ext == ".pdf":
                        try:
                            fields.update(inspect_pdf(path, record["title"], company.years))
                        except Exception as exc:  # noqa: BLE001
                            fields["error_message"] = f"inspection:{exc}"
                    status = "duplicate" if existed else "downloaded"
                    storage.update(url, status, **fields)
                    storage.manifest(run, {"event": status, "company": company.id, "url": url,
                                           "sha256": sha, "path": str(path)})
                    totals[status] += 1
                    stored += 1
                    log.info("%s %s -> %s", status, url[:85], path.name)

                time.sleep(policy.delay_seconds)

            page.close()
            context.close()
            client.close()
        browser.close()

    print(f"JS harvest totals: {totals}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
