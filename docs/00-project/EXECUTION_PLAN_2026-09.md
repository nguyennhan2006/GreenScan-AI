# Kế hoạch thực thi tới sản phẩm trình bày được

**Ngày lập:** 2026-09-17 · **Sửa lịch:** 2026-09-18 · **Mã đội:** AQ2026-119 (Eco Nexus) · **Mốc BTC:** prototype 25/08–**10/10/2026** · **Bán kết 25/10/2026** · Chung kết 10/11/2026
**Người thực hiện:** Quỳnh (nghiệp vụ kiểm chứng, gán nhãn), Thảo (pháp lý, taxonomy), Nhân (kỹ thuật)
**Thay thế:** phần "Kế hoạch phát triển prototype" 12 tuần trong hồ sơ Vòng 1 — Giai đoạn 1–2 đã làm xong phần lớn, kế hoạch này chỉ lập lại phần còn thiếu để **đến được một buổi demo trước hội đồng**.

> Tài liệu này là **kế hoạch có số đo**. Mỗi sprint có tiêu chí nghiệm thu chạy được bằng lệnh; không có tiêu chí nào là "đã làm xong" theo cảm nhận.

---

## 0. Kết luận ngắn

Hệ thống **đã chạy end-to-end** trên tài liệu thật, có UI, có reviewer workflow, có tầng pháp lý, có 206 test xanh. Cái **chưa có** là ba thứ, và cả ba đều là thứ hội đồng sẽ nhìn thấy ngay:

1. **Verdict chưa đáng tin trên tài liệu Việt Nam thật.** Chạy báo cáo PTBV Hòa Phát 2025: 419 "claim", **357 (85%) bị đánh CONTRADICTED**, 151 CRITICAL. Nguyên nhân đo được (mục 1.3) là lỗi kỹ thuật, không phải bản chất dữ liệu — sửa được trong 1 sprint. Nhưng nếu demo với kết quả hiện tại, hội đồng sẽ đọc là "hệ thống cáo buộc doanh nghiệp", trái với cam kết cốt lõi của hồ sơ.
2. **LLM chưa có mặt trong đường chạy mặc định.** Gateway, routing, FPT key đều sẵn, nhưng `claim_extraction: heuristic`, `llm_stance: off`. Với cuộc thi AI, cần chỉ ra LLM làm gì, ở đâu, và có ablation "có/không LLM".
3. **Gold set = 5 claim đã adjudicate / 7.960 candidate (0,06%).** Hồ sơ Vòng 1 cam kết tối thiểu 100 cặp. Đây là nút thắt duy nhất không giải quyết được bằng code — cần 2 người gán nhãn bắt đầu **từ tuần 2**, không phải tuần 5.

Kế hoạch (sửa 2026-09-18 theo lịch BTC): **hai mốc đóng băng** — **product freeze 10/10** (hết giai đoạn prototype) và **presentation freeze 25/10** (Bán kết). Bản 17/09 giả định demo-ready 02/11, muộn hơn Bán kết một tuần, nên toàn bộ mục 3 được nén lại; thứ tự ưu tiên không đổi: **verdict đúng trước, sản phẩm sau, trình bày cuối, quantum chỉ sau Bán kết**. Sản phẩm trình bày được định nghĩa ở mục 2; kịch bản demo ở mục 4.

Từ nay tới Bán kết GreenScan **không cần rộng hơn, cần khó bắt lỗi hơn**: không mở GraphRAG, đa tác tử, fine-tune (ISSUES_REGISTER A8/G8). Mỗi kết luận phải trả lời được bốn câu: *claim gốc ở đâu, evidence ở đâu, phép kiểm tra nào đã chạy, và tại sao hệ thống có hoặc không có quyền đưa ra verdict đó.*

---

## 1. Trạng thái đo được (2026-09-17)

### 1.1 Cái đã có và chạy được

