# PIPELINE_SPEC.md

Version: 0.1  
Status: Draft implementation spec  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document specifies the end-to-end pipeline for the Greenwashing Detection MVP. Each stage defines input, output, processing logic, validation, error handling, and acceptance criteria.

The pipeline implements the workflow from `MVP_SCOPE.md`:

```text
Upload documents
→ Parse into chunks and metrics
→ Extract green claims
→ Classify claims
→ Define evidence requirements
→ Retrieve supporting and contradicting evidence
→ Grade evidence
→ Verify five layers
→ Assign verdict
→ Score risk
→ Show evidence card and dashboard
→ Human reviewer action
→ Export working paper/report
```

## 2. Pipeline principles

1. Every stage must be idempotent where possible.
2. Every generated object must include stable IDs.
3. Every claim, evidence item, and score must be traceable.
4. No LLM output is accepted without schema validation.
5. Missing evidence must be represented explicitly, not silently ignored.
6. Human review must be triggered for high-risk or uncertain outputs.

## 3. Stage 0 — Case registration

### Purpose

Create the assessment container for one company, year, and review scope.

### Input

```json
{
  "company_name": "ABC Corporation",
  "industry": "Manufacturing",
  "reporting_year": 2024,
  "review_scope": "ESG report + annual report + financial statements",
  "reviewer_id": "USER-0001"
}
```

### Output

```json
{
  "case_id": "CASE-0001",
  "status": "CREATED",
  "created_at": "2026-07-07T00:00:00Z"
}
```

### Validation

- `company_name` required.
- `reporting_year` required.
- `industry` recommended; if missing, set `industry = UNKNOWN` and add a data quality flag.

### Acceptance criteria

- A stable `case_id` is created.
- An audit log entry is written.

## 4. Stage 1 — Document intake

### Purpose

Accept source documents and preserve raw source references.

### Input

- PDF, text, markdown, CSV, JSON fixture, or extracted text file.
- Required metadata: company, year, source type.

### Output

`Document` object:

```json
{
  "document_id": "DOC-0001",
  "case_id": "CASE-0001",
  "source_type": "ESG_REPORT",
  "file_name": "abc-esg-2024.pdf",
  "file_uri": "storage://cases/CASE-0001/raw/abc-esg-2024.pdf",
  "company_name": "ABC Corporation",
  "reporting_year": 2024,
  "ingestion_status": "INGESTED",
  "provenance": {
    "uploaded_by": "USER-0001",
    "uploaded_at": "2026-07-07T00:00:00Z",
    "content_hash": "sha256:..."
  }
}
```

### Error handling

| Error | Behavior |
|---|---|
| Unsupported file type | reject file, create audit event |
| Missing metadata | accept only if user confirms defaults, add flag |
| Corrupted file | reject and ask for replacement |

### Acceptance criteria

- Raw file preserved.
- Content hash created.
- Document metadata saved.

## 5. Stage 2 — Document processing

### Purpose

Convert documents into processable chunks, tables, and metrics.

### Input

- `Document`
- raw file reference

### Processing

1. Detect document type.
2. Extract text.
3. Extract tables when possible.
4. Extract or mock metrics.
5. Split text into chunks.
6. Normalize unit, year, company, page/section.
7. Run data quality checks.

### Output

```json
{
  "document_id": "DOC-0001",
  "chunks": ["CHUNK-0001", "CHUNK-0002"],
  "metrics": ["METRIC-0001"],
  "tables": ["TABLE-0001"],
  "quality_flags": ["MISSING_SCOPE_FOR_EMISSIONS_TABLE"],
  "processing_status": "PROCESSED"
}
```

### Data quality checks

- missing page reference;
- missing reporting year;
- missing unit;
- ambiguous metric name;
- table extraction confidence low;
- OCR confidence low;
- inconsistent company/year metadata.

### Acceptance criteria

- Chunks include source page or section.
- Metrics include unit and period when available.
- Quality flags are not lost.

## 6. Stage 3 — Index building

### Purpose

Build searchable and structured stores for retrieval.

### Input

- `DocumentChunk[]`
- `ExtractedMetric[]`
- taxonomy/legal rule files

### Processing

1. Add chunks to full-text index.
2. Add chunks to vector index where available.
3. Add metrics to structured metric store.
4. Add taxonomy/legal rules to rule store.
5. Record index version.

### Output

```json
{
  "case_id": "CASE-0001",
  "index_version": "IDX-20260707-0001",
  "text_index_status": "READY",
  "vector_index_status": "READY_OR_SKIPPED",
  "metric_store_status": "READY",
  "rule_store_status": "READY"
}
```

### Acceptance criteria

- Search can return chunk IDs.
- Metric lookup can return metric IDs.
- Index version is stored for reproducibility.

## 7. Stage 4 — Claim extraction

### Purpose

Identify sustainability-related claims from processed documents.

### Input

- chunks from company reports, ESG reports, annual reports, finance documents, external documents

