# training/ — mô hình học trò cho chế độ ngoại tuyến hoàn toàn (L2)

**Ngày:** 10/10/2026 · **Mục tiêu:** thay phần mô hình đám mây đang làm bằng mô hình nhỏ chạy trên CPU laptop, **không giảm độ chính xác** — bước cuối của lộ trình L0 → L1 → L2 ở [`../docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md`](../docs/04-data-ai/OFFLINE_TUNG_PHAN_2026-10-10.md).
**Nguyên tắc không đổi:** mã tính toán và quyết định; mô hình học trò chỉ làm phần *đọc* (nhận diện tuyên bố, đối sánh đại lượng); gold do người gán là thước đo duy nhất.

---

## 1. Học trò nào, vì sao

Chọn theo **chỗ hệ thống đang yếu nhất** (thực nghiệm 10/10: luật bỏ sót 13/51 ca; đối sánh là việc mô hình đám mây làm tốt khi che số):

| Mã | Việc | Đầu vào → đầu ra | Thay cho | Mô hình nền đề xuất (giấy phép) | Ưu tiên |
| --- | --- | --- | --- | --- | --- |
| **T1** | Nhận diện tuyên bố | câu (đã che số) → `QUANTIFIED_CLAIM` · `QUALITATIVE_CLAIM` · `VAGUE` · `NOT_CLAIM` | bộ trích bằng luật (recall thấp, trích thừa) | mDeBERTa-v3-base (MIT) · checkpoint `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (MIT, XNLI-vi 0,793) · multilingual-e5-base/small (MIT) | **1** |
| **T2** | Đối sánh đại lượng | (câu tuyên bố có 1 chỗ trống đánh dấu, câu/dòng bằng chứng có 1 chỗ trống đánh dấu) → `SAME` · `DIFFERENT` | mô hình đám mây ở L1 | cross-encoder: `Alibaba-NLP/gte-multilingual-reranker-base` (Apache-2.0, đã có trong cache máy) · mDeBERTa-xnli | **2** |
| T2-gen | (dự phòng) đối sánh dạng sinh JSON như L1 | văn bản đã che → ánh xạ | như trên | Qwen3-0.6B/1.7B/4B (Apache-2.0), QLoRA theo Aarnes & Setty 2026 | 3 — chỉ nếu T2 không đạt |
| T3 | Quan hệ định tính (tuyên bố không số) | (tuyên bố, đoạn) → xác nhận · phủ nhận · không đủ | GLM-5.2 cho cặp khó | mDeBERTa-xnli | 4 |

**Tránh vì giấy phép** (nếu định hướng thương mại): phobert-base-v2 (AGPL-3.0), VnCoreNLP (GPL-3.0), PhoNER_COVID19 (chỉ nghiên cứu), các bộ dữ liệu phi thương mại (environmental_claims, AVeriTeC, XNLI, ViANLI) — dùng được cho cuộc thi, ghi rõ.

---

## 2. Dữ liệu

| Nguồn | Vai trò | Ghi chú |
| --- | --- | --- |
| Kho công khai `data/crawl/vn30/contract/clean.jsonl` (21 doanh nghiệp) | câu chưa gán | `build_claim_sentences.py` → **66.539 câu** (10/10); 4.598 luật nhận là tuyên bố · **6.631 câu có thuật ngữ môi trường mà luật từ chối/bỏ sót** · 55.310 còn lại |
| Nhãn yếu từ luật | chọn mẫu, **không** dùng làm nhãn huấn luyện chính | — |
| **Nhãn thầy** (`teacher_label.py`) | nhãn huấn luyện | chỉ tài liệu công khai; **che số theo mặc định**; bộ nhớ đệm; trần số lời gọi; chạy ≥ 3 lần và giữ điểm nhất quán (Pangakis và cs. 2023: nhãn giống nhau qua ≥ 7 lần chạy đúng hơn 19,4 điểm) |
| **Nhãn Claude** (`claude_labels.py`, 13/10) | nhãn huấn luyện khởi đầu + mốc so sánh | 500 câu train (2 lượt độc lập, κ A–B 0,92, 170 câu đọc lại) → `data/t1/train_claude.jsonl` (498); 79 câu lô 1 để so với gold người, cất ở `gold_t1/ai/`, không mở trước khi nộp nhãn. Chi tiết: mục 11 của `docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md` |
| Ca dựng sẵn (`benchmark/size_ladder_2026-10-10/`) | kiểm hành vi, **không huấn luyện** | 51 ca + bẫy số liệu |
| **Gold do người gán** (Quỳnh, Thảo, Nhân) | **thước đo duy nhất** của học trò | T1: `gold_t1_pack.py` — dev = 160 câu thầy đã gán (đo nhãn thầy), test = 594 câu HPG BCPTBV 2025 (công ty không có trong kho); gán độc lập → họp thống nhất → gold. Khung dữ liệu chung cho train/dev/test: `t1_data.py` + `schemas/training/t1_example.schema.json`. Quy trình đầy đủ: [`docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md`](../docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md); cặp gold cho T2/T3 |
| Ca chủ động chọn (active learning) | đưa cho người gán | câu thầy không nhất quán + câu học trò không chắc (dataset cartography) theo lô 50 — Ein-Dor và cs. 2020: +4–8 F1 so với chọn ngẫu nhiên khi khởi đầu từ từ khoá |

**Thầy:** `gemma-4-31B-it` (vùng VN, rẻ ~US$0,15/0,45 mỗi 1M token; đạt 32/32 và 18/19 trong thí nghiệm che); GLM-5.2 chỉ phân xử khi các lần chạy của thầy không thống nhất.
**Rủi ro nhãn thầy** (đã thấy ở lô thử 10/10): thầy nhận "dự án do Chính phủ phê duyệt…" là tuyên bố của doanh nghiệp. Pangakis và cs.: GPT-4 có F1 trung vị 0,707 trên 27 tác vụ gán nhãn, có tác vụ chỉ 0,059. Li và cs. (EMNLP 2023): học trò trên dữ liệu do LLM sinh mất 3–8 điểm ở tác vụ khách quan. → học trò luôn được chấm bằng gold, không bằng thầy.

---

## 3. Quy trình — chạy từng bước

```bash
# 0. môi trường huấn luyện riêng (không cài vào .venv sản phẩm)
python -m venv .venv-train && .venv-train/Scripts/pip install -r training/requirements-train.txt
#    (trên laptop này có thể dùng tạm .venv của thư mục cũ: đã có torch, transformers, datasets, peft)

