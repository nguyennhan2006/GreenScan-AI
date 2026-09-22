"""Adapter chỉ được kiểm thử trên fixture HTML.

Selector của Vietstock/CafeF CHƯA đối chiếu với HTML thật -- các test dưới đây
xác nhận LOGIC adapter đúng, không xác nhận selector khớp site thật. Trước khi
bật `enabled: true`, phải thay fixture bằng HTML lưu từ site thật.
"""

from __future__ import annotations

import logging

import httpx
import pytest

from crawler.adapters import CrawlContext, get_adapter
from crawler.models import RobotsPolicy, SourceAuthority, SourceConfig
from crawler.pipeline.downloader import Downloader
from crawler.policies.rate_limit import RateLimiter
from crawler.policies.robots import RobotsGate

VIETSTOCK_HTML = """
<html><body><table>
<tr><td>HPG</td><td>Báo cáo tài chính hợp nhất quý 2 2024 đã soát xét</td>
    <td><a href="/downloadfile/1/2/bctc-hpg-q2-2024.pdf">Tải</a></td></tr>
<tr><td>VNM</td><td>Báo cáo thường niên 2023</td>
    <td><a href="https://static.vietstock.vn/data/download/btn-vnm-2023.doc">Tải</a></td></tr>
<tr><td>-</td><td>Đăng nhập để xem thêm</td><td><a href="/login.htm">Đăng nhập</a></td></tr>
</table></body></html>
"""

CAFEF_HTML = """
<html><body><table>
<tr><td>Báo cáo phát triển bền vững 2024</td>
    <td><a href="https://cafef1.mediacdn.vn/2024/ptbv-hpg-2024.pdf">Tải</a></td></tr>
<tr><td>Bản cáo bạch 2022</td>
    <td><a href="/du-lieu/hose/HPG-cong-ty-co-phan.chn">Chi tiết</a></td></tr>
</table></body></html>
"""

REPORT_TYPES = {
    "sustainability": ["báo cáo phát triển bền vững"],
    "annual": ["báo cáo thường niên"],
    "financial": ["báo cáo tài chính"],
    "prospectus": ["bản cáo bạch"],
}


def build(adapter_name: str, **overrides):
    config = SourceConfig(
        id=adapter_name,
        adapter=adapter_name,
        authority=SourceAuthority.AGGREGATOR,
        allowed_domains=overrides.pop("allowed_domains", []),
        report_types=REPORT_TYPES,
        exclude_patterns=["đăng nhập"],
        allowed_file_types=["pdf", "doc", "docx", "xls", "xlsx"],
        **overrides,
    )
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    ctx = CrawlContext(
        downloader=Downloader(client, RateLimiter(0)),
        robots=RobotsGate(client, "TestBot", RobotsPolicy()),
        client=client,
        log=logging.getLogger("test"),
    )
    return get_adapter(adapter_name)(config, ctx)


def response_for(url: str, html: str) -> httpx.Response:
    return httpx.Response(200, text=html, headers={"content-type": "text/html"},
                          request=httpx.Request("GET", url))


def test_vietstock_extracts_rows_with_metadata():
    adapter = build("vietstock",
                    allowed_domains=["finance.vietstock.vn", "static.vietstock.vn"])
    url = "https://finance.vietstock.vn/tai-lieu/bao-cao-tai-chinh.htm"
    candidates, _ = adapter.parse_listing(url, response_for(url, VIETSTOCK_HTML))

    assert len(candidates) == 2, "phải bỏ link đăng nhập"

    bctc = next(c for c in candidates if "bctc-hpg" in c.url)
    # Metadata lấy từ text của cả dòng <tr>, không chỉ anchor text "Tải".
    assert bctc.report_type == "financial"
    assert bctc.year == 2024
    assert bctc.ticker == "HPG"

    btn = next(c for c in candidates if "btn-vnm" in c.url)
    assert btn.report_type == "annual"
    assert btn.ticker == "VNM"
    assert btn.url.endswith(".doc")  # nguồn đa định dạng


def test_vietstock_row_context_feeds_scope_and_assurance():
    adapter = build("vietstock", allowed_domains=["finance.vietstock.vn"])
    url = "https://finance.vietstock.vn/tai-lieu/bao-cao-tai-chinh.htm"
    candidates, _ = adapter.parse_listing(url, response_for(url, VIETSTOCK_HTML))
    bctc = next(c for c in candidates if "bctc-hpg" in c.url)

    meta = adapter.normalize_metadata(bctc, response_for(bctc.url, ""), ".pdf")
    assert meta["statement_scope"] == "consolidated"
    assert meta["assurance_status"] == "reviewed"
    assert meta["period_type"] == "quarterly"
    assert meta["source_authority"] == "aggregator"


def test_cafef_extracts_cdn_attachment_and_ticker():
    adapter = build("cafef", allowed_domains=["cafef.vn", "cafef1.mediacdn.vn"])
    url = "https://cafef.vn/du-lieu/cong-bo-thong-tin.chn"
    candidates, pages = adapter.parse_listing(url, response_for(url, CAFEF_HTML))

    assert len(candidates) == 1
    assert candidates[0].url.startswith("https://cafef1.mediacdn.vn/")
    assert candidates[0].report_type == "sustainability"
    assert candidates[0].hints["mirror_of"] == "cafef"
    # Trang chi tiết theo mã CK được đưa vào hàng đợi
    assert any("HPG-cong-ty" in p.url for p in pages)


def test_cafef_ticker_parsed_from_url_pattern():
    adapter = build("cafef", allowed_domains=["cafef.vn", "cafef1.mediacdn.vn"])
    assert adapter._ticker_from("https://cafef.vn/du-lieu/hose/HPG-abc.chn") == "HPG"
    assert adapter._ticker_from("https://cafef.vn/du-lieu/upcom/vgt-abc.chn") == "VGT"


def test_domain_restriction_blocks_offsite_links():
    adapter = build("cafef", allowed_domains=["cafef.vn"])  # CDN không được phép
    url = "https://cafef.vn/du-lieu/cong-bo-thong-tin.chn"
    candidates, _ = adapter.parse_listing(url, response_for(url, CAFEF_HTML))
    assert candidates == []


def test_unknown_adapter_raises():
    with pytest.raises(ValueError, match="chưa được cài đặt"):
        get_adapter("hnx")
