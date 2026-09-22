"""The rubric must stay on a 0-100 scale.

Severity bands are absolute cuts (LOW <25, MEDIUM <50, HIGH <75, CRITICAL 75+).
Adding a component without rebalancing the weights therefore inflates every
score silently — splitting baseline/period and adding scope_boundary took the
total to 120 and moved 32 of 41 claims on the Hoa Phat report into HIGH review
when 3 belonged there. Nothing failed; the numbers just quietly stopped meaning
what the bands assume.
"""

from pathlib import Path

import pytest
import yaml

from quantum_gw.agents.scorer import RiskScoringAgent
from quantum_gw.storage.audit import AuditLogger

RUBRIC = Path("configs/scoring_v1.yaml")


def load():
    path = RUBRIC if RUBRIC.exists() else Path(__file__).resolve().parents[1] / RUBRIC
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_component_maxima_sum_to_100():
    rubric = load()
    total = sum(c["max_score"] for c in rubric["components"].values())
    assert total == 100, (
        f"rubric maxima sum to {total}, not 100 — severity bands are absolute "
        "cuts on a 0-100 scale, so rebalance the weights when adding a component"
    )


def test_every_mandatory_attribute_has_a_component():
    """The five UI attributes must each be backed by real scoring."""
    rubric = load()
    required = {
        "specificity", "quantitative_evidence",   # Specific metric
        "baseline",                                # Baseline
        "period",                                  # Period
        "scope_boundary",                          # Scope / Boundary
        "evidence_support", "independent_assurance",  # Evidence / Methodology
    }
    missing = required - set(rubric["components"])
    assert not missing, f"UI shows attributes with no backing component: {sorted(missing)}"


def scorer(tmp_path):
    return RiskScoringAgent(str(RUBRIC), AuditLogger(tmp_path / "audit.jsonl"))


def test_severity_bands_cover_the_whole_range_without_gaps(tmp_path):
    agent = scorer(tmp_path)
    for score, expected in [(0, "LOW"), (24.9, "LOW"), (25, "MEDIUM"), (49.9, "MEDIUM"),
                            (50, "HIGH"), (74.9, "HIGH"), (75, "CRITICAL"), (100, "CRITICAL")]:
        assert agent._severity(score).value.upper() == expected, f"score {score}"


def test_severity_bands_come_from_the_rubric_file(tmp_path):
    """Editing the rubric must move the bands.

    There were three copies of these numbers -- the rubric's `severity:` block,
    ReviewSettings.high_risk_threshold/critical_risk_threshold, and a hardcoded
    ladder in the scorer -- and only the hardcoded one had any effect. Changing
    the documented thresholds did nothing at all.
    """
    rubric = load()
    rubric["severity"] = {"low": [0, 9], "medium": [10, 19], "high": [20, 29],
                          "critical": [30, 100]}
    path = tmp_path / "rubric.yaml"
    path.write_text(yaml.safe_dump(rubric, allow_unicode=True), encoding="utf-8")

    agent = RiskScoringAgent(str(path), AuditLogger(tmp_path / "audit.jsonl"))
    assert agent._severity(9).value.upper() == "LOW"
    assert agent._severity(10).value.upper() == "MEDIUM"
    assert agent._severity(30).value.upper() == "CRITICAL"


def test_rubric_without_severity_bands_is_rejected(tmp_path):
    """A rubric that cannot state its bands must fail loudly, not score silently."""
    rubric = load()
    del rubric["severity"]
    path = tmp_path / "rubric.yaml"
    path.write_text(yaml.safe_dump(rubric, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match="severity"):
        RiskScoringAgent(str(path), AuditLogger(tmp_path / "audit.jsonl"))


def test_scorer_never_emits_more_than_a_component_maximum():
    """_component clamps, so a mis-tuned penalty cannot exceed its declared max."""
    rubric = load()
    agent = RiskScoringAgent.__new__(RiskScoringAgent)
    agent.rubric = rubric
    for name, cfg in rubric["components"].items():
        component = agent._component(name, 10_000, "overflow probe")
        assert component.score == cfg["max_score"]
        component = agent._component(name, -50, "underflow probe")
        assert component.score == 0.0
