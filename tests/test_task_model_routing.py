"""Per-task model selection.

One provider endpoint hosts many models. Before `RoutingPolicy.models`, every
task on a provider shared a single model id, so claim extraction and legal
reasoning could not use different models on the same FPT account.
"""

import pytest
import yaml

from quantum_gw.providers.local_openai import OpenAICompatibleProvider
from quantum_gw.providers.router import ModelGateway, RoutingPolicy
from quantum_gw.settings import GatewaySettings


@pytest.fixture
def routing_file(tmp_path):
    p = tmp_path / "routing.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "routing": {
                    "claim_extraction": {
                        "primary": "fpt",
                        "fallback": "local",
                        "models": {"fpt": "Qwen3.6-27B", "local": "qwen3:8b"},
                    },
                    "legal_reasoning": {
                        "primary": "fpt",
                        "fallback": "local",
                        "models": {"fpt": "GLM-5.2"},
                    },
                    "no_override": {"primary": "fpt", "fallback": "none"},
                    "quantitative_verification": {
                        "primary": "deterministic",
                        "fallback": "none",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return p


@pytest.fixture
def gateway(routing_file):
    settings = GatewaySettings(
        provider="fpt",
        fallback_order=["fpt", "local"],
        routing_file=str(routing_file),
        local_base_url="http://localhost:8000/v1",
        local_model="Qwen/Qwen3-8B",
        fpt_base_url="https://mkp-api.fptcloud.com/v1",
        fpt_api_key="test-key",
        fpt_model="Qwen3.6-27B",
    )
    return ModelGateway(settings)


def test_task_selects_its_own_model(gateway):
    assert gateway.resolve("legal_reasoning").model_info().model == "GLM-5.2"
    assert gateway.resolve("claim_extraction").model_info().model == "Qwen3.6-27B"


def test_tasks_do_not_leak_models_into_each_other(gateway):
    gateway.resolve("legal_reasoning")
    assert gateway.resolve("claim_extraction").model_info().model == "Qwen3.6-27B"


def test_missing_override_falls_back_to_provider_default(gateway):
    assert gateway.resolve("no_override").model_info().model == "Qwen3.6-27B"


def test_deterministic_task_never_reaches_a_provider(gateway):
    assert "deterministic" not in gateway.provider_chain("quantitative_verification")


def test_bind_model_does_not_mutate_the_shared_provider():
    base = OpenAICompatibleProvider(base_url="https://x/v1", model="a", api_key="k")
    bound = base.bind_model("b")
    assert bound.model == "b"
    assert base.model == "a", "binding must not mutate the cached provider"


def test_bind_model_preserves_credentials_and_endpoint():
    base = OpenAICompatibleProvider(base_url="https://x/v1", model="a", api_key="k")
    bound = base.bind_model("b")
    assert bound.api_key == "k"
    assert bound.base_url == "https://x/v1"
    assert bound.is_configured()


def test_empty_or_identical_override_returns_same_instance():
    base = OpenAICompatibleProvider(base_url="https://x/v1", model="a")
    assert base.bind_model("") is base
    assert base.bind_model("a") is base


def test_policy_without_models_defaults_to_empty():
    assert RoutingPolicy(primary="fpt").models == {}


def test_deterministic_task_has_an_empty_provider_chain(gateway):
    """`primary: deterministic, fallback: none` must not fall through to the
    global fallback order. Arithmetic verification is Python's job by design;
    letting an LLM answer it defeats the guarantee the config states."""
    assert gateway.provider_chain("quantitative_verification") == []
    assert gateway.resolve("quantitative_verification") is None


def test_explicit_none_fallback_stops_the_chain(gateway):
    """`fallback: none` means fail fast, not 'continue down the global list'."""
    assert gateway.provider_chain("no_override") == ["fpt"]


def test_normal_task_still_uses_the_global_fallback_order(gateway):
    chain = gateway.provider_chain("claim_extraction")
    assert chain[0] == "fpt"
    assert "local" in chain
