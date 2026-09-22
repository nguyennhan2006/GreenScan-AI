# Legal-case collection report — 2026-08-08

Run `legal-20260808-122721` · commit `582bedf` · crawler `legal-case-crawler/1.0`
Started 2026-08-08 12:27Z, finished 2026-08-08 12:31Z.

## Targets

| | |
| --- | ---: |
| Attempted | 29 |
| Case pack collected | 28 |
| Disclosure collected | 0 |
| Fully blocked (no artifact at all) | 1 |

Blocked: INT-CLOROX-AU

## Documents

| | |
| --- | ---: |
| New documents | 134 |
| Authority artifacts | 134 |
| Corporate disclosures | 0 |
| Exact-duplicate hash groups | 25 |
| Bytes | 30,991,029 |
| Unknown/conflicting year (`review`) | 22 |

By authority: {'ASIC / Federal Court of Australia': 18, 'U.S. SEC': 11, 'ASIC': 14, 'UK Advertising Standards Authority': 91}

By document family: {'ruling': 126, 'order': 8}

## Text layer

Not evaluated in this run — the runbook puts the OCR decision in Phase 5, after
source QA. `documents.jsonl` carries `extension` and `bytes` so the decision can
be made without re-fetching.

## Failures

- `http_403` × 1

Full queue with next actions: `failure_queue.csv`.

## Label integrity

`greenwashing_label` is null on every record and is not derivable from this run.
`case_relevance_hint` marks authority artifacts only; it is a retrieval hint, not
a verdict. Settlement and ruling qualifiers are carried per document from the
registry.

## Next actions

1. Work `failure_queue.csv`, starting with `zero_documents_found` — those seeds
   are likely JS-rendered and need `harvest_js_listings.py`.
2. Resolve the 22 `review`-year documents before any split assignment.
3. Review externally-linked case artifacts queued as `external_domain_queued`.
4. Run text-layer analysis (Phase 5) before parsing.
