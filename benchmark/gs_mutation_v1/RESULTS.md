# GS-Mutation v1: kết quả (2026-11-15)

Ngưỡng đăng ký trước: `PREREG_2026-11-14.md`. Tỉ lệ kèm khoảng tin cậy Wilson 95%.

| Kiểu | Đúng khi | Tập | before | after | v2 | internal | contradict |
|---|---|---|---|---|---|---|---|
| M0 | bản gốc không thành CONTRADICTED (1 − tỉ lệ vu oan) | dev | 56/56 = 100% [94–100] | 56/56 = 100% [94–100] | 55/56 = 98% [91–100] | — | — |
| M0 | bản gốc không thành CONTRADICTED (1 − tỉ lệ vu oan) | test | 234/234 = 100% [98–100] | 234/234 = 100% [98–100] | 234/234 = 100% [98–100] | — | — |
| M1 | phóng đại số → CONTRADICTED | dev | 2/29 = 7% [2–22] | 2/29 = 7% [2–22] | 16/29 = 55% [38–72] | — | — |
| M1 | phóng đại số → CONTRADICTED | test | 9/72 = 12% [7–22] | 9/72 = 12% [7–22] | 50/72 = 69% [58–79] | — | — |
| M2 | đảo hướng tăng/giảm → CONTRADICTED | dev | 0/1 = 0% [0–79] | 0/1 = 0% [0–79] | 1/1 = 100% [21–100] | — | — |
| M2 | đảo hướng tăng/giảm → CONTRADICTED | test | 0/16 = 0% [0–19] | 5/16 = 31% [14–56] | 13/16 = 81% [57–93] | — | — |
| M3 | lùi năm gốc → không còn SUPPORTED | test | 9/10 = 90% [60–98] | 9/10 = 90% [60–98] | 10/10 = 100% [72–100] | — | — |
| M4 | xoá phạm vi → báo thiếu phạm vi | dev | 2/6 = 33% [10–70] | 2/6 = 33% [10–70] | 2/6 = 33% [10–70] | — | — |
| M5 | tuyệt đối hoá (X% → 100%, phần lớn → toàn bộ) → không còn SUPPORTED | dev | 6/8 = 75% [41–93] | 6/8 = 75% [41–93] | 7/8 = 88% [53–98] | — | — |
| M5 | tuyệt đối hoá (X% → 100%, phần lớn → toàn bộ) → không còn SUPPORTED | test | 20/20 = 100% [84–100] | 20/20 = 100% [84–100] | 19/20 = 95% [76–99] | — | — |
| M6 | chèn từ quảng bá mơ hồ → cờ mơ hồ hoặc cờ ngôn ngữ quảng bá | dev | 0/29 = 0% [0–12] | 0/29 = 0% [0–12] | 27/29 = 93% [78–98] | — | — |
| M6 | chèn từ quảng bá mơ hồ → cờ mơ hồ hoặc cờ ngôn ngữ quảng bá | test | 0/75 = 0% [0–5] | 0/75 = 0% [0–5] | 71/75 = 95% [87–98] | — | — |
| M7 | thay bằng chứng của công ty khác → không còn SUPPORTED | dev | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] | — | — |
| M7 | thay bằng chứng của công ty khác → không còn SUPPORTED | test | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] | — | — |
| M8 | đổi đơn vị (tấn → kg, kWh → MWh, triệu ↔ nghìn) → không còn SUPPORTED | dev | — | — | 12/12 = 100% [76–100] | — | — |
| M8 | đổi đơn vị (tấn → kg, kWh → MWh, triệu ↔ nghìn) → không còn SUPPORTED | test | — | — | 17/18 = 94% [74–99] | — | — |
| M9 | phóng to ranh giới (nhà máy → toàn Tập đoàn) → không còn SUPPORTED | dev | — | — | 4/4 = 100% [51–100] | — | — |
| M9 | phóng to ranh giới (nhà máy → toàn Tập đoàn) → không còn SUPPORTED | test | — | — | 4/5 = 80% [38–96] | — | — |
| M10 | mục tiêu viết thành đã đạt → không còn SUPPORTED | test | — | — | 3/3 = 100% [44–100] | — | — |
| M0i | một tài liệu, bản gốc → không thành CONTRADICTED | dev | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] | 29/29 = 100% [88–100] |
| M0i | một tài liệu, bản gốc → không thành CONTRADICTED | test | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] | 75/75 = 100% [95–100] |
| M1i | một tài liệu, phóng đại số → CONTRADICTED hoặc cờ không nhất quán nội bộ | dev | 0/29 = 0% [0–12] | 0/29 = 0% [0–12] | 0/29 = 0% [0–12] | 0/29 = 0% [0–12] | 0/29 = 0% [0–12] |
| M1i | một tài liệu, phóng đại số → CONTRADICTED hoặc cờ không nhất quán nội bộ | test | 0/72 = 0% [0–5] | 0/72 = 0% [0–5] | 0/72 = 0% [0–5] | 0/72 = 0% [0–5] | 0/72 = 0% [0–5] |

Lỗi chạy: before 0/865, after 0/865, v2 0/907, internal 0/205, contradict 0/205
Thời gian trung bình mỗi ca (giây): before 0.16, after 0.16, v2 0.15, internal 0.17, contradict 0.16
