# Thang kích thước mô hình trên ca có đáp án dựng sẵn — 10/10/2026

**Câu hỏi:** kích thước mô hình ngôn ngữ có phải là giới hạn của bài toán kiểm chứng tuyên bố môi trường không? (một giảng viên nhận xét "mô hình của nhóm quá bé"). Phân tích đầy đủ: [`../../docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`](../../docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md).

## Thiết kế

| | Bộ sạch (`cases.py`) | Bộ trang thật (`cases_noisy.py`) |
| --- | --- | --- |
| Số ca | 32 | 19 |
| Bằng chứng | 1–2 câu tổng hợp, "Công ty" chung chung | **nguyên văn** chữ PyMuPDF trích từ 3 trang công khai của Hòa Phát: bảng KNK dàn phẳng (BCPTBV 2025 tr.39), trang tóm tắt hai cột dính chữ (tr.9), đoạn nhiều số hai ranh giới (BCTN 2024 tr.86) |
| Nhóm lỗi | 13: khớp sau làm tròn · lệch một con số · tính lại % · khác cơ sở đo · khác Scope · khác kỳ · mục tiêu/thực hiện · khác ranh giới · đơn vị/hệ số · dung sai theo độ chính xác · cộng lại bảng · bẫy từ phủ định · không liên quan | 3: bảng dàn phẳng · chữ dính cột · nhiều số nhiều ranh giới |

- **Nhãn:** S (bằng chứng xác nhận) · C (cùng chỉ số, kỳ, phạm vi, ranh giới, loại giá trị nhưng giá trị lệch ngoài sai số làm tròn) · N (không đủ để xác nhận hay bác bỏ). Đáp án suy từ ngữ nghĩa nghiệp vụ (GHG Protocol, cách đọc báo cáo), **không** từ luật của GreenScan; ca mà kiểm toán viên có thể chấp nhận hai nhãn thì ghi cả hai.
- **GreenScan:** chế độ ngoại tuyến (`QUANTUM_LLM_STANCE=off`), tài liệu tuyên bố `internal`, tài liệu bằng chứng `external`. Ánh xạ: có CONTRADICTED → C; mọi kết luận SUPPORTED → S; còn lại (khớp một phần, chưa đủ bằng chứng, không trích được tuyên bố) → N.
- **Mô hình:** cùng một prompt tiếng Việt có **định nghĩa ba nhãn** (đưa cho mô hình đúng quy tắc kiểm toán viên dùng), nhiệt độ 0, trả JSON. Qua FPT AI Marketplace: gemma-4-26B-A4B-it (MoE, ~3,8B kích hoạt), gemma-4-31B-it, Llama-3.3-70B-Instruct, GLM-5.2 (753B tổng, MoE). Tại máy: qwen3:8b qua Ollama trên CPU. Bộ trang thật chỉ gửi tới các mô hình FPT ghi vùng Việt Nam.

## Kết quả

Bộ sạch (n = 32):

| Hệ thống | Đúng | KTC 95% (Wilson) | Dám kết luận (S/C) | Đúng trên phần kết luận | Xác nhận sai | Mâu thuẫn sai | McNemar p so với GreenScan |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GreenScan (luật, ngoại tuyến) | 20/32 | 45–77% | 8/32 | 6/8 | 1 | 1 | — |
| gemma-4-26B-A4B-it | 29/32 | 76–97% | 17/32 | 15/17 | 1 | 1 | 0,012 |
| gemma-4-31B-it | 32/32 | 89–100% | 18/32 | 18/18 | 0 | 0 | 0,0005 |
| Llama-3.3-70B-Instruct | 30/32 | 80–98% | 17/32 | 15/17 | 2 | 0 | 0,002 |
| GLM-5.2 | 32/32 | 89–100% | 18/32 | 18/18 | 0 | 0 | 0,0005 |
| qwen3:8b (CPU, không suy nghĩ) | 28/32 | 72–95% | 17/32 | 13/17 | 3 | 1 | 0,022 |

Bộ trang thật (n = 19):

