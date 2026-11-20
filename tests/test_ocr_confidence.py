"""How sure the system is of what it read: OCR confidence, garbled text layers, pages left unread.

A verdict computed from a number Tesseract was unsure of is a verdict about the
scanner. These tests pin down that such a number is measured (parsers/ocr.py),
carried to the claim and the passage, kept out of every decisive figure
comparison (agents/verifier.py _unless_misread), and reported to a person
(gate G9, the Studio change report).
"""

from __future__ import annotations

import fitz
import pytest

from quantum_gw.agents.reviewer import ReviewerAgent
from quantum_gw.agents.verifier import VerificationAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, DocumentInput, RetrievedEvidence
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.parsers.ocr import (
    LOW_NUMBER_CONF,
    LOW_WORD_CONF,
    OcrReading,
    TesseractOCR,
    contains_number,
    parse_tsv,
)
from quantum_gw.parsers.text_quality import garbled, garbled_share
from quantum_gw.settings import IntakeSettings, VerificationSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.studio.report import ocr_note
from quantum_gw.verification.stance import PARTIAL, SUPPORTS

HEADER = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"


def _row(word: int, conf: float, text: str) -> str:
    return f"5\t1\t1\t1\t1\t{word}\t{100 * word}\t200\t80\t30\t{conf}\t{text}"


# ---------- the measure ----------

def test_tsv_gives_word_confidences_and_the_numbers_ocr_doubts():
    tsv = "\n".join([
        HEADER,
        "4\t1\t1\t1\t1\t0\t0\t0\t900\t40\t-1\t",          # a line record carries no word
        _row(1, 96.0, "Giảm"),
        _row(2, LOW_NUMBER_CONF - 15, "30%"),              # a number OCR is unsure of
        _row(3, 97.0, "phát"),
        _row(4, LOW_WORD_CONF - 20, "thải"),              # a doubtful word, not a number
        _row(5, 99.0, "1.936"),                           # a number OCR is sure of
        _row(6, LOW_NUMBER_CONF - 1, "30%"),               # the same number again: listed once
    ])
    reading = parse_tsv(tsv, scale=72 / 220)
    assert [w["text"] for w in reading.words] == ["Giảm", "30%", "phát", "thải", "1.936", "30%"]
    assert reading.doubtful_numbers == ["30"]
    weights = [4, 3, 4, 4, 5, 3]
    confs = [96.0, LOW_NUMBER_CONF - 15, 97.0, LOW_WORD_CONF - 20, 99.0, LOW_NUMBER_CONF - 1]
    assert reading.low_share == pytest.approx(sum(c < LOW_WORD_CONF for c in confs) / len(confs))
    # Length-weighted: a long word read well counts for more than a short one read badly.
    assert reading.mean_conf == pytest.approx(sum(w * c for w, c in zip(weights, confs, strict=True)) / sum(weights))
    # Boxes come back in page points, not pixels of the 220 dpi image.
    assert reading.words[0]["bbox"][0] == pytest.approx(100 * 72 / 220, abs=0.1)
    assert reading.summary()["ocr_doubtful_numbers"] == ["30"]


@pytest.mark.parametrize("text, token, found", [
    ("giảm 30% phát thải", "30", True),
    ("mục tiêu đến năm 2030", "30", False),
    ("đạt 1.9365 tấn", "1.936", False),
    ("đạt 1.936 tấn.", "1.936", True),
    ("tỷ lệ 12,5%", "12,5", True),
])
def test_a_doubtful_number_is_matched_as_a_whole_number(text, token, found):
    assert contains_number(text, token) is found


def test_legacy_font_text_is_measured_as_garbled():
    tcvn3 = "Bé Tµi chÝnh ban hµnh Th«ng t­ nµy cã hi~u lùc kÓ tõ ngµy ký"
    assert garbled("chÝnh") and garbled("lµc") and not garbled("chính")
    assert garbled_share(tcvn3) > 0.5
    assert garbled_share("Bộ Tài chính ban hành Thông tư này có hiệu lực kể từ ngày ký") == 0.0
    assert garbled_share("Scope 1 emissions fell 12% in 2024 (tCO2e).") == 0.0


