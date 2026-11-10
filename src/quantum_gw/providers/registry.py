from __future__ import annotations

import json

from quantum_gw.settings import GatewaySettings

from .anthropic import AnthropicProvider
from .base import LLMProvider
from .fpt import FPTProvider
from .gemini import GeminiProvider
from .local_openai import OpenAICompatibleProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider


def _build_local(settings: GatewaySettings) -> LLMProvider:
    if settings.local_provider == "ollama":
        return OllamaProvider(
            base_url=settings.local_base_url or "http://localhost:11434",
            model=settings.local_model or "qwen3:8b",
            timeout=settings.local_timeout_seconds,
        )
    return OpenAICompatibleProvider(
        base_url=settings.local_base_url,
        model=settings.local_model,
        api_key=settings.local_api_key,
        timeout=settings.local_timeout_seconds,
        max_tokens=settings.local_max_tokens,
        name="local",
    )


def _build_ollama(settings: GatewaySettings) -> LLMProvider:
    return OllamaProvider(
        base_url=settings.local_base_url if settings.local_provider == "ollama" else "http://localhost:11434",
        model=settings.local_model if settings.local_provider == "ollama" else "qwen3:8b",
        timeout=settings.local_timeout_seconds,
    )


PROVIDERS = {
    "local": _build_local,
    "ollama": _build_ollama,
    "fpt": lambda s: FPTProvider(
        base_url=s.fpt_base_url,
        api_key=s.fpt_api_key,
        model=s.fpt_model,
        api_format=s.fpt_api_format,
        timeout=s.fpt_timeout_seconds,
        max_tokens=s.fpt_max_tokens,
    ),
    "gemini": lambda s: GeminiProvider(api_key=s.gemini_api_key, model=s.gemini_model),
    "openai": lambda s: OpenAIProvider(api_key=s.openai_api_key, model=s.openai_model),
    "anthropic": lambda s: AnthropicProvider(api_key=s.anthropic_api_key, model=s.anthropic_model),
    "openrouter": lambda s: OpenRouterProvider(api_key=s.openrouter_api_key, model=s.openrouter_model),
    # Groq (US cloud, free tier may keep data): its own name so the runtime chip says "cloud", never "local:".
    "groq": lambda s: OpenAICompatibleProvider(
        base_url="https://api.groq.com/openai/v1",
        model=s.groq_model,
        api_key=s.groq_api_key,
        name="groq",
        require_api_key=True,
        # request fields differ per model (reasoning_effort, reasoning_format, response_format): chosen by
        # experiments/GROQ-PROBE/probe.py and set as JSON in GROQ_EXTRA_BODY
        extra_body=json.loads(s.groq_extra_body) if s.groq_extra_body.strip() else None,
    ),
}


def build_provider(name: str, settings: GatewaySettings) -> LLMProvider | None:
    factory = PROVIDERS.get(name)
    if factory is None:
        return None
    return factory(settings)
