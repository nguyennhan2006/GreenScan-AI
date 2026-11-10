# PQ-01 · Khi GreenScan nói "khớp" hay "mâu thuẫn", tin được bao nhiêu, và nó có biết lúc nào không chắc không?

Bản nháp 01/11/2026, theo khung luận văn ở mục 7 của `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`. Nhãn bằng chứng như PQ-06.

## 1. Câu hỏi

Ban giám khảo hỏi: "Kiểm toán viên mở báo cáo của GreenScan, thấy tuyên bố A bị gắn 'mâu thuẫn'. Họ nên tin kết luận đó tới mức nào? Và khi hệ thống không chắc, nó có nói ra không, hay vẫn đưa ra một kết luận cho có?"

## 2. Trả lời ngắn

GreenScan được thiết kế để **nói ít mà đúng**.
- Hệ thống chỉ kết luận "khớp" (S) hoặc "mâu thuẫn" (C) khi một phép tính so được hai số liệu cùng chỉ số, cùng kỳ, cùng phạm vi và cùng ranh giới.
- Mọi trường hợp khác thành "chuyển người" (N), kèm lý do: khác kỳ, khác phạm vi, chỉ có mục tiêu, không đọc được số.

Số đo hiện có, đều trên nhãn **bạc**:
- trên 87 ca ngoài mẫu đã làm sạch, đường đọc bằng mô hình cho **0 kết luận sai**, ở độ phủ 11–25 %;
- luật thuần chỉ dám kết luận 1 % số ca;
- trên dữ liệu hiệu chỉnh, luật thuần có 9 kết luận "khớp" sai; chính sách hai đường bỏ những phiếu "khớp" chỉ một mình luật đưa ra.

Mức tin hiện tại là "chưa đo thấy kết luận sai trên vài chục ca". Đó chưa phải một tỷ lệ chính xác có cận dưới chặt. Muốn có con số đó cần nhãn người (D-2026-09-22-05).

## 3. Lập luận

### 3.1. Không chắc là một kết quả hợp lệ, không phải một thất bại

**[KIẾN THỨC NỀN]** Trong kiểm toán, kết luận sai về một doanh nghiệp đắt hơn nhiều so với việc chuyển một hồ sơ cho người đọc. Vì vậy GreenScan không tối ưu "tỷ lệ đúng trên mọi ca". Hệ thống tối ưu **precision trên phần dám kết luận**, đi kèm **độ phủ** (bất biến 8: "Abstain là kết quả hợp lệ"; `docs/00-project/ARCHITECTURE_INVARIANTS.md`).

Hai con số luôn được báo cùng nhau, kèm số "mâu thuẫn sai" (vu oan) và "khớp sai" (bỏ lọt). Không có một con số gộp (PQ-06, mục 3.4).

**[ĐÃ THỰC NGHIỆM]** Bài học khiến đội chọn thiết kế này: ngày 17/09, phiên bản đầu báo 357/419 kết luận "mâu thuẫn" sai. Sau khi thêm luật "chỉ so cái so được" (bất biến 4), con số này về 0 trong bộ dựng ngày 22/09. Nguồn: `docs/07-presentation/ban-ket-2026-10-25/01_NOI_DUNG_TRINH_BAY.md` và `ISSUES_REGISTER_2026-09.md`.

### 3.2. Hệ thống "biết lúc nào không chắc" bằng cấu trúc, không bằng cảm giác của mô hình

Phần lớn hệ thống dùng LLM báo độ tin là một xác suất do chính mô hình tự đưa ra. **[NGOÀI]** Tín hiệu đó yếu: trong text-to-SQL, kiểm chéo hai nguồn khác nhau cho AUROC 0,82, còn tự nhất quán của một mô hình chỉ 0,61–0,68 (dẫn trong `Zalo AI challenge/docs/NGHIEN_CUU_PIPELINE.md`, §5.1).

GreenScan biết mình không chắc theo ba tầng, tầng nào cũng kiểm được:
1. **Không so được thì không kết luận.** `irlib.compare` trả N kèm tên chiều bị lệch, ví dụ "khác kỳ: 2023 / 2022". Đây là không chắc vì **thiếu căn cứ**, và người đọc thấy ngay vì sao.
2. **Bằng chứng tự mâu thuẫn thì không kết luận.** Nếu trong cùng đoạn có số khớp lẫn số lệch, như câu "gas 39 % và xăng dầu 14 %", `irlib.decide` trả N. Đã thấy điều này trên 2/142 ca, ngay cả khi đọc hoàn hảo.
3. **Hai đường đọc độc lập không đồng ý thì không kết luận** (AG-2, mục 3.4).
   - Luật và mô hình đọc khác nhau, hoặc chỉ một bên dám nói: hệ thống chuyển người.
   - Riêng phiếu "khớp" mà **chỉ luật** đưa ra thì bị bỏ, vì luật có lỗi "khớp sai" đã đo (mục 3.3).

