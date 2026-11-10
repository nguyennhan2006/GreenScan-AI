# Đánh giá hệ thống GreenScan hiện tại trên GS-Eval v2

*05/11/2026. Người đọc: đội GreenScan (chuẩn bị Chung kết, viết luận văn). Số tự sinh ở `benchmark/gs_eval_v2/results/EVAL_REPORT.md` và `eval_results.json` (chạy lại: `.venv/Scripts/python.exe -I benchmark/gs_eval_v2/evaluate.py`). Nhãn do Claude gán theo `benchmark/gs_eval_v2/LABELING_GUIDE.md`, Nhân đọc lại (`review_status` còn `pending_human_review`).*


## Cập nhật chiều 05/11: đã sửa hai lỗi CONTRADICTED (P0)

Nhân yêu cầu sửa ngay. Hai nguyên nhân ở mục 2 bên dưới được sửa bằng một **chốt chặn mâu thuẫn** trong `src/quantum_gw/agents/verifier.py`:
- hai con số nằm trong **cùng tài liệu** của tuyên bố không còn được kết luận là mâu thuẫn; hệ thống vẫn hiện cả hai số cho người soát;
- từ phủ định trong **chính tài liệu của doanh nghiệp** (internal, financial) chỉ còn tính khi nằm trong một phán quyết về tuyên bố. Nguồn độc lập (pháp lý, tiêu chuẩn, bên ngoài) giữ nguyên.

Cờ `verification.self_evidence_can_contradict` (env `QUANTUM_SELF_EVIDENCE_CAN_CONTRADICT`) mặc định `false`; đặt `true` để quay về hành vi cũ. Quyết định này thay D-2026-10-16-01 ("không đổi kết luận trước Chung kết") cho riêng hai lỗi này, vì các bộ kiểm cũ đều cho kết quả không đổi (bảng dưới).

| Chỉ số (GS-Eval v2, câu thật của 8 doanh nghiệp) | Trước sửa | Sau sửa 05/11 |
|---|---|---|
| CONTRADICTED đúng nhãn | 3/38 | **3/4** |
| CONTRADICTED sai trên tuyên bố thật (vu oan) | 24 | **0** |
| CONTRADICTED sai, tính cả câu không phải tuyên bố | 35 | 1 |
| Độ chính xác kết luận (n = 102 tuyên bố) | 0,40 | 0,51 |
| Cohen κ / macro-F1 | 0,15 / 0,29 | 0,18 / 0,52 |
| Điểm rủi ro: Spearman với điểm đồng thuận (n = 148) | 0,23 [0,05; 0,37] | 0,39 [0,16; 0,51] |
| Điểm rủi ro: trung bình hệ thống / nhãn | 55,9 / 30,2 | 49,2 / 30,2 |
| UXL-07: chuỗi hiện nguyên từ "vi phạm" | 24 | 0 |
| GS-Bench v1.1: 453 ca, nhãn từng ca | — | giống hệt trước (453/453) |
| 4 ca án lệ thật (BNY, DWS, KDP, KLM) | 4/4 CONTRADICTED | 4/4 CONTRADICTED |
| Toàn bộ test | qua | qua (thêm 6 test `tests/test_contradiction_guard.py`) |

Lượt chạy sau sửa: CTD `759ddae1ae8645f4`, DHG `058cf107b5024347`, PAN `9b1fa0a9aa9d4db0`, PNJ `4e8a4750b91c4fa8`, SAB `a50d238678e24ff9`, TRA `b0245707316342d8`, HPG `50f8a42652ff4ce5` / `0f8943940853473e` / `ab65781e7fae44e6`, KLM `519c955fb1ba4d07`, án lệ `b157deb1…`, `d20609b0…`, `e62a0ae6…`, `b0775111…`. Số trước sửa giữ ở `benchmark/gs_eval_v2/results/eval_results_preguard.json`.

