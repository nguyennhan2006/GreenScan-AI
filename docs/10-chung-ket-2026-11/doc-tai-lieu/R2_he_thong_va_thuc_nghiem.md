# R2: Hệ thống hiện tại và các thực nghiệm (bảng số liệu được nói)

*Ghi ngày 04/11/2026 cho Chung kết 10/11/2026. Số mới nhất tính tới 01/11/2026 17:40 (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 10). Ngày 04/11 đã chạy `find -newermt "2026-11-01 17:20"`: không có kết quả thí nghiệm nào mới hơn. Chỉ có `benchmark/gs_eval_v2/` đang được dựng song song từ 12:47 ngày 04/11, chưa có số, nên ghi chú này không dùng. Mọi đường dẫn tính từ REPO.*

*Nguồn đã đọc:*
- `docs/07-presentation/paper/GREENSCAN_PAPER_2026-10-15.md`: đọc đủ. Riêng danh mục tài liệu tham khảo (dòng 341–384) chỉ lướt.
- `docs/07-presentation/technical_brief/GreenScan_Technical_Brief.tex`: đọc đủ phần nội dung, bỏ phần khai báo LaTeX.
- `docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`: đọc đủ.
- `docs/00-project/ARCHITECTURE_INVARIANTS.md`: đọc đủ.
- `docs/00-project/DECISIONS_LOG.md`: đọc đủ, gồm mọi mục từ 18/09 đến 16/10. Sau 16/10 không có mục nào.
- `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`: đọc mục 0–5 và 7–11. Mục 6 (tài khoản Kaggle) bỏ qua.
- `docs/00-project/AUDIT_HE_THONG_2026-10.md`: đọc đủ.
- `docs/00-project/ISSUES_REGISTER_2026-09.md`: chỉ đọc B9, mục N, mục P và dòng cập nhật 10/10 (Q1–Q5). Các mục A, C–G nằm ngoài trọng tâm R2 nên không đọc.
- `experiments/AG-1/README.md` và `experiments/AG-3/README.md`: đọc đủ.
- `experiments/AG-0/` và `experiments/AG-2/`: **hai thư mục này không có README.md**. Số liệu lấy từ `experiments/AG-0/out/score_rules.json`, `experiments/AG-2/out/product_parity_q4_K_M.json` và các khối kết quả trong yaml.
- `configs/measurement_decisions.yaml`: đọc đủ 282 dòng. Khối `agentic_ag3_v0` và khối `model_selection_v2` chưa có phần kết quả.
- `docs/RUNS.md`: đọc đủ.
- `docs/09-luan-van/PQ-01_TIN_DUOC_BAO_NHIEU.md`, `PQ-02_BIA_HAY_TINH_SAI_SO_LIEU.md`, `PQ-06_DO_KHI_CHUA_CO_GOLD.md`: đọc đủ.
- `docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`: đọc đủ.
- `docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`: đọc mục 0–1 và 5–9. Mục 2–4 chỉ lướt tiêu đề.
- **Kiểm chéo bằng mã ngày 04/11:**
  - `training/runs/kaggle_t1_v3/results.json` và `benchmark/t1_kaggle/report_v3.json`;
  - `experiments/AG-1/out/v13/score_calib.json` và `score_heldout.json`;
  - `benchmark/gs_bench_v1/stats_v13.json`; đếm công ty, tầng và họ nhiễu trong `gs_bench_v1.jsonl` và `gs_heldout_v12.jsonl`;
  - `configs/default.yaml`, `configs/scoring_v1.yaml`, `configs/legal/rule_pack_vn_green_v0.1.yaml`;
  - `src/quantum_gw/verification/irlib.py` và `ir_reader.py`;
  - đếm số test trong `tests/`.

*Phần không đọc được:* không có. Mọi tài liệu của cụm R2 đều là .md, .tex, .yaml hoặc .json, nên không cần trích PDF bằng PyMuPDF.

---

## 1. Tóm tắt từng tài liệu

### 1.1 Bài báo 15/10 (`GREENSCAN_PAPER_2026-10-15.md`)
- **Là gì:** bản thảo bài báo/luận văn dùng cho Bán kết và Chung kết. Bài định nghĩa bài toán và mô tả 10 bước, 5 nhãn verdict, 10 bất biến, dữ liệu, 4 nhóm thí nghiệm, hạn chế, chương trình thí nghiệm A–H và cách tái lập.
- **Kết quả chính:**
  - T1 e5-base đạt macro-F1 0,73 [0,69; 0,76] **trên nhãn Claude**, so với luật 0,36 và zero-shot 0,27.
  - Size ladder 51 ca: luật đúng 20/32 và 7/19; các mô hình đúng 29–32/32 và 15–18/19.
  - A/B 28/09 trên HPG: LLM tự quyết sinh 10 CONTRADICTED, phần lớn sai; khi có chốt chặn thì còn 0.
  - Hàng đợi HPG còn 9/172 mục.
  - Bài tự nêu 3 điều chưa có: số đo trên nhãn người; kết quả HPG khác "phẳng" (153/156 khớp một phần); quy tắc pháp lý áp được.
- **Liên quan và độ mới:** bài viết trước toàn bộ cụm AG (31/10–01/11), nên chưa có GS-Bench, đường IR, hai đường hay AG-3. Có vài câu đã cũ hoặc sai so với hiện trạng (mục 5).

### 1.2 Technical Brief (tháng 9/2026, Vòng 2)
- **Là gì:** tài liệu kỹ thuật 1.0 nộp Vòng 2. Gồm 4 nguyên tắc (P1 evidence-first, P2 abstain hợp lệ, P3 người trong vòng lặp, P4 không kết luận vượt bằng chứng), kiến trúc 10 bước, rubric 9 thành phần (tổng trần 100), 8 cổng G0–G7, policy-as-code, và công thức QUBO chọn tập bằng chứng tối thiểu.
- **Kết quả tới 9/2026:**
  - 4/4 ca thật có phán quyết khớp CONTRADICTED; trước ADR 0003 là 0/4.
  - 206 test.
  - Báo cáo 11 MB (803 chunk) xử lý dưới 2 phút, không GPU.
- **Ngưỡng cam kết từ hồ sơ Vòng 1** (dễ bị hỏi lại): F1 trích tuyên bố ≥ 0,75; Recall@10 ≥ 0,85; độ chính xác trích dẫn ≥ 0,90; sai số học = 0; độ chính xác verdict ≥ 0,80 trên nhãn người. **Chưa ngưỡng nào đo được trên nhãn người.**
- **Độ mới:** cũ nhất cụm. Brief còn ghi "dung sai 12 %" (bỏ từ 18/09), "Qwen3-8B chính + BGE-M3 + reranker" và "local vLLM/Ollama mặc định". Cả ba không khớp cấu hình hiện tại (mục 5).

### 1.3 `HE_THONG_HIEN_TAI_2026-10-10.md`: bản đồ theo mã (commit `ea89809`)
- **Là gì:** mô tả mười bước của `agents/orchestrator.py`, quy tắc của `verifier.py`, chỗ dữ liệu rời máy, lưu trữ, cổng kiểm thử, và 13 chỗ cấu hình, tài liệu và mã không khớp nhau.
- **Dữ kiện chính:**
  - Chỉ 3 nhóm mã gọi HTTP: provider LLM, embedding, reranker.
  - Chế độ `offline` có 0 kết nối, đã kiểm 09/10 trên 264 trang.
  - Chế độ `gpu` vẫn dự phòng sang FPT, trái với lời hứa "không rời máy".
  - Chưa có sổ ghi từng lần gửi đi.
  - Cổng G3 luôn đạt.
  - Nhãn "ngoại tuyến" trên giấy làm việc chỉ dựa vào `prompt_version`.
- **Dùng khi BGK hỏi** "bước nào làm gì" và "dữ liệu đi đâu". Số test (359) đã cũ.

### 1.4 `ARCHITECTURE_INVARIANTS.md` (hiệu lực 25/09)
- **Là gì:** 10 bất biến kiến trúc, mỗi bất biến có test canh (14 test khi ban hành; file test hiện có 15 hàm), kèm danh sách "từ nay không được làm", Definition of Done kiểu "giữ được bài học", và thứ tự làm việc mới.
- **Kết quả audit ngữ nghĩa HPG 25/09:** không mâu thuẫn cũ nào còn đứng được khi chạy lại với quy tắc mới. Lý do: comparator cũ chỉ kiểm đơn vị. Bảng chiều chặn: khác công nghệ 2, khác cơ sở đo 2, chênh hàng chục lần 2, khác chỉ số con 2, mục tiêu so với thực hiện 1, không phải phép số học 1.
- **Liên quan:** đây là "hiến pháp" của dự án. Mỗi thí nghiệm AG phải gắn với một lỗi đã đo, vì có quy tắc cấm "thêm agent, fine-tune, quantum chỉ để trông AI hơn".

### 1.5 `DECISIONS_LOG.md` (từ 18/09 đến 16/10)
Các quyết định phải nhớ:
- 18/09-02: không GraphRAG, không đa tác tử, không fine-tune tới Bán kết.
- 18/09-03: bỏ dung sai 12 % và ngưỡng 35 % khỏi tài liệu trình bày.
- 18/09-04: định nghĩa vận hành 5 verdict.
- 18/09-05: bỏ mọi công thức "mức độ trung thực ESG".
- 18/09-06: sửa QUBO. k là số đoạn mục tiêu; thêm biến phủ; **không tuyên bố lợi thế lượng tử**.
- 18/09-08: slide chia 3 cột Đạt / Mục tiêu / Giả thuyết.
- 22/09-03: PARTIAL do thiếu thuộc tính chỉ được tối đa MEDIUM.
- 22/09-04: không nói "Hybrid RAG + reranker" ở thì hiện tại.
- 22/09-05: không nói "độ chính xác X %" khi gold dưới 60.
- 22/09-06: dùng 4 trạng thái năng lực thay cho "% sẵn sàng".
- 25/09-01: 10 bất biến được thi hành bằng test.
- 28/09-01: bật GLM-5.2 cho cặp khó, có chốt `llm_stance_decisive: false`.
- 06/10-01..07: hàng đợi 3 bước; một lệnh, một cổng, ba chế độ, mặc định `offline`; `priority-v1.1`; sửa registry (NĐ 83/2026); gỡ các mô hình xử lý dữ liệu ở Nhật; quy tắc dữ liệu A/B/C.
- 16/10-01: chọn mô hình theo công đoạn bằng số đo; **nhãn Claude không bao giờ được tháo chốt**.

**Lỗ hổng:** các quyết định ngày 31/10 (phương án (b), trần API US$5, bỏ khoá trả phí) chỉ nằm trong mục 9 của kế hoạch 31/10, chưa vào log. Điều này trái quy tắc ghi ở đầu log: "chỉ có hiệu lực khi có ở đây".

### 1.6 Kế hoạch 31/10 (`KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`): nguồn số mới nhất
- **Là gì:** kế hoạch mượn cách làm từ ZAIC: đo điểm mất trước, LLM chỉ dịch câu sang IR, thư viện tất định quyết, hai đường kiểm chéo, kiểm định giữ hẳn công ty ra ngoài. Kèm phiếu thí nghiệm AG-0…AG-6 (7 phiếu, dù mục 0 ghi "sáu"), 10 bài luận PQ, lịch và nhật ký tiến độ.
- **Nội dung chính:**
  - Bảng lỗi đã đo F1–F7.
  - GS-Bench v1 gồm 4 tầng: B-a ca dựng; B-b tuyên bố sinh từ bảng hoặc câu thật; B-c cặp nhãn Claude; B-d gold người.
  - Quy tắc đo: chia theo công ty; ngưỡng ghi trước; không một con số gộp; số trên B-b gọi là "trên ca dựng", không gọi là "độ chính xác".
  - **Cổng tích hợp 06/11** gồm 5 điều kiện. Không qua thì trình bày là "nghiên cứu, chưa đưa vào sản phẩm".
- **Tiến độ 31/10–01/11:** AG-0, AG-1 (lượt A–G), chấm lại trên tập sạch v1.3, AG-2 v1, kiểm "cùng kết quả" của bộ đọc Q4 trên Kaggle, AG-3 v0. Phần cổng 06/11 còn thiếu vì laptop thiếu RAM.

### 1.7 `AUDIT_HE_THONG_2026-10.md` (14/10): phản biện 10 khâu
- **Kết luận:** lõi kiểm chứng trung thực, nhưng có 3 chỗ sẽ bị bắt:
  - chưa có số trên nhãn người;
  - hệ im lặng khi hỏng ở đầu vào (DOCX bị từ chối; trang scan cho 0 đoạn mà không cảnh báo). Đã sửa 14/10;
  - HPG phẳng: 153/156 PARTIAL, 154/156 MEDIUM, 156/156 pháp lý "chưa đủ", 780/780 bằng chứng nội bộ.
- **GreenScan Studio (14/10):**
  - 4 loại đề xuất sửa theo luật;
  - rào chắn `assert_no_new_numbers`;
  - xuất DOCX có tracked changes;
  - trên HPG neo được 147/156 tuyên bố và hiện 391 đề xuất.
- **Mức rủi ro "Cao" trước hội đồng:** đầu vào, T1, truy xuất, pháp lý, đo lường.

### 1.8 `ISSUES_REGISTER_2026-09.md`
- **B9:** dung sai 12 % là hằng số không có căn cứ. Thay bằng `comparison_policy` theo loại giá trị, gồm 8 nhánh (a)–(h).
- **N1–N5 (22/09):**
  - N1: so lệch chỉ số;
  - N2: đoạn nội bộ bị coi là nguồn thẩm quyền;
  - N3: trích nhầm câu không phải tuyên bố;
  - N4: SUPPORTED chỉ nhờ một cue;
  - N5: PARTIAL bị đẩy thành HIGH.
- **P1–P11:** định vị cho kiểm toán viên, gồm tính lại % thay đổi, điểm phần trăm so với % tương đối, xu hướng, áp luật theo ngành.
- **Q1–Q5 (10/10):** lỗi lớp chuẩn hoá phát hiện nhờ size ladder (chi tiết ở mục 3.8).

### 1.9 AG-0: mốc luật (không có README)
- Chạy nguyên đường ống `offline` của sản phẩm trên từng ca rồi quy về S/C/N.
- Kết quả trên từng tập:

  | Tập | Độ phủ | Precision | Ghi chú |
  |---|---|---|---|
  | v1 B-b | 0,028 (4/142) | 0,75 | bắt được 0/44 ca mâu thuẫn; nhận ra 3/26 câu nhắc lại nguyên văn |
  | v1.1 B-b | 0,060 | 0,625 | 9 SUPPORTED sai, 0 CONTRADICTED sai |
  | ngoài mẫu v1.2 | 0,006 | 1,0 | |

- File: `experiments/AG-0/out/score_rules*.json`.

### 1.10 AG-1: IR + thư viện so sánh tất định (`experiments/AG-1/README.md`)
- **Câu hỏi:** model nhỏ chạy tại chỗ có điền IR đủ tốt để code tự kết luận không?
- **Cách làm:** thang Qwen3 từ 0.6B đến 32B-AWQ, chạy vLLM trên Kaggle T4 × 2, có `ground()` và C-guard.
- **Diễn biến:**
  - Lượt A/C cho 4B precision 1,0 nhưng độ phủ chỉ 0,134; 32B có 7 vu oan.
  - Phân loại lỗi cho thấy đó là lỗi định dạng; sửa bằng `ground` (số trong mẫu).
  - Kiểm ngoài mẫu 246 ca: 4B 0,126 / 0,903. Sau sửa báo cáo, 4B **trượt cổng**.
  - Bản v1.2 thêm C-guard.
  - Lượt G (162 ca): 0 vu oan.
  - Tập sạch v1.3 (87 ca): 0 kết luận sai.
