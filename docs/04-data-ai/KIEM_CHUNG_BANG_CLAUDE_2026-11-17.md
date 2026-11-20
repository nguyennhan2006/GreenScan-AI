# Claude đọc lại ba bộ tài liệu và so với hệ thống (17/11/2026)

Mục đích: xem hệ thống hiểu tài liệu có đúng không, và điểm yếu lớn nằm ở đâu.

**Cách làm.** Claude (mô hình `claude-fable-5-2`) tự đọc văn bản gốc, tự nhận định từng câu, rồi so với kết quả của hệ thống ở chế độ chỉ luật. Đây là nhãn của một mô hình, chưa có người rà [ĐÃ THỰC NGHIỆM, nhãn của Claude]. Nhãn từng câu: `benchmark/claude_spotcheck_2026-11-17/labels.jsonl` (67 câu) và `missed.jsonl` (14 câu bị bỏ sót).

| Bộ | Tài liệu | Claude đọc | Hệ thống ra |
|---|---|---|---|
| 1 | Công ty Minh Họa (dữ liệu mẫu, 3 tệp chữ thuần) | toàn bộ | 5 tuyên bố |
| 2 | Techcombank, Báo cáo sau phát hành trái phiếu xanh 2024 (thật, 14 trang, nhiều bảng) | toàn bộ 14 trang | 35 tuyên bố |
| 3 | Hòa Phát, BCPTBV 2025 + BCTN 2024 (thật, 264 trang) | mẫu 27 trên 171 tuyên bố (7 mục hàng đợi, 5 mẫu ngẫu nhiên của hệ thống, 15 câu rút ngẫu nhiên), cộng đọc trọn trang 47, 48, 50 | 171 tuyên bố |

## 1. Kết luận ngắn

- **Văn bản sạch, câu có số:** hệ thống hiểu đúng. Bộ 1: lấy đủ 5/5 câu, kết luận 5/5 trùng với Claude, phép tính hiện đúng.
- **Tài liệu thật có bảng và dàn trang:** hệ thống hiểu kém hơn nhiều. Nó lấy nhầm tiêu đề, mục lục, mô tả phương pháp làm “tuyên bố”, và bỏ sót phần lớn số liệu cốt lõi nằm trong bảng.
- **Không thấy kết luận “mâu thuẫn” sai nào** trong cả ba bộ. Rủi ro hiện nay không phải vu oan, mà là **bỏ lọt và làm người soát tốn công vào câu vô ích**.

## 2. Số đếm

### Hệ thống lấy ra cái gì

| Loại (theo Claude) | Bộ 1 | Bộ 2 Techcombank | Bộ 3 Hòa Phát (mẫu 27) |
|---|---|---|---|
| Tuyên bố kiểm được | 4 | 4 | 11 |
| Câu mơ hồ, cam kết chung | 1 | 8 | 2 |
| Diễn giải chung về ngành, số liệu trích của bên khác | 0 | 3 | 5 |
| Phương pháp, quy trình, giới hạn của chính báo cáo | 0 | 13 | 0 |
| Tiêu đề, mục lục, ô bảng dính nhau, nửa câu | 0 | 6 | 9 |
| Không thuộc môi trường | 0 | 1 | 0 |
| **Tổng** | 5 | 35 | 27 |

Ở bộ 3, riêng 15 câu rút ngẫu nhiên ngoài hàng đợi có 6 câu là mảnh dàn trang. Mẫu nhỏ, chỉ nên đọc là “đáng kể”, không suy ra tỉ lệ cho cả 171 câu.

### Hệ thống bỏ sót cái gì

| Bộ | Câu quan trọng theo Claude | Hệ thống lấy được |
|---|---|---|
| 2 Techcombank | 13 | 3 (điện mặt trời 30.709,8 kWp; “ngân hàng tư nhân đầu tiên”; kiểm toán UHY) |
| 3 Hòa Phát, ba trang đọc trọn | 13 | 9 |

Mười câu Techcombank bị bỏ sót gồm đúng phần lõi của một báo cáo phân bổ: phát hành 450 tỷ; đã phân bổ 399 tỷ, bằng 89%; còn 51 tỷ chưa phân bổ; tái tài trợ 0%; S&P xếp “Medium Green”; 306.356 tấn CO2 tương đương tránh được; 97.378 ô tô điện đưa ra thị trường. Hệ thống ghi “số liệu công bố: 0” cho tài liệu này.

