# Chạy GreenScan có mô hình trên máy GPU thuê (vast.ai)

Mục đích: chạy **Hòa Phát có mô hình ngôn ngữ cùng đọc**, việc mà laptop không làm nổi (Qwen3-4B trên CPU mất 32 giây mỗi lượt gọi). Câu trả lời của mô hình được mang về laptop dưới dạng bộ nhớ đệm, nên hôm demo laptop phát lại được mà không cần mạng.

Thư mục này khác `deploy/vastai_a100/` (huấn luyện mô hình, cần A100 80 GB). Ở đây chỉ cần một GPU 24 GB.

## Vì sao mang về phát lại được

Mỗi câu trả lời được lưu theo khoá gồm: phiên bản prompt, tên mô hình, câu tuyên bố, đoạn bằng chứng. Máy thuê dùng đúng mã nguồn bản nộp 16/11, đúng phiên bản thư viện đọc PDF của laptop (`constraints.txt`), đúng tên mô hình `qwen3:4b-instruct-2507-q4_K_M` qua Ollama. Bước `parity` kiểm điều đó trước khi tốn tiền chạy mô hình: Hòa Phát chỉ luật trên máy thuê phải ra đúng 171 tuyên bố với cùng kết luận như laptop.

## 0. Trên laptop, trước khi thuê máy

```bash
C:/Python314/python.exe deploy/vastai_gpu_demo/make_bundle.py
```

Ghi `AI quantum/vast_bundle/greenscan_vast.tar.gz` (khoảng 23 MB). Gói không chứa khoá nào: chỉ mã nguồn, dữ liệu mẫu, hai tệp PDF Hòa Phát đã công bố và các script.

Cần có khoá SSH đã khai trong tài khoản vast.ai (mục *Account → SSH keys*).

## 1. Thuê máy

| Mục | Chọn |
|---|---|
| GPU | 1 × RTX 3090 hoặc 4090, 24 GB |
| CPU / RAM | từ 8 nhân / từ 32 GB |
| Ổ đĩa | 60 GB |
| Loại | On-demand (không chọn interruptible) |
| Template | Ubuntu 22.04 có CUDA (ví dụ *NVIDIA CUDA* hoặc *PyTorch* của vast) |
| Độ tin cậy | từ 99%, mạng xuống từ 200 Mbps |
| Cổng | không cần mở cổng nào; mọi thứ đi qua SSH |

Sau khi máy chạy, bấm nút *Connect* để lấy `<ip>` và `<port>` của SSH.

## 2. Tải lên và chạy

Trên laptop (Git Bash):

```bash
cd "/d/Sinh viên CNhan/AI quantum/vast_bundle"
scp -P <port> greenscan_vast.tar.gz root@<ip>:/workspace/
ssh -p <port> root@<ip>
```

Trên máy thuê:

```bash
cd /workspace && tar xzf greenscan_vast.tar.gz && cd greenscan
tmux new -s gs                       # mất kết nối thì vào lại bằng: tmux attach -t gs
bash vast/00_setup.sh                # 5-8 phút: Python 3.14, thư viện, Ollama, mô hình 2,5 GB
bash vast/10_run.sh                  # bốn bước bên dưới, rồi tự gói kết quả
```

| Bước của `10_run.sh` | Việc | Dự kiến | Dấu hiệu đúng |
|---|---|---|---|
| `parity` | Hòa Phát chỉ luật | 3–5 phút | `[parity] OK: cùng tuyên bố, cùng kết luận như laptop` |
| `test` | Thử mô hình ba lượt | dưới 1 phút | `ollama ps` ghi `100% GPU`; mỗi lượt vài giây (laptop: 32,1) |
| `caseA` | Ca mẫu A có mô hình, 23 lượt gọi | vài phút (laptop: 940 giây) | dòng `[run] claims 5 read_by_model …` |
| `caseB` | Hòa Phát có mô hình | **chưa đo** | dòng `[run] claims 171 …` |

