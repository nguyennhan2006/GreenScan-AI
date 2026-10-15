# Quy trình gán nhãn T1 và khung dữ liệu huấn luyện

**Ngày:** 11/10/2026 · **Người đọc:** nhóm gán nhãn (Quỳnh, Thảo, Nhân); mục 8–9 dùng làm phụ lục phương pháp cho BGK.
**Công cụ:** [`training/gold_t1_pack.py`](../../training/gold_t1_pack.py) (gán, họp, gold, báo cáo) · [`training/t1_data.py`](../../training/t1_data.py) (khung dữ liệu, kiểm tra, gộp) · [`schemas/training/t1_example.schema.json`](../../schemas/training/t1_example.schema.json).

---

## 1. Vì sao đổi cách gán

Bản soát 22 mục hàng đợi HPG (Có/Không) cho biết hàng đợi đúng bao nhiêu, nhưng **không dùng được để huấn luyện hay đo T1**:

- T1 dự đoán 4 lớp, còn bản soát chỉ có hai đáp án.
- Bản soát chỉ có 14 câu, đều do hàng đợi chọn sẵn, nên không có câu nào luật đã bỏ sót. Vì vậy không đo được recall.
- Một số câu phải xem bảng hoặc câu trước mới gán được.
- Chỉ có một người gán, không tính được κ.
- Có ô dán nguyên câu trả lời của chatbot.

Quy trình mới tạo ra nhãn **có thể đo, có thể kiểm, có thể báo cáo**. Mỗi câu được nhiều người gán độc lập. Câu nào có bất đồng thì đem ra họp, và kết luận của buổi họp mới là gold.

## 2. Ba tập dữ liệu

| Tập | Nguồn | Cỡ | Ai gán | Dùng để |
|---|---|---|---|---|
| **train** | Câu của các công ty trong kho crawl (`claim_sentences.jsonl`, 66.539 câu) | ≈ 4.000 câu | Thầy `gemma-4-31B-it`, ≥ 3 lần, lấy đa số, chỉ giữ câu có đồng thuận ≥ 0,67 | Huấn luyện học trò |
| **dev** (bộ `audit`) | 160 câu thầy đã gán, chia đều theo nhãn thầy (người gán **không** thấy nhãn thầy); 12 công ty; 79 câu tiếng Việt, 81 câu tiếng Anh; 4 lô × 40 | 160 | Quỳnh, Thảo, Nhân, rồi họp | Đo chất lượng nhãn thầy; chọn mô hình và ngưỡng |
| **test** (bộ `hpg`) | HPG BCPTBV 2025, cắt câu bằng chính parser PDF của sản phẩm. Gồm 151 câu luật giữ, 348 câu có thuật ngữ môi trường mà luật bỏ, 95 câu ngẫu nhiên. 12 lô (lô 1 có 39 câu, các lô sau 50–51 câu) | 594 | Như trên | Đo cuối cùng, **một lần**. Kho huấn luyện không có câu nào của HPG |

Lý do chia như vậy:
- **dev** cùng công ty với train nhưng khác câu, nên đo được mô hình làm tốt đến đâu *trong miền*.
- **test** là công ty mô hình chưa từng thấy, chữ lại lấy từ PDF thay vì kho crawl, nên đo được mô hình *tổng quát hóa sang doanh nghiệp mới*. Đây chính là điều sản phẩm phải làm.
- `exclude_from_training.txt` chứa 754 id của dev và test. Lệnh `t1_data.py from-teacher` và `train_classifier.py --exclude` đều loại các id này khỏi train.

Mỗi lô là một mẫu ngẫu nhiên có phân tầng. Nếu không kịp làm hết, các lô đã xong vẫn là một mẫu đại diện: gold chỉ nhỏ đi, không bị lệch.

## 3. Quy trình thống nhất

```
lô 1 (hiệu chỉnh) ── mọi người gán ĐỘC LẬP ──► import ──► consensus ──► HỌP 1 ──► import-consensus
                                                              │                     │
                                                              ▼                     ▼
                                                      file họp: chỉ các câu   sổ quy ước v1.x
                                                      có bất đồng             (tự vào các gói sau)
lô 2…n ── export (mang quy ước mới) ── gán độc lập ── import ── consensus ── HỌP 2, 3 ── merge ── report
```

| Bước | Lệnh | Ai |
|---|---|---|
| Gửi gói | `python training/gold_t1_pack.py export-xlsx --labelers quynh thao nhan [--lots 2]` → mỗi người một file `packs/T1_<tên>_lo1.xlsx` gồm cả hai bộ: chọn từ danh sách, ô vàng là ô còn thiếu, ô đỏ là chọn nhầm loại. Mỗi dòng có cột `xem` (ảnh trang gốc, câu được tô vàng; câu của kho crawl được tìm trang trong PDF đã tải), cột `link_goc` (báo cáo trên web) và sheet "Tài liệu". **Gửi file `T1_<tên>_lo1.zip`** (Excel + thư mục ảnh `trang_lo1/`, khoảng 23 MB). Mẫu cũ tách theo bộ (`export --set …`) vẫn nhập được | Nhân |
| Hoặc: CSV gõ mã ngắn | `python training/gold_t1_pack.py export-csv --labeler <tên> [--lots 2]` → `packs/T1_<tên>_lo1.csv` + bảng mã `packs/T1_cach_dien.md`. Mỗi dòng điền 4 ô đầu: `nhan` (1/2/3/0/?), `chi_tiet` (pt, tk… hoặc kt, tck…), `chac` (3/2/1), `ngu_canh` (x) | Nhân |
| Nhận về | `python training/gold_t1_pack.py import <file.xlsx hoặc file.csv> …`. Từ chối file thiếu hoặc sai, chỉ rõ từng dòng. Với CSV, lô nào gán đủ thì nhập lô đó, lô làm dở được giữ lại | Nhân |
| Tạo file họp | `python training/gold_t1_pack.py consensus --set hpg` | Nhân |
| Họp | Điền "Nhãn thống nhất" và "Vì sao"; viết quy ước mới vào "Sổ quy ước" | Cả nhóm |
| Ghi kết quả họp | `python training/gold_t1_pack.py import-consensus <file họp>` | Nhân |
| Gold | `python training/gold_t1_pack.py merge --set hpg` | Nhân |
| Số liệu | `python training/gold_t1_pack.py report --set hpg` → `benchmark/gold_t1/hpg_report.md` | Nhân |

**Câu nào phải đem ra họp:**
- người này nói là tuyên bố, người kia nói không;
- khác loại tuyên bố;
- khác chủ đề;
- khác lý do NOT_CLAIM;
- có người chọn UNSURE;
- có người chọn độ chắc 1;
- có người dùng AI.

Câu mọi người cùng nhãn thì vào gold luôn, không cần bàn.

**Nguyên tắc:**
1. Gán độc lập, không bàn với nhau trước khi nộp.
2. Không dùng chatbot để ra nhãn. Lỡ dùng thì đánh dấu, câu đó sẽ được đem ra họp.
3. Không biểu quyết khi chưa hiểu lý do của nhau.
4. Bất đồng sinh ra do quy ước chưa nói thì viết thành quy ước mới.
5. Không thống nhất được thì để UNSURE, câu đó ra khỏi gold.

## 4. Form gán nhãn (mỗi người, mỗi lô)

