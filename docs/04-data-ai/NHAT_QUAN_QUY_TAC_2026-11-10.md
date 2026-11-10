# Nhất quán logic kiểm tra khi quy tắc của người dùng khác quy tắc chuẩn

**Ngày:** 10/11/2026 · **Trạng thái:** đã có code và test cho ba chỗ lệch; phần T1 mới có khung, chưa có nhãn thuộc tính.

## Vấn đề

Quy tắc chuẩn của GreenScan không phải lúc nào cũng là bản áp dụng đúng cho một doanh nghiệp. Hệ thống phải học được quy tắc riêng của người dùng **đúng mức**:
- ngoại lệ của một doanh nghiệp chỉ đổi kết quả của doanh nghiệp đó;
- logic kiểm tra thì không đổi.

Trước 10/11 có ba chỗ lệch:

| # | Chỗ lệch | Hậu quả |
|---|---|---|
| 1 | Quy ước nhận diện tuyên bố (CODEBOOK v1.1, Q6–Q17) nằm trong trọng số mô hình T1 | Người dùng có quy ước khác chỉ còn cách huấn luyện lại |
| 2 | Người soát ghi đè mà không ghi lý do, không ghi đang áp phiên bản quy tắc nào; mọi lần ghi đè đều thành nhãn | Ngoại lệ "quy tắc không hợp với DN này" bị dùng để dạy và chấm mô hình, nên mô hình học cách phá quy tắc ở mọi DN |
| 3 | Chưa có phép thử nhất quán giữa các gói quy tắc | Không chứng minh được ngoại lệ chỉ đổi đúng quy tắc nó nhắm tới |

Hướng xử lý giống các trợ lý doanh nghiệp kiểu Zalo OA: mô hình giữ năng lực chung; quy tắc riêng của từng doanh nghiệp là dữ liệu đưa vào lúc chạy, có phiên bản, không học vào trọng số.

## Đã làm

### Lệch 2: lý do ghi đè quyết định nhãn đi đâu

Code: [`src/quantum_gw/storage/reviews.py`](../../src/quantum_gw/storage/reviews.py).

| Lý do (bắt buộc khi ghi đè) | Nhãn đi đâu |
|---|---|
| Máy đọc sai (số, đơn vị, phạm vi, chủ thể) | `model`: được dạy và chấm mô hình |
| Máy bỏ sót hoặc chọn sai bằng chứng có trong kho | `model` |
| Quy tắc đúng nhưng không áp dụng cho DN hoặc trường hợp này | `rule`: góp ý cho gói quy tắc, **không** thành nhãn mô hình; bắt buộc nêu quy tắc |
| Quy tắc sai hoặc lỗi thời | `rule` |
| Ghi đè cũ, chưa có lý do | `unknown`: không dùng cho việc nào |

- Mỗi quyết định giữ `rule_context`: phiên bản bộ quy tắc pháp lý, các gói tổ chức, prompt, pipeline, cấu hình. Máy chủ chép từ bản ghi lượt chạy; phía trình duyệt không gửi được.
- `model_labels()` là nguồn nhãn duy nhất cho huấn luyện và chấm. [`tools/benchmark.py`](../../tools/benchmark.py) `--from-reviews` đã chuyển sang dùng nguồn này.
- `rule_feedback()` và API `GET /v1/reviews-export/rule-feedback` là hàng đợi cho người giữ gói quy tắc, gom theo quy tắc. Mỗi góp ý vẫn phải qua đường cũ: soạn nháp → người duyệt → test → tăng phiên bản gói.
- Thống kê tách tỷ lệ ghi đè thành `model_error_rate` (máy đọc sai) và `rule_mismatch_rate` (quy tắc không hợp).
- Giao diện ([`DecisionBar.jsx`](../../frontend/src/components/DecisionBar.jsx)): ô "vì sao máy sai"; khi lý do là quy tắc thì có ô chọn quy tắc, gợi ý từ các quy tắc đã chạy trên tuyên bố. Giấy làm việc in kèm lý do.