Mỗi phút có một dòng `[tick]` ghi số dòng bộ nhớ đệm và mức dùng GPU. Số dòng tăng là mô hình đang trả lời. Số dòng đứng yên quá 10 phút và GPU ở 0% là treo: bấm Ctrl+C, xem `logs/ollama.log`, chạy lại `STEPS="caseB" bash vast/10_run.sh` (phần đã hỏi không phải hỏi lại).

**Dừng ngay nếu:**
- `parity` báo `KHÁC`: máy này đọc PDF khác laptop, kết quả mang về sẽ không khớp. Gửi log cho người viết script, không chạy tiếp.
- `01_ollama.sh` báo mô hình không chạy trên GPU.

## 3. Mang kết quả về và xoá máy

Trên laptop:

```bash
scp -P <port> root@<ip>:/workspace/greenscan/gs_results.tar.gz "/d/Sinh viên CNhan/AI quantum/vast_bundle/"
cd "/d/Sinh viên CNhan/AI quantum/docs/greenscan-ai/GreenScan-AI"
C:/Python314/python.exe deploy/vastai_gpu_demo/import_results.py "/d/Sinh viên CNhan/AI quantum/vast_bundle/gs_results.tar.gz"
```

`import_results.py` sao lưu bộ nhớ đệm hiện có rồi chỉ thêm các câu trả lời laptop chưa có (các phiên demo đang có không đổi). Sau đó mở Ollama trên laptop và chạy lệnh nó in ra: phiên Hòa Phát có mô hình được dựng trong kho demo, lấy câu trả lời từ bộ nhớ đệm.

Kiểm tệp đã về đủ rồi mới bấm **Destroy** trên vast.ai. *Stop* vẫn tính tiền ổ đĩa.

## 4. Tuỳ chọn: laptop dùng GPU thuê làm mô hình lúc demo

Giữ máy thuê chạy, mở một đường hầm SSH từ laptop:

```bash
ssh -p <port> -N -L 11435:127.0.0.1:11434 root@<ip>
```

rồi mở ứng dụng bằng `demo_store_ban_ket/CHAY_DEMO_GPU.bat`. Nấc “mô hình chạy trên máy” khi đó gọi GPU thuê, nên nút *Thử mô hình* và mọi lượt phân tích mới đều nhanh.

Hai điều phải nói đúng khi dùng cách này:
- Đoạn trích tài liệu **có rời laptop** (sang máy thuê), dù giao diện vẫn ghi “mô hình chạy trên máy này”. Chỉ dùng với tài liệu đã công bố.
- Phụ thuộc mạng hội trường. Bản phát lại từ bộ nhớ đệm (mục 3) thì không.

## An toàn dữ liệu

- Máy vast là máy của bên thứ ba. Không tải lên `.env`, khoá API, hay tài liệu chưa công bố.
- Ollama trên máy thuê chỉ nghe ở `127.0.0.1`; không mở cổng 11434 ra mạng.

## Tệp trong thư mục

| Tệp | Chạy ở | Việc |
|---|---|---|
| `make_bundle.py` | laptop | dựng gói tải lên từ checkpoint `vong2_2026-11-16` |
| `env.sh` | máy thuê | thiết lập chung (tên mô hình, bản Ollama, số lượt gọi song song) |
| `00_setup.sh`, `01_ollama.sh` | máy thuê | cài đặt; bật Ollama và nạp mô hình vào GPU |
| `10_run.sh` | máy thuê | bốn bước chạy; `STEPS="…"` để chọn bước |
| `check_parity.py`, `model_test.py` | máy thuê | so với laptop; đo số giây mỗi lượt gọi |
| `30_pack.sh` | máy thuê | gói bộ nhớ đệm, phiên, log |
| `import_results.py` | laptop | nhập bộ nhớ đệm về repo |
