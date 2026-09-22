"""Nạp và validate cấu hình nguồn từ YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import CrawlConfig, SourceConfig


class ConfigError(ValueError):
    """YAML sai schema. Ném lỗi sớm thay vì để TypeError xảy ra lúc chạy."""


def _merge_defaults(defaults: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    merged.update(item)
    return merged


def load_config(path: Path) -> CrawlConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: cấu hình phải là mapping ở cấp cao nhất")

    defaults = raw.get("defaults") or {}
    items = raw.get("sources") or []
    if not isinstance(items, list):
        raise ConfigError(f"{path}: 'sources' phải là list")

    sources: list[SourceConfig] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ConfigError(f"{path}: sources[{index}] phải là mapping")
        try:
            sources.append(SourceConfig(**_merge_defaults(defaults, item)))
        except ValidationError as exc:
            source_id = item.get("id", f"index {index}")
            raise ConfigError(f"{path}: source '{source_id}' không hợp lệ:\n{exc}") from exc

    ids = [s.id for s in sources]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ConfigError(f"{path}: trùng source id: {sorted(duplicates)}")

    return CrawlConfig(sources=sources, defaults=defaults)


def load_sources(path: Path) -> list[SourceConfig]:
    return load_config(path).sources
