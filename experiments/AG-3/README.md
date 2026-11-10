# AG-3 · Dựng hàng bảng từ toạ độ chữ trong PDF (bản v0, 01/11/2026)

*Đăng ký `agentic_ag3_v0` trong `configs/measurement_decisions.yaml` lúc 17:30, trước khi bộ đọc nào thấy các hàng dựng lại.*

## 1. Vấn đề

Lỗi F3: PyMuPDF trả văn bản của một bảng thành các đoạn rời.
- Trang 39 của HPG SR 2025 cho ra "Phạm vi 1 | Phạm vi 2 | Cộng | … | 22.540.603 | 933.876 | 23.474.480".
- Size ladder (10/10) cho thấy **mọi** model tự phán đều báo SUPPORTED sai ở hai bẫy:
  - N02: "phạm vi 1 là 23.369.500", trong khi đó là số của mảng thép;
  - N05: "nông nghiệp 933.876", trong khi đó là số phạm vi 2.
- GS-Bench chưa có ca nào trên bảng.

## 2. Giả thuyết và dự đoán (ghi trước)

Dựng lại hàng bảng từ toạ độ chữ, gắn thêm năm và đơn vị lấy từ hàng tiêu đề cột. Dự đoán:
- N02 và N05 thành C;
- đúng ≥ 5/7 ca trang 39;
- SUPPORTED sai bằng 0;
- trang thô có ≥ 1 SUPPORTED sai.

## 3. Phương pháp

`rows.py` dựng hàng như sau:
- Chỉ lấy chữ của các block ngắn một dòng. PyMuPDF đặt mỗi ô bảng thành một block riêng, còn văn xuôi của cột bên cạnh là block nhiều dòng; giữ cả hai thì văn xuôi dính vào hàng bảng.
- Gom chữ thành hàng theo tâm dọc, với dung sai bằng 0,45 lần chiều cao chữ.
- Tách một hàng thành các đoạn ở khoảng trống ngang lớn. Đoạn chỉ có số thì gắn vào đoạn nhãn đứng trước nó.
- Bỏ nhãn dài quá 8 từ, vì đó là văn xuôi. Số nguyên một chữ số đứng ngay sau nhãn được coi là một phần của nhãn ("Phạm vi 1").
- Hàng tiêu đề (hàng chỉ có số năm) cho năm và đơn vị của các hàng bên dưới.
- Hàng "Cộng / Tổng" được **cộng dọc** với các hàng phía trên cùng cột, dung sai bằng nửa đơn vị của mọi số đem cộng. Số năm không được đem cộng.

Đánh giá (`eval_p39.py`):
- Cùng một bộ đọc IR: Groq `gpt-oss-120b`, `reasoning_effort` low + `json_object`, prompt của AG-1, `ground`.
- Cùng một cách kết luận: `verdict` của AG-1, bản v1.2 có C-guard.
- Hai điều kiện:
  - **thô:** cả trang đọc một lần;
  - **hàng:** mỗi câu-hàng đọc riêng.

**Phương án đã cân nhắc và bỏ:**

| Phương án | Vì sao bỏ |
|---|---|
| PyMuPDF `find_tables` chế độ đường kẻ | Không thấy bảng: bảng không có đường kẻ |
| PyMuPDF `find_tables` chế độ văn bản | Gom cả trang thành một bảng 89 × 17 |
| Docling, Table Transformer | Cần GPU; để lần sau, nếu cách toạ độ không đủ |

## 4. Cấu hình

- Tài liệu: `data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf`, trang 39. Trang 9 và 86 (infographic) dùng để thử.
- Ca: N01–N06 và N08 của `benchmark/size_ladder_2026-10-10/cases_noisy.py`.
- Lời gọi Groq: 18 lần, lưu ở `out/cache.jsonl`.

## 5. Kết quả [ĐÃ THỰC NGHIỆM]

**Dựng hàng trang 39:** đủ 10 hàng dữ liệu. Ví dụ "Năm 2025, Phạm vi 1: 22.540.603 tCO2e" và "Năm 2025, Thép: 23.369.500 tCO2e; 99,55%". **Cộng dọc: 3/3 tổng khớp** trong dung sai làm tròn:
- phạm vi 1 + 2 bằng tổng, lệch 1;
- tổng 5 mảng bằng tổng chung, lệch 1;
- tỷ trọng cộng lại đúng 100 %.

