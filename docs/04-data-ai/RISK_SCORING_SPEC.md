# RISK_SCORING_SPEC.md

Version: 0.1  
Status: Draft scoring contract  
Owner: Domain Audit Lead / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines risk scoring for greenwashing assessment. It operationalizes `MANUAL_SCORING_RUBRIC.md` for implementation.

The score measures greenwashing risk, not legal liability.

## 2. Score direction

```text
0 = low greenwashing risk
100 = critical greenwashing risk
```

## 3. Claim-level score

### 3.1 Base criteria

| Code | Criterion | Max points |
|---|---|---:|
| C1 | Specificity weakness | 15 |
| C2 | Missing quantitative data | 15 |
| C3 | Missing baseline/time/scope | 10 |
| C4 | Weak or missing evidence | 20 |
| C5 | Lack of independent assurance | 10 |
| C6 | Contradictory evidence | 20 |
| C7 | Overstatement or misleading language | 10 |
|  | Total | 100 |

### 3.2 Criterion C1 — Specificity weakness

| Points | Condition |
|---:|---|
| 0 | claim is precise and bounded |
| 5 | minor ambiguity but still verifiable |
| 10 | material ambiguity in scope or wording |
| 15 | vague/marketing claim with no clear measurable content |

### 3.3 Criterion C2 — Missing quantitative data

| Points | Condition |
|---:|---|
| 0 | quantitative claim has necessary numbers |
| 5 | some numbers present but incomplete |
| 10 | numbers exist but not directly tied to claim |
| 15 | quantitative/implied quantitative claim has no usable data |

### 3.4 Criterion C3 — Missing baseline/time/scope

| Points | Condition |
|---:|---|
| 0 | baseline, period, and scope are clear |
| 3 | one minor qualifier missing |
| 7 | key qualifier missing |
| 10 | reduction/improvement claim lacks baseline or time/scope |

### 3.5 Criterion C4 — Weak or missing evidence

| Points | Condition |
|---:|---|
| 0 | strong direct evidence, appropriate source |
| 5 | adequate evidence with minor limitations |
| 10 | partial or indirect evidence |
| 15 | weak evidence only |
| 20 | no direct evidence for material claim |

### 3.6 Criterion C5 — Lack of independent assurance

| Points | Condition |
|---:|---|
| 0 | relevant independent assurance or official confirmation exists |
| 3 | partial assurance or limited scope confirmation |
| 5 | internal methodology disclosed but no assurance |
| 10 | no assurance for claim where assurance is expected |

For minor qualitative claims, this criterion may be `0` or `NOT_APPLICABLE` converted to `0`.

### 3.7 Criterion C6 — Contradictory evidence

| Points | Condition |
|---:|---|
| 0 | no material contradiction found |
| 5 | weak or contextual tension |
| 10 | partial contradiction or scope mismatch |
| 15 | strong contradiction with some limitation |
| 20 | direct material contradiction |

### 3.8 Criterion C7 — Overstatement or misleading language

| Points | Condition |
|---:|---|
| 0 | wording is balanced and proportionate |
| 3 | mild promotional wording |
| 7 | broad claim exceeds evidence |
| 10 | strong exaggeration, absolute claim, or misleading framing |

## 4. Claim-level risk labels

| Score | Label |
|---:|---|
| 0–20 | LOW |
| 21–40 | MODERATE |
| 41–60 | HIGH |
| 61–80 | VERY_HIGH |
| 81–100 | CRITICAL |

## 5. Modifiers

Modifiers must be explicit and versioned.

### 5.1 Materiality modifier

Materiality does not automatically increase claim score, but it affects review priority and company aggregation.

Optional modifier for MVP:

| Materiality | Modifier |
|---|---:|
| LOW | 0 |
| MEDIUM | 0 |
| HIGH | +5 max |
| CRITICAL | +10 max |

Cap total score at 100.

### 5.2 Green finance modifier

Apply up to +10 when:

- use-of-proceeds is unclear,
- proceeds tracking is missing,
- project eligibility is unsupported,
- green bond/loan claim lacks impact reporting.

### 5.3 Net-zero / transition modifier

Apply up to +10 when:

- no interim target,
- no transition plan,
- no CAPEX/implementation pathway,
- boundary excludes material emissions without disclosure,
- overreliance on offsets without evidence.

## 6. Verdict-to-score consistency

| Verdict | Expected score range | Notes |
|---|---:|---|
| SUPPORTED | 0–30 | may be higher only if wording materially overstates evidence |
| PARTIALLY_SUPPORTED | 20–60 | depends on missing evidence and materiality |
| UNSUPPORTED | 40–75 | high if material or finance/legal claim |
| CONTRADICTED | 60–100 | direct contradiction should be very high |
| INSUFFICIENT_EVIDENCE | 30–80 | depends on materiality and missing evidence |

If score falls outside expected range, add `score_consistency_flag` and require reviewer check.

## 7. Company-level score

### 7.1 Purpose

Company-level score summarizes disclosure risk for prioritization. It must not hide claim-level evidence.

### 7.2 MVP aggregation

Recommended formula:

```text
Company Risk =
  35% contradicted/high contradiction claims
+ 20% green finance high-risk claims
+ 15% legal/taxonomy high-risk claims
+ 15% transparency and missing evidence profile
+ 10% vague/overstated claim density
+  5% assurance weakness
```

### 7.3 Practical calculation

For implementation, compute sub-scores:

```ts
type CompanySubScores = {
  contradiction_subscore: number;
  green_finance_subscore: number;
  legal_taxonomy_subscore: number;
  transparency_subscore: number;
  vague_overstatement_subscore: number;
  assurance_weakness_subscore: number;
};
```

Weighted average:

```text
round(
  contradiction_subscore * 0.35 +
  green_finance_subscore * 0.20 +
  legal_taxonomy_subscore * 0.15 +
  transparency_subscore * 0.15 +
  vague_overstatement_subscore * 0.10 +
  assurance_weakness_subscore * 0.05
)
```

### 7.4 Aggregation safeguards

- A single critical contradicted claim should be visible even if average score is moderate.
- Do not average duplicated claim group members as separate risk events.
- Weight by materiality.
- Show distribution, not only one number.

## 8. Score rationale

Each `RiskScore` must store rationale for:

- each criterion with non-zero points,
- any modifier,
- total risk label,
- review trigger if any.

Example:

```json
{
  "C6_contradictory_evidence": 20,
  "rationale_C6": "Evidence EVID-0002 shows Scope 1+2 increased, contradicting the claimed reduction."
}
```

## 9. Human review rules

Human review required when:

- score >= 70,
- verdict is `CONTRADICTED`,
- score/verdict consistency flag exists,
- high materiality claim has `INSUFFICIENT_EVIDENCE`,
- legal/green finance modifiers applied,
- evidence strength is below minimum.

## 10. Versioning

Any change to points, thresholds, modifiers, or aggregation weights must create a new `score_version`.

Current version:

```text
manual-rubric-0.1
```

## 11. Acceptance criteria

- Claim score equals sum of criteria and modifiers, capped at 100.
- Score rationale is stored.
- Score version is stored.
- Company score does not hide top high-risk claims.
- High-risk scores trigger review.
