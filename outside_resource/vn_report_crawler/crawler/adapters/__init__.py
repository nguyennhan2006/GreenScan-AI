"""Registry adapter. Sprint 3-5 sẽ bổ sung stockbiz / money24h / hnx / vlca."""

from __future__ import annotations

from .base import CrawlContext, SourceAdapter
from .cafef import CafeFAdapter
from .generic_html import GenericHtmlAdapter
from .vietstock import VietstockAdapter

ADAPTERS: dict[str, type[SourceAdapter]] = {
    GenericHtmlAdapter.name: GenericHtmlAdapter,
    VietstockAdapter.name: VietstockAdapter,
    CafeFAdapter.name: CafeFAdapter,
}


def get_adapter(name: str) -> type[SourceAdapter]:
    try:
        return ADAPTERS[name]
    except KeyError:
        raise ValueError(
            f"Adapter '{name}' chưa được cài đặt. Có sẵn: {sorted(ADAPTERS)}"
        ) from None


__all__ = [
    "ADAPTERS",
    "CafeFAdapter",
    "CrawlContext",
    "GenericHtmlAdapter",
    "SourceAdapter",
    "VietstockAdapter",
    "get_adapter",
]
