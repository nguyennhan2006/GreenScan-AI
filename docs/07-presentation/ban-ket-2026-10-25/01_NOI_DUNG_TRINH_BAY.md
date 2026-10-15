# Nội dung trình bày Bán kết — từng slide, lời nói, thời lượng

**Ngày:** 09/10/2026 · **Thuyết trình:** Chủ nhật 25/10/2026 · **Người dùng tài liệu:** Quỳnh, Thảo, Nhân
**Thay thế:** bộ slide `GREENSCAN.zip` (26/09) và kịch bản 7 phút ở `EXECUTION_PLAN_2026-09.md` §4 (18/09) — cả hai mô tả những thứ sản phẩm chưa làm (chuẩn hoá bằng mô hình, BGE-M3, ô bảng, panel pháp lý có kết luận).
**Đi kèm:** ảnh → [02_KICH_BAN_SINH_ANH.md](02_KICH_BAN_SINH_ANH.md) · demo và ảnh chụp sản phẩm → [03_KICH_BAN_PROTOTYPE_DEMO.md](03_KICH_BAN_PROTOTYPE_DEMO.md) · hỏi đáp → [04_HOI_DAP_BO_SUNG.md](04_HOI_DAP_BO_SUNG.md)

Mọi con số dưới đây đã được đo lại hoặc đếm lại trên kho mã ngày 09/10/2026; nguồn của từng số ở §4. Số nào không có trong §4 thì **không được đưa lên slide**.

---

## 0. Ba thay đổi so với bộ slide 26/09 — và vì sao

| # | Bộ 26/09 | Bộ này | Vì sao |
| --- | --- | --- | --- |
| 1 | "Hệ thống **chấm điểm rủi ro tẩy xanh** và **tự động tư vấn** cải thiện báo cáo" | **Trợ lý cho kiểm toán viên**: đọc báo cáo, đưa ra *hàng đợi soát* có bằng chứng tới trang, và *giấy làm việc* | Trên Hòa Phát, 154/156 tuyên bố cùng mức MEDIUM — một "điểm rủi ro" không giúp ai quyết định xem gì trước ([định vị 25/09](../../02-product/AUDITOR_WORKFLOW_POSITIONING.md)). Cam kết vòng 1: không xếp hạng doanh nghiệp, không dùng chữ "vi phạm" |
| 2 | Không có slide demo, dữ liệu, triển khai | Có — ba tiêu chí này chiếm **50%** điểm vòng 2 (prototype 20%, dữ liệu 15%, triển khai 15%) | Thể lệ Điều 11.2 |
| 3 | Vẽ "Claim normalization", "Evidence retrieval" như đang chạy bằng mô hình | Chỉ nói thứ đang chạy: trích tuyên bố và 5 thuộc tính **bằng luật**; tìm bằng chứng bằng **BM25 + n-gram ký tự**; mô hình ngôn ngữ **chỉ đọc cặp khó, có chốt chặn** | Thể lệ Điều 14 cấm làm sai lệch kết quả; BGK kỹ thuật sẽ hỏi "cho xem mô hình chuẩn hoá" |

**Tên đề tài trên bìa:** giữ tên đã đăng ký ở vòng 1 bằng chữ nhỏ (để khớp hồ sơ), dùng *khẩu hiệu mới* bằng chữ lớn. Phần "tư vấn cải thiện" của tên cũ ứng với một thứ **có thật**: với mỗi tuyên bố, hệ thống liệt kê *thông tin còn thiếu* (số liệu, kỳ, năm gốc, phạm vi, nguồn độc lập) — chính là danh sách doanh nghiệp cần bổ sung khi công bố. Nói đúng như vậy nếu BGK hỏi.

---

## 1. Thông điệp

**Một câu (nói ở slide 1 và slide cuối):**
> GreenScan đọc báo cáo bền vững vài trăm trang thay kiểm toán viên, chỉ ra những chỗ nên soát trước kèm bằng chứng tới từng trang, và chỉ kết luận khi chỉ ra được phép tính và quy tắc đã dùng.

**Ba điều BGK phải nhớ khi ra khỏi phòng:**
1. *Hai con số khác nhau chưa phải là mâu thuẫn* — hệ thống kiểm sáu điều kiện trước khi được phép so.
2. *"Chưa đủ bằng chứng" là một kết quả hợp lệ* — và mô hình ngôn ngữ không được tự kết luận.
3. *Chạy trên laptop không GPU, tài liệu không rời máy* — 264 trang trong khoảng 2 phút.

---

## 2. Bản đồ: tiêu chí chấm → slide → thời gian (bản 10 phút)

Thể lệ **không ghi thời lượng vòng 2** (vòng 3 là 10 phút + 8 phút hỏi đáp). Bản chính dựng cho **10 phút**; bản cắt 7 phút ở §5. Hỏi BTC thời lượng chính thức trước 15/10 (xem [README](README.md) §3).

