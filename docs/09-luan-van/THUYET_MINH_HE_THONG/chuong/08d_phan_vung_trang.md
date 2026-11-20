# Chương 12. Phân vùng trang và suy luận trên bảng (17/11/2026)

Chương này mô tả thay đổi lớn cuối cùng trước hạn nộp Vòng 2. Từ bản ngày 18/11, các chương 3–8 đã chạy lại trên mã có phân vùng trang (Ca A `657b68065a37496f`, Ca B `fe38a4515c1148d5`), nên chương này chỉ giữ phần giải thích thay đổi và số so sánh trước – sau. Số trong chương này lấy từ hai phiên chạy ngày 17/11 bằng mã có phân vùng trang: Ca A `3c0f2d7671e444e0`, Ca B `224d4bdfd0394ea9` (99 giây trên laptop không GPU, RAM đỉnh 0,9 GB; một lượt đo trước cùng ngày mất 216 giây); phiên Hòa Phát trong kho demo `efcd9717caef4d7b` cho cùng kết quả.

## 12.1. Vì sao cần

Ngày 17/11, đội nhờ Claude đọc lại ba bộ tài liệu và đối chiếu với đầu ra của hệ thống (nhãn của Claude, chưa có người rà; chi tiết ở `docs/04-data-ai/KIEM_CHUNG_BANG_CLAUDE_2026-11-17.md`). Kết luận chính: **chữ đọc đúng, nhưng cách hiểu trang thì sai**.

- Báo cáo phân bổ trái phiếu xanh của Techcombank (14 trang, nhiều bảng): mọi con số trong bảng phân bổ đều bị bỏ sót. Hệ thống không lấy được số liệu công bố nào và không làm được phép kiểm nào.
- Hòa Phát: chữ ở trang hai cột bị đọc xen giữa hai cột, chữ ở thanh bên dính vào câu, hàng bảng trộn vào câu văn. “7,085” dưới tiêu đề “(Nghìn tấn)” bị hiểu là 7,085 tấn.
- Câu tuyệt đối “hoàn toàn không có nước thải công nghiệp xả ra môi trường” (trang 47) đứng hạng 105. Hệ thống đã tìm thấy bảng nước thải trang 48 nhưng không dùng được, vì bảng chưa thành số liệu có nhãn.

Đội đã thử thêm một mô hình thị giác nhỏ (VLM 2B). Trên CPU nó chậm hơn khoảng 100 lần so với đọc lớp chữ, và còn dời số sang ô bên cạnh. Vì vậy cách sửa là dạy hệ thống hiểu bố cục trang, không phải thay bộ đọc chữ.

## 12.2. Phân vùng trang (`page-regions-v1`)

Mã: `src/quantum_gw/parsers/layout.py`. Mỗi trang được tách thành các vùng có kiểu trước khi bất kỳ bước nào diễn giải nội dung:

1. **Đơn vị chữ.**
   - Trang có lớp chữ: dùng khối và từ của chính tệp PDF. Khối nhiều dòng là một đoạn văn, giữ nguyên thứ tự từ của PDF. Khối một dòng, hoặc khối mà dòng nào cũng kết thúc bằng một con số đứng riêng, được cắt thành từng ô tại khoảng trống rộng hơn một ký tự. Chữ ẩn (bộ kiểm tính toàn vẹn) bị loại như trước.
   - Trang quét: dùng toạ độ từng từ do Tesseract trả về, cùng số dòng của chính Tesseract. Ký tự viền bảng như “|” bị bỏ.
2. **Cột chữ.** Tìm khe dọc mà không dòng hẹp nào cắt qua. Dòng vắt qua khe (tiêu đề) chia trang thành các dải. Trong mỗi dải, đọc hết cột trái rồi mới sang cột phải.
3. **Bảng có kẻ ô.** Dùng `find_tables` của PyMuPDF, qua cùng bộ lọc hình dạng `table-shape-v1` của ngày 16/11.
4. **Bảng không kẻ ô.** Các dòng có nhãn bên trái và con số căn lề phải thẳng hàng. Nhãn được tìm bằng cách đi sang trái từ con số, với giới hạn khoảng cách và chiều cao dòng, để không lấy nhầm chữ của cột bên cạnh. Các con số cùng một cột được nhóm theo mép phải, và mọi ô trong cột nhận cùng một tiêu đề.

