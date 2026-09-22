"""Pydantic models cho cấu hình nguồn và các bản ghi trong pipeline."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrawlStatus(str, Enum):
    DISCOVERED = "discovered"
    DOWNLOADED = "downloaded"
    DUPLICATE = "duplicate"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    ROBOTS_DENIED = "robots_denied"
    TEMPORARY_ERROR = "temporary_error"
    INVALID_DOCUMENT = "invalid_document"
    UNSUPPORTED_TYPE = "unsupported_type"


class SourceAuthority(str, Enum):
    """Thứ bậc tin cậy, dùng để chọn canonical source khi có duplicate cross-source."""

    OFFICIAL_EXCHANGE = "official_exchange"
    OFFICIAL_COMPANY = "official_company"
    AGGREGATOR = "aggregator"
    MIRROR = "mirror"


AUTHORITY_SCORE: dict[SourceAuthority, int] = {
    SourceAuthority.OFFICIAL_EXCHANGE: 100,
    SourceAuthority.OFFICIAL_COMPANY: 80,
    SourceAuthority.AGGREGATOR: 50,
    SourceAuthority.MIRROR: 30,
}


class RobotsPolicy(BaseModel):
    """Quyết định phải làm gì khi robots.txt thiếu hoặc không tải được.

    Mặc định thận trọng: thiếu robots.txt thì cho phép (đúng chuẩn RFC 9309),
    còn lỗi tạm thời thì thử lại rồi bỏ qua nguồn -- KHÔNG âm thầm coi lỗi
    mạng là lệnh cấm vĩnh viễn như hành vi của urllib.robotparser.
    """

    model_config = ConfigDict(extra="forbid")

    on_missing: Literal["allow", "deny"] = "allow"
    on_temporary_error: Literal["allow", "skip_source", "retry_then_skip"] = "retry_then_skip"
    retry_attempts: int = Field(default=2, ge=1, le=5)
    cache_ttl_seconds: int = Field(default=3600, ge=0)


class SourceConfig(BaseModel):
    """Một nguồn crawl. YAML chỉ giữ policy và điểm vào; selector chi tiết nằm trong adapter."""

    model_config = ConfigDict(extra="forbid")

    id: str
    adapter: str = "generic_html"
    company: str | None = None
    ticker: str | None = None
    authority: SourceAuthority = SourceAuthority.AGGREGATOR
    enabled: bool = False

    start_urls: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)
    allowed_file_types: list[str] = Field(default_factory=lambda: ["pdf"])

    report_types: dict[str, list[str]] = Field(default_factory=dict)
    exclude_patterns: list[str] = Field(default_factory=list)
    attachment_patterns: list[str] = Field(default_factory=list)

    tickers: list[str] = Field(default_factory=list)
    # Tuỳ chọn riêng của từng adapter (selector, endpoint API, tham số phân trang).
    # Để ở đây thay vì nhồi selector vào schema chung.
    adapter_options: dict[str, Any] = Field(default_factory=dict)
    max_depth: int = Field(default=2, ge=0, le=6)
    max_documents: int | None = Field(default=None, ge=1)

    delay_seconds: float = Field(default=2.0, ge=0)
    max_requests_per_minute: int | None = Field(default=None, ge=1)
    user_agent: str = "VNReportResearchBot/0.2 (+contact: research@example.org)"
    verify_ssl: bool = True
    robots_policy: RobotsPolicy = Field(default_factory=RobotsPolicy)

    @field_validator("allowed_file_types", mode="after")
    @classmethod
    def _normalize_types(cls, value: list[str]) -> list[str]:
        return [v.lower().lstrip(".") for v in value]

    @field_validator("allowed_domains", mode="after")
    @classmethod
    def _normalize_domains(cls, value: list[str]) -> list[str]:
        return [v.lower().strip() for v in value]


class CrawlConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources: list[SourceConfig] = Field(default_factory=list)
    defaults: dict[str, Any] = Field(default_factory=dict)


class Candidate(BaseModel):
    """Một attachment ứng viên, phát hiện được nhưng chưa tải."""

    model_config = ConfigDict(extra="forbid")

    url: str
    title: str = ""
    source_page_url: str = ""
    report_type: str | None = None
    year: int | None = None
    ticker: str | None = None
    canonical_source_url: str | None = None
    hints: dict[str, Any] = Field(default_factory=dict)


class PageLink(BaseModel):
    """Trang HTML cần duyệt tiếp."""

    model_config = ConfigDict(extra="forbid")

    url: str
    depth_delta: int = 1
