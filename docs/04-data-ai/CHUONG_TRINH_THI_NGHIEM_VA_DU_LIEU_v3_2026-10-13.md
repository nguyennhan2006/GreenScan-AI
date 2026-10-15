# Chương trình thí nghiệm và mở rộng dữ liệu v3

**Ngày:** 13/10/2026 · **Người đọc:** nhóm (Nhân, Quỳnh, Thảo); mục 1–3 dùng làm phụ lục phương pháp cho BGK.
**Nối tiếp:** [`data/COLLECTION_PLAN_v2.md`](../../data/COLLECTION_PLAN_v2.md) (nguồn Việt Nam, lớp bằng chứng độc lập) · [`QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`](QUY_TRINH_GAN_NHAN_T1_2026-10-11.md) (gold, khung dữ liệu) · kết quả Kaggle `benchmark/t1_kaggle/`.

---

## 0. Tóm tắt

- Sản phẩm phải chứng minh **bốn luận điểm** (mục 1). Mỗi luận điểm có thí nghiệm riêng, có ngưỡng đạt **ghi trước khi đo**, và có hạn (Bán kết 25/10 hoặc Chung kết 10/11).
- Bằng chứng hiện có, **chưa có gold người**, nên mọi số đều đo trên nhãn Claude:
  - học trò e5-base: macro-F1 0,66 (kiểm định chéo theo công ty);
  - luật hiện tại: 0,37;
  - zero-shot: 0,30;
  - đường học còn dốc;
  - tốc độ trên CPU 117 ms/câu.
- **Dữ liệu Việt Nam vẫn là miền chính** và là nơi duy nhất dùng để đo kết quả cuối. Dữ liệu nước ngoài dùng vào ba việc:
  1. học quy trình xử lý của các cơ quan quản lý đã xử lý tẩy xanh thật;
  2. làm "đáp án đã phán quyết" để thử hệ thống từ đầu đến cuối;
  3. làm dữ liệu phụ cho huấn luyện (chuyển giao chéo ngôn ngữ).
- Không cần tài khoản trả phí. Mục 6 liệt kê tài khoản miễn phí nào mở khóa thí nghiệm nào.

## 1. Bốn luận điểm cần chứng minh trước BGK

| # | Luận điểm | Phản biện BGK có thể đặt | Thí nghiệm trả lời |
|---|---|---|---|
| L1 | **Thước đo đáng tin**: nhãn người nhất quán; nhãn AI dùng để huấn luyện đủ tốt | "Các em tự gán rồi tự chấm?" | A1–A5 |
| L2 | **Nhận diện và đối chiếu tốt hơn cách đang có** (luật, đọc tay, LLM chung), trên doanh nghiệp Việt Nam chưa thấy | "Một mô hình chung như ChatGPT có làm được không?" | B1–B9, C1–C3, D1–D4 |
| L3 | **Bắt được tẩy xanh thật, không vu oan** | "Hệ thống có bắt được vụ nào đã bị xử lý chưa? Có quy kết sai doanh nghiệp không?" | E1–E4, G1–G3 |
| L4 | **Dùng được thật**: nhanh hơn ở cùng độ tin cậy, rẻ, chạy được offline | "Kiểm toán viên có tiết kiệm được thời gian không?" | F1–F4, B7 |

## 2. Ma trận thí nghiệm

Ký hiệu hạn: **BK** = trước Bán kết 25/10 · **CK** = trước Chung kết 10/11 · **Sau** = sau cuộc thi. Ngưỡng đạt phải ghi vào `configs/measurement_decisions.yaml` (phiên bản mới) **trước** khi đo.

### A. Thước đo (L1)

