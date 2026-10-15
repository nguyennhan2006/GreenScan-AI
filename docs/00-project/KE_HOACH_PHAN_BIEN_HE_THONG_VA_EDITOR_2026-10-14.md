# Kế hoạch 14/10: phản biện toàn hệ thống và GreenScan Studio (editor kiểu IDE)

**Yêu cầu của Nhân (14/10):**
- Kiểm tra và phản biện từng khâu của hệ thống, tìm hướng khắc phục, đưa ra minh chứng chặt chẽ cho hội đồng.
- Tối ưu khâu đưa input của người dùng.
- Làm phần chỉnh sửa giống IDE: người dùng sửa, AI đề xuất sửa, xuất ra báo cáo đã sửa.
- Giao diện trực quan; nút và chức năng nổi bật khi di chuột vào.

**Ràng buộc chi phí** (`~/.claude/CLAUDE.md`):
- Không dùng workflow hay nhiều agent song song nếu Nhân không yêu cầu rõ; mỗi việc tối đa 1 subagent.
- Ngữ cảnh phiên dưới khoảng 150 nghìn token; đọc file theo đoạn.

**Tiến độ (cuối ngày 14/10):** bước 1–5 ở §4 đã xong; bước 6 (thử với 3–5 người) chưa làm. Kết quả: [`AUDIT_HE_THONG_2026-10.md`](AUDIT_HE_THONG_2026-10.md), §10 (Studio) và §12 (số đo).

## 0. Trạng thái 14/10 (đủ để bắt đầu, không cần đọc lại phiên cũ)

- **Nhãn T1:**
  - Claude r1 + r2 (b01–b11) cho 1.217 câu train (`training/data/claude/claude_train.jsonl`).
  - Compare 238 câu (`training/data/gold_t1/ai/claude_compare.jsonl`); người gán **không được mở** file này trước khi gán xong lô của mình.
  - b12–b44 tạm dừng.
  - Gold của người: chưa có. Đây là khoảng trống lớn nhất trước hội đồng.
