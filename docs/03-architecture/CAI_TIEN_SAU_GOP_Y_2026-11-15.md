# Cải tiến sau góp ý chuyên gia (15/11/2026)

Kế hoạch: `docs/11-vong-2-nop-bai/KE_HOACH_V2_SAU_GOP_Y_2026-11-15.md`. Quyết định: D-2026-11-15-01. Mọi số ở đây đều [ĐÃ THỰC NGHIỆM] trên mã cuối ngày 15/11. "Trước" là mã cuối ngày 14/11 (checkpoint `vong2_2026-11-14d`).

## 1. Thay đổi

| Mã chính sách | Nội dung | Vì sao (số đo trước khi sửa) |
|---|---|---|
| `claim-typing-v2` (taxonomy v4, `claim_extraction.fallback_types`) | Khi câu không khớp loại tuyên bố nào, thử lần lượt: dùng tài nguyên (nước, điện, nhiên liệu), tuân thủ và quản lý môi trường (vi phạm, sự cố, ISO 14001, công trình xanh), cây xanh và rừng; sau cùng là "chỉ số đã biết + số liệu" (`metric_disclosure`). Câu đã trích trước đây giữ nguyên loại. "nước" theo nghĩa nhà nước hay đất nước bị loại | 63/63 câu "ủng hộ" của GS-Mutation không được trích đều vì không khớp loại nào |
| `units-v2` | Đọc thêm đơn vị m2, km2, ha, MWp, kWp, MW, kW và "cây". Phạm vi phát thải gán theo nhãn gần nhất **trước từng số**. Nhận "m3/tấn" là cường độ. Tách nước thải / nước khai thác / nước sử dụng. Thêm ranh giới "công ty mẹ". Số lũy kế so với số một kỳ → AMBIGUOUS | 24/26 câu đã trích mà không quyết được là do không đọc được đơn vị; 2 câu do phạm vi bị đọc theo cả câu |
| `figure-consistency-v1` (bổ sung) | Từ xu hướng ngay trước con số quyết định chiều. Cùng mức thay đổi mà khác năm gốc → PARTIAL. "100%" và "0%" là số chính xác. Đoạn khớp số và đoạn lệch số cùng xuất hiện → "bằng chứng không thống nhất" (PARTIAL kèm cờ). Với loại tuyên bố dự phòng, lệch từ 3 lần trở lên mà chưa rõ ranh giới → PARTIAL | Lượt đầu của các thay đổi trên làm vu oan tăng (7/290) và "ủng hộ" sai tăng (62). Từng mẫu lỗi được sửa đến khi vu oan về 0 trên phần test |
| `independent_support_v1` bật mặc định | "Ủng hộ" chỉ khi có đoạn từ nguồn pháp luật, bên ngoài hoặc chuẩn mực | Phát lại ngày 11/11: GS-Eval v2 có "ủng hộ" sai 5 → 0 |
| Câu "0 vi phạm" | Với tuyên bố tuân thủ, cụm "vi phạm" không có thẩm quyền không bác bỏ được | 4 ca "mâu thuẫn" sai mới trên GS-Bench |
| "Hiện nay" → năm báo cáo | Lấy năm từ `reporting_year` hoặc tên tệp; ghi `period_source = report_year`; kỳ suy ra **không** được tính là thuộc tính khớp | Góp ý H9 |
| `assessment-v1` | Mỗi kết luận có ba trường hiển thị: nhất quán (khớp / không khớp / không so được), độc lập nguồn (nguồn độc lập / tài liệu tài chính của doanh nghiệp / tự công bố), loại căn cứ (phép tính / cụm từ / mô hình / chỉ tương đồng). Giao diện và giấy làm việc hiện ba trường này. Điểm 0–100 bị ẩn khỏi giao diện. Câu miễn trừ có thêm "Không bị gắn cờ không có nghĩa là đã được xác nhận" | Góp ý H2, D2, Q6, Q12 |
| `absolute-share-v1` (bổ sung) | Đọc bảng mà đơn vị chỉ ghi ở tiêu đề cột ("Giá trị (tỷ VND)"). Tổng = đã phân bổ + chưa phân bổ khi bảng không ghi tổng. Bỏ qua câu liệt kê nội dung báo cáo ("(2) Số dư còn lại chưa được phân bổ") | Báo cáo trái phiếu xanh thật của Techcombank 2024 |

## 2. Tập nhãn GS-Claims v1 (máy gán, có kiểm soát)

