# R1: Thể lệ, tiêu chí chấm, hồ sơ dự thi, bộ hỏi đáp cũ

*Lập 04/11/2026 cho Chung kết 10/11/2026 (10 phút trình bày + 8 phút hỏi đáp). Viết tắt: `REPO` = `D:\Sinh viên CNhan\AI quantum\docs\greenscan-ai\GreenScan-AI`; `TXT` = `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt`. "Số mới" = `REPO\docs\00-project\KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` §2 và §10 (31/10–01/11).*

*Nguồn đã đọc:*
- `TXT\the_le_cuoc_thi.txt` (OCR 14 trang), đọc hết. Bảng tiêu chí Vòng 3 bị nhiễu nên đã đối chiếu ảnh trang 10–11 của `REPO\docs\Thể lệ Cuộc thi Trí tuệ nhân tạo và Lượng tử trong Kinh tế - Tài chính - Kế toán lần thứ I, năm 2026.pdf` (ảnh: `...\scratchpad\R1\the_le_p11.png`, `the_le_p10_right.png`).
- `TXT\AI-QUANTUM_AGENT_CRITERIA_v1.txt`, `TXT\AI-Q2026.txt` (kịch bản thuyết trình cũ), `TXT\ho_so_vong1.txt` (kể cả các bảng bị dồn xuống cuối tệp), `TXT\ho_so_nguyen_ly_hoi_dong.txt` (14/10, 15 trang): đọc hết.
- `REPO\docs\07-presentation\ban-ket-2026-10-25\README.md`, `01_NOI_DUNG_TRINH_BAY.md`, `04_HOI_DAP_BO_SUNG.md`: đọc hết. `03_KICH_BAN_PROTOTYPE_DEMO.md`: chỉ grep (gói nộp, Docker, OCR).
- `REPO\docs\07-presentation\QA_DRILL.md`: đọc hết. `QA_BANK_100_2026-09-20.md`: đọc quy tắc, danh sách 100 câu, bảng "đừng nói" và các câu Q15, Q48, Q53–Q57, Q62–Q64, Q74–Q80, Q86–Q87.
- `TXT\GreenScan_100_Cau_BGK.txt`: là bản xuất DOCX của chính `QA_BANK_100_2026-09-20.md` (cùng tiêu đề, cùng ngày lập 20/09, cùng Q1–Q100), nên không đọc lại phần trùng.
- Đối chiếu thêm: "Số mới" §0–2, §10–11; `REPO\docs\00-project\AUDIT_HE_THONG_2026-10.md` §0–1, §10; `REPO\docs\00-project\ARCHITECTURE_INVARIANTS.md`; `REPO\docs\04-data-ai\MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md` §0; `REPO\docs\08-knowledge\02_PHAP_LY_VIET_NAM.md` (grep ngày hiệu lực); mã `REPO\src\quantum_gw\verification\numeric_facts.py` và `irlib.py` (cổng so sánh); đếm test bằng `pytest --collect-only` ngày 04/11; grep toàn repo tìm mã lượng tử.

*Phần không đọc được và vì sao:*
- Repo **không có biên bản câu hỏi thật** của BGK ở buổi phỏng vấn Vòng 1 (09/08) và Bán kết (25/10). Việc "ghi mọi câu hỏi BGK vào QA_BANK" trong `ROUND2_READINESS_2026-09-22.md` §9.2 chưa được làm. Câu hỏi thật duy nhất có ghi là nhận xét của một giảng viên ngày 10/10 (mục 1.10). **Việc cho đội: ba người viết lại từ trí nhớ các câu BGK đã hỏi ngày 25/10, xong trước 07/11.**
- `ho_so_vong1.txt` là bản nháp: mục 3.1 "Khảo sát sơ bộ" còn bảng trống và dòng "[LƯU Ý NỘI BỘ – XÓA DÒNG NÀY TRƯỚC KHI NỘP]". Không rõ bản đã nộp có mục này hay không [CHƯA XÁC MINH].
- Không rõ "Hồ sơ nguyên lý cho Hội đồng" (14/10) đã được gửi cho BGK hay chưa [CHƯA XÁC MINH]. Nếu đã gửi thì BGK biết các lời hứa "trước Chung kết" ở §4.2 của hồ sơ này (mục 5.2).
- `02_KICH_BAN_SINH_ANH.md`: không đọc, vì đây là prompt sinh ảnh, không có luận điểm chuyên môn.
- Repo không ghi kết quả hay nhận xét của Bán kết.

**Kết luận nhanh (đọc trước khi tập):**
1. Vòng 3 chấm sáu tiêu chí: Giải quyết bài toán 20 · Kỹ thuật và dữ liệu 15 · Sản phẩm và demo 20 · Khả thi triển khai 20 · Xã hội và đạo đức 10 · Trình bày và phản biện 15. Ba tiêu chí 20% chiếm 60% điểm, và GreenScan yếu ở hai trong số đó: **chưa có số đo lợi ích so với làm tay** (TC1, Điều 6.5) và **chưa có đối tác hay pilot** (TC4).
2. TC1 chấm việc giải quyết "bài toán thực tế **đặt ra ở vòng đầu**". BGK sẽ đối chiếu với phát biểu bài toán và các ngưỡng trong hồ sơ Vòng 1: gold 100 cặp, κ ≥ 0,7, F1 ≥ 0,75, Recall@10 ≥ 0,85, verdict ≥ 0,80, rule pack QĐ 21. Hầu hết chưa đo hoặc chưa làm, nên đội phải chủ động đưa bảng "Hứa → Đạt → Chưa đạt, vì sao" (mục 5.2).
3. Thể lệ thưởng sự trung thực. TC6 ghi rõ "trung thực về giới hạn của sản phẩm"; Điều 10 nói mô hình đơn giản chạy ổn định được điểm cao hơn mô hình phức tạp. Đây là lợi thế của GreenScan nếu đội nói đúng số.
4. Số 31/10–01/11 làm nhiều câu trả lời cũ thành sai:
   - "không có hiệu ứng quy mô": sai ở độ phủ;
   - "luật gần như không bao giờ xác nhận sai": luật có 8–9 SUPPORTED sai trên GS-Bench v1.1;
   - "chế độ đám mây GLM-5.2": khoá FPT trả lỗi 401 từ 31/10;
   - "359/385 test": nay là 410.
5. Lượng tử: repo **không có dòng mã nào** (đã kiểm 04/11). Không nên tranh giải Lượng tử. Nói đúng: "QUBO đã hình thức hoá, chưa chạy".

---

## 1. Tóm tắt từng tài liệu

### 1.1 Thể lệ (Kế hoạch 567/KH-HVTC; bản OCR đọc thành "56#")
- **Là gì:** thể lệ chính thức, 8 chương, 18 điều.
- **Điểm chính:**
  - **Nguyên tắc (Điều 1.2, 10):**
    - Lấy bài toán thực tiễn làm trung tâm; đội tự đề xuất bài toán, dữ liệu và giải pháp.
    - Ưu tiên bài có bài toán rõ, dữ liệu phù hợp, giải pháp hợp lý, sản phẩm vận hành được và giá trị thực tiễn.
    - "Việc sử dụng công nghệ phức tạp hoặc mới không phải là tiêu chí tự thân".
    - "Một mô hình AI đơn giản nhưng chạy ổn định … sẽ có điểm cao hơn một mô hình phức tạp nhưng không thể triển khai" (tr.6).
  - **Sản phẩm (Điều 6):**
    - 6.5: phải chỉ ra cải thiện hiệu suất, độ chính xác, chi phí hoặc giảm rủi ro **so với phương pháp truyền thống**.
    - 6.6: mã nguồn nén zip, kèm hướng dẫn cài đặt.
    - 6.8: dữ liệu có bản quyền thì phải xuất trình giấy phép.
  - **Vòng 3 (Điều 8.3):**
    - 10/11/2026 (thứ Ba), hội trường HT 700, 6 đội.
    - Mỗi đội có khu trưng bày hoặc demo; pitching trên sân khấu trước BGK và nhà đầu tư.
    - Tối đa 10 phút trình bày và 08 phút hỏi đáp; BTC có thể điều chỉnh.
  - **BGK (Điều 9):**
    - Gồm giảng viên HVTC và các trường, chuyên gia AI và lượng tử, lãnh đạo doanh nghiệp, nhà đầu tư, quỹ đầu tư mạo hiểm.
    - **Có quyền yêu cầu bằng chứng về dữ liệu hoặc mã nguồn.**
  - **Chấm điểm (Điều 10):**
    - Mỗi tiêu chí chấm 0–100 theo bốn mức: dưới 40 Yếu; 40 đến dưới 70 Trung bình; 70 đến dưới 90 Tốt; 90–100 Xuất sắc.
    - Điểm tiêu chí = điểm trung bình các giám khảo × trọng số; điểm đội = tổng các tiêu chí.
    - Hai giám khảo lệch nhau hơn 30 điểm trên cùng tiêu chí thì Trưởng BGK tổ chức thảo luận.
  - **Giải (Điều 12):**
    - Nhất 70 triệu kèm cúp và cơ hội ươm tạo; 2 giải Nhì 30 triệu; 3 giải Ba 15 triệu; 5 giải Khuyến khích 5 triệu.
    - Giải phụ: Ứng dụng Lượng tử xuất sắc 15 triệu; Best Pitch 5 triệu (Chung kết); Lan toả cộng đồng 5 triệu.
  - **Điều 14:**
    - Cấm dùng AI tạo sinh tạo toàn bộ bài thi mà không có cải tiến đáng kể của người hoặc không giải thích được.
    - Dùng AI hỗ trợ được phép nhưng **phải khai báo rõ trong tài liệu**.
    - Cấm cố ý làm sai lệch dữ liệu hoặc kết quả.
  - **Điều 16:**
    - Sản phẩm đạt giải, **nếu được chọn để phát triển, thuộc sở hữu của HVTC**.
    - BTC được dùng hình ảnh và sản phẩm cho truyền thông.
    - Đội giải Nhất, Nhì có thể được đề nghị nộp báo cáo chi tiết về dữ liệu và phương pháp.
- **Tiêu chí ba vòng (trọng số %; đã đối chiếu ảnh trang PDF):**

| Vòng | Tiêu chí (trọng số) |
|---|---|
| V1 | Rõ ràng, đúng đắn của bài toán 25 · Giá trị ứng dụng, cần thiết 20 · Hợp lý của giải pháp 20 · Khả thi dữ liệu 15 · Sáng tạo, khác biệt 10 · Trình bày hồ sơ, phỏng vấn 10 |
| V2 | Làm rõ và xử lý bài toán 20 · Chất lượng dữ liệu và cách tiếp cận 15 · Hợp lý của giải pháp, thuật toán 20 · Chất lượng prototype 20 · Khả năng ứng dụng, triển khai 15 · Trình bày, tài liệu 10 |
| V3 | Xem bảng dưới |

- **Vòng 3: BGK chấm gì và GreenScan đang ở đâu:**

| # | Tiêu chí (trọng số) | BGK nhìn gì (thể lệ tr.9–12) | Mức 70–<90 · mức 90–100 | GreenScan có (tới 01/11) | Lỗ hổng BGK sẽ thấy |
|---|---|---|---|---|---|
| 1 | Mức độ giải quyết bài toán thực tiễn (20) | Giải triệt để bài toán **đặt ra ở vòng đầu**. Kết quả định lượng (độ chính xác, sai số, tốc độ, **lợi ích kinh tế ước tính**) chứng minh qua demo và số liệu. Cải thiện vượt trội so với giải pháp hiện có | Giải tốt, có số liệu · Giải triệt để, vượt trội | 264 trang trong khoảng 2 phút. 0 vu oan trên Hòa Phát và trên GS-Bench ngoài mẫu. 4/4 ca có phán quyết. Hàng đợi 9/172 | Chưa có số thời gian và chi phí so với làm tay. Kết quả phẳng (153/156 khớp một phần). Độ phủ kết luận thấp. 0 quy tắc pháp lý áp được, 0 nguồn độc lập |
| 2 | Chất lượng kỹ thuật giải pháp, dữ liệu (15) | Kiến trúc rõ, mở rộng và tích hợp được. Thuật toán có cơ sở, được kiểm chứng, có so sánh. Hiệu năng. Dữ liệu xử lý bài bản, cập nhật được. Có xét explainability, độ tin cậy, rủi ro kỹ thuật | **Tốt, có kiểm thử** · Xuất sắc, kiến trúc mạnh | 10 bất biến kiến trúc, 410 test. So luật với 5 LLM (size ladder); AG-1, AG-2 có đăng ký trước. Mọi kết luận có trang và phép tính. Manifest tái lập | Chưa có gold người. Dữ liệu chạy đầu–cuối mới có 1 doanh nghiệp. Bảng PDF bị dàn phẳng. Recall truy xuất chưa đo |
| 3 | Chất lượng sản phẩm, khả năng demo (20) | Đủ chức năng chính, ổn định khi demo, UI/UX thân thiện với người dùng mục tiêu, thời gian phản hồi tốt, **cài lại từ mã nguồn thuận tiện** | Ổn định, UI tốt · Hoàn hảo, production-ready | Web app một cổng (giao diện và API), chạy ngoại tuyến. Studio (14/10): gạch dưới tuyên bố, đề xuất sửa, xuất DOCX có tracked changes. Giấy làm việc in được | Chưa đo SUS và thời gian thao tác. Docker chưa build thử (tính tới 14/10). Máy demo chưa có OCR (tính tới 14/10) [kiểm lại] |
| 4 | Tính khả thi triển khai thực tế (20) | Hạ tầng, dữ liệu, nhân lực khả thi. **Chi phí triển khai, vận hành, bảo trì.** Kế hoạch pilot. (Ưu tiên) **có kết nối hoặc phản hồi từ đơn vị thực tế.** Tuân thủ bảo mật và pháp lý | Triển khai được trong 6 tháng · Sẵn sàng, **có đối tác xác nhận** | Laptop không GPU; chế độ ngoại tuyến tốn 0 đồng. Phân lớp tài liệu A/B/C. Lộ trình 6 tháng (pilot 11–12/2026) | Repo chưa ghi đối tác hay pilot nào. Đường đám mây đang hỏng (FPT 401). Chưa ước tính chi phí viết và duyệt quy tắc pháp lý |
| 5 | Tác động xã hội và đạo đức (10) | Rủi ro đạo đức, thiên vị, bảo mật; cơ chế minh bạch; AI có trách nhiệm trong tài chính – kế toán | Có phân tích · Toàn diện, có lộ trình rõ | Không kết luận về doanh nghiệp, không xếp hạng, không dùng chữ "vi phạm". Người ký. Abstain. Chạy ngoại tuyến | Thiên vị ngành (mới có thép). Luật vẫn bỏ lọt (có SUPPORTED sai) |
| 6 | Trình bày, bảo vệ, phản biện (15) | Đi thẳng vào giá trị, kết hợp số liệu và câu chuyện thực tế. Trả lời BGK và **nhà đầu tư** nhanh, chính xác, **trung thực về giới hạn**. Hiểu sâu lĩnh vực. Có tầm nhìn và lộ trình thương mại hoá | Tự tin, rõ ràng · Thuyết phục, tầm nhìn sắc bén | Kỷ luật gắn nhãn số [Đã đo] / [Sơ bộ] / [Chưa có] | Số cũ trong bộ hỏi đáp; tài liệu mâu thuẫn nhau (mục 5) |