# ---------- parsing: OCR measures reach the passage, unread pages are recorded ----------

def _scan(path, *, garbled_layer=False):
    doc = fitz.open()
    page = doc.new_page()
    if garbled_layer:
        page.insert_text((72, 72), "Bé Tµi chÝnh ban hµnh Th«ng t­ nµy cã hi~u lùc kÓ tõ ngµy ký.", fontsize=11)
    else:
        src = fitz.open()
        drawn = src.new_page()
        drawn.insert_text((72, 72), "Giam 30% phat thai", fontsize=18)
        page.insert_image(page.rect, pixmap=drawn.get_pixmap(dpi=100))
    doc.save(path)


def _document(path):
    return DocumentInput(path=str(path), role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL)


def test_a_scan_without_ocr_is_recorded_as_unread(tmp_path, monkeypatch):
    path = tmp_path / "scan.pdf"
    _scan(path)
    monkeypatch.setattr(TesseractOCR, "available", property(lambda self: False))
    parser = DocumentParser(IntakeSettings(extract_tables=False))
    parser.parse(_document(path))
    assert parser.reading == [{"source_name": "scan.pdf", "doc_id": parser.reading[0]["doc_id"], "page": 1,
                               "role": "claim_source", "ocr": False, "unread": True}]


def test_a_garbled_page_is_read_by_ocr_and_its_doubtful_numbers_reach_the_passage(tmp_path, monkeypatch):
    path = tmp_path / "luat.pdf"
    _scan(path, garbled_layer=True)
    monkeypatch.setattr(TesseractOCR, "available", property(lambda self: True))
    monkeypatch.setattr(TesseractOCR, "read_page", lambda self, page, dpi=220: OcrReading(
        text="Bộ Tài chính ban hành Thông tư này. Giảm 30% phát thải so với năm 2020.",
        mean_conf=81.4, low_share=0.1, doubtful_numbers=["30"]))
    parser = DocumentParser(IntakeSettings(extract_tables=False))
    chunks = parser.parse(_document(path))
    record = parser.reading[0]
    assert record["ocr"] and record["native_text_garbled"] > 0.5 and record["ocr_confidence"] == 81.4
    with_number = [c for c in chunks if "30%" in c.text]
    assert with_number and all(c.metadata["ocr_doubtful_numbers"] == ["30"] for c in with_number)
    assert all("ocr_doubtful_numbers" not in c.metadata for c in chunks if "30%" not in c.text)


# ---------- verification: a doubtful number decides nothing ----------

CLAIM = "Năm 2024, tổng phát thải khí nhà kính của công ty là 1.936 tấn CO2e."
EVIDENCE = "Tổng phát thải khí nhà kính năm 2024 của công ty là 1.936 tấn CO2e theo kiểm kê."


def _verify(tmp_path, *, claim_doubts=(), evidence_doubts=()):
    agent = VerificationAgent(VerificationSettings(), AuditLogger(tmp_path / "audit.jsonl"))
    claim = Claim(claim_id="c", text=CLAIM, claim_type="ghg_emissions", source_chunk_id="s",
                  source_name="bao_cao.pdf", source_doc_id="own", period="2024",
                  ocr_confidence=74.0 if claim_doubts else None, doubtful_numbers=list(claim_doubts))
    passage = RetrievedEvidence(chunk_id="e1", doc_id="other", source_name="kiem_ke.pdf",
                                source_type=SourceType.EXTERNAL, text=EVIDENCE, score=0.7,
                                citation="kiem_ke.pdf (tr. 2)", doubtful_numbers=list(evidence_doubts))
    return agent.run(claim, [passage])


def test_a_clean_reading_still_supports(tmp_path):
    result = _verify(tmp_path)
    assert result.evidence[0].relation == SUPPORTS
    assert not result.doubtful_reading


