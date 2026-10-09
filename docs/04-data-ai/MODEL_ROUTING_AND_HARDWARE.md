# Đúng mô hình cho đúng việc — định tuyến, chi phí, phần cứng

**Cập nhật:** 06/10/2026 · **Thay thế phần mô tả mô hình trong** `configs/models_v1_1.yaml` (bản 07/2026 giả định GPU, không khớp máy thật của nhóm).
Nguồn giá, vùng dữ liệu, số đo CPU và luật dữ liệu: [`../08-knowledge/sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md`](../08-knowledge/sources/2026-10-05_mo-hinh-chi-phi-phan-cung.md).

## 1. Một câu

**Số học, trích tuyên bố, truy xuất và quyết định verdict chạy bằng luật trên CPU; chỉ một việc gọi mô hình ngôn ngữ — đọc những cặp tuyên bố–bằng chứng mà luật không quyết được — và việc đó có chốt chặn, có bộ nhớ đệm, bật bằng một biến.**

## 2. Ba chế độ chạy (`QUANTUM_PROFILE` trong `.env`)

| | `offline` (mặc định) | `cloud` | `gpu` |
| --- | --- | --- | --- |
| Máy | Mọi laptop, 8–16 GB RAM, không GPU | Laptop + khoá FPT AI Marketplace | Máy chủ 1 GPU 24 GB |
| Mô hình ngôn ngữ | Không | GLM-5.2 (FPT, vùng VN) cho cặp luật không quyết được | Mô hình mở qua vLLM (cổng 8001) |
| Truy xuất | BM25 + n-gram ký tự + RRF | như offline (dense chưa được bật mặc định — chờ gold) | BGE-M3 + reranker trên CUDA |
| **Đo được (06/10, i7-1355U)** | **BCPTBV + BCTN Hòa Phát (264 trang): 116 s, RAM đỉnh 1,3 GB** | lần đầu 632 s (710 lời gọi, 8 luồng, 0 lỗi); **chạy lại 188 s, 0 lời gọi** (28/09) | chưa đo [ƯỚC TÍNH 6–11 phút/bộ] |
| Chi phí / bộ hồ sơ | 0 | ≈ US$0,8–2,0 cho ~700 cặp qua GLM-5.2 (việc duy nhất gọi mô hình hôm nay) [ƯỚC TÍNH; số token thật nay được ghi trong `audit.jsonl`]; chạy lại: 0 | điện / thuê GPU |
| Tài liệu rời máy? | **Không** | **Có** — đoạn tuyên bố + đoạn bằng chứng của cặp khó; FPT Serverless có thể xử lý ở Nhật khi quá tải | Không (nếu máy của đơn vị) |
| Dùng cho | demo không mạng, tài liệu nội bộ/mật, máy yếu | tài liệu **công khai** | tài liệu mật, xử lý lô |

Biến ghi rõ trong `.env` luôn thắng chế độ. Kiểm tra máy đang chạy gì: trang **Cài đặt & chế độ chạy** trên giao diện, hoặc `GET /v1/runtime`.

## 3. Bảng định tuyến theo việc (`configs/routing.yaml`, sửa 06/10)

| Việc | Trạng thái | `offline` | `cloud` | Vì sao | Lời gọi & chi phí/bộ (`cloud`) | Phải đo gì trên gold trước khi tin |
| --- | --- | --- | --- | --- | --- | --- |
| So sánh số liệu | **đang chạy** | Python | Python | Mô hình ngôn ngữ không được phân xử số (NumPert: −62% khi số bị nhiễu) | 0 | 17 bẫy xanh, số HPG giữ nguyên |
| Đọc cặp luật không quyết được (`qualitative_stance`) | **đang chạy** | tắt → cặp dừng ở "khớp một phần / chưa đủ bằng chứng" | **GLM-5.2** (US$1,40/4,40 per 1M token vào/ra, vùng VN, 150 yêu cầu/phút) | Chỉ ~90% cặp còn lại sau luật; chốt chặn `llm_stance_decisive: false` | ~700 lời gọi; ≈ US$0,8–2,0 | độ chính xác theo từng quan hệ, nhất là **CONTRADICTS**; tỷ lệ chuyển người xem |
| Trích tuyên bố | kế hoạch | luật | luật (+ gemma-4-26B-A4B-it cho đoạn đã lọc, nếu đo thấy recall tăng) | Khối lượng lớn; mô hình rẻ, vùng VN | 0–113; ≤ US$0,04 | recall/precision tuyên bố (lấy mẫu câu không được trích) |
| Chuẩn hoá 5 thuộc tính | kế hoạch | regex + taxonomy | gemma-4-26B-A4B-it + JSON schema | Điền cấu trúc — mô hình vừa đủ | ~250; ~US$0,02 | khớp chính xác từng thuộc tính |
| Sinh truy vấn | kế hoạch | mẫu | mẫu (mô hình chỉ khi không trúng từ khoá) | Chưa chứng minh tăng recall | ≤ US$0,01 | Recall@5/10 có/không |
| Suy luận pháp lý | kế hoạch | rule pack + người | GLM-5.2 chỉ **đề xuất**, rule pack của Thảo quyết | Khó nhất, ít lời gọi | ~40; US$0,2–0,5 | độ đúng ánh xạ điều khoản (Thảo chấm) |
| Báo cáo cuối | kế hoạch | mẫu tiếng Việt tất định (giấy làm việc) | gemma-4-31B-it | **Llama-3.3-70B bị bỏ**: model card không liệt kê tiếng Việt, ngữ cảnh 32k trên FPT | 1; < US$0,07 | chấm mù; **mọi con số trong văn bản phải có trong `result.json`** |
| Đọc trang scan | kế hoạch | Tesseract `vie` | Qwen2.5-VL-7B (vùng VN) chỉ trang không có lớp chữ | Chỉ khi cần | ~20 trang; ~US$0,04 | CER trên 20 trang scan |

