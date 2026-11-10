# R5: AI/NLP — lý thuyết và tài liệu nền cho từng tầng pipeline

*Lập 04/11/2026 cho Chung kết 10/11. Đường dẫn tính từ gốc repo `D:\Sinh viên CNhan\AI quantum\docs\greenscan-ai\GreenScan-AI\` trừ khi ghi khác.*

*Nguồn đã đọc (đường dẫn/URL), phần không đọc được và vì sao.*

**Đã đọc toàn văn**
- `docs/08-knowledge/05_AI_NLP_VA_DO_LUONG.md`; `docs/04-data-ai/RETRIEVAL_POLICY.md`; `docs/04-data-ai/VERIFICATION_POLICY.md`; `docs/04-data-ai/TARGET_PIPELINE_AND_TRAINING.md`; `docs/07-presentation/nghien-cuu/P01_doc_tai_lieu.md` … `P06_lap_truong_LLM.md`, `P13_huan_luyen.md`.
- Paper (5 trang): `C:\Users\ASUS\AppData\Local\Temp\claude\1b0eaa27687c19cd\f7145077-5467-44ec-9ed7-1bf1914d11ab\scratchpad\txt\optimizing_rag_elasticsearch.txt`. Đây là Chen, Qi, Bao, Wei, Hu, Zheng, *Optimizing Retrieval-Augmented Generation with Elasticsearch for Enhanced Question-Answering Systems*, arXiv:2410.14167 (18/10/2024, cs.IR), https://arxiv.org/abs/2410.14167. Mã arXiv và tác giả đã đối chiếu bằng tìm kiếm web ngày 04/11.
- `docs/08-knowledge/sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md`: đọc theo mục toàn bộ phần thân (§0 tới Phụ lục, dòng 1–1170).

**Đọc thêm để đối chiếu số mới và hiện trạng code**
- `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md` §0–5 và §10.
- `experiments/AG-1/README.md` §5 (phần 01/11 17:00) và §6–8.
- `docs/00-project/ARCHITECTURE_INVARIANTS.md`: mười bất biến và bảng cấm.
- Code: `src/quantum_gw/settings.py` dòng 128–140 (RetrievalSettings); `src/quantum_gw/retrieval/hybrid.py` dòng 40–165; `src/quantum_gw/retrieval/rerank.py` (tên lớp); `src/quantum_gw/utils/text.py` dòng 30–31; `experiments/AG-1/irlib.py` dòng 96–118 (`ground()`); `experiments/AG-1/llm.py` (tham số giải mã).

**Không đọc được, hoặc không đọc**
- Paper ES-RAG: các công thức (TF-IDF, cosine, điểm ES, top-K, điểm có trọng số) là ảnh nên bản text bị mất, chỉ còn lời mô tả quanh công thức. Không có Hình 1 (biểu đồ đường). Bảng 1 được dựng lại từ các dòng chữ rời; thứ tự cột Acc/F1/Recall khớp câu trong bài ("accuracy 68.29%, F1 68.42%, recall 68.13%").
- Danh mục tham khảo của tổng quan (dòng 1171–1402): không đọc hết, chỉ dùng để tra.
- Bản gốc các paper được nhắc trong tổng quan: không mở. Số liệu ngoài lấy theo tổng quan, vốn đã được đội đối chiếu ngày 05/10/2026.
- Không có PDF nào cần trích thêm, nên thư mục `scratchpad\R5\` không được dùng.

---

## 1. Tóm tắt từng tài liệu

### 1.1 `05_AI_NLP_VA_DO_LUONG.md` (06/10/2026)
- **Là gì:** bản rút gọn 6 mục của tổng quan, dùng làm kịch bản hỏi đáp.
- **Luận điểm chính kèm số:**
  - Sáu lựa chọn kiến trúc khớp với tài liệu: pipeline phân rã; số học do code (NumPert −62 %, FinQA ≥ 3 bước 22,78 %, FinDVer 77,2 so với 93,3); INSUFFICIENT do luật; gộp nhãn tất định (AVeriTeC, Climate-FEVER); đo truy xuất tách khỏi kiểm chứng (Zhao, TOSEM 2026); người chốt kết luận.
  - Bốn cảnh báo:
    - Bộ trích tuyên bố bằng từ khoá hụt recall: SVM n-gram F1 69–71 so với transformer 84–85.
    - κ ≥ 0,7 là mục tiêu cao.
    - LLM-as-judge có thiên lệch.
    - Calibration của LLM không đáng tin (ESGReveal 76,9 %).
  - Bảng embedding, reranker và NLI tiếng Việt, kèm giấy phép.
  - Đo trên gold 60–100 cặp:
    - khoảng Wilson rộng ±6–11 điểm;
    - κ = 0,70 có CI [0,52; 0,88];
    - chênh tối thiểu phát hiện được (MDE) 10–17 điểm khi n = 80;
    - bootstrap theo doanh nghiệp; pooling bias.
  - 8 câu được nói, 10 câu không được nói.
- **Liên quan:** nguồn trực tiếp cho phần hỏi đáp.
- **Giống và khác hiện trạng:** thiết kế vẫn đúng. Có ba chỗ đã lệch hiện trạng:
  - tài liệu giả định có gold người, thực tế 0;
  - coi GLM-5.2 qua FPT là đường LLM, nhưng khoá FPT hỏng từ 31/10;
  - coi Vietnamese_Embedding qua FPT là đang dùng, nhưng cấu hình là `lite`.

### 1.2 Tổng quan tài liệu AI/NLP 2019–2026 (05/10/2026)
**Là gì:** tổng quan có nhãn ADOPT / TEST / AVOID / CONTEXT cho từng nguồn, nguồn được đối chiếu ngày 05/10. Gồm 7 mục và phụ lục.

**§1 Greenwashing**
- Chưa có bộ dữ liệu greenwashing đã xác minh. Survey Calamai v2 (2026) khuyên dùng pipeline phân rã, có người giám sát.
- Environmental Claim Detection: 2 647 câu, α = 0,47. SVM đạt 69,1–70,9, RoBERTa-large 84,9; khoảng cách recall tới 25 điểm.
- NetZero: trích năm gốc bằng QA chỉ đạt 0,68.
- ChatReport: κ khi gán nhãn hallucination là 0,54 / 0,21.
- Climinator: 96,4 % nhị phân, nhưng đoán lớp đa số đã đạt 90,3 %; với 12 lớp chỉ 34,5 %.
- ClimRetrieve: BM25 0,113, embedding tốt nhất 0,167 (0,179 khi viết lại truy vấn); tác giả gọi kết quả là "lower bound".
- A3CG: mô hình có giám sát (47,5) hơn LLM (40–42) trên nhóm chưa thấy.
- EmeraldMind: 94,2 % đúng nhưng chỉ ở độ phủ 19,5 %; định nghĩa overall = accuracy × coverage.
- Chuang 2025: điểm do LLM chấm bị greenwash. Vinella: AVOID vì nhãn tự sinh.

**§2 Kiểm chứng**
- FEVER: 185 445 tuyên bố, κ = 0,684. Pipeline tốt nhất chỉ 31,87 % khi phải đúng cả bằng chứng.
- SciFact: gold lưu câu rationale.
- AVeriTeC:
  - có lớp Conflicting Evidence/Cherry-picking và quy tắc gộp nhãn tất định;
  - shared task 2024 đạt 63 %; năm 2025, khi giới hạn mô hình open-weights trên 1 GPU 23 GB, chỉ đạt 33,17 %.
- Climate-FEVER: có nhãn DISPUTED. Mô hình huấn luyện trên FEVER chỉ đạt 38,78 % (so với 77,69 % trên FEVER dev). Người gán nhãn có dung sai số ngầm.
- Phân rã tuyên bố: FActScore và các phản biện.
- Tuyên bố số:
  - QuanTemp: 15 514 tuyên bố, macro-F1 tốt nhất 58,32.
  - NumPert: accuracy giảm tới 62 %.
  - Aarnes & Setty 2026: frontier khoảng 74 %, Qwen3 nhỏ tinh chỉnh PEFT đạt 98,7 %.
  - VitaminC: bằng chứng tương phản.
- Bảng và tài chính: TabFact, FEVEROUS (18 %), FinQA, TAT-QA, FinDVer (77,2 so với 93,3), FinanceBench (81 % sai hoặc từ chối), DocMath.
- RAG:
  - Lost in the Middle: hiệu năng hình chữ U.
  - Zhao (TOSEM 2026): có lỗi ở 12,6 % mẫu dù tài liệu hoàn hảo; 5–10 tài liệu là tối ưu.
  - Sufficient Context (Joren, ICLR 2025): LLM lớn trả lời sai thay vì từ chối.

**§3 Lỗi của LLM và phối hợp người–AI**
- Trích dẫn bịa: chỉ 51,5 % câu được trích dẫn hỗ trợ đầy đủ; ALCE thiếu trích dẫn 50 %. RAGTruth.
- MiniCheck 0,8B đạt 75,0, gần GPT-4o (75,9), nhưng chỉ tiếng Anh.
- Calibration: Xiong (độ tự tin tự khai thì quá cao); Kadavath (P(True)); Kamath (56 % so với 48 % ở accuracy 80 %).
- LLM-as-judge: Wang (66/80); MT-Bench; Shi; Bavaresco; Panickssery.
- Abstention: survey của Wen; Geifman (risk–coverage); Mohri (conformal).
- Người–AI: Warren CHI 2025/2026; Bansal; Vasconcelos; Commerford (algorithm aversion).

**§4 Tiếng Việt**
- VN-MTEB (dịch máy). Thứ hạng đảo chiều trên Zalo legal (số tự báo).
- PhoRanker, ViRanker.
- mDeBERTa-xnli 0,793; ViANLI chỉ 45,5 %.
- ViFactCheck (giấy phép MIT, κ = 0,83). ViWikiFC: BM25 tìm bằng chứng cho NEI chỉ đạt 56,67 %.
- PhoBERT v1 dùng MIT, v2 dùng AGPL.
- OCR: Tesseract nhầm dấu chồng; phải chuẩn hoá NFC.

**§5 Trích KPI và đọc PDF**
- ESGReveal 76,9 %.
- Beck 2025: LLM gợi ý, 2 người kiểm, rồi phân xử.
- Scope3Trace: hybrid luật–LLM, thiết kế gần GreenScan nhất.
- Schmoll & Jatowt: LLM kém ở KPI định lượng; metadata ngắn cho kết quả tốt hơn cả báo cáo.
- Docling, TableFormer, TATR. Adhikari & Agarwal: PyMuPDF trích text tốt, TATR tốt nhất cho bảng tài chính.

**§6 Đo lường**
- Card 2020 (power); Miller 2024 (SE có cụm lớn gấp 3).
- Bootstrap theo cặp; khoảng Wilson.
- Các bẫy của κ.
- Chia theo nhóm, rò rỉ dữ liệu (Lewis: 30 % câu hỏi test trùng gần với train).
- Pooling bias: BEIR Hole@10; ANCE từ 0,654 lên 0,735 sau khi gán nhãn bổ sung.

**§7 Ý nghĩa cho GreenScan:** bảng dữ liệu và mô hình kèm giấy phép, 8 phát biểu được nói, 10 điều không được nói, việc cần làm trước freeze.

**Đánh giá:**
- **Liên quan:** căn cứ học thuật cho mọi tầng của pipeline.
- **Giống:** lập luận "luật quyết".
- **Khác:** viết trước khi có GS-Bench và AG-1/AG-2; vẫn giả định có gold người và GLM-5.2.

### 1.3 Paper ES-RAG (arXiv:2410.14167) — đọc toàn văn
**Là gì:** preprint 5 trang. Bài dùng Elasticsearch (ES) làm bộ truy xuất cho RAG và thử trên SQuAD 2.0.

**Phương pháp** (theo lời mô tả, công thức bị mất):
1. TF-IDF kèm cosine.
2. "Điểm ES" dạng BM25: k1 chỉnh ảnh hưởng của tần suất từ, K chỉnh theo độ dài tài liệu (b, avgdl).
3. Chọn top-K.
4. Điểm tổng có trọng số `S'_i = Σ_j w_j·s_ij`, trộn cosine với BM25.
- Tiền xử lý: bỏ thẻ HTML, đưa về chữ thường, **bỏ stopword**.
- Nạp dữ liệu vào cụm ES, cấu hình bộ tách từ và mapping.
- Thêm một bộ câu hỏi riêng: kiến thức chung, thuật ngữ, thông tin hiếm (long-tail).