| Cột | Bắt buộc | Vì sao cần cho huấn luyện / báo cáo |
|---|---|---|
| Nhãn (4 lớp T1 + UNSURE) | luôn | Đích của mô hình; κ |
| Chủ đề (8 claim_type của sản phẩm) | khi là tuyên bố | Đo độ phủ miền; đo sản phẩm xếp loại đúng không |
| Nếu NOT_CLAIM: vì sao (6 lý do, theo thứ tự lý do gốc) | khi NOT_CLAIM | Phân tích lỗi của luật và mô hình |
| Độ chắc 1–3 | luôn | Chọn câu cần xem lại; có thể dùng làm trọng số |
| Phải đọc câu trước/sau? | không | Quyết định có huấn luyện dạng cặp câu không; đo riêng nhóm này |
| Dấu hiệu (OVERCLAIM / INCONSISTENCY / FUTURE) | không | Dữ liệu cho bước phát hiện tẩy xanh sau này |
| Ghi chú (≤ 300 ký tự) | khi UNSURE, lý do "other", có dấu hiệu, hoặc độ chắc 1 | Đầu vào cho buổi họp |
| AI hỗ trợ | không | Câu có AI chưa qua họp không được vào gold |
| Giờ bắt đầu / kết thúc | nên có | Số giây mỗi câu, để báo công sức |

Ô bắt buộc còn trống sẽ chuyển vàng. Người gán không thấy nhãn của luật hay của thầy.

## 5. Bộ quy tắc v1.0

Định nghĩa 4 lớp giống nguyên văn `CLAIM_PROMPT` trong `teacher_label.py`. Các quy ước đề xuất Q1–Q9 sẽ được chốt ở họp 1 (sheet "Hướng dẫn" trong mỗi gói):

| Mã | Quy ước |
|---|---|
| Q1 | Chủ thể là tổ chức khác (hiệp hội, Chính phủ, cả ngành, thế giới) → NOT_CLAIM / other_org |
| Q2 | Tác dụng chung của công nghệ → NOT_CLAIM / general_knowledge; tác dụng của biện pháp DN đang làm → tuyên bố |
| Q3 | Câu thiếu chủ ngữ: đọc câu trước rồi mới gán, và đánh dấu "Phải đọc câu trước/sau" |
| Q4 | Chữ rác đầu/cuối câu: bỏ qua nếu câu vẫn trọn nghĩa; mất nghĩa → broken |
| Q5 | Câu trùng nhau → cùng nhãn |
| Q6 | Mục tiêu chỉ có mốc năm (trung hòa carbon 2050) → QUALITATIVE; có lượng (30% năm 2030) → QUANTIFIED |
| Q7 | Năm, số hiệu tiêu chuẩn (ISO 14064), số văn bản không tính là số liệu |
| Q8 | Nhiều lý do NOT_CLAIM cùng đúng → chọn lý do đứng trước trong danh sách |
| Q9 | Câu tiếng Anh gán y như câu tiếng Việt |

**Quy ước đề xuất thêm (Q10–Q17).** Khi Claude gán 579 câu (mục 11), có 8 tình huống mà Q1–Q9 chưa đủ rõ nên các lượt gán làm không đều. Claude đã áp dụng cách dưới đây; nhóm chốt ở họp 1 (giữ, sửa hoặc bỏ). Không chốt thì cột Claude không so được với cột người ở các tình huống này.

