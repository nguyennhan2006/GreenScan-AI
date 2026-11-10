# R9: Tra cứu web — hiện trạng chuẩn mực, luật 2025–2026 và lượng tử trong tài chính

*Soạn 04/11/2026 cho Chung kết 10/11/2026. Ký hiệu nguồn web: **(mở)** là đã mở trang bằng WebFetch; **(tìm)** là chỉ thấy qua tóm tắt kết quả tìm kiếm, chưa mở trang gốc, nên phải mở lại trước khi đưa lên slide. Đây là ghi chú định hướng, không phải tư vấn pháp lý.*

**Nguồn đã đọc**

*Tài liệu của đội (đọc theo đoạn):*
- `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`: toàn bộ (viết 05–06/10, ghi chú cập nhật 13/10).
- `docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`: chỉ các dòng 20, 41, 70–73, 96, 109 (qua Grep: QĐ 46/2026, NĐ 142/2026, dự thảo TT 96).
- `docs/07-presentation/QA_BANK_100_2026-09-20.md`: dòng 1–18 và Q83–Q90. `${TXT}/GreenScan_100_Cau_BGK.txt`: dòng 267–343 (Q83–Q100 và phụ lục "đừng nói").
- `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`: mục 0–2 và mục 10 (31/10; 01/11 17:00).
- `docs/00-project/DECISIONS_LOG.md` (D-2026-09-18-01, D-2026-09-18-06, D-2026-09-28-01, qua Grep); `docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md` (S13, dòng 197, 230–233); `docs/08-knowledge/04_AN_LE_VA_BAI_HOC.md` dòng 29.
- `${TXT}/the_le_cuoc_thi.txt`: dòng 172–186 (Nhóm 4), 270–282 (Điều 10), 636–644 (giải phụ).

*Kiểm mã ngày 04/11:* Grep `qubo|qaoa|simulated annealing` trong `src/` cho 0 tệp. Grep `qubo|qaoa|dimod|neal|qiskit|pennylane` trong `experiments/ tools/ benchmark/ training/ scripts/` cho 0 tệp. `.venv/Lib/site-packages` không có qiskit, pennylane, dimod, dwave, cirq.

*Web, đã mở:*
1. IFRS Foundation, "ISSB issues targeted amendments to IFRS S2", 11/12/2025: https://www.ifrs.org/news-and-events/news/2025/12/issb-issues-targeted-amendments-ifrs-s2/
2. IAASB, *ISSA 5000 and IESSA: Global Baseline Standards for Sustainability Assurance* (Fact Sheet, 01/2025): https://ifacweb.blob.core.windows.net/publicfiles/2025-01/IAASB-ISSA-5000-Sustainability-Assurance-Fact-Sheet.pdf. PDF bị mã hoá nên WebFetch không đọc được; đã trích bằng PyMuPDF ra `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\R9\issa5000_factsheet.txt` (4 trang).
3. Thời báo Tài chính Việt Nam, "Hoàn thiện quy định công bố thông tin, tăng minh bạch thị trường chứng khoán", 02/10/2026: https://thoibaotaichinhvietnam.vn/hoan-thien-quy-dinh-cong-bo-thong-tin-tang-minh-bach-thi-truong-chung-khoan-204774.html
4. Viet Nam News, "Ministry proposes expanding English disclosure rules for securities sector", 29/10/2026: https://vietnamnews.vn/economy/1803122/ministry-proposes-expanding-english-disclosure-rules-for-securities-sector.html
5. Mayer Brown, "The EU Directive on Empowering Consumers for the Green Transition two years on…", 27/10/2026: https://www.mayerbrown.com/en/insights/publications/2026/10/the-eu-directive-on-empowering-consumers-for-the-green-transition-two-years-on-what-it-requires-and-where-the-member-states-stand
6. VnEconomy, "Sẽ có quy định cụ thể về tiêu chí xanh, xác định dự án xanh, tuần hoàn, ESG", 03/04/2026: https://vneconomy.vn/se-co-quy-dinh-cu-the-ve-tieu-chi-xanh-xac-dinh-du-an-xanh-tuan-hoan-esg.htm
7. Thị trường Tài chính Tiền tệ, "10 nhóm và 30 sản phẩm công nghệ chiến lược từ ngày 1/7/2026", 06/05/2026: https://thitruongtaichinhtiente.vn/10-nhom-va-30-san-pham-cong-nghe-chien-luoc-tu-ngay-1-7-2026-82673.html
8. Farhi, Goldstone, Gutmann, "A Quantum Approximate Optimization Algorithm", arXiv:1411.4028, 14/11/2014: https://arxiv.org/abs/1411.4028

*Web, chỉ thấy qua tìm kiếm:*
- Úc: ASIC 24-173MR (Mercer) https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2024-releases/24-173mr-asic-s-first-greenwashing-case-results-in-landmark-113-million-penalty-for-mercer ; ASIC 25-254MR (Clime) https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2025-releases/25-254mr-asic-statement-clime-entities/ ; ACCC (Clorox) https://www.accc.gov.au/media-release/clorox-ordered-to-pay-825m-in-penalties-for-misleading-ocean-plastic-claims-about-certain-glad-products ; Vanguard và Active Super qua mallesons.com, gtlaw.com.au, investordaily.com.au.
- Anh: CMS, Slaughter and May, Ashurst (DMCC, 06/04/2025). EU: Latham & Watkins, Packaging Europe, CMS, Loyens & Loeff (Green Claims Directive); Jones Day, politis.com.cy (thủ tục vi phạm 2024/825). Mỹ: Kelley Drye, FKKS, Net Zero Compare (FTC Green Guides). ESMA: FMA Austria, Osborne Clarke, Morningstar.
- ISSB: S&P Global "ISSB Q3 2026" (27/08/2026) https://www.spglobal.com/sustainable1/en/insights/research-reports/issb-q3-2026 ; ICAEW (06/2025).
- Việt Nam: PwC VN news brief 15/09/2026 https://www.pwc.com/vn/vn/publications/news-brief/260915-decree-330-pdpl-violations.html ; VOV ("Từ 19/8/2026…"); hethongphapluat, luatvietnam (Luật 91/2025, TT 08/2026, QĐ 21/2025); apolatlegal, luatminhkhue, hethongphapluat (Luật 134/2025).
- Lượng tử: The Quantum Insider 25/09/2025, fi-desk, MIT Sloan ME (HSBC–IBM); Azure blog 27/06/2022 và The Quantum Insider 20/02/2023 (Toshiba SQBM+); Herman et al. 2023 (arXiv:2201.02773); Meichanetzidis et al. (arXiv:2012.03756); khảo sát QNLP 2025 (ACL, hội thảo QuantumNLP).

*Không đọc được hoặc không mở:* Crowe VN (HTTP 403), nên nội dung "IFRS S1/S2 nằm trong danh mục chuẩn mực 2026–2027" chỉ có từ tóm tắt tìm kiếm và để ở mức [CHƯA XÁC MINH]. Không mở bản gốc EUR-Lex 2024/825, cổng Bộ Tài chính/UBCKNN (dự thảo thay TT 96), Công báo (QĐ 46/2026, NĐ 330/2026, QĐ 21/2026), trang ESMA, FTC, CMA và thông cáo ASIC/ACCC, vì giới hạn khoảng 35 lượt tra web. Các dữ kiện đó ghi kèm nguồn thứ cấp.

---

## 1. Tóm tắt từng tài liệu

### A. Chuẩn mực đảm bảo và công bố bền vững

**1.1 IAASB — ISSA 5000, Fact Sheet (01/2025) (mở)**
- *Là gì:* chuẩn mực quốc tế đầu tiên về dịch vụ đảm bảo thông tin bền vững (*General Requirements for Sustainability Assurance Engagements*). Ban hành 11/2024; INCP ghi ngày 12/11/2024 (tìm).
- *Chính:*
  - Áp dụng cho mọi thông tin bền vững, kể cả KNK, lập theo bất kỳ khung báo cáo phù hợp nào, cho cả đảm bảo hạn chế lẫn hợp lý (tr.2–3).
  - "Profession agnostic", nhưng người hành nghề phải tuân thủ Bộ quy tắc IESBA và thuộc công ty áp dụng ISQM 1, hoặc theo yêu cầu tương đương (tr.1).
  - Đánh giá rủi ro ở cấp thuyết minh với đảm bảo hạn chế, ở cấp cơ sở dẫn liệu với đảm bảo hợp lý (tr.3).
  - ISAE 3410 (báo cáo KNK) được gộp vào và dự kiến rút khi ISSA 5000 có hiệu lực; ISAE 3000 (Revised) vẫn dùng cho các dịch vụ đảm bảo khác (tr.2).
  - Hiệu lực cho kỳ bắt đầu từ 15/12/2026, hoặc tại thời điểm từ 15/12/2026; được áp dụng sớm (tr.4). Với doanh nghiệp năm dương lịch, kỳ đầu là năm 2027.
  - IESSA (đạo đức) có cùng ngày hiệu lực, trừ phần chuỗi giá trị từ 01/07/2028 (tìm).
- *Liên quan GreenScan:* báo cáo đảm bảo là một nguồn bằng chứng "ngoài" (QA bank: `source_type` standard/external, prior +0,03). GreenScan không phải dịch vụ đảm bảo, mà là công cụ sàng lọc trước cho người soát hoặc kiểm toán viên.
- *Giống:* "đủ bằng chứng thích hợp mới kết luận" và thái độ hoài nghi nghề nghiệp tương ứng với evidence-first và abstain.
- *Khác:* dịch vụ đảm bảo có người ký và chịu trách nhiệm pháp lý; GreenScan không phát hành kết luận đảm bảo.
- *Việt Nam:* chưa tìm thấy văn bản của Bộ Tài chính hay VACPA chấp nhận ISSA 5000 (tìm, 04/11) [CHƯA XÁC MINH].

**1.2 ISSB — sửa đổi IFRS S2 (11/12/2025) (mở)**
- *Bốn điểm:*
  1. Được giới hạn đo và công bố Scope 3 hạng mục 15 vào phát thải tài trợ (financed emissions) theo định nghĩa của IFRS S2.
  2. Được dùng hệ phân loại khác GICS khi chia nhỏ phát thải tài trợ.
  3. Làm rõ miễn trừ dùng GHG Protocol khi chỉ một phần doanh nghiệp bị luật địa phương buộc dùng phương pháp khác.
  4. Miễn trừ mới (theo khu vực pháp lý) khỏi việc dùng hệ số GWP của báo cáo IPCC mới nhất.
- Hiệu lực cho kỳ bắt đầu từ 01/01/2027, được áp dụng sớm. Kèm sửa đổi ba chuẩn SASB về phát thải tài trợ.
- *Liên quan GreenScan:*
  - Ngân hàng: theo ISSB vẫn phải công bố phát thải tài trợ, trong khi TT 96 miễn chỉ tiêu 6.1–6.3 cho bốn ngành tài chính. Đây là hai khung khác nhau, không suy từ khung này ra khung kia.
  - GWP: hai số CO2e chỉ so được khi cùng bộ hệ số và cùng phương pháp. Đây là một điều kiện "so được" cho `comparison_policy`.
- *Giống/khác:* GreenScan không đánh giá tuân thủ IFRS S2; chỉ mượn định nghĩa (Scope, ranh giới hợp nhất, năm gốc) làm thuộc tính bắt buộc của tuyên bố số.

