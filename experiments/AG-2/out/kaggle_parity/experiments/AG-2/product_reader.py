"""Product reader on a GS-Bench file (registration agentic_ag2_product): parity with a Kaggle run + reading time (CPU).

    .venv/Scripts/python.exe -I experiments/AG-2/product_reader.py BENCH OUT_DIR [--model M] [--ref KAGGLE_CASES]

Reads every claim and evidence text through quantum_gw.verification.ir_reader (Ollama at localhost:11434), writes
OUT_DIR/cases.jsonl (id, label, why; the format of ag1_worker / policies.py) and OUT_DIR/summary.json (seconds per
model call, label agreement with --ref per case). Replies are cached in OUT_DIR, so a stopped run resumes.
"""
from __future__ import annotations

import json, sys, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from quantum_gw.providers.ollama import OllamaProvider  # noqa: E402
from quantum_gw.verification.ir_reader import IRReader  # noqa: E402


def main() -> None:
    args = sys.argv[1:]
    opt = {args[i]: args[i + 1] for i in range(len(args)) if args[i].startswith("--")}
    bench, out = Path(args[0]), Path(args[1])
    model = opt.get("--model", "qwen3:4b-instruct-2507-q4_K_M")
    out.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(line) for line in bench.open(encoding="utf-8")]
    reader = IRReader(OllamaProvider(model=model, timeout=600), out)
    texts = list(dict.fromkeys(t for c in cases for t in (c["claim"], c["evidence"])))
    print(f"[reader] {len(cases)} cases, {len(texts)} unique texts, model {model}", flush=True)
    t0, spent = time.time(), []
    for i, t in enumerate(texts, 1):
        t1, before = time.time(), reader.calls
        reader.raw(t)
        if reader.calls > before:
            spent.append(time.time() - t1)
        if i % 10 == 0 or i == len(texts):
            print(f"[reader] {i}/{len(texts)} texts, {len(spent)} calls, {sum(spent):.0f} s", flush=True)
    labels = {}
    with (out / "cases.jsonl").open("w", encoding="utf-8") as fh:
        for c in cases:
            label, why = reader.label(c["claim"], c["evidence"])
            labels[c["id"]] = label
            fh.write(json.dumps({"id": c["id"], "label": label, "why": why}, ensure_ascii=False) + "\n")
    summary = {"model": model, "cases": len(cases), "texts": len(texts), "calls": len(spent),
               "s_per_call": round(sum(spent) / len(spent), 1) if spent else None, "wall_s": round(time.time() - t0),
               "labels": dict(Counter(labels.values()))}
    if "--ref" in opt:
        ref = {r["id"]: r["label"] for r in map(json.loads, Path(opt["--ref"]).open(encoding="utf-8"))}
        both = [k for k in labels if k in ref]
        summary["ref"] = opt["--ref"]
        summary["agreement"] = round(sum(labels[k] == ref[k] for k in both) / len(both), 3)
        summary["confusion_ref_to_local"] = dict(Counter(f"{ref[k]}->{labels[k]}" for k in both if labels[k] != ref[k]))
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[reader] SUMMARY {json.dumps(summary, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()