### 3.3. Số đo: tin được bao nhiêu ở từng đường

**[ĐÃ THỰC NGHIỆM]** GS-Bench v1.3 sạch (`benchmark/gs_bench_v1/clean_v13.py`). Chấm bằng `experiments/score.py`, khoảng tin cậy bootstrap theo công ty. Kết quả ở `experiments/AG-1/out/v13/`. Mỗi ô ghi độ phủ / precision / khớp sai / mâu thuẫn sai.

| Đường | Hiệu chỉnh (B-b, n = 383–397, trong mẫu) | Ngoài mẫu (B-b, n = 87) |
|---|---|---|
| Luật hiện tại | 0,060 / 0,625 / 9 / 0 | 0,011 / 1,0 / 0 / 0 |
| Mô hình 4B đọc + `irlib` | 0,243 / 0,989 / 1 / 0 | 0,138 / 1,0 / 0 / 0 |
| Mô hình 14B đọc + `irlib` | 0,347 / 0,970 / 3 / 1 | 0,115 / 1,0 / 0 / 0 |
| Mô hình 32B đọc + `irlib` | 0,373 / 0,986 / 2 / 0 | 0,253 / 1,0 / 0 / 0 |

**Đọc bảng:**
- Luật thuần **không đáng tin khi nói "khớp"** trên câu thật: 9 trong 24 kết luận ở tập hiệu chỉnh là "khớp" sai. Nguyên nhân đã ghi từ 10/10: nhầm cường độ với tuyệt đối, và ngưỡng 0,35 che các chênh lệch 9–25 %.
- Đường đọc bằng mô hình dám kết luận nhiều hơn 4–6 lần, và gần như không sai.
- Ngoài mẫu, mỗi mô hình chỉ dám kết luận 10–22 ca, nên "precision 1,0" ở đây có nghĩa "0 lỗi trên 10–22 ca". Cận dưới thực tế còn rộng.

### 3.4. Chính sách hai đường: tin được hơn từng đường riêng

**[ĐÃ THỰC NGHIỆM]** AG-2 v1 đăng ký trước, trong khối `agentic_ag2_v1` (`configs/measurement_decisions.yaml`). Script là `experiments/AG-2/policies.py`. Chính sách được hiệu chỉnh trên 388 ca v1.1, rồi kiểm trên 162 ca của lượt G. Mỗi ô ghi độ phủ / precision / khớp sai / mâu thuẫn sai.

| Chính sách | Hiệu chỉnh | Ngoài mẫu G |
|---|---|---|
| Luật một mình | — (8 khớp sai) | 0 khớp sai |
| **Luật + 4B, bỏ phiếu "khớp" đơn độc của luật** | 0,242 / 0,989 / 1 / 0 | 0,093 / 1,0 / 0 / 0; phần tăng độ phủ so với luật có CI [0,016; 0,185] |
| Luật + 32B | — | 1 khớp sai (trượt) |
| Luật + 4 mô hình | — | 2 khớp sai (trượt) |

**Nhận xét:**
- Thêm đường đọc thứ hai **chỉ an toàn khi đi kèm việc bỏ phiếu "khớp" đơn độc của luật**. Giữ phiếu đó thì giữ luôn 8 lỗi "khớp sai" của luật.
- Thêm nhiều mô hình **không** làm an toàn hơn: luật + 4 mô hình có 2 khớp sai trên G. Lý do là xác suất đúng theo từng "xô" ước trên quá ít ca, nên ước lượng không ổn định.

Đây là lý do sản phẩm chỉ dùng đường "luật + 4B" sau cờ `QUANTUM_VERIFY=dual` (quyết định 31/10). Đường này chỉ làm **trợ giúp người soát**, verdict không đổi, cho tới khi qua cổng 06/11 và có nhãn người.

### 3.5. Người soát thấy gì

**[ĐÃ THỰC NGHIỆM, giao diện]** Hàng đợi ưu tiên `priority-v1.1` và giấy làm việc hiển thị:
- verdict;
- trích dẫn trang;
- phép tính hoặc lý do "không so được".

Nguồn: `docs/07-presentation/ban-ket-2026-10-25/03_KICH_BAN_PROTOTYPE_DEMO.md`.

Khi `QUANTUM_VERIFY=dual` bật, huy hiệu "hai đường khớp / lệch" giúp người soát mở trước những tuyên bố mà hai đường lệch nhau. **[GIẢ THUYẾT]** Chưa có thí nghiệm người dùng (v3 E4 / F) đo việc này có tiết kiệm thời gian thật không.

### 3.6. Vì sao chưa nói "độ chính xác X %"

