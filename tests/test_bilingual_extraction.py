"""The taxonomy must match claims in both languages the corpus contains.

The extractor's lexicons were Vietnamese-only while every adjudicated case in
data/real_cases is English. The consequences were silent: KDP-2024's claim
matched no claim_type and was dropped before verification ever saw it, and
KLM-2024's "Join us in creating a more sustainable future" was reported
is_vague=False — the most vague claim in the corpus scoring zero on the rubric
component named for that exact problem.
"""

import pytest

from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import EvidenceChunk
from quantum_gw.settings import ClaimSettings
from quantum_gw.storage.audit import AuditLogger


@pytest.fixture
def extractor(tmp_path):
    return ClaimExtractionAgent(ClaimSettings(), AuditLogger(tmp_path / "audit.jsonl"))


def extract(extractor, text):
    chunk = EvidenceChunk(
        chunk_id="c1", doc_id="d1", source_name="claim.txt",
        role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL, text=text,
    )
    return extractor.run([chunk])


@pytest.mark.parametrize(
    ("text", "expected_type", "expected_language"),
    [
        ("Testing with municipal recycling facilities validated that K-Cup pods could be "
         "effectively recycled.", "waste_and_circularity", "en"),
        ("ESG risks, opportunities and issues were considered throughout the research "
         "process via proprietary quality reviews.", "esg_process_integration", "en"),
        ("ESG was integrated across investment teams and the ESG Engine was used to make "
         "portfolio decisions.", "esg_process_integration", "en"),
        ("Join us in creating a more sustainable future.", "generic_sustainability", "en"),
        ("Công ty đã giảm 30% tổng phát thải khí nhà kính trong năm 2024 so với năm 2023.",
         "emissions_reduction", "vi"),
        ("Chúng tôi luôn hướng tới môi trường xanh và bền vững.",
         "generic_sustainability", "vi"),
    ],
)
def test_claims_extract_in_both_languages(extractor, text, expected_type, expected_language):
    claims = extract(extractor, text)
    assert claims, f"no claim extracted from: {text}"
    assert claims[0].claim_type == expected_type
    assert claims[0].language == expected_language


def test_english_vague_marketing_is_flagged_vague(extractor):
    claims = extract(extractor, "Join us in creating a more sustainable future.")
    assert claims[0].is_vague
    assert claims[0].vague_terms_matched


def test_specific_type_wins_over_the_generic_bucket(extractor):
    """"ESG" alone matches generic_sustainability; the process terms must win.

    Otherwise the claim is routed to the green-taxonomy legal issue instead of
    the disclosure one, which is the question BNY and DWS were actually charged
    under.
    """
    claims = extract(
        extractor,
        "ESG was integrated across investment teams and the ESG Engine was used to make "
        "portfolio decisions.",
    )
    assert claims[0].claim_type == "esg_process_integration"


def test_claim_with_no_green_content_is_not_extracted(extractor):
    assert extract(extractor, "The quarterly board meeting was held in Hanoi on 12 March.") == []
