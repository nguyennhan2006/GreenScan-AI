"""model-mode-v1: the run-time switch for the language-model stages (D-2026-11-16-01)."""
import os

import pytest
from fastapi.testclient import TestClient

from quantum_gw import model_mode
from quantum_gw.settings import load_settings

KEYS = (*model_mode._TOUCHED, "GROQ_API_KEY", "FPT_LLM_API_KEY")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    saved = {key: os.environ.get(key) for key in KEYS}
    monkeypatch.setattr(model_mode, "_BASELINE", {key: None for key in model_mode._TOUCHED})
    monkeypatch.setattr(model_mode, "_ollama_models", lambda url: [model_mode.DEFAULT_OLLAMA_MODEL])
    for key in KEYS:
        os.environ.pop(key, None)
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_rules_mode_calls_no_model():
    model_mode.set_mode("local")
    assert model_mode.set_mode("rules") == "rules"
    v = load_settings().verification
    assert (v.llm_stance, v.verify_mode, v.assist_explain, v.assist_attributes) == ("off", "rules", "off", False)
    assert model_mode.current_mode() == "rules"


def test_local_mode_keeps_everything_on_this_machine():
    model_mode.set_mode("local")
    v = load_settings().verification
    assert (v.llm_stance, v.verify_mode, v.assist_explain, v.assist_attributes) == ("on_ambiguous", "dual", "queue", True)
    assert os.environ["QUANTUM_PROFILE"] == "offline"
    assert model_mode.current_mode() == "local"
    from quantum_gw.providers.router import ModelGateway

    for task in ("qualitative_stance", "ir_reading", "claim_explanation", "claim_normalization"):
        route = ModelGateway().route(task)
        assert route and all(r.startswith("local:") for r in route), (task, route)


def test_local_mode_never_falls_back_to_a_cloud_key():
    os.environ["GROQ_API_KEY"] = "test-key"
    model_mode.set_mode("local")
    from quantum_gw.providers.router import ModelGateway

    assert all(r.startswith("local:") for r in ModelGateway().route("qualitative_stance"))


def test_a_model_alone_never_decides_supported_or_contradicted():
    for mode in ("local", "rules"):
        model_mode.set_mode(mode)
        assert load_settings().verification.llm_stance_decisive is False


def test_cloud_mode_needs_a_key_and_says_so():
    assert model_mode.availability()["cloud"]["available"] is False
    with pytest.raises(ValueError):
        model_mode.set_mode("cloud")
    os.environ["GROQ_API_KEY"] = "test-key"
    model_mode.set_mode("cloud")
    assert model_mode.current_mode() == "cloud"
    assert os.environ["LLM_PROVIDER"] == "groq"


def test_local_mode_explains_a_missing_model(monkeypatch):
    monkeypatch.setattr(model_mode, "_ollama_models", lambda url: None)
    state = model_mode.availability()["local"]
    assert state["available"] is False and "Ollama" in state["reason"]
    with pytest.raises(ValueError):
        model_mode.set_mode("local")
    monkeypatch.setattr(model_mode, "_ollama_models", lambda url: ["other:1b"])
    assert "ollama pull" in model_mode.availability()["local"]["reason"]


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError):
        model_mode.set_mode("gpu-magic")


def test_api_switch_and_runtime_report():
    from quantum_gw.api import app

    client = TestClient(app)
    body = client.post("/v1/runtime/model-mode", json={"mode": "local"}).json()
    assert body["model_mode"] == "local" and body["sends_documents_out"] is False
    assert {m["id"] for m in body["model_modes"]} == {"rules", "local", "cloud"}
    assert any(t["task"] == "claim_explanation" and t["engine"] == "llm" for t in body["tasks"])
    assert client.post("/v1/runtime/model-mode", json={"mode": "cloud"}).status_code == 409
    body = client.post("/v1/runtime/model-mode", json={"mode": "rules"}).json()
    assert body["model_mode"] == "rules"
    assert client.post("/v1/runtime/model-test").json()["ok"] is False


def test_layout_frames_are_not_tables():
    """table-shape-v1: an infographic page in one cell is not a table; a grid of values is."""
    from quantum_gw.parsers.documents import is_data_table

    page_frame = [["", "3.1 ĐIỂM NỔI BẬT\nHoàn thành kiểm kê khí nhà kính theo tiêu 90%\nTự chủ nhu cầu điện"],
                  ["BÁO CÁO PHÁT TRIỂN BỀN VỮNG\n2025", None]]
    assert is_data_table(page_frame) is False
    assert is_data_table([["", ""]]) is False
    grid = [["Chỉ tiêu", "2023", "2024"], ["Phát thải phạm vi 1", "120", "110"], ["Phát thải phạm vi 2", "80", "75"]]
    assert is_data_table(grid) is True
    wall_of_text = [["Mục", "\n".join(f"dòng {i}" for i in range(14))], ["Khác", "x"]]
    assert is_data_table(wall_of_text) is False
