# Kế hoạch dữ liệu v4: pháp lý mới, quy trình và mở rộng ngành

Ngày 13/10/2026. Tài liệu này **nối tiếp mục 4 của** `CHUONG_TRINH_THI_NGHIEM_VA_DU_LIEU_v3_2026-10-13.md`, không thay thế nó.

**Nguồn:** hai catalog đã qua kiểm chứng đối kháng, nằm trong `data/legal/catalog/2026-10-13/`:
- `vn_delta.json`: 20 mục, những gì đã thay đổi so với `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`;
- `vn_consumer_ads_labeling.json`: 17 mục giữ lại, 2 mục bị loại.

**Nhãn xác minh:**
- **[VERIFIED]**: đã đọc văn bản gốc hoặc cổng chính thức;
- **[SECONDARY]**: nguồn thứ cấp uy tín;
- **[UNVERIFIED]**: chỉ là đầu mối.

Chưa mục nào được Thảo duyệt.

## 0. Tóm tắt

1. **Mười văn bản đổi cách kiểm chứng tuyên bố.** Đó là:
   - EPR chuyển sang NĐ 110/2026;
   - QĐ 46/2026 lập chế độ "dự án xanh, tuần hoàn, ESG" thứ hai, có hiệu lực 01/11/2026, tức giữa Bán kết và Chung kết;
   - sổ đăng ký tín chỉ các-bon TT 11/2026;
   - tín chỉ các-bon rừng NĐ 180/2026;
   - quy chuẩn khí thải mới QCVN 19:2024;
   - nghị định nhãn hàng hóa NĐ 37/2026, thay NĐ 43/2017 và NĐ 111/2021;
   - nghị định xử phạt quảng cáo NĐ 87/2026, thay NĐ 38/2021;
   - danh sách 21 giấy chứng nhận Nhãn sinh thái Việt Nam;
   - quy trình báo cáo công tác BVMT mới theo TT 09/2026.
2. **Ba thông tư MRV theo ngành là "từ điển bằng chứng" cho ngành phát thải cao:** điện và thép (TT 38/2023/TT-BCT), xi măng (TT 13/2024/TT-BXD), giao thông (TT 63/2024/TT-BGTVT).
3. **Tài liệu 02 có 8 chỗ đã cũ hoặc thiếu** (mục 2). Mình chỉ gắn cờ dẫn sang đây, không tự sửa 02. Thảo xác nhận rồi mới sửa.
4. **Dữ liệu đã bắt đầu thu thập, không tốn token Claude:** 24 văn bản ứng viên ở `configs/legal/registry_candidates_2026-10.yaml`, tải bằng `tools/crawl_legal_sources.py`. Registry thật chưa bị đụng tới.
5. **Phần tạm dừng để tiết kiệm token:**
   - Quốc tế: chỉ có bản nháp EU và châu Á, chưa kiểm chứng.
   - Các quy trình VN còn lại: môi trường cốt lõi, năng lượng, nông nghiệp. Lần này chỉ kiểm phần thay đổi.

## 1. Thay đổi pháp lý ảnh hưởng tới kiểm chứng tuyên bố

