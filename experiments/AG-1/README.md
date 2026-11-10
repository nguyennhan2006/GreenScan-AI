# AG-1 · IR + thư viện so sánh tất định: model nhỏ chạy tại chỗ đọc số liệu, code kết luận

*Phiếu mở 31/10/2026. Dự đoán đăng ký trước khi có đầu ra model ở `configs/measurement_decisions.yaml`, khối `agentic_v1`. Kế hoạch: [KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md](../../docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md).*

## 1. Vấn đề

Bộ luật hiện tại hầu như không dám kết luận trên câu thật.
- Trên 142 ca B-b (tuyên bố sinh từ 26 số liệu thật của 5 doanh nghiệp), luật chỉ quyết định **4/142 ca (độ phủ 2,8 %)**.
- Luật bắt được **0/44** ca mâu thuẫn, và chỉ nhận ra 3/26 lời nhắc lại nguyên văn số liệu [ĐÃ THỰC NGHIỆM, `experiments/AG-0/out/score_rules.json`].
- Bằng chứng đã được đưa sẵn đúng câu, nên phần mất này thuộc khâu **đọc câu**, không phải khâu tìm bằng chứng.

## 2. Giả thuyết và dự đoán (ghi trước khi chạy)

Mượn DataMate D1 của ZAIC: LLM dịch câu sang IR, rồi thư viện luật tất định tính.
- Model nhỏ chỉ việc **điền IR**: chỉ số, giá trị, đơn vị, kỳ, phạm vi, loại giá trị, thực hiện hay mục tiêu.
- `irlib` kết luận theo bất biến 4–6. Trần của cách này đo bằng IR gold: độ phủ 0,528, precision 1,0, 0 kết luận sai.
- Dự đoán:

  | Model | Dự đoán |
  |---|---|
  | Qwen3-4B-Instruct-2507 | Độ phủ B-b ≥ 0,35 với precision ≥ 0,90 và CONTRADICTED sai ≤ 2; B-a sạch đúng ≥ 26/32 |
  | Qwen3-1.7B | Độ phủ thấp hơn 4B ít nhất 0,10 |
  | Qwen3-0.6B | Không dùng được: độ phủ < 0,15 hoặc precision < 0,80 |
  | 8B / 14B-AWQ / gemma-3-12B | Trong khoảng ±0,05 độ phủ của 4B: không có hiệu ứng cỡ từ khoảng 4B trở lên |

- **Cổng sang AG-2:**
  - precision ≥ 0,90;
  - cận dưới CI95 của precision ≥ 0,80;
  - CONTRADICTED sai không vượt luật quá 1.

## 3. Phương pháp, vì sao chọn

**Cách làm:**
- Mỗi văn bản (tuyên bố hoặc câu bằng chứng) đi qua cùng một prompt trích IR. Giải mã greedy, tắt thinking, trả JSON.
- Mỗi số liệu của tuyên bố được so với mọi số liệu của bằng chứng bằng `irlib.decide`:
  - một số liệu so được và khớp, không số nào mâu thuẫn: S;
  - chỉ có số mâu thuẫn: C;
  - còn lại: N (chuyển người).
- Ca có nhiều số liệu: một C là C; tất cả S thì là S.

**Vì sao chọn:**
- Size ladder (10/10) cho thấy LLM vượt luật vì luật phủ thấp, nhưng LLM để tự phán thì vẫn báo SUPPORTED sai.
- Tách "đọc" khỏi "tính" giữ được bất biến 5 (số học là của code), và mỗi kết luận chỉ ra được phép tính.

**Phương án đã cân nhắc và bỏ:**

| Phương án | Vì sao bỏ |
|---|---|
| LLM tự phán S / C / N | Trái bất biến 5. Size ladder đã đo: SUPPORTED sai trên bảng dàn phẳng |
| Giải mã JSON ràng buộc (guided decoding) | Tham số của vLLM đổi theo phiên bản. Bản đầu dùng prompt + bộ đọc JSON khoan dung; đếm số văn bản không đọc được |
| Chạy model qua API | Khoá FPT bị 401 ngày 31/10. Mục tiêu là chạy tại chỗ |

## 4. Cấu hình

