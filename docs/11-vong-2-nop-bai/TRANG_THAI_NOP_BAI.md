# Nộp sản phẩm Vòng 2: trạng thái (cập nhật 16/11/2026)

## 20/11/2026: kiểm độ ổn định prototype, đưa mô hình thách đấu vào mọi bản (D-2026-11-20-01) — trạng thái hiện hành

| Tệp nộp | Trạng thái |
|---|---|
| `nop_vong2/AQ2026-R2-AQ2026-119-Ma_nguon.zip` | checkpoint **`vong2_2026-11-20d`** (20c + giao diện vừa 1280×720), 1812 tệp, 112,5 MB, sha256 `1a27b9b16fc75809866df5084697841a96b48f4263c557aab70540f529187d8b`; repo 784 đạt; giải nén chạy `pytest` bằng mã trong zip: 779 đạt, 5 bỏ qua. Zip 18e cất ở `nop_vong2/_cu_AQ2026119/` |
| Gói chạy ngay | `goi_chay_ngay/GreenScan_chay_ngay_2026-11-20.zip` (kèm thư mục `GreenScan/` đã giải nén), 194,3 MB, sha256 `c8d63ec0af20d5328dae7196dc7995558ecdc7f5015c748adc9ea6b3334957c6`, dựng từ `20d` (bản `20c` ở `_cu_2026-11-20c/`); giải nén mới vào thư mục có dấu: lên sau 64–89 giây (lần đầu), `check_flow.py` ĐẠT, 8 bước Hướng dẫn ĐẠT. Bản 18/11 cất ở `goi_chay_ngay/_cu_2026-11-18/` |
| Bản trực tuyến | đẩy 20/11 chiều từ `static_space_v8` (dữ liệu v7, giao diện mới) (bản sao kho demo bỏ phiên Hòa Phát trùng `efcd…`, kèm `models/`); `check_flow.py` ĐẠT ở 1366 px và 390 px; 8 bước Hướng dẫn ĐẠT |
| Hướng dẫn (PDF 4 trang) | dựng lại 20/11 (`src_huongdan/huongdan_2011.pdf`; bản cũ ở `_cu_AQ2026119/`): sửa chữ “extit” in ra ở khung Thông tin nhanh; 6 phiên (trước ghi 4); tên điền sẵn “Khách”; tên mục thật (“Tải tài liệu”, “Cài đặt & chế độ chạy”); bỏ “đăng nhập giống bản trực tuyến”; bước 7 là “phần Quy tắc nội bộ của mục #2”; thêm `models/`; ghi bản trực tuyến không chạy mô hình. Mục 6 chạy lại trên mã zip: khớp mọi con số. Còn trống: link video |
| Báo cáo, Slide, Video | không đổi |

Đã kiểm 19–20/11:
- Rà mọi trang bản trực tuyến (6 phiên, 392 tuyên bố, Sửa báo cáo, Giấy làm việc, nút xuất, “Mở nguồn”): không lỗi trang, không HTTP lỗi; hai PDF Hòa Phát đủ 108 + 156 ảnh trang. Trên gói chạy ngay rà 10 tuyên bố mỗi phiên: Hòa Phát mở trang gốc có tô sáng, không lỗi.
- Hướng dẫn mục 5 (8 bước) đi bằng máy trên bản trực tuyến và gói chạy ngay, đúng mọi số liệu: 186 tuyên bố (183/3), hàng đợi 9/241, mẫu kiểm 5, 15 phép kiểm bảng khớp (4.994 + 41.334 = 46.328), phiên quy tắc 17 mục, tiền lệ “mâu thuẫn”, mô hình thách đấu bị cổng chặn.
- Đã sửa: (1) bước 8 trước đây không đúng ở mọi bản (“Chưa có mô hình nào”): phần mềm đọc `models/stance/registry.json`, thư mục này chưa có trong mã nguồn, nay thêm `models/stance/` (sổ + mô hình `hl-thuyet-minh`, 1,3 MB, đường dẫn tương đối; gate macro-F1 0,183 so với 0,345, không đạt) và `tools/build_portable.py` chép kèm. (2) Nút “Tải xuống” trong “Tệp kỹ thuật” tải tệp thật (trước mở ngay trong tab, rời khỏi ứng dụng). (3) `DOC_TRUOC.txt` của gói: lần chạy đầu khoảng 1 phút, lần sau khoảng 10 giây; nếu trình duyệt chưa kết nối thì tải lại.
- Giao diện 20/11 chiều (soát ở 1366×768 và 1280×720): thanh bên đủ mọi mục (trước: “Cài đặt & chế độ chạy” bị đẩy khỏi màn hình 768 px; mục “Hướng dẫn cho người mới” đổi thành “Hướng dẫn”); Lịch sử: mới nhất lên đầu (phiên Hòa Phát chính đứng đầu), bỏ “.quantum/runs”, “pipeline”, cột tài liệu chỉ ghi số tệp dưới 1536 px, nút “Mở →” rõ hơn; thẻ thống kê hàng đợi xuống dòng thay vì cắt chữ; Sửa báo cáo: thanh trên một dòng (“Bước 3 · Sửa báo cáo”, nhãn Phím tắt / Hướng dẫn / Mô hình chỉ hiện từ 1536 px), khung nhật ký thu gọn mặc định; trang đầu: cột phải đứng giữa, dấu kiểm. `check_flow.py` ĐẠT ở 1366×768, 1280×720, 390 px (bản thử) và trên trang thật; 8 bước Hướng dẫn ĐẠT trên trang thật và gói chạy ngay.
- Hạn chế đã biết: 4 phiên mẫu nhỏ dùng tệp .txt, “Mở nguồn” không có ảnh trang (404/415), hộp xem nguồn hiện đoạn văn thay thế.
- `CHAY_DEMO.bat` (kho bán kết) chạy mã trong repo nên cũng thấy mô hình thách đấu.

