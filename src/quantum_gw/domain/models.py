from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .enums import DocumentRole, Severity, SourceType, VerificationStatus


class DocumentInput(BaseModel):
    path: str | None = None
    name: str | None = None
    text: str | None = None
    role: DocumentRole = DocumentRole.EVIDENCE
    source_type: SourceType = SourceType.INTERNAL
    language: str = "vi"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def display_name(self) -> str:
        if self.name:
            return self.name
        if self.path:
            return Path(self.path).name
        return "inline-document"


class EvidenceChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source_name: str
    role: DocumentRole
    source_type: SourceType
    text: str
    page: int | None = None
    block_index: int | None = None
    is_table: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def citation(self) -> str:
        location = []
        if self.page is not None:
            location.append(f"page {self.page}")
        if self.block_index is not None:
            location.append(f"block {self.block_index}")
        suffix = ", ".join(location) if location else "document"
        return f"{self.source_name} ({suffix})"


class Claim(BaseModel):
    claim_id: str
    text: str
    claim_type: str
    source_chunk_id: str
    source_doc_id: str = ""
    source_name: str
    source_page: int | None = None
    metric: str | None = None
    direction: str | None = None
    values: list[float] = Field(default_factory=list)
    units: list[str] = Field(default_factory=list)
    period: str | None = None
    baseline: str | None = None
    # Which entities/facilities/emission scopes the claim covers. The rubric
    # treats this as a mandatory attribute: "giảm 30%" is unverifiable until you
    # know whether it means one plant, the parent company or the whole group.
    scope: str | None = None
    is_future_commitment: bool = False
    is_vague: bool = False
    # Vague/promotional terms found in the claim, whether or not it also carries
    # a figure. The rubric scores promotional language from this list so there is
    # one lexicon (configs/taxonomy.yaml) rather than a second copy in the
    # scorer, which had drifted and covered Vietnamese only.
    vague_terms_matched: list[str] = Field(default_factory=list)
    # Which taxonomy lexicon matched this claim: "vi", "en" or "unknown". Carried
    # so a reviewer can see when a Vietnamese rubric was applied to an English
    # claim -- the failure that silently dropped every English claim before the
    # taxonomy became bilingual.
    language: str = "unknown"
    confidence: float = 0.5


class RetrievedEvidence(BaseModel):
    chunk_id: str
    # Needed to build the deep-link back to the stored original. Without it the
    # UI knows the page number but not which document to open.
    doc_id: str = ""
    source_name: str
    source_type: SourceType
    text: str
    page: int | None = None
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    citation: str
    suspicious_instruction: bool = False
    is_table: bool = False
    # Returned by the retrieval floor despite scoring below minimum_score. Such a
    # passage can carry a refutation from an authoritative source but can never
    # establish support — see HybridRetriever._admissible.
    below_threshold: bool = False
    # Scope limits carried from the source document's metadata (settlement
    # status, adjudication scope, legal caution). See legal/qualifiers.py: a
    # finding read without these says more than the source supports.
    source_qualifiers: list[str] = Field(default_factory=list)
    # How this passage stands towards the claim: SUPPORTS | CONTRADICTS |
    # PARTIAL | CONTEXT. Retrieval rank answers "how similar", which is not the
    # same question — a passage can rank first and still contradict the claim.
    relation: str = "CONTEXT"
    relation_reason: str = ""
    # How the stance was reached: numeric | qualitative_cue | direction | llm |
    # similarity. Carried so a reviewer can weigh a deterministic figure
    # comparison differently from a cue phrase or a model's opinion, and so the
    # evaluation harness can report stance accuracy per method.
    relation_method: str = "similarity"


class VerificationResult(BaseModel):
    claim: Claim
    status: VerificationStatus
    rationale: str
    evidence: list[RetrievedEvidence] = Field(default_factory=list)
    computed_values: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    # True when a language model decided at least one passage's stance. Such a
    # result always goes to a human: a model may point a reviewer at a passage,
    # it may not close a finding.
    requires_llm_review: bool = False
    verification_tool_version: str = "verifier-v2"


class RiskComponent(BaseModel):
    name: str
    score: float
    max_score: float
    reason: str


