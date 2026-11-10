# R7: Báo cáo thiết kế pipeline, gói nguồn nghiên cứu, sản phẩm và UX

*Viết 04/11/2026 cho Chung kết 10/11. Quy ước đường dẫn: `TXT/` = `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt\` (bản text trích tạm; thư mục phiên có thể bị xoá); `REPO/` = `D:\Sinh viên CNhan\AI quantum\docs\greenscan-ai\GreenScan-AI\`. Viết tắt: **BC** = báo cáo thiết kế pipeline, "tr." = trang của BC; **SP0x** = file gói nguồn 0x; **KH31** = `REPO/docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`; **AUDIT** = `REPO/docs/00-project/AUDIT_HE_THONG_2026-10.md`.*

**Nguồn đã đọc**
- `TXT/thiet_ke_pipeline_greenwashing.txt`: toàn văn 19 trang. Bảng bị vỡ mỗi ô thành một dòng khi trích; đã đọc ghép theo cột. Số chú thích [1]–[63] trỏ tới danh mục URL ở tr.17–19.
- `TXT/source_pack_00…06_*.txt`: đủ 7 file (text của DOCX 13/08). Vài bảng mất tiêu đề cột, đã ghép theo ngữ cảnh.
- `TXT/giai_thich_pipeline_de_hieu.txt`: toàn văn.
- `REPO/docs/02-product/`: AUDITOR_WORKFLOW_POSITIONING, USER_PERSONAS, MVP_SCOPE (toàn văn); OUTPUT_SPEC (§1–3, §6.4–6.5, §8, §11); USER_STORIES (§1–2, E-04, US-08.03, §11–14).
- `REPO/docs/05-ui/`: UI_REVIEW_20260808, UI_V2_REVIEW_2026-09-20 (toàn văn); PRODUCTION_UI_SPEC_2026-09-20 (§0–3, §4.6–4.7, đầu §5 S3, §7); UX_FLOW (§3–4); HUMAN_REVIEW_SPEC (§3–5, §8, §12–14); DASHBOARD_SPEC (§1–2, §5.2, §5.8–10); EVIDENCE_CARD_SPEC (§1, §5.3, §5.6, §6–10).
- `REPO/docs/00-project/KE_HOACH_PHAN_BIEN_HE_THONG_VA_EDITOR_2026-10-14.md`: toàn văn.
- Kiểm chéo: KH31 (§0–4, §10); AUDIT (§0–1, §8–13); `TXT/ho_so_vong1.txt` (dòng 70–75, 280–292, 360–374); `REPO/src/quantum_gw/studio/suggest.py` (docstring, nhãn 4 loại, luật OC-01…OC-05); danh sách route trong `REPO/src/quantum_gw/api.py` và `api_studio.py`; `REPO/configs/default.yaml` (retrieval), `priority_v1.yaml` (trọng số), `scoring_v1.yaml` (phiên bản); `REPO/docs/04-data-ai/CHUONG_TRINH_THI_NGHIEM_VA_DU_LIEU_v3_2026-10-13.md` (F1–F4, D3, dòng 168–169); `REPO/docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md` (dòng 71).

**Không đọc / không đọc được, và vì sao**
- Mọi tài liệu cụm R7 đã có text, nên không cần trích PDF vào `scratchpad\R7\`.
- Bỏ qua có chủ đích: PRODUCTION_UI_SPEC §4.1–4.5 (token màu, chữ), wireframe chi tiết §5, prompt sinh ảnh §6, phụ lục; các schema JSON của DASHBOARD, EVIDENCE_CARD, HUMAN_REVIEW. Không phục vụ câu hỏi BGK.
- **Không mở bản gốc** các paper và URL trong BC và gói nguồn (FTC, EU, CMA, R1–R10…). Số lấy từ đó ghi [NGOÀI] và là số thứ cấp. URL trong BC có đuôi `utm_source=chatgpt.com`: BC là bản deep-research do ChatGPT tạo. Kiểm bản gốc trước khi đưa số lên slide.

---

## 1. Tóm tắt từng tài liệu

### 1.1 BC: "Thiết kế pipeline kỹ thuật để phát hiện greenwashing trong claim tiêu dùng, bài phát biểu ESG và báo cáo ESG tài chính" (`TXT/thiet_ke_pipeline_greenwashing.txt`)

**Là gì.** Báo cáo tổng quan đề xuất kiến trúc cho ba loại đầu vào: claim trên sản phẩm, bài phát biểu ESG, báo cáo ESG/tài chính. Có 63 chú thích; nguồn chính là FTC Green Guides, Directive (EU) 2024/825, IFRS S1/S2, GHG Protocol, ISO 14040/44, ISO 14067, PEF và các bộ dữ liệu NLP.

**Luận điểm chính**
1. Không dừng ở phân loại đúng/sai. Phải đi hết chuỗi mười mô-đun: tách claim → chuẩn hoá → truy hồi → xác minh → chọn baseline → ranh giới vòng đời / biên kiểm kê → kiểm tra định lượng → mâu thuẫn → chấm rủi ro → giải thích có provenance (tr.1, tr.3–7).
2. Khung pháp lý "dịch thẳng" thành nhãn (tr.1–2):
   - FTC: bốn cờ đỏ: claim chung chung; so sánh không nêu baseline; seal/chứng nhận không nêu cơ sở; ngụ ý lợi ích tổng thể khi bằng chứng chỉ cho một thuộc tính hẹp.
   - EU 2024/825: thêm claim cho toàn sản phẩm khi bằng chứng chỉ cho một phần, và claim trung hoà khí nhà kính dựa trên bù trừ (offset).
   - IFRS S1/S2 và GHG Protocol: xương sống cho báo cáo (governance, metrics/targets, ranh giới tổ chức, Scope 1/2/3, loại trừ).
   - ISO 14040/44, 14067, PEF: tránh nhầm claim hẹp với claim rộng.
3. Tách ba chế độ UX (tr.3): Consumer Fast Scan (1–3 giây, 2–5 bằng chứng, verdict tạm); Speech Guard (2–10 giây mỗi đoạn, dòng thời gian claim); Report Audit (vài phút, memo có trích dẫn, bảng mâu thuẫn, checklist pháp lý).
4. Chưa có benchmark trưởng thành cho nhãn "greenwashing có/không"; chỉ có dữ liệu cho tác vụ con. Vì vậy xây theo các tác vụ con đo được rồi gộp thành risk model có giải thích (tr.1, tr.17).
5. **Không dùng LLM sinh làm nguồn chân lý đầu tiên cho verdict.** LLM ở lớp chuẩn hoá, tổng hợp, nháp giải thích. Nhãn support/refute/insufficient, comparator, scope, đơn vị và mâu thuẫn neo bằng retriever + NLI + luật/đồ thị (tr.13).
6. Report Audit chỉ gắn rủi ro cao khi **ít nhất hai mô-đun độc lập đồng thuận**, ví dụ verifier bác bỏ + lệch ranh giới (tr.15).
7. Ba tầng giải thích (tr.15): người tiêu dùng (ngắn, ít thuật ngữ); chuyên viên (span claim, đoạn bằng chứng, bảng, comparator, scope, chỗ lệch); gói pháp lý (memo có timestamp, hash tài liệu, model/version, confidence, ghi chú người soát, lý do leo thang).
8. Một "canonical claim object" 18 trường dùng chung: claim_id, source_doc_id, source_span, claim_text, claim_type, entity, environmental_dimension, metric, unit, timeframe, baseline, scope_boundary, modality, evidence_links, verdict, confidence, risk_flags, review_status (tr.7).
9. Tiếng Việt là yêu cầu hạng nhất: PhoBERT cho phân loại/NER, XLM-R hoặc mDeBERTa cho NLI và truy xuất chéo ngôn ngữ, từ điển song ngữ cho "phát thải phạm vi 3", "tín chỉ carbon", "bù trừ", "bao bì"… Nếu dịch máy phải lưu cả bản gốc (tr.16).
10. Lộ trình (tr.16–17): MVP 8–12 tuần. Bước 1 chỉ trả lời hai câu: "đoạn này có claim đáng kiểm không?" và "có bằng chứng hỗ trợ trực tiếp, đủ phạm vi, đúng số không?". Bước 2: case packet nội bộ 100–300 ca. Bước 3: UX phân tầng ngay từ đầu ("risk flags" / "claim events" / "review memo").
11. Giới hạn tự nhận (tr.17): thiếu benchmark công khai có giấy phép rõ; nhiều bộ dữ liệu ESG còn mới; hệ thống không thay kết luận pháp lý. Vụ H&M "Conscious Choice" cho thấy tranh chấp nằm ở việc người tiêu dùng hiểu thế nào.

**Số trong BC** (đều [NGOÀI], chưa đối chiếu bản gốc): CMA khoảng 40% green claim trên web có thể gây hiểu lầm; EC 53% claim mơ hồ, gây hiểu lầm hoặc không có cơ sở, 40% không có bằng chứng (tr.3). Bộ dữ liệu ở tr.4–9 (xem §3). Các "performance target" (p95 < 300 ms/chunk, > 90% điền đủ trường, > 85% chọn đúng baseline, > 95% đúng số, 0 câu không trích dẫn) **là mục tiêu thiết kế BC tự đề xuất, không phải chuẩn** (tr.3). Tài nguyên đề xuất: 1–2 GPU 24 GB trong 50–150 GPU-giờ; 1–4 GPU 40–80 GB cho long-context; 1–3 TB lưu trữ; 2–4 người gán + 1 người phân xử; IAA κ/α ≥ 0,75 cho nhãn cấp cao (tr.13–15).

**Liên quan GreenScan.** Đây là bản thiết kế gốc. GreenScan giữ phần lõi: evidence-first, LLM không phán quyết, tách "đủ bằng chứng" khỏi verdict, provenance, đồng thuận hai đường, tự dựng benchmark, chia tập theo công ty. GreenScan **khác có chủ đích** ở bốn điểm: chỉ làm Report Audit cho báo cáo doanh nghiệp Việt Nam và thêm editor phòng ngừa (Studio); xác minh bằng số học tất định + luật thay vì NLI; chạy CPU ngoại tuyến thay vì cụm GPU; không làm LCA vòng đời sản phẩm. Đối chiếu chi tiết ở 1.2.

### 1.2 Bảng đối chiếu khuyến nghị (BC, gói nguồn) với GreenScan, trạng thái 01/11

Ký hiệu: ✅ đã làm · ◐ làm khác hoặc một phần · ✗ chưa làm · ⊘ cố ý không làm.

| # | Khuyến nghị (nguồn) | GreenScan | Vì sao / bằng chứng |
|---|---|---|---|
| 1 | Không phân loại nhị phân; nhãn theo taxonomy (BC tr.6, tr.13; SP01 §2) | ✅ verdict 5 mức `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE` | OUTPUT_SPEC §3.2. Nhưng HPG phẳng: 153/156 PARTIAL (KH31 §2 F1) |
| 2 | Ba chế độ UX Consumer / Speech / Report (BC tr.3) | ⊘ chỉ Report Audit, thêm Studio soạn thảo phòng ngừa | Phạm vi Vòng 1: tuyên bố môi trường định lượng của doanh nghiệp niêm yết. Consumer cần đọc ảnh/seal, Speech cần ASR. Thể lệ ưu tiên mô hình đơn giản chạy ổn định |
| 3 | Tách claim bằng RoBERTa / DeBERTa / PhoBERT (BC tr.10) | ◐ sản phẩm dùng luật + lexicon song ngữ (`configs/taxonomy.yaml`); học trò e5-base macro-F1 0,71–0,73 trên nhãn Claude, **chưa gắn vào sản phẩm** | Chưa có gold người. Luật: P 0,54 / R 0,70 so với nhãn Claude (KE_HOACH_PHAN_BIEN §1) |
| 4 | Chuẩn hoá claim theo schema (metric, unit, scope, timeframe, comparator), abstain khi thiếu (BC tr.4) | ◐ `Claim` có metric, values, units, period, baseline, scope, direction, is_vague, is_future_commitment; bộ đọc IR Qwen3 + `irlib.ground()` (AG-1) đặt sau cờ | Lỗi chuẩn hoá F4: cường độ vs tuyệt đối, mẹ vs tập đoàn, ngưỡng 0,35… (KH31 §2) |
| 5 | Hybrid retrieval BM25 + SPLADE + dense + ColBERTv2; chunk 150–350 token (BC tr.11) | ◐ mặc định BM25 + n-gram ký tự, gộp RRF k=60, trọng số 0,55/0,45, 30 ứng viên, giữ 5, sàn 3; bge-m3 và bge-reranker-v2-m3 có adapter nhưng **tắt** | Laptop ngoại tuyến; token hiếm ("Scope 2", "tCO2e", số hiệu văn bản) hợp BM25. Benchmark tiếng Việt AG-5 **chưa chạy** (không có thư mục `experiments/AG-5`) |
| 6 | Xác minh bằng NLI (DeBERTa/mDeBERTa), học FEVER → Climate-FEVER (BC tr.11) | ◐ lập trường theo thứ bậc numeric → qualitative_cue → direction → llm → similarity; LLM không quyết định (`llm_stance_decisive=false`) | Verifier học FEVER rơi từ 77,69% xuống 38,78% trên claim khí hậu [NGOÀI] (MO_HINH_CO_QUA_BE_KHONG dòng 71). Claim định lượng cần tính, không cần suy |
| 7 | LLM không là nguồn chân lý cho verdict (BC tr.13; SP02 §4) | ✅ "Models read – Rules decide – Humans review" | D-2026-10-16-01 cấm dùng nhãn Claude để tháo chốt LLM (KH31 §0) |
| 8 | Chọn baseline/comparator tường minh và ngầm (BC tr.5) | ◐ thuộc tính "năm gốc" + Comparability Gate 6 chiều; được phép trả NOT COMPARABLE | Không có mô-đun chọn comparator riêng. 152/156 tuyên bố HPG thiếu năm gốc (AUDIT §1) |
| 9 | Suy luận vòng đời và ranh giới (ISO 14040/44, 14067, PEF) (BC tr.5) | ⊘ LCA · ◐ ranh giới tổ chức và Scope nằm trong cổng so sánh | Đối tượng là báo cáo doanh nghiệp, không phải claim sản phẩm. Lỗi Q2 mẹ/tập đoàn; thiếu chiều `segment` (AG-3, KH31 §10) |
| 10 | Kiểm tra định lượng bằng code executor, chuẩn hoá đơn vị (BC tr.6, tr.12) | ✅ số học tất định: cặp số gần nhất, sai số tương đối, cộng ngang/dọc; thư viện `irlib` | Ví dụ HPG 22.540.603 + 933.876 = 23.474.479 ≈ 23.474.480. Lỗi còn: Q3 ngưỡng che chênh 9–25%, Q5 không cộng ngang |
| 11 | Phát hiện mâu thuẫn đa nhãn: direct / temporal / scope / metric / rhetoric-vs-number (BC tr.6) | ◐ `CONTRADICTED` cần ít nhất một bằng chứng trái trực tiếp (US-04.02); C-guard; không phân 5 lớp | Ưu tiên "0 vu oan": tập ngoài mẫu sạch v1.3, mọi model 0 kết luận sai |
| 12 | Risk model là ensemble hiệu chỉnh, tối ưu calibration (BC tr.6) | ◐ `risk-rubric-v2` 9 thành phần (tất định) + hàng đợi `priority-v1.1` (trọng yếu 40, nghĩa vụ công bố 25, khuyết bằng chứng 25, bất thường 10 nhưng chưa tính) | Không có gold để hiệu chỉnh. Abstain của AG-2 dùng xô xác suất ước trên OOF |
| 13 | Gắn rủi ro cao khi ≥ 2 mô-đun đồng thuận (BC tr.15) | ◐ AG-2: "luật + 4B, bỏ phiếu S đơn độc của luật", trên tập G: độ phủ 0,093, precision 1,0, 0 sai. **Chỉ là thí nghiệm, sau cờ `QUANTUM_VERIFY=dual`** | Đúng tinh thần BC. Chưa đổi verdict sản phẩm trước 10/11 (KH31 §0) |
| 14 | Canonical claim object, provenance là dữ liệu hạng nhất (BC tr.7; SP02 §4) | ✅ ID ổn định, trang/khối; `manifest.json` (run_id, config_hash, input_hashes), `audit.jsonl`, `evidence_pack.md` | Thiếu trích dẫn tới ô bảng (S3.3) |
| 15 | Ba tầng giải thích + gói pháp lý (BC tr.15) | ✅ tương đương: hover card (ngắn) → ClaimDetail (chuyên viên) → giấy làm việc + manifest + JSON vết | Gọi là "hồ sơ rà soát", không gọi "legal packet" |
| 16 | Confidence gating, abstain (BC tr.13–15; SP04 §6 G4) | ✅ `INSUFFICIENT_EVIDENCE` là tính năng; báo precision trên phần dám kết luận + độ phủ + số kết luận sai nguy hiểm | Độ phủ thấp: 0,08–0,25 ngoài mẫu (KH31 §10) |
| 17 | Quy trình người soát, override, audit log (BC tr.1, tr.14) | ✅ `AI_SUGGESTED → HUMAN_REVIEWED → FINALIZED`; `CONFIRM`, `OVERRIDE`, `ABSTAIN`, `REQUEST_EVIDENCE`, `REOPEN`; xuất gold; `ai_override_rate` | Đã test (PRODUCTION_UI_SPEC F9) |
| 18 | Gán nhãn hai tầng, IAA κ ≥ 0,75, 2–4 người gán (BC tr.13) | ✗ 0 gold người (0/88 cặp, 0/79 câu, kiểm 31/10). Thay bằng nhãn Claude hai lượt mù + phân xử và GS-Bench đáp án theo cấu trúc | Thiếu người gán. Từ 04/11, người dùng quyết coi nhãn Claude như một dataset và tự soát lại |
| 19 | Case packet 100–300 ca (claim, snapshot, bằng chứng, comparator, boundary, verdict, lý do) (BC tr.16) | ◐ GS-Bench v1.1: 453 ca (51 B-a + 402 B-b), 7 doanh nghiệp, nhãn bạc | Không có lý do pháp lý hay kết cục của cơ quan quản lý |
| 20 | Chia tập theo công ty và tài liệu (BC tr.14) | ✅ leave-company-out; bootstrap theo công ty | KH31 §4 |
| 21 | Stress test và counterfactual: đổi đơn vị, năm gốc, scope, đảo comparator… (BC tr.14) | ✅ B-b nhiễu có kiểm soát: giá trị / đơn vị / kỳ / Scope / mẹ–tập đoàn / mục tiêu–thành tích / cường độ–tuyệt đối; 17 bẫy `tests/test_verdict_traps.py` | Đúng loại BC đề xuất |
| 22 | Đánh giá đối kháng: chèn đoạn ủng hộ không liên quan, trùng lặp, bản cũ (BC tr.14; SP04 §3 noise 0/1/3/5) | ◐ phát hiện prompt injection (`suspicious_instruction`); retrieval floor gắn `below_threshold` ("chỉ để bác bỏ") | Bộ đo distractor có hệ thống (RET-001) [CHƯA XÁC MINH] |
| 23 | Ablation: bỏ từng mô-đun, LLM-only vs luật (BC tr.14; SP02 T9) | ◐ size ladder 51 ca: luật dám quyết 8/32 (đúng 6), LLM 29–32/32; AG-0 phép thử oracle | MO_HINH_CO_QUA_BE_KHONG; KH31 §2–3 |
| 24 | Bảng/PDF: LayoutLMv3, Donut, TAPAS (BC tr.11–12) | ◐ AG-3 v0 dựng hàng bảng từ toạ độ chữ: HPG tr.39 đủ 10 hàng, cộng dọc khớp 3/3; 7 ca: đúng 3/7 (trang thô 1/7), 0 sai | F3: bảng bị dàn phẳng làm 4/4 model ≥ 26B cùng báo SUPPORTED sai (KH31 §2) |
| 25 | Hồ sơ chính sách có phiên bản, theo dõi policy drift (BC tr.16; SP01 R8) | ◐ registry văn bản có `effective_from`, `as_of_date`, hai chế độ lịch sử/hiện hành, `rule_pack_version` | 0 quy tắc áp được trên 156/156 tuyên bố (F5) |
| 26 | Lưu snapshot, hash; không phát tán toàn văn (BC tr.16) | ◐ sha256 tài liệu, input_hashes; kho 670 tài liệu / 21 doanh nghiệp | Chính sách lưu trữ bản quyền [CHƯA XÁC MINH] |
| 27 | Tiếng Việt hạng nhất: PhoBERT, XLM-R, lexicon song ngữ (BC tr.16) | ◐ lexicon VI/EN; multilingual-e5; Qwen3; OCR `eng+vie` | Không dùng PhoBERT |
| 28 | Fine-tune, LoRA (BC tr.12) | ✗ hoãn: AG-4 QLoRA 1.7B có điều kiện | SP06 FT-001: chỉ sau khi đủ gold |
| 29 | Lớp GAT/causal (BC tr.12) | ⊘ | SP05 watch list; SP06 anti-goal |
| 30 | API tách mode; response có claim_object, evidence[], rule_hits[], numeric_checks[], abstained, provenance (BC tr.15) | ◐ `/v1/analyze/text`, `/v1/analyze/files`, `/v1/jobs/*`, `/v1/reviews*`, `/v1/runs/{id}/export`, `/v1/runs/{id}/workpaper`, `/v1/documents/{id}/page/{p}`, `/v1/legal/corpus`, `/v1/studio/*` | **Không có `/v1/ask`**: chatbot có grounding hứa ở Vòng 1 chưa làm |
| 31 | Monitoring drift + active learning từ người soát (BC tr.16) | ◐ xuất quyết định người soát làm gold; chưa có vòng học lại | |
| 32 | Preventive authoring (SP01 §2 "hậu kiểm → thêm preventive authoring"; SP06 AUTH-001, xếp P2) | ✅ GreenScan Studio (14/10), sớm hơn kế hoạch | Định vị 25/09 cần một "sản phẩm thật" cho người dùng; rào chắn không bịa số |

### 1.3 Gói nguồn nghiên cứu 13/08 (`TXT/source_pack_00…06`)

- **SP00 Master index.** North Star: kiểm chứng tuyên bố môi trường và tài chính xanh ở cấp claim trong tài liệu doanh nghiệp tiếng Việt, định lượng bất định để từ chối kết luận khi chưa đủ căn cứ. Quy tắc: mỗi claim kỹ thuật gắn nhãn Project Source / Verified Research / Working Hypothesis; mỗi thí nghiệm ghi commit, version, dataset snapshot, seed; **không nâng P2 lên P0 khi P0 chưa xong**; không dùng một headline score; thiếu căn cứ thì giữ Insufficient evidence. Ưu tiên 30 ngày: P0 Evaluation foundation, Document/Table, Vietnamese Retrieval, Evidence Sufficiency + Abstain, Numeric Verification; P1 Temporal legal RAG, Evidence UI + Reviewer; P2 Graph/Hierarchical/Quantum-inspired.
- **SP01 Problem landscape.** Đối tượng nghiên cứu là "sustainability claim verification / greenwashing risk verification". Bảng chuyển dịch: detect từ "xanh" → detect claim kiểm chứng được; nhị phân → 5 mức; LLM tự phán → LLM + retrieval + numeric + policy rules + reviewer; "luật nhét vào prompt" → policy corpus có phiên bản + as_of_date + policy-as-code; hậu kiểm → thêm preventive authoring. Tám cơ chế lỗi: vagueness/cheap talk; omission; numeric inconsistency; temporal promise; legal/taxonomy mismatch; use-of-proceeds mismatch; selective disclosure; distracting evidence. Sáu câu hỏi nghiên cứu RQ1–RQ6 (parser, truy xuất tiếng Việt, phân biệt thiếu với mâu thuẫn có hiệu chỉnh, số học tất định vs LLM-only, luật theo phiên bản, UI lấy bằng chứng làm trung tâm). Anti-scope: chấm ESG toàn diện, agent web tự trị, GraphRAG cho mọi truy vấn, fine-tune khi chưa có gold, kiến trúc quantum-first, verdict pháp lý tự động.
- **SP02 Task map T0–T11.** Luồng phụ thuộc T0 Taxonomy → … → T11 UI/Audit; DoD từng workstream; schema tối thiểu 7 nhóm trường (Identity, Semantics, Quantitative, Evidence, Policy, Decision, Audit). Năm nguyên tắc: mỗi stage có contract JSON, stage sau không âm thầm sửa stage trước; LLM chỉ làm ngữ nghĩa, phép tính và luật chạy tất định; provenance xuyên suốt; sufficiency chạy trước verdict, thiếu bằng chứng không mặc định thành Unsupported; chế độ mật phải có đường local/no-egress.
- **SP03 Roadmap 13/08–13/09.** W1 nền đánh giá; W2 parsing + truy xuất tiếng Việt (50–100 trang/bảng khó); W3 sufficiency + numeric + luật theo thời điểm; W4 tích hợp (20–50 ca demo, release gate). Rủi ro tiến độ: tối ưu model khi metric chưa ổn; thêm GraphRAG/agent vì "trông hiện đại"; dùng LLM-as-judge làm metric duy nhất; trộn lỗi parser với lỗi truy xuất; gán nhãn cấp doanh nghiệp; để UI thành leaderboard.
- **SP04 Evaluation & release gate.** Bốn split (dev, test/hold-out, hard-set, regression); metric và "critical failure" cho từng stage; ma trận ablation truy xuất (BM25/dense/hybrid × RRF/weighted RRF × k 10/20/50 × reranker × final k 3/5/8 × chunk 256/512/1024 × query × 0/1/3/5 distractor); hard-set parser (ô gộp, tiêu đề nhiều tầng, bảng nhiều trang, năm kề nhau dễ tráo, tuyệt đối vs cường độ); 9 mã lý do thiếu bằng chứng (`MISSING_BASELINE`, `MISSING_SCOPE`, `PERIOD_MISMATCH`, `UNIT_DENOMINATOR_MISMATCH`, `SOURCE_TOO_WEAK`, `RETRIEVAL_INCOMPLETE`, `OCR_UNCERTAIN`, `LEGAL_APPLICABILITY_UNKNOWN`, `EVIDENCE_CONFLICT`); release gate G1–G6 (tái lập; không tăng lỗi nghiêm trọng; truy xuất; abstain; 100% verdict demo có source ID; ca rủi ro vào hàng đợi); danh sách log bắt buộc.
- **SP05 Reading map.** Mỗi paper phải sinh ít nhất một hypothesis, baseline, metric, ý tưởng dữ liệu, error taxonomy hoặc quyết định cài đặt. Độ tin cậy A (proceedings/chính thức), B (preprint mới cần kiểm), C (blog/repo). Ưu tiên: R1 distracting evidence; R5 CLARIESG (bảng ESG); R6 truy xuất tiếng Việt; R7 MTRAGEval (câu không trả lời được); R4 PromiseEval. Watch list: GraphRAG, agentic retrieval, LoRA judge, quảng cáo/video đa phương thức, QUBO, phân tích danh mục.
- **SP06 Backlog & DoD.** P0: EVAL-001, DOC-001, RET-001, SUF-001, NUM-001, OBS-001, REG-001. P1: LEG-001/002, VER-001, CAL-001, UI-001, REV-001, SEC-001. P2: RET-ADV, PACK-001, QUBO-001, FT-001, AUTH-001, ANL-001. Anti-goals: không tối ưu một "greenwashing score"; không để LLM tính hay áp luật có thể làm tất định; không coi confidence của model là bằng chứng đúng; không đưa mạng xã hội vào tầng bằng chứng chính. DoD demo đáng tin: một tài liệu thật đi hết PDF → claim → evidence → findings → verdict/abstain → UI citation; click về trang/bảng/ô hoặc điều khoản; thiếu thì ghi thiếu gì; regression report; override có lý do; **demo không phụ thuộc bắt buộc vào Quantum, GraphRAG hay fine-tune**.

**Trạng thái các ưu tiên của gói nguồn tại 01/11**

| Hạng mục | Trạng thái | Căn cứ |
|---|---|---|
| P0 Evaluation foundation | ◐ GS-Bench v1.1 (453 ca); đăng ký trước trong `configs/measurement_decisions.yaml` (agentic_v1…v1_2, ag2, ag3); 17 bẫy; 385 test (14/10). Thiếu gold người | KH31 §4, §10; AUDIT đầu tệp |
| P0 Document/Table hard-set | ◐ AG-3 v0 mới có 7 ca trang 39; chưa có 50–100 trang khó; chưa trích dẫn tới ô | KH31 §10 17:40 |
| P0 Truy xuất tiếng Việt | ✗ AG-5 chưa chạy | không có `REPO/experiments/AG-5` |
| P0 Sufficiency + abstain | ◐ `INSUFFICIENT_EVIDENCE`, `missing_attributes`, mã gợi ý sửa; đo precision/độ phủ; chưa có đường risk–coverage trên gold | PRODUCTION_UI_SPEC F6, F8 |
| P0 Numeric verification | ✅ `irlib` + `ground()` + 9 test hồi quy; bộ kiểm số trong sản phẩm còn lỗi F4 | KH31 §2, §10 |
| P1 Luật theo thời điểm | ◐ khung có, 0 quy tắc áp được | KH31 §2 F5 |
| P1 Evidence UI + Reviewer | ✅ UI v2 + Studio | UI_V2_REVIEW; AUDIT §10 |
| SEC-001 no-egress | ◐ offline mặc định; LLM đám mây chỉ cho tài liệu công khai; test tự động [CHƯA XÁC MINH] | KE_HOACH_PHAN_BIEN §5 |
| AUTH-001 preventive authoring | ✅ Studio (nâng từ P2) | AUDIT §10 |
| P2 Graph / Quantum | ⚪ demo không phụ thuộc | SP06 §6 |

### 1.4 `TXT/giai_thich_pipeline_de_hieu.txt`

**Là gì.** Bản giải thích phổ thông (cho học sinh, khách hàng, người không chuyên) của hình "Target Pipeline".

**Nội dung chính**
- Ẩn dụ "người chấm bài có dẫn chứng": 30% so với năm nào, toàn bộ hay một phần, số gốc ở đâu, có đo cùng cách không, quy định nào đang hiệu lực.
- Ba vai: Models read / Rules decide / Humans review.
- Ba cửa vào: (A) báo cáo doanh nghiệp; (B) bằng chứng độc lập (báo cáo kiểm toán, dữ liệu cơ quan quản lý, HOSE/HNX, registry chứng nhận; báo chí chỉ để tìm số quyết định); (C) luật Việt Nam (QĐ 21/2025/QĐ-TTg; NĐ 06/2022 → 119/2025 → 83/2026; TT 17/2022; QĐ 13/2024), chọn theo ngày hiệu lực.
- Bốn bước đọc: READ DOCUMENTS, FIND CLAIMS, STRUCTURE CLAIM, FIND EVIDENCE.
- Comparability Gate 6 điều kiện; lệch một chiều thì kết quả hợp lệ là "NOT COMPARABLE".
- Năm mức verdict. Risk profile 3 chiều: evidence_strength, contradiction_strength, materiality ("currently undetermined").
- Claim Evidence Dossier: verdict, trang nguồn, phép tính, luật, thiếu gì. Ví dụ HPG 22.540.603 + 933.876.
- Ba điều cố ý không làm: để LLM tự tính rồi tự phán; coi báo chí là bằng chứng quyết định; bịa điểm trọng yếu/tuân thủ.
- Câu nói 20 giây với BGK.
- Ghi rõ: hình là **kiến trúc đích**; dense/rerank chưa bật mặc định.

**Liên quan.** Kịch bản nói với giám khảo không chuyên. Khác thực tế ở hai chỗ: demo chưa có nguồn độc lập (780/780 bằng chứng nội bộ, `has_independent: False`); tầng luật chưa áp được quy tắc nào (xem §5).

### 1.5 `REPO/docs/02-product/` (5 file)

- **AUDITOR_WORKFLOW_POSITIONING (25/09, đang hiệu lực, thay định vị cũ).**
  - Lý do viết: HPG 156 tuyên bố → 153 "khớp một phần" → 154 MEDIUM → 0 ca được gắn cờ. Kiểm toán viên sẽ hỏi "xem cái nào trước?".
  - Người dùng: kiểm toán viên / chuyên viên đảm bảo đang làm tay. Tám việc; ba việc tốn thời gian nhất (dò câu tuyên bố, lật bảng đối chiếu, gõ giấy làm việc) là cơ học nên tự động hoá được; quyết định trọng yếu (việc 7) và ký (việc 8) là của người.
  - Định vị một câu: "tự động hoá **đọc, định vị, ghi chép** để kiểm toán viên dành thời gian cho **xét đoán**, và chỉ ra nên xét đoán ở đâu trước".
  - Thước đo thành công đổi từ "verdict đúng" sang "**thời gian tiết kiệm ở cùng mức tin cậy**".
  - Ba lớp thêm: xếp ưu tiên (4 yếu tố tất định); thủ tục phân tích (chéo năm, chéo doanh nghiệp cùng ngành, chéo tài liệu; cờ "im lặng có chọn lọc"); giấy làm việc có mục "những gì không kiểm và vì sao".
  - Ánh xạ 5 thuộc tính sang cơ sở dẫn liệu ISA: chỉ số → Phân loại; giá trị + đơn vị → Chính xác; kỳ → Đúng kỳ; năm gốc → Chính xác (so sánh); phạm vi → Đầy đủ; "Trình bày" (cherry-picking) chưa có.
- **USER_PERSONAS (07/07, bị thay một phần).** Sáu persona: reviewer/auditor, analyst, cán bộ tín dụng xanh, PO/QA, nhà đầu tư/người tiêu dùng, regulator/giám khảo. Tiêu chí: soát một claim đơn giản dưới 3 phút; analyst tìm top-5 rủi ro dưới 10 phút. "Không được xảy ra": AI bịa bằng chứng; giấu bất định; SUPPORTED khi lệch scope/kỳ/metric; không tìm được nguồn gốc.
- **MVP_SCOPE (07/07).** Luồng 13 bước; 5 tầng kiểm (cụ thể, có bằng chứng, nhất quán định lượng, pháp lý/taxonomy, mâu thuẫn ngoài). Ngoài phạm vi: kết luận pháp lý, kiểm toán toàn diện, crawler web, OCR phức tạp, fine-tune, giám sát thời gian thực. Gate: chỉ SUPPORTED khi bằng chứng truy được, đúng kỳ/scope, không còn mâu thuẫn chưa giải. Chỉ tiêu "bằng chứng bịa: 0". Ngôn ngữ an toàn: "rủi ro" thay "gian lận".
- **OUTPUT_SPEC (07/07).** Bảy tầng đầu ra L1–L7; enum verdict cố định, cấm nhãn kiểu "likely true"; độ mạnh bằng chứng L1–L5; trạng thái review; RiskScore 7 tiêu chí (bản cũ); bốn disclaimer bắt buộc (đánh giá rủi ro; không phải kết luận pháp lý; phụ thuộc tài liệu có sẵn; ca rủi ro cao cần người).
- **USER_STORIES (07/07).** 9 epic, 18 story MVP. US-04.02: CONTRADICTED cần ít nhất một bằng chứng trái trực tiếp. US-08.03: ghi hai người soát cho cùng claim để đo đồng thuận. US-09.02: taxonomy và luật có phiên bản, đổi phải có changelog.

### 1.6 `REPO/docs/05-ui/` (7 file)

- **UI_REVIEW_20260808.** Bác mockup kiểu BI dashboard chấm điểm ESG:
  - bỏ KPI "Nguy cơ cao 73" (người xem đọc thành "73 vi phạm");
  - bỏ biểu đồ "xu hướng rủi ro" (chỉ đo tài liệu nào được tải lên tháng đó);
  - bỏ donut E/S/G (ngoài phạm vi MVP);
  - bỏ hàng đợi logo doanh nghiệp + nhãn High (là bảng xếp hạng trá hình; `company_has_case ≠ document_is_greenwashing ≠ claim_is_greenwashing`).
  - Thêm evidence viewer có trang, checklist 5 thuộc tính, đưa abstain thành tính năng.
- **UI_V2_REVIEW_2026-09-20.** Chuyển 12 màn mockup sang code với nguyên tắc "**không vẽ nút cho thứ máy chủ không làm**": đăng nhập thay bằng ô tên người soát; bỏ tick tiến trình giả; "độ tin cậy 0,72" đổi thành confidence của bước trích xuất; PDF ghi "sắp có"; bỏ công tắc không có backend. Kiểm: build 303 kB JS; SSR 21/21 màn không có từ cấm; pytest 215 passed, 8 xfailed. Lúc đó chưa thử thủ công trên trình duyệt. Luồng demo 7 phút: mở run đã lưu → claims → một claim → Thuộc tính → Bằng chứng → Mở trang → Kiểm tra số → Pháp lý → Rủi ro → Xác nhận/Ghi đè → Xuất.
- **PRODUCTION_UI_SPEC_2026-09-20.**
  - 8 P-rule: P1 đơn vị là claim; P2 bằng chứng trước kết luận; P3 abstain là tính năng; P4 không ngôn ngữ cáo buộc; P5 rủi ro chỉ là gợi ý ưu tiên; P6 giải thích được (badge kèm phương pháp); P7 người quyết, AI đề xuất; P8 tái lập (run_id, rubric, schema).
  - Catalog F1–F13 (đã có / còn lỗi / chưa có).
  - Copy rules: cấm "vi phạm, gian lận, sai phạm, lừa dối, phát hiện greenwashing, xếp hạng"; câu cố định cho abstain và footer.
  - Khả năng tiếp cận: tương phản ≥ 4,5:1, trạng thái không chỉ bằng màu, focus ring.
  - Checklist nghiệm thu mockup.
- **UX_FLOW, HUMAN_REVIEW_SPEC, DASHBOARD_SPEC, EVIDENCE_CARD_SPEC (07/07, tiếng Anh).** Nguyên tắc: evidence before conclusion, reviewer control, traceability by default, phân biệt UNSUPPORTED / INSUFFICIENT / CONTRADICTED; trigger vào hàng đợi; 13 mã lý do của người soát; cảnh báo khi xuất báo cáo còn mục chờ duyệt hoặc chấp nhận claim mâu thuẫn mà chưa mở evidence card; giữ nguyên bản AI khi người sửa. DASHBOARD_SPEC còn "company risk score": đã bị P1/P5 bỏ.

### 1.7 KE_HOACH_PHAN_BIEN_HE_THONG_VA_EDITOR (14/10) và kết quả ở AUDIT §10, §12

- **Khung phản biện** 10 khâu × 5 câu. Gói minh chứng: bảng chỉ số + CI so với ngưỡng đăng ký trước; thư viện ca hỏng; ablation; độ trễ; trạng thái xác minh pháp lý; thử 5 người (thời gian, SUS); demo trước/sau sửa.
- **Tối ưu input:** một ô thả nhận PDF/DOCX/URL/"mã CK + năm"; xem trước chất lượng parse (trang chữ vs trang scan, số câu, thời gian ước); thanh tiến trình theo khâu; nút "Báo cáo mẫu HPG".
- **GreenScan Studio:**
  - Ẩn dụ VS Code: Explorer + panel Problems; tuyên bố gạch lượn sóng đỏ (mâu thuẫn/pháp lý), vàng (thiếu chứng cứ/mơ hồ), xanh (thông tin); hover card; Inspector hiện đề xuất như tracked change; nhật ký và phiên bản.
  - Phím tắt: F8 / Shift+F8 sang lỗi kế/trước; Ctrl+. sửa nhanh; Ctrl+Enter chấp nhận; Esc bỏ; Ctrl+Z hoàn tác.
  - Rào chắn: **không bao giờ bịa số**, chỉ 4 loại đề xuất; mỗi đề xuất có lý do, mã quy tắc, căn cứ kèm nhãn xác minh.
- **Quyết định của Nhân (14/10):**
  - Được sửa: tài liệu đang rà soát (báo cáo doanh nghiệp, giấy làm việc GreenScan). Khoá, chỉ xem: tài liệu bằng chứng (BCTC kiểm toán, văn bản luật, dữ liệu bên thứ ba, chứng nhận). Trường `role: under_review | evidence`.
  - DOCX và PDF đều ưu tiên. PDF xuất ra được dựng lại, **không giữ bố cục gốc** (phải ghi trên giao diện).
  - Offline mặc định. Leo thang LLM khi xác suất < τ hoặc luật–học trò bất đồng, **và** tài liệu thuộc lớp A công khai (B nội bộ, C mật thì chuyển người). Phải báo tỷ lệ leo thang, độ chính xác trước/sau, chi phí/báo cáo.
- **Đã cài và đo (AUDIT §10, §12, 14/10):**
  - `studio/suggest.py`: 4 loại `add_scope`, `placeholder`, `evidence_ref`, `soften`; mọi đề xuất qua `assert_no_new_numbers` (chỉ cho phép số đã có trong câu và số trang của bằng chứng trích dẫn); trượt thì bị loại, không hiện.
  - Luật làm nhẹ OC-01…OC-05: trung hoà các-bon/net-zero → "hướng tới trung hòa các-bon [bổ sung: phần giảm thực tế, phần bù trừ bằng tín chỉ, chuẩn áp dụng]"; "100% xanh"; "không phát thải"; "thân thiện môi trường"; "hàng đầu / số 1". Căn cứ gắn nhãn xác minh, ví dụ EU 2024/825 "tham chiếu quốc tế, không ràng buộc tại Việt Nam", Luật BVQLNTD 19/2023 Điều 10 "căn cứ ứng viên, chưa có người xác minh".
  - Trên HPG: neo 147/156 tuyên bố (9 câu vắt qua hai khối PDF được liệt kê riêng); 391 đề xuất (140 phạm vi/kỳ, 124 chỗ trống, 119 dẫn chiếu, 8 làm nhẹ); mở tài liệu 0,31 s; xuất DOCX 0,06 s; PDF 130 trang 0,34 s; báo cáo rà soát 0,44 s; lái bằng Edge headless, không lỗi console.
  - Chưa làm: thử với 3–5 người, đo thời gian và SUS (AUDIT §13: "Chưa").

### 1.8 Kết quả 31/10–01/11 ảnh hưởng tới câu chuyện sản phẩm (KH31 §2, §10)

- Bảy lỗi gốc F1–F7: verdict phẳng; luật phủ thấp; bảng PDF dàn phẳng; lỗi chuẩn hoá; 0 quy tắc pháp lý áp được; chỉ có nguồn nội bộ; không có gold người.
- Đường "LLM đọc thành IR → thư viện tất định so sánh" (AG-1) và cổng đồng thuận hai đường (AG-2) cho **0 kết luận sai** ngoài mẫu, nhưng độ phủ thấp (0,08–0,25) và đo trên ca dựng, nhãn bạc.
- Bộ đọc Qwen3-4B Q4 cục bộ khớp 0,963 với bản Kaggle. Được phép đặt sau cờ, **làm trợ giúp người soát, không đổi verdict** trước 10/11.
- Cổng 06/11 còn thiếu: đo thời gian đọc trên laptop (thiếu RAM), 17 bẫy và test bất biến khi bật `QUANTUM_VERIFY=dual`, thời gian chạy HPG.
- Khoá FPT 401 nên chế độ cloud (GLM-5.2) không chạy; demo dùng `offline`.

---

## 2. Khái niệm và lý thuyết phải nắm

1. **Green claim và kiểm chứng cấp tuyên bố.** Green claim là câu doanh nghiệp tự công bố về hiệu quả hay cam kết môi trường. GreenScan không hỏi "doanh nghiệp có tẩy xanh không" mà hỏi từng câu: nói gì, bằng chứng ở đâu, hai số có so được không, luật nào áp dụng (SP01 §1). Lý do: chưa có nhãn "greenwashing" đáng tin để học (BC tr.17); kết luận cấp doanh nghiệp không truy vết được.
2. **Taxonomy cờ đỏ FTC/EU** (BC tr.1–2): chung chung; so sánh thiếu cơ sở; seal/chứng nhận không nêu căn cứ; ngụ ý lợi ích tổng thể; claim cho toàn bộ khi chỉ đúng một phần; trung hoà nhờ offset. Trong GreenScan: OC-04 "thân thiện môi trường" (chung chung), OC-01 trung hoà các-bon (offset), OC-05 "hàng đầu" (so sánh không căn cứ), OC-02/OC-03 tuyên bố tuyệt đối. "Seal không căn cứ" mới có dạng đề xuất "thêm dẫn chiếu chứng nhận".
3. **Evidence-first; "Models read – Rules decide – Humans review".** Mô hình chỉ đọc và tìm; phép tính, so sánh, điều kiện luật do code tất định; ca khó và ca rủi ro do người chốt. BC tr.13 nói cùng ý: LLM không là nguồn chân lý đầu tiên.
4. **Năm thuộc tính bắt buộc ↔ cơ sở dẫn liệu ISA:** chỉ số (Phân loại), giá trị + đơn vị (Chính xác), kỳ (Đúng kỳ), năm gốc (Chính xác khi so sánh), phạm vi/ranh giới (Đầy đủ). Còn thiếu "Trình bày": mọi số đúng nhưng chọn lọc để tạo ấn tượng sai. Căn cứ chọn: GHG Protocol (năm gốc, ranh giới tổ chức), FTC (so sánh phải nêu cơ sở) [KIẾN THỨC NỀN].
5. **Năm mức verdict.** SUPPORTED: bằng chứng khớp. PARTIALLY_SUPPORTED: khớp một phần. CONTRADICTED: bằng chứng trái trực tiếp (bắt buộc có ít nhất một đoạn trái). UNSUPPORTED: không tìm thấy bằng chứng trong kho đã kiểm. INSUFFICIENT_EVIDENCE: kho chưa đủ để kết luận an toàn. Hai mức cuối dễ lẫn; kế hoạch B10 thêm `corpus_completeness`: "không thấy trong kho đã kiểm" khác "kho chưa đủ" (PRODUCTION_UI_SPEC F13).
6. **Tách "đủ bằng chứng" khỏi verdict** (SP02 §4, SP04 §5). Đánh giá đủ/thiếu trước, kèm mã lý do (MISSING_BASELINE, PERIOD_MISMATCH…), rồi mới kết luận ủng hộ hay bác. Thiếu bằng chứng không được tự thành "Unsupported".
7. **Comparability Gate 6 chiều:** loại giá trị (tuyệt đối / tỷ trọng / mức thay đổi), ranh giới tổ chức, công nghệ/phương pháp, chỉ số con, Scope, mục tiêu vs thực hiện. Lệch một chiều thì NOT COMPARABLE. Ví dụ: "giảm 30% phát thải Scope 1+2" không được so với "tổng phát thải" có Scope 3; cường độ (tCO2e/tấn thép) có thể giảm khi tuyệt đối tăng nếu sản lượng tăng nhanh hơn.
8. **Dự đoán có chọn lọc (selective prediction) và abstain.**
   - Độ phủ = (số ca dám kết luận S hoặc C) / N.
   - Precision trên phần kết luận = số kết luận đúng / số ca dám kết luận.
   - Selective risk = 1 − precision. Đường risk–coverage vẽ đánh đổi khi đổi ngưỡng.
   - Ví dụ: tập G, luật + 4B: độ phủ 0,093, precision 1,0. Luật một mình trên tập sạch v1.3: độ phủ 0,011.
9. **Hai loại lỗi nguy hiểm, chi phí bất đối xứng:** CONTRADICTED sai = vu oan doanh nghiệp; SUPPORTED sai = bỏ lọt. Không gộp vào một con số (bất biến 8, KH31 §4).
10. **Đồng thuận hai đường độc lập** (BC tr.15; AG-2). Hai đường lỗi ít tương quan đồng ý thì đáng tin hơn một đường tự lặp lại (self-consistency). Chính sách "bỏ phiếu S đơn độc của luật": luật nói SUPPORTED một mình chính là nguồn 8 SUPPORTED sai trên tập hiệu chỉnh, nên bỏ phiếu đó là điều kiện để đường kép an toàn.
11. **Truy xuất lai** [KIẾN THỨC NỀN]:
    - BM25: `score(q,d) = Σ_t IDF(t) · f(t,d)·(k1+1) / [f(t,d) + k1·(1 − b + b·|d|/avgdl)]`.
    - RRF: `RRF(d) = Σ_r 1 / (k + rank_r(d))`, k = 60.
    - Recall@k = |gold ∩ top-k| / |gold|; MRR = trung bình 1/(hạng của đoạn đúng đầu tiên); nDCG@k = DCG@k / IDCG@k với `DCG = Σ_i (2^rel_i − 1) / log2(i+1)`.
    - GreenScan: RRF chỉ để xếp lại, điểm vẫn trộn theo trọng số 0,55/0,45 (`configs/default.yaml`).
12. **NLI và lệch miền.** NLI phân loại cặp (tiền đề, giả thuyết) thành entail / contradict / neutral. Học trên FEVER (Wikipedia) rồi đem sang claim khí hậu thì rơi mạnh (77,69% → 38,78%, [NGOÀI]). Claim định lượng cần tính chứ không cần "hiểu ngữ nghĩa".
13. **Hiệu chỉnh xác suất** [KIẾN THỨC NỀN]: `ECE = Σ_b (|B_b|/n) · |acc(B_b) − conf(B_b)|`; `Brier = (1/n) Σ (p_i − y_i)²`. GreenScan chưa có gold nên chưa báo ECE. Abstain AG-2 dùng xô xác suất ước trên OOF theo công ty.
14. **Đồng thuận người gán:** `κ = (p_o − p_e) / (1 − p_e)`. BC đề xuất κ ≥ 0,75 cho nhãn cấp cao, chấp nhận thấp hơn cho nhãn suy luận sâu nếu có ma trận phân xử (tr.13).
15. **Provenance và tái lập.** Mỗi lượt chạy ghi run_id, config_hash, input_hashes, plan, nhật ký append-only. Mục tiêu BC: 0 câu kết luận không trích dẫn trong bản xuất pháp lý (tr.7).
16. **Luật theo thời điểm** (SP01 R8). Trích đúng điều nhưng sai phiên bản là lỗi riêng. Cần `effective_from/to`, `as_of_date` và chế độ kiểm (lịch sử theo kỳ của claim, hoặc hiện hành).
17. **Policy-as-code và "bộ nhớ" của hệ thống.** Luật thành dữ liệu có phiên bản (registry, rule pack, taxonomy YAML), không nhét vào prompt. Người dùng bổ sung quy tắc bằng phiên bản mới có changelog (US-09.02), rồi chạy lại bộ bẫy hồi quy. Mô hình không cần "nhớ" luật vì luật do code áp.
18. **Điểm ưu tiên khác điểm rủi ro.** `P = 40·trọng yếu + 25·nghĩa vụ công bố + 25·khuyết bằng chứng + 10·bất thường` (`configs/priority_v1.yaml`; cách chuẩn hoá từng yếu tố [CHƯA XÁC MINH]). P chỉ để xếp hàng đợi (P5). Rubric v2 (9 thành phần, tổng 100) để giải thích vì sao thiếu.
19. **Thủ tục phân tích và "im lặng có chọn lọc"** (AUDITOR §4.2). So chéo năm, chéo doanh nghiệp, chéo tài liệu cùng kỳ; cờ khi chỉ số năm trước có mà năm nay biến mất. Tương ứng thủ tục phân tích trong chuẩn mực kiểm toán (ISA 520 [KIẾN THỨC NỀN]). **Chưa cài**: yếu tố `anomaly` là not_computed cho 172/172 mục.
20. **Preventive authoring / linter.** Kiểm và gợi ý sửa bản nháp trước công bố. Bất biến không bịa số: `Số(câu mới) ⊆ Số(câu cũ) ∪ Số trang(bằng chứng trích dẫn)`. Tracked changes DOCX dùng thẻ `w:ins`, `w:del`.
21. **Đo độ dễ dùng** [KIẾN THỨC NỀN]:
    - SUS 10 câu thang 1–5: `SUS = 2,5 × [Σ_lẻ (x_i − 1) + Σ_chẵn (5 − x_i)]`, từ 0 đến 100; trung bình các nghiên cứu khoảng 68. Ngưỡng nhóm đăng ký là ≥ 70 (F3).
    - Bài đo thời gian thiết kế hoán vị (crossover): mỗi người làm nửa bằng tay, nửa có hệ thống, đổi chéo, để khử khác biệt giữa người (F1).
    - Tỷ lệ override và automation bias: người soát dễ tin máy; tỷ lệ override thấp bất thường là tín hiệu cảnh báo.
22. **Phân lớp bảo mật tài liệu:** A công khai, B nội bộ, C mật nghề nghiệp. LLM đám mây chỉ cho lớp A (KE_HOACH_PHAN_BIEN §5). Căn cứ dự án dẫn: Luật BVDLCN 91/2025 [CHƯA XÁC MINH điều khoản].
23. **GHG Protocol** [KIẾN THỨC NỀN]: Scope 1 trực tiếp; Scope 2 năng lượng mua; Scope 3 chuỗi giá trị. Ranh giới tổ chức theo kiểm soát hoặc tỷ lệ vốn (nên mẹ khác tập đoàn). Năm gốc phải nêu và tính lại khi cơ cấu đổi.
24. **LCA (ISO 14040/44), dấu vết carbon sản phẩm (ISO 14067), PEF** [KIẾN THỨC NỀN]: đo tác động cả vòng đời sản phẩm. GreenScan không làm vì đối tượng là báo cáo doanh nghiệp, và LCA cần dữ liệu kiểm kê mà báo cáo không có.
25. **Benchmark dựng theo cấu trúc (GS-Bench).** Lấy một ô bảng thật → dựng tuyên bố đúng → LLM diễn đạt lại → nhiễu có kiểm soát (đổi giá trị/đơn vị/kỳ/Scope…) nên đáp án biết trước ("nhãn tìm bằng thực thi"). Rủi ro: "B-b đại diện tuyên bố thật" là [GIẢ THUYẾT], kiểm bằng cách so thứ hạng các hệ trên B-b với trên B-c (KH31 §4).

---

## 3. Số liệu và dữ kiện được phép nói

| Dữ kiện | Nguồn | Nhãn |
|---|---|---|
| HPG (BCPTBV 2025 + BCTN 2024): 156 tuyên bố → 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT; hàng đợi 9/172 mục | KH31 §2 F1 (lượt c892c137…, 22/10) | [ĐÃ THỰC NGHIỆM] |
| 154/156 MEDIUM; 156/156 pháp lý "chưa đủ bằng chứng"; 0 quy tắc áp dụng; 780/780 bằng chứng là tài liệu của chính doanh nghiệp | AUDIT §0 (phiên cd5a82e3, 09/10) | [ĐÃ THỰC NGHIỆM] |
| 133/156 thiếu kỳ, 152/156 thiếu năm gốc (chưa đo đây là thực trạng hay lỗi trích) | AUDIT §1, dòng khâu 3 | [ĐÃ THỰC NGHIỆM] |
| Soát hàng đợi bởi thành viên (11/10): đồng ý 12/14; khoảng 6/9 mục đúng | AUDIT §8(b) | [ĐÃ THỰC NGHIỆM]: người trong nhóm, n nhỏ, không phải gold |
| HPG chạy 107–121 s trên laptop; học trò T1 119 ms/câu trên CPU | AUDIT §13; KE_HOACH_PHAN_BIEN §0 | [ĐÃ THỰC NGHIỆM] |
| Studio trên HPG: neo 147/156; 391 đề xuất (140 / 124 / 119 / 8); mở 0,31 s; DOCX 0,06 s; PDF 130 trang 0,34 s; báo cáo rà soát 0,44 s | AUDIT §12 | [ĐÃ THỰC NGHIỆM] |
| 385 test xanh (14/10; 26 test mới cho intake và Studio) | AUDIT, dòng 5 | [ĐÃ THỰC NGHIỆM] |
| 17 bẫy là cổng hồi quy (`tests/test_verdict_traps.py`) | KE_HOACH_PHAN_BIEN §1 khâu 5 | [ĐÃ THỰC NGHIỆM] |
| UI v2: build 303 kB JS; SSR 21/21 màn không có từ cấm; pytest 215 passed / 8 xfailed (20/09) | UI_V2_REVIEW "Kiểm tra đã làm" | [ĐÃ THỰC NGHIỆM], số cũ |
| Không có gold người: 0/88 cặp, 0/79 câu (kiểm 31/10) | KH31 §0, §2 F7 | [ĐÃ THỰC NGHIỆM] |
| Học trò T1 e5-base macro-F1 0,71–0,73, kiểm định chéo theo công ty, n = 1.217, 3 seed; chưa gắn sản phẩm | KH31 §2 (`training/runs/kaggle_t1_v3/results.json`) | [ĐÃ THỰC NGHIỆM] trên nhãn Claude |
| Nhị phân "có phải tuyên bố": học trò F1 0,82, luật 0,61 | KE_HOACH_PHAN_BIEN §0 | [ĐÃ THỰC NGHIỆM] trên nhãn Claude |
| Size ladder 51 ca dựng: luật dám quyết 8/32 (đúng 6) và 3/19 (đúng 3); LLM trả lời 29–32/32 | KH31 §2 F2 | [ĐÃ THỰC NGHIỆM] |
| Bảng dàn phẳng: 4/4 model ≥ 26B báo SUPPORTED sai cùng ca N02, N05 (bảng GHG tr.39 HPG) | KH31 §2 F3 | [ĐÃ THỰC NGHIỆM] |
| GS-Bench v1.1: 453 ca = 51 B-a + 402 B-b (S 95 / C 123 / N 184), 7 doanh nghiệp, 0 ca lệch tự kiểm | KH31 §10 (31/10 14:15) | [ĐÃ THỰC NGHIỆM], nhãn bạc |
| Luật trên B-b v1: độ phủ 0,028 (4/142), precision 0,75, bắt 0/44 ca mâu thuẫn. Trần IR gold + `irlib`: 140/142, độ phủ 0,528, precision 1,0 | KH31 §10 (31/10) | [ĐÃ THỰC NGHIỆM] |
| 11/11 kết luận sai của 32B là bội số tự thêm ("10.730 m3" → "10.730 ngàn m3"); sửa bằng `irlib.ground()` + 9 test | KH31 §10 (14:15) | [ĐÃ THỰC NGHIỆM] |
| Ngoài mẫu v1.1 (246 ca): độ phủ 4B / 8B / 14B / 32B = 0,126 / 0,220 / 0,256 / 0,329; chỉ 8B qua cổng vu oan ≤ 1 | KH31 §10 (22:40) | [ĐÃ THỰC NGHIỆM] |
| Ngoài mẫu sạch v1.3 (87 ca): độ phủ luật 0,011; 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253; mọi model precision 1,0, 0 kết luận sai | KH31 §10 (01/11 17:00) | [ĐÃ THỰC NGHIỆM] |
| AG-2 luật + 4B, bỏ S đơn độc của luật, trên G (162 ca): độ phủ 0,093, precision 1,0, 0 S sai, 0 C sai; CI phần tăng độ phủ [0,016; 0,185]. Tập hiệu chỉnh: 0,242 / 0,989 / 1 / 0 (luật có 8 S sai) | KH31 §10 (23:50) | [ĐÃ THỰC NGHIỆM] |
| Bộ đọc cục bộ Q4 khớp 0,963, Q8 khớp 0,981 với 4B bf16; luật + 4B Q4 trên G: 0 sai, độ phủ 0,080; trên T4 1,7 s/câu | KH31 §10 (01/11 17:15) | [ĐÃ THỰC NGHIỆM] |
| AG-3 v0: tr.39 dựng 10 hàng, cộng dọc 3/3; 7 ca: trang thô đúng 1/7, hàng dựng lại đúng 3/7, 0 sai; dự đoán ≥ 5/7 trượt. Tiêu đề trang ghi "NĂM 2024", bảng ghi 2025 | KH31 §10 (17:40) | [ĐÃ THỰC NGHIỆM] |
| Groq `gpt-oss-120b` (reasoning low + json_object): 12/12 JSON, đúng trường 1,0, p50 1,0 s | KH31 §10 (14:15, việc 3) | [ĐÃ THỰC NGHIỆM] |
| Khoá FPT báo 401 (31/10): chế độ cloud GLM-5.2 không chạy; demo dùng offline | KH31 §10 (31/10) | [ĐÃ THỰC NGHIỆM] |
| 22.540.603 + 933.876 = 23.474.479 ≈ 23.474.480 công bố (Δ ≈ 0,000004%) | `TXT/giai_thich_pipeline_de_hieu.txt` mục 6 | [ĐÃ THỰC NGHIỆM], đã kiểm lại số học |
| Kho 670 tài liệu / 21 doanh nghiệp | AUDITOR_WORKFLOW_POSITIONING §4.2 | [ĐÃ THỰC NGHIỆM], số đếm |
| Registry pháp lý 11 văn bản thật; 24 văn bản ứng viên đã tải và OCR (14/10) | KE_HOACH_PHAN_BIEN §0 | [ĐÃ THỰC NGHIỆM] |
| Trọng số `priority-v1.1`: trọng yếu 40, nghĩa vụ 25, khuyết bằng chứng 25, bất thường 10 (bất thường not_computed 172/172) | `REPO/configs/priority_v1.yaml` dòng 13–28; AUDIT §8 | cấu hình đã kiểm |
| `risk-rubric-v2`: 9 thành phần (12+12+8+8+8+18+8+18+8 = 100); LOW 0–24, MEDIUM 25–49, HIGH 50–74, CRITICAL 75–100 | PRODUCTION_UI_SPEC §2 F6; `REPO/configs/scoring_v1.yaml` dòng 1 | cấu hình đã kiểm |
| Truy xuất mặc định: BM25 + n-gram ký tự (`embedding.provider: lite`), RRF k=60, 0,55/0,45, 30 ứng viên, giữ 5, ngưỡng 0,12, sàn 3; reranker `none` | `REPO/configs/default.yaml` dòng 20–42 | cấu hình đã kiểm |
| CMA: khoảng 40% green claim trên web có thể gây hiểu lầm (rà soát quốc tế) | BC tr.3, chú thích [9][10] (gov.uk) | [NGOÀI] |
| EC: 53% green claim mơ hồ/gây hiểu lầm/không có cơ sở; 40% không có bằng chứng | BC tr.3 | [NGOÀI] |
| Environmental Claim Detection: 2.647 câu (gốc 3.000), 16 chuyên gia, RoBERTa-large macro-F1 khoảng 84,9; giấy phép CC BY-NC-SA 4.0 (theo nhóm) | BC tr.4, tr.8; CHUONG_TRINH v3 dòng 168 | [NGOÀI] |
| FEVER khoảng 185 nghìn claim; SciFact 1.409 claim / 5.183 abstract (CC BY-NC 2.0); CLIMATE-FEVER 1.535 claim / 7.675 cặp | BC tr.7–8 | [NGOÀI] |
| Verifier học FEVER: 77,69% trên FEVER, 38,78% trên claim khí hậu | MO_HINH_CO_QUA_BE_KHONG dòng 71 (N6) | [NGOÀI] |
| ClimateBERT-NetZero khoảng 3,5 nghìn mẫu; SustainableQA 195.287 QA / 61 báo cáo / 218 bảng (CC BY-NC 4.0); GRI-QA 4.089 câu / 204 bảng (MIT); ESGDoc 1.093 báo cáo / 563 công ty; ESGenius 1.136 câu | BC tr.8–9 | [NGOÀI] |
| Tài nguyên BC đề xuất: 1–2 GPU 24 GB × 50–150 GPU-giờ; 1–4 GPU 40–80 GB; 1–3 TB; 2–4 người gán + 1 phân xử | BC tr.14–15 | [NGOÀI], đề xuất |
| Mục tiêu IAA κ/α ≥ 0,75 cho nhãn cấp cao | BC tr.13 | [NGOÀI] |
| Kiểm chéo hai đường cho tín hiệu tin cậy tốt hơn tự nhất quán (text-to-SQL: AUROC 0,82 so với 0,61–0,68) | KH31 §3 | [NGOÀI], nguồn gốc chưa ghi [CHƯA XÁC MINH] |
| SUS trung bình khoảng 68 | — | [KIẾN THỨC NỀN] |
| RRF k = 60 là giá trị mặc định thông dụng (Cormack và cs., 2009) | — | [KIẾN THỨC NỀN] |
| Báo cáo 200–300 trang cần 8–12 giờ đọc tay; mục tiêu 30 phút sàng lọc + khoảng 2 giờ rà điểm rủi ro cao | `TXT/ho_so_vong1.txt` dòng 284 | [GIẢ THUYẾT] |
| Khoanh 5–10% claim vào nhóm rủi ro cao (HPG: 9/172 ≈ 5%, phù hợp nhưng chưa kiểm) | `TXT/ho_so_vong1.txt` dòng 285; KH31 §2 | [GIẢ THUYẾT] |
| F1 giảm ≥ 30% thời gian, độ đúng không giảm (cận dưới CI của hiệu ≥ −5 điểm); F2 +10 điểm đồng ý với gold; F3 SUS ≥ 70 | CHUONG_TRINH v3 dòng 90–92 | [GIẢ THUYẾT]: ngưỡng đăng ký, chưa đo |
| "B-b đại diện cho tuyên bố thật" | KH31 §4 | [GIẢ THUYẾT] |
| Ước 25–40 giờ GPU T4 cho AG-0…AG-6 | KH31 §0 | [GIẢ THUYẾT], ước tính |

---

## 4. Câu hỏi BGK dự kiến (23 câu)

Công thức trả lời: **vấn đề → nguyên lý → GreenScan làm gì → giới hạn**. Mỗi câu khoảng 30–60 giây.

**Q1. Khách hàng của các bạn là ai, ai trả tiền?**
- *Trả lời:* "Người dùng là người soát báo cáo phát triển bền vững. Đầu tiên là phòng ESG hoặc kiểm toán nội bộ của doanh nghiệp niêm yết tự soát bản nháp trước khi công bố; sau đó là kiểm toán viên và ngân hàng thẩm định tín dụng xanh. Hôm nay họ làm tay: đọc vài trăm trang, dò câu tuyên bố, lật bảng đối chiếu, gõ giấy làm việc. Ba việc đó cơ học và tốn thời gian nhất. GreenScan tự động hoá đúng ba việc đó và trả về một hàng đợi đã xếp ưu tiên: với báo cáo Hòa Phát là 9 mục cần soát trước trong 172, kèm lý do. Xét đoán và chữ ký vẫn là của người. Giới hạn: chúng tôi chưa có khách hàng trả tiền; bước sau cuộc thi là thí điểm."
- *Vặn:* "Sao không bán cho nhà đầu tư cá nhân hay người tiêu dùng?" → "Họ dễ đọc kết quả thành phán quyết. Sản phẩm cho họ cần độ chính xác đã kiểm trên nhãn người, mà chúng tôi chưa có. Bắt đầu ở chỗ rủi ro thấp nhất: doanh nghiệp tự soát tài liệu của chính mình."
- *Bẫy:* nói "ai cũng dùng được" (6 persona là lý do sản phẩm không sắc, AUDITOR §1); nói đã có khách hàng hay thư cam kết.

**Q2. Mô hình kinh doanh và chi phí vận hành?**
- *Trả lời ([GIẢ THUYẾT], tài liệu dự án chưa có mục mô hình kinh doanh):* "Bán B2B dạng phần mềm cài tại chỗ, chạy ngoại tuyến, cấp phép theo năm hoặc theo số báo cáo; dịch vụ kèm là cập nhật gói quy tắc pháp lý có phiên bản. Lợi thế chi phí: mặc định chạy CPU, không gọi API trả phí; một lượt HPG gồm hai báo cáo mất 107–121 giây trên laptop. Trước khi định giá, chúng tôi thí điểm với một hai phòng ESG để đo thời gian tiết kiệm, rồi định giá theo giờ công tiết kiệm được."
- *Vặn:* "Giá bao nhiêu, thị trường bao lớn?" → "Chưa định giá vì chưa đo được thời gian tiết kiệm. Cỡ thị trường đầu tiên là các doanh nghiệp niêm yết có nghĩa vụ công bố thông tin môi trường và các cơ sở thuộc diện kiểm kê khí nhà kính theo QĐ 13/2024 [CHƯA XÁC MINH con số; cần lấy từ danh mục QĐ 13]."
- *Bẫy:* bịa giá, TAM, doanh thu. Lưu ý giấy phép: EnvironmentalClaims (CC BY-NC-SA 4.0), SciFact (CC BY-NC 2.0), SustainableQA (CC BY-NC 4.0) cấm dùng thương mại. Sản phẩm không phụ thuộc các bộ này.

**Q3. Khác gì MSCI, CDP, nền tảng dữ liệu ESG, hay ChatGPT?**
- *Trả lời:* "Công cụ xếp hạng ESG cho điểm tổng hợp cấp doanh nghiệp, chi phí cao, khó truy vết tới từng câu trong báo cáo tiếng Việt. Chatbot trả lời trôi chảy nhưng có thể sai khi truy xuất kém. Nguyên lý của chúng tôi: kiểm chứng từng tuyên bố, bằng chứng đi trước kết luận, và được phép từ chối kết luận. Mỗi tuyên bố có trang nguồn, phép tính tất định, danh sách thuộc tính thiếu, verdict 5 mức và nhật ký; tài liệu chưa công bố được xử lý ngoại tuyến. Giới hạn: phạm vi hẹp hơn: tuyên bố môi trường định lượng, tiếng Việt, không chấm ESG tổng thể." (bảng đối thủ: `TXT/ho_so_vong1.txt` dòng 366–371)
- *Vặn:* "ChatGPT cũng trích dẫn được mà?" → "Trích dẫn không bảo đảm số đúng. Trên bộ đo của chúng tôi, cả 11 kết luận sai của Qwen3-32B đều do model tự thêm bội số, như '10.730 m3' thành '10.730 ngàn m3'. Chúng tôi chặn lỗi này bằng một bước code so số với câu gốc, không bằng prompt."
- *Bẫy:* chê đối thủ bằng số không nguồn; nói "MSCI sai".

**Q4. Báo cáo thiết kế đề xuất ba chế độ: quét nhanh claim tiêu dùng, theo dõi phát biểu, kiểm báo cáo. Sao chỉ làm một?**
- *Trả lời:* "Mỗi chế độ là một bài toán khác. Quét nhanh cần đọc ảnh, nhãn, seal trong 1–3 giây; theo dõi phát biểu cần nhận dạng giọng nói. Báo cáo doanh nghiệp Việt Nam là nơi có nghĩa vụ công bố (TT 96, kiểm kê khí nhà kính theo QĐ 13/2024) và có bảng số để kiểm. Thể lệ ưu tiên mô hình đơn giản chạy ổn định, nên chúng tôi làm sâu chế độ kiểm báo cáo và thêm Studio để viết đúng trước khi công bố. Giới hạn: claim trên bao bì, quảng cáo, hình ảnh chưa xử lý."
- *Vặn:* "Luật bảo vệ người tiêu dùng có dùng không?" → "Chỉ làm căn cứ ứng viên cho đề xuất làm nhẹ lời nói quá (Luật BVQLNTD 19/2023, Điều 10), gắn nhãn 'chưa có người xác minh'."
- *Bẫy:* hứa làm đủ ba chế độ trong vài tháng.

**Q5. Sao không dùng NLI (DeBERTa…) hay LLM để kết luận như báo cáo khuyên, mà lại dùng luật?**
- *Trả lời:* "Tuyên bố môi trường định lượng cần phép tính, không cần suy diễn. Verifier học trên FEVER đạt 77,69% trên FEVER nhưng 38,78% trên tuyên bố khí hậu. Chính báo cáo thiết kế cũng nói không để LLM làm nguồn chân lý đầu tiên. Vì vậy lập trường của mỗi đoạn được suy theo thứ bậc: so số trước, rồi tín hiệu định tính, hướng tăng/giảm, LLM (không có quyền quyết), cuối cùng là độ tương đồng; số học do code. Giới hạn: luật phủ thấp. Trên 51 ca dựng, luật chỉ dám quyết 8/32 (đúng 6), trong khi LLM trả lời 29–32/32. Đó là lý do verdict trên HPG phẳng."
- *Vặn:* "Vậy LLM làm gì?" → "LLM đọc câu thành cấu trúc: chỉ số, giá trị, đơn vị, kỳ, phạm vi; thư viện tất định làm phép so. Trên tập ngoài mẫu sạch 87 ca, độ phủ tăng từ 0,011 (luật) lên 0,138 (Qwen3-4B) và 0,253 (32B), precision 1,0, 0 kết luận sai. Đó là ca dựng, nhãn bạc."
- *Bẫy:* chê NLI chung chung; nói LLM của mình "không bao giờ sai".

**Q6. Gần như mọi tuyên bố đều "khớp một phần" (153/156). Hệ thống có ích gì?**
- *Trả lời:* "Đúng, và chúng tôi biết nguyên nhân: luật phủ thấp, bảng PDF bị dàn phẳng, kho chỉ có tài liệu của chính doanh nghiệp, gói luật chưa có quy tắc áp được. Giá trị hôm nay không nằm ở verdict mà ở ba thứ: hàng đợi 9 mục có lý do; danh sách thuộc tính thiếu (133/156 câu thiếu kỳ, 152/156 thiếu năm gốc); và Studio biến thiếu sót thành 391 đề xuất sửa có vết. Đang sửa: đường kép luật + bộ đọc 4B đạt độ phủ 0,080 trên tập ngoài mẫu G, 0 kết luận sai. Nó đặt sau cờ, chỉ hỗ trợ người soát."
- *Vặn:* "Sao không bật luôn?" → "Quy tắc của nhóm: không dùng nhãn Claude để tháo chốt LLM. Chưa đo thời gian trên laptop, chưa chạy 17 bẫy khi bật cờ. Đổi kết luận khi chưa qua cổng là rủi ro vu oan doanh nghiệp."
- *Bẫy:* giấu con số 153/156; giải thích PARTIAL là "đúng một phần" (thực chất là hệ thống chưa phân biệt được).

**Q7. Đã đo người dùng tiết kiệm thời gian chưa? SUS bao nhiêu?**
- *Trả lời:* "Chưa. Bài đo đã đăng ký: F1 thiết kế hoán vị 20–40 câu, mỗi người làm nửa bằng tay, nửa có hệ thống rồi đổi chéo; mục tiêu giảm ít nhất 30% thời gian mà độ đúng không giảm. F3: SUS với 5–8 người (sinh viên kế toán, kiểm toán viên), ngưỡng ≥ 70. Hiện có: độ trễ (HPG 107–121 giây; Studio mở 0,31 giây, xuất DOCX 0,06 giây), đã lái trên trình duyệt thật không lỗi, thành viên soát hàng đợi đồng ý 12/14. Con số 8–12 giờ đọc tay xuống 30 phút + 2 giờ trong hồ sơ Vòng 1 là giả định."
- *Vặn:* "Sao chưa đo?" → "Bài đo thời gian cần gold để so độ đúng; chúng tôi ưu tiên đo đúng/sai trước." Nếu kịp làm SUS mini trước 10/11, báo rõ n và đối tượng.
- *Bẫy:* nói "tiết kiệm 80%"; gọi 12/14 là "độ chính xác".

**Q8. GreenScan Studio là gì? AI có viết hộ báo cáo, có bịa số không?**
- *Trả lời:* "Studio là trình soát lỗi cho báo cáo phát triển bền vững, như soát chính tả trong Word. Tuyên bố có vấn đề được gạch lượn sóng đỏ, vàng, xanh; hover hiện kết luận, bằng chứng, căn cứ; đề xuất hiện như tracked change. Chỉ có 4 loại đề xuất: thêm phạm vi, kỳ, năm gốc; thay câu mơ hồ bằng chỗ trống '[bổ sung: …]'; thêm dẫn chiếu bằng chứng đã tìm thấy; làm nhẹ lời nói quá, ví dụ 'trung hòa các-bon' thành 'hướng tới trung hòa các-bon [bổ sung: phần giảm thực tế, phần bù trừ bằng tín chỉ, chuẩn áp dụng]'. Mọi đề xuất qua một kiểm tra code: số trong câu mới phải có sẵn trong câu cũ hoặc là số trang trích dẫn, không thì bị loại. Mặc định chạy mẫu theo luật, ngoại tuyến. Xuất DOCX có tracked changes, bản sạch, báo cáo rà soát và JSON vết. Giới hạn: PDF xuất được dựng lại, không giữ bố cục gốc; 9/156 câu vắt qua hai khối chưa neo được."
- *Vặn:* "391 đề xuất cho 156 câu, người dùng có bị ngập?" → "Panel Problems nhóm theo mức độ, F8 nhảy tới lỗi kế, 'chấp nhận mọi đề xuất loại X' có bước xác nhận, và hàng đợi chỉ đưa 9 mục cần xem trước."
- *Bẫy:* gọi là "AI viết lại báo cáo"; nói LLM đang chạy trong Studio (τ chưa hiệu chỉnh nên mặc định không gọi).

**Q9. Studio có thành công cụ giúp doanh nghiệp tẩy xanh khéo hơn không?**
- *Trả lời:* "Rủi ro lưỡng dụng có thật. Nguyên tắc của chúng tôi: chỉ đề xuất theo hướng làm tuyên bố kiểm chứng được hơn: thêm phạm vi, năm gốc, bằng chứng, hoặc hạ lời tuyệt đối thành lời có điều kiện kèm chỗ trống buộc phải điền số thật. Không bao giờ thêm số, không đề xuất bỏ thông tin. Mọi thay đổi có nhật ký (người hay AI, lúc nào, quy tắc nào) và xuất kèm báo cáo rà soát. Backlog 13/08 ghi rõ anti-goal 'không giúp che giấu tác động'. Giới hạn: người dùng vẫn tự xoá được câu; Studio không đoán ý định."
- *Vặn:* "Ai bảo đảm báo cáo đã sửa là đúng?" → "Người ký. Studio chỉ làm báo cáo dễ kiểm hơn."
- *Bẫy:* khẳng định "không thể lạm dụng". [CHƯA XÁC MINH: Studio có cảnh báo khi người dùng xoá câu chứa số liệu hay không.]

**Q10. Kế toán viên không rành AI có dùng được không? Căn cứ gì nói là dễ dùng?**
- *Trả lời:* "Tám nguyên tắc giao diện đã khoá: mỗi màn xoay quanh một tuyên bố; bằng chứng có trang đứng cạnh kết luận; 'chưa đủ bằng chứng' màu trung tính kèm câu 'kết quả hợp lệ, không phải lỗi'; không dùng chữ cáo buộc; thuộc tính gọi theo cơ sở dẫn liệu kiểm toán (Phân loại, Chính xác, Đúng kỳ, Đầy đủ); một ô thả nhận PDF, DOCX, URL; nút báo cáo mẫu; tương phản ≥ 4,5:1, trạng thái không chỉ bằng màu. Giới hạn: đó là thiết kế, chưa phải số đo; SUS chưa đo."
- *Vặn:* "Phím tắt kiểu VS Code, kế toán đâu dùng VS Code?" → "Phím tắt là phần thêm. Mọi thao tác có nút và tooltip; ẩn dụ gần nhất là Track Changes trong Word, thứ kế toán viên đã quen."
- *Bẫy:* nói "được người dùng đánh giá cao".

**Q11. Doanh nghiệp có quy chế nội bộ, bộ tiêu chí riêng. Hệ thống có làm theo được không?**
- *Trả lời:* "Nếu nhét quy chế vào prompt, LLM có thể không theo và không ai kiểm được. Nguyên lý của chúng tôi: luật là dữ liệu có phiên bản, có ngày hiệu lực; mô hình chỉ đọc, code áp luật. GreenScan có registry văn bản (11 văn bản thật, 24 ứng viên đã OCR), gói quy tắc có `rule_pack_version`, taxonomy trong tệp YAML. Tài liệu nội bộ tải lên với vai trò 'tham chiếu' hoặc 'tiêu chuẩn' để truy xuất làm căn cứ. Đổi quy tắc phải có changelog và chạy lại bộ bẫy. Giới hạn: chưa có màn hình để người dùng tự thêm quy tắc; gói quy tắc Việt Nam hiện chưa áp được quy tắc nào trên 156 tuyên bố; quy tắc mới cần chuyên gia duyệt."
- *Vặn:* "LLM có 'bộ nhớ' quy tắc không?" → "Bộ nhớ là tệp cấu hình có phiên bản và kho văn bản có hiệu lực, không phải trí nhớ của model. Nhờ vậy cùng đầu vào cho cùng kết quả, và mỗi kết luận ghi phiên bản quy tắc đã dùng."
- *Bẫy:* hứa "tải quy chế lên là AI tự hiểu". [CHƯA XÁC MINH: tài liệu vai trò `reference` có tác động gì ngoài truy xuất.]

**Q12. Nhà đầu tư cần một con số. Sao không chấm điểm hay xếp hạng doanh nghiệp?**
- *Trả lời:* "Điểm cộng dồn phụ thuộc vào tài liệu nào được tải lên, mất ngữ cảnh, và người xem đọc thành 'vi phạm'. Điểm rủi ro chỉ có nghĩa ở cấp từng tuyên bố kèm bằng chứng; doanh nghiệp có vụ việc không có nghĩa tài liệu tẩy xanh, càng không có nghĩa từng tuyên bố tẩy xanh. GreenScan dùng điểm rủi ro chỉ để xếp hàng đợi, hiện bằng chấm nhỏ và phân rã 9 thành phần; ở cấp lượt chạy chỉ có trạng thái phát hành (RELEASABLE, PENDING_HUMAN_REVIEW, BLOCKED). Giới hạn: so sánh doanh nghiệp cùng ngành chưa làm."
- *Vặn:* "Vậy báo gì cho nhà đầu tư?" → "Số tuyên bố mâu thuẫn, thiếu bằng chứng, chờ người, mỗi cái truy được về trang. Không gộp thành điểm."
- *Bẫy:* đưa ra "điểm GreenScan" cho HPG.

**Q13. "Chưa đủ bằng chứng" nhiều thế, hệ thống có né trách nhiệm không?**
- *Trả lời:* "Đây là dự đoán có chọn lọc: đổi độ phủ lấy độ đúng trên phần dám kết luận. Trong kiểm toán, kết luận sai nguy hiểm hơn không kết luận: CONTRADICTED sai là vu oan, SUPPORTED sai là bỏ lọt. Chúng tôi báo ba số riêng: precision trên phần dám kết luận, độ phủ, số kết luận sai nguy hiểm. Ví dụ ngoài mẫu: luật + 4B có độ phủ 0,093, precision 1,0, 0 sai; luật một mình 0,011. Giới hạn: độ phủ còn thấp, tập ngoài mẫu nhỏ (87–162 ca) và là ca dựng."
- *Vặn:* "Precision 1,0 trên 15 ca thì nói được gì?" → "Chưa phải một cận chặt. Vì vậy chúng tôi báo kèm khoảng tin cậy phần tăng độ phủ [0,016; 0,185] và không nói 'chính xác 100%'."
- *Bẫy:* nói "không bao giờ sai".

**Q14. Độ chính xác của hệ thống là bao nhiêu?**
- *Trả lời:* "Phải tách ba lớp. Một: chưa có số đo trên nhãn người (kiểm 31/10: 0/88 cặp, 0/79 câu). Hai: trên GS-Bench (453 ca dựng từ ô bảng thật của 7 doanh nghiệp, đáp án biết trước) chúng tôi báo precision và độ phủ. Ba: học trò nhận diện tuyên bố đạt macro-F1 0,71–0,73 so với nhãn Claude (n = 1.217, kiểm định chéo theo công ty, 3 seed). Từ 04/11, nhãn Claude được dùng như một bộ dữ liệu bình thường và Nhân soát lại; khi trình bày ghi rõ 'nhãn do Claude tạo, người soát n ca'."
- *Vặn:* "Sao không thuê người gán?" → "Thời gian và chi phí. Vì vậy chúng tôi dựng nhãn bằng thực thi: đáp án sinh từ bảng thật cộng nhiễu có kiểm soát, không phụ thuộc người gán."
- *Bẫy:* gọi số trên nhãn Claude là "độ chính xác" mà không nêu nguồn nhãn; lấy macro-F1 khoảng 84,9 của bộ Environmental Claim Detection làm số của mình.

**Q15. Làm sao biết bằng chứng đúng phạm vi chứ không chỉ cùng chủ đề?**
- *Trả lời:* "Báo cáo thiết kế nêu đúng lỗi này: bằng chứng cùng chủ đề nhưng khác phạm vi vẫn bị coi là ủng hộ. GreenScan đặt Comparability Gate 6 chiều trước mọi phép so: loại giá trị, ranh giới, công nghệ, chỉ số con, Scope, mục tiêu hay thực hiện. Lệch một chiều thì trả NOT COMPARABLE. GS-Bench cố ý chèn đúng các nhiễu này. Giới hạn: lỗi đã đo gồm cường độ vs tuyệt đối, công ty mẹ vs tập đoàn, và thiếu chiều phân khúc (segment)."
- *Vặn:* "Ví dụ?" → "'Giảm 30% phát thải Scope 1+2' gặp bảng 'tổng phát thải' có cả Scope 3 thì không được so."
- *Bẫy:* nói cổng bắt được mọi lệch.

**Q16. PDF nhiều bảng xử lý ra sao? Có trích dẫn tới ô bảng như hồ sơ Vòng 1 hứa không?**
- *Trả lời:* "Lỗi đã đo: bảng bị dàn phẳng làm 4/4 model từ 26B trở lên cùng báo SUPPORTED sai hai ca ở bảng khí nhà kính trang 39 của Hòa Phát. Thí nghiệm AG-3 dựng lại hàng bảng từ toạ độ chữ: trang 39 đủ 10 hàng, cộng dọc khớp 3/3; trên 7 ca, đúng 3/7 so với 1/7 khi đọc trang thô, 0 kết luận sai. Dự đoán ban đầu là ít nhất 5/7, nên dự đoán đó trượt. Trích dẫn hiện ở mức trang kèm cờ 'là bảng'; trích dẫn tới ô (trang, bảng, hàng, cột) chưa làm."
- *Vặn:* "Sao không dùng LayoutLMv3 hay TAPAS?" → "Cần GPU và dữ liệu huấn luyện. Chạy ngoại tuyến trên laptop, chúng tôi làm tất định trước (toạ độ chữ + kiểm tổng dọc) và chỉ dùng mô hình khi đo thấy cần."
- *Bẫy:* nói đã trích dẫn tới ô bảng.

**Q17. Truy xuất: sao dùng BM25 + n-gram mà không dùng embedding và reranker như báo cáo khuyên?**
- *Trả lời:* "Truy vấn của chúng tôi nhiều token hiếm và cần khớp chính xác: 'Scope 2', 'tCO2e', số hiệu văn bản. Đó là chỗ BM25 mạnh, lại chạy được ngoại tuyến. Cấu hình: BM25 + n-gram ký tự, gộp RRF k = 60, trọng số 0,55/0,45, lấy 30 ứng viên, giữ 5, luôn giữ 3 đoạn tốt nhất dưới ngưỡng nhưng gắn cờ 'chỉ dùng để bác bỏ'. bge-m3 và bge-reranker-v2-m3 có sẵn adapter nhưng tắt mặc định. Giới hạn: chưa có benchmark Recall@k tiếng Việt, nên chúng tôi không tuyên bố cấu hình nào tốt hơn."
- *Vặn:* "RRF là gì?" → "Cộng nghịch đảo thứ hạng từ các bộ tìm: Σ 1/(60 + hạng). Bền với chênh thang điểm giữa các bộ tìm."
- *Bẫy:* nói "dense đang chạy" (hình Target Pipeline là kiến trúc đích).

**Q18. AI và người chia việc thế nào? Ai chịu trách nhiệm?**
- *Trả lời:* "Trong 8 việc của kiểm toán viên, máy làm phần dò, lật, ghi; người giữ quyết định trọng yếu và chữ ký. Mỗi tuyên bố đi qua máy trạng thái AI đề xuất → đã có người xem → đã chốt, không được nhảy thẳng từ AI sang chốt. Quyết định gồm xác nhận, ghi đè (bắt buộc chọn trạng thái mới), từ chối kết luận, yêu cầu thêm bằng chứng, mở lại; chốt lần hai phải mở lại trước. Nhật ký chỉ ghi thêm; quyết định của người được xuất làm dữ liệu chuẩn; tỷ lệ ghi đè là chỉ số chất lượng của AI. Kết quả có phần do LLM đề xuất luôn gắn cờ 'cần người xác nhận'. Giới hạn: một người soát, chưa có đăng nhập, phân quyền, hay chế độ hai người soát để đo đồng thuận."
- *Vặn:* "Người soát bấm xác nhận hết thì sao?" → "Đó là automation bias. Tỷ lệ ghi đè thấp bất thường là tín hiệu; spec yêu cầu cảnh báo khi chấp nhận claim mâu thuẫn mà chưa mở bằng chứng." [CHƯA XÁC MINH cảnh báo này đã cài.]
- *Bẫy:* nói "AI quyết định".

**Q19. Kết quả có giá trị pháp lý không? Dùng được trước cơ quan quản lý không?**
- *Trả lời:* "Không. Đây là chỉ báo rủi ro và hồ sơ truy vết để chuyên gia xem xét. Báo cáo thiết kế cũng nhận: tranh chấp kiểu H&M 'Conscious Choice' nằm ở chỗ người tiêu dùng hiểu thế nào, ngoài tầm máy. Cái chúng tôi bảo đảm là người khác kiểm lại được: trang nguồn, phép tính, phiên bản quy tắc, hash tài liệu, nhật ký. Câu cố định trên giao diện: 'không phải kết luận pháp lý… thiếu bằng chứng không đồng nghĩa vi phạm'."
- *Vặn:* "Tầng pháp lý của các bạn làm gì?" → "Chọn văn bản có hiệu lực theo ngày công bố. Hiện chưa áp được quy tắc nào (0/156), nên panel pháp lý là bối cảnh, không phải phán quyết."
- *Bẫy:* nói "tự động kiểm tra tuân thủ pháp luật".

**Q20. Dữ liệu chưa công bố của doanh nghiệp có bị gửi ra ngoài không?**
- *Trả lời:* "Mặc định ngoại tuyến. Tài liệu được phân lớp A công khai, B nội bộ, C mật; LLM đám mây chỉ cho lớp A, lớp B và C chuyển người. Groq (gói miễn phí có thể lưu dữ liệu) chỉ dùng cho báo cáo đã công khai. Bộ đọc Qwen3-4B lượng tử Q4 chạy cục bộ, khớp 0,963 với bản đầy đủ. Giới hạn: chưa đo thời gian đọc trên laptop vì thiếu RAM."
- *Vặn:* "Căn cứ pháp luật?" → "Luật Bảo vệ dữ liệu cá nhân 91/2025, theo tài liệu dự án." [CHƯA XÁC MINH điều khoản; test no-egress tự động chưa xác minh.]
- *Bẫy:* nói "không bao giờ gửi dữ liệu" trong khi sản phẩm vẫn có cấu hình cloud.

**Q21. Báo cáo thiết kế đề xuất cụm GPU và 1–3 TB. Các bạn chạy bằng gì, có ổn định không?**
- *Trả lời:* "Sản phẩm chạy trên laptop CPU; thí nghiệm chạy trên Kaggle T4, ước 25–40 giờ GPU. Ổn định: 385 test, 17 bẫy hồi quy, mỗi lượt có manifest và hash để tái lập, ngưỡng đăng ký trước khi chạy. Đúng tinh thần thể lệ: mô hình đơn giản, chạy ổn định."
- *Vặn:* "Báo cáo 300 trang chạy bao lâu?" → "Hai báo cáo của Hòa Phát: 107–121 giây, chưa gồm bộ đọc LLM. Bộ đọc 4B mất 1,7 giây/câu trên T4; trên laptop chưa đo."
- *Bẫy:* hứa thời gian khi đã bật bộ đọc LLM.

**Q22. AI thêm được gì mà người không làm được?**
- *Trả lời:* "Một, đọc hết mọi câu mà không mỏi: 156 tuyên bố, mỗi câu có trang và danh sách thiếu. Hai, phép tính có vết mà ai cũng kiểm lại được, ví dụ 22.540.603 + 933.876 = 23.474.479 so với tổng công bố 23.474.480. Ba, hướng tiếp theo là so chéo năm để bắt 'im lặng có chọn lọc': năm ngoái công bố một chỉ số, năm nay biến mất. Người đọc tay khó bắt vì phải nhớ báo cáo cũ. Giới hạn: phần so chéo năm chưa cài."
- *Vặn:* "Vậy hôm nay đã bắt được im lặng có chọn lọc chưa?" → "Chưa; yếu tố bất thường trong hàng đợi còn chưa tính."
- *Bẫy:* nói như thể tính năng đã chạy.

**Q23. Vì sao 5 thuộc tính bắt buộc là đủ để đánh giá một tuyên bố?**
- *Trả lời:* "Năm thuộc tính là chỉ số, giá trị + đơn vị, kỳ, năm gốc, phạm vi. Chúng trả lời các câu mà GHG Protocol và FTC buộc phải trả lời: đo cái gì, bao nhiêu, kỳ nào, so với mốc nào, cho ranh giới nào. Chúng khớp cơ sở dẫn liệu kiểm toán: Phân loại, Chính xác, Đúng kỳ, Đầy đủ. Thiếu một thuộc tính thì hai số không so được. Giới hạn: chưa có 'Trình bày': mọi số đúng nhưng chọn lọc để tạo ấn tượng sai."
- *Vặn:* "Còn bằng chứng độc lập?" → "Rubric có thành phần 'nguồn độc lập' (8 điểm); hiện kho demo chưa có nguồn độc lập nên thành phần này bị trừ."
- *Bẫy:* nói 5 thuộc tính "đủ để phát hiện tẩy xanh".

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

### 5.1 Mâu thuẫn giữa tài liệu (và cách nói thống nhất)

1. **Người dùng mục tiêu.**
   - Hồ sơ Vòng 1: bộ phận ESG/kiểm toán nội bộ doanh nghiệp tự soát bản nháp.
   - USER_PERSONAS 07/07: 6 persona.
   - AUDITOR 25/09: kiểm toán viên làm tay.
   - Studio 14/10: doanh nghiệp sửa báo cáo của chính mình.
   - giai_thich: 4 nhóm.
   - **Câu thống nhất đề xuất:** "Người dùng đầu tiên là người soát báo cáo phát triển bền vững: phòng ESG hoặc kiểm toán nội bộ tự soát bản nháp. Quy trình của họ giống kiểm toán viên nên sản phẩm thiết kế theo quy trình kiểm toán. Kiểm toán độc lập và ngân hàng là nhóm mở rộng khi đã có số đo."
2. **Thang rủi ro có bốn phiên bản.**
   - OUTPUT_SPEC, EVIDENCE_CARD_SPEC, US-04.03 (07/07): 7 tiêu chí (15/15/10/20/10/20/10), 5 nhãn LOW/MODERATE/HIGH/VERY_HIGH/CRITICAL, LOW 0–20.
   - `risk-rubric-v2` (PRODUCTION_UI_SPEC F6, configs): 9 thành phần, 4 dải, LOW 0–24.
   - giai_thich: "risk profile 3 chiều".
   - `priority-v1.1`: 4 yếu tố.
   - **Nói:** rubric v2 để phân rã vì sao thiếu; priority-v1.1 để xếp hàng đợi; ba chiều là hình minh hoạ.
3. **Điểm cấp doanh nghiệp.** DASHBOARD_SPEC §5.2 (company_risk_score, "High greenwashing risk"), MVP_SCOPE §4.8, US-04.04 vẫn còn. P1/P5 và UI_REVIEW đã bỏ. **Không có điểm doanh nghiệp.**
4. **Trạng thái review.** HUMAN_REVIEW_SPEC có 6 trạng thái (NOT_REQUIRED … ESCALATED). Code (F9) có 3 trạng thái + 5 quyết định. Theo code.
5. **Tầng "mâu thuẫn ngoài" trong MVP_SCOPE và "bằng chứng độc lập" trong giai_thich** đối lập thực tế: 780/780 bằng chứng nội bộ, `has_independent: False` (F6).
6. **Gói nguồn cấm "nâng P2 lên P0 khi P0 chưa xong"**, nhưng Studio (AUTH-001, P2) làm như P0 ngày 14/10 khi P0 truy xuất tiếng Việt và hard-set bảng chưa xong. Lý do nội bộ: định vị 25/09 cần sản phẩm đầu ra; Studio dùng luật sẵn có, chi phí thấp. Nếu bị hỏi về kỷ luật ưu tiên, nói thẳng điều này.
7. **Kế hoạch tháng 8 (SP03)** hẹn tới 13/09 có benchmark truy xuất tiếng Việt, 50–100 trang khó, 20–50 ca end-to-end, release gate. Tại 01/11: AG-5 chưa chạy, hard-set bảng mới 7 ca, chưa có gold. Đừng nói lộ trình 13/08 đã hoàn thành.
8. **Giấy phép dữ liệu lệch nhau.** BC ghi EnvironmentalClaims là "Creative Commons", nhóm ghi CC BY-NC-SA 4.0. BC ghi CLIMATE-FEVER cc-by-sa-4.0, nhóm ghi "chưa rõ". Theo bản ghi của nhóm cho tới khi kiểm thẻ HF.
9. **Số HPG cũ trong UI_REVIEW 08/08** ("31/41 claim thiếu kỳ và năm gốc") so với AUDIT 14/10 (133/156 thiếu kỳ, 152/156 thiếu năm gốc). Dùng số mới.
10. **"Độ bao phủ bằng chứng 72%"** trong mockup là số minh hoạ, không phải số đo.

### 5.2 Số đã cũ so với kết quả 31/10–01/11

- "Mọi model ≥ 4B qua cổng `ag1_ir_path_usable`" (31/10 14:15, trong mẫu): **bị thay**. Ngoài mẫu v1.1 chỉ 8B qua; v1.2: 8B và 32B 0 vu oan, 14B có 1; tập sạch v1.3: mọi model 0 sai.
- "4B mất độ phủ vì đọc năm": **đã rút lại** (01/11 17:00).
- AG-1 4B "precision 1,0, độ phủ 0,134" (11:45), rồi "0,437 / 0,984" (14:15, trong mẫu): ngoài mẫu chỉ 0,093–0,138. Dùng số ngoài mẫu.
- GS-Bench "193 ca" và dự kiến "khoảng 600 ca B-b": nay là 453 ca (402 B-b).
- pytest 215 (20/09) → 385 (14/10). Số mới hơn 14/10 [CHƯA XÁC MINH].
- "FPT dense/rerank (cloud)" trong KE_HOACH_PHAN_BIEN §1: khoá FPT hỏng từ 31/10.
- Groq `qwen/qwen3-32b` đã bị gỡ; cấu hình chọn là `openai/gpt-oss-120b`.
- Registry 11 văn bản (14/10): cập nhật sau đó [CHƯA XÁC MINH].
- AG-2 bốn đường: trượt cổng sản phẩm (9 S sai so với 7 của luật). Chỉ "luật + 4B, bỏ S đơn độc của luật" qua.

### 5.3 Điều không được nói

1. "GreenScan phát hiện doanh nghiệp X tẩy xanh / vi phạm / gian lận" (P4; copy rules §4.6).
2. "Độ chính xác X%" khi chưa có gold người. Với nhãn Claude đã được người soát: nói "trên tập nhãn do Claude tạo, Nhân soát n ca".
3. "Tiết kiệm X% thời gian", "SUS = …": chưa đo.
4. "Tự động kiểm tra tuân thủ pháp luật": 0 quy tắc áp được, panel pháp lý chỉ là bối cảnh.
5. "Đối chiếu với nguồn độc lập (Climate TRACE, GEM…)": chưa có trong demo.
6. "Trích dẫn tới ô bảng": hiện ở mức trang.
7. "Có chatbot hỏi đáp có grounding": không có `/v1/ask`.
8. "Phát hiện im lặng có chọn lọc, so chéo năm/ngành": chưa cài.
9. "Bộ đọc Qwen3 / đường kép đã vào sản phẩm và đổi kết luận": chỉ sau cờ, chỉ trợ giúp người soát.
10. "Chế độ cloud đang chạy": khoá FPT 401.
11. "Dense retrieval và reranker đang chạy": tắt mặc định.
12. Lấy mục tiêu thiết kế của BC (p95 < 300 ms, > 95% numeric exactness…) làm chuẩn ngành hay làm kết quả của GreenScan.
13. Trích BC như nguồn học thuật: BC là bản deep-research do ChatGPT tạo; chỉ trích các nguồn gốc nó dẫn (FTC, EU 2024/825, IFRS, bài ACL) sau khi đã mở kiểm.
14. Các paper 2026 trong gói nguồn (R5 CLARIESG, R6 IR tiếng Việt, R7 MTRAGEval, R8–R10 arXiv 2607/2608) là nhãn B "preprint cần kiểm" [CHƯA XÁC MINH]. Đừng trích số của chúng khi chưa mở bản gốc.
15. Hiển thị điểm hay xếp hạng cấp doanh nghiệp, biểu đồ "xu hướng rủi ro", donut E/S/G (UI_REVIEW).
16. "Quantum làm hệ thống tốt hơn": ngoài cụm R7; theo SP06, demo không phụ thuộc Quantum.
