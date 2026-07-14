from quantum_gw.agents.verifier import VerificationAgent
from quantum_gw.domain.enums import SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence
from quantum_gw.storage.audit import AuditLogger


def test_detects_numeric_contradiction(settings, tmp_path):
    claim = Claim(claim_id="c", text="Công ty giảm 30% phát thải năm 2024.", claim_type="emissions_reduction", source_chunk_id="x", source_name="esg", direction="decrease", values=[30.0])
    evidence = [RetrievedEvidence(chunk_id="e", source_name="ops", source_type=SourceType.ENVIRONMENTAL, text="Phát thải tăng 12% trong năm 2024.", score=0.8, citation="ops page 1")]
    result = VerificationAgent(settings.verification, AuditLogger(tmp_path / "audit.jsonl")).run(claim, evidence)
    assert result.status == VerificationStatus.CONTRADICTED
