from __future__ import annotations

import json
from pathlib import Path

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.models import DocumentInput
from quantum_gw.evaluation.metrics import MetricAccumulator
from quantum_gw.settings import AppSettings
from quantum_gw.utils.text import normalize_for_match


def evaluate_golden_set(path: str, settings: AppSettings) -> dict:
    claim_recall = MetricAccumulator()
    status_accuracy = MetricAccumulator()
    citation_coverage = MetricAccumulator()
    gate_pass_rate = MetricAccumulator()
    case_results = []

    # split("\n"), not splitlines(): splitlines() also breaks on U+2028, U+2029
    # and U+0085, which occur inside text extracted from Vietnamese PDFs and are
    # legal inside a JSON string. Using it here corrupts one record per occurrence.
    for line in Path(path).read_text(encoding="utf-8").split("\n"):
        if not line.strip():
            continue
        case = json.loads(line)
        documents = [DocumentInput.model_validate(item) for item in case["documents"]]
        result = OrchestratorAgent(settings).run(documents)
        extracted = [normalize_for_match(claim.text) for claim in result.claims]
        expected_claims = case.get("expected_claim_contains", [])
        claim_hits = sum(any(normalize_for_match(expected) in text for text in extracted) for expected in expected_claims)
        claim_recall.add(claim_hits, len(expected_claims))

        expected_status = case.get("expected_status_by_claim_contains", {})
        correct_statuses = 0
        for fragment, status in expected_status.items():
            matches = [v for v in result.verifications if normalize_for_match(fragment) in normalize_for_match(v.claim.text)]
            if matches and matches[0].status.value == status:
                correct_statuses += 1
        status_accuracy.add(correct_statuses, len(expected_status))

        cited = sum(bool(v.evidence) or v.status.value == "INSUFFICIENT_EVIDENCE" for v in result.verifications)
        citation_coverage.add(cited, len(result.verifications))
        passed_gates = sum(g.passed for g in result.quality_gates if g.gate_id != "G5")
        gate_pass_rate.add(passed_gates, len([g for g in result.quality_gates if g.gate_id != "G5"]))
        case_results.append({"case_id": case["case_id"], "run_id": result.run_id, "release_status": result.summary.release_status})

    return {
        "claim_recall": round(claim_recall.value, 4),
        "verification_status_accuracy": round(status_accuracy.value, 4),
        "citation_coverage": round(citation_coverage.value, 4),
        "mandatory_gate_pass_rate": round(gate_pass_rate.value, 4),
        "cases": case_results,
    }
