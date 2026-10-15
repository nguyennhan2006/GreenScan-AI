# Bán kết 25/10/2026 — bộ chuẩn bị trình bày

**Lập:** 09/10/2026 · **Cho:** Quỳnh, Thảo, Nhân · **Căn cứ:** Thể lệ AI-Quantum Challenge 2026 (Kế hoạch 567/KH-HVTC), Điều 8.2, 11.2, 14

| Tệp | Dùng để | Người chính |
| --- | --- | --- |
| [01_NOI_DUNG_TRINH_BAY.md](01_NOI_DUNG_TRINH_BAY.md) | 14 slide + phụ lục: nội dung trên slide, lời nói, thời lượng, câu BGK hỏi; bản 10 phút và bản cắt 7 phút; bảng số liệu được phép dùng | Quỳnh (dựng slide), cả nhóm (học lời) |
| [02_KICH_BAN_SINH_ANH.md](02_KICH_BAN_SINH_ANH.md) | Hệ phong cách, prompt 10 ảnh minh hoạ, đặc tả 4 hình vẽ tay, nhật ký AI | Thảo |
| [03_KICH_BAN_PROTOTYPE_DEMO.md](03_KICH_BAN_PROTOTYPE_DEMO.md) | Gói nộp 10/10, chuẩn bị máy, demo 2:40 bấm từng bước, 11 ảnh chụp, video dự phòng, lịch tập | Nhân |
| [04_HOI_DAP_BO_SUNG.md](04_HOI_DAP_BO_SUNG.md) | 6 câu QA_DRILL đã lỗi thời + câu hỏi mới theo 6 tiêu chí | cả nhóm |

---

## 1. Hạn chót