**1.3 Áp dụng ISSB trên thế giới và ở Việt Nam (tìm)**
- S&P Global (27/08/2026): tới 22/07/2026 có 35 khu vực pháp lý đã áp dụng (tự nguyện hoặc bắt buộc), thêm 11 khu vực dự kiến.
- IFRS Foundation (06/2025): bộ hồ sơ khu vực đầu tiên có 14 khu vực cam kết áp dụng đầy đủ, 2 chỉ phần khí hậu, 1 áp dụng một phần; báo chí khi đó nêu con số 36 khu vực "có tiến triển".
- *Việt Nam:* không tìm thấy văn bản ràng buộc về thời điểm áp dụng IFRS S1/S2.
  - Theo tóm tắt tìm kiếm của Crowe VN (trang bị 403), danh mục chuẩn mực Bộ Tài chính xây dựng cho giai đoạn 2026–2027 có IFRS S1, S2 [CHƯA XÁC MINH].
  - QĐ 345/QĐ-BTC (2020) là đề án áp dụng chuẩn mực báo cáo tài chính, không phải ISSB.
- *Liên quan:* trả lời câu "Việt Nam đã bắt buộc ISSB chưa": chưa thấy văn bản ràng buộc; khung bắt buộc hiện là TT 96/2020.

### B. Việt Nam

**1.4 Dự thảo thông tư thay TT 96/2020 (mở: TBTCVN 02/10/2026; VNS 29/10/2026)**
- *Là gì:* dự thảo của Bộ Tài chính thay toàn bộ TT 96/2020 về công bố thông tin trên thị trường chứng khoán, đăng trên cổng của Bộ và UBCKNN.
- *Chính:*
  - Có phụ lục riêng về báo cáo phát triển bền vững (môi trường, xã hội, quản trị).
  - Doanh nghiệp bỏ một chỉ tiêu bắt buộc phải nêu "lý do, nguyên nhân", kèm kế hoạch và lộ trình cho kỳ sau, trừ khi luật chuyên ngành đã quy định (VNS). Thực chất đây là cơ chế "công bố hoặc giải trình".
  - BCTN của công ty đại chúng: tối đa 120 ngày sau khi kết thúc năm tài chính. Báo cáo tình hình quản trị: 30 ngày.
  - Công bố đầy đủ bằng tiếng Anh chậm nhất từ 01/01/2028; nếu hai bản khác nhau thì bản tiếng Việt được áp dụng (cả hai bài).
  - Một tóm tắt tìm kiếm (bài 22/10/2026) ghi dự thảo có 10 chương, 47 điều, 22 phụ lục [CHƯA XÁC MINH].
  - Hai bài đã mở **không** nhắc ISSB, IFRS S1/S2, GRI hay IFC.
- *Trạng thái:* tới 29/10/2026 vẫn là đề xuất (VNS viết "proposed"). Văn bản đang hiệu lực là TT 96/2020, sửa bởi TT 68/2024, TT 18/2025 và TT 08/2026 (TT 08/2026 thay Phụ lục XVII; tìm).
- *Liên quan GreenScan:*
  - Mẫu 6 "công bố chọn lọc": nếu dự thảo được ban hành, "thiếu chỉ tiêu có giải trình" phải tách khỏi "thiếu không giải trình". Đoạn giải trình được trích làm bằng chứng về phạm vi, không coi là mâu thuẫn.
  - Hạn 120 ngày làm lùi thời điểm thu thập BCTN.
- *Giống/khác:* đội đã coi TT 96 là "bộ chỉ tiêu kỳ vọng" (02_PHAP_LY §2). Dự thảo chưa có hiệu lực, nên chỉ được dùng làm tham chiếu ở `current_policy_alignment`, không làm căn cứ.

**1.5 QĐ 21/2025/QĐ-TTg và QĐ 46/2026/QĐ-TTg (mở: VnEconomy 03/04/2026; tài liệu đội v4 13/10)**
- *QĐ 21/2025:*
  - Ký 04/07/2025; hiệu lực 22/08/2025 theo registry của đội (đối chiếu bản ký) và luatvietnam (tìm).
  - 45 loại dự án thuộc 7 lĩnh vực; dùng để xác nhận dự án cho trái phiếu xanh và tín dụng xanh.
  - Xác nhận bởi cơ quan thẩm định, hoặc tổ chức độc lập đạt ISO/IEC 17029 hay VSAE/ISAE 3000 (tài liệu đội).
  - Chưa thấy văn bản thay thế.
- *QĐ 46/2026:*
  - Ký 17/09/2026, hiệu lực 01/11/2026 (tài liệu đội v4, dòng 41, đội ghi [VERIFIED]).
  - Là chế độ thứ hai, chạy song song QĐ 21/2025: dự án xanh, dự án tuần hoàn và khung ESG (Phụ lục VI–VII).
  - Tỉnh công bố danh mục dự án xanh và tuần hoàn mỗi 30/6 và 31/12.
- *Bản dự thảo của QĐ 46 (VnEconomy 03/04/2026):*
  - Dự án tuần hoàn chia 3 loại: thiết kế tuần hoàn, sử dụng tuần hoàn, phục hồi tài nguyên.
  - Khung ESG 52 tiêu chí, yêu cầu tối thiểu theo quy mô: siêu nhỏ 7/52, nhỏ 10/52, vừa 12/52, hộ kinh doanh 4/52, còn lại 40/52 hoặc lập báo cáo phát triển bền vững theo chuẩn quốc tế.
  - Là cơ sở để được hỗ trợ lãi suất 2%/năm.
  - Đây là số của dự thảo; bản ký có thể khác [CHƯA XÁC MINH với bản ký].
- *Liên quan GreenScan:* danh mục của tỉnh là nguồn ngoài mới để kiểm tuyên bố "dự án đã được xác nhận xanh", nhưng đợt đầu chỉ có sau 01/11/2026, nên hiện chưa có dữ liệu. GreenScan không xác nhận dự án xanh; nó chỉ kiểm xem tuyên bố "đã được xác nhận" có văn bản hoặc có tên trong danh mục không.
- *Bẫy số hiệu:* QĐ **21/2026**/QĐ-TTg là danh mục công nghệ chiến lược (mục 1.8), không liên quan phân loại xanh.

**1.6 Luật BVDLCN 91/2025/QH15, NĐ 356/2025, NĐ 330/2026 (tìm; tài liệu đội)**
- Luật hiệu lực 01/01/2026 (đội [VERIFIED]; tìm). NĐ 356/2025 hướng dẫn luật và bãi bỏ NĐ 13/2023 (tài liệu đội).
- **Mới so với tài liệu đội:** NĐ 330/2026/NĐ-CP về xử phạt vi phạm hành chính trong lĩnh vực an ninh mạng và bảo vệ dữ liệu cá nhân, hiệu lực 19/08/2026 (VOV; PwC VN 15/09/2026; tìm). Theo các nguồn này:
  - Tự ý thu thập, xử lý dữ liệu cá nhân bị phạt tới 70 triệu đồng (VOV).
  - Mức phạt cố định tối đa 3 tỷ đồng (tìm).
  - Vi phạm chuyển dữ liệu cá nhân xuyên biên giới bị phạt tối đa 5% doanh thu năm trước liền kề (Luật Đ.8; tìm).
  - Phải thông báo sự cố trong 72 giờ (GV Lawyers; tìm).
  - Mọi mức phạt trên [CHƯA XÁC MINH với bản gốc].
- *Liên quan GreenScan:* chế độ `cloud` (GLM-5.2 qua FPT; khoá lỗi 401 từ 31/10) và Groq/Cerebras miễn phí đều xử lý trên nền tảng ở nước ngoài, tức là chuyển dữ liệu xuyên biên giới. Quy tắc tài liệu A/B/C của đội (02_PHAP_LY §6) đi đúng hướng.

**1.7 Luật Trí tuệ nhân tạo 134/2025/QH15 và NĐ 142/2026 (tìm; tài liệu đội)**
- Thông qua 10/12/2025, hiệu lực 01/03/2026 (nhiều nguồn thứ cấp; tìm).
- Điều 9 chia ba mức rủi ro: cao, trung bình, thấp.
  - Nhà cung cấp tự phân loại trước khi đưa hệ thống vào sử dụng.
  - Mức trung bình và cao phải có hồ sơ phân loại.
  - Danh mục rủi ro cao do Thủ tướng ban hành.
  - Tiêu chí chi tiết ở NĐ 142/2026 (ký 30/04/2026, hiệu lực 01/05/2026; đội v4 [VERIFIED]).
- Có yêu cầu bắt buộc với nội dung do AI tạo ra từ 01/03/2026 (luatminhkhue; tìm).
- *Liên quan GreenScan:* đội phải tự phân loại hệ thống. Giả thuyết: GreenScan hỗ trợ người soát chuyên môn và không tự ra quyết định về cá nhân, nên không thuộc rủi ro cao [GIẢ THUYẾT, chưa đối chiếu danh mục]. Tuy vậy kết luận có thể ảnh hưởng uy tín doanh nghiệp có tên, nên vẫn giữ người duyệt và nhật ký (`RunManifest`, `audit.jsonl`).

**1.8 QĐ 21/2026/QĐ-TTg — danh mục công nghệ chiến lược (mở: TTTCTT 06/05/2026)**
- Hiệu lực 01/07/2026, thay QĐ 1131/QĐ-TTg (12/06/2025, có 11 nhóm). Theo tóm tắt tìm kiếm, ban hành 30/04/2026.
- Có 10 nhóm công nghệ. Nhóm 7 là "Công nghệ an ninh mạng và lượng tử". Danh mục sản phẩm có mục "Truyền thông lượng tử, tính toán lượng tử và cảm biến lượng tử".
- *Liên quan:* trả lời câu "lượng tử có ý nghĩa chính sách gì ở Việt Nam". Nhà nước xếp lượng tử chung nhóm với an ninh mạng; điểm chạm gần nhất với tài chính là an ninh (mật mã hậu lượng tử), không phải việc đọc báo cáo.

### C. Luật về tuyên bố xanh ở nước ngoài

**1.9 Chỉ thị (EU) 2024/825 — ECGT/EmpCo (mở: Mayer Brown 27/10/2026)**
- Sửa Chỉ thị về hành vi thương mại không lành mạnh (UCPD) và Chỉ thị về quyền người tiêu dùng (CRD).
- Hiệu lực 26/03/2024; hạn nội luật hoá 27/03/2026; **áp dụng từ 27/09/2026**, không có giai đoạn chuyển tiếp.
- *Danh sách đen (luôn bị cấm):*
  - Tuyên bố môi trường chung chung ("xanh", "eco", "thân thiện môi trường") khi không chứng minh được hiệu quả môi trường xuất sắc được công nhận.
  - Nhãn bền vững không dựa trên hệ thống chứng nhận, hoặc không do cơ quan công quyền lập.
  - Tuyên bố cho cả sản phẩm hay cả doanh nghiệp khi chỉ đúng với một phần.
  - Tuyên bố trung hòa khí hậu cấp sản phẩm dựa trên bù trừ.
- *Đánh giá từng trường hợp:* tuyên bố về hiệu quả môi trường trong tương lai (ví dụ net zero) phải có cam kết rõ, kiểm chứng được, kế hoạch thực hiện và chuyên gia độc lập kiểm tra.
- *Nội luật hoá (EUR-Lex, qua Mayer Brown):*
  - 8 nước chưa thông báo biện pháp: Bulgaria, Séc, Malta, Ba Lan, Bồ Đào Nha, Slovenia, Tây Ban Nha, Thụy Điển. Pháp đang soạn.
  - Đan Mạch (28/05/2025) và Slovakia (19/11/2025) làm sớm; Hungary thông báo đúng ngày 27/09/2026.
  - Ủy ban mở thủ tục vi phạm với 20 nước ngày 28/05/2026 (tìm).
- *Liên quan GreenScan:* ánh xạ thẳng vào các mẫu tuyên bố của đội: chung chung (mẫu 1, 8), trung hòa nhờ tín chỉ (mẫu 9), cam kết tương lai không có kế hoạch. Phạm vi là giao dịch với người tiêu dùng EU, nên doanh nghiệp Việt xuất khẩu B2C chịu tác động; BCTN gửi nhà đầu tư không phải đối tượng trực tiếp.
- *Giống/khác:* "danh sách đen" tương ứng quy tắc cứng (Rules decide); "từng trường hợp" tương ứng chuyển người soát (Humans review). GreenScan không kết luận vi phạm luật EU.

