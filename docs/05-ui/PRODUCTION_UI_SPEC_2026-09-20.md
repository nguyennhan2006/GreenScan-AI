# GreenScan AI — Đặc tả tính năng Backend → UI production & prototype

**Phiên bản:** 1.0 · **Ngày:** 2026-09-20 · **Trạng thái:** Handoff cho thiết kế hình ảnh → code UI
**Nguồn sự thật:** `src/quantum_gw/api.py`, `domain/models.py`, `agents/*`, `configs/scoring_v1.yaml`, `frontend/src/lib/claims.js` (đọc trực tiếp ngày 2026-09-20, không suy đoán)
**Tài liệu liên quan:** `UI_REVIEW_20260808.md` (vì sao không làm BI dashboard), `UX_FLOW.md`, `EVIDENCE_CARD_SPEC.md`, `HUMAN_REVIEW_SPEC.md`, `docs/02-product/OUTPUT_SPEC.md`, `docs/00-project/EXECUTION_PLAN_2026-09.md` mục 4 (kịch bản demo 7 phút)

---

## 0. Cách dùng tài liệu này

Tài liệu có ba lớp, đọc theo thứ tự:

| Lớp | Mục | Dành cho |
| --- | --- | --- |
| **A. Backend là gì** | §2 Catalog tính năng backend — mỗi tính năng ghi rõ endpoint, trường dữ liệu, trạng thái, và **hệ quả UI bắt buộc** | Người thiết kế phải hiểu dữ liệu thật trước khi vẽ |
| **B. UI phải là gì** | §3 Kiến trúc thông tin · §4 Design system · §5 Đặc tả từng màn hình (wireframe + binding + states) | Người vẽ mockup và người code |
| **C. Sinh ảnh** | §6 Prompt cho AI tạo ảnh (tiếng Anh, có prefix nhất quán + negative prompt) · §7 Checklist nghiệm thu mockup | Đưa thẳng vào Midjourney / Flux / Ideogram / Imagen / GPT-image |

**Quy trình dự kiến:** sinh ảnh theo §6 → chọn hướng → chỉnh theo checklist §7 → gửi lại ảnh + ghi chú để code UI thật (React + Tailwind đã có sẵn khung trong `frontend/`).

Ký hiệu trạng thái tính năng: ✅ đã có và đã test · 🟡 có nhưng còn lỗi đã đo (xem `CORE_FEATURE_TEST_REPORT_2026-09-20.md`) · ⬜ chưa có, đã lên kế hoạch (EXECUTION_PLAN S3.x) — **UI phải có chỗ cho nó nhưng mockup ghi rõ "planned"**.

---

## 1. Nguyên tắc bất biến (P-rules) — mọi mockup vi phạm là loại

Đây là ranh giới sản phẩm đã cam kết trong hồ sơ Vòng 1 và `DECISIONS_LOG.md`. Chúng quyết định UI khác gì với một dashboard ESG thông thường.

| # | Nguyên tắc | Hệ quả thiết kế cụ thể |
| --- | --- | --- |
| **P1 — Đơn vị làm việc là claim** | Mọi màn hình xoay quanh **một tuyên bố**; công ty/tài liệu chỉ là ngữ cảnh | Không có "điểm doanh nghiệp", không bảng xếp hạng, không logo công ty kèm nhãn rủi ro, không biểu đồ "xu hướng rủi ro theo thời gian" |
| **P2 — Bằng chứng trước kết luận** | Không hiển thị verdict/điểm mà không có đường dẫn tới đoạn trích + trang | Mỗi badge trạng thái đứng cạnh danh sách đoạn bằng chứng có trích dẫn `tên tài liệu · tr. N` và nút mở trang gốc |
| **P3 — Abstain là tính năng** | `INSUFFICIENT_EVIDENCE` là kết quả hợp lệ, không phải lỗi | Màu trung tính (không đỏ), kèm câu cố định: *"Đây là kết quả hợp lệ, không phải lỗi — và không có nghĩa doanh nghiệp vi phạm."* |
| **P4 — Không ngôn ngữ cáo buộc** | UI không dùng: *vi phạm, gian lận, sai phạm, lừa dối, "doanh nghiệp này greenwashing"* | Dùng: *evidence gap, cần người xem xét, chưa đủ bằng chứng, mâu thuẫn với nguồn X, case kiểm tra* |
| **P5 — Rủi ro là gợi ý ưu tiên, không phải tiêu đề** | `risk_score` chỉ để sắp thứ tự hàng đợi | Hiển thị bằng chấm màu nhỏ hoặc thanh phân rã 9 thành phần; **không** hiển thị số điểm to trên card hay KPI tile |
| **P6 — Giải thích được** | Mọi phán đoán có `reason`/`method` | Badge lập trường luôn kèm phương pháp (`numeric` / `qualitative_cue` / `direction` / `llm` / `similarity`) và một dòng lý do |
| **P7 — Người quyết định, AI đề xuất** | Trạng thái AI luôn có nhãn "AI đề xuất" cho tới khi người chốt | Pill trạng thái workflow: `AI đề xuất → Đã có người xem → Đã chốt`; kết quả do LLM đề xuất bắt buộc hiện cờ "cần người xác nhận" |
| **P8 — Tái lập được** | Mỗi run có `run_id`, `config_hash`, `input_hashes` | Footer màn kết quả hiện `run_id` + phiên bản rubric + phiên bản schema; nút sao chép |

---

## 2. Catalog tính năng Backend và hệ quả UI

Mỗi mục: **Làm gì → API → Dữ liệu UI cần → Trạng thái → Hệ quả UI**.

### F1. Tiếp nhận tài liệu (Intake) ✅

- **Làm gì:** Nhận văn bản dán hoặc tệp (`.pdf`, PDF scan qua OCR `eng+vie`, `.txt`, `.md`, `.json`, `.csv`, `.yaml`); tách chunk giữ **trang / block / bảng**; lưu tệp vào `DocumentStore` để trích dẫn còn mở được sau request.
- **API:** `POST /v1/analyze/text` body `{documents:[{name,text,role,source_type,language,metadata}]}` · `POST /v1/analyze/files` multipart `files[]` + `roles` + `source_types` (1 giá trị hoặc 1-per-file, sai số lượng → 400).
- **Enum người dùng phải chọn:**
  - `role`: `claim_source` (Nguồn tuyên bố) · `evidence` (Chứng cứ) · `reference` (Tham chiếu)
  - `source_type`: `internal` (Nội bộ) · `financial` (Tài chính) · `environmental` (Môi trường) · `legal` (Pháp lý) · `external` (Bên ngoài) · `standard` (Tiêu chuẩn)
- **Vì sao UI phải hỏi role:** claim chỉ được trích từ `claim_source`; `legal/external/standard` là nguồn **độc lập** — thiếu nó rubric trừ 8 điểm `independent_assurance`. Nếu người dùng gán sai vai trò, kết quả sai một cách im lặng → UI phải làm rõ ý nghĩa mỗi vai trò ngay tại chỗ chọn.
- **Hệ quả UI:** Màn S1 có hai chế độ (dán / tải tệp); mỗi tệp một hàng với 2 select; gợi ý mặc định thông minh (tệp đầu = `claim_source`, các tệp sau = `evidence`); cảnh báo mềm khi **không có nguồn độc lập nào** trước khi chạy; tiến trình chạy hiện 10 bước của `OrchestratorAgent.PLAN`.

### F2. Trích xuất tuyên bố (Claim extraction) 🟡

