# Chương 1. Giới thiệu hệ thống

Chương này trả lời ba câu hỏi: GreenScan AI giải quyết việc gì, cho ai, và hệ thống cam kết những nguyên tắc nào khi đưa ra một kết luận. Các chương sau mô tả từng bước xử lý và cho thấy kết quả thật của từng bước trên hai ca minh hoạ.

## 1.1. Bài toán

Doanh nghiệp Việt Nam ngày càng công bố nhiều thông tin môi trường: báo cáo phát triển bền vững (BCPTBV), báo cáo thường niên (BCTN), hồ sơ vay vốn xanh, bản công bố trái phiếu xanh. Trong các tài liệu đó có những câu như "Công ty đã giảm 30% phát thải khí nhà kính" hay "Tỷ lệ tái chế chất thải rắn đạt hơn 99%". Người đọc chuyên nghiệp (kiểm toán viên, cán bộ tín dụng xanh ngân hàng, chuyên viên tuân thủ) cần biết **câu đó có bằng chứng trong bộ hồ sơ hay không**, và nếu không thì thiếu gì.

GreenScan không hỏi "doanh nghiệp có tẩy xanh không". Câu hỏi đó cần ý định và bối cảnh pháp lý mà phần mềm không có. Hệ thống hỏi một câu hẹp hơn và kiểm được: *tuyên bố này được tài liệu nào ủng hộ, bác bỏ, hay chưa có gì để đối chiếu; con số có khớp không; tuyên bố còn thiếu chỉ số, kỳ, năm gốc hay phạm vi nào*. Kết luận cuối cùng thuộc về người soát xét.

## 1.2. Người dùng và tình huống sử dụng

| Người dùng | Việc cần làm | GreenScan đưa ra |
|---|---|---|
| Kiểm toán viên / người làm dịch vụ đảm bảo | Soát các tuyên bố trước khi phát hành ý kiến | Hàng soát xếp ưu tiên, bằng chứng có trích dẫn trang, giấy làm việc tiếng Việt |
| Cán bộ tín dụng xanh, trái phiếu xanh | Kiểm hồ sơ khách hàng theo danh mục phân loại xanh | Kết luận từng tuyên bố, văn bản pháp lý liên quan, quy tắc nội bộ của ngân hàng |
| Doanh nghiệp tự soát | Phát hiện câu thiếu số liệu, thiếu năm gốc trước khi công bố | Danh sách thuộc tính còn thiếu, gợi ý bổ sung (không viết hộ, không bịa số) |
| Người dùng ứng dụng AI (Claude Desktop…) | Hỏi bằng ngôn ngữ tự nhiên về một phiên phân tích | Câu trả lời ngắn chỉ dựa trên kết quả công cụ, có kiểm số |

## 1.3. Đầu vào và đầu ra

**Đầu vào** là từ 1 đến 5 tệp (PDF có chữ hoặc bản quét, Word, văn bản), tổng không quá 80 MB mỗi lần trên máy tối thiểu. Mỗi tệp được gán một **vai trò**: `claim_source` (tài liệu chứa tuyên bố cần kiểm), `evidence` (tài liệu dùng để đối chiếu), `reference` (văn bản tham chiếu); và một **loại nguồn**: `internal`, `financial`, `environmental`, `legal`, `external`, `standard`.

**Đầu ra** của mỗi phiên là một thư mục `.quantum/runs/<run_id>/` gồm:

- `result.json`: toàn bộ kết quả có cấu trúc (tuyên bố, bằng chứng, kết luận, điểm rủi ro, kiểm tra pháp lý, hàng soát, cổng chất lượng);
- `evidence_pack.md`: gói bằng chứng cho người soát đọc;
- `manifest.json`: dấu vết tái lập (mã băm đầu vào, mã băm cấu hình, phiên bản luật, phiên bản prompt);
- `audit.jsonl`: nhật ký từng sự kiện theo thời gian;
- `contract/raw.jsonl`, `clean.jsonl`, `extract.jsonl`: ba lớp dữ liệu theo hợp đồng dữ liệu `data-layers-v1`.

Mỗi tuyên bố nhận một trong năm **mức kết luận**:

| Mã | Tên tiếng Việt trên giao diện | Ý nghĩa |
|---|---|---|
| `SUPPORTED` | Được ủng hộ | Có nguồn đối chiếu (ngoài chính tài liệu tuyên bố) xác nhận nội dung trọng yếu |
| `PARTIALLY_SUPPORTED` | Ủng hộ một phần | Có bằng chứng cùng chủ đề hoặc chỉ chính tài liệu tuyên bố xác nhận; chưa đủ để coi là được ủng hộ |
| `UNSUPPORTED` | Chưa được chứng minh | Bộ hồ sơ đã đủ tài liệu đối chiếu mà vẫn không có gì xác nhận |
| `CONTRADICTED` | Mâu thuẫn với nguồn | Có bằng chứng bác bỏ (thường là phép tính lại từ số liệu) |
| `INSUFFICIENT_EVIDENCE` | Chưa đủ bằng chứng | Bộ hồ sơ chưa đủ để nói gì |

