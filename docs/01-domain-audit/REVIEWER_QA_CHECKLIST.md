# REVIEWER_QA_CHECKLIST.md

Version: 0.1  
Status: QA checklist for reviewer consistency  
Owner: Reviewer / QA Lead  
Last updated: 2026-07-07

## 1. Purpose

This checklist is used by a second reviewer to verify that greenwashing claim assessment is consistent, evidence-based, and traceable. It should be applied to:

- high-risk claims;
- contradicted claims;
- sustainable finance claims;
- legal/taxonomy claims;
- any claim used in demo or training data;
- any AI-generated verdict before acceptance.

## 2. Quick pass/fail checklist

| # | QA item | Pass/Fail | Notes |
|---:|---|---|---|
| 1 | Claim text is preserved exactly as source |  |  |
| 2 | Source document, page, section, and year are recorded |  |  |
| 3 | Claim category follows taxonomy |  |  |
| 4 | Materiality level is justified |  |  |
| 5 | Evidence requirements are listed before verdict |  |  |
| 6 | Supporting evidence is traceable |  |  |
| 7 | Contradicting evidence search was performed |  |  |
| 8 | Evidence strength levels are assigned |  |  |
| 9 | Evidence matches claim boundary and period |  |  |
| 10 | Verdict follows evidence standard |  |  |
| 11 | Score follows manual scoring rubric |  |  |
| 12 | Rationale explains the main reason for risk |  |  |
| 13 | Missing evidence is explicitly recorded |  |  |
| 14 | Human review triggers are handled |  |  |
| 15 | Final output is suitable for evidence card |  |  |

## 3. Claim extraction QA

Check:

- The claim was not paraphrased.
- The claim is not split in a way that changes meaning.
- The claim is not merged with unrelated claims.
- The claim includes surrounding context if needed to understand what is being asserted.
- Visual/implied claims are described carefully and source screenshot/page is preserved.

Reject if:

- Original wording is missing.
- Page or source is missing.
- Claim is too broad because multiple claims were merged.

## 4. Taxonomy QA

Check:

- Claim category is selected from `GREENWASHING_TAXONOMY.md`.
- Multi-label claims are tagged with all relevant categories.
- Greenwashing pattern candidates are plausible.
- Materiality level reflects industry context.

Common errors:

- Treating CSR as core environmental performance.
- Treating product claims as entity-wide claims.
- Treating a target claim as actual performance.
- Treating a financing label as proof of green impact.

## 5. Evidence QA

Check:

- Evidence source level is correctly assigned using `EVIDENCE_STANDARD.md`.
- Evidence directly relates to the claim.
- Evidence is from the same period or has a valid comparison basis.
- Evidence boundary matches the claim boundary.
- Numeric evidence includes unit and metric name.
- Legal evidence matches exact company, subsidiary, site, or project.

Reject if:

- Evidence is only a marketing statement for a material claim.
- Evidence source cannot be found.
- Evidence uses different scope without explanation.
- Evidence from a later/earlier period is used as if same-period.

## 6. Negative evidence search QA

For material claims, confirm that reviewer searched for contradictory evidence.

Minimum negative search targets:

- regulatory penalties;
- environmental incidents;
- court/regulatory disputes;
- permit issues;
- inconsistent historical metrics;
- missing green bond allocation;
- external controversy;
- audit qualification or limitation.

Reject or return if high-materiality claim lacks negative evidence search.

## 7. Verdict QA

Use this table to check verdict consistency:

| Verdict | QA expectation |
|---|---|
| SUPPORTED | Strong evidence, same scope/period, no material contradiction |
| PARTIALLY_SUPPORTED | Some evidence but limitations clearly explained |
| UNSUPPORTED | No adequate evidence; no direct contradiction required |
| CONTRADICTED | Reliable evidence conflicts with claim |
| INSUFFICIENT_EVIDENCE | Evidence base too incomplete or ambiguous to conclude |

Common errors:

- Marking `SUPPORTED` based only on company narrative.
- Marking `CONTRADICTED` when evidence is merely missing.
- Marking `UNSUPPORTED` when there is direct contradictory evidence.
- Marking `INSUFFICIENT_EVIDENCE` to avoid making a clear `UNSUPPORTED` conclusion.

## 8. Scoring QA

Check:

- Each criterion score is filled.
- Total score calculation is correct.
- Materiality adjustment is documented.
- Finance/net-zero modifiers are documented if applied.
- Score range roughly matches verdict.
- Large deviations are explained.

Score reasonableness checks:

| Condition | Expected score behavior |
|---|---|
| Generic vague slogan only | Usually moderate risk, unless material or heavily promoted |
| Quantitative claim with no data | Usually high risk |
| Claim directly contradicted by reliable data | Usually very high or critical risk |
| Green bond without allocation tracking | Usually high risk |
| Supported by assured data | Usually low risk |

## 9. Explanation QA

The explanation should answer:

1. What was claimed?
2. What evidence was found?
3. What evidence was missing or contradictory?
4. Why does that lead to the verdict?
5. What should be checked next?

Reject if explanation:

- Uses legal/fraud language without basis.
- Does not cite source evidence.
- Overstates certainty.
- Does not mention key limitations.

## 10. Evidence card QA

Evidence card must contain:

- Claim text.
- Verdict.
- Risk score.
- Key evidence snippets.
- Source/page references.
- Missing evidence.
- Recommendation.
- Reviewer status.

## 11. AI output QA

For AI-generated assessment, reviewer must check:

- No hallucinated source.
- No fabricated page number.
- No invented legal standard.
- No unsupported claim that evidence exists.
- No raw LLM reasoning presented as evidence.
- All citations correspond to actual retrieved documents.

## 12. Escalation rules

Escalate to senior reviewer if:

- Score >= 80.
- Claim affects investor/lender decision materially.
- Claim concerns green bond proceeds or taxonomy eligibility.
- Claim concerns legal compliance and contradictory legal evidence exists.
- Reviewers disagree by more than 20 score points.
- Verdict disagreement remains after QA.

## 13. Inter-reviewer consistency log

For each reviewed batch, record:

| Batch | Reviewer A | Reviewer B | Agreement % | Main disagreement type | Action |
|---|---|---|---:|---|---|
|  |  |  |  |  |  |

Target for training set:

- Verdict agreement >= 80%.
- Score difference <= 15 points for 75% of claims.

## 14. Final sign-off

```yaml
claim_id:
qa_reviewer:
qa_date:
decision: APPROVED | RETURN_FOR_REVISION | ESCALATED
required_changes:
final_comment:
```
