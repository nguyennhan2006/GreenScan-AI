"""The retrieval threshold must not decide that evidence does not exist.

`minimum_score` dropped weak candidates outright, which merged two answers that
need different responses: "nothing in this corpus speaks to the claim" and
"nothing in this corpus *looked like* the claim". KLM-2024 is the second — the
claim shares no content word with the court finding that held it misleading, so
every passage scored below the cut and the claim came back INSUFFICIENT_EVIDENCE
with an adjudicated refutation sitting one rank below the line.

The floor returns those candidates marked `below_threshold`. The asymmetry it
creates is deliberate: a weak passage may carry a refutation from an authority,
but it may never establish support.
"""

from quantum_gw.agents.verifier import VerificationAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, EvidenceChunk
from quantum_gw.retrieval.hybrid import HybridRetriever
from quantum_gw.settings import RetrievalSettings, VerificationSettings
from quantum_gw.storage.audit import AuditLogger

KLM_CLAIM = "Join us in creating a more sustainable future."
KLM_FINDING = (
    "The court found 15 of 19 assessed environmental statements misleading, including "
    "vague claims and overly positive presentation of SAF and reforestation."
)


def chunk(chunk_id, text, source_type=SourceType.LEGAL):
    return EvidenceChunk(
        chunk_id=chunk_id, doc_id="d", source_name=f"{chunk_id}.txt",
        role=DocumentRole.EVIDENCE, source_type=source_type, text=text,
    )


def claim(text=KLM_CLAIM):
    return Claim(
        claim_id="c", text=text, claim_type="generic_sustainability",
        source_chunk_id="src", source_name="claim.txt",
    )


# A threshold nothing can clear, so the floor is what is under test rather than
# whatever score this particular pair happens to produce.
UNREACHABLE = RetrievalSettings(minimum_score=0.9, floor_k=3)


def test_evidence_below_the_threshold_is_still_returned():
    results = HybridRetriever([chunk("e1", KLM_FINDING)], UNREACHABLE).search(claim())
    assert results, "an adjudicated finding must not be filtered out for looking dissimilar"
    assert results[0].below_threshold, "and it must be marked as having scored below the cut"


def test_floor_is_disabled_when_set_to_zero():
    settings = RetrievalSettings(minimum_score=0.9, floor_k=0)
    assert HybridRetriever([chunk("e1", KLM_FINDING)], settings).search(claim()) == []


def test_floor_returns_at_most_floor_k_weak_candidates():
    settings = RetrievalSettings(minimum_score=0.9, floor_k=2, top_k=10)
    chunks = [chunk(f"e{i}", f"{KLM_FINDING} Variant {i}.") for i in range(5)]
    assert len(HybridRetriever(chunks, settings).search(claim())) == 2


def test_passing_candidates_are_not_marked_below_threshold():
    text = "Phát thải năm 2024 tăng 12% lên 112000 tCO2e."
    results = HybridRetriever(
        [chunk("e1", text, SourceType.ENVIRONMENTAL)], RetrievalSettings()
    ).search(claim("Công ty giảm 30% phát thải năm 2024."))
    assert results and not results[0].below_threshold


def test_weak_evidence_can_refute_but_never_support(tmp_path):
    """The asymmetry, end to end through retrieval and verification."""
    verifier = VerificationAgent(VerificationSettings(), AuditLogger(tmp_path / "a.jsonl"))
    retriever = HybridRetriever([chunk("e1", KLM_FINDING)], UNREACHABLE)

    refuted = verifier.run(claim(), retriever.search(claim()))
    assert refuted.evidence[0].below_threshold
    assert refuted.status == VerificationStatus.CONTRADICTED

    # Same weak similarity, but a passage that merely agrees in tone: it cannot
    # lift the claim to SUPPORTED or PARTIALLY_SUPPORTED on that score alone.
    bland = HybridRetriever(
        [chunk("e2", "The airline continued its responsible flying campaign last year.",
               SourceType.EXTERNAL)],
        UNREACHABLE,
    )
    weak = verifier.run(claim(), bland.search(claim()))
    assert weak.evidence[0].below_threshold
    assert weak.status == VerificationStatus.INSUFFICIENT_EVIDENCE
