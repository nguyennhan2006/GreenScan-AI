# Chương 7. Phần dành cho người soát xét

Hệ thống chỉ sàng lọc; người soát xét ra quyết định. Chương này mô tả ba đầu ra phục vụ việc đó: giấy làm việc, nhật ký quyết định, và gợi ý sửa câu (GreenScan Studio).

## 7.1. Giấy làm việc tiếng Việt (`src/quantum_gw/workpaper.py`)

Giấy làm việc là trang HTML in được ra PDF, dựng từ `result.json` và các quyết định của người soát. Cấu trúc: tiêu đề và cảnh báo diễn giải; bảng thông tin (đơn vị được xem xét, tên phiên, mục tiêu thủ tục, người soát); **1. Phạm vi tài liệu** (danh sách tệp kèm SHA-256 rút gọn, độ phủ bộ tài liệu, năm, mục còn thiếu, và quy tắc hệ thống đã dùng: được nói "chưa được chứng minh" hay chỉ dừng ở "chưa đủ bằng chứng"); **2. Thủ tục đã thực hiện** (số tài liệu, đoạn, tuyên bố, số liệu; phiên bản quy trình, cấu hình, bộ luật, chính sách ưu tiên; phân bố kết quả); **3. Hàng soát và kết quả** (từng mục: hạng, điểm, nguồn và trang, kết quả và lý do, tối đa 3 bằng chứng chính, văn bản pháp lý liên quan, "vì sao mở trước", quyết định mới nhất của người soát hoặc "chưa xem"); **4. Thủ tục trên số liệu công bố**; **5. Những gì KHÔNG được kiểm và vì sao**; **6. Quyết định của người soát xét**; khối chữ ký "Người thực hiện / Người soát xét" và dòng tái lập.

Hai giấy làm việc được sinh từ hai phiên trong tài liệu này (chưa có quyết định nào của người soát, nên mọi mục ghi "chưa xem"):

{{L7_WORKPAPER}}

## 7.2. Nhật ký quyết định của người soát (`src/quantum_gw/storage/reviews.py`)

Mỗi tuyên bố đi qua ba trạng thái: `AI_SUGGESTED` (máy gợi ý) → `HUMAN_REVIEWED` (người đã xem) → `FINALIZED` (đã chốt). Không có đường đi thẳng từ máy gợi ý sang đã chốt.

| Quyết định | Ý nghĩa trên giấy làm việc | Trạng thái mới |
|---|---|---|
| `CONFIRM` | Xác nhận gợi ý của máy | FINALIZED |
| `OVERRIDE` | Sửa gợi ý của máy (bắt buộc ghi kết luận thay thế và lý do) | FINALIZED |
| `ABSTAIN` | Chưa đủ căn cứ để quyết | HUMAN_REVIEWED |
| `REQUEST_EVIDENCE` | Yêu cầu thêm tài liệu | HUMAN_REVIEWED |
| `REOPEN` | Mở lại (chỉ khi đã chốt) | HUMAN_REVIEWED |

Lý do sửa được tách làm hai loại để dùng đúng chỗ: `MODEL_MISREAD` (máy đọc sai) và `EVIDENCE_MISSED` (máy bỏ sót bằng chứng) được chuyển thành nhãn cho việc huấn luyện mô hình; `RULE_NOT_APPLICABLE` (quy tắc không áp dụng) và `RULE_WRONG` (quy tắc cần sửa, bắt buộc ghi mã quy tắc) được chuyển cho người bảo trì luật và **không bao giờ** thành nhãn huấn luyện. Mỗi bản ghi lưu ảnh chụp tuyên bố và bằng chứng lúc quyết định (mã đoạn, trang, quan hệ, mã băm nội dung), ghi nối tiếp vào `.quantum/reviews/decisions.jsonl` (không sửa, không xoá).

Với hai ca trong tài liệu, các quyết định người soát hợp lý nhất là như sau. Ca A: `CONFIRM` cho cả ba tuyên bố mâu thuẫn (A1, năng lượng tái tạo, A2), vì mỗi kết luận có phép tính kiểm lại được. Ở bản ngày 14/11, A2 cần `OVERRIDE` sang `CONTRADICTED` với lý do `EVIDENCE_MISSED`; nay không cần nữa. Ca B: `ABSTAIN` hoặc `REQUEST_EVIDENCE` cho B1, vì 5 đoạn chỉ là tiêu đề cùng chủ đề và cần tài liệu ngoài BCPTBV. Với B2, nên `REQUEST_EVIDENCE` để xin giấy xác nhận khí nhà kính của BSI. Có giấy đó, người soát có thể `OVERRIDE` sang `SUPPORTED` với lý do `EVIDENCE_MISSED`, vì giấy của BSI là nguồn bên ngoài doanh nghiệp, đúng loại mà chốt nguồn độc lập đòi hỏi. Đây là gợi ý của tác giả để minh hoạ cách dùng; các quyết định này **chưa được ghi** vào nhật ký.

## 7.3. Gợi ý sửa câu (GreenScan Studio, `src/quantum_gw/studio/suggest.py`)

Studio cho doanh nghiệp tự soát câu chữ trước khi công bố. Gợi ý sinh hoàn toàn bằng luật, bốn loại:

1. **`soften` — làm mềm cụm nói quá** (mã OC-01 đến OC-05): "trung hoà carbon / net zero" (khi không kèm mốc mục tiêu), "100% xanh", "không phát thải", "thân thiện với môi trường", "hàng đầu / tiên phong / số 1". Căn cứ: Chỉ thị (EU) 2024/825 về tuyên bố môi trường chung chung và Điều 10 Luật Bảo vệ quyền lợi người tiêu dùng 19/2023/QH15 (ghi là "căn cứ ứng viên, chưa có người xác minh").
2. **`placeholder` — chừa chỗ cho số liệu** (VG-01, VG-02): chèn "[bổ sung: số liệu chứng minh — chỉ số, giá trị, đơn vị, kỳ]".
3. **`add_scope` — chừa chỗ cho kỳ, năm gốc, phạm vi** (SC-01).
4. **`evidence_ref` — dẫn chiếu bằng chứng** (EV-01 nối "(xem: tài liệu, tr. X)" khi có đoạn ủng hộ; EV-02 chừa chỗ khi chưa có).

**Quy tắc không bịa số:** mọi câu sau khi sửa đi qua `assert_no_new_numbers`; chỉ được chứa số đã có trong câu gốc và số trang của bằng chứng được dẫn. Gợi ý nào sinh số mới bị loại, không hiển thị. Studio **không viết hộ** tuyên bố: các chỗ trống `[bổ sung: …]` là để doanh nghiệp tự điền bằng số liệu thật.

**Gợi ý cho 5 tuyên bố của Ca A:**

{{L7_STUDIO_A}}

Việc chuyển gợi ý lên mô hình ngôn ngữ (`studio/escalation.py`) chỉ xảy ra khi độ tin thấp hơn ngưỡng `tau`, tài liệu thuộc loại A (công khai) và được phép dùng mạng. Ngưỡng `tau` chưa được hiệu chỉnh (khoá `studio_escalation.tau` chưa có trong `configs/measurement_decisions.yaml`), nên hiện **không gợi ý nào được chuyển lên mô hình**.
