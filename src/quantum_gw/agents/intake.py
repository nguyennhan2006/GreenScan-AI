from __future__ import annotations

import re

from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.settings import IntakeSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.security import describe, scan_injection

# Hidden text shorter than this many letters (a stray bullet, a page number in
# the page colour) is kept in the audit log but does not hold the run for review.
MIN_HIDDEN_LETTERS = 20


class DocumentIntakeAgent:
    def __init__(self, settings: IntakeSettings, audit: AuditLogger):
        self.parser = DocumentParser(settings)
        self.audit = audit
        # What gate G8 reports: hidden text and sentences addressed to the grader.
        self.integrity: list[dict] = []
        # What gate G9 reports: pages read by OCR, garbled or left unread.
        self.reading: list[dict] = []

    def run(self, documents: list[DocumentInput]) -> list[EvidenceChunk]:
        all_chunks: list[EvidenceChunk] = []
        for document in documents:
            chunks = self.parser.parse(document)
            self.audit.write(
                "document_parsed",
                {
                    "name": document.display_name(),
                    "role": document.role,
                    "source_type": document.source_type,
                    "chunks": len(chunks),
                },
            )
            all_chunks.extend(chunks)
        self.integrity = integrity_findings(self.parser.hidden, all_chunks)
        if self.parser.hidden:
            self.audit.write("hidden_text_removed", {"records": self.parser.hidden})
        if self.integrity:
            self.audit.write("document_integrity", {"findings": self.integrity})
        self.reading = list(self.parser.reading)
        if self.reading:
            self.audit.write("document_reading", {"pages": self.reading})
        return all_chunks


def integrity_findings(hidden: list[dict], chunks: list[EvidenceChunk]) -> list[dict]:
    """Hidden text worth a look, and every passage that speaks to the grader, once per page.

    `blocking` says whether the finding holds the run for a person (gate G8).
    Print below 2 pt alone does not: on 120 real PDFs (11/11/2026) it was digital
    signature stamps, product names on packshots and 0.8 pt page thumbnails of an
    annual report. Text drawn in the background colour or invisibly over an empty
    area was rarer (2 of 120 files with a sentence or more) and has no innocent
    reason to be in a report a company submits, so it does.
    """
    findings: list[dict] = []
    for record in hidden:
        hits = scan_injection(record["text"])
        if not hits and len(re.findall(r"[^\W\d_]", record["text"])) < MIN_HIDDEN_LETTERS:
            continue
        findings.append({
            "kind": "hidden_text", "source_name": record["source_name"], "doc_id": record["doc_id"],
            "role": record["role"], "page": record["page"], "reason": record["label"],
            "instruction": describe(hits), "text": record["text"][:400],
            "blocking": bool(hits) or record["reason"] != "tiny",
        })
    seen: set[tuple] = set()
    for chunk in chunks:
        hits = scan_injection(chunk.text)
        if not hits:
            continue
        key = (chunk.doc_id, chunk.page, tuple(h["match"] for h in hits))
        if key in seen:     # overlapping windows repeat the same sentence
            continue
        seen.add(key)
        findings.append({
            "kind": "instruction", "source_name": chunk.source_name, "doc_id": chunk.doc_id,
            "role": str(getattr(chunk.role, "value", chunk.role)), "page": chunk.page,
            "reason": describe(hits), "categories": [h["category"] for h in hits],
            "text": _offending_sentence(chunk.text), "blocking": True,
        })
    return findings


def _offending_sentence(text: str) -> str:
    """The sentence a reviewer should read, in the document's own words (the match is folded)."""
    for sentence in re.split(r"(?<=[.!?;\n])\s+", text):
        if scan_injection(sentence):
            return sentence.strip()[:400]
    return text.strip()[:400]
