# Three-person team workflow

## Research Lead

Owns problem definition, taxonomy, legal/standards sources, user needs and ground-truth policy. Reviews changes under `configs/taxonomy_vi.yaml`, legal rules and dataset annotation guidance.

## Reviewer / QA

Owns acceptance criteria, golden/regression sets, meeting notes, reviewer experience and release gates. Challenges unsupported conclusions and tracks deadlines.

## Product Owner / Technical Lead

Owns architecture, implementation, model/tool selection, CI, deployment, metrics and progress reporting. Ensures every change has a measurable hypothesis and rollback path.

## Pull-request ownership

| Change | Required reviewers |
|---|---|
| Parsing/OCR/retrieval/model code | Technical Lead + QA |
| Taxonomy/legal/evidence standard | Research Lead + QA |
| Scoring thresholds/severity | All three |
| UI/report wording | QA + Research Lead |
| Security/deployment | Technical Lead + QA |
