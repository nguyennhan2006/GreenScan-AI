# 05 · AI/NLP cho kiểm chứng tuyên bố — và cách đo trung thực trên bộ gold nhỏ

**Cập nhật:** 06/10/2026 · Nguồn đầy đủ (mỗi nguồn có nhãn ADOPT / TEST / AVOID / CONTEXT, kèm số liệu và đường dẫn): [sources/…tong-quan-tai-lieu-AI-NLP.md](sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md). Mã [S…] dưới đây trỏ vào tài liệu đó.

## 1. Kiến trúc GreenScan so với tài liệu — chỗ đã đúng

| Lựa chọn của GreenScan | Tài liệu nói gì | Nguồn |
| --- | --- | --- |
| Pipeline phân rã, truy vết được, có người giám sát; không tuyên bố "phát hiện greenwashing" | **Chưa có bộ dữ liệu greenwashing đã xác minh**; survey mới nhất khuyến nghị đúng kiến trúc này | Calamai và cs. (v2, 01/2026) [S1.2]; Moodaley & Telukdarie 2023 [S1.1] |
| **Số học do code**, mô hình không được ghi đè | LLM giảm tới **62%** độ chính xác khi số bị nhiễu (NumPert 2025); mô hình frontier ~**74%** trên cặp chỉ khác một con số (Aarnes & Setty, 30/09/2026); FinQA suy luận ≥ 3 bước chỉ **22,78%**; FinDVer trên báo cáo tài chính: LLM tốt nhất **77,2%** so với chuyên gia **93,3%** | [S2.7, S2.8, S2.12, S2.14] |
| `INSUFFICIENT_EVIDENCE` là kết quả hợp lệ, do **luật** quyết | Mọi benchmark kiểm chứng chuẩn có lớp này (FEVER, SciFact, AVeriTeC, Climate-FEVER); **LLM lớn thường trả lời sai thay vì từ chối khi ngữ cảnh không đủ** (Joren và cs., ICLR 2025) | [S2.1–S2.4, S2.19] |
| `PARTIALLY_SUPPORTED` / `CONTRADICTED` và quy tắc gộp nhãn tất định | AVeriTeC có lớp *Conflicting Evidence/Cherry-picking*, Climate-FEVER có *DISPUTED*; quy tắc gộp gần như trùng logic GreenScan; "cherry-picking" trong công bố khí hậu đã được kiểm chứng thực nghiệm (Bingler và cs. 2022) | [S2.3, S2.4, S1.4] |
| Đánh giá **tách** truy xuất và kiểm chứng | Thiết kế RAG phải theo từng task; có lỗi ảnh hưởng 12,6% mẫu ngay cả khi tài liệu hoàn hảo | Zhao và cs., **ACM TOSEM 2026** (arXiv:2411.19463 **v3**, đổi tên) [S2.5b] |
| Mô hình chỉ gợi ý, người chốt; giao diện hiện bằng chứng gốc | Kiểm chứng viên chuyên nghiệp đòi giải thích dựa trên bằng chứng (Warren và cs., CHI 2025); **lời giải thích của AI có thể làm người dùng tin cả khi AI sai** (Bansal và cs., CHI 2021) | [S3.16–S3.18] |

**Đính chính trích dẫn:** `docs/research/README.md` trích Zhao và cs. 2024 theo v1 (*"Towards Understanding Retrieval Accuracy and Prompt Quality in RAG Systems"*). Bản v3 (29/05/2026) đổi tên thành *"Understanding the Fundamental Design Decisions of Retrieval-Augmented Generation Systems"*, đăng ACM TOSEM 2026 — đã ghi chú phiên bản trong README (06/10).

## 2. Chỗ tài liệu cảnh báo GreenScan

1. **Bộ trích tuyên bố dựa từ khoá sẽ bỏ sót.** Trên tiếng Anh, SVM n-gram đạt F1 ~69–71, transformer ~84–85; khoảng cách recall tới 25 điểm vì "không phải tuyên bố môi trường nào cũng chứa từ khoá" (Stammbach và cs., ACL 2023) [S1.5]. → **Đo recall**: lấy mẫu các câu *không* được trích, cho người xem có bỏ sót tuyên bố không.
2. **κ ≥ 0,7 là mục tiêu cao** so với các bộ cùng loại:

   | Bộ dữ liệu | Hệ số đồng thuận |
   | --- | --- |
   | Environmental claims | Krippendorff α = 0,47 |
   | Climate-FEVER (bằng chứng) | α = 0,334 |
   | AVeriTeC | free-marginal κ = 0,619; Fleiss κ = 0,503 |
   | FEVER | Fleiss κ = 0,684 |
   | ViFactCheck (tiếng Việt, tin tức) | Fleiss κ = 0,83 |

   Đạt 0,7 là điểm mạnh; không đạt thì báo trung thực, kèm đồng thuận theo từng lớp và ma trận nhầm lẫn giữa hai người.
