# Bộ câu hỏi phản biện — luyện trước Bán kết 25/10

**Dùng cho:** S6.1 Defense week (18–24/10), mock Q&A mỗi ngày, hỏi **random member**. Mục tiêu: cả ba người trả lời được mọi câu trong 60 giây, không jargon, theo mẫu **failure mode → design choice → measurement**.
**Đi sâu 4 mảng (100 câu + truy vấn tiếp):** [QA_BANK_100_2026-09-20.md](QA_BANK_100_2026-09-20.md).
**Quy tắc chung:** không nói "phát hiện greenwashing với độ chính xác X%"; không nói "quantum advantage"; số chỉ lấy từ cột *Achieved* (DECISIONS_LOG D-2026-09-18-08).

## 1. Câu hỏi gần như chắc chắn

| # | BGK hỏi | Câu trả lời cốt lõi |
| --- | --- | --- |
| 1 | GreenScan có phát hiện doanh nghiệp greenwashing không? | Không. Đơn vị phân tích là **claim**. Hệ thống đánh giá sufficiency/consistency của evidence cho từng claim và tạo risk indicator; kết luận pháp lý thuộc reviewer/cơ quan có thẩm quyền. |
| 2 | Tại sao cần RAG? | Vì evidence nằm ngoài câu claim và thay đổi theo tài liệu/kỳ. RAG chỉ là **retrieval layer**, không đảm bảo đúng: nghiên cứu nhóm tham khảo (Zhao et al.) cho thấy vanilla RAG có thể tệ hơn LLM đơn, và retrieval hoàn hảo vẫn có lỗi generation. Vì thế verdict không giao cho LLM. |
| 3 | Tại sao hybrid BM25 + semantic? | ESG có cả từ khoá rất chính xác ("Scope 2", "tCO₂e", mã điều luật) lẫn diễn đạt semantic khác nhau. Sparse và dense có failure mode bổ sung nhau; reranker (30→5) giảm distractor. |
| 4 | Tại sao không GraphRAG? | Claim-level verification là factual/local retrieval. GraphRAG lợi khi cần tổng hợp thematic đa tài liệu (paper TREX), nhưng thêm indexing + complexity. Để ở V2 sau benchmark. |
| 5 | Nếu RAG không tìm thấy evidence thì sao? | Không suy ra false. Nếu corpus không chứng minh được completeness → `INSUFFICIENT_EVIDENCE`. **Absence chỉ thành `UNSUPPORTED` khi có lý do xác định evidence phải có trong corpus đã kiểm tra.** |
| 6 | Tài liệu của chính doanh nghiệp có tự chứng minh claim không? | Không. `claim_source` chỉ chứng minh doanh nghiệp đã nói gì. Independent/authority evidence có vai trò khác; contradiction từ authority được xử lý mạnh hơn (ADR 0003/0004). |
| 7 | LLM có làm số học không? | Không. LLM giúp hiểu claim (normalization 5 thuộc tính); comparator deterministic bằng Python chỉ chạy **sau khi** metric, unit, period, boundary, scope tương thích. |
| 8 | Dung sai 12% từ đâu? | Không giữ 12% toàn cục. Comparison policy: giá trị trực tiếp so theo độ chính xác công bố; giá trị làm tròn → tolerance suy từ số chữ số; % tăng/giảm tính lại từ base/current; cường độ chỉ so cường độ; Scope 1+2 ≠ 1+2+3; mẹ ≠ hợp nhất; OCR thấp → abstain; khác metric → không numeric contradiction. |
| 9 | Risk score 0–100 có phải xác suất greenwashing? | Không. Là screening rubric có trần thành phần, versioned (`risk-rubric-v2`), **không** phải calibrated probability. Chỉ hiệu chuẩn thống kê khi đủ human labels. |
| 10 | Vì sao trọng số rubric như vậy? | Policy/risk rubric minh bạch, versioned; chưa tuyên bố là trọng số tối ưu. Calibration sau khi gold đủ. |
| 11 | 5 gold có đủ chưa? | Không. Brief công khai đây là hạn chế; vì vậy không dùng nó để tuyên bố accuracy tổng quát. Mục tiêu ≥60 adjudicated trước 10/10, báo cáo theo từng DN kèm khoảng tin cậy. |
| 12 | Cohen's κ ≥ 0,7 có nghĩa accuracy 70%? | Không. κ đo agreement giữa hai annotator vượt quá ngẫu nhiên — chất lượng nhãn, không phải model accuracy. |
| 13 | Làm sao tránh data leakage? | Split theo **doanh nghiệp** trước, rồi theo thời gian trong train. Không random claim split vì KPI/tên issuer gây leakage. |
| 14 | Luật thay đổi thì sao? | Registry lưu effective date, supersession chain, rule-pack version; chạy được historical-as-of và current-policy mode. |
| 15 | QĐ 21/2025 dùng để làm gì? | Quy định tiêu chí môi trường và xác nhận dự án thuộc danh mục phân loại xanh; hiệu lực 22/08/2025. Không có nghĩa mọi câu marketing "xanh" tự động thuộc phạm vi. |
| 16 | NĐ 83/2026 quan hệ gì với 06/2022 và 119/2025? | NĐ 83/2026 sửa NĐ 06/2022, vốn đã được sửa bởi NĐ 119/2025; NĐ 83 hiệu lực 23/03/2026. Registry giữ cả chuỗi. |
| 17 | Quantum nằm ở đâu? | Một bài toán combinatorial downstream: chọn subset evidence tối ưu dưới constraint (QUBO). AI vẫn làm extraction/retrieval; quantum/quantum-inspired optimization không thay LLM. |
| 18 | Có quantum advantage chưa? | Chưa. MVP không phụ thuộc quantum. So với top-k, greedy/MMR và exact classical baseline trước; QAOA không thắng vẫn là kết quả hợp lệ. |
| 19 | Tại sao không multi-agent? | Workflow đã biết trước và compliance cần reproducibility (ADR 0001). Agent autonomy chỉ đáng dùng nếu benchmark chứng minh lợi ích vượt orchestrator hiện tại. |
| 20 | Prompt injection trong PDF thì sao? | Nội dung tài liệu là untrusted data, không phải instruction. Parser tách system instruction khỏi content; `injection_policy: exclude`; đã có test. |
| 21 | Nếu authority sai hoặc qualifier bị bỏ mất? | Evidence record giữ qualifier và scope. Settlement "without admission or denial" không được chuyển thành "company admitted wrongdoing" (trap test). |
| 22 | Tại sao local-first? | Báo cáo draft có thể chưa công bố; local mode giảm data-egress risk và provider dependency (ADR 0002). Cloud chỉ là optional fallback. |
| 23 | Giá trị kinh tế đã chứng minh chưa? | Chưa. "8–12 giờ → 30 phút + 2 giờ" là **hypothesis** để pilot, không phải kết quả đã xác nhận. |
| 24 | Tại sao không tăng top-k để tìm thêm evidence? | Distractor làm RAG tệ hơn (Zhao et al.). Không tăng k tùy ý; đo Recall@k và verdict accuracy theo k; rerank 30→5; evidence dưới threshold chỉ là candidate (`below_threshold`), không tự tạo support — nhưng có thể mang bác bỏ từ authority (KLM-2024). |

