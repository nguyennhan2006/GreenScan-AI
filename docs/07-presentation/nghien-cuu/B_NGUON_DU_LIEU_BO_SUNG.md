# B. Nguồn dữ liệu bổ sung để kiểm chứng tuyên bố môi trường (GreenScan)

- **Ngày lập:** 31/10/2026. **Hạn chốt:** 10/11/2026 (còn 10 ngày).
- **Phạm vi:** nguồn ngoài báo cáo thường niên và báo cáo tài chính, dùng để kiểm chứng tuyên bố môi trường hoặc phát hiện greenwashing. Ưu tiên doanh nghiệp phát thải cao tại Việt Nam (thép, xi măng, điện, hóa chất).
- **Phương pháp:** khoảng 25 lượt tìm web và 11 lượt mở trang. Không tải dataset. Chỉ ghi URL xuất hiện trong kết quả tìm kiếm hoặc đã mở. Nội dung nào lấy từ nguồn thứ cấp (công ty luật, báo chí) được ghi rõ. Mục ghi "chưa xác minh" nghĩa là chưa kiểm được trong lượt này (URL, phạm vi, điều khoản sử dụng hoặc bằng chứng sử dụng).
- **Ký hiệu ưu tiên:** P0 = bằng chứng độc lập cho doanh nghiệp phát thải cao tại Việt Nam, dùng được trước 10/11/2026. P1 = nên có, hoặc là tiền lệ và chuẩn để thiết kế. P2 = tham khảo, ít liên quan đến Việt Nam.

---

## 1. Bảng tóm tắt

