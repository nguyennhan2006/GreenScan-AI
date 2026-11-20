# Greenwashing-risk evidence pack

> **Kết quả này là tín hiệu rủi ro dựa trên thông tin công khai, hỗ trợ người hành nghề đảm bảo khoanh vùng kiểm tra — không thay thế thủ tục thu thập bằng chứng theo ISSA 5000.**

- Run ID: `55ccc737e3ba437c`
- Pipeline: `pipeline-v1`
- Release status: **PENDING_HUMAN_REVIEW**
- Claims: 1

## Quality gates

- **G0 Dữ liệu đầu vào: PASS** — Mọi đoạn đã tách phải giữ nguồn gốc (tệp, vị trí).
- **G1 Trích xuất đúng nguồn: PASS** — Mỗi tuyên bố giữ đoạn nguồn và vị trí trong tài liệu.
- **G2 Bằng chứng hợp lệ: PASS** — Mỗi tuyên bố có bằng chứng hợp lệ hoặc được ghi rõ là chưa đủ bằng chứng.
- **G3 Kiểm chứng bằng mã cố định: PASS** — Phép so sánh số liệu do mã cố định thực hiện, không do mô hình ngôn ngữ.
- **G4 Trích dẫn đầy đủ: PASS** — Mỗi bằng chứng quyết định đều có vị trí trong tài liệu.
- **G5 Soát rủi ro: PENDING_HUMAN_REVIEW** — Mục rủi ro cao, rất cao hoặc có xung đột pháp lý cần người soát duyệt.
- **G6 Tái lập được: PASS** — Bản kê lượt chạy ghi cấu hình, mã băm tệp đầu vào, hạt giống ngẫu nhiên và kế hoạch.
- **G7 Legal check: PASS** — 1 tuyên bố đã đối chiếu với kho văn bản pháp lý đã đăng ký. 1 tuyên bố chưa kết luận được.
- **G8 Toàn vẹn tài liệu: PASS** — Không thấy chữ ẩn hay câu nhắn tới hệ thống chấm tự động trong tài liệu đầu vào.
- **G9 Chất lượng đọc tài liệu: PASS** — Mọi trang có lớp chữ gốc đọc được; không trang nào phải đọc bằng OCR.

## Review queue — start here

1. **48/100** · TUYÊN BỐ · — · `CONTRADICTED` — ESG risks, opportunities and issues were considered throughout the research process via proprietary quality reviews.
   - Pháp lý: có văn bản đang hiệu lực cùng chủ đề (96/2020/TT-BTC); chưa có quy tắc xác định nghĩa vụ cụ thể.
   - Khoảng trống bằng chứng: kết quả “mâu thuẫn với nguồn”, thiếu 5/5 thuộc tính.

### Scope of this pass

Toàn bộ 1 mục (tuyên bố và số liệu công bố) đều nằm trong hàng đợi soát của lượt này (chính sách `priority-v1.1`).


## Claim assessments

### 1. ESG risks, opportunities and issues were considered throughout the research process via proprietary quality reviews.

- Type: `esg_process_integration`
- Verification: **CONTRADICTED**
- Risk: **70.0/100 (HIGH)**
- Rationale: Bằng chứng đã truy xuất bác bỏ tuyên bố. Bằng chứng phủ định tuyên bố (nguồn có thẩm quyền): “lacked”.
- Evidence:
  - `BNY-EV-001.txt (block 1)` (score 0.185): 67 of 185 investments in one Overlay Fund lacked an ESG quality-review score at the relevant time, nearly 25% of net assets.
  - `BNY-EV-002.txt (block 1)` (score 0.103): The SEC order found that prospectus language could lead a reasonable investor to believe all holdings had been reviewed, when they had not.

## Interpretation notice

This is a screening result, not a legal conclusion. Missing evidence is distinct from contradiction. High-risk outputs require human review.