- **Đã rút lại** kết luận "4B mất độ phủ vì đọc năm"; đó là lỗi của tập.
- Chi tiết số ở mục 3.4.

### 1.11 AG-2: hai đường và cổng đồng thuận (không có README)
- Script `experiments/AG-2/policies.py`; bộ đọc sản phẩm `product_reader.py`. Kết quả nằm trong yaml, khối `agentic_ag2_v1` và `agentic_ag2_product`.
- **Kết quả:** chính sách "luật + 4B, bỏ phiếu S đơn độc của luật" là cấu hình duy nhất qua **phần thống kê** của cổng trên tập G.
- Bộ đọc Q4 qua Ollama khớp 0,963 với bản bf16 trên Kaggle.

### 1.12 AG-3 v0: dựng hàng bảng từ toạ độ chữ (`experiments/AG-3/README.md`)
- Trang 39 của báo cáo HPG dựng lại đủ 10 hàng; cộng dọc khớp 3/3.
- Trên 7 ca: trang thô đúng 1/7, hàng dựng lại đúng 3/7, 0 SUPPORTED sai.
- Dự đoán "N02/N05 thành C, ≥ 5/7 đúng" **sai**, vì IR còn thiếu chiều `segment`.
- Phát hiện phụ: tiêu đề trang ghi năm 2024, còn bảng ghi 2025.

### 1.13 `configs/measurement_decisions.yaml`
Các khối đăng ký trước:
- `measurement-decisions-v1` (29/09): κ ≥ 0,70; gold ≥ 60; điều kiện tháo chốt `lift_guard_*`; điều kiện bật dense (Recall@5 tăng ≥ 10 điểm, thời gian ≤ 2×).
- `model_selection_v2` (16/10).
- `agentic_v1`, `v1_1`, `v1_2`, `ag2_v1`, `ag2_product`, `ag3_v0`: mỗi khối có thời điểm đăng ký, dự đoán, điều kiện bác bỏ, sửa đổi và kết quả.

Đây là bằng chứng "đăng ký trước" mạnh nhất để đưa ra khi bị hỏi.

### 1.14 `docs/RUNS.md`
- 9 lượt Kaggle từ 31/10 10:40 đến 01/11 17:02, tất cả COMPLETE. Mỗi lượt ghi mốc log đầu, mốc xong, thời gian chạy, tài khoản và slug.
- Lỗi chạy đã gặp:
  - `No module named vllm`;
  - notebook quá 1 MB bị lỗi 400;
  - gemma-3-12b hết bộ nhớ khi nạp rồi sinh rỗng;
  - `kapi live` trả 0 dòng.

### 1.15 PQ-01, PQ-02, PQ-06 (bản nháp 31/10–01/11)
- **PQ-01 (tin được bao nhiêu):** "nói ít mà đúng". Hệ biết mình không chắc qua 3 tầng: không so được, bằng chứng tự mâu thuẫn, hai đường bất đồng. Không dựa vào độ tự tin của mô hình. Kết quả: 0 sai trên 87 ca sạch.
- **PQ-02 (bịa hoặc tính sai số):** chia rủi ro thành bịa và tính sai. Ba chốt: đọc → `ground` → `irlib`. Có bảng ca F01–F23 và luận điểm dung sai theo độ chính xác công bố.
- **PQ-06 (đo khi chưa có gold):** đáp án lấy từ họ nhiễu; lỗi nhãn 16/455; số trong mẫu tách khỏi số ngoài mẫu; không dùng con số gộp.
- **Phần đã cũ:** PQ-02 viết "AG-3 chưa chạy" và "bộ đọc Q4 chưa đo"; PQ-06 còn ô "[CHỜ]" và tỷ lệ lỗi nhãn 3,5 % (mục 5).

### 1.16 `MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`
- Trả lời nhận xét "mô hình quá bé" theo 4 ý:
  - Tiền đề sai: chế độ offline không chạy LLM; chế độ cloud dùng GLM-5.2, 753B tổng.
  - Từ khoảng 26B trở lên không thấy hiệu ứng kích thước.
  - Đầu dưới thì có hiệu ứng: qwen3:8b trên CPU cho 3 và 4 lần xác nhận sai, 66–257 s/ca.
  - Giới hạn thật nằm ở biểu diễn đầu vào (bảng), độ phủ của luật và dữ liệu trong miền.
- Có bảng tài liệu theo từng bước (PAL, PoT, MiniCheck, Joren, Lost in the Middle, ESGReveal).
- Có câu trả lời mẫu 90 giây và mục "không nói".

### 1.17 `OFFLINE_TUNG_PHAN_2026-10-10.md`
- Bốn nấc: L0a luật offline, L0b cloud nguyên văn, L1 che số và tên, L2 mô hình nhỏ chạy tại máy.
- **Thí nghiệm che số (L1):** độ chính xác giữ trong sai số; SUPPORTED sai về 0; 0 số liệu và 0 tên riêng trong nội dung gửi đi.
- **Nhận diện lại:** mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang. Vậy che số **không bảo vệ danh tính**.
- Bản thiết kế `cloud_masked` và sổ gửi đi **chưa làm**.

---

## 2. Khái niệm và lý thuyết phải nắm

### 2.1 Mười bước của một lượt phân tích (`agents/orchestrator.py`)

| # | Tên bước | Việc thật | LLM? |
|---|---|---|---|
| 1 | `validate_inputs` | kiểm tài liệu, tạo `run_id`, ghi `manifest.json` (băm đầu vào, `config_hash`, phiên bản gói luật, prompt) | không |
| 2 | `parse_and_ocr_documents` | PyMuPDF theo khối; trang dưới 40 ký tự thì chạy Tesseract tại máy; pdfplumber giữ bảng thành một khối TABLE; đoạn ≤ 3 câu, khoảng 600 ký tự; hồ sơ độ phủ kho | không |
| 3 | `extract_green_claims` | trích bằng luật (`configs/taxonomy.yaml`), loại tiêu đề, mục lục, dòng bảng, câu cụt (có ghi lý do); regex gán 5 thuộc tính | không (học trò T1 chưa nối) |
| 4 | `build_hybrid_retrieval_index` | dựng bộ truy xuất, bộ kiểm chứng, bộ pháp lý, bộ chấm điểm | không |
| 5 | `retrieve_evidence_per_claim` | điểm = 0,55·BM25 + 0,45·n-gram ký tự 3–5; RRF chỉ đổi thứ tự; lấy 30, giữ 5, luôn giữ 3 ứng viên tốt nhất (`floor_k`); gắn cờ dấu hiệu tiêm lệnh | không (embedding và reranker mặc định tắt) |
| 6 | `verify_claim_evidence_pairs` | chỉ khi bật mô hình: hỏi trước một lượt mọi cặp luật không quyết được | có, chế độ `cloud` |
| 7 | `check_applicable_law` | thực ra gồm kiểm chứng (số học → cụm từ → chiều thay đổi → độ giống), pháp lý (hiệu lực theo ngày) và chấm rủi ro | chỉ cho cặp khó, có chốt |
| 8 | `score_greenwashing_risk` | đọc số liệu công bố, cộng lại bảng, đối chiếu chéo, nhận diện chủ thể, xếp hàng đợi | không |
| 9 | `apply_quality_gates` | 8 cổng G0–G7 cho ra BLOCKED / PENDING_HUMAN_REVIEW / RELEASABLE | không |
| 10 | `write_evidence_pack` | ghi `result.json`, `evidence_pack.md`, 3 tầng `contract/` | không |

**Lưu ý khi bị hỏi:** tên các bước 6–8 trên thanh tiến độ không khớp việc thật (HE_THONG mục 7, dòng 9). Câu khẩu hiệu dùng khi trình bày: *Models read · Rules decide · Humans review*.

### 2.2 Quy tắc kết luận của verifier sản phẩm (5 nhãn)
- **CONTRADICTED** chỉ khi luật hoặc số học cho ra mâu thuẫn. Mâu thuẫn do mô hình phát hiện chỉ thành PARTIALLY_SUPPORTED kèm cờ chuyển người (`llm_stance_decisive: false`).
- **SUPPORTED** cần đủ ba điều kiện: đoạn bằng chứng từ **tài liệu khác**; điểm ≥ 0,22; khớp số, hoặc khớp cụm từ xác nhận cùng chỉ số, kỳ, phạm vi với ít nhất 2 thuộc tính.
- **UNSUPPORTED** chỉ khi kho tài liệu đủ để suy ra là vắng bằng chứng (`corpus_completeness: sufficient`). Còn lại là **INSUFFICIENT_EVIDENCE**.
- **Số học trong sản phẩm:** dung sai bằng ½ chữ số cuối đã công bố, trần 10 %. Lệch ≥ 0,35 thì bác bỏ; ở giữa thì "khớp một phần". Ngưỡng 0,35 vẫn còn trong `configs/default.yaml`, ghi là "giả thuyết, sẽ quét trên gold".
- **Thứ tự thẩm quyền:** số học → cụm từ (lexicon song ngữ, không dùng phủ định đơn) → xu hướng → tương đồng (không bao giờ tự quyết).

### 2.3 Mười bất biến (hiến pháp kỹ thuật, D-2026-09-25-01)

| # | Bất biến | Ví dụ gắn với GreenScan |
|---|---|---|
| 1 | Kiểm chứng tuyên bố, không phán xét doanh nghiệp | không có trường kết luận cấp công ty (test quét mã nguồn) |
| 2 | Tuyên bố nguyên tử, giữ nguồn | mọi đối tượng giữ `doc_id`, `chunk_id`, trang, nguyên văn |
| 3 | Truy xuất tìm ứng viên, không quyết sự thật | tương đồng cao không bao giờ cho ra S hay C |
| 4 | Chỉ so cái so được | lệch một chiều (chỉ số, loại giá trị, đơn vị, kỳ, năm gốc, ranh giới, Scope, công nghệ) thì **cấm** C |
| 5 | Số học là của code | `computed_values` mang `policy_id`; mô hình không được ghi đè comparator |
| 6 | Mục tiêu khác thành tích; thiếu dữ liệu khác thất bại | "sẽ giảm 30 %" không chứng minh "đã giảm"; UNSUPPORTED/INSUFFICIENT tách khỏi C, kể cả trong thang điểm |
| 7 | Pháp lý phải kiểm khả năng áp dụng, không chỉ mức liên quan | ngày hiệu lực → ngành → chủ thể → loại tuyên bố → điều kiện; quy tắc bị loại phải ghi lý do |
| 8 | Từ chối kết luận là kết quả hợp lệ | INSUFFICIENT_EVIDENCE hoặc chuyển người |
| 9 | Verdict ≠ risk ≠ priority | không dùng 72/100 thay cho đúng/sai |
| 10 | Tái lập được và người kiểm được | manifest, trích dẫn bắt buộc, tín hiệu chưa tính ghi `not_computed` chứ không ghi 0 |

Danh sách cấm, mỗi dòng gắn với một lỗi thật đã đo:
- LLM ghi đè comparator;
- dùng điểm tương đồng làm độ tin cậy;
- coi "không tìm được" là "sai";
- gộp UNSUPPORTED với CONTRADICTED;
- so Scope 1+2 với Scope 1, tập đoàn với nhà máy, tuyệt đối với cường độ (5/8 mâu thuẫn sai ngày 22/09 thuộc loại này);
- báo 0 cho tín hiệu chưa tính;
- thêm GraphRAG, fine-tune, đa tác tử hay quantum chỉ để trông "AI hơn".

### 2.4 Đường IR (AG-1, `irlib`)
- **IR (biểu diễn trung gian):** mỗi số liệu môi trường trong một câu được điền thành một bản ghi gồm: chỉ số, `value_text` nguyên văn, bội số, đơn vị, loại giá trị (tuyệt đối, đếm, cường độ, tỷ trọng, thay đổi), kỳ, năm gốc, Scope, ranh giới tổ chức, thực hiện hay mục tiêu, chiều thay đổi. Mô hình chỉ **đọc**.
- **`ground(fig, câu)`:** con số phải xuất hiện nguyên văn trong câu. Bội số phải là chữ câu viết ngay sau số đó. Năm phải là năm câu có viết. Số liệu không neo được thì bị bỏ.
- **`comparable`:** phải cùng chỉ số, loại giá trị (đếm và tuyệt đối coi là một từ v1.2), thực hiện/mục tiêu, kỳ, Scope, năm gốc (với loại "thay đổi"), ranh giới (trừ khi "unspecified") và chiều đơn vị. Lệch một chiều thì trả **N** kèm tên chiều lệch.
- **`compare`:**
  - Dung sai = h(tuyên bố) + h(bằng chứng), với h bằng ½ đơn vị của chữ số cuối được viết, nhân bội số và hệ số đơn vị.
  - S khi |v_c − v_e| ≤ dung sai, ngược lại là C.
  - Đảo chiều tăng/giảm thì là C.
  - Khác verifier sản phẩm: **không có vùng 0,35**.
- **Ví dụ F01:** tuyên bố "khoảng 23,5 triệu tCO2e", bằng chứng 23.474.480 tCO2e. Dung sai = 50.000 + 0,5 = 50.000,5. Chênh 25.520, nên ra S.
- **Ví dụ 12 %:** "12 %" so với 11,6 % thì S (dung sai 0,5 + 0,05). "12,0 %" so với 11,6 % thì C (dung sai 0,05 + 0,05). Ai viết số chính xác hơn thì bị so chặt hơn.
- **`decide`:**
  - Có số so được và khớp, không số nào lệch: S.
  - Chỉ có số lệch: C.
  - Lẫn lộn hoặc không so được: N.
  - **C-guard (v1.2):** một kết luận C dựa trên chênh giá trị bị hạ về N khi câu bằng chứng có viết đúng con số và bội số của tuyên bố, vì khi đó bộ đọc đã bỏ sót số liệu ấy. Đảo chiều thì vẫn giữ C.
- **Ví dụ Coteccons:** câu bằng chứng ghi 10.175 cây, gồm 2.175 cây và 8.000 cây. Tuyên bố "8.000 cây" bị đem so với 10.175, thành vu oan. C-guard chặn được ca này.

### 2.5 Đo khi chưa có gold: GS-Bench
- **Đáp án theo cấu trúc** (kiểm thử bằng nhiễu có kiểm soát, cùng tinh thần CheckList): lấy một số liệu thật, viết lại tuyên bố theo một **họ nhiễu** đã biết đáp án.
  - Đáp án S: S0 nhắc lại, S1 làm tròn.
  - Đáp án C: C1 đổi giá trị, C2 đổi bội số, C3 đảo chiều.
  - Đáp án N: N1 đổi kỳ, N2 đổi thực hiện thành mục tiêu, N3 đổi Scope, N4 đổi ranh giới, N5 đổi tuyệt đối thành cường độ, N6 đổi chỉ số.
