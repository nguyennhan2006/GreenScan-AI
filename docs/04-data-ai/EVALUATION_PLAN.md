# EVALUATION_PLAN.md

Version: 0.1  
Status: Draft evaluation plan  
Owner: Reviewer / Product Owner / AI Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines how to evaluate the Greenwashing Detection MVP.

The goal is not to prove that the AI is always right. The goal is to measure whether the system helps reviewers find, verify, and document greenwashing risk more consistently and traceably.

## 2. Evaluation dimensions

| Dimension | Question |
|---|---|
| Claim extraction | Did the system find the relevant green claims? |
| Claim classification | Did it classify claims and patterns correctly? |
| Evidence retrieval | Did it retrieve useful support and contradiction evidence? |
| Evidence grading | Did it judge evidence strength and role correctly? |
| Verification | Did it assign the right verdict? |
| Risk scoring | Is the score consistent with the rubric? |
| Explanation | Is the rationale clear, cited, and audit-safe? |
| Human review | Does the workflow help reviewers decide faster? |
| Traceability | Can every output be traced back to source? |

## 3. Gold dataset

### 3.1 MVP gold set

Start with 20–50 claim-level cases manually labeled by the team.

Each gold case should include:

- source document excerpt,
- extracted claim,
- category,
- evidence requirements,
- supporting evidence,
- contradicting evidence,
- missing evidence,
- expected verdict,
- expected risk band,
- reviewer explanation.

### 3.2 Case mix

Include at least:

| Case type | Minimum examples |
|---|---:|
| Vague sustainability claim | 5 |
| Emissions reduction claim | 5 |
| Renewable energy claim | 3 |
| Waste/water claim | 3 |
| Green bond/use-of-proceeds claim | 5 |
| Net-zero/transition claim | 5 |
| Legal compliance claim | 3 |
| Contradicted claim | 5 |
| Insufficient evidence case | 5 |

## 4. Metrics

### 4.1 Claim extraction metrics

| Metric | Definition |
|---|---|
| Claim precision | extracted claims that are valid green claims / all extracted claims |
| Claim recall | gold claims found / all gold claims |
| Source accuracy | extracted claims with correct page/chunk / all extracted claims |
| Exact text preservation | exact claim text preserved / all extracted claims |

### 4.2 Classification metrics

| Metric | Definition |
|---|---|
| Category accuracy | correct primary category / claims |
| Pattern candidate usefulness | reviewer accepts candidate pattern / candidates |
| Quantifiability accuracy | correct quantifiable flag / claims |
| Evidence requirement accuracy | required evidence list accepted / claims |

### 4.3 Retrieval metrics

| Metric | Definition |
|---|---|
| Evidence recall@k | gold evidence found in top-k retrieved items |
| Evidence precision@k | useful evidence in top-k / k |
| Contradiction hit rate | contradiction evidence found when gold has contradiction |
| Missing evidence accuracy | missing evidence correctly identified |
| Citation accuracy | cited evidence points to correct source/page |

### 4.4 Verification metrics

| Metric | Definition |
|---|---|
| Verdict accuracy | recommended verdict matches gold verdict |
| Layer status accuracy | five-layer statuses match reviewer label |
| Contradiction safety | contradicted verdicts that cite valid contradiction evidence |
| Insufficient evidence safety | uncertain cases not forced into supported/contradicted |

### 4.5 Scoring metrics

| Metric | Definition |
|---|---|
| Risk band accuracy | predicted risk label matches gold band |
| Score deviation | absolute difference from reviewer score |
| Rubric consistency | criterion scores align with rationale |
| Review trigger recall | high-risk cases correctly routed to review |

### 4.6 Explanation metrics

| Metric | Definition |
|---|---|
| Citation completeness | key claims in explanation cite evidence IDs |
| Audit clarity | reviewer can understand rationale |
| Unsafe wording rate | explanations using legal overclaim or unsupported accusation |
| Missing evidence disclosure | explanation includes material missing evidence |

## 5. Reviewer evaluation workflow

1. Select test case.
2. Run pipeline.
3. Reviewer inspects claim table and evidence card.
4. Reviewer labels:
   - accepted/revised/rejected,
   - correct verdict,
   - correct score band,
   - missing evidence,
   - explanation quality.
5. Store reviewer decisions as evaluation records.
6. Convert accepted corrections into future gold cases.

## 6. Acceptance targets for MVP

Initial MVP does not need high automation accuracy across all tasks. It must be reliable enough for demo and reviewer-assisted workflow.

Suggested minimum targets:

| Metric | MVP target |
|---|---:|
| Source accuracy for claims | ≥ 95% |
| Exact text preservation | ≥ 95% |
| Claim precision | ≥ 80% |
| Evidence citation accuracy | ≥ 90% |
| Contradicted verdict safety | 100% must cite contradiction evidence |
| JSON schema validity | 100% |
| High-risk review trigger recall | ≥ 90% |
| Unsafe wording rate | 0% in final report |

## 7. Regression tests

Create regression tests for:

- enum stability,
- schema validation,
- evidence-before-verdict invariant,
- contradicted verdict requiring evidence,
- score total calculation,
- output export structure,
- reviewer revision versioning.

## 8. RAG-specific evaluation

If vector/hybrid retrieval is enabled, evaluate:

- context precision,
- context recall,
- evidence faithfulness,
- answer/verdict faithfulness,
- harmful context inclusion,
- lost-in-context behavior for long evidence packages.

Use automated RAG metrics as helper signals, not final audit truth. Human-labeled evidence remains the gold standard.

## 9. Error taxonomy

Track errors using this taxonomy:

| Code | Error |
|---|---|
| EXTRACT_FALSE_POSITIVE | extracted non-green claim |
| EXTRACT_FALSE_NEGATIVE | missed green claim |
| WRONG_CATEGORY | incorrect taxonomy category |
| WRONG_PATTERN | bad pattern candidate |
| EVIDENCE_MISSED | did not retrieve important evidence |
| EVIDENCE_WRONG_SCOPE | evidence from wrong scope/entity/year |
| EVIDENCE_OVERWEIGHTED | weak evidence treated as strong |
| VERDICT_OVERCONFIDENT | conclusion stronger than evidence allows |
| VERDICT_UNSAFE_CONTRADICTION | contradicted without valid contradiction evidence |
| SCORE_INCONSISTENT | score conflicts with rubric/verdict |
| EXPLANATION_UNCITED | explanation lacks evidence IDs |
| REPORT_UNSAFE_LANGUAGE | legal/accusatory overclaim |

## 10. Evaluation artifacts

Store:

- gold cases,
- pipeline outputs,
- reviewer labels,
- metric reports,
- error logs,
- regression test snapshots.

Recommended path:

```text
/evals
  /gold-cases
  /pipeline-runs
  /reviewer-labels
  /reports
```

## 11. Go/no-go checklist before demo

- [ ] JSON outputs validate.
- [ ] Claim source links work.
- [ ] Evidence cards show selected and missing evidence.
- [ ] No contradicted verdict lacks contradiction evidence.
- [ ] Scores sum correctly.
- [ ] High-risk claims are routed to review.
- [ ] Report includes limitations.
- [ ] Demo fixture can be rerun deterministically.

## 12. Long-term evaluation roadmap

1. Build manually labeled Vietnamese ESG/finance claim dataset.
2. Add multi-reviewer agreement tracking.
3. Add industry-specific materiality benchmarks.
4. Add legal/taxonomy rule test cases.
5. Add retrieval ablation tests: BM25 vs vector vs hybrid.
6. Add prompt regression suite.
7. Add reviewer productivity metrics.
