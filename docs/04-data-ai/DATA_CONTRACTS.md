# Data contracts

> **Tầng dữ liệu (raw · clean · extract) ở [DATA_LAYERS.md](DATA_LAYERS.md)** — contract
> `data-layers-v1`, nguồn sự thật `src/quantum_gw/data/layers.py`, JSON Schema ở
> `schemas/data/`. Tài liệu này mô tả các object nghiệp vụ chạy trong pipeline.

## DocumentInput

A document must have either `path` or `text`, plus:

- `role`: `claim_source`, `evidence` or `reference`.
- `source_type`: `internal`, `financial`, `environmental`, `legal`, `external`, `standard`.
- optional language and metadata.

## Claim

Key fields: text, type, source chunk/page, metric, direction, values, units, period, baseline, future commitment, vagueness and confidence.

## VerificationResult

- one normalized claim;
- explicit status;
- rationale;
- ranked evidence with citation and retrieval score;
- deterministic computed values;
- warnings and verifier version.

## RiskAssessment

A 0–100 score where a higher value means higher risk, component breakdown, severity, rubric version and human-review flag.

## Versioning rules

- Additive optional fields: minor schema revision.
- Changed meaning, enum or score interpretation: new schema/rubric version.
- Keep old evaluation fixtures for migration and regression tests.
