# Accuracy improvement playbook

## 1. Establish frozen baselines

Record input set hash, parser, OCR, chunker, retriever, model, prompt, top-k, rubric and code commit. Store stage metrics and example failures.

## 2. Improve one stage at a time

- **OCR first:** a wrong number cannot be repaired downstream.
- **Extraction second:** optimise claim boundaries and structured fields.
- **Retrieval third:** maximise evidence recall while controlling distractors.
- **Verification fourth:** calibrate status rules and deterministic calculations.
- **Scoring last:** calibrate severity only after status labels are reliable.

## 3. Retrieval experiments

Run controlled grids over chunk size, overlap, lexical/dense weights, candidate-k, reranker and final top-k. Track both newly solved cases and previously correct cases that become wrong. More context is not automatically better.

## 4. Query routing

Classify queries/claims as:

- local/factual/single-document;
- multi-hop across a small set of documents;
- thematic/portfolio-level synthesis.

Use vector/hybrid retrieval for local queries, hierarchical retrieval for long single documents, and consider graph/global retrieval only for multi-document thematic tasks after cost-benefit tests.

## 5. Prompt/model experiments

Start with a plain structured prompt. Advanced reasoning or self-refinement must beat the baseline by dataset and model, not by intuition. Keep output schema checks and a fallback path.

## 6. Calibration and review

Use two independent reviewers for difficult cases, record disagreement, adjudicate and update rule/model error clusters. Calibrate score bands against observed reviewer action rather than arbitrary thresholds.

## 7. Release policy

A candidate release must:

- pass mandatory gates;
- avoid material regression on any high-risk slice;
- document latency and cost changes;
- include a rollback path and migration note.
