# Kịch bản prototype: gói nộp, máy trình chiếu, demo trực tiếp, ảnh chụp, video

**Ngày:** 09/10/2026 · **Người chính:** Nhân (máy, demo) · Quỳnh (bấm giờ, soát lời) · Thảo (soát chữ pháp lý trên màn hình)
**Đi kèm:** [01_NOI_DUNG_TRINH_BAY.md](01_NOI_DUNG_TRINH_BAY.md) slide S6 · [02_KICH_BAN_SINH_ANH.md](02_KICH_BAN_SINH_ANH.md)

---

## 0. "Prototype" của vòng 2 là gì

Thể lệ Điều 8.2: *"Prototype ở một trong các dạng: web app, dashboard, chatbot, mobile app; mã nguồn hoặc file chạy thử; tài liệu hướng dẫn cài đặt, chạy thử"* và Điều 11.2 tiêu chí 4: *"chạy được demo… giao diện ở mức sử dụng được, thể hiện được đầu vào – đầu ra chính… mã nguồn có cấu trúc, chạy lại được với hướng dẫn"*.

GreenScan **đã là một web app chạy thật**. Vì vậy:
- **Không "sinh" prototype bằng AI.** Mọi hình giao diện trên slide, báo cáo, video là **ảnh chụp sản phẩm thật** (§4).
- Ảnh AI chỉ được dùng cho **tính năng đích chưa làm**, và phải đóng dấu *"THIẾT KẾ ĐÍCH — CHƯA CÓ TRONG PROTOTYPE"* (§6). Không có cũng được.

---

## 1. Gói nộp hạn 10/10/2026 (Điều 8.2)

| # | Thành phần | Lấy từ đâu | Ai | Trạng thái 09/10 |
| --- | --- | --- | --- | --- |
| 1 | **Báo cáo giải pháp 8–12 trang** | Cập nhật `docs/07-presentation/technical_brief/` (9 trang, bản 24/09 — còn mô tả BGE-M3/rerank như cấu hình, thiếu hàng đợi, giấy làm việc, chế độ chạy). Dùng §0–§4 của file 01 làm khung | Nhân + Quỳnh | ☐ |
| 2 | **Slide trình bày** | Dựng theo file 01 + ảnh file 02. Nếu không kịp ảnh, nộp bản chữ + ảnh chụp thật; ảnh minh hoạ bổ sung trước 25/10 (hỏi BTC có được nộp bản cập nhật) | Thảo + Quỳnh | ☐ |
| 3 | **Prototype** | Web app (chạy tại máy) + video demo 3–4 phút (§5) + bộ ảnh chụp (§4) | Nhân | ☐ |
| 4 | **Mã nguồn zip** | `git archive --format=zip -o GreenScan_AQ2026-119_src.zip rc-2026-10-10` — chỉ tệp đã commit: không có `.env`, không có PDF bên thứ ba, không có `.quantum/` | Nhân | ☐ tag chưa gắn |
| 5 | **Hướng dẫn cài đặt, chạy thử** | `README.md` gốc (mục chạy nhanh) + một trang PDF: cài Python 3.11+ và Node, chạy `GreenScan.bat`, mở trình duyệt, dùng nút "Điền ví dụ" | Nhân | ☐ chưa thử trên máy sạch |
| 6 | **Khai báo công cụ AI** | README §4 — đưa vào báo cáo (một mục) và slide P1 | Cả nhóm | ☐ |

Kiểm trước khi nộp: giải nén zip vào một thư mục mới trên **máy khác**, làm đúng theo hướng dẫn, chạy được ví dụ. Hỏi BTC giới hạn dung lượng tệp nộp — repo có `data/crawl/vn30/normalized` (~100 MB JSONL); nếu quá giới hạn thì loại thư mục đó khỏi zip và ghi cách tải lại.

---

## 2. Chuẩn bị máy trình chiếu

### 2.1 Phiên phân tích dùng cho demo

