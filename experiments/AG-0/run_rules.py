"""AG-0 baseline: the current GreenScan pipeline (offline profile, rules only) on every GS-Bench v1 case.

Same reduction as benchmark/size_ladder_2026-10-10/run_ladder.py: claim.txt (claim source) + evidence.txt
(external evidence) -> verifications; any CONTRADICTED -> C, all SUPPORTED -> S, else N (no claim extracted -> N).

usage (repository root): .venv/Scripts/python.exe -I experiments/AG-0/run_rules.py
"""
from __future__ import annotations

import json, os, sys, tempfile, time
from pathlib import Path

os.environ["QUANTUM_PROFILE"] = "offline"
os.environ.setdefault("QUANTUM_RUNS_DIR", tempfile.mkdtemp(prefix="gs-ag0-runs-"))
sys.path.insert(0, os.getcwd() + "/src")

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus as V  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
BENCH = Path(os.environ.get("GS_BENCH", "benchmark/gs_bench_v1/gs_bench_v1.jsonl"))
OUT = Path(os.environ.get("GS_RULES_OUT", "experiments/AG-0/out/rules.jsonl"))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(line)["id"] for line in OUT.open(encoding="utf-8")} if OUT.exists() else set()
    cases = [c for c in map(json.loads, BENCH.open(encoding="utf-8")) if c["id"] not in done]
    settings = load_settings()
    print(f"[ag0] {len(cases)} cases to run, {len(done)} cached", flush=True)
    with OUT.open("a", encoding="utf-8") as fh:
        for i, case in enumerate(cases, 1):
            t = time.time()
            docs = [
                DocumentInput(name="claim.txt", text=case["claim"], role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
                DocumentInput(name="evidence.txt", text=case["evidence"], role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL),
            ]
            try:
                statuses = [v.status for v in OrchestratorAgent(settings).run(docs).verifications]
                label = "N" if not statuses else "C" if V.CONTRADICTED in statuses else "S" if all(s == V.SUPPORTED for s in statuses) else "N"
                raw = [s.value for s in statuses]
            except Exception as exc:  # noqa: BLE001
                label, raw = "N", [f"ERROR {exc!r}"[:200]]
            fh.write(json.dumps({"id": case["id"], "label": label, "raw": raw, "seconds": round(time.time() - t, 2)}, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 25 == 0:
                print(f"[ag0] {i}/{len(cases)}", flush=True)
    print("[ag0] done", flush=True)


if __name__ == "__main__":
    main()