Còn nguyên sau sửa: SUPPORTED 0/5; 44/146 câu trích ra không phải tuyên bố; điểm rủi ro vẫn phạt thành phần không áp dụng. Kết quả judge (mục 2.2) chấm trên lời giải thích **trước** sửa, chưa chấm lại.

## 0. Kết luận ngắn

1. **Hai bảo đảm thiết kế đứng vững.**
   - Gợi ý sửa không thêm số nào: 0/527 gợi ý.
   - Quy tắc nội bộ (org pack) không đổi kết luận. Engine cho kết quả đúng 0,945 (Wilson 95 % [0,908; 0,968]) trên 237 ca cân bằng 4 lớp, và đúng 45/45 ca an toàn (nháp, hết hiệu lực, tiêm lệnh, vượt quyền, trái luật; 58/58 nếu tính cả ca khác ngành).
2. **Kết luận CONTRADICTED trên báo cáo thật không tin được.**
   - Chỉ 3/38 ca đúng nhãn. 35 ca còn lại: 22 đi qua luật "từ phủ định" (đoạn bằng chứng chứa "vi phạm", "do not" kể cả trong câu "không ghi nhận vi phạm"), 13 là so số của hai đối tượng khác nhau.
   - Con số "0 vu oan" đã nói trước đây là trên GS-Bench (ca dựng). Trên kho thật, kết quả khác hẳn.
3. **Khoảng 30 % câu được trích không phải tuyên bố** (44/146, Wilson [0,23; 0,38]): dòng bảng, mục lục, chân trang.
4. **Điểm rủi ro lệch so với chuyên môn.**
   - Tương quan với điểm đồng thuận của hai lượt nhãn chỉ ρ = 0,23 [0,05; 0,37], trong khi hai lượt nhãn đồng thuận với nhau ρ = 0,73.
   - Hệ thống phạt cả thành phần không áp dụng (baseline: 69/120 ca), và chấm `independent_assurance` gần như luôn tối đa.
5. **Lời giải thích theo mẫu cố định** (54 câu khác nhau trên 146 mẫu).
   - Khi hệ thống dừng phán đoán, lời giải thích trung thực: 0,95 với PARTIALLY, 0,60 với INSUFFICIENT.
   - Khi hệ thống kết luận dứt khoát, lời giải thích trung thực chỉ 0,08 với CONTRADICTED và 0 với SUPPORTED.
   - Độ phủ ý riêng của từng mẫu 0,02. Mức thiếu thuộc tính khớp nhãn thấp: F1 0,18–0,30, riêng năm gốc 0.
6. **Không có hành động sửa nào áp vào sản phẩm trước Chung kết.** Mọi đề xuất ở mục 4 đi sau cờ hoặc để sau 10/11, theo quyết định D-2026-10-16-01.

## 1. Thiết lập

**Hệ thống được đánh giá:** mã hiện tại, chế độ `offline`, không mô hình ngôn ngữ, không gọi mạng.
- 15 lượt chạy từ 22/10 tới 05/11 (`benchmark/gs_eval_v2/inputs/refresh_stats.json`).
- Tài liệu: HPG (BCPTBV 2025, BCTN 2024), CTD, DHG, PAN, PNJ, SAB, TRA (báo cáo bền vững, kèm báo cáo thường niên khi có), hồ sơ ca KLM, và 4 ca thật KDP / BNY / DWS / KLM.
- Tổng 1 138 tuyên bố khác nhau. Kết luận hệ thống: PARTIALLY_SUPPORTED 1 006, INSUFFICIENT_EVIDENCE 72, CONTRADICTED 52, SUPPORTED 8.

**Phiên bản mã.** Mẫu ban đầu lấy từ mọi lượt trong `.quantum/runs`, kể cả lượt tháng 7–9 do mã cũ tạo. Vì vậy hệ thống hiện tại được chạy lại trên đúng các tài liệu đó (`run_refresh.py`), rồi ghép đầu ra theo nội dung câu (`refresh_system_outputs.py`).
- 328/394 mẫu ghép được: 320 trùng khớp, 8 bao hàm.
- 66 câu mã hiện tại không còn trích ra; nhãn của 23 câu trong số đó là NOT_A_CLAIM. Bộ trích hiện tại đã bỏ phần lớn dòng bảng mà bản tháng 8 từng trích và từng kết luận SUPPORTED.
- Mọi số dưới đây là của **mã hiện tại**.

