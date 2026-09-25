# Mười bất biến kiến trúc — hiến pháp kỹ thuật của GreenScan

**Hiệu lực:** 2026-09-25 · **Quyết định:** `DECISIONS_LOG.md` D-2026-09-25-01
**Thi hành bằng:** [`tests/test_architecture_invariants.py`](../../tests/test_architecture_invariants.py) — 14 test, chạy trong CI.

> Một nguyên tắc viết trong tài liệu là một mong muốn. Một test đỏ là một ranh giới.
> Vì vậy mọi mục dưới đây đều có test canh; mục nào chưa canh được thì ghi rõ là chưa.

**Trục xuyên suốt:** Không hỏi *"AI có phát hiện greenwashing không"* trước. Hỏi: **với tuyên bố này, hệ thống đã tìm bằng chứng nào, chúng có so sánh được không, phép tính nào đã chạy, quy tắc nào thực sự áp dụng, và phần nào vẫn chưa biết.**

---

## Mười bất biến

| # | Bất biến | Hệ quả với code | Test canh |
| --- | --- | --- | --- |
| **1** | **Kiểm chứng tuyên bố, không phán xét doanh nghiệp** | Đơn vị trung tâm luôn là `claim`. Không tồn tại trường kết luận cấp doanh nghiệp. Dashboard chỉ tổng hợp **thống kê rủi ro/cần soát**, không thành phán quyết đạo đức hay pháp lý cho cả công ty | `invariant_1_no_company_level_verdict_exists_anywhere` (quét mã nguồn) |
| **2** | **Tuyên bố phải nguyên tử và giữ nguyên gốc** | Câu nhiều khẳng định → tách, nhưng **mọi** đối tượng giữ `doc_id` · `chunk_id` · trang · nguyên văn. Chuẩn hoá không được xoá đường về câu gốc | `invariant_2_every_extracted_object_can_be_traced_to_its_source` |
| **3** | **Truy xuất tìm ứng viên, không quyết định sự thật** | Tương đồng cao ≠ bằng chứng ủng hộ. Chỉ **số học**, **cue** hoặc **mô hình đã escalate** được phép đứng về một phía; tương đồng đơn thuần không bao giờ ra SUPPORTED/CONTRADICTED | `invariant_3_similarity_alone_never_produces_a_decisive_verdict` |
| **4** | **Chỉ so cái thật sự so được** | Trước mọi phép tính: chỉ số · loại giá trị · đơn vị · kỳ · năm gốc · ranh giới tổ chức · Scope · công nghệ. Lệch một chiều → **cấm** kết luận mâu thuẫn | `invariant_4_a_dimension_mismatch_can_never_be_a_contradiction` (3 ca) + 44 trap |
| **5** | **Số học là của code** | % thay đổi, đổi đơn vị, điểm phần trăm vs tương đối, xu hướng, cross-foot đều do code tính; `computed_values` mang `policy_id` và phép tính. **Mô hình không được ghi đè comparator** | `invariant_5_numeric_conclusions_carry_the_policy_and_the_calculation` · `invariant_5_a_model_may_not_overrule_the_comparator` (kiểm thứ tự trong `_stance`) |
| **6** | **Mục tiêu ≠ thành tích; thiếu dữ liệu ≠ thất bại** | "Sẽ giảm 30%" không chứng minh "đã giảm 30%". Không tìm thấy ≠ bằng chứng nói ngược. `UNSUPPORTED`/`INSUFFICIENT` tách hẳn khỏi `CONTRADICTED` — kể cả trong thang điểm | `invariant_6_absence_and_contradiction_stay_different` · `absence_of_support_never_scores_as_high_as_contradiction` |
| **7** | **Pháp lý phải kiểm *applicability*, không chỉ *relevance*** | Cùng chủ đề chưa đủ: phải qua ngày hiệu lực → ngành → chủ thể → loại tuyên bố → điều kiện. Quy tắc bị loại phải ghi **lý do** | `invariant_7_the_legal_layer_separates_relevance_from_applicability` |
| **8** | **Abstain là kết quả hợp lệ** | Thiếu bằng chứng, chiều không rõ, luật chưa mã hoá, mô hình bất định → `INSUFFICIENT_EVIDENCE` / chuyển người. Không ép đường chạy phải có kết luận | `invariant_8_the_pipeline_is_allowed_to_decline` |
| **9** | **Verdict ≠ risk ≠ priority** | Verdict nói quan hệ tuyên bố–bằng chứng. Risk nói mức cần chú ý theo rubric. Priority nói nên mở cái nào trước. Không dùng 72/100 thay cho đúng/sai; không suy ngược verdict từ vị trí hàng đợi | `invariant_9_verdict_risk_and_priority_are_not_interchangeable` |
| **10** | **Tái lập được và người kiểm tra được** | Manifest ghi hash đầu vào, phiên bản corpus, rule pack, prompt/model. Mọi kết luận có trích dẫn. Phần **chưa tính** ghi `not_computed`, **không giả làm 0** | 3 test: manifest · `not_computed` · trích dẫn bắt buộc |

---

## Những điều từ nay không được làm

Mỗi dòng dưới đây từng là một lỗi thật đã đo được, không phải lo xa:

| Cấm | Vì sao |
| --- | --- |
| Thêm LLM judge rồi cho ghi đè comparator tất định | Kết luận về doanh nghiệp phải chỉ ra được phép tính |
| Dùng điểm tương đồng RAG làm độ tin cậy bằng chứng | Tương đồng đo *giống*, không đo *đúng* |
| Coi "không tìm được" là "sai" | Thế giới mở: không tìm thấy ≠ không tồn tại |
| Gộp `UNSUPPORTED` và `CONTRADICTED` vào cùng mức rủi ro vì điểm bằng nhau | Hai phát hiện khác nhau; đã sửa bằng `max_without_contradiction` |
| Lấy mục tiêu tương lai làm bằng chứng cho thành tích hiện tại | T08 |
| So Scope 1+2 với Scope 1, tập đoàn với nhà máy, tuyệt đối với cường độ chỉ vì cùng `tCO₂e` | 5/8 mâu thuẫn sai ngày 22/09 đúng là loại này |
| Áp quy tắc vì nó "có vẻ liên quan" | Bất biến 7 |
| Báo `0` cho tín hiệu chưa tính được | `anomaly` đã sửa: `not_computed`, mẫu số hạ 100 → 90 |
| Tối ưu `priority-v1` đến mức đổi nghĩa của verdict | Bất biến 9 |
| Thêm GraphRAG, fine-tune, đa tác tử hay quantum **chỉ để trông "AI hơn"** | Chỉ thêm khi giải quyết một failure mode **đã đo được**. Có test quét mã nguồn |

---

## Definition of Done đổi từ "xong tính năng" sang "giữ được bài học"

Mỗi thay đổi phải trả lời được bảy câu trong [`.github/pull_request_template.md`](../../.github/pull_request_template.md). Không trả lời được thì **chưa merge**. Bốn câu quan trọng nhất:

- Điều gì xảy ra khi **thiếu bằng chứng**?
- Điều gì xảy ra khi đầu vào **không so sánh được**?
- Thay đổi này có thể làm **tăng mâu thuẫn sai** không?
- Có quyết định nào **chuyển từ luật sang mô hình** không?

---

## Thứ tự làm việc (thay thứ tự cũ)

```text
Đóng băng baseline
  → Audit ngữ nghĩa HPG (không phải diff số lượng)
  → Gold bằng chứng + nhãn ưu tiên
  → Đánh giá TÁCH RIÊNG: truy xuất và kiểm chứng
  → 3 quy tắc pháp lý thật
  → Ca so chéo kỳ / chéo bảng
  → Provenance sâu hơn (ô bảng)
  → UI demo
```

**Không phải:** UI → thêm AI → thêm GraphRAG → thêm luật → fine-tune → chạy test cuối.

Hai danh sách trông giống nhau về tính năng nhưng khác hẳn về bản chất: thứ tự trên giữ *Models read · Rules decide · Humans review*, thứ tự dưới biến sản phẩm thành một bộ phân loại có trang trí.

### Audit HPG là audit kiến trúc, không phải regression diff

Khi một mâu thuẫn cũ biến mất, câu hỏi **không** phải *"vì sao số CONTRADICTED giảm"*, mà là:

> Tuyên bố và bằng chứng có cùng chỉ số không? Cùng Scope không? Cùng ranh giới tổ chức không? Giá trị là tuyệt đối hay mức thay đổi? Nếu tuyên bố nói −20%, code đã tính lại từ kỳ gốc chưa? Nếu không so được, **vì sao trước đây lại kết luận mâu thuẫn**?

Công cụ trả lời sáu câu đó: `python tools/hpg_semantic_audit.py` — với **mỗi** mâu thuẫn trong bản trước, nó chạy lại quy tắc hiện tại trên **đúng đoạn văn đã tạo ra kết luận cũ**, in ra sáu chiều của từng cặp số và chiều nào chặn. Kết quả lần chạy 25/09 (`benchmark/semantic_audit_2026-09-25.md`):

| Chiều khiến hai con số không so được | Số cặp |
| --- | ---: |
| khác công nghệ sản xuất | 2 |
| khác cơ sở đo (tỷ trọng / mức thay đổi / tuyệt đối / cường độ) | 2 |
| chênh hàng chục lần → cần người xem | 2 |
| khác loại chỉ số con | 2 |
| mục tiêu vs số thực hiện | 1 |
| không phải kết luận số học ngay từ đầu | 1 |

**Không mâu thuẫn nào trong bản cũ sống sót.** Comparator cũ chỉ kiểm **đơn vị** — đó là toàn bộ nguyên nhân. Đây là câu trả lời cho *"vì sao trước đây lại kết luận mâu thuẫn"*, và nó nằm trong một tệp chạy lại được, không nằm trong trí nhớ.

### Đánh giá phải tách đôi

```text
Truy xuất:    claim → ứng viên → gold evidence có trong đó không?   (Recall@k, MRR, nDCG)
Kiểm chứng:   gold claim + gold evidence → verdict đúng không?      (macro-F1, false contradiction)
```

Một chỉ số end-to-end duy nhất không cho biết lỗi nằm ở đâu. Truy xuất hỏng → sửa truy xuất. Truy xuất đúng mà verdict sai → sửa verifier.

---

## Liên quan

[DECISIONS_LOG.md](DECISIONS_LOG.md) · [ISSUES_REGISTER_2026-09.md](ISSUES_REGISTER_2026-09.md) (mục N, P) · [RESEARCH_PROGRAM_2026-09-22.md](RESEARCH_PROGRAM_2026-09-22.md) · [../02-product/AUDITOR_WORKFLOW_POSITIONING.md](../02-product/AUDITOR_WORKFLOW_POSITIONING.md) · [../../tests/test_audit_checklist.py](../../tests/test_audit_checklist.py) (T01–T17)