## 18/11/2026 chiều: luồng hướng dẫn flow-v2 (D-2026-11-18-02) — trạng thái hiện hành

| Tệp nộp (`nop_vong2/`) | Trạng thái |
|---|---|
| `AQ2026-R2-AQ2026-119-Ma_nguon.zip` | checkpoint **`vong2_2026-11-18e`**, 1809 tệp, 111,8 MB, sha256 `65fab69c6f0dbb0715676cd5085cc860e5256c668192ebc109a2162322fdcc87`; giải nén chạy `pytest` bằng mã trong zip: 779 đạt, 5 bỏ qua, 0 lỗi; không còn e-mail, đường dẫn máy dựng, bản build cũ |
| `video/AQ2026-R2-AQ2026-119-Video_demo.mp4` (+ không lời, `.srt`) | 6 phút 20 giây, quay lại theo luồng mới; khung gốc `video/demo_1_phien/rec9/` |
| `AQ2026-R2-AQ2026-119-Bao_cao_giai_phap.pdf` | 12 trang, video 6 phút 20 giây |
| `AQ2026-R2-AQ2026-119-Huong_dan.pdf` | 4 trang, thêm câu về thanh “Việc tiếp theo” |
| `AQ2026-R2-AQ2026-119-Slide.pptx` | 19 slide (dựng 18/11 trưa; hai ảnh slide demo dự phòng vẫn là giao diện 09/11) |
| Bản trực tuyến | đẩy lại 18/11 chiều từ thư mục sạch; Space chỉ còn 6 phiên, 12 tệp `assets`; `tools/check_flow.py` ĐẠT trên trang thật ở 1366 px và 390 px |
| Gói chạy ngay | `goi_chay_ngay/GreenScan_chay_ngay_2026-11-18.zip`, 193,7 MB, sha256 `b64823d1b506888f573dd56d07b39fe1773ce17878c43b01f7289a0f1f4dbd75`, dựng từ `18e`; chạy từ thư mục có dấu: 6 phiên, Hòa Phát 186/55/15/9, `check_flow.py` ĐẠT |

- Kiểm luồng sau mỗi lần sửa giao diện: `C:/Python314/python.exe tools/check_flow.py <url> [--width 390 --height 844]` (bản cài: chạy trên bản sao kho phiên).
- Chưa tái hiện được “trang trắng” người dùng gặp trên link trực tuyến; nếu còn, trang sẽ hiện dòng lỗi (màn hình báo lỗi trong `frontend/src/main.jsx`) để gửi lại.
- Còn để trống: link video trong báo cáo, slide, hướng dẫn. Chưa chụp lại hai ảnh slide demo dự phòng.

## 18/11/2026: giao diện + video theo nhận xét (D-2026-11-18-01) — trạng thái hiện hành

| Tệp nộp (`nop_vong2/`) | Trạng thái |
|---|---|
| `AQ2026-R2-AQ2026-119-Ma_nguon.zip` | checkpoint **`vong2_2026-11-18d`**, 1927 tệp, 122,9 MB, sha256 `8f36b115f057371a4fb7f203e9a04076bceb1318be7a8986d6b425ba77389dbb`; giải nén chạy `pytest` (dùng mã trong zip): 779 đạt, 5 bỏ qua, 0 lỗi; e-mail và đường dẫn máy dựng đã ẩn |
| `video/AQ2026-R2-AQ2026-119-Video_demo.mp4` (+ không lời, `.srt`) | 6 phút 12 giây, bản 6: mục lục, bảng hạn chế → khắc phục, 2.1–2.4, giao diện mới; khung gốc `video/demo_1_phien/rec8/` |
| `AQ2026-R2-AQ2026-119-Bao_cao_giai_phap.pdf` | 12 trang, ảnh hàng đợi giao diện mới, video 6 phút 12 giây |
| `AQ2026-R2-AQ2026-119-Huong_dan.pdf` | 4 trang, mô tả hàng đợi gọn (bấm vào để xem lý do) |
| `AQ2026-R2-AQ2026-119-Slide.pptx` | 19 slide, ảnh hàng đợi mới (ảnh chi tiết tuyên bố / trang gốc ở slide demo dự phòng vẫn là ảnh 09/11) |
| Bản trực tuyến | đã đẩy lại 18/11, kiểm trên trang thật: Roboto, mũi tên, hàng đợi Hòa Phát 9 mục, mục 6 bấm mở hiện lý do; 0 đường dẫn máy |
| Gói chạy ngay | `goi_chay_ngay/GreenScan_chay_ngay_2026-11-18.zip`, 204,4 MB, sha256 `bcc0ffd23db489098b09dfd4ada6116ffcecf03f9ac3b6b9ef9fc2fdd83751d0`, dựng từ `18d` + kho demo (6 phiên); đã chạy thử từ thư mục có dấu: 6 phiên, Hòa Phát 186/55/15/9, giấy làm việc có Roboto |

