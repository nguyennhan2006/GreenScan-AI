# 08 — Data quality & release gates

## Gate S0 — Registry

- exactly 29 unique target IDs;
- all `case_url` are HTTPS and authority domains;
- every target has `case_entity`, `reporting_entity`, `profile`, `level`, qualifier;
- every target has >=1 official reporting seed.

## Gate S1 — Source acquisition

- no silent zero-document success;
- failed sources have reason codes;
- no HTML error masquerading as PDF;
- SHA-256 for 100% artifacts;
- source URL and access timestamp for 100% artifacts.

## Gate S2 — Coverage

- all 29 targets have case-pack status;
- 2021–2025 coverage matrix exists;
- missing years have explicit reason, not blank cells;
- case-specific document family attempted according to profile.

## Gate S3 — Parsing

- year resolved or review-queued;
- text-layer/OCR decision logged;
- page-level provenance retained;
- table extraction cannot discard original page coordinates.

## Gate S4 — Leakage

Before annotation/train split:

- 0 exact cross-split duplicate;
- near duplicate report versions grouped;
- same challenged advertisement/ruling not repeated across train and test;
- translations of same report are same group unless evaluation intentionally tests multilingual transfer.

## Gate S5 — Annotation

- raw candidates never counted as labels;
- at least two reviewers for gold target set where planned;
- disagreements adjudicated;
- legal qualifier shown to annotator but authority identity may be blinded in experiments designed to avoid authority leakage.

## Gate S6 — Release

Release report states:

- source coverage;
- missing/blocked sources;
- legal/license status;
- duplicate/leakage results;
- annotation counts;
- known limitations.
