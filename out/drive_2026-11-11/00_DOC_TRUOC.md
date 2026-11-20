# GreenScan AI — hồ sơ nộp Ban tổ chức (cập nhật 11/11/2026)

Cuộc thi Trí tuệ nhân tạo và Lượng tử trong Kinh tế – Tài chính – Kế toán lần thứ I · mã AQ2026-119 · nhóm GreenScan (Nhân, Quỳnh, Thảo)

> **Kết quả này là tín hiệu rủi ro dựa trên thông tin công khai, hỗ trợ người hành nghề đảm bảo khoanh vùng kiểm tra — không thay thế thủ tục thu thập bằng chứng theo ISSA 5000.**

## Thư mục

| Thư mục | Nội dung | Đọc khi |
|---|---|---|
| `01_bao-cao/` | Bài báo cáo đầy đủ (`GREENSCAN_BAI_BAO_2026-11-11.pdf`, 14 trang, kèm bản .md và hình), hướng dẫn sử dụng một trang | Muốn hiểu hệ thống, phương pháp và kết quả đo |
| `02_so-do/` | Sơ đồ quy trình (PNG, SVG) và tài liệu giải thích quy trình dễ hiểu | Cần một hình tổng quan |
| `03_du-lieu/` | Toàn bộ bộ dữ liệu đánh giá, chuẩn mực IAASB, thẻ dữ liệu (`THE_DU_LIEU.md`) | Kiểm lại số đo hoặc hỏi về dữ liệu |
| `04_video/` | Video demo vòng 2 (09/11/2026), video hướng dẫn sử dụng | Xem sản phẩm chạy |

## Số liệu chính (chạy ngoại tuyến, không mô hình ngôn ngữ lớn)

| Nội dung | Kết quả | Loại nhãn |
|---|---|---|
| Báo cáo Hòa Phát (264 trang) | 156 tuyên bố + 16 số liệu công bố; hàng đợi "Cần soát" chọn 8/172 mục; 107–121 giây trên laptop không GPU | — |
| Bộ phân loại tuyên bố e5-base | macro-F1 0,73 [0,69; 0,76], luật từ khoá 0,36 | Claude |
| Kết luận "mâu thuẫn" sai trên tuyên bố thật (GS-Eval v2) | 24 → 0 sau chốt chặn 05/11; GS-Bench 453/453 giữ nguyên | Claude |
| 4 ca đã có phán quyết (BNY Mellon, DWS, KLM, Keurig Dr Pepper) | 4/4 khớp | phán quyết công khai |
| Mẫu câu kết luận ISSA 5000 | nhận đúng 12/12 báo cáo minh hoạ IAASB | tiêu đề IAASB |
| Bài kiểm tự động | 626 bài, đều qua | — |

Mọi số đo hiện có so với đáp án dựng sẵn hoặc nhãn do Claude gán. Bộ phiếu gán nhãn người đã dựng xong (`03_du-lieu/bo-du-lieu/gold_nguoi/`).
