# Kịch bản hướng dẫn cho người mới bắt đầu

Ban hành 05/11/2026.

Có hai dạng:
- **Trong app:** trang "Hướng dẫn cho người mới" (`frontend/src/pages/GuidePage.jsx`). Lần đầu đăng nhập, app tự mở trang này. Sau đó mở lại từ cột trái bất cứ lúc nào.
- **Bản này:** dùng khi người hướng dẫn kèm trực tiếp, hoặc khi cho người mới tự đọc trước.

Từ ngữ theo `CHUAN_NGON_NGU_GIAO_DIEN.md`.

## Dành cho ai, cần gì

- **Người dùng:** kiểm toán viên, chuyên viên tín dụng xanh, sinh viên kế toán. Không cần biết về trí tuệ nhân tạo.
- **Thời gian:** khoảng 10 phút.
- **Cần chuẩn bị:**
  - máy đã chạy GreenScan, mở trình duyệt ở `localhost:8000`;
  - không cần mạng;
  - dữ liệu dùng bộ mẫu Hòa Phát có sẵn trong app.

## Câu mở đầu (người hướng dẫn đọc to, khoảng 30 giây)

> Báo cáo bền vững của doanh nghiệp có hàng trăm câu tự nói về môi trường. Soát tay, mỗi câu lại phải lật tìm bằng chứng trong hàng trăm trang. GreenScan chia việc làm ba phần: máy đọc và tìm bằng chứng, quy tắc kiểm tra, còn bạn là người quyết định. Kết quả là thứ tự cần soát kèm trang bằng chứng, không phải lời kết tội. Hôm nay mình làm bảy bước trên báo cáo thật của Hòa Phát.

## Bảy bước

Mỗi bước gồm bốn phần: **Làm gì**, **Nhìn vào đâu**, **Hiểu thế nào**, và **Hỏi lại** (câu kiểm tra người mới đã hiểu chưa).

### Bước 1. Tải bộ mẫu và bắt đầu (khoảng 3 phút, phần lớn là chờ máy chạy)

- **Làm gì:** Cột trái → "1 Tải tài liệu". Bấm "Nạp bộ mẫu để thử", rồi bấm "Bắt đầu".
- **Nhìn vào đâu:**
  - hai tệp hiện ra, mỗi tệp có cột vai trò;
  - nhãn xanh "Ngoại tuyến — không gửi tài liệu ra ngoài".
- **Hiểu thế nào:**
  - Báo cáo phát triển bền vững 2025 là tài liệu cần kiểm.
  - Báo cáo thường niên 2024 là tài liệu đối chiếu, nơi máy đi tìm bằng chứng.
  - Ở chế độ ngoại tuyến, máy chỉ dùng quy tắc, phép tính và tìm kiếm từ khoá ngay trên máy tính.
- **Hỏi lại:** "Tài liệu nào là cái cần kiểm, tài liệu nào để so?"

### Bước 2. Đọc hàng đợi (1 phút)

- **Làm gì:** Xem thẻ "Cần soát", rồi thẻ "Ngoài hàng đợi".
- **Nhìn vào đâu:**
  - câu gốc, tên tệp, số trang của từng mục;
  - con số nhỏ như "61/90";
  - dòng chữ "Thứ tự là thứ tự nên mở, không phải mức độ 'xấu'".
- **Hiểu thế nào:**
  - Hàng đợi là danh sách nên mở trước, có lý do.
  - "61/90" là điểm ưu tiên, không phải mức vi phạm.
  - Mục ngoài hàng đợi đều ghi vì sao lượt này chưa soát.
- **Hỏi lại:** "Con số 61/90 có nghĩa doanh nghiệp sai 61 phần không?" (Đáp án: không, đó là thứ tự mở.)

### Bước 3. Mở một tuyên bố (2 phút)

- **Làm gì:** Bấm "Mở" ở mục số 2: "…mức độ tự chủ điện năng rất cao…", trang 7.
- **Nhìn vào đâu:** nhãn kết luận ở trên cùng, rồi bảng "Thuộc tính bắt buộc".
- **Hiểu thế nào:**
  - Máy kiểm năm thuộc tính: chỉ số, năm gốc, kỳ báo cáo, phạm vi, bằng chứng và phương pháp.
  - Câu này thiếu năm gốc và kỳ báo cáo; chỉ số chỉ là chữ "rất cao". Vì vậy kết luận là "Ủng hộ một phần".
  - Mỗi thuộc tính thiếu có dòng "Việc cần làm".
- **Hỏi lại:** "Vì sao máy không nói câu này đúng?" (Đáp án: câu gốc không có số để so.)

### Bước 4. Xem bằng chứng ở trang gốc (1 phút)

- **Làm gì:** Chọn thẻ "Bằng chứng". Ở đoạn báo cáo thường niên trang 86, bấm "Mở nguồn".
- **Nhìn vào đâu:** trang gốc có đoạn tô vàng, tên tệp, số trang và mã băm.
- **Hiểu thế nào:**
  - Mỗi đoạn có nhãn quan hệ: Ủng hộ, Một phần, Mâu thuẫn, Chỉ liên quan.
  - Mã băm là dấu vân tay của tệp. Đổi một chữ là mã đổi, nên biết chắc đã kiểm đúng bản nào.
