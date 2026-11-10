# Phần chung của bài (A1–A8)

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** tài liệu nội bộ, mô tả thiết kế đã cài, chưa đo · **[NGOÀI]** tài liệu bên ngoài, trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán hoặc câu hỏi nghiên cứu. Đường dẫn tính từ thư mục gốc repo.

## A1. Bối cảnh

- Kho tri thức có sáu tài liệu (01–06) và ba tệp nguồn, lập 06/10/2026 từ ba đợt nghiên cứu 05–06/10/2026 **[KIẾN THỨC NỀN]** (`docs/08-knowledge/README.md`).
- Kho ghi 21 mẫu hình tẩy xanh và mức GreenScan kiểm được từng mẫu hôm nay **[KIẾN THỨC NỀN]** (`docs/08-knowledge/01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md`, mục 2).
- Registry pháp lý có 12 văn bản, ngày hiệu lực đã đối chiếu bản ký **[KIẾN THỨC NỀN]** (`docs/08-knowledge/02_PHAP_LY_VIET_NAM.md`, mục 1).
- Có 31 nghiên cứu về Việt Nam **[KIẾN THỨC NỀN]** (`docs/08-knowledge/03_THUC_TRANG_VA_NGHIEN_CUU_VN.md`, mục 2) và 32 vụ thực thi hoặc tòa án quốc tế 2021–2026, cùng 9 bài học **[KIẾN THỨC NỀN]** (`docs/08-knowledge/04_AN_LE_VA_BAI_HOC.md`).
- Ràng buộc: NĐ 06/2022 đã sửa hai lần trong 9 tháng; TT 96/2020 có dự thảo thay thế lấy ý kiến tới 07/10/2026 **[KIẾN THỨC NỀN]** (`docs/08-knowledge/README.md`, quy tắc 1).
- THIẾU: nội dung Luật BVMT 2020, QĐ 13, chuẩn ISSB/GRI và các vụ đã xử lý tại Việt Nam. Cách lấy: đọc `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md` mục 1–2 và `04_AN_LE_VA_BAI_HOC.md` mục 1. Lượt này chỉ đọc tiêu đề các tệp đó.

## A2. Bài toán, người dùng, câu hỏi nghiên cứu

- Đơn vị kiểm là **tuyên bố** (claim), không phán xét doanh nghiệp **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 1).
- Câu hỏi làm trục: với tuyên bố này, hệ thống đã tìm bằng chứng nào, phép tính nào đã chạy, quy tắc nào áp dụng, và phần nào còn chưa biết **[KIẾN THỨC NỀN]** (cùng file, phần đầu).
- Mốc thi: prototype 25/08–10/10/2026; Bán kết 25/10/2026; Chung kết 10/11/2026 **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-01).
- Câu hỏi nghiên cứu đề xuất: có thể tách khâu đọc (mô hình nhỏ điền IR) khỏi khâu tính (mã tất định) để tăng độ phủ kết luận mà không tăng kết luận sai hay không **[GIẢ THUYẾT]** (`experiments/AG-1/README.md`, mục 2).
- THIẾU: định nghĩa bài toán và ba nhóm người dùng (kiểm toán viên, cơ quan quản lý, doanh nghiệp). Cách lấy: đọc `docs/00-project/PROBLEM_DEFINITION.md` và `docs/02-product/`. Các tệp này nằm ngoài danh sách của lượt này.

## A3. Công trình liên quan

- Tệp `docs/08-knowledge/05_AI_NLP_VA_DO_LUONG.md` chỉ được đọc tiêu đề: tài nguyên tiếng Việt kèm giấy phép, cảnh báo về GreenScan, đo trên gold 60–100 cặp, mô hình nhỏ thay LLM **[KIẾN THỨC NỀN]**.
- Ribeiro và cs., ACL 2020 (CheckList): kiểm từng năng lực bằng ca có đáp án biết trước **[NGOÀI]** (trích theo `docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 2).
- Aarnes & Setty 2026 (arXiv:2610.00689): tinh chỉnh QLoRA mô hình 0,6–8B vượt mô hình frontier **[NGOÀI]** (trích theo `docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`, mục 2; xem thêm `training/README.md`, mục 4).
- Tự tin theo hai đường độc lập đạt AUROC 0,82, so với 0,61–0,68 của tự nhất quán **[NGOÀI]** (trích theo `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 3).
- THIẾU: ClimateBERT, ClimRetrieve, Climate-FEVER, MiniCheck, LLM-AggreFact, FinQA, DS-STAR, các công trình ESG verification. Cách lấy: đọc `05_AI_NLP_VA_DO_LUONG.md` mục 1–5 và thư mục `GreenScan_AI_Research_Source_Pack_2026-08-13/`.