| # | Nguồn | Khu vực | Kiểm chứng được | Truy cập (định dạng, phí) | Bằng chứng đã dùng | Đối ứng Việt Nam và tình trạng | Ưu tiên |
|---|---|---|---|---|---|---|---|
| 1 | EU ETS (EUTL / Union Registry, CITL) | EU | Phát thải xác minh Scope 1 của cơ sở ETS | Viewer EEA tổng hợp, xuất Excel miễn phí; dữ liệu cấp cơ sở: chưa xác minh cách tải | Chưa xác minh | Chưa có ETS vận hành đã xác minh | P2 |
| 2 | E-PRTR / IED (EEA Industrial Emissions Portal) | EU | Phát thải và chuyển giao chất ô nhiễm theo cơ sở | CSV/TXT/SQL, miễn phí | Chưa xác minh | Không có tương đương đã kiểm | P2 |
| 3 | CSRD/ESRS và EU Taxonomy | EU | Mục tiêu, KPI, cấu trúc báo cáo để đối chiếu | Văn bản công khai; Omnibus I đã ban hành (nguồn thứ cấp) | Chưa xác minh | Thông tư 96/2020/TT-BTC (báo cáo của công ty đại chúng) | P1 |
| 4 | ESMA và cơ quan quốc gia (greenwashing) | EU | Tên quỹ ESG, công bố bền vững | Văn bản ESMA; dữ liệu vụ việc theo nước: chưa xác minh | Có ít vụ việc chính thức (nguồn thứ cấp) | Chưa xác minh (SSC) | P2 |
| 5 | EPA GHGRP / FLIGHT | Mỹ | Phát thải theo cơ sở, theo ngành | Web FLIGHT miễn phí; trạng thái chương trình còn biến động | Chưa xác minh | Không có | P2 |
| 6 | EPA TRI | Mỹ | Thải hóa chất độc theo cơ sở | TRI Toolbox, miễn phí | Chưa xác minh | Không có | P2 |
| 7 | EPA ECHO | Mỹ | Hồ sơ tuân thủ, thanh tra, xử phạt liên bang | Bulk download, web services, miễn phí | Chưa có vụ cụ thể | Chưa có CSDL xử phạt công khai đã xác minh (xem VN-5) | P1 |
| 8 | SEC (nhận xét về khí hậu) | Mỹ | Yêu cầu làm rõ tuyên bố khí hậu trong hồ sơ | EDGAR: chưa xác minh | Chưa xác minh | Không | P2 |
| 9 | FTC Green Guides và vụ thực thi | Mỹ | Chuẩn chứng minh tuyên bố môi trường | Văn bản FTC: chưa xác minh đường dẫn đúng | Vụ về nhựa phân hủy sinh học (nguồn thứ cấp) | Không | P1 |
| 10 | ASA rulings (quảng cáo) | Anh | Tuyên bố carbon neutral, net zero, bù trừ | Trang rulings miễn phí, chưa có bộ lọc môi trường | Hướng dẫn ASA 2023 | Chưa xác minh | P1 |
| 11 | CMA Green Claims Code và DMCC | Anh | Khung sáu nguyên tắc; phạt có hiệu lực từ 06/04/2025 | gov.uk, miễn phí | Hướng dẫn chuỗi cung ứng 22/01/2026 (thứ cấp) | Chưa xác minh (luật tiêu dùng VN) | P1 |
| 12 | NGER (Clean Energy Regulator) | Úc | Phát thải, năng lượng theo tập đoàn; theo nhà máy điện | Công bố CER, miễn phí | Chưa xác minh | Không | P2 |
| 13 | ASIC và ACCC (greenwashing) | Úc | Tiền lệ phạt tuyên bố ESG | Công bố tòa án/ASIC | Vanguard A$12,9 triệu; Mercer A$11,3 triệu (2024) | Không | P1 |
| 14 | Climate TRACE | Toàn cầu | Phát thải ước tính theo tài sản (thép, xi măng, điện) | Bulk CSV, API beta, CC BY 4.0, cập nhật hàng tháng | Chưa xác minh | Chưa xác minh độ phủ VN (cần kiểm đầu tiên) | **P0** |
| 15 | GEM Global Steel Plant Tracker | Toàn cầu | Công suất, phương pháp sản xuất, trạng thái nhà máy | Download data, miễn phí; điều khoản chưa xác minh | Chưa xác minh | Chưa xác minh có nhà máy thép VN | **P0** |
| 16 | GEM Global Cement and Concrete Tracker | Toàn cầu | Công suất, trạng thái nhà máy xi măng | Download data | Chưa xác minh | Chưa xác minh | **P0** |
| 17 | GEM Global Coal Plant Tracker | Toàn cầu | Nhà máy than, lộ trình đóng | Chưa xác minh URL | Chưa xác minh | Chưa xác minh | P1 |
| 18 | CDP | Toàn cầu | Phản hồi khí hậu và nước của công ty | Dữ liệu phản hồi có phí; Open Data chỉ thành phố, bang | Chưa xác minh | Chưa xác minh công ty VN | P1 |
| 19 | SBTi Target Dashboard | Toàn cầu | Mục tiêu đã phê duyệt hoặc cam kết | Tải CSV/xls, cập nhật hàng tuần | Chưa xác minh | Chưa xác minh số công ty VN | P1 |
| 20 | InfluenceMap (LobbyMap) | Toàn cầu | Vận động hành lang về khí hậu | Điều khoản tải chưa xác minh | Chưa xác minh | Không | P2 |
| 21 | Environmental Claims (Stammbach 2023) | NLP | Phát hiện câu tuyên bố môi trường | Hugging Face; dùng thương mại cần liên hệ tác giả | ACL 2023; EnClaim 2024 | Không (tiếng Anh) | P1 |
| 22 | Climate-FEVER | NLP | Xác minh tuyên bố khí hậu bằng bằng chứng | arXiv, TFDS/Hugging Face | Benchmark chuẩn (arXiv) | Không | P1 |
| 23 | ClimaText | NLP | Phân loại câu liên quan khí hậu | arXiv, trang UZH | Benchmark (arXiv) | Không | P2 |
| 24 | ClimRetrieve | NLP | Truy xuất trong báo cáo bền vững | Chưa xác minh giấy phép | EMNLP 2024 | Không | P1 |
| 25 | ClimateBERT (mô hình, dữ liệu) | NLP | Mô hình nền cho phân loại | Hugging Face | Có (nhiều công trình, chưa xác minh cụ thể) | Không | P2 |
| 26 | Bộ dữ liệu ESG-NLI | NLP | Chưa xác định | Chưa tìm được tên bộ cụ thể | Chưa xác minh | Không | P2 |
| VN-1 | ĐTM và giấy phép môi trường | Việt Nam | Điều kiện phát thải được phép | Chưa tìm được cổng công khai | Không | Chưa xác minh | P1 |
| VN-2 | Báo cáo hiện trạng và báo cáo môi trường định kỳ | Việt Nam | Mô tả nguồn thải, hiện trạng | Chưa xác minh cổng | Không | Chưa xác minh | P2 |
| VN-3 | Danh mục cơ sở phát thải KNK (QĐ 13/2024/QĐ-TTg) | Việt Nam | Phạm vi bắt buộc kiểm kê, 2.166 cơ sở | Văn bản công khai | Văn bản pháp lý | Đây là danh mục VN | **P0** |
| VN-4 | Quan trắc môi trường tự động, liên tục | Việt Nam | Nồng độ, lưu lượng khí thải thực tế | Chưa xác minh cổng công khai | Bài báo mô tả hệ thống | Đây là dữ liệu VN | **P0** (rủi ro truy cập) |
| VN-5 | Xử phạt hành chính về môi trường | Việt Nam | Vi phạm, mức phạt | Chưa xác minh CSDL công khai | Thống kê 12.045 vụ (thứ cấp) | Đây là dữ liệu VN | P1 |
| VN-6 | Báo cáo phát triển bền vững và công bố thông tin trên HOSE, HNX, UPCoM | Việt Nam | Mục tiêu và KPI môi trường (năng lượng, nước, chất thải) | Cổng công bố thông tin: chưa xác minh URL | Thông tư 96/2020 | Đây là nguồn tuyên bố cần kiểm | P1 |
| VN-7 | Trái phiếu xanh, tín dụng xanh và ý kiến bên thứ hai | Việt Nam | Khung sử dụng vốn xanh | Trang phát hành: chưa xác minh | Vietcombank (S&P "Medium Green") | Thiếu danh mục phân loại xanh (nguồn thứ cấp) | P1 |
| VN-8 | Verra / Gold Standard dự án Việt Nam | Việt Nam | Tín chỉ carbon, dự án | Verra registry công khai | Dự án Việt Nam trên Verra | Có công khai (Verra) | P2 |
| VN-9 | EVN dữ liệu điện tái tạo | Việt Nam | Tỷ lệ tái tạo, sản lượng | Chưa xác minh | Chưa xác minh | Chưa xác minh | P1 |

