# Chương 10. Tuỳ biến theo tổ chức và học từ phản hồi của người soát

Chương này trình bày hai phần thêm ngày 14/11/2026: **org pack tự phục vụ** (org-pack-v1, quyết định D-2026-11-14-04) và **vòng học từ phản hồi** (feedback-loop-v1, D-2026-11-14-03). Mọi số liệu là **[ĐÃ THỰC NGHIỆM]**: chúng được sinh ra bằng `tools/thuyet_minh/run_feedback_demo.py` trên kho tạm (không đụng kho thật), cùng mã với Chương 4–8. Thiết kế đầy đủ nằm ở `docs/03-architecture/ORG_PACK.md` và `docs/03-architecture/FEEDBACK_LOOP.md`. Kiểm thử ở `tests/test_org_pack_upload.py` (10 ca) và `tests/test_feedback_loop.py` (21 ca). Toàn bộ kho mã có 729/729 bài kiểm qua.

Cả hai phần tuân theo một nguyên tắc: **thông tin của tổ chức và của người soát được thêm bên cạnh kết luận, không bao giờ đổi kết luận**. Kết luận kiểm chứng, điểm rủi ro và trạng thái phát hành vẫn chỉ do luật quyết định. Hàng soát chỉ được thêm mục, không bị bớt mục nào.

## 10.1. Org pack tự phục vụ

### 10.1.1. Luồng xử lý

| Bước | Ai làm | Hệ thống làm gì | Mã |
|---|---|---|---|
| 1. Tải lên | Người của tổ chức | Mở gói zip hoặc tệp theo giới hạn (≤ 30 tệp, ≤ 2 MB mỗi tệp, ≤ 5 MB tổng; chỉ `.yaml .md .txt .pdf .docx`; không đường dẫn tuyệt đối, không `..`). Kiểm lược đồ `org-pack-v0`; pack lỗi bị từ chối kèm mọi lỗi. **Xoá tên người duyệt ghi sẵn trong tệp**, nên gói luôn vào kho dưới dạng bản nháp | `legal/org_registry.ingest` |
| 1'. Hoặc soạn nháp | Người của tổ chức | Đọc văn bản chính sách và nhận điều khoản theo số (§2.1, Điều 3…). Mỗi câu nêu nghĩa vụ thành một quy tắc; mẫu nhận ra được thì thành kiểm máy làm được, phần còn lại thành `manual` | `legal/org_draft.draft` |
| 2. Duyệt | Người khác người tải lên | Ghi tên người duyệt vào bản lưu, kiểm lại lược đồ, ghi sự kiện vào `registry.jsonl` (chỉ ghi thêm) | `org_registry.approve` |
| 3. Chọn cho lượt chạy | Người soát | `org_packs: ["ngan_hang_xanh_demo"]` chọn bản đã duyệt mới nhất; `org_id@phiên_bản` chọn một bản cụ thể | `org_registry.resolve`, `api._settings_for` |
| 4. Áp quy tắc | Hệ thống | Mỗi quy tắc ra Đạt / Không đạt / Cần người xem / Không áp dụng, đặt cạnh kết luận. `on_fail: raise_priority` thêm tuyên bố vào hàng soát | `orchestrator._org_record`, `feedback/queue.raise_queue` |

### 10.1.2. Soạn nháp từ văn bản chính sách trình diễn

Đầu vào là `configs/org_packs/demo_ngan_hang_xanh/internal_policy.md`, chính sách tín dụng xanh của một ngân hàng giả lập. Bộ soạn theo luật cho ra 9 quy tắc, 0 lỗi lược đồ:

| Quy tắc | Điều khoản | Kiểu kiểm sinh ra | Ghi chú |
|---|---|---|---|
| NHAP_001 | §1.2 | `manual` | Câu nói về thứ bậc pháp luật, không kiểm máy được |
| NHAP_002 | §2.1 | `claim_attribute_present: baseline` | Có điều kiện áp dụng: câu nói về "giảm" |
| NHAP_003 | §2.2 | `claim_attribute_present: scope` | |
| NHAP_004 | §2.3 | `claim_attribute_present: baseline` | Từ câu "mục tiêu tương lai phải nêu năm đích và năm gốc" |
| NHAP_005 | §2.3 | `manual` (mức `violation`) | "Mục tiêu không được dùng để chứng minh thành tích" |
| NHAP_006 | §3.1 | `claim_terms_absent` | Danh sách cấm lấy từ ngoặc kép đứng sau "không chấp nhận": "trung hòa carbon", "net zero", "carbon neutral", "không phát thải"… |
| NHAP_007 | §3.1 | `manual` | Câu "cán bộ yêu cầu bổ sung chứng nhận" |
| NHAP_008 | §4.1 | `evidence_independent` | |
| NHAP_009 | §5.2 | `manual` | Trách nhiệm rà soát của Phòng Tuân thủ |

Bản thử đầu tiên gặp hai lỗi, và các lỗi này được giữ lại làm bài kiểm:
- **"cấm" khớp nhầm "cam kết":** sau khi bỏ dấu, "cấm" và "cam kết" giống nhau, nên câu §2.3 có "(cam kết, phấn đấu, 'đến năm 20xx')" bị đọc thành lời cấm, và cụm "đến năm 20xx" thành từ bị cấm. Sửa: lời cấm được đọc trên chữ có dấu, và từ trong ngoặc chỉ thành từ cấm khi đứng **sau** lời cấm.
- **Thiếu cụm "không chấp nhận":** bộ nhận lời cấm chưa có cụm này nên bỏ sót §3.1. Đã thêm.

### 10.1.3. Tải lên, duyệt bốn mắt và chạy trên Ca B

- **Tải lên:** pack trình diễn `demo_ngan_hang_xanh` (5 quy tắc NHXD_001–005) được tải lên bởi "Lan (Khối Rủi ro)" và lưu là bản `0.1.0-fa16f02316`. Tệp gốc có ghi sẵn người duyệt, nên hệ thống xoá tên đó (`self_approval_removed = true`).
- **Duyệt:** "lan (khối rủi ro)" (cùng người, khác chữ hoa) duyệt thì bị từ chối: "người duyệt phải khác người tải lên (bốn mắt)". "Minh (Phòng Tuân thủ)" duyệt thì được.
- **Chạy:** Ca B (Hòa Phát, 156 tuyên bố ở bản 14/11) chạy lại với pack đã duyệt. **Kết luận của 156 tuyên bố giống hệt lượt chạy không có pack** (so từng tuyên bố). Bản 15/11 (179 tuyên bố) cũng cho kết luận giống hệt, hàng đợi 17 mục, trong đó 8 mục do quy tắc nâng.

| Quy tắc | `on_fail` | Không đạt | Cần người xem | Đạt | Không áp dụng |
|---|---|---|---|---|---|
| NHXD_001 (tuyên bố giảm phải nêu năm gốc) | flag_for_review | 43 | 0 | 0 | 113 |
| NHXD_002 | flag_for_review | 3 | 0 | 6 | 147 |
| NHXD_003 (từ tuyệt đối khi chưa có chứng nhận) | **raise_priority** | 8 | 0 | 148 | 0 |
| NHXD_004 (thép: cần nguồn độc lập) | flag_for_review | 0 | 70 | 0 | 86 |
| NHXD_005 | flag_for_review | 33 | 0 | 0 | 123 |
| **Cộng** | | **87** | **70** | **154** | **469** |

8 tuyên bố vi phạm NHXD_003 được thêm vào hàng soát, nên hàng soát tăng từ 8 lên 15 mục. Điểm ưu tiên và thứ hạng của mọi mục giữ nguyên; mỗi mục được thêm có ghi `raised_by: org_rule:demo_ngan_hang_xanh/NHXD_003`.