- **Làm gì:** Heuristic song ngữ VI/EN theo `configs/taxonomy.yaml`; mỗi câu khớp lexicon → một `Claim`.
- **Trường UI dùng (`Claim`):** `text` (nguyên văn), `claim_type`, `source_name`, `source_page`, `source_doc_id`, `metric`, `direction` (`decrease|increase|null`), `values[]`, `units[]`, `period`, `baseline`, `scope`, `is_future_commitment`, `is_vague`, `vague_terms_matched[]`, `language` (`vi|en|unknown`), `confidence`.
- **Lỗi đã đo:** nhận heading/mục lục làm claim (B2). UI **không** che lỗi này — nhưng cần chỗ cho `rejected_reason` khi backend có (S1 §5 "Câu bị loại").
- **Hệ quả UI:** Card claim hiện nguyên văn to, chữ có dấu đầy đủ; chip `claim_type` + chip ngôn ngữ; 5 thuộc tính đọc từ rubric (F6) chứ không suy lại từ claim; các từ trong `vague_terms_matched` được **gạch chân chấm** trong nguyên văn.

### F3. Truy xuất bằng chứng lai (Hybrid retrieval) ✅

- **Làm gì:** BM25 + n-gram ký tự (hook RRF + reranker sẵn), top-k, có **retrieval floor** (đoạn dưới ngưỡng vẫn trả về nếu là nguồn thẩm quyền, gắn `below_threshold=true`), phát hiện **prompt injection** (`suspicious_instruction`).
- **Trường UI dùng (`RetrievedEvidence`):** `text`, `source_name`, `source_type`, `page`, `is_table`, `doc_id`, `citation`, `score`, `lexical_score`, `semantic_score`, `below_threshold`, `suspicious_instruction`, `source_qualifiers[]`, `relation`, `relation_reason`, `relation_method`.
- **Hệ quả UI:** Mỗi đoạn là một **Evidence card** (xem S3-C). Điểm BM25/ngữ nghĩa hiện dạng 2 thanh mảnh có tooltip "vì sao đoạn này được chọn". Đoạn `below_threshold` có viền đứt + ghi "dưới ngưỡng — chỉ dùng để bác bỏ, không để ủng hộ". Đoạn `suspicious_instruction` hiển thị mờ, gạch chéo, nhãn "đã loại: có chỉ thị đáng ngờ".

### F4. Kiểm chứng (Verification) 🟡

- **Làm gì:** Tính **lập trường từng đoạn** trước, rồi suy ra trạng thái claim. Thứ tự thẩm quyền: `numeric` → `qualitative_cue` → `direction` → `llm` (khi bật) → `similarity`.
- **Trạng thái claim (`VerificationStatus`):** `SUPPORTED` · `PARTIALLY_SUPPORTED` · `UNSUPPORTED` · `CONTRADICTED` · `INSUFFICIENT_EVIDENCE`.
- **Lập trường đoạn (`relation`):** `SUPPORTS` · `CONTRADICTS` · `PARTIAL` · `CONTEXT`.
- **Trường UI dùng (`VerificationResult`):** `status`, `rationale`, `evidence[]`, `computed_values{claim_numbers, evidence_numbers, matched, contradiction, closest_pair{claim, evidence, relative_error, citation}, calculation_method}`, `warnings[]`, `requires_llm_review`.
- **Lỗi đã đo (xem test report):** cue "thiếu" trùng "thiêu kết" (B1); nhãn phạm vi "1 và 2" bị đọc là số đo; chưa chuẩn hoá `1.200.000`/`1,2 triệu`; chưa phân biệt Scope 1+2 vs 1+2+3.
- **Hệ quả UI:**
  - Badge trạng thái claim + một dòng `rationale`.
  - **Numeric check card**: hiện `closest_pair` như một phép so sánh có thể đọc: *"Tuyên bố 30% · Tài liệu 8% · sai số tương đối 73% · nguồn: BCTN 2024 tr. 57"* + `calculation_method`. Khi backend có `comparison_policy` (B9) thêm dòng `policy_id` + `tolerance_used`. Khi không có cặp số: *"Không có số liệu cùng chỉ số để so"*.
  - `requires_llm_review=true` → banner vàng "Một phần lập trường do mô hình đề xuất — cần người xác nhận" và pill "AI đề xuất" nhấn mạnh.
  - `warnings[]` hiển thị thành danh sách cảnh báo có icon, không ẩn.

### F5. Kiểm tra pháp lý (Legal check, policy-as-code) 🟡

- **Làm gì:** Map `claim_type → issue`; chọn văn bản áp dụng theo **ngày hiệu lực** (`check_mode`: `current_policy_alignment` hoặc lịch sử theo `period` của claim); chạy rule pack; trả `legal_finding`. Layer **fail-tolerant**: thiếu registry → tắt và ghi lý do ở gate G7.
- **Trường UI dùng (một record trong `legal_checks[]`):** `issue`, `check_mode`, `as_of_date`, `applicable_sources[]{document, title, effective_from, source_url, role: base|amendment_in_force}`, `blocked_sources[]{document,…}` (văn bản có hiệu lực nhưng chưa trích được nội dung), `conditions[]`, `legal_finding` (`MATCH|PARTIAL_MATCH|NOT_MATCH|INSUFFICIENT_EVIDENCE`), `legal_risk`, `rules_applied[]`, `requires_human_review`, `notes`, `source_qualifiers[]`, `rule_pack_version`.
- **Thực trạng đo:** 100% `INSUFFICIENT_EVIDENCE`, `conditions` rỗng (B7) — UI phải đẹp cả khi **chưa có finding**: đây là màn "bối cảnh pháp lý" chứ không phải "phán quyết".
- **Hệ quả UI:** **Legal panel** (S3-E): timeline dọc các văn bản theo `effective_from`, nhãn `base`/`amendment_in_force`, link ra `source_url`; ô "Tính đến ngày" (`as_of_date`); danh sách `blocked_sources` với icon khóa và lời "có hiệu lực, chưa trích được nội dung — cần thu thập"; `source_qualifiers` hiển thị như **thẻ cảnh báo phạm vi** không thể tắt (ví dụ: "phán quyết chỉ áp dụng cho đúng tuyên bố đã xét, không cho toàn doanh nghiệp"). Không dùng chữ "vi phạm" ở bất kỳ đâu trong panel này.

### F6. Chấm rủi ro theo rubric (`risk-rubric-v2`) ✅

- **Làm gì:** 9 thành phần, tổng max = 100; dải: `LOW 0–24 · MEDIUM 25–49 · HIGH 50–74 · CRITICAL 75–100`. `requires_human_review` khi HIGH/CRITICAL, hoặc mâu thuẫn với nguồn pháp lý, hoặc có lập trường do LLM.
- **9 thành phần → UI:**

| Thành phần | Max | Thuộc tính UI | Nhóm hiển thị |
| --- | --- | --- | --- |
| `specificity` | 12 | Chỉ số cụ thể | **5 thuộc tính bắt buộc** |
| `quantitative_evidence` | 12 | Chỉ số cụ thể (giá trị + đơn vị) | |
| `baseline` | 8 | Năm gốc | |
| `period` | 8 | Kỳ báo cáo | |
| `scope_boundary` | 8 | Phạm vi áp dụng | |
| `evidence_support` | 18 | Bằng chứng & phương pháp | |
| `independent_assurance` | 8 | Bằng chứng & phương pháp (nguồn độc lập) | |
| `contradiction` | 18 | Mâu thuẫn với dữ liệu khác | **Tín hiệu cần lưu ý** (penalty) |
| `vague_or_exaggerated_language` | 8 | Ngôn ngữ mơ hồ / phóng đại | |

- **Quy tắc suy trạng thái thuộc tính (đã có trong `claims.js`):** component là penalty → `score/max = 0` ⇒ **Có**; `= 1` ⇒ **Thiếu**; giữa ⇒ **Một phần**. Thuộc tính gộp nhiều component chỉ "Có" khi tất cả = 0.
- **Hệ quả UI:** **Attribute checklist** 5 hàng (S3-B) với 3 trạng thái màu + dòng hành động cụ thể (`actionFor`); **Risk breakdown** dạng 9 thanh ngang xếp chồng (S3-F), tổng điểm chữ nhỏ ở cuối kèm dải; **không** có vòng tròn điểm to.

