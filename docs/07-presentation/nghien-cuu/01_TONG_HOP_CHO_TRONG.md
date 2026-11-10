# Tổng hợp các chỗ còn trống (THIẾU)

*Lập 31/10/2026 từ các hồ sơ A_CHUNG và P01–P15. Mỗi mục ghi nội dung còn thiếu, cách lấy và file liên quan. Mục không ghi tên người trong nguồn được xếp vào "Team".*

## Thảo (pháp lý, taxonomy)

- Quy tắc pháp lý có `reviewed_by` cho phát thải, BVMT và phân loại xanh. Cách lấy: duyệt `configs/legal/rule_pack_vn_green_v0.1.yaml` và ghi trường `reviewed_by` (P07; checklist mục C).
- Xác nhận 8 chỗ cũ hoặc thiếu của tài liệu 02 trước khi sửa (P07; `docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`, mục 0).
- Nội dung Luật BVMT 2020, QĐ 13, ISSB/GRI, các vụ đã xử lý tại Việt Nam. Cách lấy: đọc `docs/08-knowledge/02_PHAP_LY_VIET_NAM.md` mục 1–2 và `04_AN_LE_VA_BAI_HOC.md` mục 1 (A_CHUNG, A1).
- Đánh giá phát hiện (v3 E4), cùng giảng viên kiểm toán. Cách lấy: lập lịch đánh giá với giảng viên (P09; checklist mục C).
- Gold người lô 1 T1 (79 câu, ba người) (P02, P13): xem mục Quỳnh, Thảo, Nhân.

## Quỳnh (nghiệp vụ kiểm chứng, gán nhãn)

- Thứ tự hàng đợi cần nhãn để đo độ chính xác. Cách lấy: Quỳnh soát mẫu ngẫu nhiên (P08, mục 6).
- Số người soát và thời gian soát làm tay, RQ10. Cách lấy: bài đo thời gian theo `docs/06-operations/HANDOFF_2026-09-25.md` (Quỳnh, việc 3) (P09, mục 5).
- Gold người lô 1 T1 (79 câu × 3 người) và 40/88 cặp còn lại. Cách lấy: Quỳnh, Thảo, Nhân gán độc lập theo lịch trong `docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`, mục 10 (P02, P06, P13).

## Nhân (kỹ thuật, mô hình, thí nghiệm)

- Chọn mô hình theo công đoạn: tệp `CHON_MO_HINH_THEO_CONG_DOAN_2026-10-16.md` không có trong repo. Cách lấy: hỏi Nhân về vị trí, hoặc đọc khối `model-selection-v2` trong `configs/measurement_decisions.yaml` (P02).
- Xác nhận ngưỡng đăng ký trước cho T1 (`QUY_TRINH_GAN_NHAN_T1`, mục 9) (P02).
- Kết quả đo truy xuất RQ4, RQ5 (Recall@k, MRR, nDCG). Cách lấy: chạy `tools/measure_all.py` khi có gold (P04, P12).
- Thống nhất số bẫy xanh: 17 (checklist và YAML), 44 (bất biến 4), 47 hàm trong `test_verdict_traps.py`. Cách lấy: đếm lại và ghi một con số duy nhất (P05).
- Số bài test bất biến: tài liệu ghi 14, tệp có 15. Cách lấy: `pytest --collect-only` (P14).
- Đưa che số L1 vào đường gọi mô hình trước khi bật `on_ambiguous` (P10).
- Thời gian huấn luyện T1 trên T4 cho 10.000 mẫu. Cách lấy: đo 200 bước rồi ngoại suy (P13).
- Chạy `eval_student.py` trên gold và 51 ca (P13).
- Kết quả AG-0 và AG-2 đến AG-6; kết quả lượt B của AG-1 (P03, P15).
- Tệp `out/score_ag1.json` ghi trong phiếu AG-1 nhưng không có trong thư mục. Cách lấy: tạo lại bằng `experiments/score.py` (P03).
- Số "2 055 nhãn Claude" trong checklist; nguồn đã đọc chỉ có 498 + 79 câu. Cách lấy: đếm trong `training/data/` (P11).
- Giải thích sự khác nhau giữa 21 doanh nghiệp (kho) và 15 doanh nghiệp (tệp chia) (P11).
- Nguồn con số 25 % cho luật trong kế hoạch AG-2, khác với 2,8 % đo trên B-b (P15).