3. **LLM-as-judge** có thiên lệch vị trí và tự ưu tiên; dữ liệu kiểm chứng tiếng Việt do LLM sinh kém dữ liệu người viết (To và cs. 2024) → **không dùng LLM tự chấm gold** (đúng quyết định hiện tại) [S3.8–S3.12].
4. **Calibration của LLM không đáng tin** cho trích KPI định lượng (ESGReveal 76,9%) → vai trò đúng của GLM-5.2 là *gợi ý quan hệ cho cặp luật không quyết được*, không "đọc hiểu toàn bộ báo cáo" [S5.1, S5.6].

## 3. Tài nguyên tiếng Việt dùng được — kèm giấy phép

**Embedding** (VN-MTEB, Findings of EACL 2026 — dữ liệu **dịch máy** từ MTEB tiếng Anh):

| Mô hình | Tham số | Retrieval | Trung bình 6 loại | Giấy phép | Ghi chú |
| --- | --- | ---: | ---: | --- | --- |
| multilingual-e5-large-instruct | 560M | 40,88 | 67,99 | MIT | cao nhất trong nhóm ≤ 600M |
| bge-m3 | 568M | 39,84 | 64,90 | MIT | |
| gte-multilingual-base | 305M | 38,38 | 65,22 | Apache-2.0 | mạnh nhất ≤ 305M |
| AITeamVN/Vietnamese_Embedding (đang dùng qua FPT) | 568M | 34,18 | 63,34 | **Apache-2.0 trên HF, CC-BY-NC-4.0 trên trang FPT** | ClimateFEVER-VN: 13,25 so với bge-m3 21,27 |
| multilingual-e5-small | 118M | 34,12 | 60,66 | MIT | ~1/14 phép tính của bge-m3 — hợp CPU 8 GB |

**Thứ hạng đảo theo bộ dữ liệu**: trên văn bản luật Zalo, model card của AITeamVN báo điều ngược lại [self-reported]. → **Chỉ gold của GreenScan quyết được** mô hình nào dùng; phải A/B Vietnamese_Embedding với bge-m3 trước khi nói "dùng embedding tiếng Việt chuyên biệt".

**Reranker có số tiếng Việt** (mMARCO-vi, cũng là bản dịch): ViRanker MRR@10 0,7107 và PhoRanker NDCG@10 0,7422 (135M, cần tách từ VnCoreNLP, chỉ 256 token) đều vượt bge-reranker-v2-m3 (0,6209 / 0,6872) [self-reported]. Tránh jina-reranker (CC-BY-NC).

**NLI và kiểm chứng tiếng Việt:**

| Tài nguyên | Kích thước | Giấy phép | Dùng cho |
| --- | --- | --- | --- |
| mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 | ~0,3B | MIT | **Tiền lọc quan hệ** trước khi gọi GLM-5.2 (XNLI-vi 0,793) — TEST |
| ViFactCheck | 7.232 cặp | **MIT** | Bộ kiểm chứng tiếng Việt cấp phép thoáng nhất (tin tức) |
| ViNLI · ViANLI · XNLI-vi | 30k · 10k · 7,5k | nghiên cứu / CC-BY-NC-SA / CC-BY-NC | Chỉ cuộc thi, nghiên cứu |
| phobert-base-v2 | 135M | **AGPL-3.0** | Tránh nếu hướng thương mại (bkai bi-encoder xây trên nó) |

**Bẫy giấy phép:** environmental_claims, AVeriTeC, XNLI, QuanTemp, ViANLI là **phi thương mại** — dùng được cho cuộc thi và nghiên cứu, không cho sản phẩm thương mại.

## 4. Đo trung thực khi gold chỉ có 60–100 cặp

**Khoảng tin cậy 95% (Wilson) của accuracy** [tự tính]:

| n | p̂ = 0,70 | p̂ = 0,80 | p̂ = 0,90 |
| --- | --- | --- | --- |
| 60 | ±11,3 điểm | ±10,0 | ±7,7 |
| 80 | ±9,9 | ±8,7 | ±6,7 |
| 100 | ±8,8 | ±7,8 | ±6,0 |

