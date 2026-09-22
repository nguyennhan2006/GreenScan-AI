"""The doc_id in a served result must resolve in the DocumentStore.

The evidence card's deep link is built from ``RetrievedEvidence.doc_id``; if
the parser and the store derive that id differently the link is a 404 and the
reviewer cannot open the page the citation points at.
"""

from __future__ import annotations

from pathlib import Path

from quantum_gw.agents.intake import DocumentIntakeAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.storage.documents import DocumentStore


def _chunks(settings, store: DocumentStore, name: str, data: bytes):
    record = store.put(data, name)
    document = DocumentInput(
        path=str(record.path), name=name, role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL
    )
    audit = AuditLogger(store.root / "audit.jsonl")
    return record, DocumentIntakeAgent(settings.intake, audit).run([document])


def test_text_upload_doc_id_matches_store(settings, tmp_path: Path):
    store = DocumentStore(tmp_path / "documents")
    record, chunks = _chunks(settings, store, "evidence.txt", "Phát thải năm 2024 giảm 12%.".encode())
    assert chunks
    assert {c.doc_id for c in chunks} == {record.doc_id}
    assert store.get(chunks[0].doc_id) is not None


def test_pdf_upload_doc_id_matches_store(settings, tmp_path: Path):
    pdf = Path("data/real_cases/cases/KLM-2024/KLM-2024_case_packet.pdf").read_bytes()
    store = DocumentStore(tmp_path / "documents")
    record, chunks = _chunks(settings, store, "KLM-2024_case_packet.pdf", pdf)
    assert chunks
    assert {c.doc_id for c in chunks} == {record.doc_id}
    assert store.get(chunks[0].doc_id) is not None
