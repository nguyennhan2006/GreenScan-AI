# MVP_SCOPE.md

> **Định vị sản phẩm đã được viết lại 2026-09-25** — xem [AUDITOR_WORKFLOW_POSITIONING.md](AUDITOR_WORKFLOW_POSITIONING.md). Người dùng là **kiểm toán viên đang làm thủ công**, không phải sáu persona; sản phẩm tự động hoá **đọc · định vị · ghi chép** và trả về một **hàng đợi đã xếp ưu tiên**, không phải một bảng verdict. Tài liệu này giữ lại phần mô tả nhu cầu và phạm vi còn dùng được.


Version: 0.1  
Status: Draft for build planning  
Owner: Product Owner  
Last updated: 2026-07-07

## 1. Purpose

This document defines the minimum viable product for the Greenwashing Detection system. The MVP must demonstrate the full evidence-first loop, even if some AI, OCR, retrieval, or external-data components are mocked.

The MVP is successful if a reviewer can go from uploaded company documents to claim-level evidence cards, verdicts, risk scores, and a working paper export.

## 2. MVP thesis

The MVP should prove this product thesis:

> A greenwashing risk system is useful only if it can connect each sustainability claim to supporting and contradicting evidence, explain the verdict, and preserve an audit trail for human review.

Therefore the MVP should prioritize traceability and reviewer confidence over broad automation.

## 3. MVP north-star workflow

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

## 4. In scope — Functional requirements

### 4.1 Document intake

In scope:

- Upload or load local sample documents.
- Support PDF/text/markdown/JSON mock input.
- Create document metadata.
- Preserve source reference and page/section when available.

MVP acceptable simplification:

- Use sample documents stored in repository.
- OCR can be mocked or marked as future work if source PDF text is extractable.

### 4.2 Document processing

In scope:

- Convert documents into chunks.
- Extract or mock tables/metrics.
- Preserve provenance.
- Run simple data quality flags: missing page, missing year, missing unit, low confidence.

MVP acceptable simplification:

- Manual or fixture-based extracted metrics are allowed for demo cases.

### 4.3 Claim extraction

In scope:

- Extract green claims from processed chunks.
- Preserve exact claim text.
- Include source document, page/section, company, year, confidence.
- Extract at least these claim types:
  - emissions reduction,
  - renewable energy,
  - waste/water/environmental performance,
  - green finance / green bond / green loan,
  - net-zero or climate target,
  - legal compliance,
  - vague ESG / sustainability statement,
  - CSR/environmental community claim.

MVP acceptable simplification:

- Rule-based extraction or LLM-mock extractor is acceptable.
- Demo fixtures can contain pre-annotated claims.

### 4.4 Claim classification

In scope:

- Apply taxonomy categories from `GREENWASHING_TAXONOMY.md`.
- Assign whether the claim is quantifiable.
- Assign potential greenwashing pattern candidates.
- Assign materiality level.

MVP acceptable simplification:

- Materiality can be rule-based by category and sector.

### 4.5 Evidence retrieval

In scope:

- Retrieve supporting evidence from internal document chunks and structured metrics.
- Retrieve contradicting evidence through negative evidence search.
- Record retrieval method.
- Rank or score evidence relevance.

MVP acceptable simplification:

- Use BM25-like keyword search, vector search, or a simple local search adapter.
- External evidence can be fixture-based rather than live crawling.

### 4.6 Evidence grading

In scope:

- Assign evidence strength level `L1`–`L5`.
- Separate supporting evidence, contradicting evidence, missing evidence, and excluded evidence.
- Store reason for exclusion.

MVP acceptable simplification:

- Evidence strength can be rule-based by source type.

### 4.7 Verification

In scope:

- Run five-layer verification:
  1. specificity,
  2. evidence availability,
  3. quantitative consistency,
  4. legal/taxonomy alignment,
  5. external contradiction.
