"""Phân loại phải chịu được cách đặt tên file thực tế.

Mọi tên file trong file này là tên THẬT quan sát được trong dry-run ngày
2026-07-29 trên hoaphat.com.vn và vinamilk.com.vn (CDN CloudFront).
"""

from __future__ import annotations

import pytest

from crawler.pipeline.classifier import classify_report, describe_document, excluded
from crawler.utils import fold_text

REPORT_TYPES = {
    "sustainability": ["báo cáo phát triển bền vững"],
    "annual": ["báo cáo thường niên"],
    "financial": ["báo cáo tài chính", "bctc"],
    "governance": ["báo cáo quản trị", "tình hình quản trị", "qtct"],
    "explanatory": ["giải trình", "kqkd"],
}


class TestFolding:
    def test_strips_diacritics_and_separators(self):
        assert fold_text("Báo-cáo_thường.niên") == "bao cao thuong nien"

    def test_handles_d_stroke(self):
        # đ không phải tổ hợp dấu nên NFD không tách được
        assert fold_text("Đầu tư") == "dau tu"

    def test_collapses_whitespace(self):
        assert fold_text("  Báo   cáo  ") == "bao cao"


class TestRealFilenames:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            # Bug thật: CDN ASCII hoá tên + nối bằng gạch dưới, không khớp từ khoá có dấu
            ("Bao_cao_quan_tri_Cong_ty_nam_2018.pdf", "governance"),
            ("202601_VNM_Bao_cao_QTCT_ca_nam_2025_CBTT.pdf", "governance"),
            ("1589953727_Bao_cao_tinh_hinh_quan_tri_cong_ty_nam_2015.pdf", "governance"),
            ("20250728_VNM_Bao_cao_quan_tri_cong_ty_6_T2025_CBTT.pdf", "governance"),
            # gạch ngang
            ("bao-cao-thuong-nien-2023.pdf", "annual"),
            ("bao-cao-phat-trien-ben-vung-2025-7.pdf", "sustainability"),
            ("giai-trinh-kqkd-hop-nhat-6-thang-dau-nam-2025.pdf", "explanatory"),
            # vẫn phải nhận dạng chuỗi có dấu bình thường
            ("Báo cáo tài chính hợp nhất 2024", "financial"),
        ],
    )
    def test_classification(self, filename: str, expected: str):
        assert classify_report(filename, REPORT_TYPES) == expected

    @pytest.mark.parametrize(
        "filename",
        [
            "20260723-hpg-cbtt-thay-doi-dkdn.pdf",
            "20260406-hpg-thong-bao-giao-dich-co-phieu-cua-cdnb.pdf",
            "Vinamilk_Quy_che_hoat_dong_san_giao_dich_TMDT.pdf",
            "20260604-hpg-bao-cao-phat-hanh-co-phieu-tra-co-tuc-nam-2025.pdf",
        ],
    )
    def test_corporate_actions_are_excluded(self, filename: str):
        """Công bố nghiệp vụ không phải báo cáo -> phải bị loại khỏi corpus."""
        patterns = [
            "quy chế", "thay-doi-dkdn", "giao-dich-co-phieu",
            "gop-von-thanh-lap", "tra-co-tuc",
        ]
        assert excluded(filename, patterns) is True

    def test_exclusion_works_on_ascii_url_too(self):
        """Bản cũ chỉ khớp anchor text có dấu; URL ASCII lọt lưới."""
        assert excluded("http://x.test/files/tuyen-dung.pdf", ["tuyển dụng"]) is True


class TestDescribeDocument:
    def test_scope_and_assurance_from_ascii_name(self):
        result = describe_document("BCTC_hop_nhat_quy_2_2024_da_soat_xet.pdf")
        assert result["statement_scope"] == "consolidated"
        assert result["assurance_status"] == "reviewed"
        assert result["period_type"] == "quarterly"

    def test_separate_audited_annual(self):
        result = describe_document("Báo cáo tài chính riêng năm 2023 đã kiểm toán")
        assert result["statement_scope"] == "separate"
        assert result["assurance_status"] == "audited"

    def test_nothing_matched(self):
        result = describe_document("tài liệu khác")
        assert all(v is None for v in result.values())