**Kết quả (Bảng 1, trang 4, đơn vị %, Acc / F1 / Recall)**

| Hệ | Acc | F1 | Recall |
|---|---|---|---|
| RAG | 65,51 | 66,11 | 65,72 |
| BM25-RAG | 66,32 | 66,56 | 66,47 |
| TF-IDF-RAG | 67,78 | 67,63 | 67,23 |
| ES-RAG | 68,29 | 68,42 | 68,13 |

ES-RAG hơn TF-IDF-RAG 0,51 điểm Acc, hơn BM25-RAG 1,97 điểm và hơn RAG thường 2,78 điểm.

**Hạn chế (tự đọc, dùng khi bị hỏi về paper):**
1. Chênh 0,51 điểm mà không có khoảng tin cậy, không có seed, không kiểm định. Theo Card 2020 thì không đủ để kết luận.
2. Bài định nghĩa precision/recall cho *tài liệu truy xuất*, nhưng bảng lại báo "Acc" không được định nghĩa và không có cột precision.
3. Không nói dùng LLM nào, prompt gì, k bao nhiêu, chấm câu trả lời ra sao.
4. Điểm mặc định của ES chính là BM25 [KIẾN THỨC NỀN: từ ES 5.0, mặc định k1 = 1,2; b = 0,75]. Vì vậy BM25-RAG và ES-RAG chỉ khác nhau ở tiền xử lý và cấu hình, và bài không tách được yếu tố nào tạo ra chênh lệch.
5. Bài nói ES nhanh hơn nhưng không báo số đo thời gian.
6. SQuAD 2.0 có câu không trả lời được, nhưng bài không phân tích khả năng từ chối. Đây đúng là phần GreenScan cần nhất.
7. "536 bài" là tổng số bài của SQuAD (từ bản 1.1) [KIẾN THỨC NỀN]. Bài không nói dùng tập train hay dev.
8. Nhiều tài liệu tham khảo không liên quan trực tiếp (rủi ro tín dụng, bệnh phổi, nhận dạng ảnh).
9. Trạng thái phản biện: [CHƯA XÁC MINH].

**Liên quan GreenScan:** phần phương pháp của bài **trùng** với bộ `lite`: BM25, TF-IDF trên n-gram ký tự 3–5 kèm cosine, điểm có trọng số 0,55 / 0,45, rồi top-k. Khác ở sáu điểm:
1. GreenScan chạy BM25 ngay trong tiến trình, không cần cụm ES, nên chạy được ngoại tuyến trên laptop.
2. Có thêm RRF k = 60, nhưng chỉ để đổi thứ tự.
3. Truy xuất không bao giờ quyết verdict (bất biến 3); trong bài, LLM sinh đáp án thẳng từ tài liệu.
4. BM25 của GreenScan **không** bỏ stopword: `tokenize()` chỉ bỏ token 1 ký tự (`utils/text.py:30–31`). Bỏ "không" hay "chưa" sẽ làm hỏng lập trường.
5. Luôn giữ 3 ứng viên dưới ngưỡng, có gắn cờ.
6. Loại chính đoạn chứa tuyên bố khỏi kết quả.

**Cách dùng:** dẫn như tài liệu kỹ thuật cho ý "ES là hạ tầng production hợp lý cho BM25, lọc theo trường và mở rộng cụm". Không dẫn như bằng chứng ES làm tăng độ chính xác.

### 1.4 `RETRIEVAL_POLICY.md` (v0.1, 07/07/2026)
- **Là gì:** chính sách truy xuất đích.
- **Nội dung:**
  - Luồng: tuyên bố → yêu cầu bằng chứng → kế hoạch truy vấn → truy xuất nhiều nguồn → rerank → chấm bằng chứng → gói bằng chứng.
  - 6 phương pháp: BM25, vector, hybrid/RRF, tra số liệu có cấu trúc, tra luật, người thêm bằng chứng.
  - 5 họ truy vấn bắt buộc: ủng hộ, số liệu/năm gốc, mâu thuẫn, theo nguồn, chỗ trống cho bằng chứng thiếu.
  - Tìm bằng chứng phủ định là bắt buộc với tuyên bố trọng yếu, pháp lý, tài chính xanh, phát thải và net-zero.
  - Định tuyến OLTP / OLAP.
  - Thứ tự ưu tiên: số liệu có cấu trúc > luật > BM25 khớp chính xác > ngữ nghĩa > nguồn ngoài > nguồn tiếp thị.
  - Tiêu chí loại bằng chứng: sai công ty, sai kỳ, sai Scope, nguồn yếu, trùng, không có nguồn gốc, mơ hồ.
  - "Thiếu bằng chứng là một phát hiện kiểm toán, không phải lỗi."
  - Trần gói bằng chứng 5 / 5 / 3. Bảng chỉ số đo.
- **Liên quan:** khớp tinh thần FEVER/AVeriTeC (tìm cả hai phía).
- **Khác hiện trạng:** code chỉ truy vấn bằng chính câu tuyên bố. Grep `contradiction_quer|support_quer|structured_lookup|query_plan` trong `src/` ra 0 kết quả (04/11). Phải nói đây là **thiết kế đích**.

### 1.5 `VERIFICATION_POLICY.md` (v0.1, 07/07/2026)
- **Là gì:** quy tắc biến gói bằng chứng thành verdict.
- **Nội dung:**
  - 5 lớp kiểm: tính cụ thể; có bằng chứng; nhất quán định lượng (năm gốc, đơn vị, ranh giới, số liệu đã sửa lại, mẫu số, cường độ hay tuyệt đối); khớp luật và phân loại; mâu thuẫn từ bên ngoài.
  - 5 verdict: SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED (phải trích ít nhất 1 bằng chứng CONTRADICTING), INSUFFICIENT_EVIDENCE.
  - Quy tắc xung đột: hồ sơ chính thức thắng tự công bố; số đã kiểm toán thắng số chưa kiểm toán; tuyệt đối tăng mà cường độ giảm thì tuỳ câu chữ.
  - 4 dải "confidence".
  - Rào chắn cho AI: không suy số còn thiếu, không đổi nhãn enum, không phán xét đạo đức.
  - Điều kiện chuyển người: luôn khi CONTRADICTED, risk ≥ 70, OCR kém…
- **Liên quan:** tách UNSUPPORTED (thiếu bằng chứng bắt buộc) khỏi INSUFFICIENT (tài liệu không đủ để đọc). Cách chia này mịn hơn lớp NEI của FEVER. Câu "absence of external contradiction is not support" khớp Joren 2025.
- **Lưu ý:** các dải confidence chưa được hiệu chỉnh trên gold.

### 1.6 `TARGET_PIPELINE_AND_TRAINING.md` (24/09/2026)
- **Là gì:** thiết kế đích, không mô tả hiện trạng.
- **Luận điểm:**
  - "Mô hình ngôn ngữ được phép *đọc*, không được phép *kết luận*." Phần bịa được thì không có quyền quyết; phần quyết thì không bịa được.
  - Luồng 10 bước, và **chỉ ba chỗ có mô hình**: ④⑤ đọc cấu trúc, ⑥ biểu diễn để truy xuất, ⑦ nhánh lập trường bất định. Số học và chấm rủi ro vĩnh viễn không có mô hình.
  - Không bao giờ huấn luyện mô hình sinh verdict.
  - "Nhãn người để đo, nhãn máy để dạy."
  - Ba bộ dữ liệu:
    - A: câu đáng kiểm, 1 000–3 000 nhãn bạc;
    - B: câu → JSON, 500–1 500;
    - C: cặp số so được / không so được, 300–500.
  - Khuôn IR (chỉ số, hướng, kỳ, năm gốc, phạm vi, danh sách số kèm loại giá trị, là mục tiêu hay không).
  - Chưng cất: thầy lớn → ~2 000 nhãn bạc; chỉ soát chỗ thầy và luật bất đồng (15–25 %).
  - QLoRA 4-bit: rank 16–32, α = 32, dropout 0,05, 1 024 token, 2–3 epoch, giải mã ràng buộc ngữ pháp JSON, suy luận Q4_K_M; chia theo doanh nghiệp.
  - Thang B0–B4, mỗi bậc chỉ đổi một thứ; kết quả âm cũng là kết quả hợp lệ.
  - Danh sách cố ý không làm.
- **Đã cũ:** mục 3.1 (FPT có khoá), mục 8 (lịch tới Chung kết: B2 SFT, gold 100–150) và mục 5 (giải mã ràng buộc), xem mục 5 của ghi chú này.

### 1.7 Bảy phiếu nghiên cứu P01–P06, P13

| Phiếu | Nội dung | Số chính | Trạng thái và điểm cần cẩn thận |
|---|---|---|---|
| P01 đọc tài liệu | PyMuPDF đọc chữ; trang dưới 40 ký tự thì chuyển Tesseract; pdfplumber tách bảng thành khối; đoạn ≤ 3 câu | Số liệu đọc được 57 → 16 sau khi sửa; hàng đợi rác 10/22 → 0/9; độ tin cậy OCR 91–96; HPG 264 trang trong 107,4 s, RAM đỉnh 1 331 MB | Chưa kiểm định. Chưa đo độ đúng theo ô bảng hay theo ký tự OCR |
| P02 nhận diện tuyên bố (T1) | 4 lớp; thầy gemma-4-31B; học trò mDeBERTa hoặc e5 | Luật P 55 % (115/209), R 69 % (115/167) so với nhãn Claude; κ Claude A–B 0,92 / 0,98; Claude và gemma đồng ý 89/100, κ 0,63; học trò 0,71–0,73 | κ cùng một model chỉ cho thấy ổn định, không cho thấy đúng; gold 0/79 |
| P03 IR (AG-1) | Mô hình đọc IR, `irlib` ra S / C / N | Số **trước** `ground()`: 4B 0,134 / 1,0; 32B 0,423 / 0,82 / 7 C sai | **Đã cũ** (mục 5.2) |
| P04 truy xuất | 0,55 BM25 + 0,45 n-gram, RRF; lấy 30, giữ 5, giữ 3 ứng viên dưới ngưỡng | 11 DN: 15 409 trang, 14 708 vector; BGE-M3 cục bộ ≈ 7,7 giờ | Chưa có Recall@k (RQ4 và RQ5 còn mở) |
| P05 kiểm chứng định lượng | 5 lớp kiểm, 5 verdict; dung sai ½ chữ số cuối, trần 10 %; lệch ≥ 0,35 thì bác bỏ | 47 hàm test bẫy, 15 hàm test bất biến; GLM nhiệt độ 0 cho 17/19 rồi 16/19; mâu thuẫn sai: luật 1, LLM tự quyết 10 | Số bẫy 17 / 44 / 47 chưa thống nhất |
| P06 lập trường bằng LLM | `decisive=false`: mô hình một mình không tạo S hay C | A/B 713 cặp: không LLM 153/2/0/1; LLM không chốt 136/6/10/4; có chốt 150/2/0/4; chuyển người 0 / 156 / 13 | Tuyến GLM-5.2 qua FPT đã chết (31/10) |
| P13 huấn luyện | T1 phân loại; T2 cross-encoder; T2-gen là QLoRA dự phòng | CPU 1,7 mẫu/s; nhãn thầy 400 câu ≈ 0,011 USD; ONNX int8 nhanh 2–2,5 lần | QLoRA r = 32, α = 16, **lệch** với TARGET_PIPELINE (α = 32); AG-4 chưa chạy |

