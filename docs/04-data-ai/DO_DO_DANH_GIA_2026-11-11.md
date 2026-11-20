# Danh mục độ đo của GreenScan (11/11/2026)

Tài liệu dành cho đội, khi viết báo cáo, slide và khi trả lời BGK. Mỗi độ đo ghi rõ bốn điều: nó trả lời câu hỏi gì, tính ra sao, tính ở đâu, và khi nào được phép nói ra.
Quy tắc chung (theo `configs/measurement_decisions.yaml`):
- Đăng ký dự đoán trước khi đo.
- Mọi tỷ lệ đi kèm khoảng Wilson 95 %. So sánh hai hệ thống thì dùng khoảng bootstrap theo doanh nghiệp (câu thật) hoặc theo ngành (lớp A).
- Luôn ghi loại nhãn: đáp án có sẵn, nhãn Claude, nhãn bạc hay nhãn người.

**Ưu tiên (Nhân, 11/11):** độ đo nhóm A (tìm lỗ hổng) và nhóm B (đề xuất sửa) được đặt trước các nhóm khác.

## A. Tìm lỗ hổng (mới: GS-Issue, `benchmark/gs_issue/score_issue.py`)

| Độ đo | Câu hỏi | Cách tính | Nói được khi |
|---|---|---|---|
| Recall theo mã (R) | Mỗi loại lỗ hổng bắt được bao nhiêu? | TP / (TP + FN) trên câu có mã đó, kèm Wilson | cận dưới ≥ 0,70 thì nói "bắt được <mã> trên ca kiểm soát" |
| Precision theo mã (P) | Khi báo một loại lỗ hổng thì đúng bao nhiêu? | TP / (TP + FP) | đi cùng R, không nói riêng |
| macro-F1 (chặt) | Toàn bộ 14 loại, mỗi loại nặng như nhau | trung bình F1 của các mã có ca; CI bootstrap theo ngành hoặc doanh nghiệp | so hệ thống: cận dưới của chênh lệch > 0 |
| macro-F1 theo họ | Như trên, gộp các mã mà hướng dẫn gán nhãn cho phép chồng nhau (SCOPE: phạm vi / công ty mẹ; VAGUE: mơ hồ / không số) | như trên | luôn báo cạnh bản chặt |
| micro-F1 | Trên tổng mọi lỗ hổng | TP, FP, FN cộng chung | — |
| Bắt câu cần sửa | Câu có lỗi có bị bỏ qua không? | tỷ lệ câu có lỗi mà hệ thống báo ít nhất một mã | — |
| **Báo nhầm câu sạch** | Hệ thống có kêu bừa không? | tỷ lệ câu sạch bị gắn mã, kèm Wilson | phải báo cùng recall; recall cao mà báo nhầm 100 % là vô dụng |
| Độ chính xác cân bằng | Gộp hai số trên | (bắt câu cần sửa + 1 − báo nhầm) / 2 | — |
| Khớp trọn bộ mã | Bao nhiêu câu có bộ mã đúng y nhãn | — | — |
| κ máy đọc với Claude / giữa hai máy | Nhãn bạc tin được tới đâu? | Cohen κ theo từng mã | κ ≥ 0,70 (cổng `kappa_min`) |

## B. Đề xuất sửa (mới; lớp A có đáp án nên chấm tự động)

| Độ đo | Cách tính | Ghi chú |
|---|---|---|
| Sửa gỡ được lỗi | `taxonomy.oracle`. Lỗi thiếu thông tin: bản sửa có chỗ trống mới nhắc đúng ô (kỳ, năm gốc, phạm vi, nguồn, tổ chức cấp…). Lỗi nói quá: cụm cấy biến mất hoặc được hỏi lại | trên 560 ca một lỗi |
| Giữ số | mọi con số của câu gốc còn nguyên (trừ số nằm trong cụm nói quá, ví dụ "100 %") | |
| **Bịa số** | bản sửa có số mà câu gốc không có | Studio cấm việc này (`assert_no_new_numbers`); phải bằng 0 trong sản phẩm |
| **Sửa đúng** | gỡ được lỗi, giữ số và không bịa số; kèm Wilson | cận dưới ≥ 0,70 thì nói "đề xuất sửa đúng" |
| Sửa đúng theo mã | như trên, tách theo mã | biết cần bổ sung luật ở đâu |
| Hai lỗi: sửa đúng | trên 60 ca hai lỗi, phải gỡ cả hai | |
| Sửa câu sạch | tỷ lệ câu sạch bị viết lại | càng thấp càng tốt |
| Loại sửa hợp lệ | loại sửa (thêm phạm vi, chỗ trống, dẫn nguồn, làm nhẹ) nằm trong các loại hướng dẫn cho phép với mã đó | |
| chrF với bản sửa mẫu | độ giống ký tự với bản sửa mẫu | chỉ để tham khảo, có nhiều cách sửa đúng |
| Gợi ý dùng được | trong các ca đã bắt đúng mã, bao nhiêu ca có bản sửa đúng | |
| Sửa đúng chỗ trống (câu thật) | trên câu thật có mã thiếu thông tin, bản sửa có chỗ trống nhắc đúng ô | D-EDIT và lớp B |
| Chốt số từ chối | số bản sửa của mô hình bị chốt "không thêm số" gạt đi | hệ `+guard`, `hybrid` |