| Slide | Nội dung | Tiêu chí vòng 2 (trọng số) | Thời lượng | Người nói |
| --- | --- | --- | --- | --- |
| S1 | Bìa | — | 0:10 | Quỳnh |
| S2 | Một câu, bốn câu hỏi | 1 · Bài toán (20%) | 0:30 | Quỳnh |
| S3 | Kiểm toán viên đang làm bằng tay | 1 · Bài toán | 0:40 | Quỳnh |
| S4 | Vì sao bây giờ | 1 · Bài toán; 5 · Triển khai | 0:40 | Thảo |
| S5 | Dữ liệu hoá bài toán + 4 ràng buộc | 1 · Bài toán; 3 · Giải pháp | 0:35 | Quỳnh |
| S6 | **DEMO** | 4 · Prototype (20%) | 2:40 | Nhân (bấm + nói) |
| S7 | Kiến trúc: mô hình đọc, luật quyết định | 3 · Giải pháp (20%) | 0:35 | Nhân |
| S8 | Cổng khả năng so sánh | 3 · Giải pháp | 0:45 | Nhân |
| S9 | Biết từ chối; mô hình có chốt chặn | 3 · Giải pháp | 0:35 | Nhân |
| S10 | Dữ liệu | 2 · Dữ liệu (15%) | 0:45 | Thảo |
| S11 | Đã đạt · Mục tiêu · Giả thuyết | 4 · Prototype; 6 · Trình bày | 0:40 | Quỳnh |
| S12 | Triển khai: chạy ở đâu, tốn bao nhiêu, dữ liệu đi đâu | 5 · Triển khai (15%) | 0:45 | Thảo |
| S13 | Quantum: nghiên cứu, chưa vào sản phẩm | 3 · Giải pháp (giải phụ Lượng tử) | 0:15 | Nhân |
| S14 | Kết | 6 · Trình bày (10%) | 0:15 | Quỳnh |
| | **Tổng** | | **9:50** (dư 10 giây) | |

Demo đặt **ngay sau phần bài toán**: BGK thấy sản phẩm chạy trước, rồi mới nghe vì sao nó đáng tin. Phụ lục P1–P8 (§3, cuối) không trình chiếu — để mở khi bị hỏi.

---

## 3. Từng slide

Quy ước cột **Hình**: `IMG-xx` = ảnh minh hoạ sinh bằng AI (prompt ở file 02) · `SHOT-xx` = ảnh chụp sản phẩm thật (file 03 §4) · `VEC-xx` = hình vẽ vector/PowerPoint (không dùng AI vì có chữ và số phải chính xác).

### S1 · Bìa — 0:10 · Quỳnh

- **Chữ lớn:** GreenScan AI
- **Khẩu hiệu:** Từ báo cáo bền vững vài trăm trang đến hàng đợi soát có bằng chứng tới từng trang
- **Chữ nhỏ:** Đề tài đăng ký: *Hệ thống chấm điểm rủi ro "tẩy xanh" và tự động tư vấn cải thiện báo cáo ESG, BCTC cho doanh nghiệp niêm yết* · Eco Nexus · AQ2026-119 · Lê Diễm Quỳnh (HVTC) · Phan Thanh Thảo (HVTC) · Nguyễn Chơn Nhân (UIT – ĐHQG TP.HCM)
- **Hình:** IMG-01
- **Lời:** "Chúng em là Eco Nexus. GreenScan giúp kiểm toán viên soát các tuyên bố môi trường trong báo cáo của doanh nghiệp niêm yết — nhanh hơn, và có bằng chứng tới từng trang."

### S2 · Một câu, bốn câu hỏi — 0:30 · Quỳnh

- **Tiêu đề:** Một câu trong báo cáo — bốn câu hỏi kiểm toán
- **Trên slide:** câu lớn ở giữa *"Năm 2025, chúng tôi đã giảm 30% phát thải."* — bốn thẻ quanh: **Chỉ số nào?** · **So với năm nào?** · **Phạm vi nào?** · **Bằng chứng ở trang nào?**
- **Hình:** IMG-02 làm nền; bốn thẻ chữ đặt bằng PowerPoint
- **Lời:**
  > "Một báo cáo phát triển bền vững dài hàng trăm trang. Nhưng một quyết định cho vay hay đầu tư có thể dựa vào đúng một câu như thế này. Câu hỏi không phải là câu này nghe có xanh không. Câu hỏi là: ba mươi phần trăm của chỉ số nào, so với năm nào, cho phạm vi nào — và bằng chứng nằm ở trang nào. Hôm nay, trả lời bốn câu đó cho từng tuyên bố là việc làm bằng tay."
- **BGK hỏi:** *"Câu này của doanh nghiệp nào?"* → "Câu minh hoạ do nhóm viết. Chúng em không đặt tên một doanh nghiệp cạnh một câu hỏi nghi vấn."

### S3 · Kiểm toán viên đang làm việc này bằng tay — 0:40 · Quỳnh

- **Tiêu đề:** Ba việc tốn thời gian nhất đều là việc cơ học
- **Trên slide:** một hàng 8 bước, tô đậm 3 bước và ghi chú hai đầu:
  1 Nhận bộ tài liệu → **2 Đọc dò tìm tuyên bố** → **3 Lật tìm số liệu đối chiếu** → 4 Kiểm số, năm gốc, phạm vi → 5 Tra văn bản áp dụng → **6 Ghi giấy làm việc** → 7 Xét đoán trọng yếu → 8 Kết luận, ký
  Dưới bước 2, 3, 6: *"GreenScan làm"* · dưới bước 7, 8: *"luôn là của con người"*
- **Hình:** VEC-02 (hàng bước) + IMG-03 nhỏ ở góc (bàn làm việc ngập giấy)
- **Lời:**
  > "Người dùng của chúng em là kiểm toán viên và chuyên viên đảm bảo. Quy trình của họ hôm nay có tám bước. Ba bước tốn thời gian nhất — đọc dò tìm câu tuyên bố, lật tìm bảng số liệu để đối chiếu, và gõ lại vào giấy làm việc — đều là việc cơ học. GreenScan làm ba việc đó. Hai bước cuối — xét đoán chỗ nào trọng yếu và ký kết luận — luôn là của con người."
