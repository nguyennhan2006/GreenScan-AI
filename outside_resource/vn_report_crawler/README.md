# VN Report Crawler

> **Trạng thái: tài nguyên thử nghiệm bên ngoài (`outside_resource/`).**
> Chưa tích hợp vào hệ thống GreenScan.
>
> Đã kiểm chứng với site thật (2026-07-29): `hoaphat` và `vinamilk` chạy được,
> 78 tài liệu, 93% phân loại được. **Vietstock, CafeF và HNX render bằng
> JavaScript nên adapter HTML không dùng được**; Vingroup trả HTTP 403.
> Xem [SPRINT2_FINDINGS.md](SPRINT2_FINDINGS.md).

Thu thập báo cáo tài chính, thường niên, phát triển bền vững/ESG, quản trị và
tài liệu công bố của doanh nghiệp Việt Nam.

## Nguyên tắc vận hành

1. Tôn trọng `robots.txt`, điều khoản sử dụng và bản quyền.
2. Không vượt CAPTCHA, đăng nhập, paywall hay cơ chế chống bot.
3. Giới hạn tốc độ, khử trùng lặp, không tải lại file đã có.
4. Lưu URL nguồn, thời gian thu thập, SHA-256 và HTTP metadata.
5. Ưu tiên website chính thức của doanh nghiệp và sở giao dịch.
6. **FiinPro-X: không crawl.** Là sản phẩm thương mại, chỉ dùng qua API/license.

## Kiến trúc

Adapter chịu trách nhiệm "site này tổ chức tài liệu ra sao". Mọi thứ dùng chung
nằm ở shared pipeline và adapter không được tự làm lại.

```text
Source adapter                      Shared pipeline
 ├── discover_pages()                ├── robots / ToS policy
 ├── parse_listing()        ──────►  ├── rate limiter
 ├── resolve_attachment()            ├── MIME validation
 └── normalize_metadata()            ├── checksum + dedupe
                                     ├── provenance
                                     ├── storage (CAS + SQLite)
                                     └── manifest JSONL
```

```text
crawler/
├── adapters/     base, generic_html, vietstock, cafef
├── discovery/    html_links, download_resolver
├── policies/     robots, rate_limit
├── pipeline/     downloader, validator, classifier, deduplicator, manifest
├── storage/      object_store, database
└── engine.py     điều phối BFS + gọi pipeline
```

Sprint 3–5 sẽ bổ sung `stockbiz`, `money24h`, `hnx`, `vlca`.

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Chạy

```bash
# Dry-run: chỉ phát hiện, không tải file. Chạy được cả nguồn enabled: false.
python -m crawler.cli --config configs/aggregators.yml --dry-run

# Chạy thật (chỉ nguồn enabled: true)
python -m crawler.cli --config configs/official_companies.yml

# Giới hạn khi hiệu chỉnh adapter mới
python -m crawler.cli --config configs/aggregators.yml \
    --source vietstock --include-disabled --max-documents 50
```

| Cờ | Ý nghĩa |
|---|---|
| `--dry-run` | Chỉ ghi discovery + manifest, không tải bytes |
| `--source ID` | Chỉ chạy nguồn này (lặp được nhiều lần) |
| `--include-disabled` | Chạy cả nguồn `enabled: false` |
| `--max-documents N` | Trần số tài liệu mỗi nguồn |

## Dữ liệu đầu ra

Object (bytes) tách khỏi document (bản ghi logic). Nhiều document có thể tham
chiếu cùng một object mà vẫn giữ nguyên provenance riêng.

```text
data/
├── objects/sha256/64/6435ccb2...aee1.pdf      # content-addressed, 1 bytes = 1 file
├── documents/<source>/<ticker>/<year>/<type>-<hash>.json
├── manifests/crawl-YYYYMMDD-HHMMSS.jsonl      # nhật ký từng lần chạy
└── metadata.sqlite3                            # bảng objects + documents
```

`crawl_status` trong bảng `documents`:

```text
discovered  downloaded  duplicate  not_found  forbidden
robots_denied  temporary_error  invalid_document  unsupported_type
```

