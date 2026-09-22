"""Regression cho bug nghiêm trọng nhất của bản cũ.

Bản cũ: `RobotFileParser.read()` lỗi mạng -> parser giữ last_checked == 0 ->
can_fetch() trả False cho MỌI url -> toàn bộ website bị bỏ qua trong im lặng,
và kết quả lỗi đó còn bị cache cho cả lần chạy.
"""

from __future__ import annotations

import httpx
import pytest

from conftest import FixtureSite
from crawler.models import RobotsPolicy
from crawler.policies.robots import RobotsGate, SourceSkipped, load_robots

UA = "TestBot/1.0"


def client_for(site: FixtureSite) -> httpx.Client:
    return httpx.Client(transport=site.transport(), follow_redirects=True)


def test_loads_and_applies_rules():
    site = FixtureSite()
    gate = RobotsGate(client_for(site), UA, RobotsPolicy())
    assert gate.can_fetch("http://x.test/files/a.pdf")[0] is True
    assert gate.can_fetch("http://x.test/private/secret.pdf")[0] is False


def test_missing_robots_allows_by_default():
    site = FixtureSite(robots_body=None)  # 404
    gate = RobotsGate(client_for(site), UA, RobotsPolicy())
    allowed, reason = gate.can_fetch("http://x.test/a.pdf")
    assert allowed is True
    assert reason == "robots_missing_allow"


def test_missing_robots_can_be_denied_by_policy():
    site = FixtureSite(robots_body=None)
    gate = RobotsGate(client_for(site), UA, RobotsPolicy(on_missing="deny"))
    allowed, _ = gate.can_fetch("http://x.test/a.pdf")
    assert allowed is False


def test_network_error_raises_instead_of_silently_denying():
    """Đây là hành vi mới: lỗi mạng phải ồn ào, không âm thầm trả False."""
    site = FixtureSite(robots_error=True)
    policy = RobotsPolicy(on_temporary_error="retry_then_skip", retry_attempts=2)
    gate = RobotsGate(client_for(site), UA, policy)

    with pytest.raises(SourceSkipped) as exc:
        gate.can_fetch("http://x.test/a.pdf")
    assert "robots.txt" in str(exc.value)
    # Đã thực sự thử lại chứ không bỏ cuộc ngay.
    assert site.hits["/robots.txt"] == 2


def test_network_error_can_be_configured_to_allow():
    site = FixtureSite(robots_error=True)
    gate = RobotsGate(client_for(site), UA, RobotsPolicy(on_temporary_error="allow"))
    allowed, reason = gate.can_fetch("http://x.test/a.pdf")
    assert allowed is True
    assert reason.startswith("robots_error_allow")


def test_temporary_error_is_not_cached_permanently():
    """Lỗi tạm thời không được cache: nguồn phải hồi phục khi mạng trở lại."""
    site = FixtureSite(robots_error=True)
    gate = RobotsGate(client_for(site), UA, RobotsPolicy(on_temporary_error="allow"))
    gate.can_fetch("http://x.test/a.pdf")
    assert gate._cache == {}  # không có entry nào được lưu

    site.robots_error = False
    allowed, reason = gate.can_fetch("http://x.test/a.pdf")
    assert allowed is True
    assert reason == "robots_allow"  # lần này đọc được thật


def test_403_robots_denies_everything():
    """RFC 9309: robots.txt trả 401/403 nghĩa là cấm toàn site."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="forbidden")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    gate = RobotsGate(client, UA, RobotsPolicy())
    assert gate.can_fetch("http://x.test/a.pdf")[0] is False


def test_load_robots_never_raises():
    site = FixtureSite(robots_error=True)
    result = load_robots(client_for(site), "http://x.test/a.pdf")
    assert result.status == "temporary_error"
    assert result.parser is None
    assert result.detail
