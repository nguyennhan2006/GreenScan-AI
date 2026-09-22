# 01 — Mục tiêu và Definition of Done

## Mục tiêu tổng quát

Mở rộng corpus từ 21 doanh nghiệp đã crawl thành tập 50 entity chính bằng cách thêm 29 target có official legal/regulatory record. Tạo được dữ liệu đủ để nghiên cứu **claim → evidence → adjudication context**, không tạo dataset “company good/bad”.

## Mục tiêu cụ thể

1. **29/29 authority case packs** có provenance.
2. Attempt corporate/fund disclosures **2021–2025** cho 29 target, theo profile phù hợp.
3. Lưu challenged artifact nếu authority page cung cấp hoặc trích dẫn rõ nguồn official.
4. Build `coverage_matrix` theo entity × year × document family.
5. Chuẩn hóa entity mapping để tránh gắn ruling của subsidiary/brand sang parent không kiểm soát.
6. Tạo pool hard-negative: cùng doanh nghiệp nhưng claim ngoài phạm vi ruling; cùng metric nhưng sai năm/scope; cùng keyword nhưng khác product/entity.
7. Không đưa candidate vào gold set trước two-reviewer annotation/adjudication.

## Coverage không phải quota file

Không “đủ 5 năm” bằng cách tải bất kỳ PDF nào. Với mỗi năm 2021–2025 phải có một trong các status:

- `collected`
- `integrated_in_other_report`
- `not_published`
- `not_applicable`
- `not_found_after_exhaustive_official_search`
- `blocked_requires_manual_review`

Một target có 3 năm tài liệu chính thức + 2 năm `not_published` có documentation đầy đủ tốt hơn target có 5 PDF từ mirror không rõ nguồn.

## Definition of Done tổng

- Registry 29 target validate pass.
- Case packs: 100% có authority landing artifact/status.
- Corporate coverage matrix hoàn chỉnh 2021–2025.
- 0 cross-split duplicate trước annotation.
- 100% documents có SHA-256 + source URL + access timestamp + resolved year/status.
- Không có `LEGAL_POSITIVE` ở company/document level.
- Collection report nêu rõ collected/missing/blocked, không che lỗi bằng exit code 0.
