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
    source_name: str
    source_page: int | None = None
    metric: str | None = None
    direction: str | None = None
    values: list[float] = Field(default_factory=list)
    units: list[str] = Field(default_factory=list)
    period: str | None = None
    baseline: str | None = None
    is_future_commitment: bool = False
    is_vague: bool = False
    confidence: float = 0.5


class RetrievedEvidence(BaseModel):
    chunk_id: str
    source_name: str
    source_type: SourceType
    text: str
    page: int | None = None
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    citation: str
    suspicious_instruction: bool = False


class VerificationResult(BaseModel):
    claim: Claim
    status: VerificationStatus
    rationale: str
    evidence: list[RetrievedEvidence] = Field(default_factory=list)
    computed_values: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    verification_tool_version: str = "verifier-v1"


class RiskComponent(BaseModel):
    name: str
    score: float
    max_score: float
    reason: str


class RiskAssessment(BaseModel):
    claim_id: str
    risk_score: float
    severity: Severity
    components: list[RiskComponent]
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


class AnalysisResult(BaseModel):
    schema_version: str = "analysis-result-v1"
    run_id: str
    manifest: RunManifest
    claims: list[Claim]
    verifications: list[VerificationResult]
    risks: list[RiskAssessment]
    quality_gates: list[QualityGate]
    summary: AnalysisSummary
    output_directory: str