| ID | Giả thuyết | Dữ liệu | Chỉ số | Ngưỡng đạt (đề xuất) | Hạn |
|---|---|---|---|---|---|
| A1 | Người với người gán thống nhất | Lô 1 HPG + audit (79 câu, 3 người) | κ tuyên bố/không; κ 4 lớp; Fleiss κ | κ tuyên bố/không ≥ 0,70 (đã đăng ký 29/09) | BK |
| A2 | Nhãn Claude gần với gold | 79 câu lô 1 + các lô sau | accuracy, macro-F1, κ (Claude, gold) | κ ≥ 0,60 thì dùng Claude làm thầy; dưới mức đó thì dùng Claude làm ứng viên cho người duyệt | BK |
| A3 | Nhãn gemma kém Claude | 160 câu audit | macro-F1 (gemma, gold) so với (Claude, gold), so theo cặp | Ghi nhận; chọn thầy theo số đo | CK |
| A4 | Quy ước tốt lên qua các buổi họp | Tỷ lệ bất đồng lượt 1 theo lô | % câu phải họp ở lô 1 so với lô 5+ | Giảm ≥ 30% tương đối | CK |
| A5 | Một người tự gán lại vẫn khớp với chính mình | 20 câu gán lại sau ≥ 7 ngày | κ của cùng một người qua hai lần | ≥ 0,75 | CK |

### B. Nhận diện tuyên bố T1 (L2, L4)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng đạt (đề xuất) | Hạn |
|---|---|---|---|---|---|
| B1 | Học trò hơn luật và hơn zero-shot trên công ty **chưa thấy** | Test HPG gold; so theo cặp bằng bootstrap | macro-F1; recall lớp tuyên bố | Cận dưới khoảng tin cậy của (học trò − luật) > 0 và của (học trò − zero-shot) > 0; recall ≥ luật + 10 điểm (README §5) | BK (lô 1), CK (đủ) |
| B2 | Tổng quát được cho từng công ty | Bỏ-một-công-ty (13 fold) | macro-F1 theo từng công ty; công ty kém nhất | Không công ty nào < 0,5 | BK |
| B3 | Cần bao nhiêu nhãn | Đường học với **cùng số bước học**, 3 seed | macro-F1 theo 25/50/75/100%; ngoại suy | Biết điểm bão hòa → quyết định số nhãn cần mua thêm | BK |
| B4 | Dữ liệu tiếng Anh giúp được tiếng Việt | Thêm EnvironmentalClaims (EN) vào train; test vẫn là VN | Δ macro-F1 trên VN | Cận dưới Δ > 0 thì giữ | CK |
| B5 | Học thêm văn bản miền giúp được | Tiền huấn luyện tiếp (MLM) trên 66.539 câu báo cáo VN trước khi tinh chỉnh | Δ macro-F1 | Cận dưới Δ > 0 | CK |
| B6 | Mô hình biết lúc nào nó không chắc | Hiệu chỉnh nhiệt độ; vẽ đường độ phủ – độ chính xác | ECE; độ chính xác ở độ phủ 80% | ECE ≤ 0,05; ở độ phủ 80% đạt ≥ +10 điểm so với độ phủ 100% (phần câu bỏ lại đẩy cho người duyệt) | BK |
| B7 | Chạy được trên laptop | e5-small / e5-base / chưng cất / ONNX int8; đo trên i7-1355U | ms/câu, RAM, Δ macro-F1 | ≤ 50 ms/câu và mất ≤ 2 điểm | CK |
| B8 | Vững trước nhiễu PDF/OCR | Train trên kho crawl, test trên chữ từ parser PDF; thêm nhiễu OCR giả lập | Δ macro-F1 theo mức nhiễu | Giảm ≤ 5 điểm ở mức nhiễu thực tế | CK |
| B9 | Che số không làm mất nhiều | Câu đã che so với câu gốc, 3 seed (lượt 1 Kaggle: che số 0,657, câu gốc 0,627) | Δ macro-F1 kèm khoảng tin cậy | Ghi nhận cái giá của quyền riêng tư | BK |

