# Research notes integrated into V1

## Agentic AI training material

The reference training deck frames an AI agent through environment, observation/action spaces, reasoning, memory, planning, multimodal perception and self-reflection. V1 converts these concepts into bounded, auditable software components rather than unrestricted autonomy.

## Retrieval accuracy and prompt quality

Zhao et al. (2024), arXiv:2411.19463, reports that distracting documents can degrade RAG, higher recall does not guarantee correct generation, adding documents can break previously correct cases, and advanced prompts are task/model specific. V1 therefore separates retrieval and verification metrics, keeps top-k configurable, tracks distractors and starts from a plain deterministic baseline.

## Graph-based retrieval

Cahoon et al. (2025), arXiv:2503.02922, distinguishes local/fact-based and thematic/multi-document question types and studies vector, hierarchical and graph retrieval cost/performance. V1 begins with hybrid retrieval and provides explicit extension points for hierarchical or graph routes after query-type benchmarks.
