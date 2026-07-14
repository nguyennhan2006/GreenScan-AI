# API_CONTRACTS.md

Version: 0.1  
Status: Draft API contract  
Owner: Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines API contracts for the Greenwashing Detection MVP. The contracts are framework-neutral and can be implemented as REST endpoints, RPC functions, server actions, or CLI commands.

The API must expose evidence-first outputs without allowing the UI to recompute domain logic.

## 2. API principles

1. API responses must use stable IDs and documented enums.
2. API responses must include source references for claim/evidence outputs.
3. UI must not calculate verdicts or risk scores.
4. Long-running pipeline operations should return run IDs or status objects.
5. Reviewer actions must be audit logged.
6. Exports must include methodology and score version.

## 3. Shared enums

### 3.1 Verdict

```ts
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
```

### 3.2 Risk label

```ts
LOW
MODERATE
HIGH
VERY_HIGH
CRITICAL
```

### 3.3 Evidence role

```ts
SUPPORTING
CONTRADICTING
CONTEXTUAL
EXCLUDED
MISSING_REQUIRED
```

### 3.4 Evidence strength

```ts
L1_HIGH_AUTHORITY
L2_OFFICIAL_DISCLOSURE
L3_COMPANY_UNASSURED_DATA
L4_EXTERNAL_OR_MEDIA
L5_MARKETING_OR_LOW_RELIABILITY
```

### 3.5 Review status

```ts
NOT_REQUIRED
PENDING_REVIEW
ACCEPTED
REVISED
REJECTED
ESCALATED
```

## 4. Case APIs

### 4.1 Create case

`POST /cases`

Request:

```json
{
  "company_name": "ABC Corporation",
  "industry": "Manufacturing",
  "reporting_year": 2024,
  "review_scope": "ESG report + annual report + financial statements"
}
```

Response:

```json
{
  "case_id": "CASE-0001",
  "status": "CREATED",
  "created_at": "2026-07-07T00:00:00Z"
}
```

### 4.2 Get case

`GET /cases/{case_id}`

Response:

```json
{
  "case_id": "CASE-0001",
  "company_name": "ABC Corporation",
  "industry": "Manufacturing",
  "reporting_year": 2024,
  "status": "SCORED",
  "documents_count": 3,
  "claims_count": 38,
  "methodology_version": "audit-protocol-0.1"
}
```

## 5. Document APIs

### 5.1 Upload document

`POST /cases/{case_id}/documents`

Request:

- multipart file or fixture reference;
- metadata JSON.

Metadata:

```json
{
  "source_type": "ESG_REPORT",
  "reporting_year": 2024,
  "document_title": "ABC ESG Report 2024"
}
```

Response:

```json
{
  "document_id": "DOC-0001",
  "case_id": "CASE-0001",
  "file_name": "abc-esg-2024.pdf",
  "ingestion_status": "INGESTED",
  "content_hash": "sha256:..."
}
```

### 5.2 List documents

`GET /cases/{case_id}/documents`

Response:

```json
{
  "documents": [
    {
      "document_id": "DOC-0001",
      "source_type": "ESG_REPORT",
      "file_name": "abc-esg-2024.pdf",
      "processing_status": "PROCESSED",
      "quality_flags": []
    }
  ]
}
```

## 6. Pipeline run APIs

### 6.1 Run full pipeline

`POST /cases/{case_id}/runs`

Request:

```json
{
  "run_mode": "fixture_demo",
  "stages": "ALL",
  "options": {
    "use_vector_search": false,
    "use_external_fixtures": true
  }
}
```

Response:

```json
{
  "run_id": "RUN-0001",
  "case_id": "CASE-0001",
  "status": "QUEUED",
  "requested_stages": [
    "PROCESS_DOCUMENTS",
    "EXTRACT_CLAIMS",
    "RETRIEVE_EVIDENCE",
    "VERIFY",
    "SCORE",
    "BUILD_OUTPUTS"
  ]
}
```

### 6.2 Get run status

`GET /cases/{case_id}/runs/{run_id}`

Response:

```json
{
  "run_id": "RUN-0001",
  "status": "COMPLETED",
  "stage_status": {
    "PROCESS_DOCUMENTS": "COMPLETED",
    "EXTRACT_CLAIMS": "COMPLETED",
    "RETRIEVE_EVIDENCE": "COMPLETED",
    "VERIFY": "COMPLETED",
    "SCORE": "COMPLETED",
    "BUILD_OUTPUTS": "COMPLETED"
  },
  "errors": [],
  "warnings": ["VECTOR_SEARCH_SKIPPED_IN_FIXTURE_MODE"]
}
```

## 7. Claim APIs

### 7.1 List claims

`GET /cases/{case_id}/claims`

Query params:

- `verdict`
- `risk_label`
- `category`
- `review_status`
- `materiality`

Response:

```json
{
  "claims": [
    {
      "claim_id": "CLAIM-0001",
      "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
      "claim_category": "EMISSIONS_REDUCTION",
      "materiality": "HIGH",
      "verdict": "CONTRADICTED",
      "risk_score": 78,
      "risk_label": "VERY_HIGH",
      "review_status": "PENDING_REVIEW",
      "source_document_id": "DOC-0001",
      "source_page": 42
    }
  ]
}
```

### 7.2 Get claim detail

`GET /cases/{case_id}/claims/{claim_id}`

Response:

```json
{
  "claim_id": "CLAIM-0001",
  "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
  "source": {
    "document_id": "DOC-0001",
    "page": 42,
    "chunk_id": "CHUNK-0007"
  },
  "classification": {
    "claim_category": "EMISSIONS_REDUCTION",
    "pattern_candidates": ["QUANTITATIVE_CONTRADICTION"],
    "is_quantifiable": true,
    "materiality": "HIGH"
  },
  "required_evidence_types": [
    "CURRENT_PERIOD_EMISSIONS",
    "BASELINE_EMISSIONS",
    "SCOPE_BOUNDARY"
  ]
}
```

## 8. Evidence APIs

### 8.1 Get evidence card

`GET /cases/{case_id}/claims/{claim_id}/evidence-card`

Response:

```json
{
  "evidence_card_id": "ECARD-0001",
  "claim_id": "CLAIM-0001",
  "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
  "verdict": "CONTRADICTED",
  "risk_score": 78,
  "risk_label": "VERY_HIGH",
  "explanation": "The claim states a reduction, but the reported Scope 1+2 emissions increased from 100,000 tCO2e in 2023 to 125,000 tCO2e in 2024.",
  "evidence": [
    {
      "evidence_id": "EVID-0001",
      "role": "CONTRADICTING",
      "strength": "L2_OFFICIAL_DISCLOSURE",
      "source_document_id": "DOC-0001",
      "source_page": 42,
      "quote_or_value": "Scope 1+2 emissions: 2023 = 100,000; 2024 = 125,000 tCO2e",
      "retrieval_method": "STRUCTURED_METRIC_LOOKUP"
    }
  ],
  "missing_evidence": ["ASSURANCE_STATEMENT"],
  "review_status": "PENDING_REVIEW"
}
```

### 8.2 List evidence for claim

`GET /cases/{case_id}/claims/{claim_id}/evidence`

Response includes selected, excluded, and missing evidence.

## 9. Dashboard APIs

### 9.1 Get company dashboard

`GET /cases/{case_id}/dashboard`

Response:

```json
{
  "case_id": "CASE-0001",
  "company_name": "ABC Corporation",
  "reporting_year": 2024,
  "company_risk_score": 72,
  "company_risk_label": "HIGH",
  "total_claims": 38,
  "verdict_distribution": {
    "SUPPORTED": 12,
    "PARTIALLY_SUPPORTED": 9,
    "UNSUPPORTED": 8,
    "CONTRADICTED": 6,
    "INSUFFICIENT_EVIDENCE": 3
  },
  "top_risk_categories": ["EMISSIONS", "GREEN_FINANCE", "LEGAL_COMPLIANCE"],
  "review_queue_count": 8
}
```

## 10. Review APIs

### 10.1 Submit review decision

`POST /cases/{case_id}/claims/{claim_id}/review`

Request:

```json
{
  "decision": "REVISE",
  "revised_verdict": "PARTIALLY_SUPPORTED",
  "revised_score": 58,
  "comment": "Contradiction exists but the claim appears to refer only to market-based Scope 2, not total Scope 1+2. Needs scope clarification.",
  "reviewer_id": "USER-0001"
}
```

Response:

```json
{
  "review_id": "REV-0001",
  "claim_id": "CLAIM-0001",
  "review_status": "REVISED",
  "audit_log_id": "LOG-0001"
}
```

Rules:

- reviewer decision must not delete original AI verdict;
- revised verdict/score must create a review override or new version;
- comment required for `REVISED`, `REJECTED`, or `ESCALATED`.

## 11. Export APIs

### 11.1 Export working paper

`POST /cases/{case_id}/claims/{claim_id}/exports/working-paper`

Request:

```json
{
  "format": "MARKDOWN"
}
```

Response:

```json
{
  "export_id": "EXP-0001",
  "format": "MARKDOWN",
  "file_uri": "storage://cases/CASE-0001/exports/CLAIM-0001-working-paper.md",
  "created_at": "2026-07-07T00:00:00Z"
}
```

### 11.2 Export company report

`POST /cases/{case_id}/exports/company-report`

Request:

```json
{
  "format": "MARKDOWN",
  "include_appendix": true
}
```

### 11.3 Export JSON bundle

`POST /cases/{case_id}/exports/json`

Response should include a machine-readable bundle with claims, evidence, verification, scores, review status, and methodology versions.

## 12. Error response format

```json
{
  "error": {
    "code": "SCHEMA_VALIDATION_FAILED",
    "message": "Claim category is not recognized.",
    "details": {
      "field": "claim_category",
      "received": "GREENISH"
    },
    "request_id": "REQ-0001"
  }
}
```

## 13. Required API errors

| Code | Meaning |
|---|---|
| `CASE_NOT_FOUND` | invalid case ID |
| `DOCUMENT_NOT_FOUND` | invalid document ID |
| `CLAIM_NOT_FOUND` | invalid claim ID |
| `SCHEMA_VALIDATION_FAILED` | request or generated object violates schema |
| `PIPELINE_STAGE_FAILED` | a pipeline stage failed |
| `EVIDENCE_NOT_TRACEABLE` | evidence lacks source reference |
| `EXPORT_BLOCKED_MISSING_SOURCES` | export would omit required citations |
| `REVIEW_COMMENT_REQUIRED` | reviewer revision needs explanation |

## 14. Security and access assumptions for MVP

MVP may run in single-user mode. Still, the API design should preserve:

- `actor_id`;
- `reviewer_id`;
- timestamps;
- audit logs.

Production should add authentication, authorization, and role-based access.

## 15. Open questions

1. Will the first implementation use REST endpoints or local service functions only?
2. Should exports be generated synchronously or as background jobs?
3. Should `POST /runs` support partial reruns by stage?
4. Should review override be stored inside claim object or as separate review record?
