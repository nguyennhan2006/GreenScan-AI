# Chương 6. Thảo luận, hạn chế và hướng phát triển

Chương này trả lời ba câu hỏi: kết quả ở Chương 5 nói gì về cách tiếp cận "mô hình đọc, quy tắc quyết định, con người duyệt"; vì sao cùng một hệ thống lại an toàn tuyệt đối trên ca dựng nhưng sai nhiều trên báo cáo thật; và cần làm gì tiếp, theo thứ tự nào.

## 6.1 Diễn giải tổng thể: bảo đảm thiết kế đứng vững, phán đoán thì chưa

Kết quả chia thành hai nhóm rõ rệt.

**Nhóm thứ nhất là các bảo đảm được viết thành mã.** Chúng đứng vững trên mọi tập đã đo:
- gợi ý sửa không thêm số nào (0/527);
- quy tắc nội bộ không đổi kết luận kiểm chứng, đúng 45/45 ca an toàn;
- chế độ ngoại tuyến không mở kết nối nào ra ngoài;
- mọi đoạn bằng chứng của tài liệu PDF đều có tên tài liệu và trang;
- không lời giải thích nào quá 80 từ.

Đây là những tính chất **tất định**: chúng không phụ thuộc vào việc hệ thống hiểu đúng câu, chỉ phụ thuộc vào việc mã chặn đúng chỗ. Chúng cũng là những tính chất quan trọng nhất với một công cụ dùng trong kiểm toán, vì chúng giới hạn thiệt hại khi phán đoán sai.

**Nhóm thứ hai là chất lượng phán đoán.** Nhóm này yếu trên báo cáo thật:
- CONTRADICTED đúng 3/38 trước khi sửa; sau chốt chặn mâu thuẫn ngày 05/11 là 3/4, n quá nhỏ để kết luận về độ chính xác;
- SUPPORTED đúng 0/5;
- điểm rủi ro tương quan ρ = 0,23 (0,39 sau chốt chặn) với điểm đồng thuận của hai lượt nhãn;
- lời giải thích của các kết luận dứt khoát trung thực dưới 10 %.

Khi hệ thống **dừng phán đoán** thì khác: với PARTIALLY_SUPPORTED, lời giải thích trung thực 0,95; với INSUFFICIENT_EVIDENCE, lời giải thích chỉ ra việc cần bổ sung 0,98.

Hai nhóm này không mâu thuẫn mà bổ sung cho nhau. Nguyên lý của GreenScan đặt cược rằng khi quy tắc tất định còn yếu, hệ thống sẽ **nhường người** thay vì phán bừa. Phần lớn đúng như vậy: 88 % tuyên bố được xếp "khớp một phần", 1 006/1 138. Chỗ đặt cược thua là **hai đường tắt** cho phép quy tắc ra kết luận dứt khoát mà không đủ điều kiện:
- **luật từ phủ định**: một từ như "vi phạm" trong đoạn bằng chứng là đủ để bác bỏ;
- **so số khi "so sánh được" chỉ được kiểm bằng đơn vị và chiều**, không kiểm cùng đối tượng.

Cả hai đường đều được viết để tăng độ phủ, và cả hai đều vượt qua bộ kiểm hiện có, vì bộ kiểm (47 bẫy kết luận, GS-Bench) không chứa đúng loại câu gây lỗi.

## 6.2 Vì sao an toàn trên ca dựng nhưng sai trên câu thật

GS-Bench dựng tuyên bố từ **một ô bảng** (chỉ số, giá trị, đơn vị, kỳ, phạm vi), rồi gây nhiễu có kiểm soát. Trên tập này, luật không kết luận sai lần nào, kể cả trên 87 ca ngoài mẫu (v1.3). Kết quả đó đúng, nhưng chỉ đo một câu hỏi hẹp: *khi đã biết tuyên bố và bằng chứng nói về cùng một con số, hệ thống có so sánh đúng không?*

Báo cáo thật đặt ba câu hỏi mà GS-Bench không đặt:
1. **Câu này có phải tuyên bố không?** 30 % câu được trích là mảnh bảng, mục lục, chân trang.
2. **Đoạn bằng chứng có nói về cùng đối tượng không?** Một trang báo cáo bền vững thường liệt kê nhiều sáng kiến cùng đơn vị (tấn, %, m³), như ca khay giấy 23 tấn và lót PET 14 tấn.
3. **Từ phủ định trong đoạn có phủ định chính tuyên bố không?** "Không ghi nhận trường hợp nào vi phạm" là một câu tốt về doanh nghiệp, không phải bằng chứng trái chiều.

