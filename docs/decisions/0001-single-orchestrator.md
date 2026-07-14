# ADR-0001: Single orchestrator before multi-agent autonomy

**Status:** Accepted for V1

## Context

The project needs traceable errors, low operational complexity and clear stage benchmarks. Multi-agent systems add coordination failures, duplicated context, cost and harder reproducibility.

## Decision

Use one orchestrator with specialised deterministic modules. Modules expose replaceable interfaces and produce explicit artefacts. Introduce autonomous sub-agents only when a controlled benchmark demonstrates better accuracy, cost or maintainability.

## Consequences

Positive: simpler testing, reproducibility, security and failure attribution. Negative: less flexible dynamic planning in early versions.
