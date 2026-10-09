"""List, and optionally delete, saved runs nobody will open again.

Until 2026-10-05 the test suite and the regression scripts wrote into the real
`.quantum/runs`: 721 runs, of which 521 were the four adjudicated-case packs
re-run by tests and 116 were test fixtures. The History page showed those
instead of the reviewer's own analyses.

Dry run by default. A run is KEPT when any of these holds:
  * it has a label (someone named it in the UI);
  * its id, or its first 8 characters, appears in benchmark/ or docs/ (a number
    somebody cited must stay reproducible);
  * it is the newest run of its document set (every kind of analysis keeps
    its latest example);
  * it is newer than --keep-days.

    python tools/prune_runs.py                 # what would be deleted, and how much space
    python tools/prune_runs.py --apply         # delete it
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_ID = re.compile(r"\b[0-9a-f]{8}(?:[0-9a-f]{8})?\b")


def _cited_ids() -> set[str]:
    cited: set[str] = set()
    for folder in ("benchmark", "docs"):
        for path in (ROOT / folder).rglob("*"):
            if path.suffix.lower() in {".md", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".tex"} and path.is_file():
                try:
                    cited.update(_ID.findall(path.read_text(encoding="utf-8", errors="ignore")))
                except OSError:
                    continue
    return cited


def _size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs-dir", default=os.environ.get("QUANTUM_RUNS_DIR", str(ROOT / ".quantum/runs")))
    parser.add_argument("--keep-days", type=float, default=7.0, help="keep every run newer than this")
    parser.add_argument("--apply", action="store_true", help="delete; without it nothing is touched")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    root = Path(args.runs_dir)
    if not root.is_dir():
        print(f"no runs directory at {root}")
        return 0
    cited = _cited_ids()
    now = time.time()
    runs = []
    for run in root.iterdir():
        manifest = run / "manifest.json"
        if not manifest.is_file():
            continue
        try:
            hashes = json.loads(manifest.read_text(encoding="utf-8")).get("input_hashes", {})
        except (OSError, ValueError):
            continue
        documents = tuple(sorted(key.split(":", 1)[-1] for key in hashes))
        runs.append((run, documents, manifest.stat().st_mtime))

    newest: dict[tuple, Path] = {}
    for run, documents, _mtime in sorted(runs, key=lambda r: r[2]):
        newest[documents] = run

    keep, drop = [], []
    for run, documents, mtime in runs:
        reasons = []
        if (run / "label.json").is_file():
            reasons.append("labelled")
        if run.name in cited or run.name[:8] in cited:
            reasons.append("cited")
        if newest.get(documents) == run:
            reasons.append("newest of its document set")
        if now - mtime < args.keep_days * 86400:
            reasons.append("recent")
        (keep if reasons else drop).append(run)

    freed = sum(_size(run) for run in drop)
    print(f"{len(runs)} runs in {root}: keep {len(keep)}, remove {len(drop)} ({freed / 1e6:.0f} MB)")
    if not args.apply:
        print("dry run: nothing deleted. Re-run with --apply to delete.")
        return 0
    for run in drop:
        shutil.rmtree(run, ignore_errors=True)
    print(f"deleted {len(drop)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
