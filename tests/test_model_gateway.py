import pytest

from quantum_gw.providers import (
    PROVIDERS,
    LLMResponse,
    ModelGateway,
    NoProviderAvailableError,
)
from quantum_gw.providers.base import LLMProvider, ModelInfo
from quantum_gw.providers.fpt import FPTProvider
from quantum_gw.providers.ollama import OllamaProvider
from quantum_gw.settings import GatewaySettings, load_gateway_settings

EMPTY_KEYS = GatewaySettings(
    local_base_url="",  # even the local endpoint unset
    local_model="",
)


def test_registry_contains_all_locked_providers():
    for name in ["local", "ollama", "fpt", "gemini", "openai", "anthropic", "openrouter"]:
        assert name in PROVIDERS


def test_gateway_starts_with_all_keys_empty():
    gateway = ModelGateway(EMPTY_KEYS)
    assert gateway.resolve("claim_extraction") is None
    report = gateway.describe()
    assert all(not entry["configured"] for entry in report.values())


def test_generate_raises_clean_error_when_nothing_configured():
    gateway = ModelGateway(EMPTY_KEYS)
    with pytest.raises(NoProviderAvailableError):
        gateway.generate([{"role": "user", "content": "hi"}], task_type="claim_extraction")


def test_routing_policy_loaded_and_deterministic_tasks_skip_llm():
    gateway = ModelGateway(GatewaySettings())
    assert "claim_extraction" in gateway.routing
    # quantitative verification must never reach an LLM provider chain head
    chain = gateway.provider_chain("quantitative_verification")
    assert "deterministic" not in chain and "none" not in chain


def test_fallback_order_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fpt")
    monkeypatch.setenv("LLM_FALLBACK_ORDER", "fpt,local")
    settings = load_gateway_settings()
    assert settings.provider == "fpt"
    assert settings.fallback_order == ["fpt", "local"]


def test_local_slot_switches_to_ollama():
    settings = GatewaySettings(
        local_provider="ollama",
        local_base_url="http://localhost:11434",
        local_model="qwen3:8b",
    )
    gateway = ModelGateway(settings)
    provider = gateway.resolve("claim_extraction")
    assert isinstance(provider, OllamaProvider)
    assert provider.model_info().model == "qwen3:8b"


def test_fpt_requires_full_configuration():
    assert not FPTProvider(base_url="https://x/v1", api_key="", model="m").is_configured()
    assert FPTProvider(base_url="https://x/v1", api_key="k", model="m").is_configured()


class FakeProvider(LLMProvider):
    name = "fake"

    def generate(self, messages, response_schema=None):
        return LLMResponse(
            text='{"ok": true}',
            parsed={"ok": True} if response_schema else None,
            provider="fake",
            model="fake-1",
        )

    def healthcheck(self):
        return True

    def model_info(self):
        return ModelInfo(provider="fake", model="fake-1")


def test_gateway_fails_over_to_next_configured_provider():
    gateway = ModelGateway(EMPTY_KEYS)
    gateway._cache["fpt"] = FakeProvider()
    gateway.settings.fallback_order = ["local", "fpt"]
    response = gateway.generate(
        [{"role": "user", "content": "extract"}],
        response_schema={"type": "object"},
        task_type="claim_extraction",
    )
    assert response.provider == "fake"
    assert response.parsed == {"ok": True}