Mỗi bảng mang theo **tên bảng, tiêu đề cột, đơn vị** (“(tỷ VND)”, “(Nghìn tấn)”, “Đơn vị:”) và **kỳ**. Tắt bằng biến môi trường `QUANTUM_LAYOUT_REGIONS=off`, khi đó hệ thống đọc trang như trước ngày 17/11.

## 12.3. Đọc số theo cả bảng

- Kiểu dấu phân cách được quyết định một lần cho cả bảng. Ví dụ bảng có “7,085 / 6,982 / 103” là kiểu dấu phẩy hàng nghìn, nên “7,085” là bảy nghìn không trăm tám mươi lăm.
- Đơn vị lấy từ tên bảng hoặc dòng chữ ngay trên bảng. Đơn vị ghi ở tiêu đề một cột chỉ áp cho cột đó: cột “Số lượng khoản vay” không thành tiền.
- Hệ số “nghìn / triệu / tỷ” được nhân vào giá trị: “7,085” dưới “(Nghìn tấn)” thành 7.085.000 tấn.
- Ngày tháng được bỏ trước khi đọc số, nên “24-tháng 12-2024” không bị lấy làm giá trị.

## 12.4. Ô bảng thành số liệu công bố, và ba phép kiểm bảng

Mỗi ô số của bảng trở thành một **số liệu công bố** (`agents/figures.py::_from_table`), nhãn là “nhãn dòng · tiêu đề cột”. Chỉ tiêu được suy từ nhãn dòng, tiêu đề cột, tên bảng hoặc đơn vị. Bảng không còn bị bộ trích tuyên bố đọc như câu văn. Ô không gọi tên chỉ tiêu môi trường nào và không được phép kiểm nào dùng thì không vào danh sách (`keep_material`). Nhờ vậy bảng báo cáo tài chính không làm đầy hàng đợi.

Ba phép kiểm mới (`table_checks`), đều là phép tính tất định:

| Phép kiểm | Nội dung | Khi nào báo “không khớp” |
|---|---|---|
| Cộng lại bảng (`table_sum`) | Một dòng bằng tổng các dòng khác của cùng cột (cùng đơn vị, cùng tiêu đề cột) | Chỉ khi đối chiếu với dòng tổng in sẵn của chính bảng |
| Cộng tỷ trọng (`table_sum` trên cột %) | Các tỷ trọng của một cột cộng ra dòng tổng in sẵn (99,55 + 0,39 + 0,01 + 0,04 + 0,01 = 100 %) | Không bao giờ; tỷ trọng đã làm tròn |
| Cộng chéo giữa các bảng (`page_sum`) | Các dòng của một bảng cộng ra một số ở bảng khác cùng trang | Không bao giờ; chỉ ghi khi khớp |
| Kiểm tỷ lệ (`ratio`) | Tỷ lệ in ra bằng giá trị chia cho dòng tổng cùng đơn vị | Chỉ khi cột phần trăm ghi rõ là tỷ trọng (“tỷ trọng”, “cơ cấu”, “chiếm”) |

Các điều kiện chặt này có lý do: trong lần thử đầu, một tỷ lệ tái sử dụng bị so nhầm với tỷ trọng và bị báo “không khớp”. Hệ thống không được tạo ra lời buộc tội từ một phép chia ngẫu nhiên.

## 12.5. Câu tuyệt đối gặp số liệu (`figure-tension-v1`)

Mã: `agents/prioritizer.py::_figure_tension`. Quy tắc áp khi cả ba điều sau cùng đúng:

1. Câu có dạng phủ định tuyệt đối: “hoàn toàn không”, “không hề”, “không phát sinh / xả / thải … nào”, “bằng 0”.
2. Câu không phải mục tiêu hay cam kết tương lai (“hướng tới phát thải ròng bằng 0” không tính).
3. Trong hồ sơ có một số liệu cùng chủ đề lớn hơn 0. Cùng chủ đề nghĩa là chung cụm từ với câu, và cùng chỉ tiêu hoặc chung ít nhất hai cụm từ.