| Mã | Tình huống | Đề xuất |
|---|---|---|
| Q10 (C1) | Số đếm ("26 nhà máy đạt ISO 14001", "5 dự án điện mặt trời", "100% trang trại đạt GlobalG.A.P") | Là số liệu (QUANTIFIED) khi nói quy mô một kết quả môi trường. **Không** tính khi chỉ nêu vị trí ("tại hai tòa nhà"), đếm người, giờ, bước, chỉ số, hoặc là thứ hạng (Top 10) |
| Q11 (C2) | Giải thưởng, xếp hạng bền vững của chính DN (Top 100 DN bền vững, VNSI, Brand Finance) | QUALITATIVE / generic_sustainability. Giải về kinh doanh, chất lượng, xã hội → NOT_CLAIM / non_env |
| Q12 (C3) | Câu nói về chính bản báo cáo | Kỳ, phạm vi, mục đích → NOT_CLAIM / other. Chuẩn GRI, kiểm toán/đảm bảo, quy trình xác định vấn đề trọng yếu, kiểm kê KNK → QUALITATIVE / esg_process_integration |
| Q13 (C4) | Dòng bảng, nhãn biểu đồ, chuỗi chữ infographic (kể cả có số của DN) | NOT_CLAIM / table_heading (số trong bảng do mô-đun figures xử lý). Chú thích là câu trọn nghĩa thì gán theo nghĩa |
| Q14 (C5) | "Phát triển bền vững" theo nghĩa kinh doanh trường tồn, không có yếu tố môi trường | NOT_CLAIM / non_env |
| Q15 (C6) | Đặc điểm xanh của dự án khách hàng mà DN chỉ là nhà thầu | NOT_CLAIM / other_org; việc DN tự làm trên công trường vẫn là tuyên bố |
| Q16 (C7) | Câu ghép lỗi mà phần còn lại vẫn hiểu được | Gán theo phần đó; `broken` chỉ khi mất nghĩa |
| Q17 (C8) | Mô tả hiện trạng môi trường của chính DN (nguồn nước, nhiên liệu đang dùng, nhu cầu năng lượng); khẳng định tuân thủ quy định môi trường | QUALITATIVE (kiểm chứng được); có số → QUANTIFIED |

**Đồng bộ với thầy:** sau họp 1, mọi quy ước đã chốt phải được đưa vào `CLAIM_PROMPT` (thành `teacher-claim-v2`) **trước** khi chạy thầy trên 4.000 câu. Nếu không, thầy và gold đang dùng hai định nghĩa khác nhau.

## 6. Khung thuộc tính của dữ liệu đầu vào huấn luyện (`t1-example-v1`)

Mọi dòng train, dev và test đều phải có cùng một khung. Khung được khai báo **một chỗ duy nhất** là `FIELDS` trong `training/t1_data.py`. Từ đó sinh ra JSON Schema, bảng dưới đây và bộ kiểm tra. Muốn đổi khung thì sửa ở `FIELDS`, không sửa trực tiếp file schema.

**1. Định danh**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `id` | string | luôn |  | Khóa câu (sha1 16 ký tự). Dùng để loại câu dev/test khỏi train và nối nhãn các nguồn. |
| `company_id` | string | luôn |  | Mã công ty. Chia tập theo công ty: công ty ở test không được có câu nào ở train. |
| `doc` | string | luôn |  | Tài liệu gốc (tên file PDF hoặc doc_id của kho). |
| `page` | integer / null | không |  | Trang trong tài liệu gốc, để mở lại và kiểm. |
| `reporting_year` | integer / null | không |  | Năm báo cáo. Dùng để phân tích lệch theo thời gian. |
| `source_kind` | string | luôn | crawl_clean, pdf_parser | Cách lấy chữ: kho crawl đã làm sạch, hay parser PDF của sản phẩm. Hai nguồn khác nhau là một phần của độ lệch miền. |

**2. Đầu vào mô hình**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `text` | string | luôn |  | Câu gốc, 25–500 ký tự, cắt đúng như bộ tách câu của sản phẩm. |
| `text_masked` | string | luôn |  | Câu mà mô hình đọc: số đã thay bằng <E1>…, năm giữ nguyên. Thầy cũng gán trên dạng này. |
| `mask_version` | string | luôn |  | Cách che số đã dùng. Train và test phải cùng một cách che. |
| `prev_text` | string | luôn |  | Câu liền trước (rỗng nếu không có). Dùng khi huấn luyện dạng cặp câu cho câu thiếu chủ ngữ. |
| `next_text` | string | luôn |  | Câu liền sau (rỗng nếu không có). |
| `lang` | string | luôn | vi, en | Ngôn ngữ câu. Báo cáo kết quả tách theo ngôn ngữ. |

**3. Đặc trưng phụ**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `rule_label` | integer | luôn | 0, 1 | 1 nếu bộ trích bằng luật giữ câu này. Là mốc so sánh (baseline), không phải nhãn. |
| `lexicon_hit` | integer | luôn | 0, 1 | 1 nếu câu có thuật ngữ môi trường trong taxonomy. Dùng để phân tầng khi lấy mẫu. |
| `has_figure` | integer | luôn | 0, 1 | 1 nếu câu có số (không tính năm). |
| `stratum` | string | luôn |  | Nhóm lấy mẫu của câu. Cần để tính lại tỷ lệ đúng khi mẫu không đều. |

**4. Nhãn**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `label` | string | luôn | QUANTIFIED_CLAIM, QUALITATIVE_CLAIM, VAGUE, NOT_CLAIM | Đích của T1: QUANTIFIED_CLAIM · QUALITATIVE_CLAIM · VAGUE · NOT_CLAIM. UNSURE không bao giờ vào dữ liệu. |
| `is_claim` | boolean | luôn |  | label ≠ NOT_CLAIM. Đích phụ: tuyên bố hay không. |
| `topic` | string / null | gold là tuyên bố | emissions_reduction, renewable_energy, resource_efficiency, waste_and_circularity, green_finance, biodiversity, esg_process_integration, generic_sustainability | Chủ đề (8 loại claim_type của sản phẩm). Bắt buộc với câu gold là tuyên bố; đo độ đúng loại tuyên bố của sản phẩm. |
| `why_not` | string / null | gold NOT_CLAIM | table_heading, broken, other_org, general_knowledge, non_env, other | Vì sao không phải tuyên bố. Dùng để phân tích lỗi và sửa bộ lọc. |

**5. Nguồn và chất lượng nhãn**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `label_source` | string | luôn | teacher, gold_consensus, gold_agree, gold_single | teacher, hoặc gold_consensus (qua họp), gold_agree (mọi người cùng nhãn), gold_single (một người). |
| `labelers` | array | gold |  | Người gán. Gold phải có ít nhất một người. |
| `codebook_version` | string | gold |  | Phiên bản bộ quy tắc lúc gán (codebook v1.x). |
| `confidence_min` | integer / null | gold | 1, 2, 3 | Độ chắc thấp nhất trong các người gán (1–3). Có thể dùng làm trọng số. |
| `needs_context` | boolean | gold |  | Có người phải đọc câu trước/sau mới quyết được. Đo riêng nhóm này. |
| `ai_assisted` | boolean | gold | False | Luôn false: câu có AI hỗ trợ không được vào gold. |
| `flags` | array | không |  | OVERCLAIM / INCONSISTENCY / FUTURE: tín hiệu tẩy xanh, dữ liệu cho bước sau. |
| `teacher_model` | string | thầy |  | Mô hình thầy (vd gemma-4-31B-it). |
| `prompt_version` | string | thầy |  | Phiên bản prompt thầy (teacher-claim-v1, v2…). Phải khớp codebook đang dùng cho gold. |
| `teacher_runs` | integer | thầy |  | Số lần thầy gán câu này (cần ≥ 3, hoặc 2 lượt kèm `teacher_review`). |
| `teacher_agreement` | number | thầy |  | Tỷ lệ lần gán trùng nhãn cuối (0–1). Không có `teacher_review` thì chỉ huấn luyện câu ≥ 0,67. |
| `teacher_review` | string / null | không | agree, adjudicated | Claude: hai lượt độc lập trùng nhau (agree), hoặc khác nhau / đáng ngờ nên được đọc lại và quyết (adjudicated). |

**6. Chia tập**

| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |
|---|---|---|---|---|
| `split` | string | luôn | train, dev, test | train = nhãn thầy · dev = gold kiểm định · test = gold HPG. Không còn review/unassigned. |
| `set` | string | luôn | corpus, audit, hpg | Bộ dữ liệu gốc của câu. |
| `contract_version` | string | luôn | t1-example-v1 | Phiên bản khung này. |

**Quy tắc giữa các dòng** (lệnh `python training/t1_data.py check`):

