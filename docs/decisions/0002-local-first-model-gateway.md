# ADR 0002 — Local-first Model Gateway (v1.1.0)

Status: accepted — 2026-07-15

## Decision

```text
Customer
   │
   ▼
AI-QUANTUM Backend
   │
   ▼
Model Gateway
   ├── Local vLLM       ← default
   ├── Local Ollama     ← personal/dev machines
   ├── FPT Marketplace  ← key left empty
   ├── Gemini API       ← key left empty
   ├── OpenAI API       ← key left empty
   └── Anthropic API    ← key left empty
```

1. **Local is the default.** The app must start and the full deterministic
   pipeline must run with every cloud key empty.
2. **No module calls a concrete model API.** Everything goes through
   `quantum_gw.providers.LLMProvider` (`generate(messages, response_schema)`,
   `healthcheck()`, `model_info()`) resolved by `ModelGateway`.
3. **FPT Marketplace is the first-priority cloud fallback** when a key exists.
   Two formats are prepared: `openai_compatible` (works today via the shared
   client) and `fpt_native` (adapter skeleton; finish from official docs
   without touching the pipeline). International providers stay empty-keyed.
4. **Ollama for development, vLLM for servers.** `LOCAL_LLM_PROVIDER`
   switches the local slot. vLLM port 8000 is never exposed to the Internet.
5. **Routing is a policy, not if/else.** `configs/routing.yaml` maps task
   types to primary/fallback providers; `deterministic` marks tasks that must
   be solved in Python (all quantitative verification), `none` disables
   fallback. Global order: `LLM_FALLBACK_ORDER`.
6. **Retrieval is fully local.** BM25 + dense candidates (30) → RRF merge →
   BGE reranker → metadata filtering → top 3–5 evidence. Dense model:
   BAAI/bge-m3; reranker: BAAI/bge-reranker-v2-m3; both optional with a
   zero-download lite fallback so the baseline keeps running anywhere.
7. **Python owns quantitative logic** (units, percent change, scopes,
   thresholds, gates, risk aggregation). The LLM only reads language, extracts
   claims, analyses semantic consistency and writes explanations.
8. **Human review is mandatory** for material cases or low confidence.
9. **Fine-tuning is not step one.** Order: prompts + JSON schema →
   deterministic validation → RAG → few-shot → benchmark → LoRA only for
   repeated failures with ≥500–1000 reviewer-confirmed claims.

## Model set (locked for V1.1)

See `configs/models_v1_1.yaml`: Qwen3-8B (non-thinking) primary; Qwen3-14B
optional verifier for high-risk/contradiction/legal cases; BGE-M3 embeddings;
bge-reranker-v2-m3; FPT as disabled cloud fallback slot.

Routing rule of thumb:

```text
simple claim                          → Qwen3-8B
claim with clear numbers              → Python calculator
contradiction/legal/complex scope     → larger verifier model
low confidence                        → human review
```

## Hardware ladder (estimates — benchmark on real machines)

| Hardware          | Model              | Role                    |
| ----------------- | ------------------ | ----------------------- |
| CPU, 16–32 GB RAM | Qwen 3–4B quantized| light dev, classification |
| GPU 8–12 GB       | Qwen3-8B Q4        | extraction, report      |
| GPU 16 GB         | Qwen3-8B full      | main pipeline           |
| GPU 24 GB         | Qwen3-14B quantized| better verifier         |
| GPU 48 GB         | 14B/32B quantized  | batch, multi-user       |
| Multi-GPU         | 32B+               | high-risk verifier      |

Upgrade order: run 8B → benchmark errors on 100 real claims → identify 8B
failure cases → try 14B on that failure set → buy hardware only if the gain
is large enough.

## Consequences

- Switching local ↔ FPT ↔ any provider is configuration, not code.
- New deployment file `docker-compose.local-first.yml` (api, vllm, embedding,
  reranker, postgres, redis, minio; worker reserved for the queue milestone).
- Legacy `QUANTUM_LLM_*` variables replaced by `LOCAL_LLM_*`/provider blocks.
- Not decided here: 9Router-style subscription backends (explicitly rejected
  for customer traffic), async worker implementation, fpt_native schema.
