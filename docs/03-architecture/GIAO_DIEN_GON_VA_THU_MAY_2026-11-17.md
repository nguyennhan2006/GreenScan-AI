# Giao diện gọn hơn, thử toàn bộ chức năng trên laptop, gói chạy ngay (17/11/2026)

Quyết định D-2026-11-17-01. Mọi số đều [ĐÃ THỰC NGHIỆM] trên laptop i7-1355U, 16 GB, không card đồ hoạ, ngày 17/11/2026.

## 1. Vì sao làm

Yêu cầu của đội: thử hệ thống trên laptop với mọi chức năng bật, giảm số bước và thông tin gây rối cho người dùng, có video một phiên đầy đủ, và có một gói giải nén là chạy.

Soát giao diện trước khi sửa cho thấy ba chỗ làm người mới lúng túng:

1. **Không trang nào nói bước tiếp theo.** Trang tải tài liệu bắt đầu bằng hai ô không bắt buộc (tên doanh nghiệp, tên phiên) và một ô chọn quy tắc nội bộ, rồi mới tới khung thả tệp.
2. **Trang chi tiết tuyên bố cao khoảng 3.500 điểm ảnh.** Nút chốt nằm cuối trang, sau bảy khối thông tin; đoạn “chỉ liên quan” chiếm chỗ ngang với đoạn quyết định.
3. **Hàng đợi không bao giờ “xong”.** Số liệu công bố nằm trong hàng đợi nhưng không có quyết định nào để ghi, nên số đếm ở thanh bên và ô “Đã chốt 0/5” không về đích được.

## 2. Đã đổi gì (`next-step-v1`)

| Chỗ | Trước | Sau |
|---|---|---|
| Mọi trang của quy trình | không có gợi ý | một dòng “Việc tiếp theo · bước n/4” kèm đúng một nút làm việc đó (`components/NextStep.jsx`); ẩn được, bật lại ở Cài đặt |
| Lần đầu mở | nhập tên rồi vào trang hướng dẫn 7 bước | nhập tên rồi vào thẳng bước 1; trang hướng dẫn vẫn ở thanh bên |
| Tải tài liệu | ô phụ ở trên, nút “Mẫu HPG” nhỏ cạnh ô đường dẫn, bốn thẻ lặp lại thanh bên, hai dòng “Ngoại tuyến” | khung thả tệp ở trên cùng; hai bộ mẫu thành hai ô lớn (bộ mẫu nhỏ 3 tệp chạy vài giây, và Hòa Phát); ô phụ gom vào “Tuỳ chọn thêm”; nút bắt đầu ghi rõ còn thiếu gì |
| Bộ mẫu | chỉ có Hòa Phát | thêm “Công ty Minh Họa” (`intake.py::SAMPLE_SETS`) |
| Hàng đợi | “Đã chốt” đếm cả số liệu công bố | đếm tuyên bố; hết tuyên bố thì dòng “Việc tiếp theo” chuyển sang xuất giấy làm việc; phần “những gì chưa kiểm” thu gọn, bấm để mở |
| Chi tiết tuyên bố | luôn hiện 7 khối | mặc định “xem gọn”: câu, đoạn bằng chứng có kết luận, phép tính (nếu có), tiền lệ (nếu có), quyết định. Nút “Xem đầy đủ” mở mọi khối như cũ |
| Bằng chứng | 5 đoạn ngang hàng | đoạn ủng hộ / mâu thuẫn hiện trước; đoạn “chỉ liên quan” gom vào một nút |
| Quyết định | 6 ô điều khiển một hàng và một đoạn giải thích dài | ba lựa chọn: “Xác nhận gợi ý của máy”, “Máy sai, tôi sửa” (mở ô chọn kết luận và lý do), “Chưa kết luận / Yêu cầu thêm bằng chứng”; vai trò và đoạn quyết định gom vào “Ghi thêm” |
| Sau khi chốt | đứng yên | “Mục tiếp theo” đi tới tuyên bố còn chờ trong hàng đợi; hết thì về hàng đợi |
| Dòng cảnh báo vàng | mọi trang | chỉ ở trang có kết quả (hàng đợi, tuyên bố, giấy làm việc); câu ở chân trang giữ nguyên |
| Ô lời giải thích của mô hình | “kết luận do quy tắc đưa ra” | “mô hình không tự kết luận ‘ủng hộ’ hay ‘mâu thuẫn’” (đúng với D-2026-11-16-01) |

Chiều cao trang chi tiết của mục 1 bộ mẫu: khoảng 3.500 → 1.550 điểm ảnh ở chế độ xem gọn (2.000–2.250 khi bật quy tắc nội bộ và có tiền lệ).

Không đổi: luật, kết luận, thứ tự hàng đợi, giấy làm việc, API. Thay đổi phía máy chủ duy nhất là thêm một bộ mẫu.

## 3. Thử trên laptop

### 3.1 Mô hình trên máy, không dùng bộ nhớ đệm

Bộ mẫu Công ty Minh Họa, `qwen3:4b-instruct-2507-q4_K_M` qua Ollama, bộ nhớ đệm rỗng.

