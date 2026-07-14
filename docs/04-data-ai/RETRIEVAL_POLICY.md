# RETRIEVAL_POLICY.md

Version: 0.1  
Status: Draft retrieval policy  
Owner: Product Owner / Product Engineer  
Last updated: 2026-07-07

## 1. Purpose

This document defines how the system retrieves evidence for each green claim.

The retrieval system must search for both:

- supporting evidence, and
- contradicting or missing evidence.

A greenwashing system that only searches for support will systematically miss risk.

## 2. Retrieval principle

```text
Each claim → evidence requirements → query plan → multi-source retrieval → rerank → evidence grading → selected evidence package
```

No retrieved item may influence verdict or score until it is graded and linked to the claim.

## 3. Retrieval methods

| Method | Use for | Strength |
|---|---|---|
| BM25/full-text | exact phrases, metric names, legal IDs, page text | high precision for known terms |
| Vector search | semantic paraphrases, similar statements | higher recall for varied language |
| Hybrid/RRF | combine lexical and semantic retrieval | robust default when both available |
| Structured metric lookup | emissions, energy, waste, finance values | best for quantitative verification |
| Legal/taxonomy rule lookup | eligibility, criteria, compliance | best for rule-based checks |
| Manual evidence add | reviewer adds missing evidence | audit-controlled override |

## 4. Query planning

### 4.1 Inputs

- classified claim,
- evidence requirements,
- materiality,
- company profile,
- source inventory,
- available metric store,
- available legal/taxonomy rule store.

### 4.2 Required query families

For each material claim, create at least:

1. direct support query,
2. metric/baseline query if quantifiable,
3. contradiction query,
4. source-specific query,
5. missing evidence placeholder if source inventory lacks required documents.

### 4.3 Example

Claim:

> “The company reduced Scope 1 and 2 emissions by 20% in 2024.”

Retrieval plan:

```json
{
  "support_queries": [
    "Scope 1 Scope 2 emissions 2024 company",
    "GHG emissions table 2024 company",
    "20% reduction emissions 2024"
  ],
  "contradiction_queries": [
    "emissions increased 2024 company",
    "Scope 1 Scope 2 2023 2024 increase",
    "environmental violation company 2024"
  ],
  "structured_lookups": [
    "metric:scope_1_2_emissions:2023:2024"
  ]
}
```

## 5. Supporting evidence search

Supporting search tries to find evidence that can validate the claim.

| Claim type | Supporting evidence examples |
|---|---|
| Emissions reduction | current emissions, baseline emissions, methodology, boundary |
| Renewable energy | renewable energy amount, total energy, certificates, PPA |
| Waste recycling | total waste, recycled waste, hazardous waste split |
| Green bond | framework, eligible projects, proceeds allocation, impact report |
| Net zero | target, interim milestones, transition plan, CAPEX, boundary |
| Legal compliance | permits, official status, compliance statements, audit reports |

## 6. Negative evidence search

Negative evidence search is mandatory for:

- high materiality claims,
- legal compliance claims,
- green finance claims,
- emission reduction claims,
- net-zero/transition claims,
- any claim with risk score likely above moderate.

### 6.1 Negative evidence targets

Search for:

- reported metric increases,
- conflicting baseline,
- missing proceeds tracking,
- regulatory violations,
- environmental incidents,
- assurance limitations,
- missing taxonomy confirmation,
- project ineligibility,
- external news contradicting company disclosure.

### 6.2 Negative evidence output

Negative evidence can lead to:

- `CONTRADICTING` evidence,
- `CONTEXTUAL` evidence,
- `MISSING_REQUIRED` evidence,
- no material contradiction found.

It must not automatically create a `CONTRADICTED` verdict unless evidence is source-linked and relevant.

## 7. OLTP vs OLAP retrieval routing

| Query type | Example | Retrieval route |
|---|---|---|
| OLTP/fact lookup | “What is Scope 1 in 2024?” | structured metric + BM25 |
| OLTP/legal lookup | “Does this project have a permit?” | legal/rule store + exact search |
| OLAP/synthesis | “Is this green bond likely greenwashing?” | hybrid retrieval + grouped evidence + synthesis |
| OLAP/trend | “Are claims consistent across years?” | metric store + multi-document retrieval |

## 8. Ranking and fusion

### 8.1 MVP default ranking

Use deterministic priority:

1. structured metric lookup,
2. legal/taxonomy rule lookup,
3. exact BM25 match,
4. hybrid/vector semantic match,
5. external source match,
6. marketing/low reliability source.

### 8.2 Hybrid fusion

When BM25 and vector search are both enabled, use rank fusion such as Reciprocal Rank Fusion or a deterministic equivalent. Store all component scores and the final fused rank.

### 8.3 Reranking criteria

Rerank candidates using:

- claim relevance,
- source strength,
- same company,
- same reporting year,
- same metric/scope,
- directness,
- contradiction value,
- page/section reliability,
- evidence requirement coverage.

## 9. Evidence exclusion policy

Exclude evidence from final package when:

| Reason | Example |
|---|---|
| Wrong company | article about subsidiary/peer not in scope |
| Wrong period | 2022 data used for 2024 claim without trend purpose |
| Wrong scope | Scope 3 used to verify Scope 1 claim incorrectly |
| Weak source | marketing slogan used as quantitative proof |
| Duplicate | same evidence repeated from same source |
| No provenance | cannot trace to document/page/source |
| Ambiguous | unclear whether value relates to claim |

Excluded evidence must keep `excluded_reason` for auditability.

## 10. Missing evidence policy

Missing evidence is not an error; it is an audit finding.

If a required evidence type is not found, create a `MISSING_REQUIRED` evidence item or list it in `missing_required_evidence`.

Examples:

- no baseline for “reduced emissions”,
- no proceeds allocation for green bond,
- no independent assurance for claimed verified ESG data,
- no taxonomy confirmation for claimed green project,
- no boundary for net-zero target.

## 11. Evidence package construction

For each claim, the selected evidence package should contain:

- strongest supporting evidence,
- strongest contradicting evidence if any,
- contextual evidence where needed,
- missing required evidence list,
- excluded evidence with reasons.

Default cap for MVP:

| Evidence role | Max selected |
|---|---:|
| Supporting | 5 |
| Contradicting | 5 |
| Contextual | 3 |
| Missing required | unlimited |

## 12. Retrieval quality checks

| Check | Required behavior |
|---|---|
| No evidence found | mark `INSUFFICIENT_EVIDENCE` candidate, trigger review if material |
| Only weak evidence found | keep as L4/L5, do not overstate support |
| Strong contradiction found | route to verification and human review trigger |
| Conflicting strong evidence | keep both, explain conflict |
| Evidence lacks source page | mark quality flag or exclude |

## 13. Retrieval metrics

Track:

- top-k retrieval recall on labeled cases,
- evidence precision after reviewer judgment,
- missing evidence false negatives,
- contradiction search hit rate,
- citation accuracy,
- evidence package usefulness rating from reviewers.

## 14. MVP implementation route

1. Start with local keyword search and structured metric lookup.
2. Add manual fixture evidence packages for demos.
3. Add vector search when document volume justifies it.
4. Add hybrid rank fusion.
5. Add graph/hierarchical retrieval for OLAP synthesis only after baseline is working.

## 15. Acceptance criteria

- Every material claim has supporting and contradiction search.
- Quantitative claims attempt structured lookup.
- Evidence package stores selected, excluded, and missing evidence.
- Retrieval method and scores are preserved.
- Verification never uses ungraded evidence.
