# Chương 4. Luồng phân tích 10 bước và kết quả từng bước

Chương này đi qua từng bước của `OrchestratorAgent.run`. Mỗi mục gồm bốn phần: **mục đích**, **thuật toán và tham số** (lấy từ mã nguồn và tệp cấu hình, có ghi vị trí `tệp:dòng` tính từ `src/quantum_gw/`), **kết quả Ca A**, **kết quả Ca B**. Các bảng kết quả được sinh tự động từ tệp của hai phiên `{{RUN_A}}` (Ca A) và `{{RUN_B}}` (Ca B).

## 4.1. Bước 1: Kiểm đầu vào (`validate_inputs`)

**Mục đích.** Bảo đảm có ít nhất một tài liệu, cấp mã phiên và ghi lại mọi thứ cần để tái lập lượt chạy.

**Thuật toán.**

1. Danh sách tài liệu rỗng thì dừng với lỗi `At least one document is required`.
2. Cấp `run_id` = 16 ký tự hex đầu của một UUID4; tạo thư mục `.quantum/runs/<run_id>/`; mở nhật ký `audit.jsonl` và ghi sự kiện `run_started` kèm kế hoạch 10 bước.
3. Tạo bộ kiểm chứng (`VerificationAgent`). Nếu cấu hình bật mô hình lập trường thì bộ này giữ một `llm_judge`; ở hồ sơ offline thì không có.
4. Nạp bộ quy tắc nội bộ của tổ chức (org pack) nếu biến `QUANTUM_ORG_PACKS` có giá trị; bộ nào không qua kiểm tra lược đồ được ghi vào manifest và **không** được áp dụng.
5. Ghi `manifest.json`: phiên bản pipeline, mã băm cấu hình (`settings.stable_hash()`), mã băm SHA-256 của từng tệp đầu vào (văn bản dán trực tiếp thì băm nội dung), kế hoạch, phiên bản kho văn bản, phiên bản bộ luật, phiên bản prompt (rỗng khi không mô hình nào được hỏi).

**Kết quả Ca A.** Manifest của phiên:

{{S1_MANIFEST_A}}

Trường `prompt_version` rỗng xác nhận không có mô hình ngôn ngữ nào tham gia ra kết luận. `deterministic_seed: 0` và `config_hash` cho phép kiểm rằng hai lượt chạy dùng đúng cùng cấu hình. Trên thực tế, phiên Ca B ngày 18/11 cho cùng số tuyên bố (186), cùng số liệu đọc từ bảng (55), cùng 15 phép kiểm bảng và cùng hàng soát (9/241) với phiên `224d4bdfd0394ea9` chạy ngày 17/11 và phiên kho demo `efcd9717caef4d7b`. Từ 17/11 đến nay, mã chỉ đổi phần giao diện và phông chữ của giấy làm việc.

**Nhật ký sự kiện của cả phiên** (mỗi bước ghi ít nhất một sự kiện vào `audit.jsonl`):

{{S1_EVENTS}}

## 4.2. Bước 2: Đọc tài liệu, OCR và tách đoạn (`parse_and_ocr_documents`)

**Mục đích.** Biến mọi tệp thành danh sách **đoạn** (`EvidenceChunk`) có nguồn gốc rõ: tệp, trang, khối; đồng thời phát hiện chữ ẩn, câu nhắn tới máy chấm và trang đọc kém.

**Thuật toán** (`agents/intake.py:25-47`, `parsers/documents.py:46-248`).

