# Hệ thống GreenScan đang xử lý thế nào — bản đồ theo mã nguồn

**Ngày:** 10/10/2026 · **Căn cứ:** đọc mã tại commit `ea89809` (đường dẫn dưới đây tính từ gốc repo, `src/` = `src/quantum_gw/`) · **Mục đích:** một chỗ duy nhất trả lời "hệ thống làm gì, ở đâu, dữ liệu đi đâu" trước khi thiết kế chế độ ngoại tuyến một phần ([`../04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`](../04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md)) và phần huấn luyện ([`../../training/README.md`](../../training/README.md)).

---

## 1. Cửa vào

| Cửa | Lệnh / đường dẫn | Ghi chú |
| --- | --- | --- |
| Khởi động một chạm | `GreenScan.bat` / `start.sh` → tạo `.venv`, `pip install -e .`, `npm ci && npm run build` lần đầu, chép `.env.example` → `.env` nếu thiếu, chạy `quantum-agent app` ở `127.0.0.1:8000` | giao diện + API cùng cổng, tiền tố `/api` bị gỡ bởi middleware (`api.py:34-57`) |
| CLI | `quantum-agent analyze PATHS --roles --source-types` · `demo` · `evaluate` (golden) · `evaluate-real` (4 ca thật) · `serve` · `app` (`cli.py`) | tài liệu chạy bằng CLI **không** được lưu vào kho tài liệu → trang gốc không mở được trên giao diện |
| API phân tích nền | `POST /v1/jobs/analyze/files` (tải tệp, tên doanh nghiệp, tên phiên) → `GET /v1/jobs/{id}` báo từng bước (`api.py:203-232`, `jobs.py`) | 1 luồng xử lý mặc định (`QUANTUM_JOB_WORKERS`), giữ 50 job gần nhất trong bộ nhớ |
| API đọc kết quả | `/v1/runs`, `/v1/runs/{id}`, `/v1/runs/{id}/export?format=json\|md\|manifest\|audit`, `/v1/runs/{id}/workpaper`, `/v1/documents/{doc_id}[/meta\|/page/{n}?q=]`, `/v1/reviews…`, `/v1/runtime`, `/v1/legal/corpus` | ảnh trang PDF dựng tại máy bằng PyMuPDF, có tô sáng |
| Giao diện | 3 bước: *Tải tài liệu* → *Soát theo hàng đợi* → *Giấy làm việc*; phụ: *Tất cả tuyên bố*, *Lịch sử*, *Thư viện pháp lý*, *Cài đặt & chế độ chạy* | quyết định người soát → `POST /v1/reviews` (chỉ ghi thêm) |

---

## 2. Mười bước của một lượt phân tích (`agents/orchestrator.py`)

