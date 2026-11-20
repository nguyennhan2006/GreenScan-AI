"""Score a chat model (and optionally its stance LoRA) on the registered S5 set: 391 GS-Eval pairs, gold S / C / O.

    python -u eval_stance_llm.py --base Qwen/Qwen3-14B --adapter out/stance-14b/adapter --field msgs_large --tag q3-14b
    python -u eval_stance_llm.py --base openai/gpt-oss-120b --field msgs_large --tag gpt-oss-120b

Answer {"relation": SUPPORTS|PARTIAL|CONTRADICTS|CONTEXT, "reason"}; PARTIAL counts as S (as train_stance_enc.py).
An unparsed answer counts as O (the product falls back to the rules). Metrics as llm_stages_v1: macro-F1 over S and O
with a company-cluster interval, false C per 100, C found. Writes out/stance_eval/<tag>.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, cell, has, jl, log, out_dir, save_json, wjl  # noqa: E402
from train_stance_enc import TO_SCO, sco_scores  # noqa: E402


def relation(text: str) -> str | None:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)
    m = re.search(r"\{.*?\}", text, flags=re.S)
    if m:
        try:
            r = str(json.loads(m.group(0)).get("relation", "")).upper()
            if r in TO_SCO:
                return r
        except json.JSONDecodeError:
            pass
    m = re.search(r"SUPPORTS|PARTIAL|CONTRADICTS|CONTEXT", text or "")
    return m.group(0) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--adapter", default="")
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--field", default="msgs_large")
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-len", type=int, default=6144)
    ap.add_argument("--data", default="s5_pairs.jsonl", help="or stance_sft.jsonl: the 821 silver pairs (gold = target)")
    args = ap.parse_args()
    cell("stance llm load")
    data = jl(args.data)
    if data and "target" in data[0]:   # silver pairs: gold relation from the SFT target, rules from the candidates file
        rules = {c["id"]: c["relation"] for c in jl("pairs_cand_rules.jsonl")} if has("pairs_cand_rules.jsonl") else {}
        for d in data:
            d["gold"] = TO_SCO[json.loads(d["target"])["relation"]]
            d["rules"] = rules.get(d["id"])
            d.setdefault(args.field, d["messages"])
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(args.base)
    prompts = [tok.apply_chat_template(d[args.field], tokenize=False, add_generation_prompt=True, enable_thinking=False)
               for d in data]
    kw = dict(enable_lora=True, max_lora_rank=64) if args.adapter else {}
    llm = LLM(model=args.base, tensor_parallel_size=args.tp, max_model_len=args.max_len, gpu_memory_utilization=0.9,
              seed=0, **kw)
    systems = [("base", None)]
    if args.adapter:
        from vllm.lora.request import LoRARequest
        systems.append(("lora", LoRARequest("stance", 1, args.adapter)))
    tag = args.tag or Path(args.base).name
    od = out_dir("stance_eval")
    gold, comp = [d["gold"] for d in data], [d["company"] for d in data]
    res = {"base": args.base, "adapter": args.adapter, "data": args.data, "systems": {},
           "rules": sco_scores(gold, [TO_SCO.get(d.get("rules") or "CONTEXT", "O") for d in data], comp)}
    for name, lora in systems:
        cell(f"stance llm generate {name}")
        t = Timer()
        outs = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=200), lora_request=lora)
        rel = [relation(o.outputs[0].text) for o in outs]
        pred = [TO_SCO[r] if r else "O" for r in rel]
        s = sco_scores(gold, pred, comp)
        s.update(seconds=t(), unparsed=sum(r is None for r in rel))
        res["systems"][name] = s
        wjl(od / f"{tag}_{name}_answers.jsonl", [{"id": d["id"], "text": o.outputs[0].text, "relation": r}
                                                  for d, o, r in zip(data, outs, rel)])
        log(f"[stance-llm] {tag} {name}: macro-F1(S,O) {s['macro_f1_SO']} {s['ci95']} false C {s['false_C']} "
            f"unparsed {s['unparsed']}")
    save_json(od / f"{tag}.json", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
