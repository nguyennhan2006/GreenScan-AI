"""Adapter cho finance.vietstock.vn.

CẢNH BÁO CALIBRATION
--------------------
Các selector và endpoint mặc định dưới đây CHƯA được đối chiếu với HTML thật
của Vietstock (môi trường phát triển hiện tại bị chặn TLS nên không truy cập
được ra ngoài). Cấu trúc adapter là đúng, nhưng selector phải được hiệu chỉnh
bằng HTML thật trước khi bật `enabled: true`. Quy trình:

    1. Lưu một trang listing thật vào tests/fixtures/vietstock_listing.html
    2. Chỉnh `adapter_options.row_selector` / `link_selector` cho khớp
    3. Chạy `pytest tests/test_adapters.py -k vietstock`
    4. Dry-run 20-50 tài liệu rồi mới bật production

Vietstock phục vụ PDF, Word và Excel nên đây là nguồn tốt để kiểm thử parser đa
định dạng; `allowed_file_types` mặc định gồm cả doc/docx/xls/xlsx.
"""

from __future__ import annotations

import httpx

from ..discovery.html_links import extract_links
from ..models import Candidate, PageLink
from ..pipeline.classifier import classify_report
from ..pipeline.validator import is_probably_attachment
from ..utils import domain_allowed, extract_ticker, extract_year
from .base import SourceAdapter

DEFAULT_ATTACHMENT_PATTERNS = [
    "/downloadfile",
    "/filedownload",
    "static.vietstock.vn",
    "/data/download",
]


class VietstockAdapter(SourceAdapter):
    name = "vietstock"

    def __init__(self, config, ctx):
        super().__init__(config, ctx)
        self.row_selector: str = self.options.get("row_selector", "table tr, .doc-item, li")
        self.link_selector: str = self.options.get("link_selector", "a[href]")
        self.pagination_selector: str | None = self.options.get("pagination_selector")
        self.attachment_patterns = list(
            {*self.cfg.attachment_patterns, *DEFAULT_ATTACHMENT_PATTERNS}
        )

    def parse_listing(
        self, page_url: str, response: httpx.Response
    ) -> tuple[list[Candidate], list[PageLink]]:
        candidates: list[Candidate] = []
        pages: list[PageLink] = []

        for link in extract_links(page_url, response.text, self.link_selector):
            # `context` là text của <tr>/<li> chứa link -- ở Vietstock, dòng này
            # thường chứa mã CK, loại tài liệu và kỳ báo cáo.
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
                        ticker=extract_ticker(link.text, link.context),
                        hints={"row_context": link.context},
                    )
                )
                continue

            if self.pagination_selector and self.looks_relevant(haystack):
                pages.append(PageLink(url=link.url))

        if self.pagination_selector:
            for link in extract_links(page_url, response.text, self.pagination_selector):
                if domain_allowed(link.url, self.cfg.allowed_domains):
                    pages.append(PageLink(url=link.url))

        return candidates, pages
