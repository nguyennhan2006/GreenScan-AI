"""Model gateway: every LLM call goes through the LLMProvider interface.

Business modules must never import a concrete provider; use ModelGateway.
"""

from .base import (
    LLMProvider,
    LLMResponse,
    ModelInfo,
    NoProviderAvailableError,
    ProviderUnavailableError,
)
from .registry import PROVIDERS, build_provider
from .router import ModelGateway, RoutingPolicy

__all__ = [
    "PROVIDERS",
    "LLMProvider",
    "LLMResponse",
    "ModelGateway",
    "ModelInfo",
    "NoProviderAvailableError",
    "ProviderUnavailableError",
    "RoutingPolicy",
    "build_provider",
]
