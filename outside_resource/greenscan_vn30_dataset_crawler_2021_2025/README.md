# GreenScan VN30 Dataset Crawler — 2021–2025

Đây là bộ thay thế đúng mục tiêu cho crawler Saudi trước đó. Bộ này chỉ làm việc với **30 doanh nghiệp Việt Nam đã chọn từ danh sách CSI 2024**, trong giai đoạn **2021–2025**, để tạo corpus huấn luyện, đánh giá và testcase về claim–evidence/greenwashing.

## Điều có thể và không thể cam kết

Bộ code có thể tự động:
- đi từ kho IR chính thức của từng doanh nghiệp;
- đọc sitemap và trang danh sách;
- thu thập bản mirror/tài liệu từ CafeF;
- thu thập trang HNX cho mã HNX/UPCoM;
- nhận diện PDF/DOCX/XLSX dù URL không có đuôi file;
- lọc năm 2021–2025 và phân loại loại báo cáo;
- SHA-256 deduplicate và giữ provenance;
- tạo coverage report, claim/evidence candidates và testcase template.

Không thể hứa trước rằng cả 30 công ty đều có **mọi loại tài liệu** cho cả 5 năm. Một số doanh nghiệp không phát hành báo cáo PTBV riêng; khi đó pipeline cho phép chương ESG đủ sâu trong BCTN/báo cáo tích hợp thay thế. URL, robots.txt, JavaScript và cơ chế tải file cũng có thể thay đổi. Coverage report là cổng kiểm soát cuối cùng.

## 30 doanh nghiệp

Danh sách nằm ở `configs/companies.yml`. Gồm VNM, PNJ, BID, CTG, BVH, CTD, SAB, PAN, DHG, TRA, TNG, VCS, BMP, MSR, POW, NT2, QNS, HDB, MWG, TLG, ACG, PHR, DPR, FMC, CNG, CHP, OCB, DGW, CDN và DMC.

## Bộ chứng cứ cốt lõi cho mỗi công ty–năm

1. BCTN hoặc báo cáo tích hợp.
2. BCTC năm đã kiểm toán, ưu tiên hợp nhất.
3. Báo cáo quản trị cả năm.
4. Báo cáo PTBV/ESG riêng **hoặc** chương ESG đủ sâu trong BCTN/báo cáo tích hợp.

Bản mirror hoặc công bố sàn là provenance bổ sung, không thay thế bản chính thức khi bản chính thức tồn tại.

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Chạy một công ty trước

```bash
greenscan-vn-crawl --company vnm --source official --data-root data/raw --dry-run
greenscan-vn-crawl --company vnm --source official --data-root data/raw
greenscan-vn-crawl --company vnm --source cafef --data-root data/raw
```

Với mã HNX/UPCoM:

```bash
greenscan-vn-crawl --company cdn --source hnx --data-root data/raw
```

Chạy toàn bộ 30 công ty chỉ sau khi kiểm tra từng batch:

```bash
python scripts/run_batches.py --batch-size 5 --source all
```

## Xây dataset

```bash
greenscan-vn-dataset build --database data/raw/metadata.sqlite3 --output data/normalized
greenscan-vn-dataset coverage --database data/raw/metadata.sqlite3 --signals data/normalized/document_sustainability_signals.json --output outputs/coverage
greenscan-vn-dataset testcase-template --output examples/testcases.jsonl
```

Đầu ra:

```text
data/normalized/
├── documents.jsonl
├── units.jsonl
├── chunks.jsonl
├── claim_candidates.jsonl
├── evidence_candidates.jsonl
├── annotation_pairs.jsonl
├── document_sustainability_signals.json
└── leakage_report.json

outputs/coverage/
├── coverage_company_year.csv
└── coverage_company_summary.csv
```

## Chia tập thời gian

- 2021–2022: train
- 2023: dev
- 2024: test
- 2025: future holdout

`leakage_report.json` liệt kê file trùng SHA-256 xuất hiện ở nhiều split.

## Quy mô mục tiêu

- 30 công ty × 5 năm = 150 company-year.
- 4 nhóm chứng cứ cốt lõi = tối đa khoảng 600 tài liệu lõi.
- Thực tế có thể thấp hơn do ESG được tích hợp trong BCTN và một số loại tài liệu không công khai riêng.
- Nên gán nhãn thủ công 500–1.500 claim–evidence pairs và 150–300 testcase chất lượng cao, thay vì tự sinh nhãn hàng loạt.

## Trình tự vận hành an toàn

1. Chạy `--dry-run` cho từng công ty.
2. Kiểm tra robots.txt và điều khoản sử dụng.
3. Crawl nguồn chính thức.
4. Crawl CafeF/HNX để lấp thiếu và giữ provenance thứ hai.
5. Xây dataset và chạy coverage.
6. Mở `missing` trong `coverage_company_year.csv` để bổ sung thủ công hoặc thêm seed URL.
7. Chỉ gán nhãn sau dedup và leakage check.

Không vượt CAPTCHA, đăng nhập, paywall hoặc cơ chế chống bot.
