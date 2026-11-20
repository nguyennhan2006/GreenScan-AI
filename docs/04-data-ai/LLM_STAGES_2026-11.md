# Mô hình ngôn ngữ theo từng giai đoạn: kết quả đo và quyết định bật cờ (11/11/2026)

Đăng ký trước khi đo: `configs/measurement_decisions.yaml`, khối `llm_stages_v1` (16:45, sửa đổi 17:05 ghi trước lượt chạy kép).
Nhãn là nhãn bạc (Claude gán hai lượt, có phân xử, chưa có người soát), nên mọi con số dưới đây là số bạc.

## Nguyên tắc không đổi
- Mô hình chỉ đọc, gợi ý hoặc diễn đạt. Kết luận và điểm rủi ro do quy tắc và phép tính quyết (`llm_stance_decisive: false`).
- Mỗi giai đoạn có cờ riêng, mặc định tắt. Cờ chỉ bật ở hồ sơ mà giai đoạn đã qua cổng, **trên đúng cấu hình sản phẩm** (prompt có rào, lượng tử hoá, máy chạy).
- Mỗi họ mô hình có prompt riêng (`src/quantum_gw/assist/prompts.py`):

| Giai đoạn | Họ nhỏ (Qwen3-4B / 8B) | Họ lớn (gpt-oss-120b, Qwen3-32B, GLM) |
|---|---|---|
| S5 chấm quan hệ (sản phẩm, có rào) | stance-s1f | stance-v3f |
| S2 thuộc tính | attr-s1 | attr-v1 |
| S6 lời giải thích | explain-s2 | explain-v2 |
| S1 lọc tuyên bố | huấn luyện e5 (4 lớp, Kaggle) | — |

## Kết quả và quyết định

| Giai đoạn | Chỉ số chính | Quy tắc | Mô hình tốt nhất | An toàn | Cổng | Cờ |
|---|---|---|---|---|---|---|
| S1 lọc tuyên bố (e5) | bắt câu không phải tuyên bố / gắn nhầm tuyên bố thật | 11/44 · 1/102 | e5-small 28/44 · 26/102 | trần 6/102 | **trượt** (không ngưỡng nào đạt) | `QUANTUM_CLAIM_MODEL` trống |
| S2 thuộc tính | macro-F1 thuộc tính thiếu | 0,578 | gpt-oss 0,594; Qwen 0,566–0,573 | chỉ giữ cụm nguyên văn | **trượt** (không vượt quy tắc) | `QUANTUM_ASSIST_ATTRIBUTES` tắt |
| S4 đọc kép số liệu | 17 bẫy + bất biến; thời gian HPG | — | 72/72 test qua | 0 kết luận, 0 điểm rủi ro bị đổi | **trượt trên laptop** (2,81 lần > 2,0) | `QUANTUM_VERIFY=rules` |
| S5 chấm quan hệ | macro-F1 (S, O) | 0,397 | Kaggle bf16: 4B 0,605 · 8B 0,617 · 32B 0,575 | sai C ≤ quy tắc + 1 / 100 | qua trên bf16, **trượt trên cấu hình sản phẩm** | `QUANTUM_LLM_STANCE` tắt ở offline |
| S6 lời giải thích | tỉ lệ nêu đủ ý | 0,015 | gpt-oss 0,356 · 32B 0,210 · 4B 0,140 | 0 lời giải thích giữ lại có số mới | **qua** (cả cấu hình sản phẩm) | `QUANTUM_ASSIST_EXPLAIN=queue` ở hồ sơ gpu |

### Đo đối chiếu cấu hình sản phẩm (laptop, Ollama Qwen3-4B Q4, prompt có rào)
| | Quy tắc | 4B bf16, prompt cũ (Kaggle) | 4B Q4, prompt sản phẩm (laptop) | Thời gian |
|---|---|---|---|---|
| S5, 120 cặp | 0,404, sai C 0 | 0,630, sai C 0 | 0,683 [0,597; 0,822], **sai C 2 (1,67 / 100)** | 33,7 s / cặp |
| S6, 40 mục | 0,008 | 0,140 | 0,079 [0,044; 0,138], 1 bản có số mới (bị chặn) | 81 s / mục |

- S5: bản bf16 qua cổng nhưng bản Q4 có rào thì không. Kết quả trên Kaggle không được chuyển sang sản phẩm. Ngoài ra một lượt HPG có khoảng 700 cặp, tức khoảng 6,6 giờ trên laptop.
- S6: qua cổng nhưng chỉ còn khoảng nửa điểm bản bf16. 13/40 bản thô chép mã tên tệp; code thay bằng "tài liệu" trước khi hiển thị. Không bản nào dùng tên trường tiếng Anh.

## Cờ theo hồ sơ (sau 11/11)
| Hồ sơ | S1 | S2 | S4 | S5 | S6 |
|---|---|---|---|---|---|
| offline (demo nộp) | tắt | tắt | tắt | tắt | tắt; bật được bằng `QUANTUM_ASSIST_EXPLAIN=queue` (khoảng 11 phút cho 8 tuyên bố trong hàng soát) |
| gpu | tắt | tắt | chưa đo, giữ `rules` | `on_ambiguous` (có từ trước; chỉ để người soát xem, chưa đo bản có rào trên vLLM) | `queue` |
| cloud | tắt | tắt | tắt | `on_ambiguous` nhưng khoá FPT chết (401) nên không chạy | tắt (Groq chỉ dùng cho tài liệu công khai, hồ sơ không phân biệt được) |

Lượt đo đặt `LOCAL_LLM_PROVIDER=ollama`, `LOCAL_LLM_BASE_URL=http://localhost:11434` trong môi trường của lệnh. `.env` không đổi, nên bản demo nộp không có mô hình cục bộ.

## Lỗi tìm ra khi đo (đã sửa, có test)
1. `OllamaProvider` bỏ qua mô hình theo nhiệm vụ trong `routing.yaml`. Đã thêm `bind_model`.
2. Bộ chặn số của S6 coi số trang và mã tên tệp (chính prompt đưa vào) là số bịa, nên chặn 40/40. Đã tính chúng là nguồn (sửa trước khi đọc chất lượng).
3. Lời giải thích chứa tên trường tiếng Anh và mã tên tệp, trái quy định giao diện chỉ tiếng Việt. Đã sửa bằng explain-v2 / s2 và bước làm sạch trong `assist/stages.py`.

## Giới hạn
- Nhãn bạc; tập con nhỏ (S5 120 cặp với gpt-oss và laptop, S6 40 mục). Chỉ có 2 ca CONTRADICTS trong 120 cặp, nên chỉ số sai C dao động mạnh.
- Thời gian trên GPU / đám mây cho S4 là ước tính, chưa đo.

## Tệp
- Bộ dữ liệu và chấm: `benchmark/llm_stages/build_sets.py`, `score.py` (`--on=` để chấm cùng tập con).
- Đầu ra: `benchmark/llm_stages/{api_out,kaggle_out,ollama_out}/`. Notebook: `docs/RUNS.md`.