- **κ = 0,70 trên 60–100 cặp** có khoảng tin cậy xấp xỉ [0,52–0,88] → chưa phân biệt được với 0,55. Báo κ **kèm khoảng tin cậy** và phần trăm đồng thuận.
- **Chênh lệch nhỏ nhất phát hiện được** giữa hai cấu hình (power 80%): ~10–17 điểm với n = 80; ~9–15 với n = 100 → ablation chỉ kết luận được khi chênh lớn; còn lại nói **"không phát hiện được khác biệt"**, không nói "bằng nhau".
- **Cụm theo doanh nghiệp:** tuyên bố của cùng một doanh nghiệp không độc lập; sai số chuẩn có cụm có thể lớn gấp 3 lần (Miller 2024). 80 tuyên bố từ 10 doanh nghiệp với ICC 0,1 → cỡ mẫu hiệu dụng ~47 → **bootstrap theo doanh nghiệp**, báo kết quả **từng doanh nghiệp**.
- **Luôn kèm macro-F1, baseline lớp đa số, coverage.** Ví dụ: Climinator 96,4% nhị phân, nhưng đoán toàn lớp đa số đã ~90,3% [S1.8].
- **Pooling bias (quan trọng, làm trước khi gán nhãn quan hệ):** nếu ứng viên bằng chứng cho người gán chỉ đến từ BM25/n-gram, mô hình dense bị **đánh giá thấp có hệ thống** (BEIR: tỷ lệ tài liệu chưa gán trong top-10 của dense tới 31,8% so với 6,4% của BM25). → **Gộp ứng viên từ mọi bộ truy xuất** (BM25, n-gram, RRF, Vietnamese_Embedding, bge-m3, reranker) trước khi Quỳnh/Thảo gán; báo Recall@k là **cận dưới** kèm Hole@k. Lô gold hiện tại (28/09) được lấy từ bộ truy xuất 08/2026 → mọi so sánh dense ↔ lexical trên lô đó là cận dưới (đã ghi trong `MEASUREMENT_PROTOCOL_2026-09-29.md`).

## 5. Mô hình nhỏ có thể thay hoặc lọc trước lời gọi LLM (TEST, sau freeze)

Không mô hình < 1B nào đã được kiểm chứng cho tuyên bố ESG tiếng Việt → mọi lựa chọn là **TEST, không quyết định** (nhất quán với `llm_stance_decisive: false`). Thứ tự thử hợp lý:
1. mDeBERTa-xnli làm **bộ lọc**: đo tỷ lệ cặp nó "chắc chắn" và độ đúng trên phần đó (đường risk–coverage); chỉ phần còn lại gửi mô hình lớn.
2. PhoRanker / ViRanker trên CPU so với bge-reranker-v2-m3.
3. e5-large-instruct, gte-multilingual-base so với bge-m3 và Vietnamese_Embedding.
4. Bộ phát hiện tuyên bố cross-lingual (climatebert/environmental-claims qua dịch) để **đo và tăng recall** của bộ trích luật.

Chi phí và tốc độ từng lựa chọn: [`../04-data-ai/MODEL_ROUTING_AND_HARDWARE.md`](../04-data-ai/MODEL_ROUTING_AND_HARDWARE.md).

## 6. Câu được nói và không được nói trước hội đồng

**Được nói (có trích dẫn):**
1. "Chúng tôi không tuyên bố phát hiện greenwashing; chúng tôi xếp các tuyên bố cần kiểm theo rủi ro — vì chưa có bộ dữ liệu greenwashing đã xác minh nào" [S1.1, S1.2].
2. "So sánh số do code tất định, không do LLM" — kèm NumPert, Aarnes & Setty, FinQA, FinDVer.
3. "Chưa đủ bằng chứng là kết luận hợp lệ, không phải lỗi" — FEVER, SciFact, AVeriTeC, Climate-FEVER; Joren và cs. 2025.
4. "Nhãn khớp một phần / mâu thuẫn và cách gộp nhãn có tiền lệ học thuật" — AVeriTeC, Climate-FEVER, Bingler và cs.
5. "Chúng tôi đo truy xuất và kiểm chứng tách rời, coi recall là cận dưới" — Zhao và cs. TOSEM 2026; BEIR.
6. "Gold do người gán, có κ và hòa giải; không dùng LLM tự chấm" — Wang và cs. 2024; To và cs. 2024.
7. "Mục tiêu κ ≥ 0,7 là cao so với các bộ cùng loại" — bảng §2.
8. "Màn hình hiện bằng chứng gốc, quy tắc đã chạy và thông tin còn thiếu" — Warren và cs. CHI 2025.

**Không được nói:**
1. "GreenScan phát hiện / chứng minh doanh nghiệp X tẩy xanh / vi phạm".
2. Một con số accuracy trên 60–100 cặp **không kèm khoảng tin cậy**.
3. "Tốt hơn GPT / tốt hơn baseline" khi chênh < 10–15 điểm trên gold nhỏ; so trực tiếp với số trong paper tiếng Anh.
4. Accuracy nhị phân cao trên dữ liệu lệch lớp mà không kèm macro-F1 và baseline lớp đa số.
5. "Recall truy xuất = X%" như con số tuyệt đối.
6. "LLM xác minh tuyên bố", "AI đọc hiểu toàn bộ báo cáo".
7. "Lời giải thích giúp kiểm toán viên chính xác hơn" khi chưa có thí nghiệm người dùng.
8. "Embedding tiếng Việt X là tốt nhất".
9. "Chưa từng có nghiên cứu nào…" → nói "chúng tôi không tìm thấy công trình NLP công bố (arXiv/ACL Anthology) về kiểm chứng tuyên bố ESG trên báo cáo tiếng Việt tính đến 10/2026".
10. Dùng dữ liệu/mô hình phi thương mại hoặc AGPL cho định hướng thương mại mà không kiểm tra giấy phép.