Kèm theo kết luận là **điểm rủi ro** 0–100 với mức `LOW / MEDIUM / HIGH / CRITICAL`, **thứ hạng trong hàng soát**, và **trạng thái phát hành** của cả phiên (`RELEASABLE`, `PENDING_HUMAN_REVIEW`, `BLOCKED`).

## 1.4. Nguyên tắc thiết kế

1. **Bằng chứng trước.** Không có đoạn bằng chứng thì không có kết luận "được ủng hộ". Mỗi kết luận ghi tên tài liệu, trang và câu làm căn cứ.
2. **Luật và phép tính quyết định, mô hình ngôn ngữ chỉ hỗ trợ.** Toàn bộ quy trình ra kết luận chạy bằng luật và code. Các mô hình ngôn ngữ (LLM) chỉ được dùng để lập kế hoạch gọi công cụ, viết câu trả lời, giải thích hoặc điền thuộc tính, và mọi đầu ra của chúng đều qua bộ kiểm bằng code. Quyết định D-2026-10-16-01 cấm mô hình đổi kết luận của sản phẩm.
3. **Không bịa số.** Câu trả lời hay lời giải thích có con số không xuất hiện trong dữ liệu nguồn bị loại, hệ thống dùng câu soạn sẵn theo luật.
4. **Biết nhường cho người.** Trường hợp không quyết được thì gắn cờ chờ người soát (`PENDING_HUMAN_REVIEW`), không đoán.
5. **Truy vết được.** Cùng đầu vào và cùng cấu hình thì ra cùng kết quả; `manifest.json` và `audit.jsonl` cho phép tái lập.
6. **Dữ liệu không rời máy khi chưa được phép.** Hồ sơ mật (loại B, C) chỉ xử lý trên máy; API bên ngoài chỉ được gọi cho tài liệu công khai (loại A) và khi người dùng bật `public=true` (quyết định D-2026-10-06-06).
7. **Chạy trên máy tối thiểu.** CPU, 8–16 GB RAM, không GPU. Phương án thuê GPU đã bị bác ngày 13/11/2026 vì không có kinh phí (D-2026-11-13-03).

## 1.5. Cấu hình được mô tả trong tài liệu này

Mọi kết quả trong tài liệu được chạy ngày {{RUN_DATE}} trên laptop Intel i7-1355U, 16 GB RAM, không GPU NVIDIA, với cấu hình đang triển khai:

{{CONFIG_TABLE}}

Quy ước ghi nhãn mức chắc chắn của khẳng định (dùng trong toàn bộ dự án): **[ĐÃ THỰC NGHIỆM]** là số đo do nhóm chạy và có tệp kết quả; **[NGOÀI]** là thông tin từ nguồn bên ngoài; **[KIẾN THỨC NỀN]** là kiến thức chuyên môn phổ biến; **[GIẢ THUYẾT]** là điều chưa kiểm. Mọi bảng kết quả trong Chương 4 đến Chương 7 đều là **[ĐÃ THỰC NGHIỆM]**, sinh trực tiếp từ tệp kết quả của phiên chạy; không có con số nào được chép tay.

## 1.6. Cấu trúc tài liệu

- **Chương 2** mô tả kiến trúc: hai luồng xử lý (phân tích tài liệu và hỏi đáp), bản đồ hệ thống, vị trí từng mô hình.
- **Chương 3** giới thiệu hai ca minh hoạ dùng xuyên suốt.
- **Chương 4** đi qua 10 bước của luồng phân tích, mỗi bước gồm: mục đích, thuật toán, tham số, kết quả của Ca A và Ca B.
- **Chương 5** trình bày bốn bước có mô hình ngôn ngữ hỗ trợ (mặc định tắt trong sản phẩm): toàn văn prompt, thông điệp thật gửi đi, câu trả lời thô của mô hình và việc bộ kiểm làm với nó.
- **Chương 6** trình bày luồng hỏi đáp qua MCP: chốt phạm vi, lập kế hoạch bằng LLM, gọi công cụ, kiểm câu trả lời; có toàn văn prompt và vết thật.
- **Chương 7** mô tả phần dành cho người soát xét: trạng thái duyệt, giấy làm việc, gợi ý sửa.
- **Chương 8** báo cáo thời gian chạy, bộ nhớ và giới hạn tài nguyên.
- **Chương 9** liệt kê các lỗi đã sửa và các hạn chế quan sát được ngay trên hai ca minh hoạ.
- **Chương 10** mô tả org pack tự phục vụ, vòng học từ phản hồi và giao diện (gồm công tắc mô hình và dòng "Việc tiếp theo").
- **Chương 11** ghi các luật và bộ đo mới sau góp ý chuyên gia (14–16/11).
- **Chương 12** mô tả phân vùng trang và suy luận trên bảng (17/11).
- **Phụ lục** gồm toàn văn mọi prompt, cách tái lập và trích đoạn tệp kết quả.
