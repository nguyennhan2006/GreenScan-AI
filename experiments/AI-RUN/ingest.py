"""Bring the Kaggle AI run home: download, unpack, copy both HPG runs into .quantum/runs with a UI label, print the summary.

    python tools/kaggle/kapi.py output diuquinh/gs-ai-run-hpg --dest experiments/AI-RUN/kaggle_out
    .venv/Scripts/python.exe -I experiments/AI-RUN/ingest.py [experiments/AI-RUN/kaggle_out]

The LLM cache comes back too (llm_cache/): pointing QUANTUM_LLM_CACHE_DIR at it lets the laptop re-open or re-run the AI
analysis of HPG without a model, because every answer the T4 produced is already cached.
"""
import json
import shutil
import sys
import tarfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "experiments/AI-RUN/kaggle_out"
tgz = next(src.rglob("runs.tgz"))
summary = json.loads(next(src.rglob("summary.json")).read_text(encoding="utf-8"))
unpacked = src / "unpacked"
with tarfile.open(tgz) as t:
    t.extractall(unpacked, filter="data")
labels = {
    "rules": "Hòa Phát BCPTBV 2025 + BCTN 2024 — chỉ luật (Kaggle, cùng máy với bản AI)",
    "ai": f"Hòa Phát BCPTBV 2025 + BCTN 2024 — CÓ AI ({summary['model']}, Kaggle {(summary.get('gpu') or 'GPU').splitlines()[0]})",
}
dest_root = ROOT / ".quantum/runs"
for arm, run_id in summary["runs"].items():
    dst = dest_root / run_id
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(unpacked / "runs" / run_id, dst)
    (dst / "label.json").write_text(json.dumps({"label": labels[arm]}, ensure_ascii=False), encoding="utf-8")
    print(f"{arm}: .quantum/runs/{run_id}  [{labels[arm]}]")
cache = ROOT / ".quantum/llm_cache_kaggle_ai_run"
if (unpacked / "llm_cache").exists():
    shutil.copytree(unpacked / "llm_cache", cache, dirs_exist_ok=True)
    print("llm cache ->", cache.relative_to(ROOT))
print(json.dumps({k: summary[k] for k in ("seconds", "ratio_ai_over_rules", "risk_scores_changed")}, ensure_ascii=False))
print("statuses changed:", len(summary["statuses_changed"]))
for arm in ("rules", "ai"):
    f = summary[arm]
    print(arm, "| relation_method", f["relation_method"], "| IR read", f["ir_passages_read"], f["ir_vs_rules"],
          "| explanations", f["explanations_kept"], "| queue", f["queue"])
