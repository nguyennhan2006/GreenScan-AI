# USER_STORIES.md

Version: 0.1  
Status: Draft for MVP backlog  
Owner: Product Owner  
Last updated: 2026-07-07

## 1. Purpose

This document converts personas and audit requirements into user stories that Claude Code and the development team can implement. Stories are written to preserve the evidence-first workflow:

```text
Input → Processing → Claim → Evidence → Verification → Score → Output → Human review
```

Each story includes acceptance criteria and notes. Domain logic must remain aligned with `AUDIT_PROTOCOL.md`, `GREENWASHING_TAXONOMY.md`, `MANUAL_SCORING_RUBRIC.md`, and `EVIDENCE_STANDARD.md`.

## 2. Epic overview

| Epic ID | Epic | MVP priority |
|---|---|---:|
| E-01 | Document intake and processing | P0 |
| E-02 | Claim extraction and taxonomy | P0 |
| E-03 | Evidence retrieval and evidence standard | P0 |
| E-04 | Verification and scoring | P0 |
| E-05 | Evidence card and dashboard | P0 |
| E-06 | Human review and audit trail | P1 |
| E-07 | Report/export | P1 |
| E-08 | Evaluation and QA | P1 |
| E-09 | Admin/configuration | P2 |

Priority definitions:

- `P0`: required for credible MVP demo.
- `P1`: required for useful reviewer workflow.
- `P2`: useful after core loop is stable.

## 3. E-01 — Document intake and processing

### US-01.01 — Upload source documents

As an analyst, I want to upload company documents so that the system can extract claims and evidence from them.

Acceptance criteria:

- User can upload at least PDF, text, markdown, and JSON mock files.
- Each uploaded file creates a `Document` record with file name, source type, company, year, upload time, and checksum if available.
- Unsupported formats return a clear error.
- The original file reference is preserved for audit trail.

Notes:

- MVP may use local storage or mock file storage.
- Do not build full public web crawling in MVP.

### US-01.02 — Parse documents into traceable chunks

As a reviewer, I want documents to be split into traceable chunks so that every claim and evidence item can point back to a source page or section.

Acceptance criteria:

- System outputs `DocumentChunk` objects.
- Each chunk has `document_id`, `page_start`, `page_end`, `section`, `text`, and `extraction_method`.
- Chunks preserve enough context to support evidence retrieval.
- If page number is unknown, the system marks it as `page_unknown = true`.

### US-01.03 — Extract tables and metrics when possible

As a greenwashing reviewer, I want ESG and financial tables to be extracted into structured metrics so that quantitative claims can be checked.

Acceptance criteria:

- System can represent table-derived metrics as `ExtractedMetric` records.
- Each metric includes name, value, unit, year/period, scope if available, source page, and confidence.
- Missing unit or missing period is explicitly flagged.
- The system does not silently convert ambiguous metrics.

### US-01.04 — Run data quality and provenance checks

As a product owner, I want a quality gate for extracted data so that weak OCR/table extraction is not treated as strong evidence.

Acceptance criteria:

- Each document/chunk/metric has a quality status: `OK`, `LOW_CONFIDENCE`, `FAILED`, or `NEEDS_REVIEW`.
- The system flags missing page references, missing years, missing units, and low extraction confidence.
- Evidence from low-confidence extraction cannot be treated as high-strength evidence without reviewer review.

## 4. E-02 — Claim extraction and taxonomy

### US-02.01 — Extract green claims

As an ESG reviewer, I want the system to extract sustainability-related claims so that I can inspect them individually.

Acceptance criteria:

- System produces `GreenClaim` objects.
- Each claim includes exact claim text, source document, page/section, company, reporting year, and confidence.
- The system does not paraphrase claim text as the source of truth.
- Extracted claims include environmental, climate, green finance, legal compliance, net-zero, CSR, and vague ESG claims.

### US-02.02 — Classify claim category

As a reviewer, I want each claim classified by taxonomy so that the correct evidence requirements and scoring rules are applied.

Acceptance criteria:

- Each claim has at least one `claim_category`.
- Category values must come from `GREENWASHING_TAXONOMY.md`.
- Multiple categories are allowed.
- Unknown category is allowed only as `OTHER_REQUIRES_REVIEW`.