| Mã | Quy tắc | Vì sao |
|---|---|---|
| R1 | `id` không trùng | Một câu chỉ có một nhãn trong một tập |
| R2 | Công ty ở test không có dòng nào ở train | Đo đúng khả năng tổng quát sang công ty mới |
| R3 | Không id nào trong `exclude_from_training.txt` nằm ở train | Dev và test không bị rò vào train |
| R4 | Không câu nào trùng chữ giữa train và dev/test | Như R3, kể cả khi id khác nhau |
| R5 | Gold không bao giờ nằm ở train | Gold là thước đo |
| R6 | Dòng thầy cần ≥ 3 lần gán và đồng thuận ≥ 0,67 (lệnh `combine` bỏ các dòng chưa đạt) | Chỉ học từ nhãn thầy ổn định |
| R7 | Mỗi lớp có ít nhất 100 dòng ở train, 15 dòng ở dev và test (thiếu thì cảnh báo) | Không báo F1 của một lớp chỉ có vài câu |
| R8 | Train và test che số theo cùng một cách (`mask_version`); báo các chữ số còn sót sau khi che | Đầu vào lúc huấn luyện và lúc dùng phải giống nhau |

Lệnh `check` trên file nhãn thầy hiện có (`teacher_claim_gemma-4-31B-it.jsonl`, chưa theo khung) đã phát hiện hai lỗi:
- hai công ty **pan** và **sab** nằm ở cả train lẫn test (do split cũ của kho chia theo tài liệu, không theo công ty);
- **24 câu của dev** nằm trong train.

Khung mới sửa cả hai: mọi dòng thầy đều thuộc train, dev và test chỉ gồm câu người gán, và mọi id của dev/test bị loại khỏi train.

## 7. Từ nhãn đến huấn luyện

```bash
# 1. gold
python training/gold_t1_pack.py merge --set audit && python training/gold_t1_pack.py merge --set hpg
python training/t1_data.py from-gold --set audit          # → training/data/t1/dev_audit.jsonl
python training/t1_data.py from-gold --set hpg            # → training/data/t1/test_hpg.jsonl
# 2. nhãn thầy (prompt v2, ≥ 3 lần chạy với seed khác nhau)
python training/teacher_label.py claim --n 4000 --max-calls 200 --model gemma-4-31B-it   # × 3
python training/t1_data.py from-teacher <run1.jsonl> <run2.jsonl> <run3.jsonl>           # → train_teacher.jsonl
# 3. kiểm và gộp
python training/t1_data.py check                          # phải ra "đạt"
python training/t1_data.py combine                        # → training/data/t1/t1_all.jsonl
# 4. huấn luyện (Colab/Kaggle T4)
python training/train_classifier.py --data training/data/t1/t1_all.jsonl --label-field label \
       --text-field text_masked --exclude training/data/gold_t1/exclude_from_training.txt \
       --model microsoft/mdeberta-v3-base --epochs 3 --fp16 --out training/runs/t1_mdeberta
```

**Lưu ý về lô thầy 400 câu hiện có:** cả 24 câu QUANTIFIED của lô này đã vào dev, nên train hiện **không còn câu QUANTIFIED nào**. Lần chạy thầy 4.000 câu phải lấy mẫu sao cho đủ R7. `build_claim_sentences.py` đã có cờ `has_figure` để phân tầng việc này.

## 8. Chứng minh mô hình hợp với miền: phần báo cáo cho BGK

