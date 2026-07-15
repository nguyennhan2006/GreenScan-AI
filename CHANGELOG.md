# Changelog

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
