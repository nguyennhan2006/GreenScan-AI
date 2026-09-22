"""Evaluation against the adjudicated case pack in `data/real_cases`.

Two evaluation vocabularies existed and only the synthetic one was wired in.
`data/golden/golden_cases.jsonl` holds four hand-built Vietnamese cases keyed by
`expected_claim_contains` / `expected_status_by_claim_contains`, and
`evaluation/runner.py` read that and nothing else. The real pack — four cases
with a regulator's or court's decision behind them — uses `expected_verification`
plus `risk_band` plus a per-evidence `supports_status`, and was reachable only
through an untracked bridge script sitting outside the package, so it could
never gate anything.

This adapter puts the real pack on the same footing as the synthetic set, and
measures the three labels it actually carries rather than just the first:

    status accuracy   the case-level verification verdict
    stance accuracy   per evidence passage, including CONTEXT_ONLY negatives
    risk band         the severity the reviewers assigned

Control cases are scored separately and never as accuracy. A Vietnamese report
with no adjudication is there to exercise extraction and consistency; counting
it as right or wrong would invent a label the pack explicitly refuses to give it
("Control Việt Nam tuyệt đối không được chuyển thành nhãn greenwashing chỉ vì
thiếu dữ liệu").
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.models import DocumentInput
from quantum_gw.evaluation.metrics import MetricAccumulator
from quantum_gw.legal.qualifiers import QUALIFIER_KEYS
from quantum_gw.settings import AppSettings

DEFAULT_PACK = "data/real_cases"

# The pack labels each evidence record with the status it supports; the pipeline
# labels each passage with its stance. Same question, different vocabulary.
GOLD_STANCE = {
    "CONTRADICTED": "CONTRADICTS",
    "SUPPORTED": "SUPPORTS",
    "PARTIALLY_SUPPORTED": "PARTIAL",
    "CONTEXT_ONLY": "CONTEXT",
}

CONTROL_SPLIT = "control"


def _read_jsonl(path: Path) -> list[dict]:
    # split("\n"), not splitlines(): splitlines() also breaks on U+2028, U+2029
    # and U+0085, which occur inside text extracted from Vietnamese PDFs and are
    # legal inside a JSON string, corrupting one record per occurrence.
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


class RealCasePack:
    """The case pack on disk: cases, their claims and their evidence."""

    def __init__(self, root: str | Path = DEFAULT_PACK):
        self.root = Path(root)
        self.cases = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((self.root / "cases").glob("*/case.json"))
        ]
        self.claims: dict[str, list[dict]] = {}
        for claim in _read_jsonl(self.root / "claims/claims.jsonl"):
            self.claims.setdefault(claim["case_id"], []).append(claim)
        self.evidence: dict[str, list[dict]] = {}
        for item in _read_jsonl(self.root / "evidence/evidence.jsonl"):
            self.evidence.setdefault(item["case_id"], []).append(item)

    def adjudicated(self) -> list[dict]:
        return [case for case in self.cases if case["split"] != CONTROL_SPLIT]

    def documents(self, case: dict) -> list[DocumentInput]:
        """Claim and evidence records as pipeline inputs.

        Every document carries the case's scope limits in its metadata, so the
        settlement qualifier and the adjudication scope travel with the evidence
        into the legal check record instead of being lost at the boundary.
        """
        qualifiers = {key: case[key] for key in QUALIFIER_KEYS if case.get(key)}
        case_id = case["case_id"]
        documents = [
            DocumentInput(
                name=f"{claim['claim_id']}.txt",
                text=claim["text"],
                role="claim_source",
                source_type="internal",
                language="en",
                metadata={**qualifiers, "claim_id": claim["claim_id"], "case_id": case_id},
            )
            for claim in self.claims.get(case_id, [])
        ]
        for item in self.evidence.get(case_id, []):
            documents.append(
                DocumentInput(
                    name=f"{item['evidence_id']}.txt",
                    text=item["text"],
                    role="evidence",
                    # An enforcement order is a legal source; a company's own
                    # report about itself is not.
                    source_type=(
                        "legal"
                        if item.get("admissibility") == "official_regulatory_order"
                        else "external"
                    ),
                    language="en",
                    metadata={
                        **qualifiers,
                        "evidence_id": item["evidence_id"],
                        "case_id": case_id,
                        "source_id": item.get("source_id", ""),
                    },
                )
            )
        return documents


def evaluate_real_cases(
    settings: AppSettings,
    pack_root: str | Path = DEFAULT_PACK,
) -> dict[str, Any]:
    pack = RealCasePack(pack_root)
    status_accuracy = MetricAccumulator()
    stance_accuracy = MetricAccumulator()
    risk_band_accuracy = MetricAccumulator()
    legal_coverage = MetricAccumulator()
    cases: list[dict[str, Any]] = []

    for case in pack.adjudicated():
        result = OrchestratorAgent(settings).run(pack.documents(case))
        expected_status = case["expected_verification"]
        statuses = [v.status.value for v in result.verifications]
        status_hit = int(expected_status in statuses)
        status_accuracy.add(status_hit)

        gold_stances = {
            item["evidence_id"]: GOLD_STANCE.get(item["supports_status"], "")
            for item in pack.evidence.get(case["case_id"], [])
        }
        stance_hits = stance_total = 0
        for verification in result.verifications:
            for evidence in verification.evidence:
                evidence_id = evidence.source_name.removesuffix(".txt")
                expected_stance = gold_stances.get(evidence_id)
                if not expected_stance:
                    continue
                stance_total += 1
                stance_hits += int(evidence.relation == expected_stance)
        stance_accuracy.add(stance_hits, stance_total)

        expected_band = case.get("risk_band", "")
        bands = [risk.severity.value for risk in result.risks]
        band_hit = int(bool(expected_band) and expected_band in bands)
        if expected_band:
            risk_band_accuracy.add(band_hit)

        legal_coverage.add(len(result.legal_checks), len(result.verifications))

        cases.append({
            "case_id": case["case_id"],
            "run_id": result.run_id,
            "organization": case.get("organization", ""),
            "expected_status": expected_status,
            "actual_statuses": statuses,
            "status_match": bool(status_hit),
            "expected_risk_band": expected_band,
            "actual_risk_bands": bands,
            "risk_band_match": bool(band_hit),
            "stance_hits": f"{stance_hits}/{stance_total}",
            "claims_extracted": len(result.claims),
            # Zero extracted claims and a wrong status are different failures with
            # different fixes, and reporting them as one number hides which.
            "outcome": _outcome(result.claims, status_hit),
            "release_status": result.summary.release_status,
        })

    return {
        "pack": str(pack.root),
        "adjudicated_cases": len(cases),
        "verification_status_accuracy": round(status_accuracy.value, 4),
        "evidence_stance_accuracy": round(stance_accuracy.value, 4),
        "risk_band_accuracy": round(risk_band_accuracy.value, 4),
        "legal_check_coverage": round(legal_coverage.value, 4),
        "cases": cases,
        "controls": [
            {"case_id": case["case_id"], "organization": case.get("organization", ""),
             "note": "Not scored: no adjudicated label. Run separately with source documents."}
            for case in pack.cases
            if case["split"] == CONTROL_SPLIT
        ],
    }


def _outcome(claims: list, status_hit: int) -> str:
    if not claims:
        return "MISSED_CLAIM"
    return "MATCH" if status_hit else "MISMATCH"
