# Project Brief — Greenwashing Detection

## 1. Tên dự án

**Greenwashing Detection — Evidence-first ESG Verification System**

Tên ngắn: **GW Detection**

## 2. Mô tả ngắn

Dự án xây dựng một hệ thống AI hỗ trợ phát hiện sớm rủi ro **greenwashing** trong tài liệu công bố của doanh nghiệp, đặc biệt trong bối cảnh tài chính xanh tại Việt Nam. Hệ thống không chỉ đọc báo cáo ESG hoặc báo cáo thường niên, mà đi theo hướng **evidence-first**: trích xuất tuyên bố xanh, truy xuất bằng chứng, đối chiếu với số liệu/pháp lý/tài chính/nguồn ngoài, rồi đưa ra verdict và điểm rủi ro có giải thích truy vết được.

## 3. Bối cảnh

Việt Nam đang phát triển nhanh các hoạt động tài chính xanh như tín dụng xanh, trái phiếu xanh và phân loại xanh. Điều này tạo ra nhu cầu kiểm chứng xem các tuyên bố “xanh”, “ESG”, “bền vững”, “net-zero” hoặc “carbon neutral” có được hỗ trợ bởi bằng chứng thực chất hay chỉ là truyền thông gây cảm nhận tích cực.

Ở tầng quốc tế, ESMA/ESAs mô tả greenwashing là thực hành trong đó các tuyên bố, hành động hoặc truyền thông liên quan đến bền vững không phản ánh rõ ràng và công bằng hồ sơ bền vững thực chất của một tổ chức, sản phẩm tài chính hoặc dịch vụ tài chính, từ đó có thể gây hiểu lầm cho người tiêu dùng, nhà đầu tư hoặc bên tham gia thị trường.

Ở tầng Việt Nam, bối cảnh pháp lý liên quan đến tín dụng xanh, trái phiếu xanh, quản lý rủi ro môi trường và phân loại xanh đang rõ dần, nhưng greenwashing chưa phải là một chế định riêng được gọi tên trực tiếp trong một đạo luật chuyên biệt. Đây là khoảng trống khiến một hệ thống AI hỗ trợ kiểm chứng sớm có giá trị thực tiễn.

## 4. Vấn đề cần giải quyết

Doanh nghiệp có thể đưa ra nhiều tuyên bố xanh trong báo cáo và truyền thông, nhưng người tiêu dùng, nhà đầu tư, ngân hàng, kiểm toán viên hoặc reviewer khó kiểm tra nhanh:

- Claim có cụ thể hay chỉ mơ hồ?
- Có số liệu định lượng không?
- Có baseline, mốc thời gian, phạm vi đo không?
- Có bằng chứng tài chính/môi trường/pháp lý không?
- Có mâu thuẫn với bảng số liệu, báo cáo tài chính, giấy phép, xử phạt hoặc tin tức bên ngoài không?
- Nếu claim thiếu bằng chứng hoặc bị mâu thuẫn, mức rủi ro greenwashing là bao nhiêu?

## 5. Mục tiêu sản phẩm

Hệ thống cần hỗ trợ người dùng:

1. Nạp tài liệu doanh nghiệp và nguồn đối chiếu.
2. Trích xuất các claim xanh/ESG/môi trường/tài chính xanh.
3. Phân loại claim theo taxonomy nghiệp vụ.
4. Truy xuất bằng chứng hỗ trợ và bằng chứng phản bác.
5. Kiểm chứng claim theo quy trình nhiều lớp.
6. Gán verdict và risk score.
7. Hiển thị evidence card để reviewer truy vết lại nguồn.
8. Xuất báo cáo phục vụ phân tích, kiểm toán sơ bộ hoặc thẩm định.

## 6. Người dùng mục tiêu

| Persona | Nhu cầu chính | Output cần xem |
|---|---|---|
| Nhà đầu tư cá nhân | Kiểm tra doanh nghiệp/quỹ có đang phóng đại tính xanh không | Dashboard, risk score, claim nổi bật |
| Analyst / Researcher | So sánh nhiều doanh nghiệp theo dữ liệu ESG và bằng chứng | Bảng claim, evidence card, nguồn trích dẫn |
| Ngân hàng / tổ chức tín dụng | Đối chiếu khoản vay xanh, dự án xanh, rủi ro môi trường | Verification report, legal/taxonomy alignment |
| Kiểm toán viên / reviewer ESG | Kiểm tra claim, đánh giá bằng chứng, sign-off case khó | Audit working paper, reviewer queue |
| Cơ quan quản lý / giảng viên / hội đồng | Xem phương pháp, minh bạch logic đánh giá | Report, explanation, scoring rubric |

