# Kế hoạch theo stage (14/11/2026): luật mới, bộ đo cài lỗi và kết quả

Nguồn yêu cầu: `KE_HOACH_THEO_STAGE.md`, do người dùng gửi tối 14/11. Mọi số dưới đây đều [ĐÃ THỰC NGHIỆM] trên mã hiện tại, và tệp kết quả được ghi kèm từng số.

## 1. Đối chiếu kế hoạch với trạng thái

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| S1.1 #4: năm trong mã chuẩn bị coi là kỳ | Đã xong từ sáng 14/11 | `tests/test_fixes_2026_11_14.py`. B2 của Hòa Phát không còn SUPPORTED |
| S1.1 #4b: "hiện nay" → năm báo cáo | **Chưa làm** | Đổi thuộc tính "kỳ" của nhiều câu trên Ca B, kéo theo đổi điểm rủi ro. Cần một đợt đo riêng |
| S1.1 #10: mã kết luận của harness | Đã xong từ sáng 14/11 | |
| S1.1 #6: "bỏ qua mọi chỉ dẫn" | Đã xong từ sáng 14/11 | |
| S1.1 #9: chốt chống bịa số coi "Scope 3" là số mới | **Xong tối 14/11** | `assist/guards.py`: bỏ số thuộc nhãn (phạm vi/Scope 1–3, ISO, TCVN, IEC, GRI) trước khi so. Số liệu thật vẫn bị chặn |
| S1.2: tập đánh giá + đo theo tầng | **Xong một phần** | Có GS-Mutation v1 (M0–M7, chia theo công ty, Wilson 95%, ngưỡng đăng ký trước), mốc LLM gpt-oss-120b, và phát lại trên 1.766 câu thật. **Chưa có** tập nhãn người 150–200 câu: phải có người gán, máy không làm thay được |
| S1.3: tuyên bố tuyệt đối → tính tỷ trọng | **Xong**, bật mặc định | `absolute-share-v1`. A2 → CONTRADICTED, lý do "320 tỷ đồng / 500 tỷ đồng = 64%" |
| S1.4: nguồn gốc nhãn 0–100 | **Xong** → quyết định bỏ S2.3 | Xem mục 4 |
| S2.1: mâu thuẫn nội bộ có điều kiện | **Đã làm, để tắt** | `internal_inconsistency: off`. Không qua ngưỡng, xem mục 3 |
| S2.2 lớp luật: tuyệt đối ↔ một phần | **Xong**, bật mặc định, chỉ dùng cụm mạnh | Danh sách cụm của kế hoạch báo nhầm 17/17 cờ trên câu thật |
| S2.2 lớp mô hình (mDeBERTa) | **Chưa làm** | `.venv` không có transformers/torch. Mô hình đã có trong cache HF của Python hệ thống |
| S2.3: học lại trọng số rubric | **Bỏ** | Nhãn do Claude gán theo chính rubric đó, học lại sẽ thành vòng lặp |
| Phát sinh từ bộ đo: `figure-consistency-v1` | **Xong**, bật mặc định | Hai lỗ bỏ lọt mà GS-Mutation tìm ra, xem mục 2.3 |
| Chiều "mảng" trong chính sách so sánh (`comparison-policy-v3`) | **Xong** | Thép ≠ nông nghiệp ≠ bất động sản ≠ điện máy ≠ xi măng. Không xác định được thì không chặn |

## 2. Các luật mới

Mọi luật mới nằm trong `verification` (`configs/default.yaml`) và đều có biến môi trường để tắt.

### 2.1. `absolute-share-v1` (`absolute_share_check: true`, biến `QUANTUM_ABSOLUTE_SHARE`)

"Hoàn toàn / toàn bộ / tất cả / 100%" nói về việc dùng vốn của một công cụ tài chính xanh có tên (trái phiếu xanh, tín dụng xanh, khoản vay xanh…) là tuyên bố tỷ trọng = 100%. Luật chỉ chạy khi trong cùng một đoạn có đủ ba thứ:
- tên công cụ đó;
- đúng một số **tổng** (khoản thu, tổng giá trị phát hành, hạn mức…);
- số **đã dùng** (đã giải ngân / phân bổ / sử dụng) hoặc **chưa dùng** (chưa phân bổ, tiền gửi, đầu tư tạm thời), cùng loại tiền với số tổng. Tổng các phần không được lớn hơn số tổng.

Từ đó:
- tỷ trọng = đã dùng / tổng, hoặc (tổng − chưa dùng) / tổng;
- lệch so với 100% từ 35% trở lên → mâu thuẫn; bằng 100% → khớp; ở giữa → PARTIAL.

Lý do ghi lại nguyên phép tính. Luật nằm trong nhánh so số, nên chốt chống vu oan (cùng tài liệu) vẫn giữ nguyên. Mã: `verification/absolute.py`, `VerificationAgent._absolute_share`.

### 2.2. `stance-cues-v3`, lớp luật (`absolute_conflict_cues: true`, biến `QUANTUM_ABSOLUTE_CONFLICT`)

Tuyên bố có từ tuyệt đối (hoàn toàn, toàn bộ, tất cả, 100%, mọi, duy nhất, không phát thải, đã hoàn thành…) gặp một câu của đoạn bằng chứng thoả cả hai điều kiện:
- có chung ít nhất một cặp âm tiết nội dung với tuyên bố;
- nói rõ việc **chưa xong**: "chưa (được) phân bổ / giải ngân / sử dụng / hoàn thành", "not yet allocated", "unallocated".

Khi đó: PARTIALLY_SUPPORTED, cờ `absolute_claim_conflict`, và tuyên bố vào hàng soát (`raised_by: flag:absolute_claim_conflict`). Luật này **không bao giờ** ra CONTRADICTED.

Kế hoạch đề xuất danh sách cụm rộng hơn: còn lại, một phần, phần lớn, đang triển khai, giai đoạn 1… Danh sách đó đã được phát lại trên 1.766 câu thật và cho 17 cờ mới, đọc tay **0 cờ đúng**. Ví dụ báo nhầm: "giai đoạn đầu" của vòng đời thép, "một phần cốt lõi trong chiến lược", "the remaining breweries". Danh sách rộng được giữ trong `WEAK_PARTIAL_CUES` nhưng không dùng. Danh sách hẹp cho **0 cờ** trên câu thật.

### 2.3. `figure-consistency-v1` (`figure_consistency_check: true`, biến `QUANTUM_FIGURE_CONSISTENCY`)

Hai lỗ bỏ lọt do GS-Mutation v1 tìm ra:
1. **Đảo hướng.** "giảm 12,8%" sửa thành "tăng 12,8%" vẫn SUPPORTED ở 5/5 ca có bản gốc SUPPORTED, vì con số vẫn khớp. Nay số khớp mà câu bằng chứng chỉ có từ xu hướng ngược thì ra **mâu thuẫn**, lý do "Số liệu khớp (…) nhưng ngược hướng".
2. **Câu có hai số.** Một số khớp, số kia lệch xa (≥ 35%) so với số cùng loại trong tài liệu. Nay ra PARTIAL, không còn SUPPORTED.

### 2.4. `internal-inconsistency-v1` (`internal_inconsistency: off | flag | contradict`)

Số trong lời văn được phép lệch với số trong bảng của cùng báo cáo chỉ khi đồng thời thoả:
- đoạn là bảng hoặc trang dữ liệu (GRI 3xx, "bảng số liệu", "chỉ số môi trường", "phụ lục", "bảng N");
- cặp số so được theo `comparison-policy-v3`;
- đoạn có năm kỳ của tuyên bố, và cả năm gốc nếu là mức thay đổi;
- không có số OCR đáng ngờ;
- gần đó không có chữ "điều chỉnh / trình bày lại / restated";
- đoạn đó không phải đoạn chứa chính tuyên bố.

Chưa làm điều kiện "bảng cộng dọc khớp" (`cross_foot`).

## 3. Kết quả đo

**Ngưỡng.** Đăng ký trước trong `benchmark/gs_mutation_v1/PREREG_2026-11-14.md`. Lưu ý trung thực:
- tệp ngưỡng được viết **sau** lần phát lại đầu tiên trên câu thật (lần đó đã cho thấy kết quả của lớp cụm từ và của luật nội bộ);
- tệp ngưỡng được viết **trước** mọi lần chạy GS-Mutation.

### 3.1. GS-Mutation v1

Lệnh: `benchmark/gs_mutation_v1/{build,run,score}.py`. Kết quả: `RESULTS.md`, `results.json`.

Tập gồm 865 ca, lấy từ cặp GS-Bench của 8 công ty thật:
- *dev*: hpg, ctd, pow;
- *test*: bvh, dhg, tra, vnm, pnj.

Luật đã từng được chỉnh trên GS-Bench, nên *test* không phải tập chưa thấy. Số dùng để so cấu hình, không để công bố độ chính xác.

| Kiểu cài lỗi | Trước (tắt luật mới) | Sau (mặc định) |
|---|---|---|
| M0 bản gốc → **không** thành CONTRADICTED (vu oan) | 290/290 | 290/290. Tỉ lệ vu oan 0% [0–1,3%] |
| M1 phóng đại số → CONTRADICTED | 11/101 | 11/101 |
| M2 đảo tăng/giảm → CONTRADICTED | 0/17 | **5/17** |
| M3 lùi năm gốc → không còn SUPPORTED | 9/10 | 9/10 |
| M4 xoá phạm vi → báo thiếu phạm vi | 2/6 | 2/6 |
| M5 tuyệt đối hoá → không còn SUPPORTED | 26/28 | 26/28 |
| M6 chèn từ quảng bá mơ hồ → cờ mơ hồ | 0/104 | 0/104 |
| M7 thay bằng chứng của công ty khác → không còn SUPPORTED | 104/104 | 104/104 |
| Ca cài lỗi mà vẫn **SUPPORTED** (bỏ lọt nguy hiểm, M1/M2/M3/M5/M7) | 10 | **5** |
| M1i một tài liệu, phóng đại số → CONTRADICTED hoặc cờ nội bộ | 0/101 (`off`) | 0/101 (`flag` và `contradict` cũng 0) |

**Cách đọc:**
- **Nút thắt là bước trích tuyên bố, không phải bước kiểm chứng.** 63/104 câu gốc nhãn S không được trích thành tuyên bố. Chỉ 15/104 câu ra SUPPORTED, nên số ca M1 bắt được bị chặn trên ở mức đó. Tính riêng 14 ca M1 có bản gốc SUPPORTED: 11 thành CONTRADICTED.
- **M4.** Thuộc tính "phạm vi / ranh giới" coi ranh giới ("của 4 nhà máy") là đủ, nên xoá "phạm vi 1" mà còn ranh giới thì không báo thiếu. Đây là đúng định nghĩa hiện tại.
- **M6.** Từ quảng bá gắn vào câu có số không làm câu thành "mơ hồ". Đây là một hạn chế mới tìm thấy.

### 3.2. Phát lại trên 1.766 câu thật đã lưu (147 phiên)

Lệnh: `benchmark/gs_eval_v2/replay_stage_rules.py`. Kết quả: `results/replay_stage_rules.json`.

| Cấu hình | Câu đổi so với trước | Hòa Phát (156 câu) | GS-Eval v2: số kết luận dứt khoát / precision / CONTRADICTED sai |
|---|---|---|---|
| Tắt hết | 0 | 154 PARTIAL / 1 SUPPORTED / 1 INSUFFICIENT | 8 / 0,375 / 1 |
| + `figure-consistency-v1` | 3 (2 SUPPORTED sai → CONTRADICTED, 1 SUPPORTED → PARTIAL) | không đổi | 7 / 0,429 / 1 |
| + `absolute-share-v1` | +1 (A2) | không đổi | không đổi |
| + lớp cụm từ (danh sách hẹp) | +0 | không đổi | không đổi |
| + nội bộ `flag` | +1 cờ, **đọc tay: sai** (số "3,26%" của SABECO lẫn chữ) | không đổi | không đổi |
| + nội bộ `contradict` | như trên | không đổi | 8 / 0,375 / **2** (thêm 1 CONTRADICTED sai) |

→ Luật nội bộ cho 0 cờ đúng trên 1 cờ và tạo thêm CONTRADICTED sai, nên **không qua ngưỡng** và để `off`. Nó không bắt được câu nào trong GS-Mutation vì điều kiện rất chặt, và chỉ chạy khi đoạn là bảng hoặc trang dữ liệu có năm kỳ. Có thể bật thử trong một phiên bằng `QUANTUM_INTERNAL_INCONSISTENCY=flag`.

### 3.3. GS-Bench v1 (453 ca) và evaluate-real

| | Trước (sáng 14/11) | Sau |
|---|---|---|
| Số kết luận dứt khoát | 35 | 35 |
| Đúng | 24 (0,686) | **26 (0,743)** |
| "Ủng hộ" sai | 10 | **8** |
| "Mâu thuẫn" sai | 1 | 1 |