### Hàng đợi đưa cái gì lên đầu

| Bộ | Số mục tuyên bố trong hàng đợi | Trong đó tuyên bố kiểm được |
|---|---|---|
| 1 | 3 | 3 |
| 2 Techcombank | 6 | 0 (3 câu mơ hồ, 1 tiêu đề bảng, 1 diễn giải chung, 1 ghi chú giới hạn) |
| 3 Hòa Phát | 7 | 6 (mục thứ 3 là tiêu đề dính nhau) |

## 3. Điểm yếu lớn, xếp theo mức ảnh hưởng

### 3.1 Không đọc được số liệu trong bảng thành tuyên bố

Bảng phân bổ vốn của Techcombank (trang 8) và bảng tác động (trang 12) có được đưa vào kho bằng chứng, nhưng không câu nào trong đó thành tuyên bố hay “số liệu công bố”. Với loại tài liệu này, bảng chính là nội dung.

### 3.2 Hàng đợi ưu tiên chủ đề và độ mơ hồ, chưa ưu tiên “kiểm được và có chỗ vênh”

Ví dụ rõ nhất, Hòa Phát trang 47: *“Các khu liên hợp hoàn toàn không có nước thải công nghiệp xả ra môi trường.”* Trang 48 và bảng GRI trang 105 ghi 4.994 triệu lít nước thải hoàn trả môi trường trên toàn Tập đoàn. Hệ thống **tìm đúng** cả hai đoạn này, nhưng ghi “cùng chủ đề, chưa đủ số liệu” và xếp câu ở hạng 105 trên 186, ngoài hàng đợi. Đây chưa chắc là mâu thuẫn (phạm vi khác nhau: khu liên hợp và toàn Tập đoàn), nhưng đúng là loại câu một kiểm toán viên muốn thấy đầu tiên.

Hai câu tuyệt đối khác bị bỏ sót hẳn: *“không ghi nhận vi phạm hay sự cố nào liên quan đến nước thải”* (trang 48) và *“xử lý toàn bộ lượng bụi và bùn chứa kẽm”* (trang 50).

### 3.3 So số mà chưa chắc là cùng một đại lượng

| Chỗ | Hệ thống đọc | Thực tế |
|---|---|---|
| Hòa Phát tr. 37 | “Số liệu khớp: 65 ≈ 70”, đoạn ủng hộ | 65% là hàm lượng sắt của quặng; 70% là tỉ trọng sản lượng thép toàn cầu |
| Hòa Phát tr. 50 | 7,085 nghìn tấn chất thải → 7,085 tấn; cùng bảng, 247 giữ là 247 | dấu phẩy ở đây là dấu phân cách hàng nghìn; đơn vị “nghìn tấn” bị bỏ, lệch một triệu lần |
| Techcombank | số thứ tự (7), (8); “tháng 12”; số 0 trong “phát thải ròng bằng 0” → giá trị của tuyên bố | không phải số liệu |
| Techcombank, Hòa Phát | năm trong tên văn bản (2021, 2022, 2006, 2050) → kỳ báo cáo, năm gốc | năm của văn bản được trích |
| Bộ 1 | số liệu 112.000 tCO2e ghi kỳ 2023 | kỳ 2024 |

Các chỗ khớp sai chưa thành kết luận “được ủng hộ” vì luật chặn tài liệu của chính doanh nghiệp. Nếu đoạn đó đến từ một nguồn được coi là độc lập thì cơ chế này sẽ cho ra “được ủng hộ” sai.

### 3.4 Nhãn kết luận gần như không phân biệt gì trên tài liệu thật

Hòa Phát: 171/171 “Ủng hộ một phần”. Techcombank: 34/35, kể cả dòng mục lục. Người đọc không rút được thông tin nào từ nhãn; mọi thứ dồn vào thứ tự hàng đợi, mà thứ tự lại yếu ở mục 3.2.

Khi bật mô hình (bộ 1), câu “doanh nghiệp xanh hàng đầu” thành “Ủng hộ một phần”. Không có đoạn nào ủng hộ câu này; mô hình chỉ nghi nó mâu thuẫn với một quyết định xử phạt. Nhãn hiện tại nói ngược ý đó.

