# EVIDENCE_FIRST_ARCHITECTURE.md

Version: 0.1  
Status: Draft architecture baseline  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines the evidence-first architecture for the Greenwashing Detection MVP. It converts the product workflow and manual audit protocol into a system architecture that can be implemented, tested, and reviewed by both human developers and AI coding agents.

The architecture must preserve this invariant:

```text
No verdict without traceable evidence.
```

The system should not behave like a generic ESG chatbot. It should behave like an audit-support system that decomposes sustainability-related statements into claims, binds those claims to evidence, checks for support and contradiction, scores risk, and preserves a working paper for human review.

## 2. Architecture thesis

The architecture is evidence-first because every system output must be traceable back to source material.

```text
Document source
→ Processed text/table/metric
→ Green claim
→ Evidence requirement
→ Supporting and contradicting evidence
→ Five-layer verification
→ Verdict
→ Risk score
→ Explanation
→ Reviewer action
→ Audit log / working paper
```

If a pipeline stage cannot preserve provenance, that stage cannot be trusted for audit use.

## 3. Source-aligned design basis

The architecture is aligned with these design references:

| Reference | Architectural implication |
|---|---|
| `AUDIT_PROTOCOL.md` | Every AI conclusion must imitate the manual audit flow: claim, evidence, cross-check, verdict, score, sign-off. |
| `MANUAL_SCORING_RUBRIC.md` | Scoring must be criterion-level, explainable, and versioned. |
| `EVIDENCE_STANDARD.md` | Evidence must be graded by reliability and role before verification. |
| `OUTPUT_SPEC.md` | All outputs must use stable IDs, fixed enums, evidence cards, JSON export, and audit logs. |
| RAG system research | Retrieval quality, distracting evidence, document selection, and prompt construction can affect correctness; therefore retrieval must be evaluated, logged, and not treated as automatically reliable. |
| Hybrid search / RRF practice | Keyword and vector retrieval should be fused where useful, with retrievable subscores when possible. |
| GraphRAG / hierarchical retrieval | Global and multi-document synthesis questions need a different retrieval mode than simple fact lookup. |
| NIST AI RMF | AI system design should include risk management, evaluation, documentation, and traceability. |

## 4. High-level system context

```text
[User / Reviewer]
       |
       v
[Web UI / Review UI]
       |
       v
[Application API]
       |
       +--> [Case Service]
       +--> [Document Processing Pipeline]
       +--> [Claim Pipeline]
       +--> [Evidence Retrieval Pipeline]
       +--> [Verification & Scoring Pipeline]
       +--> [Output / Export Pipeline]
       +--> [Human Review Pipeline]
       |
       v
[Storage Layer]
       +--> Raw files
       +--> Document chunks
       +--> Structured metrics
       +--> Search indexes
       +--> Claims
       +--> Evidence items
       +--> Verification results
       +--> Scores
       +--> Review records
       +--> Audit logs
```

## 5. Logical architecture zones

### 5.1 Intake zone

Responsible for receiving documents, validating metadata, and preserving original files.

Components:

- `CaseService`
- `DocumentIntakeService`
- `FileStorageAdapter`
- `MetadataValidator`

Outputs:

- `Case`
- `Document`
- raw file reference
- intake audit event

### 5.2 Processing zone

Responsible for converting documents into usable text, table, metric, and chunk objects.

Components:

- `DocumentParser`
- `OCRAdapter` future or mocked in MVP
- `TableExtractor`
- `MetricExtractor`
- `Chunker`
- `UnitNormalizer`
- `ProvenanceTracker`
- `DataQualityGate`

Outputs:

- `DocumentChunk`
- `ExtractedMetric`
- `DocumentProcessingReport`
- data quality flags

### 5.3 Knowledge zone

Responsible for searchable and structured knowledge.

Components:

