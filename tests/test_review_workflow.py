"""Reviewer decisions are an audit trail and a label source at once.

Both jobs fail the same way — if a decision can be edited, or if a label can be
recorded without a human committing to it, neither the trail nor the dataset is
worth anything.
"""

import pytest

from quantum_gw.storage.reviews import (
    ABSTAIN,
    AI_SUGGESTED,
    CONFIRM,
    FINALIZED,
    HUMAN_REVIEWED,
    OVERRIDE,
    REOPEN,
    REQUEST_EVIDENCE,
    ReviewError,
    ReviewStore,
)

EVIDENCE = [
    {"chunk_id": "c1", "doc_id": "d1", "source_name": "PTBV.pdf", "page": 42,
     "relation": "CONTRADICTS", "text": "Phát thải tăng 12% so với 2023."},
]
CLAIM = {"claim_id": "k1", "text": "Giảm 30% phát thải.", "metric": "emissions"}


@pytest.fixture
def store(tmp_path):
    return ReviewStore(tmp_path / "decisions.jsonl")


def decide(store, decision, **kw):
    return store.record(
        run_id=kw.pop("run_id", "run-1"), claim_id=kw.pop("claim_id", "k1"),
        reviewer=kw.pop("reviewer", "quynh"), decision=decision,
        evidence=kw.pop("evidence", EVIDENCE), claim=kw.pop("claim", CLAIM), **kw,
    )


def test_new_claim_starts_as_ai_suggested(store):
    assert store.state_of("run-1", "k1") == AI_SUGGESTED


def test_confirm_finalizes(store):
    rec = decide(store, CONFIRM, ai_status="SUPPORTED")
    assert (rec.previous_state, rec.new_state) == (AI_SUGGESTED, FINALIZED)
    assert store.state_of("run-1", "k1") == FINALIZED


def test_abstain_is_a_normal_outcome_not_a_finalization(store):
    rec = decide(store, ABSTAIN, comment="thiếu bảng số liệu")
    assert rec.new_state == HUMAN_REVIEWED


def test_request_evidence_keeps_the_claim_open(store):
    assert decide(store, REQUEST_EVIDENCE).new_state == HUMAN_REVIEWED


def test_override_requires_the_replacement_verdict(store):
    with pytest.raises(ReviewError, match="reviewer_status"):
        decide(store, OVERRIDE, ai_status="SUPPORTED")


def test_override_records_both_verdicts(store):
    rec = decide(store, OVERRIDE, ai_status="SUPPORTED", reviewer_status="CONTRADICTED")
    assert rec.ai_status == "SUPPORTED"
    assert rec.reviewer_status == "CONTRADICTED"


def test_reviewer_is_mandatory(store):
    with pytest.raises(ReviewError, match="reviewer"):
        decide(store, CONFIRM, reviewer="  ")


def test_cannot_decide_twice_without_reopening(store):
    decide(store, CONFIRM, ai_status="SUPPORTED")
    with pytest.raises(ReviewError, match="already FINALIZED"):
        decide(store, CONFIRM, ai_status="SUPPORTED")


def test_reopen_only_applies_to_finalized(store):
    with pytest.raises(ReviewError, match="REOPEN only applies"):
        decide(store, REOPEN)


def test_reopen_then_decide_again(store):
    decide(store, CONFIRM, ai_status="SUPPORTED")
    assert decide(store, REOPEN, comment="tìm được bảng mới").new_state == HUMAN_REVIEWED
    assert decide(store, OVERRIDE, reviewer_status="CONTRADICTED").new_state == FINALIZED


def test_history_is_append_only(store):
    decide(store, ABSTAIN)
    decide(store, CONFIRM, ai_status="SUPPORTED")
    history = store.history("run-1", "k1")
    assert [h["decision"] for h in history] == [ABSTAIN, CONFIRM]
    assert history[0]["decision"] == ABSTAIN, "an earlier decision must never be rewritten"


def test_evidence_snapshot_hashes_what_the_reviewer_saw(store):
    rec = decide(store, CONFIRM, ai_status="SUPPORTED")
    snap = rec.evidence_snapshot[0]
    assert snap["page"] == 42
    assert snap["relation"] == "CONTRADICTS"
    assert len(snap["text_sha256"]) == 64
    assert "raw" not in snap


def test_snapshot_detects_changed_evidence_between_runs(store):
    """A label whose evidence text changed must be detectable, not silently reused."""
    first = decide(store, CONFIRM, ai_status="SUPPORTED")
    changed = [{**EVIDENCE[0], "text": "Phát thải giảm 30% so với 2019."}]
    decide(store, REOPEN)
    second = decide(store, CONFIRM, ai_status="SUPPORTED", evidence=changed)
    assert first.evidence_snapshot[0]["text_sha256"] != second.evidence_snapshot[0]["text_sha256"]


def test_only_committed_verdicts_become_gold(store):
    decide(store, CONFIRM, claim_id="k1", ai_status="SUPPORTED")
    decide(store, ABSTAIN, claim_id="k2")
    decide(store, REQUEST_EVIDENCE, claim_id="k3")
    gold = store.gold_records()
    assert [g["claim_id"] for g in gold] == ["k1"]
    assert gold[0]["label_source"] == "human_confirmed"


def test_override_label_uses_the_human_verdict(store):
    decide(store, OVERRIDE, ai_status="SUPPORTED", reviewer_status="CONTRADICTED")
    gold = store.gold_records()[0]
    assert gold["label"] == "CONTRADICTED"
    assert gold["label_source"] == "human_override"


def test_reopened_claim_leaves_the_gold_set(store):
    decide(store, CONFIRM, ai_status="SUPPORTED")
    assert len(store.gold_records()) == 1
    decide(store, REOPEN)
    assert store.gold_records() == [], "a reopened claim is no longer an adjudicated label"


def test_stats_report_override_rate(store):
    decide(store, CONFIRM, claim_id="a", ai_status="SUPPORTED")
    decide(store, OVERRIDE, claim_id="b", ai_status="SUPPORTED", reviewer_status="UNSUPPORTED")
    stats = store.stats()
    assert stats["gold_records"] == 2
    assert stats["ai_override_rate"] == 0.5
    assert stats["reviewers"] == ["quynh"]


def test_runs_are_isolated(store):
    decide(store, CONFIRM, run_id="run-1", ai_status="SUPPORTED")
    assert store.state_of("run-2", "k1") == AI_SUGGESTED


def test_unknown_decision_is_rejected(store):
    with pytest.raises(ReviewError, match="Unknown decision"):
        decide(store, "LOOKS_FINE")
