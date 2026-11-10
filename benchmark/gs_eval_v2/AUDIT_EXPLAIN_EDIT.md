# Kiểm định đối nghịch D-EXPLAIN và D-EDIT (GS-Eval v2)

Ngày 05/11/2026. Người kiểm: claude-sonnet-5-5 (trường `audit.auditor`). Nhãn gốc do một lượt gán khác; mặc định nghi ngờ nhãn.

## Phương pháp
- Đọc LABELING_GUIDE.md mục 0, 1, 2.
- Lấy mẫu có hệ thống dòng 5, 15, 25, 35, 45 của 4 file explain (b01 đến b04) và 4 file edit (b01 đến b04). `edit_b03.labels.jsonl` có đủ, không phải bỏ file nào.
- Mỗi dòng đối chiếu với đầu vào cùng `item_id` trong `batches/`. Không mở `system_outputs.jsonl` hay `src`.
- Kiểm bằng tay: kết luận so với bằng chứng, bất biến (lệch một chiều, mục tiêu so với thành tích, im lặng so với sai), NOT_A_CLAIM, độ khớp của `must_mention` và `must_not_say`, độ dễ hiểu của `explanation_plain`. Kiểm bằng script: mọi `quote` có nguyên văn trong chunk và không quá 25 từ, `explanation_plain` không quá 3 câu.
- Với edit: bỏ sót vấn đề, mã sai, đổi nghĩa, mục tiêu thành thành tích, sửa thừa, `rewritten_claim` so với `edits`, issue không có edit tương ứng.
- Dòng đã soát gắn `audit` (`changed` true hoặc false, `what`, `auditor`). Đã chạy lại `validate.py` cho 8 file: errors=0, warns=0.

## Kết quả
Lỗi tính là lỗi đã sửa (rõ ràng, theo guide). Khoảng Wilson 95 %, n = 20 mỗi bộ.

| Bộ | Mẫu | Lỗi đã sửa | Tỷ lệ | Wilson 95 % | Nghi vấn chưa sửa | Tỷ lệ gồm nghi vấn | Wilson 95 % |
|---|---|---|---|---|---|---|---|
| D-EXPLAIN | 20 | 2 | 10,0 % | 2,8 đến 30,1 % | 2 | 20,0 % | 8,1 đến 41,6 % |
| D-EDIT | 20 | 3 | 15,0 % | 5,2 đến 36,0 % | 1 | 20,0 % | 8,1 đến 41,6 % |

Mẫu nhỏ nên khoảng rộng; không kết luận được tỷ lệ lỗi thật dưới 30 %.

### D-EXPLAIN, theo loại
- Kết luận sai so với bằng chứng: 0 chắc chắn.
- Vi phạm bất biến: 0.
- NOT_A_CLAIM gán sai: 0 chắc chắn (9 mẫu NOT_A_CLAIM đều hợp lý).
- Quote không nguyên văn: 0 (60 quote đều đúng).
- must_mention chung chung: 0.
- explanation_plain khó hiểu hoặc dài quá 3 câu: 0.
- Lỗi văn bản khác (đã sửa): 2
  - `explain_b01` dòng 15 (A-dfb7ecf209b07ca7): `must_not_say` có cụm "(như kết luận cho câu này)" khó hiểu; đã bỏ.
  - `explain_b03` dòng 35 (A-80317f1eb9f515ce): `uncertainty_note` có tên riêng "Nhân" ("nếu Nhân coi đó là đủ"); đã đổi thành "người soát".

Nghi vấn chưa sửa (để người duyệt quyết):
1. `explain_b01` dòng 5 (DWS, CONTRADICTED, medium): bằng chứng chỉ nói thiếu kiểm soát chính thức và tuân thủ không nhất quán, không nói ESG Engine không được dùng. Nhãn có thể nên là PARTIALLY_SUPPORTED hoặc INSUFFICIENT_EVIDENCE. Chính `uncertainty_note` của nhãn thừa nhận vế ESG Engine chỉ bị làm suy yếu.
2. `explain_b02` dòng 25 (SAB, PARTIALLY_SUPPORTED): đoạn bằng chứng khớp nhất chỉ lặp lại câu tuyên bố (không tính theo guide); phần "ủng hộ" còn lại chỉ là gắn kết người lao động về an toàn lao động. INSUFFICIENT_EVIDENCE cũng có thể chấp nhận.

