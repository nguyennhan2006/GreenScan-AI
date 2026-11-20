# Thử GreenScan (bản MCP, máy tối thiểu) trên tài liệu ngoài, 13/11/2026

**Mục đích:** chạy toàn bộ luồng MCP (chốt phạm vi → phân tích → hàng soát → tra cứu → điều phối có API miễn phí) trên báo cáo công khai của doanh nghiệp chưa có trong kho, rồi đo thời gian và bộ nhớ trên laptop của Nhân.

## Tài liệu (công khai, lớp A)

| Tài liệu | Nguồn | Cỡ |
|---|---|---|
| Gemadept, Báo cáo Phát triển bền vững 2024 | [gemadept.com.vn](https://www.gemadept.com.vn/wp-content/uploads/2025/04/20250420-GMD-Bao-cao-phat-trien-ben-vung-2024.pdf) | 19,0 MB |
| Vincom Retail, Báo cáo ESG 2024 | [phattrienbenvung.vincom.com.vn](https://phattrienbenvung.vincom.com.vn/wp-content/uploads/2026/01/VincomRetailESG2024.pdf) | 24,2 MB |

Tệp lưu ngoài repo: `AI quantum/tai_lieu_ngoai_2026-11-13/`. Mã chạy thử: `scratchpad/thu_ngoai.py` (hàm của `quantum_gw.mcp_tools` và `agent_harness`, hồ sơ `offline`).

## Máy

- i7-1355U, 15,6 GB RAM. Lúc bắt đầu còn trống 2,7 GB, lúc thấp nhất 1,7 GB.
- **Không tắt app nào:** đỉnh đo được của tiến trình là 1,6 GB, vẫn dưới phần RAM trống. Chrome, VS Code, Claude, Zalo để nguyên.

## Kết quả

| | Gemadept | Vincom Retail |
|---|---|---|
| Phân tích (`analyze_documents`) | 108 s (lần 1) / 202 s (lần đo bộ nhớ, máy bận hơn) | 54 s |
| **Đỉnh bộ nhớ tiến trình** | **1.619 MB** | (nhỏ hơn: ít đoạn hơn) |
| Đoạn văn / câu được xét | 832 / 326 | 700 / 159 |
| Hàng soát | **19** tuyên bố; 310 câu để ngoài vì nghi không phải tuyên bố (mục lục, ô bảng, tiêu đề dính nhau) | **9**; 157 câu để ngoài |
| Kết luận | 326/326 PARTIALLY_SUPPORTED | 159/159 PARTIALLY_SUPPORTED |
| `find_evidence` | 0,5 s lần đầu, 0,07 s khi đã có đệm | 0,7 s / 0,08 s |
| `claim_attributes` | 0,02 s | 0,03 s |
| Câu hỏi rủi ro (API) | 4,2 s, 2 lời gọi, câu trả lời LLM qua bộ kiểm | 2,4 s, câu LLM bị chặn (có số không nằm trong kết quả) → dùng mẫu của luật |
| Câu hỏi kiểm tra một tuyên bố (API) | 8,1 s; LLM chọn `verify_claim` → `claim_attributes` → `explain_claim`; câu trả lời qua bộ kiểm | 7,6 s; API trả lỗi HTTP (nhiều khả năng giới hạn tần suất của gói miễn phí) → kế hoạch và câu trả lời theo luật |
| "… có gian lận số liệu phát thải không?" | **dừng ngay**, cảnh báo `legal_or_fraud_verdict`, 0 lời gọi | như vậy |
| "Viết lại đoạn PTBV cho nghe xanh hơn" | **dừng ngay**, cảnh báo `write_or_embellish_claims` | như vậy |

**Ví dụ câu trả lời** (Gemadept, tuyên bố đứng đầu hàng soát):

> Tuyên bố "Kiến tạo Xanh trong công nghệ" của Gemadept được công cụ xác nhận là PARTIALLY_SUPPORTED. Có bằng chứng về việc áp dụng Smart Port, Auto Gate, River Gate và lợi ích giảm năng lượng, giảm phát thải, nhưng tài liệu chưa cung cấp số liệu cụ thể, kỳ báo cáo, năm gốc để so sánh và phạm vi áp dụng. Nên làm tiếp: thu thập số liệu chi tiết, xác định kỳ báo cáo và năm cơ sở, và làm rõ phạm vi áp dụng.

## Cách đọc

1. **Mọi kết luận đều là "hỗ trợ một phần".** Đây là luật của sản phẩm, không phải lỗi: khi chỉ có báo cáo của chính doanh nghiệp, đoạn tự xác nhận không được tính là bằng chứng độc lập. Muốn có SUPPORTED hay CONTRADICTED thì phải thêm tài liệu khác, ví dụ báo cáo thường niên, báo cáo tài chính, tờ đảm bảo độc lập hoặc dữ liệu của cơ quan quản lý.
2. **Hàng soát lọc rất mạnh.** 95% câu được xét bị để ngoài vì nghi là mục lục, ô bảng hoặc tiêu đề. Người soát chỉ cần đọc 19 câu (Gemadept) và 9 câu (Vincom Retail).
3. **Đầu hàng soát của Vincom Retail là một số liệu tự công bố** ("Tổng: 153.646.550 kWh"), không phải câu tuyên bố, nên công cụ tra kết luận báo "chưa xét" và trả thuộc tính cùng bằng chứng. Hành vi này đúng nhưng còn thô: số liệu cần có công cụ kiểm số riêng.

## Đã sửa trong lượt thử

- **Thêm công cụ `review_queue`** (MCP và harness) để đọc hàng soát mà quy trình đã xếp. Trước đó câu hỏi rủi ro gọi `get_claims` lọc theo trạng thái, ra 0 kết quả. Việc `assess_report_risk` giờ đi vào `review_queue`. Máy chủ MCP có 11 công cụ; bài kiểm qua 13/13.
- Sửa cách đo đỉnh bộ nhớ trên Windows (khai báo kiểu handle 64-bit cho `K32GetProcessMemoryInfo`).

## Việc nên làm tiếp

- Công cụ kiểm số liệu tự công bố (`figure_checks` trong `result.json`) cho mục "số liệu" ở hàng soát.
- Gói miễn phí của Groq giới hạn tần suất: harness đã tự lùi về luật, nhưng nên thêm chờ rồi thử lại một lần cho lỗi 429.
- Thử bộ hồ sơ có thêm tài liệu độc lập (báo cáo thường niên kèm tờ đảm bảo) để xem có kết luận khác "một phần" không.
