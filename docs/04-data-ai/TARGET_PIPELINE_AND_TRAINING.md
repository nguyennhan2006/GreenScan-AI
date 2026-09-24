# Luồng đích và kế hoạch huấn luyện mô hình

**Ngày:** 2026-09-24 · **Loại tài liệu:** thiết kế hướng tới, không phải mô tả hiện trạng
**Hiện trạng đối chiếu:** [RESEARCH_PROGRAM_2026-09-22.md](../00-project/RESEARCH_PROGRAM_2026-09-22.md) (audit code) · [DATA_LAYERS.md](DATA_LAYERS.md) (contract dữ liệu)
**Ràng buộc còn hiệu lực:** D-2026-09-18-02 — *không fine-tune trước Bán kết 25/10*. Tài liệu này là kế hoạch sau mốc đó, cộng phần dùng LLM không cần huấn luyện có thể bật sớm hơn.

Mỗi khối dưới đây mang một nhãn:

| Nhãn | Nghĩa |
| --- | --- |
| ✅ **ĐANG CHẠY** | Có trong đường chạy mặc định hôm nay |
| 🔌 **CÓ CODE, CHƯA BẬT** | Adapter tồn tại, chưa cài/chưa đo |
| 🧪 **ĐANG NGHIÊN CỨU** | Chưa có code; có thiết kế và điều kiện nghiệm thu |
| 🚫 **CỐ Ý KHÔNG LÀM** | Đã cân nhắc và loại, kèm lý do |

---

## 1. Nguyên tắc kiến trúc quyết định mọi thứ còn lại

> **Mô hình ngôn ngữ được phép *đọc*, không được phép *kết luận*.**

Chia đôi bài toán:

| Phần | Bản chất | Ai làm | Vì sao |
| --- | --- | --- | --- |
| **Đọc hiểu ngôn ngữ** — câu này có phải tuyên bố môi trường không; chỉ số là gì; con số này là tỷ trọng hay mức thay đổi; phạm vi nào | Mơ hồ, phụ thuộc ngữ cảnh, tiếng Việt chuyên ngành | **LLM** (và đây là chỗ huấn luyện có ích) | Luật tay không phủ nổi biến thể ngôn ngữ; đây đúng là việc mô hình giỏi |
| **Phán quyết** — hai số có so được không, lệch bao nhiêu là mâu thuẫn, verdict nào, rủi ro bao nhiêu | Phải tái lập, phải giải thích được, phải audit được | **Code deterministic** | Một kết luận về doanh nghiệp phải chỉ ra được *phép tính nào đã chạy*; mô hình sinh ra con số là không kiểm chứng được |

Hệ quả trực tiếp: **không bao giờ huấn luyện mô hình sinh verdict.** Dữ liệu gán nhãn không dùng để dạy mô hình nói "CONTRADICTED", mà để dạy mô hình **điền đúng các trường** rồi để luật quyết định. Đây cũng là câu trả lời cho phản biện *"AI của các em có bịa không"*: phần bịa được thì không được quyền quyết, phần quyết thì không bịa được.

---

## 2. Luồng đích — mười bước, chỉ rõ chỗ nào có mô hình

```text
  PDF / scan
      │
 ①  Nhận & kiểm tra tài liệu                         ✅ code
      │   vai trò: nguồn tuyên bố | bằng chứng | tham chiếu
      ▼
 ②  Đọc tài liệu  ──► lớp chữ có sẵn                 ✅ code
      │             └► trang scan → OCR              ✅ code (chưa chạy tại chỗ)
      │             └► bảng/biểu đồ phức tạp → VLM   🧪 Qwen2.5-VL
      ▼
 ③  Cắt đơn vị văn bản + giữ trang/ô bảng            ✅ code (ô bảng 🧪)
      ▼
 ④  Nhận diện câu đáng kiểm chứng                    ✅ luật  →  🧪 mô hình nhỏ
      │   (claim admissibility)
      ▼
 ⑤  Chuẩn hoá tuyên bố thành cấu trúc                🔌 gateway sẵn, chưa gọi
      │   5 thuộc tính + 6 chiều của mỗi con số      →  🧪 mô hình nhỏ (SFT)
      ▼
 ⑥  Truy xuất bằng chứng                             ✅ BM25 + n-gram + RRF
      │                                              🔌 + BGE-M3, 🔌 + reranker
      ▼
 ⑦  Kiểm chứng
      ├─ so số: xét 6 chiều rồi mới tính              ✅ deterministic — KHÔNG dùng LLM
      ├─ lập trường đoạn văn: từ điển cue             ✅ luật
      │    └ trường hợp bất định                     🔌 LLM judge (đang tắt) → 🧪 NLI tiếng Việt
      └─ verdict 5 trạng thái + abstain               ✅ luật
      ▼
 ⑧  Đối chiếu pháp lý (policy-as-code)               ✅ hạ tầng · 🧪 rule có điều kiện kiểm được
      ▼
 ⑨  Chấm rủi ro: 9 thành phần + 3 chiều tách         ✅ luật
      ▼
 ⑩  Cổng G0–G7 → hồ sơ bằng chứng → người xét duyệt  ✅ code
           │
           └──► phản hồi của reviewer quay lại làm dữ liệu huấn luyện  🧪
```

