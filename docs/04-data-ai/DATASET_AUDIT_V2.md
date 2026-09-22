# Dataset Audit v2 — lineage, maturity, split

**2026-08-09.** Ba từ hay bị dùng lẫn nhau, và phải tách rõ:

| Từ | Nghĩa | Trạng thái |
| --- | --- | --- |
| **unified** | hợp nhất vật lý/schema | ✅ đạt |
| **audited** | kiểm tra tính toàn vẹn | ✅ đạt (8/8 invariant) |
| **adjudicated** | con người kiểm chứng ngữ nghĩa | ❌ **5/7.960 = 0,06%** |

Chạy: `python tools/dataset_audit_v2.py all`

---

## 1. Lineage audit — v1 merge có hai lỗi thật

Bản merge v1 gộp theo `doc_id` rồi bỏ phần còn lại. Audit bắt được hai hệ quả:

**a) Trùng nội dung bị vô hình — và đây là rủi ro leakage.**
`doc_id` có dạng `<target>:<sha16>`, nên cùng một thông cáo ASIC thu dưới
Vanguard, Mercer, Black Mountain và TLOU sinh ra bốn id khác nhau cho **một
artifact**. Không có gì ghi lại rằng chúng cùng bytes:

```
ab639a4fce1e9bdb  ['INT-VANGUARD-AU:…', 'INT-MERCER-AU:…']
12bc19f0f33e86da  ['INT-MERCER-AU:…', 'INT-TLOU-AU:…', 'INT-BLACK-MOUNTAIN-AU:…']
```

Nếu chia tập theo `doc_id`, một bản có thể rơi vào train và bản kia vào test —
mô hình được chấm trên tài liệu nó đã đọc.

**b) Mất dấu ingestion.** Phase 1 (case pack) và phase 2 (disclosure) chạy tách
nhau chỉ vì **SQLite write contention** — vấn đề lưu trữ, không phải ontology.
Sau merge không còn gì cho biết dòng nào từ phase nào, nên lỗi đặc thù theo
phase không truy vết được.

**Đã sửa** (`tools/repair_legal_case_lineage.py`): thêm `content_group`,
`duplicate_of`, `ingestion_phase`, kèm `MERGE_MANIFEST.json` chứng minh
`union(root_A, root_B) → 297 unique`.

| Chỉ số | Giá trị |
| --- | ---: |
| documents | 297 |
| content group có >1 thành viên | 8 |
| dòng đánh dấu duplicate | 9 |
| phase1_case_pack / phase2_disclosure | 117 / 180 |

**Bản trùng được đánh dấu, không xóa.** Bản thứ hai mang provenance thật (một
target khác đã tìm thấy nó); xóa đi là hủy thông tin. Nhưng **mọi split phải gom
theo `content_group`, không theo `doc_id`.**

---

## 2. Sáu mức trưởng thành

| Mức | Số lượng | Dùng cho | **Không** dùng cho |
| --- | ---: | --- | --- |
| **L0 RAW** | 670 VN + 297 legal | parsing, OCR, retrieval | bất kỳ verdict nào |
| **L1 PARSED** | 19.512 units · 15.658 chunks · 938 clauses | retrieval, clause matching | dùng clause mà bỏ qua hiệu lực/phạm vi |
| **L2 CANDIDATE** | 7.960 claim · 3.786 evidence | phát triển extraction, sampling | coi mọi candidate là claim thật |
| **L3 CURATED** | 5.028 clean · 3.682 priority | hàng đợi annotation | nhãn gold — **lọc không phải adjudication** |
| **L4 ADJUDICATED** | 4 claim + 8 evidence + 1 review | sanity test, demo regression | bất kỳ phát biểu thống kê nào |
| **L5 GOLD** | 0 | chỉ để báo cáo cuối | tinh chỉnh prompt/rule/model — vĩnh viễn |

`legal_cases` (297) và `legal_clauses` (938) chạy **song song** như policy/case
knowledge corpus, không trộn vào L4/L5.

---

## 3. Nút thắt: supervision, không phải volume

Kế hoạch MVP đặt 150–300 tài liệu và 1.000–3.000 claim candidate.
Thực tế: **670 tài liệu, 7.960 candidate** — vượt xa.

Nhưng **tỉ lệ supervision là 0,06%**.

```
670 docs      → không còn thiếu volume
21 companies  → còn thiếu diversity  (32 tài liệu/doanh nghiệp: deep, chưa broad)
7.960 claims  → extraction corpus đã đủ
297 + 938     → policy retrieval đã có nền
5 adjudicated → evaluation corpus vẫn là bottleneck
```

Crawl thêm tài liệu **sẽ không làm dịch chuyển bất kỳ metric nào** cho tới khi
số claim đã adjudicate đạt ~100–200.

---

## 4. Company-held-out split

Random split theo claim bị leak: claim 2024 của doanh nghiệp A ở test trong khi
báo cáo 2023 và 2025 của chính A ở train — retriever đã biết từ vựng, tên KPI và
văn phong của issuer đó.

**Thứ tự đúng: giữ lại theo doanh nghiệp trước, rồi mới chia theo thời gian
trong phần train.**

Kết quả (`data/crawl/vn30/curated/company_split.json`):

| | |
| --- | --- |
| claims | 3.682 / 15 doanh nghiệp |
| held-out | `pan, pow, ctg, mwg, cdn, vcs, cng` (7) |
| test share | 19,9% |
| train | 8 doanh nghiệp |

Heuristic ban đầu chọn *nhỏ trước* và cho ra 11/15 doanh nghiệp ở test mà chỉ
đạt 19,2% claim — đúng tỉ lệ nhưng bóp nghẹt diversity của train. Đã đổi sang
*lớn-vừa-đủ trước*: cùng tỉ lệ, chỉ 7 doanh nghiệp.

**Cảnh báo phải giữ:** 15 doanh nghiệp, riêng `tra` chiếm 29,8% claim. Khoảng tin
cậy cho khả năng generalize sẽ rất rộng. **Báo cáo kết quả theo từng doanh
nghiệp**, không gộp thành một con số generalisation duy nhất.

---

## 5. Việc tiếp theo

1. **Adjudicate 100–200 claim thật**, cố ý phủ đủ: `Supported`,
   `Partially supported`, `Contradicted`, `Unsupported`, `Insufficient evidence`,
   và các lỗi `missing baseline`, `scope mismatch`, `numeric contradiction`,
   `omission`, `legal/taxonomy mismatch`, `use-of-proceeds mismatch`.
   Công cụ đã sẵn: reviewer workflow ghi thẳng vào L4.
2. **Cho phép nhiều evidence đúng cho một claim.** Annotation không được ép mỗi
   claim có đúng một đoạn đáp án — gold evidence do người gán thường không phủ
   hết đoạn thực sự liên quan, khiến precision trông thấp giả tạo.
3. **Đóng băng L5** sau khi có ~300–500 cặp: company-held-out, không bao giờ
   dùng để chỉnh prompt/rule/model.
4. **Mở rộng diversity** lên 40–60 doanh nghiệp — ưu tiên hơn việc thêm tài liệu
   cho 21 doanh nghiệp hiện có.
5. **Sửa SQLite contention ở tầng ingestion** (single-writer queue / staged
   merge) thay vì tiếp tục sinh thêm corpus root.