| # | Bước (tên trong thanh tiến độ) | Làm gì | Đầu ra |
| --- | --- | --- | --- |
| 1 | `validate_inputs` | Kiểm danh sách tài liệu, tạo `run_id`, thư mục phiên, nhật ký; ghi `manifest.json` ngay đầu | `RunManifest` |
| 2 | `parse_and_ocr_documents` | PyMuPDF đọc chữ theo khối; trang < 40 ký tự → Tesseract OCR **tại máy**; pdfplumber tách bảng thành một khối `TABLE` nguyên vẹn; cắt đoạn ≤ 3 câu / ~600 ký tự; hồ sơ độ phủ kho tài liệu | `EvidenceChunk[]`, `CorpusProfile` |
| 3 | `extract_green_claims` | Bộ trích **bằng luật**: khớp từ điển `configs/taxonomy.yaml`, loại tiêu đề/mục lục/dòng bảng/câu cụt (mỗi câu loại ghi lý do), gán 5 thuộc tính bằng regex | `Claim[]` |
| 4 | `build_hybrid_retrieval_index` | Dựng bộ truy xuất, bộ kiểm chứng, bộ pháp lý, bộ chấm điểm | — |
| 5 | `retrieve_evidence_per_claim` | Điểm = 0,55 × BM25 + 0,45 × n-gram ký tự 3–5 (hoặc embedding nếu bật); RRF chỉ đổi thứ tự; lấy 30 ứng viên, giữ 5; luôn giữ 3 ứng viên tốt nhất (gắn cờ dưới ngưỡng); gắn cờ dấu hiệu tiêm lệnh | `RetrievedEvidence[]` mỗi tuyên bố |
| 6 | `verify_claim_evidence_pairs` | **Chỉ** khi bật mô hình: hỏi trước một lượt mọi cặp luật không quyết được | sự kiện `llm_stance_prefetch` |
| 7 | `check_applicable_law` | Với từng tuyên bố: **kiểm chứng** (số học → cụm từ → chiều thay đổi → độ giống; mô hình chỉ cho cặp khó) · **pháp lý** (văn bản đang hiệu lực, chuỗi sửa đổi theo vấn đề, bộ quy tắc) · **chấm rủi ro** 9 thành phần | `VerificationResult`, kết quả pháp lý, `RiskAssessment` |
| 8 | `score_greenwashing_risk` | Đọc số liệu công bố, **cộng lại bảng**, đối chiếu chéo tài liệu; nhận diện chủ thể; **xếp hàng đợi** (`priority-v1.1`: trọng yếu 40 · nghĩa vụ 25 · khoảng trống bằng chứng 25 · bất thường 10 — chưa tính) | `priorities`, `figure_checks` |
| 9 | `apply_quality_gates` | 8 cổng G0–G7 → `BLOCKED` / `PENDING_HUMAN_REVIEW` / `RELEASABLE` | `quality_gates`, `release_status` |
| 10 | `write_evidence_pack` | Ghi `result.json`, `evidence_pack.md`, 3 tầng dữ liệu `contract/` | — |

**Quy tắc kết luận** (`agents/verifier.py`): mâu thuẫn do luật/số học → `CONTRADICTED`; mâu thuẫn do mô hình → chỉ `PARTIALLY_SUPPORTED` (chốt chặn `llm_stance_decisive: false`); `SUPPORTED` cần đoạn từ **tài liệu khác**, điểm ≥ 0,22, và khớp số hoặc cụm từ xác nhận cùng chỉ số/kỳ/phạm vi + ≥ 2 thuộc tính; `UNSUPPORTED` chỉ khi kho đủ để suy ra vắng bằng chứng, còn lại `INSUFFICIENT_EVIDENCE`. Số học: dung sai = ½ chữ số cuối đã công bố (trần 10%); lệch ≥ 0,35 → bác bỏ; ở giữa → khớp một phần.

**Pháp lý trong thực tế:** bộ quy tắc có 1 quy tắc nháp nhắm loại tuyên bố mà taxonomy không bao giờ sinh ra → mọi tuyên bố ra `INSUFFICIENT_EVIDENCE` pháp lý, `rules_applied: []`.

---

## 3. Dữ liệu rời máy ở đâu — bảng đầy đủ

Trong `src/`, chỉ ba nhóm mã gọi HTTP ra ngoài: `providers/*.py` (mô hình ngôn ngữ), `retrieval/embeddings.py`, `retrieval/rerank.py`. OCR là tiến trình tại máy.

