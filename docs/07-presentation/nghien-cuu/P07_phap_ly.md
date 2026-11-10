# P07 · Pháp lý: gói luật và khả năng áp dụng (applicability)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Gắn tuyên bố với văn bản pháp lý đang hiệu lực và đúng ngành, chủ thể, loại tuyên bố. Cùng chủ đề chưa đủ; phải qua ngày hiệu lực, ngành, chủ thể, loại tuyên bố và điều kiện **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 7).

## 2. Lỗi hoặc rủi ro đã đo được

- Trên 156/156 tuyên bố HPG, không có quy tắc nào áp được. Gói `vn-green-v0.1-draft` chưa có quy tắc cho phát thải, BVMT, phân loại xanh **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, F5).
- Quy tắc nháp nhắm vào loại tuyên bố mà taxonomy không bao giờ sinh ra, nên mọi tuyên bố ra INSUFFICIENT_EVIDENCE về pháp lý, `rules_applied: []` **[ĐÃ THỰC NGHIỆM]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2).
- NĐ 83/2026 (chỉ sửa phần ô-dôn) đi kèm 55 tuyên bố phát thải trước khi sửa; sau khi sửa còn 0 **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, bảng so sánh).

## 3. Thiết kế hiện tại, file code, cấu hình

- Năm lớp dữ liệu pháp lý: văn bản và điều khoản, ma trận nghĩa vụ, sổ bằng chứng công khai, ca đã phán quyết, quy ước gán nhãn **[KIẾN THỨC NỀN]** (`docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 3).
- Cấu hình: `configs/legal/LEGAL_SOURCE_REGISTRY.yaml`, `registry_candidates_2026-10.yaml`, `rule_pack_vn_green_v0.1.yaml` **[KIẾN THỨC NỀN]** (thư mục `configs/legal/`).
- Mã: `src/quantum_gw/legal/` gồm `checker.py`, `corpus.py`, `gates.py`, `parser.py`, `qualifiers.py`, `rules.py` **[KIẾN THỨC NỀN]**.

## 4. Vì sao chọn, phương án đã bỏ

- Tách relevance khỏi applicability, vì chủ đề giống nhau không đủ để áp luật **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 7).
- Bỏ việc áp quy tắc chỉ vì "có vẻ liên quan" **[KIẾN THỨC NỀN]** (cùng file, bảng cấm).
- Chuỗi sửa đổi cũ kéo mọi văn bản sửa NĐ 06/2022 vào mọi tuyên bố; nay chỉ kéo văn bản sửa đúng vấn đề đang xét **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, nguyên nhân 6).

## 5. Số đo có n

- Registry: 12 văn bản đã đối chiếu bản ký **[KIẾN THỨC NỀN]** (`docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`, mục 1).
- Mười văn bản đổi cách kiểm chứng tuyên bố, gồm NĐ 110/2026, QĐ 46/2026 (có hiệu lực 01/11/2026), TT 11/2026, NĐ 180/2026 **[KIẾN THỨC NỀN]** (`docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 0).
- 24 văn bản ứng viên, đã tải đủ 24 bản gốc; 11 bản có lớp chữ, 13 bản scan đã OCR tiếng Việt **[ĐÃ THỰC NGHIỆM]** (cùng file, mục 3).
- Ba thông tư MRV theo ngành (điện và thép, xi măng, giao thông) **[KIẾN THỨC NỀN]** (cùng file, mục 0).

## 6. Giới hạn và yếu tố gây nhiễu

- Luật do người viết, chưa được chuyên gia duyệt. Thảo cần ký `reviewed_by` **[KIẾN THỨC NỀN]** (`docs/07-presentation/nghien-cuu/00_DANH_MUC_CAN_THU_THAP.md`, mục C).
- Tài liệu 02 có 8 chỗ đã cũ hoặc thiếu, đang chờ Thảo xác nhận **[KIẾN THỨC NỀN]** (`docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 0).
- Quốc tế chỉ có bản nháp EU và châu Á, chưa kiểm chứng **[KIẾN THỨC NỀN]** (cùng file, mục 0).

## 7. Lỗi đã gặp và cách gỡ

- NĐ 83/2026 bị gắn sai nhãn phát thải; đã sửa registry **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, nguyên nhân 6).
- Ngày hiệu lực của các nghị định (119/2025, 48/2026, 83/2026) đã sửa theo bản ký **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-04).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Cơ chế áp dụng đã có, nhưng chưa có quy tắc nào được duyệt và áp dụng trên tuyên bố thật **[ĐÃ THỰC NGHIỆM]** (mục 2 ở trên).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Hoàn thiện ma trận nghĩa vụ (L2) theo chủ thể, ngành, quy trình, hạn **[KIẾN THỨC NỀN]** (`docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 3).
- Thu sổ bằng chứng ưu tiên P0, là danh sách Nhãn sinh thái **[KIẾN THỨC NỀN]** (cùng file, mục 3).
- Theo dõi TT 96 đang có dự thảo thay thế **[KIẾN THỨC NỀN]** (`docs/08-knowledge/README.md`, quy tắc 1).

## 10. Hình nên vẽ và file dữ liệu

- Sơ đồ năm lớp dữ liệu pháp lý; bảng ma trận nghĩa vụ theo chủ thể.
- Dữ liệu: `configs/legal/`; `src/quantum_gw/legal/`.
- THIẾU: danh sách quy tắc đã được Thảo ký `reviewed_by`. Cách lấy: Thảo duyệt `rule_pack_vn_green_v0.1.yaml` và ghi trường `reviewed_by`.