## Team (chưa ghi người phụ trách trong nguồn)

- Kết quả đo độ chính xác OCR tiếng Việt trên mẫu trang scan có đáp án tay (P01).
- Hình trang tài liệu được tô sáng và hình chụp màn hình luồng 4 bước (hoặc 3 bước, sau khi chốt) (P01, P09; checklist mục C). Thư mục `docs/07-presentation/screenshots_ui_2026-10-15/` có sẵn, chưa đọc.
- Chốt một cách gọi cho luồng: 3 bước (D-2026-10-06-01) hay 4 bước (checklist) (P09).
- Đo lại thời gian trên máy trình chiếu trước 17/10 (P14).
- Nội dung thể lệ và tiêu chí chấm vòng 2 trong file PDF thể lệ (A6).
- Nội dung `docs/00-project/PROBLEM_DEFINITION.md`, `docs/02-product/`, và ba nhóm người dùng (A2).
- Các công trình liên quan (ClimateBERT, ClimRetrieve, Climate-FEVER, MiniCheck, LLM-AggreFact, FinQA, DS-STAR) (A3; Nhân đọc mục 05 theo README kho).
- Con số "14 lỗi tháng 9", "357/419 mâu thuẫn sai ngày 17/09", "sửa 22/10" (A7).
- Mục J–Z của `GLOSSARY.md` (A8).
- Ngưỡng bật L1 và ba nấc ngoại tuyến (P10, mục 1 và 8 của tài liệu OFFLINE).
- Kết quả offline so với cloud "lệch 3/156" (P06).
- Gold verdict 100–200 claim. Chưa ghi người phụ trách (P05, P11).
- Quyết định của người dùng ngày 31/10 (mục 9 của kế hoạch agent) (P15).
- Nội dung `docs/06-operations/SECURITY_AND_GOVERNANCE.md` (chỉ 11 dòng, chưa đọc) (P14).
- Lượt B của AG-1 (8B, 14B, gemma) còn chạy (P03, P15).
- Đọc 7 ca CONTRADICTED sai và 4 ca SUPPORTED sai của 32B để tách lỗi đọc với lỗi `irlib` (P03).

## Mâu thuẫn cần thống nhất trước khi báo cáo

1. Số bài test bất biến: 14 (tài liệu) so với 15 (tệp).
2. Số bẫy xanh: 17, 44 và 47.
3. Số doanh nghiệp: 21 (kho) so với 15 (tệp chia).
4. Luồng sản phẩm: 3 bước (quyết định) so với 4 bước (checklist).
5. AG-1: cấu hình liệt kê 8B, 14B và gemma; kết quả chỉ có 32B.
6. AG-2 ghi luật đạt độ phủ 25 %, AG-1 đo 2,8 %.
7. Số nhãn Claude: 2 055 (checklist) so với 498 + 79 (quy trình).

## Đối chiếu số mâu thuẫn (phiên chính kiểm, 31/10/2026)

| Mục | Kết quả kiểm | Cần làm |
|---|---|---|
| Số test | `tests/test_verdict_traps.py` có 47 hàm `test_`; `tests/test_architecture_invariants.py` có 15. Con số "14 test bất biến" trong D-2026-09-25-01 là số cũ, nay đã thêm một test | Nếu muốn giữ con số "17 bẫy xanh", phải ghi rõ đó là tập con nào |
| Nhãn Claude 2.055 | Có thật: `training/data/t1/train_claude.jsonl` có 2 055 dòng. File nằm trong `training/data/`, thư mục gitignore, nên subagent không thấy | — |
| `CHON_MO_HINH_THEO_CONG_DOAN_2026-10-16.md` | Không có trong repo, dù D-2026-10-16-01 có nhắc tới | Tìm ở thư mục cũ, hoặc ghi là chưa viết |