- `KnowledgeIndexBuilder`
- `BM25IndexAdapter`
- `VectorIndexAdapter`
- `MetricStore`
- `TaxonomyRuleStore`
- `LegalRuleStore`
- `CompanyHistoryStore`

Outputs:

- search indexes
- structured tables
- taxonomy/legal rules

### 5.4 Claim zone

Responsible for extracting and organizing green claims.

Components:

- `ClaimExtractor`
- `ClaimClassifier`
- `ClaimNormalizer`
- `ClaimDeduplicator`
- `MaterialityMapper`
- `EvidenceRequirementGenerator`

Outputs:

- `GreenClaim`
- `ClaimGroup`
- claim category
- greenwashing pattern candidates
- evidence requirements

### 5.5 Evidence zone

Responsible for retrieving, grading, and selecting evidence.

Components:

- `EvidenceQueryPlanner`
- `SupportingEvidenceRetriever`
- `NegativeEvidenceRetriever`
- `HybridSearchRetriever`
- `StructuredMetricRetriever`
- `GraphOrHierarchicalRetriever` future or optional
- `EvidenceReranker`
- `EvidenceGrader`
- `EvidenceSelector`

Outputs:

- `EvidenceItem`
- evidence role
- evidence strength
- retrieval trace
- exclusion reasons

### 5.6 Verification zone

Responsible for audit-style reasoning.

Components:

- `SpecificityChecker`
- `EvidenceAvailabilityChecker`
- `QuantitativeConsistencyChecker`
- `LegalTaxonomyChecker`
- `ExternalContradictionChecker`
- `VerdictAssigner`
- `RiskScorer`
- `CompanyRiskAggregator`

Outputs:

- `VerificationResult`
- `RiskScore`
- criterion-level rationale
- missing evidence requests

### 5.7 Output zone

Responsible for making the result usable to reviewers.

Components:

- `DashboardBuilder`
- `ClaimTableBuilder`
- `EvidenceCardBuilder`
- `WorkingPaperBuilder`
- `CompanyReportBuilder`
- `JsonExportBuilder`

Outputs:

- dashboard JSON
- claim table rows
- evidence cards
- working paper
- company report
- JSON export

### 5.8 Human review zone

Responsible for accountability and feedback.

Components:

- `ReviewQueueService`
- `ReviewDecisionService`
- `ReviewerCommentService`
- `RuleFeedbackService`
- `AuditLogService`

Outputs:

- `HumanReviewRecord`
- reviewer decision
- updated audit log
- open questions / rule feedback

## 6. End-to-end component flow

```text
CaseService
  → DocumentIntakeService
  → DocumentParser / TableExtractor / MetricExtractor
  → DataQualityGate
  → KnowledgeIndexBuilder
  → ClaimExtractor
  → ClaimClassifier
  → ClaimNormalizer / Deduplicator
  → MaterialityMapper
  → EvidenceRequirementGenerator
  → EvidenceQueryPlanner
  → HybridSearchRetriever + StructuredMetricRetriever + NegativeEvidenceRetriever
  → EvidenceReranker
  → EvidenceGrader
  → FiveLayerVerifier
  → RiskScorer
  → EvidenceCardBuilder
  → ReviewQueueService
  → WorkingPaperBuilder / ReportBuilder
```

## 7. Critical architecture invariants

### 7.1 Provenance invariant

Every generated object must preserve source provenance when applicable.

Minimum fields:

- `source_document_id`
- `source_page` or `source_section`
- `source_span` when available
- `extraction_method`
- `confidence`

### 7.2 Fixed enum invariant

All code must use the fixed enums from `OUTPUT_SPEC.md` and `DATA_SCHEMA.md` when implemented.

Examples:

```ts
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
```

No service may invent alternative verdict labels.

### 7.3 Evidence-before-verdict invariant

`VerdictAssigner` must fail closed if no evidence package is available.

Expected behavior:

- no evidence package → `INSUFFICIENT_EVIDENCE` or `UNSUPPORTED`, depending on claim type and evidence requirements;
- evidence package with direct contradiction → likely `CONTRADICTED` unless contradiction is weak/excluded;
- evidence package with weak support → `PARTIALLY_SUPPORTED` or `UNSUPPORTED`.

### 7.4 Negative evidence invariant

For material claims, the system must search for contradicting evidence, not only supporting evidence.

Examples:

- environmental compliance claim → search enforcement, fines, permit mismatch;
- emissions reduction claim → search current-year emissions, prior-year emissions, production adjustment;
- green bond claim → search allocation report, eligible project list, proceeds tracking;
- net-zero claim → search target year, interim targets, baseline, scope coverage, offset dependency.

### 7.5 Reviewer accountability invariant

High-risk or low-confidence outputs must be routed to human review.

Default triggers:

- `risk_score >= 70`
- `verdict = CONTRADICTED`
- `verdict = INSUFFICIENT_EVIDENCE` for material claim
- evidence strength only L4/L5 for material claim
- extraction confidence below threshold
- reviewer-configured category, such as green finance or legal compliance

## 8. MVP implementation strategy

The MVP may use simplified or mocked components, but it must preserve architecture boundaries.

| Layer | MVP approach | Later approach |
|---|---|---|
| OCR | mocked or text-only PDF | real OCR with confidence and layout metadata |
| Table extraction | fixture/manual extraction allowed | automated table extraction + validation |
| Claim extraction | rule-based or LLM-mock | LLM + taxonomy-guided extractor + QA |
| Retrieval | local BM25/vector/simple search | hybrid retrieval + RRF + reranker + graph mode |
| External evidence | fixture-based | crawler/API connectors + dedup + timestamp |
| Legal taxonomy | rule fixtures | versioned legal/taxonomy rule engine |
| Scoring | deterministic rubric | deterministic rubric with calibrated modifiers |
| UI | mock API or local JSON | full backend API |
| Review | single reviewer | roles, permissions, sign-off workflow |

## 9. Non-goals

The architecture does not attempt to:

- legally determine fraud;
- replace an auditor or regulator;
- certify that a company is green;
- provide real-time environmental monitoring;
- automate final investment or credit decisions;
- scrape all possible external sources in MVP.

## 10. Architecture risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| False confidence from weak evidence | AI may sound certain despite poor sources | evidence strength, missing evidence flags, reviewer routing |
| Distracting evidence | Irrelevant but similar documents can mislead verification | reranking, evidence grading, exclusion reasons |
| Incorrect table extraction | ESG numbers often live in tables | data quality gate, table confidence, human review trigger |
| Claim duplication | Repeated marketing statements can distort scoring | claim normalization and grouping |
| Over-automation | Users may treat risk score as legal finding | disclaimers, reviewer sign-off, working paper |
| Unversioned methodology | Scores become non-reproducible | methodology version, score version, audit log |

## 11. Development rule for AI agents

Claude Code and other coding agents must not implement domain logic from memory. They must map code to these documents:

| Implementation area | Source of truth |
|---|---|
| Claim categories | `GREENWASHING_TAXONOMY.md` |
| Manual reasoning flow | `AUDIT_PROTOCOL.md` |
| Evidence reliability | `EVIDENCE_STANDARD.md` |
| Score formula | `MANUAL_SCORING_RUBRIC.md` |
| Output contracts | `OUTPUT_SPEC.md` |
| Architecture boundaries | this file + `MODULE_BOUNDARIES.md` |
| Pipeline IO | `PIPELINE_SPEC.md` |
| API shapes | `API_CONTRACTS.md` |

## 12. Open questions

1. Which vector database/search backend will be used in the first code implementation?
2. Should MVP store source files locally or in object storage?
3. Should legal/taxonomy rules be hardcoded JSON, database records, or YAML config?
4. How many demo companies are needed for evaluation?
5. Should claim extraction be LLM-first or rule-first for the first prototype?
