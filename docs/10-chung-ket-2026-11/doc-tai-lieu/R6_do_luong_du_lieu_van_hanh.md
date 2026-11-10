# R6: Đo lường, dữ liệu, vận hành, riêng tư, chi phí

*Đọc ngày 04/11/2026, phục vụ Chung kết 10/11/2026. Đường dẫn tính từ REPO = `D:\Sinh viên CNhan\AI quantum\docs\greenscan-ai\GreenScan-AI`. SCR = `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt`.*

**Nguồn đã đọc đủ (18 tài liệu được giao):**
- `docs/07-presentation/nghien-cuu/`: P08_rui_ro_hang_doi.md, P09_nguoi_soat_studio.md, P10_rieng_tu_ngoai_tuyen.md, P11_du_lieu.md, P12_do_luong.md, P14_van_hanh.md, P15_chuong_trinh_agent.md, A_CHUNG.md, 01_TONG_HOP_CHO_TRONG.md, 00_DANH_MUC_CAN_THU_THAP.md, B_NGUON_DU_LIEU_BO_SUNG.md.
- `docs/08-knowledge/sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md`: đọc theo mục §0–§3, §4.3–§4.4, §5–§7.
- `docs/04-data-ai/`: MEASUREMENT_PROTOCOL_2026-09-29.md, EVALUATION_PLAN.md, DATASET_AUDIT_V2.md, QUY_TRINH_GAN_NHAN_T1_2026-10-11.md.
- `training/data/claude/CODEBOOK.md`; SCR/mo_ta_truong_du_lieu.txt (data-layers-v1, 10 trang).
- `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` (mục 0–4, 10, 11).

**Đọc thêm để đối chiếu số mới (ngoài danh sách giao):**
- `docs/09-luan-van/PQ-06_DO_KHI_CHUA_CO_GOLD.md`.
- `configs/measurement_decisions.yaml` (dòng 13–30, 117–143, 252–282).
- `src/quantum_gw/settings.py` (khối `PROFILES`).
- `training/data/claude/pairs/CODEBOOK_CAP.md` (mục 2).
- `docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md` (bảng "Ba nấc", dòng 18–25).
- SCR/AI-QUANTUM_AGENT_CRITERIA_v1.txt (bảng tiêu chí, dòng 395–405), SCR/the_le_cuoc_thi.txt (dòng 283–304), SCR/GreenScan_100_Cau_BGK.txt (chỉ grep từ khoá).
- Đếm file ngày 04/11: `training/data/t1/train_claude.jsonl`, `training/data/claude/pairs/*`, `training/data/claude/r2/labels.jsonl`, `data/`, `training/data/gold_t1/`.

**Phần đọc một phần, có chủ ý:**
- B_NGUON §2.1–2.5 (nguồn EU, Mỹ, Anh, Úc): chỉ đọc qua bảng tóm tắt mục 1, vì các nguồn này không có doanh nghiệp Việt Nam.
- Tài liệu chi phí §4.1–4.2 (ONNX, embedding nhỏ) và §8 (danh mục tham khảo R1–R66): không đọc. Các số chính đã có ở §0, §1, §5 và §7.

**Không đọc được:** không có. Không cần trích bằng PyMuPDF, vì mọi tài liệu được giao là `.md` hoặc `.txt` đã trích.

**Chưa mở lại file gốc:** `experiments/AG-1/README.md`, `benchmark/queue_quality_2026-10-06.md`, `RISK_SCORING_SPEC.md`, `DECISIONS_LOG.md`, `ARCHITECTURE_INVARIANTS.md`. Số từ các file này được trích lại qua P08–P15 và kế hoạch 31/10. Phải mở file gốc trước khi đưa lên slide.

---

## 1. Tóm tắt từng tài liệu

### 1.1 P08: Rủi ro và hàng đợi ưu tiên
- **Là gì:** hồ sơ 10 câu về hai việc khác với verdict:
  - điểm rủi ro: rubric sàng lọc 0–100, chia 5 mức LOW … CRITICAL;
  - thứ tự hàng đợi cho người soát.
- **Chính:**
  - `priority-v1.1` = trọng yếu 40 + nghĩa vụ 25 + khoảng trống bằng chứng 25 + bất thường 10 (phần bất thường chưa tính). Câu thiếu chủ thể nhân ×0,75; chữ dính cột nhân ×0,5.
  - Rà soát 06/10: số mục nên soát trước giảm từ 22/213 xuống 9/172. Trước rà soát có 10/22 mục là rác; sau rà soát cả 9 mục là câu doanh nghiệp tự nói về mình.
  - Trích sai NĐ 83/2026 cho 55 tuyên bố phát thải; sau sửa còn 0.
- **Liên quan GreenScan:** trả lời câu "người soát mở mục nào trước". Rà soát chỉ đổi thứ tự; verdict và mức rủi ro của 156 tuyên bố giữ nguyên.
- **Giới hạn:**
  - thứ tự chưa được ai kiểm;
  - trọng số chưa hiệu chỉnh;
  - mức rủi ro bị chặn ở MEDIUM cho tới khi hiệu chỉnh trên gold (D-2026-09-22-03).
  - Trạng thái: IMPLEMENTED–NOT VALIDATED.

### 1.2 P09: Người soát, giấy làm việc, Studio
- **Là gì:** luồng 3 bước:
  1. tải tài liệu;
  2. soát theo hàng đợi;
  3. xuất giấy làm việc tiếng Việt (`GET /v1/runs/{id}/workpaper`).
  - Quyết định của người soát chỉ ghi thêm, không ghi đè (`POST /v1/reviews`).
  - Demo mở bằng một tuyên bố, không mở bằng dashboard (D-2026-09-18-07).
- **Số:** 156 tuyên bố thành 9 mục nên soát trước; 163 mục không soát, có nêu lý do. Bản soát tay 22 mục HPG do một người làm.
- **Còn thiếu:** số người soát, thời gian soát (RQ10), nghiên cứu người dùng. Chưa chốt cách gọi luồng là 3 bước hay 4 bước.
- **Liên quan R6:** mọi khẳng định "dễ dùng" hay "tiết kiệm thời gian" hiện chưa có số.

### 1.3 P10: Riêng tư, ngoại tuyến, che số (bổ sung bảng ba nấc từ OFFLINE_TUNG_PHAN mục 1)
- **Các nấc ngoại tuyến:**

  | Nấc | Ai đọc cặp khó | Gửi gì ra ngoài | Kết quả trên 51 ca | Trạng thái |
  |---|---|---|---|---|
  | L0a | không có mô hình, chỉ luật | không gửi gì | 20/32 · 7/19 | đang chạy |
  | L0b | GLM-5.2 đọc nguyên văn, có chốt | nguyên văn câu và đoạn | 29–32/32 · 15–18/19 | đang chạy |
  | L1 | mô hình đám mây đọc văn bản đã che | cửa sổ ngắn đã che số | gemma-31B 32/32 · 18/19, 0 xác nhận sai | thiết kế |
  | L2 | mô hình học trò tại máy | không gửi gì | chưa có | chưa có |

- **Che số (51 ca):**
  - 0/51 ca còn số, 0 tên riêng trong nội dung gửi đi.
  - gemma-4-31B: xác nhận sai giảm 2 → 0 khi che. GLM-5.2: mâu thuẫn sai tăng 0 → 3 khi che.
  - Mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang đã che.
- **Quy tắc dữ liệu:**
  - tài liệu công khai: `offline` hoặc `cloud`;
  - tài liệu nội bộ: `offline`, `gpu`, hoặc FPT Dedicated có hợp đồng;
  - FPT Serverless có thể chuyển yêu cầu sang Nhật;
  - Groq chỉ dùng cho báo cáo công khai.
- **Giống và khác khuyến nghị pháp lý (tài liệu chi phí §6.4):**
  - giống: cùng hướng định tuyến theo loại tài liệu;
  - khác: `data_class` A/B/C và sổ gửi đi `egress.jsonl` mới là đề xuất. Grep `src/` ngày 04/11 không thấy hai thứ này.
  - Che số chưa vào sản phẩm. Đường `on_ambiguous` vẫn gửi nguyên văn.

### 1.4 P11: Dữ liệu
- **Kho:**
  - 670 tài liệu Việt Nam và 297 văn bản pháp lý;
  - 19.512 đơn vị, 15.658 đoạn, 938 điều khoản;
  - 7.960 tuyên bố ứng viên, 3.786 bằng chứng;
  - tỷ lệ có người phân xử 0,06 %.
- **Chia theo doanh nghiệp:** 3.682 claim của 15 doanh nghiệp. Giữ lại 7 doanh nghiệp làm test (19,9 % số claim). Riêng `tra` chiếm 29,8 %.
- **Kho câu T1:** 66.539 câu; luật nhận 4.598 câu là tuyên bố; 6.631 câu môi trường bị luật từ chối.
- **Liên quan R6:** nút thắt là nhãn, không phải khối lượng. Số "2.055 nhãn Claude" mà P11 ghi THIẾU đã được kiểm là có thật (01_TONG_HOP).

### 1.5 P12: Đo lường
- **Thiết kế:**
  - ngưỡng ghi trước trong `configs/measurement_decisions.yaml` (29/09);
  - mọi số có n và khoảng tin cậy bootstrap 95 %, so theo cặp, bootstrap theo công ty 2.000 lần.
- **Cổng:**
  - không báo số nào khi gold dưới 60 hoặc κ dưới 0,70;
  - cổng AG-1: precision ≥ 0,90, cận dưới CI95 ≥ 0,80, CONTRADICTED sai không vượt luật quá 1.
- **Sai lệch đã biết:** thiên lệch pooling làm mức tăng của truy xuất đo được chỉ là cận dưới.
- **Số đã cũ:**
  - "bộ AG-1 có 193 ca": nay là 453 ca, cộng tập ngoài mẫu 162 và 87 ca;
  - "luật độ phủ 0,028, precision 0,75" chỉ đúng cho B-b v1.

### 1.6 P14: Vận hành
- **Laptop i7-1355U, 16 GB, không GPU, ngoại tuyến:**
  - 264 trang, 156 tuyên bố, 107,4 s, RAM đỉnh 1.331 MB;
  - ba lần chạy: 107–121 s;
  - qua giao diện khi máy đang bận: 140,5 s.
- **Laptop có khoá FPT:** chạy đầu 632 s, chạy lại 188 s nhờ cache. Tầng GPU 24 GB chưa đo.
- **Hạ tầng:**
  - hàng đợi job một luồng, giữ 50 job trong bộ nhớ;
  - manifest ghi hash đầu vào, corpus, rule pack, prompt và model (bất biến 10);
  - 721 phiên lưu (khoảng 1 GB).
- **Giới hạn:**
  - đo trên một bộ hai tài liệu của một doanh nghiệp;
  - chưa kiểm tái lập trên máy thứ hai;
  - "khoảng 2 phút" chưa đo trên máy trình chiếu.

### 1.7 P15: Chương trình agent AG-0…AG-6
- **Là gì:** mượn cách làm của ZAIC để trị các lỗi đã đo F1–F7.
- **Lưu ý:** gần như mọi số trong hồ sơ là bản sáng 31/10 và đã cũ (xem mục 5.1). Chỉ dùng phần lập luận "vì sao không bê nguyên ZAIC":
  - GreenScan không có gold;
  - sai một kết luận là quy kết sai một doanh nghiệp;
  - ràng buộc chạy ngoại tuyến trên CPU.

