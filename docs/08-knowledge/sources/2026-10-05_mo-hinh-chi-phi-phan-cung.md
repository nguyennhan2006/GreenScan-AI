# GreenScan AI — Chọn đúng mô hình cho từng việc: giá API, phần cứng, ba tầng triển khai và bảo vệ dữ liệu

- **Ngày nghiên cứu:** 05/10/2026. Mọi giá ghi "đọc 05/10/2026" trừ khi ghi khác.
- **Phạm vi:** nghiên cứu web + **đọc** (không sửa) repo: `configs/routing.yaml`, `configs/default.yaml`, `src/quantum_gw/verification/llm_judge.py`, `src/quantum_gw/providers/*.py`, bộ đệm `.quantum/`. Có chạy vài lệnh **chỉ đọc** trên chính laptop (CPUID, WMI, đếm token bằng tokenizer đã có sẵn trong cache Hugging Face) — không tải mô hình mới, không sửa file nào của repo.
- **Ký hiệu:** **[ĐO]** = số đo thật (của nhóm, hoặc tôi đo trong phiên này); **[ƯỚC TÍNH]** = tôi suy ra từ số đo + giả định nêu rõ, phải đo lại trước khi dùng; **[UNVERIFIED]** = không xác nhận được từ nguồn chính thức.
- **Tỷ giá dùng để quy đổi:** 1 USD ≈ 25.949 VND (open.er-api.com, cập nhật 05/10/2026 00:02 UTC) [R40]. FPT niêm yết giá bằng USD; giao diện thanh toán có mục chọn tiền tệ.

---

## 0. Tóm tắt điều hành

1. **Giá FPT tìm được công khai, chính xác đến từng mô hình.** Trang FPT AI Marketplace tải danh mục từ một API công khai (không cần đăng nhập) trả về giá USD/1M token, vùng xử lý (VN/JP), giới hạn RPM/TPM và cờ hỗ trợ JSON schema [R1]. Ví dụ (đọc 05/10/2026): **GLM-5.2 $1,40 vào / $4,40 ra / $0,26 cached**; DeepSeek-V4-Flash $0,14/$0,28; gpt-oss-120b $0,143/$0,605; gemma-4-26B-A4B-it $0,14/$0,40; gemma-4-31B-it $0,15/$0,45; Llama-3.3-70B $0,209/$0,451; Qwen3.6-27B $0,30/$3,25; Qwen2.5-VL-7B $0,77/$0,77; **Vietnamese_Embedding $0,011/1M token; bge-reranker-v2-m3 $0,022/1M; multilingual-e5-large $0,022/1M**. **gpt-oss-20b không có trong danh mục công khai** ngày 05/10/2026.
2. **Tiền không phải nút thắt.** Một bộ hồ sơ (báo cáo 200 trang + BCTN 100 trang) chạy qua FPT tốn khoảng **$0,4–0,9 (≈10–23 nghìn VND)** nếu lập trường dùng gemma-4 và GLM-5.2 chỉ làm pháp lý; **$0,5–1,4 (≈13–36 nghìn VND)** với thác khuyến nghị (gemma-4 + GLM-5.2 cho 100–200 cặp khó); **$1,1–2,7 (≈29–70 nghìn VND)** nếu như hiện nay mọi cặp đi qua GLM-5.2 [ƯỚC TÍNH, §5]. GLM-5.2 chiếm phần lớn chi phí. Nút thắt thật là **độ đúng trên gold, giới hạn RPM, và nơi dữ liệu được xử lý**.
3. **Hai phát hiện về dữ liệu cần sửa ngay trong `routing.yaml`:** (a) Gói Serverless của FPT **tự chuyển yêu cầu VN↔JP khi quá tải** — "dữ liệu có thể được xử lý ở vùng khác vào giờ cao điểm"; chỉ **Dedicated Inference** mới khoá vùng [R3]. (b) Danh mục ghi **DeepSeek-V4-Flash và Qwen3.6-27B có vùng dữ liệu JP** [R1] — đúng hai mô hình mà `routing.yaml` đang giao cho trích xuất/chuẩn hoá/sinh truy vấn. Các mô hình "Partner" (tiền tố Azure:, Alibaba:, Google:, Z.ai:) đi qua bên thứ ba.
4. **Giấy phép mâu thuẫn:** trang FPT ghi **Vietnamese_Embedding theo CC-BY-NC-4.0 (phi thương mại)** [R1], nhưng model card gốc của AITeamVN trên Hugging Face ghi **Apache-2.0** [R55]. Dùng cho cuộc thi/nghiên cứu không vướng; trước khi thương mại hoá phải hỏi FPT/AITeamVN bằng văn bản. Ngoài ra trên VN-MTEB, mô hình này **không hơn** bge-m3 gốc (ClimateFEVER-VN 13,25 so với 21,27) [R53] → phải đo lại trên gold (§4.2).
5. **Llama-3.3-70B không hỗ trợ chính thức tiếng Việt** (model card: en, de, fr, it, pt, hi, es, th) và chỉ có ngữ cảnh 32k trên FPT [R1] → không nên giữ cho `final_report`. Đổi sang gemma-4-31B-it hoặc GLM-5.2, chấm mù trên vài báo cáo.
6. **Laptop i7-1355U:** tôi kiểm tra CPUID: **có AVX2 + AVX-VNNI, không có AVX-512/AMX**; RAM **2×8 GB DDR4-3200** [ĐO]. Các số đo của nhóm khớp với ~170 GFLOPS hiệu dụng (fp32) → sinh chữ bằng LLM 4–8B tại chỗ không dùng được cho 700 cặp; nhưng **encoder nhỏ + int8 (ONNX Runtime/OpenVINO) dùng được** (nhanh hơn ~2,5–4 lần theo tài liệu Sentence-Transformers [R20–R22]).
7. **Nghiên cứu ủng hộ một "thác" (cascade):** luật → mô hình nhỏ (NLI/cross-encoder) → LLM vừa → LLM lớn/người, chỉ leo thang khi độ tin cậy thấp (FrugalGPT, RouteLLM, AutoMix, MiniCheck…) [R10–R19]. Đặc biệt MiniCheck: mô hình 770M đạt độ đúng ngang GPT-4 khi kiểm chứng câu với tài liệu, rẻ hơn 400 lần [R15] — đúng loại việc "lập trường tuyên bố–bằng chứng" của GreenScan.
8. **Bảng định tuyến cuối cùng ở §7.** Nguyên tắc: định lượng = Python; khối lượng lớn = luật/encoder/mô hình rẻ; GLM-5.2 chỉ cho cặp khó + pháp lý; báo cáo cuối = mô hình viết tiếng Việt tốt; tài liệu mật = không gửi Serverless.

---

## 1. Số liệu nền dùng trong cả báo cáo

### 1.1 Máy phát triển (kiểm tra trực tiếp 05/10/2026) [ĐO]

| Thành phần | Giá trị | Cách kiểm tra |
|---|---|---|
| CPU | 13th Gen Intel Core i7-1355U, 10 nhân / 12 luồng (2P + 8E) | WMI `Win32_Processor` |
| Tập lệnh | AVX2 **có**; **AVX-VNNI có**; AVX-512F/AVX512-VNNI **không**; AMX **không** | đọc CPUID leaf 7 (subleaf 0 và 1) |
| RAM | 2 × 8 GB Samsung **DDR4-3200** (SMBIOS type 26) → kênh đôi, băng thông lý thuyết 2 × 3200 MT/s × 8 B = **51,2 GB/s** | WMI `Win32_PhysicalMemory` |
| iGPU | Intel Iris Xe Graphics, driver 32.0.101.7076 | WMI `Win32_VideoController` |
| Phần mềm | Python 3.14; onnxruntime 1.30.0; sentence-transformers 5.1.2; torch 2.12.1+cpu (dùng 10 luồng) | `pip list` |

Hệ quả: lượng tử hoá **int8** trên máy này chạy bằng lệnh VNNI 256-bit (AVX-VNNI) — khi xuất ONNX int8 phải chọn cấu hình **`avx2`**, không phải `avx512_vnni` (tài liệu ST nói các cấu hình cho tốc độ "gần tương đương" trên máy của tác giả, nhưng máy này không có AVX-512) [R21]. Bánh xe (wheel) cho Python 3.14/Windows đã có: **onnxruntime 1.30.0 cp314 win_amd64** và **openvino 2026.4.1 cp314 win_amd64** (PyPI, đọc 05/10/2026) [R27].

### 1.2 Khối lượng công việc chuẩn — "một bộ hồ sơ" = báo cáo 200 trang + BCTN 100 trang

| Đại lượng | Giá trị dùng | Nguồn |
|---|---|---|
| Trang | 300 | đề bài |
| Chunk | ~3.000 (≈10 chunk/trang) | [ĐO] lần chạy HPG `b96cbd0f` (28/09): 264 trang (BCPTBV 2025: 108 + BCTN 2024: 156) → 2.645 chunk |
| Ký tự/trang | ~2.000 | [ĐO] lấy mẫu 16 trang BCTN HPG 2024 bằng pypdf: 2.029 ký tự/trang |
| Token cho một đoạn 600 ký tự tiếng Việt | **~212 token (tokenizer Qwen3)**; **~167 token (tokenizer XLM-R của bge-m3/e5)** → 2,82 và 3,58 ký tự/token | [ĐO] 202 đoạn 600 ký tự từ BCTN HPG 2024 trang 11–70, tokenizer có sẵn trong cache |
| Toàn văn 300 trang | ~600 nghìn ký tự ≈ 170k token XLM-R ≈ 210k token Qwen | suy ra từ hai dòng trên |
| Tuyên bố | ~250 | [ƯỚC TÍNH] HPG có 156 tuyên bố từ báo cáo 108 trang |
| Cặp lập trường còn lại sau luật | ~700 | đề bài; HPG: 713 cặp (67 cặp do luật quyết) |
| Một lời gọi stance | ~550 token vào (system 165 + schema 73 + tuyên bố + đoạn 600 ký tự), ~80 token ra hiển thị (p90: 103) | [ĐO] đếm bằng tokenizer Qwen3 trên prompt thật trong `llm_judge.py` và 976 câu trả lời GLM-5.2 trong `.quantum/llm_cache/stance_cache.jsonl` |
| Cặp rerank | 250 tuyên bố × `candidate_k`=30 = **7.500 cặp** | `configs/default.yaml` |
| Kiểm tra pháp lý / báo cáo cuối / trang scan | ~40 lời gọi / 1 lời gọi (~30k vào, ~5k ra) / ~20 trang | [ƯỚC TÍNH] |

Hai con số thời gian thật của nhóm làm mốc: pipeline **không LLM** chạy HPG 144 s; bật GLM-5.2 cho 710 cặp: 632 s (trong đó 710 lời gọi/451 s/8 luồng/0 lỗi); chạy lại có cache: 188 s [ĐO, `benchmark/llm_stance_ab_2026-09-28.md`]. Embedding qua FPT: **77,7 trang/s** (15.409 trang, 14.708 vector) so với bge-m3 tại chỗ **0,49 trang/s** [ĐO, `MEASUREMENT_PROTOCOL_2026-09-29.md`].

### 1.3 Đọc lại các số đo của nhóm bằng phép tính FLOPs [ƯỚC TÍNH]

- bge-m3 và bge-reranker-v2-m3 đều là XLM-RoBERTa-large: ~302M tham số **không tính bảng embedding** (24 lớp × 12,6M) → ~0,6 GFLOP cho mỗi token.
- 0,49 trang/s × ~567 token/trang (2.029 ký tự ÷ 3,58) × 0,6 GFLOP ≈ **170 GFLOPS hiệu dụng** — hợp lý cho chip 15 W chạy fp32.
- Reranker 0,28 cặp/s × 0,6 GFLOP × N = 170 GFLOPS → N ≈ **1.000 token/cặp**. Tức là phép đo rerank dùng đoạn dài cỡ cả trang (nhất quán với việc vector hoá theo trang trong bộ đo) hoặc độn (padding) tới 512–1.024 token. Với đơn vị là **chunk ~170 token**, cùng mô hình sẽ nhanh hơn ~3–5 lần mỗi cặp.
- Hệ quả trực tiếp cho thời gian/bộ hồ sơ trên laptop (fp32, chưa tối ưu): embedding 300 trang bằng bge-m3 ≈ **10 phút** (khớp 300 ÷ 0,49 = 612 s); rerank 7.500 cặp chunk bằng bge-reranker-v2-m3 ≈ **1,6 giờ**; rerank theo trang ≈ **5 giờ**. Đây là lý do T0 phải đổi mô hình/giảm ứng viên (§4, §5).

