"""Run one API model over an llm_stages_v1 set (the Groq subset of the registration), resumable.

    .venv/Scripts/python.exe -I -X utf8 benchmark/llm_stages/run_api.py s5 120 benchmark/llm_stages/api_out/gpt-oss-120b__s5.jsonl

Provider: Groq, model openai/gpt-oss-120b, reasoning_effort low + json_object (experiments/GROQ-PROBE). The key is
read from .env (GROQ_API_KEY) and never printed. The free tier allows 8,000 tokens per minute: calls are spaced by
their own token counts, and a 429 waits for the reset the server names. Rows already in OUT are skipped.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quantum_gw.assist.guards import parse_json  # noqa: E402
from quantum_gw.assist.prompts import attr_messages, explain_messages, stance_messages, version  # noqa: E402

MODEL = os.environ.get("API_MODEL", "openai/gpt-oss-120b")
SETS = {"s5": ("s5_pairs", "stance", lambda r: stance_messages(MODEL, r["claim"], r["evidence"][:1500])),
        "s2": ("s2_attrs", "attributes", lambda r: attr_messages(MODEL, r["sentence"])),
        "s6": ("s6_explain", "explain",
               lambda r: explain_messages(MODEL, r["claim"], r["verdict"], r["rationale"], r["evidence"], r["missing"]))}
TPM = int(os.environ.get("API_TPM", "7000"))


def key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("GROQ_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("GROQ_API_KEY missing in .env")


def main() -> None:
    stage, limit, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    name, task, build = SETS[stage]
    rows = sorted((json.loads(x) for x in open(HERE / "data" / f"{name}.jsonl", encoding="utf-8")), key=lambda r: r["id"])[:limit]
    done = {json.loads(x)["id"] for x in out.open(encoding="utf-8")} if out.exists() else set()
    out.parent.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": f"Bearer {key()}", "Content-Type": "application/json"}
    pv = version(task, MODEL)
    window: list[tuple[float, int]] = []
    print(f"[api] {stage}: {len(rows)} rows, {len(done)} done, {pv}", flush=True)
    with httpx.Client(timeout=120) as client, out.open("a", encoding="utf-8") as fh:
        for i, r in enumerate(rows, 1):
            if r["id"] in done:
                continue
            body = {"model": MODEL, "messages": build(r), "temperature": 0, "max_tokens": 700,
                    "reasoning_effort": "low", "response_format": {"type": "json_object"}}
            for attempt in range(6):
                now = time.time()
                window = [(t, n) for t, n in window if now - t < 60]
                if sum(n for _, n in window) > TPM:
                    time.sleep(max(1.0, 60 - (now - window[0][0])))
                    continue
                resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
                if resp.status_code == 429:
                    wait = resp.headers.get("retry-after") or "20"
                    print(f"[api] 429, wait {wait}s ({resp.text[:120]})", flush=True)
                    if "per day" in resp.text or "TPD" in resp.text or "RPD" in resp.text:
                        raise SystemExit("[api] daily limit reached; rerun tomorrow, the file resumes")
                    time.sleep(float(re.sub(r"[^\d.]", "", wait) or 20) + 1)
                    continue
                if resp.status_code >= 400:
                    print(f"[api] HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
                    time.sleep(5)
                    continue
                b = resp.json()
                text = b["choices"][0]["message"].get("content") or ""
                used = int((b.get("usage") or {}).get("total_tokens") or 1500)
                window.append((time.time(), used))
                fh.write(json.dumps({"id": r["id"], "raw": text, "parsed": parse_json(text), "prompt_version": pv,
                                     "tokens": used}, ensure_ascii=False) + "\n")
                fh.flush()
                break
            if i % 10 == 0:
                print(f"[api] {stage} {i}/{len(rows)}", flush=True)
    print(f"[api] {stage} done", flush=True)


if __name__ == "__main__":
    main()
