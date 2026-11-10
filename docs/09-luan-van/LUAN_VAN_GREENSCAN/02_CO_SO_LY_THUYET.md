# Chương 2. Cơ sở lý thuyết

*Chương này trả lời câu hỏi: những khái niệm, quy định, chuẩn mực và kết quả nghiên cứu nào cần có để hiểu và biện minh cho các lựa chọn thiết kế ở chương 3. Chương đi từ đối tượng (tẩy xanh, pháp luật, chuẩn mực đảm bảo), qua công cụ (NLP, kiểm chứng, truy xuất, số học, mô hình ngôn ngữ lớn), đến phương pháp đo và giới hạn của công nghệ lượng tử. Mục 2.16 ghép từng phần lý thuyết với năm câu hỏi nghiên cứu.*

Quy ước trích dẫn: (Tác giả, năm) trong bài; danh mục cuối chương ghi tác giả, năm, tên, nơi công bố và URL khi ghi chú nguồn trong repo có. Kết quả của người khác được nêu đúng theo số trong ghi chú đọc tài liệu `docs/10-chung-ket-2026-11/doc-tai-lieu/R1–R9` hoặc tài liệu tri thức trong `docs/08-knowledge/`; chỗ nào ghi chú đánh dấu [CHƯA XÁC MINH] thì giữ nguyên dấu.

---

## 2.1 Tẩy xanh: định nghĩa

Không có một định nghĩa duy nhất; mỗi định nghĩa nhấn một khía cạnh khác nhau, và sự khác biệt ấy chính là lý do luận văn chọn đo "mức đủ bằng chứng" thay vì đo "tẩy xanh".

**Bảng 2.1.** Các định nghĩa tẩy xanh và điều chúng hàm ý cho thiết kế hệ thống.

| Nguồn | Nội dung chính | Hàm ý cho GreenScan |
| --- | --- | --- |
| Delmas & Burbano (2011) | Tẩy xanh là giao của hai hành vi: hiệu quả môi trường kém và truyền thông tích cực về hiệu quả môi trường. Ma trận 2×2 (hiệu quả xanh hay nâu; lên tiếng hay im lặng) cho bốn ô: *vocal green*, *silent green*, *greenwashing*, *silent brown* | Hệ thống đo khoảng cách giữa lời nói và bằng chứng đã công bố, không đo hiệu quả môi trường thật. Ô *silent brown* không có tuyên bố nên hệ thống không thấy |
| Marquis, Toffel & Zhou (2016) | Doanh nghiệp công bố chọn lọc các tác động tương đối lành tính, tạo ấn tượng minh bạch nhưng che hiệu quả thật; mẫu 4.750 công ty ở 45 nước | Chủ động tìm bằng chứng trái chiều, kiểm danh mục chỉ tiêu bắt buộc |
| Seele & Gatti (2017) | Tẩy xanh là một cáo buộc từ bên ngoài. Bốn loại: tẩy xanh (gây hiểu nhầm và bị cáo buộc), tẩy xanh bị cáo buộc oan, tẩy xanh tiềm năng (gây hiểu nhầm nhưng chưa bị cáo buộc), không tẩy xanh | Hệ thống đứng trước cáo buộc: chỉ tạo tín hiệu rủi ro "tiềm năng" kèm bằng chứng |
| ESMA, EBA, EIOPA (2024) | Thực hành trong đó các tuyên bố, hành động hoặc truyền thông về bền vững "không phản ánh rõ ràng và công bằng hồ sơ bền vững thực chất" của tổ chức, sản phẩm hay dịch vụ tài chính; cố ý hoặc vô ý | Không cần chứng minh ý định mới gọi là rủi ro; công cụ cũng không nói được về ý định |

Các nguồn học thuật ở bảng này được ghi chú R3 đọc qua tóm tắt hoặc nguồn thứ cấp (riêng abstract của Lyon & Montgomery được kiểm), nên luận văn chỉ dùng chúng làm khung khái niệm, không dùng số liệu bên trong.

**Ba lý do không dùng nhãn "tẩy xanh" để kết luận.** (i) Định nghĩa của ESAs coi cả vô ý là tẩy xanh, nên công cụ nhìn văn bản không xác định được. (ii) Theo Seele & Gatti, tẩy xanh là cáo buộc, không phải thuộc tính của văn bản. (iii) Luật Việt Nam không định nghĩa thuật ngữ này (mục 2.4). Ngoài ra, kết cục pháp lý các vụ không một chiều: Eni được hủy phạt năm 2024, CMA đóng hồ sơ Unilever năm 2024 mà "không đưa ra quan điểm", ASA không xử vi phạm Shell năm 2025, và vụ kiện tập thể Lizama & Doten v. H&M bị bác (theo nguồn thứ cấp, ngày 12/05/2023).

****Rủi ro tẩy xanh khác kết luận vi phạm.** Theo ghi chú R3 (mục 2.4), rủi ro tẩy xanh do công cụ rồi người soát đưa ra, xét một tuyên bố cùng bằng chứng bằng phép thử đủ hay thiếu theo năm thuộc tính và so số tất định, chỉ dựa trên tài liệu đã công bố, doanh nghiệp không có phần phản biện, và đầu ra là năm trạng thái cùng điểm 0–100 "không phải kết luận pháp lý". Kết luận vi phạm do cơ quan có thẩm quyền (ASA, ASIC và tòa liên bang, SEC, AGCM) đưa ra cho một quảng cáo hay hành vi cụ thể trong một pháp quyền, bằng phép thử "ấn tượng tổng thể" và "người tiêu dùng hay nhà đầu tư hợp lý", có quyền buộc cung cấp dữ liệu nội bộ (danh mục nắm giữ của Mercer, độ phủ sàng lọc của Vanguard), doanh nghiệp được trả lời và kháng cáo. Hệ thống chỉ làm phần đầu.

## 2.2 Phân loại tẩy xanh

### 2.2.1 Bảy tội của TerraChoice và mười hai tính chất của ESAs

TerraChoice phân thành bảy "tội": đánh đổi ẩn, không chứng minh, mơ hồ, nhãn giả, không liên quan, cái ác nhỏ hơn, nói dối (bản 2007 có sáu, bản 2009 thêm "nhãn giả"; số liệu khảo sát 2009 chỉ có từ nguồn thứ cấp, số 2007 và 2010 [CHƯA XÁC MINH] nên không dùng). Báo cáo tiến độ 2023 của ESAs liệt kê mười hai tính chất gây hiểu nhầm: tuyên bố rỗng, không nhất quán, không liên quan, sai sự thật, hình ảnh gợi ý, thuật ngữ ESG gợi ý, công bố chọn lọc, bỏ sót, mơ hồ, so sánh không công bằng, không có chứng minh, thông tin lỗi thời.

### 2.2.2 Hai mươi mốt mẫu hình và mức kiểm được

Luận văn dùng danh mục 21 mẫu hình hợp nhất từ bảy tội, mười hai tính chất và hồ sơ vụ việc (`docs/08-knowledge/01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md`). Mỗi mẫu hình được xếp theo việc máy có kiểm được từ chính tài liệu hay không: *có* (kiểm chủ yếu từ chính tài liệu), *một phần* (phát hiện được nhưng kết luận cần nguồn ngoài hoặc người), *không* (cần dữ liệu ngoài văn bản). Bảng 2.3 trích các mẫu hình then chốt.

**Bảng 2.3.** Một số mẫu hình tẩy xanh và khả năng kiểm bằng máy (ngày đối chiếu mã 06/10/2026).

| # | Mẫu hình | Tín hiệu trong văn bản | Máy kiểm được | Tương ứng TerraChoice |
| --- | --- | --- | --- | --- |
| 6 | Đánh đổi ẩn, công bố chọn lọc | Chỉ báo cáo Scope 1; thiếu nước, tuân thủ | Một phần | Đánh đổi ẩn |
| 7 | Sai sự thật, mâu thuẫn số liệu | Số khác bảng hay trang khác, khác nguồn ngoài | Một phần (nội bộ: có) | Nói dối |
| 9 | Trung hòa nhờ bù trừ | "trung hòa carbon" đi cùng "tín chỉ" | Có (phát hiện) | |
| 10 | Cam kết tương lai không kế hoạch | "Net Zero 2050" không năm gốc, không mốc trung gian | Có (checklist) | |
| 13 | Lệch phạm vi | "100% năng lượng tái tạo" chỉ ở một nhà máy | Một phần | |
| 20 | Greenhushing | Năm ngoái công bố, năm nay im lặng | Không (trong một kỳ) | |

