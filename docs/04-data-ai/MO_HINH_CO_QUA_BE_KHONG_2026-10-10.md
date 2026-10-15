# Mô hình có "quá bé" cho bài toán không? — nguyên lý, thước đo, thực nghiệm

**Ngày:** 10/10/2026 · **Lý do viết:** một giảng viên nhận xét *"mô hình LLM của nhóm quá bé, không xử lý được bài toán phức tạp như đã đặt ra"*.
**Bằng chứng đi kèm:** thực nghiệm [`benchmark/size_ladder_2026-10-10/`](../../benchmark/size_ladder_2026-10-10/README.md) (51 ca có đáp án dựng sẵn, GreenScan và 5 mô hình từ ~3,8B tham số kích hoạt tới 753B) · tra cứu tài liệu 10/10, mỗi nguồn gắn nhãn **[VERIFIED]** (đã đọc bản gốc) hoặc **[SECONDARY]**.

---

## 0. Kết luận một đoạn

1. **Tiền đề "mô hình bé" không đúng với sản phẩm.** Chế độ ngoại tuyến **không chạy mô hình ngôn ngữ nào**; chế độ đám mây dùng **GLM-5.2: 753 tỷ tham số tổng** (MoE 256 chuyên gia, 8 chuyên gia kích hoạt mỗi token, ngữ cảnh 1 triệu token — model card Hugging Face [VERIFIED]; dòng GLM-5 ghi "744B, 40B active" trong báo cáo kỹ thuật arXiv:2602.15763 [VERIFIED] — con số kích hoạt của 5.2 là suy ra từ cùng kiến trúc).
2. **Thực nghiệm của nhóm không phát hiện được tác động của kích thước** từ gemma-4-26B-A4B (~3,8B kích hoạt) tới GLM-5.2: trên 32 ca sạch các mô hình đúng 29–32, trên 19 ca trang thật đúng 15–18, khoảng tin cậy chồng lên nhau. Khi văn bản nhiễu, **mô hình lớn sai cùng chỗ với mô hình nhỏ** — bảng bị dàn phẳng làm mất thông tin cột, và cả GLM-5.2 lẫn Llama-70B đều tự tin "khớp hoàn toàn" với con số của cột khác. **Ngoại lệ ở đầu dưới của thang:** mô hình đa dụng 8B chạy trên laptop (qwen3:8b, không tinh chỉnh) đúng 28/32 và 12/19 nhưng có **nhiều xác nhận sai nhất** (3 và 4 — ví dụ "98%" trong bằng chứng được coi là khớp "90%" của tuyên bố) và mất 66–257 giây mỗi ca. Đúng với tài liệu: dưới khoảng 8B, mô hình đa dụng không tinh chỉnh tụt hẳn. GreenScan **không** dùng mô hình cỡ này để ra kết luận — ở chế độ ngoại tuyến, mã quyết định.
3. **Thầy đúng ở một điểm khác, quan trọng hơn:** bộ luật của GreenScan **phủ hẹp** — đúng 20/32 và 7/19, kém mọi mô hình một cách có ý nghĩa thống kê (McNemar p ≤ 0,022). Luật hiếm khi sai khi đã kết luận (6/8 và 3/3), nhưng quá thường xuyên không kết luận: bộ trích bỏ sót tuyên bố, ngưỡng 0,35 giấu các chênh lệch 9–25%, và cổng so sánh có hai lỗ hổng.
4. **Vậy giới hạn không nằm ở số tham số**, mà ở (a) **biểu diễn đầu vào** — bảng mất cấu trúc thì mô hình nào cũng đọc sai; (b) **độ phủ của luật**; (c) **dữ liệu tiếng Việt trong miền** để đo và để tinh chỉnh. Thiết kế đúng là **mô hình đọc để tăng độ phủ, mã kiểm số và cấu trúc, chỗ hai bên bất đồng chuyển người** — và chứng minh trên gold theo ngưỡng đã đăng ký trước.

