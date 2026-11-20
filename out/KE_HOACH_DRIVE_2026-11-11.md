# Kế hoạch cập nhật Drive GreenScan (11/11/2026)

Tài liệu nội bộ, không tải lên Drive. Gói sạch nằm ở `out/drive_2026-11-11/`.

Đề xuất: không xoá hẳn. Tạo thư mục `_luu-tru_truoc-11-11/` trên Drive, chuyển các mục "BỎ" vào đó, rồi đặt quyền thư mục này chỉ cho nhóm.

## 1. Mục hiện có trên Drive

| Mục trên Drive | Quyết định | Lý do |
|---|---|---|
| AQ2026-R2-AQ2026119-Video_demo.mp4 (9/11) | GIỮ → `04_video/` | Video nộp vòng 2 mới nhất |
| greenscan-huong-dan.mp4 (15/10) | GIỮ tạm → `04_video/`; quay lại sau | Giao diện đã đổi từ 15/10 (thanh lưu ý ISSA 5000, trang Hướng dẫn, nút CSV) |
| greenscan-intro-A-sonnor.mp4, greenscan-intro-C-we-will-get-it.mp4 (9/10) | BỎ | Hai bản thử, không phải bản chính thức |
| ChatGPT Image Sep 25, 2026….png | BỎ | Nguồn gốc và mục đích không rõ |
| GREENSCAN.zip | BỎ | Bộ slide 26/09, mô tả cả những phần sản phẩm chưa làm |
| PIPELINE_DIAGRAM_BRIEF.md | BỎ | Đặc tả thiết kế nội bộ; nói bước 3–5 do mô hình làm, sai với mặc định |
| QA_BANK_100_2026-09-20.md, QA_DRILL.md | BỎ | Tài liệu luyện hỏi đáp, số cũ (210 tuyên bố, 233 bài kiểm, 5 nhãn vàng) |
| SLIDES_11_16_IMAGE_PROMPTS.md | BỎ | Lời nhắc sinh ảnh, ghi chú nội bộ |
| README.md (07-presentation) | THAY bằng `00_DOC_TRUOC.md` | Mục lục cũ có lệnh dựng và câu "mọi con số đo được" |
| ban-ket-2026-10-25/ (README, 01–04) | BỎ | Kịch bản, lịch tập, hỏi đáp luyện của bán kết; số cũ (9/172, 359 bài kiểm, nhãn "khớp một phần") |
| paper/ (md, pdf, figures, make_figs.py, paper.css) | THAY bằng `01_bao-cao/` | Bài viết lại: số 11/11, năm nhãn tiếng Việt, bỏ lịch đã qua, lệnh, tên tài khoản Kaggle; thêm GS-Eval v2 và ISSA 5000 |
| technical_brief/ (pdf, tex) | BỎ | Bản 9/2026 mô tả sai cấu hình (mô hình bật mặc định, BGE-M3, dung sai 12%); bài báo cáo mới thay thế |
| diagrams/pipeline_16x9_vi.png, .svg | THAY bằng `02_so-do/so_do_quy_trinh.*` | Đổi 3 nhãn "MÔ HÌNH" thành "LUẬT", nhãn kết luận mới, 10 cổng |
| diagrams/pipeline_16x9_en.png, .svg | BỎ | Bản tiếng Anh, chưa sửa |
| diagrams/GreenScan_AI_Giai_thich_pipeline_de_hieu.docx | BỎ (hoặc sửa sau) | Nhắc "TARGET PIPELINE" không còn trên sơ đồ, nhiều từ tiếng Anh, có đoạn dặn cách nói với BGK |
| screenshots_ui_2026-10-15/ (21 ảnh + README) | BỎ; chụp lại | Chụp trước các thay đổi giao diện tháng 11 |

## 2. Mục mới cần tải lên (từ `out/drive_2026-11-11/`)

| Mục | Ghi chú |
|---|---|
| `00_DOC_TRUOC.md` | Mục lục, câu lưu ý ISSA 5000, bảng số liệu chính |
| `01_bao-cao/GREENSCAN_BAI_BAO_2026-11-11.pdf` + `.md` + `hinh/` | 14 trang, 8 hình (hình hàng đợi cũ bỏ, hình Hòa Phát dựng lại theo lượt 11/11) |
| `01_bao-cao/HUONG_DAN_SU_DUNG_1_TRANG.md` | Hướng dẫn một trang |
| `02_so-do/so_do_quy_trinh.png`, `.svg` | Sơ đồ đã sửa |
| `03_du-lieu/` (22 MB, 49 tệp) | GS-Bench v1, GS-Eval v2, GS-Issue, phiếu gán nhãn người (88 cặp, chưa gán), tài liệu IAASB, thẻ dữ liệu |

## 3. Còn phải làm

1. Chụp lại ảnh giao diện trên bản 11/11 (hàng đợi, trang tuyên bố, giấy làm việc, Studio, trang Hướng dẫn).
2. Quay lại video hướng dẫn nếu giữ.
3. Sơ đồ tiếng Anh: sửa như bản tiếng Việt nếu BTC cần.
4. Chốt lượt Hòa Phát chính thức (8/172 với bộ lọc chất lượng câu v1.1) trước khi in số vào slide.
