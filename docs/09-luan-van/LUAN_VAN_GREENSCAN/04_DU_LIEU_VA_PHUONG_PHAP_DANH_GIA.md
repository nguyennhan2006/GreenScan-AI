# Chương 4. Dữ liệu và phương pháp đánh giá

*Chương này trả lời hai câu hỏi: GreenScan được đo trên dữ liệu nào, và phép đo được thiết kế thế nào để một con số có thể đứng trước hội đồng mà không bị hiểu thành "độ chính xác" chung chung. Chương mô tả kho văn bản, ba loại nhãn (ca dựng, ca sinh có kiểm soát, nhãn do Claude gán), bộ GS-Bench v1.x, bộ GS-Eval v2, các chỉ số kèm công thức, quy ước đăng ký trước và các đe doạ tính hợp lệ. Kết quả đo nằm ở Chương 5.*

## 4.1 Nguyên tắc đo khi chưa có nhãn của người

Đến ngày 05/11/2026 dự án chưa có nhãn gold do người gán: 0/88 cặp tuyên bố–bằng chứng trong `data/gold/sessions/` và 0/79 câu của lô T1 thứ nhất (`docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2, lỗi F7; kiểm lại ngày 04/11 trong `docs/10-chung-ket-2026-11/doc-tai-lieu/R6_do_luong_du_lieu_van_hanh.md`, mục 3.1). Vì vậy mọi số trong luận văn thuộc một trong ba loại, và mỗi bảng ở Chương 5 ghi rõ loại của nó.

| Loại | Đáp án đến từ đâu | Dùng để trả lời |
|---|---|---|
| **Ca dựng** | Người dựng ca và đặt đáp án từ định nghĩa (GHG Protocol, bất biến kiểm chứng), không từ luật của GreenScan | Hệ có mắc các lỗi đã biết trước không |
| **Ca sinh có kiểm soát** (GS-Bench B-b) | Một số liệu thật trong báo cáo được dựng thành tuyên bố đúng, rồi nhiễu có kiểm soát đổi giá trị, đơn vị, kỳ, phạm vi…; đáp án theo họ nhiễu | Hệ phản ứng thế nào với từng kiểu sai |
| **Nhãn Claude đã được tác giả đọc lại** (T1, GS-Eval v2) | Claude gán theo hướng dẫn viết sẵn, hai lượt mù và phân xử; tác giả đọc lại | Hệ hành xử thế nào trên câu thật của doanh nghiệp, so với một chuẩn thống nhất |

Hệ quả cho cách viết: số trên ca dựng và ca sinh được gọi là "trên ca dựng" hoặc "trên GS-Bench"; số trên nhãn Claude được gọi là "so với nhãn Claude đã được tác giả đọc lại". Không số nào được gọi là độ chính xác trên nhãn người (quy ước 2 và 3 của `00_DAN_Y_VA_QUY_UOC.md`).

**Mô tả một lần về nhãn do Claude gán.** Nhãn của luận văn (T1 và GS-Eval v2) do các phiên bản Claude gán theo một hướng dẫn bằng văn bản (`training/` cho T1; `benchmark/gs_eval_v2/LABELING_GUIDE.md`, phiên bản `gs-eval-v2.0`, cho GS-Eval v2). Quy trình chung gồm năm bước: (1) viết hướng dẫn và bất biến trước khi gán; (2) với bộ cần độ tin cậy cao, hai lượt gán mù độc lập, người gán không được mở đầu ra của hệ thống hay mã nguồn; (3) phân xử các chỗ lệch bằng một lượt riêng; (4) kiểm định mẫu: một lượt đối nghịch đọc lại một phần nhãn với giả định nhãn có thể sai; (5) kiểm tất định bằng chương trình (mục 4.5.5) và tác giả đọc lại, trong đó mọi dòng ghi `review_status` để theo dõi việc đọc lại. Từ mục 4.2 trở đi, các nhãn này được dùng như dữ liệu thông thường của luận văn; những giới hạn của nó (cùng một họ mô hình gán nhãn, kiểm định mẫu nhỏ) được nêu ở mục 4.8 và Chương 6, không lặp lại trong từng câu kết quả.

## 4.2 Kho văn bản VN30

Kho văn bản thu thập từ các doanh nghiệp VN30, kèm các văn bản pháp lý. Đếm trực tiếp trên bảng hợp đồng dữ liệu `data/crawl/vn30/contract/raw.jsonl` (05/11/2026): **1.061 tài liệu của 21 mã**, gồm 506 báo cáo tài chính, 310 tài liệu đại hội cổ đông, 75 báo cáo thường niên, 45 báo cáo bền vững, 37 báo cáo quản trị, 1 báo cáo tích hợp, 2 hồ sơ cơ quan quản lý và 85 loại khác; năm báo cáo từ 2021 đến 2025 (257 tài liệu không ghi năm). Cùng kho đã được mô tả ở mốc 09/08/2026 là 670 tài liệu Việt Nam và 297 văn bản pháp lý, 15.658 đoạn, 7.960 tuyên bố ứng viên (`docs/10-chung-ket-2026-11/doc-tai-lieu/R6_do_luong_du_lieu_van_hanh.md`, mục 3.3, từ `DATASET_AUDIT_V2`); hai con số tài liệu khác nhau vì khác thời điểm đếm. Từ kho này, bộ cắt câu của chính sản phẩm tạo ra 66.539 câu ứng viên (`claim_sentences.jsonl`; `docs/07-presentation/paper/GREENSCAN_PAPER_2026-10-15.md`, mục 5.1). Chỉ 45 trong 1.061 tài liệu là báo cáo bền vững, nên phần lớn câu ứng viên không phải tuyên bố môi trường; đó cũng là lý do bộ trích tuyên bố được đánh giá riêng (mục 5.3.2).

Hai giới hạn của kho ảnh hưởng tới cách đọc kết quả. Thứ nhất, kho nghiêng về VN30 chứ không đại diện cho các ngành phát thải cao (thép, xi măng, điện); mã `tra` chiếm 29,8 % số tuyên bố ứng viên tại mốc 09/08 (R6, mục 3.3). Thứ hai, toàn bộ bằng chứng truy xuất được trong các lượt chạy là tài liệu của chính doanh nghiệp: trên lượt Hòa Phát ngày 22/10, 780/780 đoạn bằng chứng là nguồn nội bộ (`KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 2, lỗi F6). Nguồn độc lập (Climate TRACE, Global Energy Monitor, danh mục theo Quyết định 13/2024) mới ở mức danh sách thu thập, chưa tích hợp. Phép chia dữ liệu luôn theo doanh nghiệp: tập huấn luyện và tập thử không chung công ty, và khoảng tin cậy dùng bootstrap theo công ty (mục 4.6).

## 4.3 Nhãn T1

T1 là bài toán phân loại câu thành bốn lớp: `QUANTIFIED_CLAIM`, `QUALITATIVE_CLAIM`, `VAGUE`, `NOT_CLAIM` (bản gán nhãn đầu có năm nhãn). Bộ nhãn do Claude gán theo sổ tay mã hoá (codebook) và quy trình `QUY_TRINH_GAN_NHAN_T1`:

- Lượt 1 gồm 579 câu (500 câu huấn luyện và 79 câu so sánh), hai lượt mù A và B đồng ý ở 554/579 câu; κ giữa A và B bằng 0,92 trên năm nhãn và 0,98 trên nhãn nhị phân "có phải tuyên bố". Trọng tài đọc lại 170 câu, 21 câu đổi nhãn; trong 42 câu hai lượt đồng ý được chọn ngẫu nhiên để kiểm, 0 câu phải sửa (R6, mục 3.1).
- Tại ngày đếm 04/11 tệp `training/data/t1/train_claude.jsonl` có 2.055 dòng (1.521 câu hai lượt đồng ý, 534 câu đã phân xử; 17 công ty; 1.416 câu tiếng Việt, 639 câu tiếng Anh). Bản huấn luyện v3 được báo cáo ở Chương 5 chỉ dùng 1.217 câu của 15 công ty tại thời điểm 13/10 (`training/runs/kaggle_t1_v3/results.json`), nên hai con số cỡ mẫu không mâu thuẫn mà thuộc hai thời điểm.
- Tập `dev` (`audit`) gồm 160 câu đã cân bằng theo nhãn, 12 công ty, 79 tiếng Việt và 81 tiếng Anh, để người đọc lại mà không thấy nhãn của Claude; tập `test` (`hpg`) gồm 594 câu của báo cáo Hòa Phát 2025, cắt bằng chính bộ cắt câu của sản phẩm (151 câu luật giữ, 348 câu có thuật ngữ môi trường mà luật bỏ, 95 câu ngẫu nhiên). Cả hai tập chưa có nhãn người (paper, mục 5.2).

κ cao giữa hai lượt chỉ cho biết người gán nhất quán, không cho biết đúng; hai lượt của cùng một họ mô hình có thể sai tương quan. Vì thế mọi số T1 được viết là "đồng thuận với nhãn Claude".

## 4.4 GS-Bench v1.x: ca có đáp án theo cấu trúc

