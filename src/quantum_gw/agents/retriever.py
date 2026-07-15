from __future__ import annotations

from quantum_gw.domain.models import Claim, EvidenceChunk, RetrievedEvidence
from quantum_gw.retrieval.embeddings import build_embedder
from quantum_gw.retrieval.hybrid import HybridRetriever
from quantum_gw.retrieval.rerank import build_reranker
from quantum_gw.settings import AppSettings, RetrievalSettings
from quantum_gw.storage.audit import AuditLogger


class EvidenceRetrievalAgent:
    """Hybrid retrieval (BM25 + dense/lite semantic, RRF fusion) then reranking.

    Pipeline: candidates (top candidate_k) -> reranker -> final top_k evidence.
    Only the final evidence reaches the verifier/LLM, never the full candidate set.
    """

    def __init__(
        self,
        chunks: list[EvidenceChunk],
        settings: AppSettings | RetrievalSettings,
        audit: AuditLogger,
    ):
        if isinstance(settings, RetrievalSettings):  # direct unit-test usage
            retrieval, embedder, reranker = settings, None, None
        else:
            retrieval = settings.retrieval
            embedder = build_embedder(settings.embedding)
            reranker = build_reranker(settings.reranker)
        self.retrieval = retrieval
        self.retriever = HybridRetriever(chunks, retrieval, embedder=embedder)
        self.reranker = reranker
        self.audit = audit

    def run(self, claim: Claim) -> list[RetrievedEvidence]:
        if self.reranker is None:
            evidence = self.retriever.search(claim)
        else:
            candidates = self.retriever.search(claim, top_k=self.retrieval.candidate_k)
            evidence = self.reranker.rerank(claim.text, candidates, self.retrieval.top_k)
        self.audit.write(
            "evidence_retrieved",
            {"claim_id": claim.claim_id, "count": len(evidence), "scores": [e.score for e in evidence]},
        )
        return evidence
