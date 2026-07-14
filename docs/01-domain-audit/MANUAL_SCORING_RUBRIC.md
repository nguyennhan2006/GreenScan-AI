# MANUAL_SCORING_RUBRIC.md

Version: 0.1  
Status: Draft scoring standard  
Owner: Research Lead / Reviewer  
Last updated: 2026-07-07

## 1. Purpose

This document defines how a human reviewer manually scores greenwashing risk for each green claim. The same rubric should later be implemented in the AI system.

The score is a risk score from 0 to 100:

- 0 = very low risk.
- 100 = critical greenwashing risk.

This score is not a legal finding. It is an audit-style risk indicator based on claim quality, evidence quality, contradiction, and materiality.

## 2. Scoring principles

1. Score the claim, not the company, at the first stage.
2. Use evidence, not impression.
3. Separate missing evidence from contradictory evidence.
4. Increase risk when the claim is material to investors, lenders, regulators, or consumers.
5. Never assign `SUPPORTED` only because the company says so.
6. Document the scoring rationale in the working paper.

## 3. Claim-level scoring model

Total maximum score: 100.

| Criterion | Max points | Risk question |
|---|---:|---|
| C1. Specificity weakness | 15 | Is the claim vague, broad, or undefined? |
| C2. Missing quantitative data | 15 | Does the claim lack numbers where numbers are necessary? |
| C3. Missing baseline/time/scope | 10 | Does the claim lack baseline, period, unit, or boundary? |
| C4. Weak or missing evidence | 20 | Is there insufficient relevant evidence? |
| C5. Lack of independent assurance | 10 | Is third-party assurance missing where expected? |
| C6. Contradictory evidence | 20 | Does reliable evidence conflict with the claim? |
| C7. Overstatement or misleading presentation | 10 | Does the language, image, or comparison overstate benefit? |

## 4. Detailed scoring rules

### C1. Specificity weakness — 0 to 15

| Score | Condition |
|---:|---|
| 0 | Claim is precise and testable |
| 5 | Claim is mostly clear but one element needs interpretation |
| 10 | Claim is broad and only partly testable |
| 15 | Claim is generic, slogan-like, or undefined |

Examples:

- 0: “Scope 1 and 2 emissions decreased by 12% from 2023 to 2024.”
- 10: “We improved environmental performance significantly.”
- 15: “We are a green and sustainable company.”

### C2. Missing quantitative data — 0 to 15

| Score | Condition |
|---:|---|
| 0 | Quantitative data is provided and directly relevant |
| 5 | Data exists but is incomplete or partly indirect |
| 10 | Claim implies measurement but only qualitative explanation exists |
| 15 | Claim requires numbers but no numbers are provided |

Apply this criterion mainly to claims about reduction, efficiency, emissions, energy, waste, water, CAPEX, green revenue, or use-of-proceeds.

### C3. Missing baseline/time/scope — 0 to 10

| Score | Condition |
|---:|---|
| 0 | Baseline, reporting period, unit, and scope are clear |
| 3 | One minor element is missing |
| 6 | Multiple elements are unclear |
| 10 | Claim cannot be compared because baseline/time/scope is absent |

Common missing elements:

- Baseline year.
- Current year.
- Scope 1/2/3 boundary.
- Organizational boundary.
- Production volume or intensity denominator.
- Project boundary.

### C4. Weak or missing evidence — 0 to 20

| Score | Condition |
|---:|---|
| 0 | Strong, direct, traceable evidence supports the claim |
| 5 | Evidence supports the claim but has minor limitations |
| 10 | Evidence is indirect, incomplete, or only partly relevant |
| 15 | Evidence is weak, self-promotional, or not traceable |
| 20 | No adequate evidence found |

Evidence must be assessed using `EVIDENCE_STANDARD.md`.

### C5. Lack of independent assurance — 0 to 10

| Score | Condition |
|---:|---|
| 0 | Independent assurance/verification covers this claim or metric |
| 3 | Assurance exists but scope is limited |
| 6 | Assurance is mentioned but unclear or not claim-specific |
| 10 | No independent assurance where assurance is expected |

This criterion is especially important for:

- GHG emissions.
- Green bond allocation and impact reporting.
- Net-zero targets.
- Taxonomy alignment.
- Material environmental compliance claims.

### C6. Contradictory evidence — 0 to 20

| Score | Condition |
|---:|---|
| 0 | No contradictory evidence found after reasonable search |
| 5 | Minor inconsistency exists but does not undermine the claim |
| 10 | Material ambiguity or tension exists |
| 15 | Strong inconsistency exists |
| 20 | Reliable evidence directly contradicts the claim |

Examples:

- Claim says emissions decreased, but emissions table shows increase: 20.
- Claim says full environmental compliance, but official penalty exists in same period: 15–20 depending severity.
- Claim says all green bond proceeds allocated, but allocation report is missing: C6 may be 0 unless contradiction exists; score under C4 and finance-specific modifiers instead.

### C7. Overstatement or misleading presentation — 0 to 10