---

## 2. Mô tả theo nguồn

### 2.1 Liên minh châu Âu

**1. EU ETS (EUTL / Union Registry, CITL)**
- Nội dung: phát thải xác minh và phân bổ hạn ngạch theo cơ sở ETS. Viewer của EEA tổng hợp theo nước, loại hoạt động và năm; bản trích xuất Union Registry mới nhất ghi ngày 01/07/2026.
- Truy cập: [EEA ETS Data Viewer](https://www.eea.europa.eu/data-and-maps/dashboards/emissions-trading-viewer-1), xuất Crosstab sang Excel, miễn phí. Dữ liệu cấp cơ sở nằm ở CITL/Union Registry, cách tải chưa xác minh.
- Bằng chứng: chưa tìm được vụ việc hoặc bài báo cụ thể (chưa xác minh).
- Việt Nam: chưa xác minh. Có thông tin thứ cấp về kế hoạch phân bổ hạn ngạch cho khoảng 150 cơ sở lớn ([VnEconomy](https://vneconomy.vn/se-phan-bo-han-ngach-phat-thai-khi-nha-kinh-cho-150-co-so-doanh-nghiep-phat-thai-lon-nhat.htm)).
- Ưu tiên: P2. Dùng làm chuẩn so sánh phương pháp đo, không có doanh nghiệp VN trong phạm vi.

**2. E-PRTR / IED (EEA Industrial Emissions Portal)**
- Nội dung: phát thải không khí và nước theo cơ sở, theo ngành và chất ô nhiễm, từ 2007 đến 2024 (E-PRTR) và từ 2017 đến 2024 (IED), theo nguồn thứ cấp.
- Truy cập: [trang tải dữ liệu](https://industry.eea.europa.eu/industrial-emissions/dataset) và [dashboard](https://industry.eea.europa.eu/industrial-emissions/dashboards), miễn phí, định dạng CSV, TXT, SQL.
- Bằng chứng: chưa xác minh trích dẫn cụ thể. Có ấn phẩm [A decade of industrial pollution data](https://www.eea.europa.eu/publications/a-decade-of-industrial-pollution-data) (phân tích xu hướng, không phải kiểm chứng tuyên bố).
- Việt Nam: không có bản tương đương đã kiểm. Quan trắc VN phân tán giữa nhiều hệ thống.
- Ưu tiên: P2.

**3. CSRD / ESRS và EU Taxonomy**
- Nội dung: khung báo cáo (ESRS) và phân loại xanh (Taxonomy, Quy định (EU) 2020/852). Đây là chuẩn để đối chiếu cấu trúc tuyên bố, không phải nguồn bằng chứng độc lập.
- Trạng thái: theo nguồn thứ cấp, Omnibus I đã được Hội đồng EU thông qua ngày 24/02/2026, đăng Công báo ngày 26/02/2026 là Directive (EU) 2026/470. Ngưỡng mới: trên 1.000 nhân viên và trên 450 triệu EUR doanh thu, áp dụng từ năm tài chính bắt đầu sau 01/01/2027. Ngày thông qua ESRS sửa đổi chưa thống nhất giữa các nguồn (chưa xác minh). Nguồn: [CMS](https://cms.law/en/lux/legal-updates/final-adoption-of-omnibus-i-directive-simplifying-csrd-and-csddd).
- Việt Nam: Thông tư 96/2020/TT-BTC có hiệu lực từ 01/01/2021 ([văn bản](https://thuvienphapluat.vn/van-ban/Chung-khoan/Circular-96-2020-TT-BTC-providing-guidelines-on-disclosure-of-information-on-securities-market-460833.aspx?tab=1)). Dự thảo thay thế đang lấy ý kiến, tình trạng chưa xác minh.
- Ưu tiên: P1 (khung đối chiếu).

**4. ESMA và cơ quan quốc gia (greenwashing)**
- Nội dung: hướng dẫn ESMA về tên quỹ có thuật ngữ ESG hoặc bền vững, áp dụng từ 21/11/2024 theo nguồn thứ cấp ([tóm tắt](https://netzerocompare.com/policies/esma-guidelines-on-funds-names-using-esg-or-sustainability-related-terms)). ESMA đặt tấn công greenwashing là ưu tiên 2026–2028 ([Ropes & Gray](https://www.ropesgray.com/en/insights/viewpoints/102k049/esma-2026-2028-tackling-greenwashing-remains-key-priority)).
- Bằng chứng: theo nguồn thứ cấp, ít vụ thực thi chính thức. Chưa xác minh vụ của AMF, BaFin, AFM.
- Việt Nam: chưa xác minh cơ quan đối ứng.
- Ưu tiên: P2.

### 2.2 Hoa Kỳ

**5. EPA GHGRP / FLIGHT**
- Nội dung: phát thải khí nhà kính theo cơ sở và ngành. Công cụ tra cứu [FLIGHT](https://ghgdata.epa.gov/flight) (trang mở được nhưng nội dung tải chưa xác minh).
- Trạng thái: EPA đề xuất bãi bỏ nghĩa vụ với 46 nhóm nguồn (tháng 9/2025, [fact sheet](https://www.epa.gov/system/files/documents/2025-09/reconsideration-of-ghgrp-proposal-fact-sheet.pdf)). Theo nguồn thứ cấp, hạn nộp năm báo cáo 2025 đã gia hạn từ 31/03/2026 sang 30/10/2026, và có thể gia hạn tiếp sang 10/03/2027 (chưa xác minh trên Federal Register). Tìm kiếm không thấy quy định bãi bỏ cuối cùng.
- Việt Nam: không có tương đương.
- Ưu tiên: P2.

**6. EPA TRI (Toxics Release Inventory)**
- Nội dung: thải và chuyển giao hóa chất độc theo cơ sở. Trang chính: [TRI Program](https://www.epa.gov/toxics-release-inventory-tri-program), với công cụ tải tại đường dẫn `/tri-toolbox` (chưa xác minh đầy đủ).
- Bằng chứng: chưa xác minh.
- Việt Nam: không có tương đương.
- Ưu tiên: P2.

**7. EPA ECHO**
- Nội dung: hồ sơ tuân thủ, thanh tra, vụ thực thi dân sự và hình sự liên bang.
- Truy cập: miễn phí. [Data downloads](https://echo.epa.gov/tools/data-downloads), [web services](https://echo.epa.gov/tools/web-services) (đã mở trang chính, xác nhận các đường dẫn).
- Bằng chứng: chưa xác minh vụ cụ thể.
- Việt Nam: chưa có CSDL xử phạt công khai đã xác minh (xem VN-5).
- Ưu tiên: P1 (mô hình để đối chiếu hồ sơ tuân thủ và vi phạm).

**8. SEC (nhận xét về khí hậu)**
- Nội dung: thư nhận xét của SEC về báo cáo khí hậu trong hồ sơ công ty. Chưa xác minh URL hay số lượng thư.
- Ghi chú (kiến thức nền, chưa xác minh trong lượt này): SEC đã ngừng bảo vệ quy định công bố khí hậu năm 2025.
- Ưu tiên: P2.

**9. FTC Green Guides và vụ thực thi**
- Nội dung: chuẩn chứng minh tuyên bố môi trường. FTC mở đợt lấy ý kiến cập nhật năm 2023 (hạn 21/02/2023). Tình trạng bản cuối chưa xác minh.
- Vụ việc: theo nguồn thứ cấp, 5 trong 6 vụ FTC về tuyên bố nhựa phân hủy sinh học. Ngày và số liệu chưa xác minh.
- Lưu ý: đường dẫn trang Green Guides thử trả về 404, cần tìm lại đường dẫn chính thức.
- Ưu tiên: P1 (tiêu chuẩn chứng minh).

### 2.3 Vương quốc Anh

**10. ASA rulings**
- Nội dung: phán quyết quảng cáo. Trang [rulings](https://www.asa.org.uk/codes-and-rulings/rulings.html) tìm kiếm được theo từ khóa, ngày, chủ đề; không có bộ lọc môi trường rõ ràng (kiểm tra 31/10/2026).
- Hướng dẫn: [Carbon neutral and net zero claims](https://www.asa.org.uk/news/carbon-neutral-and-net-zero-claims-where-are-we-now.html), theo đó cần giải thích cơ sở tuyên bố và tách phần cắt giảm thực tế khỏi phần bù trừ.
- Vụ việc: quảng cáo Lufthansa bị cấm (ngày chưa xác minh, nguồn thứ cấp). Chưa tìm được phán quyết 2026 về net zero.
- Ưu tiên: P1.

**11. CMA Green Claims Code và DMCC Act**
- Nội dung: [Green Claims Code](https://www.gov.uk/government/publications/green-claims-code-making-environmental-claims), công bố 20/09/2021. Trang này là hướng dẫn, không phải luật, và không tóm tắt sáu nguyên tắc (xem nguồn gốc để trích).
- Hiệu lực: theo nguồn thứ cấp, từ 06/04/2025 CMA có quyền phạt tới 300.000 bảng hoặc 10% doanh thu ([KPMG](https://kpmg.com/uk/en/insights/legal/new-consumer-enforcement-regime.html)). Hướng dẫn chuỗi cung ứng ngày 22/01/2026 ([Ashurst](https://www.ashurst.com/en/insights/greenwatch-greenwashing-in-the-spotlight-regulatory-risks-across-the-supply-chain)). Chưa tìm được vụ phạt CMA năm 2026.
- Việt Nam: chưa xác minh luật bảo vệ người tiêu dùng VN và điều khoản về tuyên bố môi trường.
- Ưu tiên: P1 (khung kiểm tra).

### 2.4 Úc

**12. NGER (Clean Energy Regulator)**
- Nội dung: phát thải, năng lượng theo tập đoàn; phát thải và sản lượng theo nhà máy điện có phát điện là hoạt động chính. Doanh nghiệp báo cáo trước 31/10 hằng năm, CER công bố bản trích xuất trước 28/02 năm sau.
- Truy cập: [ví dụ dữ liệu ngành điện 2021–22](https://cer.gov.au/markets/reports-and-data/nger-reporting-data-and-registers/electricity-sector-emissions-and-generation-data-2021-22), miễn phí. Có thể bị sửa đổi.
- Bằng chứng: chưa xác minh.
- Việt Nam: không có tương đương.
- Ưu tiên: P2.

**13. ASIC và ACCC (greenwashing)**
- Vanguard: ASIC thắng tại Tòa án Liên bang, phạt 12,9 triệu AUD ([Bird & Bird](https://cm.twobirds.com/en/disputes-plus/shared/insights/2024/australia/asics-second-win-for-greenwashing-civil-penalty-proceedings-a-record-penalty-against-vanguard)).
- Mercer: 11,3 triệu AUD, phê duyệt ngày 02/08/2024 (nguồn thứ cấp).
- Active Super: tòa kết luận vi phạm 06/2024, mức phạt chưa xác minh.
- ACCC: theo nguồn 2024, chưa khởi kiện dân sự về greenwashing. Chưa xác minh trạng thái năm 2026.
- Tòa án tuyên bố không sai lệch: Santos (2026) được xét là không gây hiểu nhầm khi đọc trong ngữ cảnh ([HRLC](https://www.hrlc.org.au/case-summaries/net-zero-not-misleading/), chưa xác minh bản án gốc).
- Ưu tiên: P1 (tiền lệ phạt và lập luận bảo vệ).

### 2.5 Nguồn toàn cầu độc lập

**14. Climate TRACE**
- Nội dung: phát thải ước tính theo tài sản (nhà máy, lò, nhà máy điện) cho nhiều ngành, cập nhật hàng tháng. Bản mới nhất có dữ liệu đến tháng 03/2026 (nguồn thứ cấp).
- Truy cập: [climatetrace.org/data](https://www.climatetrace.org/data), miễn phí, CC BY 4.0, gói tải theo nước hoặc ngành, API đang beta (dùng lưu lượng thấp). Mirror Zenodo: chưa xác minh bản.
- Bằng chứng: chưa xác minh bài báo.
- Việt Nam: chưa xác minh độ phủ tài sản thép, xi măng, điện tại VN. Đây là việc kiểm đầu tiên.
- Ưu tiên: **P0** (nếu độ phủ VN đạt).

**15. GEM Global Steel Plant Tracker**
- Nội dung: 1.293 nhà máy thép ở 91 nước, công suất từ 0,5 Mt/năm, gồm vận hành, đang xây, ngừng, đóng cửa. Trường: công suất, phương pháp sản xuất, sở hữu, số lao động. Bản tháng 03/2026, cập nhật quý tháng 06 và 09/2026 ([trang](https://globalenergymonitor.org/projects/global-steel-plant-tracker/)).
- Truy cập: nút "Download data", miễn phí; điều khoản sử dụng chưa xác minh.
- Bằng chứng: chưa xác minh.
- Việt Nam: chưa xác minh có các nhà máy thép VN trong tracker.
- Ưu tiên: **P0**.

**16. GEM Global Cement and Concrete Tracker**
- Nội dung: nhà máy xi măng và bê tông, gồm đề xuất, đang xây, nghỉ hoặc đóng từ năm 2018 đến 2021 (theo mô tả thứ cấp). Có bảng tóm tắt [summary tables](https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/summary-tables/) và "Download Data".
- Bằng chứng: chưa xác minh. Việt Nam: chưa xác minh.
- Ưu tiên: **P0**.

**17. GEM Global Coal Plant Tracker**
- Nội dung: nhà máy than, lộ trình đóng cửa. URL chưa xác minh trong lượt này.
- Ưu tiên: P1.

**18. CDP**
- Nội dung: phản hồi khí hậu, nước, rừng của công ty.
- Truy cập: [trang dữ liệu](https://www.cdp.net/en/data). Bộ phản hồi công ty có phí (giấy phép, [điều khoản](https://www.cdp.net/en/data-licenses)). Open Data miễn phí chỉ gồm thành phố, bang, khu vực ([data.cdp.net](https://data.cdp.net/)).
- Bằng chứng: chưa xác minh. Việt Nam: chưa xác minh số công ty VN có phản hồi.
- Ưu tiên: P1 (phụ thuộc giấy phép).

**19. SBTi Target Dashboard**
- Nội dung: công ty và tổ chức tài chính có mục tiêu khoa học đã phê duyệt hoặc đã cam kết. Tải theo công ty hoặc theo mục tiêu, cập nhật hàng tuần, tạm dừng cuối năm ([trang](https://sciencebasedtargets.org/target-dashboard)).
- Lưu ý: số liệu công ty khác nhau giữa các nguồn, cần kiểm trên trang chính thức. Tên trường dữ liệu bản tải hiện nay chưa xác minh.
- Việt Nam: chưa xác minh số công ty VN.
- Ưu tiên: P1 (dùng để kiểm mục tiêu "net zero" của công ty VN nếu có trên dashboard).

**20. InfluenceMap**
- Nội dung: [LobbyMap, FinanceMap, Carbon Majors](https://influencemap.org/) (vận động hành lang, điểm khí hậu). Điều khoản tải dữ liệu chưa xác minh.
- Ưu tiên: P2 (không kiểm chứng trực tiếp tuyên bố phát thải).

### 2.6 Bộ dữ liệu nghiên cứu (NLP)

**21. Environmental Claims (Stammbach và cộng sự, 2023)**
- Nội dung: phát hiện câu tuyên bố môi trường (nhị phân). 2.117 mẫu huấn luyện, 265 dev, 265 test. Nguồn: báo cáo thường niên, báo cáo bền vững, bản ghi họp báo cáo doanh thu.
- Truy cập: [Hugging Face](https://huggingface.co/datasets/climatebert/environmental_claims), dùng thương mại cần liên hệ tác giả.
- Bằng chứng: [ACL 2023](https://aclanthology.org/2023.acl-short.91) và [EnClaim 2024](https://aclanthology.org/2024.climatenlp-1.9).
- Việt Nam: không có (tiếng Anh).
- Ưu tiên: P1 (khởi tạo bộ phân loại câu tuyên bố).

**22. Climate-FEVER**
- Nội dung: 1.535 tuyên bố khí hậu, mỗi tuyên bố có 5 câu bằng chứng từ Wikipedia (theo nguồn thứ cấp). Nhãn: SUPPORTS, REFUTES, NOT_ENOUGH_INFO, DISPUTED (catalog TFDS); một bài báo khác chỉ ghi 3 nhãn.
- Truy cập: [arXiv 2012.00614](https://arxiv.org/pdf/2012.00614); [TFDS/Hugging Face](https://tensorflow.org/datasets/community_catalog/huggingface/climate_fever).
- Bằng chứng: công bố chuẩn cho kiểm chứng tuyên bố khí hậu.
- Việt Nam: không có.
- Ưu tiên: P1 (mẫu kiến trúc kiểm chứng tuyên bố, không phải dữ liệu VN).

**23. ClimaText**
- Nội dung: câu liên quan đến khí hậu từ Wikipedia, 10-K và tuyên bố web. Nhãn -1, 0, 1. Một tập gán nhãn tự động, các tập khác gán nhãn người.
- Truy cập: [arXiv 2012.00483](https://arxiv.org/pdf/2012.00483); [trang UZH](https://www.sustainablefinance.uzh.ch/en/research/climate-fever/climatext.html). Bản Zenodo chưa xác minh.
- Ưu tiên: P2.

**24. ClimRetrieve**
- Nội dung: 30 báo cáo bền vững và 16 câu hỏi khí hậu, hơn 8.500 cặp câu hỏi-nguồn-đáp án. Dùng để đánh giá truy xuất.
- Truy cập: [SFI](https://www.sfi.ch/en/publications/n-24-89-climretrieve-a-benchmarking-dataset-for-information-retrieval-from-corporate-climate-disclosures). Giấy phép dữ liệu chưa xác minh.
- Bằng chứng: EMNLP 2024, DOI 10.18653/v1/2024.emnlp-main.969.
- Ưu tiên: P1 (thiết kế truy xuất báo cáo bền vững cho GreenScan).

**25. ClimateBERT (mô hình và dữ liệu)**
- Nội dung: mô hình nền cho văn bản khí hậu, ví dụ [climatebert/environmental-claims](https://huggingface.co/climatebert/environmental-claims) (Apache-2.0 theo model card). Dữ liệu riêng: chưa xác minh.
- Ưu tiên: P2.

**26. Bộ dữ liệu ESG-NLI**
- Chưa tìm được tên bộ cụ thể trong lượt này. Chưa xác minh. Không nêu tên để tránh bịa.
- Ưu tiên: P2.

### 2.7 Việt Nam

**VN-1. ĐTM và giấy phép môi trường**
- Căn cứ: Luật Bảo vệ môi trường 2020 (sửa đổi bởi luật 2025 về nông nghiệp và môi trường, nguồn thứ cấp). Giấy phép môi trường phải có trước khi vận hành thử nghiệm xử lý chất thải.
- Công khai: chưa tìm được cổng công khai ĐTM và giấy phép của Bộ Nông nghiệp và Môi trường (trước đây là Bộ Tài nguyên và Môi trường, MONRE). Chưa xác minh.
- Hướng xử lý: nếu không có cổng, yêu cầu cung cấp thông tin theo Luật Tiếp cận thông tin (số hiệu chưa xác minh trong lượt này).
- Ưu tiên: P1.

**VN-2. Báo cáo hiện trạng và báo cáo môi trường định kỳ**
- Chưa xác minh cổng hoặc tên báo cáo cụ thể. Báo cáo cấp tỉnh thường có trên cổng của Sở TN&MT (chưa xác minh).
- Ưu tiên: P2.

**VN-3. Danh mục cơ sở phát thải khí nhà kính (Quyết định 13/2024/QĐ-TTg)**
- Căn cứ: Nghị định 06/2022/NĐ-CP (ngưỡng phát thải 3.000 tCO2e/năm trở lên, theo nguồn thứ cấp). Quyết định 13/2024/QĐ-TTg ký ngày 13/08/2024, có hiệu lực từ 01/10/2024, gồm 2.166 cơ sở, thay danh mục 01/2022 (1.912 cơ sở).
- Nguồn: [thuvienphapluat (bản tiếng Anh)](https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Decision-13-2024-QD-TTg-gas-emitting-facilities-required-to-develop-greenhouse-gas-inventory-630930.aspx); [ACC Group (tiếng Việt)](https://accgroup.vn/quyet-dinh-13-2024-qd-ttg-danh-muc-linh-vuc-co-so-phat-thai-khi-nha-kinh-phai-thuc-hien-kiem-ke-khi-nha-kinh-cap-nhat).
- Ghi chú: danh mục 2026 dự kiến 2.705 cơ sở (nguồn thứ cấp, chưa xác minh đã ban hành). Báo cáo kiểm kê từng cơ sở chưa thấy công khai (chưa xác minh).
- Ưu tiên: **P0** (xác định phạm vi và đối chiếu cơ sở bắt buộc kiểm kê).

**VN-4. Quan trắc môi trường tự động, liên tục**
- Nội dung: trung tâm tích hợp dữ liệu quốc gia do Trung tâm Quan trắc môi trường miền Bắc vận hành; phần mềm EnviSoft dùng chung từ 2018; Quyết định 224/QĐ-TTg (07/03/2024) về quy hoạch quan trắc 2021–2030 (theo nguồn thứ cấp). Mô tả: [Nhân Dân](https://nhandan.vn/kiem-soat-o-nhiem-qua-phan-mem-quan-ly-so-lieu-quan-trac-tu-dong-post454095.html), [VietnamPlus](https://www.vietnamplus.vn/nang-cao-chat-luong-hieu-qua-he-thong-quan-trac-va-canh-bao-moi-truong-post1141414.vnp).
- Công khai: một số khu công nghiệp thí điểm công khai kết quả và thông tin doanh nghiệp. Cổng quốc gia chính thức chưa xác minh (trang cem.gov.vn xuất hiện trong kết quả, chưa xác minh là cổng công khai).
- Ưu tiên: **P0** nếu truy cập được. Rủi ro cao vì chưa xác minh.

**VN-5. Xử phạt hành chính về môi trường**
- Căn cứ: Nghị định 179/2013/NĐ-CP ([bản tiếng Anh](https://thuvienphapluat.vn/van-ban/EN/Vi-pham-hanh-chinh/Decree-No-179-2013-ND-CP-administrative-violations-in-the-domain-of-environmental-protection/225698/tieng-anh.aspx)) yêu cầu công bố thông tin vi phạm của cơ sở.
- Thống kê: 12.045 vụ xử phạt từ khi Nghị định 45/2022/NĐ-CP có hiệu lực đến tháng 10/2024 ([VietnamFinance](https://vietnamfinance.vn/hon-12000-vu-vi-pham-moi-truong-bi-xu-phat-383-ty-dong-d123917.html), nguồn thứ cấp).
- CSDL công khai từng quyết định: chưa xác minh. Có gợi ý Hệ tri thức Việt số hóa (dulieu.itrithuc.vn), chưa xác minh.
- Ưu tiên: P1.

**VN-6. Báo cáo phát triển bền vững và công bố thông tin trên HOSE, HNX, UPCoM, SSC**
- Căn cứ: Thông tư 96/2020/TT-BTC có hiệu lực từ 01/01/2021 (thay Thông tư 155/2015/TT-BTC). Bộ Tài chính đang lấy ý kiến dự thảo thay thế (chưa xác minh tình trạng).
- Cổng: theo nguồn thứ cấp, HOSE sẽ chuyển công bố sang hệ thống của sàn (ngày áp dụng chưa xác minh). URL cổng HOSE, HNX, UPCoM và SSC: chưa xác minh trong lượt này.
- Ưu tiên: P1 (đây là nguồn tuyên bố cần đối chiếu, không phải bằng chứng độc lập).

**VN-7. Trái phiếu xanh, tín dụng xanh và ý kiến bên thứ hai**
- Ví dụ: khung trái phiếu xanh của Vietcombank, được GGGI hỗ trợ kỹ thuật và S&P đánh giá "Medium Green" trong ý kiến bên thứ hai ([VnBusiness](https://vnbusiness.vn/vietcombank-thong-bao-ban-hanh-khung-trai-phieu-xanh.html), nguồn thứ cấp).
- Pháp lý: Nghị định 08/2022/NĐ-CP (Điều 154, ưu đãi theo danh mục xanh). Năm 2024, VAFIE kêu gọi ban hành danh mục phân loại xanh ([Nhà Đầu Tư](https://nhadautu.vn/chuyen-de-xuat-cua-vafie-ve-tin-dung-xanh-trai-phieu-xanh-den-cac-bo-nganh-d85615.html)). Tình trạng ban hành chưa xác minh.
- Ưu tiên: P1.

**VN-8. Verra và Gold Standard (dự án Việt Nam)**
- Verra: có dự án bếp cải tiến, tiết kiệm năng lượng và nước sạch, ví dụ [tiết kiệm năng lượng](https://verra.org/projects_public_comm/grouped-projects-for-vietnam-energy-efficiency), [bếp cải tiến giai đoạn 2](https://verra.org/projects_public_comm/grouped-projects-for-viet-nam-cookstove-program-phase-2-2/), [nước sạch trường học](https://verra.org/projects_public_comm/grouped-projects-for-safe-drinking-water-for-schools-in-viet-nam/).
- Dự án điện tái tạo chưa thấy trong kết quả. Gold Standard chưa kiểm.
- Ưu tiên: P2.

**VN-9. EVN dữ liệu điện tái tạo**
- Chưa tìm được nguồn trong lượt này. Chưa xác minh.
- Ưu tiên: P1 (cần để kiểm tỷ lệ tái tạo của công ty điện).

---

## 3. Kế hoạch thu thập 7 ngày

Hạn 10/11/2026 còn 10 ngày, nên kế hoạch dồn vào P0 và các nguồn kiểm được ngay. Mỗi bước ghi phiên bản, ngày tải và điều khoản sử dụng vào docs của dự án.

1. **Ngày 1 (31/10–01/11): Climate TRACE.** Tải gói dữ liệu Việt Nam (CSV) từ [climatetrace.org/data](https://www.climatetrace.org/data), lọc các ngành thép, xi măng và điện. Ghi phiên bản, ngày phát hành và giấy phép CC BY 4.0. Kiểm xem có tài sản VN nào không.
2. **Ngày 1–2: GEM Global Steel Plant Tracker.** Tải "Download data" bản tháng 09/2026 (V1) từ [trang GEM](https://globalenergymonitor.org/projects/global-steel-plant-tracker/). Lọc Việt Nam, ghi công suất, chủ sở hữu, trạng thái. Đọc điều khoản sử dụng trước khi dùng thương mại.
3. **Ngày 2: GEM Global Cement and Concrete Tracker.** Làm tương tự bước 2, đối chiếu với danh sách doanh nghiệp xi măng VN.
4. **Ngày 2–3: Quyết định 13/2024/QĐ-TTg.** Lấy phụ lục 2.166 cơ sở từ văn bản chính thức (Công báo hoặc cổng pháp luật), đối chiếu với các doanh nghiệp mục tiêu. Dùng bản thứ cấp chỉ để tham chiếu.
5. **Ngày 3–4: Quan trắc tự động.** Tìm cổng công khai chính thức (chưa có URL). Thử truy cập dữ liệu của 10 cơ sở thép, xi măng và nhiệt điện lớn. Nếu không truy cập được, ghi rõ "không công khai" và soạn yêu cầu cung cấp thông tin.
6. **Ngày 4–5: Báo cáo bền vững trên sàn.** Tải báo cáo phát triển bền vững và báo cáo thường niên (mục năng lượng, nước, chất thải, mục tiêu) của 10–15 doanh nghiệp thép, xi măng và điện. Đây là tuyên bố cần đối chiếu.
7. **Ngày 5–6: SBTi Target Dashboard.** Tải bản tải theo công ty từ [dashboard](https://sciencebasedtargets.org/target-dashboard), lọc Việt Nam. Ghi số công ty và tên các công ty có mục tiêu đã phê duyệt.
8. **Ngày 6: Environmental Claims (Hugging Face).** Chỉ tải để benchmark nội bộ nếu còn thời gian, sau khi kiểm điều khoản thương mại với tác giả. Không dùng để kết luận về doanh nghiệp VN.

---

## 4. Ghi chú quan trọng

- Không có doanh nghiệp VN trong EU ETS, E-PRTR, TRI, ECHO, NGER. Các nguồn này chỉ dùng làm chuẩn phương pháp hoặc tiền lệ.
- Trạng thái GHGRP (Mỹ), Omnibus I (EU) và các dự thảo thông tư VN cần kiểm lại trước khi trích dẫn trong báo cáo cuối.
- Các nhận định lấy từ nguồn thứ cấp (công ty luật, báo chí) được đánh dấu. Trước khi đưa vào báo cáo chính thức, cần đối chiếu với văn bản gốc.
