# DATA_SCHEMA.md

Version: 0.1  
Status: Draft implementation contract  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines the canonical data schema for the Greenwashing Detection MVP. It is the shared contract for:

- document processing,
- claim extraction,
- evidence retrieval,
- verification,
- risk scoring,
- product outputs,
- human review,
- exports,
- tests.

No backend, UI, AI prompt, or agent may invent alternative enum labels or silently drop required provenance fields.

## 2. Source alignment

This schema is aligned with:

- `docs/02-product/OUTPUT_SPEC.md` for product outputs,
- `docs/03-architecture/PIPELINE_SPEC.md` for pipeline stages,
- `docs/01-domain-audit/*` for audit logic,
- evidence-first principle: `Claim → Evidence → Verification → Verdict → Score → Explanation → Review`.

## 3. Global conventions

### 3.1 Stable ID prefixes

| Object | Prefix |
|---|---|
| Case | `CASE` |
| Document | `DOC` |
| Chunk | `CHUNK` |
| Table | `TABLE` |
| Metric | `METRIC` |
| Claim | `CLAIM` |
| Claim group | `CG` |
| Retrieval plan | `RP` |
| Evidence | `EVID` |
| Evidence package | `EPKG` |
| Verification result | `VER` |
| Score | `SCORE` |
| Evidence card | `ECARD` |
| Working paper | `WP` |
| Review | `REV` |
| Pipeline run | `RUN` |
| Audit log | `AUDIT` |
| Export | `EXP` |

Recommended format: `PREFIX-000001`.

### 3.2 Required provenance fields

Every object generated from source documents must include at least:

```ts
type Provenance = {
  source_document_id?: string;
  source_chunk_id?: string;
  source_table_id?: string;
  source_page?: number | string;
  source_section?: string;
  source_uri?: string;
  content_hash?: string;
  extraction_method?: ExtractionMethod;
  extracted_at?: ISODateTime;
  model_name?: string;
  prompt_version?: string;
  schema_version?: string;
};
```

### 3.3 Core enums

```ts
type ISODateTime = string;

type SourceType =
  | "ESG_REPORT"
  | "ANNUAL_REPORT"
  | "SUSTAINABILITY_REPORT"
  | "FINANCIAL_STATEMENT"
  | "GREEN_BOND_FRAMEWORK"
  | "GREEN_LOAN_DOCUMENT"
  | "LEGAL_REGULATION"
  | "TAXONOMY_STANDARD"
  | "ENVIRONMENTAL_PERMIT"
  | "VIOLATION_RECORD"
  | "AUDIT_ASSURANCE_REPORT"
  | "EXTERNAL_NEWS"
  | "COMPANY_WEBSITE"
  | "OTHER";

type ExtractionMethod =
  | "MANUAL"
  | "RULE_BASED"
  | "LLM_STRUCTURED_OUTPUT"
  | "OCR"
  | "TABLE_EXTRACTOR"
  | "STRUCTURED_IMPORT"
  | "MOCK_FIXTURE";

type VerificationVerdict =
  | "SUPPORTED"
  | "PARTIALLY_SUPPORTED"
  | "UNSUPPORTED"
  | "CONTRADICTED"
  | "INSUFFICIENT_EVIDENCE";

type RiskLabel =
  | "LOW"
  | "MODERATE"
  | "HIGH"
  | "VERY_HIGH"
  | "CRITICAL";

type EvidenceRole =
  | "SUPPORTING"
  | "CONTRADICTING"
  | "CONTEXTUAL"
  | "EXCLUDED"
  | "MISSING_REQUIRED";

type EvidenceStrength =
  | "L1_HIGH_AUTHORITY"
  | "L2_OFFICIAL_DISCLOSURE"
  | "L3_COMPANY_UNASSURED_DATA"
  | "L4_EXTERNAL_OR_MEDIA"
  | "L5_MARKETING_OR_LOW_RELIABILITY";

type ReviewStatus =
  | "NOT_REQUIRED"
  | "PENDING_REVIEW"
  | "ACCEPTED"
  | "REVISED"
  | "REJECTED"
  | "ESCALATED";

type MaterialityLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL"
  | "UNKNOWN";
```

## 4. Case and document schemas

### 4.1 AssessmentCase

```ts
type AssessmentCase = {
  case_id: string;
  company_name: string;
  industry: string | "UNKNOWN";
  reporting_year: number;
  review_scope: string;
  jurisdiction?: string;
  created_by: string;
  created_at: ISODateTime;
  status: "CREATED" | "PROCESSING" | "READY_FOR_REVIEW" | "REVIEWED" | "EXPORTED" | "ARCHIVED";
  methodology_version: string;
  score_version: string;
  notes?: string;
};
```

