# P06 · Đọc lập trường bằng LLM (có chốt, `decisive=false`)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Với các cặp tuyên bố–bằng chứng mà luật từ khoá và phép so số không quyết được, mô hình đọc quan hệ (xác nhận, phủ nhận, chỉ bối cảnh, một phần) **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2, bước 6).

## 2. Lỗi hoặc rủi ro đã đo được

- Khi để mô hình tự quyết, 10 CONTRADICTED và 2 CRITICAL xuất hiện trên doanh nghiệp đối chứng, phần lớn sai khi soát tay: câu dính cột, dòng bảng lỗi "GIỚI TÍNH: 100 %" bị đọc thành "100 % nam" **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`, mục "Đọc bảng").
- Khi tắt LLM, 713 cặp mặc định PARTIAL vì giống chữ **[ĐÃ THỰC NGHIỆM]** (cùng file, bảng A/B).

## 3. Thiết kế hiện tại, file code, cấu hình

- Bật bằng `QUANTUM_LLM_STANCE=on_ambiguous`. Chốt chặn `llm_stance_decisive: false`: lập trường của mô hình một mình không tạo SUPPORTED hay CONTRADICTED; nghi mâu thuẫn thì ra PARTIALLY_SUPPORTED và chuyển người xem **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-28-01; `benchmark/llm_stance_ab_2026-09-28.md`).
- Mã: `verification/llm_judge.py` **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 3).
- Định tuyến theo nhiệm vụ: `configs/routing.yaml`. Chỉ GLM-5.2 là tuyến đang hoạt động; gemma-4-31B-it là phương án rẻ hơn **[KIẾN THỨC NỀN]** (`configs/routing.yaml`, phần chú thích).

## 4. Vì sao chọn, phương án đã bỏ

- Chọn GLM-5.2 qua FPT vì là tuyến duy nhất đang hoạt động ở vùng dữ liệu Việt Nam **[KIẾN THỨC NỀN]** (`configs/routing.yaml`, chú thích).
- Bỏ Qwen3.6-27B và DeepSeek-V4-Flash vì vùng dữ liệu Nhật Bản; Llama-3.3-70B vì tiếng Việt không phải ngôn ngữ chính thức **[KIẾN THỨC NỀN]** (`configs/routing.yaml`; `docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-05).
- Bỏ Groq cho tài liệu người dùng vì gói miễn phí có thể lưu dữ liệu; Groq chỉ dùng cho báo cáo công khai **[KIẾN THỨC NỀN]** (`experiments/GROQ-PROBE/README.md`, giới hạn).

## 5. Số đo có n

- A/B trên HPG (156 tuyên bố, 713 cặp mà luật không quyết): không LLM 153/2/0/1; LLM không chốt 136/6/10/4; LLM có chốt 150/2/0/4 (PARTIAL/SUPPORTED/CONTRADICTED/INSUFFICIENT) **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`).
- Mức rủi ro HIGH và CRITICAL: 0; 8+2; 0. Câu chuyển người: 0; 156; 13 **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Gọi API 710 lần, 451 giây, 0 lỗi **[ĐÃ THỰC NGHIỆM]** (cùng file).
- THIẾU: so sánh offline và cloud "lệch 3/156". Không có trong hai nguồn đã đọc. Cách lấy: tìm kết quả chạy offline và cloud trong `benchmark/` và so từng tuyên bố.

## 6. Giới hạn và yếu tố gây nhiễu

- Chưa biết 151 SUPPORTS và 12 CONTRADICTS của mô hình đúng bao nhiêu phần. Phải trả lời trên gold lô 1 **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`, mục "Chưa nói được").
- Cùng nhiệt độ 0 nhưng hai lượt cho 17/19 và 16/19 **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, mục 5.1).
- Không dùng nhãn Claude để tháo chốt `llm_stance_decisive` **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0, trích D-2026-10-16-01).

## 7. Lỗi đã gặp và cách gỡ

- Để mô hình quyết trực tiếp gây lỗi. Gỡ bằng chốt chặn `decisive=false` và cờ người xem chỉ bật khi mô hình đổi kết luận so với luật (13/156) **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Đường chạy đã có, chốt chặn đã bật; độ đúng trên gold chưa đo **[KIẾN THỨC NỀN]** (`benchmark/llm_stance_ab_2026-09-28.md`).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đo `evaluate_gold` với LLM tắt, bật và bật có chốt trên gold lô 1 **[KIẾN THỨC NỀN]** (`benchmark/llm_stance_ab_2026-09-28.md`, mục "Chưa nói được").
- Chỉ tháo chốt cho quan hệ mà gold chứng minh đủ đúng **[KIẾN THỨC NỀN]** (cùng file).
- Câu hỏi mở: 151 SUPPORTS và 12 CONTRADICTS của mô hình đúng bao nhiêu phần. Chưa có đáp án, nên chưa có dự đoán đăng ký **[GIẢ THUYẾT]** (`benchmark/llm_stance_ab_2026-09-28.md`).

## 10. Hình nên vẽ và file dữ liệu

- Bảng A/B ba cột (tắt, bật không chốt, bật có chốt) dạng biểu đồ cột; phân bố quan hệ theo cách quyết.
- Dữ liệu: `benchmark/llm_stance_ab_2026-09-28.md`; `configs/routing.yaml`.