---

## 1. Bài toán "phức tạp" gồm những gì — và kích thước có phải ràng buộc ở từng chỗ không

Nguyên lý nền: **độ phức tạp của bài toán khác độ phức tạp mỗi bước.** Một bài toán phức tạp được giải bằng cách phân rã thành các bước có thước đo riêng; câu hỏi đúng không phải "mô hình có đủ lớn để giải cả bài không" mà là "**ở bước nào** năng lực của mô hình là ràng buộc, và đo bằng gì".

| # | Bước | Năng lực cần | Hôm nay ai làm | Kích thước có phải ràng buộc? | Bằng chứng | Thước đo |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Đọc PDF, **bảng** | Giữ cấu trúc hàng–cột, số trang | PyMuPDF + pdfplumber | **Không** — mất cấu trúc thì mô hình lớn cũng sai | Thực nghiệm: N02, N05 sai ở GLM-5.2 và 70B; ESGReveal: chỉ riêng tiền xử lý + truy xuất tốt hơn đã thêm **+21,8 điểm** cho GPT-4 [VERIFIED] | Tỷ lệ ô bảng trích đúng; provenance tới ô |
| 2 | Nhận diện tuyên bố | Hiểu ngữ nghĩa câu | **Luật + từ khoá** | **Có — đây là chỗ yếu nhất của luật** | Thực nghiệm: 13/51 ca không trích được; Stammbach và cs. ACL 2023: SVM n-gram ký tự F1 **70,9** so với RoBERTa-large **84,9** [VERIFIED] — một mô hình 355M tinh chỉnh đã đủ | Precision/recall theo lớp; lấy mẫu câu *không* được trích |
| 3 | Chuẩn hoá 5 thuộc tính | Trích có cấu trúc | Regex + taxonomy | Một phần | ESGReveal: GPT-4 76,9 so với GPT-3.5 47,1 khi trích KPI [VERIFIED] — trích mở thì năng lực mô hình có ý nghĩa | Khớp chính xác từng thuộc tính |
| 4 | Tìm bằng chứng | Truy xuất, không cần sinh | BM25 + n-gram ký tự + RRF | **Không** — và đưa cả báo cáo vào mô hình lớn còn tệ hơn | Lost in the Middle (TACL 2024): giảm >20% khi đáp án nằm giữa ngữ cảnh, kể cả 70B [VERIFIED]; RULER: ngữ cảnh thực dụng ≈ ½ ngữ cảnh quảng cáo (GPT-4 128K→64K) [VERIFIED]; NoLiMa: GPT-4o 99,3% → 69,7% ở 32K [VERIFIED] | Recall@k, MRR (cận dưới — pooling bias) |
| 5 | Khả năng so sánh + **số học** | Cùng chỉ số/kỳ/phạm vi/ranh giới; tính đúng | **Mã tất định** | **Không** — giao cho mã | PAL (ICML 2023): mô hình + trình thông dịch 72,0 so với PaLM-540B tự tính 56,9; cùng mô hình tự "chạy" mã của nó chỉ 23,2 [VERIFIED]. Program-of-Thoughts: GPT-4 trên FinQA 58,2 → **74,0** khi giao tính toán cho mã [VERIFIED]. NumPert: GPT-4o, GPT-5 mất **56–61 điểm** khi số bị che [VERIFIED] | Tỷ lệ lỗi số học; độ đúng "được so / không được so" |
| 6 | Đọc quan hệ định tính (cặp luật không quyết được) | Kiểm chứng dựa trên tài liệu | **GLM-5.2** (chế độ đám mây, có chốt chặn) | **Không, trên mức ~7–8B chuyên biệt** | MiniCheck (EMNLP 2024): 770M **74,7** so với GPT-4 **75,3**, rẻ hơn ~446 lần [VERIFIED]; LLM-AggreFact: Bespoke-MiniCheck-7B **77,4** > GPT-4o 75,9; **Llama-3.1-405B 74,4 < 70B 75,1**; nhưng Llama-3.2-1B = 50,3 (ngang đoán mò) [VERIFIED] | Độ chính xác theo từng quan hệ (đã đăng ký ngưỡng) |
| 7 | Biết từ chối | Nhận ra ngữ cảnh không đủ | **Luật** (`corpus_completeness`) | **Không — mô hình lớn còn kém hơn ở việc này** | Joren và cs. (ICLR 2025): khi ngữ cảnh không đủ, Gemini 1.5 Pro trả lời sai **40,4%**, Claude 3.5 Sonnet 36,5%; thêm ngữ cảnh truy xuất làm Gemini giảm từ chối từ 100% xuống 18,6% [VERIFIED] | Đường risk–coverage; tỷ lệ "xác nhận sai" |
| 8 | Pháp lý theo hiệu lực | Logic thời gian, ngành áp dụng | Registry + bộ quy tắc | Không | Bài toán logic, không phải ngôn ngữ | Độ đúng ánh xạ điều khoản (Thảo chấm) |
| 9 | Kết luận, ký | Xét đoán nghề nghiệp, trách nhiệm | **Người** | — | Không phần mềm nào chịu trách nhiệm pháp lý thay kiểm toán viên | — |

