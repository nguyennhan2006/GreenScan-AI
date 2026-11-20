# GS-Claims v1: hướng dẫn gán nhãn câu (guide_version `gs-claims-v1.0`)

**Mục đích.** Đo bước trích tuyên bố của GreenScan: câu nào là tuyên bố môi trường cần kiểm, và câu đó nêu đủ những thuộc tính nào.

Mỗi dòng của `items.jsonl` là một câu lấy từ báo cáo thường niên hoặc báo cáo phát triển bền vững của doanh nghiệp Việt Nam. Trường `context` (có thể rỗng) là câu liền trước và liền sau, chỉ để hiểu nghĩa. **Chỉ gán nhãn cho câu ở trường `text`.**

**Quy tắc làm việc:**
1. Chỉ đọc tệp này và `items.jsonl`.
2. **Không** mở thư mục `_key/`, `src/`, `.quantum/`, các tệp nhãn khác, hay bất kỳ đầu ra nào của hệ thống.
3. Gán độc lập, không đoán xem hệ thống đã làm gì.
4. Phân vân thì theo đúng quy tắc ưu tiên ghi dưới đây, và ghi lý do ngắn vào `note`.

---

## 1. `is_claim`: "yes" | "no"

**"yes"** khi câu khẳng định một điều về **môi trường hoặc khí hậu** của chính doanh nghiệp (hoặc sản phẩm, dự án, nhà máy, khoản vốn của doanh nghiệp), và người soát về nguyên tắc có thể đối chiếu với bằng chứng. Gồm năm dạng:
- **Số liệu môi trường:** "Năm 2025, lượng nước tiêu thụ là 1,2 triệu m3."
- **Kết quả, thành tích:** "Đã giảm 12% điện năng tiêu thụ.", "100% nhà máy đạt ISO 14001."
- **Cam kết, mục tiêu:** "Cam kết phát thải ròng bằng 0 vào năm 2050."
- **Thực hành, chính sách, hệ thống môi trường đang áp dụng:** "Công ty áp dụng hệ thống quản lý môi trường ISO 14001 tại các nhà máy."
- **Tự mô tả mang tính quảng bá về môi trường:** "Chúng tôi là doanh nghiệp xanh hàng đầu."

**"no"** khi câu là:
- tiêu đề, đề mục, mục lục, tên bảng, tiêu đề cột, đầu trang, chân trang, số trang, mã GRI đứng riêng;
- dòng bị dính chữ do dàn trang, không đọc ra được một khẳng định (ví dụ "Mùa thu hoạch cà gai leo 168 BÁO CÁO PHÁT TRIỂN BỀN VỮNG 169 COTECCONS");
- bối cảnh chung về thế giới, quốc gia, ngành, hay định nghĩa, luật lệ, không nói về doanh nghiệp;
- nội dung chỉ thuộc mảng **xã hội hoặc quản trị**, không có yếu tố môi trường: người lao động, cộng đồng, cổ đông, chất lượng sản phẩm, doanh thu, lợi nhuận, lịch sử công ty;
- lời cảm ơn, lời chào, tầm nhìn chung chung không có nội dung môi trường.

**Quy tắc ưu tiên:**
- Câu nói cả môi trường lẫn xã hội → "yes".
- Câu bị lỗi chữ một phần nhưng vẫn đọc ra khẳng định môi trường → "yes", ghi `note: "lỗi chữ"`.
- "Phát triển bền vững" chỉ xuất hiện như tên báo cáo hoặc tên chương → không làm câu thành tuyên bố.

## 2. `claim_kind` (chỉ khi `is_claim` = "yes"; còn lại ghi "na")

| Giá trị | Khi nào |
|---|---|
| `metric_disclosure` | Nêu giá trị của một chỉ số môi trường (có số), không có từ đánh giá hay so sánh. "Tổng phát thải năm 2025 là 23,47 triệu tCO2e." |
| `performance` | Khẳng định một kết quả, thay đổi, so sánh, thành tích: giảm, tăng, đạt, hoàn thành, dẫn đầu, "100%"… Có số hay không có số đều được |
| `commitment` | Mục tiêu, kế hoạch, cam kết cho tương lai: cam kết, mục tiêu, sẽ, phấn đấu, hướng tới, "đến năm 20xx" |
| `practice` | Mô tả chính sách, quy trình, hệ thống, chứng nhận, sáng kiến đang thực hiện, **không** kèm khẳng định kết quả. "Đang triển khai lắp điện mặt trời áp mái." |
| `promotional` | Tự mô tả tích cực, chung chung về môi trường, không có gì cụ thể để đo. "Luôn thân thiện với môi trường." |

