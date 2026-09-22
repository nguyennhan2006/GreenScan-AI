# 10 — Reporting requirements after every crawl run

## `COLLECTION_REPORT_<date>.md`

Must contain:

1. run ID, git commit, config hash;
2. targets attempted/succeeded/partial/blocked;
3. new documents, duplicates, rejected files, bytes;
4. by-authority counts;
5. by-company/year/doc-family coverage;
6. text-layer vs OCR stats;
7. unknown-year count;
8. legal case-pack completeness;
9. top failure categories;
10. next prioritized actions.

## `coverage_matrix.csv`

Columns:

`target_id, year, required_family, status, doc_count, source_url, notes`

## `failure_queue.csv`

`target_id, url, stage, error_class, http_status, retryable, attempts, next_action`

## `leakage_report.json`

At minimum:

```json
{
  "exact_duplicate_groups": [],
  "cross_split_exact": [],
  "near_duplicate_groups": [],
  "same_case_artifact_cross_split": [],
  "same_report_translation_cross_split": []
}
```

## `source_health.json`

Per domain: request count, success/4xx/5xx, rate-limit events, robots status, median latency, zero-result anomalies.

## Stop conditions

Crawler must return non-zero or `PARTIAL` status when:

- registry invalid;
- all targets return zero new/existing confirmed docs without explicit no-change explanation;
- manifest/database count mismatch;
- JSONL record loss;
- checksum missing;
- cross-split duplicate introduced into release split.
