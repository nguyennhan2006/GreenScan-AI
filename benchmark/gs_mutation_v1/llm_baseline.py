"""Baseline "just ask an LLM": gpt-oss-120b (Groq) reads the claim and the same evidence and picks one of
the five verdicts. Test split, cases M0 (supported originals), M1, M2, M5; every case asked twice to see
whether the answer is stable. Inputs are public company reports (GS-Bench v1).

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_mutation_v1/llm_baseline.py
writes benchmark/gs_mutation_v1/out/llm_gpt-oss-120b.jsonl (cache; resumable) and prints the score
The key comes from GROQ_API_KEY in .env and is never printed.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from score import wilson  # noqa: E402

MODEL = "openai/gpt-oss-120b"
OUT = HERE / "out" / "llm_gpt-oss-120b.jsonl"
VERDICTS = ("SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE")
PROMPT = """Bạn là kiểm toán viên kiểm chứng tuyên bố môi trường. Chỉ dựa vào ĐOẠN BẰNG CHỨNG, chọn đúng một kết luận cho TUYÊN BỐ:
SUPPORTED (bằng chứng xác nhận đầy đủ), PARTIALLY_SUPPORTED (xác nhận một phần), UNSUPPORTED (bằng chứng liên quan nhưng không xác nhận),
CONTRADICTED (bằng chứng mâu thuẫn với tuyên bố), INSUFFICIENT_EVIDENCE (bằng chứng không đủ liên quan).
Trả lời JSON: {{"verdict": "<một trong năm mã>", "reason": "<một câu>"}}

TUYÊN BỐ: {claim}

ĐOẠN BẰNG CHỨNG:
{evidence}"""


def key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("GROQ_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("GROQ_API_KEY trống trong .env")


def ask(client: httpx.Client, claim: str, evidence: str) -> str:
    body = {"model": MODEL, "reasoning_effort": "low", "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": PROMPT.format(claim=claim, evidence=evidence[:6000])}]}
    for attempt in range(6):
        try:
            r = client.post("https://api.groq.com/openai/v1/chat/completions", json=body)
        except httpx.HTTPError:
            time.sleep(5 * (attempt + 1))
            continue
        if r.status_code == 429:
            time.sleep(min(60, float(r.headers.get("retry-after", 10))))
            continue
        if r.status_code != 200:
            return f"HTTP {r.status_code}"
        text = r.json()["choices"][0]["message"].get("content") or ""
        m = re.search(r'"verdict"\s*:\s*"([A-Z_]+)"', text)
        return m.group(1) if m and m.group(1) in VERDICTS else "UNPARSED"
    return "RATE_LIMITED"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cases = [c for c in map(json.loads, (HERE / "cases.jsonl").open(encoding="utf-8"))
             if c["split"] == "test" and (c["mutation"] in ("M1", "M2", "M5") or (c["mutation"] == "M0" and c["base_label"] == "S"))]
    done = {o["case_id"]: o for o in map(json.loads, OUT.open(encoding="utf-8"))} if OUT.exists() else {}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers={"Authorization": f"Bearer {key()}"}, timeout=60) as client, OUT.open("a", encoding="utf-8") as fh:
        for i, c in enumerate(cases, 1):
            if c["case_id"] in done:
                continue
            answers = [ask(client, c["claim"], c["evidence"]) for _ in range(2)]
            row = {"case_id": c["case_id"], "answers": answers}
            done[c["case_id"]] = row
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 25 == 0:
                print(f"[llm] {i}/{len(cases)}", flush=True)

    report = {}
    for kind in ("M0", "M1", "M2", "M5"):
        sel = [c for c in cases if c["mutation"] == kind and c["case_id"] in done]
        first = [done[c["case_id"]]["answers"][0] for c in sel]
        if kind == "M0":
            k = sum(a != "CONTRADICTED" for a in first)
        elif kind in ("M1", "M2"):
            k = sum(a == "CONTRADICTED" for a in first)
        else:
            k = sum(a != "SUPPORTED" for a in first)
        stable = sum(len(set(done[c["case_id"]]["answers"])) == 1 for c in sel)
        lo, hi = wilson(k, len(sel))
        report[kind] = {"n": len(sel), "pass": k, "ci95": [round(lo, 3), round(hi, 3)], "same_answer_twice": stable,
                        "answers": dict(Counter(first))}
        print(f"[llm] {kind}: {k}/{len(sel)} [{lo:.2f}–{hi:.2f}], same answer twice {stable}/{len(sel)}, {dict(Counter(first))}")
    (HERE / "llm_baseline_results.json").write_text(json.dumps({"model": MODEL, "date": time.strftime("%Y-%m-%d"),
                                                                "report": report}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