| Phiên | Nội dung | Dùng ở |
| --- | --- | --- |
| **`cd5a82e3`** — *"DEMO Bán kết — Hòa Phát BCPTBV 2025 + BCTN 2024 (ngoại tuyến)"* | Tạo 09/10 qua đúng luồng tải lên của giao diện (PDF được lưu vào kho tài liệu nên **mở được trang gốc**). Chế độ ngoại tuyến. 156 tuyên bố · hàng đợi 9 mục · 1 thủ tục cộng lại bảng KNK | S6 demo |
| `ce4eb6e4` — KLM | Ca có phán quyết: "bị bác bỏ" từ nguồn có thẩm quyền (toà kết luận 15/19 tuyên bố gây hiểu nhầm) | Hỏi đáp, P5 |

**Không dùng** các phiên Hòa Phát cũ (25–28/09): tạo bằng mã trước ngày 06/10, hàng đợi 22 mục lẫn câu giải thích công nghệ và "số liệu" rác.

**Tạo lại trên máy trình chiếu** (nếu máy trình chiếu không phải máy của Nhân): mở GreenScan → *1. Tải tài liệu* → tên doanh nghiệp `Tập đoàn Hòa Phát` → chọn hai PDF trong `data/real_cases/sources/originals/` (BCPTBV 2025 vai trò *nguồn tuyên bố*, BCTN 2024 vai trò *bằng chứng*) → đặt tên phiên như trên → chạy. Ghi lại thời gian chạy để điền S11.

### 2.2 Bảng kiểm T-1 (24/10) và T-0 (sáng 25/10)

| # | Kiểm | T-1 | T-0 |
| --- | --- | --- | --- |
| 1 | `GreenScan.bat` khởi động; trang *Cài đặt & chế độ chạy* ghi **"Ngoại tuyến — không gửi tài liệu ra ngoài"**. ⚠️ Trên laptop của Nhân, `.env` là bản cũ (29/09) ghi rõ `QUANTUM_LLM_STANCE=on_ambiguous` → app khởi động ở **chế độ đám mây** (đã kiểm 09/10). Trước demo sửa `.env`: đặt `QUANTUM_PROFILE=offline` và `QUANTUM_LLM_STANCE=off` (hoặc chép lại từ `.env.example` rồi dán khoá FPT) | ☐ | ☐ |
| 2 | Tắt Wi-Fi rồi mở phiên demo: mọi bước §3 chạy được (chứng minh không cần mạng) | ☐ | ☐ |
| 3 | Bấm "Mở tài liệu gốc tại vị trí này" ở mục demo: ảnh trang hiện ra, có tô sáng | ☐ | ☐ |
| 4 | Trình duyệt: chế độ toàn màn hình (F11), thu phóng **125%**, tắt thanh dấu trang, tắt tiện ích, tắt thông báo Windows (Focus assist) | ☐ | ☐ |
| 5 | Máy cắm sạc; chế độ nguồn *Best performance*; tắt cập nhật Windows tự động trong ngày | ☐ | ☐ |
| 6 | Đổi tên người soát trên trang bắt đầu thành tên người demo | ☐ | ☐ |
| 7 | **Phiên demo sạch:** quyết định người soát được lưu theo kiểu chỉ ghi thêm (nhật ký kiểm toán, không xoá), nên các lần tập để lại quyết định trên phiên. Tập trên một phiên riêng; tối 24/10 tạo **phiên demo mới** (§2.1) để lúc thi hàng đợi bắt đầu từ "chưa chốt" | ☐ | ☐ |
| 8 | Video dự phòng (§5) chép sẵn trên **máy** và **USB**; mở thử được bằng trình phát mặc định | ☐ | ☐ |
| 9 | Máy dự phòng thứ hai đã cài sẵn, có phiên demo | ☐ | ☐ |
| 10 | Đầu chuyển HDMI/USB-C; thử máy chiếu ở độ phân giải 1920×1080 nếu được vào phòng trước | ☐ | ☐ |