| Hạng mục | Giá trị |
|---|---|
| Bộ đo | `gs_bench_v1.jsonl` (193 ca). `experiments/AG-1/` giữ bản sao nhúng trong notebook |
| Model | Qwen3-0.6B (0,75B), Qwen3-1.7B (2,03B), Qwen3-4B-Instruct-2507 (4,02B), Qwen3-8B (8,19B), Qwen3-14B-AWQ (14,77B), unsloth/gemma-3-12b-it (12,19B). Apache-2.0, trừ gemma (Gemma terms) |
| Chạy | vLLM 0.32.0 (gỡ torchaudio), fp16, `max_len` 4096, `MAX_TOKENS` 768, greedy, seed 0. Dự phòng: transformers (`backend: hf`) |
| Notebook | `nb_a.ipynb`: `thanhtruc02/gs-ag1-a`, model ≤ 4B, TP 1. `nb_b.ipynb`: `vantiennhuannguyen/gs-ag1-b`, model ≥ 8B, TP 2 |
| Code | `ag1_worker.py`, `irlib.py`; `llm.py` và `multirun.py` chép từ ZAIC `Experiment/common/` |
| Chấm | `experiments/score.py` (bootstrap theo công ty) |

## 5. Kết quả

### Kết quả 31/10 11:45

Lượt A và C đã xong; lượt B (8B / 14B / gemma) còn chạy. Chấm bằng `experiments/score.py`, lưu ở `experiments/AG-1/out_score_partial.json`.

| Hệ | B-b độ phủ | B-b precision (CI95) | B-b CONTRADICTED sai | B-b SUPPORTED sai | B-a sạch đúng | B-a trang thật đúng |
|---|---|---|---|---|---|---|
| Luật hiện tại | 0,028 | 0,75 | 0 | 1 | 20/32 | 7/19 |
| Qwen3-0.6B | 0,127 | 0,39 | 4 | 7 | 16/32 | 5/19 |
| Qwen3-1.7B | 0,183 | 0,54 | 8 | 4 | 18/32 | 4/19 |
| Qwen3-4B-Instruct | 0,134 | **1,00** [1,0; 1,0] | 0 | 0 | 17/32 | 5/19 |
| Qwen3-32B-AWQ | **0,423** | 0,82 [0,69; 1,0] | **7** | 4 | 23/32 | 7/19 |
| AG-2 thử: luật trước, rồi 4B ∧ 32B phải khớp | 0,113 | 0,94 [0,875; 1,0] | 0 | 1 | 21/32 | 7/19 |
| Trần (IR gold) | 0,528 | 1,00 | 0 | 0 | — | — |

**Đối chiếu với dự đoán đã đăng ký:**
- Dự đoán cho 4B **sai**: độ phủ 0,134 < 0,35. Precision thì đạt 1,0.
- 0.6B "không dùng được": **đúng**.
- Dự đoán "không có hiệu ứng cỡ trên 4B" **sai**: 32B gấp hơn 3 lần độ phủ của 4B, nhưng đổi lại 7 ca CONTRADICTED sai.
- **Chưa model nào qua cổng `ag1_ir_path_usable`**: 4B không bị chặn, nhưng độ phủ thấp; 32B hụt precision ≥ 0,90.
- Ghép "luật → 4B ∧ 32B" giữ 0 ca vu oan, và tăng độ phủ trên câu thật gấp 4 lần luật (0,028 → 0,113).

**Việc tiếp theo, ưu tiên cao nhất:** đọc 7 ca CONTRADICTED sai và 4 ca SUPPORTED sai của 32B (file `kaggle_out/c/**/q3-32b-awq_cases.jsonl`, trường `why`) để biết lỗi ở khâu đọc IR hay ở `irlib` (chuẩn hoá đơn vị, bội số, ranh giới). Sửa lỗi rồi chạy lại cả thang.

### Kết quả 31/10 14:10: lượt B, phân loại lỗi, và `irlib.ground()`

**Lượt B** xong. Qwen3-8B: độ phủ 0,232, precision 0,636. Qwen3-14B-AWQ: độ phủ 0,254, precision 0,944. gemma-3-12b trả `raw` rỗng cho cả 230 câu (OOM lúc nạp, rồi sinh rỗng), nên bị loại khỏi thang. Đây là lỗi chạy, không phải kết quả của model.