| Quy trình | Văn bản | Ký → hiệu lực | Điểm chính khi kiểm chứng | Nhãn |
|---|---|---|---|---|
| EPR (tái chế, thu hồi) | NĐ 110/2026/NĐ-CP | 01/04/2026 → 25/05/2026 | Bãi bỏ Chương VI và Phụ lục XXII–XXIII NĐ 08/2022. Tuyên bố tái chế **từ năm 2026** đối chiếu NĐ 110; năm 2025 trở về trước vẫn theo NĐ 08. DN doanh thu < 30 tỷ được miễn. Phương tiện giao thông đường bộ thuộc diện từ 01/01/2027 | [VERIFIED] |
| | TT 24/2026/TT-BNNMT | 25/05/2026 → 25/05/2026 | Mức đóng góp tài chính theo khối lượng; mẫu biểu | [VERIFIED] |
| Dự án xanh | QĐ 46/2026/QĐ-TTg | 17/09/2026 → **01/11/2026** | Chế độ thứ hai, song song QĐ 21/2025. Xác nhận bởi tổ chức đạt ISO/IEC 17029 hoặc VSAE/ISAE 3000. Khung ESG ở Phụ lục VI–VII. **Tỉnh công bố danh mục dự án xanh, tuần hoàn mỗi 30/6 và 31/12** | [VERIFIED] |
| | QĐ 21/2025/QĐ-TTg | còn hiệu lực | Không tìm thấy văn bản thay thế; TT 09/2026 vẫn dẫn chiếu | [UNVERIFIED] (tìm không ra ≠ không có) |
| Tín chỉ, bù trừ | TT 11/2026/TT-BNNMT | 13/02/2026 → 30/03/2026 | Sổ đăng ký quốc gia: tín chỉ dùng để bù trừ chuyển sang tiểu khoản bù trừ và bị hủy; công khai định kỳ tháng, năm, hai năm. **Nguồn đối chiếu chính cho tuyên bố "trung hòa nhờ tín chỉ"** | [VERIFIED] |
| | NĐ 180/2026/NĐ-CP | 21/05/2026 → 15/07/2026 | Tín chỉ các-bon rừng đã bán thì không bán lại (Đ.3.3); không làm ảnh hưởng mục tiêu NDC. Báo chí đưa tin "trần xuất khẩu 50%" nhưng **không thấy** trong Đ.1–20 | [VERIFIED] |
| MRV theo ngành | TT 38/2023/TT-BCT | 27/12/2023 → 11/02/2024 | Kiểm kê, thẩm định KNK cho nhiệt điện và thép (Đ.24, 32) | [VERIFIED] |
| | TT 13/2024/TT-BXD | 20/12/2024 → 05/02/2025 | Xi măng: công thức tỷ lệ clinker, sản lượng; kiểm được "giảm tỷ lệ clinker", "CO2/tấn xi măng" | [VERIFIED] |
| | TT 63/2024/TT-BGTVT | 30/12/2024 → 15/02/2025 | Giao thông: hàng không, hàng hải. Vẫn hiệu lực sau sáp nhập bộ | [VERIFIED] (ngày ký: [SECONDARY]) |
| Quan trắc, quy chuẩn | TT 45/2024/TT-BTNMT (QCVN 19:2024/BTNMT) | 30/12/2024 → 01/07/2025 | Khí thải công nghiệp. Cơ sở đang hoạt động được dùng quy chuẩn cũ **đến 31/12/2031**. Vì vậy BCTN 2025 ghi "đạt QCVN 19:2009" **không sai** | [VERIFIED] |
| | TT 06/2025/TT-BTNMT (QCVN 40:2025/BTNMT) | 28/02/2025 → 01/09/2025 | Nước thải công nghiệp; thay QCVN 40:2011 và QCVN 52:2017 (thép); lộ trình tới 2031/2032 | [SECONDARY] |
| Báo cáo BVMT | TT 09/2026/TT-BNNMT | 29/01/2026 → 29/01/2026 | Báo cáo công tác BVMT gửi Sở NN&MT và UBND xã. Dự thảo báo cáo đề xuất cấp giấy phép môi trường **công khai ≥ 10 ngày**: thêm một nguồn bằng chứng | [VERIFIED] |
| Nhãn sinh thái | CV 10612/BNNMT-MT | 22/12/2025 | Danh sách 21 giấy chứng nhận Nhãn sinh thái VN 2024–2025, **toàn bộ là bao bì**, hiệu lực 3 năm (ví dụ An Phát Xanh ANECO đến 10/12/2027). Danh sách có 2 lỗi dữ liệu | [VERIFIED] |
| Quảng cáo | Luật 75/2025/QH15 (sửa Luật Quảng cáo) | 16/06/2025 → 01/01/2026 | Đ.19: nội dung trung thực; Đ.8.10: so sánh phải có tài liệu chứng minh; Đ.19.3(b): công bố thông tin bắt buộc **không phải** quảng cáo | [VERIFIED] |
| | NĐ 342/2025/NĐ-CP | 26/12/2025 → 15/02/2026 | Hướng dẫn Luật Quảng cáo. Đ.19: lưu trữ 3 năm kể từ ngày cuối cùng quảng cáo hiển thị (nghĩa vụ của DN dịch vụ quảng cáo trực tuyến) | [VERIFIED] |
| | NĐ 87/2026/NĐ-CP | 27/03/2026 → 15/05/2026 | Xử phạt quảng cáo, **thay NĐ 38/2021**, Đ.4 NĐ 129/2021 và NĐ 128/2022. Đ.50.5(c): quảng cáo gây nhầm lẫn 80–100 triệu. Đ.50.2(a): "nhất, số một" 10–20 triệu. Đ.50.4(b): so sánh 40–60 triệu. Mức cho cá nhân hay tổ chức: Thảo xác nhận | [VERIFIED] |
| Người tiêu dùng | Luật 19/2023/QH15 | 20/06/2023 → 01/07/2024 | Đ.10.1(a): cấm gây nhầm lẫn, kể cả về giấy chứng nhận | [VERIFIED] |
| | NĐ 98/2020, sửa bởi NĐ 24/2025 | 24/2025: 21/02/2025, hiệu lực khi ký | Đ.47.2(a): cá nhân 20–30 triệu, tổ chức 40–60 triệu (Đ.4.4(b) mới) | [VERIFIED] |
| Nhãn hàng hóa | NĐ 37/2026/NĐ-CP | 23/01/2026 → 23/01/2026 | **Bãi bỏ NĐ 43/2017 và NĐ 111/2021** (Đ.97.4). Đ.50.1: nội dung ghi thêm trên nhãn, kể cả tuyên bố xanh trên bao bì, phải trung thực, chính xác | [VERIFIED] (mới đọc Đ.50 và Đ.97) |
| Thương mại điện tử | Luật 122/2025/QH15 | 10/12/2025 → 01/07/2026 | Mới xác minh số hiệu và ngày; nội dung chưa đọc | [VERIFIED] (chỉ số hiệu và ngày) |
| Công bố thông tin | Dự thảo thay TT 96/2020 | dự thảo | Phụ lục ESG riêng. Chỉ tiêu không công bố phải giải trình và có kế hoạch. BCTN 120 ngày. Tiếng Anh bắt buộc với mọi đối tượng từ 01/01/2028 | [VERIFIED] (bản tóm tắt trên cổng; chưa đọc toàn văn) |
| Xử phạt môi trường | NĐ 45/2022/NĐ-CP | 07/07/2022 → 25/08/2022 | Căn cứ cho chỉ tiêu 6.5 của TT 96 (số lần, số tiền phạt). Có dự thảo sửa đổi | [SECONDARY] |
| Thanh tra | Luật 84/2025/QH15 | thông qua 25/06/2025 → 01/07/2025 | Chỉ còn thanh tra trung ương và tỉnh. **Không có cổng quốc gia công khai vi phạm**; phải lấy theo từng tỉnh | [SECONDARY] |

