from __future__ import annotations

from typing import Any

import httpx

from .base import (
    LLMProvider,
    LLMResponse,
    ModelInfo,
    ProviderUnavailableError,
    extract_json,
    schema_instruction,
)


class OllamaProvider(LLMProvider):
    """Native Ollama adapter for personal machines and development.

    Ollama exposes a local API by default, so the repository can connect
    without any cloud key (`LOCAL_LLM_PROVIDER=ollama`).
    """

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3:8b", timeout: float = 180.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.base_url and self.model)

    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.is_configured():
            raise ProviderUnavailableError("ollama: base URL/model not configured")
        payload_messages = [dict(m) for m in messages]
        if response_schema and payload_messages:
            payload_messages[-1]["content"] += schema_instruction(response_schema)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": payload_messages,
            "stream": False,
            "options": {"temperature": 0},
        }
        if response_schema:
            payload["format"] = "json"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(f"ollama: {exc}") from exc
        content = body["message"]["content"]
        return LLMResponse(
            text=content,
            parsed=extract_json(content) if response_schema else None,
            provider=self.name,
            model=self.model,
            usage={
                "prompt_tokens": body.get("prompt_eval_count"),
                "completion_tokens": body.get("eval_count"),
            },
        )

    def healthcheck(self) -> bool:
        if not self.is_configured():
            return False
        try:
            with httpx.Client(timeout=5) as client:
                return client.get(f"{self.base_url}/api/tags").status_code == 200
        except httpx.HTTPError:
            return False

    def model_info(self) -> ModelInfo:
        return ModelInfo(provider=self.name, model=self.model, endpoint=self.base_url)
