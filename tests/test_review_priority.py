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
    by_id = {p["item_id"]: p for p in result.priorities}
    ranked = [
        (by_id[c.claim_id]["rank"], by_id[c.claim_id], c)
        for c in result.claims if c.claim_id in by_id
    ]
    ranked.sort()
    return result, ranked


def test_every_claim_gets_a_priority_with_reasons(settings):
    result, ranked = _run(settings)
    assert len(result.priorities) == len(result.claims) + len(result.disclosed_figures)
    for _, priority, _ in ranked:
        assert 0 <= priority["priority_score"] <= 100
        assert {c["name"] for c in priority["components"]} == {
            "materiality", "obligation", "evidence_gap", "anomaly",
        }
        assert priority["policy_version"] == "priority-v1.1"


def test_a_quantified_emissions_claim_outranks_promotional_prose(settings):
    """The order is the product; this is the ordering it must never get wrong."""
    _, ranked = _run(settings)
    rank_of = {claim.text: rank for rank, _, claim in ranked}
    quantified = next(r for text, r in rank_of.items() if "Tổng lượng phát thải" in text)
    promotional = next(r for text, r in rank_of.items() if "doanh nghiệp xanh hàng đầu" in text)
    assert quantified < promotional


def test_the_ranking_is_a_total_order_starting_at_one(settings):
    result, _ = _run(settings)
    ranks = sorted(p["rank"] for p in result.priorities)
    assert ranks == list(range(1, len(result.priorities) + 1))


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


# --- disclosed figures share the queue (ISSUES P2) --------------------------

TABLE = (
    "PHÁT THẢI TOÀN TẬP ĐOÀN NĂM 2025 (tCO2e)\n"
    "Phạm vi 1 22.540.603\n"
    "Phạm vi 2 933.876\n"
    "Cộng 23.474.480\n"
)


