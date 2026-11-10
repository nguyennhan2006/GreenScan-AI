"""CPU cost of every step-4 candidate on the machine that has to run it: the team laptop.

The decision rule (configs/measurement_decisions.yaml, model_selection_v2.t1_claim_detection) caps the
offline model at 50 ms per sentence and 2 GB of RAM on the i7-1355U. Kaggle's CPU is not that machine,
so this measures here. Speed depends on the architecture, not on the trained weights, so each model is
built from its config with random weights (no multi-GB download) and fed real sentences, batch 1,
after a warm-up. int8 = PyTorch dynamic quantization of the Linear layers (the cheap path B7 names).

usage (any venv with torch + transformers + psutil):
  python training/latency_t1.py [--models e5-small,e5-base] [--n 100] [--threads 4]
"""
from __future__ import annotations

import argparse
import gc
import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "model_selection" / "t1_latency_laptop.json"
MODELS = {"e5-small": ("intfloat/multilingual-e5-small", "query: "),
          "e5-base": ("intfloat/multilingual-e5-base", "query: "),
          "e5-large": ("intfloat/multilingual-e5-large", "query: "),
          "bge-m3": ("BAAI/bge-m3", ""),
          "qwen3-0.6b": ("Qwen/Qwen3-0.6B", ""),
          "qwen3-1.7b": ("Qwen/Qwen3-1.7B", "")}
MAX_LEN = 160          # the kernel's truncation


def main() -> int:
    import psutil
    import torch
    from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--threads", type=int, default=4)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    rows = [json.loads(l) for l in (ROOT / "training/data/t1/train_claude.jsonl").open(encoding="utf-8")]
    texts = [r.get("text_masked") or r["text"] for r in rows][: args.n]
    proc = psutil.Process()
    result = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    result["machine"] = {"cpu": platform.processor(), "threads": args.threads, "torch": torch.__version__,
                         "ram_gb": round(psutil.virtual_memory().total / 2**30, 1)}
    result.setdefault("models", {})
    for name in args.models.split(","):
        hf, prefix = MODELS[name]
        cfg = AutoConfig.from_pretrained(hf, num_labels=4)
        tok = AutoTokenizer.from_pretrained(hf)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        cfg.pad_token_id = tok.pad_token_id
        for variant in ("fp32", "int8"):
            gc.collect()
            before = proc.memory_info().rss
            try:
                model = AutoModelForSequenceClassification.from_config(cfg).eval()
                if variant == "int8":
                    model = torch.ao.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
            except (RuntimeError, MemoryError) as exc:
                result["models"].setdefault(name, {})[variant] = {"error": str(exc)[:200]}
                print(f"{name} {variant}: {exc}")
                continue
            params = sum(p.numel() for p in model.parameters()) / 1e6
            loaded = (proc.memory_info().rss - before) / 2**30
            times, peak = [], proc.memory_info().rss
            with torch.inference_mode():
                for i, t in enumerate(texts[:5] + texts):
                    enc = tok(prefix + t, truncation=True, max_length=MAX_LEN, return_tensors="pt")
                    t0 = time.perf_counter()
                    model(**enc)
                    if i >= 5:
                        times.append(1000 * (time.perf_counter() - t0))
                    peak = max(peak, proc.memory_info().rss)
            times.sort()
            row = {"ms_mean": round(statistics.mean(times), 1), "ms_p90": round(times[int(0.9 * len(times))], 1),
                   "params_millions": round(params, 1), "ram_model_gb": round(loaded, 2),
                   "ram_peak_delta_gb": round((peak - before) / 2**30, 2), "n": len(times)}
            result["models"].setdefault(name, {})[variant] = row
            print(f"{name:11s} {variant}: {row['ms_mean']:7.1f} ms/câu (p90 {row['ms_p90']}) · "
                  f"{row['params_millions']:.0f} M tham số · RAM +{row['ram_peak_delta_gb']} GB", flush=True)
            del model
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
