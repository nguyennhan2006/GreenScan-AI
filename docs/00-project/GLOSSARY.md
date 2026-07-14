# Glossary — Greenwashing Detection

Tài liệu này chuẩn hóa thuật ngữ để ChatGPT, Claude Code và team phát triển dùng cùng một ngôn ngữ.

## A

### AI-assisted verification
Quy trình dùng AI để hỗ trợ trích xuất claim, tìm bằng chứng, đối chiếu, gợi ý verdict và điểm rủi ro. AI không thay thế reviewer cuối cùng.

### Audit trail
Dấu vết kiểm toán của một kết luận: claim gốc, nguồn tài liệu, trang, bằng chứng đã dùng, bằng chứng bị loại, điểm từng tiêu chí, người review và thời điểm review.

### Audit working paper
Hồ sơ làm việc nội bộ cho từng claim hoặc từng doanh nghiệp. Đây là tài liệu quan trọng để mô phỏng cách kiểm toán viên chấm thủ công và để tạo ground truth cho AI.

## B

### Baseline
Mốc gốc dùng để so sánh. Claim như “giảm phát thải 20%” chỉ có ý nghĩa nếu biết giảm so với năm nào, phạm vi nào và chỉ tiêu nào.

### BM25
Phương pháp truy xuất keyword/sparse retrieval. Phù hợp khi cần tìm thuật ngữ chính xác, mã văn bản, chỉ số, tên dự án, số liệu hoặc cụm từ pháp lý.

## C

### CAPEX xanh
Chi tiêu vốn được phân bổ cho dự án hoặc hoạt động được xem là xanh. Cần kiểm tra mục đích, dòng tiền và tiêu chí taxonomy.

### Carbon neutral
Tuyên bố trung hòa carbon. Cần kiểm tra phạm vi phát thải, phương pháp tính, offset, chứng chỉ và kế hoạch giảm phát thải thực chất.

### Claim
Một tuyên bố có thể kiểm chứng hoặc cần đánh giá. Trong dự án này, claim thường là câu doanh nghiệp tự mô tả về môi trường, ESG, bền vững, net-zero, năng lượng tái tạo, tín dụng xanh hoặc tuân thủ pháp lý.

### Claim extraction
Bước trích xuất các claim xanh từ báo cáo doanh nghiệp, website, thông cáo hoặc tài liệu tài chính.

### Claim-level risk score
Điểm rủi ro greenwashing cho từng claim, thường từ 0–100. Điểm càng cao thì rủi ro gây hiểu lầm càng lớn.

### Company-level risk score
Điểm tổng hợp ở cấp doanh nghiệp. Không nên chỉ lấy trung bình đơn giản; cần xem trọng số theo mức nghiêm trọng, số claim bị contradicted, claim tài chính xanh, claim pháp lý và mức thiếu minh bạch.

### Contradicted
Verdict cho trường hợp có bằng chứng mâu thuẫn trực tiếp với claim. Ví dụ claim nói phát thải giảm nhưng bảng Scope 1+2 tăng.

### CSR
Corporate Social Responsibility — trách nhiệm xã hội doanh nghiệp. Trong greenwashing, CSR có thể bị dùng để đánh tráo trọng tâm nếu doanh nghiệp nói nhiều về hoạt động cộng đồng nhưng né dữ liệu môi trường trọng yếu.

## D

### Data provenance
Nguồn gốc dữ liệu: tài liệu nào, trang nào, năm nào, bảng nào, link nào, phiên bản nào. Không có provenance thì không nên dùng làm bằng chứng mạnh.

### Disclosure
Thông tin doanh nghiệp công bố cho nhà đầu tư, cơ quan quản lý hoặc công chúng. Disclosure có thể nằm trong báo cáo thường niên, báo cáo ESG, BCTC, thông cáo hoặc hồ sơ phát hành.

## E

### ESG
Environmental, Social, Governance — môi trường, xã hội, quản trị. Dự án hiện tập trung chủ yếu vào claim môi trường và tài chính xanh, nhưng vẫn ghi nhận claim xã hội/quản trị nếu nó được dùng để đánh tráo trọng tâm.