Khi đó thành phần “bất thường” của điểm ưu tiên được tính đủ 10/10 điểm, kèm lý do viết bằng tiếng Việt, ví dụ: *“Câu khẳng định tuyệt đối, nhưng số liệu “Nước thải hoàn trả lại môi trường sau khi qua hệ thống xử lý nước” trang 48 ghi 4.994 triệu lít (khác 0). Có thể khác phạm vi; cần người xem.”* Lý do này hiện thẳng trên trang hàng đợi, không phải rê chuột mới thấy.

## 12.5b. Gắn cờ thêm bốn kiểu câu không phải tuyên bố (`claim-quality v1.2`)

Sau khi đọc trang theo vùng, hàng đợi Hòa Phát còn 4 câu không phải tuyên bố mà giám khảo sẽ mở trước: một dòng bảng chỉ mục GRI (trang 104), các tiêu đề đọc liền nhau (trang 99), một câu bị cắt ngang (“… giảm phát thải và thúc”, trang 11), một danh sách gạch đầu dòng đọc thành một câu (trang 33). Bộ gắn cờ (`agents/claim_quality.py`) thêm bốn dấu hiệu nhìn thấy được trên chính câu: ký hiệu gạch đầu dòng nằm giữa câu; đơn vị đứng trước con số hai lần (“Tấn 933.876 … Tấn 23.474.479”); cùng sáu từ lặp lại và lần sau bắt đầu như một tiêu đề, không có dấu câu ở giữa; câu không có dấu kết thúc, không có số, và từ cuối treo sau “và / hoặc”. Như các luật cũ, câu bị gắn cờ **không bị xoá**: giữ kết luận, vẫn nằm trong danh sách tuyên bố kèm lý do, chỉ không vào hàng đợi và không được chấm rủi ro.

Đo một lần trên các bộ nhãn có sẵn: GS-Eval v2 (200 câu) bắt 17/67 câu không phải tuyên bố (trước 14/67), gắn nhầm câu thật giữ nguyên 1/133; GS-Claims v1 (150 câu) không đổi (11/92 và 6/58). Trên 293 câu duy nhất của các phiên từ 15/11, luật mới gắn cờ thêm 12 câu, đọc lại cả 12 đều là chữ dính bố cục, danh sách hoặc mảnh câu. Một bản đầu của luật lặp từ gắn nhầm 2 câu thật dài và đã được siết lại trước khi dùng. Ghi trong `configs/measurement_decisions.yaml`, khối `claim_quality_v1_2`.

Quy tắc **không đổi kết luận** của tuyên bố. Hai con số có thể nói về hai phạm vi khác nhau (khu liên hợp thép so với toàn tập đoàn; nước làm mát so với nước thải công nghiệp), nên việc quyết định thuộc về người soát.

## 12.6. Kết quả trước và sau (chế độ chỉ luật, cùng bộ tài liệu)

| | Trước (16/11) | Sau (17/11) |
|---|---|---|
| Techcombank: số liệu công bố / phép kiểm | 0 / 0 | 6 / 2: 399 + 51 = 450 tỷ VND; 399/450 = 88,67% so với 89% công bố |
| Bản quét giả lập trang 8 Techcombank (chỉ ảnh, đọc qua Tesseract) | – | Ra đủ ba bảng và cùng hai phép kiểm |
| Hòa Phát: tuyên bố | 171 | 186 |
| Hòa Phát: số liệu công bố / phép kiểm số liệu | 15 / 1 | 55 / 15, không phép nào “không khớp” |
| Hòa Phát: hàng đợi | 7 trên 186 mục | 9 trên 241 mục (8 tuyên bố, 1 số liệu); 12 câu bị gắn cờ, để ngoài hàng đợi |
| Hòa Phát: câu “hoàn toàn không có nước thải công nghiệp xả ra môi trường” | Hạng 105, ngoài hàng đợi | Hạng 6, trong hàng đợi, lý do nêu bảng trang 48 |
| Hòa Phát: “không ghi nhận vi phạm hay sự cố nào…” | Không được trích | Được trích |
| Kiểm thử tự động | 773 | 784 |

