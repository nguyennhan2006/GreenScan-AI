# P05 · Kiểm chứng định lượng

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Đối chiếu số trong tuyên bố với số trong bằng chứng: cộng ngang, khớp đơn vị, khớp kỳ và phạm vi, dung sai theo độ chính xác công bố. Kết luận số học thuộc về mã, không thuộc về mô hình **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 4–5).

## 2. Lỗi hoặc rủi ro đã đo được

- Năm lỗi chuẩn hoá (cường độ với tuyệt đối, công ty mẹ với tập đoàn, ngưỡng 0,35 che chênh 9–25 %, bỏ sót "sử dụng … nước", không cộng ngang tổng) **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, F4).
- Trên HPG, lượt 22/10: 153 khớp một phần, 2 ủng hộ, 1 chưa đủ bằng chứng trên 156 tuyên bố **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, F1).
- Luật đúng 6/8 kết luận trên bộ sạch và 3/3 trên trang thật (cỡ mẫu nhỏ) **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, mục 2).

## 3. Thiết kế hiện tại, file code, cấu hình

- Năm lớp kiểm: tính cụ thể; khả năng có bằng chứng; nhất quán định lượng; khớp luật và phân loại; mâu thuẫn từ bên ngoài **[KIẾN THỨC NỀN]** (`docs/04-data-ai/VERIFICATION_POLICY.md`, mục 5).
- Năm verdict: SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE **[KIẾN THỨC NỀN]** (cùng file, mục 6).
- Dung sai số: ½ chữ số cuối đã công bố, trần 10 %; lệch ≥ 0,35 thì bác bỏ **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2).
- Kiểm thử: `tests/test_verdict_traps.py` có 47 hàm `def test_`; `tests/test_architecture_invariants.py` có 15 **[ĐÃ THỰC NGHIỆM]** (đếm bằng grep).

## 4. Vì sao chọn, phương án đã bỏ

- Số học do mã tính, mô hình chỉ đọc. Bỏ LLM judge ghi đè comparator vì trái bất biến 5 **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bảng cấm).
- Bỏ dung sai 12 % và ngưỡng CONTRADICTS 35 % cố định; thay bằng `comparison_policy` theo loại giá trị **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-03).

## 5. Số đo có n

- Size ladder 10/10: 51 ca (32 sạch, 19 trang thật). Luật: 20/32 và 7/19 đúng **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, mục 2).
- Mô hình GLM-5.2 cho kết quả khác nhau giữa hai lượt chạy (17/19 rồi 16/19) dù nhiệt độ 0 **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 5.1).
- Mâu thuẫn sai: luật 1; LLM tự quyết 10 khi không chốt chặn **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`).

## 6. Giới hạn và yếu tố gây nhiễu

- Cỡ mẫu 51 ca, do nhóm dựng. Chưa có gold verdict; theo quy tắc, không nói độ chính xác khi gold dưới 60 hoặc κ dưới 0,70 **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 2).
- Bảng dàn phẳng khiến mô hình thấy số giống hệt và báo "khớp hoàn toàn" **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, mục 5.1).
- Sai khác cần làm rõ: checklist và `measurement_decisions.yaml` ghi 17 bẫy xanh; bất biến 4 ghi 44 trap; tệp test có 47 hàm. Cần thống nhất con số trước khi báo cáo **[KIẾN THỨC NỀN]**.

## 7. Lỗi đã gặp và cách gỡ

- Lỗi verdict 22/09: 5/8 mâu thuẫn sai do so khác Scope, khác tập đoàn, khác đơn vị. Gỡ bằng bất biến 4 và 44 ca trap **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bảng cấm).
- Trần severity PARTIALLY_SUPPORTED là MEDIUM cho tới khi có calibration gold **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-03).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Có kiểm thử hồi quy, chưa có gold verdict **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-05).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Gán gold verdict trên 100–200 claim thật, phủ đủ các loại lỗi **[KIẾN THỨC NỀN]** (`docs/04-data-ai/DATASET_AUDIT_V2.md`, mục 5).
- Phép thử oracle (AG-0): thay từng tầng bằng đáp án đúng để biết tầng nào làm mất nhiều nhất **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 3).
- Dự đoán AG-0: phần lớn chênh nằm ở bảng và ánh xạ, không ở truy xuất **[GIẢ THUYẾT]** (cùng file, AG-0).

## 10. Hình nên vẽ và file dữ liệu

- Lưu đồ năm lớp kiểm và năm verdict; bảng size ladder (luật, các mô hình sạch và trang thật).
- Dữ liệu: `benchmark/size_ladder_2026-10-10/` (README và `run_masked.py`); `tests/test_verdict_traps.py`.
