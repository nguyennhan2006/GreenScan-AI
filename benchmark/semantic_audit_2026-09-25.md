# Audit ngữ nghĩa HPG — 2026-09-25

So sánh run `d160226875ec4144` (baseline 22/09) với run `185480a0c8b747c4`.

> Câu hỏi không phải *"vì sao số CONTRADICTED giảm"* mà *"lẽ ra nó có được tồn tại không"*.
> Mỗi mục dưới đây trả lời bằng chiều nào khiến hai con số không so được, tính bằng quy tắc hiện tại trên đúng đoạn văn đã tạo ra kết luận cũ.

## Tổng hợp: 8 mâu thuẫn trong bản 22/09

| Chiều khiến hai con số không so được | Số cặp |
| --- | ---: |
| khác công nghệ sản xuất | 2 |
| khác cơ sở đo (tỷ trọng / mức thay đổi / tuyệt đối / cường độ) | 2 |
| chênh lệch hàng chục lần trở lên — thường là khác ranh giới, ngành hoặc đơn vị; cần người xem | 2 |
| khác loại chỉ số con | 2 |
| không phải số học | 1 |
| một bên là mục tiêu, một bên là số thực hiện | 1 |

Không có mâu thuẫn nào trong bản cũ sống sót qua quy tắc hiện tại: mỗi cái đều dừng ở một chiều cụ thể, hoặc không phải kết luận số học ngay từ đầu. Comparator cũ chỉ kiểm **đơn vị** — đó là toàn bộ nguyên nhân.

## Từng ca

### 1. trang 21 — trung bình (Scrap-EAF): 0,70 tấn CO2 / tấn thép thô Điểm nổi bật về phát triển bền vững năm 2025 Cường độ phát thải CO2 Cường độ phát thải CO2

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 0.7, tài liệu 1.43.
- **Hôm nay:** `PARTIALLY_SUPPORTED`
- **Lý do mới:** Có bằng chứng cùng chủ đề nhưng chưa xác minh được đầy đủ. Tuyên bố thiếu: phạm vi / ranh giới.
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 21):
  > trung bình (BF-BOF): 2,32 tấn CO2 / tấn thép thô trung bình (DRI-EAF): 1,43 tấn CO2 / tấn thép thô Tại Hòa Phát, phần lớn thép thô sản xuất từ công nghệ lò cao (KLH Gang thép Hòa Phát
- **Kiểm lại theo quy tắc hiện tại:**
  - `0.7 tco2e` vs `2.32 tco2e` → **KHÔNG so được** — khác công nghệ sản xuất
    - tuyên bố: {'basis': 'intensity', 'is_target': False, 'boundary': 'unknown', 'technology': 'scrap_eaf', 'variant': None, 'scopes': None}
    - bằng chứng: {'basis': 'intensity', 'is_target': False, 'boundary': 'unknown', 'technology': 'bf_bof', 'variant': None, 'scopes': None}
  - `0.7 tco2e` vs `1.43 tco2e` → **KHÔNG so được** — khác công nghệ sản xuất
    - tuyên bố: {'basis': 'intensity', 'is_target': False, 'boundary': 'unknown', 'technology': 'scrap_eaf', 'variant': None, 'scopes': None}
    - bằng chứng: {'basis': 'intensity', 'is_target': False, 'boundary': 'unknown', 'technology': 'dri_eaf', 'variant': None, 'scopes': None}

### 2. trang 33 — quốc gia về giảm phát thải khí nhà kính Duy trì cơ chế kê khai và nộp thuế minh bạch và tuân thủ pháp luật.

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Bằng chứng phủ định tuyên bố (nguồn có thẩm quyền): “thiếu”.
- **Hôm nay:** câu này **không còn là tuyên bố** — không còn xuất hiện ở tầng `extract` — cần kiểm tay
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 78):
  > Tập đoàn duy trì cơ chế giám sát và kiểm soát nội bộ chặt chẽ đối với các quy trình thuế, đảm bảo tính liêm chính, tuân thủ chuẩn mực cao nhất và ngăn chặn mọi hình thức trốn thuế hoặc hành vi thiếu minh bạch, từ đó củng cố niềm tin với cơ quan quản lý và
