# Kịch bản sinh ảnh cho slide Bán kết

**Ngày:** 09/10/2026 · **Dùng cùng:** [01_NOI_DUNG_TRINH_BAY.md](01_NOI_DUNG_TRINH_BAY.md) (mỗi slide ghi mã ảnh nó cần)
**Kế thừa:** [../SLIDES_11_16_IMAGE_PROMPTS.md](../SLIDES_11_16_IMAGE_PROMPTS.md) (24/09) — giữ bảng màu và quy trình, sửa nội dung cho đúng sản phẩm hôm nay.

---

## 0. Bốn quy tắc trước khi mở công cụ sinh ảnh

1. **Ảnh AI chỉ để minh hoạ ý, không bao giờ để "chụp" sản phẩm.** Màn hình GreenScan trên slide phải là **ảnh chụp thật** (`SHOT-xx`, file 03 §4). Thể lệ Điều 14 cấm *"cố ý làm sai lệch dữ liệu, kết quả đầu ra"*: một giao diện do AI vẽ đặt cạnh chữ "prototype" chính là làm sai lệch đầu ra.
2. **Không để AI viết chữ.** Mô hình sinh ảnh viết sai tiếng Việt, tự đổi số, bỏ mũi tên. Mọi prompt dưới đây yêu cầu *không có chữ*; chữ tiếng Việt đặt bằng PowerPoint/Canva sau.
3. **Hình có số, mũi tên, ngày tháng → vẽ vector** (`VEC-xx`, §3), không sinh ảnh.
4. **Ghi nhật ký mọi ảnh sinh ra** (§4). Thể lệ Điều 14: dùng AI hỗ trợ được phép *"nhưng phải được khai báo rõ trong tài liệu"*. Nhật ký là nguồn cho slide khai báo P1 và mục khai báo trong báo cáo giải pháp.

---

## 1. Hệ phong cách chung

### 1.1 Bảng màu (khớp sơ đồ pipeline và giao diện)

| Vai trò | Mã màu | Dùng cho |
| --- | --- | --- |
| Xanh chủ đạo | `#1F7A52` | điểm nhấn "có bằng chứng", dòng được tô |
| Xanh than | `#16283B` | đường nét, chữ tiêu đề |
| Nền | `#F7F7F4` | nền mọi slide |
| Hổ phách | `#C8892B` | "chưa đủ bằng chứng" / từ chối kết luận |
| Đỏ trầm | `#B42318` | "không so được" — dùng rất ít |
| Xám chữ phụ | `#6B7280` | nhãn nhỏ, nguồn |

### 1.2 Đuôi phong cách — dán vào cuối **mọi** prompt

```text
Style: flat vector editorial illustration, muted deep green #1F7A52 and navy #16283B
accents on an off-white #F7F7F4 background, thin even line weight, small corner radius,
very subtle shadow, generous negative space, calm and precise, enterprise audit-software
aesthetic, 16:9.
Absolutely no text, no letters, no numbers, no words, no logos, no watermarks.
Avoid: robots, glowing brains, circuit boards, neon, holograms, sci-fi glow, 3D render,
gradients, stock-photo people, recognizable faces, real company logos, national flags,
green leaves sprouting from factories, globe-in-hands clichés.
```

### 1.3 Giữ các ảnh cùng một "bộ"

- Sinh **IMG-01 trước**, chọn bản đẹp nhất, rồi đính kèm nó làm **ảnh tham chiếu phong cách** cho mọi ảnh sau (ChatGPT/Gemini: tải ảnh lên và viết *"match the visual style of the attached image exactly"*; Midjourney: `--sref <link ảnh IMG-01>`).
- Mỗi prompt sinh **4 phương án**, chọn 1, sinh lại tối đa 2 vòng. Quá 2 vòng chưa ưng → dùng VEC hoặc bỏ ảnh. Slide không có ảnh vẫn tốt hơn slide có ảnh sai.

### 1.4 Ghi chú theo công cụ

| Công cụ | Cách dùng prompt | Lưu ý |
| --- | --- | --- |
| ChatGPT (tạo ảnh) / Gemini | Dán nguyên prompt + đuôi §1.2; nếu ảnh vẫn có chữ, gửi tiếp *"remove all text and letters, keep everything else identical"* | Xuất PNG; kiểm tra kích thước ≥ 1920×1080 |
| Midjourney | Dán phần mô tả + đuôi; thêm `--ar 16:9 --style raw --no text, letters, words, logo, watermark` | Dùng `--sref` cho đồng bộ |
| Canva / PowerPoint Designer | Chỉ dùng để **đặt chữ và bố cục**, không sinh lại ảnh | Font: **Be Vietnam Pro** (dấu tiếng Việt đầy đủ); dự phòng Arial |

