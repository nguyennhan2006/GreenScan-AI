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


def _dedupe(chain: list[str]) -> list[str]:
    """Ordered, unique, with non-LLM targets removed."""
    seen: set[str] = set()
    ordered: list[str] = []
    for name in chain:
        key = (name or "").strip()
        if not key or key in seen or key in NON_LLM_TARGETS:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


class RoutingPolicy(BaseModel):
    primary: str = "local"
    fallback: str = "none"
    # Per-task model choice, keyed by provider name:
    #   models: {fpt: GLM-5.2, local: qwen3:8b}
    # A provider endpoint typically hosts many models, and tasks differ enough
    # that one model id per provider is the wrong granularity. Keyed by provider
    # so a fallback hop still uses a model that provider actually serves.
    models: dict[str, str] = {}


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
            # A policy naming only non-LLM targets is a hard boundary, not a
            # preference. `quantitative_verification` is deterministic/none
            # precisely so a language model can never arbitrate arithmetic;
            # appending the global fallback order would hand it to one anyway.
            if policy.primary in NON_LLM_TARGETS and policy.fallback in NON_LLM_TARGETS:
                return []
            chain.extend([policy.primary, policy.fallback])
            # An explicit `fallback: none` means stop here, not "carry on down
            # the global chain".
            if policy.fallback == "none":
                return _dedupe(chain)
        else:
            chain.append(self.settings.provider)
        chain.extend(self.settings.fallback_order)
        return _dedupe(chain)

    def _for_task(self, name: str, task_type: str | None) -> LLMProvider | None:
        """Provider `name`, aimed at whatever model this task asks it for."""
        provider = self._provider(name)
        if provider is None:
            return None
        policy = self.routing.get(task_type or "")
        override = (policy.models or {}).get(name) if policy else None
        return provider.bind_model(override) if override else provider

    def resolve(self, task_type: str | None = None) -> LLMProvider | None:
        """First *configured* provider in the chain, or None when keys are empty."""
        for name in self.provider_chain(task_type):
            provider = self._for_task(name, task_type)
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
            provider = self._for_task(name, task_type)
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
