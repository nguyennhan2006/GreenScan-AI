"""Score explanation models on the registered S6 set (142 items): must-mention proxy, new numbers, length, speed.

    python -u eval_explain.py --base Qwen/Qwen3-4B-Instruct-2507 --adapter out/explain-4b/adapter --field msgs_small
    python -u eval_explain.py --base Qwen/Qwen3-32B-AWQ --tp 2 --field msgs_large --tag teacher-32b

Systems scored in one vLLM process: the base model, and the base + LoRA adapter when --adapter is given. The scoring
is benchmark/llm_stages/score.py score_s6 (same covered() rule, same new_numbers guard, company-cluster bootstrap).
Writes out/explain_eval/<tag>.json and the raw answers.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, boot_ci, cell, jl, log, out_dir, save_json, wjl  # noqa: E402
from gen_teacher import parse  # noqa: E402
from guards import fold, new_numbers  # noqa: E402


def covered(phrase, text):
    words = [w for w in fold(phrase).split() if len(w) > 2]
    return bool(words) and sum(w in fold(text) for w in words) / len(words) >= 0.6


def score(data, answers):
    rows, bad, empty, unparsed = [], 0, 0, 0
    for d in data:
        p = answers.get(d["id"])
        unparsed += p is None
        text = " ".join(str((p or {}).get(k, "")) for k in ("explanation", "next_action")).strip()
        empty += not text
        nn = new_numbers(text, d["claim"], d["rationale"],
                         *[f"{e.get('source_name')} {e.get('page')} {e.get('text') or ''}" for e in d["evidence"]])
        bad += bool(nn)
        mm = d["must_mention"]
        rows.append({"company": d["company"], "cov": (sum(covered(m, text) for m in mm) / len(mm)) if mm else None,
                     "words": len(text.split()), "new_number": bool(nn)})

    def cov(rs):
        v = [r["cov"] for r in rs if r["cov"] is not None]
        return sum(v) / len(v) if v else 0.0

    return {"n": len(rows), "must_mention_proxy": round(cov(rows), 3),
            "ci95": boot_ci(rows, [r["company"] for r in rows], cov), "with_new_number": bad, "empty": empty,
            "unparsed": unparsed, "words_mean": round(sum(r["words"] for r in rows) / len(rows), 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--adapter", default="")
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--field", default="msgs_small")
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-len", type=int, default=6144)
    args = ap.parse_args()
    cell("explain eval load")
    data = jl("s6_explain.jsonl")
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(args.base)
    prompts = [tok.apply_chat_template(d[args.field], tokenize=False, add_generation_prompt=True, enable_thinking=False)
               for d in data]
    kw = dict(enable_lora=True, max_lora_rank=64) if args.adapter else {}
    llm = LLM(model=args.base, tensor_parallel_size=args.tp, max_model_len=args.max_len, gpu_memory_utilization=0.9,
              seed=0, **kw)
    sp = SamplingParams(temperature=0.0, max_tokens=400)
    systems = [("base", None)]
    if args.adapter:
        from vllm.lora.request import LoRARequest
        systems.append(("lora", LoRARequest("explain", 1, args.adapter)))
    od = out_dir("explain_eval")
    tag = args.tag or Path(args.base).name
    result = {"base": args.base, "adapter": args.adapter, "field": args.field, "systems": {}}
    for name, lora in systems:
        cell(f"explain eval generate {name}")
        t = Timer()
        outs = llm.generate(prompts, sp, lora_request=lora)
        secs = t()
        answers = {d["id"]: parse(o.outputs[0].text) for d, o in zip(data, outs)}
        wjl(od / f"{tag}_{name}_answers.jsonl",
            [{"id": d["id"], "text": o.outputs[0].text, "parsed": answers[d["id"]]} for d, o in zip(data, outs)])
        s = score(data, answers)
        s["seconds"] = secs
        s["seconds_per_item_batched"] = round(secs / len(data), 3)
        result["systems"][name] = s
        log(f"[explain] {tag} {name}: {s}")
    save_json(od / f"{tag}.json", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