- Còn để trống: link video trong báo cáo, slide, hướng dẫn.
- Chưa làm (người dùng 18/11: “tập trung làm video, .zip, bản prototype”): chụp lại hai ảnh slide demo dự phòng (`src_slide/img/thuoc_tinh.png`, `trang_goc.png`, giao diện 09/11).

## 17/11/2026 khuya: dựng lại TOÀN BỘ bài nộp theo bản mới nhất (D-2026-11-17-04) — trạng thái hiện hành

| Tệp nộp (`nop_vong2/`) | Trạng thái |
|---|---|
| `AQ2026-R2-AQ2026-119-Ma_nguon.zip` | checkpoint **`vong2_2026-11-17f`**, 1900 tệp, 120,3 MB, sha256 `f96079ea09c4c8a11640ec37e9fde8e649538483f25c31255a93362017fc8e24`; giải nén chạy `pytest`: 779 đạt, 5 bỏ qua (cần kho dữ liệu thô), 0 lỗi; e-mail đã ẩn |
| `AQ2026-R2-AQ2026-119-Bao_cao_giai_phap.pdf` | 12 trang, số Hòa Phát mới, ảnh hàng đợi 9/241, video 4 phút 45 giây |
| `AQ2026-R2-AQ2026-119-Huong_dan.pdf` | 4 trang, số mới, GS-Bench 123/0,272/105/0,854, kiểm thử trên zip |
| `AQ2026-R2-AQ2026-119-Slide.pptx` | 19 slide, số mới (nguồn `src_slide/build_deck.js`) |
| `video/AQ2026-R2-AQ2026-119-Video_demo.mp4` (+ không lời, `.srt`) | 4 phút 45 giây, bản 5 (Minh Họa + 3 nhịp quay thật phiên Hòa Phát), khung gốc `video/demo_1_phien/rec6/` |
| Bản trực tuyến | đã đẩy lại, 6 phiên, kiểm trên trang thật: hàng đợi 9 mục, dòng lý do mục 6 |
| Gói chạy ngay | dựng lại từ `17f` (xem dòng cuối mục này) |
| Bản thuyết minh | **18/11:** `docs/09-luan-van/THUYET_MINH_HE_THONG/THUYET_MINH_HE_THONG_2026-11-18.docx`: chương 3–9 chạy lại trên mã hiện hành (Ca A `657b68065a37496f`: 3 mâu thuẫn, 2 chưa chứng minh; Ca B `fe38a4515c1148d5`: 186 tuyên bố, 55 số liệu, 15 phép kiểm, hàng đợi 9/241), B2 đổi sang câu "Hoàn thành kiểm kê… BSI thẩm định", 784 kiểm thử đạt; vết ở `vet/` và `AI quantum/vet_tm_2026-11-18/`. Bản 17/11 giữ nguyên |

- Số Hòa Phát (chỉ luật): 186 tuyên bố (183 ủng hộ một phần, 3 chưa đủ bằng chứng), 55 số liệu đọc từ bảng, 15 phép kiểm bảng không phép nào lệch, 12 câu bị gắn cờ, hàng đợi 9/241 (8 tuyên bố, 1 số liệu), câu nước thải mục 6; 99–216 giây, RAM đỉnh 0,9 GB.
- Kho demo `demo_store_ban_ket/`: phiên Hòa Phát `efcd9717caef4d7b`, Hòa Phát + bộ quy tắc ngân hàng `f7290d115a5442ba`; phiên cũ (4431…, d4cf…, cb89…) chuyển vào `_phien_cu_2026-11-17/`.
- Còn để trống: link video trong báo cáo, slide, hướng dẫn (chưa có nơi đăng công khai).
- Gói chạy ngay (18/11): `goi_chay_ngay/GreenScan_chay_ngay_2026-11-18.zip`, 202,9 MB, sha256 `0aee4396d31d363ab5d6a4ef5b580755279440f43458a6a38a6b933e15d8dd3e`; dựng từ checkpoint `17f` + kho `demo_store_ban_ket` (6 phiên). Đã thử: giải nén vào thư mục có dấu và khoảng trắng, chạy `CHAY_GREENSCAN.bat`, máy chủ trả 6 phiên, phiên Hòa Phát `efcd9717caef4d7b` 186 tuyên bố / 55 số liệu / 15 phép kiểm / hàng đợi 9 trên 241. Bản 17/11 (thiếu phiên Hòa Phát vì dựng nhầm từ kho phụ của Space) đã xoá.