- **Kiểm lại theo quy tắc hiện tại:**
  - Không có cặp số nào để so (tuyên bố 0 số, bằng chứng 0 số) → kết luận cũ không đến từ số học.

### 3. trang 35 — trung vào các lĩnh vực có cường độ phát thải cao nhất — đặc biệt là ngành gang thép, chiếm hơn 99% tổng lượng phát thải KNK của Tập đoàn.

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 99.0, tài liệu 24.0.
- **Hôm nay:** câu này **không còn là tuyên bố** — không còn xuất hiện ở tầng `extract` — cần kiểm tay
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 40):
  > thải. Từ tháng 9 năm 2025, Hòa Phát Dung Quất 2 đi vào vận hành, Tổng sản lượng thép thô tăng 24%, tương ứng với mức tăng phát thải của toàn tập đoàn. Lĩnh vực nông nghiệp và chăn nuôi của Tập đoàn Hòa Phát ghi nhận mức phát
- **Kiểm lại theo quy tắc hiện tại:**
  - `99 %` vs `24 %` → **KHÔNG so được** — khác cơ sở đo (tỷ trọng / mức thay đổi / tuyệt đối / cường độ)
    - tuyên bố: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'group', 'technology': None, 'variant': None, 'scopes': None}
    - bằng chứng: {'basis': 'percentage_change', 'is_target': False, 'boundary': 'facility', 'technology': None, 'variant': None, 'scopes': None}

### 4. trang 40 — Hành động giảm thiểu và thích ứng với biến đổi khí hậu Trong năm 2025, tổng lượng phát thải khí nhà kính của Tập đoàn Hòa Phát là 23.474.480 tCO2e, ba

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 23474480.0, tài liệu 90846.0.
- **Hôm nay:** `PARTIALLY_SUPPORTED`
- **Lý do mới:** Có bằng chứng cùng chủ đề nhưng chưa xác minh được đầy đủ. Tuyên bố thiếu: số liệu, năm gốc để so sánh.
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 40):
  > HÀNH ĐỘNG GIẢM THIỂU VÀ THÍCH ỨNG VỚI BIẾN ĐỔI KHÍ HẬU 5.1 thải khí nhà kính ở mức tương đối thấp so với tổng lượng phát thải toàn tập đoàn (phát thải 90,846 tCO2e, chiếm 0,39%). Các nguồn phát thải chính trong lĩnh vực
- **Kiểm lại theo quy tắc hiện tại:**
  - `2.34745e+07 tco2e` vs `90846 tco2e` → **chưa chắc** — chênh lệch hàng chục lần trở lên — thường là khác ranh giới, ngành hoặc đơn vị; cần người xem

### 5. trang 40 — Lĩnh vực sản xuất gang thép và sản phẩm thép của Tập đoàn Hòa Phát tiếp tục là nguồn phát thải khí nhà kính lớn nhất, chiếm tỷ trọng vượt trội trên 99

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 99.0, tài liệu 0.39.
- **Hôm nay:** `PARTIALLY_SUPPORTED`
- **Lý do mới:** Chỉ tài liệu của chính nguồn tuyên bố khớp với tuyên bố; chưa có nguồn đối chiếu độc lập (báo cáo khác, kiểm toán, cơ quan quản lý).
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 40):
  > HÀNH ĐỘNG GIẢM THIỂU VÀ THÍCH ỨNG VỚI BIẾN ĐỔI KHÍ HẬU 5.1 thải khí nhà kính ở mức tương đối thấp so với tổng lượng phát thải toàn tập đoàn (phát thải 90,846 tCO2e, chiếm 0,39%). Các nguồn phát thải chính trong lĩnh vực
- **Kiểm lại theo quy tắc hiện tại:**
  - `99 %` vs `0.39 %` → **chưa chắc** — chênh lệch hàng chục lần trở lên — thường là khác ranh giới, ngành hoặc đơn vị; cần người xem

