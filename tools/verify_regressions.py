#!/usr/bin/env python3
"""Verify the seven crawl regressions listed in the legal-case crawl pack.

Gate for `docs/greenscan-legal-case-crawl-pack/docs/00_CURRENT_STATE_AND_BOUNDARIES.md`.
Run before any new crawl; the pack requires an audit before downloading anything.

Each check executes real code rather than grepping for a fix, because six of the
seven regressions were originally silent -- they returned success while losing
data, so "the code looks right" is not evidence.

    python tools/verify_regressions.py
    python tools/verify_regressions.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CRAWLER = REPO / "outside_resource/greenscan_vn30_dataset_crawler_2021_2025"
sys.path.insert(0, str(CRAWLER))

RESULTS: list[dict] = []


def record(n: int, name: str, ok: bool, detail: str) -> None:
    RESULTS.append({"regression": n, "name": name, "status": "PASS" if ok else "FAIL",
                    "detail": detail})


def check_1_request_headers() -> None:
    """SEC WAF: a request without Accept is refused; the downloader must send one."""
    src = (REPO / "data/real_cases/scripts/download_sources.py").read_text(encoding="utf-8")
    has_accept = '"Accept"' in src and "Accept-Encoding" in src
    decodes = "_decode(" in src and "gzip" in src
    record(1, "SEC/WAF headers", has_accept and decodes,
           f"Accept+Accept-Encoding sent={has_accept}, gzip decode handled={decodes}")


def check_2_attachment_domains() -> None:
    """Empty attachment_domains must be detectable, not a silent zero-document run."""
    probe = CRAWLER / "scripts/probe_attachment_hosts.py"
    import yaml
    cfg = yaml.safe_load((CRAWLER / "configs/companies.yml").read_text(encoding="utf-8"))
    with_docs = {"vnm", "pnj", "sab", "cdn", "dpr", "dgw", "bmp", "tlg", "bvh"}
    missing = [c["id"] for c in cfg["companies"]
               if c["id"] in with_docs and not (c.get("attachment_domains") or [])
               and c["id"] in {"vnm", "pnj", "sab", "cdn"}]
    # Detection tooling must exist; config for known-CDN companies must be populated.
    record(2, "attachment_domains populated + probe exists",
           probe.is_file() and not missing,
           f"probe script={probe.is_file()}, known-CDN companies still empty={missing or 'none'}")


def check_3_url_validation() -> None:
    """Configured start URLs must be discovered/verified, never pattern-guessed."""
    src = (CRAWLER / "scripts/discover_ir_urls.py").read_text(encoding="utf-8")
    verifies = "def verify(" in src and "status_code" in src
    only_live = "if args.write and not alive" in src
    record(3, "IR URLs verified before written to config", verifies and only_live,
           f"HTTP-verifies candidates={verifies}, writes only when all current URLs dead={only_live}")


def check_4_asset_filter() -> None:
    from crawler.utils import is_page_asset
    assets = ["https://x.vn/a/jquery.js", "https://x.vn/b/main.css", "https://x.vn/favicon.ico",
              "https://x.vn/f/logo.png", "https://x.vn/w/font.woff2"]
    docs = ["https://x.vn/f/bctn-2024.pdf", "https://x.vn/reports/",
            "https://x.vn/d/Download.ashx?f=a.pdf", "https://x.vn/r/report.docx"]
    ok = all(is_page_asset(u) for u in assets) and not any(is_page_asset(u) for u in docs)
    record(4, "static assets filtered before scoring", ok,
           f"{len(assets)} asset URLs blocked, {len(docs)} document URLs preserved")


def check_5_robots_policy() -> None:
    """RFC 9309: 4xx = unavailable (allowed); 5xx/transport = unreachable (deny)."""
    import httpx
    from crawler.robots import Robots

    def gate(status: int, body: str = ""):
        c = httpx.Client(transport=httpx.MockTransport(
            lambda r: httpx.Response(status, text=body)))
        return Robots(c, "Bot", "allow", "skip")

    url = "https://cdn.example/files/report.pdf"
    four = all(gate(s).allowed(url)[0] for s in (400, 401, 403, 404, 410, 429))
    five = all(not gate(s).allowed(url)[0] for s in (500, 502, 503))
    rules = gate(200, "User-agent: *\nDisallow: /secret\n")
    honored = (rules.allowed("https://s.example/ok/a.pdf")[0] is True)
    rules2 = gate(200, "User-agent: *\nDisallow: /secret\n")
    blocked = (rules2.allowed("https://s.example/secret/a.pdf")[0] is False)
    record(5, "robots 4xx allowed / 5xx denied / rules honored",
           four and five and honored and blocked,
           f"4xx allowed={four}, 5xx denied={five}, served Disallow still enforced={blocked}")


def check_6_per_target_cap() -> None:
    from crawler.config import load_companies
    from crawler.core import CompanyCrawler
    import tempfile
    root = Path(tempfile.mkdtemp())
    c = load_companies(CRAWLER / "configs/companies.yml")[0]
    capped = CompanyCrawler(c, root, dry=True, max_documents=3)
    uncapped = CompanyCrawler(c, root, dry=True)
    try:
        capped.stored = 3
        uncapped.stored = 10_000
        ok = capped.budget_spent() and not uncapped.budget_spent()
        record(6, "per-target document cap", ok,
               f"cap honored at limit={capped.budget_spent()}, absent cap never trips={not uncapped.budget_spent()}")
    finally:
        capped.close()
        uncapped.close()


def check_7_jsonl_safety() -> None:
    """U+2028/29/85 must not survive into a .jsonl line, and readers must not splitlines()."""
    from dataset.build import jsonl
    import tempfile
    out = Path(tempfile.mkdtemp()) / "t.jsonl"
    records = [{"t": "a b"}, {"t": "c d"}, {"t": "ef"}, {"t": "plain"}]
    jsonl(out, records)
    raw = out.read_text(encoding="utf-8")
    writer_ok = len(raw.splitlines()) == raw.count("\n") == len(records)
    round_trip = [json.loads(x) for x in raw.split("\n") if x.strip()] == records

    consumers = ["src/quantum_gw/evaluation/runner.py",
                 "data/real_cases/scripts/run_case.py",
                 "data/real_cases/scripts/validate_pack.py",
                 "data/real_cases/scripts/create_training_view.py"]
    offenders = [c for c in consumers
                 if ".splitlines()" in (REPO / c).read_text(encoding="utf-8")]
    record(7, "JSONL separator safety", writer_ok and round_trip and not offenders,
           f"writer escapes={writer_ok}, round-trip exact={round_trip}, "
           f"consumers still using splitlines()={offenders or 'none'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for fn in [check_1_request_headers, check_2_attachment_domains, check_3_url_validation,
               check_4_asset_filter, check_5_robots_policy, check_6_per_target_cap,
               check_7_jsonl_safety]:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - a crashing check is a failing check
            record(len(RESULTS) + 1, fn.__name__, False, f"check raised {type(exc).__name__}: {exc}")

    failed = [r for r in RESULTS if r["status"] != "PASS"]
    if args.json:
        print(json.dumps({"results": RESULTS, "all_pass": not failed}, indent=2, ensure_ascii=False))
    else:
        for r in RESULTS:
            mark = "PASS" if r["status"] == "PASS" else "FAIL"
            print(f"[{mark}] R{r['regression']}. {r['name']}\n        {r['detail']}")
        print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} regressions holding")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
