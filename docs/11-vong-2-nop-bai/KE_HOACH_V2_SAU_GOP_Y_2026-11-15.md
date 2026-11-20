# Kế hoạch V2 sau góp ý chuyên gia (15/11/2026)

> **Trạng thái (cuối ngày 15/11): đã làm xong cả đợt 1 và đợt 2.** Kết quả, các chỗ lệch so với kế hoạch và số đo: `docs/03-architecture/CAI_TIEN_SAU_GOP_Y_2026-11-15.md`.
>
> Ba việc làm khác kế hoạch:
> - Gán nhãn GS-Claims do hai agent Sonnet làm độc lập và agent Opus phân xử, thay cho người. Nhãn này vẫn là nhãn máy.
> - Tập giữ riêng dùng giao thức không cần nhãn trên báo cáo đầy đủ.
> - Thêm các sửa lỗi phát sinh khi đo: cường độ "m3/tấn", nước thải, công ty mẹ, lũy kế, câu "0 vi phạm", từ xu hướng gần số, năm gốc, 100% chính xác, bằng chứng không thống nhất, chỉ số không rõ và khoản tiền.

**Đầu vào.** Bản trả lời của chuyên gia ("KẾ HOẠCH UPDATE V2 14-11.md") cho tài liệu `THIEU_SOT_XIN_Y_KIEN_CHUYEN_GIA_2026-11-14.md`. Mọi số đo dưới đây đều [ĐÃ THỰC NGHIỆM] trên mã ngày 15/11. Script đo nằm trong thư mục tạm của phiên; cách tái lập ghi ở mục 2.

## 1. Kết luận

- **Ba nhận định chính của chuyên gia đúng và đã được số đo xác nhận:**
  - trích tuyên bố là nút thắt;
  - nên bật cờ "chỉ ủng hộ khi có nguồn độc lập";
  - nên dùng LLM ở vai trò chỉ gắn cờ.
- **Phỏng đoán về nguyên nhân H1 thì sai.** Không phải luật "dòng bảng" hay "thiếu vị ngữ". **Cả 63/63 câu bị bỏ vì không khớp từ điển loại tuyên bố**, chủ yếu là các chủ đề nước và điện.
- **Còn một nút thắt thứ hai** mà chuyên gia chưa thấy: bộ đọc không nhận đơn vị. Vì vậy chỉ sửa trích câu thì tỉ lệ bắt lỗi tăng rất ít.

## 2. Số đo mới làm căn cứ (15/11)

