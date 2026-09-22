"""Adapter mặc định: duyệt BFS trang HTML, lấy link đính kèm.

Dùng cho website chính thức của doanh nghiệp, nơi tài liệu là link trực tiếp
trong trang quan hệ cổ đông.
"""

from __future__ import annotations

import httpx

from ..discovery.html_links import extract_links
from ..models import Candidate, PageLink
from ..pipeline.classifier import classify_report
from ..pipeline.validator import is_probably_attachment
from ..utils import domain_allowed, extract_year
from .base import SourceAdapter


class GenericHtmlAdapter(SourceAdapter):
    name = "generic_html"

    def parse_listing(
        self, page_url: str, response: httpx.Response
    ) -> tuple[list[Candidate], list[PageLink]]:
        candidates: list[Candidate] = []
        pages: list[PageLink] = []

        for link in extract_links(page_url, response.text):
            haystack = f"{link.text} {link.context} {link.url}"
            if self.is_excluded(haystack):
                continue
            if not domain_allowed(link.url, self.cfg.allowed_domains):
                continue

            if is_probably_attachment(link.url, self.cfg.attachment_patterns):
                candidates.append(
                    Candidate(
                        url=link.url,
                        title=self.best_title(link.text, link.context),
                        source_page_url=page_url,
                        report_type=classify_report(haystack, self.cfg.report_types),
                        year=extract_year(link.text, link.url, link.context),
                        hints={"row_context": link.context},
                    )
                )
                continue

            if self.looks_relevant(haystack):
                pages.append(PageLink(url=link.url))

        return candidates, pages
