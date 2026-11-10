# Nộp sản phẩm Vòng 2: trạng thái (cập nhật 10/11/2026)

## 0. Soát lại ngày 10/11 (đối chiếu từng yêu cầu của thông báo BTC mục II)

| Yêu cầu BTC | Trạng thái 10/11 |
|---|---|
| 1. Báo cáo 8–12 trang, đúng mẫu | 12 trang, đủ 01–08, cam kết, bìa phụ. Đã điền thông tin đội lấy từ hồ sơ Vòng 1 (ngành, CCCD, email, SĐT, vai trò, nhóm chủ đề “AI cho Quản trị Rủi ro và Tuân thủ”, người liên hệ Quỳnh). **Còn đỏ:** link prototype, link video. **Còn phải làm tay:** chữ ký đại diện (Quỳnh) |
| 2. Slide .pptx | 18 slide. **Còn:** link chạy thử (S6, S17), link video (S6) |
| 3. Mã nguồn 1 tệp zip | Dựng lại 15:13 từ mã hiện tại (gồm thay đổi sáng 10/11: `claim_attributes.py`, lý do bác kết luận của máy, kiểm thử nhất quán quy tắc): 1033 tệp, 78,3 MB, sha256 `bcba56d1…85dd60`; không có CCCD/SĐT/khoá bí mật. Có kèm bản nháp `docs/09-luan-van/BAO_CAO_TONG_HOP/` |
| 4. Hướng dẫn .pdf | 4 trang. Đã điền người hỗ trợ kỹ thuật (Nhân). **Còn đỏ:** link chạy thử, mật khẩu `giamkhao`, link video |
| 5. Link prototype | **Chưa triển khai.** Token HF trên máy (`chonnhan2023`, tên token WACV-UPAR-NTN) chỉ có quyền đọc → tạo Space bị 403. Thư mục Space và script đã sẵn, chạy lại khi có token quyền ghi |

**Đã sửa 10/11:**
- Mã đội đổi thành **AQ2026-119** (theo hồ sơ Vòng 1) ở tên 4 tệp, video, báo cáo, slide, hướng dẫn. Tệp tên cũ chuyển vào `nop_vong2/_cu_AQ2026119/`.
- Báo cáo trang 6 bị cụt câu ở “tự chủ 90” (dấu `%` chưa thoát trong LaTeX) → đã sửa.
- Báo cáo ghi video “3 phút 42 giây” → 6 phút 31 giây (bản 2).
- Số kiểm thử 487 → **530** (chạy lại 10/11: 530 đạt, 0 lỗi). GS-Bench (453 / 35 / 24 / 10 + 1) và 4/4 vụ có phán quyết **không đổi** sau thay đổi mã sáng 10/11.
- Ghi chú slide 15: bỏ chỗ “[chỉ ghi khi có thật]”, ghi đội chưa có đối tác thí điểm.

**Cần đội xác nhận:** giảng viên hướng dẫn đang ghi “Không có” (hồ sơ Vòng 1 không có mục này); khoa/trường đại diện ghi “Học viện Tài chính”.

**Lưu ý phối hợp:** chiều 10/11 có phiên khác đang làm video hoạt hình ở `nop_vong2/video/hoat_hinh_2d/`. Sửa mã thêm thì phải dựng lại zip (`tools/package_submission.py --ma-doi AQ2026-119`) và, nếu Space đã lên, đẩy lại Space.

Theo *Thông báo về chuẩn bị nộp sản phẩm Vòng 2* của BTC (`docs/Thong-bao-ve-chuan-bi-nop-san-pham-Vong-2.pdf`, ngoài repo):

