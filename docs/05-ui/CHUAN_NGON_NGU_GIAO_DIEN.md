# Chuẩn ngôn ngữ giao diện GreenScan

Ban hành 05/11/2026. Áp dụng cho mọi chữ người dùng nhìn thấy:
- màn hình web;
- thông báo lỗi;
- lời giải thích của hệ thống;
- giấy làm việc và các tệp xuất.

Kiểm tự động bằng `python tools/check_ui_language.py`. Thêm `--strict` để công cụ báo lỗi khi còn chỗ vi phạm.

## 1. Năm nguyên tắc

1. **Chỉ một thứ tiếng: tiếng Việt.** Không trộn tiếng Anh vào câu (ví dụ "Tài liệu đang review", "Claim đã chốt").
2. **Thuật ngữ chuyên ngành có từ tiếng Việt thì dùng từ tiếng Việt.** Từ đó phải hiểu được ngay, theo bảng ở mục 3. Không có từ tương đương thì giải nghĩa bằng một cụm ngắn ngay lần đầu xuất hiện.
3. **Không để lộ mã nội bộ.** Không hiện ra màn hình:
   - giá trị mã như `emissions`, `ghg_scope_1_2_3`, `decrease`, `PARTIALLY_SUPPORTED`;
   - tên trường dữ liệu;
   - tên thí nghiệm như "B6".

   Mọi giá trị mã phải đi qua bảng nhãn `frontend/src/lib/labels.js`.
4. **Viết đủ, không viết tắt.** Viết "báo cáo phát triển bền vững", "khí nhà kính" thay cho BCPTBV, KNK. Chỗ quá chật thì dùng chữ ngắn nhưng phải có chú thích khi rê chuột (`title`).
5. **Một khái niệm, một từ.** Ví dụ: đã chọn "người soát xét" thì không dùng thêm "reviewer", "người duyệt", "kiểm toán viên" cho cùng một vai.

Được giữ nguyên:
- đuôi tệp và định dạng tệp: PDF, DOCX, .json;
- đơn vị: tCO2e, kWh, GB;
- phím tắt: Ctrl, Shift, Esc;
- tên riêng: GreenScan, Hòa Phát, FPT;
- tên chuẩn mực: ISO 14064, GRI, IFRS S2;
- mã chứng khoán: HPG.

Tên trường trong tệp cấu hình được giữ trong dấu `…` và luôn kèm giải thích tiếng Việt. Đây là thông báo cho người viết bộ quy tắc, không dành cho người soát xét.

## 2. Cách viết số, ngày, giờ

| Loại | Viết | Không viết |
|---|---|---|
| Số thập phân | 0,60 · 94,5 % | 0.60 · 94.5% |
| Hàng nghìn | 23.474.480 | 23,474,480 |
| Ngày | 05/11/2026 | 2026-11-05 |
| Phân số đếm | 3/4 mục | 3 of 4 |
| Trang | tr. 86 | p.86 · page 86 |

## 3. Bảng từ ngữ

### 3.1 Khái niệm chính

| Thay chữ này | Bằng chữ này | Giải thích một dòng (dùng trong hướng dẫn, chú thích) |
|---|---|---|
| claim | **tuyên bố** | Câu doanh nghiệp tự nói về môi trường, cần kiểm |
| evidence | **bằng chứng** | Đoạn văn, bảng số hoặc văn bản dùng để đối chiếu với tuyên bố |
| verdict | **kết luận** | Máy gợi ý tuyên bố được bằng chứng ủng hộ tới đâu |
| reviewer, auditor (vai trên app) | **người soát xét** | Người đọc gợi ý của máy và quyết định |
| review | **soát xét** | |
| queue | **hàng đợi** | Danh sách mục nên mở trước, có lý do |
| priority score (63/90) | **điểm ưu tiên** | Dùng để xếp thứ tự mở, **không phải** mức vi phạm |
| risk level | **mức cần chú ý** | Thấp / Trung bình / Cao / Rất cao |
| workpaper | **giấy làm việc** | Bản ghi những gì đã kiểm, để ký |
| sign-off | **ký duyệt** | |
| audit trail, audit log | **nhật ký các bước** | |
| hash, SHA-256 | **mã băm** | Dấu vân tay của tệp: đổi một chữ là mã đổi |
| source | **nguồn** | |
| independent source | **nguồn độc lập** | Không do chính doanh nghiệp viết |
| pipeline | **quy trình phân tích** | |
| session, run | **phiên phân tích** | |
| Studio | **Sửa báo cáo** | |
| demo, sample | **bộ mẫu để thử** | |
| AI đề xuất (AI_SUGGESTED) | **Máy gợi ý** | Kết quả do máy tạo, chưa có người xem |
| HUMAN_REVIEWED | Đã có người xem | |
| FINALIZED | Đã chốt | |

### 3.2 Năm loại kết luận

Ba chỗ phải dùng **cùng một nhãn**:
- `badges.jsx`;
- giấy làm việc;
- lời hướng dẫn.

Mã gốc chỉ tồn tại trong dữ liệu.

