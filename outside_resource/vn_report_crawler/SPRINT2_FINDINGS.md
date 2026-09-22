# Sprint 2 — Kết quả khảo sát nguồn

**Ngày:** 2026-07-29
**Phạm vi dự kiến:** `VietstockAdapter` + `CafeFAdapter`, dry-run 100 tài liệu mỗi nguồn,
so overlap với website doanh nghiệp.
**Kết quả:** kế hoạch không khả thi như viết. Chi tiết bên dưới.

---

## 1. Vietstock và CafeF không dùng được với adapter HTML

Cả hai listing page render hoàn toàn bằng JavaScript. HTML tĩnh trả về **0 tài liệu**:

| URL | Kích thước | `<a>` | `<tr>` | Tài liệu |
|---|---:|---:|---:|---:|
| `finance.vietstock.vn/tai-lieu/bao-cao-tai-chinh.htm` | 249 KB | 1032 | 4 | 0 |
| `finance.vietstock.vn/tai-lieu/bao-cao-thuong-nien.htm` | 249 KB | 1032 | 4 | 0 |
| `finance.vietstock.vn/HPG/tai-tai-lieu.htm` | 266 KB | — | 4 | 0 |
| `cafef.vn/du-lieu/cong-bo-thong-tin.chn` | 144 KB | 70 | 2 | 0 |
| `cafef.vn/du-lieu/hose/HPG-….chn` | 399 KB | — | 4 | 0 |

Hai trang Vietstock có kích thước và cấu trúc gần như trùng khớp — chúng là **cùng một
shell**, danh sách tài liệu nạp sau bằng AJAX. Vài PDF tìm được là tài liệu marketing
của chính Vietstock (`VSTF_Huong_dan_su_dung`, `VS-SECTOR`), không phải báo cáo doanh nghiệp.

**robots.txt** (kiểm tra cùng ngày): cả hai **cho phép** các path trên. Nhưng Vietstock
có `Disallow: /*.js`, nên không được crawl JS bundle của họ để dò endpoint API.

**Để dùng được cần:**
- (a) Xác định endpoint JSON/AJAX thủ công qua DevTools → viết adapter API, **hoặc**
- (b) Adapter Playwright chỉ cho bước listing (không bật browser cho toàn nguồn).

Cả hai nằm ngoài phạm vi Sprint 2. Hai nguồn giữ `enabled: false`.

## 2. Bức tranh nguồn sau khảo sát

| Nguồn | Trạng thái | Ghi chú |
|---|---|---|
| Hòa Phát | ✅ dùng được | HTML tĩnh, PDF trên `file.hoaphat.com.vn` |
| Vinamilk | ✅ dùng được | PDF trên CDN CloudFront — **phải** thêm domain |
| Vingroup | ❌ HTTP 403 | Chặn bot kể cả UA trình duyệt |
| Vietstock | ❌ JS-rendered | Cần adapter API/Playwright |
| CafeF | ❌ JS-rendered | Cần adapter API/Playwright |
| HNX | ❌ JS-rendered | 98 KB HTML, 0 link tài liệu |

Kết luận: **nguồn tổng hợp không phải đường tắt**. Website doanh nghiệp cho dữ liệu
tốt hơn với chi phí kỹ thuật thấp hơn nhiều. Ưu tiên P0 nên đảo lại.

## 3. Dry-run thật

`--dry-run --max-documents 100`, hai nguồn dùng được:

| Nguồn | Tài liệu | Phân loại được | Phân bố |
|---|---:|---:|---|
| hoaphat | 29 | 24 (82%) | financial 10, annual 10, explanatory 3, sustainability 1 |
| vinamilk | 49 | 49 (100%) | governance 20, annual 17, sustainability 12 |
| **Tổng** | **78** | **73 (93%)** | trải 2014–2026 |

5 mục còn lại của Hòa Phát là công bố nghiệp vụ (ngày ĐKCC cổ tức, tổng quan kinh doanh
quý), không phải báo cáo — để `None` là đúng.

## 4. Ba bug tìm được nhờ dữ liệu thật

