# Chương 2. Kiến trúc tổng thể

Chương này cho thấy hệ thống gồm những khối nào, dữ liệu chảy qua chúng ra sao, và mô hình nào nằm ở đâu. Điểm cần nhớ: **kết luận chỉ do luồng phân tích (luật và code) đưa ra**; luồng hỏi đáp và các bước có LLM chỉ đọc lại kết quả đã lưu.

## 2.1. Hai luồng xử lý

GreenScan có hai luồng tách biệt:

1. **Luồng phân tích tài liệu** (`OrchestratorAgent`, tệp `src/quantum_gw/agents/orchestrator.py`). Nhận tệp, chạy 10 bước cố định, ghi kết quả vào kho phiên `.quantum/runs/<run_id>/`. Luồng này là nơi duy nhất sinh ra kết luận. Trên máy tối thiểu, nó chạy hoàn toàn bằng luật, phép tính và truy xuất từ vựng; không có mô hình nơ-ron nào ngoài mô hình LSTM bên trong Tesseract OCR.
2. **Luồng hỏi đáp** (máy chủ MCP `src/quantum_gw/mcp_server.py` và harness `src/quantum_gw/agent_harness.py`). Nhận câu hỏi bằng tiếng Việt, kiểm phạm vi, lập kế hoạch gọi công cụ, chạy công cụ trên kho phiên, rồi viết câu trả lời. Các công cụ chỉ đọc kết quả đã lưu; không công cụ nào tự đưa ra kết luận mới.

**Hình 2.1** là sơ đồ 10 bước của luồng phân tích, kèm số liệu thật của hai ca minh hoạ ở mỗi bước.

{{IMG_PIPELINE}}

**Hình 2.2** là bản đồ toàn hệ thống (vẽ lại 13/11/2026), gồm cả luồng hỏi đáp. Đọc từ trái sang phải: tài liệu đi qua khối phân tích (xanh dương) vào kho phiên; câu hỏi đi từ trên xuống, qua chốt phạm vi (xanh lá đậm), được ghép thành lời nhắc (giấy trắng), gửi cho LLM `gpt-oss-120b` qua Groq (tím, chỉ khi `public=true`), LLM chọn công cụ MCP (cam), kết quả công cụ quay lại LLM để viết câu trả lời, câu trả lời qua bộ kiểm `guards.new_numbers` (vàng) rồi mới tới người dùng. Đường nét đứt đỏ là đường lùi về luật khi LLM lỗi hoặc câu trả lời bị chặn. Khung nét đứt dưới các khối là mô hình nhỏ đã huấn luyện trên Kaggle nhưng chưa được cắm vào vì chưa qua cổng đánh giá đã đăng ký.

{{IMG_MAP}}

## 2.2. Mười bước của luồng phân tích

| # | Tên bước trong mã (`PLAN`) | Việc làm | Mô-đun chính |
|---|---|---|---|
| 1 | `validate_inputs` | Kiểm đầu vào, cấp mã phiên, ghi manifest | `orchestrator.py` |
| 2 | `parse_and_ocr_documents` | Đọc PDF/Word/văn bản, OCR trang quét, phân vùng trang (cột chữ, bảng có và không kẻ ô), tách đoạn, kiểm toàn vẹn và chất lượng đọc | `agents/intake.py`, `parsers/layout.py`, `parsers/*` |
| 3 | `extract_green_claims` | Tìm câu tuyên bố môi trường, trích thuộc tính (chỉ số, số liệu, kỳ, năm gốc, phạm vi) | `agents/claim_extractor.py`, `agents/claim_quality.py` |
| 4 | `build_hybrid_retrieval_index` | Dựng chỉ mục truy xuất trên mọi đoạn của bộ hồ sơ | `agents/retriever.py`, `retrieval/hybrid.py` |
| 5 | `retrieve_evidence_per_claim` | Lấy 5 đoạn bằng chứng tốt nhất cho mỗi tuyên bố | `retrieval/hybrid.py` |
| 6 | `verify_claim_evidence_pairs` | So số, xét từ khoá lập trường, quyết định mức kết luận | `agents/verifier.py`, `verification/*` |
| 7 | `check_applicable_law` | Gắn văn bản pháp lý đang hiệu lực và quy tắc áp dụng | `agents/legal_check.py`, `legal/*` |
| 8 | `score_greenwashing_risk` | Chấm rủi ro 9 thành phần, đọc số liệu công bố (cả ô bảng), kiểm bảng, xếp hàng soát, rút mẫu kiểm ngoài hàng | `agents/scorer.py`, `agents/figures.py`, `agents/prioritizer.py` |
| 9 | `apply_quality_gates` | Chạy 10 cổng chất lượng G0–G9, quyết định trạng thái phát hành | `agents/reviewer.py` |
| 10 | `write_evidence_pack` | Ghi `result.json`, `evidence_pack.md`, ba lớp dữ liệu hợp đồng | `agents/reporter.py`, `data/export.py` |