### 1.8 A_CHUNG: Phần chung
- **Nền:**
  - kho tri thức: 21 mẫu hình tẩy xanh, 12 văn bản pháp lý, 31 nghiên cứu về Việt Nam, 32 vụ quốc tế;
  - 10 bất biến kiến trúc, 24 quyết định.
- **Trích ngoài:** CheckList; Aarnes & Setty 2026; tự tin theo hai đường độc lập (AUROC 0,82 so với 0,61–0,68).
- **Dùng cho R6:** D-2026-09-22-05 cấm nói "độ chính xác X %" khi gold dưới 60 và chưa có hold-out theo doanh nghiệp.

### 1.9 01_TONG_HOP_CHO_TRONG
- Danh sách chỗ THIẾU theo người và 7 mâu thuẫn cần thống nhất.
- Bảng đối chiếu ngày 31/10:
  - 47 hàm `test_` trong `test_verdict_traps.py`, 15 hàm trong `test_architecture_invariants.py`;
  - 2.055 nhãn Claude có thật;
  - `CHON_MO_HINH_THEO_CONG_DOAN_2026-10-16.md` không có trong repo.

### 1.10 00_DANH_MUC_CAN_THU_THAP
- Khung 10 câu cho từng hồ sơ và 4 nhãn nguồn.
- Mục C liệt kê bốn thứ chắc chắn còn thiếu:
  - gold người;
  - chuyên gia đánh giá phát hiện;
  - quy tắc pháp lý có `reviewed_by`;
  - ảnh chụp màn hình của luồng.

### 1.11 B_NGUON_DU_LIEU_BO_SUNG (agent Haiku, 31/10)
- **Là gì:** 26 nguồn quốc tế và 9 nguồn Việt Nam để kiểm chứng tuyên bố bằng nguồn ngoài báo cáo.
- **Nguồn P0:**
  - Climate TRACE (CC BY 4.0, theo tài sản);
  - GEM Global Steel Plant Tracker và GEM Global Cement and Concrete Tracker;
  - QĐ 13/2024/QĐ-TTg (2.166 cơ sở phải kiểm kê khí nhà kính);
  - dữ liệu quan trắc tự động.
- **Bộ dữ liệu NLP:**
  - Environmental Claims: 2.117 / 265 / 265 mẫu;
  - Climate-FEVER: 1.535 tuyên bố;
  - ClimRetrieve: 30 báo cáo, hơn 8.500 cặp, EMNLP 2024.
- **Liên quan GreenScan:** trị lỗi F6 (bằng chứng chỉ có nguồn nội bộ, `has_independent: False`).
- **Trạng thái 04/11:** `data/` chưa có dữ liệu P0 nào, tức chưa thu thập. Nhiều mục trong tài liệu ghi "chưa xác minh".

### 1.12 Mô hình, chi phí, phần cứng (05/10)
- **Là gì:** giá FPT, ba tầng triển khai T0 / T1 / T2, nguyên tắc thác mô hình có cơ sở nghiên cứu, khung pháp lý về bảo vệ dữ liệu cá nhân.
- **Số chính (đều là ước tính):**
  - T1, bộ 300 trang, chạy thác: ≈ 0,5–1,4 USD;
  - T0: 0 đồng, 5–15 phút;
  - T2: 6–11 phút.
- **Laptop:**
  - có AVX2 và AVX-VNNI, không có AVX-512;
  - LLM 4–8B chạy tại chỗ không đủ cho 700 cặp; chỉ hợp với 30–50 cặp khó nhất.
- **Giống:** GreenScan đã làm "tất định trước" (R1) và cache khớp chính xác (R6).
- **Khác:**
  - chưa có `data_class`;
  - chưa lưu `usage` token của từng lời gọi, nên chi phí vẫn là ước tính;
  - từ 31/10 khoá FPT bị 401 và người dùng quyết định không dùng khoá trả phí, nên tầng T1 hiện không chạy.

### 1.13 MEASUREMENT_PROTOCOL (29/09)
- **Là gì:** giao thức đo đăng ký trước khi có gold, gồm 6 phần: truy xuất, quan hệ từng cặp, kết luận, hàng đợi, thời gian, cổng κ.
- **Luật quyết định:**
  - bật BGE-M3: ΔRecall@5 ≥ +10 điểm **và** thời gian ≤ 2 lần bản lite;
  - cho LLM tự quyết SUPPORTED: precision ≥ 0,80, cận dưới ≥ 0,65, n ≥ 20;
  - cho LLM tự quyết CONTRADICTED: precision ≥ 0,90, cận dưới ≥ 0,75, n ≥ 10, và tỷ lệ mâu thuẫn sai không tăng.
- **Sai lệch ghi trước:**
  - pooling;
  - tuyên bố lấy từ VN30, không phải doanh nghiệp phát thải cao;
  - bài đo thời gian n = 10 mỗi nhóm;
  - mô hình qua API đổi phiên bản.
- **Đã chuẩn bị:** 14.708 vector qua FPT (77,7 trang/s); 249/249 câu trả lời mô hình đã cache; BGE-M3 chạy tại máy chỉ 0,49 trang/s.
- **Trạng thái:** chưa chạy được vì không có gold. Các bước gọi FPT nay hỏng khoá.

### 1.14 EVALUATION_PLAN (07/07, bản nháp cũ)
- **Là gì:** 9 chiều đánh giá; gold cho MVP 20–50 ca; chỉ tiêu MVP; taxonomy lỗi 12 mã.
- **Chỉ tiêu MVP:**
  - source accuracy ≥ 95 %;
  - claim precision ≥ 80 %;
  - citation ≥ 90 %;
  - mọi CONTRADICTED phải trích bằng chứng (100 %);
  - recall chuyển người soát cho ca rủi ro cao ≥ 90 %;
  - unsafe wording 0 %.
- **Bài học còn dùng được:**
  - từng chấm 0/4 trên gói đã phân xử trong khi unit test vẫn xanh;
  - `evaluate-real` báo 4 số, không gộp;
  - `risk_band_accuracy` = 0,50 trên 4 ca, và không được chỉnh rubric theo 4 ca này.
- **Khác hiện tại:** bản này dùng accuracy và risk band. Nay đã thay bằng 4 số theo bất biến 8, cộng cổng gold ≥ 60 và κ ≥ 0,70.

### 1.15 DATASET_AUDIT_V2 (09/08)
- **Phân biệt ba từ:** unified (hợp nhất), audited (đạt 8/8 bất biến kiểm tra), adjudicated (0,06 %).
- **Lỗi merge theo `doc_id`:** cùng một nội dung mang 4 id khác nhau, gây rủi ro rò rỉ giữa train và test. Kho có 297 văn bản, 8 nhóm trùng, 9 dòng duplicate.
- **Mức trưởng thành L0–L5:** L5 (gold) đang là 0.
- **Company-held-out:** giữ lại 7 doanh nghiệp, test chiếm 19,9 %.
- **Việc tiếp theo:**
  - phân xử 100–200 claim;
  - đóng băng L5 sau 300–500 cặp;
  - mở rộng lên 40–60 doanh nghiệp.
- **Lệch nội bộ:** đầu file ghi 5/7.960, bảng L4 ghi 4 claim.

### 1.16 QUY_TRINH_GAN_NHAN_T1 (11/10)
- **Ba tập:**
  - train: nhãn thầy, ≥ 3 lượt, giữ câu có đồng thuận ≥ 0,67;
  - dev: 160 câu;
  - test: 594 câu HPG.
- **Quy trình:** gán độc lập → họp → gold. Khung dữ liệu `t1-example-v1`.
- **8 quy tắc kiểm R1–R8:** đã bắt được pan và sab nằm cả ở train lẫn test, và 24 câu dev lọt vào train.
- **Thí nghiệm E1–E5:** κ, thầy so với gold, so trên HPG, đường học, phân tích lỗi.
- **Mục 11 (nhãn Claude):** κ hai lượt A–B 0,92; 21/170 câu đổi nhãn khi phân xử; 0/42 câu đồng ý chọn ngẫu nhiên phải sửa; luật so với Claude có precision 55 %, recall 69 %; Claude so với gemma κ 0,63.
- **Thực tế:** lịch 12–24/10 không thực hiện được; tới 04/11 có 0/79 nhãn người.

### 1.17 CODEBOOK.md (Claude, v1.1, 13/10)
- **Là gì:** quy tắc cho Claude đóng vai một người gán độc lập.
  - 4 nhãn cộng UNSURE; 8 chủ đề; 6 lý do NOT_CLAIM;
  - Q1–Q9 giống bản của người; Q10–Q17 là đề xuất, người chưa chốt;
  - các trường `confidence`, `needs_context`, `flag` (OVERCLAIM / INCONSISTENCY / FUTURE);
  - 4 bước tự kiểm trước khi nộp.
- **Liên quan R6:** đây là "bộ nhớ chuẩn" của khâu gán nhãn, có phiên bản (sha). Đổi quy ước nào thì phải chạy lại phân xử.

### 1.18 mo_ta_truong_du_lieu (SCR, data-layers-v1, 23/09, bản cho khách hàng)
- **Ba tầng dữ liệu:**
  1. bản gốc: URL, ngày tải, mã toàn vẹn;
  2. bản sạch: đoạn kèm số trang;
  3. ý đã tách: tuyên bố, con số, câu bị loại kèm lý do.
- **Tuyên bố và con số:**
  - tuyên bố có 5 thuộc tính;
  - con số có 6 chiều;
  - độ chính xác theo cách công bố: "12 %" hiểu là 11,5–12,5.
- **Hiện trạng 23/09:**
  - 1.061 tài liệu, 15.658 đoạn, 11.746 mục, 0 bản ghi sai cấu trúc;
  - 37 % tài liệu chưa có tệp lưu;
  - 29 % đoạn chưa được phân nhóm;
  - kho cũ chưa có số trang.
- **FAQ:**
  - hệ thống chạy hoàn toàn tại chỗ được;
  - không huấn luyện trên tài liệu khách hàng;
  - tầng bản gốc không ai sửa được.

### 1.19 Đọc thêm: PQ-06, yaml, settings.py
- **PQ-06:**
  - GS-Bench v1.1 có 453 ca; các họ nhiễu S0 / S1, C1–C3, N1–N6;
  - lỗi nhãn 16/455 = 3,5 %;
  - tách số trong mẫu và ngoài mẫu; không có con số gộp; có danh sách "không được nói".
- **yaml, cổng `ag2_dual_path_to_product`:**
  - CONTRADICTED sai và SUPPORTED sai không vượt luật;
  - cận dưới CI của phần tăng độ phủ > 0;
  - 17/17 bẫy xanh;
  - test bất biến đạt hết;
  - thời gian HPG offline ≤ 2 lần.
- **settings.py:**
  - `offline` tắt stance LLM, embedding `lite`, reranker `none`, URL LLM tại máy để trống;
  - `gpu` có `LLM_FALLBACK_ORDER: local,fpt`.

---

## 2. Khái niệm và lý thuyết phải nắm

**2.1 Vàng, bạc và đáp án theo cấu trúc**
- **Vàng (gold):** nhãn người, gán độc lập ≥ 2 người, bất đồng đem ra họp. Mức L5 đóng băng, không bao giờ dùng để chỉnh prompt, luật hay mô hình. GreenScan hiện có 0.
- **Bạc (silver):** nhãn máy có kiểm (Claude 2 lượt mù + phân xử; IR do Claude đọc rồi bộ kiểm tất định soát).
  - Được dùng để huấn luyện, sàng lọc và so thứ hạng.
  - Không được dùng để báo "độ chính xác" hay tháo chốt LLM (D-2026-10-16-01).
