from __future__ import annotations

from .local_openai import OpenAICompatibleProvider

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"

    def __init__(self, api_key: str = "", model: str = "", timeout: float = 180.0, max_tokens: int = 4096):
        super().__init__(
            base_url=OPENROUTER_BASE_URL,
            model=model,
            api_key=api_key,
            timeout=timeout,
            max_tokens=max_tokens,
            name="openrouter",
            require_api_key=True,
        )