## A4. Mười bất biến kiến trúc

Bảng đầy đủ nằm ở `docs/00-project/ARCHITECTURE_INVARIANTS.md` **[KIẾN THỨC NỀN]**. Tóm tắt:

Ba nhóm chính: kiểm tuyên bố chứ không phán xét doanh nghiệp (1–2); tách tìm kiếm, tính toán và kết luận (3–5); xử lý thiếu dữ liệu và tái lập (6–10). Mỗi bất biến có một lỗi thật làm nền. Ví dụ: 5/8 mâu thuẫn sai ngày 22/09 thuộc loại so khác Scope, tập đoàn với nhà máy, tuyệt đối với cường độ **[ĐÃ THỰC NGHIỆM]** (cùng file, bảng "Những điều từ nay không được làm").

Lưu ý sai khác: tài liệu ghi 14 test canh; tệp `tests/test_architecture_invariants.py` có 15 hàm `def test_` **[ĐÃ THỰC NGHIỆM]** (đếm bằng grep).

## A5. Nhật ký quyết định

- Bảng `DECISIONS_LOG.md` có 24 quyết định, từ D-2026-09-18-01 đến D-2026-10-16-01 **[ĐÃ THỰC NGHIỆM]** (đếm bằng grep, `docs/00-project/DECISIONS_LOG.md`).
- Ví dụ: D-2026-09-22-05 cấm nói "độ chính xác X%" khi gold chưa đạt 60 và chưa có hold-out theo doanh nghiệp. D-2026-10-16-01 chọn mô hình theo công đoạn bằng số đo, đăng ký trước.

## A6. Thể lệ và mốc thời gian

- THIẾU: nội dung thể lệ và tiêu chí chấm vòng 2. Cách lấy: đọc file PDF "Thể lệ Cuộc thi…" trong thư mục `docs/` (lượt này chưa đọc).
- Mốc đã biết: product freeze 10/10, presentation freeze 25/10 **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-01).

## A7. Lịch sử phát triển và lỗi lớn

- Mục N của `docs/00-project/ISSUES_REGISTER_2026-09.md` ghi lỗi verdict phát hiện ngày 22/09; mục B ghi độ tin cậy verdict **[KIẾN THỨC NỀN]**.
- Lỗi chuẩn hoá đã đo: 5 lỗi (cường độ với tuyệt đối, công ty mẹ với tập đoàn, ngưỡng 0,35 che chênh 9–25 %, bỏ sót "sử dụng … nước", không cộng ngang tổng) **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2, F4).
- THIẾU: "14 lỗi verdict tháng 9", "357/419 mâu thuẫn sai ngày 17/09" và "sửa 22/10". Tìm bằng grep trong `ISSUES_REGISTER_2026-09.md` không thấy các con số này. Cách lấy: đọc mục B và N (dòng 26–75) của tệp đó, rồi thư mục `benchmark/` và ghi chú phiên.

## A8. Thuật ngữ

- `docs/00-project/GLOSSARY.md` có các mục A–I, ví dụ Audit trail, BM25, Claim, Contradicted, Evidence card, Evidence-first, Greenwashing, GRI Standards, Human review **[KIẾN THỨC NỀN]**.
- Chưa có trong GLOSSARY: IR (biểu diễn trung gian), độ phủ, precision trên phần dám kết luận. AG-1 ghi là "sẽ thêm" **[KIẾN THỨC NỀN]** (`experiments/AG-1/README.md`, mục 8).
- THIẾU: các mục J–Z của GLOSSARY, vì lượt này chỉ đọc tiêu đề tới mục I. Cách lấy: đọc toàn bộ `docs/00-project/GLOSSARY.md`.