- **Hỏi lại:** "Nếu kho tài liệu không có đoạn nào để so, kết luận sẽ là gì?" (Đáp án: "Chưa đủ bằng chứng", không phải "sai".)

### Bước 5. Xem phép kiểm tra số (1 phút)

- **Làm gì:** Về hàng đợi, cuộn tới khung "Thủ tục trên số liệu công bố".
- **Nhìn vào đâu:** phép cộng bảng khí nhà kính trang 39. Phát thải phạm vi 1 (trực tiếp) cộng phạm vi 2 (từ năng lượng mua vào) bằng 23.474.479. Doanh nghiệp công bố 23.474.480.
- **Hiểu thế nào:**
  - Máy chỉ cộng hai số khi chúng cùng bảng, cùng năm, cùng đơn vị.
  - Lệch 1 tấn là do làm tròn, nên kết quả là khớp.
  - Phép tính hiện ra để bạn tự kiểm lại.
- **Hỏi lại:** "Máy có so hai con số của hai năm khác nhau không?" (Đáp án: không, phải cùng năm, cùng đơn vị, cùng phạm vi.)

### Bước 6. Ra quyết định (1 phút)

- **Làm gì:** Ở cuối trang tuyên bố, chọn Xác nhận, Ghi đè, Yêu cầu thêm bằng chứng, hoặc Chưa kết luận. Ghi lý do rồi lưu.
- **Nhìn vào đâu:** dòng "Lịch sử" có tên bạn và thời điểm.
- **Hiểu thế nào:**
  - Kết luận của máy là gợi ý; người quyết định là bạn.
  - Quyết định chỉ ghi thêm, không xoá, nên người sau đọc lại được lý do.
- **Hỏi lại:** "Ai chịu trách nhiệm kết luận cuối cùng?" (Đáp án: người soát xét.)

### Bước 7. Xem và in giấy làm việc (1 phút)

- **Làm gì:** Cột trái → "4 Giấy làm việc". Đọc lướt rồi bấm in hoặc lưu PDF.
- **Nhìn vào đâu:**
  - phạm vi tài liệu kèm mã băm;
  - thủ tục đã chạy;
  - kết quả từng mục kèm trang;
  - những gì KHÔNG được kiểm;
  - quyết định của bạn;
  - chỗ ký.
- **Hiểu thế nào:** Giấy làm việc ghi cả phần chưa kiểm, để không ai hiểu nhầm là đã kiểm hết.
- **Hỏi lại:** "Giấy làm việc có thay kết luận kiểm toán không?" (Đáp án: không. Đó là bản ghi thủ tục, người có thẩm quyền mới ký kết luận.)

## Câu kết (người hướng dẫn, khoảng 20 giây)

> Nhớ ba điều. Một, hàng đợi là thứ tự nên mở, không phải mức vi phạm. Hai, "chưa đủ bằng chứng" không có nghĩa là sai. Ba, máy chỉ gợi ý, bạn là người ký.

## Kiểm tra người mới đã hiểu chưa

Người mới trả lời bằng lời của mình, người hướng dẫn **không gợi ý**. Ghi lại nguyên văn câu trả lời.

1. GreenScan giúp ai, làm việc gì? (trả lời trong một câu)
2. Người dùng phải đưa vào những tài liệu gì?
3. Khi kiểm một tuyên bố, hệ thống làm những bước chính nào?
4. Nếu chưa đủ bằng chứng, màn hình kết luận gì?
5. Kết quả có thay kết luận kiểm toán hoặc của cơ quan quản lý không?

Năm câu này trùng bộ câu hỏi người mới ở mục 9 của phiếu chấm truyền tải. Kết quả dùng cho điểm E1 của phiếu.

## Những chỗ người mới hay vướng (cách gỡ)

| Hiểu nhầm | Câu gỡ |
|---|---|
| "Điểm 61/90 là doanh nghiệp sai nhiều" | Đó là điểm ưu tiên để mở trước. App ghi ngay trên trang: "Thứ tự là thứ tự nên mở, không phải mức độ 'xấu'". |
| "Chưa đủ bằng chứng nghĩa là doanh nghiệp nói sai" | Không. Nghĩa là kho tài liệu chưa có gì để so. Cần bổ sung tài liệu hoặc hỏi doanh nghiệp. |
| "Phạm vi" ở thuộc tính và "phạm vi 1, 2" ở bảng khí nhà kính là một | Khác nhau. Thuộc tính "phạm vi" là tuyên bố nói về đơn vị nào. "Phạm vi 1, 2, 3" là cách chia nguồn phát thải. |
| "Máy đã kiểm hết báo cáo" | Mục 5 của giấy làm việc liệt kê những gì không được kiểm. Khoảng 3 trên 10 câu máy tách ra không phải tuyên bố. |
| "Quy tắc nội bộ đổi được kết luận" | Không. Quy tắc nội bộ đứng dưới luật và không bao giờ đổi kết luận kiểm chứng. Đây là tính năng thử nghiệm, bật bằng cờ. |