**Phân loại lỗi** (`errors.py`, so IR model đọc với IR gold của từng ca B-b, `out/errors_ag1.json`):
- **32B: cả 11 kết luận sai cùng một lỗi.** Model tự thêm bội số mà câu không viết: đọc "10.730 m3" thành "10.730 ngàn m3", rồi kết luận C với tuyên bố đúng, S với tuyên bố sai gấp nghìn lần. Lỗi rơi vào số liệu nước của 4 doanh nghiệp, vì "10.730" giống "10,730 nghìn" kiểu Anh.
- **4B: mất 50 tuyên bố vì nhét cả bội số và đơn vị vào `value_text`** ("23,5 triệu tCO2e"). Bộ đọc số từ chối cả số liệu, nên 4B gần như chỉ còn N. Đây là lý do độ phủ thấp, không phải do 4B đọc kém.
- 1.7B: chủ yếu không đọc được bằng chứng (25 ca), và nhầm `scope` / `metric`.

**Sửa tất định:** `irlib.ground(fig, sentence)` giữ mỗi số liệu model đọc đúng với những gì câu viết.
- Tách số, bội số và đơn vị nếu bị nhét chung.
- Số phải có trong câu. Bội số là chữ câu viết ngay sau số đó; câu không viết thì để trống. Năm (kỳ, năm gốc) phải là năm câu có viết.
- Không model nào phải chạy lại. Chấm lại từ đầu ra thô đã lưu bằng `rescore.py`.
- Test hồi quy ở `tests/test_irlib_ground.py`, 9 test. Test đã bắt thêm một lỗi: "85 tỷ lệ" bị đọc thành bội số "tỷ".
- Mọi IR gold của bộ đi qua `ground()` không đổi số và bội số. Riêng 10 ca N2 mất năm gốc, vì câu tuyên bố không viết năm gốc (năm đó thừa kế từ bằng chứng khi sinh ca); nhãn N không đổi.

Số **trong mẫu** (cách sửa được rút ra từ chính 193 ca này, nên chưa phải bằng chứng; `out/score_ag1_ground.json`):

| Hệ (B-b, 142 ca) | độ phủ trước → sau | precision trước → sau | CONTRADICTED sai | SUPPORTED sai | B-a sạch |
|---|---|---|---|---|---|
| Qwen3-1.7B | 0,183 → 0,183 | 0,54 → 0,85 | 8 → 0 | 4 → 4 | 19/32 |
| Qwen3-4B-Instruct | 0,134 → **0,437** | 1,00 → 0,984 | 0 → 1 | 0 → 0 | 25/32 |
| Qwen3-8B | 0,232 → 0,408 | 0,64 → 0,983 | 6 → 0 | 6 → 1 | 22/32 |
| Qwen3-14B-AWQ | 0,254 → 0,451 | 0,94 → 0,984 | 1 → 0 | 1 → 1 | 26/32 |
| Qwen3-32B-AWQ | 0,423 → 0,465 | 0,82 → **0,985** | 7 → 1 | 4 → 0 | 25/32 |
| Trần (IR gold) | 0,528 | 1,00 | 0 | 0 | — |

**Đọc bảng:**
- Trong mẫu, cả 4 model ≥ 4B qua cổng `ag1_ir_path_usable`: precision ≥ 0,90, cận dưới CI ≥ 0,93, false_C ≤ 1.
- Sau khi sửa, hiệu ứng cỡ trên 4B gần như biến mất (0,408–0,465). Dự đoán "không có hiệu ứng cỡ trên 4B" đã đăng ký thành ra đúng. Khoảng cách 32B / 4B lúc trước là do lỗi định dạng, không phải do năng lực đọc.
- 1.7B vẫn kém 4B 25 điểm độ phủ, nên điều kiện mở AG-4 (QLoRA, kém ≥ 10 điểm) đã thoả.