| Thành phần | Trạng thái | Bằng chứng |
| --- | --- | --- |
| Pipeline 10 bước (intake → OCR → claim → retrieval → verify → legal → score → gates → pack) | ✅ chạy | `quantum-agent demo`, `analyze` trên PDF 11 MB xong < 2 phút |
| Backend FastAPI (analyze text/files, document page render + highlight, reviews append-only, gold export, gateway health) | ✅ | `src/quantum_gw/api.py`, 5.7k LOC package |
| Web UI React 3 màn (Tài liệu / Tổng quan / Kiểm chứng), checklist 5 thuộc tính, evidence panel có trang, decision bar | ✅ build được | `frontend/`, 2k LOC, `npm run build` OK |
| Model gateway: local vLLM/Ollama + FPT/Gemini/OpenAI/Anthropic/OpenRouter, routing theo task | ✅ | `configs/routing.yaml`, FPT key có trong `.env`, Ollama đã cài (chưa chạy) |
| Retrieval: BM25 + n-gram, RRF, hook BGE-M3 / reranker | ✅ lite mode | `retrieval/hybrid.py` |
| Tầng pháp lý: 11 văn bản VN, 938 clause, registry có hiệu lực/thay thế, rule pack v0.1, gate G7 | ✅ resolve đúng văn bản áp dụng | `configs/legal/`, `data/legal/clauses/` |
| Dữ liệu: 670 tài liệu / 21 DN VN30 (3,9 GB local), 297 tài liệu 29 case quốc tế, 4 case có phán quyết + 2 control VN | ✅ | `data/README.md` |
| Test: 206 pass, ruff sạch, CI backend | ✅ (sau khi thêm extra `crawl` hôm nay) | `pytest` |
| 4 case thật có phán quyết (BNY, DWS, KDP, KLM) | ✅ 4/4 khớp status, 2/4 khớp risk band | `run_case.py --all` |

### 1.2 Cái chưa có (so với hồ sơ Vòng 1 mục IX và MVP_SCOPE)

| Hạng mục | Hồ sơ hứa | Hiện tại |
| --- | --- | --- |
| Xuất báo cáo PDF/JSON từ UI | ☒ | API trả JSON đầy đủ, **chưa có nút xuất**, chưa có PDF |
| Trích dẫn tới bảng / ô bảng | "trang/bảng/ô bảng" | provenance dừng ở **trang** |
| Chatbot có grounding | ☒ | chưa có endpoint |
| Lịch sử phiên phân tích | dashboard theo DN/tài liệu | mỗi run độc lập, không có store |
| Gold set ≥ 100 cặp, κ ≥ 0,7 | cam kết tối thiểu | **5 claim** adjudicated |
| Bảng 6 ngưỡng đánh giá (F1, Recall@10, citation, số học, verdict, abstain) | mục V.5.1 | chưa đo được vì chưa có gold |
| LLM trong pipeline | Document AI + NLP/LLM + Hybrid RAG | chỉ heuristic; LLM tắt mặc định |
| Legal finding cụ thể | "đối chiếu pháp lý" | resolve đúng văn bản nhưng **100% INSUFFICIENT_EVIDENCE** (conditions rỗng) |
| Chạy 1 lệnh cả stack | Docker | compose chỉ có API, frontend chạy tay |

### 1.3 Ba lỗi chất lượng đo được — phải sửa trước khi demo bất kỳ thứ gì

**(a) Cue "thiếu" va chạm với "thiêu kết" sau khi bỏ dấu.**
`normalize_for_match("thiếu") == normalize_for_match("thiêu") == "thieu"`. Hòa Phát là doanh nghiệp thép; "thiêu kết" (sintering) xuất hiện khắp báo cáo. Trong 357 CONTRADICTED, **274 có lý do duy nhất là cue "thieu"**; 91 đoạn bằng chứng bị gắn CONTRADICTS xác nhận chứa "thiêu kết". Cùng cơ chế: "không có" bắt cả "không có sự cố môi trường" (một khẳng định tích cực).

**(b) Trích xuất claim bắt cả tiêu đề, mục lục, heading.**
"XANH HOÁ SẢN XUẤT", "4.1 | Quản trị phát triển bền vững", "BÁO CÁO PHÁT TRIỂN BỀN VỮNG NĂM 2025" đều thành claim. 419 claim từ một báo cáo, chỉ 67 có số. Trên demo mẫu, dòng tiêu đề tài liệu là claim #1 và bị CONTRADICTED.

**(c) So sánh số không theo metric.**
Claim "năng lượng tái tạo đạt 50%" bị đối chiếu với "12%" (là mức *tăng phát thải*) thay vì "8%" (là *tỷ lệ tái tạo*) trong cùng đoạn → rationale sai dù verdict tình cờ đúng.

Hệ quả tổng hợp: demo mẫu 6 claim → **6/6 CONTRADICTED**, kể cả cam kết Net Zero 2050 (đáng lẽ INSUFFICIENT/PARTIAL). Bộ golden 4 case vẫn pass vì được viết cho đúng các đường đi này — golden set hiện tại **không bắt được** các lỗi trên.

### 1.4 Tình trạng repo

- 33 file sửa + ~20 nhóm file mới **chưa commit từ tháng 8** (stance cues, legal layer, UI components, real_cases, crawl metadata, ADR 0003). Một ổ đĩa hỏng là mất một tháng làm việc.
- Hai file `.docx` hồ sơ Vòng 1 nằm ở gốc repo, chưa track.
- `.venv` thiếu dependency crawler → 2 test fail. **Đã sửa hôm nay**: thêm extra `crawl` vào `pyproject.toml`; `pip install -e ".[dev,crawl]"` → 206/206.
- Tesseract không có trên máy dev (OCR tắt; PDF có text layer vẫn chạy). Ollama đã cài, chưa chạy.

