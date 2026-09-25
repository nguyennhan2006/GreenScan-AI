"""T01–T10: the minimum behaviours an audit-grade verifier must get right.

Written from an external review checklist (2026-09-25), not from the code, so
they are allowed to fail. Each test states the behaviour an auditor expects; a
failure here is a gap in the product, not a broken test, and is recorded as such
in ISSUES_REGISTER rather than quietly relaxed.
"""

from __future__ import annotations

import pytest

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus
from quantum_gw.domain.models import DocumentInput


def _run(settings, claim: str, evidence: str, source_type: SourceType = SourceType.EXTERNAL):
    documents = [
        DocumentInput(name="claim.txt", text=claim, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=evidence, role=DocumentRole.EVIDENCE,
                      source_type=source_type),
    ]
    return OrchestratorAgent(settings).run(documents)


def _status(result) -> VerificationStatus:
    assert result.verifications, "no claim was extracted"
    return result.verifications[0].status


def _reasons(result) -> str:
    return " ".join(
        (v.rationale or "") + " " + " ".join(e.relation_reason or "" for e in v.evidence)
        for v in result.verifications
    )


# --- T01/T02: a percentage claim must be checked against the figures behind it ---

@pytest.mark.xfail(strict=True, reason="B9(c): % change is not recomputed from base/current — ISSUES P6")
def test_t01_exact_numeric_support(settings):
    """'giảm 20%' against 100 → 80 is arithmetic the system should perform."""
    result = _run(
        settings,
        "Phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2025 giảm 20% so với năm 2020.",
        "Kiểm kê độc lập: phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2020 là 100.000 tấn CO2e, "
        "năm 2025 là 80.000 tấn CO2e.",
    )
    assert _status(result) == VerificationStatus.SUPPORTED


@pytest.mark.xfail(strict=True, reason="B9(c): % change is not recomputed from base/current — ISSUES P6")
def test_t02_numeric_contradiction(settings):
    """'giảm 30%' against 100 → 120 is a contradiction the arithmetic should find."""
    result = _run(
        settings,
        "Phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2025 giảm 30% so với năm 2020.",
        "Kiểm kê độc lập: phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2020 là 100.000 tấn CO2e, "
        "năm 2025 là 120.000 tấn CO2e.",
    )
    assert _status(result) == VerificationStatus.CONTRADICTED


def test_t03_missing_baseline_does_not_get_a_verdict(settings):
    """One endpoint cannot verify a change: the answer is 'not enough', not a guess."""
    result = _run(
        settings,
        "Phát thải khí nhà kính của Tập đoàn giảm 20% so với năm 2020.",
        "Kiểm kê độc lập: phát thải khí nhà kính của Tập đoàn năm 2025 là 80.000 tấn CO2e.",
    )
    assert _status(result) in {
        VerificationStatus.INSUFFICIENT_EVIDENCE,
        VerificationStatus.PARTIALLY_SUPPORTED,
    }
    assert _status(result) is not VerificationStatus.SUPPORTED


def test_t04_scope_mismatch_is_not_comparable(settings):
    """Scope 1+2 against Scope 1 alone must not be turned into a −20%."""
    result = _run(
        settings,
        "Phát thải khí nhà kính Scope 1 và 2 năm 2025 là 80.000 tấn CO2e.",
        "Kiểm kê: phát thải khí nhà kính Scope 1 năm 2025 là 100.000 tấn CO2e.",
    )
    assert _status(result) != VerificationStatus.CONTRADICTED
    assert _status(result) != VerificationStatus.SUPPORTED


def test_t05_boundary_mismatch_is_not_comparable(settings):
    """A group figure and a single plant's figure are different quantities."""
    result = _run(
        settings,
        "Phát thải khí nhà kính của toàn Tập đoàn năm 2025 là 100.000 tấn CO2e.",
        "Kiểm kê: phát thải khí nhà kính tại nhà máy Dung Quất năm 2025 là 80.000 tấn CO2e.",
    )
    assert _status(result) != VerificationStatus.CONTRADICTED


def test_t06_unit_multiples_are_normalised(settings):
    """100 ktCO2e and 100.000 tCO2e are the same quantity."""
    from quantum_gw.utils.text import parse_quantities

    kilo = parse_quantities("100 ktCO2e")
    tonnes = parse_quantities("100.000 tấn CO2e")
    assert kilo and tonnes
    assert kilo[0][1] == tonnes[0][1] == "tco2e"
    assert kilo[0][0] == tonnes[0][0] == 100000.0


def test_t07_absolute_is_not_comparable_with_intensity(settings):
    """A total and a per-tonne intensity are different measurements."""
    result = _run(
        settings,
        "Phát thải khí nhà kính của Tập đoàn năm 2025 là 100.000 tấn CO2e.",
        "Cường độ phát thải năm 2025 là 0,8 tấn CO2e trên mỗi tấn thép thô.",
    )
    assert _status(result) != VerificationStatus.CONTRADICTED
    assert _status(result) != VerificationStatus.SUPPORTED


def test_t08_a_target_does_not_support_an_achievement(settings):
    """'we cut 30%' is not supported by 'we aim to cut 30% by 2030'."""
    result = _run(
        settings,
        "Tập đoàn đã giảm 30% phát thải khí nhà kính Scope 1 và 2 so với năm 2020.",
        "Tập đoàn đặt mục tiêu giảm 30% phát thải khí nhà kính Scope 1 và 2 vào năm 2030 so với năm 2020.",
    )
    assert _status(result) != VerificationStatus.SUPPORTED


def test_t09_a_distracting_target_does_not_outrank_the_actual_figures(settings):
    """A target sentence and a Net Zero pledge must not crowd out the actual table."""
    result = _run(
        settings,
        "Phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2025 giảm 20% so với năm 2020.",
        "Tập đoàn đặt mục tiêu giảm 20% phát thải khí nhà kính.\n"
        "Tập đoàn cam kết đạt Net Zero vào năm 2050.\n"
        "Kiểm kê độc lập: phát thải khí nhà kính Scope 1 và 2 năm 2020 là 100.000 tấn CO2e, "
        "năm 2025 là 105.000 tấn CO2e.",
    )
    texts = [e.text for v in result.verifications for e in v.evidence]
    assert any("105.000" in text for text in texts), "the actual figures must reach the verifier"
    assert _status(result) != VerificationStatus.SUPPORTED


def test_t10_legal_relevance_is_not_legal_applicability(settings):
    """Resolving an instrument is not the same as the instrument governing this claim."""
    result = _run(
        settings,
        "Nhà máy thép của Tập đoàn đã giảm phát thải khí nhà kính trong năm 2025.",
        "Kiểm kê ghi nhận phát thải khí nhà kính tại nhà máy thép năm 2025.",
    )
    for check in result.legal_checks:
        finding = check.get("legal_finding")
        assert finding in {None, "INSUFFICIENT_EVIDENCE"} or check.get("rules_applied"), (
            "a legal finding must name the rule it applied, not just a matched instrument"
        )
