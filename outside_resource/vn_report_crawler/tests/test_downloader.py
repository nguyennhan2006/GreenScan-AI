"""Retry phải có điều kiện: 404 fail ngay, 503 mới được thử lại."""

from __future__ import annotations

import httpx
import pytest

from crawler.pipeline.downloader import fetch, retryable


def counting_client(status: int) -> tuple[httpx.Client, dict[str, int]]:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(status, text="x")

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


@pytest.mark.parametrize("status", [400, 401, 403, 404, 410, 422])
def test_client_errors_are_not_retried(status: int):
    client, calls = counting_client(status)
    with pytest.raises(httpx.HTTPStatusError):
        fetch(client, "http://x.test/a.pdf")
    assert calls["n"] == 1, f"HTTP {status} không được retry"


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
def test_recoverable_errors_are_retried(status: int):
    client, calls = counting_client(status)
    with pytest.raises(httpx.HTTPStatusError):
        fetch(client, "http://x.test/a.pdf")
    assert calls["n"] == 3, f"HTTP {status} phải được retry đủ 3 lần"


def test_transport_error_is_retried():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(httpx.ConnectError):
        fetch(client, "http://x.test/a.pdf")
    assert calls["n"] == 3


def test_success_returns_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="ok")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert fetch(client, "http://x.test/a").text == "ok"


def test_retryable_predicate():
    request = httpx.Request("GET", "http://x.test/")
    assert retryable(httpx.ConnectTimeout("t", request=request)) is True
    assert retryable(
        httpx.HTTPStatusError("e", request=request, response=httpx.Response(503))
    ) is True
    assert retryable(
        httpx.HTTPStatusError("e", request=request, response=httpx.Response(404))
    ) is False
    assert retryable(ValueError("unrelated")) is False