- **Đáp án theo cấu trúc:** đáp án suy ra từ cách dựng ca, có trước khi hệ chạy. Đây là kiểm thử nhiễu có kiểm soát, cùng tinh thần CheckList (Ribeiro và cs., 2020).
  - Ví dụ: họ C2 đổi "nghìn" thành "triệu" thì đáp án bắt buộc là C. Họ N3 đổi phạm vi phát thải thì đáp án là N.
- **Lỗi của chính bộ nhãn:** đo bằng tự kiểm (`irlib` phải tái tạo đúng nhãn của từng họ) và bằng đọc mọi chỗ hệ bất đồng với nhãn. Kết quả: 16/455 ca.

**2.2 Hệ số κ**
- **Công thức:** κ = (p_o − p_e) / (1 − p_e), với p_e = Σ_k p_A(k)·p_B(k).
  - Ba người gán thì dùng Fleiss κ, hoặc Krippendorff α (chịu được dữ liệu thiếu).
- **Nghịch lý κ khi lớp lệch:** Claude và gemma đồng ý 89/100 nhưng κ chỉ 0,63. Suy ra p_e ≈ (0,89 − 0,63) / (1 − 0,63) ≈ 0,70: đồng ý do ngẫu nhiên đã rất cao vì phần lớn câu là NOT_CLAIM.
  - Claude A–B: p_o = 554/579 ≈ 0,957, κ = 0,92.
- **Thang tham khảo Landis–Koch:** 0,61–0,80 là "đáng kể"; trên 0,80 là "gần hoàn hảo" [KIẾN THỨC NỀN]. Ngưỡng 0,70 là cam kết vòng 1 của đội (RQ7).
- **Ý nghĩa:** κ đo **độ ổn định** giữa người gán, không đo **độ đúng**. Hai lượt của cùng một mô hình có lỗi tương quan.

