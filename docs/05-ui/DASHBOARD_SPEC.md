# DASHBOARD_SPEC.md

Version: 0.1  
Status: Draft UI component contract  
Owner: Product Owner / Frontend Engineer  
Last updated: 2026-07-07

## 1. Purpose

The company dashboard is the first decision screen after pipeline completion. It answers:

> “How risky is this company’s sustainability disclosure profile, and what should I inspect first?”

The dashboard is not a final audit conclusion. It is a triage interface that helps reviewers prioritize claim-level evidence inspection.

## 2. Source alignment

This dashboard spec is aligned with:

- `docs/02-product/OUTPUT_SPEC.md` — `CompanyDashboard`,
- `docs/03-architecture/API_CONTRACTS.md` — `GET /cases/{case_id}/dashboard`,
- `docs/04-data-ai/DATA_SCHEMA.md` — `CompanyAssessment`, `VerificationVerdict`, `RiskLabel`, `ReviewStatus`,
- `docs/01-domain-audit/MANUAL_SCORING_RUBRIC.md` — score interpretation.

The dashboard must not calculate verdicts or scores in the UI.

## 3. Data contract

### 3.1 Required API

```text
GET /cases/{case_id}/dashboard
```

### 3.2 Minimum response shape

```json
{
  "case_id": "CASE-0001",
  "company_name": "ABC Corporation",
  "industry": "Manufacturing",
  "reporting_year": 2024,
  "assessment_date": "2026-07-07",
  "company_risk_score": 72,
  "company_risk_label": "HIGH",
  "total_claims": 38,
  "verdict_distribution": {
    "SUPPORTED": 12,
    "PARTIALLY_SUPPORTED": 9,
    "UNSUPPORTED": 8,
    "CONTRADICTED": 6,
    "INSUFFICIENT_EVIDENCE": 3
  },
  "top_risk_categories": ["EMISSIONS", "GREEN_FINANCE", "LEGAL_COMPLIANCE"],
  "top_high_risk_claims": ["CLAIM-0004", "CLAIM-0012"],
  "review_queue_count": 8,
  "documents_reviewed": ["DOC-0001", "DOC-0002"],
  "methodology_version": "audit-protocol-0.1",
  "score_version": "manual-rubric-0.1",
  "disclaimer": "This is a greenwashing risk assessment, not a legal finding."
}
```

## 4. Layout

Recommended MVP layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Case header: company · industry · year · status · versions    │
├───────────────────────┬──────────────────────────────────────┤
│ Risk summary card      │ Verdict distribution                 │
│ score + label          │ Supported / Partial / Unsupported... │
├───────────────────────┴──────────────────────────────────────┤
│ Review queue + urgent actions                                │
├──────────────────────────────────────────────────────────────┤
│ Top risk categories                                           │
├──────────────────────────────────────────────────────────────┤
│ Top high-risk claims table                                    │
├──────────────────────────────────────────────────────────────┤
│ Documents reviewed + methodology disclaimer                   │
└──────────────────────────────────────────────────────────────┘
```

## 5. Components

## 5.1 Case header

### Fields

- company name,
- industry,
- reporting year,
- case ID,
- assessment date,
- pipeline status,
- methodology version,
- score version.

### Actions

- `View documents`,
- `View pipeline run`,
- `Export report`,
- `Open review queue`.

### Acceptance criteria

- Case ID is copyable.
- Methodology version is visible without opening a modal.
- User can navigate to document list and pipeline history.

## 5.2 Risk summary card

### Purpose

Show company-level greenwashing risk quickly.

### Fields

- `company_risk_score`,
- `company_risk_label`,
- total claims,
- review pending count,
- disclaimer.

### Display rules

| Risk label | UI text |
|---|---|
| LOW | Low greenwashing risk |
| MODERATE | Moderate greenwashing risk |
| HIGH | High greenwashing risk |
| VERY_HIGH | Very high greenwashing risk |
| CRITICAL | Critical review priority |

Do not display “illegal”, “fraud”, or “confirmed greenwashing”.

## 5.3 Verdict distribution

### Purpose

Show how claim-level verification outcomes are distributed.

### Required categories

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`
- `CONTRADICTED`
- `INSUFFICIENT_EVIDENCE`

### Interaction

