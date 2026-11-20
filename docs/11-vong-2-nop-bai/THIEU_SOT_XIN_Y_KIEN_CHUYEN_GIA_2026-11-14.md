# GreenScan AI: các thiếu sót hiện tại, xin ý kiến chuyên gia

*Đội AQ2026-119. Cập nhật 14/11/2026, trước hạn nộp Vòng 2 (20/11) và bán kết (28–29/11).*

Mọi con số trong tài liệu đều đo trên phiên bản mã ngày 14/11/2026. Ở mỗi mục, đội ghi điều mình **chưa chắc** và câu hỏi muốn chuyên gia góp ý. Đội ưu tiên những góp ý giúp quyết định nên làm gì trong 4 ngày còn lại trước khi dừng sửa mã (18/11).

---

## 1. GreenScan làm gì (tóm tắt để đọc phần sau)

- **Đầu vào.** Một báo cáo cần kiểm (báo cáo phát triển bền vững, báo cáo thường niên, PDF có chữ hoặc bản scan) và các tài liệu đối chiếu (báo cáo tài chính, văn bản pháp luật, nguồn bên ngoài).
- **Đơn vị đánh giá** là **từng tuyên bố môi trường**, không phải cả doanh nghiệp. Mỗi tuyên bố nhận một trong năm kết luận:

  | Kết luận | Nghĩa |
  |---|---|
  | Ủng hộ | Bằng chứng xác nhận đầy đủ |
  | Ủng hộ một phần | Bằng chứng xác nhận một phần |
  | Chưa được chứng minh | Có tài liệu liên quan nhưng không xác nhận |
  | Mâu thuẫn | Bằng chứng nói ngược tuyên bố |
  | Chưa đủ bằng chứng | Không có tài liệu đủ liên quan |

  Kèm theo kết luận còn có: các thuộc tính tuyên bố còn thiếu (chỉ số, số liệu, kỳ báo cáo, năm gốc, phạm vi), phép tính, trang nguồn, và vị trí trong **hàng soát ưu tiên** cho kiểm toán viên.
- **Nguyên tắc thiết kế:** "mô hình đọc, luật quyết định, người duyệt".
  - Phép so số và kết luận do mã tất định làm.
  - Mô hình ngôn ngữ là tuỳ chọn và không tự ra được kết luận "ủng hộ" hay "mâu thuẫn".
  - Người soát quyết định cuối cùng.
- **Hai loại lỗi đội coi là nguy hiểm:**
  - **Vu oan:** kết luận "mâu thuẫn" trong khi tuyên bố đúng.
  - **Bỏ lọt:** kết luận "ủng hộ" trong khi tuyên bố sai.

## 2. Các bộ đo đội đang dùng

| Bộ đo | Cỡ | Nhãn do ai làm | Dùng để |
|---|---|---|---|
| GS-Bench v1.1 | 453 cặp (tuyên bố, đoạn bằng chứng). Trong đó 51 cặp dựng tay, 402 cặp sinh từ bảng số liệu thật của 7–8 doanh nghiệp | Đáp án suy từ cách dựng ca; Claude hỗ trợ, tác giả rà | Đo phép so số |
| GS-Eval v2 | 146 câu thật của 8 doanh nghiệp (giải thích kết luận); 200 câu × 2 lượt chấm rủi ro; 237 ca quy tắc nội bộ | Claude gán hai lượt độc lập rồi phân xử; tác giả rà soát | Đo trên câu thật |
| GS-Mutation v1 (mới, 14/11) | 865 ca. Từ cặp thật của 8 doanh nghiệp, mỗi ca cài đúng một lỗi: phóng đại số, đảo tăng/giảm, lùi năm gốc, xoá phạm vi, tuyệt đối hoá, chèn từ quảng bá, thay bằng chứng | Đáp án suy từ kiểu lỗi đã cài | Đo vu oan và bỏ lọt trước và sau mỗi thay đổi |
| Vụ việc có phán quyết | 4 vụ (cộng 2 doanh nghiệp Việt Nam làm đối chứng) | Phán quyết của cơ quan có thẩm quyền | Cổng kiểm hồi quy sau mỗi lần sửa |
| Mốc "đưa thẳng cho LLM" (mới, 14/11) | 183 ca của GS-Mutation | Như GS-Mutation | So với cách hỏi thẳng một mô hình lớn (gpt-oss-120b) |

---

## 3. Thiếu sót về dữ liệu

