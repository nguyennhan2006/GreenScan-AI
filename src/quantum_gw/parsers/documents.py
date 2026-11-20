from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path

import fitz
import pdfplumber

from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.settings import IntakeSettings
from quantum_gw.utils.text import join_wrapped_lines, normalize_text, stable_id

from . import layout as page_layout
from .integrity import inside, merge, visible_blocks
from .ocr import TesseractOCR, contains_number
from .office import docx_text, html_text
from .text_quality import garbled_share

# Share of garbled words from which a page's text layer is treated as unreadable.
GARBLED_PAGE = 0.15


def _quality_for(quality: dict, text: str) -> dict:
    """The page's reading measures as they concern one passage: only the doubtful numbers it contains."""
    if not quality:
        return {}
    out = {k: v for k, v in quality.items() if k != "ocr_doubtful_numbers"}
    doubtful = [n for n in quality.get("ocr_doubtful_numbers", []) if contains_number(text, n)]
    if doubtful:
        out["ocr_doubtful_numbers"] = doubtful
    return out


class DocumentParser:
    def __init__(self, settings: IntakeSettings):
        self.settings = settings
        self.ocr = TesseractOCR(settings.tesseract_command, settings.ocr_languages)
        # Hidden text removed from the PDFs parsed so far, one record per page
        # and reason (parsers/integrity.py); read by the intake agent.
        self.hidden: list[dict] = []
        # Pages read by OCR or with a garbled text layer, with how sure the
        # reading is (parsers/ocr.py, text_quality.py); gate G9 reports them.
        self.reading: list[dict] = []

    def parse(self, document: DocumentInput) -> list[EvidenceChunk]:
        if document.text is not None:
            return self._chunks_from_text(document, document.text)
        if not document.path:
            raise ValueError("Document must contain either path or text")
        path = Path(document.path)
        if not path.exists():
            raise FileNotFoundError(path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(document, path)
        # Same derivation as _parse_pdf and DocumentStore.put: the evidence
        # deep-link is built from this id, and it must resolve in the store for
        # every file type, not only PDF.
        doc_id = stable_id(str(path.resolve()), document.display_name())
        if suffix == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            text = json.dumps(raw, ensure_ascii=False, indent=2)
            return self._chunks_from_text(document, text, doc_id=doc_id)
        if suffix in {".txt", ".md", ".csv", ".yaml", ".yml"}:
            return self._chunks_from_text(
                document, path.read_text(encoding="utf-8", errors="ignore"), doc_id=doc_id
            )
        if suffix == ".docx":
            return self._chunks_from_text(document, docx_text(path), doc_id=doc_id)
        if suffix in {".html", ".htm"}:
            return self._chunks_from_text(
                document, html_text(path.read_text(encoding="utf-8", errors="ignore")), doc_id=doc_id
            )
        raise ValueError(f"Unsupported file type: {suffix}")

    def _parse_pdf(self, document: DocumentInput, path: Path) -> list[EvidenceChunk]:
        chunks: list[EvidenceChunk] = []
        doc_id = stable_id(str(path.resolve()), document.display_name())
        pdf = fitz.open(path)
        # Text no reader can see is dropped here, before it can become a claim
        # or a passage, and recorded for gate G8 (parsers/integrity.py).
        visible = [visible_blocks(page) for page in pdf]
        hidden_boxes = {n: [s["bbox"] for s in hidden] for n, (_, hidden) in enumerate(visible, start=1) if hidden}
        for _, hidden in visible:
            self.hidden.extend(
                {**record, "source_name": document.display_name(), "doc_id": doc_id,
                 "role": str(getattr(document.role, "value", document.role)),
                 "source_type": str(getattr(document.source_type, "value", document.source_type))}
                for record in merge(hidden)
            )
        regions = getattr(self.settings, "layout_regions", False)
        table_map = (self._extract_tables(path, hidden_boxes)
                     if self.settings.extract_tables and not regions else {})
        for page_index, page in enumerate(pdf, start=1):
            blocks = sorted(visible[page_index - 1][0], key=lambda b: (round(b[1], 1), round(b[0], 1)))
            page_text = "\n".join(normalize_text(block[4]) for block in blocks if normalize_text(block[4]))
            used_ocr = False
            quality: dict = {}
            # A text layer from a legacy font (TCVN3, VNI) extracts as "hi~u lµc":
            # such a page is read by OCR like a scan (parsers/text_quality.py).
            garbled = garbled_share(page_text) if len(page_text) >= self.settings.min_native_text_chars else 0.0
            if garbled >= GARBLED_PAGE:
                quality["native_text_garbled"] = round(garbled, 2)
            needs_ocr = len(page_text) < self.settings.min_native_text_chars or garbled >= GARBLED_PAGE
            if needs_ocr and self.settings.ocr_enabled and self.ocr.available:
                reading = self.ocr.read_page(page)
                if normalize_text(reading.text):
                    page_text = normalize_text(reading.text)
                    used_ocr = True
                    quality.update(reading.summary())
            elif needs_ocr and (garbled >= GARBLED_PAGE or page.get_images(full=False)):
                # A scanned page, or a garbled text layer, and no OCR to read it:
                # its content is missing from the analysis, which gate G9 says.
                quality["unread"] = True
            tables: list = []
            if regions:
                # page-regions-v1: the same page read as typed regions -- prose in column order, tables as
                # rows with their caption, headers, unit and period (parsers/layout.py). A scanned page is
                # laid out from the boxes Tesseract gives each word.
                units = (page_layout.lines_from_words(page_layout.ocr_words(reading)) if used_ocr
                         else page_layout.lines_from_page(page, hidden_boxes.get(page_index, ())))
                laid = page_layout.analyze(units, page.rect.width, None if used_ocr else page)
                if laid.text or laid.tables:
                    page_text = laid.text
                    tables = laid.tables if self.settings.extract_tables else []
            if used_ocr or quality:
                self.reading.append({"source_name": document.display_name(), "doc_id": doc_id, "page": page_index,
                                     "role": str(getattr(document.role, "value", document.role)),
                                     "ocr": used_ocr, **quality})
            for block_index, text in enumerate(self._window(page_text), start=1):
                chunks.append(
                    EvidenceChunk(
                        chunk_id=stable_id(doc_id, str(page_index), str(block_index), text),
                        doc_id=doc_id,
                        source_name=document.display_name(),
                        role=document.role,
                        source_type=document.source_type,
                        text=text,
                        page=page_index,
                        block_index=block_index,
                        metadata={**document.metadata, "ocr": used_ocr, **_quality_for(quality, text)},
                    )
                )
            for table_index, table in enumerate(tables, start=1):
                table_text = "TABLE\n" + table.render()
                chunks.append(
                    EvidenceChunk(
                        chunk_id=stable_id(doc_id, str(page_index), "table", str(table_index), table_text),
                        doc_id=doc_id,
                        source_name=document.display_name(),
                        role=document.role,
                        source_type=document.source_type,
                        text=table_text,
                        page=page_index,
                        block_index=10_000 + table_index,
                        is_table=True,
                        metadata={**document.metadata, "table_index": table_index, "ocr": used_ocr,
                                  "table": table.to_dict()},
                    )
                )
            for table_index, table_text in enumerate(table_map.get(page_index, []), start=1):
                chunks.append(
                    EvidenceChunk(
                        chunk_id=stable_id(doc_id, str(page_index), "table", str(table_index), table_text),
                        doc_id=doc_id,
                        source_name=document.display_name(),
                        role=document.role,
                        source_type=document.source_type,
                        text=table_text,
                        page=page_index,
                        block_index=10_000 + table_index,
                        is_table=True,
                        metadata={**document.metadata, "table_index": table_index},
                    )
                )
        pdf.close()
        return chunks

    def _extract_tables(self, path: Path, hidden_boxes: dict[int, list] | None = None) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {}
        hidden_boxes = hidden_boxes or {}
        try:
            with pdfplumber.open(path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    boxes = hidden_boxes.get(page_number)
                    if boxes:
                        page = page.filter(lambda obj, boxes=boxes: not (
                            obj.get("object_type") == "char"
                            and any(inside((obj["x0"], obj["top"], obj["x1"], obj["bottom"]), box) for box in boxes)
                        ))
                    tables = page.extract_tables() or []
                    encoded: list[str] = []
                    for table in tables:
                        if self.settings.table_shape_filter and not is_data_table(table):
                            continue
                        rows = []
                        for row in table:
                            cells = [normalize_text(cell or "") for cell in row]
                            if any(cells):
                                rows.append(" | ".join(cells))
                        if rows:
                            encoded.append("TABLE\n" + "\n".join(rows))
                    if encoded:
                        result[page_number] = encoded
        except Exception:
            return {}
        return result

    def _chunks_from_text(
        self, document: DocumentInput, text: str, doc_id: str | None = None
    ) -> list[EvidenceChunk]:
        text = normalize_text(text)
        # Inline text has no path, so its id comes from the content itself.
        doc_id = doc_id or stable_id(document.display_name(), text[:500])
        chunks = []
        for index, part in enumerate(self._window(text), start=1):
            chunks.append(
                EvidenceChunk(
                    chunk_id=stable_id(doc_id, str(index), part),
                    doc_id=doc_id,
                    source_name=document.display_name(),
                    role=document.role,
                    source_type=document.source_type,
                    text=part,
                    block_index=index,
                    metadata=document.metadata,
                )
            )
        return chunks

    def _window(self, text: str) -> Iterable[str]:
        """Passages of a few sentences, never crossing a paragraph break.

        A passage is what a stance and a figure comparison are made against, so
        it has to be about one thing. With 1,400-character windows the demo's
        legal notice was a single chunk, and its "vi phạm" (about hazardous-waste
        storage) refuted every claim it was retrieved for, while the financial
        note's 12% (emissions) was compared against a 50% (renewables) claim.
        """
        text = normalize_text(text)
        if not text:
            return []
        size = max(120, self.settings.chunk_size_chars)
        max_sentences = max(1, self.settings.max_sentences_per_chunk)
        output: list[str] = []
        for paragraph in re.split(r"\n\s*\n", text):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            sentences = _sentences(paragraph)
            window: list[str] = []
            length = 0
            for sentence in sentences:
                if window and (length + len(sentence) > size or len(window) >= max_sentences):
                    output.append(" ".join(window))
                    window, length = [], 0
                window.append(sentence)
                length += len(sentence) + 1
            if window:
                output.append(" ".join(window))
        return output


TABLE_MIN_FILLED_ROWS = 2
TABLE_MAX_CELL_LINES = 12


def is_data_table(table: list[list[str | None]]) -> bool:
    """A grid of values, not the frame of a page layout (table-shape-v1).

    pdfplumber returns any ruled rectangle as a table. On a designed report most of them are a sidebar, a
    banner or a whole infographic page in one cell, read line by line across its columns: Hòa Phát's page 9
    gave "Hoàn thành kiểm kê khí nhà kính theo tiêu 90%", where the 90% belongs to the box beside it. The
    page text read block by block already holds those words in the right order.
    """
    rows = [[(cell or "").strip() for cell in row] for row in table]
    if sum(1 for row in rows if sum(1 for cell in row if cell) >= 2) < TABLE_MIN_FILLED_ROWS:
        return False
    return not any(cell.count("\n") >= TABLE_MAX_CELL_LINES - 1 for row in rows for cell in row)


def _sentences(paragraph: str) -> list[str]:
    """Sentences of one paragraph; a line that ends without punctuation is its own sentence.

    Short fragments (a heading, a table label) stay attached to the following
    sentence rather than becoming a passage of their own, so a citation still
    lands on readable text.
    """
    paragraph = join_wrapped_lines(paragraph)
    parts = [p.strip(" •\t") for p in re.split(r"(?<=[.!?;])\s+|\n+", paragraph) if p.strip()]
    merged: list[str] = []
    for part in parts:
        if merged and len(merged[-1]) < 40:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged
