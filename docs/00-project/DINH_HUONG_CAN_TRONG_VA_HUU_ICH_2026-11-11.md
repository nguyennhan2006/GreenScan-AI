# Định hướng: cẩn trọng nhưng hữu ích (11/11/2026)

Trạng thái: **đề xuất, chờ Nhân duyệt.** Chưa sửa mã và chưa đăng ký đo lường nào.

## 1. Câu định hướng

> GreenScan không thay kiểm toán viên kết luận doanh nghiệp có tẩy xanh hay không. GreenScan dùng AI để tìm và hiểu bằng chứng, dùng các quy tắc có thể kiểm toán để kiểm chứng thông tin, rồi giúp người soát tập trung vào những tuyên bố đáng kiểm nhất.

Ba vế ứng với ba phần đã có trong hệ thống:

| Vế | Phần trong hệ thống | Tình trạng |
|---|---|---|
| AI tìm và hiểu bằng chứng | Truy xuất; bộ đọc `verification/ir_reader.py` (Qwen3-4B cục bộ qua Ollama) | Bộ đọc nằm sau cờ `QUANTUM_VERIFY=dual`, **chưa bật** |
| Quy tắc kiểm chứng | Verifier, cổng G0–G8, các bất biến có kiểm thử | Có. Mô hình không bao giờ tự quyết một mình |
| Giúp người soát tập trung | `agents/prioritizer.py`, `configs/priority_v1.yaml` (hàng đợi 5–25 mục, ngưỡng 55) | Có, **chưa đo mức bỏ sót** |

Phần cẩn trọng vẫn giữ nguyên. Hệ thống hữu ích hơn nhờ AI kết luận thêm được những ca luật bỏ ngỏ và nhờ hàng đợi xếp đúng hơn, chứ không bỏ chốt chặn nào. Mỗi số đo về độ hữu ích luôn báo kèm một số đo an toàn: độ phủ đi cùng số kết luận sai, công sức tiết kiệm đi cùng tỷ lệ bỏ sót.

## 2. Hai điều phải chứng minh

### 2.1 AI giải được những ca luật không giải được

**Đã có số** (nhãn máy, chưa phải nhãn người; `configs/measurement_decisions.yaml`, khối `agentic_ag2_v1` và `agentic_ag2_product`):

| Tập | Chỉ luật | Luật + Qwen3-4B cục bộ (bản Q4 chạy trong sản phẩm) |
|---|---|---|
| GS-Bench v1, 453 ca | kết luận dứt khoát 7,7 %, đúng 24/35 | — |
| Tập ngoài mẫu G, 162 ca, doanh nghiệp mới | độ phủ 0,6 % | độ phủ **8,0 %**, 0 "ủng hộ" sai, 0 "mâu thuẫn" sai; phần tăng CI95 [1,6; 17,5] điểm |

**Giới hạn phải nói thật:**
- Chỉ khoảng 15 ca được kết luận, nên bằng chứng an toàn là "15/15 đúng", chưa phải một cận chặt.
- 8 % vẫn là con số nhỏ. Nên nói "AI kết luận thêm được những ca luật bỏ ngỏ", không nói "AI giải quyết phần lớn".
- Bộ đọc chưa chạy trong sản phẩm. Cổng `ag2_dual_path_to_product` còn ba phần chưa kiểm: thời gian đọc trên laptop và thời gian phân tích Hòa Phát không quá 2 lần hiện nay; 17 bẫy xanh; các kiểm thử bất biến khi bật `dual`.

**Việc:**
- **V1.1** Chạy ba phần cổng còn lại. Chỉ cần CPU, 0 giờ GPU. Laptop phải có khoảng 3,3 GB RAM trống cho Ollama (lần trước chỉ còn 0,3 GB). Qua cổng thì bật `dual` cho phiên demo.
- **V1.2** Trên trang chi tiết tuyên bố, ghi rõ kết luận nào có được nhờ máy đọc khi luật không kết luận được. Chọn 2–3 ca thật của Hòa Phát làm ví dụ cho slide và demo.
- **V1.3** Slide: hai cột "chỉ luật" và "luật + AI" cho độ phủ, đặt cạnh cột "kết luận sai = 0".