| Hệ thống | Đúng | KTC 95% | Dám kết luận | Đúng trên phần kết luận | Xác nhận sai | Mâu thuẫn sai | McNemar p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GreenScan (luật, ngoại tuyến) | 7/19 | 19–59% | 3/19 | 3/3 | 0 | 0 | — |
| gemma-4-26B-A4B-it | 18/19 | 75–99% | 16/19 | 15/16 | 1 | 0 | 0,001 |
| gemma-4-31B-it | 17/19 | 69–97% | 17/19 | 15/17 | 2 | 0 | 0,002 |
| Llama-3.3-70B-Instruct | 15/19 | 57–91% | 16/19 | 13/16 | 3 | 0 | 0,022 |
| GLM-5.2 | 17/19 | 69–97% | 16/19 | 14/16 | 2 | 0 | 0,002 |
| qwen3:8b (CPU, không suy nghĩ) | 12/19 | 41–81% | 13/19 | 9/13 | **4** | 0 | 0,063 |

Thời gian trung bình mỗi lời gọi (bộ sạch): gemma-26B-A4B 1,2 s · gemma-31B 1,5 s · Llama-70B 2,8 s · GLM-5.2 13,7 s (327 token đầu ra — mô hình suy luận) · qwen3:8b trên CPU **66 s** (bộ sạch) và **257 s** (trang thật, ~3–4 nghìn ký tự) khi tắt suy nghĩ; bật suy nghĩ thì **chưa xong ca đầu sau 15 phút** (đã dừng).

## Lỗi — đọc từng ca

- **GreenScan, bộ sạch (12 sai):** 4 ca số lệch 9–25% cùng chỉ số bị trả "khớp một phần" thay vì mâu thuẫn (F03, F04, F07, F27 — ngưỡng `0,35` chưa kiểm chứng); 3 ca bộ trích không nhận ra tuyên bố (F05, F22, F23 — "sử dụng 15 triệu m3 nước", "đáp ứng 90% nhu cầu điện"); **F11 xác nhận sai** (cường độ giảm 5% đem so với tổng giảm 5%); **F20 mâu thuẫn sai** (công ty mẹ đem so với hợp nhất); F26 không cộng thành phần để kiểm tổng; F18, F25 không bắt được 30% thực hiện vs 18%, 12,0% vs 12,4%.
- **GreenScan, bộ trang thật (12 sai):** 10 ca không trích được tuyên bố; 2 ca khớp đúng số nhưng chỉ ra "khớp một phần". Không có xác nhận sai, không có mâu thuẫn sai.
- **Mô hình, bộ trang thật:** mọi lỗi xác nhận sai rơi vào **bảng dàn phẳng** (tr.39): N02 (gán 23.369.500 của *mảng thép* cho *phạm vi 1*) — sai ở gemma-31B, Llama-70B, **GLM-5.2**; N05 (gán 933.876 của *phạm vi 2* cho *mảng nông nghiệp*) — sai ở **cả bốn** mô hình FPT. Lý do mô hình đưa ra đều là "khớp hoàn toàn".
- **qwen3:8b (tại máy):** xác nhận sai nhiều nhất thang — bộ sạch F04 (833.876 so với 933.876 → "khớp"), F07 (giảm 15% so với tuyên bố 20% → "khớp"); trang thật N02, N05 (bảng dàn phẳng, như mọi mô hình), **N11 (bằng chứng 98%, tuyên bố 90% → "khớp")**, N15 (gán 3,18 tỷ kWh của hai khu cho riêng Dung Quất).
- **Mô hình, bộ sạch:** gemma-26B-A4B nhầm đơn vị (MWh điện vs tấn than → C), dung sai (12,0% vs 12,4% → S), một lần không trả đúng định dạng; Llama-70B coi 15% là "khớp trong sai số làm tròn" với 20% và 12,4% với 12,0%.

## Giới hạn — đọc trước khi trích dẫn

1. **n nhỏ** (32 + 19): kết luận về *mẫu lỗi* và khác biệt lớn (luật vs mô hình); khác biệt giữa các mô hình **không phát hiện được**, không có nghĩa là bằng nhau.
2. **Một người dựng ca và đáp án** (soạn với hỗ trợ của AI, 10/10). Cần Quỳnh/Thảo gán lại độc lập và viết thêm ca mới trước khi dùng làm số chính thức.
3. **Prompt có định nghĩa nhãn** — điều kiện tốt nhất cho mô hình. Chưa đo prompt ngắn, chưa đo nhiều lần chạy.
4. **Mỗi ca một cặp tuyên bố–bằng chứng**, bằng chứng đưa sẵn: không đo truy xuất, không đo đọc cả báo cáo 264 trang, không đo tính độc lập của nguồn (bằng chứng gắn `external` cho GreenScan).
5. Đây **không** phải gold; không thay bộ gán nhãn D9.

