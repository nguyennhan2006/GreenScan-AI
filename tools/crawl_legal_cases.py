#!/usr/bin/env python3
"""Collect the 29 legal-case targets defined by the GreenScan legal-case crawl pack.

Implements `docs/greenscan-legal-case-crawl-pack/docs/04_CRAWL_RUNBOOK.md`:

  Phase 1  authority case pack first (landing page + orders/rulings/attachments)
  Phase 2  official corporate/fund disclosure seeds, 2021-2025
  Phase 3  download with MIME + magic-byte validation and SHA-256
  Phase 4  year resolution, listing metadata before filename
  Phase 7  coverage + leakage
  Phase 8  the five mandatory reports

Driven entirely by `config/legal_case_targets.yaml` -- the runbook forbids
hardcoding 29 loops.

    python tools/crawl_legal_cases.py --dry-run
    python tools/crawl_legal_cases.py --target INT-VANGUARD-AU
    python tools/crawl_legal_cases.py --phase case          # authority packs only
    python tools/crawl_legal_cases.py --max-docs-per-target 25

Label integrity is enforced structurally: nothing here writes a greenwashing
label. `company_has_case=true` is recorded on the *case*, never propagated to a
document or a claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
import yaml
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[1]
PACK = REPO / "docs/greenscan-legal-case-crawl-pack"
sys.path.insert(0, str(REPO / "outside_resource/greenscan_vn30_dataset_crawler_2021_2025"))
sys.path.insert(0, str(REPO / "src"))

from crawler.filetypes import infer_extension  # noqa: E402
from crawler.robots import Robots  # noqa: E402
from crawler.utils import canonical_url, is_page_asset  # noqa: E402
from quantum_gw.utils.jsonl import write_jsonl as jsonl_write  # noqa: E402

log = logging.getLogger("legal_crawl")

CRAWLER_VERSION = "legal-case-crawler/1.0"
CORPORATE_WINDOW = range(2021, 2026)

# SEC's fair-access policy asks for a contact-identifiable agent. Everything else
# gets the same declared agent so operators can identify us in their logs.
USER_AGENT = os.environ.get(
    "GREENSCAN_CRAWLER_UA",
    "GreenScanResearchBot/1.0 (academic ESG claim-verification research; contact via project owner)",
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en,vi;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}

DOC_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".xml"}

# Share widgets sit on every authority page and carry the article title in their
# query string, so they score as case artifacts. They are noise, not a blocked
# source -- keeping them out of failure_queue.csv is what makes that file usable.
SHARE_NOISE = re.compile(
    r"^(mailto:|tel:|javascript:)|(twitter\.com/intent|x\.com/intent|facebook\.com/sharer"
    r"|linkedin\.com/share|wa\.me/|api\.whatsapp\.com|reddit\.com/submit|pinterest\.[a-z.]+/pin)",
    re.I,
)

# Phase 1: anchor text/context signalling a case artifact worth keeping.
CASE_ARTIFACT_TERMS = [
    "order", "judgment", "judgement", "court", "undertaking", "infringement notice",
    "decision", "ruling", "complaint", "press release", "media release", "attachment",
    "penalty", "notice", "determination", "adjudication",
]
# Phase 2 keyword families, from the runbook.
FAMILY_TERMS = {
    "annual_or_integrated": ["annual report", "integrated report", "annual financial report",
                             "10-k", "20-f", "financial statements", "annual review"],
    "sustainability_or_esg": ["sustainability", "esg", "climate", "impact report",
                              "non-financial", "tcfd", "sasb", "responsible investment",
                              "stewardship", "transition plan"],
    "product_disclosure": ["pds", "product disclosure statement", "prospectus",
                           "investment guide", "exclusion", "screen", "holdings",
                           "methodology", "target market determination"],
    "case_artifact": ["advertisement", "market announcement", "packaging", "claim",
                      "campaign", "environmental", "net zero", "carbon neutral", "recycled"],
}
YEAR_RE = re.compile(r"(?<!\d)(20(?:1\d|2\d))(?!\d)")


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, timeout=10).stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def load_targets(path: Path) -> list[dict]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = raw.get("targets") if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"{path}: expected a non-empty 'targets' list")
    return rows


def report_seeds(target: dict) -> list[str]:
    """Official disclosure seeds.

    The registry ships in two shapes: `legal_case_targets.yaml` carries a
    `report_urls` list, `seed_urls.csv` carries flat `report_url_1..4` columns.
    Reading only the CSV shape made Phase 2 iterate an empty list and report
    zero disclosures without a single failure row -- exactly the silent-success
    class of bug this pack exists to prevent.
    """
    urls = target.get("report_urls")
    if isinstance(urls, str):
        urls = [urls]
    elif not isinstance(urls, list):
        urls = []
    flat = [target.get(f"report_url_{i}") for i in range(1, 5)]
    seen, out = set(), []
    for u in [*urls, *flat]:
        u = str(u).strip() if u else ""
        if u and u.lower() not in {"none", "nan"} and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def registered_domains(target: dict) -> set[str]:
    hosts = set()
    for url in [target.get("case_url"), *report_seeds(target)]:
        if url:
            h = (urlparse(str(url)).hostname or "").lower()
            if h:
                hosts.add(h)
                hosts.add(h[4:] if h.startswith("www.") else f"www.{h}")
    return hosts


def host_ok(url: str, allowed: set[str]) -> bool:
    h = (urlparse(url).hostname or "").lower()
    return any(h == d or h.endswith("." + d) for d in allowed)


def classify_family(text: str) -> str | None:
    low = text.casefold()
    for family, terms in FAMILY_TERMS.items():
        if any(t in low for t in terms):
            return family
    return None


def looks_like_case_artifact(text: str) -> bool:
    low = text.casefold()
    return any(t in low for t in CASE_ARTIFACT_TERMS)


class SourceHealth:
    def __init__(self) -> None:
        self.d: dict[str, dict] = defaultdict(
            lambda: {"requests": 0, "success": 0, "http_4xx": 0, "http_5xx": 0,
                     "transport_error": 0, "latencies_ms": [], "robots_status": None,
                     "zero_result_pages": 0})

    def note(self, url: str, status: int | None, ms: float, error: str | None = None) -> None:
        h = (urlparse(url).hostname or "unknown").lower()
        e = self.d[h]
        e["requests"] += 1
        e["latencies_ms"].append(round(ms))
        if error:
            e["transport_error"] += 1
        elif status and 200 <= status < 300:
            e["success"] += 1
        elif status and 400 <= status < 500:
            e["http_4xx"] += 1
        elif status and status >= 500:
            e["http_5xx"] += 1

    def serialise(self) -> dict:
        out = {}
        for host, e in self.d.items():
            lat = sorted(e["latencies_ms"])
            out[host] = {**{k: v for k, v in e.items() if k != "latencies_ms"},
                         "median_latency_ms": lat[len(lat) // 2] if lat else None}
        return out


class LegalCaseCrawler:
    def __init__(self, out_root: Path, *, dry_run: bool, delay: float,
                 max_docs: int, timeout: float):
        self.root = out_root
        self.dry_run = dry_run
        self.delay = delay
        self.max_docs = max_docs
        self.client = httpx.Client(headers=HEADERS, follow_redirects=True,
                                   timeout=httpx.Timeout(timeout, connect=20))
        self.robots = Robots(self.client, USER_AGENT, "allow", "skip")
        self.health = SourceHealth()
        self.documents: list[dict] = []
        self.failures: list[dict] = []
        self.coverage: list[dict] = []
        self._by_hash: dict[str, list[str]] = defaultdict(list)
        self._seen_urls: set[str] = set()
        self.run_id = f"legal-{datetime.now(UTC):%Y%m%d-%H%M%S}"
        self.git = git_sha()

    def close(self) -> None:
        self.client.close()

    # ---------- fetch ----------

    def fetch(self, url: str, *, stage: str, target_id: str) -> httpx.Response | None:
        allowed, reason = self.robots.allowed(url)
        if not allowed:
            self.fail(target_id, url, stage, "robots_denied", None, retryable=False,
                      next_action=f"manual review ({reason})")
            return None
        start = time.perf_counter()
        try:
            r = self.client.get(url)
            ms = (time.perf_counter() - start) * 1000
            self.health.note(url, r.status_code, ms)
            r.raise_for_status()
            time.sleep(self.delay)
            return r
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            self.health.note(url, code, (time.perf_counter() - start) * 1000)
            self.fail(target_id, url, stage, f"http_{code}", code,
                      retryable=code in {429, 500, 502, 503, 504},
                      next_action="retry with backoff" if code >= 500 else "manual acquisition")
            return None
        except Exception as exc:  # noqa: BLE001
            self.health.note(url, None, (time.perf_counter() - start) * 1000, error=str(exc))
            self.fail(target_id, url, stage, type(exc).__name__, None, retryable=True,
                      next_action="retry")
            return None

    def fail(self, target_id: str, url: str, stage: str, error_class: str,
             status: int | None, *, retryable: bool, next_action: str) -> None:
        self.failures.append({"target_id": target_id, "url": url, "stage": stage,
                              "error_class": error_class, "http_status": status or "",
                              "retryable": str(retryable).lower(), "attempts": 1,
                              "next_action": next_action})
        log.warning("%s | %s | %s", target_id, error_class, url[:100])

    # ---------- store ----------

    def store(self, target: dict, url: str, resp: httpx.Response, *, source_type: str,
              artifact_role: str, doc_family: str | None, title: str,
              listing_year: int | None) -> bool:
        ext = infer_extension(str(resp.url), resp.headers.get("content-type", ""), resp.content)
        if ext is None:
            self.fail(target["id"], url, "validate", "unrecognized_content", resp.status_code,
                      retryable=False, next_action="inspect manually")
            return False
        # Runbook Phase 3: reject an HTML error page saved as .pdf.
        if ext == ".html" and source_type == "corporate" and artifact_role != "listing_page":
            return False

        sha = hashlib.sha256(resp.content).hexdigest()
        year, year_status, candidates = self.resolve_year(listing_year, title, url, resp, ext)

        tdir = self.root / target["id"]
        sub = "authority" if source_type == "authority" else "corporate"
        path = tdir / sub / f"{sha[:16]}{ext}"
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                self.fail(target["id"], url, "store", "hash_collision_same_name",
                          None, retryable=False, next_action="investigate")
                return False
            path.write_bytes(resp.content)

        self._by_hash[sha].append(f"{target['id']}:{url}")
        self.documents.append({
            "doc_id": f"{target['id']}:{sha[:16]}",
            "target_id": target["id"],
            "case_entity": target.get("case_entity"),
            "reporting_entity": target.get("reporting_entity"),
            "brand": target.get("brand"),
            "relationship": target.get("relationship"),
            "authority": target.get("authority"),
            "case_id": target.get("case_id"),
            "legal_strength": target.get("level"),
            "qualifier": target.get("qualifier"),
            "source_url": url,
            "final_url": str(resp.url),
            "source_domain": (urlparse(url).hostname or "").lower(),
            "source_type": source_type,
            "artifact_role": artifact_role,
            "doc_family": doc_family,
            "profile": target.get("profile"),
            "title": title[:400],
            "year": year,
            "year_status": year_status,
            "year_candidates": candidates,
            "outside_corporate_window": bool(year and year not in CORPORATE_WINDOW),
            "accessed_at": datetime.now(UTC).isoformat(),
            "http_status": resp.status_code,
            "content_type": resp.headers.get("content-type"),
            "sha256": sha,
            "bytes": len(resp.content),
            "redirect_chain": [str(h.url) for h in resp.history],
            "extension": ext,
            "path": str(path.relative_to(self.root)) if not self.dry_run else None,
            "license_or_terms_status": ("public_official" if source_type == "authority"
                                        else "review_required"),
            "crawler_version": CRAWLER_VERSION,
            "parser_version": self.git,
            # Deliberately null. company_has_case must never become a document label.
            "greenwashing_label": None,
            "case_relevance_hint": artifact_role in {"ruling_page", "order", "attachment"},
        })
        log.info("stored %-22s %-11s %s", target["id"], artifact_role, path.name)
        return True

    def resolve_year(self, listing_year, title, url, resp, ext):
        """Runbook Phase 4: listing metadata > content > PDF metadata > filename."""
        cands: dict[str, int] = {}
        if listing_year:
            cands["listing"] = listing_year
        if ext == ".pdf":
            head = resp.content[:4000]
            m = YEAR_RE.findall(head.decode("latin-1", "ignore"))
            if m:
                cands["pdf_metadata"] = max(int(x) for x in m)
        elif ext in {".html", ".xml"}:
            m = YEAR_RE.findall(resp.text[:20000])
            if m:
                cands["content"] = max(int(x) for x in m)
        m = YEAR_RE.findall(f"{title} {url}")
        if m:
            cands["filename"] = max(int(x) for x in m)

        if not cands:
            return None, "review", {}
        for key in ("listing", "content", "pdf_metadata", "filename"):
            if key in cands:
                chosen = cands[key]
                break
        conflict = len({v for v in cands.values()}) > 1
        return chosen, ("review" if conflict else "resolved"), cands

    # ---------- Phase 1 ----------

    def collect_case_pack(self, target: dict) -> int:
        tid, case_url = target["id"], str(target["case_url"])
        log.info("=== %s | case pack | %s", tid, target.get("authority"))
        resp = self.fetch(case_url, stage="case_landing", target_id=tid)
        if resp is None:
            return 0

        n = int(self.store(target, case_url, resp, source_type="authority",
                           artifact_role="ruling_page", doc_family="ruling",
                           title=target.get("case_id") or tid, listing_year=target.get("case_year")))

        if "html" not in (resp.headers.get("content-type", "").lower()):
            return n

        allowed = registered_domains(target)
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            if n >= self.max_docs:
                break
            href = a["href"].strip()
            if SHARE_NOISE.search(href):
                continue
            url = canonical_url(urljoin(str(resp.url), href).split("#")[0])
            if url in self._seen_urls or is_page_asset(url) or SHARE_NOISE.search(url):
                continue
            text = " ".join(a.stripped_strings)[:300]
            ctx = " ".join((a.find_parent(["li", "p", "td", "div"]) or a).stripped_strings)[:500]
            blob = f"{text} {ctx} {url}"
            is_doc = Path(urlparse(url).path).suffix.lower() in DOC_EXTENSIONS
            if not (is_doc or looks_like_case_artifact(blob)):
                continue
            # Runbook Phase 1.4: follow authority domains automatically, queue the rest.
            if not host_ok(url, allowed):
                self.fail(tid, url, "case_external_link", "external_domain_queued", None,
                          retryable=False, next_action="manual allowlist review")
                continue
            self._seen_urls.add(url)
            r2 = self.fetch(url, stage="case_attachment", target_id=tid)
            if r2 is None:
                continue
            role = "order" if is_doc else "attachment"
            if self.store(target, url, r2, source_type="authority", artifact_role=role,
                          doc_family="order" if is_doc else "ruling",
                          title=text or url, listing_year=target.get("case_year")):
                n += 1
        return n

    # ---------- Phase 2 ----------

    def collect_disclosures(self, target: dict) -> int:
        tid = target["id"]
        allowed = registered_domains(target)
        seeds = report_seeds(target)
        if not seeds:
            # Gate S0 guarantees >=1 seed per target, so an empty list means the
            # registry was read wrongly, not that the target has no disclosures.
            self.fail(tid, "", "disclosure_preflight", "no_report_seeds_in_registry", None,
                      retryable=False,
                      next_action="check registry field names (report_urls vs report_url_N)")
            return 0
        stored = 0
        for seed in seeds:
            if stored >= self.max_docs:
                break
            log.info("=== %s | disclosure seed | %s", tid, seed[:90])
            resp = self.fetch(seed, stage="disclosure_listing", target_id=tid)
            if resp is None:
                continue
            if "html" not in resp.headers.get("content-type", "").lower():
                if self.store(target, seed, resp, source_type="corporate",
                              artifact_role="disclosure", doc_family=classify_family(seed),
                              title=Path(urlparse(seed).path).name, listing_year=None):
                    stored += 1
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            found = 0
            for a in soup.find_all("a", href=True):
                if stored >= self.max_docs:
                    break
                url = canonical_url(urljoin(str(resp.url), a["href"]).split("#")[0])
                if url in self._seen_urls or is_page_asset(url):
                    continue
                if Path(urlparse(url).path).suffix.lower() not in DOC_EXTENSIONS:
                    continue
                if not host_ok(url, allowed):
                    continue
                text = " ".join(a.stripped_strings)[:300]
                ctx = " ".join((a.find_parent(["li", "p", "td", "tr", "div"]) or a)
                               .stripped_strings)[:500]
                blob = f"{text} {ctx} {url}"
                family = classify_family(blob)
                if family is None:
                    continue
                years = [int(y) for y in YEAR_RE.findall(blob)]
                in_window = [y for y in years if y in CORPORATE_WINDOW]
                if years and not in_window:
                    continue
                self._seen_urls.add(url)
                r2 = self.fetch(url, stage="disclosure_download", target_id=tid)
                if r2 is None:
                    continue
                if self.store(target, url, r2, source_type="corporate",
                              artifact_role="disclosure", doc_family=family,
                              title=text or url,
                              listing_year=max(in_window) if in_window else None):
                    stored += 1
                    found += 1
            if found == 0:
                # Silence here is the failure mode that cost 177 PDFs before.
                self.health.d[(urlparse(seed).hostname or "unknown").lower()]["zero_result_pages"] += 1
                self.fail(tid, seed, "disclosure_listing", "zero_documents_found", 200,
                          retryable=False,
                          next_action="check JS rendering (harvest_js_listings.py) or wrong seed")
        return stored

    # ---------- run ----------

    def run(self, targets: list[dict], phase: str) -> None:
        for i, t in enumerate(targets, 1):
            log.info("---------- [%d/%d] %s ----------", i, len(targets), t["id"])
            case_n = self.collect_case_pack(t) if phase in {"all", "case"} else 0
            disc_n = self.collect_disclosures(t) if phase in {"all", "disclosure"} else 0
            self.record_coverage(t, case_n, disc_n)

    def record_coverage(self, target: dict, case_n: int, disc_n: int) -> None:
        tid = target["id"]
        docs = [d for d in self.documents if d["target_id"] == tid]
        self.coverage.append({
            "target_id": tid, "year": "case", "required_family": "authority_case_pack",
            "status": "collected" if case_n else "blocked",
            "doc_count": case_n, "source_url": target["case_url"],
            "notes": target.get("qualifier", "")[:200],
        })
        by_year = defaultdict(list)
        for d in docs:
            if d["source_type"] == "corporate":
                by_year[d["year"] if d["year_status"] == "resolved" else "review"].append(d)
        for year in CORPORATE_WINDOW:
            got = by_year.get(year, [])
            self.coverage.append({
                "target_id": tid, "year": year, "required_family": "disclosure",
                # Explicit reason, never a blank cell (Gate S2).
                "status": "collected" if got else "not_found_after_official_seed_crawl",
                "doc_count": len(got),
                "source_url": report_seeds(target)[0] if report_seeds(target) else "",
                "notes": "" if got else "no in-window document discovered from official seeds",
            })
        if by_year.get("review"):
            self.coverage.append({
                "target_id": tid, "year": "review", "required_family": "disclosure",
                "status": "year_unresolved", "doc_count": len(by_year["review"]),
                "source_url": "", "notes": "year conflict or undetected; must not enter a split",
            })

    # ---------- Phase 8 ----------

    def write_reports(self, out: Path, targets: list[dict], started: datetime) -> bool:
        rep = out / "reports"
        rep.mkdir(parents=True, exist_ok=True)
        docs = self.documents

        jsonl_write(out / "documents.jsonl", docs)

        with (rep / "coverage_matrix.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["target_id", "year", "required_family",
                                              "status", "doc_count", "source_url", "notes"])
            w.writeheader()
            w.writerows(self.coverage)

        with (rep / "failure_queue.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["target_id", "url", "stage", "error_class",
                                              "http_status", "retryable", "attempts", "next_action"])
            w.writeheader()
            w.writerows(self.failures)

        dupes = [{"sha256": h, "sources": s} for h, s in self._by_hash.items() if len(s) > 1]
        (rep / "leakage_report.json").write_text(json.dumps({
            "exact_duplicate_groups": dupes,
            "cross_split_exact": [],
            "near_duplicate_groups": [],
            "same_case_artifact_cross_split": [],
            "same_report_translation_cross_split": [],
            "note": "Splits are not assigned at collection time; cross-split checks run at build.",
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        (rep / "source_health.json").write_text(
            json.dumps(self.health.serialise(), indent=2, ensure_ascii=False), encoding="utf-8")

        attempted = {t["id"] for t in targets}
        got_case = {d["target_id"] for d in docs if d["source_type"] == "authority"}
        got_disc = {d["target_id"] for d in docs if d["source_type"] == "corporate"}
        blocked = sorted(attempted - got_case - got_disc)
        by_auth = defaultdict(int)
        by_family = defaultdict(int)
        for d in docs:
            by_auth[d["authority"]] += 1
            by_family[d["doc_family"] or "unclassified"] += 1
        unknown_year = sum(1 for d in docs if d["year_status"] != "resolved")
        fail_classes = defaultdict(int)
        for f in self.failures:
            fail_classes[f["error_class"]] += 1

        date = f"{datetime.now(UTC):%Y-%m-%d}"
        (rep / f"COLLECTION_REPORT_{date}.md").write_text(f"""# Legal-case collection report — {date}