Ghi chú R3 rút ra: hệ thống mạnh nhất ở mẫu 12 (mốc so sánh) và 13 (lệch phạm vi), loại lỗi máy làm tốt hơn người vì chỉ cần so con số; không làm được bằng văn bản các mẫu 16 (hình ảnh), 20, 21. Hai mươi mốt mẫu hình là bản đồ để nói trung thực hệ thống *phủ* những gì, không phải danh sách cam kết.

## 2.3 Án lệ và bài học cho kiểm chứng cấp tuyên bố

Kho vụ việc nội bộ có 32 vụ đã kiểm (`docs/08-knowledge/04_AN_LE_VA_BAI_HOC.md`) và `data/legal_cases/` (297 tài liệu, thu thập 08/08/2026). Mỗi bản ghi mang `legal_strength` (A: tòa phạt; B: SEC dàn xếp không thừa nhận; C: phán quyết ASA hoặc thông báo phạt ASIC), còn `greenwashing_label` luôn để trống. Bảng 2.4 chọn vài vụ minh họa.

**Bảng 2.4.** Vụ việc tiêu biểu và thủ tục kiểm tra tương ứng.

| Vụ | Cơ quan, ngày | Điều bị bác hoặc được chấp nhận | Thủ tục kiểm tra rút ra |
| --- | --- | --- | --- |
| KLM | Tòa Amsterdam, 20/03/2024 | 15/19 phát ngôn gây hiểu lầm; chỉ pha khoảng 0,5% SAF | So quy mô biện pháp với tác động mà câu chữ ngụ ý |
| Katjes | Tòa Tối cao Đức (BGH), 27/06/2024 | "klimaneutral" nhờ bù trừ; thuật ngữ mơ hồ phải được giải thích ngay trong quảng cáo | Phần giải thích phải ở cùng trang: giá trị của trích dẫn cấp trang |
| Shell UK 2023 | ASA, 07/06/2023, upheld một phần | Từng số đúng (78.000 hộ dùng điện tái tạo) nhưng ấn tượng tổng thể bỏ sót tỷ trọng các-bon thấp | Số đúng vẫn có thể gây hiểu nhầm |
| Shell UK 2025 | ASA, 09/04/2025, not upheld | Có chữ trên màn hình: 68% đầu tư dầu khí, 23% các-bon thấp, 9% phi năng lượng | Qualifier định lượng đặt cạnh tuyên bố làm hạ ưu tiên soát |
| Mercer | Tòa Liên bang Úc, 02/08/2024, A$11,3 triệu | Vẫn nắm 15 công ty hóa thạch dù tuyên bố loại trừ | Tuyên bố loại trừ chỉ cần một phản ví dụ |
| Lizama & Doten v. H&M | E.D. Mo., số 4:22-cv-01170, nộp 03/11/2022; bị bác 12/05/2023 (nguồn thứ cấp) | H&M chưa nói sản phẩm "environmentally friendly"; tuyên bố có định nghĩa kèm (≥ 50% vật liệu bền vững hơn) | Kiểm đúng câu doanh nghiệp viết, không kiểm câu diễn giải |

Từ các vụ này, ghi chú R3 và tri thức nền rút ra các bài học chi phối thiết kế: bằng chứng thường nằm ngay trong tài liệu của chính doanh nghiệp, nên kiểm nhất quán nội bộ bằng phép tất định là việc đầu tiên; tuyên bố định lượng là mỏ bằng chứng tốt nhất (tử số, mẫu số, định nghĩa, phạm vi, kỳ); tuyên bố phổ quát hay loại trừ chỉ cần một phản ví dụ để bị bác; qualifier định lượng đặt cạnh tuyên bố làm giảm rủi ro; và phải gắn nhãn từng tuyên bố, không gắn cho cả vụ hay cả doanh nghiệp, vì kết quả hỗn hợp là phổ biến (Oatly 2022: bốn vấn đề upheld, một không; Lloyds 2024: chỉ một quảng cáo upheld).

Ở Việt Nam, chưa tìm thấy vụ nào cơ quan nhà nước xử phạt vì tuyên bố môi trường gây hiểu nhầm [UNVERIFIED, phủ định có giới hạn]. Hồ sơ công khai rõ nhất là các vụ ô nhiễm (Formosa Hà Tĩnh 2016; Vedan 2008) [SECONDARY], là bài học về bằng chứng trái chiều, không phải án về tuyên bố môi trường. Vì vậy với doanh nghiệp Việt Nam, luận văn chỉ dùng các cụm "ca kiểm tra", "khoảng trống bằng chứng", "cần người soát xét".

## 2.4 Khung pháp lý

### 2.4.1 Quốc tế

Chỉ thị (EU) 2024/825 (ECGT) áp dụng từ 27/09/2026: cấm tuyên bố môi trường chung chung không chứng minh được; cấm tuyên bố "trung hòa" hay "giảm KNK" ở cấp sản phẩm dựa trên bù trừ; tuyên bố tương lai cần kế hoạch đo được, có mốc, được bên thứ ba độc lập kiểm tra định kỳ (Điều 6(2)(d)). Báo cáo bền vững gửi nhà đầu tư thường nằm ngoài phạm vi (Q&A câu Q1), trừ khi nội dung được dùng lại trong truyền thông tới người tiêu dùng. Green Claims Directive: ý định rút ngày 20/06/2025, chưa thấy văn bản rút chính thức, đến 07/2026 vẫn bất định [CHƯA XÁC MINH]. UK CMA Green Claims Code (2021) có sáu nguyên tắc (trung thực và chính xác; rõ ràng; không bỏ sót; so sánh công bằng; xét cả vòng đời; có chứng minh). US FTC Green Guides (16 CFR 260) cần "reasonable basis" (§260.2) và không nên đưa tuyên bố lợi ích chung chung (§260.4); là hướng dẫn, chưa được sửa tính đến 08/2026. ASIC INFO 271 có chín câu tự kiểm. Điểm chung, đặt gánh nặng chứng minh lên chính tuyên bố, là cơ sở để GreenScan coi "chưa đủ bằng chứng" khác "sai".

### 2.4.2 Việt Nam

Bảng 2.5 tóm tắt các văn bản liên quan, theo trạng thái đã đối chiếu bản ký (ghi chú R4; một số điểm được ghi nhận là cập nhật sau ngày 13/10/2026 và đang chờ người duyệt pháp lý xác nhận).

**Bảng 2.5.** Văn bản pháp luật Việt Nam liên quan tới tuyên bố môi trường.

| Văn bản | Nội dung liên quan | Điểm cần lưu ý |
| --- | --- | --- |
| Luật Bảo vệ môi trường 72/2020/QH14, sửa bởi Luật 146/2025/QH15 (hiệu lực 01/01/2026) | Điều 145: sản phẩm "thân thiện môi trường" phải được chứng nhận hoặc công nhận; Điều 6.9: cấm làm sai lệch thông tin gây hậu quả xấu | Điều 145, 149, 150 không đổi qua sửa đổi 2025 |
| Nghị định 06/2022/NĐ-CP, sửa bởi NĐ 119/2025/NĐ-CP (hiệu lực 01/08/2025) | Kiểm kê KNK cấp cơ sở 2 năm một lần; điện, thép, xi măng thẩm định bởi tổ chức độc lập; Điều 19: bù trừ ≤ 30% hạn ngạch, tín chỉ đã dùng cho giảm phát thải tự nguyện không được giao dịch tiếp | Nghĩa vụ ở cơ sở, báo cáo doanh nghiệp ở cấp tập đoàn |
| Quyết định 21/2025/QĐ-TTg (hiệu lực 22/08/2025), QĐ 46/2026 (hiệu lực 01/11/2026) | Tiêu chí phân loại dự án xanh; xác nhận bởi cơ quan thẩm định hoặc tổ chức độc lập theo ISO/IEC 17029 hay VSAE/ISAE 3000 | Hai quyết định chạy song song |
| Thông tư 96/2020/TT-BTC (sửa bởi TT 68/2024, 18/2025, 08/2026) | Phụ lục IV mục 6: 6.1 KNK, 6.2 vật liệu, 6.3 năng lượng, 6.4 nước, 6.5 số lần và số tiền bị phạt về môi trường; công ty tài chính, ngân hàng, chứng khoán, bảo hiểm được miễn 6.1–6.3 | Không quy định Scope, ranh giới, năm gốc hay đảm bảo độc lập. Dự thảo thay thế lấy ý kiến đến 07/10/2026 đưa "công bố hoặc giải trình" |

**Không văn bản nào trong 14 văn bản đã đọc toàn văn định nghĩa tẩy xanh**; tạp chí Công Thương số 17/2026 kết luận độc lập điều tương tự. Hệ quả thiết kế là ánh xạ từng tuyên bố sang nghĩa vụ cụ thể (thông tin sai lệch, không đầy đủ, thiếu tài liệu chứng minh, thiếu chứng nhận), không gắn nhãn doanh nghiệp. Mức phạt cụ thể (NĐ 45/2022, NĐ 156/2020, NĐ 98/2020) [UNVERIFIED]: chưa đọc bản gốc nên không đưa vào quy tắc.