**Đọc bảng:** kích thước mô hình là ràng buộc thật ở **bước 2** (nhận diện tuyên bố) và một phần **bước 3** — đúng hai bước hôm nay đang làm bằng luật. Ở bước 6, nơi GreenScan *thực sự* dùng mô hình, tài liệu cho thấy vượt khoảng 7–8B mô hình chuyên biệt đã ngang mô hình frontier. Ở bước 1, 4, 5, 7, mô hình lớn hơn **không** sửa được lỗi.

---

## 2. Thực nghiệm 10/10 — tóm tắt

Chi tiết, bảng đầy đủ, cách chạy lại: [`benchmark/size_ladder_2026-10-10/README.md`](../../benchmark/size_ladder_2026-10-10/README.md).

**Thiết kế:** 51 ca *có đáp án dựng sẵn* (kiểu kiểm thử hành vi CheckList — Ribeiro và cs., ACL 2020 [VERIFIED]: kiểm từng năng lực bằng ca biết trước đáp án, thay vì chỉ một con số accuracy). 32 ca sạch phủ 13 nhóm lỗi; 19 ca dùng **nguyên văn** ba trang thật của Hòa Phát làm bằng chứng. Mọi mô hình nhận **cùng prompt có định nghĩa nhãn** — điều kiện tốt nhất cho mô hình.

| | Bộ sạch (32) | Bộ trang thật (19) |
| --- | --- | --- |
| GreenScan (luật) | 20 · kết luận 8, đúng 6 | 7 · kết luận 3, đúng 3 |
| gemma-4-26B-A4B (~3,8B kích hoạt) | 29 | **18** |
| gemma-4-31B | **32** | 17 |
| Llama-3.3-70B | 30 | 15 |
| GLM-5.2 (753B tổng) | **32** | 17 |
| qwen3:8b trên CPU laptop (không tinh chỉnh) | 28 · **3 xác nhận sai** · 66 s/ca | 12 · **4 xác nhận sai** · 257 s/ca |

**Bốn điều thực nghiệm chứng minh:**
1. Từ cỡ ~26–31B trở lên, **không thấy kích thước làm tăng độ đúng** — trên trang thật mô hình MoE nhỏ nhất (~3,8B kích hoạt) đúng nhiều nhất.
2. **Lỗi nguy hiểm nhất của mô hình là xác nhận sai trên bảng dàn phẳng**, và nó xảy ra ở mọi cỡ, kể cả 8B → cách sửa là giữ cấu trúc bảng, không phải đổi mô hình lớn hơn.
3. **Ở đầu dưới, kích thước có ý nghĩa:** mô hình đa dụng 8B tại máy sai số học mà mô hình lớn không sai (lệch một chữ số, giảm 15% so với 20%, 98% so với 90% đều bị coi là "khớp") và chậm 1–4 phút mỗi ca → nếu muốn mô hình tại máy, phải **tinh chỉnh cho đúng việc** (Aarnes & Setty 2026: 0,6–8B tinh chỉnh vượt mô hình frontier), không dùng mô hình đa dụng.
4. **Luật của GreenScan an toàn nhưng phủ hẹp** — đây là giới hạn thật của sản phẩm hôm nay.