**Kiểm ngoài mẫu** (đăng ký `agentic_v1_1` trong `configs/measurement_decisions.yaml`, trước khi model nào đọc ca mới):
- 260 ca B-b mới của v1.1. Prompt giữ nguyên, nên lượt này kiểm riêng `ground()`.
- Lượt D, E, F đẩy lúc 14:13 (`docs/RUNS.md`).
- **Bị bác bỏ nếu** 4B có false_C > 2 hoặc precision < 0,90 trên 260 ca này.

### Kết quả 31/10 14:35: ngoài mẫu (lượt D, 246 ca B-b mới)

`out/score_heldout_d.json`. Prompt giữ nguyên; cùng một đầu ra thô được chấm với và không với `ground()`.

| Hệ | độ phủ | precision (CI95) | CONTRADICTED sai | SUPPORTED sai |
|---|---|---|---|---|
| Luật | 0,077 | 0,632 | 0 | 7 |
| 4B, không `ground` | 0,053 | 0,692 | 3 | 1 |
| 4B, có `ground` (v1.1) | 0,126 | 0,903 [0,81; 1,0] | 2 | 1 |
| 1.7B, có `ground` | 0,037 | 0,778 | 0 | 2 |

**Đối chiếu với `agentic_v1_1`:**
- Dự đoán an toàn của 4B **giữ được, sát nút**: precision 0,903 ≥ 0,90, cận dưới CI 0,81 ≥ 0,80, CONTRADICTED sai 2 ≤ 2. Điều kiện bác bỏ không xảy ra.
- `ground` giúp ngoài mẫu: CONTRADICTED sai 3 → 2, precision 0,69 → 0,90.
- Dự đoán độ phủ **sai**: 0,126 ngoài mẫu so với 0,437 trong mẫu.

**Mất độ phủ ở đâu** (`out/errors_heldout_d.json`):
- 39 ca bằng chứng không đọc được số liệu, phần lớn là câu dài nhiều số của doanh nghiệp mới.
- 27 ca lệch `value_kind` của tuyên bố.
- 13 ca không đọc được tuyên bố.

Cả 2 ca vu oan cùng một kiểu: câu bằng chứng có "10.175 cây … 8.000 cây", model chỉ đọc 10.175, rồi so tuyên bố "8.000 cây" với số đó.

**v1.2** (đăng ký `agentic_v1_2`, kiểm trên tập ngoài mẫu kế tiếp, không dùng lại 246 ca này):
- `count` và `absolute` coi là cùng loại.
- Không kết luận C vì chênh giá trị khi câu bằng chứng viết đúng con số và bội số của tuyên bố.
- Trong mẫu: 4B có CONTRADICTED sai 2 → 0, precision 0,969, độ phủ 0,130.
- Thêm 3 test; tổng 12 test.

**Kết luận tạm:**
- Với `ground` và C-guard, đường IR của 4B an toàn ngang luật (0 vu oan), ít bỏ lọt hơn (1 ca so với 7 của luật), và độ phủ gần gấp đôi.
- Trên doanh nghiệp mới, độ phủ còn thấp. Việc cần làm kế tiếp là đọc câu bằng chứng nhiều số: prompt có ví dụ (few-shot), hoặc tách câu theo từng số trước khi đọc.

### Kết quả 31/10 22:40: ngoài mẫu với 8B, 14B, 32B (lượt E, F)

Cùng 246 ca của lượt D. Mỗi ô ghi độ phủ / precision / CONTRADICTED sai. Số `ground` là phán quyết tính ngay trên Kaggle (v1.1). Cột `raw` là cùng đầu ra thô nhưng chấm không qua `ground()`. Cột v1.2 là chấm lại có C-guard và coi count = absolute. Kết quả lưu ở `out/score_heldout_ef.json`.

| Model | raw | ground (v1.1) | v1.2 |
|---|---|---|---|
| Luật | 0,077 / 0,632 / 0 (7 SUPPORTED sai) | | |
| 4B | 0,053 / 0,692 / 3 | 0,126 / 0,903 / 2 | 0,130 / 0,969 / 0 |
| 8B | 0,211 / 0,731 / 12 | 0,220 / 0,963 / 1 | 0,224 / 0,982 / 0 |
| 14B-AWQ | 0,224 / 0,855 / 7 | 0,256 / 0,921 / 3 | 0,280 / 0,957 / 1 |
| 32B-AWQ | 0,329 / 0,926 / 3 | 0,329 / 0,951 / 2 | 0,321 / 0,975 / 0 |

