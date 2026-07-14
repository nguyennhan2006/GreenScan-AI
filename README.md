# AI Quantum Greenwashing Agent

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
- Optional OpenAI-compatible LLM adapter. The default path requires no external API.

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
pip install -e ".[dev]"

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

### Docker

```bash
docker compose up --build
```

## Accuracy improvement loop

Do not optimise only the final score. Measure each stage independently:

1. Parsing/OCR fidelity and table-value preservation.
2. Claim extraction precision/recall.
3. Evidence Recall@k, Precision@k and distractor rate.
4. Verification status accuracy and citation accuracy.
5. Risk-score calibration against reviewer labels.
6. RAG vs no-RAG delta and top-k sensitivity.
7. Regression results after every model, prompt, chunking or rubric change.

See [Accuracy Improvement Playbook](docs/ACCURACY_IMPROVEMENT_PLAYBOOK.md) and [Evaluation](docs/EVALUATION.md).

## Repository map

```text
src/quantum_gw/      Core package
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
