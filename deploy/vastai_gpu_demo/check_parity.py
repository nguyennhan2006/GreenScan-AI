"""Compare the newest run in a store with the laptop's rules-only Hòa Phát run.

The model's answers are cached by (prompt version, model, claim text, evidence text). They replay on the
laptop only when this machine reads the same claims out of the same PDFs, so a difference here means: stop.

usage: python vast/check_parity.py <store> vast/expected_B.json [run_id]      exit 0 = same, 1 = different
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

store, expected_path = Path(sys.argv[1]), Path(sys.argv[2])
expected = json.loads(expected_path.read_text(encoding="utf-8"))
if len(sys.argv) > 3:      # the run to compare; without it, the newest finished run in the store
    runs = [store / "runs" / sys.argv[3] / "result.json"]
else:
    runs = sorted((p for p in (store / "runs").glob("*/result.json")), key=lambda p: p.stat().st_mtime)
if not runs or not runs[-1].is_file():
    sys.exit("[parity] no finished run to compare")
result = json.loads(runs[-1].read_text(encoding="utf-8"))
got = sorted([hashlib.sha256(v["claim"]["text"].encode("utf-8")).hexdigest()[:16], v["status"]]
             for v in result["verifications"])
want = [list(row) for row in expected["claims"]]
summary = result["summary"]
print(f"[parity] run {result['run_id']}: {summary['total_claims']} claims, {summary['status_counts']}, "
      f"chunks {summary['total_chunks']} (laptop: {expected['total_claims']}, {expected['status_counts']}, "
      f"chunks {expected['total_chunks']})")
if got == want:
    print("[parity] OK: cùng tuyên bố, cùng kết luận như laptop")
    sys.exit(0)
got_ids, want_ids = {g[0] for g in got}, {w[0] for w in want}
text_by_id = {hashlib.sha256(v["claim"]["text"].encode("utf-8")).hexdigest()[:16]: v["claim"]["text"]
              for v in result["verifications"]}
print(f"[parity] KHÁC: thừa {len(got_ids - want_ids)}, thiếu {len(want_ids - got_ids)}, "
      f"khác kết luận {sum(1 for g in got if g[0] in want_ids and g not in want)}")
for claim_id in sorted(got_ids - want_ids)[:8]:
    print("   thừa:", text_by_id[claim_id][:140])
sys.exit(1)
