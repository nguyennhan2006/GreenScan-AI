"""Trích liên kết từ HTML, kèm anchor text và ngữ cảnh dòng chứa nó."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..utils import canonical_url

_SKIP_PREFIXES = ("mailto:", "javascript:", "tel:", "#")


@dataclass
class Link:
    url: str
    text: str
    context: str = ""


def _row_context(anchor) -> str:
    """Text của <tr> hoặc <li> chứa anchor -- nơi thường có ngày, mã CK, loại báo cáo."""
    parent = anchor.find_parent(["tr", "li", "article"])
    if parent is None:
        return ""
    return " ".join(parent.stripped_strings)[:400]


def extract_links(page_url: str, html: str, selector: str = "a[href]") -> list[Link]:
    soup = BeautifulSoup(html, "lxml")
    links: list[Link] = []
    seen: set[str] = set()
    for anchor in soup.select(selector):
        href = (anchor.get("href") or "").strip()
        if not href or href.startswith(_SKIP_PREFIXES):
            continue
        absolute = canonical_url(urljoin(page_url, href))
        if absolute in seen:
            continue
        seen.add(absolute)
        text = " ".join(anchor.stripped_strings) or anchor.get("title", "") or ""
        links.append(Link(url=absolute, text=text, context=_row_context(anchor)))
    return links
