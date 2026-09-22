# Báo cáo thu thập dữ liệu — 2026-08-07

Lần chạy thu thập đầu tiên tạo ra corpus đầu vào cho bài toán phát hiện
greenwashing. Báo cáo này ghi lại **thu được gì**, **hỏng ở đâu**, và **làm gì
tiếp**.

## 1. Hai bộ dữ liệu đã tạo

### 1.1 `data/real_cases/sources/originals/` — nguồn gốc có phán quyết

14 tài liệu, 45 MB. Trước lần chạy này thư mục rỗng: script tải về fail toàn bộ
6 nguồn SEC.

| Case | Tài liệu | Trang |
| --- | --- | ---: |
| KDP-2024 | SEC order 34-100983 + press release | 5 |
| BNY-2022 | SEC order IA-6032 + press release | 8 |
| DWS-2023 | SEC order IA-6432 + press release + annual report 2023 | 9 / 277 |
| KLM-2024 | Bản án ECLI:NL:RBAMS:2024:1512 (XML) + annual report 2020 | 107 |
| VN-HPG-CONTROL | Báo cáo thường niên 2024 + báo cáo PTBV 2025 | 156 / 108 |
| VN-BVH-CONTROL | Trang PTBV + trang quan hệ cổ đông | — |

**Toàn bộ PDF đều có text layer** (0–5 % số trang thiếu chữ, chủ yếu là trang
bìa). Không cần OCR cho bộ này — tiết kiệm được cả một tầng xử lý và nguồn sai
số. Kết luận này phải kiểm lại khi thêm tài liệu scan.

Đã chạy thử `VN-HPG-CONTROL` qua pipeline: trích được 41 claim, verify hết,
35 `PARTIALLY_SUPPORTED` + 6 `SUPPORTED`. Dữ liệu dùng được thật, không chỉ
tải về nằm đó.

### 1.2 `data/crawl/vn30/` — corpus doanh nghiệp Việt Nam

670 tài liệu / 21 doanh nghiệp / 2021–2025 / 3,9 GB.
Chuẩn hoá thành 7 960 claim candidate và 3 786 evidence candidate.
Chi tiết: [README.md](README.md).

## 2. Bảy lỗi đã sửa

Không lỗi nào tìm ra bằng đọc code. Tất cả chỉ lộ ra khi chạy thật.

| # | Lỗi | Hậu quả trước khi sửa |
| --- | --- | --- |
| 1 | `urllib` không gửi header `Accept`; WAF của sec.gov trả 403 | 6/6 nguồn SEC fail — bộ real_cases không có tài liệu gốc nào |
| 2 | `attachment_domains` rỗng cho cả 30 doanh nghiệp | Crawl xong "thành công" với 0 tài liệu, không một dòng cảnh báo |
| 3 | URL trong config là URL đoán theo mẫu | 11/30 doanh nghiệp trả 404 |
| 4 | Link asset (`jquery.js`, `favicon.ico`) được chấm là liên quan | Vinamilk: >10 phút → 28 giây sau khi lọc |
| 5 | `robots.txt` trả 403 bị hiểu là cấm | 177 PDF công khai bị loại im lặng |
| 6 | Không có trần tài liệu cho mỗi doanh nghiệp | Coteccons lấy 162 tài liệu, 24 doanh nghiệp khác chưa được chạm |
| 7 | Đọc `.jsonl` bằng `splitlines()` | Mất bản ghi khi text chứa U+2028 |

Lỗi 2 và 5 nguy hiểm nhất vì chúng **im lặng**: crawler kết thúc với exit code 0
và một corpus rỗng. Một crawler báo lỗi to là crawler dễ sửa; một crawler trả về
tay trắng kèm exit 0 thì không.

Lỗi 5 đã có regression test (`tests/test_robots.py`): 4xx → cho phép, 5xx và lỗi
transport → cấm, và rule thật khi có robots.txt vẫn phải được tôn trọng.

