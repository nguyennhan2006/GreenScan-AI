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

ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str = "", model: str = "", timeout: float = 180.0, max_tokens: int = 4096):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.is_configured():
            raise ProviderUnavailableError("anthropic: ANTHROPIC_API_KEY/ANTHROPIC_MODEL not configured")
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        chat = [dict(m) for m in messages if m["role"] != "system"]
        if response_schema and chat:
            chat[-1]["content"] += schema_instruction(response_schema)
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "messages": chat,
        }
        if system_parts:
            payload["system"] = "\n".join(system_parts)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{ANTHROPIC_BASE_URL}/messages", headers=self._headers(), json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(f"anthropic: {exc}") from exc
        content = "".join(block.get("text", "") for block in body.get("content", []))
        return LLMResponse(
            text=content,
            parsed=extract_json(content) if response_schema else None,
            provider=self.name,
            model=self.model,
            usage=body.get("usage", {}),
        )

    def healthcheck(self) -> bool:
        if not self.is_configured():
            return False
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{ANTHROPIC_BASE_URL}/models/{self.model}", headers=self._headers())
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    def model_info(self) -> ModelInfo:
        return ModelInfo(provider=self.name, model=self.model, endpoint=ANTHROPIC_BASE_URL)
