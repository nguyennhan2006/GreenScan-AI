# P10 · Quyền riêng tư, ngoại tuyến, che số (L1), hồ sơ chạy

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Dùng mô hình đám mây để đọc tài liệu mà không để lộ thông tin quan trọng: số liệu và tên doanh nghiệp. Việc chia ba nấc ngoại tuyến được mô tả trong `docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 1 **[KIẾN THỨC NỀN]**.

## 2. Lỗi hoặc rủi ro đã đo được

- Che số không làm mất độ chính xác trong sai số: gemma-4-31B đạt 32/32 và 18/19 khi che, so với 32/32 và 17/19 khi không che **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 5.1).
- Danh tính vẫn suy ra được từ ngữ cảnh: mô hình đoán đúng doanh nghiệp ở 5/20 câu tuyên bố và 3/3 trang đã che **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 5.3).
- Rủi ro trong đường hiện tại: khi bật `QUANTUM_LLM_STANCE=on_ambiguous`, câu tuyên bố và đoạn bằng chứng được gửi nguyên văn, không che số **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 3).

## 3. Thiết kế hiện tại, file code, cấu hình

- Chỉ ba nhóm mã trong `src/` gọi HTTP ra ngoài: `providers/*.py`, `retrieval/embeddings.py`, `retrieval/rerank.py`. OCR là tiến trình tại máy **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 3).
- Quy tắc dữ liệu: tài liệu công khai đi `offline` hoặc `cloud`; tài liệu nội bộ đi `offline`, `gpu` hoặc FPT Dedicated có hợp đồng **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-06).
- Chỉ FPT Dedicated ghim vùng dữ liệu; FPT Serverless có thể chuyển sang Nhật khi tải cao. Tài liệu mật chỉ đi `offline` hoặc `gpu` **[KIẾN THỨC NỀN]** (`configs/routing.yaml`, phần chú thích).
- Mã che số thử: `training/masking.py`; kế hoạch đưa vào `src/quantum_gw/privacy/` **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).

## 4. Vì sao chọn, phương án đã bỏ

- Chọn che số kèm cửa sổ ngắn (câu, dòng bảng), không gửi cả trang **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 0).
- Việc cần giữ kín danh tính khách hàng thì chỉ chạy ngoại tuyến hoàn toàn bằng mô hình học trò **[KIẾN THỨC NỀN]** (cùng file, mục 0).
- Bỏ Groq cho tài liệu người dùng: gói miễn phí có thể lưu dữ liệu. Groq chỉ cho báo cáo công khai **[KIẾN THỨC NỀN]** (`experiments/GROQ-PROBE/README.md`, giới hạn).

## 5. Số đo có n

- 51 ca, trong đó 20 câu tuyên bố và 3 trang thật. Giá trị số còn lại trong nội dung gửi đi: 0/51 ca; tên riêng còn lại: 0 **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 5.2).
- Xác nhận sai của gemma-4-31B: 2 khi không che, 0 khi che. Mâu thuẫn sai của GLM-5.2: 0 khi không che, 3 khi che **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 5.1).
- GROQ-PROBE: 12 câu, mỗi ô n = 12, chỉ đủ để sàng lọc cấu hình; chọn `openai/gpt-oss-120b` **[ĐÃ THỰC NGHIỆM]** (`experiments/GROQ-PROBE/README.md`).

## 6. Giới hạn và yếu tố gây nhiễu

- Che số không bảo vệ danh tính. Với ngành đặc thù, danh tính có thể bị suy ra **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 5.3).
- Kết quả phụ thuộc phiên bản model; bộ nhớ đệm ghi `prompt_version` và model **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 3).
- Mô hình học trò L2 chưa đo trên gold **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).

## 7. Lỗi đã gặp và cách gỡ

- Tên doanh nghiệp bị ngắt dòng trong PDF ("Hòa⏎Phát") lọt qua regex; đã cho phép mọi khoảng trắng giữa các chữ **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 5.2).
- Khoảng số như "5.6–6.2%" lọt; đã sửa để che cả hai đầu **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Khoá FPT bị 401 nên không dùng được thầy đám mây; dùng tạm Groq cho báo cáo công khai **[ĐÃ THỰC NGHIỆM]** (`experiments/GROQ-PROBE/README.md`).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Che số đã thử trên 51 ca, chưa đưa vào sản phẩm: "Đưa vào sản phẩm — việc kỹ thuật (chưa làm)" **[KIẾN THỨC NỀN]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 6).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đưa L1 vào đường gọi mô hình trước khi bật, với ngưỡng đăng ký trước **[KIẾN THỨC NỀN]** (`docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 8).
- Đường LLM hiện tại gửi nguyên văn; cần che số trước khi bật `on_ambiguous` ngoài phạm vi thử nghiệm **[GIẢ THUYẾT]**.
- THIẾU: nội dung mục 1 (ba nấc) và mục 8 (ngưỡng bật L1) của tài liệu OFFLINE. Cách lấy: đọc các mục đó; lượt này chưa đọc.

## 10. Hình nên vẽ và file dữ liệu

- Bảng ba mô hình trước và sau che số; biểu đồ số lần đoán đúng doanh nghiệp.
- Dữ liệu: `benchmark/size_ladder_2026-10-10/run_masked.py` và `reid_test.py`.
