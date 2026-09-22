"""Citations must resolve to a file that still exists.

Uploads used to land in a TemporaryDirectory deleted the moment analysis
returned, so "page 42" pointed at nothing. These tests pin the two properties
the deep-link depends on: the file survives, and the id the store hands out is
the same id the parser derives.
"""

import fitz
import pytest

from quantum_gw.domain.models import DocumentInput
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.settings import load_settings
from quantum_gw.storage.documents import (
    DocumentStore,
    highlight_rects,
    page_count,
    render_page_png,
)

# ASCII on purpose: PyMuPDF's built-in base-14 fonts cannot render Vietnamese
# diacritics, so a Vietnamese fixture writes a text layer that does not match
# what was inserted and the test would fail for a reason unrelated to the code.
# Accented text is covered against a real report in test_highlight_on_real_pdf.
NEEDLE = "GHG emissions fell 30 percent against the 2019 baseline across the group."


@pytest.fixture
def pdf_bytes():
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 100), f"Trang {i + 1}", fontsize=14)
        if i == 1:
            page.insert_text((72, 140), NEEDLE, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def store(tmp_path):
    return DocumentStore(tmp_path / "documents")


def test_document_survives_the_request(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    assert record.path.is_file()
    assert store.get(record.doc_id).path.read_bytes() == pdf_bytes


def test_doc_id_matches_the_id_the_parser_derives(store, pdf_bytes):
    """The invariant the whole deep-link rests on."""
    record = store.put(pdf_bytes, "bao-cao.pdf")
    chunks = DocumentParser(load_settings().intake).parse(
        DocumentInput(path=str(record.path), name="bao-cao.pdf")
    )
    assert chunks, "fixture PDF produced no chunks"
    assert {c.doc_id for c in chunks} == {record.doc_id}


def test_identical_bytes_are_stored_once(store, pdf_bytes):
    a = store.put(pdf_bytes, "bao-cao.pdf")
    b = store.put(pdf_bytes, "bao-cao.pdf")
    assert a.sha256 == b.sha256
    assert a.path == b.path
    lines = [x for x in store.index_path.read_text(encoding="utf-8").split("\n") if x.strip()]
    assert len(lines) == 1, "re-registering the same document must not duplicate the index"


def test_unknown_id_returns_none(store):
    assert store.get("does-not-exist") is None


def test_highlight_finds_text_on_the_right_page(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    assert highlight_rects(record.path, 2, NEEDLE), "needle is on page 2"
    assert highlight_rects(record.path, 1, NEEDLE) == [], "must not match another page"


def test_highlight_tolerates_reflowed_chunk_text(store, pdf_bytes):
    """Chunks carry normalised whitespace and span blocks, so exact match fails."""
    record = store.put(pdf_bytes, "bao-cao.pdf")
    mangled = NEEDLE.replace(" ", "\n  ")
    assert highlight_rects(record.path, 2, mangled)


def test_missing_text_yields_no_rects_rather_than_raising(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    assert highlight_rects(record.path, 2, "văn bản hoàn toàn không tồn tại trong tài liệu") == []


def test_out_of_range_page_is_empty_not_an_error(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    assert highlight_rects(record.path, 99, NEEDLE) == []


def test_render_returns_a_png(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    rects = highlight_rects(record.path, 2, NEEDLE)
    png = render_page_png(record.path, 2, rects)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


def test_render_without_highlight_still_works(store, pdf_bytes):
    record = store.put(pdf_bytes, "bao-cao.pdf")
    assert render_page_png(record.path, 1, []).startswith(b"\x89PNG")


def test_page_count(store, pdf_bytes):
    assert page_count(store.put(pdf_bytes, "bao-cao.pdf").path) == 3


def test_only_known_types_are_servable(store, pdf_bytes):
    assert store.is_servable(store.put(pdf_bytes, "bao-cao.pdf"))
    assert not store.is_servable(store.put(b"MZ\x90\x00", "payload.exe"))


REAL_PDF = "data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf"


@pytest.mark.skipif(
    not __import__("pathlib").Path(REAL_PDF).is_file(),
    reason="real report not downloaded; run data/real_cases/scripts/download_sources.py",
)
def test_highlight_on_real_pdf_with_vietnamese_text(tmp_path):
    """Accented Vietnamese, real layout, re-flowed chunk text — the actual case."""
    from pathlib import Path

    store = DocumentStore(tmp_path / "documents")
    record = store.put(Path(REAL_PDF).read_bytes(), "HPG_Sustainability_Report_2025.pdf")
    chunks = DocumentParser(load_settings().intake).parse(
        DocumentInput(path=str(record.path), name="HPG_Sustainability_Report_2025.pdf")
    )
    assert {c.doc_id for c in chunks} == {record.doc_id}

    located = 0
    for chunk in [c for c in chunks if c.page and len(c.text) > 300][:12]:
        if highlight_rects(record.path, chunk.page, chunk.text):
            located += 1
    assert located >= 6, f"only {located}/12 chunks could be located on their own page"
