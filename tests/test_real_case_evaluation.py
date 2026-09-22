"""Regression against the adjudicated case pack.

This is the test that would have caught the original defect. The unit suite was
fully green while the pipeline scored 0/4 on every case with a regulator's or a
court's decision behind it, because the real pack was reachable only through an
untracked script outside the package and nothing ever ran it.
"""

import pytest

from quantum_gw.evaluation.real_cases import RealCasePack, evaluate_real_cases

PACK = "data/real_cases"


@pytest.fixture(scope="module")
def metrics():
    from quantum_gw.settings import load_settings

    return evaluate_real_cases(load_settings("configs/default.yaml"), PACK)


def test_pack_contains_the_adjudicated_cases():
    pack = RealCasePack(PACK)
    assert {c["case_id"] for c in pack.adjudicated()} == {
        "KDP-2024", "BNY-2022", "DWS-2023", "KLM-2024"
    }


def test_every_adjudicated_case_extracts_its_claim(metrics):
    missed = [c["case_id"] for c in metrics["cases"] if c["outcome"] == "MISSED_CLAIM"]
    assert not missed, f"claims dropped before verification: {missed}"


def test_verification_status_matches_the_adjudicated_outcome(metrics):
    wrong = [
        (c["case_id"], c["expected_status"], c["actual_statuses"])
        for c in metrics["cases"] if not c["status_match"]
    ]
    assert not wrong, f"status mismatches: {wrong}"


def test_evidence_stance_matches_the_pack_labels(metrics):
    """Includes KLM-EV-002, which is labelled CONTEXT_ONLY and must not refute."""
    assert metrics["evidence_stance_accuracy"] == 1.0, metrics["cases"]


def test_every_claim_reaches_the_legal_layer(metrics):
    assert metrics["legal_check_coverage"] == 1.0


def test_control_cases_are_reported_but_never_scored(metrics):
    """A Vietnamese report with no adjudication has no right answer to score.

    The pack is explicit: "Control Việt Nam tuyệt đối không được chuyển thành
    nhãn greenwashing chỉ vì thiếu dữ liệu."
    """
    controls = {c["case_id"] for c in metrics["controls"]}
    assert controls == {"VN-HPG-CONTROL", "VN-BVH-CONTROL"}
    assert not (controls & {c["case_id"] for c in metrics["cases"]})


def test_risk_band_accuracy_is_reported_separately(metrics):
    """Status and severity fail independently, so they are never blended.

    This asserts the metric exists and is honest, not that it is 1.0: the rubric
    is deliberately not tuned against four frozen cases.
    """
    assert 0.0 <= metrics["risk_band_accuracy"] <= 1.0
    assert all(c["expected_risk_band"] for c in metrics["cases"])