### 1.8 Tài liệu đối chiếu (đọc thêm)

**Kết quả mới nhất 31/10–01/11** (KE_HOACH §10, AG-1 README §5)
- Model đọc kèm `ground()` và C-guard: trên tập ngoài mẫu sạch v1.3 (87 ca) phủ 0,115–0,253, không kết luận sai nào; luật chỉ phủ 0,011.
- AG-2: luật + 4B, bỏ phiếu SUPPORTED đơn độc của luật, qua phần thống kê của cổng.
- Bộ đọc Q4 cục bộ khớp bản bf16 0,963.
- AG-3 v0 dựng lại bảng: đúng 3/7 ca.

**Mười bất biến:** chi tiết dùng ở mục 2 và 4.

**Code:** BM25 tự viết, k1 = 1,5 và b = 0,75. Không dùng Elasticsearch, OpenSearch, rank_bm25 hay FAISS (grep ngày 04/11).

---

## 2. Khái niệm và lý thuyết phải nắm

### A. Tầng đọc và nhận diện tuyên bố
- **Phát hiện tuyên bố (check-worthiness):** phân loại từng câu (QUANTIFIED / QUALITATIVE / VAGUE / NOT_CLAIM).
  - Lỗi tốn kém nhất là bỏ sót, vì câu bị sót thì không bao giờ được kiểm.
  - Đo recall bằng cách lấy mẫu các câu *không* được trích rồi cho người soát.
  - Ví dụ GreenScan: luật có recall 69 % so với nhãn Claude.
- **Tuyên bố nguyên tử và phân rã:** câu ghép phải tách thành từng khẳng định, và mỗi phần giữ `doc_id`, trang, nguyên văn (bất biến 2).
  - FActScore chấm theo từng fact nguyên tử, nhưng điểm nhạy với cách phân rã (Wanner 2024).
  - GreenScan chỉ phân rã *tất định* các tuyên bố số ghép, ví dụ "giảm 15 % Scope 1 và 20 % nước".
- **Lớp chữ trước, OCR sau; chuẩn hoá NFC:** dấu tiếng Việt có hai dạng mã hoá (dựng sẵn và tổ hợp). Lỗi gộp dấu "cộng / công" từng làm nhận nhầm dòng tổng.

### B. Tầng truy xuất
- **RAG** (Lewis và cs., NeurIPS 2020) [KIẾN THỨC NỀN]: tìm tài liệu rồi để LLM sinh câu trả lời. GreenScan là **kiểm chứng có truy xuất**: truy xuất chỉ cho ứng viên, mô hình điền IR, code kết luận.
- **BM25** (Robertson & Zaragoza 2009) [KIẾN THỨC NỀN], bản cài trong `hybrid.py:142–157`:
  `score(q,d) = Σ_{t∈q} IDF(t) · tf·(k1+1) / (tf + k1·(1 − b + b·|d|/avgdl))`,
  `IDF(t) = ln(1 + (N − df + 0,5)/(df + 0,5))`.
  - k1 làm bão hoà tần suất; b chuẩn hoá theo độ dài.
  - GreenScan dùng k1 = 1,5, b = 0,75, rồi nén `s/(s+3)` về [0; 1) để cộng được với cosine.
  - Token là âm tiết đã chuẩn hoá, viết thường, dài hơn 1 ký tự; không tách từ.
- **TF-IDF và cosine:** `cos(A,B) = A·B/(‖A‖‖B‖)`.
  - GreenScan dùng TF-IDF trên **n-gram ký tự 3–5** (`char_wb`, `hybrid.py:53`).
  - Cách này chịu được lỗi tách từ tiếng Việt, mất dấu, dính chữ do OCR và biến thể cách viết số.
- **Dense bi-encoder và cross-encoder reranker** [KIẾN THỨC NỀN]:
  - Bi-encoder mã hoá tuyên bố và đoạn văn riêng (Sentence-BERT, DPR, E5, BGE-M3), nên nhanh và dùng được chỉ mục ANN.
  - Cross-encoder chấm *cặp* cùng lúc nên chính xác hơn nhưng chi phí tăng theo số ứng viên, vì vậy chỉ dùng để rerank top-k.
  - GreenScan: có lớp BGEReranker, TEIReranker, FPTReranker; mặc định là `NoopReranker`.
- **Hợp nhất điểm:**
  - *Tuyến tính* cần đưa các điểm về cùng thang. GreenScan: `0,55·BM25' + 0,45·sem + 0,025·[không phải nguồn tuyên bố] + prior(loại nguồn)`.
  - *RRF* (Cormack, Clarke & Büttcher, SIGIR 2009) [KIẾN THỨC NỀN]: `RRF(d) = Σ_r 1/(k + rank_r(d))`, k = 60. Chỉ dùng thứ hạng nên không cần hiệu chỉnh thang điểm.
  - GreenScan dùng RRF để **đổi thứ tự** nhưng giữ điểm tuyến tính để so ngưỡng (`minimum_score` 0,12), giúp ngưỡng kiểm chứng phía sau ổn định.
- **Ứng viên dưới ngưỡng (`floor_k = 3`):** tách hai tình huống "không đoạn nào nói về tuyên bố" và "không đoạn nào *trông giống* tuyên bố".
  - Ví dụ: ca KLM-2024, phán quyết bác bỏ có ít chữ trùng với câu quảng cáo.
  - Các ứng viên này không tạo được SUPPORTED hay PARTIAL, nhưng mang được bằng chứng bác bỏ từ nguồn có thẩm quyền.
- **Chỉ số truy xuất:**
  - `Recall@k = |liên quan ∩ top-k| / |liên quan|`.
  - MRR là trung bình 1/hạng của tài liệu liên quan đầu tiên.
  - `nDCG@k = DCG/IDCG`, với `DCG = Σ (2^rel − 1)/log2(i+1)`.
  - **Hole@k** là tỷ lệ tài liệu chưa được gán nhãn trong top-k.
  - **Pooling bias:** nhãn chỉ có cho những gì các hệ cũ đã tìm ra, nên recall là *cận dưới* và hệ mới bị thiệt (BEIR: Hole@10 của TAS-B 31,8 % so với BM25 6,4 %).
  - bpref là chỉ số bền với nhãn thiếu.
- **Lost in the Middle:** đặt thông tin ở giữa ngữ cảnh dài thì hiệu năng tụt. Vì vậy prompt chỉ chứa *cặp* tuyên bố–bằng chứng, không nhồi cả trang.
- **Elasticsearch** [KIẾN THỨC NỀN]:
  - Xây trên Lucene, chỉ mục ngược, mặc định chấm BM25; có analyzer, bộ lọc theo trường, khả năng mở rộng cụm.
  - Các bản 8.x có kNN vector và RRF [chi tiết phiên bản CHƯA XÁC MINH].
  - Là *động cơ*, không phải thuật toán xếp hạng mới.

### C. Tầng kiểm chứng
- **Pipeline kiểm chứng** (Guo, Schlichtkrull & Vlachos, TACL 2022): phát hiện tuyên bố → truy xuất bằng chứng → dự đoán verdict → giải thích.
- **FEVER:** nhãn SUPPORTED / REFUTED / NOTENOUGHINFO.
  - *FEVER score* chỉ tính đúng khi nhãn đúng **và** có đủ một bộ bằng chứng gold. Đây là chấm có điều kiện bằng chứng.
  - Bài học: không chấm verdict khi bằng chứng sai.
- **NLI:** nhãn kéo theo / mâu thuẫn / trung lập, ánh xạ gần đúng sang S / R / NEI. Cần nhớ:
  - "trung lập" không có nghĩa là "sai";
  - mô hình ngoài miền rơi mạnh (FEVER → Climate-FEVER còn 38,78 %).
- **Lập trường (stance):** quan hệ xác nhận / phủ nhận / chỉ bối cảnh / một phần.
  - GreenScan dùng từ điển cue và phép so số.
  - Cặp bất định mới gọi mô hình, kèm chốt `llm_stance_decisive: false`.
- **Đủ bằng chứng chưa, và ủng hộ hay bác bỏ, là hai câu hỏi khác nhau** (Joren 2025).
  - GreenScan: "đủ" do luật quyết (đúng chỉ số, Scope, kỳ, đơn vị). Thiếu thì ra INSUFFICIENT_EVIDENCE hoặc chuyển người (bất biến 8).
  - Không tìm thấy không có nghĩa là bằng chứng nói ngược (bất biến 6).
- **Gộp nhãn tất định:**
  - AVeriTeC: có cả ủng hộ lẫn bác bỏ thì Conflicting/Cherry-picking; chỉ ủng hộ thì S; chỉ bác bỏ thì R; còn lại NEE.
  - Climate-FEVER: mặc định NEI, có cả hai thì DISPUTED.
  - Cách gộp này tương ứng với PARTIALLY_SUPPORTED / CONTRADICTED của GreenScan.
- **Bằng chứng tương phản và nhiễu số:**
  - VitaminC: hai bằng chứng gần giống hệt nhưng nhãn ngược nhau.
  - NumPert: chỉ đổi một con số mà nhãn đảo.
  - GS-Bench B-b dùng đúng ý này với các họ nhiễu: giá trị, đơn vị, kỳ, Scope, công ty mẹ hay tập đoàn, mục tiêu hay thành tích, cường độ hay tuyệt đối.

### D. Số học và bảng tài chính
- **FinQA:** mô hình sinh *chương trình* (cộng, trừ, chia, tổng bảng) rồi thực thi; điểm là *execution accuracy*. **TAT-QA:** TAGOP gắn nhãn ô/cụm từ rồi áp toán tử ký hiệu [KIẾN THỨC NỀN về TAGOP]. Cả hai đều tách "chọn số" (phần thần kinh) khỏi "tính" (phần ký hiệu). Cùng họ với PAL / Program-of-Thought [KIẾN THỨC NỀN], và cũng là ý tưởng của GreenScan: LLM → IR → `irlib`.
- **IR (biểu diễn trung gian):** gồm chỉ số, giá trị, đơn vị, bội số, kỳ, năm gốc, ranh giới tổ chức, Scope, loại giá trị (tuyệt đối / cường độ / tỷ trọng / thay đổi), thành tích hay mục tiêu.
- **Kiểm "so được" trước khi tính (bất biến 4):** lệch một chiều thì cấm CONTRADICTED. Ví dụ: Scope 1+2 so với Scope 1, tập đoàn so với nhà máy, tuyệt đối so với cường độ dù cùng đơn vị tCO₂e.
- **Dung sai theo độ chính xác công bố:** ½ đơn vị của chữ số cuối, trần 10 %. Phân biệt điểm phần trăm với phần trăm tương đối.
- **Cộng ngang/dọc (cross-footing):** kiểm bảng tự thân, tổng phải bằng tổng các thành phần. Bảng không qua kiểm thì không được dùng để kết luận.
- **Mục tiêu khác thành tích** (bất biến 6): "Sẽ giảm 30 %" không chứng minh "đã giảm 30 %".

### E. LLM: giải mã, chấm nhãn, chưng cất
- **Giải mã greedy / nhiệt độ 0:** tái lập trên máy cục bộ (AG-1: `temperature=0`, `seed=0`, tắt thinking). API vẫn có thể không tất định: GLM-5.2 cho 17/19 rồi 16/19.
- **Giải mã ràng buộc (JSON schema / ngữ pháp)** [KIẾN THỨC NỀN, ví dụ Outlines (Willard & Louf 2023), GBNF của llama.cpp]:
  - Mỗi bước, token làm vỡ automat ngữ pháp bị che (`p'(v) ∝ p(v)·1[v hợp lệ]`).
  - Bảo đảm **cú pháp**, không bảo đảm **nội dung**.
  - "JSON mode" (như `json_object` của Groq) chỉ bảo đảm JSON hợp lệ, không bảo đảm đúng schema.