**Dữ liệu (GS-Eval v2, `benchmark/gs_eval_v2/`).**

| Bộ | Cỡ | Lấy mẫu (lệch nhẹ, cân bằng) | Nhãn |
|---|---|---|---|
| D-EXPLAIN | 200 (146 có đầu ra mã hiện tại) | phân tầng theo kết luận của lượt nguồn: S 45 / C 50 / I 50 / P 55; ≤ 12 % P mỗi công ty | 1 lượt, kiểm định đối nghịch 20 mẫu (lỗi văn bản 2/20, không lỗi kết luận) |
| D-EDIT | 200 | 100 câu từ lượt chạy (có số 34 / định tính 33 / mơ hồ 33) + 100 câu kho VN30 theo nhãn T1 (33 / 34 / 33); 14 công ty, không công ty nào > 13 % | 1 lượt, kiểm định 20 mẫu |
| D-SCORE | 200 × 2 lượt mù | như D-EXPLAIN | 2 lượt mù + phân xử 122 mẫu có chỗ lệch |
| D-RULES | 14 pack (12 tổ chức giả lập + 2 nháp), 76 quy tắc, 237 ca | C 60 / V 72 / NR 57 / NA 48; đủ 8 loại ca | 3 agent, mỗi agent 4–5 tổ chức |
| D-UX | 16 nhiệm vụ theo persona, SUS tiếng Việt, 18 heuristic, 15 kiểm lint | — | bộ công cụ; chưa có người thử |

**Độ đồng thuận giữa hai lượt chấm rủi ro** (trần thực tế cho mọi hệ thống chấm tự động):
- QWK theo thành phần từ 0,59 (`specificity`) tới 0,84 (`vague_or_exaggerated_language`);
- tổng điểm Spearman 0,73;
- dải tổng thể QWK 0,75.

## 2. Kết quả theo mục tiêu

### 2.1 Trích tuyên bố
- 44/146 câu hệ thống trích ra không phải tuyên bố, 30 % (Wilson [0,23; 0,38]). Ước tính trên toàn kho sau khi trọng số lại theo tầng là 0,37; đây là xấp xỉ, vì mẫu được rút theo tầng của lượt nguồn.
- Tỷ lệ theo kết luận của hệ thống: P 21/55, C 11/38, I 10/48, S 2/5.
- Nguyên nhân: câu ghép từ ô bảng, mục lục, chỉ mục GRI, chân trang lặp lại, câu bối cảnh không nói về doanh nghiệp.

### 2.2 Kết luận và an toàn
Ma trận trên 146 mẫu (hàng = hệ thống, cột = nhãn):

| Hệ thống \ Nhãn | CONTRADICTED | INSUFFICIENT | NOT_A_CLAIM | PARTIALLY | SUPPORTED |
|---|---|---|---|---|---|
| CONTRADICTED | 3 | 9 | 11 | 11 | 4 |
| INSUFFICIENT | 0 | 17 | 10 | 14 | 7 |
| PARTIALLY | 0 | 8 | 21 | 21 | 5 |
| SUPPORTED | 0 | 0 | 2 | 3 | 0 |

- **Trên 102 tuyên bố thật:** kết luận trùng nhãn 0,40 (bootstrap theo công ty [0,34; 0,46]), κ = 0,15.
  - PARTIALLY: P 0,62, R 0,43.
  - INSUFFICIENT: P 0,45, R 0,50.
