# Evaluation

## Stage metrics

### Parsing/OCR

- character/word error rate on scan samples;
- numeric value accuracy;
- unit, period and table-cell preservation;
- page/block citation accuracy.

### Claim extraction

- exact and semantic precision, recall and F1;
- claim-type macro F1;
- metric/value/unit/period field accuracy;
- false positives on legal or explanatory text.

### Retrieval

- Evidence Recall@k;
- Evidence Precision@k;
- MRR / nDCG when graded relevance exists;
- distractor rate;
- source diversity;
- top-k sensitivity.

### Verification

- five-class macro F1;
- contradiction recall;
- numeric comparison accuracy;
- scope/period mismatch accuracy;
- abstention precision for insufficient evidence.

### End-to-end

- claim-level citation coverage and citation correctness;
- risk-severity agreement with reviewers;
- release-gate false pass rate;
- RAG vs no-RAG delta;
- latency and cost per document/claim.

## Dataset split

Keep `train/dev/test` separated by company and reporting period where possible. Do not tune prompts or thresholds on the held-out test set. Add hard negatives, missing evidence, contradictions, prompt injection and tool failures.

## Running the included seed evaluation

```bash
quantum-agent evaluate
```

The included set is intentionally small and only validates repository behaviour. Replace it with at least 50–100 adjudicated claims for the first pilot and expand by error cluster.