---

## 2. Định nghĩa "sản phẩm trình bày được" (Definition of Done)

Hội đồng chấm theo 5 tiêu chí Vòng 1 (bài toán 25% · khả thi 20% · công nghệ 20% · dữ liệu 15% · sáng tạo 10%). Sản phẩm được coi là trình bày được khi **tất cả** dòng dưới đây đạt, và mỗi dòng có lệnh hoặc thao tác kiểm tra:

| # | Tiêu chí | Cách kiểm tra | Phục vụ tiêu chí chấm |
| --- | --- | --- | --- |
| D1 | Chạy end-to-end trên **báo cáo PTBV thật của DN Việt Nam** (Hòa Phát 2025 + BCTN 2024) trong < 3 phút, ra **≤ 80 claim có nghĩa**, không có heading/mục lục | `quantum-agent analyze …HPG… ` rồi Quỳnh soát 100% claim | Khả thi, Công nghệ |
| D2 | Phân bố verdict **hợp lý**: khi chỉ có tài liệu của chính DN (không có nguồn độc lập) thì CONTRADICTED ≤ 15% và **mỗi** CONTRADICTED có lý do reviewer chấp nhận | Bảng soát của Quỳnh; test `tests/test_traps.py` ≥ 90% | Bài toán (nguyên tắc "không kết luận vượt bằng chứng") |
| D3 | 5 demo case phủ đủ 5 verdict (MVP_SCOPE 6.1), có kết quả kỳ vọng, pipeline khớp | `quantum-agent evaluate` 5/5 | Khả thi |
| D4 | 4 case thật có phán quyết vẫn khớp status (regression gate) | `run_case.py --all` 4/4 | Dữ liệu |
| D5 | Evidence card: **mọi** bằng chứng có trang + highlight; **ít nhất 1 claim** trích dẫn tới **ô bảng** (bảng KNK Hòa Phát) | Thao tác trên UI | Công nghệ |
| D6 | Legal check ra **ít nhất 1 finding cụ thể** (không phải INSUFFICIENT) trên demo, hiển thị điều khoản + hiệu lực + phạm vi | UI panel pháp lý | Bài toán, Sáng tạo |
| D7 | Reviewer override + **xuất working paper** JSON + Markdown + PDF, có quyết định reviewer | Nút xuất trên UI, mở file | Khả thi |
| D8 | LLM làm **2 việc nhìn thấy được** (chuẩn hoá 5 thuộc tính; stance khi lexicon bất định), có nhãn "AI đề xuất — cần người xác nhận", và có **bảng ablation** heuristic vs LLM | `quantum-agent evaluate --profile llm` | Công nghệ |
| D9 | Gold set **≥ 100 cặp**, 2 người gán độc lập, **κ báo cáo**, split theo doanh nghiệp | `data/gold/` + `reports/GOLD_SET_v1.md` | Dữ liệu |
| D10 | Bảng **6 ngưỡng** hồ sơ V.5.1 có số thật, báo cáo **theo từng DN**, kèm giới hạn | `docs/04-data-ai/EVALUATION_REPORT_v1.md` | Tất cả |
| D11 | **Một lệnh** chạy cả stack (`docker compose up`), README "demo trong 5 phút", chạy được **offline không key** | Máy sạch thử | Khả thi |
| D12 | Kịch bản demo 7 phút đã tập 2 lần + video dự phòng 5 phút | Dry-run trước giảng viên | Trình bày |
| D13 | **Numeric comparator không dùng hằng số 12%/35%**: `numeric_check` ghi `policy_id`, `tolerance_used`, `calculation`; % giảm được tính lại bằng code; khác metric/scope/boundary → không có numeric contradiction (ISSUES B9) | test mỗi nhánh policy; rationale demo không còn "12%" | Công nghệ |
| D14 | **5 verdict có định nghĩa vận hành** trong `taxonomy.yaml`; UNSUPPORTED chỉ khi `corpus_completeness: sufficient`, ngược lại INSUFFICIENT_EVIDENCE; UI ghi "not supported in provided corpus" (ISSUES B10) | test cùng claim, khác cờ → khác verdict | Bài toán |
| D15 | Slide/brief/UI **không** chứa công thức "mức độ trung thực", ngưỡng ngành tùy ý, "quantum advantage", hay số dự kiến trong cột Achieved (ISSUES F6, G5, G6) | grep + soát tay trước 17/10 | Trình bày |

Không nằm trong DoD (cố ý): fine-tune model, GraphRAG, đa tác tử, crawl thêm doanh nghiệp, chatbot grounding (S3.5 — chỉ làm nếu 10/10 đã xanh), QUBO chạy thật (chỉ sau Bán kết, nếu vào Chung kết).

