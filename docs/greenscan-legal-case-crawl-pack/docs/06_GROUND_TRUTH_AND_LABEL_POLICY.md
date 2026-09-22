# 06 — Ground truth và label policy

## Ground-truth level

### Level A — Court / admission
Có court judgment/order và/hoặc admission về specified conduct. Đây là strongest legal ground truth trong pack nhưng vẫn chỉ áp dụng đúng scope.

### Level B — Formal regulator order / settlement
Administrative order/settlement. Nếu settlement nói `without admitting or denying`, qualifier là bắt buộc.

### Level C — Regulatory advertising ruling / infringement notice
ASA upheld ruling hoặc ASIC infringement notice. Đây là official regulatory signal, nhưng **không đồng nghĩa criminal/civil fraud finding**. Với ASIC notice payment, không coi là admission.

## Schema label khuyến nghị

```json
{
  "case_id": "...",
  "authority": "...",
  "authority_outcome": "UPHELD | COURT_FINDING | SETTLED | INFRINGEMENT_NOTICE | ...",
  "legal_strength": "A | B | C",
  "claim_scope": "EXACT_REPRESENTATION_ONLY",
  "qualifier": "...",
  "challenged_claim_id": "...",
  "claim_verdict_for_benchmark": null,
  "human_adjudication_required": true
}
```

`claim_verdict_for_benchmark` không tự động lấy từ `authority_outcome`. Reviewer phải map authority reasoning sang taxonomy GreenScan.

## Negative / hard-negative design

Case companies rất hữu ích để tạo hard negatives:

- claim cùng company nhưng authority không xem xét;
- claim cùng topic nhưng năm khác;
- metric gần giống nhưng scope khác;
- statement có “green/sustainable” nhưng có evidence tốt;
- parent report vs local subsidiary ad.

Không dùng 21 VN companies = negative và 29 international case companies = positive. Điều đó tạo language/jurisdiction leakage.
