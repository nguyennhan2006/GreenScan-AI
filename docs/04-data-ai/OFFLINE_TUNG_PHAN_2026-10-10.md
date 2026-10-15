# Ngoại tuyến một phần — dùng mô hình đám mây mà không lộ thông tin quan trọng

**Ngày:** 10/10/2026 · **Trạng thái:** thiết kế + thí nghiệm sơ bộ; **chưa** đưa vào sản phẩm.
**Định hướng của nhóm:** *độ chính xác trước, ngoại tuyến hoàn toàn sau; đi qua ngoại tuyến một phần trước.*
**Đọc cùng:** hệ thống hiện tại [`../03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`](../03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md) · thí nghiệm [`../../benchmark/size_ladder_2026-10-10/`](../../benchmark/size_ladder_2026-10-10/README.md) · huấn luyện cho bước ngoại tuyến hoàn toàn [`../../training/README.md`](../../training/README.md).

---

## 0. Tóm tắt

1. **Giao thức:** tại máy, mọi con số được thay bằng chỗ trống (`<S1>`, `<E1>`…) và tên doanh nghiệp/cơ sở bằng nhãn; mô hình đám mây **chỉ trả lời số nào trong bằng chứng đo cùng đại lượng với số nào trong tuyên bố** (hoặc là tổng, hoặc là % thay đổi, hoặc không ứng số nào); tại máy, giá trị thật được điền lại và so theo độ chính xác công bố. Mô hình không bao giờ thấy giá trị và không bao giờ phán "đúng/sai" trên văn bản đã che.
2. **Đo 10/10 trên 51 ca:** độ chính xác **giữ nguyên trong sai số** so với gửi nguyên văn (gemma-4-31B: 32/32 và 18/19 khi che, so với 32/32 và 17/19 khi không che); **xác nhận sai về 0** ở mọi mô hình (không che: 1–3); lỗi còn lại đổi thành "mâu thuẫn" — loại lỗi luôn bị chuyển người soát.
3. **Rò rỉ:** 0 giá trị số liệu và 0 tên riêng trong nội dung gửi đi (sau khi sửa lỗi tên bị ngắt dòng). **Nhưng danh tính vẫn suy ra được từ ngữ cảnh:** mô hình đoán đúng doanh nghiệp ở 5/20 câu tuyên bố và 3/3 trang — vì "khu liên hợp gang thép", "thép + nông nghiệp + bất động sản + điện máy" chỉ một doanh nghiệp có.
4. **Hệ quả thiết kế:** ngoại tuyến một phần **bảo vệ được số liệu**, **không bảo vệ được danh tính** của doanh nghiệp đặc thù. Gửi **cửa sổ ngắn nhất** (câu, dòng bảng), không gửi cả trang; việc mà danh tính khách hàng là bí mật → chỉ ngoại tuyến hoàn toàn (mô hình học trò tại máy, [`training/`](../../training/README.md)).

---

## 1. Ba nấc

| Nấc | Mô hình đọc cặp khó | Gửi đi | Độ chính xác (51 ca, 10/10) | Trạng thái |
| --- | --- | --- | --- | --- |
| **L0a** ngoại tuyến hôm nay | không — chỉ luật | không gì | luật: 20/32 · 7/19 | đang chạy |
| **L0b** đám mây hôm nay | GLM-5.2 nguyên văn, có chốt chặn | nguyên văn câu + đoạn (kể cả số, tên, bảng nguyên khối) | mô hình đơn lẻ: 29–32/32 · 15–18/19 | đang chạy |
| **L1** ngoại tuyến một phần | mô hình đám mây **chỉ đối sánh** trên văn bản đã che; mã tính tại máy | cửa sổ ngắn đã che: không số, không tên | gemma-31B 32/32 · 18/19, 0 xác nhận sai | **thiết kế này** |
| **L2** ngoại tuyến hoàn toàn | mô hình học trò < 1B tại máy (chưng cất từ L1) | không gì | chưa có | [`training/`](../../training/README.md) |

---

## 2. "Thông tin quan trọng" là gì

