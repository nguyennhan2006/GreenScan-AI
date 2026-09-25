# Sổ khúc mắc và phương án giải quyết

**Ngày lập:** 2026-09-17 · **Cập nhật:** 2026-09-25 (mục P — định vị kiểm toán; trước đó 2026-09-22 mục N — lỗi verdict từ run HPG baseline; trước đó 2026-09-18 rà soát chiến lược) · Nguồn: khảo sát hệ thống, chạy thử Hòa Phát, lô gán nhãn thử, kế hoạch v2, lịch BTC

> **Mốc chính thức (BTC, xác nhận 2026-09-18):** phát triển prototype **25/08–10/10/2026** · Bán kết **25/10/2026** · Chung kết **10/11/2026**. Kế hoạch cũ giả định demo-ready 02/11 là **sai** — muộn hơn Bán kết. Lịch mới: **product freeze 10/10 → presentation freeze 25/10**; xem `EXECUTION_PLAN_2026-09.md` mục 3.

**Ký hiệu:** 🔴 chặn demo · 🟠 làm giảm độ tin cậy · 🟡 nên làm · ⚖️ cần nhóm quyết định (không phải việc kỹ thuật)

---

## A. Quyết định đang chờ nhóm (không tốn code, chặn việc khác)

| # | Khúc mắc | Vì sao phải quyết | Đề xuất | Ai quyết |
| --- | --- | --- | --- | --- |
| A1 ⚖️🔴 | **Work treo một tháng chưa commit** (33 file sửa, ~20 nhóm file mới, gồm legal layer, stance cues, UI, real_cases) | Mất ổ đĩa = mất một tháng; không ai khác làm được trên bản này | Commit 5 nhóm theo chủ đề + push `origin/main` ngay hôm nay | Nhân (nói "commit") |
| A2 ✅ **đã đóng 2026-09-18** | **Ngày Vòng 2 thực tế** | Kế hoạch giả định demo-ready 2026-11-02 — muộn hơn Bán kết | Website BTC: prototype 25/08–10/10, **Bán kết 25/10**, Chung kết 10/11. Ghi `DECISIONS_LOG.md` #D-2026-09-18-01; EXECUTION_PLAN mục 3 đã đổi lịch | — |
| A8 ⚖️🔴 | **Không mở thêm kiến trúc** (GraphRAG, đa tác tử, fine-tune) tới 25/10 | Vanilla RAG có thể tệ hơn LLM đơn; retrieval hoàn hảo vẫn không đảm bảo generation đúng; GraphRAG lợi cho câu hỏi global/tổng hợp, còn claim verification là factual/local (paper Zhao et al., TREX) | Chốt như nguyên tắc; câu trả lời BGK ở G8 | Cả nhóm, ghi DECISIONS_LOG |
| A3 ⚖️ | **Quy ước 1:** claim chứng nhận bên thứ ba (PAS 2060, ISO 14064, "đầu tiên tại VN") khi chỉ có tài liệu của DN | Áp cho hàng chục claim sau; đổi giữa chừng phải gán lại | `INSUFFICIENT_EVIDENCE` + notes "cần chứng chỉ công khai của tổ chức chứng nhận" | Quỳnh + Thảo |
| A4 ⚖️ | **Quy ước 2:** hai mục tiêu khác chỉ số trong cùng báo cáo (PNJ: 2% KNK vs 1%/năm năng lượng) | Là bẫy "target vs target" trong failure set | Giữ `PARTIALLY_SUPPORTED`, notes tiền tố `INCONSISTENCY:` để lọc sau | Quỳnh |
| A5 ⚖️ | **LLM trong demo dùng FPT (có key) hay chỉ Ollama local?** | FPT nhanh hơn, model lớn hơn, nhưng là điểm hỏng lúc demo; Ollama trên máy không GPU chậm (qwen3:8b ~10–20 s/call) | Mặc định **local**, FPT là fallback bật bằng `.env` khi có mạng; demo từ run đã lưu nên độ trễ không lộ | Nhân |
| A6 ✅ **đã đóng 2026-09-18** | **Có làm toy prototype QUBO (simulated annealing) không?** | Tiêu chí sáng tạo 10%; hồ sơ nói "Vòng 2 nghiên cứu" nên không bắt buộc | **Chỉ sau Bán kết 25/10, nếu vào Chung kết** (26/10–09/11); theo công thức đã sửa ở G5, benchmark 4 cột; quantum không được cứu một hệ AI verdict chưa ổn định | DECISIONS_LOG D-2026-09-18-01 |
| A7 ⚖️ | **Danh mục 25–30 DN v2** — cần người chốt | Chặn crawl v2 | Quỳnh lập `data/v2/company_registry.csv` tuần 1 theo 3 tiêu chí | Quỳnh |

---

## B. Độ tin cậy verdict (Sprint 1 — không cắt)

> **Cập nhật 2026-09-20:** B1, B2 (một phần), B3, B4, B5 đã sửa và đo lại — HPG CONTRADICTED 85% → **4%**, claim 419 → 210; demo ra 3 verdict khác nhau; 19 bẫy xanh. Số đo và phần còn mở: `CORE_FEATURE_TEST_REPORT_2026-09-20.md` mục 0. B6, B7, B9 (còn phần tolerance theo độ chính xác), B10 vẫn mở.
> **Cập nhật 2026-09-22:** run HPG baseline (`benchmark/baseline_2026-09-22.json`, 181 claim) cho thấy B3/B9 **chưa đóng thật**: 7/8 CONTRADICTED sai. Ghi thành issue riêng ở **mục N** (N1–N5); N1–N5 **đứng trước** mục E (product layer) theo D-2026-09-22-01.

