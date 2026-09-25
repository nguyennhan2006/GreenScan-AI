"""The review queue (agents/prioritizer.py).

The verdict layer answers "is this claim supported"; this layer answers the
question an auditor asks first — "which of these do I open, and why". These
tests pin the properties that make the answer usable: a quantified claim about a
material metric outranks promotional prose, the queue is bounded, and the pass
states what it did not examine.
"""

from __future__ import annotations

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput

CLAIMS = (
    "Chúng tôi là doanh nghiệp xanh hàng đầu và luôn hướng tới một tương lai thân thiện với môi trường.\n"
    "Tổng lượng phát thải khí nhà kính của Tập đoàn năm 2024 là 23.474.480 tấn CO2e.\n"
    "Công ty đã tổ chức các khóa đào tạo nội bộ về bảo vệ môi trường trong năm 2024.\n"
)
EVIDENCE = "Báo cáo kiểm kê độc lập năm 2024 ghi nhận phát thải khí nhà kính của Tập đoàn."


def _run(settings):
    documents = [
        DocumentInput(name="claim.txt", text=CLAIMS, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=EVIDENCE, role=DocumentRole.EVIDENCE,
                      source_type=SourceType.EXTERNAL),
    ]
    result = OrchestratorAgent(settings).run(documents)
    by_id = {p["claim_id"]: p for p in result.priorities}
    ranked = [
        (by_id[c.claim_id]["rank"], by_id[c.claim_id], c)
        for c in result.claims if c.claim_id in by_id
    ]
    ranked.sort()
    return result, ranked


def test_every_claim_gets_a_priority_with_reasons(settings):
    result, ranked = _run(settings)
    assert len(result.priorities) == len(result.claims)
    for _, priority, _ in ranked:
        assert 0 <= priority["priority_score"] <= 100
        assert {c["name"] for c in priority["components"]} == {
            "materiality", "obligation", "evidence_gap", "anomaly",
        }
        assert priority["policy_version"] == "priority-v1"


def test_a_quantified_emissions_claim_outranks_promotional_prose(settings):
    """The order is the product; this is the ordering it must never get wrong."""
    _, ranked = _run(settings)
    rank_of = {claim.text: rank for rank, _, claim in ranked}
    quantified = next(r for text, r in rank_of.items() if "Tổng lượng phát thải" in text)
    promotional = next(r for text, r in rank_of.items() if "doanh nghiệp xanh hàng đầu" in text)
    assert quantified < promotional


def test_the_ranking_is_a_total_order_starting_at_one(settings):
    _, ranked = _run(settings)
    assert [rank for rank, _, _ in ranked] == list(range(1, len(ranked) + 1))


def test_the_pass_states_what_it_did_not_examine(settings):
    """A working paper needs the scope sentence, not only the findings."""
    result, _ = _run(settings)
    assert result.scope_note
    assert "priority-v1" in result.scope_note


def test_the_queue_is_bounded_and_never_empty(settings):
    result, ranked = _run(settings)
    queued = [p for p in result.priorities if p["in_queue"]]
    assert 0 < len(queued) <= max(5, len(ranked))


def test_percentages_do_not_count_as_magnitude(settings):
    """A share is not a quantity: 99% must not be read as a large figure."""
    from quantum_gw.agents.prioritizer import _magnitude_scale
    from quantum_gw.domain.models import Claim

    claim = Claim(
        claim_id="c", text="Tỷ lệ tái chế đạt 99% trong năm 2024.",
        claim_type="waste_and_circularity", source_chunk_id="x", source_name="doc",
    )
    assert _magnitude_scale([claim]) == {}
