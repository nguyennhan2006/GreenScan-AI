# Chương trình nghiên cứu có căn cứ code — 2026-09-22

**Vai trò:** tài liệu **đi kèm** `ROUND2_READINESS_2026-09-22.md` (snapshot số đo, không sửa). Snapshot trả lời *"đang ở đâu"*; tài liệu này trả lời *"cái gì đã được chứng minh bằng code/test/dữ liệu, cái gì mới là giả thuyết, và thí nghiệm nào biến giả thuyết thành tuyên bố"*.
**Nguồn:** audit code trực tiếp trên working tree tại tag `demo-baseline-2026-09-22` (Nhân với Claude, 22/09) + bản dự thảo "Round 2 Readiness — Research & Code-grounded" (viết không đọc repo, 22/09) + hồ sơ Vòng 1 + `docs/research/`.
**Nguyên tắc:** *claim nào cũng phải có căn cứ; chưa có căn cứ thì không biến thành kế hoạch giả định mà thành câu hỏi nghiên cứu có điều kiện nghiệm thu.*

> **Implemented ≠ Planned ≠ Researched ≠ Proven.**

| Trạng thái | Ý nghĩa |
| --- | --- |
| **PROVEN** | Đã chạy/đo trên codebase hoặc dữ liệu thật, có artifact tái hiện |
| **IMPLEMENTED – NOT VALIDATED** | Có code, chưa có gold/evaluation đủ để chứng minh chất lượng |
| **RESEARCH-BACKED – NOT IMPLEMENTED** | Có cơ sở nghiên cứu, code chưa triển khai (hoặc có adapter nhưng chưa bật/đo) |
| **OPEN QUESTION** | Chưa đủ căn cứ cả code lẫn thực nghiệm; phải nghiên cứu trước khi tuyên bố |

---

## 1. Bài toán GreenScan thực chất đang giải

Phát biểu được phép dùng:

> **GreenScan AI là hệ hỗ trợ kiểm tra rủi ro greenwashing ở cấp từng claim.** Hệ thống trích claim, liên kết claim với bằng chứng có trang, kiểm tra nhất quán số liệu / phạm vi / kỳ bằng phép so sánh deterministic, đối chiếu quy định có cấu trúc, và chuyển case không đủ bằng chứng sang abstain/review thay vì kết luận về doanh nghiệp.

Run HPG 22/09 (`benchmark/baseline_2026-09-22.json`) cho thấy nút thắt khoa học trung tâm: **tìm thấy hai con số khác nhau ≠ tìm thấy mâu thuẫn.** 5/8 CONTRADICTED là so hai đại lượng không cùng semantics/boundary. Câu hỏi đúng không phải "có số nào khác số claim không" mà là *"hai số này có cùng metric, cùng phạm vi, cùng basis, cùng kỳ để được phép so sánh không"*.

---

## 2. Kết quả audit code — 15 câu hỏi mục 22 của bản dự thảo

Mọi dòng dưới đây đọc từ code tại tag `demo-baseline-2026-09-22`. Số dòng có thể lệch sau khi sửa; tên hàm giữ nguyên.