### Evidence
Bằng chứng dùng để kiểm chứng claim. Có thể là số liệu, đoạn văn, bảng, văn bản pháp lý, giấy phép, quyết định xử phạt, BCTC, báo cáo kiểm toán hoặc nguồn ngoài.

### Evidence card
Thẻ hiển thị một claim cùng verdict, risk score, bằng chứng hỗ trợ/phản bác, nguồn, trang, dữ liệu thiếu và khuyến nghị kiểm tra. Đây là output trung tâm cho reviewer.

### Evidence-first
Nguyên tắc thiết kế: hệ thống đi từ claim đến bằng chứng trước khi kết luận. Không có bằng chứng truy vết được thì không đưa ra kết luận chắc chắn.

### Evidence grading
Đánh giá độ mạnh của bằng chứng. Ví dụ: kiểm toán độc lập/văn bản pháp lý mạnh hơn thông cáo báo chí; bảng số liệu có đơn vị và năm mạnh hơn câu marketing.

## F

### Financial greenwashing
Tẩy xanh tài chính. Xảy ra khi trái phiếu, khoản vay, quỹ, dự án hoặc doanh nghiệp được trình bày là xanh/ESG/bền vững nhưng thiếu bằng chứng về mục đích sử dụng vốn, dòng tiền, tiêu chí taxonomy hoặc dữ liệu môi trường thực chất.

## G

### GHG
Greenhouse gases — khí nhà kính. Thường đo bằng tCO2e.

### Green bond
Trái phiếu xanh. Cần kiểm tra use-of-proceeds, dự án sử dụng vốn, cơ chế theo dõi dòng tiền, báo cáo tác động và xác nhận độc lập nếu có.

### Green claim
Claim xanh. Một tuyên bố liên quan đến môi trường hoặc bền vững, ví dụ giảm phát thải, dùng năng lượng tái tạo, đạt tiêu chuẩn môi trường, net-zero, hoặc phát hành trái phiếu xanh.

### Green credit
Tín dụng xanh. Khoản tín dụng cấp cho dự án/hoạt động đáp ứng tiêu chí môi trường hoặc phân loại xanh theo quy định/chuẩn áp dụng.

### Green taxonomy
Hệ thống phân loại hoạt động/dự án nào được xem là xanh. Dự án dùng taxonomy để đối chiếu claim tài chính xanh hoặc dự án xanh.

### Greenwashing
Thực hành hoặc hành vi truyền thông gây hiểu lầm về hồ sơ môi trường/bền vững thực chất của tổ chức, sản phẩm hoặc dịch vụ. Trong dự án, greenwashing được đánh giá theo rủi ro và bằng chứng, không kết luận pháp lý tuyệt đối.

### Greenwashing risk
Mức rủi ro cho thấy claim có thể gây hiểu lầm vì thiếu cụ thể, thiếu bằng chứng, thiếu baseline, thiếu kiểm toán, mâu thuẫn dữ liệu hoặc phóng đại.

### GRI Standards
Bộ chuẩn báo cáo giúp tổ chức hiểu và báo cáo tác động của mình đối với kinh tế, môi trường và con người theo cách có thể so sánh và đáng tin cậy.

## H

### Human review
Bước chuyên gia/reviewer xem lại case khó, rủi ro cao hoặc thiếu dữ liệu. Reviewer có thể xác nhận, sửa hoặc bác verdict của AI.

## I

### IFRS Sustainability Disclosure Standards
Chuẩn disclosure bền vững do ISSB phát triển, nhằm cung cấp thông tin có ích, có thể so sánh toàn cầu cho nhà đầu tư.

### Insufficient evidence
Verdict cho trường hợp chưa đủ dữ liệu để kết luận. Khác với Unsupported: Unsupported nghĩa là không tìm thấy bằng chứng hỗ trợ đủ dùng; Insufficient evidence nghĩa là dữ liệu quá thiếu hoặc chất lượng quá thấp để đưa verdict mạnh.

### ISSB
International Sustainability Standards Board — hội đồng thuộc IFRS Foundation phát triển chuẩn disclosure bền vững.

## M