Ví dụ trên một tuyên bố: "…hiện thực hóa cam kết đạt mức phát thải ròng bằng không (**Net Zero**) vào năm 2050."
- **Kết luận kiểm chứng:** vẫn là "ủng hộ một phần".
- **NHXD_001:** không đạt, "Tuyên bố không nêu năm gốc".
- **NHXD_003:** không đạt, "Câu tuyên bố dùng từ bị hạn chế: 'Net Zero'".
- **NHXD_004:** cần người xem, "Chưa thấy đoạn bằng chứng nào từ nguồn độc lập… Chưa xác định không có nghĩa là không đạt".

## 10.2. Vòng học từ phản hồi

### 10.2.1. Vì sao không học trực tuyến

Nếu mỗi lần người soát sửa mà mô hình tự đổi theo, ba điều sẽ hỏng:
- kết luận đổi mà không qua đo (trái D-2026-10-16-01);
- doanh nghiệp bị kiểm có thể "dạy" hệ thống chấp nhận tuyên bố của mình;
- cùng một hồ sơ, hai tuần ra hai kết luận mà không có phiên bản nào giải thích.

Vì vậy vòng học đi theo thứ tự: **phản hồi → đề xuất có phiên bản → đo → người duyệt → phát hành**. Năm tầng của vòng học, từ rẻ và an toàn tới đắt, được tóm ở Bảng 10.1.

| Tầng | Đầu vào | Đầu ra | Đổi kết luận? |
|---|---|---|---|
| 0. Nhãn chỉ chỗ | Quyết định của người soát và đoạn quyết định | Giai đoạn máy sai: `retrieval` / `reading` / `rule` / `none` | Không |
| 1. GS-Feedback | Mọi quyết định đã chốt và đã lọc | Ca kiểm chạy trên bằng chứng đã chụp; bánh cóc `ratchet.json` | Không |
| 2. Tiền lệ | Quyết định đã chốt mà triển khai này được xem | Thẻ tiền lệ cạnh kết luận; thêm chỗ trong hàng soát; ví dụ mẫu cho S5 (mặc định tắt) | Không |
| 3. Máy đào luật | Các lần ghi đè | Phiếu đề xuất có đo (cụm từ, ngoại lệ quy tắc, từ đồng nghĩa, quy tắc org pack nháp) | Không; người duyệt quyết |
| 4. Mô hình thách đấu | Cặp (tuyên bố, đoạn, quan hệ) | Mô hình ở trạng thái candidate; chỉ thăng hạng khi qua cổng và có người khác ký | Chỉ khi đã thăng hạng và được bật |

### 10.2.2. Ca A: một lần ghi đè đi qua cả năm tầng

**Lượt 1, người soát quyết định.** Người soát "Hà (kiểm toán viên)" xử lý 5 tuyên bố của Ca A:
- 4 tuyên bố được xác nhận, mỗi tuyên bố kèm đoạn bằng chứng đứng đầu làm đoạn quyết định.
- Tuyên bố A2 được ghi đè. Câu A2: "Nguồn vốn từ trái phiếu xanh được sử dụng hoàn toàn cho các dự án đủ điều kiện xanh."
  - Máy kết luận "ủng hộ một phần"; người soát sửa thành "mâu thuẫn", lý do `MODEL_MISREAD`.
  - Đoạn quyết định là đoạn đứng **hạng 1** trong danh sách bằng chứng máy đưa ra: "…320 tỷ đồng đã giải ngân cho dự án điện mặt trời; 180 tỷ đồng đang nằm trong tài khoản tiền gửi và chưa được phân bổ…".
  - Vì máy đã có đúng đoạn này mà vẫn kết luận sai, hệ thống tự ghi giai đoạn sai là **`reading`** (đọc sai, không phải tìm sai).

