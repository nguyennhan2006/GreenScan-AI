# Architecture

## Design decision

Version 1 uses a **single orchestrator plus specialised deterministic modules**. This keeps failure attribution, testing and cost control straightforward. Agent autonomy is bounded by an explicit plan and quality gates.

## Agent environment

- **Environment:** ESG reports, annual reports, financial statements, environmental data, legal documents, external disclosures and versioned rules.
- **Observation space:** parsed blocks, tables, page coordinates, document metadata, retrieval scores, prior tool results and reviewer decisions.
- **Action space:** parse/OCR, classify, retrieve, rerank, calculate, compare, cite, abstain, request review and generate structured reports.
- **Memory:** append-only audit events, semantic document index and versioned procedural rules.
- **Planning:** a fixed safe plan in V1; dynamic branching can be introduced only with benchmark coverage.
- **Self-reflection:** quality-gate checks, contradiction detection and release blocking rather than unrestricted model introspection.

## Components

1. `DocumentIntakeAgent`: file validation, PDF blocks, tables, OCR and provenance.
2. `ClaimExtractionAgent`: green-claim candidates and normalized attributes.
3. `EvidenceRetrievalAgent`: lexical + semantic retrieval with source priors.
4. `VerificationAgent`: numeric comparison, direction conflicts and evidence status.
5. `RiskScoringAgent`: versioned component rubric.
6. `ReviewerAgent`: seven gates and human-review routing.
7. `ReportingAgent`: machine-readable result and reviewer evidence pack.

## Replacement boundaries

- `parsers/`: swap PyMuPDF/Tesseract for Nanonets-OCR-s, PaddleOCR or a document-layout service.
- `retrieval/`: add embeddings, vector stores, rerankers, GraphRAG or hierarchical retrieval.
- `providers/`: add private/on-premise model providers.
- `configs/`: update taxonomy, score weights and legal rules without editing domain code.
- `evaluation/`: compare components through golden and regression sets.

## Data flow and trust boundaries

Raw files are immutable inputs. Parsed text is untrusted. Document instructions are never allowed to alter system policy. Derived claims, evidence and scores remain separate and linked by IDs. Every releaseable conclusion must have provenance.