**So với đăng ký `agentic_v1_1`:**
- 32B: precision ≥ 0,90 và vu oan ≤ 2. **Đúng**: 0,951 và 2.
- `ground` giảm vu oan ở mọi model từ 4B trở lên. **Đúng**: 3→2, 12→1, 7→3, 3→2.
- Quy mô: 8B, 14B, 32B cách 4B không quá ±0,07 độ phủ. **Sai**: 0,126 / 0,220 / 0,256 / 0,329. Trong mẫu, `ground` xoá hiệu ứng quy mô. Ngoài mẫu, model lớn đọc câu bằng chứng nhiều số tốt hơn rõ rệt.
- **Sửa báo cáo 14:35:** cổng `ag1_ir_path_usable` cho phép vu oan tối đa bằng luật + 1. Trên tập này luật có 0 vu oan, nên ngưỡng là 1. Với v1.1, chỉ 8B qua cổng. 4B (2), 14B (3) và 32B (2) **trượt cổng**, dù vẫn khớp dự đoán lỏng hơn (≤ 2). Báo cáo 14:35 đã chỉ so 4B với dự đoán, không so với cổng.

**Mọi ca vu oan của mọi model đều nằm ở cùng một câu Coteccons.** Câu ghi 10.175 cây gồm 2.175 cây và 8.000 cây, còn 11.111 cây ở chỗ khác. Mỗi lần vu oan là một tuyên bố về số con bị đem so với số tổng. C-guard của v1.2 bắt được các ca này. Ca còn sót của 14B là "11,1 nghìn cây": câu không viết đúng con số đó, nên guard không xét.

**v1.2 trên E/F:** các model này không góp phần tạo ra v1.2, nhưng các ca thì có, nên kết quả chỉ là một phần ngoài mẫu. 8B và 32B có 0 vu oan, 14B có 1.

**AG-2 (luật + 4B + 14B + 32B, v1.2):**
- Chính sách "các đường quyết định đều đồng ý": độ phủ 0,419, precision 0,903, nhưng 9 SUPPORTED sai và 1 vu oan. Kém luật (7 và 0), nên trượt cổng `ag2_dual_path_to_product`. SUPPORTED sai chủ yếu đến từ luật nói S một mình (xô S/N/N/N đúng 1/6).
- Chính sách xô OOF theo công ty (cận dưới Beta) không quyết ca nào: 4 đường cho tới 81 xô, mà chỉ có 7 công ty.
- Một đường 32B v1.2 đứng riêng: 0,321 / 0,975 / 0 vu oan / 2 SUPPORTED sai.

**Tập ngoài mẫu mới cho v1.2.** File `benchmark/gs_bench_v1/build_heldout_v12.py` → `gs_heldout_v12.jsonl`.
- Nguồn: các câu `candidates_v2` chưa làm bằng chứng trong v1.1. Reader A là 32B (lượt F, đã qua `ground`), reader B là các kiểm tra tất định của v1.1.
- Đăng ký ban đầu đòi Claude và 32B đọc khớp, nhưng chỉ được 6 số liệu (33 ca). Đã sửa đổi đăng ký lúc 22h50, trước khi model nào đọc tập.
- Kết quả: 35 số liệu, 28 câu, 9 công ty (dpr và cng là công ty mới), 162 ca (38 S, 55 C, 69 N), không ca nào lệch giữa irlib và nhãn họ.
- Luật trên tập này: độ phủ 0,006, 0 vu oan, 0 SUPPORTED sai.
- Lượt G (4B, 8B, 14B, 32B) đang chạy. Điểm của 32B trên tập này lạc quan theo cách dựng, vì chính 32B chọn số liệu.

### Kết quả 31/10 23:25: tập ngoài mẫu v1.2 (lượt G, 162 ca)

Mỗi ô ghi độ phủ / precision / CONTRADICTED sai. Kết quả lưu ở `out/score_heldout_g.json`. Luật trên tập này: 0,006 / 1,0 / 0.

