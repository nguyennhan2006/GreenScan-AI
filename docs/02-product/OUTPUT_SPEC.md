# OUTPUT_SPEC.md

Version: 0.1  
Status: Draft for data contract and UI design  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines the product outputs of the Greenwashing Detection MVP. It is the contract between the domain audit logic, backend pipeline, UI, exports, and AI agents.

Every output must follow the evidence-first principle:

```text
Claim → Evidence → Verification → Verdict → Score → Explanation → Review status
```

## 2. Output layers

| Layer | Output | Primary user | Purpose |
|---|---|---|---|
| L1 | Company dashboard | Analyst, investor, bank officer | Understand overall risk quickly |
| L2 | Claim table | Analyst, reviewer | Browse, filter, and prioritize claims |
| L3 | Evidence card | Reviewer, evaluator | Inspect claim-level evidence and reasoning |
| L4 | Working paper | Reviewer, auditor | Preserve manual audit reasoning |
| L5 | Company report | Analyst, stakeholder | Share summary and recommendations |
| L6 | JSON export | Developer, QA, evaluator | Test, reproduce, integrate |
| L7 | Audit log | Reviewer, evaluator | Track changes and accountability |

## 3. Shared conventions

### 3.1 Stable IDs

All output objects must have stable IDs:

| Object | ID prefix example |
|---|---|
| Company case | `CASE-0001` |
| Document | `DOC-0001` |
| Chunk | `CHUNK-0001` |
| Claim | `CLAIM-0001` |
| Claim group | `CG-0001` |
| Evidence | `EVID-0001` |
| Verification result | `VER-0001` |
| Score | `SCORE-0001` |
| Review | `REV-0001` |
| Export | `EXP-0001` |

### 3.2 Verdict enum

All outputs must use this exact enum:

```ts
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
```

No UI, backend, or AI agent may invent alternative labels such as “likely true” or “false”. Plain-language labels may be shown only as display text mapped to the enum.

### 3.3 Risk labels

Default claim-level risk labels:

| Score | Label |
|---:|---|
| 0–20 | LOW |
| 21–40 | MODERATE |
| 41–60 | HIGH |
| 61–80 | VERY_HIGH |
| 81–100 | CRITICAL |

If thresholds are changed, `score_version` must change.

### 3.4 Evidence role enum

```ts
SUPPORTING
CONTRADICTING
CONTEXTUAL
EXCLUDED
MISSING_REQUIRED
```

### 3.5 Evidence strength enum

```ts
L1_HIGH_AUTHORITY
L2_OFFICIAL_DISCLOSURE
L3_COMPANY_UNASSURED_DATA
L4_EXTERNAL_OR_MEDIA
L5_MARKETING_OR_LOW_RELIABILITY
```

### 3.6 Review status enum

```ts
NOT_REQUIRED
PENDING_REVIEW
ACCEPTED
REVISED
REJECTED
ESCALATED
```

## 4. Output 1 — CompanyDashboard

### 4.1 Purpose

The dashboard answers: “How risky is this company’s sustainability disclosure profile, and what should I inspect first?”