### 1.5 Kích thước theo vị trí trên slide

| Vị trí | Tỉ lệ | Ghi trong prompt |
| --- | --- | --- |
| Nền toàn slide, chừa chỗ chữ | 16:9 | "leave the left third empty for a title" |
| Ảnh nửa slide | 4:5 dọc | thay "16:9" ở đuôi bằng "4:5 portrait" |
| Ảnh nhỏ góc | 1:1 | thay bằng "1:1 square" |

---

## 2. Prompt từng ảnh

Mỗi mục: **slide** · **ý cần truyền đạt** · **prompt** · **chữ đặt sau bằng PowerPoint** · **kiểm tra trước khi dùng**.

### IMG-01 · Bìa (S1) — sinh đầu tiên, làm ảnh tham chiếu cho cả bộ

**Ý:** một dòng trong báo cáo dài được soi ra và gắn số trang.

```text
A single large page of a long corporate report, seen slightly from above at a gentle
angle, filled with many faint grey placeholder text lines. Exactly one line in the middle
of the page is highlighted with a solid deep green bar. A slim magnifying glass rests over
that highlighted line. From the highlighted line, one thin navy connector line runs to the
right edge and ends at a small page-marker tag shape and a small square with a checkmark.
Behind the page, a soft stack of more pages suggests hundreds of pages. Leave the left
third of the image completely empty for a title.
```
**Chữ đặt sau:** GreenScan AI · khẩu hiệu · tên đội.
**Kiểm tra:** chỉ một dòng được tô · không có chữ thật trên trang · nền trái đủ trống.

### IMG-02 · Một câu, bốn câu hỏi (S2)

**Ý:** một câu được tô, bốn câu hỏi toả ra.

```text
An open thick report book lying flat, pages fanned to show its thickness. On the right-hand
page, one sentence-shaped line is highlighted in deep green. Four thin navy leader lines
radiate from that highlighted line to four empty rounded rectangle label boxes placed
around the book: upper left, upper right, lower left, lower right. The four boxes are
empty outlines, evenly sized, with generous space inside for text to be added later.
```
**Chữ đặt sau:** câu "Năm 2025, chúng tôi đã giảm 30% phát thải." đặt **trên** ảnh (không đặt vào trang sách) · bốn ô: Chỉ số nào? · So với năm nào? · Phạm vi nào? · Bằng chứng ở trang nào?
**Kiểm tra:** bốn ô trống đều nhau, không có ký tự lạ bên trong.

### IMG-03 · Bàn làm việc của kiểm toán viên (S3, ảnh nhỏ góc 1:1)

**Ý:** việc tay, nhiều giấy, nhiều lần lật trang.

```text
Top-down flat illustration of an auditor's desk: two tall stacks of printed reports,
several pages with small sticky-note flags sticking out, a calculator, a ruler, a coffee
cup, and an open laptop showing an empty spreadsheet grid. One faceless hand is flipping a
page. Slightly cluttered to convey tedious manual cross-checking, but still tidy and
calm in tone. 1:1 square.
```
**Kiểm tra:** không có khuôn mặt · lưới bảng tính không có chữ/số.

### IMG-05 · Dữ liệu hoá bài toán (S5, ảnh nửa slide 4:5)

**Ý:** từ một câu đến một hàng đợi có thứ tự.

```text
A vertical flow illustration, top to bottom: a single sentence strip; below it, a small
form card with exactly five empty labelled-field slots; below that, three small document
cards each carrying a tiny page-marker tag; below that, a narrow gate shape with a check
slot; below that, a row of five small round status markers in green, light green, red,
grey and amber; at the bottom, a short ordered list of three highlighted rows with small
rank badges. Thin navy connectors between stages. 4:5 portrait.
```
**Chữ đặt sau:** (bên cạnh ảnh) tuyên bố · 5 thuộc tính · bằng chứng có trang · phép kiểm · 5 mức kết luận · hàng đợi soát.
**Kiểm tra:** đúng **5** ô trong thẻ và đúng **5** dấu trạng thái — đếm lại.

### IMG-07 · Cổng khả năng so sánh (S8, tuỳ chọn — ưu tiên VEC-04)