Sửa 2026-09-18: D9 gold **≥ 60** adjudicated là ngưỡng bắt buộc trước 10/10; 100 là mục tiêu nếu kịp.

---

## 3. Kế hoạch sprint (sửa 2026-09-18 theo lịch BTC)

Hai mốc cứng: **product freeze 10/10** (kết thúc giai đoạn prototype của BTC) và **presentation freeze 25/10** (Bán kết). Nhân full-time kỹ thuật, Quỳnh + Thảo ~15 giờ/tuần. Mã việc S0–S5 giữ nguyên để không vỡ tham chiếu; chỉ đổi tuần và thêm S1.10, S1.11, S6. Nếu thiếu thời gian, cắt theo mục 5.

| Tuần | Giai đoạn | Nghiệm thu cuối tuần |
| --- | --- | --- |
| 18–20/09 | Freeze semantics (S0 + S1 phần chốt) | tag `demo-baseline-2026-09-18`; B1–B5 có regression test; ADR 0004/0005 |
| 21–27/09 | Truth layer (S1 còn lại) | `evaluate` 10/10; traps ≥ 18/20; 3 legal finding ≠ INSUFFICIENT; HPG CONTRADICTED ≤ 15% |
| 28/09–04/10 | Product layer (S3 + S2.1/S2.2) | RunStore; export PDF/JSON; 1 bảng KNK; panel pháp lý; LLM normalization có nhãn |
| 05–10/10 | Release candidate (S2.3, S2.4, S4) — **product freeze** | tag `rc-2026-10-10`; ≥ 60 adjudicated; ablation; Docker 1 lệnh không key; video backup |
| 11–17/10 | Evidence + pitch (S5.1–S5.2) | không thêm kiến trúc; slide đóng băng số liệu |
| 18–24/10 | Defense week (S6) | mock Q&A mỗi ngày; 2 dry-run bấm giờ; backup đầy đủ |
| 25/10 | **Bán kết** | chỉ dùng release đã đóng băng |
| 26/10–09/11 | Chỉ nếu vào Chung kết: QUBO prototype (A6, theo G5), pilot feedback, polish | benchmark 4 cột |

### Tuần 18–20/09 — Freeze semantics (Sprint 0 + phần chốt của Sprint 1)

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S0.1 | **Commit toàn bộ work đang treo**, chia 5 commit theo chủ đề: (1) legal layer + configs/legal + schemas, (2) stance cues + verifier + scorer, (3) UI components + api, (4) real_cases + crawl metadata + legal_cases, (5) docs + ADR 0003. Push `origin/main`. **Tag `demo-baseline-2026-09-18`.** | Nhân | `git status` sạch; CI xanh; tag tồn tại |
| S0.2 | Chuyển 2 `.docx` hồ sơ vào `docs/reference/`, xoá bản backup. Thêm `docs/reference/README.md`: tài liệu AI-QUANTUM cũ (công thức "mức độ trung thực ESG", ngưỡng ngành tùy ý) **đã bị thay thế**, không dùng cho slide/brief/UI (ISSUES F6). | Nhân | grep slide/brief/UI không có "trung thực", "điểm trừ" |
| S0.3 | `make setup` = `pip install -e ".[dev,crawl]"` + `npm ci`; job frontend trong CI | Nhân | CI 2 job xanh (đã làm 17/09) |
| S0.4 | **Đóng băng baseline**: `tools/snapshot_baseline.py` chạy demo + 4 real case + HPG → `benchmark/baseline_2026-09-18.json` (số claim, phân bố verdict, thời gian, git hash) | Nhân | file baseline tồn tại |
| S0.5 | Cả nhóm chốt DoD mục 2, lịch mục 3, A3/A4/A8 → `DECISIONS_LOG.md` | Cả nhóm | 5 mục trong DECISIONS_LOG |
| S1.1 | **Stance cues**: bỏ cue đơn từ ("thiếu"); match theo **ranh giới từ trên chuỗi có dấu**; cue chỉ hiệu lực khi **cùng câu** với term metric/scope của claim; whitelist phủ định tích cực ("không có sự cố", "không có vi phạm", "không phát sinh"). Test hồi quy "thiêu kết", "không có sự cố môi trường". | Nhân | HPG: CONTRADICTED ≤ 15%; 4 real case vẫn MATCH |
| S1.2 | **Lọc claim**: loại heading/mục lục (ALL-CAPS, mẫu `4.1 \|`, < 6 từ, không động từ/số); `generic_sustainability` chỉ giữ khi có vague term / số / cam kết; ghi `rejected_reason`. | Nhân | HPG ≤ 80 claim, ≥ 70% có số/cam kết |
| S1.3 | **So số theo metric**: chỉ so khi cùng metric bucket + đơn vị tương thích; không cùng → "không có số liệu cùng chỉ số". | Nhân | demo mẫu: tái tạo 50% đối chiếu đúng 8% |
| S1.4 | **Chunk theo câu/đoạn** giữ trang; evidence hiện câu chứa cue. | Nhân | đoạn trích ≤ 3 câu |
| S1.5 | **Quy tắc abstain** (ADR 0004): chỉ `claim_source` → tối đa PARTIALLY_SUPPORTED/INSUFFICIENT; CONTRADICTED chỉ khi (i) mâu thuẫn số cùng metric hoặc (ii) cue phủ định từ tài liệu vai trò evidence/authority. | Nhân + Quỳnh | demo mẫu ≥ 4 verdict khác nhau |
| S1.10 | **Chốt `comparison_policy` trên giấy** (ADR 0005 phần A, ISSUES B9): thay hằng số 12%/35% bằng policy theo loại giá trị — trực tiếp / làm tròn / % tính lại / cường độ / scope / boundary / OCR thấp / khác metric. Viết bảng nhánh + ví dụ trước, code tuần sau. | Nhân viết, Quỳnh duyệt ví dụ | bảng 8 nhánh có ví dụ thật từ HPG |
| S1.11 | **Định nghĩa vận hành 5 verdict** (ADR 0005 phần B, ISSUES B10): UNSUPPORTED chỉ khi `corpus_completeness: sufficient`; ngược lại INSUFFICIENT_EVIDENCE. Ghi vào `configs/taxonomy.yaml` `description`. | Quỳnh viết, Nhân nối | taxonomy có định nghĩa; UI chuỗi "not supported in provided corpus" |