### 2.2 Hàng đợi tiết kiệm công mà không bỏ sót điều quan trọng

**Đã có:**
- Hòa Phát: 156 tuyên bố, hàng đợi 9 mục (5,8 %).
- Điểm ưu tiên tương quan với nhãn ở mức ρ 0,46 [0,23; 0,59] (nhãn Claude, n = 148).
- 30 % câu trích ra không phải tuyên bố (44/146). claim-quality-v1 mới bắt được 15/61. Mục #1 hàng đợi Hòa Phát vẫn là một dòng bị dính chữ.

**Chưa có:** không số nào cho biết hàng đợi bỏ sót bao nhiêu. ρ chỉ đo thứ tự chung. Nó không trả lời được câu BGK sẽ hỏi: "147 câu còn lại thì sao?"

**Cách đo:** dùng chính cách chọn mẫu của kiểm toán, đăng ký trước khi gán nhãn.
- **Hai mức vấn đề.** Quỳnh chốt định nghĩa trước khi gán.
  - *Nghiêm trọng*: người soát phải ghi thành phát hiện trong giấy làm việc. Ví dụ: số liệu trái với nguồn có thẩm quyền; tuyên bố tuyệt đối hay so sánh không có căn cứ; mục tiêu giảm không nêu năm gốc hoặc phạm vi; chứng nhận không nêu bên cấp.
  - *Đáng soát*: nên xin thêm bằng chứng nhưng chưa thành phát hiện.
  - Thêm lựa chọn "không phải tuyên bố".
- **Mẫu.** Lấy ba báo cáo: Hòa Phát và hai doanh nghiệp khác ngành đã có trong kho. Với mỗi báo cáo, lấy mọi mục trong hàng đợi cộng 30 câu rút ngẫu nhiên ngoài hàng đợi (hạt giống cố định). Tổng khoảng 120–130 câu, Quỳnh gán mất khoảng 3–4 giờ.
- **Gán mù.** Người gán không thấy điểm và không biết câu nằm trong hay ngoài hàng đợi (các câu được trộn). Thảo đọc lại 25 % để tính κ, theo cổng `kappa_min` 0,70.
- **Chỉ số:**
  1. *Bỏ sót*: tỷ lệ câu nghiêm trọng ngoài hàng đợi, gộp 90 câu, kèm cận trên Wilson 95 %. Nếu 0/90 thì cận trên là 4,1 %; nếu 0/30 (một báo cáo) thì cận trên là 11,4 %.
  2. *Độ tập trung*: tỷ lệ vấn đề trong hàng đợi chia cho tỷ lệ ngoài hàng đợi (bootstrap theo báo cáo). Đọc theo thứ tự trang thì tỷ lệ này xấp xỉ 1.
  3. *Công sức*: số mục hàng đợi trên tổng số tuyên bố, và số phút soát một báo cáo khi có và không có GreenScan (một lượt bấm giờ theo `benchmark/gs_eval_v2/usability/PROTOCOL.md`).
  4. *Ca đã biết đáp án*: tuyên bố gốc của 4 vụ có phán quyết và 17 bẫy xanh có lọt vào hàng đợi không.

**Khối đăng ký đề xuất.** Các dự đoán dưới đây là bản nháp. Nhân sửa rồi chép vào `measurement_decisions.yaml` **trước khi gán câu nào**.

```yaml
queue_usefulness_v1:
  registered: "<giờ đăng ký>"
  worth_check:
    failure: "chưa có số nào nói hàng đợi bỏ sót bao nhiêu; rho 0.46 chỉ đo thứ tự chung"
    decision: "được nói 'hàng đợi không bỏ sót vấn đề nghiêm trọng' trước BGK hay không; có làm 'mẫu kiểm ngoài hàng đợi' (mục 2.3) hay không"
    cost: "0 GPU; khoảng 4 giờ của Quỳnh, 1 giờ của Thảo"
  labels: "người: Quỳnh gán, Thảo đọc lại 25 %; kappa >= 0.70 trên trường mức độ"
  sample: "3 báo cáo; mọi mục hàng đợi + 30 câu ngẫu nhiên ngoài hàng đợi mỗi báo cáo, seed 20261111; trộn, ẩn điểm và vị trí"
  predictions:
    miss_serious: "<= 2/90 câu ngoài hàng đợi là nghiêm trọng"
    concentration: "tỷ lệ trong / ngoài >= 2, cận dưới > 1"
  say_if: "cận trên miss_serious <= 0.10 và cận dưới concentration > 1"
  else_say: "hàng đợi là thứ tự gợi ý; người soát vẫn phải kiểm mẫu ngoài hàng đợi; sửa chấm điểm trước khi nói thêm"
```

