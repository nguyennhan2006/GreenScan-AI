# Báo cáo kiểm thử tính năng cốt lõi — 2026-09-20

**Phạm vi:** toàn bộ đường chạy mặc định (heuristic, không LLM, không key) trên máy dev Windows · **Người chạy:** Nhân (với Claude) · **Commit gốc:** working tree sau `582bedf` (chưa commit — xem A1 trong `ISSUES_REGISTER_2026-09.md`)
**Tệp test mới:** `tests/test_verdict_traps.py` (12 test: 7 xfail-strict + 5 guard) · `tests/test_document_store_ids.py` (2 test: 1 xfail-strict + 1 pass)

> Mọi số trong báo cáo này là **số đo**, không phải số dự kiến. Các lỗi được pin bằng `xfail(strict=True)` nên khi sửa xong test sẽ tự báo đỏ để gỡ marker — đây là cơ chế chống quên.

## 0. Trạng thái sửa — cập nhật cùng ngày 2026-09-20 (phiên 2)

**Tất cả D1–D8 đã sửa**, cộng 8 lỗi phát hiện thêm trong lúc sửa (kể cả claim tự xác nhận bằng trang khác của chính báo cáo — ADR 0004/B5, và cue ủng hộ "phù hợp với/chứng nhận" bắt câu về màu sắc sản phẩm). Không còn `xfail`; `tests/test_verdict_traps.py` = **21 bẫy xanh**, toàn bộ suite **233 passed**.

| Số đo | Trước (sáng 20/09) | Sau (chiều 20/09) | Nghiệm thu (ISSUES_REGISTER) |
| --- | --- | --- | --- |
| Hòa Phát BCPTBV 2025 + BCTN 2024: số claim | 419 | **210** | ≤ 80 — *chưa đạt* (45% có số/cam kết, mục tiêu 70%) |
| Hòa Phát: CONTRADICTED | 357 (85%) | **9 (4%)** | ≤ 15% ✅ |
| Hòa Phát: SUPPORTED chỉ khi có nguồn ngoài tài liệu tuyên bố | 3 (đều tự khớp cùng trang) | **7** (BCTN xác nhận kiểm kê KNK/BSI) · 192 PARTIAL | ADR 0004 ✅ |
| Hòa Phát: heading/mục lục bị loại | 0 | 389 (caps_run 271, generic 80, section 20, short 17, toc 1) | ghi `rejected` trong audit ✅ |
| Demo `data/sample` (5 claim) | 6/6 CONTRADICTED | UNSUPPORTED 2 · CONTRADICTED 2 · PARTIAL 1 | ≥ 4 verdict khác nhau — *3/4* |
| Golden 4 case | 4/4 | 4/4 | giữ ✅ |
| Real cases (`run_case.py --all`) | 4/4 MATCH, stance 2/2, band 2/4 | 4/4 MATCH, stance 2/2, band 2/4 | giữ ✅ |
| Bẫy verdict | 6/11 | 19/19 | ≥ 18/20 ✅ |

Cơ chế đã thay (chi tiết trong `CHANGELOG.md` mục Unreleased):
`parse_numbers` bỏ nhãn (phạm vi/Scope/ISO/Điều/số mục/số trang/số có 0 đầu), định dạng số Việt, hệ số, đơn vị chuẩn; `normalize_for_match` fold `đ→d`; so số **cùng đơn vị + cùng câu có metric + cùng Scope**; overlap trên `content_tokens` **giữ dấu** (sử dụng ≠ đúng, tới ≠ tôi); cue **khớp nguyên từ trên chữ có dấu**, phải cùng câu với token chủ đề (nguồn thẩm quyền: hoặc là phán quyết về "tuyên bố/statements"), lọc `benign`, cue ủng hộ bị phủ định không tính, bỏ "không có/chưa có" trần; xu hướng ngược không số liệu → PARTIAL + cần người xem (không phải CONTRADICTED), "giảm thiểu/tăng cường" không phải xu hướng; claim mơ hồ / cam kết không số không được PARTIAL nhờ tương đồng; extractor loại heading/TOC/ALL-CAPS/chuỗi caps/generic không cam kết; chunk ≤ 3 câu trong một đoạn; `doc_id` tệp text khớp store; **SUPPORTED cần đoạn từ tài liệu khác tài liệu tuyên bố** (cùng tài liệu → PARTIAL); cue ủng hộ phải cùng câu chia sẻ một từ (bigram âm tiết) với chính claim, bỏ "phù hợp với"/"kiểm toán".

