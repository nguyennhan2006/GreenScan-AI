# Changelog

## Unreleased - 2026-09-20 (verdict truth layer + UI v2)

Verdict path (all measured defects from `docs/00-project/CORE_FEATURE_TEST_REPORT_2026-09-20.md`):

- `utils.text.parse_numbers`: scope/standard/clause labels ("phạm vi 1 và 2", "Scope 3",
  "ISO 14064-1", "Điều 5", "21/2025") are no longer measurements; Vietnamese digit
  groups (`1.200.000`, `1,2`), multipliers (`triệu`, `tỷ`) and canonical units
  (`tCO2e`, `MWh`, `m3`, `%`) are parsed. `normalize_for_match` folds `đ → d`.
- Verifier: figures are compared only with the same canonical unit, only from
  sentences that mention the claim's metric, and only across the same GHG scope
  boundary (`emission_scopes`); overlap is measured on accent-preserving content
  tokens (no function words, no years); direction words are matched on whole
  tokens; vague claims and unquantified future pledges cannot reach
  PARTIALLY_SUPPORTED on similarity alone; UNSUPPORTED needs topical overlap.
- Stance cues (`stance-cues-v2`): whole-word matching on the text's own
  orthography (no more "thiếu" firing on "thiêu kết"); a cue must sit in a
  sentence sharing a topic token with the claim, or -- for an authority -- be a
  ruling on the subject's statements; `benign` phrases ("không có sự cố") are
  stripped first; negated support cues ("không xác nhận") do not count; bare
  "không có"/"chưa có" removed from the refutation list (absence ≠ refutation).
- Verifier: SUPPORTED requires a supporting passage from a document other than the
  claim's own (a report restating its own table is PARTIAL); support cues must share a
  word (syllable bigram) with the claim's text; "phù hợp với"/"kiểm toán" dropped as cues.
- Claim extractor: headings, TOC lines, section labels, ALL-CAPS lines and bare
  generic-sustainability sentences are rejected and tallied in the audit log.
- Intake: passages are ≤ 3 sentences within one paragraph (`chunk_size_chars: 600`,
  `max_sentences_per_chunk: 3`) so a stance or a figure belongs to one topic.
- Parser: text uploads derive `doc_id` the same way the document store does, so
  the evidence deep-link resolves for `.txt/.md/.json` as well as PDF.
- Regression gate: `tests/test_verdict_traps.py` (17 traps), `tests/test_document_store_ids.py`.

Product:

- Saved runs: `GET /v1/runs`, `GET /v1/runs/{id}`, `PUT /v1/runs/{id}/label`,
  `GET /v1/runs/{id}/export?format=json|md|manifest|audit` (`storage/runs.py`, read-only over `runs_dir`).
- `GET /v1/legal/corpus`: registered instruments with text-acquisition status.
- Web UI v2 (`frontend/`): sidebar workbench with intake wizard, overview, claim list,
  claim detail in audit order (attributes → evidence → numeric check → legal context →
  risk breakdown → decision), source viewer with info panel, review queue, export,
  run history, legal library, settings. Spec: `docs/05-ui/PRODUCTION_UI_SPEC_2026-09-20.md`.

## 1.1.0 - 2026-07-15 (local-first)

- Model Gateway: single `LLMProvider` interface (`generate`, `healthcheck`, `model_info`);
  business modules never call a concrete model API directly.
- Provider registry: local (vLLM/OpenAI-compatible), Ollama, FPT Marketplace
  (openai_compatible now, fpt_native reserved), Gemini, OpenAI, Anthropic, OpenRouter.
- Task-level routing policy (`configs/routing.yaml`) with global fallback order;
  quantitative verification stays deterministic (Python, never an LLM).
- The application starts and the full pipeline runs with every cloud key empty.
- Retrieval: Reciprocal Rank Fusion ordering (BM25 + semantic), candidate_k=30,
  final top_k=5; optional BGE-M3 dense embeddings and bge-reranker-v2-m3
  cross-encoder (local FlagEmbedding or TEI HTTP), graceful lite fallback.
- `.env.example` covers all providers with empty keys; `configs/models_v1_1.yaml`
  locks the V1.1 model set (Qwen3-8B primary, Qwen3-14B optional verifier).
- `GET /v1/gateway/health` reports provider configuration/liveness.
- `docker-compose.local-first.yml`: api, vllm, embedding, reranker, postgres,
  redis, minio (worker slot reserved for the async queue milestone).
- Removed legacy `providers/llm.py` (`QUANTUM_LLM_*` env vars → `LOCAL_LLM_*`).

## 0.1.0 - 2026-07-14

- Initial GitHub-ready baseline.
- Deterministic claim extraction, hybrid retrieval, verification and risk scoring.
- PDF/OCR ingestion, quality gates, evidence packs, API, CLI, tests and evaluation.