| Loại | Ví dụ | Nhạy cảm vì | L1 che được? |
| --- | --- | --- | --- |
| Số liệu chưa công bố | phát thải dự thảo, sản lượng, chi phí | lộ trước khi công bố; có thể ảnh hưởng giá cổ phiếu | ✅ hoàn toàn (đã đo: 0 giá trị lọt) |
| Danh tính doanh nghiệp, cơ sở, khách hàng kiểm toán | tên tập đoàn, nhà máy, mã chứng khoán | quan hệ khách hàng; Luật Kiểm toán độc lập Đ.43 | ⚠️ tên thì che được, **ngữ cảnh thì không** (đã đo: 25% câu, 100% trang) |
| Nội dung giấy làm việc, ý kiến kiểm toán | đánh giá trọng yếu, kết luận | bí mật nghề nghiệp | ❌ — không gửi |
| Dữ liệu cá nhân | tên lãnh đạo, người lao động | Luật 91/2025: dữ liệu đã khử định danh không còn là dữ liệu cá nhân (Đ.2.1); cấm định danh lại (Đ.14.6b) | ✅ qua danh mục tên, nhưng cần NER dự phòng |

Phân loại tài liệu (giữ nguyên quy tắc D-2026-10-06-06): **A công khai · B nội bộ chưa công bố · C giấy làm việc kiểm toán**.

---

## 3. Sáu nguyên lý — mỗi cái có căn cứ

| # | Nguyên lý | Căn cứ | Hệ quả trong thiết kế |
| --- | --- | --- | --- |
| P1 | **Tối thiểu hoá dữ liệu** — chỉ gửi đúng thứ cần cho câu hỏi | GDPR Đ.5(1)(c); Luật 91/2025 Đ.2(1) (dữ liệu đã khử định danh không còn là dữ liệu cá nhân) [VERIFIED] | gửi cửa sổ câu/dòng, không gửi trang; không gửi tên tệp, trang, metadata |
| P2 | **Tách hiểu nghĩa khỏi tính toán** | PAL (+15 điểm GSM8K so với PaLM-540B), Program-of-Thoughts (+12% trung bình, gồm FinQA) [VERIFIED]; GSM-Symbolic: chỉ đổi con số đã làm mọi mô hình giảm điểm, một mệnh đề thừa làm GPT-4o tụt 94,9 → 63,1 [VERIFIED] | mô hình đối sánh, mã tính; giữ giá trị khỏi mô hình còn **tăng độ vững**, không chỉ bảo mật |
| P3 | **Không bao giờ hỏi "đúng/sai" trên văn bản đã che** | NumPert: thay số bằng "#", mô hình mặc định "đúng" — GPT-4o 80,00 → 19,25, Llama-3.3-70B 87,32 → 10,80 [VERIFIED] | câu hỏi duy nhất là ánh xạ, **có lựa chọn "không ứng số nào"**; kết luận do mã |
| P4 | **Che tên bằng danh mục + regex trước, NER chỉ dự phòng** | Presidio không có tiếng Việt sẵn; VnCoreNLP GPL-3.0; Stanza vi F1 82,44 (Apache-2.0); PhoBERT MIT nhưng bộ tách từ đi kèm GPL [VERIFIED]; mọi bộ NER huấn luyện trên tin tức | danh mục từ tên doanh nghiệp người dùng khai + `entity_names` của phiên + công ty con/nhà máy/mã CK |
| P5 | **Đo rò rỉ bằng tấn công thật, không tin vào việc "đã che"** | Staab và cs. (ICLR 2024): GPT-4 suy ra thuộc tính cá nhân 85% top-1, vẫn 44–64% sau khi ẩn danh [VERIFIED]; Wu và cs. 2025: thay tên bằng `ORG_1` trong biên bản họp kết quả kinh doanh, mô hình vẫn đoán đúng công ty **19–82%** tuỳ cách che [VERIFIED] | bài kiểm nhận diện lại là cổng bắt buộc (§5.3) |
| P6 | **Ghi sổ mọi lần gửi đi** | `DATA_FLOW.md` của chính dự án yêu cầu; hiện chưa có | `egress.jsonl` mỗi phiên (§6) |

Kỹ thuật **loại bỏ**: DP-Prompt, SanText, CusText (diễn đạt lại / thay từ ngẫu nhiên theo riêng tư vi phân) — phá huỷ số liệu và từ chỉ chỉ số, phạm vi, đơn vị [VERIFIED]. HaS, ProSan, PrivacyRestore cùng họ "che tại máy → mô hình → khôi phục" nhưng hoặc thước đo riêng tư yếu (HaS), hoặc khôi phục trong mô hình phục vụ — không dùng được với API của FPT (PrivacyRestore).

---

## 4. Giao thức L1