Clicking a verdict category filters the claim table.

Example route:

```text
/cases/{case_id}/claims?verdict=CONTRADICTED
```

### Acceptance criteria

- Counts sum to `total_claims`.
- Every category is visible even if count is zero.
- Verdict enum is preserved in tooltip/detail for QA.

## 5.4 Review queue summary

### Purpose

Show reviewer workload and urgent cases.

### Fields

- `review_queue_count`,
- count by review trigger if available,
- high-risk pending count,
- contradicted pending count,
- low-confidence pending count.

### Actions

- `Open review queue`,
- `Filter pending high-risk claims`.

### Trigger categories

```text
HIGH_RISK
CONTRADICTED
LOW_CONFIDENCE
MISSING_REQUIRED_EVIDENCE
LEGAL_OR_TAXONOMY_CONFLICT
GREEN_FINANCE_AMBIGUITY
```

## 5.5 Top risk categories

### Purpose

Help user understand which ESG/finance areas drive risk.

### Fields per category

- category name,
- number of claims,
- average risk score,
- number of contradicted claims,
- number of unsupported claims,
- pending review count.

### Interaction

Clicking a category filters claim table by category.

## 5.6 Top high-risk claims

### Purpose

Expose claims that deserve immediate reviewer inspection.

### Required columns

| Column | Description |
|---|---|
| Claim ID | Stable ID |
| Short claim | Truncated claim text |
| Category | Main category |
| Verdict | Standard enum/display label |
| Risk | Score + label |
| Evidence signal | Supporting/contradicting/missing counts |
| Review status | Current review status |
| Action | Open evidence card |

### Default sort

1. `review_status = PENDING_REVIEW`,
2. highest risk score,
3. `CONTRADICTED`,
4. `UNSUPPORTED`,
5. highest materiality.

## 5.7 Documents reviewed

### Purpose

Show source coverage and limitations.

### Fields

- document ID,
- file name,
- source type,
- processing status,
- quality flags.

### Acceptance criteria

- User can see if key document types are missing.
- Quality flags are visible.
- Document list links to document screen.

## 5.8 Methodology and disclaimer block

### Required text pattern

```text
This dashboard summarizes greenwashing risk based on extracted claims and available evidence. It is not a legal finding or a full financial/environmental audit. Review methodology: {methodology_version}. Score version: {score_version}.
```

## 6. Dashboard interactions

| User action | Result |
|---|---|
| Click verdict segment | Claim table filtered by verdict |
| Click risk category | Claim table filtered by category |
| Click top claim | Evidence card opens |
| Click review queue | Review queue opens |
| Click export report | Export center opens |
| Click document count | Document list opens |

## 7. States

### 7.1 Not ready

If pipeline has not run:

```text
Dashboard is not ready. Run the pipeline to generate claim verification outputs.
```

Action: `Run pipeline`.

### 7.2 Partial output

If some stages failed:

- show available data,
- show warning banner,
- do not hide failed stages,
- disable final export if required outputs are missing.

### 7.3 No claims found

```text
No green claims were extracted from the processed documents. Check document quality or extraction settings.
```

Actions:

- `View documents`,
- `View processing logs`,
- `Run claim extraction again`.

## 8. Visual rules

- Use color only as secondary cue; labels must be explicit.
- Risk card should be prominent but not sensational.
- `CONTRADICTED` and `CRITICAL` may be visually emphasized but must avoid accusatory language.
- Methodology/disclaimer must be visible, not hidden in footer only.

## 9. QA checks

Before accepting dashboard implementation:

- [ ] Counts match API response.
- [ ] Verdict categories use exact enums.
- [ ] Risk labels use exact enums.
- [ ] Clicking dashboard filters opens correct claim table state.
- [ ] Top claim opens correct evidence card.
- [ ] Dashboard does not calculate score client-side.
- [ ] Methodology and score versions are visible.
- [ ] Disclaimer is visible.
- [ ] Empty and partial states are handled.

## 10. MVP acceptance criteria

Dashboard is MVP-complete when:

1. reviewer can understand risk status in under 10 seconds,
2. reviewer can identify top risky claims,
3. reviewer can open evidence card from dashboard,
4. pending human review is visible,
5. methodology and limitations are clear,
6. dashboard can be rendered from mock API data using documented contract.

