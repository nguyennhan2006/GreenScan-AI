# 04 — Crawl Runbook chi tiết

## Phase 0 — Preflight

1. Run `python scripts/validate_registry.py`.
2. Audit existing downloader/parser and confirm seven regressions in `00_CURRENT_STATE...` still pass.
3. Snapshot current DB/manifest counts.
4. Generate work queue from `legal_case_targets.yaml`; do not manually hardcode 29 loops.
5. Configure per-domain concurrency/rate limits.

## Phase 1 — Collect legal/regulatory case pack FIRST

For each target:

1. GET `case_url` from authority domain.
2. Save landing HTML/text + response metadata.
3. Extract links whose anchor/context indicates: order, judgment, court, undertaking, infringement notice, decision, ruling, complaint, press release, PDF, attachment.
4. Follow only authority/official court domains automatically. Any external link is queued for manual/allowlist review.
5. Save every artifact with `artifact_role`.
6. Parse case sections into metadata, but never discard original artifact.
7. For ASA mixed rulings, store issue-level outcome.
8. Mark exact challenged statements/product/ad description if extractable, with page/section citation.

Recommended folder:

```text
data/legal_cases/<target_id>/
  case_metadata.json
  authority/
    landing.html
    attachments/
  challenged_artifacts/
  logs/
```

## Phase 2 — Discover official corporate/fund documents

For each `report_urls` seed:

1. Parse listing page.
2. Discover pages/documents by year 2021–2025 and profile-specific keywords.
3. Prefer listing metadata over filename heuristics.
4. For JS-driven list, use existing `harvest_js_listings.py` or browser/network endpoint discovery; do not synthesize endpoints without verification.
5. Normalize final URL and follow redirects; record redirect chain.
6. Schedule download only when domain is official/allowlisted and document family matches profile.

### Keyword families

Annual/integrated:
`annual report`, `integrated report`, `annual financial report`, `10-k`, `20-f`, `financial statements`.

ESG:
`sustainability`, `ESG`, `climate`, `impact report`, `non-financial`, `TCFD`, `SASB`, `responsible investment`, `stewardship`.

Financial-product cases:
`PDS`, `product disclosure statement`, `prospectus`, `investment guide`, `exclusion`, `screen`, `responsible investment`, `holdings`.

Case artifacts:
`advertisement`, `market announcement`, `packaging`, `claim`, `campaign`, `environmental`, `net zero`, `carbon neutral`, `recycled`.

## Phase 3 — Download

For each scheduled URL:

- Send explicit `Accept` appropriate to HTML/PDF/XML and `Accept-Language`.
- Use deterministic retry/backoff.
- Stream file; enforce max bytes but allow large integrated reports with explicit threshold override.
- Validate MIME and magic bytes; reject HTML error pages saved as `.pdf`.
- Compute SHA-256 before finalizing.
- Dedup by exact hash; preserve all source aliases/provenance even when binary is shared.
- Do not overwrite existing file with same filename and different hash.

## Phase 4 — Resolve document identity/year

Use order:

1. Official listing metadata.
2. Content cover/reporting period.
3. PDF metadata.
4. URL/filename.

If conflicting, set `year_status=review` and store all candidates/reasons.

## Phase 5 — Text-layer / OCR decision

For PDF:

1. Check page count and text extraction ratio.
2. If text layer is healthy, **do not OCR**.
3. OCR only pages below text/confidence threshold or true scans.
4. Preserve original text and OCR output separately.
5. Record `ocr_used`, `ocr_pages`, OCR model/version/confidence.

## Phase 6 — Parse and candidate generation

Only after source QA:

- parse layout/table/page provenance;
- create claim candidates;
- create evidence candidates;
- never inherit legal label from company/case metadata;
- create `case_relevance_hint` separately from verdict label.

## Phase 7 — Coverage and leakage

Generate matrix for 29 targets × 2021–2025 × required doc families.

Before any annotation split:

- exact hash duplicate check;
- normalized text near-duplicate check;
- same report in multiple languages/version check;
- parent/subsidiary duplicate check;
- case attachment duplicated in corporate corpus check.

## Phase 8 — Report

Run is not complete until required reports in `10_REPORTING_REQUIREMENTS.md` are written and validated.
