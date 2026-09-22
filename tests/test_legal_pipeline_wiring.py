"""The legal layer must actually run inside the pipeline.

corpus/rules/checker/gates were complete and unit-tested but no pipeline code
imported them — only `tools/legal_vertical_slice.py` did. A run therefore
produced a greenwashing risk score without ever stating which instrument governs
the claim, and the scope limits attached to adjudicated sources (settlement
without admission, "do not generalize this finding") never reached the output.
"""

import pytest

from quantum_gw.agents.legal_check import LegalCheckAgent
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.reviewer import ReviewerAgent
from quantum_gw.domain.models import DocumentInput, RunManifest
from quantum_gw.legal.qualifiers import from_metadata, merge
from quantum_gw.settings import LegalSettings
from quantum_gw.storage.audit import AuditLogger

CLAIM = DocumentInput(
    name="claim.txt",
    text="Testing with municipal recycling facilities validated that K-Cup pods could be "
         "effectively recycled.",
    role="claim_source",
    source_type="internal",
    metadata={
        "case_status": "SEC_SETTLEMENT_WITHOUT_ADMISSION_OR_DENIAL",
        "adjudication_scope": "Do not generalize this finding to every current K-Cup product.",
    },
)
EVIDENCE = DocumentInput(
    name="order.txt",
    text="The SEC order found the 2019 and 2020 statements incomplete and inaccurate "
         "because the negative feedback was omitted.",
    role="evidence",
    source_type="legal",
    metadata={
        "case_status": "SEC_SETTLEMENT_WITHOUT_ADMISSION_OR_DENIAL",
        "adjudication_scope": "Do not generalize this finding to every current K-Cup product.",
    },
)


@pytest.fixture
def result(settings):
    return OrchestratorAgent(settings).run([CLAIM, EVIDENCE])


def test_legal_check_runs_for_every_claim(result):
    assert result.claims
    assert len(result.legal_checks) == len(result.verifications)


def test_plan_declares_the_legal_step(result):
    assert "check_applicable_law" in result.manifest.plan


def test_legal_check_names_the_instrument_and_the_date_it_applied(result):
    record = result.legal_checks[0]
    assert record["applicable_sources"], "a finding must name what it was checked against"
    assert record["as_of_date"]
    assert record["check_mode"] in {"current_policy_alignment", "historical_compliance"}


def test_applicable_sources_are_not_listed_twice(result):
    """One amending decree sits in the chain of several base instruments."""
    ids = [source["id"] for source in result.legal_checks[0]["applicable_sources"]]
    assert len(ids) == len(set(ids))


def test_scope_limits_survive_into_the_legal_record(result):
    """Without these, "settled without admission" becomes "the company lied"."""
    qualifiers = result.legal_checks[0]["source_qualifiers"]
    assert any("SEC_SETTLEMENT_WITHOUT_ADMISSION_OR_DENIAL" in q for q in qualifiers)
    assert any("Do not generalize" in q for q in qualifiers)


def test_unbound_rule_pack_yields_insufficient_evidence_not_a_verdict(result):
    """No rule in the pack is bound to clause text or reviewed yet.

    The honest answer is that the check could not be completed, never MATCH or
    NOT_MATCH — that would be a statement about law the system never read.
    """
    record = result.legal_checks[0]
    assert record["legal_finding"] == "INSUFFICIENT_EVIDENCE"
    assert record["requires_human_review"]
    assert record["notes"]


def test_missing_registry_disables_the_layer_without_failing_the_run(tmp_path):
    """A collection gap is not a reason to lose an otherwise complete run."""
    agent = LegalCheckAgent(
        LegalSettings(registry_file=str(tmp_path / "absent.yaml")),
        AuditLogger(tmp_path / "audit.jsonl"),
    )
    assert not agent.available
    assert agent.unavailable_reason


def test_g7_reports_the_layer_was_not_consulted(tmp_path):
    gates = ReviewerAgent(AuditLogger(tmp_path / "a.jsonl")).run(
        chunks=[], verifications=[], risks=[],
        manifest=RunManifest(run_id="r", pipeline_version="v", config_hash="h",
                             input_hashes={"a": "b"}, plan=["x"]),
        legal_checks=[], legal_unavailable_reason="registry missing",
    )
    g7 = next(g for g in gates if g.gate_id == "G7")
    assert g7.passed and "registry missing" in g7.details


def test_g7_holds_a_release_on_an_adverse_finding(tmp_path):
    gates = ReviewerAgent(AuditLogger(tmp_path / "a.jsonl")).run(
        chunks=[], verifications=[], risks=[],
        manifest=RunManifest(run_id="r", pipeline_version="v", config_hash="h",
                             input_hashes={"a": "b"}, plan=["x"]),
        legal_checks=[{"legal_finding": "NOT_MATCH", "issue": "green_taxonomy",
                       "blocked_sources": []}],
    )
    g7 = next(g for g in gates if g.gate_id == "G7")
    assert not g7.passed
    assert g7.status == "PENDING_HUMAN_REVIEW"


def test_qualifiers_are_collected_and_deduplicated():
    metadata = {"case_status": "SETTLED", "legal_caution": "Scope limited.", "unrelated": "x"}
    qualifiers = from_metadata(metadata)
    assert "case_status: SETTLED" in qualifiers
    assert not any("unrelated" in q for q in qualifiers)
    assert merge([qualifiers, qualifiers]) == qualifiers
