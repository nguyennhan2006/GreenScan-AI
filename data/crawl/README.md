# `data/crawl/` — corpus thu thập tự động

Vùng thứ tư của `data/`, bên cạnh `sample/`, `golden/` và `real_cases/`.
Đây là corpus **đầu vào thô** cho pipeline: báo cáo thường niên, báo cáo phát
triển bền vững, báo cáo tài chính và báo cáo quản trị của doanh nghiệp Việt Nam,
thu thập từ website chính thức.

| Vùng | Vai trò |
| --- | --- |
| `sample/` | Demo tổng hợp, chạy được ngay |
| `golden/` | Acceptance-test cho CI |
| `real_cases/` | 4 case đã có phán quyết + 2 control Việt Nam, có nhãn |
| **`crawl/`** | **Corpus thô chưa gán nhãn, dùng để index/retrieval và làm nguồn gán nhãn tiếp** |

## Kết quả lần chạy 2026-08-07

| Chỉ số | Giá trị |
| --- | ---: |
| Tài liệu tải được | **670** (644 downloaded + 26 duplicate) |
| Doanh nghiệp có tài liệu | **21 / 30** |
| Dung lượng file gốc | 3,9 GB (không commit) |
| Bản ghi trong `documents.jsonl` | 1 061 (gồm cả bản ghi lỗi — giữ để truy vết) |
| `units.jsonl` | 19 512 |
| `chunks.jsonl` | 15 658 |
| `claim_candidates.jsonl` | **7 960** |
| `evidence_candidates.jsonl` | **3 786** |
| `annotation_pairs.jsonl` | 39 592 |
| Company-year rows | 105 (5 đủ bộ chứng cứ lõi) |
| Cross-split duplicate | 1 (xem `leakage_report.json`) |

Phân bố loại tài liệu:

```text
financial_statement 284   annual_report        51
agm_document        177   sustainability_report 41
other                85   governance_report     29
                          regulatory_record      2
                          integrated_report      1
```

Báo cáo PTBV/tích hợp — nhóm giá trị nhất cho bài toán — có **42 bản** ở 9 doanh
nghiệp: pan 11, tra 10, fmc 4, dhg 4, cng 4, pnj 3, bvh 3, sab 2, ctd 1.

Phân bố theo năm: 2021 – 22, 2022 – 46, 2023 – 63, 2024 – 165, 2025 – 178,
không xác định năm – 196. Số tài liệu năm cũ ít hơn hẳn: website IR thường chỉ
giữ vài năm gần nhất.

**9 doanh nghiệp chưa có tài liệu nào:** acg, bmp, chp, dmc, nt2, ocb, qns, tlg,
tng. Lý do đã ghi nhận: `nt2` không kết nối được, `qns` trả HTTP 403, `chp`
không tìm được trang IR nào còn sống; số còn lại render bằng JavaScript theo
kiểu mà `harvest_js_listings.py` chưa bóc được. Đây là danh sách việc tiếp theo,
không phải kết luận rằng doanh nghiệp không công bố.

## Bố cục

```text
data/crawl/
├── vn30/
│   ├── raw/                      # KHÔNG commit (xem .gitignore)
│   │   ├── objects/sha256/       # bytes gốc, content-addressed
│   │   ├── manifests/*.jsonl     # nhật ký từng lần chạy
│   │   └── metadata.sqlite3      # bảng documents
│   ├── normalized/               # commit — đây là dataset thật sự
│   │   ├── documents.jsonl
│   │   ├── units.jsonl
│   │   ├── chunks.jsonl
│   │   ├── claim_candidates.jsonl
│   │   ├── evidence_candidates.jsonl
│   │   ├── annotation_pairs.jsonl
│   │   ├── document_sustainability_signals.json
│   │   └── leakage_report.json
│   └── coverage/
│       ├── coverage_company_year.csv
│       └── coverage_company_summary.csv
└── logs/                         # log của các lần crawl
```

**Bytes gốc không được commit.** Đây là tài liệu có bản quyền của bên thứ ba;
repo chỉ giữ metadata + SHA-256 để tái lập. Chạy lại crawl để có bytes.

## Chia tập theo thời gian

| Năm | Split |
| --- | --- |
| 2021–2022 | train |
| 2023 | dev |
| 2024 | test |
| 2025 | future holdout |

Năm không xác định được rơi vào split `review` — phải gán năm thủ công trước khi
dùng, **không** mặc định coi là train.

`leakage_report.json` liệt kê file trùng SHA-256 xuất hiện ở nhiều split — phải
xử lý **trước** khi gán nhãn. Lần chạy 2026-08-07 có **1** trường hợp
(`review` + `train`): cùng một file được công bố hai lần với metadata năm khác
nhau. Chọn một split rồi loại bản còn lại.

## Tái lập

Crawler nằm ở `outside_resource/greenscan_vn30_dataset_crawler_2021_2025/`
(chưa tích hợp vào package chính). Từ thư mục đó:

```bash
# 0. Máy có proxy chặn TLS (Avast/AV doanh nghiệp) thì bật shim tin cậy.
#    Shim KHÔNG tắt xác thực chứng chỉ — xem tools/local_proxy_tls/sitecustomize.py
export PYTHONPATH=<repo>/tools/local_proxy_tls
export GREENSCAN_TRUST_LOCAL_PROXY=1

# 1. Kiểm tra URL và host CDN trước khi crawl (bắt buộc — xem phần Bẫy bên dưới)
python scripts/discover_ir_urls.py --only-broken
python scripts/probe_attachment_hosts.py

# 2. Crawl HTML tĩnh
python -m crawler.cli --config configs/companies.yml --source official \
    --data-root <repo>/data/crawl/vn30/raw \
    --max-depth 2 --delay 1.0 --requests-per-minute 45

# 3. Các site render bằng JavaScript
python scripts/harvest_js_listings.py --company bid --company pan \
    --data-root <repo>/data/crawl/vn30/raw

# 4. Chuẩn hoá + coverage
python -m dataset.cli build \
    --database <repo>/data/crawl/vn30/raw/metadata.sqlite3 \
    --output <repo>/data/crawl/vn30/normalized
python -m dataset.cli coverage \
    --database <repo>/data/crawl/vn30/raw/metadata.sqlite3 \
    --signals <repo>/data/crawl/vn30/normalized/document_sustainability_signals.json \
    --output <repo>/data/crawl/vn30/coverage
```

## Bẫy đã gặp — đọc trước khi sửa config

**1. `attachment_domains` rỗng = crawl xong với 0 tài liệu, không báo lỗi.**
Site IR Việt Nam gần như luôn để HTML trên domain công ty và PDF trên CDN riêng
(`d8um25gjecm9v.cloudfront.net` cho Vinamilk, `cdn.pnj.io` cho PNJ,
`stsbcwebsitemedia.blob.core.windows.net` cho Sabeco). `allowed_host()` kiểm tra
`official_domains + attachment_domains`; thiếu CDN thì mọi PDF bị loại vì sai
host và crawler kết thúc "thành công" với tay trắng. Chạy
`probe_attachment_hosts.py` trước mỗi lần đổi config.

**2. URL trong config có thể là URL đoán, không phải URL thật.**
Rà 30 công ty ngày 2026-08-07: 11 URL trả 404 — dấu hiệu của việc suy ra theo
mẫu `https://<domain>/quan-he-co-dong/`. `discover_ir_urls.py` đi từ trang chủ
và chỉ ghi lại URL đã xác nhận HTTP 200.

**3. Link asset bị xếp là "liên quan".**
`relevant()` chấm điểm trên text xung quanh link, nên `jquery.js` nằm trong trang
báo cáo thường niên vẫn đạt điểm cao và bị đưa vào hàng đợi. Trước khi lọc theo
đuôi file, một lần crawl Vinamilk tiêu gần hết ngân sách vào `aos.js`,
`main.js`, `favicon.ico` (28 giây → hơn 10 phút). Lọc theo đuôi file, không theo
text: `crawler/utils.py: is_page_asset()`.

**4. Trang render bằng JavaScript trả HTTP 200 và 0 link tài liệu.**
Đổi URL không sửa được. Dùng `harvest_js_listings.py` (Chromium) — kết quả ghi
vào cùng `metadata.sqlite3` với cùng schema, `dataset build` không cần biết
khác biệt. Riêng BIDV: static crawl thấy 0 tài liệu, render xong thấy 15.

**5. `robots.txt` trả 403 bị hiểu là cấm.**
S3/CloudFront trả 403 cho `/robots.txt` khi object đó không tồn tại — đó không
phải lệnh cấm. Code cũ map mọi mã khác 404 thành lỗi rồi áp `robots_on_error:
skip`, làm **177 PDF công khai** bị loại im lặng. RFC 9309 §2.3.1: 4xx là
"unavailable" → không có ràng buộc; chỉ 5xx và lỗi tầng vận chuyển mới là
"unreachable" → mới nên coi như cấm toàn bộ. Xem `tests/test_robots.py`.

**6. Một site lớn nuốt trọn ngân sách crawl.**
Coteccons kéo 162 tài liệu trong khi 24 doanh nghiệp khác chưa được chạm tới.
Dùng `--max-documents` để đặt trần cho mỗi doanh nghiệp.

## Giới hạn pháp lý và đạo đức

- Tôn trọng `robots.txt`, rate limit, điều khoản sử dụng.
- Không vượt CAPTCHA, đăng nhập, paywall hay cơ chế chống bot. Site chặn thì
  để nguyên trạng thái bị chặn và ghi lại lý do.
- **FiinPro-X không crawl** — sản phẩm thương mại, chỉ dùng qua license.
- Tài liệu thu thập được **không** phải bằng chứng greenwashing. Chúng là văn
  bản thô. Thiếu dữ liệu không bao giờ được tự động quy thành nhãn vi phạm.
