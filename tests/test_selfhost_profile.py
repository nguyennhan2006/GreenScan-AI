"""Phương án 2: the selfhost profile points the local OpenAI-compatible provider at a rented GPU; offline is untouched."""
import os

import pytest

from quantum_gw.settings import PROFILES, apply_profile

KEYS = set(PROFILES["selfhost"]) | {"LOCAL_LLM_BASE_URL", "LOCAL_LLM_API_KEY", "LOCAL_LLM_MODEL",
                                    "QUANTUM_SELFHOST_URL", "QUANTUM_SELFHOST_KEY", "QUANTUM_SELFHOST_MODEL"}


@pytest.fixture
def clean(monkeypatch):
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


def test_selfhost_maps_its_three_variables(clean):
    clean.setenv("QUANTUM_SELFHOST_URL", "http://203.0.113.7:8001/v1")
    clean.setenv("QUANTUM_SELFHOST_KEY", "k-test")
    assert apply_profile("selfhost") == "selfhost"
    assert os.environ["LOCAL_LLM_BASE_URL"] == "http://203.0.113.7:8001/v1"
    assert os.environ["LOCAL_LLM_API_KEY"] == "k-test"
    assert os.environ["LOCAL_LLM_MODEL"] == "openai/gpt-oss-120b"     # default served name: large-family prompts
    assert os.environ["LLM_PROVIDER"] == "local" and os.environ["LOCAL_LLM_PROVIDER"] == "openai_compatible"
    assert os.environ["EMBEDDING_PROVIDER"] == "lite"                 # retrieval stays on the laptop


def test_selfhost_without_url_fails_loudly(clean):
    with pytest.raises(ValueError, match="QUANTUM_SELFHOST_URL"):
        apply_profile("selfhost")


def test_offline_profile_unchanged():
    assert PROFILES["offline"] == {"QUANTUM_LLM_STANCE": "off", "EMBEDDING_PROVIDER": "lite",
                                   "RERANKER_PROVIDER": "none", "LOCAL_LLM_BASE_URL": ""}