**Hai điểm dễ nhầm.** (a) *Chủ thể nghĩa vụ*: kiểm kê KNK thuộc cơ sở, không thuộc công ty niêm yết hay tập đoàn, nên phải ánh xạ cơ sở với công ty con và công ty niêm yết trước khi nói doanh nghiệp "thuộc diện". (b) *Bộ chỉ tiêu kỳ vọng khác nghĩa vụ đo lường*: Thông tư 96 nói phải có gì, không nói đo thế nào, nên thiếu Scope hay năm gốc là "chưa đủ bằng chứng về phạm vi", không phải "sai". Ngoài ra một tuyên bố có thể xét theo luật lúc công bố (`historical_compliance`) hay luật hôm nay (`current_policy_alignment`).

Về dữ liệu, Luật 91/2025/QH15 (hiệu lực 01/01/2026) coi việc dùng nền tảng ở nước ngoài để xử lý dữ liệu cá nhân thu thập tại Việt Nam là chuyển xuyên biên giới (Điều 20.1c), và Luật Kiểm toán độc lập 67/2011 Điều 43 cấm tiết lộ hồ sơ kiểm toán khi chưa có chấp thuận của khách hàng; hai điều này là cơ sở cho chế độ chạy ngoại tuyến ở chương 3. Mức rủi ro của GreenScan theo Luật Trí tuệ nhân tạo 134/2025/QH15 và NĐ 142/2026 [CHƯA XÁC MINH].

## 2.5 Chuẩn mực đảm bảo và công bố

### 2.5.1 Đảm bảo thông tin phi tài chính: ISAE 3000 và ISSA 5000

ISAE 3000 (Revised) và bản Việt Nam tương ứng VSAE 3000 là chuẩn cho dịch vụ đảm bảo thông tin ngoài báo cáo tài chính, ở hai mức: *hạn chế* (kết luận dạng phủ định, "không có gì khiến chúng tôi cho rằng…") và *hợp lý* (ý kiến khẳng định). ISAE 3410 áp dụng riêng cho báo cáo KNK. Quyết định 21/2025 và QĐ 46/2026 công nhận VSAE/ISAE 3000 cho tổ chức xác nhận dự án xanh.

ISSA 5000 (IAASB) là chuẩn mực quốc tế đầu tiên về đảm bảo thông tin bền vững, ban hành tháng 11/2024 (ngày 12/11/2024 theo INCP, chưa xác minh trên trang IAASB). Theo Fact Sheet của IAASB (01/2025): áp dụng cho mọi thông tin bền vững, kể cả KNK, lập theo bất kỳ khung báo cáo phù hợp nào, cho cả đảm bảo hạn chế và hợp lý; "profession agnostic" nhưng người hành nghề phải tuân thủ bộ quy tắc IESBA và ISQM 1 hoặc yêu cầu tương đương; đánh giá rủi ro ở cấp thuyết minh với đảm bảo hạn chế, ở cấp cơ sở dẫn liệu với đảm bảo hợp lý; ISAE 3410 được gộp vào và dự kiến rút khi ISSA 5000 có hiệu lực. Hiệu lực cho kỳ bắt đầu từ 15/12/2026, nên với doanh nghiệp năm dương lịch kỳ đầu là năm 2027. Chưa tìm thấy văn bản của Bộ Tài chính hay VACPA chấp nhận ISSA 5000 [CHƯA XÁC MINH].

Điều GreenScan mượn và không mượn:

- *Mượn*: tư duy "tiêu chí phù hợp, bằng chứng đủ và thích hợp, kết luận có giới hạn"; hoài nghi nghề nghiệp, tương ứng với nguyên tắc bằng chứng trước và từ chối khi chưa đủ.
- *Không có*: hợp đồng dịch vụ, chữ ký của người hành nghề, trách nhiệm nghề nghiệp. GreenScan không phát hành kết luận đảm bảo.
- Một báo cáo đảm bảo hạn chế chỉ cho Scope 1–2 chỉ nên được tính là nguồn ngoài cho đúng hai chỉ tiêu đó, không cho tuyên bố "dẫn đầu xanh" ở trang khác.

### 2.5.2 Công bố bền vững: IFRS S1/S2, GRI, ESRS

IFRS S1/S2 (ISSB) xây trên bốn trụ cột: quản trị, chiến lược, quản lý rủi ro, chỉ số và mục tiêu; IFRS S2 yêu cầu Scope 1, 2, 3 theo GHG Protocol, và sửa đổi ngày 11/12/2025 (hiệu lực 01/01/2027) giới hạn Scope 3 hạng mục 15 vào phát thải tài trợ, cho dùng hệ phân loại khác GICS và thêm miễn trừ về hệ số GWP. GRI 305 (KNK) và GRI 302 (năng lượng) là chuẩn tự nguyện về trọng yếu tác động, khoảng 19–25% doanh nghiệp HOSE áp dụng. ESRS dùng trọng yếu kép. Việt Nam chưa tìm thấy văn bản ràng buộc thời điểm áp dụng IFRS S1/S2 [CHƯA XÁC MINH]; khung bắt buộc hiện là Thông tư 96/2020.

Hai điều rút ra cho kiểm chứng số: thuộc tính của tuyên bố (chỉ số, Scope, kỳ, năm gốc, ranh giới) bám IFRS S2 và GHG Protocol; hai số CO2e chỉ so được khi cùng hệ số GWP và phương pháp. Ví dụ theo ghi chú R9 (kiến thức nền): 1.000 tấn CH4 là 28.000 tCO2e theo AR5 nhưng 29.800 tCO2e theo AR6, lệch 6,4% chỉ do đổi hệ số; khi đó hệ thống phải trả "không so được", không phải "mâu thuẫn".

### 2.5.3 Ánh xạ sang ngôn ngữ kiểm toán

Năm thuộc tính của một tuyên bố ứng với cơ sở dẫn liệu theo ISA 315: chỉ số cụ thể với *phân loại* và *chính xác*; năm gốc với *chính xác (so sánh)*; kỳ báo cáo với *đúng kỳ*; phạm vi hay ranh giới với *đầy đủ*; bằng chứng và phương pháp với căn cứ kiểm chứng. Cơ sở dẫn liệu *trình bày* (cách trình bày gây hiểu nhầm dù từng số đúng) chưa có thủ tục tương ứng. GreenScan không thuộc loại nào trong năm loại "kiểm" của người làm tài chính, kế toán (kiểm toán BCTC; đảm bảo thông tin phi tài chính; thẩm định kiểm kê KNK theo NĐ 06 sửa bởi 119; xác nhận dự án xanh theo QĐ 21/2025; chứng nhận sản phẩm theo NĐ 08/2022): nó sàng lọc trước và sau khi có đảm bảo, hỗ trợ đánh giá rủi ro và việc đọc "thông tin khác" trong báo cáo thường niên. Doanh nghiệp công bố chịu trách nhiệm trước pháp luật về nội dung công bố (Thông tư 96 Điều 4.2), người dùng nghiệp vụ chịu trách nhiệm về quyết định của mình, còn kết luận vi phạm thuộc cơ quan có thẩm quyền.

## 2.6 NLP cho tuyên bố khí hậu và môi trường

### 2.6.1 Mô hình ngôn ngữ chuyên biệt và phát hiện tuyên bố

Nhóm Leippold (Zurich) đặt nền cho hướng này. ClimateBERT (Webersinke và cs., arXiv:2110.12010) tiếp tục tiền huấn luyện trên hơn 2 triệu đoạn văn khí hậu; mục tiêu masked language model cải thiện 48%, tỷ lệ lỗi giảm từ 3,57% đến 35,71% trên các tác vụ hạ nguồn (phân loại, sentiment, kiểm chứng). ClimaText (Varini và cs., NeurIPS 2020 workshop) nêu rằng mô hình dựa từ khóa "không đủ" để phát hiện câu về chủ đề khí hậu; BERT bắt được nhiều ca dễ và một phần mẫu ẩn.

