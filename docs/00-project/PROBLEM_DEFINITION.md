# Problem Definition — Greenwashing Detection trong tài chính Việt Nam

## 1. Bối cảnh vấn đề

Tài chính xanh tại Việt Nam đang tăng trưởng cùng với nhu cầu huy động vốn cho chuyển đổi xanh, tín dụng xanh, trái phiếu xanh và dự án đáp ứng tiêu chí môi trường. Khi dòng vốn “xanh” tăng lên, rủi ro các tổ chức hoặc doanh nghiệp sử dụng ngôn ngữ bền vững để tạo hình ảnh tích cực hơn so với thực chất cũng tăng theo.

Greenwashing trong tài chính không chỉ là quảng cáo sai. Nó có thể ảnh hưởng đến:

- quyết định đầu tư,
- quyết định cấp tín dụng,
- định giá doanh nghiệp,
- uy tín của trái phiếu xanh/khoản vay xanh,
- niềm tin vào thị trường tài chính bền vững.

Theo cách hiểu của ESMA/ESAs, greenwashing xảy ra khi tuyên bố, hành động hoặc truyền thông liên quan đến bền vững không phản ánh rõ ràng và công bằng hồ sơ bền vững thực chất của tổ chức, sản phẩm tài chính hoặc dịch vụ tài chính, và có thể gây hiểu lầm cho người tiêu dùng, nhà đầu tư hoặc các bên tham gia thị trường.

## 2. Khoảng trống hiện tại

Trong bối cảnh Việt Nam, greenwashing chưa được vận hành như một bài toán kiểm chứng dữ liệu có chuẩn thống nhất ở cấp doanh nghiệp. Nhiều claim trong báo cáo ESG hoặc báo cáo thường niên có thể:

- mơ hồ,
- thiếu số liệu,
- thiếu baseline,
- thiếu kiểm toán độc lập,
- chọn lọc thông tin có lợi,
- không chứng minh được dòng tiền xanh,
- mâu thuẫn với dữ liệu môi trường, tài chính, pháp lý hoặc nguồn ngoài.

Điều này tạo ra nhu cầu xây dựng hệ thống hỗ trợ kiểm tra claim theo hướng evidence-first.

## 3. Định nghĩa bài toán

Bài toán được định nghĩa là:

> Xây dựng hệ thống AI hỗ trợ phân tích và kiểm chứng thông tin ESG trong bối cảnh tài chính Việt Nam. Với đầu vào là tài liệu công bố của doanh nghiệp và dữ liệu đối chiếu từ pháp lý, môi trường, tài chính và nguồn bên ngoài, hệ thống cần trích xuất tuyên bố xanh, truy xuất bằng chứng liên quan, đánh giá mức độ nhất quán giữa tuyên bố và bằng chứng, sau đó đưa ra điểm rủi ro greenwashing kèm giải thích có căn cứ.

## 4. Định nghĩa theo ba lớp

### Lớp 1 — Greenwashing chung

Greenwashing là hành vi hoặc thực hành truyền thông trong đó doanh nghiệp/tổ chức đưa ra tuyên bố môi trường hoặc bền vững gây hiểu lầm, phóng đại, thiếu bằng chứng, chọn lọc thông tin có lợi hoặc dùng hình ảnh/ngôn ngữ “xanh” để tạo cảm nhận tích cực hơn so với tác động thực tế.

### Lớp 2 — Greenwashing trong tài chính

Greenwashing tài chính xảy ra khi doanh nghiệp, tổ chức phát hành, quỹ đầu tư, ngân hàng hoặc sản phẩm tài chính được trình bày là “xanh”, “ESG”, “bền vững”, “net-zero”, “carbon neutral”, nhưng thông tin công bố:

- không đủ rõ,
- không có bằng chứng định lượng,
- không phù hợp tiêu chí phân loại xanh,
- không theo dõi được dòng tiền xanh,
- hoặc mâu thuẫn với dữ liệu môi trường/tài chính/pháp lý.

