from quantum_gw.agents.scorer import RiskScoringAgent
from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, VerificationResult
from quantum_gw.storage.audit import AuditLogger


def test_contradiction_has_high_risk(tmp_path):
    claim = Claim(claim_id="c", text="Chúng tôi là doanh nghiệp xanh hàng đầu.", claim_type="generic_sustainability", source_chunk_id="x", source_name="esg", is_vague=True)
    verification = VerificationResult(claim=claim, status=VerificationStatus.CONTRADICTED, rationale="conflict")
    risk = RiskScoringAgent("configs/scoring_v1.yaml", AuditLogger(tmp_path / "audit.jsonl")).run(verification)
    assert risk.risk_score >= 50
    assert risk.requires_human_review
