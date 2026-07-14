# PROMPT_CONTRACTS.md

Version: 0.1  
Status: Draft prompt and structured-output contract  
Owner: Product Engineer / AI Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines prompt contracts for AI-assisted extraction, classification, evidence grading, verification, scoring explanation, and report generation.

Prompts are implementation details; schemas and audit rules are the source of truth.

## 2. Global prompt rules

1. Use the relevant schema from `DATA_SCHEMA.md`.
2. Use fixed enums only.
3. Return structured JSON where the caller expects machine-readable output.
4. Preserve source text exactly for claims and evidence.
5. Do not invent source page, evidence, metric, or legal rule.
6. Use `UNKNOWN`, `null`, or quality flags for missing information.
7. Separate reasoning summary from hidden model reasoning; store only auditable rationale.
8. Include `prompt_version` and `model_name` in generated object provenance.

## 3. Prompt versioning

Recommended format:

```text
{task_name}-v{major}.{minor}
```

Examples:

- `claim-extraction-v0.1`
- `claim-classification-v0.1`
- `evidence-grading-v0.1`
- `verification-v0.1`
- `score-rationale-v0.1`
- `report-generation-v0.1`

## 4. Contract 1 — Claim extraction

### 4.1 Input

- chunks with IDs,
- document metadata,
- source page/section,
- taxonomy summary.

### 4.2 Output

Array of `GreenClaim` draft objects.

### 4.3 Required instruction

```text
Extract only sustainability, environmental, climate, ESG, green finance, legal/taxonomy, assurance, or CSR-environmental claims.
Preserve the exact source wording in claim_text.
Do not create a claim if the text is purely factual and not a sustainability representation.
Use only the provided enum values.
```

### 4.4 Failure handling

If no claim exists, return:

```json
{"claims": []}
```

## 5. Contract 2 — Claim classification

### 5.1 Input

- extracted claim,
- source context,
- taxonomy,
- materiality map.

### 5.2 Output

Classification fields:

- `claim_category`,
- `secondary_categories`,
- `pattern_candidates`,
- `is_quantifiable`,
- `required_evidence_types`,
- `materiality`,
- confidence.

### 5.3 Guardrail

Pattern candidates are hypotheses for checking. Do not present them as confirmed greenwashing.

## 6. Contract 3 — Retrieval query planning

### 6.1 Input

- classified claim,
- company name,
- reporting year,
- evidence requirements,
- available source inventory.

### 6.2 Output

`RetrievalPlan` object.

### 6.3 Required instruction

For each material claim, generate both supporting and contradiction queries. For quantitative claims, include structured metric lookup suggestions.

## 7. Contract 4 — Evidence grading

### 7.1 Input

- claim,
- candidate evidence,
- evidence standard,
- evidence requirements.

### 7.2 Output

Evidence role and strength for each candidate.

### 7.3 Required instruction

```text
Do not mark evidence as SUPPORTING unless it directly addresses the claim.
If source period, scope, company, or metric does not match, mark EXCLUDED or CONTEXTUAL and explain why.
```

## 8. Contract 5 — Verification

### 8.1 Input

- claim,
- evidence package,
- missing evidence,
- five-layer verification policy.

### 8.2 Output

`VerificationResult`.

### 8.3 Required instruction

```text
Apply all five verification layers.
Use one of the standard verdict enums.
A CONTRADICTED verdict requires at least one contradicting evidence ID.
If evidence is not enough, use INSUFFICIENT_EVIDENCE rather than guessing.
```

## 9. Contract 6 — Risk scoring explanation

### 9.1 Input

- claim,
- verification result,
- evidence package,
- scoring rubric.

### 9.2 Output

Criterion rationale draft only. Numeric score should be computed by deterministic code where possible.

### 9.3 Rule

LLM may suggest rationale, but the application should calculate totals from structured criterion values.

## 10. Contract 7 — Evidence card explanation

### 10.1 Input

- claim,
- verdict,
- evidence,
- score,
- review status.

### 10.2 Output

Plain-language explanation for UI.

### 10.3 Required wording constraints

Use:

- “risk indicator”,
- “available evidence suggests”,
- “not enough evidence was found”,
- “contradicts the claim”.

Avoid:

- “fraud”,
- “illegal” unless directly quoting a legal source,
- “proves the company lied”,
- unsupported legal conclusions.

## 11. Contract 8 — Report generation

### 11.1 Input

- dashboard,
- claim table,
- evidence cards,
- working papers,
- limitation notes.

### 11.2 Output

Report sections:

1. executive summary,
2. scope and methodology,
3. company profile,
4. claim overview,
5. high-risk findings,
6. evidence analysis,
7. green finance/taxonomy checks,
8. limitations,
9. recommendations,
10. appendix with citations.

### 11.3 Report guardrail

Report generator must not omit limitations or missing evidence.

## 12. Structured output validation

All model outputs must be validated before storage.

If validation fails:

1. retry with validation error context,
2. if retry fails, mark task failed,
3. route to human/manual processing if material.

## 13. Prompt test set

Maintain prompt tests for:

- vague claim extraction,
- quantitative emissions claim,
- green bond use-of-proceeds claim,
- net-zero target claim,
- legal compliance claim,
- contradictory evidence package,
- insufficient evidence case,
- duplicate claim grouping.

## 14. Acceptance criteria

- All prompts reference versioned schemas.
- All prompt outputs validate before use.
- No prompt can create final verdict without evidence IDs.
- Prompt-generated explanations remain audit-safe.