class RiskAssessment(BaseModel):
    """Screening priority for one claim — not a probability that a company lied.

    `risk_score` and `severity` answer "how soon should a reviewer look at
    this". They used to answer three questions at once, which is how a claim
    that merely omitted its base year reached HIGH on a control company
    (ISSUES N5). The three are now reported apart:

        evidence_strength       how well the corpus substantiates the claim
        contradiction_strength  whether something positively contradicts it
        materiality             how much it would matter if it were wrong

    Only `contradiction_strength` may lift a claim above MEDIUM. `materiality`
    stays UNKNOWN until there is a measured basis for it (RESEARCH_PROGRAM RQ8);
    inventing a number here would be the same mistake in a new place.
    """

    claim_id: str
    risk_score: float
    severity: Severity
    components: list[RiskComponent]
    evidence_strength: str = "unknown"        # strong | moderate | weak | none | unknown
    contradiction_strength: str = "none"      # numeric | authoritative_cue | trend_only | none
    materiality: str = "unknown"
    severity_cap_reason: str | None = None
    requires_human_review: bool = False
    rubric_version: str = "risk-rubric-v1"


class QualityGate(BaseModel):
    gate_id: str
    name: str
    passed: bool
    status: str
    details: str


class RunManifest(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pipeline_version: str
    config_hash: str
    input_hashes: dict[str, str]
    deterministic_seed: int = 0
    plan: list[str]


class AnalysisSummary(BaseModel):
    total_documents: int
    total_chunks: int
    total_claims: int
    status_counts: dict[str, int]
    severity_counts: dict[str, int]
    release_status: str


class SuggestionItem(BaseModel):
    code: str
    issue: str
    recommendation: str
    example_fix: str | None = None


class ClaimSuggestion(BaseModel):
    claim_id: str
    claim_text: str
    status: VerificationStatus
    severity: Severity
    risk_score: float
    items: list[SuggestionItem] = Field(default_factory=list)


class DisclosedFigure(BaseModel):
    """One published indicator row: the number itself, with what it is a number of.

    A claim is a sentence and is verified against prose; a disclosed figure is a
    table row and is verified by arithmetic and by comparison with the same row
    elsewhere. Keeping them apart is what lets the claim extractor go on
    rejecting table rows (they are not sentences) without the system losing the
    figures an auditor actually tests (agents/figures.py, ISSUES P2).
    """

    figure_id: str
    label: str
    value: float
    unit: str
    period: str | None = None
    scopes: list[int] = Field(default_factory=list)
    is_total: bool = False
    metric: str | None = None
    source_doc_id: str
    source_chunk_id: str
    source_name: str
    source_page: int | None = None
    raw_line: str = ""


class FigureCheck(BaseModel):
    """A procedure performed on disclosed figures, with the arithmetic it ran."""

    check_id: str
    kind: str                      # cross_foot | cross_document
    status: str                    # CONSISTENT | INCONSISTENT
    figure_ids: list[str] = Field(default_factory=list)
    calculation: str = ""
    difference: float = 0.0
    tolerance: float = 0.0
    note: str = ""


class AnalysisResult(BaseModel):
    schema_version: str = "analysis-result-v2"
    run_id: str
    manifest: RunManifest
    claims: list[Claim]
    verifications: list[VerificationResult]
    risks: list[RiskAssessment]
    # Where a reviewer should start. One record per claim (agents/prioritizer.py):
    # priority score, rank, whether it made this pass's queue, and the component
    # breakdown behind it. A verdict list says what each claim is; this says which
    # ones to open first, which is the question an auditor asks before the others.
    priorities: list[dict[str, Any]] = Field(default_factory=list)
    # Published indicator rows and the procedures run on them (agents/figures.py).
    # Separate from `claims` because they are verified by arithmetic and by
    # comparison with the same row in another document, not against prose.
    disclosed_figures: list[DisclosedFigure] = Field(default_factory=list)
    figure_checks: list[FigureCheck] = Field(default_factory=list)
    # What this pass deliberately did not examine, and why -- the scope paragraph a
    # working paper needs and a claim-by-claim dump cannot give.
    scope_note: str = ""
    # One record per claim from the legal layer: which instrument governs it,
    # which clause, which conditions held, which are unknown, and the scope
    # limits its sources carry. Kept as the legal layer's own dict rather than a
    # mirrored model so the two cannot drift -- see legal/checker.py
    # LegalCheckResult. Empty when the layer is disabled or its corpus could not
    # be loaded; the reason is reported on gate G7.
    legal_checks: list[dict[str, Any]] = Field(default_factory=list)
    # What kind of corpus the run had (agents/corpus.py): which document kinds
    # were present, which years, and whether absence of support may be read as
    # UNSUPPORTED. Shown as "evidence coverage" on the overview.
    corpus: dict[str, Any] = Field(default_factory=dict)
    quality_gates: list[QualityGate]
    summary: AnalysisSummary
    output_directory: str