---

## 2. FPT AI Marketplace: giá, tín dụng miễn phí, giới hạn, điều khoản dữ liệu

### 2.1 Nguồn giá

Trang `marketplace.fptcloud.com` là ứng dụng Next.js; mã JS gọi `https://marketplace-api.fptcloud.com/api/v2/portal/models` — API công khai, không cần khoá. Tôi đọc lúc 05/10/2026 ~15:11 UTC: 32 mô hình; bộ lọc "host" cho 17 mô hình "By FPT" và 14 "By Partner"; bộ lọc "data residency" có **JP** và **VN** [R1]. Mỗi bản ghi có `pricing` (`currency: USD`, `input_price_per_1m`, `output_price_per_1m`, `cached_price_per_1m`), `region`, `max_requests_per_minute_per_api_key`, `max_tokens_per_minute_per_api_key`, `capabilities` (ngữ cảnh, `supports_json_schema`…). Công thức tính tiền trong tài liệu FPT: `token vào × giá vào/1M + token ra × giá ra/1M`, tối thiểu 1 token, trừ tiền mỗi 5 phút [R2].

### 2.2 Bảng giá các mô hình trong tài khoản của nhóm (USD / 1M token, đọc 05/10/2026) [R1]

| Mô hình (tên trong catalog) | Host / vùng dữ liệu | Vào | Ra | Cached | Ngữ cảnh / ra tối đa | RPM / TPM mỗi khoá | JSON schema |
|---|---|---:|---:|---:|---|---|---|
| GLM-5.2 (`fci-glm-5-2`) | FPT / **VN** | 1,40 | 4,40 | 0,26 | 1.000.000 / 128.000 | 150 / 2.000.000 | có |
| DeepSeek-V4-Flash | FPT / **JP** | 0,14 | 0,28 | 0,018 | 500.000 / 200.000 | 50 / 500.000 | có |
| gpt-oss-120b | FPT / VN | 0,143 | 0,605 | 0,03 | 65.000 / 65.000 | 50 / 500.000 | có |
| gpt-oss-20b | — | — | — | — | **không có trong catalog công khai** [UNVERIFIED giá] | — | — |
| Llama-3.3-70B-Instruct | FPT / VN | 0,209 | 0,451 | 0,15 | 32.000 / 32.000 | 50 / 500.000 | có |
| Qwen3.6-27B | FPT / **JP** | 0,30 | 3,25 | 0,15 | 262.000 / 262.000 | 50 / 500.000 | có |
| gemma-4-31B-it | FPT / VN | 0,15 | 0,45 | 0,09 | 262.000 / 262.000 | 50 / 500.000 | có |
| gemma-4-26B-A4B-it | FPT / VN | 0,14 | 0,40 | 0,05 | 262.000 / 262.000 | 50 / 500.000 | có |
| gemma-3-27b-it | FPT / VN | 0,11 | 0,165 | — | 128.000 / 128.000 | 50 / 500.000 | có |
| Qwen2.5-VL-7B-Instruct (vision) | FPT / VN | 0,77 | 0,77 | — | 33.000 / 33.000 | 50 / 500.000 | có |

Đáng chú ý trong catalog nhưng chưa có trong danh sách của nhóm: **Saola-Small-32B** (mô hình tiếng Việt của FPT, nhấn mạnh tài chính, luật; VN; $0,132/$0,154; 32k; **không** hỗ trợ JSON schema) và các mô hình Partner "Topup credit only/restricted" như Z.ai:GLM-5.3-Flash ($0,15/$0,50), Azure:gpt-4.1-nano ($0,10/$0,40), Azure:gpt-5.6-luna ($0,20/$1,20), Google:Gemini-3.5-Flash ($1,5/$9). GLM-5.2 có **hai bản**: `GLM-5.2` (FPT host, public, 150 RPM/khoá) và `Z.ai:GLM-5.2` (Partner, restricted) — nên gọi `GET /v1/models` để chắc khoá của nhóm đang dùng bản FPT host.

### 2.3 Embedding và rerank (đọc 05/10/2026) [R1]

| Mô hình | Giá | Ngữ cảnh | Ghi chú |
|---|---:|---|---|
| Vietnamese_Embedding (AITeamVN) | $0,011 / 1M token | 8.000 (model card: huấn luyện với độ dài tối đa 2.048) | tinh chỉnh từ BGE-M3 trên ~300k bộ ba truy vấn–dương–âm tiếng Việt; trang FPT ghi giấy phép **CC-BY-NC-4.0**, model card gốc trên Hugging Face ghi **Apache-2.0** [R55] → mâu thuẫn, cần hỏi; bảng điểm trên trang: Acc@1 0,7274 / MRR@10 0,8181 so với BGE-M3 0,5682 / 0,6822 (model card gốc: đo trên tập *train* Zalo Legal 2021 [R55]) |
| multilingual-e5-large | $0,022 / 1M | 512 | |
| bge-reranker-v2-m3 | $0,022 / 1M | **512** | cặp (tuyên bố + đoạn) dài hơn 512 token sẽ bị cắt |

Chi phí một bộ hồ sơ: embedding ~0,19M token → **$0,002**; rerank 7.500 cặp × ~220 token ≈ 1,65M token → **≈ $0,036** [ƯỚC TÍNH]. Không đáng kể; đáng kể là tốc độ: FPT 77,7 trang/s so với laptop 0,49 trang/s [ĐO].

### 2.4 Tín dụng miễn phí

- **Starter Plan** (điều khoản trong tài liệu FPT AI Factory): ưu đãi **một lần** cho người dùng mới ở site Việt Nam (ai.fptcloud.com, không áp dụng site Nhật). Phải thêm phương thức thanh toán và nạp **$5** xác minh → nhận **$100 tín dụng khuyến mãi, hạn 30 ngày**, chia cố định: GPU VM $15, GPU Container $15, **Token Factory (suy luận) $70**; không chuyển nhượng, không hoàn tiền; FPT có quyền thay đổi bất cứ lúc nào [R4].
- **Giới thiệu bạn bè:** người giới thiệu nhận $25; người được giới thiệu nhận thêm 30% giá trị nạp (tối đa $150) trong 30 ngày đầu [R4].
- Mã giao diện marketplace còn các chuỗi "Start with 3M free tokens…" và "Your $1 trial credit… up to 100M free tokens" — chỉ là chuỗi trong mã, **không chắc còn hiệu lực** [UNVERIFIED].
- Quy đổi: $70 Token Factory đủ cho ~25–175 bộ hồ sơ theo mức chi phí ở §5 [ƯỚC TÍNH].

### 2.5 Giới hạn tốc độ

- Trường trong catalog (mỗi khoá API): GLM-5.2 **150 RPM / 2M TPM**; phần lớn mô hình mở do FPT host (gemma, gpt-oss, Llama, DeepSeek-V4-Flash, Qwen3.6-27B, Qwen2.5-VL) **50 RPM / 500k TPM**; các mô hình Partner 150–15.000 RPM [R1].
- Ghi chú trên trang từng mô hình: bảng "User Type — Default: TPM 100.000, RPM 50; Enterprise: Contact Sales" và "nếu yêu cầu không xong trong 5 phút, máy chủ có thể đóng kết nối" [R1].
- Nhóm đo được 710 lời gọi/451 s = **~94 yêu cầu/phút** với GLM-5.2 [ĐO] → khoá đang chạy theo giới hạn riêng của mô hình (150), không phải mức "Default 50" [suy luận].
- Hệ quả: với mô hình 50 RPM, 700 cặp mất **≥14 phút/khoá** nếu mỗi cặp một lời gọi. Cách gỡ: gộp 4–5 cặp/lời gọi (schema mảng) — chỉ bật sau khi gold chứng minh không giảm độ đúng (rủi ro "lây" giữa các cặp trong cùng prompt).
- Giao diện có trường "Rate limit per hour" khi tạo khoá → dùng làm trần chi tiêu.

### 2.6 Dữ liệu, vùng xử lý, giấy phép — những gì FPT nói (và không nói)

- **Serverless (gói nhóm đang dùng):** "không hỗ trợ chọn vùng xử lý thủ công"; "tự động phân phối yêu cầu giữa vùng Việt Nam và Nhật Bản"; "Prioritizes availability. **Data may be processed in another region during peak times**"; khuyến nghị cho khách "chấp nhận xử lý dữ liệu ở nước ngoài ngắn hạn" [R3].
- **Dedicated Inference:** "Fixed Region… **Guarantees data never leaves the selected Region**", khuyến nghị cho chính phủ, ngân hàng [R3]. Giá Dedicated: không tìm thấy công khai [UNVERIFIED].
- FAQ "Why are requests routed to Japan?": hệ thống Hybrid Routing chuyển sang JP khi cụm VN quá tải hoặc mạng chậm [R3].
- **Privacy Statement (factory.fpt.ai):** bên kiểm soát là FPT Smart Cloud; viện dẫn NĐ 13/2023/NĐ-CP và Luật Dữ liệu 60/2024/QH15, nói đáp ứng GDPR; "xử lý dữ liệu cá nhân trong một năm, lưu 2 năm hoặc theo luật"; có thể chia sẻ trong tập đoàn và với đối tác/nhà cung cấp có ràng buộc hợp đồng. **Văn bản không nói prompt/kết quả suy luận có được ghi log, lưu bao lâu, hay dùng để huấn luyện hay không** [R5]. Terms of Use chỉ là điều khoản website, luật áp dụng là luật Việt Nam [R5].
- **Lỗi trên trang FPT cần biết:** trang gpt-oss-120b ghi giấy phép "Together Computer Research License, non-commercial" — trái với model card chính thức của OpenAI (**Apache 2.0**) [R1, R30]. Dựa vào nguồn gốc, không dựa vào trang bán lại.

### 2.7 Vòng đời mô hình trên FPT: thay đổi rất nhanh

Bảng "Model Deprecations" của FPT liệt kê hơn 30 mô hình đã tắt từ 07/2025 đến 07/2026, ví dụ **bge-m3 (19/03/2026)**, gte-multilingual-base, Qwen3-32B (06/07/2026), GLM-4.7 (22/06/2026), **GLM-5.1 (31/07/2026)**, các bản SaoLa cũ [R2]. Hệ quả cho GreenScan: (1) khoá cache phải chứa tên mô hình (đã có: `prompt_version@route`); (2) kiểm tra `/v1/models` lúc khởi động và báo rõ khi mô hình biến mất, đừng âm thầm chuyển; (3) đo gold lại mỗi khi đổi mô hình.

### 2.8 So sánh với API khác — mô hình rẻ nhất đủ dùng (chỉ trang giá chính thức, đọc 05/10/2026)

| Nhà cung cấp | Mô hình | Vào | Cached | Ra | Batch (vào/ra) | Dữ liệu |
|---|---|---:|---:|---:|---|---|
| Google Gemini API (trang cập nhật 01/10/2026) [R6] | gemini-2.5-flash-lite | 0,10 | 0,01 | 0,40 | 0,05 / 0,20 | gói Free: "Used to improve our products: **Yes**"; gói trả tiền: **No** |
| | gemini-3.1-flash-lite | 0,25 | 0,025 | 1,50 | 0,125 / 0,75 | như trên |
| | gemini-3.5-flash-lite | 0,30 | 0,03 | 2,50 | 0,15 / 1,25 | như trên |
| | gemini-embedding-2 (văn bản) | 0,20 | — | — | 0,10 | như trên |
| OpenAI [R7] | gpt-5-nano | 0,05 | 0,005 | 0,40 | 0,025 / 0,20 | API không dùng để huấn luyện mặc định; log chống lạm dụng tối đa 30 ngày; có Zero Data Retention; vùng lưu trú gồm Nhật, Singapore, Ấn Độ, Hàn (không có Việt Nam), +10% với mô hình ra mắt từ 05/03/2026 [R8] |
| | gpt-6-luna | 0,10 | 0,01 | 0,50 | 0,05 / 0,25 | như trên |
| | gpt-5-mini | 0,25 | 0,025 | 2,00 | 0,125 / 1,00 | như trên |
| | text-embedding-3-small | 0,02 | — | — | — | |
| Anthropic [R9] | Claude Haiku 4.5 | 1,00 | 0,10 | 5,00 | 0,50 / 2,50 | "Anthropic may not train models on Customer Content from Services" (Commercial Terms, hiệu lực 17/06/2025) [R9] |