| Ngày | Mốc | Ghi chú |
| --- | --- | --- |
| **10/10 (mai)** | **Nộp sản phẩm vòng 2**: báo cáo giải pháp 8–12 trang · slide · prototype · mã nguồn zip · hướng dẫn cài đặt | Điều 8.2 — slide cũng nằm trong gói nộp. Gói tối thiểu: [03 §1](03_KICH_BAN_PROTOTYPE_DEMO.md#1-gói-nộp-hạn-10102026-điều-82) |
| 15/10 | Hỏi xong BTC (§3); ảnh minh hoạ xong; video demo xong | |
| **17/10** | **Đóng băng số liệu trên slide** (số gold, κ, thời gian đo trên máy trình chiếu) | Sau ngày này không đổi số |
| 18–24/10 | Tập: cả bài, hỏi đáp ngẫu nhiên, máy dự phòng | lịch ở [03 §7](03_KICH_BAN_PROTOTYPE_DEMO.md#7-lịch-tập) |
| **25/10 (CN)** | Thuyết trình bán kết | |

---

## 2. Việc phải làm — theo thứ tự

| # | Việc | Ai | Hạn | Vì sao |
| --- | --- | --- | --- | --- |
| V1 | Gói nộp 10/10: cập nhật báo cáo giải pháp từ `technical_brief/` (bản 24/09 còn mô tả BGE-M3/reranker như cấu hình đang chạy); gắn tag `rc-2026-10-10`; zip mã nguồn; thử hướng dẫn trên máy khác | Nhân + Quỳnh | **10/10** | Không nộp = không có vòng 2 |
| V2 | Viết khai báo công cụ AI (§4) vào báo cáo và slide P1 | cả nhóm | 10/10 | Điều 14 — bắt buộc |
| V3 | Sửa sơ đồ pipeline (VEC-01): badge 3 bước đọc đổi **MÔ HÌNH → LUẬT**, thêm khối **HÀNG ĐỢI SOÁT**, đổi "Hồ sơ kiểm chứng" → "Giấy làm việc" — đặc tả ở [02 §3](02_KICH_BAN_SINH_ANH.md#3-hình-vẽ-tay-vec--không-sinh-bằng-ai) | Nhân | 13/10 | Sơ đồ hiện mô tả mô hình ở chỗ đang chạy luật — BGK kỹ thuật sẽ hỏi |
| V4 | Đọc bản gốc QĐ 263/QĐ-TTg (hạn ngạch 110 cơ sở) và nguồn ngày khai trương sàn các-bon HNX; xác nhận 3 ngày hiệu lực đã sửa trong registry | Thảo | 15/10 | Đang là nguồn thứ cấp — chưa xác minh thì bỏ khỏi slide S4 |
| V5 | Sinh 10 ảnh theo file 02, ghi nhật ký | Thảo (+ Quỳnh) | 15/10 | |
| V6 | Chụp 11 ảnh sản phẩm, ghi 2 video | Nhân | 15/10 | |
| V7 | Đo lại thời gian phân tích Hòa Phát trên **máy trình chiếu** (3 lần) | Nhân | 17/10 | Số trên slide phải là số của máy đang demo |
| V8 | Điền trạng thái gold (số cặp đã gán, κ) vào S10, S11 và câu hỏi đáp #11 | Quỳnh | 17/10 | Nếu chưa đủ: nói thẳng "đang gán" |
| V9 | Sửa 6 câu lỗi thời trong `QA_DRILL.md` theo [04 §1](04_HOI_DAP_BO_SUNG.md#1-sáu-câu-trả-lời-trong-qa_drill-đã-lỗi-thời--học-bản-này) | Quỳnh | 18/10 | |
| V10 | Gửi/cập nhật lời mời dùng thử (A10) — để có câu trả lời thật cho "đã có đối tác chưa" | Quỳnh + Thảo | 10/10 | Tiêu chí 5: 90–100 điểm = "đã có đối tác tiềm năng" |

---

## 3. Hỏi Ban tổ chức (email AI-Quantum@hvtc.edu.vn) trước 15/10

1. Thời lượng thuyết trình và hỏi đáp **vòng 2** (thể lệ chỉ ghi cho vòng 3: 10 + 8 phút).
2. Slide nộp ngày 10/10 có được **thay bản cập nhật** trước 25/10 không?
3. Giới hạn dung lượng tệp nộp (mã nguồn có ~100 MB dữ liệu đã chuẩn hoá).
4. Phòng thi: được dùng laptop của đội không, cổng kết nối máy chiếu, độ phân giải, có mạng không.
5. Prototype dạng web app chạy tại máy (không triển khai lên internet) có được chấp nhận không, hay cần đường link.

---

## 4. Khai báo công cụ AI hỗ trợ (Điều 14) — bản nháp, cả nhóm sửa cho đúng sự thật

> Thể lệ Điều 14: *"Sử dụng các mô hình AI tạo sinh để tạo ra toàn bộ bài dự thi mà không có sự can thiệp, cải tiến đáng kể của con người, không giải thích được"* là hành vi bị cấm; *"việc sử dụng AI hỗ trợ (ví dụ: kiểm tra lỗi, gợi ý cấu trúc) là được phép nhưng phải được khai báo rõ trong tài liệu."*

Bản nháp — **chỉ giữ dòng đúng với những gì nhóm đã dùng, thêm dòng còn thiếu**:

| Công cụ | Dùng vào việc | Phần của nhóm |
| --- | --- | --- |
| Claude (Anthropic), qua Claude Code | Hỗ trợ viết, rà soát và kiểm thử mã nguồn; soạn nháp tài liệu kỹ thuật và kịch bản trình bày (lịch sử commit có ghi đồng tác giả) | Đặt bài toán, thiết kế kiến trúc và luật kiểm chứng, chọn dữ liệu, đọc và chấp nhận từng thay đổi, chạy và diễn giải mọi phép đo |
| *[công cụ sinh ảnh — ChatGPT / Gemini / Midjourney…]* | Hình minh hoạ trên slide (danh sách theo nhật ký, file 02 §4); không dùng cho ảnh giao diện sản phẩm | Ý tưởng hình, chọn bản, đặt toàn bộ chữ, chỉnh màu và bố cục |
| GLM-5.2 qua FPT AI Marketplace | **Thành phần của sản phẩm** (chế độ đám mây): đọc cặp tuyên bố–bằng chứng mà luật không quyết được, có chốt chặn — không phải công cụ tạo bài thi | Thiết kế chốt chặn, thí nghiệm có đối chứng ngày 28/09 |
| *[thêm nếu có: công cụ dịch, kiểm chính tả, tạo giọng đọc video…]* | | |

Câu nói khi bị hỏi: [04 tiêu chí 6](04_HOI_DAP_BO_SUNG.md#tiêu-chí-6--trình-bày-tài-liệu-10).

---

## 5. Quy ước tệp

- Ảnh cuối và ảnh chụp: `ban-ket-2026-10-25/img/` — **không commit** (đã gitignore: ảnh nặng và đổi theo mỗi lần tập); bản slide cuối mới là thứ lưu.
- Video: `ban-ket-2026-10-25/video/` — không commit (gitignore).
- Nhật ký AI (file 02 §4) **có commit** — đó là bằng chứng khai báo.
- Phiên demo: *"DEMO Bán kết — Hòa Phát BCPTBV 2025 + BCTN 2024 (ngoại tuyến)"* trong *Lịch sử phân tích* (mã ở [03 §2.1](03_KICH_BAN_PROTOTYPE_DEMO.md#21-phiên-phân-tích-dùng-cho-demo)).
