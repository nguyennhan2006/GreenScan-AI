# R4: Pháp lý Việt Nam và quốc tế; chuẩn mực kế toán – kiểm toán – công bố bền vững

*Ghi 04/11/2026 cho phần hỏi đáp Chung kết 10/11/2026. Đây là ghi chú để đội trả lời BGK, **không phải tư vấn pháp lý**. Mọi điểm có nhãn [CHƯA XÁC MINH] hoặc "chờ Thảo" không được nói như kết luận. Đường dẫn tính từ gốc repo `GreenScan-AI/`; `TXT/` = `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt\`.*

**Nguồn đã đọc**
- Bảy tài liệu được giao, đọc toàn bộ: `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`; `docs/08-knowledge/03_THUC_TRANG_VA_NGHIEN_CUU_VN.md`; `configs/legal/LEGAL_SOURCE_REGISTRY.yaml`; `configs/legal/rule_pack_vn_green_v0.1.yaml`; `docs/07-presentation/nghien-cuu/P07_phap_ly.md`; `docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`.
- `docs/08-knowledge/sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md` (khoảng 165 KB): đọc kỹ mục 0, Tóm tắt điều hành, Phần A (A.1–A.6), Phần B, D.1 và Phần E. **Bỏ qua** Phần C (danh mục học thuật), D.2 (bảng vụ quốc tế) và danh mục tham khảo, vì thuộc cụm án lệ và học thuật, không phải luật hay chuẩn mực.
- Đọc thêm để trả lời F5 và câu hỏi trách nhiệm:
  - `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0–2 và mục 10;
  - mã: `src/quantum_gw/legal/checker.py` (toàn bộ), `rules.py` (`for_claim`, `applies_to`, `combine`), `gates.py` (định nghĩa cổng);
  - `docs/00-project/ARCHITECTURE_INVARIANTS.md` (10 bất biến) và `configs/default.yaml` dòng 68;
  - `data/legal/clauses/*.jsonl`: đếm dòng, tra Điều 4.2 TT 96 và Điều 4.2 QĐ 21;
  - `docs/08-knowledge/sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md` §6 (luật dữ liệu);
  - text trích sẵn: `TXT/GreenScan_100_Cau_BGK.txt` (mục C, Q59–Q82), `TXT/ho_so_nguyen_ly_hoi_dong.txt` (trang 2 và 5), `TXT/the_le_cuoc_thi.txt` (tiêu chí pháp lý và đạo đức), `TXT/AI-QUANTUM_AGENT_CRITERIA_v1.txt` (đề bài), `TXT/lizama_v_hm_complaint.txt` (trang 1, 7–8).
