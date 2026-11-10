# R3: Tẩy xanh — lý thuyết, phân loại, án lệ và vụ kiện

*Ghi chú chuẩn bị Chung kết 10/11/2026, viết 04/11/2026. Đường dẫn tính từ REPO = `D:\Sinh viên CNhan\AI quantum\docs\greenscan-ai\GreenScan-AI`.*
*Nhãn: [ĐÃ THỰC NGHIỆM] số đội tự đo · [NGOÀI] dữ kiện từ nguồn bên ngoài đã đọc · [KIẾN THỨC NỀN] hiểu biết chung, chưa đối chiếu nguyên bản trong phiên này · [GIẢ THUYẾT] suy luận chưa kiểm · [CHƯA XÁC MINH] chưa kiểm được.*

**Nguồn đã đọc**
- Toàn văn: `docs/08-knowledge/01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md`, `04_AN_LE_VA_BAI_HOC.md`, `06_HAM_Y_CHO_GREENSCAN.md` (cùng cập nhật 06/10/2026); 7 file `docs/01-domain-audit/` (AGENT_CRITERIA, AUDIT_PROTOCOL, CLAIM_VERIFICATION_WORKING_PAPER, EVIDENCE_STANDARD, GREENWASHING_TAXONOMY, MANUAL_SCORING_RUBRIC, REVIEWER_QA_CHECKLIST; bản 0.1 ngày 07/07/2026, tiếng Anh).
- Đơn kiện Lizama v. H&M (`C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt\lizama_v_hm_complaint.txt`, 55 trang): đọc ¶1–70 (bản chất vụ kiện, các bên, thẩm quyền, cáo buộc, định nghĩa nhóm), tiêu đề 11 Count, phần yêu cầu ¶249–250. Không đọc chi tiết ¶77–248 vì chỉ lặp lại cáo buộc theo từng điều luật.
- `data/legal_cases/`: `MERGE_MANIFEST.json`, `reports/COLLECTION_REPORT_2026-08-08.md`, metadata 297 bản ghi `documents.jsonl` (trường `qualifier`, `legal_strength`, `case_id`) cho cả 28 thư mục. Thư mục **không có README hay thẻ tóm tắt**, nên tôi trích chữ từ HTML phán quyết ra `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\R3\` (script ở `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\R3_scripts\`) và đọc phần mô tả quảng cáo, đánh giá, kết luận, chế tài của 21 phán quyết: ASA (Shell 2023, Shell 2025, TotalEnergies, HSBC, Repsol, Petronas, Nike, Uniqlo, Adidas 2026, Calvin Klein, Lloyds, Oatly, Unilever, Tesco, Etihad, Lufthansa, Equinor, Mazda) và ASIC/Tòa Liên bang Úc (Mercer, Vanguard, Active Super).
- Đối chiếu: `docs/08-knowledge/sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md` (Grep phần D, E, danh mục R99–R141); `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` mục 0–2 và 10; `docs/00-project/AUDIT_HE_THONG_2026-10.md` dòng 73–77; `src/quantum_gw/studio/suggest.py` dòng 1–101; `data/real_cases/README.md`, `VALIDATION_REPORT.txt`.
- Web 04/11 (nguồn thứ cấp): kết cục Lizama — https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/hm-wins-dismissal-in-greenwashing-suit , https://www.thefashionlaw.com/hm-escapes-lawsuit-accusing-it-of-greenwashing-its-fast-fashion-wares/ , https://natlawreview.com/article/lizama-et-al-v-hm-lesson-artful-crafting-green-claims ; TerraChoice 2009 — https://www.packagingdigest.com/smart-packaging/greenwashing-affects-98-percent-of-products-says-terrachoice , https://theecologist.org/2009/jun/23/greenwash-taints-most-eco-friendly-claims ; Delmas & Burbano — https://ioes.ucla.edu/publication/the-drivers-of-greenwashing .

**Không đọc được hoặc không đọc, và vì sao**
- Toàn văn Delmas & Burbano 2011, Lyon & Maxwell 2011, Lyon & Montgomery 2015, Seele & Gatti 2017: phải trả phí. Chỉ dựa vào tóm tắt, metadata đã kiểm trong file sources và nguồn thứ cấp.
- Văn bản lệnh bác đơn Lizama (12/05/2023): chưa đọc nguyên văn, chỉ qua bình luận của các hãng luật.
- Báo cáo TerraChoice 2007 và 2010: không tìm được nguồn cho số sản phẩm.
- Bản án Tòa Paris về TotalEnergies (23/10/2025): không có trong thư mục; file sources chỉ dẫn nguồn thứ cấp (Columbia Climate Law Blog).
- PDF bản án Mercer, Active Super; hồ sơ SEC (GSAM, Invesco, WisdomTree); thông báo phạt ASIC (Black Mountain, Fertoz, Tlou, Morningstar, Northern Trust): chỉ đọc metadata và `qualifier`. 180 tài liệu doanh nghiệp giai đoạn 2: không đọc.

## 1. Tóm tắt từng tài liệu

### 1.1 `01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md` (06/10)
- **Là gì:** bảng định nghĩa có thẩm quyền, 21 mẫu hình tẩy xanh với hai cột "máy kiểm được?" và "GreenScan hôm nay" (đối chiếu code ngày 06/10), và bảng ánh xạ sang cơ sở dẫn liệu ISA 315.
- **Luận điểm:**
  1. ESAs (04/06/2024): tẩy xanh là tuyên bố "không phản ánh rõ ràng và công bằng hồ sơ bền vững thực", **cố ý hoặc vô ý**; báo cáo tiến độ 2023 liệt kê 12 tính chất gây hiểu nhầm.
  2. ECGT (Chỉ thị EU 2024/825) áp dụng từ 27/09/2026; báo cáo gửi nhà đầu tư thường ngoài phạm vi.
  3. CMA có 6 nguyên tắc; FTC đòi "reasonable basis".
  4. Luật Việt Nam **không định nghĩa "tẩy xanh"** trong 14 văn bản đã đọc toàn văn.
  → GreenScan nói "mức đủ bằng chứng của từng tuyên bố", không gắn nhãn tẩy xanh.
- **Trạng thái 21 mẫu (06/10):**
  - Có thủ tục chạy thật: 4 mẫu (2 không chứng minh, 7 sai sự thật/mâu thuẫn số, 12 mốc so sánh, 13 lệch phạm vi).
  - Một phần: 9 mẫu (1, 6, 8, 10, 11, 14, 15, 17, 19).
  - Chưa có: 8 mẫu (3, 4, 5, 9, 16, 18, 20, 21).
  - Mẫu "rẻ để làm": 9, 4, 18, 6.
- **Liên quan GreenScan:** đây là bản đồ năng lực để trả lời "máy làm được gì, không làm được gì".
- **Giống và khác:** giống ESAs ở phạm vi rộng (vô ý cũng tính). Khác cơ quan quản lý ở chỗ GreenScan không kết luận vi phạm và chỉ đọc chữ, không đọc ảnh (mẫu 16).

### 1.2 `04_AN_LE_VA_BAI_HOC.md` (06/10)
- **Là gì:** 12 trong 32 vụ quốc tế đã kiểm, cùng 9 bài học xuyên vụ, mỗi bài học gắn một thủ tục kiểm và trạng thái GreenScan.
- **Số chính:**
  - Việt Nam: chưa tìm thấy vụ xử phạt vì tuyên bố môi trường gây hiểu nhầm (phủ định có giới hạn).
  - KLM: 15/19 phát ngôn gây hiểu lầm, SAF chỉ khoảng 0,5%.
  - SEC: BNY US$1,5 triệu; DWS US$19 triệu (cộng €25 triệu ở Đức); Keurig US$1,5 triệu; GSAM US$4 triệu; Invesco US$17,5 triệu.
  - Châu Âu và Anh: Katjes (BGH, 27/06/2024); HSBC (ASA, 19/10/2022); Shell 2025 không vi phạm (68% dầu khí, 23% các-bon thấp); Shein €1 triệu.
  - Úc: Mercer, Vanguard, Active Super A$11,3 / 12,9 / 10,5 triệu; Fiducian A$7,3 triệu.
  - Bối cảnh: SEC ngừng bảo vệ quy định công bố khí hậu (27/03/2025); ASIC 2023–2024 có 37 công bố đính chính và 8 thông báo phạt; Eni được hủy phạt (2024); CMA đóng hồ sơ Unilever (2024).
- **9 bài học:**
  1. Bằng chứng nằm ngay trong tài liệu của chính doanh nghiệp.
  2. Tuyên bố định lượng là mỏ bằng chứng tốt nhất.
  3. Tuyên bố phổ quát chỉ cần một phản ví dụ.
  4. Bỏ sót là lỗi phổ biến nhất; qualifier định lượng làm giảm rủi ro.
  5. "Trung hòa" nhờ bù trừ là nhóm rủi ro hàng đầu.
  6. Mục tiêu phải so với quỹ đạo thực.
  7. "Tái chế được", "phân hủy sinh học" phụ thuộc điều kiện thực.
  8. Kết cục pháp lý không một chiều.
  9. So cùng một tuyên bố qua các kỳ.
  - Trạng thái 06/10: có ở bài 1, 2, 8; một phần ở bài 4, 6, 7; chưa có ở bài 3, 5, 9.
- **Bộ hồi quy `data/real_cases/`:** KLM, BNY, DWS, Keurig, 4/4 khớp kết luận của cơ quan hoặc tòa. Mỗi vụ chỉ một tuyên bố: `VALIDATION_REPORT.txt` ghi 4 claims, 8 evidence.
- **Quy ước:** với doanh nghiệp Việt Nam chỉ nói "ca kiểm tra", "khoảng trống bằng chứng", "cần người soát xét".

### 1.3 `06_HAM_Y_CHO_GREENSCAN.md` (06/10)
- **Trước freeze 10/10:**
  - sửa registry NĐ 119/2025, 48/2026, 83/2026;
  - bootstrap theo doanh nghiệp;
  - quy ước gán nhãn;
  - bẫy hồi quy "cặp chỉ khác một con số";
  - không gửi tài liệu loại B/C lên cloud.
- **Cho Chung kết:** 10 tính năng xếp theo giá trị và công sức: cờ bù trừ, quy tắc TT 96 mục 6, so chéo kỳ, cờ "nghĩa vụ luật trình bày như thành tích", cờ danh hiệu, tìm phản ví dụ, so bản Anh–Việt, đo recall, bộ lọc mDeBERTa, nguồn đối chiếu ngoài.
- **Không nên làm:**
  - thêm GraphRAG, đa tác tử hay fine-tune chỉ để "AI hơn";
  - để mô hình tự quyết SUPPORTED/CONTRADICTED;
  - gọi kết quả là "tẩy xanh" hay xếp hạng doanh nghiệp;
  - dùng số [UNVERIFIED].
- **Đã làm tới đâu:** trong code tôi chỉ thấy bộ gợi ý sửa câu Studio (5 luật OC-01…05, ngày 14/10) có phần "trung hòa các-bon/net zero" (xem 1.13). Các tính năng khác [CHƯA XÁC MINH].

### 1.4 `GREENWASHING_TAXONOMY.md` (v0.1, 07/07)
- **Từ vựng kiểm soát:**
  - *green claim* hiểu rộng: cả hình ảnh, ngụ ý, nhãn, mục tiêu;
  - *greenwashing risk*: rủi ro tuyên bố gây hiểu nhầm, phóng đại, mơ hồ, thiếu chứng minh, công bố chọn lọc, bị bằng chứng bác, hoặc lệch tiêu chí pháp lý/phân loại.
- **Phân loại:**
  - 29 loại tuyên bố trong 6 nhóm: ENV 8, CLM 4, FIN 6, LEG 4, GOV 4, CSR 3.
  - 15 mã mẫu hình: VAGUE_CLAIM, NO_EVIDENCE, SELECTIVE_DISCLOSURE, QUANTITATIVE_CONTRADICTION, LEGAL_CONTRADICTION, FINANCIAL_GREENWASHING, EMPTY_FUTURE_COMMITMENT, SCOPE_SHIFTING, BASELINE_MANIPULATION, OFFSET_OVERRELIANCE, LABEL_CONFUSION, IMPLIED_CLAIM, COMPARATIVE_UNCLEAR, MATERIAL_OMISSION, CSR_DISTRACTION.
  - Trọng yếu 3 mức theo ngành; bằng chứng tối thiểu theo từng loại tuyên bố.
- **Quy tắc then chốt:**
  - thiếu bằng chứng → UNSUPPORTED hoặc INSUFFICIENT_EVIDENCE, **không** tự động CONTRADICTED;
  - CONTRADICTED chỉ khi có bằng chứng tin cậy mâu thuẫn;
  - trọng yếu cao + CONTRADICTED, hoặc điểm > 70 → người soát.
- **Giống và khác:** gần TerraChoice và ESAs, nhưng chi tiết hơn ở mảng tài chính (FIN_*), hợp với BGK tài chính. Bộ 21 mẫu ở 01 là bản sau, có thêm móc pháp lý Việt Nam.

### 1.5 `EVIDENCE_STANDARD.md`
- **SUPPORTED cần đủ 5 điều kiện:** liên quan, truy được nguồn, cùng kỳ, cùng ranh giới, đủ tin cậy.
- **Thang L1–L5:**
  - L1: độc lập, chính thức, pháp lý;
  - L2: công bố chính thức có kiểm toán;
  - L3: số liệu doanh nghiệp tự công bố, chưa đảm bảo;
  - L4: nguồn thứ cấp;
  - L5: marketing; không bao giờ tự chứng minh được tuyên bố trọng yếu.
- **Khi bằng chứng mâu thuẫn:** ưu tiên cấp cao hơn, rồi mới hơn, rồi phạm vi rõ hơn; giữ cả hai phía; không giải được thì INSUFFICIENT hoặc chuyển người. Ví dụ: "zero violations" gặp quyết định phạt cùng năm → CONTRADICTED.
- **Bắt buộc tìm bằng chứng trái chiều**, từ khóa cả Anh lẫn Việt ("xử phạt môi trường", "giấy phép môi trường"…).
- **Loại bỏ:** câu trả lời AI không có nguồn gốc; chứng nhận không ghi đơn vị cấp, phạm vi, ngày.

### 1.6 `AUDIT_PROTOCOL.md`
- **Chuỗi:** Claim → Evidence → Cross-check → Verdict → Risk score → Explanation → Review sign-off.
- **5 nguyên tắc:** hoài nghi nghề nghiệp, trọng yếu, đủ và thích hợp, truy vết, kết luận thận trọng.
- **Ngoài phạm vi:** **ý kiến pháp lý về gian lận hay trách nhiệm**; kiểm toán tài chính đầy đủ; chứng nhận doanh nghiệp "xanh".
- **17 bước; kiểm 5 lớp:** cụ thể → bằng chứng → nhất quán định lượng → phù hợp pháp lý/phân loại → mâu thuẫn bên ngoài.
- **Gộp cấp doanh nghiệp (đề xuất, chưa hiệu chỉnh):** 35% tuyên bố trọng yếu bị bác; 20% tài chính bền vững; 15% pháp lý/phân loại; 15% minh bạch; 10% khối lượng tuyên bố mơ hồ; 5% đảm bảo/quản trị.
- **Chuyển người soát khi:**
  - điểm ≥ 70, hoặc verdict CONTRADICTED;
  - trọng yếu cao mà bằng chứng yếu;
  - tuyên bố về trái phiếu/khoản vay xanh, phân loại xanh, tuân thủ, net zero;
  - OCR kém;
  - bằng chứng mâu thuẫn nhau;
  - không xác định được trang nguồn.

### 1.7 `MANUAL_SCORING_RUBRIC.md`
- **Điểm rủi ro 0–100 cho từng tuyên bố**, tài liệu ghi rõ "không phải kết luận pháp lý".
- **7 tiêu chí:** C1 mơ hồ 15 · C2 thiếu số 15 · C3 thiếu năm gốc/kỳ/phạm vi 10 · C4 bằng chứng yếu 20 · C5 thiếu đảm bảo độc lập 10 · C6 bằng chứng mâu thuẫn 20 · C7 trình bày phóng đại 10.
- **Mức:** 0–20 thấp; 21–40 vừa; 41–60 cao; 61–80 rất cao; 81–100 nghiêm trọng.
- **Điều chỉnh:** trọng yếu ±10; phụ điểm tài chính tối đa +52; phụ điểm net zero tối đa +56; trần 100.
- **Ví dụ 2 có lỗi số học** (xem mục 5): tuyên bố giảm phát thải trong khi bảng tăng từ 120.000 lên 145.000 tCO2e. Các thành phần cộng lại ra 30–38, nhưng tài liệu ghi 40–48 trước điều chỉnh trọng yếu.

### 1.8 `CLAIM_VERIFICATION_WORKING_PAPER.md`
- **Mẫu giấy làm việc cho một tuyên bố**, các phần nối tiếp:
  - A: bản ghi (giữ nguyên văn);
  - B: diễn giải ("nhà đầu tư hay người đọc hợp lý hiểu gì?");
  - C: yêu cầu bằng chứng;
  - D, E: bằng chứng ủng hộ, bằng chứng trái chiều;
  - F: chất lượng bằng chứng theo 6 chiều;
  - G: kiểm 5 lớp;
  - H: verdict;
  - I: điểm;
  - J: yêu cầu bổ sung;
  - K: kết luận;
  - L: soát xét lần hai;
  - cuối cùng: bản ghi JSON.
- **Mục B** là cầu nối với phép thử "người tiêu dùng hợp lý" và "ấn tượng tổng thể" trong án lệ (ASA, FTC, Lizama).

### 1.9 `REVIEWER_QA_CHECKLIST.md`
- **15 mục kiểm. Lỗi thường gặp:**
  - coi hoạt động CSR là hiệu quả cốt lõi;
  - coi tuyên bố về một sản phẩm là tuyên bố cấp doanh nghiệp;
  - **coi mục tiêu là thành tích**;
  - **coi nhãn tài chính là bằng chứng tác động**;
  - cho SUPPORTED chỉ dựa lời doanh nghiệp;
  - cho CONTRADICTED khi chỉ thiếu bằng chứng.
- **Kiểm đầu ra AI:** không nguồn bịa, không số trang bịa, không chuẩn pháp lý bịa, không trình bày suy luận LLM như bằng chứng.
- **Leo thang** khi điểm ≥ 80, hoặc hai người soát lệch nhau > 20 điểm.
- **Mục tiêu đồng thuận:** verdict ≥ 80%; lệch điểm ≤ 15 cho 75% số tuyên bố.

### 1.10 `AGENT_CRITERIA.md`
- **7 nguyên tắc:**
  - bằng chứng trước kết luận;
  - tách UNSUPPORTED, INSUFFICIENT và CONTRADICTED;
  - người soát cho rủi ro cao;
  - tách lớp dữ liệu, trích xuất, suy luận, điểm;
  - mọi thành phần thay được;
  - tính toán bằng công cụ tất định;
  - coi nội dung tài liệu là dữ liệu không tin cậy.
- **Thẻ điểm kỹ thuật** 100 điểm, 10 nhóm; **cổng** G0–G6.
- **Rubric mỗi lượt chạy** 21 điểm: đạt khi ≥ 16 và không mục nào 0; ca rủi ro cao cần ≥ 18 và người duyệt.

### 1.11 Lizama & Doten v. H&M Hennes & Mauritz LP (E.D. Mo., số 4:22-cv-01170, nộp 03/11/2022)
- **Loại vụ:** kiện tập thể của người tiêu dùng (nhóm toàn quốc, nhóm Missouri, nhóm California); giá trị > US$5 triệu theo CAFA.
- **Tuyên bố bị kiện** (¶29–34):
  - dòng "Conscious Choice" gắn thẻ treo màu xanh;
  - định nghĩa của chính H&M: mỗi sản phẩm chứa **ít nhất 50% vật liệu bền vững hơn**, như cotton hữu cơ hay polyester tái chế (riêng cotton tái chế chỉ cần ≥ 20%);
  - câu "our most environmentally sustainable products";
  - hình ảnh người mẫu giữa cỏ cây.
- **Cáo buộc:**
  - sản phẩm chủ yếu là polyester tái chế từ chai PET, tức "downcycling", "đường một chiều tới bãi rác hoặc lò đốt";
  - tranh nguyên liệu với tái chế chai-thành-chai; vẫn thải vi nhựa;
  - bộ Conscious có **72% sợi tổng hợp so với 61%** của bộ chính, **57% sản phẩm dùng polyester so với 52%** (dẫn Changing Markets Foundation 2021) (¶39–44);
  - người mua trả giá cao hơn (premium) (¶12, 57);
  - dẫn NYU Stern (dữ liệu 2013–2018): sản phẩm gắn nhãn bền vững bán nhanh hơn (¶49).
- **Căn cứ:**
  - FTC Green Guides 16 CFR §260.3–260.4 (¶24–27): không phóng đại; tuyên bố lợi ích môi trường chung chung khó chứng minh cho mọi cách hiểu; hai ví dụ "Eco-friendly" và máy in trong tổ chim cho thấy hình ảnh cũng là tuyên bố.
  - 11 Count: 5 Count theo luật Missouri MMPA (lừa dối; trình bày sai; che giấu hay bỏ sót sự thật trọng yếu; nửa sự thật; hành vi không công bằng); California UCL §17200, FAL §17500, CLRA §1750; làm giàu bất chính; trình bày sai do cẩu thả; gian lận.
  - Yêu cầu: công nhận nhóm, bồi thường hoặc hoàn trả, lệnh cấm, **chiến dịch quảng cáo đính chính**.
- **Kết cục** [NGOÀI, thứ cấp]: **bị bác ngày 12/05/2023** (Thẩm phán Rodney W. Sippel).
  - Với Lizama: không nêu được yêu cầu. H&M chưa từng nói sản phẩm "environmentally friendly"; cách hiểu hợp lý duy nhất là bộ này dùng vật liệu bền vững hơn bộ thường.
  - Với Doten: tòa Missouri không có thẩm quyền đối nhân (cư dân California, mua ở California).
  - Chưa thấy kháng cáo [CHƯA XÁC MINH].
- **Liên quan GreenScan:**
  1. Phải kiểm **đúng câu doanh nghiệp viết**, không kiểm câu diễn giải (QA mục 1; AUDIT_PROTOCOL §8 "không viết lại tuyên bố").
  2. Tuyên bố có **định nghĩa hay qualifier đi kèm** (≥ 50%) là tuyên bố so sánh có căn cứ, nên kết quả hợp lý là "khớp một phần, cần tỷ lệ vật liệu", không phải CONTRADICTED.
  3. Số 72% và 61% đến từ báo cáo NGO (cấp L4). Theo EVIDENCE_STANDARD, L4 chỉ dùng để tìm mâu thuẫn, không dựa vào một nguồn thứ cấp duy nhất.
  4. Cùng kiểu tuyên bố "vật liệu bền vững/tái chế", ASA Anh xử thua Nike (2025), Uniqlo và Adidas (2026), còn tòa Mỹ bác đơn kiện H&M. Kết luận phụ thuộc pháp quyền, phép thử và thủ tục.

### 1.12 `data/legal_cases/` (thu thập 08/08/2026, gộp 09/10)
- **Quy mô:**
  - 297 tài liệu: 117 hồ sơ phán quyết (giai đoạn 1) và 180 tài liệu doanh nghiệp (giai đoạn 2);
  - 288 hash nội dung khác nhau; 9 dòng trùng được đánh dấu, không xóa;
  - 29 mục tiêu, thu được 28; INT-CLOROX-AU bị chặn (HTTP 403);
  - cơ quan: ASA Anh, ASIC/Tòa Liên bang Úc, SEC.
- **`legal_strength`:**
  - **A** = tòa phạt (Mercer, Vanguard, Active Super);
  - **B** = SEC dàn xếp "không thừa nhận, không phủ nhận" (GSAM, Invesco, WisdomTree);
  - **C** = phán quyết ASA, hoặc thông báo phạt ASIC ("nộp phạt không phải thừa nhận lỗi").
- **Nhãn:** `greenwashing_label` = null trên mọi bản ghi. `qualifier` nhắc giới hạn phạm vi; ví dụ với Shell: "không phải phán quyết gian lận của tòa; chỉ gắn nhãn đúng quảng cáo/tuyên bố".
- **Tài liệu doanh nghiệp có sẵn để đối chiếu:** HSBC 25, Mercer 25, Repsol 25, TotalEnergies 24, Nike 23, Petronas 18, Uniqlo 13, Mazda 12, Invesco 7, WisdomTree 4, GSAM 2, Lufthansa 2.
- **Nhiễu:**
  - Thư mục Adidas có phán quyết 2022 và 2024 về gắn nhãn quảng cáo KOL, không phải môi trường.
  - Thư mục Shell có 24 file, phần lớn là trang điều hướng.
  - Thư mục Mercer chứa cả thông cáo về Active Super, Vanguard, Tlou…

**Thẻ vụ** (đã đọc phán quyết gốc trong thư mục; ngày theo phán quyết):

| Vụ | Cơ quan · ngày · kết quả | Tuyên bố | Lý do chính | Bài học → tiêu chí GreenScan |
|---|---|---|---|---|
| Shell UK 2023 | ASA G22-1170842 · 07/06/2023 · **upheld một phần** | Poster Bristol (20/06/2022): "BRISTOL is READY for Cleaner Energy" và "78.000 hộ dùng 100% điện tái tạo từ Shell Energy"; quảng cáo TV/YouTube "#PoweringProgress" | Vấn đề 1 (upheld): ấn tượng tổng thể là sản phẩm các-bon thấp chiếm tỷ trọng đáng kể của Shell, nên quảng cáo bỏ sót thông tin trọng yếu về tỷ trọng; phát thải năm 2021 ước 1.375 triệu tCO2e. Vấn đề 2 (not upheld): số 78.000 hộ có chứng minh, quảng cáo nói rõ điện cấp qua lưới quốc gia | Từng số đúng vẫn có thể gây hiểu nhầm → tiêu chí "tỷ trọng xanh trên tổng" (capex, doanh thu). Hiện chưa đo (01 §3, hàng "Trình bày") |
| Shell UK 2025 | ASA · 09/04/2025 · **not upheld** | TV (01/06/2024): sạc EV tới 2035, cung cấp > 20% khí đốt của Anh; chữ trên màn hình: "2023: 68% đầu tư toàn cầu cho dầu khí, 23% cho giải pháp các-bon thấp, 9% phi năng lượng" | Quảng cáo cho thấy rõ Shell làm cả hoạt động các-bon cao lẫn thấp, và có qualifier định lượng về tỷ trọng | Qualifier định lượng **đặt cạnh** tuyên bố → hạ ưu tiên soát. Dùng làm ca đối chứng "không vi phạm" để kiểm hệ thống biết hạ cờ |
| TotalEnergies | ASA A24-1246357 · 09/04/2025 · upheld | Bài X trả phí (21/05/2024) về chương trình tăng tốc start-up điện (NASH Renewables), ảnh turbine, dòng "THE ROADS TO CARBON NEUTRAL" | Bỏ sót tỷ trọng hoạt động các-bon thấp trong toàn bộ kinh doanh | Cùng ngày với Shell 2025 nhưng thiếu qualifier, nên kết quả ngược lại |
| HSBC UK | ASA G21-1127656 · 19/10/2022 · upheld | Poster (10/2021): "tới 1.000 tỷ USD tài trợ giúp khách hàng chuyển sang net zero"; "trồng 2 triệu cây, giữ 1,25 triệu tấn carbon" | Bỏ sót việc HSBC vẫn tài trợ đáng kể cho ngành phát thải cao | Với ngân hàng phải đối chiếu phát thải được tài trợ (financed emissions); GreenScan chưa có dữ liệu này |
| Repsol | ASA A23-1185942 · 07/06/2023 · upheld cả 2 vấn đề | Quảng cáo hiển thị (02/02/2023): "phát triển nhiên liệu sinh học và tổng hợp để đạt net zero"; logo cây xăng có chiếc lá | Bỏ sót thông tin trọng yếu; căn cứ tuyên bố không rõ vì không nói đây là một phần kế hoạch net zero 2050 | Net zero phải nói "bằng cách nào, khi nào" → checklist cam kết tương lai (mẫu 10) |
| Petronas | ASA A22-1169312 · 07/06/2023 · upheld | TV (9/2022), kể chuyện bằng giọng trẻ em, "điều tốt dần xảy ra" | Người xem không hiểu được mức đóng góp phát thải đáng kể đang tiếp diễn | Câu chuyện "chuyển đổi" thiếu thông tin cân bằng |
| Nike | ASA A25-1309100 · 03/12/2025 · upheld | Google ad (18/06/2025): "Nike Tennis Polo Shirts… Sustainable Materials" | "Bền vững" là từ tuyệt đối, bị hiểu là không gây hại suốt vòng đời. Áo có ≥ 75% vật liệu tái chế nhưng không chứng minh được cả vòng đời; ASA dẫn hướng dẫn ngành thời trang của CMA | Từ tuyệt đối cần chứng minh ở mức cao; sự thật một phần không cứu được tuyên bố tuyệt đối → cờ mơ hồ và gợi ý làm nhẹ (OC-04) |
| Uniqlo | ASA A26-1327727 · 24/06/2026 · upheld | Google ad (25/12/2025): "Fleece… Recycled Materials" | Không có qualifier nên bị hiểu là 100% tái chế; bằng chứng không cho thấy từng sản phẩm hoàn toàn tái chế | "% tái chế" cần tử số và mẫu số (như bài học Invesco) |
| Adidas | ASA · 24/06/2026 · upheld | Google ad (18/12/2025): "adidas Recycled Running Shoes" | Không có dòng giày tái chế riêng; không chứng minh được giày 100% tái chế | Như Uniqlo |
| Calvin Klein | ASA A26-1327724 · 24/06/2026 · upheld | "Responsibly sourced collections – Recycled, Organic & More" | Không rõ mức vật liệu tái chế hay hữu cơ trong từng sản phẩm | Như Uniqlo |
| Mercer | Tòa Liên bang Úc (ASIC 24-173MR) · 02/08/2024 · A$11,3 triệu | 7 lựa chọn đầu tư "Sustainable Plus" loại trừ hóa thạch, rượu, cờ bạc | Vẫn nắm 15 công ty hóa thạch (AGL, BHP, Glencore, Whitehaven), 15 công ty rượu, 19 công ty cờ bạc; Mercer thừa nhận | Tuyên bố loại trừ chỉ cần một phản ví dụ (bài học 3). GreenScan chưa có thủ tục này; cần danh mục nắm giữ |
| Vanguard | Tòa Liên bang Úc (ASIC 24-213MR) · 25/09/2024 · A$12,9 triệu (cao nhất lúc đó) | Quỹ trái phiếu "Ethically Conscious" có màn lọc ESG; tuyên bố trong 12 PDS, website, phỏng vấn | Khoảng 74% chứng khoán (theo giá trị thị trường) không được nghiên cứu hay sàng lọc | Đo tỷ lệ bao phủ theo giá trị |
| Active Super | Tòa Liên bang Úc (ASIC 25-042MR) · 18/03/2025 · A$10,5 triệu | Quỹ "đạo đức, có trách nhiệm" loại trừ hoặc hạn chế qua màn lọc ESG | Đầu tư vào chứng khoán đã nói là loại trừ, kéo dài khoảng 2,5 năm; thiếu hệ thống kiểm soát là trách nhiệm của quản lý cấp cao | Rủi ro ở quy trình; so cùng tuyên bố qua thời gian (bài học 9) |

**Các phán quyết ASA khác:**
- Upheld vì không rõ căn cứ hoặc thiếu bằng chứng vòng đời:
  - Unilever (Persil), 31/08/2022: "kinder to our planet";
  - Tesco (Plant Chef), 08/06/2022: thiếu bằng chứng vòng đời so với sản phẩm thịt.
- Upheld vì tuyên bố tuyệt đối không chứng minh được:
  - Etihad, 12/04/2023: "sustainable aviation";
  - Lufthansa, 01/03/2023: "PROTECTING ITS FUTURE";
  - Mazda, 25/09/2024: "sustainable" cho xe hybrid.
- Upheld vì bỏ sót thông tin quan trọng: Equinor, 20/12/2023.
- Kết quả hỗn hợp:
  - Oatly, 26/01/2022: 4 vấn đề upheld, 1 not upheld;
  - Lloyds, 18/12/2024: chỉ quảng cáo (d) upheld.
  → Phải gắn nhãn **từng tuyên bố**, không gắn nhãn cả vụ hay cả doanh nghiệp.

### 1.13 Đối chiếu phụ (code và kết quả đo)
- **`src/quantum_gw/studio/suggest.py` (14/10):** gợi ý sửa câu, gồm 4 loại: thêm phạm vi; chỗ trống "[bổ sung]"; dẫn chiếu bằng chứng; làm nhẹ lời nói quá.
- **5 luật làm nhẹ:**

| Luật | Cụm từ bắt | Gợi ý |
|---|---|---|
| OC-01 | "trung hòa các-bon", "net zero" | Tách phần giảm thực tế và phần bù trừ bằng tín chỉ |
| OC-02 | "100% xanh", "hoàn toàn xanh" | Thay bằng tuyên bố có chỉ số |
| OC-03 | "không phát thải" | Thêm mức so sánh và chỉ số |
| OC-04 | "thân thiện môi trường", "eco-friendly" | Thêm chỉ số và mức so sánh |
| OC-05 | "hàng đầu", "tiên phong", "xanh nhất", "số 1" | Cần căn cứ xếp hạng |

- **Chốt cứng `assert_no_new_numbers`:** gợi ý không được chứa con số mà câu gốc không có.
- **`KE_HOACH_…_2026-10-31.md` mục 2 và 10:** lỗi đã đo F1–F7 và số GS-Bench (xem mục 3 và 5).

## 2. Khái niệm và lý thuyết phải nắm

### 2.1 Định nghĩa học thuật (thuộc mỗi định nghĩa trong một câu)
| Tác giả | Định nghĩa, ý chính | Ứng với GreenScan | Nhãn |
|---|---|---|---|
| Delmas & Burbano 2011, *California Management Review* 54(1):64–87 | Tẩy xanh là **giao của hai hành vi: hiệu quả môi trường kém và truyền thông tích cực về hiệu quả môi trường**. Ma trận 2×2 (hiệu quả xanh/nâu × truyền thông lên tiếng/im lặng) cho 4 ô: *vocal green*, *silent green*, *greenwashing* (nâu nhưng lên tiếng), *silent brown*. Động lực chia 3 tầng: bên ngoài (thể chế và thị trường), tổ chức, cá nhân. Chi tiết từng tầng (NGO, người tiêu dùng, nhà đầu tư, đối thủ…) là [KIẾN THỨC NỀN] | GreenScan đo **khoảng cách giữa lời nói và bằng chứng đã công bố**, không đo hiệu quả thật. Ô *silent brown* không có tuyên bố nên GreenScan không thấy; chỉ thấy được khi có danh mục chỉ tiêu bắt buộc (TT 96 mục 6, chưa làm) | [NGOÀI]: định nghĩa và ma trận qua tóm tắt, nguồn thứ cấp 04/11; toàn văn chưa đọc |
| Lyon & Maxwell 2011, *JEMS* 20(1):3–41 | Tẩy xanh là **công bố chọn lọc** thông tin tích cực mà không công bố đầy đủ thông tin tiêu cực. Mô hình doanh nghiệp công bố dưới "đe dọa bị kiểm tra" (NGO audit) | Mẫu 6 (đánh đổi ẩn, công bố chọn lọc); HSBC, Shell 2023 (bỏ sót tỷ trọng) | [NGOÀI]: metadata; câu chữ chưa đối chiếu. Kết quả mô hình "áp lực có thể làm doanh nghiệp công bố ít đi" là [KIẾN THỨC NỀN] |
| Lyon & Montgomery 2015, *Organization & Environment* 28(2):223–249 | Truyền thông khiến người ta hình thành **niềm tin quá tích cực** về thực hành hoặc sản phẩm môi trường của tổ chức; là **thuật ngữ ô** | Giải thích vì sao đo theo **mẫu hình**, không theo một định nghĩa hẹp | [NGOÀI]: abstract đã kiểm theo file sources |
| Marquis, Toffel & Zhou 2016, *Organization Science* 27(2) | Doanh nghiệp "công bố chọn lọc các tác động tương đối lành tính, tạo ấn tượng minh bạch nhưng che hiệu quả thật"; mẫu 4.750 công ty ở 45 nước | Lý do phải kiểm **danh mục chỉ tiêu bắt buộc** và chủ động tìm bằng chứng trái chiều | [NGOÀI], theo 01 §1 |
| Seele & Gatti 2017, *BSE* 26(2) | Tẩy xanh là **cáo buộc từ bên ngoài**. 4 loại: greenwashing (gây hiểu nhầm và bị cáo buộc), false greenwashing (bị cáo buộc oan), potential greenwashing (gây hiểu nhầm nhưng chưa bị cáo buộc), no greenwashing | GreenScan đứng **trước** cáo buộc: chỉ tạo tín hiệu rủi ro "tiềm năng" kèm bằng chứng, và giảm cáo buộc oan bằng cổng "0 vu oan" | [NGOÀI], theo file sources R139 |
| Kim & Lyon 2015; Font và cs. 2017 | *Brownwashing* là khiêm tốn quá mức; *greenhushing* là cố ý im lặng | Mẫu 20: GreenScan không quy là tẩy xanh, chỉ báo "thiếu thông tin" | [NGOÀI]: metadata |
| TerraChoice | 7 tội: Đánh đổi ẩn · Không chứng minh · Mơ hồ · Tôn thờ nhãn giả · Không liên quan · Cái ác nhỏ hơn · Nói dối. Bản 2007 có 6 tội; bản 2009 thêm "nhãn giả" | Ánh xạ ở bảng 2.3 | Định nghĩa: [NGOÀI]. Số 2009 (2.219 sản phẩm Bắc Mỹ, > 98% phạm ít nhất 1 tội, 25 sản phẩm không phạm tội nào): [NGOÀI, thứ cấp]. Số 2007 và 2010: [CHƯA XÁC MINH] |

### 2.2 Định nghĩa của cơ quan quản lý (dùng khi BGK hỏi "theo luật")
- **ESAs 2024:** tuyên bố không phản ánh rõ ràng, công bằng hồ sơ bền vững; **cố ý hoặc vô ý**. Vì vậy không cần chứng minh ý định mới gọi là rủi ro.
- **ECGT 2024/825** (áp dụng 27/09/2026):
  - cấm tuyên bố môi trường chung chung khi không chứng minh được hiệu quả xuất sắc;
  - cấm tuyên bố sản phẩm "trung hòa" dựa trên bù trừ;
  - tuyên bố về tương lai cần kế hoạch có mốc và kiểm tra độc lập;
  - không ràng buộc tại Việt Nam; báo cáo cho nhà đầu tư thường ngoài phạm vi.
- **CMA Green Claims Code (2021):** trung thực và chính xác; rõ ràng; không bỏ sót; so sánh công bằng; xét cả vòng đời; có chứng minh.
- **FTC Green Guides (16 CFR 260):**
  - nguyên tắc chung (§260.3); không đưa tuyên bố lợi ích môi trường chung chung thiếu qualifier (§260.4); cần "reasonable basis".
  - Đây là **hướng dẫn**. FTC thực thi qua luật cấm hành vi lừa dối (Section 5 FTC Act) [KIẾN THỨC NỀN]; tư nhân kiện qua luật bang, như vụ Lizama.
- **Việt Nam:** không có định nghĩa. Móc pháp lý theo từng nghĩa vụ cụ thể [NGOÀI theo 01 §1–2; registry chờ Thảo xác nhận]:
  - Luật BVMT 2020 Đ.145: sản phẩm "thân thiện môi trường" phải được chứng nhận;
  - Luật Quảng cáo Đ.8.10–8.11: so sánh hay "nhất" cần tài liệu chứng minh;
  - Luật BVQLNTD 19/2023 Đ.10.1(a);
  - TT 96/2020 Phụ lục IV mục 6: chỉ tiêu môi trường của công ty đại chúng;
  - NĐ 06/2022 (sửa bởi 119/2025) Đ.19: bù trừ ≤ 30% hạn ngạch; tín chỉ đã dùng cho giảm phát thải tự nguyện không được giao dịch tiếp.

### 2.3 Ánh xạ 7 tội TerraChoice → mẫu hình 01 → GreenScan (theo 01, ngày 06/10)
| Tội | Mẫu 01 | Máy kiểm được? | GreenScan | Ghi chú |
|---|---|---|---|---|
| Không chứng minh | 2 | Một phần | Có: 5 thuộc tính (chỉ số, số liệu, kỳ, năm gốc, phạm vi), ra UNSUPPORTED hoặc INSUFFICIENT | Thế mạnh |
| Mơ hồ | 1 | Một phần | Một phần: từ điển `vague_terms` (scorer cộng 8 điểm khi khớp); Studio OC-04 gợi ý làm nhẹ | Không đánh giá được "ấn tượng tổng thể" |
| Nói dối | 7 | Một phần (nội bộ thì có) | Có thủ tục so số tất định, **nhưng đường chỉ dùng luật bắt được 0/44 ca mâu thuẫn** trên GS-Bench B-b (31/10) | Phải có bộ đọc IR đi kèm (mục 3) |
| Tôn thờ nhãn giả | 8 | Một phần | Một phần: chứng nhận chỉ có tài liệu doanh nghiệp thì chưa đủ bằng chứng; chưa tra danh mục Nhãn sinh thái | Cần nguồn ngoài |
| Đánh đổi ẩn | 6 | Một phần | Một phần: ghi phạm vi không soát; chưa đối chiếu TT 96 mục 6 | Shell 2023 và HSBC thuộc nhóm này |
| Không liên quan | 3 | Một phần | Chưa | Ví dụ "không chứa CFC" (đã bị cấm chung) |
| Cái ác nhỏ hơn | 5 | Một phần | Chưa | "Thép xanh", "than sạch" chỉ dựa cường độ phát thải |

- **Ngoài 7 tội**, GreenScan làm tốt nhất mẫu 12 (mốc so sánh) và 13 (lệch phạm vi): kiểu lỗi máy làm tốt hơn người.
- **Không làm được bằng văn bản:** mẫu 16 (hình ảnh), mẫu 20 (im lặng trong một kỳ), mẫu 21 (che giấu vi phạm, cần dữ liệu xử phạt).

### 2.4 Rủi ro tẩy xanh khác kết luận vi phạm
| | Rủi ro tẩy xanh (GreenScan) | Kết luận vi phạm (cơ quan, tòa) |
|---|---|---|
| Ai đưa ra | Công cụ, rồi người soát | Cơ quan có thẩm quyền (ASA, ASIC và tòa, SEC, AGCM…) |
| Đơn vị xét | Một tuyên bố cùng bằng chứng đi kèm | Một quảng cáo, tuyên bố hay hành vi cụ thể, trong một pháp quyền |
| Phép thử | Đủ hay thiếu bằng chứng theo 5 thuộc tính, cấp L1–L5, so số tất định | "Ấn tượng tổng thể", "người tiêu dùng/nhà đầu tư hợp lý", trọng yếu; gian lận còn cần ý định |
| Dữ liệu | Chỉ tài liệu đã công bố, cộng nguồn ngoài nếu có | Có quyền buộc cung cấp dữ liệu nội bộ (danh mục nắm giữ của Mercer, độ phủ sàng lọc của Vanguard) |
| Thủ tục | Doanh nghiệp không có phần phản biện | Doanh nghiệp được trả lời; có thể kháng cáo hoặc được hủy (Eni 2024) |
| Đầu ra | 5 trạng thái, điểm 0–100 "không phải kết luận pháp lý", khoảng trống, người soát | Upheld/not upheld; phạt; dàn xếp không thừa nhận; bác đơn (Lizama) |

- **Thang sức mạnh pháp lý ngay trong kho dữ liệu:** C (ASA; thông báo phạt ASIC "không phải thừa nhận") < B (SEC dàn xếp không thừa nhận, không phủ nhận) < A (tòa phạt).
- **Ba lý do độc lập để không dùng chữ "tẩy xanh":**
  1. ESAs: vô ý cũng tính, nên công cụ không nói được ý định.
  2. Seele & Gatti: tẩy xanh là một cáo buộc.
  3. Luật Việt Nam không định nghĩa thuật ngữ này.
  - Thêm: kết cục pháp lý không một chiều (Shell 2025, Lizama, Eni, CMA–Unilever).
- **Câu chốt:** "GreenScan trả lời *tuyên bố này có đủ bằng chứng không, thiếu gì*. Còn *có vi phạm không* là việc của cơ quan có thẩm quyền."

### 2.5 Khái niệm kiểm toán và bằng chứng dùng trong hệ thống
- **Hoài nghi nghề nghiệp; bằng chứng đủ và thích hợp:** gốc ISA 500 [KIẾN THỨC NỀN]. Cơ sở dẫn liệu ISA 315 (chính xác, đầy đủ, đúng kỳ, phân loại, trình bày) ánh xạ sang 5 thuộc tính (01 §3).
- **Đảm bảo hạn chế và đảm bảo hợp lý:** hạn chế cho kết luận dạng phủ định, hợp lý cho kết luận dạng khẳng định; chuẩn ISAE 3000/3410 [KIẾN THỨC NỀN]. Tương ứng tiêu chí C5 của rubric.
- **5 trạng thái:** SUPPORTED · PARTIALLY_SUPPORTED · UNSUPPORTED · CONTRADICTED · INSUFFICIENT_EVIDENCE. Quy tắc vàng: **vắng bằng chứng không phải là bằng chứng trái chiều**.
- **Tuyệt đối và tương đối:** ASA đòi "mức chứng minh cao" cho tuyên bố tuyệt đối (Nike, Uniqlo, Adidas, Etihad, Lufthansa, Mazda). Vụ Eni: tuyên bố tương đối được dùng nếu có tài liệu.
- **Qualifier:** phải rõ, nổi bật và **đặt cạnh** tuyên bố. FTC gọi là "clear and prominent"; BGH (Katjes) đòi giải thích ngay trong quảng cáo; Shell 2025 đặt sẵn tỷ lệ 68/23/9.
- **Tuyên bố phổ quát hay loại trừ** ("mọi", "100%", "loại trừ"): một phản ví dụ là đủ bác (Mercer, Vanguard, Active Super).
- **Giảm thực tế khác bù trừ:** Katjes, KLM; ECGT; NĐ 06 Đ.19.
- **Công thức điểm rubric:**
  - Điểm = min(100, max(0, C1 + … + C7 + điều chỉnh trọng yếu [−10, +10] + phụ điểm tài chính hoặc net zero)).
  - Mức đọc theo các dải cắt ở 20, 40, 60, 80.
  - Gộp cấp doanh nghiệp 35/20/15/15/10/5 chỉ là đề xuất v0.1, không dùng (xem mục 5).

## 3. Số liệu và dữ kiện được phép nói

**Định nghĩa và pháp lý**
- Định nghĩa tẩy xanh của ESAs (04/06/2024), gồm cả cố ý và vô ý · `docs/08-knowledge/01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md` §1 · [NGOÀI]
- ECGT (EU) 2024/825 áp dụng từ 27/09/2026; báo cáo cho nhà đầu tư thường ngoài phạm vi (Q&A Q1) · 01 §1 · [NGOÀI]
- Luật Việt Nam không định nghĩa "tẩy xanh" trong 14 văn bản đã đọc toàn văn · 01 §1 · [NGOÀI, phủ định có giới hạn]
- Chưa tìm thấy vụ nào cơ quan Việt Nam xử phạt vì tuyên bố môi trường gây hiểu nhầm · `docs/08-knowledge/04_AN_LE_VA_BAI_HOC.md` §1 · [NGOÀI, phủ định có giới hạn, UNVERIFIED]
- NĐ 06/2022 (sửa bởi 119/2025) Đ.19: bù trừ ≤ 30% hạn ngạch; tín chỉ đã dùng cho giảm tự nguyện không được giao dịch tiếp · 01 §2, mẫu 9 · [NGOÀI, registry chờ người xác nhận]

**Học thuật**
- Delmas & Burbano 2011: hiệu quả kém cộng truyền thông tích cực; ma trận 4 ô · ioes.ucla.edu (tóm tắt) · [NGOÀI, thứ cấp]
- Lyon & Montgomery 2015: "overly positive beliefs", thuật ngữ ô · `docs/08-knowledge/sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md` dòng 446 · [NGOÀI]
- Marquis và cs. 2016: 4.750 công ty, 45 nước · 01 §1 · [NGOÀI]
- Seele & Gatti 2017: định nghĩa dựa trên cáo buộc, 4 loại · file sources dòng 450 · [NGOÀI]
- TerraChoice 2009: 2.219 sản phẩm Bắc Mỹ, > 98% phạm ít nhất 1 tội, 25 sản phẩm không phạm · packagingdigest.com · [NGOÀI, thứ cấp]

**Án lệ** (đọc phán quyết gốc trong `data/legal_cases/`)
- Shell UK: ASA 07/06/2023 upheld một phần (bỏ sót tỷ trọng các-bon thấp; phát thải 2021 ước 1.375 triệu tCO2e theo báo cáo bền vững của Shell) · `data/legal_cases/INT-SHELL-UK/authority/29ff029ff5280625.html` · [NGOÀI]
- Shell UK: ASA 09/04/2025 not upheld nhờ qualifier về đầu tư 2023: 68% dầu khí, 23% các-bon thấp, 9% phi năng lượng · `data/legal_cases/INT-SHELL-UK/authority/87646f7f55295cbe.html` · [NGOÀI]
- TotalEnergies: ASA 09/04/2025 upheld (bỏ sót tỷ trọng) · `data/legal_cases/INT-TOTALENERGIES-FR/authority/d2f39d48a6721969.html` · [NGOÀI]
- TotalEnergies: Tòa Paris (23/10/2025) kết luận tuyên bố "trung hòa các-bon 2050" gây hiểu lầm · file sources, R110 · [NGOÀI, thứ cấp]
- HSBC UK: ASA 19/10/2022 upheld; "tới 1.000 tỷ USD", "2 triệu cây, 1,25 triệu tấn carbon" · `data/legal_cases/INT-HSBC-UK/authority/fccbe5fe959dc13c.html` · [NGOÀI]
- Repsol, Petronas: ASA 07/06/2023 upheld · `data/legal_cases/INT-REPSOL-ES/authority/c73e39918b45705e.html`; `data/legal_cases/INT-PETRONAS-MY/authority/386d84ae4560f32b.html` · [NGOÀI]
- Nike: ASA 03/12/2025 upheld; áo có ≥ 75% vật liệu tái chế vẫn thua vì "sustainable" là từ tuyệt đối · `data/legal_cases/INT-NIKE-UK/authority/75642360c681c310.html` · [NGOÀI]
- Uniqlo, Adidas, Calvin Klein: ASA 24/06/2026 upheld · `data/legal_cases/INT-UNIQLO-UK/authority/205038c83eaee38f.html`; `data/legal_cases/INT-ADIDAS-UK/authority/eeadbd94141df50c.html`; `data/legal_cases/INT-CALVIN-KLEIN-UK/authority/85eb7b4ff636cf88.html` · [NGOÀI]
- Mercer A$11,3 triệu (02/08/2024): còn nắm 15 công ty hóa thạch, 15 rượu, 19 cờ bạc · `data/legal_cases/INT-MERCER-AU/authority/ab639a4fce1e9bdb.html` · [NGOÀI]
- Vanguard A$12,9 triệu (25/09/2024): khoảng 74% chứng khoán theo giá trị không được sàng lọc · `data/legal_cases/INT-VANGUARD-AU/authority/e40166544336f10b.html` · [NGOÀI]
- Active Super A$10,5 triệu (18/03/2025); vi phạm kéo dài khoảng 2,5 năm · `data/legal_cases/INT-ACTIVE-SUPER-AU/authority/c27dc5b7aa91a27f.html` · [NGOÀI]
- KLM: 15/19 phát ngôn gây hiểu lầm, SAF khoảng 0,5% (Tòa Amsterdam, 20/03/2024) · 04 §2 · [NGOÀI]
- Lizama v. H&M: nộp 03/11/2022; 11 Count; H&M định nghĩa "≥ 50% vật liệu bền vững hơn"; nguyên đơn dẫn tỷ lệ sợi tổng hợp 72% so với 61% · đơn kiện ¶13, 29–34, 44 · [NGOÀI]
- Lizama bị bác ngày 12/05/2023 · kelleydrye.com, thefashionlaw.com · [NGOÀI, thứ cấp]
- ASIC 2023–2024: 37 công bố đính chính, 8 thông báo phạt; SEC ngừng bảo vệ quy định khí hậu ngày 27/03/2025 · 04 §2 · [NGOÀI]

**Kho dữ liệu của đội**
- `data/legal_cases/`: 297 tài liệu, 28/29 mục tiêu, 3 cơ quan, `greenwashing_label` null toàn bộ · `data/legal_cases/MERGE_MANIFEST.json`; `data/legal_cases/reports/COLLECTION_REPORT_2026-08-08.md` · [ĐÃ THỰC NGHIỆM, thu thập]
- `data/real_cases/`: 4 vụ có phán quyết (KLM, BNY, DWS, Keurig) và 2 đối chứng Việt Nam (HPG, BVH); 4 tuyên bố, 8 bằng chứng; 4/4 khớp kết luận (06/10) · `data/real_cases/VALIDATION_REPORT.txt`; 04 §3 · [ĐÃ THỰC NGHIỆM, n = 4]

**Kết quả hệ thống** (31/10–01/11; nhãn Claude là **nhãn bạc**)
- HPG, lượt 22/10: 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT trên 156 tuyên bố; hàng đợi 9/172 · `KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` mục 2 (F1) · [ĐÃ THỰC NGHIỆM]
- Lớp pháp lý áp được 0 quy tắc trên 156/156 tuyên bố; bằng chứng chỉ có nguồn nội bộ · mục 2 (F5, F6) · [ĐÃ THỰC NGHIỆM]
- 0 nhãn người (0/88 cặp, 0/79 câu) · mục 2 (F7) · [ĐÃ THỰC NGHIỆM]
- GS-Bench v1.1: 453 ca (51 ca dựng, 402 ca từ số liệu thật; S 95 / C 123 / N 184) · mục 10 (31/10 14:15) · [ĐÃ THỰC NGHIỆM]
- Đường chỉ dùng luật trên B-b: độ phủ 0,028 (4/142), precision 0,75, bắt được 0/44 ca mâu thuẫn · mục 10 (31/10) · [ĐÃ THỰC NGHIỆM]
- Tập ngoài mẫu sạch v1.3 (87 ca), mọi model precision 1,0 và 0 kết luận sai · mục 10 (01/11 17:00) · [ĐÃ THỰC NGHIỆM, nhãn bạc, n nhỏ]. Độ phủ:

| Luật | 4B | 8B | 14B | 32B |
|---|---|---|---|---|
| 0,011 | 0,138 | 0,115 | 0,115 | 0,253 |

- Chính sách "luật + 4B, bỏ phiếu SUPPORTED đơn độc của luật" · mục 10 · [ĐÃ THỰC NGHIỆM]
  - trên tập G: độ phủ 0,093, precision 1,0, 0 SUPPORTED sai, 0 CONTRADICTED sai;
  - với bộ đọc Q4 chạy cục bộ: 0 kết luận sai, độ phủ 0,080.
- HPG ngày 17/09 có 357/419 CONTRADICTED sai, sau sửa còn 0; 17 bẫy hồi quy ở `tests/test_verdict_traps.py`; LLM bị chốt `decisive=false` · `docs/00-project/AUDIT_HE_THONG_2026-10.md` dòng 74 · [ĐÃ THỰC NGHIỆM]
- Studio có 5 luật làm nhẹ OC-01…05 và chốt chặn số mới `assert_no_new_numbers` · `src/quantum_gw/studio/suggest.py` dòng 39–101 · [ĐÃ THỰC NGHIỆM: có code; hiệu quả với người dùng chưa đo]

**Giả thuyết** (chỉ nói khi kèm chữ "giả thuyết")
- Nếu cùng báo cáo có số capex xanh và capex tổng, tiêu chí "tỷ trọng" kiểu Shell 2023 có thể tính tất định · [GIẢ THUYẾT]
- Bộ phát hiện qualifier (kiểu Shell 2025) sẽ giảm cờ sai với doanh nghiệp công bố cân bằng · [GIẢ THUYẾT]

## 4. Câu hỏi BGK dự kiến

*Mỗi câu trả lời đi theo: vấn đề → nguyên lý → GreenScan làm gì → giới hạn. Đọc khoảng 30–60 giây.*

**Q1. Các bạn định nghĩa tẩy xanh thế nào, theo ai?**
- **Trả lời:**
  - Vấn đề: không có một định nghĩa duy nhất, và luật Việt Nam chưa định nghĩa (14 văn bản đã đọc).
  - Nguyên lý: học thuật có ba lớp. Delmas & Burbano: hiệu quả kém nhưng truyền thông tích cực. Lyon & Maxwell: công bố chọn lọc. Lyon & Montgomery: mọi truyền thông khiến người ta tin quá tích cực. ESAs 2024 tính cả cố ý lẫn vô ý.
  - GreenScan: không phán "tẩy xanh". Hệ thống đo khoảng cách giữa tuyên bố và bằng chứng đã công bố theo 21 mẫu hình, báo 5 trạng thái.
  - Giới hạn: không đo hiệu quả môi trường thực, chỉ đo những gì doanh nghiệp công bố và nguồn đối chiếu có được.
- **Vặn:** "Vậy hệ thống không phát hiện tẩy xanh à?" → "Hệ thống phát hiện tín hiệu rủi ro và khoảng trống bằng chứng ở cấp tuyên bố. Theo Seele & Gatti, 'tẩy xanh' là một cáo buộc, phải do chủ thể có thẩm quyền đưa ra."
- **Bẫy:** đọc thuộc định nghĩa dài; nói "theo luật Việt Nam, tẩy xanh là…".

**Q2. Không kết luận vi phạm thì công cụ giúp gì cho cơ quan quản lý hay nhà đầu tư?**
- **Trả lời:**
  - Vấn đề: cơ quan và kiểm toán viên không đủ người đọc hàng trăm trang cho hàng trăm doanh nghiệp.
  - Nguyên lý: sàng lọc rủi ro khác phán quyết. Chính cơ quan cũng ra kết quả hỗn hợp: Shell 2023 upheld một phần, Shell 2025 không vi phạm, Lizama bị bác, Eni được hủy phạt.
  - GreenScan: biến tài liệu thành hàng đợi tuyên bố xếp theo rủi ro. Mỗi dòng có trích trang, khoảng trống và câu hỏi gợi ý cho doanh nghiệp, giống giấy làm việc kiểm toán.
  - Giới hạn: người soát chịu trách nhiệm kết luận; chưa có nhãn người để đo độ chính xác.
- **Vặn:** "Điểm 0–100 có phải xác suất vi phạm?" → "Không. Rubric ghi rõ 'không phải kết luận pháp lý'. Đó là chỉ báo kiểu kiểm toán, chưa hiệu chỉnh trên nhãn người."
- **Bẫy:** nói "điểm 80 nghĩa là 80% khả năng tẩy xanh".

**Q3. TerraChoice có 7 tội. GreenScan bắt được tội nào?**
- **Trả lời** (dựa bảng 2.3):
  - Mạnh: "không chứng minh", và "nói dối" ở dạng mâu thuẫn số trong chính tài liệu; thêm mốc so sánh và lệch phạm vi.
  - Một phần: mơ hồ (từ điển), nhãn giả (chưa tra danh mục), đánh đổi ẩn.
  - Chưa làm: không liên quan, cái ác nhỏ hơn.
  - Giới hạn: số liệu của TerraChoice là về sản phẩm tiêu dùng Bắc Mỹ (2009: 2.219 sản phẩm, > 98% phạm ít nhất một tội), không phải báo cáo doanh nghiệp Việt Nam.
- **Vặn:** "Mâu thuẫn số liệu có làm tốt thật không?" → "Đường chỉ dùng luật bắt được 0/44 ca mâu thuẫn trên GS-Bench. Phải thêm bộ đọc số (LLM đọc, thư viện tất định so sánh) mới lên độ phủ 0,14–0,25, precision 1,0 trên tập ngoài mẫu 87 ca nhãn bạc. Chúng tôi chọn bỏ sót còn hơn vu oan."
- **Bẫy:** nói "phát hiện được cả 7 tội".

**Q4. Mẫu hình nào hệ thống không làm được, vì sao?**
- **Trả lời:**
  - Vấn đề: một số mẫu không nằm trong chữ của một tài liệu.
  - Nguyên lý: 01 chia ba nhóm mức kiểm được. Không làm được:
    - mẫu 16, hình ảnh: hệ thống chỉ đọc chữ, trong khi Petronas và Repsol dùng hình lá, giọng trẻ em;
    - mẫu 20, im lặng chọn lọc trong một kỳ;
    - mẫu 21, che giấu vi phạm: cần dữ liệu xử phạt;
    - mẫu 5, cái ác nhỏ hơn; mẫu 3, không liên quan.
  - GreenScan: ghi rõ "phạm vi không soát" trên thẻ bằng chứng. Hướng làm: so chéo kỳ, danh mục TT 96 mục 6, nguồn ngoài (danh mục Nhãn sinh thái, 110 cơ sở có hạn ngạch).
- **Vặn:** "Sao không dùng mô hình đọc ảnh?" → "Thể lệ ưu tiên chạy ổn định; ảnh trong báo cáo thường niên ít khi là tuyên bố đo được. Để sau."
- **Bẫy:** hứa "sắp có".

**Q5. Từng con số đều đúng mà vẫn gây hiểu nhầm, như Shell 2023. Hệ thống bắt được không?**
- **Trả lời:**
  - Vấn đề: ASA kết luận Shell bỏ sót thông tin trọng yếu. Quảng cáo năng lượng sạch tạo ấn tượng phần các-bon thấp là đáng kể, trong khi dầu khí chiếm phần lớn; số 78.000 hộ thì đúng.
  - Nguyên lý: phép thử "ấn tượng tổng thể" khác với kiểm từng con số.
  - GreenScan: hiện kiểm ở cấp tuyên bố, hàng "Trình bày" trong ánh xạ ISA 315 còn trống, và ghi rõ phạm vi không soát. Hướng làm: tiêu chí "tỷ trọng xanh trên tổng" (capex, doanh thu) khi cùng báo cáo có số; ngược lại, nhận diện qualifier định lượng như Shell 2025 (68/23/9) để hạ cờ.
  - Giới hạn: đây là phán đoán của người soát.
- **Vặn:** "Hai lần Shell khác nhau ở đâu?" → "Năm 2025 có câu tỷ trọng ngay trên màn hình. Cùng ngày đó, TotalEnergies thiếu câu này nên thua."
- **Bẫy:** nói "Shell vi phạm" mà không kèm năm.

**Q6. Doanh nghiệp tuyên bố "trung hòa carbon" nhờ mua tín chỉ thì xử lý sao?**
- **Trả lời:**
  - Vấn đề: đây là nhóm rủi ro hàng đầu trong án lệ: Katjes (BGH 2024, phải giải thích ngay trong quảng cáo), KLM, Delta.
  - Nguyên lý: giảm thực tế khác bù trừ. Từ 27/09/2026, ECGT cấm tuyên bố sản phẩm "trung hòa" dựa trên bù trừ. Ở Việt Nam, NĐ 06/2022 (sửa bởi 119/2025) Đ.19: bù trừ ≤ 30% hạn ngạch; tín chỉ đã dùng không được giao dịch tiếp.
  - GreenScan:
    - rubric net zero cộng điểm khi thiếu phạm vi, mốc trung gian, kế hoạch, hoặc không nêu phần dựa vào bù trừ;
    - Studio OC-01 gợi ý tách "phần giảm thực tế" và "phần bù trừ bằng tín chỉ";
    - mọi tuyên bố net zero phải qua người soát.
  - Giới hạn: lõi kiểm chứng chưa có cờ phát hiện riêng cho bù trừ (06 §3, việc 1); không kiểm được chất lượng tín chỉ (tính bổ sung, tính lâu dài).
- **Vặn:** "Tín chỉ giao dịch trên sàn HNX thì sao?" → "Cần dữ liệu của sàn; đã có trong danh sách nguồn ngoài."
- **Bẫy:** nói "đã có cờ bù trừ".

**Q7. Quỹ hay trái phiếu xanh ghi "loại trừ than". Kiểm thế nào?**
- **Trả lời:**
  - Vấn đề: Mercer (A$11,3 triệu; vẫn nắm 15 công ty hóa thạch, 15 rượu, 19 cờ bạc), Vanguard (A$12,9 triệu; khoảng 74% chứng khoán theo giá trị không được sàng lọc), Active Super (A$10,5 triệu).
  - Nguyên lý: tuyên bố phổ quát hay loại trừ chỉ cần một phản ví dụ là đủ bác; tuyên bố dạng % cần tử số, mẫu số và định nghĩa (bài học Invesco).
  - GreenScan: taxonomy có FIN_GREEN_BOND và FIN_USE_OF_PROCEEDS, cùng phụ điểm tài chính (thiếu danh mục dự án +8, thiếu báo cáo phân bổ +8…); bắt buộc qua người soát.
  - Giới hạn: chưa có thủ tục tìm phản ví dụ; cần danh mục nắm giữ. Cơ quan quản lý buộc doanh nghiệp nộp được dữ liệu này, còn chúng tôi chỉ dùng được nếu nó đã được công bố.
- **Vặn:** "Ngân hàng Việt Nam có trái phiếu xanh thì sao?" → nói theo khung TT 17/2022 và QĐ 21/2025 của lớp pháp lý; không nêu tên doanh nghiệp.
- **Bẫy:** gọi tên một ngân hàng Việt Nam cụ thể là "tẩy xanh".

**Q8. Việt Nam có án tẩy xanh chưa? Không có thì án nước ngoài áp được không?**
- **Trả lời:**
  - Vấn đề: chưa tìm thấy vụ nào xử phạt vì tuyên bố môi trường gây hiểu nhầm (phủ định có giới hạn). Formosa 2016 và Vedan 2008 là vụ ô nhiễm.
  - Nguyên lý: án nước ngoài không phải căn cứ pháp lý tại Việt Nam, nhưng cho **cách kiểm**, ví dụ mục tiêu phải so quỹ đạo thực, tuyên bố % phải có mẫu số. Căn cứ trong nước để móc: Luật BVMT Đ.145, Luật Quảng cáo Đ.8, Luật BVQLNTD Đ.10, TT 96 mục 6, NĐ 06 và 119.
  - GreenScan: registry pháp lý có phiên bản theo ngày hiệu lực; chỉ ghi "căn cứ ứng viên, chưa có người xác minh".
  - Giới hạn: lượt chạy 22/10, lớp pháp lý áp được 0/156 tuyên bố; ba quy tắc đang chờ người xác nhận.
- **Vặn:** "Vậy lớp pháp lý vô dụng?" → "Hiện nó dùng để tra cứu, chưa ra quyết định. Đó là thiết kế an toàn, không phải tính năng đã xong."
- **Bẫy:** nói "theo luật Việt Nam, doanh nghiệp này vi phạm".

**Q9. Vụ H&M ở Mỹ bị bác mà ASA lại xử Nike, Uniqlo. Hệ thống theo chuẩn nào?**
- **Trả lời:**
  - Vấn đề: cả hai đều là kiểu tuyên bố "vật liệu bền vững/tái chế".
    - Lizama: tòa Missouri bác đơn ngày 12/05/2023 vì H&M chưa từng nói "thân thiện môi trường" và đã định nghĩa rõ "≥ 50% vật liệu bền vững hơn". Nguyên đơn kiện một câu mà doanh nghiệp không viết.
    - ASA (2025–2026): "Sustainable Materials", "Recycled Materials" không có qualifier nên bị hiểu là tuyệt đối hoặc 100%, cần chứng minh ở mức cao. Nike có ≥ 75% vật liệu tái chế vẫn thua.
  - Nguyên lý: kết luận phụ thuộc pháp quyền, phép thử và thủ tục.
  - GreenScan: không chọn một pháp quyền để kết luận. Hệ thống dùng chuẩn bằng chứng chung (tuyên bố có định nghĩa, tử số, mẫu số, phạm vi không) và giữ nguyên văn câu.
  - Giới hạn: không nói thay tòa.
- **Vặn:** "Nếu chạy GreenScan trên H&M thì ra gì?" → "Giả thuyết: 'khớp một phần, cần tỷ lệ vật liệu từng sản phẩm', không phải CONTRADICTED. Chưa chạy thật." [GIẢ THUYẾT]
- **Bẫy:** nói "H&M thua kiện", hoặc "tòa Mỹ xác nhận H&M không tẩy xanh". Đơn bị bác ở giai đoạn xét đơn, tòa chưa xét đầy đủ nội dung sự thật.

**Q10. Thang điểm 7 tiêu chí lấy trọng số từ đâu, kiểm định chưa?**
- **Trả lời:**
  - Vấn đề: cần một điểm giải thích được.
  - Nguyên lý: C1–C7 lấy từ 5 lớp kiểm của quy trình kiểm toán (cụ thể, bằng chứng, nhất quán định lượng, pháp lý, mâu thuẫn bên ngoài) và từ CMA, FTC; mỗi tiêu chí lưu riêng, có lý do.
  - GreenScan: lõi là 5 trạng thái tất định; điểm chỉ dùng để xếp hàng đợi.
  - Giới hạn: trọng số là đề xuất của chuyên gia (v0.1); tài liệu tự ghi "cần hiệu chỉnh bằng ca có nhãn", và hiện chưa có nhãn người nào. Kiểm định dự kiến: hai người soát đồng thuận verdict ≥ 80%, lệch điểm ≤ 15 cho 75% số tuyên bố.
- **Vặn:** "Tuyên bố bị số liệu bác mà chỉ 40 điểm?" → Thừa nhận: trong rubric v0.1, C6 chỉ chiếm 20/100, nên một tuyên bố cụ thể mà bị bác có thể chỉ được 40–48 điểm (ví dụ 2). Vì vậy verdict CONTRADICTED tự động chuyển người soát bất kể điểm; đề xuất thêm sàn 65 điểm cho CONTRADICTED.
- **Bẫy:** bảo vệ trọng số như thể đã tối ưu.

**Q11. Phân biệt "không có bằng chứng" với "mâu thuẫn" thế nào? Doanh nghiệp im lặng (greenhushing) thì sao?**
- **Trả lời:**
  - Vấn đề: lỗi phổ biến là coi thiếu bằng chứng là sai.
  - Nguyên lý: vắng bằng chứng thì ra UNSUPPORTED hoặc INSUFFICIENT; CONTRADICTED chỉ khi có bằng chứng tin cậy mâu thuẫn (EVIDENCE_STANDARD §7). Đội đã trả giá cho bài học này: ngày 17/09, HPG có 357/419 CONTRADICTED sai; sau sửa còn 0, kèm 17 bẫy hồi quy.
  - Về im lặng: Lyon & Maxwell cảnh báo áp lực có thể khiến doanh nghiệp công bố ít đi. GreenScan không muốn thưởng cho im lặng; hướng làm là danh mục chỉ tiêu bắt buộc TT 96 mục 6 và so chéo kỳ.
  - Giới hạn: hai việc này chưa có.
- **Vặn:** "Doanh nghiệp sẽ công bố ít đi để tránh bị gắn cờ?" → "Đó là rủi ro thật (greenhushing). Vì vậy kế hoạch là báo thiếu chỉ tiêu bắt buộc, không chỉ chấm những câu đã viết."
- **Bẫy:** nói hệ thống đã phát hiện được im lặng.

**Q12. Bằng chứng do chính doanh nghiệp công bố thì tin được bao nhiêu?**
- **Trả lời:**
  - Vấn đề: theo thang L1–L5, ở Việt Nam phần lớn dữ liệu ESG chưa được đảm bảo (06 §2: 2/22 có đảm bảo), tức ở cấp L3. Lượt chạy 22/10 chỉ có nguồn nội bộ.
  - Nguyên lý: bài học 1 của án lệ là bằng chứng thường nằm trong chính tài liệu của doanh nghiệp (Keurig, KLM, Shein).
  - GreenScan: kiểm nhất quán nội bộ; chứng nhận chỉ có tài liệu doanh nghiệp thì chưa đủ bằng chứng; thẻ bằng chứng hiện cấp L.
  - Giới hạn: SUPPORTED dựa trên L3 chỉ dùng cho tuyên bố rủi ro thấp. Muốn kết luận mạnh cần L1: quyết định của cơ quan, giấy phép, báo cáo đảm bảo.
- **Vặn:** "Bản tiếng Anh và tiếng Việt lệch nhau thì sao?" → "TT 68/2024 yêu cầu hai bản thống nhất; hệ thống chưa so (mẫu 14 mới làm một phần)."
- **Bẫy:** nói báo cáo thường niên là "bằng chứng độc lập".

**Q13. Hệ thống báo sai làm doanh nghiệp mất uy tín thì ai chịu trách nhiệm?**
- **Trả lời:**
  - Vấn đề: sai một phía là bỏ sót, sai phía kia là vu oan, và vu oan nặng hơn vì kéo theo hậu quả pháp lý và uy tín.
  - Nguyên lý: Seele & Gatti gọi vu oan là "false greenwashing". Quy trình kiểm toán đòi kết luận thận trọng và người soát ký.
  - GreenScan:
    - cổng "0 vu oan": trên tập ngoài mẫu sạch 87 ca, mọi model precision 1,0 và 0 kết luận sai (nhãn bạc);
    - LLM không có quyền tự ra SUPPORTED hay CONTRADICTED;
    - CONTRADICTED, net zero, trái phiếu xanh đều chuyển người soát;
    - không công bố xếp hạng doanh nghiệp.
  - Giới hạn: độ phủ thấp (0,01–0,25), nhiều tuyên bố phải chuyển người; precision đo trên nhãn Claude, chưa có nhãn người.
- **Vặn:** "Độ phủ 0,1 thì có ích gì?" → "Các tuyên bố còn lại vẫn có thẻ bằng chứng và khoảng trống cho người soát. Hệ thống tiết kiệm phần đọc và tra, không thay phần phán."
- **Bẫy:** nói "chính xác 100%".

**Q14. Có bộ dữ liệu tẩy xanh chuẩn để đo không? Đã kiểm trên án thật chưa?**
- **Trả lời:**
  - Vấn đề: chưa có bộ dữ liệu tẩy xanh nào đã được xác minh (khảo sát NLP của Calamai và cs. 2025, theo paper của đội).
  - Nguyên lý: đo theo cấu trúc tuyên bố–bằng chứng–quan hệ, thay vì nhãn "tẩy xanh".
  - GreenScan có:
    - GS-Bench v1.1: 453 ca, nhãn bạc cộng bộ kiểm tất định;
    - bộ hồi quy 4 vụ có phán quyết (KLM, BNY, DWS, Keurig): 4/4 khớp, mỗi vụ một tuyên bố;
    - kho 297 tài liệu của 28 vụ ASA, ASIC, SEC, có mức sức mạnh pháp lý A/B/C, để mở rộng.
  - Giới hạn: kho án chưa gắn nhãn tuyên bố; chưa có nhãn người.
- **Vặn:** "4 vụ có ít quá không?" → "Đúng, đó là kiểm hồi quy, không phải đánh giá thống kê. Ứng viên tiếp theo: Shell 2025 (đối chứng không vi phạm), Katjes, Shein, Invesco."
- **Bẫy:** nói "đã kiểm trên 32 vụ án".

**Q15. Án lệ phần lớn về quảng cáo cho người tiêu dùng, còn GreenScan đọc báo cáo cho nhà đầu tư. Áp vào có lệch không?**
- **Trả lời:**
  - Vấn đề: đúng là ECGT ghi báo cáo cho nhà đầu tư thường ngoài phạm vi.
  - Nguyên lý: nhưng có nhóm án nhắm thẳng vào tài liệu cho nhà đầu tư: Keurig (SEC, báo cáo thường niên), Mercer và Vanguard (website, PDS), Invesco, DWS, GSAM; định nghĩa của ESAs cũng áp cho sản phẩm và dịch vụ tài chính. Thứ chuyển sang được là **thủ tục kiểm** (định lượng, mẫu số, phạm vi, bỏ sót), không phải kết luận.
  - GreenScan: ánh xạ nghĩa vụ Việt Nam theo loại tài liệu (TT 96 cho công bố thông tin; Luật Quảng cáo và Luật BVQLNTD cho quảng cáo).
  - Giới hạn: quảng cáo hình ảnh và "ấn tượng tổng thể" nằm ngoài phạm vi.
- **Vặn:** "Vậy dùng án ASA làm gì?" → "Để kiểm hành vi của các luật cứng: tuyệt đối hay tương đối, có qualifier không, tỷ trọng."
- **Bẫy:** trộn hai loại tài liệu làm một.

**Q16. Theo ma trận Delmas & Burbano, hệ thống nhận ra được 4 nhóm doanh nghiệp không?**
- **Trả lời:**
  - Vấn đề: ma trận xếp doanh nghiệp theo hiệu quả (xanh/nâu) và truyền thông (lên tiếng/im lặng).
  - GreenScan chỉ quan sát trục truyền thông cùng bằng chứng đã công bố, không đo hiệu quả thật. Nó phân biệt được tuyên bố "lên tiếng" có hay không có bằng chứng, nhưng không thấy hai ô im lặng vì không có tuyên bố để kiểm.
  - Nguyên lý: xếp doanh nghiệp vào một ô là phán xét cấp doanh nghiệp; chúng tôi dừng ở cấp tuyên bố.
  - Hướng làm: dùng nguồn ngoài (Climate TRACE, danh sách 110 cơ sở có hạn ngạch) để có trục hiệu quả, chỉ làm dữ liệu tham khảo.
- **Vặn:** "Ở Việt Nam, động lực tẩy xanh là gì?" → Theo khung Delmas & Burbano: quản lý còn lỏng và chưa chắc chắn; áp lực từ nhà đầu tư và xuất khẩu (CBAM); ít kiểm toán (2/22 có đảm bảo). Nói nhẹ, không phán xét.
- **Bẫy:** tuyên bố "đã xếp doanh nghiệp Việt Nam vào 4 ô".

**Q17. Sao không để LLM kết luận luôn cho nhanh?**
- **Trả lời:**
  - Vấn đề: LLM dễ sai ở con số. 11/11 kết luận sai của model 32B là do tự thêm bội số ("10.730 m3" thành "10.730 ngàn m3"); LLM cũng không từ chối khi thiếu ngữ cảnh.
  - Nguyên lý: Models read – Rules decide – Humans review; mọi phép tính chạy bằng công cụ tất định (AGENT_CRITERIA, cổng G3).
  - GreenScan: LLM chỉ đọc ra số, đơn vị, kỳ, phạm vi; `irlib.ground()` buộc số phải có trong câu gốc; thư viện so sánh tất định ra quyết định; người soát duyệt. Kết quả: precision 1,0 trên 87 ca ngoài mẫu sạch (nhãn bạc).
  - Giới hạn: độ phủ thấp; chưa có nhãn người.
- **Vặn:** "Dùng model lớn hơn thì sao?" → "32B có độ phủ 0,253, 4B có 0,138; sau ground cả hai đều 0 sai. Chúng tôi ưu tiên chạy cục bộ."
- **Bẫy:** nói "AI quyết định".

**Q18. Hệ thống có phân biệt cố ý hay vô ý không?**
- **Trả lời:**
  - Không, và không cần. Định nghĩa của ESAs đã gồm cả vô ý. Ý định (scienter) là yếu tố của gian lận, do tòa xác định; đơn kiện Lizama có riêng một Count "Fraud".
  - GreenScan đo hệ quả trên văn bản: câu có tạo ấn tượng vượt quá bằng chứng không.
  - Giới hạn: không suy diễn động cơ.
- **Vặn:** "Lặp lại qua nhiều năm có phải cố ý?" → "So chéo kỳ là một tín hiệu (Fiducian; Active Super kéo dài khoảng 2,5 năm), nhưng vẫn chỉ là tín hiệu để người soát đặt câu hỏi."
- **Bẫy:** dùng từ "gian lận".

**Q19. Doanh nghiệp đưa giải thưởng "Top 100 bền vững" làm bằng chứng thì sao?**
- **Trả lời:**
  - Vấn đề: đây là mẫu 18, gần với nhãn giả.
  - Nguyên lý: theo EVIDENCE_STANDARD, giải thưởng không có phương pháp là cấp L5, không chứng minh được tuyên bố trọng yếu. Taxonomy GOV_ESG_RATING đòi nêu nhà cung cấp, ngày, phương pháp. Luật Quảng cáo Đ.8.11: dùng chữ "nhất" phải có tài liệu hợp pháp chứng minh.
  - GreenScan: Studio OC-05 đòi căn cứ xếp hạng cho "hàng đầu/số 1".
  - Giới hạn: cờ "danh hiệu thay bằng chứng" chưa có (06 §3, việc 5).
- **Vặn:** "Giải thưởng của Bộ thì sao?" → "Nếu là quyết định chính thức thì là L1 cho sự kiện được trao giải, nhưng vẫn không phải bằng chứng cho từng con số."
- **Bẫy:** nói hệ thống "loại bỏ giải thưởng".

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

### 5.1 Mâu thuẫn và số đã cũ so với kết quả 31/10–01/11
1. **"Có thủ tục chạy thật" không có nghĩa là bắt tốt.**
   - 01 §2 ghi mẫu 7 (mâu thuẫn số) là có thủ tục chạy thật; 04 §3 ghi bài học 1 là đã làm.
   - Đo ngày 31/10: đường chỉ dùng luật bắt được 0/44 ca mâu thuẫn trên GS-Bench B-b; độ phủ của luật trên tập ngoài mẫu sạch chỉ 0,011.
   - Bảng PDF còn yếu: F3 (mọi model báo SUPPORTED sai ở N02, N05, trang 39 của HPG); AG-3 v0 dựng lại hàng chỉ đúng 3/7; tiêu đề trang 39 ghi "NĂM 2024" trong khi bảng ghi 2025.
   → Khi nói "so số tất định", phải kèm "sau bộ đọc IR" và con số độ phủ.
2. **Mẫu 9 (bù trừ):** 01 ghi "chưa có cờ"; 06 §3 xếp làm việc 1. Code Studio (14/10) đã có OC-01, nhưng đó là *gợi ý sửa câu*, không phải cờ rủi ro hay bước kiểm cơ chế bù trừ.
   → Chỉ nói "có gợi ý sửa câu". Lõi kiểm chứng đã có cờ hay chưa: [CHƯA XÁC MINH].
3. **Shell:** 04 dùng "Shell UK 2025" làm ca đối chứng "đạt" (đúng: ASA 09/04/2025 not upheld). Nhưng metadata `INT-SHELL-UK` lại gắn `case_id` G22-1170842 và năm 2023 (upheld một phần), trong khi thư mục chứa cả hai phán quyết.
   → Gắn nhãn ở cấp vụ sẽ trộn upheld với not upheld. Luôn trích theo ngày và kết quả.
4. **TotalEnergies có hai thủ tục khác nhau:** file sources dẫn Tòa Paris 23/10/2025 (nguồn thứ cấp); thư mục chỉ có phán quyết ASA 09/04/2025. Không được trộn.
5. **Cấp doanh nghiệp:** AUDIT_PROTOCOL (07/07) có bước 14 gộp điểm cấp doanh nghiệp (35/20/15/15/10/5) và §9 đòi "Company-level risk summary". Trái với 06 §4 ("không xếp hạng doanh nghiệp") và 04 §1 ("không kết luận doanh nghiệp").
   → Bộ domain-audit v0.1 cũ hơn quyết định sau 06/10. Không trình bày điểm cấp doanh nghiệp.
6. **MANUAL_SCORING_RUBRIC, ví dụ 2 sai số học và lệch chính tài liệu:**
   - Các thành phần (0 + 0 + 0–3 + 0 + 5–10 + 20 + 5) cộng ra 30–38, không phải 40–48 như tài liệu ghi.
   - "50–58 sau điều chỉnh trọng yếu" nằm dưới dải CONTRADICTED 65–100 (§6) và trái kỳ vọng "rất cao hoặc nghiêm trọng" ở QA §8.
   - Nguyên nhân gốc: thiết kế cộng dồn cho C6 chỉ 20/100.
   → Không chiếu ví dụ này. Nếu bị hỏi: CONTRADICTED tự chuyển người soát; đề xuất thêm sàn điểm.
7. **Ngưỡng người soát lệch nhau:** TAXONOMY §9 ghi "> 70"; AUDIT_PROTOCOL §7 ghi "≥ 70"; QA §12 leo thang ở "≥ 80".
   → Nói thống nhất: ≥ 70 chuyển người soát; ≥ 80 chuyển người soát cấp cao.
8. **Cấp bằng chứng của báo cáo doanh nghiệp:** EVIDENCE_STANDARD xếp "annual report, ESG report with methodology" vào L2 (độ tin cậy cao). Nhưng thực tế:
   - ở Việt Nam 2/22 báo cáo có đảm bảo;
   - quy ước A3 coi chứng nhận chỉ có tài liệu doanh nghiệp là chưa đủ;
   - lượt 22/10 có `has_independent: False`.
   → Phải tách phần đã kiểm toán (báo cáo tài chính, L2) với phần ESG chưa đảm bảo (L3).
9. **"4/4 khớp"** (04 §3) chỉ trên 4 tuyên bố (`VALIDATION_REPORT.txt`). Bốn ứng viên bổ sung (Katjes, Shein, Shell 2025, Invesco) chưa thấy trong `data/real_cases/`.
10. **Cột "GreenScan hôm nay" của 01 là trạng thái ngày 06/10.** Sau đó đã có Studio (14/10) và bộ đọc IR (31/10). Trên slide ngày 10/11, ghi "theo đối chiếu 06/10", không ghi "hôm nay".
11. **Nhiễu trong `data/legal_cases`:**
    - thư mục Adidas có 2 phán quyết không phải môi trường;
    - thư mục Mercer chứa thông cáo của vụ khác; heuristic chọn file của tôi đã lấy nhầm;
    - `greenwashing_label` null toàn bộ.
    → Nếu dùng làm tập truy xuất, phải lọc theo `case_id` và kiểm tay. Không gọi đây là tập có nhãn.
12. **Lizama** không có trong 04 lẫn `legal_cases`. Kết cục chỉ từ nguồn thứ cấp; chưa đọc văn bản lệnh bác.
13. **Delmas & Burbano:** file sources (dòng 444) ghi ma trận 4 ô là [UNVERIFIED]. Nay đã xác nhận qua tóm tắt và nguồn thứ cấp (04/11), nhưng vẫn chỉ nói "theo Delmas & Burbano (2011)", không trích nguyên văn câu.
14. **TerraChoice:** 01 ghi "VERIFIED định nghĩa"; các mốc 2007 và 2010 vẫn chưa xác minh. Riêng số 2009 nay có nguồn thứ cấp.
15. **"0 vu oan" chỉ đúng với phiên bản và tập cụ thể:**
    - v1.1: 4B, 14B, 32B trượt cổng `ag1_ir_path_usable`;
    - trước khi có `ground`, 32B có 7 CONTRADICTED sai;
    - "0 kết luận sai" là của v1.2 và tập sạch v1.3 (87 ca).
    → Không khái quát thành "hệ thống không bao giờ sai".
16. **Kết luận phẳng (F1):** 153/156 tuyên bố HPG là PARTIALLY_SUPPORTED. Nếu bị hỏi "hệ thống có phân biệt được không" thì nói thật, kèm nguyên nhân: không có nguồn độc lập để bác hay xác nhận (AUDIT_HE_THONG dòng 75).

### 5.2 Điều không được nói
- "GreenScan phát hiện hay kết luận tẩy xanh"; "doanh nghiệp X tẩy xanh hay vi phạm"; xếp hạng doanh nghiệp; điểm rủi ro cấp doanh nghiệp.
- "Theo luật Việt Nam, tẩy xanh là…" (luật không có định nghĩa).
- "Việt Nam đã có án tẩy xanh"; "Formosa, Vedan là án tẩy xanh".
- "Hệ thống đã kiểm chứng trên 28 hay 32 vụ án"; "kho án đã có nhãn".
- "Phát hiện được cả 7 tội hay cả 21 mẫu"; "đọc được hình ảnh".
- "Đã có cờ bù trừ carbon / tìm phản ví dụ / so chéo kỳ / danh mục TT 96" (chưa có, hoặc chưa xác minh).
- "Precision 100%" mà không nói kèm: nhãn bạc, 87 ca, độ phủ 0,01–0,25.
- "Lớp pháp lý tự động áp luật" (thực tế 0/156).
- "H&M thua kiện"; "tòa Mỹ xác nhận H&M không tẩy xanh".
- "Shell bị xử vi phạm" mà không kèm năm (2023 upheld một phần; 2025 not upheld).
- "FTC Green Guides là luật"; "ECGT áp dụng ở Việt Nam".
- Số TerraChoice 2007 và 2010; mức phạt trong các nghị định xử phạt của Việt Nam [UNVERIFIED].
- Nêu tên doanh nghiệp Việt Nam trong demo kèm chữ "vi phạm".
- "Điểm 0–100 là xác suất".