- **Kiểm nguồn gốc (grounding) tất định:** `irlib.ground()` buộc mọi số, bội số và năm trong IR phải được *viết* trong câu gốc; không có thì null. Đây là cách chặn bịa ở phần nghĩa mà ràng buộc cú pháp không chặn được.
- **LLM-as-judge và thiên lệch:**
  - Thiên lệch vị trí (đảo thứ tự là đổi kết quả), độ dài, tự ưu tiên (Panickssery); độ tin cậy biến thiên theo tác vụ.
  - Cách giảm: chạy cả hai thứ tự, không cho cùng một model vừa sinh vừa chấm, kiểm định với nhãn người, dùng **nhãn theo cấu trúc** (biết đáp án nhờ cách dựng).
- **Chưng cất tri thức** (Hinton 2015) [KIẾN THỨC NỀN]: `L = (1−λ)·CE(y, p_s) + λ·T²·KL(p_t^T ‖ p_s^T)`.
  - Với LLM thường dùng chưng cất mức chuỗi: học trò SFT trên đầu ra của thầy (Kim & Rush 2016).
  - "Nhãn tìm bằng thực thi": chỉ giữ IR của thầy nào mà `irlib` chạy ra đúng đáp án. Đây là kiểu lọc bằng thực thi, gần STaR [KIẾN THỨC NỀN].
- **LoRA / QLoRA** [KIẾN THỨC NỀN: Hu 2022; Dettmers 2023]:
  - LoRA: `h = W0·x + (α/r)·B·A·x`, với `B∈R^{d×r}`, `A∈R^{r×k}`, r ≪ d. Chỉ học A và B.
  - QLoRA giữ W0 ở 4-bit NF4, có lượng tử kép và paged optimizer, nên tinh chỉnh được trên GPU nhỏ.
  - Lượng tử khi suy luận (GGUF Q4_K_M, AWQ) thì phải kiểm độ khớp với bản đầy đủ (GreenScan: Q4 khớp bf16 0,963).
- **Self-consistency và kiểm chéo hai đường:**
  - Self-consistency là lấy mẫu nhiều lần rồi bỏ phiếu. GreenScan không mượn vì tín hiệu yếu [NGOÀI theo KE_HOACH §3].
  - Thay vào đó dùng **hai đường độc lập** (luật và mô hình đọc + code), rồi cổng đồng thuận.

### F. Hiệu chỉnh và dự đoán có từ chối
- **Calibration:** P(đúng | độ tin cậy = p) phải bằng p. `ECE = Σ_m (|B_m|/n)·|acc(B_m) − conf(B_m)|`.
  - Các cách sửa: temperature scaling (Guo 2017), histogram binning, isotonic [KIẾN THỨC NỀN].
  - Độ tự tin LLM *tự khai* thường quá cao (Xiong 2024). Softmax cũng quá tự tin ngoài miền (Kamath 2020).
- **Dự đoán có từ chối (selective prediction):** cặp (f, g), trong đó g quyết định có trả lời không.
  - Độ phủ `φ = E[g]`; rủi ro chọn lọc `R = E[ℓ·g]/E[g]`; vẽ đường risk–coverage (Geifman & El-Yaniv 2017).
  - Nguồn gốc là quy tắc từ chối của Chow (1970) [KIẾN THỨC NỀN].
  - Conformal prediction cho bảo đảm thống kê từ một tập hiệu chỉnh (Mohri & Hashimoto 2024).
- **Thước đo của GreenScan:**
  - *precision trên phần dám kết luận* = số đúng trong {S, C} / số {S, C} (tức 1 − rủi ro chọn lọc);
  - *độ phủ* = số {S, C} / N;
  - *số kết luận sai nguy hiểm*: C sai là vu oan, S sai là bỏ lọt.
  - Không gộp thành một số. Tham chiếu: EmeraldMind, overall = acc × coverage.
- **Quy tắc kết luận của AG-2:** P(đúng) theo xô (loại tuyên bố × trạng thái khớp), ước trên dự đoán ngoài fold chia theo công ty. Chỉ kết luận khi **cận dưới CI95** > 0,9 (C) hoặc > 0,8 (S). Chi phí bất đối xứng: vu oan đắt hơn bỏ lọt.

### G. Đo lường trên mẫu nhỏ
- **Wilson:** `(p̂ + z²/2n ± z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)`.
  - "Quy tắc ba": 0 lỗi trên n ca thì cận trên của tỷ lệ lỗi ≈ 3/n.
  - Tự tính, đúng hết thì cận dưới 95 %: n = 10 → 0,72; 12 → 0,76; 15 → 0,80; 22 → 0,85.
- **Cụm theo doanh nghiệp:** `DE = 1 + (m − 1)·ICC`, `n_eff = n/DE`. Bootstrap theo công ty; SE có cụm có thể lớn gấp 3 SE ngây thơ (Miller 2024).
- **Power / MDE:** n = 80 chỉ phát hiện được chênh 10–17 điểm. Nói "không phát hiện được khác biệt", không nói "bằng nhau".
- **Chia giữ hẳn công ty ra ngoài; đăng ký dự đoán trước;** báo cả dự đoán sai.
- **κ** `= (p_o − p_e)/(1 − p_e)`.
  - Nghịch lý κ: nhãn lệch thì κ thấp dù tỷ lệ đồng ý cao.
  - Báo κ kèm CI, tỷ lệ đồng ý, đồng thuận theo từng lớp, free-marginal κ.
- **Macro-F1, baseline lớp đa số:** accuracy nhị phân cao trên dữ liệu lệch lớp là ảo.

### H. Người–AI
- **Phụ thuộc quá mức:** giải thích làm người chấp nhận khuyến nghị bất kể đúng sai (Bansal 2021). Giải thích chỉ giảm phụ thuộc khi làm *rẻ việc kiểm* (Vasconcelos 2023).
- **Algorithm aversion:** kiểm toán viên xem nhẹ bằng chứng do AI đưa ra (Commerford 2022).
- **Đặc tả màn hình theo Warren 2025:** hiện đường suy luận, bằng chứng cụ thể, chỗ bất định và thông tin còn thiếu.

---

## 3. Số liệu và dữ kiện được phép nói

**Viết tắt nguồn**
- [KH] = `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`
- [AG1] = `experiments/AG-1/README.md`
- [TQ] = `docs/08-knowledge/sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md`
- [05] = `docs/08-knowledge/05_AI_NLP_VA_DO_LUONG.md`
- [TP] = `docs/04-data-ai/TARGET_PIPELINE_AND_TRAINING.md`
- [RP] = `docs/04-data-ai/RETRIEVAL_POLICY.md`
- [VP] = `docs/04-data-ai/VERIFICATION_POLICY.md`
- [INV] = `docs/00-project/ARCHITECTURE_INVARIANTS.md`
- [Pxx] = `docs/07-presentation/nghien-cuu/Pxx_*.md`
- [ES] = `scratchpad\txt\optimizing_rag_elasticsearch.txt`

Mọi số trên GS-Bench phải kèm cụm "trên ca dựng"; số trên B-c kèm "trên nhãn Claude".

### 3.1 Số đo của đội (mới nhất trước)
- Ngoài mẫu sạch v1.3, 87 ca, mỗi ô ghi độ phủ: luật 0,011; 4B 0,138 (CI [0,045; 0,314]); 8B 0,115; 14B 0,115; 32B 0,253. Mọi model precision 1,0, không kết luận sai; mỗi model dám kết luận 10–22 ca · [AG1] §5 "01/11 17:00" · [ĐÃ THỰC NGHIỆM]
- Trong mẫu sạch (383–397 ca), mỗi ô ghi độ phủ / precision / S sai / C sai:
  - luật 0,060 / 0,625 / 9 / 0;
  - 4B 0,243 / 0,989 / 1 / 0;
  - 8B 0,292 / 0,982 / 2 / 0;
  - 14B 0,347 / 0,970 / 3 / 1;
  - 32B 0,373 / 0,986 / 2 / 0 (tập lệch về 32B).
  - Nguồn · [AG1] §5 · [ĐÃ THỰC NGHIỆM]
- Cận dưới Wilson 95 % của precision 1,0 khi n = 10–22 là 0,72–0,85 · tự tính từ [AG1] §5 · [KIẾN THỨC NỀN: phép tính]
- Bộ đọc Q4 / Q8 chạy cục bộ khớp 4B bf16 lần lượt 0,963 / 0,981. Luật + 4B Q4, bỏ phiếu S đơn độc của luật, trên G: 0 sai, phủ 0,080 (CI phần tăng [0,016; 0,175]). Tốc độ 1,7 s/câu trên T4 · [KH] §10 "17:15" · [ĐÃ THỰC NGHIỆM]
- AG-2: luật + 4B, bỏ phiếu S đơn độc của luật.
  - Trên G: 0,093 / 1,0 / 0 / 0; phần tăng độ phủ có CI [0,016; 0,185].
  - Trên tập hiệu chỉnh: 0,242 / 0,989 / 1 / 0, trong khi luật có 8 S sai.
  - Luật + 32B và luật + 4 model trượt cổng (lần lượt 1 và 2 S sai).
  - Nguồn · [KH] §10 "23:50" · [ĐÃ THỰC NGHIỆM]
- Trên G, 4B chỉ dám kết luận 15 ca và đúng cả 15, nên cận dưới chỉ khoảng 0,80 · [KH] §10 · [ĐÃ THỰC NGHIỆM]
- G (v1.2, 162 ca, 9 DN): 0 CONTRADICTED sai ở cả 4 model; độ phủ 4B 0,093; 37 % ca thuộc nhóm `other_env` không phải môi trường (lỗi tập) · [KH] §10 "23:25" · [ĐÃ THỰC NGHIỆM]
- Ngoài mẫu v1.1 (246 ca): độ phủ 4B / 8B / 14B / 32B = 0,126 / 0,220 / 0,256 / 0,329. 4B có `ground` đạt precision 0,903 với 2 C sai. Với v1.1 chỉ 8B qua cổng; với v1.2 thì 8B và 32B có 0 vu oan · [KH] §10 "14:35", "22:40" · [ĐÃ THỰC NGHIỆM]
- `ground()`: 11/11 kết luận sai của 32B là do model tự thêm bội số ("10.730 m3" thành "10.730 nghìn m3"). Sau khi sửa (trong mẫu): 4B độ phủ 0,134 → 0,437, precision 0,984; 32B precision 0,817 → 0,985, C sai 7 → 1. Có 9 test hồi quy · [KH] §10 "14:15" · [ĐÃ THỰC NGHIỆM]
- Trần, khi dùng IR gold + `irlib`, trên B-b v1: đúng 140/142, độ phủ 0,528, precision 1,0 · [KH] §10 · [ĐÃ THỰC NGHIỆM]
- Mốc luật trên B-b v1: độ phủ 0,028 (4/142), precision 0,75, bắt được 0/44 ca mâu thuẫn · [KH] §10; [P03] §2 · [ĐÃ THỰC NGHIỆM]
- GS-Bench:
  - v1 có 193 ca (51 B-a + 142 B-b; S 33 / C 44 / N 65; 5 DN);
  - v1.1 có 453 ca (51 + 402; S 95 / C 123 / N 184; 7 DN);
  - soát tay 14 ca thấy nhãn đúng, sửa 3 lỗi diễn đạt.
  - Nguồn · [KH] §10; [P03] §5 · [ĐÃ THỰC NGHIỆM]