Bài học về phương pháp: **một bộ đo có đáp án theo cấu trúc là cần nhưng không đủ.** Nó cho phép kiểm từng tầng và đăng ký trước, như đội đã làm với AG-0 → AG-2. Nhưng nó đo tầng so sánh trong điều kiện đã cô lập. GS-Eval v2, lấy câu thật từ lượt chạy thật, mới đo được cả chuỗi. Hai số "0 vu oan trên ca dựng" và "35 CONTRADICTED sai trên 146 câu thật" phải luôn được nói cùng nhau. Đây là thay đổi quan trọng nhất trong cách đội trình bày kết quả.

Phân tích cũng cho thấy các thí nghiệm AG đi đúng hướng:
- Bộ đọc IR của AG-1 cùng `irlib.ground()` buộc số mà mô hình đọc phải khớp với câu gốc. Thêm chiều `segment` (đối tượng) như AG-3 đề xuất là đúng thuốc cho 13 ca so khác đối tượng.
- Chính sách hai đường của AG-2 ("luật + 4B, bỏ phiếu S đơn độc của luật") đã cho 0 kết luận sai trên 162 ca. Chính sách này cũng sẽ loại phần lớn kết luận dứt khoát dựa trên một đường duy nhất.

Điều còn thiếu là chạy các cấu hình đó trên GS-Eval v2, tức trên câu thật.

## 6.3 Bộ nhớ chuẩn và lớp quy tắc của người dùng

Yêu cầu sản phẩm đặt ra là: logic được dựng sẵn với bộ nhớ chuẩn, người dùng chỉ thêm quy tắc, bộ luật hoặc tài liệu nội bộ, và hệ thống phải hiểu chúng trước khi trả kết quả. Thiết kế org pack trả lời yêu cầu này bằng bốn tầng nhớ: lõi, tổ chức, phiên, phản hồi. Quy tắc theo thứ bậc cố định, với `precedence: below_law`. Có ba lựa chọn có chủ đích:
1. **Quy tắc là dữ liệu có cấu trúc, không phải văn bản để mô hình diễn giải.** Mọi điều kiện thuộc một kiểu kiểm đã biết. Kiểu lạ làm cả bộ bị từ chối khi nạp (fail closed).
2. **Tài liệu nội bộ chỉ để dẫn chiếu.** Không mô hình nào đọc tài liệu nội bộ để ra quyết định, nên câu tiêm lệnh trong tài liệu không có đường tác động. 11/11 ca tiêm lệnh xác nhận điều này.
3. **Quy tắc nội bộ không có quyền đổi kết luận.** Chúng chỉ sinh phát hiện riêng và nâng ưu tiên. Giá trị `on_fail` chỉ có `flag_for_review` và `raise_priority`.

Cái giá của ba lựa chọn này là **độ linh hoạt**. 13/237 lỗi của engine đều đến từ việc diễn đạt quy tắc bằng chuỗi con và nhãn loại cố định:
- 8 ca loại tuyên bố do bộ trích gán không khớp `claim_types`;
- 2 ca `when` thiếu từ đồng nghĩa;
- 3 ca `numeric_threshold` xét mọi số trong đoạn.

Thêm vào đó, đầu–cuối giảm từ 0,945 xuống 0,907 vì bộ trích luật lấy thuộc tính sai.

Câu hỏi tự nhiên là: có nên cho một mô hình ngôn ngữ đọc tài liệu nội bộ và tự áp dụng không? Kết quả ở đây ủng hộ một đường giữa, giống vòng đời của gói luật pháp lý (`draft → duyệt → test → nâng phiên bản`):
- mô hình **soạn** quy tắc có cấu trúc từ tài liệu nội bộ;
- người của tổ chức duyệt;
- `org-validate` và `org-preview` kiểm;
- chỉ sau đó quy tắc mới được áp.

Như vậy giữ được tính chất chống tiêm lệnh và truy vết, trong khi gánh nặng viết YAML chuyển từ người dùng sang mô hình.

