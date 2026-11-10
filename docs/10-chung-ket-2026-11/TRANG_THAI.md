# Trạng thái chuẩn bị Chung kết (cập nhật 05/11/2026)

> **09/11/2026:** theo thông báo nộp sản phẩm Vòng 2 của BTC, hạn nộp là 20/11/2026 và Vòng 2 (Bán kết) diễn ra 28–29/11/2026. Ngày “10/11” trong thư mục này là lịch cũ. Trạng thái nộp bài: [../11-vong-2-nop-bai/TRANG_THAI_NOP_BAI.md](../11-vong-2-nop-bai/TRANG_THAI_NOP_BAI.md).

Yêu cầu của Nhân (04/11):
- đọc tài liệu và paper để lường trước câu hỏi;
- dựng dataset explain / gợi ý sửa / chấm rủi ro / quy tắc nội bộ / độ dễ dùng (nhãn Claude coi như dataset thường, Nhân đọc lại);
- đánh giá hệ thống hiện tại;
- viết luận văn.

Mẫu phải "lệch nhẹ nhưng cân bằng". Từ 05/11, subagent chỉ chạy Sonnet, mỗi agent một việc hẹp.

## Đã xong
| Việc | Ở đâu |
|---|---|
| 9 ghi chú đọc tài liệu và paper (thể lệ, hệ thống, tẩy xanh, pháp lý, AI/NLP, đo lường, sản phẩm, paper web, luật 2025–2026 và lượng tử) | `doc-tai-lieu/R1…R9` |
| Ngân hàng câu hỏi: 170 câu (A–J), 40 câu ★, kịch bản 8 phút, 102 khái niệm | `NGAN_HANG_CAU_HOI_CHUNG_KET.md` (mục lục + nhóm J), `NGAN_HANG_CAU_HOI_P1..P3.md`, `KHAI_NIEM_CAN_NAM.md` |
| GS-Eval v2: explain 200, edit 200, score 200 × 2 lượt + phân xử 122, 14 pack / 76 quy tắc / 237 ca, bộ UX (16 nhiệm vụ, SUS, heuristic, lint) | `benchmark/gs_eval_v2/` (`LABELING_GUIDE.md`, `build_inputs.py`, `validate.py`, `evaluate.py`, `run_refresh.py`, `refresh_system_outputs.py`) |
| Đánh giá hệ thống hiện tại | `DANH_GIA_HE_THONG_2026-11-05.md`; số tự sinh ở `benchmark/gs_eval_v2/results/` |
| Org pack trong sản phẩm sau cờ `QUANTUM_ORG_PACKS` (tắt mặc định) | `src/quantum_gw/legal/org_pack.py`, `docs/03-architecture/ORG_PACK.md`, `configs/org_packs/`, `tests/test_org_pack.py`; khoảng 453 test qua |
| Luận văn: 7 chương + tóm tắt Việt/Anh + 78 tài liệu, khoảng 38 nghìn âm tiết | `docs/09-luan-van/LUAN_VAN_GREENSCAN/` (`LUAN_VAN_GREENSCAN.md`, `.docx`, ghép lại bằng `assemble.py`) |

## Việc của Nhân
1. Đọc lại nhãn. Đổi `review_status` thành `human_reviewed` hoặc `human_corrected`. Ưu tiên các mẫu ghi trong `benchmark/gs_eval_v2/AUDIT_EXPLAIN_EDIT.md` và các mẫu `confidence: low`. Sau đó chạy lại `evaluate.py`.
2. ~~Quyết định sửa hai lỗi P0~~: đã sửa chiều 05/11 theo yêu cầu (xem `DANH_GIA_HE_THONG_2026-11-05.md`, mục "Cập nhật chiều 05/11").
3. Soát danh mục tài liệu tham khảo của luận văn: nhiều mục thiếu nơi công bố hoặc URL do ghi chú nguồn thiếu, và còn vài mục trùng (ví dụ Calamai 2025).
4. Kiểm 76 chỗ [CHƯA XÁC MINH] trong ngân hàng câu hỏi trước khi dùng trên sân khấu.
5. Nếu kịp: thử độ dễ dùng với 3–5 người theo `benchmark/gs_eval_v2/usability/PROTOCOL.md`.

## Demo Chung kết (cập nhật chiều 05/11)
- Phiên demo: `16c7895261304145`, "DEMO Chung kết — Hòa Phát BCPTBV 2025 + BCTN 2024". Phân tích 154 giây, 156 tuyên bố, hàng đợi 9, mục #2 là câu "tự chủ điện năng rất cao" (tr. 7). Mục #2 đã có một quyết định mẫu ("Yêu cầu thêm bằng chứng"). Trước giờ thi nên tạo phiên mới để hàng đợi bắt đầu từ "chưa chốt".
- **Muốn hiện quy tắc nội bộ khi demo:** khởi động với `QUANTUM_ORG_PACKS=configs/org_packs/demo_ngan_hang_xanh` (thêm dòng này vào `.env` của máy trình chiếu), rồi phân tích lại. Giao diện có mục "Quy tắc nội bộ" ở trang chi tiết tuyên bố và ở cuối trang Thư viện pháp lý (mới thêm 05/11, đã build `frontend/dist`).
- Chụp lại toàn bộ màn hình demo (kèm toạ độ phần tử): `tools/capture_demo_screens.py` (Playwright; xem đầu tệp).
- Video demo có lời đọc: `D:/Sinh viên CNhan/Learn_to_present_video/videos/greenscan-demo-ck/` (BRIEF, STORYBOARD, FACTS, giọng Piper tạm). Bản dùng: `renders/greenscan-demo-ck-v4.mp4` (3 phút 42 giây). Kịch bản viết lại theo nhịp video giải thích ngắn: móc câu đầu video, câu ngắn, hứa ở đầu rồi trả ở cảnh tự kiểm. Phụ đề hiện từng cụm, từ đang đọc sáng lên. Ảnh chụp lại theo giao diện tiếng Việt mới, phiên `ddb55c3be3ff46a2`. Bản v3 vẫn giữ để so. Phiếu đã chấm: `renders/Phieu_cham_GreenScan_demo_v2_v3_2026-11-05.docx` (tự chấm A–D: 63,6 → 71,8/90; phần E chưa thử với người xem).

