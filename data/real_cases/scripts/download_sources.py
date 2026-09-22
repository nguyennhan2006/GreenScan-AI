#!/usr/bin/env python3
"""Download original public source documents listed in source_registry.csv.

Usage:
  python scripts/download_sources.py --dry-run
  python scripts/download_sources.py --case-id KDP-2024
  python scripts/download_sources.py --all

The script does not bypass authentication or access controls. It records URL,
HTTP metadata and SHA-256. Review each source's copyright and terms before
redistributing original documents.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sources/source_registry.csv"
OUT = ROOT / "sources/originals"

DEFAULT_USER_AGENT = os.environ.get(
    "GREENSCAN_CRAWLER_UA",
    "AI-Quantum-Research-Pilot/0.1 (document-archiving; contact project owner)",
)

# sec.gov's WAF returns 403 when `Accept` is absent. urllib sends no `Accept`
# header by default, so the request must set one explicitly -- this is the only
# reason every SEC source failed before. Declaring gzip also honours SEC's
# fair-access guidance, which means responses have to be decoded manually.
BASE_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
}


def _decode(data: bytes, encoding: str) -> bytes:
    encoding = (encoding or "").lower().strip()
    if encoding == "gzip":
        return gzip.decompress(data)
    if encoding == "deflate":
        return zlib.decompress(data, -zlib.MAX_WBITS)
    return data

ALLOWED_HOSTS = {
    "www.sec.gov",
    "uitspraken.rechtspraak.nl",
    "data.rechtspraak.nl",
    "img.static-kl.com",
    "download.dws.com",
    "file.hoaphat.com.vn",
    "www.baoviet.com.vn",
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", action="append", default=[])
    ap.add_argument("--source-id", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    with REGISTRY.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    selected = []
    for row in rows:
        if not row["url"]:
            continue
        if args.source_id and row["source_id"] not in args.source_id:
            continue
        if args.case_id and row["case_id"] not in args.case_id:
            continue
        if not (args.all or args.source_id or args.case_id):
            continue
        selected.append(row)

    if not selected:
        print("No sources selected. Use --all, --case-id or --source-id.")
        return 0

    manifest = []
    for row in selected:
        host = urlparse(row["url"]).hostname or ""
        if host not in ALLOWED_HOSTS:
            raise SystemExit(f"Host not allowed: {host}")
        target = OUT / row["expected_filename"]
        print(f"{row['source_id']}: {row['url']} -> {target}")
        if args.dry_run:
            continue

        req = Request(row["url"], headers=dict(BASE_HEADERS))
        try:
            with urlopen(req, timeout=90) as resp:
                data = _decode(resp.read(), resp.headers.get("Content-Encoding", ""))
                content_type = resp.headers.get("Content-Type", "")
                final_url = resp.geturl()
                status = getattr(resp, "status", 200)
            target.write_bytes(data)
            rec = {
                "source_id": row["source_id"],
                "case_id": row["case_id"],
                "status": "downloaded",
                "http_status": status,
                "url": row["url"],
                "final_url": final_url,
                "path": str(target.relative_to(ROOT)),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "content_type": content_type,
                "retrieved_at": datetime.now(UTC).isoformat(),
                "user_agent": BASE_HEADERS["User-Agent"],
            }
        except Exception as exc:
            rec = {
                "source_id": row["source_id"],
                "case_id": row["case_id"],
                "status": "error",
                "url": row["url"],
                "error": repr(exc),
                "retrieved_at": datetime.now(UTC).isoformat(),
            }
            print(f"ERROR: {exc}")
        manifest.append(rec)
        time.sleep(max(args.sleep, 0))

    # Merge instead of overwrite: re-running a single --source-id must not wipe
    # the record of everything fetched in previous runs.
    manifest_path = OUT / "download_manifest.json"
    merged: dict[str, dict] = {}
    if manifest_path.is_file():
        for rec in json.loads(manifest_path.read_text(encoding="utf-8")):
            merged[rec["source_id"]] = rec
    for rec in manifest:
        merged[rec["source_id"]] = rec

    manifest_path.write_text(
        json.dumps(list(merged.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUT / 'download_manifest.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
