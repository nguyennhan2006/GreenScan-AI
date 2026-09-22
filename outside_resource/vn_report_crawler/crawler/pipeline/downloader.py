"""Tải nội dung với retry CÓ ĐIỀU KIỆN.

Bản cũ retry mọi exception ba lần, nên một URL 404 vẫn bị gọi lại ba lần và in
full traceback. Ở đây chỉ retry lỗi transport và các mã HTTP có khả năng phục
hồi; 4xx còn lại fail ngay.
"""

from __future__ import annotations

import logging

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from ..policies.rate_limit import RateLimiter

log = logging.getLogger(__name__)

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


def retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS
    return False


@retry(
    retry=retry_if_exception(retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def fetch(client: httpx.Client, url: str) -> httpx.Response:
    response = client.get(url)
    response.raise_for_status()
    return response


class Downloader:
    """Bọc fetch() với rate limiter dùng chung cho một nguồn."""

    def __init__(self, client: httpx.Client, limiter: RateLimiter):
        self.client = client
        self.limiter = limiter

    def get(self, url: str) -> httpx.Response:
        self.limiter.acquire()
        return fetch(self.client, url)


def status_of(exc: BaseException) -> int | None:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code
    return None