### 3.5 Tín hiệu sai ở từng đoạn bằng chứng

- **“Xu hướng ngược với tuyên bố”** (Hòa Phát, 2 trong 27 câu mẫu): hệ thống so chữ “gia tăng tỷ lệ tái sử dụng” với chữ “giảm phát thải” ở đoạn khác. Hai chỉ số khác nhau.
- **“Ủng hộ”** vì có chữ “chứng nhận” (Hòa Phát tr. 38 so với tr. 86): đoạn kia nói về chứng nhận chất lượng, không nói về carbon.
- **“Chưa đủ số liệu”** trong khi đoạn bằng chứng có số: câu “tự chủ điện năng rất cao” có ngay đoạn BCTN tr. 86 ghi “tự chủ trên 90% lượng điện”. Hệ thống chưa nối được chữ định tính với con số.

### 3.6 Dàn trang nhiều cột

Câu bị cắt đôi, hai cột đọc xen nhau, tiêu đề dính vào câu, số trang dính vào cuối câu. Cờ “có thể không phải tuyên bố” bắt được 7/35 ở Techcombank và 3/171 ở Hòa Phát, và đẩy chúng xuống cuối. Còn sót những mảnh không bị gắn cờ, trong đó có mục đang nằm trong hàng đợi của cả hai tài liệu.

## 4. Chỗ hệ thống làm đúng

- Câu có số và có đoạn đối chiếu cùng đại lượng: tính đúng, hiện phép tính (giảm 30% so với tăng 12%; 50% so với 8%; “hoàn toàn” so với 320/500).
- Phép cộng bảng khí nhà kính Hòa Phát trang 39: 22.540.603 + 933.876 khớp tổng công bố.
- “Hơn 99% phát thải” khớp đúng với trang 40.
- Truy xuất thường tìm đúng đoạn (bảng nước thải, đoạn “tự chủ trên 90%”). Chỗ hỏng là bước đọc đoạn đó.
- Phân biệt được “98% ở Dung Quất” với “tái chế 100%” là khác ranh giới.
- Luật chặn tài liệu tự xác nhận đã ngăn mọi chỗ khớp sai ở mục 3.3 và 3.5 thành kết luận sai.

## 5. Giới hạn của phép kiểm này

- Người gán nhãn là một mô hình ngôn ngữ, đọc một lượt, có nhìn thấy kết quả của hệ thống khi gán nhãn. Cần người rà trước khi dùng làm số đo.
- Hòa Phát chỉ đọc mẫu 27 câu và 3 trang; không suy ra tỉ lệ cho cả báo cáo.
- Bộ 2 chỉ có một tài liệu, không có tài liệu đối chiếu, nên không thử được nhánh “nguồn độc lập”.
- Chỉ so chế độ chỉ luật (riêng bộ 1 có xem thêm phiên bật mô hình).

## 6. Hướng sửa, theo thứ tự lợi ích trên công sức (chưa làm)

1. **Đọc bảng thành số liệu công bố có nhãn dòng, đơn vị của bảng và kỳ**, rồi cho bảng phân bổ vốn chạy phép kiểm cộng và chia như bảng khí nhà kính (399 + 51 = 450; 399/450 = 89%).
2. **Thêm tín hiệu “câu tuyệt đối” vào điểm ưu tiên** (“hoàn toàn không”, “không … nào”, “toàn bộ”, “100%”), nhất là khi kho có số liệu cùng chủ đề.
3. **Khi so số, bắt buộc cùng đại lượng**: cùng danh từ chỉ số hoặc cùng đơn vị cụ thể, không chỉ cùng ký hiệu %.
4. **Đọc số theo ngữ cảnh bảng**: nếu tiêu đề ghi “nghìn tấn” và các ô khác là số nguyên thì “7,085” là bảy nghìn không trăm tám mươi lăm.
5. **Bỏ số thứ tự, tháng, năm của văn bản được trích** khỏi giá trị, kỳ và năm gốc.
6. **Bật mô hình cho đúng hai việc nó làm tốt hơn luật**: lọc câu không phải tuyên bố (tiêu đề, phương pháp), và nối câu định tính với đoạn có số. Bộ 2 và bộ 3 là bài thử sẵn cho việc này.
7. **Tách nhãn “Ủng hộ một phần”** thành ít nhất hai ý: “chỉ có nguồn của chính doanh nghiệp” và “có dấu hiệu trái chiều, cần người xem”.