Nhận xét: (1) về giá token, gpt-5-nano, gemini-2.5-flash-lite, gpt-6-luna ngang hoặc rẻ hơn gemma-4 trên FPT; Claude Haiku 4.5 đắt ~7 lần gemma-4. (2) Giá/token **không so 1:1** được vì tokenizer khác nhau với tiếng Việt (ở trên: Qwen3 2,82 ký tự/token, XLM-R 3,58). (3) Cả ba đều xử lý ngoài Việt Nam → chỉ dùng cho tài liệu công khai, và **tuyệt đối không dùng gói Free của Gemini** cho tài liệu người dùng tải lên. (4) Chất lượng tiếng Việt phải đo trên gold; bảng xếp hạng VMLU công khai chỉ cập nhật đến 03/2025, không có các mô hình hiện tại [R39].

---

## 3. Nguyên tắc định tuyến mô hình — có cơ sở nghiên cứu

### 3.1 FrugalGPT — chuỗi mô hình + xấp xỉ + cache
Chen, Zaharia, Zou (2023) đề xuất ba chiến lược giảm chi phí: điều chỉnh prompt, xấp xỉ LLM (cache, mô hình nhỏ tinh chỉnh) và **chuỗi LLM (cascade)**; báo cáo "có thể khớp hiệu năng LLM tốt nhất (GPT-4) với **giảm tới 98% chi phí**, hoặc tăng độ đúng 4% với cùng chi phí" [R10].

### 3.2 RouteLLM — bộ định tuyến học từ dữ liệu ưa thích
Ong và cs. (2024): router chọn giữa mô hình mạnh/yếu cho từng truy vấn, "giảm chi phí **hơn 2 lần** trong một số trường hợp mà không giảm chất lượng" [R11]. Bài blog LMSYS: giảm chi phí **>85% trên MT Bench, 45% MMLU, 35% GSM8K** so với chỉ dùng GPT-4 mà vẫn đạt 95% hiệu năng GPT-4; router matrix factorization chỉ cần 14% lời gọi GPT-4 trên MT Bench [R12]. Bài học: router đơn giản (BERT classifier, matrix factorization) đủ tốt **nếu có dữ liệu nhãn của chính miền**.

### 3.3 Thác (cascade) leo thang theo độ tin cậy
- Yue và cs. (ICLR 2024): mô hình yếu trả lời trước; đo **độ nhất quán** giữa nhiều lần trả lời; không nhất quán mới chuyển mô hình mạnh → hiệu năng ngang mô hình mạnh với **40% chi phí** [R13].
- AutoMix (NeurIPS 2024): mô hình nhỏ **tự kiểm chứng** (few-shot), router POMDP quyết định có chuyển lên không → giảm **>50%** chi phí với hiệu năng tương đương [R14].
- Gupta và cs. (2024): luật trì hoãn (deferral) dựa trên **độ bất định mức token** học được tốt hơn hẳn lấy trung bình đơn giản [R16].
- Dekoninck, Baader, Vechev (2024/2025): "cascade routing" hợp nhất routing và cascading; **bộ ước lượng chất lượng tốt là yếu tố quyết định** [R17].
- Ding và cs. (ICLR 2024, Hybrid LLM): ít hơn **40%** lời gọi mô hình lớn mà không giảm chất lượng [R18].
- Nie và cs. (ICML 2024, Online Cascade Learning): thác từ hồi quy logistic → mô hình nhỏ → LLM, mô hình nhỏ học dần theo đầu ra LLM; "ngang LLM về độ đúng, **giảm tới 90% chi phí suy luận**" [R19].

### 3.4 Mô hình nhỏ tinh chỉnh vẫn thắng LLM zero-shot ở bài toán phân loại
- Bucher & Martini (2024): "các LLM 'nhỏ' tinh chỉnh **nhất quán và đáng kể** vượt mô hình lớn prompt zero-shot (GPT-3.5, GPT-4, Claude Opus) trong phân loại văn bản" [R23].
- Edwards & Camacho-Collados (LREC-COLING 2024), 16 tập dữ liệu: "tinh chỉnh mô hình nhỏ hơn vẫn có thể vượt few-shot của LLM lớn" [R24].
- **MiniCheck** (Tang, Laban, Durrett; EMNLP 2024): kiểm chứng câu với tài liệu gốc; MiniCheck-FT5 (770M) "đạt độ đúng GPT-4", "rẻ hơn **400 lần**" [R15]. **AlignScore** (ACL 2023): 355M tham số "ngang hoặc vượt" thước đo dựa trên ChatGPT/GPT-4 về nhất quán sự thật [R25].
- Distilling step-by-step (Findings ACL 2023): T5 770M tinh chỉnh **vượt PaLM 540B** few-shot, chỉ dùng 80% dữ liệu [R26].
- Lưu ý: các kết quả này chủ yếu là tiếng Anh; miền "tuyên bố môi trường tiếng Việt có số liệu/bảng" **chưa ai đo** → phải đo trên gold của nhóm.

### 3.5 Đầu ra có cấu trúc (JSON schema/giải mã ràng buộc) và cỡ mô hình
- Tam và cs. (2024): ép định dạng (JSON/XML) làm **giảm đáng kể khả năng suy luận**, ràng buộc càng chặt càng giảm [R28].
- StructuredRAG (2024): 24 thí nghiệm, tỷ lệ JSON hợp lệ **trung bình 82,55%**, dao động **0–100%**; Llama 3 8B thường ngang Gemini 1.5 Pro; đầu ra dạng danh sách/đối tượng lồng khó hơn [R29].
- JSONSchemaBench (2025): 10k schema thực tế, so Guidance, Outlines, llama.cpp, XGrammar, OpenAI, Gemini về độ phủ, hiệu năng, chất lượng [R31].
- Geng và cs. (EMNLP 2023): giải mã ràng buộc ngữ pháp giúp LM "vượt LM không ràng buộc và **thậm chí mô hình tinh chỉnh chuyên biệt**" ở trích xuất thông tin [R32]. XGrammar (MLSys 2025): nhanh tới 100 lần, chi phí gần bằng 0 [R33].
- Công cụ: vLLM nhận `response_format: {"type":"json_schema",…}` (backend xgrammar/guidance/outlines) [R34]; Ollama nhận JSON schema ở trường `format`, khuyên nhiệt độ 0 và đưa schema vào prompt [R35]; catalog FPT ghi `supports_json_schema: true` cho mọi LLM trong tài khoản (trừ Saola) [R1].
- **Hiện trạng repo:** `local_openai.py` chỉ **nối schema vào cuối prompt** rồi bắt JSON bằng regex, không dùng `response_format` → mô hình nhỏ dễ hỏng JSON. Đề xuất: dùng `response_format` khi nhà cung cấp hỗ trợ, giữ đường dự phòng hiện tại, ghi tỷ lệ JSON hỏng thành chỉ số.

### 3.6 Bộ nhớ đệm (cache)
- FrugalGPT coi cache là một dạng "xấp xỉ LLM" [R10]; GPTCache (NLP-OSS 2023) là cache **ngữ nghĩa** mã nguồn mở [R36].
- Với kiểm chứng, **cache ngữ nghĩa nguy hiểm**: hai tuyên bố chỉ khác năm hoặc con số sẽ "trúng cache" sai. Repo đang làm đúng: cache **khớp chính xác** theo sha256(prompt_version, route, claim, evidence); chạy lại HPG 0 lời gọi, 188 s thay vì 632 s [ĐO].
- Cache tiền tố phía nhà cung cấp: OpenAI cần ≥1.024 token, giảm giá tới 95%, giữ ~30 phút [R37]; FPT có giá "cached" (GLM-5.2 $0,26 so với $1,40) nhưng không công bố điều kiện kích hoạt [UNVERIFIED]. Prompt stance chỉ ~550 token nên lợi ích nhỏ, trừ khi gộp nhiều cặp vào một prompt có phần hướng dẫn chung đặt ở đầu.

### 3.7 Tám quy tắc rút ra cho GreenScan
1. **R1 — Tất định trước:** số học, đơn vị, năm gốc, phạm vi = Python (đã làm); LLM không phân xử số.
2. **R2 — Mô hình rẻ nhất vượt ngưỡng gold đăng ký trước** cho từng việc; ngưỡng ghi vào `configs/measurement_decisions.yaml` trước khi đo.
3. **R3 — Thác theo độ tin cậy:** luật → NLI/cross-encoder → LLM vừa → GLM-5.2 → người; chỉ leo thang khi điểm thấp, khi hai tầng bất đồng, hoặc khi nghi mâu thuẫn.
4. **R4 — Chưng cất:** lưu (tuyên bố, đoạn, nhãn LLM, nhãn người) của **tài liệu công khai** để tinh chỉnh một cross-encoder tiếng Việt; hiện cache chỉ lưu khoá băm nên chưa dùng được để huấn luyện.
5. **R5 — JSON schema/giải mã ràng buộc cho mọi việc có cấu trúc**; kiểm tra hợp lệ; thử lại 1 lần; ghi lỗi, không im lặng.
6. **R6 — Cache khớp chính xác, có phiên bản;** không dùng cache ngữ nghĩa cho kết luận.
7. **R7 — Gộp nhiều cặp/lời gọi** chỉ khi bị giới hạn RPM và gold chứng minh không giảm độ đúng.
8. **R8 — Định tuyến theo loại dữ liệu:** tài liệu mật → tại chỗ/T2 hoặc Dedicated VN; tài liệu công khai → Serverless được; mô hình vùng JP/Partner chỉ cho dữ liệu công khai.

---

## 4. Tăng tốc trên CPU cho đúng chiếc laptop này

### 4.1 ONNX Runtime / OpenVINO (encoder: embedding, reranker, NLI)

- Sentence-Transformers hỗ trợ `SentenceTransformer(..., backend="onnx" | "openvino")` và `CrossEncoder(..., backend="onnx" | "openvino")`; có hàm `export_optimized_onnx_model` (O1–O4), `export_dynamic_quantized_onnx_model` (int8 ONNX, không cần dữ liệu hiệu chỉnh) và `export_static_quantized_openvino_model` (int8 OpenVINO, cần dữ liệu hiệu chỉnh) [R20, R21].
- **Số liệu tốc độ có nguồn:**
  - Ghi chú phát hành v3.2.0 (10/10/2024): "trên CPU có thể kỳ vọng **~2,5 lần nhanh hơn** với cái giá **0,4% độ đúng**" (trung bình 4 mô hình, 3 tập dữ liệu, nhiều batch size) [R21].
  - v3.3.0 (11/11/2024): "**4x speedup for CPU** với OpenVINO int8 static quantization", "vượt mọi backend khác" với tổn thất nhỏ [R22].
  - Tài liệu (bản v3.3–v5.0): với văn bản ngắn (stsb), ONNX 1,39x, OpenVINO 1,29x, **ONNX int8 3,08x**; "với văn bản dài hơn, ONNX và OpenVINO **có thể còn chậm hơn PyTorch một chút**"; sơ đồ khuyến nghị: CPU + chấp nhận mất 0,4% → `openvino-qint8`; không chấp nhận → CPU Intel dùng `openvino` [R21].
  - Tài liệu hiện hành (2026): đo trên **i7-13700K** (cùng thế hệ Raptor Lake với i7-1355U) — "OpenVINO INT8 tốt nhất trên máy này", nhưng llama.cpp dẫn trên máy cloud; "hãy đo trên phần cứng triển khai" [R20].
  - Với CrossEncoder trên CPU, **không dùng fp16/bf16 của PyTorch: chỉ ~0,17x** tốc độ fp32 [R20].
  - Intel (Xeon 8480+ có AMX): INT8 tăng tới 4,5x độ trễ, 4x thông lượng so với BF16, mất <1% (rerank) và <1,55% (retrieval) trên MTEB [R38] — **không áp dụng thẳng** cho i7-1355U (không AMX), nhưng cho thấy int8 giữ chất lượng tốt.