**Lỗi 7 đáng nói riêng.** `str.splitlines()` ngắt dòng ở cả U+2028, U+2029 và
U+0085 — những ký tự hợp lệ bên trong chuỗi JSON và có thật trong text bóc từ PDF
tiếng Việt. Đọc file `.jsonl` kiểu `read_text().splitlines()` sẽ mất một bản ghi
cho mỗi lần xuất hiện, **không báo lỗi gì** ở phần lớn trường hợp. Trong repo có
bốn chỗ dùng đúng kiểu này, gồm cả `evaluation/runner.py` chạy golden set:

```python
# sai
[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
# đúng
[json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x.strip()]
```

Đã sửa cả hai đầu: consumer đọc bằng `split("\n")`, và `dataset/build.py` escape
ba ký tự này khi ghi, để file `.jsonl` an toàn với cả reader viết theo thói quen.
File đã sinh cũng được escape lại tại chỗ — số bản ghi giữ nguyên và cả hai cách
đọc giờ cho cùng kết quả.

## 3. Vấn đề môi trường: proxy chặn TLS

Máy chạy có Avast can thiệp TLS. Root của nó mã hoá `basicConstraints` không
critical, mà Python 3.13+ bật `VERIFY_X509_STRICT` mặc định, nên **mọi** request
HTTPS fail với `CERTIFICATE_VERIFY_FAILED`.

Cách làm thường gặp là `verify=False`. Đó là đổi một lỗi lấy một lỗ hổng: tắt
xác thực cho mọi host, crawler không còn phân biệt được server thật với bất cứ
thứ gì trả lời ở cổng 443.

`tools/local_proxy_tls/sitecustomize.py` chỉ làm hai việc: thêm root của proxy
vào trust store, và bỏ cờ kiểm tra mã hoá nghiêm ngặt. Chuỗi chứng chỉ và
hostname vẫn được xác thực đầy đủ — đã kiểm chứng với `expired.badssl.com`,
`wrong.host.badssl.com`, `untrusted-root.badssl.com`: cả ba vẫn bị từ chối.

Shim này chỉ bật khi `GREENSCAN_TRUST_LOCAL_PROXY=1` và chỉ nằm trên `sys.path`
khi người chạy tự thêm vào `PYTHONPATH`. **Không dùng ở production.**

## 4. Việc tiếp theo, theo thứ tự ưu tiên

1. **9 doanh nghiệp chưa có tài liệu** (acg, bmp, chp, dmc, nt2, ocb, qns, tlg,
   tng). `nt2` không kết nối được, `qns` 403, `chp` không còn trang IR sống —
   ba trường hợp này cần lấy qua HNX/HOSE thay vì crawl trực tiếp. Sáu trường
   hợp còn lại cần mở rộng `harvest_js_listings.py`.
2. **196 tài liệu chưa xác định năm** đang nằm ở split `review`. Gán năm từ nội
   dung tài liệu thay vì từ tên file, rồi build lại.
3. **1 cross-split duplicate** trong `leakage_report.json` — xử lý trước khi gán
   nhãn.
4. **Gán nhãn thủ công.** Bộ crawl là dữ liệu thô, **không** phải nhãn. Kế hoạch
   trong `real_cases/reports/NEXT_COLLECTION_PLAN.md` đặt mục tiêu 500–1 500
   cặp claim–evidence có hai reviewer. 7 960 claim candidate là đầu vào để chọn
   mẫu, không phải nhãn dùng luôn được.
5. **Ưu tiên 42 báo cáo PTBV/tích hợp** khi chọn mẫu gán nhãn — đây là nơi claim
   môi trường tập trung dày nhất.

## 5. Ranh giới phải giữ

- Tài liệu thu được **không** phải bằng chứng greenwashing. Chúng là văn bản thô.
- Thiếu dữ liệu **không** được tự động quy thành nhãn vi phạm.
- Các case SEC là dàn xếp *without admitting or denying* — giữ nguyên qualifier
  khi trích dẫn.
- Control Việt Nam (Hoà Phát, Bảo Việt) không được gán nhãn greenwashing nếu
  chưa có bằng chứng độc lập và phán quyết.
