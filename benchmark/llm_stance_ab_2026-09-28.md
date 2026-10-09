# Mô hình xét quan hệ tuyên bố–bằng chứng: bật thật trên HPG — 2026-09-28

Cùng hai tài liệu (HPG BCPTBV 2025 + BCTN 2024), cùng code, chỉ khác cách xét những cặp mà luật từ khoá và phép so số **không quyết được**.

| | Tắt LLM (`185480a0`, 25/09) | Bật, không chốt chặn (`288cc3f7`) | **Bật, có chốt chặn (`b96cbd0f`)** |
| --- | ---: | ---: | ---: |
| Cặp do luật từ khoá/số học quyết | 67 | 67 | 67 |
| Cặp "đoán theo độ giống chữ" | **713** | 0 | 0 |
| Cặp do GLM-5.2 đọc | 0 | 713 | 713 |
| Quan hệ PARTIAL / CONTEXT / SUPPORTS / CONTRADICTS | 648 / 84 / 48 / 0 | 290 / 327 / 151 / 12 | 290 / 327 / 151 / 12 |
| Kết luận PARTIAL / SUPPORTED / CONTRADICTED / INSUFFICIENT | 153 / 2 / 0 / 1 | 136 / 6 / **10** / 4 | 150 / 2 / 0 / 4 |
| Mức rủi ro HIGH + CRITICAL (DN đối chứng) | 0 | **8 + 2** | 0 |
| Câu chuyển người xem vì mô hình | 0 | 156 | **13** |
| Số lý do PARTIAL khác nhau | 31 | 28 | 43 |
| Gọi API / thời gian gọi | 0 | 710 / 451 s, 0 lỗi | 0 (bộ nhớ đệm) |
| Tổng thời gian chạy | 144 s | 632 s | 188 s |

Cổng hồi quy `run_case.py --all` (4 ca thật): **4/4 khớp** cả khi bật lẫn tắt; `risk band 0.5` là mức sẵn có, không đổi.

## Đọc bảng

- **Mô hình đọc được nội dung**: 713 cặp trước đây mặc định PARTIAL vì giống chữ, nay 327 cặp được nhận ra là chỉ bối cảnh và 151 cặp là xác nhận. Ba tuyên bố chuyển đúng sang `INSUFFICIENT_EVIDENCE` (bằng chứng nói về chuyển đổi số / tiêu đề mục / rủi ro chung, không phải điều tuyên bố nói).
- **Để mô hình tự quyết là sai hướng**: 10 `CONTRADICTED` và 2 `CRITICAL` trên doanh nghiệp đối chứng, phần lớn sai khi soát tay — câu tuyên bố bị trích dính cột, câu giải thích quy trình luyện thép, dòng bảng lỗi "GIỚI TÍNH: 100 %" bị đọc thành "100 % nam", "phát thải trực tiếp" so với "gián tiếp". Đây đúng là loại lỗi 22/09.
- **Chốt chặn** (`llm_stance_decisive: false`): lập trường của mô hình một mình không tạo ra `SUPPORTED` hay `CONTRADICTED`; nghi mâu thuẫn → `PARTIALLY_SUPPORTED` + chuyển người xem; cờ người xem chỉ bật khi mô hình làm đổi kết luận so với luật hoặc nghi mâu thuẫn (13/156).

## Chưa nói được

Không có con số độ chính xác nào ở đây — đây là phân bố, không phải đúng/sai. Câu hỏi quyết định là **151 SUPPORTS và 12 CONTRADICTS của mô hình đúng bao nhiêu phần**; trả lời trên lô 1 gold (về 1/10) bằng `evaluate_gold.py` với `llm_stance` tắt / bật / bật + `llm_stance_decisive`. Chốt chặn chỉ được tháo cho quan hệ nào gold chứng minh đủ đúng.