### Tuần 21–27/09 — Truth layer (Sprint 1 còn lại)

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S1.6 | **20 câu bẫy** → `tests/fixtures/traps.jsonl` + `tests/test_traps.py`: sai năm, absolute vs intensity, Scope 1/2/3, target vs actual, "không có sự cố", tái chế kỹ thuật vs thực tế, "without admitting", evidence tự khớp, evidence sau năm claim | Quỳnh viết, Nhân nối | ≥ 18/20 |
| S1.7 | **3 rule pháp lý chạy thật** (không phải retrieval luật + LLM tóm tắt): QĐ 21/2025 Phụ lục I, TT 17/2022, NĐ 06/2022 sửa bởi 119/2025 & 83/2026. Mỗi rule: điều kiện kiểm tra được từ claim + evidence, effective date, 1 fixture ra finding ≠ INSUFFICIENT. | Thảo viết, Nhân nối | `tests/test_legal_layer.py` 3 finding cụ thể |
| S1.8 | `golden_cases.jsonl` 4 → **≥ 10 case** phủ 5 verdict + 3 bẫy | Quỳnh + Nhân | `evaluate` 10/10 |
| S1.10b | **Code `comparison_policy`** theo S1.10: `configs/numeric_policy.yaml`, `numeric_check` ghi `policy_id`, `tolerance_used`, `calculation`; % giảm tính lại từ base/current; cấm numeric contradiction khi khác metric/scope/boundary; OCR confidence thấp → abstain | Nhân | test mỗi nhánh; rationale không còn "12%" |
| S1.11b | **Cờ `corpus_completeness`** từ intake (có BCPTBV/BCTN đúng kỳ? có bảng KNK?) → verifier chọn UNSUPPORTED vs INSUFFICIENT | Nhân | test: cùng claim, khác cờ → khác verdict |
| S1.9 | **Nhánh dữ liệu v2** theo `data/COLLECTION_PLAN_v2.md`: 25–30 DN phát thải cao ∩ QĐ 13/2024 ∩ có BCPTBV; registry xử phạt; parse Phụ lục QĐ 13; `label_session.py` v2 loại self-match, ràng buộc năm evidence ≤ năm claim | Quỳnh, Thảo, Nhân | gate §6 plan v2: ≥ 70% on-topic, 100% có năm |
| S2.4a | **Gold set bắt đầu** (không đợi tuần 5): Quỳnh + Thảo gán độc lập từ hàng đợi v2; Nhân script κ | Quỳnh, Thảo | ≥ 20 cặp cuối tuần |

**Nghiệm thu:** `pytest` xanh · `run_case.py --all` 4/4 · `evaluate` 10/10 · Quỳnh ký bảng soát HPG · so với `benchmark/baseline_2026-09-18.json`.

