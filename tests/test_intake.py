"""Intake: every format a reviewer brings, and no silent loss of pages (audit 14/10, stage 1)."""

from __future__ import annotations

import fitz
import pytest
from fastapi.testclient import TestClient

from quantum_gw import intake
from quantum_gw.domain.models import DocumentInput
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.parsers.ocr import TesseractOCR
from quantum_gw.settings import IntakeSettings
from quantum_gw.studio.export import docx_from_lines

CLAIM = "Năm 2024, Tập đoàn giảm 30% phát thải khí nhà kính phạm vi 1 và 2 so với năm 2020."


def _docx(tmp_path, lines):
    path = tmp_path / "bao-cao-phat-trien-ben-vung-2024.docx"
    path.write_bytes(docx_from_lines(lines, lines, [None] * len(lines), [], "", tracked=False))
    return path


def test_docx_is_parsed_paragraph_by_paragraph(tmp_path):
    path = _docx(tmp_path, ["CÔNG TY CỔ PHẦN THÉP XANH", CLAIM])
    chunks = DocumentParser(IntakeSettings()).parse(DocumentInput(path=str(path)))
    assert any("giảm 30% phát thải" in c.text for c in chunks)


def test_html_is_parsed_without_scripts(tmp_path):
    path = tmp_path / "trang.html"
    path.write_text(f"<html><script>var x=1</script><body><h1>Báo cáo</h1><p>{CLAIM}</p></body></html>", encoding="utf-8")
    chunks = DocumentParser(IntakeSettings()).parse(DocumentInput(path=str(path)))
    text = " ".join(c.text for c in chunks)
    assert "giảm 30%" in text and "var x" not in text


def _scanned_pdf(path):
    src = fitz.open()
    page = src.new_page()
    page.insert_text((72, 72), "Giam 30% phat thai", fontsize=18)
    pix = page.get_pixmap(dpi=100)
    out = fitz.open()
    image_page = out.new_page(width=page.rect.width, height=page.rect.height)
    image_page.insert_image(image_page.rect, pixmap=pix)
    text_page = out.new_page()
    text_page.insert_text((72, 72), "Bao cao phat trien ben vung 2024. " * 4, fontsize=11)
    out.save(path)


def test_preview_warns_when_scanned_pages_will_be_lost(tmp_path, monkeypatch):
    path = tmp_path / "scan.pdf"
    _scanned_pdf(path)
    monkeypatch.setattr(TesseractOCR, "available", property(lambda self: False))
    preview = intake.preview_file(path, "scan.pdf", IntakeSettings())
    assert preview["pages"] == 2 and preview["scanned_pages"] == [1] and preview["text_pages"] == 1
    assert preview["ocr_available"] is False
    assert any("không có OCR" in w for w in preview["warnings"])


def test_preview_guesses_company_year_and_report_type(tmp_path):
    path = _docx(tmp_path, ["CÔNG TY CỔ PHẦN THÉP XANH", "Báo cáo phát triển bền vững năm 2024", CLAIM])
    guess = intake.preview_file(path, path.name, IntakeSettings())["guess"]
    assert guess["report_type"] == "sustainability"
    assert guess["year"] == 2024
    assert guess["company"] == "THÉP XANH"
    assert guess["suggested_role"] == "claim_source"


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/a.pdf", "http://127.0.0.1:8000/v1/runs",
                                 "http://localhost/x.pdf", "http://10.0.0.5/a.pdf", "http://169.254.169.254/latest"])
def test_fetch_refuses_local_and_non_http_targets(url):
    with pytest.raises(intake.FetchError):
        intake.fetch_url(url)


def test_preview_endpoint_reports_unsupported_files_per_file(tmp_path):
    from quantum_gw.api import app

    client = TestClient(app)
    response = client.post("/v1/intake/preview", files=[
        ("files", ("ghi-chu.txt", CLAIM.encode("utf-8"), "text/plain")),
        ("files", ("anh.png", b"\x89PNG", "image/png")),
    ])
    assert response.status_code == 200
    first, second = response.json()["files"]
    assert first["sentences"] >= 1 and not first.get("error")
    assert "Chưa hỗ trợ" in second["error"]