1. **Chọn đường đọc theo loại tệp.** `.pdf` đọc bằng PyMuPDF; `.docx` đọc `word/document.xml` (mỗi đoạn một khối, bảng thành dòng `a | b | c`); `.html` bỏ thẻ `script, style, nav, footer…`; `.txt .md .csv .yaml .json` đọc UTF-8. Đuôi khác bị từ chối.
2. **Mã định danh ổn định.** `doc_id` và `chunk_id` là 16 ký tự đầu của SHA-256 trên các thành phần nối bằng `||` (`utils/text.py:87-89`). Với PDF: `chunk_id = stable_id(doc_id, trang, khối, nội dung)`. Cùng tệp thì cùng mã ở mọi lần chạy.
3. **Trang PDF: phân vùng trang (`page-regions-v1`, `parsers/layout.py`, từ 17/11).** Trước khi diễn giải nội dung, mỗi trang được tách thành các vùng có kiểu. Trang có lớp chữ dùng khối và từ của chính tệp PDF; trang quét dùng toạ độ từng từ do Tesseract trả về. Chữ ẩn bị loại (bước 6 dưới đây). Hệ thống tìm **cột chữ** bằng khe dọc không dòng hẹp nào cắt qua, rồi đọc hết cột trái mới sang cột phải. **Bảng có kẻ ô** lấy bằng `find_tables` của PyMuPDF, qua bộ lọc hình dạng `table-shape-v1` (bỏ các "bảng" thực ra là khung bố cục). **Bảng không kẻ ô** là các dòng có nhãn bên trái và con số căn lề phải thẳng hàng. Mỗi bảng mang theo tên bảng, tiêu đề cột, đơn vị ("(tỷ VND)", "(Nghìn tấn)", "Đơn vị:") và kỳ. Kiểu dấu phân cách được quyết một lần cho cả bảng, nên "7,085" trong bảng có "7,085 / 6,982 / 103" là bảy nghìn không trăm tám mươi lăm. Ô bảng **không** đi vào bộ trích tuyên bố như câu văn; nó thành số liệu công bố ở bước 8 (mục 4.8.2). Tắt bằng `QUANTUM_LAYOUT_REGIONS=off`, khi đó trang được đọc như trước 17/11: khối chữ sắp theo toạ độ, bảng `pdfplumber` thành dòng `ô1 | ô2 | …`. Chi tiết ở Chương 12.
4. **Điều kiện OCR.** Một trang được OCR khi lớp chữ gốc có **dưới 40 ký tự** hoặc **từ 15% từ trở lên bị lỗi phông** (chữ ngoài bảng chữ tiếng Việt, ký hiệu phông TCVN3/VNI kiểu "chÝnh"). OCR dùng Tesseract `-l vie+eng --psm 6` trên ảnh trang 220 dpi, giới hạn 120 s mỗi trang. Từ bảng TSV của Tesseract, hệ thống tính: độ tin cậy trung bình (có trọng số độ dài từ), tỉ lệ từ có độ tin cậy dưới 80, và danh sách **"con số đáng ngờ"** (chuỗi có chữ số với độ tin cậy dưới 90). Mốc 80 và 90 được chọn theo hiệu chỉnh ghi trong `parsers/ocr.py:267-276`: số đọc với độ tin cậy dưới 90 chỉ đúng tối đa 48%, từ 90 trở lên đúng 83–91%. Trang cần OCR mà không OCR được thì gắn `unread = true`.
5. **Tách đoạn** (`documents.py:200-248`). Văn bản tách theo dòng trống thành đoạn văn; mỗi đoạn văn tách câu tại `. ! ? ;` hoặc xuống dòng; mảnh dưới 40 ký tự (tiêu đề, nhãn bảng) được dính vào câu sau. Câu được gom thành cửa sổ **tối đa 3 câu và tối đa 600 ký tự**; cửa sổ không bao giờ vượt qua dòng trống. Chuẩn hoá: NFKC, khoảng trắng cứng thành dấu cách, gộp khoảng trắng, nối dòng gãy khi dòng trước chưa hết câu và dòng sau bắt đầu bằng chữ thường.
6. **Kiểm toàn vẹn (cổng G8)** (`parsers/integrity.py`). Một đoạn chữ PDF bị coi là ẩn khi cỡ chữ dưới 2 pt, hoặc vô hình (alpha = 0) trên nền đồng màu, hoặc màu sáng (độ sáng tương đối ≥ 0,85) trên nền đồng màu (chênh xám dưới 16 mức khi render 72 dpi). Chữ ẩn bị loại khỏi văn bản phân tích. Mỗi đoạn còn được quét bằng `scan_injection` (`utils/security.py`) theo 5 nhóm dấu hiệu: đòi bỏ qua chỉ dẫn, giả thẻ hội thoại/system prompt, nói với "hệ thống chấm/AI", đòi một kết luận có lợi, đòi giấu cờ. Bộ quét chạy trên cả bản có dấu và bản bỏ dấu, gỡ ký tự vô hình, đổi chữ Cyrillic/Hy Lạp giống chữ Latin, ghép chữ viết cách quãng.
7. **Hồ sơ bộ tài liệu** (`agents/corpus.py:157-192`). Sau khi đọc, hệ thống lập hồ sơ: có tài liệu chứa tuyên bố không; có tài liệu **đối chiếu** (không phải nguồn tuyên bố, loại `financial / environmental / internal`) không; có **nguồn độc lập** (`legal / external / standard`) không; các năm xuất hiện nhiều nhất. `coverage` là tỉ lệ đạt của 4 mục này. `sufficient_for_absence = có đối chiếu VÀ có nguồn độc lập`: chỉ khi đúng như vậy, bộ kiểm chứng mới được nói "chưa được chứng minh" (`UNSUPPORTED`) thay vì "chưa đủ bằng chứng".