**Điều thực nghiệm chưa chứng minh:** độ đúng trên dữ liệu thật quy mô lớn (cần gold); khả năng tiếng Việt của GLM-5.2 nói chung (không có benchmark công khai — tra VMLU không có mục GLM [VERIFIED]); hiệu quả khi đọc cả báo cáo thay vì một cặp.

---

## 3. Sáu nguyên lý — vì sao chọn cách làm này, và mỗi nguyên lý đo bằng gì

| # | Nguyên lý | Cơ sở | GreenScan áp dụng ở đâu | Đo bằng gì |
| --- | --- | --- | --- | --- |
| N1 | **Phân rã thay vì phóng to** — kết quả tốt nhất ngày nay đến từ *hệ thống ghép* nhiều thành phần, không chỉ từ mô hình lớn hơn | Zaharia và cs., BAIR 2024 "The Shift from Models to Compound AI Systems": AlphaCode 2, AlphaGeometry (mô hình + bộ giải ký hiệu), Medprompt [VERIFIED] | Pipeline 9 bước, mỗi bước có đầu ra kiểm được | Thước đo riêng từng bước (§1) + đầu-cuối |
| N2 | **Giao tính toán cho công cụ** | PAL, Program-of-Thoughts (§1 bước 5) [VERIFIED] | Mã so số, tính lại % thay đổi, cộng lại bảng | Tỷ lệ lỗi số học = 0 trên bẫy; phép tính in ra trong lý do |
| N3 | **Kiểm chứng dựa trên tài liệu không cần mô hình lớn nhất — cần mô hình đúng việc** | MiniCheck, LLM-AggreFact (§1 bước 6); Aarnes & Setty (arXiv:2610.00689, 2026): Qwen3-**0,6B tinh chỉnh 88,44**, 8B tinh chỉnh **97,67** so với GPT-5.4 Pro **73,96** trên tuyên bố số — *"Scale matters, but fine-tuning matters more"* [VERIFIED] | Mô hình chỉ đọc cặp khó; định tuyến theo việc (`configs/routing.yaml`) | Độ chính xác theo quan hệ; chi phí/lời gọi |
| N4 | **Biểu diễn đầu vào quyết định** | ESGReveal +21,8 điểm nhờ tiền xử lý [VERIFIED]; thực nghiệm N02/N05 | Provenance tới trang; tới ô bảng là việc còn thiếu (D5) | Tỷ lệ ô bảng đúng; lỗi xác nhận sai trên bảng |
| N5 | **Biết từ chối là một năng lực cần thiết kế, không tự có khi phóng to** | Joren và cs. 2025 [VERIFIED]; EmeraldMind (arXiv:2512.11506): 94,21% đúng nhưng chỉ trả lời 25,97% ca — đánh đổi độ đúng và độ phủ [VERIFIED] | `INSUFFICIENT_EVIDENCE` do luật; chốt chặn mô hình | **Đường risk–coverage**: độ đúng theo tỷ lệ ca dám kết luận |
| N6 | **Đo trong miền, bằng dữ liệu của mình** | Climate-FEVER: bộ kiểm chứng huấn luyện trên FEVER đạt 77,69% trên FEVER nhưng **38,78%** trên tuyên bố khí hậu [VERIFIED]; VMLU: Llama-3-8B tinh chỉnh tiếng Việt 65,34 ≈ GPT-4 65,53 [VERIFIED trang xếp hạng, số do đơn vị nộp] | Gold tiếng Việt, ngưỡng đăng ký trước (`configs/measurement_decisions.yaml`) | κ, macro-F1, khoảng tin cậy theo doanh nghiệp |

