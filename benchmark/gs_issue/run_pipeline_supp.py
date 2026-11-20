"""Run the full GreenScan pipeline (offline profile) on the supplements: score twins and explain cases.

    .venv/Scripts/python.exe -I -X utf8 benchmark/gs_issue/run_pipeline_supp.py [--limit N] [--only pairs|explain]

Each item is analysed alone: the claim as the claim source, its evidence (if any) as an external document.
Writes out/pipeline_pairs.jsonl (priority score, band, verdict of clean and mutated twin) and out/pipeline_explain.jsonl
(verdict and explanation per explain case). Settings: configs/default.yaml (same as gs_eval_v2/evaluate.py).
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
import os
SRC = Path(os.environ.get("GS_SRC", ROOT / "src"))  # GS_SRC: another code state, e.g. `git archive HEAD src`
sys.path.insert(0, str(SRC))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def analyse(orch_cls, settings, DocumentInput, claim, evidence):
    docs = [DocumentInput(name="claim.txt", text=claim, role="claim_source", source_type="internal", language="vi")]
    if evidence:
        docs.append(DocumentInput(name="evidence.txt", text=evidence, role="evidence", source_type="external", language="vi"))
    res = orch_cls(settings).run(docs)
    pr = sorted(res.priorities, key=lambda p: -(p.get("priority_score") or 0))
    claims = [p for p in pr if p.get("item_type") == "claim"]
    top = claims[0] if claims else {}
    v = res.verifications[0] if res.verifications else None
    expl = ""
    if v is not None:
        for k in ("explanation", "rationale", "reason"):
            if getattr(v, k, None):
                expl = str(getattr(v, k))
                break
    return {"n_claims": len(res.claims), "priority": top.get("priority_score"), "max_available": top.get("max_available"),
            "reasons": top.get("reasons"), "verdict": v.status.value if v is not None else None, "explanation": expl}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    from quantum_gw.agents.orchestrator import OrchestratorAgent
    from quantum_gw.domain.models import DocumentInput
    from quantum_gw.settings import load_settings
    settings = load_settings(str(ROOT / "configs/default.yaml"))
    out = HERE / "out" / os.environ.get("GS_TAG", "")
    out.mkdir(parents=True, exist_ok=True)
    if a.only in ("", "pairs"):
        pairs = [json.loads(line) for line in open(HERE / "data/supp_score_pairs.jsonl", encoding="utf-8")]
        pairs = pairs[: a.limit] if a.limit else pairs
        t0 = time.time()
        with open(out / "pipeline_pairs.jsonl", "w", encoding="utf-8") as fh:
            for i, p in enumerate(pairs):
                row = {"pair_id": p["pair_id"], "code": p["code"], "severe": p["severe"]}
                for side in ("clean", "mutated"):
                    try:
                        row[side] = analyse(OrchestratorAgent, settings, DocumentInput, p[side]["claim"], p[side]["evidence"])
                    except Exception as e:  # keep going; the error is a result too
                        row[side] = {"error": repr(e)[:300]}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                print(f"pairs {i + 1}/{len(pairs)} {time.time() - t0:.0f}s", flush=True)
    if a.only in ("", "explain"):
        ex = [json.loads(line) for line in open(HERE / "data/supp_explain.jsonl", encoding="utf-8")]
        ex = ex[: a.limit] if a.limit else ex
        t0 = time.time()
        with open(out / "pipeline_explain.jsonl", "w", encoding="utf-8") as fh:
            for i, r in enumerate(ex):
                try:
                    row = analyse(OrchestratorAgent, settings, DocumentInput, r["claim"]["text"], r["evidence"][0]["text"])
                except Exception as e:
                    row = {"error": repr(e)[:300]}
                fh.write(json.dumps({"item_id": r["item_id"], **row}, ensure_ascii=False) + "\n")
                fh.flush()
                print(f"explain {i + 1}/{len(ex)} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
