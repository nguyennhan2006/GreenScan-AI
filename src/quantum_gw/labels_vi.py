"""Nhãn tiếng Việt cho các mã nội bộ hiện ra trước người soát (lý do chấm điểm, cổng chất lượng, ghi chú pháp lý).

Khớp với frontend/src/lib/labels.js. Mã chỉ giữ nguyên khi là chuẩn được công nhận (GRI, tCO2e, GHG Protocol).
"""
from __future__ import annotations

CLAIM_TYPE = {
    "emissions_reduction": "Giảm phát thải",
    "renewable_energy": "Năng lượng tái tạo",
    "resource_efficiency": "Dùng tài nguyên hiệu quả",
    "resource_use": "Sử dụng tài nguyên (nước, điện, nhiên liệu)",
    "metric_disclosure": "Số liệu môi trường công bố",
    "environmental_compliance": "Tuân thủ và quản lý môi trường",
    "greening": "Cây xanh, rừng",
    "waste_and_circularity": "Chất thải và tuần hoàn",
    "green_finance": "Tài chính xanh",
    "biodiversity": "Đa dạng sinh học",
    "esg_process_integration": "Lồng ghép môi trường – xã hội – quản trị vào quy trình",
    "generic_sustainability": "Phát triển bền vững nói chung",
}

LEGAL_ISSUE = {
    "controlled_substances": "Chất được kiểm soát",
    "disclosure": "Công bố thông tin",
    "emissions": "Phát thải",
    "environmental_protection": "Bảo vệ môi trường",
    "environmental_risk_management": "Quản lý rủi ro môi trường",
    "ghg_inventory": "Kiểm kê khí nhà kính",
    "green_bond": "Trái phiếu xanh",
    "green_credit": "Tín dụng xanh",
    "green_taxonomy": "Danh mục phân loại xanh",
    "listed_company_obligations": "Nghĩa vụ của công ty niêm yết",
    "ozone_protection": "Bảo vệ tầng ô-dôn",
    "permits": "Giấy phép môi trường",
}

SCOPE = {
    "ghg_scope_1_2_3": "phát thải phạm vi 1, 2, 3",
    "group_consolidated": "toàn tập đoàn (hợp nhất)",
    "parent_only": "riêng công ty mẹ",
    "site_or_facility": "một nhà máy hoặc cơ sở",
    "product_or_service": "một sản phẩm hoặc dịch vụ",
    "geography": "một vùng địa lý",
}

# Việc 34: nguyên văn, ở đầu mọi đầu ra (trang web, giấy làm việc, HTML, PDF, DOCX, CSV, gói bằng chứng).
# frontend/src/lib/labels.js DISCLAIMER phải trùng từng chữ (tests/test_disclaimer.py).
DISCLAIMER_VI = "Kết quả này là tín hiệu rủi ro dựa trên thông tin công khai, hỗ trợ người hành nghề đảm bảo khoanh vùng kiểm tra — không thay thế thủ tục thu thập bằng chứng theo ISSA 5000. Không bị gắn cờ không có nghĩa là đã được xác nhận."

VERDICT = {
    "SUPPORTED": "Được ủng hộ",
    "PARTIALLY_SUPPORTED": "Ủng hộ một phần",
    "UNSUPPORTED": "Chưa được chứng minh",
    "CONTRADICTED": "Mâu thuẫn với nguồn",
    "INSUFFICIENT_EVIDENCE": "Chưa đủ bằng chứng",
}


def vi(table: dict[str, str], key: object) -> str:
    """Nhãn của một mã; chưa có trong bảng thì đổi gạch dưới thành khoảng trắng (không hiện mã thô)."""
    k = getattr(key, "value", key)
    k = "" if k is None else str(k)
    return table.get(k, k.replace("_", " "))
