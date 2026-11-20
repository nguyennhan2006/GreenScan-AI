# Gán lại 50 câu: hướng dẫn cho người gán (khoảng 60–90 phút)

**Mục đích.** Bộ nhãn GS-Claims v1 hiện do hai mô hình Sonnet gán độc lập, rồi mô hình Opus phân xử chỗ lệch. Bạn gán lại 50 câu để đội biết người và máy khớp nhau đến đâu. Số đo đó gọi là **mức trần**: hệ thống không thể đúng hơn mức mà hai người, hay người với nhãn, khớp nhau.

**Người nên gán.** Một sinh viên kế toán – kiểm toán, hoặc một người hiểu báo cáo phát triển bền vững. Người đó **chưa từng xem** nhãn của máy và cũng không xem đầu ra của GreenScan.

## Cách làm

1. **Đọc kỹ toàn bộ** `benchmark/gs_claims_v1/LABELING_GUIDE.md`, gồm cả bảng ví dụ và phụ lục cuối. Phụ lục ghi các điểm đã được làm rõ sau lượt máy gán.
2. **Mở `items_50.xlsx`.** Mỗi cột nhãn có danh sách chọn sẵn các giá trị hợp lệ. Nếu không dùng Excel, mở `items_50.csv` và gõ đúng các giá trị viết thường như trong hướng dẫn.
3. **Gán nhãn cho câu ở cột `text`.** Cột `context` chỉ để hiểu nghĩa. Gán đủ 9 cột cho mọi câu, kể cả câu "no". Cột `note` dùng khi phân vân (tối đa 20 chữ).
4. **Không mở** các thư mục `labels/`, `_key/`, `gold.jsonl`, `adjudication.jsonl`, `disagreements.jsonl`.
5. **Lưu tệp** thành `items_50_<tên>.xlsx` trong cùng thư mục này, rồi báo người phụ trách.

## Người phụ trách chấm

```
.venv/Scripts/python.exe -I benchmark/gs_claims_v1/human/score_human.py benchmark/gs_claims_v1/human/items_50_<tên>.xlsx <tên>
```

Script in kappa từng trường của người so với nhãn đã phân xử và so với từng mô hình. Kết quả ghi vào `human_vs_sonnet.json`, kèm danh sách câu lệch để cả nhóm xem lại.

**Cách đọc kết quả:**
- **Kappa ≥ 0,7:** nhãn máy dùng được làm nhãn tham chiếu cho bộ trích tuyên bố. Ghi vào báo cáo: "nhãn mô hình, kiểm tra bằng một người trên 50 câu, κ = …".
- **Kappa từ 0,6 đến dưới 0,7:** dùng được, nhưng phải nêu là mức trần thấp.
- **Kappa < 0,6 ở một trường:** sửa hướng dẫn cho trường đó trước khi dùng nhãn của nó.
