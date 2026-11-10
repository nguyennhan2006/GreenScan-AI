# P13 · Huấn luyện học trò và Kaggle

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Thay phần mô hình đám mây bằng mô hình nhỏ chạy trên CPU laptop, không giảm độ chính xác. Học trò chỉ làm phần đọc; mã vẫn quyết định **[KIẾN THỨC NỀN]** (`training/README.md`, phần mở đầu).

## 2. Lỗi hoặc rủi ro đã đo được

- Luật bỏ sót 13/51 ca; đối sánh là việc mô hình đám mây làm tốt khi che số **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 1).
- Huấn luyện trên CPU laptop: 1,7 mẫu mỗi giây, nên 10.000 mẫu × 3 epoch cần khoảng 5 giờ, không thực tế **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 4; chạy `training/runs/smoke_t1_e5small`).
- Bộ trích bằng luật sai ở cả hai chiều, theo đánh giá của thầy: trích thừa 34/120 câu nó nhận, bỏ sót 36/160 câu môi trường nó từ chối **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 6).

## 3. Thiết kế hiện tại, file code, cấu hình

- T1: mDeBERTa-v3-base hoặc multilingual-e5-base/small (MIT). T2: cross-encoder `gte-multilingual-reranker-base` (Apache-2.0). T2-gen: Qwen3 QLoRA, dự phòng **[KIẾN THỨC NỀN]** (`training/README.md`, mục 1).
- QLoRA: r = 32, α = 16, 2 epoch, lr 1e-4, trộn 1:1 ca gốc và ca nhiễu số **[KIẾN THỨC NỀN]** (cùng file, mục 4).
- Nhãn thầy `gemma-4-31B-it`, chạy ba lần, lấy đa số; 400 câu ≈ US$0,011, 26 giây **[KIẾN THỨC NỀN]** (cùng file, mục 2–3).
- Mã: `training/t1_data.py`, `teacher_label.py`, `train_classifier.py`, `latency_t1.py`, thư mục `training/kaggle/` **[KIẾN THỨC NỀN]** (cùng file).

## 4. Vì sao chọn, phương án đã bỏ

- Chọn mô hình nhỏ vì khối lượng (15.658 đoạn) và tính riêng tư, và vì việc là điền khuôn có schema **[KIẾN THỨC NỀN]** (`docs/04-data-ai/TARGET_PIPELINE_AND_TRAINING.md`, mục 3.2).
- Bỏ PhoBERT (AGPL-3.0) và VnCoreNLP (GPL-3.0) vì giấy phép không hợp định hướng thương mại **[KIẾN THỨC NỀN]** (`training/README.md`, mục 1).
- Bỏ nhãn yếu từ LLM làm nhãn chính: học trò trên dữ liệu LLM sinh mất 3–8 điểm ở tác vụ khách quan **[NGOÀI]** (Li và cs., EMNLP 2023, trích theo `training/README.md`, mục 2).

## 5. Số đo có n

- Kaggle T1 (v3): e5-base macro-F1 0,71–0,73 trên nhãn Claude, n = 1.217, 3 seed, kiểm chéo theo công ty **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2).
- Nhãn thầy: 400 câu lô thử; mục tiêu 4.000 câu × 3 lần ≈ US$0,5 **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).
- Suy luận ONNX int8 nhanh hơn 2–2,5 lần, mất tối đa 0,3 điểm **[NGOÀI]** (Hugging Face Optimum, trích theo `training/README.md`, mục 4).

## 6. Giới hạn và yếu tố gây nhiễu

- Kết quả Kaggle là trên nhãn Claude, không phải gold người. Chưa nối vào sản phẩm **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2).
- Thầy có thiên lệch: GPT-4 có F1 trung vị 0,707 trên 27 tác vụ, có tác vụ chỉ 0,059 **[NGOÀI]** (Pangakis và cs. 2023, trích theo `training/README.md`, mục 2).
- THIẾU: thời gian huấn luyện trên T4 cho 10.000 mẫu. Tài liệu ghi `[NOT FOUND]`. Cách lấy: đo 200 bước trên T4 rồi ngoại suy (`training/README.md`, mục 4).

## 7. Lỗi đã gặp và cách gỡ

- Thầy coi "dự án do Chính phủ phê duyệt" là tuyên bố doanh nghiệp **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 2).
- Hướng gỡ, chưa làm: đưa quy ước đã chốt vào `CLAIM_PROMPT` thành `teacher-claim-v2` trước khi chạy 4.000 câu **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).

## 8. Trạng thái năng lực

- T1: **IMPLEMENTED–NOT VALIDATED** (mã có; kết quả trên nhãn bạc).
- T2: **RESEARCH-BACKED–NOT IMPLEMENTED**.
- T2-gen: **OPEN QUESTION**, chỉ chạy nếu T2 không đạt **[KIẾN THỨC NỀN]** (`training/README.md`, mục 1).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Gán gold T1 lô 1 (79 câu, ba người) trước 22/10; sau đó chạy thầy 4.000 câu × 3 lần **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).
- Huấn luyện T1 trên T4 (mDeBERTa-xnli, e5-base); chạy `eval_student.py` trên gold và 51 ca **[KIẾN THỨC NỀN]** (cùng file, mục 6).
- AG-4 chỉ chạy nếu 1,7B kém 4B ít nhất 10 điểm **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, AG-4).
- Dự đoán: 1,7B tinh chỉnh đạt độ đúng IR không kém 8B zero-shot **[GIẢ THUYẾT]** (cùng file, AG-4).

## 10. Hình nên vẽ và file dữ liệu

- Đường cong học theo số mẫu; bảng ba cổng (học trò so với luật và thầy).
- Dữ liệu: `training/runs/kaggle_t1_v3/results.json`; `training/data/t1/train_claude.jsonl`.
