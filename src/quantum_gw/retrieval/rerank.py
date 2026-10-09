from __future__ import annotations

import logging
import os
import time

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


class FPTReranker:
    """bge-reranker-v2-m3 served by FPT Marketplace (`/rerank`, Infinity format).

    The same cross-encoder as `BGEReranker`. Measured 29/09 on this project's
    CPU laptop the local one scores 0.28 pairs/s, about 108 s per claim at 30
    candidates; the endpoint answers a batch in under a second.
    """

    def __init__(self, base_url: str, api_key: str, model: str, max_chars: int = 4000,
                 timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_chars = max_chars
        self.timeout = timeout

    def rerank(self, query: str, evidence: list[RetrievedEvidence], top_k: int) -> list[RetrievedEvidence]:
        if not evidence:
            return []
        payload = {"model": self.model, "query": query,
                   "documents": [item.text[: self.max_chars] or " " for item in evidence]}
        for attempt in range(3):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(f"{self.base_url}/rerank", json=payload,
                                           headers={"Authorization": f"Bearer {self.api_key}"})
                    response.raise_for_status()
                results = response.json()["results"]
                break
            except (httpx.HTTPError, KeyError):
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        ordered = sorted(results, key=lambda row: row["relevance_score"], reverse=True)
        return [evidence[row["index"]] for row in ordered[:top_k]]


def build_reranker(
    settings: RerankerSettings, *, strict: bool = False
) -> NoopReranker | BGEReranker | TEIReranker:
    """Return the configured reranker, degrading to no-op so the app always runs.

    With `strict` (measurement), a reranker that cannot load raises instead of
    silently keeping retrieval order under a "reranked" label.
    """
    if settings.provider == "local":
        try:
            return BGEReranker(settings.model, settings.device)
        except Exception as exc:  # ImportError or model load failure
            if strict:
                raise
            logger.warning("BGE reranker unavailable (%s); keeping retrieval order", exc)
            return NoopReranker()
    if settings.provider == "http" and settings.base_url:
        return TEIReranker(settings.base_url)
    if settings.provider == "fpt":
        base, key = os.getenv("FPT_LLM_BASE_URL", ""), os.getenv("FPT_LLM_API_KEY", "")
        if base and key:
            return FPTReranker(base, key, settings.fpt_model)
        if strict:
            raise ValueError("reranker provider fpt needs FPT_LLM_BASE_URL and FPT_LLM_API_KEY")
    elif strict and settings.provider != "none":
        raise ValueError(f"reranker provider {settings.provider!r} is not usable")
    return NoopReranker()