```text
TẠI MÁY                                   ĐÁM MÂY (FPT, vùng VN)              TẠI MÁY
câu tuyên bố + đoạn bằng chứng (đã truy xuất tại máy)
  │ 1. thay tên: danh mục + regex (+ NER dự phòng)
  │ 2. thay số: <S1>, <E1>… (giữ đơn vị, năm, nhãn phạm vi, số hiệu văn bản)
  │ 3. cắt cửa sổ: câu chứa số + dòng bảng chứa số, ≤ N ký tự
  │ 4. kiểm trước khi gửi: không còn giá trị số liệu, không còn tên → ghi sổ
  └──────────────► "S1 ứng với E3" / "S1 = tổng E1+E2" / "S1 = % thay đổi E1→E2" / "không ứng"
                                                                        │ 5. điền giá trị thật
                                                                        │ 6. so theo độ chính xác công bố
                                                                        │    (dung sai % theo số chữ số thập phân;
                                                                        │     số tuyệt đối: ½ chữ số cuối, trần 1%)
                                                                        │ 7. ánh xạ sai/không hợp lệ → "chưa đủ";
                                                                        │    mâu thuẫn → luôn chuyển người soát
```

**Được gửi:** câu và cửa sổ đã che; đơn vị; năm; nhãn phạm vi phát thải; số hiệu văn bản/tiêu chuẩn; ngày. **Không bao giờ gửi:** giá trị số liệu; tên doanh nghiệp, cơ sở, người; tên tệp, số trang, metadata phiên; nội dung giấy làm việc.

Tuyên bố không có số → hỏi nhãn định tính trên văn bản đã che tên (không có số nên P3 không áp dụng), kết quả vẫn dưới chốt chặn hiện có.

---

## 5. Thực nghiệm 10/10

Mã: `benchmark/size_ladder_2026-10-10/run_masked.py`, `reid_test.py`; cùng 51 ca có đáp án dựng sẵn với thí nghiệm thang mô hình.

### 5.1 Độ chính xác

| Mô hình | Không che: sạch · trang thật | **Che (L1): sạch · trang thật** | Xác nhận sai (không che → che) | Mâu thuẫn sai (không che → che) |
| --- | --- | --- | --- | --- |
| gemma-4-26B-A4B (~3,8B kích hoạt) | 29 · 18 | 31 · 16 | 2 → **0** | 1 → 1 |
| gemma-4-31B | 32 · 17 | **32 · 18** | 2 → **0** | 0 → 1 |
| GLM-5.2 (753B) | 32 · 17 | 32 · 16 | 2 → **0** | 0 → 3 |
| *luật GreenScan (tham chiếu)* | 20 · 7 | — | 1 | 1 |

- Khác biệt che/không che nằm trong sai số (n = 51); **không phát hiện được tổn thất độ chính xác**.
- **Mọi xác nhận sai biến mất**: lỗi "bảng dàn phẳng" trước đây đến từ việc mô hình thấy con số giống hệt và kết luận "khớp hoàn toàn"; khi số bị che, lối tắt đó mất.
- Lỗi còn lại vẫn ở **cột phần trăm của bảng dàn phẳng** (chọn nhầm cột) → giữ cấu trúc bảng (D5) vẫn là việc cần làm, độc lập với L1.
- GLM-5.2 cho kết quả khác nhau giữa hai lượt chạy dù nhiệt độ 0 (17/19 rồi 16/19 trên cùng bộ) → thêm lý do để mã kiểm mọi phép tính.

### 5.2 Rò rỉ trong nội dung gửi đi

- **Giá trị số liệu còn lại:** 0 / 51 ca (kiểm tự động: mọi số còn trong văn bản đã che được đối chiếu với giá trị đã thay).
- **Tên riêng còn lại:** 0 — sau khi sửa một lỗi phát hiện trong chính thí nghiệm: tên bị **ngắt dòng** trong chữ PDF ("Hòa⏎Phát") lọt qua regex; nay cho phép mọi khoảng trắng giữa các chữ.
- Chữ số còn lại là nhãn: "phạm vi 1 và 2", số trang, số mục, ISO 14064, ngày tháng, "G7", "CO2". Khoảng số "5.6–6.2%", "750–900 độ C" ban đầu lọt (bị coi như số hiệu) → đã sửa để che cả hai đầu.

### 5.3 Nhận diện lại doanh nghiệp (tấn công thật)

Hỏi gemma-4-31B "đây là doanh nghiệp nào" trên đúng nội dung L1 sẽ gửi:

| Nội dung gửi | Đoán đúng doanh nghiệp |
| --- | --- |
| 20 câu tuyên bố riêng lẻ (đã che) | **5/20** (độ tự tin 70–90) |
| 3 trang báo cáo (đã che) | **3/3** (độ tự tin 100) |

