# Kế hoạch thu thập dữ liệu v2 — sát chủ đề, có nguồn đối chứng độc lập

**Ngày:** 2026-09-17 · **Thay thế:** đợt crawl VN30 2026-08-07 làm nguồn gán nhãn (corpus cũ vẫn giữ cho retrieval)
**Người thực hiện:** Quỳnh (chọn DN, yêu cầu bằng chứng), Thảo (nguồn pháp lý/xử phạt), Nhân (crawler, trích mục, bảng)

## 1. Vì sao đổi hướng — số đo

| Vấn đề | Số đo (2026-09-17) |
| --- | --- |
| Danh mục DN lệch ngành | 30 target: 4 ngân hàng, 3 dược, 3 bán lẻ/phân phối, 1 bảo hiểm… Ngành phát thải cao (điện, dệt, khí, khai khoáng) chỉ 6 DN và **crawl được 0–6 tài liệu mỗi DN** |
| Tài liệu lệch loại | 670 tài liệu: BCTC 284, ĐHĐCĐ 177, other 85 — **BCPTBV chỉ 41** (9 DN) |
| Hàng đợi gán nhãn lệch chủ đề | 3.682 ứng viên → **945 (26%)** có từ khoá môi trường; lô thử 8 câu: **6 câu là GDP / kế hoạch kinh doanh / thu nhập NLĐ** |
| Không có nguồn đối chứng độc lập | 100% bằng chứng là tài liệu của chính DN; không có xử phạt, giấy phép, kiểm kê nhà nước |
| Bằng chứng sai kỳ | claim 2023 được ghép với báo cáo 2024–2025; ứng viên #1 thường là chính câu claim |

Kết luận: khối lượng không thiếu, **độ sát chủ đề và độ tin cậy nguồn** thiếu. Đợt v2 tối ưu hai thứ đó, không tối ưu số tài liệu.

## 2. Nguyên tắc chọn nguồn (áp cho mọi tài liệu mới)

1. **Sát chủ đề:** đơn vị thu thập là *mục môi trường* và *bảng chỉ số* (GRI 302/303/305/306, mục 6 Phụ lục IV TT 96), không phải cả tài liệu.
2. **Có thẩm quyền trước, tự công bố sau:** thứ tự ưu tiên bằng chứng giữ nguyên `NEXT_COLLECTION_PLAN.md`: cơ quan nhà nước → BCTC kiểm toán → assurance độc lập → số liệu môi trường chính thức → báo cáo DN → báo chí uy tín.
3. **Có mỏ neo pháp lý:** chỉ chọn DN nằm trong phạm vi một nghĩa vụ công bố cụ thể (QĐ 13/2024 kiểm kê KNK; TT 96/2020 mục môi trường), để "thiếu" là một finding có căn cứ, không phải ý kiến.
4. **Truy vết đủ:** URL gốc, ngày truy cập, SHA-256, năm báo cáo **bắt buộc** — tài liệu không xác định năm không được vào hàng đợi.
5. **Quyền sử dụng rõ:** chỉ trang IR/HOSE/HNX/UBCKNN/cổng Chính phủ/cổng Bộ; không mạng xã hội, không dữ liệu trả phí.

## 3. Ba lớp dữ liệu

### Lớp A — Nguồn tuyên bố (claim source)

| Loại | Vì sao | Cách lấy |
| --- | --- | --- |
| BCPTBV độc lập (tiếng Việt) 2022–2024 | Mật độ claim môi trường cao nhất | Trang IR + HOSE; ưu tiên DN từng vào vòng chung khảo hạng mục Báo cáo PTBV của giải VLCA (danh sách công khai — **cần xác minh URL**) |
| Mục "Báo cáo tác động môi trường" trong BCTN (Phụ lục IV mục 6 TT 96) | Bắt buộc với mọi DN niêm yết; cấu trúc cố định → so sánh được | Trích trang theo tiêu đề mục; parser bảng |
| Thuyết minh BCTC kiểm toán: chi phí môi trường, quỹ phục hồi, thuế BVMT, trái phiếu xanh | Số kiểm toán để đối chiếu số tự công bố | Đã có trong corpus cũ, chỉ cần lọc trang |