### Tuần 28/09–04/10 — Product layer (Sprint 3 + S2.1/S2.2)

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S3.2 | **RunStore** SQLite → màn "Phiên phân tích"; demo từ run đã lưu (bảo hiểm demo) | Nhân | mở lại run < 2 s |
| S3.1 | **Xuất working paper** JSON + Markdown + **PDF** theo `OUTPUT_SPEC.md`, có quyết định reviewer + manifest tái lập | Nhân | file mở được, đủ mục |
| S3.3 | **Ô bảng**: chunk `table` `(page, table_idx, row, col)` — cam kết **đúng 1 bảng KNK** case demo chủ lực, kiểm tra tay; mọi bảng khác `confidence: low` | Nhân | D5 |
| S3.4 | **Panel pháp lý** UI: điều khoản, hiệu lực, phạm vi, finding; grep toàn bộ chuỗi UI "vi phạm/gian lận/sai phạm" theo P4 | Nhân + Thảo | D6 |
| S2.1 | **LLM chuẩn hoá claim** (`claim_normalization` → JSON 5 thuộc tính, heuristic fallback, `normalization_method`, nhãn "AI đề xuất") | Nhân | Quỳnh soát 30 claim: LLM ≥ heuristic + 15 điểm % |
| S2.2 | `llm_stance: on_ambiguous` khi có provider; cờ "cần người xác nhận" | Nhân | 4 real case stance không giảm |
| S2.5 | Mapping claim type → QĐ 21 Phụ lục I cho 3 ngành demo | Thảo | `configs/legal/sector_mapping.yaml` |
| S3.7 | Kiểm thử chấp nhận Flow A/B/C (`MVP_SCOPE.md` mục 7) | Quỳnh (B), Thảo (C) | checklist ký |

### Tuần 05–10/10 — Release candidate → **product freeze 10/10** (S2.3, S2.4, S4, S3.6)

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S2.4 | **Gold ≥ 60 adjudicated** (100 nếu kịp), 2 người độc lập, κ, split theo DN; **không** dùng nhãn LLM làm gold | Quỳnh, Thảo | `data/gold/` + `reports/GOLD_SET_v1.md` |
| S2.3 | **Ablation** `evaluate --profile heuristic\|llm` → F1 thuộc tính, verdict acc, thời gian, số call | Nhân | bảng trong `EVALUATION.md` |
| S4.1 | Eval trên gold (hold-out theo DN): F1 trích xuất, Recall@k theo k, citation precision, số học 0 lỗi, verdict acc, abstain precision; **báo cáo theo từng DN, kèm CI** | Nhân chạy, Quỳnh viết | `EVALUATION_REPORT_v1.md` |
| S4.2 | Đối kháng: prompt injection, claim không evidence → INSUFFICIENT, chạy offline | Nhân | test xanh |
| S3.6 | `docker compose up` cả stack; README "demo 5 phút"; chạy **không key** | Nhân | máy sạch |
| S4.3 | Đo thời gian thật 1 báo cáo ~200 trang; ghi là số đo, không ghi "8–12 h → 30 phút" nếu chưa đo | Quỳnh | bảng |
| S4.4 | Cập nhật brief (F4: số ở mục 6, thay "dung sai 12%" bằng comparison policy), `PROJECT_STATUS.md`, `CHANGELOG.md`, `README.md`; **tag `rc-2026-10-10`**; video dự phòng 5 phút | Cả nhóm | tag; video |

### Tuần 11–17/10 — Evidence + pitch (S5.1, S5.2)

**Không thêm kiến trúc. Chỉ fix bug.**

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S5.1 | Kịch bản 7 phút mục 4, 2 người tập; thử trên **máy trình chiếu** | Quỳnh dẫn, Nhân điều khiển | 2 lần tập bấm giờ |
| S5.2 | Slide: hook claim → why now → thesis → demo → công nghệ → validation (**3 cột Achieved/Target/Hypothesis**, ISSUES G6) → differentiation → quantum (QUBO đã sửa theo G5, không nói advantage) → close. Benchmark card. | Thảo + Quỳnh | slide đóng băng số liệu 17/10 |

### Tuần 18–24/10 — Defense week (S6)

| ID | Việc | Ai | Nghiệm thu |
| --- | --- | --- | --- |
| S6.1 | **Mock Q&A mỗi ngày**, hỏi random member; bộ 24 câu ở `docs/07-presentation/QA_DRILL.md`; kiến thức chung 8 khối (ISSUES G7) | Cả nhóm | mỗi người trả lời được mọi câu trong 60 s |
| S6.2 | Demo offline hoàn toàn; backup laptop + video + JSON/PDF in sẵn | Nhân | checklist |
| S5.3 | Dry-run trước hội đồng giả (giảng viên) | Cả nhóm | biên bản phản hồi |

### 25/10 — Bán kết. Chỉ dùng release `rc-2026-10-10` + fix đã kiểm.

### 26/10–09/11 — Chỉ nếu vào Chung kết

