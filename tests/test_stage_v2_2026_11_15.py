"""Expert-review batch, 15/11/2026: claim-typing-v2, units-v2, figure-consistency additions, support guard on,
report-year period, assessment-v1, table amounts in absolute-share-v1."""
from __future__ import annotations

import tempfile
from pathlib import Path

from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus as V
from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import parse_quantities
from quantum_gw.verification.absolute import allocated_share, amounts
from quantum_gw.verification.numeric_facts import eligibility, facts_in


def _extract(settings, text, name="report_2025.pdf"):
    agent = ClaimExtractionAgent(settings.claim_extraction, AuditLogger(Path(tempfile.mkdtemp()) / "a.jsonl"))
    chunk = EvidenceChunk(chunk_id="c", doc_id="d", source_name=name, role=DocumentRole.CLAIM_SOURCE,
                          source_type=SourceType.INTERNAL, text=text)
    return agent.run([chunk])


def _run(settings, claim, evidence, source_type=SourceType.EXTERNAL):
    return OrchestratorAgent(settings).run([
        DocumentInput(name="claim.txt", text=claim, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=evidence, role=DocumentRole.EVIDENCE, source_type=source_type),
    ]).verifications


# --- claim-typing-v2 ------------------------------------------------------------

def test_water_and_electricity_sentences_are_now_claims(settings):
    claims = _extract(settings, "Năm 2024, các nhà máy điện nhiệt dư phát 3,18 tỷ kWh điện, tăng 29% so với năm trước. "
                                "Tổng lượng nước tiêu thụ năm 2024 là 1,2 triệu m3.")
    assert {c.claim_type for c in claims} == {"resource_use"}
    assert len(claims) == 2


def test_fallback_can_be_switched_off(settings):
    settings.claim_extraction.fallback_types = False
    assert _extract(settings, "Tổng lượng nước tiêu thụ năm 2024 là 1,2 triệu m3.") == []


def test_state_and_country_water_is_not_water(settings):
    assert _extract(settings, "Doanh thu trong nước năm 2024 tăng 12% so với năm 2023.") == []


def test_report_year_period_is_marked_and_never_matches(settings):
    claim = _extract(settings, "Hiện nay, 100% nhà máy của Tập đoàn đã đạt chứng nhận ISO 14001.", "HPG_SR_2025.pdf")[0]
    assert claim.period == "2025" and claim.period_source == "report_year"
    assert claim.claim_type == "environmental_compliance"


# --- units-v2 ---------------------------------------------------------------------

def test_area_capacity_and_tree_units():
    assert parse_quantities("Không gian xanh 140 m2.")[0][1] == "m2"
    assert parse_quantities("Công suất 2,7 MWp.")[0][1] == "mwp"
    assert parse_quantities("Trồng 11.111 cây xanh.")[0][1] == "cay"
    assert parse_quantities("Rừng 25 hecta.")[0][1] == "ha"


def test_scope_is_read_per_figure():
    facts = facts_in("Phạm vi 1: 10.973.000 tấn CO2; Phạm vi 2: 134.820 tấn CO2")
    assert [sorted(f.scopes) for f in facts] == [[1], [2]]


def test_intensity_slash_parent_water_and_cumulative():
    per_ton = facts_in("Tổng lượng nước sử dụng của Công ty là 34.325 m3/tấn sản phẩm.")[0]
    total = facts_in("Lượng nước sử dụng năm 2024: 34.325 m3.")[0]
    assert eligibility(per_ton, total) == ("NOT_COMPARABLE", "different_basis")
    waste = facts_in("Lượng nước thải của Công ty là 34.325 m3.")[0]
    assert eligibility(waste, total) == ("NOT_COMPARABLE", "different_variant")
    parent = facts_in("Phát thải phạm vi 1 và 2 của công ty mẹ năm 2025 là 1,2 triệu tCO2e.")[0]
    group = facts_in("Tổng phạm vi 1 và 2 của Tập đoàn: 23.474.480 tCO2e.")[0]
    assert eligibility(parent, group) == ("NOT_COMPARABLE", "different_boundary")
    cumul = facts_in("Nhà máy đạt sản lượng điện lũy kế 10 tỷ kWh.")[0]
    year = facts_in("Năm 2024 nhà máy phát 788 triệu kWh.")[0]
    assert eligibility(cumul, year) == ("AMBIGUOUS", "cumulative_vs_period")


# --- figure-consistency additions ------------------------------------------------------

def test_trend_word_nearest_the_figure_decides(settings):
    evidence = ("Trong năm 2021, mặc dù tổng sản lượng tăng lên 20%, mức tiêu thụ gas và xăng dầu giảm tương ứng là 39% "
                "so với năm 2020.")
    v = _run(settings, "Năm 2021, mức tiêu thụ gas và xăng dầu của Công ty tăng 39% so với năm 2020.", evidence)[0]
    assert v.status == V.CONTRADICTED and "ngược hướng" in v.rationale


