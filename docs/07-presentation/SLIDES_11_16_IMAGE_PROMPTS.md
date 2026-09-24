# Slide 11–16: prompt sinh ảnh + kịch bản tự giải thích

**Ngày:** 2026-09-24 · **Dùng cho:** phần kiến trúc trong bài thuyết trình
**Nguyên tắc:** mỗi slide có **một hình**, **một câu chốt**, và **một kịch bản 30–40 giây**. Hình không cần chứa nhiều chữ — người nói mới là nơi chứa nội dung. Nếu hình phải giải thích bằng đoạn văn thì hình đó sai.

---

## 0. Hai chỗ phải sửa trước khi vẽ

### 0.1 🔴 Slide 14 **không được** ghi "GraphRAG"

Nhóm đã **cố ý loại GraphRAG** (DECISIONS_LOG D-2026-09-18-02, ISSUES A8/G8). Vẽ nó lên slide là tự tạo một câu hỏi không trả lời được: *"cho xem graph của các em"*.

Quan trọng hơn: **việc loại nó là một luận điểm mạnh**, nên đem ra nói thay vì giấu.

> Kiểm chứng một tuyên bố là bài toán truy xuất **cục bộ theo sự kiện** — cần đúng đoạn văn có con số đó, ở đúng trang. GraphRAG mạnh ở câu hỏi **tổng hợp toàn cục** ("xu hướng ngành ra sao"), đổi lại phải dựng và bảo trì đồ thị. Với bài toán này nó thêm chi phí mà không thêm độ đúng.

**Tiêu đề đúng cho slide 14:** *"Truy xuất bằng chứng đa nguồn: hybrid retrieval + reranking"*.

### 0.2 🟠 Ghi đúng thì của "hybrid RAG" và "reranker"

Cấu hình mặc định hôm nay: **BM25 + char n-gram TF-IDF + RRF**; `embedding: lite`, `reranker: none` (bộ rerank là no-op, chỉ cắt 30→5). Adapter BGE-M3 và bge-reranker-v2-m3 **có code, chưa bật, chưa đo** (D-2026-09-22-04).

Cách trình bày an toàn — và vẫn mạnh: trên hình, khối dense + rerank có **viền nét đứt** và nhãn nhỏ *"đã tích hợp, bật sau khi có gold"*. Người nói: *"Chúng tôi chỉ bật một thành phần khi đo được nó có ích."*

### 0.3 Cách dùng prompt

Mô hình sinh ảnh viết chữ sai, đặc biệt tiếng Việt. Quy trình đúng:

1. Dùng prompt để lấy **hình minh hoạ + bố cục**, yêu cầu **không có chữ** hoặc chỉ vài nhãn tiếng Anh.
2. Đặt **chữ tiếng Việt bằng PowerPoint/Figma** đè lên.
3. Với sơ đồ có mũi tên và số liệu (slide 11, 15): dùng bản vector đã dựng ([`diagrams/`](diagrams/)) thay vì sinh ảnh.

Đuôi chung thêm vào mọi prompt:

```text
flat vector infographic, muted deep green #1F7A52 and navy #16283B on off-white #F7F7F4,
thin line icons, small corner radius, subtle shadow, generous white space, no gradients,
no neon, no circuit board, no robot, no glowing brain, no 3D, enterprise audit software
aesthetic, 16:9
```

---

## Slide 11 — Kiến trúc tổng thể

**Câu chốt:** *Mô hình đọc. Luật quyết định. Người duyệt ca rủi ro cao.*

**Không sinh ảnh cho slide này.** Dùng [`diagrams/pipeline_16x9_vi.png`](diagrams/pipeline_16x9_vi.png) — sơ đồ có mũi tên và con số, phải chính xác tuyệt đối.

**Kịch bản 40 giây:**
> "Đầu vào có ba cửa, không phải một: báo cáo doanh nghiệp, bằng chứng độc lập, và văn bản pháp luật — mỗi loại đi vào một bước khác nhau. Nửa trên là phần mô hình đọc: đọc tài liệu, lọc câu nào đáng kiểm chứng, chuẩn hoá thành cấu trúc, tìm bằng chứng. Đường kẻ ngang này là ranh giới quan trọng nhất của kiến trúc: **bên dưới không có mô hình nào cả**. Phép so sánh, đối chiếu luật và kết luận đều do mã tất định làm, nên mỗi kết luận chỉ ra được phép tính nào đã chạy. Cuối cùng, ca rủi ro cao bắt buộc qua người duyệt, và quyết định của người quay lại thành dữ liệu huấn luyện."