---

## 3. Kịch bản demo trực tiếp — 2:40

**Nguyên tắc:** kể một câu chuyện, không đi menu. Mỗi bước có **một điều BGK phải thấy**. Nhân bấm và nói; Quỳnh giơ tay ra hiệu khi còn 30 giây.

| Thời điểm | Bấm | Nói (gợi ý — học ý, không học thuộc) | BGK phải thấy | Nếu hỏng |
| --- | --- | --- | --- | --- |
| **0:00–0:15** | Đang ở *Lịch sử phân tích* → mở phiên *"DEMO Bán kết — Hòa Phát…"* | "Đây là báo cáo bền vững 2025 và báo cáo thường niên 2024 của Hòa Phát — 264 trang, tài liệu công khai. Phân tích chạy khoảng hai phút trên chính laptop này, không GPU, không mạng; để tiết kiệm thời gian em mở phiên đã chạy. Góc trên ghi: ngoại tuyến, tài liệu không rời máy." | Chip "Ngoại tuyến — không gửi tài liệu ra ngoài" | Không mở được phiên → mở video từ 0:00 |
| **0:15–0:50** | *2. Soát theo hàng đợi* — dừng ở danh sách **Nên soát trước** | "Hệ thống trích được 156 tuyên bố môi trường. Đưa 156 dòng cho kiểm toán viên thì vô ích — nên nó xếp thứ tự và đưa ra 9 mục nên soát trước. Mỗi mục ghi lý do: nhóm khí nhà kính, có văn bản đang hiệu lực cùng chủ đề, thiếu mấy trên năm thuộc tính. Và đây —" *(chỉ khung "Phạm vi lượt soát này — những gì chưa được kiểm")* "— hệ thống nói rõ 163 mục nó không soát trong lượt này và vì sao. Kiểm toán viên cần dòng này nhất." | 156 → 9; lý do dạng thẻ; khung phạm vi không soát | — |
| **0:50–1:35** | Mở mục **#2** — *"…cả hai khu liên hợp… đều có mức độ tự chủ điện năng **rất cao**…"* (trang 7). Kéo tới **Bằng chứng** → bấm **Mở tài liệu gốc tại vị trí này** ở đoạn BCTN 2024 trang 86 | "Câu ở trang 7 nói 'rất cao' — không có số. Hệ thống tìm sang báo cáo thường niên 2024, trang 86: tự chủ 90%, 788 triệu kWh. Nó **không** tự kết luận 'đúng', vì tuyên bố không nêu số, kỳ hay năm gốc để so — kết luận là 'khớp một phần', và đây là danh sách thiếu gì. Bấm vào bằng chứng thì mở đúng trang gốc, đúng đoạn được tô." | Thuộc tính thiếu: số liệu, kỳ, năm gốc · trang gốc tô sáng | Trang không hiện → nói "đây là ảnh trang gốc" và chuyển sang SHOT-05 trên slide dự phòng |
| **1:35–2:00** | Về hàng đợi → khung **Thủ tục trên số liệu công bố** → dòng cộng lại bảng khí nhà kính trang 39 | "Với số liệu, hệ thống làm thủ tục kiểm toán viên vẫn làm: cộng lại bảng. Phạm vi 1 cộng phạm vi 2: 22.540.603 cộng 933.876 bằng 23.474.479; doanh nghiệp công bố 23.474.480 — lệch 1 tấn, trong sai số làm tròn, nên **khớp**. Phép tính hiện ra trên màn hình — không phải mô hình đoán." | Phép tính đầy đủ, kết luận khớp | — |
| **2:00–2:20** | Quay lại mục #2 → **Xét duyệt** → chọn kết luận của người soát, gõ lý do ngắn → **Lưu** | "Kết luận cuối là của người. Kiểm toán viên chọn, ghi lý do; quyết định được lưu kèm tên người soát và hàng đợi cập nhật." | Mục chuyển trạng thái; bộ đếm hàng đợi giảm | Lưu lỗi → bỏ bước, nói một câu ở bước sau |
| **2:20–2:40** | *4. Giấy làm việc* → **Mở giấy làm việc** → cuộn nhanh → **In / Lưu PDF** (mở hộp thoại rồi đóng) | "Đầu ra cuối là giấy làm việc tiếng Việt: phạm vi tài liệu kèm mã băm, thủ tục đã chạy, kết quả từng mục kèm trang, những gì không kiểm và vì sao, quyết định người soát, và chỗ ký. In ra PDF được ngay." | Mục "những gì không kiểm"; chỗ ký | — |

