# P15 · Chương trình agent (mượn từ ZAIC: AG-0 … AG-6)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Dùng cách làm của một dự án cuộc thi khác (ZAIC) để trị các lỗi đã đo của GreenScan, trên Kaggle, trong thời gian từ 31/10 đến 10/11/2026. Chỉ mượn thành phần nào trị được một lỗi đã đo **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0).

## 2. Lỗi hoặc rủi ro đã đo được

Bảng F1–F7 trong kế hoạch **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 2):

- F1: kết luận phẳng, 153 khớp một phần trên 156 tuyên bố.
- F2: luật phủ thấp; quyết định 8/32 ca bộ sạch.
- F3: bảng PDF dàn phẳng; mọi mô hình báo SUPPORTED sai trên N02, N05.
- F4: năm lỗi chuẩn hoá. F5: 0 quy tắc pháp lý áp được trên 156 tuyên bố.
- F6: bằng chứng chỉ có nguồn nội bộ. F7: không có gold người (0/88 cặp, 0/79 câu).

## 3. Thiết kế hiện tại, file code, cấu hình

- Sáu thí nghiệm AG-0 đến AG-6 và bản đồ mượn từ ZAIC **[KIẾN THỨC NỀN]** (cùng file, mục 3 và 5).
- Mỗi thí nghiệm có phiếu riêng `experiments/AG-*/README.md`, ghi dự đoán trước khi đẩy **[KIẾN THỨC NỀN]** (cùng file, mục 5).
- AG-1: LLM nhỏ điền IR, `irlib` kết luận tất định, `experiments/AG-1/ag1_worker.py` **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 3–4).

## 4. Vì sao chọn, phương án đã bỏ

- Không bê nguyên ZAIC vì GreenScan không có gold người và ràng buộc khác **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 1).
- Không mượn RL/GRPO (cần phần thưởng kiểm được), đa tác tử tự do (trái bất biến 5), và phần âm thanh **[KIẾN THỨC NỀN]** (cùng file, mục 3).
- Dự đoán đã đăng ký cho AG-1: 4B đạt độ phủ ≥ 0,35 với precision ≥ 0,90. Kết quả: độ phủ 0,134, sai **[GIẢ THUYẾT → ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 2 và 5).

## 5. Số đo có n

- AG-1 (193 ca, lượt A và C): luật độ phủ 0,028 precision 0,75; 4B độ phủ 0,134 precision 1,00; 32B độ phủ 0,423, precision 0,82, 7 CONTRADICTED sai **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 5).
- Lượt B (8B, 14B, gemma) còn đang chạy **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Chưa model nào qua cổng `ag1_ir_path_usable` **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 6. Giới hạn và yếu tố gây nhiễu

- Không có gold người; nhãn B-b là nhãn bạc **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 6).
- Bốn tài khoản Kaggle, ước tính 25–40 giờ GPU T4, dưới một phần ba quota tuần **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0).
- Khoá FPT bị 401 ngày 31/10 nên không gọi được API **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 3).

## 7. Lỗi đã gặp và cách gỡ

- Dự đoán cho 4B và 32B sai; ghi nhận, không đổi ngưỡng đã đăng ký **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 5; `configs/measurement_decisions.yaml`).
- Shell nuốt dấu `\` khi viết regex; đã sửa **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 7).

## 8. Trạng thái năng lực

- AG-0: **OPEN QUESTION** (chưa chạy). AG-1: **IMPLEMENTED–NOT VALIDATED** (chưa qua cổng).
- AG-2 đến AG-6: **RESEARCH-BACKED–NOT IMPLEMENTED** hoặc có điều kiện (AG-4 chỉ khi 1,7B kém 4B ≥ 10 điểm; AG-6 sau AG-0) **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 5).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- AG-0 (01–02/11): phép thử oracle, xác định tầng làm mất điểm nhiều nhất **[KIẾN THỨC NỀN]** (cùng file, AG-0).
- AG-2 (04–05/11): hai đường, cổng đồng thuận, abstain. Dự đoán: độ phủ từ khoảng 25 % lên ít nhất 50 % ở cùng precision **[GIẢ THUYẾT]** (cùng file, AG-2). Lưu ý: con số 25 % cho luật không khớp với 2,8 % đo trên B-b trong AG-1; cần làm rõ nguồn trước khi báo cáo.
- AG-2 vào sản phẩm chỉ dưới dạng huy hiệu và thứ tự hàng đợi; verdict không đổi **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 5; `configs/measurement_decisions.yaml`, dòng 131).

## 10. Hình nên vẽ và file dữ liệu

- Bảng bản đồ mượn (thành phần ZAIC → lỗi → thí nghiệm); biểu đồ độ phủ và precision theo mô hình.
- Dữ liệu: `experiments/AG-1/out_score_partial.json`; `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`.
- THIẾU: kết quả AG-0 và AG-2 đến AG-6, và quyết định của người dùng ngày 31/10 (mục 9 của kế hoạch chưa đọc). Cách lấy: đọc mục 9 và 10 của kế hoạch; chạy AG-0 theo phiếu.