Dùng nguyên prompt *Slide 15* trong [../SLIDES_11_16_IMAGE_PROMPTS.md](../SLIDES_11_16_IMAGE_PROMPTS.md), **đổi** câu cuối thành:
```text
... the path splits into two: one continues down to a small calculator shape, the other
ends at a red-outlined closed barrier. Six small check slots in one row. No law book.
```
**Kiểm tra:** đúng **6** ô kiểm — sai số lượng thì bỏ, dùng VEC-04.

### IMG-08 · Biết từ chối · mô hình có chốt chặn (S9, nền 16:9)

**Ý:** trái — "chưa đủ bằng chứng" là một ngả đường riêng; phải — mô hình chỉ chỉ chỗ, người mới quyết.

```text
Two-part illustration on one wide canvas. Left half: a vertical path splits under a small
question-mark-free diamond node; the left branch leads to a row of four small round status
markers; the right branch leads to one larger amber-outlined marker standing apart, with
three small empty tag shapes hanging beneath it, suggesting missing pieces. Right half: a
small abstract reading device drawn as a document with a scanning line (not a robot, not
a brain) points a thin dashed arrow at a highlighted passage; between the device and a
large verdict stamp there is a simple closed gate bar; the dashed arrow instead continues
to a faceless person silhouette at a desk who holds the stamp. Calm, balanced.
```
**Chữ đặt sau:** trái — 5 mức kết luận, "chưa đủ bằng chứng + thiếu gì"; phải — "mô hình chỉ chỗ · người quyết", số 10 mâu thuẫn sai (đặt trong khung VEC nhỏ, không trên ảnh).
**Kiểm tra:** không có robot/bộ não · con dấu nằm ở **người**, không ở thiết bị.

### IMG-09 · Dữ liệu (S10, nền 16:9)

**Ý:** ba nguồn → ba tầng dữ liệu → hai người gán nhãn độc lập.

```text
Left: three separate incoming streams, each starting from a distinct source icon: a stack
of corporate report booklets; a closed law book with a small calendar badge on its cover;
a document folder with a small gavel icon. The three streams flow into three stacked
horizontal trays in the center, the top tray holding rough unsorted sheets, the middle
tray holding neatly aligned sheets, the bottom tray holding small structured cards.
Right: two faceless people at two separate small desks, each independently placing tag
marks on identical cards, with a simple semicircular gauge between them indicating
agreement. Thin navy connectors. Leave a band at the bottom empty for captions.
```
**Chữ đặt sau:** 1.061 tài liệu · 21 doanh nghiệp · 11 văn bản · 28 bộ án lệ · raw → clean → extract · "gán độc lập · đo κ".
**Kiểm tra:** hai người không nhìn vào bài của nhau (ý "độc lập").

### IMG-10 · Triển khai: ba chế độ (S12, ảnh dải trên 16:9)

**Ý:** dữ liệu ở đâu là quyết định của đơn vị dùng.

```text
Three equal side-by-side panels separated by thin vertical rules. Panel one: an ordinary
laptop with a closed padlock icon on its screen and a small cloud icon crossed out above
it. Panel two: the same laptop connected by one thin line to a small cloud that has a
map-pin marker on it; only two tiny paper snippets travel along the line. Panel three: a
compact server rack with one visible accelerator card, standing inside a simple building
outline with a closed door. Under each panel, an empty rounded label box.
```
**Chữ đặt sau:** Ngoại tuyến (mặc định) · Đám mây Việt Nam · Máy chủ của đơn vị; bảng số liệu S12 đặt **dưới** ảnh bằng PowerPoint.
**Kiểm tra:** panel 2 chỉ có **mẩu nhỏ** đi lên mây (không phải cả tập tài liệu).

### IMG-12 · Quantum: chọn tập bằng chứng (S13, ảnh nhỏ 1:1)

**Ý:** chọn một tập con tối ưu trong nhiều đoạn bằng chứng — tối ưu tổ hợp, không phải phép màu.

```text
About twelve small document-card nodes arranged loosely in a circle, connected by thin
grey lines forming a network. Exactly four of the cards are highlighted in deep green and
connected by slightly thicker green lines, forming the chosen subset. In the faint
background, a sparse regular lattice of small hollow circles hints at qubits. Restrained,
no glow, no sparkles. 1:1 square.
```
**Kiểm tra:** đúng 4 thẻ được chọn · không hiệu ứng phát sáng.

### IMG-13 · Kết (S14)