`canonical_document_id` là thuộc tính của **nhóm** cùng object, được tính lại
cho toàn nhóm mỗi khi có tài liệu mới (authority cao nhất → phát hiện sớm nhất
→ document_id nhỏ nhất). Bước indexing nên lấy canonical thay vì mọi bản mirror.

## Thêm nguồn mới

YAML chỉ giữ **policy và điểm vào**. Selector chi tiết nằm trong adapter hoặc
`adapter_options`, không nhồi vào schema chung.

```yaml
defaults:
  enabled: false
  authority: aggregator          # official_exchange | official_company | aggregator | mirror
  delay_seconds: 3
  max_requests_per_minute: 15
  robots_policy:
    on_missing: allow            # allow | deny
    on_temporary_error: retry_then_skip   # allow | skip_source | retry_then_skip

sources:
  - id: example
    adapter: generic_html
    company: Example JSC
    ticker: EXM
    start_urls: [https://example.com/investor/reports]
    allowed_domains: [example.com]
    allowed_file_types: [pdf, docx, xlsx]
    attachment_patterns: ["/Handlers/DownloadAttachedFile.ashx"]
    adapter_options: {}
```

Cấu hình sai schema bị từ chối ngay khi nạp (pydantic `extra="forbid"`), kèm
tên nguồn và trường lỗi — không nổ `TypeError` giữa lúc crawl.

### Checklist trước khi bật `enabled: true`

1. Kiểm tra `robots.txt`
2. Kiểm tra điều khoản sử dụng
3. Xác định endpoint ổn định
4. Lưu HTML thật vào fixture và chỉnh selector
5. `pytest tests/ -k <adapter>`
6. Dry-run 20–50 tài liệu
7. Xem tỷ lệ lỗi và duplicate trong manifest
8. Bật production

## Nhận diện attachment

Không chỉ dựa vào đuôi URL. Thứ tự ưu tiên: magic bytes → `Content-Type` →
`Content-Disposition`. DOCX/XLSX được phân biệt bằng entry trong ZIP container.

Xử lý được các dạng:

```text
/report.pdf                                    đuôi trực tiếp
/download?file=report.pdf                      query-string
/Handlers/DownloadFinancialStatement.ashx?FileName=...   download handler
/Handlers/DownloadAttachedFile.ashx?NewsID=99  handler không lộ tên file
302 → /files/real.pdf                          redirect
<iframe src="/files/real.pdf">                 trang xem trước
```

Website render bằng JavaScript cần adapter Playwright riêng; không bật browser
automation cho toàn bộ nguồn.

## Kiểm thử

```bash
pytest          # 95 test, chạy hoàn toàn offline qua httpx.MockTransport
ruff check crawler/ tests/ scripts/

python scripts/refresh_fixtures.py    # tải lại HTML thật (cần mạng)
```

Không cần mạng, không cần server phụ, không cần `respx`. Một phần test chạy trên
HTML **thật** lưu sẵn ở `tests/fixtures/` (Vietstock, CafeF, Hòa Phát, Vinamilk).

> **Lưu ý:** `vietstock.py` và `cafef.py` chưa dùng được — hai site render listing
> bằng JavaScript. Test của chúng xác nhận *logic* adapter đúng trên fixture tự
> dựng, không phải chúng chạy được với site thật.

## Chất lượng dữ liệu

Sau khi crawl nên chạy tiếp:

1. Trích xuất bằng Docling/PaddleOCR.
2. Phát hiện text layer / scan, đếm trang, nhận diện bố cục.
3. Lưu provenance đến trang, bảng và ô dữ liệu.
4. Chọn mẫu theo quota loại tài liệu, kiểu trình bày và ngành — quan trọng hơn
   việc tải hàng chục nghìn BCTC có cấu trúc gần giống nhau.
5. Hợp nhất duplicate và chọn canonical source **trước** khi đưa vào index RAG.
   Thêm nhiều tài liệu có thể tăng recall nhưng cũng đưa thêm nhiễu và làm giảm
   độ chính xác.