Còn mở (không chặn demo): số claim HPG 210 > 80 và tỷ lệ có số 45% < 70% — cần chuẩn hoá claim bằng LLM (S2.1) hoặc siết `include_vague_claims`; B10 `corpus_completeness` chưa có nên UNSUPPORTED vẫn xuất hiện khi corpus nhỏ; B9 `comparison_policy` mới có phần (đơn vị/metric/scope/tolerance ghi ra `numeric_check`), chưa có tolerance theo độ chính xác công bố; B7 legal rule pack vẫn 100% INSUFFICIENT.

---

## 1. Kết quả tổng

| Hạng mục | Kết quả | Ghi chú |
| --- | --- | --- |
| `pytest tests/` (bộ có sẵn) | **206 passed** | ~2 phút, không flaky |
| `pytest tests/test_verdict_traps.py tests/test_document_store_ids.py` | **6 passed · 8 xfail** | 8 lỗi đã pin, không lỗi mới ngoài dự kiến |
| `quantum-agent demo` | chạy, 6 claim / **6 CONTRADICTED** | lỗi B5 còn nguyên (demo kém thuyết phục) |
| `quantum-agent evaluate` (golden 4 case) | recall 1.0 · status acc 1.0 · citation 1.0 · gate 1.0 | **không bắt được lỗi nào bên dưới** (B8) |
| `quantum-agent evaluate-real` (4 case adjudicated) | 4/4 status MATCH · risk band 2/4 | như đã ghi (B6) |
| API smoke qua `TestClient` (13 lời gọi) | đúng 12/13 | 1 lỗi: `doc_id` txt → 404 |
| Review workflow (7 chuyển trạng thái) | **7/7 đúng**, kể cả các lỗi 400 mong đợi | phần vững nhất của hệ thống |
| PDF deep-link (meta → render PNG → highlight) | đúng; 1 rect định vị; trang 999 → 404 | KLM-2024 packet, 0.5 s |
| Frontend `npm run build` / `oxlint` | build OK (237 kB JS) · 6 warning, 0 error | F5 |
| Hiệu năng | tài liệu 400 câu trùng: 0.2 s, dedupe về 2 claim | không có vấn đề hiệu năng ở quy mô text |

---

## 2. Lỗi tìm được (xếp theo mức ảnh hưởng verdict)

Ký hiệu: 🔴 đổi verdict sai hướng nguy hiểm (false SUPPORTED/CONTRADICTED) · 🟠 verdict yếu/nhiễu · 🟡 UX/liên kết

### D1 🔴 **MỚI** — Nhãn phạm vi "phạm vi 1 và 2" / "Scope 1" bị đọc là số đo

- **Tái hiện:** claim *"…phạm vi 1 và 2 giảm 30% so với năm 2020"* vs evidence *"…phạm vi 1 và 2 năm 2024 giảm 8%…"* → **SUPPORTED**, lý do `"Số liệu khớp: 1.0 ≈ 1.0"`. Mâu thuẫn 30% vs 8% bị che hoàn toàn.
- **Root cause:** `utils/text.parse_numbers` trả `[(2024,None),(1,None),(2,None),(30,'%'),(2020,None)]`; `verifier._measurements` chỉ lọc năm 1900–2100. `_numeric_relation` chọn cặp sai số nhỏ nhất → cặp `1≈1` thắng cặp `30 vs 8`.
- **Hậu quả:** mọi claim có "Scope 1/2/3", "phạm vi 1, 2", "ISO 14064-1", "category 11", "Tier 2" đều có sẵn một cặp số khớp giả → **false SUPPORTED có hệ thống** trên đúng loại claim quan trọng nhất (KNK). Case tiếng Anh trong probe cũng SUPPORTED vì `Scope 1 ≈ Scope 1`, không phải vì 25% ≈ 25%.
- **Hướng sửa:** (a) `parse_numbers` bỏ số đứng ngay sau token phạm vi/tiêu chuẩn (`phạm vi|scope|tier|category|iso|category|mục|điều|khoản|phụ lục|bảng|hình`) và số không có đơn vị ≤ 3 chữ số đứng cạnh chữ; (b) `_numeric_relation` chỉ so cặp **có đơn vị tương thích và cùng metric bucket** (đúng tinh thần B9 `comparison_policy`); (c) khi có nhiều cặp, ưu tiên cặp có đơn vị `%`/đơn vị vật lý hơn cặp không đơn vị. Test: `test_scope_labels_are_not_measurements`.