- **BGK hỏi:** *"Tiết kiệm được bao nhiêu giờ?"* → "Chúng em chưa đo nên chưa nói con số. Có sẵn giao thức đo: 20 tuyên bố, một người làm tay, một người làm với GreenScan, đo thời gian và số bằng chứng tìm đúng. Con số '8–12 giờ' trong hồ sơ vòng 1 là giả thuyết, không phải kết quả."

### S4 · Vì sao bây giờ — 0:40 · Thảo

- **Tiêu đề:** Nghĩa vụ công bố tăng nhanh hơn năng lực kiểm tra
- **Cột trái — chất lượng công bố hôm nay** (ghi nguồn chữ nhỏ dưới mỗi số):
  - **28,38%** công ty trên HOSE có báo cáo phát triển bền vững (2024) — Hąbek & Bui, 2025
  - **72,5%** báo cáo bền vững chỉ có thông tin định tính — như trên
  - **2/22** báo cáo độc lập có bên thứ ba đảm bảo — như trên
  - **50,6%** quan sát công bố khí nhà kính đạt 0 điểm — Lâm Thị Trúc Linh và cs., 2025
- **Cột phải — dòng thời gian nghĩa vụ:**
  - 01/10/2024 · QĐ 13/2024/QĐ-TTg — **2.166 cơ sở** phải kiểm kê khí nhà kính
  - 01/08/2025 · NĐ 119/2025/NĐ-CP — thép, xi măng, nhiệt điện: kiểm kê **có thẩm định độc lập**, nộp từ 2027
  - 01/01/2026 · EU CBAM áp dụng chính thức — thép, xi măng
  - 2026 · Hạn ngạch phát thải thí điểm cho **110 cơ sở** thép, xi măng, nhiệt điện (QĐ 263/QĐ-TTg) ⚠️
- **Hình:** VEC-03 (dòng thời gian, dựng bằng PowerPoint — không sinh ảnh vì toàn chữ và ngày tháng)
- **Lời:**
  > "Hai cột này là bài toán. Bên trái là chất lượng công bố hôm nay: chỉ 28% công ty trên HOSE có báo cáo bền vững, gần ba phần tư số đó chỉ có thông tin định tính, và chỉ 2 trên 22 báo cáo có bên thứ ba đảm bảo. Bên phải là nghĩa vụ đang đến: hơn hai nghìn cơ sở phải kiểm kê khí nhà kính; thép, xi măng, nhiệt điện phải có thẩm định độc lập; và CBAM của châu Âu. Khi con số phát thải gắn với tiền, ai đó phải kiểm từng con số — và không đủ người để đọc tay."
- ⚠️ **QĐ 263/2026 và ngày khai trương sàn các-bon HNX mới có nguồn thứ cấp.** Thảo đọc bản gốc trước 17/10; chưa đọc được thì **bỏ dòng đó khỏi slide** (giữ trong phụ lục).
- **BGK hỏi:** *"Ngân hàng có phải công bố khí nhà kính không?"* → "Không. Thông tư 96 miễn mục 6.1–6.3 cho tài chính, ngân hàng, chứng khoán, bảo hiểm — nhưng vẫn phải công bố nước và số lần bị xử phạt môi trường. Quy tắc mục 6 chúng em đang viết sẽ miễn đúng phần đó; với ngân hàng, thứ đáng kiểm là tính nhất quán của số dư tín dụng xanh qua các năm."

### S5 · Dữ liệu hoá bài toán — 0:35 · Quỳnh

- **Tiêu đề:** Biến "đọc và xét" thành bài toán máy kiểm được
- **Trên slide — luồng một hàng:** tuyên bố → **5 thuộc tính** → bằng chứng có trang → phép kiểm → **5 mức kết luận** → hàng đợi soát
  - Dưới "5 thuộc tính", ghi theo từ vựng kiểm toán: chỉ số (*phân loại*) · giá trị + đơn vị (*chính xác*) · kỳ (*đúng kỳ*) · năm gốc (*so sánh*) · phạm vi (*đầy đủ*)
- **Khung "4 ràng buộc quyết định thiết kế":**
  1. Tài liệu của doanh nghiệp **không tự chứng minh** cho chính nó
  2. Hai con số khác nhau **chưa phải** mâu thuẫn
  3. Không tìm thấy bằng chứng **không có nghĩa** tuyên bố sai
  4. Phần mềm **không kết luận** vi phạm — người có thẩm quyền mới kết luận
- **Hình:** IMG-05 (nhỏ, bên phải) hoặc chỉ dùng luồng chữ
- **Lời:**
  > "Để máy làm được, chúng em dữ liệu hoá bài toán: mỗi tuyên bố được tách thành năm thuộc tính — chính là năm cơ sở dẫn liệu kiểm toán viên vẫn dùng. Sau đó tìm bằng chứng có số trang, chạy phép kiểm, và đưa ra một trong năm mức kết luận. Bốn ràng buộc bên dưới quyết định toàn bộ thiết kế phía sau — và em sẽ quay lại từng cái trong demo."
- **BGK hỏi:** *"Năm thuộc tính do mô hình AI trích?"* → "Hiện bằng luật và từ điển, chưa dùng mô hình — để mỗi thuộc tính truy được về đúng chữ trong câu. Trích bằng mô hình là bước tiếp theo, chỉ bật khi đo được nó tốt hơn."

### S6 · DEMO — 2:40 · Nhân bấm và nói