| Mốc | Ngày |
|---|---|
| Hạn nộp (trước 24h, tại https://ai-quantum.hvtc.edu.vn/) | **20/11/2026** |
| Vòng 2 – Bán kết (trực tiếp hoặc trực tuyến) | **28–29/11/2026** |

Các tài liệu trong `docs/10-chung-ket-2026-11/` được soạn theo lịch cũ (“Chung kết 10/11”). Nội dung câu hỏi và khái niệm vẫn dùng được; **ngày tháng trong đó đã cũ**. Nếu lịch còn điểm chưa rõ, hỏi BTC.

## 1. Gói nộp (thư mục `D:/Sinh viên CNhan/AI quantum/nop_vong2/`, ngoài repo)

| Tệp | Trạng thái 09/11 | Dựng lại |
|---|---|---|
| `AQ2026-R2-AQ2026-119-Bao_cao_giai_phap.pdf` | 12 trang, đúng mẫu BTC (bìa, mục lục, 01–08, cam kết, bìa phụ) | `src_baocao/`: `xelatex baocao.tex` × 2 |
| `AQ2026-R2-AQ2026-119-Slide.pptx` | 18 slide (17 trình chiếu + 1 phụ lục), lời nói và phân vai trong ghi chú; theo kịch bản `docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md`, số liệu 09/11 | `src_slide/`: `NODE_PATH=<node_modules có pptxgenjs> node build_deck.js` |
| `AQ2026-R2-AQ2026-119-Huong_dan.pdf` | 4 trang: ba mức kiểm (trực tuyến, cài trên máy, tái lập số liệu), dữ liệu mẫu, kịch bản kiểm, xử lý sự cố | `src_huongdan/`: `xelatex huongdan.tex` × 2 |
| `AQ2026-R2-AQ2026-119-Ma_nguon.zip` | Dựng bằng `tools/package_submission.py --ma-doi AQ2026-119`; quét khoá bí mật, kèm `MANIFEST_NOP_BAI.txt` (SHA-256 từng tệp) | Chạy lại **sau lần sửa mã cuối cùng** |
| Link prototype | **Chưa triển khai**: cần tài khoản của đội (xem `deploy/HUONG_DAN_TRIEN_KHAI.md`) | — |
| `video/AQ2026-R2-AQ2026-119-Video_demo.mp4` (+ `.srt`) | Bản 2 “Một ngày của chị Hà”: 6:31, 1920×1080, 11 chương, mỗi chương một khó khăn thật của người soát xét, giải trên ứng dụng thật. Thuyết minh giọng nam Edge TTS `vi-VN-NamMinhNeural`. Quay trực tiếp ứng dụng ngoại tuyến trên phiên Hòa Phát mới (`490a960b80224504`), phân tích thật 2 phút 12 giây, tua ×17 có đồng hồ thời gian thật. Nhân vật, thư giao việc, mốc giờ, cảnh họp là giả định và có nhãn | Mã dựng ở thư mục tạm của phiên 09/11 (`beats2.cjs`, `record.cjs`, `assemble2.py`); quy trình ở `video/KICH_BAN_VIDEO.md` mục 9 |
| `video/AQ2026-R2-AQ2026-119-Video_demo_khong_loi.mp4` | Cùng hình, không lời; chú thích trên màn hình thay lời đọc | như trên |
| `video/KICH_BAN_VIDEO.md` | Ý đồ đạo diễn, storyboard, kịch bản 11 chương (khó khăn → thao tác → kết quả → nhận xét), lời thuyết minh, chú thích, dòng thời gian zoom và ảnh chèn, phân tích kết quả, kết luận | `write_docs2.py` |
| `video/ban_cu_v1/` | Bản 1 (6:04, giọng HoaiMy, 9 bước), giữ để so sánh; không nộp | — |
| Link video | **Chưa có**: đội tải video lên (YouTube không công khai hoặc Drive) rồi điền vào báo cáo, hướng dẫn, slide | — |

## 2. Thay đổi trong mã ngày 09/11

- **claim-quality-v1** (`src/quantum_gw/agents/claim_quality.py`): câu có thể không phải tuyên bố được *đánh dấu*, không xoá, và không chấm rủi ro. Trên 210 câu có nhãn: bắt 15/61 câu không phải tuyên bố, đánh dấu nhầm 1/149 tuyên bố thật. Dự đoán và kết quả ở `configs/measurement_decisions.yaml` (khối `claim_quality_v1_and_risk_rubric_v3`).
- **risk-rubric-v3** (`configs/scoring_v1.yaml`): tương quan điểm rủi ro với nhãn tăng từ 0,39 lên 0,46 [0,23; 0,59]. Mức rủi ro trên 4 vụ việc có phán quyết giảm từ khớp 2/4 xuống 1/4 (BNY 78 CRITICAL → 70 HIGH): **việc chờ Nhân quyết** là có thêm sàn CRITICAL cho “mâu thuẫn từ nguồn có thẩm quyền” hay không.
- **Triển khai:** lớp mật khẩu demo (`QUANTUM_DEMO_USERS`), trần tải lên (`QUANTUM_MAX_UPLOAD_MB`), kho tài liệu chép sang máy khác vẫn tìm được tệp, phiên mẫu tự cài khi khởi động (`deploy/seed/`, `tools/build_demo_seed.py`), `QUANTUM_HOME` có tác dụng thật trong container, Dockerfile chạy bằng uid 1000.
- **Sửa lỗi:** máy chủ dừng ngay khi khởi động trên cửa sổ Windows tiếng Việt (cp1258) vì in tiếng Việt; trong Docker, đường dẫn mặc định tới phiên mẫu sai nên phiên mẫu không được cài.
- **Tái lập số liệu:** `experiments/AG-0/score.py` chấm GS-Bench từ đầu ra của `run_rules.py` (số ở báo cáo mục 3.4).

## 3. Số đo 09/11 (đã chạy lại trên máy của đội)

| Kiểm | Kết quả |
|---|---|
| `pytest` | 487 đạt, 0 lỗi |
| GS-Bench v1 (`run_rules.py` + `score.py`) | 453 ca; 35 kết luận dứt khoát (0,077); đúng 24 (0,686); 10 “ủng hộ” sai, 1 “mâu thuẫn” sai |
| Vụ việc có phán quyết (`run_case.py --all`) | 4/4 khớp; verification 1.0; stance 1.0; legal coverage 1.0; risk band 0.25 |
| GS-Eval v2 (`evaluate.py`) | kết luận trùng nhãn 0,51 (n = 102); Spearman điểm rủi ro 0,459 [0,234; 0,588] (n = 148) |
| Máy chủ trên kho trống, có mật khẩu | `/health` 200; không mật khẩu 401; có mật khẩu 200; phiên Hòa Phát tự cài; trang PDF gốc hiện được |
| Docker build | **Chưa thử**: Docker Desktop không lên trong phiên 09/11 |

## 4. Việc của đội trước 20/11

**Điền chỗ in đỏ / trong ngoặc vuông:**
- Báo cáo: đội trưởng; ngành học, CCCD, email, điện thoại từng người; khoa/trường đại diện; giảng viên hướng dẫn (nếu có); nhóm chủ đề theo Thể lệ; người liên hệ chính; link prototype và video; phiên bản mã nguồn; người trình bày; thời lượng thuyết trình; chữ ký đại diện.
- Hướng dẫn: link chạy thử, mật khẩu tài khoản `giamkhao`, người hỗ trợ kỹ thuật (họ tên, điện thoại, email), phiên bản mã nguồn, link video.
- Slide: link chạy thử, link video; đối tác thí điểm (chỉ ghi khi có thật).

**Điểm chưa nhất quán trên giao diện, thấy khi quay video 09/11 (sửa thì quay lại video):**
- Mục #2: hàng đợi ghi “thiếu 1/5 thuộc tính”, thẻ Thuộc tính ghi 2/5 và “Năm gốc: Có”, còn dòng tóm tắt ghi thiếu số liệu, kỳ, năm gốc và “Giá trị trích xuất” ghi năm gốc “không nêu”. Báo cáo và slide đã đổi sang câu theo dòng tóm tắt, bỏ “3/5”.
- Hàng đợi ghi “Ủng hộ một phần”, trình sửa báo cáo ghi “Khớp một phần” cho cùng kết luận.
- Lịch sử quyết định hiện giờ địa phương, nhật ký thay đổi và giấy làm việc hiện giờ UTC, không ghi chú.
- Mục #1 của hàng đợi không phải tuyên bố: khi đọc PDF trang 20, chữ “HÒA PHÁT” bị ghép vào giữa một câu mô tả lò cao. Video bản 2 (chương 5) nói thẳng lỗi này và chèn ảnh trang gốc. Sửa bộ đọc PDF thì phải quay lại chương 5.
- Mã tiếng Anh còn hiện: REQUEST_EVIDENCE, AI_SUGGESTED → HUMAN_REVIEWED, internal, similarity, priority-v1.1, result.json, tco2e, VG-02 / SC-01; số trong thủ tục cộng bảng viết kiểu Anh (22,540,603).

**Xác nhận:**
- Phân công chuyên môn trong báo cáo (Quỳnh: kiểm toán – ESG và gán nhãn; Thảo: pháp lý; Nhân: kỹ thuật và số liệu) là suy ra từ tài liệu cũ.
- Chọn nền tảng triển khai. Hugging Face Space miễn phí phải để **công khai**: mã nguồn và hai PDF Hòa Phát trong `deploy/seed/` sẽ tải được từ repo của Space (lớp mật khẩu chỉ che giao diện). Nếu không muốn vậy, dùng máy chủ riêng (mục 4 của `deploy/HUONG_DAN_TRIEN_KHAI.md`).
- Quyết định sàn CRITICAL (mục 2).
- Mục #1 hàng đợi Hòa Phát vẫn là dòng dính chữ “HÒA PHÁT trò nền tảng…”; kịch bản demo đã tránh mở mục này.

**Thứ tự đề xuất:** triển khai và kiểm link (mục 5 của hướng dẫn triển khai) → điền chỗ trống → dựng lại 3 tệp PDF/PPTX → đóng băng mã, gắn thẻ phiên bản → dựng lại zip → nộp trước 20/11 → kiểm link mỗi ngày tới 29/11.