### Lớp 3 — Định nghĩa cho hệ thống AI

**Greenwashing risk** là điểm rủi ro cho thấy mức độ không nhất quán giữa:

1. tuyên bố xanh trong văn bản doanh nghiệp,
2. bằng chứng định lượng: phát thải, năng lượng, nước, chất thải, CAPEX xanh, doanh thu xanh,
3. bằng chứng pháp lý: giấy phép môi trường, xác nhận dự án xanh, vi phạm/xử phạt,
4. dữ liệu tài chính: trái phiếu xanh, khoản vay xanh, mục đích sử dụng vốn, tracking dòng tiền,
5. dữ liệu bên ngoài: tin tức, xử phạt, báo cáo kiểm toán, xác nhận độc lập.

## 5. Các dạng greenwashing cần phát hiện

| Dạng | Mô tả | Tín hiệu ví dụ |
|---|---|---|
| Tuyên bố mơ hồ | Dùng từ “xanh”, “bền vững”, “thân thiện”, “có trách nhiệm” nhưng không có chỉ số hoặc phạm vi rõ | “Chúng tôi luôn hướng tới môi trường xanh” |
| Không có bằng chứng | Có claim nhưng thiếu số liệu, thiếu tài liệu xác nhận, thiếu nguồn | Không có GHG, năng lượng, nước, chất thải |
| Chọn lọc thông tin | Nêu thành tựu nhỏ, né tác động lớn hoặc chỉ công bố phần có lợi | Nêu trồng cây nhưng không nêu phát thải tăng |
| Mâu thuẫn định lượng | Claim nói giảm/cải thiện nhưng số liệu lại tăng/xấu đi | Scope 1+2 tăng nhưng vẫn nói “giảm mạnh” |
| Mâu thuẫn pháp lý | Tự nhận tuân thủ/xanh nhưng có xử phạt, giấy phép không phù hợp hoặc dự án không đạt tiêu chí | Có quyết định xử phạt môi trường |
| Tẩy xanh tài chính | Trái phiếu/khoản vay xanh nhưng mục đích sử dụng vốn không rõ hoặc dự án không thuộc taxonomy | Không tracking dòng tiền xanh |
| Cam kết tương lai rỗng | Net-zero/ESG target không có lộ trình, ngân sách, KPI trung hạn | “Net Zero 2050” nhưng không có kế hoạch 2030 |
| Đánh tráo trọng tâm | Nói nhiều về CSR xã hội/từ thiện để che vấn đề môi trường trọng yếu | Tặng quà cộng đồng nhưng né dữ liệu phát thải |
| Gắn nhãn xanh quá mức | Gọi sản phẩm/dự án là xanh khi chỉ đáp ứng yêu cầu tối thiểu hoặc không chứng minh được tiêu chí | “Eco-friendly” không có chứng chỉ/chuẩn đo |

## 6. Input của hệ thống

| Nhóm dữ liệu | Ví dụ | Vai trò |
|---|---|---|
| Báo cáo doanh nghiệp | Báo cáo thường niên, báo cáo ESG, báo cáo phát triển bền vững | Nguồn chứa claim xanh và số liệu tự công bố |
| Dữ liệu tài chính | BCTC, thuyết minh, CAPEX, trái phiếu xanh, khoản vay xanh | Kiểm tra dòng tiền, mục đích sử dụng vốn, chi phí môi trường |
| Dữ liệu môi trường | GHG, năng lượng, nước, chất thải, giấy phép môi trường | Kiểm tra tác động và số liệu vận hành |
| Dữ liệu pháp lý | Luật BVMT, Thông tư 17, Quyết định 21/2025, văn bản chứng khoán | Đối chiếu nghĩa vụ và tiêu chí xanh |
| Dữ liệu bên ngoài | Tin tức, xử phạt, HOSE/HNX/SSC, báo cáo kiểm toán | Tìm mâu thuẫn ngoài báo cáo |
| Dữ liệu chuẩn hóa | GRI, ISSB, SASB, ASEAN Taxonomy, Vietnam Green Taxonomy | Chuẩn hóa chỉ tiêu, materiality và taxonomy |

