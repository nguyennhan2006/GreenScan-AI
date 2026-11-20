"""Switch to the local model and time the same call the "Thử mô hình" button makes (three times)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from quantum_gw import model_mode  # noqa: E402

print("[test] mode", model_mode.set_mode("local"), flush=True)
seconds = []
for attempt in range(1, 4):
    answer = model_mode.test_call()
    seconds.append(float(answer.get("seconds") or 0))
    print(f"[test] lượt {attempt}:", {k: (str(v)[:90]) for k, v in answer.items()}, flush=True)
print(f"[test] giây mỗi lượt gọi: {seconds} (laptop CPU: 32,1)")
