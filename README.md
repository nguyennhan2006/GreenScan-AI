# AI Quantum Greenwashing Agent

## Bắt đầu nhanh (GreenScan AI)

**Windows:** nhấp đúp `GreenScan.bat`. Lần đầu tự cài (cần Python 3.11+ và Node.js 20+, mất vài phút), sau đó trình duyệt mở `http://localhost:8000`.
**macOS / Linux:** `sh start.sh`. **Docker:** `docker compose up --build` rồi mở `http://localhost:8000` (image đa tầng có cả giao diện — viết 06/10, chưa build thử).

Quy trình trên giao diện: **① Tải tài liệu** (báo cáo cần kiểm + tài liệu đối chiếu) → **② Soát theo hàng đợi** (các mục nên mở trước, kèm lý do) → **③ Giấy làm việc** (tiếng Việt, in hoặc lưu PDF).

| Chế độ (`QUANTUM_PROFILE` trong `.env`) | Cần gì | Tài liệu rời máy? |
| --- | --- | --- |
| `offline` (mặc định) | mọi laptop, 8–16 GB RAM; báo cáo ~260 trang chạy ~2 phút | Không |
| `cloud` | thêm khoá FPT AI Marketplace; mô hình chỉ đọc các cặp luật không quyết được | Có — chỉ dùng cho tài liệu công khai |
| `gpu` | máy chủ có GPU chạy vLLM | Không |

Chi tiết: [docs/04-data-ai/MODEL_ROUTING_AND_HARDWARE.md](docs/04-data-ai/MODEL_ROUTING_AND_HARDWARE.md) · Kho tri thức: [docs/08-knowledge/](docs/08-knowledge/README.md) · Trạng thái dự án: [docs/00-project/AUDIT_2026-10-06.md](docs/00-project/AUDIT_2026-10-06.md)

---

A production-oriented **Version 1 baseline** for analysing environmental and ESG claims in Vietnamese financial documents. The repository is designed to be pushed directly to GitHub, run locally without a paid LLM, and improved module-by-module as better OCR, retrieval, reranking, models and legal rules become available.

> The system estimates **greenwashing risk**. It does not make a legal finding and does not replace an auditor, lawyer, regulator or domain reviewer.

## What works in this baseline

- PDF, scanned PDF, TXT, Markdown and JSON ingestion.
- Page/block provenance, table extraction and optional Tesseract OCR (`eng+vie`).
- Vietnamese/English environmental claim extraction with a deterministic heuristic baseline.
- Hybrid retrieval: BM25-style lexical score + character n-gram semantic score.
- Claim–evidence verification with explicit statuses:
  `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE`.
- Versioned 0–100 risk rubric and human-review flags.
- Seven quality gates, append-only audit log and reproducibility manifest.
- CLI, FastAPI service, Docker, tests, golden-set evaluation and GitHub Actions.
- **Local-first model gateway** (v1.1): one `LLMProvider` interface over local
  vLLM/Ollama plus optional FPT Marketplace, Gemini, OpenAI, Anthropic and
  OpenRouter fallbacks. The default path requires no external API and no keys.

## Architecture

```text
Input documents
      │
      ▼
Document Intake ──► provenance-preserving chunks/tables/OCR
      │
      ▼
Claim Extraction ─► normalized green-claim schema
      │
      ▼
Hybrid Retrieval ─► ranked candidate evidence + citations
      │
      ▼
Verification ─────► support/contradiction/insufficient evidence
      │
      ▼
Risk Scoring ─────► component scores + severity
      │
      ▼
Reviewer Gates ───► release / pending human review
      │
      ▼
JSON + Markdown evidence pack + audit trail
```

Version 1 intentionally uses **one orchestrator with specialised modules**. Multi-agent autonomy should only be introduced after controlled benchmarks show a measurable benefit.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev,crawl]"      # crawl = deps cho tools/crawl_*.py và test smoke

quantum-agent demo
quantum-agent evaluate
```

The demo writes a complete evidence pack under `.quantum/runs/<run_id>/`.

### Analyse your own files

```bash
quantum-agent analyze \
  path/to/esg-report.pdf \
  path/to/financial-report.pdf \
  path/to/legal-notice.pdf \
  --roles claim_source,evidence,evidence
