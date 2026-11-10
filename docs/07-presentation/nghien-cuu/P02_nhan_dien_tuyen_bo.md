# P02 · Nhận diện tuyên bố (T1)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Phân loại từng câu của báo cáo thành QUANTIFIED_CLAIM, QUALITATIVE_CLAIM, VAGUE hoặc NOT_CLAIM. Bộ trích bằng luật bỏ sót và trích thừa, nên cần một mô hình học trò **[KIẾN THỨC NỀN]** (`training/README.md`, mục 1).

## 2. Lỗi hoặc rủi ro đã đo được

- Bộ trích bằng luật có precision 55 % (115/209) và recall 69 % (115/167) so với nhãn Claude trên tập train. Luật giữ gần một nửa câu không phải tuyên bố và bỏ sót khoảng một phần ba tuyên bố **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 11).
- Trên lô thử 400 câu, luật và thầy đồng ý 73 %. Theo đánh giá của thầy, luật trích thừa 34/120 câu nó nhận, và bỏ sót 36/160 câu môi trường nó từ chối **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 6).
- Thầy nhận "dự án do Chính phủ phê duyệt" là tuyên bố của doanh nghiệp **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 2).

## 3. Thiết kế hiện tại, file code, cấu hình

- Đầu vào là câu đã che số. Đầu ra là bốn lớp T1. Mô hình nền đề xuất: mDeBERTa-v3-base (MIT) hoặc multilingual-e5-base/small (MIT) **[KIẾN THỨC NỀN]** (`training/README.md`, mục 1).
- Thầy là `gemma-4-31B-it`. Nhãn thầy đi qua `training/teacher_label.py`, huấn luyện qua `training/train_classifier.py` **[KIẾN THỨC NỀN]** (cùng file, mục 2–3).
- Tập dữ liệu: train (500 câu Claude, còn 498 sau khi bỏ 2 câu UNSURE); dev (160 câu thầy đã gán, 12 công ty); test (594 câu HPG 2025, công ty mô hình chưa thấy) **[KIẾN THỨC NỀN]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 2 và 11).

## 4. Vì sao chọn, phương án đã bỏ

- Chọn mô hình nhỏ chạy CPU vì mục tiêu là không giảm độ chính xác mà vẫn chạy ngoại tuyến **[KIẾN THỨC NỀN]** (`training/README.md`, phần mở đầu).
- Bỏ nhãn yếu từ luật làm nhãn huấn luyện chính; chỉ dùng để chọn mẫu **[KIẾN THỨC NỀN]** (cùng file, mục 2).
- Bỏ bản soát 22 mục hàng đợi (Có/Không) để huấn luyện vì chỉ có hai đáp án, không đo được recall, và chỉ có một người gán **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 1).

## 5. Số đo có n

- 66.539 câu chưa gán; 4.598 câu luật nhận là tuyên bố; 6.631 câu có thuật ngữ môi trường mà luật từ chối **[ĐÃ THỰC NGHIỆM]** (`training/README.md`, mục 2).
- Nhãn Claude: κ A–B = 0,92 (5 nhãn), 0,98 (tuyên bố hay không); trùng 554/579 câu; 21 câu đổi nhãn sau khi đọc lại **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 11).
- Claude đồng ý với gemma 89/100 câu; κ 0,63 **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Học trò e5-base đạt macro-F1 0,71–0,73 trên nhãn Claude, kiểm chéo theo công ty, n = 1.217, 3 seed. Đây là nhãn bạc, chưa nối vào sản phẩm **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2).

## 6. Giới hạn và yếu tố gây nhiễu

- Gold người bằng 0 (0/79 câu trong cả ba gói T1). Mọi số trên là nhãn bạc **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0).
- Hai lượt Claude dùng cùng một mô hình, nên κ chỉ cho thấy ổn định, không cho thấy đúng **[KIẾN THỨC NỀN]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 11).
- 498 câu chưa đủ cho lớp hiếm; quy tắc R7 cần ít nhất 100 câu mỗi lớp **[KIẾN THỨC NỀN]** (cùng file).

## 7. Lỗi đã gặp và cách gỡ

- Thầy coi lời nói của chính phủ là tuyên bố doanh nghiệp. Hướng xử lý: đưa quy ước đã chốt vào `CLAIM_PROMPT` thành `teacher-claim-v2` trước khi chạy 4.000 câu **[KIẾN THỨC NỀN]** (`training/README.md`, mục 6).
- Quy ước Q10–Q17 mới chỉ là đề xuất, chờ họp 1 **[KIẾN THỨC NỀN]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 11).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Mã đã có. Chưa có gold người, chưa nối vào sản phẩm **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Gán gold T1 lô 1 (79 câu, ba người độc lập), hạn 14/10 theo lịch; mọi lô sau theo lịch mục 10 **[KIẾN THỨC NỀN]** (`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 10).
- Ngưỡng đề xuất chờ Nhân xác nhận: macro-F1 của thầy ≥ 0,70 và F1 tuyên bố ≥ 0,85 **[GIẢ THUYẾT]** (cùng file, mục 9).
- Học trò thay được luật khi macro-F1 ≥ luật và recall lớp tuyên bố cao hơn luật ít nhất 10 điểm **[GIẢ THUYẾT]** (`training/README.md`, mục 5).
- THIẾU: `CHON_MO_HINH_THEO_CONG_DOAN_2026-10-16.md`. Tệp này không có trong repo (Glob không thấy). Cách lấy: hỏi Nhân về tên hoặc vị trí đúng. Ngày 16/10 có khối `model-selection-v2` trong `configs/measurement_decisions.yaml` (dòng 63–79), chưa đọc nội dung trong lượt này.

## 10. Hình nên vẽ và file dữ liệu

- Ma trận nhầm lẫn luật với nhãn Claude; biểu đồ cột precision và recall. Dữ liệu: `training/data/t1/train_claude.jsonl`.
- Không mở `training/data/gold_t1/ai/claude_compare.jsonl` trước khi nộp nhãn lô 1 của chính mình, theo quy tắc trong quy trình gán nhãn.
