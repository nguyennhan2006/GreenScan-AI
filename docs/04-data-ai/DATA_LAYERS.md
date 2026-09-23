# Ba tầng dữ liệu: raw · clean · extract

**Phiên bản contract:** `data-layers-v1` · **Ngày:** 2026-09-23 · **Nguồn sự thật:** [`src/quantum_gw/data/layers.py`](../../src/quantum_gw/data/layers.py) (pydantic) → JSON Schema sinh ra ở [`schemas/data/`](../../schemas/data/)
**Áp cho hai nơi sinh dữ liệu:** corpus (crawl, case pack) và runtime (mỗi lần chạy pipeline). Một hình dạng bản ghi cho mỗi tầng, không có hai định nghĩa "chunk".

> Trước bản này, cùng một thứ có hai tên: `document_id`/`doc_id`, `unit_id`/`chunk_id`, `publication_year`/`period`. Không thể viết một Dataset Card từ hai bộ tên.

## 1. Ba tầng là gì

| Tầng | Một bản ghi = | Sinh ra khi | Không bao giờ sửa sau khi ghi |
| --- | --- | --- | --- |
| **raw** | một tài liệu nguồn đã thu được | crawl tải xong, hoặc người dùng nạp tài liệu vào một run | ✅ (bytes đã có SHA-256) |
| **clean** | một đơn vị văn bản sau parse/OCR/chuẩn hoá/khử trùng lặp — đoạn, bảng, tiêu đề | parser chạy | ghi lại khi đổi parser, kèm `producer_version` |
| **extract** | một đối tượng đọc ra từ đơn vị clean: claim, evidence candidate, numeric fact — **và câu bị loại kèm lý do** | extractor chạy | ghi lại khi đổi extractor |

Trường `origin` (`corpus` \| `run`) là thứ duy nhất quyết định trường nào được phép thiếu: một PDF crawl về phải có URL và ngày truy cập; một tệp người dùng tải lên trong một run thì không.

## 2. Ba nguyên tắc bất biến

1. **Provenance bắt buộc.** `clean.doc_id` → `raw.doc_id`; `extract.unit_id` → `clean.unit_id`. Mọi bản ghi mang `sha256` (raw) hoặc `text_sha256` (clean/extract) của chính nội dung nó. Một claim luôn truy được về một tệp reviewer mở được.
2. **Không loại bỏ âm thầm.** Câu bị extractor từ chối trở thành một dòng `extract` với `rejected_reason` (`caps_run`, `table_row`, `chunk_boundary_fragment`, `generic_without_commitment`, …). "Hệ thống đã bỏ qua cái gì" là câu hỏi của reviewer và là một thống kê của dataset.
3. **Phiên bản đi cùng dữ liệu.** Mọi dòng có `producer` + `producer_version`; numeric fact có `policy_id`. Hai dòng do hai phiên bản code sinh ra không bao giờ bị so như cùng một phép đo.

## 3. Trường theo tầng

### 3.1 raw — 40 trường

| Nhóm | Trường |
| --- | --- |
| Định danh, toàn vẹn | `doc_id`, `sha256`, `contract_version`, `origin`, `producer`, `producer_version`, `produced_at`, `run_id` |
| Nguồn gốc | `url`, `final_url`, `source_page_url`, `source_authority`, `retrieved_by`, `access_date`, `licence_note` |
| Đơn vị công bố | `organization_name`, `company_id`, `ticker`, `exchange`, `jurisdiction`, `sector` |
| Nội dung là gì | `title`, `document_type`, `reporting_year`, `publication_date`, `language` |
| Tệp | `file_name`, `media_type`, `byte_size`, `page_count`, `object_path`, `native_text_chars`, `scan_like_ratio` |
| Pipeline được phép dùng thế nào | `role` (claim_source/evidence/reference), `source_type` (internal/financial/environmental/legal/external/standard) |
| Trạng thái | `status`, `error_message`, `notes`, `metadata` |

`source_authority` mã hoá thứ bậc bằng chứng của `COLLECTION_PLAN_v2` §2.2: `government` → `court_or_regulator` → `auditor` → `assurance_provider` → `exchange` → `company` → `press`.

### 3.2 clean — 33 trường

| Nhóm | Trường |
| --- | --- |
| Định danh + liên kết ngược | `unit_id`, `doc_id`, `doc_sha256`, `source_name` |
| Nội dung | `text`, `text_sha256`, `char_count`, `language` |
| Vị trí trong tài liệu | `page`, `block_index`, `unit_type`, `is_table`, `table_index`, `row_index`, `column_index` |
| Cách tạo ra | `used_ocr`, `ocr_confidence`, `normalizations` (nfkc · join_wrapped_lines · whitespace) |
| Dataset | `duplicate_of`, `split` (train/dev/test/holdout/review/unassigned), `company_id`, `reporting_year` |
| Chất lượng | `quality_flags` (`low_text`, `scan_like`, `suspicious_instruction`, `table_parse_low_confidence`, `ocr_used`) |

`row_index`/`column_index` đã có chỗ nhưng **luôn null** cho tới khi làm trích dẫn tới ô bảng (E3) — trường tồn tại để không phải đổi schema, không phải để tuyên bố đã có.

### 3.3 extract — 36 trường