### US-02.03 — Detect greenwashing pattern candidates

As an analyst, I want the system to flag potential greenwashing patterns so that I can prioritize review.

Acceptance criteria:

- System assigns zero or more pattern candidates: vague claim, no evidence, selective disclosure, quantitative contradiction, legal contradiction, financial greenwashing, empty future commitment, scope shifting, baseline manipulation, offset overreliance, label confusion.
- Pattern candidates are not final verdicts.
- Final verdict is assigned only after evidence verification.

### US-02.04 — Normalize and deduplicate claims

As a reviewer, I want repeated or equivalent claims grouped so that the dashboard is not distorted by duplicates.

Acceptance criteria:

- Similar claims can be grouped into a `claim_group_id`.
- The system preserves each original claim instance.
- Grouping cannot remove the source citation for any instance.
- Claim-level score can be calculated per instance and summarized per group.

### US-02.05 — Assign materiality level

As a reviewer, I want materiality assigned so that core environmental claims are prioritized over peripheral CSR claims.

Acceptance criteria:

- Each claim receives a materiality level: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- Materiality considers sector, claim type, financial relevance, legal relevance, and stakeholder impact.
- Reviewer can override materiality.

## 5. E-03 — Evidence retrieval and evidence standard

### US-03.01 — Generate evidence requirements

As a reviewer, I want the system to define what evidence is needed for each claim so that verification is consistent.

Acceptance criteria:

- For each claim, system outputs required evidence fields.
- Quantitative reduction claims require baseline, current value, unit, scope, period, method, and source.
- Green finance claims require use-of-proceeds, project list, allocation/tracking, eligibility criteria, reporting, and external review when available.
- Net-zero/transition claims require target year, baseline, interim target, scope coverage, transition plan, and progress metric.

### US-03.02 — Retrieve supporting evidence

As an analyst, I want the system to retrieve evidence that may support the claim so that I can review it quickly.

Acceptance criteria:

- Retrieval returns `EvidenceItem` objects with source, page/section, text/table reference, relevance score, and extraction confidence.
- Evidence items must be traceable to source documents.
- Results include both text and structured metrics when available.
- Retrieval method is recorded: keyword, vector, structured query, manual, or external.

### US-03.03 — Retrieve contradicting evidence

As a reviewer, I want the system to search for evidence that contradicts the claim so that the review is not confirmation-biased.

Acceptance criteria:

- System runs negative evidence search for high-materiality claims.
- Negative evidence sources include metrics, legal/enforcement records, external news, audit notes, and internal contradictions.
- Contradicting evidence is separated from supporting evidence in the evidence card.
- If no contradiction search was run, the system must mark `negative_search_status = NOT_RUN`.

### US-03.04 — Grade evidence strength

As an auditor, I want evidence strength graded so that weak marketing text is not treated like audited or legal evidence.

Acceptance criteria:

- Each evidence item has evidence strength level `L1`–`L5` from `EVIDENCE_STANDARD.md`.
- L1 includes legal/regulatory/external assurance or audited evidence.
- L5 includes marketing slogans or unsubstantiated webpage text.
- Verdict logic must consider evidence strength, not only retrieval relevance.

### US-03.05 — Exclude weak or irrelevant evidence

As a reviewer, I want irrelevant or weak evidence to be excluded with reasons so that the audit trail remains transparent.

Acceptance criteria:

- Evidence can be marked `USED`, `EXCLUDED`, or `NEEDS_REVIEW`.
- Excluded evidence must include a reason: wrong period, wrong scope, irrelevant, duplicate, weak source, low extraction confidence, or contradiction unresolved.
- Excluded evidence remains visible in working paper, but not counted as supporting evidence.

## 6. E-04 — Verification and scoring

### US-04.01 — Verify claim across five layers

As an ESG reviewer, I want each claim verified through five checks so that verdicts are consistent.

Acceptance criteria:

- System records the result of each layer:
  1. specificity check,
  2. evidence availability check,
  3. quantitative consistency check,
  4. legal/taxonomy alignment check,
  5. external contradiction check.
