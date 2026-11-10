from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ProviderUnavailableError(RuntimeError):
    """Raised when a provider cannot serve a request (not configured, offline, error)."""


class NoProviderAvailableError(RuntimeError):
    """Raised when every provider in the routing chain is unavailable."""


class ModelInfo(BaseModel):
    provider: str
    model: str
    endpoint: str | None = None
    mode: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    text: str
    parsed: dict[str, Any] | None = None
    provider: str
    model: str
    usage: dict[str, Any] = Field(default_factory=dict)


class LLMProvider(ABC):
    """Common interface every model backend must implement.

    Business modules must never talk to a concrete model API directly; they go
    through this interface so switching local/FPT/cloud never touches pipeline logic.
    """

    name: str = "base"

    @abstractmethod
    def generate(
        self, messages: list[dict[str, str]], response_schema: dict[str, Any] | None = None
    ) -> LLMResponse: ...

    def bind_model(self, model: str) -> LLMProvider:
        """Return this provider aimed at a different model on the same endpoint.

        One endpoint usually serves many models -- FPT Marketplace exposes a
        dozen behind a single base URL -- and tasks have genuinely different
        needs: claim extraction wants a fast small model, legal reasoning wants
        the strongest one available. Without this, every task on a provider is
        stuck with one model id.

        Providers that cannot switch models return themselves unchanged, so
        routing never fails because of an override it cannot honour.
        """
        return self

    @abstractmethod
    def healthcheck(self) -> bool: ...

    @abstractmethod
    def model_info(self) -> ModelInfo: ...

    def is_configured(self) -> bool:
        """True when required settings (endpoint/key/model) are present. Never does I/O."""
        return True


def schema_instruction(response_schema: dict[str, Any]) -> str:
    return (
        "\nReturn ONLY a JSON object matching this schema, no prose:\n"
        + json.dumps(response_schema, ensure_ascii=False)
    )


def extract_json(content: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