---

## 4. Thước đo và cách chứng minh — từ thực nghiệm sơ bộ đến số chính thức

### 4.1 Bộ thước đo

| Tầng | Thước đo | Vì sao không chỉ dùng accuracy |
| --- | --- | --- |
| Nhận diện tuyên bố | Precision, recall, F1 theo lớp (đáng kiểm / mơ hồ / không phải tuyên bố / văn mẫu) | Hệ dựa từ khoá có thể precision cao, recall thấp |
| Truy xuất | Recall@k, MRR, Hole@k | Recall là **cận dưới** khi ứng viên gán nhãn chỉ lấy từ một bộ truy xuất |
| So sánh số | Độ đúng "được so / không được so"; tỷ lệ lỗi tính toán | Một con số đúng có thể đang so sai đại lượng |
| Kết luận | **Macro-F1** 5 lớp; ma trận nhầm lẫn; baseline lớp đa số | Dữ liệu lệch lớp: trên Hòa Phát 153/156 là "khớp một phần" |
| An toàn | **Tỷ lệ xác nhận sai**, **tỷ lệ mâu thuẫn sai** — báo riêng | Hai lỗi này có giá khác nhau với kiểm toán viên |
| Độ phủ | **Đường risk–coverage**; độ đúng trên phần dám kết luận | Một hệ không kết luận gì có "0 lỗi" nhưng vô dụng |
| Chi phí | Giây/lời gọi, token, đồng/bộ hồ sơ, tài liệu có rời máy | Tiêu chí triển khai (15% điểm vòng 2) |

### 4.2 Thống kê

- **Khoảng tin cậy Wilson** cho mọi tỷ lệ; với n = 60–100 khoảng tin cậy ±8–11 điểm ([05 §4](../08-knowledge/05_AI_NLP_VA_DO_LUONG.md)).
- **So sánh cặp** hai hệ trên cùng ca: **McNemar chính xác** (đã dùng trong thực nghiệm); trên gold: **bootstrap theo doanh nghiệp**.
- **Ngưỡng đăng ký trước** (đã có từ 29/09): ví dụ mô hình chỉ được tự kết luận "bị bác bỏ" khi độ chính xác ≥ 0,90, cận dưới khoảng tin cậy ≥ 0,75, n ≥ 10.
- Khác biệt không có ý nghĩa thống kê thì nói **"không phát hiện được khác biệt"**, không nói "bằng nhau".

### 4.3 Ba thí nghiệm tiếp theo để chứng minh chính thức

| # | Thí nghiệm | Trả lời câu hỏi | Cần gì | Khi nào |
| --- | --- | --- | --- | --- |
| E1 | **Mở rộng bộ ca dựng sẵn lên ≥ 100**, Quỳnh/Thảo viết thêm ca *không nhìn đầu ra hệ thống* và gán lại độc lập 51 ca hiện có (κ) | Kết quả 10/10 có đứng vững khi người khác dựng đề? | 2 buổi × 2 giờ | trước 20/10 |
| E2 | **Cùng thang mô hình trên gold** (cặp thật, ứng viên gộp từ mọi bộ truy xuất): luật · mô hình có chốt chặn · mô hình tự quyết · **lai** (mô hình đọc, mã kiểm số, bất đồng → người) | Cấu hình nào tốt nhất theo risk–coverage trên dữ liệu thật? | Gold ≥ 60 cặp | khi gold về |
| E3 | **Bảng có cấu trúc**: cùng ca bảng dàn phẳng, đưa bảng dạng hàng–cột (Markdown/JSON) cho mô hình | Lỗi N02/N05 có biến mất khi giữ cấu trúc? — kiểm trực tiếp nguyên lý N4 | Trích bảng giữ ô | sau 25/10 |

---

## 5. Thầy nói đúng ở đâu — và việc phải sửa