Hai ca đổi đều thuộc họ đảo hướng có nhãn C: `bb-e6f8…-C3` và `bb-afe2…-C3`. evaluate-real (4 vụ đã có phán quyết) không đổi, chỉ khác mã phiên.

### 3.4. Mốc "đưa thẳng cho LLM"

Lệnh: `benchmark/gs_mutation_v1/llm_baseline.py`. Kết quả: `llm_baseline_results.json`.

Thiết lập: gpt-oss-120b qua Groq, `reasoning_effort: low`. Mô hình đọc cùng tuyên bố và cùng bằng chứng, rồi chọn 1 trong 5 mức. Mỗi câu được hỏi 2 lần. Phạm vi là phần *test*: M0 (bản gốc S), M1, M2, M5, tổng 183 ca.

| Trên cùng 183 ca | GreenScan (luật) | gpt-oss-120b đọc thẳng |
|---|---|---|
| M0, 75 bản gốc → CONTRADICTED (vu oan) | 0 | **1** |
| M0, 75 bản gốc → SUPPORTED | 10 | 67 |
| M1 phóng đại số → CONTRADICTED | 9/72 | **47/72** |
| M2 đảo hướng → CONTRADICTED | 5/16 | **13/16** |
| M5 tuyệt đối hoá → CONTRADICTED | 2/20 | 15/20 (cả hai đều 20/20 "không còn SUPPORTED") |
| Ca cài lỗi mà vẫn SUPPORTED (M1 + M2) | **0** | 5 |
| Hai lần hỏi giống nhau, trả lời khác nhau | 0 (tất định) | **30/183 (16%)** |
| Có phép tính để người soát kiểm lại | Có | Không |

**Cách đọc.** Mô hình bắt nhiều lỗi cài hơn hẳn, và nhận nhiều câu gốc là "ủng hộ" hơn. Lý do một phần là mô hình được đưa thẳng câu tuyên bố, còn GreenScan phải tự trích câu từ văn bản: 63/104 câu gốc không được trích. Đổi lại, mô hình:
- có vu oan (1/75);
- bỏ lọt nguy hiểm ở 5 ca (lỗi đã cài mà vẫn "ủng hộ");
- đổi ý ở 16% câu khi hỏi lại;
- không để lại phép tính.

Kết quả này ủng hộ hướng "mô hình đọc – mã quyết định" (đường đọc kép): dùng mô hình để tăng độ phủ ở bước đọc, còn kết luận vẫn qua phép so của mã.

## 4. S1.4: nguồn gốc nhãn rủi ro 0–100

| Câu hỏi | Trả lời |
|---|---|
| Ai gán? | Claude (`claude-opus-5-5`), hai lượt mù A/B, mỗi lượt 200 câu; 122 câu phải phân xử. Tác giả rà soát. Theo `benchmark/gs_eval_v2/LABELING_GUIDE.md`, mục D-SCORE |
| Gán ở mức nào? | Câu tuyên bố. 148 câu được so với hệ thống |
| "Rủi ro" định nghĩa thế nào? | Theo **chính rubric 9 thành phần của GreenScan** (`configs/scoring_v1.yaml`), tức là thiếu sót công bố, cộng một dải và một kết luận tổng thể. Không phải mức nghiêm trọng của hành vi tẩy xanh |
| Đã ai gán lại chưa? | Hai lượt là **cùng một mô hình**: Spearman 0,734, QWK dải 0,752, κ kết luận 0,691. Chưa có người thứ hai gán độc lập |

**Quyết định:** không học lại trọng số rubric (S2.3). Nhãn sinh từ chính rubric cần hiệu chỉnh, nên học lại chỉ là vòng lặp. Độ khớp giữa hai lượt cùng mô hình lại là một mức trần bị thổi phồng.

Nhãn này chỉ dùng để kiểm tra chéo. Số hiện có: Spearman giữa hệ thống và nhãn là 0,459 (n = 148).

Kế hoạch gốc nhắc tới "bộ khoảng 500 báo cáo + nhãn 0–100". Bộ đó **không tồn tại** dưới dạng có nhãn. Cái có thật:
- `data/crawl/`: 670 tài liệu chưa gán nhãn;
- các bộ nhãn GS-Bench và GS-Eval v2 nói ở trên.
