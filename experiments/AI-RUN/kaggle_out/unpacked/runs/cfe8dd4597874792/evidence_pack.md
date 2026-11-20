# Greenwashing-risk evidence pack

> **Kết quả này là tín hiệu rủi ro dựa trên thông tin công khai, hỗ trợ người hành nghề đảm bảo khoanh vùng kiểm tra — không thay thế thủ tục thu thập bằng chứng theo ISSA 5000.**

- Run ID: `cfe8dd4597874792`
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

1. **51/100** · TUYÊN BỐ · — · `CONTRADICTED` — Testing with municipal recycling facilities validated that K-Cup pods could be effectively recycled.
   - Pháp lý: có văn bản đang hiệu lực cùng chủ đề (48/2026/NĐ-CP, 05/2025/NĐ-CP); chưa có quy tắc xác định nghĩa vụ cụ thể.
   - Khoảng trống bằng chứng: kết quả “mâu thuẫn với nguồn”, thiếu 3/4 thuộc tính.

### Scope of this pass

Toàn bộ 1 mục (tuyên bố và số liệu công bố) đều nằm trong hàng đợi soát của lượt này (chính sách `priority-v1.1`).


## Claim assessments

### 1. Testing with municipal recycling facilities validated that K-Cup pods could be effectively recycled.

- Type: `waste_and_circularity`
- Verification: **CONTRADICTED**
- Risk: **65.0/100 (HIGH)**
- Rationale: Bằng chứng đã truy xuất bác bỏ tuyên bố. Bằng chứng phủ định tuyên bố (nguồn có thẩm quyền): “did not”.
- Evidence:
  - `KDP-EV-001.txt (block 1)` (score 0.193): Two large recycling companies reported significant concerns about commercial feasibility and did not intend to accept the pods.
  - `KDP-EV-002.txt (block 1)` (score 0.068): The SEC order found the 2019 and 2020 statements incomplete and inaccurate because the negative feedback was omitted.

## Interpretation notice

This is a screening result, not a legal conclusion. Missing evidence is distinct from contradiction. High-risk outputs require human review.