| # | Khúc mắc | Số đo | Phương án | Nghiệm thu |
| --- | --- | --- | --- | --- |
| B1 🔴 | Cue "thiếu" trùng "thiêu kết" sau bỏ dấu; "không có" bắt cả "không có sự cố" | 274/357 CONTRADICTED của Hòa Phát; 91 đoạn chứa "thiêu kết" | Match cue theo **ranh giới từ trên chuỗi có dấu**; cue phải **cùng câu** với term metric/scope của claim; whitelist phủ định tích cực ("không có sự cố/tai nạn/vi phạm", "không phát sinh") | HPG CONTRADICTED ≤ 15%; 4 case thật vẫn MATCH; test "thiêu kết" |
| B2 🔴 | Extractor bắt heading, mục lục, tiêu đề tài liệu | 419 claim / 1 báo cáo, 67 có số; demo mẫu claim #1 là dòng tiêu đề | Lọc: ALL-CAPS, mẫu `4.1 \|`, < 6 từ, không động từ/số; `generic_sustainability` chỉ giữ khi có vague term/số/cam kết; ghi `rejected_reason` | HPG ≤ 80 claim, ≥ 70% có số/cam kết |
| B3 🟠 | So số không theo metric | "tái tạo 50%" đối chiếu với 12% (mức tăng phát thải) | Chỉ so khi câu bằng chứng cùng metric bucket + đơn vị tương thích; không cùng → "không có số liệu cùng chỉ số" | demo mẫu đối chiếu đúng 8% |
| B4 🟠 | Chunk quá thô: file txt = 1 chunk; trích dẫn "block 1" | demo: 3 tài liệu → 3 chunk | Chunk theo câu/đoạn giữ trang; evidence hiện câu chứa cue | đoạn trích ≤ 3 câu |
| B5 🔴 | CONTRADICTED từ chính tài liệu của DN khi không có nguồn độc lập | demo: Net Zero 2050 bị CONTRADICTED bởi BCTC cùng công ty | Quy tắc abstain: chỉ `claim_source` → tối đa PARTIAL/INSUFFICIENT; CONTRADICTED cần mâu thuẫn số cùng metric **hoặc** cue từ tài liệu vai trò evidence/authority → ADR 0004 | demo mẫu ra ≥ 4 verdict khác nhau |
| B6 🟡 | Dải rủi ro lệch 2/4 case thật (HIGH thay vì CRITICAL) | `run_case.py --all` | Chưa hiệu chỉnh rubric cho tới khi có gold; ghi nhận, báo cáo trung thực | — |
| B7 🟠 | Legal check 100% `INSUFFICIENT_EVIDENCE`, `conditions` rỗng | demo 6/6, HPG 419/419 | Thảo viết 3 rule có điều kiện kiểm tra được (QĐ 21 Phụ lục I, TT 17, NĐ 06/119/83) + fixture mỗi rule | 3 finding ≠ INSUFFICIENT trong test |
| B8 🟠 | Golden set 4 case không bắt được B1–B5 | evaluate 4/4 pass với lỗi còn nguyên | Mở rộng ≥ 10 case phủ 5 verdict + 20 câu bẫy (`tests/test_traps.py`) | evaluate 10/10; traps ≥ 18/20 |
| B9 🔴 | **Dung sai số 12% là hằng số toàn cục**, ngưỡng CONTRADICTS 35% cũng vậy; không có tài liệu chuyên môn hay thực nghiệm chứng minh | `settings.py:101` `numeric_relative_tolerance=0.12`; `verifier.py:234,270`; `verifier.py:241` `error >= 0.35`; brief dòng 158/210 nói "dung sai 12%" | Thay bằng `comparison_policy` (`configs/numeric_policy.yaml`): (a) giá trị trực tiếp → so theo **độ chính xác thể hiện** sau normalize đơn vị (1,2 triệu ≡ 1.200.000); (b) giá trị làm tròn → tolerance suy từ số chữ số công bố; (c) % tăng/giảm → **tính lại bằng code** từ base/current; (d) cường độ chỉ so với cường độ; (e) Scope 1+2 ≠ Scope 1+2+3; (f) công ty mẹ ≠ hợp nhất; (g) OCR confidence thấp → abstain; (h) khác metric → **cấm** numeric contradiction. Ghi `policy_id` + `tolerance_used` vào `numeric_check`. Sau khi code xong mới sửa brief (F4). | Test mỗi nhánh (a)–(h); demo mẫu không còn "12%" trong rationale; câu trả lời BGK: *"LLM hiểu claim; phép toán không giao cho LLM; comparator chỉ chạy khi metric/unit/period/boundary/scope tương thích"* |
| B10 🔴 | **`UNSUPPORTED` và `INSUFFICIENT_EVIDENCE` chưa có định nghĩa vận hành** — open-world: "không tìm thấy" ≠ "không tồn tại" | Taxonomy có 5 verdict nhưng không nói khi nào absence được suy thành UNSUPPORTED | Định nghĩa trong `configs/taxonomy.yaml` + ADR 0005: `SUPPORTED` = evidence đúng metric/period/scope/boundary, không conflict chưa giải; `PARTIALLY_SUPPORTED` = có evidence nhưng thiếu 1 điều kiện material (scope, base year, precision); `CONTRADICTED` = có **positive contradictory evidence**, không phải thiếu support; `UNSUPPORTED` = corpus được xác định **đủ để kiểm tra yêu cầu đó** (`corpus_completeness: sufficient`) mà không tìm thấy support bắt buộc — UI ghi "not supported in provided corpus"; `INSUFFICIENT_EVIDENCE` = không thể suy luận absence → abstain. Verifier cần cờ `corpus_completeness` (đầu vào từ intake: có đủ BCPTBV/BCTN kỳ claim? có bảng KNK?). | Quy tắc: *absence chỉ thành UNSUPPORTED khi có lý do xác định evidence phải có trong corpus đã kiểm tra*; test 2 case cùng claim, khác `corpus_completeness` → 2 verdict khác nhau |

