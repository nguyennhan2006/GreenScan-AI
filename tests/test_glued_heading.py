"""claim-quality v1.1 (11/11/2026): a heading read into the first line of a sentence.

The HPG queue was led by "HÒA PHÁT trò nền tảng …": the reader set the running
title between "đóng vai" and "trò". The rule marks such a sentence (it keeps its
verdict and stays in the claim list) and leaves the company's own all-caps name in
front of a predicate alone.
"""
import pytest

from quantum_gw.agents.claim_quality import starts_with_glued_heading, suspect_reason

GLUED = [
    "HÒA PHÁT trò nền tảng để cung cấp nguồn thép chất lượng cao cho các công trình hạ tầng và máy móc.",
    "MÔI TRƯỜNG nhóm thép và nông nghiệp đạt trên 99% Điểm nổi bật về phát triển bền vững năm 2025.",
    "KEY PROJECTS equivalent in 2023 and 90,791 tonnes CO2 equivalent in 2022).",
]
REAL = [
    "TẬP ĐOÀN HÒA PHÁT đã giảm 10% phát thải khí nhà kính năm 2024 so với năm 2020.",
    "HÒA PHÁT cam kết đạt phát thải ròng bằng 0 vào năm 2050.",
    "ESG Hòa Phát tích hợp các mục tiêu phát triển bền vững vào chiến lược kinh doanh.",
    "CO2 phát thải năm 2024 giảm 12% so với năm 2020.",
    "Năm 2024, Tập đoàn tiêu thụ 1.250 GWh điện.",
    "GRI 305 được áp dụng cho toàn bộ báo cáo.",
]


@pytest.mark.parametrize("text", GLUED)
def test_heading_glued_to_a_clause_is_marked(text):
    assert starts_with_glued_heading(text)
    assert suspect_reason(text) == "layout_glue"


@pytest.mark.parametrize("text", REAL)
def test_real_claims_are_left_alone(text):
    assert not starts_with_glued_heading(text)