## 2. Tài liệu 02 cần sửa (chờ Thảo xác nhận)

1. **§1, dòng NĐ 08/2022:** thiếu NĐ 110/2026 trong cột "sửa đổi bởi". Registry: thêm `ND110-2026-ND-CP` vào `amended_by`; đã ghi ở mục `updates_to_existing` của file ứng viên.
2. **§1, tiêu đề:** ghi "Mười hai văn bản" nhưng bảng và registry chỉ có 11.
3. **§3:**
   - còn dẫn **NĐ 38/2021**, đã hết hiệu lực từ 15/05/2026 (NĐ 87/2026 thay thế);
   - mức phạt NĐ 98/2020 và NĐ 24/2025 nay đã xác minh, không còn [UNVERIFIED].
4. **§5, dòng dự thảo TT 96:** cổng chính thức (05/10) **không** nhắc ISSB/IFC, "4 trụ cột", ngày 25/09 hay hạn 07/10. Các chi tiết này chưa được xác nhận.
5. **§5, dòng QĐ 21/2025:** vẫn chưa có văn bản thay thế, nhưng đã có QĐ 46/2026 chạy song song.
6. **§6, dòng Luật AI:**
   - NĐ 142/2026 có thật: ký 30/04/2026, hiệu lực 01/05/2026 [VERIFIED];
   - Luật 134/2025 hiệu lực 01/03/2026 [SECONDARY].
7. **Thẩm quyền nhận báo cáo:** mọi mẫu biểu hay quy tắc còn ghi "cấp huyện" hoặc "Sở TN&MT" đều đã cũ (TT 09/2026).
8. **Nghị định nhãn hàng hóa:** mọi chỗ dẫn NĐ 43/2017 hoặc NĐ 111/2021 phải đổi sang NĐ 37/2026.

