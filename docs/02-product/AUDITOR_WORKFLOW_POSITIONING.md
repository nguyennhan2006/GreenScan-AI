# Định vị lại sản phẩm quanh quy trình của kiểm toán viên

**Ngày:** 2026-09-25 · **Trạng thái:** định vị có hiệu lực, thay phần định vị sản phẩm trong `USER_PERSONAS.md` và `MVP_SCOPE.md` (bản 07/07, 6 persona)
**Lý do viết:** số đo ngày 23/09 trên Hoà Phát — **156 tuyên bố → 153 "khớp một phần" → 154 "MEDIUM" → 0 ca được gắn cờ**. Đưa bảng đó cho một kiểm toán viên thì câu hỏi đầu tiên của họ là *"tôi phải xem cái nào trước?"* và hệ thống không trả lời được. Đó không phải lỗi thuật toán; đó là lỗi định vị.

---

## 1. Người dùng là ai — một câu

> **Một kiểm toán viên / chuyên viên đảm bảo đang làm việc này bằng tay:** mở báo cáo phát triển bền vững vài trăm trang, đọc dò tìm câu có tuyên bố môi trường, lật sang bảng số liệu để đối chiếu, tra xem văn bản nào áp dụng, rồi gõ từng dòng vào giấy làm việc.

Không phải nhà đầu tư nhỏ lẻ. Không phải người tiêu dùng. Không phải "ai cũng dùng được". Bản 07/07 liệt kê 6 persona — đó là lý do sản phẩm không sắc: **thiết kế cho sáu người thì không tối ưu cho ai.**

---

## 2. Hôm nay họ làm gì, và thời gian đi đâu

| # | Việc | Bản chất | Thời gian | Tự động hoá được? |
| --- | --- | --- | --- | --- |
| 1 | Nhận bộ tài liệu: BCPTBV + BCTN + BCTC | thủ tục | ít | — |
| 2 | **Đọc dò tìm câu có tuyên bố môi trường** | cơ học, mỏi mắt | **rất nhiều** | ✅ **hoàn toàn** |
| 3 | **Lật tìm bảng/đoạn số liệu tương ứng** | cơ học, Ctrl+F, lật trang | **rất nhiều** | ✅ **hoàn toàn** |
| 4 | Kiểm tra số khớp không, có năm gốc không, Scope nào, đơn vị nào | nửa cơ học nửa xét đoán | trung bình | ✅ phần cơ học |
| 5 | Tra văn bản áp dụng, hiệu lực thời điểm công bố | tra cứu | trung bình | ✅ phần tra cứu |
| 6 | **Gõ vào giấy làm việc: câu, trang, nhận định, lý do** | cơ học | **rất nhiều** | ✅ **hoàn toàn** |
| 7 | Quyết định chỗ nào trọng yếu, soi tiếp hay dừng | **xét đoán nghề nghiệp** | ít nhưng quyết định tất cả | ❌ **hỗ trợ, không thay** |
| 8 | Kết luận, bảo lưu, ký | **trách nhiệm nghề nghiệp** | ít | ❌ **không bao giờ** |

**Ba việc chiếm phần lớn thời gian là 2, 3, 6 — và cả ba đều là việc cơ học.** Đó chính xác là phạm vi sản phẩm.

> **Định vị một câu:** GreenScan tự động hoá việc **đọc, định vị và ghi chép** trong phân tích greenwashing, để kiểm toán viên dành toàn bộ thời gian còn lại cho **xét đoán** — và chỉ ra nên xét đoán ở đâu trước.

---

## 3. Chỗ định vị cũ bị lệch

| | Bản cũ (fact-checking) | Bản này (hỗ trợ kiểm toán) |
| --- | --- | --- |
| Đơn vị làm việc | một câu tuyên bố | một **hàng đợi soát** đã xếp ưu tiên |
| Điểm bắt đầu | câu đầu tiên trong tài liệu | **chỗ rủi ro cao nhất** |
| Đầu ra | danh sách 156 verdict | **giấy làm việc** + danh sách việc cần soát, có thứ tự |
| Coi là xong khi | mọi câu có verdict | kiểm toán viên đã soát hết phần trọng yếu và ký |
| Bỏ qua điều gì | không được bỏ gì | **bỏ phần không trọng yếu là đúng quy trình**, miễn có ghi lý do |
| Thước đo thành công | độ chính xác verdict | **thời gian tiết kiệm được với cùng mức độ tin cậy** |

Dòng cuối là thay đổi lớn nhất. Trước đây tôi tối ưu "verdict đúng"; người dùng cần "cùng kết luận đó nhưng nhanh hơn, và chứng minh được là đã soát đủ".

---

## 4. Ba lớp phải thêm

Kiến trúc hiện tại (evidence-first, cổng khả năng so sánh, abstain) **giữ nguyên** — nhưng nó là **một thủ tục kiểm tra chi tiết**, không phải cả cuộc kiểm toán. Ba lớp còn thiếu:

### 4.1 Lớp xếp ưu tiên — sửa trực tiếp lỗi "154 MEDIUM"

Kiểm toán không đối xử mọi khoản mục như nhau. 156 tuyên bố cũng vậy: *"tổng phát thải toàn tập đoàn 23,4 triệu tCO₂e"* không cùng hạng với *"đã tổ chức đào tạo về môi trường"*.

Điểm ưu tiên là **tổng có trọng số của bốn yếu tố, tính bằng mã tất định** (giữ nguyên nguyên tắc "luật quyết định"):

| Yếu tố | Nghĩa | Lấy từ đâu |
| --- | --- | --- |
| **Độ trọng yếu** | Con số này lớn đến đâu so với chính tổng của doanh nghiệp; chỉ số có phải loại nhà đầu tư quan tâm | `numeric_facts` đã có — giá trị, đơn vị, ranh giới |
| **Nghĩa vụ công bố** | Tuyên bố này có nằm trong một nghĩa vụ cụ thể không (kiểm kê KNK theo QĐ 13, mục 6 Phụ lục IV TT 96) | tầng pháp lý |
| **Mức khuyết bằng chứng** | Thiếu 1 thuộc tính khác thiếu 4 thuộc tính | `missing_attributes` đã có |
| **Bất thường so với kỳ trước** | Cùng chỉ số, năm nay khác hẳn năm ngoái, hoặc năm nay im lặng về thứ năm ngoái công bố | **§4.2 — chưa có** |

Đầu ra không phải một dải mà là **một thứ tự**: *"trong 156 câu, 12 câu này nên soát trước, vì sao thì đây."* Đó là thứ kiểm toán viên dùng được ngay từ phút đầu.

### 4.2 Thủ tục phân tích — chỗ corpus 670 tài liệu mới phát huy

Hiện 670 tài liệu / 21 doanh nghiệp chỉ dùng làm kho tra cứu. Kiểm toán có một thủ tục chuẩn mà chúng ta đang bỏ trống: **so sánh phân tích** (analytical procedures). Ba phép so chéo dựng được ngay trên tầng `extract` đã có:

| Phép so | Câu hỏi | Cờ sinh ra |
| --- | --- | --- |
| **Chéo năm, cùng doanh nghiệp** | Cường độ phát thải năm nay lệch bất thường so với ba năm trước? Chỉ số năm ngoái công bố mà năm nay không còn? | *biến động bất thường* · **im lặng có chọn lọc** |
| **Chéo doanh nghiệp, cùng ngành** | Doanh nghiệp này báo cường độ thấp hơn hẳn mọi doanh nghiệp thép khác? | *ngoại lai so với ngành* |
| **Chéo tài liệu, cùng kỳ** | BCPTBV và BCTN nói hai số khác nhau cho cùng chỉ số? | *không nhất quán nội bộ* |

**"Im lặng có chọn lọc"** là phát hiện mà đọc tay gần như không bắt được — phải nhớ báo cáo năm trước có gì. Đây là chỗ máy hơn người rõ rệt, và là lập luận thuyết phục nhất cho việc dùng AI trong kiểm toán.

### 4.3 Giấy làm việc — sản phẩm thật của kiểm toán

Hiện có `evidence_pack.md`. Cần một giấy làm việc đúng nghĩa: mục tiêu thủ tục · phạm vi và cách chọn mẫu · công việc đã thực hiện · bằng chứng kèm trang · kết luận · **người thực hiện và người soát xét** · những gì **không** kiểm và vì sao. Mục cuối là mục kiểm toán viên cần nhất và là mục hệ thống hiện không có.

---

## 5. Ánh xạ sang từ vựng kiểm toán

Năm thuộc tính hiện có đã gần với **cơ sở dẫn liệu** của ISA — chỉ cần gọi đúng tên, và khi gọi đúng tên thì kiểm toán viên hiểu ngay:

| Thuộc tính trong hệ thống | Cơ sở dẫn liệu | Câu hỏi kiểm toán |
| --- | --- | --- |
| chỉ số (metric) | **Phân loại** | Số này có đúng là chỉ số mà tuyên bố nói tới? |
| giá trị + đơn vị | **Chính xác** | Số có đúng và đo bằng đơn vị đã nêu? |
| kỳ | **Đúng kỳ** | Thuộc kỳ báo cáo hay kỳ khác? |
| năm gốc | **Chính xác** (so sánh) | Mốc so sánh có được nêu? |
| phạm vi / ranh giới | **Đầy đủ** | Có bao trùm đúng phạm vi đã tuyên bố, hay chỉ một phần? |
| — *(chưa có)* | **Trình bày** | Cách trình bày có gây hiểu nhầm dù từng số đều đúng? |

Dòng cuối là khoảng trống đáng ghi nhận: *cherry-picking* — mọi con số đúng nhưng chọn lọc để tạo ấn tượng sai. Thủ tục phân tích ở §4.2 là cách tiếp cận nó.