## 17/11/2026 tối: phân vùng trang, dựng lại video, báo cáo BTC, bản thuyết minh (D-2026-11-17-02, D-2026-11-17-03)

- **Mã:** `page-regions-v1` + `figure-tension-v1` (chi tiết mục 8 `docs/04-data-ai/KIEM_CHUNG_BANG_CLAUDE_2026-11-17.md`), cộng hai chỗ hiển thị (lý do câu tuyệt đối hiện trên hàng đợi; phép cộng bảng ghi theo đơn vị trang). **781 kiểm thử** qua; GS-Bench 0/453 nhãn đổi; evaluate-real 4/4.
- **Hòa Phát (chỉ luật):** 186 tuyên bố, 55 số liệu đọc từ bảng, 14 phép kiểm bảng (không phép nào lệch), hàng đợi **14/241**; câu “hoàn toàn không có nước thải công nghiệp xả ra môi trường” ở mục 7 (trước đây hạng 105). 216 giây, RAM đỉnh 0,9 GB. Phiên kho demo `d4cf4018876947ca` (đã đặt nhãn).
- **Video bản 5** (4 phút 47 giây): `nop_vong2/video/demo_1_phien/out/GreenScan_demo_mot_phien.mp4` (+ bản không lời, `.srt`), chép thành `nop_vong2/video/AQ2026-R2-AQ2026-119-Video_demo*.{mp4,srt}`. Video 6 phút 31 giây cũ chuyển vào `nop_vong2/video/ban_cu_2026-11-09/`. Khung hình gốc `rec5/`; kịch bản `KICH_BAN.md`.
- **Báo cáo theo mẫu BTC:** 12 trang, số mới, ảnh hàng đợi mới, độ dài video 4 phút 47 giây. Bản trước ở `nop_vong2/_cu_AQ2026119/ban_2026-11-17c/`.
- **Bản thuyết minh (báo cáo toàn văn):** `docs/09-luan-van/THUYET_MINH_HE_THONG/THUYET_MINH_HE_THONG_2026-11-17.docx`, thêm Chương 12 và đoạn cập nhật ở phần tóm tắt; chương 3–8 giữ hai phiên 14–15/11 (phân tích từng câu viết theo hai phiên đó).
- **Chưa dựng lại (mang số cũ 171, 7/186, 773):** zip mã nguồn (checkpoint `vong2_2026-11-17c`), slide, hướng dẫn, bản trực tuyến, gói chạy ngay.

## 17/11/2026 chiều: giao diện gọn, thử trên laptop, video một phiên, gói chạy ngay (D-2026-11-17-01)

Chi tiết và số đo: `docs/03-architecture/GIAO_DIEN_GON_VA_THU_MAY_2026-11-17.md`.