**Environmental Claim Detection** (Stammbach và cs., ACL 2023) định nghĩa tác vụ phân loại câu có phải tuyên bố môi trường hay không. Bộ dữ liệu có 3.000 câu, mỗi câu do bốn người trong nhóm 16 chuyên gia gán; sau khi bỏ 353 câu hòa phiếu còn 2.647 câu, 25% là tuyên bố; Krippendorff α = 0,47. F1 trên test: SVM TF-IDF 69,1; SVM n-gram ký tự 70,9; DistilBERT 83,7; ClimateBERT 83,8; RoBERTa-large 84,9. Khoảng cách recall giữa SVM và transformer lên tới 25 điểm vì không phải tuyên bố môi trường nào cũng chứa từ khóa. Điều này có hai hệ quả: bộ trích tuyên bố bằng từ khóa chắc chắn bỏ sót, và lỗi tốn kém nhất của tầng này là bỏ sót, vì câu bị sót không bao giờ được kiểm. Cách đo recall hợp lý là lấy mẫu các câu *không* được trích rồi cho người xem. Dữ liệu `climatebert/environmental_claims` mang giấy phép CC BY-NC-SA 4.0 (phi thương mại).

Các hướng tiếp theo: ClimateBERT-NetZero (Schimanski và cs., EMNLP 2023) nhận diện mục tiêu net-zero, trong đó trích năm gốc bằng hỏi đáp chỉ đạt 0,68; ClimRetrieve (Schimanski và cs., EMNLP 2024) là bộ chuẩn truy xuất trên báo cáo khí hậu doanh nghiệp, tác giả gọi kết quả là cận dưới; A3CG (Ong và cs., ACL 2025) cho thấy mô hình có giám sát (47,5) hơn LLM (40–42) trên nhóm chưa thấy; Braun và cs. (2026, arXiv:2601.21722) dùng học tương phản để phân biệt hành động cụ thể với tuyên bố mơ hồ; climateBUG (Yu và cs., 2024) có hơn 1,07 triệu câu từ báo cáo ngân hàng EU 2015–2020 nhưng giấy phép CC BY-NC-ND 4.0 nên chỉ tham khảo.

### 2.6.2 Phát hiện tẩy xanh và khoảng trống dữ liệu

Khảo sát của Calamai và cs. (2025; phiên bản 2, 01/2026) kết luận chưa có bộ dữ liệu tẩy xanh nào được xác minh và khuyến nghị kiến trúc phân rã có người giám sát. Greench-v1 (Raspanti và cs., NLP4Ecology 2026) dùng mô hình nhỏ dựa trên Qwen3-4B để *phán* lớp "Greenwashing Alert" trên khoảng 2.000 đoạn ESG. EmeraldMind (Kaoukis và cs., WWW 2026, arXiv:2512.11506) dùng đồ thị tri thức cộng RAG có từ chối; trên EmeraldData (620 tuyên bố bán tổng hợp), LLM nền đạt độ đúng 94,21% nhưng độ phủ chỉ 19,52% (overall 18,39%, với overall = độ đúng × độ phủ), còn EM-HYBRID đạt 83,80% và 74,68% (overall 62,58%). Hai điểm rút ra: báo độ đúng không kèm độ phủ gây hiểu nhầm; và hệ thống để mô hình ra verdict tẩy xanh khác căn bản với hệ thống để mô hình đọc, luật quyết. Trong phạm vi các tài liệu đã rà, chúng tôi không tìm thấy công trình NLP công bố về kiểm chứng tuyên bố ESG trên báo cáo tiếng Việt tính đến 10/2026, cũng không thấy bộ dữ liệu tẩy xanh tiếng Việt công khai (dự án VinUni GREEN-X dự kiến phát hành một bộ, chưa rõ đã phát hành).

## 2.7 Kiểm chứng tuyên bố và lớp "không đủ bằng chứng"

Quy trình kiểm chứng chuẩn (Guo, Schlichtkrull & Vlachos, TACL 2022) gồm bốn bước: phát hiện tuyên bố, truy xuất bằng chứng, dự đoán verdict, giải thích. Các bộ dữ liệu chuẩn đều có lớp "không đủ thông tin":

- **FEVER** (Thorne và cs., NAACL 2018): 185.445 tuyên bố; Fleiss κ = 0,6841; nhãn SUPPORTED, REFUTED, NOTENOUGHINFO. Pipeline tốt nhất chỉ đạt 31,87% khi bắt buộc đúng cả bằng chứng, và 50,91% nếu bỏ qua bằng chứng. Bài học: chỉ chấm verdict khi bằng chứng đúng.
- **CLIMATE-FEVER** (Diggelmann và cs., NeurIPS 2020 workshop): 1.535 tuyên bố, 7.675 cặp tuyên bố–bằng chứng, thêm nhãn DISPUTED; mô hình huấn luyện trên FEVER đạt 77,69% trên FEVER dev nhưng chỉ 38,78% ở đây.
- **AVeriTeC** (Schlichtkrull và cs., NeurIPS 2023): 4.568 tuyên bố, có lớp bằng chứng xung đột hay chọn lọc và quy tắc gộp nhãn tất định (có cả ủng hộ lẫn bác bỏ thì xung đột; chỉ ủng hộ thì ủng hộ; chỉ bác bỏ thì bác bỏ; còn lại thiếu bằng chứng). Shared task 2024 đạt 63%; năm 2025, khi giới hạn mô hình mở trên một GPU 23 GB, chỉ đạt 33,17%.

Hai điểm lý thuyết quan trọng với thiết kế:

1. *Đủ bằng chứng chưa và bằng chứng ủng hộ hay bác bỏ là hai câu hỏi khác nhau.* Joren và cs. (ICLR 2025, "Sufficient Context") cho thấy LLM lớn thường trả lời, kể cả trả lời sai, thay vì từ chối khi ngữ cảnh không đủ. Do đó quyết định "đủ" nên tách khỏi quyết định "ủng hộ hay bác bỏ" và giao cho thủ tục kiểm tra được.
2. *Vắng bằng chứng không phải bằng chứng trái chiều.* Lớp `INSUFFICIENT_EVIDENCE` là kết quả hợp lệ. Nhãn khớp một phần và mâu thuẫn cùng cách gộp tất định có tiền lệ học thuật ở AVeriTeC và Climate-FEVER; "cherry-picking" trong công bố khí hậu cũng đã được kiểm chứng thực nghiệm (Bingler và cs., 2022).

Về nhiễu nhãn: κ của các bộ đạt từ rất thấp đến khá. Bảng 2.6 đặt mục tiêu κ ≥ 0,7 của luận văn vào bối cảnh.

**Bảng 2.6.** Hệ số đồng thuận của các bộ dữ liệu cùng loại.

| Bộ dữ liệu | Hệ số đồng thuận |
| --- | --- |
| Environmental claims | Krippendorff α = 0,47 |
| Climate-FEVER (bằng chứng) | α = 0,334 |
| AVeriTeC | free-marginal κ = 0,619; Fleiss κ = 0,503 |
| FEVER | Fleiss κ = 0,684 |
| ViFactCheck (tiếng Việt, tin tức) | Fleiss κ = 0,83 |

Vì thế κ ≥ 0,7 là mục tiêu cao so với các bộ cùng loại; nếu không đạt, kết quả phải được báo trung thực kèm đồng thuận theo từng lớp.

## 2.8 Truy xuất lai và RAG

### 2.8.1 RAG và vai trò đã thu hẹp trong GreenScan

RAG (Lewis và cs., NeurIPS 2020; arXiv:2005.11401) kết hợp bộ nhớ tham số của mô hình seq2seq với bộ nhớ phi tham số là chỉ mục vector, và cho kết quả tốt nhất trên ba tác vụ hỏi đáp miền mở. GreenScan chỉ dùng phần "R" để tìm ứng viên bằng chứng; phần "G" không dùng để ra kết luận. Đây là *kiểm chứng có truy xuất*: truy xuất cho ứng viên, mô hình điền biểu diễn trung gian, mã kết luận.

Zhao và cs. (ACM TOSEM 2026; arXiv:2411.19463) cho thấy tài liệu gây nhiễu làm hỏng RAG, thiết kế phải theo từng tác vụ, và có lỗi ảnh hưởng 12,6% mẫu ngay cả khi tài liệu hoàn hảo. "Lost in the Middle" cho thấy hiệu năng hình chữ U theo vị trí thông tin, nên lời gọi mô hình chỉ chứa cặp tuyên bố–bằng chứng. RAGAS (Es và cs., arXiv:2309.15217) đánh giá RAG không cần đáp án tham chiếu, hợp để kiểm lời giải thích có bám bằng chứng nhưng "nhất quán với ngữ cảnh" chưa phải là "đúng".

### 2.8.2 Truy xuất lai: BM25, n-gram ký tự, embedding và hợp nhất