**Tiền lệ (lượt 2).** Chạy lại Ca A bằng cùng tài liệu:
- Kết luận của cả 5 tuyên bố giống hệt lượt 1.
- Cả 5 tuyên bố có thẻ tiền lệ (độ giống 1,0).
- A2 được thêm vào hàng soát (`raised_by: precedent:4a669d2f…/5a7271fe…`) vì người soát từng ghi đè máy ở chính câu này. Điểm 49,58 và thứ hạng 5 giữ nguyên.
- Manifest ghi đường dẫn, số bản ghi và sha256 của kho quyết định đã được dùng.

**GS-Feedback.** 5 quyết định thành 5 ca. Chạy lại trên bằng chứng đã chụp, kèm hồ sơ kho tài liệu của phiên gốc:

| Ca | Nhãn người soát | Hệ thống hôm nay | Qua? |
|---|---|---|---|
| …b313ba | UNSUPPORTED | UNSUPPORTED | Có |
| …b4c068 | CONTRADICTED | CONTRADICTED | Có |
| …2c08a1 | CONTRADICTED | CONTRADICTED | Có |
| …2addb6 | UNSUPPORTED | UNSUPPORTED | Có |
| …0c8036 (A2) | CONTRADICTED | PARTIALLY_SUPPORTED | Không: việc cần làm, không phải hồi quy |

Bánh cóc giữ 4 ca. Ở lần chạy sau, nếu một trong 4 ca này hỏng thì lệnh `quantum-agent feedback-bench` trả mã lỗi.

Bản thử đầu tiên của GS-Feedback ra INSUFFICIENT_EVIDENCE cho hai ca UNSUPPORTED. Lý do là bộ kiểm chứng chỉ được kết luận "không có bằng chứng" khi biết đã tìm trong những gì (hồ sơ kho tài liệu). Sửa: ca GS-Feedback lấy hồ sơ kho từ phiên gốc. Hai ca này nay qua.

**Máy đào luật.** Từ đoạn quyết định của A2, máy đào đề xuất đúng một cụm bác bỏ: **"chưa được phân bổ"**. Các cụm bị cắt cụt như "và chưa được phân" hay "tiền gửi và chưa" đã bị luật cắt cụm loại. Phiếu đề xuất tự ghi chú: đoạn quyết định nằm trong tài liệu của chính doanh nghiệp, nên chốt chống vu oan vẫn bỏ qua cụm này. Đo với `--measure --bench-limit 453`, dùng một bản sao tạm của `stance_cues.yaml`:

| Bộ đo | Trước | Sau khi thêm cụm | Kết luận |
|---|---|---|---|
| GS-Feedback (5 ca) | qua 4 | qua 4; sửa 0, hỏng 0 | Không giúp ca A2 |
| GS-Bench (453 ca) | đúng 219 | đúng 219; 0 ca đổi nhãn; 0 "mâu thuẫn" sai mới (786 giây) | Vô hại nhưng vô ích |

Đề xuất **không được áp dụng**. Muốn sửa A2 thì phải đổi chính sách chốt chống vu oan, và đó là quyết định của con người (Chương 9, hạn chế 1). Đây đúng là việc vòng học phải làm: biến một lần sửa thành một câu hỏi có số đo, thay vì thành một thay đổi lặng lẽ.

**Hai người soát.** "Lan (kiểm toán viên 2)" soát mù lại A2 và cũng kết luận "mâu thuẫn": 1 ca soát hai lần, đồng ý 1, kappa 1,0. Đây là con số minh hoạ cơ chế, n = 1.

### 10.2.3. Mô hình thách đấu và cổng thăng hạng

**Dữ liệu:** 824 cặp, gồm 821 cặp Claude gán nhãn theo bộ quy tắc (hai lượt cộng phân xử, tác giả rà soát) và 3 cặp nhãn chỉ chỗ từ Ca A. Phân bố: CONTEXT 633, PARTIAL 125, SUPPORTS 63, CONTRADICTS 3. Tách theo công ty hoặc theo phiên: 691 cặp huấn luyện, 133 cặp giữ lại.

