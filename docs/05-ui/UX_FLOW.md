# UX_FLOW.md

Version: 0.1  
Status: Draft UI workflow contract  
Owner: Product Owner / Reviewer UX  
Last updated: 2026-07-07

## 1. Purpose

This document defines the user experience flow for the Greenwashing Detection MVP.

The UI must make the evidence-first workflow visible and auditable:

```text
Case → Documents → Claims → Evidence → Verification → Score → Review → Export
```

The product is not a generic ESG chatbot. It is a reviewer-facing audit support tool that helps users inspect green claims, understand evidence quality, and decide whether an AI-generated verdict should be accepted, revised, rejected, or escalated.

## 2. Source alignment

This UX flow is aligned with:

- `docs/02-product/MVP_SCOPE.md` for MVP boundaries,
- `docs/02-product/OUTPUT_SPEC.md` for product outputs,
- `docs/03-architecture/API_CONTRACTS.md` for data/API expectations,
- `docs/04-data-ai/DATA_SCHEMA.md` for canonical enums,
- `docs/01-domain-audit/AUDIT_PROTOCOL.md` for manual audit reasoning.

The UI must not redefine domain logic. Verdicts, scores, evidence strength, and review status must come from backend/domain outputs.

## 3. UX principles

### 3.1 Evidence before conclusion

Any screen showing a verdict or risk score must provide a route to the underlying evidence.

Bad UX:

```text
Claim: “Company reduced emissions.”
Risk: HIGH.
```

Good UX:

```text
Claim → Verdict → Risk → Why → Evidence → Source page → Reviewer decision
```

### 3.2 Reviewer control

The user must be able to:

- inspect every high-risk claim,
- view supporting and contradicting evidence separately,
- see missing required evidence,
- override or reject AI output,
- export an audit working paper.

### 3.3 Traceability by default

Every claim, evidence item, score rationale, and review action must show stable IDs and source references.

### 3.4 Clear uncertainty

The UI must distinguish:

- `UNSUPPORTED`: claim exists but evidence is not found or not sufficient,
- `INSUFFICIENT_EVIDENCE`: data is too weak or incomplete to reach a stable conclusion,
- `CONTRADICTED`: evidence conflicts with the claim.

The UI must not present uncertainty as factual wrongdoing.

### 3.5 Decision-useful, not decorative

Charts and badges should answer reviewer questions:

- What should I inspect first?
- Which claims are contradicted?
- Which claims have weak evidence?
- Which claims require human review?
- What changed after reviewer action?

## 4. Primary user journey

### 4.1 Journey overview

```text
1. Create or open assessment case
2. Upload or load documents
3. Run processing pipeline
4. View dashboard
5. Inspect claim table
6. Open evidence card
7. Review verdict and score
8. Submit reviewer decision
9. Export working paper/report
10. Preserve audit log
```

### 4.2 Entry states

| State | User sees | Primary action |
|---|---|---|
| No case | Empty workspace | Create case |
| Case created, no documents | Case shell | Upload documents |
| Documents uploaded, not processed | Document list | Run pipeline |
| Pipeline running | Run status | Monitor progress |
| Pipeline failed | Error and retry guidance | Fix input or retry stage |
| Pipeline completed | Dashboard | Inspect claims |
| Review pending | Claim queue | Review high-risk claims |
| Reviewed | Dashboard + review summary | Export |

## 5. Screen map

```text
/                         Landing or case list
/cases/new                 Create assessment case
/cases/{case_id}           Case overview
/cases/{case_id}/documents Document intake and processing status
/cases/{case_id}/runs      Pipeline run history
/cases/{case_id}/dashboard Company dashboard
/cases/{case_id}/claims    Claim table
/cases/{case_id}/claims/{claim_id} Evidence card
/cases/{case_id}/review    Human review queue
/cases/{case_id}/exports   Export center
```

MVP may combine multiple routes into one page with tabs, but the conceptual separation must remain.

## 6. Detailed UX flows

## Flow A — Create case

### User goal

Start a new assessment for a company and reporting period.

### Steps

1. User clicks `New assessment case`.
2. User enters company name, industry, reporting year, review scope, jurisdiction.
3. System creates `AssessmentCase`.
4. User is routed to document intake.

### Required fields

- `company_name`
- `industry` or `UNKNOWN`
- `reporting_year`
- `review_scope`
- `methodology_version`
- `score_version`

### Acceptance criteria

- Case ID is shown after creation.
- User can return to case list.
- Case creation does not require document upload in the same step.

## Flow B — Upload or load documents

### User goal

Add source material to the assessment.

### Steps

1. User uploads ESG report, annual report, BCTC, green bond framework, legal/taxonomy fixture, or external evidence fixture.
2. User assigns `source_type` and optional metadata.
3. System stores raw file and content hash.
4. UI shows document status.

### UI requirements

Document list should show:

- file name,
- source type,
- reporting year,
- processing status,
- quality flags,
- content hash or shortened hash,
- uploaded time.

### Error states

| Error | UI response |
|---|---|
| Unsupported file | Show accepted formats |
| Missing source type | Require metadata before processing |
| Corrupted file | Mark as failed and preserve error |
| Duplicate file hash | Warn user and allow skip/replace |

## Flow C — Run pipeline

### User goal

Process documents and produce claims, evidence cards, dashboard, and review queue.

### Steps

