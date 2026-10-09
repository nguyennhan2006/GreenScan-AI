# GreenScan AI: tổng quan tài liệu khoa học AI/NLP (2019–2026)

*Lập ngày 05/10/2026 cho nhóm AQ2026-119. Mục đích: (1) căn cứ khoa học cho các quyết định thiết kế, (2) thiết kế đo lường trên gold set nhỏ, (3) chuẩn bị Q&A với Ban giám khảo.*

---

## 0. Cách đọc tài liệu này

**Nhãn đánh giá cho từng nguồn (verdict cho GreenScan):**

- **ADOPT**: dùng ngay, làm căn cứ thiết kế hoặc thực hành đo lường.
- **TEST**: đáng làm một ablation sau khi đã có gold.
- **AVOID**: không nên dùng (có ghi lý do).
- **CONTEXT**: kiến thức nền để trả lời Ban giám khảo.

**Quy ước kiểm chứng:**

- Mỗi nguồn đã được đối chiếu trực tiếp với arXiv, ACL Anthology, trang nhà xuất bản/DOI (Crossref, Semantic Scholar) hoặc Hugging Face/GitHub vào ngày 05/10/2026.
- Số liệu lấy từ abstract, bảng kết quả trong PDF hoặc model card.
- **[UNVERIFIED]**: chưa xác minh được từ nguồn gốc, thường là licence.
- **[self-reported]**: số do tác giả model card tự công bố, chưa có peer review.
- **[tự tính]**: phép tính minh hoạ của người lập, không phải số trong paper.

**Lưu ý về một trích dẫn nhóm đang dùng.** `docs/research/README.md` trích arXiv:2411.19463 (Zhao et al. 2024). Bài này đã đổi tên và đã được xuất bản:

- v1 (29/11/2024): *"Towards Understanding Retrieval Accuracy and Prompt Quality in RAG Systems"*.
- v3 (29/05/2026): *"Understanding the Fundamental Design Decisions of Retrieval-Augmented Generation Systems"*, ACM TOSEM 2026.

Nên ghi rõ phiên bản đang trích (xem [S2.5b]).

---

## Tóm tắt điều hành: 10 điều quan trọng nhất

1. **Chưa có bộ dữ liệu "greenwashing đã được xác minh" nào.** Survey mới nhất (Calamai et al., v2 01/2026) khuyến nghị pipeline phân rã thành các bước, truy vết được và có con người giám sát. Đây đúng là kiến trúc GreenScan đang theo.
2. **Không nên để LLM so sánh số.** Độ chính xác của LLM giảm tới 62% khi số liệu bị nhiễu (NumPert 2025). Các mô hình frontier chỉ đạt khoảng 74% trên phép đảo nhãn bằng số (Aarnes & Setty 2026). FinQA với chuỗi suy luận từ 3 bước trở lên chỉ đạt 22.78%. Bộ so sánh số tất định (deterministic numeric comparator) có căn cứ vững.
3. **NEI/INSUFFICIENT_EVIDENCE là nhãn bắt buộc** (FEVER, SciFact, AVeriTeC, Climate-FEVER). Khi ngữ cảnh không đủ, các LLM lớn thường vẫn trả lời thay vì từ chối (Joren et al., ICLR 2025). Vì vậy nên giữ quy tắc "không đủ bằng chứng" ở phần rule, không giao cho LLM.
4. **Cần nhãn riêng cho claim "đúng một phần / cherry-picking".** AVeriTeC có lớp *Conflicting Evidence/Cherry-picking*, Climate-FEVER có *DISPUTED*. Quy tắc gộp nhãn tất định của hai bộ này gần như trùng với logic CONTRADICTED / PARTIALLY_SUPPORTED của GreenScan.
5. **Bộ trích claim dựa từ khoá sẽ bỏ sót claim.** Trên tiếng Anh, SVM n-gram đạt F1 khoảng 69–71, còn transformer khoảng 84–85. Khoảng cách recall lên tới 25 điểm vì "không phải claim môi trường nào cũng chứa từ khoá" (Stammbach et al., ACL 2023). Cần đo recall của bộ trích claim heuristic.
6. **κ ≥ 0.7 là mục tiêu cao so với các bộ dữ liệu cùng loại:** environmental claims α = 0.47, Climate-FEVER α = 0.334, AVeriTeC κ = 0.619, FEVER Fleiss κ = 0.684. Đạt được thì là điểm mạnh. Không đạt thì báo cáo trung thực, kèm theo agreement của từng lớp.
7. **Với n = 60–100, khoảng tin cậy 95% của accuracy rộng khoảng ±8–11 điểm %. Hai hệ thống phải chênh khoảng 10–16 điểm % mới phân biệt được** [tự tính]. Claim lấy từ cùng một công ty không độc lập với nhau nên cần cluster bootstrap theo công ty. Sai số chuẩn có cụm có thể lớn hơn 3 lần sai số chuẩn ngây thơ (Miller 2024).
8. **Recall retrieval đo bằng pooled judgments chỉ là cận dưới.** Nếu pool chỉ gồm BM25/char n-gram thì dense retriever bị đánh giá thấp một cách hệ thống. Trong BEIR, tỷ lệ tài liệu chưa được gán nhãn trong top-10 (Hole@10) của dense lên tới 31.8%, của BM25 là 6.4%.
9. **Embedding tiếng Việt: thứ hạng đổi theo benchmark.** Trên VN-MTEB (dịch máy từ MTEB), bge-m3 hơn AITeamVN/Vietnamese_Embedding ở retrieval (39.84 so với 34.18). Trên Zalo legal, model card của AITeamVN lại báo điều ngược lại (Acc@1 0.727 so với 0.568) [self-reported]. Chỉ nên chọn mô hình dựa trên gold của chính GreenScan.
10. **Mô hình nhỏ thay hoặc tiền lọc LLM là khả thi nhưng phải TEST:**
    - mDeBERTa-v3-base-xnli (~279M, MIT, XNLI-vi 0.793) cho NLI tiền lọc;
    - MiniCheck-Flan-T5-L (770M, MIT; LLM-AggreFact 75.0 so với GPT-4o 75.9, nhưng chỉ tiếng Anh);
    - PhoRanker (~0.1B) hoặc bge-reranker-v2-m3 cho rerank.

    Không mô hình nào được làm nhãn quyết định khi chưa qua A/B trên gold.

---

## 1. Phát hiện greenwashing bằng NLP/LLM

### 1.1 Survey tổng quan

**[S1.1] Moodaley, W., & Telukdarie, A. (2023).** *Greenwashing, Sustainability Reporting, and Artificial Intelligence: A Systematic Literature Review.* Sustainability, 15(2), 1481. https://doi.org/10.3390/su15021481

- **Nội dung:** phân tích bibliometric và thematic về giao thoa AI/ML, greenwashing và báo cáo bền vững, kèm một khung khái niệm.
- **Kết luận chính:** việc dùng AI cho greenwashing trong báo cáo bền vững là *"an underexplored research field"*.
- **Với GreenScan:** câu mở đầu tốt cho phần "khoảng trống nghiên cứu". Đây là survey thư mục học, không có kết quả mô hình.
- **Verdict: CONTEXT.**

**[S1.2] Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M. (2025; v2 29/01/2026).** v1: *Corporate Greenwashing Detection in Text – a Survey*; v2: *Detecting Greenwashing: A Natural Language Processing Literature Survey.* arXiv:2502.07541 (working paper, 42 trang). https://arxiv.org/abs/2502.07541

- **Nội dung:** coi greenwashing là tập các "climate NLP tasks" trung gian, từ phát hiện chủ đề khí hậu đến nhận diện mẫu giao tiếp gây hiểu lầm.
- **Kết luận chính:**
  - Một số subtask đạt hiệu năng gần hoàn hảo trong điều kiện kiểm soát. Các task có tính mơ hồ, chủ quan hoặc cần suy luận vẫn khó.
  - *"no dataset of verified greenwashing cases currently exists"*.
  - Khuyến nghị dùng đánh giá của bên thứ ba (báo chí đã kiểm chứng, hồ sơ cơ quan quản lý) và *"decomposed pipelines that support human oversight, traceable reasoning, and efficient model design"*.
- **Với GreenScan:** đây là căn cứ mạnh nhất cho kiến trúc phân rã (extract → retrieve → numeric → stance → legal → risk → hàng đợi kiểm toán viên). Khi trích dẫn nên dùng tên v2.
- **Verdict: ADOPT** (làm khung lập luận) **+ CONTEXT.**

### 1.2 Dòng nghiên cứu ClimateBERT (nhóm Leippold, Đại học Zurich)

**[S1.3] Webersinke, N., Kraus, M., Bingler, J. A., & Leippold, M. (2021/2022).** *ClimateBERT: A Pretrained Language Model for Climate-Related Text.* arXiv:2110.12010. https://arxiv.org/abs/2110.12010

- **Nội dung:** DistilRoBERTa được tiếp tục pretrain trên hơn 2 triệu đoạn văn về khí hậu (tin tức, bài nghiên cứu, báo cáo khí hậu của doanh nghiệp). Mô hình có 82M tham số (theo [S1.6]).
- **Kết quả:** objective MLM cải thiện 48%; sai số trên các task phân loại, sentiment và fact-checking giảm 3.57%–35.71%.
- **Bổ sung mới nhất:** *Climate-ModernBERT* (Yu, Raj, Ni, Vaghefi, Stammbach, Leippold; arXiv:2609.07798, 07/09/2026) đạt 76.3 F1 trung bình trên 9 benchmark khí hậu, hơn ModernBERT thường 2.8 điểm. Thông điệp: domain-adaptive pretraining mang lại vài điểm, không làm thay đổi bản chất bài toán.
- **Với GreenScan:** chỉ hỗ trợ tiếng Anh, không dùng trực tiếp được cho báo cáo tiếng Việt.
- **Verdict: CONTEXT** (AVOID nếu định dùng trực tiếp cho tiếng Việt).

**[S1.4] Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).** *Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures.* Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776

- **Kết luận chính:** với các doanh nghiệp ủng hộ TCFD, *"the firms' TCFD support is mostly cheap talk and … firms cherry-pick to report primarily non-material climate risk information"*.
- **Công trình tiếp theo:** Bingler et al. (2024), *How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk*, Journal of Banking & Finance 164, 107191 (https://doi.org/10.1016/j.jbankfin.2024.107191). Thước đo ClimateBertCTI trên báo cáo thường niên của MSCI World cho thấy:
  - công bố tự nguyện đi kèm nhiều cheap talk hơn;
  - cheap talk tương quan với tin tức tiêu cực và tăng trưởng phát thải cao hơn;
  - chỉ engagement có mục tiêu cụ thể mới gắn với ít cheap talk hơn.
- **Dữ liệu công khai:** `climatebert/climate_specificity` và `climatebert/climate_commitments_actions`, mỗi bộ 1,320 đoạn (1,000 train / 320 test), CC BY-NC-SA 4.0.
- **Với GreenScan:**
  - Hai khái niệm *cheap talk* (nói mà không có hành động/số liệu) và *cherry-picking* (chọn lọc thông tin) là ngôn ngữ chuẩn để giải thích risk rubric với Ban giám khảo.
  - Đặc trưng "specificity" (claim có số liệu/cam kết cụ thể hay không) có thể thành một feature rủi ro.
- **Verdict: CONTEXT; TEST** (feature specificity, huấn luyện cross-lingual).

**[S1.5] Stammbach, D., Webersinke, N., Bingler, J. A., Kraus, M., & Leippold, M. (2023).** *Environmental Claim Detection.* Proceedings of ACL 2023 (Vol. 2: Short Papers), tr. 1051–1066. https://aclanthology.org/2023.acl-short.91/

- **Dữ liệu:**
  - 3,000 câu từ báo cáo bền vững, báo cáo thường niên và earnings calls của các công ty niêm yết.
  - 16 chuyên gia gán nhãn, mỗi câu 4 người; loại 353 câu hoà phiếu (11.7%), còn 2,647 câu (2,117 / 265 / 265), 25% là claim.
  - Krippendorff α = 0.47 ("moderate").
  - Định nghĩa claim lấy theo Uỷ ban châu Âu (hướng dẫn Directive 2005/29/EC).
- **Kết quả (F1 trên test):**

| Mô hình | F1 |
|---|---|
| TF-IDF SVM | 69.1 |
| Character n-gram SVM | 70.9 |
| DistilBERT | 83.7 |
| ClimateBERT | 83.8 |
| RoBERTa-large | 84.9 (acc 91.7) |
| Mô hình ClaimBuster (train ngoài miền) | 33.9 |
| Mô hình pledge detection (train ngoài miền) | 26.4 |

  - Tác giả viết: *"not all environmental claims contain distinguishing environmental keywords"*. Khoảng cách recall giữa transformer và SVM lên tới 25 điểm.
- **Tài nguyên:**
  - Dataset `climatebert/environmental_claims`: CC BY-NC-SA 4.0. Phần mô tả trong card ghi 2,400/300/300, nhưng dataset viewer hiện 2,647 dòng, khớp với paper.
  - Model `climatebert/environmental-claims`: 82.3M tham số, Apache-2.0.
- **Với GreenScan:**
  1. Dùng định nghĩa của EC trong hướng dẫn gán nhãn.
  2. Bộ trích claim heuristic giống SVM từ khoá, nên dự kiến hụt recall. Cần lấy mẫu ngẫu nhiên các câu không được trích để đo recall.
  3. Có thể thử bộ phân loại đa ngôn ngữ (mDeBERTa/XLM-R) fine-tune trên dữ liệu dịch cộng một ít câu tiếng Việt, dùng làm "recall booster".
- **Verdict: ADOPT** (định nghĩa, đo recall) **/ TEST** (classifier cross-lingual).

**[S1.6] Schimanski, T., Bingler, J., Hyslop, C., Kraus, M., & Leippold, M. (2023).** *ClimateBERT-NetZero: Detecting and Assessing Net Zero and Reduction Targets.* EMNLP 2023, tr. 15745–15756. https://aclanthology.org/2023.emnlp-main.975/

- **Dữ liệu:** 3.5K mẫu (990 net zero, 1,005 reduction, 1,522 no target) từ dự án Net Zero Tracker. HF `climatebert/netzero_reduction_data`: 3,441 dòng, Apache-2.0 theo card.
- **Kết quả phân loại (accuracy):** ClimateBERT (82M) 0.966; RoBERTa-base 0.963; GPT-3.5-turbo 0.938. Kiểm tay 300 câu từ báo cáo bền vững cho thấy 98% đúng.
- **Kết quả trích xuất bằng QA** (RoBERTa-base-squad2, dữ liệu thô):

| Trường cần trích | Accuracy |
|---|---|
| Năm net zero | 0.95 |
| Năm mục tiêu giảm phát thải | 0.84 |
| % giảm | 0.88 |
| Năm gốc (base year) | 0.68 (yếu nhất) |

- **Với GreenScan:** claim về mục tiêu (target) là một loại claim riêng. Việc năm gốc khó trích nhất củng cố quy tắc "period eligibility" của bộ so sánh số: thiếu năm gốc thì không được so sánh.
- **Verdict: TEST** (loại claim target/reduction) **+ CONTEXT.**

### 1.3 Hệ thống LLM trên báo cáo bền vững

**[S1.7] Ni, J., Bingler, J., Colesanti-Senni, C., Kraus, M., Gostlow, G., Schimanski, T., Stammbach, D., Vaghefi, S. A., Wang, Q., Webersinke, N., Wekhof, T., Yu, T., & Leippold, M. (2023).** *CHATREPORT: Democratizing Sustainability Disclosure Analysis through LLM-based Tools.* EMNLP 2023 System Demonstrations, tr. 21–51. https://aclanthology.org/2023.emnlp-demo.3/

- **Pipeline:**
  - Chunk 500 ký tự (overlap 20), embedding bằng text-embedding-ada-002, lấy top-20 chunk.
  - ChatGPT trả lời 11 khuyến nghị TCFD kèm số nguồn.
  - Chuyên gia tham gia vòng chỉnh prompt.
- **Đánh giá con người** (10 báo cáo, 110 cặp hỏi-đáp):

| | ChatGPT | GPT-4 |
|---|---|---|
| Tỷ lệ không hallucination (nội dung) | 83.63% | 69.09% |
| Tỷ lệ không hallucination (nguồn) | 75.00% | 72.37% |
| κ khi gán nhãn hallucination | 0.54 | 0.21 |

  - Hallucination chủ yếu đến từ *ngoại suy* và từ việc *ghép sai hai chunk*.
  - Hệ thống đã phân tích 1,015 báo cáo.
- **Với GreenScan:**
  - Ủng hộ nguyên tắc trả lời theo kiểu trích xuất, có số trang.
  - Cảnh báo cụ thể: không để một verdict dựa trên văn bản ghép từ hai chunk.
  - κ = 0.21 cho thấy câu trả lời trừu tượng làm *khó kiểm* hơn, kể cả với chuyên gia.
- **Verdict: ADOPT** (bài học thiết kế) **+ CONTEXT.**

**[S1.8] Leippold, M., Vaghefi, S. A., Stammbach, D., Muccione, V., Bingler, J., Ni, J., Colesanti Senni, C., Wekhof, T., Schimanski, T., Gostlow, G., Yu, T., Luterbacher, J., & Huggel, C. (2025).** *Automated fact-checking of climate claims with large language models* (Climinator). npj Climate Action 4, 17. https://doi.org/10.1038/s44168-025-00215-8 (preprint arXiv:2401.12566)

- **Phương pháp:** khung Mediator–Advocate. Các advocate dùng RAG trên IPCC, WMO, AbsCC và 1000S, thêm GPT-4o. Đánh giá trên 170 claim của Climate Feedback.
- **Kết quả** (đã loại nhãn NEI, 165 claim):

| Mức nhãn | Climinator | GPT-4o |
|---|---|---|
| Level 1 (12 lớp) | 34.5% (macro-F1 0.176) | 31.1% |
| Level 2 (5 lớp) | 72.7% | 58.5% |
| Level 4 (nhị phân) | 96.4% | 95.1% |

- **Lưu ý:** ở Level 4 có 16 claim "credible" và 149 "not credible", nên chỉ đoán lớp đa số đã đạt khoảng 90.3% [tự tính].
- **Với GreenScan:**
  - Nhãn càng mịn càng khó. 5 nhãn của GreenScan cần báo cáo macro-F1 và baseline lớp đa số, không chỉ accuracy.
  - Bài cũng cho thấy debate giữa nhiều LLM gần như không kích hoạt khi các nguồn đã đồng thuận.
- **Verdict: CONTEXT.**

**[S1.9] Schimanski, T., Ni, J., Spacey Martín, R., Ranger, N., & Leippold, M. (2024).** *ClimRetrieve: A Benchmarking Dataset for Information Retrieval from Corporate Climate Disclosures.* EMNLP 2024, tr. 17509–17524. https://aclanthology.org/2024.emnlp-main.969/

- **Dữ liệu:** 30 báo cáo bền vững, 16 câu hỏi khí hậu dạng có/không, 3 chuyên gia; 743 bộ question–source–answer gốc; 8,628 đoạn được gán độ liên quan (thang 1–3); 43,445 dòng ở mức báo cáo.
- **Kết quả** (F1 gộp trên top-k = 5/10/15, truy vấn chính là câu hỏi):
  - BM25 0.113; ColBERTv2 0.109; DRAGON+ 0.139; GTE-base 0.161; text-embedding-3-large 0.167.
  - Tốt nhất khoảng 0.179 khi viết lại truy vấn bằng định nghĩa "expert-informed".
- **Hạn chế do chính tác giả nêu:** *"we certainly know that the source is relevant once labeled, but we do not know whether the source is irrelevant if not labeled … our results represent a lower bound"*.
- **Với GreenScan:**
  - Đây là mẫu cách gán nhãn mức báo cáo cho retrieval.
  - Số tuyệt đối thấp và BM25 không thua xa embedding, đúng tinh thần "hybrid lexical trước, dense sau".
  - Recall đo được phải gọi là cận dưới (xem §6.4).
- **Verdict: ADOPT** (phương pháp đánh giá) **+ CONTEXT.**

### 1.4 Công trình 2024–2026 về greenwashing và xác minh claim ESG

**[S1.10] Ong, K., Mao, R., Varshney, D., Cambria, E., & Mengaldo, G. (2025).** *Towards Robust ESG Analysis Against Greenwashing Risks: Aspect-Action Analysis with Cross-Category Generalization* (A3CG). ACL 2025 (Long), tr. 14854–14879. https://aclanthology.org/2025.acl-long.723/

- **Dữ liệu:** 2,004 câu với 2,723 cặp aspect–action, lấy từ 1,679 báo cáo bền vững của doanh nghiệp niêm yết sàn Singapore (2017–2022). Licence CC BY 4.0 (theo paper).
- **Nhãn action:** implemented 1,459; planning 379; indeterminate 885.
- **Kết quả trên các aspect category chưa thấy khi train (F1):**
  - Mô hình có giám sát: GRACE 47.51; CONTRASTE 46.34.
  - LLM: Claude 3.5 Sonnet + few-shot 42.03; DeepSeek V3 41.08; GPT-4o + few-shot 40.41; Llama 3 70B 20.67.
  - Tác giả kết luận mô hình có giám sát nhìn chung hơn LLM khi gặp category mới.
- **Công trình tiếp theo:** Braun, Ong, Mao, Cambria, Mengaldo (2026), *Enhancing Language Models for Robust Greenwashing Detection*, arXiv:2601.21722 (contrastive learning + ordinal ranking).
- **Với GreenScan:**
  - Bộ nhãn implemented / planning / indeterminate ánh xạ thẳng vào risk rubric: claim "đang lên kế hoạch" hay "mơ hồ" không thể là SUPPORTED chỉ vì có bằng chứng về ý định.
  - Đánh giá trên category chưa thấy chính là tinh thần của company-held-out.
- **Verdict: TEST** (thêm thuộc tính action-type vào gold và rubric) **+ CONTEXT.**

**[S1.11] Kaoukis, G., Koufopoulos, I.-A., Psaroudaki, E., Pla Karidi, D., Pitoura, E., Papastefanatos, G., & Tsaparas, P. (2026).** *EmeraldMind: A Knowledge Graph–Augmented Framework for Greenwashing Detection.* Proceedings of the ACM Web Conference 2026, tr. 9645–9655. https://doi.org/10.1145/3774904.3792997 (arXiv:2512.11506)

- **Phương pháp:** knowledge graph ESG kết hợp RAG, kèm khả năng *abstain* khi không kiểm chứng được.
- **Dữ liệu:** EmeraldData gồm 620 claim *bán tổng hợp* (do LLM sinh): 225 greenwashing, 395 không.
- **Kết quả (few-shot):**

| Biến thể | Accuracy trên phần trả lời | Coverage | Overall |
|---|---|---|---|
| Baseline LLM | 94.21% | 19.52% | 18.39% |
| EM-RAG | 85.19% | 69.68% | 59.35% |
| EM-HYBRID | 83.80% | 74.68% | 62.58% |

  - Định nghĩa: *Overall Acc = Accuracy × Coverage*.
- **Với GreenScan:** báo cáo đồng thời accuracy, coverage và overall. Một hệ thống "chính xác 94%" nhưng chỉ trả lời 20% số claim là gây hiểu nhầm.
- **Verdict: ADOPT** (cách báo cáo coverage) **+ CONTEXT** (dữ liệu bán tổng hợp nên số tuyệt đối ít giá trị).

**[S1.12] Xu, C., Liu, J., Li, Z., & Lin, C. (2026).** *DeepGreen: Effective LLM-Driven Greenwashing Monitoring System Designed for Empirical Testing — Evidence from China.* Computational Economics (online 19/02/2026). https://doi.org/10.1007/s10614-026-11328-5 (arXiv:2504.07733)

- **Phương pháp và dữ liệu:** LLM hai tầng trên 9,369 báo cáo thường niên của doanh nghiệp A-share Trung Quốc (2021–2023).
- **Kết quả:**
  - RAG giảm hallucination so với chỉ kéo dài cửa sổ đầu vào.
  - Điểm greenwashing tương quan với các án phạt môi trường (kiểm định bằng IV, PSM, placebo).
- **Với GreenScan:** ví dụ gần nhất về thị trường mới nổi và báo cáo thường niên. Cũng gợi ý một hướng validation ngoài gold: đối chiếu với án phạt hoặc vi phạm môi trường đã công bố.
- **Verdict: CONTEXT.**

**[S1.13] Chuang, M., Chuang, G., Chuang, C., & Chuang, J. (2025).** *Judging It, Washing It: Scoring and Greenwashing Corporate Climate Disclosures using Large Language Models.* ClimateNLP 2025; arXiv:2502.15094. https://arxiv.org/abs/2502.15094

- **Kết quả:**
  - LLM-as-a-Judge phân biệt được nhóm công ty tốt.
  - Chính LLM cũng có thể "greenwash" câu trả lời khi được yêu cầu.
  - Chấm theo cặp (pairwise) bền vững hơn chấm điểm số trước nội dung đã bị greenwash.
- **Với GreenScan:** không dùng điểm số do LLM chấm làm ground truth.
- **Verdict: CONTEXT; AVOID** (LLM chấm điểm làm thước đo).

**[S1.14] Vinella, A., Capetz, M., Pattichis, R., Chance, C., Ghosh, R., & Chang, K.-W. (2023).** *Leveraging Language Models to Detect Greenwashing.* arXiv:2311.01469. https://arxiv.org/abs/2311.01469

- **Phương pháp và kết quả:** fine-tune ClimateBERT trên nhãn "greenwashing risk" do chính tác giả sinh ra; accuracy 86.34%, F1 0.67.
- **Verdict: AVOID.** Nhãn được sinh tự động, không phải greenwashing đã kiểm chứng. Đây đúng là kiểu lỗi Calamai et al. phê phán.

**[S1.15] Các nghiên cứu liên quan khác (CONTEXT)**

- **Schimanski, T., Ni, J., Kraus, M., Ash, E., & Leippold, M. (2024).** *Towards Faithful and Robust LLM Specialists for Evidence-Based Question-Answering.* ACL 2024 (Long), tr. 1913–1931. https://aclanthology.org/2024.acl-long.105/
  - LLM thường trích sai nguồn và diễn đạt sai nội dung nguồn.
  - Fine-tune trên dữ liệu tổng hợp có lọc chất lượng cải thiện cả in- lẫn out-of-distribution.
  - Chất lượng dữ liệu quan trọng hơn số lượng.
- **Ni, J., Schimanski, T., Lin, M., Sachan, M., Ash, E., & Leippold, M. (2025).** *DIRAS: Efficient LLM Annotation of Document Relevance in Retrieval Augmented Generation.* NAACL 2025 (Long). https://arxiv.org/abs/2406.14162
  - Fine-tune LLM 8B để gán nhãn relevance, đạt mức GPT-4.
  - Mục đích: giảm "annotation selection bias" khi đo recall. **TEST sau** (phương án khắc phục pooling bias).
- **He, C., Zhou, X., Wu, Y., Yu, X., Zhang, Y., Zhang, L., Wang, D., Lyu, S., Xu, H., Wang Xiaoqiao, Liu, W., & Miao, C. (2025).** *ESGenius.* EMNLP 2025, tr. 14612–14653. https://aclanthology.org/2025.emnlp-main.739/
  - 1,136 câu hỏi trắc nghiệm ESG, 50 LLM.
  - Zero-shot các mô hình tốt nhất chỉ đạt khoảng 55–70%; RAG cải thiện rõ.

### 1.5 Encoder chuyên ESG (ESG-BERT, FinBERT-ESG, ESGBERT)

**[S1.16] Schimanski, T., Reding, A., Reding, N., Bingler, J., Kraus, M., & Leippold, M. (2024).** *Bridging the gap in ESG measurement: Using NLP to quantify environmental, social, and governance communication.* Finance Research Letters 61, 104979. https://doi.org/10.1016/j.frl.2024.104979

- **Nội dung:** các mô hình E/S/G được pretrain trên 13.8 triệu văn bản, kèm ba bộ dữ liệu 2k mẫu. Ví dụ `ESGBERT/EnvironmentalBERT-environmental`, Apache-2.0.

**[S1.17] Huang, A. H., Wang, H., & Yang, Y. (2023, online 2022).** *FinBERT: A Large Language Model for Extracting Information from Financial Text.* Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12832

- **FinBERT-ESG** (`yiyanghkust/finbert-esg`): 2,000 câu được gán nhãn, 4 lớp E/S/G/None. Licence trên HF không ghi [UNVERIFIED].

**[S1.18] ESG-BERT** (`nbroad/ESG-BERT`, Mukherjee & Pothireddi / Parabole.ai)

- Không có paper. F1 0.90 so với BERT-base 0.79 [self-reported]. Licence trên card ghi "More information needed".

**Verdict chung cho §1.5: AVOID** với pipeline tiếng Việt. Lý do:

- chỉ hỗ trợ tiếng Anh;
- làm phân loại *chủ đề*, không phải *xác minh claim*;
- ESG-BERT thiếu bằng chứng peer-review và licence rõ ràng.

Chỉ dùng làm CONTEXT.

---

## 2. Phương pháp xác minh claim–evidence liên quan

### 2.1 Bộ nhãn, lớp NEI và quy tắc gộp nhãn

**[S2.1] Thorne, J., Vlachos, A., Christodoulopoulos, C., & Mittal, A. (2018).** *FEVER: a Large-scale Dataset for Fact Extraction and VERification.* NAACL 2018, tr. 809–819. https://aclanthology.org/N18-1074/

- **Dữ liệu:** 185,445 claim được sinh từ câu Wikipedia; nhãn Supported / Refuted / NotEnoughInfo; Fleiss κ = 0.6841. Licence CC BY-SA 3.0 cộng điều khoản Wikipedia (theo HF).
- **Kết quả:** pipeline tốt nhất đạt 31.87% khi bắt buộc đúng cả bằng chứng, 50.91% nếu bỏ qua bằng chứng.
- **Với GreenScan:**
  - Ngữ nghĩa NEI là "không đủ bằng chứng để kết luận", khác với "sai".
  - Metric nên cho điểm verdict *chỉ khi* bằng chứng đúng (evidence-conditioned scoring).
- **Verdict: ADOPT.**

**[S2.2] Wadden, D., Lin, S., Lo, K., Wang, L. L., van Zuylen, M., Cohan, A., & Hajishirzi, H. (2020).** *Fact or Fiction: Verifying Scientific Claims* (SciFact). EMNLP 2020, tr. 7534–7550. https://aclanthology.org/2020.emnlp-main.609/

- **Dữ liệu:** 1.4K claim do chuyên gia viết, ghép với abstract có nhãn và *rationale* (câu làm căn cứ). Nhãn SUPPORTS / REFUTES / NOINFO.
- **Kết quả:** domain adaptation đơn giản cải thiện rõ so với mô hình train trên Wikipedia hoặc tin chính trị.
- **Licence:** claim CC BY 4.0; abstract ODC-By 1.0; code Apache-2.0.
- **Với GreenScan:** gold nên lưu *câu rationale*, không chỉ trang.
- **Verdict: ADOPT** (định dạng gold có rationale) **+ CONTEXT.**

**[S2.3] Schlichtkrull, M., Guo, Z., & Vlachos, A. (2023).** *AVeriTeC: A Dataset for Real-world Claim Verification with Evidence from the Web.* NeurIPS 2023 Datasets & Benchmarks. https://arxiv.org/abs/2305.13117

- **Dữ liệu:**
  - 4,568 claim thật từ 50 tổ chức fact-check. Licence CC BY-NC 4.0.
  - 4 nhãn: Supported, Refuted, Not Enough Evidence, **Conflicting Evidence/Cherry-picking**.
  - Phân bố nhãn trên test: S 25.5% / R 62.0% / C 6.3% / N 6.2%.
- **Thiết kế gán nhãn và đo lường:**
  - Bước "evidence sufficiency check": một người gán nhãn *khác* chỉ nhìn các cặp hỏi–đáp bằng chứng rồi đưa verdict.
  - Agreement: free-marginal κ (Randolph) = 0.619; Fleiss κ = 0.503.
  - Baseline gộp nhãn *tất định*: có cả bằng chứng ủng hộ lẫn bác bỏ thì *conflicting/cherry-picking*; chỉ có ủng hộ thì supported; chỉ có bác bỏ thì refuted; còn lại là NEE.
  - Với gold evidence, BERT-large đạt macro-F1 0.49.
- **Ví dụ minh hoạ trong paper:** claim "Mỹ đã giảm phát thải KNK những năm qua" bị gán *Conflicting Evidence/Cherry-picking* vì phát thải có giảm rồi lại tăng. Đây là mẫu greenwashing kinh điển: chọn năm gốc có lợi.
- **Shared task 2024** (Schlichtkrull et al., FEVER 2024, tr. 1–26, https://aclanthology.org/2024.fever-1.1/): 21 đội nộp, 18 đội vượt baseline. Đội thắng (InFact; Rothermel, Braun, Rohrbach & Rohrbach, https://aclanthology.org/2024.fever-1.12/) dùng GPT-4o với pipeline 6 bước, đạt AVeriTeC score 63%.
- **Shared task 2025** (Akhtar et al., FEVER 2025, tr. 201–223, https://aclanthology.org/2025.fever-1.15/):
  - Điều kiện: chỉ dùng mô hình open-weights, một GPU 23GB, tối đa 1 phút mỗi claim.
  - Đội thắng (CTU AIC) đạt 33.17%.
  - Không so sánh trực tiếp với 63% năm 2024 vì điều kiện khác hẳn.
- **Với GreenScan:**
  - Logic CONTRADICTED / PARTIALLY_SUPPORTED và quy tắc gộp tất định có tiền lệ học thuật trực tiếp.
  - Kết quả 2025 cho thấy giới hạn phần cứng làm hiệu năng giảm mạnh, củng cố việc giữ rule tất định làm lõi.
- **Verdict: ADOPT.**

**[S2.4] Diggelmann, T., Boyd-Graber, J., Bulian, J., Ciaramita, M., & Leippold, M. (2020).** *CLIMATE-FEVER: A Dataset for Verification of Real-World Climate Claims.* Tackling Climate Change with ML Workshop @ NeurIPS 2020; arXiv:2012.00614. https://arxiv.org/abs/2012.00614

- **Dữ liệu:**
  - 1,535 claim thật; 7,675 cặp claim–evidence (top-5 câu Wikipedia cho mỗi claim).
  - Phân bố nhãn claim: SUPPORTS 655 (42.67%), REFUTES 253 (16.5%), DISPUTED 153 (9.97%), NOT_ENOUGH_INFO 474 (30.88%).
  - Agreement khi gán nhãn evidence: Krippendorff α = 0.334.
  - Licence [UNVERIFIED]; card HF ghi "unknown".
- **Quy tắc gộp nhãn:** mặc định NEI, trừ khi có bằng chứng ủng hộ hoặc bác bỏ; có cả hai thì DISPUTED. Tác giả nhận xét gộp theo đa số kiểu FEVER là *"too naïve"*.
- **Kết quả:** mô hình train trên FEVER chỉ đạt label accuracy 38.78% trên Climate-FEVER, so với 77.69% trên FEVER dev. Đây là domain shift rất lớn.
- **Chi tiết đáng chú ý:** người gán nhãn coi "mực nước biển dâng 6 m" được *ủng hộ* bởi bằng chứng ghi "x + ε m". Con người có dung sai số ngầm.
- **Với GreenScan:**
  - Quy tắc gộp của Climate-FEVER và AVeriTeC trùng với cách gộp của GreenScan.
  - Cần viết *rõ* chính sách dung sai số (tuyệt đối/tương đối, làm tròn) vào hướng dẫn gán nhãn, để người gán nhãn và comparator dùng cùng một chuẩn.
  - Không dùng NLI/fact-checker "off-the-shelf" mà chưa đo trên miền của mình.
- **Verdict: ADOPT** (quy tắc gộp, chính sách dung sai) **+ CONTEXT.**

### 2.2 Phân rã claim (claim decomposition)

**[S2.5] Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023).** *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation.* EMNLP 2023, tr. 12076–12100. https://aclanthology.org/2023.emnlp-main.741/

- **Phương pháp:** tách văn bản thành *atomic facts*, rồi tính tỷ lệ fact được nguồn tin cậy ủng hộ.
- **Kết quả:** ChatGPT chỉ đạt 58% trên tiểu sử. Bộ ước lượng tự động có sai số dưới 2%.

**Phản biện và bổ sung:**

- **Kamoi, R., Goyal, T., Rodriguez, J. D., & Durrett, G. (2023).** *WiCE: Real-World Entailment for Claims in Wikipedia.* EMNLP 2023, tr. 7561–7583. https://aclanthology.org/2023.emnlp-main.470/
  - Gán nhãn entailment ở mức tiểu câu.
  - Tách claim bằng GPT-3.5 giúp mô hình entailment.
  - Claim thật khó cả ở khâu retrieval lẫn verification.
- **Wanner, M., Ebner, S., Jiang, Z., Dredze, M., & Van Durme, B. (2024).** *A Closer Look at Claim Decomposition.* *SEM 2024, tr. 153–175. https://aclanthology.org/2024.starsem-1.13/
  - FActScore *nhạy với phương pháp phân rã*: lỗi của bước phân rã bị tính thành lỗi của mô hình được đánh giá.
- **Hu, Q., Long, Q., & Wang, W. (2025).** *Decomposition Dilemmas: Does Claim Decomposition Boost or Burden Fact-Checking Performance?* NAACL 2025. https://arxiv.org/abs/2411.02400
  - Có đánh đổi giữa lợi ích accuracy và *nhiễu do phân rã sinh ra*; tác giả phân loại các lỗi phân rã.

**Với GreenScan:**

- Chỉ phân rã *tất định* các claim ghép rõ ràng, ví dụ "giảm 15% phát thải Scope 1 và 20% nước so với 2020" tách thành 2 claim số.
- Không dùng LLM tự do phân rã trước khi có gold, vì lỗi phân rã sẽ lẫn vào kết quả đo.

**Verdict: TEST** (phân rã bằng LLM) **/ ADOPT** (phân rã tất định cho claim số ghép).

### 2.3 Claim số và độ giòn của LLM với con số

**[S2.6] Venktesh V, Anand, A., Anand, A., & Setty, V. (2024).** *QuanTemp: A real-world open-domain benchmark for fact-checking numerical claims.* SIGIR 2024. https://arxiv.org/abs/2403.17169

- **Dữ liệu:** 15,514 claim thật có yếu tố số hoặc thời gian; 18.79% True / 57.93% False / 23.27% Conflicting; corpus 423,320 snippet (đã loại các trang fact-check). Licence CC BY-NC 4.0 (GitHub).
- **Taxonomy:** statistical, temporal, comparison, interval.
- **Kết quả:** tốt nhất macro-F1 58.32, đạt bởi FinQA-RoBERTa-Large kết hợp ClaimDecomp.
- **Với GreenScan:** dùng taxonomy này để *phân tầng gold* (claim thống kê, so sánh theo thời gian, khoảng) và báo cáo kết quả theo từng loại.
- **Verdict: ADOPT** (taxonomy) **+ CONTEXT.**

**[S2.7] Aarnes, P. R., & Setty, V. (2025).** *NumPert: Numerical Perturbations to Probe Language Models for Veracity Prediction.* IJCNLP-AACL 2025 SRW; arXiv:2511.09971. https://arxiv.org/abs/2511.09971

- **Kết quả:**
  - Dưới các nhiễu số có kiểm soát (gồm label-flipping), *"even leading proprietary systems experience accuracy drops of up to 62%"*.
  - Không mô hình nào bền vững ở mọi điều kiện.
  - Context càng dài thì accuracy nhìn chung càng giảm.

**[S2.8] Aarnes, P. R., & Setty, V. (2026).** *Towards Robust Numerical Claim Verification.* Accepted to AACL-IJCNLP 2026 Findings; arXiv:2610.00689 (30/09/2026). https://arxiv.org/abs/2610.00689

- **Kết quả:**
  - Độ giòn với số vẫn còn ở mô hình frontier: trên label-flipping perturbations, GPT-5.4 Pro đạt 74.0%, Gemini 2.5 Flash 73.9%.
  - Qwen3 nhỏ (0.6B–8B) được fine-tune đối kháng theo kiểu PEFT đạt 98.7%, có tổng quát hoá sang loại nhiễu chưa thấy và sang tiếng Tây Ban Nha.
- **Với GreenScan:**
  - Đây là bằng chứng mới nhất (tuần trước) ủng hộ việc **không** để LLM quyết định trên con số.
  - Bộ "green traps" hiện có nên được mở rộng bằng *các cặp đảo nhãn chỉ khác một con số* theo kiểu NumPert, làm regression test.
- **Verdict: ADOPT** (lập luận thiết kế + kiểu test) **; TEST** (mô hình nhỏ fine-tune đối kháng, chỉ sau freeze).

**[S2.9] Schuster, T., Fisch, A., & Barzilay, R. (2021).** *Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence.* NAACL 2021, tr. 624–643. https://aclanthology.org/2021.naacl-main.52/

- **Dữ liệu:** hơn 400K cặp claim–evidence tương phản từ hơn 100K lần sửa Wikipedia; hai bằng chứng gần như giống hệt nhưng một cái ủng hộ, một cái không. Licence CC BY-SA 3.0.
- **Kết quả:** train trên dữ liệu này tăng 10% accuracy trên adversarial fact verification và 6% trên adversarial NLI.
- **Với GreenScan:** nguyên lý "bằng chứng tương phản tối thiểu" là cách xây test tốt cho stance rules.
- **Verdict: TEST** (thiết kế test) **+ CONTEXT.**

### 2.4 Bảng và suy luận số trên tài liệu tài chính

**[S2.10] Chen, W., Wang, H., Chen, J., Zhang, Y., Wang, H., Li, S., Zhou, X., & Wang, W. Y. (2020).** *TabFact: A Large-scale Dataset for Table-based Fact Verification.* ICLR 2020. https://arxiv.org/abs/1909.02164

- **Dữ liệu:** 16k bảng Wikipedia, 118k phát biểu ENTAILED/REFUTED.
- **Kết quả:** Table-BERT 65.1% (complex 58.2%); LPA 65.0%; con người 92.1% (small test).
- **Verdict: CONTEXT.**

**[S2.11] Aly, R., Guo, Z., Schlichtkrull, M., Thorne, J., Vlachos, A., Christodoulopoulos, C., Cocarascu, O., & Mittal, A. (2021).** *FEVEROUS: Fact Extraction and VERification Over Unstructured and Structured information.* NeurIPS 2021 D&B. https://arxiv.org/abs/2106.05707

- **Dữ liệu:** 87,026 claim; bằng chứng là câu và/hoặc ô bảng; có lớp NEI.
- **Kết quả:** baseline chỉ đúng cả bằng chứng lẫn verdict ở 18% số claim.
- **Verdict: CONTEXT.**

**[S2.12] Chen, Z., Chen, W., Smiley, C., Shah, S., Borova, I., Langdon, D., Moussa, R., Beane, M., Huang, T.-H., Routledge, B., & Wang, W. Y. (2021).** *FinQA: A Dataset of Numerical Reasoning over Financial Data.* EMNLP 2021, tr. 3697–3711. https://aclanthology.org/2021.emnlp-main.300/

- **Dữ liệu:** 8,281 cặp hỏi–đáp từ 2,789 trang báo cáo của doanh nghiệp S&P 500.
- **Kết quả:**

| Hệ thống | Execution accuracy |
|---|---|
| FinQANet (RoBERTa-large) | 61.24% |
| Chuyên gia tài chính | 91.16% |
| Crowd không chuyên | 50.68% |

  - Theo số bước suy luận của FinQANet: 1 bước 67.61%; 2 bước 59.08%; từ 3 bước trở lên 22.78%.
- **Verdict: CONTEXT** (bằng chứng suy luận nhiều bước sụp đổ).

**[S2.13] Zhu, F., Lei, W., Huang, Y., Wang, C., Zhang, S., Lv, J., Feng, F., & Chua, T.-S. (2021).** *TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content in Finance.* ACL-IJCNLP 2021, tr. 3277–3287. https://aclanthology.org/2021.acl-long.254/

- **Kết quả:** TAGOP đạt 58.0% F1, còn chuyên gia đạt 90.8%.
- **Verdict: CONTEXT.**

**[S2.14] Zhao, Y., Long, Y., Jiang, Y., Wang, C., Chen, W., Liu, H., Zhang, Y., Tang, X., Zhao, C., & Cohan, A. (2024).** *FinDVer: Explainable Claim Verification over Long and Hybrid-Content Financial Documents.* EMNLP 2024, tr. 14739–14752. https://aclanthology.org/2024.emnlp-main.818/

- **Dữ liệu:**
  - 2,100 claim entailed/refuted (600 testmini + 1,500 test) trên 523 tài liệu 10-K/10-Q.
  - Tài liệu dài khoảng 41K từ và khoảng 79 bảng mỗi tài liệu; khoảng 66–71% claim cần bằng chứng từ bảng.
  - Inter-annotator agreement (percent agreement) 90.3%. Licence MIT (GitHub).
- **Kết quả:** LLM tốt nhất (Claude-3.5-Sonnet, theo PDF) đạt 77.2%, so với chuyên gia 93.3%.
- **Lưu ý:** trang ACL Anthology ghi "GPT-4o" là mô hình tốt nhất; PDF bản cuối ghi Claude-3.5-Sonnet.
- **Với GreenScan:** đây là benchmark gần nhất với bài toán (xác minh claim trên báo cáo dài có bảng). Tuy vậy không có lớp NEI và chỉ có tiếng Anh.
- **Verdict: CONTEXT** (con số đối chiếu cho Ban giám khảo).

**[S2.15] Islam, P., Kannappan, A., Kiela, D., Qian, R., Scherrer, N., & Vidgen, B. (2023).** *FinanceBench: A New Benchmark for Financial Question Answering.* arXiv:2311.11944. https://arxiv.org/abs/2311.11944

- **Kết quả:** 10,231 câu hỏi; trên mẫu 150 câu, *"GPT-4-Turbo used with a retrieval system incorrectly answered or refused to answer 81% of questions"*.
- **Verdict: CONTEXT.**

**[S2.16] Zhao, Y., Long, Y., Liu, H., Kamoi, R., Nan, L., Chen, L., Liu, Y., Tang, X., Zhang, R., & Cohan, A. (2024).** *DocMath-Eval: Evaluating Math Reasoning Capabilities of LLMs in Understanding Long and Specialized Documents.* ACL 2024, tr. 16103–16120. https://aclanthology.org/2024.acl-long.852/

- **Kết quả:** đánh giá 48 LLM; ngay cả GPT-4o vẫn *"significantly lags behind human experts"* khi suy luận số trên ngữ cảnh dài.
- **Verdict: CONTEXT.**

### 2.5 Tài liệu dài và các kiểu thất bại của RAG

**[S2.17] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024).** *Lost in the Middle: How Language Models Use Long Contexts.* TACL 12, tr. 157–173. https://aclanthology.org/2024.tacl-1.9/

- **Kết quả:**
  - Hiệu năng có hình chữ U: cao khi thông tin liên quan nằm ở đầu hoặc cuối ngữ cảnh, giảm mạnh khi nằm giữa (thử với 10/20/30 tài liệu).
  - Khi thông tin nằm giữa, GPT-3.5-Turbo còn *thấp hơn* cả chế độ không đưa tài liệu nào (closed-book, 56.1%).
- **Với GreenScan:** prompt stance cho GLM chỉ nên chứa *ít* đoạn (cặp claim–evidence), evidence đặt sát claim, không nhồi cả trang.
- **Verdict: ADOPT.**

**[S2.5b] Zhao, S., Shao, Y., Huang, Y., Song, J., Wang, Z., Wan, C., & Ma, L. (2024; v3 2026).** *Understanding the Fundamental Design Decisions of Retrieval-Augmented Generation Systems* (v1: *Towards Understanding Retrieval Accuracy and Prompt Quality in RAG Systems*). ACM TOSEM 2026; arXiv:2411.19463. https://arxiv.org/abs/2411.19463

- **Kết luận ở v3:**
  - Việc triển khai RAG cần chọn lọc: có các failure mode ảnh hưởng tới 12.6% mẫu *ngay cả khi tài liệu hoàn hảo*.
  - Với QA, lấy khoảng 5–10 tài liệu là tối ưu.
  - Prompting nâng cao cải thiện rất ít cho QA.
- **Với GreenScan:** củng cố các quyết định đã ghi trong README: tách retrieval khỏi verification, cho phép cấu hình top-k, bắt đầu từ baseline tất định. Cần cập nhật tên và venue khi trích dẫn.
- **Verdict: ADOPT.**

**[S2.18] Barnett, S., Kurniawan, S., Thudumu, S., Brannelly, Z., & Abdelrazek, M. (2024).** *Seven Failure Points When Engineering a Retrieval Augmented Generation System.* arXiv:2401.05856. https://arxiv.org/abs/2401.05856

- **Kết luận:** báo cáo kinh nghiệm từ 3 case study; đưa ra 7 điểm thất bại. Hai bài học chính: validation chỉ khả thi khi vận hành thật, và độ bền của hệ thống *tiến hoá dần* chứ không được thiết kế xong từ đầu.
- **Verdict: CONTEXT.**

**[S2.19] Joren, H., Zhang, J., Ferng, C.-S., Juan, D.-C., Taly, A., & Rashtchian, C. (2025).** *Sufficient Context: A New Lens on Retrieval Augmented Generation Systems.* ICLR 2025; arXiv:2411.06037. https://arxiv.org/abs/2411.06037

- **Kết quả:**
  - Các mô hình lớn (Gemini 1.5 Pro, GPT-4o, Claude 3.5) trả lời tốt khi ngữ cảnh đủ, nhưng *"often output incorrect answers instead of abstaining when the context is not"*.
  - Mô hình nhỏ hay hallucinate hoặc abstain ngay cả khi ngữ cảnh đủ.
  - Selective generation dựa trên tín hiệu "đủ ngữ cảnh" tăng tỷ lệ trả lời đúng (trong số lần chịu trả lời) thêm 2–10%.
- **Với GreenScan:** tách câu hỏi "bằng chứng có *đủ* không?" (rule: đúng metric, scope, kỳ, đơn vị) khỏi câu hỏi "bằng chứng *ủng hộ* hay *bác bỏ*?". Nhãn INSUFFICIENT_EVIDENCE nên do rule quyết định, không do LLM.
- **Verdict: ADOPT** (nguyên lý) **; TEST** (autorater "sufficiency").

---

## 3. Các kiểu lỗi đã biết của LLM và thiết kế human-in-the-loop

### 3.1 Bằng chứng "ủng hộ" bị bịa (hallucinated support / attribution)

**[S3.1] Liu, N. F., Zhang, T., & Liang, P. (2023).** *Evaluating Verifiability in Generative Search Engines.* Findings of EMNLP 2023. https://arxiv.org/abs/2304.09848

- **Kết quả:** với 4 search engine sinh văn bản, *"a mere 51.5% of generated sentences are fully supported by citations and only 74.5% of citations support their associated sentence"*.
- **Verdict: CONTEXT.**

**[S3.2] Gao, T., Yen, H., Yu, J., & Chen, D. (2023).** *Enabling Large Language Models to Generate Text with Citations* (ALCE). EMNLP 2023, tr. 6465–6488. https://aclanthology.org/2023.emnlp-main.398/

- **Kết quả:** trên ELI5, *"even the best models lack complete citation support 50% of the time"*.
- **Verdict: CONTEXT.**

**[S3.3] Niu, C., Wu, Y., Zhu, J., Xu, S., Shum, K., Zhong, R., Song, J., & Zhang, T. (2024).** *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models.* ACL 2024, tr. 10862–10878. https://aclanthology.org/2024.acl-long.585/

- **Dữ liệu và kết quả:** khoảng 18,000 câu trả lời RAG được gán nhãn hallucination tới mức từ. Fine-tune một LLM tương đối nhỏ cho kết quả phát hiện hallucination cạnh tranh với GPT-4 dùng prompt.
- **Verdict: CONTEXT; TEST** (chỉ khi có dữ liệu tiếng Việt).

**[S3.4] Tang, L., Laban, P., & Durrett, G. (2024).** *MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents.* EMNLP 2024. https://arxiv.org/abs/2404.10774. Leaderboard LLM-AggreFact: https://llm-aggrefact.github.io/

- **Kết quả:**
  - Fact-checker nhỏ train trên dữ liệu tổng hợp do GPT-4 tạo đạt mức GPT-4 với chi phí thấp hơn 400 lần.
  - Leaderboard (truy cập 05/10/2026): MiniCheck-Flan-T5-L (0.8B) 75.0; gpt-4o-2024-05-13 75.9; Claude-3.5 Sonnet 77.2; Bespoke-MiniCheck-7B 77.4.
- **Licence:** MiniCheck-Flan-T5-Large dùng MIT, *chỉ tiếng Anh*.
- **So sánh liên quan:** HHEM-2.1-Open (Vectara; FLAN-T5-base, khoảng 0.1B, Apache-2.0; chỉ tiếng Anh) đạt balanced accuracy 76.55% trên AggreFact-SOTA và 74.28% trên RAGTruth-QA; chạy khoảng 1.5 giây cho đầu vào 2k token trên CPU x86, dưới 600MB RAM [self-reported]. https://huggingface.co/vectara/hallucination_evaluation_model
- **Verdict: TEST** (chỉ theo kiểu translate-test hoặc trên claim song ngữ; không dùng làm nhãn quyết định).

### 3.2 Lỗi số

Bằng chứng ở [S2.6]–[S2.8] và [S2.12]–[S2.16]. Có thể tóm tắt cho Ban giám khảo như sau:

- Dưới nhiễu số, accuracy của LLM giảm tới 62% (NumPert).
- Mô hình frontier chỉ khoảng 74% trên label-flipping (2026).
- Suy luận số từ 3 bước trở lên chỉ khoảng 23% (FinQA).
- Claim trên báo cáo tài chính dài: 77.2% so với chuyên gia 93.3% (FinDVer).
- Hỏi–đáp tài chính có retrieval: 81% sai hoặc từ chối (FinanceBench).

**Verdict: ADOPT** (bộ so sánh số tất định là lõi; LLM không quyết định trên con số).

### 3.3 Tự tin quá mức và hiệu chỉnh (calibration)

**[S3.5] Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024).** *Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs.* ICLR 2024. https://arxiv.org/abs/2306.13063

