"""The three data layers — raw, clean, extract — as one contract.

The corpus (crawled reports, adjudicated case packs) and a pipeline run produce
the same three kinds of record, and until now they used different field names
for the same thing: `document_id`/`doc_id`, `unit_id`/`chunk_id`,
`publication_year`/`period`. One shape per layer removes that, so a dataset
card, a labelling queue and a working paper can be built from the same reader.

    raw      one acquired source document: where it came from, its bytes, its
             integrity and its licence to be used. Never edited after capture.
    clean    one unit of text after parsing, OCR, normalisation and dedup:
             a paragraph, a table, a heading — with the page it sits on.
    extract  one object read out of a clean unit: a claim, an evidence
             candidate, a numeric fact, and the reason a sentence was rejected.

`origin` says which producer wrote the row (`corpus` or `run`) and is the only
field whose value changes what may be missing: a crawled PDF has a URL and a
download date, an uploaded file in a run has neither.

Rules that hold for every row, in every layer:

* provenance is mandatory: a clean unit names its raw document, an extract row
  names its clean unit, and every row carries `sha256` of the bytes or text it
  came from, so a claim can be traced to a file a reviewer can open;
* nothing is dropped silently: a sentence the extractor refuses becomes an
  extract row with `rejected_reason`, because "what the system ignored" is a
  reviewer's question and a dataset statistic;
* versions travel with the data: `producer_version` on every row and
  `policy_id` on numeric facts, so two rows made by different code are never
  compared as if they were the same measurement.

JSON Schema for each layer is generated from these models by
`tools/data_contract.py schema` into `schemas/data/`; the models are the source
of truth, the JSON files are for other languages and for review.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "data-layers-v1"


class Origin(StrEnum):
    CORPUS = "corpus"
    RUN = "run"


class DocumentType(StrEnum):
    SUSTAINABILITY_REPORT = "sustainability_report"
    ANNUAL_REPORT = "annual_report"
    INTEGRATED_REPORT = "integrated_report"
    FINANCIAL_STATEMENT = "financial_statement"
    GOVERNANCE_REPORT = "governance_report"
    AGM_DOCUMENT = "agm_document"
    REGULATORY_RECORD = "regulatory_record"
    LEGAL_DECISION = "legal_decision"
    ASSURANCE_STATEMENT = "assurance_statement"
    PRESS = "press"
    LEGAL_INSTRUMENT = "legal_instrument"
    OTHER = "other"


class SourceAuthority(StrEnum):
    """Who stands behind the document — the evidence hierarchy of NEXT_COLLECTION_PLAN."""

    GOVERNMENT = "government"
    COURT_OR_REGULATOR = "court_or_regulator"
    AUDITOR = "auditor"
    ASSURANCE_PROVIDER = "assurance_provider"
    EXCHANGE = "exchange"
    COMPANY = "company"
    PRESS = "press"
    UNKNOWN = "unknown"


class UnitType(StrEnum):
    PARAGRAPH = "paragraph"
    TABLE = "table"
    TABLE_ROW = "table_row"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    CAPTION = "caption"
    CLAUSE = "clause"


class ExtractType(StrEnum):
    CLAIM = "claim"
    REJECTED_SENTENCE = "rejected_sentence"
    EVIDENCE_CANDIDATE = "evidence_candidate"
    NUMERIC_FACT = "numeric_fact"


class Split(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"
    HOLDOUT = "holdout"
    REVIEW = "review"       # year unknown or leakage unresolved: not usable yet
    UNASSIGNED = "unassigned"


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class _Record(BaseModel):
    """Fields every row of every layer carries."""

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    contract_version: str = CONTRACT_VERSION
    origin: Origin
    # What made this row: the crawler manifest id, or the pipeline run id.
    producer: str = Field(description="crawler | parser | claim_extractor | verifier | manual")
    producer_version: str
    produced_at: datetime
    run_id: str | None = Field(default=None, description="set when origin=run")


class RawDocument(_Record):
    """One acquired source document, as captured. Never edited after capture."""

    layer: Literal["raw"] = "raw"
    doc_id: str = Field(description="stable id; the clean layer references it")
    sha256: str = Field(min_length=64, max_length=64, description="of the bytes as downloaded")

    # where it came from
    url: str | None = None
    final_url: str | None = Field(default=None, description="after redirects")
    source_page_url: str | None = Field(default=None, description="the IR/listing page it was found on")
    source_authority: SourceAuthority = SourceAuthority.UNKNOWN
    retrieved_by: str = Field(default="unknown", description="crawler | manual | upload | fixture")
    access_date: date | None = Field(default=None, description="mandatory for corpus rows")
    licence_note: str | None = Field(
        default=None, description="why this file may be stored and quoted (COLLECTION_PLAN_v2 §2.5)"
    )

    # who published it
    organization_name: str | None = None
    company_id: str | None = None
    ticker: str | None = None
    exchange: str | None = None
    jurisdiction: str | None = None
    sector: str | None = None

    # what it is
    title: str | None = None
    document_type: DocumentType = DocumentType.OTHER
    reporting_year: int | None = Field(default=None, description="the period the document reports on")
    publication_date: date | None = None
    language: str = "vi"

    # the file itself
    file_name: str | None = None
    media_type: str | None = None
    byte_size: int | None = None
    page_count: int | None = None
    object_path: str | None = Field(default=None, description="content-addressed path; bytes are not committed")
    native_text_chars: int | None = Field(default=None, description="text layer size; 0 means a scan")
    scan_like_ratio: float | None = Field(default=None, ge=0, le=1)

    # how the pipeline is allowed to treat it
    role: str = Field(default="evidence", description="claim_source | evidence | reference")
    source_type: str = Field(default="internal", description="internal | financial | environmental | legal | external | standard")

    status: str = Field(default="ok", description="ok | download_failed | parse_failed | excluded")
    error_message: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CleanUnit(_Record):
    """One unit of text after parsing, OCR, normalisation and dedup."""

    layer: Literal["clean"] = "clean"
    unit_id: str
    doc_id: str = Field(description="the raw row this came from")
    doc_sha256: str | None = Field(default=None, description="integrity link to the raw row")
    source_name: str

    text: str
    text_sha256: str
    char_count: int
    language: str = "vi"

    # where in the document
    page: int | None = None
    block_index: int | None = None
    unit_type: UnitType = UnitType.PARAGRAPH
    is_table: bool = False
    table_index: int | None = None
    row_index: int | None = Field(default=None, description="cell provenance; null until E3 lands")
    column_index: int | None = None

    # how it was produced
    used_ocr: bool = False
    ocr_confidence: float | None = Field(default=None, ge=0, le=1)
    normalizations: list[str] = Field(
        default_factory=list,
        description="applied steps, e.g. nfkc, join_wrapped_lines, whitespace",
    )

    # dedup and dataset bookkeeping
    duplicate_of: str | None = Field(default=None, description="unit_id kept instead of this one")
    split: Split = Split.UNASSIGNED
    company_id: str | None = None
    reporting_year: int | None = None

    # quality flags a reviewer or a filter acts on
    quality_flags: list[str] = Field(
        default_factory=list,
        description="low_text | scan_like | suspicious_instruction | truncated | table_parse_low_confidence",
    )
    role: str = "evidence"
    source_type: str = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class NumericFactFields(BaseModel):
    """The dimensions that decide whether two figures may be compared (N1/RQ2)."""

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    value: float
    unit: str | None = None
    half_precision: float | None = Field(default=None, description="half of the last significant digit")
    basis: str = "unknown"          # absolute | intensity | percentage_share | percentage_change | unknown
    boundary: str = "unknown"       # group | subsidiary | facility | project | unknown
    technology: str | None = None
    variant: list[str] = Field(default_factory=list)
    scopes: list[int] = Field(default_factory=list)
    is_target: bool = False
    policy_id: str = Field(default="comparison-policy-v2", description="the eligibility rule that read these")


class ExtractRecord(_Record):
    """One object read out of a clean unit — or one sentence the extractor refused."""

    layer: Literal["extract"] = "extract"
    extract_id: str
    extract_type: ExtractType
    unit_id: str = Field(description="the clean row this came from")
    doc_id: str
    page: int | None = None
    sentence_index: int | None = None

    text: str
    text_sha256: str
    language: str = "vi"

    # claim attributes (the five the rubric scores, plus what the extractor read)
    claim_type: str | None = None
    metric: str | None = None
    direction: str | None = Field(default=None, description="increase | decrease")
    values: list[float] = Field(default_factory=list)
    units: list[str] = Field(default_factory=list)
    period: str | None = None
    baseline: str | None = None
    scope: str | None = None
    is_future_commitment: bool = False
    is_vague: bool = False
    vague_terms_matched: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)

    # why a sentence did not become a claim — kept, never dropped
    rejected_reason: str | None = Field(
        default=None,
        description="caps_run | section_label | table_row | too_short | no_predicate | "
        "fragment | chunk_boundary_fragment | generic_without_commitment | table_of_contents",
    )

    # numeric facts found in this text (empty for a rejected sentence)
    numeric_facts: list[NumericFactFields] = Field(default_factory=list)

    # evidence-candidate bookkeeping
    has_number: bool = False
    candidate_type: str | None = None

    # gold labels, when a human has adjudicated this row
    label: dict[str, Any] | None = Field(
        default=None, description="see data/gold/LABELING_CONVENTIONS.md; null until adjudicated"
    )
    annotator: str | None = None
    adjudicated_at: datetime | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


LAYERS: dict[str, type[_Record]] = {
    "raw": RawDocument,
    "clean": CleanUnit,
    "extract": ExtractRecord,
}

# Fields that must be present and non-null for a row to be usable, per origin.
# A crawled file without an access date cannot be cited; an uploaded file in a
# run legitimately has none.
REQUIRED_BY_ORIGIN: dict[str, dict[str, tuple[str, ...]]] = {
    "raw": {
        "corpus": ("sha256", "access_date", "source_authority", "document_type", "object_path"),
        "run": ("sha256", "document_type"),
    },
    "clean": {
        "corpus": ("doc_id", "text_sha256", "split"),
        "run": ("doc_id", "text_sha256"),
    },
    "extract": {
        "corpus": ("unit_id", "doc_id", "text_sha256"),
        "run": ("unit_id", "doc_id", "text_sha256"),
    },
}


def missing_required(row: dict[str, Any], layer: str) -> list[str]:
    """Required fields that are absent, null, or an empty string for this row's origin."""
    origin = row.get("origin") or "corpus"
    required = REQUIRED_BY_ORIGIN[layer].get(origin, ())
    missing = []
    for field in required:
        value = row.get(field)
        if value is None or value == "" or value == "unassigned":
            missing.append(field)
    return missing
