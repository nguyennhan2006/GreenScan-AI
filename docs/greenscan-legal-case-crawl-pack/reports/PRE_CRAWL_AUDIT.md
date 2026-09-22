# PRE_CRAWL_AUDIT — 2026-08-08

Gate required by `README.md` §"Chạy trước khi crawl" and `04_CRAWL_RUNBOOK.md` Phase 0.
No document may be downloaded for the 29 legal-case targets until this passes.

## S0 — Registry

```
$ python scripts/validate_registry.py
OK: 29 unique targets; mandatory fields and URL shape valid
```

| Check | Result |
| --- | --- |
| Exactly 29 unique target IDs | ✅ 29 |
| `case_url` HTTPS + authority domain | ✅ all |
| `case_entity`, `reporting_entity`, `profile`, `level`, `qualifier` present | ✅ all |
| ≥1 official reporting seed per target | ✅ all (`report_url_1` populated on every row) |

Distribution — authorities: ASA UK 17, ASIC 5, U.S. SEC 3, ASIC/Federal Court 3,
ACCC/Federal Court 1. Levels: A (court/admission), B (regulator order), C
(advertising ruling / infringement notice). Profiles: 11 distinct, `energy_company`
(7) and `asset_manager` (6) largest.

**Note on class balance.** 17 of 29 targets are ASA advertising rulings — Level C,
the weakest legal ground truth. A benchmark built without stratifying on
`legal_strength` will mostly measure "can the model spot a UK ad ruling", not
greenwashing detection. Flagged for the annotation plan, not a blocker for
collection.

## Seven regressions — verified by execution

Run `python tools/verify_regressions.py`. Every check exercises real code paths;
six of these seven originally failed **silently**, so static inspection is not
acceptable evidence.

```
[PASS] R1. SEC/WAF headers          Accept+Accept-Encoding sent, gzip decode handled
[PASS] R2. attachment_domains       probe script present, known-CDN companies populated
[PASS] R3. IR URL validation        HTTP-verifies candidates, writes only when current URLs dead
[PASS] R4. static asset filter      5 asset URLs blocked, 4 document URLs preserved
[PASS] R5. robots policy            4xx allowed, 5xx denied, served Disallow still enforced
[PASS] R6. per-target cap           cap honored at limit, absent cap never trips
[PASS] R7. JSONL separator safety   writer escapes, round-trip exact, 0 consumers on splitlines()

7/7 regressions holding
```

Regression tests also green: `outside_resource/.../tests` 16 passed, repo `tests/` 18 passed.

## Baseline snapshot before this run

| Store | Documents | Notes |
| --- | ---: | --- |
| `data/crawl/vn30/raw` | 670 stored (442 PDF) | 21 companies, 2021–2025, 3.9 GB |
| `data/real_cases/sources/originals` | 14 | 45 MB |
| `vn30/normalized/claim_candidates.jsonl` | 7,960 | candidates, **not labels** |
| `vn30/normalized/evidence_candidates.jsonl` | 3,786 | |
| Unknown-year documents | 196 | split=`review` |
| Cross-split duplicates | 1 | unresolved |

Counts recorded so Gate S1's "no silent zero-document success" can be evaluated
as a delta rather than an absolute.

## Gaps I am carrying into the run, stated rather than hidden

1. **R2 is satisfied by tooling, not by fail-fast.** `probe_attachment_hosts.py`
   detects an empty `attachment_domains` before a run, and the known-CDN companies
   are populated. The crawler itself still does not abort when a target resolves
   zero candidate hosts. The new legal-case crawler implements the stronger
   behaviour: a target that ends with zero artifacts and no reason code is
   reported as `PARTIAL`, and the run exits non-zero.

2. **R6 fairness is a cap, not a scheduler.** Targets are processed sequentially
   with a per-target ceiling. That prevents one entity from consuming the run
   (the Coteccons failure) but is not round-robin. Acceptable for 29 targets;
   revisit if the queue grows.

3. **ASA rulings are HTML, not PDF.** 17 targets will produce ruling pages rather
   than attachments. Their `artifact_role` must be `ruling_page`, and issue-level
   outcomes must be stored per `CLAUDE_CRAWL.md` §1 for mixed rulings.

4. **Entity separation is a data-modelling risk, not a crawl risk.** Clorox
   Australia Pty Ltd ≠ The Clorox Company; Active Super has a 1 Mar 2025 merger
   boundary into Vision Super. The schema carries `case_entity`, `reporting_entity`,
   `brand`, `relationship`; nothing downstream may collapse them.

## Authorisation to proceed

S0 passes, seven regressions hold, baseline is recorded. Collection may start
with Phase 1 (authority case packs first, per runbook ordering).

Binding constraints for the run: respect robots and rate limits, no TLS
verification downgrade (proxy shim only under `GREENSCAN_TRUST_LOCAL_PROXY=1`),
no login/paywall/anti-bot circumvention, no direct-PDF URL guessing without
discovery from an official page, and `company_has_case=true` never becomes a
document- or claim-level greenwashing label.
