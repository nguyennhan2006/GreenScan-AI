# 06 · Hệ quả cho GreenScan — từ tri thức thành việc cần làm

**Cập nhật:** 06/10/2026 · Nguyên tắc chọn: việc nào **làm sai số liệu, sai pháp lý, hoặc làm hỏng phép đo** thì làm trước; việc nào chỉ thêm tính năng thì sau. Không mở kiến trúc mới trước Bán kết (D-2026-09-18-02).

## 1. Trước product freeze 10/10 — rủi ro thấp, không đổi logic verdict

| # | Việc | Vì sao (tri thức nào) | Ai | Trạng thái |
| --- | --- | --- | --- | --- |
| 1 | Sửa registry: NĐ 119/2025 hiệu lực 01/08/2025; NĐ 48/2026 ngày 29/01/2026; NĐ 83/2026 ngày 23/03/2026 và **bỏ nhãn phát thải** | Đối chiếu bản ký ([02](02_PHAP_LY_VIET_NAM.md) §1); NĐ 83 đang bị trích cho mọi tuyên bố phát thải | Nhân (đã sửa) → **Thảo xác nhận** | ✅ 06/10, chờ xác nhận |
| 2 | **Gộp ứng viên bằng chứng từ mọi bộ truy xuất** (gồm dense qua FPT) trước khi gán nhãn quan hệ ở các lô tiếp theo | Pooling bias làm dense bị đánh giá thấp có hệ thống ([05](05_AI_NLP_VA_DO_LUONG.md) §4) | Nhân | ☐ |
| 3 | Báo cáo đo: bootstrap **theo doanh nghiệp**, kết quả từng doanh nghiệp, macro-F1, baseline lớp đa số, κ kèm khoảng tin cậy và đồng thuận theo lớp | n = 60–100 cho khoảng ±8–11 điểm; tuyên bố cùng doanh nghiệp không độc lập | Nhân | ◐ 06/10: `tools/evaluate_gold.py` đã có macro-F1, ma trận nhầm lẫn, tỷ lệ mâu thuẫn sai, bootstrap từng mục và bootstrap cặp; **thêm** bootstrap theo doanh nghiệp, kết quả từng doanh nghiệp, baseline lớp đa số. Còn thiếu: khoảng tin cậy của κ và đồng thuận theo lớp (`labeling_pack.py kappa`) |
| 4 | Bổ sung `LABELING_CONVENTIONS.md`: chính sách dung sai số; loại hành động *đã làm / đang lên kế hoạch / không rõ*; cột lý do | Climate-FEVER, A3CG, SciFact ([05](05_AI_NLP_VA_DO_LUONG.md) §1–2) | Quỳnh | ☐ |
| 5 | Thêm bẫy hồi quy: **cặp tuyên bố–bằng chứng chỉ khác một con số** | LLM sụp ở đúng kiểu này (NumPert, Aarnes & Setty); giữ comparator làm chủ | Nhân | ☐ |
| 6 | Không gửi tài liệu loại B/C (nội bộ, giấy làm việc kiểm toán) qua chế độ `cloud` | Luật 91/2025, NĐ 356/2025, Luật Kiểm toán độc lập Đ.43 ([02](02_PHAP_LY_VIET_NAM.md) §6) | Cả nhóm (quy tắc vận hành) | ✅ giao diện cảnh báo trước khi chạy |

## 2. Sau freeze, trước Bán kết 25/10 — chỉ trình bày, không thêm kiến trúc

- Slide "Vì sao bây giờ": QĐ 13/2024 (2.166 cơ sở phải kiểm kê), NĐ 119/2025 (lịch kiểm kê có thẩm định độc lập cho nhiệt điện/thép/xi măng từ chu kỳ 2027), QĐ 263/2026 (hạn ngạch cho 110 cơ sở), sàn các-bon HNX (29/06/2026), CBAM chính thức 2026, dự thảo thay TT 96 có phụ lục ESG "công bố hoặc giải trình". Mỗi ý ghi nhãn nguồn.
- Slide "Thực trạng": 28,38% công ty HOSE có BCPTBV (2024); 72,5% báo cáo định tính; 2/22 có đảm bảo; 50,6% quan sát KNK điểm 0 ([03](03_THUC_TRANG_VA_NGHIEN_CUU_VN.md) §1).
- Q&A: dùng 8 câu được nói và 10 câu không được nói ([05](05_AI_NLP_VA_DO_LUONG.md) §6); khung trả lời "lỗi đã đo → lựa chọn thiết kế → cách đo".