- **Kết luận dứt khoát (S / C):** 43, chỉ 3 đúng.
  - **CONTRADICTED sai: 35.** 24 trên tuyên bố thật (nhãn đúng: P 11, I 9, S 4), 11 trên câu không phải tuyên bố.
    - 22 đi qua luật từ phủ định. Danh sách cụm phủ định lành tính trong `configs/stance_cues.yaml` (`không có vi phạm`, `không ghi nhận vi phạm`…) chỉ khớp nguyên cụm, nên "Không ghi nhận **trường hợp nào** vi phạm" vẫn bị coi là bác bỏ.
    - 13 là "số liệu lệch" giữa hai đối tượng khác nhau, ví dụ khay giấy 23 tấn so với lót PET 14 tấn của một sáng kiến khác. Cổng so sánh được mới kiểm đơn vị và chiều, chưa kiểm cùng đối tượng.
    - Theo công ty: PAN 7, DHG 7, SAB 6, CTD 6, PNJ 5, TRA 3, KLM 1. Lượt demo HPG (`c892c13727c24bb9`) không có CONTRADICTED nào.
  - **SUPPORTED: 5 ca, không ca nào đúng nhãn** (3 là PARTIALLY, 2 không phải tuyên bố). Mã hiện tại chỉ kết luận SUPPORTED 8/1 138 lần.
- **Đối chiếu số cũ.** GS-Bench v1.3 ngoài mẫu (87 ca dựng): luật precision 1,0, 0 kết luận sai (`experiments/AG-1/README.md`). Hai số không mâu thuẫn: GS-Bench dựng tuyên bố từ một ô bảng và so với chính ô đó; kho thật có câu bối cảnh, phủ định lành tính và nhiều sáng kiến cùng đơn vị trong một trang.

### 2.3 Lời giải thích
- Trung bình 34 từ, không câu nào quá 80 từ. Chỉ 54 câu khác nhau trên 146 mẫu: lời giải thích là mẫu cố định theo nhánh luật.
- 17/146 lời giải thích chứa số không có trong câu hay đoạn bằng chứng được hiển thị. Số này lấy từ bằng chứng nằm ngoài ba đoạn đầu, nên chưa chắc là bịa; cần soát.
- Thuộc tính thiếu so với nhãn: metric F1 0,21; value 0,30; period 0,27; scope 0,18; baseline 0.
  - Hệ thống báo thiếu năm gốc cho mọi tuyên bố có chiều thay đổi; nhãn chỉ ghi khi tuyên bố thực sự cần.
  - Hệ thống không báo thiếu khi bộ trích luật nhận nhầm thuộc tính.
- **Chấm theo danh mục tham chiếu.** Một agent Sonnet chấm 146 lời giải thích theo danh mục must_mention / must_not_say của từng mẫu, kèm ba tiêu chí: trung thực với bằng chứng, có chỉ ra việc cần làm, và độ rõ 1–5 (`benchmark/gs_eval_v2/explain/judge/judge_output.jsonl`).
  - Độ phủ ý bắt buộc: 0,02 (137/146 lời giải thích không nêu ý riêng nào của mẫu).
  - 19 mẫu nói điều không được nói.
  - Trung thực 0,58 (Wilson [0,49; 0,65]); chỉ ra việc cần làm 0,40; độ rõ 2,7/5.

  | Kết luận hệ thống | n | Trung thực | Chỉ ra việc cần làm | Độ rõ |
  |---|---|---|---|---|
  | CONTRADICTED | 38 | 0,08 | 0,00 | 2,0 |
  | SUPPORTED | 5 | 0,00 | 0,00 | 2,0 |
  | INSUFFICIENT_EVIDENCE | 48 | 0,60 | 0,98 | 3,0 |
  | PARTIALLY_SUPPORTED | 55 | 0,95 | 0,20 | 2,9 |

  - **Diễn giải:** khi hệ thống dừng phán đoán (INSUFFICIENT, PARTIALLY), lời giải thích phần lớn trung thực. Riêng INSUFFICIENT còn gần như luôn chỉ ra việc cần làm. Khi hệ thống kết luận dứt khoát, lời giải thích gần như luôn sai lệch, vì nó lặp lại đúng lỗi của kết luận: trích từ phủ định, so số không cùng đối tượng, coi câu tự lặp lại là xác nhận.
  - Lời giải thích không bao giờ nói câu là mảnh bảng hay tiêu đề, cũng không nói phần nào của câu có bằng chứng.

