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


class OpenAICompatibleProvider(LLMProvider):
    """Adapter for any endpoint speaking the OpenAI chat-completions dialect.

    Covers vLLM (`vllm serve Qwen/Qwen3-8B`), FPT Marketplace in
    openai_compatible mode, OpenRouter and OpenAI itself. The API key is
    optional because local vLLM does not require one.
    """

    name = "local"

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout: float = 180.0,
        max_tokens: int = 4096,
        name: str | None = None,
        require_api_key: bool = False,
        extra_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.require_api_key = require_api_key
        self.extra_headers = extra_headers or {}
        if name:
            self.name = name

    def is_configured(self) -> bool:
        if not self.base_url or not self.model:
            return False
        if self.require_api_key and not self.api_key:
            return False
        return True

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.is_configured():
            raise ProviderUnavailableError(f"{self.name}: base URL/model/API key not configured")
        payload_messages = [dict(m) for m in messages]
        if response_schema and payload_messages:
            payload_messages[-1]["content"] += schema_instruction(response_schema)
        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": self.max_tokens,
            "messages": payload_messages,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions", headers=self._headers(), json=payload
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(f"{self.name}: {exc}") from exc
        content = body["choices"][0]["message"]["content"]
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
                response = client.get(f"{self.base_url}/models", headers=self._headers())
                return response.status_code < 500
        except httpx.HTTPError:
            return False

    def model_info(self) -> ModelInfo:
        return ModelInfo(provider=self.name, model=self.model, endpoint=self.base_url)
