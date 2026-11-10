# PQ-06 · Chưa có nhãn người thì lấy gì để nói GreenScan đúng?

Bản nháp 31/10/2026, viết theo khung luận văn ở mục 7 của `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`. Các chỗ ghi **[CHỜ]** sẽ điền khi lượt Kaggle D, E, F xong (`docs/RUNS.md`).

Nhãn: **[ĐÃ THỰC NGHIỆM]** là số của đội, kèm n và đường dẫn. **[KIẾN THỨC NỀN]** là kiến thức chung của ngành. **[NGOÀI]** là tài liệu bên ngoài. **[GIẢ THUYẾT]** là điều chưa kiểm.

## 1. Câu hỏi

Ban giám khảo hỏi: "Đội nói hệ thống kết luận đúng, nhưng chưa có người gán nhãn. Vậy đúng so với cái gì?"

## 2. Trả lời ngắn

Chúng tôi không nói "độ chính xác" trên dữ liệu thật, vì chưa có nhãn người. Hiện có 0 nhãn người: 88 cặp trong `data/gold/sessions` đều trống, 79 câu T1 lô 1 cũng trống.
Thay vào đó, chúng tôi đo trên **bộ ca có đáp án theo cấu trúc** (GS-Bench). Mỗi tuyên bố được dựng từ một số liệu thật, rồi bị làm nhiễu có chủ đích, nên đáp án đúng được biết trước khi hệ thống chạy. Ngưỡng và dự đoán được đăng ký trước mỗi lượt chạy; kết luận nào rút từ lỗi đã thấy thì phải kiểm lại trên ca chưa thấy.

## 3. Lập luận

### 3.1. Đáp án đến từ cách dựng ca, không đến từ hệ thống được đo

- **[ĐÃ THỰC NGHIỆM]** GS-Bench v1.1 (`benchmark/gs_bench_v1/gs_bench_v1.jsonl`) có 453 ca:
  - **B-a**: 51 ca dựng tay. Gồm 32 câu sạch và 19 câu trên trang báo cáo HPG thô.
  - **B-b**: 402 ca sinh tự động từ 77 số liệu thật của 7 doanh nghiệp. Nhãn: S 95, C 123, N 184.
- Cách sinh một ca B-b:
  - Lấy một câu thật có số liệu, ví dụ "Tổng lượng nước sử dụng: 10.730 m3".
  - Đọc số liệu thành một biểu diễn trung gian (IR): chỉ số, giá trị, đơn vị, kỳ, phạm vi phát thải, ranh giới tổ chức, thực hiện hay mục tiêu.
  - Viết lại tuyên bố theo một **họ nhiễu** đã biết đáp án:
    - S0 nhắc lại và S1 làm tròn: đáp án S.
    - C1 đổi giá trị, C2 đổi bội số (nghìn → triệu), C3 đảo chiều tăng/giảm: đáp án C.
    - N1 đổi kỳ, N2 đổi thực hiện thành mục tiêu, N3 đổi phạm vi phát thải, N5 đổi tuyệt đối thành cường độ, N6 đổi chỉ số: đáp án N, vì tuyên bố và bằng chứng không so được với nhau.
- Đáp án được quyết định bởi họ nhiễu, trước khi model nào chạy. Hệ thống được đo không tham gia gán nhãn, nên phép đo không bị vòng lặp.
- **[KIẾN THỨC NỀN]** Đây là kiểu kiểm thử bằng nhiễu có kiểm soát: thay đổi một thứ, biết trước đáp án phải đổi ra sao.

### 3.2. Nhãn vẫn có lỗi, và chúng tôi đo được tỷ lệ lỗi đó

IR của câu thật do Claude đọc một lượt, rồi qua bộ kiểm tất định (`irlib`). Vì vậy B-b là nhãn **bạc**, không phải vàng. Chúng tôi tìm lỗi nhãn bằng hai cách:

1. **Tự kiểm khi sinh:** `irlib` phải tự ra đúng nhãn của từng họ nhiễu. 2 ca lệch đều là lỗi của bộ sinh: C2 nhân "0 trường hợp" thành "0 nghìn trường hợp", giá trị vẫn là 0 nên không thể là C. Đã sửa `build.py`. **[ĐÃ THỰC NGHIỆM]**
2. **Đọc chỗ các hệ độc lập bất đồng với nhãn:** Luật của sản phẩm kết luận C ở 4 ca PV Power có nhãn S hoặc N. Đọc lại thì thấy luật đúng, nhãn sai.
   - Bộ sinh không viết phạm vi phát thải vào câu.
   - Vì vậy "Tổng phát thải phạm vi 2 là 134.820 tấn" thành "Tổng phát thải là 134.820 tấn", nhỏ hơn cả phạm vi 1 (10.973.000 tấn).
   - Ca S0 và N3 của cùng một số liệu thành **cùng một câu** với hai nhãn khác nhau.
   - Đã sửa: 14 ca được sinh lại (`errata_v1_1.txt`). **[ĐÃ THỰC NGHIỆM]**