---

## N. Lỗi verdict phát hiện 2026-09-22 (run HPG baseline) — sửa trước mục E

> Nguồn: `ROUND2_READINESS_2026-09-22.md` mục 3; root cause theo code: `RESEARCH_PROGRAM_2026-09-22.md` mục 2; số đo gốc `benchmark/baseline_2026-09-22.json` (run `d160226875ec4144`, HPG BCPTBV 2025 + BCTN 2024, roles `claim_source,evidence`). Quy tắc chung: mỗi issue đóng khi (i) regression test xanh, (ii) chạy lại HPG và so với baseline, (iii) `run_case.py --all` 4/4 và 21 trap cũ vẫn xanh. **Hard gate:** Case A không vào demo cho tới khi N1 đóng (D-2026-09-22-02).

| # | Khúc mắc | Bằng chứng (run baseline) | Phương án | Owner | Nghiệm thu | Regression test | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N1 🔴 | **So số vẫn lệch metric.** Metric bucket quá thô (mọi thứ "phát thải" là một bucket); hai số cùng bảng/cùng câu của cùng tài liệu bị coi là mâu thuẫn | "99% tổng phát thải là gang thép" vs "24%" (tăng sản lượng); "23.474.480 tCO2e toàn Tập đoàn" vs "90.846" (một công ty con); "0,70 tCO2/tấn thép (Scrap-EAF)" vs "1,43" (BOF); "4,5% điện lưới" vs "0,03% tái tạo" (cả hai chiều) → 5/8 CONTRADICTED sai | (a) Khoá so sánh theo tuple `(metric, sub_metric/công nghệ, boundary tập đoàn↔công ty con, absolute↔intensity, kỳ)`; khác bất kỳ phần nào → **cấm** numeric contradiction, ghi `policy_id: metric_mismatch`; (b) hai số cùng xuất hiện trong **một câu hoặc một bảng** của cùng tài liệu → **không tự động** là mâu thuẫn: chỉ so khi xác định được quan hệ giữa chúng (target↔actual, base↔current, cùng dòng khác năm); không xác định được quan hệ → PARTIAL "cần reviewer" (sửa 22/09 chiều theo RESEARCH_PROGRAM §4 — "cùng bảng = không bao giờ mâu thuẫn" là sai, target vs actual cùng bảng là mâu thuẫn hợp lệ); (c) tỷ lệ % của "tỷ trọng" (share) không so với % của "tăng/giảm" (change); (d) ghi `calculation` khi so | Nhân | Chạy lại HPG: **0 CONTRADICTED sai** sau soát tay của Quỳnh; 4 real case vẫn 4/4 | `tests/test_verdict_traps.py`: `test_share_pct_vs_change_pct_not_contradiction`, `test_group_total_vs_subsidiary_not_contradiction`, `test_intensity_by_technology_not_contradiction`, `test_two_numbers_same_table_row_not_contradiction`, `test_grid_share_vs_renewable_share_not_contradiction` | ✅ đóng 23/09 |
| N2 🔴 | Đoạn **nội bộ** bị coi là "nguồn thẩm quyền" vì chứa cue *adjudicative* quá chung ("cơ quan quản lý", "kết luận", "quyết định của" — `configs/stance_cues.yaml`), rồi cue "thiếu" (trong "thiếu minh bạch") được tính vì câu chia sẻ token với claim; claim lại là mảnh ghép qua ranh giới chunk | Run baseline: claim tr.33 "quốc gia về giảm phát thải… Duy trì cơ chế kê khai và nộp thuế…" ↔ BCPTBV tr.78 (source_type `internal`) "…ngăn chặn… hành vi thiếu minh bạch, từ đó củng cố niềm tin với cơ quan quản lý" → CONTRADICTED "(nguồn có thẩm quyền)" (`stance.py:169–170`) | (a) `authoritative` chỉ khi `source_type ∈ {legal, standard}` **hoặc** (adjudicative cue **và** statement noun trong cùng câu — tức là câu phán quyết về tuyên bố); bỏ "cơ quan quản lý", "kết luận", "quyết định của" khỏi adjudicative, giữ "quyết định xử phạt", "kết luận thanh tra", "bản án"; (b) claim không được cắt qua ranh giới chunk (extractor: bỏ câu bắt đầu bằng chữ thường ở đầu chunk); (c) log câu chứa cue vào `relation_reason` để soát | Nhân | HPG: cue "thiếu" = 0 CONTRADICTED không hợp lệ; KLM-2024 vẫn CONTRADICTED (cue thẩm quyền thật) | `test_authority_cue_requires_topic_overlap` | ✅ đóng 23/09 |
| N3 🟠 | Extractor nhận câu không phải claim (thư CEO, câu ưu tiên chiến lược); 168 PARTIAL dùng **một** rationale chung tiếng Anh. **Root cause (audit 22/09):** `numbers = parse_numbers(sentence)` ở `claim_extractor.py` đếm cả **năm** ("năm 2025" → `[(2025, None)]`) nên câu thư CEO được coi là "có số liệu", không vague, đủ điều kiện commitment; `confidence` (0.48–0.96) luôn ≥ ngưỡng 0.40 nên không loại gì; rationale là 2 chuỗi tiếng Anh cứng ở `verifier._status` 201–212 | "Tôi rất vinh dự giới thiệu Báo cáo… năm 2025…", "xanh hóa sản xuất… là ba ưu tiên hàng đầu" → PARTIAL; 66/181 claim có số (36%) | (a) Loại năm khỏi `numbers` ở extractor (như `_measurements` ở verifier); câu không có metric/số đo/cam kết → `rejected_reason: no_claimable_content` (không vào verifier); (b) rationale PARTIAL phải nêu **thuộc tính nào trong 5 thuộc tính bị thiếu** (metric / kỳ / base year / scope / boundary) — sinh từ checklist đã có; (c) rationale tiếng Việt khi claim tiếng Việt | Nhân (code), Quỳnh (soát 30 claim bị loại) | HPG ≤ 120 claim (bước trung gian, đích ≤ 80 sau S2.1), ≥ 55% có số; 0 câu thư CEO; ≥ 3 mẫu rationale khác nhau | `test_ceo_letter_sentence_not_claim`, `test_partial_rationale_names_missing_attribute` | ✅ đóng 23/09 |
| N4 🟠 | SUPPORTED chỉ nhờ **một** cue ủng hộ từ tài liệu khác, không khớp số/thuộc tính. **Audit 22/09:** SUPPORTED có đúng 1 route (`verifier._status` 164–178); cue ủng hộ với claim **có số** đã bị hạ PARTIAL (289–296), nhưng claim **không số** + 1 cue ở tài liệu khác vẫn SUPPORTED. Ngưỡng "≥ 3/5 thuộc tính" bên dưới là **giả thuyết**, chốt sau sweep trên gold (RQ7) | "Đào tạo lập Báo cáo kiểm kê KNK" SUPPORTED vì BCTN có "chứng nhận"; 3/3 SUPPORTED cùng kiểu | SUPPORTED cần **một trong hai**: (i) khớp số cùng metric/kỳ/scope (`policy_id` ghi nhận), hoặc (ii) ≥ 3/5 thuộc tính khớp + cue ủng hộ cùng câu; chỉ cue → tối đa PARTIAL "có xác nhận định tính, chưa có số" | Nhân | HPG: mọi SUPPORTED có `numeric_check` hoặc `attribute_match ≥ 3`; 4 real case không đổi | `test_single_support_cue_is_not_supported`, `test_numeric_match_same_metric_is_supported` (guard) | ✅ đóng 23/09 |
| N5 🟠 | PARTIAL do thiếu thuộc tính mặc định ra **HIGH**; 65 HIGH + 1 CRITICAL trên DN control → đọc như cáo buộc (G2, P4). **Audit 22/09:** `scorer.py` cộng dồn 9 component với band tuyệt đối (`scoring_v1.yaml`: HIGH ≥ 50); claim PARTIAL không số/không baseline/kỳ/scope/nguồn độc lập/có từ mơ hồ = 6+12+8+8+8+7+8+0+8 = **65 → HIGH** dù không có mâu thuẫn nào | `severity_counts`: HIGH 65 (36%), CRITICAL 1 | Rubric v2: PARTIAL vì thiếu thuộc tính → **trần MEDIUM**; HIGH chỉ khi numeric contradiction cùng metric **hoặc** authoritative cue hợp lệ; CRITICAL chỉ khi kèm legal/numeric violation có `policy_id`; ghi `severity_cap_reason` vào `risk.components`; giữ nguyên cho tới khi có calibration trên gold (B6) | Nhân (code), Quỳnh (duyệt bảng trần) | HPG: HIGH ≤ 5% và mỗi HIGH có lý do thuộc 2 loại trên; KLM/DWS/BNY/KDP band không giảm | `test_partial_missing_attribute_capped_medium`, `test_high_requires_contradiction_or_authority` | ✅ đóng 23/09 |

