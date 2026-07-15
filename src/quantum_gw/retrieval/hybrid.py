from __future__ import annotations

import math
from collections import Counter

from quantum_gw.domain.models import Claim, EvidenceChunk, RetrievedEvidence
from quantum_gw.settings import RetrievalSettings
from quantum_gw.utils.security import contains_prompt_injection
from quantum_gw.utils.text import tokenize

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None


class HybridRetriever:
    def __init__(
        self,
        chunks: list[EvidenceChunk],
        settings: RetrievalSettings,
        embedder=None,
    ):
        self.chunks = chunks
        self.settings = settings
        self.tokenized = [tokenize(chunk.text) for chunk in chunks]
        self.doc_freq = Counter()
        for tokens in self.tokenized:
            self.doc_freq.update(set(tokens))
        self.avg_len = sum(map(len, self.tokenized)) / max(1, len(self.tokenized))
        self.vectorizer = None
        self.matrix = None
        self.embedder = embedder
        self.dense_vectors: list[list[float]] | None = None
        if embedder is not None and chunks:
            self.dense_vectors = embedder.encode([chunk.text for chunk in chunks])
        elif TfidfVectorizer is not None and chunks:
            self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
            self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in chunks])

    def search(self, claim: Claim, top_k: int | None = None) -> list[RetrievedEvidence]:
        query_tokens = tokenize(claim.text)
        lexical = [self._bm25(query_tokens, index) for index in range(len(self.chunks))]
        semantic = self._semantic_scores(claim.text)
        combined = []
        for index, chunk in enumerate(self.chunks):
            if self.settings.exclude_same_chunk and chunk.chunk_id == claim.source_chunk_id:
                continue
            l_score = lexical[index]
            s_score = semantic[index]
            score = self.settings.lexical_weight * l_score + self.settings.semantic_weight * s_score
            # Evidence and external/legal sources get a small prior; claim-source restatements do not dominate.
            if chunk.role.value != "claim_source":
                score += 0.025
            if chunk.source_type.value in {"legal", "external", "financial", "environmental"}:
                score += 0.015
            if score >= self.settings.minimum_score:
                combined.append((score, l_score, s_score, chunk))
        if self.settings.fusion == "rrf":
            combined = self._rrf_order(combined)
        else:
            combined.sort(key=lambda item: item[0], reverse=True)
        selected = combined[: top_k or self.settings.top_k]
        return [
            RetrievedEvidence(
                chunk_id=chunk.chunk_id,
                source_name=chunk.source_name,
                source_type=chunk.source_type,
                text=chunk.text,
                page=chunk.page,
                score=round(score, 6),
                lexical_score=round(l_score, 6),
                semantic_score=round(s_score, 6),
                citation=chunk.citation,
                suspicious_instruction=contains_prompt_injection(chunk.text),
            )
            for score, l_score, s_score, chunk in selected
        ]

    def _rrf_order(self, combined: list[tuple]) -> list[tuple]:
        """Reciprocal Rank Fusion over the lexical and semantic rankings.

        Only the candidate ORDER changes; the reported `score` stays the
        weighted combination so downstream verification thresholds are stable.
        """
        if not combined:
            return combined
        k = self.settings.rrf_k
        by_lexical = sorted(combined, key=lambda item: item[1], reverse=True)
        by_semantic = sorted(combined, key=lambda item: item[2], reverse=True)
        rrf: dict[int, float] = {}
        for ranking in (by_lexical, by_semantic):
            for rank, item in enumerate(ranking, start=1):
                rrf[id(item)] = rrf.get(id(item), 0.0) + 1.0 / (k + rank)
        return sorted(combined, key=lambda item: (rrf[id(item)], item[0]), reverse=True)

    def _bm25(self, query_tokens: list[str], index: int) -> float:
        tokens = self.tokenized[index]
        if not tokens or not query_tokens:
            return 0.0
        counts = Counter(tokens)
        score = 0.0
        n_docs = max(1, len(self.chunks))
        k1, b = 1.5, 0.75
        for token in set(query_tokens):
            df = self.doc_freq.get(token, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            tf = counts.get(token, 0)
            denom = tf + k1 * (1 - b + b * len(tokens) / max(1, self.avg_len))
            if denom:
                score += idf * (tf * (k1 + 1) / denom)
        return score / (score + 3.0) if score > 0 else 0.0

    def _semantic_scores(self, query: str) -> list[float]:
        if self.dense_vectors is not None and self.embedder is not None:
            query_vector = self.embedder.encode([query])[0]
            return [self._cosine(query_vector, vector) for vector in self.dense_vectors]
        if self.vectorizer is None or self.matrix is None or cosine_similarity is None:
            query_set = set(tokenize(query))
            return [
                len(query_set & set(tokens)) / max(1, len(query_set | set(tokens)))
                for tokens in self.tokenized
            ]
        query_vector = self.vectorizer.transform([query])
        raw = cosine_similarity(query_vector, self.matrix)[0]
        return [float(value) for value in raw]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if not norm_a or not norm_b:
            return 0.0
        return dot / (norm_a * norm_b)