## C. Ưu tiên và chấm rủi ro

| Độ đo | Cách tính | Ở đâu |
|---|---|---|
| Spearman điểm với đồng thuận nhãn | ρ, bootstrap theo doanh nghiệp | `gs_eval_v2/evaluate.py` (0,459 [0,234; 0,588]) |
| QWK theo thành phần | κ trọng số bậc hai | như trên |
| **Thứ tự cặp song sinh** (mới) | tỷ lệ cặp có điểm(bản có lỗi) > điểm(bản sạch); báo riêng tỷ lệ hoà vì hoà nghĩa là bộ chấm không thấy lỗi | `gs_issue/score_supp.py` |
| Lỗi nặng vào dải cao (mới) | tỷ lệ bản có lỗi nặng (tuyệt đối hoá, trung hòa, mục tiêu như thành tích, cường độ thay tuyệt đối, che mặt xấu) có điểm ≥ 50 | như trên; phải đọc cùng thứ tự cặp, vì điểm của bản sạch có thể đã cao sẵn |
| Bỏ sót ngoài hàng đợi | tỷ lệ câu nghiêm trọng trong mẫu ngẫu nhiên ngoài hàng đợi, kèm cận trên Wilson | cần nhãn người: `00-project/DINH_HUONG_CAN_TRONG_VA_HUU_ICH_2026-11-11.md` |
| Độ tập trung hàng đợi | tỷ lệ vấn đề trong hàng đợi chia cho tỷ lệ ngoài hàng đợi | như trên |

## D. Trích tuyên bố

| Độ đo | Cách tính | Ở đâu |
|---|---|---|
| Câu không phải tuyên bố | tỷ lệ trên mẫu đã gán | `gs_eval_v2` (30 %, Wilson [0,23; 0,38]) |
| **Độ phủ trích câu đứng một mình** (mới) | tỷ lệ câu tuyên bố rõ ràng, đứng một mình, mà bộ trích lấy ra được, tách theo chỉ số | `gs_issue/run_pipeline_supp.py` (cặp song sinh và GS-Bench) |

## E. Kết luận và lời giải thích

| Độ đo | Cách tính | Ở đâu |
|---|---|---|
| Kết luận trùng nhãn, κ, macro-F1 | | `gs_eval_v2/evaluate.py` |
| Độ chính xác kết luận dứt khoát, số "mâu thuẫn" sai, số "khớp" sai | | GS-Bench `experiments/AG-0/score.py`; cổng an toàn |
| Độ phủ kết luận (luật, luật + 4B) | tỷ lệ ca được kết luận dứt khoát | `agentic_ag2_*` |
| Recall C / S trên phần bù (mới) | kết luận của hệ thống so với nhãn GS-Bench trên 50 ca C và 35 ca S | `gs_issue/score_supp.py` |
| Lời giải thích nêu cả hai số (mới) | với ca C: lời giải thích có số của tuyên bố **và** số của bằng chứng | như trên |

## F. Cân bằng dữ liệu (mới; `benchmark/data_card.py`)

| Độ đo | Cách tính | Ngưỡng |
|---|---|---|
| Độ đều Pielou J | H / ln(k) | — |
| Tỷ lệ lớp lớn / lớp nhỏ (IR) | | ≤ 3 |
| Số ca lớp nhỏ nhất | | ≥ 20 |
| Tỷ trọng doanh nghiệp lớn nhất | | nên ≤ 0,35 |

Bộ nào vượt ngưỡng thì thêm ca theo [HUONG_DAN_TAO_THEM_CASE.md](HUONG_DAN_TAO_THEM_CASE.md) trước khi dùng số của bộ đó.