| Mã | Nhãn | Nghĩa nói cho người mới |
|---|---|---|
| SUPPORTED | Được ủng hộ | Có bằng chứng khớp đủ chỉ số, phạm vi, kỳ |
| PARTIALLY_SUPPORTED | Ủng hộ một phần | Có bằng chứng cùng chủ đề nhưng thiếu số, kỳ hoặc phạm vi để so |
| UNSUPPORTED | Chưa được chứng minh | Có tài liệu liên quan nhưng không cái nào chứng minh được |
| CONTRADICTED | Mâu thuẫn với nguồn | Có bằng chứng nói khác với tuyên bố; cần người soát xét đọc kỹ |
| INSUFFICIENT_EVIDENCE | Chưa đủ bằng chứng | Kho tài liệu chưa có gì để so. **Không có nghĩa là tuyên bố sai** |

### 3.3 Năm thuộc tính của một tuyên bố

| Thay | Bằng | Ví dụ |
|---|---|---|
| metric | chỉ số | lượng phát thải, điện tiêu thụ |
| value / unit | con số / đơn vị | 12.400 / tấn CO2 tương đương |
| baseline | năm gốc | "giảm 20 % **so với năm 2020**" |
| period | kỳ báo cáo | năm 2024, năm tài chính 2024 |
| scope, boundary | phạm vi | một nhà máy, công ty mẹ hay toàn tập đoàn |
| method | phương pháp tính | |
| trend: decrease / increase / stable | xu hướng: giảm / tăng / giữ nguyên | |

**Phát thải phạm vi 1, 2, 3** (tiếng Anh: Scope 1, 2, 3) được viết kèm nghĩa:
- phạm vi 1 là phát thải trực tiếp;
- phạm vi 2 là phát thải từ năng lượng mua vào;
- phạm vi 3 là phát thải trong chuỗi giá trị.

Không viết "Scope". Lần đầu xuất hiện trên một màn hình thì ghi đủ nghĩa.

### 3.4 Kỹ thuật (trang Cài đặt, thông báo hệ thống)

| Thay | Bằng |
|---|---|
| LLM, mô hình ngôn ngữ lớn | mô hình ngôn ngữ |
| heuristic | quy tắc kinh nghiệm |
| taxonomy | danh mục phân loại |
| OCR | nhận dạng chữ trên bản quét |
| scan (bản) | bản quét |
| BM25, n-gram, lexical | tìm theo từ khoá |
| vector, embedding, semantic | tìm theo nghĩa |
| cross-encoder, reranker | bộ xếp hạng lại |
| stance | quan hệ với tuyên bố (ủng hộ / ngược lại / chỉ liên quan) |
| lexical score / semantic score | độ khớp từ khoá / độ khớp nghĩa |
| threshold τ | ngưỡng |
| offline / cloud / GPU server | ngoại tuyến / có mạng (đám mây) / máy chủ riêng có card đồ hoạ |
| laptop | máy tính xách tay |
| API | máy chủ GreenScan |
| endpoint | địa chỉ máy chủ |
| URL | đường dẫn web |
| tracked changes (DOCX) | đánh dấu sửa đổi |
| rule pack | bộ quy tắc |
| org pack | bộ quy tắc nội bộ |
| rubric | thang chấm |
| gold label | nhãn chuẩn |
| Abstain (lựa chọn của người soát xét) | Chưa kết luận |
| override | ghi đè |
| manifest | phiếu tái lập kết quả |
| JSON / JSONL / Markdown (tệp xuất) | tệp dữ liệu (.json) / nhật ký các bước (.jsonl) / bản văn bản (.md) |
| schema, version | dạng dữ liệu, phiên bản |

### 3.5 Viết tắt tiếng Việt phải viết đủ

| Viết tắt | Viết đủ |
|---|---|
| BCPTBV | báo cáo phát triển bền vững |
| BCTN | báo cáo thường niên |
| BCTC | báo cáo tài chính |
| KNK | khí nhà kính |
| ĐTM | đánh giá tác động môi trường |
| mã CK | mã chứng khoán |
| ESG | môi trường – xã hội – quản trị (ghi "ESG" trong ngoặc ở lần đầu) |

## 4. Giọng văn

- **Câu ngắn, tối đa khoảng 25 từ.** Nói việc người dùng cần làm trước, lý do sau.
- **Trung tính.** Không viết "doanh nghiệp vi phạm", "tẩy xanh", "gian lận". Viết "cần người soát xét xem", "chưa đủ bằng chứng".
- **Không hứa quá mức.** Không viết "chính xác 100 %", "AI hiểu toàn bộ báo cáo".
- **Gọi người dùng là "bạn".** Gọi sản phẩm là "GreenScan" hoặc "máy" khi nói phần việc tự động.

## 5. Khi thêm chữ mới

1. Tra bảng mục 3. Chưa có từ thì thêm vào bảng trước, rồi mới dùng.
2. Giá trị mã hiện ra màn hình thì thêm nhãn vào `frontend/src/lib/labels.js`.
3. Chạy `python tools/check_ui_language.py` trước khi gộp code.