Truy xuất lai kết hợp tín hiệu từ vựng và ngữ nghĩa. Các thành phần dùng trong GreenScan (kiến thức nền, theo ghi chú R5 mục B): BM25 (Robertson & Zaragoza, 2009) với k1 = 1,5 và b = 0,75; TF-IDF trên n-gram ký tự 3–5, chịu được lỗi tách từ tiếng Việt, mất dấu và dính chữ do OCR; bi-encoder cho truy xuất nhanh và cross-encoder chỉ dùng xếp lại top-k; hợp nhất tuyến tính (cần cùng thang điểm) hoặc RRF (Cormack, Clarke & Büttcher, SIGIR 2009) với RRF(d) = Σ 1/(k + rank_r(d)), k = 60, chỉ cần thứ hạng. GreenScan dùng RRF để đổi thứ tự nhưng giữ điểm tuyến tính để so ngưỡng. Ba ứng viên tốt nhất luôn được giữ dù dưới ngưỡng, để tách "không đoạn nào nói về tuyên bố" khỏi "không đoạn nào *trông giống* tuyên bố": trong vụ KLM, phán quyết bác bỏ ít chữ trùng với câu quảng cáo nhưng mang bằng chứng bác bỏ có thẩm quyền.

### 2.8.3 Đo truy xuất và thiên lệch pooling

Chỉ số: Recall@k = |liên quan ∩ top-k| / |liên quan|; MRR; nDCG@k; Hole@k là tỷ lệ tài liệu chưa gán nhãn trong top-k. **Thiên lệch pooling**: nếu ứng viên cho người gán chỉ đến từ BM25, mô hình dense bị đánh giá thấp có hệ thống. Theo BEIR, Hole@10 của TAS-B là 31,8% so với 6,4% của BM25; ANCE tăng từ 0,654 lên 0,735 sau khi gán nhãn bổ sung. Vì vậy cần gộp ứng viên từ mọi bộ truy xuất trước khi gán nhãn, và báo Recall@k là cận dưới kèm Hole@k. Cũng vì lẽ đó chỉ số truy xuất phải được đo tách khỏi chỉ số kiểm chứng (độ đúng, macro-F1, số mâu thuẫn sai, tỷ lệ từ chối).

### 2.8.4 Tài nguyên tiếng Việt

Multilingual E5 (Wang và cs., 2024, arXiv:2402.05672) là họ embedding giấy phép MIT có ba cỡ, được chọn làm nền cho mô hình nhỏ nhận diện tuyên bố. Theo VN-MTEB (Findings of EACL 2026, dữ liệu dịch máy), thứ hạng đảo theo bộ dữ liệu: `AITeamVN/Vietnamese_Embedding` thấp hơn bge-m3 trên ClimateFEVER-VN (13,25 so với 21,27) nhưng model card tự báo điều ngược lại trên văn bản luật, nên chỉ dữ liệu của chính dự án quyết được mô hình nào dùng. Bẫy giấy phép: environmental_claims, AVeriTeC, XNLI, QuanTemp, ViANLI phi thương mại; `phobert-base-v2` là AGPL-3.0.

## 2.9 Số học trong văn bản tài chính và môi trường

Các kết quả sau cho thấy mô hình ngôn ngữ yếu ở đúng chỗ kiểm chứng cần chính xác:

- **NumPert** (Aarnes & Setty, 2025): độ chính xác giảm tới 62% khi số bị nhiễu.
- **Aarnes & Setty (30/09/2026)**: mô hình tiên tiến chỉ khoảng 74% trên cặp khác đúng một con số; Qwen3 nhỏ được tinh chỉnh PEFT đạt 98,7% (số tự báo trong ghi chú).
- **FinQA** (Chen và cs., EMNLP 2021): 8.281 cặp hỏi–đáp từ 2.789 trang báo cáo S&P 500; FinQANet 61,24%, chuyên gia 91,16%; câu cần từ ba bước suy luận trở lên chỉ 22,78%.
- **FinDVer** (Zhao và cs., EMNLP 2024): trên báo cáo tài chính, LLM tốt nhất 77,2% so với chuyên gia 93,3%.

FinQA và TAT-QA đều tách "chọn số" (phần thần kinh) khỏi "tính" (phần ký hiệu): mô hình sinh chương trình rồi thực thi. Đây cũng là ý tưởng của GreenScan: mô hình đọc câu thành biểu diễn trung gian (chỉ số, giá trị, đơn vị, bội số, kỳ, năm gốc, ranh giới, Scope, loại giá trị, thành tích hay mục tiêu), và mã tất định làm phần còn lại. Các khái niệm thủ tục:

- **Kiểm "so được" trước khi tính**: Scope 1+2 không so với Scope 1; tập đoàn không so với nhà máy; tuyệt đối không so với cường độ dù cùng đơn vị tCO2e. Lệch một chiều thì cấm kết luận mâu thuẫn.
- **Dung sai theo độ chính xác công bố**: nửa đơn vị của chữ số cuối, trần 10%; phân biệt điểm phần trăm với phần trăm tương đối.
- **Cộng ngang, dọc (cross-footing)**: tổng phải bằng tổng các thành phần; bảng không qua kiểm thì không dùng để kết luận. Ví dụ trong bản thảo bài báo: 22.540.603 + 933.876 = 23.474.479 so với công bố 23.474.480 là khớp do làm tròn.
- **Mục tiêu khác thành tích**: "sẽ giảm 30%" không chứng minh "đã giảm 30%".
- **Kiểm nguồn gốc tất định**: mọi số, bội số và năm trong biểu diễn trung gian phải được *viết* trong câu gốc, nếu không thì để rỗng. Giải mã ràng buộc bằng JSON schema (như Outlines hay GBNF của llama.cpp, kiến thức nền) chỉ bảo đảm cú pháp, không bảo đảm nội dung; kiểm nguồn gốc chặn bịa ở phần nghĩa.
- **Chuẩn hóa NFC**: dấu tiếng Việt có hai dạng mã hóa; lỗi gộp dấu "cộng" và "công" từng làm nhận nhầm dòng tổng.

## 2.10 Mô hình ngôn ngữ lớn làm thẩm định viên: thiên lệch và độ tin cậy

### 2.10.1 LLM làm người chấm

Zheng và cs. (NeurIPS 2023, D&B) báo GPT-4 đồng ý với người trên 80% ở bài sở thích hội thoại, nhưng cũng chỉ ra thiên lệch vị trí, độ dài và tự ưu tiên. G-Eval (Liu và cs., arXiv:2303.16634) đạt Spearman 0,514 với người trên bài tóm tắt, và tác giả cảnh báo evaluator LLM thiên vị văn bản do LLM viết. Wang và cs. (ACL 2024) và Panickssery (tự ưu tiên) củng cố điều này. To và cs. (2024) báo dữ liệu kiểm chứng tiếng Việt do LLM sinh kém dữ liệu người viết.

Mặt đối lập: Gilardi, Alizadeh & Kubli (PNAS 2023; arXiv:2303.15056) với 2.382 tweet cho thấy ChatGPT zero-shot chính xác hơn người làm thuê đám đông ở 4/5 tác vụ, độ đồng thuận nội bộ cao hơn cả đám đông lẫn người gán được đào tạo, chi phí dưới 0,003 USD mỗi nhãn. Giới hạn: miền là tweet; đồng thuận cao chưa phải là đúng; nếu nhãn và bài thi cùng một nguồn LLM thì dễ thành vòng tròn. Hai chiều lập luận này đi tới cùng kết luận thực hành: có thể dùng LLM gán nhãn nếu quy trình gán chặt (hướng dẫn, hai lượt mù, phân xử, người đọc lại) và không để cùng một mô hình vừa sinh vừa chấm. Biện pháp giảm thiên lệch: chạy cả hai thứ tự, kiểm định với nhãn đã được người đọc, và dùng nhãn theo cấu trúc, tức biết đáp án nhờ cách dựng ca kiểm tra.

### 2.10.2 Độ trung thực của lời giải thích

Jacovi & Goldberg (ACL 2020, tr. 4198–4205) đề nghị bỏ định nghĩa nhị phân của faithfulness và chuyển sang thang bậc. Turpin và cs. (NeurIPS 2023; arXiv:2305.04388) cho thấy lời giải thích kiểu chuỗi suy luận có thể xuyên tạc có hệ thống lý do thật của dự đoán, độ chính xác giảm tới 36% trên 13 tác vụ BIG-Bench Hard khi có đặc trưng gây lệch không được nhắc trong lời giải thích. Hàm ý: lời giải thích do mô hình viết chỉ nên coi là "dễ đọc", không là căn cứ; với phần tất định, lời giải thích *chính là* đường tính thật (giá trị đã tính, mã quy tắc, câu trích kèm trang), nên trung thực theo cách dựng.

## 2.11 Dự đoán có từ chối và hiệu chỉnh