| # | Thí nghiệm | Số đo | Trả lời câu hỏi |
|---|---|---|---|
| E1 | Độ tin của nhãn người | κ lượt 1 (tuyên bố/không và 5 nhãn) kèm khoảng tin cậy 95%; số câu qua họp; số quy ước mới; giây/câu | Thước đo có đáng tin không? |
| E2 | Nhãn thầy so với gold dev | accuracy, macro-F1 kèm khoảng tin cậy, P/R/F1 từng lớp, ma trận nhầm | Có nên học từ nhãn thầy không? |
| E3 | So sánh trên test HPG | macro-F1 (kèm khoảng tin cậy) và recall lớp tuyên bố của bốn cách: (a) luật hiện tại · (b) mô hình đa ngôn ngữ zero-shot, không huấn luyện (mDeBERTa-xnli) · (c) học trò · (d) thầy | Huấn luyện trên dữ liệu miền có hơn mô hình chung và hơn luật không, trên một công ty chưa thấy? |
| E4 | Đường học | macro-F1 dev của học trò với 500 / 1.000 / 2.000 / 4.000 câu train | Dữ liệu miền có tác dụng không, bao nhiêu thì đủ? |
| E5 | Phân tích lỗi | Lỗi theo `why_not`, `needs_context`, `lang`, `source_kind` | Mô hình sai ở đâu, cần sửa gì? |

"**Hợp với miền**" được chứng minh bằng hiệu số (c) − (b) và (c) − (a) trên test HPG. Cận dưới khoảng tin cậy phải lớn hơn 0, và κ của nhãn người phải đạt ngưỡng (E1).

Lệnh `report` tự sinh `benchmark/gold_t1/{hpg,audit}_report.md`, gồm E1, E2, độ chính xác và recall của luật, và độ đúng loại tuyên bố của sản phẩm. Báo cáo cũng in "Được báo cáo cho BGK: CÓ/CHƯA" theo các ngưỡng đã đăng ký ngày 29/09: κ ≥ 0,70 và ≥ 60 câu gold.

## 9. Ngưỡng cần đăng ký TRƯỚC khi có nhãn đầu tiên (đề xuất, chờ Nhân xác nhận)

Đã có trong `configs/measurement_decisions.yaml` (29/09): κ ≥ 0,70; không báo số đo nào khi có dưới 60 câu gold.

Đề xuất thêm dưới dạng phiên bản mới `measurement-decisions-v2`. Phải ghi **trước** khi nhãn lô 1 về:

| Quyết định | Ngưỡng đề xuất | Nguồn |
|---|---|---|
| Dùng nhãn thầy để huấn luyện | macro-F1 thầy trên dev ≥ 0,70 **và** F1 tuyên bố/không ≥ 0,85; không đạt thì sửa prompt trước khi chạy 4.000 câu | mới |
| Học trò thay được luật | macro-F1 ≥ luật **và** recall lớp tuyên bố ≥ luật + 10 điểm; precision giảm không quá 5 điểm (trên test HPG) | `training/README.md` §5 |
| Được nói "hợp với miền" | cận dưới khoảng tin cậy của (học trò − zero-shot) > 0 trên test HPG | mới |

## 10. Lịch đến Bán kết 25/10

| Ngày | Việc |
|---|---|
| 12/10 | Gửi lô 1 của hai bộ (39 + 40 câu, khoảng 35 phút/người). Đăng ký ngưỡng mục 9 |
| 14/10 | Hạn lô 1 → `import`, `consensus` |
| 15/10 | Họp 1 (khoảng 60 phút) → bộ quy tắc v1.x; cập nhật prompt thầy v2; chạy thầy 4.000 câu × 3 |
| 15–21/10 | Lô 2–12 (HPG) và lô 2–4 (audit): 675 câu, khoảng 4,7 giờ/người nếu mỗi người gán hết, tức khoảng 40 phút/ngày |
| 18/10, 21/10 | Họp 2, họp 3 → `merge`, `report` |
| 22–23/10 | `from-gold`, `from-teacher`, `check`, `combine`; huấn luyện trên T4; chạy E2–E5 |
| 24/10 | Hoàn tất phần báo cáo cho BGK từ `benchmark/gold_t1/*_report.md` |

Nếu thiếu thời gian: làm hết bộ audit trước (E2 quyết định có dùng nhãn thầy không), rồi càng nhiều lô HPG càng tốt. Vì các lô là mẫu ngẫu nhiên, mỗi lô làm xong vẫn là mẫu đại diện.

## 11. Nhãn của Claude: dữ liệu khởi đầu và mốc so sánh (13/10/2026)