- Assign standardized verdict:
  - `SUPPORTED`,
  - `PARTIALLY_SUPPORTED`,
  - `UNSUPPORTED`,
  - `CONTRADICTED`,
  - `INSUFFICIENT_EVIDENCE`.

MVP acceptable simplification:

- Legal/taxonomy checks can be limited to rule/fixture data.
- External contradiction can be run only on demo external sources.

### 4.8 Risk scoring

In scope:

- Claim-level score 0–100 using seven criteria from `MANUAL_SCORING_RUBRIC.md`.
- Criterion-level rationale.
- Risk label derived from score.
- Company-level summary score.

MVP acceptable simplification:

- Company-level aggregation can be a documented rule-based weighted formula.

### 4.9 Output UI

In scope:

- Company dashboard.
- Claim table.
- Evidence card.
- Reviewer action panel.
- Export button for working paper/report.

MVP acceptable simplification:

- UI can be a static frontend using mock API data as long as data contracts are stable.

### 4.10 Human review

In scope:

- Reviewer can accept, revise, reject, or comment on AI verdict.
- System records reviewer status.
- High-risk/uncertain cases are flagged.

MVP acceptable simplification:

- Authentication can be omitted or mocked.
- Single reviewer mode is acceptable.

### 4.11 Export

In scope:

- Export claim-level working paper as Markdown or JSON.
- Export company-level report as Markdown.
- Include source references and limitations.

MVP acceptable simplification:

- PDF export can be deferred if Markdown export is complete.

## 5. Out of scope for MVP

The following are explicitly out of scope:

- Legal conclusion that a company committed fraud or violated law.
- Full financial audit.
- Full environmental engineering verification.
- Full live web crawler for news and enforcement databases.
- Automatic retrieval of all financial reports from stock exchange sources.
- Full OCR system for complex scanned documents.
- Fine-tuned model training.
- Full multi-company benchmarking product.
- Real-time emissions monitoring.
- Production-grade access control and enterprise deployment.
- Automated regulatory filing.

## 6. MVP data scope

### 6.1 Required demo data

The MVP should include at least 5 demo cases:

| Case type | Required output |
|---|---|
| Supported claim | Claim has direct evidence and low risk score |
| Partially supported claim | Claim has evidence but misses baseline/scope/assurance |
| Unsupported claim | Claim has no sufficient evidence |
| Contradicted claim | Claim conflicts with metric/legal/external evidence |
| Insufficient evidence claim | Claim cannot be judged due to missing source data |

### 6.2 Required source types

At minimum, demo fixtures should represent:

- ESG/sustainability report excerpt.
- Annual report or financial statement excerpt.
- Structured environmental metric table.
- Green bond/green loan excerpt.
- External contradiction source such as enforcement/news/mock regulator note.
- Taxonomy/legal criteria excerpt.

## 7. MVP user flows

### Flow A — Analyst checks a company

```text
Open company dashboard
→ View total risk score and top risks
→ Filter high-risk claims
→ Open evidence card
→ Export report
```

### Flow B — Reviewer verifies a claim

```text
Open review queue
→ Select high-risk claim
→ Inspect evidence card
→ Check five-layer verification
→ Accept/revise/reject verdict
→ Add comment
→ Export working paper
```

### Flow C — Bank officer checks green finance claim

```text
Open green finance category
→ Inspect bond/loan claim
→ Check use-of-proceeds evidence
→ Check project/taxonomy evidence
→ Review missing allocation/reporting data
→ Flag for due diligence
```

### Flow D — Product owner validates demo

```text
Run demo cases
→ Compare expected verdicts and scores
→ Check citations
→ Review broken or missing evidence
→ Update open questions and backlog
```

## 8. MVP outputs

The MVP must output:

1. `CompanyDashboard`
2. `ClaimTable`
3. `EvidenceCard`
4. `VerificationResult`
5. `RiskScore`
6. `HumanReviewRecord`
7. `ClaimWorkingPaper`
8. `CompanyReport`
9. JSON export for test/evaluation

