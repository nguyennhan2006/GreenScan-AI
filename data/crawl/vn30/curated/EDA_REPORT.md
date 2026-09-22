# EDA — VN30 claim candidates

## Input

7,960 claim candidates from 177 documents across
18 companies. Median length 267 chars, p95
936. 4,089 contain a number.

## Three problems that make the raw file unusable as-is

**1. Boilerplate — 31.3% of records (2,493).**
Keyword matching cannot tell a claim from a navigation menu that happens to
contain "phát triển bền vững". Reasons:

- `no_predicate` × 2,188
- `title_case_fragment` × 758
- `too_short` × 123
- `navigation_menu` × 100
- `section_header` × 46
- `too_few_unique_tokens` × 21
- `standards_index_row` × 12
- `layout_artifact` × 4

**2. Duplication — 984 redundant records
(12.4%).** The same boilerplate line repeats across pages and
report years. Annotating these spends budget re-labelling one sentence.

**3. Concentration — HHI 0.1686, effective companies 5.9
out of 18.** Top contributors: tra (2,157), pan (1,687), bvh (1,150), sab (779), pnj (772).
A benchmark drawn uniformly from this file mostly measures the largest issuer's
house style, not greenwashing.

## Output

| | |
| --- | ---: |
| Kept after filtering | 5,028 (63.2%) |
| Dropped (with reasons) | 2,932 |
| Annotation priority pool (score ≥ 2.0) | 3,682 |

Priority pool by split: {'future_holdout': 1602, 'review': 1058, 'test': 378, 'dev': 376, 'train': 268}

`informativeness` rewards a number with a unit, a target year, claim vocabulary
and sustainability-report provenance; it penalises very long passages. It is a
**sampling aid, not a label** — it says "worth a reviewer's time", never
"this is greenwashing".

## Files

- `claim_candidates_clean.jsonl` — filtered, deduplicated, scored
- `annotation_priority.jsonl` — the pool to annotate first
- `dropped_with_reasons.jsonl` — every exclusion, auditable and reversible
- `EDA_REPORT.json` — the numbers above, machine-readable

Nothing here is deleted from `normalized/`; this is an additive curated view.
