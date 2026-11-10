# Danh mục thông tin cần thu thập cho bài nghiên cứu hoàn chỉnh về GreenScan

*Lập 31/10/2026.*

**Mục đích:** gom đủ nguyên liệu để viết một bài nghiên cứu đạt bốn yêu cầu:
- ngôn ngữ chuẩn mực;
- mỗi phần nhỏ của hệ thống có chuỗi suy luận "vấn đề → giả thuyết → phương pháp → kết quả → giới hạn → kết luận → hướng phát triển";
- mọi khẳng định có nguồn;
- được đánh dấu bằng một trong bốn nhãn: **[ĐÃ THỰC NGHIỆM]** (số của đội, kèm n và đường dẫn), **[KIẾN THỨC NỀN]**, **[NGOÀI]** (tài liệu, paper, kèm trích dẫn), **[GIẢ THUYẾT]**.

**Nơi lưu:** mỗi phần một hồ sơ `Pxx_<tên>.md` trong thư mục này. Chỗ còn thiếu ghi **THIẾU: …**, kèm cách lấy.

## A. Phần chung của bài

| # | Thông tin | Nguồn dự kiến |
|---|---|---|
| A1 | Bối cảnh: tẩy xanh ở Việt Nam và thế giới; quy định (Luật BVMT 2020, NĐ 06/2022, QĐ 13, TT 96, chuẩn ISSB/GRI); các vụ đã xử lý | `docs/08-knowledge/`, `docs/01-domain-audit/`, `data/real_cases/` |
| A2 | Phát biểu bài toán, người dùng (kiểm toán viên, cơ quan quản lý, doanh nghiệp), câu hỏi nghiên cứu | `docs/00-project/`, `docs/02-product/` |
| A3 | Công trình liên quan: ClimateBERT, ClimRetrieve, Climate-FEVER, MiniCheck, LLM-AggreFact, FinQA, DS-STAR, ESG verification | `docs/08-knowledge/05_AI_NLP_VA_DO_LUONG.md`, `docs/research/`, `GreenScan_AI_Research_Source_Pack_2026-08-13/` |
| A4 | Mười bất biến kiến trúc và lý do (lỗi thật đã gặp) | `docs/00-project/ARCHITECTURE_INVARIANTS.md` |
| A5 | Nhật ký quyết định (D-…) | `docs/00-project/DECISIONS_LOG.md` |
| A6 | Thể lệ, tiêu chí chấm vòng 2, mốc thời gian | file thể lệ PDF, `docs/07-presentation/` |
| A7 | Lịch sử phát triển và các lỗi lớn đã sửa (14 lỗi verdict tháng 9, 357/419 mâu thuẫn sai ngày 17/09, sửa 22/10) | `ISSUES_REGISTER_2026-09.md`, `benchmark/*`, memory |
| A8 | Thuật ngữ | `docs/00-project/GLOSSARY.md` |

## B. Hồ sơ cho từng phần của hệ thống

Mỗi hồ sơ trả lời đủ 10 câu:
1. phần này giải quyết vấn đề gì;
2. lỗi hay rủi ro nào đã đo được;
3. thiết kế hiện tại, file code, cấu hình;
4. vì sao chọn, phương án đã bỏ và vì sao;
5. số đo có n và đường dẫn;
6. giới hạn và yếu tố gây nhiễu;
7. lỗi đã gặp và cách gỡ;
8. trạng thái năng lực: PROVEN / IMPLEMENTED–NOT VALIDATED / RESEARCH-BACKED–NOT IMPLEMENTED / OPEN QUESTION;
9. hướng phát triển và thí nghiệm kế tiếp;
10. hình nên vẽ và file dữ liệu để vẽ.

| Mã | Phần | Điểm cần chú ý |
|---|---|---|
| P01 | Tiếp nhận và đọc tài liệu (PDF, Office, OCR tiếng Việt) | Tesseract `vie` sửa 22/10; tài liệu loại A/B/C; bảng dàn phẳng |
| P02 | Nhận diện tuyên bố (T1: luật, học trò e5) | macro-F1 trên nhãn Claude; gold người = 0; quy trình gán nhãn |
| P03 | Chuẩn hoá tuyên bố → IR (AG-1) | GS-Bench v1; thang model Kaggle; oracle 0,528 |
| P04 | Truy xuất bằng chứng (lite BM25 + char n-gram RRF; dense / rerank) | RETRIEVAL_POLICY; câu hỏi v3 C1 / C2 |
| P05 | Kiểm chứng định lượng (`numeric_facts`, cộng ngang, dung sai theo độ chính xác công bố, `irlib`) | 17 bẫy xanh; size ladder; F1–F13 |
| P06 | Đọc lập trường bằng LLM (có chốt, `decisive=false`) | A/B ngày 28/09; GLM-5.2; offline và cloud lệch 3/156 |
| P07 | Pháp lý: gói luật, khả năng áp dụng (applicability) | 0 quy tắc áp được; luật do người viết; `legal/` |
| P08 | Rủi ro và hàng đợi ưu tiên (`priority-v1.1`) | Verdict ≠ risk ≠ priority; queue_quality |
| P09 | Quy trình người soát, giấy làm việc, Studio | Luồng 4 bước; DOCX theo dõi thay đổi |
| P10 | Quyền riêng tư, ngoại tuyến, che số (L1), hồ sơ chạy | 0 kết nối ra ngoài; che số không giấu được danh tính 5/20; mục `groq` |
| P11 | Dữ liệu: kho câu, doanh nghiệp, nguồn, nhãn | 66 539 câu; 20 DN; 2 055 nhãn Claude; GS-Bench |
| P12 | Đo lường: giao thức, ngưỡng đăng ký trước, bootstrap | `MEASUREMENT_PROTOCOL`, `measurement_decisions.yaml` |
| P13 | Huấn luyện học trò và Kaggle | `training/`, `kaggle_t1_v1..3`, AG-4 |
| P14 | Vận hành: hiệu năng, phần cứng, tái lập, manifest | 107–121 s HPG; 1 331 MB; test bất biến |
| P15 | Chương trình agent (mượn từ ZAIC: AG-0…AG-6), hai đường + cổng đồng thuận | kế hoạch 31/10; kết quả AG-1 / AG-2 thử |

## C. Những thứ chắc chắn còn thiếu (phải có người làm)

- **Gold người:** lô 1 T1 (79 câu × 3 người) và 40/88 cặp. Không có thì mọi số ở P02, P03 và P05 chỉ là nhãn bạc.
- **Chuyên gia đánh giá phát hiện** (v3 E4): giảng viên kiểm toán và Thảo.
- **Quy tắc pháp lý có `reviewed_by`:** cho phát thải, BVMT, phân loại xanh (Thảo).
- **Hình chụp màn hình** của luồng 4 bước, cho phần P09.