### 4.2 Document

```ts
type Document = {
  document_id: string;
  case_id: string;
  source_type: SourceType;
  file_name: string;
  file_uri: string;
  company_name?: string;
  reporting_year?: number;
  language?: "vi" | "en" | "mixed" | "unknown";
  ingestion_status: "INGESTED" | "REJECTED" | "PROCESSING" | "PROCESSED" | "FAILED";
  quality_flags: DataQualityFlag[];
  provenance: Provenance;
};
```

### 4.3 DocumentChunk

```ts
type DocumentChunk = {
  chunk_id: string;
  document_id: string;
  case_id: string;
  text: string;
  page_start?: number;
  page_end?: number;
  section_title?: string;
  token_count?: number;
  chunk_index: number;
  embedding_id?: string;
  text_index_id?: string;
  quality_flags: DataQualityFlag[];
  provenance: Provenance;
};
```

### 4.4 ExtractedTable

```ts
type ExtractedTable = {
  table_id: string;
  document_id: string;
  case_id: string;
  title?: string;
  page?: number;
  raw_cells: string[][];
  normalized_rows?: NormalizedMetric[];
  extraction_confidence?: number;
  quality_flags: DataQualityFlag[];
  provenance: Provenance;
};
```

### 4.5 NormalizedMetric

```ts
type NormalizedMetric = {
  metric_id: string;
  case_id: string;
  document_id: string;
  table_id?: string;
  metric_name: string;
  metric_category:
    | "GHG_EMISSIONS"
    | "ENERGY"
    | "WATER"
    | "WASTE"
    | "CAPEX"
    | "OPEX"
    | "REVENUE"
    | "USE_OF_PROCEEDS"
    | "OTHER";
  value: number | string;
  unit?: string;
  period_start?: string;
  period_end?: string;
  reporting_year?: number;
  boundary?: string;
  scope?: "SCOPE_1" | "SCOPE_2" | "SCOPE_3" | "SCOPE_1_2" | "UNKNOWN";
  normalized_value?: number;
  normalized_unit?: string;
  quality_flags: DataQualityFlag[];
  provenance: Provenance;
};
```

## 5. Claim schemas

### 5.1 ClaimCategory

```ts
type ClaimCategory =
  | "EMISSIONS_REDUCTION"
  | "CLIMATE_TARGET"
  | "NET_ZERO"
  | "RENEWABLE_ENERGY"
  | "ENERGY_EFFICIENCY"
  | "WATER_MANAGEMENT"
  | "WASTE_AND_RECYCLING"
  | "BIODIVERSITY"
  | "GREEN_PRODUCT_OR_SERVICE"
  | "GREEN_BOND"
  | "GREEN_LOAN"
  | "SUSTAINABLE_FINANCE"
  | "TAXONOMY_ALIGNMENT"
  | "LEGAL_COMPLIANCE"
  | "ASSURANCE_OR_CERTIFICATION"
  | "CSR_ENVIRONMENTAL"
  | "VAGUE_SUSTAINABILITY"
  | "OTHER";
```

### 5.2 GreenwashingPatternCandidate

```ts
type GreenwashingPatternCandidate =
  | "VAGUE_CLAIM"
  | "NO_EVIDENCE"
  | "SELECTIVE_DISCLOSURE"
  | "QUANTITATIVE_CONTRADICTION"
  | "LEGAL_CONTRADICTION"
  | "FINANCIAL_GREENWASHING"
  | "EMPTY_FUTURE_COMMITMENT"
  | "SCOPE_SHIFTING"
  | "BASELINE_MANIPULATION"
  | "OFFSET_OVERRELIANCE"
  | "LABEL_CONFUSION"
  | "NONE_IDENTIFIED";
```

### 5.3 GreenClaim

```ts
type GreenClaim = {
  claim_id: string;
  case_id: string;
  claim_group_id?: string;
  claim_text: string;
  claim_text_short?: string;
  normalized_claim?: string;
  claim_category: ClaimCategory;
  secondary_categories?: ClaimCategory[];
  pattern_candidates: GreenwashingPatternCandidate[];
  is_quantifiable: boolean;
  mentioned_metric?: string;
  mentioned_value?: string | number;
  mentioned_unit?: string;
  mentioned_baseline?: string;
  mentioned_period?: string;
  mentioned_scope_or_boundary?: string;
  materiality: MaterialityLevel;
  required_evidence_types: EvidenceRequirementType[];
  extraction_confidence: number;
  classification_confidence?: number;
  review_status: ReviewStatus;
  provenance: Provenance;
};
```

