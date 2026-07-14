# EVIDENCE_CARD_SPEC.md

Version: 0.1  
Status: Draft UI component contract  
Owner: Product Owner / Reviewer UX / Frontend Engineer  
Last updated: 2026-07-07

## 1. Purpose

The evidence card is the most important reviewer screen in the product. It connects one extracted green claim to:

```text
Claim → Source → Required evidence → Supporting evidence → Contradicting evidence → Missing evidence → Verification → Score → Human review
```

The evidence card must let a reviewer decide whether the AI-generated verdict and score are justified.

## 2. Source alignment

This spec is aligned with:

- `docs/02-product/OUTPUT_SPEC.md` — `EvidenceCard`,
- `docs/03-architecture/API_CONTRACTS.md` — `GET /cases/{case_id}/claims/{claim_id}/evidence-card`,
- `docs/04-data-ai/DATA_SCHEMA.md` — `EvidenceItem`, `EvidencePackage`, `VerificationResult`, `RiskScore`,
- `docs/01-domain-audit/CLAIM_VERIFICATION_WORKING_PAPER.md`,
- `docs/01-domain-audit/EVIDENCE_STANDARD.md`,
- `docs/01-domain-audit/REVIEWER_QA_CHECKLIST.md`.

## 3. Data contract

### 3.1 Required API

```text
GET /cases/{case_id}/claims/{claim_id}/evidence-card
```

### 3.2 Minimum response shape

```json
{
  "evidence_card_id": "ECARD-0001",
  "case_id": "CASE-0001",
  "claim_id": "CLAIM-0001",
  "claim_text": "The company reduced Scope 1 and 2 emissions by 20% in 2024.",
  "claim_category": "EMISSIONS_REDUCTION",
  "materiality": "HIGH",
  "source": {
    "source_document_id": "DOC-0001",
    "source_page": 42,
    "source_section": "Environment",
    "source_chunk_id": "CHUNK-0007"
  },
  "verdict": "CONTRADICTED",
  "risk_score": 78,
  "risk_label": "VERY_HIGH",
  "explanation": "The claim states a reduction, but the reported Scope 1+2 emissions increased from 100,000 tCO2e in 2023 to 125,000 tCO2e in 2024.",
  "evidence": [],
  "missing_evidence": ["ASSURANCE_STATEMENT"],
  "verification_layers": [],
  "score_breakdown": [],
  "review_status": "PENDING_REVIEW",
  "methodology_version": "audit-protocol-0.1",
  "score_version": "manual-rubric-0.1"
}
```

## 4. Layout