| Model | raw | v1.1 | v1.2 |
|---|---|---|---|
| 4B | 0,019 / 0,667 / 0 | 0,093 / 1,0 / 0 | 0,093 / 1,0 / 0 |
| 8B | 0,031 / 1,0 / 0 | 0,074 / 0,833 / 1 | 0,068 / 0,909 / 0 (CI [0,40, 1,0]) |
| 14B-AWQ | 0,025 / 1,0 / 0 | 0,086 / 0,929 / 0 | 0,086 / 0,929 / 0 (CI [0,625, 1,0]) |
| 32B-AWQ (lệch) | 0,185 / 1,0 / 0 | 0,228 / 0,973 / 0 | 0,228 / 0,973 / 0 |

**So với đăng ký `agentic_v1_2`:**
- Mọi dự đoán đều đúng. 4B có 0 vu oan và precision 1,0, nhưng chỉ trên 15 ca dám kết luận. Độ phủ của 4B là 0,093, dưới 0,25 như dự đoán. 8B và 14B có 0 vu oan.
- C-guard có tác dụng một lần trên dữ liệu thật sự mới: 8B có 1 ca vu oan, guard chuyển ca đó sang N.
- Cổng `ag1_ir_path_usable`: 4B qua, nhưng chỉ trên 15 ca. 8B và 14B trượt vì cận dưới CI thấp (0,40 và 0,625). 32B qua nhưng không tính được, vì tập lệch theo cách dựng.

**Lỗi tập (phát hiện hậu kiểm):**
- 60/162 ca (37 %) dựa trên những số 32B gán mã `other_env` nhưng không phải số liệu môi trường, ví dụ "năng suất tăng 10%" hay "thiệt hại 1,5 % GDP". Model không đọc ra số từ các tuyên bố như vậy là đúng; 26 trong 39 tuyên bố 4B bỏ sót thuộc nhóm này.
- Bỏ nhóm này đi thì còn 102 ca. Kết quả hậu kiểm, không thuộc đăng ký: 4B 0,147 / 1,0; 8B 0,108 / 0,909; 14B 0,137 / 0,929; 32B 0,275 / 1,0. Mọi model đều 0 vu oan.
- Tập sau, nếu dùng model làm reader A, phải loại `other_env`.

**Kết luận:**
- Đường IR v1.2 an toàn trên dữ liệu mới: 0 vu oan ở cả bốn model.
- Nhưng 4B chỉ dám kết luận khoảng 10–15 % số ca. Mất mát còn lại của 4B: không đọc được bằng chứng (20 ca) và đọc sai năm của bằng chứng (14 ca).

### Kết quả 01/11 17:00: lỗi tập v1.2 và chấm lại trên tập sạch v1.3 (không tốn GPU)

**Phát hiện.** Đọc các ca 4B "bỏ lỡ" trên tập ngoài mẫu (`errors.py`) thì thấy phần lớn là lỗi của tập, không phải của model.
- **Năm bịa từ tiêu đề trang.** Câu bằng chứng "…tiết giảm được giảm 12%, tương đương 4.000m3/năm…" không nêu năm. Nhãn gold vẫn ghi 2022, vì dòng tiêu đề "BÁO CÁO THƯỜNG NIÊN 2022" dính vào câu. Bộ kiểm B chỉ đòi năm xuất hiện ở đâu đó trong câu, nên lọt.
- **Tuyên bố méo.** Có câu như "tiết giảm được giảm 12% … đạt 12%", hay "… là 02 Đơn vị".
- Trong các ca đó, 4B trả null hoặc từ chối là **đúng**. Các nhóm lỗi "e.period 14" và "miss_claim 13" chủ yếu đến từ 2–3 câu bằng chứng hỏng; mỗi câu sinh khoảng 6 ca.

**Sửa.** `benchmark/gs_bench_v1/clean_v13.py` bỏ nguyên số liệu bằng chứng khi gặp một trong các dấu hiệu sau. Không gán lại nhãn nào. Danh sách bỏ ở `errata_v13.txt`.
- năm không đứng sau một từ chỉ thời gian trong phạm vi 25 ký tự ("năm tài chính 2024" và "Tháng 8/2023" vẫn giữ);
- tên chỉ số có chữ số;
- đơn vị là "đơn vị";
- ở tập ngoài mẫu: mã `other_env`.

