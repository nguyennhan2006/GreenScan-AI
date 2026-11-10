# PQ-02 · GreenScan có bịa hoặc tính sai số liệu không?

Bản nháp 01/11/2026, theo khung luận văn ở mục 7 của `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`.

Nhãn:
- **[ĐÃ THỰC NGHIỆM]**: số của đội, kèm n và đường dẫn.
- **[KIẾN THỨC NỀN]**: kiến thức chung của ngành.
- **[NGOÀI]**: tài liệu bên ngoài.
- **[GIẢ THUYẾT]**: điều chưa kiểm.

## 1. Câu hỏi

Ban giám khảo hỏi: "Mô hình ngôn ngữ hay bịa. Làm sao các em chắc GreenScan không bịa ra một con số, hoặc tính sai rồi kết luận một doanh nghiệp nói dối?"

Câu hỏi chứa hai rủi ro khác nhau, cần tách ra trả lời riêng:
1. **Bịa:** hệ thống đưa ra một số liệu không có trong tài liệu.
2. **Tính sai:** số liệu có thật, nhưng phép so sánh sai. Ví dụ: nhầm đơn vị, nhầm bội số, so nhầm kỳ hay nhầm phạm vi, làm tròn quá tay.

Hậu quả nặng nhất của cả hai là **CONTRADICTED sai**, tức vu oan một doanh nghiệp. Hậu quả nặng thứ hai là **SUPPORTED sai**: bỏ lọt một tuyên bố không có căn cứ.

## 2. Trả lời ngắn

GreenScan không để mô hình làm phép tính hay tự phán đúng sai.
- Mô hình chỉ **đọc câu thành một bản ghi có cấu trúc (IR)**.
- Một hàm kiểm bằng code (`ground`) buộc mỗi con số, bội số và năm trong IR phải có nguyên văn trong câu gốc.
- Phép so sánh do thư viện tất định `irlib` làm, với dung sai đúng bằng độ chính xác mà doanh nghiệp đã công bố.

Trên 87 ca ngoài mẫu đã làm sạch, bốn mô hình 4B–32B đọc theo cách này có **0 kết luận sai**. Luật thuần cũng 0 kết luận sai, nhưng gần như không dám kết luận (1/87 ca). Còn hai rủi ro chưa khép:
- bảng PDF bị dàn phẳng;
- câu có nhiều số liệu cùng loại.

Gặp hai trường hợp này, hệ thống trả "chuyển người", không kết luận.

## 3. Lập luận

### 3.1. Bịa số bị chặn ở kiến trúc, không phải nhờ hy vọng mô hình ngoan

**[KIẾN THỨC NỀN]** Mô hình ngôn ngữ sinh văn bản theo xác suất. Nó có thể viết ra một con số "hợp lý" mà tài liệu không hề có. Đây là lý do bất biến 5 của GreenScan ghi rõ: "Số học là của code"; mô hình không được ghi đè phép so sánh tất định (`docs/00-project/ARCHITECTURE_INVARIANTS.md`).

Đường đi của một kết luận định lượng gồm ba bước, mỗi bước có một chốt chặn kiểm được:
1. **Đọc.** Mô hình điền IR cho từng số liệu môi trường trong câu: chỉ số, giá trị nguyên văn, bội số, đơn vị, loại giá trị (tuyệt đối / cường độ / tỷ trọng / thay đổi), kỳ, năm gốc, phạm vi phát thải, ranh giới tổ chức, thực hiện hay mục tiêu. Prompt nằm ở `experiments/AG-1/ag1_worker.py` và `src/quantum_gw/verification/ir_reader.py`.
2. **Neo vào câu gốc** (`irlib.ground`):
   - con số phải xuất hiện nguyên văn trong câu;
   - bội số ("nghìn", "triệu", "tỷ") phải là chữ câu viết ngay sau số đó;
   - năm phải là năm câu có viết.

   Số liệu nào không neo được thì bị bỏ. Không có số liệu thì không có kết luận.
3. **So sánh** (`irlib.compare`, `irlib.decide`):
   - lệch một chiều bất kỳ (chỉ số, loại giá trị, kỳ, phạm vi, ranh giới, đơn vị, thực hiện / mục tiêu) thì trả N, **không bao giờ trả C** (bất biến 4);
   - mục tiêu không chứng minh thành tích (bất biến 6);
   - giá trị được so trong dung sai bằng tổng nửa đơn vị chữ số cuối mà mỗi bên đã viết.

   Mỗi kết luận vì thế mang theo phép tính, ví dụ "|2,35e+07 − 2,34745e+07| = 25 520 tCO2e; dung sai 50 000,5".

