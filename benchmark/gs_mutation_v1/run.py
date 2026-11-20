"""Run GreenScan (offline profile, rules only) on every GS-Mutation v1 case under one configuration.

  before    absolute-share-v1, figure-consistency-v1 and the stance-cues-v3 rule layer off (behaviour before 14/11 evening)
  after     the shipped defaults
  internal  shipped defaults + internal-inconsistency-v1 "flag"      (one-document cases only)
  contradict shipped defaults + internal-inconsistency-v1 "contradict" (one-document cases only)

Reduction per case: the verifications of the run; a case passes when any verification meets the
expectation (see score.py). Resumable: cases already in the output file are skipped.

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_mutation_v1/run.py after
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

CONFIG = sys.argv[1] if len(sys.argv) > 1 else "after"
ENV = {
    "before": {"QUANTUM_ABSOLUTE_SHARE": "0", "QUANTUM_ABSOLUTE_CONFLICT": "0", "QUANTUM_FIGURE_CONSISTENCY": "0", "QUANTUM_INTERNAL_INCONSISTENCY": "off"},
    "after": {"QUANTUM_INTERNAL_INCONSISTENCY": "off"},
    "v2": {"QUANTUM_INTERNAL_INCONSISTENCY": "off"},   # 15/11/2026 code (claim-typing-v2, units-v2, support guard on)
    "internal": {"QUANTUM_INTERNAL_INCONSISTENCY": "flag"},
    "contradict": {"QUANTUM_INTERNAL_INCONSISTENCY": "contradict"},
}[CONFIG]
os.environ.update(ENV)
os.environ["QUANTUM_PROFILE"] = "offline"
os.environ.setdefault("QUANTUM_RUNS_DIR", tempfile.mkdtemp(prefix="gs-mut-runs-"))
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.agents.verifier import missing_attributes  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = HERE / "out" / f"{CONFIG}.jsonl"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(line)["case_id"] for line in OUT.open(encoding="utf-8")} if OUT.exists() else set()
    cases = [json.loads(line) for line in (HERE / "cases.jsonl").open(encoding="utf-8") if line.strip()]
    if CONFIG in ("internal", "contradict"):
        cases = [c for c in cases if c["layout"] == "one_doc"]
    cases = [c for c in cases if c["case_id"] not in done]
    settings = load_settings()
    print(f"[mut:{CONFIG}] {len(cases)} cases to run, {len(done)} cached", flush=True)
    with OUT.open("a", encoding="utf-8") as fh:
        for i, case in enumerate(cases, 1):
            t = time.time()
            if case["layout"] == "one_doc":
                docs = [DocumentInput(name="report.txt", text=case["claim"] + "\n\n" + case["evidence"],
                                      role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL)]
            else:
                docs = [
                    DocumentInput(name="claim.txt", text=case["claim"], role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
                    DocumentInput(name="evidence.txt", text=case["evidence"], role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL),
                ]
            try:
                verifications = OrchestratorAgent(settings).run(docs).verifications
                rows = [{"status": v.status.value, "flags": list(v.review_flags), "vague": bool(v.claim.is_vague),
                         "promo": bool(v.claim.vague_terms_matched),
                         "missing": missing_attributes(v.claim), "text": v.claim.text[:160]} for v in verifications]
                error = None
            except Exception as exc:  # noqa: BLE001
                rows, error = [], repr(exc)[:200]
            fh.write(json.dumps({"case_id": case["case_id"], "verifications": rows, "error": error,
                                 "seconds": round(time.time() - t, 2)}, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 50 == 0:
                print(f"[mut:{CONFIG}] {i}/{len(cases)}", flush=True)
    print(f"[mut:{CONFIG}] done", flush=True)


if __name__ == "__main__":
    main()