**1.10 Green Claims Directive (tìm)**
- Đề xuất 22/03/2023 [KIẾN THỨC NỀN]. Nghị viện thông qua lập trường lần đọc thứ nhất 12/03/2024.
- Ngày 20/06/2025 Ủy ban tuyên bố ý định rút; Ý rút ủng hộ ngày 23/06/2025. Một ghi chú 12/2025 cho biết Ủy ban xác nhận chưa rút chính thức; bài 07/2026 vẫn gọi tương lai của đề xuất là "bất định".
- Không tìm thấy văn bản rút trên Công báo EU [CHƯA XÁC MINH].
- *Liên quan:* đây không phải luật, nên không viện dẫn làm căn cứ. Ý tưởng "chứng minh trước khi tuyên bố" gần với evidence-first, nhưng chỉ dùng làm lập luận thiết kế.

**1.11 UK DMCC Act 2024 (tìm)**
- Phần bảo vệ người tiêu dùng có hiệu lực 06/04/2025.
- CMA tự ra quyết định vi phạm và phạt tới 10% doanh thu toàn cầu hằng năm, hoặc £300.000 nếu mức này cao hơn, với vi phạm thực chất. Hướng dẫn: CMA200; CMA58 được cập nhật.
- Green Claims Code của CMA có từ 09/2021 [KIẾN THỨC NỀN].
- *Liên quan:* tuyên bố xanh gây hiểu nhầm với người tiêu dùng Anh có thể bị phạt mà không cần ra tòa, nên chi phí của một false SUPPORTED rất cao.

**1.12 FTC Green Guides (tìm)**
- 16 CFR Part 260, sửa lần cuối năm 2012 [KIẾN THỨC NỀN]. FTC mở lấy ý kiến ngày 14/12/2022; tới 2025–2026 vẫn chưa có bản sửa (Kelley Drye 2025; Net Zero Compare 08/2026).
- Đây là hướng dẫn diễn giải Điều 5 FTC Act, không phải quy tắc có chế tài riêng [KIẾN THỨC NỀN].
- *Liên quan:* Mỹ chưa có luật liên bang riêng về tuyên bố xanh; nói "Mỹ vừa ban hành luật chống greenwashing" là sai.

**1.13 ESMA — tên quỹ dùng thuật ngữ ESG hoặc bền vững (tìm)**
- Áp dụng từ 21/11/2024 với quỹ mới; quỹ hiện hữu phải tuân thủ trước 21/05/2025.
- Ít nhất 80% khoản đầu tư phải đáp ứng đặc tính môi trường/xã hội hoặc mục tiêu bền vững.
- Tên có chữ môi trường, tác động, ESG hay bền vững phải áp loại trừ của chuẩn PAB. Tên ghép nhiều thuật ngữ thì áp yêu cầu chặt nhất. Tên "bền vững" còn phải cam kết đầu tư bền vững "đáng kể".
- Tới giữa 05/2025, khoảng 880 quỹ (19% diện áp dụng) đã đổi tên, phần lớn bỏ hẳn chữ ESG (Morningstar).
- *Liên quan:* ví dụ chuẩn của "quy tắc cứng có ngưỡng" (Rules decide). GreenScan V1 chưa nhận dữ liệu danh mục nắm giữ, nên chưa kiểm được loại tuyên bố này.

**1.14 Úc — ASIC và ACCC (tìm)**
- *Mercer Superannuation:* Tòa Liên bang phạt A$11,3 triệu ngày 02/08/2024, cộng A$200.000 án phí. Là vụ greenwashing đầu tiên ASIC đưa ra tòa (ASIC 24-173MR).
- *Vanguard Investments Australia:* phạt A$12,9 triệu ngày 25/09/2024, liên quan quỹ Ethically Conscious Global Aggregate Bond Index Fund (Hedged). Theo tài liệu 04_AN_LE của đội, khoảng 74% chứng khoán của quỹ không được sàng lọc ESG.
- *Active Super (LGSS):* phạt A$10,5 triệu ngày 18/03/2025. ASIC đề nghị A$13,5 triệu; phía Active Super đề nghị A$2,456 triệu.
- *ACCC v Clorox Australia:* phạt A$8,25 triệu ngày 14/04/2025, cộng A$200.000 án phí; đây là mức phạt hai bên thoả thuận.
  - Nhãn "50% ocean plastic" trên túi GLAD, trong khi nhựa được thu gom ở các cộng đồng Indonesia cách bờ biển tới 50 km.
  - Vi phạm kéo dài 06/2021–07/2023, trên hơn 2,2 triệu sản phẩm.
- ***Clime:*** ASIC 25-254MR (10/2025) chỉ là điều tra sơ bộ Clime Asset Management về tài liệu công bố và xác định thị trường mục tiêu của Clime Australian Income Fund. Clime Capital và Clime Investment Management không phải đối tượng; Clime phủ nhận. **Đây không phải vụ greenwashing.**
- *Liên quan:*
  - Bài học "tuyên bố loại trừ bị bác bởi một phản ví dụ".
  - Phải tách thực thể pháp lý: Clorox Australia Pty Ltd khác The Clorox Company; Active Super sáp nhập ngày 01/03/2025 (PRE_CRAWL_AUDIT của đội).

### D. Lượng tử

**1.15 Farhi, Goldstone, Gutmann (2014) — QAOA (mở)**
- Thuật toán lượng tử tìm nghiệm xấp xỉ cho bài tối ưu tổ hợp, điều khiển bằng tham số nguyên p.
- Độ sâu mạch tăng tuyến tính theo p; chất lượng xấp xỉ tăng khi p tăng.
- Với MaxCut trên đồ thị 3-chính quy và p = 1, thuật toán luôn tìm được lát cắt ít nhất bằng 0,6924 lần lát cắt tối ưu.
- *Liên quan:* QAOA chỉ bảo đảm xấp xỉ, không bảo đảm nghiệm tối ưu. Ở 30 biến, ILP hoặc vét cạn cho nghiệm chính xác, nên QAOA chỉ có vai trò minh họa ở quy mô nhỏ.

**1.16 Herman et al. (2023), "Quantum computing for finance", *Nature Reviews Physics* 5:450–465 (arXiv:2201.02773) (tìm)**
- Monte Carlo lượng tử (ước lượng biên độ) có tăng tốc bậc hai về lý thuyết, nhưng chưa chứng minh được tăng tốc thực tế và cần máy chịu lỗi.
- Bài toán tối ưu trong tài chính có dạng liên tục, rời rạc và hỗn hợp.
- Ưu điểm và khó khăn của học máy lượng tử với bài toán cổ điển cũng chuyển sang tài chính.
- *Liên quan:* căn cứ để nói "chưa có lợi thế lượng tử thực tế trong tài chính". Phải nói đó là kết luận của bài tổng quan năm 2023, không phải của đội.

**1.17 HSBC và IBM (25/09/2025) (tìm)**
- Quy trình lai lượng tử–cổ điển trên bộ xử lý IBM Heron, với dữ liệu RFQ trái phiếu doanh nghiệp châu Âu ở quy mô sản xuất.
- Cải thiện "tới 34%" khả năng dự báo một lệnh có được khớp ở giá chào hay không. Theo fi-desk, đây là cải thiện tương đối về AUC so với dùng dữ liệu thường.
- Không có giao dịch thật; kết quả chỉ trên dữ liệu của HSBC.
- *Liên quan:* ví dụ thật gần nhất của lượng tử trong nghiệp vụ tài chính. Đây là cải thiện so với một baseline cụ thể, không phải lợi thế lượng tử tổng quát.

**1.18 Toshiba SQBM+ (tìm)**
- Bộ giải Ising "lấy cảm hứng lượng tử" dựa trên thuật toán phân nhánh mô phỏng (simulated bifurcation), chạy trên phần cứng cổ điển.
- Có trên Azure Quantum (06/2022, tới 100.000 biến) và AWS Marketplace (02/2023). Bản 2 (11/2023) giải tới 10 triệu biến, nhắm bài toán danh mục đầu tư; từng thử nghiệm cho giao dịch tần suất cao.
- Không tìm thấy tên ngân hàng cụ thể đã triển khai.
- *Liên quan:* nếu bài QUBO của GreenScan lớn lên, con đường thực tế là dùng bộ giải lấy cảm hứng lượng tử, không cần máy lượng tử.

**1.19 QNLP — DisCoCat và lambeq (tìm)**
- Meichanetzidis et al. (2020, arXiv:2012.03756) lần đầu chạy một tác vụ NLP (phân loại câu có xét ngữ pháp) trên máy NISQ. lambeq là thư viện Python đầu tiên cho QNLP.
- Khảo sát 2025: trên tác vụ nhỏ, QNLP đạt hiệu năng cạnh tranh với ít tham số hơn, nhưng lĩnh vực bị giới hạn nghiêm trọng bởi phần cứng NISQ.
- *Liên quan:* không dùng được cho báo cáo hàng trăm trang, có bảng, viết tiếng Việt. Nói QNLP sẽ thay LLM là "greenwashing công nghệ".

**1.20 Thể lệ cuộc thi về lượng tử và hiện trạng GreenScan (tài liệu đội; kiểm mã)**
- *Thể lệ:*
  - Nhóm 4 "Quantum Computing cho Tài chính" gợi ý tối ưu danh mục và học máy lượng tử cho dự báo, chấm điểm. "Đội thi không cần phần cứng lượng tử thực tế"; được dùng Qiskit, PennyLane, Cirq (the_le dòng 174–181).
  - Điều 10: mọi chủ đề, kể cả AI và lượng tử, chấm theo cùng hệ tiêu chí: giá trị bài toán, độ hợp lý của giải pháp, khả năng thành sản phẩm, tác động.
  - Giải phụ "Ứng dụng Lượng tử xuất sắc" 15 triệu đồng dành cho sản phẩm "sử dụng công nghệ lượng tử hoặc AI-Quantum" (dòng 640–642).
- *GreenScan ngày 04/11:*
  - 0 tệp mã có QUBO, QAOA hay ủ mô phỏng; không cài qiskit, pennylane, dimod, neal hay cirq.
  - Kế hoạch 31/10 (AG-0 … AG-6) không có hạng mục lượng tử. Quyết định D-2026-09-18-01 ghi "QUBO prototype chỉ sau 25/10 nếu vào Chung kết", nhưng tới nay chưa làm.
  - Phần đã có trên tài liệu: công thức QUBO (brief §7.2, D-2026-09-18-06) và slide S13 Bán kết "Quantum: nghiên cứu, chưa vào sản phẩm".
  - Chữ "quantum" trong `src/quantum_gw/`, lệnh `quantum-agent`, thư mục `.quantum/runs` và các biến `QUANTUM_PROFILE`, `QUANTUM_LLM_STANCE`, `QUANTUM_VERIFY` chỉ là tên dự án, không phải tính toán lượng tử.

---

## 2. Khái niệm và lý thuyết phải nắm

**2.1 Đảm bảo hạn chế và đảm bảo hợp lý (ISSA 5000).**
- Hạn chế: kết luận dạng phủ định ("không có gì khiến chúng tôi cho rằng…"); đánh giá rủi ro ở cấp thuyết minh.
- Hợp lý: ý kiến khẳng định; đánh giá rủi ro ở cấp cơ sở dẫn liệu; khối lượng công việc lớn hơn.
- *Ví dụ:* báo cáo phát triển bền vững có đảm bảo hạn chế chỉ cho Scope 1–2. Khi đó báo cáo đảm bảo chỉ nên tính là nguồn ngoài cho đúng hai chỉ tiêu đó, không cho tuyên bố "dẫn đầu xanh" ở trang 3 (cần kiểm mã xem đã giới hạn phạm vi chưa).

