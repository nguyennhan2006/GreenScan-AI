"""Giới hạn tốc độ: khoảng nghỉ tối thiểu giữa các request + trần request/phút."""

from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(
        self,
        delay_seconds: float = 0.0,
        max_requests_per_minute: int | None = None,
        sleep=time.sleep,
        clock=time.monotonic,
    ):
        self.delay_seconds = max(0.0, delay_seconds)
        self.max_requests_per_minute = max_requests_per_minute
        self._sleep = sleep
        self._clock = clock
        self._last_request_at: float | None = None
        self._window: deque[float] = deque()

    def _respect_window(self) -> None:
        if not self.max_requests_per_minute:
            return
        now = self._clock()
        while self._window and now - self._window[0] >= 60.0:
            self._window.popleft()
        if len(self._window) >= self.max_requests_per_minute:
            wait = 60.0 - (now - self._window[0])
            if wait > 0:
                self._sleep(wait)

    def acquire(self) -> None:
        self._respect_window()
        if self._last_request_at is not None and self.delay_seconds > 0:
            elapsed = self._clock() - self._last_request_at
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                self._sleep(remaining)
        now = self._clock()
        self._last_request_at = now
        self._window.append(now)

    def bump_delay(self, seconds: float) -> None:
        """Nâng delay khi robots.txt khai báo Crawl-delay lớn hơn cấu hình."""
        if seconds > self.delay_seconds:
            self.delay_seconds = seconds
