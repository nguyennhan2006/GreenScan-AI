"""prompt_router_v1 planner: score Qwen3-0.6B (base and + LoRA) on router_test with router_metrics.score.

    python -u eval_router.py --base Qwen/Qwen3-0.6B --adapter out/router-0p6b/adapter

Greedy, thinking off, JSON parsed by code (an unparsed answer counts as a refusal). Writes out/router_eval/<tag>.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import cell, jl, log, out_dir, save_json, wjl  # noqa: E402
from router_metrics import score  # noqa: E402


def parse(text: str) -> dict | None:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or not isinstance(d.get("in_scope"), bool):
        return None
    d["tasks"] = [t for t in d.get("tasks") or [] if isinstance(t, str)]
    d["slots"] = d.get("slots") if isinstance(d.get("slots"), dict) else {}
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--adapter", default="")
    ap.add_argument("--tag", default="router-0p6b")
    a = ap.parse_args()
    cell("router eval load")
    te = jl("router_test.jsonl")
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(a.base)
    prompts = [tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
               for r in te]
    kw = dict(enable_lora=True, max_lora_rank=64) if a.adapter else {}
    llm = LLM(model=a.base, max_model_len=2048, gpu_memory_utilization=0.85, seed=0, **kw)
    systems = [("base", None)]
    if a.adapter:
        from vllm.lora.request import LoRARequest
        systems.append(("lora", LoRARequest("router", 1, a.adapter)))
    od, res = out_dir("router_eval"), {"base": a.base, "adapter": a.adapter, "systems": {}}
    for name, lora in systems:
        cell(f"router eval generate {name}")
        t0 = time.time()
        outs = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=300), lora_request=lora)
        preds = [parse(o.outputs[0].text) for o in outs]
        s = score(te, preds)
        s["seconds"] = round(time.time() - t0, 1)
        res["systems"][name] = s
        wjl(od / f"{a.tag}_{name}_answers.jsonl", [{"id": r["id"], "text": o.outputs[0].text} for r, o in zip(te, outs)])
        log(f"[router] {name}: OOS recall {s['oos_recall']} {s['oos_recall_ci95']} · false refusal {s['false_refusal']} · "
            f"task macro-F1 {s['task_macro_f1']} · claim EM {s['slot_claim_exact']} · unparsed {s['unparsed']}")
    save_json(od / f"{a.tag}.json", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