**2.2 Khung báo cáo phù hợp và "trung lập về khung".** ISSA 5000 áp cho mọi khung (ISSB, ESRS, GRI, luật địa phương). Kiểm tuyên bố phải gắn với khung mà doanh nghiệp tuyên bố đã theo. *Ví dụ:* doanh nghiệp Việt Nam báo cáo theo TT 96 Phụ lục IV thì không thể bị coi là "thiếu" theo IFRS S2.

**2.3 Phát thải tài trợ (Scope 3 hạng mục 15) và GWP.**
- Phát thải tài trợ là phát thải của khoản vay và khoản đầu tư, quy về tổ chức tài chính theo tỷ lệ tài trợ (theo phương pháp PCAF) [KIẾN THỨC NỀN].
- GWP là hệ số quy khí nhà kính về CO2e. CH4: AR5 là 28; AR6 (nguồn hóa thạch) là 29,8 [KIẾN THỨC NỀN].
- *Ví dụ:* 1.000 t CH4 bằng 28.000 tCO2e theo AR5 nhưng 29.800 tCO2e theo AR6, lệch 6,4% chỉ do đổi hệ số. GreenScan phải trả "không so được", không phải "mâu thuẫn".

**2.4 "Công bố hoặc giải trình" (comply or explain).** Doanh nghiệp được phép không công bố một chỉ tiêu nếu giải trình lý do và kế hoạch. *Ví dụ:* trong dự thảo thay TT 96, "thiếu chỉ tiêu nước, có giải trình" khác "thiếu im lặng". GreenScan trích đoạn giải trình; chất lượng giải trình do người soát phán đoán.

**2.5 Phân loại xanh và xác nhận độc lập.**
- Phân loại xanh (taxonomy) là danh mục hoạt động đủ điều kiện xanh kèm tiêu chí.
- Xác nhận độc lập do tổ chức đạt ISO/IEC 17029 (yêu cầu chung cho tổ chức thẩm định và kiểm tra xác nhận) hoặc theo VSAE/ISAE 3000.
- *Ví dụ:* tuyên bố "dự án điện mặt trời đã được xác nhận xanh theo QĐ 21/2025" cần văn bản xác nhận hoặc tên trong danh mục được công bố. Không đạt tiêu chí phân loại xanh không có nghĩa là nói dối.

**2.6 Tuyên bố môi trường chung chung và "hiệu quả môi trường xuất sắc được công nhận".**
- Theo 2024/825, các từ "xanh", "eco", "thân thiện môi trường" chỉ được dùng khi chứng minh được hiệu quả xuất sắc được công nhận, ví dụ EU Ecolabel hay nhãn sinh thái loại I [KIẾN THỨC NỀN].
- Tuyên bố trung hòa dựa trên bù trừ ở cấp sản phẩm bị cấm hẳn.
- *Ví dụ:* "bao bì thân thiện môi trường" không kèm chứng nhận rơi vào mẫu 1 và mẫu 8 của đội. Ở Việt Nam, Luật BVMT Đ.145 cũng yêu cầu chứng nhận.

**2.7 Danh sách đen (cấm tuyệt đối) và đánh giá từng trường hợp.** Danh sách đen không cần chứng minh tác động tới người tiêu dùng; đánh giá từng trường hợp cần xét bối cảnh. *Ánh xạ:* danh sách đen tương ứng quy tắc cứng (Rules decide); từng trường hợp tương ứng người soát (Humans review).

**2.8 Ngưỡng 80% và loại trừ PAB/CTB (ESMA).**
- PAB là loại trừ của chuẩn Paris-Aligned Benchmark (gồm loại trừ nhiên liệu hóa thạch theo ngưỡng doanh thu); CTB là bản nhẹ hơn [KIẾN THỨC NỀN].
- *Ví dụ:* quỹ tên "Sustainable Transition" phải áp PAB, vì tên ghép thì áp yêu cầu chặt nhất.

**2.9 Lượng từ "với mọi" và "tồn tại" trong tuyên bố loại trừ.** "Không đầu tư vào than" nghĩa là với mọi khoản nắm giữ h, h không thuộc ngành than; chỉ cần một khoản nắm giữ là than là đủ bác bỏ. *Ví dụ:* các vụ Mercer và Vanguard. GreenScan cần dữ liệu nắm giữ, và một phản ví dụ có nguồn là đủ để gắn cờ.

**2.10 Phạt theo phần trăm doanh thu và mức phạt thoả thuận.** Anh (DMCC): tới 10% doanh thu toàn cầu. Việt Nam (Luật 91/2025): tới 5% doanh thu năm trước với vi phạm chuyển dữ liệu xuyên biên giới. Úc thường dùng mức phạt hai bên thoả thuận rồi tòa chấp thuận (vụ Clorox).

**2.11 QUBO và mô hình Ising.**
- QUBO: tìm x thuộc {0,1}^n để tối thiểu xᵀQx = Σᵢ Qᵢᵢxᵢ + Σᵢ<ⱼ Qᵢⱼxᵢxⱼ. Ràng buộc đưa vào bằng hàm phạt, ví dụ ràng buộc chọn đúng k phần tử là μ(Σⱼxⱼ − k)².
- Đổi sang Ising bằng xᵢ = (1 − sᵢ)/2 với sᵢ thuộc {−1, +1}, được H = Σhᵢsᵢ + ΣJᵢⱼsᵢsⱼ + c.
- *GreenScan (brief §7.2):* xⱼ = chọn đoạn j; năng lượng gồm −Σrⱼxⱼ (độ liên quan, nên gồm cả prior về thẩm quyền), λΣsⱼₗxⱼxₗ (trùng lặp), μ(Σxⱼ − k)² và phần phạt độ phủ 5 thuộc tính qua biến yₘ. Xem brief để biết hệ số đúng.

**2.12 Ủ mô phỏng (SA).** Thuật toán **cổ điển** (Kirkpatrick et al. 1983) [KIẾN THỨC NỀN]: lật một bit, nhận nghiệm tệ hơn với xác suất e^(−ΔH/T), rồi giảm T dần. Lấy cảm hứng từ vật lý thống kê, không phải từ cơ học lượng tử.

**2.13 Ủ lượng tử.**
- H(t) = A(t)·(−Σσᵢˣ) + B(t)·H_Ising. Bắt đầu ở trạng thái cơ bản của số hạng trường ngang, rồi biến đổi đủ chậm (định lý đoạn nhiệt) để kết thúc ở trạng thái năng lượng thấp của H_Ising. Thời gian cần thiết tăng khi khe năng lượng nhỏ nhất hẹp lại [KIẾN THỨC NỀN].
- Phần cứng D-Wave có kết nối thưa, nên phải nhúng đồ thị bài toán vào chip (minor embedding) bằng chuỗi qubit. QUBO dày như bài của GreenScan tốn nhiều chuỗi.

**2.14 QAOA.**
- Trạng thái |ψ(γ,β)⟩ = Πₗ₌₁…ₚ e^(−iβₗH_M)·e^(−iγₗH_C)·|+⟩^⊗n, với mixer H_M = ΣXᵢ.
- Tham số γ, β được tối ưu bằng vòng lặp cổ điển; đo trạng thái để lấy chuỗi bit.
- Thuật toán chỉ bảo đảm xấp xỉ (p = 1 trên MaxCut 3-chính quy cho ít nhất 0,6924 lần tối ưu). p lớn làm mạch sâu, và nhiễu phần cứng phá kết quả.

**2.15 Thuật toán lấy cảm hứng lượng tử.** Là thuật toán cổ điển chạy trên CPU, GPU hoặc FPGA, không có qubit. Gồm [KIẾN THỨC NỀN]:
- ủ lượng tử mô phỏng (Monte Carlo tích phân đường);
- phân nhánh mô phỏng (Goto et al. 2019; Toshiba SQBM+);
- digital annealer của Fujitsu;
- mạng tensor;
- thuật toán "giải lượng tử hoá" (Tang 2019).

**2.16 NISQ và giới hạn mô phỏng.**
- NISQ (Preskill 2018): vài chục tới vài trăm qubit có nhiễu, chưa sửa lỗi [KIẾN THỨC NỀN].
- Bộ mô phỏng statevector cần 2ⁿ số phức × 16 byte: 20 qubit cần 16 MiB, 25 qubit 512 MiB, 28 qubit 4 GiB, 30 qubit 16 GiB.
- *Ví dụ:* laptop của đội có 15,6 GB RAM và đã gần đầy (ghi chép 01/11), nên QAOA statevector chỉ khả thi tới khoảng 25 qubit.

**2.17 Lợi thế lượng tử.**
- Chỉ có khi, trên cùng bài toán, lượng tử đạt chất lượng bằng hoặc hơn thuật toán cổ điển **tốt nhất** với chi phí (thời gian, năng lượng, tiền) thấp hơn, và lặp lại được.
- Ước lượng biên độ: để đạt sai số ε cần O(1/ε) truy vấn, so với O(1/ε²) của Monte Carlo cổ điển (Montanaro 2015) [KIẾN THỨC NỀN]. Điều này cần mạch sâu, nên cần máy chịu lỗi.

**2.18 QNLP (DisCoCat).** Câu được đổi thành sơ đồ ngữ pháp (pregroup), rồi thành mạch lượng tử có tham số; nghĩa của từ là tham số, huấn luyện như mạch biến phân. Mới chạy được câu ngắn và tập dữ liệu nhỏ.

**2.19 Mật mã hậu lượng tử (PQC).**
- Thuật toán Shor trên máy lượng tử đủ lớn phá được RSA và ECC; dữ liệu bị thu hôm nay có thể bị giải mã sau này ("thu trước, giải mã sau").
- NIST công bố FIPS 203 (ML-KEM), 204 (ML-DSA) và 205 (SLH-DSA) ngày 13/08/2024 [KIẾN THỨC NỀN].
- Đây là điểm chạm lượng tử thực tế nhất với hạ tầng tài chính hiện nay.

**2.20 Hai chế độ kiểm theo thời gian (đội).** `historical_compliance` đối chiếu với luật có hiệu lực lúc công bố; `current_policy_alignment` đối chiếu với tiêu chí hôm nay. *Ví dụ:* tuyên bố công bố 06/2026 về "dự án xanh" được xét theo QĐ 21/2025 ở chế độ lịch sử, và có thể xét thêm theo QĐ 46/2026 (hiệu lực 01/11/2026) ở chế độ hiện hành.

---

## 3. Số liệu và dữ kiện được phép nói

