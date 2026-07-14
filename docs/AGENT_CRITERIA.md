# AI Agent implementation criteria

## Core principles

1. Evidence before conclusion.
2. Separate `UNSUPPORTED`, `INSUFFICIENT_EVIDENCE` and `CONTRADICTED`.
3. Human review for high/critical risk and legal conflict.
4. Preserve raw input, extraction, inference and score as separate layers.
5. Keep OCR, retriever, reranker, LLM and rubric replaceable.
6. Use deterministic tools for calculations.
7. Treat all document content as untrusted data.

## 100-point engineering scorecard

| Group | Weight | Acceptance focus |
|---|---:|---|
| Input and provenance | 10 | File identity, source, period, page/block traceability |
| Parsing/OCR/table fidelity | 12 | Values, units, rows and page positions preserved |
| Claim extraction | 10 | Precision/recall and schema completeness |
| Retrieval | 14 | Recall@k, Precision@k, distractor rate, source diversity |
| Verification | 14 | Status accuracy, deterministic calculations, scope matching |
| Groundedness/citations | 12 | Claim-level citations and no unsupported conclusions |
| Safety/governance | 10 | Prompt injection, access, privacy, review controls |
| Reproducibility/observability | 8 | Config/model/rubric versions, hashes and audit log |
| Cost/latency/resilience | 5 | Budget, timeout, graceful degradation |
| Reviewer experience | 5 | Evidence pack, override reason and actionable gaps |

## Quality gates

- **G0 Data admissibility:** readable input, valid source and provenance.
- **G1 Extraction fidelity:** values retain unit, period, scope and location.
- **G2 Retrieval:** evidence above threshold or explicit insufficient evidence.
- **G3 Verification:** calculations run in code/tool, not mental arithmetic by an LLM.
- **G4 Citation:** every decisive statement has a working document location.
- **G5 Risk review:** high/critical and legal conflicts require approval.
- **G6 Reproducibility:** input/config/version/seed manifest enables reruns.

## Per-run rubric

Maximum 21 points; normal pass is at least 16 with no zero item. High-risk cases require at least 18 and reviewer approval.

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Input admissibility | invalid | partial | valid | validated + provenance |
| Claim extraction | wrong | incomplete | mostly correct | schema-complete |
| Retrieval | no evidence | weak | relevant | relevant + diverse + low distractor |
| Verification | unsupported reasoning | partial | correct | deterministic + scope-aware |
| Citation | missing | coarse | document/page | exact block/table |
| Risk explanation | opaque | generic | component based | actionable and calibrated |
| Safety/review | unsafe | warning only | controlled | controlled + auditable |

## MVP completion

- Text and scanned PDF processing.
- Claim schema with source location.
- Internal and independent/legal evidence channels.
- Five verification statuses.
- Versioned component risk score.
- Reviewer evidence pack, reasoned override and audit log.
- Golden-set gates with no critical source-free hallucination.
