# 00 — Hiện trạng và ranh giới dữ liệu

## Baseline ngày 2026-08-07

Theo crawl report hiện tại:

- `data/real_cases/sources/originals/`: **14 tài liệu / 45 MB**.
- Case đã có: KDP-2024, BNY-2022, DWS-2023, KLM-2024 và 2 Vietnam controls HPG/BVH.
- `data/crawl/vn30/`: **670 tài liệu / 21 doanh nghiệp / 2021–2025 / 3.9 GB**.
- Sau normalize: **7,960 claim candidates** + **3,786 evidence candidates**.
- HPG control đã chạy end-to-end: 41 claim, 35 `PARTIALLY_SUPPORTED`, 6 `SUPPORTED`.
- 9 VN30 config targets chưa có tài liệu: `acg, bmp, chp, dmc, nt2, ocb, qns, tlg, tng`.
- 196 tài liệu chưa xác định năm đang ở review.
- 1 cross-split duplicate phải xử lý trước annotation.
- 42 báo cáo PTBV/tích hợp là sampling pool ưu tiên.

## Bảy regression bắt buộc giữ

1. WAF/SEC: phải có header phù hợp, không để 403 phá toàn bộ source.
2. `attachment_domains` rỗng phải fail fast, không silent success.
3. Không đoán URL config theo pattern mà không validate.
4. Filter static assets trước scoring.
5. robots 4xx không biến thành silent global disallow; 5xx/transport fail-safe.
6. Per-company/target cap + scheduler fairness.
7. JSONL U+2028/U+2029/U+0085 safe.

## Ranh giới

- Tài liệu thô != bằng chứng greenwashing.
- Missing data != violation.
- Settlement/ruling qualifiers phải giữ nguyên.
- Vietnam controls không được tự động chuyển thành positive.
- 29 case targets mới là **legal/regulatory case bank**, không phải 29 company-level positive labels.