### 4.2 Required fields

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
  "top_risk_categories": [
    "EMISSIONS",
    "GREEN_FINANCE",
    "LEGAL_COMPLIANCE"
  ],
  "top_high_risk_claims": ["CLAIM-0004", "CLAIM-0012"],
  "documents_reviewed": ["DOC-0001", "DOC-0002"],
  "methodology_version": "audit-protocol-0.1",
  "score_version": "manual-rubric-0.1",
  "disclaimer": "This is a greenwashing risk assessment, not a legal finding."
}
```

### 4.3 UI requirements

The dashboard must display:

- company risk score and label,
- number of claims,
- verdict distribution,
- top categories by risk,
- top high-risk claims,
- human review pending count,
- link to claim table,
- link to report export,
- disclaimer.

### 4.4 Acceptance criteria

- Dashboard can be understood in under 10 seconds.
- User can drill down from dashboard to claim table and evidence card.
- Dashboard must not hide methodology version.
- Dashboard must not present risk score as legal conclusion.

## 5. Output 2 — ClaimTable

### 5.1 Purpose

The claim table lets users browse, filter, sort, and prioritize all extracted green claims.

### 5.2 Required columns

| Field | Description |
|---|---|
| `claim_id` | Stable claim ID |
| `claim_text_short` | Shortened claim text |
| `claim_category` | Main taxonomy category |
| `patterns` | Candidate greenwashing patterns |
| `materiality` | LOW/MEDIUM/HIGH/CRITICAL |
| `source` | Document/page/section |
| `verdict` | Standard verdict enum |
| `risk_score` | 0–100 |
| `risk_label` | Risk label |
| `supporting_evidence_count` | Count of used supporting evidence |
| `contradicting_evidence_count` | Count of used contradicting evidence |
| `missing_required_evidence_count` | Missing evidence count |
| `review_status` | Human review status |

### 5.3 Filters

The claim table should support filtering by:

- company/case,
- source document,
- claim category,
- greenwashing pattern candidate,
- verdict,
- risk label,
- materiality,
- review status,
- evidence strength,
- score range.

### 5.4 Sort options

Default sort:

1. review pending first,
2. highest materiality,
3. highest risk score,
4. contradicted before unsupported,
5. newest claim ID.

### 5.5 Acceptance criteria

- Clicking a row opens the evidence card.
- All verdicts and labels use the standard enums.
- Claim table must show source reference for every claim.
- Duplicate claim groups must be visible without losing original instances.

## 6. Output 3 — EvidenceCard

### 6.1 Purpose

The evidence card is the core product output. It answers: “Why did the system reach this verdict for this claim?”

### 6.2 Required fields

```json
{
  "claim_id": "CLAIM-0001",
  "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
  "claim_category": ["EMISSIONS_REDUCTION"],
  "patterns": ["QUANTITATIVE_CONTRADICTION"],
  "materiality": "HIGH",
  "source_document": "DOC-0001",
  "source_page": 18,
  "source_section": "Environment",
  "verdict": "CONTRADICTED",
  "risk_score": 82,
  "risk_label": "CRITICAL",
  "plain_language_summary": "The claim says emissions decreased, but extracted Scope 1+2 data shows an increase for the same period.",
  "five_layer_checks": {
    "specificity": "PASS",
    "evidence_availability": "PASS",
    "quantitative_consistency": "FAIL",
    "legal_taxonomy_alignment": "NOT_APPLICABLE",
    "external_contradiction": "NOT_APPLICABLE"
  },
  "supporting_evidence": [],
  "contradicting_evidence": ["EVID-0003"],
  "missing_evidence": ["Independent assurance of emissions data"],
  "scoring_breakdown": "SCORE-0001",
  "review_status": "PENDING_REVIEW"
}
```

### 6.3 Evidence item display

Each evidence item shown inside the card must include:

| Field | Required? |
|---|---:|
| Evidence ID | Yes |
| Evidence role | Yes |
| Source name | Yes |
| Source type | Yes |
| Page/section/link | Yes, or explicit unknown |
| Quoted evidence text or metric reference | Yes |
| Extracted value/unit/year if metric | If applicable |
| Evidence strength | Yes |
| Relevance score | If available |
| Extraction confidence | If available |
| Used/excluded status | Yes |
| Exclusion reason | If excluded |

### 6.4 Explanation rules

The explanation must:

- separate claim text from AI interpretation,
- cite evidence IDs,
- explain missing evidence,
- use cautious language,
- avoid legal conclusion unless source evidence is legal/regulatory,
- state uncertainty when evidence is incomplete.

### 6.5 Acceptance criteria

- Reviewer can understand verdict without reading the full source document.
- Reviewer can trace every evidence item back to source.
- Evidence card displays both supporting and contradicting evidence.
- Missing required evidence is shown explicitly.
- Human review action is available when required.

## 7. Output 4 — VerificationResult

### 7.1 Purpose

A structured object representing the claim verification decision.

### 7.2 Required fields

```json
{
  "verification_id": "VER-0001",
  "claim_id": "CLAIM-0001",
  "verification_version": "audit-protocol-0.1",
  "checks": {
    "specificity": {
      "status": "PASS",
      "rationale": "Claim includes metric, percentage, and reporting year."
    },
    "evidence_availability": {
      "status": "PASS",
      "rationale": "Emissions table found in ESG report."
    },
    "quantitative_consistency": {
      "status": "FAIL",
      "rationale": "Scope 1+2 increased instead of decreased."
    },
    "legal_taxonomy_alignment": {
      "status": "NOT_APPLICABLE",
      "rationale": "Claim is not a taxonomy/project eligibility claim."
    },
    "external_contradiction": {
      "status": "NOT_APPLICABLE",
      "rationale": "No external contradiction required for this metric claim."
    }
  },
  "verdict": "CONTRADICTED",
  "verdict_rationale": "The same-period emissions metric contradicts the reduction claim.",
  "used_evidence_ids": ["EVID-0003"],
  "missing_evidence": [],
  "requires_human_review": true
}
```

### 7.3 Check status enum

```ts
PASS
PARTIAL
FAIL
NOT_APPLICABLE
NEEDS_REVIEW
```

## 8. Output 5 — RiskScore

### 8.1 Purpose

A structured score object with criterion-level traceability.

### 8.2 Required fields

```json
{
  "score_id": "SCORE-0001",
  "claim_id": "CLAIM-0001",
  "score_version": "manual-rubric-0.1",
  "criteria": {
    "vagueness": { "points": 0, "max": 15, "rationale": "Claim is specific." },
    "missing_quantitative_data": { "points": 0, "max": 15, "rationale": "Quantitative metric is available." },
    "missing_baseline_time_scope": { "points": 3, "max": 10, "rationale": "Year is present but baseline is not explicit in claim text." },
    "missing_evidence": { "points": 5, "max": 20, "rationale": "Evidence exists but no independent assurance." },
    "missing_independent_assurance": { "points": 10, "max": 10, "rationale": "No assurance found." },
    "contradiction": { "points": 20, "max": 20, "rationale": "Same-period data contradicts claim." },
    "exaggerated_language": { "points": 4, "max": 10, "rationale": "Uses strong wording but not extreme." }
  },
  "total_score": 42,
  "risk_label": "HIGH"
}
```

### 8.3 Acceptance criteria

- Criterion points must sum to total score unless capped.
- Each criterion must include rationale.
- Score object must be linked to the claim and verification result.
- Score version must be included.

## 9. Output 6 — HumanReviewRecord

### 9.1 Purpose

Captures reviewer decision and accountability.

### 9.2 Required fields

```json
{
  "review_id": "REV-0001",
  "claim_id": "CLAIM-0001",
  "reviewer": "reviewer_name",
  "review_status": "REVISED",
  "ai_verdict": "CONTRADICTED",
  "final_verdict": "PARTIALLY_SUPPORTED",
  "ai_score": 82,
  "final_score": 65,
  "comment": "The contradiction is partial because the claim refers to operational intensity, not absolute emissions.",
  "timestamp": "2026-07-07T10:00:00+07:00"
}
```

### 9.3 Acceptance criteria

- Reviewer action never deletes AI suggestion.
- Final decision records reviewer and timestamp.
- Revised score/verdict must include comment.

## 10. Output 7 — ClaimWorkingPaper

### 10.1 Purpose

The working paper preserves manual audit reasoning and is the most important export for professional review.

### 10.2 Sections

The working paper must include:

1. Claim record.
2. Claim interpretation.
3. Evidence requirements.
4. Supporting evidence reviewed.
5. Contradicting evidence reviewed.
6. Evidence excluded and reasons.
7. Five-layer verification.
8. Verdict rationale.
9. Scoring breakdown.
10. Missing evidence and follow-up requests.
11. Reviewer action and sign-off.
12. Limitations.

### 10.3 Markdown export skeleton

```md
# Claim Working Paper — CLAIM-0001