**Đóng 2026-09-23.** Thứ tự thực tế: N1 → N3(a) → N2 → N4 → N5 → N3(b). Số đo cuối trên HPG (`benchmark/progress_2026-09-23_p0-final.json` so với `baseline_2026-09-22.json`):

| Số đo | 22/09 | 23/09 | Nghiệm thu |
| --- | ---: | ---: | --- |
| CONTRADICTED | 8 (7 sai) | **0** | 0 CONTRADICTED sai ✅ |
| HIGH · CRITICAL | 65 · 1 | **0 · 0** | PARTIAL không còn HIGH ✅ |
| Claim trích xuất | 181 | 156 | ≤ 80 — *chưa đạt*, cần S2.1 |
| Claim có số | 66 (36%) | 49 (31%) | ≥ 70% — *chưa đạt* |
| Mẫu rationale PARTIAL | 2 | **31** | nêu đúng thuộc tính thiếu ✅ |
| Claim cần người xem | — | 5 | — |
| Golden · real case · suite | 4/4 · 4/4 · xanh | 4/4 · 4/4 · xanh | giữ ✅ |

Commit: `aa49ecd` (N1, N3a), `12c352b` (N2, N4), `b9b9cd6` (N5, N3b). Còn mở sau P0: số claim và tỷ lệ có số (cần chuẩn hoá bằng LLM — S2.1/RQ6); B6 dải rủi ro chưa hiệu chỉnh (2/4 real case) — chờ gold; B7 legal rule pack.

Thứ tự cũ (giữ để tham chiếu): N1 → N4 → N5 → N2 → N3. Sau mỗi bước: `pytest`, `run_case.py --all`, `tools/hpg_progress.py`, ghi `benchmark/progress_<ngày>.json` (không sửa baseline).

---

## P. Định vị kiểm toán (mở 2026-09-25)

