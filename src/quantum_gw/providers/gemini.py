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

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str = "", model: str = "", timeout: float = 180.0, max_tokens: int = 4096):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.is_configured():
            raise ProviderUnavailableError("gemini: GEMINI_API_KEY/GEMINI_MODEL not configured")
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in messages
            if m["role"] != "system"
        ]
        if response_schema and contents:
            contents[-1]["parts"][0]["text"] += schema_instruction(response_schema)
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": 0, "maxOutputTokens": self.max_tokens},
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{GEMINI_BASE_URL}/models/{self.model}:generateContent",
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(f"gemini: {exc}") from exc
        content = body["candidates"][0]["content"]["parts"][0]["text"]
        return LLMResponse(
            text=content,
            parsed=extract_json(content) if response_schema else None,
            provider=self.name,
            model=self.model,
            usage=body.get("usageMetadata", {}),
        )

    def healthcheck(self) -> bool:
        if not self.is_configured():
            return False
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(
                    f"{GEMINI_BASE_URL}/models/{self.model}",
                    headers={"x-goog-api-key": self.api_key},
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    def model_info(self) -> ModelInfo:
        return ModelInfo(provider=self.name, model=self.model, endpoint=GEMINI_BASE_URL)
