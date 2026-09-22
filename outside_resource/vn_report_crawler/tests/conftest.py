"""Fixture site chạy hoàn toàn trong tiến trình qua httpx.MockTransport.

Không cần mạng, không cần server phụ, không cần thêm dependency (respx).
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PDF_A = b"%PDF-1.4\n" + b"A" * 200 + b"\n%%EOF\n"
PDF_B = b"%PDF-1.4\n" + b"B" * 200 + b"\n%%EOF\n"


def make_xlsx() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("xl/workbook.xml", "<workbook/>")
    return buffer.getvalue()


def make_docx() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<document/>")
    return buffer.getvalue()


# Lưu ý: urllib.robotparser dùng luật KHỚP ĐẦU TIÊN thắng (không phải longest-match
# như RFC 9309). Vì vậy Disallow phải đứng trước Allow: / mới có hiệu lực.
ROBOTS_OK = "User-agent: *\nDisallow: /private/\nAllow: /\n"

INDEX_HTML = """
<html><body>
<table>
  <tr><td>HPG</td><td>Báo cáo phát triển bền vững 2024</td>
      <td><a href="/files/ptbv-2024.pdf">Tải về</a></td></tr>
  <tr><td>HPG</td><td>Báo cáo thường niên 2023 hợp nhất đã kiểm toán</td>
      <td><a href="/Handlers/DownloadAttachedFile.ashx?NewsID=99&FileName=btn-2023.pdf">Tải về</a></td></tr>
  <tr><td>VNM</td><td>Báo cáo tài chính quý 1 2024</td>
      <td><a href="/download?file=bctc-q1-2024.xlsx">Tải về</a></td></tr>
  <tr><td>VNM</td><td>Báo cáo quản trị 2024</td>
      <td><a href="/redirect/governance">Tải về</a></td></tr>
  <tr><td>-</td><td>Thông báo tuyển dụng báo cáo tài chính</td>
      <td><a href="/files/tuyen-dung.pdf">Tải về</a></td></tr>
  <tr><td>-</td><td>Báo cáo thường niên 2022 (link hỏng)</td>
      <td><a href="/files/missing-2022.pdf">Tải về</a></td></tr>
  <tr><td>-</td><td>Báo cáo phát triển bền vững 2021 bản sao</td>
      <td><a href="/files/ptbv-2024-mirror.pdf">Tải về</a></td></tr>
  <tr><td>-</td><td>Báo cáo thường niên trang 2</td>
      <td><a href="/page2.html">Xem tiếp</a></td></tr>
</table>
</body></html>
"""

PAGE2_HTML = """
<html><body>
<a href="/viewer/annual-2020">Báo cáo thường niên 2020</a>
</body></html>
"""

VIEWER_HTML = """
<html><body><iframe src="/files/btn-2020.pdf"></iframe></body></html>
"""


class FixtureSite:
    """Đếm số lần mỗi path được gọi -- dùng để kiểm chứng hành vi retry."""

    def __init__(self, robots_body: str | None = ROBOTS_OK, robots_error: bool = False):
        self.robots_body = robots_body
        self.robots_error = robots_error
        self.hits: dict[str, int] = {}

    def _count(self, path: str) -> None:
        self.hits[path] = self.hits.get(path, 0) + 1

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        query = request.url.query.decode()
        self._count(path)

        if path == "/robots.txt":
            if self.robots_error:
                raise httpx.ConnectError("TLS handshake failed", request=request)
            if self.robots_body is None:
                return httpx.Response(404, text="not found")
            return httpx.Response(200, text=self.robots_body)

        if path == "/":
            return httpx.Response(200, text=INDEX_HTML,
                                  headers={"content-type": "text/html; charset=utf-8"})
        if path == "/page2.html":
            return httpx.Response(200, text=PAGE2_HTML,
                                  headers={"content-type": "text/html; charset=utf-8"})
        if path == "/viewer/annual-2020":
            return httpx.Response(200, text=VIEWER_HTML,
                                  headers={"content-type": "text/html; charset=utf-8"})

        if path == "/files/ptbv-2024.pdf":
            return httpx.Response(200, content=PDF_A, headers={"content-type": "application/pdf"})
        # Cùng nội dung với ptbv-2024.pdf -> phải bị nhận là duplicate.
        if path == "/files/ptbv-2024-mirror.pdf":
            return httpx.Response(200, content=PDF_A, headers={"content-type": "application/pdf"})
        if path == "/files/btn-2020.pdf":
            return httpx.Response(200, content=PDF_B, headers={"content-type": "application/pdf"})
        if path == "/files/tuyen-dung.pdf":
            return httpx.Response(200, content=PDF_B, headers={"content-type": "application/pdf"})
        if path == "/files/missing-2022.pdf":
            return httpx.Response(404, text="not found")

        # Download handler: URL không có đuôi .pdf, chỉ content-type mới biết.
        if path == "/Handlers/DownloadAttachedFile.ashx":
            return httpx.Response(200, content=PDF_B,
                                  headers={"content-type": "application/octet-stream",
                                           "content-disposition": 'attachment; filename="btn-2023.pdf"'})
        # Query-string attachment trả về XLSX.
        if path == "/download" and "xlsx" in query:
            return httpx.Response(200, content=make_xlsx(),
                                  headers={"content-type": "application/octet-stream"})
        # Redirect 302 tới file thật.
        if path == "/redirect/governance":
            return httpx.Response(302, headers={"location": "/files/btn-2020.pdf"})

        if path.startswith("/private/"):
            return httpx.Response(200, content=PDF_B, headers={"content-type": "application/pdf"})

        return httpx.Response(404, text="not found")

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handler)


@pytest.fixture
def site() -> FixtureSite:
    return FixtureSite()


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    return tmp_path / "data"