- **Nhãn bạc và nhãn vàng:**
  - IR của câu bằng chứng do Claude đọc một lượt (tập ngoài mẫu v1.2 thì do Qwen3-32B đọc), rồi qua bộ kiểm tất định. Đó là nhãn **bạc**.
  - **Vàng** là nhãn người có hai người gán và trọng tài. Thang trưởng thành L0–L5 (brief): L4 đã trọng tài, L5 gold chỉ dùng cho báo cáo cuối.
- **Tầng của GS-Bench:**
  - B-a: 51 ca dựng tay, gồm 32 ca sạch và 19 ca trên trang HPG thô;
  - B-b: tuyên bố sinh từ câu thật;
  - B-c: cặp tuyên bố–đoạn thật, nhãn Claude 2 lượt mù;
  - B-d: gold người.
- **Giới hạn cố hữu:**
  - Bằng chứng được đưa sẵn đúng câu, nên AG không đo khâu truy xuất.
  - Tuyên bố sinh theo khuôn, dễ đọc hơn câu thật.
  - Câu "B-b đại diện cho tuyên bố thật" là **[GIẢ THUYẾT]**.

### 2.6 Chỉ số
- **Độ phủ** (coverage) = số ca hệ dám kết luận S hoặc C / n.
- **Precision trên phần dám kết luận** = số kết luận S/C đúng / số kết luận S/C.
- **CONTRADICTED sai** (vu oan) và **SUPPORTED sai** (bỏ lọt) báo riêng. Không dùng một con số gộp.
  - Ví dụ: luật trên 402 ca B-b có 0 vu oan nhưng 9 bỏ lọt, precision 0,625. Nếu chỉ ghi "đúng 192/402" thì che mất cả hai sự thật này.
- **Đường risk–coverage** (selective prediction): độ đúng thay đổi theo tỷ lệ ca dám kết luận. Một hệ không kết luận gì có "0 lỗi" nhưng vô dụng. Tài liệu ngoài: EmeraldMind đúng 94,21 % nhưng chỉ trả lời 25,97 % số ca **[NGOÀI]**.
- **Macro-F1** = trung bình F1 của các lớp, với F1 = 2PR / (P + R). **κ Cohen** = (p_o − p_e) / (1 − p_e).

### 2.7 Thống kê phải nói được
- **Bootstrap theo công ty:** lặp 2.000 lần; mỗi lần rút có hoàn lại K công ty trong K, lấy mọi ca của chúng, tính chỉ số; khoảng tin cậy là phân vị 2,5–97,5. Lý do: các câu của cùng một báo cáo không độc lập.
- **Khoảng tin cậy suy biến:** khi mọi ca dám kết luận đều đúng, bootstrap cho ra [1,0; 1,0]. **Không được trình bày đó như bằng chứng.** Dùng Clopper–Pearson thay thế; với x = n thì cận dưới 95 % hai phía bằng (0,025)^(1/n) **[KIẾN THỨC NỀN, tự tính 04/11]**:

  | Số ca dám kết luận, 0 sai | Cận dưới precision | Hệ |
  |---|---|---|
  | n = 10 | khoảng 0,69 | 8B, 14B trên tập sạch |
  | n = 12 | khoảng 0,74 | 4B trên tập sạch |
  | n = 15 | khoảng 0,78 | 4B trên tập G |
  | n = 22 | khoảng 0,85 | 32B trên tập sạch |

  **Quy tắc 3:** 0 lỗi trong n ca thì tỷ lệ lỗi thật có thể tới khoảng 3/n (n = 12 cho khoảng 25 %).
- **Cận Beta trong AG-2:** một xô được giữ khi phân vị 2,5 % của Beta(k+1, n−k+1) lớn hơn 0,90 (với C) hoặc 0,80 (với S). Với 81 xô có thể có và chỉ 7 công ty, không xô nào qua, nên chính sách xô quyết 0 ca.
- **McNemar chính xác:** so hai hệ trên cùng ca, chỉ dùng các ca bất đồng. Size ladder có p ≤ 0,022 cho luật so với các mô hình.
- **Wilson:** với n = 60–100 thì khoảng tin cậy rộng khoảng ±8–11 điểm. Với 60–100 cặp, κ = 0,70 có khoảng tin cậy khoảng [0,52; 0,88].

### 2.8 Đăng ký trước, trong mẫu và ngoài mẫu, cổng và dự đoán
- **Đăng ký trước:** ghi dự đoán, ngưỡng và điều kiện bác bỏ vào yaml **trước khi** thấy đầu ra. Sửa đổi chỉ hợp lệ khi ghi trước khi đầu ra được xem (ví dụ 14:40 và 22:50 ngày 31/10).
- **Trong mẫu và ngoài mẫu:**
  - Cách sửa rút ra từ chính các ca đang chấm thì số đó là trong mẫu, không phải bằng chứng.
  - Phải kiểm trên tập ngoài mẫu mới. Bài học: độ phủ của 4B là 0,437 trong mẫu nhưng chỉ 0,126 ngoài mẫu, nói quá hơn 3 lần.
- **Dự đoán và cổng:** dự đoán cho biết giả thuyết đứng hay đổ; cổng cho biết có được vào sản phẩm không. Phải báo kết quả so với **cả hai**. Ví dụ: 4B có 2 vu oan, đúng dự đoán (≤ 2) nhưng trượt cổng (≤ luật + 1 = 1).
- **Oracle:** thay một tầng bằng đáp án đúng để biết trần. IR gold + `irlib` trên v1 B-b cho độ phủ 0,528, precision 1,0. Đó là trần của cách tiếp cận IR trên tập đó.

### 2.9 Chính sách hai đường (AG-2)
- `union`: các đường dám kết luận đều đồng ý thì lấy nhãn đó, còn lại N.
- `union_noloneS`: như `union`, nhưng một S **chỉ do luật đưa ra** thì thành N.
  - Lý do: S đơn độc của luật chỉ đúng 1/6 ca trên tập ngoài mẫu của lượt D.
  - Giữ phiếu đó thì giữ luôn 8 SUPPORTED sai của luật trên tập hiệu chỉnh.
- `bucket`: xác suất đúng theo xô (nhãn luật, nhãn hợp, số đường IR cho nhãn), ước trên tập hiệu chỉnh, có cận Beta.

### 2.10 Chạy mô hình
- **bf16 và fp16:** trọng số đầy đủ, dùng trên Kaggle.
- **AWQ:** lượng tử hoá 4-bit cho 14B và 32B.
- **GGUF Q4_K_M / Q8_0:** lượng tử hoá cho llama.cpp và Ollama, chạy trên CPU laptop. Q4 cần 3,3 GiB RAM.
- **Parity (cùng kết quả):** tỷ lệ ca có cùng nhãn S/C/N giữa bộ đọc lượng tử hoá và bản bf16.
- **vLLM, greedy, TP:** vLLM chạy suy luận; greedy là giải mã tham lam, tái lập được; TP (tensor parallel) chia một mô hình lên 2 GPU.
- **MoE:** "tham số kích hoạt" khác "tham số tổng". GLM-5.2 có 753B tổng; gemma-4-26B-A4B chỉ kích hoạt khoảng 3,8B.

### 2.11 Bảng PDF
- **Cộng dọc/ngang (cross-foot):** tổng phải bằng tổng các thành phần, trong dung sai làm tròn. Ví dụ: 22.540.603 + 933.876 = 23.474.479, so với 23.474.480 công bố, chỉ lệch 1.
- **Hàng tiêu đề:** hàng chỉ có số năm cho biết năm và đơn vị của các hàng bên dưới.
- **`segment`:** mảng kinh doanh (thép, nông nghiệp…). IR hiện chưa có chiều này, nên N02/N05 còn N.

### 2.12 Riêng tư và chế độ chạy
- **`QUANTUM_PROFILE`:**
  - `offline` (mặc định): không gửi gì ra ngoài;
  - `cloud`: cặp khó gửi sang FPT, định tuyến GLM-5.2;
  - `gpu`: vLLM tại máy, nhưng vẫn dự phòng sang FPT.
- **Loại dữ liệu:**
  - A, công khai: dùng mọi chế độ;
  - B, nội bộ: dùng `offline`, `gpu` hoặc FPT Dedicated có hợp đồng;
  - C, giấy làm việc kiểm toán: chỉ `offline` hoặc `gpu` tại đơn vị (D-2026-10-06-06).
- **L1 (che số và tên):** mô hình chỉ ánh xạ số nào trong bằng chứng ứng với số nào trong tuyên bố, rồi máy điền giá trị thật và tự tính. **Nhận diện lại:** tổ hợp ngành và thuật ngữ đặc thù vẫn lộ danh tính doanh nghiệp.

### 2.13 Rủi ro, ưu tiên, cổng
- **Rubric `risk-rubric-v2`** gồm 9 thành phần, tổng trần 100 (`configs/scoring_v1.yaml`):

  | Thành phần | Trần | Thành phần | Trần |
  |---|---|---|---|
  | Tính cụ thể của chỉ số | 12 | Bằng chứng hỗ trợ | 18 |
  | Số liệu định lượng | 12 | Bảo đảm độc lập | 8 |
  | Năm gốc | 8 | Mâu thuẫn | 18 |
  | Kỳ báo cáo | 8 | Ngôn ngữ mơ hồ, phóng đại | 8 |
  | Phạm vi, ranh giới | 8 | | |

  Dải mức: Thấp 0–24, Trung bình 25–49, Cao 50–74, Nghiêm trọng 75–100. PARTIAL do thiếu thuộc tính tối đa MEDIUM.
- **Hàng đợi `priority-v1.1`:** trọng yếu 40, nghĩa vụ pháp lý 25, khoảng trống bằng chứng 25, bất thường 10 (chưa tính, ghi `not_computed`). Câu không nêu chủ thể và không có số thì trọng yếu ×0,75; chữ dính cột thì ×0,5. Hàng đợi **chỉ đổi thứ tự**, không đổi verdict.
- **Tám cổng G0–G7:** G0 provenance; G1 trung thực trích xuất; G2 truy xuất đủ; G3 số học bằng mã (hiện luôn đạt); G4 toàn vẹn trích dẫn; G5 rủi ro cao chờ người; G6 tái lập; G7 pháp lý.

### 2.14 QUBO chọn bằng chứng (chỉ có trên giấy)
- Công thức: H(x, y) = −Σ r_j·x_j + λ·Σ s_jl·x_j·x_l − γ·Σ w_m·y_m + μ·(Σ x_j − k)² + ν·Σ y_m·(1 − Σ_{j∈J_m} x_j)₊.
  - r_j: độ liên quan của đoạn j;
  - s_jl: độ trùng lặp giữa hai đoạn;
  - y_m: biến phủ cho từng thuộc tính bắt buộc m;
  - k: **số đoạn mục tiêu**, không phải số tối đa.
- Benchmark dự kiến: 4 cột (top-k, MMR, nghiệm chính xác, SA/QAOA) × 4 chỉ tiêu.
- **Không có mã:** grep "qubo" trong `*.py` ngày 04/11 cho 0 kết quả. Không tuyên bố lợi thế lượng tử (D-2026-09-18-06).

### 2.15 Hai nguyên lý thiết kế dựa trên tài liệu ngoài
- **Hệ thống ghép** (compound AI; Zaharia và cs., BAIR 2024) **[NGOÀI]**.
- **Giao phép tính cho công cụ** (PAL; Program-of-Thoughts: GPT-4 trên FinQA tăng từ 58,2 lên 74,0 khi giao tính toán cho mã) **[NGOÀI]**.
- Hệ quả cho GreenScan: kích thước mô hình chỉ là ràng buộc ở bước nhận diện tuyên bố và một phần bước chuẩn hoá. Ở các bước bảng, tìm bằng chứng, số học và từ chối, mô hình lớn hơn không sửa được lỗi (MO_HINH mục 1).

---

## 3. Số liệu và dữ kiện được phép nói

Ký hiệu loại đáp án:
- **(ca dựng):** đáp án do đội dựng;
- **(bạc):** tuyên bố sinh từ câu thật, đáp án theo họ nhiễu, IR bằng chứng do Claude hoặc 32B đọc, có bộ kiểm tất định;
- **(nhãn Claude):** nhãn Claude, 2 lượt mù + trọng tài;
- **(nhãn người);**
- **(đếm, không nhãn):** đếm trên tài liệu thật.

Mỗi ô kết quả viết theo dạng độ phủ / precision / SUPPORTED sai / CONTRADICTED sai, nếu không ghi khác.

### 3.0 Mười hai con số nên đưa lên slide (mới nhất, kèm câu nói an toàn)

| # | Câu nói được | Nguồn | Nhãn |
|---|---|---|---|
| 1 | "Trên 87 ca ngoài mẫu đã làm sạch (bạc), đường mô hình đọc + code tính có **0 kết luận sai**. 4B dám kết luận 12/87 ca (13,8 %), 32B 22/87 (25,3 %), luật thuần 1/87 (1,1 %)." | `experiments/AG-1/out/v13/score_heldout.json`; AG-1 README, mục 01/11 17:00 | [ĐÃ THỰC NGHIỆM] (bạc) |
| 2 | "Hai đường **luật + 4B, bỏ phiếu khớp đơn độc của luật**, trên 162 ca ngoài mẫu: độ phủ 9,3 % so với 0,6 % của luật, 0 kết luận sai; phần tăng độ phủ có khoảng tin cậy [1,6; 18,5] điểm." | yaml `agentic_ag2_v1.result_2026-10-31_23h50` | [ĐÃ THỰC NGHIỆM] (bạc) |
| 3 | "Bộ đọc 4B nén Q4 chạy được bằng Ollama khớp bản gốc ở 96,3 % số ca; cùng chính sách hai đường vẫn 0 sai, độ phủ 8,0 %." | yaml `agentic_ag2_product.result_2026_11_01` | [ĐÃ THỰC NGHIỆM] (bạc; đo trên Kaggle, chưa đo trên laptop) |
| 4 | "Neo số vào câu gốc (`ground`) làm giảm vu oan ngoài mẫu ở mọi mô hình: 3→2, 12→1, 7→3, 3→2 (246 ca)." | yaml `agentic_v1_1.result_held_out_246_runs_E_F` | [ĐÃ THỰC NGHIỆM] (bạc) |
| 5 | "Cả 11 kết luận sai của Qwen3-32B ở lượt đầu chung một lỗi: mô hình tự thêm bội số ('10.730 m3' thành '10.730 ngàn m3'). Đội sửa bằng code, không sửa bằng mô hình to hơn." | AG-1 README, mục 31/10 14:10 | [ĐÃ THỰC NGHIỆM] |
| 6 | "Thang mô hình 51 ca dựng: luật đúng 20/32 và 7/19; các mô hình 26B–753B đúng 29–32/32 và 15–18/19; **mọi** mô hình đều xác nhận sai trên bảng dàn phẳng (N02, N05)." | `MO_HINH_CO_QUA_BE_KHONG` mục 2; paper mục 6.2 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| 7 | "Che số trước khi gửi mô hình đám mây: xác nhận sai về 0, không lọt số hay tên nào; nhưng mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang." | `OFFLINE_TUNG_PHAN` mục 5 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| 8 | "Báo cáo HPG 264 trang: 107–121 giây, RAM đỉnh 1,33 GB, laptop không GPU, 0 kết nối ra ngoài." | paper mục 6.4; HE_THONG mục 3 | [ĐÃ THỰC NGHIỆM] |
| 9 | "Trên HPG: 156 tuyên bố, 153 'khớp một phần', hàng đợi 9/172 mục, 780/780 bằng chứng là tài liệu của chính doanh nghiệp, 0/156 quy tắc pháp lý áp được." Nói như **thực trạng và giới hạn**, không nói như thành tích. | AUDIT mục 0; KE_HOACH mục 2 | [ĐÃ THỰC NGHIỆM] (đếm, không nhãn) |
| 10 | "Cho LLM tự quyết trên HPG thì sinh 10 kết luận 'mâu thuẫn', phần lớn sai; khi có chốt chặn thì còn 0, và 13 câu được chuyển người." | paper mục 6.3; D-2026-09-28-01 | [ĐÃ THỰC NGHIỆM] (soát tay, không gold) |
| 11 | "Học trò e5-base (278 triệu tham số, 119 ms/câu trên CPU) đồng thuận với nhãn Claude ở macro-F1 0,73, so với luật 0,36; **chưa nối vào sản phẩm**." | paper mục 6.1; `training/runs/kaggle_t1_v3/results.json` | [ĐÃ THỰC NGHIỆM] (nhãn Claude) |
| 12 | "Nhãn người hiện bằng 0, nên đội không công bố 'độ chính xác X %'." | KE_HOACH mục 0 (kiểm 31/10) | [ĐÃ THỰC NGHIỆM] (cần cập nhật 04/11: [CHƯA XÁC MINH]) |

