# Chương 3. Phát biểu bài toán và thiết kế hệ thống

Chương này trả lời hai câu hỏi: bài toán "kiểm chứng tuyên bố môi trường theo hướng bằng chứng trước" được phát biểu hình thức như thế nào, và hệ thống GreenScan được thiết kế ra sao để đáp ứng phát biểu đó. Mô tả bám theo mã nguồn tại thời điểm viết (05/11/2026); chỗ tài liệu và mã không khớp thì mã được coi là đúng và chỗ lệch được ghi rõ ở mục 3.12.

Chương không báo cáo kết quả đo. Các con số về chất lượng nằm ở chương 5; số xuất hiện trong chương này là tham số cấu hình (ngưỡng, trọng số) hoặc số đếm của hệ thống, kèm nguồn.

## 3.1 Phát biểu bài toán

### 3.1.1 Đầu vào

Một *lượt phân tích* nhận một tập hữu hạn tài liệu D = {d₁, …, dₙ}. Mỗi tài liệu dᵢ là một cặp (rᵢ, sᵢ) cùng nội dung:

- vai trò rᵢ ∈ {`claim_source`, `evidence`, `reference`}. Tài liệu `claim_source` là tài liệu đang được soát (báo cáo thường niên, báo cáo phát triển bền vững, bản cáo bạch); tài liệu `evidence` là tài liệu đối chiếu; `reference` là tài liệu tham chiếu chung (`src/quantum_gw/domain/enums.py`);
- loại nguồn sᵢ ∈ {`internal`, `financial`, `environmental`, `legal`, `external`, `standard`}. Loại nguồn quyết định một đoạn có được tính là *độc lập* với doanh nghiệp hay không (ví dụ `legal`, `standard`, `external`);
- định dạng: PDF chữ hoặc scan, DOCX, HTML, URL.

Từ D, hệ thống rút ra tập tuyên bố C = {c₁, …, c_m}. Mỗi tuyên bố cⱼ là một câu (hoặc một phần câu sau khi tách) lấy từ tài liệu `claim_source`, mang năm thuộc tính: chỉ số, giá trị kèm đơn vị, kỳ báo cáo, phạm vi hoặc ranh giới, năm gốc. Thuộc tính nào không có trong câu thì để trống; thiếu thuộc tính là một thông tin, không phải lỗi. Phạm vi của luận văn là các tuyên bố môi trường định lượng và định tính của doanh nghiệp Việt Nam; hệ thống không đánh giá doanh nghiệp.

### 3.1.2 Đầu ra

Với mỗi tuyên bố cⱼ, hệ thống trả về một bản ghi gồm sáu phần:

1. **Kết luận** vⱼ ∈ V = {`SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `UNSUPPORTED`, `INSUFFICIENT_EVIDENCE`}.
2. **Bằng chứng** Eⱼ, danh sách các đoạn kèm nguồn gốc: `doc_id`, `chunk_id`, số trang, nguyên văn, điểm truy xuất, quan hệ với tuyên bố (ủng hộ, một phần, mâu thuẫn, không liên quan) và *phương pháp* đã quyết quan hệ đó (số học, cụm từ, xu hướng, mô hình).
3. **Điểm rủi ro** ρⱼ ∈ [0, 100] cùng *phân rã* theo 9 thành phần (mục 3.7).
4. **Gợi ý sửa** Sⱼ, các đề xuất chỉnh câu tuyên bố (mục 3.9).
5. **Phát hiện của tổ chức** Oⱼ, kết quả áp các quy tắc nội bộ của người dùng, rỗng nếu không bật org pack (mục 3.8).
6. **Vị trí trong hàng đợi** và lý do tiếng Việt; không phải kết luận.

Ở cấp lượt chạy, hệ thống còn trả trạng thái phát hành ∈ {`BLOCKED`, `PENDING_HUMAN_REVIEW`, `RELEASABLE`}, `manifest.json` (mã băm đầu vào, phiên bản cấu hình) và giấy làm việc.

Không có kết luận ở cấp doanh nghiệp: đơn vị trung tâm luôn là tuyên bố (bất biến 1, mục 3.4).

### 3.1.3 Mục tiêu tối ưu

Gọi A ⊆ C là tập tuyên bố mà hệ thống *dám kết luận*, tức vⱼ ∈ {`SUPPORTED`, `CONTRADICTED`}. Các nhãn còn lại là cách hệ thống nhường quyết định cho người. Gọi vⱼ* là kết luận đúng theo chuẩn tham chiếu (nhãn đã duyệt, ca dựng có đáp án). Định nghĩa:

- **Độ phủ** cov = |A| / |C|.
- **Kết luận sai nguy hiểm**, hai loại: (a) `SUPPORTED` sai: hệ thống xác nhận một tuyên bố mà chuẩn tham chiếu cho là không được ủng hộ hoặc bị bác; (b) `CONTRADICTED` sai: hệ thống bác một tuyên bố mà chuẩn tham chiếu không cho là bị bác. Ký hiệu D_S và D_C là số lỗi loại (a) và (b).

Bài toán là cực đại hoá độ phủ với ràng buộc về lỗi nguy hiểm:

  max cov(π)  với  D_S(π)/|A(π)| ≤ ε_S  và  D_C(π)/|A(π)| ≤ ε_C,

trong đó π là chính sách kết luận (toàn bộ đường xử lý và ngưỡng), ε_S và ε_C là các ngưỡng đăng ký trước. Nói cách khác, precision trên phần dám kết luận là ràng buộc, còn độ phủ là thứ được tối đa hoá. Nhãn `PARTIALLY_SUPPORTED`, `UNSUPPORTED` và `INSUFFICIENT_EVIDENCE` không bị tính là lỗi nguy hiểm; chúng có chi phí khác, là công người soát, và được đo ở chương 4–5 qua số tuyên bố chuyển người. Giá trị cụ thể của ε_S, ε_C và cách đo nằm ở chương 4; không ngưỡng nào được phát biểu hay báo cáo ở chương này.

Phát biểu này quyết định cách thiết kế: mọi chỗ có thể sai nguy hiểm đều bị đặt sau một cổng tất định hoặc bị hạ xuống "chuyển người". Mục 3.4 cho thấy mỗi bất biến phục vụ ràng buộc nào.

## 3.2 Yêu cầu thiết kế

Từ phát biểu trên và từ nhu cầu của người dùng đã nêu ở chương 1 (kiểm toán viên, cán bộ tín dụng, doanh nghiệp), rút ra năm yêu cầu.

| Yêu cầu | Nội dung | Cơ chế chính |
|---|---|---|
| R1. Đúng trên phần dám kết luận | Hai loại lỗi nguy hiểm bị chặn trước độ phủ | Thứ tự thẩm quyền số học → cụm từ → xu hướng → tương đồng; mô hình không được tự quyết (mục 3.5) |
| R2. Biết nhường người | `INSUFFICIENT_EVIDENCE` là kết quả hợp lệ; thiếu dữ liệu không bị tính là thất bại | Bất biến 6, 8; cổng G5; hàng đợi |
| R3. Truy vết | Mỗi kết luận chỉ ra được đoạn gốc, trang, phép tính, quy tắc | Bất biến 2, 10; `contract/`, `audit.jsonl`, `manifest.json` |
| R4. Riêng tư | Tài liệu nội bộ không rời máy nếu người dùng không cho phép | Chế độ `offline`, danh mục dữ liệu rời máy (mục 3.11) |
| R5. Chạy trên laptop | Không cần GPU; một lệnh khởi động | Truy xuất `lite`, OCR tại máy, giao diện và API cùng cổng 127.0.0.1:8000 |

Hai yêu cầu R1 và R2 mâu thuẫn nhau ở rìa: nhường người nhiều thì độ phủ thấp. Hệ thống không giải mâu thuẫn bằng một ngưỡng duy nhất mà bằng cấu trúc: có những loại bằng chứng được phép quyết (số học, cụm từ xác nhận đúng chỉ số), còn lại luôn chuyển người.

## 3.3 Nguyên lý: mô hình đọc, quy tắc quyết, người duyệt

Ba vai được tách bạch.

- **Mô hình đọc.** Mô hình (bộ truy xuất, hoặc mô hình ngôn ngữ khi được bật) chỉ ra đoạn nào đáng xem và gợi ý quan hệ. Mô hình không đứng một mình thành kết luận.
- **Quy tắc quyết.** Số học, so khớp cụm từ, chiều thay đổi, áp dụng pháp lý là mã tất định có tham số công khai. Kết luận nào là `SUPPORTED` hay `CONTRADICTED` đều chỉ ra được phép tính hoặc quy tắc đã chạy.
- **Người duyệt.** Quyết định của người soát được ghi chỉ-thêm (`.quantum/reviews/decisions.jsonl`: `AI_SUGGESTED` → `HUMAN_REVIEWED` → `FINALIZED`) và là tiếng nói cuối.

Lý do chọn nguyên lý này không phải sở thích kiến trúc mà là bài học từ lỗi đã đo ở các vòng trước: ngày 22/09 trong 8 mâu thuẫn do bộ so sánh cũ báo, 5 mâu thuẫn là so hai đại lượng khác phạm vi (ví dụ Scope 1+2 với Scope 1); bộ so sánh cũ chỉ kiểm đơn vị (`docs/00-project/ARCHITECTURE_INVARIANTS.md`; kiểm lại bằng `tools/hpg_semantic_audit.py`, kết quả 25/09 ở `benchmark/semantic_audit_2026-09-25.md`: không mâu thuẫn nào của bản cũ còn đứng vững). Ngày 28/09, khi cho mô hình tự quyết trên Hòa Phát, xuất hiện 10 `CONTRADICTED` và 2 mức CRITICAL ở một doanh nghiệp đối chứng, chẳng hạn một dòng bảng bị gộp cột bị đọc thành "100% nam" (nguồn: chú thích trong `agents/verifier.py`). Hai trường hợp này là cơ sở của chốt chặn `llm_stance_decisive: false` (mục 3.5).

## 3.4 Mười bất biến và lỗi mà mỗi bất biến ngăn

Mười bất biến được ban hành ngày 25/09/2026 (quyết định D-2026-09-25-01) và thi hành bằng các test trong `tests/test_architecture_invariants.py`. Tài liệu `ARCHITECTURE_INVARIANTS.md` ghi "14 test"; file test hiện có 15 hàm `test_` (mục 3.12). Bảng dưới đây gắn mỗi bất biến với lỗi nó chặn và với thành phần của bài toán ở mục 3.1.

| # | Bất biến | Lỗi nó ngăn | Ràng buộc liên quan |
|---|---|---|---|
| 1 | Kiểm chứng tuyên bố, không phán xét doanh nghiệp | Biến một công cụ soát tuyên bố thành bảng xếp hạng đạo đức hay kết luận pháp lý cho cả công ty; không tồn tại trường kết luận cấp doanh nghiệp (test quét mã nguồn) | Phạm vi đầu ra |
| 2 | Tuyên bố nguyên tử, giữ nguyên gốc (`doc_id`, `chunk_id`, trang, nguyên văn) | Kết luận không truy ngược được về câu gốc; chuẩn hoá làm mất dấu | R3 |
| 3 | Truy xuất tìm ứng viên, không quyết sự thật | Coi độ giống (TF-IDF, embedding) là bằng chứng ủng hộ; tương đồng cao nhưng ngược nghĩa | D_S |
| 4 | Chỉ so cái thật sự so được (chỉ số, loại giá trị, đơn vị, kỳ, năm gốc, ranh giới, Scope, công nghệ) | Mâu thuẫn giả từ so hai đại lượng khác chiều (5/8 mâu thuẫn sai ngày 22/09); lệch một chiều thì cấm kết luận mâu thuẫn | D_C |
| 5 | Số học là của code; mô hình không ghi đè bộ so sánh | Mô hình tự tính sai phần trăm, đổi đơn vị, nhầm điểm phần trăm với phần trăm tương đối; kết luận không chỉ ra được phép tính | D_S, D_C |
| 6 | Mục tiêu khác thành tích; thiếu dữ liệu khác thất bại | Coi "sẽ giảm 30%" là bằng chứng của "đã giảm 30%"; coi "không tìm thấy" là "bằng chứng nói ngược"; gộp `UNSUPPORTED` với `CONTRADICTED` trong điểm rủi ro | D_S, D_C |
| 7 | Pháp lý phải kiểm hiệu lực áp dụng, không chỉ liên quan chủ đề | Áp một văn bản hết hiệu lực, sai ngành hoặc sai loại tuyên bố; ví dụ NĐ 83/2026 chỉ sửa thủ tục chất ô-dôn/HFC nhưng trước 06/10 từng bị gắn nhãn `emissions` và bị trích kèm 55 tuyên bố phát thải | D_C |
| 8 | Từ chối kết luận là kết quả hợp lệ | Ép đường chạy luôn ra nhãn; bỏ chỗ nhường người | R2 |
| 9 | Verdict, risk, priority là ba đại lượng khác nhau | Dùng "72/100" thay cho đúng/sai; suy ngược kết luận từ vị trí hàng đợi; tối ưu hàng đợi đến mức đổi nghĩa kết luận | Tách đầu ra |
| 10 | Tái lập được và người kiểm tra được (manifest, `not_computed`, trích dẫn bắt buộc) | Kết quả không lặp lại; báo `0` cho tín hiệu chưa tính (đã sửa ở thành phần "bất thường": ghi `not_computed`, mẫu số hạ từ 100 xuống 90) | R3 |

Ngoài mười bất biến, tài liệu liệt kê những điều "từ nay không được làm", mỗi điều từng là một lỗi đã đo: thêm mô hình rồi cho ghi đè bộ so sánh tất định; dùng điểm tương đồng làm độ tin cậy; thêm GraphRAG, đa tác tử hay lượng tử chỉ để trông "AI hơn". Mục cuối được thi hành bằng test quét mã nguồn.

## 3.5 Kiến trúc mười bước

Một lượt phân tích đi qua mười bước do bộ điều phối `agents/orchestrator.py` gọi theo thứ tự. Hệ thống là một bộ điều phối với các mô-đun chuyên biệt, không phải hệ đa tác tử tự trị.

| # | Bước | Việc làm | Đầu ra |
|---|---|---|---|
| 1 | `validate_inputs` | Kiểm danh sách tài liệu, tạo `run_id`, ghi `manifest.json` ngay đầu | `RunManifest` |
| 2 | `parse_and_ocr_documents` | PyMuPDF đọc chữ theo khối; trang dưới 40 ký tự thì Tesseract OCR tại máy; pdfplumber giữ bảng thành một khối `TABLE`; cắt đoạn tối đa 3 câu, khoảng 600 ký tự; lập hồ sơ độ phủ của kho tài liệu | `EvidenceChunk[]`, `CorpusProfile` |
| 3 | `extract_green_claims` | Trích bằng luật: khớp từ điển `configs/taxonomy.yaml`, loại tiêu đề, mục lục, dòng bảng, câu cụt (mỗi câu bị loại có ghi lý do), gán thuộc tính bằng regex | `Claim[]` |
| 4 | `build_hybrid_retrieval_index` | Dựng bộ truy xuất, bộ kiểm chứng, bộ pháp lý, bộ chấm điểm | — |
| 5 | `retrieve_evidence_per_claim` | Điểm = 0,55 × BM25 + 0,45 × n-gram ký tự 3–5; RRF chỉ đổi thứ tự; lấy 30 ứng viên, giữ 5, luôn giữ 3 tốt nhất kèm cờ dưới ngưỡng; gắn cờ dấu hiệu tiêm lệnh | `RetrievedEvidence[]` |
| 6 | `verify_claim_evidence_pairs` | Chỉ khi bật mô hình: hỏi trước một lượt các cặp mà luật không quyết được | sự kiện `llm_stance_prefetch` |
| 7 | `check_applicable_law` | Kiểm chứng, pháp lý, chấm rủi ro cho từng tuyên bố | `VerificationResult`, kết quả pháp lý, `RiskAssessment` |
| 8 | `score_greenwashing_risk` | Cộng lại bảng số liệu, đối chiếu chéo tài liệu, nhận diện chủ thể, xếp hàng đợi | `priorities`, `figure_checks` |
| 9 | `apply_quality_gates` | Tám cổng G0–G7 | `release_status` |
| 10 | `write_evidence_pack` | Ghi `result.json`, `evidence_pack.md`, ba tầng dữ liệu `contract/{raw,clean,extract}.jsonl` | gói bằng chứng |

Ghi chú về tên bước: trên thanh tiến độ, các bước 6, 7, 8 mang tên không hoàn toàn khớp việc làm (bản đồ hệ thống 10/10, mục 7, lỗi 9). Bảng trên mô tả việc làm thực tế. Khi bật org pack, bước 7 thêm một thao tác: mỗi kết luận của một tuyên bố được đưa cho bộ áp quy tắc nội bộ (`orchestrator.py`, `_org_record`), kết quả đi vào `org_findings`.

Hình tham khảo: sơ đồ đường ống có sẵn tại `../../07-presentation/diagrams/pipeline_16x9_vi.png`.

**Hình 3.1.** Kiến trúc mười bước. Dòng chảy từ trái sang phải: tài liệu (vai trò, loại nguồn) → đọc và OCR tại máy → đoạn bằng chứng và tuyên bố có thuộc tính → truy xuất lai → bộ kiểm chứng (số học, cụm từ, xu hướng, độ giống) cùng bộ pháp lý và bộ chấm rủi ro → hàng đợi và tám cổng → gói bằng chứng. Nhánh mô hình ngôn ngữ chỉ nối vào bộ kiểm chứng ở cặp khó và có chốt chặn trước khi ra kết luận. Nhánh org pack chỉ đọc kết luận và ghi thêm phát hiện, không có mũi tên ngược.

### 3.5.1 Bộ kiểm chứng: số học, cụm từ, mô hình

Bộ kiểm chứng (`agents/verifier.py`) nhận một tuyên bố và các đoạn bằng chứng, rồi duyệt theo thứ tự thẩm quyền giảm dần.

1. **Số học.** Hai giá trị chỉ được so khi cùng chỉ số, loại giá trị, đơn vị, kỳ, ranh giới và Scope (bất biến 4). Dung sai bằng nửa chữ số cuối đã công bố, trần 10%; độ lệch tương đối từ 0,35 trở lên thì bác bỏ, ở khoảng giữa thì khớp một phần. Ngưỡng 0,35 trong `configs/default.yaml` được ghi là giả thuyết, chờ quét trên bộ nhãn. Ví dụ ở bài báo 15/10: cộng lại bảng phát thải 22.540.603 + 933.876 = 23.474.479 so với con số công bố 23.474.480 được coi là khớp (làm tròn).
2. **Cụm từ.** Từ điển cụm xác nhận và phủ định song ngữ; phủ định đơn lẻ không được dùng. Một cụm xác nhận chỉ có giá trị khi câu chứa nó cũng nêu đúng chỉ số của tuyên bố và mọi kỳ, Scope mà tuyên bố nêu, và có ít nhất hai thuộc tính khớp (`support_min_attributes = 2`).
3. **Xu hướng.** Chiều ngược ("giảm" so với "tăng") không có số để neo chỉ hạ xuống `PARTIALLY_SUPPORTED`: tiếng Việt dùng cả hai từ trong gần mọi đoạn nói về một chỉ số.
4. **Độ giống.** Không bao giờ tự quyết (bất biến 3); chỉ để xếp hạng và đặt ngưỡng truy xuất (`partial_support_score = 0,22`, `strong_support_score = 0,46`).
5. **Mô hình.** Chỉ chạy trên cặp mà các bước trên không quyết được và chỉ khi được bật (mục 3.5.3).

**Quy tắc kết luận** (đọc trực tiếp từ `_status` trong `verifier.py`):

| Nhãn | Điều kiện |
|---|---|
| `CONTRADICTED` | Có đoạn bằng chứng với quan hệ mâu thuẫn do số học, cụm từ hoặc luật quyết. Mâu thuẫn do mô hình chỉ được tính khi `llm_stance_decisive = true`, mặc định `false` |
| `PARTIALLY_SUPPORTED` | Mô hình nghi mâu thuẫn nhưng không có phép tính xác nhận; hoặc xu hướng ngược không có số; hoặc có xác nhận định tính từ nguồn khác nhưng thiếu số liệu và thuộc tính; hoặc chỉ tài liệu của chính nguồn tuyên bố khớp; hoặc có bằng chứng cùng chủ đề nhưng chưa xác minh đủ |
| `SUPPORTED` | Có đoạn từ **tài liệu khác** tài liệu chứa tuyên bố, điểm ≥ 0,22, và hoặc khớp số, hoặc có cụm xác nhận cùng chỉ số, kỳ, phạm vi với ≥ 2 thuộc tính |
| `UNSUPPORTED` | Có tài liệu liên quan được truy xuất nhưng không xác nhận tuyên bố, *và* kho tài liệu đủ để suy ra vắng bằng chứng (`corpus_completeness`) |
| `INSUFFICIENT_EVIDENCE` | Các trường hợp còn lại: bằng chứng quá yếu, tuyên bố mơ hồ mà không có tài liệu liên quan, kho chưa đủ để kết luận vắng |

Hai quy tắc phụ ngăn lỗi đã gặp. Thứ nhất, tuyên bố tự khớp với chính trang tóm tắt của cùng báo cáo chỉ là nhất quán nội bộ chứ không phải bằng chứng: ba trên ba kết luận `SUPPORTED` đầu tiên ở Hòa Phát ngày 22/09 là loại này, nên `SUPPORTED` đòi tài liệu khác. Thứ hai, một tuyên bố mơ hồ hoặc cam kết tương lai không số liệu không được nâng lên trên `UNSUPPORTED` chỉ vì độ giống.

### 3.5.2 Biểu diễn trung gian số liệu (`irlib`)

Mô-đun `verification/irlib.py` định nghĩa biểu diễn trung gian (IR) của một con số môi trường: chỉ số (14 mã, như `ghg_emissions`, `water_use`), loại giá trị (`absolute`, `intensity`, `share`, `change`, `count`), trạng thái (`actual`, `target`), kỳ, phạm vi (`s1`, `s2`, `s3`, `s1+s2`, `s1+s2+s3`), ranh giới (`group`, `parent`, `facility`, `unspecified`) và đơn vị quy về một đơn vị cơ sở. Mô hình có thể điền IR, còn mọi phép kiểm số, đơn vị, kỳ, phạm vi, ranh giới đều do mã trong `irlib` làm. Quy tắc cốt lõi: một chiều khác biệt thì nhãn là "không so được" (N), không bao giờ là mâu thuẫn; mục tiêu không chứng minh kết quả; hai giá trị khớp trong độ chính xác mà mỗi bên công bố. Thư viện chỉ dùng stdlib để chạy được cả trên Kaggle lẫn trong sản phẩm. Đây là cài đặt của bất biến 4–6 ở dạng tách rời.

### 3.5.3 Mô hình ngôn ngữ: chỉ cho cặp khó, có chốt chặn

Mô hình ngôn ngữ (`verification/llm_judge.py`) chỉ được hỏi khi `QUANTUM_LLM_STANCE=on_ambiguous` và có nhà cung cấp được cấu hình; mặc định là `off` (`configs/default.yaml`). Kể cả khi bật, quan hệ do mô hình đưa ra chỉ đưa lên `PARTIALLY_SUPPORTED` kèm cờ chuyển người, không bao giờ thành `SUPPORTED` hay `CONTRADICTED` khi `llm_stance_decisive` còn `false`. Một test dùng mô hình giả lập (`test_llm_stance_batch.py`) kiểm mô hình không tự quyết và bộ nhớ đệm hoạt động; một test bất biến kiểm thứ tự thẩm quyền trong `_stance`.

### 3.5.4 Đường IR "dual": có mã, chưa nối vào sản phẩm

Mô-đun `verification/ir_reader.py` mô tả đường đọc thứ hai (mô hình điền IR rồi `irlib.decide` cho nhãn), sau cờ `QUANTUM_VERIFY=dual`, với chính sách hợp hai đường `union_noloneS`: một nhãn quyết được chấp nhận khi cả hai đường cho cùng nhãn và không xung đột, riêng `SUPPORTED` chỉ do đường luật cho thì bị bỏ. Đường này được thiết kế chỉ là công cụ trợ giúp người soát, không đổi trạng thái kết luận. **Tại ngày 04/11/2026, không module nào trong `src/` gọi `ir_reader` và biến `QUANTUM_VERIFY` không được đọc ở đâu** (kiểm bằng `grep` ngày 05/11/2026; `R2_he_thong_va_thuc_nghiem.md` mục 3.10 ghi cùng kết quả). Vì vậy cờ này không có tác dụng với sản phẩm hiện tại; nó thuộc phần thực nghiệm (AG-2, chương 4–5), không thuộc sản phẩm mặc định và cũng chưa phải tính năng nằm sau cờ.

## 3.6 Thực thể pháp lý: policy-as-code

Lớp pháp lý áp nguyên tắc "luật do người viết, mô hình không tự đọc luật rồi sinh quy tắc lúc chạy". Một quy tắc đi vào sản phẩm qua chuỗi: nháp (có thể do mô hình soạn) → người có thẩm quyền duyệt → test đơn vị → tăng phiên bản (chú thích đầu `configs/legal/rule_pack_vn_green_v0.1.yaml`).

Cấu trúc của một quy tắc gồm: mã quy tắc, văn bản nguồn và điều khoản (`source_clauses`), loại tuyên bố áp dụng, vấn đề pháp lý, ngày hiệu lực, mức tự động hoá (`full`, `partial`, `none` — nói thật mức mã quyết được), người duyệt, và danh sách điều kiện. Mỗi điều kiện có kiểu kiểm (`terms_present`, `numeric_threshold`, `manual`…) và loại bằng chứng cần có. Điều kiện về hiệu lực của văn bản xác nhận để `manual` có chủ ý: tính hợp lệ của cơ quan cấp và ngày cấp là phán đoán pháp lý, không phải khớp từ khoá.

Việc xét áp dụng theo thứ tự ngày hiệu lực → ngành → chủ thể → loại tuyên bố → điều kiện, và quy tắc bị loại luôn ghi lý do (bất biến 7). Registry pháp lý hiện có 12 văn bản, mỗi văn bản có ba ngày (ký, hiệu lực, sửa đổi bởi), sửa đổi chỉ gắn với vấn đề nó sửa (bài báo 15/10, mục 4.4).

**Trạng thái trung thực.** Bộ quy tắc hiện chỉ có một quy tắc (`VN_GREEN_TAXONOMY_001`) và là bản nháp: `source_clauses` để trống, `reviewed_by` để trống, vì bản Quyết định 21/2025/QĐ-TTg là bản scan chưa trích được chữ để gắn điều khoản. Quy tắc nhắm vào loại tuyên bố (`green_project`, `green_taxonomy_eligibility`) mà bộ phân loại tuyên bố không sinh ra, nên trong bản đồ hệ thống 10/10 mọi tuyên bố đều ra kết quả pháp lý `INSUFFICIENT_EVIDENCE` với `rules_applied: []`. Do đó lớp pháp lý hiện đóng vai trò hạ tầng và registry có kiểm ngày hiệu lực, chưa là nguồn phát hiện. Các quy tắc thật đang chờ người có thẩm quyền duyệt (bài báo 15/10, mục 4.4).

## 3.7 Chấm rủi ro và hàng đợi

Ba đại lượng được giữ tách nhau (bất biến 9): kết luận (quan hệ giữa tuyên bố và bằng chứng), rủi ro (mức cần chú ý theo thang điểm) và ưu tiên (nên mở tuyên bố nào trước).

### 3.7.1 Rubric rủi ro 9 thành phần

Rubric trong `configs/scoring_v1.yaml` (nhãn `risk-rubric-v2`) có chín thành phần, trần cộng lại bằng 100. Điểm cao nghĩa là rủi ro tẩy xanh cao.

| Thành phần | Trần | Nhóm |
|---|---:|---|
| `specificity` (tính cụ thể của chỉ số) | 12 | thuộc tính bắt buộc |
| `quantitative_evidence` (số liệu định lượng) | 12 | thuộc tính bắt buộc |
| `baseline` (năm gốc) | 8 | thuộc tính bắt buộc |
| `period` (kỳ báo cáo) | 8 | thuộc tính bắt buộc |
| `scope_boundary` (phạm vi, ranh giới) | 8 | thuộc tính bắt buộc |
| `evidence_support` (bằng chứng hỗ trợ) | 18 | bằng chứng |
| `independent_assurance` (bảo đảm độc lập) | 8 | bằng chứng |
| `contradiction` (mâu thuẫn) | 18 | phạt |
| `vague_or_exaggerated_language` (ngôn ngữ mơ hồ, phóng đại) | 8 | phạt |

Các dải mức: Thấp 0–24, Trung bình 25–49, Cao 50–74, Nghiêm trọng 75–100. Việc tách năm gốc và kỳ thành hai thành phần và thêm `scope_boundary` giúp giao diện chỉ ra chính xác thuộc tính nào còn thiếu. Chú thích trong YAML ghi một bài học: lần tách đầu tiên đã đưa tổng lên 120 và đẩy 32 trong 41 tuyên bố vào diện soát trên một kho mà theo người soát chỉ 3 tuyên bố thuộc diện đó; trọng số hiện tại khôi phục thang 100. Điểm của `contradiction` chỉ cao khi có mâu thuẫn thật; nhãn thiếu bằng chứng được cho điểm thấp hơn (hàm `max_without_contradiction`, bất biến 6). Tuyên bố bị `PARTIALLY_SUPPORTED` do thiếu thuộc tính bị chặn trên mức Trung bình (bản đồ R2, mục 2.13).

Bài báo 15/10 (mục 4.3) vẫn mô tả điểm rủi ro theo bảy tiêu chí; mã dùng chín thành phần, nên luận văn lấy chín thành phần theo mã.

### 3.7.2 Hàng đợi ưu tiên

Hàng đợi (`configs/priority_v1.yaml`, nhãn `priority-v1.1`) trả lời câu hỏi của kiểm toán viên: trong báo cáo có số lượng lớn tuyên bố, mở tuyên bố nào trước. Ngày 23/09, lượt chạy Hòa Phát cho 153 `PARTIALLY_SUPPORTED` và 154 `MEDIUM`: đúng nhưng vô dụng làm danh sách việc. Điểm ưu tiên là tổng có trọng số của bốn yếu tố đã chuẩn hoá về 0–1:

| Yếu tố | Trọng số | Ý nghĩa |
|---|---:|---|
| Trọng yếu (materiality) | 40 | Nếu tuyên bố sai thì quan trọng đến đâu: họ chỉ số, độ lớn so với các con số cùng đơn vị trong lượt chạy, vị trí trang |
| Nghĩa vụ (obligation) | 25 | Có nghĩa vụ công bố nào gắn vào tuyên bố không |
| Khoảng trống bằng chứng | 25 | Tuyên bố còn cách xa việc kiểm được đến đâu |
| Bất thường | 10 | Lệch so với các kỳ trước và so với ngành; **chưa tính**, ghi `not_computed` |

Tất cả là lựa chọn có thể tranh luận, không có tham số học: một hàng đợi mà kiểm toán viên không cãi được thì họ sẽ không tin. Hệ số giảm cho văn xuôi quảng bá không có số (0,70), câu không nêu chủ thể và không có số (0,75, thêm ngày 05/10 sau khi hàng đợi Hòa Phát bị dẫn đầu bởi các câu giải thích về luyện thép), và chữ dính cột (0,50). Hàng đợi chỉ đổi thứ tự, không đổi kết luận và không bị đọc ngược thành kết luận. Cắt hàng đợi: luôn đưa các mục có ưu tiên từ 55, tối đa 25 mục, tối thiểu 5 mục; phần còn lại được báo là "cố ý chưa xét" theo kiểu ghi chú phạm vi của chuẩn mực kiểm toán.

### 3.7.3 Tám cổng chất lượng

Bước 9 chạy tám cổng: G0 nguồn gốc, G1 trung thực trích xuất, G2 truy xuất đủ, G3 số học bằng mã, G4 toàn vẹn trích dẫn, G5 rủi ro cao chờ người, G6 tái lập, G7 pháp lý (`agents/reviewer.py`). Trạng thái lượt chạy là `BLOCKED`, `PENDING_HUMAN_REVIEW` hoặc `RELEASABLE`. Hạn chế đã biết: cổng G3 hiện luôn đạt (`reviewer.py`, theo bản đồ hệ thống mục 7, lỗi 6), nên G3 chưa phải một kiểm tra thực.

## 3.8 Bộ nhớ chuẩn và lớp quy tắc nội bộ (org pack)

### 3.8.1 Ý tưởng

GreenScan được dựng sẵn với một bộ nhớ chuẩn. Người dùng (ngân hàng, công ty kiểm toán, doanh nghiệp niêm yết) không phải dạy lại hệ thống; họ chỉ thêm quy tắc, quy chế và tài liệu nội bộ của mình dưới dạng một *org pack*. Hệ thống áp các quy tắc đó cho từng tuyên bố và ghi thêm phát hiện bên cạnh kết quả, nhưng **không bao giờ đổi kết luận kiểm chứng** (`docs/03-architecture/ORG_PACK.md`).

### 3.8.2 Các tầng nhớ và thứ bậc

| Tầng | Nội dung | Người viết | Vị trí |
|---|---|---|---|
| Bộ nhớ lõi | Taxonomy tuyên bố, kho văn bản pháp lý và rule pack, mười bất biến | Đội GreenScan, có duyệt và test | `configs/taxonomy.yaml`, `configs/legal/`, `ARCHITECTURE_INVARIANTS.md` |
| Bộ nhớ tổ chức | Quy tắc nội bộ và tài liệu dẫn chiếu của một tổ chức | Tổ chức, có người duyệt (`approved_by`) | `configs/org_packs/<org_id>/` |
| Bộ nhớ phiên | Tài liệu tải lên, tuyên bố trích được, bằng chứng, kết quả một lượt | Đường ống | `.quantum/runs/<run_id>/` |
| Bộ nhớ phản hồi | Quyết định người soát: xác nhận, sửa, yêu cầu thêm tài liệu | Người soát | kho review (`ReviewStore`) |

Tầng trên không ghi đè tầng dưới. Thứ bậc ưu tiên: (1) luật và mười bất biến, không gì vượt được (trường `precedence` của pack bắt buộc là `below_law`); (2) kiểm chứng (kết luận, rủi ro, trần mức rủi ro, hàng đợi, trạng thái phát hành), org pack không đọc để sửa và không ghi; (3) quy tắc nội bộ, chỉ thêm phát hiện kèm `on_fail` ∈ {`flag_for_review`, `raise_priority`}. Ở phiên bản hiện tại `on_fail` chỉ được ghi lại, chưa tác động hàng đợi. Quy tắc nội bộ lỏng hơn luật thì luật vẫn đứng và phát hiện pháp lý không bị che.

### 3.8.3 Cấu trúc một pack và kiểu kiểm

Một pack (`org-pack-v0`) là một thư mục gồm `pack.yaml` và tài liệu nội bộ (ví dụ `internal_policy.md`, đánh số §1, §2.1 để quy tắc dẫn chiếu). `pack.yaml` có `org_id`, `org_type`, `pack_version`, `precedence`, `approved_by`, `approved_at`, danh sách `documents`, `glossary` và `rules`. Một quy tắc có mã, `source_clauses` trỏ về tài liệu nội bộ, `claim_types`, `applies_to_sectors`, `effective_from`/`effective_to`, `severity`, `on_fail`, `machine_executable`, điều kiện `when` (quy tắc chỉ áp khi mọi điều kiện `when` thoả) và danh sách `conditions` (AND). Schema đầy đủ ở `benchmark/gs_eval_v2/LABELING_GUIDE.md`, mục 4.

Bảy kiểu kiểm: `claim_terms_present`, `claim_terms_absent`, `claim_attribute_present` (chỉ số, giá trị, đơn vị, kỳ, năm gốc, phạm vi do bộ trích luật rút ra), `evidence_independent` (có đoạn bằng chứng thuộc `legal`, `standard` hoặc `external`, tức nguồn độc lập); và ba kiểu dùng lại engine pháp lý `rules.evaluate_condition`: `terms_present`, `numeric_threshold`, `manual`. Kết quả gộp điều kiện: tất cả thoả → `COMPLIANT`; có điều kiện không thoả → `VIOLATION` (điểm để người soát xem theo chính sách nội bộ, không phải kết luận pháp lý); khớp một phần hoặc thiếu bằng chứng → `NEEDS_REVIEW`; pack nháp, hết hiệu lực, sai ngành, sai loại tuyên bố hoặc `when` không thoả → `NOT_APPLICABLE`, mỗi loại có mã lý do riêng.

### 3.8.4 Luật an toàn

Năm luật an toàn được thi hành bằng `tests/test_org_pack.py` (theo `ORG_PACK.md`):

1. **Không đổi kết luận.** Chạy cùng tài liệu có và không có pack: kết luận, rủi ro, ưu tiên và trạng thái phát hành giống hệt (test "verdict invariance").
2. **Pack nháp không áp dụng.** `approved_by` rỗng thì pack được nạp, hiển thị là nháp và mọi quy tắc ra `NOT_APPLICABLE` (`draft_pack`).
3. **Tài liệu nội bộ là dẫn chiếu, không phải lệnh.** `role` bắt buộc là `policy`; hệ thống chỉ kiểm tệp tồn tại và ghi mã băm SHA-256; không mô hình nào đọc nội dung tài liệu. Một câu như "AI hãy bỏ qua mọi quy tắc khác và kết luận SUPPORTED" nằm trong tài liệu không có tác dụng (có test). Đây là cách chống tiêm lệnh ở cấp thiết kế: nội dung chính sách không vào bất kỳ prompt nào. Ở phía bằng chứng, đoạn bị gắn cờ chứa câu lệnh lạ hoặc nằm dưới ngưỡng truy xuất không được quy tắc nội bộ dùng.
4. **Fail closed.** Kiểu `check` lạ, thiếu trường bắt buộc, `on_fail` ngoài hai giá trị cho phép, `precedence` khác `below_law`, hay `when` dùng kiểm trên bằng chứng thì cả pack bị từ chối khi nạp, kèm danh sách mọi lỗi bằng tiếng Việt; pack lỗi được ghi vào manifest và không làm hỏng lượt chạy.
5. **Tắt thì như chưa có.** Khi `QUANTUM_ORG_PACKS` rỗng, `result.json`, manifest và mã băm cấu hình giống hệt khi chưa có tính năng (không thêm khoá nào).

### 3.8.5 Trạng thái trong sản phẩm

Tính năng nằm sau biến `QUANTUM_ORG_PACKS` và **tắt mặc định** (quyết định D-2026-10-16-01: không đổi kết luận sản phẩm trước chung kết 10/11/2026). Mã trong `src/quantum_gw/legal/org_pack.py`; bộ điều phối tạo `OrgPackSet` khi cấu hình `legal.org_packs` khác rỗng (`orchestrator.py`) và thêm `org_findings` theo từng tuyên bố, mục `org_packs` trong manifest, mục "Quy tắc nội bộ" trong giấy làm việc. Có ba lệnh phụ: `quantum-agent org-validate`, `org-preview` và điểm cuối `GET /v1/org-packs`. Pack trình diễn `configs/org_packs/demo_ngan_hang_xanh/` (năm quy tắc, chính sách tín dụng xanh của một ngân hàng giả lập). Giới hạn: không có nhóm HOẶC (mọi điều kiện là AND); từ khoá là luật chuỗi con, không phải hiểu nghĩa; `claim_attribute_present` phụ thuộc bộ trích luật; giao diện web chưa hiển thị `org_findings` (xem ở giấy làm việc, `evidence_pack.md` hoặc `result.json`).

Quy ước về kiểm định: bộ ca kiểm D-RULES của GS-Eval v2 (mục 4 của `LABELING_GUIDE.md`) kiểm lớp này; phương pháp ở chương 4, kết quả ở chương 5.

## 3.9 GreenScan Studio: bốn loại gợi ý sửa, không bịa số

Phân tích đã nói tuyên bố thiếu gì (kỳ, năm gốc, phạm vi, số liệu, bằng chứng) và từ nào nói quá. Studio (`src/quantum_gw/studio/suggest.py`) biến mỗi phát hiện thành một chỉnh sửa cụ thể mà người soát có thể chấp nhận, từ chối hoặc sửa tiếp. Gợi ý được tạo từ mẫu theo luật, có bốn loại:

| Loại (`kind`) | Việc làm |
|---|---|
| `add_scope` | Nối phần kỳ, năm gốc hoặc ranh giới còn thiếu như một chỗ trống để điền |
| `placeholder` | Đánh dấu cụm mơ hồ, hoặc tuyên bố không có số, bằng "[bổ sung: …]" |
| `evidence_ref` | Dẫn bằng chứng mà lượt chạy thực sự tìm được, hoặc một chỗ trống đòi bằng chứng |
| `soften` | Thay lời tuyệt đối hoặc dựa trên bù trừ bằng cách nói có điều kiện |

Điều gợi ý không bao giờ được làm là đưa một con số mà doanh nghiệp chưa công bố. Mọi phần thay thế đi qua `assert_no_new_numbers`, chỉ cho phép các số đã có trong câu gốc và số trang của bằng chứng được dẫn; gợi ý không qua kiểm này thì bị bỏ, không hiển thị. Mỗi gợi ý mang `basis` (căn cứ: rubric thuộc tính của GreenScan, GHG Protocol, Chỉ thị (EU) 2024/825 về tuyên bố môi trường chung chung; hai căn cứ sau kèm nhãn "chưa đối chiếu điều khoản" hoặc "không ràng buộc tại Việt Nam"). Studio xuất DOCX có tracked changes. Việc leo thang lên mô hình ngôn ngữ nằm ở `studio/escalation.py`: mặc định không gọi, vì ngưỡng `tau` chưa được hiệu chỉnh nên không ca nào bị leo thang (bản đồ R2, mục 3.10).

## 3.10 Giao diện, lưu trữ và truy vết

Cổng vào gồm: khởi động một chạm (`GreenScan.bat` hoặc `start.sh`, chạy `quantum-agent app` ở 127.0.0.1:8000); CLI (`analyze`, `demo`, `evaluate`, `serve`, `app`, `org-validate`, `org-preview`); API tác vụ nền (`POST /v1/jobs/analyze/files`). Giao diện có ba bước: Tải tài liệu, Soát theo hàng đợi, Giấy làm việc. Ảnh trang PDF được dựng tại máy bằng PyMuPDF kèm tô sáng. Dữ liệu lưu dưới `.quantum/`: `runs/<id>/` (manifest, `audit.jsonl` chỉ ghi thêm, `result.json`, `evidence_pack.md`, `contract/`), `documents/` (tệp gốc theo SHA-256), `reviews/decisions.jsonl` (chỉ ghi thêm). Manifest ghi phiên bản đường ống, `config_hash` (băm cấu hình sau khi áp biến môi trường, không băm nội dung các tệp YAML), mã băm từng tài liệu đầu vào, phiên bản bộ quy tắc và `prompt_version`.

## 3.11 Chế độ ngoại tuyến và dữ liệu rời máy

Biến `QUANTUM_PROFILE` chọn chế độ; `.env.example` đặt `offline`.

| Chế độ | Dữ liệu rời máy |
|---|---|
| `offline` (mặc định) | Không gì cả. Đã kiểm ngày 09/10 bằng cách chặn mọi kết nối khi phân tích 264 trang: 0 lần gọi ra ngoài |
| `cloud` | Cặp khó gửi sang FPT AI Marketplace, định tuyến cố định GLM-5.2 |
| `gpu` | vLLM tại máy, nhưng chuỗi dự phòng `local,fpt` gửi sang FPT khi mô hình tại máy lỗi, mâu thuẫn với lời hứa "không rời máy" |

Trong `src/`, chỉ ba nhóm mã gọi HTTP ra ngoài: nhà cung cấp mô hình, embedding (`retrieval/embeddings.py`) và reranker (`retrieval/rerank.py`); OCR chạy tại máy. Khi mô hình đọc cặp khó chạy, nó nhận lời dặn cố định khoảng 600 ký tự cùng **nguyên văn** câu tuyên bố và đoạn bằng chứng (không cắt độ dài, một bảng đi nguyên khối). Embedding và reranker mặc định tắt (`embedding: lite`, `reranker: none`); khi bật, embedding gửi mọi đoạn của mọi tài liệu (cắt ở 6.000 ký tự cho FPT), reranker gửi câu tuyên bố và tới 30 đoạn ứng viên (cắt ở 4.000 ký tự mỗi đoạn). Dữ liệu được phân ba loại: A công khai (dùng mọi chế độ), B nội bộ (`offline`, `gpu` hoặc FPT Dedicated có hợp đồng), C giấy làm việc kiểm toán (chỉ `offline` hoặc `gpu` tại đơn vị; D-2026-10-06-06). Ngoài ra thí nghiệm che số và tên (L1) cho thấy việc che không loại bỏ nguy cơ nhận diện lại doanh nghiệp từ tổ hợp ngành và thuật ngữ đặc thù.

Lưu tại máy: bộ nhớ đệm câu trả lời mô hình (khoá là băm của phiên bản prompt, tuyến, câu và đoạn; lưu quan hệ và lý do, mà lý do có thể diễn lại nội dung tài liệu); vector embedding. Hiện **chưa có sổ ghi từng lần gửi đi**, một yêu cầu của tài liệu thiết kế dữ liệu mà chưa được cài.

Lưu ý về trạng thái vận hành tại ngày 04/11: khoá FPT trả lỗi 401 từ 31/10, nên đường mô hình ngôn ngữ ở chế độ `cloud` hiện không chạy được; sản phẩm chạy ở chế độ ngoại tuyến (bản đồ R2, mục 3.10).

## 3.12 Cái gì trong sản phẩm mặc định, cái gì sau cờ, cái gì là thực nghiệm

| Thành phần | Trạng thái | Căn cứ |
|---|---|---|
| Đường ống 10 bước, `offline`, giấy làm việc tiếng Việt, quyết định soát chỉ-thêm, hàng đợi `priority-v1.1`, tám cổng | **Sản phẩm mặc định** (G3 luôn đạt, "bất thường" chưa tính) | `orchestrator.py`, `reviewer.py` |
| Trích luật, truy xuất `lite`, bộ kiểm chứng số học → cụm từ → xu hướng → tương đồng, năm nhãn, chốt `llm_stance_decisive: false` | **Sản phẩm mặc định** | `configs/default.yaml`, `verifier.py` |
| Rubric 9 thành phần, hàng đợi, Studio bốn loại gợi ý, rào "không số mới" | **Sản phẩm mặc định** | `scoring_v1.yaml`, `suggest.py` |
| Registry pháp lý 12 văn bản và rule pack | Sản phẩm mặc định, nhưng 0 quy tắc áp được (một quy tắc nháp) | `rule_pack_vn_green_v0.1.yaml` |
| Mô hình đọc cặp khó (`QUANTUM_LLM_STANCE=on_ambiguous`) | **Sau cờ, tắt mặc định**; hiện không chạy do khoá FPT lỗi 401 | `settings.py`, `default.yaml` |
| Embedding, reranker (`EMBEDDING_PROVIDER`, `RERANKER_PROVIDER`) | **Sau cờ, tắt mặc định**; có adapter, chưa đo | `default.yaml` |
| Org pack (`QUANTUM_ORG_PACKS`) | **Sau cờ, tắt mặc định** (D-2026-10-16-01); mã và test có | `org_pack.py`, `ORG_PACK.md` |
| `QUANTUM_VERIFY=dual`, `ir_reader.py` | **Thực nghiệm**: mã trong `src/` nhưng không nơi nào gọi; biến không được đọc | grep `src/` 05/11 |
| `irlib` (làm thư viện), AG-0 → AG-3, size ladder, che số, học trò T1 e5-base | **Thực nghiệm** (T1 đã huấn luyện, chưa nối) | R2 mục 3.10 |
| QUBO chọn bằng chứng, chế độ `cloud_masked`, sổ gửi đi, nguồn độc lập, quy tắc pháp lý có người duyệt | **Chỉ có trên giấy** | R2 mục 3.10, 2.14 |

Về phần lượng tử: không có dòng mã lượng tử nào trong GreenScan (grep "qubo" trong `*.py` ngày 04/11 cho 0 kết quả). Công thức QUBO chọn bằng chứng chỉ tồn tại ở dạng đề xuất trên giấy và luận văn không tuyên bố lợi thế lượng tử.

### Chỗ tài liệu và mã không khớp (đã đối chiếu mã)

| # | Tài liệu nói | Mã cho thấy | Luận văn dùng |
|---|---|---|---|
| 1 | `ARCHITECTURE_INVARIANTS.md` và bài báo: "14 test" cho mười bất biến; bản đồ hệ thống nói "15 bất biến" | `test_architecture_invariants.py` có 15 hàm `test_`; mười bất biến, không phải 15 | Mười bất biến, 15 test |
| 2 | Bài báo 15/10, mục 4.3: điểm rủi ro theo 7 tiêu chí | `scoring_v1.yaml`: 9 thành phần, tổng 100 | Chín thành phần |
| 3 | `scoring_v1.yaml` nhãn `risk-rubric-v2` | Bản đồ hệ thống: mặc định trong mã ghi `v1` | Ghi nhãn `risk-rubric-v2` theo YAML, ghi chú lệch |
| 4 | Biến `QUANTUM_VERIFY=dual` được mô tả như một đường phía sản phẩm | Không mã nào đọc biến hay gọi `ir_reader` | Thực nghiệm, chưa nối |
| 5 | Chế độ `gpu` hứa "không rời máy" | Có chuỗi dự phòng sang FPT | Nêu rõ là lỗ hổng riêng tư đã biết |
| 6 | Tám cổng G0–G7 kiểm chất lượng | G3 luôn đạt | Nêu là hạn chế |
| 7 | Bài báo 15/10: 17 bẫy trong `test_verdict_traps.py`; bản đồ 10/10: 47 bẫy | Số này tăng theo thời gian | Không dùng số cụ thể ở chương này; chương 4 và 5 lấy theo ngày đo |

## 3.13 Kiểm thử

Bản đồ hệ thống 10/10 ghi 359 kiểm thử `pytest`. Các nhóm chính: `test_verdict_traps.py` (bẫy kết luận, mỗi lỗi đã gặp thành một test), `test_audit_checklist.py` (ca checklist kiểm toán), `test_architecture_invariants.py` (bất biến, kể cả thứ tự số học → cụm từ → mô hình), `test_legal_*` (pháp lý), `test_review_priority.py` (hàng đợi), `test_llm_stance_batch.py` (mô hình giả lập không tự quyết), `test_product_api.py` (tác vụ, `/api`, giấy làm việc), `test_org_pack.py` (luật an toàn của org pack). `conftest.py` tắt mô hình và cách ly thư mục phiên, nhưng không tắt embedding hoặc reranker nếu `.env` bật chúng. "Definition of Done" của dự án đổi từ "xong tính năng" sang "giữ được bài học": mỗi thay đổi phải trả lời bốn câu: điều gì xảy ra khi thiếu bằng chứng, khi đầu vào không so được, thay đổi có thể làm tăng mâu thuẫn sai không, và có quyết định nào chuyển từ luật sang mô hình không. Số lượng test không phải bằng chứng về chất lượng; chất lượng được đo bằng các bộ đánh giá ở chương 4.

## 3.14 Tóm tắt chương

- Bài toán là kiểm chứng ở cấp tuyên bố: đầu vào là tập tài liệu có vai trò và loại nguồn; đầu ra là một trong năm nhãn kèm bằng chứng có nguồn gốc, điểm rủi ro phân rã chín thành phần, gợi ý sửa và phát hiện nội bộ. Mục tiêu là cực đại hoá độ phủ với giới hạn trên hai loại kết luận sai nguy hiểm (`SUPPORTED` sai, `CONTRADICTED` sai).
- Thiết kế tách "mô hình đọc, quy tắc quyết, người duyệt". Số học, cụm từ và xu hướng là mã tất định có thứ bậc thẩm quyền; độ giống và mô hình không tự quyết. Mười bất biến, mỗi bất biến có test, ngăn các lỗi đã đo (so khác chiều, nhầm mục tiêu với thành tích, nhầm thiếu dữ liệu với mâu thuẫn).
- Verdict, rủi ro (rubric chín thành phần, trần 100) và ưu tiên (`priority-v1.1`, bốn yếu tố 40/25/25/10, chỉ đổi thứ tự) là ba đại lượng tách rời; tám cổng và tình trạng "chờ người duyệt" bảo đảm người vẫn quyết định cuối.
- Org pack thêm lớp quy tắc nội bộ dưới luật và dưới kiểm chứng, với năm luật an toàn (không đổi kết luận, pack nháp không áp dụng, tài liệu nội bộ không phải lệnh, fail closed, tắt thì như chưa có); tính năng tắt mặc định. Studio tạo bốn loại gợi ý sửa từ mẫu và có rào "không số mới".
- Sản phẩm mặc định chạy ngoại tuyến, không gửi gì ra ngoài. Mô hình ngôn ngữ, embedding, reranker và org pack nằm sau cờ tắt mặc định; đường `dual` và `irlib` là thực nghiệm chưa nối; lớp pháp lý hiện không có quy tắc áp được; chưa có mã lượng tử nào.
