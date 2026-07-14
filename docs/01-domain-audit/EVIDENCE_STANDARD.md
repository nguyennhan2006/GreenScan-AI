# EVIDENCE_STANDARD.md

Version: 0.1  
Status: Draft evidence hierarchy  
Owner: Reviewer / Research Lead  
Last updated: 2026-07-07

## 1. Purpose

This document defines what counts as evidence when assessing greenwashing risk. It provides a hierarchy for evidence reliability, rules for evidence acceptance, and minimum standards for claim support.

The system must not treat every retrieved text chunk as equal. A verified emissions table, a regulatory decision, and a marketing slogan have different evidentiary value.

## 2. Evidence-first rule

A claim can only be concluded as `SUPPORTED` if evidence is:

1. Relevant to the claim.
2. Traceable to a source.
3. Within the same reporting period or clearly comparable.
4. Within the same organizational/project/product boundary.
5. Sufficiently reliable for the type of claim.

## 3. Evidence object schema

Each evidence item should be captured as:

```json
{
  "evidence_id": "E-0001",
  "claim_id": "C-0001",
  "source_type": "ESG_REPORT",
  "source_name": "ABC Sustainability Report 2024",
  "source_url_or_path": "...",
  "page": 42,
  "section": "GHG emissions",
  "evidence_text": "...",
  "metric_name": "Scope 1+2 emissions",
  "metric_value": 145000,
  "unit": "tCO2e",
  "period": "2024",
  "evidence_strength": "L2",
  "supports_or_contradicts": "CONTRADICTS",
  "relevance_note": "Same company, same year, directly conflicts with reduction claim"
}
```

## 4. Evidence hierarchy

| Level | Evidence type | Reliability | Examples |
|---|---|---|---|
| L1 | Independent / official / legal evidence | Very high | Regulatory decision, permit, court record, official taxonomy confirmation, independent assurance report |
| L2 | Audited or formal company disclosure | High | Financial statements, annual report, ESG report with methodology, bond allocation report |
| L3 | Company-disclosed raw data without assurance | Medium | ESG tables, website KPI table, internal project list disclosed publicly |
| L4 | External secondary source | Medium to low | Reputable news, NGO report, analyst report, controversy database |
| L5 | Marketing and symbolic evidence | Low | Slogan, brochure, campaign page, nature imagery, unverified badges |

## 5. Acceptance rules by evidence level

### L1 — Independent / official / legal evidence

Use for high-confidence conclusions when source is authentic and relevant.

Typical sources:

- Environmental permits.
- Regulatory inspection or penalty decisions.
- Court decisions.
- Official green taxonomy confirmation.
- External assurance or verification statement.
- Accredited certification with scope and validity.

Rules:

- Check date and validity period.
- Check whether the source applies to the same company/project/site.
- Check whether the source is final or preliminary.

### L2 — Audited or formal company disclosure

Use as primary evidence for reported metrics and financial figures.

Typical sources:

- Audited financial statements.
- Annual reports.
- Sustainability reports with methodology.
- Green bond framework.
- Allocation and impact reports.

Rules:

- Prefer audited or assured sections over unaudited narrative.
- Check footnotes and methodology.
- Check whether the metric boundary matches the claim.

### L3 — Company-disclosed raw data without assurance

Use with caution.

Typical sources:

- ESG data tables.
- Project pages.
- KPI dashboards.
- Press releases with data.

Rules:

- Do not treat as independently verified.
- Can support low/medium-risk claims if internally consistent.
- For high-materiality claims, request stronger evidence or assurance.

### L4 — External secondary source

Use for contradiction search and context.

Typical sources:

- Reputable news.
- NGO reports.
- Research reports.
- Stock exchange disclosures.
- Analyst reports.

Rules:

- Check publication date.
- Prefer primary official evidence if available.
- Do not rely on one weak secondary source for a critical contradiction.

### L5 — Marketing and symbolic evidence

Use mostly to identify claims, not support them.

Typical sources:

- Website slogans.
- Advertisements.
- Brochures.
- Images and icons.
- Awards without methodology.

Rules:

- L5 cannot independently support a material claim.
- L5 can increase risk if it creates a misleading impression without substantiation.

## 6. Evidence quality dimensions

Every evidence item should be scored qualitatively across these dimensions:

| Dimension | Good evidence | Weak evidence |
|---|---|---|
| Relevance | Directly addresses claim | Indirect or loosely related |
| Reliability | Official, assured, audited, or independently verified | Marketing or unaudited statement |
| Timeliness | Same period or valid for claim period | Outdated or future-looking |
| Scope match | Same entity/site/project/product/scope | Boundary mismatch |
| Completeness | Includes metric, unit, baseline, method | Missing key elements |
| Traceability | Page/source/link available | No source or hard to verify |

## 7. Minimum evidence by verdict

| Verdict | Minimum evidence condition |
|---|---|
| SUPPORTED | Direct L1/L2 evidence, or strong L3 evidence for low-risk claims, no material contradiction found |
| PARTIALLY_SUPPORTED | Some relevant evidence exists but has limitations in scope, period, method, assurance, or completeness |
| UNSUPPORTED | Claim exists but adequate supporting evidence is missing |
| CONTRADICTED | Reliable evidence conflicts with the claim |
| INSUFFICIENT_EVIDENCE | Evidence base is incomplete, inaccessible, or too ambiguous to conclude |

## 8. Source-specific rules

### 8.1 ESG and sustainability reports

Use for:

- Claim extraction.
- ESG metrics.
- Targets.
- Narrative context.

Risks:

- Narrative sections may be promotional.
- Metrics may be unaudited.
- Boundary may change across years.

### 8.2 Financial statements

Use for:

- CAPEX.
- financing instruments.
- provisions, penalties, environmental liabilities.
- use-of-proceeds clues.

Risks:

- ESG-specific allocation may not be disaggregated.
- Environmental expenses may be embedded in broader accounts.

### 8.3 Green bond documents

Use for:

- Use-of-proceeds verification.
- project eligibility.
- proceeds management.
- reporting.
- external review.

Minimum documents:

- Bond framework.
- Eligible categories or project list.
- Allocation report.
- Impact report where available.
- External review or second-party opinion where claimed.

### 8.4 Regulatory and legal documents

Use for:

- compliance claims.
- permits.
- penalties.
- official classification.

Risks:

- Need exact entity match.
- Need check whether penalty relates to subsidiary/site/project.
- Need validity period.

### 8.5 News and external reports

Use for:

- negative evidence search.
- controversy detection.
- triangulation.

Rules:

- Use multiple sources when possible.
- Prefer official documents over news summaries.
- Mark as L4 unless backed by primary document.

## 9. Evidence conflict rules

When evidence conflicts:

1. Prefer higher-level evidence.
2. Prefer more recent evidence if periods overlap.
3. Prefer source with clearer scope.
4. Preserve both sides in the working paper.
5. If conflict cannot be resolved, use `INSUFFICIENT_EVIDENCE` or human review.

Example:

- Website says “zero violations”.
- Official regulator decision shows a fine in the same year.
- Verdict should normally be `CONTRADICTED`, with L1 evidence overriding L5/L3 narrative.

## 10. Negative evidence search standard

For material claims, reviewers must actively search for contradiction, not only support.

Search targets:

- environmental fine
- penalty
- pollution incident
- permit revoked
- community complaint
- lawsuit
- restatement
- audit qualification
- bond proceeds misuse
- taxonomy non-alignment

For Vietnam-focused cases, use Vietnamese keywords as well:

- xử phạt môi trường
- vi phạm môi trường
- giấy phép môi trường
- đánh giá tác động môi trường
- trái phiếu xanh
- tín dụng xanh
- công bố thông tin
- thanh tra môi trường

## 11. Evidence exclusion rules

Do not use evidence if:

- It cannot be traced to a source.
- It refers to a different company or unrelated subsidiary.
- It refers to a different period with no valid comparison.
- It is only a generated AI answer with no primary source.
- It is an image or slogan with no factual content, except as evidence of implied claim.
- It is a certification/award with no issuer, scope, date, or criteria.

## 12. Evidence pack requirement

For every high-risk claim, the reviewer should preserve an evidence pack:

1. Original claim source.
2. Supporting evidence.
3. Contradicting evidence.
4. Evidence grading notes.
5. Missing evidence list.
6. Final verdict rationale.

## 13. Implementation notes

- Retrieval should return candidate evidence with source type and page.
- Reranking should consider evidence strength, not semantic similarity alone.
- The system should support `supports_or_contradicts` labels.
- The evidence store should preserve rejected evidence, not only accepted evidence.
- Evidence cards should display source strength to reviewer.

## 14. Open issues

- Need official source registry for Vietnamese legal documents.
- Need method to score OCR/table extraction confidence.
- Need rule for treating social media posts and user-generated reports.