## 7. Nguyên tắc thiết kế

### 7.1 Evidence-first

Không kết luận chỉ dựa trên ngôn ngữ trong báo cáo. Mọi verdict phải dựa trên bằng chứng có nguồn, trang, năm, đơn vị đo hoặc link truy vết.

### 7.2 Human-in-the-loop

AI hỗ trợ trích xuất, truy xuất, đối chiếu và gợi ý điểm. Với case rủi ro cao, thiếu bằng chứng hoặc có mâu thuẫn, reviewer phải được quyền xác nhận/bác bỏ verdict.

### 7.3 Auditability

Mọi kết luận phải có audit trail: claim gốc, bằng chứng dùng, bằng chứng bị loại, logic điểm, người review, thời điểm review.

### 7.4 Không thay thế kết luận pháp lý

Hệ thống đưa ra **risk assessment**, không kết luận doanh nghiệp vi phạm pháp luật hoặc gian lận nếu chưa có thẩm quyền/kiểm toán chính thức.

## 8. Phạm vi MVP

### In scope

- Upload tài liệu doanh nghiệp: PDF/text/markdown/mock JSON.
- Parse tài liệu thành chunks có provenance.
- Trích xuất claim xanh bằng rule/LLM/mocking layer.
- Phân loại claim cơ bản: emission, energy, waste, water, green finance, net-zero, legal compliance, vague ESG, CSR.
- Truy xuất bằng chứng trong kho nội bộ bằng hybrid retrieval hoặc mock retrieval.
- Gán verdict: Supported, Partially supported, Unsupported, Contradicted, Insufficient evidence.
- Chấm risk score 0–100 theo rubric thủ công.
- Evidence card và dashboard demo.
- Human review queue cho case high-risk/uncertain.

### Out of scope giai đoạn đầu

- Kết luận pháp lý chính thức.
- Thu thập tự động toàn bộ báo cáo tài chính từ mọi nguồn thị trường.
- Crawling tin tức thời gian thực quy mô lớn.
- Fine-tuning mô hình riêng.
- Chấm điểm ESG toàn diện thay cho rating agency.

## 9. Output sản phẩm

| Output | Ý nghĩa |
|---|---|
| Claim list | Danh sách các tuyên bố xanh được trích xuất |
| Claim taxonomy | Loại claim và dạng greenwashing tiềm năng |
| Evidence card | Claim, verdict, bằng chứng, nguồn, trang, dữ liệu thiếu |
| Risk score | Điểm rủi ro claim-level và company-level |
| Dashboard | Tổng quan số claim, phân bố verdict, top rủi ro |
| Report | Báo cáo xuất file có giải thích và phụ lục trích dẫn |
| Audit working paper | Hồ sơ nội bộ phục vụ reviewer/kiểm toán thủ công |

## 10. Success metrics

| Nhóm metric | Metric đề xuất |
|---|---|
| Claim extraction | Precision/recall của claim được trích xuất |
| Evidence retrieval | Recall@k của bằng chứng liên quan; citation accuracy |
| Verification | Agreement với reviewer; tỷ lệ verdict đúng |
| Explainability | Reviewer hiểu được lý do verdict; số verdict không truy vết được |
| Usability | Thời gian reviewer kiểm tra một claim; số click đến bằng chứng nguồn |
| Safety | Tỷ lệ hallucinated evidence; số kết luận thiếu căn cứ |

## 11. Nguồn nền tảng

- ESMA / ESAs: common understanding of greenwashing trong tài chính.
- IFRS / ISSB: chuẩn disclosure hướng tới thông tin hữu ích cho nhà đầu tư.
- GRI: chuẩn báo cáo tác động kinh tế, môi trường, con người.
- ASEAN Taxonomy: taxonomy khu vực cho tài chính bền vững.
- Bối cảnh Việt Nam: Luật BVMT 2020, Thông tư 17/2022/TT-NHNN, Quyết định 21/2025/QĐ-TTg, các văn bản công bố thông tin và chứng khoán liên quan.

## 12. Working hypothesis

Một hệ thống evidence-first có thể hỗ trợ phát hiện sớm greenwashing tốt hơn chatbot ESG thông thường vì nó buộc mỗi claim phải đi qua các bước: claim extraction → evidence retrieval → contradiction search → verification → scoring → human review.