- AG-3 v0: trang 39 của HPG dựng được 10 hàng, cộng dọc khớp 3/3. Trên 7 ca: trang thô đúng 1/7, hàng dựng lại đúng 3/7, 0 sai. Dự đoán ≥ 5/7 **sai** · [KH] §10 "17:40" · [ĐÃ THỰC NGHIỆM]
- GROQ-PROBE, `gpt-oss-120b` kèm `json_object`: 12/12 JSON hợp lệ, độ đúng trường 1,0, p50 1,0 s · [KH] §10 "14:15" · [ĐÃ THỰC NGHIỆM]
- Lỗi đã đo: F1 HPG 153 PARTIAL / 2 S / 1 INSUFFICIENT trên 156; F2 luật quyết 8/32 (đúng 6) và 3/19 (đúng 3); F3 cả 4 model ≥ 26B báo SUPPORTED sai trên bảng dàn phẳng; F4 có 5 lỗi chuẩn hoá; F7 0 nhãn người · [KH] §2 · [ĐÃ THỰC NGHIỆM]
- A/B lập trường LLM (HPG, 713 cặp luật không quyết), ghi P / S / C / I:
  - không LLM 153/2/0/1;
  - LLM không chốt 136/6/10/4;
  - LLM có chốt 150/2/0/4.
  - Số câu chuyển người lần lượt 0 / 156 / 13; 710 lần gọi API trong 451 s, không lỗi.
  - Nguồn · [P06] §5 · [ĐÃ THỰC NGHIỆM]
- GLM-5.2 ở nhiệt độ 0 cho 17/19 rồi 16/19 · [P05] §5 · [ĐÃ THỰC NGHIỆM]
- 22/09 có 5/8 kết luận mâu thuẫn sai, do khác Scope, khác tập đoàn, khác đơn vị · [P05] §7; [INV] bảng cấm · [ĐÃ THỰC NGHIỆM]
- Bộ trích luật có P 55 % (115/209), R 69 % (115/167) so với nhãn Claude · [P02] §2 · [ĐÃ THỰC NGHIỆM]
- Claude hai lượt: κ 0,92 (5 nhãn), 0,98 (tuyên bố hay không). Claude và gemma đồng ý 89/100, κ 0,63 · [P02] §5 · [ĐÃ THỰC NGHIỆM]
- Học trò T1 (e5-base): macro-F1 0,71–0,73 trên nhãn Claude, chia theo công ty, n = 1 217, 3 seed. Chưa nối vào sản phẩm · [KH] §2 · [ĐÃ THỰC NGHIỆM]
- HPG: 264 trang, 156 tuyên bố, 107,4 s (3 lần chạy 107–121 s), RAM đỉnh 1 331 MB, i7-1355U không GPU · [P01] §5 · [ĐÃ THỰC NGHIỆM]
- Thư viện 11 DN có 15 409 trang, 14 708 vector; chạy BGE-M3 cục bộ mất ≈ 7,7 giờ · [P04] §4–5 · [ĐÃ THỰC NGHIỆM]
- Truy xuất **chưa** có Recall@k, MRR hay nDCG trên gold · [P04] §5 · [ĐÃ THỰC NGHIỆM, là trạng thái]
- Kiểm thử: 47 hàm trong `test_verdict_traps.py`, 15 hàm trong `test_architecture_invariants.py` · [P05] §3 · [ĐÃ THỰC NGHIỆM]
- Kho câu: 66 539 câu chưa gán; luật nhận 4 598 câu là tuyên bố; luật từ chối 6 631 câu có thuật ngữ môi trường · [P02] §5 · [ĐÃ THỰC NGHIỆM]
- ZAIC, dự án khác của đội: Qwen3-4B QLoRA từ 0,215 lên 0,485 · [KH] §3 · [ĐÃ THỰC NGHIỆM, ZAIC — không phải GreenScan]

### 3.2 Thiết kế đã cài trong code (chưa đo)
- BM25 với k1 = 1,5, b = 0,75, IDF kiểu Lucene, nén điểm bằng `s/(s+3)` · `src/quantum_gw/retrieval/hybrid.py:142–157` · [KIẾN THỨC NỀN]
- TF-IDF trên n-gram ký tự `char_wb` 3–5, kèm cosine · `hybrid.py:53` · [KIẾN THỨC NỀN]
- Điểm = 0,55 × lexical + 0,45 × semantic. RRF k = 60 chỉ đổi thứ tự. Tham số: `candidate_k` 30, `top_k` 5, `minimum_score` 0,12, `floor_k` 3, `exclude_same_chunk` · `src/quantum_gw/settings.py:128–140`; `hybrid.py:60–140` · [KIẾN THỨC NỀN]
- Mỗi đoạn truy xuất mang cờ `suspicious_instruction` (prompt injection) và cờ `below_threshold` · `hybrid.py:89, 94` · [KIẾN THỨC NỀN]
- Reranker mặc định là Noop; có sẵn bge-reranker-v2-m3 chạy cục bộ, qua TEI hoặc FPT. Cấu hình `embedding: lite`, `reranker: none` · `rerank.py:15–62`; [P04] §3 · [KIẾN THỨC NỀN]
- AG-1 giải mã greedy (nhiệt độ 0, seed 0), tắt thinking, **không** dùng guided JSON · `experiments/AG-1/llm.py`; [P03] §4 · [KIẾN THỨC NỀN]
- `ground()`: số, bội số và năm phải được viết trong câu gốc · `experiments/AG-1/irlib.py:96–118` · [KIẾN THỨC NỀN]
- Mười bất biến, trong đó số 3 (truy xuất không quyết), 4 (chỉ so cái so được), 5 (số học là của code), 6 (mục tiêu khác thành tích), 8 (từ chối là hợp lệ), 10 (tái lập được) · [INV] · [KIẾN THỨC NỀN]
- Dung sai ½ chữ số cuối, trần 10 %; lệch ≥ 0,35 thì bác bỏ · [P05] §3 · [KIẾN THỨC NỀN] (xem mục 5.1, ý 6)
- Họ truy vấn ủng hộ / mâu thuẫn / có cấu trúc chỉ có trong chính sách, chưa có trong `src/` · [RP] §4; grep 04/11 · [KIẾN THỨC NỀN]

### 3.3 Tài liệu ngoài (theo [TQ], trừ khi ghi khác)
- Chưa có bộ greenwashing đã xác minh; nên dùng pipeline phân rã có người giám sát · [TQ] §1.1 [S1.2] · [NGOÀI]
- Environmental claims: SVM 69,1 / 70,9; RoBERTa-large 84,9; chênh recall tới 25 điểm; α = 0,47 · [TQ] §1.2 [S1.5] · [NGOÀI]
- ClimRetrieve: BM25 0,113, text-embedding-3-large 0,167, tốt nhất 0,179; tác giả tự gọi là cận dưới · [TQ] §1.3 [S1.9] · [NGOÀI]
- EmeraldMind: baseline 94,21 % đúng ở độ phủ 19,52 % (overall 18,39 %); EM-HYBRID 83,80 % ở 74,68 % (overall 62,58 %) · [TQ] §1.4 [S1.11] · [NGOÀI]
- Climinator: 96,4 % nhị phân, trong khi baseline lớp đa số 90,3 % (TQ tự tính); 12 lớp chỉ 34,5 % · [TQ] §1.3 [S1.8] · [NGOÀI]
- FEVER: 31,87 % khi phải đúng cả bằng chứng, 50,91 % nếu bỏ qua bằng chứng; κ = 0,684 · [TQ] §2.1 [S2.1] · [NGOÀI]
- AVeriTeC: κ 0,619 / 0,503; BERT-large macro-F1 0,49 khi có gold evidence; shared task 2024 đạt 63 %, 2025 đạt 33,17 % (mô hình mở, 1 GPU 23 GB, 1 phút/tuyên bố) · [TQ] §2.1 [S2.3] · [NGOÀI]
- Climate-FEVER: mô hình huấn luyện trên FEVER đạt 38,78 % (so với 77,69 % trên FEVER dev); α = 0,334 · [TQ] §2.1 [S2.4] · [NGOÀI]
- NumPert: giảm tới 62 %. Aarnes & Setty 2026: GPT-5.4 Pro 74,0 %, Gemini 2.5 Flash 73,9 %; Qwen3 0,6–8B tinh chỉnh PEFT đối kháng đạt 98,7 % · [TQ] §2.3 [S2.7, S2.8] · [NGOÀI]
- QuanTemp: 15 514 tuyên bố, macro-F1 58,32. VitaminC: +10 % trên kiểm chứng đối kháng, +6 % trên NLI đối kháng · [TQ] §2.3 · [NGOÀI]
- FinQA: FinQANet 61,24 %, chuyên gia 91,16 %, người không chuyên 50,68 %; 1 / 2 / ≥ 3 bước suy luận: 67,61 / 59,08 / 22,78 % · [TQ] §2.4 [S2.12] · [NGOÀI]
- TAT-QA: TAGOP 58,0 F1, chuyên gia 90,8 · [TQ] §2.4 [S2.13] · [NGOÀI]
- FinDVer: LLM tốt nhất 77,2 %, chuyên gia 93,3 %; 66–71 % tuyên bố cần bằng chứng từ bảng; mỗi tài liệu ≈ 41K từ, ≈ 79 bảng · [TQ] §2.4 [S2.14] · [NGOÀI]
- FinanceBench: GPT-4-Turbo có truy xuất trả lời sai hoặc từ chối 81 % câu (mẫu 150). TabFact: 65,1 % so với người 92,1 %. FEVEROUS: 18 % · [TQ] §2.4 · [NGOÀI]
- Lost in the Middle: thông tin nằm giữa thì GPT-3.5 còn thấp hơn chế độ không đưa tài liệu (56,1 %) · [TQ] §2.5 [S2.17] · [NGOÀI]
- Zhao (TOSEM 2026): lỗi ở 12,6 % mẫu dù tài liệu hoàn hảo; với QA, 5–10 tài liệu là tối ưu · [TQ] §2.5 [S2.5b] · [NGOÀI]
- Joren (ICLR 2025): LLM lớn trả lời sai thay vì từ chối; sinh có chọn lọc tăng 2–10 % · [TQ] §2.5 [S2.19] · [NGOÀI]
- Chỉ 51,5 % câu được trích dẫn hỗ trợ đầy đủ, 74,5 % trích dẫn đúng; ALCE thiếu hỗ trợ trích dẫn 50 % · [TQ] §3.1 · [NGOÀI]
- MiniCheck-Flan-T5-L 75,0 so với GPT-4o 75,9; rẻ hơn 400 lần; chỉ tiếng Anh · [TQ] §3.1 [S3.4] · [NGOÀI]
- Xiong: độ tin cậy tự khai thường quá cao, AUROC 0,522–0,605. Kamath: bộ hiệu chỉnh trả lời 56 % câu ở accuracy 80 %, so với 48 % · [TQ] §3.3 · [NGOÀI]
- Wang 2024: đảo thứ tự là Vicuna-13B "thắng" ChatGPT 66/80. Shi 2025: 15 giám khảo, hơn 150 000 lượt. Bavaresco 2025: 20 bộ dữ liệu, 11 LLM, biến thiên lớn · [TQ] §3.4 · [NGOÀI]
- Geifman: lỗi top-5 2 % ở độ phủ gần 60 %. Mohri: bảo đảm 80–90 % · [TQ] §3.5 · [NGOÀI]
- Bansal 2021; Vasconcelos 2023 (N = 731); Commerford 2022 (algorithm aversion trong kiểm toán) · [TQ] §3.6 · [NGOÀI]
- VN-MTEB (dịch máy), cột Retrieval: e5-large-instruct 40,88; bge-m3 39,84; gte-multilingual-base 38,38; AITeamVN 34,18; e5-small 34,12. Trên Zalo legal (tự báo): AITeamVN 0,7274 so với bge-m3 0,5682 · [TQ] §4.1 · [NGOÀI]
- PhoRanker NDCG@10 0,7422 so với bge-reranker-v2-m3 0,6872 (tự báo, mMARCO-vi) · [TQ] §4.2 · [NGOÀI]
- mDeBERTa-xnli trên XNLI tiếng Việt 0,793; ViANLI (XLM-R) 45,5 %; ViFactCheck 7 232 cặp, κ 0,83, MIT; ViWikiFC: BM25 cho NEI 56,67 % · [TQ] §4.3–4.4 · [NGOÀI]
- ESGReveal 76,9 %. Schmoll & Jatowt: LLM kém ở KPI định lượng zero-shot, calibration không đáng tin · [TQ] §5.1 · [NGOÀI]
- BEIR Hole@10: BM25 6,4 %, TAS-B 31,8 %; ANCE 0,654 → 0,735 sau khi gán bổ sung · [TQ] §6.4 · [NGOÀI]
- Miller 2024: SE có cụm lớn hơn 3 lần (DROP). Lewis 2021: 30 % câu hỏi test trùng gần với train · [TQ] §6.1, §6.3 · [NGOÀI]
- Học trò trên dữ liệu do LLM sinh mất 3–8 điểm (Li và cs. 2023). GPT-4 có F1 trung vị 0,707 trên 27 tác vụ (Pangakis 2023) · [P13] §4, §6 · [NGOÀI]
- Kiểm chéo hai đường đạt AUROC 0,82, tự nhất quán 0,61–0,68 (text-to-SQL) · [KH] §3 · [NGOÀI; paper gốc chưa ghi, CHƯA XÁC MINH]
- ES-RAG: Acc 68,29 % so với TF-IDF-RAG 67,78 % (+0,51), không có CI · [ES] trang 4, Bảng 1 · [NGOÀI]

