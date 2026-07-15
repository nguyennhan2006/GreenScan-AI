from __future__ import annotations

import logging
from typing import Protocol

import httpx

from quantum_gw.settings import EmbeddingSettings

logger = logging.getLogger(__name__)


class DenseEmbedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class BGEM3Embedder:
    """Dense embeddings via BAAI/bge-m3 running fully local (FlagEmbedding)."""

    def __init__(self, model_name: str, device: str = "cuda", batch_size: int = 16):
        from FlagEmbedding import BGEM3FlagModel  # heavy optional dependency

        self.model = BGEM3FlagModel(model_name, use_fp16=device == "cuda", device=device)
        self.batch_size = batch_size

    def encode(self, texts: list[str]) -> list[list[float]]:
        output = self.model.encode(texts, batch_size=self.batch_size)
        return [vector.tolist() for vector in output["dense_vecs"]]


class TEIEmbedder:
    """Embeddings via a text-embeddings-inference (TEI) HTTP service."""

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def encode(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/embed", json={"inputs": texts})
            response.raise_for_status()
            return response.json()


def build_embedder(settings: EmbeddingSettings) -> DenseEmbedder | None:
    """Return the configured dense embedder, or None for the lite fallback.

    The application must keep working with zero model downloads, so any
    failure here degrades to the built-in char n-gram semantic scorer.
    """
    if settings.provider == "local":
        try:
            return BGEM3Embedder(settings.model, settings.device, settings.batch_size)
        except Exception as exc:  # ImportError or model load failure
            logger.warning("BGE-M3 unavailable (%s); falling back to lite semantic scorer", exc)
            return None
    if settings.provider == "http" and settings.base_url:
        return TEIEmbedder(settings.base_url)
    return None
