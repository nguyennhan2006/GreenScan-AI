"""Bring the static-demo store up to the 15/11/2026 code without losing the 14/11 feedback story.

The store made by run_feedback_demo.py (14/11) holds three sessions: Hòa Phát + the "Ngân hàng TMCP Xanh Demo"
pack, and Ca A round 1 (a reviewer overrode A2 to CONTRADICTED) and round 2 (the precedent shown). Since 15/11
the machine itself finds A2 CONTRADICTED by arithmetic (absolute-share-v1). This script:
  1. re-runs Hòa Phát with the same approved pack, on today's code, and removes the 14/11 pack session;
  2. runs Ca A once more with precedents on: the machine's own CONTRADICTED now sits beside the reviewer's
     earlier decision -- the feedback loop closed by a rule the team wrote, not by the machine changing itself.
Prints the new run ids for build_static_demo.py --label.

usage (repo root): .venv/Scripts/python.exe -I tools/thuyet_minh/run_demo_v2.py <demo_store>
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

STORE = Path(sys.argv[1])
os.environ.update({
    "QUANTUM_PROFILE": "offline",
    "QUANTUM_REVIEWS_FILE": str(STORE / "reviews" / "decisions.jsonl"),
    "QUANTUM_RUNS_DIR": str(STORE / "runs"),
    "QUANTUM_DOCUMENTS_DIR": str(STORE / "documents"),
    "QUANTUM_ORG_PACK_STORE": str(STORE / "org_packs"),
    "QUANTUM_LLM_STANCE": "off",
    "QUANTUM_ORG_PACKS": "",
})
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.legal import org_registry  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

CASES = {
    "A": [("data/sample/company_esg_2024.txt", "claim_source", "internal"),
          ("data/sample/financial_2024.txt", "evidence", "financial"),
          ("data/sample/legal_notice_2024.txt", "evidence", "legal")],
    "B": [("data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf", "claim_source", "internal"),
          ("data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf", "evidence", "financial")],
}


def docs(case):
    return [DocumentInput(path=p, role=DocumentRole(r), source_type=SourceType(t)) for p, r, t in CASES[case]]


old_pack_runs = []
for run in (STORE / "runs").iterdir():
    result = run / "result.json"
    if result.is_file() and json.loads(result.read_text(encoding="utf-8")).get("org_findings"):
        old_pack_runs.append(run)

settings_b = load_settings()
settings_b.legal.org_packs = org_registry.resolve(["demo_ngan_hang_xanh"])
settings_b.feedback.precedents = False
run_b = OrchestratorAgent(settings_b).run(docs("B"))
for run in old_pack_runs:
    shutil.rmtree(run)
print("pack_run", run_b.run_id, run_b.summary.status_counts, "removed", [r.name for r in old_pack_runs])

run_a = OrchestratorAgent(load_settings()).run(docs("A"))
print("case_a_run", run_a.run_id, {v.claim.text[:40]: v.status.value for v in run_a.verifications})
print("case_a_precedents", bool(run_a.precedents))