### 3.4 Giả thuyết đã đăng ký hoặc chưa kiểm
- AG-0: phần lớn chênh lệch nằm ở bảng và ánh xạ, không ở truy xuất. Chưa thấy kết quả phép thử oracle "đoạn gold" · [KH] §5 · [GIẢ THUYẾT]
- AG-4: 1,7B tinh chỉnh ≥ 8B zero-shot về độ đúng IR; ≤ 3 s/tuyên bố trên CPU · [KH] §5 · [GIẢ THUYẾT]
- Ngưỡng bật BGE-M3: ΔRecall@5 ≥ +10 điểm, thời gian ≤ 2 lần `lite` · [P04] §9 · [GIẢ THUYẾT]
- "B-b đại diện cho tuyên bố thật" · [KH] §4 · [GIẢ THUYẾT]

---

## 4. Câu hỏi BGK dự kiến

Công thức trả lời: **Vấn đề → Nguyên lý → GreenScan làm gì → Giới hạn**.

**Q1. "Sao không đưa cả báo cáo cho một LLM lớn kết luận cho gọn?"**
- **Trả lời:**
  - *Vấn đề:* kết luận về một doanh nghiệp phải tái lập được và chỉ ra được phép tính đã chạy.
  - *Nguyên lý:* LLM giòn với số. Accuracy giảm tới 62 % khi số bị nhiễu (NumPert). Mô hình frontier chỉ khoảng 74 % trên cặp chỉ khác một con số (Aarnes & Setty, 30/09/2026). Trên báo cáo tài chính dài, LLM tốt nhất đạt 77,2 % so với chuyên gia 93,3 % (FinDVer). Khi ngữ cảnh thiếu, LLM thường trả lời sai thay vì từ chối (Joren, ICLR 2025).
  - *GreenScan:* mô hình chỉ đọc câu thành cấu trúc; thư viện code so sánh; luật kết luận; thiếu thì chuyển người. Chính đội đã đo: để LLM tự quyết lập trường trên HPG sinh 10 CONTRADICTED, phần lớn sai khi soát tay; có chốt thì 0.
  - *Giới hạn:* luật một mình phủ rất thấp (0,011 ngoài mẫu). Đó là lý do cần mô hình đọc.
- **Vặn:** "Model đời mới sẽ hết lỗi?" **Đáp:** Bài 30/09/2026 vẫn đo GPT-5.4 Pro chỉ 74,0 % trên phép đảo nhãn bằng số. Và kể cả khi đúng 99 %, kết luận vẫn phải giải thích được bằng phép tính.
- **Bẫy:** không nói "LLM không biết tính". Không nêu tên model tốt nhất của FinDVer (ACL Anthology và PDF ghi khác nhau).

**Q2. "GreenScan có phải RAG? Khác chatbot RAG ở đâu?"**
- **Trả lời:**
  - *Vấn đề:* RAG kinh điển tìm tài liệu rồi để LLM sinh câu trả lời tự do, và câu trả lời đó khó kiểm.
  - *Nguyên lý:* kiểm chứng là bài toán tuyên bố → bằng chứng → nhãn (FEVER), không phải sinh văn bản. Tương đồng chữ đo "giống", không đo "đúng".
  - *GreenScan:* truy xuất chỉ cho ứng viên (lấy 30, giữ 5). Bất biến 3 cấm điểm tương đồng tạo SUPPORTED hay CONTRADICTED. Mô hình chỉ điền IR dạng JSON, code kết luận. Gọi đúng là "kiểm chứng có truy xuất". Khi tắt LLM, 713 cặp từng bị gán "khớp một phần" chỉ vì giống chữ; đó là lý do có lệnh cấm.
  - *Giới hạn:* chưa đo chất lượng truy xuất trên gold.
- **Vặn:** "Vậy LLM sinh ra gì?" **Đáp:** JSON IR, không có verdict, không có điểm rủi ro.
- **Bẫy:** không nói "Hybrid RAG + reranker" đang chạy; cấu hình thật là `lite`, `reranker: none`.

**Q3. "Sao dùng BM25 + n-gram ký tự mà không dùng embedding hay Elasticsearch như paper ES-RAG?"**
- **Trả lời:**
  - *Vấn đề:* báo cáo tiếng Việt đầy tên chỉ số, mã văn bản, con số và đơn vị. OCR làm lỗi dấu và dính chữ. Máy demo là laptop chạy ngoại tuyến.
  - *Nguyên lý:* BM25 là baseline mạnh ở miền chuyên ngành; trên báo cáo khí hậu (ClimRetrieve), BM25 đạt 0,113 so với embedding tốt nhất 0,167. N-gram ký tự chịu được lỗi tách từ và mất dấu. Elasticsearch là *động cơ* và điểm mặc định của nó chính là BM25; paper ES-RAG chỉ hơn TF-IDF 0,51 điểm, không có khoảng tin cậy.
  - *GreenScan:* BM25 (k1 1,5; b 0,75) cộng TF-IDF n-gram 3–5, chạy ngay trong tiến trình. HPG 264 trang xong trong 107 s trên laptop không GPU. BGE-M3 chạy cục bộ mất ≈ 7,7 giờ cho cả thư viện; còn API embedding thì phải gửi toàn văn ra ngoài, nên để tắt.
  - *Giới hạn:* chưa so `lite` với dense trên gold (AG-5).
- **Vặn:** "Lên 1 000 doanh nghiệp thì sao?" **Đáp:** chuyển chỉ mục sang ES hoặc OpenSearch (BM25, lọc theo DN/năm, kNN, RRF). Hợp đồng đầu ra giữ nguyên, truy xuất vẫn không quyết.
- **Bẫy:** không dẫn ES-RAG làm bằng chứng độ chính xác. Không nói "embedding tiếng Việt X tốt nhất".

**Q4. "RRF là gì? k = 60 ở đâu ra? Sao vừa cộng trọng số vừa RRF?"**
- **Trả lời:**
  - *Vấn đề:* điểm BM25 không có trần, còn cosine nằm trong [0; 1], nên cộng thẳng là so táo với cam.
  - *Nguyên lý:* `RRF = Σ 1/(k + hạng)` chỉ dùng thứ hạng, nên không cần hiệu chỉnh thang điểm. k = 60 là giá trị kinh nghiệm của Cormack và cs. (SIGIR 2009), làm mềm chênh lệch giữa các hạng đầu.
  - *GreenScan:* BM25 được nén `s/(s+3)`, rồi tính 0,55 × BM25 + 0,45 × n-gram để có một điểm ổn định dùng làm ngưỡng (0,12). RRF k = 60 chỉ đổi thứ tự, không đổi điểm, nên ngưỡng kiểm chứng phía sau không trôi.
  - *Giới hạn:* trọng số và k chưa được chỉnh trên gold.
- **Vặn:** "0,55 / 0,45 tối ưu chưa?" **Đáp:** chưa. Đây là lựa chọn thiết kế, sẽ chỉnh bằng Recall@k chia theo công ty.
- **Bẫy:** không gọi trọng số là "tối ưu"; không nhầm RRF với trung bình điểm.

**Q5. "Truy xuất tốt tới đâu? Recall@k bao nhiêu? Có reranker không?"**
- **Trả lời:**
  - *Vấn đề:* bằng chứng không được tìm thấy thì không bao giờ được kiểm.
  - *Nguyên lý:* phải đo truy xuất tách khỏi kiểm chứng (Zhao, TOSEM 2026). Recall đo trên pool chỉ là cận dưới và thiên vị các hệ đã tạo ra pool (BEIR: Hole@10 của dense 31,8 % so với BM25 6,4 %).
  - *GreenScan:* nói thẳng là **chưa có Recall@k trên gold**. GS-Bench đưa sẵn câu bằng chứng, nên đo phần đọc và kết luận, không đo truy xuất. Có code reranker bge-reranker-v2-m3 nhưng mặc định tắt. Hệ thống luôn giữ 3 ứng viên tốt nhất dưới ngưỡng, có gắn cờ: chúng không tạo được SUPPORTED nhưng mang được bằng chứng bác bỏ ít trùng chữ (ca KLM).
  - *Giới hạn:* AG-5 (k nhỏ nhất đạt recall 95 %) chưa chạy.
- **Vặn:** "Sót bằng chứng thì sao?" **Đáp:** kết quả rơi về INSUFFICIENT hoặc chuyển người, không bao giờ thành SUPPORTED.
- **Bẫy:** không đưa ra "Recall = X %".

**Q6. "'Chưa đủ bằng chứng' có phải né tránh? Độ phủ 10–25 % thì có ích gì?"**
- **Trả lời:**
  - *Vấn đề:* đoán bừa về tuyên bố của doanh nghiệp có hậu quả pháp lý.
  - *Nguyên lý:* mọi benchmark kiểm chứng đều có lớp NEI. Dự đoán có từ chối được đo bằng cặp precision–độ phủ (Geifman & El-Yaniv). EmeraldMind cho thấy "94 % đúng" mà chỉ trả lời 19,5 % thì gây hiểu nhầm.
  - *GreenScan:* báo 3 số: precision trên phần dám kết luận, độ phủ, số kết luận sai nguy hiểm. Ngoài mẫu sạch: luật phủ 0,011; mô hình đọc + code phủ 0,115–0,253 và 0 sai, tức gấp 10–20 lần luật. Phần còn lại vào hàng đợi người kèm lý do (thiếu kỳ, lệch phạm vi…).
  - *Giới hạn:* kể cả đọc hoàn hảo (IR gold), độ phủ cũng chỉ 0,528.
- **Vặn:** "Sao không hạ ngưỡng?" **Đáp:** đây là đánh đổi trên đường độ phủ–precision. Ngưỡng đăng ký trước (C > 0,9; S > 0,8 theo cận dưới CI) vì vu oan đắt hơn bỏ lọt.
- **Bẫy:** không đọc 0,138 thành "13,8 % độ chính xác"; không giấu độ phủ.

**Q7. "Kiểm chứng khác NLI thế nào? Sao không dùng mô hình NLI hay fact-check có sẵn?"**
- **Trả lời:**
  - *Vấn đề:* cần biết bằng chứng ủng hộ, bác bỏ, hay chưa đủ.
  - *Nguyên lý:* NLI ba nhãn ánh xạ gần đúng sang S / R / NEI, nhưng "trung lập" không có nghĩa là sai. Mô hình ngoài miền rơi mạnh: huấn luyện trên FEVER chỉ đạt 38,78 % trên Climate-FEVER. mDeBERTa-xnli đạt 0,793 trên XNLI tiếng Việt, nhưng đó là câu dịch máy, không phải báo cáo ESG.
  - *GreenScan:* lập trường do cue và phép so số quyết. Cặp bất định mới gọi mô hình, kèm chốt `decisive=false`. Mô hình NLI nhỏ chỉ là TEST làm bộ lọc trước, đo bằng đường risk–coverage.
  - *Giới hạn:* chưa biết 151 SUPPORTS và 12 CONTRADICTS của mô hình đúng bao nhiêu.
