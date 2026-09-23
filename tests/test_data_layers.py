"""The raw / clean / extract contract (docs/04-data-ai/DATA_LAYERS.md).

A layer is only worth having if a bad row fails loudly, so these check three
things: a run writes all three layers and they validate; a field a row's origin
requires is reported when absent; and a sentence the extractor refused is kept
with the reason, not dropped.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.data.builders import clean_from_crawl, extract_from_crawl_candidate, raw_from_crawl
from quantum_gw.data.layers import LAYERS, ExtractType, missing_required
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput

CLAIM_TEXT = (
    "Tập đoàn giảm 20% phát thải khí nhà kính Scope 1 và 2 trong năm 2024 so với năm 2020.\n"
    "XANH HOÁ SẢN XUẤT\n"
    "Tấn 131.639 306-4 Chất thải được chuyển giao khỏi quy trình xử lý\n"
)
EVIDENCE_TEXT = "Kiểm toán môi trường: phát thải khí nhà kính Scope 1 và 2 năm 2024 giảm 20% so với 2020."


def _run(settings):
    documents = [
        DocumentInput(name="claim.txt", text=CLAIM_TEXT, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=EVIDENCE_TEXT, role=DocumentRole.EVIDENCE,
                      source_type=SourceType.EXTERNAL),
    ]
    result = OrchestratorAgent(settings).run(documents)
    return Path(result.output_directory) / "contract"


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture
def layers(settings):
    directory = _run(settings)
    return {name: _rows(directory / f"{name}.jsonl") for name in LAYERS}


def test_a_run_writes_all_three_layers(layers):
    assert layers["raw"] and layers["clean"] and layers["extract"]


def test_every_row_validates_against_the_contract(layers):
    for name, rows in layers.items():
        for row in rows:
            LAYERS[name].model_validate(row)


def test_provenance_chains_from_extract_to_raw(layers):
    raw_ids = {row["doc_id"] for row in layers["raw"]}
    unit_ids = {row["unit_id"] for row in layers["clean"]}
    assert {row["doc_id"] for row in layers["clean"]} <= raw_ids
    for row in layers["extract"]:
        assert row["unit_id"] in unit_ids
        assert row["doc_id"] in raw_ids
        assert row["text_sha256"]


def test_rejected_sentences_are_kept_with_a_reason(layers):
    rejected = [r for r in layers["extract"] if r["extract_type"] == ExtractType.REJECTED_SENTENCE.value]
    assert rejected, "a heading and a table row were fed in; both must be recorded, not dropped"
    assert {"caps_run", "table_row"} & {r["rejected_reason"] for r in rejected}
    assert all(r["rejected_reason"] for r in rejected)


def test_claims_carry_numeric_facts_with_their_dimensions(layers):
    claims = [r for r in layers["extract"] if r["extract_type"] == ExtractType.CLAIM.value]
    facts = [fact for row in claims for fact in row["numeric_facts"]]
    assert facts, "the claim states 20% and two scopes"
    assert all(fact["policy_id"] == "comparison-policy-v2" for fact in facts)
    assert any(fact["basis"] == "percentage_change" for fact in facts)


def test_a_missing_required_field_is_reported_per_origin():
    corpus_row = {"origin": "corpus", "doc_id": "d1", "text_sha256": "x", "split": "unassigned"}
    assert missing_required(corpus_row, "clean") == ["split"]
    run_row = dict(corpus_row, origin="run")
    assert missing_required(run_row, "clean") == []


def test_an_unknown_field_is_rejected_rather_than_kept(layers):
    row = dict(layers["clean"][0])
    row["invented_field"] = 1
    with pytest.raises(ValidationError):
        LAYERS["clean"].model_validate(row)


def test_crawl_rows_convert_to_the_same_shapes():
    raw = raw_from_crawl(
        {"document_id": "D1", "sha256": "a" * 64, "document_type": "sustainability_report",
         "downloaded_at": "2026-08-07T10:00:00Z", "object_path": "objects/sha256/aa",
         "source_authority": "company", "publication_year": "2024", "ticker": "HPG"},
        producer_version="test",
    )
    assert raw.origin == "corpus" and raw.reporting_year == 2024
    assert missing_required(raw.model_dump(mode="json"), "raw") == []

    clean = clean_from_crawl(
        {"chunk_id": "C1", "document_id": "D1", "text": "Phát thải giảm 20% trong năm 2024.",
         "split": "train", "unit_type": "paragraph", "publication_year": "2024"},
        producer_version="test", doc_sha256="a" * 64,
    )
    assert clean.split == "train" and clean.char_count == len(clean.text)

    extract = extract_from_crawl_candidate(
        {"candidate_id": "E1", "chunk_id": "C1", "document_id": "D1", "text": "Phát thải giảm 20% năm 2024.",
         "sentence_index": 0, "has_number": True},
        producer_version="test", extract_type=ExtractType.EVIDENCE_CANDIDATE,
    )
    assert extract.extract_type == ExtractType.EVIDENCE_CANDIDATE.value
    assert extract.numeric_facts and extract.numeric_facts[0].unit == "%"