### 3.1 Sản phẩm trên tài liệu thật (đếm, không nhãn trừ khi ghi khác)

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| Lượt HPG `c892c13727c24bb9` (22/10), giống lượt demo `cd5a82e326bf4117` (09/10): 156 tuyên bố gồm 153 PARTIAL, 2 SUPPORTED, 1 INSUFFICIENT; hàng đợi 9/172 | KE_HOACH mục 2 F1; AUDIT mục 0 | [ĐÃ THỰC NGHIỆM] |
| 154/156 MEDIUM; 780/780 bằng chứng nội bộ (`has_independent: False`); quan hệ 648 PARTIAL / 84 CONTEXT / 48 SUPPORTS | AUDIT mục 0 và 5; paper mục 6.4 | [ĐÃ THỰC NGHIỆM] |
| Pháp lý: 156/156 `legal_finding` INSUFFICIENT, 0 quy tắc áp dụng. Gói `vn-green-v0.1-draft` có đúng 1 quy tắc nháp (`VN_GREEN_TAXONOMY_001`), `reviewed_by` để trống | AUDIT mục 7; `configs/legal/rule_pack_vn_green_v0.1.yaml` (kiểm 04/11) | [ĐÃ THỰC NGHIỆM] |
| Thuộc tính: 133/156 thiếu kỳ, 152/156 thiếu năm gốc, 127/156 không có số. Chưa tách được bao nhiêu là thực trạng công bố, bao nhiêu là lỗi trích | AUDIT mục 4 | [ĐÃ THỰC NGHIỆM] |
| HPG (BCPTBV 2025 + BCTN 2024, 264 trang): 107–121 s, RAM đỉnh 1,33 GB, i7-1355U 16 GB, `offline` | paper mục 6.4; `benchmark/queue_quality_2026-10-06.md` | [ĐÃ THỰC NGHIỆM] |
| `offline`: chặn mọi kết nối khi phân tích 264 trang, kết quả 0 lần (09/10) | HE_THONG mục 3 | [ĐÃ THỰC NGHIỆM] |
| Cộng lại bảng KNK: 22.540.603 + 933.876 = 23.474.479 so với 23.474.480 công bố → khớp (làm tròn). HPG có 16 số liệu công bố; chỉ 1 phép kiểm số liệu chạy | paper mục 4.2; AUDIT mục 4 | [ĐÃ THỰC NGHIỆM] |
| A/B 28/09 trên 780 cặp (67 cặp luật tự quyết, 713 cặp còn lại):<br>- Tắt mô hình: 153/2/0/1 (PARTIAL/SUPPORTED/CONTRADICTED/INSUFFICIENT), 144 s.<br>- Bật, tự quyết: 136/6/10/4; 8 HIGH + 2 CRITICAL trên doanh nghiệp đối chứng; 632 s, 710 lời gọi.<br>- Bật, có chốt: 150/2/0/4; 0 HIGH/CRITICAL; 13 câu chuyển người; 188 s (có cache).<br>Khi bật, 327 cặp lộ ra chỉ là bối cảnh; 3 tuyên bố chuyển đúng sang INSUFFICIENT | paper mục 6.3; D-2026-09-28-01 | [ĐÃ THỰC NGHIỆM] (soát tay) |
| Lịch sử vu oan:<br>- 17/09: 357/419 kết luận "mâu thuẫn" sai.<br>- 22/09: HPG có 7/8 CONTRADICTED sai, 3/3 SUPPORTED chỉ nhờ một cue, 93 % PARTIAL chung một lý do, 65 HIGH + 1 CRITICAL trên doanh nghiệp đối chứng.<br>- 25/09: audit ngữ nghĩa cho thấy không mâu thuẫn cũ nào còn đứng.<br>- Từ đó HPG có 0 CONTRADICTED sai | PQ-01 mục 3.1; D-2026-09-22-01; ARCHITECTURE_INVARIANTS; AUDIT mục 6 | [ĐÃ THỰC NGHIỆM] |
| Hàng đợi 06/10: sau khi sửa lỗi gộp dấu ("cộng" và "công") và nhãn NĐ 83/2026, hàng đợi còn 9/172 mục, 0 trích dẫn pháp lý sai, verdict không đổi. Trước khi sửa, 25/57 "số liệu công bố" thực ra là tỷ lệ sở hữu, cơ cấu giới tính hoặc công suất | paper mục 6.4; D-2026-10-06-03 | [ĐÃ THỰC NGHIỆM] |
| Lượt soát của người ngày 11/10 trên hàng đợi HPG: đồng ý 12/14 mục; hàng đợi đúng khoảng 6/9 | paper mục 5.2; AUDIT mục 8 | [ĐÃ THỰC NGHIỆM] (nhãn người, n rất nhỏ, **không phải gold**) |
| 4 ca thật đã có phán quyết (KDP 2024, BNY 2022, DWS 2023, KLM 2024): 4/4 khớp CONTRADICTED, 4/4 khớp lập trường, 2/4 khớp dải rủi ro; trước ADR 0003 là 0/4. `run_case.py --all` cho 4/4 dù bật hay tắt mô hình | brief mục "Kết quả đo được đến 9/2026"; paper mục 5.3 | [ĐÃ THỰC NGHIỆM] |
| Đầu vào (14/10): 4/108 trang BCPTBV HPG là ảnh quét; máy demo không có tesseract nên mất chữ ở 4 trang này. Đã thêm cảnh báo; cài tesseract là việc P0 | AUDIT mục 2 | [ĐÃ THỰC NGHIỆM] ([CHƯA XÁC MINH] đã cài chưa) |
| Studio trên HPG (14/10): neo được 147/156 tuyên bố; 391 đề xuất (140 phạm vi/kỳ, 124 chỗ trống, 119 dẫn chiếu, 8 làm nhẹ); mở tài liệu 0,31 s; xuất DOCX 0,06 s; PDF 130 trang 0,34 s | AUDIT mục 12 | [ĐÃ THỰC NGHIỆM] |

### 3.2 Ca dựng: size ladder và che số (10/10)

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| 51 ca: 32 ca sạch (13 nhóm lỗi) và 19 ca dùng nguyên văn 3 trang HPG. Nhãn S/C/N suy từ GHG Protocol, không suy từ luật GreenScan; một người đặt đáp án | MO_HINH mục 2; OFFLINE mục 9 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| Luật: đúng 20/32 (kết luận 8, đúng 6) và 7/19 (kết luận 3, đúng 3). Số "đúng" tính cả ca N đúng. Trên ca sạch luật có 1 SUPPORTED sai (F11, cường độ) và 1 CONTRADICTED sai (F20, công ty mẹ so với hợp nhất) | MO_HINH; `experiments/AG-0/out/score_rules.json` | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| Từng mô hình (sạch · trang thật · xác nhận sai trên trang thật · thời gian/ca):<br>- gemma-4-26B-A4B: 29 · 18 · 1 · 1,2 s<br>- gemma-4-31B: 32 · 17 · 2 · 1,5 s<br>- Llama-3.3-70B: 30 · 15 · 3 · 2,8 s<br>- GLM-5.2: 32 · 17 · 2 · 13,7 s<br>- qwen3:8b trên CPU: 28 · 12 · 4 · 66–257 s (thêm 3 xác nhận sai trên ca sạch) | paper mục 6.2; MO_HINH mục 2 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| McNemar luật so với các mô hình: p ≤ 0,022 trên bộ sạch | MO_HINH mục 0 | [ĐÃ THỰC NGHIỆM] |
| Mọi mô hình ≥ 26B đều báo SUPPORTED sai ở N02 ("phạm vi 1 là 23.369.500", thật ra là số của mảng thép) và N05 ("nông nghiệp 933.876", thật ra là số phạm vi 2) | KE_HOACH F3; AG-3 README mục 1 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| Che số L1, không che → che:<br>- gemma-31B: sạch 32 → 32, trang thật 17 → 18.<br>- Xác nhận sai: 2 → 0 ở 26B, 31B và GLM.<br>- Mâu thuẫn sai: 26B 1 → 1; 31B 0 → 1; GLM 0 → 3.<br>- 0/51 ca còn giá trị số; 0 tên riêng | OFFLINE mục 5.1–5.2 | [ĐÃ THỰC NGHIỆM] (ca dựng) |
| Nhận diện lại bằng gemma-31B: đoán đúng doanh nghiệp ở 5/20 câu (độ tự tin 70–90) và 3/3 trang (100) | OFFLINE mục 5.3 | [ĐÃ THỰC NGHIỆM] |
| GLM-5.2 không tất định dù nhiệt độ 0: cùng bộ cho 17/19 rồi 16/19 | OFFLINE mục 5.1 | [ĐÃ THỰC NGHIỆM] |

### 3.3 GS-Bench: tập và lỗi nhãn

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| v1 (31/10): 193 ca = 51 B-a + 142 B-b sinh từ 26 số liệu thật của 5 doanh nghiệp. `irlib` tự ra đúng nhãn họ nhiễu ở 142/142 ca. Soát tay 14 ca, sửa 3 lỗi diễn đạt | KE_HOACH mục 10 (31/10) | [ĐÃ THỰC NGHIỆM] |
| v1.1: 453 ca = 51 B-a + 402 B-b (S 95, C 123, N 184), 7 doanh nghiệp: bvh 116, dhg 88, tra 57, vnm 52, ctd 35, pnj 28, pow 26 ca. Giữ 77 số liệu trong 203 số liệu đọc được | KE_HOACH; đếm `gs_bench_v1.jsonl` (04/11) | [ĐÃ THỰC NGHIỆM] (bạc) |
| Lỗi nhãn v1.1: 16/455 (3,5 %), gồm 2 ca C2 trên giá trị 0 và 14 ca PV Power thiếu Scope. Lỗi được tìm nhờ đọc những chỗ luật bất đồng với nhãn | PQ-06 mục 3.2 | [ĐÃ THỰC NGHIỆM] |
| Tập ngoài mẫu v1.2: 162 ca, 9 doanh nghiệp (dpr và cng mới), S 38 / C 55 / N 69. Bộ đọc A là Qwen3-32B, nên điểm của 32B **lạc quan theo cách dựng** | yaml `agentic_v1_2.amendment_2026-10-31_22h50` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Hậu kiểm v1.2: 75/162 ca hỏng (other_env 60, tên chỉ số có chữ số 6, đơn vị giả 4, năm lấy từ tiêu đề 5). Bỏ theo quy tắc tất định, không gán lại nhãn nào. Còn tập sạch v1.3: 87 ca (S 19 / C 28 / N 40, 7 doanh nghiệp) | AG-1 README mục 01/11; `stats_v13.json`; `errata_v13.txt` | [ĐÃ THỰC NGHIỆM] |
| Tập hiệu chỉnh sạch v1.3: 448 ca (B-b 397; bỏ 5 ca có tên chỉ số chứa chữ số) | `stats_v13.json` | [ĐÃ THỰC NGHIỆM] |