| # | Dữ kiện | Nguồn (đường dẫn, mục/trang) | Nhãn |
|---|---|---|---|
| 1 | ISSA 5000 hiệu lực cho kỳ bắt đầu từ 15/12/2026 (hoặc thời điểm từ 15/12/2026); được áp dụng sớm | IAASB Fact Sheet (mở) tr.4; `scratchpad\R9\issa5000_factsheet.txt` dòng 220–223 | [NGOÀI] |
| 2 | ISSA 5000 áp cho đảm bảo hạn chế và hợp lý, mọi khung báo cáo phù hợp, kể cả KNK | Fact Sheet tr.2–3 | [NGOÀI] |
| 3 | ISAE 3410 gộp vào ISSA 5000, dự kiến rút khi ISSA 5000 có hiệu lực; ISAE 3000 (Revised) vẫn dùng cho dịch vụ khác | Fact Sheet tr.2 | [NGOÀI] |
| 4 | ISSA 5000 "profession agnostic", với điều kiện IESBA Code và ISQM 1 hoặc tương đương | Fact Sheet tr.1 | [NGOÀI] |
| 5 | ISSA 5000 ban hành 12/11/2024 | INCP (tìm) | [NGOÀI] [CHƯA XÁC MINH trên trang IAASB] |
| 6 | Chưa tìm thấy văn bản Việt Nam chấp nhận ISSA 5000 | Tìm kiếm 04/11 | [CHƯA XÁC MINH] |
| 7 | IFRS S2 sửa đổi ngày 11/12/2025, gồm 4 điểm (hạng mục 15, ngoài GICS, GHG Protocol, GWP); hiệu lực 01/01/2027, được áp dụng sớm | ifrs.org (mở) | [NGOÀI] |
| 8 | 35 khu vực pháp lý đã áp dụng ISSB tới 22/07/2026; 11 khu vực dự kiến | S&P Global 27/08/2026 (tìm) | [NGOÀI] |
| 9 | Chưa tìm thấy văn bản Việt Nam ràng buộc thời điểm áp dụng IFRS S1/S2 | Tìm kiếm 04/11 | [CHƯA XÁC MINH] |
| 10 | Dự thảo thay TT 96 có phụ lục riêng về báo cáo phát triển bền vững; bỏ chỉ tiêu phải nêu lý do và kế hoạch cho kỳ sau | VNS 29/10/2026 (mở) | [NGOÀI] |
| 11 | Dự thảo: BCTN tối đa 120 ngày; báo cáo quản trị 30 ngày | TBTCVN 02/10/2026 (mở) | [NGOÀI] |
| 12 | Dự thảo: tiếng Anh đầy đủ chậm nhất 01/01/2028; bản tiếng Việt được áp dụng khi khác biệt | TBTCVN, VNS (mở) | [NGOÀI] |
| 13 | Dự thảo có 10 chương, 47 điều, 22 phụ lục | Tóm tắt tìm kiếm (bài 22/10/2026) | [NGOÀI] [CHƯA XÁC MINH] |
| 14 | Hai bài về dự thảo không nhắc ISSB, IFRS S1/S2, GRI, IFC | TBTCVN, VNS (mở) | [NGOÀI] |
| 15 | TT 08/2026/TT-BTC sửa TT 96, thay Phụ lục XVII | hethongphapluat (tìm); 02_PHAP_LY §1 | [NGOÀI] |
| 16 | QĐ 21/2025/QĐ-TTg: ký 04/07/2025, hiệu lực 22/08/2025; 45 loại dự án thuộc 7 lĩnh vực | 02_PHAP_LY §1; luatvietnam (tìm) | [NGOÀI] |
| 17 | QĐ 46/2026/QĐ-TTg: ký 17/09/2026, hiệu lực 01/11/2026; chạy song song QĐ 21/2025; tỉnh công bố danh mục mỗi 30/6 và 31/12 | KE_HOACH_DU_LIEU_PHAP_LY_v4 dòng 41 | [NGOÀI] (đội ghi VERIFIED) |
| 18 | Dự thảo QĐ (03/2026): khung ESG 52 tiêu chí, tối thiểu 7/10/12/4/40 theo quy mô; hỗ trợ lãi suất 2%/năm | VnEconomy 03/04/2026 (mở) | [NGOÀI] (số của dự thảo) |
| 19 | Luật 91/2025/QH15 hiệu lực 01/01/2026; NĐ 356/2025 bãi bỏ NĐ 13/2023 | 02_PHAP_LY §6; tìm | [NGOÀI] |
| 20 | NĐ 330/2026/NĐ-CP xử phạt vi phạm về an ninh mạng và dữ liệu cá nhân, hiệu lực 19/08/2026 | VOV; PwC VN 15/09/2026 (tìm) | [NGOÀI] |
| 21 | Vi phạm chuyển dữ liệu cá nhân xuyên biên giới bị phạt tối đa 5% doanh thu năm trước liền kề | Luật 91/2025 Đ.8, qua hethongphapluat (tìm) | [NGOÀI] [CHƯA XÁC MINH bản gốc] |
| 22 | Luật TTNT 134/2025/QH15: thông qua 10/12/2025, hiệu lực 01/03/2026; ba mức rủi ro | apolatlegal, luatminhkhue, hethongphapluat (tìm) | [NGOÀI] |
| 23 | NĐ 142/2026: ký 30/04/2026, hiệu lực 01/05/2026 | KE_HOACH_DU_LIEU_PHAP_LY_v4 dòng 73 | [NGOÀI] |
| 24 | QĐ 21/2026/QĐ-TTg: 10 nhóm công nghệ chiến lược, hiệu lực 01/07/2026, thay QĐ 1131/2025; nhóm 7 là "an ninh mạng và lượng tử" | TTTCTT 06/05/2026 (mở) | [NGOÀI] |
| 25 | Chỉ thị 2024/825: hiệu lực 26/03/2024; hạn nội luật hoá 27/03/2026; áp dụng từ 27/09/2026 | Mayer Brown 27/10/2026 (mở) | [NGOÀI] |
| 26 | 8 nước EU chưa thông báo biện pháp nội luật hoá 2024/825 | Mayer Brown, dẫn EUR-Lex (mở) | [NGOÀI] |
| 27 | Ủy ban EU mở thủ tục vi phạm với 20 nước ngày 28/05/2026 | Jones Day, politis (tìm) | [NGOÀI] |
| 28 | Green Claims Directive: ý định rút ngày 20/06/2025; chưa thấy văn bản rút chính thức; 07/2026 vẫn "bất định" | Latham & Watkins, Packaging Europe, CMS (tìm) | [NGOÀI] [CHƯA XÁC MINH] |
| 29 | DMCC: hiệu lực 06/04/2025; CMA phạt tới 10% doanh thu toàn cầu hoặc £300.000 | CMS, Slaughter and May (tìm) | [NGOÀI] |
| 30 | FTC Green Guides: rà soát từ 14/12/2022; chưa có bản sửa tới 08/2026 | Kelley Drye, Net Zero Compare (tìm) | [NGOÀI] |
| 31 | ESMA: áp dụng 21/11/2024 (quỹ mới), 21/05/2025 (quỹ hiện hữu); ngưỡng 80%; loại trừ PAB | FMA Austria, Osborne Clarke (tìm) | [NGOÀI] |
| 32 | Khoảng 880 quỹ (19%) đổi tên tới giữa 05/2025 | Morningstar (tìm) | [NGOÀI] |
| 33 | Mercer bị phạt A$11,3 triệu (02/08/2024) | ASIC 24-173MR (tìm) | [NGOÀI] |
| 34 | Vanguard bị phạt A$12,9 triệu (25/09/2024) | Mallesons, GTLaw (tìm) | [NGOÀI] |
| 35 | Active Super bị phạt A$10,5 triệu (18/03/2025) | investordaily và các hãng luật (tìm) | [NGOÀI] |
| 36 | Clorox bị phạt A$8,25 triệu (14/04/2025) vì nhãn "50% ocean plastic"; hơn 2,2 triệu sản phẩm | ACCC (tìm) | [NGOÀI] |
| 37 | Clime: ASIC 25-254MR là điều tra sơ bộ về tài liệu công bố của quỹ, không phải greenwashing | ASIC (tìm) | [NGOÀI] |
| 38 | QAOA p = 1 trên MaxCut 3-chính quy cho ít nhất 0,6924 lần tối ưu | arXiv:1411.4028 (mở) | [KIẾN THỨC NỀN] |
| 39 | Monte Carlo lượng tử: tăng tốc bậc hai về lý thuyết, chưa chứng minh thực tế, cần máy chịu lỗi | Herman et al. 2023 (tìm) | [NGOÀI] |
| 40 | HSBC–IBM 25/09/2025: cải thiện "tới 34%" dự báo khớp lệnh RFQ (AUC tương đối); không giao dịch thật | TQI, fi-desk, MIT Sloan ME (tìm) | [NGOÀI] |
| 41 | SQBM+ trên Azure 06/2022 (100.000 biến); bản 2 (11/2023) tới 10 triệu biến | Azure blog, TQI (tìm) | [NGOÀI] |
| 42 | QNLP lần đầu chạy trên NISQ năm 2020; lĩnh vực bị giới hạn bởi NISQ (khảo sát 2025) | arXiv:2012.03756; ACL 2025 (tìm) | [NGOÀI] |
| 43 | Statevector n qubit cần 2ⁿ × 16 byte; 30 qubit khoảng 16 GiB | Tự tính | [KIẾN THỨC NỀN] |
| 44 | C(30,5) = 142.506 tổ hợp, vét cạn được | QA bank Q89 | [KIẾN THỨC NỀN] |
| 45 | GWP của CH4: AR5 là 28, AR6 (hóa thạch) là 29,8, lệch 6,4% chỉ do hệ số | IPCC AR5/AR6 (chưa mở trong phiên) | [KIẾN THỨC NỀN] |
| 46 | NIST FIPS 203/204/205 công bố 13/08/2024 | Chưa mở trong phiên | [KIẾN THỨC NỀN] |
| 47 | 0 tệp mã QUBO/QAOA/SA trong `src/ experiments/ tools/ benchmark/ training/ scripts/`; không cài thư viện lượng tử | Kiểm mã 04/11 | [ĐÃ THỰC NGHIỆM] |
| 48 | Thể lệ: không cần phần cứng lượng tử; được dùng Qiskit, PennyLane, Cirq | the_le_cuoc_thi.txt dòng 179–181 | [NGOÀI] |
| 49 | Điều 10 chấm mọi chủ đề theo cùng tiêu chí; giải phụ Lượng tử 15 triệu đồng | the_le dòng 272–276, 640–642 | [NGOÀI] |
| 50 | HPG (lượt 22/10): 156 tuyên bố gồm 153 PARTIAL, 2 SUPPORTED, 1 INSUFFICIENT; 0 quy tắc pháp lý áp được trên 156/156 | KE_HOACH_AGENT…31 mục 2 (F1, F5) | [ĐÃ THỰC NGHIỆM] |
| 51 | Ngoài mẫu sạch 87 ca (nhãn bạc): độ phủ của luật 0,011; 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253; mọi model precision 1,0, 0 kết luận sai | Như trên, mục 10 (01/11 17:00) | [ĐÃ THỰC NGHIỆM] |
| 52 | Khoá FPT lỗi 401 từ 31/10; chế độ cloud không chạy, demo chạy `offline` | Như trên, mục 10 (31/10) | [ĐÃ THỰC NGHIỆM] |
| 53 | Chưa có nhãn người: 0/88 cặp, 0/79 câu | Như trên, mục 2 (F7) | [ĐÃ THỰC NGHIỆM] |

---

## 4. Câu hỏi BGK dự kiến

*Công thức trả lời: vấn đề → nguyên lý → GreenScan làm gì → giới hạn.*

**Q1. Lượng tử nằm ở đâu trong sản phẩm?**
- *Trả lời:*
  - (Vấn đề) Bài toán của người dùng là đọc báo cáo, tìm bằng chứng, so số; đó là bài toán của AI và quy tắc.
  - (Nguyên lý) Chỉ đưa lượng tử vào chỗ có cấu trúc tối ưu tổ hợp và đo được so với cổ điển.
  - (GreenScan) Bản demo hôm nay không chạy thành phần lượng tử nào, kể cả mô phỏng; chúng em đã kiểm lại mã ngày 04/11. Phần lượng tử là một bài toán con đã viết thành QUBO: chọn k đoạn bằng chứng phủ đủ năm thuộc tính (chỉ số, giá trị–đơn vị, kỳ, năm gốc, phạm vi) và ít trùng lặp. Bài này chạy được bằng ủ lượng tử, QAOA hoặc bộ giải lấy cảm hứng lượng tử.
  - (Giới hạn) Chưa có benchmark nên không nói nhanh hơn hay tốt hơn. Với 30 ứng viên, vét cạn 142.506 tổ hợp là đủ.