Bước 6 đến bước 8 chạy theo vòng lặp trên từng tuyên bố: kiểm chứng, rồi pháp lý, rồi rủi ro. Phần kiểm số liệu công bố và xếp hàng soát chạy một lần cho cả phiên sau vòng lặp.

## 2.3. Mô hình nằm ở đâu

Bảng dưới lấy từ tài liệu `docs/04-data-ai/MCP_MAY_TOI_THIEU.md` (13/11/2026) và đã được đối chiếu với cấu hình của lượt chạy trong tài liệu này.

| Công đoạn | Công cụ MCP / mã | Mô hình hoặc engine | Trên máy tối thiểu |
|---|---|---|---|
| Chọn công cụ | ứng dụng MCP (Claude Desktop…) | LLM của client | ngoài hệ thống |
| Chốt phạm vi | `check_scope` · `scope_guard.rules_route` | luật (không mô hình) | **đang dùng** |
| Chốt phạm vi (thay luật) | bộ định tuyến | e5-small + Qwen3-0.6B LoRA GGUF | chờ cổng `prompt_router_v1` |
| Lập kế hoạch | `ask_greenscan` · `agent_harness.llm_plan` | Groq `openai/gpt-oss-120b` | chỉ khi `public=true`; lỗi thì về luật |
| Đọc tài liệu | `analyze_documents` | PyMuPDF, pdfplumber, Tesseract OCR | đang dùng |
| Trích tuyên bố | `analyze_documents`, `claim_attributes` | luật taxonomy + biểu thức chính quy | đang dùng |
| Lọc tuyên bố bằng mô hình | `claim_model.py` | multilingual-e5-small (T1) | **tắt** (trượt cổng S1) |
| Truy xuất | `analyze_documents`, `find_evidence` | BM25 + bộ chấm "lite" | đang dùng |
| Xếp lại bằng chứng | — | bge-reranker-v2-m3 tinh chỉnh | chờ cổng |
| So số và lập trường | `analyze_documents` | code so số + bộ từ khoá | đang dùng |
| Lập trường bằng mô hình | `verification/llm_judge.py` | LLM stance; mDeBERTa-xnli; Qwen3-4B LoRA | **tắt** |
| Rủi ro, hàng soát, pháp lý | `analyze_documents`, `review_queue` | luật (`scoring_v1`, `priority_v1`) | đang dùng |
| Lời giải thích (S6) | cờ `assist_explain` | Ollama Qwen3-4B Q4 hoặc API | tuỳ chọn, mặc định tắt |
| Viết câu trả lời | `agent_harness.audited_answer` | Groq `openai/gpt-oss-120b` | chỉ khi `public=true` |
| Kiểm câu trả lời | `guards.new_numbers` | code | đang dùng |

**Công tắc mô hình (`model-mode-v1`, từ 16/11).** Trên giao diện (trang Cài đặt và trang Phân tích mới), người dùng đổi được giữa ba chế độ khi máy chủ đang chạy: **chỉ luật** (mặc định, đúng như bảng trên); **mô hình trên máy** (Ollama `qwen3:4b-instruct-2507-q4_K_M`, tài liệu không rời máy); **mô hình trên đám mây** (Groq `gpt-oss-120b`, chỉ cho tài liệu đã công bố). Mã: `src/quantum_gw/model_mode.py`, API `POST /v1/runtime/model-mode` và `/v1/runtime/model-test`. Khi bật mô hình, các bước hỗ trợ ở Chương 5 chạy. Mô hình không bao giờ tự viết kết luận "được ủng hộ" hay "mâu thuẫn", nhưng có thể chuyển một kết luận trung gian sang "ủng hộ một phần" kèm cờ chờ người. Ví dụ ở Ca A với mô hình trên máy, một tuyên bố chuyển từ "chưa được chứng minh" sang "ủng hộ một phần" kèm cờ chờ người. Vì vậy không được nói "bật mô hình thì kết luận không đổi". Mọi bảng kết quả trong tài liệu này chạy ở chế độ chỉ luật.

## 2.4. Bản đồ mã nguồn

{{CODE_MAP}}

## 2.5. Tóm tắt chương

- Hệ thống có hai luồng: phân tích (sinh kết luận, toàn luật) và hỏi đáp (chỉ đọc kết quả).
- Luồng phân tích có 10 bước cố định, mỗi bước ghi sự kiện vào `audit.jsonl`.
- LLM chỉ xuất hiện ở lập kế hoạch, viết câu trả lời và bốn bước hỗ trợ tuỳ chọn; mọi đầu ra của LLM đều qua bộ kiểm bằng code.
- Các mô hình nhỏ huấn luyện trên Kaggle chưa được cắm vào sản phẩm vì chưa qua cổng đánh giá đã đăng ký trước.