# 1. dựng câu + nhãn yếu (≈ 45 s)
python training/build_claim_sentences.py

# 2. nhãn thầy cho T1 — mỗi lời gọi 20 câu, đã che số; lô thử 400 câu ≈ US$0,011, 26 s
python training/teacher_label.py claim --n 4000 --max-calls 200 --model gemma-4-31B-it
#    lặp lại với --seed khác để có ≥ 3 lần chạy và điểm nhất quán

# 3. nhãn thầy cho T2 — từ một phiên đã lưu của tài liệu CÔNG KHAI
python training/teacher_label.py align --run .quantum/runs/<id> --public \
       --entities "Tập đoàn Hòa Phát" "Dung Quất" "Hải Dương" --max-calls 300

# 4. huấn luyện (laptop: chỉ chạy thử; thật: Colab/Kaggle T4 với --fp16)
python training/train_classifier.py --data training/data/teacher_claim_gemma-4-31B-it.jsonl \
       --label-field teacher_label --model microsoft/mdeberta-v3-base --epochs 3 --fp16 \
       --out training/runs/t1_mdeberta

# 5. chấm trên gold (khi có) — học trò vs luật vs thầy, cùng một bộ
#    (bổ sung eval_student.py khi gold T1 về)
```

---

## 4. Tính toán — số đo và ước tính

| | Số liệu | Nguồn |
| --- | --- | --- |
| Huấn luyện trên **CPU laptop** (i7-1355U), multilingual-e5-small, độ dài 128 | **1,7 mẫu/giây** → 10.000 mẫu × 3 epoch ≈ 5 giờ: không thực tế | đo 10/10 (`training/runs/smoke_t1_e5small`) |
| Huấn luyện trên **T4 16 GB** (Colab/Kaggle miễn phí) | chưa có số đáng tin cho 10k mẫu; **đo 200 bước rồi ngoại suy** | tài liệu không có số tin cậy [NOT FOUND] |
| T2-gen QLoRA Qwen3 | r = 32, α = 16, 2 epoch, lr 1e-4 cosine, AdamW 8-bit, batch 5, Unsloth + TRL; **trộn 1:1 ca gốc và ca nhiễu số** — học trò 8B chỉ học dữ liệu sạch đạt **8,65%** trên ca nhiễu; T4 không có bf16, giới hạn ~2k token | Aarnes & Setty 2026 (arXiv:2610.00689) [VERIFIED] |
| Suy luận CPU sau ONNX int8 | nhanh hơn 2–2,5 lần, mất ≤ 0,3 điểm (DistilBERT, RoBERTa-base — đo trên CPU máy chủ AVX-512) | Hugging Face Optimum [VERIFIED] |
| Mục tiêu suy luận học trò T1/T2 trên laptop | ≤ 50 ms/câu → 156 tuyên bố × 5 đoạn trong < 1 phút | mục tiêu |

---

## 5. Cổng — học trò chỉ thay thầy/luật khi

| Học trò | Điều kiện (trên gold, khoảng tin cậy theo doanh nghiệp) |
| --- | --- |
| T1 | macro-F1 ≥ luật **và** recall lớp tuyên bố ≥ luật + 10 điểm; precision không giảm quá 5 điểm |
| T2 | độ chính xác đối sánh ≥ L1 (mô hình đám mây đã che) − 3 điểm; **tỷ lệ xác nhận sai ≤ L1** |
| T3 | như chốt chặn hiện có: SUPPORTS precision ≥ 0,80, CONTRADICTS ≥ 0,90 (`configs/measurement_decisions.yaml`) |

Ghi các ngưỡng này vào `configs/measurement_decisions.yaml` (phiên bản mới) **trước** khi có số.

---

## 6. Trạng thái 10/10 và việc tiếp

| Đã có | |
| --- | --- |
| `masking.py` | che số + tên (bản thử của module sản phẩm `src/quantum_gw/privacy/`) |
| `build_claim_sentences.py` | 66.539 câu, nhãn yếu, chia theo doanh nghiệp |
| `teacher_label.py` | nhãn thầy T1/T2, che số, bộ nhớ đệm, trần lời gọi; lô thử 400 câu: luật và thầy đồng ý 73%; thầy thấy luật **trích thừa** (34/120 câu luật nhận là "không phải tuyên bố") và **bỏ sót** (36/160 câu môi trường luật từ chối là tuyên bố thật) |
| `train_classifier.py` | huấn luyện + chấm theo doanh nghiệp; chạy thử CPU thành công (độ chính xác chưa có nghĩa: 191 mẫu) |

| Việc tiếp | Ai | Khi |
| --- | --- | --- |
| Gold T1: lô 1 của bộ `audit` và `hpg` (79 câu) cả ba gán độc lập → `consensus` → họp 1 chốt quy ước → các lô còn lại → `merge` → `report`; lịch ở mục 10 của tài liệu quy trình | Quỳnh, Thảo, Nhân | trước 22/10 |
| Đưa các quy ước đã chốt ở lô 1 (tổ chức khác, câu cơ chế chung, mục tiêu chỉ có năm) vào `CLAIM_PROMPT` → `teacher-claim-v2` **trước** khi chạy 4.000 câu, để thầy và gold cùng một định nghĩa | Nhân | sau buổi trọng tài |
| Nhãn thầy 4.000 câu × 3 lần chạy; tính điểm nhất quán | Nhân | ~US$0,5 |
| Huấn luyện T1 trên T4 (mDeBERTa-xnli, e5-base) | Nhân | sau gold T1 |
| `eval_student.py`: học trò vs luật vs thầy trên gold + 51 ca | Nhân | cùng lúc |
| Nhãn thầy T2 từ các phiên công khai (che số); huấn luyện cross-encoder | Nhân | sau L1 vào sản phẩm |

`training/data/` và `training/runs/` không commit (dựng lại được; lô nhãn thầy nên lưu ra ngoài khi đã tốn tiền).