Như vậy, để bịa được một con số, mô hình phải viết ra một chuỗi số **có sẵn trong câu**. Cái tệ nhất nó làm được là gán nhầm một số có thật cho sai chỉ số. Rủi ro đó thuộc loại "tính sai", đo ở mục 3.3.

### 3.2. Dung sai theo độ chính xác công bố: không làm tròn quá tay, không bắt bẻ vô lý

**[ĐÃ THỰC NGHIỆM]** Các ca dựng của size ladder (F01–F27, `benchmark/size_ladder_2026-10-10/cases.py`) được dùng làm test cho `irlib`:

| Ca | Tuyên bố | Bằng chứng | Nhãn mong đợi | `irlib` |
|---|---|---|---|---|
| F01 | khoảng 23,5 triệu tCO2e | 23.474.480 tCO2e | S | S (chênh 25 520 ≤ dung sai 50 000,5) |
| F03 | 21,4 triệu tCO2e | 23.474.480 tCO2e | C | C (chênh khoảng 2,07 triệu) |
| F22 | 15 triệu m3 | 15.000 m3 | C | C (lệch bội số 1 000 lần) |
| F23 | 15 triệu m3 | 15.000.000 m3 | S | S |
| F13 | Phạm vi 1 + 2 | Phạm vi 1 | N | N (khác phạm vi) |
| F16 | "đã giảm 30%" | mục tiêu 30% đến 2030 | N | N (thực hiện ≠ mục tiêu) |

Hai ca cùng giá trị 12 % và 11,6 % cho kết quả khác nhau, và đó là chủ đích:
- "12 %" khớp, vì dung sai là 0,5 + 0,05;
- "12,0 %" không khớp, vì dung sai chỉ còn 0,05 + 0,05.

Ai viết số chính xác hơn thì bị so chặt hơn.

### 3.3. "Tính sai" đã xảy ra thật, được đo, và đã sửa bằng code

**[ĐÃ THỰC NGHIỆM]** Lượt AG-1 đầu tiên (31/10, 193 ca, Kaggle) cho thấy hai lỗi định dạng của mô hình. Chúng không phải lỗi hiểu nghĩa (`experiments/AG-1/README.md`, mục 5).
- **Qwen3-32B: cả 11 kết luận sai cùng một lỗi.** Mô hình tự thêm bội số mà câu không viết, đọc "10.730 m3" thành "10.730 ngàn m3". Một số liệu đúng thành sai 1 000 lần, nên tuyên bố đúng bị kết luận C. Đây chính là kiểu "tính sai" ban giám khảo lo.
- **Qwen3-4B:** nhét cả bội số lẫn đơn vị vào ô giá trị ("23,5 triệu tCO2e"). Bộ đọc số từ chối, nên 4B gần như chỉ trả N: an toàn, nhưng vô dụng.

Sửa bằng `irlib.ground()`, có 9 test hồi quy ở `tests/test_irlib_ground.py`. Không mô hình nào phải chạy lại; đầu ra thô được chấm lại bằng `experiments/AG-1/rescore.py`. Một test còn bắt thêm một lỗi của chính bộ neo: "85 tỷ lệ" bị đọc thành bội số "tỷ".

| B-b, 142 ca, **trong mẫu** | CONTRADICTED sai trước → sau | precision trước → sau |
|---|---|---|
| Qwen3-8B | 6 → 0 | 0,64 → 0,983 |
| Qwen3-32B-AWQ | 7 → 1 | 0,82 → 0,985 |
| Qwen3-1.7B | 8 → 0 | 0,54 → 0,85 |

Số trong mẫu chưa phải bằng chứng, vì cách sửa được rút ra từ chính các ca này. Vì vậy đội **đăng ký trước** rồi mới kiểm ngoài mẫu: khối `agentic_v1_1` và `agentic_v1_2` trong `configs/measurement_decisions.yaml`.
- Trên 246 ca mới của v1.1 (lượt D, E, F), 4B có `ground` đạt precision 0,903 nhưng còn 2 ca CONTRADICTED sai. Đội ghi đúng như vậy: **trượt** cổng an toàn đã đăng ký (vu oan ≤ luật + 1).
- Lỗi này dẫn tới bản v1.2: đơn vị đếm được coi là tuyệt đối, và thêm một "C-guard". Bản này chỉ được đánh giá trên tập ngoài mẫu mới (lượt G).

### 3.4. Trên dữ liệu ngoài mẫu sạch: không kết luận sai nào

