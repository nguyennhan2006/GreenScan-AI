import httpx
import pytest

from crawler.robots import Robots

RULES = "User-agent: *\nDisallow: /secret\n"


def client_returning(status: int, body: str = "") -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, text=body)))


def gate(status: int, body: str = "") -> Robots:
    return Robots(client_returning(status, body), "Bot", "allow", "skip")


@pytest.mark.parametrize("status", [400, 401, 403, 404, 410, 429])
def test_4xx_robots_means_no_restrictions(status):
    """RFC 9309 s2.3.1: an unavailable robots.txt imposes no restrictions.

    S3 and CloudFront answer 403 for a robots.txt object that does not exist.
    Reading that as a disallow silently dropped 177 public PDFs from a real run.
    """
    allowed, reason = gate(status).allowed("https://cdn.example/files/report.pdf")
    assert allowed is True
    assert reason == "robots_missing"


@pytest.mark.parametrize("status", [500, 502, 503])
def test_5xx_robots_is_unreachable_and_denies(status):
    """A server that cannot answer is not the same as a server with no rules."""
    allowed, reason = gate(status).allowed("https://cdn.example/files/report.pdf")
    assert allowed is False
    assert reason == "robots_error"


def test_transport_failure_denies():
    def boom(request):
        raise httpx.ConnectError("no route", request=request)

    robots = Robots(httpx.Client(transport=httpx.MockTransport(boom)), "Bot", "allow", "skip")
    assert robots.allowed("https://cdn.example/files/report.pdf") == (False, "robots_error")


def test_served_rules_are_still_enforced():
    robots = gate(200, RULES)
    assert robots.allowed("https://site.example/files/report.pdf")[0] is True
    assert robots.allowed("https://site.example/secret/report.pdf")[0] is False