**Không mở trong demo:**
- Mục **#1** của hàng đợi — chữ gãy dòng "HÒA PHÁT trò nền tảng…" (đúng là "vai trò"): lỗi trích đã biết (ISSUES P5).
- *Tất cả tuyên bố* lọc "ủng hộ" — 1 trong 2 là chữ dính cột ("Hoàn thành kiểm kê khí nhà kính theo tiêu 90%": 90% thuộc câu "tự chủ 90% điện" bên cạnh). Nếu BGK tự hỏi: nhận đúng như vậy, chỉ ra đây là lý do bộ gán nhãn và nhãn "khớp một phần" tồn tại (P2).
- Chế độ đám mây — không bật mạng trong phòng thi.

**Nếu BGK yêu cầu chạy trực tiếp một tài liệu:** *1. Tải tài liệu* → **Điền ví dụ** → chạy (vài giây, văn bản ngắn) → mở hàng đợi. Không chạy lại hai PDF 264 trang trước hội đồng (≈ 2 phút chờ).

---

## 4. Danh sách ảnh chụp sản phẩm thật

Chụp từ phiên `cd5a82e3`, trình duyệt 1920×1080, thu phóng 125%, ẩn thanh địa chỉ (F11). Lưu PNG vào `ban-ket-2026-10-25/img/` với tên dưới đây. Dùng cho slide dự phòng, báo cáo giải pháp, video.

| Mã | Màn hình / trạng thái | Cắt | Dùng ở |
| --- | --- | --- | --- |
| SHOT-01 | *Tải tài liệu*, đã chọn 2 PDF, ô tên doanh nghiệp điền "Tập đoàn Hòa Phát", thanh tiến độ đang chạy (chụp lúc ~50%) | toàn màn | báo cáo §prototype |
| SHOT-02 | **Hàng đợi** — danh sách *Nên soát trước* 9 mục, lý do hiện đủ | toàn màn | slide dự phòng S6, báo cáo |
| SHOT-03 | Khung *Phạm vi lượt soát này — những gì chưa được kiểm* | khung | S6, S11 |
| SHOT-04 | Chi tiết mục #2: tuyên bố + 5 thuộc tính (có/thiếu) + *Việc cần làm để tuyên bố kiểm chứng được* | nửa trên | S5, S6 |
| SHOT-05 | Ảnh trang gốc BCTN 2024 trang 86, đoạn được tô | khung xem trang | S6 dự phòng |
| SHOT-06 | *Thủ tục trên số liệu công bố* — dòng cộng lại bảng KNK trang 39 | khung | S6, S8 |
| SHOT-07 | Hộp *Xét duyệt* đang chọn kết luận, có lý do | hộp | S6 |
| SHOT-08 | Giấy làm việc — trang đầu (mục tiêu, phạm vi, mã băm) | trang | S6, báo cáo |
| SHOT-09 | Giấy làm việc — mục "những gì không kiểm và vì sao" + chỗ ký | trang | S11, báo cáo |
| SHOT-10 | *Cài đặt & chế độ chạy* — chế độ ngoại tuyến, bảng "chế độ chạy theo từng việc" | toàn màn | S12 |
| SHOT-11 | Phiên KLM — tuyên bố "bị bác bỏ", đoạn bằng chứng từ nguồn có thẩm quyền | khung | P5 |