**Kết quả trên tập sạch:**
- Tập hiệu chỉnh: 448 ca (bỏ 5).
- Tập ngoài mẫu: 87 ca (bỏ 75: `other_env` 60, tên chỉ số có số 6, đơn vị giả 4, năm từ tiêu đề 5).

Chấm lại đầu ra Kaggle đã có (`experiments/AG-1/out/v13/`). Mỗi ô ghi độ phủ / precision / SUPPORTED sai / CONTRADICTED sai.

| Hệ | Hiệu chỉnh sạch (B-b, n = 383–397, trong mẫu) | Ngoài mẫu sạch (B-b, n = 87) |
|---|---|---|
| Luật | 0,060 / 0,625 / 9 / 0 | 0,011 / 1,0 / 0 / 0 |
| 4B (Q bf16, Kaggle) | 0,243 / 0,989 / 1 / 0 | 0,138 / 1,0 / 0 / 0 (CI độ phủ [0,045; 0,314]) |
| 8B | 0,292 / 0,982 / 2 / 0 | 0,115 / 1,0 / 0 / 0 |
| 14B-AWQ | 0,347 / 0,970 / 3 / 1 | 0,115 / 1,0 / 0 / 0 |
| 32B-AWQ (tập lệch về 32B) | 0,373 / 0,986 / 2 / 0 | 0,253 / 1,0 / 0 / 0 |

**Diễn giải và giới hạn:**
- Trên dữ liệu ngoài mẫu sạch, **không model nào kết luận sai** (precision 1,0, n = 10–22 ca dám kết luận mỗi model). Model kết luận được gấp 10–20 lần luật.
- n còn nhỏ, nên cận dưới của precision chưa chặt.
- Kết luận cũ "4B mất độ phủ vì đọc sai năm bằng chứng" **bị rút lại**: đó là lỗi tập.
- Việc "sửa prompt đọc năm" không còn là ưu tiên. Việc đọc câu có nhiều số vẫn mở; chờ đo lại trên tập sạch.

## 6. Giới hạn đã biết trước

- Nhãn B-b là **bạc**: IR bằng chứng do Claude đọc một lượt, rồi qua bộ kiểm tất định.
- B-b chỉ có 5 doanh nghiệp, đều không phải ngành phát thải cao. Chưa có bảng, và tuyên bố sinh bằng khuôn câu, nên dễ đọc hơn tuyên bố thật.
- B-a có 51 ca, do nhóm dựng.
- Máy T4 khác laptop của người dùng.

## 7. Thất bại và cách gỡ

- **Khoá FPT bị 401** nên không dùng được thầy đám mây. Đọc IR bằng Claude (1 subagent) cộng bộ kiểm tất định.
- **Gán nhãn quá thận trọng:** 75/109 số liệu bị chính người đọc đánh dấu "không chắc" và bị bỏ. B-b vì thế chỉ còn 26 số liệu.
- **Shell nuốt dấu `\`** khi viết regex qua heredoc, sinh ký tự điều khiển `\x08` và `\x01` trong `build.py`. Đã sửa bằng `chr(92)`.
- **Smoke đầu lỗi `No module named vllm`:** `multirun` tự đặt `LLM_BACKEND=vllm`. Đã thêm ứng viên `hf`.

## 8. Khái niệm

IR (biểu diễn trung gian), độ phủ, precision trên phần dám kết luận, oracle, nhãn theo cấu trúc, bootstrap theo công ty. Sẽ thêm vào `docs/00-project/GLOSSARY.md`.

## 9. Hình nên vẽ

- Cột độ phủ và precision theo model, có mốc luật và mốc oracle.
- Ma trận họ nhiễu × model.

Dữ liệu: `out/score_ag1.json`.

## 10. Bước tiếp

- Nếu qua cổng: AG-2 (hai đường + cổng đồng thuận).
- Nếu 1.7B kém 4B ≥ 10 điểm: mở AG-4 (QLoRA).
- Mở rộng B-b bằng bảng của doanh nghiệp phát thải cao (AG-3).
