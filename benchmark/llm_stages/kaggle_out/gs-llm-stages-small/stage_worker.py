"""llm_stages_v1 worker: one local LLM answers the S2 / S5 / S6 sets with the stage prompts of its family.

    STAGES=s5,s2,s6 python -u multirun.py jobs_small.json stage_worker.py

Runs inside a Kaggle notebook built by tools/kaggle/build_nb.py with llm.py and multirun.py of experiments/AG-1 and
src/quantum_gw/assist/prompts.py (copied next to this file). Greedy, thinking off. Inputs: s5_pairs.jsonl,
s2_attrs.jsonl, s6_explain.jsonl (benchmark/llm_stages/build_sets.py). Output: out/<tag>__<stage>.jsonl, one row per
set row: {id, raw, parsed, prompt_version}; out/<tag>_summary.json. Env: LIMIT=n (smoke), STAGES.
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

from prompts import attr_messages, explain_messages, stance_messages, version

STAGE = {
    "s5": ("s5_pairs.jsonl", "stance", 220, lambda m, r: stance_messages(m, r["claim"], r["evidence"][:1500])),
    "s2": ("s2_attrs.jsonl", "attributes", 220, lambda m, r: attr_messages(m, r["sentence"])),
    "s6": ("s6_explain.jsonl", "explain", 420,
           lambda m, r: explain_messages(m, r["claim"], r["verdict"], r["rationale"], r["evidence"], r["missing"])),
}


def parse(text):
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                esc = (ch == "\\" and not esc)
                if ch == '"' and not esc:
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            depth += {"{": 1, "}": -1}.get(ch, 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    break
        start = text.find("{", start + 1)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    job = json.loads(ap.parse_args().job)
    tag, repo = job["tag"], job["repo"]
    stages = [s for s in os.environ.get("STAGES", "s5,s2,s6").split(",") if s]
    from llm import LLM
    t0 = time.time()
    m = LLM(repo, max_len=job.get("max_len", 4096), tp=job.get("tp", 1), **job.get("kw", {}))
    summary = {"tag": tag, "repo": repo, "load_s": round(time.time() - t0), "stages": {}}
    Path("out").mkdir(exist_ok=True)
    for st in stages:
        path, name, max_tokens, build = STAGE[st]
        rows = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
        if os.environ.get("LIMIT"):
            rows = rows[: int(os.environ["LIMIT"])]
        pv = version(name, repo)
        print(f"[{tag}] [cell-progress] {st}: {len(rows)} rows, prompt {pv}", flush=True)
        prompts = [build(repo, r) for r in rows]
        t1, raw = time.time(), []
        for i in range(0, len(prompts), 64):
            raw += m.gen(prompts[i:i + 64], max_tokens=max_tokens)
            print(f"[{tag}] {st} generated {len(raw)}/{len(prompts)} ({time.time() - t1:.0f}s)", flush=True)
        bad = 0
        with open(f"out/{tag}__{st}.jsonl", "w", encoding="utf-8") as fh:
            for r, text in zip(rows, raw):
                obj = parse(text)
                bad += obj is None
                fh.write(json.dumps({"id": r["id"], "raw": text, "parsed": obj, "prompt_version": pv},
                                    ensure_ascii=False) + "\n")
        summary["stages"][st] = {"rows": len(rows), "unparsed": bad, "gen_s": round(time.time() - t1), "prompt": pv}
    summary.update(ntok_in=getattr(m, "ntok_in", None), ntok_out=getattr(m, "ntok_out", None),
                   overflow=getattr(m, "overflow", None))
    json.dump(summary, open(f"out/{tag}_summary.json", "w"), ensure_ascii=False)
    print(f"[{tag}] SUMMARY {json.dumps(summary, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()