### 5.4 ClaimGroup

```ts
type ClaimGroup = {
  claim_group_id: string;
  case_id: string;
  group_label: string;
  canonical_claim_id: string;
  claim_ids: string[];
  merge_reason: string;
  materiality: MaterialityLevel;
};
```

## 6. Evidence schemas

### 6.1 EvidenceRequirementType

```ts
type EvidenceRequirementType =
  | "CURRENT_PERIOD_METRIC"
  | "BASELINE_METRIC"
  | "SCOPE_BOUNDARY"
  | "METHODOLOGY"
  | "ASSURANCE_STATEMENT"
  | "LEGAL_OR_PERMIT_RECORD"
  | "TAXONOMY_CRITERIA"
  | "USE_OF_PROCEEDS_TRACKING"
  | "PROJECT_ELIGIBILITY"
  | "EXTERNAL_CONTRADICTION_SEARCH"
  | "CAPEX_OR_FINANCIAL_ALLOCATION"
  | "TRANSITION_PLAN"
  | "INTERIM_TARGET"
  | "OTHER";
```

### 6.2 RetrievalPlan

```ts
type RetrievalPlan = {
  retrieval_plan_id: string;
  claim_id: string;
  case_id: string;
  support_queries: RetrievalQuery[];
  contradiction_queries: RetrievalQuery[];
  structured_lookups: StructuredLookup[];
  legal_taxonomy_lookups: LegalTaxonomyLookup[];
  missing_evidence_placeholders: EvidenceRequirementType[];
  query_plan_version: string;
};
```

### 6.3 RetrievalQuery

```ts
type RetrievalQuery = {
  query_id: string;
  query_text: string;
  query_role: "SUPPORTING_SEARCH" | "CONTRADICTION_SEARCH" | "CONTEXT_SEARCH";
  target_sources: SourceType[];
  expected_evidence_type?: EvidenceRequirementType;
};
```

### 6.4 EvidenceItem

```ts
type EvidenceItem = {
  evidence_id: string;
  case_id: string;
  claim_id?: string;
  evidence_text?: string;
  metric_id?: string;
  evidence_role: EvidenceRole;
  evidence_strength: EvidenceStrength;
  relevance_score?: number;
  retrieval_score?: number;
  retrieval_method?: RetrievalMethod;
  supports_requirement?: EvidenceRequirementType;
  excluded_reason?: string;
  contradiction_type?: "NUMERIC" | "LEGAL" | "TEMPORAL" | "SCOPE" | "EXTERNAL" | "OTHER";
  quality_flags: DataQualityFlag[];
  provenance: Provenance;
};

type RetrievalMethod =
  | "BM25"
  | "VECTOR"
  | "HYBRID_RRF"
  | "STRUCTURED_METRIC_LOOKUP"
  | "LEGAL_RULE_LOOKUP"
  | "MANUAL_ADDED"
  | "MOCK_FIXTURE";
```

### 6.5 EvidencePackage

```ts
type EvidencePackage = {
  evidence_package_id: string;
  claim_id: string;
  case_id: string;
  selected_evidence_ids: string[];
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  contextual_evidence_ids: string[];
  excluded_evidence_ids: string[];
  missing_required_evidence: EvidenceRequirementType[];
  package_quality_flags: DataQualityFlag[];
  created_at: ISODateTime;
};
```

## 7. Verification and scoring schemas

### 7.1 VerificationLayerStatus

```ts
type VerificationLayerStatus =
  | "PASS"
  | "PARTIAL"
  | "FAIL"
  | "NOT_APPLICABLE"
  | "UNKNOWN";
```

### 7.2 VerificationResult

```ts
type VerificationResult = {
  verification_id: string;
  case_id: string;
  claim_id: string;
  evidence_package_id: string;
  layer_results: {
    specificity: VerificationLayerStatus;
    evidence_availability: VerificationLayerStatus;
    quantitative_consistency: VerificationLayerStatus;
    legal_taxonomy_alignment: VerificationLayerStatus;
    external_contradiction: VerificationLayerStatus;
  };
  recommended_verdict: VerificationVerdict;
  rationale: string;
  cited_evidence_ids: string[];
  missing_evidence: EvidenceRequirementType[];
  verification_confidence: number;
  verification_version: string;
  created_at: ISODateTime;
};
```

### 7.3 RiskScore