```

### Start the API

```bash
quantum-agent serve --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the interactive API.

### Web UI (React + Tailwind)

```bash
cd frontend
npm install
npm run dev            # expects the API on http://localhost:8000
```

Open `http://localhost:5173`. The v2 UI (sidebar workbench) covers: new
analysis wizard (upload/paste → configure → run), overview, claim list, claim
detail (5 attributes → evidence → numeric check → legal context → risk
breakdown → reviewer decision), source-page viewer with highlight, review
queue, export (JSON/Markdown/manifest/audit), saved-run history (reopen a run
without re-running the pipeline), legal library and settings. Screen map and
design rules: `docs/05-ui/PRODUCTION_UI_SPEC_2026-09-20.md`; what changed
from the mockups and why: `docs/05-ui/UI_V2_REVIEW_2026-09-20.md`.
Set `VITE_API_URL` if the API
runs on a different host/port. CORS origins for the API are configured with
the `QUANTUM_CORS_ORIGINS` environment variable
(default `http://localhost:5173,http://127.0.0.1:5173`).

### Docker

```bash
docker compose up --build
```

### Local-first model gateway (v1.1)

All model access goes through a single gateway; business modules never call a
concrete model API. Configure via `.env` (see `.env.example` — the app starts
normally with every cloud key empty):

```bash
# Development with Ollama
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=qwen3:8b

# Server with vLLM (never expose port 8000 to the Internet)
vllm serve Qwen/Qwen3-8B --host 0.0.0.0 --port 8000 --max-model-len 32768
```

Task-level routing lives in `configs/routing.yaml`; the locked V1.1 model set
in `configs/models_v1_1.yaml` (Qwen3-8B primary, BGE-M3 embeddings,
bge-reranker-v2-m3). Check provider status at `GET /v1/gateway/health`.
Full stack (vLLM + embedding + reranker + postgres/redis/minio):

```bash
docker compose -f docker-compose.local-first.yml --profile gpu up --build
```

Design rationale: [ADR 0002](docs/decisions/0002-local-first-model-gateway.md).

## Accuracy improvement loop

Do not optimise only the final score. Measure each stage independently:

1. Parsing/OCR fidelity and table-value preservation.
2. Claim extraction precision/recall.
3. Evidence Recall@k, Precision@k and distractor rate.
4. Verification status accuracy and citation accuracy.
5. Risk-score calibration against reviewer labels.
6. RAG vs no-RAG delta and top-k sensitivity.
7. Regression results after every model, prompt, chunking or rubric change.

See [Accuracy Improvement Playbook](docs/04-data-ai/ACCURACY_IMPROVEMENT_PLAYBOOK.md) and [Evaluation](docs/04-data-ai/EVALUATION.md).

## Repository map

```text
src/quantum_gw/      Core package
frontend/            React + Tailwind web UI (Vite)
configs/             Versioned taxonomy, pipeline and scoring rules
data/sample/         Runnable synthetic demonstration
data/golden/         Small acceptance-test seed set
docs/                Architecture, criteria, contracts, security and roadmap
tests/               Unit, security and end-to-end tests
.github/workflows/   CI for linting, tests and package build
```

## Important limitations

- The included heuristics are a transparent baseline, not a state-of-the-art Vietnamese ESG model.
- OCR quality depends on scan quality and installed language packs.
- The legal taxonomy is a starter knowledge base and must be reviewed/versioned by qualified experts.
- Missing evidence is not automatically treated as greenwashing.
- High/critical results and legal conflicts require human approval.

## References incorporated into the design

- Zhao et al. (2024), *Towards Understanding Retrieval Accuracy and Prompt Quality in RAG Systems*.
- Cahoon et al. (2025), *Optimizing Open-Domain Question Answering with Graph-Based Retrieval Augmented Generation*.
- *Tập huấn AIC 2026 – Buổi 3: Kiến trúc Agentic AI và ứng dụng LLM trong hệ thống tìm kiếm*.

See [Research Notes](docs/research/README.md).