- **Kết quả:**
  - Khi tự nói ra mức tự tin, LLM *"tend to be overconfident"*.
  - Chênh lệch giữa phương pháp white-box và black-box hẹp (AUROC 0.522 so với 0.605).
  - Mọi phương pháp đều kém ở task cần kiến thức chuyên môn.
- **Với GreenScan:** không dùng "confidence" do GLM tự khai làm ngưỡng quyết định.
- **Verdict: ADOPT** (cấm dùng verbalized confidence làm ngưỡng).

**[S3.6] Kadavath, S. et al. (36 tác giả) (2022).** *Language Models (Mostly) Know What They Know.* arXiv:2207.05221. https://arxiv.org/abs/2207.05221

- **Kết quả:** mô hình lớn có calibration khá tốt *khi câu hỏi được định dạng phù hợp* (trắc nghiệm, đúng/sai, đại lượng P(True)).
- **Verdict: CONTEXT.**

**[S3.7] Kamath, A., Jia, R., & Liang, P. (2020).** *Selective Question Answering under Domain Shift.* ACL 2020, tr. 5684–5696. https://aclanthology.org/2020.acl-main.503/

- **Kết quả:**
  - Abstain dựa trên softmax kém vì mô hình *overconfident ngoài miền*.
  - Một calibrator riêng trả lời được 56% câu hỏi ở mức accuracy 80%, so với 48% nếu chỉ dùng xác suất của mô hình.
- **Với GreenScan:** báo cáo ESG tiếng Việt là ngoài miền với hầu hết mô hình. Nếu cần ngưỡng abstain, nên học từ đặc trưng có thể quan sát được (độ phủ rule, số bằng chứng, sự bất đồng giữa các retriever), không từ xác suất của LLM.
- **Verdict: TEST.**

### 3.4 Position bias và độ tin cậy của LLM-as-a-judge

**[S3.8] Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Kong, L., Liu, Q., Liu, T., & Sui, Z. (2024).** *Large Language Models are not Fair Evaluators.* ACL 2024, tr. 9440–9450. https://aclanthology.org/2024.acl-long.511/

- **Kết quả:** chỉ cần đảo thứ tự hai câu trả lời là kết quả xếp hạng thay đổi. Với ChatGPT làm giám khảo, Vicuna-13B "thắng" ChatGPT ở 66/80 truy vấn.
- **Biện pháp đề xuất:** multiple evidence calibration, balanced position calibration, human-in-the-loop calibration.

**[S3.9] Zheng, L. et al. (2023).** *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS 2023 D&B. https://arxiv.org/abs/2306.05685

- **Kết quả:**
  - GPT-4 đồng ý với con người trên 80% *cho bài toán sở thích hội thoại*.
  - Đồng thời ghi nhận position, verbosity và self-enhancement bias.

**[S3.10] Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2025).** *Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge.* AACL-IJCNLP 2025. https://arxiv.org/abs/2406.07791

- **Kết quả:** 15 LLM giám khảo, hơn 150,000 lượt đánh giá. Position bias *"is not due to random chance"*, thay đổi theo giám khảo và task, và bị ảnh hưởng mạnh bởi khoảng cách chất lượng giữa các phương án.

**[S3.11] Bavaresco, A. et al. (2025).** *LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks.* ACL 2025. https://arxiv.org/abs/2406.18403

- **Kết quả:** JUDGE-BENCH với 20 bộ dữ liệu và 11 LLM cho thấy *"substantial variance across models and datasets"*. Tác giả khuyến nghị kiểm định LLM với nhãn người trước khi dùng làm giám khảo.

**[S3.12] Panickssery, A., Bowman, S. R., & Feng, S. (2024).** *LLM Evaluators Recognize and Favor Their Own Generations.* arXiv:2404.13076. https://arxiv.org/abs/2404.13076

- **Kết quả:** self-preference bias có quan hệ tuyến tính với khả năng tự nhận ra văn bản của chính mình.

**Với GreenScan (cho cả §3.4):**

- Không dùng GLM chấm hiệu năng của GreenScan; thước đo là gold do người gán.
- Nếu GLM được dùng cho stance *theo cặp*, phải chạy cả hai thứ tự và chỉ nhận kết quả khi hai lần nhất quán.
- Không dùng cùng một LLM vừa sinh vừa chấm.

**Verdict: ADOPT.**

### 3.5 Abstention và selective prediction

**[S3.13] Wen, B., Yao, J., Feng, S., Xu, C., Tsvetkov, Y., Howe, B., & Wang, L. L. (2024/2025).** *Know Your Limits: A Survey of Abstention in Large Language Models.* TACL. https://arxiv.org/abs/2407.18418

- **Nội dung:** khung phân tích abstention theo 3 góc độ: truy vấn, mô hình, giá trị con người.
- **Verdict: CONTEXT.**

**[S3.14] Geifman, Y., & El-Yaniv, R. (2017).** *Selective Classification for Deep Neural Networks.* NeurIPS 2017; arXiv:1705.08500. https://arxiv.org/abs/1705.08500

- **Nội dung:** khung risk–coverage chuẩn. Ví dụ trong paper: top-5 error 2% trên ImageNet với xác suất 99.9%, ở coverage gần 60%.
- **Với GreenScan:** vẽ đường risk–coverage của hàng đợi ưu tiên (sai bao nhiêu nếu chỉ tự động hoá X% claim).
- **Verdict: ADOPT.**

**[S3.15] Mohri, C., & Hashimoto, T. (2024).** *Language Models with Conformal Factuality Guarantees.* ICML 2024, PMLR 235, tr. 36029–36047. https://proceedings.mlr.press/v235/mohri24a.html

- **Kết quả:** conformal prediction cho đầu ra LM đạt bảo đảm đúng 80–90% với rất ít mẫu có nhãn, bằng cách làm đầu ra *bớt cụ thể đi*.
- **Verdict: CONTEXT** (TEST sau Chung kết, cần gold lớn hơn).

Xem thêm [S1.11] EmeraldMind (báo cáo coverage) và [S2.19] Sufficient Context.

### 3.6 Human-in-the-loop cho kiểm toán và fact-checking

**[S3.16] Warren, G., Shklovski, I., & Augenstein, I. (2025).** *Show Me the Work: Fact-Checkers' Requirements for Explainable Automated Fact-Checking.* CHI 2025, tr. 1–21. https://arxiv.org/abs/2502.09083

- **Phương pháp và kết quả:** phỏng vấn bán cấu trúc các fact-checker chuyên nghiệp. Họ cần lời giải thích *"trace the model's reasoning path, reference specific evidence, and highlight uncertainty and information gaps"*.
- **Với GreenScan:** đây là đặc tả trực tiếp cho màn hình review queue: hiện đường suy luận (rule nào bắn), trích nguyên văn bằng chứng kèm trang, và nói rõ còn thiếu gì.
- **Verdict: ADOPT.**

**[S3.17] Warren, G., Sun, J., Shklovski, I., & Augenstein, I. (2026).** *Show me the evidence: Evaluating the role of evidence and natural language explanations in AI-supported fact-checking.* arXiv:2601.11387. https://arxiv.org/abs/2601.11387