**Hiệu chỉnh (calibration).** Mô hình hiệu chỉnh tốt khi P(đúng | độ tin cậy = p) = p; sai số hiệu chỉnh kỳ vọng ECE = Σ_m (|B_m|/n)·|acc(B_m) − conf(B_m)|. Guo và cs. (ICML 2017; arXiv:1706.04599) cho thấy mạng nơ-ron hiện đại hiệu chỉnh kém hơn mạng cũ và temperature scaling đơn giản mà hiệu quả. Độ tự tin LLM tự khai thường quá cao (Xiong, 2024); softmax quá tự tin ngoài miền (Kamath, 2020: 56% so với 48% ở độ đúng 80%). Vì vậy điểm rủi ro 0–100 của GreenScan *không* được coi là xác suất.

**Dự đoán có từ chối (selective prediction).** Bộ (f, g) trong đó g quyết có trả lời không. Độ phủ φ = E[g]; rủi ro chọn lọc R = E[ℓ·g]/E[g]; đường risk–coverage (Geifman & El-Yaniv, NeurIPS 2017); nguồn gốc là quy tắc từ chối của Chow (1970). Conformal prediction cho bảo đảm thống kê từ tập hiệu chỉnh: Angelopoulos & Bates (arXiv:2107.07511) cho tập dự đoán chứa đáp án đúng với xác suất người dùng chọn, không cần giả định phân phối; Mohri & Hashimoto (ICML 2024) đạt bảo đảm 80–90% với ít mẫu có nhãn bằng cách làm đầu ra bớt cụ thể.

**Các thước đo dùng ở chương 4.**

- *precision trên phần dám kết luận* = số đúng trong {SUPPORTED, CONTRADICTED} chia số kết luận thuộc {SUPPORTED, CONTRADICTED} (bằng 1 trừ rủi ro chọn lọc);
- *độ phủ* = số kết luận thuộc {SUPPORTED, CONTRADICTED} chia N;
- *số kết luận sai nguy hiểm*: `CONTRADICTED` sai là vu oan, `SUPPORTED` sai là bỏ lọt.

Không gộp ba thước đo thành một số. EmeraldMind (mục 2.6.2) minh họa vì sao: overall = độ đúng × độ phủ che mất đánh đổi. Chi phí bất đối xứng: vu oan đắt hơn bỏ lọt, nên ngưỡng kết luận cho `CONTRADICTED` đặt cao hơn.

## 2.12 Người và máy trong kiểm toán

Bansal và cs. (CHI 2021): lời giải thích của AI có thể làm người chấp nhận khuyến nghị bất kể đúng sai. Vasconcelos và cs. (2023): giải thích chỉ giảm phụ thuộc quá mức khi làm *rẻ việc kiểm*. Commerford và cs. (2022): kiểm toán viên xem nhẹ bằng chứng do AI đưa ra. Warren và cs. (CHI 2025): kiểm chứng viên chuyên nghiệp đòi giải thích dựa trên bằng chứng, hiện đường suy luận, chỗ bất định và thông tin còn thiếu. Hàm ý thiết kế: hiện bằng chứng gốc (ảnh trang có tô sáng), người chốt, không tự động hóa kết luận có hệ quả. Về đo khả dụng, mười heuristic của Nielsen là công cụ đánh giá chuyên gia; SUS (Brooke) cho điểm 0–100 nhưng các số SUS trong ghi chú chỉ ở dạng [TÌM, CHƯA XÁC MINH trên trang gốc], nên nếu dùng phải đối chiếu lại nguồn.

## 2.13 Tuân thủ quy tắc, tiêm lệnh và bộ nhớ của hệ thống

Phần này phục vụ RQ4: nếu người dùng thêm quy tắc và tài liệu nội bộ, làm sao không mở ra kênh tấn công.

- **RuLES** (Mu và cs., arXiv:2311.04235) và **IFEval** (Zhou và cs., arXiv:2311.07911) dùng hàm chấm bằng chương trình, vì chấm bằng người đắt, khó lặp lại và chấm bằng LLM thiên lệch; RuLES cho thấy hầu hết mô hình khó tuân thủ quy tắc và tấn công tối ưu đơn giản đủ làm tăng mạnh tỷ lệ hỏng.
- **Instruction Hierarchy** (Wallace và cs., arXiv:2404.13208): LLM thường coi system prompt ngang hàng với văn bản không tin cậy; đề xuất thứ bậc chỉ dẫn. **Tiêm lệnh gián tiếp** (Greshake và cs., arXiv:2302.12173): cài chỉ dẫn vào nội dung ứng dụng sẽ truy xuất, vì ứng dụng tích hợp LLM "xóa ranh giới giữa dữ liệu và chỉ dẫn".
- **MemGPT** (Packer và cs., arXiv:2310.08560) quản lý ngữ cảnh theo bộ nhớ phân tầng; **ACE** (Zhang và cs., ICLR 2026, arXiv:2510.04618) coi ngữ cảnh là "playbook" tiến hóa, chỉ ra *brevity bias* và *context collapse*.

Bốn bài học thiết kế rút ra, đối chiếu với nguyên tắc ở chương 3: (i) quy tắc nên có thứ bậc và phần quan trọng nhất không do mô hình diễn giải; (ii) kiểm tra quy tắc bằng hàm tất định, theo tinh thần RuLES và IFEval; (iii) tài liệu do người dùng cung cấp là *dữ liệu*, không phải lệnh, vì ranh giới dữ liệu–chỉ dẫn là điểm yếu đã được chứng minh (Greshake và cs.); (iv) khác ACE, không để mô hình tự viết lại bộ quy tắc: một quy tắc chỉ bật khi qua bốn cổng (gắn điều khoản nguồn, có người duyệt, test đạt, phạm vi thời gian xác định).

## 2.14 Đo trên mẫu nhỏ

Khi nhãn vàng chỉ vài chục đến vài trăm cặp, các điểm sau là nền cho RQ5:

- **Khoảng tin cậy Wilson** cho tỷ lệ; nếu đúng hết thì cận dưới 95% là 0,72 với n = 10, 0,80 với n = 15, 0,85 với n = 22 (tự tính). Với p̂ = 0,80, n = 60 cho ±10,0 điểm, n = 100 cho ±7,8 điểm; κ = 0,70 trên 60–100 cặp có khoảng tin cậy xấp xỉ [0,52; 0,88]. Chênh lệch nhỏ nhất phát hiện được (power 80%) là khoảng 10–17 điểm với n = 80; chênh nhỏ hơn thì nói "không phát hiện được khác biệt", không nói "bằng nhau".
- **Cụm theo doanh nghiệp**: tuyên bố của cùng doanh nghiệp không độc lập; sai số chuẩn có cụm có thể lớn gấp 3 sai số ngây thơ (Miller, 2024). Với DE = 1 + (m − 1)·ICC, n_eff = n/DE: 80 tuyên bố từ 10 doanh nghiệp, ICC 0,1 cho n_eff khoảng 47. Cần bootstrap theo công ty và chia dữ liệu giữ hẳn công ty ra ngoài.
- **Hệ số đồng thuận**: κ = (p_o − p_e)/(1 − p_e); nghịch lý κ làm κ thấp dù tỷ lệ đồng ý cao khi nhãn lệch (Feinstein & Cicchetti, 1990). Krippendorff α dùng được cho nhiều loại nhãn và dữ liệu thiếu; ngưỡng α ≥ 0,800 thì dựa vào được, 0,667 ≤ α < 0,800 chỉ cho kết luận tạm.
- **Luôn kèm baseline lớp đa số và macro-F1.** Ví dụ Climinator báo 96,4% nhị phân nhưng đoán toàn lớp đa số đã đạt 90,3%; với 12 lớp chỉ 34,5%.
- **Đăng ký trước** ngưỡng và dự đoán; báo cả dự đoán sai và kết quả âm.

Với bốn loại đầu ra không có đáp án duy nhất, điểm xuất phát lý thuyết là: lời giải thích đo bằng độ trung thực thang bậc (mục 2.10.2) và độ bám bằng chứng; gợi ý sửa đo bằng ca dựng có tuyên bố đúng gốc; điểm rủi ro đo bằng tương quan thứ hạng với nhãn đã đọc lại (Spearman, QWK); khả dụng đo bằng heuristic và SUS (mục 2.12). Phương án cụ thể nằm ở chương 4.

## 2.15 Vị trí của công nghệ lượng tử: nói đúng bằng chứng

Thể lệ cuộc thi có nhóm đề tài lượng tử, cho phép không dùng phần cứng lượng tử thực và dùng Qiskit, PennyLane, Cirq; mọi chủ đề chấm cùng hệ tiêu chí (Điều 10). **GreenScan hiện không có dòng mã lượng tử nào**: kiểm mã ngày 04/11/2026 cho 0 tệp QUBO, QAOA hay ủ mô phỏng và không cài thư viện lượng tử nào; chữ "quantum" trong tên gói, thư mục và biến môi trường chỉ là tên dự án. Những điều đã ghi chú giúp đặt lượng tử đúng chỗ:

- **QUBO và Ising.** QUBO cực tiểu hóa xᵀQx trên x thuộc {0,1}^n, ràng buộc đưa vào bằng hàm phạt (chọn đúng k phần tử là μ(Σxⱼ − k)²). Bài chọn đoạn bằng chứng của GreenScan có công thức QUBO trên tài liệu thiết kế nhưng chưa cài đặt; ở n = 30, C(30,5) = 142.506 tổ hợp, vét cạn được.
- **Chỉ bảo đảm xấp xỉ, mô phỏng có trần.** QAOA (Farhi, Goldstone & Gutmann, 2014; arXiv:1411.4028) ở p = 1 trên MaxCut đồ thị 3-chính quy bảo đảm ít nhất 0,6924 lần lát cắt tối ưu; bộ mô phỏng statevector cần 2ⁿ × 16 byte (30 qubit là 16 GiB).
- **Lợi thế lượng tử** chỉ có khi lượng tử bằng hoặc hơn thuật toán cổ điển *tốt nhất* với chi phí thấp hơn và lặp lại được. Herman và cs. (2023, *Nature Reviews Physics* 5:450–465; arXiv:2201.02773) kết luận Monte Carlo lượng tử có tăng tốc bậc hai về lý thuyết nhưng chưa chứng minh được trong thực tế và cần máy chịu lỗi; đó là kết luận của bài tổng quan 2023, không phải của nhóm tác giả. HSBC và IBM (25/09/2025) báo cải thiện "tới 34%" dự báo lệnh RFQ được khớp, là cải thiện tương đối về AUC so với một baseline cụ thể, không có giao dịch thật.
- **Thuật toán lấy cảm hứng lượng tử** chạy trên phần cứng cổ điển (SQBM+ của Toshiba, tới 10 triệu biến ở phiên bản 2); nếu bài QUBO lớn lên, đây là con đường thực tế. **QNLP** (Meichanetzidis và cs., 2020, arXiv:2012.03756) mới chạy được tác vụ nhỏ trên máy NISQ; nói QNLP sẽ thay mô hình ngôn ngữ lớn là "tẩy xanh công nghệ".

Luận văn vì vậy không khẳng định lượng tử cải thiện kết quả. Lượng tử chỉ xuất hiện như bối cảnh và như một hướng nghiên cứu có điều kiện (bài chọn bằng chứng ở quy mô nhỏ), trình bày ở chương 6.

## 2.16 Liên hệ lý thuyết với câu hỏi nghiên cứu

| RQ | Lý thuyết nền | Điều rút ra cho thiết kế |
| --- | --- | --- |
| RQ1 | Mẫu hình tẩy xanh (2.2); án lệ (2.3); kiểm chứng và lớp thiếu bằng chứng (2.7); dự đoán có từ chối (2.11) | Kết luận theo từng tuyên bố; "đủ bằng chứng" quyết bằng luật; vắng bằng chứng không phải bằng chứng trái chiều; báo precision trên phần dám kết luận cùng độ phủ |
| RQ2 | Số học trong văn bản tài chính (2.9); IFRS S2 và GHG Protocol (2.5.2) | Mô hình đọc, mã tính; kiểm "so được" trước; dung sai theo độ chính xác; cross-footing; kiểm nguồn gốc |
| RQ3 | NLP khí hậu (2.6); tài nguyên tiếng Việt (2.8.4); mô hình nhỏ | Mô hình nhỏ đọc và nhường người; mọi lựa chọn là thử nghiệm đến khi có đo; chú ý giấy phép |
| RQ4 | Tuân thủ quy tắc, tiêm lệnh và bộ nhớ (2.13); bốn cổng của quy tắc pháp lý | Thứ bậc quy tắc; tài liệu nội bộ là dữ liệu; từ chối nạp khi lỗi; không để mô hình tự viết quy tắc |
| RQ5 | LLM làm người chấm (2.10.1); mẫu nhỏ (2.14); người–máy (2.12) | Không dùng LLM tự chấm; Wilson, bootstrap theo công ty, κ kèm khoảng tin cậy; đăng ký trước |

## 2.17 Tóm tắt chương

- Tẩy xanh có nhiều định nghĩa; ESAs (2024) coi cả vô ý là tẩy xanh, Seele & Gatti (2017) coi đó là cáo buộc, luật Việt Nam không định nghĩa. Vì vậy hệ thống đo mức đủ bằng chứng của từng tuyên bố, tách rủi ro khỏi kết luận vi phạm; 21 mẫu hình cho biết trung thực phần máy kiểm được và không kiểm được.
- Án lệ (KLM, Shell 2023 và 2025, Katjes, Mercer...) cho thấy bằng chứng thường nằm trong chính tài liệu của doanh nghiệp, qualifier đặt cạnh tuyên bố đổi kết cục, và tuyên bố loại trừ chỉ cần một phản ví dụ.
- ISAE 3000, ISSA 5000 (kỳ từ 15/12/2026) và IFRS S1/S2 cho khuôn thuộc tính của tuyên bố và phân định rõ GreenScan là công cụ sàng lọc, không phải dịch vụ đảm bảo.
- Các nghiên cứu NLP ủng hộ kiến trúc phân rã: từ khóa bỏ sót tuyên bố (chênh recall tới 25 điểm), LLM tụt mạnh với số và bảng, LLM lớn trả lời thay vì từ chối; do đó số học do mã, "không đủ bằng chứng" do luật, truy xuất đo tách khỏi kiểm chứng.
- Đo mẫu nhỏ cần khoảng tin cậy, bootstrap theo công ty và đăng ký trước. Lượng tử chưa có dòng mã nào trong hệ thống và lý thuyết không cho phép nói lượng tử cải thiện kết quả.

---

## Tài liệu tham khảo của chương 2

Chỉ ghi nơi công bố và URL khi ghi chú nguồn trong repo (`docs/10-chung-ket-2026-11/doc-tai-lieu/R*.md`, `docs/08-knowledge/`, bản thảo bài báo) có; các chỗ "không ghi trong ghi chú" được để nguyên để biên tập viên bổ sung. Nhãn [KTN] là kiến thức nền do ghi chú nêu, chưa mở lại nguồn gốc.

**Tẩy xanh, khung khái niệm và án lệ**

- Delmas, M. A. & Burbano, V. C. (2011). Định nghĩa tẩy xanh và ma trận 2×2. *California Management Review* 54(1): 64–87. (Qua tóm tắt, nguồn thứ cấp; tên bài và URL không ghi trong ghi chú R3.)
- Lyon, T. P. & Montgomery, A. W. (2015). Tẩy xanh như thuật ngữ ô. *Organization & Environment* 28(2): 223–249. (Abstract đã kiểm theo file nguồn; URL không ghi.)
- Marquis, C., Toffel, M. W. & Zhou, Y. (2016). Công bố chọn lọc tác động lành tính (4.750 công ty, 45 nước). *Organization Science* 27(2). URL không ghi.
- Seele, P. & Gatti, L. (2017). Tẩy xanh như cáo buộc, bốn loại. *Business Strategy and the Environment* 26(2). Tên bài đầy đủ và URL không ghi.
- ESMA, EBA, EIOPA (2024). *Final Report on Greenwashing*, 04/06/2024, và báo cáo tiến độ 2023 (mười hai tính chất gây hiểu nhầm). URL không ghi.
- TerraChoice (2007, 2009). Bảy tội của tẩy xanh. Số liệu 2009 chỉ từ nguồn thứ cấp; số 2007 và 2010 [CHƯA XÁC MINH]. URL không ghi.
- Hồ sơ vụ việc: `docs/08-knowledge/04_AN_LE_VA_BAI_HOC.md`; ghi chú R3 mục 1.11 và 1.12 (Lizama & Doten v. H&M, E.D. Mo., 4:22-cv-01170); `data/legal_cases/` (ASA, ASIC, SEC).

**Pháp lý và chuẩn mực**

