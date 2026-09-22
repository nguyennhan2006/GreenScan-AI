"""Robots.txt loader dùng chung httpx.Client với phần còn lại của crawler.

`urllib.robotparser.RobotFileParser.read()` tự mở kết nối bằng urllib nên KHÔNG
dùng chung proxy / SSL setting / timeout / user-agent của crawler. Tệ hơn, khi
read() thất bại vì lỗi mạng, đối tượng parser giữ nguyên `last_checked == 0` và
`can_fetch()` trả về False cho mọi URL -- tức là một lỗi TLS thoáng qua sẽ âm
thầm loại bỏ toàn bộ website. Module này tách bạch ba trạng thái (loaded /
missing / temporary_error) để caller quyết định theo policy.
"""

from __future__ import annotations

import logging
import time
import urllib.robotparser
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from ..models import RobotsPolicy

log = logging.getLogger(__name__)


@dataclass
class RobotsResult:
    parser: urllib.robotparser.RobotFileParser | None
    status: str  # loaded | missing | temporary_error
    detail: str | None = None
    fetched_at: float = 0.0


def robots_url_for(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def load_robots(client: httpx.Client, url: str) -> RobotsResult:
    """Tải robots.txt một lần. Không raise; luôn trả về RobotsResult."""
    target = robots_url_for(url)
    try:
        response = client.get(target)

        # 404/410: không có robots.txt -> theo RFC 9309 là cho phép toàn bộ.
        if response.status_code in (404, 410):
            return RobotsResult(None, "missing", "robots.txt not found", time.time())

        # 401/403: truy cập bị từ chối -> theo RFC 9309 là cấm toàn bộ.
        if response.status_code in (401, 403):
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(target)
            parser.disallow_all = True
            return RobotsResult(parser, "loaded", "robots.txt forbidden", time.time())

        response.raise_for_status()

        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(target)
        parser.parse(response.text.splitlines())
        return RobotsResult(parser, "loaded", None, time.time())

    except Exception as exc:  # noqa: BLE001 - mọi lỗi đều là "tạm thời" ở đây
        return RobotsResult(None, "temporary_error", f"{type(exc).__name__}: {exc}", time.time())


class SourceSkipped(RuntimeError):
    """Robots policy yêu cầu bỏ qua toàn bộ nguồn (on_temporary_error=skip_source)."""


class RobotsGate:
    """Cache robots.txt theo origin và áp dụng RobotsPolicy.

    Khác biệt quan trọng so với bản cũ: kết quả `temporary_error` KHÔNG được
    cache vĩnh viễn -- nó hết hạn ngay để lần gọi sau thử lại, và policy quyết
    định là allow, skip_source hay retry_then_skip.
    """

    def __init__(self, client: httpx.Client, user_agent: str, policy: RobotsPolicy):
        self.client = client
        self.user_agent = user_agent
        self.policy = policy
        self._cache: dict[str, RobotsResult] = {}
        self._skipped_origins: set[str] = set()

    def _origin(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _fetch_with_retry(self, url: str) -> RobotsResult:
        attempts = (
            self.policy.retry_attempts
            if self.policy.on_temporary_error == "retry_then_skip"
            else 1
        )
        result = load_robots(self.client, url)
        for attempt in range(2, attempts + 1):
            if result.status != "temporary_error":
                break
            log.warning(
                "robots.txt lỗi tạm thời (%s), thử lại lần %d/%d: %s",
                self._origin(url),
                attempt,
                attempts,
                result.detail,
            )
            time.sleep(min(2 ** (attempt - 1), 8))
            result = load_robots(self.client, url)
        return result

    def _resolve(self, url: str) -> RobotsResult:
        origin = self._origin(url)
        cached = self._cache.get(origin)
        if cached is not None:
            fresh = (time.time() - cached.fetched_at) < self.policy.cache_ttl_seconds
            if cached.status != "temporary_error" and fresh:
                return cached

        result = self._fetch_with_retry(url)
        # Chỉ cache kết quả xác định. Lỗi tạm thời để lần sau thử lại.
        if result.status != "temporary_error":
            self._cache[origin] = result
        return result

    def can_fetch(self, url: str) -> tuple[bool, str]:
        """Trả về (được phép, lý do). Ném SourceSkipped nếu policy yêu cầu dừng nguồn."""
        origin = self._origin(url)
        if origin in self._skipped_origins:
            raise SourceSkipped(f"{origin}: đã bị bỏ qua do lỗi robots.txt trước đó")

        result = self._resolve(url)

        if result.status == "loaded":
            assert result.parser is not None
            allowed = result.parser.can_fetch(self.user_agent, url)
            return allowed, "robots_allow" if allowed else "robots_deny"

        if result.status == "missing":
            if self.policy.on_missing == "allow":
                return True, "robots_missing_allow"
            return False, "robots_missing_deny"

        # temporary_error
        detail = result.detail or "unknown"
        if self.policy.on_temporary_error == "allow":
            log.warning("%s: robots.txt lỗi (%s), policy=allow -> vẫn crawl", origin, detail)
            return True, f"robots_error_allow: {detail}"

        self._skipped_origins.add(origin)
        raise SourceSkipped(
            f"{origin}: không đọc được robots.txt sau khi thử lại ({detail}). "
            f"policy={self.policy.on_temporary_error}"
        )

    def crawl_delay(self, url: str) -> float | None:
        result = self._cache.get(self._origin(url))
        if result is None or result.parser is None:
            return None
        try:
            value = result.parser.crawl_delay(self.user_agent)
        except Exception:  # noqa: BLE001
            return None
        return float(value) if value is not None else None