## Chạy lại

```bash
# từ gốc repo, có khoá FPT trong .env
python benchmark/size_ladder_2026-10-10/run_ladder.py benchmark/size_ladder_2026-10-10/results_clean.json
LADDER_CASES=cases_noisy python benchmark/size_ladder_2026-10-10/run_ladder.py benchmark/size_ladder_2026-10-10/results_noisy.json
# mô hình tại máy (Ollama đang chạy, đã pull qwen3:8b); LADDER_THINK=1 để bật suy nghĩ
LADDER_CASES=cases python benchmark/size_ladder_2026-10-10/run_local.py benchmark/size_ladder_2026-10-10/results_local_clean.json qwen3:8b
LADDER_CASES=cases_noisy python benchmark/size_ladder_2026-10-10/run_local.py benchmark/size_ladder_2026-10-10/results_local_noisy.json qwen3:8b
python benchmark/size_ladder_2026-10-10/summarize.py benchmark/size_ladder_2026-10-10/results_clean.json benchmark/size_ladder_2026-10-10/results_local_clean.json
```
Chi phí một lượt FPT (51 ca × 4 mô hình): dưới 1 USD.

## Bổ sung cùng ngày: che số + tên (ngoại tuyến một phần) và thử nhận diện lại

Thiết kế và phân tích: [`../../docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`](../../docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md).

`run_masked.py`: mọi con số → `<S1>`, `<E1>`… (giá trị ở lại máy), tên doanh nghiệp/cơ sở → nhãn; mô hình **chỉ trả lời ánh xạ** (trực tiếp / tổng / % thay đổi / không ứng); mã điền giá trị và so tại máy.

| Mô hình | Che: sạch (32) | Che: trang thật (19) | Xác nhận sai | Mâu thuẫn sai |
| --- | --- | --- | --- | --- |
| gemma-4-26B-A4B-it | 31 | 16 | 0 | 1 |
| gemma-4-31B-it | **32** | **18** | **0** | 1 |
| GLM-5.2 | 32 | 16 | 0 | 3 |

So với không che (bảng trên): độ chính xác trong sai số; xác nhận sai 1–3 → **0**. Lỗi còn lại: chọn nhầm cột phần trăm trong bảng dàn phẳng (N03, N04). GLM-5.2 lượt trước được 17/19 trên cùng bộ — kết quả dao động giữa các lượt dù nhiệt độ 0.

Lỗi của chính bộ che, tìm ra và sửa trong thí nghiệm: số thứ tự đầu dòng ("1. Tổng…") bị che làm mô hình tưởng là tổng; chiều "giảm" đọc nhầm vị trí ("20" trong "2025"); "năng lượng" đọc thành "nâng" sau khi bỏ dấu; khoảng số "5.6-6.2%" lọt như số hiệu; tên ngắt dòng "Hòa⏎Phát" lọt qua regex.

`reid_test.py` (gemma-4-31B-it, phiên `cd5a82e3`): hỏi "đây là doanh nghiệp nào" trên đúng nội dung đã che → **đoán đúng 5/20 câu tuyên bố, 3/3 trang** (độ tự tin 100 ở trang) dù không còn tên nào — suy ra từ ngữ cảnh ngành. Kết quả: `results_masked_clean.json`, `results_masked_noisy.json`, `results_reid.json`.

```bash
python benchmark/size_ladder_2026-10-10/run_masked.py benchmark/size_ladder_2026-10-10/results_masked_clean.json gemma-4-31B-it GLM-5.2
LADDER_CASES=cases_noisy python benchmark/size_ladder_2026-10-10/run_masked.py benchmark/size_ladder_2026-10-10/results_masked_noisy.json gemma-4-31B-it GLM-5.2
python benchmark/size_ladder_2026-10-10/reid_test.py .quantum/runs/<id> benchmark/size_ladder_2026-10-10/results_reid.json gemma-4-31B-it
```