Kiểm mỗi ảnh: không lộ đường dẫn thư mục cá nhân, khoá API, tên người khác ngoài nhóm.

---

## 5. Video dự phòng — 3 đến 4 phút

- **Ghi bằng:** OBS Studio (miễn phí) · 1920×1080 · 30 fps · MP4 · chỉ cửa sổ trình duyệt · micro ngoài nếu có.
- **Kịch bản:** đúng bảng §3, cộng thêm **0:00–0:40 chạy thật từ đầu** (tải hai PDF, thanh tiến độ chạy qua từng bước — tua nhanh ×8 phần chờ, ghi chữ "tua nhanh ×8" ở góc). Đây là bằng chứng "chạy được" mà demo trực tiếp không có thời gian cho.
- **Phụ đề tiếng Việt** gắn cứng (phòng thi có thể không bật được loa).
- **Hai bản:** `GreenScan_demo_full.mp4` (3–4 phút, nộp kèm prototype và đăng nội bộ) · `GreenScan_demo_2m40.mp4` (đúng phần S6, để chiếu thay demo nếu máy hỏng).
- Nếu dùng giọng đọc tổng hợp hoặc công cụ AI dựng video → **ghi vào nhật ký AI** (file 02 §4).

---

## 6. Mockup tính năng đích — tuỳ chọn, phải đóng dấu

Chỉ dùng nếu slide S12 (lộ trình) cần hình minh hoạ cho thứ **chưa làm**. Hai màn đáng vẽ: *so chéo kỳ — "im lặng có chọn lọc"* và *kết luận pháp lý có điều khoản*. Dùng công cụ dựng giao diện (Claude, v0, Figma AI…) với prompt dưới, rồi **đóng dấu chéo góc** dòng chữ *"THIẾT KẾ ĐÍCH — CHƯA CÓ TRONG PROTOTYPE"* bằng PowerPoint. Không đóng dấu thì không dùng.

```text
Design one desktop web screen (1440x900) for an audit-support tool called GreenScan, in
Vietnamese, matching this style: off-white background #F7F7F4, navy #16283B text, deep
green #1F7A52 accents, amber #C8892B for "insufficient evidence", font Be Vietnam Pro,
dense but calm enterprise layout, left sidebar with three numbered steps
("1. Tải tài liệu", "2. Soát theo hàng đợi", "3. Sửa báo cáo (Studio)", "4. Giấy làm việc").
Screen: "So chéo kỳ" — a table comparing the same company's environmental indicators
across reporting years 2023, 2024, 2025 (rows: phát thải phạm vi 1, phạm vi 2, cường độ
phát thải, nước sử dụng, năng lượng tái tạo). One indicator reported in 2023 and 2024 is
missing in 2025; that cell is outlined in amber with the note "Năm trước có công bố, năm nay
không — cần soát". Each reported value has a small page-number link. No charts, no scores,
no company ranking, no word "vi phạm".
```
Ghi vào nhật ký AI (file 02 §4) như mọi ảnh sinh khác.

---

## 7. Lịch tập

| Ngày | Việc | Đạt khi |
| --- | --- | --- |
| 12/10 | Chạy demo §3 lần đầu, bấm giờ, sửa thứ tự bấm cho trơn | ≤ 3:00 |
| 15/10 | Ghi video §5 | hai tệp MP4 |
| 18/10 | Tập cả bài 10 phút, có người ngoài nhóm nghe | ≤ 10:00, người nghe kể lại được 3 điều §1 file 01 |
| 20/10 | Tập trên máy dự phòng, tắt mạng | chạy hết §3 |
| 22/10 | Tập hỏi đáp ngẫu nhiên (file 04) | mỗi người trả lời ≤ 60 giây |
| 24/10 | T-1 bảng kiểm §2.2; tạo lại phiên demo sạch | đủ 10 ô |