### F7. Cổng chất lượng & trạng thái phát hành ✅

- **8 gate:** `G0 Data admissibility · G1 Extraction fidelity · G2 Retrieval admissibility · G3 Deterministic verification · G4 Citation integrity · G5 Risk review · G6 Reproducibility · G7 Legal check`; `status ∈ {PASS, FAIL, PENDING_HUMAN_REVIEW}`; `details` là câu giải thích.
- **`release_status`:** `RELEASABLE` · `PENDING_HUMAN_REVIEW` · `BLOCKED`.
- **Hệ quả UI:** Dải 8 ô nhỏ trên S2 (xanh/vàng/đỏ) mở rộng ra `details`; `release_status` là **pill duy nhất** ở cấp run, đặt ở góc, không phải KPI.

### F8. Gợi ý chỉnh sửa (Suggestions) ✅

- **API:** trả kèm trong `AnalyzeResponse.suggestions[]` — mỗi claim có `items[]{code, issue, recommendation, example_fix?}`.
- **Mã:** `vague_claim · missing_quantitative_value · missing_baseline · missing_period · contradicted_by_evidence · missing_evidence · partial_evidence · no_independent_source · verifier_warning`.
- **Hệ quả UI:** Khối "Việc cần làm để claim kiểm chứng được" (S3-G): danh sách có checkbox tĩnh, `example_fix` hiện trong khung mã màu xanh nhạt; nút **"Sửa và chạy lại"** mở editor nội tuyến → gọi `analyze/text` lại (đã có `handleRecheck`).

### F9. Quy trình người xem xét (Review workflow) ✅ — đã test kỹ, đúng

- **API:** `POST /v1/reviews` · `GET /v1/reviews/{run_id}` (`states{claim_id: state}` + `decisions[]`) · `GET /v1/reviews/{run_id}/{claim_id}` (`state`, `history[]`) · `GET /v1/reviews-export/gold` (`stats{total_decisions, claims_touched, by_decision, by_state, reviewers, gold_records, ai_override_rate}`, `records[]`).
- **Máy trạng thái:** `AI_SUGGESTED → HUMAN_REVIEWED → FINALIZED` (REOPEN về HUMAN_REVIEWED; không được nhảy thẳng AI→FINALIZED).
- **Quyết định:** `CONFIRM` (chốt) · `OVERRIDE` (bắt buộc `reviewer_status`) · `ABSTAIN` · `REQUEST_EVIDENCE` · `REOPEN`. Đã kiểm: chốt lần hai → 400 "REOPEN before deciding again"; OVERRIDE thiếu status → 400; reviewer rỗng → 400.
- **Hệ quả UI:** **Decision bar** cố định đáy màn claim (S3-H): ô tên reviewer (nhớ localStorage), ô lý do, 4 nút chính + REOPEN chỉ hiện khi `FINALIZED`; OVERRIDE mở select 5 trạng thái; lịch sử dạng timeline; lỗi 400 hiển thị nguyên văn `detail`. Badge `ai_override_rate` xuất hiện ở S2 như chỉ số **chất lượng AI**, không phải chất lượng doanh nghiệp.

### F10. Dịch vụ tài liệu gốc & render trang ✅ (PDF) / 🟡 (txt/md/json)

- **API:** `GET /v1/documents/{doc_id}` (inline, `#page=N` được PDF viewer tôn trọng) · `GET /v1/documents/{doc_id}/meta` (`name, sha256, bytes, content_type, page_count`) · `GET /v1/documents/{doc_id}/page/{page}?q=…&zoom=1..4` → PNG + header `X-Highlight-Rects` (0 = không định vị được đoạn).
- **Đã kiểm:** PDF: meta 200, PNG 200 với 1 rect, trang ngoài phạm vi 404. **Tệp text: `doc_id` không khớp store → 404** (lỗi backend, đã pin test).
- **Hệ quả UI:** **Source viewer** (S4) dạng modal/drawer rộng: ảnh trang có vùng highlight vàng, thanh trang `‹ 12 / 57 ›`, zoom, nút "Mở tệp gốc", chỉ báo `sha256` rút gọn; khi `X-Highlight-Rects = 0` hiện dòng: *"Không định vị được đoạn trích trên ảnh trang — không có nghĩa đoạn không tồn tại."* Với tệp không phải PDF: hiện đoạn text với ngữ cảnh ± 2 câu thay ảnh.

### F11. Model gateway local-first ✅

- **API:** `GET /v1/gateway/health?live=` → `active_provider`, `fallback_order[]`, `providers{name:{configured,…}}`. Mặc định: `local` → `fpt → gemini → openai → anthropic`; **không key vẫn chạy** (heuristic).
- **Hệ quả UI:** Chip trạng thái ở header: "● Chạy bằng heuristic" (xám) / "● Mô hình: local (qwen3:8b)" (xanh); click mở popover liệt kê provider + nút "kiểm tra live". Không bao giờ chặn người dùng khi offline.

### F12. Gói bằng chứng & tái lập ✅

- **Mỗi run ghi:** `.quantum/runs/<run_id>/{manifest.json, result.json, audit.jsonl, evidence_pack.md}`; `manifest{run_id, created_at, pipeline_version, config_hash, input_hashes, plan[]}`.
- **Hệ quả UI:** Footer S2/S3: `run_id · rubric risk-rubric-v2 · schema analysis-result-v2 · config #a1b2c3` với nút copy; nút "Tải JSON / Markdown" (đã có dữ liệu, cần nút — E1).

### F13. Chưa có — UI phải chừa chỗ ⬜

| Tính năng | Kế hoạch | Chỗ trong UI |
| --- | --- | --- |
| **RunStore / Phiên phân tích** (mở lại run, demo từ run đã lưu) | S3.2 | Tab thứ 4 "Phiên" — danh sách run: ngày, số tài liệu, số claim, release_status, số claim đã chốt |
| **Xuất working paper PDF/JSON/MD** (kèm quyết định reviewer + manifest) | S3.1 | Nút "Xuất hồ sơ" góc phải S2/S3 → menu 3 định dạng |
| **Trích dẫn tới ô bảng** `(page, table_idx, row, col)` | S3.3 | Evidence card có chip "bảng · hàng 4 · cột 3"; Source viewer highlight ô |
| **LLM chuẩn hoá 5 thuộc tính** (`normalization_method`) | S2.1 | Nhãn nhỏ "AI đề xuất" / "heuristic" cạnh mỗi thuộc tính |
| **Hỏi–đáp có grounding** `/v1/ask` | E5 | Drawer phải "Hỏi về run này" — chỉ trả lời có trích dẫn, có trạng thái "Không đủ dữ liệu" |
| **`corpus_completeness`** phân biệt UNSUPPORTED / INSUFFICIENT | B10 | Dòng phụ dưới badge: "không thấy trong kho tài liệu đã kiểm tra" vs "kho chưa đủ để kết luận" |

---

## 3. Kiến trúc thông tin & bản đồ màn hình

```text
S0  App shell ─ header (logo chữ, chip API, chip mô hình) · nav 4 tab · footer disclaimer
 │
 ├─ S1  Tài liệu      (intake)          — dán tuyên bố / tải tệp → chạy → tiến trình 10 bước
 ├─ S2  Tổng quan     (work resume)     — 4 hàng đợi · tài liệu · thuộc tính thiếu · phân bố verdict · 8 gate
 ├─ S3  Kiểm chứng    (MÀN CHÍNH)       — trái: hàng đợi claim · phải: hồ sơ một claim (A→H)
 │     ├─ S3-A Claim header        ├─ S3-E Legal panel
 │     ├─ S3-B Attribute checklist ├─ S3-F Risk breakdown
 │     ├─ S3-C Evidence cards      ├─ S3-G Suggestions + Sửa & chạy lại
 │     ├─ S3-D Numeric check       └─ S3-H Decision bar (sticky)
 │     └─ S4  Source viewer (modal, mở từ S3-C)
 └─ S5  Phiên          ⬜ planned      — danh sách run đã lưu → mở lại S2/S3
```