### Lớp B — Bằng chứng độc lập (mới hoàn toàn)

| Nguồn | Dùng để kiểm chứng | Trạng thái |
| --- | --- | --- |
| **Phụ lục QĐ 13/2024/QĐ-TTg** — cơ sở + mức phát thải tCO₂tđ | Scope 1+2 DN tự công bố vs số Chính phủ; nghĩa vụ kiểm kê | **Đã có OCR** trong `data/legal/raw/QD13-2024-QD-TTg/`; cần parse bảng + khớp tên cơ sở ↔ mã CK |
| Quyết định xử phạt VPHC về môi trường (Bộ TN&MT / Sở TN&MT / Thanh tra) | Mâu thuẫn "tuân thủ pháp luật BVMT"; mục 6.4 TT 96 yêu cầu DN tự khai số lần/số tiền bị phạt | Cổng Bộ + báo chí dẫn số quyết định; Thảo lập registry |
| Công bố thông tin bất thường HOSE/HNX về xử phạt, sự cố môi trường | Đối chứng claim trong cùng kỳ | HOSE/HNX CBTT, đã tiếp cận được |
| Giấy phép môi trường / ĐTM đã phê duyệt | Phạm vi được cấp phép vs tuyên bố | Cổng Bộ (dữ liệu phân tán — chỉ lấy cho DN demo) |
| Assurance statement bên thứ ba trong BCPTBV | Thuộc tính "bảo đảm độc lập" | Trích trang từ chính báo cáo |
| Chứng nhận (PAS 2060, ISO 14064, ISO 50001) — danh bạ tổ chức chứng nhận | Claim "trung hoà carbon", "đầu tiên tại VN" | Chỉ khi có URL công khai; nếu không → INSUFFICIENT |

### Lớp C — Policy (đã có, bổ sung)

- Phụ lục I QĐ 21/2025 tách theo ngành cho 3 ngành demo (Thảo, S2.5).
- Mục 6 Phụ lục IV TT 96/2020 mã hoá thành checklist "trường bắt buộc" → rule `disclosure` (Thảo).

## 4. Danh mục doanh nghiệp mục tiêu v2

Tiêu chí chọn (đủ cả ba): (i) ngành phát thải cao theo hồ sơ Vòng 1; (ii) có cơ sở trong Phụ lục QĐ 13/2024; (iii) có BCPTBV hoặc mục môi trường ≥ 3 năm liên tiếp, PDF có text layer.

| Ngành | Ứng viên (mã CK) | Ghi chú |
| --- | --- | --- |
| Thép | HPG, HSG, NKG | HPG đã có 2 báo cáo trong `real_cases/` |
| Xi măng / VLXD | HT1, BCC, VGC | |
| Điện | POW, PGV, NT2, QTP, HND, REE, GEG | POW/NT2 crawl cũ thất bại — cần harvest JS |
| Dầu khí / hoá chất / phân bón | GAS, PLX, BSR, DPM, DCM, DGC | |
| Dệt may | TCM, MSH, TNG, STK | TNG crawl cũ 0 tài liệu |
| Thực phẩm / đồ uống | VNM, SAB, MSN, DBC, QNS | VNM/SAB giữ lại từ corpus cũ |
| BĐS KCN | KBC, IDC, SZC, BCM | |
| Logistics / hàng không | GMD, HAH, ACV | |
| Nhựa / giấy / bao bì | AAA, DHC, BMP | AAA có BCPTBV nhiều năm |

