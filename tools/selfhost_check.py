"""Phương án 2: check the rented GPU server before a run (models listed, one stance call, one explanation call, latency).

    set QUANTUM_SELFHOST_URL=http://<ip>:8001/v1
    set QUANTUM_SELFHOST_KEY=<the server's --api-key>
    .venv/Scripts/python.exe -X utf8 tools/selfhost_check.py [--model openai/gpt-oss-120b]

Sends one public example (no user document). Exit 0 when the server answers both prompts with parseable JSON.
Then run GreenScan with QUANTUM_PROFILE=selfhost (README of deploy/vastai_a100).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quantum_gw.assist.guards import parse_json  # noqa: E402
from quantum_gw.assist.prompts import explain_messages, stance_messages  # noqa: E402

CLAIM = "Năm 2024, Tập đoàn đã lắp đặt hệ thống điện mặt trời áp mái công suất 5 MWp tại nhà máy Hải Dương."
EVIDENCE = "Trong năm 2024, hệ thống điện mặt trời áp mái 5 MWp tại Khu liên hợp Hải Dương đã đi vào vận hành."


def call(url: str, key: str, payload: dict) -> tuple[dict, float]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST" if payload else "GET",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "greenscan-check/1.0"})
    if not payload:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode()), round(time.time() - t0, 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("QUANTUM_SELFHOST_MODEL", "openai/gpt-oss-120b"))
    a = ap.parse_args()
    url, key = os.environ.get("QUANTUM_SELFHOST_URL", "").rstrip("/"), os.environ.get("QUANTUM_SELFHOST_KEY", "")
    if not url:
        print("Đặt QUANTUM_SELFHOST_URL (http://<ip>:8001/v1) và QUANTUM_SELFHOST_KEY trước.")
        return 2
    models, secs = call(f"{url}/models", key, {})
    names = [m["id"] for m in models.get("data", [])]
    print(f"models ({secs} s): {names}")
    if a.model not in names:
        print(f"! '{a.model}' không có trên máy chủ; đặt QUANTUM_SELFHOST_MODEL bằng một tên ở trên.")
        return 1
    ok = True
    for task, msgs in (("stance", stance_messages(a.model, CLAIM, EVIDENCE)),
                       ("explain", explain_messages(a.model, CLAIM, "SUPPORTED", "Đoạn bằng chứng xác nhận công suất và năm.",
                                                    [{"source_name": "BCPTBV 2024", "page": 12, "text": EVIDENCE,
                                                      "relation": "SUPPORTS"}], []))):
        out, secs = call(f"{url}/chat/completions", key, {"model": a.model, "messages": msgs, "temperature": 0,
                                                          "max_tokens": 400})
        text = out["choices"][0]["message"].get("content") or ""
        parsed = parse_json(text)
        ok &= parsed is not None
        print(f"{task}: {secs} s · tokens {out.get('usage')} · {'OK' if parsed else '!! không đọc được JSON'} · {text[:160]!r}")
    print("Sẵn sàng: đặt QUANTUM_PROFILE=selfhost rồi chạy GreenScan." if ok else "Chưa sẵn sàng.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
