# Huấn luyện cho hai phương án chạy: ngoại tuyến (PA1) và GPU tự thuê (PA2), 13/11/2026

**Quyết định của Nhân (13/11):**
- PA1, ngoại tuyến hoàn toàn: huấn luyện ngay trên Kaggle, được dùng mọi tài khoản dự phòng.
- PA2: chuẩn bị một thư mục để tải lên máy vast.ai A100 và chạy.
- Nhãn cặp: Claude gán nốt rồi chốt. Q13 sửa theo v1.2.
- Đầu ra cần có biểu đồ, đánh giá chất lượng và bảng chi phí sinh từ Python.

Dự đoán và cổng được đăng ký **trước** khi huấn luyện, ở `configs/measurement_decisions.yaml`, khối `offline_training_v1` (09:05).

## 1. Nhãn đã làm hôm nay (nhãn bạc, chờ người soát)

| Bộ | Cách làm | Kết quả |
|---|---|---|
| 821 cặp tuyên bố – đoạn (`training/data/claude/pairs/labels.jsonl`) | Claude gán 2 lượt mù theo CAP v1.0 (17 lượt còn thiếu làm hôm nay), ghép, phân xử 191 cặp. **Bỏ bước soát mù** (`finalize --audit-optional`) | CONTEXT 633 · PARTIAL 125 · SUPPORTS 63 · **CONTRADICTS 0**. Độ liên quan 0/1/2: 260 / 373 / 188. κ A–B về quan hệ: 0,78–1,0 ở 11 lô; riêng p02 0,33 (nhãn cũ 16/10), 14 nhãn thứ ba do người phân xử đặt |
| Q13 v1.2 (`training/data/claude/q13/q13_relabel_v1.2.jsonl`) | Gán lại 164 câu T1 đang là `NOT_CLAIM / table_heading` có số | Chỉ **31 câu** thành tuyên bố (16 định lượng, 14 định tính, 1 mơ hồ). 64 câu chuyển sang `non_env`, 62 câu giữ `table_heading` |

**Hệ quả cần biết:**
- Bộ cặp không có ca phản bác nào, nên không mô hình nào học được CONTRADICTS từ bộ này. Mô hình chấm quan hệ chỉ được nói CONTRADICTS khi P ≥ 0,9; dưới mức đó, quyết định thuộc về luật.
- Q13 chỉ chữa được phần nhỏ lỗi S1 (xem mục 3).
- Mọi số đo dưới đây đều là số trên nhãn bạc. `lift_guard` vẫn đóng cho tới khi người soát xong 821 cặp.

## 2. Mô hình, nhãn, loss, metric

| Mô hình (PA) | Nhãn | Loss | Metric chính | Cổng |
|---|---|---|---|---|
| e5-small / e5-base lọc tuyên bố (PA1, CPU) | T1 4 lớp, Q13 v1.2 | CE; CE có trọng số ∝ 1/√tần suất, làm mềm nhãn 0,05 | macro-F1 kiểm chéo 5 phần theo DN; cổng S1 trên GS-Eval | bắt ≥ 22/44, gắn nhầm ≤ 6/102 |
| mDeBERTa-xnli chấm quan hệ (PA1, CPU) | 4 quan hệ CAP | CE có trọng số; hiệu chỉnh nhiệt độ trên dự đoán ngoài fold | macro-F1 theo DN, so với luật và NLI chưa tinh chỉnh; S5 macro-F1(S,O), sai C / 100; ms/cặp | S5 CI dưới > 0,397, sai C ≤ luật + 1, ≤ 300 ms |
| gte-multilingual-reranker-base (PA1, CPU) | độ liên quan 2/1/0 | softmax CE theo danh sách (1 dương, 7 âm) | nDCG@5, MRR@5, hit@5 trong pool, so với lite | Δ nDCG@5 CI dưới > 0, thời gian ≤ 2 lần |
| Qwen3-4B học trò lời giải thích (PA1, Ollama) | lời giải thích của Qwen3-32B-AWQ (thầy), đã lọc | CE chỉ trên token câu trả lời, LoRA r 16 | S6 tỉ lệ nêu đủ ý; số mới = 0 | ≥ bản gốc 4B, GGUF trên laptop lệch ≤ 0,03 |
| Qwen3-14B chấm quan hệ / lời giải thích (PA2, A100) | như trên, dạng JSON; thầy gpt-oss-120b | như trên | S5, S6 | như trên |

## 3. Các lượt Kaggle (chi tiết và trạng thái: `docs/RUNS.md`)