| Score | Condition |
|---:|---|
| 0 | Language is balanced and proportional |
| 3 | Mild promotional language |
| 6 | Strong language that may exaggerate significance |
| 10 | Highly misleading language, unclear comparison, or deceptive implied claim |

Warning signs:

- “100% green” without evidence.
- “Environmentally superior” without comparator.
- “Carbon neutral” without explaining offsets and residual emissions.
- Nature imagery creating environmental impression with no supporting data.

## 5. Risk level mapping

| Score | Level | Meaning |
|---:|---|---|
| 0–20 | LOW | Claim is well-supported or low-risk |
| 21–40 | MODERATE | Claim has limitations but no major contradiction |
| 41–60 | HIGH | Claim has weak evidence, ambiguity, or material omissions |
| 61–80 | VERY_HIGH | Claim is materially unsupported, overstated, or inconsistent |
| 81–100 | CRITICAL | Claim is strongly contradicted or severely misleading |

## 6. Verdict mapping guidance

| Verdict | Typical score range | Notes |
|---|---:|---|
| SUPPORTED | 0–25 | Strong evidence, low ambiguity |
| PARTIALLY_SUPPORTED | 20–50 | Evidence supports part of the claim but limitations remain |
| UNSUPPORTED | 40–70 | Claim lacks adequate support but no direct contradiction |
| CONTRADICTED | 65–100 | Reliable evidence conflicts with claim |
| INSUFFICIENT_EVIDENCE | 30–70 | Data too incomplete to conclude; score depends on materiality |

The score and verdict do not have to match perfectly, but large deviations require explanation.

## 7. Materiality adjustment

After base scoring, apply materiality adjustment:

| Materiality | Adjustment |
|---|---:|
| HIGH | +0 to +10 |
| MEDIUM | +0 |
| LOW | -0 to -10 |

Rules:

- Do not reduce below 0 or increase above 100.
- Apply adjustment only after documenting base score.
- A high-materiality claim with weak evidence should normally not be below 40.

## 8. Finance-specific modifiers

For green bond, green loan, sustainable finance, and use-of-proceeds claims, add risk if missing:

| Missing item | Add points |
|---|---:|
| No use-of-proceeds definition | +10 |
| No eligible project list or category | +8 |
| No project evaluation/selection criteria | +6 |
| No management-of-proceeds tracking | +10 |
| No allocation report | +8 |
| No impact reporting | +5 |
| No external review for material labelled instrument | +5 |

Cap total score at 100.

## 9. Net-zero and target-specific modifiers

For net-zero, carbon neutral, climate neutral, Paris-aligned, or transition claims, add risk if missing:

| Missing item | Add points |
|---|---:|
| No Scope 1/2/3 boundary | +10 |
| No interim milestone | +8 |
| No baseline year | +6 |
| No decarbonization plan | +10 |
| No CAPEX or operational plan | +8 |
| Offset reliance not disclosed | +8 |
| No progress tracking | +6 |

## 10. Scoring examples

### Example 1 — Vague claim

Claim: “We are committed to a greener future.”

Suggested scoring:

- C1: 15
- C2: 0, if no quantitative implication; 15 if framed as performance claim
- C3: 5
- C4: 10
- C5: 0
- C6: 0
- C7: 6
- Base: 36–51 depending context
- Verdict: `UNSUPPORTED` or `INSUFFICIENT_EVIDENCE`

### Example 2 — Quantitative contradiction

Claim: “The company reduced Scope 1 and 2 emissions in 2024.”  
Evidence: ESG table shows Scope 1+2 increased from 120,000 to 145,000 tCO2e.

Suggested scoring:

- C1: 0
- C2: 0
- C3: 0–3
- C4: 0
- C5: 5–10
- C6: 20
- C7: 5
- Materiality: +10 if emissions are high materiality
- Score: 40–48 before materiality; 50–58 after materiality if language is not extreme. If claim uses “strongly reduced” or investors rely on it, score may be 70+.
- Verdict: `CONTRADICTED`

### Example 3 — Green bond without allocation report

Claim: “Our green bond financed eligible renewable energy projects.”  
Evidence: bond framework exists but no allocation report, no project list, no management-of-proceeds disclosure.

Suggested scoring:

- C1: 3
- C2: 10
- C3: 6
- C4: 15
- C5: 10
- C6: 0 unless contradictory evidence exists
- C7: 5
- Finance modifiers: +20 to +30
- Score: 69–79
- Verdict: `UNSUPPORTED` or `PARTIALLY_SUPPORTED` depending framework detail

## 11. Reviewer notes

Reviewers should write a short rationale:

```text
The claim was scored HIGH because it implies a measurable environmental improvement but does not provide baseline, period, or supporting metrics. No direct contradiction was found. Evidence is limited to marketing language in the sustainability section.
```

## 12. Implementation notes

- The rubric should be implemented as an explainable scoring object, not just a final number.
- Store every criterion score separately.
- Store materiality adjustment separately.
- Store finance/net-zero modifiers separately.
- Do not allow final score without a rationale string.

## 13. Open issues

- Score calibration requires sample labelled cases.
- Sector-specific thresholds need further research.
- Treatment of positive CSR claims needs weighting calibration.