**Kết quả: số đoạn theo tệp.**

{{S2_DOCS}}

**Kết quả Ca A: toàn bộ 10 đoạn.** Mỗi đoạn mang `unit_id` (chính là `chunk_id`), tệp nguồn, số khối và các phép chuẩn hoá đã áp dụng:

{{S2_CHUNKS_A}}

Một bản ghi đầy đủ ở lớp `clean` (tệp `contract/clean.jsonl`):

{{S2_CLEAN_RECORD_A}}

**Kết quả: hồ sơ bộ tài liệu.**

{{S2_CORPUS}}

Ca A có đủ cả tài liệu đối chiếu (thuyết minh tài chính) và nguồn độc lập (thông báo pháp lý), nên `sufficient_for_absence = true`: hệ thống được phép kết luận `UNSUPPORTED` cho tuyên bố không tìm thấy gì xác nhận. Ca B chỉ có báo cáo thường niên làm tài liệu đối chiếu, không có nguồn độc lập, nên hệ thống không bao giờ kết luận `UNSUPPORTED` ở Ca B; tuyên bố không có gì xác nhận sẽ nhận `INSUFFICIENT_EVIDENCE`.

**Kết quả Ca B: trang đọc bằng OCR.**

{{S2_READING_B}}

**Cổng toàn vẹn và chất lượng đọc:**

{{S2_GATES_READING}}

## 4.3. Bước 3: Trích tuyên bố môi trường (`extract_green_claims`)

**Mục đích.** Từ các đoạn của tài liệu nguồn tuyên bố (`role = claim_source`), tìm những câu là **tuyên bố môi trường** và ghi lại câu đó nêu gì: chỉ số, số liệu, đơn vị, kỳ, năm gốc, phạm vi, có phải cam kết tương lai, có ngôn ngữ mơ hồ không.

**Thuật toán** (`agents/claim_extractor.py`, từ điển `configs/taxonomy.yaml` phiên bản `greenwashing-taxonomy-v4`). Bộ trích hoàn toàn bằng luật; mọi từ khoá được so trên câu đã bỏ dấu và hạ chữ thường.

