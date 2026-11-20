# GreenScan: hướng dẫn sử dụng một trang

Cập nhật 11/11/2026. Bản đầy đủ từng bước nằm trong ứng dụng, mục **Hướng dẫn** (bảy bước trên bộ mẫu Hòa Phát, khoảng 10 phút).

> **Kết quả này là tín hiệu rủi ro dựa trên thông tin công khai, hỗ trợ người hành nghề đảm bảo khoanh vùng kiểm tra — không thay thế thủ tục thu thập bằng chứng theo ISSA 5000.**

## 1. Đưa vào gì

| Tài liệu | Vai trò khi tải lên | Ghi chú |
|---|---|---|
| Báo cáo phát triển bền vững, báo cáo thường niên | **Tài liệu cần kiểm**: máy tách các câu nói về môi trường từ đây | |
| Báo cáo thường niên, kiểm kê khí nhà kính, quan trắc, văn bản pháp luật, tờ xác nhận của bên thứ ba | **Tài liệu đối chiếu**: máy tìm bằng chứng ở đây | Khai đúng **loại nguồn**. Chỉ văn bản pháp luật, nguồn bên ngoài doanh nghiệp và chuẩn mực được tính là nguồn độc lập. |

- Định dạng: PDF có lớp chữ, PDF quét (máy tự đọc ảnh chữ bằng OCR và báo độ tin cậy), DOCX, HTML, TXT, MD, CSV, JSON.
- Chế độ mặc định là **Ngoại tuyến**: mọi bước chạy trên máy tính này, tài liệu không rời máy. Một báo cáo khoảng 250 trang mất khoảng 2–3 phút.

## 2. Nhận được gì

| Đầu ra | Dùng để |
|---|---|
| **Hàng đợi “Cần soát”** (5 đến 25 mục; bộ mẫu Hòa Phát có 8) | Biết nên mở câu nào trước, kèm lý do, trang và điểm ưu tiên. Điểm ưu tiên không phải mức vi phạm. |
| **Trang tuyên bố** | Xem kết luận máy gợi ý, năm thuộc tính (chỉ số, giá trị, kỳ báo cáo, năm gốc, phạm vi), đoạn bằng chứng ở trang gốc và loại nguồn của nó. |
| **Quyết định của bạn** | Xác nhận, Ghi đè, Yêu cầu thêm bằng chứng, Chưa kết luận. Có lý do, tên, thời điểm; chỉ ghi thêm, không xoá được. |
| **Giấy làm việc** (HTML, in ra PDF) | Bản ghi để ký: phạm vi tài liệu kèm mã băm, thủ tục đã chạy, kết quả từng mục, phần chưa kiểm, quyết định. |
| **Bảng hàng đợi CSV** | Mở bằng Excel để chia việc trong nhóm. |
| **Studio** (HTML, PDF, DOCX) | Sửa câu trong báo cáo và xuất báo cáo chỉnh sửa kèm lý do từng đoạn. |

Năm loại kết luận: **Được ủng hộ**, **Ủng hộ một phần**, **Chưa được chứng minh**, **Mâu thuẫn với nguồn**, **Chưa đủ bằng chứng**. “Chưa đủ bằng chứng” không có nghĩa là tuyên bố sai.

## 3. Hai cổng tự động bạn sẽ thấy

- **G8 — Toàn vẹn tài liệu:** chữ ẩn (vô hình, trùng màu nền, cỡ rất nhỏ) và câu nhắn tới máy chấm trong tài liệu bị loại khỏi phân tích và báo cho bạn.
- **G9 — Chất lượng đọc tài liệu:** trang quét đọc với độ tin cậy thấp được nêu tên. Số đọc chưa chắc không được dùng để kết luận “khớp” hay “mâu thuẫn”; kết luận bị hạ xuống “Ủng hộ một phần” để bạn xem trang gốc.

## 4. Giới hạn: GreenScan chưa làm những việc này

- Không kết luận doanh nghiệp vi phạm hay “tẩy xanh”, và không thay người soát xét.
- Chưa đối chiếu hoá đơn, chứng từ hay sổ sách gốc.
- Chưa đọc báo cáo kiểm toán tài chính đính kèm. Cờ kiểm tờ xác nhận đảm bảo về phát triển bền vững (D6–D8) đang làm, chưa có trong sản phẩm.
- Chưa so với dữ liệu ngành hay doanh nghiệp cùng ngành.
- Chưa so cùng một chỉ số giữa các năm một cách tự động; phép cộng lại bảng số chỉ chạy khi các số cùng bảng, cùng năm, cùng đơn vị.
- Pháp lý: tìm được văn bản đang hiệu lực cùng chủ đề, nhưng chưa có quy tắc xác định nghĩa vụ cụ thể của doanh nghiệp.
- Chưa đối chiếu số OCR đọc chưa chắc bằng mô hình thị giác.
- Khoảng 3 trên 10 câu máy tách ra không phải tuyên bố (đo trên 146 câu, 05/11/2026). Bạn vẫn cần lọc.
- Chưa có số đo độ chính xác trên nhãn của người; các số hiện có đo trên nhãn do Claude gán.