### 6. trang 40 — Từ tháng 9 năm 2025, Hòa Phát Dung Quất 2 đi vào vận hành, Tổng sản lượng thép thô tăng 24%, tương ứng với mức tăng phát thải của toàn tập đoàn.

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 24.0, tài liệu 99.0.
- **Hôm nay:** `PARTIALLY_SUPPORTED`
- **Lý do mới:** Có bằng chứng cùng chủ đề nhưng chưa xác minh được đầy đủ. Tuyên bố thiếu: năm gốc để so sánh.
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 35):
  > trung vào các lĩnh vực có cường độ phát thải cao nhất — đặc biệt là ngành gang thép, chiếm hơn 99% tổng lượng phát thải KNK của Tập đoàn. Trong đó, hai Khu liên hợp Gang thép Hòa Phát Hải Dương và Hòa Phát Dung Quất — chiếm khoảng
- **Kiểm lại theo quy tắc hiện tại:**
  - `24 %` vs `99 %` → **KHÔNG so được** — khác cơ sở đo (tỷ trọng / mức thay đổi / tuyệt đối / cường độ)
    - tuyên bố: {'basis': 'percentage_change', 'is_target': False, 'boundary': 'facility', 'technology': None, 'variant': None, 'scopes': None}
    - bằng chứng: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'group', 'technology': None, 'variant': None, 'scopes': None}

### 7. trang 104 — GJ 193.403.521 302-1 Tiêu thụ năng lượng trong tổ chức Năng lượng tiêu thụ được cung cấp từ lưới điện tại các địa điểm % 4,5% Năng lượng tiêu thụ là n

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 4.5, tài liệu 0.03.
- **Hôm nay:** câu này **không còn là tuyên bố** — bị extractor loại với lý do `table_row`
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 104):
  > TABLE
DỮ LIỆU VỀ MÔI TRƯỜNG
TIÊU CHUẨN CHUNG ĐƠN VỊ TÍNH 2025 CHỈ SỐ THEO TIÊU CHUẨN GRI
BIẾN ĐỔI KHÍ HẬU/ PHÁT THẢI KHÍ NHÀ KÍNH & NĂNG LƯỢNG
Tổng phát thải khí nhà kính trực tiếp (Phạm vi 1) (CO2e) Tấn 22.540.603 305-1- Phát thải khí nhà kính (GHG) trực tiếp
- **Kiểm lại theo quy tắc hiện tại:**
  - `1.93404e+08 gj` vs `1.93404e+08 gj` → **chưa chắc** — một bên là mục tiêu, một bên là số thực hiện
  - `4.5 %` vs `4.5 %` → **so được**
  - `4.5 %` vs `0.03 %` → **KHÔNG so được** — khác loại chỉ số con
    - tuyên bố: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'unknown', 'technology': None, 'variant': 'grid', 'scopes': None}
    - bằng chứng: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'unknown', 'technology': None, 'variant': 'renewable', 'scopes': None}

### 8. trang 104 — Năng lượng tiêu thụ là năng lượng tái tạo tại các % 0,03%

- **Lý do cũ:** Bằng chứng đã truy xuất bác bỏ tuyên bố. Số liệu lệch: tuyên bố 0.03, tài liệu 4.5.
- **Hôm nay:** `PARTIALLY_SUPPORTED`
- **Lý do mới:** Có bằng chứng cùng chủ đề nhưng chưa xác minh được đầy đủ. Tuyên bố thiếu: kỳ báo cáo, phạm vi / ranh giới.
- **Đoạn đã tạo ra kết luận cũ** (HPG_Sustainability_Report_2025.pdf, trang 104):
  > GJ 193.403.521 302-1 Tiêu thụ năng lượng trong tổ chức Năng lượng tiêu thụ được cung cấp từ lưới điện tại các địa điểm % 4,5% Năng lượng tiêu thụ là năng lượng tái tạo tại các
- **Kiểm lại theo quy tắc hiện tại:**
  - `0.03 %` vs `4.5 %` → **KHÔNG so được** — khác loại chỉ số con
    - tuyên bố: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'unknown', 'technology': None, 'variant': 'renewable', 'scopes': None}
    - bằng chứng: {'basis': 'percentage_share', 'is_target': False, 'boundary': 'unknown', 'technology': None, 'variant': 'grid', 'scopes': None}