Recommended MVP layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Claim ID · verdict · risk · review status             │
├──────────────────────────────────────────────────────────────┤
│ Exact claim text + source reference                           │
├───────────────────────┬──────────────────────────────────────┤
│ Verification summary  │ Reviewer action panel                 │
├───────────────────────┴──────────────────────────────────────┤
│ Evidence tabs: Supporting · Contradicting · Missing · Excluded │
├──────────────────────────────────────────────────────────────┤
│ Five-layer verification                                       │
├──────────────────────────────────────────────────────────────┤
│ Score breakdown                                               │
├──────────────────────────────────────────────────────────────┤
│ Audit trail / versions / export working paper                 │
└──────────────────────────────────────────────────────────────┘
```

## 5. Sections

## 5.1 Header

### Required fields

- `claim_id`,
- `evidence_card_id`,
- `verdict`,
- `risk_score`,
- `risk_label`,
- `review_status`,
- methodology version,
- score version.

### Actions

- `Back to claims`,
- `Copy claim ID`,
- `Export working paper`,
- `Open source` if source viewer exists.

## 5.2 Exact claim block

### Purpose

Show what the company actually claimed.

### Required display

- exact claim text,
- short display text if needed,
- source document ID,
- page/section/chunk,
- claim category,
- materiality,
- pattern candidates if available.

### Rules

- Do not paraphrase the claim as the primary display.
- Paraphrase may be shown only as helper text.
- Source reference must be copyable.

## 5.3 Verification summary

### Purpose

Give reviewer a fast understanding of why the verdict was assigned.

### Required display

- verdict,
- plain-language verdict explanation,
- risk score and label,
- top reason,
- top contradicting evidence if any,
- missing required evidence count.

### Verdict display mapping

| Enum | Display text |
|---|---|
| SUPPORTED | Supported by evidence |
| PARTIALLY_SUPPORTED | Partially supported |
| UNSUPPORTED | Unsupported by available evidence |
| CONTRADICTED | Contradicted by evidence |
| INSUFFICIENT_EVIDENCE | Insufficient evidence |

The enum must remain accessible to QA/developer views.

## 5.4 Evidence tabs

### Tabs

```text
Supporting evidence
Contradicting evidence
Missing required evidence
Excluded/contextual evidence
```

### Evidence item display

Each evidence item must show:

| Field | Requirement |
|---|---|
| Evidence ID | Required |
| Role | SUPPORTING/CONTRADICTING/CONTEXTUAL/EXCLUDED/MISSING_REQUIRED |
| Strength | L1–L5 enum + readable label |
| Source type | Required |
| Source reference | Document/page/link/chunk/table |
| Quote or value | Required unless missing evidence placeholder |
| Retrieval method | Required for AI/retrieved evidence |
| Why relevant | Required if used in verification |
| Why excluded | Required for excluded evidence |

### Evidence strength display

| Enum | Display label |
|---|---|
| L1_HIGH_AUTHORITY | High authority / independent |
| L2_OFFICIAL_DISCLOSURE | Official disclosure |
| L3_COMPANY_UNASSURED_DATA | Company data, unaudited |
| L4_EXTERNAL_OR_MEDIA | External/media source |
| L5_MARKETING_OR_LOW_RELIABILITY | Marketing or low reliability |

### Rules

- Contradicting evidence must not be hidden below supporting evidence.
- Missing required evidence must be visible when verdict is not `SUPPORTED`.
- Excluded evidence must show exclusion reason.

## 5.5 Five-layer verification

### Required layers

1. Specificity check,
2. Evidence availability check,
3. Quantitative consistency check,
4. Legal/taxonomy alignment check,
5. External contradiction check.

### Layer display shape

```json
{
  "layer": "QUANTITATIVE_CONSISTENCY",
  "status": "FAILED",
  "summary": "Claim says emissions decreased, but normalized Scope 1+2 metrics increased.",
  "linked_evidence_ids": ["EVID-0001", "EVID-0002"]
}
```

### Layer status enum for UI

```text
PASSED
PARTIAL
FAILED
NOT_APPLICABLE
INSUFFICIENT_DATA
```

These layer statuses are UI/verification details and must not replace the canonical verdict enum.

## 5.6 Score breakdown

### Required display

Show the 7 scoring criteria from `MANUAL_SCORING_RUBRIC.md` / `RISK_SCORING_SPEC.md`:

| Criterion | Max points |
|---|---:|
| C1 Claim vagueness | 15 |
| C2 Missing quantitative data | 15 |
| C3 Missing baseline/time/scope | 10 |
| C4 Missing evidence | 20 |
| C5 Missing independent assurance | 10 |
| C6 Contradiction | 20 |
| C7 Exaggerated language | 10 |

Each criterion must show:

- points assigned,
- rationale,
- linked evidence IDs if applicable.

### Rules

- UI must not recalculate criterion points.
- If reviewer revises score, original AI score must remain visible as prior version.

## 5.7 Reviewer action panel

### Actions

```text
Accept
Revise
Reject
Escalate
Add comment
```

### Required fields for revise

- revised verdict,
- revised score,
- comment,
- reason category if available.

### Required fields for reject/escalate

- comment,
- reason category.

### UI validation

- Comment required for revise/reject/escalate.
- Revised score must be 0–100.
- Revised verdict must use canonical enum.
- User must confirm before overwriting review status.

## 5.8 Audit trail and versions

### Display

- original AI verdict,
- current verdict if revised,
- reviewer name/ID,
- timestamp,
- review decision,
- audit log ID,
- model/prompt/schema versions if available.

### Rule

Reviewer action must create a new version or override record. It must never delete the original AI output.

## 6. Source viewer behavior

MVP source viewer may be simple:

- show document ID and page,
- show quote/snippet,
- allow copy source reference,
- optionally link to raw file.

Production source viewer may support:

- PDF page preview,
- highlighted source text,
- table cell locator,
- side-by-side claim/evidence.

## 7. Empty and edge states

| Situation | UI behavior |
|---|---|
| No supporting evidence | Show “No supporting evidence selected.” |
| No contradicting evidence | Show “No contradicting evidence selected.” |
| Missing evidence exists | Show required evidence list prominently |
| Evidence source unavailable | Show source unavailable warning |
| Score missing | Show scoring incomplete state |
| Review locked | Disable actions and explain why |
| Claim not found | Return to claim table |

## 8. Safety and wording rules

Use:

- “This claim is contradicted by available evidence.”
- “The evidence package is insufficient.”
- “Requires reviewer confirmation.”

Avoid:

- “The company lied.”
- “Illegal greenwashing.”
- “Fraudulent claim.”
- “AI proves misconduct.”

## 9. QA checklist

- [ ] Exact claim text is shown.
- [ ] Claim source reference is visible.
- [ ] Verdict enum is correct.
- [ ] Risk score and risk label match API.
- [ ] Supporting and contradicting evidence are separated.
- [ ] Missing required evidence is visible.
- [ ] Evidence strength is shown.
- [ ] Every evidence item has source reference.
- [ ] Five verification layers are visible.
- [ ] Score breakdown has 7 criteria.
- [ ] Reviewer comment is required for revise/reject/escalate.
- [ ] Original AI result is preserved after reviewer action.
- [ ] Working paper export is reachable.

## 10. MVP acceptance criteria

Evidence card is MVP-complete when a reviewer can:

1. read exact claim text,
2. identify claim source,
3. understand verdict and risk score,
4. inspect supporting evidence,
5. inspect contradicting evidence,
6. see missing evidence,
7. understand five-layer verification,
8. inspect score breakdown,
9. submit review decision,
10. export claim-level working paper.

