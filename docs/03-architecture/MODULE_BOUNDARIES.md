# MODULE_BOUNDARIES.md

Version: 0.1  
Status: Draft implementation boundaries  
Owner: Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines module boundaries for the Greenwashing Detection codebase. It prevents AI coding agents and developers from mixing domain logic, retrieval logic, UI formatting, and persistence logic in the same place.

Each module should have one clear responsibility and should map to the evidence-first pipeline.

## 2. Boundary principles

1. Domain modules define objects and rules; they do not call databases, LLMs, or UI code.
2. Pipeline modules orchestrate steps; they do not define scoring rules from scratch.
3. Infrastructure adapters implement storage, parsing, retrieval, and external services behind interfaces.
4. Output builders format existing verified data; they do not create new verdicts.
5. Human review can revise results, but revisions must be versioned and audit logged.
6. No module may invent enums outside the documented contracts.

## 3. Recommended package structure

```text
src/
  domain/
    case/
    document/
    claim/
    evidence/
    verification/
    scoring/
    review/
    audit-log/

  application/
    pipelines/
    services/
    use-cases/

  infrastructure/
    storage/
    parsers/
    search/
    vector/
    llm/
    external-sources/

  interfaces/
    api/
    cli/
    ui-contracts/

  config/
    taxonomy/
    scoring/
    retrieval/
    legal-rules/

  tests/
```

This structure can be adapted to the chosen framework, but the boundaries should remain stable.

## 4. Domain modules

### 4.1 `domain/case`

Responsibility:

- define assessment cases;
- track company, year, scope, status;
- link documents, claims, outputs, and review records.

Should contain:

- `Case`
- `CaseStatus`
- `CompanyProfile`
- `MaterialityMap`

Should not:

- parse documents;
- call search;
- calculate scores.

### 4.2 `domain/document`

Responsibility:

- define source documents, chunks, tables, metrics, provenance, and quality flags.

Should contain:

- `Document`
- `DocumentChunk`
- `SourceSpan`
- `ExtractedTable`
- `ExtractedMetric`
- `DataQualityFlag`
- `ProcessingReport`

Should not:

- decide greenwashing verdicts;
- store retrieval logic;
- call LLMs directly.

### 4.3 `domain/claim`

Responsibility:

- define green claims and claim taxonomy assignments.

Should contain:

- `GreenClaim`
- `ClaimCategory`
- `GreenwashingPatternCandidate`
- `ClaimGroup`
- `EvidenceRequirement`
- `MaterialityLevel`

Should not:

- retrieve evidence;
- score risk;
- assign final verdict alone.

### 4.4 `domain/evidence`

Responsibility:

- define evidence records, role, strength, retrieval trace, and exclusion reasons.

Should contain:

- `EvidenceItem`
- `EvidenceRole`
- `EvidenceStrength`
- `EvidencePackage`
- `EvidenceRetrievalTrace`
- `EvidenceExclusionReason`
- `MissingEvidenceItem`

Should not:

- create claims;
- calculate total risk score.

### 4.5 `domain/verification`

Responsibility:

- define five-layer verification outputs and verdict enum.

Should contain:

- `VerificationResult`
- `LayerCheckResult`
- `VerificationVerdict`
- `VerificationRationale`

Should not:

- execute search;
- format dashboard outputs.

### 4.6 `domain/scoring`

Responsibility:

- implement claim-level and company-level risk scoring according to `MANUAL_SCORING_RUBRIC.md`.

Should contain:

- `RiskScore`
- `CriterionScore`
- `RiskLabel`
- `CompanyRiskAggregation`
- `ScoreVersion`

Should not:

- extract evidence;
- mutate claim text;
- silently change thresholds.

### 4.7 `domain/review`

Responsibility:

- represent human review state and reviewer decisions.

Should contain:

- `HumanReviewRecord`
- `ReviewStatus`
- `ReviewDecision`
- `ReviewerComment`
- `ReviewTrigger`

Should not:

- overwrite system-generated output without versioning.

### 4.8 `domain/audit-log`

Responsibility:

- define audit log event types and versioning metadata.

Should contain:

- `AuditLogEntry`
- `AuditEventType`
- `ActorType`
- `ObjectVersion`

Should not:

- perform business logic.

## 5. Application services

### 5.1 `CaseOrchestrator`

Coordinates the end-to-end case run.

Allowed dependencies:

- document processing pipeline;
- claim pipeline;
- evidence pipeline;
- verification pipeline;
- scoring service;
- output builders;
- repositories.

Must not:

- contain detailed scoring formulas;
- contain UI-specific formatting;
- call external APIs directly without adapters.

### 5.2 `DocumentProcessingPipeline`

Coordinates parsing, chunking, metric extraction, and data quality checks.

Allowed dependencies:

- parser adapters;
- table extractor;
- metric normalizer;
- document repository.

### 5.3 `ClaimPipeline`

Coordinates extraction, classification, normalization, deduplication, materiality mapping, and evidence requirements.

Allowed dependencies:

- claim extractor interface;
- classifier;
- taxonomy config;
- claim repository.

### 5.4 `EvidencePipeline`

Coordinates query planning, retrieval, reranking, grading, and evidence package creation.

Allowed dependencies:

- search adapters;
- metric store;
- rule store;
- evidence grader.

### 5.5 `VerificationPipeline`

Coordinates five-layer verification and verdict assignment.

Allowed dependencies:

- verification checkers;
- evidence package;
- claim object;
- rule store.

### 5.6 `ScoringService`

Computes scores according to the rubric.

Allowed dependencies:

- scoring config;
- verification result;
- evidence package;
- claim materiality.

### 5.7 `OutputService`

Builds dashboard, claim table, evidence card, working paper, report, and JSON export.

Allowed dependencies:

- output builders;
- repositories.

Must not:

- change verdict or score values.

### 5.8 `ReviewService`

Handles review queue, decisions, comments, and sign-off.

Allowed dependencies:

- review repository;
- audit log service;
- output repository.

## 6. Infrastructure adapters

Infrastructure adapters implement external or replaceable details.

| Adapter | Responsibility |
|---|---|
| `FileStorageAdapter` | store and fetch raw files |
| `PdfParserAdapter` | extract text and page references |
| `OcrAdapter` | OCR scanned pages, future or mock |
| `TableExtractionAdapter` | extract table cells and confidence |
| `BM25SearchAdapter` | keyword/full-text retrieval |
| `VectorSearchAdapter` | vector similarity retrieval |
| `HybridSearchAdapter` | combine keyword and vector results |
| `RerankerAdapter` | rerank candidate evidence |
| `LLMAdapter` | schema-constrained extraction or explanation |
| `ExternalSourceAdapter` | news/regulatory/external evidence retrieval |
| `ReportExportAdapter` | markdown/pdf/json export |

All adapters must return typed results and error objects, not unstructured strings.

## 7. Configuration modules

Configuration should be versioned and reviewable.

```text
config/
  taxonomy/greenwashing_taxonomy.v0.1.yaml
  scoring/manual_rubric.v0.1.yaml
  retrieval/retrieval_policy.v0.1.yaml
  legal-rules/vietnam_green_taxonomy.v0.1.yaml
  review/review_triggers.v0.1.yaml
```

MVP may use JSON instead of YAML, but config should remain separate from code logic.

## 8. Cross-module data contracts

### 8.1 Document to claim

`ClaimExtractor` receives:

```ts
DocumentChunk[]
```

and returns:

```ts
GreenClaim[]
```

It must not return raw prose only.

### 8.2 Claim to evidence

`EvidencePipeline` receives:

```ts
GreenClaim + EvidenceRequirement[]
```

and returns:

```ts
EvidencePackage
```

### 8.3 Evidence to verification

`VerificationPipeline` receives:

```ts
GreenClaim + EvidencePackage
```

and returns:

```ts
VerificationResult
```

### 8.4 Verification to scoring

`ScoringService` receives:

```ts
GreenClaim + EvidencePackage + VerificationResult
```

and returns:

```ts
RiskScore
```

### 8.5 Score to output

`OutputService` receives:

```ts
GreenClaim + EvidencePackage + VerificationResult + RiskScore + ReviewStatus
```

and returns:

```ts
EvidenceCard + ClaimTableRow + DashboardSummary
```

## 9. Dependency rules

Allowed direction:

```text
interfaces → application → domain
application → infrastructure through interfaces
infrastructure → domain types allowed
infrastructure must not call application services
```

Forbidden examples:

- UI component calculating risk score directly.
- Retrieval adapter assigning final verdict.
- LLM adapter writing database records directly.
- Report builder changing score thresholds.
- Review service deleting previous AI result versions.

## 10. Testing responsibility by module

| Module | Required tests |
|---|---|
| document processing | provenance, page reference, quality flags |
| claim extraction | exact text, source ID, category validity |
| claim deduplication | grouping without deleting originals |
| retrieval | returns candidate evidence with method and score |
| evidence grading | strength level and exclusion reason |
| verification | verdict rules for supported/contradicted/insufficient cases |
| scoring | criterion totals, label thresholds, score version |
| output | schema validity, source citation presence |
| review | trigger logic, decision versioning |

## 11. Claude Code implementation rule

When implementing any module, Claude Code must add a comment or test reference showing which document section the module implements.

Example:

```ts
// Implements docs/03-architecture/PIPELINE_SPEC.md Stage 10 — Risk scoring
```

This is required until the codebase stabilizes.