- **Liên quan GreenScan:** đội dự thi Nhóm 3 (AI cho Quản trị rủi ro và Tuân thủ: RegTech, kiểm toán thông minh). Thể lệ không bắt buộc dùng lượng tử (Điều 6.3: "AI … hoặc/và Lượng tử").
- **Giống:** triết lý "đơn giản, chạy ổn định, đo được" của Điều 10 trùng với "Models read – Rules decide – Humans review".
- **Khác:** thể lệ đòi chứng minh lợi ích so với cách làm truyền thống và đòi kết nối đơn vị thực tế. GreenScan chưa có cả hai.

### 1.2 AI-QUANTUM_AGENT_CRITERIA_v1 (tài liệu nội bộ, tổng hợp từ "Tập huấn AIC 2026 – Buổi 3", Zhao et al. 2024, Cahoon et al. 2025)
- **Là gì:** ba phần ghép lại.
  - (a) **Định nghĩa bài toán greenwashing tài chính theo ba lớp:** greenwashing chung; greenwashing trong tài chính; định nghĩa cho AI.
    - Theo lớp AI, rủi ro là mức không nhất quán giữa tuyên bố và bốn loại bằng chứng: định lượng, pháp lý, tài chính, bên ngoài.
    - Kèm theo: 8 dạng greenwashing, nhóm dữ liệu, output mong muốn, và rubric điểm gợi ý 7 tiêu chí (0–15 · 0–15 · 0–10 · 0–20 · 0–10 · 0–20 · 0–10).
  - (b) **"Thẻ 1": 7 công thức trừ điểm** và "Mức độ trung thực ESG = 100 − Σ điểm trừ + điểm thưởng". Ngưỡng đều tự đặt, ví dụ:
    - năng lượng tái tạo ≥ 20% thì không trừ;
    - tái chế ≥ 90% thì không trừ;
    - "chi phí môi trường tiềm ẩn" = chi phí dịch vụ mua ngoài × hệ số ngành 0,10.
  - (c) **"Bộ tiêu chí AI Agent":**
    - 8 vai agent; khuyến nghị V1 dùng **"single orchestrator + specialized tools"**.
    - 7 Quality Gate (Gate 0–6).
    - 10 nhóm chỉ tiêu có trọng số: A 8 · B 12 · C 15 · D 15 · E 10 · F 12 · G 8 · H 7 · I 6 · J 7.
    - Ngưỡng: Evidence Recall@k ≥ 0,85; citation ≥ 0,95; contradiction F1 ≥ 0,80; calculation accuracy ≥ 0,95; faithfulness ≥ 0,90; P95 ≤ 120 s/tài liệu; SUS ≥ 70.
    - Rubric cho một lần chạy: 7 hạng mục × 0–3 = 21 điểm. Đạt khi ≥ 16 và không hạng mục nào 0 điểm; ca rủi ro cao cần ≥ 18 và reviewer duyệt.
    - Bộ test nghiệm thu: golden set 50–100 claim, hard negatives, contradiction, missing evidence, prompt injection, tool failure, regression.
- **Liên quan:** đây là khung tự đánh giá agent. BGK, nhất là người dạy buổi tập huấn của BTC, có thể hỏi theo các khái niệm: environment, observation/action space, memory (episodic/semantic/procedural), planning, self-reflection.
- **Giống:**
  - GreenScan theo đúng khuyến nghị V1: một orchestrator và các công cụ, không đa tác tử (ADR 0001).
  - Đã có Gate 0 (màn xem trước báo trang mất chữ), Gate 2 (bằng chứng dưới ngưỡng chỉ là ứng viên), Gate 3 (số học bằng mã), Gate 5 (ca rủi ro qua người) và Gate 6 (manifest).
  - GS-Bench có đúng các họ test: N (khác kỳ, đơn vị, phạm vi, tức hard negatives), C (mâu thuẫn), S (khớp).
- **Khác:**
  - Phần "Thẻ 1" (điểm trung thực, ngưỡng tự đặt) **đội đã bỏ** theo D-2026-09-18-05 (dẫn trong QA_BANK Q53), vì ngưỡng không có căn cứ và biến điểm thành cáo buộc.
  - Gate 4 (citation) mới trích tới trang, chưa tới ô bảng.
  - Phần lớn ngưỡng (Recall@k, citation accuracy, faithfulness, SUS) chưa đo trên gold.

### 1.3 AI-Q2026.txt: kịch bản thuyết trình cũ (15 slide, khoảng 10 phút)
- **Là gì:** kịch bản đi kèm bộ slide 26/09, bộ mà file 01 Bán kết ghi là đã thay thế. Đây là suy luận: kịch bản có ngày "22/09/2025" và nhắc BM25 + char n-gram, đều là chi tiết của khoảng cuối tháng 9.
- **Luận điểm chính:**
  - Tên đề tài: "chấm điểm rủi ro tẩy xanh **và tự động tư vấn cải thiện báo cáo ESG, BCTC**".
  - Số bối cảnh: Bloomberg 53.000 tỷ USD (dự báo 2025); 704.000 tỷ đồng, trên 21%/năm; PwC 2022: 80% có kế hoạch ESG, 22% ưu tiên môi trường.
  - Chuẩn mực: ISAE 3000, ISSA 5000.
  - "Cổng so sánh **7 điều kiện**". Điều kiện 7 là khung chuẩn mực (IFRS S1/S2, GRI, SASB, QĐ 21), "bổ sung để phù hợp ISSA 5000".
  - "QĐ 21/2025: 7 nhóm ngành, 45 lĩnh vực, phải có giấy phép môi trường".
  - Risk profile: evidence strength 0,92; contradiction 0,05; trọng yếu kép "currently undetermined".
  - Ví dụ Hòa Phát: "Scope 1+2 **năm 2023**, BCPTBV 2023 **trang 47**"; "Reviewer: Chuyên gia ESG, ngày duyệt 22/09/2025".
  - "2 ngày → 2 phút"; "ngăn chặn **triệt để** ảo giác".
  - **"Lộ trình ESG 6 bước cho doanh nghiệp FDI"**, nhắc lại ở 5 slide.
- **Liên quan:** đây là nguồn của phần lớn các lời hứa BGK có thể vặn (mục 5).
- **Giống:** kiến trúc 4 giai đoạn và 5 mức kết luận.
- **Khác sản phẩm thật:**
  - không có tư vấn tự động theo nghĩa rộng;
  - không có điều kiện thứ 7;
  - không có tính năng nào cho doanh nghiệp FDI;
  - không có chuyên gia ESG ngoài nhóm duyệt;
  - mô tả sai hai văn bản luật (mục 5.1).

### 1.4 Hồ sơ Vòng 1 (mã đội AQ2026-119, Eco Nexus; Nhóm 3; Liên ngành)
- **Là gì:** hồ sơ đề xuất ý tưởng. Đội 3 người:
  - Lê Diễm Quỳnh (Kiểm toán, HVTC): trưởng nhóm, nghiệp vụ kiểm chứng;
  - Phan Thanh Thảo (Thuế – Hải quan, HVTC): pháp lý, taxonomy;
  - Nguyễn Chơn Nhân (Khoa học máy tính, UIT): kỹ thuật.
- **Luận điểm chính kèm số:**
  - **Bối cảnh:**
    - Dư nợ tín dụng xanh trên 704.244 tỷ đồng (31/3/2025), 58 tổ chức tín dụng, chiếm 4,3% tổng dư nợ, tăng bình quân trên 21,2%/năm giai đoạn 2017–2024 [1][2].
    - QĐ 21/2025 ban hành 04/7, hiệu lực 22/8/2025.
    - QĐ 13/2024: 2.166 cơ sở phải kiểm kê khí nhà kính.
    - EC: 53,3% tuyên bố môi trường mơ hồ, gây hiểu lầm hoặc không căn cứ; 40% không được chứng minh.
    - Giữa năm 2025 mới có 13–15 ngân hàng thương mại công bố báo cáo phát triển bền vững.
  - **Định nghĩa vận hành:**
    - Tuyên bố định lượng chỉ được **Supported** khi đủ 5 thuộc tính: chỉ số; giá trị và đơn vị; kỳ; năm gốc; phạm vi.
    - Thiếu một thuộc tính thì là Partially supported.
    - Không có bằng chứng thì là Insufficient evidence.
  - **Người dùng đầu tiên:** **bộ phận ESG và kiểm toán nội bộ của doanh nghiệp niêm yết, tự soát bản nháp** trước khi công bố.
  - **Phạm vi MVP:** tuyên bố môi trường định lượng của 4–6 ngành phát thải cao; đối chiếu Luật BVMT 2020, TT 17/2022, QĐ 21/2025.
  - **Ngưỡng MVP:** F1 trích xuất ≥ 0,75; Recall@10 ≥ 0,85; độ chính xác trích dẫn ≥ 0,90; lỗi số học = 0; độ chính xác verdict ≥ 0,80; abstain thì "báo cáo minh bạch".
  - **Dữ liệu:**
    - 30–50 doanh nghiệp mục tiêu; corpus lõi 8–12 doanh nghiệp × 3 năm.
    - 150–300 tài liệu; 30.000–80.000 đơn vị nội dung; 1.000–3.000 claim ứng viên.
    - **Gold tối thiểu 100 cặp**, mở rộng lên 300–500; hai người gán độc lập và một trọng tài, mục tiêu **κ ≥ 0,7**; khoảng 5 phút mỗi cặp.
    - Dữ liệu silver **không trộn vào gold** và "không dùng để đánh giá cuối cùng".
  - **Lợi ích (hồ sơ tự ghi là giả thuyết):** một báo cáo 200–300 trang cần 8–12 giờ đọc tay, mục tiêu rút còn 30 phút sàng lọc và khoảng 2 giờ rà; khoanh 5–10% số claim vào nhóm rủi ro cao.
  - **Lượng tử:**
    - QUBO chọn tập bằng chứng: H(x) = −Σ r_j·x_j + λ·Σ s_jk·x_j·x_k + μ·(Σ x_j − k)².
    - 20–40 đoạn ứng viên cho mỗi claim; so với thuật toán tham lam và MMR.
    - Ghi là "nghiên cứu ở Vòng 2".
  - **Kế hoạch:** 12 tuần, 4 giai đoạn. Sản phẩm dự kiến: dashboard, web app, chatbot có grounding, API, hệ hỗ trợ quyết định, bộ dữ liệu claim–evidence.
  - **Cam kết:** không kết luận vượt bằng chứng; không công bố xếp hạng hay cáo buộc doanh nghiệp; ưu tiên chạy cục bộ.
- **Liên quan:** TC1 Vòng 3 chấm theo "bài toán đặt ra ở vòng đầu", nên đây là thước đo BGK sẽ dùng.
- **Giống hiện tại:** vẫn giữ lõi evidence-first, 5 mức kết luận, abstain, không xếp hạng doanh nghiệp, chạy cục bộ.
- **Khác:**
  - người dùng chính đã chuyển sang kiểm toán viên (từ Bán kết);
  - điểm rủi ro cấp tài liệu đã bị bỏ;
  - gold, các ngưỡng, rule pack, reranker, trích dẫn ô bảng, chatbot và QUBO đều chưa có (mục 5.2).

### 1.5 Hồ sơ nguyên lý cho Hội đồng (14/10/2026)
- **Là gì:** bộ 4 phần (báo cáo tổng quan, bài báo, hướng dẫn, phát triển tương lai). Mọi số đều gắn nhãn [Đã đo], [Sơ bộ] hoặc [Chưa có].
- **Số đã đo:**
  - Hòa Phát 264 trang: 107–121 s, RAM đỉnh 1,3 GB, không GPU, không khoá API.
  - 0 mâu thuẫn sai (ngày 17/09 là 357/419).
  - 4/4 ca có phán quyết khớp.
  - 385 test.
  - Studio neo được 147/156 tuyên bố, sinh 391 đề xuất, không đề xuất nào thêm số.
- **Số sơ bộ:**
  - Hàng đợi: người soát đồng ý 12/14 mục; khoảng 6/9 mục đúng.
  - Học trò T1 (e5-base): F1 nhị phân 0,82, luật 0,61; macro-F1 0,726. κ 0,92 là **giữa hai lượt Claude**, không phải giữa người.
  - Size ladder: luật đúng 20/32; các mô hình đúng 29–32/32.
- **Tự nhận chưa đạt:**
  - gold người: 0;
  - nguồn độc lập: 0 (780/780 bằng chứng là tài liệu nội bộ);
  - 0/156 tuyên bố có quy tắc pháp lý áp được;
  - kết quả phẳng;
  - 4/108 trang quét bị mất chữ;
  - học trò chưa gắn vào sản phẩm.
- **Khung lý luận:**
  - 8 nguyên lý N1–N8: compound AI, PAL/PoT, MiniCheck, ESGReveal, Sufficient Context, Climate-FEVER, pháp lý theo hiệu lực, người ký.
  - 4 luận điểm L1–L4: thước đo tin được; tốt hơn cách đang có; bắt được thật mà không vu oan; dùng được thật.
  - Quy tắc quyết định ghi trước khi có kết quả.
- **Liên quan:** đây là "hiến pháp" để trả lời phản biện. Bốn luận điểm L1–L4 khớp với TC1–TC4 Vòng 3.
- **Khác so với 01/11:**
  - chế độ đám mây GLM-5.2 nay hỏng khoá;
  - số test từ 385 lên 410;
  - "không phát hiện tác động của kích thước" chỉ còn đúng cho bước kiểm chứng từng cặp, không còn đúng cho độ phủ của bước đọc IR.

