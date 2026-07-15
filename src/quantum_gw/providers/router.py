from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from quantum_gw.settings import GatewaySettings, load_gateway_settings

from .base import LLMProvider, LLMResponse, NoProviderAvailableError, ProviderUnavailableError
from .registry import build_provider

# Task targets that never reach an LLM provider.
NON_LLM_TARGETS = {"none", "deterministic"}


class RoutingPolicy(BaseModel):
    primary: str = "local"
    fallback: str = "none"


class ModelGateway:
    """Single entry point for every LLM call in the system.

    Modules ask for a *task type*; the gateway resolves the provider chain from
    the routing policy plus the global fallback order, skips providers that are
    not configured, and fails over on transport errors. With every cloud key
    empty the gateway simply reports no providers — the deterministic pipeline
    keeps working.
    """

    def __init__(self, settings: GatewaySettings | None = None):
        self.settings = settings or load_gateway_settings()
        self.routing = self._load_routing(self.settings.routing_file)
        self._cache: dict[str, LLMProvider | None] = {}

    @staticmethod
    def _load_routing(routing_file: str) -> dict[str, RoutingPolicy]:
        path = Path(routing_file)
        if not path.exists():
            alternative = Path(__file__).resolve().parents[3] / routing_file
            if alternative.exists():
                path = alternative
            else:
                return {}
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return {
            task: RoutingPolicy.model_validate(policy)
            for task, policy in (raw.get("routing") or {}).items()
        }

    def _provider(self, name: str) -> LLMProvider | None:
        if name not in self._cache:
            self._cache[name] = build_provider(name, self.settings)
        return self._cache[name]

    def provider_chain(self, task_type: str | None = None) -> list[str]:
        chain: list[str] = []
        policy = self.routing.get(task_type or "")
        if policy:
            chain.extend([policy.primary, policy.fallback])
        else:
            chain.append(self.settings.provider)
        chain.extend(self.settings.fallback_order)
        seen: set[str] = set()
        ordered = []
        for name in chain:
            key = (name or "").strip()
            if not key or key in seen or key in NON_LLM_TARGETS:
                continue
            seen.add(key)
            ordered.append(key)
        return ordered

    def resolve(self, task_type: str | None = None) -> LLMProvider | None:
        """First *configured* provider in the chain, or None when keys are empty."""
        for name in self.provider_chain(task_type):
            provider = self._provider(name)
            if provider is not None and provider.is_configured():
                return provider
        return None

    def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict[str, Any] | None = None,
        task_type: str | None = None,
    ) -> LLMResponse:
        errors: list[str] = []
        for name in self.provider_chain(task_type):
            provider = self._provider(name)
            if provider is None or not provider.is_configured():
                continue
            try:
                return provider.generate(messages, response_schema)
            except ProviderUnavailableError as exc:
                errors.append(str(exc))
        raise NoProviderAvailableError(
            "No LLM provider could serve the request"
            + (f" (task={task_type})" if task_type else "")
            + (": " + "; ".join(errors) if errors else " — all providers unconfigured")
        )

    def describe(self) -> dict[str, dict[str, Any]]:
        """Configuration report without any network I/O."""
        report: dict[str, dict[str, Any]] = {}
        for name in self.provider_chain():
            provider = self._provider(name)
            if provider is None:
                continue
            configured = provider.is_configured()
            info = provider.model_info()
            report[name] = {
                "configured": configured,
                "model": info.model or None,
                "endpoint": info.endpoint,
            }
        return report

    def healthcheck(self) -> dict[str, dict[str, Any]]:
        report: dict[str, dict[str, Any]] = {}
        for name in self.provider_chain():
            provider = self._provider(name)
            if provider is None:
                continue
            configured = provider.is_configured()
            report[name] = {
                "configured": configured,
                "healthy": provider.healthcheck() if configured else False,
                "model": provider.model_info().model if configured else None,
            }
        return report