Tổng cộng 16 trên 455 ca có nhãn sai (3,5 %). Chúng đều nằm ở hai lỗi hệ thống của bộ sinh, không rải ngẫu nhiên. Bài học là **chỗ hệ thống bất đồng với nhãn phải được đọc**, chứ không mặc định coi là lỗi của hệ thống.

### 3.3. Đăng ký trước, rồi tách số trong mẫu khỏi số ngoài mẫu

- **[ĐÃ THỰC NGHIỆM]** Trước lượt AG-1 đầu tiên, khối `agentic_v1` trong `configs/measurement_decisions.yaml` đã ghi cổng (precision ≥ 0,90, cận dưới CI95 ≥ 0,80, CONTRADICTED sai không vượt luật quá 1) và dự đoán cho từng model.
- Kết quả lượt đầu **bác bỏ** hai dự đoán:
  - 4B chỉ phủ 0,134, trong khi dự đoán ≥ 0,35.
  - 32B phủ gấp ba 4B, trong khi dự đoán "không có hiệu ứng cỡ trên 4B".
- Phân loại lỗi (`experiments/AG-1/errors.py`) cho thấy cả hai đều do định dạng, không do năng lực đọc:
  - 32B tự thêm bội số mà câu không viết ("10.730 m3" → "10.730 ngàn m3"). Lỗi này gây ra cả 11 kết luận sai của 32B.
  - 4B nhét "triệu tCO2e" vào ô giá trị, nên mất 50 tuyên bố.
- Sau khi thêm bước giữ số liệu đúng với câu gốc (`irlib.ground`):
  - Precision của 32B lên 0,985, CONTRADICTED sai giảm từ 7 còn 1.
  - Độ phủ của 4B lên 0,437.
- Số này là **trong mẫu**. Cách sửa được rút ra từ chính 193 ca đó, nên nó không phải bằng chứng. Vì vậy, trước khi model nào đọc ca mới, chúng tôi đăng ký khối `agentic_v1_1`: dự đoán cho 246 ca ngoài mẫu, kèm điều kiện bác bỏ ("4B có CONTRADICTED sai > 2 hoặc precision < 0,90 thì `ground` đã khớp quá mức vào v1").
- **[ĐÃ THỰC NGHIỆM]** Kết quả ngoài mẫu của 4B (lượt D, 246 ca, `experiments/AG-1/out/score_heldout_d.json`):
  - Phần an toàn **giữ được, sát nút**: precision 0,903, cận dưới CI 0,81, CONTRADICTED sai 2.
  - Phần độ phủ **sai**: 0,126, trong khi trong mẫu là 0,437.
- Nếu chỉ báo số trong mẫu, chúng tôi đã nói quá độ phủ hơn ba lần. Đây là lý do mọi bản sửa mới (v1.2) đều phải đăng ký và kiểm trên một tập ngoài mẫu nữa.
- **[ĐÃ THỰC NGHIỆM] Sửa báo cáo (31/10 22:40).** Câu "giữ được, sát nút" ở trên chỉ đúng khi so với dự đoán (vu oan ≤ 2). Nhưng cổng `ag1_ir_path_usable`, ghi trước đó, chặt hơn: vu oan không được vượt luật + 1. Trên 246 ca này, luật có 0 vu oan, nên ngưỡng là 1.
  - Với v1.1, 4B (2), 14B (3) và 32B (2) **trượt cổng**. Chỉ 8B (1) qua.
  - Bài học cho cách đo: khi một lần thực nghiệm có cả dự đoán lẫn cổng, phải báo kết quả so với **cả hai**. Dự đoán cho biết giả thuyết đứng hay đổ; cổng cho biết có được đưa vào sản phẩm hay không.
- **[ĐÃ THỰC NGHIỆM]** Dự đoán "trên 4B, kích thước không còn ảnh hưởng" (rút ra từ trong mẫu) **sai** khi ra ngoài mẫu. Độ phủ của 4B / 8B / 14B / 32B là 0,126 / 0,220 / 0,256 / 0,329. Trong mẫu, hiệu ứng này đã bị chính cách sửa che đi.

### 3.4. Không có con số gộp

- **[ĐÃ THỰC NGHIỆM]** Mỗi hệ được báo bằng bốn số trên mỗi tầng: độ phủ (tỷ lệ dám kết luận), precision trên phần dám kết luận, số CONTRADICTED sai (vu oan doanh nghiệp), số SUPPORTED sai (bỏ lọt). Khoảng tin cậy tính bằng bootstrap theo **công ty**, không theo câu, vì các câu của cùng một báo cáo không độc lập với nhau.
- Ví dụ vì sao không gộp: trên 402 ca B-b của v1.1, luật hiện tại có 0 CONTRADICTED sai nhưng 9 SUPPORTED sai, precision 0,625. Luật cho qua cả ca đảo chiều "giảm" thành "tăng". Một con số "đúng 192/402" sẽ giấu cả hai sự thật này. **[ĐÃ THỰC NGHIỆM]** (`experiments/AG-0/out/score_rules_v11.json`).

### 3.5. Khi nào cần nhãn người

