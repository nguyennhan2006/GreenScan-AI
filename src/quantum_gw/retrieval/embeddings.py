from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
import time
from array import array
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Protocol

import httpx

from quantum_gw.settings import EmbeddingSettings

logger = logging.getLogger(__name__)


class DenseEmbedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class BGEM3Embedder:
    """Dense embeddings via BAAI/bge-m3 running fully local (FlagEmbedding)."""

    def __init__(self, model_name: str, device: str = "cuda", batch_size: int = 16,
                 max_length: int = 512):
        from FlagEmbedding import BGEM3FlagModel  # heavy optional dependency

        self.model = BGEM3FlagModel(model_name, use_fp16=device == "cuda", device=device)
        self.batch_size = batch_size
        # BGE-M3 accepts 8,192 tokens; on a CPU that length is the whole cost.
        # A passage is a few sentences, so 512 loses nothing there.
        self.max_length = max_length

    def encode(self, texts: list[str]) -> list[list[float]]:
        output = self.model.encode(texts, batch_size=self.batch_size, max_length=self.max_length)
        return [vector.tolist() for vector in output["dense_vecs"]]


class OpenAICompatibleEmbedder:
    """Embeddings from an OpenAI-compatible `/embeddings` endpoint (FPT Marketplace).

    Measured 29/09: BGE-M3 on this project's CPU laptop encodes 0.49 pages/s,
    eight hours for the gold companies' libraries. FPT serves
    `Vietnamese_Embedding` (per its model card, BAAI/bge-m3 fine-tuned for
    Vietnamese, 1,024 dimensions) at about half a second per batch.
    """

    def __init__(self, base_url: str, api_key: str, model: str, batch_size: int = 32,
                 workers: int = 4, max_chars: int = 6000, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self.workers = workers
        # A page can exceed the model's 2,048 tokens; the head of a page is what
        # retrieval keys on, and a request that is rejected helps nobody.
        self.max_chars = max_chars
        self.timeout = timeout

    def _batch(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self.model, "input": [t[: self.max_chars] or " " for t in texts]}
        for attempt in range(3):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(f"{self.base_url}/embeddings", json=payload,
                                           headers={"Authorization": f"Bearer {self.api_key}"})
                    response.raise_for_status()
                data = sorted(response.json()["data"], key=lambda row: row["index"])
                return [row["embedding"] for row in data]
            except (httpx.HTTPError, KeyError):
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("unreachable")

    def encode(self, texts: list[str]) -> list[list[float]]:
        batches = [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            results = list(pool.map(self._batch, batches))
        return [vector for batch in results for vector in batch]


class CachedEmbedder:
    """Vectors kept on disk by (model, text), so a passage is encoded once.

    BGE-M3 on a CPU is the slowest step of a run. Re-running the same report,
    or measuring on the gold set again after a change elsewhere, must not pay
    it twice. Misses are encoded in slices and committed as they go, so a long
    warm-up that is interrupted resumes where it stopped.
    """

    SLICE = 128

    def __init__(self, inner: DenseEmbedder, model_name: str, cache_dir: str | Path):
        self.inner = inner
        self.model_name = model_name
        path = Path(cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path / "vectors.sqlite3", check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS v (k TEXT PRIMARY KEY, vec BLOB)")
        self.hits = 0
        self.misses = 0

    def _key(self, text: str) -> str:
        return hashlib.sha1(f"{self.model_name}\x00{text}".encode()).hexdigest()

    def missing(self, texts: list[str]) -> int:
        """How many of these would have to be encoded now (for a cost check before a run)."""
        keys = list({self._key(t) for t in texts})
        found = 0
        for start in range(0, len(keys), 500):
            part = keys[start:start + 500]
            found += self.db.execute(
                f"SELECT COUNT(*) FROM v WHERE k IN ({','.join('?' * len(part))})", part
            ).fetchone()[0]
        return len(keys) - found

    def encode(self, texts: list[str]) -> list[list[float]]:
        keys = [self._key(t) for t in texts]
        found: dict[str, list[float]] = {}
        for start in range(0, len(keys), 500):
            part = keys[start:start + 500]
            rows = self.db.execute(
                f"SELECT k, vec FROM v WHERE k IN ({','.join('?' * len(part))})", part
            ).fetchall()
            found.update({k: array("f", blob).tolist() for k, blob in rows})
        missing = [i for i, k in enumerate(keys) if k not in found]
        for start in range(0, len(missing), self.SLICE):
            part = missing[start:start + self.SLICE]
            vectors = self.inner.encode([texts[i] for i in part])
            self.db.executemany(
                "INSERT OR REPLACE INTO v VALUES (?, ?)",
                [(keys[i], array("f", vec).tobytes()) for i, vec in zip(part, vectors, strict=True)],
            )
            self.db.commit()
            for i, vec in zip(part, vectors, strict=True):
                found[keys[i]] = list(vec)
        self.hits += len(texts) - len(missing)
        self.misses += len(missing)
        return [found[k] for k in keys]


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


def build_embedder(settings: EmbeddingSettings, *, strict: bool = False) -> DenseEmbedder | None:
    """Return the configured dense embedder, or None for the lite fallback.

    The application must keep working with zero model downloads, so any
    failure here degrades to the built-in char n-gram semantic scorer. A
    measurement must not: with `strict`, a failure raises, so a table labelled
    "BGE-M3" can never have been computed by the lite scorer.
    """
    embedder: DenseEmbedder | None = None
    if settings.provider == "local":
        try:
            embedder = BGEM3Embedder(settings.model, settings.device, settings.batch_size,
                                     settings.max_length)
        except Exception as exc:  # ImportError or model load failure
            if strict:
                raise
            logger.warning("BGE-M3 unavailable (%s); falling back to lite semantic scorer", exc)
            return None
    elif settings.provider == "http" and settings.base_url:
        embedder = TEIEmbedder(settings.base_url)
    elif settings.provider == "fpt":
        base, key = os.getenv("FPT_LLM_BASE_URL", ""), os.getenv("FPT_LLM_API_KEY", "")
        if base and key:
            embedder = OpenAICompatibleEmbedder(base, key, settings.fpt_model)
        elif strict:
            raise ValueError("embedding provider fpt needs FPT_LLM_BASE_URL and FPT_LLM_API_KEY")
        else:
            logger.warning("FPT embedding not configured; falling back to lite semantic scorer")
    elif strict and settings.provider != "lite":
        raise ValueError(f"embedding provider {settings.provider!r} is not usable")
    if embedder is not None and settings.cache_dir:
        name = f"fpt:{settings.fpt_model}" if settings.provider == "fpt" else settings.model
        return CachedEmbedder(embedder, name, settings.cache_dir)
    return embedder
