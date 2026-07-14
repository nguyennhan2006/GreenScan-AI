# EXTRACTION_SPEC.md

Version: 0.1  
Status: Draft extraction contract  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document specifies how the system extracts structured information from source documents. It covers:

- document text extraction,
- table and metric extraction,
- green claim extraction,
- claim normalization and deduplication,
- quality gates,
- structured LLM output requirements.

The extraction layer must create traceable objects, not free-form summaries.

## 2. Extraction principle

```text
Preserve source first → extract object → validate schema → attach provenance → flag uncertainty
```

No extracted claim, metric, or evidence candidate may be used downstream if it cannot be traced back to a document/page/section or explicit fixture source.

## 3. Extraction inputs

| Input type | Examples | Default extraction route |
|---|---|---|
| Digital PDF | ESG report, annual report, financial statement | text extraction + table extraction |
| Scanned PDF | scan of disclosure or legal document | OCR + manual confidence flag |
| CSV/XLSX/JSON | metric tables, fixture data | structured import |
| HTML/text | news, website, legal text | text extraction + metadata capture |
| Markdown | generated docs, test cases | direct parsing |

## 4. Document processing outputs

Document processing must generate:

- `DocumentChunk[]`,
- `ExtractedTable[]`,
- `NormalizedMetric[]`,
- `quality_flags[]`,
- source provenance.

## 5. Chunking policy

### 5.1 Goals

Chunks should be large enough to preserve meaning but small enough to support precise retrieval.

### 5.2 MVP default

| Setting | Default |
|---|---|
| Chunk target | 500–900 tokens |
| Overlap | 80–120 tokens |
| Split preference | section → paragraph → sentence |
| Required metadata | document ID, page/section, chunk index |

### 5.3 Do not split

Avoid splitting:

- table captions from tables,
- claim sentence from immediately following metric sentence,
- footnote references from the sentence they qualify,
- legal clause ID from clause text.

## 6. Table and metric extraction

### 6.1 Minimum metric fields

A metric is useful only if the system can identify:

- metric name,
- value,
- unit or explicit `MISSING_UNIT`,
- period/year or explicit `MISSING_REPORTING_YEAR`,
- source document/page.

### 6.2 Normalization examples

| Raw text | Normalized metric |
|---|---|
| `Scope 1: 120,000 tCO2e` | `metric_category = GHG_EMISSIONS`, `scope = SCOPE_1`, `unit = tCO2e` |
| `Renewable electricity 15%` | `metric_category = ENERGY`, `unit = percent` |
| `Green CAPEX: VND 200 billion` | `metric_category = CAPEX`, `unit = VND` |

### 6.3 Quality flags

Add quality flags when:

- table headers are ambiguous,
- units are missing,
- period is missing,
- row/column alignment is uncertain,
- OCR confidence is low,
- the same metric appears with conflicting values.

## 7. Green claim extraction

### 7.1 What counts as a green claim

A green claim is any statement that represents the company, product, project, bond, loan, operation, or strategy as environmentally sustainable, climate-aligned, ESG-positive, low-carbon, green, responsible, circular, compliant, certified, or transition-oriented.

### 7.2 Claim categories

Use only the `ClaimCategory` enum from `DATA_SCHEMA.md`.

### 7.3 Claim extraction output

Each extracted claim must include:

```json
{
  "claim_text": "exact source sentence or passage",
  "source_document_id": "DOC-0001",
  "source_chunk_id": "CHUNK-0007",
  "source_page": 42,
  "claim_category": "EMISSIONS_REDUCTION",
  "is_quantifiable": true,
  "mentioned_metric": "Scope 1 and 2 emissions",
  "mentioned_period": "2024",
  "extraction_confidence": 0.86
}
```

### 7.4 Extract exact text

The extractor must preserve exact claim text. Paraphrases may be stored in `normalized_claim`, not in `claim_text`.

### 7.5 Claim boundary rules

| Situation | Extraction rule |
|---|---|
| One sentence contains one claim | create one claim |
| One sentence contains multiple distinct claims | split into multiple claims, keep same source |
| Several sentences form one promise/target | create one claim with passage source |
| Repeated claim appears on multiple pages | group via `ClaimGroup`, do not delete source claims |
| Pure CSR with environmental framing | extract as `CSR_ENVIRONMENTAL` or `VAGUE_SUSTAINABILITY` |