- **Giao diện (`next-step-v1`):** dòng “Việc tiếp theo” ở mỗi trang, trang tải tài liệu gọn, bộ mẫu “Công ty Minh Họa”, trang chi tiết “xem gọn”, hàng đợi báo xong được. Không đổi luật, kết luận, thứ tự hàng đợi.
- **Thử trên laptop:** 23/23 bước qua giao diện đạt; Hòa Phát chạy lại từ đầu qua giao diện ra 171 tuyên bố, hàng đợi 7/186 (186 giây); mô hình trên máy chạy lại không dùng bộ nhớ đệm 1.066 giây, 8/8 cặp trả lời. 773 kiểm thử qua.
- **Mã nguồn nộp:** checkpoint **`vong2_2026-11-17c`** (xem dòng “Bản trực tuyến” bên dưới; số tệp và sha256 ghi trong `CHECKPOINT.md` của thư mục đó). Đã chép vào `nop_vong2/`. Bản `17b` (sha256 `ad72091e…1c49`) là bản dùng để dựng gói chạy ngay; hai bản chỉ khác ở phần dành cho bản xem trên web. Bản 16/11 ở `nop_vong2/_cu_AQ2026119/ban_2026-11-16/`.
- **Báo cáo, hướng dẫn, slide:** dựng lại với ảnh hàng đợi theo giao diện mới và số 773 kiểm thử (12 trang, 4 trang, 19 slide).
- **Video một phiên:** `nop_vong2/video/demo_1_phien/out/GreenScan_demo_mot_phien.mp4` (3 phút 53 giây, 1920×1080, 23,5 MB), bản không lời có chú thích, tệp `.srt`. Kịch bản và nguồn từng con số: `KICH_BAN.md` cùng thư mục. Khung hình gốc để dựng lại: `rec3/` (894 MB).
- **Gói chạy ngay (`portable-v1`):** `AI quantum/goi_chay_ngay/GreenScan_chay_ngay_2026-11-17.zip`, 202,0 MB (509 MB khi giải nén), sha256 `3c04e925df5bf57c506b67eda4ae0cac77f1d67eeb81e95963630a5f1e14d982`. Dựng bằng `tools/build_portable.py` từ checkpoint trên. Đã thử trên đúng tệp zip này: giải nén vào thư mục có dấu và khoảng trắng, chạy bằng `CHAY_GREENSCAN.bat` với PATH chỉ còn thư mục Windows; 22/22 bước qua giao diện đạt; PDF chỉ có ảnh quét tiếng Việt đọc ra tuyên bố. Gói đã ẩn 12 đường dẫn máy và 13 chỗ có địa chỉ email trong `download_manifest.json`; không có khoá nào.
- **Bản trực tuyến:** đã đẩy lại 17/11 chiều lên https://chonnhan2023-greenscan-ai.static.hf.space (6 phiên, giao diện mới). Trên bản web, người mới vào thẳng danh sách phiên đã chạy sẵn và trang tải tài liệu nói rõ bản web không phân tích tài liệu mới. `tools/build_static_demo.py` nay thay đường dẫn thư mục của máy dựng bằng tên ngắn (31 chỗ). Kiểm trên trang thật: 14/14 phép kiểm đạt, không lỗi JavaScript. Lịch sử commit của Space vẫn giữ các bản cũ có đường dẫn máy.
- **Claude đọc lại ba bộ tài liệu (17/11 tối):** kết quả và điểm yếu xếp theo mức ảnh hưởng ở `docs/04-data-ai/KIEM_CHUNG_BANG_CLAUDE_2026-11-17.md`; nhãn ở `benchmark/claude_spotcheck_2026-11-17/`. Tóm tắt: văn bản sạch có số thì đúng (5/5); tài liệu thật có bảng thì bỏ sót số liệu trong bảng (Techcombank: lấy 3 trên 13 câu quan trọng), hàng đợi chưa đưa câu tuyệt đối có chỗ vênh lên đầu, so số chưa chắc cùng đại lượng. Không có kết luận “mâu thuẫn” sai. Chưa sửa gì.
- **Chưa làm / chưa thử:**
  - Nhánh tự cài Ollama trong `CAI_MO_HINH_TREN_MAY.bat` chưa chạy thử (máy này đã có Ollama); chỉ thử nhánh “đã cài”.
  - Gói chưa thử trên một máy Windows khác hẳn (chỉ mô phỏng bằng PATH tối thiểu).
  - Sáu chỗ link video trong báo cáo, slide, hướng dẫn vẫn trống.
  - Tệp `data/real_cases/sources/originals/download_manifest.json` trong zip mã nguồn còn một địa chỉ email trong chuỗi `user_agent` (13 lần); đội quyết có ẩn hay không.
  - Hòa Phát có mô hình: chờ máy GPU thuê (mục 17/11 sáng bên dưới).

## 17/11/2026 sáng: chuẩn bị chạy trên GPU thuê (vast.ai), CHƯA thuê máy

- Mục đích: chạy Hòa Phát có mô hình cùng đọc (việc dừng ở 34/171 với Groq), mang bộ nhớ đệm về laptop để phát lại khi demo.
- Thư mục: `deploy/vastai_gpu_demo/` (hướng dẫn từng bước trong `README.md`). Gói tải lên: `AI quantum/vast_bundle/greenscan_vast.tar.gz` (23,4 MB, 328 tệp, mã nguồn checkpoint `vong2_2026-11-16`, không có khoá).
- Cấu hình thuê: 1 × RTX 3090/4090 24 GB, từ 8 nhân, từ 32 GB RAM, ổ 60 GB, on-demand, Ubuntu 22.04 có CUDA.
- Đã kiểm trên laptop: cú pháp các script; 47 thư viện ghim đúng phiên bản laptop đều có bản cho Linux / Python 3.14; phép so khớp với phiên `4431e073ee1241dd`; script đo mô hình (26,2 / 9,4 / 9,7 giây trên CPU); bước nhập bộ nhớ đệm.
- **Chưa kiểm:** chạy thật trên Linux (Docker Desktop trên laptop không khởi động được engine), cài Ollama trên máy vast, tốc độ trên GPU. Bước `parity` của `10_run.sh` là chỗ phát hiện nếu Linux đọc PDF khác laptop.
- Mốc dự kiến khi chạy: có log `[cell] setup gpu` ngay; `[parity] OK` sau khoảng 15 phút kể từ lúc bắt đầu cài; Hòa Phát có mô hình chưa có số đo.

## 16/11/2026: bật mô hình khi demo, lọc bảng giả, dựng lại gói nộp (D-2026-11-16-01)

Chi tiết và số đo: `docs/03-architecture/MO_HINH_BAT_TAT_VA_LOC_BANG_2026-11-16.md`.