## 7. Có nên thêm một mô hình thị giác (VLM) nhẹ để đọc trang? Số đo tối 17/11

Người dùng hỏi có nên thêm một VLM nhẹ để nâng khả năng đọc. Đo trên laptop i7-1355U, 16 GB, không GPU (Ollama nâng từ 0.13.5 lên 0.40.16 để chạy Qwen3.5), trang 8 Techcombank (ba bảng phân bổ vốn):

| Cách đọc | Thời gian / trang | Số đọc đúng | Đúng hàng, đúng cột | Ghi chú |
|---|---|---|---|---|
| Lớp chữ PDF + pdfplumber (đang dùng) | < 1 s | 15/15 | đúng cả ba bảng | 399, 450, 89%, 51, 0% đều đúng ô |
| Qwen3-VL 2B, ảnh 1400 px | 818 s | 0 | – | hết 2.048 token mà không trả chữ nào |
| Qwen3.5 2B, ảnh 1000 px, tắt suy nghĩ | 113 s | 15/15, không bịa số | **sai một dòng**: “51 | 0%” (51 dời sang cột tỷ lệ, 0% lấy từ dòng dưới) | đổi nghĩa vài chữ: “chênh lệch” → “chính sách”, “tái tài trợ” → “tài tại trị” |
| Tesseract trên bản quét giả lập (150 dpi, nghiêng 0,6°, JPEG) | vài giây | đủ, chỉ thiếu số trang | giữ đúng hàng | sai dấu ở vài chữ |

Hòa Phát trang 50 và trang 9 cũng vậy: lớp chữ có đúng “7,085”, “(Nghìn tấn)”, “Tự chủ 90% nhu cầu điện…”.

**Kết luận:** sáu điểm yếu ở mục 3 không do đọc sai chữ mà do bước diễn giải sau khi đọc: hàng bảng không thành số liệu (mục 3.1), khối chữ xếp theo tung độ nên hai cột đọc xen nhau (`parsers/documents.py`, dòng sắp `blocks`), dấu phẩy hàng nghìn và đơn vị ở tiêu đề bảng, điểm ưu tiên. Một VLM 2B trên CPU chậm hơn khoảng 100 lần và còn dời ô bảng, nên không phải đòn bẩy chính. VLM chỉ đáng dùng cho trang không có lớp chữ hoặc số nằm trong hình vẽ, chạy trên GPU và đối chiếu số với Tesseract. Mô hình đã tải sẵn trên laptop: `qwen3.5:2b`, `qwen3-vl:2b` (có thể xoá bản này, 1,9 GB).

## 8. Phân vùng trang và suy luận trên bảng (`page-regions-v1`, `figure-tension-v1`), tối 17/11

Người dùng đề nghị một cách phân vùng giúp agent hiểu bảng trong PDF quét và các cụm số liệu đứng riêng, để suy luận tốt hơn. Đã làm, không dùng mô hình:

1. **Phân vùng** (`src/quantum_gw/parsers/layout.py`). Mỗi trang thành các vùng có kiểu:
   - chữ thường, đọc theo thứ tự cột: tìm khe dọc không dòng hẹp nào cắt qua; dòng vắt qua khe (tiêu đề) chia trang thành dải;
   - bảng kẻ ô (`find_tables` của PyMuPDF, cùng bộ lọc hình dạng `table-shape-v1`);
   - bảng không kẻ ô: các dòng có nhãn bên trái và con số căn lề phải thẳng hàng.

   Mỗi bảng có tên, tiêu đề cột, đơn vị (“(tỷ VND)”, “(Nghìn tấn)”, “Đơn vị:”) và kỳ. Trang có lớp chữ dùng khối và từ của PDF (bỏ chữ ẩn như cũ); trang quét dùng toạ độ từng từ mà Tesseract trả về, kèm số dòng của chính Tesseract.
