# Kho tri thức GreenScan — tẩy xanh, pháp lý Việt Nam, AI kiểm chứng

**Lập:** 06/10/2026 · **Nguồn:** ba đợt nghiên cứu ngày 05–06/10/2026 (đọc văn bản gốc trên vanban.chinhphu.vn / congbao, trang cơ quan quản lý, arXiv / ACL Anthology / DOI) và số đo trên chính repo.
**Ai cần đọc:** cả nhóm. Quỳnh đọc 01, 03, 04, 05 §4. Thảo đọc 01, 02, 04. Nhân đọc 05, 06 và [`../04-data-ai/MODEL_ROUTING_AND_HARDWARE.md`](../04-data-ai/MODEL_ROUTING_AND_HARDWARE.md). Trước buổi hỏi đáp với hội đồng: đọc 06 §3–§4.

> Kho này trả lời ba câu: **tẩy xanh là gì và trông ra sao trong một báo cáo**, **luật Việt Nam thực sự đòi gì, đòi ai**, và **khoa học nói gì về việc dùng AI để kiểm** — kèm hệ quả cho từng phần của GreenScan.

## Đọc theo thứ tự

| # | Tài liệu | Trả lời câu hỏi |
| --- | --- | --- |
| 01 | [Tẩy xanh là gì — định nghĩa và 21 mẫu hình](01_TAY_XANH_DINH_NGHIA_VA_MAU_HINH.md) | Các định nghĩa có thẩm quyền; 21 mẫu hình, mỗi mẫu trông thế nào trong văn bản, máy kiểm được tới đâu, **GreenScan hôm nay kiểm được mẫu nào** |
| 02 | [Pháp lý Việt Nam](02_PHAP_LY_VIET_NAM.md) | Văn bản nào, hiệu lực từ ngày nào (đã đối chiếu bản ký), nghĩa vụ đặt lên **ai** (cơ sở / công ty niêm yết / ngân hàng / tổ chức phát hành), các "móc" pháp lý cho tuyên bố gây hiểu nhầm, luật dữ liệu cá nhân khi dùng AI đám mây |
| 03 | [Thực trạng công bố và nghiên cứu về Việt Nam](03_THUC_TRANG_VA_NGHIEN_CUU_VN.md) | Doanh nghiệp Việt Nam công bố thế nào (con số có nguồn), 31 nghiên cứu về Việt Nam, khoảng trống mà GreenScan lấp |
| 04 | [Án lệ và bài học](04_AN_LE_VA_BAI_HOC.md) | 32 vụ thực thi/tòa án quốc tế 2021–2026 và bối cảnh Việt Nam; 9 bài học → thủ tục kiểm tra cụ thể |
| 05 | [AI/NLP cho kiểm chứng và cách đo trên gold nhỏ](05_AI_NLP_VA_DO_LUONG.md) | Phương pháp, mô hình, bộ dữ liệu (kèm giấy phép), lỗi đã biết của LLM, κ và khoảng tin cậy thực tế với 60–100 cặp |
| 06 | [Hệ quả cho GreenScan](06_HAM_Y_CHO_GREENSCAN.md) | Việc cần làm rút ra từ tri thức (trước/sau 10/10), câu được nói và **không** được nói trước hội đồng |

Tài liệu gốc đầy đủ (trích dẫn nguyên văn, danh mục tài liệu tham khảo đánh số): [`sources/`](sources/)

| Tệp | Nội dung |
| --- | --- |
| [sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md](sources/2026-10-05_phap-ly-thi-truong-an-le-VN.md) | Pháp lý (A), thị trường (B), học thuật Việt Nam (C), án lệ (D), định nghĩa và typology (E) |
| [sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md](sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md) | Tổng quan tài liệu AI/NLP 2019–2026, mỗi nguồn có nhãn ADOPT / TEST / AVOID / CONTEXT |
| [sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md](sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md) | Giá FPT AI Marketplace, vùng xử lý dữ liệu, tăng tốc CPU, ba tầng phần cứng, Luật Bảo vệ dữ liệu cá nhân |

## Nhãn độ tin cậy (dùng thống nhất trong mọi tài liệu ở đây)

| Nhãn | Nghĩa | Được dùng trên slide? |
| --- | --- | --- |
| **[VERIFIED]** | Đã đọc văn bản gốc (bản ký số, Công báo, trang cơ quan ban hành, bài báo gốc) | Được |
| **[SECONDARY]** | Công ty luật, Big-4, báo uy tín, chỉ mục học thuật | Được, ghi nguồn |
| **[UNVERIFIED]** | Chưa xác nhận được | **Không** |
| **[self-reported]** | Số do tác giả mô hình tự công bố | Chỉ kèm chữ "tự công bố" |
| **[tự tính]** / **[ƯỚC TÍNH]** | Phép tính của nhóm từ số đo + giả định nêu rõ | Chỉ ở cột Target/Hypothesis |

## Quy tắc giữ kho này đúng

1. **Văn bản pháp luật thay đổi nhanh** (NĐ 06/2022 đã sửa hai lần trong 9 tháng; TT 96/2020 có dự thảo thay thế lấy ý kiến tới 07/10/2026). Mỗi khi đổi `configs/legal/LEGAL_SOURCE_REGISTRY.yaml`, cập nhật [02](02_PHAP_LY_VIET_NAM.md) §1 cùng commit.
2. **Không sửa số trong `sources/`** — đó là ảnh chụp ngày 05–06/10. Phát hiện mới ghi vào tài liệu tổng hợp kèm ngày.
3. Một nhận định chỉ được chuyển từ [UNVERIFIED] sang [VERIFIED] khi có người đọc bản gốc và ghi đường dẫn.
4. Ba việc chờ Thảo xác nhận (đã sửa trong registry 06/10, ghi rõ "pending"): hiệu lực NĐ 119/2025, NĐ 48/2026, phạm vi NĐ 83/2026 — xem [02](02_PHAP_LY_VIET_NAM.md) §1.