| Số đo | 16/11 | 17/11 |
|---|---|---|
| Tổng thời gian | 940 giây | 1.066 giây (máy đang chạy kiểm thử và dựng giao diện song song) |
| Cặp tuyên bố – bằng chứng hỏi mô hình | 8, trong đó 1 quá hạn 180 giây | 8, trả lời đủ 8, 413 giây |
| Điền thuộc tính | 5 lượt | 5 lượt, 0 lỗi |
| Lời giải thích | 3 lượt | 3 lượt, 0 lỗi, hiện 2 |
| Kết luận | 3 mâu thuẫn, 1 ủng hộ một phần, 1 chưa được chứng minh | giống hệt |

Hạn chờ 600 giây (đặt hôm 16/11) đã hết lượt bị cắt. Chạy lại cùng tài liệu: 1–3 giây, lấy từ bộ nhớ đệm.

### 3.2 Thử từng chức năng qua giao diện (trình duyệt tự động, 23 bước)

Kho thử là bản sao của kho demo; kho demo thật không bị đụng. Kết quả: **23/23 bước đạt**, không lỗi JavaScript.

| Nhóm | Bước | Số đo |
|---|---|---|
| Vào việc | nhập tên → bước 1 có dòng “Việc tiếp theo”; bộ mẫu 3 tệp, vai trò gán sẵn | 3–4 giây mỗi bước |
| Mô hình trên máy | bật công tắc; nút “Thử mô hình” | 10 giây khi mô hình đã nạp, 30 giây khi vừa nạp |
| Phân tích | 3 tệp + mô hình trên máy + quy tắc nội bộ của ngân hàng mẫu | 3 giây từ bộ nhớ đệm; lần đầu 348 giây vì quy tắc nội bộ đưa thêm 2 tuyên bố vào hàng đợi, cần 4 lượt gọi mới |
| Soát | mở mục, mở nguồn, xem đầy đủ 5 khối, xác nhận, ghi đè có lý do, chốt hết → hàng đợi báo xong, số đếm thanh bên về 0 | 2–15 giây |
| Xuất | giấy làm việc có tên người soát; tải bảng CSV | 5 giây |
| Trang khác | sửa báo cáo, học từ phản hồi, thư viện pháp lý, lịch sử | 3–5 giây mỗi trang |
| Mô hình đám mây | bật, thử một lượt, tắt | 1,1–1,2 giây; một lần 22 giây |
| Khác | tắt / bật dòng “Việc tiếp theo”; dán văn bản thay cho tệp | 4 giây |
| Báo cáo thật | Hòa Phát 264 trang, chỉ luật, chạy từ đầu qua giao diện | 186 giây kể cả tải tệp: 171 tuyên bố, hàng đợi 7/186 (trùng số trong báo cáo nộp) |

Kiểm thử tự động của mã: 768/768 qua sau các thay đổi.

RAM: máy còn 2,1–2,8 GB trống trong lúc thử. Đã tắt Docker Desktop, WSL và một máy chủ xem trước video còn sót; giữ nguyên Chrome, Zalo và VS Code.

### 3.3 Điểm yếu thấy khi thử, chưa sửa

- **Mô hình 4B trên CPU:** hơn 15 phút cho 5 tuyên bố ở lần đầu. Báo cáo dài chỉ chạy được bằng luật trên máy này.
- **Câu mô hình gắn “cần người xem” có thể nằm ngoài hàng đợi.** Ở bộ mẫu, câu “doanh nghiệp xanh hàng đầu” có điểm ưu tiên 44,7, dưới ngưỡng 55. Sửa là đổi chính sách hàng đợi, kéo theo đổi các con số đã nộp, nên để lại.
- **Danh sách lý do ghi đè thiếu một mục** cho trường hợp “máy không dám kết luận, người chốt sau khi đọc nguồn”.
- **Mô hình đám mây gói miễn phí:** có lượt 1 giây, có lượt 22 giây.
- **Số liệu công bố không có trạng thái “đã xem”.** Hiện chỉ không tính chúng vào số cần chốt.

## 4. Video một phiên

`nop_vong2/video/demo_1_phien/` (ngoài repo). Kịch bản và nguồn từng con số: `KICH_BAN.md`. 19 nhịp, khoảng 4 phút: bài toán (4 cảnh đồ hoạ) → một phiên đầy đủ trên bộ mẫu với mô hình trên máy (12 nhịp quay ứng dụng thật) → kết quả trên Hòa Phát, giới hạn, kết (3 cảnh).

## 5. Gói chạy ngay (`portable-v1`)

`tools/build_portable.py` dựng một thư mục cho Windows 64-bit: Python nhúng và thư viện, mã nguồn bản chốt, giao diện đã dựng, Tesseract (chỉ các tệp cần), kho phiên mẫu, bộ nhớ đệm của mô hình. Người dùng bấm đúp `CHAY_GREENSCAN.bat`. Mô hình trên máy không nằm trong gói (2,5 GB); `CAI_MO_HINH_TREN_MAY.bat` tự cài Ollama và tải mô hình. Gói không chứa khoá nào. Số đo của gói: xem `docs/11-vong-2-nop-bai/TRANG_THAI_NOP_BAI.md`.