**Việc sửa rẻ giúp hàng đợi hữu ích hơn** (đã có trong mục 4 của `DANH_GIA_HE_THONG_2026-11-05.md`):
- P1: lọc câu không phải tuyên bố để chúng không đứng đầu hàng đợi.
- P1: thành phần điểm không áp dụng thì tính 0.
- Bốn chỗ hiển thị chưa nhất quán ở mục 4 của `TRANG_THAI_NOP_BAI.md`.

### 2.3 Đề xuất sản phẩm: mẫu kiểm ngoài hàng đợi

Mỗi phiên rút thêm 5 câu ngẫu nhiên ngoài hàng đợi, ghi hạt giống vào nhật ký. Người soát đánh dấu từng câu là "có vấn đề" hoặc "không". Giấy làm việc ghi kết quả này ngay dưới đoạn "phạm vi chưa soát" mà `scope_note()` đã viết.

Lý do làm:
- Kiểm toán viên vẫn kiểm phần ngoài vùng rủi ro theo cách này, nên BGK chuyên ngành sẽ nhận ra ngay.
- Phép đo ở mục 2.2 trở thành một bước làm thường ngày. Mỗi phiên dùng thật góp thêm dữ liệu về tỷ lệ bỏ sót.

Việc này chạm vào prioritizer, giao diện và giấy làm việc, nên làm sau cờ. Nhân quyết làm trước hạn đóng băng mã 20/11 hay để sau.

## 3. Lịch đề xuất

| Ngày | Việc | Ai |
|---|---|---|
| 11–12/11 | Duyệt định hướng. Chốt định nghĩa hai mức. Đăng ký `queue_usefulness_v1` | Nhân, Quỳnh |
| 12–14/11 | V1.1 (cổng `dual`). Chọn 3 báo cáo, rút mẫu, xuất phiếu gán mù | Nhân |
| 14–18/11 | Gán khoảng 130 câu; Thảo đọc lại 25 % | Quỳnh, Thảo |
| 18–19/11 | Chấm, ghi kết quả vào khối đăng ký. Đưa câu định hướng và số liệu vào báo cáo và slide | Nhân |
| 20/11 | Đóng băng mã, dựng lại zip, nộp. Vế 2 chưa có số thì ghi "đang đo", không ghi số | Đội |
| 21–27/11 | Mẫu kiểm ngoài hàng đợi (nếu duyệt). Cập nhật demo và ngân hàng câu hỏi | Nhân |

Lưu ý phối hợp: sáng 11/11 có một phiên đang sửa mã (ADR 0004: báo cáo thay đổi và chống chèn lệnh). Mọi sửa mã ở trên phải đợi phiên đó xong.

## 4. Câu nói trước BGK (nháp; điền số vế 2 khi có)

"Chỉ dùng luật thì hệ thống chỉ dám kết luận chưa tới 1 % tuyên bố của các doanh nghiệp mới. Thêm một mô hình 4 tỷ tham số chạy ngay trên laptop, phần kết luận được tăng lên 8 % mà không có thêm kết luận sai nào trên tập kiểm. Những tuyên bố còn lại vẫn không bị bỏ qua: GreenScan xếp chúng thành hàng đợi cho người soát. Trên [n] câu chọn ngẫu nhiên ngoài hàng đợi, người soát tìm thấy [k] vấn đề nghiêm trọng."

Nếu BGK hỏi thêm về số 8 %: chỉ có khoảng 15 ca được kết luận, nhãn là nhãn máy, và người vẫn chốt mọi kết luận "mâu thuẫn".