### 3.4 AG-0, AG-1: luật, oracle và bộ đọc IR (Kaggle T4 × 2, vLLM 0.32, greedy)

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| Luật trên v1 B-b (142): độ phủ 0,028 (4/142), precision 0,75 [0,5; 1,0], bắt được 0/44 ca C, nhận ra 3/26 ca S0 | `experiments/AG-0/out/score_rules.json` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Oracle (IR gold + `irlib`) trên v1 B-b: đúng 140/142, độ phủ 0,528, precision 1,0, 0 sai. Hai ca hụt là câu gộp hai nhiên liệu | KE_HOACH 31/10 | [ĐÃ THỰC NGHIỆM] (bạc) |
| Lượt đầu (31/10 11:45, v1 B-b) theo dạng độ phủ / precision / C sai / S sai / B-a sạch:<br>- luật 0,028 / 0,75 / 0 / 1 / 20/32<br>- 0.6B 0,127 / 0,39 / 4 / 7<br>- 1.7B 0,183 / 0,54 / 8 / 4<br>- 4B 0,134 / 1,00 / 0 / 0 / 17/32<br>- 32B-AWQ 0,423 / 0,82 / 7 / 4 / 23/32<br>- 8B (lượt B): 0,232 / 0,636<br>- 14B-AWQ (lượt B): 0,254 / 0,944<br>- gemma-3-12b: sinh rỗng, loại | AG-1 README mục 5 | [ĐÃ THỰC NGHIỆM] (bạc) |
| Phân loại lỗi: 32B có 11/11 kết luận sai do bội số tự thêm; 4B mất 50 tuyên bố vì nhét bội số và đơn vị vào `value_text`; 1.7B không đọc được bằng chứng ở 25 ca | AG-1 README mục 5 (14:10) | [ĐÃ THỰC NGHIỆM] |
| Sau `ground`, **trong mẫu** (142 ca), độ phủ trước → sau, precision sau:<br>- 1.7B: 0,183 → 0,183; 0,85; C sai 8 → 0<br>- 4B: 0,134 → 0,437; 0,984<br>- 8B: 0,232 → 0,408; 0,983<br>- 14B: 0,254 → 0,451; 0,984<br>- 32B: 0,423 → 0,465; 0,985; C sai 7 → 1<br>Số trong mẫu, **không phải bằng chứng** | yaml `agentic_v1_1.in_sample_193_B-b_142` | [ĐÃ THỰC NGHIỆM] (trong mẫu) |
| Ngoài mẫu lượt D (246 ca B-b mới):<br>- luật 0,077 / 0,632 / 7 / 0<br>- 4B thô 0,053 / 0,692 / 1 / 3<br>- **4B có `ground` 0,126 / 0,903 [0,81; 1,0] / 1 / 2**<br>- 1.7B có `ground` 0,037 / 0,778 / 2 / 0 | yaml `agentic_v1_1.result_held_out_246_run_D` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Mất độ phủ của 4B ở lượt D: 39 ca bằng chứng nhiều số không đọc được; 27 ca lệch `value_kind`; 13 ca không đọc được tuyên bố | yaml `loss_buckets_4b` | [ĐÃ THỰC NGHIỆM] |
| Ngoài mẫu lượt E/F (cùng 246 ca), có `ground` (v1.1):<br>- 8B 0,220 / 0,963 [0,90; 1,0] / 1 / 1<br>- 14B 0,256 / 0,921 / 2 / 3<br>- 32B 0,329 / 0,951 [0,891; 0,992] / 2 / 2<br>Chấm thô không `ground`, C sai là 12 / 7 / 3 | yaml `result_held_out_246_runs_E_F` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Mọi vu oan của mọi mô hình đều nằm ở cùng một câu của Coteccons (số con đem so với số tổng) | yaml `false_C_cases` | [ĐÃ THỰC NGHIỆM] |
| Bản v1.2 trên cùng 246 ca (một phần trong mẫu):<br>- 4B 0,130 / 0,969 / 1 / 0<br>- 8B 0,224 / 0,982 / 1 / 0<br>- 14B 0,280 / 0,957 / 2 / 1<br>- 32B 0,321 / 0,975 / 2 / 0 | yaml `agentic_v1_2` | [ĐÃ THỰC NGHIỆM] (một phần trong mẫu) |
| Lượt G (162 ca ngoài mẫu v1.2), bản v1.2:<br>- luật 0,006 / 1,0 / 0 / 0<br>- **4B 0,093 / 1,0 / 0 / 0 (15 ca dám kết luận)**<br>- 8B 0,068 / 0,909 [0,40; 1,0] / 1 / 0<br>- 14B 0,086 / 0,929 [0,625; 1,0] / 1 / 0<br>- 32B 0,228 / 0,973 / 1 / 0 (tập lệch về 32B)<br>C-guard có tác dụng 1 lần (8B: 1 → 0) | yaml `result_held_out_162_run_G` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Tập con 102 ca không thuộc other_env (hậu kiểm, ngoài đăng ký): 4B 0,147 / 1,0; 8B 0,108 / 0,909; 14B 0,137 / 0,929; 32B 0,275 / 1,0; mọi mô hình 0 vu oan | yaml `bench_defect_post_hoc` | [ĐÃ THỰC NGHIỆM] (hậu kiểm) |
| **Ngoài mẫu sạch v1.3 (87 ca), số ca dám kết luận trong ngoặc:**<br>- luật 0,011 (1)<br>- 4B 0,138 (12), khoảng tin cậy độ phủ [0,045; 0,314]<br>- 8B 0,115 (10)<br>- 14B 0,115 (10)<br>- 32B 0,253 (22)<br>Mọi mô hình precision 1,0, 0 S sai, 0 C sai | `experiments/AG-1/out/v13/score_heldout.json` | [ĐÃ THỰC NGHIỆM] (bạc) |
| **Hiệu chỉnh sạch v1.3 (n = 383–397, trong mẫu), số ca dám kết luận trong ngoặc:**<br>- luật 0,060 / 0,625 / 9 / 0 (24)<br>- 4B 0,243 / 0,989 / 1 / 0 (93)<br>- 8B 0,292 / 0,982 / 2 / 0 (112)<br>- 14B 0,347 / 0,970 / 3 / 1 (133)<br>- 32B 0,373 / 0,986 / 2 / 0 (143) | `experiments/AG-1/out/v13/score_calib.json` | [ĐÃ THỰC NGHIỆM] (trong mẫu) |
| Thời gian chạy trên Kaggle:<br>- lượt D: nạp 239 s, sinh 278 s cho 507 câu<br>- lượt E: 8B 509 s, 14B 436 s<br>- lượt F: 1.290 s cho 1.273 câu<br>- lượt G: 4B 312 s, 8B 379 s, 14B 316 s, 32B 579 s<br>Mọi lượt 0 câu không parse được | `docs/RUNS.md` | [ĐÃ THỰC NGHIỆM] |
| GROQ-PROBE: chọn `openai/gpt-oss-120b`, `reasoning_effort` low + `json_object`. Kết quả 12/12 JSON hợp lệ, độ đúng trường 1,0, p50 1,0 s | KE_HOACH 31/10 14:15 | [ĐÃ THỰC NGHIỆM] (n = 12) |

### 3.5 AG-2 và bộ đọc của sản phẩm

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| Hiệu chỉnh trên 388 ca v1.1, kiểm trên 162 ca G. Ô cuối mỗi dòng là khoảng tin cậy của phần tăng độ phủ so với luật:<br>- Luật: hiệu chỉnh 0,059 / 0,652 / 8 / 0; G 0,006 / 1,0 / 0 / 0.<br>- **Luật + 4B, `union_noloneS`:** hiệu chỉnh 0,242 / 0,989 / 1 / 0 / [0,065; 0,353]; G 0,093 / 1,0 / 0 / 0 / [0,016; 0,185]. | yaml `agentic_ag2_v1.result_2026-10-31_23h50` | [ĐÃ THỰC NGHIỆM] (bạc) |
| Các chính sách trượt cổng:<br>- Luật + 4B `union`: hiệu chỉnh 0,278 / 0,926 / **8** / 0, vì giữ S đơn độc của luật.<br>- Luật + 32B `noloneS`: G 0,228 / 0,973 / **1** / 0, trượt.<br>- Luật + 4 mô hình `noloneS`: hiệu chỉnh 0,459 / 0,961 / 6 / 1; G 0,247 / 0,95 / **2** / 0, trượt.<br>- Luật + 4 mô hình `bucket`: chỉ giữ ca 4/4 đồng ý; G 0,037, cận dưới phần tăng < 0. | yaml, như trên | [ĐÃ THỰC NGHIỆM] |
| Bốn đường đồng ý trên 246 ca: 0,419 / 0,903 / 9 / 1, kém luật (7 và 0), trượt cổng. Chính sách xô OOF quyết 0 ca (81 xô có thể có, chỉ 7 công ty) | yaml `agentic_v1_2.same_cases_new_readers_246` | [ĐÃ THỰC NGHIỆM] |
| Parity (01/11, Kaggle `rehoanzun/gs-ag2-q4-parity`, cùng đường code Ollama + `ir_reader.py`):<br>- Q4_K_M khớp 0,963 (S→N 1, C→N 3, N→S 1, N→C 1).<br>- Q8_0 khớp 0,981. | yaml `agentic_ag2_product.result_2026_11_01` | [ĐÃ THỰC NGHIỆM] |
| Luật + 4B chạy cục bộ, `noloneS`, trên G:<br>- Q4: 0,080 / 1,0 / 0 / 0; khoảng tin cậy phần tăng [0,016; 0,175].<br>- Q8: 0,074 / 1,0 / 0 / 0; [0,011; 0,171].<br>Bộ đọc cục bộ đứng một mình trên 87 ca sạch: Q4 0,149 / 1,0; Q8 0,138 / 1,0 | như trên | [ĐÃ THỰC NGHIỆM] (bạc) |
| Thời gian đọc: 1,7 s/câu trên GPU T4. **Không phải** thời gian trên laptop. Ollama cần 3,3 GiB, laptop chỉ còn trống 2,6 GiB (01/11) | yaml; KE_HOACH 01/11 | [ĐÃ THỰC NGHIỆM] |

### 3.6 AG-3: bảng PDF

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| Trang 39 của HPG SR 2025: dựng đủ 10 hàng dữ liệu. Cộng dọc khớp 3/3: phạm vi 1 + 2 bằng tổng (lệch 1); 5 mảng bằng tổng (lệch 1); tỷ trọng cộng lại 100 % | AG-3 README mục 5 | [ĐÃ THỰC NGHIỆM] (1 trang) |
| Trên 7 ca (N01–N06, N08), cùng bộ đọc Groq gpt-oss-120b và cùng `verdict` v1.2:<br>- trang thô: đúng 1/7, 0 ca dám kết luận;<br>- hàng dựng lại: đúng 3/7, 2 ca dám kết luận (N04 S, N08 S, cả hai đúng), 0 SUPPORTED sai, 0 CONTRADICTED sai.<br>Tổng 18 lời gọi Groq | AG-3 README mục 5 | [ĐÃ THỰC NGHIỆM] (ca dựng, n = 7) |
| `find_tables` của PyMuPDF thất bại: chế độ đường kẻ không thấy bảng; chế độ văn bản gom cả trang thành một bảng 89 × 17 | AG-3 README mục 3 | [ĐÃ THỰC NGHIỆM] |
| Mâu thuẫn nội bộ trong báo cáo HPG: tiêu đề trang 39 ghi "KIỂM KÊ … NĂM 2024", còn bảng ghi năm 2025 | AG-3 README mục 6 | [ĐÃ THỰC NGHIỆM] |

### 3.7 Nhãn Claude (T1) và nhãn người

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| T1 v3 (13/10): 1.217 câu, 15 công ty, kiểm định chéo theo công ty, 3 seed. e5-base đạt macro-F1 0,726 (paper làm tròn 0,73 [0,69; 0,76]); theo seed 0,719 / 0,717 / 0,706; accuracy 0,80; κ 0,66; F1 nhị phân "là tuyên bố" 0,82 [0,79; 0,85] | `training/runs/kaggle_t1_v3/results.json` (kiểm 04/11); paper mục 6.1 | [ĐÃ THỰC NGHIỆM] (nhãn Claude) |
| Mốc so sánh: luật 0,36 [0,33; 0,38]; zero-shot mDeBERTa 0,27 [0,24; 0,30]; đoán lớp đông nhất 0,19. Hiệu số e5 so với luật: +0,37 [0,33; 0,41]. Từ v2 sang v3 trên 498 câu: +0,061 [0,021; 0,098] | paper mục 6.1 | [ĐÃ THỰC NGHIỆM] (nhãn Claude) |
| Theo lớp: QUANT 0,74, QUAL 0,71, VAGUE 0,57 (luật có F1 = 0 ở lớp VAGUE). Theo ngôn ngữ: tiếng Việt 0,75 (n = 845), tiếng Anh 0,68 (n = 372) | paper | [ĐÃ THỰC NGHIỆM] (nhãn Claude) |
| Ablation che số: +0,014 [−0,02; +0,04]; thêm câu kề: −0,012 [−0,06; +0,02]. Cả hai không kết luận được | paper; `report_v3.json` | [ĐÃ THỰC NGHIỆM] |
| Nhãn Claude: 2 lượt mù có κ 0,92, trọng tài 170 câu. κ cao chỉ cho biết thầy **nhất quán**, không cho biết thầy **đúng** | paper mục 5.2, mục 7 | [ĐÃ THỰC NGHIỆM] |
| Bộ trích bằng luật so với nhãn Claude: P 0,54 / R 0,70 | AUDIT mục 3 | [ĐÃ THỰC NGHIỆM] (nhãn Claude) |
| Chi phí suy luận: 118,7 ms/câu trên CPU (batch 1, 4 luồng), 278 triệu tham số. mDeBERTa fine-tune sụp về toàn NOT_CLAIM sau 18 lần thử; e5-large hết bộ nhớ trên T4 | `results.json` timings; paper mục 6.1 | [ĐÃ THỰC NGHIỆM] |
| **Nhãn người:** 0/88 cặp trong `data/gold/sessions/` và 0/79 câu trong cả ba gói T1 (kiểm 31/10). Kế hoạch: 79 câu + 40 cặp trước 04/11 | KE_HOACH mục 0, mục 9 | [ĐÃ THỰC NGHIỆM] (tình trạng 04/11: [CHƯA XÁC MINH]) |
| Ngưỡng được nói số với hội đồng: ≥ 60 hàng gold và κ ≥ 0,70 (D-2026-09-22-05; yaml `gates`) | yaml dòng 21–24 | [ĐÃ THỰC NGHIỆM] (quy tắc) |

### 3.8 Lỗi đã đo F1–F7 và cách sửa (trạng thái 01/11, kiểm mã 04/11)

| # | Lỗi · số đo | Gốc rễ | Đã làm | Kết quả | Còn mở |
|---|---|---|---|---|---|
| F1 | Kết luận phẳng: HPG 153/156 PARTIAL, hàng đợi 9/172 | 100 % bằng chứng nội bộ (F6) và luật phủ thấp (F2) | `priority-v1.1` (06/10) xếp thứ tự; AG-2 hai đường **chỉ** làm huy hiệu và thứ tự hàng đợi | Hàng đợi 9 mục, người soát thấy đúng khoảng 6/9 (n nhỏ); hai đường đạt 0,093 so với 0,006 trên G, 0 sai | Verdict sản phẩm **không đổi** trước Chung kết (D-2026-10-16-01, quyết định 31/10); cần nguồn độc lập |
| F2 | Luật phủ thấp: B-a 8/32 và 3/19 dám kết luận; B-b 2,8 % (v1), 6,0 % (v1.1), 0,6 % (G), 1,1 % (sạch 87) | Luật đọc câu thật kém; bằng chứng đã đúng câu mà vẫn trượt | AG-1: LLM điền IR, `irlib` tính, `ground`, C-guard | Ngoài mẫu sạch: 4B 13,8 %, 32B 25,3 %, 0 sai; trần oracle 52,8 % | Câu bằng chứng nhiều số (39/246 ca); nối vào sản phẩm |
| F3 | Bảng dàn phẳng: mọi mô hình ≥ 26B báo S sai ở N02/N05 | PyMuPDF trả ô bảng thành đoạn rời | Che số L1 (S sai về 0); AG-3 v0 dựng hàng từ toạ độ + cộng dọc | 10 hàng, cộng dọc 3/3; 1/7 → 3/7; 0 S sai; N02/N05 vẫn N | IR v1.3 thêm `segment`; gắn nhãn hàng tổng từ kết quả cộng dọc; lớp bảng cho GS-Bench |
| F4 | Lỗi chuẩn hoá Q1–Q5 (10/10):<br>- Q1 cường độ so với tuyệt đối (F11);<br>- Q2 mẹ so với hợp nhất (F20);<br>- Q3 ngưỡng 0,35 che chênh 9–25 %;<br>- Q4 bộ trích bỏ sót "sử dụng … nước" (13/51 ca);<br>- Q5 không cộng tổng của tuyên bố (F26, F27) | Comparator thiếu chiều; luật trích dựa vào động từ | Đường IR: `comparable` có loại giá trị, ranh giới, kỳ, năm gốc; dung sai theo độ chính xác công bố, không có vùng 0,35 | Trong đường IR, Q1/Q2/Q3 bị chặn theo thiết kế | Verifier sản phẩm vẫn dùng 0,35 (`configs/default.yaml`). Không thấy bẫy F11/F20 trong `tests/` (grep 04/11), nên chưa xác minh đã sửa trong sản phẩm. Q4 cần T1 (chưa nối). Q5: cộng dọc của AG-3 chưa nối vào phép kiểm tuyên bố |
| F5 | Pháp lý: 0 quy tắc áp được trên 156/156 tuyên bố | Gói luật chỉ có 1 quy tắc nháp, chưa ai duyệt | Sửa registry: ngày hiệu lực, nhãn NĐ 83/2026 (06/10) | Vẫn 0 quy tắc | Thảo duyệt 3–5 quy tắc có `reviewed_by` ([CHƯA XÁC MINH] tiến độ) |
| F6 | Bằng chứng chỉ nội bộ (780/780) | Chưa có nguồn ngoài | Lập danh sách nguồn P0: Climate TRACE, GEM thép, GEM xi măng, QĐ 13/2024, quan trắc tự động | Chưa tích hợp | Đưa vào với vai trò `evidence` hoặc `external` |
| F7 | Không có gold người (0/88 cặp, 0/79 câu) | Phụ thuộc người gán | GS-Bench làm thước đo tạm; kế hoạch B-d (≤ 167 mục) | 0 tới 31/10 | Chỉ người làm được |

