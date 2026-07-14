# HUMAN_REVIEW_SPEC.md

Version: 0.1  
Status: Draft reviewer workflow contract  
Owner: Product Owner / Reviewer Lead / Frontend Engineer  
Last updated: 2026-07-07

## 1. Purpose

Human review is the control layer that prevents the system from presenting AI outputs as final audit conclusions. The reviewer validates, revises, rejects, or escalates AI-generated verdicts and scores.

The MVP must support a simple but auditable review loop:

```text
Review trigger → Review queue → Evidence card → Reviewer decision → Audit log → Updated output/version
```

## 2. Source alignment

This spec is aligned with:

- `docs/02-product/MVP_SCOPE.md` — human review in scope,
- `docs/02-product/OUTPUT_SPEC.md` — `HumanReviewRecord`,
- `docs/03-architecture/API_CONTRACTS.md` — `POST /cases/{case_id}/claims/{claim_id}/review`,
- `docs/04-data-ai/DATA_SCHEMA.md` — `ReviewStatus`, `HumanReviewRecord`, `AuditLogEntry`,
- `docs/01-domain-audit/REVIEWER_QA_CHECKLIST.md`.

## 3. Review principles

### 3.1 Reviewer is accountable

AI can propose verdicts, scores, and explanations. The reviewer is responsible for accepting or changing high-risk/uncertain conclusions.

### 3.2 Preserve original output

Reviewer decisions must not delete original AI output. They must create:

- review record,
- audit log entry,
- updated current status or override version.

### 3.3 Require comments for non-accept decisions

Any revise, reject, or escalate action requires a comment.

### 3.4 Review is evidence-centered

Reviewer decision should reference evidence card content, not unsupported personal judgment.

## 4. Review statuses

Canonical enum from data schema:

```text
NOT_REQUIRED
PENDING_REVIEW
ACCEPTED
REVISED
REJECTED
ESCALATED
```

### Status meanings

| Status | Meaning |
|---|---|
| NOT_REQUIRED | Claim did not trigger mandatory review |
| PENDING_REVIEW | Claim needs reviewer action |
| ACCEPTED | Reviewer accepts AI verdict/score |
| REVISED | Reviewer changed verdict, score, or rationale |
| REJECTED | Reviewer rejected AI output as unusable |
| ESCALATED | Reviewer sent claim to senior/domain expert |

## 5. Review triggers

A claim should enter review queue if any trigger applies.

### 5.1 Mandatory MVP triggers

| Trigger | Condition |
|---|---|
| High risk | `risk_label` is `VERY_HIGH` or `CRITICAL` |
| Contradicted | `verdict = CONTRADICTED` |
| Missing required evidence | Required evidence list is not empty and materiality is high |
| Green finance ambiguity | Use-of-proceeds or green bond claim lacks tracking evidence |
| Legal/taxonomy issue | Legal/taxonomy layer fails or has insufficient data |
| Low confidence | Extraction/retrieval/verification confidence below configured threshold |

### 5.2 Optional future triggers

- large score change after new evidence,
- conflicting external sources,
- OCR/table confidence low,
- multiple duplicate claims with inconsistent wording,
- reviewer disagreement in multi-reviewer mode.

## 6. Review queue screen

### Purpose

Let reviewers work through claims that require human attention.

### Required columns

| Column | Description |
|---|---|
| Claim ID | Stable ID |
| Short claim | Truncated claim text |
| Category | Claim category |
| Materiality | LOW/MEDIUM/HIGH/CRITICAL/UNKNOWN |
| Verdict | AI verdict |
| Risk | Score + label |
| Trigger | Why review is required |
| Evidence signal | Supporting/contradicting/missing counts |
| Review status | Current status |
| Action | Open evidence card |

### Default sort

1. `CRITICAL` risk,
2. `CONTRADICTED`,
3. high materiality,
4. missing required evidence,
5. oldest pending first.

### Filters

- review status,
- trigger type,
- verdict,
- risk label,
- category,
- materiality,
- assigned reviewer if available.

## 7. Reviewer action panel

This panel appears in the evidence card.

### 7.1 Accept

Use when reviewer agrees with AI result.

Payload:

```json
{
  "decision": "ACCEPT",
  "comment": "Evidence and score are reasonable.",
  "reviewer_id": "USER-0001"
}
```

Comment optional but recommended.

### 7.2 Revise

Use when reviewer agrees the claim needs assessment but changes verdict, score, rationale, or evidence interpretation.

Payload:

```json
{
  "decision": "REVISE",
  "revised_verdict": "PARTIALLY_SUPPORTED",
  "revised_score": 58,
  "comment": "Original contradiction was too strong because the claim refers only to market-based Scope 2, not total Scope 1+2.",
  "reviewer_id": "USER-0001"
}
```

Validation:

- `revised_verdict` required,
- `revised_score` required,
- comment required,
- score 0–100,
- verdict must use canonical enum.

### 7.3 Reject

Use when AI output is not usable.

Common reasons:

- wrong claim extraction,
- wrong source citation,
- irrelevant evidence,
- hallucinated rationale,
- score inconsistent with rubric.

Payload:

```json
{
  "decision": "REJECT",
  "comment": "Evidence item EVID-0004 is unrelated to the claim and the source page is incorrect.",
  "reviewer_id": "USER-0001"
}
```

### 7.4 Escalate

Use when claim requires senior expert, legal/taxonomy expert, or external verification.

Payload:

```json
{
  "decision": "ESCALATE",
  "comment": "Green bond taxonomy alignment cannot be resolved with available documents.",
  "reviewer_id": "USER-0001"
}
```

## 8. Review reason categories

For structured analytics, UI may ask reviewer to select one or more reason categories.

```text
CLAIM_EXTRACTION_ERROR
CLAIM_CLASSIFICATION_ERROR
EVIDENCE_IRRELEVANT
EVIDENCE_MISSING
SOURCE_CITATION_ERROR
VERDICT_TOO_STRONG
VERDICT_TOO_WEAK
SCORE_TOO_HIGH
SCORE_TOO_LOW
LEGAL_TAXONOMY_AMBIGUITY
GREEN_FINANCE_AMBIGUITY
NEEDS_MORE_DOCUMENTS
OTHER
```

## 9. Audit log requirements

Every review action must produce an audit log entry.

### Required audit fields

- audit log ID,
- case ID,
- claim ID,
- previous review status,
- new review status,
- original AI verdict,
- original AI score,
- revised verdict if any,
- revised score if any,
- reviewer ID,
- timestamp,
- comment,
- reason category,
- affected output version.

## 10. Versioning behavior

### 10.1 Original AI output

Must remain visible as:

```text
AI-generated result
```

### 10.2 Current reviewed output

If revised, UI should show:

```text
Reviewed result
```

### 10.3 Comparison

When reviewer revised verdict/score, show a comparison:

| Field | AI result | Reviewer result |
|---|---|---|
| Verdict | CONTRADICTED | PARTIALLY_SUPPORTED |
| Score | 78 | 58 |
| Risk label | VERY_HIGH | HIGH |

## 11. Permission model for MVP

MVP can use single-reviewer mode.

Minimal roles:

| Role | Permissions |
|---|---|
| Viewer | View dashboard, claims, evidence cards, exports |
| Reviewer | Viewer + submit review decisions |
| Admin | Reviewer + reset review status, configure methodology versions |

If roles are not implemented, mock `reviewer_id` must still be captured.

## 12. Review completion rules

A case may be marked `REVIEWED` when:

- no claims remain `PENDING_REVIEW`, or
- reviewer explicitly accepts unresolved pending items as limitation.

Company-level report must state:

- number of claims reviewed,
- number accepted,
- number revised,
- number rejected,
- number escalated,
- unresolved limitations.

## 13. UI warnings

Show warning banners when:

- user attempts to export final report with pending review items,
- reviewer revises score without comment,
- reviewer tries to mark contradicted/critical claim as accepted without viewing evidence card,
- source references are unavailable,
- pipeline output version changed after review.

## 14. QA checklist

- [ ] Review queue shows all mandatory trigger claims.
- [ ] Evidence card action panel supports accept/revise/reject/escalate.
- [ ] Comments required for revise/reject/escalate.
- [ ] Revised verdict uses canonical enum.
- [ ] Revised score is 0–100.
- [ ] Original AI result is preserved.
- [ ] Audit log entry is created.
- [ ] Review status updates in dashboard and claim table.
- [ ] Export includes review status and reviewer comments.
- [ ] Pending review warnings work.

## 15. MVP acceptance criteria

Human review is MVP-complete when:

1. high-risk/uncertain claims enter review queue,
2. reviewer can open evidence card from queue,
3. reviewer can accept/revise/reject/escalate,
4. non-accept actions require comments,
5. original AI output is preserved,
6. review decision changes current review status,
7. audit log records reviewer action,
8. exported working paper includes review result.