Run `{self.run_id}` · commit `{self.git}` · crawler `{CRAWLER_VERSION}`
Started {started:%Y-%m-%d %H:%M}Z, finished {datetime.now(UTC):%Y-%m-%d %H:%M}Z.

## Targets

| | |
| --- | ---: |
| Attempted | {len(attempted)} |
| Case pack collected | {len(got_case)} |
| Disclosure collected | {len(got_disc)} |
| Fully blocked (no artifact at all) | {len(blocked)} |

{"Blocked: " + ", ".join(blocked) if blocked else "No target ended with zero artifacts."}

## Documents

| | |
| --- | ---: |
| New documents | {len(docs)} |
| Authority artifacts | {sum(1 for d in docs if d['source_type'] == 'authority')} |
| Corporate disclosures | {sum(1 for d in docs if d['source_type'] == 'corporate')} |
| Exact-duplicate hash groups | {len(dupes)} |
| Bytes | {sum(d['bytes'] for d in docs):,} |
| Unknown/conflicting year (`review`) | {unknown_year} |

By authority: {dict(by_auth) or "none"}

By document family: {dict(by_family) or "none"}

## Text layer

Not evaluated in this run — the runbook puts the OCR decision in Phase 5, after
source QA. `documents.jsonl` carries `extension` and `bytes` so the decision can
be made without re-fetching.

