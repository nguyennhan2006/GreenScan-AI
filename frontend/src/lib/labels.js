/**
 * Nhãn tiếng Việt cho mọi giá trị mã hiện ra màn hình.
 * Chuẩn từ ngữ: docs/05-ui/CHUAN_NGON_NGU_GIAO_DIEN.md (mục 3).
 * Giá trị mã (emissions, ghg_scope_1_2_3, decrease…) chỉ tồn tại trong dữ liệu;
 * giao diện luôn gọi labelOf(loại, giá trị) trước khi hiển thị.
 */

export const LABELS = {
  claim_type: {
    emissions_reduction: 'Giảm phát thải',
    renewable_energy: 'Năng lượng tái tạo',
    resource_efficiency: 'Dùng tài nguyên hiệu quả',
    waste_and_circularity: 'Chất thải và tuần hoàn',
    green_finance: 'Tài chính xanh',
    biodiversity: 'Đa dạng sinh học',
    esg_process_integration: 'Lồng ghép môi trường – xã hội – quản trị vào quy trình',
    generic_sustainability: 'Phát triển bền vững nói chung',
  },
  metric: {
    emissions: 'lượng phát thải',
    renewable_energy: 'năng lượng tái tạo',
    energy: 'năng lượng tiêu thụ',
    water: 'nước sử dụng',
    waste: 'chất thải',
    green_finance: 'vốn cho dự án xanh',
  },
  scope: {
    ghg_scope_1_2_3: 'phát thải phạm vi 1, 2, 3',
    group_consolidated: 'toàn tập đoàn (hợp nhất)',
    parent_only: 'riêng công ty mẹ',
    site_or_facility: 'một nhà máy hoặc cơ sở',
    product_or_service: 'một sản phẩm hoặc dịch vụ',
    geography: 'một vùng địa lý',
  },
  direction: { decrease: 'giảm', increase: 'tăng', stable: 'giữ nguyên' },
  unit: { tan: 'tấn', tco2e: 'tấn CO2 tương đương', tco2: 'tấn CO2', kwh: 'kWh', mwh: 'MWh', m3: 'm³', '%': '%' },
  language: { vi: 'Tiếng Việt', en: 'Tiếng Anh' },
  severity: { LOW: 'Thấp', MEDIUM: 'Trung bình', HIGH: 'Cao', CRITICAL: 'Rất cao' },
  // claim-quality-v1: why a sentence is probably not a claim (agents/claim_quality.py)
  quality_flag: {
    layout_glue: 'chữ dàn trang dính nhau (ô bảng, mục lục hoặc tiêu đề đọc liền thành câu)',
    standard_title: 'tên một tiêu chuẩn, không phải lời doanh nghiệp tự khẳng định',
    legal_text: 'trích văn bản pháp luật, không phải lời doanh nghiệp tự khẳng định',
    contact_line: 'thông tin liên hệ',
  },
  legal_issue: {
    controlled_substances: 'Chất được kiểm soát',
    disclosure: 'Công bố thông tin',
    emissions: 'Phát thải',
    environmental_protection: 'Bảo vệ môi trường',
    environmental_risk_management: 'Quản lý rủi ro môi trường',
    ghg_inventory: 'Kiểm kê khí nhà kính',
    green_bond: 'Trái phiếu xanh',
    green_credit: 'Tín dụng xanh',
    green_taxonomy: 'Danh mục phân loại xanh',
    listed_company_obligations: 'Nghĩa vụ của công ty niêm yết',
    ozone_protection: 'Bảo vệ tầng ô-dôn',
    permits: 'Giấy phép môi trường',
  },
  doc_status: {
    effective: 'Đang hiệu lực',
    effective_with_amendments: 'Đang hiệu lực (có sửa đổi)',
    expired: 'Hết hiệu lực',
    superseded: 'Đã bị thay thế',
    draft: 'Dự thảo',
  },
  legal_finding: {
    MATCH: 'Phù hợp điều kiện đã kiểm',
    PARTIAL_MATCH: 'Phù hợp một phần',
    NOT_MATCH: 'Chưa đáp ứng điều kiện đã kiểm',
    INSUFFICIENT_EVIDENCE: 'Chưa đủ dữ liệu pháp lý để kết luận',
    NOT_APPLICABLE: 'Không áp dụng',
  },
  check_mode: {
    current_policy_alignment: 'đối chiếu với chính sách hiện hành',
    historical_compliance: 'đối chiếu với văn bản hiệu lực tại kỳ báo cáo',
  },
}

/** Nhãn của một giá trị mã; chưa có trong bảng thì đổi gạch dưới thành khoảng trắng (không hiện mã thô). */
export function labelOf(kind, value) {
  if (value == null || value === '') return value
  if (Array.isArray(value)) return value.map((v) => labelOf(kind, v)).join(', ')
  const table = LABELS[kind] || {}
  const key = String(value)
  return table[key] ?? table[key.toLowerCase()] ?? key.replace(/_/g, ' ')
}

/** Số thập phân kiểu Việt Nam: 0,60 */
export function vnDecimal(x, digits = 2) {
  if (x == null || Number.isNaN(Number(x))) return '—'
  return Number(x).toFixed(digits).replace('.', ',')
}