- **Kết quả:** người dùng luôn dựa vào *bằng chứng* để kiểm tra lời khuyên của AI. Khi có giải thích bằng ngôn ngữ tự nhiên, họ xem bằng chứng ít hơn, trừ khi lời giải thích có vẻ thiếu hoặc sai.
- **Verdict: ADOPT** (ưu tiên hiển thị bằng chứng hơn văn bản giải thích do LLM viết).

**[S3.18] Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. S. (2021).** *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance.* CHI 2021. https://arxiv.org/abs/2006.14779

- **Kết quả:** AI có giúp đội người–AI, nhưng giải thích *không* làm tăng thêm. Giải thích làm người dùng *"accept the AI's recommendation, regardless of its correctness"*.
- **Verdict: CONTEXT** (và AVOID tuyên bố "giải thích giúp chính xác hơn").

**[S3.19] Vasconcelos, H., Jörke, M., Grunde-McLaughlin, M., Gerstenberg, T., Bernstein, M., & Krishna, R. (2023).** *Explanations Can Reduce Overreliance on AI Systems During Decision-Making.* CSCW 2023. https://arxiv.org/abs/2212.06823

- **Kết quả:** 5 nghiên cứu, N = 731. Giải thích chỉ giảm over-reliance khi nó *giảm chi phí kiểm chứng* cho người dùng.
- **Verdict: ADOPT** (thiết kế UI giúp kiểm nhanh: highlight con số, so khớp metric/kỳ ngay cạnh nhau).

**[S3.20] Commerford, B. P., Dennis, S. A., Joe, J. R., & Ulla, J. W. (2022).** *Man Versus Machine: Complex Estimates and Auditor Reliance on Artificial Intelligence.* Journal of Accounting Research 60(1), 171–201. https://doi.org/10.1111/1475-679X.12407

- **Kết quả (thí nghiệm với kiểm toán viên):** khi bằng chứng mâu thuẫn đến từ *hệ thống AI* thay vì *chuyên gia con người*, kiểm toán viên đề xuất điều chỉnh nhỏ hơn. Đây là hiện tượng "algorithm aversion".
- **Với GreenScan:** người dùng là kiểm toán viên có thể *xem nhẹ* cảnh báo của AI. Cách trình bày nên để bằng chứng gốc tự nói, không để "AI phán".
- **Verdict: CONTEXT** (rất hữu ích cho Q&A).

**[S3.21] Guo, Z., Schlichtkrull, M., & Vlachos, A. (2022).** *A Survey on Automated Fact-Checking.* TACL 10, tr. 178–206. https://aclanthology.org/2022.tacl-1.11/

- **Nội dung:** khung chuẩn của pipeline claim detection → evidence retrieval → verdict prediction → justification.
- **Verdict: CONTEXT.**

---

## 4. Tài nguyên NLP tiếng Việt dùng được ngay

### 4.1 Embedding và benchmark truy hồi tiếng Việt

**[S4.1] Pham, L., Luu, T., Vo, T., Nguyen, M., & Hoang, V. (2025).** *VN-MTEB: Vietnamese Massive Text Embedding Benchmark.* arXiv:2507.21500. https://arxiv.org/abs/2507.21500

**Dữ liệu:**

- 41 bộ dữ liệu, 6 task (15 retrieval, 13 classification, 3 pair-classification, 5 clustering, 3 rerank, 3 STS).
- Được **dịch máy** từ MTEB bằng Aya-23-35B rồi lọc bằng embedding và LLM-as-judge.
- Có **ClimateFEVER-VN** (giữ lại 3,401/4,681 mẫu), dùng được làm phép thử nhanh cho truy hồi miền khí hậu bằng tiếng Việt.
- Licence của bộ dịch theo licence MTEB gốc từng bộ [UNVERIFIED cho riêng ClimateFEVER-VN].
- Tác giả tự nêu hạn chế: không có tài liệu rất dài.

**Kết quả (Bảng 3, cột Retrieval và trung bình 41 bộ):**

| Mô hình | Kích thước | Retrieval | Avg |
|---|---|---|---|
| gte-Qwen2-7B-instruct | 7B | 46.05 | 65.84 |
| gte-Qwen2-1.5B-instruct | 1.5B | 42.01 | 63.47 |
| e5-Mistral-7B-instruct | 7B | 41.73 | 67.67 |
| **multilingual-e5-large-instruct** | 560M | **40.88** | **67.99** (cao nhất) |
| **bge-m3** | 568M | **39.84** | 64.90 |
| gte-multilingual-base | 305M | 38.38 | 65.22 |
| multilingual-e5-large | 560M | 37.65 | 63.87 |
| m-e5-base | 278M | 34.50 | 62.42 |
| halong_embedding | 278M | 34.45 | 61.60 |
| **AITeamVN/Vietnamese_Embedding** | 568M | **34.18** | 63.34 |
| m-e5-small | 118M | 34.12 | 60.66 |
| bkai vietnamese-bi-encoder | 135M | 25.37 | 54.89 |

**Với GreenScan:**

- Trên dữ liệu dịch thuộc miền tổng quát, bge-m3 và m-e5-large-instruct dẫn đầu nhóm dưới 1B.
- Mô hình fine-tune cho tiếng Việt *không* hơn trên benchmark này, nhưng lại hơn trên Zalo legal (xem [S4.2]).
- Kết luận: chọn mô hình bằng gold của chính mình.

**Verdict: ADOPT** (làm căn cứ chọn ứng viên) **; TEST** (m-e5-large-instruct, gte-multilingual-base so với bge-m3 và Vietnamese_Embedding trên gold GreenScan).

**[S4.2] Model card các embedding tiếng Việt** (số [self-reported], giao thức đánh giá khác nhau nên không so chéo được)