**[ĐÃ THỰC NGHIỆM]** Tập ngoài mẫu v1.2 có 162 ca. Khi hậu kiểm, đội phát hiện tập này có lỗi:
- 60 ca dựa trên số liệu không phải môi trường;
- 5 ca có năm bị lấy từ dòng tiêu đề "BÁO CÁO THƯỜNG NIÊN 2022" dính vào câu;
- 10 ca có tuyên bố méo.

Các ca này được loại theo quy tắc tất định (`benchmark/gs_bench_v1/clean_v13.py`, danh sách ở `errata_v13.txt`), **không gán lại nhãn nào**. Trên 87 ca còn lại (`experiments/AG-1/out/v13/score_heldout.json`):

| Hệ | Độ phủ | Precision | SUPPORTED sai | CONTRADICTED sai |
|---|---|---|---|---|
| Luật hiện tại | 0,011 | 1,0 | 0 | 0 |
| Qwen3-4B | 0,138 | 1,0 | 0 | 0 |
| Qwen3-8B | 0,115 | 1,0 | 0 | 0 |
| Qwen3-14B-AWQ | 0,115 | 1,0 | 0 | 0 |
| Qwen3-32B-AWQ | 0,253 | 1,0 | 0 | 0 |

**Giới hạn của bảng này:**
- Mỗi mô hình chỉ dám kết luận 10–22 ca, nên cận dưới của precision chưa chặt.
- Nhãn là **bạc**: số liệu bằng chứng do Claude và Qwen3-32B đọc, có bộ kiểm tất định, nhưng chưa đối chiếu với người.
- Số của 32B lạc quan, vì 32B tham gia chọn số liệu của tập.

### 3.5. So với để mô hình tự phán

**[ĐÃ THỰC NGHIỆM]** Size ladder (10/10, 51 ca dựng, `docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`) cho các mô hình tự xếp nhãn S / C / N, từ 26B đến 753B tham số.
- **Mọi** mô hình đều báo SUPPORTED sai trên cùng hai ca có bảng GHG bị dàn phẳng (N02, N05).
- Khi chỉ cho mô hình ánh xạ số đã che, còn code so sánh, SUPPORTED sai về 0 ở mọi mô hình.

Đây là lý do GreenScan tách "đọc" khỏi "tính": lỗi của cách tự phán không giảm khi tăng cỡ mô hình, còn lỗi của cách tách thì sửa được bằng code và test.

### 3.6. Luật thuần cũng có thể sai

**[ĐÃ THỰC NGHIỆM]** Trên tập hiệu chỉnh sạch (397 ca B-b), bộ luật hiện tại có 9 ca SUPPORTED sai. Các lỗi đã ghi từ 10/10:
- nhầm cường độ với tuyệt đối;
- ngưỡng 0,35 che các chênh lệch 9–25 %.

Chính sách hai đường (AG-2, `experiments/AG-2/policies.py`, đăng ký `agentic_ag2_v1`) **bỏ phiếu S đơn độc của luật**. Nhờ vậy, đường "luật + 4B" giữ 0 kết luận sai trên tập ngoài mẫu G, trong khi vẫn tăng độ phủ (CI của phần tăng là [0,016; 0,185]). Từ đây, "tính sai" của luật cũng trở thành chuyển người thay vì kết luận.

### 3.7. Rủi ro còn mở

| Rủi ro | Vì sao chưa khép | Hệ thống làm gì lúc này |
|---|---|---|
| Bảng PDF bị dàn phẳng (F3) | AG-3 (dựng bảng có cấu trúc, kiểm cộng ngang) chưa chạy | Chưa đo trên bảng thật; GS-Bench B-b chưa có bảng **[GIẢ THUYẾT]** |
| Câu có hai số cùng loại ("gas 39 % và xăng dầu 14 %") | IR không tách được hai nhiên liệu cùng mã chỉ số | `decide()` thấy vừa khớp vừa lệch nên trả N. Đã thấy trên IR gold: 2/142 ca |
| OCR sai chữ số | Chưa có bộ đo OCR | `ground()` chỉ bảo đảm số có trong chữ đã OCR, không bảo đảm OCR đúng |
| Quy đổi chéo đơn vị (TOE ↔ kWh, GJ) | Có trong `irlib` nhưng chưa có ca thật để kiểm | **[GIẢ THUYẾT]** |
| Bộ đọc nén Q4 chạy trên laptop đọc khác bản Kaggle | Chưa đo được: máy thiếu RAM ngày 01/11 (đăng ký `agentic_ag2_product`) | Chưa bật trong sản phẩm |

## 4. Thí nghiệm được dẫn (khung 10 điểm, rút gọn)