| Phép đo | Kết quả | Ý nghĩa |
|---|---|---|
| Vì sao 63/104 câu "ủng hộ" của GS-Mutation không được trích | **63/63: không khớp loại tuyên bố nào** trong `configs/taxonomy.yaml`. Trong 63 câu: 38 câu có chỉ số đã biết kèm số liệu; 25 câu có số nhưng chỉ số không có trong từ điển. Từ chủ đề hay gặp: "nước" 28, "điện" 20, "tiêu thụ" 19, "kWh" 10 | Sửa bằng một loại tuyên bố dự phòng "số liệu công bố" (chỉ số đã biết + số liệu: 38 câu) và bổ sung từ vựng nước, điện, kWh. Recall trích có thể từ 41/104 lên khoảng ≥ 79/104, nếu độ chính xác giữ được |
| Phóng đại số (M1) bị bắt, theo kết quả của câu gốc | Câu gốc "ủng hộ" (14 ca): bắt 11. Câu gốc "ủng hộ một phần" (23 ca): bắt **0**. Câu gốc "chưa đủ bằng chứng" (3): 0. Câu gốc không được trích (61): 0 | Câu "11/14" chuyên gia trích là trên câu có **bản gốc được ủng hộ**, không phải trên câu đã trích được. Tính trên câu đã trích được là 11/40 |
| Vì sao 26 câu đã trích vẫn không quyết được | **24/26:** số khớp có trong đoạn bằng chứng, nhưng bộ đọc không nhận đơn vị ("cây xanh", "m2", "MWp"), nên coi là "khác đơn vị". **2/26:** phạm vi phát thải bị đọc theo cả câu (dòng "Phạm vi 1: …; Phạm vi 2: …" bị gán phạm vi {1,2} cho mọi số) | Sửa hẹp: thêm đơn vị m2/m²/ha, MWp/kWp/MW, đếm cây; đọc phạm vi theo từng số (như cách đã làm với mảng kinh doanh) |
| Cột "kết hợp" của mốc LLM, tính từ câu trả lời đã lưu, không gọi API thêm (luật kết luận; LLM chỉ gắn cờ ở ca luật chưa quyết, và **chỉ khi cả hai lần hỏi đều nói "mâu thuẫn"**) | Câu gốc (M0): **0/75** cờ giả. M1: 9 → **45/72**. M2: 5 → **16/16**. M5: 2 → **16/20**. Nếu chỉ cần một lần hỏi nói "mâu thuẫn" thì có 1 cờ giả trên câu gốc | Điều kiện "hai lần hỏi đồng ý" bỏ được cờ giả duy nhất của LLM. Kiến trúc đã có sẵn chế độ chỉ gắn cờ (`llm_stance: on_ambiguous`, mô hình không có quyền kết luận). **Lưu ý:** đo bằng gpt-oss-120b qua API; bản cài nội bộ dùng mô hình cục bộ sẽ cho số khác. Trên báo cáo thật chưa đo: ngày 28/09, Hòa Phát từng cho 10 cờ, phần lớn sai |
| Bật cờ "nguồn độc lập" (phát lại ngày 11/11, `results/replay_support_guard.json`) | GS-Eval v2: kết luận dứt khoát 9 → 4; precision 0,33 → **0,75**; "ủng hộ" sai 5 → **0**. Trên toàn bộ câu đã lưu: SUPPORTED 24 → 16 | GS-Bench không đổi, vì bằng chứng ở đó là nguồn ngoài. Hòa Phát: 1 câu SUPPORTED → PARTIAL. Cần chạy lại vì từ đó đã có luật mới |
| Mẫu báo cáo BTC | Ghi đúng "giải pháp **AI hoặc** lượng tử". Tên hai tiêu chí cuối: tiêu chí 5 "Khả năng ứng dụng và triển khai thực tế" (15%), tiêu chí 6 "Trình bày, tài liệu" (10%) | Không bắt buộc có thành phần lượng tử, như chuyên gia nói |
| Công ty chưa dùng ở bộ đo nào (ứng viên tập giữ riêng) | Trong 21 công ty của kho thu thập, đã dùng: BVH, CTD, DHG, HPG, PNJ, POW, TRA, VNM, SAB. Chưa dùng, có tài liệu: **PAN** (51 tài liệu), **DPR** (35), **PHR** (18), **BID** (8, ngân hàng), **MWG** (7), **FMC** (6), **CNG** (6), **VCS** (4), CDN (51, cảng, cùng ngành GMD) | Chọn 3–5 công ty khác ngành, ví dụ PAN, DPR hoặc PHR, BID, VCS. Phải kiểm từng công ty có cặp "báo cáo cần kiểm + tài liệu đối chiếu" không |
| Giao diện hiện điểm 0–100 | `ClaimPanels.jsx` có hiện "Tổng X/100". Câu miễn trừ trách nhiệm (`lib/labels.js`) chưa có ý "không gắn cờ ≠ đã xác nhận" | Ẩn con số và thêm câu miễn trừ là sửa nhỏ |

## 3. Đánh giá từng góp ý