**2.3 Độ phủ và precision trên phần dám kết luận (dự đoán có chọn lọc)**
- **Bốn số, báo riêng, không gộp (bất biến 8):**
  - độ phủ = (#S + #C) / N;
  - precision = số kết luận đúng trong S∪C / (#S + #C);
  - số CONTRADICTED sai, tức vu oan;
  - số SUPPORTED sai, tức bỏ lọt.
- **Đường độ phủ–precision:** quét ngưỡng tin cậy, mỗi ngưỡng cho một điểm.
  - GreenScan hiện chỉ có các điểm rời:
    - luật: 0,011–0,06;
    - luật + 4B: 0,08–0,093 trên G, precision 1,0;
    - 32B một mình: 0,253 trên 87 ca sạch;
    - trần khi đọc IR hoàn hảo: 0,528 trên B-b v1.
  - Đường liên tục dựng từ xô xác suất OOF chưa làm được, vì xô quá mảnh (kế hoạch, 31/10 22:40).
- **Abstain:** kết luận N ("chưa đủ bằng chứng" hoặc "không so được") là kết quả hợp lệ, được chuyển cho người.

**2.4 Bootstrap theo công ty, so theo cặp**
- **Vì sao:** các câu cùng một báo cáo tương quan với nhau, nên đơn vị độc lập là công ty.
- **Cách làm:**
  - rút có hoàn lại K công ty trong K, gộp mọi ca của các công ty đó, tính chỉ số;
  - lặp B = 2.000 lần; CI 95 % là phân vị 2,5 và 97,5.
- **So hai hệ:** tính hiệu trên từng ca, rồi bootstrap theo công ty. Ví dụ: phần tăng độ phủ của luật + 4B so với luật trên G có CI [0,016; 0,185].
- **Giới hạn:** chỉ có 7–9 công ty. Khi ít cụm như vậy, CI phân vị thường hẹp hơn thật [KIẾN THỨC NỀN]. Luôn báo số công ty đi kèm.

**2.5 Mẫu nhỏ: khoảng Wilson và "luật số 3"**
- **Wilson khi không sai ca nào:** cận dưới = n / (n + 1,96²).
  - 15/15 đúng thì cận dưới ≈ 0,80.
  - Muốn cận dưới ≥ 0,99 cần khoảng 381 kết luận. Ở độ phủ ~0,09, tức khoảng 4.000 ca.
- **Luật số 3:** 0 lỗi trong n ca cho cận trên 95 % của tỷ lệ lỗi ≈ 3/n (giả định các ca độc lập).
  - 0 vu oan / 87 ca: tới ~3,4 %.
  - 0 / 162: ~1,9 %.
  - 0 / 402: ~0,75 %.
  - 0 / 42 ca soát ngẫu nhiên: lỗi dưới ~7 %.
- **Vì sao ngưỡng 60 câu gold:** CI Wald ở p = 0,8 là ±1,96·√(0,16/60) ≈ ±0,10.

**2.6 Leave-company-out và chống rò rỉ**
- **Nguyên tắc:**
  - chia theo nhóm (kiểu GroupKFold): công ty ở test không có câu nào ở train;
  - giữ doanh nghiệp trước, rồi mới chia theo thời gian trong phần train;
  - gom các bản trùng bytes theo `content_group`.
- **T1:**
  - test là HPG: công ty chưa thấy, chữ lấy từ parser PDF thay vì kho crawl;
  - loại 754 id dev/test khỏi train;
  - lệnh `t1_data.py check` chạy R1–R8.
- **AG:** hiệu chỉnh trên 388 ca v1.1; thử trên G (162 ca, 9 công ty) và tập sạch 87 ca. Mức trùng công ty giữa hai tập là [CHƯA XÁC MINH].

**2.7 Đăng ký trước; trong mẫu và ngoài mẫu**
- **Cách làm:**
  - ghi ngưỡng, dự đoán và điều kiện bác bỏ trước khi thấy đầu ra;
  - muốn đổi thì thêm phiên bản (`agentic_v1` → `v1_1` → `v1_2`, rồi `ag2_v1`, `ag2_product`, `ag3_v0`).
  - Chống việc chọn ngưỡng sau khi thấy số.
- **Ví dụ thật:** 4B đạt độ phủ 0,437 trong mẫu nhưng chỉ 0,126 ngoài mẫu. Nếu chỉ báo trong mẫu, đội đã nói quá 3,5 lần.
- **Báo theo cả hai thước:**
  - dự đoán cho biết giả thuyết đứng hay đổ;
  - cổng cho biết có được vào sản phẩm hay không.

**2.8 Thiên lệch pooling**
- Nhãn truy xuất chỉ có trên các trang mà bộ truy xuất cũ đã đề xuất. Bộ mới tìm được trang đúng khác sẽ không được tính.
- Vì vậy mức tăng đo được chỉ là cận dưới (MEASUREMENT_PROTOCOL §3).

**2.9 Thầy – trò, nhãn ổn định, che số**
- **Thầy:** gán ≥ 3 lượt và chỉ giữ câu có đồng thuận ≥ 0,67; hoặc Claude 2 lượt mù + phân xử (`teacher_review` = agree / adjudicated).
- **Che số:** train và test che số theo cùng một cách (R8, trường `text_masked`).
- **Học trò:** đạt macro-F1 0,71–0,73 trên nhãn Claude. Số này đo mức "bắt chước thầy", không đo độ đúng.

**2.10 Thác mô hình, định tuyến, cache**
- **Thác:** tất định trước, rồi luật → NLI → LLM vừa → LLM lớn → người. Chỉ leo thang khi độ tin cậy thấp hoặc hai tầng bất đồng (FrugalGPT, RouteLLM, AutoMix, MiniCheck).
- **Cache khớp chính xác:** khoá là sha256(prompt_version, route, tuyên bố, bằng chứng).
- Không dùng cache ngữ nghĩa, vì hai tuyên bố chỉ khác năm sẽ trúng cache sai.

**2.11 Tốc độ giải mã bị chặn bởi băng thông RAM**
- **Công thức:** tok/s ≈ băng thông hiệu dụng ÷ dung lượng trọng số.
- **Trên laptop:** lý thuyết 51,2 GB/s, hiệu dụng đo được ~22 GB/s (qwen3:8b Q4 khoảng 5 GB chạy 4,3 tok/s).
- **Hệ quả:** 4B tại máy ước khoảng 15–25 s cho mỗi lời gọi stance.

**2.12 Riêng tư**
- **Vùng xử lý:** Serverless có thể chuyển vùng; Dedicated ghim vùng.
- **Chuyển dữ liệu cá nhân xuyên biên giới:** gồm cả việc dùng nền tảng ở ngoài Việt Nam để xử lý (Luật 91/2025, Điều 20.1c).
- **Thủ tục:** DPIA; phân loại tài liệu A / B / C.
- **Che số không phải ẩn danh:** danh tính vẫn bị nhận lại từ ngữ cảnh (5/20 câu, 3/3 trang).

**2.13 Verdict, risk và priority là ba thứ khác nhau**
- verdict: đúng hay sai theo bằng chứng;
- risk: rubric 0–100 có trần thành phần, không phải xác suất tẩy xanh;
- priority: thứ tự mở cho người soát.
- Không suy ngược từ cái này ra cái kia (bất biến 9).

**2.14 Đo mức dễ dùng [KIẾN THỨC NỀN]**
- **Công cụ:**
  - SUS: 10 câu, thang 0–100, khoảng 68 là trung bình;
  - tỷ lệ hoàn tất tác vụ không cần trợ giúp;
  - thời gian cho mỗi tuyên bố khi có và không có GreenScan (RQ10, mỗi câu chỉ làm một lần).
- **Chỉ tiêu nội bộ** (AGENT_CRITERIA, nhóm J): SUS ≥ 70, hoặc ≥ 80 % người soát hoàn tất không trợ giúp.
- **Hiện trạng:** chưa đo.

**2.15 Tái lập**
- manifest ghi hash và phiên bản;
- test không bao giờ gọi mô hình thật;
- nhà cung cấp tắt mô hình nhanh, nên mỗi lần đổi mô hình phải đo lại.

---

## 3. Số liệu và dữ kiện được phép nói

Ghi chú: kết quả đếm file ngày 04/11 ghi là [ĐÃ THỰC NGHIỆM, đếm 04/11]. Các con số ước tính trong tài liệu chi phí ghi là [GIẢ THUYẾT, ước tính].

### 3.1 Nhãn người và nhãn máy
- Nhãn người = 0: 0/88 cặp trong `data/gold/sessions/`, 0/79 câu T1 lô 1 của Nhân, Quỳnh, Thảo · KE_HOACH §0, §2 F7; PQ-06 §2 · [ĐÃ THỰC NGHIỆM]. Ngày 04/11: `training/data/gold_t1/` không có file nào mới hơn 13/10 · đếm 04/11.
- Nhãn Claude T1: 2.055 dòng · `training/data/t1/train_claude.jsonl` · [ĐÃ THỰC NGHIỆM, đếm 04/11]:
  - 1.521 câu hai lượt đồng ý, 534 câu đã phân xử;
  - NOT_CLAIM 1.334 · QUALITATIVE 427 · VAGUE 153 · QUANTIFIED 141;
  - 1.416 câu tiếng Việt, 639 câu tiếng Anh; 17 công ty;
  - codebook v1.0: 484 câu; v1.1: 1.571 câu.
- Lượt 1 của Claude (579 câu = 500 train + 79 so sánh) · QUY_TRINH_T1 §11 · [ĐÃ THỰC NGHIỆM]:
  - κ A–B = 0,92 (5 nhãn) và 0,98 (tuyên bố hay không); trùng 554/579;
  - đọc lại 170 câu, 21 câu đổi nhãn; 0/42 câu đồng ý chọn ngẫu nhiên phải sửa.
- Bộ trích bằng luật so với Claude: precision 115/209 = 55 %, recall 115/167 = 69 % · QUY_TRINH_T1 §11 · [ĐÃ THỰC NGHIỆM].
- Claude so với gemma-4-31B trên 100 câu chung: đồng ý 89/100, κ 0,63 · cùng nguồn · [ĐÃ THỰC NGHIỆM].
- Học trò T1 (e5-base) · KE_HOACH §2 · [ĐÃ THỰC NGHIỆM]:
  - macro-F1 0,71–0,73 trên nhãn Claude, kiểm định chéo theo công ty, n = 1.217, 3 seed (`training/runs/kaggle_t1_v3/results.json`);
  - chưa nối vào sản phẩm.
- Cặp tuyên bố–đoạn (B-c), sổ tay CAP v1.0 ngày 16/10 với 4 quan hệ SUPPORTS / PARTIAL / CONTRADICTS / CONTEXT · `training/data/claude/pairs/` · [ĐÃ THỰC NGHIỆM, đếm 04/11]:
  - pool có 821 cặp;
  - đủ hai lượt mù mới có p01 (74 cặp) và p02 (62 cặp), tức 136 cặp, kèm 40 dòng phân xử;
  - p05 mới có lượt B; p06 và p07 mới có lượt A.

### 3.2 GS-Bench và kết quả đo (31/10–01/11)
- **Các phiên bản GS-Bench** · KE_HOACH §10; PQ-06 §3.1–3.2 · [ĐÃ THỰC NGHIỆM]:
  - v1: 193 ca = 51 B-a + 142 B-b, sinh từ 26 số liệu thật của 5 doanh nghiệp.
  - v1.1: 453 ca = 51 + 402 (S 95 / C 123 / N 184), từ 77 số liệu của 7 doanh nghiệp.
  - Nhãn sai tìm được: 16/455 ca (3,5 %), đều từ 2 lỗi của bộ sinh.
- **Mốc luật** · `experiments/AG-0/out/`; PQ-06 §3.4, §4 · [ĐÃ THỰC NGHIỆM]:
  - B-b v1: độ phủ 0,028 (4/142), precision 0,75; bắt được 0/44 ca mâu thuẫn.
  - B-b v1.1: 0,060 / 0,625; 9 SUPPORTED sai, 0 CONTRADICTED sai.
- **Trần khi IR đúng hoàn toàn (IR gold + `irlib`), trên B-b v1:** 140/142; độ phủ 0,528; precision 1,0; 0 kết luận sai · KE_HOACH §10 · [ĐÃ THỰC NGHIỆM].
- **AG-1, trong mẫu, sau `irlib.ground`** · KE_HOACH §10 (31/10 14:15) · [ĐÃ THỰC NGHIỆM]:
  - 4B: độ phủ 0,134 → 0,437, precision 0,984;
  - 32B: precision 0,817 → 0,985, CONTRADICTED sai 7 → 1;
  - nguyên nhân: 11/11 kết luận sai của 32B là bội số mô hình tự thêm vào.
- **AG-1, ngoài mẫu v1.1 (246 ca)** · KE_HOACH §10 (14:35, 22:40); PQ-06 §3.3 · [ĐÃ THỰC NGHIỆM]:
  - 4B: precision 0,903, cận dưới CI 0,81, CONTRADICTED sai 2.
  - Độ phủ 4B / 8B / 14B / 32B = 0,126 / 0,220 / 0,256 / 0,329.
  - Cổng `ag1_ir_path_usable` (vu oan ≤ luật + 1 = 1): chỉ 8B qua.
- **v1.2 trên tập G (162 ca, 9 công ty)** · KE_HOACH §10 (23:25) · [ĐÃ THỰC NGHIỆM]:
  - cả 4 model có 0 vu oan; độ phủ của 4B là 0,093;
  - 37 % số ca của G là `other_env` (lỗi của tập).
- **Tập ngoài mẫu sạch v1.3 (87 ca)** · KE_HOACH §10 (01/11 17:00) · [ĐÃ THỰC NGHIỆM]:
  - độ phủ: luật 0,011; 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253;
  - mọi model precision 1,0 và 0 kết luận sai.
- **AG-2 v1, chính sách luật + 4B bỏ phiếu S đơn độc của luật** · KE_HOACH §10 (23:50) · [ĐÃ THỰC NGHIỆM]:
  - trên G: 0,093 / 1,0 / 0 / 0; CI phần tăng độ phủ [0,016; 0,185];
  - trên 388 ca hiệu chỉnh: 0,242 / 0,989 / 1 S sai / 0 C sai, trong khi luật có 8 S sai;
  - luật + 32B có 1 S sai và luật + 4 model có 2 S sai trên G: trượt cổng.
- **Bộ đọc trong sản phẩm (Ollama + `ir_reader.py`, chạy kiểm trên Kaggle)** · yaml `agentic_ag2_product.result_2026_11_01` · [ĐÃ THỰC NGHIỆM]:
  - khớp với 4B bf16 trên Kaggle: Q4_K_M 0,963, Q8_0 0,981;
  - luật + 4B Q4 trên G: 0,080 / 1,0 / 0 / 0, CI phần tăng [0,016; 0,175];
  - 1,7 s/câu trên T4. Thời gian trên laptop chưa đo.
- **AG-3 v0 (7 ca trang 39 HPG, bộ đọc Groq gpt-oss-120b)** · KE_HOACH §10 (17:40) · [ĐÃ THỰC NGHIỆM]:
  - trang thô đúng 1/7; hàng bảng dựng lại đúng 3/7, 0 sai;
  - dự đoán "≥ 5/7" sai; cộng dọc 3/3 khớp.
- **Lỗi đã đo của hệ hiện tại (lượt 22/10)** · KE_HOACH §2 F1, F5 · [ĐÃ THỰC NGHIỆM]:
  - HPG: 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT trên 156 tuyên bố;
  - 0 quy tắc pháp lý áp được trên 156/156 tuyên bố.
- **Size ladder (51 ca dựng)** · KE_HOACH §2 F2–F3 · [ĐÃ THỰC NGHIỆM]:
  - luật quyết định 8/32 ca (đúng 6) và 3/19 ca (đúng 3); LLM quyết 29–32/32;
  - 4/4 model từ 26B trở lên báo SUPPORTED sai ở N02 và N05 (bảng PDF bị dàn phẳng).

### 3.3 Kho dữ liệu
- Kho tại thời điểm 09/08 · DATASET_AUDIT_V2 §2 · [ĐÃ THỰC NGHIỆM]:
  - 670 tài liệu Việt Nam + 297 văn bản pháp lý (legal cases);
  - 19.512 đơn vị · 15.658 đoạn · 938 điều khoản;
  - 7.960 claim ứng viên · 3.786 bằng chứng;
  - 5.028 câu sạch · 3.682 câu ưu tiên · L4: 4 claim · L5: 0.
- Nút thắt là supervision, không phải khối lượng (tỷ lệ 0,06 %); crawl thêm không dịch chuyển chỉ số nào khi chưa có ~100–200 claim phân xử · DATASET_AUDIT_V2 §3 · [ĐÃ THỰC NGHIỆM].
- Chia theo doanh nghiệp · DATASET_AUDIT_V2 §4 · [ĐÃ THỰC NGHIỆM]:
  - 3.682 claim của 15 doanh nghiệp;
  - giữ lại `pan, pow, ctg, mwg, cdn, vcs, cng`; test chiếm 19,9 %;
  - `tra` chiếm 29,8 % claim.
- Lỗi rò rỉ đã bắt được · DATASET_AUDIT_V2 §1; QUY_TRINH_T1 §6 · [ĐÃ THỰC NGHIỆM]:
  - cùng một thông cáo mang 4 `doc_id`;
  - pan và sab nằm cả ở train lẫn test;
  - 24 câu dev nằm trong train.
- data-layers-v1, đo 23/09 · SCR/mo_ta_truong_du_lieu.txt tr. 8 · [ĐÃ THỰC NGHIỆM]:
  - 1.061 tài liệu, 15.658 đoạn, 11.746 mục, 0 bản ghi sai cấu trúc;
  - 37 % chưa có tệp lưu; 29 % đoạn chưa phân nhóm.
- Kho câu: 66.539 câu; luật nhận 4.598; 6.631 câu môi trường bị luật từ chối · P11 §5 (`training/README.md` §2) · [ĐÃ THỰC NGHIỆM].
- Tập T1 · QUY_TRINH_T1 §2 · [KIẾN THỨC NỀN]:
  - dev 160 câu (12 công ty, 79 tiếng Việt, 81 tiếng Anh);
  - test HPG 594 câu = 151 luật giữ + 348 có thuật ngữ môi trường nhưng luật bỏ + 95 câu ngẫu nhiên;
  - loại 754 id khỏi train;
  - cả hai tập chưa có nhãn người.
- Nguồn độc lập P0 chưa thu thập: `data/` chỉ có `crawl, gold, golden, legal, legal_cases, real_cases, sample` · B_NGUON §1, §3 · [ĐÃ THỰC NGHIỆM, đếm 04/11].

### 3.4 Riêng tư và pháp lý
- Thí nghiệm che số trên 51 ca (20 câu tuyên bố, 3 trang thật) · P10 §2, §5 (OFFLINE_TUNG_PHAN §5.1–5.3) · [ĐÃ THỰC NGHIỆM]:
  - 0/51 ca còn số, 0 tên riêng;
  - gemma-4-31B: 32/32 · 18/19 khi che, so với 32/32 · 17/19 khi không che;
  - GLM-5.2: mâu thuẫn sai 0 → 3 khi che;
  - mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang.
- Chỉ 3 nhóm mã gọi HTTP ra ngoài (`providers/*.py`, `retrieval/embeddings.py`, `retrieval/rerank.py`); OCR chạy tại máy · P10 §3 · [KIẾN THỨC NỀN].
- Profile `offline`: `QUANTUM_LLM_STANCE=off`, `EMBEDDING_PROVIDER=lite`, `RERANKER_PROVIDER=none`, `LOCAL_LLM_BASE_URL=""` · `src/quantum_gw/settings.py` · [KIẾN THỨC NỀN].
- Profile `gpu`: `LLM_FALLBACK_ORDER: local,fpt` · cùng file · [KIẾN THỨC NỀN]. Hành vi khi không có khoá FPT: [CHƯA XÁC MINH].
- `egress.jsonl` và `data_class` không có trong `src/` · grep 04/11 · [ĐÃ THỰC NGHIỆM].
- Vùng xử lý của FPT: Serverless tự chuyển Việt Nam ↔ Nhật khi quá tải; chỉ Dedicated khoá vùng · tài liệu chi phí §2.6 [R3] · [NGOÀI].
- Privacy Statement của FPT AI Factory (đọc 05/10) vẫn viện dẫn NĐ 13/2023, không nói prompt có bị lưu log hay dùng để huấn luyện không · §6.3 · [NGOÀI].
- Khung pháp lý · tài liệu chi phí §6.1–6.2 [R60–R61] · [NGOÀI] (Thảo cần soát trước khi trích):
  - Luật BVDLCN số 91/2025/QH15, hiệu lực 01/01/2026;
  - NĐ 356/2025/NĐ-CP, hiệu lực 01/01/2026, làm NĐ 13/2023 hết hiệu lực;
  - Điều 20: chuyển xuyên biên giới, hồ sơ nộp trong 60 ngày;
  - Điều 30: xử lý bằng AI và đám mây;
  - NĐ 356 Điều 12: dữ liệu trên đám mây mã hoá khi lưu và khi truyền;
  - mức phạt tối đa 5 % doanh thu với vi phạm chuyển xuyên biên giới, 3 tỷ đồng với vi phạm khác;
  - doanh nghiệp nhỏ được hoãn DPIA 5 năm nhưng **không** được miễn Điều 20.
- Luật Kiểm toán độc lập 67/2011: Điều 43 về nghĩa vụ bảo mật; Điều 50 về lưu hồ sơ ≥ 10 năm · §6.1 [R65] · [NGOÀI].
- Luật Trí tuệ nhân tạo 134/2025/QH15 và NĐ 142/2026 · §6.1 · [NGOÀI, CHƯA XÁC MINH].

### 3.5 Chi phí, phần cứng, thời gian
- **Máy phát triển** · tài liệu chi phí §1.1 · [ĐÃ THỰC NGHIỆM]: i7-1355U (10 nhân / 12 luồng), 2 × 8 GB DDR4-3200 (51,2 GB/s lý thuyết), có AVX2 và AVX-VNNI, không có AVX-512.
- **Thời gian chạy ngoại tuyến** · P14 §5; `benchmark/queue_quality_2026-10-06.md` · [ĐÃ THỰC NGHIỆM]:
  - HPG 264 trang, 156 tuyên bố: 107,4 s, RAM đỉnh 1.331 MB;
  - ba lần chạy: 107–121 s; qua giao diện khi máy bận: 140,5 s.
- **Có GLM-5.2 cho 710 cặp:** 632 s (710 lời gọi trong 451 s, 8 luồng, 0 lỗi); chạy lại nhờ cache: 188 s · tài liệu chi phí §1.2 (`benchmark/llm_stance_ab_2026-09-28.md`) · [ĐÃ THỰC NGHIỆM].
- **Embedding:** qua FPT 77,7 trang/s; BGE-M3 tại máy 0,49 trang/s (≈ 7,7 giờ cho thư viện); reranker tại máy 0,28 cặp/s · MEASUREMENT_PROTOCOL §4 · [ĐÃ THỰC NGHIỆM].
- **LLM tại máy:** qwen3:8b chạy 4,3 tok/s; 98 s mỗi lời gọi khi bật thinking · tài liệu chi phí §4.3 · [ĐÃ THỰC NGHIỆM].
- **Chi phí cho bộ 300 trang theo giá FPT 05/10** · tài liệu chi phí §0, §5 · [GIẢ THUYẾT, ước tính]:
  - chỉ dùng gemma: ≈ 0,4–0,9 USD (10–23 nghìn đồng);
  - thác: 0,5–1,4 USD (13–36 nghìn đồng);
  - mọi cặp qua GLM-5.2: 1,1–2,7 USD;
  - T0: 0 đồng.
  - Tỷ giá dùng: 25.949 đồng/USD.
- **Giá GLM-5.2:** 1,40 USD vào / 4,40 USD ra / 0,26 USD cached cho 1 triệu token · tài liệu chi phí §2.2 [R1] · [NGOÀI].
- **Thời gian theo tầng** · tài liệu chi phí §5 · [GIẢ THUYẾT, ước tính]:
  - T0: 5–15 phút cho bộ đầy đủ có encoder;
  - T1: 10–20 phút lần đầu, 3–4 phút khi có cache;
  - T2: 6–11 phút, cộng 1–3 phút khởi động.
- **Chi phí vẫn là ước tính** vì `LLMResponse.usage` không được lưu · tài liệu chi phí §7 · [KIẾN THỨC NỀN].
- **Khoá FPT bị 401 từ 31/10.** Người dùng quyết định không dùng khoá trả phí; vai "thầy" và "người đọc thứ hai" chuyển sang Qwen3-32B-AWQ chạy trên Kaggle · KE_HOACH §10 (31/10) · [ĐÃ THỰC NGHIỆM].
- **Kaggle:** 4 tài khoản, ước 25–40 giờ GPU T4 · KE_HOACH §0 · [GIẢ THUYẾT, ước tính]. Số giờ đã dùng thực tế: [CHƯA XÁC MINH].
- **GROQ-PROBE:** `gpt-oss-120b`, `reasoning_effort` low + `json_object`: 12/12 JSON hợp lệ, độ đúng trường 1,0, p50 1,0 s (n = 12, chỉ đủ để sàng lọc) · KE_HOACH §10 · [ĐÃ THỰC NGHIỆM].
- **Laptop bị chặn khi đo bộ đọc trong sản phẩm:** Ollama báo cần 3,3 GiB nhưng chỉ còn 2,6 GiB trống · KE_HOACH §10 (01/11) · [ĐÃ THỰC NGHIỆM].

### 3.6 Vận hành, hàng đợi, người soát
- **Hàng đợi:**
  - 213 → 172 mục; mục nên soát trước 22 → 9; sau rà soát 9/9 là câu doanh nghiệp tự nói;
  - verdict và mức rủi ro không đổi trên 156 tuyên bố.
  - Nguồn: P08 §2, §5 · [ĐÃ THỰC NGHIỆM].
- **Mức rủi ro trên doanh nghiệp đối chứng** · P08 §5 · [ĐÃ THỰC NGHIỆM]:
  - 8 HIGH và 2 CRITICAL khi bật mô hình không có chốt;
  - 0 khi tắt mô hình, và 0 khi bật có chốt.
- **Thiết kế hàng đợi và rủi ro** · P08 §3 · [KIẾN THỨC NỀN]: `priority-v1.1` = 40 / 25 / 25 / 10; risk 0–100 chia 5 mức.
- **Hạ tầng** · P14 §3 · [KIẾN THỨC NỀN]: hàng đợi job một luồng, giữ 50 job trong bộ nhớ; giao diện và API cùng cổng 127.0.0.1:8000.
- **Phiên lưu:** 721 phiên (khoảng 1 GB), trong đó 637 là của bộ test và bộ hồi quy · P14 §2 · [ĐÃ THỰC NGHIỆM].
- **Bài đo thời gian người soát (RQ10)** · MEASUREMENT_PROTOCOL §1, §3 · [KIẾN THỨC NỀN]: đã thiết kế, n = 10 mỗi nhóm, chưa chạy.
- **Chỉ tiêu nội bộ** · SCR/AI-QUANTUM_AGENT_CRITERIA_v1.txt dòng 402–405 · [KIẾN THỨC NỀN] (mục tiêu, không phải kết quả):
  - P95 ≤ 120 s cho mỗi tài liệu;
  - 100 % lượt chạy có trace_id và phiên bản model, prompt, rubric;
  - SUS ≥ 70.
- **Thể lệ:** BGK "ưu tiên kết quả thực, … mô hình AI đơn giản nhưng chạy ổn định"; mỗi tiêu chí chấm 0–100 · SCR/the_le_cuoc_thi.txt dòng 291–298 · [NGOÀI].

### 3.7 Nghiên cứu ngoài (trích qua tài liệu nội bộ)
- **Mô hình và định tuyến** · tài liệu chi phí §3 · [NGOÀI]:
  - FrugalGPT: khớp GPT-4 với chi phí giảm tới 98 % [R10];
  - RouteLLM: giảm chi phí hơn 2 lần [R11];
  - MiniCheck-FT5 (770M) đạt độ đúng ngang GPT-4, rẻ hơn 400 lần [R15];
  - Bucher & Martini 2024: LLM nhỏ tinh chỉnh vượt LLM lớn zero-shot ở phân loại [R23];
  - StructuredRAG: JSON hợp lệ trung bình 82,55 % [R29].
- **Embedding tiếng Việt** · §0, §2.3 [R53, R55] · [NGOÀI]:
  - Vietnamese_Embedding: FPT ghi giấy phép CC-BY-NC-4.0, Hugging Face ghi Apache-2.0;
  - VN-MTEB ClimateFEVER-VN nDCG@10: 13,25, so với 21,27 của bge-m3.
- **Bộ dữ liệu và văn bản** · B_NGUON §2.6–2.7 · [NGOÀI]:
  - Environmental Claims: 2.117 / 265 / 265 mẫu;
  - Climate-FEVER: 1.535 tuyên bố;
  - ClimRetrieve: 30 báo cáo, 16 câu hỏi, hơn 8.500 cặp;
  - QĐ 13/2024/QĐ-TTg: 2.166 cơ sở, hiệu lực 01/10/2024.
  - Ngưỡng 3.000 tCO2e/năm và 12.045 vụ xử phạt là nguồn thứ cấp.
- **AUROC 0,82 so với 0,61–0,68** (hai đường so với tự nhất quán, bài toán text-to-SQL) · KE_HOACH §3 · [NGOÀI]. Nguồn gốc: [CHƯA XÁC MINH].

---

## 4. Câu hỏi BGK dự kiến (21 câu)

*Công thức trả lời: vấn đề → nguyên lý → GreenScan làm gì → giới hạn. Nói trong 30–60 giây.*

**Q1. Chưa có nhãn người thì "đúng" là so với cái gì?**
- **Trả lời:**
  - Nhãn người là nút thắt: hiện có 0/88 cặp và 0/79 câu. Khi chưa có vàng, chúng tôi dùng đáp án suy từ cách dựng ca, có trước khi hệ chạy.
  - GS-Bench v1.1 có 453 ca: 51 ca dựng tay và 402 ca sinh từ 77 số liệu thật của 7 doanh nghiệp. Mỗi ca là một họ nhiễu đã biết đáp án: đổi giá trị thì đáp án là C; đổi kỳ, phạm vi, hay mục tiêu với thực hiện thì đáp án là N.
  - Ngưỡng ghi trước. Chúng tôi báo 4 số với khoảng tin cậy bootstrap theo công ty.
  - Giới hạn: câu sinh theo khuôn dễ hơn câu thật. Vì vậy chúng tôi nói "trên ca dựng", không nói "độ chính xác". Tính đại diện còn là giả thuyết, sẽ kiểm bằng so thứ hạng với cặp thật nhãn Claude (B-c) và nhãn người (B-d).
- **Vặn:** "Sao không thuê người gán?" → Quy trình đã sẵn (3 người, κ ≥ 0,70, ≥ 60 câu, có họp phân xử), nhưng tới 04/11 chưa có nhãn nào. Chúng tôi nói thẳng điều này, không thay bằng nhãn Claude.
- **Bẫy:** nói "độ chính xác 98–100 %"; nói "đã kiểm trên dữ liệu thật".

**Q2. Bộ đo do đội tự dựng, vậy có phải tự chấm điểm mình?**
- **Trả lời:**
  - Rủi ro là vòng lặp tự xác nhận, nên đáp án phải độc lập với hệ được đo.
  - Ở GreenScan, đáp án do họ nhiễu quyết trước khi model chạy, và hệ được đo không tham gia gán nhãn.
  - Lỗi của chính bộ sinh thì chúng tôi đo và công bố. Hai cách: tự kiểm (`irlib` phải tái tạo đúng nhãn của từng họ) và đọc mọi chỗ hệ bất đồng với nhãn.
  - Kết quả: 16/455 ca nhãn sai (3,5 %), dồn vào 2 lỗi hệ thống. Một là C2 nhân số 0. Hai là câu PV Power thiếu phạm vi phát thải, làm S0 và N3 thành cùng một câu. Cả hai đã sinh lại, có errata.
  - Giới hạn: IR của bằng chứng do Claude đọc một lượt, nên đây là nhãn bạc.
- **Vặn:** "Chỉ đọc chỗ bất đồng thì có thiên về phía hệ không?" → Có rủi ro đó. Vì vậy mọi sửa nhãn đều ghi errata công khai (`errata_v1_1.txt`, `errata_v13.txt`), và mọi hệ, kể cả luật, được chấm lại trên cùng một bản nhãn.
- **Bẫy:** nói "bộ đo không có lỗi".

**Q3. Nhãn Claude tin được đến đâu? κ 0,92 nói lên điều gì?**
- **Trả lời:**
  - κ đo mức đồng ý vượt ngẫu nhiên, tức độ **ổn định**, không phải độ **đúng**.
  - Mỗi câu được hai agent Claude gán mù và độc lập. κ A–B = 0,92, trùng 554/579 câu.
  - Chúng tôi đọc lại 170 câu: mọi câu bất đồng, câu có độ chắc thấp, câu có cờ, cộng 42 câu đồng ý chọn ngẫu nhiên. 21 câu đổi nhãn; 0/42 câu ngẫu nhiên phải sửa, nên lỗi ở phần hai lượt đồng ý dưới khoảng 7 %.
  - Hiện có 2.055 câu: 1.521 câu hai lượt đồng ý, 534 câu đã phân xử.
  - Giới hạn: hai lượt cùng một mô hình nên dễ sai giống nhau; so với gemma, κ chỉ 0,63. Nhãn Claude dùng để huấn luyện và sàng lọc, **không** dùng để tháo chốt LLM (D-2026-10-16-01).
- **Vặn:** "Người soát lại nhãn Claude rồi thì thành vàng chứ?" → Thành "bạc đã soát". Người nhìn nhãn có sẵn dễ bị neo theo. Vàng cần gán độc lập rồi mới so; quy trình T1 cấm câu có AI hỗ trợ vào gold.
- **Bẫy:** gọi nhãn Claude là gold; dùng κ A–B làm bằng chứng nhãn đúng.

**Q4. Vì sao bootstrap theo công ty, không theo câu? Chỉ 7–9 công ty thì khoảng tin cậy còn ý nghĩa không?**
- **Trả lời:**
  - Các câu cùng một báo cáo không độc lập: cùng văn phong, cùng bảng, cùng lỗi parser.
  - Vì vậy chúng tôi lấy mẫu lại theo cụm: rút có hoàn lại các công ty, gộp mọi ca của chúng, lặp 2.000 lần, lấy phân vị 2,5 và 97,5. So hai hệ thì bootstrap trên hiệu của từng ca.
  - Ví dụ: phần tăng độ phủ của luật + 4B so với luật trên tập G (162 ca, 9 công ty) có CI [0,016; 0,185]. Cận dưới lớn hơn 0, nên phần thống kê của cổng qua.
  - Giới hạn: khi ít cụm, CI phân vị thường hẹp hơn thật. Chúng tôi luôn báo số công ty và không suy rộng ra ngành.
- **Vặn:** "Tính CI theo câu cho hẹp hơn, sao không làm?" → Hẹp giả. Đếm 162 câu như 162 bằng chứng độc lập là đếm trùng.
- **Bẫy:** nói "CI 95 % chắc chắn chứa giá trị thật".

**Q5. Làm sao biết không có rò rỉ dữ liệu giữa train và test?**
- **Trả lời:**
  - Chia ngẫu nhiên theo câu thì mô hình đã "quen" công ty ở test: từ vựng, tên KPI, văn phong.
  - Chúng tôi chia theo công ty: giữ doanh nghiệp trước, rồi mới chia theo thời gian, và gom các bản trùng nội dung.
  - Kho: giữ lại 7/15 doanh nghiệp (19,9 % claim). T1: test là HPG, một công ty chưa thấy, chữ lấy từ parser PDF.
  - Loại 754 id khỏi train. Lệnh `check` chạy 8 quy tắc và đã bắt được pan, sab nằm cả hai bên, 24 câu dev lọt vào train; đã sửa. Merge theo `doc_id` từng sinh 4 id cho cùng một tài liệu, nên đã thêm `content_group`.
  - Giới hạn: `tra` chiếm 29,8 % claim, nên khả năng khái quát có CI rộng.
- **Vặn:** "GS-Bench có chia theo công ty không?" → Có tách hiệu chỉnh (388 ca v1.1) và ngoài mẫu (G 162 ca, sạch 87 ca). Mức trùng công ty giữa hai tập: [CHƯA XÁC MINH], phải mở `build_heldout_v12.py` trước khi khẳng định.
- **Bẫy:** nói "test độc lập tuyệt đối" mà không kể hai lỗi rò rỉ đã gặp.

**Q6. "Đăng ký trước" là gì? Có lần nào nó thật sự đổi kết luận của đội không?**
- **Trả lời:**
  - Chọn ngưỡng hay cách sửa sau khi thấy số sẽ làm số đẹp giả.
  - Vì vậy chúng tôi ghi ngưỡng, dự đoán và điều kiện bác bỏ vào `configs/measurement_decisions.yaml` trước khi chạy: bản 29/09, rồi các khối `agentic_v1` ngày 31/10 đến `agentic_ag3_v0` ngày 01/11.
  - Ví dụ: sửa định dạng cho 4B đạt độ phủ 0,437 trong mẫu, nhưng trên 246 ca ngoài mẫu chỉ còn 0,126. Nếu chỉ báo trong mẫu, chúng tôi đã nói quá 3,5 lần.
  - Dự đoán "trên 4B không còn hiệu ứng cỡ" cũng bị bác: 0,126 / 0,220 / 0,256 / 0,329.
  - Giới hạn: chưa có dấu thời gian độc lập cho file đăng ký.
- **Vặn:** "Lấy gì chứng minh là ghi trước?" → Hiện chỉ có ngày ghi trong file và nhật ký chạy Kaggle. Từ lượt tới, chúng tôi băm SHA-256 file đăng ký và gửi cho người hướng dẫn trước khi chạy.
- **Bẫy:** nói "đã chứng minh không overfit"; khẳng định có lịch sử git (thư mục làm việc hiện không phải git repo, [CHƯA XÁC MINH] bản sao khác).

**Q7. Độ phủ chỉ 8–9 % thì hệ thống có ích gì?**
- **Trả lời:**
  - Bản cũ cho kết luận phẳng: 153/156 tuyên bố HPG là "khớp một phần", người soát không dùng được.
  - Trong kiểm chứng, một kết luận sai đắt hơn một lần nhường người. Nên chúng tôi tối ưu precision trên phần dám kết luận; phần còn lại vào hàng đợi, kèm lý do.
  - Trên G, luật + đọc IR bằng Qwen3-4B kết luận 15/162 ca và đúng cả 15: 0 vu oan, 0 bỏ lọt. Luật một mình chỉ phủ 0,011–0,06 và có 9 SUPPORTED sai trên v1.1.
  - Trần khi đọc IR hoàn hảo là 0,528. Khoảng trống nằm ở khâu đọc: câu nhiều số, năm của bằng chứng.
  - Giới hạn: 15 ca thì cận dưới Wilson chỉ khoảng 0,80, và đây là ca dựng.
- **Vặn:** "Vậy 90 % còn lại người phải làm hết?" → Đúng. Nhưng có thứ tự ưu tiên (9/172 mục nên mở trước trong demo HPG) và lý do vì sao chưa kết luận. Phần tiết kiệm thời gian (RQ10) chưa đo.
- **Bẫy:** nói "tự động hoá 90 %"; giấu chuyện độ phủ thấp.

**Q8. Precision 1,0 có đáng tin không?**
- **Trả lời:**
  - Tỷ lệ trên mẫu nhỏ dao động mạnh, nên phải báo khoảng tin cậy. 0 lỗi trong n ca chỉ cho cận trên của tỷ lệ lỗi khoảng 3/n.
  - 15/15 cho cận dưới Wilson khoảng 0,80. 0 vu oan trên 87 ca sạch nghĩa là tỷ lệ vu oan có thể tới khoảng 3,4 %; trên 162 ca là khoảng 1,9 %.
  - Vì vậy cổng ghi cả "cận dưới CI95 ≥ 0,80", không chỉ precision điểm.
  - Giới hạn: đây là ca dựng, và các ca cùng công ty không độc lập, nên khoảng thật còn rộng hơn.
- **Vặn:** "Vậy cần bao nhiêu ca?" → Muốn cận dưới precision ≥ 0,99 khi không sai ca nào cần khoảng 381 kết luận. Ở độ phủ hiện tại, tức khoảng 4.000 ca.
- **Bẫy:** nói "không bao giờ vu oan".

**Q9. Sao không báo một con số accuracy hay F1?**
- **Trả lời:**
  - Một con số giấu loại lỗi.
  - Bất biến 8 bắt báo riêng 4 số: độ phủ, precision trên phần dám kết luận, số C sai (vu oan doanh nghiệp, có hậu quả pháp lý và uy tín), số S sai (bỏ lọt tẩy xanh).
  - Ví dụ: luật trên 402 ca v1.1 có 0 C sai nhưng 9 S sai, precision 0,625, kể cả ca đảo "giảm" thành "tăng". Một con số gộp sẽ giấu cả hai điều đó.
  - Vì vậy đường kép phải bỏ phiếu S đơn độc của luật mới an toàn.
  - Giới hạn: bốn số khó xếp hạng hơn một số. Vì vậy cổng sản phẩm ghi rõ thứ tự: C sai và S sai không vượt luật, cận dưới phần tăng độ phủ > 0.
- **Vặn:** "Sao không dùng macro-F1?" → Có dùng cho T1 (phân loại câu). Không dùng cho verdict, vì F1 coi vu oan và bỏ lọt nặng như nhau.
- **Bẫy:** tự tính một tỷ lệ gộp ngay trên sân khấu.

**Q10. Dữ liệu lấy từ đâu, bao nhiêu, có đại diện doanh nghiệp phát thải cao không?**
- **Trả lời:**
  - Kết luận chỉ đúng cho miền đã đo.
  - Kho VN30: 670 tài liệu Việt Nam và 297 văn bản pháp lý, 15.658 đoạn, 7.960 tuyên bố ứng viên, 21 doanh nghiệp; kho câu 66.539 câu.
  - GS-Bench lấy từ 7 doanh nghiệp (G có 9). Nhãn Claude có 2.055 câu của 17 công ty. Demo là HPG, ngành thép.
  - Mỗi tài liệu có lineage: URL, ngày tải, SHA-256, cấp độ nguồn.
  - Giới hạn: phần lớn là VN30, chưa đại diện thép, xi măng, điện; `tra` chiếm 29,8 % claim. Nguồn độc lập P0 (Climate TRACE, GEM, QĐ 13/2024) chưa thu thập.
- **Vặn:** "Sao không crawl thêm?" → Audit 09/08 cho thấy crawl không dịch chuyển chỉ số nào khi chưa có 100–200 claim phân xử. Ưu tiên tăng độ đa dạng (40–60 doanh nghiệp) hơn thêm tài liệu cho doanh nghiệp cũ.
- **Bẫy:** nói "dữ liệu toàn thị trường"; trộn các số 670 / 1.061 / 21 / 15 mà không nói mỗi số là tập nào.

**Q11. Tài liệu nội bộ của khách hàng có bị gửi ra khỏi máy không?**
- **Trả lời:**
  - Tài liệu chưa công bố và hồ sơ kiểm toán có nghĩa vụ bảo mật. Nguyên tắc là phân loại dữ liệu rồi định tuyến cứng, mặc định không gửi gì.
  - Profile `offline` tắt LLM, dùng embedding `lite`, không reranker, không URL mô hình. Chỉ còn luật, số học và tìm kiếm từ vựng; trên laptop mất 107 s cho 264 trang.
  - Chỉ 3 nhóm mã có gọi HTTP; OCR chạy tại máy. Bộ đọc IR Qwen3-4B Q4 chạy tại chỗ qua Ollama, khớp 0,963 với bản Kaggle.
  - Giới hạn:
    - chưa có sổ gửi đi `egress.jsonl`;
    - chưa có test tự động chứng minh 0 kết nối ra ngoài;
    - profile `gpu` có dự phòng sang FPT, phải tắt khi chạy tài liệu mật;
    - chưa có trường `data_class`.
- **Vặn:** "Chứng minh bằng gì?" → Hiện bằng cấu hình và đọc mã. Đề xuất: demo chạy với mạng đã ngắt trước mặt BGK, và thêm một test chặn socket trước 10/11.
- **Bẫy:** khẳng định "đã kiểm định 0 kết nối".

**Q12. Luật Bảo vệ dữ liệu cá nhân 2025 tác động gì tới GreenScan?**
- **Trả lời:**
  - Tên và chữ ký lãnh đạo trong tài liệu là dữ liệu cá nhân.
  - Theo Luật 91/2025/QH15 (hiệu lực 01/01/2026) và NĐ 356/2025 (thay NĐ 13/2023):
    - dùng nền tảng ở nước ngoài để xử lý là chuyển xuyên biên giới (Điều 20), phải nộp hồ sơ đánh giá trong 60 ngày;
    - xử lý bằng AI phải phân loại rủi ro (Điều 30);
    - hợp đồng đám mây phải có mã hoá và xoá dữ liệu;
    - phạt tới 5 % doanh thu với vi phạm chuyển xuyên biên giới.
  - GreenScan: báo cáo đã công bố chứa dữ liệu cá nhân "đã được công khai theo quy định", nhiều khả năng thuộc diện miễn (NĐ 356 Điều 17.3, chờ Thảo xác nhận). Tài liệu nội bộ hoặc mật chỉ chạy offline hay trên GPU tại chỗ. Không dùng gói miễn phí cho tài liệu người dùng.
  - Giới hạn: đây là tổng hợp kỹ thuật, chưa có ý kiến pháp lý, chưa có DPIA.
- **Vặn:** "Khởi nghiệp được miễn không?" → Được hoãn DPIA 5 năm, nhưng không miễn nghĩa vụ chuyển xuyên biên giới. Cách đơn giản nhất là không gửi tài liệu loại B và C ra ngoài.
- **Bẫy:** nói "GreenScan đã tuân thủ"; viện dẫn NĐ 13/2023 như còn hiệu lực.

**Q13. Che số trước khi gửi lên đám mây có đủ an toàn không?**
- **Trả lời:**
  - Mục tiêu là dùng LLM mạnh mà không lộ số liệu và tên doanh nghiệp. Nhưng che không phải ẩn danh.
  - Trên 51 ca: sau khi che, 0/51 ca còn số, 0 tên riêng. Độ đúng giữ được: gemma-4-31B 32/32 · 18/19, xác nhận sai 2 → 0.
  - Nhưng GLM-5.2 mâu thuẫn sai 0 → 3, và mô hình vẫn đoán đúng doanh nghiệp ở 5/20 câu và 3/3 trang.
  - Kết luận: che số hợp với tài liệu công khai hoặc ít nhạy cảm. Tài liệu cần giấu danh tính thì chỉ chạy ngoại tuyến.
  - Giới hạn: n = 51 nhỏ, và che số chưa vào sản phẩm.
- **Vặn:** "Sao GLM tệ hơn khi che?" → Mất ngữ cảnh số thì mô hình đoán. Đó là lý do LLM không được tự quyết C (`llm_stance_decisive=false`).
- **Bẫy:** nói "che số là bảo mật tuyệt đối".

**Q14. Chi phí vận hành cho mỗi bộ hồ sơ là bao nhiêu?**
- **Trả lời:**
  - Nguyên tắc giảm chi phí: tất định trước, thác mô hình, cache khớp chính xác.
  - Chế độ ngoại tuyến tốn 0 đồng API trên laptop sẵn có.
  - Ước tính theo giá FPT ngày 05/10 cho bộ 300 trang:
    - chỉ dùng gemma: ≈ 0,4–0,9 USD;
    - thác gemma + GLM-5.2 cho cặp khó: 0,5–1,4 USD (13–36 nghìn đồng);
    - mọi cặp qua GLM-5.2: 1,1–2,7 USD.
  - Chạy lại có cache thì 0 lời gọi.
  - Giới hạn:
    - đây là ước tính, vì mã chưa lưu `usage` token;
    - khoá FPT bị 401 từ 31/10, nên chế độ đám mây hiện không chạy;
    - thí nghiệm chạy trên Kaggle miễn phí.
- **Vặn:** "Chi phí lớn nhất là gì?" → Thời gian của người soát, và phần này chưa đo (RQ10).
- **Bẫy:** nói "đã đo chi phí thực tế"; quy đổi VND mà không nêu tỷ giá (25.949 đồng/USD ngày 05/10).

**Q15. Chạy trên phần cứng gì, mất bao lâu, mở rộng thế nào?**
- **Trả lời:**
  - Khách hàng như kiểm toán, ngân hàng thường chỉ có laptop, không có GPU.
  - Trên i7-1355U, 16 GB, không GPU, ngoại tuyến: 2 tài liệu HPG 264 trang, 156 tuyên bố, 107,4 s, RAM đỉnh 1,3 GB (ba lần chạy 107–121 s). Có đám mây: chạy đầu 632 s, chạy lại 188 s.
  - Ba tầng triển khai:
    - T0 laptop, 0 đồng;
    - T1 laptop + API trong nước;
    - T2 GPU 24 GB cho tài liệu mật hoặc xử lý lô, ước 6–11 phút mỗi bộ.
  - Giới hạn:
    - mới đo trên 1 bộ tài liệu của 1 doanh nghiệp;
    - hàng đợi job một luồng, giữ 50 job trong bộ nhớ, nên chưa hợp nhiều người dùng cùng lúc;
    - chưa đo P95;
    - chưa đo trên máy trình chiếu.
- **Vặn:** "Bật bộ đọc IR thì chậm thêm bao nhiêu?" → Trên T4 là 1,7 s/câu; trên laptop chưa đo vì máy thiếu RAM trống. Cổng ngày 06/11 đòi thời gian HPG ≤ 2 lần chế độ offline.
- **Bẫy:** nói "2 phút trên mọi máy".

**Q16. Sao không dùng một LLM lớn trên đám mây cho xong?**
- **Trả lời:**
  - LLM lớn có độ phủ cao hơn nhưng sai theo kiểu nguy hiểm. Thể lệ cũng ưu tiên mô hình đơn giản, chạy ổn định. Ở GreenScan, LLM chỉ đọc, số học do code làm.
  - 32B trước khi sửa có 7 C sai vì tự thêm bội số "nghìn"; thêm `ground` thì còn 1.
  - Chính sách luật + 32B có 1 S sai trên G trong khi luật có 0, nên trượt cổng. Luật + 4B chạy tại chỗ có 0 sai.
  - Tài liệu nội bộ không được gửi ra ngoài, và gói miễn phí có thể lưu dữ liệu.
  - Giới hạn: 4B phủ ít hơn 32B (0,138 so với 0,253 trên 87 ca sạch).
- **Vặn:** "Sao không fine-tune?" → AG-4 (QLoRA 1.7B) chỉ chạy sau khi sửa khâu đọc câu nhiều số. Chưa làm.
- **Bẫy:** nói "mô hình nhỏ tốt hơn mô hình lớn". Sai về độ phủ.

**Q17. Hàng đợi người soát xếp theo gì? Đã kiểm chưa?**
- **Trả lời:**
  - 156 tuyên bố thì người soát không đọc hết.
  - Chúng tôi tách verdict, risk (rubric có trần, không phải xác suất) và priority, không suy ngược từ cái này ra cái kia (bất biến 9).
  - `priority-v1.1` = trọng yếu 40 + nghĩa vụ 25 + khoảng trống bằng chứng 25 + bất thường 10. Câu thiếu chủ thể nhân ×0,75, chữ dính cột nhân ×0,5.
  - Rà soát 06/10: mục nên soát trước giảm từ 22/213 xuống 9/172, cả 9 đều là câu doanh nghiệp tự nói; verdict và mức rủi ro không đổi.
  - Mức rủi ro bị chặn ở MEDIUM cho tới khi hiệu chỉnh trên gold.
  - Giới hạn: thứ tự chưa được ai kiểm; trọng số chưa hiệu chỉnh.
- **Vặn:** "40/25/25/10 lấy từ đâu?" → Từ thiết kế, chưa hiệu chỉnh. Sẽ đo precision@k của hàng đợi bằng nhãn của Quỳnh.
- **Bẫy:** đọc điểm rủi ro như xác suất tẩy xanh; nói "hàng đợi đã tối ưu".

**Q18. Đã thử với người dùng thật chưa? Đo "dễ dùng" thế nào?**
- **Trả lời:**
  - Công cụ hỗ trợ chỉ có giá trị khi người soát nhanh hơn và ít sai hơn.
  - Cách đo: thời gian mỗi tuyên bố khi có và không có công cụ (mỗi câu chỉ làm một lần, để tránh hiệu ứng nhớ), tỷ lệ hoàn tất tác vụ, và thang SUS.
  - Đã có:
    - thiết kế bài đo (RQ10, n = 10 mỗi nhóm);
    - giao diện mở bằng một tuyên bố, thẻ bằng chứng bấm về đúng trang PDF;
    - giấy làm việc tiếng Việt liệt kê cả phần chưa kiểm;
    - quyết định của người soát chỉ ghi thêm.
  - Giới hạn: chưa có nghiên cứu người dùng, chưa có số người soát, chưa có điểm SUS. Chỉ tiêu nội bộ (SUS ≥ 70) chưa đo.
- **Vặn:** "Vậy dựa vào đâu để nói hữu ích?" → Chỉ nói được hai điều: số mục phải mở trước giảm từ 156 xuống 9, và mỗi kết luận truy được về đúng trang. Chưa nói được "tiết kiệm X % thời gian".
- **Bẫy:** bịa số người dùng thử, hoặc bịa điểm SUS.

**Q19. Kết quả có tái lập được không? Nếu nhà cung cấp đổi mô hình thì sao?**
- **Trả lời:**
  - Mô hình qua API đổi phiên bản làm kết quả trôi.
  - Manifest ghi hash đầu vào, phiên bản corpus, rule pack, prompt và model (bất biến 10). Cache khoá theo sha256(prompt_version, route, tuyên bố, bằng chứng), nên chạy lại thì 0 lời gọi. Bộ test không bao giờ gọi mô hình thật.
  - FPT đã tắt hơn 30 mô hình trong 12 tháng, trong đó có bge-m3 và Qwen3-32B. Vì vậy mỗi lần đổi mô hình phải đo lại.
  - Giới hạn: chưa kiểm tái lập trên máy thứ hai.
- **Vặn:** "Kết quả demo hôm nay có giống trong slide không?" → Chế độ offline là tất định. Chúng tôi sẽ chạy lại trên máy trình chiếu và so hash kết quả trước giờ thi.
- **Bẫy:** nói "tái lập 100 %" khi chưa kiểm trên máy thứ hai.

**Q20. Người dùng thêm quy chế nội bộ hay bộ luật của họ, làm sao bảo đảm hệ thống "hiểu đúng"?**
- **Trả lời:**
  - Nếu LLM chỉ "nhớ" quy tắc qua prompt thì không kiểm được.
  - Nguyên tắc: quy tắc là dữ liệu có phiên bản (rule pack YAML). Mỗi quy tắc có điều kiện áp dụng, người duyệt (`reviewed_by`) và ca kiểm có đáp án. LLM chỉ đọc câu thành IR; code mới quyết.
  - Manifest ghi phiên bản rule pack. Tài liệu nội bộ chỉ chạy offline. Mỗi quy tắc mới phải kèm bẫy và chạy hồi quy trước khi bật.
  - Giới hạn:
    - gói `vn-green-v0.1-draft` hiện áp được 0 quy tắc trên 156/156 tuyên bố HPG;
    - chưa quy tắc nào có `reviewed_by`;
    - giao diện thêm quy tắc cho người không lập trình: [CHƯA XÁC MINH].
- **Vặn:** "LLM có học quy chế của khách không?" → Không huấn luyện trên tài liệu khách hàng. Quy tắc được áp bằng code, nên kiểm được.
- **Bẫy:** hứa "tải quy chế lên là AI tự hiểu".

**Q21. Vì sao ngưỡng là 60 câu gold và κ 0,70?**
- **Trả lời:**
  - Cần mức tối thiểu để một con số có nghĩa.
  - Với 60 câu, khoảng tin cậy 95 % quanh độ đúng 0,8 rộng khoảng ±0,10. κ 0,70 nằm trong vùng "đáng kể" của thang Landis–Koch, và là cam kết vòng 1 (RQ7).
  - Cả hai ghi trong yaml từ 29/09. Báo cáo tự bật cảnh báo "chỉ dùng nội bộ" khi chưa đạt.
  - Giới hạn: 60 câu vẫn chưa đủ để báo theo từng lớp hiếm (quy tắc R7 cần ≥ 15 câu mỗi lớp ở test).
- **Vặn:** "Không đạt thì sao?" → Không báo số nào với hội đồng (D-2026-09-22-05). Hôm nay đúng là trường hợp đó với dữ liệu thật.
- **Bẫy:** nói "κ 0,92 đã vượt ngưỡng". Đó là κ Claude–Claude, không phải κ giữa người.

---

## 5. Mâu thuẫn, số đã cũ, điều không được nói

### 5.1 Số đã cũ so với kết quả 31/10–01/11
- **P15 (mục 5, 8):**
  - Ghi: "chưa model nào qua cổng `ag1_ir_path_usable`", "lượt B còn chạy", "AG-0 chưa chạy", "AG-2 đến AG-6 chưa làm", "32B precision 0,82, 7 C sai".
  - Nay:
    - mốc luật AG-0 đã xong;
    - lượt B xong: 14B 0,254 / 0,944; gemma-12B sinh rỗng, đã loại;
    - trong mẫu sau `ground`, 32B đạt 0,985 với 1 C sai;
    - ngoài mẫu v1.1 chỉ 8B qua cổng; với v1.2, 8B và 32B có 0 vu oan, 14B có 1;
    - trên G cả 4 model có 0 vu oan;
    - đã chạy AG-2 v1, kiểm parity của bộ đọc tại chỗ, và AG-3 v0.
- **P12 và P15 "193 ca":** nay v1.1 có 453 ca; G có 162 ca; tập sạch có 87 ca.
- **"Luật 0,028 / 0,75":** chỉ đúng cho B-b v1 (142 ca). Trên v1.1 là 0,060 / 0,625; trên tập sạch là 0,011.
- **P15 "AG-2 nâng độ phủ của luật từ khoảng 25 % lên ≥ 50 %":** 25 % nhiều khả năng là 8/32 (luật quyết định trên bộ sạch B-a, F2), không phải 2,8 % đo trên B-b [suy luận]. Không dùng con số này.
- **P14 "tầng 2 laptop + FPT":** khoá bị 401 từ 31/10, và người dùng quyết định không dùng khoá trả phí. Không trình bày tầng này như đang chạy.
- **P11 và 01_TONG_HOP "498 + 79 nhãn Claude":** nay là 2.055 dòng.
  - κ 0,92 là của lượt 1 (579 câu).
  - κ của lượt `r2` (`training/data/claude/r2/labels.jsonl`, 2.000 dòng): [CHƯA XÁC MINH].
  - Học trò T1 chạy với n = 1.217, ít hơn 2.055, tức chạy trên tập cũ hơn [CHƯA XÁC MINH].
- **B-c "khoảng 800 cặp Claude 2 lượt mù + phân xử" (KE_HOACH §4):** thực tế mới có 136 cặp đủ hai lượt (đếm 04/11). Giả thuyết "thứ hạng các hệ trên B-b giống trên cặp thật" chưa kiểm được.
- **QUY_TRINH_T1 §10 (lịch 12–24/10, E1–E5):** chưa có nhãn người nào, nên họp 1 chưa diễn ra. Q10–Q17 vẫn là đề xuất (suy từ 0/79).
- **Tài liệu chi phí (05/10) chọn GLM-5.2 / gemma trên FPT:** từ 31/10 thầy là Qwen3-32B-AWQ trên Kaggle. Groq `gpt-oss-120b` chỉ dùng cho báo cáo công khai.
- **EVALUATION_PLAN (07/07):** chỉ tiêu MVP và gold 20–50 ca đã bị thay bởi giao thức 29/09 (gold ≥ 60, κ ≥ 0,70) và bất biến 8. Không trích các chỉ tiêu này như kết quả đạt được.

### 5.2 Mâu thuẫn giữa các tài liệu
- **Thời gian chạy offline HPG:** khác ngày đo, khác phiên bản mã, khác tải máy. Nói "107–121 s trên i7-1355U, ngoại tuyến" và ghi nguồn.
  - 107,4 s: rà soát hàng đợi 06/10;
  - 116 s: chú thích trong `settings.py`, đo 05/10;
  - 107–121 s: ba lần chạy;
  - 140,5 s: qua giao diện khi máy bận, 09/10;
  - 144 s: pipeline không LLM, 28/09, lượt `b96cbd0f`.
- **"Khoảng 2 phút" (Bán kết) và "T0 5–15 phút" (tài liệu chi phí):** khác cấu hình. 2 phút là pipeline luật + lite hiện tại; 5–15 phút là T0 đầy đủ có encoder và NLI, chưa cài.
- **Số tài liệu và số doanh nghiệp:** luôn nói kèm tập nào.
  - Tài liệu: 670 tài liệu Việt Nam + 297 văn bản pháp lý (09/08) so với 1.061 tài liệu (23/09, có cả bản ghi tải lỗi: 37 % chưa có tệp).
  - Doanh nghiệp: 21 (kho), 15 (tệp chia), 17 (nhãn Claude), 13 (lượt 1 của Claude), 12 (dev T1), 7 (GS-Bench v1.1), 9 (G).
- **DATASET_AUDIT_V2:** đầu file ghi "5/7.960 adjudicated", bảng L4 ghi "4 claim".
- **Ba số chưa thống nhất:** bẫy xanh 17 / 44 / 47; test bất biến 14 / 15; luồng sản phẩm 3 / 4 bước. Cổng 06/11 ghi "17/17 bẫy", nên phải nói rõ 17 là tập con nào.
- **Định tuyến:** quy tắc ghi "tài liệu mật chỉ đi offline hoặc gpu", nhưng profile `gpu` có `LLM_FALLBACK_ORDER: local,fpt`. Nếu máy có khoá FPT, lỗi ở mô hình local có thể đẩy yêu cầu sang FPT Serverless, rồi có thể sang Nhật [CHƯA XÁC MINH hành vi khi chạy].
- **FAQ khách hàng "chạy hoàn toàn tại chỗ":** chỉ đúng cho profile offline (chỉ luật). Bộ đọc IR tại chỗ chưa đo trên laptop. Mọi kết quả AG đều chạy trên Kaggle với báo cáo công khai.
- **Hai loại ngưỡng khác nhau, không trộn:**
  - ngưỡng cho LLM tự quyết trên cặp thật (protocol: S có precision ≥ 0,80 và n ≥ 20; C có precision ≥ 0,90 và n ≥ 10), cần gold;
  - cổng của đường IR trên GS-Bench (precision ≥ 0,90, cận dưới ≥ 0,80).
- **Kết quả trên G:** có 37 % ca `other_env`. Mọi số trên G, kể cả AG-2 và parity của bộ đọc, phải nói kèm "tập có lỗi đã biết". Số sạch là tập 87 ca.

### 5.3 Rủi ro cổng 06/11, cần nói thật nếu bị hỏi
- **Thời gian:** cổng đòi HPG ≤ 2 lần offline, tức khoảng 215–240 s. Tài liệu chi phí ước 4B tại máy mất 15–25 s mỗi lời gọi, nên chỉ đọc được khoảng 4–8 câu trong phần ngân sách thêm [GIẢ THUYẾT, ước tính]. Phần này có nguy cơ trượt nếu đọc mọi câu có số.
- **Phần chưa chạy:** 17 bẫy xanh và test bất biến khi bật `QUANTUM_VERIFY=dual`. Thời gian đọc trên laptop chưa đo vì máy thiếu RAM.

### 5.4 Điều không được nói
- "Độ chính xác X %" hay "GreenScan đúng 98–100 %". Số đó chỉ là precision trên phần dám kết luận, trên ca dựng, phải kèm độ phủ và CI.
- "Đã kiểm trên dữ liệu thật hay tuyên bố thật". Câu nguồn là thật, nhưng tuyên bố là câu sinh.
- "Nhãn Claude là gold", "đã có nhãn người", "κ 0,92 chứng minh nhãn đúng".
- "Không bao giờ vu oan" hay "0 sai tuyệt đối".
- "Tiết kiệm X % thời gian", "người dùng đánh giá dễ dùng", hay bất kỳ điểm SUS nào.
- "Tuân thủ Luật BVDLCN", "đã có DPIA", "đã kiểm định 0 kết nối ra ngoài". Không viện dẫn NĐ 13/2023 như còn hiệu lực.
- "Chi phí thực tế X đồng mỗi bộ". Chỉ có ước tính, phải nêu ngày giá và tỷ giá.
- "Chạy 2 phút trên máy trình chiếu", "bộ đọc IR chạy trên laptop trong X giây". Cả hai chưa đo.
- "Chế độ đám mây đang hoạt động". Khoá FPT bị 401.
- "Hàng đợi hay điểm rủi ro đã hiệu chỉnh". Không đọc điểm rủi ro như xác suất tẩy xanh.
- "Dữ liệu đại diện ngành thép, xi măng, điện", "B-b đại diện tuyên bố thật". Đó là giả thuyết.
- "Đã dùng Climate TRACE, GEM hay QĐ 13/2024 làm bằng chứng". Chưa thu thập.
