"""YAML phải fail sớm và rõ ràng, không nổ TypeError giữa lúc crawl."""

from __future__ import annotations

from pathlib import Path

import pytest

from crawler.config import ConfigError, load_config

CONFIGS = Path(__file__).resolve().parents[1] / "configs"


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "c.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_shipped_configs_are_valid():
    for path in CONFIGS.glob("*.yml"):
        assert load_config(path).sources, f"{path} không có source nào"


def test_shipped_aggregators_are_disabled():
    """Không nguồn tổng hợp nào được bật sẵn khi chưa qua checklist."""
    config = load_config(CONFIGS / "aggregators.yml")
    assert all(not s.enabled for s in config.sources)


def test_defaults_are_merged(tmp_path):
    path = write(tmp_path, """
defaults:
  delay_seconds: 5.0
  allowed_domains: [a.test]
sources:
  - id: one
    start_urls: [http://a.test/]
  - id: two
    start_urls: [http://a.test/]
    delay_seconds: 1.0
""")
    sources = load_config(path).sources
    assert sources[0].delay_seconds == 5.0
    assert sources[1].delay_seconds == 1.0
    assert sources[0].allowed_domains == ["a.test"]


def test_unknown_key_is_rejected(tmp_path):
    path = write(tmp_path, """
sources:
  - id: one
    start_urls: [http://a.test/]
    typo_field: oops
""")
    with pytest.raises(ConfigError) as exc:
        load_config(path)
    assert "typo_field" in str(exc.value)


def test_duplicate_ids_rejected(tmp_path):
    path = write(tmp_path, """
sources:
  - id: dup
    start_urls: [http://a.test/]
  - id: dup
    start_urls: [http://b.test/]
""")
    with pytest.raises(ConfigError, match="trùng source id"):
        load_config(path)


def test_bad_authority_rejected(tmp_path):
    path = write(tmp_path, """
sources:
  - id: one
    authority: super_official
    start_urls: [http://a.test/]
""")
    with pytest.raises(ConfigError):
        load_config(path)


def test_bad_robots_policy_rejected(tmp_path):
    path = write(tmp_path, """
sources:
  - id: one
    start_urls: [http://a.test/]
    robots_policy:
      on_temporary_error: ignore_everything
""")
    with pytest.raises(ConfigError):
        load_config(path)


def test_file_types_normalized(tmp_path):
    path = write(tmp_path, """
sources:
  - id: one
    start_urls: [http://a.test/]
    allowed_file_types: ['.PDF', 'XLSX']
    allowed_domains: ['A.TEST']
""")
    source = load_config(path).sources[0]
    assert source.allowed_file_types == ["pdf", "xlsx"]
    assert source.allowed_domains == ["a.test"]