- Chỉ thị (EU) 2024/825 (Empowering Consumers). Mayer Brown (27/10/2026) về ngày áp dụng. URL không ghi.
- UK CMA (2021). *Green Claims Code*; US FTC. *Green Guides*, 16 CFR 260; ASIC. *INFO 271* (cập nhật 03/2026). URL không ghi.
- Luật Bảo vệ môi trường 72/2020/QH14 và 146/2025/QH15; NĐ 06/2022 và 119/2025; QĐ 13/2024, 21/2025, 46/2026; TT 96/2020/TT-BTC; TT 17/2022/TT-NHNN; Luật 19/2023/QH15; Luật Quảng cáo sửa bởi 75/2025/QH15; Luật 91/2025/QH15. Nguồn: `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`; ghi chú R4 và R9.
- IAASB (01/2025). *ISSA 5000, Fact Sheet*. Chuẩn mực ISSA 5000 ban hành 11/2024. URL không ghi (ghi chú R9: đã mở, bản lưu `scratchpad\R9\issa5000_factsheet.txt`).
- ISSB (11/12/2025). Sửa đổi IFRS S2. ifrs.org (đã mở theo ghi chú R9; URL đầy đủ không ghi).
- IAASB. ISAE 3000 (Revised) và ISAE 3410; GRI 302, GRI 305; GHG Protocol; ISA 315. [KTN]; URL không ghi.

**NLP cho tuyên bố môi trường và khí hậu**

- Webersinke, Kraus, Bingler, Leippold (2022 phiên bản 3). ClimateBERT. arXiv:2110.12010. https://arxiv.org/abs/2110.12010
- Varini, Boyd-Graber, Ciaramita, Leippold (2020). ClimaText. Workshop Tackling Climate Change with ML @ NeurIPS 2020. https://arxiv.org/abs/2012.00483
- Stammbach, Webersinke, Bingler, Kraus, Leippold (2023). Environmental Claim Detection. ACL 2023 (Vol. 2 Short), tr. 1051–1066. https://aclanthology.org/2023.acl-short.91/
- Schimanski và cs. (2023). ClimateBERT-NetZero. EMNLP 2023. URL không ghi.
- Schimanski và cs. (2024). ClimRetrieve. EMNLP 2024. URL không ghi.
- Ong và cs. (2025). A3CG. ACL 2025. aclanthology 2025.acl-long.723 (theo bảng bộ dữ liệu R8).
- Braun, Ong, Mao, Cambria, Mengaldo (2026). *Enhancing Language Models for Robust Greenwashing Detection*. arXiv:2601.21722, 29/01/2026.
- Yu, Scheidegger, Elliott, Löfgren (2024). climateBUG. *Expert Systems With Applications* 239, 122162. https://huggingface.co/datasets/lumilogic/climateBUG-Data
- Raspanti, Bardelli, Scala, Demirtaş, Di Bari, Filannino (2026). Greench-v1. NLP4Ecology 2026, tr. 79–86. https://aclanthology.org/2026.nlp4ecology-1.8/
- Kaoukis và cs. (2026). EmeraldMind. WWW 2026; arXiv:2512.11506.
- Calamai và cs. (2025; phiên bản 2, 01/2026). Khảo sát phát hiện tẩy xanh bằng NLP. Tên bài và URL không ghi.
- Bingler và cs. (2022). Đo "nói suông" và công bố chọn lọc trong công bố khí hậu. Nơi công bố và URL không ghi.

**Kiểm chứng tuyên bố, truy xuất và RAG**

- Thorne và cs. (2018). FEVER. NAACL 2018 (aclanthology N18-1074).
- Diggelmann, Boyd-Graber, Bulian, Ciaramita, Leippold (2020). CLIMATE-FEVER. Workshop NeurIPS 2020. https://arxiv.org/abs/2012.00614
- Schlichtkrull và cs. (2023). AVeriTeC. NeurIPS 2023. arXiv:2305.13117.
- VitaminC (2021). NAACL 2021 (aclanthology 2021.naacl-main.52). Tác giả không ghi trong ghi chú.
- Joren và cs. (2025). Sufficient Context. ICLR 2025. URL không ghi.
- Guo, Schlichtkrull & Vlachos (2022). Khảo sát kiểm chứng tự động. TACL 2022. URL không ghi.
- Lewis và cs. (2020). Retrieval-Augmented Generation. NeurIPS 2020. https://arxiv.org/abs/2005.11401
- Zhao và cs. (2026). *Understanding the Fundamental Design Decisions of Retrieval-Augmented Generation Systems*. ACM TOSEM 2026; arXiv:2411.19463 (v3; v1 có tên khác).
- Es, James, Espinosa-Anke, Schockaert (2025). RAGAS. arXiv:2309.15217 (v2, 28/04/2025).
- BEIR (Hole@10 của TAS-B 31,8% so với 6,4% của BM25); Lost in the Middle. Tác giả và URL không ghi trong ghi chú.
- Robertson & Zaragoza (2009), BM25; Cormack, Clarke & Büttcher (2009), RRF, SIGIR 2009. [KTN]; URL không ghi.
- Wang và cs. (2024). Multilingual E5. arXiv:2402.05672. VN-MTEB, Findings of EACL 2026. URL không ghi.

**Số học và bảng tài chính**

- Aarnes & Setty (2025). NumPert. Nơi công bố và URL không ghi. Aarnes & Setty (30/09/2026), cặp khác một con số; URL không ghi.
- Zhu và cs. (2021). TAT-QA. ACL 2021 (giấy phép: README ghi CC BY 4.0, bài báo ghi phi thương mại; hai nguồn mâu thuẫn). https://github.com/NExTplusplus/tat-qa
- Chen và cs. (2021). FinQA. EMNLP 2021. https://github.com/czyssrs/FinQA
- Zhao và cs. (2024). FinDVer. EMNLP 2024 (aclanthology 2024.emnlp-main.818).

**LLM làm người chấm, giải thích, hiệu chỉnh, người–máy**

- Zheng và cs. (2023). LLM-as-a-judge. NeurIPS 2023 D&B. Wang và cs. (2024). ACL 2024. Panickssery (tự ưu tiên). URL không ghi.
- Liu, Iter, Xu, Wang, Xu, Zhu (2023). G-Eval. arXiv:2303.16634 (v3, 23/05/2023).
- Gilardi, Alizadeh, Kubli (2023). *PNAS* 120(30) e2305016120; arXiv:2303.15056.
- To và cs. (2024). Dữ liệu kiểm chứng tiếng Việt do LLM sinh. URL không ghi.
- Jacovi & Goldberg (2020). ACL 2020, tr. 4198–4205. https://aclanthology.org/2020.acl-main.386/
- Turpin, Michael, Perez, Bowman (2023). NeurIPS 2023. arXiv:2305.04388.
- Geifman & El-Yaniv (2017). NeurIPS 2017. Chow (1970). [KTN]; URL không ghi.
- Guo, Pleiss, Sun, Weinberger (2017). ICML 2017. arXiv:1706.04599.
- Angelopoulos & Bates (v6, 07/12/2022). Conformal prediction. arXiv:2107.07511.
- Mohri & Hashimoto (2024). ICML 2024. Xiong (2024); Kamath (2020). URL không ghi.
- Bansal và cs. (2021). CHI 2021. Warren và cs. (2025). CHI 2025. Vasconcelos và cs. (2023). Commerford và cs. (2022). URL không ghi.
- Nielsen. Ten Usability Heuristics. https://www.nngroup.com/articles/ten-usability-heuristics/
- Brooke, SUS [TÌM, CHƯA XÁC MINH trên trang gốc]; Bangor và cs. (2009) trang trả lỗi 404, không dùng làm nguồn.
- Krippendorff α. https://en.wikipedia.org/wiki/Krippendorff%27s_alpha. Landis & Koch (1977); McHugh (2012); Feinstein & Cicchetti (1990); Miller (2024); Card (2020). URL không ghi.

**Tuân thủ quy tắc, tiêm lệnh, bộ nhớ**

- Mu và cs. (2024). RuLES. arXiv:2311.04235 (v3, 08/03/2024).
- Zhou và cs. (2023). IFEval. arXiv:2311.07911.
- Wallace và cs. (2024). The Instruction Hierarchy. arXiv:2404.13208.
- Greshake và cs. (2023). Tiêm lệnh gián tiếp. arXiv:2302.12173 (v2, 05/05/2023).
- Packer và cs. (2024). MemGPT. arXiv:2310.08560 (v2, 12/02/2024).
- Zhang và cs. (2026). Agentic Context Engineering (ACE). ICLR 2026; arXiv:2510.04618 (v3, 29/03/2026).

**Lượng tử**

- Farhi, Goldstone & Gutmann (2014). QAOA. arXiv:1411.4028.
- Herman và cs. (2023). Quantum computing for finance. *Nature Reviews Physics* 5: 450–465; arXiv:2201.02773.
- HSBC và IBM (25/09/2025), thông cáo về dự báo RFQ. Qua ghi chú R9 (tìm kiếm); URL không ghi.
- Toshiba. SQBM+ (Azure Quantum 06/2022; AWS Marketplace 02/2023; bản 2 11/2023). Qua ghi chú R9 (tìm kiếm); URL không ghi.
- Meichanetzidis và cs. (2020). QNLP trên máy NISQ. arXiv:2012.03756.
