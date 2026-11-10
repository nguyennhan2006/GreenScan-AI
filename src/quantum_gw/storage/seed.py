"""Install seeded demo runs into the local store (2026-11-09).

A jury opening the prototype -- deployed, or unzipped and started with GreenScan.bat --
should find finished analyses at once and be able to open every cited page.
`tools/build_demo_seed.py` copies chosen runs and the documents they cite into
`deploy/seed/`; this module copies them into the store when the API starts.

Nothing is ever overwritten: a run or a document already in the store is left alone,
so analyses and reviewer decisions made on the server survive a restart.
QUANTUM_SEED_DIR points elsewhere; set it to an empty string to disable seeding.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def seed_dir() -> Path | None:
    raw = os.environ.get("QUANTUM_SEED_DIR")
    if raw is not None and not raw.strip():
        return None
    if raw:
        path = Path(raw)
        return path if path.is_dir() else None
    # A source checkout finds deploy/seed next to src/; an installed package (pip install .,
    # as in the Docker image) does not, so the working directory is tried as well.
    for path in (REPO_ROOT / "deploy" / "seed", Path.cwd() / "deploy" / "seed"):
        if path.is_dir():
            return path
    return None


def install(runs_dir: str | Path, documents_dir: str | Path | None = None) -> dict:
    """Copy missing seeded runs and documents into the store; return what was copied."""
    source = seed_dir()
    copied = {"runs": 0, "documents": 0}
    if source is None:
        return copied
    runs_root = Path(runs_dir)
    docs_root = Path(documents_dir or os.environ.get("QUANTUM_DOCUMENTS_DIR", ".quantum/documents"))
    if (source / "runs").is_dir():
        runs_root.mkdir(parents=True, exist_ok=True)
        for run in sorted((source / "runs").iterdir()):
            target = runs_root / run.name
            if run.is_dir() and not target.exists():
                shutil.copytree(run, target)
                copied["runs"] += 1
    index = source / "documents" / "index.jsonl"
    if index.is_file():
        (docs_root / "blobs").mkdir(parents=True, exist_ok=True)
        local_index = docs_root / "index.jsonl"
        have = set()
        if local_index.is_file():
            have = {
                json.loads(line)["doc_id"]
                for line in local_index.read_text(encoding="utf-8").split("\n") if line.strip()
            }
        new_rows = []
        for line in index.read_text(encoding="utf-8").split("\n"):
            if not line.strip():
                continue
            row = json.loads(line)
            blob = source / "documents" / row["path"]
            target = docs_root / row["path"]
            if blob.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(blob, target)
            if row["doc_id"] not in have and target.is_file():
                new_rows.append({**row, "path": str(target.resolve())})
        if new_rows:
            with local_index.open("a", encoding="utf-8") as out:
                for row in new_rows:
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
            copied["documents"] = len(new_rows)
    return copied
