# Phản biện toàn hệ thống — 14/10/2026

**Kế hoạch gốc:** [`KE_HOACH_PHAN_BIEN_HE_THONG_VA_EDITOR_2026-10-14.md`](KE_HOACH_PHAN_BIEN_HE_THONG_VA_EDITOR_2026-10-14.md) §1. **Đợt trước:** [`AUDIT_2026-10-06.md`](AUDIT_2026-10-06.md).
**Cách đọc:** mỗi khâu trả lời 5 câu: (a) hội đồng sẽ hỏi gì · (b) bằng chứng hiện có · (c) cách nó hỏng (đã thử phá) · (d) khắc phục, P0 = trước Bán kết 25/10, P1 = trước Chung kết 10/11 · (e) minh chứng sẽ trình bày.
**Nguồn số liệu:** phiên HPG `cd5a82e326bf4117` (BCPTBV 2025 + BCTN 2024, 09/10); script thử phá chạy lại được ở §12; `pytest` 385 test xanh sau đợt sửa (359 trước + 26 mới: `tests/test_intake.py`, `tests/test_studio.py`).

## 0. Kết luận một đoạn

Lõi kiểm chứng vẫn trung thực: không tạo mâu thuẫn sai, số học tất định, biết từ chối kết luận. Nhưng ba chỗ sẽ bị hội đồng bắt ngay. (1) **Chưa có một con số độ chính xác nào đo trên nhãn người**: mọi số của T1 so với nhãn Claude, không phải gold. (2) **Hệ thống im lặng khi hỏng ở đầu vào**: DOCX bị từ chối; trang scan cho **0 đoạn văn mà không báo gì** vì máy demo không có tesseract. (3) **Kết quả trên HPG gần như phẳng**: 153/156 "khớp một phần", 154/156 MEDIUM, 156/156 pháp lý "chưa đủ bằng chứng", 0 quy tắc pháp lý được áp dụng, 780/780 bằng chứng là tài liệu của chính doanh nghiệp. Giá trị hiện nằm ở **hàng đợi 9 mục** và **danh sách thuộc tính còn thiếu**, nên trình bày phải nói đúng điều đó thay vì nói "phát hiện tẩy xanh". Đợt 14/10 sửa (2) và thêm GreenScan Studio để biến danh sách thiếu sót thành sửa đổi cụ thể có vết; (1) cần người gán nhãn; (3) cần nguồn độc lập và quy tắc pháp lý do Thảo duyệt.

## 1. Bảng tổng hợp

| # | Khâu | Mức rủi ro trước hội đồng | Lỗi nặng nhất đã thấy | Ưu tiên | Trạng thái 14/10 |
|---|---|---|---|---|---|
| 1 | Input | **Cao** | DOCX, HTML bị từ chối; trang scan → 0 đoạn, không cảnh báo | P0 | **Đã sửa** (§2) |
| 2 | T1 tuyên bố | **Cao** | Không có gold người; học trò chưa gắn | P0 | Chờ người gán |
| 3 | Số liệu, thuộc tính | Trung bình | 133/156 thiếu kỳ, 152/156 thiếu năm gốc: đúng thực trạng hay lỗi trích? chưa đo | P1 | Mở |
| 4 | Truy xuất | **Cao** | 780/780 bằng chứng là `internal` | P0 | Mở |
| 5 | Kiểm chứng | Trung bình | 153/156 PARTIAL: không phân biệt được | P1 | Mở |
| 6 | Pháp lý | **Cao** | 0/156 tuyên bố có quy tắc áp dụng | P0 | Chờ Thảo |
| 7 | Ưu tiên, hàng đợi | Trung bình | ~6/9 đúng theo người; yếu tố "bất thường" chưa tính | P1 | Mở |
| 8 | Người duyệt | Trung bình | Chưa đo thời gian ra quyết định, SUS | P0 | Studio xong 14/10; chờ thử với người |
| 9 | Xuất báo cáo | Trung bình | Không xuất được báo cáo **đã sửa**; nhật ký chỉ có quyết định | P0 | **Đã sửa** (Studio, §9) |
| 10 | Đo lường | **Cao** | Ngưỡng đăng ký trước có, nhưng 0 hàng gold | P0 | Chờ người gán |

