"""claim-quality v1.2 (17/11/2026): list glue, table rows, repeated headings, cut sentences -- marked, never removed."""
from quantum_gw.agents.claim_quality import reason_vi, suspect_reason


def test_shapes_left_at_the_head_of_the_hpg_queue_are_marked():
    assert suspect_reason("Quản trị doanh nghiệp tốt • Tuân thủ các quy định pháp luật và minh bạch về Thuế, "
                          "Môi trường • Đóng góp cho lộ trình giảm phát thải khí nhà kính") == "list_glue"
    assert suspect_reason("Tổng phát khí thải nhà kính gián tiếp (Phạm vi 2) (CO2e) Tấn 933.876 305- 2 Phát thải "
                          "khí nhà kính gián tiếp Tổng phát thải khí nhà kính (Phạm vi 1+2) (CO2e Tấn 23.474.479") == "layout_glue"
    assert suspect_reason("Phương pháp quản lý Kết quả tiêu thụ năng lượng năm 2025 Chưa thu thập được đầy đủ thông tin "
                          "từ các bên liên quan Kết quả tiêu thụ năng lượng năm 2025 Hành động giảm thiểu") == "layout_glue"
    assert suspect_reason("Hỗ trợ sản xuất thép bền vững, giảm phát thải và thúc") == "fragment"
    for code in ("list_glue", "fragment"):
        assert reason_vi(code)


def test_real_claims_of_the_same_look_are_left_alone():
    # a programme named twice, the second time in quotes after a comma (GS-Eval v2, a true claim)
    assert suspect_reason("Chương trình có sự tham dự của các tập đoàn lớn tại “Hội nghị xúc tiến đầu tư phát triển "
                          "khu công nghiệp thông minh, bền vững” do Cổng thông tin tổ chức, trong đề án “Đầu tư phát "
                          "triển Khu công nghiệp thông minh bền vững” (SSIP).") is None
    assert suspect_reason("Công ty đã giảm 933.876 tấn phát thải và tái chế 99% chất thải rắn.") is None
    assert suspect_reason("Năm 2024 nhà máy tiêu thụ 120 tấn 2024 theo kế hoạch.") is None   # a year after a unit
    assert suspect_reason("Tập đoàn tiết kiệm năng lượng và nước.") is None                  # closed sentence
    assert suspect_reason("Giảm 10% lượng nước và điện") is None                              # a figure: a claim
