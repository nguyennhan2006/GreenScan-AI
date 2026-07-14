from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import Claim, EvidenceChunk
from quantum_gw.retrieval.hybrid import HybridRetriever


def test_retrieval_prefers_matching_metric(settings):
    chunks = [
        EvidenceChunk(chunk_id="a", doc_id="1", source_name="a", role=DocumentRole.EVIDENCE, source_type=SourceType.ENVIRONMENTAL, text="Phát thải năm 2024 tăng 12% lên 112000 tCO2e."),
        EvidenceChunk(chunk_id="b", doc_id="2", source_name="b", role=DocumentRole.EVIDENCE, source_type=SourceType.FINANCIAL, text="Doanh thu năm 2024 tăng 5%."),
    ]
    claim = Claim(claim_id="c", text="Công ty giảm 30% phát thải năm 2024.", claim_type="emissions_reduction", source_chunk_id="x", source_name="esg")
    result = HybridRetriever(chunks, settings.retrieval).search(claim)
    assert result
    assert result[0].chunk_id == "a"