- **Công tắc mô hình trên giao diện** (trang Cài đặt và trang Tải tài liệu): chỉ luật / mô hình trên máy (Qwen3-4B qua Ollama) / mô hình đám mây cho tài liệu đã công bố; nút “Thử mô hình” gọi trực tiếp (32 giây trên máy, 1 giây đám mây).
- **Bộ lọc bảng giả:** Hòa Phát còn **171 tuyên bố**, hàng đợi **7/186**, 179 mục ngoài hàng đợi, 5 mẫu kiểm ngẫu nhiên; mục đầu hàng đợi nay là câu trang 7. 37 câu khớp tài liệu của chính doanh nghiệp, 134 chưa so được. **768 kiểm thử.**
- **Phiên demo** (kho `D:/Sinh viên CNhan/AI quantum/demo_store_ban_ket/`): Hòa Phát chỉ luật `4431e073ee1241dd` (cũng là phiên cài sẵn ở `deploy/seed/`); Hòa Phát + bộ quy tắc ngân hàng `7ad64e64912542f8` (hàng đợi 14, 86 “không đạt”, 77 “cần xem”); Ca A có mô hình trên máy `bddf874a95874c97`; Ca A chỉ luật `2dbe512e8d1c4237`; hai phiên Ca A ngày 14/11 của câu chuyện phản hồi.
- **Tệp nộp đã dựng lại:** báo cáo 12 trang, slide 19, hướng dẫn 4 trang (thêm đoạn bật mô hình), ảnh hàng đợi mới; zip từ checkpoint **`vong2_2026-11-16`**: 1815 tệp, 116,7 MB, sha256 `f139b5ab350548913f185ffdc1fbe40eb0d609564d9727574cfae9a7f53bda5b`. Bản cũ ở `nop_vong2/_cu_AQ2026119/ban_2026-11-15b/`.
- **Bản trực tuyến:** đã đẩy lại 16/11 (6 phiên; công tắc mô hình hiện nhưng khoá, vì là bản tĩnh).
- **Chưa xong:** lượt Hòa Phát với mô hình đám mây bị giới hạn tốc độ của gói Groq miễn phí (khoảng 1 tuyên bố mỗi phút ở bước kiểm chứng) nên đã dừng ở 34/171; phần đã hỏi nằm trong `.quantum/llm_cache/`. Chạy tiếp: `.venv/Scripts/python.exe tools/thuyet_minh/run_demo_models.py <kho demo> cloud B`. Bản thuyết minh .docx chưa dựng lại (nguồn Chương 11 đã có mục 11.6).
- **Video:** kịch bản bản 4 ở `nop_vong2/video/demo_ban_ket/KICH_BAN.md`, chờ đội duyệt rồi dựng. Sáu chỗ để trống link video vẫn chưa điền.
- **Chờ người:** duyệt kịch bản video; gán 50 câu ở `benchmark/gs_claims_v1/human/`; link video, chữ ký, khai biểu mẫu.


## 15/11/2026 tối: độ chính xác bộ trích, mẫu kiểm ngẫu nhiên, bản thuyết minh (D-2026-11-15-02)

- **Bộ trích tuyên bố:** chính xác 0,56 → **0,71** trên GS-Claims; 0,65 trên 2 báo cáo không dùng để chỉnh. Hòa Phát còn **179 tuyên bố**, hàng đợi **10/195**, cộng **5 mục kiểm ngẫu nhiên** ngoài hàng đợi. **759 kiểm thử.**
- **Tệp nộp đã dựng lại:**
  - báo cáo 12 trang, slide (slide 7 có ảnh mới, slide 15 ghi 88 "không đạt"), hướng dẫn 4 trang;
  - zip từ checkpoint **`vong2_2026-11-15b`**: 1803 tệp, 116,0 MB, sha256 `28040a4f49138ad36687160127b6c8ba68d846aed57fb6c227cfc5adfe86575f`.
- **Bản trực tuyến:** đã đẩy lại; phiên Hòa Phát `378c88974afa42b3`; có thẻ "Mẫu kiểm ngẫu nhiên".
- **Bản thuyết minh:** `docs/09-luan-van/THUYET_MINH_HE_THONG/THUYET_MINH_HE_THONG_2026-11-15.docx` (Chương 11).
- **Chờ người:** gán 50 câu ở `benchmark/gs_claims_v1/human/` (hướng dẫn `HUONG_DAN_NGUOI_GAN.md`); link video, chữ ký, khai biểu mẫu.

## 15/11/2026: làm hai đợt của kế hoạch V2 sau góp ý chuyên gia, dựng lại cả 4 tệp và bản trực tuyến

Chi tiết và mọi số đo: `docs/03-architecture/CAI_TIEN_SAU_GOP_Y_2026-11-15.md` (D-2026-11-15-01).

**Hiện trạng gói nộp** (`nop_vong2/`; bản cũ ở `_cu_AQ2026119/`):