### 3.1. Dùng được ngay; máy làm được
| Góp ý | Đánh giá |
|---|---|
| H1: sửa bước trích tuyên bố | **Làm, nhưng theo nguyên nhân thật:** thêm loại dự phòng `disclosed_figure` (chỉ số đã biết + số liệu) và từ vựng nước, điện. Phải đi cùng sửa đơn vị và phạm vi (nút thắt 2), nếu không M1 gần như không tăng |
| H4: chỉ "ủng hộ" khi có nguồn độc lập | **Làm.** Đổi mặc định, chạy lại 4 cổng và phát lại |
| H2 + Q6: hiển thị hai trục và loại căn cứ | **Làm.** Suy ra từ trường đã có (quan hệ của đoạn, `relation_method`, `source_type`); không đổi logic kết luận. **Sửa lại một điểm:** `financial` trong hệ thống gồm cả báo cáo thường niên, không chỉ BCTC đã kiểm toán. Nhãn nên là "tài liệu tài chính của doanh nghiệp", không ghi "đã kiểm toán" |
| D2: ẩn điểm 0–100 trên giao diện | **Làm.** Giữ điểm ở bên trong để xếp thứ tự; báo cáo ghi "đặt theo chuyên môn, chưa hiệu chỉnh" |
| H9: "hiện nay → năm báo cáo" | **Làm**, ghi `period_source`. Kỳ suy ra không được tính là thuộc tính khớp |
| H5: cờ ngôn ngữ quảng bá mức nhẹ | **Làm.** Chỉ gắn cờ; không đổi kết luận, không cộng vào thành phần "từ mơ hồ" |
| D5: thêm kiểu cài lỗi | **Làm**, rẻ: đổi đơn vị (kg ↔ tấn, MWh ↔ GWh), ranh giới phóng to (nhà máy → toàn tập đoàn), mục tiêu viết thành đã đạt, cường độ viết thành tổng. **Lưu ý:** chênh ≥ 100 lần là AMBIGUOUS theo thiết kế, nên kỳ vọng là "không còn ủng hộ, cần người xem", không phải "mâu thuẫn" |
| H3: bảng LLM / luật / kết hợp trên cùng 183 ca | **Phần lớn đã có.** Báo cáo đã so cùng mẫu số (47/72 so với 9/72). Cột "kết hợp" vừa tính xong (mục 2), chỉ cần đưa vào bảng |
| Q12: câu "không gắn cờ ≠ đã xác nhận" | **Làm**: một câu trong giao diện và giấy làm việc |
| Danh mục kiểm trước phát hành | **Làm** sau khi dừng code: một trang số đo, có ngày và người duyệt |
| Q4: lấy mẫu ngẫu nhiên ngoài hàng soát | Làm dạng tuỳ chọn (`random_audit_slots`, mặc định 0) hoặc thành danh sách riêng, không tính vào hàng soát. 30 mẫu cho mỗi báo cáo là quá nhiều; nên gộp nhiều báo cáo |

### 3.2. Đã làm rồi (chuyên gia không biết)
- **H7, chạy chẩn đoán "chỉ nạp báo cáo cần kiểm":** đã chạy (M1i: 0/101 ở cả chế độ `flag` và `contradict`). Trên một báo cáo tự dựng có tiêu đề bảng số liệu thì luật chạy đúng. → Để tắt, ghi vào giới hạn. Việc còn lại chỉ là mở tay 5 ca, giá trị thấp.
- **D10:** câu trả lời của mốc LLM đã được lưu lại kèm ngày và phiên bản.
- **H3:** mẫu số đã thống nhất trong báo cáo. Riêng mục H3 của tài liệu gửi chuyên gia viết lẫn mẫu số.

### 3.3. Cần sửa lại so với góp ý
- **D4: không dùng lại được script GS-Mutation cho tập giữ riêng.** Script đó cần cặp tuyên bố–bằng chứng đã có nhãn "ủng hộ", mà công ty mới thì không có. Thay bằng **giao thức không cần nhãn trên báo cáo đầy đủ:**
  1. chạy pipeline;
  2. đọc tay **mọi** kết luận "mâu thuẫn" (đo vu oan) và **mọi** kết luận "ủng hộ" (đo bỏ lọt);
  3. cài lỗi ngay trong văn bản báo cáo vào các tuyên bố đã trích, rồi xem có bắt được không.

  Cùng script này cho luôn **recall@k của hàng soát** (Q5), điều mà ca đơn lẻ của GS-Mutation không đo được.