- *Vặn:* "Vậy phần lượng tử chỉ trên giấy?" → "Đúng. Đó là công thức và kế hoạch đo bốn cột; chúng em chọn nói thật thay vì ghép một demo không nối với sản phẩm."
- *Bẫy:* nói "QAOA của nhóm", "quantum-enhanced", "đã chạy trên simulator". Nếu bị hỏi về giải phụ Lượng tử, nói rõ thành phần lượng tử mới ở mức hình thức hoá.

**Q2. Gói mã tên `quantum_gw`, lệnh `quantum-agent`, biến `QUANTUM_PROFILE`; vậy là có lượng tử?**
- *Trả lời:*
  - (Vấn đề) Tên mã dễ gây hiểu nhầm.
  - (Nguyên lý) Một sản phẩm kiểm tuyên bố phóng đại thì không được tự phóng đại.
  - (GreenScan) Chữ "quantum" là tên dự án từ khi đăng ký cuộc thi. Không thư viện lượng tử nào được cài (không có Qiskit, PennyLane, dimod), không có mạch lượng tử, không có bộ giải Ising.
  - (Giới hạn) Nên ghi chú điều này trên slide kiến trúc và trong README.
- *Vặn:* "Sao không đổi tên?" → "Đổi tên gói sát Chung kết sẽ làm vỡ đường dẫn, test và lệnh chạy; chúng em ưu tiên ổn định và nói rõ."
- *Bẫy:* lảng tránh, hoặc nói "tên thể hiện định hướng lượng tử".

**Q3. Bài chọn bằng chứng có đủ khó để cần lượng tử không?**
- *Trả lời:*
  - (Vấn đề) Mỗi tuyên bố có 20–40 đoạn ứng viên; cần chọn k đoạn vừa liên quan, vừa phủ thuộc tính, vừa không trùng lặp.
  - (Nguyên lý) Đây là bài chọn tập con có ràng buộc, NP-khó ở dạng tổng quát, nhưng ở 30 biến thì cổ điển giải chính xác ngay.
  - (GreenScan) Vì thế benchmark có cột ILP hoặc vét cạn làm trần, greedy/MMR làm baseline mạnh. Lượng tử chỉ đáng thử khi các bài nhỏ bị ghép lại: ví dụ ngân sách OCR/LLM dùng chung cho cả lô 200 tuyên bố, hoặc bằng chứng dùng chung giữa nhiều tuyên bố. Khi đó số biến lên hàng nghìn và có liên kết chéo.
  - (Giới hạn) Chưa đo điểm mà cổ điển bắt đầu không theo kịp.
- *Vặn:* "5.000 doanh nghiệp × 200 tuyên bố mà mỗi tuyên bố độc lập thì chỉ là một triệu bài nhỏ?" → "Đúng. Bài nhỏ độc lập không cần lượng tử; chỉ ràng buộc chung (ngân sách, phủ chéo) mới tạo bài lớn, và đó là giả thuyết cần kiểm."
- *Bẫy:* dùng con số "5.000 × 200" như QA bank Q89 mà không nêu ràng buộc ghép.

**Q4. Ủ lượng tử, QAOA và thuật toán lấy cảm hứng lượng tử khác nhau thế nào? Đội chọn gì?**
- *Trả lời:*
  - (Vấn đề) Ba thuật ngữ hay bị dùng lẫn.
  - (Nguyên lý)
    - Ủ lượng tử dùng phần cứng tương tự (D-Wave), biến đổi chậm từ trường ngang sang Hamiltonian Ising để hệ dừng ở trạng thái năng lượng thấp.
    - QAOA là mạch cổng gồm p lớp xen kẽ Hamiltonian bài toán và mixer, tham số tối ưu bằng vòng lặp cổ điển; chỉ bảo đảm xấp xỉ (p = 1 trên MaxCut 3-chính quy cho ít nhất 0,6924 lần tối ưu).
    - Lấy cảm hứng lượng tử là thuật toán cổ điển, như phân nhánh mô phỏng của Toshiba SQBM+, chạy trên CPU hoặc GPU.
  - (GreenScan) Kế hoạch theo thứ tự: ILP chính xác và greedy làm mốc; ủ mô phỏng hoặc ủ lượng tử mô phỏng; QAOA mô phỏng tới khoảng 20 qubit để minh họa.
  - (Giới hạn) Chưa chạy.
- *Vặn:* "Ủ mô phỏng có phải lượng tử không?" → "Không. Đó là thuật toán cổ điển từ năm 1983, lấy ý tưởng từ vật lý thống kê."
- *Bẫy:* gọi SA là "quantum-inspired" (QA bank Q83 đang viết như vậy).

**Q5. Có ngân hàng nào dùng lượng tử thật chưa? Đã có lợi thế lượng tử trong tài chính chưa?**
- *Trả lời:*
  - (Vấn đề) Có nhiều thông cáo, ít bằng chứng.
  - (Nguyên lý) Chỉ có lợi thế khi thắng thuật toán cổ điển tốt nhất trên cùng bài với chi phí thấp hơn, và lặp lại được.
  - (Thực tế)
    - HSBC–IBM (25/09/2025): quy trình lai trên IBM Heron với dữ liệu RFQ trái phiếu doanh nghiệp châu Âu, cải thiện "tới 34%" khả năng dự báo lệnh được khớp so với baseline của họ; không có giao dịch thật.
    - Tổng quan trên *Nature Reviews Physics* (2023): Monte Carlo lượng tử có tăng tốc bậc hai về lý thuyết nhưng cần máy chịu lỗi, và chưa chứng minh được tăng tốc thực tế.
    - Bộ giải lấy cảm hứng lượng tử đã được bán trên cloud.
  - (GreenScan) Vì vậy chúng em không tuyên bố lợi thế lượng tử.
- *Vặn:* "34% chẳng phải là lợi thế sao?" → "Đó là cải thiện tương đối một chỉ số dự báo trên dữ liệu của HSBC so với một baseline, chưa phải so với thuật toán cổ điển tốt nhất ở cùng chi phí."
- *Bẫy:* nói "lượng tử nhanh hơn 34%".

**Q6. Sao không dùng QNLP hay học máy lượng tử để đọc báo cáo?**
- *Trả lời:*
  - (Vấn đề) Phần khó của GreenScan là đọc bảng, số và tiếng Việt trong báo cáo hàng trăm trang.
  - (Nguyên lý) QNLP (DisCoCat, lambeq) mới chạy được câu ngắn và tập dữ liệu nhỏ; khảo sát 2025 nói lĩnh vực bị giới hạn nghiêm trọng bởi phần cứng NISQ.
  - (GreenScan) Dùng BM25, bge-m3, mô hình nhỏ chạy ngoại tuyến và bộ so tất định. Trên tập ngoài mẫu sạch 87 ca (nhãn bạc), mọi mô hình cho 0 kết luận sai, độ phủ 0,115–0,253. Nút thắt là đọc bảng (HPG trang 39), không phải thứ QNLP giải.
  - (Giới hạn) Độ phủ còn thấp; nhãn là nhãn bạc, chưa có nhãn người.
- *Vặn:* "Còn tương lai?" → "Khi có máy chịu lỗi thì có thể; hôm nay chưa có bằng chứng QNLP xử lý được văn bản dài."
- *Bẫy:* hứa dùng QNLP; gọi độ phủ là "accuracy".

**Q7. Lượng tử đe dọa bảo mật dữ liệu tài chính; GreenScan có tính tới không?**
- *Trả lời:*
  - (Vấn đề) Máy lượng tử đủ lớn phá được RSA và ECC; dữ liệu bị thu hôm nay có thể bị giải mã sau này.
  - (Nguyên lý) NIST đã chuẩn hoá mật mã hậu lượng tử (FIPS 203/204/205, 08/2024). QĐ 21/2026/QĐ-TTg xếp "công nghệ an ninh mạng và lượng tử" thành một nhóm công nghệ chiến lược.
  - (GreenScan) Giảm bề mặt rủi ro bằng cách chạy ngoại tuyến: tài liệu nội bộ (loại B) và mật nghề nghiệp (loại C) không rời máy của đơn vị.
  - (Giới hạn) Mã hoá đường truyền là việc của hạ tầng; GreenScan chưa có gì riêng về PQC.
- *Vặn:* "Vậy đây là chỗ có lượng tử?" → "Đây là rủi ro lượng tử, không phải tính năng lượng tử của sản phẩm."
- *Bẫy:* nói GreenScan "kháng lượng tử".

**Q8. ISSA 5000 là gì, khi nào có hiệu lực? GreenScan có thay kiểm toán viên được không?**
- *Trả lời:*
  - (Vấn đề) Báo cáo bền vững được đảm bảo ngày càng nhiều, nhưng cách làm còn phân mảnh.
  - (Nguyên lý) ISSA 5000 của IAASB là chuẩn nền toàn cầu cho dịch vụ đảm bảo thông tin bền vững, áp dụng cho mọi khung báo cáo, cả đảm bảo hạn chế lẫn hợp lý. Chuẩn có hiệu lực cho kỳ bắt đầu từ 15/12/2026, tức năm 2027 với doanh nghiệp năm dương lịch; ISAE 3410 sẽ bị rút.
  - (GreenScan) Không thay kiểm toán viên. GreenScan là công cụ sàng lọc trước: mỗi tuyên bố kèm trích trang, và hệ thống biết lúc nào phải nhường người. Báo cáo đảm bảo là một nguồn bằng chứng ngoài; về nguyên tắc chỉ tính cho đúng các chỉ tiêu được đảm bảo (cần kiểm mã đã giới hạn phạm vi chưa).
  - (Giới hạn) Chưa thấy văn bản Việt Nam chấp nhận ISSA 5000.
- *Vặn:* "Đảm bảo hạn chế khác hợp lý thế nào?" → "Hạn chế cho kết luận dạng phủ định, đánh giá rủi ro ở cấp thuyết minh; hợp lý cho ý kiến khẳng định, đánh giá rủi ro ở cấp cơ sở dẫn liệu."
- *Bẫy:* nói "GreenScan đạt chuẩn ISSA 5000" hay "GreenScan cung cấp đảm bảo hạn chế".

**Q9. Việt Nam đã bắt buộc IFRS S1/S2 chưa? GreenScan kiểm theo chuẩn nào?**
- *Trả lời:*
  - (Vấn đề) Doanh nghiệp niêm yết chịu nhiều chuẩn cùng lúc.
  - (Nguyên lý) Khung bắt buộc hiện là TT 96/2020, Phụ lục IV mục 6 (sửa bởi TT 68/2024, TT 18/2025, TT 08/2026). Chúng em chưa tìm thấy văn bản ràng buộc thời điểm áp dụng IFRS S1/S2. S&P đếm được 35 khu vực pháp lý đã áp dụng ISSB tới 22/07/2026.
  - (GreenScan) Dùng TT 96 làm bộ chỉ tiêu kỳ vọng. Dùng khái niệm của IFRS S2 và GHG Protocol (Scope, ranh giới, năm gốc) làm thuộc tính bắt buộc của tuyên bố số. Không chấm "tuân thủ ISSB".
  - (Giới hạn) Lớp pháp lý chưa vận hành: lượt HPG ngày 22/10 có 0 quy tắc áp được trên 156 tuyên bố.
- *Vặn:* "Sao không theo ISSB cho hiện đại?" → "Chấm theo một khung chưa bắt buộc dễ dẫn tới quy kết sai; ISSB được dùng làm từ điển khái niệm."
- *Bẫy:* nói "Việt Nam áp dụng ISSB từ 2026".