- **Áp vào máy này [ƯỚC TÍNH]:** bge-m3 300 trang: fp32 ~10 phút → int8 ~3–4 phút. bge-m3 ONNX fp32 đã có sẵn trong repo chính thức (`onnx/model.onnx` + `model.onnx_data` 2,27 GB — đang nằm trong cache HF của máy từ 29/09) [ĐO]; int8 sẽ ~0,6 GB.
- **Iris Xe:** OpenVINO và llama.cpp đều có bản cho GPU Intel (llama.cpp b11425 ngày 05/10/2026 có bản Windows `sycl-x64`, `vulkan-x64`, `openvino-2026.4.1-x64`) [R27]. Tôi **không tìm được số đo đáng tin** cho encoder kiểu BERT trên Iris Xe [UNVERIFIED]; iGPU dùng chung băng thông DDR4 với CPU. Đáng thử 30 phút bằng `benchmark_app -d GPU` so với `-d CPU`, không nên lập kế hoạch dựa trên nó.
- **Đòn bẩy không cần đổi mô hình:** sắp xếp đoạn theo độ dài + padding động; batch 16–32; `max_length` 512 cho chunk (đa số <250 token); cắm sạc + chế độ "Best performance" của Windows (chip U 15 W bị hạ xung mạnh khi dùng pin) [khuyến nghị chung].

### 4.2 Mô hình embedding/reranker nhỏ hơn có số liệu tiếng Việt

**Nguồn (đọc 05/10/2026):** VN-MTEB — Pham, Luu, Vo, Nguyen, Hoang (GreenNode AI & HCMIU), arXiv:2507.21500 (29/07/2025), cùng nội dung ở Findings of EACL 2026, tr. 1705–1725: **41 tập dữ liệu, 6 loại tác vụ** (Retrieval 15, Classification 12, Pair classification 3, Clustering 5, Reranking 3, STS 3), 18 mô hình. Dữ liệu là MTEB tiếng Anh **dịch máy bằng LLM rồi lọc** — văn bản dịch, không phải tiếng Việt gốc [R53]. Bổ sung bằng kết quả chính thức của MTEB (repo `embeddings-benchmark/results`, nDCG@10) cho các tác vụ tiếng Việt gốc [R54], và model card Hugging Face [R55].

**Bảng A — VN-MTEB (Bảng 3 của bài báo), mô hình ≤ 600M tham số** [R53, R55]

| Mô hình | Tham số / chiều | Retrieval | TB 6 loại | Giấy phép (HF) | Cần tách từ? |
|---|---|---:|---:|---|---|
| multilingual-e5-large-instruct | 560M / 1024 | 40,88 | **67,99** | MIT | Không |
| gte-multilingual-base | 305M / 768 | 38,38 | 65,22 | Apache-2.0 (cần `trust_remote_code`) | Không |
| bge-m3 | 568M / 1024 | 39,84 | 64,90 | MIT | Không |
| multilingual-e5-large | 560M / 1024 | 37,65 | 63,87 | MIT | Không |
| AITeamVN/Vietnamese_Embedding | 568M / 1024 | 34,18 | 63,34 | Apache-2.0 (FPT ghi CC-BY-NC-4.0) | Không |
| multilingual-e5-base | 278M / 768 | 34,50 | 62,42 | MIT | Không |
| halong_embedding | 278M / 768 | 34,45 | 61,60 | Apache-2.0 | Không |
| multilingual-e5-small | 118M / 384 | 34,12 | 60,66 | MIT | Không |
| bkai vietnamese-bi-encoder | 135M / 768 | 25,37 | 54,89 | Apache-2.0 | **Có** (PhoBERT); bài báo không nói có tách từ khi chấm → có thể bị chấm thấp [UNVERIFIED] |

Điểm retrieval tốt nhất trong 18 mô hình là gte-Qwen2-7B-instruct 46,05 (quá lớn cho laptop). Hai tập gần miền GreenScan nhất (nDCG@10, Bảng 16 VN-MTEB): **ClimateFEVER-VN** — e5-large-instruct 25,01; bge-m3 21,27; gte-base 21,05; e5-large 15,43; e5-small 15,13; AITeamVN 13,25; e5-base 12,62. **FiQA2018-VN** (tài chính) — e5-large-instruct 36,46; bge-m3 34,38; gte-base 32,88; AITeamVN 29,94; e5-small 22,71 [R53].

**Bảng B — tác vụ tiếng Việt gốc trong kết quả MTEB chính thức (nDCG@10 × 100)** [R54]

| Mô hình | Belebele vie | MLQA vie (test) | VieQuAD | GreenNodeTable (bảng tài chính dạng markdown) |
|---|---:|---:|---:|---:|
| multilingual-e5-small | 90,86 | 63,29 | 55,27 | 39,20 |
| multilingual-e5-base | 93,52 | 66,71 | 57,65 | 38,89 |
| multilingual-e5-large | **95,49** | **70,37** | **61,12** | 42,63 |
| multilingual-e5-large-instruct | 94,21 | 68,36 | 55,36 | 39,87 |
| bge-m3 | 93,24 | 67,84 | 56,84 | 40,37 |
| Qwen3-Embedding-0.6B | 92,96 | 64,55 | – | – |
| embeddinggemma-300m | 93,91 | 66,83 | – | – |
| jina-embeddings-v3 | 93,26 | 63,10 | – | – |
| AITeamVN v1 / halong / bkai | – | – | 55,64 / 52,01 / 43,47 | 39,72 / 35,97 / 15,62 |
| GreenNode-Large-VN-V1 / Mixed-V1 | – | – | 55,41 / 56,89 | **46,69 / 46,21** |

Lưu ý: các lần chạy dùng mteb 1.12–2.4; GreenNode được huấn luyện trên chính bộ GreenNode-Table nên có lợi thế trong miền. Kết quả luật Zalo trên model card mỗi nơi đo một kiểu (AITeamVN đo trên **tập train** Zalo Legal 2021: MRR@10 Vietnamese_Embedding 0,8181; bkai 0,7951; bge-m3 0,6822 [R55]); bkai được huấn luyện trên 80% tập train Zalo nên số của nó trong các bảng này có thể bị thổi phồng (suy luận). Jina-embeddings-v3 (CC-BY-NC-4.0), Qwen3-Embedding-0.6B, embeddinggemma-300m **không có trong VN-MTEB**.

**Bảng C — reranker có bằng chứng tiếng Việt** [R55, R56, R57]

| Mô hình | Tham số | Giấy phép | Độ dài tối đa | Tách từ? | Bằng chứng tiếng Việt |
|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 | 568M | Apache-2.0 | 8.194 vị trí | Không | mMARCO-vi: NDCG@10 0,6872; MRR@10 0,6209 |
| namdp-ptit/ViRanker (xây trên BGE-M3) | 568M | Apache-2.0 | 512 (ví dụ trong card) | Không | mMARCO-vi: NDCG@10 0,7302; MRR@10 **0,7107** |
| itdainb/PhoRanker | 135M | Apache-2.0 | 256 | **Có** (VnCoreNLP) | mMARCO-vi: NDCG@10 **0,7422**; MRR@10 0,6830; A100 fp16: 15 tài liệu/s so với 3,51 của bge-reranker-v2-m3 |
| AITeamVN/Vietnamese_Reranker | 568M | Apache-2.0 | 2.304 | Không | Zalo Legal 2021 (tập train): Acc@1 0,7944; MRR@10 0,8672 |
| Alibaba-NLP/gte-multilingual-reranker-base | 306M | Apache-2.0 | 8.192 | Không | MKQA, truy vấn tiếng Việt → đoạn tiếng Anh: Recall@20 70,3 (bài mGTE, arXiv:2407.19669, Bảng 19) |
| jinaai/jina-reranker-v2-base-multilingual | 278M | **CC-BY-NC-4.0** | 1.024 | Không | không có số riêng cho tiếng Việt |
| Qwen/Qwen3-Reranker-0.6B | 596M | Apache-2.0 | 32k | Không | không có số riêng cho tiếng Việt (MMTEB-R 66,36) |

mMARCO-vi cũng là bản **dịch máy**; card ghi "Dev", bài ViRanker (arXiv:2509.09131) ghi "test" — cùng con số [R56].

**Bản ONNX/OpenVINO có sẵn trên Hugging Face (05/10/2026)** [R55]: e5-small/base/large có ONNX chính thức (fp32, O4, `qint8_avx512_vnni`) và OpenVINO fp32 — bản qint8 chính thức nhắm AVX-512 nên trên máy này nên tự lượng tử hoá lại với cấu hình `avx2` hoặc dùng OpenVINO int8; bge-m3 và Vietnamese_Embedding có ONNX chính thức; Qwen3-Embedding-0.6B và Qwen3-Reranker-0.6B có bản OpenVINO int8 (tổ chức OpenVINO); bge-reranker-v2-m3 và gte reranker có ONNX cộng đồng; **PhoRanker, ViRanker, Vietnamese_Reranker chưa có ONNX/OpenVINO** — phải tự xuất.

**Tốc độ:** không mô hình nào ở trên công bố độ trễ trên CPU laptop. Số tham chiếu duy nhất là biểu đồ CPU trong tài liệu Sentence-Transformers (i7-13700K, trung vị qua các mô hình/tập dữ liệu, so với PyTorch fp32): **openvino-qint8 2,84x (giữ 99,37% chất lượng)**, onnx-qint8 1,92x (99,58%), llama.cpp Q4_K_M 1,23x, OpenVINO fp32 1,06x, ONNX fp32 0,90x, torch fp16/bf16 chỉ 0,25x/0,28x [R20]. Khối lượng tính trên mỗi token, so với bge-m3 [ƯỚC TÍNH theo số tham số không tính bảng embedding]: e5-small ≈ 1/14; e5-base, gte-base, PhoBERT, mDeBERTa ≈ 1/3,5; **Qwen3-Embedding-0.6B ≈ 1,45 lần** (bộ giải mã ~0,44B tham số không tính embedding) → "0.6B" **không** rẻ hơn bge-m3 trên CPU.

**Kết luận cho GreenScan**
1. T0 mặc định: **multilingual-e5-small** (8 GB) hoặc **e5-base**; máy 16 GB: **bge-m3 int8** hoặc e5-large. Trên VN-MTEB, e5-small kém bge-m3 5,7 điểm retrieval (34,12 so với 39,84) nhưng tốn ~1/14 phép tính. gte-multilingual-base là mô hình ≤ 305M mạnh nhất (65,22) nhưng chỉ có ONNX cộng đồng và cần `trust_remote_code`.
2. Các bản tinh chỉnh tiếng Việt (AITeamVN, halong, GreenNode) **không vượt mô hình gốc trên VN-MTEB** (dữ liệu dịch), nhưng thắng ở văn bản luật tiếng Việt, và GreenNode thắng ở bảng tài chính → đáng thử cho bảng trong BCTN. Nhóm đang dùng Vietnamese_Embedding qua FPT: cần A/B với bge-m3 trên gold, vì ở ClimateFEVER-VN nó chỉ đạt 13,25 so với 21,27.
3. Reranker: ViRanker (không cần tách từ, MRR@10 0,7107 so với 0,6209 của bge-reranker-v2-m3 trên mMARCO-vi) và PhoRanker (nhỏ hơn 4 lần, NDCG@10 0,7422, nhưng cần VnCoreNLP và chỉ 256 token) đều vượt bge-reranker-v2-m3; trên CPU, PhoRanker rẻ nhất (~1/3,5 phép tính) nếu chấp nhận bước tách từ.
4. Tránh vì giấy phép phi thương mại: jina-embeddings-v3, jina-reranker-v2/v3.
5. Backend: OpenVINO hoặc ONNX int8; không chạy fp16 trên CPU.

### 4.3 LLM nhỏ chạy tại chỗ (llama.cpp / Ollama)

- **Vật lý:** giải mã (decode) bị giới hạn bởi băng thông RAM: tok/s ≈ băng thông hiệu dụng ÷ dung lượng trọng số. Nhóm đo qwen3:8b (Q4_K_M ~5 GB) **4,3 tok/s** [ĐO] → băng thông hiệu dụng ~22 GB/s (≈43% của 51,2 GB/s). Pha nạp prompt (prefill) bị giới hạn bởi tính toán.
- **Số đo tham chiếu (máy yếu hơn, cùng cách đo):** It's FOSS (15/05/2026), laptop Intel i5 + UHD 620, 12 GB RAM, Ollama, Q4_K_M: **Qwen3 0.6B 34–36 tok/s; Gemma 3 1B 18,6; Gemma 4 E2B 9,9; Granite 4 3B 8,5–9; Phi-4-mini 3.8B 6,9; mô hình 7B 4,1–4,3; Ministral 3 8B 3,16** [R41]. Mô hình 7B ở đó ra đúng 4,3 tok/s như qwen3:8b trên máy nhóm → bảng này là ước lượng sát cho i7-1355U.
- **Ứng viên 2026 (mã nguồn mở, Apache 2.0):**

