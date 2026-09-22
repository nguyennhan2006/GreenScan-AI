# Training readiness

## Kết luận

Bộ pilot này phù hợp cho:

- end-to-end demo;
- retrieval regression;
- citation and page-location tests;
- verification prompt evaluation;
- legal-scope and settlement-qualifier tests;
- reviewer workflow.

Bộ pilot này chưa phù hợp để fine-tune một classifier tổng quát vì chỉ có 4 claim đã adjudicate.

## Ngưỡng trước khi fine-tune

- 500-1,000 claim được hai reviewer độc lập và adjudication;
- ít nhất 20-30% hard negatives;
- split theo entity + period + document family;
- tách claim detection, evidence relevance và verification labels;
- lưu exact quote, page, bounding box, source checksum và effective date;
- không dùng LLM-generated label làm gold nếu chưa có reviewer.

## Có thể huấn luyện sớm

1. Claim detector:
   - environmental-claim datasets sau khi kiểm tra license;
   - dữ liệu corporate reports không cần nhãn greenwashing.

2. Evidence reranker:
   - positive passage, hard negative sai entity/kỳ/scope;
   - pairwise/listwise training.

3. Vietnamese fact verifier:
   - pretrain/domain-adapt với corpus fact-check tiếng Việt;
   - fine-tune tiếp bằng claim-evidence ESG Việt Nam do dự án gán nhãn.

4. Không fine-tune phép tính:
   - số liệu, tỷ lệ, unit conversion và threshold phải chạy bằng code deterministic.
