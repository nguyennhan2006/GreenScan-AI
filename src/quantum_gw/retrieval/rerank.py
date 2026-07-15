from __future__ import annotations

import logging

import httpx

from quantum_gw.domain.models import RetrievedEvidence
from quantum_gw.settings import RerankerSettings

logger = logging.getLogger(__name__)


class NoopReranker:
    """Keeps the hybrid-retrieval order. Default when no reranker is installed."""

    def rerank(self, query: str, evidence: list[RetrievedEvidence], top_k: int) -> list[RetrievedEvidence]:
        return evidence[:top_k]


class BGEReranker:
    """Cross-encoder reranking via BAAI/bge-reranker-v2-m3 running local."""

    def __init__(self, model_name: str, device: str = "cuda"):
        from FlagEmbedding import FlagReranker  # heavy optional dependency

        self.model = FlagReranker(model_name, use_fp16=device == "cuda", device=device)

    def rerank(self, query: str, evidence: list[RetrievedEvidence], top_k: int) -> list[RetrievedEvidence]:
        if not evidence:
            return []
        scores = self.model.compute_score([[query, item.text] for item in evidence], normalize=True)
        if not isinstance(scores, list):
            scores = [scores]
        ranked = sorted(zip(scores, evidence, strict=True), key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:top_k]]


class TEIReranker:
    """Reranking via a text-embeddings-inference (TEI) /rerank HTTP endpoint."""

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def rerank(self, query: str, evidence: list[RetrievedEvidence], top_k: int) -> list[RetrievedEvidence]:
        if not evidence:
            return []
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/rerank",
                json={"query": query, "texts": [item.text for item in evidence]},
            )
            response.raise_for_status()
            ranking = response.json()
        ordered = sorted(ranking, key=lambda row: row["score"], reverse=True)
        return [evidence[row["index"]] for row in ordered[:top_k]]


def build_reranker(settings: RerankerSettings) -> NoopReranker | BGEReranker | TEIReranker:
    """Return the configured reranker, degrading to no-op so the app always runs."""
    if settings.provider == "local":
        try:
            return BGEReranker(settings.model, settings.device)
        except Exception as exc:  # ImportError or model load failure
            logger.warning("BGE reranker unavailable (%s); keeping retrieval order", exc)
            return NoopReranker()
    if settings.provider == "http" and settings.base_url:
        return TEIReranker(settings.base_url)
    return NoopReranker()
