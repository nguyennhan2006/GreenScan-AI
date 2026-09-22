#!/usr/bin/env python3
"""L0 harvester for the legal source registry.

Fetches the authoritative copy of each registered instrument, records full
provenance, and — the part that matters — writes back an honest
`text_acquisition` status instead of leaving a half-collected document looking
usable.

    python tools/crawl_legal_sources.py --dry-run
    python tools/crawl_legal_sources.py --id QD21-2025-QD-TTg
    python tools/crawl_legal_sources.py --all --update-registry

Vietnamese legal portals fail in specific ways this handles rather than hides:
signed PDFs are frequently scans with no text layer, and vbpl.vn returns 5xx
intermittently. Both are recorded as statuses, not swallowed as errors, because
"we have the file but cannot read it" and "the portal was down" need different
follow-up.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin

import httpx
import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
RAW = REPO / "data/legal/raw"

HEADERS = {
    "User-Agent": "GreenScanResearchBot/1.0 (academic legal-compliance research)",
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    "Accept-Language": "vi,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}
ATTACHMENT_RE = re.compile(r'href="([^"]+\.(?:pdf|doc|docx)(?:\?[^"]*)?)"', re.I)

# Below this, a PDF's "text" is the signature block and nothing else.
MIN_TEXT_CHARS_PER_PAGE = 60


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_text_health(path: Path) -> tuple[int, int]:
    """(page_count, text_chars). Decides scanned vs machine-readable."""
    import fitz

    with fitz.open(path) as doc:
        text = "\n".join(p.get_text("text") for p in doc)
        return doc.page_count, len(text.strip())


def fetch(client: httpx.Client, url: str) -> httpx.Response | None:
    try:
        r = client.get(url)
        r.raise_for_status()
        return r
    except Exception as exc:  # noqa: BLE001
        print(f"    ! {type(exc).__name__}: {str(exc)[:80]}")
        return None


def harvest(client: httpx.Client, entry: dict, out_root: Path, dry_run: bool) -> dict:
    doc_id = entry["id"]
    print(f"\n=== {doc_id} — {entry['document_number']}")
    record: dict = {"id": doc_id, "checked_at": datetime.now(UTC).isoformat(), "artifacts": []}

    original = entry.get("original_url")
    landing = entry.get("landing_url")

    # Landing page first: it is where the signed original is linked from, so
    # guessing a datafiles URL is never necessary.
    if not original and landing:
        resp = fetch(client, landing)
        if resp is not None:
            links = ATTACHMENT_RE.findall(resp.text)
            if links:
                original = urljoin(str(resp.url), links[0])
                print(f"    discovered original: {original[:88]}")
                record["discovered_original_url"] = original

    if not original:
        record["text_acquisition"] = "source_unavailable"
        record["note"] = "No attachment discoverable from the landing page."
        print("    -> source_unavailable")
        return record

    if dry_run:
        record["text_acquisition"] = entry.get("text_acquisition", "not_attempted")
        print(f"    [dry-run] would fetch {original[:88]}")
        return record

    resp = fetch(client, original)
    if resp is None:
        record["text_acquisition"] = "source_unavailable"
        record["note"] = "Authority endpoint failed at collection time."
        return record

    target_dir = out_root / doc_id
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".pdf" if "pdf" in (resp.headers.get("content-type") or "").lower() else ".html"
    path = target_dir / f"original{suffix}"
    path.write_bytes(resp.content)

    digest = sha256(resp.content)
    artifact = {
        "path": str(path.relative_to(REPO)), "sha256": digest,
        "bytes": len(resp.content), "source_url": original,
        "final_url": str(resp.url), "http_status": resp.status_code,
        "content_type": resp.headers.get("content-type"),
        "retrieved_at": datetime.now(UTC).isoformat(),
    }
    record["artifacts"].append(artifact)

    if suffix == ".pdf":
        pages, chars = pdf_text_health(path)
        artifact.update({"pages": pages, "text_chars": chars})
        if chars < pages * MIN_TEXT_CHARS_PER_PAGE:
            record["text_acquisition"] = "scanned_no_text"
            record["note"] = (
                f"Signed original is a scan: {pages} pages, {chars} characters of text. "
                "Needs OCR with the `vie` traineddata before any clause can be cited."
            )
            print(f"    -> scanned_no_text ({pages}p, {chars} chars)")
        else:
            record["text_acquisition"] = "ok"
            print(f"    -> ok ({pages}p, {chars:,} chars)")
    else:
        text_len = len(re.sub(r"<[^>]+>", " ", resp.text))
        artifact["text_chars"] = text_len
        record["text_acquisition"] = "ok" if text_len > 2000 else "source_unavailable"
        print(f"    -> {record['text_acquisition']} (html, {text_len:,} chars)")

    (target_dir / "metadata.json").write_text(
        json.dumps({**{k: entry.get(k) for k in
                       ("document_number", "title", "authority", "issued_date",
                        "effective_from", "status")},
                    **record}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--out", type=Path, default=RAW)
    ap.add_argument("--id", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--update-registry", action="store_true",
                    help="write text_acquisition back into the registry")
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args()

    raw = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
    entries = raw["documents"]
    if args.id:
        wanted = set(args.id)
        entries = [e for e in entries if e["id"] in wanted]
    elif not args.all:
        print("Pass --all or --id <ID>.", file=sys.stderr)
        return 2

    results = []
    with httpx.Client(headers=HEADERS, timeout=args.timeout, follow_redirects=True) as client:
        for entry in entries:
            results.append(harvest(client, entry, args.out, args.dry_run))

    if args.update_registry and not args.dry_run:
        by_id = {r["id"]: r for r in results}
        for entry in raw["documents"]:
            r = by_id.get(entry["id"])
            if not r:
                continue
            entry["text_acquisition"] = r["text_acquisition"]
            if r.get("note"):
                entry["text_acquisition_note"] = r["note"]
            if r.get("discovered_original_url"):
                entry["original_url"] = r["discovered_original_url"]
        args.registry.write_text(
            yaml.safe_dump(raw, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8")
        print(f"\nUpdated {args.registry}")

    counts: dict[str, int] = {}
    for r in results:
        counts[r["text_acquisition"]] = counts.get(r["text_acquisition"], 0) + 1
    print(f"\nAcquisition status: {counts}")
    usable = counts.get("ok", 0)
    print(f"{usable}/{len(results)} document(s) have usable full text.")
    if usable == 0:
        print("No instrument can support a legal finding until its text is extracted.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