Ba chỗ có mô hình, và **chỉ ba chỗ**: bước ④⑤ (đọc cấu trúc), bước ⑥ (biểu diễn ngữ nghĩa để tìm bằng chứng), bước ⑦ nhánh bất định (lập trường). Bước ⑦ phần số học và bước ⑨ vĩnh viễn không có mô hình.

---

## 3. Mô hình nào cho việc nào

### 3.1 Đang dùng hôm nay

| Hạ tầng | Trạng thái |
| --- | --- |
| Model Gateway, định tuyến theo task (`configs/routing.yaml`, 8 task) | ✅ có |
| Ollama local — `qwen3:8b` | 🔌 đã cài, chưa chạy trong pipeline |
| FPT Marketplace — GLM-5.2, DeepSeek-V4-Flash, Qwen3.6-27B, Llama-3.3-70B, Qwen2.5-VL-7B, bge-reranker-v2-m3, Vietnamese_Embedding | 🔌 có key, chưa đo |
| Đường chạy mặc định | ✅ **heuristic, LLM tắt hoàn toàn** |

### 3.2 Phân bổ đích

| Bước | Mô hình đề xuất | Vì sao cỡ đó | Chạy ở đâu |
| --- | --- | --- | --- |
| ④ Nhận diện câu đáng kiểm chứng | **Qwen3 1.7B** (phân loại 4 lớp) | Khối lượng rất lớn (mỗi báo cáo hàng nghìn câu); quyết định đơn giản; 1.7B lượng tử hoá chạy được trên CPU | Local |
| ⑤ Chuẩn hoá thành JSON có schema | **Llama 3.2 3B** hoặc **Qwen3 1.7B** sau SFT | Điền form theo khuôn, không cần suy luận sâu — đúng việc mô hình nhỏ làm tốt sau khi được dạy khuôn | Local |
| ⑥ Biểu diễn để truy xuất | **BGE-M3** (đa ngôn ngữ, dense+sparse) + **bge-reranker-v2-m3** | Không phải LLM sinh; chỉ mã hoá | Local / TEI |
| ⑦ Lập trường ca khó | **NLI tiếng Việt** (PhoBERT/ViDeBERTa fine-tune) hoặc LLM 8B | Chỉ chạy trên phần dư sau khi từ điển và số học bó tay (~5–10% cặp) | Local |
| ⑧ Suy luận pháp lý (soạn *draft* rule) | Mô hình lớn (GLM-5.2 / Llama-3.3-70B) | Chạy **offline khi soạn rule**, người duyệt trước khi vào production; không chạy lúc phân tích | FPT |
| ⑩ Viết báo cáo tiếng Việt | Mô hình lớn | 1 lần/run, chất lượng văn quan trọng hơn độ trễ | FPT, có thể tắt |
| ② Trang scan / bảng ảnh | **Qwen2.5-VL-7B** | Chỉ khi lớp chữ không đọc được | FPT |

**Vì sao mô hình nhỏ 1.7B–3B chứ không phải mô hình lớn cho ④⑤:** ba lý do đo được — (1) khối lượng: 15.658 đoạn/21 DN, gọi mô hình lớn cho từng câu là không khả thi về chi phí lẫn thời gian; (2) tính riêng tư: tài liệu chưa công bố của khách hàng phải xử lý tại chỗ, mà tại chỗ thì máy không có GPU lớn; (3) bản chất công việc là **điền khuôn có schema**, không phải suy luận mở — đây chính là loại việc fine-tune một mô hình nhỏ đuổi kịp mô hình lớn.

---

## 4. Dữ liệu biến thành dữ liệu huấn luyện như thế nào

Ba tầng dữ liệu ([DATA_LAYERS.md](DATA_LAYERS.md)) đã được thiết kế sẵn cho việc này. Mỗi tầng cho ra một loại ví dụ huấn luyện khác nhau:

| Tầng | Cho ra | Dùng huấn luyện bước nào |
| --- | --- | --- |
| **clean** (15.658 đoạn) | Câu + vị trí + ngữ cảnh đoạn | Đầu vào của mọi ví dụ |
| **extract → claim** (7.960 ứng viên) | Câu **là** tuyên bố | Lớp dương của bước ④; đầu vào của bước ⑤ |
| **extract → rejected_sentence** | Câu **không phải** tuyên bố, **kèm lý do** | **Lớp âm của bước ④ — có sẵn, không phải gán thêm** |
| **extract → numeric_facts** | Con số + 6 chiều do luật đọc | Nhãn bạc (silver) cho bước ⑤, người soát lại |
| **gold labels** (`label`, `annotator`) | Nhãn người đã trọng tài | **Chỉ dùng để đánh giá**, không dùng để huấn luyện |
| **quyết định của reviewer** (append-only) | Người sửa chỗ nào, sửa thành gì | Vòng lặp cải thiện sau khi có người dùng thật |

Quyết định quan trọng: **nhãn người là để đo, nhãn máy là để dạy.** Nếu lấy gold đi huấn luyện thì không còn gì để đo trung thực. Với 60–150 cặp gold, con số đó quá quý để tiêu vào training.

### 4.1 Ba bộ dữ liệu cần xây

| Bộ | Kích thước | Nguồn | Dùng để |
| --- | --- | --- | --- |
| **A. Câu đáng kiểm chứng** | 1.000–3.000 câu (bạc) + 100 câu (vàng) | Bạc: luật hiện tại + mô hình lớn gán; Vàng: Quỳnh/Thảo | Huấn luyện + đo bước ④ |
| **B. Thuộc tính tuyên bố** | 500–1.500 cặp (câu → JSON) | Bạc: mô hình lớn; Vàng: 60–150 cặp người trọng tài | Huấn luyện + đo bước ⑤ |
| **C. Cặp số so được / không so được** | 300–500 cặp (bạc) + 50 (vàng) | Sinh tự động từ `numeric_facts` đã có + người dán nhãn | Huấn luyện + đo phần đọc 6 chiều |

Bốn lớp nhãn của bộ A (`AUDITABLE` / `VAGUE_ENVIRONMENTAL` / `NON_CLAIM` / `BOILERPLATE`) và bốn lớp của bộ C (`COMPARABLE` / `COMPARABLE_AFTER_NORMALIZATION` / `NOT_COMPARABLE` / `AMBIGUOUS`) đã định nghĩa trong RESEARCH_PROGRAM (RQ1, RQ3).

### 4.2 Khuôn ví dụ huấn luyện (bước ⑤)

```jsonc
// input cho mô hình: câu + đoạn chứa nó (ngữ cảnh), không có gì khác
{
  "instruction": "Đọc câu tuyên bố môi trường và điền vào khuôn JSON. Chỉ điền cái câu nói rõ; không suy đoán. Không có thì để null.",
  "input": {
    "cau": "Trong năm 2025, tổng lượng phát thải khí nhà kính của Tập đoàn là 23.474.480 tCO2e, giảm 4% so với năm 2024.",
    "doan_chua_cau": "... (đoạn 3 câu để lấy ngữ cảnh) ..."
  },
  "output": {
    "chi_so": "phat_thai_knk",
    "huong": "giam",
    "ky": "2025",
    "nam_goc": "2024",
    "pham_vi": {"to_chuc": "tap_doan", "scope": null},
    "so_lieu": [
      {"gia_tri": 23474480, "don_vi": "tCO2e", "co_so_do": "tuyet_doi",
       "ranh_gioi": "tap_doan", "cong_nghe": null, "chi_so_con": null, "la_muc_tieu": false},
      {"gia_tri": 4, "don_vi": "%", "co_so_do": "muc_thay_doi",
       "ranh_gioi": "tap_doan", "cong_nghe": null, "chi_so_con": null, "la_muc_tieu": false}
    ],
    "la_cam_ket_tuong_lai": false,
    "ngon_tu_mo_ho": []
  }
}
```

Đầu ra **không có verdict, không có điểm rủi ro**. Mô hình chỉ đọc; luật quyết định.

### 4.3 Nguồn nhãn bạc: chưng cất từ mô hình lớn

Quy trình 🧪:

```text
7.960 ứng viên  ──► lọc theo từ vựng + sát chủ đề  ──► ~2.000 câu
                                                          │
                              GLM-5.2 / Llama-3.3-70B trên FPT
                              (prompt có schema + 8 ví dụ mẫu)
                                                          │
                                        ~2.000 JSON nhãn bạc
                                                          │
                     luật hiện tại chạy song song → so hai bên
                                                          │
              khác nhau → xếp hàng cho người soát (đây là chỗ đáng soát nhất)
                                                          │
                              bộ huấn luyện đã lọc mâu thuẫn
```

Lợi ích: người chỉ soát phần **hai nguồn bất đồng** — kinh nghiệm cho thấy đó là 15–25% số câu, tiết kiệm phần lớn công. Nhãn vàng vẫn giữ riêng, không trộn.

---

## 5. Công thức huấn luyện đề xuất

| Hạng mục | Lựa chọn | Lý do |
| --- | --- | --- |
| Mô hình nền | Qwen3 1.7B (ưu tiên) · Llama 3.2 3B (đối chứng) | Qwen có dữ liệu tiếng Việt/Trung tốt hơn ở cỡ nhỏ; Llama để so, không tin một mô hình duy nhất |
| Phương pháp | **QLoRA** (4-bit, rank 16–32, alpha 32, dropout 0.05) trên các lớp attention + MLP | Máy dev không có GPU lớn; LoRA đủ cho việc học khuôn đầu ra |
| Độ dài chuỗi | 1.024 token (câu + đoạn ngữ cảnh + schema) | Đủ cho một câu và đoạn chứa nó |
| Số epoch | 2–3, dừng sớm theo tập dev | Dữ liệu ít, quá 3 epoch là học thuộc |
| Kích thước tập | Bắt đầu 500, tăng dần 1.000 → 1.500, vẽ đường cong học | Để biết **thêm dữ liệu còn có ích không** — câu này BGK hay hỏi |
| Định dạng ràng buộc | Sinh có ràng buộc ngữ pháp JSON (grammar-constrained) | Mô hình nhỏ hay sai cú pháp JSON; ràng buộc loại hẳn lỗi này thay vì retry |
| Suy luận | llama.cpp / Ollama, lượng tử Q4_K_M | Chạy CPU tại chỗ |
| Chia tập | **Hold-out theo doanh nghiệp**, không theo câu | Câu cùng một báo cáo rất giống nhau; chia theo câu là tự lừa mình |

**Điều kiện bắt buộc trước khi bấm nút train** (nếu thiếu một điều, chưa train):

1. Có tập dev/test **theo doanh nghiệp chưa từng thấy**, tối thiểu 3 DN.
2. Có kết quả **B1 few-shot không huấn luyện** để so — nếu prompt tốt đã đủ thì không cần train.
3. Có ngân sách độ trễ rõ ràng: mô hình phải đạt **≤ 1,5 giây/câu trên CPU**, nếu không thì vô dụng trong sản phẩm.
4. Bộ 44 trap hiện tại vẫn phải xanh sau khi thay đổi.

---

## 6. Thang thí nghiệm — chỉ lên bậc khi đo được lợi ích

| Bậc | Cấu hình | Đo gì | Điều kiện lên bậc kế |
| --- | --- | --- | --- |
| **B0** | Luật hiện tại (đang chạy) | F1 từng trường, verdict accuracy, thời gian | — (đây là mốc so) |
| **B1** | B0 + LLM few-shot (không train), Qwen3 1.7B local | Như trên + độ trễ/câu, tỷ lệ JSON hỏng | Hơn B0 ≥ 15 điểm F1 thuộc tính |
| **B2** | B1 + SFT trên nhãn bạc đã lọc | Như trên | Hơn B1 ≥ 5 điểm F1 **và** ≤ 1,5 s/câu |
| **B3** | B2 + BGE-M3 + reranker ở bước ⑥ | Recall@5/@10, verdict accuracy | Chỉ giữ nếu verdict accuracy tăng, không chỉ ranking đẹp hơn |
| **B4** | B3 + NLI tiếng Việt cho lập trường | Stance macro-F1 trên 44 trap + gold | Hơn heuristic ≥ 10 điểm |

Quy tắc: **mỗi bậc đổi đúng một thứ**. Bật đồng thời LLM + dense retrieval + reranker thì điểm có tăng cũng không biết nhờ cái nào.

Kết quả âm là kết quả hợp lệ. Nếu B2 không hơn B1, bản trình bày nói đúng như vậy — đó là một phát hiện, không phải thất bại.

---

## 7. Những thứ cố ý không làm 🚫