- Each layer has status: `PASS`, `PARTIAL`, `FAIL`, `NOT_APPLICABLE`, or `NEEDS_REVIEW`.
- Layer results are visible in evidence card.

### US-04.02 — Assign verification verdict

As a reviewer, I want the system to assign a standardized verdict so that all outputs use the same conclusion language.

Acceptance criteria:

- Verdict enum must be one of:
  - `SUPPORTED`
  - `PARTIALLY_SUPPORTED`
  - `UNSUPPORTED`
  - `CONTRADICTED`
  - `INSUFFICIENT_EVIDENCE`
- Verdict must be justified by evidence and layer results.
- `SUPPORTED` is not allowed if there is unresolved direct contradiction.
- `CONTRADICTED` requires at least one direct contradicting evidence item.

### US-04.03 — Score claim-level risk

As an analyst, I want each claim scored from 0 to 100 so that I can prioritize high-risk claims.

Acceptance criteria:

- Score uses the seven criteria from `MANUAL_SCORING_RUBRIC.md`.
- Each criterion stores numeric points and a short rationale.
- Total score is capped at 100.
- Score label is derived from the numeric score.

### US-04.04 — Aggregate company-level risk

As an analyst, I want a company-level risk score so that I can compare the overall risk profile.

Acceptance criteria:

- Company-level score considers high-risk claims, contradicted claims, materiality, financial greenwashing, legal/taxonomy issues, and evidence gaps.
- Aggregation method is documented and visible.
- Score must not be a hidden black-box value.
- MVP may use rule-based aggregation.

### US-04.05 — Trigger human review

As a product owner, I want high-risk or uncertain cases to enter human review so that AI does not finalize sensitive conclusions alone.

Acceptance criteria:

- Human review is triggered when risk score exceeds threshold, verdict is `CONTRADICTED`, evidence confidence is low, claim is material and unsupported, or scoring has unresolved conflict.
- Reviewer can accept, revise, or reject AI verdict.
- Reviewer action is logged.

## 7. E-05 — Evidence card and dashboard

### US-05.01 — Show evidence card for each claim

As a reviewer, I want a claim-level evidence card so that I can understand the conclusion without searching manually.

Acceptance criteria:

- Evidence card includes claim text, category, source, verdict, score, explanation, supporting evidence, contradicting evidence, missing evidence, and reviewer status.
- Every evidence item has a source and page/section when available.
- Evidence card separates AI-generated explanation from source text.
- Evidence card displays uncertainty and missing data.

### US-05.02 — Show claim table

As an analyst, I want a table of all claims so that I can filter and prioritize.

Acceptance criteria:

- Table supports filtering by verdict, score range, category, materiality, source document, and reviewer status.
- Table shows claim ID, short text, category, verdict, risk score, and top evidence count.
- Clicking a row opens evidence card.

### US-05.03 — Show company dashboard

As a user, I want a dashboard summary so that I can understand the company’s risk profile quickly.

Acceptance criteria:

- Dashboard shows company risk score, risk label, number of claims, verdict distribution, top categories, and top high-risk claims.
- Dashboard includes disclaimer: risk assessment, not legal conclusion.
- Dashboard links to evidence cards and report export.

### US-05.04 — Show method and scoring transparency

As an evaluator, I want to see the scoring method so that I can trust the output.

Acceptance criteria:

- Dashboard or evidence card links to rubric summary.
- Each claim score shows criterion-level points.
- Company score shows aggregation method.

## 8. E-06 — Human review and audit trail

### US-06.01 — Review queue

As a reviewer, I want a queue of high-risk or uncertain claims so that I know what to inspect first.

Acceptance criteria:

- Queue includes claims triggered by risk threshold, contradiction, low evidence confidence, missing required evidence, or manual flag.
- Queue can be filtered by company, category, materiality, verdict, and assigned reviewer.
- Claim opens evidence card and working paper.

### US-06.02 — Reviewer action

As a reviewer, I want to accept, revise, or reject AI output so that final decisions are accountable.

Acceptance criteria:

- Reviewer can set final verdict, final score, comment, and sign-off status.
- System records reviewer name, timestamp, and changes.
- AI-generated output remains visible as original suggestion.

### US-06.03 — Audit log