**Q10. Dự thảo thay TT 96 đổi gì? Nếu doanh nghiệp không công bố một chỉ tiêu thì GreenScan kết luận gì?**
- *Trả lời:*
  - (Vấn đề) Thiếu chỉ tiêu có thể là che giấu, cũng có thể chỉ là chưa có dữ liệu.
  - (Nguyên lý) Dự thảo (VNS 29/10/2026) có phụ lục riêng về báo cáo phát triển bền vững; bỏ chỉ tiêu phải nêu lý do và kế hoạch cho kỳ sau, thực chất là "công bố hoặc giải trình". BCTN nộp trong 120 ngày; công bố tiếng Anh chậm nhất từ 01/01/2028.
  - (GreenScan) Chỉ tiêu bị thiếu trong báo cáo không thành CONTRADICTED; đó là "chưa đủ bằng chứng về phạm vi". Chỉ khi doanh nghiệp tuyên bố đã có một thứ (ví dụ "đã được xác nhận xanh") mà nguồn thẩm quyền cho thấy không có, hệ thống mới xét bác bỏ, và vẫn qua người soát. Khi dự thảo thành thông tư, cần tách "thiếu có giải trình" (trích đoạn giải trình) với "thiếu không giải trình" (đưa người soát).
  - (Giới hạn) Vẫn là dự thảo; chưa xác nhận được dự thảo có tham chiếu ISSB.
- *Vặn:* "Giải trình yếu thì sao?" → "Chất lượng giải trình là phán đoán của người soát, không phải của máy."
- *Bẫy:* nói dự thảo đã được ban hành, hoặc nói dự thảo "theo ISSB".

**Q11. QĐ 21/2025 và QĐ 46/2026 khác nhau thế nào? GreenScan có xác nhận dự án xanh không?**
- *Trả lời:*
  - (Vấn đề) Tuyên bố "dự án xanh" được dùng để huy động vốn ưu đãi.
  - (Nguyên lý)
    - QĐ 21/2025/QĐ-TTg (hiệu lực 22/08/2025) quy định tiêu chí môi trường và việc xác nhận dự án thuộc danh mục phân loại xanh cho trái phiếu xanh và tín dụng xanh.
    - QĐ 46/2026 (hiệu lực 01/11/2026) lập chế độ thứ hai cho dự án xanh, dự án tuần hoàn và khung ESG; tỉnh công bố danh mục mỗi 30/6 và 31/12.
    - Cả hai chấp nhận xác nhận của tổ chức độc lập đạt ISO/IEC 17029 hoặc theo VSAE/ISAE 3000.
  - (GreenScan) Không xác nhận dự án. Hệ thống chỉ kiểm tuyên bố "đã được xác nhận" có văn bản hoặc có tên trong danh mục hay không.
  - (Giới hạn) Danh mục tỉnh đợt đầu chưa có; quy tắc QĐ 21 vẫn là bản nháp chưa gắn với phụ lục cụ thể.
- *Vặn:* "Không đạt tiêu chí phân loại xanh có phải là nói dối?" → "Không; chỉ là không đủ điều kiện ưu đãi theo tiêu chí hiện hành."
- *Bẫy:* nói "QĐ 21" mà không kèm năm, vì QĐ 21/2026 là danh mục công nghệ chiến lược.

**Q12. Chỉ thị EU 2024/825 là gì? Liên quan gì đến doanh nghiệp Việt?**
- *Trả lời:*
  - (Vấn đề) Tuyên bố chung chung và "trung hòa carbon nhờ tín chỉ" xuất hiện tràn lan.
  - (Nguyên lý) Chỉ thị 2024/825 sửa luật bảo vệ người tiêu dùng EU và áp dụng từ 27/09/2026. Nó cấm hẳn: tuyên bố chung chung không chứng minh được hiệu quả môi trường xuất sắc được công nhận; nhãn bền vững không qua chứng nhận; tuyên bố cho cả sản phẩm khi chỉ đúng một phần; tuyên bố trung hòa khí hậu dựa trên bù trừ. Cam kết tương lai phải có kế hoạch và chuyên gia độc lập kiểm tra.
  - (GreenScan) Các điểm này ánh xạ thẳng vào mẫu tuyên bố đã có: "thân thiện môi trường", "trung hòa nhờ tín chỉ", "net zero 2050". Doanh nghiệp xuất khẩu B2C vào EU có thể dùng như một danh sách kiểm.
  - (Giới hạn) Chỉ thị áp cho giao dịch với người tiêu dùng EU, không áp cho BCTN gửi nhà đầu tư; 8 nước chưa nội luật hoá.
- *Vặn:* "GreenScan có kết luận vi phạm luật EU không?" → "Không; chỉ gắn cờ các mẫu tuyên bố rủi ro."
- *Bẫy:* nói "EU cấm greenwashing trong báo cáo thường niên".

**Q13. Green Claims Directive đã có hiệu lực chưa?**
- *Trả lời:*
  - (Vấn đề) Văn bản này hay bị nhầm với Chỉ thị 2024/825.
  - (Nguyên lý) Đề xuất từ 03/2023; Nghị viện thông qua lập trường 12/03/2024; ngày 20/06/2025 Ủy ban tuyên bố ý định rút, sau đó nói chưa rút chính thức; tới 07/2026 tương lai vẫn bất định.
  - (GreenScan) Không dùng làm căn cứ. Chỉ dùng như lập luận thiết kế: "chứng minh trước khi tuyên bố" giống evidence-first.
  - (Giới hạn) Chưa kiểm hồ sơ thủ tục trên Legislative Observatory của Nghị viện EU.
- *Vặn:* "Vậy EU có bắt chứng minh trước không?" → "Hiện EU kiểm soát qua 2024/825 và luật về hành vi thương mại không lành mạnh; chưa có thủ tục xác minh trước bắt buộc."
- *Bẫy:* nói Green Claims Directive là luật.

**Q14. Anh, Úc, Mỹ xử lý greenwashing thế nào? GreenScan học được gì?**
- *Trả lời:*
  - (Vấn đề) Chi phí của tuyên bố sai đang tăng.
  - (Nguyên lý)
    - Anh: từ 06/04/2025, CMA tự ra quyết định và phạt tới 10% doanh thu toàn cầu.
    - Úc: Mercer A$11,3 triệu (08/2024), Vanguard A$12,9 triệu (09/2024), Active Super A$10,5 triệu (03/2025), Clorox A$8,25 triệu (04/2025).
    - Mỹ: Green Guides bản 2012 vẫn hiệu lực; đợt rà soát mở từ 12/2022 chưa xong.
  - (GreenScan) Ba vụ quỹ ở Úc đều là tuyên bố "loại trừ" hoặc "sàng lọc" bị một phản ví dụ bác bỏ. Muốn kiểm tuyên bố loại trừ thì cần dữ liệu danh mục nắm giữ; một phản ví dụ có nguồn là đủ để gắn cờ.
  - (Giới hạn) GreenScan V1 chưa nhận dữ liệu danh mục; Việt Nam chưa có án lệ tương tự.
- *Vặn:* "Còn vụ Clime?" → "Không phải greenwashing. ASIC 25-254MR chỉ là điều tra sơ bộ về tài liệu công bố của một quỹ thu nhập."
- *Bẫy:* nêu Clime như vụ greenwashing; quy đổi ra VNĐ mà không kèm tỷ giá và ngày.

**Q15. Dùng LLM đám mây có vi phạm Luật Bảo vệ dữ liệu cá nhân không?**
- *Trả lời:*
  - (Vấn đề) Báo cáo có tên và chức vụ lãnh đạo; LLM đám mây đặt ở nước ngoài.
  - (Nguyên lý) Luật 91/2025 (hiệu lực 01/01/2026) coi xử lý trên nền tảng ở nước ngoài là chuyển dữ liệu xuyên biên giới, phải có hồ sơ đánh giá tác động. Vi phạm về chuyển xuyên biên giới bị phạt tới 5% doanh thu năm trước. NĐ 330/2026 (hiệu lực 19/08/2026) là nghị định xử phạt.
  - (GreenScan) Mặc định chạy ngoại tuyến. Chỉ tài liệu công khai mới được chạy trên cloud; tài liệu nội bộ và mật nghề nghiệp chỉ chạy tại chỗ; giao diện báo khi dữ liệu rời máy. Khoá FPT lỗi từ 31/10, nên demo hiện chạy hoàn toàn ngoại tuyến.
  - (Giới hạn) Ý "dữ liệu đã công khai hợp pháp được miễn đánh giá" là suy luận của đội, chưa có luật sư xác nhận.
- *Vặn:* "Còn Groq miễn phí?" → "Chỉ dùng cho báo cáo công khai, người dùng tự đăng ký, vì gói miễn phí có thể lưu dữ liệu."
- *Bẫy:* nói "báo cáo công khai thì không có dữ liệu cá nhân".

**Q16. GreenScan thuộc mức rủi ro nào theo Luật Trí tuệ nhân tạo?**
- *Trả lời:*
  - (Vấn đề) Luật 134/2025/QH15 (hiệu lực 01/03/2026) chia ba mức rủi ro; nhà cung cấp tự phân loại; mức trung bình và cao phải có hồ sơ; tiêu chí nằm ở NĐ 142/2026.
  - (Nguyên lý) Mức rủi ro xét theo tác động tới quyền, an toàn, lĩnh vực sử dụng và phạm vi ảnh hưởng.
  - (GreenScan) GreenScan hỗ trợ người soát chuyên môn và không tự ra quyết định về cá nhân. Mô hình không tự tạo SUPPORTED hay CONTRADICTED (chốt `llm_stance_decisive: false`). Mỗi lượt chạy có manifest và nhật ký chỉ ghi thêm. Giả thuyết của đội: không thuộc nhóm rủi ro cao.
  - (Giới hạn) Chưa lập hồ sơ tự phân loại; chưa đối chiếu danh mục rủi ro cao.
- *Vặn:* "Nếu quy kết sai một doanh nghiệp thì sao?" → "Vì thế mới có hàng đợi người soát và quyền abstain."
- *Bẫy:* nói "đã được xếp rủi ro thấp".

**Q17. Sửa đổi IFRS S2 tháng 12/2025 ảnh hưởng gì tới việc kiểm số KNK?**
- *Trả lời:*
  - (Vấn đề) Hai số CO2e khác nhau có thể do phương pháp, không phải do thực tế thay đổi.
  - (Nguyên lý) Sửa đổi ngày 11/12/2025 (hiệu lực 01/01/2027): được giới hạn hạng mục 15 vào phát thải tài trợ; được dùng hệ phân loại khác GICS; làm rõ miễn trừ GHG Protocol theo khu vực; thêm miễn trừ về hệ số GWP.
  - (GreenScan) Chỉ so hai số CO2e khi cùng phương pháp, phạm vi và bộ GWP. Ví dụ 1.000 t CH4 là 28.000 tCO2e theo AR5 nhưng 29.800 tCO2e theo AR6 (hóa thạch), lệch 6,4% chỉ do hệ số. Khác phương pháp thì kết luận "không so được", không phải "mâu thuẫn".
  - (Giới hạn) Chưa kiểm `comparison_policy` đã xét bộ GWP hay chưa; cần xem mã trước khi nói.
- *Vặn:* "Ngân hàng Việt Nam được miễn KNK?" → "TT 96 miễn chỉ tiêu 6.1–6.3 cho bốn ngành tài chính; theo ISSB họ vẫn phải công bố phát thải tài trợ. Đây là hai khung khác nhau."
- *Bẫy:* lẫn hai khung.

**Q18. Tên quỹ ESG ở EU phải đạt 80%; GreenScan kiểm được không?**
- *Trả lời:*
  - (Vấn đề) Tên quỹ là tuyên bố xanh ngắn nhất.
  - (Nguyên lý) Theo hướng dẫn của ESMA, từ 21/11/2024 với quỹ mới và 21/05/2025 với quỹ cũ, ít nhất 80% khoản đầu tư phải đáp ứng đặc tính môi trường/xã hội; tên có chữ môi trường, tác động hay bền vững phải áp loại trừ PAB. Tới giữa 05/2025 khoảng 19% quỹ trong diện đã đổi tên.
  - (GreenScan) Đây là kiểu "quy tắc cứng có ngưỡng" mà kiến trúc Rules decide làm tốt nhất, nhưng cần dữ liệu danh mục; V1 chưa có.
  - (Giới hạn) Chưa thấy quy định tương tự ở Việt Nam [CHƯA XÁC MINH].