- **Kaggle v3** (`training/runs/kaggle_t1_v3`; báo cáo https://claude.ai/artifact/BJV5qq2uP1ETXJg7ggwP7J, đang để ai có link cũng xem được):
  - e5-base macro-F1 0,726; so với v2 trên cùng 498 câu: Δ +0,061 [+0,02; +0,10].
  - Nhị phân "có phải tuyên bố": học trò F1 0,82, luật 0,61.
  - Mốc so sánh là nhãn Claude, **không phải độ chính xác**.
  - e5-large tràn bộ nhớ T4.
  - Học trò **chưa gắn vào sản phẩm**: pipeline vẫn dùng luật + lexicon; CPU 119 ms/câu.
- **Pháp lý:**
  - Registry thật 11 văn bản; các sửa ngày 06/10 chờ Thảo.
  - 24 văn bản ứng viên (`configs/legal/registry_candidates_2026-10.yaml`), đã tải và OCR (`data/legal/raw/<id>/`).
  - Tài liệu 02 có 8 điểm đã cũ.
  - Xem `docs/04-data-ai/KE_HOACH_DU_LIEU_PHAP_LY_v4_2026-10-13.md`.
- **Thí nghiệm:** `docs/04-data-ai/CHUONG_TRINH_THI_NGHIEM_VA_DU_LIEU_v3_2026-10-13.md` (luận điểm L1–L4, thí nghiệm A–H, 11 nguyên tắc).
- **Frontend:**
  - `frontend/src/pages`: Start, NewAnalysis, Queue, Claims, ClaimDetail, Export, History, LegalLibrary, Settings (1.453 dòng).
  - `frontend/src/components`: Shell, SourceViewer, EvidencePanel, AttributeChecklist, DecisionBar, ClaimPanels, Overview, badges.
  - Spec cũ: `docs/05-ui/*`.

## 1. Phản biện từng khâu: khung kiểm

Mỗi khâu trả lời 5 câu, ghi vào `docs/00-project/AUDIT_HE_THONG_2026-10.md`:
- (a) hội đồng sẽ hỏi gì;
- (b) bằng chứng hiện có (số, khoảng tin cậy, file);
- (c) cách nó hỏng (thử phá có chủ đích);
- (d) khắc phục, xếp P0 (trước Bán kết 25/10) và P1 (trước Chung kết 10/11);
- (e) minh chứng sẽ trình bày.

| # | Khâu | Mã chính | Điểm nghi ngờ đã biết |
|---|---|---|---|
| 1 | Input: tải PDF/URL, parse, tách câu, OCR | NewAnalysisPage, parser | Bản scan, bảng, câu bị ghép hoặc cắt (`broken` 4% nhãn), chữ rác đầu trang |
| 2 | T1 nhận diện tuyên bố | `agents/claim_extractor.py` | Luật: P 0,54 / R 0,70; học trò chưa gắn; chưa có gold |
| 3 | Số liệu, thuộc tính | `agents/figures.py`, AttributeChecklist | Đơn vị, kỳ, phạm vi; số trong bảng (Q13) |
| 4 | Truy xuất bằng chứng | `agents/retriever.py`, `retrieval/*` | FPT dense/rerank (cloud); chưa có nguồn độc lập (Climate TRACE, GEM) |
| 5 | Kiểm chứng | `agents/verifier.py`, `verification/stance.py`, `llm_judge.py` | LLM có chốt `decisive=false`; 17 bẫy ở `tests/test_verdict_traps.py` là cổng hồi quy |
| 6 | Pháp lý | `legal/{corpus,checker,gates,rules}.py` | Văn bản OCR có độ tin cậy thấp; chưa có `reviewed_by`; hai chế độ lịch sử / hiện hành |
| 7 | Chấm rủi ro, hàng đợi | `agents/prioritizer.py`, `configs/priority_v1.yaml` | HPG: hàng đợi khoảng 6/9 đúng; lệch HD 80% so với 61% |
| 8 | Người duyệt | ClaimDetail, DecisionBar, EvidencePanel | Thời gian ra quyết định, độ dễ dùng (F1–F4 của plan v3) |
| 9 | Xuất báo cáo, giấy làm việc | ExportPage | Truy vết đã đủ chưa (nguồn, trang, phiên bản luật) |
| 10 | Đo lường | `measure_all.py`, `configs/measurement_decisions.yaml` | Ngưỡng đăng ký trước; tập test chỉ chạm một lần |

**Gói minh chứng cho hội đồng:**
- bảng chỉ số kèm khoảng tin cậy, đối chiếu với ngưỡng đăng ký trước;
- thư viện ca hỏng;
- ablation;
- độ trễ;
- trạng thái xác minh pháp lý;
- thử nghiệm người dùng (5 người: thời gian, SUS);
- demo trước và sau khi sửa.

## 2. Tối ưu input

1. **Một ô thả duy nhất** nhận PDF, DOCX, URL hoặc "mã CK + năm". Hệ thống tự nhận công ty, năm, loại báo cáo, ngôn ngữ; người dùng chỉ xác nhận.
2. **Xem trước chất lượng parse:**
   - số trang có chữ và số trang scan (gợi ý OCR);
   - số câu và thời gian ước lượng;
   - chọn khoảng trang.
3. **Thanh tiến trình theo khâu:** Parse → Tuyên bố → Bằng chứng → Pháp lý → Chấm rủi ro. Mỗi khâu có số đếm trực tiếp và chạy lại được riêng.
4. **Nút "Báo cáo mẫu HPG"** để demo trước hội đồng.

## 3. GreenScan Studio: editor kiểu IDE

**Giả định cần Nhân xác nhận:**
- Editor sửa **báo cáo của doanh nghiệp**, giống một linter cho báo cáo phát triển bền vững.
- Đầu ra gồm hai thứ: báo cáo đã sửa, và báo cáo rà soát của GreenScan.

**Bố cục (ẩn dụ VS Code):**
- **Trái, "Explorer":**
  - mục lục và trang;
  - bộ lọc theo mức rủi ro, chủ đề, trạng thái;
  - panel **Problems**, nhóm theo mức độ.
- **Giữa:** văn bản báo cáo, từng đoạn neo vào trang gốc.
  - Tuyên bố gạch dưới lượn sóng theo mức độ: đỏ là mâu thuẫn hoặc vấn đề pháp lý; vàng là thiếu chứng cứ hoặc mơ hồ; xanh là thông tin. Có dấu ở lề.
  - Di chuột vào tuyên bố hiện **hover card**: kết luận, đoạn bằng chứng, căn cứ pháp lý kèm nhãn xác minh, và các nút Xem bằng chứng / Đề xuất sửa (Ctrl+.) / Bỏ qua kèm lý do.
- **Phải, "Inspector":**
  - bằng chứng, checklist thuộc tính và checklist pháp lý;
  - **đề xuất của AI hiển thị như tracked change**: phần gạch bỏ và phần chèn, lý do, mã quy tắc, căn cứ;
  - nút Chấp nhận / Từ chối / Sửa lại;
  - "Chấp nhận mọi đề xuất loại X" có bước xác nhận.
- **Dưới:** nhật ký thay đổi (AI hay người, ai, lúc nào), lịch sử phiên bản, khôi phục.
- **Hover và nổi bật:**
  - mọi nút có trạng thái hover và tooltip nói rõ việc nó làm kèm phím tắt;
  - di chuột vào một khâu trên thanh tiến trình thì vùng liên quan trong văn bản sáng lên;
  - có tour hướng dẫn lần đầu.
- **Phím tắt:** F8 / Shift+F8 sang lỗi kế tiếp / trước đó; Ctrl+. sửa nhanh; Ctrl+Enter chấp nhận; Esc bỏ; Ctrl+Z hoàn tác.

**Rào chắn cho đề xuất của AI:**
- **Không bao giờ bịa số.** Chỉ có 4 loại đề xuất:
  1. thêm phạm vi hoặc điều kiện (ranh giới, năm gốc, Scope);
  2. thay câu mơ hồ bằng **chỗ trống cần bổ sung số liệu** "[bổ sung: …]";
  3. thêm dẫn chiếu bằng chứng (trang, bảng, chứng nhận);
  4. bỏ hoặc làm nhẹ lời nói quá (ví dụ "trung hòa các-bon" chỉ nhờ tín chỉ).
- Mỗi đề xuất có lý do, mã quy tắc và căn cứ kèm nhãn xác minh.
- **Nguồn đề xuất:**
  - mặc định dùng mẫu theo quy tắc, chạy offline, không gửi dữ liệu ra ngoài;
  - viết lại bằng LLM chỉ khi chế độ cloud được phép (Luật BVDLCN 91/2025).

**Xuất:**
1. báo cáo đã sửa: DOCX có tracked changes (`w:ins`, `w:del`), kèm bản sạch DOCX hoặc PDF;
2. báo cáo rà soát của GreenScan (PDF, HTML hoặc DOCX): phát hiện, quyết định, bằng chứng, căn cứ, nhật ký thay đổi;
3. JSON vết kiểm toán.

**Công nghệ đề xuất:**
- CodeMirror 6: `@codemirror/lint` cho diagnostics kèm actions (sửa nhanh), `hoverTooltip`, decorations. Khớp đúng mô hình IDE, ít code tự viết hơn ProseMirror hay Monaco cho văn bản thuần.
- Backend: mô hình tài liệu (đoạn có id và trang), API đề xuất (có cache), nhật ký thao tác, xuất DOCX tracked changes bằng XML tự sinh (python-docx không hỗ trợ revision sẵn).

## 4. Thứ tự làm và chi phí ước lượng (phiên mới, ngữ cảnh khoảng 30–60 nghìn token mỗi lượt)

| Bước | Việc | Cách | Token ước lượng |
|---|---|---|---|
| 1 | Bản đồ mã nguồn và test của 10 khâu | 1 subagent Explore, hoặc đọc theo đoạn | khoảng 1–2 triệu |
| 2 | Chạy test, `measure_all`, đo độ trễ (cục bộ) | lệnh, chỉ lọc kết quả | thấp |
| 3 | Viết `AUDIT_HE_THONG_2026-10.md` (P0/P1) | phiên chính | khoảng 1 triệu |
| 4 | Input: ô thả, xem trước, tiến trình | phiên chính | khoảng 2–3 triệu |
| 5 | Studio MVP: editor, Problems, hover, sửa nhanh, tracked changes, xuất DOCX | phiên chính | khoảng 5–8 triệu |
| 6 | Thử với 3–5 người, đo thời gian, SUS | người | 0 |

**Mốc:** MVP Studio và input trước 20/10; gói minh chứng trước Bán kết 25/10.

## 5. Quyết định của Nhân (14/10). Mục này thay giả định ở mục 3

1. **Phạm vi được sửa: mọi tài liệu đang được rà soát mà không phải bằng chứng.**
   - Được sửa:
     - báo cáo của doanh nghiệp (thường niên, phát triển bền vững, tích hợp, trang web);
     - báo cáo rà soát hoặc giấy làm việc của GreenScan.
   - **Chỉ đọc, không bao giờ sửa** (tài liệu bằng chứng):
     - BCTC kiểm toán;
     - văn bản pháp luật;
     - dữ liệu bên thứ ba (Climate TRACE, GEM, …);
     - chứng nhận, danh sách công bố (nhãn sinh thái, QĐ 13, sổ tín chỉ).
   - Mỗi tài liệu mang trường `role: under_review | evidence`. Editor khóa tài liệu `evidence`; chúng chỉ hiện trong khung xem bằng chứng.
2. **Định dạng: DOCX và PDF đều ưu tiên, cả đầu vào lẫn đầu ra.**
   - DOCX: sửa tại chỗ, giữ định dạng; xuất bản có tracked changes (`w:ins`, `w:del`) và bản sạch.
   - PDF: sửa trên văn bản đã trích (mỗi đoạn neo trang gốc). PDF xuất ra được dựng lại từ văn bản đã sửa, kèm phụ lục thay đổi; **không giữ nguyên bố cục gốc**. Đây là giới hạn phải nói rõ trên giao diện.
3. **Chạy offline mặc định. API LLM chỉ xử lý tình huống độ tin cậy thấp.**
   - Mặc định dùng luật, mẫu đề xuất và mô hình cục bộ.
   - **Leo thang lên API LLM khi:**
     - xác suất của học trò hoặc bộ kiểm dưới ngưỡng τ, hoặc luật và học trò bất đồng;
     - **và** lớp bảo mật của tài liệu cho phép (02 §6: A công khai thì được; B nội bộ và C mật nghề nghiệp thì **không**, chuyển cho người).
   - τ hiệu chỉnh bằng thí nghiệm B6 trên dev; ghi `configs/measurement_decisions.yaml` sau khi nhóm đồng ý.
   - Mọi kết quả LLM được cache, ghi nhật ký, gắn nhãn "AI-LLM", và vẫn tuân rào chắn không bịa số.
   - Hội đồng sẽ hỏi "bao nhiêu % câu phải gọi API": báo tỷ lệ leo thang, độ chính xác trước và sau leo thang, chi phí cho mỗi báo cáo.