@pytest.mark.parametrize("side", ["claim", "evidence"])
def test_a_match_resting_on_a_doubtful_number_goes_to_a_person(tmp_path, side):
    doubts = {"claim_doubts": ["1.936"]} if side == "claim" else {"evidence_doubts": ["1.936"]}
    result = _verify(tmp_path, **doubts)
    assert result.evidence[0].relation == PARTIAL
    assert "1.936" in result.evidence[0].relation_reason and "OCR" in result.evidence[0].relation_reason
    assert result.status != VerificationStatus.SUPPORTED
    assert result.doubtful_reading
    assert any("OCR" in w or "trang quét" in w for w in result.warnings)


def test_a_doubtful_number_the_comparison_does_not_use_changes_nothing(tmp_path):
    result = _verify(tmp_path, evidence_doubts=["17"])
    assert result.evidence[0].relation == SUPPORTS
    assert not result.doubtful_reading


def test_a_claim_with_an_uncompared_doubtful_figure_keeps_the_match_but_asks_a_person(tmp_path):
    result = _verify(tmp_path, claim_doubts=["2024"])
    assert result.evidence[0].relation == SUPPORTS
    assert result.doubtful_reading and any("2024" in w for w in result.warnings)


def test_a_label_number_is_not_a_doubtful_figure_of_the_claim():
    from quantum_gw.agents.claim_extractor import _reading
    from quantum_gw.domain.models import EvidenceChunk
    chunk = EvidenceChunk(chunk_id="k", doc_id="d", source_name="scan.pdf", role=DocumentRole.CLAIM_SOURCE,
                          source_type=SourceType.INTERNAL, page=2, text="",
                          metadata={"ocr": True, "ocr_confidence": 77.0, "ocr_doubtful_numbers": ["1", "1.936"]})
    reading = _reading(chunk, "Phát thải phạm vi 1 năm 2024 là 1.936 tấn CO2e.")
    assert reading == {"ocr_confidence": 77.0, "doubtful_numbers": ["1.936"]}


# ---------- reporting: gate G9 and the change report ----------

def _page(page, **extra):
    return {"source_name": "bao_cao.pdf", "doc_id": "d", "page": page, "role": "claim_source", **extra}


def test_g9_passes_a_born_digital_input():
    gate = ReviewerAgent._reading_gate([], [])
    assert gate.gate_id == "G9" and gate.status == "PASS"


def test_g9_reports_ocr_pages_without_holding_the_run():
    reading = [_page(3, ocr=True, ocr_confidence=91.2), _page(4, ocr=True, ocr_confidence=62.0)]
    gate = ReviewerAgent._reading_gate(reading, [])
    assert gate.status == "PASS"
    assert "2 trang đọc bằng OCR" in gate.details and "62 đến 91/100" in gate.details
    assert "1 trang có độ tin cậy dưới" in gate.details and "bao_cao.pdf tr. 4" in gate.details


def test_g9_holds_the_run_for_unread_pages_and_doubtful_numbers(tmp_path):
    unread = ReviewerAgent._reading_gate([_page(7, ocr=False, unread=True)], [])
    assert unread.status == "PENDING_HUMAN_REVIEW" and "không có trong phân tích" in unread.details
    result = _verify(tmp_path, claim_doubts=["1.936"])
    leaning = ReviewerAgent._reading_gate([_page(1, ocr=True, ocr_confidence=74.0)], [result])
    assert leaning.status == "PENDING_HUMAN_REVIEW" and "1 tuyên bố có số liệu OCR đọc" in leaning.details


def test_change_report_says_how_sure_the_original_text_is():
    item = {"ocr": True, "ocr_confidence": 83.6, "doubtful_numbers": ["30", "1.936"]}
    assert ocr_note(item) == " · chữ đọc bằng OCR, độ tin cậy 84/100; số đọc chưa chắc: 30, 1.936, đối chiếu trang gốc"
    assert ocr_note({"ocr": False}) == ""