## 6.4 Đo lường khi thiếu nhãn người

Tới ngày viết, GreenScan vẫn chưa có nhãn người cho kết luận: 0/88 cặp, 0/79 câu. Luận văn dùng ba lớp bằng chứng thay thế, mỗi lớp có giới hạn riêng:
- **GS-Bench:** đáp án theo cấu trúc, không cần người, nhưng chỉ đo tầng so sánh.
- **GS-Eval v2:** nhãn Claude theo hướng dẫn viết trước, hai lượt mù và phân xử, kiểm định đối nghịch, tác giả đọc lại. Đồng thuận hai lượt (Spearman 0,73, QWK dải 0,75) là **trần lạc quan**, vì cả hai lượt cùng một họ mô hình. Khoảng cách giữa hệ thống và trần này (ρ 0,23 so với 0,73) quá lớn để là sản phẩm phụ của nhãn.
- **Kiểm tất định:** số không có nguồn, cấu trúc nhãn, UX lint. Lớp này không cần tin người gán nhãn.

Kết luận về phương pháp: với một hệ thống dùng trong kiểm toán, các **tính chất an toàn** nên được chứng minh bằng kiểm tất định và test bất biến, còn **chất lượng phán đoán** cần nhãn người. Nhãn Claude là cách nhanh để tìm lỗi lớn; lỗi CONTRADICTED là ví dụ, được tìm ra trong một ngày. Nó không thay được con số cuối cùng trên nhãn người.

## 6.5 Đe doạ tính hợp lệ

| Loại | Đe doạ | Cách giảm đã làm | Còn lại |
|---|---|---|---|
| Nội tại | Người gán nhãn và người chấm lời giải thích cùng họ mô hình Claude | Hướng dẫn viết trước; không xem đầu ra hệ thống; hai lượt mù; kiểm định đối nghịch; bộ kiểm tất định | Thiên lệch chung của họ mô hình; Nhân chưa đọc lại hết |
| Nội tại | Người gán nhãn chỉ thấy 3 đoạn, mỗi đoạn ≤ 900 ký tự | Kiểm 5 ca CONTRADICTED: người gán nhãn thấy đủ cặp số bị so | Một số ca có thể thiếu ngữ cảnh |
| Nội tại | Mẫu rút theo kết luận của lượt nguồn (kể cả mã cũ) | Chạy lại mã hiện tại, ghép theo nội dung câu; báo riêng 54 câu không còn trích | Tầng SUPPORTED hiện tại chỉ có 5 mẫu |
| Ngoại tại | 8 doanh nghiệp, chủ yếu VN30, tiếng Việt và tiếng Anh | Lấy mẫu round-robin theo công ty, chặn tỷ trọng mỗi công ty | Chưa có ngân hàng, chưa có doanh nghiệp nhỏ |
| Cấu trúc | Năm mức kết luận và nhãn NOT_A_CLAIM có ranh giới mờ | Định nghĩa bằng bảng; phân xử quy ước rõ | Câu bối cảnh có thể được xếp khác |
| Thống kê | n nhỏ mỗi lớp; bootstrap theo công ty chỉ 8–12 cụm | Wilson, bootstrap cụm, báo cả số đếm | Khoảng tin cậy rộng |

## 6.6 Hạn chế của hệ thống

1. **Pháp lý:** gói luật `vn-green-v0.1-draft` có 1 quy tắc nháp, 0 quy tắc áp được trên 156/156 tuyên bố của HPG. Lớp pháp lý hiện chỉ trình bày văn bản liên quan, chưa kiểm điều kiện.
2. **Nguồn độc lập:** bằng chứng gần như toàn là tài liệu tự công bố. Không có dữ liệu bên thứ ba (Climate TRACE, GEM, quan trắc tự động) trong lượt chạy.
3. **Trích tuyên bố và bảng:** 30 % câu trích ra không phải tuyên bố. Bảng PDF bị dàn phẳng (F3); AG-3 v0 mới dựng lại được hàng bảng cho một trang.
4. **Độ phủ thấp:** hệ thống hiếm khi dám kết luận (S 8, C 52 trên 1 138). Bộ đọc IR cục bộ (4B, Q4) đã qua kiểm "cùng kết quả" trên Kaggle (khớp 0,963) nhưng chưa vào profile ngoại tuyến của sản phẩm, vì laptop thiếu RAM để đo.
5. **Chưa có người dùng thật:** bộ thử độ dễ dùng đã sẵn sàng, n = 0.
6. **Lượng tử:** sản phẩm không có thành phần lượng tử nào. QUBO cho chọn mẫu soát mới ở mức hình thức hoá.
7. **Đám mây:** khoá FPT hỏng từ 31/10; chế độ `cloud` hiện không chạy. Chế độ `gpu` còn dự phòng sang FPT, trái với mô tả "không rời máy".