A6 QUBO prototype (simulated annealing + QAOA simulator) theo công thức đã sửa (ISSUES G5): benchmark Top-k · Greedy/MMR · exact ILP nhỏ · SA/QAOA trên coverage, redundancy, #chunks, runtime. Pilot feedback. Polish UI.

---

## 4. Kịch bản demo 7 phút

**Sửa 2026-09-18 — kể một câu chuyện, không demo menu.** Không mở màn bằng dashboard hay "risk score 78" (BGK sẽ đọc là cáo buộc). Mở màn bằng **một claim**, rồi đi đúng logic kiểm toán: *Claim → 5 thuộc tính → evidence → numeric calculation → legal context → verdict → risk components → reviewer decision → export working paper.*

Ba case, **mở sâu hai**:

| Case | Vai trò | Kết quả kỳ vọng |
| --- | --- | --- |
| **A** — DN VN (Hòa Phát BCPTBV 2025 + BCTN 2024, run đã lưu) | Claim định lượng KNK có đủ evidence, evidence là **ô bảng** | `SUPPORTED`, numeric calculation hiện phép tính |
| **B** — DN VN, claim cố ý thiếu base year/scope | Hệ thống **biết không kết luận** | `INSUFFICIENT_EVIDENCE` — "kết quả hợp lệ, không phải lỗi, không có nghĩa DN vi phạm" |
| **C** — KLM-2024 (phán quyết quốc tế) | Chứng minh xử lý contradiction từ authority; **chỉ nhắc nhanh** | `CONTRADICTED`, qualifier giữ nguyên |

Chạy **live đúng một claim nhỏ** để chứng minh hệ thống thật; toàn bộ báo cáo dùng saved run (S3.2) — tránh 2 phút parsing/LLM/mạng làm hỏng buổi thi. Với DN VN chỉ dùng "case kiểm tra", "evidence gap", "cần reviewer"; không dùng "doanh nghiệp này greenwashing".

| Thời gian | Nội dung | Lời nói gợi ý |
| --- | --- | --- |
| 0:00–0:35 | Hook | "Một báo cáo bền vững có thể dài hàng trăm trang. Nhưng một quyết định đầu tư có thể phụ thuộc vào đúng một câu: 'chúng tôi đã giảm 30% phát thải'. Vấn đề không phải câu này nghe có xanh hay không. Vấn đề là: 30% của chỉ số nào, so với năm nào, phạm vi nào, và bằng chứng nằm ở đâu?" |
| 0:35–1:15 | Why now | Taxonomy xanh QĐ 21/2025; 2.166 cơ sở kiểm kê KNK theo QĐ 13/2024; NĐ 06 → 119/2025 → 83/2026. Khối lượng dữ liệu đã thành bài toán kiểm chứng. |
| 1:15–1:45 | Product thesis | "GreenScan không quyết định ai greenwashing. Chúng tôi kiểm chứng từng claim và tạo hồ sơ evidence để con người ra quyết định." |
| 1:45–4:10 | **Demo** | Case A đầy đủ chuỗi (claim live nhỏ → 5 thuộc tính có nhãn "AI đề xuất" → ô bảng có trang → phép tính → verdict → risk components) → Case B abstain → Case C 20 giây → panel pháp lý (QĐ 21 Phụ lục I, hiệu lực 22/8/2025) → reviewer override → **xuất PDF** |
| 4:10–5:05 | Technology | Hybrid BM25 + BGE-M3 + rerank 30→5; số học deterministic theo comparison policy; legal policy-as-code theo effective date; LLM chỉ phần ngôn ngữ khó; 8 quality gates; local-first |
| 5:05–5:40 | Validation | **Số hiện có, không số dự kiến.** Tách automated tests / real adjudicated cases / human gold set; bảng 3 cột Achieved–Target–Hypothesis |
| 5:40–6:15 | Differentiation | "Điểm mới không phải một LLM mới. Điểm mới là kiến trúc evidence-first có thể audit, abstain và chạy local." |
| 6:15–6:40 | Quantum | "Quantum không bị ép vào MVP. Chúng tôi formalize bước chọn evidence thành QUBO và chỉ kích hoạt nếu benchmark cho thấy lợi ích so với classical baseline." |
| 6:40–7:00 | Close | "GreenScan không cố trả lời mọi câu hỏi. Nó cố làm một việc khó hơn: chỉ đưa ra kết luận mà nó có thể chỉ cho reviewer bằng chứng, phép tính và quy tắc đã sử dụng." |

Nếu BTC quy định thời lượng khác: co giãn phần demo, giữ nguyên storyline. **Không** nói "AI của chúng em phát hiện greenwashing với độ chính xác X%" cho tới khi gold đủ lớn. Bộ câu hỏi phản biện: `docs/07-presentation/QA_DRILL.md`.

---