## Thống nhất ngôn ngữ và hướng dẫn người mới (tối 05/11)

- Chuẩn từ ngữ: `docs/05-ui/CHUAN_NGON_NGU_GIAO_DIEN.md`. Gồm năm nguyên tắc, bảng từ ngữ, nhãn năm loại kết luận và cách viết số/ngày.
- Nhãn tiếng Việt cho mọi giá trị mã: `frontend/src/lib/labels.js`. Ví dụ: emissions → lượng phát thải; ghg_scope_1_2_3 → phát thải phạm vi 1, 2, 3; decrease → giảm.
- Đã thay chữ tiếng Anh, thuật ngữ và viết tắt trong khoảng 30 tệp: giao diện, giấy làm việc, lời giải thích. Đổi chính: "AI đề xuất" → "Máy gợi ý"; "Studio" → "Sửa báo cáo"; "Abstain" → "Chưa kết luận"; "nhãn gold" → "nhãn chuẩn"; BCPTBV/BCTN/BCTC/KNK → viết đủ; "Scope" → "phạm vi phát thải".
- Kiểm tự động:
  - công cụ `tools/check_ui_language.py`;
  - kiểm thử `tests/test_ui_language.py`, báo lỗi khi có từ tiếng Anh hoặc mã mới;
  - ngoại lệ đã duyệt ghi trong `tools/ui_language_allow.txt`: tên tệp, tên sản phẩm, thông báo cho người viết bộ quy tắc và dòng lệnh.
- Hướng dẫn người mới:
  - trang app "Hướng dẫn cho người mới" (`#/guide`), tự mở ở lần đăng nhập đầu, có bảy bước đánh dấu được, bảng năm kết luận, giải thích từ ngữ và mục "GreenScan không làm gì";
  - kịch bản cho người hướng dẫn: `docs/05-ui/KICH_BAN_HUONG_DAN_NGUOI_MOI.md`.
- `tools/capture_demo_screens.py` đã đổi theo chữ mới và bỏ qua trang hướng dẫn lần đầu.
- **Còn lại:**
  - video đã khớp app (v4);
  - thông báo dòng lệnh và thông báo cho người viết bộ quy tắc vẫn giữ tên trường kỹ thuật.

## Ảnh chụp toàn bộ giao diện (06/11)
- 73 ảnh ở `anh-chup-giao-dien-2026-11-06/` (mục lục: `README.md` trong thư mục), chụp lại sau khi Việt hoá, phiên `eff127d3f9614e06`, server bật `QUANTUM_ORG_PACKS`. Tạo lại: `python tools/capture_all_screens.py` (+ `QUANTUM_ORG_PACKS=configs/org_packs/demo_ngan_hang_xanh`). Các phiên chụp thử cùng nhãn "Ảnh chụp tổng hợp"/"DEMO bản chậm" nằm trong Lịch sử (chưa có API xoá phiên).
- Đã sửa 06/11: (1) tour Studio kẹt ở bước 2 (thẻ z-42); (2) **Việt hoá mọi mã hiển thị**: phân rã rủi ro, lý do chấm điểm, cổng chất lượng G0–G7, ghi chú pháp lý (backend `src/quantum_gw/labels_vi.py`; frontend `lib/labels.js`: legal_issue, doc_status, check_mode, legal_finding; `RISK_COMPONENT_LABELS`), bỏ mã việc cần làm, chọn kết luận thay thế bằng nhãn Việt; (3) lần đầu nhập tên không tới trang Hướng dẫn (race điều hướng trong `App.jsx`) → đã sửa. Quy ước: chỉ giữ ký hiệu chuẩn được công nhận (GRI, tCO2e, GHG Protocol); đường dẫn cấu hình / biến môi trường admin phải gõ thì giữ nguyên.
- Còn mở: Studio chưa co giãn cho màn hình hẹp (390 px tràn ngang). F8 chỉ chạy khi con trỏ ở trong vùng soạn thảo.
- Video demo **bản chậm** (kể chuyện theo người soát Nhân, 20 khung, ~8 phút): `D:/Sinh viên CNhan/Learn_to_present_video/videos/greenscan-demo-ck-cham/` (BRIEF, STORYBOARD, FACTS; ảnh chụp bằng `tools/capture_video_v5.py`). Bản v4 3,5 phút giữ nguyên.