- Tra web ngày 04/11/2026. **Chỉ đọc phần tóm tắt trong kết quả tìm kiếm, chưa mở toàn văn**:
  - [IAASB FAQ ISSA 5000](https://ifacweb.blob.core.windows.net/publicfiles/2025-08/IAASB-ISSA-5000-FAQ-Applicability-ISAE-3000-3410.pdf);
  - [IFRS Foundation, sửa đổi IFRS S2](https://www.ifrs.org/projects/completed-projects/2025/amendments-to-disclosure-of-greenhouse-gas-emissions-s2/);
  - [GRI 103 FAQ](https://www.globalreporting.org/media/mead5ytn/gri-103-energy-2025-frequently-asked-questions-faqs.pdf) và [BDO về GRI 102/103](https://www.bdo.ch/en-gb/insights/gri-updates-2025-2027-transparency-and-impact-in-sustainability);
  - [lsvn.vn, dự thảo thay TT 96 (22/10/2026)](https://lsvn.vn/huong-dan-cong-bo-thong-tin-tren-thi-truong-chung-khoan-a180456.html);
  - [luatvietnam, QĐ 345/QĐ-BTC](https://luatvietnam.vn/tai-chinh/quyet-dinh-345-qd-btc-2020-de-an-ap-dung-chuan-muc-bao-cao-tai-chinh-181513-d1.html).
- **Không đọc được, hoặc không có:**
  - Danh mục được giao không có PDF (toàn .md và .yaml), nên không cần chạy PyMuPDF.
  - Toàn văn ISAE 3000, ISSA 5000, IFRS S1/S2, GRI, ESRS không có trong repo. Phần quốc tế dựa trên mục A.5 và E của tài liệu nguồn, kiến thức nền và kết quả tìm kiếm, có ghi nhãn.
  - File điều khoản Luật BVMT trong repo **vẫn chỉ có Điều 1–89** (kiểm 04/11: 938 dòng, không có điều nào từ 90 trở lên). Vì vậy Điều 91, 114, 119, 139, 145, 149, 150 chưa nằm trong file điều khoản.

---

## 1. Tóm tắt từng tài liệu

### 1.1 `02_PHAP_LY_VIET_NAM.md` (06/10; đầu file có cờ "8 điểm đã cũ", ghi 13/10)
- **Là gì:** bảng tổng hợp pháp lý Việt Nam cho tuyên bố môi trường, dùng để định hướng kỹ thuật.
- **Luận điểm chính:**
  1. Ngày ký và ngày hiệu lực đã đối chiếu với bản ký số. Đã sửa ba lỗi: NĐ 119/2025 có hiệu lực 01/08/2025; NĐ 48/2026 ký và có hiệu lực 29/01/2026; NĐ 83/2026 ký và có hiệu lực 23/03/2026, **chỉ sửa phần ô-dôn/HFC**.
  2. Nghĩa vụ đặt lên các chủ thể khác nhau:
     - **cơ sở** (QĐ 13/2024, 2.166 cơ sở);
     - **công ty đại chúng** (TT 96, Phụ lục IV mục 6);
     - **tổ chức tín dụng** (TT 17/2022);
     - **tổ chức phát hành trái phiếu xanh** (Luật BVMT Điều 150.3; NĐ 08 Điều 157.6);
     - **chủ dự án** (QĐ 21/2025);
     - **người bán sản phẩm "thân thiện môi trường"** (Luật BVMT Điều 145).
  3. Việt Nam **không có luật riêng về green claims**. Các "móc pháp lý" chỉ dùng làm **ngữ cảnh**: Luật 19/2023 Điều 10.1(a), Luật Quảng cáo Điều 8 và 19, Luật Cạnh tranh Điều 45, Luật BVMT Điều 6.9, NĐ 29/2026 Điều 4.5.
  4. Thị trường các-bon có nguồn đối chiếu mới: 110 cơ sở có hạn ngạch.
  5. Luật dữ liệu: Luật 91/2025 và NĐ 356/2025 (NĐ này **bãi bỏ NĐ 13/2023**). Từ đó có quy tắc vận hành theo loại tài liệu A/B/C.
- **Liên quan GreenScan:** là nguồn cho registry, cho ba quy tắc ưu tiên ở §7 và cho chế độ chạy theo loại tài liệu.
- **Giống và khác:** GreenScan giống ở chỗ coi luật là điều kiện gắn với chủ thể và ngày. Khác ở chỗ tài liệu đề xuất ba quy tắc, còn gói luật mới có **một quy tắc nháp, và nó không thuộc ba quy tắc đó**.

### 1.2 `03_THUC_TRANG_VA_NGHIEN_CUU_VN.md`
- **Số liệu chính:**
  - Tỷ lệ công ty HOSE có báo cáo phát triển bền vững: 1,06% (2015) → **28,38%** (107 công ty, 2024).
  - Báo cáo định tính: 94,4% → **72,5%**.
  - Chỉ **2/22** báo cáo độc lập có đảm bảo bên thứ ba (ACB, VNM).
  - Công bố KNK: **50,6%** quan sát đạt điểm 0; chỉ 21,3% công bố đầy đủ.
  - Tuân thủ công bố bắt buộc theo TT 155/2015: phần môi trường thấp nhất, 40,75%.
  - Tỷ lệ áp dụng GRI 19–25%. Dư nợ tín dụng xanh khoảng 750.000 tỷ đồng, khoảng 5% tổng dư nợ.
- **Hàm ý cho sản phẩm:**
  - Kết quả phổ biến nhất trên dữ liệu thật sẽ là "chưa đủ bằng chứng" (khớp HPG 153/156), nên **hàng đợi ưu tiên** mới là sản phẩm.
  - "Có hay không đảm bảo, ai đảm bảo, phạm vi nào" nên là trường của bằng chứng.
  - Với ngân hàng: kiểm nhất quán chuỗi thời gian, không kiểm KNK.
- **Câu nói an toàn về khoảng trống nghiên cứu:** "trong phạm vi đã rà, chúng tôi không tìm thấy nghiên cứu Việt Nam nào kiểm chứng số liệu của từng tuyên bố".
- **Chuẩn mềm** UBCKNN–IFC (2013, 2015/16, *Little Book of GHG* 2023, *ESG Handbook* 2024): dùng làm checklist kỳ vọng, không phải nghĩa vụ.

### 1.3 `sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md` (tài liệu gốc, 05/10)
- **Phần A:**
  - Chi tiết từng văn bản, có trích nguyên văn.
  - A.3: các văn bản repo còn thiếu (BVQLNTD, Quảng cáo, Cạnh tranh, xử phạt, trái phiếu xanh, các-bon, NHNN, ISSB).
  - A.3.9: rà toàn văn 14 văn bản, **không thấy** chữ "tẩy xanh" hay "greenwash".
  - A.4: lịch kiểm kê theo NĐ 119 cho từng loại cơ sở; TT 96 còn hiệu lực; miễn trừ **chỉ 6.1–6.3**.
  - A.5: áp lực từ bên ngoài: CBAM từ 01/01/2026; ECGT 2024/825 áp dụng từ 27/09/2026; Green Claims Directive đang "Blocked"; Omnibus 2026/470; ISSB ở ASEAN (Việt Nam không có hồ sơ).
  - A.6: bảy đề xuất cho registry và bộ quy tắc.
- **Phần B:** số liệu thị trường như tài liệu 03.
- **D.1:** chưa tìm thấy vụ nào ở Việt Nam bị xử phạt vì green claim (bằng chứng phủ định có giới hạn). Formosa và Vedan là vụ ô nhiễm, không phải vụ tuyên bố xanh.
- **Phần E:**
  - Định nghĩa của ESAs 2024, ECGT, CMA (6 nguyên tắc), FTC 16 CFR 260, ASIC INFO 271, TerraChoice và các nguồn học thuật.
  - Bảng typology 21 mẫu hình, ánh xạ sang điều luật Việt Nam đã xác minh, có cột "Tự động?".
- **Định vị GreenScan (E.2):** chỉ gắn tín hiệu rủi ro gây hiểu nhầm ở cấp tuyên bố và mức đủ bằng chứng. Với BCTN gửi nhà đầu tư, khung tham chiếu phù hợp nhất là **ESAs**; ECGT, CMA và FTC chủ yếu điều chỉnh quan hệ B2C.
- **Khác:** GreenScan chưa làm mẫu 16 (hình ảnh, vì pipeline chỉ đọc chữ) và mẫu 21 (cần dữ liệu xử phạt công khai).

### 1.4 `LEGAL_SOURCE_REGISTRY.yaml` (v0.1, tạo 09/08/2026, sửa 06/10)
- Có **11 văn bản**. Mỗi văn bản có:
  - số hiệu, cơ quan ban hành, ngày ký, ngày hiệu lực, trạng thái;
  - `legal_issues` và các quan hệ `amends` / `amended_by` / `implements` / `legal_basis`;
  - URL chính thức;
  - `text_acquisition` (ok hoặc ok_ocr), kèm độ tin cậy OCR trung bình 88,08–95,9;
  - `clauses_file`.
- Bản ghi NĐ 83/2026 có chú thích: trong toàn văn, "chất được kiểm soát" xuất hiện 66 lần, "kiểm kê khí nhà kính" 0 lần. Các chỗ sửa này **chờ Thảo xác nhận**.
- **Còn thiếu so với mục A.6 và tài liệu v4:**
  - `amended_by` cho Luật BVMT (6 luật sửa đổi) và TT 96 (TT 68/2024, 18/2025, 08/2026);
  - NĐ 110/2026 trong `amended_by` của NĐ 08;
  - QĐ 46/2026 và các văn bản ứng viên khác.
- Ghi chú "harvest pending" của TT 17 đã cũ, vì file điều khoản đã có.

### 1.5 `rule_pack_vn_green_v0.1.yaml`
- **Nguyên tắc:**
  - Quy tắc chỉ vào sản phẩm qua đường "draft → human legal review → unit tests → version bump".
  - "Nothing reads a statute and generates its own rule at runtime."
  - Trường `machine_executable` khai thật mức máy tự quyết: `full` / `partial` / `none`.
- **Nội dung:** đúng **một** quy tắc, `VN_GREEN_TAXONOMY_001` (QĐ 21/2025):
  - `claim_types: [green_project, green_taxonomy_eligibility]`;
  - `source_clauses: []`, `reviewed_by: ''`;
  - ba điều kiện: hai điều kiện `terms_present` dò từ khóa ("dự án", "phát thải"…), một điều kiện `manual` có chủ đích (tính hợp lệ của văn bản xác nhận là phán đoán pháp lý).
- Ghi chú STATUS 09/08 nói QĐ 21 là bản scan không trích được. Ghi chú này **đã cũ**: registry nay ghi ok_ocr, độ tin cậy 93,25, và file điều khoản có 137 dòng.

### 1.6 `P07_phap_ly.md`
- **Số đo của đội:**
  - 0 quy tắc áp được trên 156/156 tuyên bố HPG.
  - Quy tắc nháp nhắm vào loại tuyên bố mà taxonomy không sinh ra, nên `rules_applied: []`.
  - Trước khi sửa, NĐ 83/2026 bị trích kèm **55 tuyên bố phát thải**; sau khi sửa còn **0**.
- **Trạng thái:** IMPLEMENTED–NOT VALIDATED.
- **Hướng tiếp:** ma trận nghĩa vụ (L2); sổ bằng chứng P0 là danh sách Nhãn sinh thái; theo dõi dự thảo thay TT 96.

### 1.7 `KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`
- **Mười văn bản đổi cách kiểm chứng:**
  - NĐ 110/2026 (EPR);
  - **QĐ 46/2026**: chế độ "dự án xanh, tuần hoàn, ESG" thứ hai, **có hiệu lực 01/11/2026**;
  - TT 11/2026 (sổ đăng ký tín chỉ);
  - NĐ 180/2026 (tín chỉ các-bon rừng);
  - QCVN 19:2024 (khí thải công nghiệp);
  - NĐ 37/2026 (nhãn hàng hóa);
  - NĐ 87/2026 (xử phạt quảng cáo);
  - CV 10612 (danh sách 21 giấy chứng nhận Nhãn sinh thái);
  - TT 09/2026 (báo cáo công tác BVMT).
- **Ba thông tư MRV theo ngành:** TT 38/2023/TT-BCT (điện, thép), TT 13/2024/TT-BXD (xi măng), TT 63/2024/TT-BGTVT (giao thông).
- **Phần khác:**
  - 8 điểm của tài liệu 02 cần sửa (§2).
  - Năm lớp dữ liệu L1–L5 (§3). Đã tải đủ 24 văn bản ứng viên: 11 có lớp chữ, 13 bản scan đã OCR tiếng Việt.
  - Danh sách sổ bằng chứng theo ưu tiên; mở rộng ngành; đề xuất quy ước Q18–Q24.
- **Hai chế độ kiểm theo thời gian (§6):**
  - Cơ sở đang hoạt động được dùng QCVN cũ đến 31/12/2031.
  - EPR: năm báo cáo đến 2025 theo NĐ 08, từ 2026 theo NĐ 110.
  - Dự án xanh: từ 01/11/2026 có hai bộ tiêu chí.
  - **Thông tin bắt buộc trong BCTN không phải quảng cáo** (Luật 75/2025 Điều 19.3(b)).
- **Rủi ro đã nêu:**
  - Tìm không ra không có nghĩa là không có.
  - Không gắn quy tắc dựa trên nguồn thứ cấp.
  - Báo chí từng ghi sai ngày: NĐ 180 có hiệu lực 15/07, không phải 01/07; TT 11 có hiệu lực 30/03, không phải 13/02.

### 1.8 Từng văn bản Việt Nam: liên quan gì tới tuyên bố xanh, GreenScan dùng ở đâu, vì sao chưa thành quy tắc

| Văn bản (hiệu lực) | Điều chạm tuyên bố xanh | GreenScan dùng ở đâu (04/11) | Vì sao chưa có quy tắc áp được |
|---|---|---|---|
| Luật BVMT 72/2020/QH14 (01/01/2022; sửa tới Luật 146/2025, có hiệu lực 01/01/2026) | Đ.6.9: cấm gian dối **dẫn đến hậu quả xấu**. Đ.91.7: nghĩa vụ kiểm kê ở **cơ sở**. Đ.119: báo cáo công tác BVMT hằng năm. **Đ.145**: sản phẩm thân thiện môi trường phải được cơ quan có thẩm quyền chứng nhận hoặc công nhận. Đ.149–150: tín dụng và trái phiếu xanh; Đ.150.3 buộc cung cấp ĐTM, giấy phép, việc sử dụng vốn | Registry; file điều khoản (chỉ Đ.1–89) | Các điều quan trọng (từ Đ.90 trở đi) chưa có trong file điều khoản, nên không bind được. Đ.6.9 có điều kiện "hậu quả xấu", máy không quyết được |
| NĐ 08/2022 (sửa bởi 05/2025, 48/2026; NĐ 110/2026 bãi bỏ Chương VI về EPR) | Đ.145–150: Nhãn sinh thái, hiệu lực 36 tháng, Bộ công bố danh mục. Đ.157.6: trái phiếu xanh công bố hằng năm đến khi đáo hạn. Đ.64: túi ni lông và nhựa dùng một lần | Registry; file điều khoản (OCR 95,9) | Muốn kiểm "có Nhãn sinh thái" phải có sổ bằng chứng (CV 10612, ưu tiên P0), **chưa tải**. Registry chưa ghi NĐ 110 |
| NĐ 06/2022 (sửa bởi 119/2025, 83/2026) | Đ.6.1: ngưỡng phải kiểm kê. Đ.10.3: báo cáo giảm nhẹ hằng năm từ 2027. Đ.11.4: lịch kiểm kê. Đ.11.6a: thẩm định độc lập. Đ.19: tín chỉ, bù trừ ≤ 30%, tín chỉ tự nguyện đã dùng không được giao dịch tiếp | Registry; file điều khoản; chuỗi sửa đổi trong corpus | **Không có quy tắc nào** cho vấn đề `emissions` hay `ghg_inventory`. Nghĩa vụ ở cơ sở, phải ánh xạ cơ sở ↔ công ty con ↔ công ty niêm yết (lớp L2, chưa làm) |
| QĐ 13/2024/QĐ-TTg (01/10/2024) | Danh mục 2.166 cơ sở phải kiểm kê (tính theo TOE) | Registry; file điều khoản; danh sách cơ sở đã có | Chưa có quy tắc "thuộc diện", chưa ánh xạ tên cơ sở với doanh nghiệp niêm yết |
| QĐ 21/2025/QĐ-TTg (22/08/2025) | Đ.3: tiêu chí. Đ.4: xác nhận bởi cơ quan, hoặc tổ chức đạt **ISO/IEC 17029 hoặc VSAE/ISAE 3000**; tổ chức xác nhận **chịu trách nhiệm trước pháp luật** về kết quả. Đ.8–9: Bộ công bố danh mục. Phụ lục I là "từ điển bằng chứng" | Registry (OCR 93,25); 137 dòng điều khoản; **quy tắc nháp duy nhất** | Quy tắc chưa bind điều khoản (`source_clauses` rỗng), chưa có người ký, `claim_types` không khớp taxonomy. Thẩm quyền ban hành nay chuyển cho Bộ trưởng NN&MT (NĐ 48 Đ.31) |
| QĐ 46/2026/QĐ-TTg (**01/11/2026**) | Chế độ dự án xanh, tuần hoàn, ESG thứ hai; xác nhận theo ISO/IEC 17029 hoặc VSAE/ISAE 3000; tỉnh công bố danh mục mỗi 30/6 và 31/12 | Chỉ có trong file ứng viên (đã tải) | Chưa vào registry, chưa được duyệt. Đợt danh mục đầu tiên chưa có |
| TT 17/2022/TT-NHNN (01/06/2023) | Quản lý rủi ro môi trường của dự án thuộc Phụ lục III–V NĐ 08. Đ.5: thông tin phục vụ quản lý rủi ro. Khách hàng chịu trách nhiệm về tính chính xác của thông tin | Registry; file điều khoản; là lý do người dùng đầu tiên là ngân hàng | Không đặt nghĩa vụ lên doanh nghiệp báo cáo, không định nghĩa tín dụng xanh, nên không có điều kiện để kiểm một tuyên bố. Một phần phụ lục NĐ 08 đã bị NĐ 48 Đ.35 thay |
| TT 96/2020/TT-BTC (01/01/2021; sửa bởi 68/2024, 18/2025, 08/2026; có dự thảo thay thế) | Đ.4.2: trách nhiệm về thông tin công bố. Đ.10.2: hạn công bố BCTN. Phụ lục IV mục 6.1–6.8; **miễn 6.1–6.3** cho bốn ngành tài chính. TT 68/2024: bản tiếng Anh phải thống nhất với bản tiếng Việt | Registry; 327 dòng điều khoản; dùng làm **bộ chỉ tiêu kỳ vọng** | Chưa viết quy tắc. Không tìm thấy trong corpus chưa phải là không công bố (cần kiểm độ đầy đủ của corpus, lỗi mở B10). TT 96 không quy định Scope, ranh giới, năm gốc hay đảm bảo |
| Luật BVQLNTD 19/2023 (01/07/2024), NĐ 55/2024; NĐ 98/2020 sửa bởi NĐ 24/2025 | Đ.10.1(a): cấm gây nhầm lẫn bằng thông tin sai lệch, không đầy đủ, kể cả về **giấy tờ chứng nhận** | File ứng viên; dự kiến làm "tham chiếu ngữ cảnh" | Điều chỉnh quan hệ với người tiêu dùng, không áp trực tiếp cho BCTN gửi nhà đầu tư |
| Luật Quảng cáo 16/2012 sửa bởi 75/2025 (01/01/2026); NĐ 342/2025; NĐ 87/2026 về xử phạt (15/05/2026) | Đ.8.9: cấm gây nhầm lẫn. Đ.8.10: so sánh phải có tài liệu chứng minh. Đ.8.11: "nhất", "số một" phải chứng minh. Đ.19: nội dung trung thực. **Đ.19.3(b): thông tin bắt buộc công bố không phải quảng cáo** | File ứng viên; ngữ cảnh | Chỉ áp khi nội dung BCTN được dùng lại trong truyền thông |
| Luật Cạnh tranh 23/2018 Đ.45 (xử phạt theo NĐ 75/2019) | Thông tin gian dối để lôi kéo khách hàng; so sánh không chứng minh được | File ứng viên | Nguồn thứ cấp; điều chỉnh quan hệ cạnh tranh |
| NĐ 29/2026, QĐ 263/2026, TT 11/2026, NĐ 180/2026 | Cấm thông tin sai lệch để thao túng giá tín chỉ (NĐ 29 Đ.4.5); sổ đăng ký công khai tín chỉ đã hủy để bù trừ (TT 11) | TT 11 và NĐ 180 có trong file ứng viên | Sổ bằng chứng chưa thu (TT 11: P1; dữ liệu HNX: P1) |
| NĐ 37/2026 về nhãn hàng hóa (23/01/2026) | Đ.50.1: tuyên bố xanh trên nhãn phải trung thực, chính xác | File ứng viên | Điều chỉnh nhãn sản phẩm, chưa được duyệt |
| Luật BVDLCN 91/2025 + NĐ 356/2025; Luật Kiểm toán độc lập 67/2011 Đ.43; Luật AI 134/2025 + NĐ 142/2026 | Không điều chỉnh tuyên bố xanh mà điều chỉnh **việc vận hành GreenScan**: chuyển dữ liệu xuyên biên giới, mã hóa trên đám mây, bảo mật hồ sơ kiểm toán, phân loại rủi ro AI và gắn nhãn | Quy tắc tài liệu A/B/C; demo chạy `offline`; Groq và Kaggle chỉ dùng cho báo cáo đã công bố | Đây là ràng buộc triển khai, không phải quy tắc kiểm tuyên bố |

### 1.9 Chuẩn mực và luật quốc tế (repo không có toàn văn)

| Chuẩn/luật | Điểm chạm tuyên bố xanh | GreenScan dùng ở đâu | Giống / khác |
|---|---|---|---|
| ISAE 3000 (Revised) / VSAE 3000; ISAE 3410 (KNK) | Dịch vụ đảm bảo thông tin phi tài chính, mức **hạn chế** hoặc **hợp lý** | QĐ 21/2025 và QĐ 46/2026 công nhận VSAE/ISAE 3000 cho tổ chức xác nhận. GreenScan ghi "có hay không đảm bảo, ai, phạm vi nào" thành trường của bằng chứng | Giống tư duy "tiêu chí phù hợp + bằng chứng đủ và thích hợp + kết luận có giới hạn". **Khác:** GreenScan không có hợp đồng dịch vụ, không phát hành kết luận đảm bảo, không chịu trách nhiệm nghề nghiệp |
| ISSA 5000 (IAASB) | Chuẩn chung cho dịch vụ đảm bảo thông tin bền vững; áp cho kỳ bắt đầu từ **15/12/2026**. Từ mốc đó ISAE 3000 không còn áp cho đảm bảo bền vững và ISAE 3410 bị rút | Bối cảnh cho báo cáo năm 2027 trở đi | Việt Nam chưa có chuẩn tương ứng [CHƯA XÁC MINH] |
| IFRS S1/S2 (ISSB) | 4 trụ cột: Quản trị, Chiến lược, Quản lý rủi ro, Chỉ số và mục tiêu. IFRS S2 yêu cầu Scope 1, 2, 3 theo GHG Protocol; sửa đổi 12/2025 | Thuộc tính của tuyên bố (chỉ số, Scope, kỳ, năm gốc, ranh giới) bám IFRS S2 §29 và GHG Protocol (`docs/00-project/RESEARCH_PROGRAM_2026-09-22.md`, RQ2) | Việt Nam chưa có lộ trình áp dụng chính thức |
| GRI | GRI 305 (KNK), GRI 302 (năng lượng); GRI 102 và GRI 103 có hiệu lực 01/01/2027 | Định nghĩa chỉ số; 19–25% doanh nghiệp HOSE có áp dụng GRI | Trọng yếu **tác động**; là chuẩn tự nguyện, không phải luật |
| ESRS (thuộc CSRD) | ESRS E1 về khí hậu; trọng yếu **kép**; Omnibus đã thu hẹp phạm vi | Chỉ tham chiếu cấu trúc | Doanh nghiệp Việt Nam chỉ chịu gián tiếp qua chuỗi giá trị |
| Chỉ thị (EU) 2024/825 (ECGT) | Cấm tuyên bố chung chung, nhãn không dựa trên certification scheme, tuyên bố trung hòa cấp sản phẩm dựa trên bù trừ, trình bày yêu cầu luật như ưu điểm. Tuyên bố tương lai cần kế hoạch có kiểm định độc lập | Typology mẫu 1, 4, 8, 9, 10 | Điều chỉnh B2C. Báo cáo bắt buộc gửi nhà đầu tư **thường nằm ngoài phạm vi** (Q&A, câu Q1) |
| UK CMA Green Claims Code | 6 nguyên tắc | Checklist | Hướng dẫn dựa trên luật bảo vệ người tiêu dùng |
| US FTC Green Guides (16 CFR 260) | §260.2 "reasonable basis"; §260.4 tuyên bố lợi ích chung chung; §260.5 bù trừ các-bon; §260.12 ngưỡng 60% cho "recyclable" | Checklist. Ví dụ vụ *Lizama & Doten v. H&M* (E.D. Mo., 4:22-cv-01170, nộp 03/11/2022) dẫn §260.3–260.4 | Bản hướng dẫn chưa được sửa đổi |
| ESAs (ESMA/EBA/EIOPA) | Định nghĩa greenwashing cho thị trường tài chính; 12 "misleading qualities" | Khung định vị chính khi xét BCTN gửi nhà đầu tư | Có thể xảy ra "intentionally or unintentionally" |
| ASEAN Taxonomy; SASB | Đề bài liệt kê là "dữ liệu chuẩn hóa" (`TXT/AI-QUANTUM_AGENT_CRITERIA_v1.txt`) | Chưa dùng | [CHƯA XÁC MINH] phiên bản hiện hành của ASEAN Taxonomy |

---

## 2. Khái niệm và lý thuyết phải nắm

**2.1 Liên quan (relevance) khác áp dụng được (applicability)** (bất biến 7)
- Một quy tắc chỉ được áp khi đi qua đủ năm bộ lọc theo thứ tự: **ngày hiệu lực → ngành → chủ thể → loại tuyên bố → điều kiện**.
- Quy tắc bị loại phải ghi lý do (trường `not_applicable_rules`).
- Ví dụ: TT 17 (thông tư cho ngân hàng) không được áp cho nhà máy thép. NĐ 83 (chỉ về ô-dôn) không được trích cho tuyên bố KNK; sửa đúng chỗ này làm số trích dẫn sai giảm từ 55 xuống 0.

**2.2 Policy-as-code: luật viết thành mã** (`rules.py`)
- Một quy tắc là phép AND của các điều kiện nguyên tử. Mỗi điều kiện ra một trong ba kết quả: SATISFIED (đạt), NOT_SATISFIED (không đạt), UNKNOWN (chưa biết).
- Hàm `combine` gộp kết quả:
  - có điều kiện NOT_SATISFIED → `NOT_MATCH`;
  - mọi điều kiện SATISFIED → `MATCH`;
  - mọi điều kiện UNKNOWN, hoặc không có điều kiện nào → `INSUFFICIENT_EVIDENCE`;
  - các trường hợp còn lại → `PARTIAL_MATCH`.
- Cần người soát khi kết luận khác `MATCH`, **hoặc** khi có quy tắc nào không phải `machine_executable: full`.
- Ví dụ với quy tắc QĐ 21: "xác định được dự án" đạt, "có dữ liệu môi trường" đạt, "có văn bản xác nhận" là điều kiện manual nên UNKNOWN. Kết quả là `PARTIAL_MATCH` kèm cờ cần người soát, **không bao giờ là "vi phạm"**.

**2.3 Hai cổng** (`gates.py`)
- Văn bản dùng được: `LEGAL_SOURCE_READY = official_source ∧ full_text_available ∧ … ∧ amendment_chain_resolved ∧ provenance_complete`.
- Quy tắc được bật: `LEGAL_RULE_ACTIVE = source_clause_bound ∧ human_reviewed ∧ unit_tests_pass ∧ temporal_scope_defined`.
- Lưu ý [CHƯA XÁC MINH]: `checker.check()` không tự gọi cổng; cổng chạy trong `audit_rules`. Vì vậy trạng thái "chưa qua cổng" hiện được giữ bằng ghi chú trong quy tắc và bằng quy trình, chưa phải bằng một lệnh chặn lúc chạy.

**2.4 Hai chế độ thời gian**
- `historical_compliance`: xét theo luật có hiệu lực **lúc doanh nghiệp công bố**.
- `current_policy_alignment`: xét theo luật **hôm nay**. Đây là mặc định, vì mục đích là sàng lọc.
- Hàm `in_force_on(as_of)` dựa trên `effective_from` và `effective_to`.
- Ví dụ:
  - BCTN 2025 ghi "đạt QCVN 19:2009" **không sai**, vì cơ sở đang hoạt động được dùng quy chuẩn cũ đến 31/12/2031.
  - Tuyên bố về một khoản vay xanh cấp năm 2023 phải chấm theo luật lúc đó, vì trước QĐ 21/2025 Việt Nam chưa có taxonomy quốc gia.

**2.5 Chuỗi sửa đổi và xung đột văn bản**
- Văn bản gốc mang trạng thái `effective_with_amendments`.
- Các nguyên tắc chọn văn bản (luật sau, luật chuyên ngành, văn bản cấp cao hơn) là **phán đoán của luật sư**. Hệ thống **không tự chọn** (Q82 trong `TXT/GreenScan_100_Cau_BGK.txt`). Việc tự động duy nhất là loại văn bản đã hết hiệu lực theo registry.
- Ví dụ: Luật BVMT Đ.91.7(a) ghi cơ sở gửi kết quả kiểm kê lên Bộ trước 01/12; NĐ 119 Đ.11.4(b) ghi gửi UBND tỉnh trước 31/3. Hệ thống ghi chú điểm không khớp này và dẫn chiếu nghị định.

**2.6 Chủ thể nghĩa vụ và ranh giới tổ chức**
- Cơ sở (nhà máy, địa điểm) khác công ty niêm yết, và khác tập đoàn.
- Nghĩa vụ kiểm kê KNK đặt ở **cơ sở**. BCTN lập ở cấp công ty hoặc tập đoàn. Phải ánh xạ giữa hai cấp trước khi nói một doanh nghiệp "thuộc diện".
- GHG Protocol cho ba cách xác định ranh giới: kiểm soát vận hành, kiểm soát tài chính, tỷ lệ vốn góp [KIẾN THỨC NỀN]. Điều này gắn với bất biến 4: chỉ so cái thật sự so được.

**2.7 Bộ chỉ tiêu kỳ vọng khác nghĩa vụ đo lường**
- TT 96 Phụ lục IV mục 6 nói **phải có gì**, không nói **đo thế nào**. Vì vậy thiếu Scope hay thiếu năm gốc là "chưa đủ bằng chứng về phạm vi", không phải "sai".
- Dự thảo thay TT 96 đưa vào nguyên tắc "công bố hoặc giải trình" (*comply or explain*).

**2.8 Nghĩa vụ chứng minh (substantiation)**
- FTC: cần *reasonable basis*, thường là *competent and reliable scientific evidence*.
- CMA: tuyên bố *must be substantiated*.
- ECGT Đ.6(2)(d): tuyên bố về tương lai cần kế hoạch chi tiết, mục tiêu đo được và có kiểm định độc lập định kỳ.
- Việt Nam: Luật Quảng cáo Đ.8.10–8.11 đòi "tài liệu hợp pháp chứng minh"; Luật BVMT Đ.145 đòi chứng nhận hoặc công nhận.
- GreenScan đặt gánh nặng bằng chứng lên **chính tuyên bố**. Vì vậy "chưa đủ bằng chứng" khác "sai" (bất biến 6).

**2.9 Phạm vi: người tiêu dùng hay nhà đầu tư**
- Luật bảo vệ người tiêu dùng, luật quảng cáo và ECGT điều chỉnh truyền thông tới người tiêu dùng.
- BCTN bắt buộc gửi nhà đầu tư thường nằm ngoài phạm vi các luật đó (ECGT Q&A câu Q1; Luật 75/2025 Đ.19.3(b)), trừ khi nội dung được dùng lại trong truyền thông.
- Khung phù hợp cho thị trường vốn là định nghĩa của ESAs.

**2.10 Định nghĩa greenwashing**
- ESAs (04/06/2024): tuyên bố "do not clearly and fairly reflect the underlying sustainability profile", có thể xảy ra "intentionally or unintentionally".
- Seele & Gatti (2017): greenwashing là **một cáo buộc** từ bên ngoài.
- Vì vậy GreenScan không gán nhãn "tẩy xanh". Hệ thống chỉ đưa tín hiệu rủi ro gây hiểu nhầm và mức đủ bằng chứng của từng tuyên bố.

**2.11 Năm loại "kiểm" mà người làm tài chính – kế toán phải phân biệt**

| Loại | Chuẩn hoặc căn cứ | Ai làm | Mức đảm bảo / kết quả |
|---|---|---|---|
| Kiểm toán BCTC | VSA (TT 214/2012/TT-BTC) / ISA [KIẾN THỨC NỀN] | Kiểm toán viên hành nghề | Hợp lý; ý kiến dạng khẳng định |
| Đảm bảo thông tin phi tài chính | VSAE/ISAE 3000; ISAE 3410 cho KNK; **ISSA 5000** cho kỳ bắt đầu từ 15/12/2026 | Người hành nghề đảm bảo | **Hạn chế** ("không thấy điều gì khiến chúng tôi cho rằng…") hoặc **hợp lý** [KIẾN THỨC NỀN] |
| Thẩm định kiểm kê KNK | NĐ 06 sửa bởi 119, Đ.11.6a và Đ.14: tổ chức được chứng nhận theo pháp luật đánh giá sự phù hợp (thường theo ISO 14064-3 / ISO 14065 [KIẾN THỨC NỀN]) | Đơn vị thẩm định | Báo cáo đã thẩm định; bắt buộc cho điện, thép, xi măng từ chu kỳ nộp năm 2027 |
| Xác nhận dự án xanh | QĐ 21/2025, QĐ 46/2026 | Cơ quan thẩm định hoặc tổ chức đạt ISO/IEC 17029 / VSAE-ISAE 3000 | Văn bản xác nhận; tổ chức xác nhận chịu trách nhiệm trước pháp luật |
| Chứng nhận sản phẩm | NĐ 08 Đ.145–150: Nhãn sinh thái Việt Nam | Cơ quan có thẩm quyền | Hiệu lực 36 tháng; Bộ công bố danh mục |
| **GreenScan** | Không thuộc loại nào ở trên | Công cụ cho người soát | Sàng lọc trước và sau khi có đảm bảo. Có thể giúp kiểm toán viên ở bước đánh giá rủi ro và khi đọc "thông tin khác" trong BCTN (VSA/ISA 720 [KIẾN THỨC NỀN]; TT 96 Đ.10.2 yêu cầu thông tin tài chính trong BCTN phù hợp BCTC đã kiểm toán) |

**2.12 Ba cách hiểu trọng yếu (materiality)**
- Trọng yếu tài chính (ISSB): thông tin ảnh hưởng tới triển vọng của doanh nghiệp; người dùng chính là nhà đầu tư.
- Trọng yếu tác động (GRI): tác động của doanh nghiệp lên môi trường và con người.
- Trọng yếu kép (ESRS) [KIẾN THỨC NỀN].
- GreenScan **chưa chấm trọng yếu**. Kết luận, mức rủi ro và thứ tự ưu tiên là ba thứ tách nhau (bất biến 9). Trọng yếu theo ngành là một trục riêng, dự kiến làm sau.

**2.13 Bốn trụ cột ISSB/TCFD và GHG Protocol**
- Bốn trụ cột: Quản trị, Chiến lược, Quản lý rủi ro, Chỉ số và mục tiêu. Tuyên bố GreenScan kiểm phần lớn thuộc "Chỉ số và mục tiêu"; một phần thuộc "Chiến lược" (kế hoạch chuyển đổi).
- GHG Protocol: Scope 1, 2 (theo vị trí hoặc theo thị trường), 3 (15 hạng mục). Năm gốc phải tính lại khi cấu trúc doanh nghiệp đổi vượt ngưỡng trọng yếu, ngưỡng thường dùng là 5% [KIẾN THỨC NỀN] (`docs/00-project/CORE_FEATURE_TEST_REPORT_2026-09-20.md`).

**2.14 Vì sao F5 = 0 quy tắc áp được** (đã kiểm trong mã và cấu hình ngày 04/11)
1. Gói luật chỉ có **một** quy tắc. Quy tắc đó thuộc QĐ 21, `legal_issue: green_taxonomy`.
2. Hàm `for_claim` chỉ chọn quy tắc khi `claim_type` của tuyên bố nằm trong danh sách của quy tắc. Quy tắc này chỉ nhận `green_project` và `green_taxonomy_eligibility`. Bộ trích xuất chỉ sinh **8 loại**: `emissions_reduction`, `renewable_energy`, `resource_efficiency`, `waste_and_circularity`, `green_finance`, `biodiversity`, `esg_process_integration`, `generic_sustainability`. Vì vậy mọi tuyên bố đều rơi vào nhánh "rule pack chưa có rule nào cho claim_type…", ra `INSUFFICIENT_EVIDENCE` với `rules_applied: []`. Chú thích trong `checker.py` ghi rằng bảng ánh xạ cũ từng viết theo một bộ từ vựng mà bộ trích xuất không bao giờ sinh ra.
3. Không có quy tắc nào cho các vấn đề `emissions` (loại `emissions_reduction` được ánh xạ sang vấn đề này), `environmental_protection`, `disclosure` hay `green_credit`.
4. Kể cả khi loại tuyên bố khớp, quy tắc vẫn là bản nháp chưa bind điều khoản và chưa có người ký. Ghi chú trong quy tắc cấm trình kết quả của nó như phát hiện pháp lý.
5. **Gốc rễ:**
   - Thiết kế buộc quy tắc phải do người viết và người ký, mà chưa có người duyệt pháp lý ký.
   - Các điều quan trọng của Luật BVMT (từ Đ.90 trở đi) chưa có trong file điều khoản.
   - Nhiều nghĩa vụ chỉ quyết được khi có dữ kiện ngoài báo cáo (ánh xạ cơ sở với doanh nghiệp, danh sách Nhãn sinh thái, văn bản xác nhận, sổ đăng ký tín chỉ), hoặc khi chứng minh được corpus đầy đủ (lỗi mở B10).
   - TT 96 không quy định cách đo, nên có ít điều kiện máy quyết được.
6. **Cách hiểu đúng:**
   - Đây là **khoảng trống bao phủ của gói luật**, không phải phát hiện về doanh nghiệp, và không chặn phát hành (Q73).
   - Không có quy tắc vẫn tốt hơn áp sai quy tắc: ví dụ NĐ 83 từng bị trích sai cho 55 tuyên bố.
7. **Đường ra** (02 §7, A.6):
   - Sửa lại `claim_types` của quy tắc.
   - Viết ba quy tắc ưu tiên: QĐ 13 cộng lịch kiểm kê NĐ 119; TT 96 mục 6 với miễn trừ đúng; kỳ báo cáo kiểm kê và giảm nhẹ.
   - Thu sổ Nhãn sinh thái.
   - Mỗi quy tắc đi qua bước: Thảo duyệt → unit test → tăng phiên bản. Thời gian hoàn thành là [GIẢ THUYẾT].

**2.15 Ai chịu trách nhiệm khi máy gợi ý "vi phạm"**
- **Máy không gợi ý "vi phạm".**
  - `checker.py`: "It never says 'doanh nghiệp vi phạm'". Đầu ra pháp lý là bản ghi: văn bản nào, điều khoản nào, điều kiện nào đạt, không đạt hay chưa biết.
  - `NOT_MATCH` cho mức rủi ro HIGH và **bắt buộc người soát**.
  - Kết luận CONTRADICTED có nguồn pháp lý cũng bắt buộc người soát (`require_human_for_legal_conflict: true`, `configs/default.yaml` dòng 68).
  - Không có trường kết luận ở cấp doanh nghiệp (bất biến 1, có test quét mã nguồn).
- **Ma trận trách nhiệm:**

| Vai | Chịu trách nhiệm về | Căn cứ |
|---|---|---|
| Doanh nghiệp công bố | Nội dung thông tin công bố, kể cả phần sửa nhận từ GreenScan Studio | TT 96 Đ.4.2: "Đối tượng công bố thông tin phải chịu trách nhiệm trước pháp luật về nội dung thông tin công bố" (clause `TT96-2020-TT-BTC:article_4:paragraph_2`) |
| Tổ chức xác nhận hoặc đảm bảo | Kết quả xác nhận; kết luận đảm bảo | QĐ 21 Đ.4.2(c); ISAE 3000 [KIẾN THỨC NỀN] |
| Người dùng nghiệp vụ (cán bộ tín dụng, kiểm toán viên, nhà phân tích) | Quyết định của chính họ. GreenScan cung cấp hồ sơ tái dựng được: trích dẫn, phiên bản gói luật, ngày đối chiếu, manifest | TT 17 (nghĩa vụ quản lý rủi ro của ngân hàng); Q70 trong `TXT/GreenScan_100_Cau_BGK.txt` |
| Cơ quan có thẩm quyền, tòa án | **Kết luận vi phạm và xử phạt** (UBCKNN với công bố thông tin; cơ quan môi trường và thanh tra; cơ quan cạnh tranh và bảo vệ người tiêu dùng) | `TXT/ho_so_nguyen_ly_hoi_dong.txt` trang 2 ("kết luận pháp lý thuộc về con người có thẩm quyền") |
| Người soạn và người duyệt quy tắc (Thảo, chuyên gia ngoài) | Quy tắc trỏ đúng điều khoản, đúng ngày hiệu lực | Trường `reviewed_by`; cổng `human_reviewed` |
| Đội phát triển, nhà cung cấp công cụ | Chất lượng phần mềm, nhật ký, không quảng bá như tư vấn pháp lý, bảo vệ dữ liệu; nghĩa vụ minh bạch và gắn nhãn AI | Luật 91/2025; Luật AI 134/2025 và NĐ 142/2026 (mức áp dụng [CHƯA XÁC MINH]) |

- **Rủi ro cần nói trước:** nếu **công bố công khai** điểm "rủi ro tẩy xanh" của một doanh nghiệp niêm yết, có thể ảnh hưởng giá cổ phiếu và uy tín; luật chứng khoán cấm công bố thông tin sai lệch [KIẾN THỨC NỀN, CHƯA XÁC MINH số điều]. Vì vậy GreenScan định vị là **công cụ nội bộ cho người soát**, không phát hành xếp hạng công khai. Nếu làm dịch vụ xếp hạng ESG ở EU thì thuộc phạm vi Quy định (EU) 2024/3005 [KIẾN THỨC NỀN, CHƯA XÁC MINH].

---

## 3. Số liệu và dữ kiện được phép nói

*Nhãn: [ĐÃ THỰC NGHIỆM] là số đo của đội; [NGOÀI] là trích theo nguồn (VERIFIED: đã đọc văn bản gốc hoặc cổng chính thức; SECONDARY: nguồn thứ cấp); [KIẾN THỨC NỀN] là thiết kế đã cài hoặc kiến thức chung chưa đo; [GIẢ THUYẾT] là dự đoán.*

**Hệ thống GreenScan**
- 0 quy tắc áp được trên 156/156 tuyên bố HPG (lượt chạy 22/10) · `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` mục 2, F5 · [ĐÃ THỰC NGHIỆM]
- Trên HPG có 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT trên 156 tuyên bố · cùng file, F1 · [ĐÃ THỰC NGHIỆM]
- Toàn bộ 780/780 bằng chứng trên HPG là tài liệu của chính doanh nghiệp; `has_independent: False` · `TXT/ho_so_nguyen_ly_hoi_dong.txt` trang 5; KE_HOACH F6 · [ĐÃ THỰC NGHIỆM]
- 127/156 tuyên bố HPG không có con số nào · `TXT/ho_so_nguyen_ly_hoi_dong.txt` trang 2 · [ĐÃ THỰC NGHIỆM]
- Chưa có nhãn người: 0/88 cặp, 0/79 câu (kiểm 31/10) · KE_HOACH F7 · [ĐÃ THỰC NGHIỆM]
- Registry có **11** văn bản, độ tin cậy OCR trung bình 88,08–95,9 · `configs/legal/LEGAL_SOURCE_REGISTRY.yaml` · [ĐÃ THỰC NGHIỆM]
- 11 file điều khoản, tổng 4.189 dòng: Luật BVMT 938 dòng (89 Điều, 473 điểm, chỉ Đ.1–89), TT 96 có 327 dòng, QĐ 21 có 137 dòng · `data/legal/clauses/`, đếm 04/11 · [ĐÃ THỰC NGHIỆM]
- **Số điều khoản đã bind vào quy tắc: 0** · `configs/legal/rule_pack_vn_green_v0.1.yaml` · [ĐÃ THỰC NGHIỆM]
- Gói `vn-green-v0.1-draft` có 1 quy tắc, `machine_executable: partial`, `reviewed_by` trống · cùng file · [KIẾN THỨC NỀN]
- NĐ 83/2026 bị trích kèm 55 tuyên bố phát thải trước khi sửa, 0 sau khi sửa · `docs/07-presentation/nghien-cuu/P07_phap_ly.md` §2 (nguồn: `benchmark/queue_quality_2026-10-06.md`) · [ĐÃ THỰC NGHIỆM]
- Trong toàn văn NĐ 83/2026: "chất được kiểm soát" 66 lần, "kiểm kê khí nhà kính" 0 lần · chú thích trong registry · [ĐÃ THỰC NGHIỆM]
- Đã tải đủ 24 văn bản ứng viên: 11 bản có lớp chữ, 13 bản scan đã OCR tiếng Việt (độ tin cậy mỗi trang phần lớn 91–96) · `docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md` §3 · [ĐÃ THỰC NGHIỆM]
- Hai cổng `LEGAL_SOURCE_READY` / `LEGAL_RULE_ACTIVE`; hai chế độ thời gian; `require_human_for_legal_conflict: true` · `src/quantum_gw/legal/gates.py`, `checker.py`; `configs/default.yaml:68` · [KIẾN THỨC NỀN]
- Khóa FPT trả lỗi 401 từ 31/10; người dùng quyết định không dùng khóa trả phí; demo chạy `offline`; Groq và Cerebras chỉ dùng cho báo cáo công khai · KE_HOACH mục 10, mục 31/10 · [ĐÃ THỰC NGHIỆM] (sự kiện) / [KIẾN THỨC NỀN] (chính sách)

**Pháp lý Việt Nam**
- Luật BVMT 72/2020: ký 17/11/2020, hiệu lực 01/01/2022; sửa bởi Luật 11/2022, 16/2023, 18/2023, 47/2024, 54/2024 và 146/2025 (hiệu lực 01/01/2026); Luật 146 **không sửa** Đ.145, 149, 150 · `sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md` A.2.1 · [NGOÀI · VERIFIED]
- Luật BVMT Đ.145: sản phẩm, dịch vụ thân thiện môi trường phải "được cơ quan có thẩm quyền chứng nhận hoặc công nhận". Đ.6.9 có điều kiện "dẫn đến hậu quả xấu". Đ.150.3: tổ chức phát hành trái phiếu xanh cung cấp thông tin ĐTM, giấy phép môi trường, việc sử dụng vốn · A.2.1 · [NGOÀI · VERIFIED]
- NĐ 06/2022 Đ.6.1: phải kiểm kê nếu phát thải ≥ 3.000 tCO2tđ/năm, hoặc tiêu thụ ≥ 1.000 TOE/năm (nhiệt điện, công nghiệp, vận tải, tòa nhà thương mại), hoặc xử lý ≥ 65.000 tấn chất thải rắn/năm · A.2.5 · [NGOÀI · VERIFIED]
- NĐ 119/2025 (hiệu lực 01/08/2025):
  - cơ sở trong danh mục kiểm kê 2 năm/lần cho năm 2024 trở đi, nộp UBND tỉnh trước 31/3 từ năm 2025;
  - nhiệt điện, thép, xi măng: 2 năm/lần cho năm 2026 trở đi, **thẩm định độc lập**, nộp Bộ NN&MT trước 01/12 từ năm 2027 (báo cáo nộp năm 2027 chứa số liệu 2025–2026);
  - báo cáo giảm nhẹ phát thải hằng năm, nộp trước 31/3 từ năm 2027;
  - · A.4(e) · [NGOÀI · VERIFIED]
- NĐ 119/2025 Đ.19: tín chỉ phải cho kết quả giảm từ 01/01/2021; vay mượn hạn ngạch ≤ 15%; bù trừ bằng tín chỉ ≤ 30% hạn ngạch; tín chỉ đã dùng cho giảm phát thải tự nguyện không được giao dịch tiếp · A.2.6 · [NGOÀI · VERIFIED]
- QĐ 13/2024: có hiệu lực 01/10/2024, thay QĐ 01/2022 · A.2.8 · [NGOÀI · VERIFIED]. Danh mục 2.166 cơ sở: 1.805 thuộc Công Thương, 75 GTVT, 229 Xây dựng, 57 TN&MT · cùng mục · [NGOÀI · SECONDARY]
- QĐ 21/2025: ký 04/07/2025, hiệu lực 22/08/2025. Xác nhận bởi tổ chức đạt TCVN ISO/IEC 17029:2020 / ISO/IEC 17029:2019 hoặc theo VSAE/ISAE 3000 (Đ.4.2.d). "Tổ chức xác nhận độc lập chịu trách nhiệm trước pháp luật…" về kết quả (Đ.4.2.c). Bộ công bố danh mục dự án trên cổng (Đ.8–9) · A.2.9; `data/legal/clauses/QD21-2025-QD-TTg.jsonl` · [NGOÀI · VERIFIED]
- QĐ 21/2025 áp cho dự án muốn hưởng ưu đãi, hỗ trợ của Nhà nước về tín dụng xanh và trái phiếu xanh · `TXT/AI-QUANTUM_AGENT_CRITERIA_v1.txt` dòng 5; điều khoản Đ.4.2.c · [NGOÀI]
- NĐ 48/2026 Đ.31: thẩm quyền ban hành danh mục phân loại xanh chuyển cho Bộ trưởng NN&MT · A.2.4, A.4(d) · [NGOÀI · VERIFIED]
- QĐ 46/2026: ký 17/09/2026, **hiệu lực 01/11/2026**; tỉnh công bố danh mục dự án xanh, tuần hoàn mỗi 30/6 và 31/12 · v4 §1 · [NGOÀI · VERIFIED]
- TT 96/2020:
  - Đ.10.2: BCTN công bố trong 20 ngày sau khi công bố BCTC năm đã kiểm toán, không quá 110 ngày sau khi kết thúc năm tài chính;
  - Phụ lục IV mục 6: 6.1 KNK trực tiếp và gián tiếp, 6.2 vật liệu, 6.3 năng lượng, 6.4 nước, 6.5 số lần và số tiền bị phạt về môi trường, 6.8 thị trường vốn xanh;
  - 6.1–6.3 không bắt buộc với doanh nghiệp tài chính, ngân hàng, chứng khoán, bảo hiểm;
  - · A.2.11 · [NGOÀI · VERIFIED]
- TT 68/2024: tổ chức niêm yết và công ty đại chúng quy mô lớn công bố thông tin định kỳ bằng tiếng Anh từ 01/01/2025, bản tiếng Anh phải thống nhất với bản tiếng Việt · A.4(f) · [NGOÀI · VERIFIED ngày / SECONDARY nội dung]
- Dự thảo thay TT 96 (10 chương, 47 điều, 22 phụ lục; phụ lục ESG; "công bố hoặc giải trình"; hạn BCTN 120 ngày) **vẫn là dự thảo** đến 22/10/2026 · A.4(f); lsvn.vn 22/10/2026 · [NGOÀI · SECONDARY]
- TT 17/2022: ký 23/12/2022, hiệu lực 01/06/2023; không có nghĩa vụ công bố công khai danh mục dự án; không định nghĩa tín dụng xanh (định nghĩa nằm ở Luật BVMT Đ.149) · A.2.10 · [NGOÀI · VERIFIED]
- Luật 19/2023 có hiệu lực 01/07/2024 (Đ.10.1(a)); Luật 75/2025 có hiệu lực 01/01/2026 (Đ.19, Đ.8.10, Đ.19.3(b)) · A.3.1–A.3.2; v4 §1 · [NGOÀI · VERIFIED]
- NĐ 87/2026 (hiệu lực 15/05/2026, thay NĐ 38/2021): Đ.50.5(c) quảng cáo gây nhầm lẫn phạt 80–100 triệu; Đ.50.4(b) so sánh 40–60 triệu; Đ.50.2(a) "nhất, số một" 10–20 triệu. Mức này áp cho cá nhân hay tổ chức: **chờ Thảo** · v4 §1 · [NGOÀI · VERIFIED]
- NĐ 98/2020 sửa bởi NĐ 24/2025, Đ.47.2(a): cá nhân 20–30 triệu, tổ chức 40–60 triệu · v4 §1 · [NGOÀI · VERIFIED] (mâu thuẫn ngày hiệu lực của NĐ 24/2025, xem mục 5)
- Nhãn sinh thái: CV 10612/BNNMT-MT (22/12/2025) liệt kê 21 giấy chứng nhận giai đoạn 2024–2025, **toàn bộ là bao bì**, hiệu lực 3 năm · v4 §1 · [NGOÀI · VERIFIED]
- QCVN 19:2024 (TT 45/2024) có hiệu lực 01/07/2025; cơ sở đang hoạt động được dùng quy chuẩn cũ đến 31/12/2031 · v4 §1 · [NGOÀI · VERIFIED]
- QĐ 263/QĐ-TTg: hạn ngạch thí điểm 2025 là 243.082.392 tCO2tđ, 2026 là 268.391.454 tCO2tđ, cho 34 nhà máy nhiệt điện, 25 cơ sở thép, 51 cơ sở xi măng; sàn các-bon khai trương 29/06/2026 · A.3.6 · [NGOÀI · SECONDARY]
- TT 11/2026 (hiệu lực 30/03/2026): tín chỉ dùng để bù trừ được chuyển sang tiểu khoản bù trừ và bị hủy; sổ đăng ký công khai định kỳ · v4 §1 · [NGOÀI · VERIFIED]
- Không thấy chữ "tẩy xanh" hay "greenwash" trong 14 văn bản đã rà toàn văn · A.3.9 · [NGOÀI · VERIFIED trong phạm vi 14 văn bản]. Nhận định ở phạm vi toàn hệ thống pháp luật: [CHƯA XÁC MINH]
- Chưa tìm thấy vụ nào ở Việt Nam bị xử phạt vì green claim · D.1 · [CHƯA XÁC MINH, bằng chứng phủ định có giới hạn]
- Luật BVDLCN 91/2025/QH15 (thông qua 26/06/2025, hiệu lực 01/01/2026):
  - Đ.20.1(c): dùng nền tảng ở nước ngoài để xử lý dữ liệu cá nhân thu tại Việt Nam là chuyển dữ liệu xuyên biên giới;
  - phải lập hồ sơ đánh giá tác động trong 60 ngày;
  - Đ.30: xử lý dữ liệu cá nhân bằng AI phải phân loại theo mức rủi ro;
  - phạt tới 5% doanh thu năm liền trước với vi phạm chuyển xuyên biên giới;
  - ưu đãi 5 năm cho doanh nghiệp nhỏ và khởi nghiệp **không** miễn Đ.20;
  - · `docs/08-knowledge/sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md` §6.1–6.2 · [NGOÀI · VERIFIED]
- NĐ 356/2025 có hiệu lực 01/01/2026 và **bãi bỏ NĐ 13/2023** (Đ.42.2); Đ.12: dữ liệu cá nhân trên đám mây phải mã hóa khi lưu và khi truyền · cùng nguồn · [NGOÀI · VERIFIED]
- Tên lãnh đạo trong báo cáo đã công bố có thể thuộc diện miễn đánh giá theo NĐ 356 Đ.17.3 · cùng nguồn · [GIẢ THUYẾT – chờ Thảo]
- Luật Kiểm toán độc lập 67/2011 Đ.43: không được tiết lộ hồ sơ kiểm toán khi chưa có chấp thuận của khách hàng · cùng nguồn · [NGOÀI · VERIFIED]
- NĐ 142/2026: ký 30/04/2026, hiệu lực 01/05/2026 · v4 §2.6 · [NGOÀI · VERIFIED]. Luật AI 134/2025 có hiệu lực 01/03/2026 · [NGOÀI · SECONDARY]
- Thực trạng thị trường: tỷ lệ báo cáo phát triển bền vững trên HOSE 28,38%; báo cáo định tính 72,5%; đảm bảo bên thứ ba 2/22; KNK 50,6% điểm 0; tuân thủ phần môi trường 40,75%; GRI 19–25% · `docs/08-knowledge/03_THUC_TRANG_VA_NGHIEN_CUU_VN.md` §1 · [NGOÀI · VERIFIED]
- Tín dụng xanh khoảng 750.000 tỷ đồng (30/11/2025), khoảng 5% tổng dư nợ · 03 §1 · [NGOÀI · SECONDARY]
- Tiêu chí chấm của cuộc thi có mục "tuân thủ bảo mật dữ liệu, an toàn thông tin và quy định pháp lý liên quan; rủi ro đạo đức, thiên vị; cơ chế minh bạch, AI có trách nhiệm"; thang 90–100 ứng với "toàn diện, có lộ trình rõ" · `TXT/the_le_cuoc_thi.txt` trang 11 · [NGOÀI] (trọng số của tiêu chí: OCR lỗi, [CHƯA XÁC MINH])

**Quốc tế và chuẩn mực**
- ISSA 5000 áp cho kỳ bắt đầu từ 15/12/2026. Sau mốc đó ISAE 3000 (Revised) không còn áp cho đảm bảo bền vững, và ISAE 3410 bị rút cùng mốc · IAASB FAQ (URL ở đầu file) · [NGOÀI · qua kết quả tìm kiếm]
- ISAE 3000 (Revised) có hai mức đảm bảo: hạn chế (kết luận dạng phủ định) và hợp lý (kết luận dạng khẳng định) · [KIẾN THỨC NỀN]
- IFRS S1/S2 ban hành 26/06/2023, áp cho kỳ từ 01/01/2024 tùy từng pháp quyền thông qua; IFRS S2 yêu cầu Scope 1, 2, 3 theo GHG Protocol, có miễn trừ Scope 3 năm đầu · [KIẾN THỨC NỀN]
- Sửa đổi IFRS S2 về phát thải KNK ban hành 11/12/2025, áp cho kỳ từ 01/01/2027; cho phép giới hạn Scope 3 hạng mục 15 ở phát thải tài trợ · ifrs.org (URL ở đầu file) · [NGOÀI · qua kết quả tìm kiếm]
- Việt Nam không có trong danh sách hồ sơ pháp quyền ISSB của IFRS Foundation (đến 24/09/2026). Các nước ASEAN có hồ sơ: Singapore, Malaysia, Philippines, Indonesia, Thái Lan · A.5.5 · [NGOÀI · VERIFIED]
- Lộ trình ISSB chính thức của Việt Nam: chưa tìm thấy · A.3.8; kết quả tìm kiếm 04/11 · [CHƯA XÁC MINH]
- QĐ 345/QĐ-BTC (16/03/2020): đề án áp dụng IFRS cho BCTC, tự nguyện 2022–2025, bắt buộc sau 2025 theo quy định của Bộ Tài chính · luatvietnam · [NGOÀI · SECONDARY]; đối tượng và mốc cụ thể [CHƯA XÁC MINH]
- GRI 102 Climate Change 2025 và GRI 103 Energy 2025 công bố 6/2025, có hiệu lực 01/01/2027, thay GRI 305-1 đến 305-5 và GRI 302 · GRI FAQ, BDO · [NGOÀI · SECONDARY]
- Omnibus I, Chỉ thị (EU) 2026/470: đăng Công báo EU 26/02/2026, có hiệu lực 18/03/2026; CSRD còn áp cho doanh nghiệp trên 1.000 lao động · A.5.4 · [NGOÀI · VERIFIED]; ngưỡng doanh thu trên 450 triệu EUR · [NGOÀI · SECONDARY]
- ESRS rút gọn: EFRAG nộp tư vấn kỹ thuật 03/12/2025 (giảm 61% số datapoint bắt buộc); Commission thông qua delegated act 03/07/2026 · A.5.4 · [NGOÀI · VERIFIED]
- ECGT 2024/825: hạn chuyển hóa 27/03/2026, **áp dụng từ 27/09/2026**. Ngày 28/05/2026 Commission gửi thư khởi động thủ tục vi phạm tới 20 nước thành viên. Nhãn do cơ quan công quyền ngoài EU cấp không được coi là "public authority" · A.5.2 · [NGOÀI · VERIFIED]
- Green Claims Directive: Legislative Train ghi "Blocked" (cập nhật 20/09/2026) · A.5.3 · [NGOÀI · VERIFIED]
- CBAM áp dụng chính thức từ 01/01/2026; ngưỡng de minimis 50 tấn/năm · A.5.1 · [NGOÀI · VERIFIED]. Năm 2023 Việt Nam xuất trên 2,5 triệu tấn thép sang EU · [NGOÀI · SECONDARY]
- CMA Green Claims Code (20/09/2021), 6 nguyên tắc · E.1 · [NGOÀI · VERIFIED]. CMA được tự phạt tới 10% doanh thu toàn cầu theo DMCC Act · [CHƯA XÁC MINH]
- FTC Green Guides: quá trình rà soát bắt đầu 14/12/2022, chưa có bản sửa đổi được thông qua · E.1 · [NGOÀI · VERIFIED]
- ESAs Final Report (04/06/2024): định nghĩa greenwashing, có cụm "intentionally or unintentionally" · E.1 · [NGOÀI · VERIFIED]

---

## 4. Câu hỏi BGK dự kiến

*Mỗi câu trả lời 30–60 giây, theo khung **vấn đề → nguyên lý → GreenScan làm gì → giới hạn**.*

**Q1. "Việt Nam có luật cấm greenwashing không? Các em dựa vào đâu để nói một tuyên bố là sai?"**
- **Trả lời:**
  - *Vấn đề:* pháp luật chưa định nghĩa "tẩy xanh"; trong 14 văn bản chúng tôi đã rà toàn văn không có từ này.
  - *Nguyên lý:* căn cứ gần nhất là các nghĩa vụ cụ thể, ví dụ:
    - Luật BVMT Điều 145: sản phẩm thân thiện môi trường phải có chứng nhận;
    - Điều 150.3: trái phiếu xanh phải công bố việc sử dụng vốn;
    - TT 96 Phụ lục IV mục 6;
    - NĐ 06 Điều 19 về tín chỉ;
    - luật người tiêu dùng và luật quảng cáo, nhưng chỉ khi có truyền thông.
  - *GreenScan làm:* không nói "sai" hay "tẩy xanh". Hệ thống nói: điều kiện X của nghĩa vụ Y, điều khoản Z, hiệu lực từ ngày D, là đạt, không đạt hay chưa có bằng chứng; hoặc nói tuyên bố "chưa đủ bằng chứng".
  - *Giới hạn:* câu "không văn bản nào định nghĩa" chỉ đúng trong phạm vi 14 văn bản đã rà.
- **Câu vặn:** "Vậy GreenScan vô dụng ở Việt Nam?" → Không. Giá trị nằm ở hàng đợi, ở thuộc tính còn thiếu và ở mâu thuẫn số. Luật chỉ là một trục.
- **Bẫy:** nói "luật Việt Nam cấm tẩy xanh"; dẫn Luật BVMT Điều 6.9 như một lệnh cấm chung (điều này có điều kiện "dẫn đến hậu quả xấu").

**Q2. "Đề bài yêu cầu đối chiếu tiêu chí xanh pháp lý, mà gói luật của các em áp được 0/156. Lớp pháp lý có giá trị gì?" (F5)**
- **Trả lời:**
  - *Vấn đề:* đo trên lượt chạy 22/10, không quy tắc nào áp được cho 156 tuyên bố HPG.
  - *Nguyên lý:* "đóng khi thiếu". Một quy tắc chỉ được áp khi có điều khoản đã bind, có người ký, có test và có phạm vi thời gian.
  - *Nguyên nhân cụ thể:*
    - gói luật có một quy tắc nháp, cho QĐ 21;
    - loại tuyên bố mà quy tắc nhận không trùng với 8 loại bộ trích xuất sinh ra;
    - chưa có quy tắc nào cho phát thải, bảo vệ môi trường hay công bố thông tin.
  - *GreenScan vẫn làm:*
    - giữ registry 11 văn bản theo ngày hiệu lực và chuỗi sửa đổi;
    - loại văn bản không áp được và ghi lý do. Ví dụ NĐ 83/2026 chỉ về ô-dôn từng bị gắn vào 55 tuyên bố phát thải; sau khi sửa còn 0.
  - *Giới hạn:* hôm nay cột pháp lý là báo cáo độ phủ của gói luật, không phải phát hiện về doanh nghiệp.
- **Câu vặn:** "Bao giờ có quy tắc thật?" → Ba quy tắc ưu tiên đã đặc tả: QĐ 13 cộng lịch kiểm kê NĐ 119; TT 96 mục 6 với miễn trừ; kỳ kiểm kê và giảm nhẹ. Nút thắt là người duyệt pháp lý, không phải code. Không hứa ngày.
- **Bẫy:** nói "có 4.189 điều khoản" như thể là quy tắc; nói "hệ thống đã đối chiếu taxonomy".

**Q3. "Nếu máy gợi ý một doanh nghiệp vi phạm, mà gợi ý đó sai, thì ai chịu trách nhiệm?"**
- **Trả lời:**
  - *Vấn đề:* quy kết sai là rủi ro pháp lý và uy tín lớn nhất của bài toán này.
  - *Nguyên lý:* Models read – Rules decide – Humans review. Máy không có quyền kết luận vi phạm.
  - *GreenScan làm:*
    1. Không có trường kết luận cấp doanh nghiệp (bất biến 1, có test canh).
    2. Đầu ra pháp lý chỉ là bản ghi điều kiện. Kết quả "không đạt", hoặc mâu thuẫn có nguồn pháp lý, bắt buộc người soát.
    3. Có manifest, trích dẫn và phiên bản gói luật để tái dựng lại kết quả.
  - *Trách nhiệm theo vai:*
    - doanh nghiệp chịu trách nhiệm về nội dung công bố (TT 96 Điều 4.2);
    - tổ chức xác nhận chịu trách nhiệm về kết quả xác nhận (QĐ 21 Điều 4.2.c);
    - người dùng nghiệp vụ chịu trách nhiệm về quyết định của họ;
    - kết luận vi phạm thuộc cơ quan có thẩm quyền hoặc tòa án;
    - đội phát triển chịu trách nhiệm về chất lượng quy tắc và không quảng bá công cụ như tư vấn pháp lý.
  - *Giới hạn:* chưa có ý kiến luật sư về trách nhiệm sản phẩm.
- **Câu vặn:** "Ngân hàng dùng kết quả để từ chối cho vay, doanh nghiệp kiện thì sao?" → Ngân hàng quyết định và chịu trách nhiệm theo TT 17. GreenScan cung cấp hồ sơ tái dựng được để họ bảo vệ hoặc sửa quyết định.
- **Bẫy:** nói "AI chịu trách nhiệm", "không ai chịu", hoặc "GreenScan bảo đảm chính xác".

**Q4. "TT 96 yêu cầu gì về môi trường? Doanh nghiệp không công bố KNK có vi phạm công bố thông tin không?"**
- **Trả lời:**
  - *Vấn đề và quy định:*
    - BCTN lập theo Phụ lục IV, công bố trong 20 ngày sau BCTC đã kiểm toán và không quá 110 ngày sau khi kết thúc năm tài chính;
    - mục 6 gồm: KNK trực tiếp và gián tiếp, vật liệu, năng lượng, nước, số lần và số tiền bị phạt về môi trường, thị trường vốn xanh;
    - mục 6 có thể tách thành báo cáo phát triển bền vững riêng.
  - *Nguyên lý:* TT 96 là bộ chỉ tiêu kỳ vọng. Nó không quy định Scope, ranh giới, năm gốc hay việc đảm bảo.
  - *GreenScan làm:*
    - dùng mục 6 để định hướng tìm bằng chứng và phát hiện công bố chọn lọc;
    - thiếu Scope hay năm gốc thì ghi "chưa đủ bằng chứng về phạm vi";
    - không kết luận "vi phạm công bố", vì không tìm thấy trong tài liệu chúng tôi có chưa phải là không công bố (có thể nằm trong báo cáo phát triển bền vững rời).
  - *Giới hạn:* chưa thành quy tắc; chưa có kiểm tra độ đầy đủ của corpus.
- **Câu vặn:** "Vậy bị phạt bao nhiêu?" → Chúng tôi chưa đọc bản gốc nghị định xử phạt trong lĩnh vực chứng khoán, nên không nêu mức phạt.
- **Bẫy:** quên miễn trừ 6.1–6.3 cho bốn ngành tài chính; nói TT 96 đã bị thay (thông tư thay thế vẫn là dự thảo).

**Q5. "Ngân hàng không công bố phát thải, sao các em không gắn cờ?"**
- **Trả lời:**
  - *Quy định:* ghi chú Phụ lục IV TT 96 nói 6.1–6.3 không bắt buộc với doanh nghiệp tài chính, ngân hàng, chứng khoán, bảo hiểm. Mục 6.4 (nước) và 6.5 (tuân thủ) vẫn áp.
  - *GreenScan làm với ngân hàng:* kiểm nhất quán số dư tín dụng xanh giữa các năm và giữa BCTN với báo cáo phát triển bền vững; đối chiếu hạng mục với QĐ 21.
  - *Bối cảnh:* TT 17 là nghĩa vụ quản lý rủi ro môi trường của chính ngân hàng, vì vậy ngân hàng là người dùng đầu tiên.
  - *Giới hạn:* quy tắc miễn trừ chưa viết; nghiên cứu ghi nhận dữ liệu tín dụng xanh "không nhất quán qua các năm".
- **Câu vặn:** "TT 17 có định nghĩa tín dụng xanh không?" → Không. Định nghĩa nằm ở Luật BVMT Điều 149.
- **Bẫy:** nói ngân hàng được miễn toàn bộ mục 6; nói TT 17 buộc ngân hàng công khai danh mục dự án.

**Q6. "GreenScan kiểm 'dự án xanh' theo QĐ 21 thế nào? QĐ 46/2026 vừa có hiệu lực thì sao?"**
- **Trả lời:**
  - *Quy định QĐ 21 (hiệu lực 22/08/2025):*
    - tiêu chí: có ĐTM, giấy phép hoặc đăng ký môi trường, **và** thuộc Phụ lục I;
    - xác nhận bởi cơ quan thẩm định hoặc tổ chức độc lập đạt ISO/IEC 17029 hoặc VSAE/ISAE 3000;
    - tổ chức xác nhận chịu trách nhiệm trước pháp luật; Bộ công bố danh mục;
    - áp cho dự án muốn hưởng ưu đãi về tín dụng xanh và trái phiếu xanh.
  - *GreenScan làm:* quy tắc nháp có ba điều kiện. Điều kiện "có văn bản xác nhận" cố ý để người xét, vì tính hợp lệ của văn bản là phán đoán pháp lý.
  - *QĐ 46/2026 (hiệu lực 01/11/2026):* tạo chế độ thứ hai chạy song song, nên tuyên bố phải nói rõ theo bộ tiêu chí nào; tỉnh công bố danh mục mỗi 30/6 và 31/12.
  - *Giới hạn:* quy tắc chưa bind điều khoản; QĐ 46 chưa vào registry.
- **Câu vặn:** "Không thuộc taxonomy có nghĩa là tẩy xanh?" → Không. Taxonomy là điều kiện để hưởng cơ chế, không phải định nghĩa mọi hoạt động xanh.
- **Bẫy:** nói QĐ 21 bắt buộc mọi doanh nghiệp; quên NĐ 48 Điều 31 đã chuyển thẩm quyền ban hành danh mục cho Bộ trưởng NN&MT.

**Q7. "Doanh nghiệp thép viết 'số liệu KNK đã được thẩm định theo NĐ 06'. Các em kiểm thế nào?"**
- **Trả lời:**
  - *Quy định:* nghĩa vụ kiểm kê đặt ở cơ sở có tên trong QĐ 13. Theo NĐ 119 Điều 11.4:
    - cơ sở nói chung kiểm kê 2 năm/lần cho năm 2024 trở đi, nộp tỉnh trước 31/3 từ năm 2025;
    - nhiệt điện, thép, xi măng kiểm kê 2 năm/lần cho năm 2026 trở đi, do đơn vị độc lập thẩm định, nộp Bộ trước 01/12 từ năm 2027.
  - *GreenScan suy ra:* chu kỳ thẩm định bắt buộc chưa bắt đầu, nên một BCTN 2024–2025 viết như vậy cần bằng chứng riêng: ai thẩm định, theo chuẩn nào, phạm vi nào.
  - *Phải làm thêm:* ánh xạ cơ sở ↔ công ty con ↔ công ty niêm yết trước khi nói "thuộc diện".
  - *Giới hạn:* quy tắc lịch kiểm kê chưa viết; ánh xạ chưa làm.
- **Câu vặn:** "Kiểm kê hằng năm à?" → Không. Kiểm kê 2 năm/lần; báo cáo giảm nhẹ hằng năm từ 2027; báo cáo công tác BVMT hằng năm.
- **Bẫy:** coi NĐ 83/2026 là văn bản về KNK.

**Q8. "Tuyên bố 'trung hòa các-bon nhờ mua tín chỉ' có hợp pháp không?"**
- **Trả lời:**
  - *Việt Nam:* chưa cấm. NĐ 06 sửa bởi 119, Điều 19:
    - tín chỉ phải cho kết quả giảm từ 01/01/2021;
    - bù trừ không quá 30% hạn ngạch;
    - tín chỉ đã dùng cho giảm phát thải tự nguyện không được giao dịch tiếp.
    TT 11/2026 thêm: tín chỉ bù trừ bị chuyển sang tiểu khoản và hủy, có công khai.
  - *EU và Mỹ:* ECGT Phụ lục I điểm 4c cấm tuyên bố trung hòa **cấp sản phẩm** dựa trên bù trừ, từ 27/09/2026. FTC có §260.5 về bù trừ.
  - *GreenScan làm:* gắn cờ OVERCLAIM ("cờ, không phải kết luận"); đòi bằng chứng hủy hoặc khóa tín chỉ và nguồn gốc tín chỉ.
  - *Giới hạn:* dữ liệu sổ đăng ký chưa thu (ưu tiên P1).
- **Câu vặn:** "Tuyên bố trung hòa cấp công ty có bị cấm không?" → Theo Q&A câu Q10 thì điểm 4c không áp cho tuyên bố cấp công ty, nhưng tuyên bố đó vẫn chịu các điều khác của UCPD. ECGT là luật EU và điều chỉnh B2C.
- **Bẫy:** nói "luật Việt Nam cấm"; nói "ECGT áp cho BCTN".

**Q9. "GreenScan có thay được kiểm toán hay dịch vụ đảm bảo (ISAE 3000, ISSA 5000) không?"**
- **Trả lời:**
  - *Không.* Đảm bảo là một hợp đồng nghề nghiệp:
    - theo chuẩn: ISAE/VSAE 3000, ISAE 3410 cho KNK, ISSA 5000 cho kỳ bắt đầu từ 15/12/2026;
    - người hành nghề tuân thủ chuẩn đạo đức và quản lý chất lượng;
    - phát hành kết luận hạn chế hoặc hợp lý, và chịu trách nhiệm về kết luận đó.
  - *GreenScan là công cụ sàng lọc:*
    - trước khi có đảm bảo: doanh nghiệp tự kiểm, xếp hàng các tuyên bố cần mở;
    - sau khi có đảm bảo: đối chiếu tuyên bố ở trang 3 với bảng đã được đảm bảo ở trang 75.
  - *Có thể hỗ trợ kiểm toán viên:* ở bước đánh giá rủi ro, và khi đọc "thông tin khác" trong BCTN (VSA/ISA 720).
  - *Giới hạn:* chưa có nhãn người; toàn bộ 780 bằng chứng trên HPG là nguồn nội bộ.
- **Câu vặn:** "Vậy giá trị kinh tế ở đâu?" → Rút ngắn việc đọc vài trăm trang và đưa tuyên bố rủi ro lên trước. Mức thời gian tiết kiệm **chưa đo** [GIẢ THUYẾT].
- **Bẫy:** gọi đầu ra của GreenScan là "audit", "assurance" hay "xác nhận".

**Q10. "Báo cáo đã có Big 4 đảm bảo rồi, còn cần GreenScan làm gì?"**
- **Trả lời:**
  - *Vấn đề:* dịch vụ đảm bảo thường ở mức hạn chế, trên một số chỉ số chọn lọc. Nó xác nhận số liệu theo phương pháp, không xác nhận câu "dẫn đầu xanh" có phù hợp với bảng số hay không.
  - *Thực trạng:* năm 2024 ở Việt Nam chỉ 2/22 báo cáo độc lập có đảm bảo bên thứ ba (ACB, VNM).
  - *GreenScan làm:* ghi "có hay không đảm bảo, ai đảm bảo, phạm vi nào" thành thuộc tính của bằng chứng; báo cáo đảm bảo được coi là nguồn bên ngoài, làm tăng độ tin.
  - *Giới hạn:* trên HPG chưa có nguồn độc lập nào.
- **Câu vặn:** "Nếu là đảm bảo hợp lý thì sao?" → Vẫn chỉ trong phạm vi được đảm bảo. Tuyên bố ngoài phạm vi vẫn cần kiểm.
- **Bẫy:** trích "PwC: 10% doanh nghiệp có đảm bảo" (trang nguồn trả lỗi 403, chưa xác minh).

**Q11. "Lộ trình IFRS và ISSB ở Việt Nam thế nào? Khi ISSB bắt buộc, GreenScan có phải làm lại không?"**
- **Trả lời:**
  - *IFRS cho BCTC:* QĐ 345/QĐ-BTC (2020) đặt giai đoạn tự nguyện 2022–2025 và bắt buộc sau 2025 theo quy định của Bộ Tài chính. Chi tiết đối tượng và mốc cần đối chiếu thêm.
  - *ISSB cho báo cáo bền vững:*
    - chưa thấy lộ trình chính thức;
    - Việt Nam không có hồ sơ pháp quyền ở IFRS Foundation (đến 24/09/2026);
    - điểm neo gần nhất là dự thảo thay TT 96 (phụ lục ESG, "công bố hoặc giải trình"), vẫn là dự thảo đến 22/10/2026.
  - *GreenScan làm:*
    - thuộc tính tuyên bố (chỉ số, Scope, kỳ, năm gốc, ranh giới, đảm bảo) đã bám IFRS S2 và GHG Protocol;
    - khi có văn bản mới, chỉ cần thêm vào registry và viết quy tắc, không phải huấn luyện lại mô hình.
  - *Giới hạn:* chưa có quy tắc nào cho TT 96 hiện hành.
- **Câu vặn:** "IFRS S2 có đòi Scope 3 không?" → Có, kèm miễn trừ năm đầu. Bản sửa 12/2025, áp từ 2027, nới cách đo Scope 3 hạng mục 15 (phát thải tài trợ).
- **Bẫy:** nói "Việt Nam đã áp ISSB"; nói dự thảo đã ban hành; nhầm IFRS (BCTC) với ISSB (báo cáo bền vững).

**Q12. "GRI, ISSB, ESRS khác nhau ra sao? GreenScan theo khung nào?"**
- **Trả lời:**
  - *ISSB:* trọng yếu tài chính, người dùng chính là nhà đầu tư, 4 trụ cột, có chỉ số theo ngành.
  - *GRI:* trọng yếu tác động. Phần KNK của GRI 305 sẽ được thay bằng GRI 102 và GRI 103 từ 01/01/2027.
  - *ESRS:* trọng yếu kép. Omnibus đã thu hẹp CSRD còn doanh nghiệp trên 1.000 lao động; ESRS rút gọn giảm 61% số datapoint bắt buộc.
  - *GreenScan:* không chọn một khung. Hệ thống kiểm ở cấp tuyên bố, lấy khung pháp lý Việt Nam (TT 96) làm bộ kỳ vọng; các khung quốc tế dùng để định nghĩa chỉ số và làm typology.
  - *Giới hạn:* chưa có trục trọng yếu.
- **Câu vặn:** "Doanh nghiệp Việt Nam có phải theo ESRS không?" → Chỉ gián tiếp, qua khách hàng EU trong chuỗi giá trị.
- **Bẫy:** gọi GRI là luật; nói ESRS áp trực tiếp cho doanh nghiệp Việt Nam.

**Q13. "Luật Bảo vệ quyền lợi người tiêu dùng và Luật Quảng cáo có áp cho báo cáo thường niên không?"**
- **Trả lời:**
  - *Quy định:*
    - Luật 19/2023 Điều 10.1(a) cấm gây nhầm lẫn cho người tiêu dùng, kể cả về giấy chứng nhận;
    - Luật Quảng cáo sửa năm 2025: Điều 19 đòi nội dung trung thực; Điều 8.10 và 8.11 đòi chứng minh khi so sánh hoặc dùng chữ "nhất";
    - nhưng Điều 19.3(b) nói thông tin bắt buộc công bố không phải quảng cáo.
  - *Nguyên lý:* hai luật này chỉ áp khi nội dung BCTN được dùng lại trong truyền thông tới người tiêu dùng.
  - *GreenScan làm:* dùng làm tham chiếu ngữ cảnh, không dùng để kết luận.
  - *Mức phạt có thể nêu:* quảng cáo gây nhầm lẫn bị phạt 80–100 triệu theo NĐ 87/2026 Điều 50.5(c). Áp cho cá nhân hay tổ chức còn chờ xác nhận.
  - *Giới hạn:* hai luật này mới ở file ứng viên, chưa vào registry.
- **Câu vặn:** "EU có giống vậy không?" → Có. Q&A của ECGT (câu Q1) theo cùng logic.
- **Bẫy:** dẫn NĐ 38/2021, đã bị NĐ 87/2026 thay từ 15/05/2026.

**Q14. "Áp lực quốc tế (EU 2024/825, CBAM, CMA, FTC) liên quan gì tới doanh nghiệp Việt Nam?"**
- **Trả lời:**
  - *CBAM:* áp dụng chính thức từ 01/01/2026, gồm thép và xi măng. Năm 2023 Việt Nam xuất trên 2,5 triệu tấn thép sang EU [SECONDARY]. Vì vậy các tuyên bố "thép xanh", "tCO2/tấn" sẽ tăng và đối chiếu định lượng được.
  - *ECGT:* áp dụng từ 27/09/2026, kể cả với hàng từ nước thứ ba. Nhãn của cơ quan công quyền ngoài EU không được coi là "public authority".
  - *CMA và FTC:* là typology và checklist.
  - *GreenScan làm:* dùng các nguồn này làm checklist bằng chứng; không áp luật nước ngoài cho doanh nghiệp Việt Nam.
  - *Giới hạn:* phần quốc tế chưa được kiểm chứng sâu (tài liệu v4 ghi đang tạm dừng).
- **Câu vặn:** "Còn Green Claims Directive?" → Đang ở trạng thái "Blocked" (20/09/2026), chưa thành luật.
- **Bẫy:** nói GCD đã có hiệu lực; nêu mức phạt 10% của CMA (chưa xác minh).

**Q15. "Luật thay đổi liên tục, như QĐ 46 có hiệu lực ngày 01/11. Các em có phải huấn luyện lại mô hình không?"**
- **Trả lời:**
  - *Không.* Luật nằm trong registry và gói quy tắc, không nằm trong trọng số mô hình.
  - *Quy trình khi có văn bản mới:*
    1. thêm văn bản, ghi ngày ký, ngày hiệu lực, chuỗi sửa đổi, URL chính thức;
    2. tải bản gốc, OCR tiếng Việt, tách điều khoản;
    3. sửa các quy tắc bị ảnh hưởng;
    4. người duyệt ký, chạy test, tăng phiên bản.
  - *Đã làm:* tải đủ 24 văn bản ứng viên, OCR tiếng Việt 13 bản scan; sửa 3 lỗi ngày hiệu lực và nhãn của NĐ 83 (55 → 0 trích dẫn sai).
  - *Giới hạn:* registry chưa cập nhật QĐ 46 và NĐ 110; nút thắt là người duyệt.
- **Câu vặn:** "Mất bao lâu?" → Thêm vào registry mất từ vài giờ tới một ngày. Viết quy tắc phụ thuộc người duyệt pháp lý.
- **Bẫy:** nói "hệ thống tự cập nhật luật", hoặc "LLM tự đọc luật mới".

**Q16. "Gửi báo cáo lên LLM đám mây hay Kaggle có vi phạm Luật Bảo vệ dữ liệu cá nhân không? NĐ 13/2023 thì sao?"**
- **Trả lời:**
  - *Khung hiện hành:* Luật 91/2025 (hiệu lực 01/01/2026) và NĐ 356/2025. **NĐ 13/2023 đã hết hiệu lực từ 01/01/2026.**
  - *Nghĩa vụ chính:*
    - dùng nền tảng ở nước ngoài để xử lý dữ liệu cá nhân là chuyển xuyên biên giới (Điều 20.1(c)), phải lập hồ sơ đánh giá trong 60 ngày;
    - xử lý bằng AI phải phân loại rủi ro (Điều 30);
    - dữ liệu trên đám mây phải mã hóa;
    - phạt tới 5% doanh thu với vi phạm chuyển xuyên biên giới.
  - *GreenScan làm:*
    - demo chạy `offline`;
    - quy tắc A/B/C: chỉ tài liệu công khai mới được dùng đám mây; tài liệu nội bộ chỉ xử lý tại chỗ; hồ sơ kiểm toán chỉ trên hạ tầng của đơn vị (Luật Kiểm toán độc lập Điều 43);
    - thí nghiệm trên Kaggle và Groq chỉ dùng báo cáo đã công bố.
  - *Giới hạn:* việc dữ liệu "đã công khai theo quy định" được miễn đánh giá mới là suy luận, đang chờ ý kiến pháp lý.
- **Câu vặn:** "Startup có được miễn không?" → Được miễn hồ sơ đánh giá tác động và bộ phận bảo vệ dữ liệu trong 5 năm, nhưng **không** miễn nghĩa vụ khi chuyển dữ liệu ra nước ngoài.
- **Bẫy:** dẫn NĐ 13/2023 như còn hiệu lực.

**Q17. "Theo Luật Trí tuệ nhân tạo, GreenScan thuộc mức rủi ro nào? Có phải gắn nhãn không?"**
- **Trả lời:**
  - *Quy định:* Luật 134/2025 (hiệu lực 01/03/2026 theo nguồn thứ cấp) và NĐ 142/2026 (hiệu lực 01/05/2026) quy định phân loại rủi ro hệ thống AI, thông báo và gắn nhãn, đánh giá sự phù hợp với hệ thống rủi ro cao.
  - *GreenScan:* chưa tự xếp mức. Thiết kế đã đi theo hướng giảm rủi ro:
    - mô hình chỉ đọc;
    - kết luận về số và về luật do mã tất định đưa ra;
    - người duyệt cuối ký (`PENDING_HUMAN_REVIEW`);
    - gắn nhãn nội dung do AI tạo;
    - có huy hiệu "Có dùng AI đám mây" [KIẾN THỨC NỀN].
  - *Giới hạn:* chưa có ý kiến pháp lý về việc phân loại.
- **Câu vặn:** "Nếu bị xếp rủi ro cao thì sao?" → Hồ sơ tái lập (manifest, nhật ký kiểm tra) là nền cho bước đánh giá sự phù hợp.
- **Bẫy:** khẳng định "GreenScan rủi ro thấp" hay "không thuộc diện".

**Q18. "Sao không cho LLM đọc luật bằng RAG rồi kết luận? Nhanh hơn viết quy tắc bằng tay."**
- **Trả lời:**
  - *Vấn đề:* câu hỏi pháp lý có điều kiện và có thời gian. RAG trả về đoạn "giống" chứ không phải đoạn "áp dụng"; dễ lấy nhầm bản đã bị sửa; có thể bịa điều khoản; và không ai chịu trách nhiệm cho cách diễn giải.
  - *Ví dụ đã đo:* chuỗi sửa đổi cũ kéo NĐ 83 (chỉ về ô-dôn) vào 55 tuyên bố phát thải.
  - *GreenScan làm:*
    - retrieval chỉ dùng để tìm điều khoản ứng viên;
    - quyết định phải qua quy tắc có `source_clause`, `effective_from`, `reviewed_by` và unit test;
    - mọi kết luận phải trỏ tới điều khoản có trong file;
    - LLM được soạn nháp quy tắc, nhưng phải có người ký.
  - *Giới hạn:* hiện chưa có quy tắc nào qua cổng.
- **Câu vặn:** "Điều kiện dò từ khóa có ngây thơ quá không?" → Đúng. Vì vậy quy tắc nháp chỉ ở mức `partial`, điều kiện xác nhận để người xét. Bước tiếp theo là thay bằng điều kiện số và tra sổ bằng chứng.
- **Bẫy:** nói "LLM hiểu luật tốt hơn người".

**Q19. "Ai duyệt quy tắc? Sinh viên viết quy tắc pháp lý thì tin được không?"**
- **Trả lời:**
  - *Nói thật:* Thảo phụ trách quy tắc; cần chuyên gia bên ngoài xác nhận. `reviewed_by` để trống là điều kiện chặn đưa vào sản phẩm.
  - *Thiết kế phù hợp với tình huống này:*
    - quy tắc viết bằng YAML có phiên bản, trỏ điều khoản, có test, nên luật sư và kiểm toán viên đọc và ký được;
    - mức máy tự quyết được khai thật bằng `machine_executable` (full, partial, none).
  - *Hiện trạng:* 1 quy tắc ở mức partial, 0 quy tắc qua cổng.
  - Đây là việc cần đối tác. Mời BGK và đơn vị thực tế góp ý.
- **Bẫy:** nói "đã được luật sư duyệt".

**Q20. "Doanh nghiệp xi măng ghi 'đạt QCVN 19:2009' trong báo cáo 2025, trong khi QCVN 19:2024 đã có. Có sai không?"**
- **Trả lời:**
  - *Quy định:* QCVN 19:2024 có hiệu lực 01/07/2025, nhưng cơ sở đang hoạt động được dùng quy chuẩn cũ đến 31/12/2031. Vì vậy câu này không sai.
  - *GreenScan làm:*
    - tách chế độ lịch sử và chế độ hiện hành;
    - theo quy ước Q17, câu "đạt QCVN" được xếp QUALITATIVE;
    - nếu câu đó nằm trong mục "thành tựu xanh" thì là mẫu "trình bày yêu cầu pháp luật như ưu điểm" (ECGT 10a): chỉ là cờ, không phải kết luận.
  - *Giới hạn:* chưa có quy tắc cho trường hợp này.
- **Bẫy:** gắn cờ sai chỉ vì doanh nghiệp dẫn quy chuẩn cũ.

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

**5.1 Mâu thuẫn giữa các tài liệu**
1. **Số văn bản trong registry:** tiêu đề §1 của tài liệu 02 và mục A.1 của tài liệu nguồn ghi "12"; registry chỉ có **11** (v4 §2, mục 2). → Nói 11.
2. **NĐ 24/2025:**
   - A.3.1 ghi "ký 21/02/2025, hiệu lực 10/04/2025" [SECONDARY]; v4 ghi "hiệu lực khi ký" [VERIFIED].
   - Mức phạt theo NĐ 98/2020: tài liệu 02 ghi [UNVERIFIED], v4 ghi [VERIFIED].
   - → Dùng v4, kèm câu "chờ Thảo".
3. **Xử phạt quảng cáo:** tài liệu 02 §3 và A.3.2 còn dẫn NĐ 38/2021. Văn bản này **đã bị NĐ 87/2026 thay từ 15/05/2026**.
4. **Dự thảo thay TT 96:**
   - Tài liệu 02 §5 và A.3.8 nêu chi tiết: tham chiếu ISSB/IFC, 4 trụ cột, ngày 25/09, hạn góp ý 07/10 (nguồn báo chí).
   - v4 §2 cho biết cổng chính thức **không** nhắc các chi tiết này.
   - lsvn.vn (22/10/2026) cho biết dự thảo vẫn đang lấy ý kiến.
   - → Nói "dự thảo; theo báo chí có…".
5. **Luật AI:** tài liệu 02 ghi Luật 134/2025 và NĐ 142/2026 là [UNVERIFIED]. v4 ghi NĐ 142 ký 30/04/2026, hiệu lực 01/05/2026 [VERIFIED], và Luật 134 có hiệu lực 01/03/2026 [SECONDARY].
6. **QĐ 21/2025:** tài liệu 02 ghi "chưa xác minh có văn bản thay thế". Theo v4, QĐ 46/2026 chạy song song và **đã có hiệu lực từ 01/11/2026**.
7. **Rule pack:** ghi chú STATUS (09/08) nói "QĐ 21 là bản scan, không trích được". Nay registry ghi ok_ocr với độ tin cậy 93,25 và có 137 dòng điều khoản. Lý do đúng hôm nay là: chưa bind điều khoản, chưa có người ký, và `claim_types` lệch.
8. **Registry, mục TT 17:** ghi chú "harvest pending" mâu thuẫn với việc file điều khoản đã có.
9. **Hai nghĩa vụ không khớp:** Luật BVMT Đ.91.7(a) (gửi Bộ trước 01/12) và NĐ 119 Đ.11.4(b) (gửi UBND tỉnh trước 31/3). Không tự phân xử; ghi chú và dẫn nghị định.
10. **Tỷ lệ đảm bảo:** "2/22" có đảm bảo trong khi cùng bài nêu "26 báo cáo độc lập", nên mẫu số không rõ; chỉ dùng như số định hướng. Số "25–27% được đảm bảo" của Pham Viet Anh mâu thuẫn với số bình duyệt, **không dùng**.
11. **QĐ 13/2024:** số cơ sở tăng so với QĐ 01/2022 được ghi là "tăng 254" ở nguồn này và "tăng 259" ở nguồn khác (cả hai thứ cấp).

**5.2 Số đã cũ so với kết quả 31/10–01/11**
- `TXT/GreenScan_100_Cau_BGK.txt` dòng 6 và mục C dùng số **cũ**:
  - "HPG 210 claim, CONTRADICTED 4%" → nay là 156 tuyên bố, với 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT;
  - "gold adjudicated 5 claim" → nay là **0 nhãn người** (0/88 cặp, 0/79 câu);
  - "4/4 case thật khớp verdict", "233 test", "21 bẫy" → chưa đo lại; 17 bẫy xanh là phần cổng còn mở;
  - "~4.200 điều khoản; TT 96 chưa có file" → nay là 4.189 dòng trong 11 file, TT 96 đã có 327 dòng; Luật BVMT **vẫn chỉ Điều 1–89**.
- Q60 và Q79 trong cùng file nói việc soạn quy tắc chạy bằng GLM-5.2 trên FPT. **Khóa FPT lỗi 401 từ 31/10**; người dùng quyết không dùng khóa trả phí; demo chạy offline; thí nghiệm dùng Qwen3 trên Kaggle. → Không nói GLM-5.2 hay FPT như hiện trạng.
- Q75 và Q76 của file đó không nêu miễn trừ 6.1–6.3 cho ngân hàng. Bổ sung khi trả lời.
- Tài liệu 02 vẫn còn 8 điểm chờ sửa (v4 §2). Registry cũng chưa cập nhật `amended_by` của Luật BVMT và TT 96, chưa có NĐ 110/2026 và QĐ 46/2026.
- Các số **vẫn đúng**: F5 (0/156), F1 (153/156), 780/780 bằng chứng nội bộ, trạng thái IMPLEMENTED–NOT VALIDATED.

**5.3 Điều không được nói**
- "Doanh nghiệp X tẩy xanh" hoặc "vi phạm"; "GreenScan phát hiện vi phạm pháp luật"; "GreenScan tư vấn pháp lý". Không đưa tên doanh nghiệp Việt Nam làm ví dụ tẩy xanh; chỉ nói "ca kiểm tra" hoặc "khoảng trống bằng chứng".
- "Luật Việt Nam định nghĩa hoặc cấm tẩy xanh"; "Điều 6.9 cấm mọi thông tin sai".
- "Có 4.189 (hay 4.200) quy tắc"; "đã đối chiếu taxonomy hoặc QĐ 21"; "quy tắc đã được luật sư hoặc Thảo duyệt".
- Viện dẫn như còn hiệu lực các văn bản đã bị thay: **NĐ 13/2023**, **NĐ 38/2021**, **NĐ 43/2017 và NĐ 111/2021** (về nhãn hàng hóa).
- "TT 96 đã bị thay"; "ISSB đã bắt buộc ở Việt Nam"; "Việt Nam có lộ trình ISSB".
- "Green Claims Directive đã có hiệu lực"; "CMA phạt 10%"; bất kỳ mức phạt nào của NĐ 45/2022 hay NĐ 156/2020 (chưa đọc bản gốc).
- "GreenScan là kiểm toán, đảm bảo hay xác nhận"; "GreenScan thay kiểm toán viên".
- "Kiểm kê KNK hằng năm"; "NĐ 83 quy định về KNK"; "ngân hàng được miễn toàn bộ mục 6".
- "PwC: 10% doanh nghiệp có đảm bảo"; "45% doanh nghiệp có báo cáo phát triển bền vững độc lập" (nguồn xám).
- "Chưa từng có ai làm". Nói thay bằng: "trong phạm vi đã rà, chúng tôi không tìm thấy".
- "Dữ liệu của khách hàng được gửi lên Kaggle hoặc Groq".
- Kết cục vụ *Lizama v. H&M*: [CHƯA XÁC MINH], không nêu.
