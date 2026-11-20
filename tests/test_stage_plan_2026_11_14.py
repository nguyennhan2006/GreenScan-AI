"""Stage plan, 14/11/2026 evening: absolute-share-v1, stance-cues-v3 rule layer,
internal-inconsistency-v1, comparison-policy-v3 (segment) and the label-number guard.
"""
from __future__ import annotations

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.assist.guards import new_numbers
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus as V
from quantum_gw.domain.models import DocumentInput
from quantum_gw.feedback.queue import raise_queue
from quantum_gw.verification.absolute import absolute_conflict, allocated_share, amounts
from quantum_gw.verification.numeric_facts import eligibility, facts_in
from quantum_gw.utils.text import content_bigrams

A2 = "Nguồn vốn từ trái phiếu xanh được sử dụng hoàn toàn cho các dự án đủ điều kiện xanh."
A2_EVIDENCE = (
    "Khoản thu từ trái phiếu xanh là 500 tỷ đồng. Báo cáo phân bổ vốn xác định 320 tỷ đồng đã giải ngân "
    "cho dự án điện mặt trời; 180 tỷ đồng đang nằm trong tài khoản tiền gửi và chưa được phân bổ tại ngày "
    "kết thúc kỳ báo cáo."
)


def _run(settings, claim, evidence, source_type=SourceType.FINANCIAL):
    return OrchestratorAgent(settings).run([
        DocumentInput(name="claim.txt", text=claim, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=evidence, role=DocumentRole.EVIDENCE, source_type=source_type),
    ])


def test_amount_roles_and_share():
    roles = [(a["role"], a["value"]) for a in amounts(A2_EVIDENCE)]
    assert roles == [("total", 500e9), ("used", 320e9), ("unused", 180e9)]
    found = allocated_share(A2, A2_EVIDENCE)
    assert found["share_pct"] == 64.0 and "320 tỷ đồng" in found["formula"] and "500 tỷ đồng" in found["formula"]


def test_share_needs_every_piece():
    assert allocated_share("Vốn trái phiếu xanh được sử dụng cho dự án xanh.", A2_EVIDENCE) is None   # not absolute
    assert allocated_share("Toàn bộ nhà máy đạt ISO 14001.", A2_EVIDENCE) is None                       # no instrument
    assert allocated_share(A2, "Khoản thu từ tín dụng xanh là 500 tỷ đồng; 320 tỷ đồng đã giải ngân.") is None  # other instrument
    assert allocated_share(A2, "Trái phiếu xanh: 320 tỷ đồng đã giải ngân.") is None                     # no total
    assert allocated_share(A2, "Trái phiếu xanh phát hành 500 tỷ đồng; 600 tỷ đồng đã giải ngân.") is None  # parts > whole
    full = allocated_share(A2, "Trái phiếu xanh phát hành 1.200 tỷ đồng; 1.200 tỷ đồng đã được giải ngân.")
    assert full["share_pct"] == 100.0


def test_case_a2_is_contradicted_with_the_arithmetic(settings):
    result = _run(settings, A2, A2_EVIDENCE)
    v = result.verifications[0]
    assert v.status == V.CONTRADICTED
    assert "64%" in v.rationale and "100%" in v.rationale
    assert "absolute_claim_conflict" in v.review_flags


def test_share_check_can_be_switched_off(settings):
    settings.verification.absolute_share_check = False
    assert _run(settings, A2, A2_EVIDENCE).verifications[0].status != V.CONTRADICTED


def test_fully_used_proceeds_are_not_contradicted(settings):
    evidence = "Khoản thu từ trái phiếu xanh là 500 tỷ đồng, 500 tỷ đồng đã được giải ngân hết cho dự án điện mặt trời."
    assert _run(settings, A2, evidence).verifications[0].status != V.CONTRADICTED


def test_absolute_conflict_needs_a_strong_cue_about_the_claim():
    claim = "Toàn bộ vốn tín dụng xanh đã được giải ngân cho dự án năng lượng tái tạo."
    yes = absolute_conflict(claim, "Một phần vốn tín dụng xanh chưa được giải ngân tại cuối kỳ.", content_bigrams(claim), content_bigrams)
    assert yes and yes["partial"] == "chưa được giải ngân"
    # weak cue ("giai đoạn đầu"): replayed on real reports, 0 of 17 such flags were right
    assert absolute_conflict(claim, "Vốn tín dụng xanh ở giai đoạn đầu được dùng cho dự án.", content_bigrams(claim), content_bigrams) is None
    # strong cue in a sentence about something else
    assert absolute_conflict(claim, "Nhà máy xử lý nước thải chưa hoàn thành.", content_bigrams(claim), content_bigrams) is None