Lỗi trước F1–F7 (22/09, N1–N5) đã đóng bằng các bất biến:
- Đóng bằng bất biến 4: 7/8 mâu thuẫn sai, 5/8 trong số đó là so khác chiều.
- Đóng bằng N4 (SUPPORTED cần ≥ 2 thuộc tính): SUPPORTED chỉ nhờ 1 cue.
- Đóng bằng trần MEDIUM (D-2026-09-22-03): 65 HIGH + 1 CRITICAL trên doanh nghiệp đối chứng.

### 3.9 Dự đoán đăng ký trước: đúng hay sai

| Khối (thời điểm) | Dự đoán | Kết quả | Đúng/Sai |
|---|---|---|---|
| `agentic_v1` (31/10, trước khi có đầu ra) | 4B: độ phủ B-b ≥ 0,35, precision ≥ 0,90, C sai ≤ 2, B-a sạch ≥ 26/32 | 0,134; 1,0; 0; 17/32 | **Sai** (độ phủ, B-a); precision và C sai thì đạt |
| | 1.7B kém 4B ít nhất 0,10 độ phủ | Lượt đầu 1.7B 0,183 **cao hơn** 4B 0,134 | **Sai**. Chỉ đúng **sau** `ground` trong mẫu (0,25); ngoài mẫu lượt D chênh 0,089 < 0,10 |
| | 0.6B không dùng được (độ phủ < 0,15 hoặc precision < 0,80) | 0,127 / 0,39 | Đúng |
| | 8B / 14B / gemma trong khoảng ±0,05 của 4B | 0,232 / 0,254 so với 0,134; gemma sinh rỗng | **Sai** |
| `agentic_v1_1` (31/10, trước khi mô hình đọc 260 ca mới) | 4B ngoài mẫu: precision ≥ 0,90, cận dưới khoảng tin cậy ≥ 0,80, C sai ≤ 2 | 0,903; 0,81; 2 | Đúng, sát nút |
| | 4B độ phủ ≥ 0,30 | 0,126 | **Sai** |
| | 32B precision ≥ 0,90 và C sai ≤ 2 | 0,951; 2 | Đúng |
| | Chấm không `ground` có nhiều C sai hơn, với mọi mô hình ≥ 4B | 3→2, 12→1, 7→3, 3→2 | Đúng |
| | 8B/14B/32B trong khoảng ±0,07 độ phủ của 4B | 0,126 / 0,220 / 0,256 / 0,329 | **Sai** |
| | Cổng `ag1_ir_path_usable` (C sai ≤ luật + 1 = 1) | Chỉ 8B qua; 4B, 14B, 32B trượt | (cổng) trượt |
| `agentic_v1_2` (sau lượt D; sửa đổi 22:50 trước khi đọc tập mới) | 4B C sai ≤ 1 và precision ≥ 0,90 trên tập ngoài mẫu kế tiếp | 0; 1,0 (15 ca) | Đúng |
| | 4B độ phủ < 0,25 trên doanh nghiệp mới | 0,093 | Đúng |
| | 8B và 14B C sai ≤ 1 | 0; 0 | Đúng |
| `agentic_ag2_v1` (31/10 23:40) | Luật + 4B `noloneS` trên G: 0 C sai, 0 S sai, độ phủ ≥ 0,09, cận dưới phần tăng > 0 | 0; 0; 0,093; 0,016 | Đúng |
| | Luật + 4B `bucket`: độ phủ ≤ `noloneS`, 0 C sai | 0,093 = 0,093; 0 | Đúng |
| | Luật + 4 mô hình `noloneS`: độ phủ ≥ 0,15, C sai ≤ 1 | 0,247; 0 (nhưng 2 S sai nên trượt cổng) | Đúng |
| `agentic_ag2_product` (01/11 14:40) | Parity ≥ 0,95 | 0,963 | Đúng |
| | Luật + 4B cục bộ: 0 C sai, 0 S sai, độ phủ ≥ 0,06 | 0; 0; 0,080 | Đúng |
| `agentic_ag3_v0` (01/11 17:30) | N02 và N05 thành C | Cả hai vẫn N | **Sai** |
| | Đúng ≥ 5/7 ca trang 39 | 3/7 | **Sai** |
| | 0 SUPPORTED sai | 0 | Đúng |
| | Trang thô có ≥ 1 SUPPORTED sai | 0 (trên trang thô bộ đọc không kết luận ca nào) | **Sai** |
| Kế hoạch 31/10 (không phải yaml) | AG-1: 4B độ phủ ≥ 2 lần luật, kết luận sai ≤ luật | v1: 4,8 lần, đạt; lượt D: 1,6 lần và 2 C sai so với 0, không đạt; G và tập sạch: đạt | Lẫn lộn |
| | AG-2: cùng precision, độ phủ tăng từ khoảng 25 % lên ≥ 50 % | Hiệu chỉnh 0,242; G 0,093 | **Không đạt** (mốc 25 % lấy từ B-a, không phải B-b) |
| | AG-3: kiểm tổng chặn ≥ 80 % bảng dựng sai; N02/N05 hết S sai | S sai = 0 trên 7 ca; tỷ lệ chặn chưa đo (mới 1 bảng) | Một phần |
| D-2026-09-28-01 | Đo trên lô 1 ngày 02/10 để quyết tháo chốt | Không có gold | **Chưa làm** |
| measurement-decisions-v1 (29/09) | Các cổng gold: κ, `lift_guard_*`, dense, reranker | Gold = 0 | **Chưa đo được** |

**Cách nói:** "Từ 31/10 đến 01/11, đội đăng ký trước 21 dự đoán: 13 đúng, 8 sai. Đội công bố cả 8 dự đoán sai, và một lần tự sửa báo cáo (22:40)."
- Đếm theo các dòng yaml ở bảng trên. Không tính dòng cổng, các dòng của kế hoạch và hai dòng "chưa làm/chưa đo".
- Nếu đếm dự đoán 1.7B là đúng (sau `ground`) thì thành 14/7. **Nên nói "phần lớn đúng; 8 dự đoán sai đã công bố"** để tránh bị bắt lỗi đếm.

### 3.10 Cái gì chạy trong sản phẩm, cái gì là thí nghiệm, cái gì trên giấy (04/11)

| Thành phần | Trạng thái | Căn cứ |
|---|---|---|
| Pipeline 10 bước, `offline` mặc định, 0 kết nối, giấy làm việc tiếng Việt, quyết định soát ghi chỉ-thêm, hàng đợi `priority-v1.1`, 8 cổng | **Sản phẩm, đang chạy** (G3 luôn đạt; "bất thường" chưa tính) | HE_THONG; D-2026-10-06-01/02/03 |
| Đọc PDF, OCR tại máy, bảng thành khối TABLE; DOCX/HTML/URL; cảnh báo trang scan (14/10) | Sản phẩm; OCR cần tesseract trên máy demo ([CHƯA XÁC MINH] đã cài) | AUDIT mục 2 |
| Trích tuyên bố bằng luật + regex | Sản phẩm | HE_THONG |
| Truy xuất `lite`: BM25 0,55 + n-gram 0,45, RRF, lấy 30 giữ 5, `floor_k` 3 | Sản phẩm, mặc định | `configs/default.yaml` (`embedding: lite`, `reranker: none`) |
| Embedding BGE-M3 hoặc FPT, reranker bge-reranker-v2-m3 | **Có adapter, mặc định tắt, chưa đo** | D-2026-09-22-04 |
| Verifier số học → cụm từ → xu hướng → tương đồng; 5 verdict; chốt LLM | Sản phẩm (`llm_stance: "off"` trong YAML; bật qua `.env`) | `configs/default.yaml` |
| LLM đọc cặp khó (GLM-5.2 qua FPT, chế độ `cloud`) | Mã có, nhưng **khoá FPT trả lỗi 401 từ 31/10**, nên hiện không chạy. Mục Groq đã có trong cấu hình và gắn nhãn "đám mây" | KE_HOACH 31/10 |
| Registry pháp lý (11–12 văn bản, 3 ngày cho mỗi văn bản) + gói luật | Sản phẩm, nhưng 0 quy tắc áp được | AUDIT mục 7 |
| Rubric 9 thành phần + trần MEDIUM | Sản phẩm | `configs/scoring_v1.yaml` |
| GreenScan Studio, đề xuất sửa theo luật, rào không bịa số, DOCX tracked changes | Sản phẩm (14/10); LLM leo thang mặc định không gọi | AUDIT mục 10 |
| `irlib` v1.2 và `ir_reader.py` (`QUANTUM_VERIFY=dual`) | **Mã nằm trong `src/`, có 12 + 4 test, nhưng không module nào gọi tới** (grep 04/11: `ir_reader` và `QUANTUM_VERIFY` không xuất hiện ngoài chính file) | grep `src/` 04/11 |
| Học trò T1 e5-base | Đã huấn luyện trên Kaggle, **chưa nối** | AUDIT mục 3 |
| AG-0, AG-1 (lượt A–G), AG-2, parity Q4, AG-3 v0, GROQ-PROBE, size ladder, che số L1, nhận diện lại | **Thí nghiệm** | mục 3.2–3.6 |
| Cổng 06/11 | Phần thống kê đạt trên G (C sai và S sai không vượt luật; cận dưới phần tăng > 0). **Còn thiếu:** bẫy và test bất biến khi bật dual; thời gian HPG ≤ 2× trên laptop | yaml `agentic_ag2_product.remaining_gate_parts` |
| QUBO chọn bằng chứng, AG-4 QLoRA, AG-5 truy xuất có số đo, AG-6 agent nhiều bước, chế độ `cloud_masked`, L2, sổ gửi đi, nguồn độc lập, quy tắc pháp lý có người duyệt, thử nghiệm người dùng (SUS, thời gian) | **Trên giấy** | brief mục 7.2; KE_HOACH mục 5; OFFLINE mục 6; AUDIT mục 13 |

### 3.11 Kiểm thử, cấu hình, chi phí

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| Số test tại các mốc: 206 (9/2026) → 351 (paper) → 359 (10/10) → 385 test xanh (14/10) | brief; paper mục 6.5; HE_THONG mục 6; AUDIT | [ĐÃ THỰC NGHIỆM] (số mới nhất 04/11: [CHƯA XÁC MINH], chưa chạy pytest) |
| Đếm hàm test ngày 04/11: `test_verdict_traps.py` 47, `test_audit_checklist.py` 17, `test_architecture_invariants.py` 15, `test_irlib_ground.py` 12, `test_ir_reader.py` 4 | grep `tests/` 04/11 | [ĐÃ THỰC NGHIỆM] |
| Cấu hình mặc định: dung sai số trần 0,10; mâu thuẫn từ 0,35; điểm hỗ trợ 0,22 (một phần) và 0,46 (mạnh); SUPPORTED chỉ nhờ cue cần ≥ 2 thuộc tính | `configs/default.yaml` | [ĐÃ THỰC NGHIỆM] |
| Giá GLM-5.2 trên FPT: US$1,40 / 4,40 mỗi 1 triệu token (đầu vào / đầu ra), ngữ cảnh 1 triệu; danh mục FPT không ghi vùng xử lý | MO_HINH mục 7 (kiểm 10/10) | [NGOÀI] |
| Trần API đám mây do người dùng đặt: US$5. Kaggle ước 25–40 giờ GPU T4 cho AG (kế hoạch) | KE_HOACH mục 0, mục 9 | [ĐÃ THỰC NGHIỆM] (kế hoạch) |
| Giả thuyết giá trị: báo cáo 200–300 trang cần 8–12 giờ đọc tay, mục tiêu 30 phút sàng lọc + khoảng 2 giờ rà | brief mục "Giả thuyết giá trị" | [GIẢ THUYẾT] |

### 3.12 Số ngoài được dẫn trong cụm R2 (chỉ nói kèm nguồn; R khác nên kiểm lại bản gốc)

| Dữ kiện | Nguồn trong repo | Nhãn |
|---|---|---|
| Tỷ lệ công ty HOSE có báo cáo PTBV: 1,06 % (2015) → 28,38 % (2024); 72,5 % định tính; 2/22 báo cáo có đảm bảo bên thứ ba (Hąbek & Bui 2025, 673 công ty) | paper mục 1.1 | [NGOÀI] |
| 50,6 % quan sát công bố KNK theo TT 96 đạt 0 %; chỉ 21,3 % đầy đủ (Lâm Thị Trúc Linh và cs. 2025, 399 quan sát) | paper mục 1.1 | [NGOÀI] |
| Tín dụng xanh khoảng 750 nghìn tỷ đồng (30/11/2025), khoảng 5 % dư nợ. Brief dùng số cũ hơn: 704.244 tỷ, 4,3 % (31/3/2025) | paper; brief | [NGOÀI] |
| Stammbach ACL 2023: SVM n-gram F1 70,9 so với RoBERTa-large 84,9 | MO_HINH mục 1 | [NGOÀI] |
| MiniCheck 770M đạt 74,7, ngang GPT-4 75,3. LLM-AggreFact: Llama-405B 74,4 < 70B 75,1; Llama-3.2-1B 50,3 | MO_HINH mục 1 | [NGOÀI] |
| Aarnes & Setty 2026 (arXiv:2610.00689): Qwen3-0,6B tinh chỉnh 88,44, 8B tinh chỉnh 97,67, so với GPT-5.4 Pro 73,96 | MO_HINH mục 3 | [NGOÀI] |
| PAL 72,0 so với PaLM-540B 56,9; PoT GPT-4 trên FinQA 58,2 → 74,0; NumPert: mất 56–61 điểm khi số bị che | MO_HINH mục 1 | [NGOÀI] |
| Joren ICLR 2025: khi ngữ cảnh không đủ, Gemini 1.5 Pro trả lời sai 40,4 %, Claude 3.5 Sonnet 36,5 % | MO_HINH mục 1 | [NGOÀI] |
| Kiểm chéo hai nguồn trong text-to-SQL cho AUROC 0,82, so với 0,61–0,68 của tự nhất quán | KE_HOACH mục 3; PQ-01 (nguồn thứ cấp: tài liệu ZAIC) | [NGOÀI] ([CHƯA XÁC MINH] bản gốc) |

---

## 4. Câu hỏi BGK dự kiến (20 câu)

Mỗi câu trả lời đi theo khung: vấn đề → nguyên lý → GreenScan làm gì → giới hạn.

**Q1. "Độ chính xác của hệ thống là bao nhiêu phần trăm?"**
- **Trả lời:**
  - Vấn đề: một con số gộp che hai lỗi có giá rất khác nhau: vu oan doanh nghiệp và bỏ lọt tuyên bố. Hơn nữa, đội chưa có nhãn người.
  - Nguyên lý: trong kiểm toán, đo precision trên phần dám kết luận, đi kèm độ phủ, và đếm riêng hai loại lỗi (bất biến 8).
  - GreenScan: trên 87 ca ngoài mẫu đã làm sạch (tuyên bố sinh từ câu thật của 7 doanh nghiệp, nhãn bạc), đường "mô hình đọc, code tính" dám kết luận 11–25 % số ca và không kết luận sai ca nào. Luật thuần chỉ dám kết luận 1 ca.
  - Giới hạn: mỗi mô hình chỉ có 10–22 ca dám kết luận. Quy tắc đội tự đặt: dưới 60 nhãn người và κ dưới 0,70 thì không công bố "độ chính xác".
