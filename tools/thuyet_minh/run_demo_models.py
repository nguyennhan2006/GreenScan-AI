"""Run a demo case into a demo store with the language-model stages on (model-mode-v1).

The answers are cached under .quantum/llm_cache, so pressing "Phân tích" on the same documents in the same
mode during a demo replays them without waiting. Ca A (sample data) is meant for the local model; Hòa Phát
(a published report) for the hosted one.

usage (repo root): .venv/Scripts/python.exe tools/thuyet_minh/run_demo_models.py <demo_store> <local|cloud|rules> <A|B>
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

STORE, MODE, CASE = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
os.environ.update({
    "QUANTUM_REVIEWS_FILE": str(STORE / "reviews" / "decisions.jsonl"),
    "QUANTUM_RUNS_DIR": str(STORE / "runs"),
    "QUANTUM_DOCUMENTS_DIR": str(STORE / "documents"),
    "QUANTUM_ORG_PACK_STORE": str(STORE / "org_packs"),
    "QUANTUM_ORG_PACKS": "",
})
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from quantum_gw import model_mode  # noqa: E402
from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

CASES = {
    "A": [("data/sample/company_esg_2024.txt", "claim_source", "internal"),
          ("data/sample/financial_2024.txt", "evidence", "financial"),
          ("data/sample/legal_notice_2024.txt", "evidence", "legal")],
    "B": [("data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf", "claim_source", "internal"),
          ("data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf", "evidence", "financial")],
}

print("[run] mode", model_mode.set_mode(MODE), "case", CASE, flush=True)
started = time.time()
result = OrchestratorAgent(load_settings()).run(
    [DocumentInput(path=p, role=DocumentRole(r), source_type=SourceType(t)) for p, r, t in CASES[CASE]],
    progress=lambda *a, **k: print("[progress]", *[str(x)[:80] for x in a], flush=True),
)
print(f"[run] seconds {time.time() - started:.1f} run_id {result.run_id}")
print("[run] verdicts", result.summary.status_counts)
with_llm = sum(1 for v in result.verifications if any(e.relation_method == "llm" for e in v.evidence))
explained = sum(1 for v in result.verifications if (v.assist or {}).get("explanation"))
ir_notes = sum(1 for v in result.verifications if (v.assist or {}).get("ir"))
review = sum(1 for v in result.verifications if v.requires_llm_review)
print(f"[run] claims {len(result.verifications)} read_by_model {with_llm} explained {explained} ir_notes {ir_notes} model_flags {review}")
for line in open(Path(result.output_directory) / "audit.jsonl", encoding="utf-8"):
    event = json.loads(line)
    if any(key in event.get("event", "") for key in ("llm", "assist")):
        print("[audit]", event.get("event"), {k: v for k, v in (event.get("payload") or {}).items() if isinstance(v, (int, float, str))})
