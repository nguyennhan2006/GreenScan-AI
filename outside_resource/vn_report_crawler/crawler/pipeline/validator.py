"""Nhận diện loại file dựa trên NỘI DUNG response, không chỉ đuôi URL.

Cần thiết cho các endpoint kiểu:
    /Handlers/DownloadFinancialStatement.ashx?FileName=...
    /Handlers/DownloadAttachedFile.ashx?NewsID=...
    /download?file=report.pdf
"""

from __future__ import annotations

import io
import zipfile
from urllib.parse import parse_qs, urlparse

import httpx

SUPPORTED_MIME_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/x-pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/msword": ".doc",
    "application/vnd.ms-excel": ".xls",
}

_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_ZIP_MAGIC = b"PK\x03\x04"


def _sniff_zip_office(content: bytes) -> str | None:
    """Phân biệt DOCX/XLSX bằng danh sách entry trong ZIP container."""
    try:
        names = set(zipfile.ZipFile(io.BytesIO(content)).namelist())
    except Exception:  # noqa: BLE001 - ZIP hỏng thì coi như không nhận diện được
        return None
    if "word/document.xml" in names:
        return ".docx"
    if "xl/workbook.xml" in names or "xl/workbook.bin" in names:
        return ".xlsx"
    return None


def _extension_from_url(url: str) -> str | None:
    """Lấy đuôi từ path hoặc từ query string (?FileName=x.pdf, ?file=x.xlsx)."""
    parsed = urlparse(url)
    candidates = [parsed.path]
    for values in parse_qs(parsed.query).values():
        candidates.extend(values)
    for value in candidates:
        lowered = value.lower()
        for ext in (".pdf", ".docx", ".xlsx", ".doc", ".xls"):
            if lowered.endswith(ext):
                return ext
    return None


def detect_file_type(response: httpx.Response) -> str | None:
    """Trả về đuôi file chuẩn hoá ('.pdf', '.docx', ...) hoặc None nếu không nhận ra."""
    content = response.content
    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()

    # 1. Magic bytes -- đáng tin nhất.
    if content.startswith(b"%PDF-"):
        return ".pdf"
    if content.startswith(_ZIP_MAGIC):
        sniffed = _sniff_zip_office(content)
        if sniffed:
            return sniffed
    if content.startswith(_OLE2_MAGIC):
        # OLE2 dùng chung cho .doc/.xls; phân biệt bằng content-type rồi tới URL.
        if content_type in ("application/msword",):
            return ".doc"
        if content_type in ("application/vnd.ms-excel",):
            return ".xls"
        return _extension_from_url(str(response.url)) or ".doc"

    # 2. Content-Type header.
    if content_type in SUPPORTED_MIME_TYPES:
        return SUPPORTED_MIME_TYPES[content_type]

    # 3. Content-Disposition filename.
    disposition = response.headers.get("content-disposition", "")
    if disposition:
        for ext in (".pdf", ".docx", ".xlsx", ".doc", ".xls"):
            if ext in disposition.lower():
                return ext

    return None


def is_probably_attachment(url: str, attachment_patterns: list[str]) -> bool:
    """Đoán trước khi tải: URL có vẻ là file đính kèm không?"""
    lowered = url.lower()
    if _extension_from_url(url):
        return True
    return any(pattern.lower() in lowered for pattern in attachment_patterns)