### D2 🔴 B1 — Cue "thiếu" trùng "thiêu kết"; "không có" bắt "không có sự cố" (còn nguyên)

- **Tái hiện:** *"Nhà máy thép áp dụng công nghệ thiêu kết mới giúp giảm phát thải…"* → **CONTRADICTED** `qualitative_cue "thieu"`. *"Năm 2024 không có sự cố môi trường…"* → **CONTRADICTED** `"khong co"`.
- **Root cause:** `stance_cues.yaml` ghi rõ *"Matching is substring-based over accent-folded text"*; `normalize_for_match("thiếu") == normalize_for_match("thiêu") == "thieu"`.
- **Hướng sửa (như B1):** match theo **ranh giới từ trên chuỗi có dấu** (regex `\b` với NFC), cue phải cùng câu với term metric/scope của claim, whitelist phủ định tích cực (`không có sự cố|tai nạn|vi phạm|phát sinh`). Test: `test_sintering_is_not_a_refutation`, `test_no_incident_is_not_a_refutation`. Số đo nghiệm thu: HPG CONTRADICTED ≤ 15%.

### D3 🟠 B2 — Heading/mục lục thành claim (còn nguyên)

- **Tái hiện:** `"XANH HOÁ SẢN XUẤT\n4.1 | PHÁT THẢI KHÍ NHÀ KÍNH\n…"` → 3 claim; `"4.1 | …"` còn bị **CONTRADICTED** vì `4.1` so với `1.000`.
- **Hướng sửa:** lọc trong `claim_extractor.run`: ALL-CAPS ratio > 0.7, mẫu `^\d+(\.\d+)*\s*[|.\-–]`, < 6 từ, không có động từ/số/cam kết; `generic_sustainability` chỉ giữ khi có vague term hoặc số hoặc future term; ghi `rejected_reason` để UI hiện "Câu bị loại". Test: `test_headings_are_not_claims`.

### D4 🟠 B9 — Định dạng số Việt: `1.200.000` → không có số; `1,2 triệu` → 1.2 không hệ số

- **Tái hiện:** claim *"1,2 triệu tấn CO2e"* vs evidence *"1.200.000 tấn CO2e"* → PARTIALLY_SUPPORTED thay vì SUPPORTED. `parse_numbers("1.200.000 tấn")` = `[]`.
- **Hướng sửa:** normalize theo locale trước khi parse: `(\d{1,3})(\.\d{3})+` → bỏ dấu chấm; `\d+,\d+` → dấu thập phân; hệ số `nghìn|ngàn|triệu|tỷ|k|m|bn`; bắt đơn vị `tấn CO2e|tCO2e|tCO₂tđ|kWh|MWh|m3|m³|%`. Đây là điều kiện tiên quyết của `comparison_policy`. Test: `test_vietnamese_thousand_separators_and_multipliers`.

### D5 🟠 Ranh giới Scope 1+2 vs Scope 1+2+3 không phân biệt

- **Tái hiện:** *"Scope 1 và 2 giảm 10%"* vs *"Scope 1, 2 và 3 giảm 10%"* → SUPPORTED.
- **Hướng sửa:** trích `scope` thành tập `{1,2}` / `{1,2,3}`; khác tập → tối đa PARTIALLY_SUPPORTED với lý do "khác ranh giới phát thải" (B9 mục e). Test: `test_scope_boundary_mismatch_is_not_supported`.

### D6 🟠 Ngưỡng PARTIAL quá thấp: đoạn không liên quan vẫn "ủng hộ một phần"

- **Tái hiện:** *"lắp điện mặt trời áp mái năm 2024"* vs *"Năm 2023 khởi công nhà máy mới"* → PARTIALLY_SUPPORTED (score 0.25, overlap ≥ 0.18 nhờ các token "năm", "công ty").
- **Hướng sửa:** loại stopword tiếng Việt khỏi `_metric_overlap` (`năm, công ty, tập đoàn, của, và, trong, so với`); yêu cầu ít nhất một token metric/scope trùng mới cho PARTIAL; dưới đó → INSUFFICIENT. Test: `test_unrelated_passage_is_insufficient`.

