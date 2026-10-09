# 02 · Pháp lý Việt Nam cho tuyên bố môi trường

**Cập nhật:** 06/10/2026 · Nguồn chi tiết và trích dẫn nguyên văn: [sources/…phap-ly-thi-truong-an-le-VN.md](sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md) Phần A; luật dữ liệu: [sources/…mo-hinh-chi-phi-phan-cung.md](sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md) §6.
**Lưu ý:** đây là tổng hợp để định hướng kỹ thuật, không phải tư vấn pháp lý. Mọi quy tắc đưa vào `configs/legal/` phải qua Thảo (trường `reviewed_by`).

## 1. Mười hai văn bản trong registry — ngày đã đối chiếu bản ký

| Văn bản | Ký | Hiệu lực | Sửa đổi bởi | Trạng thái trong registry (06/10) |
| --- | --- | --- | --- | --- |
| Luật BVMT 72/2020/QH14 | 17/11/2020 | 01/01/2022 | Luật 11/2022, 16/2023, 18/2023, 47/2024, 54/2024, **146/2025 (hiệu lực 01/01/2026)** | Đúng ngày. **Repo chỉ có Điều 1–89**; thiếu Đ.91 (KNK), 114, 119, 139, **145**, 149–150 |
| NĐ 08/2022/NĐ-CP | 10/01/2022 | 10/01/2022 | NĐ 05/2025, NĐ 48/2026 | Đúng |
| NĐ 05/2025/NĐ-CP | 06/01/2025 | 06/01/2025 | — | Đúng |
| NĐ 48/2026/NĐ-CP | **29/01/2026** | **29/01/2026** | — | **Đã sửa 06/10** (trước ghi 01/01/2026) — chờ Thảo xác nhận |
| NĐ 06/2022/NĐ-CP | 07/01/2022 | 07/01/2022 | NĐ 119/2025, NĐ 83/2026 | Đúng |
| NĐ 119/2025/NĐ-CP | 09/06/2025 | **01/08/2025** (Đ.2) | — | **Đã sửa 06/10** (trước ghi hiệu lực 09/06/2025) — chờ Thảo xác nhận |
| NĐ 83/2026/NĐ-CP | **23/03/2026** | **23/03/2026** | — | **Đã sửa 06/10**: chỉ sửa thủ tục **chất được kiểm soát (ô-dôn/HFC)** — Đ.24, 26, mẫu Phụ lục VI; **không** có nội dung kiểm kê KNK. Trước đó bị gắn nhãn `emissions`, nên **mọi tuyên bố phát thải đều bị trích kèm NĐ 83/2026** — chờ Thảo xác nhận |
| QĐ 13/2024/QĐ-TTg | 13/08/2024 | 01/10/2024 | thay QĐ 01/2022 | Đúng |
| QĐ 21/2025/QĐ-TTg | 04/07/2025 | 22/08/2025 | thẩm quyền ban hành danh mục chuyển cho Bộ trưởng NN&MT (NĐ 48/2026 Đ.31) | Đúng |
| TT 17/2022/TT-NHNN | 23/12/2022 | 01/06/2023 | — | Đúng |
| TT 96/2020/TT-BTC | 16/11/2020 | 01/01/2021 | TT 68/2024, TT 18/2025, TT 08/2026; **dự thảo thay thế lấy ý kiến tới 07/10/2026** | Đúng ngày; thiếu danh sách văn bản sửa đổi |

Tất cả [VERIFIED] (bản ký số trên datafiles.chinhphu.vn, đọc qua OCR; điều khoản hiệu lực trích nguyên văn ở tài liệu gốc A.4). Hai lần kiểm độc lập (nhóm đọc PDF 28/09, nghiên cứu 05/10) và kiểm lại trên tệp điều khoản trong repo 06/10 cho cùng kết quả.

## 2. Nghĩa vụ đặt lên ai — điều dễ nhầm nhất

| Chủ thể | Nghĩa vụ | Căn cứ | Hệ quả cho kiểm chứng |
| --- | --- | --- | --- |
| **Cơ sở** (nhà máy, địa điểm) trong danh mục QĐ 13/2024 — 2.166 cơ sở | Kiểm kê KNK cấp cơ sở **2 năm/lần** cho năm 2024 trở đi, nộp UBND tỉnh trước 31/3 từ 2025 | NĐ 06/2022 Đ.11.4(b), sửa bởi NĐ 119/2025 | Nghĩa vụ ở **cơ sở**, báo cáo của doanh nghiệp ở **cấp tập đoàn** → phải ánh xạ cơ sở ↔ công ty con ↔ công ty niêm yết trước khi nói "thuộc diện" |
| Nhà máy **nhiệt điện, thép, xi măng** trong danh mục | 2 năm/lần **cho năm 2026 trở đi**, **thẩm định bởi tổ chức độc lập**, nộp Bộ NN&MT trước **01/12 từ 2027** | NĐ 119/2025 Đ.11.4(c), 11.6a | Một BCTN 2024–2025 nói "số liệu KNK đã được thẩm định theo NĐ 06" cần bằng chứng riêng — chu kỳ thẩm định bắt buộc chưa bắt đầu |
| Cơ sở trong danh mục | Báo cáo **giảm nhẹ** phát thải hằng năm, nộp UBND tỉnh trước 31/3 **từ 2027**; kế hoạch giảm nhẹ 2026–2030 | NĐ 119/2025 Đ.10.3, 13.4 | Tách "báo cáo kiểm kê (2 năm)" ≠ "báo cáo giảm nhẹ (hằng năm)" ≠ "báo cáo công tác BVMT (hằng năm, Luật BVMT Đ.119)" |
| **Công ty đại chúng** | Báo cáo thường niên theo Phụ lục IV, mục 6: **6.1 KNK trực tiếp và gián tiếp**, 6.2 vật liệu, 6.3 năng lượng, 6.4 nước, **6.5 số lần và số tiền bị phạt về môi trường**, 6.8 thị trường vốn xanh; công bố trong 20 ngày sau BCTC kiểm toán, ≤ 110 ngày sau năm tài chính | TT 96/2020 Đ.10.2, Phụ lục IV | Bộ chỉ tiêu **kỳ vọng** để phát hiện "công bố chọn lọc" (mẫu 6). TT 96 **không** quy định Scope, ranh giới hợp nhất, năm gốc hay đảm bảo độc lập → thiếu những thứ đó là "chưa đủ bằng chứng về phạm vi", không phải "sai" |
| Công ty đại chúng **ngành tài chính, ngân hàng, chứng khoán, bảo hiểm** | **Được miễn chỉ 6.1, 6.2, 6.3**; 6.4, 6.5 vẫn áp dụng | Ghi chú Phụ lục IV TT 96 | Không gắn cờ ngân hàng vì thiếu số KNK; **vẫn** kỳ vọng nước và tuân thủ |
| Tổ chức niêm yết / công ty đại chúng quy mô lớn | Công bố thông tin định kỳ **bằng tiếng Anh từ 01/01/2025**, phải thống nhất bản tiếng Việt | TT 68/2024 (sửa TT 96) | Cơ hội: so cùng tuyên bố giữa hai bản ngôn ngữ (mẫu 14) |
| **Tổ chức tín dụng** | Quản lý rủi ro môi trường cho dự án thuộc Phụ lục III–V NĐ 08/2022 | TT 17/2022 | Không có nghĩa vụ công bố công khai danh mục dự án; dữ liệu tín dụng xanh "không nhất quán qua các năm" (nghiên cứu) → kiểm nhất quán chuỗi thời gian |
| **Tổ chức phát hành trái phiếu xanh** | Cung cấp thông tin ĐTM, giấy phép, sử dụng vốn; **công bố hằng năm tới khi đáo hạn** | Luật BVMT Đ.150.3; NĐ 08/2022 Đ.157.6 | Thiếu công bố sử dụng vốn = khoảng trống bằng chứng cụ thể |
| **Chủ dự án thuộc danh mục phân loại xanh** | Xác nhận bởi cơ quan thẩm định hoặc **tổ chức độc lập đạt ISO/IEC 17029 hoặc VSAE/ISAE 3000**; Bộ NN&MT công bố danh mục dự án trên cổng của Bộ | QĐ 21/2025 Đ.4–9 | Tuyên bố "dự án xanh" có thể tra danh mục công bố; Phụ lục I là "từ điển bằng chứng" theo loại dự án |
| **Người bán sản phẩm "thân thiện môi trường"** | Sản phẩm phải **được cơ quan có thẩm quyền chứng nhận hoặc công nhận**; Nhãn sinh thái Việt Nam hiệu lực 36 tháng, Bộ công bố danh mục | Luật BVMT Đ.145; NĐ 08/2022 Đ.145–150 | Tuyên bố "thân thiện môi trường" không kèm chứng nhận → cần xem xét (mẫu 1, 8) |

## 3. "Móc" pháp lý cho tuyên bố môi trường gây hiểu nhầm

