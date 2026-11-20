"""Parity read of the PRODUCT prompts on the PRODUCT reader: Qwen3-4B Q4 via Ollama on this laptop.

The Kaggle runs read stance-s1 (unfenced) and explain-s1 with bf16 vLLM; the product sends stance-s1f (fenced, as
llm_judge does) and explain-s2 to qwen3:4b-instruct-2507-q4_K_M. Same subsets as Groq (first N by id).
    python benchmark/llm_stages/run_ollama.py s5 120 OUT ;  ... s6 40 OUT
"""
from __future__ import annotations

import json
import secrets
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from quantum_gw.assist.guards import parse_json  # noqa: E402
from quantum_gw.assist.prompts import explain_messages, stance_messages, version  # noqa: E402
from quantum_gw.verification.llm_judge import fenced  # noqa: E402

MODEL = "qwen3:4b-instruct-2507-q4_K_M"


def s5(r):
    tag = secrets.token_hex(6)
    return stance_messages(MODEL, r["claim"], r["evidence"][:1500], fence=lambda label, text: fenced(label, text, tag))


SETS = {"s5": ("s5_pairs", "stance_fenced", s5),
        "s6": ("s6_explain", "explain",
               lambda r: explain_messages(MODEL, r["claim"], r["verdict"], r["rationale"], r["evidence"], r["missing"]))}


def main() -> None:
    stage, limit, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    name, task, build = SETS[stage]
    rows = sorted((json.loads(x) for x in open(HERE / "data" / f"{name}.jsonl", encoding="utf-8")), key=lambda r: r["id"])[:limit]
    done = {json.loads(x)["id"] for x in out.open(encoding="utf-8")} if out.exists() else set()
    print(f"[ollama] {stage}: {len(rows)} rows, {len(done)} done, {version(task, MODEL)}", flush=True)
    t0 = time.time()
    with httpx.Client(timeout=600) as client, out.open("a", encoding="utf-8") as fh:
        for i, r in enumerate(rows, 1):
            if r["id"] in done:
                continue
            body = {"model": MODEL, "messages": build(r), "stream": False, "format": "json",
                    "options": {"temperature": 0, "num_ctx": 4096}}
            raw = client.post("http://localhost:11434/api/chat", json=body).json()["message"]["content"]
            fh.write(json.dumps({"id": r["id"], "raw": raw, "parsed": parse_json(raw), "version": version(task, MODEL)},
                                ensure_ascii=False) + "\n")
            fh.flush()
            if i % 10 == 0:
                print(f"[ollama] {stage} {i}/{len(rows)} {(time.time() - t0) / i:.1f} s/row", flush=True)
    print(f"[ollama] {stage} done {(time.time() - t0):.0f} s", flush=True)


if __name__ == "__main__":
    main()
