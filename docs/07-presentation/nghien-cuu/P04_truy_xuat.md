# P04 · Truy xuất bằng chứng

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Với mỗi tuyên bố, tìm các đoạn ứng viên trong thư viện tài liệu của doanh nghiệp. Truy xuất chỉ tìm ứng viên, không quyết định sự thật **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2, bước 5; bất biến 3).

## 2. Lỗi hoặc rủi ro đã đo được

- Tương đồng chữ không phải bằng chứng. Khi tắt LLM, 713 cặp được đoán theo độ giống chữ và mặc định PARTIAL **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`, bảng A/B).
- Khi bật mô hình không chốt chặn, 327 cặp được nhận là chỉ bối cảnh và 151 là xác nhận; số này cho thấy đọc nội dung cần thiết **[ĐÃ THỰC NGHIỆM]** (cùng file, mục "Đọc bảng").
- Thay đổi "Hybrid RAG + reranker" trên slide vì cấu hình thực tế là `embedding: lite`, `reranker: none` **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-04).

## 3. Thiết kế hiện tại, file code, cấu hình

- Điểm = 0,55 × BM25 + 0,45 × n-gram ký tự 3–5 (hoặc embedding nếu bật). RRF chỉ đổi thứ tự. Lấy 30 ứng viên, giữ 5, luôn giữ 3 ứng viên tốt nhất kèm cờ dưới ngưỡng **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2).
- Cấu hình: `configs/default.yaml` với `embedding: lite`, `reranker: none` **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-04).
- Thứ tự ưu tiên khi xếp hạng: số liệu có cấu trúc, luật, BM25 chính xác, ngữ nghĩa, nguồn ngoài, nguồn tiếp thị **[KIẾN THỨC NỀN]** (`docs/04-data-ai/RETRIEVAL_POLICY.md`, mục 8.1).

## 4. Vì sao chọn, phương án đã bỏ

- Chọn `lite` (BM25 và n-gram, RRF) vì chạy được trên CPU không GPU, và chưa đo BGE-M3 **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-04).
- BGE-M3 chạy local mất khoảng 7,7 giờ cho thư viện; nên dùng API FPT `Vietnamese_Embedding` **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 4).
- Bỏ GraphRAG và đa tác tử: không đo được failure mode cần đến **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, cấm mục cuối).

## 5. Số đo có n

- Thư viện 11 doanh nghiệp: 15.409 trang, 14.708 vector đã lưu **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 4).
- Chưa có số đo nào của RQ4 (bật BGE-M3?) và RQ5 (reranker giúp?). Cần đo trên gold. THIẾU: bảng Recall@k, MRR, nDCG của lite so với BGE-M3. Cách lấy: chạy `tools/measure_all.py` sau khi có gold lô 1.
- Chỉ số AG-5: recall@k và k nhỏ nhất đạt recall 95 % **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, AG-5).

## 6. Giới hạn và yếu tố gây nhiễu

- Thiên lệch pooling: nhãn chỉ có cho các trang bộ truy xuất đề xuất, nên mức tăng đo được là cận dưới **[KIẾN THỨC NỀN]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 3).
- Gửi mọi đoạn của mọi tài liệu tới API embedding khi bật, nên đã để tắt mặc định. Rủi ro riêng tư **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 3).

## 7. Lỗi đã gặp và cách gỡ

- Tương đồng chữ đang đóng vai kết luận mặc định cho 713 cặp (PARTIAL), trong khi bất biến 3 cấm điều này. Gỡ bằng cách đọc nội dung cặp qua mô hình có chốt chặn `llm_stance_decisive: false` **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`; `docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 3).

## 8. Trạng thái năng lực

- `lite` (BM25 + n-gram + RRF): **IMPLEMENTED–NOT VALIDATED**.
- BGE-M3 và reranker: **RESEARCH-BACKED–NOT IMPLEMENTED** cho cấu hình baseline; có mã nhưng chưa bật và chưa đo **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-04).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- AG-5 (03–06/11): so `lite` với multilingual-e5 tinh chỉnh (cặp bạc, chia theo công ty) và với reranker gte-multilingual **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, AG-5).
- Ngưỡng bật BGE-M3: ΔRecall@5 ≥ +10 điểm và thời gian ≤ 2 lần `lite` **[GIẢ THUYẾT]** (`docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`, mục 2).

## 10. Hình nên vẽ và file dữ liệu

- Đường cong Recall@k theo phương pháp; cột thời gian mỗi tuyên bố.
- Câu hỏi QA_BANK cần trả lời: Q6 (vì sao 30 → 5), Q12 (RRF), Q13 (reranker), Q17 (bằng chứng ngoài top-k), Q27 (prompt injection). Đọc đáp án trong `docs/07-presentation/QA_BANK_100_2026-09-20.md`.
- THIẾU: kết quả đo truy xuất. Cách lấy: chạy `tools/measure_all.py` khi có gold.