## 2. Khâu 1 — Input

- **(a) Hội đồng hỏi:** Đưa báo cáo thật vào có được không, kể cả bản scan, Word, trang web? Mất bao lâu?
- **(b) Bằng chứng:** HPG 264 trang chạy 107–121 s, RAM đỉnh 1,3 GB, không GPU (`benchmark/queue_quality_2026-10-06.md`). Parser chia đoạn theo đoạn văn, không vượt ranh giới đoạn (`parsers/documents.py`).
- **(c) Đã thử phá** (script §12):

  | Đầu vào | Kết quả trước 14/10 |
  |---|---|
  | `.docx` | `ValueError: Unsupported file type` |
  | `.html` | `ValueError: Unsupported file type` |
  | PDF chỉ gồm ảnh (trang scan) | **0 đoạn, không lỗi, không cảnh báo**: `tesseract` không có trên máy demo, `ocr_page` trả chuỗi rỗng |
  | URL, "mã CK + năm" | Không có lối vào |
  | **BCPTBV 2025 của HPG** (bộ demo) | **4/108 trang là ảnh quét**: trên máy demo không có OCR nên 4 trang này mất chữ mà không ai biết. Phát hiện nhờ màn hình xem trước mới. |

  Thêm từ nhãn T1: 4% câu bị cắt hoặc ghép (`broken`), chữ rác đầu trang lọt vào câu.
- **(d) Khắc phục:**
  - P0 (**đã làm 14/10**): đọc DOCX (từng đoạn `w:p`, cả bảng) và HTML; `POST /v1/intake/preview` báo số trang có chữ / trang scan / OCR có sẵn không, số câu, thời gian ước lượng, đoán công ty, năm, loại báo cáo; `GET /v1/intake/fetch?url=` tải PDF/DOCX/HTML từ URL (chặn địa chỉ nội bộ, giới hạn 60 MB); bộ mẫu HPG một nút; cảnh báo đỏ trước khi chạy nếu có trang scan mà không có OCR.
  - P1: cài tesseract vào Docker image và bộ cài Windows; chọn khoảng trang; chạy lại riêng từng khâu.
- **(e) Minh chứng:** demo thả một DOCX, một URL, một PDF scan và màn hình xem trước chỉ ra trang nào sẽ mất chữ; bộ mẫu HPG hiện ngay cảnh báo 4/108 trang. Test `tests/test_intake.py`.
- **P0 phát sinh:** cài tesseract (`vie+eng`) trên laptop demo trước 25/10, chạy lại HPG, so số tuyên bố trước và sau.

## 3. Khâu 2 — T1 nhận diện tuyên bố

- **(a)** "Bộ trích bỏ sót bao nhiêu tuyên bố? So với nhãn của ai?"
- **(b)** Luật: P 0,54 / R 0,70 so với nhãn Claude. Học trò e5-base (Kaggle v3): macro-F1 0,726; nhị phân "có phải tuyên bố" F1 0,82 so với 0,61 của luật; Δ so với v2 +0,061 [+0,02; +0,10] trên cùng 498 câu. Nhãn Claude: 2 lượt mù κ 0,92.
- **(c)** Mốc so sánh là **nhãn Claude**, không phải gold. Hội đồng có thể nói "AI chấm AI". Học trò **chưa gắn vào sản phẩm**: pipeline vẫn dùng luật + lexicon. e5-large tràn bộ nhớ T4.
- **(d)** P0: gold người ≥ 60 câu cho lô test HPG (gói `gold_t1_pack.py` đã sẵn, có buổi đồng thuận); báo cáo κ người–người và người–Claude. Gắn học trò vào pipeline sau cờ cấu hình (119 ms/câu CPU → khoảng 20 s cho 156 câu), giữ luật làm phương án dự phòng. P1: leo thang LLM khi học trò dưới ngưỡng τ (quyết định 14/10 §5.3).
- **(e)** Bảng P/R/F1 trên gold người kèm khoảng tin cậy bootstrap; ma trận nhầm lẫn; 10 ca bỏ sót tiêu biểu.

