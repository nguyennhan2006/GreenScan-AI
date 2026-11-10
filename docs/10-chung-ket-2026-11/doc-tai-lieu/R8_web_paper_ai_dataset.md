# R8: Tra cứu web: paper AI/NLP nền, bộ dữ liệu công khai, LLM tuân thủ quy tắc và bộ nhớ, lý thuyết UX

*Lập 04/11/2026 cho Chung kết 10/11 (10 phút trình bày + 8 phút hỏi đáp). Số của GreenScan lấy từ kết quả 31/10–01/11; không thấy kết quả mới hơn trong `docs/RUNS.md` hay README của AG-1/2/3 tính đến 04/11.*

**Ký hiệu nguồn.**
- **[MỞ]**: trang đã mở trong phiên 04/11.
- **[TQ]**: lấy từ tổng quan nội bộ `docs/08-knowledge/sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md`. Tổng quan này đã đối chiếu với nguồn gốc ngày 05/10; phiên này không mở lại.
- **[TÌM]**: chỉ thấy trong phần tóm tắt kết quả WebSearch, chưa mở trang gốc. Mọi số đi kèm nhãn này coi như **[CHƯA XÁC MINH]**.

**Nguồn đã đọc**
- **Nội bộ:**
  - `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, mục 0–4, 10, 11.
  - `docs/00-project/ARCHITECTURE_INVARIANTS.md`: 10 bất biến và danh sách "không được làm".
  - `docs/08-knowledge/sources/2026-10-05_tong-quan-tai-lieu-AI-NLP.md`: tóm tắt, S1.5, S1.11–12, S2.1, S2.4, S2.12–13, S3.9, S3.14–15, mục 6.2 và 7a–d.
  - `src/quantum_gw/legal/gates.py` (`check_rule`) và `src/quantum_gw/studio/suggest.py` (docstring, `KIND_LABELS`).
  - `scratchpad/txt/GreenScan_100_Cau_BGK.txt`, chỉ lọc theo từ khoá.
  - Grep `docs/` tìm SUS và thử nghiệm người dùng.
- **Web: 35 lượt** (27 lần mở trang, 8 lần tìm).
  - arXiv: 2110.12010, 2012.00483, 2012.00614, 2601.21722, 2005.11401, 2309.15217, 2303.16634, 1706.04599, 2107.07511, 2305.04388, 2311.04235, 2311.07911, 2302.12173, 2310.08560, 2404.13208, 2303.15056, 2510.04618.
  - ACL Anthology: 2023.acl-short.91, 2020.acl-main.386, 2026.nlp4ecology-1.8.
  - Hugging Face: climatebert/environmental_claims, tdiggelm/climate_fever, lumilogic/climateBUG-Data.
  - Khác: nngroup.com (10 heuristic), en.wikipedia.org/wiki/Krippendorff's_alpha, trang Microsoft Research "Guidelines for Human-AI Interaction".
  - Tám lần tìm: ClimateBUG; tẩy xanh bằng LLM 2026; cỡ ClimaText; SUS; bộ dữ liệu fact-check có lời giải thích; Greench; ESG/tẩy xanh tiếng Việt; giấy phép TAT-QA/FinQA.
- **Không đọc được, hoặc cố ý không trích:**
  - Trang Bangor et al. 2009 trên uxpajournal.org trả **404**. Số về SUS vì vậy chỉ có dạng [TÌM].
  - Abstract của ClimaText, CLIMATE-FEVER và Stammbach 2023 **không ghi số**. Số của các bài này lấy từ [TQ], hoặc từ [TÌM] với ClimaText.
  - Không tìm thấy Thorne & Vlachos 2021 (sửa lỗi sự thật), nên không trích.
  - Bài "LLM-based agentic system for greenwashing detection" (IJAIS) ghi ngày xuất bản 12/2026, nhiều khả năng là lỗi metadata, và chưa mở. Không trích.
  - Không tải PDF và không dùng PyMuPDF vì đã hết ngân sách 35 lượt. Thư mục `scratchpad\R8\` không được dùng.

---

## 1. Tóm tắt từng tài liệu

### 1A. NLP về khí hậu, ESG và tẩy xanh

**ClimateBERT.** Webersinke, Kraus, Bingler, Leippold. arXiv 2110.12010 (v1 22/10/2021; v3 17/12/2022; trang không ghi nơi công bố). https://arxiv.org/abs/2110.12010 [MỞ]
- **Phương pháp:** pretrain tiếp trên hơn 2 triệu đoạn văn về khí hậu.
- **Kết quả:** mục tiêu masked LM cải thiện 48%. Tỷ lệ lỗi giảm 3,57%–35,71% trên các tác vụ hạ nguồn: phân loại, sentiment, fact-checking.
- **So với GreenScan:**
  - Giống: coi văn bản khí hậu là một miền riêng.
  - Khác: GreenScan không dùng ClimateBERT, vì mô hình chỉ có tiếng Anh và bất biến cấm fine-tune "cho trông AI hơn".
  - Học trò T1 (e5-base, đa ngữ) đạt macro-F1 0,71–0,73 **trên nhãn Claude**, nhưng chưa nối vào sản phẩm.
- **BGK có thể hỏi:** "Sao không dùng mô hình chuyên khí hậu có sẵn?"

**ClimaText.** Varini, Boyd-Graber, Ciaramita, Leippold. Workshop Tackling Climate Change with ML @ NeurIPS 2020. https://arxiv.org/abs/2012.00483 [MỞ]
- **Bài toán:** phát hiện câu có chủ đề biến đổi khí hậu.
- **Abstract:**
  - Mô hình dựa trên từ khoá "không đủ" cho bài toán này.
  - BERT bắt được nhiều ca dễ và một phần các mẫu ẩn, nhưng còn nhiều chỗ để cải thiện.
  - Abstract không ghi số.
- **Cỡ dữ liệu [TÌM, CHƯA XÁC MINH]:**
  - Wikipedia: train gán nhãn theo tài liệu khoảng 115.854 câu, dev 3.826; dev/test 300; tập active-learning 3.000 câu (261 dương).
  - 10-K: test 300 câu (67 dương); tập active-learning 3.000 câu (58 dương).
  - Claims: test 1.000 câu (500/500).
  - Giấy phép: chưa rõ.
- **So với GreenScan:** bộ trích tuyên bố của GreenScan là heuristic, gần với cách dựa trên từ khoá, nên có cùng rủi ro hụt recall.
- **BGK có thể hỏi:** "Bộ trích claim bỏ sót bao nhiêu?"

**Environmental Claim Detection.** Stammbach, Webersinke, Bingler, Kraus, Leippold. ACL 2023 (Vol. 2 Short), tr. 1051–1066. https://aclanthology.org/2023.acl-short.91/ [MỞ]
- **Abstract:** công bố dữ liệu do chuyên gia gán và mô hình đã huấn luyện. Số tuyên bố môi trường tăng đều kể từ Hiệp định Paris 2015.
- **Số liệu [TQ]:**
  - 3.000 câu; mỗi câu do 4 người trong nhóm 16 chuyên gia gán.
  - Bỏ 353 câu hoà phiếu, còn 2.647 câu; 25% là tuyên bố.
  - Krippendorff α = 0,47.
  - F1 trên test: TF-IDF SVM 69,1; char n-gram SVM 70,9; DistilBERT 83,7; ClimateBERT 83,8; RoBERTa-large 84,9.
- **Dataset trên HF [MỞ]:**
  - Giấy phép CC BY-NC-SA 4.0.
  - 2.647 dòng: viewer hiện 2,12k/265/265, còn mô tả trong card ghi 2.400/300/300.
  - Nhãn 0/1; trích dẫn arXiv 2209.00507.
- **So với GreenScan:**
  - Giống: đơn vị là câu và giữ nguyên văn (bất biến 2).
  - Khác: GreenScan không dừng ở bước phát hiện mà đối chiếu tuyên bố với bằng chứng và luật.
- **BGK có thể hỏi:** "Mức đồng thuận gán nhãn của em so với chuẩn ngành thế nào?"

**CLIMATE-FEVER.** Diggelmann, Boyd-Graber, Bulian, Ciaramita, Leippold. Workshop NeurIPS 2020. https://arxiv.org/abs/2012.00614 [MỞ]
- **Phương pháp:** áp quy trình FEVER cho tuyên bố khí hậu thật thu từ Internet.
- **HF `tdiggelm/climate_fever` [MỞ]:**
  - Giấy phép **"unknown"**.
  - 1,54k dòng, chỉ có split test.
  - Mỗi tuyên bố có 5 bằng chứng, mỗi bằng chứng kèm votes và entropy.
  - Nhãn: SUPPORTS / REFUTES / NOT_ENOUGH_INFO / DISPUTED.
- **Số liệu [TQ]:**
  - 1.535 tuyên bố, 7.675 cặp tuyên bố–bằng chứng; α = 0,334.
  - Mô hình train trên FEVER đạt 77,69% trên FEVER dev nhưng chỉ 38,78% trên Climate-FEVER.
- **So với GreenScan:**
  - Giống: có lớp "không đủ bằng chứng" và lớp "xung đột".
  - Khác: bằng chứng của GreenScan là báo cáo doanh nghiệp và bảng số, không phải Wikipedia; số do code so.
- **BGK có thể hỏi:** "Sao không chấm trên CLIMATE-FEVER?"

**climateBUG.** Yu, Scheidegger, Elliott, Löfgren (2024). *Expert Systems With Applications* 239, 122162. https://huggingface.co/datasets/lumilogic/climateBUG-Data [MỞ]
- **Dữ liệu:** hơn 1,07 triệu câu đã gán nhãn, từ báo cáo thường niên và báo cáo bền vững của ngân hàng EU, 2015–2020, tiếng Anh.
- **Giấy phép:** CC BY-NC-ND 4.0, kèm điều kiện cấm chia sẻ lại.
- **[TÌM]:**
  - Nhãn là climate / non-climate; có mô hình climateBUG-LM.
  - Survey 2025 xếp climateBUG vào dữ liệu truyền thông doanh nghiệp, không phải dữ liệu tẩy xanh.
- **So với GreenScan:** liên quan khi BGK tài chính hỏi về ngân hàng hay tín dụng xanh. Vì giấy phép ND, chỉ dùng để tham khảo.

**ESG-BERT [TQ].** Không có paper. F1 0,90 so với BERT-base 0,79 do tác giả tự báo; giấy phép ghi "More information needed". Không dùng.

**Braun, Ong, Mao, Cambria, Mengaldo (2026).** *Enhancing Language Models for Robust Greenwashing Detection.* arXiv 2601.21722, 29/01/2026. [MỞ]
- **Phương pháp:**
  - Tinh chỉnh tiết kiệm tham số.
  - Học tương phản cộng mục tiêu xếp hạng thứ bậc, để phân biệt theo mức độ giữa "hành động cụ thể" và "tuyên bố mơ hồ".
  - Gated feature modulation để lọc nhiễu; MetaGradNorm để ổn định tối ưu đa mục tiêu.
- **Kết quả:** bền hơn baseline khi thử khác danh mục, nhưng có đánh đổi giữa độ cứng của biểu diễn và khả năng tổng quát hoá. Abstract không có số.
- **So với GreenScan:**
  - Giống: coi độ mơ hồ là thang bậc; rubric rủi ro có thành phần "mơ hồ" và "specificity".
  - Khác: GreenScan dùng quy tắc minh bạch, không học không gian ẩn.

**Greench-v1.** Raspanti, Bardelli, Scala, Demirtaş, Di Bari, Filannino. NLP4Ecology 2026 (workshop, ELRA), tr. 79–86, tháng 5/2026. https://aclanthology.org/2026.nlp4ecology-1.8/ [MỞ]
- **Phương pháp:**
  - Mô hình nhỏ dựa trên Qwen3-4B, sàng lọc văn bản ESG theo từng đoạn.
  - Dữ liệu khoảng 2.000 đoạn, chuyển từ kho ClimateBERT.
  - So bốn chế độ: chưng cất cứng, chưng cất mềm từ thầy Qwen3-14B, GRPO, và GRPO lai.
- **Kết quả:** chưng cất mềm và GRPO tăng weighted F1 của lớp "Greenwashing Alert" lần lượt 36,7% và 49,0%.
- **[TÌM]:** đầu ra 3 lớp kèm lý do ngắn; lý do do GPT-4o sinh.
- **So với GreenScan:**
  - Giống: cùng dùng Qwen3-4B, chạy được ngoại tuyến.
  - Khác căn bản: Greench để model *phán* "tẩy xanh". GreenScan để model *đọc* câu thành IR, rồi code so số và luật quyết.
  - GreenScan đã loại RL/GRPO vì không có phần thưởng kiểm được khi chưa có gold.

**EmeraldMind [TQ].** Kaoukis et al., WWW 2026, arXiv 2512.11506.
- **Phương pháp:** knowledge graph ESG cộng RAG, có abstain.
- **Dữ liệu:** EmeraldData gồm 620 tuyên bố bán tổng hợp: 225 tẩy xanh, 395 không.
- **Kết quả:**

| Hệ | Accuracy trên phần trả lời | Coverage | Overall |
|---|---|---|---|
| LLM baseline | 94,21% | 19,52% | 18,39% |
| EM-HYBRID | 83,80% | 74,68% | 62,58% |

  - Overall = Accuracy × Coverage.
- **[TÌM 04/11]:** đầu ra là greenwashing / not / abstain kèm lý giải; có bản demo EmeraldApp.
- **So với GreenScan:**
  - Giống: báo cặp precision–độ phủ và có abstain.
  - Khác: LLM của EmeraldMind ra verdict; dữ liệu do LLM sinh.

### 1B. Kiểm chứng, suy luận số và bảng [TQ, không mở lại]

- **FEVER** (Thorne et al., NAACL 2018):
  - 185.445 tuyên bố; Fleiss κ = 0,6841; giấy phép CC BY-SA 3.0.
  - Pipeline tốt nhất đạt 31,87% khi bắt buộc đúng cả bằng chứng, 50,91% nếu bỏ qua bằng chứng.
  - Bài học cho GreenScan: chỉ chấm verdict khi bằng chứng đúng.
- **FinQA** (Chen et al., EMNLP 2021):
  - 8.281 cặp hỏi–đáp từ 2.789 trang báo cáo S&P 500.
  - FinQANet 61,24%; chuyên gia 91,16%; người không chuyên 50,68%.
  - Câu cần từ 3 bước suy luận trở lên: 22,78%.
  - Giấy phép: thẻ HF ghi cc-by-4.0 [TÌM].
- **TAT-QA** (Zhu et al., ACL 2021):
  - TAGOP đạt 58,0 F1; chuyên gia 90,8.
  - Giấy phép: README của repo ghi CC BY 4.0, nhưng bài báo ghi "phi thương mại" [TÌM]. Hai nguồn **mâu thuẫn**.
- **Liên quan GreenScan:**
  - Số học nhiều bước và bảng là chỗ model sụp, nên số học giao cho code (bất biến 5).
  - Bảng PDF bị dàn phẳng là lỗi F3; AG-3 dựng lại hàng bảng.

### 1C. RAG và đánh giá bằng LLM

**RAG.** Lewis et al., NeurIPS 2020. https://arxiv.org/abs/2005.11401 [MỞ]
- **Phương pháp:** bộ nhớ tham số là mô hình seq2seq đã pretrain; bộ nhớ phi tham số là chỉ mục vector dày của Wikipedia, truy cập qua retriever nơ-ron.
- **Kết quả:** SOTA trên 3 tác vụ QA miền mở. Văn bản sinh ra cụ thể, đa dạng và đúng sự thật hơn baseline chỉ có bộ nhớ tham số.
- **So với GreenScan:** GreenScan chỉ dùng phần "R" để tìm ứng viên bằng chứng (bất biến 3); không dùng "G" để ra kết luận.

**RAGAS.** Es, James, Espinosa-Anke, Schockaert. arXiv 2309.15217 (v2 28/04/2025). [MỞ]
- **Phương pháp:** đánh giá RAG không cần đáp án tham chiếu, theo ba chiều:
  - retriever có lấy được ngữ cảnh liên quan và gọn không;
  - LLM có dùng ngữ cảnh một cách trung thực không;
  - chất lượng câu trả lời.
- **So với GreenScan:**
  - Hợp để kiểm *lời giải thích* có bám bằng chứng không.
  - Không thay được bộ đo verdict, vì "nhất quán với ngữ cảnh" chưa phải là "đúng".

**LLM-as-a-judge [TQ].** Zheng et al., NeurIPS 2023 D&B.
- GPT-4 đồng ý với người trên 80% ở bài sở thích hội thoại.
- Có thiên vị vị trí, độ dài và tự đề cao.

**G-Eval.** Liu, Iter, Xu, Wang, Xu, Zhu. arXiv 2303.16634 (v3 23/05/2023). [MỞ]
- **Phương pháp:** GPT-4 với CoT và điền phiếu.
- **Kết quả:** Spearman 0,514 với người trên bài tóm tắt.
- **Cảnh báo của tác giả:** evaluator LLM thiên vị văn bản do LLM viết.

**Gilardi, Alizadeh, Kubli.** PNAS 120(30) e2305016120, 2023. arXiv 2303.15056 [MỞ]
- **Dữ liệu:** 2.382 tweet; tác vụ: liên quan, lập trường, chủ đề, khung.
- **Kết quả:**
  - ChatGPT zero-shot chính xác hơn crowd-worker ở 4/5 tác vụ.
  - Độ đồng thuận nội bộ của ChatGPT cao hơn cả crowd lẫn người gán đã được đào tạo, ở mọi tác vụ.
  - Chi phí dưới 0,003 USD/nhãn, rẻ hơn MTurk khoảng 20 lần.
- **So với GreenScan:**
  - Là căn cứ để dùng nhãn Claude làm dữ liệu; người dùng sẽ soát lại.
  - Giới hạn: miền là tweet; đồng thuận cao chưa phải là đúng; nếu nhãn và bài thi cùng một nguồn Claude thì dễ thành vòng tròn.

### 1D. Bất định: abstain, hiệu chỉnh, conformal

- **Geifman & El-Yaniv, NeurIPS 2017 [TQ]:** khung risk–coverage. Ví dụ trong paper: top-5 error 2% trên ImageNet với xác suất 99,9%, ở coverage gần 60%.
- **Guo, Pleiss, Sun, Weinberger, ICML 2017.** arXiv 1706.04599 [MỞ]
  - Mạng nơ-ron hiện đại hiệu chỉnh kém hơn mạng của 10 năm trước.
  - Độ sâu, độ rộng, weight decay và BatchNorm đều ảnh hưởng tới hiệu chỉnh.
  - Temperature scaling đơn giản nhưng "hiệu quả bất ngờ".
- **Angelopoulos & Bates.** arXiv 2107.07511 (v6 07/12/2022). [MỞ]
  - Tập dự đoán conformal chứa đáp án đúng với xác suất do người dùng chọn.
  - Bảo đảm tường minh, không tiệm cận, không cần giả định phân phối.
  - Gắn được vào mọi mô hình đã train.
- **Mohri & Hashimoto, ICML 2024 [TQ]:** conformal factuality đạt bảo đảm 80–90% với ít mẫu có nhãn, bằng cách làm đầu ra bớt cụ thể.
- **GreenScan đang làm dạng đơn giản nhất của selective prediction:**
  - Luật và bộ đọc đồng thuận thì kết luận; còn lại nhường người.
  - Báo precision trên phần kết luận và độ phủ (bất biến 8).
  - Chưa hiệu chỉnh xác suất. Điểm rủi ro 0–100 không phải xác suất (D-2026-09-18-05).

### 1E. Độ trung thực của lời giải thích

- **Jacovi & Goldberg, ACL 2020, tr. 4198–4205.** https://aclanthology.org/2020.acl-main.386/ [MỞ]
  - Đề nghị bỏ định nghĩa nhị phân của faithfulness, chuyển sang thang bậc; định nghĩa nhị phân đặt chuẩn phi thực tế.
  - Đưa hướng dẫn nên và không nên khi đánh giá.
- **Turpin, Michael, Perez, Bowman, NeurIPS 2023.** arXiv 2305.04388 [MỞ]
  - Lời giải thích CoT có thể xuyên tạc có hệ thống lý do thật của dự đoán.
  - Đặc trưng gây lệch (ví dụ đáp án luôn là "(A)") tác động mạnh nhưng không được nhắc trong lời giải thích.
  - Accuracy giảm tới 36% trên 13 tác vụ BIG-Bench Hard, với GPT-3.5 và Claude 1.0.
- **GreenScan:**
  - Với phần tất định, lời giải thích *chính là* đường tính thật: `computed_values`, `policy_id`, câu trích kèm trang, `rule_id`. Vì vậy trung thực theo cách dựng.
  - Văn bản do LLM viết (nếu bật) chỉ được coi là "dễ đọc", không phải căn cứ.

### 1F. Tuân thủ quy tắc, prompt injection, bộ nhớ của agent

- **RuLES.** Mu et al. arXiv 2311.04235 (v3 08/03/2024; trang không ghi hội nghị). [MỞ]
  - 14 kịch bản văn bản đơn giản; mỗi kịch bản có hàm chấm bằng chương trình.
  - Hầu hết model hiện tại khó tuân thủ quy tắc.
  - Tấn công tối ưu đơn giản đủ làm tăng mạnh tỷ lệ hỏng.
  - Hướng cải thiện: lái model lúc suy luận và SFT.
- **IFEval.** Zhou et al. arXiv 2311.07911 [MỞ]
  - 25 loại chỉ dẫn kiểm được tự động, khoảng 500 prompt.
  - Lý do chọn chỉ dẫn kiểm được: chấm bằng người đắt và khó lặp lại; chấm bằng LLM thì thiên lệch.
- **Instruction Hierarchy.** Wallace et al. arXiv 2404.13208 [MỞ]
  - LLM thường coi system prompt ngang hàng với văn bản không tin cậy của người dùng và bên thứ ba.
  - Đề xuất thứ bậc chỉ dẫn, kèm dữ liệu huấn luyện dạy model bỏ qua chỉ dẫn cấp thấp.
  - Trên GPT-3.5: độ bền tăng mạnh, kể cả với kiểu tấn công chưa thấy khi huấn luyện; năng lực chuẩn giảm rất ít.
- **Greshake et al.** arXiv 2302.12173 (v2 05/05/2023). [MỞ]
  - Prompt injection gián tiếp: cài chỉ dẫn vào nội dung mà ứng dụng sẽ truy xuất.
  - Ứng dụng tích hợp LLM "xoá ranh giới giữa dữ liệu và chỉ dẫn".
  - Đã tấn công được Bing Chat (GPT-4), công cụ hoàn thành mã và các ứng dụng GPT-4 tự dựng.
  - Hậu quả: lấy cắp dữ liệu, lây lan, làm bẩn hệ sinh thái thông tin, điều khiển lệnh gọi API khác.
- **MemGPT.** Packer et al. arXiv 2310.08560 (v2 12/02/2024). [MỞ]
  - Quản lý "ngữ cảnh ảo" theo bộ nhớ phân tầng của hệ điều hành, chuyển dữ liệu giữa bộ nhớ nhanh và chậm.
  - Thử trên phân tích tài liệu dài và chat nhiều phiên.
- **ACE (Agentic Context Engineering).** Zhang et al., ICLR 2026, arXiv 2510.04618 (v3 29/03/2026). [MỞ]
  - Coi ngữ cảnh là "playbook" tiến hoá: tích luỹ, tinh chỉnh và sắp xếp chiến lược qua ba bước sinh, phản tư, chọn lọc.
  - Chỉ ra hai lỗi của cách cũ:
    - **brevity bias**: tóm gọn làm rơi hiểu biết miền;
    - **context collapse**: viết lại nhiều lần làm mòn chi tiết.
  - Kết quả: +10,6% trên benchmark agent, +8,6% trên benchmark tài chính.
  - Thích nghi không cần nhãn, dựa vào phản hồi thực thi.
- **GreenScan, phần "bộ nhớ chuẩn":** rule pack có phiên bản, kho điều khoản pháp lý, `taxonomy.yaml`, `stance_cues.yaml` và `measurement_decisions.yaml`.
- **GreenScan, phần "bổ sung":**
  - Một quy tắc chỉ ACTIVE khi qua 4 cổng trong `check_rule`: `source_clause_bound`, `human_reviewed`, `unit_tests_pass`, `temporal_scope_defined`.
  - Khác ACE: GreenScan không để LLM tự viết lại bộ quy tắc.

### 1G. UX và độ tin cậy của nhãn

- **10 heuristic của Nielsen.** https://www.nngroup.com/articles/ten-usability-heuristics/ [MỞ]
  - Nielsen soạn cùng Molich năm 1990, tinh chỉnh năm 1994 bằng phân tích nhân tố trên 249 vấn đề khả dụng.
  - Mười mục:
    1. hiển thị trạng thái hệ thống;
    2. khớp với thế giới thực;
    3. quyền kiểm soát và tự do của người dùng;
    4. nhất quán và theo chuẩn;
    5. phòng lỗi;
    6. nhận ra hơn là nhớ lại;
    7. linh hoạt và hiệu quả;
    8. thẩm mỹ tối giản;
    9. giúp nhận ra, chẩn đoán và phục hồi lỗi;
    10. trợ giúp và tài liệu.
- **SUS (Brooke) [TÌM, CHƯA XÁC MINH trên trang gốc]:**
  - Thang "quick and dirty" gồm 10 câu, điểm 0–100.
  - Trung bình 68 (MeasuringU, khoảng 500 nghiên cứu). Điểm này không phải phần trăm.
  - Thang chấm cong của Lewis (2018), xây từ 241 nghiên cứu: 68 = C, trên 80,3 = A, dưới 51 = F.
  - Các nguồn ghi năm tạo thang là 1986, bài tham chiếu năm 1996.
- **Guidelines for Human-AI Interaction.** Amershi et al., CHI 2019 (Honorable Mention). [MỞ]
  - 18 hướng dẫn.
  - Kiểm qua nhiều vòng, trong đó có nghiên cứu với 49 người làm thiết kế trên 20 sản phẩm có AI.
  - Thuộc bộ HAX Toolkit.
  - Trang đã mở không liệt kê 18 hướng dẫn.
- **Krippendorff α.** https://en.wikipedia.org/wiki/Krippendorff%27s_alpha [MỞ]
  - α = 1 − D_o/D_e.
  - Dùng được cho nhãn danh nghĩa, thứ bậc, khoảng, tỉ lệ, cực và vòng; bao nhiêu người gán cũng được; chịu được dữ liệu thiếu.
  - Ngưỡng: α ≥ 0,800 thì dựa vào được; 0,667 ≤ α < 0,800 chỉ đủ cho kết luận tạm; α < 0,667 thì bỏ.
- **Cohen κ [TQ + KIẾN THỨC NỀN]:**
  - Thang Landis & Koch 1977: 0,41–0,60 trung bình, 0,61–0,80 đáng kể, 0,81–1 gần hoàn hảo.
  - McHugh 2012: thang này quá dễ dãi; nên báo kèm percent agreement.
  - Khi lớp lệch, κ có thể thấp dù tỷ lệ đồng ý cao (Feinstein & Cicchetti 1990).
- **GreenScan:**
  - Kế hoạch v3 (mục F3) đặt mục tiêu SUS ≥ 70 với 5–8 người (sinh viên kế toán, kiểm toán viên).
  - `AUDIT_HE_THONG_2026-10.md` ghi mục này là "Chưa". Tới 01/11 không thấy kết quả SUS trong docs.

### 1H. Danh mục bộ dữ liệu công khai theo mục tiêu

| Mục tiêu | Bộ dữ liệu | Cỡ | Ngôn ngữ | Giấy phép | URL | Mức xác minh |
|---|---|---|---|---|---|---|
| Phát hiện tuyên bố | environmental_claims | 2.647 câu (2.117/265/265) | EN | CC BY-NC-SA 4.0 | huggingface.co/datasets/climatebert/environmental_claims | [MỞ] |
| Phát hiện tuyên bố | ClimaText | khoảng 115,9k câu train Wiki gán tự động; test 300 / 300 / 1.000 | EN | chưa rõ | arxiv.org/abs/2012.00483 | abstract [MỞ]; cỡ [TÌM] |
| Phát hiện tuyên bố | climateBUG-Data | hơn 1,07 triệu câu, ngân hàng EU 2015–2020 | EN | CC BY-NC-ND 4.0 + cấm chia sẻ lại | huggingface.co/datasets/lumilogic/climateBUG-Data | [MỞ] |
| Phát hiện / chấm rủi ro | netzero_reduction; climate_specificity; climate_commitments_actions | 3.441; 1.320; 1.320 | EN | Apache-2.0; CC BY-NC-SA; CC BY-NC-SA | hf climatebert/* | [TQ] |
| Chấm rủi ro (hành động vs mơ hồ) | A3CG | 2.004 câu, 2.723 cặp aspect–action | EN | CC BY 4.0 (theo paper) | aclanthology 2025.acl-long.723 | [TQ] |
| Kiểm chứng | FEVER | 185.445 tuyên bố | EN | CC BY-SA 3.0 | aclanthology N18-1074 | [TQ] |
| Kiểm chứng | CLIMATE-FEVER | 1.535 tuyên bố × 5 bằng chứng; 4 nhãn | EN | "unknown" | huggingface.co/datasets/tdiggelm/climate_fever | [MỞ] |
| Kiểm chứng (độ nhạy) | VitaminC | hơn 400k cặp tương phản | EN | CC BY-SA 3.0 | aclanthology 2021.naacl-main.52 | [TQ] |
| Kiểm chứng + cherry-picking | AVeriTeC | 4.568 | EN | CC BY-NC 4.0 | arxiv 2305.13117 | [TQ] |
| Tuyên bố có số | QuanTemp | 15.514 | EN | CC BY-NC 4.0 | arxiv 2403.17169 | [TQ] |
| Số / bảng tài chính | FinQA | 8.281 cặp hỏi–đáp | EN | cc-by-4.0 (thẻ HF) | github.com/czyssrs/FinQA | cỡ [TQ]; giấy phép [TÌM] |
| Số / bảng tài chính | TAT-QA | (chưa mở) | EN | CC BY 4.0 (README) hay phi thương mại (paper)? | github.com/NExTplusplus/tat-qa | [TÌM], mâu thuẫn |
| Kiểm chứng báo cáo tài chính | FinDVer | 2.100 | EN | MIT (repo) | aclanthology 2024.emnlp-main.818 | [TQ] |
| Tẩy xanh có abstain | EmeraldData | 620 tuyên bố bán tổng hợp | EN | chưa rõ | arxiv 2512.11506 | [TQ] |
| Giải thích | PUBHEALTH | 11,8k tuyên bố, kèm lời giải thích của nhà báo; nhãn true/false/unproven/mixture | EN | chưa rõ | github.com/neemakot/Health-Fact-Checking | [TÌM] |
| Giải thích | LIAR-PLUS | 10.146 / 1.278 / 1.255; lý giải trích từ PolitiFact | EN | chưa rõ | (chưa mở) | [TÌM] |
| Giải thích | e-FEVER / EX-FEVER | FEVER cộng lời giải thích tổng hợp bằng GPT-3 (chất lượng không bảo đảm); EX-FEVER nhiều bước | EN | chưa rõ | ar5iv 2310.09754 | [TÌM] |
| Gợi ý sửa | VitaminC (cặp sửa tối thiểu đổi kết luận) | như trên | EN | CC BY-SA 3.0 | như trên | [TQ] |
| Gợi ý sửa | GS-Bench B-b nội bộ: mỗi ca nhiễu có tuyên bố đúng gốc và IR gold | 402 ca B-b | VI | nội bộ | `benchmark/gs_bench_v1/` | dữ liệu [ĐÃ THỰC NGHIỆM]; dùng cho gợi ý sửa là [GIẢ THUYẾT] |
| Tiếng Việt | ViFactCheck; ISE-DSC01; ViNLI; ViANLI; XNLI-vi | 7.232; khoảng 48k; 30.376; 10.012; dev 2.490 / test 5.010 | VI | MIT; chưa rõ; chỉ cho nghiên cứu; CC BY-NC-SA; CC BY-NC | xem [TQ] mục 4 | [TQ] |
| Tẩy xanh tiếng Việt | **không tìm thấy** bộ NLP công khai; dự án VinUni GREEN-X dự kiến phát hành "Vietnam ESG Transparency Dataset", chưa rõ đã phát hành | — | VI | — | greenx.vinuni.edu.vn | [TÌM] |

---

## 2. Khái niệm và lý thuyết phải nắm

**1. Phát hiện tuyên bố khác kiểm chứng tuyên bố.**
- Phát hiện: câu này có phải tuyên bố môi trường không (Stammbach 2023, ClimaText).
- Kiểm chứng: tuyên bố có khớp bằng chứng không (FEVER, CLIMATE-FEVER).
- GreenScan làm cả hai. Lõi giá trị nằm ở kiểm chứng tuyên bố có số, với điều kiện so được: cùng chỉ số, đơn vị, kỳ, Scope, ranh giới (bất biến 4).

**2. Nhãn kiểm chứng và quy tắc gộp.**
- NEI / INSUFFICIENT_EVIDENCE là kết luận hợp lệ.
- "Vắng bằng chứng" khác "bị bác bỏ" (bất biến 6).
- Có cả bằng chứng ủng hộ lẫn bác bỏ thì gộp thành DISPUTED / xung đột (CLIMATE-FEVER).
- Ví dụ: "giảm 30% phát thải", trong khi bảng ghi Scope 1 giảm 8% còn tuyên bố nói Scope 1+2. Lệch một chiều thì **cấm** kết luận CONTRADICTED; chuyển người soát.

**3. Selective prediction (risk–coverage).**
- Công thức:
  - độ phủ φ = (số ca dám kết luận) / N;
  - rủi ro chọn lọc = (số kết luận sai) / (số ca dám kết luận);
  - precision trên phần kết luận = 1 − rủi ro chọn lọc;
  - EmeraldMind dùng thêm Overall = Accuracy × Coverage.
- Ví dụ trên tập G (162 ca), luật + 4B: φ = 0,093, tức khoảng 15 ca, và 15/15 đúng.
  - Khoảng Clopper–Pearson 95% cho tỷ lệ đúng là [0,78; 1] [tự tính, KIẾN THỨC NỀN].
  - Theo "quy tắc số 3", tỷ lệ sai thật có thể tới khoảng 3/15 = 20%.
  - Đây là lý do kế hoạch ghi "chưa phải một cận chặt".

**4. Hiệu chỉnh (calibration).**
- Mô hình hiệu chỉnh tốt nghĩa là trong các dự đoán có độ tin 0,8 thì khoảng 80% đúng.
- ECE = Σ_m (|B_m|/n)·|acc(B_m) − conf(B_m)|. Temperature scaling: p = softmax(z/T), với T học trên tập kiểm định [KIẾN THỨC NỀN].
- GreenScan:
  - AG-2 ước P(đúng) trên OOF theo công ty, nhưng "xô OOF quá mảnh", nên chuyển sang chính sách đồng thuận đơn giản.
  - Điểm rủi ro 0–100 là thang xếp hàng, không phải xác suất.

**5. Conformal prediction (dạng split).**
- Cách làm: tính điểm bất phù hợp s_i trên n ca hiệu chỉnh; lấy q̂ là phân vị mức ⌈(n+1)(1−α)⌉/n; tập dự đoán C(x) = {y : s(x,y) ≤ q̂}.
- Bảo đảm: P(Y ∈ C(X)) ≥ 1 − α khi dữ liệu hoán đổi được (exchangeable) [KIẾN THỨC NỀN; trang đã mở chỉ nói "không cần giả định phân phối"].
- GreenScan có thể trả tập {SUPPORTED, PARTIAL} thay cho một nhãn. Vướng mắc: tuyên bố cùng công ty không độc lập, nên cần hiệu chỉnh theo cụm công ty [GIẢ THUYẾT].

**6. Trung thực (faithful) và hợp lý (plausible).**
- Trung thực: lời giải thích phản ánh đúng quá trình ra quyết định.
- Hợp lý: lời giải thích thuyết phục người đọc (Jacovi & Goldberg) [KIẾN THỨC NỀN].
- Ví dụ GreenScan: "lệch 22%, cùng tCO₂e, cùng Scope 1+2, câu trang 39, policy `rel_tol`" là lời giải thích trung thực vì nó chính là phép tính. Một đoạn CoT do LLM viết thì chỉ hợp lý (Turpin: có thể giấu lý do thật).

**7. RAG.**
- Bộ nhớ tham số (trọng số model) cộng bộ nhớ phi tham số (chỉ mục tài liệu).
- GreenScan:
  - Retrieval chỉ tìm ứng viên.
  - Đánh giá tách tầng: Recall@k cho tầng tìm, precision/độ phủ cho tầng verdict.
  - Tương đồng cao không bao giờ tự ra SUPPORTED/CONTRADICTED (bất biến 3).

**8. Đánh giá có và không có tham chiếu.**
- RAGAS không cần đáp án: đo tính nhất quán.
- GS-Bench có đáp án theo cấu trúc: đo đúng sai.
- LLM-as-judge có thiên vị vị trí, độ dài, tự đề cao (Zheng) và thiên vị văn bản LLM (G-Eval).

**9. Nhãn bạc và LLM gán nhãn.**
- LLM có thể gán nhãn tốt hơn crowd (Gilardi).
- Để không thành vòng tròn:
  1. sinh đáp án bằng code khi có thể (B-b);
  2. gán hai lượt mù rồi phân xử (B-c);
  3. dùng người đọc thứ hai khác họ model (Qwen3-32B);
  4. có người soát mẫu;
  5. không vừa train vừa thi trên nhãn của cùng một model mà gọi kết quả là "độ chính xác".

**10. Tuân thủ quy tắc kiểm được.**
- Quy tắc phải biến thành vị từ chạy được (RuLES, IFEval). Trong GreenScan, đó chính là policy-as-code.
- Ví dụ: quy tắc "không kết luận CONTRADICTED khi lệch chiều Scope" là bất biến 4, có test `invariant_4_…` và 44 bẫy.

**11. Thứ bậc chỉ dẫn và prompt injection gián tiếp.**
- Kênh chỉ dẫn (system / nhà phát triển) tách khỏi kênh dữ liệu (PDF của doanh nghiệp).
- GreenScan:
  - `contains_prompt_injection` đánh dấu chunk nghi ngờ bằng `suspicious_instruction`; `injection_policy: exclude` loại chunk đó khỏi verifier.
  - Đầu ra của bộ đọc là JSON có schema; `ground()` buộc mọi số phải có trong câu gốc.

**12. Bộ nhớ của agent.**
- MemGPT: bộ nhớ phân tầng. ACE: playbook tự tiến hoá, với hai rủi ro brevity bias và context collapse.
- Bộ nhớ của GreenScan:
  - chỉ ghi thêm (`audit.jsonl`), có phiên bản, có người ký và test;
  - manifest ghi hash đầu vào, rule pack và prompt/model (bất biến 10).

**13. Hệ số đồng thuận.**
- κ = (p_o − p_e)/(1 − p_e), với p_e = Σ_k p_A,k · p_B,k. α = 1 − D_o/D_e.
- Ví dụ minh hoạ [tự tính]: hai người gán 100 cặp, đồng ý 85 cặp, mỗi người gán 70% là S.
  - p_e = 0,7² + 0,3² = 0,58, nên κ = 0,27/0,42 ≈ 0,64.
  - Theo Landis–Koch đó là "đáng kể", nhưng vẫn dưới mốc 0,667 của Krippendorff. So sánh này chỉ minh hoạ, vì κ và α là hai hệ số khác nhau.

**14. SUS.**
- Điểm = 2,5 × [Σ câu lẻ (x_i − 1) + Σ câu chẵn (5 − x_i)], với x_i từ 1 tới 5 [KIẾN THỨC NỀN].
- Thang 0–100, không phải phần trăm. Trung bình 68 [TÌM].
- Kế hoạch đo kèm tỷ lệ hoàn thành nhiệm vụ và thời gian hoàn thành, ví dụ "tìm câu bằng chứng của tuyên bố X" và "chấp nhận hoặc bác một gợi ý sửa".

**15. Heuristic Nielsen và hướng dẫn Human-AI, áp vào Studio.**
- "Hiển thị trạng thái": tiến độ chạy, chế độ `offline`.
- "Khớp thế giới thực": thuật ngữ kế toán–KNK.
- "Phòng lỗi": gợi ý sửa không bao giờ đưa số mới.
- "Phục hồi lỗi": người soát bác được kết luận.

**16. Kiểm định giữ nhóm.**
- Leave-company-out: train/dev không bao giờ chung công ty với test.
- Bootstrap theo công ty để tính khoảng tin cậy.
- Ngưỡng và dự đoán đăng ký trước trong `configs/measurement_decisions.yaml`.

---

## 3. Số liệu và dữ kiện được phép nói

### GreenScan (nguồn chung: `docs/00-project/KE_HOACH_AGENT_KAGGLE_LUAN_VAN_2026-10-31.md`, gọi tắt KH)
- GS-Bench v1.1 có 453 ca: 51 B-a + 402 B-b (S 95 / C 123 / N 184), trên 7 doanh nghiệp, 0 ca lệch selfcheck · KH §10 "31/10 14:15" · [ĐÃ THỰC NGHIỆM]
- Luật (AG-0) trên B-b v1 (142 ca): độ phủ 0,028 (4/142), precision 0,75, bắt được 0/44 ca mâu thuẫn · KH §10 "31/10" · [ĐÃ THỰC NGHIỆM, trên ca dựng]
- Trần IR gold + `irlib`: đúng 140/142, độ phủ 0,528, precision 1,0, 0 kết luận sai · KH §10 "31/10" · [ĐÃ THỰC NGHIỆM, trên ca dựng]
- 11/11 kết luận sai của 32B là do model tự thêm bội số ("10.730 m3" → "10.730 ngàn m3"). Đã sửa bằng `irlib.ground()` kèm 9 test hồi quy · KH §10 "14:15" · [ĐÃ THỰC NGHIỆM]
- Trong mẫu, sau `ground()`:
  - 4B: độ phủ 0,134 → 0,437, precision 0,984.
  - 32B: precision 0,817 → 0,985; CONTRADICTED sai 7 → 1.
  - Nguồn: KH §10 "14:15" · [ĐÃ THỰC NGHIỆM, **trong mẫu**, không dùng làm số chính]
- Ngoài mẫu v1.1, độ phủ 4B / 8B / 14B / 32B = 0,126 / 0,220 / 0,256 / 0,329 · KH §10 "22:40" · [ĐÃ THỰC NGHIỆM]
- **Ngoài mẫu sạch v1.3 (87 ca):**
  - Độ phủ: luật 0,011; 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253.
  - Mọi model precision 1,0, 0 kết luận sai.
  - Nguồn: KH §10 "01/11 17:00" · [ĐÃ THỰC NGHIỆM]
  - Số ca thực sự được kết luận chỉ khoảng 1–22 [tự tính]. Cận dưới Clopper–Pearson 95%: 12/12 ≈ 0,74; 22/22 ≈ 0,85 [KIẾN THỨC NỀN].
- **AG-2, chính sách "luật + 4B, bỏ phiếu S đơn độc của luật"** (mỗi ô: độ phủ / precision / SUPPORTED sai / CONTRADICTED sai):
  - Trên G (162 ca): 0,093 / 1,0 / 0 / 0; phần tăng độ phủ có CI [0,016; 0,185].
  - Trên tập hiệu chỉnh (388 ca): 0,242 / 0,989 / 1 / 0, trong khi luật một mình có 8 SUPPORTED sai.
  - Nguồn: KH §10 "23:50" · [ĐÃ THỰC NGHIỆM]
- Luật + 32B và luật + 4 model **trượt cổng** trên G: lần lượt 1 và 2 SUPPORTED sai, trong khi luật có 0 · KH §10 "23:50" · [ĐÃ THỰC NGHIỆM]
- **Bộ đọc của sản phẩm** (Ollama + `ir_reader.py`, chạy trên Kaggle):
  - Q4 khớp 0,963 và Q8 khớp 0,981 so với 4B bf16.
  - Luật + 4B Q4 trên G: 0 kết luận sai, độ phủ 0,080, CI phần tăng [0,016; 0,175].
  - Trên T4: 1,7 giây/câu. Thời gian trên laptop **chưa đo** vì thiếu RAM.
  - Nguồn: KH §10 "17:15" · [ĐÃ THỰC NGHIỆM]
- **AG-3 v0:**
  - HPG trang 39 dựng lại đủ 10 hàng; cộng dọc khớp 3/3.
  - Trên 7 ca của trang này: trang thô đúng 1/7; hàng dựng lại đúng 3/7, 0 sai.
  - Dự đoán "≥ 5/7" **sai**.
  - Nguồn: KH §10 "17:40" · [ĐÃ THỰC NGHIỆM]
- **Lỗi nền đã đo:**
  - HPG 156 tuyên bố: 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT.
  - 0 quy tắc pháp lý áp được trên 156/156 tuyên bố.
  - Gold người: 0/88 cặp và 0/79 câu.
  - Nguồn: KH §2 (F1, F5, F7) · [ĐÃ THỰC NGHIỆM]
- T1 (e5-base) đạt macro-F1 0,71–0,73 trên nhãn Claude, kiểm định chéo theo công ty, n = 1.217, 3 seed; chưa nối vào sản phẩm · KH §2 · [ĐÃ THỰC NGHIỆM, **trên nhãn Claude**]
- Nhãn họ nhiễu của GS-Bench khớp `irlib` 142/142; soát tay 14 ca thấy nhãn đúng, sửa 3 lỗi diễn đạt · KH §10 "31/10" · [ĐÃ THỰC NGHIỆM]
- GROQ-PROBE chọn `gpt-oss-120b` với `reasoning_effort` low + `json_object`: 12/12 JSON hợp lệ, độ đúng trường 1,0, p50 1,0 giây · KH §10 "14:15" · [ĐÃ THỰC NGHIỆM]
- Một quy tắc chỉ ACTIVE khi qua 4 cổng: `source_clause_bound`, `human_reviewed`, `unit_tests_pass`, `temporal_scope_defined` · `src/quantum_gw/legal/gates.py`, `check_rule` · [ĐÃ THỰC NGHIỆM: có trong code và test `test_legal_gates.py`]
- **Gợi ý sửa của Studio:**
  - Bốn loại, sinh từ mẫu luật: thêm phạm vi/kỳ/năm gốc (`add_scope`); chỗ trống cần bổ sung số liệu (`placeholder`); dẫn chiếu bằng chứng (`evidence_ref`); làm nhẹ lời nói quá (`soften`).
  - Mọi gợi ý qua `assert_no_new_numbers`; gợi ý nào đưa số mới thì bị bỏ.
  - Nguồn: `src/quantum_gw/studio/suggest.py` (docstring) · [ĐÃ THỰC NGHIỆM: có trong code; **chưa có số đo chất lượng gợi ý**]

### Ngoài
- ClimateBERT: hơn 2 triệu đoạn văn; masked LM cải thiện 48%; tỷ lệ lỗi giảm 3,57–35,71% · arXiv 2110.12010, abstract · [NGOÀI]
- Environmental claims: 2.647 câu; α = 0,47; RoBERTa-large F1 84,9 so với SVM 69,1–70,9; giấy phép CC BY-NC-SA 4.0 · [TQ] S1.5 + thẻ HF [MỞ] · [NGOÀI]
- CLIMATE-FEVER: 1.535 tuyên bố, 4 nhãn, α = 0,334; giấy phép trên HF "unknown"; chuyển từ FEVER sang Climate-FEVER làm accuracy rơi từ 77,69% xuống 38,78% · [TQ] S2.4 + HF [MỞ] · [NGOÀI]
- climateBUG: hơn 1,07 triệu câu, 2015–2020, CC BY-NC-ND 4.0 · HF [MỞ] · [NGOÀI]
- Greench-v1: Qwen3-4B, khoảng 2.000 đoạn; weighted F1 lớp Alert tăng 36,7% / 49,0% · ACL Anthology 2026.nlp4ecology-1.8, abstract · [NGOÀI]
- EmeraldMind: LLM đạt 94,21% ở coverage 19,52%; EM-HYBRID 83,80% ở coverage 74,68% · [TQ] S1.11 · [NGOÀI]
- FinQA: câu từ 3 bước trở lên 22,78%; chuyên gia 91,16% · [TQ] S2.12 · [NGOÀI]
- TAT-QA: TAGOP 58,0 F1, chuyên gia 90,8 · [TQ] S2.13 · [NGOÀI]
- FEVER: 185.445 tuyên bố; 31,87% khi bắt buộc đúng bằng chứng · [TQ] S2.1 · [NGOÀI]
- G-Eval: Spearman 0,514 với người trên bài tóm tắt; thiên vị văn bản LLM · arXiv 2303.16634 · [NGOÀI]
- LLM-as-judge: GPT-4 đồng ý với người trên 80% (bài sở thích hội thoại) · [TQ] S3.9 · [NGOÀI]
- Gilardi: 2.382 tweet; hơn crowd ở 4/5 tác vụ; dưới 0,003 USD/nhãn · PNAS 120(30) / arXiv 2303.15056 · [NGOÀI]
- Turpin: accuracy giảm tới 36% trên 13 tác vụ BBH · arXiv 2305.04388 · [NGOÀI]
- RuLES: 14 kịch bản chấm bằng chương trình; "almost all current models struggle" · arXiv 2311.04235 · [NGOÀI]
- IFEval: 25 loại chỉ dẫn kiểm được, khoảng 500 prompt · arXiv 2311.07911 · [NGOÀI]
- Instruction Hierarchy: độ bền tăng mạnh trên GPT-3.5, kể cả với tấn công chưa thấy · arXiv 2404.13208 · [NGOÀI]
- ACE: +10,6% trên agent, +8,6% trên tài chính, không cần nhãn · arXiv 2510.04618 (ICLR 2026) · [NGOÀI]
- Amershi: 18 hướng dẫn; 49 người làm thiết kế; 20 sản phẩm có AI · trang Microsoft Research · [NGOÀI]
- Nielsen: 10 heuristic; 1990 cùng Molich, tinh chỉnh 1994 trên 249 vấn đề · nngroup.com · [NGOÀI]
- Krippendorff: α ≥ 0,800 dựa vào được; 0,667–0,800 kết luận tạm; dưới 0,667 bỏ · Wikipedia · [KIẾN THỨC NỀN]
- SUS: trung bình 68; trên 80,3 là A; dưới 51 là F · [TÌM] measuringu.com, Lewis 2018 · [NGOÀI][CHƯA XÁC MINH]
- Geifman: top-5 error 2% với xác suất 99,9% ở coverage khoảng 60% · [TQ] S3.14 · [NGOÀI]
- "Chúng tôi không tìm thấy bộ dữ liệu NLP tẩy xanh tiếng Việt công khai (tìm ngày 04/11/2026)" · [TÌM] · [NGOÀI][CHƯA XÁC MINH đầy đủ]

### Kiến thức nền và giả thuyết
- Công thức κ, α, ECE, temperature scaling, conformal (giả định hoán đổi được), cách tính điểm SUS · [KIẾN THỨC NỀN]
- "B-b đại diện cho tuyên bố thật" · KH §4 · [GIẢ THUYẾT], kiểm bằng cách so thứ hạng các hệ trên B-b với thứ hạng trên B-c
- "Cặp nhiễu → đúng của B-b dùng được làm gold cho gợi ý sửa" · đề xuất của R8 · [GIẢ THUYẾT]
- "Conformal theo cụm công ty khả thi khi có vài trăm gold" · [GIẢ THUYẾT]
- "SUS ≥ 70": chỉ là mục tiêu, chưa đo · `docs/04-data-ai/CHUONG_TRINH_THI_NGHIEM_VA_DU_LIEU_v3_2026-10-13.md`, mục F3 · [GIẢ THUYẾT]

---

## 4. Câu hỏi BGK dự kiến (20 câu)

*Mỗi câu gồm: trả lời 30–60 giây theo bốn bước (vấn đề → nguyên lý → GreenScan làm gì → giới hạn), câu vặn tiếp kèm trả lời ngắn, và bẫy cần tránh.*

**Q1. Đã có ClimateBERT, Greench… sao không fine-tune một mô hình "phát hiện tẩy xanh"?**
- **Trả lời:**
  - Vấn đề: "tẩy xanh" chưa có nhãn thật đã xác minh, và một bộ phân loại không chỉ ra được phép tính.
  - Nguyên lý: phát hiện khác kiểm chứng. ClimateBERT giảm lỗi 3,57–35,71% ở phân loại; Greench tăng 49% F1 lớp cảnh báo. Cả hai trả lời câu "đoạn này đáng ngờ không", chứ không trả lời "30% có khớp bảng KNK trang 39 không".
  - GreenScan: model đọc câu thành cấu trúc, code so số, luật quyết, người duyệt. Trên 87 ca ngoài mẫu sạch: 0 kết luận sai.
  - Giới hạn: độ phủ còn thấp (4B 0,138) và chưa có gold người.
- **Vặn tiếp:** "Vậy AI của em nằm ở đâu?"
  - Qwen3-4B chạy ngoại tuyến làm bộ đọc, đặt sau cờ, không đổi verdict.
  - Học trò T1 đã train nhưng chưa nối vào sản phẩm.
- **Bẫy:** đừng chê fine-tune. Nói "chưa có nhãn hay phần thưởng kiểm được nên chưa đáng làm" (bất biến: không thêm chỉ để trông AI hơn).

**Q2. Sao không chấm trên CLIMATE-FEVER / FEVER để so với thế giới?**
- **Trả lời:**
  - Vấn đề: bằng chứng ở hai bộ đó là Wikipedia tiếng Anh, còn GreenScan đối chiếu báo cáo doanh nghiệp Việt Nam và bảng số.
  - Nguyên lý: lệch miền làm số rơi mạnh; mô hình FEVER đạt 77,69% trên FEVER nhưng chỉ 38,78% trên Climate-FEVER.
  - GreenScan: dựng GS-Bench (453 ca, đáp án theo cấu trúc) và tập ngoài mẫu chia theo công ty.
  - Giới hạn: số trên GS-Bench là "trên ca dựng", không so trực tiếp với số trong paper.
- **Vặn tiếp:** "Biết đâu GS-Bench dễ hơn thực tế?" → Đúng, đó là giả thuyết. Đội kiểm bằng cách so thứ hạng các hệ trên B-b với thứ hạng trên cặp thật B-c.
- **Bẫy:** không nói "hơn baseline FEVER". Khác dữ liệu, khác ngôn ngữ, khác nhãn.

**Q3. Nhãn do Claude gán: chẳng phải AI tự chấm AI?**
- **Trả lời:**
  - Vấn đề: chưa có gold người (0/88 cặp, 0/79 câu).
  - Nguyên lý: LLM gán nhãn có thể hơn crowd (Gilardi 2023: hơn ở 4/5 tác vụ, dưới 0,003 USD/nhãn). Nhưng evaluator LLM thiên vị văn bản LLM (G-Eval) và tự đề cao (Zheng).
  - GreenScan chặn vòng tròn bằng năm lớp:
    1. Đáp án B-b do code sinh; Claude chỉ đọc IR, và bộ kiểm tất định soát (khớp 142/142).
    2. B-c gán hai lượt mù rồi phân xử.
    3. Người đọc thứ hai là model khác họ (Qwen3-32B).
    4. Người soát 14 ca.
    5. Đội đọc lại toàn bộ nhãn trước khi dùng như dữ liệu chính thức.
  - Giới hạn: T1 vừa học vừa thi trên nhãn Claude. Số 0,71–0,73 chỉ nói "bắt chước Claude được bao nhiêu".
- **Vặn tiếp:** "Bao giờ có người gán?" → 79 câu và 88 cặp đang chờ. Khi có sẽ báo α kèm CI; mục tiêu α ≥ 0,667.
- **Bẫy:** không gọi số trên nhãn Claude là "độ chính xác".

**Q4. Độ chính xác của hệ thống là bao nhiêu?**
- **Trả lời:**
  - Vấn đề: một con số gộp che hai loại sai nguy hiểm là vu oan và bỏ lọt.
  - Nguyên lý: selective prediction báo cặp rủi ro–độ phủ. EmeraldMind (WWW 2026) là ví dụ: LLM đúng 94,21% nhưng chỉ dám trả lời 19,52%.
  - GreenScan báo ba số. Ngoài mẫu sạch 87 ca: 4B precision 1,0, độ phủ 0,138; 32B precision 1,0, độ phủ 0,253; 0 vu oan, 0 bỏ lọt.
  - Giới hạn: chỉ 12–22 ca được kết luận. Kể cả 15/15 đúng thì cận dưới 95% vẫn chỉ khoảng 0,78.
- **Vặn tiếp:** "Sao không gộp thành F1?" → Vu oan một doanh nghiệp và bỏ lọt có chi phí khác nhau (bất biến 8).
- **Bẫy:** không nói "chính xác 100%" khi không kèm độ phủ và n.

**Q5. Độ phủ 9–25% thì 75–90% còn lại ai làm? Hệ thống có ích gì?**
- **Trả lời:**
  - Vấn đề: một kết luận sai về doanh nghiệp tốn hơn nhiều so với việc nhường người.
  - Nguyên lý: đánh đổi rủi ro–độ phủ. EmeraldMind tăng coverage từ 19,52% lên 74,68% thì accuracy giảm từ 94,21% xuống 83,80%.
  - GreenScan: phần còn lại vào hàng đợi có ưu tiên, kèm evidence card và số, kỳ, phạm vi đã trích sẵn. Nguồn mất độ phủ đã định vị: câu có nhiều số và bảng.
  - Giới hạn: chưa đo thời gian tiết kiệm cho người soát.
- **Vặn tiếp:** "Làm sao tăng độ phủ?" → IR v1.3 (thêm `segment`, sửa C-guard) và lớp bảng AG-3 (3/7 so với 1/7).
- **Bẫy:** không hứa con số độ phủ cho ngày 10/11.

**Q6. Điểm rủi ro 82/100 có phải xác suất tẩy xanh? Có hiệu chỉnh không?**
- **Trả lời:**
  - Vấn đề: điểm chưa hiệu chỉnh thì không đọc được như xác suất.
  - Nguyên lý: Guo 2017 cho thấy mạng hiện đại hiệu chỉnh kém; muốn hiệu chỉnh cần ECE hoặc temperature scaling trên dữ liệu có nhãn.
  - GreenScan: điểm là tổng 9 thành phần có trần, dùng để xếp hàng. Verdict, rủi ro và ưu tiên là ba thứ khác nhau (bất biến 9).
  - Giới hạn: chưa có thước "điểm 80 nghĩa là sai X%".
- **Vặn tiếp:** "Vậy abstain dựa vào đâu?" → Dựa vào đồng thuận giữa luật và bộ đọc. P(đúng) ước trên OOF theo công ty vẫn quá mảnh để dùng làm ngưỡng.
- **Bẫy:** không nói "82% khả năng tẩy xanh".

**Q7. Có dùng conformal prediction để có bảo đảm thống kê không?**
- **Trả lời:**
  - Vấn đề: người dùng muốn cam kết "sai không quá α".
  - Nguyên lý: conformal cho tập dự đoán chứa đáp án đúng với xác suất chọn trước, hữu hạn mẫu, không cần giả định phân phối (Angelopoulos & Bates). Điều kiện: có tập hiệu chỉnh có nhãn và dữ liệu hoán đổi được.
  - GreenScan: chưa dùng, vì 0 gold người và tuyên bố cùng công ty không độc lập. Hướng tiếp: conformal theo cụm công ty.
  - Giới hạn: bảo đảm conformal là bảo đảm biên (trung bình), không cho từng doanh nghiệp.
- **Vặn tiếp:** "Dùng ngay trên nhãn Claude được không?" → Được về kỹ thuật, nhưng khi đó bảo đảm chỉ là "phủ nhãn Claude", không phải phủ sự thật.
- **Bẫy:** không nói đã có "bảo đảm thống kê".

**Q8. Lời giải thích có phải lý do thật, hay LLM bịa cho hợp lý?**
- **Trả lời:**
  - Vấn đề: CoT có thể giấu lý do thật. Turpin 2023: accuracy giảm tới 36% trên 13 tác vụ mà lời giải thích không nhắc yếu tố gây lệch.
  - Nguyên lý: phân biệt trung thực với hợp lý (Jacovi & Goldberg).
  - GreenScan: lời giải thích dựng từ chính đường tính: `computed_values`, `policy_id`, câu trích kèm trang, `rule_id`. LLM không viết lý do cho verdict.
  - Giới hạn: nếu bật LLM viết báo cáo, phần văn bản đó chưa đo độ trung thực. Đề xuất kiểm bằng vị từ: mỗi con số trong lời giải thích phải có trong `computed_values`.
- **Vặn tiếp:** "Người dùng có hiểu không?" → Chưa đo; đó là mục F3 (SUS và nhiệm vụ).
- **Bẫy:** không nói "giải thích giúp kiểm toán viên chính xác hơn". Chưa đo, và Bansal 2021 [TQ] cho thấy giải thích có thể tăng tin mù.

**Q9. Đã có RAG sao còn sai? Sao không để LLM viết kết luận như chatbot?**
- **Trả lời:**
  - Vấn đề: RAG đưa đúng tài liệu, nhưng model vẫn có thể tính sai hoặc hiểu sai.
  - Nguyên lý: RAG (Lewis 2020) ghép bộ nhớ tham số với phi tham số. Nhưng với câu từ 3 bước suy luận, FinQA chỉ đạt 22,78%; TAT-QA đạt 58,0 F1 so với chuyên gia 90,8.
  - GreenScan: "R" chỉ tìm ứng viên; số học do code. Lỗi đã đo của 32B là tự thêm "ngàn" (11/11 kết luận sai); `ground()` hạ CONTRADICTED sai từ 7 xuống 1.
  - Giới hạn: recall truy xuất đo trên gold nhỏ chỉ là cận dưới.
- **Vặn tiếp:** "Vậy LLM vô dụng?" → Không. LLM làm việc nó giỏi nhất: đọc câu thành cấu trúc.
- **Bẫy:** không gọi GreenScan là "chatbot RAG".

**Q10. Đã đánh giá bằng RAGAS hay LLM-as-a-judge chưa?**
- **Trả lời:**
  - Vấn đề: RAGAS không cần đáp án; nó đo độ liên quan của ngữ cảnh, độ trung thực và chất lượng câu trả lời.
  - Nguyên lý: chấm không tham chiếu đo tính nhất quán, không đo đúng sai so với thế giới. Judge LLM có thiên vị vị trí, độ dài, tự đề cao; G-Eval chỉ đạt Spearman 0,514 với người.
  - GreenScan: số chính đo trên đáp án theo cấu trúc. RAGAS hợp để kiểm lời giải thích sau này.
  - Giới hạn: chưa có số RAGAS.
- **Vặn tiếp:** "Thế ai chấm?" → Code chấm theo đáp án theo cấu trúc; người chấm khi có gold.
- **Bẫy:** không bịa điểm RAGAS.

**Q11. Ngân hàng hay doanh nghiệp muốn thêm quy định nội bộ: LLM có tuân thủ không, kiểm thế nào?**
- **Trả lời:**
  - Vấn đề: LLM tuân thủ quy tắc kém. RuLES (14 kịch bản, chấm bằng chương trình) thấy hầu hết model không theo được, và tấn công đơn giản làm tăng mạnh tỷ lệ hỏng.
  - Nguyên lý: quy tắc phải kiểm được bằng chương trình (IFEval: 25 loại chỉ dẫn kiểm được).
  - GreenScan: quy tắc là policy-as-code: điều kiện tường minh, trỏ tới điều khoản nguồn, có ngày hiệu lực, người ký và unit test. Quy tắc chỉ ACTIVE khi qua 4 cổng. Lúc chạy, hệ thống chỉ thực thi quy tắc, không để LLM diễn giải luật.
  - Giới hạn:
    - Gói quy tắc hiện tại áp được cho 0/156 tuyên bố (F5).
    - Chưa có giao diện để người không lập trình tự thêm quy tắc [CHƯA XÁC MINH trong Studio].
- **Vặn tiếp:** "Tài liệu nội bộ là văn bản tự do thì sao?" → LLM soạn nháp quy tắc → người duyệt → test → nâng phiên bản. Đây là thiết kế, chưa nối.
- **Bẫy:** không nói "LLM tự đọc luật và áp dụng".

**Q12. Hệ thống có "trí nhớ" không? Có tự học từ phản hồi không?**
- **Trả lời:**
  - Vấn đề: agent cần nhớ quy tắc và kinh nghiệm. MemGPT dùng bộ nhớ phân tầng; ACE cho playbook tự tiến hoá (+10,6% agent, +8,6% tài chính) nhưng cảnh báo context collapse.
  - Nguyên lý: trong kiểm toán, bộ nhớ phải truy vết được và tái lập được.
  - GreenScan: bộ nhớ có phiên bản, chỉ ghi thêm, và manifest ghi rule pack cùng model/prompt. Phản hồi của người soát chỉ thành nhãn vàng hoặc quy tắc mới sau khi qua cổng; hệ thống không tự sửa mình.
  - Giới hạn: chưa có vòng học từ phản hồi. Nếu theo kiểu ACE thì playbook chỉ đưa ra gợi ý, phải có người ký.
- **Vặn tiếp:** "Thế có chậm thích nghi không?" → Có, đó là cái giá đổi lấy khả năng chạy lại 6 tháng sau vẫn ra cùng kết quả.
- **Bẫy:** không nói "hệ thống tự học".

**Q13. PDF có thể chứa câu lệnh lừa AI. Xử lý thế nào?**
- **Trả lời:**
  - Vấn đề: Greshake 2023 cho thấy injection gián tiếp xoá ranh giới dữ liệu–chỉ dẫn; nhóm này đã tấn công được Bing Chat GPT-4.
  - Nguyên lý: theo thứ bậc chỉ dẫn (Wallace 2024), nội dung của bên thứ ba ở cấp thấp nhất.
  - GreenScan:
    - Chunk nghi ngờ bị gắn `suspicious_instruction` và loại khỏi verifier.
    - Bộ đọc chỉ trả JSON IR có schema; `ground()` buộc số phải có trong câu gốc.
    - Quan trọng nhất: LLM không quyết verdict.
  - Giới hạn: bộ lọc dựa trên mẫu, injection viết khéo có thể lọt.
- **Vặn tiếp:** "Injection làm bộ đọc trả số sai thì sao?" → `ground()` loại số không có trong câu, và luật với bộ đọc phải đồng thuận mới kết luận.
- **Bẫy:** không nói "miễn nhiễm".

**Q14. Sao chọn model 4B mà không dùng model lớn nhất?**
- **Trả lời:**
  - Vấn đề: dữ liệu doanh nghiệp nhạy cảm; demo chạy laptop CPU ở chế độ ngoại tuyến.
  - Nguyên lý: hiệu ứng quy mô có thật. Độ phủ ngoài mẫu của 4B / 8B / 14B / 32B là 0,126 / 0,220 / 0,256 / 0,329. Nhưng an toàn mới là cổng: luật + 32B trượt cổng trên G (1 SUPPORTED sai), còn luật + 4B qua.
  - GreenScan: bản 4B Q4 cục bộ khớp 0,963 với bản Kaggle và có 0 kết luận sai trên G.
  - Giới hạn: thời gian đọc trên laptop chưa đo; trên T4 là 1,7 giây/câu.
- **Vặn tiếp:** "Greench cũng dùng 4B?" → Greench phân loại đoạn; 4B của GreenScan chỉ đọc số.
- **Bẫy:** không nói chung chung "4B tốt hơn 32B".

**Q15. Độ dễ dùng đo thế nào? Có điểm SUS chưa?**
- **Trả lời:**
  - Vấn đề: công cụ tốt mà kiểm toán viên không dùng thì vô ích.
  - Nguyên lý:
    - SUS gồm 10 câu, thang 0–100, trung bình khoảng 68 [CHƯA XÁC MINH].
    - 10 heuristic của Nielsen.
    - 18 hướng dẫn Human-AI của Amershi, kiểm với 49 người làm thiết kế trên 20 sản phẩm.
  - GreenScan: kế hoạch đo SUS với 5–8 người (sinh viên kế toán, kiểm toán viên), mục tiêu ≥ 70, kèm tỷ lệ hoàn thành và thời gian hoàn thành nhiệm vụ.
  - Giới hạn: tới 01/11 chưa có kết quả.
- **Vặn tiếp:** "5 người có đủ không?" → Đủ để tìm vấn đề lớn, không đủ để kết luận thống kê; sẽ báo khoảng tin cậy.
- **Bẫy:** không bịa điểm SUS; không nói "người dùng hài lòng".

**Q16. Giao diện giúp người soát tránh tin mù vào AI thế nào?**
- **Trả lời:**
  - Vấn đề: lời giải thích có thể làm người dùng tin cả khi AI sai (Bansal 2021 [TQ]).
  - Nguyên lý: hướng dẫn Human-AI; nội dung chi tiết từng hướng dẫn là [KIẾN THỨC NỀN], vì trang đã mở không liệt kê.
  - GreenScan:
    - Mỗi kết luận có trang trích và highlight trên PDF.
    - Hiện `relation_method` để biết kết luận đến từ số học, cue hay LLM.
    - INSUFFICIENT và abstain hiện rõ.
    - Không có kết luận cấp doanh nghiệp (bất biến 1).
    - Gợi ý sửa không bao giờ đưa số mới.
  - Giới hạn: chưa đo mức tin quá đà.
- **Vặn tiếp:** "Người soát lười, bấm chấp nhận hết thì sao?" → Kết luận đã quyết vẫn cần bằng chứng; gợi ý sửa chỉ là mẫu có chỗ trống.
- **Bẫy:** không nói "AI thay kiểm toán viên".

**Q17. Đồng thuận gán nhãn bao nhiêu là đủ? Dùng κ hay α?**
- **Trả lời:**
  - Vấn đề: nhãn kiểm chứng khó, người cũng bất đồng: environmental claims α = 0,47; Climate-FEVER α = 0,334; FEVER κ = 0,684.
  - Nguyên lý: κ dùng cho hai người; α dùng cho nhiều người, dữ liệu thiếu và nhãn thứ bậc. Ngưỡng của Krippendorff là 0,800 và 0,667.
  - GreenScan sẽ báo α kèm CI, percent agreement và ma trận nhầm lẫn theo lớp.
  - Giới hạn: chưa có số vì chưa có gold người.
- **Vặn tiếp:** "Nếu α thấp thì sao?" → Báo trung thực kèm agreement từng lớp, sửa hướng dẫn gán nhãn rồi gán lại.
- **Bẫy:** không hứa κ ≥ 0,8; không trộn thang κ với thang α.

**Q18. Có dữ liệu tiếng Việt không? Các em có phải người đầu tiên?**
- **Trả lời:**
  - Tìm ngày 04/11 không thấy bộ dữ liệu NLP tẩy xanh tiếng Việt công khai.
  - Có các nguồn gần: ViFactCheck (tin tức, MIT), ISE-DSC01; dự án VinUni GREEN-X dự kiến phát hành dữ liệu minh bạch ESG; một nghiên cứu kinh tế lượng trên 33 doanh nghiệp.
  - GreenScan tự dựng GS-Bench từ báo cáo công khai.
  - Giới hạn: phạm vi tìm có hạn.
- **Vặn tiếp:** "Sao không lấy dữ liệu tiếng Anh dịch sang?" → Khác miền và khác giấy phép (NC); chỉ dùng để tham khảo.
- **Bẫy:** không nói "chưa ai làm". Nói "chúng tôi không tìm thấy… tính đến 11/2026".

**Q19. Thương mại hoá thì dùng được dữ liệu công khai nào?**
- **Trả lời:**
  - environmental_claims là CC BY-NC-SA; climateBUG là CC BY-NC-ND và cấm chia sẻ lại; CLIMATE-FEVER ghi "unknown"; AVeriTeC và QuanTemp là NC.
  - FinQA ghi cc-by-4.0 trên thẻ HF; TAT-QA có hai nguồn mâu thuẫn.
  - GreenScan: dữ liệu NC chỉ dùng để đánh giá và nghiên cứu; dữ liệu của sản phẩm là GS-Bench tự dựng từ báo cáo công khai cộng nhãn của đội.
  - Giới hạn: chưa có tư vấn pháp lý về giấy phép.
- **Bẫy:** không nói "dữ liệu mở thì dùng thoải mái".

**Q20. Benchmark tự sinh bằng nhiễu có kiểm soát có dễ quá không? Gợi ý sửa tuyên bố được kiểm thế nào?**
- **Trả lời:**
  - Vấn đề: dữ liệu tự sinh dễ mắc lỗi của bộ sinh. Đã gặp: 14 ca PV Power; 37% số ca trong G là `other_env`; năm bịa ở v1.2.
  - Nguyên lý: cặp gần giống nhưng khác kết luận đo được độ nhạy (kiểu VitaminC).
  - GreenScan:
    - Ghi errata, lọc thành tập sạch v1.3 (87 ca), đăng ký dự đoán trước khi chạy.
    - Gợi ý sửa của Studio có 4 loại mẫu và không bao giờ đưa số mới.
  - Đề xuất: mỗi ca nhiễu của B-b đều có bản đúng gốc, nên có sẵn dữ liệu "sai → sửa đúng" kèm đáp án. Kiểm một gợi ý bằng cách chạy lại verifier trên câu đã sửa.
  - Giới hạn: chưa có số đo chất lượng gợi ý sửa.
- **Bẫy:** không nói "gợi ý sửa đã được kiểm chứng".

---

## 5. Mâu thuẫn giữa tài liệu, số đã cũ, điều không được nói

### 5.1 Mâu thuẫn giữa các tài liệu
1. **Gold người.**
   - Tổng quan 05/10, mục 7(c) phát biểu 6, viết: "Gold do người gán, có κ và adjudication; chúng tôi không dùng LLM tự chấm".
   - Hiện trạng 31/10: 0 gold người; dữ liệu là nhãn bạc của Claude; T1 học trên nhãn Claude.
   - **Không dùng câu đó nữa.**
2. **Yêu cầu của người dùng 04/11 so với quy tắc đo.**
   - Người dùng cho phép "xem nhãn Claude như dataset bình thường", vì chính họ sẽ đọc lại.
   - `KE_HOACH…` §4 và D-2026-10-16-01 lại cấm gọi số trên nhãn Claude là "độ chính xác", và cấm dùng nhãn Claude để tháo chốt `llm_stance_decisive`.
   - Cách dung hoà:
     - Dùng nhãn như dữ liệu.
     - Khi trình bày, ghi nguồn là "nhãn Claude, đã qua người soát (n = …)".
     - Không dùng các nhãn này để đổi verdict của sản phẩm.
3. **File 100 câu BGK, bản trước Bán kết, có số cũ:**
   - "HPG 210 claim, CONTRADICTED 4%", trong khi lượt 22/10 có 156 tuyên bố: 153 PARTIAL, 2 S, 1 INSUFF.
   - "Gold hiện 5, mục tiêu 60 trước 10/10", trong khi hiện có 0/88 cặp, 0/79 câu.
   - "Recall 1,0 trên golden 4 case".
   - "233 test · 21 bẫy verdict", trong khi cổng 06/11 dùng "17 bẫy xanh".
   - Cần thống nhất trước khi đưa lên slide.
4. **environmental_claims:** mô tả trong card ghi 2.400/300/300, viewer hiện 2.117/265/265 (tổng 2.647, khớp paper). Nói **2.647**.
5. **CLIMATE-FEVER:** "publicly available" không có nghĩa là đã có giấy phép rõ; HF ghi "unknown".
6. **TAT-QA:** README ghi CC BY 4.0, còn paper ghi phi thương mại [TÌM]. Chưa xác minh.
7. **SUS:** năm tạo thang là 1986, bài tham chiếu năm 1996. Trích "Brooke (1996)" là tham chiếu bài, không phải năm tạo.
8. **Greench-v1:** tóm tắt tìm kiếm gọi là "ACL 2026", nhưng thực tế là workshop NLP4Ecology 2026, do ELRA xuất bản. Không nói "bài ACL".
9. **ClimaText:** số câu chỉ có từ tóm tắt tìm kiếm, ghi [CHƯA XÁC MINH].

### 5.2 Số đã cũ ngay trong kế hoạch 31/10–01/11 (chỉ dùng bản đã sửa)
- "4B, 14B, 32B qua cổng" (báo cáo 14:15/14:35) đã sửa lúc 22:40: với v1.1 **chỉ 8B qua**; với v1.2 thì 8B và 32B có 0 vu oan, 14B có 1.
- "Không có hiệu ứng quy mô": dự đoán **sai**.
- "4B mất độ phủ vì đọc năm": **rút lại** ngày 01/11.
- Tập G (162 ca) có 37% `other_env` và năm bịa, nên ưu tiên trích **v1.3 sạch (87 ca)**. Số AG-2 trên G vẫn dùng được nếu ghi rõ là tập G.
- "Độ phủ 4B 0,437" là số **trong mẫu**, không phải số ngoài mẫu.
- Groq đã gỡ `qwen/qwen3-32b`; đội dùng `gpt-oss-120b`, và chỉ cho báo cáo công khai.
- Khoá FPT bị 401, nên chế độ `cloud` (GLM-5.2) không chạy; demo dùng `offline`.
- Bộ đọc Q4 "đủ điều kiện đặt sau cờ", nhưng cổng 06/11 còn thiếu ba việc: đo thời gian trên laptop, 17 bẫy, và test bất biến khi bật `QUANTUM_VERIFY=dual`. **Không nói là đã bật trong sản phẩm.**

### 5.3 Điều không được nói
- "GreenScan phát hiện / chứng minh doanh nghiệp X tẩy xanh" hay "vi phạm pháp luật". Hệ thống kiểm chứng từng tuyên bố, không phán xét doanh nghiệp (bất biến 1).
- "Độ chính xác 100%" khi không kèm độ phủ, n và khoảng tin cậy; hoặc gọi số trên ca dựng hay nhãn Claude là "độ chính xác".
- "LLM xác minh tuyên bố", "AI đọc hiểu toàn bộ báo cáo", "LLM tuân thủ 100% quy tắc", "hệ thống tự học quy tắc".
- "Có bảo đảm thống kê / conformal", "điểm rủi ro là xác suất", "đã hiệu chỉnh".
- Bất kỳ điểm SUS, RAGAS hay κ/α nào: **chưa đo**.
- "Lời giải thích giúp kiểm toán viên chính xác hơn": chưa có thí nghiệm người dùng.
- "Dùng ClimateBERT / CLIMATE-FEVER trong sản phẩm": không dùng.
- "Chưa ai nghiên cứu tẩy xanh tiếng Việt". Chỉ nói "chúng tôi không tìm thấy bộ dữ liệu NLP công khai tính đến 11/2026".
- "Miễn nhiễm prompt injection". Chỉ nói "thiệt hại bị giới hạn vì LLM không quyết verdict".
- Chuyển số của paper sang GreenScan, ví dụ "ACE +10,6% thì GreenScan cũng sẽ tăng", hay "Gilardi chứng minh nhãn Claude đúng".
- "Dữ liệu công khai dùng thương mại được" với các bộ NC/ND hoặc "unknown".
