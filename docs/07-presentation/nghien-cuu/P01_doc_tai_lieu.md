# P01 · Tiếp nhận và đọc tài liệu (PDF, Office, OCR tiếng Việt)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Biến tài liệu công bố (PDF, Office, scan) thành đoạn văn bản, bảng và số liệu có trang, để các khâu sau trích tuyên bố và đối chiếu **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2, bước 2).

## 2. Lỗi hoặc rủi ro đã đo được

- Bảng PDF bị dàn phẳng khiến cả 4 mô hình từ 26B trở lên báo SUPPORTED sai trên các ca N02, N05 và bảng GHG trang 39 **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, F3).
- Số liệu công bố đọc được giảm từ 57 xuống 16 sau khi sửa bộ đọc số; 34 số trước đó không gắn được chỉ số môi trường nào **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, bảng so sánh, HPG 264 trang).
- Trước khi sửa, 10/22 mục đầu hàng đợi là câu giải thích công nghệ hoặc chữ dính cột; sau khi sửa, 0/9 **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Trong 13 tệp scan đã OCR tiếng Việt, độ tin cậy trung bình từng trang phần lớn nằm ở 91–96 **[ĐÃ THỰC NGHIỆM]** (`docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 3, lớp L1).

## 3. Thiết kế hiện tại, file code, cấu hình

- PyMuPDF đọc chữ theo khối. Trang dưới 40 ký tự được chuyển sang Tesseract OCR chạy tại máy. pdfplumber tách bảng thành một khối `TABLE`. Đoạn tối đa 3 câu hoặc khoảng 600 ký tự **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2).
- Mã nguồn: `src/quantum_gw/parsers/documents.py`, `ocr.py`, `office.py` **[KIẾN THỨC NỀN]**.
- Mốc sửa Tesseract `vie` là 22/10 **[KIẾN THỨC NỀN]** (`docs/07-presentation/nghien-cuu/00_DANH_MUC_CAN_THU_THAP.md`, bảng P01).

## 4. Vì sao chọn, phương án bỏ

- OCR chạy tại máy, không gửi tài liệu ra ngoài. Lý do là quy tắc dữ liệu D-2026-10-06-06 **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`).
- Giữ bảng nguyên khối, không cắt, vì mô hình đọc bảng vỡ sẽ sai **[ĐÃ THỰC NGHIỆM]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2).
- Đang so bốn cách dựng bảng: PyMuPDF `find_tables`, pdfplumber, Docling, Table Transformer **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, AG-3). Chưa có kết quả so sánh.

## 5. Số đo có n

- HPG: 2 tài liệu, 264 trang, 156 tuyên bố. Thời gian 107,4 s; 3 lần chạy 107–121 s; RAM đỉnh 1.331 MB; máy i7-1355U, 16 GB, không GPU **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).
- Trước và sau rà soát 06/10, số tuyên bố và kết quả kiểm chứng không đổi (156; 153 khớp một phần, 2 ủng hộ, 1 chưa đủ bằng chứng) **[ĐÃ THỰC NGHIỆM]** (cùng file).

## 6. Giới hạn và yếu tố gây nhiễu

- Chỉ một doanh nghiệp, một bộ 2 tài liệu. Chưa có số đo độ chính xác OCR theo ký tự hoặc theo ô bảng.
- Câu "Mục #1 chữ gãy dòng" còn tồn tại; "7,085" và "6,838" mơ hồ dấu thập phân **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, mục "Còn lại").
- THIẾU: tỷ lệ lỗi OCR tiếng Việt trên một mẫu trang scan có đáp án tay. Cách lấy: lấy 30 trang scan, nhập đáp án tay, chạy `tools/ocr_legal_document.py` và tính độ đúng ký tự.

## 7. Lỗi đã gặp và cách gỡ

- Gộp dấu "cộng" và "công" khiến dòng tổng bị nhận nhầm; nay so trên chữ có dấu **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, nguyên nhân 1).
- Nhãn vượt ranh giới câu và đơn vị của cột bên cạnh bị đọc nhầm (ví dụ "100 %" thành 23 triệu phần trăm) **[ĐÃ THỰC NGHIỆM]** (cùng file, nguyên nhân 2–3).

## 8. Trạng thái năng lực

**IMPLEMENTED–NOT VALIDATED.** Đường đọc và OCR đã cài và chạy được trên một bộ tài liệu. Độ đúng từng ô bảng chưa đo **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-06 về bốn trạng thái).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- AG-3 (01–04/11): so bốn cách dựng bảng, kiểm tổng cộng ngang và dọc, gold 12–15 bảng của 4–5 doanh nghiệp **[KIẾN THỨC NỀN]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, AG-3).
- Dự đoán: kiểm tổng chặn ít nhất 80 % bảng dựng sai; SUPPORTED sai trên N02 và N05 về 0 **[GIẢ THUYẾT]** (cùng file).

## 10. Hình nên vẽ và file dữ liệu

- Sơ đồ mười bước của một lượt phân tích, đánh dấu bước đọc tài liệu.
- Bảng trước và sau rà soát 06/10 (số liệu, hàng đợi, tuyên bố). Dữ liệu: `benchmark/queue_quality_2026-10-06.md`.
- THIẾU: hình chụp trang tài liệu được tô sáng. Cách lấy: chụp từ phiên demo đã lưu trong ứng dụng.