## 2. Kiến thức cả ba thành viên phải nắm (60 giây mỗi mục)

| Khối | Phải giải thích được |
| --- | --- |
| ESG / climate | Scope 1/2/3; absolute vs intensity; base year; organizational boundary; renewable share; carbon neutral vs net-zero; assurance; target vs achieved |
| Green finance | Green credit/bond use-of-proceeds; taxonomy; project eligibility; claim marketing vs claim để hưởng cơ chế tài chính |
| Pháp lý VN | Luật BVMT 2020; TT 17/2022; QĐ 21/2025; QĐ 13/2024; NĐ 06/2022 → 119/2025 → 83/2026; effective-date reasoning |
| Information retrieval | BM25, embedding, cosine, RRF, reranker, Recall@k, MRR/nDCG cơ bản, distractor, top-k tradeoff |
| LLM | extraction vs generation; structured JSON; NLI/stance; hallucination; confidence ≠ correctness; prompt injection; abstention |
| Evaluation | precision/recall/F1; macro vs micro; company-held-out split; κ; confidence interval; ablation; calibration/selective accuracy |
| Document AI | text layer vs OCR; reading order; table extraction; provenance page/block/cell; OCR confidence |
| Quantum | binary variable; QUBO; penalty; Ising mapping; simulated annealing; QAOA; classical baseline; NISQ limitations |

## 3. Mẫu câu trả lời tốt

> "Vì distractor có thể làm RAG tệ hơn, chúng tôi không tăng top-k tùy ý; chúng tôi đo Recall@k và verdict accuracy theo k, rerank 30 xuống 5, và giữ evidence dưới threshold chỉ như candidate chứ không cho nó tự tạo support."

Có đủ ba phần: nghiên cứu (failure mode) → kiến trúc (design choice) → đánh giá (measurement).

## 4. Câu chốt

> Mỗi kết luận của GreenScan đều phải trả lời được bốn câu: **claim gốc ở đâu, evidence ở đâu, phép kiểm tra nào đã chạy, và tại sao hệ thống có hoặc không có quyền đưa ra verdict đó.**
