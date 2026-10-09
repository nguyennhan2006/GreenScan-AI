"""The stance model, asked in one batch and cached — checked without a network.

Measured 28/09 on HPG: 713 of 780 pairs reach the judge at 4-6 s each. These
tests pin the three properties that make that affordable and honest: each pair
is asked once per model and prompt, a re-run asks nothing, and the batch asks
exactly the pairs the sequential verifier would have escalated.
"""

from __future__ import annotations

import pytest

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput
from quantum_gw.providers.base import LLMResponse
from quantum_gw.settings import load_settings
from quantum_gw.verification import llm_judge
from quantum_gw.verification.llm_judge import PROMPT_VERSION, LLMStanceJudge


class FakeGateway:
    def __init__(self, model="m1", relation="SUPPORTS", fail=False):
        self.model = model
        self.relation = relation
        self.fail = fail
        self.calls: list[str] = []

    def route(self, task_type=None):
        return [f"fake:{self.model}"]

    def generate(self, messages, response_schema=None, task_type=None):
        self.calls.append(messages[-1]["content"])
        if self.fail:
            raise RuntimeError("provider down")
        return LLMResponse(text="{}", parsed={"relation": self.relation, "reason": "vì sao"},
                           provider="fake", model=self.model)


PAIRS = [("tuyên bố A", "đoạn 1"), ("tuyên bố A", "đoạn 2"), ("tuyên bố A", "đoạn 1")]


def test_the_batch_asks_each_pair_once_and_judge_then_reads_the_cache(tmp_path):
    gateway = FakeGateway()
    judge = LLMStanceJudge(gateway, cache_dir=tmp_path, workers=4)

    stats = judge.prefetch(PAIRS)
    assert len(gateway.calls) == 2          # the repeated pair is asked once
    assert stats["asked"] == 2 and stats["answered"] == 2
    assert stats["served_by"] == {"fake/m1": 2}

    signal = judge.judge("tuyên bố A", "đoạn 2")
    assert signal.relation == "SUPPORTS" and signal.method == "llm"
    assert "[fake/m1]" in signal.reason
    assert len(gateway.calls) == 2          # answered from cache


def test_a_rerun_of_the_same_documents_calls_nothing(tmp_path):
    LLMStanceJudge(FakeGateway(), cache_dir=tmp_path).prefetch(PAIRS)

    again = FakeGateway()
    stats = LLMStanceJudge(again, cache_dir=tmp_path).prefetch(PAIRS)
    assert again.calls == []
    assert stats["asked"] == 0


def test_an_answer_from_one_model_is_never_served_for_another(tmp_path):
    LLMStanceJudge(FakeGateway(model="m1"), cache_dir=tmp_path).prefetch(PAIRS)

    other = FakeGateway(model="m2")
    LLMStanceJudge(other, cache_dir=tmp_path).prefetch(PAIRS)
    assert len(other.calls) == 2


def test_a_failed_call_leaves_the_deterministic_reading_and_is_not_cached(tmp_path):
    down = FakeGateway(fail=True)
    judge = LLMStanceJudge(down, cache_dir=tmp_path)
    stats = judge.prefetch(PAIRS[:1])
    assert stats["failed"] == 1 and stats["answered"] == 0
    assert judge.judge(*PAIRS[0]) is None   # no verdict invented, the rule-based one stands

    recovered = FakeGateway()
    LLMStanceJudge(recovered, cache_dir=tmp_path).prefetch(PAIRS[:1])
    assert len(recovered.calls) == 1        # the failure was not cached


def test_the_manifest_names_the_prompt_and_the_model(tmp_path):
    judge = LLMStanceJudge(FakeGateway(), cache_dir=tmp_path)
    assert judge.version == f"{PROMPT_VERSION}@fake:m1"


# --- the batch asks exactly what the sequential verifier would --------------

CLAIM = ("Công ty đã triển khai chương trình tiết kiệm năng lượng tại các nhà máy "
         "và mở rộng hệ thống điện mặt trời áp mái.")
EVIDENCE = ("Các nhà máy của công ty tiếp tục triển khai chương trình tiết kiệm năng lượng "
            "và lắp thêm hệ thống điện mặt trời áp mái cho khu sản xuất.")