| Nhóm | Trường |
| --- | --- |
| Định danh + liên kết ngược | `extract_id`, `extract_type` (claim/rejected_sentence/evidence_candidate/numeric_fact), `unit_id`, `doc_id`, `page`, `sentence_index` |
| Nội dung | `text`, `text_sha256`, `language` |
| Năm thuộc tính rubric + những gì extractor đọc được | `claim_type`, `metric`, `direction`, `values`, `units`, `period`, `baseline`, `scope`, `is_future_commitment`, `is_vague`, `vague_terms_matched`, `confidence` |
| Vì sao **không** thành claim | `rejected_reason` |
| Numeric facts | `numeric_facts[]`: `value`, `unit`, `half_precision`, `basis`, `boundary`, `technology`, `variant[]`, `scopes[]`, `is_target`, `policy_id` |
| Ứng viên | `has_number`, `candidate_type` |
| Nhãn người | `label`, `annotator`, `adjudicated_at` |

`numeric_facts` dùng **đúng** code mà verifier dùng để quyết định hai số có được so hay không (`verification/numeric_facts.py`, N1/RQ2). Một con số trong dataset và một con số trong verdict là cùng một đối tượng, cùng `policy_id`.

## 4. Trường bắt buộc theo `origin`

| Tầng | corpus | run |
| --- | --- | --- |
| raw | `sha256`, `access_date`, `source_authority`, `document_type`, `object_path` | `sha256`, `document_type` |
| clean | `doc_id`, `text_sha256`, `split` | `doc_id`, `text_sha256` |
| extract | `unit_id`, `doc_id`, `text_sha256` | `unit_id`, `doc_id`, `text_sha256` |

Validator tách hai loại lỗi và **chỉ** loại đầu làm CI đỏ:

- **invalid** — dòng không khớp contract (sai kiểu, thừa trường, thiếu trường model bắt buộc): lỗi của phía ghi dữ liệu.
- **incomplete** — dòng khớp contract nhưng thiếu trường mà `origin` của nó cần để dùng được: **khoảng trống dữ liệu**, sửa bằng thu thập chứ không bằng code.

## 5. Lệnh

```bash
python tools/data_contract.py schema                    # sinh schemas/data/*.schema.json từ pydantic
python tools/data_contract.py validate-run              # kiểm tra layer của run mới nhất
python tools/data_contract.py validate <file|dir>
python tools/data_contract.py migrate-crawl             # data/crawl/vn30/contract/ (~15 giây)
python tools/data_contract.py report <dir>              # độ phủ từng trường
```

Mỗi lần chạy pipeline tự ghi `\.quantum/runs/<run_id>/contract/{raw,clean,extract}.jsonl` (orchestrator → `data/export.py`). Thư mục `data/crawl/**/contract/` là **dữ liệu dẫn xuất**, không commit — dựng lại trong ~15 giây.

## 6. Số đo đầu tiên (2026-09-23)

Toàn bộ corpus VN30 chuyển sang contract, **0 dòng invalid**:

| Tầng | Dòng | Khoảng trống đo được |
| --- | ---: | --- |
| raw | 1.061 | `object_path` thiếu **391 (37%)** — bản ghi tải lỗi/trùng vẫn giữ để truy vết |
| clean | 15.658 | `split` chưa gán **4.469 (29%)**; `page` **0%** — corpus cũ không giữ số trang |
| extract | 11.746 | — (7.960 claim candidate + 3.786 evidence candidate) |

Hai con số này là việc phải làm, không phải lỗi code:

1. **`page` 0% ở corpus** — runtime có trang cho mọi đoạn, corpus crawl thì không. Mọi cặp gold lấy từ corpus hiện **không** trích dẫn được tới trang. Đợt thu thập v2 phải giữ `page` ngay từ bước chuẩn hoá.
2. **`split` 29% chưa gán** — đúng số tài liệu chưa xác định năm (`review` split trong `data/crawl/README.md`). Không được mặc định coi là `train`.

## 7. Bản cho người không chuyên kỹ thuật

[`GreenScan_Mo_ta_truong_du_lieu_v1.pdf`](GreenScan_Mo_ta_truong_du_lieu_v1.pdf) — 10 trang, tiếng Việt, giải thích từng trường bằng ngôn ngữ thông thường kèm ví dụ thật, dùng để gửi khách hàng / kiểm toán viên / thành viên nghiệp vụ. Dựng lại bằng `python tools/make_data_fields_pdf.py` (cần `pip install -e ".[docs]"`). **Khi contract đổi, sửa cả hai tài liệu cùng lúc** — script có kiểm tra ký tự thiếu glyph nên sẽ báo lỗi thay vì in ra ô vuông.

## 8. Liên quan

[DATA_SCHEMA.md](DATA_SCHEMA.md) (object nghiệp vụ tầng trên: Claim, Evidence, Verification, Score) · [DATA_CONTRACTS.md](DATA_CONTRACTS.md) · [../../data/COLLECTION_PLAN_v2.md](../../data/COLLECTION_PLAN_v2.md) · [../../data/gold/LABELING_CONVENTIONS.md](../../data/gold/LABELING_CONVENTIONS.md) · [../00-project/RESEARCH_PROGRAM_2026-09-22.md](../00-project/RESEARCH_PROGRAM_2026-09-22.md) (RQ2 numeric fact schema)