As an evaluator, I want all changes recorded so that the assessment is reproducible.

Acceptance criteria:

- Audit log records document upload, claim extraction, evidence retrieval, scoring, reviewer action, and export events.
- Log entries include timestamp, actor, action, and affected object ID.
- Audit log is exportable for review.

## 9. E-07 — Report/export

### US-07.01 — Export company report

As an analyst, I want to export a report so that I can share results with stakeholders.

Acceptance criteria:

- Report includes executive summary, company profile, methodology, claim summary, top risks, evidence analysis, taxonomy/financial review, limitations, recommendations, and appendix.
- Report includes citations/page references for evidence used.
- Report states that the output is a greenwashing risk assessment, not legal finding.

### US-07.02 — Export claim-level working paper

As a reviewer, I want to export working papers so that manual audit reasoning is preserved.

Acceptance criteria:

- Working paper follows `CLAIM_VERIFICATION_WORKING_PAPER.md`.
- Includes claim text, evidence used/excluded, five-layer checks, scoring, verdict, missing evidence, and reviewer sign-off.
- Export can be Markdown or JSON for MVP.

### US-07.03 — Export structured data

As a product owner, I want structured exports so that outputs can be tested and reused.

Acceptance criteria:

- System can export claims, evidence, verification results, scores, and review actions as JSON.
- JSON uses stable field names and enums.
- Export includes version metadata.

## 10. E-08 — Evaluation and QA

### US-08.01 — Run demo case tests

As a product owner, I want sample cases with expected outputs so that system behavior can be verified.

Acceptance criteria:

- Each demo case includes source text, expected claim extraction, expected evidence, expected verdict, and expected score range.
- Test cases include supported, partially supported, unsupported, contradicted, and insufficient evidence examples.

### US-08.02 — Measure citation accuracy

As a reviewer, I want citation accuracy checked so that evidence cards do not mislead users.

Acceptance criteria:

- Each evidence item citation is checked against source document ID and page/section.
- Broken or missing citations are flagged.
- Claims without traceable citations cannot be finalized as supported.

### US-08.03 — Measure reviewer agreement

As a research lead, I want reviewer agreement tracked so that the rubric can be improved.

Acceptance criteria:

- The system can record two reviewer decisions for the same claim.
- Disagreement is flagged for discussion.
- Agreement results inform updates to rubric or taxonomy.

## 11. E-09 — Admin/configuration

### US-09.01 — Configure scoring thresholds

As a product owner, I want configurable score thresholds so that risk labels can be adjusted during calibration.

Acceptance criteria:

- Default thresholds are documented.
- Changes are versioned.
- Historical scores preserve the scoring version used.

### US-09.02 — Configure taxonomy and evidence rules

As a research lead, I want taxonomy and evidence rules to be editable by version so that the system can evolve.

Acceptance criteria:

- Taxonomy version is stored with each claim.
- Evidence standard version is stored with each verification result.
- Rule changes require changelog entry.

## 12. MVP story set

The minimum credible MVP should implement:

```text
US-01.01 Upload source documents
US-01.02 Parse documents into traceable chunks
US-01.03 Extract tables and metrics when possible, even if mocked
US-02.01 Extract green claims
US-02.02 Classify claim category
US-03.01 Generate evidence requirements
US-03.02 Retrieve supporting evidence
US-03.03 Retrieve contradicting evidence
US-03.04 Grade evidence strength
US-04.01 Verify claim across five layers
US-04.02 Assign verification verdict
US-04.03 Score claim-level risk
US-05.01 Show evidence card
US-05.02 Show claim table
US-05.03 Show company dashboard
US-06.02 Reviewer action, at least accept/reject/comment
US-07.02 Export claim-level working paper
US-08.01 Run demo case tests
```

## 13. Definition of Ready

A user story is ready for Claude Code when it has:

- clear input and output,
- schema references,
- acceptance criteria,
- domain rule references,
- test expectation,
- explicit out-of-scope items.

## 14. Definition of Done

A story is done when:

- implementation matches documented schema,
- tests or demo cases pass,
- output is traceable to source where applicable,
- no new verdict/scoring enum is invented,
- implementation notes are added to the implementation log,
- open questions are documented instead of guessed.