| Mô hình | Tham số | Điểm đa ngữ công bố | Ghi chú |
|---|---|---|---|
| Qwen3.5-0.8B / 2B / 4B / 9B (ra 02–03/2026) | 0,8 / 2 / 4 / 9B | MMMLU: 2B 56,9; 4B 76,1; 9B 81,2 · MMLU-ProX (29 ngôn ngữ, **có tiếng Việt**): 2B 52,3; 4B 71,5; 9B 76,3 | đa phương thức (ảnh+chữ), 262k ngữ cảnh, 201 ngôn ngữ; 4B **mặc định bật thinking** — tắt bằng `enable_thinking: False`; 2B "dễ rơi vào vòng lặp thinking" [R42–R44] |
| Gemma 4 E2B / E4B / 12B / 26B-A4B / 31B (02/04/2026) | E2B 2,3B hiệu dụng (5,1B kể embedding); E4B 4,5B (8B); 26B-A4B: 25,2B tổng, 3,8B kích hoạt | MMMLU: E2B 67,4; E4B 76,6; 12B 83,4; 26B-A4B 86,3; 31B 88,4 | 128k (nhỏ) / 256k (lớn); >140 ngôn ngữ [R45] |

  Lưu ý: **MMMLU không có tiếng Việt** (14 ngôn ngữ) [R46]; MMLU-ProX có tiếng Việt nhưng điểm là trung bình 29 ngôn ngữ [R47] → chỉ để sàng lọc, không thay gold.
- **Thời gian một lời gọi stance (~550 vào, ~80 ra, tắt thinking) [ƯỚC TÍNH]:** 4B ≈ 15–25 s; 2B ≈ 6–12 s; 0.8B ≈ 3–5 s. Với 700 cặp: 4B ≈ 3–5 giờ; 2B ≈ 1,2–2,3 giờ; 0.8B ≈ 35–60 phút. qwen3:8b đo 98 s/lời gọi (có thinking) [ĐO]. **Kết luận:** LLM tại chỗ trên laptop này chỉ hợp cho ≤30–50 cặp khó nhất (chạy nền) hoặc 1 đoạn tóm tắt; không thay được API/GPU cho 700 cặp.
- Bản Windows của llama.cpp có `llama-bench`; đo bằng chính prompt stance trước khi quyết.

### 4.4 Cross-encoder NLI đa ngữ làm bộ lọc lập trường rẻ trên CPU

| Mô hình | Cỡ | Giấy phép | XNLI tiếng Việt | Trung bình | Tốc độ công bố |
|---|---|---|---:|---:|---|
| MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 | ~0,3B (278M) | MIT | **0,793** | ~0,80 (15 ngôn ngữ; en 0,871) | A100: 877–1.887 văn bản/s; "mDeBERTa hiện không hỗ trợ FP16" [R48] |
| MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli | ~0,1B | MIT | 0,723 | 0,713 | A100: ~6.093 văn bản/s [R49] |

- Trên laptop [ƯỚC TÍNH theo FLOPs, §1.3]: mDeBERTa-base ≈ 3,5 lần ít phép tính hơn bge-m3/token → 700 cặp × ~250 token ≈ **3–4 phút fp32, ~1,5 phút int8**; MiniLM-L6 < 30 giây.
- Ánh xạ: entailment → ứng viên SUPPORTS; contradiction → ứng viên CONTRADICTS (**không bao giờ tự quyết**, chuyển LLM/người); neutral → CONTEXT/PARTIAL.
- Giới hạn: XNLI là cặp câu miền chung; dữ liệu huấn luyện 2,7M cặp do **dịch máy** (tác giả tự nêu là làm giảm chất lượng) [R48]; câu ESG có số liệu/bảng khác xa. Dùng làm **bộ lọc và sắp thứ tự**, không làm kết luận. Đường nâng cấp: tinh chỉnh mDeBERTa trên cặp do GLM-5.2 gắn nhãn + gold người (quy tắc R4).

---

## 5. Ba tầng phần cứng/triển khai

Giả định chung: một bộ = 300 trang (§1.2); phần không-LLM của pipeline (đọc PDF, OCR khi cần, luật, chấm điểm) ≈ 144 s × 300/264 ≈ **2,7 phút** trên laptop [suy từ ĐO].

### T0 — Laptop ngoại tuyến (không GPU, 8–16 GB RAM, không khoá API)

| Việc | Chọn | Thời gian/bộ [ƯỚC TÍNH] |
|---|---|---|
| Đọc PDF/OCR | text-layer; Tesseract `vie+eng` cho trang scan (đã cấu hình) | trong 2,7 phút nền |
| claim_extraction / normalization / query generation | **luật + từ điển (như hiện tại)**, không LLM | ~0 |
| Dense retrieval | 16 GB: bge-m3 **int8 OpenVINO/ONNX**; 8 GB: multilingual-e5-small/base int8 | 3–4 phút (bge-m3) / <1–1,5 phút (e5) |
| Rerank | không rerank, hoặc reranker cỡ base int8 trên **top-10** (không phải 30) | 0–4 phút |
| qualitative_stance | luật → **mDeBERTa NLI int8** → phần còn lại "PARTIAL + cần người xem" | 1,5–4 phút |
| LLM tại chỗ (tuỳ chọn) | Qwen3.5-4B hoặc Gemma 4 E4B Q4, tắt thinking, **chỉ ≤30 cặp khó** | +10–15 phút (chạy nền) |
| legal_reasoning | rule pack + người | ~0 |
| final_report | mẫu (template) tiếng Việt tất định; LLM chỉ đánh bóng đoạn tóm tắt (tuỳ chọn) | ~0 (+5–10 phút nếu dùng 4B) |
| document_vision | Tesseract `vie` | theo số trang scan |
| **Tổng** | | **~5–15 phút** (không LLM); **+10–25 phút** nếu bật LLM cho ít cặp |

- **RAM:** 8 GB đủ cho e5 + mDeBERTa (mỗi mô hình < 1,5 GB RAM), không LLM; 16 GB cho bge-m3 + reranker + LLM 4B Q4 (~3 GB).
- **Đĩa:** bge-m3 fp32 ~2,3 GB (int8 ~0,6 GB); mDeBERTa ~1,1 GB fp32 (~0,3 GB int8); e5-small ~0,5 GB; Qwen3.5-4B Q4 ~2,5–3 GB → tổng 4–7 GB.
- **Chi phí/bộ:** 0 đồng tiền API; điện năng không đáng kể.
- **Đánh đổi:** không có lập trường do LLM → nhiều câu "cần người xem" hơn; phải đo trên gold xem NLI mất bao nhiêu so với GLM-5.2.

### T1 — Laptop + API Việt Nam (FPT Serverless)

| Việc | Mô hình | Lời gọi/bộ | Chi phí/bộ [ƯỚC TÍNH] |
|---|---|---:|---:|
| claim_extraction | luật hiện tại; tuỳ chọn gemma-4-26B-A4B-it cho **chunk đã qua bộ lọc từ khoá**, gộp 8 chunk/lời gọi | 0–113 | $0–0,04 |
| claim_normalization | gemma-4-26B-A4B-it + JSON schema + kiểm tra tất định | ~250 | ~$0,02 |
| retrieval_query_generation | mẫu tất định; LLM chỉ khi tuyên bố không trúng từ khoá nào | 0–50 | <$0,01 |
| Dense + rerank | Vietnamese_Embedding + bge-reranker-v2-m3 (FPT) | 1 lô + 7.500 cặp | ~$0,04 |
| qualitative_stance | luật → NLI tại chỗ → **gemma-4-26B-A4B-it** → **GLM-5.2** cho cặp bất đồng/nghi mâu thuẫn → người | 700 (+ ~100–200 lên GLM) | chỉ gemma: $0,08–0,19; thác gemma + GLM cho 100–200 cặp: $0,19–0,76; tất cả qua GLM-5.2: **$0,79 (không suy luận) – $2,02 (~400 token suy luận/lời gọi)** |
| legal_reasoning | GLM-5.2 (VN, ngữ cảnh 1M); thử thách: Saola-Small-32B | ~40 | $0,21–0,47 |
| final_report | **gemma-4-31B-it hoặc GLM-5.2** (bỏ Llama-3.3-70B) | 1 | $0,007–0,064 |
| document_vision | Qwen2.5-VL-7B (VN) chỉ cho trang không có lớp chữ; đặt `max_pixels` (mỗi token ảnh = ô 28×28 px) [R50] | ~20 trang | ~$0,04 |
| **Tổng** | | | **≈ $0,4–0,9 (≈10–23k VND)** chỉ gemma cho lập trường; **≈ $0,5–1,4 (≈13–36k VND)** thác khuyến nghị; **≈ $1,1–2,7 (≈29–70k VND)** GLM-5.2 cho mọi cặp (như hiện nay) |

- **Thời gian:** 2,7 phút nền + embedding qua FPT ~4 s + rerank (chưa đo, ước 1–3 phút) + stance 700 cặp: **451 s với 8 luồng** [ĐO]; ở 150 RPM tối đa ~2,5 lời gọi/s → ~4,7 phút; mô hình 50 RPM → ≥14 phút trừ khi gộp cặp; pháp lý + báo cáo cuối ~1–3 phút → **tổng ~10–20 phút lần đầu (tới ~25 phút nếu mô hình 50 RPM không gộp cặp), ~3–4 phút khi chạy lại (cache)**.
- **RAM/đĩa:** 8 GB đủ; chỉ cần NLI tại chỗ (~1 GB).
- **Sửa ngay:** bỏ DeepSeek-V4-Flash và Qwen3.6-27B (vùng JP) khỏi các việc đụng tài liệu người dùng; thay bằng gemma-4-26B-A4B-it/gemma-4-31B-it (VN).

### T2 — Máy chủ 1 GPU 24 GB chạy vLLM (mô hình mở)

| Việc | Lựa chọn | Ghi chú |
|---|---|---|
| LLM thường trú (một mô hình) | **Qwen3.5-9B** (FP8 lượng tử hoá trực tuyến, ~10 GB) — đa phương thức, 262k; hoặc **gpt-oss-20b** ("chạy trong 16 GB", MXFP4, Apache 2.0) [R30]; hoặc gemma-4-26B-A4B 4-bit (~14–16 GB [ƯỚC TÍNH]) | để lại ≥6–8 GB cho KV cache |
| Encoder | Vietnamese_Embedding/bge-m3 + bge-reranker-v2-m3 fp16 (~1–2 GB mỗi cái) | ST: fp16 trên GPU ~2x so với fp32 [R21] |
| extraction / normalization / query / stance | mô hình thường trú + `response_format` json_schema (xgrammar) | stance có thể chạy hết 700 cặp vì rẻ |
| legal_reasoning / final_report | mô hình thường trú nếu qua gold; nếu không → API VN (GLM-5.2) cho tài liệu công khai, hoặc người | |
| document_vision | cùng Qwen3.5-9B (ảnh+chữ) hoặc Qwen2.5-VL-7B | đo CER |

- **Thời gian [ƯỚC TÍNH]:** nền 2,7 phút + encoder <1–2 phút + stance 700 cặp ~2–6 phút (vLLM gộp lô; tham chiếu L4: 24 GB, **300 GB/s**, FP8 485 TFLOPS có sparsity [R51]; với mô hình 9B FP8 ~9,5 GB, mỗi bước giải mã đọc trọng số mất ~32 ms → ~30 tok/s một luồng, hàng nghìn tok/s khi gộp 32–64 luồng) → **~6–11 phút/bộ**, chưa kể khởi động mô hình 1–3 phút. Đo bằng `vllm bench serve` (báo throughput, TTFT, TPOT) [R52].
- **Phần cứng:** GPU 24 GB (L4/RTX 3090/4090), RAM 32–64 GB, SSD ≥100 GB.
- **Chi phí/bộ:** máy tự có → điện năng (~0,1 kWh/bộ [ƯỚC TÍNH]). Thuê: tài liệu tính tiền của FPT lấy ví dụ GPU VM 1×H100 **$2,54/giờ** và GPU Container 1×H100 **$2,31/giờ**, tính theo giây [R2]; giá GPU 24 GB trên FPT không tìm thấy [UNVERIFIED]. Nếu máy thuê chạy liên tục và xử lý ~6 bộ/giờ → ~$0,4/bộ; nếu bật lên cho từng bộ thì thời gian khởi động chiếm phần lớn → T2 chỉ đáng khi xử lý theo lô hoặc khi tài liệu là **mật** (dữ liệu không rời máy chủ).

### Tóm tắt ba tầng

| | T0 laptop ngoại tuyến | T1 laptop + FPT | T2 1 GPU 24 GB |
|---|---|---|---|
| Thời gian/bộ 300 trang | ~5–15 phút (không LLM) | ~10–20 phút lần đầu; ~3–4 phút khi có cache | ~6–11 phút (+1–3 phút khởi động) |
| Chi phí/bộ | 0 | ≈ $0,4–0,9 (chỉ gemma) · $0,5–1,4 (thác) · $1,1–2,7 (GLM-5.2 mọi cặp) | điện; hoặc ~$0,4 nếu thuê H100 chạy lô |
| RAM / đĩa | 8–16 GB / 4–7 GB | 8 GB / ~1 GB | 32–64 GB + 24 GB VRAM / ≥100 GB |
| Dữ liệu rời máy? | Không | Có (VN, có thể sang JP) | Không (nếu máy của nhóm/khách) |
| Hợp với | demo không mạng, tài liệu mật, bản dùng thử | demo cuộc thi, tài liệu công khai | khách hàng có tài liệu mật, xử lý lô |

---

## 6. Bảo vệ dữ liệu: gửi tài liệu lên LLM đám mây

*Đây là tổng hợp để nhóm định hướng kỹ thuật, không phải tư vấn pháp lý; Thảo cần soát lại trước khi đưa vào hồ sơ dự thi.* Văn bản gốc lấy từ hệ thống văn bản của Cổng TTĐT Chính phủ (bản PDF ký số; bản quét được tôi OCR bằng Tesseract `vie`, đọc 06/10/2026) [R60–R66].

### 6.1 Khung pháp lý đang có hiệu lực (đã kiểm tra văn bản gốc)

| Văn bản | Số hiệu, ngày | Hiệu lực | Điểm liên quan |
|---|---|---|---|
| **Luật Bảo vệ dữ liệu cá nhân** | **91/2025/QH15**, Quốc hội khóa XV kỳ họp thứ 9 thông qua 26/06/2025 | **01/01/2026** (Điều 38.1) | toàn bộ nghĩa vụ xử lý DLCN, chuyển xuyên biên giới (Điều 20), AI/đám mây (Điều 30), mức phạt (Điều 8) [R60] |
| Nghị định hướng dẫn | **356/2025/NĐ-CP** ngày 31/12/2025 | 01/01/2026 (Điều 42.1) | "**Nghị định số 13/2023/NĐ-CP… hết hiệu lực** kể từ ngày Nghị định này có hiệu lực" (Điều 42.2) [R61] |
| NĐ 13/2023/NĐ-CP | ngày 17/04/2023 | **hết hiệu lực từ 01/01/2026** | hồ sơ và sự đồng ý đã có theo NĐ 13 được dùng tiếp (Luật 91, Điều 39) |
| Nghị định xử phạt | 330/2026/NĐ-CP ngày 19/08/2026 "xử phạt vi phạm hành chính trong lĩnh vực an ninh mạng và bảo vệ dữ liệu cá nhân" | [UNVERIFIED] — chỉ xác nhận tên và ngày trong danh mục, chưa đọc nội dung | [R62] |
| Luật Dữ liệu | 60/2024/QH15 ngày 30/11/2024 | 01/07/2025 (Điều 45) | "dữ liệu quan trọng/cốt lõi" theo **danh mục do Thủ tướng ban hành**; Điều 23 về chuyển/xử lý xuyên biên giới [R63] |
| Luật Trí tuệ nhân tạo | **134/2025/QH15** (số hiệu xác nhận qua NĐ 142/2026/NĐ-CP ngày 30/04/2026 hướng dẫn luật này) | [UNVERIFIED] | NĐ 142 quy định phân loại mức độ rủi ro hệ thống AI, thông báo/gắn nhãn, đánh giá sự phù hợp hệ thống rủi ro cao [R64]; GreenScan thuộc mức nào: chưa xác định |
| Luật Kiểm toán độc lập | 67/2011/QH12 | — | Điều 43 "Nghĩa vụ bảo mật"; Điều 50 lưu hồ sơ kiểm toán tối thiểu 10 năm, "an toàn, đầy đủ, hợp pháp và bảo mật" [R65]; Luật 56/2024/QH15 có sửa một số điều — chưa kiểm tra có chạm Điều 43/50 không [UNVERIFIED] |

### 6.2 Các điều khoản chạm trực tiếp vào việc gửi tài liệu lên LLM đám mây

- **Gọi API ở nước ngoài là "chuyển dữ liệu cá nhân xuyên biên giới".** Luật 91, Điều 20.1(c): "…sử dụng nền tảng ở ngoài lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam để xử lý dữ liệu cá nhân được thu thập tại Việt Nam"; NĐ 356, Điều 17.1(a) nêu cả việc lưu "trên dịch vụ điện toán đám mây của nhà cung cấp dịch vụ ở nước ngoài" [R60, R61]. Vì vậy mọi đoạn văn có tên người, chữ ký, số điện thoại… gửi tới Gemini/OpenAI/Anthropic, và **có thể cả khi FPT Serverless tự chuyển sang Nhật** (§2.6), đều rơi vào diện này [suy luận].
- **Nghĩa vụ:** lập hồ sơ đánh giá tác động chuyển DLCN xuyên biên giới, gửi bản chính cho cơ quan chuyên trách (Bộ Công an) trong **60 ngày** kể từ lần chuyển đầu tiên; làm một lần cho suốt thời gian hoạt động và cập nhật khi thay đổi (Điều 20.2–20.3) [R60].
- **Miễn đánh giá chuyển xuyên biên giới:** cơ quan nhà nước; tổ chức lưu DLCN của chính người lao động trên điện toán đám mây; chủ thể tự chuyển (Luật 91, Điều 20.6). NĐ 356, Điều 17.3 thêm: hoạt động báo chí; **"việc chuyển dữ liệu cá nhân xuyên biên giới đã được công khai theo quy định của pháp luật"**; tình huống khẩn cấp; quản lý nhân sự; ký kết hợp đồng vận chuyển, thanh toán, thị thực… [R61]. → Tên lãnh đạo, thành viên HĐQT trong báo cáo đã công bố theo quy định công bố thông tin là DLCN "đã được công khai theo quy định của pháp luật" → nhiều khả năng thuộc diện miễn [suy luận, Thảo cần xác nhận].
- **AI và điện toán đám mây:** Luật 91, Điều 30 — xử lý "đúng mục đích và giới hạn trong phạm vi cần thiết"; "xử lý dữ liệu cá nhân bằng trí tuệ nhân tạo phải thực hiện phân loại theo mức độ rủi ro" [R60]. NĐ 356, Điều 12 — hợp đồng với nhà cung cấp đám mây phải nêu rõ việc chấp hành pháp luật Việt Nam về bảo vệ DLCN, luồng xử lý, vai trò các bên, biện pháp bảo mật, thời hạn xử lý và xóa/hủy; "**dữ liệu cá nhân trên điện toán đám mây phải được mã hoá ở trạng thái nghỉ và truyền**, kèm theo phân quyền truy cập nghiêm ngặt". NĐ 356, Điều 10 — phải thông báo cho chủ thể về xử lý tự động, giải thích nguyên tắc thuật toán, cho lựa chọn không tham gia; đánh giá tuân thủ định kỳ 1 năm/lần [R61].
- **Đánh giá tác động xử lý (DPIA):** Luật 91, Điều 21 — lập hồ sơ, nộp bản chính trong 60 ngày từ ngày bắt đầu xử lý; thành phần hồ sơ ở NĐ 356, Điều 19 (báo cáo theo Mẫu số 10, hợp đồng xử lý, chính sách, sơ đồ luồng dữ liệu…) [R60, R61].
- **Ưu đãi cho doanh nghiệp nhỏ/khởi nghiệp:** được chọn **không** thực hiện Điều 21, Điều 22 và khoản 2 Điều 33 (chỉ định bộ phận/nhân sự bảo vệ DLCN) trong **05 năm** từ 01/01/2026; hộ kinh doanh và doanh nghiệp siêu nhỏ không phải thực hiện — **trừ** khi kinh doanh dịch vụ xử lý DLCN, trực tiếp xử lý DLCN nhạy cảm, hoặc từ khi xử lý tích lũy **từ 100 nghìn chủ thể trở lên** (Luật 91, Điều 38.2–38.3; NĐ 356, Điều 41) [R60, R61]. Lưu ý: ưu đãi này **không** bao gồm Điều 20 (chuyển xuyên biên giới).
- **"Dịch vụ xử lý dữ liệu cá nhân" cần giấy chứng nhận:** NĐ 356, Điều 21 liệt kê, trong đó có "cung cấp và vận hành hệ thống, phần mềm tự động để thay mặt bên kiểm soát… xử lý dữ liệu cá nhân" và "xử lý dữ liệu cá nhân tự động dựa trên công nghệ dữ liệu lớn, trí tuệ nhân tạo"; Điều 22–27 quy định điều kiện và Giấy chứng nhận đủ điều kiện kinh doanh [R61]. GreenScan không nhằm xử lý DLCN, nhưng nếu thương mại hoá như dịch vụ phân tích tài liệu của khách hàng có chứa DLCN thì cần ý kiến pháp lý về việc có thuộc diện này không.
- **Mức phạt tối đa:** 5% doanh thu năm liền kề trước với vi phạm chuyển DLCN xuyên biên giới; 10 lần khoản thu với mua bán DLCN; 3 tỷ đồng với vi phạm khác (mức cho tổ chức; cá nhân bằng một nửa) (Luật 91, Điều 8.3–8.6) [R60].
- **Dữ liệu quan trọng/cốt lõi (Luật Dữ liệu):** chỉ những dữ liệu thuộc danh mục do Thủ tướng ban hành; chuyển xuyên biên giới phải bảo đảm quốc phòng, an ninh, lợi ích quốc gia (Điều 23) [R63]. Báo cáo bền vững đã công bố gần như chắc chắn không thuộc; tài liệu nội bộ của doanh nghiệp ngành nhạy cảm (năng lượng, ngân hàng…) phải đối chiếu danh mục [UNVERIFIED danh mục]. Nếu dữ liệu đó là DLCN thì theo luật DLCN (NĐ 356, Điều 42.3 sửa NĐ 165/2025/NĐ-CP) [R61].
- **Hồ sơ kiểm toán:** Luật Kiểm toán độc lập, Điều 43.1 — kiểm toán viên, doanh nghiệp kiểm toán "không được tiết lộ thông tin về hồ sơ kiểm toán, khách hàng, đơn vị được kiểm toán, trừ trường hợp được khách hàng, đơn vị được kiểm toán chấp thuận hoặc theo quy định của pháp luật"; Điều 43.3 — phải có hệ thống kiểm soát nội bộ bảo đảm nghĩa vụ bảo mật [R65]. Gửi giấy tờ làm việc của kiểm toán lên một LLM bên thứ ba khi chưa có chấp thuận là rủi ro trực tiếp với điều này.

### 6.3 Vị trí xử lý dữ liệu của FPT (nhắc lại §2.6) và khoảng trống trong điều khoản

- Serverless: tự chuyển VN↔JP khi quá tải; Dedicated: khoá vùng, "bảo đảm dữ liệu không rời vùng đã chọn" [R3]. DeepSeek-V4-Flash, Qwen3.6-27B ghi vùng **JP**; các mô hình Partner đi qua bên thứ ba [R1].
- Privacy Statement của FPT AI Factory (đọc 05/10/2026) vẫn viện dẫn **NĐ 13/2023 — văn bản đã hết hiệu lực từ 01/01/2026** — và không nhắc Luật 91/2025; cũng không nói prompt/kết quả suy luận có được ghi log, lưu bao lâu, hay dùng để huấn luyện hay không [R5]. → Trước khi xử lý tài liệu không công khai, cần **hợp đồng/phụ lục xử lý dữ liệu** với FPT có các nội dung NĐ 356, Điều 12.2 yêu cầu.