**AG-1 · IR + `irlib` + `ground`** (`experiments/AG-1/README.md`)
1. **Vấn đề:** luật quyết định 4/142 ca trên câu thật.
2. **Dự đoán (`agentic_v1`):** 4B có độ phủ ≥ 0,35 và precision ≥ 0,90. Kết quả: dự đoán sai về độ phủ, đạt về precision.
3. **Phương pháp:**
   - mô hình điền IR, code so sánh;
   - phương án bỏ: mô hình tự phán (trái bất biến 5), và giải mã ràng buộc (tham số vLLM không ổn định giữa các phiên bản).
4. **Cấu hình:**
   - Qwen3 0.6B / 1.7B / 4B-Instruct-2507 / 8B / 14B-AWQ / 32B-AWQ;
   - vLLM 0.32.0, fp16, greedy, `max_len` 4096;
   - Kaggle T4 × 2, notebook `gs-ag1-a` … `gs-ag1-g`; tài khoản liệt kê ở `docs/RUNS.md`.
5. **Kết quả:** các bảng ở mục 3.3 và 3.4.
6. **Giới hạn:**
   - nhãn bạc;
   - mỗi mô hình chỉ 10–22 ca dám kết luận ngoài mẫu;
   - chưa có bảng;
   - tuyên bố sinh bằng khuôn câu.
7. **Thất bại:**
   - lỗi bội số của 32B;
   - 4B nhét đơn vị vào giá trị;
   - năm bịa từ tiêu đề trong tập ngoài mẫu (01/11).
8. **Khái niệm:** IR, `ground`, dung sai theo độ chính xác công bố (`docs/00-project/GLOSSARY.md`).
9. **Hình:** CONTRADICTED sai trước và sau `ground` theo mô hình. Dữ liệu ở `experiments/AG-1/out/score_ag1_ground.json` và `out/v13/`.
10. **Bước tiếp:** AG-3 cho bảng; tách câu nhiều số; đo bộ đọc trên laptop.

**Size ladder** (`benchmark/size_ladder_2026-10-10/`)
- 51 ca dựng; bảy hệ, gồm luật, Ollama qwen3:8b và các mô hình FPT 26B–753B.
- Kết quả: mọi mô hình tự phán đều báo SUPPORTED sai trên N02 và N05. Cách che số rồi để code so sánh đưa SUPPORTED sai về 0.

## 5. Câu hỏi vặn của BGK

- **"Nếu doanh nghiệp viết sai số trong chính báo cáo thì sao?"**
  - GreenScan kiểm tuyên bố so với bằng chứng, không kiểm sự thật ngoài tài liệu.
  - Hai số tự mâu thuẫn trong một tài liệu sẽ được nêu ra (v3 D4, kiểm cộng ngang).
  - Số sai cả ở hai nơi thì cần bằng chứng độc lập: Climate TRACE, GEM, danh mục QĐ 13. Xem `docs/07-presentation/nghien-cuu/B_NGUON_DU_LIEU_BO_SUNG.md`.
- **"Mô hình đọc nhầm số này sang chỉ số khác thì sao?"**
  - Đó là rủi ro còn lại sau khi đã chặn bịa số. Nó hiện ra thành nhầm chỉ số, kỳ hay phạm vi.
  - `irlib` cấm trả C khi lệch một chiều, nên lỗi đọc thường thành N chứ ít khi thành vu oan.
  - Trên 87 ca ngoài mẫu sạch, số vu oan là 0.
- **"0 lỗi trên vài chục ca thì chứng minh được gì?"**
  - Chứng minh được rằng tỷ lệ vu oan **chưa đo thấy**. Chưa chứng minh nó thấp tới mức nào.
  - Muốn có cận dưới chặt cần ≥ 60 ca dám kết luận và nhãn người (D-2026-09-22-05).
- **"Sao không dùng mô hình lớn nhất cho chắc?"** Sau khi sửa định dạng, hiệu ứng cỡ trong mẫu gần như biến mất: độ phủ 0,408–0,465 cho 8B–32B. Lỗi lớn nhất là định dạng, sửa bằng code rẻ hơn tăng cỡ.

## 6. Không được nói

- "GreenScan không bao giờ sai" hay "độ chính xác 100 %". Đúng là 0 kết luận sai trên 87 ca bạc ngoài mẫu, với 10–22 ca dám kết luận mỗi mô hình.
- "Mô hình đã kiểm chứng số liệu". Mô hình chỉ đọc; code so sánh.
- "Đã xử lý bảng PDF". AG-3 chưa chạy.
- "Bộ đọc đã có trong sản phẩm". Chưa: còn chờ đo trên laptop và cổng 06/11.
