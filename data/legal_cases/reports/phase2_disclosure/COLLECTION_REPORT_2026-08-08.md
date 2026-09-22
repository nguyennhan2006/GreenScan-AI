# Legal-case collection report — 2026-08-08

Run `legal-20260808-123238` · commit `582bedf` · crawler `legal-case-crawler/1.0`
Started 2026-08-08 12:32Z, finished 2026-08-08 12:48Z.

## Targets

| | |
| --- | ---: |
| Attempted | 29 |
| Case pack collected | 0 |
| Disclosure collected | 12 |
| Fully blocked (no artifact at all) | 17 |

Blocked: INT-ACTIVE-SUPER-AU, INT-ADIDAS-UK, INT-BLACK-MOUNTAIN-AU, INT-CALVIN-KLEIN-UK, INT-CLOROX-AU, INT-EQUINOR-NO, INT-ETIHAD-AE, INT-FERTOZ-AU, INT-LLOYDS-UK, INT-MORNINGSTAR-AU, INT-NORTHERN-TRUST-AU, INT-OATLY-UK, INT-SHELL-UK, INT-TESCO-UK, INT-TLOU-AU, INT-UNILEVER-UK, INT-VANGUARD-AU

## Documents

| | |
| --- | ---: |
| New documents | 186 |
| Authority artifacts | 0 |
| Corporate disclosures | 186 |
| Exact-duplicate hash groups | 5 |
| Bytes | 1,457,133,924 |
| Unknown/conflicting year (`review`) | 80 |

By authority: {'ASIC / Federal Court of Australia': 25, 'U.S. SEC': 13, 'UK Advertising Standards Authority': 148}

By document family: {'annual_or_integrated': 97, 'sustainability_or_esg': 69, 'product_disclosure': 16, 'case_artifact': 4}

## Text layer

Not evaluated in this run — the runbook puts the OCR decision in Phase 5, after
source QA. `documents.jsonl` carries `extension` and `bytes` so the decision can
be made without re-fetching.

## Failures

- `zero_documents_found` × 28
- `http_403` × 11
- `robots_denied` × 6
- `http_429` × 3
- `http_404` × 2
- `ReadError` × 1
- `ReadTimeout` × 1

Full queue with next actions: `failure_queue.csv`.

## Label integrity

`greenwashing_label` is null on every record and is not derivable from this run.
`case_relevance_hint` marks authority artifacts only; it is a retrieval hint, not
a verdict. Settlement and ruling qualifiers are carried per document from the
registry.

## Next actions

1. Work `failure_queue.csv`, starting with `zero_documents_found` — those seeds
   are likely JS-rendered and need `harvest_js_listings.py`.
2. Resolve the 80 `review`-year documents before any split assignment.
3. Review externally-linked case artifacts queued as `external_domain_queued`.
4. Run text-layer analysis (Phase 5) before parsing.