## 4. Khâu 3 — Số liệu, thuộc tính

- **(a)** "Đơn vị, kỳ, phạm vi có đọc đúng không? Số trong bảng thì sao?"
- **(b)** HPG: 16 số liệu công bố, cộng lại bảng KNK khớp (22.540.603 + 933.876 = 23.474.479 so với 23.474.480, làm tròn). 47 test bẫy verdict + 17 ca checklist kiểm toán.
- **(c)** 133/156 tuyên bố thiếu kỳ, 152/156 thiếu năm gốc, 127/156 không có số. Chưa tách được bao nhiêu là thực trạng công bố (72,5% báo cáo định tính) và bao nhiêu là bộ trích bỏ sót (kỳ nằm ở câu trước, ở tiêu đề mục). Chỉ 1 phép kiểm số liệu chạy trên HPG.
- **(d)** P1: kế thừa kỳ và phạm vi từ tiêu đề mục và câu liền trước (có cờ `inherited`); đo trên 50 tuyên bố có gold thuộc tính.
- **(e)** Tỷ lệ thuộc tính đúng trên gold; ví dụ bảng → số liệu → phép cộng lại.

## 5. Khâu 4 — Truy xuất bằng chứng

- **(a)** "Bằng chứng lấy từ đâu? Có nguồn độc lập không?"
- **(b)** Hybrid BM25 + dense (FPT cloud), rerank tùy chọn; 4/4 ca thật khớp.
- **(c)** HPG: **780/780 bằng chứng là tài liệu của chính doanh nghiệp** (`internal`); quan hệ 648 PARTIAL, 84 CONTEXT, 48 SUPPORTS. Không có nguồn độc lập nào nên mọi kết luận chỉ là "tự nhất quán". Recall truy xuất chưa đo.
- **(d)** P0: gói bằng chứng độc lập cho HPG (Climate TRACE / GEM cho nhà máy thép, QĐ 13 danh mục cơ sở phát thải, báo cáo đảm bảo nếu có) với `role: evidence`; hiển thị "nguồn độc lập: 0" ngay trên tổng quan. P1: đo recall@k trên gold cặp.
- **(e)** Trước và sau khi thêm nguồn độc lập: số tuyên bố đổi kết luận.

## 6. Khâu 5 — Kiểm chứng

- **(a)** "Kết luận SUPPORTED / CONTRADICTED dựa vào đâu? LLM có quyết định thay người không?"
- **(b)** 0 CONTRADICTED sai trên HPG (17/09 là 357/419); LLM có chốt `decisive=false`, không tự tạo SUPPORTED/CONTRADICTED; chạy lại 0 lời gọi nhờ cache. 17 bẫy trong `tests/test_verdict_traps.py` là cổng hồi quy.
- **(c)** 153/156 PARTIAL, 2 SUPPORTED, 1 INSUFFICIENT: không phân biệt được. Nguyên nhân chính là khâu 4 (không có nguồn để bác hay xác nhận), không phải bộ kiểm.
- **(d)** P1: sau khi có nguồn độc lập, tách PARTIAL thành "cùng chủ đề, thiếu số" và "có số, lệch phạm vi"; ablation luật / luật + LLM trên gold cặp.
- **(e)** Bảng 5 verdict có định nghĩa vận hành (ADR 0005); 17 bẫy; A/B LLM.

## 7. Khâu 6 — Pháp lý

