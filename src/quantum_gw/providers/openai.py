from __future__ import annotations

from .local_openai import OpenAICompatibleProvider

OPENAI_BASE_URL = "https://api.openai.com/v1"


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"

    def __init__(self, api_key: str = "", model: str = "", timeout: float = 180.0, max_tokens: int = 4096):
        super().__init__(
            base_url=OPENAI_BASE_URL,
            model=model,
            api_key=api_key,
            timeout=timeout,
            max_tokens=max_tokens,
            name="openai",
            require_api_key=True,
        )
