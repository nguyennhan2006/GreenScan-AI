# AUDIT_PROTOCOL.md

Version: 0.1  
Status: Draft for manual audit simulation  
Owner: Research Lead / Reviewer  
Last updated: 2026-07-07

## 1. Purpose

This document describes the manual audit workflow used to assess greenwashing risk before automation. It is the professional reasoning model that AI should imitate. The purpose is not to legally determine fraud, but to produce a traceable, evidence-based risk assessment for sustainability-related claims.

## 2. Audit philosophy

The protocol follows an evidence-first principle:

```text
Claim → Evidence → Cross-check → Verdict → Risk score → Explanation → Review sign-off
```

No claim should be marked as supported unless the reviewer can trace it back to specific evidence with source, page, date, metric, and scope.

## 3. Professional principles

### 3.1 Professional skepticism

Reviewers must not assume that a sustainability claim is true because it appears in an annual report, ESG report, marketing page, prospectus, bond framework, or assurance statement. Each claim must be checked against evidence.

### 3.2 Materiality

Claims related to core business impacts, legal compliance, climate targets, financial instruments, or investor decision-making are more material than peripheral CSR claims.

### 3.3 Sufficiency and appropriateness of evidence

Evidence must be both sufficient and appropriate:

- Sufficient: enough evidence exists to evaluate the claim.
- Appropriate: the evidence is relevant, reliable, timely, and within the same scope as the claim.

### 3.4 Traceability

Every conclusion must be auditable. A reviewer must be able to find the exact source of the claim and the exact evidence used.

### 3.5 Conservative conclusion

