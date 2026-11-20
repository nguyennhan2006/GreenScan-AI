"""llm_stages_v1: the language-model stages may read and phrase, never decide or invent. Checked without a network."""
from __future__ import annotations

import pytest

from quantum_gw.agents.claim_model import FLAG, ClaimModel
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.assist.client import StageModel
from quantum_gw.assist.guards import new_numbers, verbatim
from quantum_gw.assist.prompts import family, stance_messages, version
from quantum_gw.assist.stages import explain_result, fill_attributes
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import Claim, DocumentInput
from quantum_gw.providers.base import LLMResponse
from quantum_gw.settings import load_settings


class FakeProvider:
    name, model = "local", "qwen3:4b-instruct-2507-q4_K_M"


class FakeGateway:
    def __init__(self, reply: str, fail: bool = False):
        self.reply, self.fail, self.calls = reply, fail, 0

    def resolve(self, task_type=None):
        return FakeProvider()

    def route(self, task_type=None):
        return ["local:qwen3:4b-instruct-2507-q4_K_M"]

    def generate(self, messages, response_schema=None, task_type=None):
        self.calls += 1
        if self.fail:
            raise RuntimeError("down")
        return LLMResponse(text=self.reply, parsed=None, provider="local", model=FakeProvider.model)


def claim(text: str, **kw) -> Claim:
    return Claim(claim_id="c1", text=text, claim_type="emissions", source_chunk_id="k", source_name="r.pdf", **kw)


def test_guards_catch_invented_numbers_and_spans():
    assert new_numbers("giảm 3,2% năm 2025", "Năm 2025 giảm 3,2%") == set()
    assert new_numbers("giảm 4%", "giảm 3,2%") == {"4"}
    assert new_numbers("1.250.000 m3", "1,250,000 m3") == set()   # separators do not make a new number
    assert verbatim("toàn Tập đoàn", "Phát thải của TOÀN TẬP ĐOÀN giảm") == "toàn Tập đoàn"
    assert verbatim("cả nhà máy", "Phát thải của toàn Tập đoàn giảm") is None


def test_each_family_gets_its_own_prompt_and_version():
    assert family("qwen3:4b-instruct-2507-q4_K_M") == "small" and family("openai/gpt-oss-120b") == "large"
    assert version("stance", "Qwen/Qwen3-4B-Instruct-2507").startswith("stance-s1@")
    assert version("stance", "openai/gpt-oss-120b").startswith("stance-v3@")
    small = stance_messages("Qwen/Qwen3-4B-Instruct-2507", "a", "b")[0]["content"]
    large = stance_messages("openai/gpt-oss-120b", "a", "b")[0]["content"]
    assert small != large and len(small) < len(large)
    fenced = stance_messages("openai/gpt-oss-120b", "a", "b", fence=lambda label, text: f"<{label}>{text}</>")
    assert "injection" in fenced[0]["content"] and "<TUYÊN BỐ (CLAIM)>a</>" in fenced[1]["content"]


def test_a_stage_answer_is_cached_and_an_outage_returns_nothing(tmp_path):
    gw = FakeGateway('{"explanation": "x"}')
    stage = StageModel("explain", "claim_explanation", gateway=gw, cache_dir=tmp_path)
    assert stage.ask(lambda m: [{"role": "user", "content": "q"}], ["k"]) == {"explanation": "x"}
    again = StageModel("explain", "claim_explanation", gateway=gw, cache_dir=tmp_path)
    again.ask(lambda m: [{"role": "user", "content": "q"}], ["k"])
    assert gw.calls == 1
    down = StageModel("explain", "claim_explanation", gateway=FakeGateway("", fail=True), cache_dir=tmp_path)
    assert down.ask(lambda m: [], ["other"]) is None


def test_attributes_are_filled_from_verbatim_spans_only(tmp_path):
    reply = '{"metric": "phát thải", "period": "năm 2025", "baseline": "so với 2019", "scope": "toàn Tập đoàn"}'
    c = claim("Năm 2025 phát thải của toàn Tập đoàn giảm 5%.", scope="nhà máy A")
    out = fill_attributes([c], StageModel("attributes", "claim_normalization", gateway=FakeGateway(reply)))
    assert c.period == "năm 2025"          # written in the sentence: kept
    assert c.baseline is None              # "so với 2019" is not in the sentence: dropped
    assert c.scope == "nhà máy A"          # the rules' value is never overwritten
    assert c.assisted_fields == ["period"] and out["non_verbatim_dropped"] == 1


def test_an_explanation_with_a_new_number_is_not_shown():
    from quantum_gw.domain.enums import VerificationStatus
    from quantum_gw.domain.models import VerificationResult

    v = VerificationResult(claim=claim("Phát thải giảm 5% năm 2025."), status=VerificationStatus.PARTIALLY_SUPPORTED,
                           rationale="Thiếu năm gốc.")
    bad = StageModel("explain", "claim_explanation", gateway=FakeGateway('{"explanation": "Giảm 7% so với 2019."}'))
    assert explain_result(v, bad, ["baseline"]) is False and "explanation" not in v.assist
    good = StageModel("explain", "claim_explanation",
                      gateway=FakeGateway('{"explanation": "Tuyên bố giảm 5% chưa nêu năm gốc.", "next_action": "Xin số liệu năm gốc."}'))
    assert explain_result(v, good, ["baseline"]) is True
    assert v.assist["explanation"]["version"].startswith("explain-s2@")
    assert v.status == VerificationStatus.PARTIALLY_SUPPORTED