### D1. Chưa có tập nhãn do người gán độc lập
- **Hiện trạng.** Nhãn câu thật (GS-Eval v2) do Claude gán theo hướng dẫn viết sẵn, tác giả rà lại. GS-Bench là ca dựng. Chưa có hai người gán cùng một mẫu, nên chưa có số đo độ đồng thuận giữa người với người (Cohen's kappa).
- **Vì sao là vấn đề.** Mọi tỉ lệ đúng đều tính trên nhãn máy. Hệ thống có thể "khớp nhãn" chỉ vì máy gán nhãn và hệ thống mắc cùng một kiểu hiểu sai.
- **Đội dự định:** 2 người gán 150–200 câu từ khoảng 5 báo cáo. Gán chung 50 câu đầu để tính kappa; dưới khoảng 0,6 thì sửa hướng dẫn trước khi gán tiếp.
- **Xin ý kiến:**
  1. Người gán nên có nền gì: kiểm toán viên, chuyên viên ESG, hay sinh viên được hướng dẫn kỹ? Với bán kết, nhãn sinh viên có kappa tốt có đủ sức thuyết phục không?
  2. 150–200 câu có đủ không? Ngưỡng kappa bao nhiêu thì chấp nhận được với bài toán này?
  3. Năm mức kết luận có phải đơn vị nhãn đúng không? Hay nên gán theo từng thuộc tính (có số liệu, có năm gốc, có phạm vi, có nguồn độc lập)?

### D2. Nhãn "mức rủi ro 0–100" tự quy chiếu vào rubric của đội
- **Hiện trạng.**
  - Điểm rủi ro là tổng 9 thành phần với trọng số **đặt tay**: bằng chứng 18, mâu thuẫn 18, mức cụ thể 12, có số 12; năm gốc, kỳ báo cáo, phạm vi, nguồn độc lập và từ mơ hồ mỗi thành phần 8.
  - Nhãn tham chiếu do Claude chấm **theo chính rubric này**: hai lượt mù của cùng một mô hình, Spearman 0,73 giữa hai lượt.
  - Tương quan giữa điểm hệ thống và nhãn là Spearman 0,46 (n = 148).
- **Vì sao là vấn đề.** Đây là vòng lặp. Không thể dùng bộ nhãn này để hiệu chỉnh trọng số, và con số 0,46 không chứng minh điểm rủi ro phản ánh rủi ro tẩy xanh thật. Vì vậy đội đã bỏ kế hoạch "học lại trọng số từ nhãn".
- **Xin ý kiến:**
  1. Có nguồn tham chiếu bên ngoài nào cho "mức rủi ro" của một tuyên bố không? Ví dụ: kết luận thanh tra, xử phạt, ý kiến kiểm toán, đánh giá của bên thứ hai.
  2. Có nên bỏ hẳn điểm 0–100, chỉ giữ hàng soát ưu tiên và danh sách thuộc tính thiếu? Kiểm toán viên cần một con số hay cần một thứ tự?
  3. Trọng số hiện tại có điểm nào trái với thực hành kiểm toán hoặc đảm bảo (assurance) không?

### D3. Mẫu đo nhỏ, khoảng tin cậy rộng
- **Hiện trạng.**
  - Trên câu thật, hệ thống chỉ ra 7 kết luận dứt khoát ("ủng hộ" hoặc "mâu thuẫn"), precision 0,43.
  - Tập ngoài mẫu có 15 kết luận.
  - Phán quyết thật chỉ có 4 vụ.
  - Trong GS-Mutation: 17 ca đảo hướng, 10 ca lùi năm gốc, 6 ca xoá phạm vi.
- **Xin ý kiến:** với một cuộc thi sinh viên, cỡ mẫu và cách trình bày nào là trung thực mà vẫn đủ thuyết phục? Đội đang ghi khoảng tin cậy Wilson 95% kèm mọi tỉ lệ.

### D4. Không có tập kiểm tra thật sự "chưa từng thấy"
- **Hiện trạng.**
  - Luật đã từng được chỉnh trên GS-Bench, kể cả các công ty đội xếp vào phần "test" của GS-Mutation.
  - Ngưỡng đăng ký trước được viết trước khi chạy GS-Mutation, nhưng sau lần chạy thử đầu tiên trên câu thật.
- **Hệ quả.** Số đo hiện dùng để **so trước và sau một thay đổi**, không công bố được như độ chính xác tổng thể.
- **Xin ý kiến:** nên giữ riêng những báo cáo nào (ngành nào, năm nào) làm tập kiểm tra cuối, và ai nên giữ tập đó?

### D5. Bộ cài lỗi có nền mỏng
- **Hiện trạng.**
  - GS-Mutation dựng từ 104 cặp "ủng hộ" của 8 doanh nghiệp.
  - Chỉ 15/104 câu gốc được hệ thống kết luận "ủng hộ"; 63/104 câu gốc không được trích thành tuyên bố (xem H1).
  - Vì thế phần đo được thật của kiểu "phóng đại số" chỉ là 14 ca. Trong 14 ca đó, 11 ca bị bắt.
- **Xin ý kiến:**
  1. Kiểm thử bằng cách cài lỗi có được chấp nhận như bằng chứng bổ sung, bên cạnh nhãn người?
  2. Bảy kiểu lỗi đã cài có sát với các kiểu tẩy xanh thường gặp ở Việt Nam không? Còn thiếu kiểu nào?

### D6. Chưa có dữ liệu thật về trái phiếu xanh và tín dụng xanh
- **Hiện trạng.**
  - Đây là mảng sản phẩm nhắm tới: kiểm tra việc dùng vốn xanh.
  - Luật mới tính tỷ trọng "đã dùng / tổng" cho tuyên bố "sử dụng hoàn toàn". Luật này mới chỉ được kiểm trên **một ca tự dựng**: 500 tỷ huy động, 320 tỷ đã giải ngân, 180 tỷ chưa phân bổ. Kho dữ liệu chưa có báo cáo phân bổ vốn trái phiếu xanh thật nào.
- **Xin ý kiến:**
  1. Lấy báo cáo phân bổ và tác động của trái phiếu xanh ở Việt Nam ở đâu (sở giao dịch, tổ chức phát hành, bên đánh giá độc lập)?
  2. Báo cáo thật thường trình bày "tổng huy động, đã phân bổ, chưa phân bổ, đầu tư tạm thời" theo mẫu nào?
  3. Kiểu sai lệch nào hay gặp nhất: vốn chưa phân bổ, tài trợ lại dự án cũ, hay dự án không đủ điều kiện xanh?

### D7. Kho tài liệu mỏng ở phần chứng cứ đối chiếu
- **Hiện trạng.**
  - Đã thu thập 670 tài liệu của 21/30 doanh nghiệp, tương ứng 105 bộ công ty–năm. Chỉ 5 bộ có đủ chứng cứ lõi (báo cáo cần kiểm cùng tài liệu đối chiếu độc lập).
  - Ca thật chạy đầy đủ chủ yếu là Hòa Phát (264 trang).
- **Xin ý kiến:** nên ưu tiên ngành nào (thép, điện, xi măng, ngân hàng, bất động sản, thực phẩm)? Nguồn đối chiếu độc lập nào khả thi nhất ở Việt Nam?

### D8. Dữ liệu cho vòng "học từ phản hồi" gần như chưa có
- **Hiện trạng.**
  - Hệ thống ghi lại quyết định của người soát và dùng làm tiền lệ, làm ca kiểm hồi quy, và làm đề xuất sửa luật. Không gì trong số này tự đổi kết luận.
  - Dữ liệu thật hiện có: 1 lần ghi đè và 5 ca kiểm hồi quy.
  - Mô hình thử nghiệm học trên 824 cặp nhãn máy đạt F1 0,18, kém luật (0,35), nên bị cổng chặn.
- **Xin ý kiến:** trong một công ty kiểm toán, ai được phép biến quyết định của người soát thành dữ liệu huấn luyện? Cần quy trình kiểm soát chất lượng nào (soát lần hai, phân xử, tách theo khách hàng)?

### D9. Bộ quy tắc riêng của tổ chức chỉ có bản minh hoạ
- **Hiện trạng.** Bộ quy tắc mẫu là của một ngân hàng giả định. Chưa có chính sách thật của tổ chức nào.
- **Xin ý kiến:** chuyên gia có thể chia sẻ một chính sách tín dụng xanh hoặc tiêu chí soát xét nội bộ (đã ẩn danh) để thử không?

### D10. Mốc so sánh với LLM khó tái lập
- **Hiện trạng.** Mốc dùng gpt-oss-120b qua dịch vụ Groq miễn phí. Danh sách mô hình của dịch vụ này thay đổi không báo trước. Câu trả lời đã được lưu lại, nhưng chạy lại về sau có thể không được.
- **Xin ý kiến:** có nên thêm một mốc chạy cục bộ (mô hình mở, cố định phiên bản) để ai cũng tái lập được không?

### D11. Lợi ích chính chưa được đo
- **Hiện trạng.** Giả thuyết "giảm thời gian soát của kiểm toán viên" mới có quy trình đo, chưa chạy.
- **Xin ý kiến:** cách thiết kế một phép đo thời gian nhỏ với 3–5 kiểm toán viên: so có và không có công cụ, đếm cả số phát hiện đúng và sai?

---

## 4. Thiếu sót của hệ thống

### H1. Bước trích tuyên bố bỏ sót nhiều (nút thắt lớn nhất)
- **Số đo.** 63/104 câu gốc nhãn "ủng hộ" trong GS-Mutation không được trích thành tuyên bố.
- **Ví dụ câu bị bỏ:** câu nhắc lại số liệu của bảng, câu có nhiều số và nhiều ranh giới.
- **Xin ý kiến:** theo chuẩn nghề nghiệp, một câu thế nào thì là "tuyên bố môi trường cần kiểm"? Câu mô tả số liệu thuần tuý ("phát thải năm 2025 là X") có cần kiểm như một tuyên bố không?

### H2. Kết luận gần như một màu trên báo cáo thật
- **Số đo.** Hòa Phát: 154/156 tuyên bố "ủng hộ một phần". Trên GS-Bench, hệ thống chỉ dám kết luận dứt khoát ở 7,7% số ca.
- **Lý do một phần là cố ý:**
  - Đoạn trong chính báo cáo của doanh nghiệp không được dùng để bác bỏ tuyên bố, sau khi 35/38 kết luận "mâu thuẫn" trước ngày 05/11 bị xác định là sai.
  - Không có gì bác bỏ thì mức rủi ro tối đa là "trung bình".
- **Xin ý kiến:** kiểm toán viên có chấp nhận đầu ra chủ yếu là "ủng hộ một phần", nếu hàng soát và danh sách thuộc tính thiếu chỉ đúng chỗ cần đọc? Hay họ cần hệ thống dứt khoát hơn, dù có thêm rủi ro sai?

### H3. Bắt số bị phóng đại còn yếu
- **Số đo.** 11/101 ca phóng đại số bị bắt. Nguyên nhân chính là H1; tính riêng các ca đã trích được câu: 11/14.
- **So với mốc LLM:** hỏi thẳng gpt-oss-120b thì bắt được 47/72. Đổi lại, LLM:
  - vu oan 1/75 câu gốc;
  - để 5 ca đã cài lỗi vẫn "ủng hộ";
  - đổi câu trả lời ở 16% số câu khi hỏi lại y hệt;
  - không để lại phép tính.

  Luật: 0 vu oan, 0 ca cài lỗi còn "ủng hộ", và luôn cho cùng một kết quả.
- **Xin ý kiến:** trong kiểm toán, đánh đổi nào chấp nhận được? Bắt nhiều hơn nhưng không ổn định, hay bắt ít nhưng tái lập được và có phép tính? Hướng "mô hình đọc câu, mã so số và kết luận" có phù hợp chuẩn mực về bằng chứng kiểm toán không?

### H4. Vẫn còn kết luận "ủng hộ" sai
- **Số đo.**
  - GS-Bench: 8 ca.
  - Câu thật: 3/7 kết luận dứt khoát là "ủng hộ" sai. Hai câu thực ra không phải tuyên bố; một câu chỉ đáng "ủng hộ một phần".
  - Câu có hai số, một số đúng một số sai: còn 2 ca lọt.
- **Biện pháp tạm thời:** khuyến nghị người soát xác nhận mọi kết luận "ủng hộ".
- **Xin ý kiến:** có nên chỉ cho phép "ủng hộ" khi bằng chứng đến từ nguồn độc lập (văn bản pháp luật, bên thứ ba, chuẩn mực), không tính báo cáo khác của chính doanh nghiệp? Hệ thống đã có cờ này nhưng đang tắt.

### H5. Từ quảng bá đi kèm câu có số không bị gắn cờ "mơ hồ"
- **Số đo.** Thêm "khẳng định vị thế doanh nghiệp thân thiện với môi trường hàng đầu" vào câu có số liệu: 0/104 câu bị gắn cờ.
- **Xin ý kiến:** trong thực hành, đây có tính là tuyên bố mơ hồ cần nêu không, khi phần có số đã được chứng minh?

### H6. "Phạm vi" đang gộp hai khái niệm
- **Hiện trạng.** Thuộc tính "phạm vi / ranh giới" coi ranh giới tổ chức ("của 4 nhà máy", "toàn tập đoàn") là đủ. Vì vậy câu không nêu phạm vi phát thải 1, 2, 3 vẫn không bị báo thiếu.
- **Xin ý kiến:** có nên tách thành hai thuộc tính riêng: phạm vi phát thải theo GHG Protocol và ranh giới tổ chức? Thiếu thuộc tính nào nghiêm trọng hơn?

### H7. Chưa so lời văn với bảng số liệu trong cùng một báo cáo
- **Hiện trạng.**
  - Đội đã viết luật với điều kiện chặt: đoạn là bảng hoặc trang dữ liệu, cùng kỳ, cùng mảng kinh doanh, không có số OCR đáng ngờ, không có chữ "điều chỉnh / trình bày lại". Luật đang **tắt**: trên 1.766 câu thật đã lưu, nó chỉ ra 1 cờ, và cờ đó sai.
  - Chưa làm điều kiện "bảng cộng dọc khớp".
  - Người chỉ có một báo cáo (doanh nghiệp tự soát, cán bộ tín dụng) vì thế chưa được hỗ trợ kiểu phát hiện này.
- **Xin ý kiến:** kiểm toán viên dùng tiêu chí nào để coi chênh lệch giữa lời văn và bảng là một phát hiện? (Làm tròn, trình bày lại số liệu, khác ranh giới, khác kỳ…)

### H8. Điểm rủi ro chưa hiệu chỉnh
- **Hiện trạng.**
  - Trọng số đặt tay; mức rủi ro bị chặn ở "trung bình" khi không có bằng chứng bác bỏ.
  - Thành phần "bất thường so với kỳ trước" chưa tính.
  - Tương quan với nhãn 0,46, mà nhãn đó tự quy chiếu (D2).
- **Xin ý kiến:** xem D2.

### H9. Các việc chưa làm
- "Hiện nay / năm nay" chưa được hiểu thành năm của báo cáo. Sửa việc này sẽ đổi điểm rủi ro của nhiều câu.
- Lớp mô hình suy luận ngôn ngữ (mDeBERTa) ở vai trò chỉ cảnh báo: chưa làm.
- Bộ đọc Qwen3-4B (mô hình đọc câu thành dữ kiện, mã kết luận) chưa bật mặc định, vì chưa đo thời gian chạy trên laptop.

### H10. Bản trình diễn trực tuyến
- **Hiện trạng.** Đây là bản tĩnh miễn phí, xem được 4 phiên đã chạy sẵn.
- **Giới hạn:**
  - không phân tích được tài liệu mới;
  - ảnh trang gốc không tô sáng đoạn bằng chứng;
  - một phiên mẫu chạy từ sáng 14/11 nên còn lệch với kết quả mới ở một ca.

---

## 5. Phương pháp và thiết kế để đảm bảo chất lượng đầu ra

Phần này mô tả cách đội đang giữ chất lượng đầu ra ở mức đo được, rồi nêu những chỗ đội muốn chuyên gia **góp ý tưởng hoặc lưu ý**. Đó là những chỗ đội tự thiết kế, chưa đối chiếu với thực hành nghề nghiệp.

### 5.1. Cơ chế hiện có

| Lớp | Cơ chế | Mục đích |
|---|---|---|
| Kiến trúc | 10 bất biến được thi hành bằng kiểm thử, ví dụ "số học là việc của mã", "vắng bằng chứng không phải vi phạm", "mô hình không tự ra kết luận" | Lỗi thiết kế không lọt qua lúc sửa mã |
| So số | Trước khi tính, hai con số phải "so được": cùng đơn vị, cơ sở đo (tỷ trọng, mức thay đổi, tuyệt đối, cường độ), ranh giới, công nghệ, loại chỉ số, phạm vi phát thải, mảng kinh doanh, và cùng là mục tiêu hoặc cùng là số thực hiện. Sai số cho phép tính theo độ chính xác công bố | Phần lớn kết luận sai trước đây là so hai số không cùng đối tượng |
| Chốt chống vu oan | Đoạn trong chính tài liệu chứa tuyên bố không được bác bỏ tuyên bố. Cụm từ bác bỏ trong tài liệu của chính doanh nghiệp chỉ có hiệu lực khi nằm trong một phán quyết | Trước ngày 05/11, 35/38 kết luận "mâu thuẫn" trên câu thật là sai |
| Bỏ phiếu trắng an toàn | Không đủ căn cứ thì trả "chưa đủ bằng chứng". Chỉ trả "chưa được chứng minh" khi kho tài liệu đủ | Thà không kết luận còn hơn kết luận sai |
| Mô hình ngôn ngữ | Lập trường do mô hình đưa ra không tự tạo "ủng hộ" hay "mâu thuẫn". Lời giải thích của mô hình bị loại nếu có con số không xuất hiện trong nguồn. Trích dẫn phải đúng nguyên văn | Mô hình được đọc, không được bịa |
| Số OCR đáng ngờ | Phép so dựa trên số mà OCR đọc kém tự tin thì hạ xuống "ủng hộ một phần" và ghi rõ số nào | Không để lỗi máy quét thành kết luận |
| Người duyệt | Mọi kết luận "mâu thuẫn" và mọi xung đột pháp lý đưa phiên vào trạng thái "chờ người duyệt". Hàng soát chỉ được thêm mục, không bao giờ bớt | Người quyết định cuối |
| Tái lập | Mỗi phiên ghi biên bản (manifest): mã băm đầu vào, phiên bản cấu hình, bộ quy tắc, lời nhắc mô hình. Chạy lại cho cùng kết quả | Kiểm tra lại được về sau |
| Đo trước khi bật | Ngưỡng và dự đoán được ghi vào sổ đo trước khi chạy. Luật mới phải qua bốn cổng hồi quy (GS-Bench, GS-Eval v2, các vụ có phán quyết, GS-Mutation) và không được tăng vu oan. Không qua ngưỡng thì để tắt và ghi lý do | Không chỉnh luật theo kết quả mình muốn thấy |
| Học từ phản hồi | Ca người soát đã chốt thành ca kiểm hồi quy; ca đã qua không được hỏng lại. Mô hình mới chạy ở chế độ "bóng" (chỉ ghi log, không hiện cho người dùng). Muốn thay mô hình cũ thì phải qua cổng: bộ giữ lại ≥ 30 ca, macro-F1 không kém, không thêm "mâu thuẫn" hay "ủng hộ" sai, và người duyệt khác người huấn luyện | Phản hồi không làm hệ thống tệ đi một cách âm thầm |
| Vệ sinh nhãn | 10% nhãn được người thứ hai soát mù, tính kappa, có phân xử. Nhãn của doanh nghiệp đang bị soát không dùng để huấn luyện | Nhãn bẩn không vào mô hình |
| Quy tắc tổ chức | Bộ quy tắc tải lên luôn là bản nháp; người duyệt phải khác người tải lên. Quy tắc chỉ thêm phát hiện, không đổi kết luận | Tuỳ biến không phá chuẩn chung |

### 5.2. Đang đo ở những mức nào

| Mức | Chỉ số hiện có | Chưa có |
|---|---|---|
| Từng bước | Truy xuất: kiểm tay trên vài ca. Kiểm chứng: precision theo từng loại kết luận, vu oan, bỏ lọt. Mỗi quyết định ghi đè của người soát được phân loại hệ thống sai ở bước tìm, đọc, hay luật | Recall của bước trích tuyên bố và recall@5 của bước truy xuất trên **nhãn người** |
| Từng đầu ra | Kết luận: precision trên phần kết luận dứt khoát, độ phủ. Điểm rủi ro: Spearman. Hàng soát: số mục, lý do | Độ tin cậy kèm từng kết luận. Recall của hàng soát (bao nhiêu tuyên bố có vấn đề lọt ra ngoài hàng soát) |
| Cả phiên | Thời gian, RAM, tái lập | Thời gian soát của con người (D11) |
| Theo thời gian | 743 kiểm thử, cổng hồi quy mỗi lần sửa | Theo dõi khi gặp định dạng báo cáo mới (trôi dữ liệu) |

### 5.3. Ý tưởng đội đang cân nhắc

| Ý tưởng | Nội dung |
|---|---|
| Lấy mẫu ngẫu nhiên ngoài hàng soát | Mỗi phiên rút ngẫu nhiên vài tuyên bố **không** nằm trong hàng soát cho người kiểm, để ước lượng tỉ lệ bỏ sót của hàng soát |
| Kiểm thử biến hình (metamorphic) | Viết lại câu mà giữ nguyên nghĩa thì kết luận không được đổi. Đổi số hay đổi hướng thì kết luận phải đổi đúng chiều |
| Đường cong rủi ro–độ phủ | Báo cáo precision ở từng mức độ phủ (càng dám kết luận nhiều thì sai bao nhiêu), thay vì một con số duy nhất. Để người dùng chọn điểm vận hành |
| Ngưỡng theo mức trọng yếu | Tuyên bố trọng yếu (tài chính xanh, số phát thải tổng) đòi bằng chứng mạnh hơn mới được "ủng hộ"; tuyên bố phụ thì nới hơn |
| Thứ bậc nguồn bằng chứng | Văn bản pháp luật và bên thứ ba độc lập > báo cáo tài chính đã kiểm toán > báo cáo khác của chính doanh nghiệp. "Ủng hộ" chỉ được dựa trên nhóm đầu |
| Danh mục kiểm trước khi phát hành | Mỗi phiên bản phát hành có một trang ghi số đo ở mọi mức, so với phiên bản trước, kèm chữ ký người duyệt |

### 5.4. Câu hỏi xin chuyên gia

**Định nghĩa "chất lượng đủ dùng":**
1. Với một công cụ hỗ trợ kiểm toán hoặc soát xét ESG, chỉ số chính nên là gì: precision của kết luận dứt khoát, recall của hàng soát, hay thời gian người soát tiết kiệm được? Có mức tối thiểu nào theo thông lệ, ví dụ vu oan dưới bao nhiêu %?
2. Nên cân hai loại lỗi thế nào? Với kiểm toán viên, bỏ lọt có nặng hơn vu oan không? Câu trả lời có đổi theo người dùng (ngân hàng thẩm định tín dụng xanh, doanh nghiệp tự soát, cơ quan quản lý) không?

**Thiết kế để đảm bảo chất lượng:**

3. Đối chiếu với chuẩn mực đảm bảo (ISAE 3000, ISAE 3410 cho báo cáo khí nhà kính, ISSA 5000 cho báo cáo bền vững):
   - "Đủ và thích hợp" của bằng chứng nên được mã hoá thành luật như thế nào?
   - Thứ bậc nguồn ở mục 5.3 có hợp lý không?
4. Có nên lấy mẫu ngoài hàng soát theo phương pháp chọn mẫu kiểm toán (ISA 530) không? Cỡ mẫu bao nhiêu thì đủ để ước lượng tỉ lệ bỏ sót?
5. Hàng soát hiện mở tối đa 25 mục, với ngưỡng điểm ưu tiên 55. Một kiểm toán viên thực tế xem được bao nhiêu mục cho một báo cáo 250 trang? Nên kiểm định thứ tự ưu tiên bằng cách nào?
6. Có nên kèm độ tin cậy (đã hiệu chỉnh) cho từng kết luận không, hay độ tin cậy dễ bị hiểu nhầm thành xác suất tẩy xanh?
7. Nên phân bổ trách nhiệm giữa máy và người thế nào để không ai phó mặc cho ai? Ví dụ: khi người soát chỉ bấm "xác nhận" mà không đọc.

**Phương pháp đo:**

8. Kiểm thử cài lỗi và kiểm thử biến hình có được coi là bằng chứng chất lượng hợp lệ bên cạnh nhãn người không? Nếu có, nên trình bày ra sao để không bị coi là "tự chấm cho mình"?
9. Đo theo từng bước (trích, tìm, đọc, so) rồi đặt cổng cho từng bước có phải cách đúng không, hay chỉ cần đo đầu–cuối?
10. Khi hệ thống dùng mô hình ngôn ngữ, vốn không tất định: nên tái lập bằng cách cố định phiên bản mô hình và lưu đệm câu trả lời, hay phải chạy nhiều lần rồi báo độ ổn định?
11. Khi vận hành thật, nên theo dõi những tín hiệu nào để biết chất lượng đang giảm? Ví dụ: tỉ lệ người soát ghi đè, tỉ lệ "chưa đủ bằng chứng", định dạng báo cáo lạ.
12. Tài liệu nào nên kèm khi bàn giao cho người dùng chuyên nghiệp: thẻ dữ liệu, thẻ mô hình, giới hạn sử dụng, quy trình xử lý khi hệ thống sai?

## 6. Các phần khác của hệ thống cần tham khảo

Các mục trên tập trung vào dữ liệu, độ chính xác và cách đo. Mục này hỏi những phần còn lại của hệ thống, nơi đội thiếu kinh nghiệm thực tế.

### 6.1. Bài toán, người dùng và quy trình nghiệp vụ
- **Hiện trạng.**
  - Đội nhắm bốn nhóm người dùng: kiểm toán viên hoặc người soát xét ESG, cán bộ thẩm định tín dụng xanh, doanh nghiệp tự soát trước khi công bố, và cơ quan quản lý.
  - Đầu ra gồm hàng soát, giấy làm việc tiếng Việt in được, và hồ sơ bằng chứng xuất ra JSON hoặc Markdown.
- **Xin ý kiến:**
  1. Trong bốn nhóm, nhóm nào thật sự có nhu cầu và có ngân sách trong 1–2 năm tới? Nên chọn một nhóm để làm thí điểm trước không?
  2. Trong quy trình soát xét báo cáo bền vững hiện nay ở Việt Nam, công cụ nên chen vào bước nào: lập kế hoạch, thu thập bằng chứng, hay rà soát cuối?
  3. Giấy làm việc do máy sinh ra có dùng được trong hồ sơ kiểm toán không? Cần thêm trường nào: người lập, người soát, ngày, tham chiếu chỉ mục…?
  4. Người dùng muốn đầu ra ở dạng nào: Excel, Word, hay tích hợp vào phần mềm kiểm toán đang dùng?

### 6.2. Kiến thức nghiệp vụ, phân loại và khung pháp lý
- **Hiện trạng.**
  - Tuyên bố được chia thành 8 loại.
  - Có từ điển chỉ số song ngữ và một kho kiến thức nghiệp vụ. Kho này chỉ để giải thích, không bao giờ được dùng làm bằng chứng.
  - Bộ quy tắc pháp lý Việt Nam (`rule_pack_vn_green_v0.1`) là **bản nháp chưa có người am hiểu pháp luật duyệt**. Quy tắc nháp vì thế không bao giờ được kích hoạt.
  - Danh mục văn bản pháp luật có ghi ngày hiệu lực. Hệ thống tách hai câu hỏi:
    - tuân thủ luật tại thời điểm công bố;
    - phù hợp với tiêu chí hiện hành.
- **Xin ý kiến:**
  1. 8 loại tuyên bố và 5 thuộc tính cần có (chỉ số, số liệu, kỳ, năm gốc, phạm vi) đã đủ và đúng với thực hành chưa? Có nên đối chiếu với danh mục phân loại xanh quốc gia và với yêu cầu công bố thông tin trong báo cáo thường niên không?
  2. Nhờ chuyên gia pháp lý duyệt bộ quy tắc pháp lý: văn bản nào bắt buộc phải có, văn bản nào đã hết hiệu lực hoặc bị thay thế, và điều khoản nào thật sự tạo ra nghĩa vụ công bố?
  3. Ở Việt Nam, "tẩy xanh" đã có định nghĩa pháp lý hay chế tài cụ thể nào chưa? Nếu chưa, hệ thống nên dùng khung tham chiếu nào: hướng dẫn quốc tế, tiêu chí trái phiếu xanh, hay quy định về quảng cáo?
  4. Những chỉ số nào doanh nghiệp Việt Nam hay công bố sai đơn vị hoặc sai ranh giới nhất (khí nhà kính, năng lượng, nước, chất thải)?

### 6.3. Trách nhiệm pháp lý và đạo đức
- **Hiện trạng.**
  - Sản phẩm tự nhận là công cụ sàng lọc rủi ro, không đưa kết luận pháp lý.
  - Mọi kết luận "mâu thuẫn" đều cần người duyệt.
  - Báo cáo của doanh nghiệp được thu thập công khai từ trang web chính thức.
- **Xin ý kiến:**
  1. Nếu kết quả về một doanh nghiệp có tên bị lộ ra ngoài, ví dụ trên slide hay trong bản trình diễn, đội có rủi ro pháp lý gì không? Có nên ẩn danh doanh nghiệp trong mọi tài liệu công khai?
  2. Thu thập và lưu báo cáo công khai của doanh nghiệp để làm dữ liệu huấn luyện và đánh giá có vướng bản quyền không? Cần ghi điều kiện sử dụng ra sao?
  3. Có rủi ro thiên lệch không: doanh nghiệp nhỏ, báo cáo sơ sài hoặc chỉ có bản scan sẽ bị đẩy vào hàng soát nhiều hơn chỉ vì công bố kém, chứ không phải vì tẩy xanh. Nên xử lý thế nào?
  4. Tuyên bố miễn trừ trách nhiệm và giới hạn sử dụng nên ghi những gì để người dùng không hiểu nhầm "không bị gắn cờ" thành "đã được xác nhận"?

### 6.4. Bảo mật và quản trị dữ liệu khách hàng
- **Hiện trạng.**
  - Mặc định chạy hoàn toàn trên máy của người dùng: không GPU, không khoá API, không gửi dữ liệu ra ngoài.
  - Mô hình ngôn ngữ qua API là tuỳ chọn. Đội chỉ dùng API cho thí nghiệm, và chỉ trên báo cáo công khai.
  - Khi chạy máy chủ dùng chung thì có lớp đăng nhập.
  - Mọi thao tác được ghi vào vết kiểm toán.
- **Xin ý kiến:**
  1. Công ty kiểm toán hoặc ngân hàng đòi những gì trước khi cho đưa tài liệu khách hàng vào một công cụ như vậy: cài đặt nội bộ, mã hoá, thời hạn lưu, xoá dữ liệu, phân quyền?
  2. Có chấp nhận gửi tài liệu chưa công bố tới mô hình ngôn ngữ qua API trong bất kỳ trường hợp nào không, hay chỉ được chạy mô hình cục bộ?
  3. Vết kiểm toán hiện ghi người thao tác, thời điểm và phiên bản cấu hình. Như vậy đã đủ để phục vụ kiểm soát chất lượng hồ sơ kiểm toán chưa?

### 6.5. Thành phần AI và lựa chọn mô hình
- **Hiện trạng.**
  - Lõi kết luận chạy bằng luật.
  - Mô hình chỉ được dùng ở vai trò đọc (Qwen3-4B chạy cục bộ, gpt-oss-120b qua API cho thí nghiệm), hoặc chạy "bóng" để học từ phản hồi. Chưa mô hình nào đủ tốt để thay luật.
  - Một phần nhãn huấn luyện do Claude gán.
- **Xin ý kiến:**
  1. Với cuộc thi về AI, giám khảo có đánh giá thấp một hệ thống mà lõi kết luận "không dùng AI" không? Nên trình bày vai trò của AI ra sao cho trung thực mà vẫn đúng giá trị?
  2. Có nên tinh chỉnh một mô hình nhỏ tiếng Việt cho bước trích tuyên bố (nút thắt H1), thay vì tiếp tục viết luật?
  3. Dùng nhãn do một mô hình lớn gán để huấn luyện mô hình nhỏ có được chấp nhận về phương pháp không, nếu ghi rõ nguồn gốc và có người rà?
  4. Có nên thử thành phần lượng tử không? Hiện đội không đưa vào vì chưa thấy lợi thế được chứng minh ở bài toán này. Cuộc thi có tên "AI và Lượng tử"; không có thành phần lượng tử có bị trừ điểm không, hay trình bày thẳng như hiện nay là đủ?

### 6.6. Prototype, giao diện và vận hành
- **Hiện trạng.**
  - Ứng dụng web giao diện tiếng Việt.
  - Báo cáo 264 trang chạy khoảng 2 phút trên laptop 16 GB.
  - Bản trực tuyến là bản tĩnh: xem và soát các phiên đã chạy sẵn, không phân tích tài liệu mới.
  - Bản cài trên máy chạy được đầy đủ.
- **Xin ý kiến:**
  1. Ở bán kết, nên demo trực tiếp trên một báo cáo giám khảo đưa (rủi ro chạy lỗi) hay demo trên phiên đã chạy sẵn? Có nên trả phí để có bản trực tuyến chạy được phân tích mới?
  2. Màn hình nào kiểm toán viên cần nhất mà hiện chưa có: so sánh hai năm, theo dõi tiến độ soát, phân công người soát, hay ghi chú?
  3. Bản scan chất lượng kém (OCR) hay gặp đến mức nào trong báo cáo của doanh nghiệp Việt Nam? Có cần ưu tiên cải thiện phần đọc bảng trong PDF không?
  4. Ai sẽ cập nhật bộ luật, từ điển và văn bản pháp luật sau khi phát hành, và theo chu kỳ nào?

### 6.7. Triển khai, chi phí và tác động
- **Hiện trạng.** Lộ trình 12 tháng nằm ở slide "Ai dùng, và lộ trình 12 tháng". Chi phí vận hành gần bằng 0 khi chạy cục bộ. Chưa có đối tác thí điểm.
- **Xin ý kiến:**
  1. Đơn vị nào có thể nhận thí điểm: công ty kiểm toán vừa và nhỏ, ngân hàng có danh mục tín dụng xanh, hay khoa kế toán–kiểm toán trong trường?
  2. Nên đo tác động bằng chỉ số nào cho thuyết phục: giờ công tiết kiệm, số phát hiện thêm, hay số tuyên bố được sửa trước khi công bố?
  3. Mô hình kinh doanh nào hợp lý: phần mềm cài nội bộ có phí bản quyền, dịch vụ theo báo cáo, hay công cụ miễn phí cho doanh nghiệp kèm bản trả phí cho kiểm toán viên?

### 6.8. Trình bày trước hội đồng
- **Xin ý kiến:**
  1. Hội đồng có nền tài chính, kế toán, kiểm toán sẽ hỏi gì đầu tiên? Đội đang chuẩn bị các câu: "sao không đưa thẳng cho ChatGPT", "ai gán nhãn", "đúng bao nhiêu %", "khác gì phần mềm kiểm toán hiện có".
  2. Trình bày trung thực các giới hạn (kết luận một màu, nhãn máy, mẫu nhỏ) ở mức nào thì được đánh giá là nghiêm túc, và từ mức nào thì bị xem là sản phẩm chưa dùng được?
  3. Ví dụ minh hoạ nào sẽ thuyết phục nhất với hội đồng: Hòa Phát (báo cáo thật nhưng kết quả "phẳng"), ca trái phiếu xanh tự dựng (kết quả rõ nhưng là dữ liệu giả lập), hay ca có phán quyết thật?

## 7. Thứ tự đội định làm trước 18/11. Xin góp ý.

1. **Tập nhãn người, 150–200 câu, có kappa** (D1, D2, D4).
2. **3–5 báo cáo phân bổ vốn trái phiếu xanh thật**: chạy luật tỷ trọng và đọc tay từng kết quả (D6).
3. **Cải thiện bước trích tuyên bố** (H1), đo trước và sau bằng GS-Mutation và tập nhãn người.

Câu hỏi chung: nếu chỉ kịp **một** việc, chuyên gia chọn việc nào? Có việc nào quan trọng hơn mà đội chưa thấy không?

---

## Phụ lục: số đo hiện tại (14/11/2026)

| Bộ đo | Chỉ số | Giá trị |
|---|---|---|
| GS-Bench (453 ca) | Tỷ lệ dám kết luận dứt khoát | 0,077 (35 ca) |
| | Chính xác trên phần kết luận | 0,743 (26/35) |
| | "Ủng hộ" sai / "mâu thuẫn" sai | 8 / 1 |
| GS-Eval v2 (146 câu thật) | Kết luận dứt khoát / precision | 7 / 0,43 |
| | "Mâu thuẫn" sai | 1 (câu đó không phải tuyên bố) |
| | Kết luận trùng nhãn, toàn bộ 102 tuyên bố thật | 0,51 |
| | Spearman điểm rủi ro với nhãn | 0,46 (n = 148) |
| GS-Mutation (865 ca) | Vu oan trên bản gốc | 0/290 |
| | Bắt phóng đại số / đảo hướng | 11/101 / 5/17 |
| | Ca cài lỗi mà vẫn "ủng hộ" | 5 |
| | Câu gốc được trích thành tuyên bố | 41/104 |
| Vụ có phán quyết | Khớp kỳ vọng | 4/4 |
| Hòa Phát (264 trang) | Thời gian, RAM đỉnh | khoảng 2 phút, 1,3–1,7 GB, không GPU |
| | Phân bố kết luận | 154 ủng hộ một phần, 1 ủng hộ, 1 chưa đủ bằng chứng |
| | Hàng soát | 8 mục trên 172 mục được xếp hạng |
| Kiểm thử tự động | | 743 đạt |