def test_absolute_conflict_caps_at_partial_and_raises_the_queue(settings):
    claim = "Toàn bộ vốn tín dụng xanh năm 2024 đã được giải ngân cho dự án năng lượng tái tạo."
    evidence = "Năm 2024, vốn tín dụng xanh cho dự án năng lượng tái tạo chưa được giải ngân hết."
    result = _run(settings, claim, evidence, SourceType.EXTERNAL)
    v = result.verifications[0]
    assert v.status != V.CONTRADICTED
    assert "absolute_claim_conflict" in v.review_flags
    queued = {p["item_id"]: p for p in result.priorities if p["item_type"] == "claim"}
    assert queued[v.claim.claim_id]["in_queue"]
    assert "flag:absolute_claim_conflict" in queued[v.claim.claim_id].get("raised_by", [])


def test_segment_blocks_steel_against_agriculture():
    steel = facts_in("Tỷ lệ tái chế chất thải của nhóm thép đạt 99%.")[0]
    farm = facts_in("Nhóm nông nghiệp tái chế 100% phân chăn nuôi.")[0]
    group = facts_in("Tỷ lệ tái chế chất thải toàn Tập đoàn đạt 99%.")[0]
    assert eligibility(steel, farm) == ("NOT_COMPARABLE", "different_segment")
    assert eligibility(steel, group)[0] == "COMPARABLE"   # unknown never blocks


def test_internal_inconsistency_off_by_default_and_flag_mode(settings):
    report = (
        "Năm 2025, tổng phát thải khí nhà kính phạm vi 1 của Công ty là 9.000 tCO2e.\n\n"
        "Bảng 5.2 – Chỉ số môi trường năm 2025\nPhát thải khí nhà kính phạm vi 1 năm 2025: 15.000 tCO2e."
    )
    docs = [DocumentInput(name="r.txt", text=report, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL)]
    off = OrchestratorAgent(settings).run(docs).verifications
    assert all(V.CONTRADICTED != v.status and "internal_inconsistency" not in v.review_flags for v in off)
    settings.verification.internal_inconsistency = "flag"
    flagged = OrchestratorAgent(settings).run(docs).verifications
    assert all(v.status != V.CONTRADICTED for v in flagged)


def test_raise_queue_takes_review_flags():
    class P:
        def __init__(self, i):
            self.item_id, self.item_type, self.in_queue, self.raised_by = i, "claim", False, []
    ps = [P("a"), P("b")]
    out = raise_queue(ps, flags={"a": ["absolute_claim_conflict"]})
    assert ps[0].in_queue and ps[0].raised_by == ["flag:absolute_claim_conflict"] and not ps[1].in_queue
    assert out["by_reason"]["flag"] == 1


def test_label_numbers_are_not_invented_figures():
    source = "Phát thải phạm vi 1 là 22.540.603 tCO2e theo ISO 14064-1:2018."
    assert new_numbers("Tuyên bố chưa nêu phát thải phạm vi 3 (Scope 3) theo GRI 305-3.", source) == set()
    assert new_numbers("Phát thải phạm vi 1 là 25.000.000 tCO2e.", source) == {"25000000"}


def _external(settings, claim, evidence):
    return _run(settings, claim, evidence, SourceType.EXTERNAL).verifications


def test_same_figure_opposite_trend_is_contradicted(settings):
    evidence = "Năm 2023, chất thải nguy hại phát sinh của Công ty giảm 10% so với năm 2022."
    assert _external(settings, "Năm 2023, chất thải nguy hại phát sinh của Công ty giảm 10% so với năm 2022.", evidence)[0].status != V.CONTRADICTED
    flipped = _external(settings, "Năm 2023, chất thải nguy hại phát sinh của Công ty tăng 10% so với năm 2022.", evidence)[0]
    assert flipped.status == V.CONTRADICTED and "ngược hướng" in flipped.rationale


def test_figure_consistency_can_be_switched_off(settings):
    settings.verification.figure_consistency_check = False
    evidence = "Năm 2023, chất thải nguy hại phát sinh của Công ty giảm 10% so với năm 2022."
    assert _external(settings, "Năm 2023, chất thải nguy hại phát sinh của Công ty tăng 10% so với năm 2022.", evidence)[0].status != V.CONTRADICTED


def test_one_matching_figure_does_not_support_a_claim_whose_other_figure_is_off(settings):
    evidence = "Năm 2025, mảng thép phát thải 23.369.500 tCO2e, chiếm 99,55% tổng phát thải khí nhà kính của Tập đoàn."
    ok = _external(settings, evidence, evidence)[0]
    bad = _external(settings, "Năm 2025, mảng thép phát thải 58.423.750 tCO2e, chiếm 99,55% tổng phát thải khí nhà kính của Tập đoàn.", evidence)[0]
    assert bad.status not in (V.SUPPORTED,)
    assert ok.status != V.CONTRADICTED