**Mô hình:** `hashed-linear-v1` là hồi quy logistic trên đặc trưng băm (từ, cặp từ, 4-gram ký tự đã bỏ dấu, từ chung giữa tuyên bố và đoạn, khớp số), huấn luyện trên CPU trong vài giây. Nhà vô địch là quan hệ do luật gán trên đúng các cặp đó.

| Chỉ số trên 133 cặp giữ lại | Luật (nhà vô địch) | Mô hình thách đấu |
|---|---|---|
| Macro-F1 (4 quan hệ) | **0,345** | 0,183 |
| SUPPORTS sai (đoạn chỉ là bối cảnh hoặc bác bỏ) | 6 | 0 |
| CONTRADICTS sai | 0 | 0 |
| Dự đoán | đa dạng (PARTIAL 105, CONTEXT 13, SUPPORTS 13, CONTRADICTS 2) | **CONTEXT cho cả 133 cặp** |

Mô hình thách đấu suy biến: lớp CONTEXT chiếm 77% dữ liệu, và đặc trưng băm không đủ để tách các quan hệ còn lại. Cổng ghi:
- "đạt: 133 cặp giữ lại được chấm (cần ≥ 30)";
- "**KHÔNG đạt**: macro-F1 0.183 so với nhà vô địch 0.345";
- "đạt: CONTRADICTS sai 0 so với 0";
- "đạt: SUPPORTS sai 0 so với 6".

Mô hình ở lại trạng thái candidate và không ai thăng hạng được nó. `feedback.local_stance_model` từ chối nạp mọi mô hình chưa thăng hạng, và từ chối cả mô hình đã thăng hạng nếu tệp trọng số bị tráo sau khi đăng ký. Nếu chỉ nhìn số "SUPPORTS sai 0", người ta dễ tưởng mô hình an toàn hơn luật. Cổng có nhiều điều kiện chính là để chặn kiểu nhầm đó.

### 10.2.4. Lọc nhãn và phạm vi tổ chức

| Cơ chế | Hành vi đã kiểm |
|---|---|
| Vai trò `reviewed_company` | Nhãn được lưu trong vết kiểm toán, `train_eligible = false`, không vào GS-Feedback, không vào dữ liệu huấn luyện |
| Soát mù lần hai | Lấy mẫu tất định theo tháng (hạt giống `YYYY-MM`, mặc định 10%). Người thứ hai phải khác người đầu. Ca bất đồng bị giữ ngoài cho tới khi có trọng tài; nhãn trọng tài thay nhãn cũ |
| Phạm vi tổ chức | Triển khai cấu hình `org_id = X` chỉ thấy nhãn lõi và nhãn của X; nhãn của tổ chức khác chỉ hiện sau khi đội GreenScan thăng hạng lên lõi |
| Mã băm cấu hình | `settings.feedback` để mặc định thì không vào bản dump, nên mã băm cấu hình của mọi lượt chạy cũ giữ nguyên (`d1599c3f9c61`) |

## 10.3. Giao diện, API, MCP và bản trình diễn