Detailed field requirements are defined in `OUTPUT_SPEC.md`.

## 9. MVP quality gates

### 9.1 Evidence gate

The system must not mark a claim as `SUPPORTED` unless:

- there is at least one used evidence item,
- evidence is traceable to source,
- evidence is relevant to the claim,
- evidence matches time period and scope where applicable,
- no direct contradiction remains unresolved.

### 9.2 Citation gate

Every evidence card must show:

- source document or source name,
- page/section or reason page is unavailable,
- evidence text or metric reference,
- retrieval/extraction method,
- evidence strength.

### 9.3 Scoring gate

Every risk score must show:

- score version,
- criterion-level points,
- criterion rationale,
- final numeric score,
- risk label.

### 9.4 Human review gate

The system must flag for human review if:

- risk score is high or critical,
- verdict is `CONTRADICTED`,
- claim is high-materiality and unsupported,
- evidence confidence is low,
- data quality is low,
- legal/taxonomy alignment is uncertain.

## 10. MVP success metrics

| Metric | MVP target |
|---|---:|
| Demo cases runnable end-to-end | 5+ cases |
| Evidence cards with source references | 100% of generated evidence cards |
| Verdict enum consistency | 100% |
| Score criterion traceability | 100% |
| Reviewer can override verdict | Yes |
| Report/working paper export | Markdown or JSON |
| Hallucinated evidence allowed | 0 |

## 11. Non-functional requirements

### 11.1 Traceability

All claims, evidence, verdicts, scores, and reviewer actions must keep IDs and source references.

### 11.2 Reproducibility

Demo outputs must be reproducible from fixture data.

### 11.3 Explainability

The system must distinguish:

- source text,
- AI interpretation,
- scoring rationale,
- reviewer comment.

### 11.4 Safety

The system must use careful language:

- Say “greenwashing risk” rather than “fraud”.
- Say “unsupported by available evidence” rather than “false” unless contradiction is explicit.
- Say “requires review” when evidence is incomplete.

### 11.5 Agent compatibility

Claude Code must be able to implement MVP modules by reading:

- `USER_STORIES.md`,
- `OUTPUT_SPEC.md`,
- `DATA_SCHEMA.md`,
- `PIPELINE_SPEC.md`,
- `TASK_BREAKDOWN.md`.

## 12. MVP release stages

### Stage 0 — Documentation baseline

- Project docs complete.
- Domain audit docs complete.
- Product docs complete.
- Architecture and data schema ready.

### Stage 1 — Demo fixtures and schemas

- Fixture documents.
- Claim/evidence/verification schemas.
- Expected outputs for demo cases.

### Stage 2 — Core pipeline

- Document processing adapter.
- Claim extractor.
- Evidence retriever.
- Verifier.
- Risk scorer.

### Stage 3 — UI outputs

- Dashboard.
- Claim table.
- Evidence card.
- Reviewer action.

### Stage 4 — Export and QA

- Working paper export.
- Company report export.
- Demo test suite.
- Review checklist pass.

## 13. MVP risks and mitigations

| Risk | Mitigation |
|---|---|
| Demo looks good but not auditable | Enforce evidence and citation gates |
| AI invents evidence | Use fixture/source-only retrieval and block unsupported citations |
| Scoring seems arbitrary | Show rubric and criterion-level points |
| Too many claims overwhelm reviewer | Deduplicate and rank by materiality/risk |
| Green finance logic too broad | Limit MVP to use-of-proceeds and taxonomy checklist |
| Legal claims are sensitive | Use risk language and human review trigger |
| OCR/table extraction unreliable | Mark low confidence and use fixtures for core demo |

## 14. Explicit MVP acceptance statement

The MVP is accepted when a reviewer can open a company case, inspect at least five representative claims, see supporting/contradicting evidence, understand the verdict and risk score, override AI output, and export a working paper with traceable sources.
