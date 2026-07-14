from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus
from quantum_gw.domain.models import DocumentInput


def test_end_to_end_creates_evidence_pack(settings):
    documents = [
        DocumentInput(name="esg.txt", text="Công ty đã giảm 30% phát thải trong năm 2024 so với năm 2023.", role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="ops.txt", text="Phát thải năm 2024 tăng 12% so với năm 2023.", role=DocumentRole.EVIDENCE, source_type=SourceType.ENVIRONMENTAL),
    ]
    result = OrchestratorAgent(settings).run(documents)
    assert result.claims
    assert result.verifications[0].status == VerificationStatus.CONTRADICTED
    assert (settings.runs_dir and result.output_directory)