2. **Đọc số theo bảng.** Kiểu dấu phân cách quyết định một lần cho cả bảng (“7,085 / 6,982 / 103” là kiểu dấu phẩy hàng nghìn). Đơn vị ở tiêu đề cột chỉ áp cho cột đó (“Số lượng khoản vay” không thành tiền). Ngày tháng không bị đọc thành số.
3. **Ô bảng thành số liệu công bố** (`agents/figures.py::_from_table`): nhãn = nhãn dòng · tiêu đề cột. Bảng không còn bị bộ trích tuyên bố đọc như câu văn. Ô không gọi tên chỉ tiêu và không được phép kiểm nào dùng thì bị loại (`keep_material`), để bảng báo cáo tài chính không làm đầy hàng đợi.
4. **Ba phép kiểm bảng** (`table_checks`):
   - `table_sum`: một dòng bằng tổng các dòng khác của cùng cột;
   - `page_sum`: các dòng của một bảng cộng ra một số ở bảng khác cùng trang;
   - `ratio`: tỷ lệ in ra bằng giá trị chia cho dòng tổng.

   Chỉ báo “không khớp” khi đối chiếu với dòng tổng của chính bảng, và với tỷ lệ chỉ khi cột ghi rõ là tỷ trọng.
5. **Câu tuyệt đối gặp số liệu** (`agents/prioritizer.py::_figure_tension`). Câu phủ định tuyệt đối (“hoàn toàn không có…”, “không phát sinh … nào”) gặp số liệu cùng chủ đề lớn hơn 0 thì thành phần “bất thường” của điểm ưu tiên được tính đủ 10 điểm, kèm lý do “có thể khác phạm vi; cần người xem”. Không áp cho câu mục tiêu (“hướng tới phát thải ròng bằng 0”). Không bao giờ là kết luận.

### Số đo (chế độ chỉ luật, cùng bộ tài liệu)

| | Trước | Sau |
|---|---|---|
| Techcombank: số liệu công bố / phép kiểm | 0 / 0 | 6 / 2: 399 + 51 = 450 tỷ VND; 399 / 450 = 88,67 % so với 89 % công bố |
| Bản quét giả lập trang 8 Techcombank (chỉ ảnh, qua Tesseract) | – | ra đủ ba bảng, cùng hai phép kiểm |
| Hòa Phát: phép kiểm số liệu | 1 (cộng phạm vi 1 + 2) | 14, không có “không khớp”: bảng nước 4.994 + 41.334 = 46.328 triệu lít; chất thải 6.838 + 247 = 7.085 nghìn tấn; trang 51 cả hai cột; phát thải theo ngành và năm tỷ trọng (99,55 %, 0,39 %…) |
| Hòa Phát: câu “hoàn toàn không có nước thải công nghiệp xả ra môi trường” | hạng 105, ngoài hàng đợi | hạng 7, trong hàng đợi, lý do ghi bảng 4.994 triệu lít trang 48 |
| Hòa Phát: “không ghi nhận vi phạm hay sự cố nào…” | không được trích | được trích |
| Hòa Phát: 25 câu đầu danh sách trong số các câu bị bỏ | khoảng 22 là rác (hàng bảng trộn, chữ ở thanh bên dính vào câu, hai cột xen) | – |
| Hòa Phát: 25 câu đầu danh sách trong số các câu mới | – | khoảng 19 câu sạch; còn nhãn sơ đồ và câu bị cắt ngang trang |

Đếm rác và câu sạch là Claude đọc nhanh danh sách, chưa có người rà.

### Còn lại
- Câu cắt ngang trang, nhãn sơ đồ ngắn (“Bùn thải từ các trạm xử lý nước thải”) vẫn thành tuyên bố; cờ “có thể không phải tuyên bố” chưa bắt loại này.
- Ô có chữ lẫn số chỉ lấy số có từ 3 chữ số trở lên hoặc %, nên “4 khoản vay” và số xe (không gọi tên chỉ tiêu môi trường) không vào danh sách.
- Dòng 0 % trên bản quét chưa lấy được (một dòng lẻ không thành bảng).
- Nhãn “Ủng hộ một phần” vẫn chưa phân biệt (điểm yếu 3.4), chưa sửa.
- Số tuyên bố và hàng đợi của Hòa Phát đổi so với bản nộp, nên báo cáo, slide, video và kho demo vẫn mang số cũ.