- **D.2 #1, mô hình T1 chạy song song:** chưa cần. Sửa từ điển có thể đã đạt điểm rẽ ≥ 70%. Môi trường `.venv` cũng không có torch.
- **H10, đồng bộ phiên mẫu:** không chỉ là dựng lại. Câu chuyện "tiền lệ" trên bản trình diễn dựa vào việc người soát ghi đè A2 từ "ủng hộ một phần" sang "mâu thuẫn"; nay máy đã tự ra "mâu thuẫn". **Đề xuất:** giữ hai phiên cũ, ghi chú là chạy sáng 14/11, và **thêm một phiên Ca A mới** để kể trọn vòng học:
  1. người soát ghi đè;
  2. máy đào luật đề xuất cụm từ, đo không đạt;
  3. đội viết luật tỷ trọng tất định;
  4. máy tự bắt A2.

  Đây là một ví dụ tốt cho tiêu chí Giải pháp.

### 3.4. Cần người hoặc nguồn ngoài
| Việc | Ai | Ghi chú |
|---|---|---|
| D1: gán `is_claim` + thuộc tính, 100–150 câu, kappa trên 50 câu đầu | 2 người trong đội | Máy chuẩn bị sẵn: hướng dẫn 1–2 trang, tệp câu (gồm cả câu bộ trích đã bỏ), script tính kappa và precision/recall |
| D4: chọn và khoá tập giữ riêng | Đội chọn, **người ngoài đội** giữ | Ứng viên ở mục 2 |
| D6: một báo cáo phân bổ vốn trái phiếu xanh thật | Đội, hoặc máy tìm trên web (tối đa 2 giờ) | Nguồn chuyên gia gợi ý **[cần kiểm]**: chuyên trang trái phiếu doanh nghiệp của HNX, trang quan hệ nhà đầu tư của tổ chức phát hành, báo cáo ý kiến bên thứ hai |
| D11: thử nghiệm đo thời gian với 2–3 sinh viên | Đội | Ghi rõ là "sơ bộ" |
| Pháp lý (6.2, 6.3) | Người có chuyên môn luật | QĐ 21/2025/QĐ-TTg và danh mục kiểm kê khí nhà kính hiện hành là **[cần kiểm]** |

## 4. Thứ tự thực hiện đề xuất

**Nguyên tắc:** gom mọi thay đổi mã vào một đợt, đo xong mới sửa tài liệu **một lần**. Mỗi thay đổi ở đợt 1 đều làm đổi số của Hòa Phát (156 tuyên bố, hàng đợi 8/172, phân bố 154/1/1). Các số này đang nằm trong báo cáo, slide, hướng dẫn, bản trình diễn, và có thể cả video.

**Đợt 1: mã, máy làm (khoảng 1 ngày).** Mỗi bước chạy cổng: GS-Mutation (vu oan phải giữ 0/290), GS-Bench, evaluate-real, phát lại 1.766 câu thật, pytest.
1. Trích tuyên bố: thêm loại `disclosed_figure` và từ vựng nước, điện. Đo recall trích trên GS-Mutation; đo số tuyên bố Hòa Phát tăng bao nhiêu; đọc mẫu 30 câu mới để ước lượng độ chính xác.
2. Đơn vị (m2, ha, MWp, cây) và phạm vi theo từng số.
3. Cờ "nguồn độc lập" bật mặc định.
4. "Hiện nay", cờ quảng bá nhẹ.
5. Hiển thị hai trục, loại căn cứ, ẩn điểm 0–100, câu miễn trừ.
6. Bốn kiểu cài lỗi mới; chạy lại GS-Mutation.

**Song song: người** (D1, D4, D6), máy chuẩn bị bộ công cụ cho D1 và script giao thức giữ riêng.

**Đợt 2, sau khi dừng code 18/11:**
- chạy tập giữ riêng một lần;
- cập nhật báo cáo, slide, hướng dẫn một lần; thêm bảng LLM / luật / kết hợp và trình bày hai nhóm số đo (trước–sau và giữ riêng);
- thêm phiên Ca A mới vào bản trình diễn;
- viết danh mục kiểm phát hành;
- tạo checkpoint và đóng gói zip.

**Nếu trễ thì cắt theo thứ tự:** bước 6 → bước 5 (phần giao diện) → bước 4. **Không cắt:** bước 1, bước 2, bước 3.