> Nguồn: `../02-product/AUDITOR_WORKFLOW_POSITIONING.md`. Người dùng là kiểm toán viên đang làm thủ công; sản phẩm phải trả lời "soát cái nào trước" trước khi trả lời "câu này đúng không".

| # | Khúc mắc | Số đo | Phương án | Nghiệm thu | Trạng thái |
| --- | --- | --- | --- | --- | --- |
| P1 🔴 | Đầu ra là 156 dòng cùng một dải, không dùng được làm danh sách việc | 23/09: 153 PARTIAL / 154 MEDIUM / 0 gắn cờ | Lớp xếp ưu tiên 4 yếu tố (trọng yếu · nghĩa vụ công bố · khoảng trống bằng chứng · bất thường) + hàng đợi có giới hạn + câu ghi phạm vi không soát | Điểm có phân bố; hàng đợi ≤ 25 mục; có câu "không soát gì và vì sao" | ✅ **đóng 25/09** — `agents/prioritizer.py`, `configs/priority_v1.yaml`, 6 test. HPG: 21/156 vào hàng đợi, điểm 41,3–62,9 |
| P2 🔴 | **Con số công bố quan trọng nhất không có trong danh sách claim.** Bộ lọc `table_row` (N3) loại toàn bộ dòng bảng chỉ số — mà với kiểm toán viên, chính dòng đó mới là cơ sở dẫn liệu cần kiểm | HPG trước: **4/156** claim có đại lượng tuyệt đối; "23.474.480 tCO2e" không có trong danh sách | `agents/figures.py`: `DisclosedFigure` là loại đối tượng riêng, đọc nhãn+số từ dòng bảng, giải đơn vị và kỳ ở mức trang; hai thủ tục tất định: **cross-foot** (cộng lại thành phần so với số tổng công bố) và **đối chiếu chéo tài liệu**; đưa vào cùng hàng đợi với tuyên bố | HPG: **57 số liệu công bố** trích được (5 tCO2e, 15 tấn, 36 %, 1 kWh); cross-foot chạy đúng trên bảng KNK: `22.540.603 + 933.876 = 23.474.479` so với công bố `23.474.480` → lệch −1 tCO2e, kết luận CONSISTENT (làm tròn); hàng đợi gộp 213 mục; N3 trap vẫn xanh (dòng bảng **không** thành "tuyên bố") | ✅ **đóng 25/09** |
| P3 🟠 | Corpus 670 tài liệu chưa dùng cho thủ tục phân tích; hiện mới có cross-foot trong một trang và đối chiếu chéo tài liệu cùng kỳ | 1 thủ tục chạy trên HPG | So chéo kỳ (cùng DN, nhiều năm) và chéo DN cùng ngành; cờ "im lặng có chọn lọc" | Ít nhất 1 cờ bất thường trên dữ liệu thật, có thể kiểm bằng tay | 🔲 mở — là yếu tố thứ 4 của P1, hiện chấm 0 |
| P6 🔴 | **Không tính lại % thay đổi từ số gốc và số hiện tại.** Tuyên bố "giảm 20%" đối chiếu với bằng chứng "100.000 → 80.000 tCO2e" không kết luận được, vì comparator chỉ so hai con số cùng đơn vị mà "%" và "tCO2e" khác đơn vị. Đây là mục B9(c) đã chốt 18/09 nhưng chưa làm | `tests/test_audit_checklist.py` T01, T02 đang **xfail(strict)** | Khi tuyên bố nêu % thay đổi và bằng chứng có **hai** số cùng đơn vị, cùng chỉ số, cùng ranh giới, thuộc kỳ gốc và kỳ hiện tại → tính `(current − base)/base`, so với % của tuyên bố theo dung sai `precision-v1`; ghi `calculation` vào `numeric_check` | T01 SUPPORTED, T02 CONTRADICTED; 44 trap cũ vẫn xanh; HPG không sinh CONTRADICTED mới sai | 🔲 **mở — ưu tiên cao nhất sau P5** |
| P7 🟠 | Không tách được câu chứa nhiều khẳng định thành các tuyên bố con; một câu 3 ý cho một verdict chung | rà tay checklist mục 6 | Tách theo mệnh đề khi mỗi mệnh đề có chỉ số/số riêng; giữ span gốc và provenance | Một câu 3 ý ra 3 tuyên bố con, mỗi cái có verdict riêng | 🔲 mở |
| P8 🟠 | Không phân biệt **điểm phần trăm** với **% tương đối** (20% → 30% là +10 điểm phần trăm nhưng +50% tương đối) | checklist mục 13 | Đưa `point_change` vào `NumericFact` khi hai giá trị đều là tỷ lệ; rationale nói rõ loại nào | Test hai chiều: +10 điểm pt không bị đọc là +50% | 🔲 mở |
| P9 🟠 | Logic xu hướng: "giảm từ 2020 đến 2025" bị coi như "giảm liên tục từng năm"; năm thiếu không được suy ra là giảm đều | checklist mục 14 | Chỉ kết luận xu hướng khi có đủ chuỗi năm; thiếu năm → nêu rõ khoảng trống | Test chuỗi thiếu năm → không kết luận liên tục | 🔲 mở |
| P10 🟠 | **Áp dụng pháp luật chưa kiểm ngành/đối tượng.** Tầng pháp lý chọn văn bản theo `issue` và ngày hiệu lực, chưa kiểm chủ thể/ngành/hoạt động; hiện chưa lộ ra vì rule pack rỗng nên luôn trả INSUFFICIENT — tức là **T10 pass nhờ abstain, không nhờ thiết kế** | `legal/checker.py` không có kiểm `sector`/`subject` | Mỗi rule khai `applies_to`: ngành, loại chủ thể, ngưỡng quy mô; không khớp → `LEGAL_RELEVANT` nhưng **không** `LEGAL_APPLICABLE` | Test: thông tư ngân hàng không áp cho DN sản xuất | 🔲 mở |
| P11 🟡 | Manifest chưa ghi phiên bản corpus/chỉ mục và phiên bản prompt | `RunManifest` có run/pipeline/config hash + input hash, thiếu corpus & prompt version | Thêm `corpus_version`, `prompt_version` (khi bật LLM), `rule_pack_version` vào manifest | Chạy lại từ manifest dựng đúng bộ dữ liệu | 🔲 mở |
| P5 🟠 | **Đầu hàng đợi vẫn là văn tường thuật, không phải số liệu** — và đây là hành vi *đúng* của lớp ưu tiên: một số liệu đã cross-foot và nhất quán thì rủi ro sai thấp nên xếp sau một câu chưa ai kiểm. Vấn đề nằm ở **độ chính xác của bước trích tuyên bố**: những câu như "Vòng đời của thép đi qua hai giai đoạn" là câu giải thích, không phải tuyên bố môi trường | HPG: 5/14 mục đầu hàng đợi là câu giải thích | Bộ 100 câu gán nhãn 4 lớp (RQ1) rồi siết `claim admissibility`; đo P/R theo từng lớp trước và sau | ≥ 80% mục trong 14 mục đầu là tuyên bố thật theo Quỳnh soát | 🔲 mở |
| P4 🟠 | Chưa có giấy làm việc đúng nghĩa | `evidence_pack.md` thiếu mục phạm vi, người thực hiện, người soát | Mở rộng theo `OUTPUT_SPEC`; mục "không kiểm gì và vì sao" đã có từ P1 | Xuất được file kiểm toán viên ký | 🔲 mở |