### D7 🟡 **MỚI** — `doc_id` của tệp text tải lên không khớp `DocumentStore` → deep-link 404

- **Tái hiện:** upload `ev.txt` qua `/v1/analyze/files`, lấy `evidence[0].doc_id` → `GET /v1/documents/{doc_id}` **404**; với PDF thì 200.
- **Root cause:** `parsers/documents.py:108` `_chunks_from_text` dùng `stable_id(display_name, text[:500])`; `storage/documents.py:74` dùng `stable_id(resolved_path, name)`; chỉ `_parse_pdf` (dòng 43) khớp công thức của store.
- **Hướng sửa:** trong `parse()` khi có `document.path`, luôn dùng `stable_id(str(path.resolve()), display_name)` cho mọi loại tệp; giữ công thức theo text chỉ cho inline text. Sửa 2 dòng. Test: `test_text_upload_doc_id_matches_store`.

### D8 🟡 B5 — Demo mẫu 6/6 CONTRADICTED

- Vẫn đúng như đã ghi: claim_source tự mâu thuẫn với BCTC cùng công ty qua cue/direction. Đây là hệ quả của D2 + thiếu quy tắc "chỉ nguồn nội bộ → tối đa PARTIAL/INSUFFICIENT" (ADR 0004). Sau khi sửa D1/D2 phải chạy lại demo và cập nhật `data/sample`.

### D9 🟡 Legal layer 100% INSUFFICIENT_EVIDENCE, `conditions` rỗng (B7)

- Xác nhận lại trên KLM PDF: 8/8 inconclusive. Layer chạy đúng về mặt kỹ thuật (chọn văn bản theo hiệu lực, ghi `blocked_sources`) nhưng chưa có rule kiểm được. UI vì thế phải thiết kế thành "bối cảnh pháp lý", không phải "phán quyết" (đã ghi trong spec UI §F5).

### Ghi nhận không phải lỗi

- Review workflow: đúng toàn bộ máy trạng thái (CONFIRM lần hai bị chặn, OVERRIDE bắt buộc `reviewer_status`, REOPEN về HUMAN_REVIEWED, reviewer rỗng → 400, decision lạ → 400 kèm danh sách hợp lệ).
- Prompt injection: đoạn có chỉ thị bị loại, claim về INSUFFICIENT với warning — đúng.
- Cross-metric (50% tái tạo vs 12% phát thải): PASS **nhưng vì may** — 50 khớp 50 trước khi 50 so 12. Nếu evidence chỉ có "12%" thì sẽ CONTRADICTED. Phải sửa cùng D1 (so theo metric bucket).
- Gate G0–G7: hợp lý; G7 báo đúng "inconclusive" thay vì FAIL.

---

## 3. Vì sao golden set không bắt được — và cách đo lại

Golden 4 case + 4 real case đều pass với cả 8 lỗi. Nguyên nhân: các case đó không chứa nhãn phạm vi, không có "thiêu kết", không có heading, số đều là `%` đơn giản. **Bộ trap 12 câu mới là lưới đầu tiên.** Đề xuất mở rộng theo B8:

| Nhóm bẫy | Số câu cần | Đã có |
| --- | --- | --- |
| Đồng âm sau bỏ dấu (thiếu/thiêu, không có/không có sự cố, giảm/giám…) | 5 | 2 |
| Heading/TOC/tiêu đề bảng/chú thích hình | 4 | 1 |
| Số không phải số đo (scope, ISO, điều khoản, số trang, năm) | 4 | 1 |
| Định dạng số Việt + hệ số + đơn vị | 4 | 1 |
| Ranh giới (Scope, công ty mẹ/hợp nhất, một nhà máy/toàn tập đoàn) | 3 | 1 |
| Kỳ (2023 vs 2024, FY vs CY, target vs actual) | 3 | 0 |
| Cường độ vs tuyệt đối (tCO2e/tấn thép vs tCO2e) | 2 | 0 |
| Guard: hành vi đúng phải giữ | 5 | 5 |

Mục tiêu B8: ≥ 20 trap, nghiệm thu ≥ 18/20 sau Sprint 1.