## 8. Quantifiable claim detection

A claim is quantifiable when it contains or implies:

- numeric value,
- percentage,
- reduction/increase,
- baseline comparison,
- target date,
- investment amount,
- financed amount,
- use-of-proceeds,
- compliance threshold,
- measurable operational metric.

Examples:

| Claim | Quantifiable? | Required evidence |
|---|---|---|
| “Reduced emissions by 20%” | Yes | current metric, baseline, scope, methodology |
| “Uses renewable energy” | Usually yes | renewable energy amount/percentage |
| “Committed to net zero by 2050” | Yes | interim target, plan, CAPEX, boundary |
| “Cares for a green future” | No | qualitative support, likely vague claim |

## 9. Claim classification

### 9.1 Required classification fields

- primary category,
- secondary categories where relevant,
- greenwashing pattern candidates,
- quantifiability,
- materiality,
- required evidence types,
- classification confidence.

### 9.2 Pattern candidate guidance

Assign pattern candidates conservatively. A candidate means “this needs checking”, not “greenwashing proven”.

Examples:

| Claim signal | Candidate pattern |
|---|---|
| “green”, “eco-friendly”, “sustainable” with no metric | `VAGUE_CLAIM`, `NO_EVIDENCE` |
| “reduced emissions” without baseline | `BASELINE_MANIPULATION` |
| “green bond” without proceeds tracking | `FINANCIAL_GREENWASHING` |
| “compliant with all environmental laws” | `LEGAL_CONTRADICTION` candidate search |
| “net zero 2050” without interim plan | `EMPTY_FUTURE_COMMITMENT` |

## 10. Claim normalization and deduplication

### 10.1 Goals

Deduplication prevents inflated counts and distorted company-level scoring.

### 10.2 Similarity signals

Group claims when they share:

- same topic,
- same metric,
- same year or target period,
- same project/product/bond,
- semantically equivalent statement.

### 10.3 Do not merge

Do not merge claims if they differ materially by:

- business unit,
- geography,
- reporting year,
- metric scope,
- baseline,
- financial instrument.

### 10.4 Claim group output

```json
{
  "claim_group_id": "CG-0001",
  "canonical_claim_id": "CLAIM-0001",
  "claim_ids": ["CLAIM-0001", "CLAIM-0008"],
  "merge_reason": "Same emissions reduction claim repeated in CEO letter and ESG section"
}
```

## 11. Structured LLM extraction requirements

When an LLM is used, the output must be schema-bound.

### 11.1 Required rules

1. Return JSON only.
2. Use fixed enums only.
3. Preserve exact source text.
4. Include confidence.
5. Include source chunk ID and page if provided.
6. Do not infer missing numbers.
7. Use `UNKNOWN` or quality flags for missing fields.

### 11.2 Invalid LLM behavior

- hallucinating page numbers,
- converting vague claims into numeric claims,
- inventing evidence,
- changing enum names,
- omitting source references,
- using “true/false” instead of standard verdicts.

## 12. Extraction quality gate

Before objects enter downstream stages:

| Object | Gate |
|---|---|
| DocumentChunk | must have document ID and chunk index |
| NormalizedMetric | must have metric name, value, source, quality flags if incomplete |
| GreenClaim | must preserve exact text and source provenance |
| ClaimGroup | must preserve all original claim IDs |

## 13. MVP extraction strategy

### Phase 1 — fixture/demo

- Use prepared markdown/text/PDF samples.
- Use deterministic mock extraction for claims and metrics.
- Validate downstream pipeline before real OCR/LLM integration.

### Phase 2 — semi-automated

- Add text extraction and table extraction.
- Use rule-based claim extraction patterns.
- Allow manual correction.

### Phase 3 — LLM-assisted

- Add structured LLM extraction.
- Compare LLM extraction against fixture/manual labels.
- Store prompt version and model name.

## 14. Acceptance criteria

- All extracted claims have source provenance.
- All extracted metrics have unit/year or explicit quality flags.
- Duplicate claims are grouped, not deleted.
- Low-confidence extraction triggers review or secondary processing.
- Extraction output validates against `DATA_SCHEMA.md`.