| # | Phát hiện | Mức | Việc |
| --- | --- | --- | --- |
| 1 | **Cổng so sánh có hai lỗ hổng**: cường độ giảm 5% đem so với tổng giảm 5% → *xác nhận sai* (F11); công ty mẹ đem so với hợp nhất → *mâu thuẫn sai* (F20). Đây đúng là tính năng nhóm đang giới thiệu là điểm mạnh nhất | 🔴 | Thêm hai bẫy `xfail(strict)` ngay; sửa và chạy lại 47 bẫy + 4 ca thật + Hòa Phát |
| 2 | **Ngưỡng 0,35 giấu chênh lệch 9–25%** cùng chỉ số, cùng kỳ (833.876 so với 933.876 ra "khớp một phần" với lý do không nhắc chênh lệch) | 🟠 | Giữ quyết định chưa gọi "bị bác bỏ" tới khi quét ngưỡng trên gold, nhưng **ghi rõ chênh lệch và phép tính vào lý do** và đưa mục lên đầu hàng đợi |
| 3 | **Bộ trích bỏ sót** câu định lượng không có động từ "giảm/tiết kiệm" ("sử dụng 15 triệu m3 nước", "đáp ứng 90% nhu cầu điện", "tái sử dụng 98% nước") | 🟠 | Đo recall (lấy mẫu câu không được trích); thử bộ phân loại tuyên bố nhỏ tinh chỉnh (bước 2, §1) |
| 4 | **Không cộng thành phần để kiểm tổng của tuyên bố** (F26, F27) — dù đã cộng lại bảng trong thủ tục số liệu công bố | 🟡 | Nối thủ tục cộng lại bảng vào phép kiểm tuyên bố |
| 5 | **Bảng mất cấu trúc** làm mọi mô hình xác nhận sai | 🟠 | Trích bảng giữ ô (D5); giữ chốt chặn: mô hình không được tự "xác nhận" từ đoạn là bảng dàn phẳng |

**Về chưng cất mô hình nhỏ:** tài liệu ủng hộ hướng này *về lâu dài* — Aarnes & Setty 2026: mô hình 0,6–8B tinh chỉnh vượt GPT-5.4 Pro trên kiểm chứng tuyên bố số. Nhưng điều kiện là **dữ liệu có nhãn đúng trong miền** (gold + ca dựng sẵn) và GPU để huấn luyện; làm trước khi có nhãn là chép lại lỗi của mô hình thầy (xem 28/09: GLM-5.2 tự quyết tạo 10 mâu thuẫn sai). Thứ tự: E1 → E2 → nếu mô hình lớn đạt ngưỡng, chưng cất vào bộ phân loại < 1B chạy CPU.

---

## 6. Trả lời thầy — 90 giây

> "Em cảm ơn thầy — nhận xét này giúp nhóm đo lại và tìm ra lỗi thật. Có ba ý ạ.
> **Thứ nhất,** sản phẩm không dựa vào một mô hình bé: chế độ ngoại tuyến không dùng mô hình ngôn ngữ, còn chế độ đám mây dùng GLM-5.2 với khoảng 750 tỷ tham số.
> **Thứ hai,** nhóm đã thử đúng câu hỏi của thầy: cho cùng 51 ca có đáp án biết trước đi qua các mô hình từ loại chỉ kích hoạt khoảng 4 tỷ tham số mỗi lượt tới GLM-5.2 khoảng 750 tỷ tham số. Từ cỡ khoảng 30 tỷ trở lên không thấy mô hình lớn hơn làm tốt hơn; khi bằng chứng là bảng bị mất cấu trúc, mô hình lớn nhất cũng xác nhận sai đúng chỗ mô hình nhỏ sai. Thầy đúng ở đầu dưới: mô hình 8B đa dụng chạy trên laptop sai số học và xác nhận sai nhiều nhất — đó là lý do ở chế độ ngoại tuyến chúng em để mã quyết định, không để mô hình nhỏ quyết định. Tài liệu cũng cho kết quả tương tự: bộ kiểm chứng 770 triệu tham số ngang GPT-4, mô hình 405B không hơn 70B trên kiểm chứng dựa tài liệu.
> **Thứ ba,** chỗ thầy lo là có thật nhưng nằm ở chỗ khác: bộ luật của nhóm phủ hẹp — đúng 20/32 ca so với 32/32 của mô hình — vì bộ trích bỏ sót tuyên bố và cổng so sánh còn hai lỗ hổng. Nhóm sửa bằng cách cho mô hình đọc để tăng độ phủ, giữ mã để kiểm số và cấu trúc, chỗ nào hai bên bất đồng thì chuyển người — và chỉ công bố con số khi bộ gán nhãn đạt ngưỡng đã đăng ký trước."

