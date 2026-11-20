# Thư mục chạy trên máy GPU thuê (vast.ai A100 80 GB)

> **Đã bác bỏ ngày 13/11/2026 (D-2026-11-13-03): không có kinh phí thuê GPU.** Thư mục được giữ vì `gs_train/` và `data/` là mã và dữ liệu huấn luyện mà các notebook Kaggle (`kaggle/`) dùng chung. Các lệnh `00_setup.sh`, `10_train.sh`, `20_eval.sh`, `30_serve.sh` không còn trong kế hoạch.

Tải nguyên thư mục này lên máy thuê rồi chạy 4 lệnh. Trong thư mục đã có đủ mã, dữ liệu, danh sách thư viện và lệnh mở máy chủ. Mã huấn luyện cũng chạy được trên Kaggle (T4), qua các notebook trong `kaggle/`.

| Phương án | Chạy ở đâu | Mô hình | Dữ liệu ra khỏi laptop |
|---|---|---|---|
| **1. Ngoại tuyến hoàn toàn** (bản nộp) | Laptop CPU | luật + e5 lọc tuyên bố + mDeBERTa chấm quan hệ + gte reranker + Qwen3-4B (GGUF, Ollama) viết lời giải thích; huấn luyện trên Kaggle | không |
| **2. GPU tự thuê** | Laptop chạy GreenScan, gọi máy vast.ai | gpt-oss-120b (hoặc Qwen3-14B + adapter) qua vLLM | chỉ cặp tuyên bố – đoạn bằng chứng của hàng soát |

## Cấu trúc

```
vastai_a100/
  00_setup.sh     cài thư viện, tải trước mô hình
  10_train.sh     huấn luyện: t1, stance_enc, reranker, teacher, explain, stance_llm (khoảng 3-4 giờ)
  20_eval.sh      chấm trên bộ đã đăng ký (S5, S6), xuất GGUF, vẽ biểu đồ
  30_serve.sh     máy chủ vLLM API kiểu OpenAI, cổng 8001, có API key (phương án 2)
  requirements.txt
  gs_train/       mã dùng chung Kaggle / A100 (mỗi bước in "[cell] ..." để đọc log)
  data/           dữ liệu, dựng bằng tools/build_gpu_bundle.py (chỉ văn bản báo cáo công khai + nhãn)
  kaggle/         notebook Kaggle của phương án 1
  out/ logs/      sinh ra khi chạy
```

## Các bước

**0. Ở laptop:** dựng lại dữ liệu nếu nhãn đã đổi.

```bash
.venv/Scripts/python.exe -X utf8 tools/build_gpu_bundle.py     # ghi data/ + data/manifest.json (md5 từng tệp)
```

**1. Thuê máy trên vast.ai**
- GPU: 1 × A100 SXM4 80 GB. Ổ đĩa ≥ 250 GB, vì riêng gpt-oss-120b khoảng 65 GB.
- Image: `vllm/vllm-openai` hoặc PyTorch CUDA 12.x.
- Mở cổng 8001 nếu dùng phương án 2.
- **Nên chọn máy "Secure Cloud" (trung tâm dữ liệu).** Máy "community" là máy của cá nhân. Xem mục An toàn dữ liệu.

**2. Tải lên và chạy** (dùng `tmux` để không mất tiến trình khi mất kết nối):

```bash
scp -P <port> -r deploy/vastai_a100 root@<ip>:/workspace/
ssh -p <port> root@<ip>
cd /workspace/vastai_a100 && tmux new -s gs
bash 00_setup.sh && bash 10_train.sh && bash 20_eval.sh
```

- Chỉ chạy vài bước: `STEPS="stance_llm explain" bash 10_train.sh`.
- Đổi mô hình thầy: `TEACHER=Qwen/Qwen3-32B-AWQ bash 10_train.sh`.
- Log nằm ở `logs/<bước>.log`. Mỗi bước in `[cell] ...` khi bắt đầu.

**3. Lấy kết quả về laptop** rồi vẽ lại biểu đồ:

```bash
scp -P <port> -r root@<ip>:/workspace/vastai_a100/out deploy/vastai_a100/out_a100
C:/Python314/python.exe deploy/vastai_a100/gs_train/plots.py --results deploy/vastai_a100/out_a100 --out docs/04-data-ai/hinh_mo_hinh/a100
```