| Nguồn gọi | Bật khi | Gửi gì | Cắt độ dài |
| --- | --- | --- | --- |
| Mô hình đọc cặp khó (`verification/llm_judge.py`) | `QUANTUM_LLM_STANCE=on_ambiguous` và có nhà cung cấp được cấu hình | lời dặn hệ thống (~600 ký tự, cố định) + **nguyên văn câu tuyên bố + nguyên văn đoạn bằng chứng** — số liệu, tên doanh nghiệp, tên cơ sở đi kèm nếu có trong câu | **không cắt** — một bảng pdfplumber đi nguyên khối |
| Embedding (`EMBEDDING_PROVIDER=fpt\|http`) | không bật mặc định | **mọi đoạn của mọi tài liệu** + từng câu tuyên bố | 6.000 ký tự (FPT) |
| Reranker (`RERANKER_PROVIDER=fpt\|http`) | không bật mặc định | câu tuyên bố + tới 30 đoạn ứng viên | 4.000 ký tự/đoạn |
| Kiểm tra sức khoẻ `/v1/gateway/health?live=true` | khi bấm | chỉ `GET /models` | — |
| Công cụ đo (`tools/measure_all.py`, `evaluate_gold.py`) | khi chạy | đoạn kho công khai và gold cho embedding/rerank/mô hình | — |

| Chế độ (`QUANTUM_PROFILE`) | Ra ngoài |
| --- | --- |
| `offline` | **không gì cả** — đã kiểm 09/10: chặn mọi kết nối khi phân tích 264 trang → 0 lần |
| `cloud` | cặp khó → FPT (định tuyến cố định GLM-5.2 cho việc này) |
| `gpu` | vLLM tại máy, nhưng **chuỗi dự phòng `local,fpt` gửi sang FPT khi mô hình tại máy lỗi** (mâu thuẫn với tài liệu "không rời máy") |
| không đặt | thứ tự dự phòng mặc định `local,fpt,gemini,openai,anthropic` |

**Lưu tại máy:** câu trả lời mô hình `.quantum/llm_cache/stance_cache.jsonl` (khoá = băm của phiên bản prompt + tuyến + câu + đoạn; lưu quan hệ và **lý do** — lý do có thể diễn lại nội dung tài liệu); vector `.quantum/emb_cache/vectors.sqlite3`; số token chỉ ghi trong sự kiện `llm_stance_prefetch`. **Không có sổ ghi từng lần gửi đi** (tài liệu `DATA_FLOW.md` yêu cầu có).

---

## 4. Lưu trữ

| Đường dẫn | Nội dung |
| --- | --- |
| `.quantum/runs/<id>/manifest.json` | phiên bản pipeline, `config_hash` (băm cấu hình sau khi áp biến môi trường — **không** băm nội dung các tệp YAML), mã băm từng tài liệu đầu vào, `rule_pack_version` (đang là đường dẫn tệp), `prompt_version` |
| `…/audit.jsonl` | nhật ký sự kiện, chỉ ghi thêm |
| `…/result.json`, `evidence_pack.md`, `contract/{raw,clean,extract}.jsonl`, `label.json` | kết quả, gói bằng chứng, 3 tầng dữ liệu (tầng extract giữ mọi câu bị loại kèm lý do), tên phiên |
| `.quantum/documents/` | tệp gốc người dùng tải lên (theo SHA-256) — nguồn cho xem trang gốc |
| `.quantum/reviews/decisions.jsonl` | quyết định người soát, chỉ ghi thêm, trạng thái AI_SUGGESTED → HUMAN_REVIEWED → FINALIZED |

---

## 5. Dữ liệu ngoài một lượt chạy

- **Kho công khai:** `data/crawl/vn30/contract/` — 1.061 tài liệu (670 có bản gốc), 15.658 đoạn, 11.746 câu ứng viên, 21 doanh nghiệp, đã chia train/dev/test theo doanh nghiệp. Dựng lại bằng `tools/data_contract.py migrate-crawl`.
- **Gold:** `data/gold/sessions/*.jsonl` (8 + 20 + 30 + 30 cặp, chưa gán) · `tools/labeling_pack.py` (Excel ra/vào, κ) · `tools/evaluate_gold.py` (đo truy xuất và kiểm chứng tách rời) · `tools/measure_all.py` (ngưỡng đăng ký trước ở `configs/measurement_decisions.yaml`).
- **Thực nghiệm 10/10:** `benchmark/size_ladder_2026-10-10/` — thang mô hình, chế độ che dữ liệu, thử nhận diện lại doanh nghiệp.
- **Huấn luyện:** `training/` (dữ liệu dựng lại được, không commit).