- **[GIẢ THUYẾT]** Thứ hạng các hệ trên B-b giống thứ hạng trên tuyên bố thật. Câu B-b sinh theo khuôn, dễ đọc hơn câu thật. Chúng tôi sẽ kiểm bằng cách so thứ hạng trên B-b với thứ hạng trên B-c (cặp thật, nhãn Claude hai lượt mù) và trên B-d (nhãn người, khi có).
- Nhãn Claude **không** được dùng để mở khoá kết luận quyết định của LLM (quyết định D-2026-10-16-01). Chỉ nhãn người mới làm được việc đó.

## 4. Thí nghiệm được dẫn (khung 10 điểm, rút gọn; đủ chi tiết ở README từng thí nghiệm)

**AG-0 · Mốc luật** (`experiments/AG-0/`)
1. Vấn đề: luật hiện tại đúng và sai ở đâu trên ca có đáp án.
2. Dự đoán: độ phủ thấp trên câu thật (đã biết từ size ladder 10/10).
3. Phương pháp: chạy nguyên đường ống offline của sản phẩm trên từng ca; quy về S/C/N.
4. Cấu hình: `run_rules.py`, `QUANTUM_PROFILE=offline`, CPU laptop.
5. Kết quả: v1 B-b có độ phủ 0,028, precision 0,75. v1.1 B-b có độ phủ 0,060, precision 0,625, SUPPORTED sai 9, CONTRADICTED sai 0.
6. Giới hạn: B-b chỉ có 7 công ty, câu sinh theo khuôn.
7. Thất bại: lần chấm đầu trên v1.1 có 4 CONTRADICTED sai. Nguyên nhân là nhãn sai do bộ sinh (mục 3.2), không phải luật.
8. Khái niệm: độ phủ, precision trên phần dám kết luận.
9. Hình: cột độ phủ và precision, mốc luật cạnh mốc IR gold.
10. Bước tiếp: phân loại 9 SUPPORTED sai của luật theo họ nhiễu.

**AG-1 · IR + thư viện so sánh tất định** (`experiments/AG-1/README.md`)
1. Vấn đề: model nhỏ chạy tại chỗ có đọc số liệu đủ tốt để code tự kết luận không.
2. Dự đoán: đã đăng ký trong `agentic_v1` và `agentic_v1_1`.
3. Phương pháp: model chỉ điền IR; mọi phép so số, đơn vị, kỳ, phạm vi do `irlib` làm. Nhờ vậy mỗi kết luận chỉ ra được đúng bước tính.
4. Cấu hình: Qwen3 0.6B–32B (32B dạng AWQ), vLLM 0.32, greedy, tắt thinking. Kaggle T4 × 2, các notebook `gs-ag1-a` đến `gs-ag1-f`.
5. Kết quả: bảng ở README mục 5. Ngoài mẫu: **[CHỜ]**.
6. Giới hạn: số trong mẫu không phải bằng chứng; nhãn B-b là bạc.
7. Thất bại: gemma-3-12b sinh rỗng (OOM); notebook lớn hơn 1 MB bị Kaggle từ chối (lỗi 400).
8. Khái niệm: IR, grounding (giữ số liệu khớp câu gốc), trong mẫu và ngoài mẫu.
9. Hình: độ phủ và precision theo cỡ model, trước và sau `ground`.
10. Bước tiếp: AG-2 (hai đường + cổng đồng thuận), AG-4 (1.7B kém 4B 25 điểm độ phủ).

## 5. Câu hỏi vặn của BGK

- **"Bộ đo do đội tự dựng thì đội tự chấm điểm mình à?"**
  Đáp án đến từ họ nhiễu, có trước khi hệ chạy, và hệ được đo không tham gia gán nhãn. Bộ sinh có lỗi, nhưng chúng tôi công bố cả tỷ lệ lỗi nhãn (16/455) và cách tìm ra.
- **"Câu sinh theo khuôn thì dễ hơn câu thật."**
  Đúng. Vì vậy chúng tôi không gọi số trên B-b là "độ chính xác", và tính đại diện của B-b vẫn là giả thuyết, chờ so thứ hạng trên B-c và B-d.
- **"Sửa lỗi sau khi xem kết quả là overfit."**
  Đúng, với số trong mẫu. Vì vậy cách sửa phải qua 246 ca ngoài mẫu, với điều kiện bác bỏ đã ghi trước.
- **"Sao không thuê người gán nhãn?"**
  Có kế hoạch (B-d, 167 mục), nhưng đến 31/10 chưa có nhãn nào. Chúng tôi nói thẳng điều này, không thay bằng nhãn Claude.

## 6. Không được nói

- "GreenScan đúng 98 %". Precision 0,98 chỉ là trên phần dám kết luận, trên ca dựng, và đang là số trong mẫu.
- "Đã kiểm trên dữ liệu thật". Câu nguồn là thật, nhưng tuyên bố là câu sinh.
- "Không bao giờ vu oan". Đúng là 0 CONTRADICTED sai trên 402 ca B-b với luật, nhưng 402 ca dựng không phải "không bao giờ".
- "Nhãn Claude là gold".
