# VERIFICATION_POLICY.md

Version: 0.1  
Status: Draft verification policy  
Owner: Domain Audit Lead / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines how the system converts a claim-evidence package into a verification result and recommended verdict.

Verification is not generic question answering. It is audit-style reasoning over a specific claim and source-linked evidence.

## 2. Verification principle

```text
Do not decide whether a company is “good” or “bad”.
Decide whether a specific claim is supported by available evidence.
```

## 3. Inputs

- `GreenClaim`,
- `EvidencePackage`,
- selected evidence items,
- missing evidence list,
- evidence strength levels,
- scoring rubric,
- taxonomy/legal rule outputs where available.

## 4. Outputs

- `VerificationResult`,
- recommended verdict,
- five-layer statuses,
- cited evidence IDs,
- rationale,
- confidence,
- review triggers.

## 5. Five verification layers

### Layer 1 — Specificity check

Question: Is the claim specific enough to verify?

Check:

- metric,
- value,
- baseline,
- time period,
- scope/boundary,
- project/product/company boundary,
- methodology.

Status guidance:

| Status | Condition |
|---|---|
| PASS | claim has enough specificity to verify |
| PARTIAL | claim has some specifics but missing important qualifiers |
| FAIL | claim is vague or marketing-like |
| NOT_APPLICABLE | rare, only for non-claim contextual statements |
| UNKNOWN | source text unclear |

### Layer 2 — Evidence availability check

Question: Is there relevant evidence that directly addresses the claim?

Check:

- supporting evidence exists,
- evidence matches same company/entity,
- evidence matches same period,
- evidence matches same scope,
- source strength is adequate,
- missing required evidence is listed.

### Layer 3 — Quantitative consistency check

Question: Do numbers support or contradict the claim?

Applies to:

- emissions,
- energy,
- water,
- waste,
- CAPEX/OPEX,
- proceeds allocation,
- reduction/increase claims,
- net-zero milestones.

Check:

- current vs baseline,
- unit consistency,
- boundary consistency,
- restatements,
- denominator effects,
- production/intensity vs absolute metric.

### Layer 4 — Legal/taxonomy alignment check

Question: Does the claim align with relevant legal or taxonomy criteria?

Applies to:

- green project claims,
- green bond/loan claims,
- compliance claims,
- permit claims,
- taxonomy alignment claims.

Status cannot be `PASS` unless the relevant rule or source is available.

### Layer 5 — External contradiction check

Question: Is there credible external or independent evidence that materially contradicts the claim?

Check:

- regulatory violation,
- fines/sanctions,
- credible news,
- audit qualifications,
- NGO/report findings,
- inconsistent public disclosures.

Absence of external contradiction is not the same as support. Use careful wording: “no material contradiction found in searched sources”.

## 6. Verdict decision rules

### 6.1 SUPPORTED

Use only when:

- claim is sufficiently specific,
- direct evidence exists,
- evidence matches scope/time/company,
- no material contradiction is found,
- missing evidence is not material to the claim.

### 6.2 PARTIALLY_SUPPORTED

Use when:

- evidence supports part of the claim,
- some important qualifier is missing,
- claim is directionally supported but incomplete,
- evidence strength is adequate but not ideal.

Example: emission reduction claim has current/baseline data but lacks assurance statement.

### 6.3 UNSUPPORTED

Use when:

- claim exists,
- required evidence is missing,
- no direct support is found,
- there is no strong contradicting evidence.

### 6.4 CONTRADICTED

Use only when:

- source-linked evidence conflicts with the claim,
- contradiction is material,
- evidence relates to the same claim scope/time/company,
- contradiction evidence is cited.

A `CONTRADICTED` verdict must cite at least one `CONTRADICTING` evidence item.

### 6.5 INSUFFICIENT_EVIDENCE

Use when:

- documents or sources are too incomplete to judge,
- OCR/table quality prevents reliable comparison,
- required evidence is unavailable,
- claim cannot be interpreted reliably.

Use this instead of forcing a conclusion.

## 7. Conflict resolution rules

| Situation | Recommended handling |
|---|---|
| Strong support and strong contradiction | keep both, likely `PARTIALLY_SUPPORTED` or `CONTRADICTED`, trigger review |
| Company disclosure conflicts with official violation record | official record has higher evidence strength |
| Unaudited ESG data conflicts with audited/assured data | stronger source wins, document conflict |
| Absolute emissions increase but intensity decreases | verdict depends on exact claim wording |
| Claim omits Scope 3 | mark partial/unsupported if Scope 3 is material to claim boundary |

## 8. Verification confidence

Confidence is not the same as risk score.

Suggested confidence inputs:

- evidence strength,
- evidence directness,
- number of missing requirements,
- source quality,
- extraction quality,
- contradiction clarity,
- reviewer history.

Default confidence bands:

| Confidence | Meaning |
|---:|---|
| 0.80–1.00 | strong basis for recommended verdict |
| 0.60–0.79 | usable but should be reviewed for material claims |
| 0.40–0.59 | uncertain; review recommended |
| 0.00–0.39 | insufficient basis; do not auto-finalize |

## 9. Rationale requirements

Every verification rationale must include:

- exact claim summary,
- verdict,
- key supporting evidence IDs,
- key contradicting evidence IDs if any,
- missing evidence if material,
- limitation statement.

Example:

```text
The claim states that Scope 1 and 2 emissions decreased in 2024. Evidence EVID-0001 and EVID-0002 show that Scope 1+2 emissions increased from 120,000 tCO2e in 2023 to 145,000 tCO2e in 2024. Therefore the recommended verdict is CONTRADICTED. This conclusion is limited to the documents and sources reviewed in this case.
```

## 10. Guardrails for AI-generated verification

The verifier must not:

- assert legal fraud,
- infer missing numbers,
- ignore missing evidence,
- cite uncited evidence,
- cite excluded evidence as support,
- change verdict enum labels,
- output a score without a verification result,
- use broad moral judgments about the company.

## 11. Human review triggers

Default triggers:

- `CONTRADICTED`,
- `risk_score >= 70`,
- high materiality and `INSUFFICIENT_EVIDENCE`,
- low verification confidence,
- low evidence strength,
- legal/taxonomy conflict,
- green finance/use-of-proceeds issue,
- external contradiction found,
- table/OCR confidence low.

## 12. Acceptance criteria

- Every verification result has five layer statuses.
- Every rationale cites evidence IDs.
- Contradictions require source-linked contradicting evidence.
- Missing evidence is explicitly represented.
- High-risk or uncertain results route to human review.