---

## 4. Thứ tự sửa đề xuất (theo tác động / công sức)

1. **D7** (2 dòng, 30 phút) — mở khoá deep-link cho demo tệp text.
2. **D1 + D4** (cùng `utils/text.py`, ~½ ngày) — chặn false SUPPORTED, mở đường `comparison_policy`.
3. **D2** (`stance.py` + `stance_cues.yaml`, ~1 ngày) — số đo HPG CONTRADICTED.
4. **D3** (`claim_extractor.py`, ~½ ngày) — giảm claim rác, demo sạch.
5. **D5 + D6** (`verifier.py`, ~½ ngày).
6. Chạy lại: `pytest`, `demo`, `evaluate`, `evaluate-real`, `data/real_cases/scripts/run_case.py --all`, HPG run; gỡ từng `xfail`; snapshot `benchmark/baseline_<date>.json` (F3).

Tất cả đều nằm trong "Truth layer" tuần 21–27/09 của `EXECUTION_PLAN_2026-09.md`. Không mở tính năng mới trước khi xong 1–5.

---

## 5. Hướng nghiên cứu thêm (để bạn đọc và quyết, không phải để code ngay)

Mỗi mục: **câu hỏi → vì sao quan trọng với GreenScan → đọc gì / đo gì → quyết định cần ra**.

### R1. Numeric comparison policy thay cho dung sai 12% toàn cục (B9)
- **Câu hỏi:** Khi nào hai con số "khớp"? Theo độ chính xác công bố, theo đơn vị, theo metric, theo ranh giới.
- **Đọc:** GHG Protocol *Corporate Standard* ch. 7 (base year recalculation, significance threshold thường 5%); ISO 14064-1:2018 §9 (materiality); IFRS S2 §29 (đo lường & so sánh), TT 96/2020/TT-BTC mẫu báo cáo KNK; cách các fact-checker số (ClaimBuster, *FEVEROUS* numeric cells) định nghĩa "numerically consistent".
- **Đo:** trên gold hiện có, phân phối `relative_error` của các cặp reviewer gán SUPPORTED vs CONTRADICTED → chọn ngưỡng theo dữ liệu, ghi vào `configs/numeric_policy.yaml` với `policy_id`.
- **Quyết:** tolerance theo số chữ số có nghĩa (khuyên) hay theo ngành.

### R2. Định nghĩa vận hành UNSUPPORTED vs INSUFFICIENT_EVIDENCE (B10, ADR 0005)
- **Đọc:** *FEVER* (NotEnoughInfo), *SciFact* (NEI), *AVeriTeC* (Conflicting/Cherry-picking) — cách họ tách "không có thông tin" khỏi "bị bác"; tài liệu kiểm toán ISA 500 về "sufficient appropriate evidence" và ISA 705 về scope limitation.
- **Đo:** cùng một claim với 2 corpus (đủ / thiếu BCPTBV) phải ra 2 verdict khác nhau → test.
- **Quyết:** `corpus_completeness` do intake suy ra (có BCPTBV + BCTN cùng kỳ + bảng KNK?) hay do người dùng khai.

### R3. Stance detection tiếng Việt không dựa vào substring bỏ dấu
- **Đọc:** *ViNLI* (Vietnamese NLI), *ViHealthNLI*, PhoBERT/ViDeBERTa fine-tune NLI; *Climate-FEVER*, *ClimateNLI*, *ClimateBERT* cho domain; khảo sát *"Fact-checking with NLI: entailment ≠ verification"*.
- **Đo:** thay `qualitative_stance` bằng NLI cross-encoder (VI) chạy local, so stance accuracy trên 4 real case + trap set + 30 cặp Quỳnh gán → nếu không hơn heuristic đã sửa ≥ 10 điểm thì **không** đưa vào (D3 ablation).
- **Quyết:** NLI local (CPU ~200 ms/cặp) có chấp nhận được với demo không, hay giữ heuristic + LLM `on_ambiguous`.

### R4. Table-cell provenance (E3 / S3.3)
- **Đọc:** *PubTables-1M* / *TableBank* (detection), *TATR*, `pdfplumber` vs `camelot` vs PyMuPDF `find_tables()` trên PDF Việt; *FEVEROUS* & *TabFact* về trích dẫn ô.
- **Đo:** 1 bảng KNK Hòa Phát kiểm tra tay: tỉ lệ ô đúng, thời gian; ghi `confidence`.
- **Quyết:** chỉ cam kết 1 bảng demo (như plan) hay mở rộng.