def test_same_change_other_base_year_is_not_supported(settings):
    evidence = "Trong năm 2021, mức tiêu thụ gas và xăng dầu giảm 39% so với năm 2020."
    v = _run(settings, "Năm 2021, mức tiêu thụ gas và xăng dầu của Công ty giảm 39% so với năm 2017.", evidence)[0]
    assert v.status != V.SUPPORTED


def test_one_hundred_percent_is_exact(settings):
    v = _run(settings, "Năm 2025, khu liên hợp tự chủ 100% nhu cầu điện năng.",
             "Năm 2025, khu liên hợp tự chủ 98% nhu cầu điện năng.")[0]
    assert v.status != V.SUPPORTED


def test_zero_violation_claim_is_not_refuted_by_the_word_violation(settings):
    v = _run(settings, "Trường hợp vi phạm pháp luật về môi trường của Công ty là 0 trường hợp.",
             "Trong năm, trường hợp vi phạm pháp luật về môi trường của Công ty là 0 trường hợp.")[0]
    assert v.status != V.CONTRADICTED


def test_evidence_that_disagrees_with_itself_goes_to_a_reviewer(settings):
    evidence = ("Năm 2024, các nhà máy điện nhiệt dư thuộc hai khu liên hợp tại Hải Dương và Dung Quất có tổng lượng điện "
                "phát đạt 3,18 tỷ kWh. Riêng tại Dung Quất, nhà máy điện nhiệt dư phát 788 triệu kWh.")
    v = _run(settings, "Năm 2024, các nhà máy điện nhiệt dư tại hai khu liên hợp đạt tổng lượng điện phát 3,18 tỷ kWh.", evidence)[0]
    assert v.status != V.CONTRADICTED


# --- support guard on, assessment ----------------------------------------------------------

def test_company_echo_is_partial_and_says_who_wrote_it(settings):
    v = _run(settings, "Năm 2024, tổng lượng nước tiêu thụ của Công ty là 1,2 triệu m3.",
             "Tổng lượng nước tiêu thụ năm 2024 của Công ty là 1,2 triệu m3.", SourceType.FINANCIAL)[0]
    assert v.status == V.PARTIALLY_SUPPORTED
    assert v.assessment["consistency"] == "match"
    assert v.assessment["source_independence"] == "company_financial"
    assert v.assessment["basis"] == "arithmetic"


# --- absolute-share-v1 on a real allocation table -----------------------------------------------

TABLE = ("TABLE\nTóm tắt phân bổ\nTechcombank đã phân bổ một phần trong kỳ báo cáo năm 2024 | Tỷ lệ | Giá trị (tỷ VND)\n"
         "Số tiền thu được từ phát hành trái phiếu được phân bổ vào Dự Án đủ\nđiều kiện | 89% | 399\n"
         "Số tiền còn lại chưa được phân bổ được giữ dưới dạng tiền mặt,\ncác khoản tương đương tiền | | 51\n")


def test_table_amounts_take_the_header_unit_and_sum_to_the_total():
    roles = [(a["role"], a["value"]) for a in amounts(TABLE)]
    assert roles == [("used", 399e9), ("unused", 51e9)]
    share = allocated_share("Toàn bộ vốn từ trái phiếu xanh đã được phân bổ cho các dự án đủ điều kiện.", TABLE)
    assert round(share["share_pct"], 1) == 88.7


# --- claim-precision-v1, audit-sample-v1 ---------------------------------------------------

def test_generic_sustainability_needs_an_environmental_word(settings):
    assert _extract(settings, "Đây không chỉ là sự kiện tri ân mà còn khẳng định mối quan hệ bền vững giữa Công ty và khách hàng.") == []
    assert _extract(settings, "Ban Điều hành có trách nhiệm xây dựng các mục tiêu cho chiến lược phát triển bền vững.") == []
    kept = _extract(settings, "Chúng tôi là doanh nghiệp xanh hàng đầu, luôn thân thiện với môi trường.")
    assert kept and kept[0].claim_type == "generic_sustainability"


def test_audit_sample_is_outside_the_queue_and_stable(settings):
    def run():
        return OrchestratorAgent(settings).run([
            DocumentInput(path="data/sample/company_esg_2024.txt", role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
            DocumentInput(path="data/sample/financial_2024.txt", role=DocumentRole.EVIDENCE, source_type=SourceType.FINANCIAL),
        ])
    settings.review.audit_sample_size = 2
    first, second = run(), run()
    pick = lambda r: sorted(p["item_id"] for p in r.priorities if p.get("audit_sample"))
    assert pick(first) == pick(second)
    assert all(not p["in_queue"] for p in first.priorities if p.get("audit_sample"))