### Processing

1. Scan chunks for green/sustainability-related statements.
2. Preserve exact claim text.
3. Create initial claim object.
4. Assign extraction confidence.
5. Link source chunk and page.

### Output

```json
{
  "claim_id": "CLAIM-0001",
  "case_id": "CASE-0001",
  "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
  "source_document_id": "DOC-0001",
  "source_chunk_id": "CHUNK-0007",
  "source_page": 42,
  "extraction_method": "RULE_BASED_OR_LLM",
  "extraction_confidence": 0.86
}
```

### Acceptance criteria

- Exact claim text preserved.
- Claim has source document and source location.
- Low-confidence claims are marked for review or secondary extraction.

## 8. Stage 5 — Claim classification and normalization

### Purpose

Classify each claim using the taxonomy and prepare evidence requirements.

### Input

- `GreenClaim[]`
- taxonomy from `GREENWASHING_TAXONOMY.md`
- company profile/materiality map

### Processing

1. Assign claim category.
2. Assign greenwashing pattern candidates.
3. Determine whether claim is quantifiable.
4. Normalize duplicate/similar claims.
5. Group related claims.
6. Assign materiality.
7. Generate evidence requirements.

### Output

```json
{
  "claim_id": "CLAIM-0001",
  "claim_group_id": "CG-0001",
  "claim_category": "EMISSIONS_REDUCTION",
  "pattern_candidates": ["QUANTITATIVE_CONTRADICTION", "BASELINE_MANIPULATION"],
  "is_quantifiable": true,
  "materiality": "HIGH",
  "required_evidence_types": [
    "CURRENT_PERIOD_EMISSIONS",
    "BASELINE_EMISSIONS",
    "SCOPE_BOUNDARY",
    "ASSURANCE_STATEMENT"
  ]
}
```

### Acceptance criteria

- Every claim has at least one category.
- Duplicate claims are grouped, not deleted.
- Evidence requirements are explicit.

## 9. Stage 6 — Evidence query planning

### Purpose

Generate retrieval plans for supporting and contradicting evidence.

### Input

- classified claim
- evidence requirements
- company profile
- available source inventory

### Processing

For each claim, generate:

- supporting search queries;
- contradicting search queries;
- structured metric lookups;
- legal/taxonomy rule lookups;
- fallback missing evidence requests.

### Output

```json
{
  "claim_id": "CLAIM-0001",
  "retrieval_plan_id": "RP-0001",
  "supporting_queries": [
    "Scope 1 Scope 2 emissions 2024 ABC",
    "GHG emissions table ABC 2024"
  ],
  "contradicting_queries": [
    "ABC emissions increased 2024",
    "ABC environmental violation 2024"
  ],
  "structured_lookups": [
    "metric:scope_1_2_emissions:2023:2024"
  ]
}
```

### Acceptance criteria

- Material claims always include contradiction search.
- Quantitative claims include structured metric lookup where metrics exist.

## 10. Stage 7 — Evidence retrieval

### Purpose

Retrieve candidate evidence from internal and external stores.

### Input

- retrieval plan
- search indexes
- metric store
- rule store

### Processing

1. Run full-text search.
2. Run vector search where enabled.
3. Run structured metric query.
4. Run taxonomy/legal rule lookup.
5. Fuse or merge results.
6. Preserve retrieval scores and method.

### Output

```json
{
  "claim_id": "CLAIM-0001",
  "candidate_evidence": [
    {
      "evidence_id": "EVID-0001",
      "source_document_id": "DOC-0001",
      "source_page": 42,
      "retrieval_method": "STRUCTURED_METRIC_LOOKUP",
      "retrieval_score": 0.98,
      "evidence_role_candidate": "SUPPORTING"
    }
  ]
}
```

### Acceptance criteria

- Evidence retrieval stores method and score.
- No candidate evidence is used for verdict until graded.

## 11. Stage 8 — Evidence reranking and grading

### Purpose

Select useful evidence and classify evidence strength.

### Input

- candidate evidence
- evidence standard
- claim evidence requirements

### Processing

1. Rerank evidence by relevance.
2. Assign evidence role:
   - `SUPPORTING`
   - `CONTRADICTING`
   - `CONTEXTUAL`
   - `EXCLUDED`
   - `MISSING_REQUIRED`
3. Assign evidence strength L1–L5.
4. Exclude weak or mismatched evidence with reason.
5. Create missing evidence items where requirements are unmet.

### Output

```json
{
  "claim_id": "CLAIM-0001",
  "selected_evidence": ["EVID-0001", "EVID-0002"],
  "excluded_evidence": [
    {
      "evidence_id": "EVID-0005",
      "reason": "Wrong reporting year"
    }
  ],
  "missing_required_evidence": [
    "ASSURANCE_STATEMENT"
  ]
}
```

### Acceptance criteria

- Evidence strength is assigned.
- Excluded evidence has a reason.
- Missing evidence is explicit.

