# P12 · Đo lường: giao thức, ngưỡng đăng ký trước, bootstrap

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Trả lời các câu hỏi về truy xuất, quan hệ từng cặp, kết luận và thời gian, với ngưỡng quyết định đã ghi trước khi có số. Đây là cách tránh tự chọn ngưỡng sau khi thấy kết quả **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 1).

## 2. Lỗi hoặc rủi ro đã đo được

- Các ngưỡng cũ có thể làm người nghe hiểu nhầm. Đã bỏ hằng số 12 % và ngưỡng 35 % **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-03).
- Dự đoán AG-1 đăng ký trước đã sai ở cỡ 4B: đăng ký ≥ 0,35, đạt 0,134. Việc đăng ký giúp phát hiện điều này **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 5).
- Thiên lệch pooling: tuyên bố chỉ có nhãn trên các trang đã đề xuất, nên mức tăng đo được là cận dưới **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 3).

## 3. Thiết kế hiện tại, file code, cấu hình

- Ngưỡng nằm trong `configs/measurement_decisions.yaml`. Đăng ký 29/09/2026. Công cụ đọc thẳng từ file đó **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, đầu trang).
- Khối `agentic_v1` đăng ký 31/10/2026, trước khi thấy đầu ra của mô hình AG-1 **[KIẾN THỨC NỀN]** (`configs/measurement_decisions.yaml`, dòng 117–118).
- Mọi số có n và khoảng tin cậy bootstrap 95 %, so theo cặp; bootstrap theo công ty với 2.000 lần lặp **[KIẾN THỨC NỀN]** (cùng file, dòng 125; `docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 1).
- Công cụ: `tools/measure_all.py`, `tools/labeling_pack.py` **[KIẾN THỨC NỀN]** (cùng file, mục 5).

## 4. Vì sao chọn, phương án đã bỏ

- Đăng ký trước vì đổi ngưỡng sau khi thấy số làm vô hiệu phép đo **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, đầu trang).
- Bỏ BGE-M3 local vì quá chậm trên máy không GPU (0,49 trang/s); dùng API FPT **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 4).

## 5. Số đo có n

- Thư viện 11 doanh nghiệp: 15.409 trang, 14.708 vector **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 4).
- Bộ AG-1: 193 ca (51 B-a, 142 B-b). Luật: độ phủ 0,028, precision 0,75 **[ĐÃ THỰC NGHIỆM]** (`configs/measurement_decisions.yaml`, dòng 123).
- Chưa có gold người nên chưa báo số nào. Ngưỡng: không báo khi gold dưới 60 hoặc κ dưới 0,70 **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 2).

## 6. Giới hạn và yếu tố gây nhiễu

- B-b là nhãn bạc, sinh từ 5 doanh nghiệp, không đại diện ngành phát thải cao **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 6).
- Mô hình qua API thay đổi theo phiên bản; kết quả cùng model có thể khác giữa hai lượt **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, mục 5.1).

## 7. Lỗi đã gặp và cách gỡ

- Các ngưỡng cũ được thay bằng quy tắc theo loại giá trị (`comparison_policy`) **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-03).
- Báo cáo tự bật cảnh báo "chỉ dùng nội bộ" khi gold dưới 60 hoặc κ dưới 0,70 **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 4, chạy thử trên nhãn giả).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Giao thức và công cụ có; chưa có gold để đo **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 4).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Khi có gold lô 1: chạy `labeling_pack.py import-all`, rồi `measure_all.py`; so với luật đã đăng ký **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 5).
- Cổng AG-1 sang AG-2: precision ≥ 0,90; cận dưới CI95 ≥ 0,80; CONTRADICTED sai không vượt luật quá 1 **[KIẾN THỨC NỀN]** (`configs/measurement_decisions.yaml`, dòng 127–130).
- THIẾU: kết quả đo trên gold. Cách lấy: chạy `measure_all.py` sau khi nhận gold của Quỳnh và Thảo.

## 10. Hình nên vẽ và file dữ liệu

- Biểu đồ độ phủ và precision, có khoảng CI95; biểu đồ rừng cho từng doanh nghiệp.
- Dữ liệu: `configs/measurement_decisions.yaml`; `experiments/AG-1/out_score_partial.json`.