- *Vặn:* "Vậy khi nào làm được?" → "Có thể thêm một gói quy tắc khi có dữ liệu nắm giữ."
- *Bẫy:* nói GreenScan đã kiểm quỹ.

**Q19. Luật thay đổi liên tục; GreenScan cập nhật thế nào, kết quả cũ ra sao?**
- *Trả lời:*
  - (Vấn đề) Chỉ trong 09–11/2026 đã có QĐ 46/2026 có hiệu lực, Chỉ thị 2024/825 bắt đầu áp dụng, và dự thảo thay TT 96.
  - (Nguyên lý) Luật là dữ liệu có ngày hiệu lực; mỗi kết luận phải gắn với phiên bản luật.
  - (GreenScan) Registry ghi `effective_from` và `effective_to`, có hàm `in_force_on(date)`. Có hai chế độ: tuân thủ lịch sử (luật lúc công bố) và đối chiếu chính sách hiện hành. Mỗi lượt có manifest. Quy tắc chỉ được gắn khi người phụ trách pháp lý ký vào trường `reviewed_by`.
  - (Giới hạn) Cập nhật thủ công; registry có 12 văn bản; hiện chưa quy tắc nào áp được trên HPG.
- *Vặn:* "Ai chịu trách nhiệm nếu luật cập nhật chậm?" → "Người phụ trách pháp lý của đơn vị dùng; vì thế mỗi kết luận ghi phiên bản registry."
- *Bẫy:* nói "cập nhật luật tự động".

**Q20. Sao không làm tối ưu danh mục bằng lượng tử như gợi ý của Nhóm 4?**
- *Trả lời:*
  - (Vấn đề) Tối ưu danh mục là bài mẫu của lượng tử trong tài chính.
  - (Nguyên lý) Bài Markowitz với biến nhị phân viết được thành QUBO và đã có nhiều demo. Nhưng thêm nó vào GreenScan là đổi sang bài toán khác.
  - (GreenScan) Đầu ra của GreenScan có thể làm ràng buộc cho bài danh mục của bên khác (ví dụ loại doanh nghiệp có tuyên bố bị bác bỏ, có nguồn), nhưng đội không làm phần đó.
  - (Giới hạn) Đây là hướng mở, không phải tính năng.
- *Vặn:* "Thế có phải bỏ lỡ cơ hội?" → "Chúng em ưu tiên làm tới nơi một bài toán thật."
- *Bẫy:* hứa tích hợp tối ưu danh mục lượng tử.

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ và điều không được nói

### 5.1 So với `02_PHAP_LY_VIET_NAM.md` (viết 05–06/10)

| Điểm trong tài liệu đội | Hiện trạng 04/11 | Cần sửa |
|---|---|---|
| §5: dự thảo thay TT 96 "ngày 25/09/2026, lấy ý kiến tới 07/10/2026; tham chiếu ISSB/IFC, 4 trụ cột, công bố hoặc giải trình; hạn 120 ngày" [SECONDARY] | Đã xác nhận: phụ lục phát triển bền vững riêng; giải trình khi bỏ chỉ tiêu; hạn 120 ngày; tiếng Anh chậm nhất 01/01/2028; vẫn là dự thảo tới 29/10. **Chưa xác nhận:** tham chiếu ISSB/IFC, "4 trụ cột", ngày 25/09, hạn 07/10 (bản v4 ngày 13/10 cũng ghi cổng chính thức không nhắc các chi tiết này) | Bỏ "ISSB/IFC, 4 trụ cột"; thêm mốc tiếng Anh 2028 |
| §5: "Văn bản thay QĐ 21/2025 … [UNVERIFIED]" | Chưa có văn bản thay thế; có QĐ 46/2026 chạy song song, hiệu lực 01/11/2026 (đã ghi ở bản v4, chưa đưa vào 02_PHAP_LY) | Thêm QĐ 46/2026 |
| §5: "Green Claims Directive ở trạng thái 'Blocked' [VERIFIED]" | Chính xác hơn: Ủy ban tuyên bố ý định rút ngày 20/06/2025; chưa thấy văn bản rút chính thức; tới 07/2026 tương lai vẫn bất định | Sửa câu chữ |
| §5: "Directive 2024/825 áp dụng từ 27/09/2026" | Nay đã áp dụng; tới 27/10/2026 còn 8 nước chưa nội luật hoá; Ủy ban mở thủ tục vi phạm với 20 nước ngày 28/05/2026 | Cập nhật trạng thái |
| §5: "Việt Nam chưa có lộ trình ISSB chính thức [UNVERIFIED]" | Vẫn đúng theo tìm kiếm ngày 04/11. Thêm số 35 khu vực đã áp dụng (S&P, 22/07/2026) | Giữ, thêm số |
| §6: "Luật TTNT 134/2025; NĐ 142/2026 [UNVERIFIED hiệu lực]" | Luật hiệu lực 01/03/2026 (nhiều nguồn thứ cấp); NĐ 142/2026 hiệu lực 01/05/2026 (bản v4) | Điền ngày hiệu lực |
| §6: chưa có nghị định xử phạt về dữ liệu cá nhân | NĐ 330/2026/NĐ-CP, hiệu lực 19/08/2026 | Thêm |
| §6: "phạt tới 5% doanh thu với vi phạm chuyển xuyên biên giới" | Đúng phạm vi; nhưng không được nói như mức phạt chung (mức cố định khác, tới 3 tỷ đồng theo nguồn thứ cấp) | Giữ, ghi rõ phạm vi |
| §1: QĐ 21/2025 hiệu lực 22/08/2025 | VnEconomy (03/04/2026) ghi "02/8/2025" | Giữ 22/08/2025 theo bản ký; ngày 02/08 chỉ cách ngày ký 29 ngày, ngắn hơn khoảng 45 ngày thường thấy với QĐ của Thủ tướng [KIẾN THỨC NỀN], nên nhiều khả năng là lỗi báo |
| Không có | Trùng số hiệu: QĐ 21/2025 (phân loại xanh) và QĐ 21/2026 (danh mục công nghệ chiến lược, có nhóm lượng tử) | Luôn ghi đủ năm |

R9 không kiểm lại các mục EU CBAM, Omnibus (EU) 2026/470, NĐ 110/2026, NĐ 37/2026, NĐ 87/2026 nêu trong ghi chú 13/10.

### 5.2 Số cũ trong QA bank (20/09) và `GreenScan_100_Cau_BGK.txt` so với kết quả 31/10–01/11

- **"233 test · 21 bẫy verdict · 4/4 case thật · HPG 210 claim, CONTRADICTED 4% · 11 văn bản pháp lý · ~4.200 điều khoản · gold adjudicated 5 claim" đều là số cũ.** Số mới:
  - Lượt HPG ngày 22/10: 156 tuyên bố, gồm 153 PARTIAL, 2 SUPPORTED, 1 INSUFFICIENT; hàng đợi 9/172.
  - 0 quy tắc pháp lý áp được trên 156/156 tuyên bố.
  - Registry có 12 văn bản (06/10).
  - Nhãn người: 0/88 cặp, 0/79 câu.
  - GS-Bench v1: 193 ca nhãn bạc.
  - Ngoài mẫu sạch (87 ca): độ phủ của luật 0,011, các mô hình 0,115–0,253; precision 1,0.
  - Bộ đọc Q4 trong sản phẩm: độ phủ 0,080, 0 kết luận sai.
  - Chế độ cloud hỏng (khoá 401).
- **Q97** "QUBO prototype chỉ sau 25/10 nếu vào Chung kết": tới 04/11 vẫn chưa có dòng mã nào. Không được nói "đã chạy" hay "đã có benchmark".
- **Q93** "Trên simulator p = 2–5 là thực tế cho 30 qubit": statevector 30 qubit cần khoảng 16 GiB, trong khi laptop của đội có 15,6 GB và đang gần đầy. Nên nói "khoảng 20–25 qubit trên laptop; 30 qubit cần GPU hoặc mô phỏng kiểu MPS".
- **Q83** "thuật toán lấy cảm hứng lượng tử (simulated annealing)": SA là thuật toán cổ điển, lấy cảm hứng từ vật lý thống kê. "Lấy cảm hứng lượng tử" đúng hơn là ủ lượng tử mô phỏng hoặc phân nhánh mô phỏng. Q88 đã nói "không gọi SA là quantum"; Q83 cần sửa cho khớp.
- **Q89** "5.000 doanh nghiệp × 200 claim": bài chọn bằng chứng tách được theo từng tuyên bố, nên quy mô lớn chỉ là nhiều bài 30 biến chạy song song. Phải nêu ràng buộc ghép (ngân sách chung, bằng chứng dùng chung), nếu không lập luận về quy mô không đứng được.
- **Phụ lục "đừng nói"**: dòng "registry 11 văn bản" nay là 12 văn bản. Với "1 rule draft chưa bind", thêm F5: 0 quy tắc áp được trên HPG.
- QA bank ghi assurance được coi là nguồn ngoài và đủ điều kiện cho SUPPORTED. Cần kiểm mã xem có giới hạn theo đúng chỉ tiêu được đảm bảo không (mục 2.1).

### 5.3 Mâu thuẫn giữa các nguồn ngoài

- Ngày hiệu lực QĐ 21/2025: 22/08/2025 (bản ký, luatvietnam) hay 02/08/2025 (VnEconomy).
- Số khu vực áp dụng ISSB: 35 (S&P, 07/2026); 36 (IFRS 2025, gồm cả khu vực đang tiến hành); "70+" (UAO, không tin cậy vì tính cả EU vốn dùng ESRS).
- Green Claims Directive: một số blog viết "đã rút chính thức 06/2025", trong khi ghi chú 12/2025 nói Ủy ban xác nhận chưa rút chính thức.
- Clorox: A$8,25 triệu, tương đương khoảng US$5,19 triệu (Reuters qua iTiger). Phải nói rõ đơn vị tiền.
- HSBC: con số là "tới 34%", là cải thiện tương đối và đo bằng AUC (fi-desk). Các báo khác viết lỏng hơn.
- Dự thảo QĐ 46 trên VnEconomy tự mâu thuẫn: nêu "7 lĩnh vực" ở một chỗ và "8 lĩnh vực" ở chỗ khác.

### 5.4 Điều không được nói

- "GreenScan dùng/ứng dụng lượng tử", "QAOA của nhóm", "đã chạy trên máy lượng tử hoặc simulator", "quantum advantage", "quantum-enhanced RAG".
- "Simulated annealing là thuật toán lượng tử".
- "HSBC chứng minh lượng tử vượt cổ điển"; "lượng tử nhanh hơn 34%".
- "QNLP sẽ thay LLM".
- "GreenScan đạt chuẩn ISSA 5000 hoặc IFRS S2", "GreenScan thực hiện đảm bảo".
- "Việt Nam bắt buộc ISSB từ năm X".
- "Thông tư mới về ESG đã ban hành"; "dự thảo áp dụng ISSB".
- "QĐ 21" mà không ghi năm.
- "GreenScan xác nhận dự án xanh".
- "Green Claims Directive là luật EU"; "luật EU áp cho báo cáo thường niên".
- "Clime bị phạt vì greenwashing".
- "GreenScan thuộc nhóm rủi ro thấp theo Luật AI" (chưa tự phân loại).
- "Dữ liệu công khai thì không phải dữ liệu cá nhân".
- Số tiền phạt quy đổi ra VNĐ mà không kèm tỷ giá và ngày.
- Mọi số cũ nêu ở mục 5.2.
