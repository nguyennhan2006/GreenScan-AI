# Kết quả GS-Issue và dữ liệu bù (11/11/2026)

Tài liệu dành cho đội. Dự đoán được đăng ký lúc 09:45 (`configs/measurement_decisions.yaml`, khối `gs_issue_v1`), trước khi có hệ thống nào đọc ca. Bảng đầy đủ do máy sinh nằm ở `benchmark/gs_issue/results/SCORE_ISSUE.md`; biểu đồ ở `benchmark/gs_issue/results/figs/`.
Phần mô hình (Qwen3 4B, 8B, 14B, 32B và hệ lai) **đang chạy trên Kaggle**, dự kiến xong khoảng 10:25. Khi xong, chạy `bash benchmark/gs_issue/ingest.sh` rồi điền mục 3.

## 1. Luật hiện có của GreenScan (studio.suggest), đo trên máy

| | Lớp A (đáp án có sẵn) | D-EDIT (nhãn Claude) |
|---|---|---|
| macro-F1 tìm lỗ hổng (14 mã) | **0,27** [0,26; 0,29] | 0,26 [0,24; 0,34] |
| Bắt câu cần sửa | 1,00 | 1,00 |
| **Báo nhầm câu sạch** | **1,00** (120/120) | — |
| Sửa đúng (gỡ lỗi, giữ số, không bịa số), ca một lỗi | 0,53 [0,49; 0,57] | — |
| Bịa số | 0 | 0 [0; 0,025] |
| Sửa đúng chỗ trống trên câu thật | — | 0,84 [0,78; 0,88] (n 212) |

Ba điều đọc được từ bảng:
- **Luật bắt mọi câu, kể cả câu sạch.** Lý do là luật "thiếu dẫn nguồn" (EV-02) luôn bật, và luật thiếu năm gốc không nhận ra cụm "so với năm gốc 2021". Vì thế recall trông rất cao nhưng không có giá trị phân biệt.
- **Năm loại lỗ hổng nằm ngoài từ vựng của luật, recall bằng 0:** mục tiêu nói như đã đạt, chứng nhận không nêu bên cấp, che mặt xấu, khoe nghĩa vụ luật định, dùng cường độ thay tổng. MISSING_PERIOD chỉ bắt được 0,14 và ABSOLUTE_CLAIM 0,26.
- **Luật không bao giờ bịa số.** Đây là ưu điểm phải giữ khi thêm mô hình.

## 2. Chấm rủi ro và kết luận trên dữ liệu bù (chạy toàn bộ pipeline, hồ sơ ngoại tuyến)

- **Cặp song sinh** (cùng một câu, bản sạch và bản có lỗi). Có 55/80 cặp mà cả hai bản đều được trích:
  - điểm ưu tiên tăng ở **18 %** số cặp [10 %; 30 %];
  - **không đổi ở 78 %**;
  - điểm trung bình của bản sạch là 52,4, của bản có lỗi là 53,0.
  - Bộ chấm phản ứng với "thiếu năm gốc" (5/5 cặp) và với "trung hòa nhờ tín chỉ" (5/7). Nó không phản ứng với tuyệt đối hoá, mục tiêu như thành tích, cường độ thay tổng, từ mơ hồ, che mặt xấu.
  - 62 % bản có lỗi nặng vẫn rơi vào dải cao, nhưng đó là vì bản sạch vốn đã ở mức khoảng 50. Điểm không tách được câu có lỗi khỏi câu sạch.
- **Kết luận C/S trên phần bù** (50 ca C, 35 ca S từ GS-Bench):
  - recall C = 0 [0; 0,07], recall S = 0,11 [0,05; 0,26];
  - không có kết luận dứt khoát sai nào;
  - không có lời giải thích nào nêu số của tuyên bố hoặc số của bằng chứng.
  - Hệ thống vẫn cẩn trọng (không vu oan), nhưng trên những ca này nó chưa hữu ích.
- **Bộ trích:** bỏ qua 22/80 câu sạch song sinh và 50/85 câu GS-Bench khi các câu này đứng một mình. Lỗi tập trung ở chỉ số "nhiên liệu hóa thạch" (9/13) và "lượng nước tiêu thụ" (9/14). Mã HEAD cho kết quả y hệt.

## 3. Mô hình và hệ lai (điền sau khi Kaggle xong)

Bảng macro-F1, báo nhầm, sửa đúng, bịa số cho q3-4b, q3-8b, q3-14b-awq, q3-32b-awq, hybrid và các bản `+guard`; đối chiếu từng dự đoán đã đăng ký: _chờ kết quả_.

## 4. Việc sửa đề xuất (chưa áp vào mã; một phiên khác đang sửa mã sản phẩm)

1. Chỉ bật EV-02 khi câu thật sự không có dẫn chiếu. Nhận ra "(Báo cáo …, trang …)" và "theo …" là dẫn chiếu.
2. Bộ trích thuộc tính phải nhận "so với năm gốc YYYY" là năm gốc, và nhận "năm YYYY" hay "trong năm YYYY" là kỳ báo cáo.
3. Thêm "nhiên liệu hóa thạch", "lượng nước tiêu thụ" và "nước thải" vào từ vựng chỉ số của bộ trích.
4. Bộ chấm ưu tiên phải cộng điểm cho tuyệt đối hoá, mục tiêu như thành tích và cường độ thay tổng, vì các mã này đã có trong bảng mã vấn đề.
5. Năm mã ngoài từ vựng luật nên giao cho bộ đọc mô hình (4B cục bộ) kèm chốt "không thêm số". Hệ lai ở mục 3 sẽ cho biết làm vậy có đáng không.

Mọi việc sửa đều phải đăng ký trước, chạy lại GS-Bench (không được tăng kết luận sai), rồi chạy lại GS-Issue.
