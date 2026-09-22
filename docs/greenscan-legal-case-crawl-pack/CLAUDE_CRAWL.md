# CLAUDE_CRAWL.md — Non-negotiable instructions

Bạn đang mở rộng dữ liệu GreenScan AI. Ưu tiên **đúng nguồn, provenance, khả năng tái lập và label integrity** hơn số lượng file.

## 1. Không được thay đổi định nghĩa nhãn

Các mệnh đề sau luôn đúng:

```text
company_has_case = true
!= document_is_greenwashing = true
!= claim_is_greenwashing = true
```

- Raw PDF/HTML/XML chỉ là **source document**.
- Candidate claim chỉ là **candidate**, không phải gold label.
- Thiếu evidence không đồng nghĩa vi phạm.
- Chỉ representation nằm trong phạm vi order/ruling/judgment mới nhận legal ground-truth tương ứng.
- Với SEC settlement, giữ `without_admitting_or_denying` khi nguồn nói như vậy.
- Với ASIC infringement notices, giữ `payment_not_admission`.
- Với ASA, lưu `UPHELD`, `NOT_UPHELD` theo từng issue nếu ruling mixed; không đổi thành “court-proven fraud”.

## 2. Cửa sổ dữ liệu

Corporate/fund disclosure target: **2021–2025 inclusive**.

Case pháp lý có thể xảy ra ngoài cửa sổ này (ví dụ ASA 2026). Vẫn lưu case pack nhưng **không tự động mở rộng corporate benchmark sang 2026**. Nếu cần 2026 cho case evidence, lưu trong `case_artifacts/` và đánh `outside_corporate_window=true`.

## 3. URL policy

Mỗi target phải bắt đầu từ `config/legal_case_targets.yaml`:

1. `case_url`: bắt buộc, authority domain.
2. `report_urls`: official company/fund seeds.
3. Không đoán direct-PDF URL theo pattern nếu chưa discover từ official page.
4. Không dùng search-result snippets làm source artifact.
5. Third-party mirror chỉ được dùng để **tìm đường về nguồn chính thức**, không làm corpus chính nếu official source có thể lấy được.

## 4. Crawl behavior

- Set `User-Agent`, `Accept`, `Accept-Language` hợp lý; SEC phải có contact-identifiable User-Agent theo chính sách của họ nếu codebase đã hỗ trợ.
- Rate limit theo domain, exponential backoff, jitter.
- Tôn trọng robots rules khi tải được robots.txt.
- Theo regression policy hiện tại: robots 4xx không được silently biến thành toàn-domain disallow; 5xx/transport failure phải fail-safe và đưa vào review queue.
- Không `verify=False` cho TLS.
- Local Avast/proxy shim chỉ dùng khi opt-in `GREENSCAN_TRUST_LOCAL_PROXY=1`; không production.
- Filter asset links (`.js`, `.css`, fonts, icons, favicons, tracking URLs, images không phải challenged ad artifact).
- Có hard cap theo target + pagination stop criteria để một entity không chiếm toàn bộ run.
- URL canonicalization + SHA-256 dedup.
- JSONL reader dùng `split("\n")`, không `splitlines()`; writer escape U+2028, U+2029, U+0085.

## 5. Year resolution

Không tin filename một cách tuyệt đối. Resolution order:

1. metadata/title/date trên official listing;
2. cover/title page hoặc reporting-period text trong PDF/HTML;
3. document metadata;
4. URL/filename;
5. nếu conflict -> `year_status=review`.

Không để file chưa biết năm âm thầm vào train/dev/test.

## 6. Entity mapping

Bắt buộc lưu cả:

- `case_entity`
- `reporting_entity`
- `brand`
- `relationship`
- `relationship_effective_date` nếu biết

Ví dụ Nike Retail B.V. != NIKE, Inc.; Calvin Klein Europe B.V. != PVH Corp.; Active Super có merger boundary.

## 7. Definition of done cho mỗi target

Target chỉ là `COLLECTED` khi:

- authority case landing page đã lưu;
- tất cả attachment/order/ruling chính trên case page đã crawl hoặc có reason code;
- challenged representation/artifact đã lưu nếu authority cung cấp;
- 2021–2025 disclosure đã được attempt theo `profile`;
- mỗi năm có status (`collected`, `integrated`, `not_published`, `not_found_after_exhaustive_official_search`, `blocked`, `not_applicable`);
- checksum + provenance + content type + file size + HTTP metadata có đủ;
- duplicate/leakage checks chạy xong.

Số lượng file không phải Definition of Done.

## 8. Báo cáo bắt buộc

Mỗi run tạo:

- `reports/COLLECTION_REPORT_<YYYY-MM-DD>.md`
- `reports/coverage_matrix.csv`
- `reports/failure_queue.csv`
- `reports/leakage_report.json`
- `reports/source_health.json`

Không exit code 0 nếu toàn bộ run tạo 0 tài liệu mà không có `explicit_no_new_documents=true` và lý do được log.