1. **Tách câu** tại `. ! ?`, xuống dòng hoặc sau `;`; bỏ mảnh dưới 12 ký tự. Một câu có nhiều vế số liệu nối bằng `;`, "đồng thời", "trong khi đó", "mặt khác" được tách thành nhiều phát biểu khi mỗi vế có từ 6 từ trở lên và có chữ số.
2. **Gán loại tuyên bố** bằng cách đếm từ khoá của 8 loại trong từ điển: `emissions_reduction` (phát thải, carbon, CO2, khí nhà kính, net zero…), `renewable_energy` (năng lượng tái tạo, điện mặt trời, điện gió…), `resource_efficiency` (tiết kiệm năng lượng, tiết kiệm nước…), `waste_and_circularity` (tái chế, chất thải, kinh tế tuần hoàn…), `green_finance` (tín dụng xanh, trái phiếu xanh, sử dụng vốn), `biodiversity`, `esg_process_integration`, `generic_sustainability` (xanh, bền vững, thân thiện môi trường, ESG). Loại có nhiều từ khớp nhất thắng; hoà thì xét độ ưu tiên. Câu không khớp loại nào được thử thêm các **loại dự phòng** (`claim-typing-v2`, `fallback_types: true`): dùng tài nguyên (nước, điện, nhiên liệu), tuân thủ và quản lý môi trường, cây xanh và rừng, hoặc câu có tên chỉ số kèm số liệu. Vẫn không khớp thì bỏ qua. Câu tiếng Việt thuộc loại "bền vững chung chung" phải có ít nhất một từ môi trường mới được giữ (`claim-precision-v1`), vì phần lớn câu "bền vững", "ESG" bị trích sai là nói về xã hội hoặc quản trị.
3. **Loại câu không phải tuyên bố** bằng chuỗi luật, theo thứ tự, ghi lý do đầu tiên khớp: `chunk_boundary_fragment` (câu đầu đoạn bắt đầu bằng chữ thường, tức là phần đuôi của câu trước), `table_of_contents` (kết thúc bằng dấu chấm dẫn và số trang), `table_row` (có mã GRI như 305-1, hoặc mở đầu bằng đơn vị), `section_label` (có `|`, hoặc mở đầu bằng số thứ tự/chữ La Mã), `caps_run` (từ 3 từ IN HOA liên tiếp), `all_caps` (từ 70% chữ in hoa), `too_short` (dưới 6 từ và không có số), `fragment` (bắt đầu chữ thường và dưới 15 từ), `no_predicate` (không có động từ/vị ngữ trong danh sách: đã, đang, sẽ, được, đạt, giảm, tăng, thực hiện, triển khai, cam kết…), `generic_without_commitment` (loại chung chung, không số, không từ mơ hồ, không cam kết).
4. **Trích số** (`utils/text.py:110-255`). Đọc số theo cả kiểu Việt và kiểu Anh (`1.200.000`, `1,2`, `1.234,56`), nhân bội số (nghìn, triệu, tỷ), chuẩn hoá đơn vị (`tco2e`, `kgco2e`, `gwh/mwh/kwh`, `gj/mj/tj`, `m3`, tấn, kg, ha, tiền tệ, `%`). Số đứng sau từ nhãn (phạm vi, scope, ISO, GRI, điều, khoản, trang, nghị định…) trong 24 ký tự trước không được tính là số liệu; năm trần (1900–2100 không đơn vị) cũng không. Mỗi số kèm **nửa đơn vị chữ số có nghĩa cuối** để làm dung sai làm tròn: "12" là ±0,5; "12,5" là ±0,05; "112.000" là ±500.
5. **Gán thuộc tính** (`claim_extractor.py:272-301`). `metric` là nhóm chỉ số đầu tiên khớp (phát thải, năng lượng tái tạo, năng lượng, nước, chất thải, tài chính xanh); `direction` là `decrease` nếu có "giảm / cắt giảm / thấp hơn", `increase` nếu có "tăng / cao hơn"; `period` là năm đầu tiên trong câu, sau khi bỏ các năm nằm trong mã chuẩn (`ISO 14064-1:2018`, `14001:2015`) hay số hiệu văn bản (`08/2022/NĐ-CP`, `21/2025/QĐ-TTg`); `baseline` là năm cuối nếu câu có từ hai năm trở lên; `scope` là nhóm phạm vi đầu tiên khớp (phạm vi 1/2/3, toàn tập đoàn, công ty mẹ, nhà máy, sản phẩm, địa lý); `is_future_commitment` khi có "sẽ, dự kiến, mục tiêu, cam kết, lộ trình"; `is_vague` khi có từ mơ hồ ("hướng tới, cam kết mạnh mẽ, thân thiện, xanh hơn, hàng đầu, đáng kể, tích cực, toàn diện, nỗ lực, không ngừng") **và không có số**.
6. **Độ tin trích xuất** `confidence = min(0,96; 0,48 + 0,18·[có số] + 0,12·[loại khác generic])`, nên chỉ nhận bốn giá trị 0,48; 0,60; 0,66; 0,78. Đây là độ tin của bước trích, không phải độ tin của kết luận.
7. **Cờ "có thể không phải tuyên bố"** (`agents/claim_quality.py::suspect_reason`, bản `claim-quality v1.2` ngày 17/11). Không xoá câu, chỉ gắn `quality_flag`: `layout_glue` (chữ của bảng/bố cục dính vào câu: từ 3 số nguyên đứng riêng, chuỗi năm, chuỗi chữ in hoa dài, tiêu đề dính đầu câu, đơn vị đứng trước số từ hai lần, cụm lặp lại), `list_glue` (gạch đầu dòng đọc liền thành một câu), `fragment` (mảnh câu), `contact_line`, `standard_title`, `legal_text`. Câu mang cờ không được chấm rủi ro (trừ khi mâu thuẫn) và không vào hàng soát.
8. `claim_id = stable_id(chunk_id, câu)`; câu trùng (sau chuẩn hoá) bị bỏ.

