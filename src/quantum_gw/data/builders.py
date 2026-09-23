"""Build the three layers from what the pipeline and the crawler already produce.

Two producers, one contract (see `layers.py`):

    run     DocumentInput -> RawDocument, EvidenceChunk -> CleanUnit,
            Claim / rejected sentence -> ExtractRecord
    corpus  data/crawl/vn30/normalized/*.jsonl -> the same three shapes

Nothing here re-reads a PDF or re-runs a model: it renames and completes fields
that exist, and computes the numeric-fact dimensions with the same code the
verifier uses, so a fact in the dataset and a fact in a verdict are the same
object.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from quantum_gw.data.layers import (
    CleanUnit,
    DocumentType,
    ExtractRecord,
    ExtractType,
    NumericFactFields,
    Origin,
    RawDocument,
    SourceAuthority,
    Split,
    UnitType,
    text_sha256,
)
from quantum_gw.domain.models import Claim, DocumentInput, EvidenceChunk
from quantum_gw.utils.text import file_sha256, split_sentences
from quantum_gw.verification.numeric_facts import POLICY_ID, facts_in


def _now() -> datetime:
    return datetime.now(UTC)


def _fact_fields(text: str) -> list[NumericFactFields]:
    facts = []
    for sentence in split_sentences(text) or [text]:
        for fact in facts_in(sentence):
            facts.append(
                NumericFactFields(
                    value=fact.value,
                    unit=fact.unit,
                    half_precision=fact.half,
                    basis=fact.basis,
                    boundary=fact.boundary,
                    technology=fact.technology,
                    variant=sorted(fact.variant),
                    scopes=sorted(fact.scopes),
                    is_target=fact.is_target,
                    policy_id=POLICY_ID,
                )
            )
    return facts


# --------------------------------------------------------------------------- run


_DOCUMENT_TYPE_HINTS = (
    ("phat trien ben vung", DocumentType.SUSTAINABILITY_REPORT),
    ("sustainability", DocumentType.SUSTAINABILITY_REPORT),
    ("esg", DocumentType.SUSTAINABILITY_REPORT),
    ("thuong nien", DocumentType.ANNUAL_REPORT),
    ("annual", DocumentType.ANNUAL_REPORT),
    ("tai chinh", DocumentType.FINANCIAL_STATEMENT),
    ("financial", DocumentType.FINANCIAL_STATEMENT),
    ("quan tri", DocumentType.GOVERNANCE_REPORT),
    ("order", DocumentType.LEGAL_DECISION),
    ("judgment", DocumentType.LEGAL_DECISION),
)


def guess_document_type(name: str, declared: str | None = None) -> DocumentType:
    """Document type from the metadata when it is given, else from the file name."""
    if declared:
        try:
            return DocumentType(declared)
        except ValueError:
            pass
    from quantum_gw.utils.text import normalize_for_match

    folded = normalize_for_match(name)
    for needle, kind in _DOCUMENT_TYPE_HINTS:
        if needle in folded:
            return kind
    return DocumentType.OTHER


def raw_from_document(
    document: DocumentInput,
    doc_id: str,
    *,
    run_id: str,
    producer_version: str,
) -> RawDocument:
    """A run's input document as a raw row; `metadata` supplies anything the run knows."""
    meta = dict(document.metadata or {})
    name = document.display_name()
    if document.path:
        path = Path(document.path)
        digest = file_sha256(str(path))
        byte_size = path.stat().st_size if path.exists() else None
    else:
        digest = hashlib.sha256((document.text or "").encode("utf-8")).hexdigest()
        byte_size = len((document.text or "").encode("utf-8"))
    return RawDocument(
        origin=Origin.RUN,
        producer="parser",
        producer_version=producer_version,
        produced_at=_now(),
        run_id=run_id,
        doc_id=doc_id,
        sha256=digest,
        url=meta.get("url"),
        source_authority=SourceAuthority(meta.get("source_authority", SourceAuthority.UNKNOWN)),
        retrieved_by=meta.get("retrieved_by", "upload"),
        access_date=_as_date(meta.get("access_date")),
        licence_note=meta.get("licence_note"),
        organization_name=meta.get("organization_name"),
        company_id=meta.get("company_id"),
        ticker=meta.get("ticker"),
        jurisdiction=meta.get("jurisdiction"),
        sector=meta.get("sector"),
        title=meta.get("title"),
        document_type=guess_document_type(name, meta.get("document_type")),
        reporting_year=_as_int(meta.get("reporting_year")),
        language=document.language,
        file_name=name,
        media_type=meta.get("media_type"),
        byte_size=byte_size,
        object_path=str(document.path) if document.path else None,
        role=document.role.value,
        source_type=document.source_type.value,
        metadata={k: v for k, v in meta.items() if k not in _RAW_META_CONSUMED},
    )


