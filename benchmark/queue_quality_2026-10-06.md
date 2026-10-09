# Chất lượng hàng đợi soát trên Hòa Phát — trước và sau rà soát 06/10/2026

Cùng hai tài liệu (HPG BCPTBV 2025 + BCTN 2024, 264 trang), chế độ `offline` (không gọi mô hình), laptop i7-1355U không GPU, 16 GB RAM. Đo bằng `quantum_gw.cli analyze` trong tiến trình con, lấy mẫu bộ nhớ mỗi 0,5 s.

| | Trước (`1b24695c`, 05/10) | Sau (`4fab851a`, 06/10) |
| --- | ---: | ---: |
| Thời gian | 115,6 s | 107,4 s (3 lần chạy: 107–121 s) |
| RAM đỉnh | 1.329 MB | 1.331 MB |
| Tuyên bố | 156 | 156 |
| Kết quả kiểm chứng | 153 khớp một phần · 2 ủng hộ · 1 chưa đủ bằng chứng | **không đổi** (thay đổi chỉ chạm thứ tự soát) |
| Mức rủi ro | 154 MEDIUM · 2 LOW | **không đổi** |
| Số liệu công bố đọc được | **57** (36 %, 15 tấn, 5 tCO2e, 1 kWh); **34 không gắn được chỉ số môi trường nào** | **16**; 0 không gắn chỉ số |
| Mục trong hàng đợi | 22 / 213 | **9 / 172** |
| Mục đầu hàng đợi là câu giải thích công nghệ, câu nối ý, chữ dính cột | 10 trong 22 ("Vòng đời của thép đi qua hai giai đoạn…", "Ngược lại, EAF có mức phát thải thấp hơn…", "Quan trọng hơn, biogas tạo ra khí Mê-tan…", "VIỆT NAM (VSA) NAM (VCCI) (VAMI)…") | 0 trong 9 — cả 9 là câu doanh nghiệp tự nói về mình |
| "Số liệu" rác trong hàng đợi | 2 ("tCO2e, chiếm: 0 %"; "điều chỉnh carbon. GIỚI TÍNH QUỐC TỊCH: 100 %") | 0 |
| Văn bản pháp lý bị trích sai | NĐ 83/2026 (chỉ sửa phần ô-dôn) đi kèm **55** tuyên bố phát thải | **0** |
| Lý do xếp hạng | lẫn tiếng Anh ("chỉ số emissions (hệ số 1.00)", "kết luận PARTIALLY_SUPPORTED") | tiếng Việt ("nhóm phát thải khí nhà kính", "kết quả “ủng hộ một phần”, thiếu 4/5 thuộc tính") |
| Cộng lại bảng KNK | 22.540.603 + 933.876 = 23.474.479; công bố 23.474.480 → khớp (làm tròn) | như trước |

## Nguyên nhân gốc, đã sửa

1. **Gộp dấu "cộng" / "công"** (`agents/figures.py`): nhãn dòng tổng được so trên chữ đã bỏ dấu, nên "Tổng công ty …", "công suất", "công nghiệp", "cộng đồng" đều thành "dòng tổng" — cùng loại lỗi "thiếu"/"thiêu" đã sửa ở bộ cue ngày 20/09. Nay so trên chữ có dấu, tách nghĩa "tổng công ty", "cộng đồng".
2. **Nhãn vượt ranh giới câu**: "…điều chỉnh carbon. GIỚI TÍNH QUỐC TỊCH 100 %" được đọc thành dòng phát thải.
3. **Đơn vị của cột bên cạnh**: "Cộng 23.474.480 100%" bị đọc thành 23 triệu phần trăm; hệ số "triệu/tỷ" bị bỏ ("5,6 triệu tấn" thành 5,6 tấn); "nước" nghĩa quốc gia ("cả nước") bị đọc là nước sử dụng.
4. **Dòng % hoặc tấn không gắn chỉ số môi trường** (tỷ lệ sở hữu công ty con, cơ cấu lao động, công suất nhà máy) nay không còn là "số liệu công bố".
5. **Ai đang nói** (`priority-v1.1`): câu không nêu chủ thể là doanh nghiệp (tên tự nhận diện: "Hòa Phát") và không có số liệu → trọng yếu ×0,75; chữ dính cột → ×0,5. Chỉ đổi thứ tự, không đổi kết quả kiểm chứng.
6. **Registry pháp lý**: NĐ 83/2026 gắn sai nhãn phát thải; chuỗi sửa đổi kéo mọi văn bản sửa NĐ 06/2022 vào mọi tuyên bố bất kể sửa điều gì — nay chỉ kéo văn bản sửa đúng vấn đề đang xét.

## Còn lại (không sửa trong lượt này)

- Mục #1 "HÒA PHÁT trò nền tảng…" là chữ gãy dòng ("vai trò"); mục #5 là tiêu đề dính câu kể — bộ trích tuyên bố (ISSUES P5) cần gold 100 câu để siết mà không mất recall.
- Hàng đợi vẫn toàn câu định tính: số liệu tổng KNK đã cộng khớp nên điểm khoảng trống thấp — đúng thiết kế (P5), nhưng nghĩa là **thứ tự hiện tại chưa được ai kiểm** — đo "độ chính xác thứ tự" cần nhãn của Quỳnh.
- "Cộng 193.404 tấn" trang 41 (bảng năng lượng) lấy nhầm đơn vị của bảng khác cùng trang; "7,085" và "6,838" (trang 50) mơ hồ dấu thập phân giữa chuẩn Việt và Anh.

Tái hiện: `QUANTUM_LLM_STANCE=off python -m quantum_gw.cli analyze data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf --roles claim_source,evidence --source-types internal,internal`.