## Failures

{chr(10).join(f"- `{k}` × {v}" for k, v in sorted(fail_classes.items(), key=lambda x: -x[1])) or "- none"}

Full queue with next actions: `failure_queue.csv`.

## Label integrity

`greenwashing_label` is null on every record and is not derivable from this run.
`case_relevance_hint` marks authority artifacts only; it is a retrieval hint, not
a verdict. Settlement and ruling qualifiers are carried per document from the
registry.

## Next actions

1. Work `failure_queue.csv`, starting with `zero_documents_found` — those seeds
   are likely JS-rendered and need `harvest_js_listings.py`.
2. Resolve the {unknown_year} `review`-year documents before any split assignment.
3. Review externally-linked case artifacts queued as `external_domain_queued`.
4. Run text-layer analysis (Phase 5) before parsing.
""", encoding="utf-8")

        # Stop conditions from 10_REPORTING_REQUIREMENTS.md
        return bool(docs) and not blocked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=PACK / "config/legal_case_targets.yaml")
    ap.add_argument("--out", type=Path, default=REPO / "data/legal_cases")
    ap.add_argument("--target", action="append", default=[])
    ap.add_argument("--phase", choices=["all", "case", "disclosure"], default="all")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--max-docs-per-target", type=int, default=30)
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")

    targets = load_targets(args.registry)
    if args.target:
        want = {t.lower() for t in args.target}
        targets = [t for t in targets if str(t["id"]).lower() in want]
        if not targets:
            print("No target matched", file=sys.stderr)
            return 2

    log.info("%d target(s) | phase=%s | cap=%d/target | dry_run=%s",
             len(targets), args.phase, args.max_docs_per_target, args.dry_run)

    started = datetime.now(UTC)
    c = LegalCaseCrawler(args.out, dry_run=args.dry_run, delay=args.delay,
                         max_docs=args.max_docs_per_target, timeout=args.timeout)
    try:
        c.run(targets, args.phase)
    finally:
        complete = c.write_reports(args.out, targets, started)
        c.close()

    print(f"\nDocuments: {len(c.documents)} | failures: {len(c.failures)} | "
          f"reports: {args.out / 'reports'}")
    if not complete:
        print("Status: PARTIAL — see failure_queue.csv (non-zero exit per pack §10 stop conditions)")
        return 1
    print("Status: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