**Kết quả Ca A: năm tuyên bố được giữ lại.**

{{S3_CLAIMS_A}}

Đối chiếu với đáp án ở mục 3.1: cả 5 câu tuyên bố của BCPTBV đều được nhận, câu tiêu đề "CÔNG TY CỔ PHẦN MINH HỌA - BÁO CÁO…" không bị coi là tuyên bố. Câu thứ nhất được nhận diện mơ hồ với ba từ khớp ("hướng tới", "thân thiện", "hàng đầu"). Câu Net Zero được gắn `is_future_commitment` và kỳ 2050. Câu "giảm 30%… năm 2024 so với năm 2023" có đủ chỉ số (`emissions`), hướng (`decrease`), giá trị (30 %), kỳ (2024) và năm gốc (2023); chỉ thiếu phạm vi.

**Câu bị loại ở Ca A:**

{{S3_REJECTED_A}}

Bản ghi đầy đủ của tuyên bố A1 ở lớp `extract`:

{{S3_EXTRACT_RECORD_A1}}

**Kết quả Ca B.** Từ 2.071 đoạn của BCPTBV 2025, bộ trích giữ 186 tuyên bố. Nó loại 472 câu, mỗi câu có ghi lý do, trong đó 18 câu "bền vững chung chung" không có từ môi trường (`claim-precision-v1`). Ngoài ra 12 câu được giữ nhưng gắn cờ "có thể không phải tuyên bố": 6 câu `list_glue`, 5 câu `layout_glue`, 1 câu `fragment`. Ba phiên bản trước giữ 156 tuyên bố (14/11), 179 (15/11) và 171 (16/11). Số đoạn tăng từ 911 lên 2.071 (2.043 đoạn văn, 28 bảng) vì từ 17/11 phân vùng trang giữ mỗi khối chữ của PDF thành một đơn vị riêng, và cắt khối một dòng thành từng ô, thay vì gộp nhiều khối theo toạ độ (Chương 12).

{{S3_STATS_B}}

Số câu bị loại vì `caps_run` lớn do BCPTBV dùng nhiều tiêu đề in hoa. Phân bố loại tuyên bố có cả các loại dự phòng của `claim-typing-v2`: 37 câu `resource_use`, 3 câu `metric_disclosure`, 3 câu `environmental_compliance`. Thuộc tính của các tuyên bố được theo dõi:

{{S3_CLAIMS_TRACED}}

Hai điểm người soát cần biết ngay ở bước này. (1) Với B1, "Hiện nay" không phải là năm. Từ 15/11, câu không ghi năm nhận năm của báo cáo làm kỳ, nên `period = 2025`. (2) Với B2, `period` để trống, vì 2018 trong "ISO 14064-1:2018" là năm ban hành của chuẩn chứ không phải kỳ báo cáo. Trước ngày 14/11, luật "năm đầu tiên trong câu là kỳ" đã lấy nhầm loại năm này, kể cả "2022" trong số hiệu Nghị định 06/2022/NĐ-CP; lỗi đã được sửa (mục 9.1). Phạm vi của B2 là `group_consolidated` ("cho toàn Tập đoàn"). Ví dụ câu có từ mơ hồ ở Ca B:

{{S3_VAGUE_EXAMPLES_B}}

## 4.4. Bước 4: Dựng chỉ mục truy xuất (`build_hybrid_retrieval_index`)

**Mục đích.** Dựng một lần cho cả phiên chỉ mục trên **mọi đoạn** (kể cả đoạn của tài liệu nguồn tuyên bố), để bước sau tìm bằng chứng cho từng tuyên bố.

**Thuật toán** (`retrieval/hybrid.py:83-175`, cấu hình `configs/default.yaml:24-33`). Ở hồ sơ offline, `embedding.provider = lite` và `reranker.provider = none`, nên chỉ mục gồm hai thành phần không cần mô hình nơ-ron:

1. **Chiều từ vựng BM25.** Tách token sau khi bỏ dấu, giữ token dài hơn 1 ký tự; tính tần suất tài liệu của từng token và độ dài trung bình đoạn. Tham số `k1 = 1,5`, `b = 0,75`, `idf = ln(1 + (N − df + 0,5)/(df + 0,5))`.
2. **Chiều "ngữ nghĩa" lite.** `TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5))` của scikit-learn, huấn luyện trên chữ của các đoạn; điểm là cosine giữa vectơ câu hỏi và vectơ đoạn. N-gram ký tự giúp khớp được các biến thể chính tả và từ ghép tiếng Việt mà không cần mô hình nhúng.

Khi bật hồ sơ có GPU (đã bị bác ngày 13/11), chiều thứ hai được thay bằng mô hình nhúng BGE-M3 và có thêm bộ xếp lại bge-reranker-v2-m3; mã cho các đường này có sẵn nhưng không chạy trong tài liệu này.

## 4.5. Bước 5: Truy xuất bằng chứng cho từng tuyên bố (`retrieve_evidence_per_claim`)

**Mục đích.** Với mỗi tuyên bố, lấy 5 đoạn có khả năng làm bằng chứng nhất.

**Thuật toán** (`hybrid.py:152-209`).

1. Điểm BM25 của từng đoạn được chuẩn hoá về [0, 1) bằng `s/(s + 3)`.
2. **Điểm gộp** `score = 0,55 × BM25 + 0,45 × điểm lite`; cộng thêm **0,025** nếu đoạn **không** thuộc tài liệu nguồn tuyên bố (ưu tiên bằng chứng bên ngoài); cộng **tiên nghiệm theo loại nguồn**: pháp lý 0,030; chuẩn mực 0,030; bên ngoài, môi trường, tài chính 0,015; nội bộ 0.
3. Bỏ chính đoạn chứa tuyên bố (`exclude_same_chunk`).
4. **Thứ tự** theo hợp nhất thứ hạng RRF: tổng `1/(60 + hạng)` của hai bảng xếp hạng (BM25 và lite), dùng điểm gộp để phân hoà. Điểm báo cáo vẫn là điểm gộp.
5. **Ngưỡng nhận** `score ≥ 0,12`. Nếu ít hơn 3 đoạn đạt ngưỡng, hệ thống bổ sung đoạn tốt nhất dưới ngưỡng cho đủ 3 và gắn `below_threshold = true`; đoạn dưới ngưỡng không bao giờ được dùng để kết luận "được ủng hộ".
6. Mỗi đoạn được quét lại bằng bộ phát hiện chèn lệnh; đoạn nghi chèn lệnh (`suspicious_instruction = true`) bị loại khỏi lập luận ở bước 6 (chính sách `injection_policy = exclude`).

**Kết quả: 5 đoạn bằng chứng của từng tuyên bố được theo dõi.**

*Tuyên bố A1* ("giảm 30% tổng phát thải…"):

{{S5_EV_A1}}

Đoạn đứng đầu (điểm gộp cao nhất) chính là đoạn chứa hai con số phát thải 2023 và 2024 trong thuyết minh tài chính. Bốn đoạn còn lại chỉ cùng chủ đề.

*Tuyên bố A2* ("vốn trái phiếu xanh được sử dụng hoàn toàn…"):

{{S5_EV_A2}}

*Tuyên bố B1* ("tỷ lệ tái chế chất thải rắn của nhóm thép đạt hơn 99%"):

{{S5_EV_B1}}

*Tuyên bố B2* ("hoàn thành kiểm kê khí nhà kính theo ISO 14064-1:2018… được BSI thẩm định"):

{{S5_EV_B2}}

**Phân bố điểm gộp trên toàn phiên:**

{{S5_SCORES_B}}

Ở Ca B, 5 đoạn của B1 đều đến từ chính BCPTBV (trang 9, 49 và 100). Đó là các tiêu đề và dòng mục lục "Quản lý chất thải rắn", không đoạn nào nêu tỉ lệ tái chế. Báo cáo thường niên không có đoạn nào về tỉ lệ tái chế của nhóm thép đủ điểm để lọt vào top 5. Với B2, cả năm đoạn đến từ báo cáo thường niên 2024 (trang 23, 46, 82), trong đó bốn đoạn kể việc BSI trao giấy kiểm tra, xác nhận khí nhà kính. Sự khác biệt này quyết định kết luận ở bước 6.
