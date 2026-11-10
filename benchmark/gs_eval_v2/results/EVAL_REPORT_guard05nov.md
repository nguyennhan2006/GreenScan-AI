# GS-Eval v2: kết quả đánh giá hệ thống hiện tại (tự sinh bởi evaluate.py)

*Chạy 2026-11-05. Nhãn: Claude theo `LABELING_GUIDE.md`, tác giả đọc lại. Hệ thống: lượt offline trong `.quantum/runs`.*

*Nguồn đầu ra hệ thống: current-code runs (>= 2026-10-22), see inputs/refresh_stats.json.*

## 1. Giải thích và kết luận (D-EXPLAIN)
- 200 mẫu có nhãn; 146 mẫu có đầu ra của mã hiện tại (theo kết luận hiện tại: {'PARTIALLY_SUPPORTED': 89, 'CONTRADICTED': 4, 'INSUFFICIENT_EVIDENCE': 48, 'SUPPORTED': 5}). Mã hiện tại không còn trích 54 câu (nhãn: {'NOT_A_CLAIM': 23, 'PARTIALLY_SUPPORTED': 11, 'INSUFFICIENT_EVIDENCE': 10, 'SUPPORTED': 9, 'CONTRADICTED': 1}).
- Câu hệ thống trích ra nhưng **không phải tuyên bố**: 44/146 (Wilson 95 % [0.233, 0.38]); ước tính trên toàn kho sau khi trọng số lại: 0.339. Theo kết luận hệ thống: {'PARTIALLY_SUPPORTED': '31/89', 'CONTRADICTED': '1/4', 'INSUFFICIENT_EVIDENCE': '10/48', 'SUPPORTED': '2/5'}.
- Trên 102 tuyên bố thật: kết luận trùng nhãn 0.51 (trọng số toàn kho 0.543, bootstrap theo công ty [0.444, 0.571]), κ = 0.179, macro-F1 0.517.
- Kết luận dứt khoát của hệ thống (S/C): 9, precision so với nhãn 0.333; CONTRADICTED sai 1 (trên tuyên bố thật 0; nhãn: {'NOT_A_CLAIM': 1}); SUPPORTED sai 5 (nhãn: {'NOT_A_CLAIM': 2, 'PARTIALLY_SUPPORTED': 3}).
- Lời giải thích: trung bình 36.2 từ, 38 câu khác nhau trên 146 mẫu; độ phủ ý bắt buộc (proxy từ khoá) 0.025; số không có nguồn: 4.

| Hệ thống \ Nhãn | CONTRADICTED | INSUFFICIENT_EVIDENCE | NOT_A_CLAIM | PARTIALLY_SUPPORTED | SUPPORTED |
|---|---|---|---|---|---|
| CONTRADICTED | 3 | 0 | 1 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 0 | 17 | 10 | 14 | 7 |
| PARTIALLY_SUPPORTED | 0 | 17 | 31 | 32 | 9 |
| SUPPORTED | 0 | 0 | 2 | 3 | 0 |

| Thuộc tính thiếu | P | R | F1 |
|---|---|---|---|
| metric | 0.261 | 0.375 | 0.308 |
| value | 0.333 | 0.3 | 0.316 |
| period | 0.5 | 0.432 | 0.463 |
| baseline | 0.143 | 0.5 | 0.222 |
| scope | 0.194 | 0.292 | 0.233 |

### Chấm lời giải thích theo danh mục tham chiếu
- n = 146; độ phủ ý bắt buộc 0.022; nói điều không được nói: 19 mẫu; trung thực với bằng chứng 0.575 (Wilson [0.494, 0.653]); chỉ ra việc cần làm 0.397; độ rõ TB 2.68/5.

| Kết luận hệ thống | n | Phủ ý | Trung thực | Chỉ việc | Rõ |
|---|---|---|---|---|---|
| CONTRADICTED | 4 | 0.167 | 0.75 | 0.0 | 2.0 |
| INSUFFICIENT_EVIDENCE | 48 | 0.051 | 0.604 | 0.979 | 3.0 |
| PARTIALLY_SUPPORTED | 89 | 0.0 | 0.584 | 0.124 | 2.57 |
| SUPPORTED | 5 | 0.0 | 0.0 | 0.0 | 2.0 |

## 2. Chấm rủi ro (D-SCORE)
- Hai lượt mù: 200 mẫu; phân xử 122 mẫu.
- Đồng thuận hai lượt (tổng điểm) Spearman 0.734; dải tổng thể QWK 0.752.
- Hệ thống so với đồng thuận: Spearman tổng điểm 0.389 (bootstrap công ty [0.162, 0.512]); trung bình 49.2 so với 30.2; mức độ so với dải tổng thể: đúng 0.473, lệch ≤ 1 bậc 0.986.