**Công cụ:** [`training/claude_labels.py`](../../training/claude_labels.py) · bộ quy tắc cho Claude [`training/data/claude/CODEBOOK.md`](../../training/data/claude/CODEBOOK.md) (giống bản của người, cộng phần làm rõ chủ đề) · quyết định khi đọc lại [`training/data/claude/adjudicate_2026-10-13.py`](../../training/data/claude/adjudicate_2026-10-13.py).

| Bộ | Câu | Dùng để | Nơi lưu |
|---|---|---|---|
| train | 500 câu từ phần train của kho: 13 công ty, mỗi công ty ≤ 60 câu; 356 câu tiếng Việt, 144 câu tiếng Anh; 6 nhóm theo tín hiệu của luật; 100 câu trùng với lô gemma; không id nào của dev/test | Huấn luyện (`label_source` = teacher, `teacher_model` = claude-opus-5-5) | `training/data/t1/train_claude.jsonl` (498 câu, bỏ 2 câu UNSURE) |
| so sánh | 79 câu lô 1 (40 audit + 39 HPG), cùng chữ và ảnh trang người gán thấy | Mốc AI so với gold khi người gán xong; **không bao giờ** vào gold hay train | `training/data/gold_t1/ai/claude_compare.jsonl`: **không mở trước khi nộp nhãn lô 1 của chính mình** |

**Cách làm (cùng kỷ luật như người):**
1. Mỗi câu được hai agent Claude gán **độc lập** (lượt A, lượt B). Các batch trộn lẫn câu train và câu so sánh, và chỉ chứa đúng những gì người gán thấy.
2. Đối chiếu hai lượt: **κ A–B = 0,92** (5 nhãn), 0,98 (tuyên bố/không), trùng nhãn 554/579 câu.
3. Đọc lại 170 câu: mọi câu khác nhãn, khác chủ đề hoặc lý do, UNSURE, độ chắc 1, có cờ, câu có số mà gán QUALITATIVE, cộng 42 câu đồng ý chọn ngẫu nhiên. Kết quả: 21 câu đổi nhãn so với lượt A. Trong 42 câu soát ngẫu nhiên không câu nào phải sửa, nên sai số ước tính của các câu hai lượt đã đồng ý là dưới khoảng 7% (95%).
4. Rà thêm các câu hai lượt đồng ý xem có vi phạm Q10–Q17 không; không phát hiện câu nào.

**Kết quả trên 498 câu train:** NOT_CLAIM 331 · QUALITATIVE 90 · VAGUE 39 · QUANTIFIED 38; 85 câu cần ngữ cảnh; 18 cờ FUTURE, 4 OVERCLAIM, 1 INCONSISTENCY.

| So sánh (chưa phải gold) | Kết quả |
|---|---|
| Claude và gemma trên 100 câu chung | Đồng ý 89/100; κ 0,63. Gemma hay gọi NOT_CLAIM những câu Claude xếp QUALITATIVE (5 câu) |
| Bộ trích bằng luật so với Claude (train) | Precision 115/209 = 55%; recall 115/167 = 69%. Luật giữ gần một nửa câu không phải tuyên bố và bỏ sót khoảng 1/3 tuyên bố |

**Giới hạn, nói rõ khi báo cáo:**
- Hai lượt cùng một mô hình nên dễ sai giống nhau. κ A–B chỉ cho thấy Claude **ổn định**, không cho thấy Claude **đúng**; độ đúng chỉ đo được bằng gold của người (`report` có mục "Claude so với gold").
- 498 câu chưa đủ cho các lớp hiếm (quy tắc R7 cần ≥ 100 câu/lớp ở train). Bộ này là dữ liệu khởi đầu chất lượng cao, đi cùng lần chạy thầy 4.000 câu (prompt v2 có Q10–Q17).
- Q10–Q17 đang là đề xuất. Nếu họp 1 đổi quy ước nào, chạy lại `adjudicate` cho các câu liên quan rồi `finalize` và `from-claude`.