### 1.6 Bộ chuẩn bị Bán kết 25/10 (README, 01, 04; 03 chỉ grep)
- **Là gì:** kịch bản 14 slide, demo 2:40 và hỏi đáp bổ sung theo 6 tiêu chí Vòng 2; lập ngày 09/10.
- **Luận điểm chính:**
  - **Định vị lại:** "trợ lý cho kiểm toán viên" thay cho "chấm điểm và tư vấn".
  - **Ba điều BGK phải nhớ:** hai con số khác nhau chưa phải là mâu thuẫn; "chưa đủ bằng chứng" là một kết quả hợp lệ; chạy trên laptop không GPU, tài liệu không rời máy.
  - **Demo trên Hòa Phát:**
    - Tuyên bố "mức độ tự chủ điện năng rất cao" → hệ thống tìm sang BCTN 2024 tr.86 "tự chủ 90% … 788 triệu kWh" → khớp một phần.
    - Cộng bảng khí nhà kính tr.39: 22.540.603 + 933.876 = 23.474.479, công bố 23.474.480.
  - **Cơ chế:** cổng so sánh 6 điều kiện; dung sai theo độ chính xác công bố; thí nghiệm có đối chứng ngày 28/09.
  - **Dữ liệu:** 1.061 tài liệu từ 21 doanh nghiệp, 670 bản gốc có SHA-256; registry 11 văn bản; 28 bộ án lệ.
  - **Khác:** ba cột Đã đạt / Mục tiêu / Giả thuyết; 3 chế độ triển khai; lộ trình 6 tháng; slide QUBO 15 giây "không tuyên bố quantum advantage".
  - **§4 "Số liệu được phép":** cấm nói "độ chính xác X%", "8–12 giờ", "53.000 tỷ USD", "704,2 nghìn tỷ", ">21%/năm", số PwC, mức phạt cụ thể.
- **04 §1:** liệt kê 6 câu QA_DRILL đã lỗi thời: #3 (reranker), #7 (LLM chuẩn hoá), #11 (gold), #16 (NĐ 83/2026), #22 (local-first), #24 (rerank 30→5).
- **Giới hạn tự khai (P2):**
  - chữ gãy dòng vẫn lọt vào hàng đợi (mục #1);
  - 1 trong 2 tuyên bố "ủng hộ" là chữ dính cột (con số "90%");
  - chưa trích dẫn tới ô bảng;
  - mới có 1 quy tắc pháp lý nháp;
  - nhánh OCR chưa kiểm trên máy demo;
  - thứ tự hàng đợi chưa được kiểm toán viên kiểm.
- **Liên quan:** đây là khung câu trả lời tốt nhất hiện có, nhưng phải thay số theo mục 5.

### 1.7 QA_DRILL.md (24 câu "gần như chắc chắn")
- **Cách trả lời:** theo mẫu "failure mode → design choice → measurement".
- **Phần nguyên lý vẫn đúng:**
  - đơn vị phân tích là claim;
  - RAG chỉ là tầng truy xuất;
  - không tìm thấy bằng chứng thì ra INSUFFICIENT, chỉ thành UNSUPPORTED khi kho tài liệu lẽ ra phải có;
  - tài liệu của doanh nghiệp không tự chứng minh cho chính nó;
  - risk score không phải xác suất;
  - κ không phải accuracy;
  - chia tập theo doanh nghiệp;
  - luật xét theo ngày hiệu lực;
  - không dùng đa tác tử;
  - prompt injection được coi là dữ liệu không tin cậy.
- **Lỗi thời:** #3, #7, #11, #16, #22, #24 (đã nêu ở 04 §1). Riêng #11 hứa "≥ 60 cặp trước 10/10", chưa đạt.
- **Kiến thức chung:** bảng 8 khối cả ba người phải nắm: ESG, tài chính xanh, pháp lý Việt Nam, IR, LLM, đánh giá, Document AI, lượng tử.

### 1.8 QA_BANK_100 (20/09) và bản trùng GreenScan_100_Cau_BGK.txt
- **Cấu trúc:** 100 câu chia 4 mảng (RAG Q1–30; tài chính – kế toán và số liệu Q31–58; pháp lý Q59–82; lượng tử Q83–100). Kèm công thức trả lời 4 bước, nhãn hiện trạng (đã chạy / có hook nhưng tắt / mới trên giấy) và bảng "đừng nói".
- **Số cũ phải thay:**
  - 233 test; 21 bẫy;
  - Hòa Phát 210 claim, CONTRADICTED 4%;
  - 11 MB/803 chunk;
  - gold 5 claim đã trọng tài;
  - BGE-M3 làm embedding; reranker 30→5;
  - ví dụ rubric điểm 82;
  - "người dùng đầu tiên là ngân hàng" (Q74).
- **Vẫn dùng được:**
  - Nguyên lý RAG: distractor, top-k, lost in the middle, để GraphRAG sau.
  - Rubric (Q53–Q55): 9 thành phần có trần, không phải xác suất, không có điểm doanh nghiệp.
  - Tái lập (Q57).
  - Pháp lý (Q62–Q66, Q74–Q80): QĐ 21 chỉ áp cho dự án xin xác nhận; Luật BVMT tách được 938 điều khoản; khoảng 4.200 dòng điều khoản cho 11 văn bản; **0 điều khoản đã gắn vào quy tắc**.
  - Lượng tử (Q83–Q100): QUBO mở rộng có biến phủ y_m; ánh xạ Ising x = (1 − s)/2; khoảng 30–50 qubit logic.

### 1.9 Kết quả mới 31/10–01/11 ("Số mới" §2, §10)
- **7 lỗi đã đo (F1–F7):**
  - F1 kết luận phẳng;
  - F2 luật phủ thấp;
  - F3 bảng PDF bị dàn phẳng;
  - F4 lỗi chuẩn hoá Q1–Q5;
  - F5 pháp lý: 0 quy tắc áp được;
  - F6 bằng chứng chỉ từ nguồn nội bộ;
  - F7 0 gold người (0/88 cặp, 0/79 câu).
- **GS-Bench v1.1:**
  - 453 ca: 51 ca B-a dựng tay và 402 ca B-b sinh từ số liệu thật (S 95 / C 123 / N 184), trên 7 doanh nghiệp.
  - Nhãn bạc: Claude đọc IR, bộ kiểm tất định soát lại; soát tay 14 ca.
- **Luật:**
  - Trên B-b: độ phủ 0,028, precision 0,75, **bắt được 0/44 ca mâu thuẫn**.
  - Trên v1.1: 0 CONTRADICTED sai nhưng **9 SUPPORTED sai**.
  - Trần (IR đúng hoàn toàn + irlib): độ phủ 0,528, precision 1,0.
- **AG-1:**
  - Lỗi của model chủ yếu là lỗi định dạng: cả 11/11 ca sai của 32B là do model tự thêm bội số. Sửa bằng `irlib.ground()`.
  - Ngoài mẫu sạch v1.3 (87 ca): độ phủ luật 0,011 · 4B 0,138 · 8B 0,115 · 14B 0,115 · 32B 0,253. Mọi cấu hình có precision 1,0, 0 kết luận sai.
  - Ngoài mẫu v1.1 (246 ca): độ phủ 4B/8B/14B/32B = 0,126 / 0,220 / 0,256 / 0,329. Dự đoán "không có hiệu ứng quy mô" vì vậy sai.
- **AG-2 ("luật + 4B, bỏ phiếu S đơn độc của luật"):**
  - Qua phần thống kê của cổng.
  - Tập G (162 ca): độ phủ 0,093, precision 1,0, 0 SUPPORTED sai, 0 CONTRADICTED sai; CI phần tăng độ phủ [0,016; 0,185].
  - Tập hiệu chỉnh (388 ca): 0,242 / 0,989 / 1 / 0, trong khi luật có 8 SUPPORTED sai.
  - Lưu ý: trên G, 4B chỉ dám kết luận 15 ca.
- **Bộ đọc Qwen3-4B Q4 chạy cục bộ:**
  - Khớp 0,963 với bản bf16.
  - Luật + 4B Q4 trên G: 0 sai, độ phủ 0,080.
  - 1,7 s/câu trên T4; chưa đo trên laptop vì thiếu RAM.
  - Chưa vào sản phẩm, chờ cổng 06/11. Nếu vào thì chỉ là trợ giúp người soát, đặt sau cờ cấu hình, **không đổi verdict** (D-2026-10-16-01).
- **AG-3 (dựng bảng):**
  - Dựng hàng bảng từ toạ độ chữ: Hòa Phát tr.39 đủ 10 hàng, cộng dọc 3/3 khớp.
  - Trên 7 ca: đúng 3/7, 0 sai. Dự đoán "≥ 5/7" sai. Nguyên nhân: IR thiếu chiều `segment`.
  - Tiêu đề trang ghi "NĂM 2024", còn bảng ghi 2025.
- **Hạ tầng:**
  - Khoá FPT trả 401, nên đường đám mây GLM-5.2 không chạy.
  - Chọn Groq `openai/gpt-oss-120b` (12/12 JSON, p50 1,0 s), chỉ dùng cho tài liệu công khai.
  - Demo vẫn chạy `offline`.

### 1.10 Câu hỏi đã gặp ở Vòng 1–2 (có ghi lại)
- **Có ghi (1 câu):** một giảng viên nhận xét ngày 10/10: *"mô hình LLM của nhóm quá bé, không xử lý được bài toán phức tạp như đã đặt ra"* (`MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`). Câu trả lời cập nhật ở Q6.
- **Không có ghi:** câu hỏi phỏng vấn Vòng 1 (09/08) và câu hỏi Bán kết (25/10). Các bộ QA_DRILL, QA_BANK và 04 là câu **dự kiến**, không phải câu đã gặp.

---

## 2. Khái niệm và lý thuyết phải nắm

| Khái niệm | Định nghĩa ngắn / công thức | Ví dụ gắn GreenScan |
|---|---|---|
| Cách tính điểm Vòng 3 | Điểm đội = Σ (TB điểm giám khảo ở tiêu chí i × wᵢ), với w = 0,20 / 0,15 / 0,20 / 0,20 / 0,10 / 0,15 | TC4 tăng từ 55 lên 75 (nhờ có thư quan tâm pilot) thì tổng tăng 4 điểm; muốn được 4 điểm từ TC5 phải tăng TC5 thêm 40 |
| Greenwashing (ESMA) | Tuyên bố, hành động hay truyền thông về bền vững không phản ánh rõ ràng và công bằng hồ sơ bền vững thực chất, có thể gây hiểu lầm nhà đầu tư [NGOÀI, dẫn trong AGENT_CRITERIA] | GreenScan không kết luận greenwashing; chỉ kiểm quan hệ giữa tuyên bố và bằng chứng |
| 8 dạng greenwashing | Mơ hồ · không bằng chứng · chọn lọc · mâu thuẫn định lượng · mâu thuẫn pháp lý · tẩy xanh tài chính (use of proceeds) · cam kết tương lai rỗng · đánh tráo trọng tâm | Đo được hôm nay: mơ hồ (thiếu thuộc tính), mâu thuẫn định lượng (cộng bảng, tính lại %). Chưa đo được: pháp lý, use of proceeds, chọn lọc |
| Tuyên bố, bằng chứng, provenance | Tuyên bố nguyên tử, giữ doc_id, trang, nguyên văn. Bằng chứng là đoạn văn, bảng hoặc điều khoản. Provenance ghi nguồn, trang, thời điểm, phiên bản công cụ | Bất biến 2 và 10 |
| 5 thuộc tính | Chỉ số · giá trị và đơn vị · kỳ · năm gốc · phạm vi | "Giảm 30% phát thải" thiếu chỉ số con, năm gốc, phạm vi → khớp một phần, kèm danh sách thiếu |
| 5 mức kết luận | SUPPORTED: cùng chỉ số, kỳ, phạm vi, khớp trong sai số làm tròn. CONTRADICTED: đủ điều kiện so, lệch ngoài sai số. PARTIALLY_SUPPORTED: cùng chủ đề nhưng thiếu điều kiện. UNSUPPORTED: chỉ dùng khi kho tài liệu lẽ ra phải có mà không có (ADR 0005). INSUFFICIENT_EVIDENCE: kho chưa đủ để nói | "Không tìm thấy" không có nghĩa là "sai" |
| Cổng khả năng so sánh | Sản phẩm (`numeric_facts.eligibility`): đơn vị và 6 chiều (cơ sở đo, ranh giới, công nghệ, chỉ số con, Scope, mục tiêu hay thực hiện), cộng kiểm khoảng cách độ lớn. Chiều "không rõ" không tự chặn; chỉ chặn khi cả hai bên đều biết và lệch nhau. Đường IR mới (`irlib.comparable`): chỉ số, loại giá trị, trạng thái, kỳ, phạm vi, ranh giới, đơn vị | "Chiếm 99% tổng phát thải" và "sản lượng tăng 24%" → không được so |
| Dung sai theo độ chính xác công bố | Nửa đơn vị của chữ số cuối: tol = 0,5 × 10^(−d), d là số chữ số thập phân công bố | "12%" → 11,5–12,5; "12,0%" → 11,95–12,05; 23.474.479 so với 23.474.480 là khớp (làm tròn 1 tCO2e) |
| % thay đổi tính lại | Δ% = (kỳ báo cáo − kỳ gốc)/kỳ gốc; điểm phần trăm khác % tương đối | Tuyên bố "giảm 30%" được kiểm bằng hai số tuyệt đối cùng phạm vi |
| GHG Protocol | Scope 1 trực tiếp; Scope 2 năng lượng mua; Scope 3 chuỗi giá trị. Phân biệt tuyệt đối với cường độ; năm gốc; ranh giới tổ chức theo kiểm soát hoặc theo vốn [KIẾN THỨC NỀN] | Lỗi Q1 (cường độ so với tuyệt đối) và Q2 (công ty mẹ so với hợp nhất) |
| Dự đoán có chọn lọc | Độ phủ = số ca dám kết luận / tổng số ca; precision tính trên phần đã kết luận; vẽ đường risk–coverage | AG-1: 4B có độ phủ 0,138, precision 1,0 |
| Vu oan và bỏ lọt | Vu oan = CONTRADICTED sai (hại doanh nghiệp). Bỏ lọt = SUPPORTED sai (hại nhà đầu tư) | Luật: 0 vu oan nhưng 8–9 bỏ lọt trên GS-Bench v1.1 → AG-2 bỏ phiếu S đơn độc của luật |
| Cohen's κ | κ = (p_o − p_e)/(1 − p_e): đồng thuận vượt mức ngẫu nhiên giữa hai người gán; từ 0,7 trở lên là khá [KIẾN THỨC NỀN] | κ 0,92 là giữa hai lượt Claude, không phải giữa người |
| Kiểm định McNemar | So hai bộ phân loại trên cùng tập ca: χ² = (b − c)²/(b + c), với b, c là số ca chỉ một bên đúng; n nhỏ thì dùng phép thử nhị thức chính xác | Luật so với LLM trên 32 ca sạch: p ≤ 0,022 |
| CI bootstrap theo doanh nghiệp | Lấy mẫu lại theo doanh nghiệp chứ không theo câu, để tránh tự tương quan | CI phần tăng độ phủ [0,016; 0,185] |
| Chia tập theo doanh nghiệp, đăng ký trước | Tách train/test theo doanh nghiệp. Ngưỡng và dự đoán ghi vào `configs/measurement_decisions.yaml` trước khi chạy. Tập test chỉ chạm một lần | AG-1, AG-3 công bố cả các dự đoán sai |
| Macro-F1 | Trung bình F1 các lớp; lớp hiếm có trọng số bằng lớp đông | T1 macro-F1 0,71–0,73 (trên nhãn Claude) |
| RAG, BM25, n-gram ký tự, RRF | BM25: khớp từ có trọng số IDF và chuẩn hoá độ dài. N-gram ký tự: chịu được lỗi chính tả, lỗi OCR, mất dấu. RRF(d) = Σ_r 1/(k + rank_r(d)), k thường là 60 [KIẾN THỨC NỀN] | Mặc định: BM25 + n-gram ký tự + RRF, lấy 30 ứng viên giữ 5. Dense và reranker có adapter nhưng đang tắt |
| Distractor, top-k, lost in the middle | Đoạn giống câu hỏi nhưng không hỗ trợ có thể làm RAG tệ hơn; tăng k không luôn tốt hơn; thông tin nằm giữa ngữ cảnh dài dễ bị bỏ sót (Zhao 2024; Liu 2024, TACL) | Không đưa cả báo cáo vào LLM |
| Compound AI, giao tính toán cho công cụ | Hệ ghép nhiều bước, mỗi bước có đầu ra kiểm được (Zaharia 2024). PAL 72,0 so với 56,9; PoT trên FinQA từ 58,2 lên 74,0 [NGOÀI] | Số học do mã; LLM chỉ đọc |
| Sufficient context | Mô hình lớn trả lời sai 36–40% khi ngữ cảnh không đủ (Joren, ICLR 2025) [NGOÀI] | Nhãn "chưa đủ bằng chứng" do luật quyết, không giao cho mô hình |
| Policy-as-code, hiệu lực theo ngày, "đóng khi thiếu" | Mỗi quy tắc có điều kiện, căn cứ đến điều và khoản, ngày hiệu lực, chuỗi sửa đổi và `reviewed_by`. Thiếu quy tắc hoặc điều kiện chưa biết thì ra "cần người xem", không bao giờ ra "phù hợp" | NĐ 06/2022 → 119/2025 → 83/2026; NĐ 83 chỉ sửa phần chất làm suy giảm tầng ô-dôn |
| Bộ nhớ của agent | Episodic (lịch sử phiên), semantic (tri thức, taxonomy), procedural (quy trình, rubric), mỗi loại có version, TTL và phạm vi (AGENT_CRITERIA) | Semantic: registry 11 văn bản và từ điển. Procedural: rule pack, comparison policy, risk rubric có version. Episodic: nhật ký append-only các quyết định của người soát. Người dùng thêm quy định nội bộ nghĩa là thêm văn bản vào registry và viết quy tắc có `reviewed_by`, không phải huấn luyện lại |
| Quality gates (Gate 0–6) | Đủ điều kiện đầu vào → trích xuất → truy xuất → kiểm chứng bằng mã → trích dẫn → duyệt rủi ro → tái lập | GreenScan có Gate 0, 2, 3, 5, 6; Gate 4 mới trích tới trang |
| Đảm bảo thông tin bền vững | ISAE 3000 (Revised); ISSA 5000 (IAASB công bố 11/2024, áp dụng cho kỳ bắt đầu từ 15/12/2026) [KIẾN THỨC NỀN]. Đảm bảo hạn chế khác đảm bảo hợp lý. Không thu đủ bằng chứng thì đưa kết luận ngoại trừ hoặc từ chối kết luận | GreenScan là công cụ thu thập bằng chứng và lập giấy làm việc, không phát hành kết luận đảm bảo |
| Trọng yếu kép | Trọng yếu tài chính cộng trọng yếu tác động [KIẾN THỨC NỀN] | Chưa có trục trọng yếu theo ngành (QA_BANK Q56) |
| QUBO, Ising, SA, QAOA | min xᵀQx với x ∈ {0,1}ⁿ; ràng buộc đưa vào dạng phạt; x = (1 − s)/2 ánh xạ sang Ising. SA (ủ mô phỏng) là thuật toán cổ điển; QAOA chạy trên trình mô phỏng; phần cứng NISQ giới hạn số qubit và độ sâu mạch | Chọn k đoạn bằng chứng: −Σ r_j x_j + λ Σ s_jk x_j x_k + μ(Σ x_j − k)², khoảng 30–50 qubit logic. **Chưa có mã** |

---

## 3. Số liệu và dữ kiện được phép nói

*Quy ước:* số đo trên nhãn Claude hoặc trên đáp án sinh theo cấu trúc vẫn gắn [ĐÃ THỰC NGHIỆM], nhưng ghi rõ "nhãn AI". Theo chỉ đạo của người dùng (04/11), nhãn Claude được dùng như một dataset bình thường sau khi người dùng duyệt lại. Khi nói với BGK thì gọi là **"nhãn AI, có người duyệt"**, không gọi là "gold do người gán độc lập", vì hồ sơ Vòng 1 đã định nghĩa gold là nhãn do người gán và trọng tài xác nhận.

### 3.1 Thể lệ
- Vòng 3: 10/11/2026, HT 700 HVTC, 6 đội, tối đa 10 phút trình bày và 8 phút hỏi đáp, có khu demo và nhà đầu tư · thể lệ Điều 8.3, tr.5 · [NGOÀI]
- Trọng số Vòng 3: 20/15/20/20/10/15 · Điều 11.3, tr.9–12 (đã đối chiếu ảnh tr.11) · [NGOÀI]
- Mức 70–90 của TC2 là "Tốt, có kiểm thử" · tr.10 (đối chiếu ảnh) · [NGOÀI]
- Mô hình đơn giản chạy ổn định được điểm cao hơn mô hình phức tạp; hai giám khảo lệch quá 30 điểm thì thảo luận · Điều 10, tr.6 · [NGOÀI]
- AI hỗ trợ phải khai báo; BGK được yêu cầu xem dữ liệu, mã nguồn · Điều 14 tr.12; Điều 9 tr.5 · [NGOÀI]
- Sản phẩm đạt giải, nếu được chọn phát triển, thuộc sở hữu HVTC · Điều 16.1, tr.13 · [NGOÀI]

### 3.2 GreenScan: đã đo
- Hòa Phát 264 trang (BCPTBV 2025 và BCTN 2024): 107–121 s qua 3 lần chạy, RAM đỉnh 1.331 MB, i7-1355U 16 GB, không GPU, ngoại tuyến · `REPO\benchmark\queue_quality_2026-10-06.md`; `01_NOI_DUNG_TRINH_BAY.md` §4 · [ĐÃ THỰC NGHIỆM] (06/10; cần đo lại trên máy trình chiếu)
- 156 tuyên bố: 153 khớp một phần, 2 ủng hộ, 1 chưa đủ bằng chứng, 0 mâu thuẫn; hàng đợi 9/172 mục · "Số mới" §2 F1 (lượt `c892c13727c24bb9` ngày 22/10, giống lượt demo `cd5a82e3`) · [ĐÃ THỰC NGHIỆM]
- 127/156 tuyên bố Hòa Phát không có con số nào; 4/108 trang BCPTBV là ảnh quét · Hồ sơ nguyên lý §1.2, §1.4 · [ĐÃ THỰC NGHIỆM]
- Mâu thuẫn sai giảm từ 357/419 (17/09) xuống 0 sau khi có cổng so sánh · `CORE_FEATURE_TEST_REPORT_2026-09-20.md`; 01 §4 · [ĐÃ THỰC NGHIỆM]
- Cho GLM-5.2 tự quyết trên Hòa Phát: 10 CONTRADICTED và 2 CRITICAL, phần lớn sai · `REPO\benchmark\llm_stance_ab_2026-09-28.md` · [ĐÃ THỰC NGHIỆM] (28/09)
- Chạy ngoại tuyến thật: chặn mọi kết nối ra ngoài, chạy 264 trang, 0 lần hệ thống cố kết nối. Đối chứng: bật mô hình đám mây thì bộ chặn bắt 15 lần gọi · 01 §4 · [ĐÃ THỰC NGHIỆM] (09/10; script tạm, **chưa vào repo**)
- 4/4 ca có phán quyết quốc tế khớp (KLM, BNY Mellon, DWS, Keurig Dr Pepper) · `REPO\evaluation\real_cases.py`; 01 §4 · [ĐÃ THỰC NGHIỆM]
- 410 test được thu thập trong 37 tệp: 47 bẫy kết luận, 17 ca checklist kiểm toán, 15 test canh 10 bất biến, 15 test Studio, 12 test `irlib_ground` · `pytest --collect-only` ngày 04/11 · [ĐÃ THỰC NGHIỆM] (chỉ đếm, chưa chạy lại để xem pass/fail)
- Size ladder (51 ca: 32 ca sạch và 19 ca trang thật Hòa Phát; 5 mô hình từ 3,8B đến 753B):
  - luật đúng 20/32 và 7/19; các mô hình đúng 29–32/32 và 15–18/19; McNemar p ≤ 0,022;
  - khi đã kết luận, luật đúng 6/8 (ca dựng) và 3/3 (trang thật).
  - Nguồn: `MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md` §0; `REPO\benchmark\size_ladder_2026-10-10\` · [ĐÃ THỰC NGHIỆM] (ca do một người dựng có AI hỗ trợ; n nhỏ)
- Học trò T1 (e5-base): macro-F1 0,71–0,73, n = 1.217, 3 seed, kiểm định chéo theo công ty; F1 nhị phân 0,82 so với luật 0,61; 119 ms/câu trên CPU; **chưa nối vào sản phẩm** · `REPO\training\runs\kaggle_t1_v3\results.json`; "Số mới" §2 · [ĐÃ THỰC NGHIỆM] (nhãn Claude)
- GS-Bench v1.1: 453 ca (51 B-a và 402 B-b; S 95 / C 123 / N 184), 7 doanh nghiệp · `REPO\benchmark\gs_bench_v1\` · [ĐÃ THỰC NGHIỆM] (nhãn AI và đáp án theo cấu trúc)
- Luật trên B-b: độ phủ 0,028, precision 0,75, bắt 0/44 ca mâu thuẫn. Trên v1.1: 0 CONTRADICTED sai, 9 SUPPORTED sai · "Số mới" §10 (31/10) · [ĐÃ THỰC NGHIỆM]
- Trần IR đúng hoàn toàn + irlib trên B-b: độ phủ 0,528, precision 1,0, 0 kết luận sai · như trên · [ĐÃ THỰC NGHIỆM]
- AG-1, ngoài mẫu sạch v1.3 (87 ca): độ phủ luật 0,011 · 4B 0,138 · 8B 0,115 · 14B 0,115 · 32B 0,253; precision 1,0; 0 kết luận sai · "Số mới" §10 (01/11 17:00) · [ĐÃ THỰC NGHIỆM]
- AG-1, ngoài mẫu v1.1 (246 ca): độ phủ 4B/8B/14B/32B = 0,126 / 0,220 / 0,256 / 0,329 · "Số mới" §10 (31/10 22:40) · [ĐÃ THỰC NGHIỆM]
- `irlib.ground()` (bắt số model đọc phải khớp với câu gốc): 32B precision từ 0,817 lên 0,985, CONTRADICTED sai từ 7 xuống 1 (trong mẫu) · "Số mới" §10 (31/10 14:15) · [ĐÃ THỰC NGHIỆM]
- AG-2, luật + 4B, bỏ phiếu S đơn độc của luật:
  - tập G: 0,093 / 1,0 / 0 / 0; CI phần tăng độ phủ [0,016; 0,185];
  - tập hiệu chỉnh 388 ca: 0,242 / 0,989 / 1 / 0, luật có 8 SUPPORTED sai.
  - Nguồn: "Số mới" §10 (23:50) · [ĐÃ THỰC NGHIỆM] (trên G, 4B chỉ dám kết luận 15 ca)
- Bộ đọc Q4 cục bộ khớp 0,963 với bản bf16; luật + 4B Q4 trên G: 0 sai, độ phủ 0,080; 1,7 s/câu trên T4 · "Số mới" §10 (01/11 17:15) · [ĐÃ THỰC NGHIỆM]
- AG-3: Hòa Phát tr.39 dựng đủ 10 hàng, cộng dọc 3/3; trên 7 ca đúng 3/7, 0 sai; tiêu đề trang "NĂM 2024" lệch với bảng 2025 · "Số mới" §10 (01/11 17:40) · [ĐÃ THỰC NGHIỆM]
- Studio: neo được 147/156 tuyên bố, 391 đề xuất, 0 đề xuất thêm số · `REPO\tests\test_studio.py`; Hồ sơ nguyên lý §1.4 · [ĐÃ THỰC NGHIỆM] (14/10)
- Hàng đợi: người soát đồng ý 12/14 mục; khoảng 6/9 mục đúng · Hồ sơ nguyên lý §1.4 (lượt soát 11/10) · [ĐÃ THỰC NGHIỆM, SƠ BỘ] (một lượt soát nội bộ)
- Kho dữ liệu: 1.061 tài liệu, 21 doanh nghiệp, 670 bản gốc có SHA-256; 28 bộ án lệ (176 tài liệu); registry 11 văn bản · 01 §4 · [ĐÃ THỰC NGHIỆM] (đếm 09/10)
- Pháp lý: 0/156 tuyên bố có quy tắc áp được; bằng chứng 780/780 là tài liệu nội bộ; gold người 0/88 cặp, 0/79 câu · "Số mới" §2 F5–F7 · [ĐÃ THỰC NGHIỆM]
- Repo không có mã lượng tử (không có qiskit, pennylane, QAOA, ủ mô phỏng hay QUBO trong `.py`, `.toml`, `.ipynb`) · grep ngày 04/11 · [ĐÃ THỰC NGHIỆM]

### 3.3 Ngoài (thị trường, pháp lý, nghiên cứu)
- Dư nợ tín dụng xanh trên 704.244 tỷ đồng (31/3/2025), 58 tổ chức tín dụng, 4,3% tổng dư nợ, tăng bình quân trên 21,2%/năm (2017–2024) · số NHNN công bố 21/5/2025, theo Thanh Niên và VnBusiness; hồ sơ Vòng 1 Phần III.1 [1][2] · [NGOÀI] (nguồn thứ cấp; nói phải kèm nguồn, mục 5.3)
- 28,38% công ty trên HOSE có báo cáo phát triển bền vững (2024); 72,5% chỉ có thông tin định tính; 2/22 có bên thứ ba đảm bảo · Hąbek & Bui (2025), theo `REPO\docs\08-knowledge\03_THUC_TRANG_VA_NGHIEN_CUU_VN.md` §1 · [NGOÀI]
- 50,6% quan sát công bố khí nhà kính được 0 điểm · Lâm Thị Trúc Linh và cs. (2025), cùng nguồn · [NGOÀI]
- EC: 53,3% tuyên bố môi trường mơ hồ, gây hiểu lầm hoặc không căn cứ; 40% không được chứng minh · hồ sơ Vòng 1 [9][10] · [NGOÀI]
- KLM: tòa Hà Lan (2024) kết luận 15/19 tuyên bố gây hiểu nhầm · 01 S8 · [NGOÀI]
- QĐ 13/2024/QĐ-TTg: ban hành 13/8/2024, hiệu lực 01/10/2024, 2.166 cơ sở phải kiểm kê khí nhà kính · `02_PHAP_LY_VIET_NAM.md`; hồ sơ Vòng 1 [7][8] · [NGOÀI]
- NĐ 119/2025/NĐ-CP: hiệu lực 01/08/2025. Nhiệt điện, thép, xi măng kiểm kê 2 năm/lần từ năm 2026, có thẩm định độc lập, nộp trước 01/12 từ 2027 · `02_PHAP_LY_VIET_NAM.md` · [NGOÀI] (ngày hiệu lực đã sửa 06/10, chờ Thảo xác nhận)
- NĐ 83/2026/NĐ-CP (23/03/2026) chỉ sửa thủ tục về chất được kiểm soát (ô-dôn, HFC), không đụng tới kiểm kê khí nhà kính · như trên · [NGOÀI]
- QĐ 21/2025/QĐ-TTg: ban hành 04/7/2025, hiệu lực 22/8/2025. Dự án được xác nhận bởi cơ quan thẩm định hoặc tổ chức độc lập đạt ISO/IEC 17029 hoặc VSAE/ISAE 3000. Thẩm quyền ban hành danh mục đã chuyển cho Bộ trưởng Bộ NN&MT (NĐ 48/2026, Đ.31) · như trên · [NGOÀI]
- TT 17/2022/TT-NHNN (ban hành 23/12/2022, hiệu lực 01/06/2023): quản lý rủi ro môi trường trong hoạt động cấp tín dụng · như trên · [NGOÀI]
- TT 96/2020/TT-BTC, Phụ lục IV mục 6: 6.1 khí nhà kính, 6.2 vật liệu, 6.3 năng lượng, 6.4 nước, 6.5 số lần và số tiền bị phạt về môi trường, 6.8 thị trường vốn xanh. Bốn ngành tài chính được miễn 6.1–6.3 · như trên; 01 S4 · [NGOÀI]
- Dự thảo thông tư thay TT 96/2020 (25/09/2026), lấy ý kiến tới 07/10/2026, có phụ lục ESG riêng theo hướng "công bố hoặc giải trình" · `02_PHAP_LY_VIET_NAM.md` · [NGOÀI] (thứ cấp; chỉ gọi là "dự thảo")
- EU CBAM áp dụng chính thức từ 01/01/2026 cho thép, xi măng · 01 S4 · [KIẾN THỨC NỀN]
- PAL 72,0 so với 56,9; PoT trên FinQA từ 58,2 lên 74,0; MiniCheck 770M đạt 74,7 so với GPT-4 75,3; ESGReveal +21,8 điểm; Joren: 36–40% sai khi ngữ cảnh không đủ; Climate-FEVER: 77,69% trên FEVER còn 38,78% · Hồ sơ nguyên lý §2.2 · [NGOÀI] (đội ghi đã đọc bản gốc ngày 10/10)

### 3.4 Giả thuyết (chỉ nói kèm chữ "giả thuyết")
- Đọc tay một báo cáo 200–300 trang mất 8–12 giờ; dùng GreenScan còn 30 phút sàng lọc và khoảng 2 giờ rà · hồ sơ Vòng 1 Phần IV.3 · [GIẢ THUYẾT]
- Hệ thống khoanh 5–10% số claim vào nhóm rủi ro cao · như trên · [GIẢ THUYẾT]
- Truy xuất ngữ nghĩa (embedding, reranker) tăng độ phủ top-5 ít nhất 10 điểm mà không chậm quá 2 lần (ngưỡng ghi ngày 29/09) · 04 §1 · [GIẢ THUYẾT]
- QUBO chọn bằng chứng tốt hơn thuật toán tham lam hoặc MMR · hồ sơ Vòng 1 VII.3; 01 S13 · [GIẢ THUYẾT]
- Chi phí đám mây US$0,8–2,0 mỗi bộ hồ sơ (cho GLM-5.2 qua FPT, ước tính) · 01 §4 · [GIẢ THUYẾT] (đường này đang hỏng khoá)

---

## 4. Câu hỏi BGK dự kiến (24 câu)

*Trả lời theo công thức vấn đề → nguyên lý → GreenScan làm gì → giới hạn. Câu kỹ thuật chuyển Nhân, câu luật chuyển Thảo, câu nghiệp vụ kiểm toán chuyển Quỳnh. Mỗi số nói ra phải có trong mục 3.*

**Q1. [TC1 · mọi BGK] "Sau ba vòng, sản phẩm đã giải quyết được bài toán đặt ra ở Vòng 1 tới đâu?"**
- *Trả lời (≈50 s):* "Hồ sơ Vòng 1 đặt bài toán: kiểm chứng từng tuyên bố môi trường, truy vết tới trang, và không kết luận vượt bằng chứng. Chúng em chia bài toán thành các bước, mỗi bước có thước đo riêng. Phần đã làm được: đọc trọn 264 trang của Hòa Phát trong khoảng 2 phút trên laptop không GPU; mọi kết luận có trang và phép tính; 0 kết luận mâu thuẫn sai, cả trên Hòa Phát lẫn trên 87 ca kiểm tra ngoài mẫu; 4/4 vụ đã có phán quyết quốc tế ra đúng hướng. Phần chưa làm được, nói thẳng: đối chiếu pháp lý và nguồn độc lập chưa chạy (0 quy tắc áp được; 780/780 bằng chứng là tài liệu của chính doanh nghiệp), và chưa có số đo trên nhãn do người gán." Sau câu này mở slide "Hứa → Đạt" (mục 5.2).
- *Vặn tiếp:* "Vậy là chưa giải quyết triệt để?" → "Đúng. Phần đã giải là đọc, tìm, kiểm số và sắp hàng soát. Phần pháp lý và nguồn độc lập là việc của 6 tháng tới, có tiêu chí dừng ghi sẵn."
- *Bẫy:* liệt kê tính năng mà không đối chiếu ngưỡng Vòng 1; nói "đã hoàn thành MVP".

**Q2. [TC1/TC2 · AI] "Hệ thống chính xác bao nhiêu phần trăm?"**
- *Trả lời (≈50 s):* "Một con số phần trăm che mất hai loại lỗi có hậu quả rất khác nhau: kết luận sai 'mâu thuẫn' là vu oan doanh nghiệp, kết luận sai 'khớp' là bỏ lọt. Vì vậy chúng em đo riêng độ chính xác trên phần hệ thống dám kết luận và độ phủ. Trên 87 ca ngoài mẫu của bộ GS-Bench, đáp án sinh theo cấu trúc từ số liệu thật, mọi cấu hình có precision 1,0 và 0 kết luận sai. Độ phủ thì thấp: luật kết luận được 1,1% số ca, thêm bộ đọc 4B được 13,8%, bộ đọc 32B được 25,3%. Nếu bộ đọc hoàn hảo, trần là 52,8% với precision 1,0. Giới hạn: nhãn là nhãn AI có bộ kiểm tất định, chưa phải gold người gán độc lập; mẫu nhỏ."
- *Vặn tiếp:* "Độ phủ 14% thì 86% còn lại để làm gì?" → "Chuyển vào hàng đợi cho người soát, kèm danh sách còn thiếu gì. Trong kiểm toán, xác nhận sai đắt hơn một lần từ chối; mục tiêu là tăng độ phủ mà giữ vu oan bằng 0."
- *Bẫy:* nói "chính xác 100%"; lẫn precision với accuracy; quên nói n và nguồn nhãn.

**Q3. [TC1 · tài chính – kế toán, nhà đầu tư] "Tiết kiệm được bao nhiêu giờ, bao nhiêu tiền so với kiểm toán viên làm tay?" (Điều 6.5)**
- *Trả lời (≈40 s):* "Thể lệ yêu cầu so với cách truyền thống, và chúng em chỉ nói số đo trên người. Phần máy đã đo: đọc 264 trang trong 107–121 giây, rút 156 tuyên bố thành hàng đợi 9 mục ưu tiên, mục nào cũng có lý do. Phần người chưa đo. Giao thức đo đã sẵn: 20 tuyên bố, một người làm tay, một người dùng GreenScan, đo số phút mỗi tuyên bố và số bằng chứng tìm đúng. Con số '8–12 giờ xuống 30 phút cộng 2 giờ' trong hồ sơ Vòng 1 là giả thuyết, chưa phải kết quả." *(Nếu trước 10/11 đo được dù mẫu nhỏ: thay bằng số thật và nêu n.)*
- *Vặn tiếp:* "Không có số thì sao biết đáng tiền?" → "Thứ người dùng trả tiền là phút công của kiểm toán viên. Chúng em đề xuất một pilot miễn phí để đo đúng con số đó trước khi bán."
- *Bẫy:* nhắc "2 ngày → 2 phút" của kịch bản cũ; lấy giờ công nhân lương để ra "tiết kiệm X tỷ".

**Q4. [TC1 · mọi BGK] "153/156 tuyên bố 'khớp một phần': kết quả phẳng như vậy thì giúp được gì?"**
- *Trả lời (≈45 s):* "Kết luận giống nhau thì không giúp ai quyết định, chúng em đồng ý. Nguyên nhân đã đo được: 127/156 tuyên bố không có con số nào; chưa có nguồn độc lập; chưa có quy tắc pháp lý; và luật của chúng em phủ hẹp. Giá trị hôm nay nằm ở thứ tự: 9 trong 172 mục nên mở trước, mục nào cũng có lý do và danh sách thiếu (số liệu, kỳ, năm gốc, phạm vi). Phần đang sửa: bộ đọc số liệu kết hợp thư viện so sánh tất định để tăng độ phủ mà vẫn 0 vu oan; nguồn độc lập ưu tiên là Climate TRACE, Global Energy Monitor cho thép và xi măng, và danh mục cơ sở của QĐ 13/2024."
- *Vặn tiếp:* "Phẳng là do hệ thống kém?" → "Một phần, và chúng em tách được phần đó: trên bộ đo có đáp án, luật chỉ dám kết luận 2,8% số ca số liệu. Đó là lỗi của hệ thống, không phải của báo cáo."
- *Bẫy:* đổ hết cho "thực trạng công bố".

**Q5. [TC1/TC2 · doanh nghiệp, nhà đầu tư] "Khác gì MSCI hay Refinitiv, ChatGPT, hoặc một công ty Big4?"**
- *Trả lời (≈45 s):* "MSCI hay Refinitiv chấm doanh nghiệp bằng một điểm tổng; một điểm ESG không cho biết câu nào trong báo cáo cần soát. GreenScan kiểm từng tuyên bố, chỉ ra trang, phép tính và thứ còn thiếu, biết từ chối, và chạy trên máy của đơn vị. Với ChatGPT: chúng em đã thử có đối chứng. Cho GLM-5.2, mô hình khoảng 750 tỷ tham số, tự quyết trên báo cáo Hòa Phát thì ra 10 'mâu thuẫn' và 2 'nghiêm trọng', phần lớn sai; một dòng bảng vỡ bị đọc thành '100% nam giới'. Với Big4: GreenScan là công cụ cho chính họ dùng, làm các bước cơ học (đọc dò, lật tìm số, ghi giấy làm việc), còn xét đoán và ký vẫn là của con người."
- *Vặn tiếp:* "Đã so trực tiếp với ChatGPT trên cùng tài liệu chưa?" → So trên 51 ca có đáp án: mô hình đúng nhiều hơn luật (29–32/32 so với 20/32) vì luật phủ hẹp, nhưng mô hình xác nhận sai khi bảng mất cấu trúc. Màn đặt cạnh một LLM chung trên 20 tuyên bố Hòa Phát đã có trong kế hoạch 14/10 [CHƯA XÁC MINH đã làm].
- *Bẫy:* chê đối thủ; nói "Big4 không làm được".

**Q6. [TC2 · AI; câu thật của giảng viên 10/10] "Mô hình của nhóm quá bé / sao không cho LLM lớn đọc cả báo cáo rồi kết luận?"**
- *Trả lời (≈55 s):* "Câu hỏi đúng là lỗi nằm ở bước nào. Chúng em đo từng bước.
  - Một: trên 51 ca với 5 mô hình từ 3,8 tỷ đến 753 tỷ tham số, ở bước kiểm chứng từng cặp không thấy khác biệt theo kích thước. Khi bảng bị dàn phẳng, mọi mô hình, kể cả mô hình 753 tỷ, đều tự tin xác nhận sai.
  - Hai: ở bước đọc số liệu (31/10), mô hình lớn hơn dám đọc nhiều hơn: độ phủ của 4B, 8B, 14B, 32B lần lượt là 0,126, 0,220, 0,256, 0,329. Nhưng sự an toàn đến từ lớp so sánh tất định: trước khi có bước kiểm số với câu gốc, 32B có 7 mâu thuẫn sai; sau đó còn 1.
  
  Kết luận: kích thước mua độ phủ, không mua an toàn. Vì vậy mô hình đọc, mã quyết, người ký. Giới hạn: mẫu nhỏ, nhãn AI."
- *Vặn tiếp:* "Thế sao không dùng luôn 32B?" → "32B cần GPU hoặc đám mây, trong khi giấy làm việc kiểm toán không được rời máy. Trên tập G, 32B có 1 xác nhận sai. Bản 4B lượng tử hoá chạy cục bộ khớp 96,3% với bản gốc."
- *Bẫy:* nhắc lại "kích thước không quan trọng" (đã bị bác ở độ phủ); nói GLM-5.2 đang chạy trong sản phẩm (khoá hỏng từ 31/10).

**Q7. [TC2 · AI, kế toán] "Chưa có người gán nhãn: các em tự gán rồi tự chấm?"**
- *Trả lời (≈55 s):* "Thước đo phải độc lập với hệ được đo. Chúng em làm ba việc:
  - Đáp án sinh theo cấu trúc. GS-Bench có 453 ca: 51 ca dựng tay, 402 ca sinh từ số liệu thật bằng biến đổi có kiểm soát. Đổi đơn vị, phạm vi hay kỳ thì đáp án là 'không so được'; đổi giá trị vượt dung sai thì đáp án là 'mâu thuẫn'. Giống như kiểm thử phần mềm. Số liệu gốc do Claude đọc, bộ kiểm tất định soát lại, 14 ca soát tay.
  - Ngưỡng và dự đoán ghi vào cấu hình trước khi chạy; tập kiểm tra giữ riêng theo công ty.
  - Công bố cả dự đoán sai. Ví dụ: chúng em dự đoán dựng lại bảng sẽ đúng ít nhất 5/7 ca, thực tế được 3/7.
  
  Giới hạn: bộ này đo phần kiểm số, chưa đo khả năng hiểu câu định tính. Gold do người gán vẫn là 0/88 cặp tính tới 31/10."
- *Vặn tiếp:* "Hồ sơ Vòng 1 cam kết 100 cặp gold, κ ≥ 0,7. Đâu rồi?" → "Chưa đạt. Đường găng là người gán; chúng em không ước lượng thay. [Cập nhật nếu có số trước 10/11.]"
- *Bẫy:* gọi κ 0,92 là đồng thuận giữa người (thực ra là giữa hai lượt Claude); nói "đã có gold".

**Q8. [TC2 · AI] "Bảng trong PDF bị vỡ cấu trúc thì sao?"**
- *Trả lời (≈40 s):* "Đây là lỗi lớn nhất đã đo: khi bảng bị dàn phẳng, mọi mô hình từ 26 tỷ tham số trở lên đều báo 'khớp' sai trên cùng một bảng khí nhà kính. Lúc đó biểu diễn đầu vào quan trọng hơn số tham số. Ngày 01/11 chúng em dựng lại hàng của bảng từ toạ độ chữ: trang 39 của Hòa Phát dựng đủ 10 hàng, cộng dọc 3/3 khớp; trên 7 ca, hệ thống đúng 3/7 và không sai ca nào. Chúng em đã dự đoán ít nhất 5/7 nên dự đoán này sai; nguyên nhân là thiếu chiều 'mảng kinh doanh'."
- *Vặn tiếp:* "Có phát hiện gì trên bảng đó không?" → "Tiêu đề trang ghi 'NĂM 2024' nhưng bảng ghi 2025. Hệ thống đưa điểm này cho người soát xem, không kết luận gì về doanh nghiệp."
- *Bẫy:* nói "đã xử lý được bảng"; nói "Hòa Phát ghi sai".

**Q9. [TC2 · kế toán, doanh nghiệp] "Dữ liệu lấy từ đâu, có hợp pháp không, đã đủ đại diện chưa?"**
- *Trả lời (≈40 s):* "Báo cáo thường niên và báo cáo bền vững là tài liệu doanh nghiệp bắt buộc công bố theo TT 96. Kho của chúng em có 1.061 tài liệu từ 21 doanh nghiệp niêm yết, 670 bản gốc có mã băm SHA-256. Chúng em không phát tán lại PDF; repo chỉ lưu siêu dữ liệu, đường dẫn và mã băm. Về đại diện, nói thẳng là chưa đủ: chạy đầu–cuối mới có một doanh nghiệp, ngành thép; bộ đo số liệu có 7–9 doanh nghiệp. Từ 17/09 chúng em đã chuyển hướng sang các doanh nghiệp phát thải cao."
- *Vặn tiếp:* "Mô hình nhúng có vướng giấy phép không?" → "Vietnamese_Embedding công bố hai giấy phép khác nhau ở hai nơi, và vài bộ dữ liệu tham khảo là phi thương mại, nên chúng chưa nằm trong cấu hình mặc định."
- *Bẫy:* nói "dữ liệu lớn", hoặc nói về 30–80 nghìn đoạn văn (hồ sơ Vòng 1, chưa đếm).

**Q10. [TC3 · mọi BGK] "Cho chạy thử một tài liệu khác ngay bây giờ được không? Bản scan, bản Word?"**
- *Trả lời (≈30 s):* "Được. Nút 'Điền ví dụ' chạy trong vài giây. Từ 14/10 hệ thống nhận PDF, DOCX và HTML. Màn xem trước báo trước trang nào sẽ mất chữ. Trang quét cần OCR (tesseract) trên máy." Không chạy lại 264 trang trước hội đồng, trừ khi được yêu cầu (mất khoảng 2 phút).
- *Vặn tiếp:* "Xuất lại PDF có giữ bố cục gốc không?" → "Không. Giao diện ghi rõ giới hạn này; bản DOCX có tracked changes thì giữ nguyên các đoạn không đổi."
- *Bẫy:* đưa scan vào khi máy demo chưa cài tesseract. **Kiểm máy demo trước 10/11.**

**Q11. [TC3 · doanh nghiệp] "Người dùng thật dùng có dễ không? Đã đo trải nghiệm chưa? Cài đặt lại có khó không?"**
- *Trả lời (≈40 s):* "Giao diện đi theo thói quen làm việc: hàng đợi soát, bằng chứng mở đúng trang được tô sáng, Studio gạch dưới từng tuyên bố như trình soạn mã, phím tắt F8 để sang tuyên bố kế tiếp, Ctrl+Enter để chấp nhận đề xuất. Đo trải nghiệm thì chưa: chưa có điểm SUS, chưa đo thời gian thao tác. Kế hoạch là 3–5 người, ngưỡng SUS 70. Cài đặt: một tệp GreenScan.bat hoặc lệnh `quantum-agent app`; một cổng phục vụ cả giao diện và API." Riêng Docker: tính tới 14/10 chưa build thử [kiểm lại].
- *Vặn tiếp:* "Ai đã dùng thử?" → chỉ nói người thật và số thật.
- *Bẫy:* nói "người dùng khen dễ dùng".

**Q12. [TC1/TC3 · doanh nghiệp, kế toán] "Tên đề tài có 'tự động tư vấn cải thiện báo cáo'. Làm được chưa?"**
- *Trả lời (≈50 s):* "Làm được phần có căn cứ, qua GreenScan Studio từ 14/10. Với mỗi tuyên bố, hệ thống đưa đề xuất sửa theo 4 loại quy tắc:
  - thêm phạm vi, kỳ, năm gốc;
  - thay câu mơ hồ bằng chỗ trống '[bổ sung: …]';
  - thêm dẫn chiếu tới bằng chứng đã tìm thấy;
  - làm nhẹ lời nói quá.
  
  Mọi đề xuất phải qua phép kiểm 'không thêm số': số trong câu mới phải có sẵn trong câu cũ hoặc trong trích dẫn. Trên Hòa Phát, Studio neo được 147/156 tuyên bố, sinh 391 đề xuất, không đề xuất nào thêm số. Kết quả xuất ra DOCX có tracked changes. Giới hạn: đề xuất theo khuôn, chưa đo mức hữu ích với người dùng, chưa làm cho BCTC, và không tư vấn chiến lược ESG."
- *Vặn tiếp:* "Vậy là giúp doanh nghiệp viết khéo hơn để qua mặt?" → "Không. Đề xuất chỉ thêm điều kiện hoặc chỗ trống đòi số liệu, không bao giờ bịa số. Tài liệu bằng chứng bị khoá chỉ đọc, mọi sửa đổi đều để lại vết."
- *Bẫy:* nói "AI viết lại báo cáo"; nói Studio đã có người dùng.

**Q13. [TC4 · nhà đầu tư, doanh nghiệp] "Chi phí triển khai, vận hành và bảo trì là bao nhiêu?"**
- *Trả lời (≈45 s):* "Chế độ mặc định chạy ngoại tuyến: 0 đồng ngoài máy tính, laptop 8–16 GB là đủ, RAM đỉnh 1,3 GB. Chế độ đám mây chỉ dùng cho tài liệu đã công bố. Trước đây chúng em dùng GLM-5.2 qua FPT, ước tính 0,8–2 đô-la một bộ hồ sơ; khoá hết hạn từ 31/10 nên nay không còn là cấu hình demo; phương án thay là Groq gpt-oss-120b, chi phí chưa đo. Khoản tốn nhất là con người: chuyên gia pháp lý viết và duyệt quy tắc, cập nhật registry khi luật đổi." [CHƯA có ước tính giờ công: nên ước tính trước 10/11.]
- *Vặn tiếp:* "Bảo trì khi luật đổi có phải huấn luyện lại không?" → "Không. Luật mới tạo ra phiên bản mới của bộ quy tắc, và manifest của mỗi lượt chạy ghi phiên bản đã dùng."
- *Bẫy:* nói số chi phí đám mây cũ như số hiện hành.

**Q14. [TC4 · nhà đầu tư] "Đã có đối tác hay đơn vị dùng thử chưa?"**
- *Trả lời (≈25 s):* chỉ nói điều có văn bản. Repo chưa ghi đối tác hay pilot nào [CHƯA XÁC MINH]. Nếu vẫn chưa có: "Chưa có đối tác xác nhận. Chúng em đã mời [ai, ngày nào]. Mục tiêu là một buổi thử với kiểm toán viên thật để đo thời gian soát, trong tháng 11–12."
- *Vặn tiếp:* "Vì sao chưa có?" → "Chúng em ưu tiên có số đo trước khi mời đơn vị đặt tài liệu thật vào hệ thống."
- *Bẫy:* nói "đang làm việc với X" khi chưa có email hay biên bản. Thể lệ chỉ cho mức 90–100 khi "có đối tác xác nhận".

**Q15. [TC4/TC2 · doanh nghiệp, ngân hàng, AI] "Ngân hàng hay công ty có quy định nội bộ riêng. Đưa vào được không? Có phải huấn luyện lại mô hình?"**
- *Trả lời (≈50 s):* "Quy định không nên nằm trong trí nhớ của mô hình, vì như vậy không kiểm được và không biết hiệu lực từ ngày nào. GreenScan lưu quy định dưới dạng policy-as-code. Văn bản được đăng ký vào registry kèm ngày hiệu lực và chuỗi sửa đổi. Mỗi quy tắc ghi điều kiện, căn cứ tới điều và khoản, người duyệt (`reviewed_by`), kèm một ca đúng, một ca sai và một ca biên. Quy tắc chưa có người ký chỉ hiện là 'căn cứ ứng viên'. Thêm quy định nội bộ nghĩa là thêm văn bản và quy tắc vào kho này, giống bộ nhớ quy trình của agent, không cần huấn luyện lại. Thiếu quy tắc thì hệ thống ra 'cần người xem', không bao giờ ra 'phù hợp'. Giới hạn: hạ tầng đã có, nhưng quy tắc pháp lý thật hiện chưa áp được trên tuyên bố nào, và chưa có giao diện soạn quy tắc cho người dùng cuối [CHƯA XÁC MINH]."
- *Vặn tiếp:* "Vậy LLM có đọc tài liệu nội bộ không?" → "Mô hình chỉ đọc để tìm và trích; quyết định áp quy tắc là của mã, có phiên bản."
- *Bẫy:* nói "LLM đọc tài liệu nội bộ rồi tự hiểu và áp dụng".

**Q16. [TC4/TC5 · doanh nghiệp, ngân hàng] "Bảo mật dữ liệu thế nào? Nói chạy ngoại tuyến thì chứng minh ra sao?"**
- *Trả lời (≈45 s):* "Tài liệu chia ba lớp: A là tài liệu công khai, dùng được mọi chế độ; B là tài liệu nội bộ chưa công bố, chỉ chạy ngoại tuyến hoặc trên máy chủ của đơn vị; C là giấy làm việc kiểm toán, chỉ chạy ngoại tuyến. Căn cứ là Luật Bảo vệ dữ liệu cá nhân 91/2025, NĐ 356/2025 và nghĩa vụ bảo mật hồ sơ kiểm toán [điều khoản Luật Kiểm toán độc lập: CHƯA XÁC MINH]. Chứng minh ngoại tuyến bằng ba cách: chặn mọi kết nối ra ngoài rồi chạy cả 264 trang, có 0 lần hệ thống cố kết nối, còn bật đám mây thì bộ chặn bắt được 15 lần gọi; manifest của phiên demo không có lời gọi mô hình nào; và tắt Wi-Fi ngay trước hội đồng."
- *Vặn tiếp:* "Script chặn đó có trong repo không?" → "Chưa, đó là script tạm ngày 09/10. Chúng em sẽ đưa thành kiểm thử hồi quy."
- *Bẫy:* nói "không bao giờ dùng đám mây" (vẫn có chế độ đám mây cho tài liệu lớp A).

**Q17. [TC5 · mọi BGK] "Nếu hệ thống sai, làm hại uy tín doanh nghiệp thì sao? Có thiên vị không?"**
- *Trả lời (≈50 s):* "Có hai loại sai. Với vu oan, chúng em có ba lớp chặn: không có chữ 'vi phạm' và không xếp hạng doanh nghiệp; chỉ kết luận 'mâu thuẫn' khi có số cùng điều kiện hoặc nguồn có thẩm quyền; người soát chốt và được ghi tên. Kết quả đo: 0 mâu thuẫn sai. Với bỏ lọt, chúng em thừa nhận luật của mình từng xác nhận sai 8–9 ca trên bộ đo, nên đã đổi chính sách: không chấp nhận phiếu 'khớp' đơn độc của luật. Trên tập kiểm tra, cách này còn 0 xác nhận sai. Về thiên vị: dữ liệu hiện lệch về ngành thép; mỗi quy tắc khai rõ ngành áp dụng, ví dụ bốn ngành tài chính được miễn mục 6.1–6.3 của TT 96. Doanh nghiệp nhỏ thường công bố định tính nên hay nhận 'chưa đủ bằng chứng'; đó không phải kết luận tiêu cực."
- *Vặn tiếp:* "Tài liệu cài lệnh độc (prompt injection) thì sao?" → "Nội dung tài liệu là dữ liệu không tin cậy, không phải chỉ dẫn; có chính sách loại bỏ và có test."
- *Bẫy:* nói "hệ thống không bao giờ sai"; giấu số bỏ lọt.

**Q18. [TC6 · mọi BGK; Điều 14] "Nhóm dùng AI tạo sinh ở những đâu trong bài thi?"**
- *Trả lời (≈45 s):* "Chúng em khai báo đủ trong báo cáo và slide phụ lục:
  - Claude Code hỗ trợ viết, rà soát và kiểm thử mã, soạn nháp tài liệu; lịch sử commit ghi đồng tác giả.
  - Claude gán nhãn dữ liệu: 1.217 câu cho học trò T1 và phần đọc số liệu của GS-Bench. Đây là dữ liệu, có bộ kiểm tất định và người duyệt.
  - Công cụ sinh ảnh dùng cho hình minh hoạ.
  - Qwen3 và gpt-oss là thành phần của sản phẩm.
  
  Phần của nhóm: đặt bài toán, thiết kế kiến trúc và luật kiểm chứng, chọn dữ liệu, đọc và chấp nhận từng thay đổi, chạy và diễn giải mọi phép đo. Mỗi đoạn mã chúng em đều giải thích được."
- *Vặn tiếp:* "Giải thích đoạn này cho tôi?" → người phụ trách mở đúng tệp (`numeric_facts.eligibility`, `irlib.ground`, `studio/suggest.py`).
- *Bẫy:* phủ nhận dùng AI; không giải thích được mã khi bị chỉ vào (BGK có quyền yêu cầu xem mã theo Điều 9).

**Q19. [Lượng tử · chuyên gia lượng tử] "Lượng tử nằm ở đâu? Nhóm đã chạy QAOA chưa?"**
- *Trả lời (≈40 s):* "Chưa. Chúng em nói thẳng: sản phẩm không có phần lượng tử. Một bài toán con có cấu trúc tổ hợp thật: chọn k đoạn bằng chứng phủ đủ 5 thuộc tính mà ít trùng lặp. Chúng em đã viết nó dưới dạng QUBO; bài này ánh xạ được sang mô hình Ising, khoảng 30–50 qubit logic. Kế hoạch so bốn cách: top-k, tham lam hoặc MMR, quy hoạch nguyên chính xác, và ủ mô phỏng hoặc QAOA trên trình mô phỏng. Chưa có dòng mã nào, và chúng em không tuyên bố quantum advantage."
- *Vặn tiếp 1:* "Vậy sao dự thi AI-Quantum?" → "Thể lệ cho phép 'AI hoặc/và Lượng tử' (Điều 6.3), và Điều 10 nói công nghệ phức tạp không tự thân được điểm."
- *Vặn tiếp 2:* "Tên gói `quantum_gw`, biến `QUANTUM_PROFILE`?" → "Đó là tên dự án đặt theo cuộc thi, không có tính toán lượng tử nào."
- *Bẫy:* nói "QAOA của nhóm" hay "quantum-inspired" như đã chạy; nhận đề cử giải Lượng tử.

**Q20. [Tài chính – kế toán] "GreenScan có thay kiểm toán viên hay đơn vị đảm bảo theo ISAE 3000 / ISSA 5000 không?"**
- *Trả lời (≈45 s):* "Không. Đảm bảo là xét đoán nghề nghiệp có người ký. GreenScan làm các thủ tục cơ học: đọc dò tìm tuyên bố, đối chiếu, tính lại, ghi giấy làm việc, và nói rõ 'những gì không kiểm và vì sao'. Nhu cầu đang tăng: từ dữ liệu năm 2026, NĐ 119/2025 yêu cầu thép, xi măng, nhiệt điện kiểm kê có thẩm định độc lập, trong khi nghiên cứu của Hąbek & Bui cho thấy chỉ 2/22 báo cáo có bên thứ ba đảm bảo. Giới hạn: chưa đo trên một hồ sơ đảm bảo thật."
- *Vặn tiếp:* "Năm thuộc tính có phải là cơ sở dẫn liệu không?" → "Gần với chúng: chính xác, đúng kỳ, phân loại, đầy đủ. Riêng năm gốc là tính so sánh được, không phải một cơ sở dẫn liệu chuẩn." *(Slide Bán kết S5 nói "chính là", cần sửa.)*
- *Bẫy:* nói "đáp ứng yêu cầu ISAE 3000 / ISSA 5000" hay "kiểm toán ESG" (kịch bản cũ). Nên gọi là "dịch vụ đảm bảo".

**Q21. [Pháp lý · Thảo] "QĐ 21/2025 và luật Việt Nam được áp dụng thế nào? Đang có bao nhiêu quy tắc chạy?"**
- *Trả lời (≈45 s):* "Registry có 11 văn bản, ghi ngày hiệu lực và chuỗi sửa đổi; hệ thống kiểm được theo luật tại thời điểm tuyên bố hoặc theo luật hiện hành. Nhưng hiện chưa có quy tắc nào áp được trên 156 tuyên bố: bộ quy tắc vn-green-v0.1 vẫn là bản nháp. Nhờ thiết kế 'đóng khi thiếu', hệ thống không bao giờ báo 'phù hợp' sai. QĐ 21 chỉ áp cho dự án xin xác nhận thuộc danh mục phân loại xanh để hưởng ưu đãi tín dụng hoặc trái phiếu xanh, và việc xác nhận do tổ chức độc lập làm. Ba quy tắc ưu tiên tiếp theo: đối tượng kiểm kê theo QĐ 13 và lịch theo NĐ 119; mục 6 Phụ lục IV TT 96, có miễn trừ 6.1–6.3 cho bốn ngành tài chính."
- *Vặn tiếp:* "TT 17/2022 nói về gì?" → "Quản lý rủi ro môi trường trong cấp tín dụng của tổ chức tín dụng, hiệu lực 01/06/2023. Nó không nói về kiểm kê khí nhà kính."
- *Bẫy:* nói "QĐ 21 có 7 nhóm ngành, 45 lĩnh vực, bắt buộc giấy phép môi trường" (chưa đối chiếu Phụ lục I); nói "TT 17 về kiểm kê khí nhà kính", "NĐ 06/2022 về bảo vệ môi trường" (cả hai đều sai, có trong kịch bản cũ).

**Q22. [Nhà đầu tư] "Ai trả tiền, thị trường lớn cỡ nào, lộ trình thương mại hoá ra sao, ai sở hữu sản phẩm?"**
- *Trả lời (≈50 s):*
  - **Ba nhóm khách hàng:** công ty kiểm toán và đảm bảo ESG; ngân hàng thẩm định tín dụng xanh (theo TT 17); doanh nghiệp niêm yết tự soát trước khi công bố.
  - **Lực kéo nhu cầu:** 2.166 cơ sở phải kiểm kê; thẩm định độc lập theo NĐ 119; CBAM từ 2026; dự thảo thay TT 96 có phụ lục ESG.
  - **Lộ trình:** pilot 11–12/2026 để đo thời gian soát; Q1/2027 viết quy tắc pháp lý; Q2/2027 mở rộng sang thép, xi măng, nhiệt điện.
  - **Hình thức bán:** cài tại máy của đơn vị, vì tài liệu không rời máy. Cách tính phí cụ thể [GIẢ THUYẾT, đội cần chốt].
  - **Sở hữu:** theo Điều 16 thể lệ, sản phẩm đạt giải nếu được chọn phát triển thuộc HVTC; chúng em sẵn sàng phát triển theo cơ chế ươm tạo.
- *Vặn tiếp:* "Quy mô thị trường bao nhiêu tiền?" → không bịa con số. Chỉ nói số đối tượng có nghĩa vụ (2.166 cơ sở; 28,38% công ty HOSE có báo cáo bền vững).
- *Bẫy:* bịa quy mô thị trường hay doanh thu; nói "mã nguồn mở Apache-2.0" mà không nhắc Điều 16.

**Q23. [AI · agent] "Hệ thống có phải AI agent không? Memory, planning nằm ở đâu?"**
- *Trả lời (≈45 s):* "Chúng em theo khuyến nghị V1 trong tài liệu tập huấn: một bộ điều phối duy nhất và các công cụ chuyên biệt, chưa dùng đa tác tử tự trị, vì kiểm toán cần tái lập được.
  - Planning là đường ống 9 bước có điều kiện dừng; thiếu bằng chứng thì dừng và chuyển người.
  - Memory có ba loại: ngữ nghĩa (registry văn bản, từ điển), quy trình (bộ quy tắc, chính sách so sánh, rubric có phiên bản), sự kiện (nhật ký chỉ ghi thêm các quyết định của người soát).
  - Tự kiểm là cổng trích dẫn, cổng so sánh và hàng đợi người.
  
  Từ ZAIC chúng em mượn cách hai đường đọc độc lập kiểm chéo nhau, có cổng đồng thuận. Agent tìm bằng chứng nhiều bước chỉ làm khi số đo chỉ ra điểm mất nằm ở truy xuất."
- *Vặn tiếp:* "Sao không dùng đa tác tử cho hiện đại?" → "Chỉ thêm agent khi đo được lợi ích. Đó là bất biến kiến trúc của chúng em, và cũng là tinh thần Điều 10 thể lệ."
- *Bẫy:* phóng đại thành "hệ đa tác tử".

**Q24. [Bẫy tổng hợp · mọi BGK] "Hồ sơ và slide cũ nói 'cổng 7 điều kiện', 'lộ trình FDI 6 bước', 'reranker', 'chuyên gia ESG đã duyệt'. Những thứ đó đâu?"**
- *Trả lời (≈40 s):* "Từ 09/10, chúng em đã thu hẹp lời hứa cho khớp với sản phẩm và ghi rõ vì sao.
  - Cổng so sánh hiện kiểm đơn vị và 6 chiều; điều kiện 'khung chuẩn mực' trong kịch bản cũ chưa làm.
  - Lộ trình FDI 6 bước là cách kể chuyện, không phải tính năng; chúng em đã bỏ.
  - Reranker có sẵn nhưng chỉ bật khi đo được độ phủ tăng ít nhất 10 điểm.
  - Chưa có chuyên gia ESG ngoài nhóm duyệt kết quả.
  
  Chúng em có bảng 'Hứa → Đạt' để hội đồng xem."
- *Vặn tiếp:* "Sao lúc đầu lại hứa?" → "Hồ sơ Vòng 1 là thiết kế đích; khi đo, chúng em thấy một số phần chưa đứng vững nên không đưa vào sản phẩm."
- *Bẫy:* chống chế, hoặc khẳng định vẫn có.

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ so với kết quả 31/10–01/11, điều không được nói

### 5.1 Câu trả lời cũ đã sai hoặc lỗi thời

| Tài liệu (câu) | Bản cũ nói | Sự thật mới (nguồn) | Nói thay bằng |
|---|---|---|---|
| QA_BANK, GreenScan_100 (quy tắc 2) | 233 test · 21 bẫy · Hòa Phát 210 claim, CONTRADICTED 4% · gold 5 claim | 410 test, 47 bẫy (collect 04/11) · 156 claim, 0 CONTRADICTED · gold người 0 ("Số mới" F7) | Số ở mục 3.2 |
| 01 S11, 04 TC4 | 359 kiểm thử (47 · 17 · **15 bất biến**) | 410; con số 15 là **số test** canh **10 bất biến** | "10 bất biến, 15 test canh" |
| Hồ sơ nguyên lý §1.4 | 385 test | 410 (04/11) | 410, ghi ngày |
| Hồ sơ nguyên lý §2; MO_HINH §0 | "Không phát hiện tác động của kích thước" | Chỉ đúng ở bước kiểm chứng cặp. Ở bước đọc IR, độ phủ tăng theo cỡ: 0,126 → 0,329 ("Số mới" 31/10 22:40) | "Kích thước mua độ phủ, không mua an toàn" |
| 04 TC3 | "Luật gần như không bao giờ xác nhận sai" | Luật có 9 SUPPORTED sai trên v1.1 và 8 trên tập hiệu chỉnh ("Số mới" §10) | "Luật chưa vu oan lần nào, nhưng có bỏ lọt; đã sửa bằng cách bỏ phiếu S đơn độc" |
| Hồ sơ nguyên lý §2.1 | "Bộ luật hiếm khi sai khi đã kết luận" | 6/8 và 3/3 (size ladder); precision 0,75 trên B-b | Nói số, không nói "hiếm khi" |
| 04 TC5; 01 S12; Hồ sơ nguyên lý §1.3 | Chế độ đám mây GLM-5.2; US$0,8–2,0; 632 s | Khoá FPT 401 từ 31/10; đám mây chuyển sang Groq gpt-oss-120b (thử nghiệm, chỉ tài liệu công khai) | "Chế độ đám mây đã thử 28/09; demo chạy ngoại tuyến" |
| 04 TC5 | "8B mất 98 s một lời gọi, nên hướng đúng là bộ phân loại dưới 1B" | Qwen3-4B Q4 cục bộ khớp 0,963, 1,7 s/câu trên T4; chưa đo trên laptop; chưa vào sản phẩm | Số mới, kèm chữ "chưa vào sản phẩm" |
| 04 TC2 | "Lô đầu 20 cặp, hai người gán độc lập để đo κ" | Chưa làm (0/88) | "Chưa có gold người" |
| QA_DRILL #11; 01 S11 | "≥ 60 cặp trước 10/10", "Gold ≥ 60, κ ≥ 0,7 (đang đo)" | Không đạt | Nói thẳng |
| QA_DRILL #3, #24; QA_BANK Q13–Q15 | Reranker 30→5; BGE-M3 | BM25 + n-gram ký tự + RRF; lấy 30 giữ 5; dense và reranker tắt | Lời trong 04 §1 |
| QA_DRILL #7 | LLM chuẩn hoá 5 thuộc tính | Chuẩn hoá bằng luật | Lời trong 04 §1 |
| QA_DRILL #16 | NĐ 83/2026 sửa NĐ 06/2022, áp cho tuyên bố phát thải | Chỉ sửa phần chất được kiểm soát | Lời trong 04 §1 |
| QA_BANK Q74 | "Người dùng đầu tiên là ngân hàng" | Bán kết chọn kiểm toán viên; Vòng 1 chọn doanh nghiệp tự soát | Một câu thống nhất ở 5.3 |
| QA_BANK Q48 | Demo chạy dung sai 0,12, ngưỡng 0,35 | Dung sai theo độ chính xác công bố; ngưỡng 0,35 là lỗi F4/Q3 (che chênh lệch 9–25%) [CHƯA XÁC MINH đã sửa] | Kiểm `configs` trước khi nói |
| AI-Q2026 slide 11 | Hòa Phát "Scope 1+2 năm 2023, BCPTBV 2023 trang 47", "Reviewer: Chuyên gia ESG 22/09/2025" | Số nằm ở bảng khí nhà kính tr.39 BCPTBV 2025; tiêu đề trang ghi "NĂM 2024" còn bảng ghi 2025; không có chuyên gia ESG nào duyệt | "Bảng khí nhà kính trang 39, BCPTBV 2025", không khẳng định năm phát thải |
| AI-Q2026 slide 7, 9 | "TT 17/2022 về kiểm kê khí nhà kính"; "NĐ 06/2022 về bảo vệ môi trường" | TT 17 là quản lý rủi ro môi trường trong cấp tín dụng; NĐ 06 là giảm nhẹ phát thải khí nhà kính và bảo vệ tầng ô-dôn (hồ sơ Vòng 1 [6][8]; `02_PHAP_LY_VIET_NAM.md`) | Tên đúng |
| AI-Q2026 slide 3 | "Bộ Tài chính dự kiến bắt buộc công bố ESG từ 2026" | Chỉ có dự thảo thay TT 96 (lấy ý kiến tới 07/10/2026) [thứ cấp] | "Có dự thảo", không nói "bắt buộc từ 2026" |
| 01 S10 | "Đã gán [n] cặp, κ = [ ]" | 0 | "Chưa có" |

### 5.2 Lời hứa trong hồ sơ cũ mà sản phẩm chưa làm (BGK dễ vặn)

| Lời hứa | Ở đâu | Hiện trạng (01/11) | Trả lời ngắn |
|---|---|---|---|
| "Tự động tư vấn cải thiện báo cáo ESG, **BCTC**" | Tên đề tài; AI-Q2026 slide 1 | Studio: 4 loại đề xuất theo quy tắc, có rào "không thêm số", xuất DOCX có tracked changes. Chưa thử với người dùng. Không có phần BCTC | Q12 |
| "Chấm điểm rủi ro tẩy xanh"; điểm 0–100 **cấp tài liệu** | Tên đề tài; Vòng 1 V.5 | Đã bỏ điểm cấp tài liệu và doanh nghiệp (bất biến 1, 9). Risk cấp claim chỉ để xếp hàng; 154/156 cùng mức MEDIUM | "Bỏ có chủ đích sau khi đo" |
| Cổng so sánh **7 điều kiện** (điều 7: khung chuẩn mực) | AI-Q2026 slide 9 | Sản phẩm kiểm đơn vị và 6 chiều; IR mới kiểm 7 chiều khác; không có điều kiện khung chuẩn mực; thiếu chiều `segment` (AG-3) | Q24 |
| **Lộ trình ESG 6 bước cho doanh nghiệp FDI** | AI-Q2026 slide 5, 7, 8, 10, 14 | Không có tính năng nào | Q24; không nhắc lại |
| Vòng phản hồi "cải thiện mô hình" từ quyết định của chuyên gia | AI-Q2026 slide 12 | Có nhật ký quyết định chỉ ghi thêm; không có huấn luyện lại tự động; học trò T1 chưa nối | "Phản hồi được lưu; dùng cho đo và gán nhãn, chưa tự huấn luyện" |
| Hybrid RAG có **embedding đa ngữ và cross-encoder reranker** (ghi là "Lõi MVP") | Vòng 1 V.2; Phụ lục A | Mặc định chỉ dùng từ vựng (BM25 + n-gram ký tự + RRF); dense và reranker tắt | Lời trong 04 §1 |
| Trích dẫn tới **ô bảng**, tách biểu đồ | Vòng 1 Phụ lục A, VII | Mới tới trang; AG-3 v0 thử dựng hàng bảng | Q8 |
| OCR cho PDF scan | Vòng 1 V.2 | Có nhánh OCR; máy demo chưa có tesseract (14/10) [kiểm lại] | Q10 |
| **Rule pack v1** cho 2–3 loại dự án theo Phụ lục I QĐ 21 | Vòng 1 V.3.2 | 0 quy tắc áp được; chưa có người ký | Q21 |
| **Gold ≥ 100 cặp**, hai người gán, κ ≥ 0,7 | Vòng 1 VI.2 | 0/88 cặp, 0/79 câu | Q7 |
| Ngưỡng: F1 ≥ 0,75 · Recall@10 ≥ 0,85 · trích dẫn ≥ 0,90 · verdict ≥ 0,80 | Vòng 1 V.5.1 | Chưa đo trên gold; recall truy xuất chưa đo (Hồ sơ nguyên lý §2.6) | Q2, Q7 |
| Đo thời gian xử lý so với làm thủ công | Vòng 1 VIII (giai đoạn 4) | Chưa đo | Q3 |
| Bằng chứng độc lập (kiểm toán, xử phạt, công bố HOSE/HNX) | Vòng 1; AI-Q2026 slide 7 | 0 nguồn độc lập trong chạy đầu–cuối (780/780 là tài liệu nội bộ) | Q4 |
| Đối chiếu BCTC (CAPEX xanh, mục đích sử dụng vốn) | Vòng 1 II.2, VI | Ca demo chỉ dùng BCPTBV và BCTN [CHƯA XÁC MINH có đọc BCTC] | "Chưa làm" |
| Chatbot có grounding; dashboard theo doanh nghiệp; học chủ động | Vòng 1 IX, VI.4 | Chatbot không thuộc tiêu chí hoàn thành (`EXECUTION_PLAN` §DoD) [CHƯA XÁC MINH]; không có dashboard doanh nghiệp (bất biến 1); không có học chủ động. API thì có | "Đã cắt khỏi phạm vi" |
| Corpus lõi 8–12 doanh nghiệp × 3 năm; 4–6 ngành | Vòng 1 VI.2 | Chạy đầu–cuối 1 doanh nghiệp, 1 ngành; bộ đo số liệu 7–9 doanh nghiệp | Q9 |
| Khảo sát sơ bộ (mục 3.1) | Vòng 1 III.3.1 | Bảng trống trong bản nháp [CHƯA XÁC MINH bản đã nộp] | Nếu bị hỏi: "Phần đó chúng em thay bằng số liệu khảo sát đã công bố (Hąbek & Bui 2025)" |
| QUBO thử nghiệm ở Vòng 2 | Vòng 1 VII.3; `ISSUES_REGISTER` A6 ("sau Bán kết nếu vào Chung kết") | Không có mã (grep 04/11) | Q19 |
| Trọng yếu kép theo ISSA 5000 | AI-Q2026 slide 10 | Ghi "currently undetermined"; chưa có | "Chưa có; trục trọng yếu theo ngành là việc sau" |
| Hồ sơ nguyên lý §4.2, các việc ghi "P0 trước Bán kết / P1 trước Chung kết": gold T1 và 60 cặp; chuyên gia pháp lý duyệt 3–5 quy tắc; gói bằng chứng độc lập cho Hòa Phát; cài OCR; thử Studio 3–5 người; đặt cạnh LLM chung trên 20 tuyên bố; gắn học trò sau cờ; hiệu chỉnh τ; trích dẫn ô bảng; doanh nghiệp thứ hai; yếu tố "bất thường so với kỳ trước"; tỷ lệ chỉ đúng điều khoản trên quyết định xử phạt | Hồ sơ nguyên lý §4.2–4.3 (text trích bị lệch cột, chưa tách chắc việc nào là P0, việc nào là P1) | Theo "Số mới", đều chưa xong; riêng bộ đọc 4B đã qua kiểm tra khớp, chờ cổng 06/11 | Nếu hồ sơ này đã gửi BGK: mở đầu phần hỏi đáp bằng bảng tiến độ của chính các mục này |

### 5.3 Mâu thuẫn giữa các tài liệu (thống nhất lời trước 10/11)
- **Người dùng đầu tiên:** Vòng 1 nói bộ phận ESG và kiểm toán nội bộ doanh nghiệp tự soát; QA_BANK Q74 nói ngân hàng; Bán kết nói kiểm toán viên và chuyên viên đảm bảo; Hồ sơ nguyên lý nói "người soát xét" gồm cả 5 nhóm. **Câu thống nhất:** "Người dùng trực tiếp là người soát xét: kiểm toán viên, chuyên viên đảm bảo, kiểm toán nội bộ. Cùng lõi đó, Studio phục vụ người soạn báo cáo của doanh nghiệp tự soát trước khi công bố. Ngân hàng là khách hàng mở rộng khi đã có quy tắc theo TT 17."
- **Số điều kiện của cổng so sánh:** kịch bản cũ nói 7; Bán kết S8 nói 6; Hồ sơ nguyên lý §2.3 nói "chỉ số, kỳ, phạm vi, cơ sở đo, ranh giới, loại giá trị"; bất biến 4 liệt kê 8 chiều; mã sản phẩm kiểm đơn vị và 6 chiều. **Nói:** "kiểm đơn vị và sáu chiều ngữ cảnh trước mọi phép tính", đúng như mã.
- **10 hay 15 bất biến:** có 10 bất biến, 15 là số test canh chúng.
- **Size ladder:** MO_HINH và phần tóm tắt Hồ sơ nguyên lý ghi mô hình đúng "29–32/32"; Hồ sơ nguyên lý §2.4 ghi "28–32". Kiểm `REPO\benchmark\size_ladder_2026-10-10\` trước khi nói; nếu chưa kiểm thì nói "28–32".
- **704 nghìn tỷ, 21%/năm:** Vòng 1 có nguồn [1][2]; Bán kết §4 cấm vì "chưa có trong kho tri thức". **Được nói** nếu kèm nguồn: "số NHNN công bố 21/5/2025, theo Thanh Niên". Riêng Bloomberg 53.000 tỷ USD và PwC 80%/22% vẫn không nói.
- **Silver:** Vòng 1 cam kết silver "không dùng để đánh giá cuối cùng", trong khi mọi số hiện nay đo trên nhãn AI hoặc đáp án theo cấu trúc. **Nói:** "đây là đánh giá trung gian, có người duyệt; đánh giá cuối cần gold". Theo chỉ đạo người dùng ngày 04/11, nhãn đã được người dùng duyệt thì gọi là "nhãn AI có người duyệt".
- **Điểm rủi ro:** Vòng 1 hứa thang 0–100 ở cấp tài liệu; bất biến 1 và 9 cấm điểm cấp doanh nghiệp và tách risk khỏi priority. Nói: "đã bỏ có chủ đích sau khi đo 154/156 tuyên bố cùng mức".
- **72,5% "định tính":** Hồ sơ nguyên lý §1.2 viết "72,5% báo cáo được khảo sát" mà không ghi nguồn, dễ bị hiểu là khảo sát của đội. Đây là số của Hąbek & Bui (2025).
- **Thời gian chạy:** 107–121 s (06/10), 140,5 s qua giao diện (09/10), "khoảng 2 phút". Nói "khoảng 2 phút (107–121 s, đo 06/10)" và đo lại trên máy trình chiếu.
- **Gold:** QA_BANK (20/09) nói "5 claim đã trọng tài"; "Số mới" (31/10) nói 0. Không nhắc con số 5.

### 5.4 Không được nói
- "Phát hiện greenwashing hay tẩy xanh với độ chính xác X%"; "Hòa Phát tẩy xanh" hay "Hòa Phát ghi sai"; chữ "vi phạm".
- "Chính xác 100%" (precision 1,0 là trên n nhỏ và nhãn AI); "không có hiệu ứng quy mô"; "luật gần như không bao giờ xác nhận sai".
- "Quantum advantage", "QAOA của nhóm", "đã chạy QUBO hoặc ủ mô phỏng".
- "Tiết kiệm 8–12 giờ", "2 ngày → 2 phút", bất kỳ số tiền tiết kiệm nào.
- "Bloomberg 53.000 tỷ USD", "PwC 80%/22%", "Bộ Tài chính bắt buộc công bố ESG từ 2026".
- "Đáp ứng ISAE 3000 / ISSA 5000", "kiểm toán ESG" (dùng "dịch vụ đảm bảo"); "ngăn chặn triệt để ảo giác".
- "TT 17/2022 về kiểm kê khí nhà kính"; "NĐ 06/2022 về bảo vệ môi trường"; "QĐ 21: 7 nhóm ngành, 45 lĩnh vực, bắt buộc giấy phép môi trường" (chưa đối chiếu Phụ lục I); "hạn ngạch 110 cơ sở theo QĐ 263/QĐ-TTg" và ngày khai trương sàn các-bon (chỉ có nguồn thứ cấp); mức phạt cụ thể của các nghị định.
- "Lộ trình FDI 6 bước", "cổng 7 điều kiện", "chuyên gia ESG đã duyệt", "reranker / BGE-M3 đang chạy", "trích dẫn tới ô bảng", "chatbot", "học chủ động", "mô hình học trò đã tích hợp", "chế độ đám mây GLM-5.2 đang chạy".
- "κ 0,92" mà không nói rõ là giữa hai lượt Claude; "đã có gold".
- "Có đối tác" khi chưa có văn bản.

### 5.5 Việc nên làm trước 10/11 để đóng lỗ hổng chấm điểm
1. Ba người ghi lại câu hỏi thật của BGK Bán kết từ trí nhớ (bổ sung mục 1.10).
2. TC1, Điều 6.5: đo thời gian trên mẫu nhỏ, 20 tuyên bố Hòa Phát, một người làm tay và một người dùng GreenScan; báo cả n.
3. TC3: SUS với 3–5 người (bạn cùng lớp kế toán cũng được, nhưng phải nói rõ là ai); thử cài từ zip trên máy sạch; build thử Docker hoặc nói rõ là chưa.
4. TC4: xin một email hoặc thư quan tâm pilot từ một đơn vị; ước tính giờ công viết và duyệt quy tắc pháp lý.
5. Máy demo: cài tesseract rồi chạy lại Hòa Phát; chạy `pytest -q` để lấy số pass thật; tắt Wi-Fi diễn tập.
6. Sửa slide và bộ hỏi đáp theo 5.1. Thêm slide "Hứa → Đạt → Chưa đạt". Đóng băng số theo mục 3.