### Materiality
Tính trọng yếu. Một vấn đề được xem là trọng yếu nếu nó có ảnh hưởng đáng kể đến tác động môi trường, quyết định nhà đầu tư, nghĩa vụ pháp lý hoặc rủi ro tài chính.

### Metric normalization
Chuẩn hóa chỉ số, đơn vị, thời gian, phạm vi. Ví dụ chuyển kg CO2e sang tCO2e, xác định năm báo cáo, phân biệt Scope 1/2/3.

## N

### Negative evidence search
Tìm bằng chứng phản bác claim. Ví dụ với claim “tuân thủ pháp luật môi trường”, hệ thống phải tìm xử phạt, sự cố môi trường, giấy phép không phù hợp hoặc tin tức mâu thuẫn.

### Net-zero
Cam kết cân bằng phát thải ròng về 0. Cần kiểm tra phạm vi, năm mục tiêu, kế hoạch trung hạn, ngân sách, CAPEX, KPI, offset và kiểm toán.

## O

### OLAP-style query
Câu hỏi tổng hợp, cần phân tích nhiều tài liệu hoặc nhiều nguồn. Ví dụ: “Doanh nghiệp này có rủi ro greenwashing cao không?”

### OLTP-style query
Câu hỏi fact-based, có đáp án cụ thể. Ví dụ: “Scope 1 năm 2024 là bao nhiêu?”

## P

### Partially supported
Verdict cho claim có bằng chứng hỗ trợ một phần nhưng thiếu yếu tố quan trọng như baseline, phạm vi, mốc thời gian, kiểm toán hoặc bằng chứng pháp lý.

### Professional skepticism
Hoài nghi nghề nghiệp. Nguyên tắc kiểm toán: không mặc định claim xanh là đúng chỉ vì doanh nghiệp tự công bố; mọi kết luận phải có bằng chứng.

## R

### RAG
Retrieval-Augmented Generation — kỹ thuật kết hợp truy xuất tài liệu liên quan với mô hình ngôn ngữ để tạo câu trả lời có căn cứ. Trong dự án, RAG phục vụ tìm và sử dụng bằng chứng, không phải để sinh kết luận tự do.

### Reranking
Xếp hạng lại các bằng chứng truy xuất để chọn bằng chứng liên quan, đáng tin và ít nhiễu hơn.

### Risk score
Điểm rủi ro. Trong dự án, risk score thường là 0–100, điểm càng cao thì rủi ro greenwashing càng lớn.

## S

### Scope 1
Phát thải trực tiếp từ nguồn do doanh nghiệp sở hữu hoặc kiểm soát.

### Scope 2
Phát thải gián tiếp từ điện, nhiệt, hơi nước hoặc năng lượng mua ngoài.

### Scope 3
Phát thải gián tiếp khác trong chuỗi giá trị, ví dụ nhà cung cấp, vận chuyển, sử dụng sản phẩm, đầu tư hoặc danh mục cho vay.

### Supported
Verdict cho claim được hỗ trợ bởi bằng chứng trực tiếp, đáng tin, cùng kỳ, cùng phạm vi và đủ rõ.

## T

### Taxonomy alignment
Mức độ một dự án/hoạt động/khoản vốn phù hợp với tiêu chí phân loại xanh.

### tCO2e
Tấn CO2 tương đương. Đơn vị thường dùng để đo phát thải khí nhà kính.

## U

### Unsupported
Verdict cho claim không có bằng chứng đủ dùng để hỗ trợ. Không nhất thiết có bằng chứng phản bác; nếu có phản bác trực tiếp thì dùng Contradicted.

### Use-of-proceeds
Mục đích sử dụng vốn, đặc biệt quan trọng với trái phiếu xanh hoặc khoản vay xanh. Cần kiểm tra vốn có thực sự đi vào dự án xanh được công bố hay không.

## V

### Vector search
Truy xuất theo ngữ nghĩa bằng embedding. Phù hợp để tìm đoạn văn tương tự về ý nghĩa, dù không trùng từ khóa.

### Verdict
Kết luận kiểm chứng claim. Enum chuẩn của dự án gồm: Supported, Partially supported, Unsupported, Contradicted, Insufficient evidence.
