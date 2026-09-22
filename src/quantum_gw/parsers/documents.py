from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path

import fitz
import pdfplumber

from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.settings import IntakeSettings
from quantum_gw.utils.text import normalize_text, stable_id

from .ocr import TesseractOCR


class DocumentParser:
    def __init__(self, settings: IntakeSettings):
        self.settings = settings
        self.ocr = TesseractOCR(settings.tesseract_command, settings.ocr_languages)

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
        raise ValueError(f"Unsupported file type: {suffix}")

    def _parse_pdf(self, document: DocumentInput, path: Path) -> list[EvidenceChunk]:
        chunks: list[EvidenceChunk] = []
        doc_id = stable_id(str(path.resolve()), document.display_name())
        pdf = fitz.open(path)
        table_map = self._extract_tables(path) if self.settings.extract_tables else {}
        for page_index, page in enumerate(pdf, start=1):
            blocks = sorted(page.get_text("blocks"), key=lambda b: (round(b[1], 1), round(b[0], 1)))
            page_text = "\n".join(normalize_text(block[4]) for block in blocks if normalize_text(block[4]))
            used_ocr = False
            if len(page_text) < self.settings.min_native_text_chars and self.settings.ocr_enabled:
                page_text = normalize_text(self.ocr.ocr_page(page))
                used_ocr = bool(page_text)
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
                        metadata={**document.metadata, "ocr": used_ocr},
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

    def _extract_tables(self, path: Path) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {}
        try:
            with pdfplumber.open(path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []
                    encoded: list[str] = []
                    for table in tables:
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


def _sentences(paragraph: str) -> list[str]:
    """Sentences of one paragraph; a line that ends without punctuation is its own sentence.

    Short fragments (a heading, a table label) stay attached to the following
    sentence rather than becoming a passage of their own, so a citation still
    lands on readable text.
    """
    parts = [p.strip(" •\t") for p in re.split(r"(?<=[.!?;])\s+|\n+", paragraph) if p.strip()]
    merged: list[str] = []
    for part in parts:
        if merged and len(merged[-1]) < 40:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged
