"""Build the Kaggle dataset and kernel folders for training/kaggle/t1_kaggle.py.

  training/data/kaggle/data/     train.jsonl (Claude training labels, T1 frame)
                                 compare.jsonl (lot-1 sentences, Claude labels, set = audit | hpg)
                                 dataset-metadata.json (private dataset <user>/greenscan-t1-data)
  training/data/kaggle/kernel/   t1_kaggle.py + kernel-metadata.json (private, GPU, internet)

Only public-report text and labels leave the machine; no credentials are written.
Then, with KAGGLE_USERNAME / KAGGLE_API_TOKEN in the environment:
  kaggle datasets create -p training/data/kaggle/data          (first time; later: datasets version -m "...")
  kaggle kernels push -p training/data/kaggle/kernel --accelerator NvidiaTeslaT4
  kaggle kernels status <user>/greenscan-t1-train
  kaggle kernels output <user>/greenscan-t1-train -p training/runs/kaggle_t1

usage: python training/kaggle/prepare.py --user <kaggle username>
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "training"))

import t1_data  # noqa: E402

OUT = ROOT / "training/data/kaggle"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", required=True)
    args = ap.parse_args()

    data, kernel = OUT / "data", OUT / "kernel"
    data.mkdir(parents=True, exist_ok=True)
    kernel.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "training/data/t1/train_claude.jsonl", data / "train.jsonl")
    compare = []
    for line in (ROOT / "training/data/gold_t1/ai/claude_compare.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        if r["label"] == "UNSURE":
            continue
        compare.append({**t1_data._base(r), "label": r["label"], "set": r["set"].removeprefix("compare_")})
    (data / "compare.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in compare),
                                        encoding="utf-8")
    (data / "dataset-metadata.json").write_text(json.dumps({
        "title": "greenscan-t1-data", "id": f"{args.user}/greenscan-t1-data",
        "licenses": [{"name": "other"}]}, indent=1), encoding="utf-8")
    shutil.copy(ROOT / "training/kaggle/t1_kaggle.py", kernel / "t1_kaggle.py")
    (kernel / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{args.user}/greenscan-t1-train", "title": "greenscan-t1-train", "code_file": "t1_kaggle.py",
        "language": "python", "kernel_type": "script", "is_private": True, "enable_gpu": True,
        "enable_tpu": False, "enable_internet": True, "dataset_sources": [f"{args.user}/greenscan-t1-data"],
        "competition_sources": [], "kernel_sources": [], "model_sources": []}, indent=1), encoding="utf-8")
    n_train = sum(1 for _ in (data / "train.jsonl").open(encoding="utf-8"))
    print(f"data -> {data.relative_to(ROOT)}: train {n_train}, compare {len(compare)} "
          f"({sum(r['set'] == 'hpg' for r in compare)} hpg)")
    print(f"kernel -> {kernel.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