| Không làm | Vì sao |
| --- | --- |
| Fine-tune mô hình **sinh verdict** | Verdict phải giải thích được bằng phép tính và quy tắc; một mô hình nói "CONTRADICTED" không chỉ ra được vì sao |
| Dùng nhãn LLM làm **gold** | Mất luôn thước đo; mọi con số sau đó là tự chấm |
| Fine-tune trước khi có hold-out theo DN | Không phân biệt được "học được" và "học thuộc" |
| Huấn luyện trên tài liệu khách hàng | Cam kết với khách hàng; dữ liệu khách chỉ để phân tích, không vào tập huấn luyện |
| Nhét toàn bộ PDF vào một mô hình lớn và hỏi "có greenwashing không" | Không truy vết được, không tái lập, và nghiên cứu RAG cho thấy nhiều ngữ cảnh nhiễu làm kết quả tệ đi |
| GraphRAG / đa tác tử trước Bán kết | Kiểm chứng claim là truy xuất cục bộ theo sự kiện, không phải tổng hợp toàn cục (D-2026-09-18-02) |

---

## 8. Lộ trình gắn với mốc thi

| Giai đoạn | Việc | Trạng thái đích |
| --- | --- | --- |
| Tới **10/10** (product freeze) | Gold ≥ 60 cặp · bộ A/B/C khởi động · **B1 few-shot** đo trên 30 claim · bật + đo BGE-M3 | Không train gì. Có bảng so B0 vs B1 |
| 11/10 – **25/10** (Bán kết) | Đóng băng. Chỉ sửa lỗi | Trình bày: kiến trúc + B0/B1 có số |
| 26/10 – 10/11 (nếu vào Chung kết) | Chưng cất nhãn bạc → **B2 SFT Qwen3 1.7B** · gold lên 100–150 · B3 retrieval | Có đường cong học + bảng 4 bậc |
| Sau cuộc thi | B4 NLI · rule pháp lý mở rộng · vòng lặp phản hồi reviewer | — |

---

## 9. Câu trả lời ngắn cho ba câu hỏi hay gặp

**"Các em dùng AI gì?"** — Mô hình ngôn ngữ làm phần đọc hiểu: nhận diện câu nào là tuyên bố và điền tuyên bố đó vào cấu trúc gồm chỉ số, kỳ, năm gốc, phạm vi và các con số kèm ý nghĩa. Phần quyết định — hai số có so được không, lệch bao nhiêu là mâu thuẫn, kết luận nào — do luật deterministic làm, để mỗi kết luận chỉ ra được phép tính đã chạy.

**"Dữ liệu crawl để train gì?"** — Trước hết là hạ tầng đo lường: nó sinh ra hàng đợi gán nhãn và bộ chuẩn để biết hệ thống sai ở đâu. Sau đó mới là dữ liệu huấn luyện, và chỉ cho phần đọc cấu trúc, theo ba bộ A/B/C ở mục 4. Các câu hệ thống **loại bỏ** cũng được giữ kèm lý do — chúng là lớp âm có sẵn, không phải gán lại.

**"Sao không dùng một mô hình lớn cho gọn?"** — Ba lý do đo được: khối lượng (hàng nghìn câu mỗi báo cáo), tính riêng tư (tài liệu chưa công bố phải xử lý tại chỗ, tại chỗ thì không có GPU lớn), và bản chất công việc là điền khuôn có sẵn schema — loại việc mà mô hình nhỏ sau khi được dạy đuổi kịp mô hình lớn với chi phí thấp hơn nhiều.

---

## 10. Bản tổng quan để trình bày

Khi cần một trang duy nhất cho slide hoặc để vẽ sơ đồ: [../07-presentation/PIPELINE_DIAGRAM_BRIEF.md](../07-presentation/PIPELINE_DIAGRAM_BRIEF.md) — cùng pipeline, diễn đạt cho người nghe, kèm ngân sách huấn luyện theo giả định T4 không giới hạn / A100 10 giờ (khác giả định CPU của tài liệu này: M2 có thể lên 7–8B).

## 11. Liên quan

[RESEARCH_PROGRAM_2026-09-22.md](../00-project/RESEARCH_PROGRAM_2026-09-22.md) (RQ1, RQ2, RQ3, RQ6, RQ7) · [DATA_LAYERS.md](DATA_LAYERS.md) · [EVALUATION.md](EVALUATION.md) · [ACCURACY_IMPROVEMENT_PLAYBOOK.md](ACCURACY_IMPROVEMENT_PLAYBOOK.md) · [../../configs/routing.yaml](../../configs/routing.yaml) · [LABELING_CONVENTIONS.md](../../data/gold/LABELING_CONVENTIONS.md)