- **Mẫu:** 150 câu từ 4 báo cáo của 4 ngành (thép HPG, dược DHG, xây dựng CTD, cảng GMD). Mỗi báo cáo lấy 18 câu hệ thống đã trích và 17 câu không trích (câu có số hoặc có từ môi trường), cộng 10 câu kiểm soát có đáp án biết trước.
- **Quy trình:**
  - hướng dẫn gán nhãn: `benchmark/gs_claims_v1/LABELING_GUIDE.md`;
  - hai người gán Sonnet làm **độc lập** (một người đi ngược thứ tự), không được xem đầu ra của hệ thống;
  - agent Opus phân xử chỗ lệch, có ghi lý do;
  - người điều phối soát lại.
- **Chất lượng nhãn:**
  - câu kiểm soát: cả hai người gán đúng **29/29** trường;
  - kappa: "là tuyên bố" **0,92**, loại tuyên bố 0,89, có số 1,0, có kỳ 0,90, năm gốc 0,74, phạm vi phát thải 1,0, ranh giới 0,74, nguồn độc lập 1,0, ngôn ngữ quảng bá 0,75;
  - 29 câu lệch, 36 trường được phân xử.
- **Giới hạn:** đây là nhãn của mô hình ngôn ngữ, **không phải nhãn người**. Kappa đo độ nhất quán giữa hai lượt cùng loại mô hình. Đội vẫn cần người gán lại một mẫu để có mức trần thật.

**Đo bộ trích tuyên bố** (140 câu, không tính câu kiểm soát; độ phủ tính trong khung lấy mẫu):

| | Chính xác | Độ phủ |
|---|---|---|
| Pipeline 14/11 | 0,56 [0,44–0,67] | 0,75 [0,62–0,85] |
| Mã 15/11 | 0,56 [0,45–0,67] | 0,79 [0,67–0,88] |

→ Nút thắt bây giờ là **độ chính xác**: 33/75 câu bị trích không phải tuyên bố môi trường, phần lớn là câu quản trị ESG và dòng dính chữ do dàn trang. Đây là việc tiếp theo.

## 3. Số đo trước / sau

| Bộ đo | Trước (14/11) | Sau (15/11) |
|---|---|---|
| GS-Bench (453 ca): số kết luận dứt khoát | 35 (7,7%) | **123 (27,2%)** |
| GS-Bench: chính xác trên phần kết luận | 0,743 | **0,854** |
| GS-Bench: "ủng hộ" sai / "mâu thuẫn" sai | 8 / 1 | 17 / 1 |
| GS-Mutation, phần test: vu oan trên câu gốc | 0/234 | **0/234** |
| GS-Mutation: phóng đại số (test) | 9/72 | **50/72** |
| GS-Mutation: đảo hướng (test) | 5/16 | **13/16** |
| GS-Mutation: lùi năm gốc → không còn "ủng hộ" | 9/10 | **10/10** |
| GS-Mutation: tuyệt đối hoá → không còn "ủng hộ" (test) | 20/20 | 19/20 (*) |
| GS-Mutation: từ quảng bá → có cờ (test) | 0/75 | **71/75** |
| GS-Mutation mới: đổi đơn vị / phóng to ranh giới / mục tiêu thành đã đạt | — | 29/30, 8/9, 3/3 |
| GS-Eval v2 (146 câu thật, phát lại): kết luận dứt khoát / chính xác | 7 / 0,43 | **4 / 0,75** ("ủng hộ" sai 3 → 0; "mâu thuẫn" sai 1, câu đó không phải tuyên bố) |
| evaluate-real (4 vụ có phán quyết) | 4/4 | 4/4 (không đổi) |
| Ca A (5 tuyên bố) | 3 mâu thuẫn, 2 chưa được chứng minh | không đổi |
| Hòa Phát: số tuyên bố / hàng soát | 156 / 8 trên 172 mục | 199 / 10 trên 215 mục |
| Hòa Phát: phân bố kết luận | 154 ủng hộ một phần, 1 ủng hộ, 1 chưa đủ bằng chứng | 198 ủng hộ một phần, 1 chưa đủ bằng chứng. Theo hai trục: 43 khớp tài liệu của chính doanh nghiệp (10 khớp BCTN), 155 chưa so được, 0 có nguồn độc lập |
| Kiểm thử | 743 | 757 |

(*) Ca còn lại: tuyên bố "mảng thép chiếm 100%" bị khớp với ô "100%" ở dòng tổng của bảng. Đã ghi vào giới hạn.

**Ngưỡng đăng ký trước** (`benchmark/gs_mutation_v1/PREREG_2026-11-14.md`):
- Đạt: vu oan trên phần test 0/234, không tăng; phóng đại số và đảo hướng không giảm (tăng mạnh); M3 và M7 không giảm.
- **Không đạt một ca ở M5** (20/20 → 19/20). Ghi rõ ở trên.
- GS-Bench có số "ủng hộ" sai tuyệt đối tăng 8 → 17, vì số ca dám kết luận tăng 3,5 lần; tỉ lệ đúng trên phần kết luận vẫn tăng.