When evidence is incomplete, ambiguous, or weak, do not overstate certainty. Use `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, or `INSUFFICIENT_EVIDENCE` instead of forcing a binary true/false conclusion.

## 4. Audit scope

### 4.1 In scope

- ESG reports.
- Annual reports.
- Sustainability reports.
- Financial statements and notes.
- Green bond or sustainable finance documents.
- Environmental permits and regulatory documents.
- News, enforcement actions, stock exchange disclosures, and external assurance.
- Taxonomies, reporting standards, and sector criteria.

### 4.2 Out of scope for MVP

- Legal opinion on fraud or liability.
- Full financial audit.
- Full environmental engineering verification.
- Real-time monitoring of emissions equipment.
- Final certification that an entity is green.

## 5. Audit workflow overview

```text
1. Register audit case
2. Build company profile
3. Determine material ESG/environmental issues
4. Collect and preserve source documents
5. Extract green claims
6. Classify claims by taxonomy
7. Define evidence requirements
8. Collect supporting evidence
9. Collect contradicting evidence
10. Grade evidence strength
11. Verify claim across five layers
12. Assign verdict
13. Score claim-level risk
14. Aggregate company-level risk
15. Prepare evidence card and working paper
16. Reviewer QA and sign-off
17. Record open questions and follow-up requests
```

## 6. Step-by-step protocol

### Step 1 — Register audit case

Create an audit case record:

- Company name.
- Industry.
- Reporting year.
- Documents reviewed.
- Reviewer name.
- Review date.
- Scope limitations.

### Step 2 — Build company profile

Before claim scoring, identify:

- Main business lines.
- Revenue drivers.
- Geographic footprint.
- Major assets/projects.
- Industry-specific environmental impacts.
- Known environmental incidents or controversies.
- Financial instruments labelled green or sustainable.

### Step 3 — Determine materiality map

Map the company to material environmental issues:

| Sector | Typical high-materiality issues |
|---|---|
| Banking/finance | Green credit, financed emissions, use-of-proceeds, exposure to carbon-intensive sectors |
| Energy | Scope 1 emissions, transition plan, fossil fuel dependency, renewable CAPEX |
| Cement/steel | Emissions intensity, energy, dust, waste heat, environmental permits |
| Real estate | Green building certification, construction waste, energy efficiency, land use |
| Manufacturing | Energy, water, waste, hazardous materials, supply chain impacts |
| Consumer goods | Packaging, recyclability, product claims, supply chain, waste |

### Step 4 — Preserve source documents

For every source document, capture:

- Document ID.
- File name.
- Source URL or upload path.
- Publication date.
- Version/hash if available.
- Pages used.
- Extraction quality notes.

### Step 5 — Extract green claims

A claim should be extracted if it creates an environmental or sustainability impression. Extract the exact text and preserve page/section.

Minimum fields:

```json
{
  "claim_id": "C-0001",
  "claim_text": "...",
  "source_document": "...",
  "page": 0,
  "section": "...",
  "company": "...",
  "year": 2024
}
```

### Step 6 — Classify claims

Classify each claim using `GREENWASHING_TAXONOMY.md`:

- Claim category.
- Greenwashing pattern candidates.
- Quantifiable or non-quantifiable.
- Materiality level.
- Evidence requirements.

### Step 7 — Define evidence requirements

For each claim, define what would be needed to support it. Example:

| Claim | Required evidence |
|---|---|
| “Reduced CO2 emissions by 20%” | Baseline, current emissions, scope boundary, method, assurance |
| “Green bond funded clean energy projects” | Bond framework, project list, allocation report, management of proceeds |
| “Complies with environmental law” | Permits, inspection records, no contradictory enforcement actions |

### Step 8 — Collect supporting evidence

Find evidence that could support the claim:

- Same report.
- Financial statement notes.
- ESG data tables.
- Assurance reports.
- Legal documents.
- Taxonomy confirmations.
- Project documents.

### Step 9 — Collect contradicting evidence

Perform negative evidence search. For each material claim, look for:

- Regulatory penalties.
- Environmental violations.
- News about pollution, incidents, disputes.
- Inconsistent data tables.
- Historical reports showing opposite trend.
- Missing allocation reports for green finance instruments.

### Step 10 — Grade evidence strength

Use `EVIDENCE_STANDARD.md` to assign evidence level from L1 to L5. Strong evidence should be preferred over marketing material.

### Step 11 — Verify claim across five layers

For every claim, answer:

1. Specificity: is the claim specific enough to test?
2. Evidence: is there direct evidence?
3. Quantitative consistency: do numbers match the claim?
4. Legal/taxonomy alignment: is the claim aligned with applicable criteria?
5. External contradiction: is there contradictory evidence outside the source report?

### Step 12 — Assign verdict

Use one of five verdicts:

| Verdict | Meaning |
|---|---|
| SUPPORTED | Strong evidence directly supports the claim |
| PARTIALLY_SUPPORTED | Some evidence supports the claim but key limitations remain |
| UNSUPPORTED | Claim is made but no adequate supporting evidence is found |
| CONTRADICTED | Reliable evidence conflicts with the claim |
| INSUFFICIENT_EVIDENCE | Evidence base is too incomplete to conclude |

### Step 13 — Score claim-level risk

Use `MANUAL_SCORING_RUBRIC.md`. Score the claim from 0 to 100. Higher score means higher greenwashing risk.

### Step 14 — Aggregate company-level risk

Aggregate by materiality and severity. Do not use a simple average if a few high-materiality contradicted claims dominate the risk profile.

Recommended high-level aggregation:

```text
Company Risk =
35% contradicted high-materiality claims
20% sustainable finance / use-of-proceeds risk
15% legal/taxonomy contradiction risk
15% disclosure transparency risk
10% vague/overstated claim volume
5% assurance and governance weakness
```

### Step 15 — Prepare evidence card and working paper

For every claim reviewed, produce:

- Evidence card for UI/demo.
- Working paper for audit trace.

The evidence card is user-facing. The working paper is reviewer-facing and must include scoring details and sign-off trail.

### Step 16 — Reviewer QA and sign-off

A second reviewer should check:

- Claim was extracted exactly.
- Evidence matches claim scope and period.
- Verdict follows evidence.
- Score follows rubric.
- Explanation is traceable.

### Step 17 — Record follow-up

If evidence is missing, record a request:

- Data needed.
- Source owner.
- Deadline if applicable.
- Reason the missing evidence matters.

## 7. Human review trigger rules

Send a claim to human review if any of the following is true:

- Risk score >= 70.
- Verdict is `CONTRADICTED`.
- Claim is high materiality and evidence is weak.
- Claim concerns green bond, green loan, taxonomy alignment, compliance, or net-zero.
- OCR/table extraction confidence is low.
- AI retrieved conflicting evidence.
- AI cannot identify source page or source document.

## 8. Reviewer conduct rules

Reviewers must:

- Preserve original wording.
- Avoid rewriting a claim to make it easier to support.
- Distinguish absence of evidence from contradiction.
- Record uncertainty explicitly.
- Avoid final legal conclusions unless supported by formal legal evidence.
- Escalate ambiguous high-materiality claims.

## 9. Minimum audit outputs

For MVP, every reviewed company should produce:

1. Claim register.
2. Evidence register.
3. Claim-level verdicts and scores.
4. Company-level risk summary.
5. Evidence cards.
6. Working papers for high-risk claims.
7. Reviewer QA checklist.
8. Open evidence requests.

## 10. Implementation notes

- The AI pipeline should implement this protocol as separate services: claim extraction, evidence retrieval, verification, scoring, explanation, and human review.
- Every AI verdict should be treated as preliminary until reviewed for high-risk cases.
- The system should store both evidence accepted and evidence rejected.

## 11. Open issues

- Define exact Vietnamese legal source hierarchy.
- Create sector-specific materiality maps.
- Calibrate company-level aggregation against sample cases.