_RAW_META_CONSUMED = {
    "url", "source_authority", "retrieved_by", "access_date", "licence_note",
    "organization_name", "company_id", "ticker", "jurisdiction", "sector", "title",
    "document_type", "reporting_year", "media_type",
}


def clean_from_chunk(
    chunk: EvidenceChunk,
    *,
    run_id: str,
    producer_version: str,
    doc_sha256: str | None = None,
) -> CleanUnit:
    meta = dict(chunk.metadata or {})
    flags: list[str] = []
    if meta.get("ocr"):
        flags.append("ocr_used")
    if chunk.is_table:
        flags.append("table_parse_low_confidence")
    return CleanUnit(
        origin=Origin.RUN,
        producer="parser",
        producer_version=producer_version,
        produced_at=_now(),
        run_id=run_id,
        unit_id=chunk.chunk_id,
        doc_id=chunk.doc_id,
        doc_sha256=doc_sha256,
        source_name=chunk.source_name,
        text=chunk.text,
        text_sha256=text_sha256(chunk.text),
        char_count=len(chunk.text),
        page=chunk.page,
        block_index=chunk.block_index,
        unit_type=UnitType.TABLE if chunk.is_table else UnitType.PARAGRAPH,
        is_table=chunk.is_table,
        table_index=meta.get("table_index"),
        used_ocr=bool(meta.get("ocr")),
        normalizations=["nfkc", "join_wrapped_lines", "whitespace"],
        split=Split.UNASSIGNED,
        quality_flags=flags,
        role=chunk.role.value,
        source_type=chunk.source_type.value,
        metadata={k: v for k, v in meta.items() if k not in {"ocr", "table_index"}},
    )


def extract_from_claim(claim: Claim, *, run_id: str, producer_version: str) -> ExtractRecord:
    return ExtractRecord(
        origin=Origin.RUN,
        producer="claim_extractor",
        producer_version=producer_version,
        produced_at=_now(),
        run_id=run_id,
        extract_id=claim.claim_id,
        extract_type=ExtractType.CLAIM,
        unit_id=claim.source_chunk_id,
        doc_id=claim.source_doc_id,
        page=claim.source_page,
        text=claim.text,
        text_sha256=text_sha256(claim.text),
        language=claim.language,
        claim_type=claim.claim_type,
        metric=claim.metric,
        direction=claim.direction,
        values=list(claim.values),
        units=list(claim.units),
        period=claim.period,
        baseline=claim.baseline,
        scope=claim.scope,
        is_future_commitment=claim.is_future_commitment,
        is_vague=claim.is_vague,
        vague_terms_matched=list(claim.vague_terms_matched),
        confidence=claim.confidence,
        numeric_facts=_fact_fields(claim.text),
        has_number=bool(claim.values),
    )


def extract_from_rejected(
    chunk: EvidenceChunk,
    sentence: str,
    reason: str,
    index: int,
    *,
    run_id: str,
    producer_version: str,
) -> ExtractRecord:
    """A sentence the extractor refused, kept with the reason it was refused."""
    return ExtractRecord(
        origin=Origin.RUN,
        producer="claim_extractor",
        producer_version=producer_version,
        produced_at=_now(),
        run_id=run_id,
        extract_id=hashlib.sha256(f"{chunk.chunk_id}:{index}:{sentence}".encode()).hexdigest()[:16],
        extract_type=ExtractType.REJECTED_SENTENCE,
        unit_id=chunk.chunk_id,
        doc_id=chunk.doc_id,
        page=chunk.page,
        sentence_index=index,
        text=sentence,
        text_sha256=text_sha256(sentence),
        rejected_reason=reason,
    )


# ------------------------------------------------------------------------ corpus


_CRAWL_DOCUMENT_TYPES = {
    "sustainability_report": DocumentType.SUSTAINABILITY_REPORT,
    "integrated_report": DocumentType.INTEGRATED_REPORT,
    "annual_report": DocumentType.ANNUAL_REPORT,
    "financial_statement": DocumentType.FINANCIAL_STATEMENT,
    "governance_report": DocumentType.GOVERNANCE_REPORT,
    "agm_document": DocumentType.AGM_DOCUMENT,
    "regulatory_record": DocumentType.REGULATORY_RECORD,
}

_CRAWL_AUTHORITY = {
    "company": SourceAuthority.COMPANY,
    "issuer": SourceAuthority.COMPANY,
    "exchange": SourceAuthority.EXCHANGE,
    "regulator": SourceAuthority.COURT_OR_REGULATOR,
    "government": SourceAuthority.GOVERNMENT,
    "auditor": SourceAuthority.AUDITOR,
    "press": SourceAuthority.PRESS,
}