- **Vặn:** "Sao không tinh chỉnh trên ViFactCheck?" **Đáp:** làm được (giấy phép MIT, κ 0,83), nhưng đó là miền tin tức; cần gold ESG để đo khả năng chuyển miền.
- **Bẫy:** không nói "NLI đạt 79 %" như thể đo trên báo cáo.

**Q8. "LLM giờ làm toán tốt, sao số học phải là của code? FinQA, TAT-QA nói gì?"**
- **Trả lời:**
  - *Vấn đề:* sai một bội số "nghìn" là kết luận ngược.
  - *Nguyên lý:* FinQA: mô hình 61,24 % so với chuyên gia 91,16 %; suy luận từ 3 bước trở lên chỉ 22,78 %. TAT-QA: 58,0 F1 so với 90,8. Chính các benchmark này tách "chọn số" khỏi "tính" (chương trình, toán tử).
  - *GreenScan:* trước khi tính, kiểm đủ các chiều: chỉ số, loại giá trị, đơn vị, kỳ, năm gốc, ranh giới tổ chức, Scope. Lệch một chiều thì cấm kết luận mâu thuẫn. Dung sai theo độ chính xác công bố; có bộ chuẩn hoá số tiếng Việt. 11/11 kết luận sai của 32B là do model tự thêm "nghìn", và code đã bắt được.
  - *Giới hạn:* còn 5 lỗi chuẩn hoá F4.
- **Vặn:** "Ngưỡng 0,35 quá rộng với kế toán?" **Đáp:** đúng, đã ghi thành lỗi F4-Q3 và đang chuyển sang chính sách theo loại giá trị. [CHƯA XÁC MINH cách xử lý vùng giữa dung sai và 0,35 trong code hiện tại]
- **Bẫy:** không nói "lệch dưới 35 % coi là khớp".

**Q9. "Làm sao chắc LLM xuất đúng JSON và không bịa số? Có dùng giải mã ràng buộc?"**
- **Trả lời:**
  - *Vấn đề:* model nhỏ hay hỏng cú pháp và, nguy hơn, sai nghĩa.
  - *Nguyên lý:* giải mã ràng buộc bảo đảm cú pháp, không bảo đảm nội dung. Lỗi thật của đội là lỗi nghĩa: "10.730 m3" thành "10.730 nghìn m3".
  - *GreenScan:* giải mã greedy ở nhiệt độ 0, prompt có khuôn JSON. Sau đó kiểm tất định: parse, enum, rồi `ground()` — số, bội số và năm phải được viết trong câu gốc, không thì để null và chuyển người. Kết quả trong mẫu: 32B precision 0,817 → 0,985, C sai 7 → 1. Guided decoding của vLLM đã bỏ vì tham số đổi theo phiên bản; probe Groq dùng `json_object` đạt 12/12.
  - *Giới hạn:* `ground` khắt khe nên làm giảm độ phủ.
- **Vặn:** "Năm nằm ở tiêu đề trang thì bỏ à?" **Đáp:** đúng, cố ý. Tập v1.2 từng có nhãn sai vì năm dính từ tiêu đề trang.
- **Bẫy:** không nói AG-1 "dùng giải mã ràng buộc ngữ pháp".

**Q10. "Mô hình 4B có đủ không? To hơn có tốt hơn?"**
- **Trả lời:**
  - *Vấn đề:* phải chạy ngoại tuyến vì tài liệu của khách chưa công bố.
  - *Nguyên lý:* điền khuôn có schema là việc mô hình nhỏ làm tốt. Qwen3 0,6–8B tinh chỉnh đạt 98,7 % trên nhiễu số (Aarnes & Setty 2026).
  - *GreenScan:* ngoài mẫu sạch, độ phủ 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253, và tất cả precision 1,0. Bản Q4 chạy cục bộ khớp bf16 96,3 %; 1,7 s/câu trên T4. Hai model 0,6B và 1,7B zero-shot không dùng được (precision 0,39 và 0,54).
  - *Giới hạn:* n nhỏ; chưa đo tốc độ trên laptop vì thiếu RAM; tập hiệu chỉnh lệch về 32B.
- **Vặn:** "Sao không dùng 32B?" **Đáp:** không chạy được trên laptop. Groq chỉ dùng cho báo cáo công khai. 32B còn 1 SUPPORTED sai trên G.
- **Bẫy:** không nói "không có hiệu ứng quy mô" hay "4B bằng 32B".

**Q11. "Có fine-tune hay chưng cất không? Dạy cái gì? QLoRA là gì?"**
- **Trả lời:**
  - *Vấn đề:* muốn bỏ phụ thuộc vào mô hình đám mây.
  - *Nguyên lý:* chưng cất là học trò học từ đầu ra của thầy. QLoRA giữ trọng số gốc ở 4-bit và chỉ học `ΔW = (α/r)·B·A`.
  - *GreenScan:* chỉ dạy phần **đọc**, không bao giờ dạy ra verdict. Đã có học trò T1 (e5-base) đạt macro-F1 0,71–0,73 trên nhãn Claude, chia theo công ty, n = 1 217, 3 seed; chưa nối sản phẩm. AG-4 (QLoRA Qwen3 trên IR của thầy, chỉ giữ IR mà `irlib` chạy ra đúng đáp án) **chưa chạy**.
  - *Giới hạn:* học trò trên dữ liệu do LLM sinh có thể mất 3–8 điểm (Li và cs. 2023).
- **Vặn:** "Sao không train ra verdict?" **Đáp:** verdict phải chỉ ra được phép tính; một model nói "CONTRADICTED" thì không chỉ ra được vì sao.
- **Bẫy:** không nói "đã QLoRA"; không đọc siêu tham số khi hai tài liệu còn ghi α khác nhau.

**Q12. "Nhãn do Claude gán — LLM chấm LLM có thiên lệch không?"**
- **Trả lời:**
  - *Vấn đề:* LLM làm giám khảo có thiên lệch vị trí, độ dài và tự ưu tiên. Chỉ cần đảo thứ tự là Vicuna-13B "thắng" ChatGPT 66/80 (Wang 2024).
  - *Nguyên lý:* giảm phần phán đoán của LLM bằng nhãn theo cấu trúc và kiểm tất định.
  - *GreenScan:*
    1. Ở B-b, lấy ô bảng thật rồi gây nhiễu có kiểm soát, nên nhãn S / C / N biết trước nhờ cách dựng.
    2. Claude chỉ đọc IR của câu bằng chứng, rồi qua bộ kiểm tất định.
    3. Ở cặp thật: hai lượt mù cộng phân xử, người đọc thứ hai là model khác (Qwen3-32B).
    4. Hệ được chấm là Qwen3, không phải Claude.
    5. Soát tay 14 ca.
  - *Giới hạn:* hai lượt cùng model cho κ 0,92, nhưng đó là ổn định, không phải đúng; Claude với gemma chỉ đạt κ 0,63.
- **Vặn:** "Có người kiểm không?" **Đáp:** theo quyết định ngày 04/11, nhãn Claude được dùng như bộ dữ liệu và người duyệt đọc lại. Khi trình bày, nói "Claude gán, người soát N ca" với N là số đã soát thật.
- **Bẫy:** không gọi là "gold"; không gọi số trên B-b hay B-c là "độ chính xác".

**Q13. "Có xác suất hay độ tin cậy không? Sao không dùng mức tự tin LLM tự khai?"**
- **Trả lời:**
  - *Vấn đề:* cần biết khi nào máy được phép kết luận.
  - *Nguyên lý:* độ tin cậy tự khai thường quá cao, AUROC chỉ 0,52–0,61 (Xiong 2024). Một bộ hiệu chỉnh riêng tốt hơn xác suất của chính model (Kamath: 56 % so với 48 % ở accuracy 80 %).
  - *GreenScan (AG-2):* dùng tín hiệu quan sát được — hai đường độc lập có khớp nhau không. Ước P(đúng) theo xô, trên dự đoán ngoài fold chia theo công ty. Chỉ kết luận khi cận dưới CI95 > 0,9 (C) hoặc > 0,8 (S). Luật + 4B trên G: 0 sai, phủ 0,093, phần tăng phủ có CI [0,016; 0,185].
  - *Giới hạn:* xô mỏng (bản 4 đường đã trượt cổng); 15/15 đúng chỉ cho cận dưới khoảng 0,80.
- **Vặn:** "Sao ngưỡng C cao hơn S?" **Đáp:** vu oan đắt hơn bỏ lọt, và CONTRADICTED luôn bật cờ chuyển người.
- **Bẫy:** không hiển thị "độ tin cậy 95 %".

**Q14. "Precision 1,0 — có quá đẹp không? n bao nhiêu?"**
- **Trả lời:**
  - *Vấn đề:* tỷ lệ trên mẫu nhỏ dao động lớn.
  - *Nguyên lý:* khoảng Wilson và "quy tắc ba". Các ca của cùng một doanh nghiệp không độc lập, nên phải bootstrap theo công ty.
  - *GreenScan:* mỗi model chỉ dám kết luận 10–22 ca, đúng hết, nên cận dưới 95 % là 0,72–0,85; độ phủ 4B có CI [0,045; 0,314]. Dự đoán ghi trước trong `configs/measurement_decisions.yaml`, và đội báo cả dự đoán sai (4B phủ ≥ 0,35; "không có hiệu ứng quy mô").
  - *Giới hạn:* tuyên bố sinh từ khuôn câu, chỉ 5–9 DN.
- **Vặn:** "Hơn luật có ý nghĩa thống kê không?" **Đáp:** phần tăng độ phủ có CI không chứa 0; còn precision thì chưa phân biệt được.
- **Bẫy:** không nói "chính xác 100 %".

**Q15. "Chống rò rỉ dữ liệu và quá khớp thế nào?"**
- **Trả lời:**
  - *Vấn đề:* các câu trong cùng một báo cáo rất giống nhau.
  - *Nguyên lý:* chia ngẫu nhiên cho ước lượng quá lạc quan (Søgaard 2021). 30 % câu test trùng gần với train (Lewis 2021).
  - *GreenScan:* chia theo công ty; prompt đóng băng; đăng ký dự đoán trước. Mỗi lần sửa (`ground`, C-guard) thì thử lại trên một tập ngoài mẫu **mới**: 246 ca → G 162 ca → v1.3 87 ca.
  - *Giới hạn:* các tập mới đều nhỏ và có lỗi chỉ phát hiện khi hậu kiểm (37 % `other_env`).
- **Vặn:** "C-guard sửa sau khi thấy lỗi?" **Đáp:** đã đăng ký thành v1.2, rồi chạy trên G chưa thấy, và mọi dự đoán đứng vững.
- **Bẫy:** không nói "tổng quát cho mọi ngành"; B-b chưa có ngành phát thải cao.

**Q16. "Bảng trong PDF đọc thế nào?"**
- **Trả lời:**
  - *Vấn đề:* bảng bị dàn phẳng làm số của hàng, cột khác dính vào nhau.
  - *Nguyên lý:* suy luận trên bảng còn xa người (TabFact 65,1 % so với 92,1 %). FinDVer: 66–71 % tuyên bố cần bằng chứng từ bảng. TATR tốt nhất cho bảng tài chính.
  - *GreenScan:* bảng dàn phẳng từng khiến cả 4 model ≥ 26B báo SUPPORTED sai. AG-3 dựng lại hàng từ toạ độ chữ, cộng dọc khớp 3/3; trên 7 ca, trang thô đúng 1/7, dựng lại đúng 3/7, 0 sai. Bảng không qua kiểm tổng thì không được dùng để kết luận.
  - *Giới hạn:* dự đoán ≥ 5/7 sai; IR còn thiếu chiều "mảng".
- **Vặn:** "Sao không dùng VLM?" **Đáp:** VLM mở còn yếu với bảng và biểu đồ (Gupta 2025, kết quả âm); để TEST cho trang ảnh.
- **Bẫy:** không nói "đã giải xong bảng".

