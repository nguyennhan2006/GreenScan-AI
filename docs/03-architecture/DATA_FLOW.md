# DATA_FLOW.md

Version: 0.1  
Status: Draft data-flow specification  
Owner: Product Engineer / Data Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document describes how data moves through the Greenwashing Detection system from raw documents to final outputs. It complements `PIPELINE_SPEC.md` by focusing on object lifecycle, provenance, versioning, and data dependencies.

## 2. Data-flow summary

```text
RawFile
  → Document
  → DocumentChunk / ExtractedTable / ExtractedMetric
  → SearchIndexRecord / MetricRecord
  → GreenClaim
  → ClaimGroup
  → EvidenceRequirement
  → RetrievalPlan
  → EvidenceCandidate
  → EvidenceItem
  → EvidencePackage
  → VerificationResult
  → RiskScore
  → EvidenceCard / Dashboard / WorkingPaper / Report
  → HumanReviewRecord
  → AuditLogEntry
```

## 3. Object lifecycle map

| Object | Created by | Consumed by | Persisted? |
|---|---|---|---|
| `RawFile` | Document intake | Parser, audit | Yes |
| `Document` | Intake service | Processing, output | Yes |
| `DocumentChunk` | Chunker | Claim extractor, search index | Yes |
| `ExtractedTable` | Table extractor | Metric extractor, reviewer | Yes |
| `ExtractedMetric` | Metric extractor | Structured retrieval, verification | Yes |
| `SearchIndexRecord` | Index builder | Retrieval | Yes or rebuildable |
| `GreenClaim` | Claim extractor | Classifier, retrieval planner | Yes |
| `ClaimGroup` | Deduplicator | Scoring, dashboard | Yes |
| `EvidenceRequirement` | Claim classifier | Retrieval planner | Yes |
| `RetrievalPlan` | Query planner | Retrievers | Yes for audit |
| `EvidenceCandidate` | Retriever | Reranker/grader | Optional, recommended |
| `EvidenceItem` | Evidence grader | Verifier, output | Yes |
| `EvidencePackage` | Evidence selector | Verifier, scorer, output | Yes |
| `VerificationResult` | Verification pipeline | Scorer, output, review | Yes |
| `RiskScore` | Scoring service | Dashboard, evidence card, review | Yes |
| `EvidenceCard` | Output builder | UI, reviewer, export | Yes or generated |
| `HumanReviewRecord` | Review service | audit log, final report | Yes |
| `AuditLogEntry` | all services | audit/reproducibility | Yes |

## 4. Data states

### 4.1 Case states

```ts
CREATED
DOCUMENTS_UPLOADED
PROCESSING
PROCESSED
CLAIMS_EXTRACTED
EVIDENCE_RETRIEVED
VERIFIED
SCORED
READY_FOR_REVIEW
REVIEWED
EXPORTED
FAILED
```

### 4.2 Document states

```ts
UPLOADED
INGESTED
PROCESSING
PROCESSED
INDEXED
PROCESSING_FAILED
EXCLUDED
```

### 4.3 Claim states

```ts
EXTRACTED
CLASSIFIED
GROUPED
EVIDENCE_REQUIRED
EVIDENCE_RETRIEVED
VERIFIED
SCORED
PENDING_REVIEW
REVIEWED
EXCLUDED
```

### 4.4 Evidence states

```ts
CANDIDATE
RERANKED
SELECTED
EXCLUDED
MISSING_REQUIRED
USED_IN_VERIFICATION
```

## 5. Provenance chain

Every claim-level output must support a chain like this:

```text
EvidenceCard
  → RiskScore
  → VerificationResult
  → EvidencePackage
  → EvidenceItem
  → DocumentChunk / ExtractedMetric
  → Document
  → RawFile
```

Minimum provenance fields:

```json
{
  "source_document_id": "DOC-0001",
  "source_chunk_id": "CHUNK-0007",
  "source_page": 42,
  "source_section": "Environment",
  "source_span": {
    "start_char": 120,
    "end_char": 340
  },
  "extraction_method": "PDF_TEXT_EXTRACTOR",
  "extraction_confidence": 0.92
}
```

If the system cannot preserve provenance, the data should be marked with a quality flag and should not support a `SUPPORTED` verdict by itself.

## 6. Main data flows

### 6.1 Raw document flow

```text
RawFile
→ Document metadata
→ text/table extraction
→ chunks + metrics
→ indexes + metric store
```

Primary quality risks:

- OCR failure;
- table misalignment;
- missing page numbers;
- unit conversion error;
- duplicate documents;
- outdated source version.

Required controls:

- content hash;
- page reference;
- extraction method;
- confidence score;
- data quality flags.

### 6.2 Claim flow

```text
DocumentChunk
→ GreenClaim
→ ClaimCategory
→ ClaimGroup
→ Materiality
→ EvidenceRequirement
```

Primary quality risks:

- marketing slogan extracted as high-materiality claim;
- duplicate claim counted multiple times;
- claim paraphrased incorrectly;
- missing source page;
- wrong category assignment.

Required controls:

- exact claim text;
- source chunk link;
- extraction confidence;
- category enum validation;
- deduplication/grouping trace.

### 6.3 Evidence flow

```text
EvidenceRequirement
→ RetrievalPlan
→ CandidateEvidence
→ RerankedEvidence
→ EvidenceItem
→ EvidencePackage
```

Primary quality risks:

- retrieving similar but irrelevant documents;
- retrieving support but not contradiction;
- using weak media/marketing evidence for strong claim;
- wrong year or boundary;
- missing required evidence not recorded.

Required controls:

- retrieval method;
- retrieval score;
- evidence role;
- evidence strength;
- exclusion reason;
- missing evidence records.

### 6.4 Verification and scoring flow

```text
GreenClaim + EvidencePackage
→ FiveLayerVerification
→ Verdict
→ CriterionScores
→ RiskScore
→ RiskLabel
```

Primary quality risks:

- unsupported verdict due to weak evidence;
- arithmetic scoring error;
- score thresholds drift;
- contradiction asserted without evidence;
- legal/taxonomy check skipped silently.

Required controls:

- layer-level status;
- evidence IDs in rationale;
- score version;
- criterion-level scores;
- deterministic scoring tests.

### 6.5 Human review flow

```text
EvidenceCard
→ ReviewTrigger
→ ReviewerDecision
→ RevisedVerdict or AcceptedVerdict
→ AuditLog
→ Feedback item
```

Primary quality risks:

- reviewer action overwrites AI output;
- no explanation for revised verdict;
- feedback not captured;
- high-risk case not routed to review.

Required controls:

- review status;
- reviewer ID;
- timestamp;
- old/new value;
- reason for revision;
- immutable audit log.

## 7. Data dependencies by output

### 7.1 Company dashboard

Depends on:

- `Case`
- all `GreenClaim`
- all `RiskScore`
- all `VerificationResult`
- review status

Must not depend directly on raw LLM output.

### 7.2 Claim table

Depends on:

- `GreenClaim`
- `ClaimCategory`
- `VerificationResult`
- `RiskScore`
- `ReviewStatus`

### 7.3 Evidence card

Depends on:

- `GreenClaim`
- `EvidencePackage`
- `VerificationResult`
- `RiskScore`
- `HumanReviewRecord`

### 7.4 Working paper

Depends on:

- `GreenClaim`
- all candidate and selected evidence if available
- layer verification
- scoring detail
- reviewer comments
- audit log references

### 7.5 Company report

Depends on:

- dashboard summary;
- top risk claims;
- evidence cards;
- limitations;
- review status;
- methodology version.

## 8. Versioning model

Version these objects:

| Object | Version reason |
|---|---|
| `Document` | source file replaced or metadata corrected |
| `DocumentChunk` | chunking strategy changed |
| `ExtractedMetric` | extraction correction or unit normalization changed |
| `GreenClaim` | claim text/category/materiality changed |
| `EvidencePackage` | retrieval/reranking/grading changed |
| `VerificationResult` | verdict logic changed |
| `RiskScore` | scoring rule or reviewer revision changed |
| `OutputExport` | report regenerated |

Do not overwrite previous versions in high-risk or reviewed cases.

## 9. Data lineage requirements

Every final export must include:

- case ID;
- methodology version;
- score version;
- index version;
- source document list;
- claim IDs;
- evidence IDs;
- review status;
- export timestamp.

## 10. Data retention assumptions for MVP

MVP can use local files and local database, but it must mimic production data boundaries:

```text
/data/raw-files
/data/processed
/data/indexes
/data/exports
```

Avoid mixing raw files and generated outputs in the same folder.

## 11. Privacy and sensitivity note

The system may process company reports, financial documents, and external sources. For MVP, use public or synthetic documents unless project owners explicitly approve private materials. Do not send private documents to external model APIs without explicit approval and logging.

## 12. Open questions

1. Should candidate evidence be persisted or only selected evidence?
2. Should each retrieval run create a unique run ID?
3. Should reviewer revisions create new `VerificationResult` objects or a separate override object?
4. How much raw extracted table structure is needed for UI debugging?