### Lệch 3: phép thử nhất quán

[`tests/test_rule_consistency.py`](../../tests/test_rule_consistency.py) kiểm bốn điều:
- Cùng câu và cùng gói thì cho cùng kết quả, kể cả khi nạp lại gói.
- Thứ tự các gói không đổi kết quả.
- Gói của DN B bỏ một quy tắc thì chỉ quy tắc đó đổi, mọi quy tắc khác giữ nguyên.
- Mọi kết quả ghi phiên bản gói, mã quy tắc và điều khoản nguồn.

### Lệch 1: khung tách T1 thành thuộc tính và quy ước

Code: [`src/quantum_gw/domain/claim_attributes.py`](../../src/quantum_gw/domain/claim_attributes.py) · quy ước: [`configs/claim_policy/codebook_v1_1.yaml`](../../configs/claim_policy/codebook_v1_1.yaml) · test: [`tests/test_claim_attributes.py`](../../tests/test_claim_attributes.py).

Mô hình chỉ đọc 9 thuộc tính của câu:
- hình thức: câu, ô bảng hay câu vỡ;
- chủ thể: DN, tổ chức khác hay dự án khách hàng;
- có nội dung môi trường không;
- có phải kiến thức chung không;
- loại câu: hành động, quy trình ESG, giải thưởng, tuân thủ hay nói về báo cáo;
- có cụ thể không;
- số liệu: không có, đo lường hay số đếm;
- có phải mục tiêu không;
- mục tiêu có năm không.

`compose_label` ghép các thuộc tính thành nhãn bằng code, theo tệp quy ước. Sáu quy ước người dùng có thể đặt khác:

| Khoá | Mặc định (CODEBOOK v1.1) | Mã |
|---|---|---|
| `year_only_target` | mục tiêu chỉ có năm → định tính | Q6 |
| `count_is_quantity` | số đếm kết quả môi trường → có số | Q10 |
| `esg_process_is_claim` | quy trình ESG của DN → tuyên bố (nhóm người chưa chốt) | Q12 |
| `award_is_claim` | giải thưởng bền vững → tuyên bố | Q11 |
| `compliance_is_claim` | khẳng định tuân thủ → tuyên bố | Q17 |
| `client_project_is_claim` | dự án khách hàng → không phải tuyên bố | Q15 |

Đã kiểm bằng test:
- Quy ước mặc định cho đúng nhãn của 18 ví dụ trong CODEBOOK.
- Đổi một khoá thì chỉ đúng câu thuộc quy ước đó đổi nhãn.
- Mỗi nhãn ghi các khoá đã quyết định nó. Nhờ vậy người soát thấy ngay máy đọc sai (một thuộc tính sai) hay quy ước không hợp (một khoá), đúng như cách tách ở lệch 2.

## Chưa làm, cần duyệt trước

| Việc | Vì sao chưa | Cần gì |
|---|---|---|
| Gán thuộc tính cho 2.055 câu T1 và cho gold lô 1 | Tốn lượt gọi mô hình thầy hoặc công người gán | Đồng ý ngân sách; nên chờ gold lô 1 gộp xong để chốt Q10–Q17 trước |
| Kiểm ghép thuộc tính → nhãn có khớp nhãn hiện có không | Cần bước trên | Mục tiêu: khớp ≥ 95% với nhãn Claude trên câu thầy nhất quán; câu lệch là chỗ CODEBOOK chưa rõ |
| Huấn luyện T1 đọc thuộc tính (đa nhãn) thay cho 4 lớp | Cần nhãn thuộc tính | Cùng chia theo DN, cùng cổng ở `configs/measurement_decisions.yaml` |
| Cho gói tổ chức mang quy ước T1 riêng | Đụng lược đồ org-pack-v0 (khoá lạ đang bị từ chối, có chủ ý) | Thêm khoá `claim_policy` ở org-pack-v1, kèm test từ chối |