Ba lý do, mỗi lý do có số:
1. **Nhãn bạc.** Nhãn đến từ cách dựng ca, trên số liệu do Claude và Qwen3-32B đọc. Người chưa duyệt: gold người vẫn bằng 0 (kiểm 31/10).
2. **n nhỏ.** 10–22 kết luận ngoài mẫu mỗi mô hình; D-2026-09-22-05 đòi ít nhất 60.
3. **Tập đo từng có lỗi.** Tập ngoài mẫu v1.2 có 75/162 ca lỗi, chỉ phát hiện khi hậu kiểm (`errata_v13.txt`). Đội báo lỗi đó và loại theo quy tắc tất định, nhưng nó cho thấy nhãn bạc cần người soát lại.

## 4. Thí nghiệm được dẫn (khung 10 điểm, rút gọn)

**AG-2 · Hai đường + bỏ phiếu "khớp" đơn độc của luật** (`experiments/AG-2/`)
1. **Vấn đề:** cần biết khi nào được kết luận, mà không dựa vào độ tự tin của mô hình.
2. **Dự đoán và cổng:** đăng ký `agentic_ag2_v1` lúc 31/10 23:40, trước khi tính chính sách nào trên G. Cổng `ag2_dual_path_to_product`:
   - khớp sai và mâu thuẫn sai không vượt luật;
   - phần tăng độ phủ có cận dưới CI > 0.
3. **Phương pháp:**
   - Cách chọn: hợp hai đường, bỏ phiếu S đơn độc của luật, và xô xác suất ước trên OOF theo công ty.
   - Phương án đã bỏ:
     - tự nhất quán bằng lấy mẫu (tín hiệu yếu [NGOÀI], và luật bắt greedy);
     - bỏ phiếu nhiều mô hình (trượt trên G).
4. **Cấu hình:**
   - đầu ra AG-1 của 4B / 8B / 14B / 32B (Kaggle);
   - luật `experiments/AG-0/out/rules*.jsonl`;
   - `policies.py --cal … --test …`.
5. **Kết quả:** bảng mục 3.4.
6. **Giới hạn:**
   - trên G, 4B chỉ dám kết luận 15 ca (đúng cả 15), nên chưa phải cận chặt;
   - nhãn bạc;
   - phần ba cổng còn lại chưa chạy: 17 bẫy xanh, test bất biến, thời gian chạy HPG trên laptop.
7. **Thất bại:**
   - xô OOF quá mảnh;
   - chính sách hợp giữ lỗi của luật.
8. **Khái niệm:** độ phủ, precision trên phần dám kết luận, OOF theo công ty (`GLOSSARY.md`).
9. **Hình:** đường độ phủ – precision của luật, từng mô hình và hai đường (`experiments/AG-2/out/*_curve.json`).
10. **Bước tiếp:**
    - đo bộ đọc trong sản phẩm: lượt Kaggle `gs-ag2-q4-parity` cho phần "cùng kết quả", laptop cho phần thời gian;
    - nhãn người cho 40 cặp;
    - kiểm cổng ngày 06/11.

## 5. Câu hỏi vặn của BGK

- **"Hệ thống chỉ kết luận 14 % số ca. Vậy 86 % còn lại người vẫn phải đọc à?"**
  - Đúng. Nhưng 86 % đó đã được xếp hàng theo mức cần soát, kèm trang và lý do.
  - Hôm nay luật chỉ kết luận được 1 %. Mục tiêu là chuyển việc đọc từ "dò từng trang" sang "duyệt các ca hệ thống đã khoanh".
- **"0 lỗi thì có phải hệ thống hoàn hảo?"**
  - Không. Đó là 0 lỗi trên 10–22 kết luận ngoài mẫu, nhãn bạc.
  - Với n như vậy, tỷ lệ lỗi thật vẫn có thể lên tới vài chục phần trăm ở cận trên. Đội không công bố độ chính xác.
- **"Sao không cho mô hình lớn tự quyết cho nhanh?"**
  - Mô hình tự phán từng báo "khớp" sai trên bảng dàn phẳng, ở mọi cỡ 26B–753B (size ladder, 10/10).
  - Trong đường hai đường, thêm 32B làm tăng lỗi "khớp sai" trên G (mục 3.4).
- **"Ai chịu trách nhiệm kết luận cuối?"**
  - Người soát. GreenScan kiểm chứng tuyên bố, không phán xét doanh nghiệp (bất biến 1).
  - Mọi kết luận có phép tính và trích dẫn để người soát kiểm lại (bất biến 10).

## 6. Không được nói

- "Độ chính xác X %" dưới mọi hình thức. Chưa có nhãn người, n < 60.
- "Hệ thống tự đánh giá độ tin cậy." Hệ thống không dùng độ tự tin của mô hình; nó dùng điều kiện so được và sự đồng thuận của hai đường.
- "Đường hai đường đã có trong sản phẩm." Còn chờ cổng 06/11.
- "Kiểm toán viên tiết kiệm Y % thời gian." Chưa đo.