- **Slide chuyển cảnh (3 giây):** *Demo — báo cáo phát triển bền vững 2025 + báo cáo thường niên 2024 của Tập đoàn Hòa Phát (tài liệu công khai) · 264 trang · laptop không GPU, không mạng*
- **Kịch bản bấm từng bước, lời nói và phương án dự phòng:** [03 §3](03_KICH_BAN_PROTOTYPE_DEMO.md#3-kịch-bản-demo-trực-tiếp--240). Tóm tắt:

| Thời điểm | Màn hình | Điều BGK phải thấy |
| --- | --- | --- |
| 0:00–0:15 | Lịch sử → phiên *"DEMO Bán kết — Hòa Phát…"* | Phân tích thật đã chạy trên máy này; chip **"Ngoại tuyến — không gửi tài liệu ra ngoài"** |
| 0:15–0:50 | **Soát theo hàng đợi** | 156 tuyên bố → **9 mục nên soát trước**, mỗi mục có lý do; dòng "163 mục không soát trong lượt này và vì sao" |
| 0:50–1:35 | Mục #2 — "mức độ tự chủ điện năng **rất cao**" (trang 7) | Tuyên bố không có số; hệ thống tìm sang **BCTN 2024 trang 86**: "tự chủ 90%… 788 triệu kWh" → **khớp một phần**, thiếu: số liệu, kỳ, năm gốc. Bấm bằng chứng → PDF mở đúng trang, tô sáng |
| 1:35–2:00 | Số liệu công bố → bảng khí nhà kính trang 39 | **22.540.603 + 933.876 = 23.474.479**, công bố 23.474.480 → **khớp (làm tròn 1 tCO2e)** — phép tính hiện ra, không phải mô hình đoán |
| 2:00–2:20 | Ghi quyết định người soát | Kiểm toán viên chọn kết luận + lý do; hàng đợi cập nhật; quyết định được lưu kèm tên người soát |
| 2:20–2:40 | **Giấy làm việc** → In / lưu PDF | Phạm vi tài liệu kèm mã băm, thủ tục đã chạy, **"những gì không kiểm và vì sao"**, chỗ ký |

- **Không mở trong demo:** mục #1 của hàng đợi (chữ gãy dòng "HÒA PHÁT trò nền tảng…" — lỗi trích đã biết); danh sách *Tất cả tuyên bố* lọc "ủng hộ" (1 trong 2 là chữ dính cột, xem P2).

### S7 · Kiến trúc — 0:35 · Nhân

- **Tiêu đề:** Mô hình đọc · Luật quyết định · Người ký
- **Hình:** VEC-01 — sơ đồ `diagrams/pipeline_16x9_vi.png` **sau khi sửa** (xem [README](README.md) §2, việc V3): badge của *Lọc tuyên bố*, *Cấu trúc hoá*, *Tìm bằng chứng* đổi thành **LUẬT** (thêm nhãn nhỏ nét đứt *"mô hình: bước kế tiếp"*), thêm khối **HÀNG ĐỢI SOÁT** trước *Hồ sơ kiểm chứng*.
- **Lời:**
  > "Ba loại đầu vào đi ba đường khác nhau: báo cáo doanh nghiệp, bằng chứng độc lập, và văn bản pháp luật kèm ngày hiệu lực. Đường kẻ ngang này là ranh giới quan trọng nhất: bên dưới nó không có mô hình nào. So số, đối chiếu luật, kết luận đều do mã tất định làm, nên mỗi kết luận chỉ ra được phép tính nào đã chạy. Hôm nay, kể cả phần đọc phía trên cũng chạy bằng luật trên CPU; mô hình ngôn ngữ chỉ được gọi cho những cặp mà luật không quyết được — em sẽ nói ở slide sau vì sao chúng em khoá nó lại."
- **BGK hỏi:** *"Vậy AI nằm ở đâu?"* → "Ở ba chỗ: xử lý ngôn ngữ tự nhiên tiếng Việt có dấu để trích tuyên bố và thuộc tính; truy xuất thông tin lai (BM25 + n-gram ký tự, hợp nhất RRF) — thuộc nhóm kỹ thuật RAG trong thể lệ; và mô hình ngôn ngữ lớn GLM-5.2 cho cặp khó. Chúng em chọn kỹ thuật đơn giản nhất mà đo được là đúng — thể lệ Điều 10 cũng chấm như vậy."

### S8 · Cổng khả năng so sánh — 0:45 · Nhân

- **Tiêu đề:** Hai con số khác nhau chưa phải là mâu thuẫn
- **Trên slide:**
  - Ví dụ lấy từ chính báo cáo đã demo: *"gang thép chiếm hơn **99%** tổng phát thải"* và *"sản lượng thép thô tăng **24%**"* → tỷ trọng ≠ mức thay đổi → **không được so**
  - Sáu điều kiện: loại giá trị · ranh giới tổ chức · công nghệ · chỉ số con · phạm vi phát thải (Scope) · mục tiêu hay thực hiện
  - Dung sai theo độ chính xác công bố: "12%" → 11,5–12,5 · "12,0%" → 11,95–12,05
  - % giảm được **tính lại** từ số kỳ gốc và kỳ báo cáo
  - **Kết quả:** cùng hai tài liệu này, 17/09: **357/419** tuyên bố bị đánh "mâu thuẫn" (phần lớn sai) → nay **0**; lỗi cũ thành **47 bẫy kiểm thử** chạy mỗi lần sửa mã
- **Hình:** VEC-04 (cắt khối "Cổng khả năng so sánh" từ VEC-01, phóng to) — hoặc IMG-07 nếu muốn nhẹ hơn
- **Lời:**
  > "Đây là điểm khác biệt kỹ thuật lớn nhất. Trong báo cáo vừa demo có hai câu: gang thép chiếm hơn 99% phát thải, và sản lượng thép thô tăng 24%. Một hệ thống ngây thơ thấy 99 khác 24 và báo mâu thuẫn. Hệ thống của chúng em từng mắc đúng lỗi đó: ngày 17/9, 357 trên 419 tuyên bố bị đánh mâu thuẫn, phần lớn sai. Nay mỗi con số mang theo sáu điều kiện, và hai con số chỉ được đem so khi không điều kiện nào lệch. Dung sai không phải một hằng số: viết 12% thì hiểu là 11,5 đến 12,5; viết 12,0% thì chỉ 11,95 đến 12,05. Mỗi lỗi từng gặp được biến thành một bẫy kiểm thử — hiện có 47 bẫy, chạy lại mỗi lần sửa mã."
- **BGK hỏi:** *"0 mâu thuẫn — có phải hệ thống không bắt được gì?"* → "0 là bằng chứng hết mâu thuẫn **sai**, không phải thành tích độ chính xác. Khả năng bắt mâu thuẫn **thật** được kiểm trên 4 ca có phán quyết — ví dụ KLM bị toà Hà Lan kết luận 15/19 tuyên bố gây hiểu nhầm, hệ thống ra 'bị bác bỏ' và giữ nguyên trích dẫn — và trên bẫy kiểm thử có mâu thuẫn số cố ý. Đo tỷ lệ bắt được trên dữ liệu Việt Nam cần bộ gán nhãn đang làm."

### S9 · Biết từ chối · Mô hình có chốt chặn — 0:35 · Nhân

- **Tiêu đề:** "Chưa đủ bằng chứng" là một kết quả — và mô hình không được tự kết luận
- **Trái:** 5 mức — khớp · khớp một phần · bị bác bỏ · không được chứng minh · **chưa đủ bằng chứng**. "Không được chứng minh" chỉ khi kho tài liệu *lẽ ra phải có* bằng chứng; còn lại là "chưa đủ bằng chứng" **kèm danh sách thiếu gì**.
- **Phải — một thí nghiệm có đối chứng (28/09):** cho mô hình GLM-5.2 tự quyết trên chính báo cáo Hòa Phát → **10** tuyên bố "mâu thuẫn" + **2** "nghiêm trọng", phần lớn sai (một dòng bảng vỡ bị đọc thành "100% nam giới"). → Chốt chặn: mô hình chỉ **chỉ chỗ cho người xem**, không đổi kết luận. 4–6 giây/lời gọi; chạy lại cùng tài liệu **0 lời gọi** (bộ nhớ đệm).
- **Hình:** IMG-08
- **Lời:**
  > "Kết quả hay gặp nhất trên dữ liệu thật là 'chưa đủ bằng chứng' — đúng với thực trạng: ba phần tư báo cáo chỉ có định tính. Hệ thống chỉ được nói 'không được chứng minh' khi biết chắc kho tài liệu lẽ ra phải có bằng chứng; còn lại thì từ chối kết luận và nói rõ thiếu gì. Mô hình ngôn ngữ cũng bị giới hạn như vậy, và lý do là một thí nghiệm: khi cho mô hình tự quyết, nó tạo ra 10 mâu thuẫn trên một doanh nghiệp mà chúng em dùng làm đối chứng, phần lớn sai. Nên mô hình chỉ được chỉ chỗ cho người xem — chỉ tháo chốt khi bộ gán nhãn đo được nó đúng."

### S10 · Dữ liệu — 0:45 · Thảo

- **Tiêu đề:** Dữ liệu thật, có nguồn, có giấy phép, có quy trình gán nhãn
- **Bốn khối:**
  1. **Báo cáo doanh nghiệp Việt Nam:** 1.061 tài liệu được lập chỉ mục từ **21 doanh nghiệp** niêm yết; **670** có bản gốc kèm mã băm SHA-256. Nguồn công khai (TT 96 bắt buộc công bố). **Không phân phối lại PDF** — repo chỉ lưu siêu dữ liệu và mã băm.
  2. **Văn bản pháp luật:** registry **11 văn bản**, ngày hiệu lực đối chiếu với bản ký; chuỗi sửa đổi chỉ kéo văn bản sửa đúng vấn đề đang xét.
  3. **Ca có phán quyết:** **28** bộ hồ sơ án lệ quốc tế (176 tài liệu); **4 ca** làm kiểm thử hồi quy — KLM, BNY Mellon, DWS, Keurig Dr Pepper → **khớp 4/4**.
  4. **Bộ gán nhãn tiếng Việt (gold):** quy ước gán nhãn thành văn bản; **88 cặp** tuyên bố–bằng chứng đã lấy mẫu từ doanh nghiệp phát thải cao; lô 1 (20 cặp) **hai người gán độc lập** để đo đồng thuận κ; chia tập **theo doanh nghiệp** (không rò rỉ); ngưỡng đánh giá **đăng ký trước** khi có nhãn. Trạng thái: *đã gán [n] cặp, κ = [ ]* ⚠️
  - Dải dưới: ba tầng dữ liệu **raw → clean → extract**, mỗi bản ghi giữ nguồn, ngày truy cập, mã băm.
- **Hình:** IMG-09
- **Lời:**
  > "Dữ liệu có bốn phần. Báo cáo thật của 21 doanh nghiệp niêm yết, hơn một nghìn tài liệu, mỗi bản gốc có mã băm — và chúng em không phát tán lại bản PDF của bên thứ ba. Văn bản pháp luật với ngày hiệu lực đối chiếu bản ký — chúng em đã tự phát hiện và sửa ba ngày hiệu lực sai. Hai mươi tám bộ án lệ quốc tế, bốn ca dùng làm kiểm thử, khớp cả bốn. Và bộ gán nhãn tiếng Việt: hai người gán độc lập, đo đồng thuận, chia theo doanh nghiệp, và ngưỡng đánh giá được ghi ra trước khi thấy kết quả — để không ai chỉnh ngưỡng cho đẹp."
- ⚠️ **Dòng trạng thái gold** điền số thật ngày 17/10 (slide đóng băng số liệu). Nếu n < 20 hoặc chưa có κ: nói thẳng *"đang gán, chưa đủ để báo độ chính xác"* — không bỏ trống, không ước lượng.

### S11 · Đã đạt · Mục tiêu · Giả thuyết — 0:40 · Quỳnh

- **Tiêu đề:** Chúng em tách rõ điều đã đo, điều đang đo và điều chưa đo
- **Ba cột:**

| Đã đạt — có hiện vật kiểm lại được | Mục tiêu — đang đo | Giả thuyết — chưa tuyên bố |
| --- | --- | --- |
| 264 trang trong **~2 phút**, RAM đỉnh **1,3 GB**, laptop không GPU, không khoá API | Gold ≥ 60 cặp, đồng thuận κ ≥ 0,7 | Thời gian soát giảm bao nhiêu |
| **0** mâu thuẫn sai trên Hòa Phát (17/09: 357/419) | Độ chính xác kết luận theo từng lớp, khoảng tin cậy theo doanh nghiệp | Truy xuất ngữ nghĩa (embedding, reranker) tăng độ phủ |
| **4/4** ca có phán quyết quốc tế khớp | Recall của bộ trích tuyên bố | Chọn bằng chứng bằng QUBO tốt hơn thuật toán tham lam |
| **359** kiểm thử tự động (47 bẫy kết luận, 17 ca checklist kiểm toán, 15 bất biến kiến trúc) | Thứ tự hàng đợi được kiểm toán viên đồng ý | |
| Hàng đợi **156 → 9** mục, mỗi mục có lý do; mọi bằng chứng có trang | | |
| Mỗi phiên có biên bản tái lập: mã băm đầu vào, cấu hình, phiên bản bộ quy tắc | | |

- **Lời:**
  > "Chúng em chia kết quả làm ba cột và chỉ cột đầu là thứ chúng em khẳng định. Cột giữa là thứ đang đo — và chúng em đã đăng ký ngưỡng trước khi có số. Cột cuối là giả thuyết: chúng em có lý do để tin, nhưng chưa đo, nên không nói thành kết quả."
- **Thời gian "~2 phút":** đo lại trên **chính máy trình chiếu** trước 17/10 (file 03 §2). Số chuẩn hiện có: 107–121 giây, 3 lần chạy ngày 06/10 trên i7-1355U.

### S12 · Triển khai — 0:45 · Thảo

- **Tiêu đề:** Chạy ở đâu, tốn bao nhiêu, dữ liệu đi đâu
- **Bảng ba chế độ** (chọn bằng một biến `QUANTUM_PROFILE`):

| | Ngoại tuyến (mặc định) | Đám mây Việt Nam | Máy chủ GPU |
| --- | --- | --- | --- |
| Máy | Mọi laptop 8–16 GB | Laptop + khoá FPT AI | 1 GPU 24 GB |
| Đo được | 264 trang ~2 phút, 1,3 GB | chạy đầu 632 s, chạy lại 188 s | chưa đo |
| Chi phí mỗi bộ hồ sơ | **0 đồng** | ước tính US$0,8–2,0 | điện / thuê máy |
| Tài liệu rời máy? | **Không** | Có — chỉ đoạn của cặp khó | Không |

- **Phân loại tài liệu:** A công khai → mọi chế độ · B nội bộ chưa công bố → ngoại tuyến / máy chủ của đơn vị · C giấy làm việc kiểm toán → **chỉ** ngoại tuyến (Luật Bảo vệ dữ liệu cá nhân 91/2025, NĐ 356/2025, Luật Kiểm toán độc lập Đ.43)
- **Cài đặt:** một tệp `GreenScan.bat` (Windows) hoặc `quantum-agent app` — giao diện và API trên một cổng
- **Lộ trình 6 tháng:** 11–12/2026 thử nghiệm với 1–2 đơn vị + đo thời gian soát · Q1/2027 quy tắc pháp lý (đối tượng kiểm kê QĐ 13, mục 6 TT 96), so chéo kỳ *"im lặng có chọn lọc"* · Q2/2027 mở rộng theo ngành thép, xi măng, nhiệt điện
- **Ai trả tiền:** công ty kiểm toán/đảm bảo ESG · ngân hàng thẩm định tín dụng xanh · doanh nghiệp niêm yết tự soát trước khi công bố (danh sách thông tin còn thiếu)
- **Đối tác:** ⚠️ chỉ ghi khi có thật — lời mời pilot (A10) gửi chưa, ai trả lời. Không có thì ghi *"đang mời: …"*
- **Hình:** IMG-10
- **Lời:**
  > "Mặc định, GreenScan chạy ngoại tuyến trên một laptop bình thường, không tốn tiền và tài liệu không rời máy — vì giấy làm việc kiểm toán là tài liệu mật theo luật. Nếu đơn vị muốn mô hình đọc thêm các cặp khó, có chế độ đám mây đặt tại Việt Nam, chỉ dùng cho tài liệu đã công bố. Cài đặt là một tệp chạy. Sáu tháng tới, chúng em thử nghiệm với đơn vị thật để đo đúng thứ người dùng trả tiền: thời gian tiết kiệm được."

### S13 · Quantum — 0:15 · Nhân

- **Tiêu đề:** Quantum ở đâu: chọn tập bằng chứng tối ưu — nghiên cứu, chưa vào sản phẩm
- **Trên slide:** chọn k đoạn bằng chứng phủ đủ 5 thuộc tính, ít trùng lặp = bài toán QUBO · benchmark 4 cột: Top-k · Tham lam/MMR · ILP chính xác · Ủ mô phỏng / QAOA mô phỏng · đo độ phủ, trùng lặp, số đoạn, thời gian · **không tuyên bố quantum advantage**
- **Hình:** IMG-12
- **Lời:**
  > "Lượng tử không bị ép vào sản phẩm. Bước chọn tập bằng chứng có thể viết thành bài toán QUBO; chúng em đã viết công thức và kế hoạch so với ba phương pháp cổ điển. Nếu QAOA không thắng, đó vẫn là một kết quả hợp lệ."

### S14 · Kết — 0:15 · Quỳnh

- **Tiêu đề:** Mỗi kết luận trả lời được bốn câu
- **Trên slide:** Tuyên bố gốc ở đâu? · Bằng chứng ở đâu? · Phép kiểm nào đã chạy? · Vì sao hệ thống được — hoặc không được — kết luận?
- **Hình:** IMG-13
- **Lời:**
  > "GreenScan không quyết định ai tẩy xanh. Nó bảo đảm người quyết định nhìn đúng chỗ, với đúng bằng chứng — và mọi điều nó nói đều trả lời được bốn câu này. Chúng em cảm ơn hội đồng."

### Phụ lục — không trình chiếu, mở khi bị hỏi

| Mã | Nội dung | Nguồn |
| --- | --- | --- |
| **P1** | **Khai báo công cụ AI hỗ trợ** (bắt buộc theo Điều 14) — xem [README](README.md) §4 | — |
| P2 | Giới hạn đã biết: chữ gãy dòng/tiêu đề dính câu vẫn lọt vào hàng đợi (mục #1); **1 trong 2 tuyên bố "ủng hộ" trên Hòa Phát là chữ dính cột** ("Hoàn thành kiểm kê khí nhà kính theo tiêu 90%" — 90% thuộc câu "tự chủ 90% điện" bên cạnh, phát hiện 09/10); chưa trích dẫn tới ô bảng; bộ quy tắc pháp lý mới 1 quy tắc nháp; nhánh OCR chưa kiểm trên máy demo; thứ tự hàng đợi chưa được kiểm toán viên kiểm | `AUDIT_2026-10-06.md` §2, §3 |
| P3 | Ngưỡng đánh giá đăng ký trước | `configs/measurement_decisions.yaml` |
| P4 | Registry pháp lý: chuỗi NĐ 06/2022 → 119/2025 → 83/2026, ba ngày hiệu lực đã sửa | `configs/legal/LEGAL_SOURCE_REGISTRY.yaml` |
| P5 | Ca KLM: "bị bác bỏ" từ nguồn có thẩm quyền, giữ nguyên trích dẫn | phiên `ce4eb6e4` |
| P6 | Chi phí và số đo phần cứng chi tiết | `docs/04-data-ai/MODEL_ROUTING_AND_HARDWARE.md` |
| P7 | Định tuyến mô hình theo từng việc (việc nào đang chạy, việc nào kế hoạch) | `configs/routing.yaml` |
| P8 | Hướng dẫn cài đặt và chạy một trang | `README.md` gốc repo |

---

## 4. Số liệu được phép đưa lên slide

| Số | Giá trị | Nguồn / cách tái hiện | Ngày đo |
| --- | --- | --- | --- |
| Thời gian, RAM trên Hòa Phát | 107–121 s (3 lần), RAM đỉnh 1.331 MB, i7-1355U, 16 GB, không GPU, ngoại tuyến · 09/10 qua giao diện: 140,5 s (máy đang chạy việc khác) | `benchmark/queue_quality_2026-10-06.md`; job của phiên `cd5a82e3` | 06/10, 09/10 — **đo lại trên máy trình chiếu** |
| Ngoại tuyến thật sự | Chặn mọi kết nối ra ngoài máy khi chạy 264 trang: **0 lần cố kết nối**, 156 tuyên bố, 108 s. Đối chứng: bật mô hình đám mây cùng bộ chặn → 15 lần bị chặn tới `mkp-api.fptcloud.com` (bộ chặn hoạt động) | Kiểm 09/10 bằng audit hook của Python chặn `socket.getaddrinfo`/`socket.connect` ra ngoài loopback (script tạm — **chưa vào repo**, nên đưa thành kiểm thử hồi quy); câu trả lời ở [04 tiêu chí 5](04_HOI_DAP_BO_SUNG.md#tiêu-chí-5--triển-khai-15) | 09/10 |
| Ngoại tuyến mất gì | So với mô hình có chốt chặn: 3/156 kết luận khác (150/2/0/4 so với 153/2/0/1), 13 gợi ý cho người soát; số "bị bác bỏ" bằng nhau (0) | `benchmark/llm_stance_ab_2026-09-28.md` | 28/09 |
| Số tuyên bố / kết luận | 156; 153 khớp một phần · 2 ủng hộ · 1 chưa đủ bằng chứng | phiên `cd5a82e3` | 09/10 |
| Hàng đợi | 9/172 mục | phiên `cd5a82e3` | 09/10 |
| Cộng lại bảng KNK | 22.540.603 + 933.876 = 23.474.479; công bố 23.474.480 | phiên `cd5a82e3`, trang 39 | 09/10 |
| Mâu thuẫn sai trước/sau | 357/419 (17/09) → 0 | `CORE_FEATURE_TEST_REPORT_2026-09-20.md`; phiên `cd5a82e3` | 17/09; 09/10 |
| Mô hình tự quyết | 10 CONTRADICTED + 2 CRITICAL | `benchmark/llm_stance_ab_2026-09-28.md` | 28/09 |
| Chế độ đám mây | 632 s lần đầu (710 lời gọi, 8 luồng, 0 lỗi); 188 s chạy lại, 0 lời gọi; 4–6 s/lời gọi | như trên | 28/09 |
| Chi phí đám mây | US$0,8–2,0/bộ — **ước tính**, ghi chữ "ước tính" | `MODEL_ROUTING_AND_HARDWARE.md` §2 | 06/10 |
| Kiểm thử | 359 (47 · 17 · 15) | `pytest` | 09/10 |
| Ca có phán quyết | 4/4 | `data/real_cases/scripts/run_case.py --all` | 09/10 |
| Kho dữ liệu | 1.061 tài liệu · 670 có bản gốc · 21 doanh nghiệp | `data/crawl/vn30/contract/raw.jsonl` | 09/10 |
| Pháp lý | 11 văn bản trong registry | `configs/legal/LEGAL_SOURCE_REGISTRY.yaml` | 09/10 |
| Án lệ | 28 bộ, 176 tài liệu | `data/legal_cases/` | 09/10 |
| Gold | 88 cặp lấy mẫu; **0 đã gán tính tới 09/10** | `data/gold/sessions/` | cập nhật 17/10 |
| Thực trạng Việt Nam | 28,38% · 72,5% · 2/22 · 50,6% | `docs/08-knowledge/03_THUC_TRANG_VA_NGHIEN_CUU_VN.md` §1 | — |
| Pháp lý "vì sao bây giờ" | 2.166 cơ sở; ngày hiệu lực; 110 cơ sở ⚠️ | `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md` | — |

**Không đưa lên slide:** "độ chính xác X%", "tiết kiệm 8–12 giờ", "53.000 tỷ USD", "704,2 nghìn tỷ", ">21%/năm" (slide 2 cũ — chưa có nguồn trong kho tri thức; nếu muốn giữ, Thảo tìm nguồn gốc và ghi dưới slide), khảo sát PwC (nguồn lỗi 403), mức phạt cụ thể của các nghị định xử phạt (chưa đọc bản gốc).

---

## 5. Cắt xuống 7 phút

| Slide | 10 phút | 7 phút | Cách cắt |
| --- | --- | --- | --- |
| S1 | 0:10 | 0:10 | — |
| S2 | 0:30 | 0:20 | Bỏ câu "hôm nay trả lời bốn câu đó là việc tay" |
| S3 | 0:40 | 0:25 | Chỉ nói ba bước tô đậm |
| S4 | 0:40 | 0:30 | Mỗi cột nói hai số |
| S5 | 0:35 | 0:25 | Chỉ đọc 4 ràng buộc |
| S6 | 2:40 | 2:00 | Bỏ bước ghi quyết định người soát (nói một câu khi ở giấy làm việc) |
| S7 | 0:35 | 0:30 | — |
| S8 + S9 | 1:20 | 0:45 | Gộp: giữ ví dụ 99%/24% và thí nghiệm 10 mâu thuẫn sai |
| S10 | 0:45 | 0:35 | Bỏ khối án lệ (giữ con số 4/4 ở S11) |
| S11 | 0:40 | 0:30 | — |
| S12 | 0:45 | 0:35 | Bỏ dòng "ai trả tiền" |
| S13 | 0:15 | — | Chuyển vào phụ lục |
| S14 | 0:15 | 0:15 | — |
| **Tổng** | **9:50** | **7:00** | |

---

## 6. Phân vai và chuyển lời

- **Quỳnh** (kiểm toán): S1–S3, S5, S11, S14 — mở và đóng, vì người dùng là kiểm toán viên.
- **Thảo** (pháp lý): S4, S10, S12 — mọi thứ về luật, dữ liệu và bảo mật.
- **Nhân** (kỹ thuật): S6–S9, S13 — bấm demo và giải thích cơ chế.
- **Câu chuyển** (mỗi câu ≤ 5 giây): S5→S6 Quỳnh: *"Nhân sẽ cho hội đồng thấy hệ thống làm việc đó trên một báo cáo thật."* · S9→S10 Nhân: *"Thảo sẽ nói dữ liệu đứng sau những kết luận này."* · S10→S11 Thảo: *"Quỳnh tổng kết điều đã đo được."* · S11→S12 Quỳnh: *"Còn đưa vào dùng thật thế nào — Thảo."*
- **Hỏi đáp:** người được hỏi trả lời trước; câu kỹ thuật chuyển Nhân, câu luật chuyển Thảo, câu nghiệp vụ kiểm toán chuyển Quỳnh. Khung trả lời ở [04](04_HOI_DAP_BO_SUNG.md).
