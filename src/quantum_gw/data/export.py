"""Write a run's three layers next to its evidence pack.

Every run already writes `manifest.json`, `result.json`, `audit.jsonl` and
`evidence_pack.md`. This adds `contract/raw.jsonl`, `contract/clean.jsonl` and
`contract/extract.jsonl` in the shape of `quantum_gw.data.layers`, so the data
a run consumed and produced can be validated, counted and labelled with the
same tools as the crawled corpus — and so a dataset card can be built from runs
as well as from crawls.

The clean layer holds *every* parsed unit, not only the ones retrieval chose,
and the extract layer holds every rejected sentence with its reason. What the
system ignored is a reviewer's question, and a silent drop cannot be audited.
"""

from __future__ import annotations

from pathlib import Path

from quantum_gw.data.builders import (
    clean_from_chunk,
    extract_from_claim,
    extract_from_figure,
    extract_from_rejected,
    raw_from_document,
    write_jsonl,
)
from quantum_gw.domain.models import Claim, DocumentInput, EvidenceChunk


def _doc_ids(documents: list[DocumentInput], chunks: list[EvidenceChunk]) -> dict[int, str]:
    """doc_id per input document, taken from the chunks the parser produced.

    The parser derives the id from the resolved path (or the text), and the
    chunks carry it; re-deriving it here would be a second implementation of
    the same rule and a chance for the two to drift.
    """
    by_name: dict[str, str] = {}
    for chunk in chunks:
        by_name.setdefault(chunk.source_name, chunk.doc_id)
    ids: dict[int, str] = {}
    for index, document in enumerate(documents):
        name = document.display_name()
        if name in by_name:
            ids[index] = by_name[name]
    return ids


def write_run_layers(
    directory: Path,
    *,
    run_id: str,
    producer_version: str,
    documents: list[DocumentInput],
    chunks: list[EvidenceChunk],
    claims: list[Claim],
    rejected: list[tuple[EvidenceChunk, int, str, str]],
    figures: list | None = None,
) -> dict[str, int]:
    directory = Path(directory)
    ids = _doc_ids(documents, chunks)
    raw_rows = []
    digests: dict[str, str] = {}
    for index, document in enumerate(documents):
        doc_id = ids.get(index)
        if doc_id is None:
            continue  # a document that produced no chunk: recorded by the gates, not here
        row = raw_from_document(document, doc_id, run_id=run_id, producer_version=producer_version)
        digests[doc_id] = row.sha256
        raw_rows.append(row)

    clean_rows = [
        clean_from_chunk(
            chunk, run_id=run_id, producer_version=producer_version,
            doc_sha256=digests.get(chunk.doc_id),
        )
        for chunk in chunks
    ]
    extract_rows = [
        extract_from_claim(claim, run_id=run_id, producer_version=producer_version)
        for claim in claims
    ]
    extract_rows += [
        extract_from_figure(figure, run_id=run_id, producer_version=producer_version)
        for figure in (figures or [])
    ]
    extract_rows += [
        extract_from_rejected(
            chunk, sentence, reason, index,
            run_id=run_id, producer_version=producer_version,
        )
        for chunk, index, sentence, reason in rejected
    ]
    return {
        "raw": write_jsonl(directory / "raw.jsonl", raw_rows),
        "clean": write_jsonl(directory / "clean.jsonl", clean_rows),
        "extract": write_jsonl(directory / "extract.jsonl", extract_rows),
    }