## 3. Nếu vào Chung kết (26/10–10/11) — tính năng rút ra từ tri thức, xếp theo giá trị/công sức

| # | Tính năng | Mẫu hình ([01](01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md)) | Công sức | Ghi chú |
| --- | --- | --- | --- | --- |
| 1 | **Cờ "trung hòa nhờ bù trừ"**: từ điển ("trung hòa carbon", "net zero", "bù đắp", "tín chỉ"), yêu cầu nêu cơ chế, phạm vi, mốc ngay cùng trang | 9 | Thấp | Nhóm rủi ro hàng đầu trong án lệ (Katjes, KLM, Delta, 21 hãng bay) |
| 2 | **Quy tắc TT 96 mục 6** với miễn trừ đúng (chỉ 6.1–6.3, chỉ bốn ngành tài chính): báo chỉ tiêu bắt buộc nào vắng mặt | 6, 20, 21 | Trung bình | Là một trong ba quy tắc chờ Thảo |
| 3 | **So chéo kỳ** (cùng doanh nghiệp, hai năm): chỉ tiêu năm trước có, năm nay không → "im lặng có chọn lọc"; điền yếu tố `anomaly` của hàng đợi | 20, bài học 9 | Trung bình | ISSUES P3; corpus 670 tài liệu đã có |
| 4 | Cờ "nghĩa vụ luật trình bày như thành tích" (kiểm kê KNK, QCVN, giấy phép đặt trong mục thành tựu) | 4 | Thấp | Cần quy tắc 1 (QĐ 13) |
| 5 | Cờ "danh hiệu thay bằng chứng" (Top 100, VNSI, giải thưởng) | 18 | Thấp | |
| 6 | Tìm **phản ví dụ** cho tuyên bố phổ quát ("100%", "tất cả", "không có") | 3 (bài học 3) | Trung bình | |
| 7 | So bản BCTN tiếng Anh với tiếng Việt cùng kỳ | 14 | Trung bình | TT 68/2024 bắt buộc bản tiếng Anh thống nhất |
| 8 | **Đo recall** bộ trích tuyên bố (lấy mẫu câu không được trích) | — | Thấp (cần người) | Khoảng cách recall tới 25 điểm ở tiếng Anh |
| 9 | Bộ lọc quan hệ mDeBERTa-xnli trước GLM-5.2; reranker ViRanker/PhoRanker; A/B embedding | — | Trung bình | Chỉ sau khi có gold; theo `configs/measurement_decisions.yaml` |
| 10 | Nguồn đối chiếu ngoài: danh mục Nhãn sinh thái (Bộ NN&MT), danh mục dự án phân loại xanh (QĐ 21/2025 Đ.9), danh sách 110 cơ sở có hạn ngạch, dữ liệu sàn HNX | 8, 17, 9 | Trung bình | Thu thập một lần, gắn ngày |

## 4. Những điều tri thức xác nhận là **không nên** làm

- Không thêm GraphRAG, đa tác tử hay fine-tune chỉ để "AI hơn" — tài liệu không ủng hộ cho bài toán kiểm chứng cục bộ, và gold chưa đủ để chứng minh lợi ích (bất biến kiến trúc, D-2026-09-18-02).
- Không để mô hình tự quyết `SUPPORTED`/`CONTRADICTED` trước khi gold đo được độ chính xác theo từng quan hệ (D-2026-09-28-01; LLM không từ chối khi thiếu ngữ cảnh — Joren và cs. 2025).
- Không gọi kết quả là "tẩy xanh", không xếp hạng doanh nghiệp — kể cả khi hội đồng gợi ý.
- Không dùng số liệu [UNVERIFIED] (khảo sát PwC, mức phạt cụ thể của các nghị định xử phạt) trên slide.