```ts
type RiskScore = {
  score_id: string;
  case_id: string;
  claim_id: string;
  verification_id: string;
  score_version: string;
  criteria_scores: {
    C1_specificity_weakness: number;
    C2_missing_quantitative_data: number;
    C3_missing_baseline_time_scope: number;
    C4_weak_or_missing_evidence: number;
    C5_lack_of_independent_assurance: number;
    C6_contradictory_evidence: number;
    C7_overstatement_or_misleading_language: number;
  };
  modifiers?: {
    materiality_modifier?: number;
    green_finance_modifier?: number;
    net_zero_modifier?: number;
  };
  total_score: number;
  risk_label: RiskLabel;
  score_rationale: string;
  created_at: ISODateTime;
};
```

### 7.4 CompanyAssessment

```ts
type CompanyAssessment = {
  case_id: string;
  company_name: string;
  reporting_year: number;
  company_risk_score: number;
  company_risk_label: RiskLabel;
  verdict_distribution: Record<VerificationVerdict, number>;
  top_risk_categories: ClaimCategory[];
  top_high_risk_claim_ids: string[];
  pending_review_count: number;
  methodology_version: string;
  score_version: string;
  generated_at: ISODateTime;
};
```

## 8. Review and audit schemas

### 8.1 HumanReviewRecord

```ts
type HumanReviewRecord = {
  review_id: string;
  case_id: string;
  claim_id: string;
  evidence_card_id?: string;
  review_status: ReviewStatus;
  trigger_reasons: ReviewTriggerReason[];
  reviewer_id?: string;
  reviewer_decision?: VerificationVerdict;
  reviewer_score_override?: number;
  reviewer_comment?: string;
  created_at: ISODateTime;
  resolved_at?: ISODateTime;
};

type ReviewTriggerReason =
  | "RISK_SCORE_ABOVE_THRESHOLD"
  | "CONTRADICTED_VERDICT"
  | "HIGH_MATERIALITY_INSUFFICIENT_EVIDENCE"
  | "LOW_EXTRACTION_CONFIDENCE"
  | "LOW_EVIDENCE_STRENGTH"
  | "LOW_OCR_OR_TABLE_CONFIDENCE"
  | "GREEN_FINANCE_USE_OF_PROCEEDS_ISSUE"
  | "MANUAL_ESCALATION";
```

### 8.2 AuditLogEntry

```ts
type AuditLogEntry = {
  audit_log_id: string;
  case_id: string;
  actor_type: "SYSTEM" | "USER" | "AI_AGENT";
  actor_id?: string;
  action: string;
  target_object_type: string;
  target_object_id: string;
  previous_version_id?: string;
  new_version_id?: string;
  timestamp: ISODateTime;
  metadata?: Record<string, unknown>;
};
```

## 9. Data quality flags

```ts
type DataQualityFlag =
  | "MISSING_SOURCE_PAGE"
  | "MISSING_REPORTING_YEAR"
  | "MISSING_UNIT"
  | "AMBIGUOUS_METRIC_NAME"
  | "LOW_OCR_CONFIDENCE"
  | "LOW_TABLE_EXTRACTION_CONFIDENCE"
  | "INCONSISTENT_COMPANY_METADATA"
  | "INCONSISTENT_YEAR_METADATA"
  | "POSSIBLE_DUPLICATE_CLAIM"
  | "WEAK_EVIDENCE_MATCH"
  | "WRONG_PERIOD_MATCH"
  | "WRONG_SCOPE_MATCH"
  | "UNVERIFIED_EXTERNAL_SOURCE"
  | "MISSING_REQUIRED_EVIDENCE";
```

## 10. Schema validation rules

1. A `GreenClaim` without source provenance is invalid.
2. An `EvidenceItem` without source provenance is invalid unless its role is `MISSING_REQUIRED`.
3. A `VerificationResult` must cite at least one evidence ID unless the verdict is `INSUFFICIENT_EVIDENCE`.
4. A `CONTRADICTED` verdict must cite at least one `CONTRADICTING` evidence item.
5. A `RiskScore` must reference a `VerificationResult`.
6. Every score must store `score_version`.
7. Human reviewer revisions must create a new version; they must not overwrite the original AI result.
8. Exported JSON must preserve stable IDs and source links.

## 11. MVP simplification

For the first demo, the implementation may use:

- local JSON files instead of a relational database,
- mock embeddings or disabled vector search,
- fixture documents and deterministic outputs,
- manual or rule-based extraction before real LLM extraction,
- one company case at a time.

Even in simplified mode, provenance, enums, verdicts, risk score, and review records must follow this schema.