Việt Nam không có luật riêng về green claims. Các căn cứ gần nhất — dùng làm **ngữ cảnh**, không để kết luận vi phạm:

| Căn cứ | Nội dung | Áp cho | Nhãn |
| --- | --- | --- | --- |
| Luật Bảo vệ quyền lợi người tiêu dùng **19/2023/QH15** Đ.10.1(a) (hiệu lực 01/07/2024) | Cấm lừa dối, gây nhầm lẫn bằng thông tin sai lệch, không đầy đủ, không chính xác — kể cả về **giấy tờ chứng nhận** | Quan hệ với người tiêu dùng (không áp trực tiếp cho BCTN gửi nhà đầu tư) | [VERIFIED] |
| Luật Quảng cáo 16/2012, sửa bởi **75/2025/QH15** (hiệu lực 01/01/2026) | Đ.8.9 cấm quảng cáo gây nhầm lẫn; Đ.8.10 so sánh phải có tài liệu hợp pháp chứng minh; Đ.8.11 "nhất/số một" phải chứng minh; **Đ.19 mới: nội dung phải trung thực, chính xác, không gây hiểu nhầm**; Đ.15a người có ảnh hưởng phải kiểm tra tài liệu | Quảng cáo (nội dung BCTN thường được dùng lại trong truyền thông) | [VERIFIED] |
| Luật Cạnh tranh 23/2018 Đ.45 | Thông tin gian dối/gây nhầm lẫn để lôi kéo khách hàng | Cạnh tranh | [SECONDARY] |
| Luật BVMT Đ.6.9 | Cấm làm sai lệch thông tin, gian dối trong BVMT **dẫn đến hậu quả xấu** | Có điều kiện hậu quả | [VERIFIED] |
| NĐ 29/2026 Đ.4.5 | Cấm thông tin sai lệch để thao túng giá hạn ngạch, tín chỉ các-bon | Sàn các-bon | [VERIFIED] |
| Xử phạt: NĐ 45/2022 (môi trường), NĐ 156/2020 sửa bởi 128/2021 (chứng khoán), NĐ 98/2020 sửa bởi 24/2025 (thương mại, NTD) | Mức phạt cụ thể | — | **[UNVERIFIED]** — chưa đọc bản gốc; không đưa vào quy tắc |

## 4. Thị trường các-bon — nguồn đối chiếu mới từ 2026

- **QĐ 232/QĐ-TTg (24/01/2025)**: Đề án thị trường các-bon — thí điểm 2025–2028, chính thức từ 2029 [VERIFIED].
- **NĐ 29/2026 (19/01/2026)**: sàn giao dịch các-bon trong nước; HNX công bố kết quả giao dịch cuối mỗi ngày [VERIFIED].
- **QĐ 263/QĐ-TTg (09/02/2026)**: hạn ngạch thí điểm 2025: 243.082.392 tCO2tđ; 2026: 268.391.454 tCO2tđ cho **34 nhiệt điện, 25 thép, 51 xi măng** [SECONDARY].
- Sàn khai trương **29/06/2026** tại HNX [SECONDARY].
- NĐ 06/2022 Đ.19 (sửa bởi 119/2025): tín chỉ phải cho kết quả giảm từ 01/01/2021; bù trừ ≤ 30% hạn ngạch; **tín chỉ đã dùng để giảm phát thải tự nguyện không được giao dịch tiếp** [VERIFIED].

**Hệ quả:** với 110 cơ sở có hạn ngạch, tuyên bố "giảm phát thải"/"đạt hạn ngạch" có nguồn đối chiếu bên ngoài; tuyên bố "trung hòa các-bon nhờ tín chỉ" cần bằng chứng hủy/khóa tín chỉ và nguồn gốc (mẫu 9).

## 5. Sắp thay đổi — cần theo dõi trước Chung kết

| Việc | Trạng thái | Ảnh hưởng |
| --- | --- | --- |
| **Dự thảo thông tư thay TT 96/2020** (ngày 25/09/2026) | Lấy ý kiến tới **07/10/2026** [SECONDARY] | Phụ lục ESG riêng, tham chiếu ISSB/IFC, 4 trụ cột, **"công bố hoặc giải trình"**; hạn BCTN 120 ngày. Nếu ban hành, bộ chỉ tiêu kỳ vọng của mẫu 6 đổi theo |
| Luật 146/2025/QH15 | Hiệu lực 01/01/2026 [VERIFIED] | Sửa Luật BVMT chủ yếu về thủ tục; Đ.145, 149, 150 **không** đổi |
| Văn bản thay QĐ 21/2025 do Bộ trưởng NN&MT ban hành | Chưa xác minh đã có hay chưa [UNVERIFIED] | Tiêu chí phân loại xanh có thể đổi cơ quan ban hành |

