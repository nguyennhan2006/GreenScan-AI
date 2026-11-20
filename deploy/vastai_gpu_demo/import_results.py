"""Bring the rented machine's results back to the laptop.

    C:/Python314/python.exe deploy/vastai_gpu_demo/import_results.py <path>/gs_results.tar.gz

1. Unpacks into <AI quantum>/vast_bundle/results_<time>/ (logs and the machine's own runs, kept for the record).
2. Adds the cached model answers to the repo's .quantum/llm_cache/*.jsonl. Only keys the laptop does not
   have yet are added, so the answers behind the existing demo sessions stay as they are. The laptop's
   cache is copied to .quantum/llm_cache_backup_<time>/ first.
Then run the Hòa Phát case on the laptop in `local` mode: every answer comes from the cache, and the session
lands in the demo store like any other.
"""
from __future__ import annotations

import json
import shutil
import sys
import tarfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO.parents[2]
CACHE = REPO / ".quantum" / "llm_cache"


def main() -> None:
    archive = Path(sys.argv[1])
    stamp = time.strftime("%Y-%m-%d_%H%M")
    target = WRAPPER / "vast_bundle" / f"results_{stamp}"
    target.mkdir(parents=True)
    with tarfile.open(archive) as tar:
        tar.extractall(target, filter="data")
    shutil.copytree(CACHE, CACHE.parent / f"llm_cache_backup_{stamp}")
    for incoming in sorted((target / ".quantum" / "llm_cache").glob("*.jsonl")):
        mine = CACHE / incoming.name
        have = set()
        if mine.is_file():
            for line in mine.read_text(encoding="utf-8").splitlines():
                try:
                    have.add(json.loads(line)["key"])
                except (json.JSONDecodeError, KeyError):
                    continue
        added = []
        for line in incoming.read_text(encoding="utf-8").splitlines():
            try:
                key = json.loads(line)["key"]
            except (json.JSONDecodeError, KeyError):
                continue
            if key not in have:
                have.add(key)
                added.append(line)
        if added:
            with mine.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(added) + "\n")
        print(f"{incoming.name}: +{len(added)} câu trả lời mới (máy thuê có {len(incoming.read_text(encoding='utf-8').splitlines())})")
    print(f"\nĐã giải nén vào {target}")
    print("Bước tiếp (mở Ollama trên laptop trước), ở thư mục repo:")
    print('  .venv/Scripts/python.exe tools/thuyet_minh/run_demo_models.py "' + str(WRAPPER / "demo_store_ban_ket") + '" local B')


if __name__ == "__main__":
    main()
