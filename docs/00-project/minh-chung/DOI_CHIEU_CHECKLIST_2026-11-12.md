# Đối chiếu checklist AQ2026-119 với việc đã làm (12/11/2026)

Checklist: [AQ2026 - 119 - Check list công việc](https://docs.google.com/spreadsheets/d/18r2JLcgvSxvJwlMSlpaepjpE6jmhBxbaEO4_pGQalJY/edit?gid=1676970004), tab "Trang tính3".

**Nguyên tắc (Nhân đặt 12/11):**
- Việc của Nhân được đối chiếu với codebase hiện tại.
- Việc của Thảo và Quỳnh được kiểm bằng tệp thành phẩm của hai bạn trên Drive, rồi ghi kết quả về repo.
- Việc nào "Đã hoàn thành" phải có tài liệu thành phẩm (Google Docs, gộp theo nhóm) trong thư mục Drive gốc "AIquantum", và có link ở cột Thành phẩm.
- Việc do Nhân làm ghi `nguyenchonnhan@gmail.com` ở cột Chủ sở hữu.

## Căn cứ đã kiểm

- **Bài kiểm:** toàn bộ `pytest tests` qua 638/638. Riêng 6 tệp gắn với việc đã xong qua 57/57: claim_quality, disclaimer, independent_support, issa5000_patterns, ocr_confidence, ui_language.
- **Đường dẫn:** mọi đường dẫn nhắc trong cột Tiến độ đều có trong repo. Riêng `data/issa_samples/` vốn được ghi là "không dùng".
- **Bộ kiểm điểm yếu** `benchmark/weakness_check_2026-11-12.json`: 6 đạt, 9 chưa đạt, 2 chỉ để biết.
- **Thay đổi repo:** không có tệp nào đổi sau bản `cap_nhat_bang_2026-11-12.json` (22:27).

## Tệp của thành viên

| Việc | Người | Tệp trên Drive | Kết quả kiểm |
|---|---|---|---|
| 5 | Thảo | ISSA 5000 PDF (`10-DsBMweuEVL554eWMI10LL6B6irHqnH`) | Trùng md5 với `data/standards/iaasb/`. Giữ "Đã hoàn thành". |
| 3 | Thảo | Sheet "GreenScan - Phan Thanh Thảo - Báo cáo đảm bảo độc lập & đối chứng AI" (`1R1XfRxDBmZTDn4FFeSNsnE3dFgfi9m2orJx_APHZeuw`) | Khung 4 tab tốt, 8 báo cáo ứng viên. Nhưng chỉ Vinamilk có đủ đơn vị, chuẩn, mức. Tab bằng chứng chưa có câu trích, tab đối chiếu AI còn chữ mẫu, 9 bước hướng dẫn đều "Chưa bắt đầu". **Chuyển về "Đang thực hiện".** |
| 6 | Quỳnh | Thư mục "8 Báo cáo Đảm bảo mẫu" (`1VsCqdlv7Ok0nBSkc29RgmoxnacDi12tb`) | Bộ 8 báo cáo minh hoạ trùng md5 với repo. Giữ "Đã hoàn thành". Có thêm 4 báo cáo PTBV Việt Nam kèm tờ đảm bảo và 2 ảnh, xem dưới. |
| 7 | Quỳnh | Thư mục "Mục 7" (`1Kl_wP6nqg3fH0gIFODNHh8jZi9Q__Z1a`) | Implementation Guide và FAQ trọng yếu trùng md5 với repo. Giữ "Đã hoàn thành". |
| 47 | Quỳnh | (cùng thư mục việc 6) | Đã gom tờ đảm bảo, tên tệp ghi "Không sửa đổi" cho ACB và Novaland. **Chuyển sang "Đang thực hiện".** Kết quả đọc từng tờ: `data/standards/assurance_vn/bao_cao_dam_bao_vn.yaml`. |

Các việc khác của Thảo (46, 64, 52, 15) và Quỳnh (51, 16, 17) chưa thấy tệp thành phẩm trên Drive, nên giữ nguyên trạng thái.

**Kết quả đọc các tờ đảm bảo Quỳnh gom** (đọc lớp chữ PDF ngày 12/11, chưa có người soát):
- ACB 2023: KPMG, ISAE 3000, có giới hạn, chỉ số GRI chọn lọc, kết luận không sửa đổi.
- Novaland 2021: PwC, ISAE 3000 (Sửa đổi), có giới hạn.
- VPBank 2025: KPMG, ISAE 3000 (sửa đổi), có giới hạn, có đoạn nhấn mạnh. Mẫu câu này chưa có trong `configs/issa5000_conclusion_patterns.yaml`.
- Vinamilk 2022: PwC, ISAE 3000 (Revised), có giới hạn (ảnh chụp).
- PVCFC 2025: chỉ có lời doanh nghiệp nói Deloitte đảm bảo. Trang 140 là "ý kiến đảm bảo" của **kiểm toán nội bộ**, không phải đảm bảo độc lập.

## Đổi trên checklist

- **Trạng thái:**
  - Việc 3: Hoàn thành → Đang thực hiện.
  - Việc 47: Chưa bắt đầu → Đang thực hiện.
  - Việc 62: Chưa bắt đầu → Đang thực hiện. Bộ kiểm G1 không còn "[URL]", còn 13 dòng "9/172".
  - Việc 61 (đổi trước đó cùng ngày): Chưa bắt đầu → Hoàn thành, căn cứ khối `llm_stages_v1` và lượt HPG hai nhánh trong `docs/RUNS.md`.
- **Tiến độ:** ghi thêm kết quả kiểm cho việc 2, 3, 5, 6, 7, 40, 47, 57, 62, 64.
  - Việc 57: lượt chạy có bật AI còn 3 chỗ số kiểu Anh; bản mặc định tắt AI không bị.
- **Chủ sở hữu:** 34 việc Nhân làm trong codebase (cả đã xong và đang làm) ghi `nguyenchonnhan@gmail.com`.
- **Thành phẩm:** 22 việc hoàn thành link tới tài liệu nhóm. Việc 5, 6, 7 giữ link tệp của Thảo và Quỳnh.
- **Ảnh minh chứng (cột I):** 25 việc hoàn thành có ảnh; ô việc 3 đã xoá.

Sau khi đổi: 25 hoàn thành, 18 đang thực hiện, 20 chưa bắt đầu, 1 bị chặn (tổng 64).

## Tài liệu thành phẩm trên Drive

Thư mục "Thành phẩm các việc đã hoàn thành (AQ2026-119)": https://drive.google.com/drive/folders/1Ez-cAbfH6IwNCM9IdoX1T4BAOl3JX9Y-. Link từng tài liệu: `thanh_pham_drive_2026-11-12.json`. Dựng lại bằng `tools/minh_chung/thanh_pham_docs.py`; khi dựng lại, tài liệu cùng tên được ghi đè nhưng giữ nguyên link.

| Tài liệu | Việc |
|---|---|
| Thành phẩm 1 - Tài liệu đầu vào và nguồn dữ liệu | 1, 4 |
| Thành phẩm 2 - Đọc PDF, OCR và làm sạch văn bản | 8, 9, 11, 49, 50, 56 |
| Thành phẩm 3 - Chuẩn mực ISSA 5000 và báo cáo đảm bảo mẫu | 5, 6, 7, 12, 13, 14, 28, 48 |
| Thành phẩm 4 - Nhận diện số liệu và trích dẫn phát hiện | 18, 27 |
| Thành phẩm 5 - Đầu ra cho người dùng và tài liệu hướng dẫn | 34, 35, 43, 45, 57 |
| Thành phẩm 6 - Kiểm thử và đo lường | 58, 61 |

## Còn chờ quyết

- Việc 20: ghi chú đề xuất không làm.
- Việc 46: phạm vi MVP. Chặn 15, 32, 33.
- Việc 55: bật cờ nguồn độc lập mặc định cho bản nộp 20/11.
- Việc 52: dùng mô hình thị giác hay không.
- Việc 16: trọng số bằng nhau.
- `tools/check_weaknesses.py` mục E2 chỉ tìm tệp tên `*ablation*`, nên vẫn báo "chưa có" dù đã có số đo bật/tắt AI.