- **(a)** "Căn cứ pháp lý nào? Ai xác minh?"
- **(b)** Registry 11 văn bản thật, 3 ngày tháng đã sửa 06/10; 24 văn bản ứng viên đã tải và OCR.
- **(c)** HPG: **156/156 `legal_finding` = INSUFFICIENT_EVIDENCE, 0 quy tắc áp dụng**: rule pack `vn-green-v0.1-draft` chưa có quy tắc cho hầu hết `claim_type`. Văn bản OCR độ tin cậy thấp; chưa có `reviewed_by`.
- **(d)** P0: Thảo duyệt 3–5 quy tắc cho tuyên bố phát thải và tuyên bố "xanh" chung (Luật BVMT, Luật 19/2023 Đ.10, Luật Quảng cáo sửa 2025 Đ.19), mỗi quy tắc có `reviewed_by` và ngày; giao diện hiện nhãn "chưa xác minh" cho mọi căn cứ còn lại. P1: thêm 24 văn bản ứng viên sau khi duyệt.
- **(e)** Ít nhất 1 finding pháp lý thật trên demo (D6); bảng trạng thái xác minh từng văn bản.

## 8. Khâu 7 — Chấm rủi ro, hàng đợi

- **(a)** "Vì sao mục này đứng đầu?"
- **(b)** Hàng đợi 9 mục có lý do từng thành phần (`priority-v1.1`); lượt soát của người 11/10: 12/14 đồng ý, hàng đợi khoảng 6/9 đúng.
- **(c)** 154/156 MEDIUM nên severity vô dụng để xếp; yếu tố "bất thường so với kỳ trước" `not_computed` cho 172/172 mục. Lệch HD 80% so với 61% chưa giải thích.
- **(d)** P1: tính `anomaly` khi có hai kỳ báo cáo; quét trọng số trên gold thứ tự.
- **(e)** Precision@9 trên gold; giải thích từng thành phần của mục đứng đầu.

## 9. Khâu 8–9 — Người duyệt và xuất báo cáo

- **(a)** "Người dùng làm gì với kết quả? Ra được sản phẩm gì?"
- **(b)** Hàng đợi, ClaimDetail, DecisionBar, giấy làm việc tiếng Việt in PDF.
- **(c)** Trước 14/10, kết quả dừng ở **danh sách thiếu sót**: không có cách biến nó thành bản báo cáo đã sửa; nhật ký chỉ ghi quyết định đồng ý hay bác, không ghi sửa gì. Chưa có số đo thời gian ra quyết định hay SUS.
- **(d)** P0 (**đã làm 14/10**): GreenScan Studio (§10). P0 còn lại: thử với 3–5 người, đo thời gian mỗi tuyên bố và SUS.
- **(e)** Demo: mở HPG → F8 qua từng lỗi → Ctrl+. → chấp nhận đề xuất → xuất DOCX có tracked changes và báo cáo rà soát kèm nhật ký.

## 10. GreenScan Studio — những gì có từ 14/10

- **Tài liệu:** mỗi tài liệu mang `role: under_review | evidence`. Báo cáo cần kiểm sửa được; BCTC, văn bản luật, dữ liệu bên thứ ba **khóa**, chỉ xem.
- **Chẩn đoán kiểu linter:** gạch lượn sóng theo mức (đỏ: mâu thuẫn hoặc pháp lý; vàng: thiếu chứng cứ, mơ hồ; xanh: thông tin), dấu ở lề, panel Problems, hover card có kết luận, bằng chứng, căn cứ kèm nhãn xác minh.
- **Đề xuất sửa:** 4 loại theo quy tắc (`studio/suggest.py`), chạy offline:
  1. thêm phạm vi, kỳ, năm gốc;
  2. thay câu mơ hồ bằng chỗ trống `[bổ sung: …]`;
  3. thêm dẫn chiếu bằng chứng **đã tìm thấy**;
  4. làm nhẹ lời nói quá.