Không còn tên nào trong nội dung — mô hình suy ra từ **tổ hợp ngành** và **thuật ngữ đặc thù**. Kết quả khớp Wu và cs. 2025. → **Cửa sổ ngắn giảm rủi ro nhưng không triệt tiêu**; với doanh nghiệp đầu ngành có hoạt động đặc thù, coi như danh tính có thể bị suy ra.

---

## 6. Đưa vào sản phẩm — việc kỹ thuật (chưa làm)

| # | Việc | Ở đâu | Kiểm bằng |
| --- | --- | --- | --- |
| 1 | Module che dữ liệu: danh mục tên (tên khai khi tải + `entity_names` + công ty con/nhà máy người dùng nhập), che số, cửa sổ tối thiểu, kiểm trước khi gửi | `src/quantum_gw/privacy/` (bản thử: `training/masking.py`) | kiểm thử thuộc tính trên toàn kho công khai: **không có giá trị số liệu hay tên nào trong mọi nội dung gửi** |
| 2 | Prompt `align-v1` + quyết định tại máy, nối vào nhánh số học của bộ kiểm chứng | `verification/llm_judge.py`, `agents/verifier.py` | 47 bẫy + 17 ca checklist + 4 ca thật giữ nguyên; 51 ca dựng sẵn |
| 3 | Sổ gửi đi mỗi phiên: thời điểm, mô hình, băm nội dung, số ký tự, số chỗ trống, chữ số còn lại; bản đầy đủ lưu **tại máy** để kiểm toán | `.quantum/runs/<id>/egress.jsonl` | giấy làm việc và `/v1/runtime` đọc từ sổ này — sửa không khớp #2 ở [bản đồ hệ thống §7](../03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md#7-chỗ-cấu-hình-tài-liệu-và-mã-không-khớp-nhau--việc-cần-sửa) |
| 4 | Chế độ mới `QUANTUM_PROFILE=cloud_masked`; chế độ `gpu` **bỏ dự phòng sang FPT** | `settings.py` | `test_product_api.py` |
| 5 | Chính sách theo loại tài liệu ở §7, chọn khi tải lên | giao diện bước 1 | — |
| 6 | Bài kiểm nhận diện lại chạy lại mỗi khi đổi quy tắc che | `benchmark/.../reid_test.py` | cổng §8 |

---

## 7. Chính sách theo loại tài liệu

| Loại | Danh tính có phải bí mật? | Chế độ được phép |
| --- | --- | --- |
| A — công khai | không | L0a, L0b, L1, L2 |
| B — nội bộ chưa công bố | **không** (ví dụ doanh nghiệp tự soát trước khi công bố) | L0a, **L1 với cửa sổ câu/dòng**, L2 |
| B — nội bộ chưa công bố | **có** (ví dụ khách hàng kiểm toán chưa công khai quan hệ) | L0a, L2 |
| C — giấy làm việc kiểm toán | — | L0a, L2 (không gửi đi dưới mọi hình thức) |

---

## 8. Ngưỡng để bật L1 — đăng ký trước, đo trên gold

| Điều kiện | Ngưỡng |
| --- | --- |
| Độ chính xác đối sánh trên gold, che so với nguyên văn | không thấp hơn quá **3 điểm** (cận dưới khoảng tin cậy) |
| Tỷ lệ xác nhận sai | **≤** chế độ nguyên văn |
| Giá trị số liệu / tên riêng trong nội dung gửi | **0** trên toàn kho công khai |
| Nhận diện lại trên cửa sổ câu (tài liệu loại B, danh tính không bí mật) | báo cáo con số; người dùng quyết định chấp nhận |

Không đạt → giữ L0a (luật) cho tài liệu B/C cho tới khi L2 sẵn sàng.

---

## 9. Giới hạn

- 51 ca do nhóm dựng (hỗ trợ bởi AI), một người đặt đáp án; cần Quỳnh/Thảo dựng thêm và gán lại.
- Chưa thử trên cặp truy xuất thật của nhiều doanh nghiệp; chưa thử với tuyên bố nhiều số và bảng giữ cấu trúc.
- Nhận diện lại mới thử một doanh nghiệp rất đặc thù (Hòa Phát) và một mô hình; doanh nghiệp ít đặc thù có thể khó đoán hơn — cần đo trên nhiều doanh nghiệp.
- Danh mục tên phụ thuộc người dùng khai đủ công ty con, nhà máy; NER tiếng Việt chỉ là dự phòng.