| Notebook | Việc | Trạng thái lúc 09:40 |
|---|---|---|
| `phanththui/gs-off-t1-q13` | T1, 4 cấu hình | đang chạy. Cấu hình đầu (e5-small, CE có trọng số): CV macro-F1 **0,720**, recall tuyên bố 0,874. Cổng S1 ở ngưỡng 0,5: bắt 26/44, gắn nhầm **21/102** (11/11 là 26/102). Đúng dự đoán đã đăng ký: Q13 giảm gắn nhầm nhưng cổng vẫn trượt |
| `quynhnhu82/gs-off-pairs-v2` | mDeBERTa chấm quan hệ + gte reranker | đang chạy (bản v1 lỗi fp16, đã xoá và đẩy lại) |
| `nngocnh/gs-off-explain-teacher` | thầy Qwen3-32B-AWQ, 996 lời giải thích (T4 × 2, khoảng 43 token/s) | đang sinh; xong khoảng 10:40 |
| `phannguyngiahuy11a5/gs-off-explain-sft` | học trò Qwen3-4B LoRA → chấm S6 → GGUF Q4_K_M | **chưa đẩy**: cần đầu ra của thầy |

**Thu kết quả, đẩy học trò, vẽ biểu đồ:** một lệnh, chạy lại được nhiều lần.

```bash
C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/thu_ket_qua.py --push-sft
```

Biểu đồ ghi vào `docs/04-data-ai/hinh_mo_hinh/`:
- `t1_cv_macro_f1.png`, `t1_gate_s1.png`, `t1_threshold_tradeoff.png`, `t1_loss.png`;
- `stance_confusion.png`, `stance_quality.png`, `stance_risk_coverage.png`, `stance_loss.png`;
- `reranker_quality.png`;
- `explain_quality.png`, `explain-4b_loss.png`;
- `latency_cpu.png`.

## 4. PA2: thư mục cho vast.ai và hồ sơ `selfhost` — ĐÃ BÁC BỎ 13/11 (D-2026-11-13-03, không kinh phí)

- **Thư mục:** `deploy/vastai_a100/` (hướng dẫn trong README.md của thư mục). Gồm 4 lệnh: `00_setup.sh`, `10_train.sh`, `20_eval.sh`, `30_serve.sh`. Mã huấn luyện là cùng một bộ với Kaggle.
- **Ở laptop:** đặt `QUANTUM_PROFILE=selfhost` cùng `QUANTUM_SELFHOST_URL / _KEY / _MODEL`. Kiểm máy chủ bằng `tools/selfhost_check.py`. Bài kiểm ở `tests/test_selfhost_profile.py` (3 bài, qua). Hồ sơ `offline` không đổi.
- **Giới hạn dữ liệu:** máy trên chợ GPU không phải "GPU tại đơn vị" (D-2026-10-06-06). PA2 trên vast.ai chỉ dùng cho tài liệu lớp A, hoặc lớp B khi có thoả thuận. Lớp C ở lại PA1.

## 5. Chi phí

Giả định có ghi nguồn ở `configs/chi_phi_gia_dinh.yaml`; script là `tools/bao_cao_mo_hinh/chi_phi.py`; ảnh là `chi_phi_bang.png`, `chi_phi_thang.png`, `chi_phi_huan_luyen.png`. Với 200 bộ hồ sơ mỗi tháng, giá thuê tra ngày 13/11:

| Cấu hình | Thời gian / bộ | USD / tháng |
|---|---|---|
| PA1, laptop chỉ luật | 1 ph 44 s | ≈ 0 |
| PA1 + mô hình CPU đã huấn luyện | khoảng 2 ph 21 s (giả định 0,25 s/cặp, chờ số đo) | ≈ 0 |
| PA1 + Qwen3-4B viết lời giải thích | 12 ph 32 s | ≈ 0 |
| PA2, A100 bật giờ hành chính (176 giờ) | khoảng 2 ph 47 s | 176 (128–227) |
| PA2, A100 thuê theo lượt (12 phút bật máy) | 14 ph 47 s | 49 (36–64) |
| PA2, RTX 4090 bật giờ hành chính | khoảng 3 ph 18 s | 70 (44–93) |
| API Groq (tham chiếu, chỉ tài liệu công khai) | 5 ph 40 s | 5,6 |

Tốc độ trên A100 và RTX 4090 là giả định. Phải đo lại bằng `tools/selfhost_check.py` khi có máy.

## 6. Việc còn mở