def _run(settings):
    return OrchestratorAgent(settings).run([
        DocumentInput(name="claim.txt", text=CLAIM, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=EVIDENCE, role=DocumentRole.EVIDENCE,
                      source_type=SourceType.EXTERNAL),
    ])


def test_the_dry_pass_finds_exactly_the_pairs_the_verifier_escalates(tmp_path, monkeypatch):
    gateway = FakeGateway(relation="PARTIAL")
    monkeypatch.setattr(llm_judge, "ModelGateway", lambda: gateway)
    settings = load_settings("configs/default.yaml")
    settings.runs_dir = str(tmp_path / "runs")
    settings.verification.llm_stance = "on_ambiguous"
    settings.verification.llm_cache_dir = str(tmp_path / "cache")

    result = _run(settings)

    escalated = [e for v in result.verifications for e in v.evidence if e.relation_method == "llm"]
    assert escalated, "the fixture must reach the judge, or this test proves nothing"
    # Every escalated pair was asked in the batch, and the sequential pass asked
    # nothing new: the number of model calls equals the number of distinct pairs.
    distinct = {(v.claim.text, e.text) for v in result.verifications for e in v.evidence
                if e.relation_method == "llm"}
    assert len(gateway.calls) == len(distinct)
    assert result.manifest.prompt_version == f"{PROMPT_VERSION}@fake:m1"


def _run_with(relation, tmp_path, monkeypatch, decisive=False):
    gateway = FakeGateway(relation=relation)
    monkeypatch.setattr(llm_judge, "ModelGateway", lambda: gateway)
    settings = load_settings("configs/default.yaml")
    settings.runs_dir = str(tmp_path / "runs")
    settings.verification.llm_stance = "on_ambiguous"
    settings.verification.llm_cache_dir = str(tmp_path / f"cache-{relation}-{decisive}")
    settings.verification.llm_stance_decisive = decisive
    return _run(settings)


def test_a_model_alone_cannot_contradict_a_claim_or_raise_its_severity(tmp_path, monkeypatch):
    """HPG 28/09 unguarded: 10 CONTRADICTED, 8 HIGH, 2 CRITICAL on a control company."""
    result = _run_with("CONTRADICTS", tmp_path, monkeypatch)
    for verification, risk in zip(result.verifications, result.risks, strict=True):
        assert verification.status.value != "CONTRADICTED"
        assert risk.severity.value not in {"HIGH", "CRITICAL"}
    suspected = [v for v in result.verifications
                 if any(e.relation == "CONTRADICTS" for e in v.evidence)]
    assert suspected and all(v.requires_llm_review for v in suspected)
    assert all("cần người xem" in v.rationale for v in suspected)


def test_a_model_alone_cannot_make_a_claim_supported(tmp_path, monkeypatch):
    result = _run_with("SUPPORTS", tmp_path, monkeypatch)
    assert all(v.status.value != "SUPPORTED" for v in result.verifications)
    # Same fixture with the guard lifted is SUPPORTED, so the guard is what held.
    lifted = _run_with("SUPPORTS", tmp_path, monkeypatch, decisive=True)
    assert any(v.status.value == "SUPPORTED" for v in lifted.verifications)


def test_the_gold_set_can_lift_the_guard_when_it_says_the_model_is_right(tmp_path, monkeypatch):
    result = _run_with("CONTRADICTS", tmp_path, monkeypatch, decisive=True)
    assert any(v.status.value == "CONTRADICTED" for v in result.verifications)


def test_a_model_that_agrees_with_the_rules_is_not_sent_to_a_reviewer(tmp_path, monkeypatch):
    """Only a changed verdict or a suspected contradiction needs a human."""
    result = _run_with("PARTIAL", tmp_path, monkeypatch)
    touched = [v for v in result.verifications if any(e.relation_method == "llm" for e in v.evidence)]
    assert touched
    assert not any(v.requires_llm_review for v in touched)


def test_the_model_is_switched_by_the_deployment_not_the_checkout(monkeypatch):
    monkeypatch.setenv("QUANTUM_LLM_STANCE", "on_ambiguous")
    assert load_settings("configs/default.yaml").verification.llm_stance == "on_ambiguous"
    monkeypatch.setenv("QUANTUM_LLM_STANCE", "sometimes")
    with pytest.raises(ValueError):
        load_settings("configs/default.yaml")