### D-EDIT, theo loại
- Bỏ sót vấn đề: 2 (đã sửa)
  - `edit_b01` dòng 25 (A-089adfcb41fe031a): "không gây hại tầng ozone" mạnh hơn bằng chứng ("giảm thiểu tác động tới tầng ozone"). Đã thêm ABSOLUTE_CLAIM, edit soften theo lời bằng chứng, nâng priority medium lên high; notes cũng có tên riêng "Nhân", đã bỏ.
  - `edit_b01` dòng 35 (B-79d11206b3494e8d): số liệu 11.111 cây không dẫn nguồn, thiếu NO_EVIDENCE_REF (các mẫu B khác có gắn mã này). Đã thêm issue, edit evidence_ref và cập nhật `rewritten_claim`.
- `rewritten_claim` hoặc edits không khớp issues: 1 (đã sửa). `edit_b03` dòng 25 (B-4b0839ca34a8d6ac) có issue NO_FIGURE cho "lắp đặt điện mặt trời tại các dự án" nhưng không có edit; đã thêm edit placeholder và cập nhật `rewritten_claim`.
- Mã sai: 0. Đổi nghĩa: 0. Biến mục tiêu thành thành tích: 0. Thêm số lạ: 0. Sửa thừa cho câu đã tốt: 0.
- Câu không phải tuyên bố xanh: 6 mẫu, đều hợp lý.
- Nghi vấn chưa sửa: `edit_b02` dòng 45 (B-70f2db796478a3ee), `is_green_claim=false`. Vế "thúc đẩy một cách thiết thực thực hành ESG trong cộng đồng" và "phát triển xanh" có thể xếp VAGUE_TERM mức thấp. Nhãn tự ghi độ tin cậy medium.
- Lưu ý định dạng: trường `confidence` lẫn số (0,55) và chữ ("high"); validate không báo. Nên thống nhất trước khi dùng làm dữ liệu.

## Vấn đề hệ thống ngoài mẫu
Tên riêng "Nhân" (tên người duyệt) bị lọt vào văn bản nhãn ở khoảng 27 dòng (explain_b03: 19, edit_b01: 5, edit_b03: 2, explain_b04: 1 ... theo grep thô, có thể gồm cả từ "Nhân" hợp lệ đầu câu). Chưa sửa ngoài mẫu vì ngoài phạm vi; nên thay bằng "người soát".

## Khuyến nghị cho người duyệt
1. Duyệt tay hai nghi vấn explain ở trên (DWS và SAB). Đây là chỗ rủi ro nhất: nhãn CONTRADICTED chỉ dựa vào bằng chứng pháp lý gián tiếp.
2. Chạy một lượt thay "Nhân" bằng "người soát" trên toàn bộ file explain và edit, rồi validate lại.
3. Với các mẫu B (không có bằng chứng) kiểm tra nhất quán mã NO_EVIDENCE_REF cho mọi số liệu định lượng; mẫu b01 dòng 35 cho thấy có chỗ bỏ sót.
4. Với tuyên bố tự khen có từ tuyệt đối ("không gây hại", "100 %"), đối chiếu từng từ với lời bằng chứng; đây là kiểu bỏ sót phổ biến của bộ edit.
5. Các nhãn NOT_A_CLAIM (tiêu đề, mảnh bảng, câu dẫn) nhìn chung đáng tin; ưu tiên duyệt các nhãn có `verdict_confidence` medium và bằng chứng cùng nguồn với tuyên bố.
6. Kết quả dựa trên 20 mẫu mỗi bộ, chưa đủ để kết luận cả bộ sạch; nên lấy mẫu mở rộng (ví dụ dòng 10, 20, 30, 40) nếu còn thời gian trước 10/11.