**BGK có thể hỏi:** *"Vì sao không để LLM quyết luôn cho nhanh?"* → "Vì kết luận về một doanh nghiệp phải audit được. Một mô hình nói CONTRADICTED không chỉ ra được vì sao; một dòng code so 23.474.480 với 23.474.479 thì chỉ ra được."

---

## Slide 12 — Bước 1: Document AI & OCR

**Câu chốt:** *Mỗi câu phải biết nó nằm ở trang nào — nếu không, nó không phải bằng chứng.*

**Nội dung đúng:** lớp chữ có sẵn đọc bằng PyMuPDF; trang dưới 40 ký tự → Tesseract OCR và đánh dấu `used_ocr`; bảng tách riêng bằng pdfplumber thành chunk độc lập. Provenance hiện tới **trang**; tới **ô bảng** là việc đang làm, chưa xong.

```text
A clean illustration of document understanding: on the left a stack of PDF pages, one
page lifted and shown large; on the page, three regions are highlighted with thin
rounded outlines - a paragraph block, a data table, and a heading - each connected by a
short thin line to a small tag on the right showing a page marker icon. Below the page,
a smaller scanned page with a dashed outline routes through a small OCR badge before
joining the same flow. No paragraphs of text anywhere, only shapes suggesting text.
```

**Kịch bản:**
> "Một báo cáo 118 trang được cắt thành hàng nghìn đơn vị nhỏ: đoạn văn, bảng, tiêu đề. Mỗi đơn vị mang theo số trang và mã kiểm tra nội dung. Trang nào không có lớp chữ thì mới qua nhận dạng ảnh, và đơn vị đó bị đánh dấu là kém chắc chắn hơn. Lý do làm chặt ở đây rất đơn giản: nếu một câu không biết nó ở trang nào thì nó không dùng làm bằng chứng được."

**BGK hỏi:** *"PDF scan thì sao?"* → "Có nhánh OCR và cờ đánh dấu. Trên máy demo chưa cài Tesseract nên hai tài liệu demo đều dùng lớp chữ có sẵn — chúng tôi nói đúng như vậy chứ không nói đã kiểm chứng nhánh OCR."

---

## Slide 13 — Bước 2: Claim Extraction & Normalization

**Câu chốt:** *Câu bị loại cũng được giữ lại, kèm lý do — vì "hệ thống đã bỏ qua cái gì" là câu hỏi đầu tiên của người kiểm tra.*

**Nội dung đúng:** lọc 4 lớp (đáng kiểm chứng · mơ hồ · không phải tuyên bố · văn mẫu); loại tiêu đề, mục lục, dòng bảng chỉ số, mảnh câu bị cắt — **mỗi câu loại đều ghi lý do**. Chuẩn hoá thành 5 thuộc tính. Hiện extractor là **luật**; chuẩn hoá bằng mô hình là bước kế tiếp (chưa bật).

```text
An illustration of sentence triage: a column of short text-line shapes flows into a
simple sorting device; four labelled output trays fan out below, three of them dimmed
and one highlighted in green. Each dimmed tray has a tiny tag icon attached, suggesting
a recorded reason. To the right, one highlighted sentence expands into a small form card
with five empty labelled fields. Shapes only, minimal words.
```

**Kịch bản:**
> "Không phải câu nào trong báo cáo cũng là tuyên bố cần kiểm chứng. Tiêu đề, mục lục, dòng của bảng số liệu, câu chào của lãnh đạo — hệ thống loại ra, nhưng **không xoá**: mỗi câu bị loại được lưu kèm lý do, nên đếm được và soát được. Câu nào đi tiếp thì được điền vào một khuôn năm thuộc tính: chỉ số, kỳ, năm gốc, phạm vi, giá trị. Khuôn này là cái làm cho bước sau có thể kiểm tra bằng máy."

**BGK hỏi:** *"Làm sao biết lọc đúng?"* → "Chúng tôi đang xây bộ 100 câu gán nhãn tay để đo precision/recall theo từng lớp. Hiện chưa có con số, nên chúng tôi không báo con số."

---

## Slide 14 — Bước 3: Truy xuất bằng chứng đa nguồn