- **AITeamVN/Vietnamese_Embedding** (https://huggingface.co/AITeamVN/Vietnamese_Embedding)
  - Fine-tune từ bge-m3 trên khoảng 300K triplet; 0.6B; max 2048 token; 1024 chiều; Apache-2.0.
  - Zalo Legal 2021: Acc@1 0.7274, MRR@10 0.8181, so với bge-m3 0.5682 / 0.6822.
- **bkai-foundation-models/vietnamese-bi-encoder** (https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder)
  - Gốc PhoBERT-base-v2; 0.1B; max 256 token; **bắt buộc tách từ**; card ghi Apache-2.0.
  - Train trên MS MARCO và SQuAD v2 dịch, cộng 80% train Zalo. Đánh giá trên 20% còn lại: Acc@1 73.28%, MRR@10 80.73%.
  - **Lưu ý licence:** phobert-base-v2 dùng **AGPL-3.0** (xem [S4.10]), nên cần kiểm tra licence kế thừa nếu thương mại hoá.
- **dangvantuan/vietnamese-embedding** (https://huggingface.co/dangvantuan/vietnamese-embedding)
  - Gốc PhoBERT; 135M; max 512; cần tách từ (PyVi); Apache-2.0.
  - Tối ưu cho STS (Pearson trung bình 84.21 trên 7 bộ). Không có số cho retrieval.
- **hiieu/halong_embedding** (https://huggingface.co/hiieu/halong_embedding)
  - Gốc multilingual-e5-base; 278M; Matryoshka; Apache-2.0.
  - Zalo legal Acc@1 0.8294 (tập đánh giá in-house).
- **Đa ngôn ngữ:**
  - BAAI/bge-m3: MIT, 568M, max 8192 token, hỗ trợ dense + sparse + multi-vector. Paper: Chen et al., arXiv:2402.03216.
  - intfloat/multilingual-e5-large-instruct: MIT, 560M, max 512, *bắt buộc instruction cho query*. Paper: Wang et al., arXiv:2402.05672.
  - intfloat/multilingual-e5-small: MIT, 118M.
  - Alibaba-NLP/gte-multilingual-base: Apache-2.0, 305M, max 8192. Paper mGTE, EMNLP 2024 Industry.
  - Qwen/Qwen3-Embedding-0.6B: Apache-2.0, 0.6B, ngữ cảnh 32K, hơn 100 ngôn ngữ, MTEB multilingual 64.33 [self-reported]. Chưa có trong VN-MTEB.

**Verdict: TEST.** Ưu tiên gte-multilingual-base hoặc m-e5-small cho CPU; giữ bge-m3 hoặc Vietnamese_Embedding qua FPT.

**[S4.3] Nguyen, P.-V., Tran, M.-N., Nguyen, L., & Dinh, D. (2024/2025).** *Advancing Vietnamese Information Retrieval with Learning Objective and Benchmark.* PACLIC 38 (2024); arXiv:2503.07470. https://arxiv.org/abs/2503.07470

- **Nội dung:** benchmark retrieval và rerank tiếng Việt, cùng một biến thể InfoNCE.
- **Verdict: CONTEXT.**

### 4.2 Reranker tiếng Việt

- **BAAI/bge-reranker-v2-m3** (https://huggingface.co/BAAI/bge-reranker-v2-m3): Apache-2.0, 0.6B, gốc bge-m3, đa ngôn ngữ. Dữ liệu train có cả FEVER.
- **AITeamVN/Vietnamese_Reranker** (https://huggingface.co/AITeamVN/Vietnamese_Reranker): fine-tune bge-reranker-v2-m3 trên khoảng 1.1M triplet; Apache-2.0; 0.6B. Zalo legal Acc@1 0.7944, MRR@10 0.8672 [self-reported].
- **itdainb/PhoRanker** (https://huggingface.co/itdainb/PhoRanker): cross-encoder khoảng 0.1B, max 256, **cần VnCoreNLP để tách từ**; card ghi Apache-2.0 nhưng base model cần kiểm tra licence. Trên mMARCO-vi: NDCG@10 0.7422, so với bge-reranker-v2-m3 0.6872 [self-reported].
- **Dang, P.-N., Nguyen, K.-L., & Pham, T.-H. (2025).** *ViRanker: A BGE-M3 & Blockwise Parallel Transformer Cross-Encoder for Vietnamese Reranking.* arXiv:2509.09131. https://arxiv.org/abs/2509.09131
  - Train trên corpus 8GB; trên MMARCO-VI vượt các baseline đa ngôn ngữ và *"competing closely with PhoRanker"*.

**Với GreenScan:** PhoRanker (khoảng 0.1B) là ứng viên chạy CPU. Bản ghi nhớ của nhóm cho biết chạy bge-reranker cục bộ quá chậm.

**Verdict: TEST** (PhoRanker trên CPU so với bge-reranker-v2-m3 qua FPT; đo bằng gold, có pool đầy đủ).

### 4.3 NLI tiếng Việt và cross-encoder NLI đa ngôn ngữ

**[S4.4] Huynh, T. V., Nguyen, K. V., & Nguyen, N. L.-T. (2022).** *ViNLI: A Vietnamese Corpus for Studies on Open-Domain Natural Language Inference.* COLING 2022, tr. 3858–3872. https://aclanthology.org/2022.coling-1.339/

- **Dữ liệu:** 30,376 cặp premise–hypothesis từ hơn 800 bài báo, 13 chủ đề.
- **Kết quả:** hệ thống tốt nhất kém con người 14.20 điểm accuracy.
- **Licence:** "available publicly for research purposes" [UNVERIFIED licence cụ thể].

**[S4.5] Huynh, T. V., Nguyen, K. V., & Nguyen, N. L.-T. (2024/2025).** *A New Benchmark Dataset and Mixture-of-Experts Language Models for Adversarial Natural Language Inference in Vietnamese* (ViANLI). Expert Systems with Applications (accepted); arXiv:2406.17716. https://arxiv.org/abs/2406.17716

- **Dữ liệu:** 10,012 cặp (8,012 / 1,000 / 1,000), CC BY-NC-SA 4.0 (https://huggingface.co/datasets/uitnlp/ViANLI).
- **Kết quả:** XLM-R Large chỉ đạt 45.5%, NLIMoE 47.3%.

**[S4.6] Conneau, A., Lample, G., Rinott, R., Williams, A., Bowman, S. R., Schwenk, H., & Stoyanov, V. (2018).** *XNLI: Evaluating Cross-lingual Sentence Representations.* EMNLP 2018. https://arxiv.org/abs/1809.05053

- **Dữ liệu:** 15 ngôn ngữ có tiếng Việt; mỗi ngôn ngữ dev 2,490 / test 5,010 (train 392,702 là MNLI qua dịch). Licence **CC BY-NC 4.0** (file LICENSE trên GitHub facebookresearch/XNLI).

**[S4.7] MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** (https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)

- MIT; khoảng 0.3B (mDeBERTa-v3-base); train trên 2.73M cặp NLI dịch máy (26 ngôn ngữ) *cộng tập XNLI validation*.
- XNLI test tiếng Việt: **0.793**.
- Tác giả cảnh báo dữ liệu dịch máy làm giảm chất lượng cho NLI phức tạp. Số XNLI không phản ánh hiệu năng trên báo cáo ESG.

**Với GreenScan (cho §4.3):**

- Đây là ứng viên *tiền lọc* stance chạy CPU: cặp claim–evidence rõ ràng là entailment hoặc contradiction thì không cần gọi GLM.
- Nhưng Climate-FEVER cho thấy NLI train ngoài miền có thể rơi xuống khoảng 39% accuracy [S2.4], và WiCE cho thấy claim thật khó [S2.5].
- Cần A/B trên gold. Không cho mô hình quyết định với claim có số.

**Verdict: TEST** (mDeBERTa-xnli); **CONTEXT** (ViNLI, ViANLI, XNLI). Lưu ý licence NC.

### 4.4 Dữ liệu fact-checking tiếng Việt

**[S4.8] Hoa, T. T., Duy, T. Q., Tran, K. Q., & Nguyen, K. V. (2025).** *ViFactCheck: A New Benchmark Dataset and Methods for Multi-domain News Fact-Checking in Vietnamese.* AAAI 2025, tr. 308–316. https://arxiv.org/abs/2412.15308

- **Dữ liệu:**
  - 7,232 cặp claim–evidence (5,060 / 723 / 1,449), 12 chủ đề tin tức, 9 báo.
  - Nhãn Supported / Refuted / NEI; Fleiss κ = 0.83.
  - **MIT** (https://huggingface.co/datasets/tranthaihoa/vifactcheck).
- **Kết quả:** Gemma đạt macro-F1 89.90%.
- **Với GreenScan:** dữ liệu tiếng Việt có licence thoáng nhất để fine-tune hoặc đánh giá một mô hình stance 3 lớp. Miền là tin tức, khác báo cáo ESG.
- **Verdict: TEST.**

**[S4.9] Các bộ khác**

- **ViWikiFC:** Le, H. T., To, L. T., Nguyen, M. T., & Nguyen, K. V. (2024). *ViWikiFC: Fact-Checking for Vietnamese Wikipedia-Based Textual Knowledge Source.* arXiv:2405.07615. https://arxiv.org/abs/2405.07615
  - Hơn 20K claim (theo SemViQA: 16,738 / 2,090 / 2,091).
  - BM25 tìm bằng chứng tốt cho SUPPORTS (88.30%) và REFUTES (86.93%) nhưng chỉ 56.67% cho NEI.
  - InfoXLM-Large verdict F1 86.51%; pipeline strict accuracy chỉ 67.00%.
  - Licence [UNVERIFIED].
- **ISE-DSC01** (UIT Data Science Challenge 2023): khoảng 48K mẫu (37,967 / 4,794 / 5,396 theo SemViQA), nhãn SUPPORTED / REFUTED / NEI, ngữ cảnh có thể dài hơn 4,800 token. Licence [UNVERIFIED].
- **SemViQA:** Tran, D. X., Nguyen, N. V., Tran, T. T., Hoang, A. T., Duong, T. V., Le, D. T., & Le, P.-L. (2026). ACL 2026 Industry. https://aclanthology.org/2026.acl-industry.94/ (arXiv:2503.00955)
  - Strict accuracy 78.97% (ISE-DSC01) và 80.82% (ViWikiFC); dùng encoder cỡ large (InfoXLM, XLM-R).
  - Bản Faster nhanh hơn 7 lần; các LLM Qwen chậm hơn rõ rệt.
- **To, L. T. et al. (2024).** *Evaluating Large Language Model Capability in Vietnamese Fact-Checking Data Generation.* arXiv:2411.05641. https://arxiv.org/abs/2411.05641
  - *"LLMs still cannot match the data quality produced by humans"*.
  - Lập luận cho việc gold của GreenScan phải do người gán.

**Verdict: CONTEXT** (ViWikiFC, ISE-DSC01, SemViQA); **ADOPT** (To et al. làm lập luận "gold do người gán").

### 4.5 Encoder tiếng Việt

**[S4.10] Nguyen, D. Q., & Nguyen, A. T. (2020).** *PhoBERT: Pre-trained language models for Vietnamese.* Findings of EMNLP 2020, tr. 1037–1042. https://aclanthology.org/2020.findings-emnlp.92/

| Phiên bản | Tham số | Dữ liệu pretrain | Licence |
|---|---|---|---|
| phobert-base | 135M | 20GB | **MIT** |
| phobert-large | 370M | 20GB | **MIT** |
| phobert-base-v2 | 135M | 20GB + 120GB OSCAR | **AGPL-3.0** |

- Cả ba: max 256 token, **bắt buộc tách từ bằng VnCoreNLP RDRSegmenter** (theo GitHub VinAIResearch/PhoBERT).

**[S4.11] Tran, C. D., Pham, N. H., Nguyen, A. T., Hy, T. S., & Vu, T. (2023).** *ViDeBERTa: A powerful pre-trained language model for Vietnamese.* Findings of EACL 2023, tr. 1071–1078. https://aclanthology.org/2023.findings-eacl.79/

- **Nội dung:** 3 cỡ xsmall / base / large; bản base có backbone 86M, tức khoảng 23% của PhoBERT-large, nhưng đạt bằng hoặc hơn SOTA trước đó ở POS, NER và QA. Licence trên HF [UNVERIFIED].

**Verdict: TEST** (backbone cho claim detector tiếng Việt nếu có dữ liệu). Ưu tiên PhoBERT v1 (MIT) nếu cân nhắc licence.

### 4.6 PDF và OCR tiếng Việt: ghi chú chất lượng

- **Survey:** Le, A., Lam, T., & Nguyen, D. (2025). *A Survey on Vietnamese Document Analysis and Recognition: Challenges and Future Directions.* arXiv:2506.05061. https://arxiv.org/abs/2506.05061
  - Thách thức chính: dấu thanh phức tạp, biến thể tài liệu thực tế, thiếu dữ liệu gán nhãn lớn.
  - VLM và LLM mở ra hướng mới nhưng vẫn vướng domain adaptation và chi phí tính toán.
- **Tesseract `vie`** (tessdata_best, Apache-2.0; https://github.com/tesseract-ocr/tessdata_best)
  - Issue #66 (02/04/2017, Tesseract 4.00) ghi nhận nhầm *dấu sắc ↔ dấu hỏi khi nằm trên dấu mũ (dấu chồng)* (https://github.com/tesseract-ocr/langdata/issues/66).
  - Chưa thấy số liệu đánh giá peer-review gần đây [UNVERIFIED về mức lỗi hiện nay].
- **VietOCR** (https://github.com/pbcquoc/vietocr; Apache-2.0)
  - Chỉ nhận dạng *ảnh dòng chữ*, cần bộ phát hiện text riêng.
  - VGG-Transformer đạt 88% "full sequence precision", VGG-Seq2Seq 87.01% (nhanh hơn) [self-reported]. Train trên khoảng 10 triệu ảnh.
- **PaddleOCR** (Apache-2.0; https://github.com/PaddlePaddle/PaddleOCR)
  - PP-OCRv5 nhận dạng đa ngôn ngữ (106 ngôn ngữ, có mô hình Latin).
  - **PaddleOCR-VL-0.9B:** Cui et al. (2025), arXiv:2510.14528. Kết hợp NaViT encoder và ERNIE-4.5-0.3B; parse văn bản, bảng, công thức, biểu đồ; 109 ngôn ngữ; Apache-2.0.
  - Việc tiếng Việt có trong danh sách 109 ngôn ngữ: [UNVERIFIED].
- **Vintern-1B:** Doan, K. T., Huynh, B. G., Hoang, D. T., Pham, T. D., Pham, N. H., Nguyen, Q. T. M., Vo, B. Q., & Hoang, S. N. (2024), *Vintern-1B: An Efficient Multimodal Large Language Model for Vietnamese.* arXiv:2408.12480. Bản v3.5 (https://huggingface.co/5CD-AI/Vintern-1B-v3_5): MIT, 0.9B, gốc InternVL2.5-1B. DocVQA 78.8, vi-MTVQA 41.9, OCRBench 706 [self-reported].

**Ghi chú kỹ thuật (kinh nghiệm thực hành, không phải số liệu từ tài liệu):**

- Phần lớn báo cáo thường niên và báo cáo bền vững của doanh nghiệp niêm yết là PDF sinh số (có text layer). Nên trích text layer trước; Adhikari & Agarwal 2024 cho thấy PyMuPDF/pypdfium trích text tốt.
- Chỉ OCR khi trang là ảnh scan.
- Luôn chuẩn hoá Unicode **NFC**, vì dấu tiếng Việt có thể ở dạng dựng sẵn hoặc tổ hợp. Lỗi accent-fold mà nhóm đã sửa ngày 20/09 thuộc đúng họ lỗi này.

**Verdict:**

- **ADOPT:** text-layer trước, chuẩn hoá NFC.
- **TEST:** VietOCR hoặc PaddleOCR cho trang scan; Vintern hoặc PaddleOCR-VL cho bảng dạng ảnh.
- **AVOID:** chỉ dùng Tesseract `vie` cho bảng số có dấu.

---

## 5. Trích xuất KPI và bảng từ báo cáo bền vững bằng LLM; hiểu tài liệu PDF

### 5.1 Trích xuất ESG/KPI bằng LLM (2023–2026)

**[S5.1] Zou, Y., Shi, M., Chen, Z., Deng, Z., Lei, Z., Zeng, Z., Yang, S., Tong, H., Xiao, L., & Zhou, W. (2023).** *ESGReveal: An LLM-based approach for extracting structured data from ESG reports.* arXiv:2312.17264. https://arxiv.org/abs/2312.17264

- **Kết quả:** trên báo cáo ESG 2022 của 166 công ty niêm yết HKEX, GPT-4 với RAG đạt **76.9%** accuracy trích dữ liệu và 83.7% phân tích công bố. Hệ thống chưa xử lý ảnh.
- **Verdict: CONTEXT** (khoảng 1/4 giá trị trích bằng LLM là sai, nên cần kiểm của con người hoặc rule).

**[S5.2] Bronzini, M., Nicolini, C., Lepri, B., Passerini, A., & Staiano, J. (2024).** *Glitter or Gold? Deriving Structured Insights from Sustainability Reports via Large Language Models.* EPJ Data Science 13, 41. https://doi.org/10.1140/epjds/s13688-024-00481-2 (arXiv:2310.05628)

- **Kết quả:** LLM, in-context learning và RAG trích sáng kiến ESG; tìm ra hơn 500 chủ đề ESG, nhiều chủ đề nằm ngoài các bảng phân loại hiện có.
- **Verdict: CONTEXT.**

**[S5.3] Beck, J., Steinberg, A., Dimmelmeier, A., Domenech Burin, L., Kormanyos, E., Fehr, M., & Schierholz, M. (2025).** *Addressing data gaps in sustainability reporting: A benchmark dataset for greenhouse gas emission extraction.* Scientific Data (2025). https://doi.org/10.1038/s41597-025-05664-8

- **Quy trình:**
  1. Pipeline LLM trích chỉ số phát thải từ 139 báo cáo bền vững.
  2. **Hai người không chuyên** kiểm độc lập.
  3. Báo cáo được cả hai đồng ý thì vào gold; bất đồng thì chuyên gia xét qua 2 vòng, còn lại thì họp trực tiếp.
- **Với GreenScan:** đây là quy trình gán nhãn mẫu cho Quỳnh và Thảo: LLM gợi ý → 2 người kiểm → adjudication. Nó giảm phụ thuộc vào chuyên gia mà vẫn giữ chất lượng.
- **Verdict: ADOPT.**

**[S5.4] Wilhelmi, L., Bruns, C., & Schumann, M. (2026).** *Enhancing the Extraction of GHG Emission-Reduction Targets from Sustainability Reports Using Vision Language Models.* Machine Learning and Knowledge Extraction 8(2), 37. https://doi.org/10.3390/make8020037

- **Kết quả:** trên báo cáo ngành dầu khí, Mistral Small 3.2 với đầu vào **text + ảnh trang** cho F1 tốt nhất (0.82), đặc biệt ở layout phức tạp. Vẫn khó với trang dày đặc hình ảnh và lỗi *"inference-based hallucinations"*.
- **Verdict: TEST** (sau freeze; chỉ cho bảng dạng ảnh).

**[S5.5] Zheng, S., Duan, Y., Xue, C., & Salim, F. D. (2026).** *Scope3Trace: Evidence-Based Identification and Extraction of Scope 3 GHG Emissions from Sustainability Reports.* arXiv:2607.17122. https://arxiv.org/abs/2607.17122

- **Thiết kế:** LLM định vị trang và dựng lại bảng; **rule xử lý parse số, ánh xạ category và kiểm bằng chứng với text OCR** ("hybrid rule–LLM").
- **Với GreenScan:** đây là thiết kế gần GreenScan nhất trong tài liệu 2026, ủng hộ việc để rule giữ phần số.
- **Verdict: ADOPT** (lập luận kiến trúc).

**[S5.6] Schmoll, J., & Jatowt, A. (2025).** *Automated Analysis of Sustainability Reports: Using Large Language Models for the Extraction and Prediction of EU Taxonomy-Compliant KPIs.* arXiv:2512.24289. https://arxiv.org/abs/2512.24289

- **Kết quả** (190 báo cáo):
  - LLM làm khá ở task định tính.
  - LLM *"substantially underperform on quantitative financial KPI prediction"* trong zero-shot.
  - Metadata ngắn gọn cho kết quả *tốt hơn* đưa cả báo cáo.
  - Calibration độ tự tin không đáng tin.
  - Tác giả kết luận LLM hợp với vai trò trợ lý cho chuyên viên.
- **Verdict: CONTEXT** (rất hợp để trả lời "sao không để GPT đọc cả báo cáo?").

**[S5.7] Ali, M., Abdallah, A., & Jatowt, A. (2025/2026).** *SustainableQA: A Comprehensive Question Answering Dataset for Corporate Sustainability and EU Taxonomy Reporting.* EMNLP 2026 (Main); arXiv:2508.03000. https://arxiv.org/abs/2508.03000

- **Kết quả:** hơn 195,000 cặp hỏi–đáp có bước chuyển *table-to-paragraph*; mô hình 8B được fine-tune vượt các mô hình lớn hơn.
- **Verdict: CONTEXT.**

**[S5.8] Gupta, T., Goel, T., & Verma, I. (2025).** *Exploring Multimodal Language Models for Sustainability Disclosure Extraction: A Comparative Study.* Workshop on Insights from Negative Results in NLP, tr. 141–149. https://aclanthology.org/2025.insights-1.13/

- **Kết quả (kết quả âm):** nhiều VLM mã nguồn mở hạn chế rõ khi trích thông tin từ infographic, bảng và biểu đồ trong báo cáo bền vững.
- **Verdict: CONTEXT** (AVOID kỳ vọng "VLM mở đọc mọi bảng").

**[S5.9] Dave, A., Zhu, M., Hu, D., & Tiwari, S. (2024).** *Climate AI for Corporate Decarbonization Metrics Extraction.* arXiv:2411.03402. https://arxiv.org/abs/2411.03402

- **Nội dung:** pipeline LLM trích và *kiểm* các chỉ số mục tiêu giảm phát thải, có kiểm định bởi chuyên gia (SME).
- **Verdict: CONTEXT.**

Xem thêm [S1.6] (QA trích năm và % mục tiêu) và [S1.7] (ChatReport).

### 5.2 Hiểu tài liệu PDF và bảng

- **Auer, C. et al. (19 tác giả) (2024).** *Docling Technical Report.* arXiv:2408.09869. https://arxiv.org/abs/2408.09869
  - Gói MIT; dùng DocLayNet (layout) và TableFormer (cấu trúc bảng); chạy được trên phần cứng phổ thông.
- **Nassar, A., Livathinos, N., Lysak, M., & Staar, P. (2022).** *TableFormer: Table Structure Understanding with Transformers.* CVPR 2022; arXiv:2203.01017. https://arxiv.org/abs/2203.01017
  - TEDS 91% → 98.5% với bảng đơn giản, 88.7% → 95% với bảng phức tạp.
  - Lấy nội dung ô trực tiếp từ PDF lập trình được, nên xử lý được bảng không phải tiếng Anh.
- **Smock, B., Pesala, R., & Abraham, R. (2022).** *PubTables-1M: Towards comprehensive table extraction from unstructured documents.* CVPR 2022; arXiv:2110.00061. https://arxiv.org/abs/2110.00061
  - Gần 1 triệu bảng; Table Transformer (TATR).
- **Adhikari, N. S., & Agarwal, S. (2024/2025).** *A Comparative Study of PDF Parsing Tools Across Diverse Document Categories.* arXiv:2410.09871. https://arxiv.org/abs/2410.09871
  - So sánh 10 công cụ trên DocLayNet.
  - Trích text: PyMuPDF và pypdfium tốt.
  - Phát hiện bảng: **TATR tốt nhất** ở nhóm Financial, Patent, Law và Scientific; Camelot tốt cho hồ sơ thầu.
  - Chọn công cụ theo loại tài liệu.
- **Ouyang, L. et al. (2025).** *OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations.* CVPR 2025; arXiv:2412.07626. https://arxiv.org/abs/2412.07626
  - 9 nguồn tài liệu, 19 loại layout, 15 thuộc tính; có metric TEDS cho bảng.
  - Leaderboard trên GitHub thay đổi liên tục; không có tiếng Việt.
  - Danh sách tác giả đầy đủ: xem arXiv [chưa liệt kê đủ].
- **Poznanski, J. et al. (2025).** *olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models.* arXiv:2502.18443. https://arxiv.org/abs/2502.18443
  - VLM 7B; khoảng 176 USD cho mỗi triệu trang (so với hơn 6,240 USD nếu dùng GPT-4o); olmOCR-Bench có 1,400 PDF.
  - Quá nặng cho laptop.
- **Nguyen, Q. H., Trinh, P. A., Mai, P. Q. H., & Trinh, T. P. (2025).** *FinStat2SQL: A Text2SQL Pipeline for Financial Statement Analysis.* INLG 2025. https://aclanthology.org/2025.inlg-main.27/
  - Báo cáo tài chính theo chuẩn VAS; mô hình 7B fine-tune đạt 61.33% trên bộ QA tổng hợp.
  - Một trong số ít công trình NLP về báo cáo tài chính Việt Nam.

**Verdict cho GreenScan:**

- **ADOPT:** text layer qua PyMuPDF/pypdfium là đường chính.
- **TEST:** Docling/TATR cho bảng KPI trong PDF sinh số.
- **CONTEXT:** VLM (Vintern, PaddleOCR-VL, olmOCR), chỉ dùng cho trang ảnh.

---

## 6. Phương pháp đánh giá cho gold set nhỏ

### 6.1 Khoảng tin cậy, bootstrap và statistical power

- **Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020).** *With Little Power Comes Great Responsibility.* EMNLP 2020, tr. 9263–9274. https://aclanthology.org/2020.emnlp-main.745/
  - Thí nghiệm thiếu power rất phổ biến trong NLP; test set nhỏ khiến hầu hết so sánh với SOTA không đủ power.
  - Ví dụ: với MT, test set 2,000 câu chỉ có khoảng 75% power để phát hiện chênh lệch 1 BLEU.
  - **ADOPT.**
- **Miller, E. (2024).** *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations.* arXiv:2411.00640. https://arxiv.org/abs/2411.00640
  - Báo cáo SE và CI.
  - Dùng **clustered standard errors** khi các câu hỏi theo nhóm, vì *"may lead an analyst to suppose that measurement … is much more precise than it actually is"*. Trên DROP, SE có cụm lớn hơn 3 lần SE ngây thơ.
  - So sánh hai hệ thống bằng *paired differences* trên từng câu.
  - Khuyến nghị eval mới có ít nhất 1,000 câu.
  - **ADOPT** (cluster theo công ty, paired bootstrap cho ablation).
- **Dror, R., Baumer, G., Shlomov, S., & Reichart, R. (2018).** *The Hitchhiker's Guide to Testing Statistical Significance in NLP.* ACL 2018, tr. 1383–1392. https://aclanthology.org/P18-1128/
  - Đưa ra quy trình chọn kiểm định phù hợp với metric và thiết kế.
  - **ADOPT.**
- **Berg-Kirkpatrick, T., Burkett, D., & Klein, D. (2012).** *An Empirical Investigation of Statistical Significance in NLP.* EMNLP-CoNLL 2012, tr. 995–1005. https://aclanthology.org/D12-1091/
- **Koehn, P. (2004).** *Statistical Significance Tests for Machine Translation Evaluation.* EMNLP 2004, tr. 388–395. https://aclanthology.org/W04-3250/
  - Kinh điển về paired bootstrap resampling.
  - **CONTEXT/ADOPT.**
- **Wilson, E. B. (1927).** *Probable Inference, the Law of Succession, and Statistical Inference.* JASA 22(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
- **Agresti, A., & Coull, B. A. (1998).** *Approximate Is Better than "Exact" for Interval Estimation of Binomial Proportions.* The American Statistician 52(2), 119–126. https://doi.org/10.2307/2685469
  - Dùng khoảng Wilson hoặc Agresti–Coull thay cho khoảng Wald khi n nhỏ.
  - **ADOPT.**

### 6.2 Cohen's κ: diễn giải và các bẫy

- **Landis, J. R., & Koch, G. G. (1977).** *The measurement of observer agreement for categorical data.* Biometrics 33(1), 159–174. https://doi.org/10.2307/2529310
  - Thang quen thuộc: 0.41–0.60 moderate, 0.61–0.80 substantial, 0.81–1.00 almost perfect.
- **McHugh, M. L. (2012).** *Interrater reliability: the kappa statistic.* Biochemia Medica 22(3), 276–282. https://doi.org/10.11613/BM.2012.031
  - Thang của Cohen có thể *"too lenient"*, vì κ = 0.41 bị coi là chấp nhận được.
  - Bảng đề xuất chặt hơn: 0.60–0.79 "moderate", 0.80–0.90 "strong".
  - Nên báo cáo kèm percent agreement.
- **Artstein, R., & Poesio, M. (2008).** *Inter-Coder Agreement for Computational Linguistics.* Computational Linguistics 34(4), 555–596. https://aclanthology.org/J08-4004/
  - Survey chuẩn cho NLP.
  - Ngưỡng hợp lý tuỳ mục đích dùng dữ liệu.
  - Với nhãn có thứ bậc nên cân nhắc hệ số có trọng số.
- **Feinstein, A. R., & Cicchetti, D. V. (1990).** *High agreement but low kappa: I. The problems of two paradoxes.* Journal of Clinical Epidemiology 43(6), 543–549. https://doi.org/10.1016/0895-4356(90)90158-L
  - Khi phân bố nhãn lệch, κ có thể thấp dù đồng ý cao.
  - GreenScan dễ gặp nếu đa số cặp là SUPPORTED. Nên báo cáo thêm percent agreement, agreement theo lớp, và free-marginal κ (Randolph) như AVeriTeC.
- **Sim, J., & Wright, C. C. (2005).** *The kappa statistic in reliability studies: use, interpretation, and sample size requirements.* Physical Therapy 85(3), 257–268. https://doi.org/10.1093/ptj/85.3.257
  - Bảng cỡ mẫu cho nghiên cứu κ; nhấn mạnh báo cáo CI của κ.

**Đối chiếu agreement trong tài liệu (để đặt κ ≥ 0.7 vào bối cảnh):**

| Bộ dữ liệu | Hệ số | Giá trị |
|---|---|---|
| Environmental claims | Krippendorff α | 0.47 |
| Climate-FEVER (evidence) | Krippendorff α | 0.334 |
| AVeriTeC | free-marginal κ / Fleiss κ | 0.619 / 0.503 |
| FEVER | Fleiss κ | 0.684 |
| ChatReport (hallucination, ChatGPT / GPT-4) | κ | 0.54 / 0.21 |
| ViFactCheck | Fleiss κ | 0.83 |
| FinDVer | percent agreement | 90.3% |

**ADOPT:** báo cáo κ kèm CI, percent agreement, ma trận nhầm lẫn giữa hai người gán, và agreement theo từng lớp.

### 6.3 Company-held-out split và leakage

- **Gorman, K., & Bedrick, S. (2019).** *We Need to Talk about Standard Splits.* ACL 2019, tr. 2786–2791. https://aclanthology.org/P19-1267/
  - Thứ hạng hệ thống không ổn định qua các split ngẫu nhiên.
- **Søgaard, A., Ebert, S., Bastings, J., & Filippova, K. (2021).** *We Need To Talk About Random Splits.* EACL 2021, tr. 1823–1832. https://aclanthology.org/2021.eacl-main.156/
  - Split ngẫu nhiên *"lead to overly optimistic performance estimates"*.
  - Nên dùng nhiều test set độc lập; nếu không được thì dùng nhiều biased split.
- **Lewis, P., Stenetorp, P., & Riedel, S. (2021).** *Question and Answer Test-Train Overlap in Open-Domain Question Answering Datasets.* EACL 2021, tr. 1000–1008. https://aclanthology.org/2021.eacl-main.86/
  - 30% câu hỏi test có bản gần trùng trong train; chênh lệch hiệu năng trung bình 61% giữa câu lặp và không lặp.
- **Kapoor, S., & Narayanan, A. (2023).** *Leakage and the reproducibility crisis in machine-learning-based science.* Patterns. https://doi.org/10.1016/j.patter.2023.100804
  - Phân loại 8 dạng leakage; 294 paper ở 17 lĩnh vực bị ảnh hưởng.
- Xem thêm A3CG [S1.10]: đánh giá trên category chưa thấy.

**Với GreenScan:**

- Lexicon cue, rule và ngưỡng *đã được chỉnh trên* các công ty dev. Test trên công ty mới là cách duy nhất để chống tự lừa mình.
- Báo cáo kết quả theo từng công ty để thấy độ dao động.

**ADOPT.**

### 6.4 Pooling bias trong đánh giá retrieval

- **Zobel, J. (1998).** *How reliable are the results of large-scale information retrieval experiments?* SIGIR 1998. https://doi.org/10.1145/290941.291014
  - Thứ hạng tương đối giữa các hệ thống ổn định, nhưng *"recall is overestimated: it is likely that many relevant documents have not been found"*.
- **Buckley, C., & Voorhees, E. M. (2004).** *Retrieval evaluation with incomplete information.* SIGIR 2004. https://doi.org/10.1145/1008992.1009000
  - Đề xuất bpref, metric bền với relevance judgment không đầy đủ.
- **Buckley, C., Dimmick, D., Soboroff, I., & Voorhees, E. (2007).** *Bias and the limits of pooling for large collections.* Information Retrieval 10(6). https://doi.org/10.1007/s10791-007-9032-x
  - Với collection lớn, pool bị lệch về phía tài liệu khớp từ khoá của truy vấn.
- **Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., & Gurevych, I. (2021).** *BEIR.* NeurIPS 2021 D&B. https://arxiv.org/abs/2104.08663
  - *"Many BEIR datasets are found to be subject to a lexical bias"*.
  - Hole@10: BM25 6.4%, docT5query 2.8%, ANCE 14.4%, TAS-B 31.8%.
  - Sau khi gán bổ sung nhãn cho TREC-COVID, ANCE tăng từ 0.654 (dưới BM25) lên 0.735 (trên BM25 6.7 điểm).
- **Arabzadeh, N., Vtyurina, A., Yan, X., & Clarke, C. L. A. (2022; arXiv 2021).** *Shallow pooling for sparse labels.* Information Retrieval Journal. https://doi.org/10.1007/s10791-022-09411-0
  - Trên MS MARCO, top của ranker thường *được người đánh giá ưa hơn* tài liệu đã gán là liên quan.
- ClimRetrieve [S1.9]: chính tác giả gọi kết quả là "lower bound".

**Với GreenScan:**

1. Pool ứng viên từ *mọi* retriever cần so sánh (BM25, char n-gram, RRF, bge-m3, Vietnamese_Embedding, reranker) trước khi Quỳnh và Thảo gán nhãn.
2. Báo cáo Recall@k là "cận dưới trên tập đã gán".
3. Báo cáo thêm Hole@k của từng hệ thống.
4. Cân nhắc bpref hoặc metric chỉ tính trên tài liệu đã gán khi so sánh dense với lexical.

**ADOPT.**

### 6.5 Hướng dẫn cỡ mẫu (tính minh hoạ) [tự tính]

**Khoảng Wilson 95% cho accuracy:**

| n | p̂ = 0.70 | p̂ = 0.80 | p̂ = 0.90 |
|---|---|---|---|
| 60 | [0.575, 0.801] (±11.3 điểm %) | [0.682, 0.882] (±10.0) | [0.799, 0.953] (±7.7) |
| 80 | [0.592, 0.789] (±9.9) | [0.700, 0.873] (±8.7) | [0.815, 0.948] (±6.7) |
| 100 | [0.604, 0.781] (±8.8) | [0.711, 0.867] (±7.8) | [0.826, 0.945] (±6.0) |
| 200 | ±6.3 | ±5.5 | ±4.2 |

**CI xấp xỉ của κ = 0.70** (công thức SE xấp xỉ của Cohen, p_e = 0.5): n = 60 cho [0.52, 0.88]; n = 100 cho [0.56, 0.84]. Nghĩa là với 60–100 cặp, "κ = 0.7" chưa phân biệt được với 0.55.

**Chênh lệch accuracy tối thiểu phát hiện được** khi so cặp hai hệ thống (power 80%, α = 0.05), với tỷ lệ cặp hai hệ thống trả lời khác nhau là 10–30%:

- n = 80: khoảng 10–17 điểm %;
- n = 100: khoảng 9–15 điểm %;
- n = 200: khoảng 6–11 điểm %.

**Design effect do cụm theo công ty:** DE = 1 + (m − 1) × ICC. Ví dụ 80 claim từ 10 công ty (m = 8) với ICC = 0.1 thì DE = 1.7, cỡ mẫu hiệu dụng chỉ khoảng 47.

**Hệ quả:**

- Đặt ngưỡng pre-registered dưới dạng *khoảng* thay vì điểm.
- Ablation chỉ kết luận được khi chênh lệch lớn (trên 10–15 điểm %).
- Nên báo cáo "không phát hiện được khác biệt" thay vì "bằng nhau".

---

## 7. Ý nghĩa cho GreenScan

### (a) Dữ liệu công khai dùng được cho cross-lingual training/eval của claim detection và stance

| Bộ dữ liệu | Task | Kích thước | Ngôn ngữ | Licence | Dùng cho GreenScan |
|---|---|---|---|---|---|
| climatebert/environmental_claims [S1.5] | Claim môi trường (nhị phân) | 2,647 câu | EN | CC BY-NC-SA 4.0 | Train/eval claim detector qua dịch; đo recall extractor |
| climatebert/netzero_reduction_data [S1.6] | Net zero / reduction / none | 3,441 (card) | EN | Apache-2.0 (card) | Phân loại claim target |
| climatebert/climate_specificity [S1.4] | Cụ thể / không cụ thể | 1,320 | EN | CC BY-NC-SA 4.0 | Feature "cheap talk" |
| climatebert/climate_commitments_actions [S1.4] | Cam kết/hành động | 1,320 | EN | CC BY-NC-SA 4.0 | Feature hành động |
| A3CG [S1.10] | Aspect–action (implemented / planning / indeterminate) | 2,004 câu, 2,723 cặp | EN | CC BY 4.0 (paper) | Thuộc tính action-type trong rubric |
| FEVER [S2.1] | S/R/NEI | 185,445 claim | EN | CC BY-SA 3.0 + điều khoản Wikipedia | Tiền huấn luyện stance |
| VitaminC [S2.9] | Bằng chứng tương phản | >400K cặp | EN | CC BY-SA 3.0 | Test và train độ nhạy chi tiết |
| SciFact [S2.2] | S/R/NOINFO + rationale | 1.4K claim | EN | CC BY 4.0 (claim) | Định dạng gold |
| Climate-FEVER [S2.4] | S/R/NEI/DISPUTED | 1,535 claim / 7,675 cặp | EN | [UNVERIFIED] | Eval stance miền khí hậu |
| AVeriTeC [S2.3] | S/R/NEE/Conflicting | 4,568 | EN | CC BY-NC 4.0 | Định nghĩa lớp cherry-picking |
| QuanTemp [S2.6] | Claim số T/F/Conflicting | 15,514 | EN | CC BY-NC 4.0 | Taxonomy và test claim số |
| FinDVer [S2.14] | Entailed/refuted trên báo cáo tài chính | 2,100 | EN | MIT (repo) | Eval tham chiếu |
| ViFactCheck [S4.8] | S/R/NEI (tin tức) | 7,232 | **VI** | **MIT** | Fine-tune hoặc eval stance tiếng Việt |
| ViWikiFC [S4.9] | S/R/NEI | ~20.9K | VI | [UNVERIFIED] | Eval |
| ISE-DSC01 [S4.9] | S/R/NEI | ~48K | VI | [UNVERIFIED] | Eval (kiểm tra licence trước) |
| ViNLI [S4.4] | NLI | 30,376 | VI | Chỉ cho nghiên cứu [UNVERIFIED] | Stance/NLI |
| ViANLI [S4.5] | NLI đối kháng | 10,012 | VI | CC BY-NC-SA 4.0 | Kiểm độ bền |
| XNLI-vi [S4.6] | NLI | 2,490 dev / 5,010 test | VI | CC BY-NC 4.0 | Eval NLI |
| VN-MTEB: ClimateFEVER-VN [S4.1] | Retrieval (dịch) | 3,401 | VI (dịch máy) | Theo bộ gốc [UNVERIFIED] | Phép thử nhanh cho embedding |

**Lưu ý licence:** các bộ NC (NonCommercial) dùng được cho cuộc thi và nghiên cứu, *không* cho sản phẩm thương mại. phobert-base-v2 dùng AGPL-3.0.

### (b) Mô hình nhỏ (<1B, chạy được CPU) để thay thế hoặc tiền lọc lời gọi LLM

| Mô hình | Tham số | Licence | Vai trò đề xuất | Hiệu năng đã báo cáo | Ghi chú |
|---|---|---|---|---|---|
| MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 | ~0.3B | MIT | **Tiền lọc stance** (entail/contradict rõ thì không gọi GLM) | XNLI-vi acc 0.793 | Không dùng cho claim có số; cần A/B trên gold |
| MiniCheck-Flan-T5-Large | 0.77B | MIT | Grounding check (claim có được đoạn văn ủng hộ không) | LLM-AggreFact 75.0 (GPT-4o 75.9) | Chỉ tiếng Anh, cần translate-test |
| MiniCheck-RoBERTa-L / DeBERTa-v3-L | 0.4B | MIT (RoBERTa-L); DeBERTa-L [UNVERIFIED] | Như trên | Chưa trích số (không có trong 11 mô hình hiển thị mặc định của leaderboard) | Chỉ tiếng Anh |
| HHEM-2.1-Open | ~0.1B | Apache-2.0 | Hallucination check rẻ | AggreFact-SOTA BAcc 76.55%; khoảng 1.5 giây/2k token trên CPU [self-reported] | Chỉ tiếng Anh |
| climatebert/environmental-claims | 82M | Apache-2.0 | Claim detector (EN) / thầy cho distillation | Test F1 khoảng 83.8 (ClimateBERT trong paper) | Phải qua dịch |
| climatebert/netzero-reduction | ~82M | Apache-2.0 | Phân loại claim target | Acc 0.966 | Phải qua dịch |
| PhoBERT-base (v1) / ViDeBERTa-base | 135M / 86M backbone | MIT / [UNVERIFIED] | Backbone cho claim detector tiếng Việt | Cần dữ liệu VI | Cần tách từ (PhoBERT) |
| PhoRanker | ~0.1B | Apache-2.0 (card) | Rerank CPU | mMARCO-vi NDCG@10 0.742 (bge-reranker-v2-m3 0.687) [self-reported] | Cần VnCoreNLP |
| gte-multilingual-base | 305M | Apache-2.0 | Dense retrieval CPU | VN-MTEB Retrieval 38.38 | max 8192 token |
| multilingual-e5-small | 118M | MIT | Dense retrieval CPU nhẹ nhất | VN-MTEB Retrieval 34.12 | Cần prefix "query:"/"passage:" theo chuẩn E5 |
| multilingual-e5-large-instruct | 560M | MIT | Dense (ứng viên mạnh) | VN-MTEB Retrieval 40.88, Avg 67.99 | Cần instruction |
| Qwen3-Embedding-0.6B | 0.6B | Apache-2.0 | Dense | MTEB multilingual 64.33 [self-reported] | Chưa có trên VN-MTEB |

**Khuyến nghị dựa trên tài liệu:**

1. Không có mô hình <1B nào đã được kiểm chứng cho xác minh claim ESG tiếng Việt. Mọi lựa chọn đều là **TEST** và **không quyết định**, nhất quán với chính sách `decisive=false` hiện tại.
2. Thứ tự thử hợp lý sau freeze:
   - mDeBERTa-xnli làm bộ tiền lọc;
   - đo ở bao nhiêu % cặp nó "chắc chắn" và accuracy trên phần đó (đường risk–coverage);
   - chỉ chuyển phần còn lại cho GLM.

### (c) 8 phát biểu có thể bảo vệ trước Ban giám khảo (có trích dẫn)

1. **"Chúng tôi không tuyên bố 'phát hiện greenwashing'. Chúng tôi đánh dấu các tuyên bố cần kiểm tra theo rủi ro, vì hiện chưa có bộ dữ liệu greenwashing đã được xác minh nào."** Survey mới nhất khuyến nghị đúng kiến trúc này: pipeline phân rã, truy vết được, có con người giám sát (Calamai et al. 2025/2026 [S1.2]; Moodaley & Telukdarie 2023 [S1.1]).
2. **"So sánh số do code tất định đảm nhiệm, không do LLM."** LLM giảm accuracy tới 62% khi số bị nhiễu (NumPert 2025); mô hình frontier chỉ khoảng 74% trên phép đảo nhãn bằng số (Aarnes & Setty 2026); suy luận từ 3 bước trở lên chỉ 22.78% (FinQA 2021); trên báo cáo tài chính dài, LLM tốt nhất 77.2% so với chuyên gia 93.3% (FinDVer 2024) [S2.7, S2.8, S2.12, S2.14].
3. **"INSUFFICIENT_EVIDENCE là một kết luận hợp lệ, không phải lỗi."** Mọi benchmark fact-checking chuẩn đều có lớp này (FEVER, SciFact, AVeriTeC, Climate-FEVER). LLM lớn có xu hướng trả lời sai thay vì từ chối khi ngữ cảnh không đủ (Joren et al., ICLR 2025) [S2.1–S2.4, S2.19].
4. **"Nhãn PARTIALLY_SUPPORTED / CONTRADICTED và cách gộp nhãn tất định có tiền lệ học thuật."** AVeriTeC có lớp *Conflicting Evidence/Cherry-picking*; Climate-FEVER có *DISPUTED*. Hai bộ này gộp nhãn theo đúng quy tắc chúng tôi dùng (có cả ủng hộ lẫn bác bỏ thì là xung đột; không có gì thì không đủ bằng chứng). Khái niệm cherry-picking trong công bố khí hậu đã được kiểm chứng thực nghiệm (Bingler et al. 2022) [S2.3, S2.4, S1.4].
5. **"Chúng tôi đo retrieval và verification tách rời, và coi recall là cận dưới."** Thiết kế RAG phải theo từng task: có failure mode ảnh hưởng tới 12.6% mẫu ngay cả khi tài liệu hoàn hảo (Zhao et al., TOSEM 2026). Nhãn relevance pool từ hệ lexical làm lệch đánh giá dense retriever (BEIR: Hole@10 tới 31.8%). ClimRetrieve tự nhận kết quả là "lower bound" [S2.5b, S6.4, S1.9].
6. **"Gold do người gán, có κ và adjudication; chúng tôi không dùng LLM tự chấm."** LLM-as-judge có position bias và self-preference, độ tin cậy dao động lớn theo task (Wang et al. 2024; Shi et al. 2025; Bavaresco et al. 2025). Dữ liệu fact-check tiếng Việt do LLM sinh vẫn kém dữ liệu do người viết (To et al. 2024). Quy trình "LLM gợi ý → 2 người kiểm → adjudication" theo Beck et al. (Scientific Data 2025) [S3.8–S3.12, S4.9, S5.3].
7. **"Mục tiêu κ ≥ 0.7 là cao so với các bộ dữ liệu cùng loại."** Environmental claims α = 0.47; Climate-FEVER α = 0.334; AVeriTeC κ = 0.619; FEVER κ = 0.684 [§6.2]. Kết quả được báo cáo kèm khoảng tin cậy và tách theo công ty giữ lại (company-held-out), vì split ngẫu nhiên cho ước lượng quá lạc quan (Søgaard et al. 2021; Miller 2024) [§6.1, §6.3].
8. **"Màn hình kiểm toán viên hiển thị bằng chứng gốc, rule đã kích hoạt và thông tin còn thiếu."** Đây đúng là yêu cầu fact-checker chuyên nghiệp đặt ra (Warren et al., CHI 2025). Người dùng dựa vào *bằng chứng* để kiểm AI (Warren et al. 2026). Chúng tôi không dựa vào lời giải thích của LLM, vì giải thích có thể làm người dùng tin cả khi AI sai (Bansal et al., CHI 2021) [S3.16–S3.18].

### (d) Những điều tài liệu KHÔNG cho phép tuyên bố

1. **Không nói "GreenScan phát hiện / chứng minh doanh nghiệp X greenwashing"** hay "vi phạm pháp luật". Không có ground truth đã xác minh [S1.2]. Kết luận pháp lý thuộc về con người hoặc cơ quan có thẩm quyền. Nên nói "tuyên bố có rủi ro, cần kiểm tra" và "chưa đủ bằng chứng trong báo cáo".
2. **Không báo một con số accuracy đơn lẻ trên 60–100 cặp mà thiếu khoảng tin cậy.** Khoảng tin cậy thực tế rộng ±8–11 điểm %, và rộng hơn khi tính cụm theo công ty [§6.5].
3. **Không nói "tốt hơn GPT / tốt hơn baseline"** khi chênh lệch dưới khoảng 10–15 điểm % trên gold nhỏ (không đủ power, Card et al. 2020). Không so sánh trực tiếp số của mình với số trong paper tiếng Anh (FEVER, FinDVer…) vì khác dữ liệu, ngôn ngữ và nhãn.
4. **Không khoe accuracy nhị phân cao trên dữ liệu lệch lớp.** Climinator đạt 96.4% nhưng chỉ đoán lớp đa số đã khoảng 90.3%; với 12 lớp thì chỉ 34.5% [S1.8]. Luôn kèm macro-F1, baseline lớp đa số và coverage [S1.11].
5. **Không nói "recall retrieval = X%" như một con số tuyệt đối** khi nhãn relevance được pool từ một số hệ thống [§6.4].
6. **Không nói "LLM xác minh claim"** hay "AI đọc hiểu toàn bộ báo cáo". Tài liệu cho thấy LLM trích KPI định lượng kém và calibration không đáng tin (Schmoll & Jatowt 2025; ESGReveal 76.9%) [S5.1, S5.6]. Vai trò đúng của GLM là *gợi ý stance cho cặp mà rule không quyết được*.
7. **Không nói "lời giải thích giúp kiểm toán viên chính xác hơn"** khi chưa đo bằng thí nghiệm người dùng [S3.18, S3.19]. Cũng không nói kiểm toán viên sẽ tin AI: có bằng chứng về algorithm aversion trong kiểm toán [S3.20].
8. **Không nói "mô hình embedding tiếng Việt X là tốt nhất".** Thứ hạng đảo chiều giữa VN-MTEB (dịch máy) và Zalo legal (model card tự báo) [S4.1, S4.2]; chỉ gold của GreenScan mới quyết được.
9. **Không nói "chưa từng có nghiên cứu nào về greenwashing tiếng Việt".** Nên nói: *"chúng tôi không tìm thấy công trình NLP công bố (arXiv/ACL Anthology) về xác minh claim ESG trên báo cáo tiếng Việt tính đến 10/2026"*. Truy vấn arXiv của người lập chỉ thấy fact-checking tin tức/Wikipedia tiếng Việt và text2SQL trên báo cáo tài chính VAS.
10. **Không dùng dữ liệu hoặc mô hình NC hay AGPL cho định hướng thương mại** mà không kiểm tra licence (environmental_claims, AVeriTeC, XNLI, QuanTemp, ViANLI, phobert-base-v2).

### (e) Việc nên làm trước product freeze 10/10 (rủi ro thấp, không đổi logic verdict)

1. Sửa trích dẫn arXiv:2411.19463 trong `docs/research/README.md`: ghi rõ v1 (11/2024) hoặc chuyển sang bản TOSEM 2026.
2. Thêm vào protocol đo lường:
   - Wilson CI và cluster bootstrap theo công ty;
   - macro-F1 và baseline lớp đa số;
   - coverage và đường risk–coverage của hàng đợi;
   - Recall@k ghi rõ "cận dưới", kèm Hole@k.
3. Trước khi Quỳnh và Thảo gán relevance, pool ứng viên từ *tất cả* retriever (cả dense qua FPT).
4. Ghi vào hướng dẫn gán nhãn:
   - chính sách dung sai số (bài học Climate-FEVER);
   - định nghĩa claim môi trường theo EC (Stammbach);
   - cột rationale (SciFact);
   - thuộc tính action-type implemented / planning / indeterminate (A3CG);
   - loại claim số statistical / temporal / comparison / interval (QuanTemp).
5. Mở rộng "green traps" bằng các cặp đảo nhãn chỉ khác một con số (NumPert, VitaminC).
6. Để sau freeze (TEST): mDeBERTa-xnli làm tiền lọc; PhoRanker trên CPU; m-e5-large-instruct và gte-multilingual-base so với bge-m3 và Vietnamese_Embedding; claim detector cross-lingual để đo và tăng recall.

---

## Phụ lục: giới hạn của tổng quan này

- Toàn bộ nguồn đã được đối chiếu trực tiếp. Riêng số liệu trong model card Hugging Face là **[self-reported]**; một số licence chưa xác minh được (ghi **[UNVERIFIED]**).
- Bảng kết quả từng bộ con của VN-MTEB (ví dụ điểm ClimateFEVER-VN theo mô hình) quá nhỏ trong PDF để đọc chính xác, nên không trích.
- Số trên leaderboard OmniDocBench không được trích vì thay đổi liên tục.
- Không truy cập được bản toàn văn: Sim & Wright (2005), Buckley et al. (2007), Feinstein & Cicchetti (1990). Nội dung trích từ hiểu biết chuẩn về các bài kinh điển này và metadata DOI, không có số liệu cụ thể.
- Danh sách tác giả của Vintern-1B, OmniDocBench và mGTE đã được đối chiếu lại trên arXiv ngày 06/10/2026 (xem Danh mục tài liệu tham khảo). Docling (19 tác giả) và Kadavath et al. (36 tác giả) chỉ ghi tác giả đầu + "et al.".
- Phần §6.5 là **tính minh hoạ** của người lập (Python), dùng công thức Wilson, SE xấp xỉ của κ (Cohen 1960), MDE cho so sánh cặp, và design effect. Đây không phải số trong paper.

---

## Danh mục tài liệu tham khảo (đánh số)

**Quy ước:**

- Mã trong ngoặc vuông ([S1.5]…) là mã dùng trong thân bài.
- "theo arXiv comments" nghĩa là venue lấy từ trường Comments/Journal-ref trên arXiv, chưa đối chiếu với proceedings.
- Mọi link đã được truy cập ngày 05–06/10/2026.

### A. Phát hiện greenwashing, NLP về khí hậu và ESG

1. [S1.1] Moodaley, W., & Telukdarie, A. (2023). Greenwashing, Sustainability Reporting, and Artificial Intelligence: A Systematic Literature Review. *Sustainability*, 15(2), 1481. https://doi.org/10.3390/su15021481
2. [S1.2] Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M. (2025; v2 29/01/2026). *Detecting Greenwashing: A Natural Language Processing Literature Survey* (v1: *Corporate Greenwashing Detection in Text – a Survey*). Working paper, arXiv:2502.07541. https://arxiv.org/abs/2502.07541
3. [S1.3] Webersinke, N., Kraus, M., Bingler, J. A., & Leippold, M. (2021). ClimateBert: A Pretrained Language Model for Climate-Related Text. arXiv:2110.12010. https://arxiv.org/abs/2110.12010
4. [S1.3] Yu, Y., Raj, S., Ni, J., Vaghefi, A. S., Stammbach, D., & Leippold, M. (2026). Climate-ModernBERT: Revisiting Corpus Composition for Domain-Adaptive Continued Pretraining. arXiv:2609.07798. https://arxiv.org/abs/2609.07798
5. [S1.4] Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. *Finance Research Letters*, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
6. [S1.4] Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. *Journal of Banking & Finance*, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
7. [S1.5] Stammbach, D., Webersinke, N., Bingler, J. A., Kraus, M., & Leippold, M. (2023). Environmental Claim Detection. *Proceedings of ACL 2023 (Volume 2: Short Papers)*, 1051–1066. https://doi.org/10.18653/v1/2023.acl-short.91
8. [S1.5] European Commission (2009). *Commission Staff Working Document — Guidance on the implementation/application of Directive 2005/29/EC on Unfair Commercial Practices*, SEC(2009) 1666. Trích gián tiếp qua [7]; chưa đối chiếu văn bản gốc [UNVERIFIED].
9. [S1.6] Schimanski, T., Bingler, J., Hyslop, C., Kraus, M., & Leippold, M. (2023). ClimateBERT-NetZero: Detecting and Assessing Net Zero and Reduction Targets. *Proceedings of EMNLP 2023*, 15745–15756. https://doi.org/10.18653/v1/2023.emnlp-main.975
10. [S1.7] Ni, J., Bingler, J., Colesanti-Senni, C., Kraus, M., Gostlow, G., Schimanski, T., Stammbach, D., Vaghefi, S. A., Wang, Q., Webersinke, N., Wekhof, T., Yu, T., & Leippold, M. (2023). CHATREPORT: Democratizing Sustainability Disclosure Analysis through LLM-based Tools. *Proceedings of EMNLP 2023: System Demonstrations*, 21–51. https://doi.org/10.18653/v1/2023.emnlp-demo.3
11. [S1.8] Leippold, M., Vaghefi, S. A., Stammbach, D., Muccione, V., Bingler, J., Ni, J., Colesanti Senni, C., Wekhof, T., Schimanski, T., Gostlow, G., Yu, T., Luterbacher, J., & Huggel, C. (2025). Automated fact-checking of climate claims with large language models. *npj Climate Action*, 4, 17. https://doi.org/10.1038/s44168-025-00215-8 (preprint arXiv:2401.12566)
12. [S1.9] Schimanski, T., Ni, J., Spacey Martín, R., Ranger, N., & Leippold, M. (2024). ClimRetrieve: A Benchmarking Dataset for Information Retrieval from Corporate Climate Disclosures. *Proceedings of EMNLP 2024*, 17509–17524. https://doi.org/10.18653/v1/2024.emnlp-main.969
13. [S1.10] Ong, K., Mao, R., Varshney, D., Cambria, E., & Mengaldo, G. (2025). Towards Robust ESG Analysis Against Greenwashing Risks: Aspect-Action Analysis with Cross-Category Generalization. *Proceedings of ACL 2025 (Volume 1: Long Papers)*, 14854–14879. https://doi.org/10.18653/v1/2025.acl-long.723
14. [S1.10] Braun, N. H., Ong, K., Mao, R., Cambria, E., & Mengaldo, G. (2026). Enhancing Language Models for Robust Greenwashing Detection. arXiv:2601.21722. https://arxiv.org/abs/2601.21722
15. [S1.11] Kaoukis, G., Koufopoulos, I.-A., Psaroudaki, E., Pla Karidi, D., Pitoura, E., Papastefanatos, G., & Tsaparas, P. (2026). EmeraldMind: A Knowledge Graph–Augmented Framework for Greenwashing Detection. *Proceedings of the ACM Web Conference 2026*, 9645–9655. https://doi.org/10.1145/3774904.3792997 (arXiv:2512.11506)
16. [S1.12] Xu, C., Liu, J., Li, Z., & Lin, C. (2026). DeepGreen: Effective LLM-Driven Greenwashing Monitoring System Designed for Empirical Testing — Evidence from China. *Computational Economics* (online 19/02/2026). https://doi.org/10.1007/s10614-026-11328-5 (arXiv:2504.07733)
17. [S1.13] Chuang, M., Chuang, G., Chuang, C., & Chuang, J. (2025). Judging It, Washing It: Scoring and Greenwashing Corporate Climate Disclosures using Large Language Models. ClimateNLP 2025 (theo arXiv comments); arXiv:2502.15094. https://arxiv.org/abs/2502.15094
18. [S1.14] Vinella, A., Capetz, M., Pattichis, R., Chance, C., Ghosh, R., & Chang, K.-W. (2023). Leveraging Language Models to Detect Greenwashing. arXiv:2311.01469. https://arxiv.org/abs/2311.01469
19. [S1.15] Schimanski, T., Ni, J., Kraus, M., Ash, E., & Leippold, M. (2024). Towards Faithful and Robust LLM Specialists for Evidence-Based Question-Answering. *Proceedings of ACL 2024 (Volume 1: Long Papers)*, 1913–1931. https://aclanthology.org/2024.acl-long.105/
20. [S1.15] Ni, J., Schimanski, T., Lin, M., Sachan, M., Ash, E., & Leippold, M. (2025). DIRAS: Efficient LLM Annotation of Document Relevance in Retrieval Augmented Generation. NAACL 2025 Long (theo arXiv comments); arXiv:2406.14162. https://arxiv.org/abs/2406.14162
21. [S1.15] He, C., Zhou, X., Wu, Y., Yu, X., Zhang, Y., Zhang, L., Wang, D., Lyu, S., Xu, H., Wang Xiaoqiao, Liu, W., & Miao, C. (2025). ESGenius: Benchmarking LLMs on Environmental, Social, and Governance (ESG) and Sustainability Knowledge. *Proceedings of EMNLP 2025*, 14612–14653. https://doi.org/10.18653/v1/2025.emnlp-main.739
22. [S1.16] Schimanski, T., Reding, A., Reding, N., Bingler, J., Kraus, M., & Leippold, M. (2024). Bridging the gap in ESG measurement: Using NLP to quantify environmental, social, and governance communication. *Finance Research Letters*, 61, 104979. https://doi.org/10.1016/j.frl.2024.104979
23. [S1.17] Huang, A. H., Wang, H., & Yang, Y. (2023; online 2022). FinBERT: A Large Language Model for Extracting Information from Financial Text. *Contemporary Accounting Research*. https://doi.org/10.1111/1911-3846.12832

### B. Xác minh claim, suy luận số/bảng, RAG

24. [S2.1] Thorne, J., Vlachos, A., Christodoulopoulos, C., & Mittal, A. (2018). FEVER: a Large-scale Dataset for Fact Extraction and VERification. *Proceedings of NAACL-HLT 2018*, 809–819. https://doi.org/10.18653/v1/N18-1074
25. [S2.2] Wadden, D., Lin, S., Lo, K., Wang, L. L., van Zuylen, M., Cohan, A., & Hajishirzi, H. (2020). Fact or Fiction: Verifying Scientific Claims. *Proceedings of EMNLP 2020*, 7534–7550. https://doi.org/10.18653/v1/2020.emnlp-main.609
26. [S2.3] Schlichtkrull, M., Guo, Z., & Vlachos, A. (2023). AVeriTeC: A Dataset for Real-world Claim Verification with Evidence from the Web. NeurIPS 2023 Datasets & Benchmarks Track; arXiv:2305.13117. https://arxiv.org/abs/2305.13117
27. [S2.3] Schlichtkrull, M., Chen, Y., Whitehouse, C., Deng, Z., Akhtar, M., Aly, R., Guo, Z., Christodoulopoulos, C., Cocarascu, O., Mittal, A., Thorne, J., & Vlachos, A. (2024). The Automated Verification of Textual Claims (AVeriTeC) Shared Task. *Proceedings of the Seventh Fact Extraction and VERification Workshop (FEVER)*, 1–26. https://doi.org/10.18653/v1/2024.fever-1.1
28. [S2.3] Rothermel, M., Braun, T., Rohrbach, M., & Rohrbach, A. (2024). InFact: A Strong Baseline for Automated Fact-Checking. *Proceedings of the Seventh FEVER Workshop*, 108–112. https://aclanthology.org/2024.fever-1.12/
29. [S2.3] Akhtar, M., Aly, R., Chen, Y., Deng, Z., Schlichtkrull, M., Whitehouse, C., & Vlachos, A. (2025). The 2nd Automated Verification of Textual Claims (AVeriTeC) Shared Task: Open-weights, Reproducible and Efficient Systems. *Proceedings of the Eighth FEVER Workshop*, 201–223. https://doi.org/10.18653/v1/2025.fever-1.15
30. [S2.4] Diggelmann, T., Boyd-Graber, J., Bulian, J., Ciaramita, M., & Leippold, M. (2020). CLIMATE-FEVER: A Dataset for Verification of Real-World Climate Claims. Tackling Climate Change with Machine Learning Workshop @ NeurIPS 2020; arXiv:2012.00614. https://arxiv.org/abs/2012.00614
31. [S2.5] Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. *Proceedings of EMNLP 2023*, 12076–12100. https://doi.org/10.18653/v1/2023.emnlp-main.741
32. [S2.5] Kamoi, R., Goyal, T., Rodriguez, J. D., & Durrett, G. (2023). WiCE: Real-World Entailment for Claims in Wikipedia. *Proceedings of EMNLP 2023*, 7561–7583. https://aclanthology.org/2023.emnlp-main.470/
33. [S2.5] Wanner, M., Ebner, S., Jiang, Z., Dredze, M., & Van Durme, B. (2024). A Closer Look at Claim Decomposition. *Proceedings of *SEM 2024*, 153–175. https://doi.org/10.18653/v1/2024.starsem-1.13
34. [S2.5] Hu, Q., Long, Q., & Wang, W. (2025). Decomposition Dilemmas: Does Claim Decomposition Boost or Burden Fact-Checking Performance? NAACL 2025 Main (theo arXiv comments); arXiv:2411.02400. https://arxiv.org/abs/2411.02400
35. [S2.6] Venktesh V, Anand, A., Anand, A., & Setty, V. (2024). QuanTemp: A real-world open-domain benchmark for fact-checking numerical claims. SIGIR 2024 (theo arXiv comments); arXiv:2403.17169. https://arxiv.org/abs/2403.17169
36. [S2.7] Aarnes, P. R., & Setty, V. (2025). NumPert: Numerical Perturbations to Probe Language Models for Veracity Prediction. IJCNLP-AACL 2025 Student Research Workshop (theo arXiv comments); arXiv:2511.09971. https://arxiv.org/abs/2511.09971
37. [S2.8] Aarnes, P. R., & Setty, V. (2026). Towards Robust Numerical Claim Verification. Accepted to AACL-IJCNLP 2026 Findings (theo arXiv comments); arXiv:2610.00689. https://arxiv.org/abs/2610.00689
38. [S2.9] Schuster, T., Fisch, A., & Barzilay, R. (2021). Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence. *Proceedings of NAACL-HLT 2021*, 624–643. https://aclanthology.org/2021.naacl-main.52/
39. [S2.10] Chen, W., Wang, H., Chen, J., Zhang, Y., Wang, H., Li, S., Zhou, X., & Wang, W. Y. (2020). TabFact: A Large-scale Dataset for Table-based Fact Verification. ICLR 2020 (theo arXiv comments); arXiv:1909.02164. https://arxiv.org/abs/1909.02164
40. [S2.11] Aly, R., Guo, Z., Schlichtkrull, M., Thorne, J., Vlachos, A., Christodoulopoulos, C., Cocarascu, O., & Mittal, A. (2021). FEVEROUS: Fact Extraction and VERification Over Unstructured and Structured information. NeurIPS 2021 Datasets & Benchmarks (theo arXiv comments); arXiv:2106.05707. https://arxiv.org/abs/2106.05707
41. [S2.12] Chen, Z., Chen, W., Smiley, C., Shah, S., Borova, I., Langdon, D., Moussa, R., Beane, M., Huang, T.-H., Routledge, B., & Wang, W. Y. (2021). FinQA: A Dataset of Numerical Reasoning over Financial Data. *Proceedings of EMNLP 2021*, 3697–3711. https://doi.org/10.18653/v1/2021.emnlp-main.300
42. [S2.13] Zhu, F., Lei, W., Huang, Y., Wang, C., Zhang, S., Lv, J., Feng, F., & Chua, T.-S. (2021). TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content in Finance. *Proceedings of ACL-IJCNLP 2021 (Volume 1: Long Papers)*, 3277–3287. https://doi.org/10.18653/v1/2021.acl-long.254
43. [S2.14] Zhao, Y., Long, Y., Jiang, Y., Wang, C., Chen, W., Liu, H., Zhang, Y., Tang, X., Zhao, C., & Cohan, A. (2024). FinDVer: Explainable Claim Verification over Long and Hybrid-Content Financial Documents. *Proceedings of EMNLP 2024*, 14739–14752. https://doi.org/10.18653/v1/2024.emnlp-main.818
    - Tên tác giả thứ 3: PDF ghi "Yuru Jiang", metadata ACL Anthology ghi "Tintin Jiang".
    - Thứ tự tác giả 7–8 cũng khác nhau giữa hai nguồn.
44. [S2.15] Islam, P., Kannappan, A., Kiela, D., Qian, R., Scherrer, N., & Vidgen, B. (2023). FinanceBench: A New Benchmark for Financial Question Answering. arXiv:2311.11944. https://arxiv.org/abs/2311.11944
45. [S2.16] Zhao, Y., Long, Y., Liu, H., Kamoi, R., Nan, L., Chen, L., Liu, Y., Tang, X., Zhang, R., & Cohan, A. (2024). DocMath-Eval: Evaluating Math Reasoning Capabilities of LLMs in Understanding Long and Specialized Documents. *Proceedings of ACL 2024 (Volume 1: Long Papers)*, 16103–16120. https://doi.org/10.18653/v1/2024.acl-long.852
46. [S2.17] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. *Transactions of the ACL*, 12, 157–173. https://doi.org/10.1162/tacl_a_00638
47. [S2.5b] Zhao, S., Shao, Y., Huang, Y., Song, J., Wang, Z., Wan, C., & Ma, L. (2024; v3 29/05/2026). *Understanding the Fundamental Design Decisions of Retrieval-Augmented Generation Systems* (v1: *Towards Understanding Retrieval Accuracy and Prompt Quality in RAG Systems*). ACM TOSEM 2026 (theo arXiv journal-ref); arXiv:2411.19463. https://arxiv.org/abs/2411.19463
48. [S2.18] Barnett, S., Kurniawan, S., Thudumu, S., Brannelly, Z., & Abdelrazek, M. (2024). Seven Failure Points When Engineering a Retrieval Augmented Generation System. arXiv:2401.05856. https://arxiv.org/abs/2401.05856
49. [S2.19] Joren, H., Zhang, J., Ferng, C.-S., Juan, D.-C., Taly, A., & Rashtchian, C. (2025). Sufficient Context: A New Lens on Retrieval Augmented Generation Systems. ICLR 2025; arXiv:2411.06037. https://arxiv.org/abs/2411.06037

### C. Kiểu lỗi của LLM, LLM-as-judge, abstention, phối hợp người–AI

50. [S3.1] Liu, N. F., Zhang, T., & Liang, P. (2023). Evaluating Verifiability in Generative Search Engines. Findings of EMNLP 2023 (theo arXiv comments); arXiv:2304.09848. https://arxiv.org/abs/2304.09848
51. [S3.2] Gao, T., Yen, H., Yu, J., & Chen, D. (2023). Enabling Large Language Models to Generate Text with Citations. *Proceedings of EMNLP 2023*, 6465–6488. https://aclanthology.org/2023.emnlp-main.398/
52. [S3.3] Niu, C., Wu, Y., Zhu, J., Xu, S., Shum, K., Zhong, R., Song, J., & Zhang, T. (2024). RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models. *Proceedings of ACL 2024 (Volume 1: Long Papers)*, 10862–10878. https://aclanthology.org/2024.acl-long.585/
53. [S3.4] Tang, L., Laban, P., & Durrett, G. (2024). MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents. EMNLP 2024 (theo arXiv comments); arXiv:2404.10774. https://arxiv.org/abs/2404.10774
    - Leaderboard LLM-AggreFact: https://llm-aggrefact.github.io/ (truy cập 05/10/2026).
54. [S3.5] Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. ICLR 2024 (theo arXiv comments); arXiv:2306.13063. https://arxiv.org/abs/2306.13063
55. [S3.6] Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., et al. (36 tác giả) (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221. https://arxiv.org/abs/2207.05221
56. [S3.7] Kamath, A., Jia, R., & Liang, P. (2020). Selective Question Answering under Domain Shift. *Proceedings of ACL 2020*, 5684–5696. https://doi.org/10.18653/v1/2020.acl-main.503
57. [S3.8] Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Kong, L., Liu, Q., Liu, T., & Sui, Z. (2024). Large Language Models are not Fair Evaluators. *Proceedings of ACL 2024 (Volume 1: Long Papers)*, 9440–9450. https://aclanthology.org/2024.acl-long.511/
58. [S3.9] Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets & Benchmarks (theo arXiv comments); arXiv:2306.05685. https://arxiv.org/abs/2306.05685
59. [S3.10] Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2025). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. AACL-IJCNLP 2025 (theo arXiv comments); arXiv:2406.07791. https://arxiv.org/abs/2406.07791
60. [S3.11] Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., Gatt, A., Ghaleb, E., Giulianelli, M., Hanna, M., Koller, A., Martins, A. F. T., Mondorf, P., Neplenbroek, V., Pezzelle, S., Plank, B., Schlangen, D., Suglia, A., Surikuchi, A. K., Takmaz, E., & Testoni, A. (2025). LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks. ACL 2025 main (theo arXiv comments); arXiv:2406.18403. https://arxiv.org/abs/2406.18403
61. [S3.12] Panickssery, A., Bowman, S. R., & Feng, S. (2024). LLM Evaluators Recognize and Favor Their Own Generations. arXiv:2404.13076. https://arxiv.org/abs/2404.13076
62. [S3.13] Wen, B., Yao, J., Feng, S., Xu, C., Tsvetkov, Y., Howe, B., & Wang, L. L. (2024/2025). Know Your Limits: A Survey of Abstention in Large Language Models. TACL (theo arXiv comments); arXiv:2407.18418. https://arxiv.org/abs/2407.18418
63. [S3.14] Geifman, Y., & El-Yaniv, R. (2017). Selective Classification for Deep Neural Networks. arXiv:1705.08500. https://arxiv.org/abs/1705.08500
    - Venue NeurIPS (NIPS) 2017 theo hiểu biết chung, chưa đối chiếu trực tiếp [UNVERIFIED venue].
64. [S3.15] Mohri, C., & Hashimoto, T. (2024). Language Models with Conformal Factuality Guarantees. *Proceedings of ICML 2024*, PMLR 235, 36029–36047. https://proceedings.mlr.press/v235/mohri24a.html
65. [S3.16] Warren, G., Shklovski, I., & Augenstein, I. (2025). Show Me the Work: Fact-Checkers' Requirements for Explainable Automated Fact-Checking. *CHI '25: Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*, 1–21. arXiv:2502.09083. https://arxiv.org/abs/2502.09083
66. [S3.17] Warren, G., Sun, J., Shklovski, I., & Augenstein, I. (2026). Show me the evidence: Evaluating the role of evidence and natural language explanations in AI-supported fact-checking. arXiv:2601.11387. https://arxiv.org/abs/2601.11387
67. [S3.18] Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. S. (2021). Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance. CHI 2021 (theo arXiv comments); arXiv:2006.14779. https://arxiv.org/abs/2006.14779
68. [S3.19] Vasconcelos, H., Jörke, M., Grunde-McLaughlin, M., Gerstenberg, T., Bernstein, M., & Krishna, R. (2023). Explanations Can Reduce Overreliance on AI Systems During Decision-Making. CSCW 2023 (theo arXiv comments); arXiv:2212.06823. https://arxiv.org/abs/2212.06823
69. [S3.20] Commerford, B. P., Dennis, S. A., Joe, J. R., & Ulla, J. W. (2022). Man Versus Machine: Complex Estimates and Auditor Reliance on Artificial Intelligence. *Journal of Accounting Research*, 60(1), 171–201. https://doi.org/10.1111/1475-679X.12407
70. [S3.21] Guo, Z., Schlichtkrull, M., & Vlachos, A. (2022). A Survey on Automated Fact-Checking. *Transactions of the ACL*, 10, 178–206. https://doi.org/10.1162/tacl_a_00454

### D. Tài nguyên NLP tiếng Việt và đa ngôn ngữ

71. [S4.1] Pham, L., Luu, T., Vo, T., Nguyen, M., & Hoang, V. (2025). VN-MTEB: Vietnamese Massive Text Embedding Benchmark. arXiv:2507.21500. https://arxiv.org/abs/2507.21500
72. [S4.1] Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2022). MTEB: Massive Text Embedding Benchmark. arXiv:2210.07316. https://arxiv.org/abs/2210.07316 (bộ gốc mà VN-MTEB dịch)
73. [S4.2] Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. arXiv:2402.03216. https://arxiv.org/abs/2402.03216 (mô hình BAAI/bge-m3)
74. [S4.2] Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Multilingual E5 Text Embeddings: A Technical Report. arXiv:2402.05672. https://arxiv.org/abs/2402.05672 (theo trích dẫn trên model card intfloat/multilingual-e5-large-instruct)
75. [S4.2] Zhang, X., Zhang, Y., Long, D., Xie, W., Dai, Z., Tang, J., Lin, H., Yang, B., Xie, P., Huang, F., Zhang, M., Li, W., & Zhang, M. (2024). mGTE: Generalized Long-Context Text Representation and Reranking Models for Multilingual Text Retrieval. EMNLP 2024 Industry Track (theo arXiv comments); arXiv:2407.19669. https://arxiv.org/abs/2407.19669 (mô hình Alibaba-NLP/gte-multilingual-base)
76. [S4.2] Zhang, Y., Li, M., Long, D., et al. (2025). Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models. arXiv:2506.05176. https://arxiv.org/abs/2506.05176
    - Tên và tác giả lấy từ trích dẫn trên model card Qwen/Qwen3-Embedding-0.6B; chưa mở trang arXiv.
77. [S4.3] Nguyen, P.-V., Tran, M.-N., Nguyen, L., & Dinh, D. (2025). Advancing Vietnamese Information Retrieval with Learning Objective and Benchmark. PACLIC 38 (2024) (theo arXiv journal-ref); arXiv:2503.07470. https://arxiv.org/abs/2503.07470
78. [S4.2] Dang, P.-N., Nguyen, K.-L., & Pham, T.-H. (2025). ViRanker: A BGE-M3 & Blockwise Parallel Transformer Cross-Encoder for Vietnamese Reranking. arXiv:2509.09131. https://arxiv.org/abs/2509.09131
79. [S4.4] Huynh, T. V., Nguyen, K. V., & Nguyen, N. L.-T. (2022). ViNLI: A Vietnamese Corpus for Studies on Open-Domain Natural Language Inference. *Proceedings of COLING 2022*, 3858–3872. https://aclanthology.org/2022.coling-1.339/
80. [S4.5] Huynh, T. V., Nguyen, K. V., & Nguyen, N. L.-T. (2024/2025). A New Benchmark Dataset and Mixture-of-Experts Language Models for Adversarial Natural Language Inference in Vietnamese. Expert Systems with Applications (accepted, theo arXiv comments); arXiv:2406.17716. https://arxiv.org/abs/2406.17716
81. [S4.6] Conneau, A., Lample, G., Rinott, R., Williams, A., Bowman, S. R., Schwenk, H., & Stoyanov, V. (2018). XNLI: Evaluating Cross-lingual Sentence Representations. EMNLP 2018 (theo arXiv comments); arXiv:1809.05053. https://arxiv.org/abs/1809.05053
82. [S4.8] Hoa, T. T., Duy, T. Q., Tran, K. Q., & Nguyen, K. V. (2025). ViFactCheck: A New Benchmark Dataset and Methods for Multi-domain News Fact-Checking in Vietnamese. *Proceedings of AAAI 2025*, 308–316. https://ojs.aaai.org/index.php/AAAI/article/view/32008 (arXiv:2412.15308)
    - Số trang lấy từ kết quả tìm kiếm trang AAAI, chưa mở PDF proceedings.
83. [S4.9] Le, H. T., To, L. T., Nguyen, M. T., & Nguyen, K. V. (2024). ViWikiFC: Fact-Checking for Vietnamese Wikipedia-Based Textual Knowledge Source. arXiv:2405.07615. https://arxiv.org/abs/2405.07615
84. [S4.9] Tran, D. X., Nguyen, N. V., Tran, T. T., Hoang, A. T., Duong, T. V., Le, D. T., & Le, P.-L. (2026). SemViQA: A Semantic Question Answering System for Vietnamese Information Fact-Checking. ACL 2026 Industry Track. https://aclanthology.org/2026.acl-industry.94/ (arXiv:2503.00955)
85. [S4.9] To, L. T., Le, H. T., Nguyen, D. V.-T., Nguyen, M. T., Nguyen, T. T., Huynh, T. V., & Nguyen, K. V. (2024). Evaluating Large Language Model Capability in Vietnamese Fact-Checking Data Generation. arXiv:2411.05641. https://arxiv.org/abs/2411.05641
86. [S4.10] Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. *Findings of EMNLP 2020*, 1037–1042. https://doi.org/10.18653/v1/2020.findings-emnlp.92
87. [S4.11] Tran, C. D., Pham, N. H., Nguyen, A. T., Hy, T. S., & Vu, T. (2023). ViDeBERTa: A powerful pre-trained language model for Vietnamese. *Findings of EACL 2023*, 1071–1078. https://doi.org/10.18653/v1/2023.findings-eacl.79
88. [§4.6] Le, A., Lam, T., & Nguyen, D. (2025). A Survey on Vietnamese Document Analysis and Recognition: Challenges and Future Directions. arXiv:2506.05061. https://arxiv.org/abs/2506.05061
89. [§4.6] Cui, C., Sun, T., Liang, S., Gao, T., Zhang, Z., et al. (18 tác giả) (2025). PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model. arXiv:2510.14528. https://arxiv.org/abs/2510.14528
90. [§4.6] Doan, K. T., Huynh, B. G., Hoang, D. T., Pham, T. D., Pham, N. H., Nguyen, Q. T. M., Vo, B. Q., & Hoang, S. N. (2024). Vintern-1B: An Efficient Multimodal Large Language Model for Vietnamese. arXiv:2408.12480. https://arxiv.org/abs/2408.12480
91. [§5.2] Nguyen, Q. H., Trinh, P. A., Mai, P. Q. H., & Trinh, T. P. (2025). FinStat2SQL: A Text2SQL Pipeline for Financial Statement Analysis. *Proceedings of INLG 2025*. https://aclanthology.org/2025.inlg-main.27/

### E. Trích xuất KPI/ESG và hiểu tài liệu PDF

92. [S5.1] Zou, Y., Shi, M., Chen, Z., Deng, Z., Lei, Z., Zeng, Z., Yang, S., Tong, H., Xiao, L., & Zhou, W. (2023). ESGReveal: An LLM-based approach for extracting structured data from ESG reports. arXiv:2312.17264. https://arxiv.org/abs/2312.17264
93. [S5.2] Bronzini, M., Nicolini, C., Lepri, B., Passerini, A., & Staiano, J. (2024). Glitter or Gold? Deriving Structured Insights from Sustainability Reports via Large Language Models. *EPJ Data Science*, 13, 41. https://doi.org/10.1140/epjds/s13688-024-00481-2 (arXiv:2310.05628)
94. [S5.3] Beck, J., Steinberg, A., Dimmelmeier, A., Domenech Burin, L., Kormanyos, E., Fehr, M., & Schierholz, M. (2025). Addressing data gaps in sustainability reporting: A benchmark dataset for greenhouse gas emission extraction. *Scientific Data*. https://doi.org/10.1038/s41597-025-05664-8
95. [S5.4] Wilhelmi, L., Bruns, C., & Schumann, M. (2026). Enhancing the Extraction of GHG Emission-Reduction Targets from Sustainability Reports Using Vision Language Models. *Machine Learning and Knowledge Extraction*, 8(2), 37. https://doi.org/10.3390/make8020037
96. [S5.5] Zheng, S., Duan, Y., Xue, C., & Salim, F. D. (2026). Scope3Trace: Evidence-Based Identification and Extraction of Scope 3 GHG Emissions from Sustainability Reports. arXiv:2607.17122. https://arxiv.org/abs/2607.17122
97. [S5.6] Schmoll, J., & Jatowt, A. (2025). Automated Analysis of Sustainability Reports: Using Large Language Models for the Extraction and Prediction of EU Taxonomy-Compliant KPIs. arXiv:2512.24289. https://arxiv.org/abs/2512.24289
98. [S5.7] Ali, M., Abdallah, A., & Jatowt, A. (2025/2026). SustainableQA: A Comprehensive Question Answering Dataset for Corporate Sustainability and EU Taxonomy Reporting. EMNLP 2026 Main (theo arXiv comments); arXiv:2508.03000. https://arxiv.org/abs/2508.03000
99. [S5.8] Gupta, T., Goel, T., & Verma, I. (2025). Exploring Multimodal Language Models for Sustainability Disclosure Extraction: A Comparative Study. *Proceedings of the Sixth Workshop on Insights from Negative Results in NLP*, 141–149. https://aclanthology.org/2025.insights-1.13/
100. [S5.9] Dave, A., Zhu, M., Hu, D., & Tiwari, S. (2024). Climate AI for Corporate Decarbonization Metrics Extraction. arXiv:2411.03402. https://arxiv.org/abs/2411.03402
101. [§5.2] Auer, C., Lysak, M., Nassar, A., Dolfi, M., Livathinos, N., et al. (19 tác giả) (2024). Docling Technical Report. arXiv:2408.09869. https://arxiv.org/abs/2408.09869
102. [§5.2] Nassar, A., Livathinos, N., Lysak, M., & Staar, P. (2022). TableFormer: Table Structure Understanding with Transformers. arXiv:2203.01017. https://arxiv.org/abs/2203.01017
    - Venue CVPR 2022 theo hiểu biết chung; trang arXiv không ghi [UNVERIFIED venue].
103. [§5.2] Smock, B., Pesala, R., & Abraham, R. (2022). PubTables-1M: Towards comprehensive table extraction from unstructured documents. arXiv:2110.00061. https://arxiv.org/abs/2110.00061
    - Venue CVPR 2022 theo hiểu biết chung [UNVERIFIED venue].
104. [§5.2] Adhikari, N. S., & Agarwal, S. (2024). A Comparative Study of PDF Parsing Tools Across Diverse Document Categories. arXiv:2410.09871. https://arxiv.org/abs/2410.09871
105. [§5.2] Ouyang, L., Qu, Y., Zhou, H., Zhu, J., Zhang, R., Lin, Q., Wang, B., Zhao, Z., Jiang, M., Zhao, X., Shi, J., Wu, F., Chu, P., Liu, M., Li, Z., Xu, C., Zhang, B., Shi, B., Tu, Z., & He, C. (2025). OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations. CVPR 2025 (theo arXiv comments); arXiv:2412.07626. https://arxiv.org/abs/2412.07626
106. [§5.2] Poznanski, J., Rangapur, A., Borchardt, J., Dunkelberger, J., Huff, R., Lin, D., Wilhelm, C., Lo, K., & Soldaini, L. (2025). olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models. arXiv:2502.18443. https://arxiv.org/abs/2502.18443

### F. Phương pháp đánh giá và thống kê

107. [§6.1] Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020). With Little Power Comes Great Responsibility. *Proceedings of EMNLP 2020*, 9263–9274. https://doi.org/10.18653/v1/2020.emnlp-main.745
108. [§6.1] Miller, E. (2024). Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations. arXiv:2411.00640. https://arxiv.org/abs/2411.00640
109. [§6.1] Dror, R., Baumer, G., Shlomov, S., & Reichart, R. (2018). The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing. *Proceedings of ACL 2018*, 1383–1392. https://doi.org/10.18653/v1/P18-1128
110. [§6.1] Berg-Kirkpatrick, T., Burkett, D., & Klein, D. (2012). An Empirical Investigation of Statistical Significance in NLP. *Proceedings of EMNLP-CoNLL 2012*, 995–1005. https://aclanthology.org/D12-1091/
111. [§6.1] Koehn, P. (2004). Statistical Significance Tests for Machine Translation Evaluation. *Proceedings of EMNLP 2004*, 388–395. https://aclanthology.org/W04-3250/
112. [§6.1] Wilson, E. B. (1927). Probable Inference, the Law of Succession, and Statistical Inference. *Journal of the American Statistical Association*, 22(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
113. [§6.1] Agresti, A., & Coull, B. A. (1998). Approximate Is Better than "Exact" for Interval Estimation of Binomial Proportions. *The American Statistician*, 52(2), 119–126. https://doi.org/10.2307/2685469
    - Crossref xác nhận trang bắt đầu 119; trang cuối 126 theo trích dẫn thông dụng.
114. [Phụ lục] Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales. *Educational and Psychological Measurement*, 20(1), 37–46. https://doi.org/10.1177/001316446002000104
115. [§6.2] Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174. https://doi.org/10.2307/2529310
116. [§6.2] McHugh, M. L. (2012). Interrater reliability: the kappa statistic. *Biochemia Medica*, 22(3), 276–282. https://doi.org/10.11613/BM.2012.031
117. [§6.2] Artstein, R., & Poesio, M. (2008). Inter-Coder Agreement for Computational Linguistics. *Computational Linguistics*, 34(4), 555–596. https://doi.org/10.1162/coli.07-034-R2
118. [§6.2] Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. *Journal of Clinical Epidemiology*, 43(6), 543–549. https://doi.org/10.1016/0895-4356(90)90158-L
119. [§6.2] Sim, J., & Wright, C. C. (2005). The kappa statistic in reliability studies: use, interpretation, and sample size requirements. *Physical Therapy*, 85(3), 257–268. https://doi.org/10.1093/ptj/85.3.257
120. [§6.2] Randolph, J. J. (2005). *Free-Marginal Multirater Kappa (multirater κ_free): An Alternative to Fleiss' Fixed-Marginal Multirater Kappa.* [UNVERIFIED]
    - Chỉ trích gián tiếp qua AVeriTeC [26]; tên, venue và link chưa đối chiếu được bản gốc.
121. [§6.3] Gorman, K., & Bedrick, S. (2019). We Need to Talk about Standard Splits. *Proceedings of ACL 2019*, 2786–2791. https://doi.org/10.18653/v1/P19-1267
122. [§6.3] Søgaard, A., Ebert, S., Bastings, J., & Filippova, K. (2021). We Need To Talk About Random Splits. *Proceedings of EACL 2021*, 1823–1832. https://doi.org/10.18653/v1/2021.eacl-main.156
123. [§6.3] Lewis, P., Stenetorp, P., & Riedel, S. (2021). Question and Answer Test-Train Overlap in Open-Domain Question Answering Datasets. *Proceedings of EACL 2021*, 1000–1008. https://doi.org/10.18653/v1/2021.eacl-main.86
124. [§6.3] Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*. https://doi.org/10.1016/j.patter.2023.100804
125. [§6.4] Zobel, J. (1998). How reliable are the results of large-scale information retrieval experiments? *Proceedings of ACM SIGIR 1998*. https://doi.org/10.1145/290941.291014
126. [§6.4] Buckley, C., & Voorhees, E. M. (2004). Retrieval evaluation with incomplete information. *Proceedings of ACM SIGIR 2004*. https://doi.org/10.1145/1008992.1009000
127. [§6.4] Buckley, C., Dimmick, D., Soboroff, I., & Voorhees, E. (2007). Bias and the limits of pooling for large collections. *Information Retrieval*, 10(6). https://doi.org/10.1007/s10791-007-9032-x
128. [§6.4] Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., & Gurevych, I. (2021). BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models. NeurIPS 2021 Datasets & Benchmarks (theo arXiv comments); arXiv:2104.08663. https://arxiv.org/abs/2104.08663
129. [§6.4] Arabzadeh, N., Vtyurina, A., Yan, X., & Clarke, C. L. A. (2022; arXiv 2021). Shallow pooling for sparse labels. *Information Retrieval Journal*. https://doi.org/10.1007/s10791-022-09411-0

### G. Dataset card, model card và repo phần mềm được trích (licence, kích thước, số tự báo)

**Dataset trên Hugging Face:**

- climatebert/environmental_claims: https://huggingface.co/datasets/climatebert/environmental_claims
- climatebert/netzero_reduction_data: https://huggingface.co/datasets/climatebert/netzero_reduction_data
- climatebert/climate_specificity: https://huggingface.co/datasets/climatebert/climate_specificity
- climatebert/climate_commitments_actions: https://huggingface.co/datasets/climatebert/climate_commitments_actions
- fever/fever: https://huggingface.co/datasets/fever/fever
- tals/vitaminc: https://huggingface.co/datasets/tals/vitaminc
- tdiggelm/climate_fever: https://huggingface.co/datasets/tdiggelm/climate_fever
- facebook/xnli: https://huggingface.co/datasets/facebook/xnli
- uitnlp/ViANLI: https://huggingface.co/datasets/uitnlp/ViANLI
- tranthaihoa/vifactcheck: https://huggingface.co/datasets/tranthaihoa/vifactcheck

**Repo GitHub (licence/dữ liệu):**

- SciFact: https://github.com/allenai/scifact
- AVeriTeC: https://github.com/MichSchli/AVeriTeC
- QuanTemp: https://github.com/factiverse/QuanTemp
- FinDVer: https://github.com/yilunzhao/FinDVer
- ViFactCheck: https://github.com/TTHHA/ViFactCheck
- A3CG: https://github.com/keanepotato/a3cg_greenwash
- PhoBERT: https://github.com/VinAIResearch/PhoBERT
- XNLI: https://github.com/facebookresearch/XNLI
- VietOCR: https://github.com/pbcquoc/vietocr
- Tesseract tessdata_best: https://github.com/tesseract-ocr/tessdata_best
- Tesseract langdata issue #66: https://github.com/tesseract-ocr/langdata/issues/66
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR

**Model card trên Hugging Face:**

- ClimateBERT: climatebert/environmental-claims (https://huggingface.co/climatebert/environmental-claims); climatebert/netzero-reduction (https://huggingface.co/climatebert/netzero-reduction)
- ESG encoder:
  - ESGBERT/EnvironmentalBERT-environmental: https://huggingface.co/ESGBERT/EnvironmentalBERT-environmental
  - yiyanghkust/finbert-esg: https://huggingface.co/yiyanghkust/finbert-esg
  - nbroad/ESG-BERT: https://huggingface.co/nbroad/ESG-BERT
- Kiểm grounding/hallucination:
  - lytang/MiniCheck-Flan-T5-Large: https://huggingface.co/lytang/MiniCheck-Flan-T5-Large
  - lytang/MiniCheck-RoBERTa-Large: https://huggingface.co/lytang/MiniCheck-RoBERTa-Large
  - vectara/hallucination_evaluation_model (HHEM-2.1-Open): https://huggingface.co/vectara/hallucination_evaluation_model
- NLI: MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 (https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)
- Embedding đa ngôn ngữ:
  - BAAI/bge-m3: https://huggingface.co/BAAI/bge-m3
  - intfloat/multilingual-e5-large-instruct: https://huggingface.co/intfloat/multilingual-e5-large-instruct
  - intfloat/multilingual-e5-small: https://huggingface.co/intfloat/multilingual-e5-small
  - Alibaba-NLP/gte-multilingual-base: https://huggingface.co/Alibaba-NLP/gte-multilingual-base
  - Qwen/Qwen3-Embedding-0.6B: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Embedding tiếng Việt:
  - AITeamVN/Vietnamese_Embedding: https://huggingface.co/AITeamVN/Vietnamese_Embedding
  - bkai-foundation-models/vietnamese-bi-encoder: https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder
  - dangvantuan/vietnamese-embedding: https://huggingface.co/dangvantuan/vietnamese-embedding
  - hiieu/halong_embedding: https://huggingface.co/hiieu/halong_embedding
- Reranker:
  - BAAI/bge-reranker-v2-m3: https://huggingface.co/BAAI/bge-reranker-v2-m3
  - AITeamVN/Vietnamese_Reranker: https://huggingface.co/AITeamVN/Vietnamese_Reranker
  - itdainb/PhoRanker: https://huggingface.co/itdainb/PhoRanker
- Encoder tiếng Việt:
  - vinai/phobert-base-v2: https://huggingface.co/vinai/phobert-base-v2
  - Fsoft-AIC/videberta-base: https://huggingface.co/Fsoft-AIC/videberta-base
- Hiểu tài liệu/OCR:
  - PaddlePaddle/PaddleOCR-VL: https://huggingface.co/PaddlePaddle/PaddleOCR-VL
  - 5CD-AI/Vintern-1B-v3_5: https://huggingface.co/5CD-AI/Vintern-1B-v3_5

**Leaderboard:** LLM-AggreFact: https://llm-aggrefact.github.io/

**Ghi chú về các benchmark chỉ được nhắc qua model card** (Zalo AI 2021 Legal Text Retrieval, mMARCO-vi, MS MARCO dịch) và dự án Net Zero Tracker (nguồn dữ liệu của [9]): không có mục riêng trong danh mục. Số liệu liên quan được ghi [self-reported] hoặc trích qua bài gốc.
