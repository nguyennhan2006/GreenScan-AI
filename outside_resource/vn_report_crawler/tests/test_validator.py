"""Nhận diện file theo nội dung, không chỉ theo đuôi URL."""

from __future__ import annotations

import httpx

from conftest import PDF_A, make_docx, make_xlsx
from crawler.pipeline.validator import detect_file_type, is_probably_attachment


def response(content: bytes, url: str = "http://x.test/a", **headers) -> httpx.Response:
    return httpx.Response(
        200, content=content, headers=headers, request=httpx.Request("GET", url)
    )


def test_pdf_by_magic_bytes_without_extension():
    resp = response(PDF_A, "http://x.test/Handlers/Download.ashx?NewsID=1",
                    **{"content-type": "application/octet-stream"})
    assert detect_file_type(resp) == ".pdf"


def test_xlsx_disambiguated_from_zip():
    assert detect_file_type(response(make_xlsx())) == ".xlsx"


def test_docx_disambiguated_from_zip():
    assert detect_file_type(response(make_docx())) == ".docx"


def test_content_type_header_fallback():
    resp = response(b"garbage", **{"content-type": "application/pdf; charset=binary"})
    assert detect_file_type(resp) == ".pdf"


def test_content_disposition_fallback():
    resp = response(b"garbage", **{"content-disposition": 'attachment; filename="a.xlsx"'})
    assert detect_file_type(resp) == ".xlsx"


def test_html_page_is_not_a_document():
    resp = response(b"<html><body>hi</body></html>", **{"content-type": "text/html"})
    assert detect_file_type(resp) is None


def test_plain_zip_is_not_office():
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", "hello")
    assert detect_file_type(response(buf.getvalue())) is None


class TestAttachmentGuess:
    def test_plain_pdf_url(self):
        assert is_probably_attachment("http://x.test/a/b.pdf", []) is True

    def test_query_string_pdf(self):
        assert is_probably_attachment("http://x.test/download?file=report.pdf", []) is True

    def test_ashx_query_filename(self):
        url = "http://x.test/Handlers/DownloadFinancialStatement.ashx?FileName=DHA-17-Q2.pdf"
        assert is_probably_attachment(url, []) is True

    def test_ashx_without_filename_needs_pattern(self):
        url = "http://x.test/Handlers/DownloadAttachedFile.ashx?NewsID=99"
        assert is_probably_attachment(url, []) is False
        assert is_probably_attachment(url, ["/Handlers/DownloadAttachedFile.ashx"]) is True

    def test_ordinary_page_is_not_attachment(self):
        assert is_probably_attachment("http://x.test/tin-tuc.html", []) is False