### C. Truy xuất bằng chứng (L2)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng | Hạn |
|---|---|---|---|---|---|
| C1 | Kết hợp BM25 + dense + rerank tìm đúng đoạn bằng chứng | Cặp gold (tuyên bố, bằng chứng) | recall@5, MRR | +10 điểm so với `lite` (đã đăng ký, RQ4) | CK |
| C2 | Truy xuất của ta không thua chuẩn quốc tế | [ClimRetrieve](https://www.sfi.ch/en/publications/n-24-89-climretrieve-a-benchmarking-dataset-for-information-retrieval-from-corporate-climate-disclosures) (EMNLP 2024; 30 báo cáo, hơn 8,5 nghìn cặp câu hỏi–nguồn–trả lời) | recall@k so với bảng của bài báo | Ghi nhận; dùng làm chuẩn ngoài | Sau |
| C3 | Không dùng bằng chứng "từ tương lai" | Bật/tắt lọc năm và phạm vi | Số verdict thay đổi; số cặp sai kỳ | 0 cặp sai kỳ | BK |

### D. Đối chiếu, kiểm chứng (L2, L3)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng | Hạn |
|---|---|---|---|---|---|
| D1 | Kết luận đúng, ít "mâu thuẫn" sai | Cặp gold | accuracy verdict; precision SUPPORTS/CONTRADICTS; tỷ lệ báo mâu thuẫn sai | SUPPORTS ≥ 0,80, CONTRADICTS ≥ 0,90 (đã đăng ký) | CK |
| D2 | Bắt được bẫy số liệu | Sinh ca nhiễu: đổi đơn vị, kỳ, phạm vi, tổng–thành phần | Tỷ lệ phát hiện theo loại bẫy | ≥ 90% với đơn vị và kỳ | BK |
| D3 | Không chỉ giỏi trên dữ liệu nhà | Climate-FEVER (1.535 tuyên bố, 7.675 cặp với Wikipedia) | macro-F1 phần quan hệ | Ghi nhận; kiểm tra sức khỏe mô hình | Sau |
| D4 | Kiểm tra số học nội bộ tìm ra lỗi thật | Tính lại tỷ lệ; cùng chỉ số mang hai giá trị trên một trang; tiêm lỗi giả | Precision trên lỗi tiêm; số phát hiện thật | Bắt lại được ca HPG 80% so với 61% và 17,48 so với 17,51 | BK |

### E. Đầu–cuối trên ca thật (L3)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng | Hạn |
|---|---|---|---|---|---|
| E1 | Bắt được tuyên bố **đã bị cơ quan quản lý kết luận** là tẩy xanh | Bộ "đáp án đã phán quyết" (mục 4.2): SEC (BNY, DWS, KDP: đã có trong `real_cases/`), KLM (đã có), ASIC (Vanguard, Mercer, Active Super), một số phán quyết ASA | recall vấn đề đã phán quyết; hệ thống có chỉ đúng câu không | ≥ 70% vấn đề được đưa lên hàng đợi; n nhỏ nên báo từng ca | CK |
| E2 | Không vu oan doanh nghiệp làm tốt | Công ty đối chứng có assurance độc lập, không có vi phạm | Số phát hiện "mâu thuẫn" sai trên 100 tuyên bố | ≤ 2 | CK |
| E3 | Ra phát hiện có giá trị trên doanh nghiệp Việt Nam | HPG (80% so với 61%; điện mặt trời ≤ 0,5%) + 2–3 công ty phát thải cao có bằng chứng độc lập (mục 4.1) | Số phát hiện được chuyên gia xác nhận | ≥ 3 phát hiện xác nhận được trên mỗi công ty | BK (HPG), CK (thêm) |
| E4 | Chuyên gia thấy phát hiện có ích | 20 phát hiện, chuyên gia không biết nguồn đánh giá (giảng viên kiểm toán, Thảo) | Likert 1–5 cho "đúng", "có ích", "đủ căn cứ" | Trung vị ≥ 4 | CK |

### F. Giá trị cho người dùng (L4)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng | Hạn |
|---|---|---|---|---|---|
| F1 | Nhanh hơn ở cùng độ tin cậy | Bài đo thời gian 20 → 40 câu; **thiết kế hoán vị** (mỗi người làm nửa tay, nửa có hệ thống, đổi chéo) | phút/câu; độ đúng so với gold | Giảm ≥ 30% thời gian; độ đúng không giảm (cận dưới khoảng tin cậy của hiệu ≥ −5 điểm) | BK (thử), CK |
| F2 | Quyết định của người duyệt tốt hơn khi có hệ thống | Người duyệt quyết với và không có bằng chứng do hệ thống gợi ý | Đồng ý với gold | +10 điểm | CK |
| F3 | Dễ dùng | System Usability Scale, 5–8 người (sinh viên kế toán, kiểm toán viên) | Điểm SUS | ≥ 70 | CK |
| F4 | Rẻ | Ghi token, thời gian, phần cứng cho mỗi báo cáo | VNĐ/báo cáo; phút/báo cáo | Báo cáo kèm mức offline | BK |

### G. Pháp lý (L3)

| ID | Giả thuyết | Thiết kế | Chỉ số | Ngưỡng | Hạn |
|---|---|---|---|---|---|
| G1 | Bộ luật phủ đủ nghĩa vụ chính | Checklist TT 96 mục 6 + QĐ 13 + NĐ 06/119 (Thảo) | % nghĩa vụ có quy tắc | ≥ 80% nghĩa vụ chính | CK |
| G2 | Phát hiện pháp lý chính xác | HPG + 5 công ty; Thảo duyệt | precision phát hiện pháp lý | ≥ 0,85 | CK |
| G3 | Danh mục văn bản đúng hiệu lực | Đối chiếu ngày hiệu lực với văn bản gốc | Số sai | 0 (các sửa ngày 06/10 chờ Thảo xác nhận) | BK |

### H. Công bằng, độ vững

| ID | Thiết kế | Chỉ số | Hạn |
|---|---|---|---|
| H1 | Tách kết quả theo ngôn ngữ, ngành, quy mô, loại báo cáo | macro-F1 theo nhóm; nhóm kém nhất | CK |
| H2 | Viết lại tuyên bố (đổi chữ, giữ ý) | Tỷ lệ đổi nhãn | Sau |

## 3. Nguyên tắc thiết kế để kết luận chặt

1. **Tách ba câu hỏi, không trộn:**
   - nhãn có đáng tin không (người với người);
   - thầy có đúng không (thầy với gold);
   - học trò có đúng không (học trò với gold).

   "Học trò so với thầy" chỉ cho biết học trò bắt chước giỏi đến đâu, không bao giờ được trình bày như độ chính xác.
2. **Đơn vị độc lập là công ty, không phải câu.** Chia tập, kiểm định chéo và khoảng tin cậy đều tính theo công ty. Nếu lấy mẫu lại theo câu, khoảng tin cậy hẹp giả tạo.
3. **Đăng ký trước:** ngưỡng, chỉ số chính, cách chọn mô hình. Muốn đổi thì thêm phiên bản mới và ghi lý do vào `DECISIONS_LOG`.
4. **Tập test chỉ chạm một lần.** Chọn mô hình trên dev (audit) hoặc trên kiểm định chéo lồng nhau; HPG gold chỉ dùng cho con số cuối.
5. **So sánh theo cặp kèm khoảng tin cậy.** Chỉ nói "hơn" khi cận dưới của hiệu số lớn hơn 0. Với nhiều phép so sánh chính, chỉnh theo Holm.
6. **Mốc so sánh phải mạnh và công bằng:**
   - đoán toàn lớp đông nhất;
   - luật hiện tại;
   - zero-shot;
   - LLM lớn (thầy);
   - so luật ở dạng nhị phân, vì luật không có lớp VAGUE.
7. **Tỷ lệ cơ sở.** Mẫu được lấy phân tầng nên tỷ lệ tuyên bố bị đẩy lên. Phải báo thêm chỉ số ước lượng trên phân phối tự nhiên (trọng số ngược xác suất lấy mẫu), nếu không precision ngoài đời sẽ thấp hơn số báo cáo.
8. **Nhiều seed, báo độ dao động.** Lượt 1 cho thấy chỉ đổi seed, điểm trên tập so sánh đã chênh từ 0,50 đến 0,62.
9. **Báo cả kết quả âm.** Ví dụ lượt 1: mDeBERTa sụp về lớp đông nhất; đường học ở lượt 1 bị nhiễu vì số bước học khác nhau.
10. **Truy vết đủ cho mỗi con số:** phiên bản dataset, kernel, seed, codebook, prompt, commit.
11. **Không vòng tròn.** Nhãn AI không bao giờ làm test. Dữ liệu nước ngoài không thay test Việt Nam.

## 4. Mở rộng dữ liệu v3

### 4.1 Việt Nam: miền chính, mở rộng theo chiều sâu

Danh mục 25–30 doanh nghiệp phát thải cao của v2 giữ nguyên. Điểm mới là thêm **nguồn bằng chứng độc lập theo cơ sở sản xuất**, nhờ vậy kiểm chứng được tuyên bố về phát thải, công nghệ và công suất mà không phụ thuộc vào báo cáo của chính doanh nghiệp.

| Nguồn | Kiểm chứng được gì | Truy cập | Lưu ý phản biện |
|---|---|---|---|
| [Climate TRACE](https://climatetrace.org/data): ước tính phát thải theo cơ sở (nhà máy thép, xi măng, điện) | **Bậc độ lớn** của Scope 1 do DN tự báo (ví dụ HPG 23,5 triệu tCO2e) | Tải miễn phí, CC BY 4.0; có API beta | Là ước tính từ vệ tinh và mô hình, không phải số đo. Chỉ dùng để báo khi chênh rất lớn, không để kết luận vi phạm |
| [Global Energy Monitor, Global Steel Plant Tracker](https://gem.wiki/Hoa_Phat_Dung_Quat_steel_plant) (và Coal Plant Tracker) | Công nghệ (BF-BOF hay EAF), công suất, năm vận hành: đối chiếu tuyên bố "thép xanh", "chuyển sang EAF" | Tải dataset trên trang GEM (có form) | Số công suất có thể cũ hơn báo cáo; luôn ghi phiên bản tracker |
| Phụ lục QĐ 13/2024 | Nghĩa vụ kiểm kê KNK; năng lượng (TOE) theo cơ sở | Đã OCR trong repo | **Không** có tCO2e (đã sửa 28/09) |
| Mục "Công khai vi phạm, khắc phục vi phạm" trên cổng Bộ NN&MT (mae.gov.vn) + quyết định xử phạt cấp tỉnh | Mâu thuẫn với "tuân thủ pháp luật BVMT"; mục 6.4 TT 96 | Thủ công; Thảo lập danh mục | Số vụ vi phạm 2022–2025 [theo báo chí](https://tapchikinhtetaichinh.vn/gan-15000-vu-vi-pham-moi-truong-bi-phat-hien-xu-ly-giai-doan-2022-2025-158659.html) gần 15.000; cần khớp tên cơ sở với mã chứng khoán |
| [SBTi Target Dashboard](https://sciencebasedtargets.org/target-dashboard) và Net Zero Tracker | Tuyên bố "mục tiêu khoa học", "Net Zero": đã được SBTi xác nhận chưa | Tải .xls theo công ty hoặc theo mục tiêu | Có thể rất ít DN Việt Nam; "chưa có trong danh sách" ≠ sai, chỉ là chưa được xác nhận |
| CBTT HOSE/HNX, BCTC kiểm toán (thuế BVMT, chi phí môi trường) | Số đã kiểm toán đối chiếu với số tự công bố | Đã có trong kho crawl | — |

**Đề xuất thêm ngành ngân hàng** (VCB, BID, TCB, ACB): tuyên bố "tín dụng xanh" là loại tuyên bố có số và có mỏ neo pháp lý (quy định của NHNN về tín dụng xanh). Lớp `green_finance` hiện gần như trống (1 câu train). Cần kiểm tra văn bản NHNN cụ thể trước khi dùng làm mỏ neo.

### 4.2 Quốc tế: học quy trình chuyên nghiệp và lấy "đáp án đã phán quyết"

**a) Ca đã có phán quyết.** Mỗi ca cho ba thứ: câu tuyên bố gốc, lập luận của cơ quan quản lý, và loại vi phạm. Đây là bộ thử đầu–cuối tốt nhất có thể có, vì đáp án do bên thứ ba có thẩm quyền đưa ra.

| Nguồn | Có gì | Dùng cho |
|---|---|---|
| ASIC (Úc): [Mercer, phạt 11,3 triệu AUD](https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2024-releases/24-173mr-asic-s-first-greenwashing-case-results-in-landmark-113-million-penalty-for-mercer); Vanguard 12,9 triệu; [Active Super 10,5 triệu (03/2025)](https://cm.twobirds.com/en/insights/2025/australia/three-wins-in-a-row-active-super-to-pay) | Bản án nêu rõ tuyên bố nào sai và vì sao. Ví dụ: lời không kèm điều kiện thì không thể "sửa" bằng cách dẫn sang tài liệu chính sách khác | E1; bổ sung quy ước VAGUE và quy ước loại trừ |
| SEC (Mỹ): BNY, DWS, KDP | Đã có trong `data/real_cases/` | E1 (đang dùng) |
| Tòa Amsterdam: KLM (2024) | Đã có | E1 |
| ASA (Anh): phán quyết về quảng cáo xanh (hàng không 12/2023: [Air France, Lufthansa, Etihad](https://cityam.com/?p=2089028); thời trang: Nike, Lacoste, Superdry) | Lý do cấm từng tuyên bố; chuẩn "cơ sở của tuyên bố phải rõ" (CAP Code) | E1; mẫu câu VAGUE |
| [ESMA, Final Report on Greenwashing (06/2024)](https://www.arendt.com/news-insights/news/esma-final-report-on-greenwashing/) | Định nghĩa chung của 3 cơ quan giám sát EU; cách giám sát dựa trên rủi ro; khuyến nghị dùng NLP | Nguyên lý thiết kế hàng đợi theo rủi ro; trích dẫn cho BGK |
| EU: [Chỉ thị 2024/825 (EmpCo), áp dụng từ 27/09/2026](https://www.taylorwessing.com/en/insights-and-events/insights/2025/07/green-claims-richtlinie) | Cấm tuyên bố chung chung ("thân thiện môi trường") nếu không có bằng chứng, và cấm "trung hòa carbon" chỉ dựa vào bù trừ. Green Claims Directive [đang tạm dừng](https://www.climatepartner.com/en/knowledge/glossary/green-claims-directive) | Căn cứ quốc tế cho lớp VAGUE và cờ OVERCLAIM; so sánh với khung Việt Nam |

**b) Bộ dữ liệu nghiên cứu.** Tất cả đều tiếng Anh, chỉ dùng làm dữ liệu phụ hoặc chuẩn ngoài:

| Bộ | Quy mô | Giấy phép | Dùng cho |
|---|---|---|---|
| [EnvironmentalClaims](https://huggingface.co/datasets/climatebert/environmental_claims) (Stammbach và cs., ACL 2023) | Khoảng 2,6–3 nghìn câu từ báo cáo DN niêm yết (thẻ dữ liệu ghi số không khớp nhau) | CC BY-NC-SA 4.0: được dùng cho cuộc thi và nghiên cứu, **không** dùng thương mại | B4 (chuyển giao chéo ngôn ngữ) |
| Climate-FEVER | 1.535 tuyên bố, 7.675 cặp với Wikipedia, nhãn SUPPORTS/REFUTES/NEI/DISPUTED | [Chưa rõ](https://www.tensorflow.org/datasets/community_catalog/huggingface/climate_fever), cần kiểm thẻ HF | D3 |
| [ClimRetrieve](https://www.sfi.ch/en/publications/n-24-89-climretrieve-a-benchmarking-dataset-for-information-retrieval-from-corporate-climate-disclosures) (EMNLP 2024) | Hơn 8,5 nghìn cặp, 30 báo cáo | Cần kiểm | C2 |
| A3CG (ACL 2025, [arXiv 2502.15821](https://arxiv.org/pdf/2502.15821v1)) | Cam kết đã làm / dự kiến / không xác định | Cần kiểm | Đối chiếu với cờ FUTURE; ý tưởng nhãn "đã thực hiện" |
| [EmeraldData](https://huggingface.co/datasets/geoka/EmeraldData/blob/main/README.md) | 620 tuyên bố bán tổng hợp, 36% tẩy xanh | Cần kiểm | Thử phần kết luận ở mức tuyên bố, chỉ để tham khảo vì dữ liệu tổng hợp |

**c) Quy trình chuyên nghiệp cần học và mã hóa vào hệ thống:** ISAE 3000/3410 (đảm bảo thông tin phi tài chính và KNK), IFRS S2, GHG Protocol, cách ASA/ASIC xét "ấn tượng tổng thể", và yêu cầu chứng minh của EmpCo. Kết quả mong đợi là một checklist "tuyên bố loại X cần bằng chứng gì", cập nhật vào `VERIFICATION_POLICY.md`.

### 4.3 Dùng dữ liệu nước ngoài mà không lệch miền

1. Dữ liệu nước ngoài **không bao giờ** làm test chính. Test luôn là doanh nghiệp Việt Nam chưa thấy (HPG, và sau đó thêm 1–2 công ty giữ lại).
2. Chỉ dùng cho: huấn luyện phụ (B4), chuẩn ngoài (C2, D3), ca đầu–cuối (E1), và nguyên lý (4.2c).
3. Nếu dịch sang tiếng Việt: kiểm 50 câu bằng dịch ngược và người soát; ghi `source_kind = translated`, rồi đo riêng nhóm này.
4. Thử tỷ lệ trộn (0 / 25 / 50% dữ liệu tiếng Anh) và chọn theo dev tiếng Việt, không theo test.

### 4.4 Gán nhãn hiệu quả hơn

1. **Học chủ động:** ưu tiên đưa cho người các câu học trò không chắc (entropy cao) và các câu mà các thầy bất đồng (Claude, gemma, GLM).
2. **Hội đồng thầy:** ba mô hình gán. Câu nào cả ba đồng ý thì vào train; câu bất đồng thì người quyết. A2 và A3 cho biết có nên tin hội đồng hay không.
3. **Sinh dữ liệu khó cho T2:** đổi đơn vị, kỳ, phạm vi trong cặp số liệu thật để tạo ca phải bắt.
4. **Mở rộng người gán:** mời thêm bạn học, nhưng chỉ nhận người đạt κ ≥ 0,70 trên lô kiểm tra (lô 1 làm đề kiểm tra).

## 5. Lịch đề xuất

| Mốc | Việc |
|---|---|
| Đến 18/10 | Gold lô 1 (A1, A2); D4 (kiểm tra tỷ lệ); B2, B3 (Kaggle v2 + bỏ-một-công-ty); F4 |
| Đến 25/10 (BK) | B1 trên HPG gold đã có; B6 (hiệu chỉnh và từ chối trả lời); E3 HPG; F1 thử nghiệm; tải Climate TRACE + GEM cho HPG; báo cáo trực quan |
| Đến 10/11 (CK) | Đủ gold; B4, B5, B7, B8; C1; D1, D2; E1, E2, E4; F1 đủ, F2, F3; G1–G3; mở rộng 2–3 công ty phát thải cao |
| Sau cuộc thi | C2, D3, H2; ngành ngân hàng |

## 6. Tài khoản: cần gì để làm gì

| Tài khoản | Mở khóa | Bắt buộc? |
|---|---|---|
| Kaggle | Huấn luyện GPU (đã có; khoảng 30 giờ GPU/tuần) | Đã có |
| **Hugging Face (token đọc)** | Tải bộ dữ liệu và mô hình có điều kiện; lưu mô hình học trò riêng tư để đưa vào sản phẩm | Nên có (B4, B7) |
| **Khóa API Anthropic** (có hạn mức chi tiêu) | Chạy Claude làm thầy và trọng tài ở quy mô hàng nghìn câu bằng script có kiểm soát chi phí, thay vì chạy agent tay | Tùy chọn; ước tính vài USD cho 4.000 câu × 2 lượt, cần kiểm giá trước |
| Google (Gmail) | Điền form tải dataset Global Energy Monitor | Tùy chọn |
| Semantic Scholar API | Lập bản đồ tài liệu cho phần cơ sở lý thuyết | Không bắt buộc |
| CDP, Refinitiv, Bloomberg | Dữ liệu ESG trả phí | **Không dùng.** Trái nguyên tắc v2 (không dữ liệu trả phí) |

Climate TRACE, SBTi, ASIC, SEC, ASA, ESMA, ClimRetrieve và EnvironmentalClaims đều tải công khai, không cần tài khoản.
