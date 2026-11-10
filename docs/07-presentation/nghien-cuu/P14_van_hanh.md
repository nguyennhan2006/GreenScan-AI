# P14 · Vận hành: hiệu năng, phần cứng, tái lập, manifest

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Chạy được một lượt phân tích trên máy laptop không GPU, ngoại tuyến, trong thời gian chấp nhận được, và tái lập được kết quả. Đây là điều kiện để demo và để kiểm tra độc lập **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 1).

## 2. Lỗi hoặc rủi ro đã đo được

- Thời gian dao động: 107–121 giây qua ba lần chạy; lần đo qua giao diện ngày 09/10 là 140,5 giây khi máy đang chạy việc khác **[ĐÃ THỰC NGHIỆM]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, bảng phần cứng; `benchmark/queue_quality_2026-10-06.md`).
- Bộ test có 721 phiên lưu (khoảng 1 GB), trong đó 637 phiên của bộ test và bộ hồi quy **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-07).
- Con số "khoảng 2 phút" trong kịch bản trình bày chưa đo trên máy trình chiếu **[KIẾN THỨC NỀN]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, dòng 204).

## 3. Thiết kế hiện tại, file code, cấu hình

- Khởi động một chạm: `GreenScan.bat` hoặc `start.sh`; giao diện và API cùng cổng 127.0.0.1:8000, tiền tố `/api` **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 1).
- CLI: `quantum-agent analyze`, `demo`, `evaluate`, `evaluate-real`, `serve`, `app` (`cli.py`) **[KIẾN THỨC NỀN]** (cùng file).
- Hàng đợi job: một luồng xử lý mặc định, giữ 50 job gần nhất trong bộ nhớ **[KIẾN THỨC NỀN]** (cùng file, mục 1).
- Manifest ghi hash đầu vào, phiên bản corpus, rule pack, prompt và model **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 10).

## 4. Vì sao chọn, phương án đã bỏ

- Chạy ngoại tuyến trên laptop vì tài liệu chưa công bố không được gửi đi **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 3).
- Bỏ phương án máy GPU đám mây cho việc đọc tài liệu do chi phí và vùng dữ liệu **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-05).

## 5. Số đo có n

- 264 trang, 156 tuyên bố, i7-1355U, 16 GB, không GPU, ngoại tuyến; thời gian 107,4 giây; RAM đỉnh 1.331 MB **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).
- Ba tầng phần cứng: laptop 8–16 GB; laptop kèm khoá FPT AI; GPU 24 GB. Đã đo tầng 1: khoảng 2 phút, RAM 1,3 GB. Đã đo tầng 2: chạy đầu 632 giây, chạy lại 188 giây. Tầng 3 chưa đo **[ĐÃ THỰC NGHIỆM]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, bảng phần cứng).

## 6. Giới hạn và yếu tố gây nhiễu

- Chỉ đo trên một bộ hai tài liệu của một doanh nghiệp **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).
- Hàng đợi job chỉ giữ trong bộ nhớ, một luồng; không phù hợp nhiều người dùng đồng thời **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 1).

## 7. Lỗi đã gặp và cách gỡ

- Bộ test ghi vào dữ liệu thật. Gỡ bằng quy tắc không ghi vào dữ liệu thật và công cụ `tools/prune_runs.py` chỉ liệt kê mặc định **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-10-06-07).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Hiệu năng đo trên một bộ tài liệu; tái lập trên máy khác chưa kiểm **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-06).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đo lại thời gian trên máy trình chiếu trước 17/10 **[KIẾN THỨC NỀN]** (`docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, dòng 204).
- Kiểm tra manifest tái lập trên máy thứ hai. Dự đoán: kết quả khớp hash **[GIẢ THUYẾT]**.

## 10. Hình nên vẽ và file dữ liệu

- Cột thời gian theo lần chạy; biểu đồ RAM theo thời gian (đường lấy mẫu mỗi 0,5 giây).
- Dữ liệu: `benchmark/queue_quality_2026-10-06.md`.
- THIẾU: số bài test chính xác. Tài liệu ghi 14 test bất biến, nhưng tệp có 15 hàm `def test_`. Cách lấy: chạy `pytest tests/test_architecture_invariants.py --collect-only` và cập nhật tài liệu.