Một số phép kiểm trên Hòa Phát:

- Bảng nước trang 48: 4.994 + 41.334 = 46.328 triệu lít, đúng dòng “Nước khai thác”.
- Bảng chất thải rắn trang 50: 6.838 + 247 = 7.085 nghìn tấn, đúng dòng tổng; cũng khớp với số ở bảng khác cùng trang.
- Bảng khí nhà kính theo ngành trang 39: 23.369.500 + 90.846 + 2.836 + 9.666 + 1.631 = 23.474.479 tCO₂e, so với dòng tổng 23.474.480 (lệch 1, trong sai số làm tròn).
- Năm tỷ trọng theo ngành ở cùng bảng: 23.369.500 / 23.474.480 = 99,55%, đúng số in; 0,39%, 0,01%, 0,04%, 0,01% cũng đúng; năm tỷ trọng cộng lại đúng 100%.
- Trang 51: hai cột của bảng chất thải theo khu (phát sinh, xử lý) đều cộng ra dòng tổng trong sai số làm tròn.

Chất lượng chữ đọc ra cũng khác. Claude đọc nhanh 25 câu đầu danh sách ở mỗi bên (chưa có người rà): trong số câu bị bỏ, khoảng 22 là rác (hàng bảng trộn vào câu, chữ thanh bên dính vào, hai cột đọc xen); trong số câu mới, khoảng 19 là câu sạch.

Kết luận của các bộ đo dựng trên văn bản (GS-Bench, GS-Mutation, GS-Eval v2) không đổi, vì các bộ này không đi qua bước đọc PDF. Chi tiết ở mục 12.8.

## 12.7. Giới hạn còn lại

1. Danh sách đọc liền, dòng bảng và câu bị cắt có “và / hoặc” ở cuối đã được gắn cờ (mục 12.5b). Nhãn sơ đồ ngắn (“Bùn thải từ các trạm xử lý nước thải”), câu bị cắt ở chỗ khác và câu bối cảnh chung vẫn có thể thành tuyên bố; hàng đợi Hòa Phát còn một câu bối cảnh như vậy (mục 7, đã có nhãn “có thể là câu giải thích chung”).
2. Trong ô có cả chữ lẫn số, hệ thống chỉ lấy số có từ 3 chữ số trở lên hoặc số phần trăm. Vì vậy “4 khoản vay” và số xe không vào danh sách.
3. Trên bản quét, một dòng đứng lẻ (ví dụ dòng 0%) chưa thành bảng nên bị sót.
4. Biểu đồ và trang chỉ có hình vẫn chưa đọc được. Đây là chỗ một mô hình thị giác chạy trên GPU có ích; trên CPU thì quá chậm (mục 12.1).
5. Nhãn “ủng hộ một phần” vẫn chưa phân biệt được câu nào chắc hơn câu nào. Hai trục ở Chương 11 vẫn là cách đọc nên dùng.

## 12.8. Kiểm lại các bộ đo

- GS-Bench v1.1: so từng ca với `experiments/AG-0/out/rules.jsonl`, **0/453 nhãn của luật đổi**.
- Bốn vụ có phán quyết (`quantum-agent evaluate-real`): **4/4 đúng kết luận**, không đổi.
- **784 kiểm thử tự động đều qua** (thêm 9 kiểm thử ở `tests/test_page_regions.py` và 2 ở `tests/test_claim_quality_v12.py`).
- GS-Mutation và GS-Eval v2 dựng trên văn bản đã lưu, không đi qua bước đọc PDF, nên không chạy lại.
- Thời gian: Ca B mất 99 giây khi máy rảnh, 216 giây ở một lượt đo trước cùng ngày (bản 16/11: 115–185 giây). Phần tăng thêm chủ yếu do dò bảng kẻ ô trên từng trang (khoảng 0,3–0,4 giây mỗi trang). RAM đỉnh giảm từ 1,7 GB xuống 0,9 GB vì không còn dùng pdfplumber để đọc bảng.

Chi tiết và quyết định: D-2026-11-17-02 trong `docs/00-project/DECISIONS_LOG.md`.