## 1. Claim

- Claim text:
- Source document:
- Page/section:
- Company:
- Year:

## 2. Classification

- Category:
- Pattern candidates:
- Materiality:
- Quantifiable:

## 3. Evidence requirements

...

## 4. Supporting evidence

...

## 5. Contradicting evidence

...

## 6. Verification

...

## 7. Score

...

## 8. Verdict

...

## 9. Reviewer sign-off

...
```

### 10.4 Acceptance criteria

- Export includes all used and excluded evidence.
- Export includes criterion-level score.
- Export includes reviewer status.
- Export states limitations and missing evidence.

## 11. Output 8 — CompanyReport

### 11.1 Purpose

The company report is a shareable summary for analysts, bank officers, evaluators, or stakeholders.

### 11.2 Required sections

```text
1. Executive summary
2. Scope and documents reviewed
3. Company profile and materiality map
4. Methodology summary
5. Claim summary and verdict distribution
6. Top high-risk claims
7. Evidence analysis by category
8. Green finance / use-of-proceeds review, if applicable
9. Legal/taxonomy alignment review, if applicable
10. Missing evidence and limitations
11. Recommendations for further review
12. Appendix: claim table, evidence references, scoring rubric version
```

### 11.3 Required disclaimers

The report must state:

- It is a greenwashing risk assessment.
- It is not a legal finding.
- It depends on available documents and extracted evidence.
- Human review is required for high-risk conclusions.

## 12. Output 9 — JSON export

### 12.1 Purpose

JSON export is for testing, reproducibility, downstream integration, and AI-agent synchronization.

### 12.2 Required top-level structure

```json
{
  "export_id": "EXP-0001",
  "export_version": "output-spec-0.1",
  "case": {},
  "documents": [],
  "claims": [],
  "claim_groups": [],
  "evidence_items": [],
  "verification_results": [],
  "risk_scores": [],
  "human_reviews": [],
  "audit_log": [],
  "limitations": []
}
```

### 12.3 Acceptance criteria

- Export must be deterministic for fixture demo cases.
- Export includes all IDs needed to reconstruct evidence cards.
- Export includes version metadata.
- Export must not include hallucinated sources.

## 13. Output 10 — AuditLog

### 13.1 Purpose

The audit log records system and reviewer actions.

### 13.2 Required fields

```json
{
  "log_id": "LOG-0001",
  "timestamp": "2026-07-07T10:00:00+07:00",
  "actor": "system_or_user",
  "action": "CLAIM_VERDICT_ASSIGNED",
  "object_type": "GreenClaim",
  "object_id": "CLAIM-0001",
  "details": {
    "previous_value": null,
    "new_value": "CONTRADICTED"
  }
}
```

### 13.3 Required logged actions

- Document uploaded.
- Document parsed.
- Claim extracted.
- Claim classified.
- Evidence retrieved.
- Evidence excluded.
- Verification completed.
- Score assigned.
- Human review action recorded.
- Report/export generated.

## 14. Display language rules

The UI should use clear Vietnamese labels for users, while keeping stable English enums in data.

Example mapping:

| Enum | Vietnamese display |
|---|---|
| `SUPPORTED` | Được hỗ trợ |
| `PARTIALLY_SUPPORTED` | Hỗ trợ một phần |
| `UNSUPPORTED` | Chưa có bằng chứng đủ dùng |
| `CONTRADICTED` | Bị mâu thuẫn bởi bằng chứng |
| `INSUFFICIENT_EVIDENCE` | Không đủ dữ liệu để kết luận |

## 15. Safety wording rules

The product must avoid unsupported accusation language.

Use:

- “Rủi ro greenwashing cao.”
- “Claim chưa được hỗ trợ bởi bằng chứng hiện có.”
- “Có bằng chứng mâu thuẫn với claim.”
- “Cần reviewer kiểm tra thêm.”

Avoid:

- “Doanh nghiệp gian lận.”
- “Claim chắc chắn sai” unless direct evidence clearly contradicts and reviewer confirms.
- “Vi phạm pháp luật” unless source legal evidence supports that wording.

## 16. Cross-document alignment

This output specification must stay aligned with:

- `USER_PERSONAS.md`: who consumes each output.
- `USER_STORIES.md`: backlog and acceptance criteria.
- `MVP_SCOPE.md`: MVP boundaries.
- `CLAIM_VERIFICATION_WORKING_PAPER.md`: working paper structure.
- `MANUAL_SCORING_RUBRIC.md`: scoring fields and risk labels.
- `EVIDENCE_STANDARD.md`: evidence strength and evidence role.
- `AUDIT_PROTOCOL.md`: five-layer verification and human sign-off.