## 3. Năm lớp dữ liệu pháp lý và việc đã làm

| Lớp | Nội dung | Đường dẫn | Công cụ | Trạng thái 13/10 |
|---|---|---|---|---|
| L1. Văn bản và điều khoản | Toàn văn, parse theo điều khoản | `data/legal/raw/<id>/`, `data/legal/clauses/` | `tools/catalog_to_registry.py` → `tools/crawl_legal_sources.py --registry configs/legal/registry_candidates_2026-10.yaml --all` → `tools/ocr_legal_document.py` (vie) | 24 ứng viên, **đã tải đủ 24 bản gốc**: 11 bản có lớp chữ, 13 bản scan **đã OCR tiếng Việt** (`ocr.txt`, độ tin cậy trung bình mỗi trang phần lớn 91–96). Còn lại: parse điều khoản, rồi Thảo duyệt |
| L2. Ma trận nghĩa vụ | Chủ thể × ngành × quy trình × hạn | đề xuất `data/legal/obligations_2026-10.csv` | Lấy từ trường `sectors`, `process_types`, `key_dates` của catalog | Chưa làm |
| L3. Sổ bằng chứng công khai | Danh sách để đối chiếu tuyên bố | đề xuất `data/legal/evidence/` | Tải thủ công hoặc crawl | Xem bảng dưới |
| L4. Ca đã phán quyết | Ca tẩy xanh có câu nguyên văn | `data/legal_cases/` | — | Đợt này không tìm thêm ca VN; bản nháp quốc tế tạm dừng |
| L5. Quy ước gán nhãn | Quy tắc rút ra khi phân xử | `QUY_TRINH_GAN_NHAN_T1` §5 | Họp nhóm | Q18–Q24 đề xuất (mục 5) |

**L3: các sổ bằng chứng nên lấy**, xếp theo ưu tiên:

| Sổ | Kiểm được tuyên bố gì | Truy cập | Ưu tiên |
|---|---|---|---|
| Danh sách Nhãn sinh thái (CV 10612/BNNMT-MT) | "Sản phẩm đạt Nhãn sinh thái / Nhãn xanh Việt Nam", "thân thiện môi trường" có chứng nhận | PDF công văn trên cổng Sở NN&MT Lạng Sơn | P0 |
| Công khai của sổ đăng ký tín chỉ (TT 11/2026) | "Trung hòa các-bon", "bù trừ bằng tín chỉ": tín chỉ có thật sự bị hủy để bù trừ không | Cổng của Bộ NN&MT; chưa xác định URL | P1 |
| Danh sách cơ sở QĐ 13/2024 | Có thuộc diện kiểm kê KNK không | Đã có trong repo | Sẵn |
| Kết quả giao dịch sàn các-bon (NĐ 29/2026) | Tuyên bố mua, bán hạn ngạch | HNX công bố cuối ngày | P1 |
| Danh mục dự án xanh, tuần hoàn của tỉnh (QĐ 46/2026) | "Dự án xanh được xác nhận" | Cổng tỉnh, mỗi 30/6 và 31/12; đợt đầu sau 01/11/2026 | P2 |
| Dự thảo báo cáo đề xuất giấy phép môi trường (TT 09/2026) | Công suất, công nghệ, biện pháp xử lý tự công bố | Cổng tỉnh, công khai ≥ 10 ngày | P2 |
| Quyết định xử phạt và thanh tra cấp tỉnh | Mâu thuẫn với "tuân thủ pháp luật BVMT", chỉ tiêu 6.5 TT 96 | Theo từng tỉnh, không có cổng quốc gia | P2 (tốn công) |

## 4. Mở rộng ngành: ngành nào có thêm tuyên bố kiểm chứng được