Mục tiêu: **25–30 DN đạt đủ 3 tiêu chí** (không nhất thiết đủ cả bảng), mỗi DN 3 năm × (BCPTBV hoặc mục môi trường BCTN) ≈ **75–90 tài liệu lõi**, tất cả on-topic. Bước xác minh (ii) chạy bằng script khớp tên cơ sở QĐ 13 ↔ công ty mẹ — khớp mờ, Quỳnh duyệt tay.

## 5. Đơn vị thu thập và hàng đợi gán nhãn mới

```text
Tài liệu → trang thuộc mục môi trường / bảng chỉ số
        → câu ứng viên  (lọc bằng lexicon taxonomy, KHÔNG dùng informativeness)
        → ghép bằng chứng: cùng DN, năm ≤ năm claim, loại nguồn ≠ chính câu claim,
                            ưu tiên lớp B trước lớp A
        → hàng đợi gán nhãn (mục tiêu ≥ 70% là claim môi trường thật)
```

Thay đổi trong `tools/label_session.py` (Nhân): lọc lexicon; bỏ ứng viên trùng câu; sắp bằng chứng theo (thẩm quyền nguồn, |năm chênh|, điểm truy xuất).

## 6. Gate chất lượng cho đợt v2 (đo trước khi gán nhãn)

| Gate | Ngưỡng |
| --- | --- |
| Tỷ lệ ứng viên là claim môi trường thật (Quỳnh soát 50 câu ngẫu nhiên) | ≥ 70% |
| Tài liệu có năm xác định | 100% |
| DN có ≥ 1 nguồn lớp B | 100% DN demo, ≥ 60% toàn danh mục |
| Cặp claim–evidence sai kỳ (evidence sau claim) | 0 trong hàng đợi |
| Trùng SHA-256 xuyên split | 0 |
| Tỷ lệ trang OCR (không text layer) | báo cáo; DN demo phải < 10% |

## 7. Phân công và lịch (song song Sprint 1, không chờ code)

| Tuần | Quỳnh | Thảo | Nhân |
| --- | --- | --- | --- |
| 1 (09-22) | Chốt 25–30 DN theo tiêu chí §4; ghi bảng `data/v2/company_registry.csv` (mã, ngành, URL IR, có BCPTBV năm nào) | Registry xử phạt môi trường: 20 quyết định gần nhất có tên DN niêm yết (số QĐ, cơ quan, ngày, URL, hành vi, số tiền) | Parse bảng Phụ lục QĐ 13 → `data/legal/derived/qd13_facilities.csv`; script khớp tên ↔ mã CK |
| 2 (09-29) | Với 5 DN demo: viết "yêu cầu bằng chứng" theo loại claim (KNK, năng lượng, nước, chất thải, vốn xanh) | Mã hoá mục 6 Phụ lục IV TT 96 thành checklist trường bắt buộc | Crawl lớp A cho 25–30 DN (cấu hình lại crawler, harvest JS cho POW/NT2/TNG); trích mục môi trường + bảng |
| 3 (10-06) | Soát 50 câu ngẫu nhiên → gate ≥ 70%; bắt đầu gán nhãn lô 1 | Gán nhãn độc lập lô 1 | Xây hàng đợi v2, `label_session.py` v2, báo cáo gate §6 |

## 8. Giữ gì từ corpus cũ

- **Giữ nguyên** `data/crawl/vn30/` làm nền retrieval và làm *hard negatives* (câu có số nhưng không phải môi trường — chính là 74% đã đo).
- **Giữ** 642 câu môi trường có số đã lọc được từ hàng đợi cũ; đưa vào hàng đợi v2 sau khi gán năm cho phần `review`.
- **Không** gán nhãn thêm từ hàng đợi cũ chưa lọc.

## 9. Điều không làm

- Không crawl thêm ngân hàng/dược/bán lẻ.
- Không lấy báo chí làm bằng chứng quyết định; chỉ dùng để tìm số quyết định xử phạt rồi truy về văn bản gốc.
- Không đưa chứng nhận bên thứ ba vào gold nếu không có URL công khai của tổ chức chứng nhận.