**Ưu tiên khi câu thuộc nhiều dạng:** `commitment` > `performance` > `metric_disclosure` > `practice` > `promotional`. Ví dụ: "Mục tiêu giảm 30% phát thải vào 2030" là `commitment`; "Giảm 12% so với 2020, khẳng định vị thế dẫn đầu" là `performance`.

## 3. Các thuộc tính

Gán cho **mọi** câu, kể cả câu "no". Với câu "no", ghi "no" hoặc "na" theo đúng định nghĩa.

| Trường | Giá trị | Định nghĩa |
|---|---|---|
| `has_figure` | "yes" / "no" | Có ít nhất một **con số đo lường** về đối tượng môi trường: lượng, %, tỷ lệ, số cây, diện tích, công suất. **Không tính:** năm, ngày, số hiệu văn bản, mã chuẩn (ISO 14001, GRI 305), số trang, số chương, cấp hạng ("Cảng Xanh 3"), và con số chỉ đếm phạm vi áp dụng ("tại 4 nhà máy") khi câu không có số đo nào khác |
| `has_period` | "yes" / "implicit" / "no" | **"yes":** nêu rõ thời gian áp dụng ("năm 2025", "trong năm 2024", "giai đoạn 2020–2025"; với cam kết: năm mục tiêu như "đến năm 2050"). **"implicit":** chỉ có từ thời gian tương đối ("hiện nay", "hiện tại", "năm nay", "vừa qua", "gần đây", "đến nay"). **"no":** không có |
| `has_baseline` | "yes" / "no" / "na" | **"na":** câu không nêu thay đổi, so sánh hay mục tiêu thay đổi (giá trị tĩnh, thực hành, quảng bá). **"yes":** có mốc so sánh ("so với năm 2020", "so với năm trước", "so với cùng kỳ", "so với phương pháp truyền thống"). **"no":** có thay đổi hoặc mục tiêu thay đổi nhưng không nói so với gì ("giảm 12% phát thải") |
| `has_ghg_scope` | "yes" / "no" / "na" | **"na":** câu không nói về phát thải khí nhà kính hoặc carbon. **"yes":** nêu phạm vi 1, 2 hoặc 3 (Scope 1/2/3). **"no":** nói về khí nhà kính nhưng không nêu phạm vi |
| `has_boundary` | "yes" / "no" | Nêu **rõ** ranh giới áp dụng: "toàn Tập đoàn", "tất cả các nhà máy", "công ty mẹ", "công ty con X", tên một nhà máy, khu liên hợp, dự án, tòa nhà, cảng cụ thể. Chủ ngữ chung chung ("Công ty", "Tập đoàn", "chúng tôi") **không** tính |
| `cites_independent_source` | "yes" / "no" | Chính câu đó nói có **bên thứ ba** kiểm toán, xác nhận, chứng nhận, đánh giá: "được kiểm toán độc lập", "đạt chứng nhận ISO 14001", "được tổ chức X xác nhận", "đạt chứng nhận LEED". "Lập theo tiêu chuẩn GRI" (chuẩn báo cáo) **không** tính |
| `promotional_language` | "yes" / "no" | Có từ quảng bá hoặc mơ hồ về môi trường dùng để tự khen: xanh, bền vững, sạch, thân thiện với môi trường, hàng đầu, tiên phong, vì môi trường, có trách nhiệm, tương lai xanh… **Không tính:** tên riêng ("Cảng Xanh", "Báo cáo phát triển bền vững") và thuật ngữ kỹ thuật ("năng lượng tái tạo") |
| `note` | chuỗi, ≤ 20 từ, có thể rỗng | Lý do khi phân vân, hoặc "lỗi chữ" |

## 4. Ví dụ đã gán sẵn