**4. Phương án 2: dùng máy này làm máy đọc cho GreenScan**
- Trên máy thuê:

  ```bash
  GS_API_KEY=$(openssl rand -hex 24) bash 30_serve.sh      # ghi lại khoá; mặc định gpt-oss-120b
  ```

- Ở laptop (PowerShell):

  ```powershell
  $env:QUANTUM_SELFHOST_URL="http://<ip>:<cổng ngoài của 8001>/v1"; $env:QUANTUM_SELFHOST_KEY="<khoá>"
  $env:QUANTUM_SELFHOST_MODEL="openai/gpt-oss-120b"
  .venv/Scripts/python.exe -X utf8 tools/selfhost_check.py    # liệt kê mô hình, gọi thử 1 cặp + 1 lời giải thích
  $env:QUANTUM_PROFILE="selfhost"; quantum-agent ...           # chạy như thường
  ```

- Hồ sơ `selfhost` (`src/quantum_gw/settings.py`):
  - bật đọc cặp mơ hồ (`on_ambiguous`) và lời giải thích cho hàng soát (`queue`);
  - truy xuất vẫn chạy ở laptop (`lite`);
  - thiếu `QUANTUM_SELFHOST_URL` thì báo lỗi ngay, không lặng lẽ chạy sai.
- Bản ngoại tuyến (`offline`) không đổi.

**5. Tắt máy khi xong.** vast.ai tính tiền theo giờ, kể cả khi máy đứng yên. Chi phí so sánh: `docs/04-data-ai/hinh_mo_hinh/chi_phi_bang.png`.

## An toàn dữ liệu

- Theo D-2026-10-06-06, giấy làm việc kiểm toán (lớp C) chỉ được chạy ngoại tuyến hoặc trên GPU tại đơn vị.
- Máy thuê trên chợ GPU **không** phải GPU tại đơn vị. Vì vậy phương án 2 trên vast.ai chỉ dùng cho tài liệu công khai (lớp A), hoặc tài liệu nội bộ (lớp B) khi đã có thoả thuận với nhà cung cấp.
- Với lớp C, dùng phương án 1, hoặc đặt chính thư mục này lên GPU của đơn vị (hồ sơ `gpu`).
- Máy chủ luôn chạy với `--api-key`. Không mở cổng khi chưa đặt khoá; có thể dùng SSH tunnel (`ssh -L 8001:localhost:8001 ...`) để không mở cổng ra Internet.

## Nhãn, loss, metric (tóm tắt; số đăng ký trước ở `configs/measurement_decisions.yaml` khối `offline_training_v1`)

| Mô hình | Nhãn | Loss | Metric chính | Cổng |
|---|---|---|---|---|
| e5 lọc tuyên bố | 4 lớp T1, Claude + Q13 v1.2 | CE / CE có trọng số + làm mềm nhãn | macro-F1 kiểm chéo theo DN; cổng S1 (bắt ≥ 22/44, gắn nhầm ≤ 6/102) | s1 |
| mDeBERTa chấm quan hệ | 4 quan hệ CAP v1.0 (821 cặp, 2 lượt + phân xử) | CE có trọng số, hiệu chỉnh nhiệt độ | macro-F1 theo DN; S5 macro-F1(S,O), sai C / 100 | S5 CI dưới > 0,397, sai C ≤ luật + 1, ≤ 300 ms |
| gte reranker | độ liên quan 2/1/0 | softmax CE theo danh sách | nDCG@5, MRR@5, hit@5 | Δ nDCG@5 CI dưới > 0 |
| Qwen3-4B / 14B lời giải thích | lời giải thích của thầy (lọc: đọc được, không số mới) | CE chỉ trên token câu trả lời (LoRA) | S6 tỉ lệ nêu đủ ý, số mới = 0 | ≥ bản gốc, 0 số mới |
| Qwen3-14B chấm quan hệ (A100) | như mDeBERTa, dạng JSON | CE chỉ trên câu trả lời | S5 macro-F1(S,O), sai C / 100 | như S5 |

Mọi nhãn hiện là nhãn bạc (Claude). Chỉ mở `lift_guard` khi đã có nhãn vàng do người soát.