### 2.4 Chấm rủi ro (đồng thuận hai lượt trên 200 mẫu; so với hệ thống trên 148 mẫu có đầu ra của mã hiện tại)

| Thành phần | QWK hai lượt nhãn | QWK hệ thống–nhãn | Mức TB hệ thống / nhãn (0–3) | Không áp dụng | Hệ thống vẫn phạt |
|---|---|---|---|---|---|
| specificity | 0,59 | 0,27 | 1,26 / 1,16 | 43 | 43 |
| quantitative_evidence | 0,66 | 0,42 | 2,09 / 1,41 | 45 | 45 |
| baseline | 0,78 | 0,11 | 1,82 / 0,41 | 120 | 69 |
| period | 0,60 | 0,20 | 2,35 / 0,98 | 50 | 44 |
| scope_boundary | 0,70 | −0,09 | 2,15 / 1,08 | 43 | 34 |
| evidence_support | 0,66 | 0,15 | 1,83 / 1,24 | 41 | 39 |
| independent_assurance | 0,65 | −0,06 | 2,92 / 1,82 | 43 | 43 |
| contradiction | 0,83 | 0,18 | 0,81 / 0,15 | 35 | 10 |
| vague_or_exaggerated_language | 0,84 | 0,38 | 0,51 / 0,95 | 28 | 3 |

- Tổng điểm: hệ thống trung bình 55,9, nhãn 30,2; Spearman 0,23 [0,05; 0,37].
- Mức độ so với dải tổng thể của kiểm toán viên: trùng 0,37, lệch ≤ 1 bậc 0,81.
- Hệ thống chấm đúng hướng ở hai thành phần dựa trên chữ trong câu (ngôn ngữ mơ hồ, có số). Nó chấm sai ở các thành phần cần hiểu loại tuyên bố: năm gốc, phạm vi, đảm bảo độc lập.
- Câu không phải tuyên bố vẫn nhận điểm rủi ro cao, vì mọi thành phần "thiếu" đều bị phạt.

### 2.5 Gợi ý sửa (Studio, 200 mẫu)
- **Không bịa số: 0/527 gợi ý thêm số mới.** Rào chắn `assert_no_new_numbers` hoạt động.
- Hệ thống gợi ý cho **mọi** câu (200/200 có ít nhất một gợi ý), nên không phân biệt câu cần sửa với câu đã ổn: 16/16 câu ổn vẫn bị gợi ý, và có 130 gợi ý trên 49 câu không phải tuyên bố xanh.
- Theo loại sửa, trên 151 tuyên bố xanh:

  | Loại | P | R | F1 |
  |---|---|---|---|
  | placeholder | 0,74 | 0,71 | 0,72 |
  | add_scope | 0,49 | 0,97 | 0,66 |
  | evidence_ref | 0,34 | 1,0 | 0,51 |
  | soften | 0,53 | 0,42 | 0,47 |

- Theo mã vấn đề, macro-F1 0,36. Mạnh nhất: VAGUE_TERM P 0,68, NO_FIGURE P 0,56. Yếu nhất:
  - ABSOLUTE_CLAIM R 0/10, vì mẫu "100 %", "hoàn toàn" của bộ gợi ý quá hẹp;
  - MISSING_BASELINE P 0,14.
- Vấn đề nằm ngoài từ vựng của hệ thống: chứng nhận / nhãn không nêu bên cấp (17), đánh đổi bị che (3).