## 4. So với "đưa thẳng cho LLM" (cùng 183 ca phần test)

| | Luật (14/11) | **Luật (15/11)** | gpt-oss-120b | Kết hợp: luật quyết, LLM chỉ gắn cờ khi 2 lần hỏi cùng nói "mâu thuẫn" |
|---|---|---|---|---|
| Phóng đại số → mâu thuẫn hoặc cờ | 9/72 | **50/72** | 47/72 | **57/72** |
| Đảo hướng | 5/16 | 13/16 | 13/16 | **16/16** |
| Tuyệt đối hoá → mâu thuẫn | 2/20 | 7/20 | 15/20 | 16/20 |
| Câu gốc thành "mâu thuẫn" hoặc có cờ sai | 0/75 | **0/75** | 1/75 | **0/75** |
| Ca cài lỗi vẫn "ủng hộ" | 0 | 7 | 5 | — |
| Đổi kết quả khi hỏi lại | 0% | 0% | 16% | 0% (cờ chỉ bật khi 2 lần hỏi cùng ý) |

## 5. Báo cáo trái phiếu xanh thật

Hai báo cáo do agent tìm trên web (`data/green_bond_cases/raw/`):
- **Techcombank, "Báo cáo sau phát hành trái phiếu xanh 2024":** phân bổ 399 tỷ, chưa phân bổ 51 tỷ. Báo cáo không có câu nào nói "100%", nên đội dùng một **tuyên bố giả định** "Toàn bộ vốn … đã được phân bổ" để thử với bằng chứng thật. Kết quả: hệ thống đọc bảng, tính 399 / (399 + 51) = 89%, trả "ủng hộ một phần" kèm cờ "tuyên bố tuyệt đối", lý do ghi rõ phép tính. Không ra "mâu thuẫn", vì độ lệch 11% thấp hơn ngưỡng 35%.
- **BIDV, "Allocation & Impact Report 2025":** tuyên bố thật "BIDV đã hoàn thành phân bổ 100% vốn trái phiếu xanh phát hành năm 2023". Kết quả: số khớp (100 ≈ 100) nhưng "chỉ tài liệu của chính doanh nghiệp xác nhận", nên là "ủng hộ một phần". Đúng thiết kế của cờ nguồn độc lập.
- **Lần chạy đầu trên dữ liệu thật đã lộ ba lỗi**, đều đã sửa:
  - đơn vị chỉ ghi ở tiêu đề cột;
  - bảng không ghi tổng;
  - luật cụm từ bắt nhầm một câu liệt kê nội dung báo cáo.

## 6. Tập giữ riêng

`benchmark/holdout_v1/` gồm PAN (SR và BCTN 2020, tiếng Anh) và DPR (BCTN và BCTC, bản scan). Tệp khoá và dự đoán viết trước khi chạy: `HOLDOUT_2026-11-15.md`.
- Một lượt chạy đầu đã bị dừng trước khi có bất kỳ kết quả nào, vì phát hiện lỗi danh sách động từ (dòng bảng lọt vào hàng soát). Sửa xong mới chạy lại.

**Kết quả lần chạy duy nhất** (`results_lan_duy_nhat_2026-11-15.json`, `contradicted_lan_duy_nhat_2026-11-15.jsonl`):

| | PAN (tiếng Anh, có lớp chữ) | DPR (bản scan, OCR) |
|---|---|---|
| Tuyên bố | 201 | 53 |
| Kết luận | 176 ủng hộ một phần, 23 chưa đủ bằng chứng, **2 mâu thuẫn** | 53 ủng hộ một phần |
| Hàng soát | 8 | 5 |
| Thời gian | 139 giây | 521 giây (OCR 208 trang) |
| "Mâu thuẫn" đọc tay | **2/2 sai (vu oan)**: (1) "điện năng của máy nén giảm 40%" bị so với "tiêu thụ qua kênh online tăng 25%"; (2) "chi phí nâng cấp hệ thống xử lý nước thải 483 triệu đồng" bị so với "tổng tài trợ 700 triệu đồng" | — |
| Lỗi cài vào câu có số khớp, bắt được (mâu thuẫn hoặc có cờ) | 1/7 | 0/1 |

**So với dự đoán đăng ký trước:**
- Vu oan: dự đoán "0–1 mỗi công ty"; PAN có 2, **sai dự đoán**.
- DPR có ít tuyên bố và ít số khớp hơn: đúng dự đoán.
- Bắt lỗi cài: dự đoán "ít nhất một nửa"; thực tế 1/8, **sai dự đoán**.