| # | Câu hỏi | Trả lời từ code | Hệ quả |
| --- | --- | --- | --- |
| 1 | **Numeric schema ở đâu? Metric bucket tạo ở đâu?** | Số được parse thành tuple `(value, canonical_unit, half_precision)` bởi `parse_quantities` ([utils/text.py:198](../../src/quantum_gw/utils/text.py#L198)); đơn vị canonical hoá qua bảng `_UNITS` (text.py:115–134). Thuộc tính claim gán ở **extractor** ([agents/claim_extractor.py:174–193](../../src/quantum_gw/agents/claim_extractor.py#L174-L193)): `metric` = bucket taxonomy đầu tiên khớp (**6 bucket**: emissions, renewable_energy, energy, water, waste, green_finance — `configs/taxonomy.yaml`), `scope` = scope_bucket đầu tiên, `period`/`baseline` = năm đầu/cuối tìm thấy, `direction` = regex. Model `Claim` ([domain/models.py](../../src/quantum_gw/domain/models.py)) **không có** `metric_variant`, `measurement_basis`, `organizational_boundary`, `technology`, `denominator`. | Không có intermediate representation cho "numeric fact". "99% tỷ trọng" và "24% tăng sản lượng" cùng là `(x, '%')` trong bucket `emissions`. → **RQ2/RQ3, N1** |
| 2 | **Comparison eligibility quyết ở đâu? Có IR hay so trực tiếp?** | So trực tiếp trên tuple, tại `VerificationAgent._numeric_relation` ([verifier.py:324–399](../../src/quantum_gw/agents/verifier.py#L324-L399)) và `_numeric_comparison` (415–469). Điều kiện: (a) đơn vị canonical **bằng nhau**, số trần bị loại (`_compatible_units` 589–596); (b) câu bằng chứng chứa ≥1 term taxonomy của `claim.metric` (`_metric_sentences` 529–535); (c) tập Scope 1/2/3 bằng nhau nếu cả hai nêu (335–346); (d) không thuộc năm khác (`_dated_to_other_year` 612–619). Chọn cặp bằng **relative error nhỏ nhất** (`_closest_pair` 599–609). Dung sai `precision-v1` theo độ chính xác công bố, trần 10% ([settings](../../configs/default.yaml)); ngưỡng CONTRADICTS **hằng số 0.35** (dòng 373, 456). Ghi `policy_id`, `tolerance_used`, `calculation_method` vào `computed_values`. | B9 đã có phần dung sai theo precision (không còn 12% toàn cục) ✅. Nhưng eligibility chỉ có unit + term + scope + năm; **không** có variant/boundary/basis; và 0.35 chưa có căn cứ. → **N1, RQ3** |
| 3 | **Cue N2: sentence window, token window hay regex global?** | Câu-level. `StanceLexicon` biên dịch cue thành regex ranh giới từ trên chữ **có dấu** (`_phrase_re` [stance.py:90](../../src/quantum_gw/verification/stance.py#L90)); `_cues_in_claim_sentences` (219–258) tách câu, cue *refutes* chỉ tính trong câu chia sẻ ≥1 content token với claim (hoặc câu "phán quyết về tuyên bố" nếu authoritative); cue *supports* cần chung bigram âm tiết với chính claim; `benign` bị strip trước; phủ định trong cửa sổ 4 từ (`_NEGATION_WINDOW`). **Authoritative** = `source_type ∈ {legal, standard}` **hoặc** đoạn chứa cue *adjudicative* (169–170). | **Root cause N2 đã xác định từ run:** đoạn BCPTBV HPG tr.78 (source_type `internal`) chứa "cơ quan quản lý" → cue adjudicative → đoạn thành "authoritative" → "thiếu" trong "hành vi thiếu minh bạch" được tính vì câu chia sẻ token với claim (claim lại là mảnh ghép qua ranh giới chunk). Lỗi ở **danh sách adjudicative quá rộng** ("cơ quan quản lý", "kết luận", "quyết định của") chứ không phải ở cửa sổ. |
| 4 | **Extractor N3: có scoring/confidence hay chỉ rule?** | Rule + một công thức confidence hình thức ([claim_extractor.py:166](../../src/quantum_gw/agents/claim_extractor.py#L166)): `0.48 + 0.18·(có số) + 0.12·(không generic)`, ngưỡng `minimum_confidence 0.40` → **không bao giờ loại** (giá trị nhỏ nhất 0.48). Gate thật: khớp term claim_type (bắt buộc), `heading_reason` (55), `generic_without_commitment`, `is_vague` (nhưng `include_vague_claims: true`). **`numbers = parse_numbers(sentence)` đếm cả năm**: "…năm 2025…" → `[(2025, None)]` → câu được coi là "có số liệu", không vague, đủ điều kiện commitment. | Root cause N3: năm được coi là số ở extractor (verifier đã loại năm ở `_measurements` 626–632 nhưng extractor thì chưa). Confidence hiện không mang thông tin → không dùng để báo "claim precision". → **RQ1** |
| 5 | **PARTIAL rationale sinh ở đâu?** | Template cứng trong `_status` ([verifier.py:130–224](../../src/quantum_gw/agents/verifier.py#L130-L224)); nhánh 201–212 là hai chuỗi **tiếng Anh** cố định (168/181 PARTIAL của HPG rơi vào đây); các nhánh khác tiếng Việt. Không tham chiếu thuộc tính thiếu. Thông tin "thuộc tính nào thiếu" **đã có** ở risk components (`scorer.py:33–54`: specificity/quantitative/baseline/period/scope_boundary) nhưng verifier không đọc. | N3(b) làm được bằng cách sinh rationale từ 5 component đã có, không cần model. |
| 6 | **SUPPORTED có bao nhiêu route?** | **Một** route trạng thái ([verifier.py:164–178](../../src/quantum_gw/agents/verifier.py#L164-L178)): ≥1 đoạn có `relation == SUPPORTS`, `doc_id ≠ claim.source_doc_id`, `score ≥ partial_support_score`. `SUPPORTS` sinh từ 2 nguồn: (i) số khớp cùng unit/metric/scope/kỳ (`_numeric_relation` 368–372); (ii) cue ủng hộ trong câu chung bigram với claim (stance 203–216) — nhưng nếu claim **có số** thì cue bị hạ xuống PARTIAL (verifier 289–296; test `test_quantified_claim_is_not_supported_by_a_phrase`). (iii) LLM judge (`llm_stance: off`). | Root cause N4: claim **không có số** + 1 cue ("chứng nhận"/"xác nhận") ở tài liệu khác → SUPPORTED. Không có kiểm tra thuộc tính. → **RQ7** |
| 7 | **Severity: rule table hay công thức tổng?** | Công thức **cộng dồn 9 thành phần** ([scorer.py:33–85](../../src/quantum_gw/agents/scorer.py#L33-L85)), band tuyệt đối từ `configs/scoring_v1.yaml`: LOW <25, MEDIUM 25–49, HIGH 50–74, CRITICAL ≥75. Ví dụ tính tay cho claim PARTIAL không số, không metric, không baseline/kỳ/scope, chỉ nguồn nội bộ, có từ mơ hồ: 6+12+8+8+8+7+8+0+8 = **65 → HIGH**. Test `test_rubric_calibration.py` (6) chỉ kiểm cấu trúc rubric (tổng max = 100, band liền), **không** kiểm calibration. | Root cause N5: thiếu-thuộc-tính, thiếu-bằng-chứng và mâu-thuẫn được cộng cùng thang → evidence insufficiency bị đọc như likelihood. → **RQ8** |
| 8 | **Legal: clause retrieval trước hay condition matching trước?** | Không retrieval. `LegalChecker.check` ([legal/checker.py:98–200](../../src/quantum_gw/legal/checker.py#L98-L200)): resolve `as_of` theo check_mode → issue từ `CLAIM_TYPE_TO_ISSUE` → `corpus.applicable(issue, as_of)` (registry có `text_acquisition`; văn bản chưa trích toàn văn → `blocked_sources`) → **nếu không có văn bản usable → INSUFFICIENT** → `rule_pack.for_claim(claim_type, issue, as_of)` → `evaluate_condition` ([legal/rules.py:147](../../src/quantum_gw/legal/rules.py#L147)): `terms_present` (keyword) hoặc `manual` → `combine`. Rule pack `vn-green-v0.1-draft`: **đúng 1 rule**, `source_clauses: []` (draft_unbound), `claim_types: [green_project, green_taxonomy_eligibility]` — không có claim HPG nào thuộc loại này. | 181/181 INSUFFICIENT là **đúng theo thiết kế** (không có rule cho emissions/energy/waste), không phải lỗi runtime. B7 = viết rule cho claim_type có trong dữ liệu (kiểm kê KNK theo QĐ 13/NĐ 06; mục 6 Phụ lục IV TT 96). → **RQ9** |
| 9 | **RRF fusion những retriever nào, weights cố định?** | `HybridRetriever` ([retrieval/hybrid.py:32–180](../../src/quantum_gw/retrieval/hybrid.py#L32-L180)): 2 ranking — BM25 (`_bm25` 142) và "semantic" = **TF-IDF char n-gram 3–5 cosine** ở chế độ `lite` (53, 159–172), hoặc dense nếu có embedder. RRF (125–140) chỉ **đổi thứ tự**, `rrf_k = 60` cố định, `score` báo ra vẫn là weighted 0.55/0.45; `candidate_k 30 → top_k 5`; `floor_k 3` giữ ứng viên dưới ngưỡng có cờ `below_threshold`. | Ở baseline, "hybrid" = **hai bộ lexical** (từ + ký tự). Câu chữ đúng cho slide: *"BM25 + char n-gram TF-IDF, hợp nhất RRF; adapter dense/rerank có sẵn nhưng chưa bật"*. → **RQ4** |
| 10 | **`embedding: local` là adapter thật hay placeholder?** | Adapter thật: `BGEM3Embedder` ([retrieval/embeddings.py:17](../../src/quantum_gw/retrieval/embeddings.py#L17)) qua `FlagEmbedding.BGEM3FlagModel`, `TEIEmbedder` cho HTTP; `build_embedder` (45) fallback về lite kèm warning nếu import lỗi. **`FlagEmbedding` chưa cài trong `.venv`** (kiểm tra 22/09: `ModuleNotFoundError`). Device mặc định `cuda`. | RESEARCH-BACKED – NOT IMPLEMENTED (chưa chạy lần nào trên máy dev). Cần: cài, chạy CPU, đo. |
| 11 | **Reranker interface có implementation chưa?** | Có: `BGEReranker` (FlagReranker), `TEIReranker`, `NoopReranker` mặc định ([retrieval/rerank.py](../../src/quantum_gw/retrieval/rerank.py)); test `test_reranker_local_falls_back_gracefully_without_flagembedding`. Chưa cài, chưa đo. | Như Q10. → **RQ5** |
| 12 | **LLM gateway hỗ trợ structured JSON ở task nào?** | Không có JSON mode/native structured output: schema được **nối vào prompt** (`schema_instruction` [providers/base.py:74](../../src/quantum_gw/providers/base.py#L74)) và parse bằng regex `extract_json` (81–87). Gateway hiện chỉ được gọi bởi `LLMStanceJudge` ([verification/llm_judge.py:68](../../src/quantum_gw/verification/llm_judge.py#L68)) và endpoint health. Task `claim_extraction`, `claim_normalization`, `retrieval_query_generation` có trong `routing.yaml` nhưng **không có code path nào gọi** (grep 22/09). | **Đính chính bản dự thảo §3.1:** pipeline đang chạy **không có** bước "Claim normalization"; 5 thuộc tính đến từ heuristic extractor. LLM hiện = ablation candidate đúng nghĩa. → **RQ6** |
| 13 | **OCR có code thật không?** | Có: [parsers/documents.py:51–71](../../src/quantum_gw/parsers/documents.py#L51-L71) — PyMuPDF lấy text; trang < 40 ký tự native và `ocr_enabled` → `TesseractOCR.ocr_page` (`parsers/ocr.py`), ghi `metadata.ocr`. Bảng: pdfplumber `extract_tables` → chunk text `"TABLE\nô | ô"` (90–110), **không** có `(row, col)`. Tesseract chưa cài trên máy dev; 2 PDF HPG có text layer nên nhánh OCR chưa chạy lần nào tại chỗ (E7). | OCR: IMPLEMENTED – NOT VALIDATED. Ô bảng: chưa có provenance cấp ô (E3) — bảng đã là chunk riêng nên "ít nhất trích tới bảng/trang" là làm được. |
| 14 | **RunStore có primitive nào reuse?** | **Đã có**: `RunStore` read-only trên `runs_dir/<run_id>/{manifest.json,result.json,audit.jsonl,evidence_pack.md}` ([storage/runs.py](../../src/quantum_gw/storage/runs.py)), `label.json`; API `GET /v1/runs`, `/v1/runs/{id}`, `/v1/runs/{id}/export?format=json\|md` ([api.py:247–300](../../src/quantum_gw/api.py#L247-L300)) — docstring ghi *"PDF is not produced yet"*; UI có `HistoryPage.jsx`, `ExportPage.jsx`. Reviews: append-only JSONL (`storage/reviews.py`). | **Đính chính snapshot 22/09 §2 tiêu chí 4:** "chưa có xuất PDF/JSON, RunStore" → đúng là **có RunStore + export JSON/MD, thiếu PDF**. E2 gần xong; E1 còn PDF. |
| 15 | **233 test cover gì mạnh, gì yếu?** | Đếm theo file (22/09): legal infra 65 (`test_legal_layer` 35, `test_legal_gates` 20, `test_legal_pipeline_wiring` 10); **verdict traps 29**; review workflow 19; document store 15; routing/gateway 19; stance 8; CLI 8; real-case eval 7; rubric structure 6; retrieval floor/fusion 9 (dữ liệu tổng hợp). **Gần như không có:** claim extractor semantic (1 + 4 bilingual), calibration severity (0), Recall@k trên gold (0), nội dung rationale (0), OCR (0), ô bảng (0), e2e 1. | Test mạnh ở *hạ tầng* (legal, review, store), yếu ở *chất lượng verdict* — khớp với việc golden 4/4 không bắt được N1–N5. |

---

## 3. Bảng nối research ↔ code ↔ test ↔ dữ liệu ↔ thí nghiệm ↔ nghiệm thu

| RQ | Yêu cầu | Cơ sở nghiên cứu | Code path hiện tại | Test hiện có | Bằng chứng dữ liệu thật | Gap | Thí nghiệm tiếp theo | Nghiệm thu | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RQ1 Claim | Định nghĩa "auditable green claim" | FEVER/SciFact/AVeriTeC (claim worth checking), ClaimBuster (check-worthiness) — `docs/research/` | `claim_extractor.run` (taxonomy match + heading/generic/vague gate; năm đếm là số) | 1 + 4 + traps heading | HPG 181 claim, 66 có số, có câu thư CEO | Không có sentence-level gold; confidence không mang thông tin | Quỳnh + Thảo gán 100 câu: auditable / vague-environmental / non-claim / boilerplate; đo P/R/F1 extractor trước–sau khi (a) loại năm khỏi `numbers`, (b) yêu cầu ≥1 semantic commitment | F1 báo theo lớp; extractor mới không giảm recall lớp auditable > 5 điểm | IMPLEMENTED – NOT VALIDATED |
| RQ2 Metric | Schema semantic identity của numeric fact | GHG Protocol ch.7, ISO 14064-1 §9, IFRS S2, FEVEROUS numeric cells; GRI 302/305 | Không có IR; tuple `(value, unit, half)` + `claim.metric` 6 bucket | traps `cross_metric`, `numbers_within_metric`, `scope_boundary` | 5/8 CONTRADICTED HPG là cross-variant | Thiếu variant/basis/boundary/technology/denominator | Thiết kế `NumericFact` cho 5 family (GHG, energy, water, waste, green finance); gán tay 50 fact từ HPG + 2 DN khác; đo field-level F1 rule vs LLM (RQ6) | Schema có trong `domain/models.py`; F1 boundary/basis ≥ 0.8 trên 50 fact | OPEN QUESTION |
| RQ3 Comparison | Khi nào hai fact được so | như RQ2 + ISA 500 (sufficient appropriate evidence) | `_numeric_relation`, `_closest_pair`, `_compatible_units`; ngưỡng 0.35 hằng | traps precision (3), scope, other-year | N1: 7/8 sai | Eligibility thiếu 3 chiều; "cùng bảng" chưa xử lý; 0.35 chưa có căn cứ | Gold **50 cặp numeric** nhãn Comparable / Not comparable / Comparable-after-normalization / Ambiguous; sweep ngưỡng CONTRADICTS; **không** dùng rule tuyệt đối "cùng bảng = không mâu thuẫn" (target vs actual cùng bảng là mâu thuẫn hợp lệ) — cần quan hệ row/column | Pair-eligibility accuracy ≥ 0.9; HPG 0 CONTRADICTED sai sau soát tay; 4 real case giữ | OPEN QUESTION (P0) |
| RQ4 Retrieval | Dense có tăng Recall@k không | Zhao et al. (RAG có thể tệ hơn; recall ↔ correctness), BGE-M3 paper | `HybridRetriever` lite = BM25 + char-TF-IDF; adapter BGE-M3 có, chưa cài | fusion 4, floor 5 (tổng hợp) | 0 | Không có gold evidence → không đo được | Sau ≥20 cặp gold: Recall@3/5/10, MRR, false-evidence rate, s/claim CPU cho B0 lite vs B1 +BGE-M3 | Báo bảng theo k; chỉ bật mặc định nếu ΔRecall@5 ≥ +10 điểm và ≤ 2× thời gian | RESEARCH-BACKED – NOT IMPLEMENTED |
| RQ5 Ranking | Reranker cải thiện downstream hay chỉ ranking | "Lost in the middle", bge-reranker-v2-m3 | `BGEReranker`/`NoopReranker`, `candidate_k 30 → final_k 5` | 2 (noop, fallback) | 0 | Chưa cài, chưa đo | B2 = B1 + rerank; đo ΔRecall@5, Δverdict accuracy, latency | Chỉ nói "reranker giúp" khi Δverdict accuracy > 0 trên hold-out | RESEARCH-BACKED – NOT IMPLEMENTED |
| RQ6 LLM | LLM normalization hơn heuristic bao nhiêu | Structured extraction với LLM (schema-in-prompt); ablation per-module | Gateway + `schema_instruction`; **không có** task normalization được gọi | gateway/routing 19 (mock) | 0 | Không có code path; không có JSON mode | Viết `claim_normalization` gọi gateway trả JSON 5 thuộc tính (+ variant/boundary theo RQ2); Quỳnh soát 30 claim; đo field F1, s/claim, số call | Ngưỡng nội bộ +15 điểm F1 (management gate, không phải chuẩn học thuật); nhãn "AI đề xuất" trên UI | RESEARCH-BACKED – NOT IMPLEMENTED |
| RQ7 Stance/verdict | Ranh giới SUPPORTED / PARTIAL / INSUFFICIENT | FEVER NEI, AVeriTeC conflicting; ADR 0004/0005 | `_status` 1 route SUPPORTED; PARTIAL 4 nhánh; `_absence` theo `corpus_completeness` | traps 29, real case 4 | N4: 3/3 SUPPORTED chỉ nhờ cue | Không có kiểm tra thuộc tính cho SUPPORTED; "≥3/5" chỉ là đề xuất | Threshold sweep số thuộc tính khớp trên gold; đo κ giữa Quỳnh–Thảo cho PARTIAL vs INSUFFICIENT trước khi gán 60 | Convention ghi vào `LABELING_CONVENTIONS.md`; κ ≥ 0.7 trên 20 cặp thử | IMPLEMENTED – NOT VALIDATED |
| RQ8 Risk | Severity biểu diễn gì | Explainable AI for auditors (ACCA/ICAEW), ESMA guidelines (không cáo buộc) | Cộng dồn 9 component, band tuyệt đối | rubric structure 6 | N5: 65 HIGH trên DN control | Trộn evidence insufficiency + contradiction strength + materiality | Tách `verification_status` / `evidence_strength` / `contradiction_strength` / `materiality` trong `RiskAssessment`; trước mắt cap MEDIUM cho PARTIAL-thiếu-thuộc-tính (D-2026-09-22-03) | HPG HIGH ≤ 5%, mỗi HIGH có lý do thuộc {numeric contradiction, authoritative cue}; 4 real case band không giảm | IMPLEMENTED – NOT CALIBRATED |
| RQ9 Legal | Rule nào thành policy-as-code mà không vượt bằng chứng | Regulation-as-Code (OpenFisca/Catala), `docs/research/` legal | `LegalChecker` + rule pack 1 rule draft_unbound | 65 (hạ tầng) | 181/181 INSUFFICIENT (đúng thiết kế) | Không có rule cho claim_type có trong dữ liệu; finding 4 mức chưa tách | Thảo viết 3 rule có input extractable + positive/negative fixture: (1) đối tượng kiểm kê KNK theo QĐ 13, (2) kỳ báo cáo NĐ 06→119→83, (3) mục 6 Phụ lục IV TT 96 trường bắt buộc; finding 4 mức: *applicable requirement found / evidence satisfies / evidence does not establish / potential mismatch* | 3 finding ≠ INSUFFICIENT trong `test_legal_layer`; UI không dùng chữ "vi phạm" | infra PROVEN; substance NOT VALIDATED |
| RQ10 Utility | GreenScan tiết kiệm bao nhiêu thời gian tìm evidence | Human-AI audit studies; hồ sơ V1 "8–12 h → 2,5 h" là giả thuyết | UI evidence panel + deep-link trang | review workflow 19 | 0 | Chưa đo người | Protocol 1 trang (Quỳnh): 20 claim, tay vs với GreenScan, đo thời gian + evidence tìm đúng; n nhỏ ghi rõ | Số giờ/báo cáo có CI; dùng cho Vòng 3 | OPEN QUESTION |

---

## 4. Đính chính bản dự thảo 22/09 theo audit

| Bản dự thảo nói | Code nói | Xử lý |
| --- | --- | --- |
| §3.1 pipeline đang chạy có bước "Claim normalization" | Không có; 5 thuộc tính từ heuristic extractor; task chỉ tồn tại trong `routing.yaml` | Bỏ khỏi sơ đồ "đang chạy"; đưa vào sơ đồ "đang nghiên cứu" |
| §3.1 "Numeric + legal rule layer" | Numeric: có, deterministic. Legal: 1 rule draft, không bind clause, không áp cho claim_type HPG | Ghi "legal layer: hạ tầng + 1 rule draft" |
| §7 "Không thể áp dụng rule 'same table = never contradiction'" | Đúng — ISSUES N1(b) viết 22/09 sáng quá tuyệt đối | **N1(b) sửa:** cùng câu/bảng → không tự động là mâu thuẫn; chỉ so khi xác định được quan hệ (target↔actual, base↔current), còn lại PARTIAL "cần reviewer" |
| §9 "SUPPORTED ≥3/5 attributes" là kết luận | Chỉ là đề xuất trong ISSUES N4 | Gọi là giả thuyết; chốt sau sweep (RQ7) |
| §14 "prototype thiếu RunStore" (từ snapshot) | RunStore + export JSON/MD đã có; thiếu PDF | Đính chính snapshot §2 (mục 8 dưới) |
| §5.1 RQ-O1 "output có deterministic hoàn toàn không" | Manifest có `deterministic_seed: 0`, `config_hash`, `input_hashes`; chưa có test chạy 2 lần so `result.json` | Thêm test `test_two_runs_same_inputs_identical_result` (không cần gold) |

---

## 5. Tuyên bố được phép / chưa được phép trước BGK (đã đối chiếu code)

**Được phép (có artifact):**
- "Pipeline chạy end-to-end trên PDF doanh nghiệp Việt Nam; 2 tài liệu 11 MB trong ~79 s trên máy dev CPU" (`benchmark/baseline_2026-09-22.json`).
- "Mọi run có manifest hash input/config/pipeline để tái hiện; mọi evidence có trang."
- "Số học là deterministic, dung sai theo độ chính xác công bố (`precision-v1`), không giao cho LLM."
- "Hệ thống abstain: UNSUPPORTED chỉ khi corpus được xác định đủ; còn lại INSUFFICIENT" (`_absence`, ADR 0005, test 2 nhánh).
- "Chúng tôi phát hiện false contradiction trên case thật và biến chúng thành 29 regression trap."
- "4 case có phán quyết (SEC/tòa) khớp status 4/4."
- "Kiến trúc hỗ trợ dense retrieval và reranking (adapter BGE-M3 / bge-reranker-v2-m3 / TEI); cấu hình baseline hiện dùng BM25 + char n-gram + RRF."

**Chưa được phép (chưa có số đo):**
- "accuracy X%", "claim extraction accuracy", "reranker tăng độ chính xác", "BGE-M3 tốt hơn BM25", "LLM tốt hơn heuristic", "legal AI xác định vi phạm", "AI phát hiện greenwashing chính xác", "quantum tối ưu hệ thống", "tiết kiệm 8–12 h → 2,5 h".

---

## 6. Bốn gate thay cho "% readiness"

Snapshot 22/09 có ước lượng điểm (~66–68) để xếp ưu tiên nội bộ. Từ nay **không dùng % readiness** trên tài liệu trình bày; dùng 4 gate, mỗi gate gắn với DoD `EXECUTION_PLAN` và test/lệnh kiểm tra.

| Gate | Điều kiện | Kiểm tra bằng | Liên kết |
| --- | --- | --- | --- |
| **A — DEMO SAFE** | 0 false CONTRADICTED trong curated demo; mọi SUPPORTED được người xác nhận; PARTIAL không over-severity; demo từ saved run tái hiện được | N1–N5 đóng; `run_case.py --all`; HPG soát tay; `/v1/runs/{id}` | D1, D2, D3, D13, D14; D-2026-09-22-02/03 |
| **B — DATA DEFENSIBLE** | ≥60 gold, gán đôi, κ, hold-out theo DN, Dataset Card | `data/gold/`, `reports/GOLD_SET_v1.md`, `DATASET_CARD_v1.md` | D9 |
| **C — METRICS DEFENSIBLE** | claim F1, Recall@k, stance macro-F1, citation precision, latency, error analysis, ablation B0/B1/B2 | `EVALUATION_REPORT_v1.md` | D8, D10 |
| **D — DEPLOYMENT DEFENSIBLE** | bảng runtime/tài nguyên đa cấu hình, chạy offline không key, sơ đồ bảo mật, kế hoạch pilot | `docker compose up` máy sạch; bảng chi phí | D11, S4.3 |

Slide chỉ đóng băng khi A–D đều xanh; nếu 10/10 chưa xanh gate nào thì slide nói đúng trạng thái gate đó.

---

## 7. Ưu tiên thực thi (thay §6 snapshot ở mức chi tiết; thứ tự không đổi)

| P | Việc | Điều kiện vào | Điều kiện ra |
| --- | --- | --- | --- |
| **P0 Correctness** | N1 (eligibility 3 chiều + quan hệ cùng bảng) → N4 (SUPPORTED cần số hoặc thuộc tính) → N5 (cap + tách chiều) → N2 (thu hẹp adjudicative; cue chỉ authoritative khi `source_type` legal/standard **hoặc** adjudicative *và* có statement noun) → N3 (loại năm khỏi `numbers`; rationale từ 5 component) | baseline 22/09 | mỗi issue: trap mới xanh; HPG chạy lại ghi `benchmark/progress_<ngày>.json`; 4 real case giữ |
| **P1 Measurement** | 20 gold + κ thử; 50 cặp numeric (RQ3); 100 câu claim (RQ1); test determinism 2 run | P0 đang chạy song song (không phụ thuộc code) | số đầu tiên có CI, báo theo DN |
| **P2 AI ablation** | cài FlagEmbedding, chạy CPU; B0/B1/B2 Recall@k; `claim_normalization` gọi gateway; NLI tuỳ chọn | ≥20 gold | bảng ablation; chỉ promote module có Δ dương |
| **P3 Productization** | export PDF (JSON/MD đã có); panel pháp lý; docker cả stack; video | Gate A xanh | D5–D7, D11 |

---

## 8. Việc ghi sổ đi kèm (22/09)

- `ISSUES_REGISTER_2026-09.md` mục N: cập nhật root cause N2/N3 theo audit, sửa N1(b).
- `DECISIONS_LOG.md` D-2026-09-22-06: bốn trạng thái + bốn gate thay % readiness.
- `ROUND2_READINESS_2026-09-22.md`: thêm mục "Đính chính sau audit code" (không sửa số).