## 12. Stage 9 — Five-layer verification

### Purpose

Apply audit-style verification to the claim-evidence package.

### Input

- claim
- selected evidence
- missing evidence
- score rubric

### Processing layers

1. Specificity check.
2. Evidence availability check.
3. Quantitative consistency check.
4. Legal/taxonomy alignment check.
5. External contradiction check.

### Output

```json
{
  "verification_id": "VER-0001",
  "claim_id": "CLAIM-0001",
  "layer_results": {
    "specificity": "PASS",
    "evidence_availability": "PARTIAL",
    "quantitative_consistency": "FAIL",
    "legal_taxonomy_alignment": "NOT_APPLICABLE",
    "external_contradiction": "NO_MATERIAL_CONTRADICTION_FOUND"
  },
  "recommended_verdict": "CONTRADICTED",
  "rationale": "The claim states a reduction, but Scope 1+2 emissions increased from baseline to current year."
}
```

### Acceptance criteria

- Every layer has a status.
- Rationale references evidence IDs.
- Contradiction cannot be asserted without evidence ID.

## 13. Stage 10 — Risk scoring

### Purpose

Apply the 0–100 manual scoring rubric.

### Input

- claim
- verification result
- evidence package
- materiality

### Processing

Score criteria:

- C1 specificity weakness, max 15;
- C2 missing quantitative data, max 15;
- C3 missing baseline/time/scope, max 10;
- C4 weak or missing evidence, max 20;
- C5 lack of independent assurance, max 10;
- C6 contradictory evidence, max 20;
- C7 overstatement/misleading presentation, max 10.

### Output

```json
{
  "score_id": "SCORE-0001",
  "claim_id": "CLAIM-0001",
  "score_version": "manual-rubric-0.1",
  "total_score": 78,
  "risk_label": "VERY_HIGH",
  "criteria_scores": {
    "C1": 5,
    "C2": 0,
    "C3": 3,
    "C4": 10,
    "C5": 10,
    "C6": 20,
    "C7": 10
  },
  "score_rationale": "Material quantitative claim contradicted by reported emissions table."
}
```

### Acceptance criteria

- Total score equals sum of criteria and modifiers.
- Criterion rationale is stored.
- Score version is stored.

## 14. Stage 11 — Output generation

### Purpose

Generate product outputs for review.

### Input

- claims
- evidence packages
- verification results
- scores
- review status

### Output

- `CompanyDashboard`
- `ClaimTable`
- `EvidenceCard`
- `ClaimWorkingPaper`
- `CompanyReport`
- `JsonExport`

### Acceptance criteria

- Evidence card includes claim, verdict, risk score, evidence, missing evidence, explanation.
- Report includes limitation note.
- JSON export validates against output schema.

## 15. Stage 12 — Human review

### Purpose

Route high-risk or uncertain claims to reviewer.

### Input

- evidence card
- risk score
- verdict
- review triggers

### Default triggers

- `risk_score >= 70`
- `verdict = CONTRADICTED`
- `verdict = INSUFFICIENT_EVIDENCE` and materiality high
- evidence strength below required minimum
- low extraction confidence
- low table/OCR confidence

### Output

```json
{
  "review_id": "REV-0001",
  "claim_id": "CLAIM-0001",
  "review_status": "PENDING_REVIEW",
  "trigger_reason": "VERY_HIGH_RISK_AND_CONTRADICTED"
}
```

### Acceptance criteria

- Review status is visible in UI and export.
- Reviewer action is audit logged.

## 16. Stage 13 — Feedback and audit logging

### Purpose

Preserve accountability and improve future runs.

### Input

- reviewer decisions
- system-generated outputs
- user actions

### Output

- audit log entries;
- rule feedback;
- open questions;
- test case candidates.

### Acceptance criteria

- Every reviewer decision has timestamp and reviewer ID.
- Revisions do not overwrite original AI output; they create a new version.

## 17. Global failure modes

| Failure | Required behavior |
|---|---|
| Claim extracted without source | reject claim or mark invalid |
| Evidence retrieved without source | exclude evidence |
| Score produced without verification result | reject score |
| Report generated with missing evidence links | warn and block final export unless user confirms draft |
| AI output violates schema | retry or send to manual review |

## 18. MVP run modes

| Mode | Description |
|---|---|
| `fixture_demo` | Uses sample documents, pre-extracted metrics, and deterministic outputs. |
| `local_pipeline` | Runs parser, extractor, retrieval, scoring locally. |
| `review_only` | Loads JSON export and allows human review. |
| `api_mode` | Full backend API mode, future. |

## 19. Open implementation questions

1. Which file formats are guaranteed in the first demo?
2. Should extracted tables be stored as raw cell grid, normalized metric rows, or both?
3. Will vector search be enabled in MVP or deferred?
4. How should duplicate claim groups affect company-level scoring?
5. Should reviewer corrections feed an immediate rerun or only future runs?
