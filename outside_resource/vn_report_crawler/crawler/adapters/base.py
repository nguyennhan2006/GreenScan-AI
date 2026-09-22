"""Giao diện adapter cho từng nguồn.

Adapter chỉ chịu trách nhiệm "site này tổ chức tài liệu như thế nào". Mọi thứ
dùng chung (robots, rate limit, MIME, checksum, provenance, storage, manifest)
nằm ở shared pipeline và adapter không được tự làm lại.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import httpx

from ..models import Candidate, PageLink, SourceConfig
from ..pipeline.classifier import classify_report, describe_document, excluded
from ..pipeline.downloader import Downloader
from ..policies.robots import RobotsGate
from ..utils import extract_year, filename_from_url, normalize_text

# Anchor text vô nghĩa -- khi gặp thì lấy text của cả dòng làm tiêu đề.
GENERIC_ANCHOR_TEXT = {
    "tải", "tải về", "tải file", "tai ve", "download", "xem", "xem chi tiết",
    "chi tiết", "link", "file", "pdf", "đọc tiếp", "xem tiếp",
}


@dataclass
class CrawlContext:
    downloader: Downloader
    robots: RobotsGate
    client: httpx.Client
    log: logging.Logger


class SourceAdapter(ABC):
    name: str = "base"

    def __init__(self, config: SourceConfig, ctx: CrawlContext):
        self.cfg = config
        self.ctx = ctx
        self.options: dict[str, Any] = dict(config.adapter_options)

    # ------------- các bước adapter phải/có thể cài đặt -------------

    def discover_pages(self) -> Iterator[str]:
        """URL điểm vào. Mặc định là start_urls trong config."""
        yield from self.cfg.start_urls

    @abstractmethod
    def parse_listing(
        self, page_url: str, response: httpx.Response
    ) -> tuple[list[Candidate], list[PageLink]]:
        """Tách một trang thành (danh sách attachment ứng viên, trang cần duyệt tiếp)."""

    def resolve_attachment(self, candidate: Candidate) -> str:
        """URL tải cuối cùng. Ghi đè nếu site cần bước trung gian."""
        return candidate.url

    def normalize_metadata(
        self, candidate: Candidate, response: httpx.Response, file_ext: str
    ) -> dict[str, Any]:
        """Metadata chuẩn hoá cho một tài liệu đã tải."""
        # row_context (text của cả dòng <tr>) mới là nơi chứa kỳ báo cáo, phạm vi
        # hợp nhất/riêng và trạng thái kiểm toán -- anchor text thường chỉ là "Tải".
        row_context = str(candidate.hints.get("row_context", ""))
        haystack = " ".join(
            [candidate.title, row_context, candidate.url, candidate.source_page_url]
        )
        described = describe_document(haystack)
        report_type = candidate.report_type or classify_report(haystack, self.cfg.report_types)
        return {
            "source_id": self.cfg.id,
            "adapter": self.name,
            "source_authority": self.cfg.authority.value,
            "company": self.cfg.company,
            "ticker": candidate.ticker or self.cfg.ticker,
            "report_type": report_type,
            "document_family": report_type,
            "statement_scope": described["statement_scope"],
            "period_type": described["period_type"],
            "assurance_status": described["assurance_status"],
            "title": candidate.title.strip() or filename_from_url(candidate.url),
            "year": candidate.year or extract_year(candidate.title, candidate.url),
            "source_page_url": candidate.source_page_url,
            "file_url": candidate.url,
            "canonical_source_url": candidate.canonical_source_url,
            "file_format": file_ext.lstrip("."),
            "metadata": {
                "http_status": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": len(response.content),
                "final_url": str(response.url),
                **candidate.hints,
            },
        }

    # ------------- tiện ích dùng chung -------------

    @staticmethod
    def best_title(anchor_text: str, row_context: str) -> str:
        """Chọn tiêu đề có nghĩa: anchor text nếu đủ mô tả, ngược lại lấy cả dòng."""
        cleaned = normalize_text(anchor_text)
        if not cleaned or cleaned in GENERIC_ANCHOR_TEXT or len(cleaned) < 8:
            return (row_context or anchor_text).strip()[:300]
        return anchor_text.strip()

    def is_excluded(self, text: str) -> bool:
        return excluded(text, self.cfg.exclude_patterns)

    def looks_relevant(self, text: str) -> bool:
        if self.is_excluded(text):
            return False
        return classify_report(text, self.cfg.report_types) is not None