**Bên ngoài:** EU CBAM áp dụng chính thức từ 01/01/2026 (thép, xi măng là hai ngành Việt Nam xuất khẩu nhiều) [VERIFIED]; Directive 2024/825 áp dụng từ 27/09/2026 [VERIFIED]; Green Claims Directive ở trạng thái "Blocked" [VERIFIED]; Omnibus (EU) 2026/470 thu hẹp CSRD [VERIFIED]. Việt Nam chưa có lộ trình ISSB chính thức [UNVERIFIED].

## 6. Luật dữ liệu khi vận hành GreenScan với AI đám mây

| Văn bản | Hiệu lực | Điểm chạm |
| --- | --- | --- |
| **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** | 01/01/2026 [VERIFIED] | Dùng nền tảng **ở nước ngoài** để xử lý dữ liệu cá nhân thu thập tại Việt Nam là **chuyển xuyên biên giới** (Đ.20.1c) → hồ sơ đánh giá tác động trong 60 ngày; xử lý bằng AI phải phân loại rủi ro (Đ.30); phạt tới 5% doanh thu với vi phạm chuyển xuyên biên giới |
| **NĐ 356/2025/NĐ-CP** (31/12/2025) | 01/01/2026 [VERIFIED] | **Bãi bỏ NĐ 13/2023**; dữ liệu cá nhân trên đám mây phải mã hoá khi lưu và truyền (Đ.12); miễn đánh giá với dữ liệu "đã được công khai theo quy định của pháp luật" (Đ.17.3) — tên lãnh đạo trong báo cáo đã công bố **có thể** thuộc diện này (suy luận — Thảo xác nhận) |
| Luật Kiểm toán độc lập 67/2011 Đ.43 | — [VERIFIED] | **Không được tiết lộ hồ sơ kiểm toán** khi chưa có chấp thuận của khách hàng |
| Luật Trí tuệ nhân tạo 134/2025/QH15; NĐ 142/2026 | [UNVERIFIED hiệu lực] | Phân loại mức rủi ro hệ thống AI, thông báo/gắn nhãn; GreenScan thuộc mức nào: chưa xác định |

**FPT AI Marketplace (Serverless)** có thể tự chuyển yêu cầu sang Nhật khi quá tải; chỉ gói Dedicated khoá vùng. Chính sách quyền riêng tư của FPT AI Factory (đọc 05/10) **vẫn viện dẫn NĐ 13/2023 đã hết hiệu lực** và không nói prompt có được lưu hay dùng huấn luyện [VERIFIED].

**Quy tắc vận hành (áp dụng cho sản phẩm từ 06/10):**

| Loại tài liệu | Ví dụ | Chế độ chạy được phép |
| --- | --- | --- |
| A — Công khai | BCPTBV, BCTN đã công bố | `offline` hoặc `cloud` (FPT) |
| B — Nội bộ, chưa công bố | bản thảo, số liệu nội bộ | `offline`, `gpu` tại chỗ, hoặc FPT Dedicated có hợp đồng xử lý dữ liệu |
| C — Mật nghề nghiệp | giấy làm việc kiểm toán | **chỉ** `offline` / `gpu` trên hạ tầng của đơn vị |

Giao diện báo rõ khi nào tài liệu bị gửi ra ngoài (huy hiệu "Có dùng AI đám mây" và cảnh báo trước khi chạy).

## 7. Việc cho registry và bộ quy tắc

1. Thảo xác nhận ba sửa đổi §1 → điền `reviewed_by`.
2. Tải Công báo 1187+1188 (Luật BVMT Điều 90–171), parse Đ.91, 114, 119, 139, 145, 149, 150.
3. Ba quy tắc ưu tiên (đã có trong bàn giao 25/09, nay đủ căn cứ ngày tháng): (1) đối tượng kiểm kê theo QĐ 13/2024 + lịch theo ngành NĐ 119/2025; (2) mục 6 Phụ lục IV TT 96 với miễn trừ đúng **chỉ 6.1–6.3, chỉ bốn ngành tài chính**; (3) kỳ báo cáo kiểm kê/giảm nhẹ.
4. Thêm khuyến nghị `amended_by` cho Luật BVMT và TT 96; cờ "đang có dự thảo thay thế" cho TT 96.
5. Luật 19/2023 và Luật Quảng cáo (sửa 2025): thêm như **tham chiếu ngữ cảnh**, không dùng kết luận.