_CRAWL_UNIT_TYPES = {
    "paragraph": UnitType.PARAGRAPH,
    "table": UnitType.TABLE,
    "heading": UnitType.HEADING,
    "list": UnitType.LIST_ITEM,
    "caption": UnitType.CAPTION,
}


def _as_int(value: Any) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    text = str(value)
    for cut in (10, 19):
        try:
            return datetime.fromisoformat(text[:cut].replace("Z", "")).date()
        except ValueError:
            continue
    return None


def raw_from_crawl(row: dict[str, Any], *, producer_version: str) -> RawDocument:
    """One row of data/crawl/vn30/normalized/documents.jsonl."""
    return RawDocument(
        origin=Origin.CORPUS,
        producer="crawler",
        producer_version=producer_version,
        produced_at=_now(),
        doc_id=str(row.get("document_id") or row.get("id")),
        sha256=str(row.get("sha256") or "").lower() or "0" * 64,
        url=row.get("url"),
        final_url=row.get("final_url"),
        source_page_url=row.get("source_page_url"),
        source_authority=_CRAWL_AUTHORITY.get(
            str(row.get("source_authority") or "").lower(), SourceAuthority.UNKNOWN
        ),
        retrieved_by="crawler",
        access_date=_as_date(row.get("downloaded_at") or row.get("discovered_at")),
        licence_note=(row.get("metadata_json") or {}).get("licence_note")
        if isinstance(row.get("metadata_json"), dict) else None,
        company_id=row.get("company_id"),
        ticker=row.get("ticker"),
        exchange=row.get("exchange"),
        title=row.get("title"),
        document_type=_CRAWL_DOCUMENT_TYPES.get(
            str(row.get("document_type") or "").lower(), DocumentType.OTHER
        ),
        reporting_year=_as_int(row.get("publication_year")),
        language=row.get("language") or "vi",
        media_type=row.get("content_type"),
        byte_size=_as_int(row.get("content_length")),
        page_count=_as_int(row.get("page_count")),
        object_path=row.get("object_path"),
        native_text_chars=_as_int(row.get("native_text_chars")),
        scan_like_ratio=row.get("scan_like_ratio"),
        role="evidence",
        source_type="internal",
        status="ok" if str(row.get("status", "ok")).lower() in {"ok", "downloaded"} else str(row.get("status")),
        error_message=row.get("error_message"),
    )


def clean_from_crawl(row: dict[str, Any], *, producer_version: str, doc_sha256: str | None = None) -> CleanUnit:
    """One row of data/crawl/vn30/normalized/chunks.jsonl."""
    text = row.get("text") or ""
    return CleanUnit(
        origin=Origin.CORPUS,
        producer="crawler",
        producer_version=producer_version,
        produced_at=_now(),
        unit_id=str(row.get("chunk_id") or row.get("unit_id")),
        doc_id=str(row.get("document_id")),
        doc_sha256=doc_sha256,
        source_name=str(row.get("ticker") or row.get("company_id") or row.get("document_id")),
        text=text,
        text_sha256=text_sha256(text),
        char_count=len(text),
        unit_type=_CRAWL_UNIT_TYPES.get(str(row.get("unit_type") or "").lower(), UnitType.PARAGRAPH),
        is_table=str(row.get("unit_type") or "").lower() == "table",
        block_index=_as_int(row.get("unit_index")),
        split=_split(row.get("split")),
        company_id=row.get("company_id"),
        reporting_year=_as_int(row.get("publication_year")),
        normalizations=["nfkc", "whitespace"],
        role="evidence",
        source_type="internal",
    )


def _split(value: Any) -> Split:
    try:
        return Split(str(value).lower())
    except ValueError:
        return Split.UNASSIGNED


def extract_from_crawl_candidate(
    row: dict[str, Any], *, producer_version: str, extract_type: ExtractType
) -> ExtractRecord:
    """One row of claim_candidates.jsonl or evidence_candidates.jsonl."""
    text = row.get("text") or ""
    return ExtractRecord(
        origin=Origin.CORPUS,
        producer="crawler",
        producer_version=producer_version,
        produced_at=_now(),
        extract_id=str(row.get("candidate_id")),
        extract_type=extract_type,
        unit_id=str(row.get("chunk_id")),
        doc_id=str(row.get("document_id")),
        sentence_index=_as_int(row.get("sentence_index")),
        text=text,
        text_sha256=text_sha256(text),
        numeric_facts=_fact_fields(text),
        has_number=bool(row.get("has_number") or row.get("numbers")),
        candidate_type=row.get("candidate_type"),
    )


def write_jsonl(path: Path, rows: Iterable[Any]) -> int:
    """Write records (pydantic models or dicts) as one JSON object per line."""
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = row.model_dump(mode="json") if hasattr(row, "model_dump") else row
            handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
            count += 1
    return count