### 2.6 Quy tắc nội bộ (org pack)
- **Engine với thuộc tính đúng:** đúng 224/237, 0,945 (Wilson [0,908; 0,968]), macro-F1 0,945. 13 lỗi:
  - 10 ca kỳ vọng COMPLIANT / VIOLATION / NEEDS_REVIEW nhưng engine trả NOT_APPLICABLE:
    - 8 ca vì loại tuyên bố do bộ trích luật gán (thường là `generic_sustainability`) không khớp `claim_types` của quy tắc;
    - 2 ca vì điều kiện `when` thiếu từ đồng nghĩa.
  - 3 ca còn lại (2 VIOLATION thành COMPLIANT, 1 NEEDS_REVIEW thành VIOLATION) do `numeric_threshold` xét **mọi** số trong đoạn bằng chứng: chỉ cần một số bất kỳ thoả ngưỡng là đạt.
- **Đầu–cuối** (thuộc tính do bộ trích luật lấy): 0,907 (Wilson [0,863; 0,938]).
- **Ca an toàn:** nháp 11/11, hết hiệu lực 6/6, tiêm lệnh 11/11, vượt quyền 11/11, trái luật 6/6, khác ngành 13/13.
- Kết luận kiểm chứng không đổi khi bật pack: tính chất này kiểm bằng test bất biến trong `tests/test_org_pack.py`. Toàn bộ test (khoảng 453) qua ngày 05/11.

### 2.7 Độ dễ dùng
**UX lint** trên 15 lượt (9 621 chuỗi, 8 015 đoạn bằng chứng):
- **Đạt:**
  - độ dài (0 chuỗi > 80 từ, 0 câu > 40 từ);
  - không lộ mã nội bộ hay tiếng Anh trong mã hiện tại (câu tiếng Anh "A retrieved source supports…" chỉ có ở lượt tháng 8);
  - gợi ý sửa an toàn.
- **Không đạt:**
  - UXL-07: 24 chuỗi hiện nguyên từ "vi phạm" / "xử phạt" khi trích từ phủ định, mang tính cáo buộc;
  - UXL-06a: 73/74 kết luận chưa đủ bằng chứng có cụm trung tính;
  - UXL-04: 8 đoạn bằng chứng không có trang (ca thật dạng .txt);
  - UXL-13: 8/9 ca pack lỗi bị từ chối đúng. E8 (`source_document` không có trong `documents`) chỉ bị cảnh báo; đây là lựa chọn của bản cài đặt, lệch đặc tả.

**Thử với người:** `usability/PROTOCOL.md`, `tasks.yaml` (gồm nhiệm vụ thêm org pack), `SUS_vi.md` đã sẵn sàng. **Chưa có người tham gia (n = 0)**, nên chưa có điểm SUS.

## 3. Chỗ phải nói khác trước BGK

| Đã nói | Nói đúng từ nay |
|---|---|
| "0 vu oan" | "0 CONTRADICTED sai trên GS-Bench (ca dựng có đáp án). Trên 146 câu thật của 8 doanh nghiệp, CONTRADICTED còn sai nhiều; đã tìm ra hai nguyên nhân (từ phủ định, so khác đối tượng) và có cách sửa. Vì vậy mọi CONTRADICTED đều vào hàng đợi người soát." |
| "Hệ thống kết luận khớp / mâu thuẫn" | "Phần lớn tuyên bố được xếp 'khớp một phần'; hệ thống hiếm khi dám kết luận dứt khoát (S 8, C 52 trên 1 138)." |
| "Điểm rủi ro 0–100" | "Điểm rủi ro là chỉ báo ưu tiên, tương quan yếu với chuyên gia (ρ 0,23). Dùng để xếp hàng đợi, không dùng để kết luận." |
| (mới) | "Người dùng thêm quy tắc nội bộ bằng YAML; trên 237 ca kiểm, engine đúng 94,5 %, 45/45 ca an toàn, không bao giờ đổi kết luận kiểm chứng." |
| (mới) | "Gợi ý sửa không bao giờ thêm số (0/527)." |