> ⚠️ **Đổi tiêu đề**, bỏ "GraphRAG" — xem mục 0.1.

**Câu chốt:** *Lấy rộng rồi lọc hẹp: 30 ứng viên, giữ 5. Nhiều ngữ cảnh hơn không đồng nghĩa với đúng hơn.*

**Nội dung đúng:** BM25 (từ) + TF-IDF ký tự 3–5 gram (chịu lỗi OCR) hợp nhất bằng RRF → 30 ứng viên → rerank → 5 đoạn, mỗi đoạn có trang. Bằng chứng độc lập vào ở đúng bước này. Dense + cross-encoder: **đã tích hợp, chưa bật**.

```text
A funnel diagram illustration: on the left two parallel narrow columns of small document
cards representing two different search methods, merging into a single wider column of
about thirty small cards; the column passes through a funnel shape with a small gear at
its neck; below the funnel only five cards remain, larger and highlighted, each carrying
a small page-number tag. A separate short inflow arrow joins the thirty-card column from
the side, labelled with a small government-building icon and an audit icon. Two of the
upstream elements are drawn with dashed outlines to mark them as integrated but not yet
switched on.
```

**Kịch bản:**
> "Hệ thống tìm bằng chứng theo hai cách song song: khớp từ khoá, và khớp theo dạng ký tự để chịu được lỗi chính tả và lỗi OCR. Hai bảng xếp hạng được hợp nhất, lấy 30 ứng viên rồi lọc xuống 5. Vì sao không đưa cả 30 vào? Nghiên cứu về RAG cho thấy thêm tài liệu nhiễu làm kết quả **tệ đi**, nên chúng tôi lấy rộng để không bỏ sót, rồi lọc hẹp để không nhiễu. Đây cũng là chỗ bằng chứng độc lập — kiểm toán, cơ quan quản lý — đi vào, vì một báo cáo không được tự xác nhận chính mình."

**BGK hỏi:** *"Sao không dùng GraphRAG cho hiện đại?"* → dùng nguyên đoạn ở mục 0.1. Đây là câu trả lời ghi điểm, không phải câu chống đỡ.

---

## Slide 15 — Bước 4: Numeric & Legal Checker

**Câu chốt:** *Tìm thấy hai con số khác nhau chưa phải là tìm thấy mâu thuẫn.*

Đây là **slide quan trọng nhất trong sáu slide**. Nên dùng hình vẽ vector cho phần cổng (chính xác tuyệt đối), hoặc nếu sinh ảnh thì theo prompt dưới.

**Nội dung đúng:** 6 chiều — loại giá trị · ranh giới tổ chức · công nghệ · chỉ số con · phạm vi phát thải · mục tiêu/thực hiện. Lệch bất kỳ chiều nào → **không kết luận mâu thuẫn**. Dung sai theo **độ chính xác đã công bố** ("12%" tolerate 11,5–12,5; "12,0%" chỉ 11,95–12,05), không dùng một hằng số chung. Pháp lý: chọn văn bản còn hiệu lực tại thời điểm công bố (NĐ 06/2022 → 119/2025 → 83/2026), điều kiện kiểm được. Trạng thái thật: rule pack mới có **1 rule nháp**, nên phần lớn trả về "chưa đủ căn cứ" — nói thẳng điều này.

```text
A gate mechanism illustration: two number tokens enter from the top left and top right
and meet at a horizontal barrier drawn as a row of six small check slots; below the
barrier the path splits into two, one continuing down to a small calculator shape, the
other ending at a closed barrier marker. To the right, separate from the gate, a law
book with a small calendar badge on its cover sits above a short vertical list of three
outcome markers. Balanced, symmetrical, no decorative clutter, almost no words.
```

**Kịch bản:**
> "Đây là điểm khác biệt kỹ thuật lớn nhất. Trong báo cáo Hoà Phát có câu 'gang thép chiếm hơn 99% tổng phát thải' và câu 'sản lượng thép thô tăng 24%'. Một hệ thống ngây thơ thấy 99 khác 24 và kết luận mâu thuẫn — hệ thống của chúng tôi từng mắc đúng lỗi đó, 5 lần trong một lần chạy. Nay mỗi con số mang theo sáu chiều, và hai con số chỉ được đem so khi không chiều nào lệch. 99% là tỷ trọng, 24% là mức thay đổi — khác cơ sở đo, nên không so. Về pháp lý, hệ thống chọn văn bản còn hiệu lực **tại thời điểm doanh nghiệp công bố**, không phải hiệu lực hôm nay."

