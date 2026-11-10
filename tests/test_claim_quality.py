"""claim-quality-v1 and risk-rubric-v3 (2026-11-09).

A probable non-claim is marked, never removed: it keeps its verdict and stays in
the claim list, but it leaves the review queue and the risk score. Every
sentence below is taken from a real report in the GS-Eval v2 pool.
"""

from __future__ import annotations

import pytest

from quantum_gw.agents.claim_quality import suspect_reason
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.scorer import RiskScoringAgent
from quantum_gw.domain.enums import DocumentRole, Severity, SourceType, VerificationStatus
from quantum_gw.domain.models import Claim, DocumentInput, VerificationResult
from quantum_gw.storage.audit import AuditLogger

NOT_CLAIMS = {
    "Bảo mật thông tin khách hàng DHG Pharma 2 6 1 3 4 Phát triển bền vững 5.": "layout_glue",
    "Báo cáo phát triển bền vững Điểm nhấn Tổng quan về báo cáo 140 Mô hình phát triển bền vững của Traphaco 141 "
    "Định hướng chiến lược phát triển bền vững 142": "layout_glue",
    "Tuân thủ kinh tế và xã hội Năng lượng 4 Giám sát & Đánh giá GRI 419 GRI 302 Đa dạng sinh học": "layout_glue",
    "CO2 CH4 SF6 N2O HFCs PFCs Scope 1 DIRECT Scope 2 INDIRECT Scope 3 INDIRECT purchased goods": "layout_glue",
    "Topic Identification Stakeholder Engagement Environmental Social Governance As SABECO operates within "
    "the beverage industry, we researched peers": "layout_glue",
    "Điểm nổi bật về phát triển bền vững năm 2025 2015 2016 2017 2019 2020 2021": "layout_glue",
    "ISO 14064-1: Greenhouse gases — Part 1: Specification with guidance at the organization level for "
    "quantification and reporting of greenhouse gas emissions and removals.": "standard_title",
    "Nghị định hướng dẫn Luật Bảo vệ môi trường năm 2020 bao gồm: Nghị định 06/2022/NĐ-CP quy định về giảm "
    "nhẹ phát thải khí nhà kính và bảo vệ tầng ô-dôn.": "legal_text",
    "Điện thoại: +84 243.974.7751 | Email: esg@hoaphat.com.vn": "contact_line",
}

# Real claims that look close to a rule and must stay unmarked.
CLAIMS = [
    "Tổng lượng phát thải khí nhà kính Phạm vi 1 và 2 của Tập đoàn năm 2024 là 23.474.480 tấn CO2e.",
    "Công ty đã lắp đặt 5 nhà máy điện mặt trời áp mái với tổng công suất 12 MW trong năm 2024.",
    "Công ty tuân thủ Luật Bảo vệ môi trường 2020 và Nghị định 08/2022/NĐ-CP trong toàn bộ hoạt động sản xuất.",
    "Effective water management in 2024 resulted in the reduction, reuse, and recycling of water, compared to "
    "the total volume of water withdrawal, as follows:",
    "Công ty áp dụng công cụ kiểm kê khí nhà kính trên website https://co2.coteccons.vn cho toàn bộ dự án.",
    "Dự án “Toa Thuốc Vì Cộng Đồng” vừa được vinh danh với hạng mục “Dự án bền bỉ”, khẳng định sự đóng góp bền vững.",
    "Khu liên hợp Gang thép Hòa Phát Dung Quất đã giảm 12% cường độ phát thải so với năm 2022.",
    "At SABECO, we consumed electricity, steam and fuel covering Diesel oil (DO), Fuel Oil (FO), Gasoline, "
    "Biomass and LPG in 2024.",
    "Hòa Phát đặt mục tiêu giảm 20% phát thải Phạm vi 1 vào năm 2030 so với năm gốc 2020 theo Bước 3 của lộ trình.",
]


@pytest.mark.parametrize("text,reason", list(NOT_CLAIMS.items()))
def test_probable_non_claims_are_marked_with_their_reason(text, reason):
    assert suspect_reason(text) == reason


@pytest.mark.parametrize("text", CLAIMS)
def test_real_claims_are_not_marked(text):
    assert suspect_reason(text) is None


def _verification(text, status=VerificationStatus.PARTIALLY_SUPPORTED, **kw):
    claim = Claim(claim_id="c1", text=text, claim_type="emissions", source_chunk_id="k1", source_name="sr.pdf", **kw)
    return VerificationResult(claim=claim, status=status, rationale="test")


def _scorer(tmp_path):
    return RiskScoringAgent("configs/scoring_v1.yaml", AuditLogger(tmp_path / "audit.jsonl"))


def test_a_marked_sentence_is_not_scored(tmp_path):
    risk = _scorer(tmp_path).run(_verification("DHG Pharma 2 6 1 3 4", quality_flag="layout_glue"))
    assert risk.risk_score == 0 and risk.severity == Severity.LOW
    assert all(c.status == "not_applicable" and c.score == 0 for c in risk.components)
    assert "Không chấm" in risk.severity_cap_reason


def test_a_marked_sentence_that_is_contradicted_is_still_scored(tmp_path):
    risk = _scorer(tmp_path).run(
        _verification("DHG Pharma 2 6 1 3 4", status=VerificationStatus.CONTRADICTED, quality_flag="layout_glue")
    )
    assert risk.risk_score > 0
    assert all(c.status == "computed" for c in risk.components)


def test_baseline_is_needed_only_for_a_quantified_change_or_a_target(tmp_path):
    scorer = _scorer(tmp_path)
    by_name = lambda r: {c.name: c.score for c in r.components}  # noqa: E731
    trend_word_only = scorer.run(_verification("Công ty giảm thiểu tác động môi trường.", direction="decrease"))
    quantified = scorer.run(_verification("Phát thải giảm 20%.", direction="decrease", values=[20.0], units=["%"]))
    target = scorer.run(_verification("Giảm phát thải vào 2030.", direction="decrease", is_future_commitment=True))
    assert by_name(trend_word_only)["baseline"] == 0
    assert by_name(quantified)["baseline"] == 8
    assert by_name(target)["baseline"] == 8


def test_marked_sentences_leave_the_queue_but_stay_in_the_list(settings):
    text = (
        "Bảo mật thông tin khách hàng DHG Pharma 2 6 1 3 4 Phát triển bền vững 5 phát thải khí nhà kính.\n"
        "Tổng lượng phát thải khí nhà kính của Tập đoàn năm 2024 là 23.474.480 tấn CO2e.\n"
    )
    documents = [
        DocumentInput(name="claim.txt", text=text, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text="Báo cáo kiểm kê năm 2024 ghi nhận phát thải khí nhà kính.",
                      role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL),
    ]
    result = OrchestratorAgent(settings).run(documents)
    marked = [c for c in result.claims if c.quality_flag]
    assert marked, "the glued index line should be extracted and marked"
    queue = {p["item_id"] for p in result.priorities if p["in_queue"]}
    assert all(c.claim_id not in queue for c in marked)
    assert any(c.claim_id in queue for c in result.claims if not c.quality_flag)
    assert "không phải tuyên bố" in result.scope_note


def test_the_flag_can_be_turned_off(settings):
    settings.claim_extraction.flag_suspect_non_claims = False
    documents = [
        DocumentInput(name="claim.txt", text="Bảo mật thông tin khách hàng DHG Pharma 2 6 1 3 4 phát thải khí nhà kính.",
                      role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
    ]
    result = OrchestratorAgent(settings).run(documents)
    assert all(c.quality_flag is None for c in result.claims)
