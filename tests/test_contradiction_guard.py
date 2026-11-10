"""Contradiction guard (05/11/2026): the claim's own document and the company's own
prose do not contradict a claim; independent documents and rulings still do.

Cases are the two failure families found on 146 real sentences (GS-Eval v2):
two figures about different objects inside one report, and a refutation cue read
out of the company's own text.
"""
from quantum_gw.agents.verifier import VerificationAgent
from quantum_gw.domain.enums import SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence
from quantum_gw.storage.audit import AuditLogger


def _agent(settings, tmp_path, legacy=False):
    config = settings.verification.model_copy(update={"self_evidence_can_contradict": legacy})
    return VerificationAgent(config, AuditLogger(tmp_path / "audit.jsonl"))


def _claim(text, doc="sr-2025", **kw):
    return Claim(claim_id="c", text=text, claim_type="emissions_reduction", source_chunk_id="x",
                 source_name="bctn", source_doc_id=doc, **kw)


def _evidence(text, doc, source_type=SourceType.INTERNAL, score=0.8):
    return RetrievedEvidence(chunk_id="e", source_name="doc", source_type=source_type, text=text,
                             score=score, citation="doc page 1", doc_id=doc)


CLAIM_CO2 = "Việc sử dụng bê tông khoáng hóa CO2 năm 2025 tiết giảm được 1.936 tấn CO2."
OTHER_OBJECT = "Việc ưu tiên sử dụng gạch không nung năm 2025 góp phần tiết giảm được 926 tấn CO2."


def test_same_document_figures_do_not_contradict(settings, tmp_path):
    claim = _claim(CLAIM_CO2, values=[1936.0])
    result = _agent(settings, tmp_path).run(claim, [_evidence(OTHER_OBJECT, "sr-2025")])
    assert result.status != VerificationStatus.CONTRADICTED
    item = result.evidence[0]
    assert item.relation == "CONTEXT"
    assert "cùng tài liệu" in item.relation_reason


def test_legacy_flag_restores_same_document_contradiction(settings, tmp_path):
    claim = _claim(CLAIM_CO2, values=[1936.0])
    result = _agent(settings, tmp_path, legacy=True).run(claim, [_evidence(OTHER_OBJECT, "sr-2025")])
    assert result.status == VerificationStatus.CONTRADICTED


def test_other_document_figures_still_contradict(settings, tmp_path):
    claim = _claim("Công ty giảm 30% phát thải năm 2024.", direction="decrease", values=[30.0])
    evidence = _evidence("Phát thải tăng 12% trong năm 2024.", "monitoring", SourceType.ENVIRONMENTAL)
    result = _agent(settings, tmp_path).run(claim, [evidence])
    assert result.status == VerificationStatus.CONTRADICTED


def test_company_prose_negation_is_not_a_refutation(settings, tmp_path):
    claim = _claim("DHG bảo mật thông tin khách hàng và chăm sóc khách hàng bền vững.", doc="sr")
    evidence = _evidence(
        "Hệ thống chăm sóc khách hàng vận hành 24/7. Không ghi nhận trường hợp nào vi phạm liên quan "
        "đến quyền bảo mật thông tin khách hàng.", "ar")
    result = _agent(settings, tmp_path).run(claim, [evidence])
    assert result.status != VerificationStatus.CONTRADICTED


def test_gri_index_listing_a_decree_is_not_a_refutation(settings, tmp_path):
    claim = _claim("Công ty tuân thủ Luật Bảo vệ môi trường trong mọi dự án.", doc="sr")
    evidence = _evidence(
        "Nghị định 45/2022/NĐ-CP quy định về xử phạt vi phạm hành chính trong lĩnh vực bảo vệ môi trường. "
        "Luật Bảo vệ môi trường 2020.", "ar", SourceType.FINANCIAL)
    result = _agent(settings, tmp_path).run(claim, [evidence])
    assert result.status != VerificationStatus.CONTRADICTED


def test_independent_ruling_still_contradicts(settings, tmp_path):
    claim = _claim("Join us in creating a more sustainable future with sustainable aviation fuel.", doc="ad")
    evidence = _evidence(
        "The court found 15 of 19 assessed environmental statements misleading, including vague claims "
        "and an overly positive presentation of sustainable aviation fuel.", "judgment", SourceType.LEGAL)
    result = _agent(settings, tmp_path).run(claim, [evidence])
    assert result.status == VerificationStatus.CONTRADICTED