**BGK hỏi:** *"Dung sai bao nhiêu thì coi là khớp?"* → "Theo độ chính xác doanh nghiệp công bố, không theo một hằng số. Viết 12% thì chúng tôi hiểu là 11,5–12,5; viết 12,0% thì chỉ 11,95–12,05. Trước đây chúng tôi có dùng một hằng số 12% cho mọi trường hợp và đã bỏ, vì không có cơ sở nào biện minh cho con số đó."

---

## Slide 16 — Bước 5: Verdict Engine & Risk

**Câu chốt:** *"Chưa đủ bằng chứng" là một kết quả hợp lệ — và là lý do hệ thống đáng tin.*

**Nội dung đúng:** 5 mức kết luận; `UNSUPPORTED` chỉ khi kho tài liệu **đủ** để lẽ ra phải có bằng chứng, ngược lại `INSUFFICIENT_EVIDENCE`. Rủi ro tách ba chiều: **độ mạnh bằng chứng · mức mâu thuẫn · mức trọng yếu (chưa xác định)**. Claim không bị bác bỏ **trần MEDIUM**. Mọi mâu thuẫn đều chuyển người duyệt bất kể điểm.

```text
An outcome illustration: a vertical branch splits into two paths under a small question
marker; the left path leads to a row of four small status markers, the right path leads
to a single larger amber-outlined marker that stands apart, with three small tags
beneath it suggesting what is missing. To the right, three separate small bar meters of
different heights stand side by side, the third one drawn in faint dashed outline to
indicate it is not yet measured. Calm, restrained, no words.
```

**Kịch bản:**
> "Đầu ra không phải một điểm 'greenwashing 73%'. Đơn vị đánh giá là từng tuyên bố, với năm mức. Mức thứ năm — chưa đủ bằng chứng — là chỗ chúng tôi đầu tư nhiều nhất: hệ thống chỉ được phép nói 'không được chứng minh' khi biết chắc kho tài liệu **lẽ ra phải có** bằng chứng đó; còn lại thì từ chối kết luận và nói rõ thiếu gì. Rủi ro tách làm ba chiều, vì bằng chứng yếu không đồng nghĩa với khả năng doanh nghiệp sai. Chiều thứ ba — mức trọng yếu — chúng tôi **chưa đo được**, nên để trống thay vì bịa ra một con số."

**BGK hỏi:** *"Vậy rốt cuộc có phát hiện được greenwashing không?"* → "Chúng tôi phát hiện **tuyên bố không đứng vững được trước bằng chứng**, và chỉ ra chính xác nó hỏng ở đâu. Việc gọi đó là greenwashing là một kết luận pháp lý — thuộc về người có thẩm quyền, không thuộc về phần mềm."

---

## Bảng kiểm trước khi đưa sáu slide này ra

| # | Kiểm | |
| --- | --- | --- |
| 1 | Không còn chữ "GraphRAG" ở bất kỳ slide nào | ☐ |
| 2 | Dense retrieval / reranker có ghi rõ "chưa bật" hoặc slide có tiêu đề *luồng đích* | ☐ |
| 3 | Không slide nào ghi "độ chính xác X%" | ☐ |
| 4 | Không slide nào gọi đầu ra là "điểm greenwashing" | ☐ |
| 5 | Mọi tên văn bản pháp luật là văn bản Việt Nam, đúng số hiệu | ☐ |
| 6 | Mỗi slide nói được trong 40 giây mà không đọc chữ trên hình | ☐ |
| 7 | Mỗi slide có sẵn một câu trả lời cho câu hỏi khó nhất của nó | ☐ |

---

## Liên quan

[PIPELINE_DIAGRAM_BRIEF.md](PIPELINE_DIAGRAM_BRIEF.md) · [`diagrams/`](diagrams/) · [QA_BANK_100_2026-09-20.md](QA_BANK_100_2026-09-20.md) · [TARGET_PIPELINE_AND_TRAINING.md](../04-data-ai/TARGET_PIPELINE_AND_TRAINING.md) · [DECISIONS_LOG.md](../00-project/DECISIONS_LOG.md) (D-2026-09-18-02 GraphRAG, D-2026-09-22-04 hybrid RAG)
