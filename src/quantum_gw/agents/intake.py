from __future__ import annotations

from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.settings import IntakeSettings
from quantum_gw.storage.audit import AuditLogger


class DocumentIntakeAgent:
    def __init__(self, settings: IntakeSettings, audit: AuditLogger):
        self.parser = DocumentParser(settings)
        self.audit = audit

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
        return all_chunks
