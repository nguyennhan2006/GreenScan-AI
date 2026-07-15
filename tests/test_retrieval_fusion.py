from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import Claim, EvidenceChunk, RetrievedEvidence
from quantum_gw.retrieval.hybrid import HybridRetriever
from quantum_gw.retrieval.rerank import NoopReranker, build_reranker
from quantum_gw.settings import RerankerSettings


def _chunk(chunk_id: str, text: str) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        doc_id=chunk_id,
        source_name=chunk_id,
        role=DocumentRole.EVIDENCE,
        source_type=SourceType.ENVIRONMENTAL,
        text=text,
    )


def _claim(text: str) -> Claim:
    return Claim(
        claim_id="c",
        text=text,
        claim_type="emissions_reduction",
        source_chunk_id="x",
        source_name="esg",
    )


def test_rrf_fusion_keeps_relevant_chunk_first(settings):
    settings.retrieval.fusion = "rrf"
    chunks = [
        _chunk("a", "Phát thải CO2 năm 2024 giảm 12% so với năm 2023."),
        _chunk("b", "Doanh thu quý 4 năm 2024 tăng trưởng ổn định."),
        _chunk("c", "Chính sách nhân sự và đào tạo nội bộ."),
    ]
    result = HybridRetriever(chunks, settings.retrieval).search(_claim("Công ty giảm 30% phát thải CO2 năm 2024."))
    assert result
    assert result[0].chunk_id == "a"


def test_weighted_and_rrf_return_same_candidate_set(settings):
    chunks = [
        _chunk("a", "Phát thải CO2 năm 2024 giảm 12%."),
        _chunk("b", "Tiêu thụ điện năng lượng tái tạo đạt 40%."),
    ]
    claim = _claim("Công ty giảm phát thải CO2 năm 2024.")
    settings.retrieval.fusion = "weighted"
    weighted_ids = {e.chunk_id for e in HybridRetriever(chunks, settings.retrieval).search(claim)}
    settings.retrieval.fusion = "rrf"
    rrf_ids = {e.chunk_id for e in HybridRetriever(chunks, settings.retrieval).search(claim)}
    assert weighted_ids == rrf_ids


def test_reranker_defaults_to_noop_and_truncates():
    reranker = build_reranker(RerankerSettings(provider="none"))
    assert isinstance(reranker, NoopReranker)
    evidence = [
        RetrievedEvidence(
            chunk_id=str(i),
            source_name="s",
            source_type=SourceType.ENVIRONMENTAL,
            text="t",
            score=1.0 - i * 0.1,
            citation="s (document)",
        )
        for i in range(10)
    ]
    assert len(reranker.rerank("q", evidence, top_k=5)) == 5


def test_reranker_local_falls_back_gracefully_without_flagembedding():
    reranker = build_reranker(RerankerSettings(provider="local", model="BAAI/bge-reranker-v2-m3"))
    assert reranker.rerank("q", [], top_k=5) == []
