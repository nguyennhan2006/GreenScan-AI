# P09 · Quy trình người soát, giấy làm việc, Studio

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Con người quyết định cuối cùng với từng mục. Hệ thống ghi lại quyết định, người soát và lý do, và xuất giấy làm việc có những gì không kiểm **[KIẾN THỨC NỀN]** (`docs/05-ui/HUMAN_REVIEW_SPEC.md`, mục 1).

## 2. Lỗi hoặc rủi ro đã đo được

- Bản UI 08/08 đặt "Nguy cơ cao — 73" làm KPI chính, thiếu evidence viewer và thiếu checklist năm thuộc tính **[KIẾN THỨC NỀN]** (`docs/05-ui/UI_REVIEW_20260808.md`, mục 1, 5, 6).
- Hàng đợi cũ không dùng thứ tự ưu tiên của backend; đã sửa **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-01).
- Đo lường chưa có: chưa có số người soát, chưa có số thời gian làm tay so với GreenScan **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 1, RQ10).

## 3. Thiết kế hiện tại, file code, cấu hình

- Sản phẩm mở bằng quy trình ba bước: tải tài liệu, soát theo hàng đợi, giấy làm việc tiếng Việt (`GET /v1/runs/{id}/workpaper`) **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-01).
- Quyết định người soát ghi bằng `POST /v1/reviews`, chỉ ghi thêm **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 1).
- Màn hình trong đặc tả: S1 tài liệu, S2 tổng quan, S3 kiểm chứng (màn chính), S4 source viewer, S5 phiên (kế hoạch) **[KIẾN THỨC NỀN]** (`docs/05-ui/PRODUCTION_UI_SPEC_2026-09-20.md`, mục 5).
- Kịch bản demo 2:40 gồm sáu màn hình **[KIẾN THỨC NỀN]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, bảng demo).

## 4. Vì sao chọn, phương án đã bỏ

- Demo kể một câu chuyện mở bằng một tuyên bố, không mở bằng dashboard hay risk score. Lý do: BGK dễ đọc dashboard là cáo buộc **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-07).
- Gộp các trang "Tổng quan" và "Xét duyệt" vào trang hàng đợi **[KIẾN THỨC NỀN]** (cùng file, D-2026-10-06-01).

## 5. Số đo có n

- 156 tuyên bố thành 9 mục nên soát trước; 163 mục không soát trong lượt này và lý do được nêu **[KIẾN THỨC NỀN]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, bảng demo).
- Bản soát tay 22 mục hàng đợi HPG, trong đó 14 câu, do một người gán **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 1).
- THIẾU: số người soát và thời gian soát. Cách lấy: bài đo thời gian làm tay so với GreenScan, Quỳnh là người phụ trách **[KIẾN THỨC NỀN]** (`docs/06-operations/HANDOFF_2026-09-25.md`, mục Quỳnh, việc 3).

## 6. Giới hạn và yếu tố gây nhiễu

- Chưa có nghiên cứu người dùng. Hệ thống chưa được kiểm chứng trên người soát thật **[KIẾN THỨC NỀN]**.
- Một số mục hàng đợi chưa mở trong demo: mục #1 bị gãy dòng, và lọc "ủng hộ" có chữ dính cột **[ĐÃ THỰC NGHIỆM]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, dòng cuối bảng).
- Sai khác cần làm rõ: checklist ghi "luồng 4 bước", còn quyết định D-2026-10-06-01 và đặc tả ghi 3 bước. Cần chốt một cách gọi.

## 7. Lỗi đã gặp và cách gỡ

- Chữ gãy dòng và chữ dính cột khiến mục hàng đợi sai. Gỡ bằng bộ trích và trọng số ưu tiên; mục còn lỗi không đưa vào demo **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Luồng đã chạy và có kiểm thử quy trình; chưa có đánh giá của người soát ngoài nhóm **[KIẾN THỨC NỀN]** (`docs/05-ui/PRODUCTION_UI_SPEC_2026-09-20.md`, F9).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đánh giá với giảng viên kiểm toán và Thảo **[KIẾN THỨC NỀN]** (`docs/07-presentation/nghien-cuu/00_DANH_MUC_CAN_THU_THAP.md`, mục C).
- Đo thời gian soát có và không có GreenScan; ghi số người và số câu **[GIẢ THUYẾT]**.

## 10. Hình nên vẽ và file dữ liệu

- Sơ đồ luồng 3 bước (hoặc 4 bước, sau khi chốt) với đường dẫn API.
- THIẾU: hình chụp màn hình của luồng. Cách lấy: chụp từ phiên demo; thư mục `docs/07-presentation/screenshots_ui_2026-10-15/` có sẵn nhưng lượt này chưa đọc.