## 4. Đề xuất sửa (thứ tự ưu tiên; không áp vào sản phẩm trước 10/11 nếu đổi kết luận)

| # | Sửa | Trị | Ước lượng tác động trên GS-Eval v2 |
|---|---|---|---|
| P0 | Luật từ phủ định: cụm phủ định lành tính khớp có khoảng cách ("không ghi nhận … vi phạm" trong cửa sổ 6 từ); từ phủ định chỉ hạ xuống PARTIALLY / cần soát, không bao giờ tự ra CONTRADICTED; chỉ xét từ phủ định trong đoạn cùng chỉ số | 22/35 CONTRADICTED sai | tối đa −22 vu oan |
| P0 | Cổng so sánh được: thêm "cùng đối tượng / sáng kiến" (IR có `segment`, `irlib.ground()` của AG-1) trước khi so số | 13/35 | tối đa −13 |
| P1 | Lọc câu trích: bỏ câu ghép từ ô bảng, mục lục, chỉ mục GRI, chân trang lặp | 30 % câu không phải tuyên bố | giảm hàng đợi và điểm rủi ro ảo |
| P1 | SUPPORTED không tính câu tự lặp lại trong tài liệu khác của cùng doanh nghiệp | 5/5 S sai | — |
| P1 | Chấm rủi ro: thành phần không áp dụng thì 0 điểm; `independent_assurance` phân mức theo loại nguồn; câu không phải tuyên bố không chấm | ρ 0,23 | kiểm lại trên D-SCORE |
| P2 | Gợi ý sửa: không gợi ý cho câu không phải tuyên bố; `evidence_ref` chỉ khi có số; thêm mẫu ABSOLUTE ("100 %", "hoàn toàn", "duy nhất"), thêm loại "chứng nhận không nêu bên cấp" | P loại sửa 0,34–0,49 | kiểm lại trên D-EDIT |
| P2 | Ngôn ngữ: không trích nguyên từ "vi phạm"; nói "bằng chứng có nội dung trái chiều cần soát" | UXL-07 | — |
| P2 | Org pack: `claim_types` khớp mềm (hoặc để trống mặc định trong mẫu pack); `when` đọc cả glossary (từ đồng nghĩa); `numeric_threshold` chỉ xét số đi cùng chỉ số được nêu; E8 từ chối thay vì cảnh báo | 13 ca sai, UXL-13 | tối đa +13 ca đúng |

Mọi sửa đổi đổi kết luận phải đăng ký trước trong `configs/measurement_decisions.yaml`, chạy lại GS-Bench (không được tăng kết luận sai) và GS-Eval v2, rồi mới bỏ cờ.

## 5. Giới hạn của đánh giá này
- **Nhãn của Claude:**
  - một họ mô hình gán cả hai lượt;
  - hai lượt score có 122/200 mẫu (61 %) lệch ít nhất một trường cần phân xử, phần lớn do ranh giới NOT_A_CLAIM;
  - kiểm định đối nghịch 20 + 20 mẫu cho tỷ lệ lỗi explain khoảng 10 % (Wilson [3 %; 30 %]), không lỗi kết luận;
  - Nhân chưa đọc lại hết.
- **Mẫu:**
  - rút theo kết luận của lượt nguồn rồi đánh giá theo kết luận của mã hiện tại, nên tầng SUPPORTED hiện tại chỉ còn 5 mẫu;
  - số trọng số toàn kho là xấp xỉ;
  - bootstrap theo công ty chỉ có 8–12 cụm.
- **Bằng chứng:**
  - người gán nhãn thấy tối đa 3 đoạn, mỗi đoạn tối đa 900 ký tự; hệ thống có thể đã dùng phần bị cắt (đã kiểm 5 ca CONTRADICTED: người gán nhãn thấy đủ cặp số bị so);
  - gợi ý sửa được đánh giá không có quan hệ bằng chứng, nên chưa kiểm được EV-01.
- **Độ dễ dùng:** mới có kiểm tự động; chưa có người dùng thật.