### R5. Retrieval: RRF + reranker có đáng bật cho demo không
- **Đọc:** *BGE-M3* paper (dense+sparse+multi-vector), *bge-reranker-v2-m3*; Zhao et al. về RAG có thể tệ hơn (đã trích trong G8); *"Lost in the middle"* cho top-k.
- **Đo:** Recall@5/@10 và verdict accuracy theo k (3/5/10/30→5) trên gold; thời gian/claim trên CPU. Hook đã có trong `retrieval/rerank.py`.
- **Quyết:** k và có/không reranker cho bản 10/10.

### R6. Đo độ tin cậy gán nhãn và cách báo cáo số (S2.4, S4.1)
- **Đọc:** Cohen κ vs Krippendorff α cho 5 nhãn không cân bằng; bootstrap CI cho accuracy trên n = 60; company-held-out split để tránh leakage.
- **Đo:** κ trên 20 cặp thử trước khi gán 60; báo cáo theo từng DN với CI.
- **Quyết:** ngưỡng κ ≥ 0.7 giữ hay báo cáo α kèm κ.

### R7. Legal rule pack có điều kiện kiểm được (B7, S2.5)
- **Đọc:** QĐ 21/2025/QĐ-TTg Phụ lục I (tiêu chí xanh theo ngành), TT 17/2022/TT-BTNMT (đo đạc, kiểm kê KNK), NĐ 06/2022 → 119/2025 → 83/2026 (đối tượng, kỳ hạn báo cáo); cách *OpenFisca* / *Catala* / *Regulation as Code* (NZ) biểu diễn điều kiện có thể kiểm.
- **Đo:** 3 rule đầu (đối tượng phải kiểm kê theo QĐ 13; kỳ báo cáo; phương pháp theo TT 17) chạy được trên fixture → 3 finding ≠ INSUFFICIENT.
- **Quyết:** rule viết bằng YAML điều kiện đơn (khuyên) hay DSL.

### R8. QUBO chọn bằng chứng — chỉ sau 25/10 (A6, G5)
- **Đọc:** *Kochenberger et al. 2014 "The unconstrained binary quadratic programming problem: a survey"*; QAOA (Farhi 2014); D-Wave Ocean `dimod`; MMR (Carbonell & Goldstein 1998) và *facility-location* submodular selection làm baseline classical; công thức đã sửa với biến coverage `y_m`.
- **Đo:** benchmark 4 cột Top-k · Greedy/MMR · ILP · SA/QAOA trên coverage 5 thuộc tính, redundancy, #chunks, runtime.
- **Quyết:** nói gì về quantum nếu SA/QAOA không thắng — kết quả âm vẫn là kết quả.

### R9. UX của "abstain" và phân rã rủi ro cho người không kỹ thuật
- **Đọc:** *Explainable AI for auditors* (ACCA/ICAEW 2023–2025), nghiên cứu về "algorithm aversion" khi hệ thống nói "không biết"; hướng dẫn *ESMA guidelines on funds' names using ESG terms* (cách trình bày không cáo buộc); *SEC climate disclosure rule* (đã tạm dừng) về ngôn ngữ "material".
- **Đo:** test với 3 người (Quỳnh, Thảo, 1 người ngoài) trên mockup S3: họ đọc INSUFFICIENT là gì? họ tìm đoạn trích trong bao lâu?
- **Quyết:** copy cuối cho abstain và có hiện tổng điểm rủi ro ở S3-F hay chỉ 9 thanh.

---

## Phụ lục — Lệnh tái hiện

```bash
.venv/Scripts/python.exe -m pytest tests -q                                   # 206 passed (+6 pass, 8 xfail mới)
.venv/Scripts/python.exe -m pytest tests/test_verdict_traps.py -q -rx         # xem lý do từng xfail
.venv/Scripts/python.exe -m quantum_gw.cli demo
.venv/Scripts/python.exe -m quantum_gw.cli evaluate
.venv/Scripts/python.exe -m quantum_gw.cli evaluate-real
cd frontend && npm run build && npm run lint
```