def _table_run(settings, text: str = TABLE):
    from quantum_gw.agents.orchestrator import OrchestratorAgent

    documents = [
        DocumentInput(name="report.txt", text=text, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
    ]
    return OrchestratorAgent(settings).run(documents)


def test_disclosed_figures_are_extracted_from_indicator_rows(settings):
    """The rows the claim extractor rejects are read here instead of being lost."""
    result = _table_run(settings)
    by_value = {f.value: f for f in result.disclosed_figures}
    assert 22540603.0 in by_value and 933876.0 in by_value and 23474480.0 in by_value
    assert by_value[22540603.0].unit == "tco2e"          # unit taken from the heading
    assert by_value[22540603.0].scopes == [1]
    assert by_value[23474480.0].is_total


def test_cross_foot_reperforms_the_companys_own_addition(settings):
    """22,540,603 + 933,876 = 23,474,479 against a disclosed 23,474,480."""
    result = _table_run(settings)
    checks = [c for c in result.figure_checks if c.kind == "cross_foot"]
    assert checks, "a table with two scope rows and a total must be cross-footed"
    check = checks[0]
    assert check.status == "CONSISTENT"      # one tonne apart: rounding, not an error
    assert check.difference == -1.0
    assert "23,474,479" in check.calculation


def test_a_total_that_does_not_add_up_is_inconsistent(settings):
    broken = TABLE.replace("Cộng 23.474.480", "Cộng 25.000.000")
    result = _table_run(settings, broken)
    checks = [c for c in result.figure_checks if c.kind == "cross_foot"]
    assert checks and checks[0].status == "INCONSISTENT"
    assert checks[0].note


def test_figures_are_ranked_in_the_same_queue_as_claims(settings):
    result = _table_run(settings)
    kinds = {p["item_type"] for p in result.priorities}
    assert "figure" in kinds
    top = min(result.priorities, key=lambda p: p["rank"])
    assert top["item_type"] == "figure", "a published group total outranks nothing else here"


# --- what the score does not know, it must say (external review, 2026-09-25) ---

def test_a_factor_that_was_never_computed_is_not_reported_as_zero(settings):
    """An unscored factor reads as "checked, nothing found" unless it says otherwise."""
    result = _table_run(settings)
    item = result.priorities[0]
    anomaly = next(c for c in item["components"] if c["name"] == "anomaly")
    assert anomaly["status"] == "not_computed"
    assert "chưa tính" in anomaly["reason"]
    assert item["not_computed"] == ["anomaly"]
    # and its weight is not counted as points the item could have earned
    assert item["max_available"] == 90.0


def test_absence_of_support_never_scores_as_high_as_contradiction(settings):
    """UNSUPPORTED plus missing attributes must stay below CONTRADICTED's ceiling."""
    import tempfile
    from pathlib import Path

    from quantum_gw.agents.prioritizer import PrioritizationAgent
    from quantum_gw.domain.enums import VerificationStatus
    from quantum_gw.domain.models import Claim, VerificationResult
    from quantum_gw.storage.audit import AuditLogger

    agent = PrioritizationAgent(
        "configs/priority_v1.yaml", AuditLogger(Path(tempfile.mkdtemp()) / "a.jsonl")
    )
    bare = Claim(claim_id="c", text="Công ty thân thiện với môi trường.",
                 claim_type="generic_sustainability", source_chunk_id="x", source_name="d")
    gaps = {
        status: agent._evidence_gap(
            VerificationResult(claim=bare, status=status, rationale="")
        ).score
        for status in (VerificationStatus.UNSUPPORTED, VerificationStatus.CONTRADICTED)
    }
    assert gaps[VerificationStatus.UNSUPPORTED] < gaps[VerificationStatus.CONTRADICTED]


# --- disclosed-figure reading on real Hòa Phát lines (review 2026-10-05) -------
#
# On the HPG 2025 run 25 of 57 "disclosed figures" were not environmental rows:
# folded, "cộng" (total) equals "công" (công ty, công suất, công nghiệp), "Tổng
# công ty" is a corporation, a label reached back into the previous sentence,
# "triệu" was dropped and a neighbouring column's "%" became the unit. Each line
# below is copied from that run's raw text.

def _figures(text: str):
    import tempfile
    from pathlib import Path

    from quantum_gw.agents.figures import DisclosedFigureAgent
    from quantum_gw.domain.models import EvidenceChunk
    from quantum_gw.storage.audit import AuditLogger

    chunk = EvidenceChunk(chunk_id="c1", doc_id="d1", source_name="hpg.pdf", text=text, page=57,
                          role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL)
    agent = DisclosedFigureAgent(AuditLogger(Path(tempfile.mkdtemp()) / "a.jsonl"))
    return agent.run([chunk])


def test_a_corporation_is_not_a_total_row():
    from quantum_gw.agents.figures import is_total_label

    assert not is_total_label("Tổng công ty Gang thép")
    assert not is_total_label("Công ty TNHH Tôn Hòa Phát")
    assert not is_total_label("công suất thiết kế")
    assert not is_total_label("cộng đồng")
    assert is_total_label("Cộng")
    assert is_total_label("TỔNG CỘNG")
    assert is_total_label("Tổng phát thải khí nhà kính")
    assert is_total_label("Tong cong")          # OCR without diacritics, unambiguous form
    assert not is_total_label("cong suat")       # ... but a bare "cong" may be "công"


def test_ownership_shares_and_headcount_ratios_are_not_disclosed_figures():
    rows = (
        "Quản trị nguồn nhân lực Tổng công ty Nông nghiệp 69,39% 30,61% Nhân quyền\n"
        "Công ty TNHH Điện lạnh Hòa Phát 99,8001% 500 Khu công nghiệp Phố Nối A\n"
        "65,47% 34,53% Phát triển cộng đồng Tổng cộng 89,19% 19,81% CƠ CẤU LAO ĐỘNG\n"
    )
    assert _figures(rows) == []


def test_a_label_does_not_reach_back_into_the_previous_sentence():
    line = "Hòa Phát coi quản trị tốt là điều kiện cần cho điều chỉnh carbon. GIỚI TÍNH QUỐC TỊCH: 100 %"
    assert _figures(line) == [], "a headcount row is not an emissions figure"


def test_country_is_not_water():
    line = "Hòa Phát dẫn đầu cả nước về ống thép với 27,7% thị phần"
    assert _figures(line) == []


def test_a_multiplier_word_is_applied():
    figures = _figures("Tổng lượng điện phát đạt 3,18 tỷ kWh trong năm 2024")
    assert [(f.value, f.unit, f.metric) for f in figures] == [(3.18e9, "kwh", "energy")]


def test_the_next_columns_percentage_is_not_the_unit():
    text = "PHÁT THẢI THEO ĐƠN VỊ (tCO2e)\n1.631 0,01% Cộng 23.474.480 100% 39"
    totals = [f for f in _figures(text) if f.is_total]
    assert [(f.value, f.unit) for f in totals] == [(23474480.0, "tco2e")]


# --- who is speaking (priority-v1.1, review 2026-10-05) -------------------------

def test_the_entity_name_is_read_from_the_report():
    from quantum_gw.agents.prioritizer import entity_names

    text = (
        "Tập đoàn Hòa Phát đã đầu tư lò điện. Năm 2025, Tập đoàn Hòa Phát giảm tiêu hao. "
        "Công ty Cổ phần Hòa Phát cam kết minh bạch. Tập đoàn Hòa Phát công bố báo cáo."
    )
    assert "Hòa Phát" in entity_names([text])
    assert entity_names([], declared=["Vinamilk"]) == ["Vinamilk"]


def test_an_explanation_of_technology_ranks_below_the_entitys_own_statement(settings):
    """The head of the HPG queue was textbook steelmaking, not Hòa Phát speaking."""
    text = (
        "Tập đoàn Hòa Phát đã triển khai giải pháp giảm phát thải khí nhà kính tại các nhà máy.\n"
        "Ngược lại, EAF có mức phát thải thấp hơn, nhưng phụ thuộc vào nguồn thép phế.\n"
    )
    documents = [DocumentInput(name="r.txt", text=text, role=DocumentRole.CLAIM_SOURCE,
                               source_type=SourceType.INTERNAL)]
    result = OrchestratorAgent(settings).run(documents)
    by_text = {p["text"][:20]: p for p in result.priorities if p["item_type"] == "claim"}
    own, textbook = by_text["Tập đoàn Hòa Phát đã"], by_text["Ngược lại, EAF có mứ"]
    assert own["priority_score"] > textbook["priority_score"]
    materiality = next(c for c in textbook["components"] if c["name"] == "materiality")
    assert "không nêu chủ thể" in materiality["reason"]
    # moved down, not out: the verdict layer never sees this factor
    assert {v.claim.text[:20] for v in result.verifications} >= set(by_text)


def test_a_unit_with_a_digit_in_it_stays_whole():
    figures = _figures("Cường độ phát thải CO2 trung bình (BF-BOF) 2,32 tấn CO2/tấn thép")
    assert [(f.value, f.unit) for f in figures] == [(2.32, "tco2e")]


def test_a_unit_alone_is_not_an_indicator_name():
    line = "Phát thải của các công ty thành viên khác là 90.846 tCO2e, chiếm 0,39% tổng phát thải"
    assert all(f.label != "tCO2e, chiếm" for f in _figures(line))