## 5. Nếu thiếu thời gian — thứ tự cắt

Cắt từ dưới lên; **không bao giờ** cắt tuần 18–27/09 (B1–B5, B9, B10, legal rules, golden/traps). Mốc 10/10 và 25/10 là cố định, chỉ có phạm vi co lại.

1. S3.5 chatbot grounding → **đã cắt khỏi DoD** (18/09); nói "đã thiết kế, endpoint ở v1.3"
2. A6 QUBO prototype → chỉ sau Bán kết
3. S3.3 ô bảng → giữ trích dẫn trang, nói rõ giới hạn (nhưng cố giữ **một** bảng case A)
4. S2.4 gold 100 → **tối thiểu 60**, vẫn phải có κ và báo cáo thật
5. S3.1 PDF → chỉ JSON + Markdown
6. S2.2 LLM stance → giữ S2.1 (normalization) để vẫn có LLM nhìn thấy được
7. S1.11b cờ `corpus_completeness` tự động → cho reviewer đặt tay trên UI, UNSUPPORTED mặc định tắt (mọi absence → INSUFFICIENT)

## 6. Rủi ro và phương án

| Rủi ro | Xác suất | Phương án |
| --- | --- | --- |
| Sửa stance/extractor làm 4 case thật lệch | Trung bình | 4 case là gate trong CI (S0.4); mỗi thay đổi verifier phải chạy `run_case.py --all` |
| FPT API lỗi lúc demo | Trung bình | Ollama `qwen3:8b` local đã cài; heuristic profile chạy không cần model; run HPG đã lưu (S3.2); video dự phòng |
| Gán nhãn chậm (5 phút/cặp × 100 × 2 người = ~17 giờ) | Cao | bắt đầu tuần 2 chứ không tuần 5; cắt xuống 60 nếu cần; **không** dùng nhãn LLM làm gold |
| κ < 0,7 | Trung bình | hiệu chỉnh hướng dẫn `AUDIT_PROTOCOL.md`, gán lại 20 cặp, báo cáo cả hai lần |
| PDF 11 MB chậm trên máy demo | Thấp | demo từ run đã lưu; chạy live trên file nhỏ hơn (báo cáo 40 trang) |
| Bảng PDF trích sai | Cao | chỉ cam kết 1 bảng đã kiểm tra tay; mọi bảng khác gắn `confidence: low` |
| Hội đồng hỏi "quantum ở đâu" | Chắc chắn | trả lời đúng như hồ sơ: QUBO chọn tập bằng chứng tối thiểu là hướng Vòng 2; MVP hoàn thành bằng AI hiện có |

## 7. Việc làm ngay (18–20/09)

- [x] Thêm extra `crawl` vào `pyproject.toml`, cài vào venv → 206/206 test xanh (Nhân, 17/09)
- [x] A2: xác nhận lịch BTC (prototype 25/08–10/10, Bán kết 25/10, Chung kết 10/11); đổi lịch mục 3; `DECISIONS_LOG.md` (18/09)
- [x] G5: sửa công thức QUBO trong Technical Brief — $k$ là target cardinality, thêm term coverage (18/09)
- [ ] S0.1 commit + push toàn bộ work đang treo, **tag `demo-baseline-2026-09-18`** (Nhân)
- [ ] S0.4 `benchmark/baseline_2026-09-18.json`
- [ ] S0.2 `docs/reference/README.md` đánh dấu tài liệu AI-QUANTUM cũ đã thay thế (F6)
- [ ] S0.5 họp 30 phút: chốt DoD D1–D15, lịch mục 3, A3/A4/A8 → DECISIONS_LOG
- [ ] S1.1–S1.5 code + regression test (Nhân, tới 20/09)
- [ ] S1.10 bảng `comparison_policy` 8 nhánh có ví dụ HPG (Nhân viết, Quỳnh duyệt)
- [ ] S1.11 định nghĩa vận hành 5 verdict (Quỳnh viết) → `taxonomy.yaml`
- [ ] Quỳnh: 20 câu bẫy (S1.6) — không phụ thuộc code
- [ ] Thảo: 3 rule pháp lý với điều kiện kiểm tra được + effective date (S1.7) — không phụ thuộc code

---

*Liên quan:* [ROADMAP.md](ROADMAP.md) · [IMPLEMENTATION_BACKLOG.md](IMPLEMENTATION_BACKLOG.md) · [../02-product/MVP_SCOPE.md](../02-product/MVP_SCOPE.md) · [../04-data-ai/DATASET_AUDIT_V2.md](../04-data-ai/DATASET_AUDIT_V2.md) · [../05-ui/UI_REVIEW_20260808.md](../05-ui/UI_REVIEW_20260808.md) · Hồ sơ Vòng 1 (`docs/reference/`)
