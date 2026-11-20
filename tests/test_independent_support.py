"""Support guard (11/11/2026, flag): the company's own documents agreeing with a claim
is not independent support.

On GS-Eval v2 (05/11) every SUPPORTED verdict was wrong: the annual report or
another report of the same company restated the sentence. With
`support_requires_independent_source` on, only a legal, external or standard
source makes a claim SUPPORTED; the company's own echo stays PARTIALLY_SUPPORTED
and the reason says what is missing. Off by default until the registered reruns
(independent_support_v1) are read.
"""
from quantum_gw.agents.verifier import INDEPENDENT_SOURCE_TYPES, VerificationAgent
from quantum_gw.domain.enums import SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.studio.document import INDEPENDENT_SOURCES

CLAIM = "Tổng phát thải khí nhà kính năm 2024 của Tập đoàn là 23.474.480 tCO2e."
ECHO = "Năm 2024, tổng phát thải khí nhà kính của Tập đoàn là 23.474.480 tCO2e."


def _agent(settings, tmp_path, guard):
    config = settings.verification.model_copy(update={"support_requires_independent_source": guard})
    return VerificationAgent(config, AuditLogger(tmp_path / "audit.jsonl"))


def _claim():
    return Claim(claim_id="c", text=CLAIM, claim_type="emissions", source_chunk_id="x", source_name="bcptbv",
                 source_doc_id="sr-2025", metric="emissions", values=[23474480.0], units=["tco2e"], period="2024")


def _evidence(source_type, doc="ar-2024"):
    return RetrievedEvidence(chunk_id="e", source_name="doc", source_type=source_type, text=ECHO, score=0.8,
                             citation="doc trang 39", doc_id=doc)


def test_default_is_on(settings):
    """On since 15/11/2026 (expert review; GS-Eval v2 replay: false SUPPORTED 5 -> 0)."""
    assert settings.verification.support_requires_independent_source is True


def test_company_echo_supports_while_the_flag_is_off(settings, tmp_path):
    result = _agent(settings, tmp_path, guard=False).run(_claim(), [_evidence(SourceType.FINANCIAL)])
    assert result.status == VerificationStatus.SUPPORTED


def test_company_echo_is_partial_with_the_flag_on(settings, tmp_path):
    for own in (SourceType.INTERNAL, SourceType.FINANCIAL, SourceType.ENVIRONMENTAL):
        result = _agent(settings, tmp_path, guard=True).run(_claim(), [_evidence(own)])
        assert result.status == VerificationStatus.PARTIALLY_SUPPORTED, own
        assert "chính doanh nghiệp" in result.rationale and "nguồn độc lập" in result.rationale
        # The stance of the passage itself is unchanged: the figures do agree.
        assert result.evidence[0].relation == "SUPPORTS"


def test_independent_source_still_supports_with_the_flag_on(settings, tmp_path):
    for independent in (SourceType.EXTERNAL, SourceType.LEGAL, SourceType.STANDARD):
        result = _agent(settings, tmp_path, guard=True).run(_claim(), [_evidence(independent, doc="regulator")])
        assert result.status == VerificationStatus.SUPPORTED, independent


def test_independent_passage_wins_over_company_echo(settings, tmp_path):
    evidence = [_evidence(SourceType.FINANCIAL), _evidence(SourceType.EXTERNAL, doc="regulator")]
    result = _agent(settings, tmp_path, guard=True).run(_claim(), evidence)
    assert result.status == VerificationStatus.SUPPORTED


def test_studio_and_verifier_share_one_definition():
    assert INDEPENDENT_SOURCES == INDEPENDENT_SOURCE_TYPES == {"legal", "external", "standard"}