### 6.4 Khuyến nghị thực tế cho GreenScan

| Loại tài liệu | Ví dụ | Được gửi tới | Điều kiện |
|---|---|---|---|
| **A — Công khai** | BCPTBV, BCTN đã công bố | FPT Serverless (VN/JP); API nước ngoài **gói trả tiền** nếu cần | chỉ gửi đoạn cần thiết (tuyên bố + đoạn bằng chứng, như stance hiện nay); ghi nhà cung cấp/mô hình/vùng vào manifest; không dùng gói Free của Gemini (dữ liệu dùng để cải tiến sản phẩm) [R6] |
| **B — Nội bộ, chưa công bố** | bản thảo báo cáo, số liệu nội bộ | **chỉ** T0/T2 tại chỗ, hoặc FPT **Dedicated (khoá VN)** có hợp đồng xử lý dữ liệu | che DLCN (tên, SĐT, email, số định danh) trước khi gửi; mã hoá khi lưu và truyền (NĐ 356, Điều 12.4); không dùng mô hình vùng JP/Partner |
| **C — Mật nghề nghiệp** | hồ sơ kiểm toán, giấy tờ làm việc | **chỉ** T0/T2 trên hạ tầng của khách hàng/công ty kiểm toán | chấp thuận bằng văn bản của khách hàng nếu muốn khác (Luật KTĐL, Điều 43); không bao giờ gửi API nước ngoài |

Biện pháp kỹ thuật đề xuất:
1. Thêm trường `data_class` (A/B/C) khi tải tài liệu; router chặn cứng các nhà cung cấp không được phép (quy tắc R8, §3.7).
2. Gỡ DeepSeek-V4-Flash và Qwen3.6-27B (vùng JP) khỏi các việc đụng tài liệu người dùng trong `routing.yaml`; kiểm tra `GET /v1/models` để chắc "GLM-5.2" là bản FPT host (VN).
3. Bộ đệm `.quantum/llm_cache` chứa lý do do mô hình viết (có thể trích lại nội dung) → với loại B/C coi như dữ liệu nhạy cảm: lưu cục bộ, mã hoá, có hạn xoá.
4. Giao diện báo rõ khi nào AI đám mây được dùng, cho chọn chế độ ngoại tuyến (phù hợp nghĩa vụ thông báo xử lý tự động, NĐ 356, Điều 10.3).
5. Giữ người duyệt cuối (`release_status: PENDING_HUMAN_REVIEW`) và gắn nhãn nội dung do AI tạo, phù hợp hướng của Luật Trí tuệ nhân tạo và NĐ 142/2026 (thông báo, gắn nhãn) [R64]; mức rủi ro cụ thể chờ ý kiến pháp lý.
6. Nhóm sinh viên/khởi nghiệp có thể dùng ưu đãi 5 năm cho DPIA và bộ phận bảo vệ DLCN, nhưng **không** được miễn nghĩa vụ khi chuyển DLCN xuyên biên giới → cách đơn giản nhất là không bao giờ gửi tài liệu loại B/C ra nước ngoài.

---

## 7. Bảng định tuyến khuyến nghị cuối cùng

Chi phí cột T1 tính cho một bộ 300 trang theo giá FPT đọc 05/10/2026 [ƯỚC TÍNH, giả định ở §1.2].

| Việc | T0 (ngoại tuyến) | T1 (laptop + FPT) | T2 (1 GPU 24 GB) | Vì sao | Lời gọi & chi phí/bộ (T1) | Phải đo gì trên gold trước khi tin |
|---|---|---|---|---|---|---|
| quantitative_verification | Python tất định | Python tất định | Python tất định | LLM không phân xử số (R1) | 0 | 17 bẫy xanh + số HPG giữ nguyên |
| claim_extraction | luật + từ điển (hiện tại) | luật; tuỳ chọn gemma-4-26B-A4B-it trên chunk đã lọc, gộp 8 chunk/lời gọi | mô hình thường trú trên chunk đã lọc | khối lượng lớn, cần recall; thác rẻ trước (R3) | 0–113 lời gọi; $0–0,04 | recall/precision tuyên bố so với gold; không hỏng 17 bẫy; tỷ lệ JSON hỏng < 1% |
| claim_normalization | regex + taxonomy | gemma-4-26B-A4B-it + JSON schema + kiểm tra đơn vị/năm | mô hình thường trú + xgrammar | điền 5 thuộc tính là việc có cấu trúc; mô hình vừa đủ (R5) | ~250; ~$0,02 | khớp chính xác từng thuộc tính (metric, giá trị+đơn vị, kỳ, gốc, phạm vi); so với regex |
| retrieval_query_generation | mẫu tất định | mẫu; LLM chỉ khi 0 kết quả từ khoá | như T1 | LLM thêm độ trễ mà chưa chứng minh tăng recall | 0–50; <$0,01 | Recall@5/10, MRR có/không LLM query |
| dense + rerank | bge-m3 int8 (16 GB) hoặc e5-small/base int8 (8 GB); rerank 0 hoặc base int8 top-10 | Vietnamese_Embedding + bge-reranker-v2-m3 (FPT) — **lưu ý giấy phép mâu thuẫn (FPT: CC-BY-NC; HF: Apache-2.0)** | bge-m3/Vietnamese_Embedding + bge-reranker-v2-m3 fp16 trên GPU | encoder rẻ; chất lượng truy xuất quyết định mọi bước sau | ~$0,04 | Recall@1/5/10/30, nDCG@10 (RQ4/RQ5 trong protocol); thời gian/tuyên bố; **A/B Vietnamese_Embedding với bge-m3 và e5** (VN-MTEB ClimateFEVER-VN nDCG@10: AITeamVN 13,25; bge-m3 21,27; e5-small 15,13 [R53]) |
| qualitative_stance | luật → mDeBERTa NLI int8 → người | luật → NLI → gemma-4-26B-A4B-it → GLM-5.2 cho cặp bất đồng/nghi CONTRADICTS → người; giữ `llm_stance_decisive: false` | luật → NLI → mô hình thường trú → (GLM-5.2 qua API nếu được phép) → người | MiniCheck/AlignScore: mô hình nhỏ đủ cho grounding; thác giảm 40–90% lời gọi lớn | 700 + ~100–200 lên GLM; ~$0,19–0,76 (thác) — so với $0,79–2,02 nếu tất cả qua GLM-5.2 | precision/recall theo từng quan hệ, **đặc biệt precision CONTRADICTS**; độ đồng thuận NLI–gemma–GLM; tỷ lệ chuyển người xem; A/B thứ tự trường "reason trước/relation trước" |
| legal_reasoning | rule pack + người | GLM-5.2 (VN) với văn bản luật đưa vào prompt; Saola-Small-32B làm đối chứng | thường trú nếu qua gold, nếu không → người/API | khó nhất, số lời gọi ít → dùng mô hình mạnh | ~40; $0,21–0,47 | độ đúng ánh xạ điều khoản (Thảo chấm), cho phép "không đủ căn cứ" |
| final_report | mẫu tiếng Việt tất định | **gemma-4-31B-it hoặc GLM-5.2** (không dùng Llama-3.3-70B) | thường trú | văn tiếng Việt; Llama 3.3 không hỗ trợ chính thức tiếng Việt, ngữ cảnh 32k | 1; $0,007–0,064 | chấm mù 3–5 báo cáo (độ trôi chảy, trung thực); kiểm tra tự động: **mọi con số trong văn bản phải có trong result.json** |
| document_vision | Tesseract `vie` | Qwen2.5-VL-7B (VN) chỉ trang không có lớp chữ, giới hạn `max_pixels` | Qwen3.5-9B (ảnh+chữ) hoặc Qwen2.5-VL-7B | chỉ dùng khi cần, giá theo token ảnh | ~20 trang; ~$0,04 | CER trên 20 trang scan; độ đúng ô bảng |
| **Tổng/bộ** | **0 đ, ~5–15 phút** | **thác: ≈ $0,5–1,4 (13–36k VND), ~10–20 phút** (chỉ gemma: $0,4–0,9; GLM mọi cặp: $1,1–2,7) | **điện/thuê GPU, ~6–11 phút** | | | |

Việc cần làm trước khi tin bất kỳ số nào ở trên:
1. **Ghi `usage` của từng lời gọi** (prompt/completion/reasoning tokens) vào manifest — `LLMResponse.usage` đã nhận nhưng chưa lưu; không có nó thì mọi con số chi phí ở đây vẫn là ước tính.
2. Kiểm tra GLM-5.2 trên FPT có đang suy luận ngầm không (4–6 s/lời gọi gợi ý là có); thử tắt bằng `chat_template_kwargs` [UNVERIFIED tham số đúng cho GLM-5.2 trên FPT] và A/B trên gold.
3. Chuyển sang `response_format: json_schema` khi nhà cung cấp hỗ trợ; ghi tỷ lệ JSON hỏng.
4. Đo trên laptop: bge-m3 fp32 vs ONNX int8 (`avx2`) vs OpenVINO int8 với 500 đoạn thật; mDeBERTa NLI; `llama-bench` với prompt stance thật.
5. Đăng ký ngưỡng trước cho từng việc mới trong `configs/measurement_decisions.yaml` (đúng quy trình D-2026-09-22-05).

---

## 8. Tài liệu tham khảo

Ngày đọc: 05/10/2026, trừ [R60]–[R66] đọc 06/10/2026.

