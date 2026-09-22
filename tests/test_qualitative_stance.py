"""Qualitative refutation — the failure that made the whole pipeline score 0/4.

Every adjudicated case in data/real_cases is contradicted without a single pair
of conflicting numbers: by omission, by a coverage gap, by a control gap, or by
a court holding a statement misleading. The verifier could only reach
CONTRADICTED through arithmetic or a direction flip, so it reported
INSUFFICIENT_EVIDENCE for three of them and PARTIALLY_SUPPORTED for the fourth —
counting a regulator's finding that DWS "lacked formalized controls" as partial
support for DWS's own claim.
"""

import pytest

from quantum_gw.agents.verifier import VerificationAgent
from quantum_gw.domain.enums import SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence
from quantum_gw.settings import VerificationSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.verification.stance import CONTEXT, CONTRADICTS, StanceLexicon, qualitative_stance


@pytest.fixture
def verifier(tmp_path):
    return VerificationAgent(VerificationSettings(), AuditLogger(tmp_path / "audit.jsonl"))


def claim(text, **kw):
    return Claim(
        claim_id="c", text=text, claim_type=kw.pop("claim_type", "esg_process_integration"),
        source_chunk_id="src", source_name="claim.txt", **kw
    )


def evidence(text, *, source_type=SourceType.LEGAL, score=0.30, chunk_id="e1"):
    return RetrievedEvidence(
        chunk_id=chunk_id, source_name=f"{chunk_id}.txt", source_type=source_type,
        text=text, score=score, citation=f"{chunk_id}.txt (document)",
    )


# ---------- the four adjudicated shapes ----------

@pytest.mark.parametrize(
    ("case", "claim_text", "evidence_text"),
    [
        (
            "KDP-2024 omission",
            "Testing with municipal recycling facilities validated that K-Cup pods "
            "could be effectively recycled.",
            "The SEC order found the 2019 and 2020 statements incomplete and inaccurate "
            "because the negative feedback was omitted.",
        ),
        (
            "BNY-2022 coverage gap",
            "ESG risks, opportunities and issues were considered throughout the research "
            "process via proprietary quality reviews.",
            "67 of 185 investments in one Overlay Fund lacked an ESG quality-review score "
            "at the relevant time, nearly 25% of net assets.",
        ),
        (
            "DWS-2023 control gap",
            "ESG was integrated across investment teams and the ESG Engine was used to "
            "make portfolio decisions.",
            "The order states DWS lacked formalized controls to verify use of the ESG "
            "Engine and documentation of material ESG factors.",
        ),
        (
            "KLM-2024 court finding",
            "Join us in creating a more sustainable future.",
            "The court found 15 of 19 assessed environmental statements misleading, "
            "including vague claims and overly positive presentation of SAF and reforestation.",
        ),
    ],
)
def test_qualitative_refutation_reaches_contradicted(verifier, case, claim_text, evidence_text):
    result = verifier.run(claim(claim_text), [evidence(evidence_text)])
    assert result.status == VerificationStatus.CONTRADICTED, case
    assert result.evidence[0].relation == CONTRADICTS, case
    assert result.evidence[0].relation_method == "qualitative_cue", case


def test_refuting_evidence_is_never_read_as_support(verifier):
    """The DWS regression: a refutation must not raise the claim's status."""
    result = verifier.run(
        claim("ESG was integrated across investment teams and the ESG Engine was used "
              "to make portfolio decisions."),
        [evidence("The order states DWS lacked formalized controls to verify use of the "
                  "ESG Engine and documentation of material ESG factors.")],
    )
    assert result.status is not VerificationStatus.PARTIALLY_SUPPORTED
    assert result.status is not VerificationStatus.SUPPORTED


# ---------- guards ----------

def test_neutral_corporate_context_is_not_a_refutation(verifier):
    """KLM-EV-002 is labelled CONTEXT_ONLY in the pack and must stay context."""
    result = verifier.run(
        claim("Join us in creating a more sustainable future."),
        [evidence(
            "The annual report says KLM continued the Fly Responsibly campaign and set "
            "targets for further CO2 and noise reduction.",
            source_type=SourceType.EXTERNAL,
        )],
    )
    assert result.evidence[0].relation == CONTEXT


def test_bare_negation_does_not_refute():
    """"không trình bày" is an absence of disclosure, not a contradiction.

    Cue phrases are multi-word precisely so that the commonest word in either
    language cannot flip a verdict on its own.
    """
    signal = qualitative_stance(
        "Báo cáo tài chính không trình bày chỉ tiêu môi trường.",
        source_type="financial",
        overlap=0.5,
        minimum_overlap=0.2,
        lexicon=StanceLexicon(),
    )
    assert signal is None


def test_unrelated_passage_with_a_cue_is_ignored():
    """A refutation cue in a passage about something else must not count."""
    signal = qualitative_stance(
        "The canteen refurbishment was inadequate and did not meet the schedule.",
        source_type="internal",
        overlap=0.01,
        minimum_overlap=0.2,
        lexicon=StanceLexicon(),
    )
    assert signal is None


def test_authority_bypasses_the_overlap_floor():
    """BNY's refutation shares almost no vocabulary with the claim it refutes."""
    signal = qualitative_stance(
        "67 of 185 investments in one Overlay Fund lacked an ESG quality-review score.",
        source_type="legal",
        overlap=0.0,
        minimum_overlap=0.2,
        lexicon=StanceLexicon(),
    )
    assert signal is not None
    assert signal.relation == CONTRADICTS
    assert signal.authoritative


def test_authority_bypass_does_not_extend_to_clearing_a_claim():
    """An authority may refute off-topic; it may not vouch off-topic.

    A false refutation surfaces to a reviewer as a flagged item. A false
    clearance surfaces as nothing at all, so support keeps the overlap floor.
    """
    off_topic_support = qualitative_stance(
        "The SEC order confirmed the firm's cybersecurity controls were audited.",
        source_type="legal",
        overlap=0.0,
        minimum_overlap=0.2,
        lexicon=StanceLexicon(),
    )
    assert off_topic_support is None


def test_numeric_agreement_outranks_a_cue(verifier):
    """Deterministic arithmetic decides a passage before any lexicon does."""
    result = verifier.run(
        claim("Tỷ lệ năng lượng tái tạo đạt 50% trong năm 2024.", claim_type="renewable_energy"),
        [evidence("Chứng chỉ năng lượng xác nhận năng lượng tái tạo chiếm 50% trong năm 2024.",
                  source_type=SourceType.EXTERNAL)],
    )
    assert result.evidence[0].relation_method == "numeric"
    assert result.status == VerificationStatus.SUPPORTED
