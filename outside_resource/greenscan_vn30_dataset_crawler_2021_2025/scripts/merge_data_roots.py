#!/usr/bin/env python3
"""Merge a secondary crawl data-root into a primary one.

The static crawler and ``harvest_js_listings.py`` both write a ``documents``
table plus a content-addressed ``objects/`` tree. Running them against the same
root serialises on SQLite's single writer, so long runs are done side by side
into separate roots and merged afterwards.

    python scripts/merge_data_roots.py --primary data/raw --secondary data/raw_js

Objects are content-addressed, so copying is idempotent: identical bytes land on
the identical path. Rows are keyed by ``url``; when both roots hold the same URL
the one that actually has bytes wins, and a tie goes to the primary.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

STORED = {"downloaded", "duplicate"}


def rank(row: sqlite3.Row) -> tuple[int, int]:
    """Higher is better: real bytes beat a bare discovery record."""
    return (1 if row["status"] in STORED else 0, row["content_length"] or 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", type=Path, required=True)
    ap.add_argument("--secondary", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdb, sdb = args.primary / "metadata.sqlite3", args.secondary / "metadata.sqlite3"
    for path in (pdb, sdb):
        if not path.is_file():
            print(f"missing database: {path}", file=sys.stderr)
            return 2

    primary = sqlite3.connect(pdb)
    primary.row_factory = sqlite3.Row
    secondary = sqlite3.connect(f"file:{sdb}?mode=ro", uri=True)
    secondary.row_factory = sqlite3.Row

    existing = {r["url"]: r for r in primary.execute("SELECT * FROM documents")}
    columns = [d[0] for d in primary.execute("SELECT * FROM documents LIMIT 0").description if d[0] != "id"]

    inserted = replaced = skipped = copied = 0
    for row in secondary.execute("SELECT * FROM documents"):
        current = existing.get(row["url"])
        if current is not None and rank(current) >= rank(row):
            skipped += 1
            continue

        # Move the bytes first: a row pointing at a missing object is worse than
        # no row at all, because dataset build silently drops it.
        values = dict(row)
        src = Path(values["object_path"]) if values.get("object_path") else None
        if src and src.is_file():
            try:
                rel = src.relative_to(args.secondary)
            except ValueError:
                rel = Path("objects") / "sha256" / src.parent.name / src.name
            dst = args.primary / rel
            if not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    shutil.copy2(src, dst)
                    copied += 1
            values["object_path"] = str(dst)

        if args.dry_run:
            inserted += current is None
            replaced += current is not None
            continue

        payload = {c: values.get(c) for c in columns}
        placeholders = ",".join(":" + c for c in columns)
        if current is not None:
            primary.execute("DELETE FROM documents WHERE url=?", (row["url"],))
            replaced += 1
        else:
            inserted += 1
        primary.execute(f"INSERT INTO documents({','.join(columns)}) VALUES({placeholders})", payload)

    if not args.dry_run:
        primary.commit()

    manifests = args.primary / "manifests"
    if not args.dry_run:
        manifests.mkdir(parents=True, exist_ok=True)
        for m in (args.secondary / "manifests").glob("*.jsonl"):
            target = manifests / m.name
            if not target.exists():
                shutil.copy2(m, target)

    primary.close()
    secondary.close()
    print(f"inserted={inserted} replaced={replaced} skipped={skipped} objects_copied={copied}"
          + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