| Tệp | Trạng thái |
|---|---|
| Báo cáo | 12 trang. Số mới: GS-Bench 0,27 / 0,85; GS-Mutation; mốc LLM có cột luật + cờ LLM; dòng GS-Claims; dòng tập giữ riêng. Hòa Phát 199 tuyên bố, hàng đợi 10/215, hai trục; 757 kiểm thử; ảnh hàng đợi mới. Nguồn trước khi sửa: `src_baocao/baocao_ban_2026-11-15_truoc_v2.tex` |
| Slide | 19 slide. Đã sửa slide 7 (199 tuyên bố, 10/215, hai trục, ảnh mới), slide 13, slide 15 (96 “không đạt”, 79 “cần xem”) |
| Hướng dẫn | 4 trang. Kịch bản kiểm: bước 1–3 (199/198/0/1, 10/215, mục #2 và ba nhãn), bước 7 (hàng đợi 17), 757 kiểm thử |
| Zip | Checkpoint **`vong2_2026-11-15`**: 1796 tệp, 115,1 MB, sha256 `ec88ec822bfc880687fb513c08bcd93c2362ec882ea66fa0400478e73564754d`. Không có PDF trái phiếu xanh của bên thứ ba, không có tệp bí mật |
| Bản trực tuyến | Đã đẩy lại https://chonnhan2023-greenscan-ai.static.hf.space, kiểm bằng trình duyệt không giao diện: 0 lỗi JavaScript, 0 request hỏng. Có 5 phiên: Hòa Phát (15/11), Hòa Phát + bộ quy tắc ngân hàng, Ca A lượt 1 và 2 (14/11, câu chuyện tiền lệ), Ca A chạy lại 15/11 (máy tự bắt A2) |
| Phiên mẫu cài sẵn | `deploy/seed/` thay bằng phiên Hòa Phát `fbfd7b5a7b7e4e88`; phiên cũ chép ra thư mục tạm |

**Vẫn còn của đội:** link video, chữ ký, khai link prototype trên biểu mẫu. Bản thuyết minh .docx chưa cập nhật các số của ngày 15/11.

## Khuya 14/11/2026: làm theo `KE_HOACH_THEO_STAGE.md`, dựng lại cả 4 tệp

Chi tiết từng mục, cách đo và quyết định: `docs/03-architecture/ABSOLUTE_AND_INTERNAL.md` (D-2026-11-14-05).

**Luật mới bật mặc định:**
- `absolute-share-v1`: A2 → CONTRADICTED, lý do 320/500 = 64%.
- `figure-consistency-v1`: cùng số mà ngược hướng → mâu thuẫn; câu có hai số, một số lệch xa → PARTIAL.
- Cụm mạnh "chưa phân bổ / giải ngân / sử dụng / hoàn thành" → PARTIAL, gắn cờ và đưa vào hàng soát.
- `comparison-policy-v3`: thêm chiều mảng kinh doanh.
- Chốt "Scope 3" không còn bị coi là số bịa.

**Đã làm nhưng để tắt:** mâu thuẫn nội bộ (`internal_inconsistency`). **Bỏ:** học lại trọng số rubric.

**Số đo:**
- GS-Bench: đúng 24 → 26 trên 35 kết luận (0,686 → 0,743); "ủng hộ" sai 10 → 8; "mâu thuẫn" sai giữ 1.
- GS-Mutation v1 (865 ca, mới):
  - vu oan 0/290;
  - đảo hướng bắt 0/17 → 5/17;
  - ca cài lỗi vẫn "ủng hộ" 10 → 5.
- Mốc gpt-oss-120b đọc thẳng (183 ca test):
  - bắt phóng đại số 47/72, trong khi luật bắt 9/72;
  - nhưng vu oan 1/75, 5 ca lỗi vẫn "ủng hộ", và 16% câu trả lời đổi giữa hai lần hỏi.
- evaluate-real không đổi. Hòa Phát không đổi (154/1/1).
- Kiểm thử: **743 passed**.

| Tệp | Thay đổi |
|---|---|
| Báo cáo (12 trang) | Bảng 3.4 thêm hai dòng: GS-Mutation và mốc LLM. GS-Bench 0,74. Cổng so sánh nói thêm về mảng, ngược hướng và tỷ trọng. Mục giới hạn thêm "nút thắt là bước trích" và "luật nội bộ để tắt"; A2 đã sửa. Ghi 743 kiểm thử. Nguồn: `src_baocao/baocao.tex`; bản trước: `baocao_ban_2026-11-14_truoc_stage.tex` |
| Slide (19) | Slide 13: 743 kiểm thử, GS-Bench đúng 74%, bộ cài lỗi. Đã xuất ảnh để soát: không tràn |
| Hướng dẫn (4 trang) | Ghi 743 kiểm thử |
| Zip | Checkpoint **`vong2_2026-11-14d`**: 1768 tệp, 114,9 MB, sha256 `f41b69a27fce9cb3e1d558b2e9b485f081377c3d9099b7d114f76c3d5e24d357` (bản `-14c` cùng mã, tài liệu cũ hơn). Bản cũ ở `_cu_AQ2026119/` |
| Bản tĩnh trên HF | **Chưa dựng lại.** Phiên "Ca mẫu A" trên đó là bản chạy sáng 14/11, khi A2 còn "ủng hộ một phần" và người soát ghi đè sang "mâu thuẫn" (ví dụ tiền lệ). Vẫn đúng như một phiên lịch sử |

## Tối 14/11/2026: gói nộp đã đủ 4 tệp + link prototype

| Yêu cầu BTC | Trạng thái |
|---|---|
| Báo cáo 8–12 trang, đúng mẫu | `nop_vong2/AQ2026-R2-AQ2026-119-Bao_cao_giai_phap.pdf`, **12 trang**. Cập nhật: 729 kiểm thử, hàng đợi 8/172 (phiên chạy lại 14/11), org pack tự phục vụ, vòng học từ phản hồi (kết quả đo thật: cụm đề xuất 0 đổi trên 453 ca, mô hình thách đấu bị cổng chặn), nhãn GS-Eval ghi rõ nguồn gốc (Claude gán theo bộ quy tắc, tác giả rà soát), ảnh hàng đợi mới, link prototype. Nguồn `src_baocao/baocao.tex` (bản cũ `baocao_ban_2026-11-10.tex`) |
| Slide | `AQ2026-R2-AQ2026-119-Slide.pptx`, **19 slide** (thêm slide 15 “Mỗi tổ chức một bộ quy tắc, mỗi lần soát là một bài học”); số liệu và link cập nhật. Dựng: `NODE_PATH=<thư mục có pptxgenjs> node src_slide/build_deck.js` |
| Mã nguồn zip | `AQ2026-R2-AQ2026-119-Ma_nguon.zip` từ checkpoint **`checkpoint_nop_bai/vong2_2026-11-14b/`** (1748 tệp, 114,7 MB, sha256 `2a4ec25b8fd7bf3ab38e09e55fe4d3e5fcab60e26d7a8319abee7b165fda9a4d`, 729/729 kiểm thử) |
| Hướng dẫn | `AQ2026-R2-AQ2026-119-Huong_dan.pdf`, 4 trang: link bản tĩnh, không cần tài khoản, kịch bản kiểm 8 bước (thêm org pack và tiền lệ), số liệu 14/11 |
| **Link prototype** | **https://chonnhan2023-greenscan-ai.static.hf.space** (Space `chonnhan2023/greenscan-ai`, static, miễn phí, không ngủ). Đội chọn bản tĩnh ngày 14/11 vì Hugging Face đòi gói PRO cho Space Docker (HTTP 402). Bản tĩnh = giao diện thật + phản hồi API xuất nguyên văn từ máy chủ thật (`tools/build_static_demo.py`, lớp giả lập `frontend/src/staticApi.js`) trên 4 phiên: Hòa Phát; Hòa Phát + bộ quy tắc “Ngân hàng Xanh”; Ca mẫu A lượt 1 (đã soát) và lượt 2 (tiền lệ). Quyết định soát lưu trong trình duyệt; phân tích mới trả lời “cần bản cài đặt”. Đã kiểm bằng Chromium không giao diện trên link thật: 0 yêu cầu lỗi |
| Link video | **Còn trống theo ý đội** (chưa chọn video). Video 6:31 đã có trên Drive `AIquantum` (`AQ2026-R2-AQ2026119-Video_demo.mp4`, id `16XPUvvKsGyhMlgwrM3AAdWBFTPpY6rFy`) nhưng **chưa bật chia sẻ**; chọn xong thì điền 3 chỗ `\can{URL}` trong báo cáo, 1 chỗ trong hướng dẫn, 2 chỗ “[điền link]” trong slide rồi dựng lại |

**Còn phải làm tay:** chữ ký đại diện trên báo cáo; khai link prototype trên biểu mẫu nộp; link video. Muốn bản trực tuyến chạy phân tích mới thì cần Space Docker (gói PRO 9 USD/tháng): `python tools/deploy_hf_space.py --space chonnhan2023/greenscan-ai --demo-users "giamkhao:<mật khẩu>"` (token ghi ở `~/.kaggle/flag_secrets.env`, biến `HF_TOKEN_WRITE`).

**Dựng lại bản tĩnh** (sau khi sửa mã hoặc thêm phiên): `.venv/Scripts/python.exe -I tools/build_static_demo.py --out <thư mục> --demo-store <tmp của run_feedback_demo>` rồi đẩy bằng `C:/Python314/python.exe tools/build_static_demo.py --out <thư mục> --skip-build --deploy chonnhan2023/greenscan-ai` (cần `HF_TOKEN`).

---

# (cũ) Trạng thái ngày 10/11/2026

> **14/11/2026: mã nguồn nộp bài lấy từ checkpoint, không lấy từ repo** (D-2026-11-14-01).
> Thư mục `D:/Sinh viên CNhan/AI quantum/checkpoint_nop_bai/vong2_2026-11-14/`: bản sao 1710 tệp, `MANIFEST.txt` (sha256 từng tệp), `CHECKPOINT.md`, và zip `AQ2026-R2-AQ2026-119-Ma_nguon.zip` (113,2 MB, sha256 `0a09a1367f00d9074b5e9dc6e5014d9a0099254fd93e632060e0742796d8af57`, 654/654 kiểm thử qua). Zip cũ 78,3 MB ngày 10/11 trong `nop_vong2/` đã cũ hơn checkpoint. Zip lớn hơn chủ yếu vì `deploy/vastai_a100/` (44 MB), `benchmark/` và `out/` mới; có cắt bớt thì chốt checkpoint mới bằng `tools/make_checkpoint.py --name <tên mới>`.

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
