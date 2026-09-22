"""Giải quyết URL tải file khi nó không phải link .pdf trực tiếp.

Xử lý các dạng: redirect 302, download handler .ashx, query-string ?file=,
và trang xem trước nhúng iframe/embed trỏ tới file thật.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

_EMBED_SELECTORS = (
    "iframe[src]",
    "embed[src]",
    "object[data]",
    "a[href$='.pdf']",
)


def _attr_of(node) -> str | None:
    for attr in ("src", "data", "href"):
        value = node.get(attr)
        if value:
            return value
    return None


def resolve_attachment_url(response: httpx.Response) -> str | None:
    """Nếu response là trang HTML xem trước, trả về URL file nhúng bên trong."""
    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type:
        return None

    soup = BeautifulSoup(response.text, "lxml")
    for selector in _EMBED_SELECTORS:
        node = soup.select_one(selector)
        if node is None:
            continue
        raw = _attr_of(node)
        if not raw:
            continue
        resolved = urljoin(str(response.url), raw)
        log.debug("Giải quyết attachment nhúng: %s -> %s", response.url, resolved)
        return resolved
    return None