## 6.7 Hướng phát triển

**Ngắn hạn (sau Chung kết, 2–4 tuần).** Mỗi việc đăng ký trước trong `configs/measurement_decisions.yaml`. Điều kiện để qua: không tăng kết luận sai trên GS-Bench, và cải thiện trên GS-Eval v2.
1. Sửa luật từ phủ định: cụm phủ định lành tính khớp có khoảng cách; từ phủ định không bao giờ tự ra CONTRADICTED. Mục tiêu: −22 vu oan.
2. Cổng so sánh được kiểm cùng đối tượng, dùng IR có `segment`. Mục tiêu: −13 vu oan.
3. Lọc câu không phải tuyên bố trước khi kiểm chứng.
4. Chấm rủi ro: thành phần không áp dụng thì 0 điểm; không chấm câu không phải tuyên bố. Kiểm lại ρ trên D-SCORE.
5. Gợi ý sửa: không gợi ý cho câu không phải tuyên bố; mở rộng mẫu ABSOLUTE; thêm loại "chứng nhận không nêu bên cấp".
6. Org pack: khớp `claim_types` mềm, `when` đọc glossary, `numeric_threshold` gắn với chỉ số.

**Trung hạn (1–3 tháng).**
1. Nhãn người: lô 1 T1 (79 câu) và 40/88 cặp của ba người gán; tính κ với nhãn Claude để biết nhãn Claude lệch ở đâu.
2. Thử với 5–8 người dùng (kiểm toán viên, cán bộ tín dụng xanh) theo `usability/PROTOCOL.md`: tỷ lệ hoàn thành, thời gian, SUS.
3. Đưa bộ đọc IR 4B cục bộ và chính sách hai đường vào sản phẩm sau cờ `QUANTUM_VERIFY=dual`, khi đo được thời gian trên laptop.
4. Nguồn độc lập P0: Climate TRACE, GEM thép và xi măng, danh mục QĐ 13/2024, quan trắc tự động.
5. Viết quy tắc pháp lý có điều khoản gắn với văn bản đã tách (QĐ 21/2025, TT 17/2022), có người duyệt.

**Dài hạn.**
- Mô hình soạn quy tắc org pack từ tài liệu nội bộ, có người duyệt.
- Hiệu chỉnh xác suất đúng theo tầng để dừng phán đoán có nguyên tắc.
- Thử nghiệm với một công ty kiểm toán hoặc một ngân hàng.
- Thành phần lượng tử chỉ khi bài toán chọn mẫu soát theo ngân sách (QUBO) được chứng minh có giá trị so với thuật toán cổ điển trên dữ liệu thật.

## Tóm tắt chương
- Các bảo đảm viết thành mã (không bịa số, quy tắc nội bộ không đổi kết luận, ngoại tuyến, truy vết) đứng vững; chất lượng phán đoán dứt khoát trên câu thật thì chưa.
- Lỗi tập trung ở hai đường tắt cho phép quy tắc kết luận khi chưa đủ điều kiện (từ phủ định, so khác đối tượng), cộng với lỗi trích câu và cách chấm điểm phạt cả thành phần không áp dụng.
- Bộ đo theo cấu trúc (GS-Bench) cần đi cùng bộ đo câu thật (GS-Eval v2); con số an toàn phải luôn nói kèm tập đo.
- Org pack cho người dùng thêm quy tắc mà không làm yếu bảo đảm; cái giá là độ linh hoạt, và hướng khắc phục là để mô hình soạn, người duyệt.
- Ưu tiên tiếp theo: sửa hai đường tắt, có nhãn người, thử với người dùng thật.