def test_offline_profile_never_routes_to_a_cloud_provider(monkeypatch):
    from quantum_gw.providers.router import ModelGateway

    monkeypatch.setenv("QUANTUM_PROFILE", "offline")
    chain = ModelGateway().provider_chain("qualitative_stance")
    assert set(chain) <= {"local", "ollama"}
    monkeypatch.setenv("QUANTUM_PROFILE", "cloud")
    assert "groq" in ModelGateway().provider_chain("qualitative_stance")


def test_the_claim_model_marks_and_never_removes():
    claims = [claim("Mục lục 3 Báo cáo"), claim("Năm 2025 phát thải giảm 5%.", quality_flag="layout_glue")]
    out = ClaimModel("unused", predict=lambda texts: [0.9] * len(texts)).mark(claims)
    assert out["marked"] == 1 and claims[0].quality_flag == FLAG
    assert claims[1].quality_flag == "layout_glue"     # an existing flag is kept
    assert ClaimModel("no/such/folder").mark(claims).get("skipped")


CLAIM = ("Năm 2025, tổng phát thải khí nhà kính phạm vi 1 của công ty là 120.000 tCO2e, giảm 5% so với năm 2024 "
         "nhờ chương trình tiết kiệm năng lượng tại các nhà máy.")
EVIDENCE = ("Báo cáo kiểm kê: phát thải phạm vi 1 năm 2025 của công ty là 120.000 tCO2e; năm 2024 là 126.300 tCO2e. "
            "Chương trình tiết kiệm năng lượng được triển khai tại các nhà máy.")


class FakeReader:
    model = "fake-reader"

    def label(self, claim_text, evidence_text):
        return "C", ["ir says C"]


def _run(tmp_path, monkeypatch, on: bool):
    settings = load_settings("configs/default.yaml")
    settings.runs_dir = str(tmp_path / ("on" if on else "off"))
    if on:
        settings.verification.verify_mode = "dual"
        settings.verification.assist_explain = "all"
        gw = FakeGateway('{"explanation": "Tuyên bố khớp số liệu kiểm kê.", "next_action": "Mở báo cáo kiểm kê."}')
        monkeypatch.setattr("quantum_gw.assist.client.StageModel.__init__.__defaults__", (gw, None), raising=False)
        monkeypatch.setattr("quantum_gw.agents.verifier.VerificationAgent.ir_reader", property(lambda self: FakeReader()))
    return OrchestratorAgent(settings).run([
        DocumentInput(name="claim.txt", text=CLAIM, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=EVIDENCE, role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL),
    ])


def test_stages_on_change_no_verdict_and_no_risk(tmp_path, monkeypatch):
    off = _run(tmp_path, monkeypatch, on=False)
    on = _run(tmp_path, monkeypatch, on=True)
    assert [v.status for v in on.verifications] == [v.status for v in off.verifications]
    assert [r.risk_score for r in on.risks] == [r.risk_score for r in off.risks]
    noted = [v for v in on.verifications if v.assist.get("ir")]
    assert noted and all(n["ir"] == "C" for v in noted for n in v.assist["ir"])
    assert any("explanation" in v.assist for v in on.verifications)
    assert not any(v.assist for v in off.verifications)


@pytest.mark.parametrize("name,value", [("QUANTUM_VERIFY", "sometimes"), ("QUANTUM_ASSIST_EXPLAIN", "maybe")])
def test_stage_flags_reject_unknown_values(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        load_settings("configs/default.yaml")


def test_ollama_honours_the_model_routing_names_for_a_task():
    from quantum_gw.providers.ollama import OllamaProvider

    base = OllamaProvider("http://localhost:11434", "qwen3:8b")
    bound = base.bind_model("qwen3:4b-instruct-2507-q4_K_M")
    assert bound.model == "qwen3:4b-instruct-2507-q4_K_M" and base.model == "qwen3:8b"
    assert bound.base_url == base.base_url and base.bind_model("") is base


def test_an_explanation_never_shows_a_hashed_file_name():
    from quantum_gw.domain.enums import VerificationStatus
    from quantum_gw.domain.models import VerificationResult

    v = VerificationResult(claim=claim("Phát thải giảm 5% năm 2025."), status=VerificationStatus.PARTIALLY_SUPPORTED,
                           rationale="Thiếu năm gốc.")
    reply = '{"explanation": "Mở tài liệu 0ff212c8265ac9cddbbd67de9439011e.pdf để xem.", "next_action": "x"}'
    assert explain_result(v, StageModel("explain", "claim_explanation", gateway=FakeGateway(reply)), ["baseline"])
    assert v.assist["explanation"]["text"] == "Mở tài liệu để xem."