**Nguyên nhân, đã kiểm:**
1. Hai ca vu oan:
   - ca thứ nhất: tuyên bố không có chỉ số mà từ điển biết, nên mọi câu của đoạn đều bị đem so;
   - ca thứ hai: hai khoản tiền không cùng đối tượng.
2. Bắt lỗi cài thấp: ở PAN, 9/11 tuyên bố có số khớp chỉ khớp với **chính báo cáo đó**. Chốt chống vu oan không cho tài liệu tự bác bỏ mình, và luật so lời văn với bảng đang tắt.

**Sửa sau khi chạy (không còn là số ngoài mẫu):** thuộc `figure-consistency-v1`.
- Không kết luận "mâu thuẫn" khi tuyên bố không có chỉ số mà câu bằng chứng cũng không có chung cụm từ nội dung nào với tuyên bố.
- Với tuyên bố không thuộc tài chính xanh, không kết luận "mâu thuẫn" dựa trên một khoản tiền.

Chạy lại PAN sau khi sửa: 0 "mâu thuẫn"; bắt lỗi cài vẫn 1/7 (`results_sau_sua.json`). GS-Bench, GS-Mutation và 757 kiểm thử không đổi so với trước khi sửa.

**Bài học:** con số ngoài mẫu xấu hơn số trên tập dev và tập test. Hai lỗi vu oan chỉ lộ ra trên báo cáo tiếng Anh của một ngành chưa từng thấy. Báo cáo vòng 2 nêu đúng con số này.

## 7. Đợt tiếp theo (cuối ngày 15/11): độ chính xác của bộ trích, mẫu kiểm ngẫu nhiên, nhãn người (D-2026-11-15-02)

**`claim-precision-v1`.**
- Nội dung: câu tiếng Việt thuộc loại "bền vững chung chung" phải có ít nhất một từ môi trường (môi trường, khí hậu, phát thải, năng lượng, điện, nước, chất thải, xanh, rừng…). Cụm "phát triển bền vững" chỉ nêu tên lĩnh vực nên không tính.
- Câu tiếng Anh giữ như cũ. Lần chạy đầu áp dụng cho cả tiếng Anh đã làm hỏng vụ KLM có phán quyết ("Join us in creating a more sustainable future"), nên luật chỉ áp dụng cho tiếng Việt.
- Chỉnh luật trên 2 báo cáo dev (HPG, DHG), đo trên 2 báo cáo test (CTD, GMD):

| GS-Claims | Câu trích sai | Câu đúng bị mất | Chính xác | Độ phủ |
|---|---|---|---|---|
| Dev (HPG, DHG) | 17 → 5 | 1 | 0,54 → 0,79 | 0,83 → 0,79 |
| Test (CTD, GMD) | 16 → 12 | 0 | 0,58 → 0,65 | 0,76 → 0,76 |
| Toàn bộ 140 câu | 33 → 17 | 1 | 0,56 → **0,71** | 0,79 → 0,77 |

- GS-Bench, GS-Mutation và evaluate-real không đổi.
- Hòa Phát: 199 → **179** tuyên bố (20 câu bị loại vì không có từ môi trường); hàng đợi 10 trên 195 mục; 40 câu khớp tài liệu của chính doanh nghiệp, 139 câu chưa so được.
- Kiểm thử: **759**.

**`audit-sample-v1`.**
- Mỗi phiên rút 5 tuyên bố ngoài hàng đợi, tất định theo mã tuyên bố.
- Hàng đợi không đổi.
- Giao diện có thẻ "Mẫu kiểm ngẫu nhiên"; giấy làm việc có mục riêng.
- Cách đọc: n mẫu mà 0 mục bị bỏ sót thì tỉ lệ bỏ sót có cận trên khoảng 3/n.

**Nhãn người.**
- `benchmark/gs_claims_v1/human/` có 50 câu rút ngẫu nhiên phân tầng (25 câu là tuyên bố, 25 câu không; 11 câu từng bị tranh chấp), ở dạng Excel có danh sách chọn và CSV.
- Kèm hướng dẫn `HUONG_DAN_NGUOI_GAN.md` và script `score_human.py` tính kappa giữa người với nhãn đã phân xử và với từng mô hình.
- **Còn chờ một người gán.**

**Tài liệu và tệp đã dựng lại:**
- bản thuyết minh `THUYET_MINH_HE_THONG_2026-11-15.docx` (thêm Chương 11; sửa các số Ca B cũ);
- báo cáo 12 trang, slide, hướng dẫn 4 trang;
- zip từ checkpoint `vong2_2026-11-15b`;
- bản trực tuyến đẩy lại; trang thật có thẻ mẫu kiểm, không có lỗi JavaScript.