---

## C. Dữ liệu (nhánh v2, song song Sprint 1–2)

| # | Khúc mắc | Số đo | Phương án | Ai / khi |
| --- | --- | --- | --- | --- |
| C1 🔴 | Hàng đợi gán nhãn lệch chủ đề | 945/3.682 (26%) có từ khoá môi trường; lô thử 6/8 off-topic | Không gán thêm từ hàng đợi cũ; xây hàng đợi v2 lọc lexicon | Nhân, tuần 3 |
| C2 🔴 | Danh mục DN lệch ngành, ngành phát thải cao crawl được 0–6 tài liệu | 30 DN: 4 ngân hàng, 3 dược, 3 bán lẻ | `COLLECTION_PLAN_v2.md` §4: 25–30 DN phát thải cao ∩ QĐ 13 ∩ có BCPTBV | Quỳnh tuần 1, Nhân crawl tuần 2 |
| C3 🔴 | Không có nguồn đối chứng độc lập | 0 tài liệu lớp B | Parse Phụ lục QĐ 13 (tCO₂tđ/cơ sở); registry 20 quyết định xử phạt; CBTT bất thường | Nhân + Thảo tuần 1–2 |
| C4 🟠 | OCR Phụ lục QĐ 13 nhiễu ("Céng ty", "Viét Trung") → khớp tên cơ sở ↔ mã CK không chắc | quan sát mẫu | Khớp mờ (rapidfuzz) + Quỳnh duyệt tay 100%; ghi `match_confidence` | Nhân tuần 1 |
| C5 🟠 | Ghép bằng chứng sai kỳ và tự trùng | claim 2023 ↔ BCPTBV 2025; E1 = chính câu claim (score 1.30) | `label_session.py` v2: loại self-match; sắp theo (thẩm quyền nguồn, \|Δnăm\|, điểm) với ràng buộc năm evidence ≤ năm claim | Nhân tuần 2 |
| C6 🟡 | 196 tài liệu chưa gán năm; 1 trường hợp leakage cross-split | `leakage_report.json` | Gán năm tay chỉ cho DN nằm trong danh mục v2; xử lý leakage trước khi gán nhãn | Quỳnh tuần 2 |
| C7 🟠 | Gold set 5 → 100, hai người gán độc lập ≈ 17 h/người | 0,06% adjudicated | Bắt đầu tuần 3 (không tuần 5); tối thiểu 60 nếu thiếu thời gian; **không** dùng nhãn LLM làm gold | Quỳnh, Thảo |
| C8 🟡 | Bằng chứng chứng nhận bên thứ ba khó lấy (PAS 2060, ISO) | VNM trial | Chỉ nhận khi có URL công khai của tổ chức chứng nhận; nếu không → A3 | Thảo |
| C9 🟡 | PDF gốc không commit; máy demo cần có | 36 MB real_cases + 4 GB crawl local | Gói `demo_bundle/` (5 DN demo, ~100 MB) + checksum, tải riêng | Nhân S3 |

---

## D. LLM trong pipeline (Sprint 2)

| # | Khúc mắc | Phương án | Nghiệm thu |
| --- | --- | --- | --- |
| D1 🟠 | Đường chạy mặc định không dùng LLM (`heuristic`, `llm_stance: off`) | Bật LLM cho `claim_normalization` (5 thuộc tính, JSON schema) + `qualitative_stance` khi bất định; heuristic là fallback; UI nhãn "AI đề xuất" | Quỳnh soát 30 claim: LLM đúng hơn heuristic ≥ 15 điểm % |
| D2 🟠 | Ollama đã cài nhưng chưa chạy; chưa kiểm tra JSON mode với `qwen3:8b` trên máy không GPU | Khởi động, đo độ trễ/claim, thử `format: json`; nếu > 20 s/claim → batch + cache theo hash claim | bảng độ trễ |
| D3 🟡 | Chưa có ablation | `quantum-agent evaluate --profile heuristic\|llm` → bảng F1 thuộc tính, verdict, thời gian, số call | bảng trong `EVALUATION.md` |
| D4 🟡 | Routing hiện là giả thuyết chưa đo (ghi rõ trong `routing.yaml`) | Giữ; chỉ đổi khi ablation cho thấy khác | — |

