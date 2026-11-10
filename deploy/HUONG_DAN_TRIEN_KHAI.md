# Triển khai bản chạy thử GreenScan (link prototype cho Vòng 2)

Cập nhật 09/11/2026. Thông báo Vòng 2 (mục II.5) yêu cầu link prototype **chạy được và truy cập ổn định**
từ lúc nộp (20/11/2026) tới hết vòng thi (29/11/2026). Tài liệu này mô tả cách đưa bản chạy thử lên mạng
và cách kiểm trước khi khai link vào phiếu nộp.

## 1. Bản triển khai gồm những gì

| Thành phần | Ở đâu | Ghi chú |
|---|---|---|
| Ảnh container | `Dockerfile` | Hai tầng: dựng giao diện (Node 22), rồi Python 3.11 + Tesseract (tiếng Việt, tiếng Anh). Chạy bằng người dùng uid 1000, không cần quyền root. |
| Lệnh khởi động | `deploy/entrypoint.sh` | Tạo kho dữ liệu dưới `QUANTUM_HOME`, rồi chạy API và giao diện trên một cổng `PORT` (mặc định 8000). |
| Phiên mẫu | `deploy/seed/` | Phiên phân tích Hòa Phát (156 tuyên bố) và 2 PDF gốc mà phiên trích dẫn. API chép vào kho khi khởi động; không ghi đè thứ đã có. Dựng lại bằng `tools/build_demo_seed.py`. |
| Mật khẩu demo | biến `QUANTUM_DEMO_USERS` | Đặt thì mọi trang và API (trừ `/health`) đòi đăng nhập HTTP Basic. Không đặt thì mở tự do. |

Chế độ mặc định là ngoại tuyến (`QUANTUM_PROFILE=offline`): không gọi API mô hình ngôn ngữ nào, không cần khoá API.
**Không đưa tệp `.env` hay khoá API lên máy chủ.**

## 2. Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `QUANTUM_DEMO_USERS` | (trống: tắt) | Danh sách `ten:matkhau`, cách nhau bằng `;`. Ví dụ `giamkhao:<mật khẩu>;doithi:<mật khẩu>`. Đặt dưới dạng *secret* của nền tảng, không ghi vào mã. |
| `QUANTUM_MAX_UPLOAD_MB` | `80` | Trần dung lượng tải lên mỗi lượt; vượt thì trả lỗi 413. `0` là không giới hạn. |
| `QUANTUM_HOME` | `/app/.quantum` | Thư mục kho (phiên, tài liệu, quyết định của người duyệt). Trỏ vào ổ lưu bền (ví dụ `/data`) nếu nền tảng có. |
| `QUANTUM_SEED_DIR` | `/app/deploy/seed` | Thư mục phiên mẫu. Đặt chuỗi rỗng để tắt cài phiên mẫu. |
| `PORT` | `8000` | Cổng phục vụ. Phần lớn nền tảng tự đặt biến này. |
| `QUANTUM_JOB_WORKERS` | `1` | Số phân tích chạy song song. Máy 2 nhân nên để 1. |

## 3. Cách A: Hugging Face Spaces (miễn phí, khuyến nghị)

Gói miễn phí có 2 vCPU và 16 GB RAM, đủ cho chế độ ngoại tuyến (khoảng 1,3 GB RAM mỗi phân tích).

1. Tạo Space mới: *SDK = Docker*, *Blank*, chế độ **Public** (giám khảo không có tài khoản Hugging Face;
   lớp mật khẩu demo ở bước 4 thay cho quyền riêng tư).
2. Lấy mã nguồn từ chính tệp nộp `AQ2026-R2-<Mã đội>-Ma_nguon.zip` (đã loại bí mật và kho crawl 4 GB),
   giải nén, rồi thêm vào **đầu** tệp `README.md` của bản sao này khối khai báo:

   ```yaml
   ---
   title: GreenScan AI
   sdk: docker
   app_port: 8000
   pinned: false
   ---
   ```

3. Đẩy lên Space bằng git. Các PDF lớn hơn 10 MB (phiên mẫu, `data/real_cases/sources/originals`) phải đi qua
   Git LFS/Xet: `git lfs install` rồi `git lfs track "*.pdf"` trước khi `git add`.
4. Trong *Settings → Variables and secrets*: thêm secret `QUANTUM_DEMO_USERS`. Không thêm khoá API nào.
5. Chờ dựng ảnh (lần đầu có thể mất trên 10 phút). Log khởi động phải có dòng
   `[phiên mẫu] đã cài 1 phiên, 2 tài liệu vào kho`.

Lưu ý: Space miễn phí **ngủ khi không có truy cập** và kho dữ liệu bị đặt lại mỗi lần khởi động lại
(phiên mẫu được cài lại tự động; phân tích giám khảo tự chạy sẽ mất). Đánh thức Space một ngày trước 20/11
và trước buổi thi 28–29/11; có thể đặt dịch vụ giám sát gọi `/health` mỗi 30 phút trong các ngày đó.

## 4. Cách B: máy chủ riêng (VPS) hoặc máy của đội

```sh
docker build -t greenscan .
docker run -d --restart unless-stopped -p 8000:8000 \
  -e QUANTUM_DEMO_USERS='giamkhao:<mật khẩu>' \
  -v greenscan-data:/app/.quantum \
  --name greenscan greenscan
```

`-v greenscan-data:/app/.quantum` giữ phiên và quyết định qua các lần khởi động lại. Đặt sau một reverse proxy
có HTTPS (Caddy, Nginx) nếu dùng tên miền. Không có Docker thì chạy trực tiếp:
`QUANTUM_DEMO_USERS=... .venv/bin/python -m uvicorn quantum_gw.api:app --app-dir src --host 0.0.0.0 --port 8000`.

## 5. Kiểm trước khi khai link

| Kiểm | Kết quả đúng |
|---|---|
| Mở `<link>/health` | `200`, không hỏi mật khẩu |
| Mở `<link>/` | Trình duyệt hỏi tên và mật khẩu; nhập đúng thì vào giao diện tiếng Việt |
| Danh sách phiên | Có phiên "Hòa Phát (HPG) – BC phát triển bền vững 2025 + BC thường niên 2024": 156 tuyên bố; kết luận 153 ủng hộ một phần, 2 ủng hộ, 1 chưa đủ bằng chứng |
| Hàng đợi soát | 9 mục được đưa vào hàng đợi trên 172 mục ưu tiên |
| Mở một bằng chứng | Trang PDF gốc hiện ra, đoạn trích được tô sáng |
| Tải lên một PDF nhỏ | Phân tích chạy nền, có thanh tiến độ, xong thì hiện trong danh sách |
| Thử mật khẩu sai | Bị từ chối (401) |

Đã kiểm ngày 09/11/2026 trên máy của đội với kho trống (cách chạy trực tiếp): `/health` 200; `/v1/runs`
không có mật khẩu 401, có mật khẩu 200; phiên Hòa Phát cài tự động; trang 39 của báo cáo phát triển bền vững
hiện dạng ảnh PNG; giao diện 200.
