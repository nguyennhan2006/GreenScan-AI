"""Adapter cho cafef.vn (trang công bố thông tin và tài liệu theo mã chứng khoán).

CẢNH BÁO CALIBRATION
--------------------
Giống VietstockAdapter: selector mặc định CHƯA đối chiếu với HTML thật. Phải
hiệu chỉnh bằng fixture HTML thật trước khi bật `enabled: true`.

PROVENANCE
----------
CafeF ghi rõ dữ liệu tổng hợp chỉ có giá trị tham khảo. Vì vậy adapter này đặt
`authority: aggregator` và luôn cố gắng điền `canonical_source_url` trỏ về nguồn
công bố gốc khi trang có link đó. Bước indexing về sau nên ưu tiên canonical
source thay vì bản mirror của CafeF.
"""

from __future__ import annotations

import re

import httpx

from ..discovery.html_links import extract_links
from ..models import Candidate, PageLink
from ..pipeline.classifier import classify_report
from ..pipeline.validator import is_probably_attachment
from ..utils import domain_allowed, extract_ticker, extract_year
from .base import SourceAdapter

DEFAULT_ATTACHMENT_PATTERNS = [
    "cafef1.mediacdn.vn",
    "cafefcdn.com",
    "/download.chn",
    "/tai-file",
]

# CafeF đặt mã CK trong URL kiểu /du-lieu/hose/HPG-cong-ty-....chn
_TICKER_IN_URL = re.compile(r"/(?:hose|hnx|upcom)/([a-z0-9]{3})[-.]", re.IGNORECASE)


class CafeFAdapter(SourceAdapter):
    name = "cafef"

    def __init__(self, config, ctx):
        super().__init__(config, ctx)
        self.link_selector: str = self.options.get("link_selector", "a[href]")
        self.follow_ticker_pages: bool = self.options.get("follow_ticker_pages", True)
        self.attachment_patterns = list(
            {*self.cfg.attachment_patterns, *DEFAULT_ATTACHMENT_PATTERNS}
        )

    def _ticker_from(self, *values: str) -> str | None:
        for value in values:
            match = _TICKER_IN_URL.search(value or "")
            if match:
                return match.group(1).upper()
        return extract_ticker(*values)

    def parse_listing(
        self, page_url: str, response: httpx.Response
    ) -> tuple[list[Candidate], list[PageLink]]:
        candidates: list[Candidate] = []
        pages: list[PageLink] = []

        for link in extract_links(page_url, response.text, self.link_selector):
            haystack = f"{link.text} {link.context} {link.url}"
            if self.is_excluded(haystack):
                continue
            if not domain_allowed(link.url, self.cfg.allowed_domains):
                continue

            if is_probably_attachment(link.url, self.attachment_patterns):
                candidates.append(
                    Candidate(
                        url=link.url,
                        title=self.best_title(link.text, link.context),
                        source_page_url=page_url,
                        report_type=classify_report(haystack, self.cfg.report_types),
                        year=extract_year(link.context, link.text, link.url),
                        ticker=self._ticker_from(link.url, link.context, link.text),
                        # CafeF là aggregator; trang chứa link chính là mốc provenance
                        # gần nhất mà ta biết cho tới khi resolve được nguồn gốc.
                        canonical_source_url=None,
                        hints={"row_context": link.context, "mirror_of": "cafef"},
                    )
                )
                continue

            if self.follow_ticker_pages and self.looks_relevant(haystack):
                pages.append(PageLink(url=link.url))

        return candidates, pages