| Thành phần | QWK hai lượt | QWK hệ thống–đồng thuận | Mức TB hệ thống | Mức TB nhãn | Không áp dụng | Hệ thống vẫn phạt |
|---|---|---|---|---|---|---|
| specificity | 0.585 | 0.268 | 1.26 | 1.16 | 43 | 43 |
| quantitative_evidence | 0.66 | 0.419 | 2.09 | 1.41 | 45 | 45 |
| baseline | 0.777 | 0.109 | 1.82 | 0.41 | 120 | 69 |
| period | 0.596 | 0.201 | 2.35 | 0.98 | 50 | 44 |
| scope_boundary | 0.697 | -0.092 | 2.15 | 1.08 | 43 | 34 |
| evidence_support | 0.663 | 0.277 | 1.37 | 1.24 | 41 | 39 |
| independent_assurance | 0.645 | -0.062 | 2.92 | 1.82 | 43 | 43 |
| contradiction | 0.826 | 0.669 | 0.12 | 0.15 | 35 | 2 |
| vague_or_exaggerated_language | 0.838 | 0.378 | 0.51 | 0.95 | 28 | 3 |

## 3. Gợi ý sửa (D-EDIT)
- n = 200; tuyên bố xanh 151, cần sửa 135.
- Nhận ra câu cần sửa: {'tp': 135, 'fp': 16, 'fn': 0, 'precision': 0.894, 'recall': 1.0, 'f1': 0.944}.
- Gợi ý của hệ thống: 527 ({'add_scope': 194, 'evidence_ref': 200, 'placeholder': 117, 'soften': 16}); trên câu không phải tuyên bố xanh: 130; thêm số mới: 0.
- Macro-F1 mã vấn đề: 0.359. Vấn đề nằm ngoài từ vựng của hệ thống: {'VAGUE_TERM': 35, 'NO_FIGURE': 34, 'UNVERIFIED_LABEL_OR_CERT': 17, 'MISSING_SCOPE': 13, 'ABSOLUTE_CLAIM': 10, 'OTHER': 5, 'HIDDEN_TRADEOFF': 3, 'MISSING_PERIOD': 2, 'IRRELEVANT_CLAIM': 1}.

| Mã vấn đề | P | R | F1 | tp/fp/fn |
|---|---|---|---|---|
| MISSING_PERIOD | 0.35 | 0.953 | 0.512 | 41/76/2 |
| MISSING_BASELINE | 0.139 | 1.0 | 0.244 | 11/68/0 |
| MISSING_SCOPE | 0.275 | 0.683 | 0.392 | 28/74/13 |
| NO_FIGURE | 0.564 | 0.477 | 0.517 | 31/24/34 |
| VAGUE_TERM | 0.676 | 0.397 | 0.5 | 23/11/35 |
| ABSOLUTE_CLAIM | 0.0 | 0.0 | 0.0 | 0/4/10 |
| OFFSET_NEUTRALITY | 0.2 | 1.0 | 0.333 | 1/4/0 |
| NO_EVIDENCE_REF | 0.232 | 1.0 | 0.376 | 35/116/0 |

## 4. Quy tắc nội bộ (D-RULES, org pack)
- 14 pack, 76 quy tắc, 237 ca; kết quả kỳ vọng {'COMPLIANT': 60, 'VIOLATION': 72, 'NOT_APPLICABLE': 48, 'NEEDS_REVIEW': 57}.
- Engine với thuộc tính đúng: accuracy 0.945 (Wilson [0.908, 0.968]), macro-F1 0.945.
- Đầu–cuối (thuộc tính do bộ trích luật lấy): accuracy 0.907 (Wilson [0.863, 0.938]), macro-F1 0.908.
- Theo loại ca (thuộc tính đúng): {'conflict_with_law': '6/6', 'draft_rule': '11/11', 'edge': '35/39', 'expired_rule': '6/6', 'injection': '11/11', 'normal': '131/140', 'other_sector': '13/13', 'override_attempt': '11/11'}.
- Ca an toàn lệch kỳ vọng: 0.

## 5. UX lint
- Kiểm: {'UXL-01_length': 'PASS', 'UXL-03_code_leak': 'PASS', 'UXL-04_doc_and_page': 'FAIL', 'UXL-06a_neutral_phrase': 'FAIL', 'UXL-07_forbidden_terms': 'PASS', 'UXL-10_safe_suggestions': 'PASS'}
- Tổng: {'strings': 8685, 'over_80_words': 0, 'sentence_over_40_words': 0, 'internal_code_leaks': 0, 'english_strings': 0, 'forbidden_terms': 0, 'evidence_items': 7235, 'evidence_without_doc_or_page': 8, 'insufficient_or_unsupported': 73, 'insufficient_with_neutral_phrase': 72}
- UXL-13 pack lỗi: FAIL (E8; 8/9 đạt)
