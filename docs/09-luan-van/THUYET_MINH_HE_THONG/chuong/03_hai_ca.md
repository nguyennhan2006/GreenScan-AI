# Chương 3. Hai ca minh hoạ dùng xuyên suốt

Tài liệu dùng hai ca bổ sung cho nhau. **Ca A** nhỏ, dựng sẵn, biết trước đáp án, nên có thể in ra toàn bộ đầu ra của mọi bước và kiểm từng con số bằng tay. **Ca B** là bộ hồ sơ thật, công khai, cỡ lớn, cho thấy hệ thống chạy trên tài liệu thực tế với những khó khăn thực tế (bảng, chữ trộn cột, trang quét).

## 3.1. Ca A: Công ty Cổ phần Minh Họa (bộ hồ sơ dựng)

Bộ hồ sơ nằm trong `data/sample/` của kho mã, gồm ba tệp văn bản ngắn. Công ty là hư cấu; nội dung được viết để mỗi tuyên bố có một "bẫy" biết trước.

{{CASE_A_DOCS}}

Toàn văn ba tệp:

{{CASE_A_TEXTS}}

**Đáp án biết trước (theo cách dựng):**

| Tuyên bố trong BCPTBV | Sự thật trong bộ hồ sơ | Kết luận mong đợi |
|---|---|---|
| "doanh nghiệp xanh hàng đầu… thân thiện với môi trường" | Không có số liệu nào để đối chiếu | Ngôn ngữ mơ hồ, chưa được chứng minh |
| "giảm 30% tổng phát thải… năm 2024 so với năm 2023" | Phát thải tăng từ 100.000 lên 112.000 tCO2e (+12%) | Mâu thuẫn |
| "năng lượng tái tạo đạt 50%… năm 2024" | Điện tái tạo mua chiếm 8% | Mâu thuẫn |
| "cam kết Net Zero 2050" | Không có lộ trình, không có số liệu | Cam kết tương lai chưa được chứng minh |
| "vốn trái phiếu xanh được sử dụng hoàn toàn cho dự án xanh" | 320/500 tỷ đồng đã giải ngân, 180 tỷ chưa phân bổ | Mâu thuẫn (về chữ "hoàn toàn") |

Bảng này dùng để đối chiếu với kết quả của hệ thống ở Chương 4. Ở phiên ngày 18/11, hệ thống ra đúng cả năm kết luận mong đợi. Tuyên bố trái phiếu xanh từng bị **bỏ lọt** ở các phiên trước ngày 14/11 (kết luận "ủng hộ một phần"). Nay luật `absolute-share-v1` bắt được nó: luật đọc "hoàn toàn" là 100%, rồi so với tỷ trọng tính được từ đoạn bằng chứng, 320/500 = 64% (mục 4.6.2, Chương 11).

## 3.2. Ca B: Tập đoàn Hòa Phát (HPG), hồ sơ thật

Hai tài liệu công khai do Tập đoàn Hòa Phát phát hành, lưu trong `data/real_cases/sources/originals/`:

{{CASE_B_DOCS}}

Báo cáo phát triển bền vững 2025 là nguồn tuyên bố; báo cáo thường niên 2024 đóng vai tài liệu đối chiếu. Đây là cách một kiểm toán viên thường làm: đọc lời khẳng định trong báo cáo bền vững, rồi tìm dấu vết của nó trong báo cáo thường niên đã kiểm toán tài chính. Ca B không có đáp án dựng sẵn; giá trị của nó là cho thấy hệ thống xử lý tài liệu dày hàng trăm trang ra sao và người soát nhận được gì.

## 3.3. Các tuyên bố được theo dõi chi tiết

Ca A có 5 tuyên bố, Ca B có 186 tuyên bố (phiên ngày 18/11). Tài liệu in toàn bộ kết quả của Ca A và chọn hai tuyên bố của mỗi ca để theo qua từng bước, kể cả các bước có LLM và luồng hỏi đáp:

{{TRACED_CLAIMS}}

Hai tuyên bố của Ca B được chọn vì chúng cho thấy hai đường đi khác nhau của bộ kiểm chứng. B1 có số liệu (hơn 99%), nhưng không đoạn nào nêu lại tỉ lệ đó; 5 đoạn tìm được chỉ cùng chủ đề, nên kết luận dừng ở "ủng hộ một phần". B2 không có số liệu. Báo cáo thường niên 2024 xác nhận B2 bằng bốn câu có cụm "xác nhận" (BSI trao giấy kiểm tra, xác nhận khí nhà kính). Nhưng đó vẫn là tài liệu của chính Hòa Phát, nên **chốt nguồn độc lập** (`independent_support_v1`, bật từ 15/11) giữ B2 ở "ủng hộ một phần" kèm lý do "các báo cáo của cùng một doanh nghiệp khớp nhau chưa phải là kiểm chứng". B2 cũng chứa bẫy năm trong tên chuẩn "ISO 14064-1:2018". Lỗi lấy năm này làm kỳ báo cáo đã làm câu B2 của các phiên trước bị nâng nhầm lên "được ủng hộ" ngày 13/11, và đã được sửa ngày 14/11 (mục 9.1). Câu B2 cũ ("Thực hiện kiểm kê khí nhà kính theo tiêu chuẩn ISO 14064-1:2018 và báo cáo đầy đủ…") nay bị gắn cờ `list_glue` vì là hai gạch đầu dòng đọc liền, nên tài liệu theo dõi câu B2 mới ở trên.