Sinh lại IMG-01 với thay đổi:
```text
Same scene as the reference image, but closer: the highlighted line and its page-marker
tag fill the right half; four small empty rounded tags line up vertically to the right of
the page-marker. Left half empty for text.
```
**Chữ đặt sau:** bốn câu hỏi của S14.

---

## 3. Hình vẽ tay (VEC) — không sinh bằng AI

| Mã | Slide | Dựng bằng | Đặc tả |
| --- | --- | --- | --- |
| **VEC-01** | S7 | `python tools/make_pipeline_diagram.py` (sửa mã, dựng lại SVG/PNG) | Sơ đồ hiện có **mô tả sai hai chỗ** so với sản phẩm 09/10: (1) badge *Lọc tuyên bố*, *Cấu trúc hoá*, *Tìm bằng chứng* đang ghi **MÔ HÌNH** nhưng cả ba chạy bằng **luật / truy xuất từ khoá** → đổi badge thành **LUẬT**, thêm nhãn nét đứt nhỏ *"mô hình: bước kế tiếp"*; chú thích ký hiệu "MÔ HÌNH — học từ dữ liệu" giữ cho phần nét đứt; (2) thiếu **HÀNG ĐỢI SOÁT** — thêm khối giữa *Cổng kiểm soát* và *Hồ sơ kiểm chứng*: "xếp thứ tự theo trọng yếu · nghĩa vụ · khoảng trống bằng chứng — 156 → 9". Khối *Kết luận*: thêm badge nhỏ "LUẬT (+ mô hình đọc cặp khó, có chốt chặn)". Đổi "Hồ sơ kiểm chứng" thành **"Giấy làm việc"**. |
| **VEC-02** | S3 | PowerPoint (hình khối + mũi tên) | 8 ô một hàng, đánh số; ô 2, 3, 6 nền `#1F7A52` chữ trắng; ô 7, 8 viền `#16283B` đậm; hai ghi chú dưới: "GreenScan làm" (ngoặc dưới 2, 3, 6) · "luôn là của con người" (ngoặc dưới 7, 8) |
| **VEC-03** | S4 | PowerPoint | Trục ngang 10/2024 → 2027; 4–5 mốc chấm tròn; mỗi mốc: ngày (đậm) · văn bản · một dòng hệ quả. Mốc ⚠️ chưa xác minh bản gốc thì **không vẽ** |
| **VEC-04** | S8 | Cắt khối "Cổng khả năng so sánh" từ VEC-01 (bản SVG, phóng to) | Thay hai thẻ số mẫu "giảm 30%" / "1,2 triệu tCO₂e" bằng "hơn **99%** tổng phát thải (tỷ trọng)" / "sản lượng thép thô tăng **24%** (mức thay đổi)"; tô đỏ ô *loại giá trị* → ngả **KHÔNG SO ĐƯỢC** |

---

## 4. Nhật ký sinh ảnh (bắt buộc — nguồn cho khai báo Điều 14)

Tạo bảng tính `docs/07-presentation/ban-ket-2026-10-25/nhat_ky_AI.xlsx` (hoặc thêm vào cuối file này) với các cột:

| Mã ảnh | Slide | Công cụ (tên + phiên bản nếu biết) | Ngày | Người sinh | Prompt (mã mục ở file này + chỉnh sửa thêm) | Số vòng sinh | Chỉnh sửa của người (cắt, đặt chữ, đổi màu, ghép) | Tệp cuối |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMG-01 | S1 | | | | §2 IMG-01 | | | `img/IMG-01_final.png` |

Tệp ảnh cuối lưu trong `docs/07-presentation/ban-ket-2026-10-25/img/` (thư mục này đã được gitignore cho `*.png`, xem README §5).

---

## 5. Bảng kiểm trước khi chèn ảnh vào slide

| # | Kiểm | |
| --- | --- | --- |
| 1 | Không có chữ/số do AI viết trên ảnh (phóng to 200% để soát) | ☐ |
| 2 | Không có logo thật, khuôn mặt nhận diện được, cờ quốc gia | ☐ |
| 3 | Không có ảnh nào giả làm màn hình GreenScan | ☐ |
| 4 | Số lượng chi tiết đúng: 5 ô (IMG-05), 6 ô kiểm (IMG-07), 4 thẻ chọn (IMG-12) | ☐ |
| 5 | Cùng bảng màu, cùng nét vẽ với IMG-01 | ☐ |
| 6 | Đã ghi nhật ký §4 | ☐ |
| 7 | Slide P1 (khai báo AI) liệt kê ảnh này | ☐ |