**4.1. Tên file ASCII hoá không phân loại được** *(nghiêm trọng)*

CDN đặt tên file bỏ dấu và nối bằng gạch dưới:

```
Bao_cao_quan_tri_Cong_ty_nam_2018.pdf
202601_VNM_Bao_cao_QTCT_ca_nam_2025_CBTT.pdf
```

Từ khoá `"báo cáo quản trị"` không bao giờ khớp vì so khớp là substring liền mạch trên
chuỗi có dấu. Toàn bộ 20 báo cáo quản trị của Vinamilk bị xếp `report_type = None`.

Sửa: thêm `fold_text()` (bỏ dấu, xử lý `đ`, coi `-_.` như khoảng trắng) và dùng cho
toàn bộ classifier. Cũng vá luôn lỗi cũ: `exclude_patterns: [tuyển dụng]` trước đây
không chặn được URL `tuyen-dung.pdf`.

**4.2. Thiếu biến thể từ khoá**

`"báo cáo quản trị"` không khớp `"báo cáo tình hình quản trị công ty"` và viết tắt
`QTCT`. Đã bổ sung vào `DEFAULT_REPORT_TYPES`.

**4.3. CDN không nằm trong `allowed_domains`** *(im lặng)*

Toàn bộ PDF của Vinamilk ở `d8um25gjecm9v.cloudfront.net`, không phải `vinamilk.com.vn`.
Config cũ chỉ khai báo domain công ty → crawler chạy xong với 0 tài liệu, không báo lỗi.

## 5. Bổ sung: phát hiện trang JS-rendered

`crawler/discovery/browser_fallback.py` — biến thất bại im lặng thành cảnh báo có lý do:

```
WARNING Trang có vẻ cần render JavaScript, không lấy được tài liệu:
        .../investor/reports/governance
        (tỷ lệ script/text = 248438/2771; 21 link giống file nhưng không phân loại được)
```

**Tín hiệu phải là kết quả thực tế của adapter, không phải hình dạng HTML.** Bản đầu
dùng heuristic "nhiều script + ít `<tr>`" và báo nhầm Vinamilk — trang đó có 202k ký tự
script, **0** thẻ `<tr>` (layout thẻ), nhưng vẫn tĩnh với 13 PDF thật. Ngược lại Vietstock
có sẵn vài PDF marketing nên "đếm link .pdf" cũng đánh lừa. Tín hiệu đáng tin duy nhất
là số ứng viên **phân loại được thành một report_type đã biết**.

Cả hai ca đối chứng nằm trong `tests/test_browser_fallback.py`, chạy trên HTML thật
lưu tại `tests/fixtures/`.

## 6. Đề xuất điều chỉnh kế hoạch

**Sprint 3 (thay cho stockbiz/24hmoney):** mở rộng nguồn website doanh nghiệp — đây là
nguồn `official_company`, authority cao hơn aggregator, và đang chứng minh là rẻ nhất.
Chọn 15–20 doanh nghiệp theo quota ngành mà kế hoạch gốc đã nêu.

**Sprint 4:** khảo sát HNX/HOSE bằng DevTools thủ công để tìm endpoint API. HNX là
`official_exchange` nên đáng đầu tư hơn aggregator. Cùng đợt này xử lý Vietstock/CafeF
nếu API lộ ra.

**Playwright:** chỉ cân nhắc sau khi đã vét hết nguồn tĩnh. Chi phí vận hành cao và
làm crawler khó tái lập.

---

## Phụ lục: tái lập

```bash
python scripts/refresh_fixtures.py          # tải lại HTML thật
pytest                                       # 95 test
python -m crawler.cli --config configs/official_companies.yml --dry-run --max-documents 100
```

Môi trường phát triển dùng để chạy khảo sát này có proxy MITM (`CERTIFICATE_VERIFY_FAILED`
với mọi domain ngoài), nên các lệnh trên chạy với `verify_ssl: false`. Config trong repo
giữ `verify_ssl: true` — **không** hạ mức xác thực TLS ở production.
