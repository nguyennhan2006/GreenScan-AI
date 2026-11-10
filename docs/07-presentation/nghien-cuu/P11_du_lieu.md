# P11 · Dữ liệu: kho câu, doanh nghiệp, nguồn, nhãn

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Có đủ tài liệu, tuyên bố và nhãn để đo, nhưng nhãn người là nút thắt. Kho dữ liệu cần ba thứ: tài liệu có nguồn, tuyên bố ứng viên có lineage, và nhãn đã được người kiểm **[KIẾN THỨC NỀN]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 3).

## 2. Lỗi hoặc rủi ro đã đo được

- Tỷ lệ supervision: 5 claim đã adjudicate trên 7.960, tức 0,06 % **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, bảng đầu).
- Cùng một thông cáo thu từ bốn nguồn sinh bốn `doc_id` khác nhau; chia theo `doc_id` có thể làm rò rỉ tài liệu giữa train và test **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 1a).
- Phase 1 và phase 2 chạy tách nhau vì SQLite write contention, làm mất dấu ingestion **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 1b).

## 3. Thiết kế hiện tại, file code, cấu hình

- Sáu mức trưởng thành L0 đến L5, mỗi mức có phạm vi dùng và không dùng riêng **[KIẾN THỨC NỀN]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 2).
- Công cụ: `tools/dataset_audit_v2.py`, `tools/repair_legal_case_lineage.py`; tệp chia `data/crawl/vn30/curated/company_split.json` **[KIẾN THỨC NỀN]** (cùng file, mục 1 và 4).
- Chia tập giữ lại theo doanh nghiệp, rồi mới chia theo thời gian **[KIẾN THỨC NỀN]** (cùng file, mục 4).
- Gate chất lượng đợt v2: ứng viên là claim môi trường thật ≥ 70 %; tài liệu có năm 100 %; doanh nghiệp demo có nguồn lớp B 100 %; OCR dưới 10 % trang cho doanh nghiệp demo **[KIẾN THỨC NỀN]** (`data/COLLECTION_PLAN_v2.md`, mục 6).

## 4. Vì sao chọn, phương án đã bỏ

- Gom split theo `content_group` chứ không theo `doc_id` **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 1).
- Bỏ heuristic "nhỏ trước" vì chỉ đưa được 11/15 doanh nghiệp vào test mà có 19,2 % claim; đổi sang "lớn vừa đủ trước": 7 doanh nghiệp, cùng tỷ lệ **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 4).
- Không crawl thêm trước khi có 100–200 claim adjudicate, vì crawl không làm dịch chuyển metric **[KIẾN THỨC NỀN]** (cùng file, mục 3).

## 5. Số đo có n

- 670 tài liệu Việt Nam; 297 văn bản pháp lý; 19.512 đơn vị, 15.658 đoạn, 938 điều khoản **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 2).
- 7.960 claim ứng viên và 3.786 evidence; 5.028 câu sạch và 3.682 câu ưu tiên **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 2).
- Split: 3.682 claim, 15 doanh nghiệp; giữ lại 7 doanh nghiệp, tỷ lệ test 19,9 % **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 4).
- 66.539 câu, 4.598 luật nhận là tuyên bố, 6.631 câu môi trường bị luật từ chối **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 2).
- Tập T1 đã định: dev 160 câu (nhãn thầy, chưa có nhãn người) và test 594 câu HPG (chưa gán) **[KIẾN THỨC NỀN]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 2).

## 6. Giới hạn và yếu tố gây nhiễu

- Doanh nghiệp `tra` chiếm 29,8 % claim; khoảng tin cậy khái quát hoá rất rộng. Báo cáo theo từng doanh nghiệp **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 4).
- Số doanh nghiệp không khớp: 21 trong kho; 15 trong tệp chia. Cần giải thích **[KIẾN THỨC NỀN]** (cùng file, mục 3 và 4).
- THIẾU: "2 055 nhãn Claude" trong checklist. Không thấy trong các nguồn đã đọc. Cách lấy: đếm trong `training/data/claude/` và `training/data/t1/`.

## 7. Lỗi đã gặp và cách gỡ

- Trùng nội dung và mất dấu: thêm `content_group`, `duplicate_of`, `ingestion_phase` và `MERGE_MANIFEST.json`; kiểm tổng `union → 297 unique` **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 1).

## 8. Trạng thái năng lực

- Unified và audited: **IMPLEMENTED–NOT VALIDATED** (8/8 bất biến kiểm tra được). Adjudicated: **OPEN QUESTION** (0,06 %).
- Gold (L5): 0; đóng băng sau 300–500 cặp **[KIẾN THỨC NỀN]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 2 và 5).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Adjudicate 100–200 claim, phủ đủ loại lỗi; cho phép nhiều evidence đúng cho một claim **[KIẾN THỨC NỀN]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 5).
- Mở rộng lên 40–60 doanh nghiệp, ưu tiên hơn thêm tài liệu cho 21 doanh nghiệp hiện có **[KIẾN THỨC NỀN]** (cùng file, mục 5).
- Sửa SQLite contention ở tầng ingestion **[KIẾN THỨC NỀN]** (cùng file, mục 5).

## 10. Hình nên vẽ và file dữ liệu

- Phễu L0 đến L5 (số lượng và trạng thái); cột claim theo doanh nghiệp.
- Dữ liệu: `data/crawl/vn30/curated/company_split.json`; `docs/04-data-ai/DATASET_AUDIT_V2.md`.
- THIẾU: gold người (adjudicate 100–200 claim). Chưa ghi người phụ trách. Cách lấy: ghi nhận người gán và nhập vào `reviewer workflow` để ghi thẳng vào L4.
