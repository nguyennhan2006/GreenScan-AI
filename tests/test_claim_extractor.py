from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import EvidenceChunk
from quantum_gw.storage.audit import AuditLogger


def test_extracts_quantitative_claim(settings, tmp_path):
    chunk = EvidenceChunk(
        chunk_id="c1",
        doc_id="d1",
        source_name="esg.txt",
        role=DocumentRole.CLAIM_SOURCE,
        source_type=SourceType.INTERNAL,
        text="Công ty đã giảm 30% phát thải khí nhà kính trong năm 2024 so với năm 2023.",
    )
    agent = ClaimExtractionAgent(settings.claim_extraction, AuditLogger(tmp_path / "audit.jsonl"))
    claims = agent.run([chunk])
    assert len(claims) == 1
    assert claims[0].claim_type == "emissions_reduction"
    assert claims[0].direction == "decrease"
    assert 30.0 in claims[0].values