- **Vặn:** "0 lỗi là hoàn hảo à?" → Không. 0 lỗi trên 12 ca (4B) chỉ cho cận dưới khoảng 0,74 (Clopper–Pearson 95 %). Tỷ lệ lỗi thật có thể tới khoảng 25 %.
- **Bẫy:** nói "98 %" hay "100 %"; đưa khoảng tin cậy [1,0; 1,0] ra làm bằng chứng.

**Q2. "Nhãn do Claude gán thì có phải AI tự chấm AI không?"**
- **Trả lời:**
  - Vấn đề: nếu cùng một AI vừa gán nhãn vừa được chấm thì phép đo là vòng tròn.
  - Nguyên lý: đáp án theo cấu trúc. Lấy số liệu thật, làm nhiễu có kiểm soát, nên biết đáp án trước khi hệ chạy.
  - GreenScan: Claude, hoặc Qwen3-32B, chỉ đọc số liệu của câu bằng chứng thật, rồi bộ kiểm tất định soát lại. Nhãn S/C/N do họ nhiễu quyết: đổi bội số thì phải C, đổi kỳ thì phải N. Đội công bố cả lỗi nhãn: 16/455 ca ở v1.1, và 75/162 ca tập ngoài mẫu v1.2 phải loại khi hậu kiểm. Nhãn Claude không bao giờ được dùng để cho LLM tự quyết (D-2026-10-16-01).
  - Giới hạn: đây vẫn là nhãn bạc, người chưa duyệt.
- **Vặn:** "Sao không thuê người gán?" → Đã có kế hoạch 79 câu + 40 cặp; tới 31/10 có 0 nhãn. Đội nói thẳng, không lấy nhãn Claude thay vào.
- **Bẫy:** gọi nhãn Claude là "gold" hay "nhãn tham chiếu"; giấu chuyện 75/162 ca hỏng.

**Q3. "Hệ thống chỉ kết luận 10–25 % số ca. Vậy được việc gì?"**
- **Trả lời:**
  - Vấn đề: báo cáo Việt Nam phần lớn định tính (72,5 %); HPG có 152/156 tuyên bố thiếu năm gốc. Vì vậy kết quả trung thực phổ biến nhất là "chưa đủ bằng chứng".
  - Nguyên lý: dự đoán có chọn lọc, tức đánh đổi độ phủ lấy độ đúng. Kết luận sai về một doanh nghiệp đắt hơn chuyển hồ sơ cho người.
  - GreenScan: phần không kết luận thành hàng đợi có lý do. Trên HPG, 9/172 mục được đưa lên trước, mỗi mục ghi thiếu thuộc tính nào. Studio biến danh sách thiếu sót thành 391 đề xuất sửa, có rào không bịa số.
  - Giới hạn: chưa đo thời gian tiết kiệm hay SUS; "8–12 giờ còn khoảng 2,5 giờ" là giả thuyết.
- **Vặn:** "Người vẫn phải đọc 86 % còn lại?" → Đúng, nhưng đã được khoanh và xếp thứ tự, không phải dò từng trang. Luật hiện chỉ dám kết luận 1 %.
- **Bẫy:** hứa tiết kiệm X % thời gian.

**Q4. "Sao không để LLM lớn tự kết luận, hoặc dùng multi-agent?"**
- **Trả lời:**
  - Vấn đề: LLM đọc tốt nhưng mắc kiểu sai nguy hiểm.
  - Nguyên lý: hệ thống ghép. Tách "đọc" khỏi "tính", giao phép tính cho code (PAL, PoT).
  - GreenScan đã đo ba lần:
    - mọi mô hình 26B–753B đều xác nhận sai trên bảng dàn phẳng (N02, N05), còn luật thì không;
    - GLM-5.2 tự quyết trên HPG sinh 10 kết luận "mâu thuẫn", phần lớn sai, và 2 CRITICAL trên doanh nghiệp đối chứng; khi có chốt thì 0;
    - thêm 32B vào hai đường làm tăng SUPPORTED sai trên tập G (1 so với 0).
  - Vì vậy kiến trúc là một orchestrator 10 bước cố định, không có đa tác tử tự trị (bất biến 5, quy tắc "không thêm agent cho trông AI hơn").
  - Giới hạn: độ phủ còn thấp.
- **Vặn:** "Vậy LLM làm gì?" → Đọc câu thành IR. Nhờ vậy, trên ca ngoài mẫu sạch, hệ kết luận được gấp 10–20 lần luật mà không sai.
- **Bẫy:** nói "LLM không biết tính". Trên ca sạch các mô hình tính đúng; chúng chỉ dễ vỡ khi số bị nhiễu hoặc bảng mất cấu trúc.

**Q5. "Mô hình 4B có quá bé không? Sao không dùng 32B?"**
- **Trả lời:**
  - Vấn đề: cần chọn cỡ mô hình theo bước, không theo cảm giác.
  - Số đo ngoài mẫu 246 ca: độ phủ của 4B / 8B / 14B / 32B là 0,126 / 0,220 / 0,256 / 0,329, nên có hiệu ứng kích thước ở độ phủ. Precision sau `ground` đều ≥ 0,90. Trên 87 ca sạch, cả bốn mô hình 0 sai.
  - Đội chọn 4B vì hai lý do: chạy được cục bộ (bản Q4 cần 3,3 GiB RAM, khớp bản gốc 96,3 %), và "luật + 4B" là cấu hình duy nhất qua phần thống kê của cổng trên G (32B có 1 SUPPORTED sai).
  - Hiện chế độ offline không chạy LLM; chế độ cloud dùng GLM-5.2 (753B tổng).
  - Giới hạn: chưa đo tốc độ trên laptop; trên T4 là 1,7 s/câu.
- **Vặn:** "Dự đoán 'không có hiệu ứng kích thước' của các em sai?" → Đúng, sai ngoài mẫu. Trong mẫu, chính `ground` che mất hiệu ứng; ra ngoài mẫu, mô hình lớn đọc câu nhiều số tốt hơn. Đội đã ghi đó là dự đoán sai.
- **Bẫy:** dẫn "0,408–0,465 trong mẫu" như bằng chứng không có hiệu ứng kích thước; nói chế độ cloud đang chạy (khoá FPT lỗi 401 từ 31/10).

**Q6. "LLM có bịa số hay tính sai không?"**
- **Trả lời:**
  - Vấn đề: hai rủi ro khác nhau, bịa và tính sai, cùng dẫn tới vu oan.
  - Nguyên lý: bất biến 5, số học là của code.
  - GreenScan:
    - `ground` buộc mỗi con số, bội số và năm phải có nguyên văn trong câu;
    - `irlib` so với dung sai bằng độ chính xác đã công bố, và in ra phép tính;
    - lỗi thật đã gặp: cả 11 kết luận sai của 32B là bội số tự thêm ("10.730 m3" thành "10.730 ngàn m3"); sửa bằng code;
    - ngoài mẫu, `ground` giảm vu oan ở mọi mô hình; v1.2 thêm C-guard; tập G và tập sạch 0 vu oan.
  - Giới hạn: vẫn có thể nhầm chỉ số hoặc kỳ, OCR sai chữ số, và bảng.
- **Vặn:** "Doanh nghiệp tự viết sai số thì sao?" → Cần nguồn độc lập. AG-3 đã bắt được một mâu thuẫn nội bộ trong báo cáo HPG: tiêu đề ghi 2024, bảng ghi 2025.
- **Bẫy:** nói "mô hình đã kiểm chứng số liệu".

**Q7. "Trên Hòa Phát gần như mọi tuyên bố 'khớp một phần'. Hệ thống phân biệt được gì?"**
- **Trả lời:**
  - Vấn đề F1: 153/156 PARTIAL vì 780/780 bằng chứng là tài liệu của chính doanh nghiệp, và luật phủ thấp.
  - Nguyên lý: kiểm chứng cần nguồn độc lập. Không tìm thấy không có nghĩa là sai.
  - GreenScan: giá trị hiện nằm ở hàng đợi 9/172 mục và danh sách thuộc tính thiếu. Hướng sửa:
    - nguồn ngoài: Climate TRACE, GEM, QĐ 13;
    - huy hiệu "hai đường khớp / lệch" để sắp hàng đợi; verdict không đổi.
  - Giới hạn: kết quả đầu–cuối trên HPG sẽ không đổi trước Chung kết; đây là quyết định có chủ đích.
- **Vặn:** "Demo cho thấy gì?" → Tuyên bố → bằng chứng có trang → phép tính hoặc lý do không so được → đề xuất sửa.
- **Bẫy:** nói "phát hiện HPG tẩy xanh"; trình bày con số phẳng như thành tích.

**Q8. "Hệ thống áp được điều luật nào?"**
- **Trả lời:**
  - Vấn đề: liên quan về chủ đề chưa có nghĩa là áp dụng được.
  - Nguyên lý: bất biến 7 (ngày hiệu lực → ngành → chủ thể → loại tuyên bố → điều kiện).
  - GreenScan:
    - registry có 11–12 văn bản đã đối chiếu bản ký, có ngày hiệu lực và chuỗi sửa đổi;
    - gói luật chỉ có 1 quy tắc nháp, chưa ai duyệt, nên 0/156 tuyên bố có quy tắc áp dụng;
    - bài học NĐ 83/2026: trước 06/10 bị gắn nhãn phát thải và trích kèm 55 tuyên bố; đã sửa.
  - Giới hạn: quy tắc thật cần người có chuyên môn duyệt.
- **Vặn:** "Trích sai luật thì ai chịu?" → Hệ chỉ gợi ý căn cứ, có nhãn trạng thái xác minh; người soát quyết.
- **Bẫy:** nói hệ "kết luận vi phạm pháp luật".

**Q9. "Bảng trong PDF xử lý thế nào?"**
- **Trả lời:**
  - Vấn đề F3: bảng bị dàn phẳng làm mọi mô hình xác nhận sai.
  - Nguyên lý: biểu diễn đầu vào quyết định chất lượng; dựng cấu trúc trước rồi mới hỏi; tự kiểm bằng cộng dọc.
  - GreenScan (AG-3 v0): dựng hàng bảng từ toạ độ chữ. Trang 39 HPG cho đủ 10 hàng, cộng dọc khớp 3/3. Trên 7 ca: đúng 3/7 so với 1/7 của trang thô, không xác nhận sai ca nào.
  - Giới hạn: N02/N05 vẫn chưa ra C vì IR thiếu chiều "mảng kinh doanh". Mới thử 1 trang và 7 ca, bằng bộ đọc đám mây.
- **Vặn:** "Sao không dùng Docling hay Table Transformer?" → Cần GPU. `find_tables` thất bại (bảng không có đường kẻ, hoặc gom cả trang thành 89 × 17), nên đội thử cách toạ độ trước.
- **Bẫy:** nói "đã xử lý bảng".

**Q10. "Tài liệu của doanh nghiệp có rời máy không?"**
- **Trả lời:**
  - Chế độ mặc định `offline` có 0 kết nối; đã kiểm bằng cách chặn mạng khi phân tích 264 trang.
  - Chế độ đám mây chỉ dùng cho tài liệu công khai (loại A).
  - Thí nghiệm che số: không lọt số hay tên nào, xác nhận sai về 0. Nhưng mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang, nên che số **không bảo vệ danh tính**.
  - Hướng đi là bộ đọc 4B chạy hoàn toàn tại máy: bản Q4 khớp bản gốc 96,3 %.
  - Giới hạn: chế độ `gpu` còn dự phòng sang FPT (ghi 10/10; đã sửa chưa: [CHƯA XÁC MINH]); chưa có sổ gửi đi.
- **Vặn:** "Groq miễn phí có lưu dữ liệu?" → Có thể, nên chỉ dùng cho báo cáo công khai.
- **Bẫy:** nói "ngoại tuyến một phần là an toàn tuyệt đối".

**Q11. "Làm sao biết các em không chỉnh ngưỡng sau khi thấy kết quả?"**
- **Trả lời:**
  - Nguyên lý: đăng ký trước để chống chọn số sau khi nhìn.
  - GreenScan:
    - `configs/measurement_decisions.yaml` ghi thời điểm đăng ký, dự đoán, điều kiện bác bỏ; sửa đổi ghi trước khi thấy đầu ra;
    - đội báo cả dự đoán sai: độ phủ của 4B (dự đoán ≥ 0,35, thực tế 0,134; dự đoán ≥ 0,30, thực tế 0,126), "không hiệu ứng kích thước" (sai hai lần), AG-3 (dự đoán ≥ 5/7, thực tế 3/7);
    - tự sửa báo cáo lúc 22:40: 4B, 14B, 32B trượt cổng dù vẫn khớp dự đoán.
  - Giới hạn: file nằm trong repo của đội, không có dấu thời gian của bên thứ ba ([CHƯA XÁC MINH] có git commit tương ứng không; thư mục làm việc hiện không phải git repo).
- **Vặn:** "Sửa rồi đo lại trên chính các ca đó là overfit." → Đúng, nên mọi bản sửa (`ground`, v1.2) đều được kiểm trên một tập ngoài mẫu mới.
- **Bẫy:** nói "chưa từng sửa đăng ký". Có sửa lúc 14:40 và 22:50, nhưng đều trước khi thấy đầu ra.

**Q12. "Chi phí, tốc độ và phần cứng khi triển khai?"**
- **Trả lời:**
  - Báo cáo HPG 264 trang chạy 107–121 s, RAM đỉnh 1,33 GB, laptop i7 không GPU (luật thuần).
  - Học trò T1: 119 ms/câu trên CPU (chưa nối).
  - Bộ đọc 4B: cần khoảng 3,3 GiB RAM; trên T4 là 1,7 s/câu.
  - GLM-5.2 qua FPT có giá US$1,40 / 4,40 mỗi 1 triệu token.
  - Giới hạn: thời gian HPG khi bật hai đường chưa đo; cổng yêu cầu ≤ 2 lần thời gian hiện tại.
- **Vặn:** "Máy 8 GB chạy được không?" → Luật thuần chạy được. Bộ đọc 4B thì chưa chắc: ngày 01/11 laptop 16 GB còn trống 2,6 GiB nên Ollama từ chối.
- **Bẫy:** lấy 1,7 s × số câu rồi nói như thời gian trên laptop.

**Q13. "Phần lượng tử nằm ở đâu?"**
- **Trả lời:**
  - Đội hình thức hoá bài toán chọn tập bằng chứng nhỏ nhất mà đủ thành QUBO: thưởng độ liên quan, phạt trùng lặp, thưởng phủ đủ 5 thuộc tính, ép đúng k đoạn. Dạng này ánh xạ được sang Ising, giải bằng tôi luyện mô phỏng hoặc QAOA trên trình mô phỏng.
  - Benchmark dự kiến so với top-k, MMR và nghiệm chính xác.
  - Hiện **chưa có mã**; đội không tuyên bố lợi thế lượng tử.
  - Thứ tự ưu tiên: lỗi đã đo nằm ở khâu đọc câu và bảng, không ở khâu chọn bằng chứng. Thể lệ cũng ưu tiên mô hình đơn giản chạy ổn định.