---

## 6. Cổng kiểm thử

359 kiểm thử (`pytest`). Chính: `test_verdict_traps.py` (47 bẫy kết luận), `test_audit_checklist.py` (17 ca checklist kiểm toán), `test_architecture_invariants.py` (15 bất biến, kể cả thứ tự số học → cụm từ → mô hình), `test_legal_*` (pháp lý), `test_review_priority.py` (hàng đợi), `test_llm_stance_batch.py` (mô hình giả lập: không tự quyết, bộ nhớ đệm), `test_product_api.py` (job, `/api`, giấy làm việc). `conftest.py` tắt mô hình và cách ly thư mục phiên — **nhưng không tắt embedding/reranker** nếu `.env` bật chúng.

---

## 7. Chỗ cấu hình, tài liệu và mã không khớp nhau — việc cần sửa

| # | Không khớp | Mức |
| --- | --- | --- |
| 1 | Chế độ `gpu` mô tả "tài liệu không rời máy" nhưng dự phòng sang FPT | 🔴 với tài liệu mật |
| 2 | Nhãn "không gọi mô hình (ngoại tuyến)" trên giấy làm việc chỉ dựa vào `prompt_version` — phiên dùng embedding/rerank FPT vẫn ghi ngoại tuyến; `/v1/runtime` bỏ qua nhà cung cấp `http` và URL tại máy trỏ ra ngoài | 🔴 |
| 3 | Không có sổ ghi từng lần gửi đi (yêu cầu ở `DATA_FLOW.md`) | 🟠 |
| 4 | Mô hình đọc cặp khó gửi đoạn bằng chứng **không cắt** (bảng nguyên khối), trong khi embedding cắt 6.000, rerank 4.000 | 🟠 |
| 5 | `.env` máy này ghi `FPT_LLM_MODEL=Qwen3.6-27B` (mô hình vùng Nhật đã bị loại) — `/v1/gateway/health` báo mô hình này, còn việc thật dùng GLM-5.2 qua định tuyến; `LLM_PROVIDER` không có tác dụng với việc này | 🟡 |
| 6 | Cổng G3 luôn đạt (`reviewer.py:33`) | 🟡 |
| 7 | Tham số không ai đọc: `claim_extraction.provider`, `minimum_confidence` (giá trị thấp nhất tính được 0,48 > 0,40), `chunk_overlap_chars`, `reranker.candidate_k/final_k` + `RERANK_*`, `deterministic_seed` | 🟡 |
| 8 | Manifest ghi đường dẫn thay vì nội dung (bộ quy tắc, taxonomy, cue, rubric, định tuyến), không ghi commit git, không ghi danh tính mô hình embedding | 🟡 |
| 9 | Tên bước trên thanh tiến độ không khớp việc làm (bước 6, 7, 8 ở §2) | 🟡 |
| 10 | Tài liệu cũ mô tả thứ không có: `API_CONTRACTS.md` (endpoint `/cases/…`), `PROMPT_CONTRACTS.md` (6 prompt, thực tế 1), `EXTRACTION_SPEC.md` (đoạn 500–900 token, thực tế 600 ký tự) | 🟡 |
| 11 | Bộ quy tắc pháp lý ghi "chưa dùng tới khi gắn điều khoản" nhưng registry đánh dấu QĐ 21/2025 `ok_ocr`; checker không kiểm `source_clauses`/`reviewed_by` | 🟡 |
| 12 | Nhãn phiên bản rubric `risk-rubric-v2` trong YAML, `v1` trong mặc định mã | 🟢 |
| 13 | Docstring `RunStore` lỗi thời (không nhắc `label.json`, `contract/`) | 🟢 |
