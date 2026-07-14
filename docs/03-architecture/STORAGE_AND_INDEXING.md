# STORAGE_AND_INDEXING.md

Version: 0.1  
Status: Draft storage and retrieval architecture  
Owner: Product Engineer / Data Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines how data should be stored, indexed, retrieved, and versioned for the Greenwashing Detection MVP.

Storage must support auditability, not only application convenience. The system must be able to answer:

```text
Where did this claim come from?
Which evidence was retrieved?
Which evidence was used?
Which evidence was excluded?
Which version of the scoring method produced this result?
Who reviewed or changed it?
```

## 2. Storage principles

1. Raw source files must be preserved.
2. Generated data must be linked back to raw source and processing run.
3. Search indexes may be rebuildable, but index version must be recorded.
4. Evidence and verdicts must be persisted for audit review.
5. Reviewer revisions must create new versions or review records, not silent overwrites.
6. Methodology and score versions must be stored with outputs.

## 3. Logical storage layers

```text
Raw file store
Processed document store
Structured metric store
Search indexes
Domain database
Export store
Audit log store
```

## 4. MVP storage options

### 4.1 Simplest local MVP

Recommended for first prototype:

```text
data/
  raw/
  processed/
  indexes/
  exports/
  fixtures/
```

Use:

- local file system for raw files and exports;
- SQLite/Postgres for domain records;
- in-memory or local search index for retrieval;
- JSON fixtures for legal/taxonomy rules.

### 4.2 Production-like direction

Future direction:

- object storage for raw files;
- relational database for domain records;
- search engine for BM25/full-text;
- vector database or vector-capable search engine;
- separate audit log table or append-only event store.

## 5. Entity storage model

### 5.1 Required persisted entities

| Entity | Persisted? | Reason |
|---|---|---|
| `Case` | Yes | assessment container |
| `Document` | Yes | source inventory and provenance |
| `DocumentChunk` | Yes | source trace and retrieval target |
| `ExtractedMetric` | Yes | quantitative verification |
| `GreenClaim` | Yes | audit unit of work |
| `ClaimGroup` | Yes | deduplication and aggregation |
| `EvidenceRequirement` | Yes | missing evidence reasoning |
| `RetrievalPlan` | Recommended | audit/debug retrieval behavior |
| `EvidenceCandidate` | Optional but recommended | retrieval evaluation |
| `EvidenceItem` | Yes | verification input |
| `EvidencePackage` | Yes | claim-level evidence set |
| `VerificationResult` | Yes | verdict and rationale |
| `RiskScore` | Yes | criterion scoring and labels |
| `HumanReviewRecord` | Yes | accountability |
| `AuditLogEntry` | Yes | traceability |
| `ExportRecord` | Yes | reproducibility |

### 5.2 Rebuildable entities

These can be rebuilt but must have version records:

- keyword index;
- vector index;
- reranker cache;
- generated dashboard views;
- generated reports.

## 6. Raw file storage

Raw files must be immutable after upload.

Minimum metadata:

```json
{
  "document_id": "DOC-0001",
  "file_uri": "storage://cases/CASE-0001/raw/file.pdf",
  "file_name": "file.pdf",
  "mime_type": "application/pdf",
  "content_hash": "sha256:...",
  "uploaded_at": "2026-07-07T00:00:00Z",
  "uploaded_by": "USER-0001"
}
```

If a document is corrected, create a new document version.

## 7. Processed document storage

### 7.1 Chunks

Chunk records should preserve source location.

```json
{
  "chunk_id": "CHUNK-0001",
  "document_id": "DOC-0001",
  "page_start": 12,
  "page_end": 13,
  "section_title": "Environmental Performance",
  "text": "...",
  "token_count": 420,
  "chunk_strategy": "page_section_v0.1",
  "extraction_confidence": 0.93
}
```

### 7.2 Tables

Store both raw table representation and normalized metrics where possible.

```json
{
  "table_id": "TABLE-0001",
  "document_id": "DOC-0001",
  "page": 42,
  "caption": "GHG emissions",
  "cells": [["Metric", "2023", "2024"], ["Scope 1+2", "100000", "125000"]],
  "extraction_confidence": 0.88
}
```

### 7.3 Metrics

```json
{
  "metric_id": "METRIC-0001",
  "case_id": "CASE-0001",
  "document_id": "DOC-0001",
  "source_table_id": "TABLE-0001",
  "metric_name": "scope_1_2_emissions",
  "value": 125000,
  "unit": "tCO2e",
  "period": "2024",
  "boundary": "company-wide",
  "source_page": 42,
  "normalization_notes": "Combined Scope 1 and Scope 2 as reported."
}
```

## 8. Search indexes

The retrieval system should support at least two modes:

1. full-text/keyword search for exact terms, values, legal references, and document codes;
2. vector search for semantic similarity.

Hybrid retrieval is recommended for evidence search because environmental claims often require both exact terms and semantic matching.

## 9. Keyword index

Keyword index targets:

- document chunks;
- table captions;
- metric names;
- source types;
- external evidence snippets;
- legal/taxonomy rules.

Fields:

```json
{
  "record_id": "IDXTXT-0001",
  "object_type": "DOCUMENT_CHUNK",
  "object_id": "CHUNK-0001",
  "case_id": "CASE-0001",
  "text": "...",
  "source_type": "ESG_REPORT",
  "company_name": "ABC Corporation",
  "reporting_year": 2024
}
```

Use cases:

- “Scope 1”;
- “tCO2e”;
- “green bond allocation”;
- “Decision No.”;
- “environmental penalty”.

## 10. Vector index

Vector index targets:

- document chunks;
- external evidence snippets;
- taxonomy descriptions;
- claim text.

Fields:

```json
{
  "record_id": "IDXVEC-0001",
  "object_type": "DOCUMENT_CHUNK",
  "object_id": "CHUNK-0001",
  "embedding_model": "embedding-model-name",
  "embedding_version": "v0.1",
  "vector": [0.01, 0.02],
  "text_preview": "..."
}
```

MVP may skip real embeddings if fixture retrieval is used, but the interface should remain.

## 11. Hybrid retrieval and RRF

Recommended hybrid pattern:

```text
keyword query results
+ vector query results
+ structured metric lookup results
→ fusion/reranking
→ evidence candidates
```

If Reciprocal Rank Fusion is implemented, preserve:

- source ranking method;
- original rank;
- fused score;
- reranker score if used.

Example trace:

```json
{
  "evidence_id": "EVID-0001",
  "retrieval_trace": [
    {
      "method": "BM25",
      "rank": 2,
      "score": 12.4
    },
    {
      "method": "VECTOR",
      "rank": 5,
      "score": 0.82
    },
    {
      "method": "RRF",
      "rank": 1,
      "score": 0.031
    }
  ]
}
```

## 12. Structured metric store

Structured metrics are essential for quantitative contradiction checks.

Minimum query capabilities:

- find metric by company, year, metric name;
- compare current period vs baseline;
- filter by boundary/scope;
- return source document and page;
- return normalization notes.

Example lookup:

```text
getMetric(company="ABC", metric="scope_1_2_emissions", periods=[2023, 2024])
```

## 13. Legal and taxonomy rule store

Rules should be versioned separately from code.

Example shape:

```json
{
  "rule_id": "RULE-GREEN-FINANCE-001",
  "rule_set": "vietnam_green_taxonomy_v0.1",
  "claim_category": "GREEN_BOND",
  "required_evidence": [
    "eligible_project_list",
    "use_of_proceeds_tracking",
    "allocation_report",
    "external_review_or_assurance"
  ],
  "severity_if_missing": "HIGH"
}
```

MVP may use project-context rules and mark Vietnam-specific legal references as `TO_VERIFY` until official source files are added.

## 14. External source storage

External evidence should include timestamp and source reliability.

```json
{
  "external_source_id": "EXT-0001",
  "source_type": "NEWS_OR_ENFORCEMENT",
  "publisher": "Regulator or news publisher",
  "published_at": "2024-10-01",
  "retrieved_at": "2026-07-07T00:00:00Z",
  "url": "...",
  "text": "...",
  "reliability_level": "L1_HIGH_AUTHORITY_OR_L4_EXTERNAL"
}
```

For MVP, external sources can be fixtures.

## 15. Audit log storage

Audit logs should be append-only.

Minimum fields:

```json
{
  "audit_log_id": "LOG-0001",
  "case_id": "CASE-0001",
  "actor_type": "SYSTEM_OR_USER_OR_AGENT",
  "actor_id": "SYSTEM",
  "event_type": "CLAIM_VERIFIED",
  "object_type": "VerificationResult",
  "object_id": "VER-0001",
  "timestamp": "2026-07-07T00:00:00Z",
  "before": null,
  "after": { "verdict": "CONTRADICTED" },
  "methodology_version": "audit-protocol-0.1"
}
```

## 16. Index rebuild policy

An index rebuild is required when:

- chunking strategy changes;
- embedding model changes;
- source documents are added/replaced;
- taxonomy/legal rules change;
- retrieval scoring method changes.

Each rebuild creates a new `index_version`.

Final outputs must record the `index_version` used.

## 17. Data quality flags

Suggested flags:

```ts
MISSING_PAGE_REFERENCE
MISSING_YEAR
MISSING_UNIT
MISSING_SCOPE
LOW_OCR_CONFIDENCE
LOW_TABLE_CONFIDENCE
AMBIGUOUS_METRIC_NAME
CONFLICTING_METADATA
UNVERIFIED_EXTERNAL_SOURCE
MISSING_BASELINE
MISSING_ASSURANCE
```

Quality flags should be visible in evidence cards and working papers when they affect confidence.

## 18. MVP acceptance criteria

The storage/indexing layer is acceptable for MVP if:

- raw files are preserved;
- chunks and metrics link back to documents;
- claims link back to chunks;
- evidence links back to chunks, metrics, rules, or external sources;
- verification and scores link back to evidence;
- review actions are audit logged;
- exports can be reproduced from persisted data.

## 19. Open questions

1. Should the project use SQLite, Postgres, or file-based JSON for MVP?
2. Should vector index be local-only at first?
3. Should external sources be stored as documents or separate source objects?
4. What retention policy applies to uploaded private documents?