---

## E. Sản phẩm / UI (Sprint 3)

| # | Khúc mắc | Phương án |
| --- | --- | --- |
| E1 🔴 | Không có nút xuất báo cáo (hồ sơ hứa PDF/JSON) | Nút xuất → JSON + Markdown + PDF (working paper theo OUTPUT_SPEC), gồm quyết định reviewer |
| E2 🔴 | Mỗi run độc lập, không lưu → demo phải chạy lại live | `RunStore` SQLite; màn "Phiên phân tích"; demo từ run đã lưu |
| E3 🟠 | Provenance dừng ở trang; hồ sơ hứa "ô bảng" | Chunk loại `table` (page, table_idx, row, col) — cam kết 1 bảng KNK Hòa Phát đã kiểm tra tay |
| E4 🟠 | Chưa có panel pháp lý; ngôn ngữ UI có thể lộ chữ "vi phạm" | Panel điều khoản + hiệu lực + phạm vi; rà toàn bộ chuỗi UI theo nguyên tắc P4 (grep "vi phạm", "gian lận", "sai phạm") |
| E5 🟡 | Chatbot grounding trong deliverables, chưa có | `/v1/ask` chỉ trả lời từ evidence của run, có trích dẫn, "Không đủ dữ liệu" khi dưới ngưỡng; giới hạn 2 ngày |
| E6 🟠 | Docker compose chỉ có API; frontend chạy tay | Thêm service frontend (nginx); README "demo 5 phút"; kiểm tra chạy không key |
| E7 🟡 | Tesseract không có trên máy dev → nhánh OCR chưa được thử tại chỗ | Demo chỉ dùng PDF có text layer; OCR thử trong Docker (image đã cài tesseract) |

---

## F. Quy trình / repo / CI

| # | Khúc mắc | Trạng thái |
| --- | --- | --- |
| F1 | Test cần extra `crawl` nhưng CI cài `.[dev]` → CI sẽ đỏ | **Đã sửa hôm nay:** `ci.yml`, `Makefile`, `README` dùng `.[dev,crawl]`; thêm job `frontend` (npm ci, lint, build) |
| F2 | 2 file `.docx` hồ sơ ở gốc repo, chưa track | Chuyển vào `docs/reference/`, xoá bản backup (S0.2) |
| F3 | Không có baseline số đo để so sau mỗi sprint | `tools/snapshot_baseline.py` → `benchmark/baseline_<date>.json` (S0.4) |
| F4 | Technical brief chứa số sẽ lỗi thời (gold 5/100, HPG 85%) | Mục 6 của brief gắn phiên bản; cập nhật sau Sprint 1 và Sprint 4 |
| F5 | Lint frontend có 3 warning (fast-refresh export, unused param) | Sửa trong S3, không chặn |
| F6 🔴 | **Tài liệu AI-QUANTUM cũ (`docs/reference/AI-QUANTUM_AGENT_CRITERIA_v1.docx`) còn công thức "mức độ trung thực ESG", "Rất trung thực", ngưỡng ngành tùy ý** (≥20% tái tạo = 0 điểm trừ; "chi phí môi trường tiềm ẩn = 10% dịch vụ mua ngoài") — xung đột trực tiếp nguyên tắc P4 | Không đưa bất kỳ công thức nào trong đó lên slide/brief/UI; đổi tên file thành `..._SUPERSEDED.docx` hoặc thêm `docs/reference/README.md` ghi "đã thay thế bởi risk-rubric-v2, không dùng"; grep slide/brief/UI theo "trung thực", "honesty", "điểm trừ" trước presentation freeze |
| F7 🔴 | **Tag baseline** | Sau A1 commit: `git tag demo-baseline-2026-09-18`; mọi số đo sau so với tag này (F3 ghi hash tag vào `benchmark/baseline_*.json`) |

---

## G. Rủi ro trình bày

