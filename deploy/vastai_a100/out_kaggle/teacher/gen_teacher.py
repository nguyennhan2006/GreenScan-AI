"""Teacher explanations for distillation: a large model writes the explanation of each stored verdict.

    python -u gen_teacher.py --model Qwen/Qwen3-32B-AWQ --tp 2 --input explain_train.jsonl --field msgs_large \
        --out out/teacher/explain_teacher.jsonl [--limit N]

Greedy decoding, thinking off. Keeps an answer only when it parses as {"explanation", "next_action"}, is 12-140 words,
and adds no number absent from the input (guards.new_numbers, the product's own check). Kept rows carry the student
prompt (msgs_small) and the teacher answer as the SFT target.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, cell, jl, log, save_json, wjl  # noqa: E402
from guards import new_numbers  # noqa: E402


def parse(text: str) -> dict | None:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or not str(d.get("explanation") or "").strip():
        return None
    return {"explanation": str(d["explanation"]).strip(), "next_action": str(d.get("next_action") or "").strip()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--input", default="explain_train.jsonl")
    ap.add_argument("--field", default="msgs_large")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-len", type=int, default=6144)
    ap.add_argument("--max-tokens", type=int, default=450)
    args = ap.parse_args()

    cell("teacher load")
    rows = jl(args.input)[: args.limit or None]
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(args.model)
    prompts = [tok.apply_chat_template(r[args.field], tokenize=False, add_generation_prompt=True, enable_thinking=False)
               for r in rows]
    t = Timer()
    llm = LLM(model=args.model, tensor_parallel_size=args.tp, max_model_len=args.max_len, gpu_memory_utilization=0.92,
              enforce_eager=False, seed=0)
    log(f"[teacher] loaded {args.model} in {t()} s; {len(rows)} prompts")

    cell("teacher generate")
    t = Timer()
    outs = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=args.max_tokens))
    secs = t()
    why = Counter()
    kept, raw = [], []
    for r, o in zip(rows, outs):
        text = o.outputs[0].text
        d = parse(text)
        user = r[args.field][-1]["content"]
        reason = "kept"
        if d is None:
            reason = "unparsed"
        else:
            words = len((d["explanation"] + " " + d["next_action"]).split())
            if not 12 <= words <= 140:
                reason = "length"
            elif new_numbers(d["explanation"] + " " + d["next_action"], user):
                reason = "new_number"
        why[reason] += 1
        raw.append({"id": r["id"], "reason": reason, "text": text})
        if reason == "kept":
            kept.append({"id": r["id"], "company": r.get("company"), "verdict": r.get("verdict"),
                         "messages": r["msgs_small"], "target": json.dumps(d, ensure_ascii=False)})
    out = Path(args.out)
    wjl(out, kept)
    wjl(out.with_name(out.stem + "_raw.jsonl"), raw)
    ntok = sum(len(o.outputs[0].token_ids) for o in outs)
    save_json(out.with_name(out.stem + "_summary.json"),
              {"model": args.model, "n": len(rows), "reasons": dict(why), "seconds": secs,
               "output_tokens": ntok, "tokens_per_second": round(ntok / max(secs, 1e-6), 1)})
    log(f"[teacher] {dict(why)} in {secs} s, {ntok} output tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