- **Vặn:** "Vậy dự thi AI-Quantum để làm gì?" → AI giải bài toán thật; lượng tử là một bài toán con đã đặt rõ, sẽ đo so với cách cổ điển và báo cả kết quả âm.
- **Bẫy:** nói "đã chạy QAOA" hay "lượng tử tăng độ chính xác".

**Q14. "Học trò T1 đạt 0,73 nghĩa là gì? Đã dùng trong sản phẩm chưa?"**
- **Trả lời:**
  - 0,73 là macro-F1 đồng thuận với **nhãn Claude**, trên 1.217 câu của 15 công ty, kiểm định chéo theo công ty, 3 seed (0,706–0,719 từng seed). So với luật 0,36 và zero-shot 0,27.
  - Mô hình e5-base 278 triệu tham số, 119 ms/câu trên CPU.
  - Mục đích: thay bộ trích từ khoá vì bộ này bỏ sót tuyên bố (lỗi Q4).
  - Giới hạn: chưa so với nhãn người; chưa nối vào sản phẩm.
- **Vặn:** "κ 0,92 của Claude chứng minh nhãn đúng?" → Không; κ cao chỉ cho thấy Claude nhất quán.
- **Bẫy:** nói "T1 chính xác 73 %".

**Q15. "Sao bootstrap theo công ty mà không theo câu? Sao không có một F1 gộp?"**
- **Trả lời:**
  - Câu của cùng một báo cáo không độc lập: cùng văn phong, cùng KPI. Bootstrap theo câu sẽ cho khoảng tin cậy hẹp giả.
  - Train và test luôn khác công ty để tránh rò từ vựng.
  - Bốn số không gộp. Ví dụ luật trên 402 ca: precision 0,625, 0 vu oan nhưng 9 bỏ lọt. Một câu "đúng 192/402" sẽ che cả hai.
  - Giới hạn: chỉ có 7 công ty nên khoảng tin cậy rộng. Chính sách xô (81 xô / 7 công ty) không quyết được ca nào.
- **Bẫy:** đưa accuracy tổng.

**Q16. "Nếu hệ nói 'mâu thuẫn' sai, doanh nghiệp bị oan, ai chịu trách nhiệm?"**
- **Trả lời:**
  - Thiết kế chặn từ gốc: kiểm tuyên bố, không phán doanh nghiệp (bất biến 1); lệch một chiều thì cấm C (bất biến 4); LLM không tự tạo C; mọi kết luận có phép tính và trích dẫn.
  - Đã đo:
    - HPG sau audit 25/09: 0 vu oan (trước đó 17/09: 357/419; 22/09: 7/8);
    - đường IR trên tập G và tập sạch: 0.
  - Người soát là người ký; quyết định ghi chỉ-thêm.
  - Giới hạn: "0 vu oan" là trên tập hữu hạn và nhãn bạc.
- **Bẫy:** nói "không bao giờ vu oan".

**Q17. "Áp cho doanh nghiệp hay ngành chưa thấy thì sao?"**
- **Trả lời:**
  - GS-Bench có 7 công ty (bvh, dhg, tra, vnm, ctd, pnj, pow), phần lớn ngành phát thải thấp. Tập ngoài mẫu thêm dpr và cng.
  - Trên doanh nghiệp mới, độ phủ của 4B tụt: 0,437 trong mẫu → 0,126 ngoài mẫu. Precision giữ được nhờ cấu trúc `irlib`.
  - T1 kiểm định chéo theo công ty: 0,71–0,73 (nhãn Claude).
  - Giới hạn: B-b chưa có thép hay xi măng, chưa có lớp bảng.
- **Bẫy:** khẳng định "tổng quát tốt".

**Q18. "Truy xuất bằng chứng có đúng không? Recall bao nhiêu?"**
- **Trả lời:**
  - Chưa đo được recall vì gold trống.
  - Cấu hình mặc định là `lite`: BM25 0,55 + n-gram 0,45, RRF, lấy 30 giữ 5, luôn giữ 3 ứng viên yếu nhất có cờ (bài học vụ KLM: phán quyết không chia sẻ từ nào với tuyên bố nó bác bỏ).
  - BGE-M3 và reranker có adapter nhưng tắt. Điều kiện bật đã đăng ký trước: Recall@5 tăng ≥ 10 điểm và thời gian ≤ 2 lần.
  - Thí nghiệm AG đưa sẵn bằng chứng đúng câu, nên chỉ đo khâu đọc.
- **Bẫy:** nói "hybrid RAG + reranker" ở thì hiện tại (D-2026-09-22-04).

**Q19. "Hai đường cụ thể là gì? Đã có trong sản phẩm chưa?"**
- **Trả lời:**
  - Đường 1 là luật; đường 2 là 4B đọc IR rồi `irlib` tính. Hai đường đồng ý thì giữ; S do luật nói một mình thì bỏ; còn lại chuyển người.
  - Kết quả trên G: độ phủ 9,3 % so với 0,6 %, 0 sai.
  - Trạng thái: mã `ir_reader.py` đã nằm trong `src/` và có test, nhưng **chưa nối vào pipeline**. Cổng 06/11 còn thiếu bẫy, test bất biến và thời gian chạy trên laptop.
  - Nếu không qua cổng thì trình bày đúng là "nghiên cứu, chưa đưa vào sản phẩm". Kể cả khi qua, nó chỉ là trợ giúp người soát; verdict không đổi.
- **Bẫy:** nói "đã có trong sản phẩm".

**Q20. "Ở vòng 1 các em cam kết F1 ≥ 0,75, Recall@10 ≥ 0,85, verdict ≥ 0,80. Đạt chưa?"**
- **Trả lời:**
  - Chưa đo được trên nhãn người, và đội nói thẳng điều đó.
  - Đã đạt: sai số học bằng 0 trên bộ bẫy; 4/4 ca thật có phán quyết; 0 kết nối ở chế độ offline.
  - Trong lúc chờ gold, đội chuyển sang thước đo có đáp án theo cấu trúc (GS-Bench) với ngưỡng đăng ký trước, và báo cả kết quả âm.
  - Giới hạn: muốn có con số chính thức thì phải có người gán.
- **Bẫy:** lấy số trên nhãn Claude để thay cho số cam kết.

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

### 5.1 Mâu thuẫn giữa các tài liệu (thống nhất trước khi lên slide)

| # | Mâu thuẫn | Nên nói |
|---|---|---|
| 1 | **Số bẫy:** paper, kế hoạch 31/10, PQ-01 và AUDIT mục 6 ghi "17 bẫy xanh trong `test_verdict_traps.py`". HE_THONG, MO_HINH, AUDIT mục 4 và file thật (04/11) có 47 test trong file đó, cộng 17 ca checklist ở `test_audit_checklist.py`. D-2026-09-22-05 ghi 21 trap | "47 bẫy kết luận + 17 ca checklist kiểm toán + 15 test bất biến (đếm 04/11)". Phải làm rõ "17 bẫy xanh" trong cổng 06/11 nghĩa là gì |
| 2 | **Test bất biến:** tài liệu ghi 14, file hiện có 15 hàm. Tổng test: 206 → 351 → 359 → 385 | Nói con số kèm ngày đo; số hiện tại [CHƯA XÁC MINH], cần chạy pytest |
| 3 | **Dung sai:** brief ghi "dung sai tương đối 12 %". Hiện tại: ½ chữ số cuối, trần 10 %, 0,35 thì bác bỏ (verifier); `irlib` không có vùng 0,35 | Không nói 12 %. Nếu bị hỏi, giải thích hai chính sách: verifier sản phẩm và đường IR |
| 4 | **Rubric:** brief, HE_THONG và mã: 9 thành phần (`risk-rubric-v2`). Paper mục 4.3: "7 tiêu chí C1–C7" | Nói 9 thành phần có trần, tổng 100 |
| 5 | **Registry pháp lý:** brief và AUDIT ghi 11 văn bản, 938 điều khoản; paper ghi 12 văn bản | Nói "11–12 văn bản" kèm nguồn, hoặc kiểm lại registry trước 10/11 |
| 6 | **Bộ mô hình:** brief ghi "Qwen3-8B chính, BGE-M3, reranker; local vLLM/Ollama mặc định". Thực tế: `offline` không có LLM; embedding `lite`; reranker `none`; cloud là GLM-5.2 qua FPT (đang lỗi 401). AUDIT mục 5 ghi "Hybrid BM25 + dense (FPT cloud)" cũng không khớp cấu hình mặc định | Theo D-2026-09-22-04: "kiến trúc hỗ trợ hybrid; cấu hình hiện tại là BM25 + n-gram + RRF" |
| 7 | **Nhãn người:** paper mục 6.1 ghi "trên 79 câu lô 1 so với người: +0,053 [−0,06; +0,16]"; brief ghi "5 claim đã adjudicate"; D-2026-09-22-05 ghi "gold 5 cặp". Kế hoạch 31/10 kiểm: 0/79 câu, 0/88 cặp | Không dẫn +0,053 hay "5 cặp". Nói "0 nhãn người (kiểm 31/10)" |
| 8 | **Abstract của paper** gọi 1.217 câu là "nhãn tham chiếu" | Nói "nhãn Claude" |
| 9 | **PQ-01** ghi "357/419 về 0 trong bộ dựng ngày 22/09". Nhưng D-2026-09-22-01 ghi HPG 22/09 còn 7/8 C sai; số 0 có sau audit 25/09 | "Về 0 sau khi thêm bất biến 4 và audit 25/09" |
| 10 | Kế hoạch F2 ghi "luật quyết định 8/32 (đúng 6)"; paper ghi "luật đúng 20/32" | Cả hai đúng. 20/32 tính cả ca N đúng; nói rõ |
| 11 | Bảng che số ghi xác nhận sai của gemma-26B khi không che là 2; paper ghi 1 (chỉ trang thật) | Có thể 2 là tổng sạch + trang thật [CHƯA XÁC MINH]; chỉ nói "→ 0 khi che" |
| 12 | Kế hoạch ghi "4 tài khoản Kaggle dành riêng"; RUNS ghi 5 tài khoản. Mục 0 ghi "Sáu thí nghiệm AG-0…AG-6" (thực ra là 7) | Lỗi nhỏ, không đưa lên slide |
| 13 | **Tín dụng xanh:** paper ghi khoảng 750 nghìn tỷ, khoảng 5 % (30/11/2025); brief ghi 704.244 tỷ, 4,3 % (31/3/2025). QĐ 13/2024: 2.166 cơ sở (brief); QĐ 42/2026: 2.441 cơ sở (paper) | Dùng số mới, ghi rõ ngày |
| 14 | **PQ-01** ghi "sản phẩm chỉ dùng đường luật + 4B sau cờ `QUANTUM_VERIFY=dual`" | Cờ chưa nối vào pipeline (grep 04/11); nói "sẽ đặt sau cờ nếu qua cổng" |
| 15 | **Quyết định 31/10** (phương án (b), trần US$5, Kaggle thay API trả phí) không có trong DECISIONS_LOG | Chép vào log trước Chung kết |

### 5.2 Số đã cũ so với kết quả 31/10–01/11

| Câu hoặc số cũ | Ở đâu | Thay bằng |
|---|---|---|
| "4B qua cổng an toàn sát nút" (14:35) | Kế hoạch 31/10 14:35; AG-1 README | **Trượt** cổng `ag1_ir_path_usable` (2 > 1); chỉ 8B qua (sửa lúc 22:40) |
| "Dự đoán không có hiệu ứng kích thước đã thành đúng" (14:10, trong mẫu) | AG-1 README; PQ-02 mục 5 | Ngoài mẫu **sai**: 0,126 / 0,220 / 0,256 / 0,329 |
| "4B mất độ phủ vì đọc sai năm bằng chứng" | AG-1 README 23:25; kế hoạch | **Đã rút lại** (01/11): đó là lỗi tập (năm lấy từ tiêu đề trang) |
| "AG-3 chưa chạy"; "Đã xử lý bảng PDF" là điều cấm | PQ-02 mục 3.7 và 6 | AG-3 v0 đã chạy 01/11: 3/7, 0 S sai. Vẫn **không** được nói "đã xử lý bảng" |
| "Bộ đọc Q4 chưa đo được (thiếu RAM)" | PQ-02 mục 3.7 | Parity đo trên Kaggle: 0,963. Thời gian trên laptop vẫn chưa đo |
| Ô "[CHỜ]" ngoài mẫu AG-1 | PQ-06 mục 4 | Điền kết quả lượt D–G và tập sạch v1.3 |
| "Tỷ lệ lỗi nhãn 16/455 (3,5 %)" như tỷ lệ chung | PQ-06 mục 3.2 | Đúng cho v1.1. Tập ngoài mẫu v1.2 có 75/162 ca hỏng (46 %), nên nhãn bạc phải có người soát |
| Điều kiện mở AG-4 ("1.7B kém 4B ≥ 10 điểm đã thoả") | AG-1 README mục 5 | Chỉ thoả trong mẫu sau `ground` (0,25). Lượt đầu 1.7B cao hơn 4B; ngoài mẫu lượt D chênh 0,089 |
| Độ phủ "11–25 %" (PQ-01) | PQ-01 | Đúng với tập sạch 87 ca; ghi kèm n = 10–22 ca dám kết luận |
| Số trong paper và brief (T1, size ladder, A/B, hàng đợi) | paper, brief | Vẫn đúng với ngày đo, nhưng chưa phản ánh AG (GS-Bench, IR, hai đường) |

### 5.3 Điều không được nói
- "Độ chính xác X %", "đúng 98 %", "100 %", "không bao giờ sai", "không bao giờ vu oan".
- "Đã kiểm trên dữ liệu thật". Câu nguồn là thật, nhưng tuyên bố trong B-b là câu sinh.
- "Nhãn Claude là gold" hoặc "nhãn tham chiếu". Không lấy số trên nhãn Claude thay cho cam kết trên nhãn người.
- Khoảng tin cậy "[1,0; 1,0]" như bằng chứng an toàn.
- "Hybrid RAG + BGE-M3 + reranker" ở thì hiện tại.
- "Đường hai đường, bộ đọc IR hoặc `QUANTUM_VERIFY=dual` đã có trong sản phẩm"; "T1 đã chạy trong sản phẩm".
- "Đã xử lý bảng PDF"; "đã có nguồn độc lập".
- "GreenScan phát hiện tẩy xanh" hay "doanh nghiệp X tẩy xanh"; "hệ thống kết luận vi phạm pháp luật".
- "Không có hiệu ứng kích thước mô hình" (chỉ đúng trong mẫu); "luật chính xác hơn mô hình" (chỉ đúng khi luật đã dám kết luận); "LLM không làm được số học".
- "Lượng tử đã chạy" hoặc "có lợi thế lượng tử"; "QUBO cải thiện kết quả".
- "Tiết kiệm Y % thời gian kiểm toán" (giả thuyết, chưa đo).
- "Dung sai 12 %".
- "Chế độ cloud GLM-5.2 đang chạy" (khoá FPT lỗi 401 từ 31/10; [CHƯA XÁC MINH] đã gia hạn chưa).
- "Ngoại tuyến một phần bảo vệ danh tính doanh nghiệp".
- "Đạt các ngưỡng cam kết Vòng 1" (F1 ≥ 0,75, Recall@10 ≥ 0,85, verdict ≥ 0,80): chưa đo trên nhãn người.
- "AG-4 (QLoRA), AG-5 (truy xuất), AG-6 (agent nhiều bước) đã làm".