| Ngành | Vì sao (văn bản) | Tuyên bố sẽ gặp | Cần làm |
|---|---|---|---|
| Xi măng | TT 13/2024/TT-BXD; hạn ngạch thí điểm QĐ 263/2026 (51 nhà máy) | Tỷ lệ clinker, CO2/tấn xi măng, đồng xử lý chất thải | Thêm 1–2 DN xi măng niêm yết vào danh mục crawl |
| Nhiệt điện, thép | TT 38/2023/TT-BCT; QĐ 263/2026 | Cường độ phát thải, thẩm định KNK | Đã có HPG; thêm 1 DN nhiệt điện |
| Bao bì, nhựa, hàng tiêu dùng | NĐ 110/2026 (EPR); Nhãn sinh thái toàn là bao bì; NĐ 37/2026 về nhãn | Tỷ lệ tái chế, "bao bì thân thiện môi trường", "đạt Nhãn sinh thái" | Thêm DN nhựa, bao bì có tên trong danh sách nhãn sinh thái (kiểm có BCTN, báo cáo PTBV) |
| Hàng không, vận tải biển | TT 63/2024/TT-BGTVT | Nhiên liệu SAF, cường độ phát thải mỗi chuyến | P2 |
| Lâm nghiệp, tín chỉ | NĐ 180/2026; TT 11/2026 | Bán tín chỉ rừng, trung hòa nhờ tín chỉ | P2 |
| Ngân hàng, dự án xanh | QĐ 46/2026; QĐ 21/2025; TT 17/2022/TT-NHNN | "Tài trợ dự án xanh được xác nhận" | Sau Chung kết (đã có trong kế hoạch v3) |

**Giữ miền Việt Nam:** ngành mới vào train theo **công ty**, không theo câu. Test vẫn là HPG và các công ty giữ lại.

## 5. Tác động tới gán nhãn T1

**Móc tuyên bố mới, xếp vào chủ đề có sẵn** (chưa cần chủ đề mới):

| Tuyên bố | Chủ đề | Ghi chú |
|---|---|---|
| Tái chế, EPR, thu hồi bao bì | `waste_and_circularity` | Có tỷ lệ hoặc khối lượng thì là QUANTIFIED |
| "Đạt Nhãn sinh thái", chứng nhận sản phẩm xanh | `esg_process_integration` (chứng nhận) | Kiểm chứng với sổ L3 |
| Tín chỉ, bù trừ, "trung hòa các-bon" | `emissions_reduction` | Cờ OVERCLAIM nếu "trung hòa" chỉ nhờ tín chỉ: hướng EmpCo (EU) đang đi; tại VN chưa có quy định cấm, chỉ là cờ, không phải kết luận |
| "Đạt QCVN …" về khí thải, nước thải | Q17 → QUALITATIVE | Quy chuẩn cũ vẫn hợp lệ đến 2031 |

**Quy ước đề xuất Q18–Q24.** Hai agent phân xử lượt 2 gặp các tình huống Q1–Q17 chưa đủ rõ (80% câu đã gán trong b02–b11). Đây là **đề xuất của Claude để họp nhóm chốt**, chưa áp dụng:

| Mã | Tình huống | Đề xuất của người phân xử | Ví dụ |
|---|---|---|---|
| Q18 | Câu trỏ ngược ("Đây là", "This recognition") rồi chỉ đánh giá | VAGUE, trừ khi chính câu nêu việc cụ thể | "…là minh chứng sự cam kết…" |
| Q19 | Đếm nơi diễn ra hoạt động ("trên 50 dự án … tổng vệ sinh") | Không là số liệu kết quả → QUALITATIVE (mở rộng Q10) | id cdc26623cb9ae9ec |
| Q20 | "Chiến lược PTBV / ESG" chung, không có yếu tố môi trường, nhưng không theo nghĩa trường tồn của Q14 | VAGUE / `generic_sustainability`. Lượt A gán `non_env`: cần chốt | "…theo đuổi chiến lược phát triển bền vững…" |
| Q21 | DN tham gia hội thảo, diễn đàn bền vững | Chưa chốt: QUALITATIVE (như giải thưởng Q11) hay NOT_CLAIM | "…tham gia chia sẻ tại Hội thảo… kinh tế tuần hoàn" |
| Q22 | Động từ ý định yếu ("cân nhắc", "nghiên cứu giải pháp") gắn với biện pháp cụ thể | Chưa chốt: QUALITATIVE + FUTURE hay VAGUE | "Cân nhắc triển khai lắp đặt điện mặt trời áp mái" |
| Q23 | Sản lượng kinh doanh tính bằng đơn vị năng lượng hoặc nhiên liệu (than giao nhận, kWh phát) | NOT_CLAIM / `non_env`, trừ khi câu gắn với môi trường | "tổng khối lượng than giao nhận… 2.785.000 tấn" |
| Q24 | Chữ infographic lẫn trong câu | Tiêu đề lẫn vào → `table_heading`; danh sách gạch đầu dòng → gán theo mục trọn nghĩa; phần chú thích dính vào câu văn → bỏ chú thích | "• 50% tòa nhà lắp đặt hệ thống năng lượng tái tạo" |