| # | Rủi ro | Phương án |
| --- | --- | --- |
| G1 | FPT/mạng lỗi lúc demo | Local Ollama + run đã lưu (E2) + video 5 phút |
| G2 | Hội đồng đọc điểm rủi ro là "cáo buộc" | Không hiện điểm tổng DN; mở màn bằng claim + bằng chứng; câu mở/kết nhắc nguyên tắc P4 |
| G3 | "Quantum ở đâu?" | Trả lời như hồ sơ: QUBO chọn bằng chứng là hướng Vòng 2; A6 quyết có toy prototype |
| G4 | Số liệu đánh giá chưa có khi nộp | Nếu gold < 100: công bố số trên tập có, kèm khoảng tin cậy và theo DN — không ngoại suy |
| G5 🔴 | **Công thức QUBO trong brief sai ngữ nghĩa**: term $\mu(\sum_j x_j - k)^2$ ép **đúng** $k$, không phải "tối đa $k$" như mô tả; objective chỉ có relevance + redundancy, không có coverage 5 thuộc tính dù sản phẩm hứa đo coverage | **Đã sửa brief 2026-09-18:** $k$ = target cardinality (benchmark nhiều $k$); nếu cần $\le k$ phải encode slack/inequality penalty; thêm biến $y_m$ cho từng thuộc tính bắt buộc với reward $-\gamma\sum_m w_m y_m$ và penalty liên kết $y_m$ với chunk chứa thuộc tính $m$. Benchmark 4 cột: Top-k · Greedy/MMR · Exact ILP/brute-force nhỏ · SA/QAOA — đo coverage, redundancy, #chunks, runtime. **Không nói "quantum advantage" nếu chưa đo.** QAOA thua vẫn là kết quả hợp lệ. |
| G6 | Nhiều bộ số khác nhau giữa hồ sơ V1, kế hoạch, trạng thái thật → dễ bị hỏi vặn | Slide tách 3 cột **Achieved → Target → Hypothesis**. Achieved (tại 09/2026): 670 tài liệu/21 DN, 15.658 chunks, 7.960 claim candidates, 3.786 evidence candidates; legal 11 văn bản/938 điều khoản; 206 test; 4 real case khớp contradiction; golden citation coverage 100%; gold adjudicated rất nhỏ; risk band 2/4. **Không** đưa "100 pair", "accuracy ≥0,80", "8–12 h → 2,5 h" sang cột Achieved trước khi đo. |
| G7 | BGK hỏi chéo — không "đẩy cho Nhân/Quỳnh/Thảo" | Trước 25/10 cả ba giải thích được trong 60 s: Scope 1/2/3, absolute vs intensity, base year, boundary; green credit/bond, taxonomy; Luật BVMT 2020, TT17/2022, QĐ21/2025, QĐ13/2024, NĐ06→119→83; BM25/embedding/RRF/reranker/Recall@k; extraction vs generation, NLI, hallucination, injection, abstention; P/R/F1, company-held-out split, κ, CI, ablation; text layer vs OCR, table provenance; QUBO/penalty/Ising/SA/QAOA/NISQ. Mẫu trả lời: **failure mode → design choice → measurement**. Bộ 24 câu Q&A ở `docs/07-presentation/QA_DRILL.md` (S6) |
| G8 | "Tại sao không GraphRAG / multi-agent / fine-tune?" | Claim-level verification là factual/local retrieval; GraphRAG lợi cho global synthesis nhưng thêm indexing/complexity (TREX); multi-agent không cần khi workflow đã biết trước và compliance cần reproducibility; đặt V2 sau benchmark. Dẫn paper Zhao et al.: RAG có thể làm tệ hơn standalone, perfect retrieval vẫn lỗi generation, tăng #doc có thể giảm hiệu năng → vì thế không tăng top-k tùy ý, rerank 30→5, đo Recall@k và verdict acc theo k |
| G9 | Demo mở màn bằng dashboard/risk score → BGK đọc là cáo buộc | Mở màn bằng **một claim**: "giảm 30% phát thải Scope 1+2 năm 2024 so với năm gốc 2020" → 5 thuộc tính → evidence → numeric → legal → verdict → risk components → reviewer → export. 3 case, mở sâu 2: A (VN, SUPPORTED), B (VN, cố ý thiếu base year/scope → INSUFFICIENT), C (quốc tế có phán quyết, nhắc nhanh). Chạy **live 1 claim nhỏ**, còn lại từ saved run. Với DN VN dùng "case kiểm tra", "evidence gap", "cần reviewer" |

---

## Thứ tự làm (theo lịch BTC, cập nhật 2026-09-18)

Nguyên tắc: **không rộng hơn, khó bắt lỗi hơn.** Lỗi làm đổi verdict (B1–B5, B9, B10) là lỗi lõi, sửa trước mọi tính năng.

| Giai đoạn | Mục | Definition of Done |
| --- | --- | --- |
| **18–20/09** Freeze semantics | A1, F7, A3/A4, A8, F2, F6; B1–B5 có regression test; B9/B10 chốt policy trên giấy (ADR 0004/0005) | `git tag demo-baseline-2026-09-18`; DECISIONS_LOG có 5 mục; brief không còn công thức truth score |
| **21–27/09** Truth layer | **N1–N5 trước** (D-2026-09-22-01), B8 (≥10 golden, ≥20 trap), B7 (3 legal rule chạy thật), B9/B10 code, C5 (self-match, cross-year), C1–C4; C7 **bắt đầu** gán nhãn | evaluate 10/10; traps ≥18/20; 3 legal finding ≠ INSUFFICIENT; HPG CONTRADICTED ≤15% **và 0 CONTRADICTED sai sau soát tay**; PARTIAL không còn HIGH |
| **28/09–04/10** Product layer | E2 RunStore, E1 export JSON/PDF + reviewer decision, E3 **một** bảng KNK, E4 panel pháp lý + grep P4, D1/D2 LLM normalization | mở lại run <2 s; PDF mở được; 1 claim trích tới ô bảng |
| **05–10/10** Release candidate (**product freeze 10/10**) | C7 ≥60 adjudicated (100 nếu kịp); D3 ablation; Recall@k, citation precision, verdict metrics theo DN; E6 Docker 1 lệnh không key; video backup; F4 cập nhật brief | tag `rc-2026-10-10`; máy sạch chạy được |
| **11–17/10** Evidence + pitch | **Không thêm kiến trúc.** Chỉ fix bug; benchmark card; G6 bộ số 3 cột; luyện demo; thử trên máy trình chiếu | slide đóng băng số liệu |
| **18–24/10** Defense week | G7 mock Q&A mỗi ngày, random member; demo offline; backup laptop/video/JSON/PDF | 2 dry-run bấm giờ |
| **25/10** Bán kết | Chỉ dùng release đã đóng băng | — |
| 26/10–09/11 (nếu vào Chung kết) | A6 QUBO prototype theo G5; pilot feedback; polish | benchmark 4 cột |