1. Người soát 821 cặp (ưu tiên 191 cặp đã phân xử) để có nhãn vàng; khi đó mới xét `lift_guard`.
2. Không có ca CONTRADICTS: cần gom thêm cặp phản bác thật, ví dụ từ GS-Eval hoặc các bẫy số liệu, trước khi tin mô hình ở lớp này.
3. S1 vẫn trượt sau Q13. Cần đọc 21 tuyên bố thật bị gắn nhầm để tìm nguyên nhân, trước khi huấn luyện lại.
4. Đo lại độ trễ CPU của mô hình PA1 trên laptop i7-1355U. Số hiện có đo trên CPU của Kaggle.

## 7. Cập nhật 10:55: kết quả đã có, notebook đang chạy, notebook kế tiếp

**Đã có** (số trong `configs/measurement_decisions.yaml` → `offline_training_v1.results`; giải thích toán học của mọi cổng trượt trong [GIAI_THICH_TRUOT_2026-11-13.md](GIAI_THICH_TRUOT_2026-11-13.md)):
- **T1:** trượt cổng S1 ở cả 4 cấu hình. d′ trung vị 0,89, trong khi cổng cần 1,565.
- **mDeBERTa đầu 4 lớp mới:** không hơn luật. κ = 0,03; S5 đạt 0,536, luật tính cùng cách đạt 0,558; tốc độ 633 ms/cặp.
- **Thầy 32B:** giữ 939/996 lời giải thích; S6 đạt 0,214.

**Đang chạy** (7 notebook, mốc trong `docs/RUNS.md`):
- học trò 4B;
- học trò 1.7B;
- reranker bản sửa;
- Qwen3-4B LoRA chấm quan hệ;
- nhóm LLM dùng prompt (4B, 8B, 14B-AWQ);
- T1 bản xuất xác suất từng câu;
- mDeBERTa giữ đầu NLI.

Khi xong, chạy `C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/thu_ket_qua.py`, rồi `tools/bao_cao_mo_hinh/giai_thich_truot.py`.

**Notebook kế tiếp** (chưa đẩy được vì thiếu dữ liệu, phải chờ kết quả đang chạy, hoặc phải chạy ở máy khác):

| Mã dự kiến | Việc | Điều kiện để đẩy |
|---|---|---|
| `gs-off-t1-q13-v3` | Huấn luyện lại T1 với sổ tay v1.3 | đọc các câu gắn nhầm từ `gs-off-t1-q13-v2`, sửa định nghĩa cho khớp GS-Eval, gán lại (Claude, người soát) |
| `gs-off-stance-nli-v2` | Rút gọn mDeBERTa (6 lớp hoặc ONNX int8) nếu bản giữ đầu NLI đạt chất lượng nhưng còn chậm | kết quả `gs-off-stance-nli-head` |
| `gs-off-stance-gold` | Huấn luyện lại và chấm trên nhãn vàng; quyết định `lift_guard` | người soát xong 821 cặp |
| `gs-off-contradicts` | Thêm ca phản bác: thật (GS-Eval, bẫy số) và tổng hợp chỉ cho train | bộ cặp hiện có 0 CONTRADICTS: cần gom dữ liệu trước |
| `gs-off-retriever-e5` | Tinh chỉnh e5-small hai tháp cho truy xuất ngoại tuyến, so với lite | kết quả `gs-off-reranker-v3` (nếu reranker không có ích thì bỏ) |
| `gs-off-attr-lora` | Qwen3-4B LoRA trích thuộc tính (S2) | chưa có nhãn huấn luyện thuộc tính ngoài bộ test S2 (200 câu): cần gán trước |
| (laptop) parity GGUF | `ollama create` từ GGUF rồi chấm lại S6 trên laptop (cổng lệch ≤ 0,03) | GGUF từ notebook học trò 4B và 1.7B |
| ~~(vast.ai) `10_train.sh` + `20_eval.sh`~~ | đã bỏ: không thuê GPU (D-2026-11-13-03) | — |

**Cập nhật 11:10:**
- mDeBERTa giữ đầu NLI đã xong và không qua cổng (mục 4 của tệp giải thích).
- Đã đẩy thêm `gs-off-stance-nli-probe` (zero-shot + linear probe). Notebook `gs-off-stance-nli-v2` (rút gọn hoặc ONNX) chỉ đẩy khi probe hơn luật trên S5 mà còn chậm.
- Reranker chuyển sang bge-reranker-v2-m3, có ghi bổ sung vào bản đăng ký lúc 11:00.
- Hai học trò được đẩy lại bằng dataset `phantrnanna/gs-explain-teacher-v1`.


**Cập nhật 11:45 (D-2026-11-13-03):** bác bỏ PA2 vì không có kinh phí. Hệ thống còn PA1: laptop ngoại tuyến + MCP, suy luận qua API miễn phí cho tài liệu công khai, huấn luyện trên Kaggle. Bảng chi phí giữ lại làm căn cứ của quyết định.
