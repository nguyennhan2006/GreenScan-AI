from __future__ import annotations

from typing import Any

from .base import LLMProvider, LLMResponse, ModelInfo, ProviderUnavailableError
from .local_openai import OpenAICompatibleProvider


class FPTProvider(LLMProvider):
    """FPT Marketplace adapter — the first-priority cloud provider when a key exists.

    Two API formats are supported:
    - ``openai_compatible``: delegates to the shared OpenAI-compatible client.
    - ``fpt_native``: reserved. Public endpoint/schema documentation was not
      available when this adapter was written; finish ``_generate_native``
      from the official account documentation without touching the pipeline.
    """

    name = "fpt"

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
        api_format: str = "openai_compatible",
        timeout: float = 180.0,
        max_tokens: int = 4096,
    ):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.api_key = api_key
        self.model = model
        self.api_format = api_format
        self._delegate = OpenAICompatibleProvider(
            base_url=self.base_url,
            model=model,
            api_key=api_key,
            timeout=timeout,
            max_tokens=max_tokens,
            name="fpt",
            require_api_key=True,
        )

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        if not self.is_configured():
            raise ProviderUnavailableError("fpt: FPT_LLM_BASE_URL/API_KEY/MODEL not configured")
        if self.api_format == "openai_compatible":
            return self._delegate.generate(messages, response_schema)
        return self._generate_native(messages, response_schema)

    def _generate_native(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse:
        raise ProviderUnavailableError(
            "fpt: fpt_native format is not implemented yet. Set FPT_LLM_API_FORMAT=openai_compatible "
            "or implement _generate_native from the official FPT Marketplace API documentation."
        )

    def healthcheck(self) -> bool:
        if not self.is_configured():
            return False
        if self.api_format == "openai_compatible":
            return self._delegate.healthcheck()
        return False

    def model_info(self) -> ModelInfo:
        return ModelInfo(
            provider=self.name,
            model=self.model,
            endpoint=self.base_url,
            extra={"api_format": self.api_format},
        )