1. User clicks `Run pipeline`.
2. User selects run mode: fixture/demo or normal.
3. System returns `run_id`.
4. UI shows stage-level progress.
5. On completion, user moves to dashboard.

### Stage display

```text
PROCESS_DOCUMENTS
EXTRACT_CLAIMS
CLASSIFY_CLAIMS
RETRIEVE_EVIDENCE
VERIFY
SCORE
BUILD_OUTPUTS
```

### Acceptance criteria

- User can see which stage failed.
- Warnings are not hidden.
- Pipeline status is refreshable.
- Completed run links to dashboard.

## Flow D — Dashboard triage

### User goal

Understand overall risk and prioritize inspection.

### Steps

1. User opens dashboard.
2. User sees company risk, claim counts, verdict distribution, pending review count, top categories.
3. User clicks a high-risk category or top risky claim.
4. UI routes to filtered claim table or evidence card.

### Dashboard must answer

- How risky is the company?
- How many claims were reviewed by the AI pipeline?
- How many claims are contradicted, unsupported, or pending review?
- Which risk category should be inspected first?

## Flow E — Claim table triage

### User goal

Browse and prioritize extracted claims.

### Steps

1. User opens claim table.
2. User filters by verdict, risk label, materiality, category, review status.
3. User sorts by highest risk or review pending first.
4. User opens a claim evidence card.

### Acceptance criteria

- Every row has source reference.
- Claim text can be expanded.
- Filter state is visible.
- User can return from evidence card to same filtered table.

## Flow F — Evidence card inspection

### User goal

Decide whether the AI verdict and score are justified.

### Steps

1. User opens evidence card.
2. User reads exact claim and source location.
3. User reviews verdict, score, and explanation.
4. User inspects supporting evidence.
5. User inspects contradicting evidence.
6. User inspects missing required evidence.
7. User opens source snippets/pages.
8. User submits review decision.

### Evidence card must answer

- What exactly did the company claim?
- Where did the claim appear?
- What evidence supports it?
- What evidence contradicts it?
- What evidence is missing?
- Why did the system assign this verdict and score?
- What should the reviewer do next?

## Flow G — Human review

### User goal

Accept, revise, reject, or escalate AI output.

### Steps

1. User opens review queue or evidence card action panel.
2. User selects decision.
3. User adds required comment for non-accept decisions.
4. User optionally revises verdict/score.
5. System creates `HumanReviewRecord` and audit log.
6. UI reflects updated review status.

### Review decisions

| Decision | Meaning | Comment required |
|---|---|---|
| Accept | AI result is acceptable | Optional |
| Revise | Reviewer changes verdict/score/rationale | Required |
| Reject | AI result is not usable | Required |
| Escalate | Needs senior/domain expert review | Required |

## Flow H — Export

### User goal

Generate shareable and auditable outputs.

### Steps

1. User opens export center.
2. User chooses claim-level working paper, company-level report, or JSON export.
3. System generates export with version metadata.
4. User downloads output.

### Export requirements

- Include methodology version.
- Include score version.
- Include source references.
- Include review status.
- Include limitations/disclaimer.

## 7. Navigation rules

- Dashboard links to claim table and evidence card.
- Claim table links to evidence card.
- Evidence card links back to claim table with filters preserved.
- Evidence card links to working paper export.
- Review queue links directly to evidence cards.
- Export center links to generated files and audit log.

## 8. Empty states

| Screen | Empty state message | Action |
|---|---|---|
| Case list | No assessment cases yet | Create case |
| Documents | No documents uploaded | Upload document |
| Dashboard | No pipeline output yet | Run pipeline |
| Claim table | No claims match filters | Clear filters |
| Evidence card | Claim not found | Return to claim table |
| Review queue | No claims pending review | Go to dashboard |
| Exports | No exports generated | Generate export |

## 9. Loading and failure states

### Loading

Show stage-specific loading messages rather than generic spinners:

```text
Extracting claims from ESG report...
Searching contradicting evidence...
Building evidence cards...
```

### Failure

Failure UI must include:

- failed stage,
- error code/message,
- affected document or claim if known,
- retry action,
- link to logs if available.

## 10. UX copy rules

### Use

- “Greenwashing risk”
- “Evidence suggests”
- “The claim is contradicted by...”
- “Insufficient evidence to conclude”
- “Requires human review”

### Avoid

- “Fraud”
- “Illegal”
- “False claim” unless a legal/official source explicitly states it
- “Guaranteed green”
- “AI has proven”

## 11. Accessibility and readability requirements

- Do not encode risk only by color; always include text labels.
- Tables must support keyboard navigation in production design.
- Badges must have readable labels.
- Long claim text must be expandable.
- Source references must be copyable.
- Minimum supported language for MVP: English labels or Vietnamese labels, but enums remain uppercase English.

## 12. MVP acceptance criteria

The UX is complete for MVP when a reviewer can:

1. create a case,
2. add documents or fixtures,
3. run the pipeline,
4. understand dashboard risk in under 10 seconds,
5. filter claims,
6. open an evidence card,
7. inspect supporting/contradicting/missing evidence,
8. submit a review decision,
9. export a working paper,
10. reproduce the reasoning through source references.

## 13. Non-goals

The MVP UX does not need:

- full enterprise authentication,
- multi-reviewer workflow,
- real-time collaboration,
- live source PDF viewer with advanced annotations,
- full visual charting suite,
- public-facing consumer UI.