- **Rào chắn không bịa số:** mọi đề xuất qua `assert_no_new_numbers`: số trong câu mới phải có trong câu cũ hoặc trong trích dẫn trang. Test bắt buộc.
- **LLM:** chỉ leo thang khi độ tin cậy dưới τ **và** tài liệu thuộc lớp A công khai (`studio/escalation.py`); τ chưa hiệu chỉnh nên mặc định **không gọi**.
- **Nhật ký và phiên bản:** nhật ký thay đổi ghi người hay AI, lúc nào, quy tắc nào; lưu phiên bản và khôi phục.
- **Xuất:**
  - DOCX có tracked changes (`w:ins`, `w:del`) và bản sạch; DOCX gốc thì giữ nguyên các đoạn không đổi.
  - PDF dựng lại từ văn bản đã sửa, kèm phụ lục thay đổi. **Không giữ bố cục gốc**; giao diện ghi rõ giới hạn này.
  - Báo cáo rà soát (HTML in được) và JSON vết kiểm toán.

## 11. Khâu 10 — Đo lường

- **(a)** "Các con số này có bị chọn sau khi nhìn kết quả không?"
- **(b)** Ngưỡng đăng ký trước trong `configs/measurement_decisions.yaml`; `tools/measure_all.py`; tập test chỉ chạm một lần; manifest có hash đầu vào, cấu hình, phiên bản bộ quy tắc.
- **(c)** 0 hàng gold người. Mọi số T1 là so với nhãn Claude. Với 60–100 cặp, khoảng tin cậy ±8–11 điểm.
- **(d)** P0: gold T1 lô HPG test + 60 cặp kiểm chứng trước 22/10; chạy `measure_all.py` **một lần** và công bố cả số không đạt ngưỡng.
- **(e)** Bảng chỉ số kèm khoảng tin cậy, đối chiếu ngưỡng đăng ký trước, ngày đăng ký, hash commit.

## 12. Tái lập

Script thử phá: `tools/audit_probe.py [run_id]`: thử DOCX/HTML/PDF scan, rồi in phân bố verdict, nguồn, pháp lý, thuộc tính, hàng đợi của phiên (mặc định là phiên mới nhất có hàng đợi). Kết quả 14/10 trên `cd5a82e326bf4117` khớp mọi số trong tài liệu này.

Đo Studio trên HPG (laptop, không GPU):
- neo được 147/156 tuyên bố vào văn bản; 9 tuyên bố vắt qua hai khối PDF được liệt kê riêng là "không neo được";
- 391 đề xuất được hiện (140 phạm vi/kỳ, 124 chỗ trống, 119 dẫn chiếu, 8 làm nhẹ); đề xuất nào không qua rào chắn không bịa số bị loại trước khi hiện;
- mở tài liệu 0,31 s; xuất DOCX 0,06 s, PDF 130 trang 0,34 s, báo cáo rà soát 0,44 s.

Đã lái bằng trình duyệt thật (Edge headless): F8, Ctrl+., hover card, chấp nhận và từ chối đề xuất, tự lưu, bộ mẫu HPG trên màn hình nhập liệu. Không có lỗi console.

## 13. Gói minh chứng cho hội đồng (tới 25/10)

| Hạng mục | Nguồn | Trạng thái |
|---|---|---|
| Bảng chỉ số + CI so với ngưỡng đăng ký trước | `measure_all.py` | Chờ gold |
| Thư viện ca hỏng | §2–§11 mục (c) + `tests/test_verdict_traps.py` | Có |
| Ablation luật / học trò / LLM | Kaggle v3 + gold | Một phần |
| Độ trễ | HPG 107–121 s; học trò 119 ms/câu | Có |
| Trạng thái xác minh pháp lý | registry + `reviewed_by` | Chờ Thảo |
| Thử nghiệm người dùng 5 người (thời gian, SUS) | Studio | Chưa |
| Demo trước / sau khi sửa | Studio xuất DOCX tracked changes | Có từ 14/10 |