**Giá, điều khoản, nhà cung cấp**
- [R1] FPT AI Marketplace — API danh mục công khai: https://marketplace-api.fptcloud.com/api/v2/portal/models?page=1&page_size=50 và https://marketplace-api.fptcloud.com/api/v2/portal/models/options (giá, vùng, RPM/TPM, JSON schema, model card trên từng trang mô hình); giao diện: https://marketplace.fptcloud.com/en
- [R2] FPT AI Factory docs — AI Inference Billing: https://ai-docs.fptcloud.com/account/billing/tutorials/billing-policy/ai-inference-billing.md ; Model Deprecations: https://ai-docs.fptcloud.com/fpt-ai-inference/fpt-ai-inference/tutorials/model-deprecations.md ; ví dụ tính tiền GPU VM/Container trong https://ai-docs.fptcloud.com/llms-full.txt
- [R3] FPT FAQ — Can I select a specific Region?: https://ai-docs.fptcloud.com/fpt-ai-inference/fpt-ai-inference/faq/can-i-select-a-specific-region.md ; Why are requests routed to Japan?: https://ai-docs.fptcloud.com/fpt-ai-inference/fpt-ai-inference/faq/why-are-requests-routed-to-japan.md
- [R4] FPT AI Factory — Starter Plan, Online Referral (điều khoản trong https://ai-docs.fptcloud.com/llms-full.txt)
- [R5] FPT AI Factory — Privacy Statement: https://factory.fpt.ai/privacy-policy/privacy-statement ; Terms of Use: https://factory.fpt.ai/privacy-policy/terms-of-use
- [R6] Google — Gemini Developer API pricing (trang ghi "Last updated 2026-10-01 UTC"): https://ai.google.dev/gemini-api/docs/pricing
- [R7] OpenAI — API pricing: https://developers.openai.com/api/docs/pricing
- [R8] OpenAI — Data controls in the OpenAI platform: https://developers.openai.com/api/docs/guides/your-data
- [R9] Anthropic — Pricing: https://platform.claude.com/docs/en/about-claude/pricing ; Commercial Terms of Service (hiệu lực 17/06/2025): https://www.anthropic.com/legal/commercial-terms

**Định tuyến, thác, mô hình nhỏ, đầu ra có cấu trúc, cache**
- [R10] Chen, L., Zaharia, M., Zou, J. (2023). *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance*. arXiv:2305.05176. https://arxiv.org/abs/2305.05176
- [R11] Ong, I., Almahairi, A., Wu, V., Chiang, W.-L., Wu, T., Gonzalez, J. E., Kadous, M. W., Stoica, I. (2024). *RouteLLM: Learning to Route LLMs with Preference Data*. arXiv:2406.18665. https://arxiv.org/abs/2406.18665
- [R12] LMSYS (01/07/2024). *RouteLLM: An Open-Source Framework for Cost-Effective LLM Routing*. https://lmsys.org/blog/2024-07-01-routellm/
- [R13] Yue, M., Zhao, J., Zhang, M., Du, L., Yao, Z. (2024). *Large Language Model Cascades with Mixture of Thoughts Representations for Cost-efficient Reasoning*. ICLR 2024. https://arxiv.org/abs/2310.03094
- [R14] Aggarwal, P., Madaan, A., et al. (2024). *AutoMix: Automatically Mixing Language Models*. NeurIPS 2024. https://arxiv.org/abs/2310.12963
- [R15] Tang, L., Laban, P., Durrett, G. (2024). *MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents*. EMNLP 2024. https://arxiv.org/abs/2404.10774
- [R16] Gupta, N., Narasimhan, H., Jitkrittum, W., Rawat, A. S., Menon, A. K., Kumar, S. (2024). *Language Model Cascades: Token-level uncertainty and beyond*. arXiv:2404.10136. https://arxiv.org/abs/2404.10136
- [R17] Dekoninck, J., Baader, M., Vechev, M. (2024, rev. 2025). *A Unified Approach to Routing and Cascading for LLMs*. arXiv:2410.10347. https://arxiv.org/abs/2410.10347
- [R18] Ding, D., Mallick, A., Wang, C., Sim, R., Mukherjee, S., Ruhle, V., Lakshmanan, L. V. S., Awadallah, A. H. (2024). *Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing*. ICLR 2024. https://arxiv.org/abs/2404.14618
- [R19] Nie, L., Ding, Z., Hu, E., Jermaine, C., Chaudhuri, S. (2024). *Online Cascade Learning for Efficient Inference over Streams*. ICML 2024. https://arxiv.org/abs/2402.04513
- [R23] Bucher, M. J. J., Martini, M. (2024). *Fine-Tuned 'Small' LLMs (Still) Significantly Outperform Zero-Shot Generative AI Models in Text Classification*. arXiv:2406.08660. https://arxiv.org/abs/2406.08660
- [R24] Edwards, A., Camacho-Collados, J. (2024). *Language Models for Text Classification: Is In-Context Learning Enough?* LREC-COLING 2024. https://arxiv.org/abs/2403.17661
- [R25] Zha, Y., Yang, Y., Li, R., Hu, Z. (2023). *AlignScore: Evaluating Factual Consistency with a Unified Alignment Function*. ACL 2023. https://arxiv.org/abs/2305.16739
- [R26] Hsieh, C.-Y., Li, C.-L., Yeh, C.-K., Nakhost, H., Fujii, Y., Ratner, A., Krishna, R., Lee, C.-Y., Pfister, T. (2023). *Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes*. Findings of ACL 2023. https://arxiv.org/abs/2305.02301
- [R28] Tam, Z. R., Wu, C.-K., Tsai, Y.-L., Lin, C.-Y., Lee, H.-y., Chen, Y.-N. (2024). *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models*. arXiv:2408.02442. https://arxiv.org/abs/2408.02442
- [R29] Shorten, C., Pierse, C., Smith, T. B., Cardenas, E., Sharma, A., Trengrove, J., van Luijt, B. (2024). *StructuredRAG: JSON Response Formatting with Large Language Models*. arXiv:2408.11061. https://arxiv.org/abs/2408.11061
- [R31] Geng, S., Cooper, H., Moskal, M., Jenkins, S., Berman, J., Ranchin, N., West, R., Horvitz, E., Nori, H. (2025). *JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models*. arXiv:2501.10868. https://arxiv.org/abs/2501.10868
- [R32] Geng, S., Josifoski, M., Peyrard, M., West, R. (2023). *Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning*. EMNLP 2023. https://arxiv.org/abs/2305.13971
- [R33] Dong, Y., Ruan, C. F., Cai, Y., Lai, R., Xu, Z., Zhao, Y., Chen, T. (2025). *XGrammar: Flexible and Efficient Structured Generation Engine for Large Language Models*. MLSys 2025. https://arxiv.org/abs/2411.15100
- [R34] vLLM docs — Structured Outputs: https://docs.vllm.ai/en/latest/features/structured_outputs.html
- [R35] Ollama docs — Structured outputs: https://docs.ollama.com/capabilities/structured-outputs
- [R36] Bang, F. (2023). *GPTCache: An Open-Source Semantic Cache for LLM Applications Enabling Faster Answers and Cost Savings*. NLP-OSS 2023, tr. 212–218. https://aclanthology.org/2023.nlposs-1.24/
- [R37] OpenAI — Prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching

**Tăng tốc CPU, mô hình mở, phần cứng**
- [R20] Sentence-Transformers — Speeding up Inference (SentenceTransformer, kèm biểu đồ CPU): https://sbert.net/docs/sentence_transformer/usage/efficiency.html ; (CrossEncoder): https://sbert.net/docs/cross_encoder/usage/efficiency.html
- [R21] Sentence-Transformers v3.2.0 release notes (10/10/2024): https://github.com/UKPLab/sentence-transformers/releases/tag/v3.2.0 ; efficiency.rst bản v5.0.0: https://raw.githubusercontent.com/UKPLab/sentence-transformers/v5.0.0/docs/sentence_transformer/usage/efficiency.rst
- [R22] Sentence-Transformers v3.3.0 release notes (11/11/2024): https://github.com/UKPLab/sentence-transformers/releases/tag/v3.3.0
- [R27] PyPI JSON: https://pypi.org/pypi/openvino/json , https://pypi.org/pypi/onnxruntime/json ; llama.cpp releases (b11425, 05/10/2026): https://github.com/ggml-org/llama.cpp/releases
- [R30] OpenAI — gpt-oss-20b model card: https://huggingface.co/openai/gpt-oss-20b
- [R38] Hugging Face/Intel — *CPU Optimized Embeddings with 🤗 Optimum Intel and fastRAG*: https://huggingface.co/blog/intel-fast-embedding
- [R39] VMLU leaderboard: https://vmlu.ai/leaderboard
- [R40] ExchangeRate-API (open endpoint; cập nhật 05/10/2026 00:02 UTC): https://open.er-api.com/v6/latest/USD
- [R41] It's FOSS (15/05/2026). *Can You Run LLMs Locally Without a GPU? I Tested 8 Models on Linux*. https://itsfoss.com/testing-local-llms-without-gpu/
- [R42] Qwen/Qwen3.5-4B model card: https://huggingface.co/Qwen/Qwen3.5-4B
- [R43] Qwen/Qwen3.5-9B: https://huggingface.co/Qwen/Qwen3.5-9B ; Qwen/Qwen3.5-2B: https://huggingface.co/Qwen/Qwen3.5-2B
- [R44] Hugging Face API — danh sách mô hình Qwen theo ngày tạo: https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=80
- [R45] Google — Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- [R46] openai/MMMLU dataset card: https://huggingface.co/datasets/openai/MMMLU
- [R47] li-lab/MMLU-ProX dataset card: https://huggingface.co/datasets/li-lab/MMLU-ProX
- [R48] MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7: https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
- [R49] MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli: https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli
- [R50] Qwen/Qwen2.5-VL-7B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- [R51] NVIDIA L4: https://www.nvidia.com/en-us/data-center/l4/
- [R52] vLLM docs — `vllm bench serve`: https://docs.vllm.ai/en/latest/cli/bench/serve.html

**Embedding/reranker tiếng Việt**
- [R53] Pham, L., Luu, T., Vo, T., Nguyen, M., Hoang, V. (2025). *VN-MTEB: Vietnamese Massive Text Embedding Benchmark*. arXiv:2507.21500. https://arxiv.org/abs/2507.21500 (bảng: https://arxiv.org/html/2507.21500); Findings of EACL 2026, tr. 1705–1725: https://aclanthology.org/2026.findings-eacl.86/
- [R54] MTEB — kho kết quả chính thức: https://github.com/embeddings-benchmark/results ; định nghĩa benchmark "VN-MTEB (vie, v1)": https://github.com/embeddings-benchmark/mteb/blob/main/mteb/benchmarks/benchmarks/benchmarks.py
- [R55] Model card Hugging Face (giấy phép, tham số, ONNX/OpenVINO, số liệu tự công bố): https://huggingface.co/AITeamVN/Vietnamese_Embedding (API: https://huggingface.co/api/models/AITeamVN/Vietnamese_Embedding — license apache-2.0, sửa lần cuối 25/08/2025), https://huggingface.co/intfloat/multilingual-e5-small , https://huggingface.co/intfloat/multilingual-e5-base , https://huggingface.co/intfloat/multilingual-e5-large , https://huggingface.co/intfloat/multilingual-e5-large-instruct , https://huggingface.co/Alibaba-NLP/gte-multilingual-base , https://huggingface.co/BAAI/bge-m3 , https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder , https://huggingface.co/contextboxai/halong_embedding , https://huggingface.co/GreenNode/GreenNode-Embedding-Large-VN-V1 , https://huggingface.co/jinaai/jina-embeddings-v3 , https://huggingface.co/Qwen/Qwen3-Embedding-0.6B , https://huggingface.co/google/embeddinggemma-300m , https://huggingface.co/BAAI/bge-reranker-v2-m3 , https://huggingface.co/namdp-ptit/ViRanker , https://huggingface.co/itdainb/PhoRanker , https://huggingface.co/AITeamVN/Vietnamese_Reranker , https://huggingface.co/Alibaba-NLP/gte-multilingual-reranker-base , https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual , https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- [R56] Dang, P.-N., Nguyen, K.-L., Pham, T.-H. (2025). *ViRanker: A BGE-M3 & Blockwise Parallel Transformer Cross-Encoder for Vietnamese Reranking*. arXiv:2509.09131. https://arxiv.org/abs/2509.09131
- [R57] Zhang, X., Zhang, Y., Long, D., Xie, W., Dai, Z., Tang, J., et al. (2024). *mGTE: Generalized Long-Context Text Representation and Reranking Models for Multilingual Text Retrieval*. arXiv:2407.19669. https://arxiv.org/abs/2407.19669

**Văn bản pháp luật Việt Nam (Cổng TTĐT Chính phủ — bản ký số; đọc 06/10/2026)**
- [R60] Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 (thông qua 26/06/2025; hiệu lực 01/01/2026): https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/7/91qh.signed.pdf (bản quét — tôi OCR bằng Tesseract `vie`)
- [R61] Nghị định 356/2025/NĐ-CP ngày 31/12/2025 quy định chi tiết một số điều và biện pháp thi hành Luật Bảo vệ dữ liệu cá nhân: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/01/356-nd.signed.pdf (bản quét — OCR)
- [R62] Nghị định 330/2026/NĐ-CP ngày 19/08/2026 quy định xử phạt vi phạm hành chính trong lĩnh vực an ninh mạng và bảo vệ dữ liệu cá nhân (chỉ xác nhận tên/ngày): https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/8/330_2026_nd-cp_19082026-signed.signed.pdf
- [R63] Luật Dữ liệu số 60/2024/QH15 ngày 30/11/2024: https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/luat60.pdf
- [R64] Nghị định 142/2026/NĐ-CP ngày 30/04/2026 quy định chi tiết một số điều và biện pháp thi hành Luật Trí tuệ nhân tạo (căn cứ "Luật Trí tuệ nhân tạo số 134/2025/QH15"): https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/142-2026-ndcp.signed.pdf (OCR trang 1–2 và 3 trang cuối)
- [R65] Luật Kiểm toán độc lập số 67/2011/QH12: https://datafiles.chinhphu.vn/cpp/files/vbpq/2011/04/105909_l67qh.doc ; Luật số 56/2024/QH15 sửa đổi, bổ sung (có Luật Kiểm toán độc lập): https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/luat56.pdf
- [R66] Cổng TTĐT Chính phủ — Hệ thống văn bản (danh mục Luật: https://vanban.chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3 ; Nghị định: https://vanban.chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=4)

**Số liệu nội bộ của nhóm (đọc, không sửa)**: `benchmark/llm_stance_ab_2026-09-28.md`; `docs/04-data-ai/MEASUREMENT_PROTOCOL_2026-09-29.md`; `configs/routing.yaml`; `configs/default.yaml`; `.quantum/runs/b96cbd0fab874f0c/result.json`; `.quantum/llm_cache/stance_cache.jsonl`.