**Đã đổi 06/10 và vì sao:**
- **DeepSeek-V4-Flash và Qwen3.6-27B bị gỡ** khỏi các việc đụng tài liệu người dùng: danh mục FPT ghi vùng dữ liệu **Nhật Bản**.
- **Llama-3.3-70B** thay bằng gemma-4-31B-it cho báo cáo cuối (lý do ở bảng).
- Mỗi việc có `status: active | planned` — chỉ 2 việc đang chạy; danh sách việc "kế hoạch" trước đây đọc như tính năng có sẵn.
- `LOCAL_LLM_BASE_URL` mặc định **rỗng** (trước trỏ `localhost:8000/v1` — trùng cổng API của chính GreenScan, khiến máy mới báo "đã cấu hình Qwen3-8B" dù không có gì chạy).
- Số token mỗi lời gọi (`usage`) nay được cộng vào sự kiện `llm_stance_prefetch` trong `audit.jsonl` → chi phí thật của mỗi lần chạy tính được, không còn chỉ là ước tính.
- GLM-5.2 **giữ nguyên** cho việc đọc cặp khó: các số đo 28/09 và 976 câu trả lời trong bộ nhớ đệm được làm với nó; đổi mô hình trước khi có gold là đổi mà không đo.

## 4. Thác mô hình nên thử sau khi có gold (giảm ~60–90% chi phí lời gọi lớn)

```text
luật + phép tính  →  NLI nhỏ trên CPU (mDeBERTa-xnli, ~0,3B, MIT)  →  gemma-4-26B-A4B-it  →  GLM-5.2  →  người
                     lọc cặp "rõ ràng"                                  mọi cặp còn lại        chỉ khi gemma nói
                                                                                               SUPPORTS/CONTRADICTS
```

Cơ sở: FrugalGPT (giảm tới 98% chi phí ở cùng chất lượng), RouteLLM, AutoMix, Online Cascade Learning; MiniCheck 770M ngang GPT-4 khi kiểm câu với tài liệu, rẻ hơn 400 lần (tiếng Anh). Ước tính cho GreenScan: GLM-5.2 cho mọi cặp ≈ US$0,8–2,0/bộ → thác ≈ US$0,2–0,8/bộ [ƯỚC TÍNH]. Chỉ hai quan hệ SUPPORTS/CONTRADICTS làm đổi kết luận (dưới chốt chặn hiện tại, phần còn lại chỉ đổi cờ người xem), nên mô hình đắt chỉ cần nhìn những cặp đó. **Điều kiện bật:** ngưỡng đăng ký trước trong `configs/measurement_decisions.yaml`, đo trên gold, không trước.

## 5. Vì sao không chạy mô hình ngôn ngữ ngay trên laptop

| Số đo trên i7-1355U (AVX2 + AVX-VNNI, không AVX-512, 2×8 GB DDR4-3200) | |
| --- | --- |
| qwen3:8b qua Ollama | **98 s/lời gọi**, 4,3 token/s → 700 cặp ≈ 19 giờ |
| BGE-M3 tại chỗ (fp32) | 0,49 trang/s ≈ 10 phút/300 trang |
| bge-reranker-v2-m3 tại chỗ | 0,28 cặp/s |
| Vietnamese_Embedding qua FPT | 77,7 trang/s |

Hướng khả thi trên CPU (đều là TEST): encoder nhỏ lượng tử hoá int8 qua OpenVINO/ONNX (~2–3 lần nhanh hơn theo tài liệu Sentence-Transformers, giữ ~99% chất lượng); multilingual-e5-small (~1/14 phép tính của BGE-M3) cho máy 8 GB; mô hình ngôn ngữ ≤ 4B chỉ cho ≤ 30–50 cặp khó nhất chạy nền.

## 6. Dữ liệu và quy tắc gửi ra ngoài

Tóm tắt (chi tiết pháp lý: [`../08-knowledge/02_PHAP_LY_VIET_NAM.md`](../08-knowledge/02_PHAP_LY_VIET_NAM.md) §6):

| Loại tài liệu | Chế độ được phép |
| --- | --- |
| A — Công khai (BCPTBV, BCTN đã công bố) | `offline`, `cloud` |
| B — Nội bộ, chưa công bố | `offline`, `gpu`, hoặc FPT Dedicated có hợp đồng xử lý dữ liệu |
| C — Mật nghề nghiệp (giấy làm việc kiểm toán) | **chỉ** `offline` / `gpu` trên hạ tầng của đơn vị |

Không dùng gói miễn phí của Gemini cho tài liệu người dùng tải lên (gói đó dùng dữ liệu để cải thiện sản phẩm). Vietnamese_Embedding: model card Hugging Face ghi Apache-2.0, trang FPT ghi CC-BY-NC-4.0 → **cần xác nhận bằng văn bản trước khi thương mại hoá**.

## 7. Việc cần đo (đã có công cụ: `tools/measure_all.py`, `tools/evaluate_gold.py`)

1. Độ chính xác theo từng quan hệ của GLM-5.2 (đặc biệt CONTRADICTS) → quyết định tháo chốt chặn (D-2026-09-28-01).
2. Độ đồng thuận NLI–gemma–GLM trên cùng cặp → quyết định thác.
3. Recall@k: Vietnamese_Embedding vs BGE-M3 vs e5 (ứng viên gộp từ **mọi** bộ truy xuất trước khi gán nhãn — tránh pooling bias).
4. Token thật mỗi bộ hồ sơ (nay đã ghi) → thay mọi con số [ƯỚC TÍNH] ở trên.
