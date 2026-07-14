# CLAIM_VERIFICATION_WORKING_PAPER.md

Version: 0.1  
Status: Template for manual review and AI evaluation  
Owner: Reviewer  
Last updated: 2026-07-07

## 1. Purpose

This document is the standard working paper template for reviewing a single green claim. It records the full reasoning trail from original claim to final verdict and score.

The working paper is internal. It is more detailed than the user-facing evidence card and is used for:

- manual audit simulation;
- reviewer sign-off;
- creating labelled datasets;
- checking AI outputs;
- resolving disputes between reviewers.

## 2. Working paper metadata

```yaml
working_paper_id:
audit_case_id:
claim_id:
company:
industry:
reporting_year:
reviewer:
second_reviewer:
review_date:
status: DRAFT | REVIEWED | APPROVED | NEEDS_MORE_EVIDENCE
```

## 3. Section A — Claim record

| Field | Value |
|---|---|
| Claim ID |  |
| Original claim text |  |
| Source document |  |
| Page / section |  |
| Publication date |  |
| Claim category |  |
| Greenwashing pattern candidates |  |
| Quantifiable? | Yes / No / Partly |
| Materiality | High / Medium / Low |
| Requires external evidence? | Yes / No |

### Reviewer notes

```text
Preserve the original claim wording. Do not paraphrase in this section.
```

## 4. Section B — Claim interpretation

Answer the following:

1. What exactly is being claimed?
2. Is the claim about entity, product, project, site, financing instrument, or target?
3. What environmental attribute is implied?
4. What period is implied?
5. What boundary is implied?
6. What would a reasonable investor/reader understand from this claim?

```text
Interpretation:

```

## 5. Section C — Evidence requirements

List the evidence needed to support the claim.

| Required evidence | Why needed | Found? | Source |
|---|---|---|---|
|  |  | Yes / No / Partial |  |

Examples:

- Baseline emissions.
- Current emissions.
- Scope boundary.
- Methodology.
- External assurance.
- Allocation report.
- Permit or official confirmation.

## 6. Section D — Supporting evidence collected

| Evidence ID | Source | Page/link | Level | Summary | Relevance |
|---|---|---|---|---|---|
| E- |  |  | L1/L2/L3/L4/L5 |  |  |

Detailed excerpts:

```text
E-0001:

E-0002:

```

## 7. Section E — Contradicting evidence collected

| Evidence ID | Source | Page/link | Level | Summary | Contradiction type |
|---|---|---|---|---|---|
| E- |  |  | L1/L2/L3/L4/L5 |  | quantitative/legal/external/scope |

Detailed excerpts:

```text
E-0003:

E-0004:

```

## 8. Section F — Evidence quality assessment

| Dimension | Assessment | Notes |
|---|---|---|
| Relevance | Strong / Medium / Weak |  |
| Reliability | Strong / Medium / Weak |  |
| Timeliness | Strong / Medium / Weak |  |
| Scope match | Strong / Medium / Weak |  |
| Completeness | Strong / Medium / Weak |  |
| Traceability | Strong / Medium / Weak |  |

## 9. Section G — Five-layer verification

| Layer | Question | Result | Notes |
|---|---|---|---|
| 1. Specificity | Is the claim specific and testable? | Pass / Partial / Fail |  |
| 2. Evidence | Is there direct supporting evidence? | Pass / Partial / Fail |  |
| 3. Quantitative consistency | Do numbers match the claim? | Pass / Partial / Fail / N/A |  |
| 4. Legal/taxonomy alignment | Does it align with criteria/legal evidence? | Pass / Partial / Fail / N/A |  |
| 5. External contradiction | Did negative search find contradiction? | Pass / Partial / Fail |  |

## 10. Section H — Verdict decision

Choose one:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`
- `CONTRADICTED`
- `INSUFFICIENT_EVIDENCE`

Verdict:

```text

```

Rationale:

```text

```

## 11. Section I — Claim-level scoring

| Criterion | Max | Score | Rationale |
|---|---:|---:|---|
| C1. Specificity weakness | 15 |  |  |
| C2. Missing quantitative data | 15 |  |  |
| C3. Missing baseline/time/scope | 10 |  |  |
| C4. Weak or missing evidence | 20 |  |  |
| C5. Lack of independent assurance | 10 |  |  |
| C6. Contradictory evidence | 20 |  |  |
| C7. Overstatement or misleading presentation | 10 |  |  |
| Base score | 100 |  |  |
| Materiality adjustment | +/-10 |  |  |
| Finance/net-zero modifier | variable |  |  |
| Final score | 100 |  |  |

Risk level:

```text
LOW / MODERATE / HIGH / VERY_HIGH / CRITICAL
```

## 12. Section J — Missing evidence and follow-up requests

| Missing evidence | Why it matters | Requested from | Priority |
|---|---|---|---|
|  |  |  | High / Medium / Low |

## 13. Section K — Reviewer conclusion

Short conclusion for evidence card:

```text

```

Internal reviewer note:

```text

```

## 14. Section L — Second reviewer QA

| QA item | Pass? | Comment |
|---|---|---|
| Original claim preserved exactly | Yes / No |  |
| Source and page recorded | Yes / No |  |
| Category is appropriate | Yes / No |  |
| Evidence matches claim scope | Yes / No |  |
| Negative evidence search performed | Yes / No |  |
| Verdict follows evidence | Yes / No |  |
| Score follows rubric | Yes / No |  |
| Explanation is traceable | Yes / No |  |
| High-risk trigger handled | Yes / No / N/A |  |

Second reviewer decision:

```text
APPROVE / RETURN_FOR_REVISION / ESCALATE
```

## 15. Machine-readable output

At the end of manual review, produce a JSON record:

```json
{
  "claim_id": "C-0001",
  "verdict": "CONTRADICTED",
  "risk_score": 78,
  "risk_level": "VERY_HIGH",
  "primary_evidence_ids": ["E-0001", "E-0003"],
  "missing_evidence": ["independent assurance report"],
  "review_status": "APPROVED",
  "reviewer_rationale": "..."
}
```

## 16. Usage guidance

- Use one working paper per claim.
- For low-risk repetitive claims, a lightweight version may be used.
- For high-risk claims, all sections are mandatory.
- Working papers should be stored with audit case ID and claim ID.
