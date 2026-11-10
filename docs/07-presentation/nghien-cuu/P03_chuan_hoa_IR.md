# P03 · Chuẩn hoá tuyên bố thành IR (AG-1)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Chuyển câu tuyên bố và câu bằng chứng thành biểu diễn trung gian (IR): chỉ số, giá trị, đơn vị, kỳ, phạm vi, loại giá trị, thực hiện hay mục tiêu. Mô hình nhỏ chỉ điền IR; thư viện `irlib` tất định kết luận **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 2–3).

## 2. Lỗi hoặc rủi ro đã đo được

- Luật hiện tại quyết định 4/142 ca B-b (độ phủ 2,8 %). Luật bắt được 0/44 ca mâu thuẫn **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 1; số liệu từ `experiments/AG-0/out/score_rules.json`).
- Trong 109 số liệu đọc được, người đọc đánh dấu 75 số "không chắc" và bỏ; B-b còn 26 số **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 7; `benchmark/gs_bench_v1/stats.json`).

## 3. Thiết kế hiện tại, file code, cấu hình

- Mỗi văn bản đi qua cùng một prompt trích IR, giải mã greedy, tắt thinking, trả JSON **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 3).
- Mỗi số của tuyên bố so với mọi số của bằng chứng bằng `irlib.decide`, cho S (khớp), C (mâu thuẫn) hoặc N (chuyển người) **[KIẾN THỨC NỀN]** (cùng file).
- File: `experiments/AG-1/ag1_worker.py`, `irlib.py`, `llm.py`, `multirun.py`, `nb_a.ipynb` (≤ 4B) và `nb_b.ipynb` (≥ 8B), chạy trên hai tài khoản Kaggle **[KIẾN THỨC NỀN]** (cùng file, mục 4).

## 4. Vì sao chọn, phương án đã bỏ

- Tách "đọc" khỏi "tính" để giữ bất biến 5 (số học thuộc về mã) **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 3).
- Bỏ LLM tự phán S/C/N vì size ladder cho thấy SUPPORTED sai trên bảng dàn phẳng **[ĐÃ THỰC NGHIỆM]** (cùng file, bảng phương án bỏ).
- Bỏ guided decoding vì tham số vLLM đổi theo phiên bản; bỏ gọi API vì khoá FPT bị 401 ngày 31/10 **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 5. Số đo có n

- Bộ đo: 193 ca = B-a 51 + B-b 142. B-b có 33 ca S, 44 ca C, 65 ca N; 5 doanh nghiệp (tra 46, pnj 24, bvh 5, dhg 37, vnm 30 ca) **[ĐÃ THỰC NGHIỆM]** (`benchmark/gs_bench_v1/stats.json`).
- Kết quả trên B-b (độ phủ; precision CI95; CONTRADICTED sai):
  - luật: 0,028; 0,75; 0;
  - Qwen3-0.6B: 0,127; 0,39; 4;
  - Qwen3-1.7B: 0,183; 0,54; 8;
  - Qwen3-4B: 0,134; 1,00 [1,0; 1,0]; 0;
  - Qwen3-32B-AWQ: 0,423; 0,82 [0,69; 1,0]; 7;
  - trần (IR gold): 0,528; 1,00; 0 **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 5).
- Sai khác trong tài liệu: mục 4 liệt kê Qwen3-8B, 14B-AWQ và gemma-3-12B, nhưng mục 5 chỉ có kết quả 32B. Lượt B còn chạy **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 6. Giới hạn và yếu tố gây nhiễu

- Nhãn B-b là nhãn bạc: Claude đọc IR bằng chứng một lượt, rồi qua kiểm tất định **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 6).
- Chỉ 5 doanh nghiệp, không phải ngành phát thải cao; tuyên bố sinh bằng khuôn câu, nên dễ đọc hơn tuyên bố thật **[KIẾN THỨC NỀN]** (cùng file).
- Máy T4 khác laptop của người dùng **[KIẾN THỨC NỀN]** (cùng file).

## 7. Lỗi đã gặp và cách gỡ

- Shell nuốt dấu `\` khi viết regex, sinh ký tự điều khiển trong `build.py`; đã sửa bằng `chr(92)` **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 7).
- Smoke đầu lỗi `No module named vllm` vì `multirun` tự đặt backend; đã thêm ứng viên `hf` **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Chưa model nào qua cổng `ag1_ir_path_usable`: 4B không bị chặn nhưng độ phủ thấp, 32B hụt precision ≥ 0,90 **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-1/README.md`, mục 5).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đọc 7 ca CONTRADICTED sai và 4 ca SUPPORTED sai của 32B để tách lỗi đọc IR với lỗi `irlib` **[KIẾN THỨC NỀN]** (cùng file, mục 5).
- Dự đoán đã đăng ký: 4B đạt độ phủ ≥ 0,35. Kết quả: 0,134, **sai**. 0.6B không dùng được: **đúng** **[GIẢ THUYẾT → ĐÃ THỰC NGHIỆM]** (`configs/measurement_decisions.yaml`, khối `agentic_v1`; `experiments/AG-1/README.md`, mục 5).
- Nếu 1.7B kém 4B ≥ 10 điểm thì mở AG-4 (QLoRA) **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 10).

## 10. Hình nên vẽ và file dữ liệu

- Cột độ phủ và precision theo model, có mốc luật và mốc trần; ma trận họ nhiễu × model.
- Dữ liệu: `experiments/AG-1/out_score_partial.json` (bản chấm lượt A và C). File `out/score_ag1.json` mà tài liệu nêu chưa có trong thư mục đã kiểm.