- **Thanh quyết định:** nút **Chỉ đoạn quyết định** (đánh dấu đoạn, hoặc dán trích dẫn khi máy không đưa ra đoạn đó) và ô **vai trò** người soát.
- **Trang tuyên bố:** mục **Tiền lệ của người soát**, kèm lý do vì sao tuyên bố được đưa vào hàng soát.
- **Trang Học từ phản hồi:** nhãn, giai đoạn máy sai, bánh cóc, độ đồng thuận, lấy mẫu soát lần hai, phiếu đề xuất, mô hình thách đấu và kết quả cổng.
- **Thư viện pháp lý → Gửi bộ quy tắc của tổ chức bạn:** tải lên, soạn nháp, duyệt, thu hồi, thử trên một câu. Trang **Tải tài liệu** có thêm ô chọn bộ quy tắc đã duyệt.
- **API:** `/v1/org-packs/upload`, `…/approve`, `…/retire`, `/v1/org-packs/preview`, `/v1/org-packs/draft`, `/v1/feedback/*`. Trường `org_packs` được thêm vào các lệnh phân tích.
- **Công tắc mô hình (16/11, `model-mode-v1`):** ở trang Cài đặt và trang Phân tích mới, người dùng chọn chỉ luật, mô hình trên máy hoặc mô hình trên đám mây, và bấm thử một lượt gọi (`/v1/runtime/model-mode`, `/v1/runtime/model-test`). Xem mục 2.3.
- **Giao diện gọn (17/11, `next-step-v1`, D-2026-11-17-01):** mỗi trang của quy trình (Phân tích mới, Hàng đợi, Chi tiết tuyên bố, Xuất kết quả) có một dòng "Việc tiếp theo" kèm một nút. Trang chi tiết tuyên bố mặc định ở chế độ "xem gọn", có nút mở bản đầy đủ. Hàng đợi chỉ đếm tuyên bố và báo khi đã soát xong. Có thêm bộ mẫu "Công ty Minh Họa" để thử ngay. Các thay đổi này không đổi luật, kết luận hay thứ tự hàng đợi. Chi tiết ở `docs/03-architecture/GIAO_DIEN_GON_VA_THU_MAY_2026-11-17.md`.
- **Phông chữ (18/11):** giao diện và giấy làm việc nhúng phông Roboto (bản Latin và tiếng Việt, giấy phép OFL), để chữ tiếng Việt hiển thị giống nhau trên mọi máy, kể cả khi giấy làm việc HTML được gửi sang máy không cài Roboto.
- **MCP:** thêm 2 công cụ, `precedents` và `org_pack_preview`, nâng tổng số lên 14. Cả hai đi qua chốt phạm vi; câu chèn lệnh bị chặn trước khi tra.
- **Bản trình diễn trực tuyến** (https://chonnhan2023-greenscan-ai.static.hf.space): Hugging Face đòi gói trả phí cho Space chạy Docker, nên đội dựng bản tĩnh miễn phí.
  - `tools/build_static_demo.py` gọi chính máy chủ GreenScan cho mọi endpoint GET và xuất nguyên văn ra tệp. Giao diện thật chạy trên các tệp đó qua lớp `frontend/src/staticApi.js`.
  - Bản gồm 4 phiên: Hòa Phát; Hòa Phát cộng bộ quy tắc ngân hàng xanh; Ca A lượt 1 và lượt 2.
  - Quyết định soát lưu trong trình duyệt, theo đúng luật của kho quyết định. Phân tích tài liệu mới cần bản cài đặt.
  - Đã kiểm bằng Chromium không giao diện trên đường dẫn thật: 8 trang chính tải đủ dữ liệu, 0 yêu cầu lỗi.

## 10.4. Giới hạn

1. **Tiền lệ so theo chữ, không theo nghĩa.** Hai câu cùng ý viết khác chữ không khớp; câu cùng chữ khác chủ thể vẫn khớp. Thẻ tiền lệ ghi "từ chung" để người soát tự cân nhắc.
2. **Mô hình CPU quá yếu** với dữ liệu lệch lớp. Bước tiếp theo là huấn luyện cross-encoder tiếng Việt trên GPU Kaggle qua cùng bộ dữ liệu và cùng cổng; cần thêm nhãn chỉ chỗ cho PARTIAL, SUPPORTS và CONTRADICTS.
3. **Bộ soạn nháp theo luật nhận mẫu bằng từ khoá.** Trên chính sách trình diễn, 4/9 quy tắc là `manual`, nên người viết pack vẫn phải đọc và sửa trước khi duyệt.
4. **Bản trình diễn tĩnh không chạy phân tích mới**, và ảnh trang gốc ở bản tĩnh không tô sáng đoạn bằng chứng.
5. **Kappa trên 1 ca chỉ minh hoạ cơ chế**, chưa phải số đo về độ đồng thuận.