**Luồng chính (đúng logic kiểm toán, cũng là kịch bản demo):**
`Claim → 5 thuộc tính → bằng chứng → phép tính số → bối cảnh pháp lý → verdict → phân rã rủi ro → quyết định người xem xét → xuất hồ sơ`.
S3 xếp các khối theo đúng thứ tự này từ trên xuống.

**Trạng thái toàn cục cần thiết kế:** (1) chưa có kết quả — tab 2/3 mờ; (2) đang chạy — stepper; (3) lỗi 400 với `detail`; (4) API offline; (5) chế độ heuristic (không LLM); (6) hàng đợi rỗng — "Không còn việc trong hàng đợi này."

---

## 4. Design system

### 4.1 Định vị hình ảnh

**"Audit workbench"** — bàn làm việc của kiểm toán viên, không phải dashboard marketing. Tĩnh, dày thông tin nhưng thở được; chữ là trung tâm (nguyên văn claim, đoạn trích, số liệu). Một màu thương hiệu duy nhất, dùng tiết kiệm cho hành động chính. Màu trạng thái mang nghĩa cố định, không dùng trang trí. Tham chiếu cảm giác: Linear (mật độ, chip), Notion (đọc dài), Stripe Dashboard (số liệu tabular), công cụ pháp lý như Westlaw (timeline văn bản).

### 4.2 Token màu (light là chính; dark là biến thể)

| Token | Light | Vai trò |
| --- | --- | --- |
| `--bg` | `#F6F7F9` (slate-50) | nền trang |
| `--surface` | `#FFFFFF` | card |
| `--border` | `#E2E8F0` (slate-200) | viền 1px |
| `--text` | `#0F172A` (slate-900) | chữ chính |
| `--text-muted` | `#64748B` (slate-500) | chữ phụ |
| `--brand` | `#047857` (emerald-700) | nút chính, tab active, focus ring |
| `--brand-soft` | `#ECFDF5` (emerald-50) | nền chọn / hover nhẹ |

**Màu ngữ nghĩa — cố định, dùng thống nhất ở badge, chấm, thanh:**

| Ý nghĩa | Nền | Chữ | Áp cho |
| --- | --- | --- | --- |
| Ủng hộ / Có / SUPPORTED / SUPPORTS | `emerald-100 #D1FAE5` | `emerald-800 #065F46` | status, relation, attribute present |
| Một phần / PARTIALLY_SUPPORTED / PARTIAL | `amber-100 #FEF3C7` | `amber-800 #92400E` | |
| Mâu thuẫn / CONTRADICTED / CONTRADICTS / Thiếu | `red-100 #FEE2E2` | `red-800 #991B1B` | status, relation, attribute missing |
| Chưa chứng minh / UNSUPPORTED | `violet-100 #EDE9FE` | `violet-800 #5B21B6` | tách khỏi INSUFFICIENT để không nhầm |
| **Abstain / INSUFFICIENT_EVIDENCE** | `sky-100 #E0F2FE` | `sky-800 #075985` | **trung tính, không đỏ** (P3) |
| Ngữ cảnh / CONTEXT / Chưa đánh giá | `slate-100 #F1F5F9` | `slate-700 #334155` | |
| Ưu tiên review (chấm nhỏ) | LOW `emerald-400` · MEDIUM `amber-400` · HIGH `orange-500` · CRITICAL `red-500` | — | chỉ chấm 8px, không số |
| Workflow | AI đề xuất `slate` · Đã có người xem `amber` · Đã chốt `emerald` | | pill viền |
| Highlight trang PDF | `#FDE047` alpha 0.45 | | vùng highlight |

### 4.3 Chữ

- **UI & nội dung tiếng Việt:** *Inter* (hoặc *IBM Plex Sans*) — hai font hỗ trợ đầy đủ dấu tiếng Việt; **kiểm tra chữ "ứ, ỡ, ậ" trong mockup**.
- **Số liệu, ID, mã văn bản:** *JetBrains Mono* / *IBM Plex Mono*, `tabular-nums`.
- **Thang:** 12 / 13 (caption, chip) · 14 (body) · 16 (nguyên văn claim trong list) · 20 (nguyên văn claim ở header S3-A, `leading-relaxed`) · 24 (tiêu đề trang). Không dùng chữ > 32px ở bất kỳ đâu — không có số KPI khổng lồ.

### 4.4 Khoảng cách & hình khối

Grid 4px; card `rounded-xl` (12px), viền 1px, **không đổ bóng** (hoặc bóng rất nhẹ ở modal); padding card 16px; khoảng cách giữa card 16px; radius chip `full`. Bố cục desktop tối đa 1280px (max-w-7xl); S3 chia `[340px | 1fr]`.

### 4.5 Kho component

| Component | Biến thể | Dữ liệu |
| --- | --- | --- |
| `StatusBadge` | 5 trạng thái claim | `VerificationStatus` |
| `RelationBadge` | 4 lập trường + hậu tố phương pháp `· numeric` | `relation`, `relation_method` |
| `AttributeRow` | present / partial / missing / unknown; kèm dòng hành động | rubric components |
| `AttributeDots` | 5 chấm 8px trong list | |
| `RiskDot` | 4 mức, chỉ tooltip | `severity` |
| `RiskBreakdownBars` | 9 thanh ngang, nhóm 5 attr + 2 penalty | `components[]` |
| `EvidenceCard` | normal / below_threshold (viền đứt) / excluded (mờ, gạch) / table (chip bảng) | `RetrievedEvidence` |
| `ScoreBars` | 2 thanh mảnh BM25 / ngữ nghĩa | `lexical_score`, `semantic_score` |
| `NumericCheckCard` | matched / contradiction / no-pair | `computed_values` |
| `LegalTimeline` | item base / amendment / blocked (khóa) | `applicable_sources`, `blocked_sources` |
| `QualifierTag` | không tắt được, icon shield | `source_qualifiers` |
| `GateStrip` | 8 ô PASS/PENDING/FAIL | `quality_gates` |
| `WorkTile` | hàng đợi có số đếm, click mở S3 với filter | `summary` |
| `DecisionBar` | theo state; 4/5 nút | review API |
| `HistoryTimeline` | decision, reviewer, time, comment | `history[]` |
| `WorkflowPill` | 3 state | `states[claim_id]` |
| `SourceViewer` | pdf / text fallback / not-located | documents API |
| `RunFooter` | run_id, versions, copy, export | `manifest` |
| `ProgressStepper` | 10 bước PLAN | client-side |
| `Disclaimer` | footer cố định | tĩnh |

### 4.6 Copy rules (bắt buộc)

- **Cấm:** vi phạm · gian lận · sai phạm · lừa dối · "phát hiện greenwashing" · "doanh nghiệp X greenwashing" · điểm trung thực · xếp hạng.
- **Dùng:** "chưa đủ bằng chứng trong kho đã kiểm tra" · "mâu thuẫn với [tên nguồn], tr. N" · "cần người xem xét" · "evidence gap" · "AI đề xuất" · "case kiểm tra".
- **Câu cố định** cho abstain: *"Đây là kết quả hợp lệ, không phải lỗi — và không có nghĩa doanh nghiệp vi phạm."*
- **Câu cố định** footer: *"Hệ thống ước lượng mức độ đầy đủ của bằng chứng cho từng tuyên bố. Kết quả không phải kết luận pháp lý về hành vi của doanh nghiệp, không thay thế kiểm toán viên hay cơ quan quản lý, và thiếu bằng chứng không đồng nghĩa vi phạm."*
- Song ngữ: nhãn thuộc tính hiện **EN đậm + VI nhạt** (`Baseline · Năm gốc`) vì rubric và hồ sơ dùng thuật ngữ EN; mọi thứ khác tiếng Việt.

