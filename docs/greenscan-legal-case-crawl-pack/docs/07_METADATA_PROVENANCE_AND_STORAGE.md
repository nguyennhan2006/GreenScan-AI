# 07 — Metadata, provenance và storage

## Document metadata tối thiểu

```json
{
  "doc_id": "sha256-derived-or-stable-id",
  "target_id": "INT-SHELL-UK",
  "case_entity": "Shell UK Ltd",
  "reporting_entity": "Shell plc",
  "brand": "Shell",
  "relationship": "subsidiary_of_parent",
  "source_url": "https://...",
  "source_domain": "...",
  "source_type": "authority|corporate|filing|product",
  "doc_family": "annual|integrated|sustainability|pds|policy|ruling|order|ad|...",
  "year": 2024,
  "year_status": "resolved|review",
  "published_date": null,
  "accessed_at": "ISO-8601",
  "http_status": 200,
  "content_type": "application/pdf",
  "sha256": "...",
  "bytes": 0,
  "redirect_chain": [],
  "license_or_terms_status": "public_official|review_required|...",
  "text_layer_ratio": null,
  "ocr_used": false,
  "crawler_version": "git-sha",
  "parser_version": "git-sha"
}
```

## Provenance chain

```text
source URL
  -> HTTP response/download manifest
  -> immutable original artifact (sha256)
  -> page/block/table extraction
  -> claim candidate
  -> evidence candidate
  -> legal-case relevance link
  -> reviewer annotation
  -> adjudicated gold label
```

Không skip từ company case trực tiếp sang gold label.

## Folder layout đề xuất

```text
data/
  legal_cases/<target_id>/...
  corporate/<target_id>/<year>/...
  derived/<target_id>/...
  annotations/...
reports/...
```

## Filename

`<target_id>__<year-or-unknown>__<doc_family>__<short_sha256>.<ext>`

Không dùng title thô làm filename vì ký tự Unicode/URL/path length dễ phá pipeline.
