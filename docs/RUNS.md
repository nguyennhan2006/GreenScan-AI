# Lượt chạy Kaggle của GreenScan

Kế hoạch: [00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md](00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md).

**Tài khoản:** 12 tài khoản dự phòng trong `C:\Users\ASUS\.kaggle\acc_kaggle_du_phong.env`. ZAIC không dùng file này. Phân vai ở mục 6 của kế hoạch.

**Công cụ:** `tools/kaggle/kapi.py` (push, status, logs, output, delete) và `tools/kaggle/build_nb.py`.

**Luật** (`~/.claude/CLAUDE.md` mục 5):
- Mọi cell mở bằng `print("[cell] …", flush=True)`.
- Lúc đẩy, ghi hai mốc: có log đầu (giờ đẩy + 10 phút) và xong.
- Không có log tới mốc: chờ thêm 30 phút. Vẫn không có thì xoá, rồi đẩy lại trên tài khoản khác.
- Notebook treo thì xoá, không cancel.

| Đẩy (giờ VN) | Notebook | Việc | Mốc log đầu | Mốc xong | Trạng thái |
|---|---|---|---|---|---|
| 31/10 ~10:40 | `thanhtruc02/gs-ag1-a-smoke` (v2) | AG-1 smoke trên CPU: Qwen3-0.6B qua transformers, 3 ca. v1 lỗi `No module named vllm`; v2 thêm ứng viên `hf` | có (model nạp xong ở t = 77 s) | sinh trên CPU chậm | **COMPLETE** (t = 202 s): đường ống đầu–cuối chạy; 0.6B đúng 0/3 ca B-a (đúng như dự đoán) |
| 31/10 10:56 | `thanhtruc02/gs-ag1-a` | **AG-1 A** (GPU T4 × 2): Qwen3-0.6B, Qwen3-1.7B, Qwen3-4B-Instruct-2507, TP 1, trên 193 ca | 11:06 | khoảng 11:20 (chậm nhất 11:45) | **COMPLETE**, tải 11:41 về `experiments/AG-1/kaggle_out/a/`; số ở README AG-1 mục 5 |
| 31/10 10:56 | `vantiennhuannguyen/gs-ag1-b` | **AG-1 B** (GPU T4 × 2): Qwen3-8B, Qwen3-14B-AWQ, gemma-3-12b-it (unsloth), TP 2 | 11:06 | khoảng 11:40 (chậm nhất 12:15) | **COMPLETE**, tải 14:00 về `experiments/AG-1/kaggle_out/b/`. 14B: độ phủ B-b 0,254, precision 0,944. gemma-12B trả `raw` rỗng cho mọi câu (OOM lúc nạp, rồi sinh rỗng), nên loại khỏi thang |
| 31/10 11:03 | `hdonqu/gs-ag1-c` | **AG-1 C** (GPU T4 × 2): Qwen3-32B-AWQ (32,8B, Apache-2.0), TP 2, chạy thay API trả phí (khoá FPT 401). Hai vai: (1) một hệ trên 193 ca, mốc model lớn; (2) người đọc thứ hai cho 211 câu `candidates.jsonl`, để mở rộng B-b bằng số liệu Claude và Qwen-32B cùng đọc giống nhau | 11:13 | khoảng 11:40 (chậm nhất 12:30) | **COMPLETE**, tải 11:41 về `experiments/AG-1/kaggle_out/c/`: 193 ca đúng 144, chép xong 211 câu đọc lần hai |
| 31/10 14:13 | `thanhtruc02/gs-ag1-d` | **AG-1 D** (T4 × 2, TP 1): Qwen3-4B-Instruct-2507 và Qwen3-1.7B trên GS-Bench **v1.1** (453 ca, 507 câu), có `irlib.ground()`. Kiểm `ground` trên 260 ca B-b chưa model nào đọc (đăng ký `agentic_v1_1`) | 14:23 | khoảng 14:55 (chậm nhất 15:30) | **COMPLETE** khoảng 14:29 (nạp 239 s, sinh 278 s cho 507 câu), tải về `experiments/AG-1/kaggle_out/d/`. Ngoài mẫu 246 ca: 4B có `ground` đạt độ phủ 0,126, precision 0,903, CONTRADICTED sai 2 (qua cổng an toàn sát nút; dự đoán độ phủ sai). `kapi live` trả 0 dòng với cả ba lượt dù hạn mức đang tăng: lỗi công cụ, không phải treo |
| 31/10 14:13 | `vantiennhuannguyen/gs-ag1-e` | **AG-1 E** (T4 × 2, TP 2): Qwen3-8B rồi Qwen3-14B-AWQ, cùng bộ v1.1 | 14:23 | khoảng 14:50 (chậm nhất 15:30) | **COMPLETE** (8B 509 s, 14B 436 s; 0 câu không parse). Đã tải và chấm 22:40: ngoài mẫu 246, 8B ground 0,220 / 0,963 / false_C 1; 14B ground 0,256 / 0,921 / false_C 3. Kết quả trong `measurement_decisions.yaml` `agentic_v1_1.result_held_out_246_runs_E_F` |
| 31/10 14:14 | `hdonqu/gs-ag1-f` | **AG-1 F** (T4 × 2, TP 2): Qwen3-32B-AWQ trên v1.1, và đọc lần hai 800 câu `candidates_v2.jsonl` (mở rộng v1.1, việc 5). Tổng 1 273 câu. Lần đẩy đầu bị 400 vì notebook quá 1 MB; đã rút bộ nhúng chỉ còn `id/claim/evidence/labels` (639 KB) | 14:24 | khoảng 15:45 (chậm nhất 16:30) | **COMPLETE** (1 290 s; 0 câu không parse). Đã tải và chấm 22:40: ngoài mẫu 246, 32B ground 0,329 / 0,951 / false_C 2. Bản đọc `candidates_v2` dùng làm reader A cho tập ngoài mẫu v1.2 (`gs_heldout_v12.jsonl`, 162 ca) |
| 31/10 22:42 | `nguyenlethaonhi123/gs-ag1-g` | **AG-1 G** (T4 × 2): Qwen3-4B-Instruct-2507 (TP 1), Qwen3-8B, Qwen3-14B-AWQ, Qwen3-32B-AWQ (TP 2) đọc tập ngoài mẫu v1.2 `gs_heldout_v12.jsonl` (162 ca, 186 câu; `GS_BENCH` trong jobs). Kiểm đăng ký `agentic_v1_2` (sửa đổi 22h50). Tài khoản mới vì còn nhiều GPU nhất (28,2 h) | 22:52 | khoảng 23:20 (chậm nhất 00:00) | **COMPLETE** (4B 312 s, 8B 379 s, 14B 316 s, 32B 579 s; 0 câu không parse). Tải và chấm 23:25: mọi dự đoán `agentic_v1_2` đứng; 37 % ca của tập là `other_env` không phải môi trường (lỗi tập). Xem `agentic_v1_2.result_held_out_162_run_G` |
| 01/11 17:02 | `rehoanzun/gs-ag2-q4-parity` | **agentic_ag2_product, nửa "cùng kết quả"** (laptop thiếu RAM): bộ đọc sản phẩm (Ollama GGUF + `ir_reader.py` + `product_reader.py`) trên tập G (162 ca), so với 4B bf16 của lượt G; Q4_K_M (đăng ký) và Q8_0 (thăm dò). Thời gian đọc trên T4 không phải thời gian trên laptop | 17:12 | khoảng 17:25 (chậm nhất 17:50) | **COMPLETE** 17:15, tải về `experiments/AG-2/out/kaggle_parity/`. Q4 khớp 0,963, Q8 khớp 0,981 với 4B bf16; luật + 4B cục bộ trên G: 0 sai, độ phủ 0,080 (Q4). Dự đoán `agentic_ag2_product` đứng vững |

**Khi xong:**
1. Tải đầu ra: `python tools/kaggle/kapi.py output thanhtruc02/gs-ag1-a --dest experiments/AG-1/kaggle_out/a` (tương tự cho b).
2. Chấm: `.venv/Scripts/python.exe -I experiments/score.py rules=experiments/AG-0/out/rules.jsonl q3-4b=experiments/AG-1/kaggle_out/a/out/q3-4b-inst_cases.jsonl ... --json experiments/AG-1/out/score_ag1.json`.
3. Điền mục 5 của `experiments/AG-1/README.md`, đối chiếu với dự đoán trong `agentic_v1`.