GS-Bench (`benchmark/gs_bench_v1/`) là thước đo tạm khi chưa có gold người, thiết kế trong `KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 4. Mỗi ca là một tuyên bố cộng một bằng chứng, kèm đáp án S (SUPPORTED), C (CONTRADICTED) hoặc N (không đủ bằng chứng / không so được) và, với tầng B-b, kèm biểu diễn trung gian (IR) vàng của bằng chứng: chỉ số, giá trị, bội số, đơn vị, kỳ, năm gốc, phạm vi, loại giá trị (tuyệt đối, cường độ, số đếm, tỷ lệ).

- **B-a (51 ca dựng)** là "size ladder" ngày 10/10: 32 ca sạch thuộc 13 nhóm lỗi (làm tròn, lệch một con số, khác Scope, khác kỳ, mục tiêu so với thực hiện, khác ranh giới, đơn vị, cộng bảng, phủ định…) và 19 ca dùng nguyên văn ba trang thật của Hòa Phát. Nhãn suy từ GHG Protocol, không từ luật của GreenScan.
- **B-b (ca sinh)**: lấy một số liệu thật trong báo cáo, dựng tuyên bố đúng (họ S), rồi áp **nhiễu có kiểm soát**, mỗi họ đổi đúng một yếu tố: giá trị, đơn vị, kỳ, Scope, công ty mẹ so với tập đoàn, mục tiêu so với thành tích, cường độ so với tuyệt đối, bội số. Đáp án là hệ quả của họ nhiễu. IR bằng chứng do Claude đọc một lượt (về sau thêm Qwen3-32B đọc lần hai) và bộ kiểm tất định `irlib` soát; `irlib` tự tính lại đúng nhãn của họ nhiễu ở 142/142 ca của v1.

| Phiên bản | Ngày | Nội dung | Nguồn |
|---|---|---|---|
| v1 | 31/10 | 193 ca = 51 B-a + 142 B-b từ 26 số liệu thật của 5 doanh nghiệp | `KE_HOACH…`, mục 10 |
| v1.1 | 31/10 | 453 ca = 51 B-a + 402 B-b (S 95, C 123, N 184), 7 doanh nghiệp; giữ 77/203 số liệu đọc được | `KE_HOACH…`; `R2_he_thong_va_thuc_nghiem.md`, mục 3.3 |
| Ngoài mẫu v1.2 | 31/10 | 162 ca, 9 doanh nghiệp (S 38, C 55, N 69) | `configs/measurement_decisions.yaml`, khối `agentic_v1_2` |
| Sạch v1.3 | 01/11 | hiệu chỉnh 448 ca (B-b 397); ngoài mẫu 87 ca (S 19, C 28, N 40) | `experiments/AG-1/README.md`, mục 01/11 17:00; `benchmark/gs_bench_v1/errata_v13.txt` |

Tập đã được sửa theo từng phát hiện lỗi nhãn của chính nó. Với v1.1, 16/455 ca (3,5 %) có nhãn lỗi: 2 ca nhiễu C2 nhân bội số lên giá trị 0 (giá trị không đổi) và 14 ca PV Power có câu không nêu phạm vi phát thải, nên hai câu khác nhau mang cùng văn bản (`errata_v1_1.txt`). Với v1.2, hậu kiểm cho thấy 75/162 ca hỏng (60 ca `other_env` là số liệu không thuộc môi trường, 6 ca tên chỉ số chứa chữ số, 4 ca đơn vị giả, 5 ca năm lấy từ tiêu đề trang), loại theo quy tắc tất định mà không gán lại nhãn nào (`clean_v13.py`). Tập sạch v1.3 chỉ còn 87 ca ngoài mẫu, nên số ca "dám kết luận" mỗi hệ chỉ từ 1 đến 22; Chương 5 luôn kèm số này.

Giả thuyết "B-b đại diện cho tuyên bố thật" được ghi là giả thuyết trong kế hoạch. Chính GS-Eval v2 (mục 4.5) là phép thử đầu tiên của giả thuyết đó trên câu thật, và kết quả không ủng hộ nó (mục 5.3.3).

## 4.5 GS-Eval v2

GS-Eval v2 (`benchmark/gs_eval_v2/`) trả lời câu hỏi mà GS-Bench không trả lời được: mã hiện tại của GreenScan hành xử thế nào trên **câu thật** của doanh nghiệp, ở năm mục tiêu của sản phẩm (giải thích kết luận, gợi ý sửa, chấm rủi ro, quy tắc nội bộ, độ dễ dùng). Toàn bộ hệ thống được đánh giá ở chế độ `offline`, không mô hình ngôn ngữ, không gọi mạng. Nguồn mô tả: `benchmark/gs_eval_v2/LABELING_GUIDE.md`, docstring của `build_inputs.py`, `validate.py`, `evaluate.py`, và `docs/10-chung-ket-2026-11/DANH_GIA_HE_THONG_2026-11-05.md`.

### 4.5.1 Năm bộ dữ liệu

| Bộ | Mục đích | Cỡ | Nhãn |
|---|---|---|---|
| D-EXPLAIN | Kết luận và lời giải thích của hệ có đúng, trung thực không | 200 mẫu (146 có đầu ra của mã hiện tại) | Một lượt, kiểm định đối nghịch 20 mẫu |
| D-EDIT | Gợi ý sửa của Studio có đúng loại, có thêm số không | 200 mẫu (100 từ lượt chạy, 100 từ kho VN30 theo nhãn T1) | Một lượt, kiểm định 20 mẫu |
| D-SCORE | Điểm rủi ro 9 thành phần có khớp phán đoán chuyên môn không | 200 mẫu, mỗi mẫu hai lượt mù | Hai lượt mù và phân xử 122 mẫu có chỗ lệch |
| D-RULES | Quy tắc nội bộ (org pack) có chạy đúng và an toàn không | 14 pack (12 tổ chức giả lập và 2 bản nháp), 76 quy tắc, 237 ca | Ba agent soạn ca, mỗi agent 4–5 tổ chức |
| D-UX | Người dùng có hiểu và dùng được không | 16 nhiệm vụ theo persona, SUS tiếng Việt, 18 heuristic, 15 kiểm lint | Bộ công cụ; chưa có người thử |

(Nguồn: `DANH_GIA_HE_THONG_2026-11-05.md`, mục 1; số nhiệm vụ UX theo `usability/PROTOCOL.md` và `usability/tasks.yaml`.)

### 4.5.2 Nguồn mẫu và việc chạy lại mã hiện tại trên tài liệu cũ

Mẫu ban đầu được rút từ mọi lượt chạy trong `.quantum/runs` (nhóm A), gồm 1.589 tuyên bố khác nhau, và từ các câu của kho VN30 có nhãn T1 (nhóm B, 721 câu) (`inputs/stats.json`). Nhóm A có cả lượt tháng 7–9 do mã cũ tạo, nên đầu ra "của hệ thống" trong các lượt đó không phải của mã hiện tại. Hai bước sửa:

1. `run_refresh.py` chạy lại **mã hiện tại**, chế độ `offline`, trên đúng các tài liệu đứng sau các lượt cũ (báo cáo bền vững và thường niên Hòa Phát, hồ sơ KLM, bộ ca thật), tạo ra 15 lượt từ 22/10 tới 05/11 (`inputs/refresh_stats.json`).
2. `refresh_system_outputs.py` **ghép đầu ra theo nội dung câu**: chuẩn hoá văn bản (gấp khoảng trắng, không phân biệt hoa thường), ghép khớp nguyên văn trước, rồi ghép theo bao hàm với tỷ lệ độ dài ≥ 0,8. Mã mẫu và nhãn không đổi; mẫu nào bộ trích hiện tại không còn trích thì ghi `not_extracted` và không đưa vào số đo của hệ.

Kết quả ghép trên 394 mẫu nhóm A: 320 khớp nguyên văn, 8 khớp bao hàm, 66 không còn được trích (`refresh_stats.json`). Trong 66 mẫu đó, nhãn của 23 mẫu D-EXPLAIN là NOT_A_CLAIM: bộ trích hiện tại đã bỏ phần lớn dòng bảng mà bản tháng 8 từng trích. Kho kết luận hiện tại gồm 1.138 tuyên bố khác nhau: PARTIALLY_SUPPORTED 1.006, INSUFFICIENT_EVIDENCE 72, CONTRADICTED 52, SUPPORTED 8. Mọi số hệ thống ở Chương 5 là của mã hiện tại.

### 4.5.3 Lấy mẫu phân tầng "lệch nhẹ nhưng cân bằng"

Nếu rút ngẫu nhiên từ kho, 88 % tuyên bố là PARTIALLY_SUPPORTED (1.006/1.138), và các lớp S và C, vốn là nơi rủi ro tập trung, gần như vắng mẫu. Nếu cân bằng tuyệt đối thì mẫu không còn phản ánh kho. GS-Eval v2 chọn một điểm giữa, gọi là "lệch nhẹ nhưng cân bằng": tầng theo kết luận của lượt nguồn, mỗi tầng được bù đủ để có số mẫu đọc được, nhưng tầng đông nhất vẫn nhiều nhất và có trần theo công ty.

- **D-EXPLAIN và D-SCORE:** S 45, C 50, I (INSUFFICIENT_EVIDENCE) 50, P (PARTIALLY_SUPPORTED) 55, tổng 200. Tầng P chọn rời nhau, Hòa Phát xếp cuối và bị chặn tối đa 12 % tầng; các tầng còn lại chặn 40 % mỗi công ty (`build_inputs.py`, hàm `capped_round_robin`, `split_stratified`). Hạt giống ngẫu nhiên 20261104. Hai bộ giao nhau ở 106 mẫu (`stats.json`).
- **D-EDIT:** 100 câu từ lượt chạy, chia theo đặc điểm câu (có số 34, định tính 33, mơ hồ 33), và 100 câu của kho VN30 theo nhãn T1 (33 / 34 / 33); 14 công ty, không công ty nào chiếm quá 13 %.
- **D-RULES:** các ca soạn theo loại: 60 COMPLIANT, 72 VIOLATION, 57 NEEDS_REVIEW, 48 NOT_APPLICABLE; đủ tám loại ca (bình thường 140, biên 39, tiêm lệnh 11, vượt quyền 11, quy tắc nháp 11, hết hiệu lực 6, trái luật 6, khác ngành 13).

Vì mẫu được rút theo kết luận của lượt nguồn nhưng đánh giá theo kết luận của mã hiện tại, tầng SUPPORTED hiện tại chỉ còn 5 mẫu trong D-EXPLAIN. Ước lượng cho toàn kho vì vậy phải **tái trọng số theo tầng** (mục 4.6) và chỉ là xấp xỉ.

### 4.5.4 Hướng dẫn gán nhãn

`LABELING_GUIDE.md` đặt bảy nguyên tắc chung và nhúng các bất biến kiểm chứng của sản phẩm để nhãn không dạy hệ điều sai:

1. Không bịa số: mọi số trong nhãn phải có trong câu hoặc đoạn bằng chứng của chính mẫu; thiếu thì viết chỗ trống `[bổ sung: …]`.
2. Chỉ dùng tối đa ba đoạn bằng chứng đã cho (mỗi đoạn tối đa 900 ký tự); kiến thức nền chỉ để diễn giải, không thay bằng chứng.
3. Trích nguyên văn, tối đa 25 từ.
4. Không xem đầu ra của hệ thống khi gán nhãn.
5. Thận trọng hơn là đoán: không chắc thì hạ `confidence` và chọn kết luận thận trọng hơn.
6. Lệch một chiều (cường độ so với tuyệt đối; công ty mẹ so với hợp nhất; năm khác, Scope khác, đơn vị không quy đổi được) là không so được, không bao giờ là mâu thuẫn.
7. Mục tiêu không chứng minh thành tích; không tìm thấy không có nghĩa là sai (bằng chứng im lặng là INSUFFICIENT_EVIDENCE); dung sai số học bằng nửa chữ số cuối đã công bố.

Sáu nhãn kết luận được định nghĩa: SUPPORTED (có đoạn nói cùng chỉ số, kỳ, phạm vi, giá trị khớp trong dung sai; câu nhắc lại chính tuyên bố không tính), PARTIALLY_SUPPORTED, CONTRADICTED (trái ngược trên cùng chỉ số, kỳ, phạm vi, so sánh được), UNSUPPORTED (hiếm), INSUFFICIENT_EVIDENCE và NOT_A_CLAIM (tiêu đề, mục lục, dòng bảng cụt, định nghĩa). Mỗi bộ có lược đồ riêng:

- **explain:** nhãn tham chiếu, thuộc tính tuyên bố, thuộc tính còn thiếu (trong tám loại), các đoạn bằng chứng đã dùng kèm trích dẫn, các cặp số đã kiểm, lời giải thích cho người không chuyên và cho chuyên gia, và hai danh mục kiểm để chấm lời giải thích của hệ một cách khách quan: `must_mention` (2–5 ý mà mọi lời giải thích tốt phải có) và `must_not_say` (1–3 khẳng định không được nói).
- **edit:** bốn loại sửa được phép, đúng bằng rào chắn của GreenScan Studio (`add_scope`, `placeholder`, `evidence_ref`, `soften`), 15 mã vấn đề (như `MISSING_PERIOD`, `MISSING_BASELINE`, `ABSOLUTE_CLAIM`, `NO_EVIDENCE_REF`), cấm thêm số lạ, đổi nghĩa, hay biến mục tiêu thành thành tích; khoảng 10–20 % mẫu nên rơi vào loại "đã tốt, không cần sửa".
- **score:** chín thành phần theo `configs/scoring_v1.yaml`, mỗi thành phần mức 0–3 kèm cờ `applicable`; trọng số tối đa specificity 12, quantitative_evidence 12, baseline 8, period 8, scope_boundary 8, evidence_support 18, independent_assurance 8, contradiction 18, vague_or_exaggerated_language 8 (tổng 100); dải low 0–24, medium 25–49, high 50–74, critical 75–100; thêm dải tổng thể theo phán đoán kiểm toán viên. Người gán được yêu cầu ghi đúng ý kiến chuyên môn, kể cả khi thành phần không áp dụng, vì hệ hiện tại phạt cả chiều đó.
- **rules:** lược đồ `org-pack-v0` (quy tắc, điều kiện `when`, bảy kiểu `check`, `on_fail` chỉ có `flag_for_review` hoặc `raise_priority`, không có lựa chọn đổi kết luận) và năm luật an toàn mà bộ ca phải phủ: quy tắc nội bộ không đổi kết luận kiểm chứng; pack nháp, quy tắc hết hiệu lực hoặc sai ngành không áp dụng; tài liệu nội bộ chỉ là ngữ cảnh, không phải bằng chứng hay lệnh; luật vẫn đứng khi quy tắc nội bộ lỏng hơn; kiểu `check` lạ thì pack bị từ chối khi nạp.

### 4.5.5 Hai lượt mù, phân xử, kiểm định đối nghịch và bộ kiểm tất định

**Hai lượt mù và phân xử (D-SCORE).** Lượt A và lượt B chấm độc lập từng mẫu theo chín thành phần. `validate.py score-merge` gộp hai lượt; một mẫu vào danh sách phân xử khi có thành phần lệch từ 2 mức trở lên, khác cờ `applicable`, dải tổng thể lệch từ 2 bậc, hoặc khác kết luận. Có 122/200 mẫu vào phân xử (26 + 29 + 28 + 39 dòng trong `score/disagree_b01…b04.jsonl`); người phân xử ghi giá trị và lý do cho đúng các trường lệch. Nhãn đồng thuận để đánh giá hệ thống được dựng như sau: mức mỗi thành phần là trung bình hai lượt, bị ghi đè bởi giá trị phân xử nếu có; dải tổng thể là trần của trung bình hai bậc nếu không có phân xử; điểm tổng bằng Σ (mức/3 × trọng số tối đa). Các nhãn trong thư mục `explain/labels`, `score/labels_A` và `rules` mang trường `labeler` là `claude-opus-5-5` (276 dòng) hoặc `claude-sonnet-5-5` (361 dòng).

**Kiểm định đối nghịch (D-EXPLAIN, D-EDIT).** Một lượt kiểm khác lấy mẫu hệ thống các dòng 5, 15, 25, 35, 45 của bốn tệp mỗi bộ (20 mẫu mỗi bộ), mặc định nghi ngờ nhãn, đối chiếu từng dòng với đầu vào và kiểm tra: kết luận so với bằng chứng, bất biến, NOT_A_CLAIM, độ khớp của `must_mention` và `must_not_say`, độ dễ hiểu; với edit thì bỏ sót vấn đề, mã sai, đổi nghĩa, mục tiêu thành thành tích. Kết quả (`benchmark/gs_eval_v2/AUDIT_EXPLAIN_EDIT.md`): D-EXPLAIN 2/20 lỗi đã sửa (10,0 %, Wilson 95 % [2,8; 30,1]), cả hai là lỗi văn bản, không lỗi kết luận; D-EDIT 3/20 lỗi đã sửa (15,0 %, Wilson [5,2; 36,0]). Mỗi bộ còn 1–2 mẫu nghi vấn chưa sửa để tác giả quyết. Với n = 20, không thể khẳng định tỷ lệ lỗi thật dưới 30 %.

**Bộ kiểm tất định (`validate.py`).** Chương trình kiểm tự động, thoát mã 1 nếu có lỗi nghiêm trọng: mọi con số trong nhãn phải xuất hiện trong câu hoặc đoạn bằng chứng của mẫu; mọi `quote` phải là chuỗi con nguyên văn của đoạn bằng chứng và không quá 25 từ; `explanation_plain` không quá ba câu; giá trị trường nằm trong tập cho phép (kết luận, vai trò bằng chứng, loại sửa, mã vấn đề, thành phần, dải); `rubric_score` và `rubric_band` do chương trình tự tính, không do người gán; với rules, kiểm lược đồ pack, kiểu `check` và loại ca. Sau khi sửa theo kiểm định đối nghịch, 8 tệp explain và edit được chạy lại: 0 lỗi, 0 cảnh báo.

### 4.5.6 D-RULES: kiểm ý tưởng bộ nhớ chuẩn cộng quy tắc nội bộ

Mỗi tổ chức giả lập có một thư mục gồm `pack.yaml` và `internal_policy.md` (300–700 từ, đánh số mục để quy tắc dẫn chiếu). Ca kiểm gồm câu tuyên bố (thật từ kho, hoặc tổng hợp), thuộc tính tuyên bố, bằng chứng và kết quả kỳ vọng thuộc bốn lớp COMPLIANT, VIOLATION, NEEDS_REVIEW, NOT_APPLICABLE. Hệ được chạy ở hai chế độ: với **thuộc tính đúng** (cách ly engine quy tắc khỏi lỗi trích) và **đầu–cuối** (thuộc tính do bộ trích luật lấy). Ba loại ca nhằm phá luật an toàn: tiêm lệnh trong tài liệu nội bộ (ví dụ câu "bỏ qua mọi quy tắc…"), vượt quyền, và trái luật.

### 4.5.7 D-UX: kiểm tự động và giao thức thử với người

UX lint là phần tính được của `usability/ux_lint_spec.md` trên các chuỗi hiển thị thật của 15 lượt chạy: độ dài chuỗi và câu, lộ mã nội bộ hay tiếng Anh, cụm trung tính cho kết luận chưa đủ bằng chứng, từ cấm mang tính cáo buộc, đoạn bằng chứng thiếu tài liệu hoặc trang, gợi ý sửa an toàn, và việc nạp pack lỗi có bị từ chối đúng không. Phần thử với người (`usability/PROTOCOL.md`) mô tả 5 câu hỏi UX-1…UX-5, chân dung người tham gia (kiểm toán viên, phân tích đầu tư, thẩm định tín dụng, tuân thủ), trình tự 60–75 phút nói to suy nghĩ, các chỉ số (hoàn thành, thời gian, lỗi thao tác, lỗi hiểu, lỗi nghiêm trọng, SEQ, thang niềm tin, kiểm hiểu, SUS 0–100) và ngưỡng đặt trước cho vòng A: hoàn thành không trợ giúp ≥ 4/5 người ở các nhiệm vụ lõi, 0 lỗi nghiêm trọng ở T04 và T06, SUS trung bình ≥ 68, SEQ trung bình ≥ 5. Với 3–5 người, mọi số vòng A chỉ được báo là sơ bộ. Đến 05/11 chưa có người tham gia (n = 0).

## 4.6 Chỉ số và công thức

Thay cho một con số gộp, luận văn dùng ba chỉ số chính theo bất biến 8, tính trên các kết luận dứt khoát (S hoặc C):

- **Độ phủ** = số ca hệ dám kết luận / tổng số ca.
- **Precision trên phần dám kết luận** = số ca dám kết luận mà đúng nhãn / số ca dám kết luận. Với GS-Bench, "đúng" là trùng đáp án của họ nhiễu; với GS-Eval v2, trùng nhãn tham chiếu (nhãn NOT_A_CLAIM tính là không đúng với S và C).
- **Số kết luận sai nguy hiểm**: `false_C` là số CONTRADICTED mà đáp án không phải C (vu oan doanh nghiệp), `false_S` là số SUPPORTED mà đáp án không phải S (bỏ lọt). Hai số được báo riêng, không gộp.

Các chỉ số còn lại:

- **Precision, recall, F1** của một lớp: P = TP/(TP+FP), R = TP/(TP+FN), F1 = 2PR/(P+R); **macro-F1** là trung bình F1 các lớp có mặt.
- **κ Cohen** = (p_o − p_e)/(1 − p_e), với p_o là tỷ lệ trùng và p_e = Σ_k p_A(k)·p_B(k) (Cohen, 1960). Khi lớp lệch, κ thấp dù tỷ lệ trùng cao: Claude và gemma-4-31B trùng 89/100 câu T1 nhưng κ chỉ 0,63 (R6, mục 2). Để diễn giải mức κ, luận văn dùng thang Landis và Koch (1977) làm tham chiếu.
- **QWK** (quadratic weighted kappa) cho thang thứ bậc với k bậc: QWK = 1 − Σ w_ij·O_ij / Σ w_ij·E_ij, trọng số w_ij = (i − j)²/(k − 1)², O là ma trận quan sát, E là ma trận kỳ vọng từ hai phân bố biên. Mức thành phần 0–3 dùng k = 4; dải tổng thể cũng k = 4.
- **Hệ số hạng Spearman ρ** của điểm tổng giữa hệ thống và nhãn đồng thuận, tính bằng `scipy.stats.spearmanr`.
- **Khoảng Wilson 95 %** cho tỷ lệ k/n: tâm c = (p + z²/2n)/(1 + z²/n), nửa rộng h = z·√(p(1 − p)/n + z²/4n²)/(1 + z²/n), z = 1,96 (Wilson, 1927). Khi không có ca sai nào trong n ca, cận dưới là n/(n + z²); ví dụ 0 vu oan trên 87 ca cho tỷ lệ vu oan có thể tới khoảng 3,4 % (R6, mục 2.5).
- **Bootstrap theo công ty.** Đơn vị độc lập là công ty chứ không phải câu, vì các câu cùng một báo cáo tương quan. Mỗi lần lặp rút lại công ty có hoàn lại (số công ty bằng số công ty trong mẫu), giữ nguyên mọi câu của công ty được chọn, tính lại chỉ số; khoảng 95 % lấy từ phân vị 2,5 % và 97,5 % của 1.000 lần lặp trong `evaluate.py` (hạt giống 20261105) và 2.000 lần lặp trong chấm GS-Bench. Mẫu GS-Eval v2 chỉ có 8–12 cụm công ty, nên khoảng này vẫn rộng.
- **Tái trọng số theo tầng.** Với tầng s có N_s tuyên bố trong kho hiện tại (lấy từ `refresh_stats.json`) và tỷ lệ mẫu p̂_s, ước lượng toàn kho là p̂ = Σ_s N_s·p̂_s / Σ_s N_s. Vì tầng của mẫu là tầng của lượt nguồn chứ không phải của mã hiện tại, ước lượng này chỉ là xấp xỉ và luôn được báo cạnh số của mẫu thô.
- **Chỉ số của từng bộ.** Explain: tỷ lệ câu được trích không phải tuyên bố; ma trận hệ–nhãn; P, R, F1 của thuộc tính thiếu; độ phủ ý bắt buộc (một chỉ báo theo từ khoá); số `must_not_say` bị vi phạm; số chứa trong lời giải thích mà không có trong câu hay bằng chứng. Judge: một agent Sonnet chấm 146 lời giải thích theo `must_mention` và `must_not_say` của từng mẫu và ba tiêu chí (trung thực với bằng chứng, có chỉ ra việc cần làm, độ rõ 1–5) (`benchmark/gs_eval_v2/explain/judge/`). Edit: nhận ra câu cần sửa (P, R, F1), P, R, F1 theo loại sửa và theo mã vấn đề, số gợi ý thêm số mới (phải bằng 0). Rules: accuracy bốn lớp, Wilson, macro-F1, độ đúng theo loại ca, số ca an toàn lệch kỳ vọng.
- **So sánh hai hệ trên cùng ca**: kiểm McNemar chính xác trên các ca bất đồng (dùng cho size ladder).

Judge và người gán cùng thuộc họ Claude, nên điểm judge có thể thiên lệch khi chấm đầu ra có văn phong khác (Zheng và cs., 2023; Wang và cs., 2024); đây là một giới hạn được ghi ở mục 4.8.

## 4.7 Đăng ký trước

Với các thí nghiệm agentic AG-0 đến AG-3, giả thuyết, cổng quyết định và điều kiện bác bỏ được ghi vào `configs/measurement_decisions.yaml` trước khi mô hình nào đọc dữ liệu kiểm, theo các khối `agentic_v1`, `agentic_v1_1`, `agentic_v1_2`, `agentic_ag2_v1`, `agentic_ag2_product`, `agentic_ag3_v0` (khối đầu đăng ký ngày 31/10, khối cuối ngày 01/11). Mỗi khối có:

- **thời điểm đăng ký** và những gì đã biết trước đó (`known_before`; ví dụ luật và oracle IR vàng đã biết khi đăng ký `agentic_v1`);
- **dự đoán** định lượng (ví dụ 4B: độ phủ B-b ≥ 0,35 với precision ≥ 0,90 và `false_C` ≤ 2);
- **điều kiện bác bỏ** (`falsified_if`) và **cổng** (ví dụ `ag1_ir_path_usable`: precision ≥ 0,90, cận dưới CI ≥ 0,80, `false_C` không quá của luật cộng 1; `ag2_dual_path_to_product`: không vượt luật về `false_C` và `false_S`, cận dưới phần tăng độ phủ > 0, 17/17 bẫy xanh, mọi test bất biến, thời gian chạy Hòa Phát ≤ 2 lần).

Ba quy ước giữ cho đăng ký có nghĩa. Một: số **trong mẫu** (dữ liệu đã dùng để rút ra cách sửa) được gọi đúng tên và không dùng làm bằng chứng; chỉ số ngoài mẫu mới tính. Hai: khi dữ liệu kiểm bị lộ hay hỏng, sửa đổi được ghi thành `amendment` có giờ, trước khi mô hình đọc tập mới, và tập cũ chuyển thành trong mẫu cho thay đổi đó (như lượt D của v1.2). Ba: dự đoán sai được công bố cùng dự đoán đúng; R2 (mục 3.9) đếm 21 dự đoán đăng ký trong khoảng 31/10–01/11, 13 đúng, 8 sai.

GS-Eval v2 khác về tính chất: đây là một phép **đo mô tả** mã hiện tại trên mẫu đã chốt hạt giống, không phải kiểm một dự đoán đã đăng ký; trong các tài liệu đã đọc không có khối đăng ký dự đoán riêng cho nó. Điều đã đăng ký trước cho GS-Eval v2 là phương pháp (hướng dẫn gán nhãn, lược đồ, luật tính điểm, chỉ số) và quy tắc sau đó: mọi sửa đổi làm đổi kết luận phải đăng ký trước trong `measurement_decisions.yaml`, chạy lại GS-Bench (không được tăng kết luận sai) và GS-Eval v2 rồi mới bỏ cờ (`DANH_GIA_HE_THONG_2026-11-05.md`, mục 4). Với D-UX, các ngưỡng vòng A được đặt trước buổi thử trong `PROTOCOL.md` mục 7.

## 4.8 Các đe doạ tính hợp lệ

Phần này liệt kê ngắn các đe doạ ảnh hưởng trực tiếp tới cách đọc Chương 5; bàn luận đầy đủ ở Chương 6.

- **Cùng một họ mô hình gán nhãn.** Hai lượt D-SCORE cùng họ Claude nên có thể sai tương quan; κ và QWK giữa hai lượt đo độ ổn định, không đo độ đúng. Tác giả chưa đọc hết nhãn (`review_status` còn `pending_human_review`). Độ đồng thuận giữa hai lượt (mục 5.3.5) được dùng như **trần thực tế** của một hệ chấm tự động, không như chuẩn tuyệt đối.
- **Kiểm định mẫu nhỏ.** 20 mẫu mỗi bộ cho tỷ lệ lỗi explain khoảng 10 % (Wilson [3 %; 30 %]) và edit 15 % (Wilson [5 %; 36 %]).
- **Mẫu.** Rút theo tầng của lượt nguồn, đánh giá theo tầng của mã hiện tại; tầng SUPPORTED chỉ còn 5 mẫu; ước lượng toàn kho là xấp xỉ; bootstrap theo công ty chỉ có 8–12 cụm.
- **Bằng chứng người gán thấy bị cắt** tối đa ba đoạn, mỗi đoạn 900 ký tự, trong khi hệ có thể dùng phần bị cắt. Với 5 ca CONTRADICTED được kiểm, người gán vẫn thấy đủ cặp số bị so.
- **Phiên bản mã.** Số của GS-Eval v2 chỉ đúng với mã tại ngày 05/11; việc sửa mã sau đó làm số cũ hết hiệu lực. Với mẫu cũ, 66/394 câu không còn được trích, nên không thể so từng câu với bản tháng 8.
- **Đơn vị phân tích.** Câu và công ty chưa độc lập; kho thiên về VN30, nhiều nhất là Hòa Phát ở nhóm A.
- **Tập B-b không thay cho câu thật.** Kết quả GS-Bench nói về khả năng chống các họ nhiễu đã biết, không nói về tỷ lệ vu oan trên kho thật.
- **Judge cùng họ mô hình** (xem trên) và **D-UX chưa có người.**

## 4.9 Tóm tắt chương

1. Chưa có nhãn gold của người; mọi số được phân loại thành ca dựng, ca sinh có kiểm soát, hoặc so với nhãn Claude đã được tác giả đọc lại, và được gọi đúng tên như vậy.
2. Kho gồm 1.061 tài liệu của 21 mã VN30, trong đó 45 báo cáo bền vững cùng 66.539 câu ứng viên; T1 có nhãn hai lượt mù (κ 0,92 trên 579 câu); GS-Bench v1.x có 51 ca dựng cộng 402 ca sinh, được sửa theo từng lỗi nhãn tìm ra, còn 87 ca ngoài mẫu sạch.
3. GS-Eval v2 gồm năm bộ (explain 200, edit 200, score 200 hai lượt mù và 122 mẫu phân xử, rules 237 ca, UX), lấy mẫu phân tầng "lệch nhẹ nhưng cân bằng", chạy lại mã hiện tại trên tài liệu cũ rồi ghép đầu ra theo nội dung câu; nhãn qua hướng dẫn, hai lượt mù, kiểm định đối nghịch và kiểm tất định.
4. Chỉ số chính: precision trên phần dám kết luận, độ phủ, `false_C` và `false_S` báo riêng; kèm κ, QWK, Spearman, khoảng Wilson, bootstrap theo công ty và tái trọng số theo tầng.
5. Thí nghiệm agentic được đăng ký trước (21 dự đoán, công bố cả đúng lẫn sai); GS-Eval v2 là phép đo mô tả với các giới hạn đã nêu.

## Tài liệu tham khảo của chương

- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46.
- Landis, J. R. và Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174. (Thang diễn giải κ, theo ghi chú `docs/10-chung-ket-2026-11/doc-tai-lieu/R6_do_luong_du_lieu_van_hanh.md`, mục 2, và `R8_web_paper_ai_dataset.md`.)
- Wang, P. và cs. (2024). Large Language Models are not Fair Evaluators. *ACL 2024*. (Theo `docs/07-presentation/paper/GREENSCAN_PAPER_2026-10-15.md`, mục Tài liệu tham khảo.)
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
- Zheng, L. và cs. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*. (Theo paper 15/10, mục Tài liệu tham khảo.)
