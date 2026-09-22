"""Chẩn đoán JS-rendering, kiểm chứng trên HTML THẬT đã lưu trong tests/fixtures.

Đối chứng dương: finance.vietstock.vn, cafef.vn -- listing đổ bằng JS, 0 tài liệu.
Đối chứng âm:    hoaphat.com.vn, vinamilk.com.vn -- HTML tĩnh, có PDF thật.

Vinamilk là ca khó: 202k ký tự script và KHÔNG có <tr> nào, nhưng vẫn tĩnh.
Nó tồn tại ở đây để chặn việc quay lại heuristic chỉ nhìn hình dạng HTML.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crawler.discovery.browser_fallback import diagnose_empty_listing

FIXTURES = Path(__file__).parent / "fixtures"


def read(name: str) -> str:
    path = FIXTURES / name
    if not path.exists():
        pytest.skip(f"thiếu fixture {name} (chạy scripts/refresh_fixtures.py khi có mạng)")
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.parametrize(
    "fixture",
    ["vietstock_bctc.html", "vietstock_btn.html", "cafef_cbtt.html"],
)
def test_js_rendered_listings_are_flagged(fixture: str):
    reason = diagnose_empty_listing(read(fixture), candidates=0, typed_candidates=0)
    assert reason, f"{fixture} phải bị đánh dấu là cần render JS"
    assert "script" in reason


@pytest.mark.parametrize(
    "fixture",
    ["hoaphat_ptbv.html", "vinamilk_sustainability.html"],
)
def test_static_pages_with_documents_are_not_flagged(fixture: str):
    """Có tài liệu phân loại được -> không bao giờ báo JS-rendered."""
    assert diagnose_empty_listing(read(fixture), candidates=13, typed_candidates=13) is None


def test_typed_candidates_short_circuits():
    """Dù HTML trông thế nào, có tài liệu là không chẩn đoán."""
    html = "<html><body>" + "<script>" + "x" * 500_000 + "</script></body></html>"
    assert diagnose_empty_listing(html, candidates=5, typed_candidates=5) is None


def test_empty_spa_mount_is_flagged():
    html = """
    <html><body><div id="root"></div>
    <script>%s</script></body></html>
    """ % ("var app=1;" * 3000)
    reason = diagnose_empty_listing(html, candidates=0, typed_candidates=0)
    assert reason and "mount node 'root'" in reason


def test_plain_static_page_without_scripts_is_not_flagged():
    html = "<html><body><p>Chưa công bố báo cáo nào trong kỳ này.</p></body></html>"
    assert diagnose_empty_listing(html, candidates=0, typed_candidates=0) is None


def test_untyped_candidates_are_mentioned_in_reason():
    """Vietstock có sẵn vài PDF marketing -> lý do phải nói rõ có link nhưng vô nghĩa."""
    reason = diagnose_empty_listing(read("vietstock_bctc.html"), candidates=4, typed_candidates=0)
    assert reason and "không phân loại được" in reason
