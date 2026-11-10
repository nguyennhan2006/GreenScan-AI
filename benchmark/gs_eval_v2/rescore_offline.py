"""Re-score stored GS-Eval v2 verifications with the CURRENT scorer, without re-running the pipeline.

Registered in configs/measurement_decisions.yaml, block claim_quality_v1_and_risk_rubric_v3.

For every labelled item that the current extractor still extracts (inputs/system_outputs_current.jsonl),
the stored VerificationResult is read back from .quantum/runs/<run_id>/result.json, the claim is
marked with claim_quality.suspect_reason (as the extractor now does), and RiskScoringAgent scores it
again. Verdicts are not touched: only the risk score and its components change.

Prints the score section of evaluate.py for the stored scores (before) and the re-scored ones
(after), and writes results/rescore_offline.json.

Run: .venv/Scripts/python.exe -I benchmark/gs_eval_v2/rescore_offline.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

import evaluate as ev  # noqa: E402
from build_inputs import norm  # noqa: E402
from quantum_gw.agents.claim_quality import suspect_reason  # noqa: E402
from quantum_gw.agents.scorer import RiskScoringAgent  # noqa: E402
from quantum_gw.domain.models import VerificationResult  # noqa: E402


class _NoAudit:
    def write(self, *args, **kwargs):
        return None


def stored_verifications(run_ids: set[str]) -> dict[tuple[str, str], dict]:
    out = {}
    for rid in run_ids:
        f = ROOT / ".quantum" / "runs" / rid / "result.json"
        if not f.exists():
            continue
        for v in json.loads(f.read_text(encoding="utf-8")).get("verifications", []):
            out[(rid, norm(v["claim"]["text"]))] = v
    return out


def summary(res: dict) -> dict:
    s = res["system_vs_consensus"]
    return {
        "n": s["n"],
        "total_spearman": s["total_spearman"],
        "spearman_company_bootstrap95": s["spearman_company_bootstrap95"],
        "total_mean_system": s["total_mean_system"],
        "total_mean_reference": s["total_mean_reference"],
        "severity_exact": s["severity_vs_holistic_band"]["exact"],
        "severity_within1": s["severity_vs_holistic_band"]["within1"],
        "penalised_when_not_applicable": {
            c: v["system_penalised_when_not_applicable"] for c, v in s["components"].items()
        },
        "qwk_by_component": {c: v["qwk_system_vs_consensus"] for c, v in s["components"].items()},
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rows = [json.loads(x) for x in (HERE / "inputs" / "system_outputs_current.jsonl").open(encoding="utf-8")]
    sysout = {r["item_id"]: r for r in rows if r["match"] != "not_extracted"}
    items = {}
    for kind in ("explain", "score", "edit"):
        items.update(ev.items_of(kind))
    stored = stored_verifications({r["run_id"] for r in sysout.values()})
    scorer = RiskScoringAgent(str(ROOT / "configs" / "scoring_v1.yaml"), _NoAudit())

    after, missing, flagged = {}, 0, 0
    for iid, so in sysout.items():
        it = items.get(iid)
        v = stored.get((so["run_id"], norm(it["claim"]["text"]))) if it else None
        if v is None:
            missing += 1
            after[iid] = so
            continue
        verification = VerificationResult.model_validate(v)
        verification.claim.quality_flag = suspect_reason(verification.claim.text)
        flagged += bool(verification.claim.quality_flag)
        risk = scorer.run(verification).model_dump(mode="json")
        after[iid] = {**so, "risk": risk}

    before_res, after_res = ev.eval_score(sysout), ev.eval_score(after)
    report = {
        "rubric_version": scorer.version,
        "items_rescored": len(sysout) - missing,
        "items_without_stored_verification": missing,
        "items_flagged_suspect_non_claim": flagged,
        "before": summary(before_res),
        "after": summary(after_res),
    }
    out = HERE / "results" / "rescore_offline.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