**Q17. "Bộ nhận diện tuyên bố có bỏ sót không?"**
- **Trả lời:**
  - *Nguyên lý:* bộ trích theo từ khoá hụt recall: SVM n-gram 69–71 so với transformer 84–85, chênh recall tới 25 điểm (Stammbach, ACL 2023).
  - *GreenScan:* so với nhãn Claude, luật có precision 55 % và recall 69 %. Học trò T1 đạt 0,71–0,73 nhưng chưa nối sản phẩm. Cách đo đúng là soát mẫu các câu luật **không** trích.
  - *Giới hạn:* 0/79 câu có nhãn người.
- **Vặn:** "Sao học trò chưa vào sản phẩm?" **Đáp:** ngưỡng là macro-F1 ≥ luật và recall cao hơn luật ≥ 10 điểm trên gold, mà gold thì chưa có.
- **Bẫy:** không nói "nhận diện 100 % tuyên bố".

**Q18. "Có tái lập được không? Chạy lại có ra kết quả khác?"**
- **Trả lời:**
  - *Nguyên lý:* API có thể không tất định kể cả ở nhiệt độ 0; lượng tử hoá làm đổi một phần đầu ra.
  - *GreenScan:* đã đo GLM-5.2 cho 17/19 rồi 16/19, nên mô hình không được quyết. Bộ đọc cục bộ dùng greedy, seed 0. Manifest ghi hash đầu vào, phiên bản corpus, gói luật, prompt và model (bất biến 10). Q4 khớp bf16 96,3 %.
  - *Giới hạn:* 3,7 % lệch có thể đổi kết luận ở biên, nhưng vẫn phải qua luật.
- **Bẫy:** không nói "nhiệt độ 0 nên tất định".

**Q19. "Giải thích cho kiểm toán viên có làm họ tin máy quá mức không?"**
- **Trả lời:**
  - *Nguyên lý:* người kiểm chứng cần lần được đường suy luận, bằng chứng và thông tin còn thiếu (Warren, CHI 2025). Giải thích làm người chấp nhận khuyến nghị bất kể đúng sai (Bansal 2021). Giải thích chỉ có ích khi làm rẻ việc kiểm (Vasconcelos 2023). Kiểm toán viên lại xem nhẹ AI (Commerford 2022).
  - *GreenScan:* hiện nguyên văn bằng chứng, trang, quy tắc đã chạy, phép tính và phần còn thiếu; huy hiệu "hai đường khớp/lệch". Không dùng văn do LLM viết làm lý do.
  - *Giới hạn:* chưa có thí nghiệm người dùng.
- **Bẫy:** không nói "giải thích giúp kiểm toán viên chính xác hơn".

**Q20. "Tài liệu có thể cài lệnh (prompt injection) thì sao?"**
- **Trả lời:**
  - *Nguyên lý:* chèn lệnh gián tiếp qua tài liệu mà LLM đọc (Greshake 2023) [KIẾN THỨC NỀN].
  - *GreenScan:* mỗi đoạn truy xuất mang cờ `suspicious_instruction`; mô hình không quyết verdict; số phải khớp nguyên văn câu gốc (`ground`).
  - *Giới hạn:* bộ phát hiện là heuristic, chưa red-team [CHƯA XÁC MINH độ phủ].
- **Bẫy:** không nói "miễn nhiễm prompt injection".

**Q21. "Dùng tài nguyên tiếng Việt nào? Giấy phép ra sao?"**
- **Trả lời:**
  - *Nguyên lý:* trên VN-MTEB (dịch máy), e5-large-instruct đạt 40,88, bge-m3 39,84, AITeamVN 34,18; trên Zalo legal (tự báo) thứ hạng lại đảo. Chỉ gold của chính mình mới quyết được.
  - *Giấy phép:* environmental_claims, AVeriTeC, XNLI, QuanTemp, ViANLI là phi thương mại; phobert-base-v2 dùng AGPL; ViFactCheck dùng MIT.
  - *GreenScan:* hôm nay chạy `lite`, không dùng mô hình; các ứng viên đều ở mức TEST.
  - *Giới hạn:* đội chưa tìm thấy công trình NLP công bố về kiểm chứng tuyên bố ESG trên báo cáo tiếng Việt (tính đến 10/2026).
- **Bẫy:** không nói "chưa từng có nghiên cứu nào".

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

### 5.1 Mâu thuẫn giữa các tài liệu (thống nhất trước 10/11)
1. **Giải mã JSON.** [TP] §5 ghi "ràng buộc ngữ pháp JSON", [KH] §5 AG-1 ghi "vLLM guided JSON". Nhưng [P03] §4 và code AG-1 không dùng guided decoding (greedy cộng `ground()`). Nói theo code.
2. **QLoRA.** [TP] §5 ghi rank 16–32, α = 32, dropout 0,05; [P13] §3 ghi r = 32, α = 16, lr 1e-4. AG-4 chưa chạy, nên không đọc số nào.
3. **Số bẫy.** Checklist và yaml ghi 17 "bẫy xanh"; [INV] bất biến 4 và [TP] ghi 44 trap; tệp test có 47 hàm [P05] §6.
4. **Luật trên 51 ca dựng.** Có nơi ghi "đúng 20/32 và 7/19" ([P05] §5; [KH] §10 AG-0), nơi khác ghi "quyết định 8/32 (đúng 6) và 3/19 (đúng 3)" ([KH] §2 F2). Đây là hai phép đo khác nhau (có tính ca chuyển người đúng hay không) [CHƯA XÁC MINH]. Phải nói rõ đang dùng phép đo nào.
5. **ClimateFEVER-VN.** [05] §3 ghi 13,25 so với 21,27, nhưng phụ lục [TQ] nói không trích số từng bộ con của VN-MTEB vì PDF quá nhỏ. Số trong [05] không rõ nguồn [CHƯA XÁC MINH]; không dùng.
6. **Ngưỡng số.** [P05] §3 ghi "lệch ≥ 0,35 thì bác bỏ". [P05] §4 ghi đã bỏ ngưỡng 35 % cố định (D-2026-09-18-03). [KH] F4-Q3 ghi "0,35 che chênh 9–25 %". Cần kiểm code hiện tại [CHƯA XÁC MINH].
7. **Truy vấn nhiều họ.** [RP] mô tả họ truy vấn ủng hộ / mâu thuẫn / có cấu trúc, tìm bằng chứng phủ định bắt buộc và `MISSING_REQUIRED`, nhưng grep `src/` ra 0 kết quả. Retriever hiện chỉ truy vấn bằng câu tuyên bố. Phải gọi đây là thiết kế đích.
8. **PhoBERT.** [TP] §3.2 đề xuất NLI dùng PhoBERT hoặc ViDeBERTa; [P13] §4 ghi bỏ PhoBERT vì AGPL. Thực ra chỉ phobert-base-v2 là AGPL, bản v1 dùng MIT ([TQ] §4.5).
9. **Dải confidence.** Các dải trong [VP] §8 chưa được hiệu chỉnh, và khác khái niệm P(đúng) theo xô của AG-2. Không trình bày các dải này như xác suất.
10. **Gold T1.** [P02] §9 và [P13] §9 hẹn gán gold T1 lô 1 trước 14/10 hoặc 22/10, nhưng [KH] §0 ghi 0/79 tới 31/10.
11. **AG-3.** Câu "trang thô đúng 1/7 với 0 kết luận" ([KH] §10) khó hiểu; hỏi lại người chạy trước khi đưa lên slide.
12. **FinDVer.** ACL Anthology ghi GPT-4o là model tốt nhất, còn PDF ghi Claude-3.5-Sonnet ([TQ] §2.4).

### 5.2 Số đã cũ → số mới (31/10–01/11)

| Tài liệu | Câu hoặc số cũ | Thay bằng |
|---|---|---|
| [P03] §5, §8 | 4B 0,134 / 1,0; 32B 0,423 / 0,82 / 7 C sai; "chưa model nào qua cổng" | Sau `ground` (trong mẫu): 4B 0,437 / 0,984; 32B 0,985, 1 C sai. Ngoài mẫu v1.1: chỉ 8B qua cổng. G: 0 C sai ở cả 4 model. v1.3 sạch: phủ 0,115–0,253, precision 1,0 |
| [KH] §10 "14:15" | "Mọi model ≥ 4B qua cổng"; "hiệu ứng cỡ gần như biến mất" | Chỉ đúng trong mẫu. Ngoài mẫu v1.1, độ phủ tăng theo cỡ (0,126 → 0,329). v1.3 sạch không đơn điệu (4B 0,138; 8B và 14B 0,115; 32B 0,253) |
| [KH] §10 "23:25" và §11 | "4B mất độ phủ vì đọc sai năm" | Đã rút lại ngày 01/11: đó là lỗi của tập |
| [05] §2, §6; [TP] §3; [P06] §3–4 | GLM-5.2 qua FPT là đường LLM; Vietnamese_Embedding qua FPT "đang dùng" | Khoá FPT bị 401 từ 31/10. Thầy và người đọc thứ hai là Qwen3-32B-AWQ trên Kaggle. Demo chạy `offline`; embedding là `lite` |
| [05] §6 câu 6; [TQ] §7(c) câu 6 | "Gold do người gán, có κ và hoà giải" | 0 nhãn người. Nhãn Claude (bạc) đang được người duyệt đọc lại |
| [TP] §8 | Tới Chung kết: SFT Qwen3 1,7B, gold 100–150, B3 retrieval | Chưa làm: AG-4 và AG-5 chưa chạy, gold 0 |
| [KH] §5, dự đoán AG-2 | Độ phủ ≈ 25 % → ≥ 50 % ở cùng precision | Trên G, luật + 4B chỉ phủ 0,093 (precision 1,0). Dự đoán không đạt |
| [P03] §9 | Dự đoán "4B phủ ≥ 0,35" | Sai: 0,134, rồi 0,138 ngoài mẫu sạch |

### 5.3 Điều không được nói
1. "GreenScan phát hiện hoặc chứng minh doanh nghiệp X tẩy xanh hay vi phạm" (bất biến 1).
2. "Độ chính xác X %" hay "100 %" cho số trên GS-Bench hoặc nhãn Claude. Phải nói: "precision trên phần dám kết luận, trên ca dựng, n = …, CI …" ([KH] §4).
3. "Có gold người, κ = …" — hiện chưa có nhãn người nào.
4. "Recall truy xuất = X %"; "Hybrid RAG + BGE-M3 + reranker đang chạy".
5. "LLM xác minh tuyên bố"; "AI đọc hiểu toàn bộ báo cáo"; "mô hình quyết định kết luận".
6. "Đã fine-tune hay QLoRA bộ đọc IR"; "AG-1 dùng giải mã JSON ràng buộc ngữ pháp".
7. "Bộ đọc mô hình đã chạy trong bản demo" — chưa: bị chặn vì thiếu RAM, chờ cổng 06/11.
8. "Không có hiệu ứng quy mô" hay "4B bằng 32B".
9. "ES-RAG chứng minh Elasticsearch tăng độ chính xác đáng kể".
10. "Mô hình tự tin 95 %", hay trình bày dải confidence như xác suất.
11. "Tốt hơn baseline" khi chênh dưới 10–15 điểm trên mẫu nhỏ; so trực tiếp với số trong paper tiếng Anh.
12. "Chưa từng có nghiên cứu nào…"
13. "Lượng tử giúp truy xuất hay kiểm chứng". Bảng cấm của [INV] không cho thêm quantum "chỉ để trông AI hơn". Cần hỏi đội ý nghĩa các tên `quantum_gw` và `QUANTUM_VERIFY` để trả lời nếu BGK hỏi [CHƯA XÁC MINH].
14. Trình bày kết quả ZAIC như kết quả của GreenScan.
15. Dùng dữ liệu phi thương mại hoặc AGPL cho định hướng thương mại.