| Câu | is_claim | kind | figure | period | baseline | ghg_scope | boundary | indep. | promo |
|---|---|---|---|---|---|---|---|---|---|
| Năm 2025, tổng phát thải khí nhà kính phạm vi 1 và 2 của toàn Tập đoàn là 23,47 triệu tCO2e. | yes | metric_disclosure | yes | yes | na | yes | yes | no | no |
| Lượng nước tiêu thụ trên một tấn sản phẩm năm 2024 giảm 12% so với năm 2020. | yes | performance | yes | yes | yes | na | no | no | no |
| Điện năng tiêu thụ giảm 8%, góp phần xây dựng tương lai xanh. | yes | performance | yes | no | no | na | no | no | yes |
| Chúng tôi cam kết đạt phát thải ròng bằng 0 vào năm 2050. | yes | commitment | no | yes | na | no | no | no | no |
| Hiện nay, 100% nhà máy của Tập đoàn đã đạt chứng nhận ISO 14001. | yes | performance | yes | implicit | na | na | yes | yes | no |
| Công ty triển khai lắp đặt hệ thống điện mặt trời áp mái tại Nhà máy Bình Dương. | yes | practice | no | no | na | na | yes | no | no |
| Chúng tôi là doanh nghiệp xanh hàng đầu, luôn thân thiện với môi trường. | yes | promotional | no | no | na | na | no | no | yes |
| Biến đổi khí hậu đang là thách thức lớn đối với toàn cầu. | no | na | no | no | na | na | no | no | no |
| Doanh thu thuần năm 2024 đạt 140.000 tỷ đồng, tăng 18%. | no | na | no | yes | no | na | no | no | no |
| Bảng 5.2 – Phát thải khí nhà kính theo phạm vi, giai đoạn 2023–2025 | no | na | no | yes | na | yes | no | no | no |

Hai dòng cuối là câu "no": các thuộc tính vẫn được gán theo đúng định nghĩa (doanh thu không phải số liệu môi trường, nên `has_figure` = "no"). Hai lựa chọn "no" và "na" phải dùng đúng như bảng ở mục 3.

## 5. Định dạng đầu ra

Một tệp JSONL, **đủ đúng một dòng cho mỗi `item_id`** trong `items.jsonl`, không thừa không thiếu. Mỗi dòng:

```json
{"item_id": "C-…", "labeler": "<tên được giao>", "guide_version": "gs-claims-v1.0", "is_claim": "yes", "claim_kind": "performance", "has_figure": "yes", "has_period": "implicit", "has_baseline": "na", "has_ghg_scope": "na", "has_boundary": "yes", "cites_independent_source": "no", "promotional_language": "no", "note": ""}
```

Chỉ dùng đúng các giá trị liệt kê ở trên, viết thường, không dấu cách thừa.

---

## Phụ lục: ghi chú sau lượt phân xử đầu tiên (15/11/2026, áp dụng cho bản v1.1)

Lượt đầu có hai người gán Sonnet làm độc lập (sonnet-A, sonnet-B):
- câu kiểm soát: cả hai đúng 29/29 trường;
- kappa "is_claim": 0,92; mọi trường ≥ 0,74;
- 29 câu lệch, 36 trường, do agent Opus phân xử theo hướng dẫn rồi người điều phối soát lại.

Các điểm hướng dẫn còn mơ hồ cần làm rõ trong bản v1.1:
1. `promotional_language`: "bền vững", "phát triển bền vững", "hàng đầu" dùng như tên lĩnh vực, tên chính sách hay đề mục **không** tính; "xanh" mang nghĩa kỹ thuật ("phủ xanh", "mua sắm xanh") **không** tính.
2. Khẩu hiệu tương lai có "sẽ" hoặc "hướng tới" nhưng không có mục tiêu cụ thể: theo thứ tự ưu tiên thì là `commitment`. Bản v1.1 cân nhắc cho xếp `promotional`.
3. Câu chỉ nói "ESG" mà không có nội dung môi trường rõ ràng:
   - chính sách ESG (bao trùm cả mảng môi trường) → "yes", `practice`;
   - nhân sự hoặc tổ chức của ban ESG → "no".
4. Mục liệt kê, đề mục không có chủ ngữ ("Thu gom và xử lý rác thải/ bùn thải 4.") → "no".
5. `has_baseline`: "từ X lên Y" có tính là mốc so sánh. Mục tiêu giảm không có số thì vẫn là mục tiêu thay đổi, nên `has_baseline` = "no".