### 4.7 Khả năng tiếp cận

Tương phản ≥ 4.5:1 cho chữ trên badge (các cặp 100/800 ở trên đạt). Trạng thái **không chỉ bằng màu**: luôn có chữ hoặc icon (✓ / ◐ / ✕ / ○). Focus ring 2px `--brand`. Highlight PDF có thêm viền 1px cam để người mù màu nhìn được.

---

## 5. Đặc tả từng màn hình

### S0 — App shell

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌿 GreenScan AI                                   [● Mô hình: local] [● API] │
│ Kiểm chứng tuyên bố môi trường bằng bằng chứng có trích dẫn — không kết luận  │
│ [Tài liệu] [Tổng quan] [Kiểm chứng ⑦] [Phiên ⬜]                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                              (nội dung màn)                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ disclaimer 2 dòng chữ nhỏ · run_id a1b2c3d4 · rubric v2 · schema v2 · [copy] │
└──────────────────────────────────────────────────────────────────────────────┘
```

- Logo là **wordmark chữ** + icon lá đơn sắc; không mascot.
- Badge số trên tab "Kiểm chứng" = `needsConfirmation.length` (claim cần người xác nhận).
- Chip mô hình: click → popover `fallback_order` với chấm configured/live + nút "Kiểm tra live".

### S1 — Tài liệu (Intake)

```text
┌ Nhập tuyên bố │ Tải báo cáo ┐
│                                                                              │
│  [Nguồn tuyên bố]                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Dán đoạn/báo cáo chứa tuyên bố... (Ví dụ: "Công ty đã giảm 30%      │    │
│  │ phát thải CO2 phạm vi 1 và 2 năm 2024 so với năm gốc 2020")          │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│  Tài liệu chứng cứ (tuỳ chọn)                                    [+ Thêm]    │
│  ┌ Tên: BCTN_2024.txt  Vai trò: [Chứng cứ ▾]  Loại: [Tài chính ▾]  [×] ┐    │
│  │ (nội dung)                                                            │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
│  ⚠ Chưa có nguồn độc lập (pháp lý / bên ngoài / tiêu chuẩn) — rubric sẽ      │
│    ghi "thiếu bằng chứng độc lập". Vẫn chạy được.                             │
│                                              [ Phân tích ▸ ]                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

- Chế độ **Tải báo cáo**: dropzone nét đứt; mỗi tệp một hàng: icon loại tệp, tên, kích thước, 2 select, nút xoá; hàng đầu mặc định `claim_source`.
- Tooltip cho mỗi vai trò/loại (một câu). Khi tệp là PDF scan: chip "có thể cần OCR — chậm hơn".
- **Đang chạy:** thay nút bằng stepper 10 bước theo `OrchestratorAgent.PLAN` (Kiểm tra đầu vào → Đọc & OCR → Trích tuyên bố → Lập chỉ mục → Truy xuất → Kiểm chứng → Pháp lý → Chấm rủi ro → Cổng chất lượng → Ghi hồ sơ). Bước hiện tại nhấp nháy nhẹ; không có % giả.
- **Lỗi 400:** banner đỏ nhạt, nguyên văn `detail` trong font mono.
- ⬜ Khu "Câu bị loại (N)" thu gọn — hiện khi backend trả `rejected_reason`.

### S2 — Tổng quan (Tiếp tục công việc)

```text
┌ Tiếp tục công việc ─────────────────────────────── [Xuất hồ sơ ⬜] [RELEASE PILL] ┐
│ Lần phân tích: 20/09/2026 14:02 · 41 tuyên bố · 3 tài liệu · 118 chunk               │
│ ┌ Chưa xử lý ┐ ┌ Thiếu bằng chứng ┐ ┌ Có mâu thuẫn ┐ ┌ Cần người xác nhận ┐          │
│ │    31  →   │ │       9    →      │ │     4   →     │ │        7     →       │          │
│ └────────────┘ └───────────────────┘ └───────────────┘ └──────────────────────┘          │
├───────────────────────────────┬─────────────────────────────────────────────────────────┤
│ Tài liệu đang review          │ Thuộc tính thiếu nhiều nhất                              │
│ BCPTBV_2025.pdf  41 · 31 · 4  │ Period · Kỳ báo cáo        ████████████████  31  →       │
│ BCTN_2024.pdf     0 · — · —   │ Baseline · Năm gốc         ██████████████    28  →       │
│                               │ Scope/Boundary · Phạm vi   ████████          17  →       │
│                               │ Specific metric            ███               6   →       │
│                               │ Evidence/Methodology       ██████████████████ 35 →       │
├───────────────────────────────┼─────────────────────────────────────────────────────────┤
│ Kết quả kiểm chứng            │ Cổng chất lượng                                          │
│ SUPPORTED          ███ 6      │ [G0✓][G1✓][G2✓][G3✓][G4✓][G5◐][G6✓][G7✓]                 │
│ PARTIALLY          ████ 9     │ G5 · Risk review · PENDING — 7 claim HIGH/CRITICAL       │
│ UNSUPPORTED        ██ 3       │ G7 · Legal · PASS — 41 checked, 41 inconclusive          │
│ CONTRADICTED       ██ 4       │                                                          │
│ INSUFFICIENT  (abstain) █████ 19 · Tỷ lệ dừng phán đoán 46% — tính năng, không phải lỗi │
└───────────────────────────────┴─────────────────────────────────────────────────────────┘
```

- **Mọi số đều là hàng đợi bấm được** (mở S3 với filter tương ứng). Không donut, không đường xu hướng.
- Thanh phân bố verdict là thanh ngang đơn giản, màu theo token §4.2; INSUFFICIENT dùng màu sky và chú thích tích cực.
- Chỉ số **`ai_override_rate`** (từ gold stats) hiện nhỏ ở góc: "Người xem xét ghi đè AI: 12% (2/17)" — đây là chỉ số về AI.

### S3 — Kiểm chứng (màn chính)

```text
┌─ Hàng đợi ────────────────────┐ ┌─ S3-A Claim ───────────────────────────────────────────────┐
│ [Chưa xử lý 31][Thiếu BC 9]   │ │ [CONTRADICTED] [AI đề xuất] [emissions] [vi]  ● HIGH        │
│ [Mâu thuẫn 4][Cần xác nhận 7] │ │ "Năm 2024, Tập đoàn giảm 30% phát thải CO2 phạm vi 1 và 2  │
│ [Tất cả 41]                   │ │  so với năm gốc 2020."                                       │
│ ─────────────────────────────  │ │ BCPTBV_2025.pdf · tr. 57 · [Mở trang gốc ↗]                  │
│ ● [CONTRADICTED] 1 mâu thuẫn  │ │ Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch…       │
│ "Năm 2024, Tập đoàn giảm 30%…"│ ├─ S3-B Thuộc tính bắt buộc ─────────────────────────────────┤
│ ●●●○●  BCPTBV · tr. 57        │ │ ✓ Specific metric · Chỉ số cụ thể      Có                    │
│ ─────────────────────────────  │ │ ✓ Baseline · Năm gốc                   Có                    │
│ ● [INSUFFICIENT] hợp lệ       │ │ ✓ Period · Kỳ báo cáo                  Có                    │
│ "Công ty cam kết Net Zero…"   │ │ ✕ Scope/Boundary · Phạm vi             Thiếu                 │
│ ○○●○○  BCPTBV · tr. 3         │ │   → Nêu phạm vi: công ty mẹ / hợp nhất / Scope 1-2-3          │
│ …                             │ │ ◐ Evidence/Methodology                 Một phần              │
│                               │ │   → Cần bằng chứng cùng chỉ số + cùng kỳ (2024) + phương pháp│
│                               │ │ Tín hiệu: [Mâu thuẫn với dữ liệu khác]                        │
│                               │ ├─ S3-C Bằng chứng (5) ──────────────────────────────────────┤
│                               │ │ ┌ [CONTRADICTS · numeric]  BCTN_2024.pdf · tr. 112 · bảng ┐   │
│                               │ │ │ "Tổng phát thải phạm vi 1 và 2 năm 2024 giảm 8% so với…" │   │
│                               │ │ │ Số liệu lệch: tuyên bố 30, tài liệu 8.   BM25 ▮▮▮ NG ▮▮  │   │
│                               │ │ │ 🛡 Phạm vi: báo cáo hợp nhất          [Mở trang ↗]        │   │
│                               │ │ └────────────────────────────────────────────────────────┘   │
│                               │ │ ┌ [CONTEXT · similarity] (viền đứt) dưới ngưỡng …         ┐   │
│                               │ ├─ S3-D Kiểm tra số ─────────────────────────────────────────┤
│                               │ │ Tuyên bố 30% ──── Tài liệu 8% ──── sai số tương đối 73%      │
│                               │ │ nguồn: BCTN_2024 tr. 112 · phương pháp: deterministic        │
│                               │ ├─ S3-E Bối cảnh pháp lý ────────────────────────────────────┤
│                               │ │ Vấn đề: emissions · Tính đến 20/09/2026 · current_policy     │
│                               │ │ ┃ 2026-03-01  83/2026/NĐ-CP  base        ↗                    │
│                               │ │ ┃ 2025-06-09  119/2025/NĐ-CP base        ↗                    │
│                               │ │ ┃ 2024-10-01  13/2024/QĐ-TTg base        ↗                    │
│                               │ │ 🔒 Chưa trích được nội dung: TT 17/2022 — cần thu thập        │
│                               │ │ Kết quả: INSUFFICIENT_EVIDENCE — chưa có điều kiện kiểm được │
│                               │ ├─ S3-F Phân rã rủi ro (gợi ý ưu tiên) ──────────────────────┤
│                               │ │ specificity ▮ quantitative ▮ baseline ▯ period ▯ scope ▮▮▮▮  │
│                               │ │ evidence ▮▮▮▮▮ independent ▮▮ contradiction ▮▮▮▮▮ vague ▯    │
│                               │ │ tổng 62/100 · HIGH · cần người xem xét                        │
│                               │ ├─ S3-G Việc cần làm ────────────────────────────────────────┤
│                               │ │ ☐ Nêu phạm vi (scope_boundary)                                │
│                               │ │ ☐ Đối chiếu lại số liệu với BCTN_2024 tr.112 hoặc giải trình │
│                               │ │ ☐ Bổ sung nguồn độc lập (assurance, ISO 14064)               │
│                               │ │ [✎ Sửa tuyên bố và chạy lại]                                  │
│                               │ ╞═ S3-H Quyết định (sticky) ═════════════════════════════════╡
│                               │ │ [AI đề xuất] Reviewer: [Quỳnh____] Lý do: [____________]     │
│                               │ │ [Xác nhận] [Ghi đè ▾] [Chưa đủ để kết luận] [Yêu cầu tài liệu]│
└───────────────────────────────┘ └──────────────────────────────────────────────────────────────┘
```

Chi tiết từng khối:

- **Hàng đợi (trái):** chip filter có số; mỗi hàng: chấm ưu tiên · StatusBadge · chip "N mâu thuẫn" · nguyên văn 2 dòng · 5 chấm thuộc tính · nguồn/trang. Hàng đang chọn nền `brand-soft`. Hàng đã `FINALIZED` có dấu ✓ xanh mờ và xuống cuối.
- **S3-A Claim header:** nguyên văn 20px, từ mơ hồ gạch chân chấm; chip: status, workflow pill, `claim_type`, ngôn ngữ; chấm severity có tooltip; link trang gốc; một dòng `rationale`. Nếu `requires_llm_review` → banner vàng.
- **S3-B Attribute checklist:** 5 hàng; icon + màu + nhãn EN/VI + trạng thái; hàng Thiếu/Một phần mở dòng hành động `actionFor`; phía dưới "Tín hiệu cần lưu ý" (2 penalty) dạng chip đỏ/cam chỉ khi active.
- **S3-C Evidence cards:** sắp theo `relation` (CONTRADICTS trước, rồi SUPPORTS, PARTIAL, CONTEXT); header card: RelationBadge + phương pháp, `source_name · tr. N · bảng`; body: đoạn trích ≤ 3 câu (khi backend chunk mịn hơn), phần khớp cue/số **được tô nền**; footer: `relation_reason`, 2 thanh điểm, QualifierTag, nút mở trang. Biến thể below_threshold / excluded như §4.5.
- **S3-D Numeric check:** một hàng so sánh 3 ô có mũi tên; khi `matched` nền emerald, `contradiction` nền red, no-pair nền slate với chữ "Không có số liệu cùng chỉ số để so sánh". Dòng dưới: `calculation_method`, ⬜ `policy_id`, `tolerance_used`.
- **S3-E Legal panel:** header (issue, as_of, check_mode), timeline văn bản (ngày mono, mã văn bản mono đậm, tiêu đề, chip role, link), khối blocked_sources, `legal_finding` + `notes`, các QualifierTag. Khi layer tắt: card xám "Không tra pháp lý: {lý do}" từ gate G7.
- **S3-F Risk breakdown:** 9 thanh ngang cùng thang (max khác nhau → thanh nền dài theo max, phần tô theo score); nhóm 5 thuộc tính / 2 penalty; tổng nhỏ ở cuối + dải + "cần người xem xét" nếu true. Tooltip mỗi thanh = `reason`.
- **S3-G Suggestions:** danh sách `items[]`; `example_fix` khung xanh nhạt mono; nút "Sửa tuyên bố và chạy lại" mở textarea nội tuyến với nguyên văn, nút "Chạy lại" → S2/S3 với kết quả mới, toast "Đã chạy lại với claim đã sửa (run mới #…)".
- **S3-H Decision bar:** sticky đáy cột phải; WorkflowPill; ô reviewer, ô lý do; nút: `Xác nhận` (brand), `Ghi đè ▾` (mở select 5 status, bắt buộc), `Chưa đủ để kết luận` (ABSTAIN), `Yêu cầu tài liệu` (REQUEST_EVIDENCE); khi FINALIZED chỉ còn `Mở lại`. Link "Lịch sử (N)" mở timeline. Lỗi 400 hiện nguyên văn.

### S4 — Source viewer (modal)

```text
┌ BCTN_2024.pdf · tr. 112 / 168 · sha256 69f3…a1d4 ─────────── [Mở tệp gốc ↗] [×] ┐
│ [CONTRADICTS · numeric]  "Tổng phát thải phạm vi 1 và 2 năm 2024 giảm 8%…"      │
│ ┌────────────────────────────────────────────────────────────────────────────┐  │
│ │                     (ảnh trang PNG, zoom 2x)                               │  │
│ │        ┌────────────────────────────────────────┐                          │  │
│ │        │ ▓▓▓▓ highlight vàng có viền cam ▓▓▓▓▓▓▓ │                          │  │
│ │        └────────────────────────────────────────┘                          │  │
│ └────────────────────────────────────────────────────────────────────────────┘  │
│ ‹ 111   [112]   113 ›        zoom [−][2.0x][+]        ⓘ Định vị: 1 vùng          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

- Khi `X-Highlight-Rects = 0`: thanh thông báo sky: *"Không định vị được đoạn trích trên ảnh trang — không có nghĩa đoạn không tồn tại (có thể là trang scan)."*
- Với tệp text: thay ảnh bằng khung văn bản mono, đoạn trích tô nền, ±2 câu ngữ cảnh.
- Khi 404 (lỗi doc_id hiện tại với txt): *"Tài liệu gốc không còn trong kho — trích dẫn vẫn hợp lệ theo tên/trang."*

### S5 — Phiên phân tích ⬜ (planned, vẽ để chừa chỗ)

Bảng: `run_id` (mono) · thời gian · tài liệu (N) · claim (N) · phân bố verdict mini-bar · `release_status` pill · đã chốt x/N · nút "Mở". Hàng đầu ghim "Run demo Case A/B/C". Nút "Xuất hồ sơ" theo run.

---

## 6. Prompt sinh ảnh (dùng nguyên văn, tiếng Anh)

**Cách dùng:** ghép `STYLE PREFIX` + prompt màn + `NEGATIVE`. Tỷ lệ 16:10, 1920×1200 (hoặc 1600×1000). Sinh 4 biến thể/màn, chọn 1, rồi chạy lại với "same style as reference" để đồng nhất. Model gợi ý: Flux 1.1 Pro / Ideogram 3 (chữ tốt) / GPT-image-1; Midjourney v7 dùng `--ar 16:10 --style raw --v 7`.

**Lưu ý chữ tiếng Việt trong ảnh:** hầu hết model vẽ sai dấu. Chấp nhận chữ giả (lorem) trong mockup, **hoặc** yêu cầu chữ tiếng Anh placeholder; mockup dùng để chốt bố cục/màu, không phải để chốt copy. Copy thật ở §4.6 và §5.

### STYLE PREFIX (dán đầu mọi prompt)

```
High-fidelity UI design mockup of a professional web application called "GreenScan AI", an evidence-first audit workbench for verifying corporate environmental claims. Clean light theme: off-white page background (#F6F7F9), white cards with 1px light-gray borders and 12px rounded corners, no drop shadows. Typography: Inter, small dense text sizes, monospace digits for numbers and IDs. Single brand accent: deep emerald green (#047857) used only for the primary button and active tab. Semantic status colors as soft pastel pills with dark text: emerald = supported, amber = partial, red = contradicted, violet = unsupported, sky blue = insufficient evidence (neutral, never red), gray = context. Calm, information-dense, auditor's tool aesthetic like Linear and Stripe Dashboard, not a marketing dashboard. Desktop 1440px wide layout, 16:10, crisp vector-like rendering, realistic product screenshot, no people, no photos.
```

### NEGATIVE (dán cuối / negative prompt)

```
no big KPI numbers, no giant score circle, no gauge, no speedometer, no donut chart, no pie chart, no line chart over time, no company logos, no leaderboard or ranking table, no red "HIGH RISK" headline, no 3D, no glassmorphism, no neon, no gradients, no dark mode, no stock photos, no people, no illustrations, no mascot, no blurry text, no watermark
```

### S1 — Intake

```
Screen: "Documents" intake page. Top header bar with a small leaf wordmark "GreenScan AI", a one-line gray subtitle, two small status chips on the right ("Model: local" green dot, "API ready" green dot), and a 4-tab nav below (Documents active in emerald, Overview, Verify with a small amber count badge "7", Sessions grayed). Main card with two toggle buttons "Paste claim" | "Upload reports". Under it a large textarea with placeholder text, then a section "Evidence documents (optional)" listing two document rows, each row with a filename, two small dropdown selects labeled "Role: Evidence" and "Type: Financial", and an x button; a "+ Add" link. A soft amber inline notice with a warning icon: "No independent source (legal / external / standard) yet". Primary emerald button "Analyze" bottom right. Below, a horizontal 10-step progress stepper in gray with the 5th step highlighted, small labels under each step. Footer with two lines of small gray disclaimer text.
```

### S2 — Overview (work resume)

```
Screen: "Overview" page titled "Resume work". Top row: four equal work-queue tiles, each a white card with a small gray label, a medium tabular number and a right arrow: "Unresolved 31", "No evidence 9", "Contradicted 4", "Needs human confirmation 7" (this one with a subtle amber left border). Top right of the row: a small outlined pill "PENDING HUMAN REVIEW" and a secondary button "Export dossier". Second row two columns: left card "Documents under review" listing 2 PDF filenames with small counts; right card "Most missing attributes" showing 5 horizontal bars with labels "Period · Kỳ báo cáo", "Baseline", "Scope/Boundary", "Specific metric", "Evidence/Methodology", each with a count and arrow. Third row two columns: left card "Verification results" with 5 short horizontal bars in the semantic pastel colors (emerald, amber, violet, red, sky blue) and counts, the sky blue one labeled "Insufficient evidence (abstain) 19 — a feature, not an error"; right card "Quality gates" showing a strip of 8 small squares G0–G7, seven green with check marks and one amber half-circle, with two explanatory lines under it. Footer line in mono: "run a1b2c3d4 · rubric v2 · schema v2" with a copy icon.
```

### S3 — Verification workbench (màn chính, quan trọng nhất)

```
Screen: "Verify" workbench, two-column layout. LEFT column (340px): a white card with a row of small filter chips with counts ("Unresolved 31" selected in emerald, "No evidence 9", "Contradicted 4", "Needs confirmation 7", "All 41") and a scrollable list of claim rows; each row shows a tiny colored priority dot, a pastel status pill, a two-line quoted sentence, five tiny attribute dots (green/red/amber), and a gray source label "report.pdf · p. 57"; the selected row has a very light emerald background. RIGHT column (fluid): a vertical stack of white cards in this order: (1) Claim header card: pills "CONTRADICTED" red pastel, "AI suggested" gray outline, "emissions", "vi"; a large 20px quoted claim sentence in dark text with one phrase dotted-underlined; small link "Open source page ↗"; one gray rationale line. (2) "Mandatory attributes" checklist: five rows with a status icon (check / half circle / x), label in bold English with lighter Vietnamese beside it, status word right-aligned; the red row expands to show an indented action line with an arrow. (3) "Evidence (5)" cards: each with a pastel relation pill "CONTRADICTS · numeric" or "CONTEXT · similarity", source and page in gray, a quoted passage with the matched figure highlighted in pale yellow, a gray reason line, two thin score bars labeled "BM25" and "Semantic", a small shield tag "Scope: consolidated report", and a small "Open page" link; one card has a dashed border and a note "below threshold". (4) "Numeric check" card: three boxes in a row connected by arrows: "Claim 30%" → "Evidence 8%" → "Relative error 73%" on a light red background, small gray method line beneath. (5) "Legal context" card: a vertical timeline with monospace dates and document codes like "83/2026/NĐ-CP", small role chips "base" / "amendment", external link icons, one locked item with a padlock "text not yet extracted", and a neutral result line. (6) "Risk breakdown (priority hint)" card: nine thin horizontal bars of different max lengths, partially filled, grouped 7 + 2, a small total "62/100 · HIGH · needs human review" in small text — not prominent. (7) "To do" card: three checklist lines and a secondary button "Edit claim and re-run". (8) Sticky bottom decision bar: gray pill "AI suggested", input "Reviewer name", input "Reason", buttons: emerald "Confirm", outlined "Override ▾", outlined "Insufficient to decide", outlined "Request document", small link "History (3)". Overall dense but airy, lots of small text, no large numbers anywhere.
```

### S4 — Source viewer modal

```
Screen: the same workbench dimmed behind a large centered modal (about 80% width). Modal header: filename "BCTN_2024.pdf · p. 112 / 168", a short monospace hash "69f3…a1d4", buttons "Open original ↗" and a close x. Under it a small red pastel pill "CONTRADICTS · numeric" and the quoted passage in one line. Main area: a rendered PDF page as a crisp white document image with realistic dense report text and a data table, one rectangular region highlighted with translucent yellow fill and a thin orange border. Footer bar: page navigation "‹ 111 [112] 113 ›", zoom controls "− 2.0x +", and a small info note "Highlight located: 1 region". 
```

### S5 — Sessions (planned)

```
Screen: "Sessions" page: a simple table of saved analysis runs. Columns: monospace run id, timestamp, documents count, claims count, a tiny 5-segment stacked bar in the semantic pastel colors, a status pill, "finalized 12/41", and an "Open" text button. The first row is pinned with a small bookmark icon and labeled "Demo · Case A/B/C". Top right: secondary button "Export dossier". Same header and nav as other screens with the "Sessions" tab active.
```

### Biến thể để so sánh hướng (chạy thêm nếu cần)

- **Hướng 1 "Paper":** thêm `warm off-white (#FAF9F6) background, serif for the quoted claim sentence (Source Serif), feels like an audit working paper`.
- **Hướng 2 "Console":** thêm `slightly denser, 13px base text, thin dividers instead of cards, engineering console feel`.
- Không thử hướng dark làm chính; dark chỉ là biến thể sau khi chốt.

---

## 7. Checklist nghiệm thu mockup (trước khi đưa sang code)

Loại ngay nếu vi phạm mục có ★.

- [ ] ★ Không có số điểm/KPI to; không gauge, donut, line chart; không logo công ty; không bảng xếp hạng (P1, P5)
- [ ] ★ Mọi badge trạng thái đứng cạnh ít nhất một đoạn trích có `tên tài liệu · tr. N` (P2)
- [ ] ★ INSUFFICIENT_EVIDENCE màu trung tính (sky), có câu "kết quả hợp lệ" (P3)
- [ ] ★ Không có chữ *vi phạm / gian lận / sai phạm / greenwashing* như nhãn (P4)
- [ ] Badge lập trường luôn có hậu tố phương pháp (P6)
- [ ] Có pill workflow "AI đề xuất / Đã có người xem / Đã chốt" và decision bar 4 nút (P7)
- [ ] Footer có run_id + phiên bản rubric/schema (P8)
- [ ] 5 thuộc tính đúng tên EN/VI theo §4.6, trạng thái có icon không chỉ màu
- [ ] Legal panel có ngày hiệu lực, role chip, mục "chưa trích được nội dung", qualifier tag
- [ ] Numeric check hiện cặp số + sai số + nguồn + phương pháp
- [ ] Có chỗ cho ⬜: tab Phiên, nút Xuất hồ sơ, chip "bảng · hàng · cột", nhãn "AI đề xuất/heuristic"
- [ ] Chữ tiếng Việt có dấu (kiểm tra ứ/ỡ/ậ) khi đã sang code; mockup ảnh được phép dùng placeholder
- [ ] Tương phản badge ≥ 4.5:1; focus ring nhìn thấy
- [ ] Bố cục hoạt động ở 1280px và thu gọn được về 1 cột ở < 1024px (S3 hàng đợi thành drawer)

---

## 8. Handoff sang code — tôi cần gì từ bạn sau khi có ảnh

1. Ảnh mockup đã chọn cho **S3** (quan trọng nhất), S2, S1, S4 — 1 ảnh/màn, kèm ghi chú "giữ / bỏ / đổi" bằng gạch đầu dòng.
2. Quyết định hướng (mặc định / Paper / Console) và font cuối (Inter hay IBM Plex Sans).
3. Xác nhận thứ tự khối trong S3 (A→H như §5) hay muốn đổi — thứ tự này là kịch bản demo 7 phút nên tôi khuyên giữ.
4. Với các mục ⬜: vẽ placeholder có nhãn "planned" hay ẩn hoàn toàn cho bản Bán kết 25/10 (khuyên: hiện tab Phiên + nút Xuất vì S3.1/S3.2 nằm trong tuần 28/09–04/10).

Khi có 1–4, phần code sẽ đi theo khung `frontend/src/components/*` hiện có (đã có `Workbench`, `EvidencePanel`, `AttributeChecklist`, `DecisionBar`, `SourceViewer`, `Overview`, `InputPanel`) — chủ yếu là nâng cấp bố cục, thêm `NumericCheckCard`, `LegalTimeline`, `RiskBreakdownBars`, `RunFooter`, `ProgressStepper`, tab `Sessions`, và menu xuất hồ sơ, không viết lại từ đầu.

---

## Phụ lục A — Bảng enum → nhãn hiển thị

| Enum | EN | VI (UI) | Màu |
| --- | --- | --- | --- |
| `SUPPORTED` | Supported | Được ủng hộ bởi bằng chứng | emerald |
| `PARTIALLY_SUPPORTED` | Partially supported | Ủng hộ một phần | amber |
| `UNSUPPORTED` | Unsupported | Chưa được chứng minh trong kho đã kiểm | violet |
| `CONTRADICTED` | Contradicted | Mâu thuẫn với nguồn | red |
| `INSUFFICIENT_EVIDENCE` | Insufficient evidence | Chưa đủ bằng chứng (dừng phán đoán) | sky |
| `SUPPORTS / CONTRADICTS / PARTIAL / CONTEXT` | — | Ủng hộ / Mâu thuẫn / Một phần / Ngữ cảnh | emerald / red / amber / slate |
| `numeric / qualitative_cue / direction / llm / similarity` | — | so số / cụm từ / xu hướng / mô hình / tương đồng | hậu tố mono |
| `LOW / MEDIUM / HIGH / CRITICAL` | — | tooltip "Ưu tiên review: …" | chấm |
| `AI_SUGGESTED / HUMAN_REVIEWED / FINALIZED` | — | AI đề xuất / Đã có người xem / Đã chốt | slate / amber / emerald |
| `CONFIRM / OVERRIDE / ABSTAIN / REQUEST_EVIDENCE / REOPEN` | — | Xác nhận / Ghi đè / Chưa đủ để kết luận / Yêu cầu tài liệu / Mở lại | — |
| `RELEASABLE / PENDING_HUMAN_REVIEW / BLOCKED` | — | Có thể phát hành / Chờ người duyệt / Bị chặn | emerald / amber / red |
| `MATCH / PARTIAL_MATCH / NOT_MATCH / INSUFFICIENT_EVIDENCE` (legal) | — | Phù hợp / Phù hợp một phần / Chưa đáp ứng điều kiện / Chưa đủ dữ liệu pháp lý | emerald / amber / orange (không đỏ) / sky |

## Phụ lục B — Mẫu dữ liệu một claim (rút gọn, thật từ pipeline)

```json
{
  "claim": {"text": "Năm 2024 phát thải CO2 phạm vi 1 và 2 giảm 30% so với năm 2020.", "claim_type": "emissions", "metric": "emissions", "direction": "decrease", "values": [2024, 1, 2, 30, 2020], "units": ["%"], "period": "2024", "baseline": "2020", "scope": null, "language": "vi", "source_name": "claim.txt", "source_page": null},
  "status": "CONTRADICTED",
  "rationale": "Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 30.0, tài liệu 8.0.",
  "evidence": [{"relation": "CONTRADICTS", "relation_method": "numeric", "relation_reason": "Số liệu lệch: tuyên bố 30.0, tài liệu 8.0.", "score": 0.65, "lexical_score": 0.41, "semantic_score": 0.24, "source_name": "evidence.txt", "source_type": "external", "page": null, "is_table": false, "below_threshold": false, "suspicious_instruction": false, "source_qualifiers": []}],
  "computed_values": {"matched": false, "contradiction": true, "closest_pair": {"claim": 30.0, "evidence": 8.0, "relative_error": 0.733, "citation": "evidence.txt (block 1)"}, "calculation_method": "deterministic-relative-error"},
  "risk": {"risk_score": 62.0, "severity": "HIGH", "requires_human_review": true, "components": [{"name": "scope_boundary", "score": 8, "max_score": 8, "reason": "No entity, facility or emission scope stated."}]},
  "legal": {"issue": "emissions", "check_mode": "current_policy_alignment", "as_of_date": "2026-09-20", "legal_finding": "INSUFFICIENT_EVIDENCE", "applicable_sources": [{"document": "83/2026/NĐ-CP", "effective_from": "2026-03-01", "role": "base"}]}
}
```