## 7. Output của hệ thống

| Output | Ý nghĩa |
|---|---|
| Danh sách claim xanh | Các câu doanh nghiệp tự tuyên bố về ESG/môi trường/tài chính xanh |
| Loại claim | Emission, energy, waste, water, green finance, net-zero, legal compliance, vague ESG, CSR |
| Bằng chứng liên quan | Số liệu, đoạn văn, bảng, văn bản pháp lý, nguồn ngoài |
| Verdict | Supported / Partially supported / Unsupported / Contradicted / Insufficient evidence |
| Điểm rủi ro | 0–100 hoặc Low/Medium/High/Critical |
| Giải thích | Vì sao claim có rủi ro, thiếu gì, mâu thuẫn ở đâu |
| Khuyến nghị kiểm tra | Cần kiểm toán, Scope 1/2/3, baseline, xác nhận taxonomy, use-of-proceeds |
| Audit trail | Claim gốc, nguồn, trang, bằng chứng đã dùng, người review, thời điểm review |

## 8. Tiêu chí chấm điểm thủ công ban đầu

| Tiêu chí | Điểm rủi ro tối đa |
|---|---:|
| Claim có cụ thể không? | 15 |
| Có số liệu định lượng không? | 15 |
| Có baseline và mốc thời gian không? | 10 |
| Có bằng chứng tài chính/môi trường/pháp lý không? | 20 |
| Có xác nhận độc lập/kiểm toán không? | 10 |
| Có mâu thuẫn với dữ liệu khác không? | 20 |
| Có dấu hiệu ngôn ngữ phóng đại/mơ hồ không? | 10 |

Tổng điểm rủi ro claim-level: **0–100**.

## 9. Verdict chuẩn

| Verdict | Khi dùng |
|---|---|
| Supported | Claim được hỗ trợ bởi bằng chứng trực tiếp, cùng kỳ, cùng phạm vi, đáng tin cậy |
| Partially supported | Có bằng chứng hỗ trợ nhưng thiếu một phần: baseline, phạm vi, kiểm toán, dữ liệu phụ |
| Unsupported | Không tìm thấy bằng chứng đủ dùng để hỗ trợ claim |
| Contradicted | Có bằng chứng mâu thuẫn trực tiếp với claim |
| Insufficient evidence | Không đủ dữ liệu để kết luận, cần yêu cầu thêm hồ sơ |

## 10. Ranh giới an toàn

Hệ thống không được:

- tuyên bố chắc chắn doanh nghiệp “gian lận” nếu chỉ có risk signal,
- thay thế kiểm toán viên hoặc cơ quan quản lý,
- sinh bằng chứng không có nguồn,
- chấm điểm claim định lượng khi không có đơn vị đo/phạm vi/năm,
- xem ngôn ngữ marketing là bằng chứng.

Hệ thống nên:

- luôn hiển thị nguồn và trang,
- nêu rõ dữ liệu còn thiếu,
- tách “rủi ro greenwashing” khỏi “kết luận vi phạm pháp luật”,
- đẩy case high-risk hoặc low-confidence sang human review.

## 11. Câu hỏi nghiên cứu mở

1. Làm thế nào để đo độ mạnh của bằng chứng ESG trong báo cáo không kiểm toán?
2. Nên tính company-level score bằng trung bình, trọng số hay worst-case aggregation?
3. Với claim định tính, tiêu chí nào giúp phân biệt “mơ hồ nhưng vô hại” và “mơ hồ gây hiểu lầm”?
4. Negative evidence search nên ưu tiên nguồn nào tại Việt Nam?
5. Có thể chuẩn hóa claim taxonomy theo ngành không: ngân hàng, bất động sản, sản xuất, năng lượng, thép/xi măng?