**Kết luận trên 7 ca** (`out/result_p39.json`):

| Điều kiện | Đúng | Dám kết luận | SUPPORTED sai | CONTRADICTED sai |
|---|---|---|---|---|
| Trang thô | 1/7 | 0 | 0 | 0 |
| Hàng dựng lại | 3/7 | 2 (N04 S, N08 S, đều đúng) | 0 | 0 |

**Đối chiếu dự đoán:**
- "N02 và N05 thành C" **sai**: cả hai vẫn là N.
- "≥ 5/7 đúng" **sai**: chỉ 3/7.
- "Trang thô có ≥ 1 SUPPORTED sai" **sai**: đường IR không đoán, nên trên trang thô nó không kết luận ca nào.
- "SUPPORTED sai bằng 0" **đúng** ở cả hai điều kiện.

## 6. Diễn giải và giới hạn

**Vì sao còn N** (đọc trường `why`):
- **Thiếu chiều "mảng kinh doanh" trong IR.**
  - **N02:** so với hàng "Phạm vi 1" thì ra C đúng ("|23.369.500 − 22.540.603| = 828 897"). Nhưng số 23.369.500 có trong bảng ở hàng "Thép", nên C-guard hạ C về N.
  - **N03:** số khớp hàng "Thép" nhưng lệch hàng "Cộng", vì hai hàng này không phân biệt được. Kết quả là vừa khớp vừa lệch, nên N.
- **Hàng "Cộng" không ghi rõ là "phạm vi 1 + 2"**, nên N01 không so được.
- Phép cộng dọc đã cho biết các hàng nào cộng thành tổng, nhưng thông tin đó chưa được đưa vào câu-hàng.

**Giới hạn:**
- Chỉ có một trang bảng và 7 ca dựng.
- Bộ đọc là `gpt-oss-120b` (đám mây), không phải bộ đọc 4B của sản phẩm.

**Phát hiện phụ về chính tài liệu:** tiêu đề trang 39 ghi "KIỂM KÊ PHÁT THẢI KHÍ NHÀ KÍNH NĂM 2024", còn bảng ghi năm 2025. Đây là một mâu thuẫn nội bộ của báo cáo, thuộc loại v3 D4 nhắm tới.

## 7. Thất bại và cách gỡ

- **Văn xuôi cột trái dính vào hàng bảng.** Lần thử 1 ra 18 hàng rác; lần thử 2 tách theo khoảng trống thì mất các hàng "Phạm vi 1" và "Thép". Đã gỡ bằng cách chỉ lấy block ngắn.
- **Số năm bị đem cộng dọc** (tổng 100 % bị cộng thành 46,9 triệu). Đã thêm `is_year`.
- **Chỉ số tuple sai** (word của PyMuPDF có 8 phần tử): lỗi IndexError ở lần chạy đầu.

## 8. Khái niệm

Cộng dọc (cross-foot), hàng tiêu đề, C-guard, chiều "mảng kinh doanh" (segment).

## 9. Hình nên vẽ

Ảnh trang 39 chồng hộp các hàng đã dựng, kèm ba phép cộng dọc. Dữ liệu: `rows.table_rows()` và `cross_foot()`.

## 10. Bước tiếp

1. **IR v1.3:**
   - thêm trường `segment` (mảng kinh doanh / đơn vị thành viên) vào prompt và `irlib`;
   - C-guard chỉ hạ C khi số trùng nằm ở một số liệu **so được** với tuyên bố;
   - đăng ký trước, rồi chạy lại trên 7 ca này và trên GS-Bench.
2. **Gắn nhãn hàng tổng bằng kết quả cộng dọc**, ví dụ "Cộng (Phạm vi 1 + Phạm vi 2)". Cách này tất định, và chỉ áp khi cộng dọc khớp.
3. **Lớp bảng cho GS-Bench:** bảng GHG, năng lượng, nước của các doanh nghiệp phát thải cao (thép, xi măng, điện), sinh ca bằng các họ nhiễu như B-b.