---

## 6. Thước đo mới: thời gian, không phải độ chính xác

| Thước đo | Vì sao | Trạng thái |
| --- | --- | --- |
| **Thời gian/báo cáo, cùng mức tin cậy** | Là lý do người ta mua | ❌ chưa đo — RQ10 |
| **Tỷ lệ thu hẹp hàng đợi**: bao nhiêu % tuyên bố cần mắt người | 156/156 = vô dụng; 12/156 có giải trình = dùng được | ❌ chưa có lớp ưu tiên |
| **Độ chính xác của thứ tự ưu tiên**: trong 12 câu xếp đầu, kiểm toán viên đồng ý mấy câu đáng soi | Đo đúng thứ sản phẩm bán | ❌ cần gold |
| **Tỷ lệ trích dẫn dùng được**: bấm vào có ra đúng trang | Nếu sai thì mất hết niềm tin | ✅ hiện 100% trên demo |
| Độ chính xác verdick | Vẫn cần, nhưng là chỉ tiêu nội bộ | ⏳ chờ gold |

Bài đo cho dòng đầu (protocol 1 trang, Quỳnh): 20 tuyên bố, một người làm tay, một người làm với GreenScan, đo thời gian và số bằng chứng tìm đúng. n nhỏ thì ghi rõ n nhỏ.

---

## 7. Đổi gì trong kế hoạch

| Ưu tiên | Việc | Sửa được vấn đề gì | Ghi chú |
| --- | --- | --- | --- |
| **P1** | **Lớp xếp ưu tiên** (§4.1) + màn "hàng đợi soát" thay vì bảng 156 dòng | 154 MEDIUM → thứ tự dùng được | Dùng dữ liệu đã có, không cần gold |
| **P1** | **Giấy làm việc** có mục "không kiểm gì và vì sao" (§4.3) | Sản phẩm thật của kiểm toán | Mở rộng `evidence_pack` |
| **P2** | **So chéo năm** + cờ "im lặng có chọn lọc" (§4.2) | Corpus 670 tài liệu có tác dụng thật | Chạy trên tầng `extract` đã có |
| **P2** | Đổi nhãn UI sang từ vựng cơ sở dẫn liệu (§5) | Kiểm toán viên hiểu ngay | Chỉ đổi chữ |
| **P3** | Bài đo thời gian (§6) | Có con số bán được | Cần người thật |
| **P3** | So chéo doanh nghiệp cùng ngành | Ngoại lai so với ngành | Sau khi có dữ liệu v2 |

Không đổi: cổng khả năng so sánh, abstain, tầng pháp lý theo hiệu lực, 8 cổng kiểm soát, nguyên tắc "mô hình đọc, luật quyết định". Chúng vẫn đúng — chỉ là chúng nằm **bên trong** khung kiểm toán, chứ không **là** sản phẩm.

---

## 8. Cách nói trước hội đồng

**Trước:** "Hệ thống của chúng tôi kiểm chứng tuyên bố môi trường bằng bằng chứng và phát hiện rủi ro greenwashing."

**Sau:**
> "Người dùng của chúng tôi là kiểm toán viên đang làm việc này bằng tay: đọc vài trăm trang, dò tìm tuyên bố, lật tìm số liệu, gõ giấy làm việc. Ba việc đó chiếm phần lớn thời gian của họ và cả ba đều là việc cơ học. GreenScan làm ba việc đó, rồi đưa lại cho họ **một hàng đợi đã xếp thứ tự**: trong 156 tuyên bố của báo cáo này, đây là 12 câu nên soát trước, và đây là lý do từng câu. Xét đoán vẫn là của họ — chúng tôi chỉ đảm bảo họ xét đoán đúng chỗ, và mọi thứ họ quyết định đều có giấy làm việc truy được về đúng trang."

Điểm mạnh nhất để nói thêm: **"im lặng có chọn lọc"** — năm ngoái doanh nghiệp công bố cường độ phát thải, năm nay không còn. Đọc tay khó bắt vì phải nhớ báo cáo cũ; máy so hai năm trong một giây. Đó là câu trả lời cho *"AI thêm được gì mà người không làm được"*.

---

## 9. Liên quan

[USER_PERSONAS.md](USER_PERSONAS.md) · [MVP_SCOPE.md](MVP_SCOPE.md) · [OUTPUT_SPEC.md](OUTPUT_SPEC.md) (giấy làm việc) · [../01-domain-audit/AUDIT_PROTOCOL.md](../01-domain-audit/AUDIT_PROTOCOL.md) · [../04-data-ai/TARGET_PIPELINE_AND_TRAINING.md](../04-data-ai/TARGET_PIPELINE_AND_TRAINING.md) · [../00-project/RESEARCH_PROGRAM_2026-09-22.md](../00-project/RESEARCH_PROGRAM_2026-09-22.md) (RQ8 rủi ro, RQ10 thời gian)