**Không nói:** "LLM không làm được số học" — trong thực nghiệm sạch các mô hình tính đúng; điều tài liệu chứng minh là chúng **dễ vỡ khi số bị nhiễu hoặc bị che** (NumPert) và khi đầu vào mất cấu trúc. **Không nói:** "luật của nhóm chính xác hơn mô hình" — chỉ đúng khi luật đã dám kết luận, và nó dám quá ít.

---

## 7. Nguồn (đã kiểm 10/10/2026)

| Nguồn | Nhãn |
| --- | --- |
| zai-org/GLM-5.2, model card + config (huggingface.co/zai-org/GLM-5.2); GLM-5-Team, arXiv:2602.15763 | VERIFIED |
| FPT AI Marketplace `GET /v1/models`: `GLM-5.2`, ngữ cảnh 1.000.000, US$1,40/4,40 mỗi 1M token; **vùng xử lý không ghi** trong danh mục | VERIFIED (vùng VN trong `routing.yaml` chưa kiểm lại được) |
| Tang, Laban, Durrett, *MiniCheck*, EMNLP 2024, arXiv:2404.10774; bảng xếp hạng LLM-AggreFact (llm-aggrefact.github.io, trung bình tự tính từ 11 bộ) | VERIFIED |
| Aarnes & Setty, *NumPert*, IJCNLP-AACL 2025 SRW, arXiv:2511.09971; *Towards Robust Numerical Claim Verification*, arXiv:2610.00689 (2026) | VERIFIED |
| Chen và cs., *FinQA*, EMNLP 2021 (22,78% là FinQANet-RoBERTa, **không phải LLM**); Zhao và cs., *FinDVer*, EMNLP 2024 | VERIFIED |
| Gao và cs., *PAL*, ICML 2023; Chen và cs., *Program of Thoughts*, TMLR 2023 | VERIFIED |
| Liu và cs., *Lost in the Middle*, TACL 2024; Hsieh và cs., *RULER*, COLM 2024; Modarressi và cs., *NoLiMa*, ICML 2025 | VERIFIED |
| Joren và cs., *Sufficient Context*, ICLR 2025, arXiv:2411.06037 | VERIFIED |
| Stammbach và cs., *Environmental Claim Detection*, ACL 2023; Diggelmann và cs., *Climate-FEVER*, 2020; Webersinke và cs., *ClimateBERT*, 2021 | VERIFIED |
| Bucher & Martini, arXiv:2406.08660 (2024, chưa bình duyệt) | VERIFIED — preprint |
| Zaharia và cs., BAIR Blog 18/02/2024 | VERIFIED |
| Ribeiro và cs., *CheckList*, ACL 2020 | VERIFIED |
| Zou và cs., *ESGReveal*, arXiv:2312.17264; Saad và cs., arXiv:2609.15242 (chỉ tóm tắt: 7 mô hình 2–30B, không thấy xu hướng theo kích thước); EmeraldMind, arXiv:2512.11506 | VERIFIED |
| VMLU leaderboard (vmlu.ai) — không có mục GLM | VERIFIED (số do đơn vị tự nộp) |