**Khoảng trống chủ đề:** thích ứng khí hậu chưa có chủ đề; câu ESG chung chung đang lẫn giữa `esg_process_integration` và `generic_sustainability`.

## 6. Tác động tới kiểm chứng (quy tắc có ngày)

Bộ kiểm có hai chế độ: `historical_compliance` (luật lúc DN công bố) và `current_policy_alignment` (luật hiện hành). Các văn bản mới khiến chế độ lịch sử trở nên quan trọng:

1. **QCVN:** báo cáo 2025–2031 viện dẫn quy chuẩn cũ là hợp lệ với cơ sở đang hoạt động. Không gắn cờ.
2. **EPR:** năm báo cáo ≤ 2025 đối chiếu NĐ 08/2022 Chương VI; từ 2026 đối chiếu NĐ 110/2026.
3. **Dự án xanh:** từ 01/11/2026 có hai bộ tiêu chí; tuyên bố phải nói rõ theo bộ nào.
4. **Nhãn hàng hóa:** từ 23/01/2026 dẫn NĐ 37/2026, không còn NĐ 43/2017.
5. **"Trung hòa nhờ tín chỉ":** từ 30/03/2026 đối chiếu được với dữ liệu công khai của sổ đăng ký.
6. **Thông tin bắt buộc trong BCTN không phải quảng cáo** (Luật 75/2025 Đ.19.3(b)). Vì vậy móc pháp lý quảng cáo chỉ áp khi nội dung được dùng lại trong truyền thông. Điều này **đúng với cách 02 đang ghi** ("tham chiếu ngữ cảnh, không dùng kết luận").

## 7. Việc tiếp theo

| Việc | Ai | Tốn token Claude? | Hạn |
|---|---|---|---|
| Tải 24 văn bản ứng viên | máy (harvester) | Không | **xong 13/10** |
| OCR tiếng Việt cho các bản scan | máy (`ocr_legal_document.py --langs vie+eng`) | Không | **xong 13/10** (13 bản) |
| Thảo duyệt P0: NĐ 110/2026, QĐ 46/2026, NĐ 37/2026, NĐ 87/2026, TT 11/2026, QCVN 19:2024; 8 điểm sửa ở mục 2 | Thảo | Không | trước 25/10 |
| Tải danh sách Nhãn sinh thái về `data/legal/evidence/` | Nhân | Không | 18/10 |
| Chốt Q18–Q24 ở họp nhóm | 3 người | Không | họp 1 |
| Kiểm chứng bản nháp quốc tế (EU, châu Á) | agent | **Có** (~2 agent) | chỉ khi cần cho Chung kết |
| Các quy trình VN chưa kiểm (môi trường cốt lõi, năng lượng, nông nghiệp) | agent | **Có** (~2–3 agent) | chỉ khi cần |

## 8. Rủi ro

- **OCR bằng mô hình tiếng Anh mất dấu:** số và ngày đọc được, điều khoản phải OCR lại bằng `vie` trước khi gắn quy tắc.
- **Tìm không ra ≠ không có:** hai mục "không có sửa đổi hoặc thay thế" (NĐ 06/2022, QĐ 21/2025) là kết quả tìm kiếm âm, nên để [UNVERIFIED].
- **Nguồn thứ cấp:** QCVN 40:2025, NĐ 45/2022, Luật 84/2025 chưa có bản gốc. Không gắn quy tắc trước khi có.
- **Báo chí sai ngày:** NĐ 180/2026 có hiệu lực 15/07, **không phải** 01/07; TT 11/2026 có hiệu lực 30/03, **không phải** 13/02. Đừng chép từ báo.
- **Dữ liệu nước ngoài** không bao giờ làm test Việt Nam (nguyên tắc 11 của v3).
