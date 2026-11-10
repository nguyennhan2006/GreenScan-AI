# Kế hoạch 31/10 → 10/11: mượn kiến trúc agent từ ZAIC, thí nghiệm trên Kaggle, viết luận văn cho câu hỏi production

*Viết 31/10/2026, sau Bán kết. Chung kết 10/11/2026. Người duyệt: Nhân. Trạng thái: **đã duyệt 31/10** (quyết định ở mục 9).*

## 0. Kết luận ngắn

- **Làm được, với ba điều kiện.**
  1. **Chỉ mượn từ ZAIC những thành phần trị được lỗi đã đo.** Mỗi thành phần mượn phải gắn với một lỗi đã đo của GreenScan, vì bất biến kiến trúc cấm thêm agent hay fine-tune "cho trông AI hơn" (`ARCHITECTURE_INVARIANTS.md`).
  2. **Phải có thước đo trước khi chạy.** GreenScan chưa có nhãn người (đã kiểm 31/10: 0/88 cặp trong `data/gold/sessions/`, 0/79 câu trong cả ba gói T1 của Nhân, Quỳnh và Thảo). Việc đầu tiên vì thế là dựng **bộ đo có đáp án theo cấu trúc** (mục 4); ZAIC không cần bước này vì đã có bộ chấm của BTC.
  3. **Sản phẩm của buổi demo không đổi kết luận trước Chung kết.** Cái gì qua cổng thì vào sản phẩm dưới dạng **trợ giúp người soát**, sau một cờ cấu hình, và không đổi verdict. Lý do: D-2026-10-16-01 cấm dùng nhãn Claude để tháo chốt `llm_stance_decisive`.
- **Sáu thí nghiệm** `AG-0` … `AG-6` (mục 5) chạy trên **4 tài khoản Kaggle dành riêng** (mục 6). Ước tính khoảng 25–40 giờ GPU T4, tức dưới 1/3 quota tuần của 4 tài khoản.
- **Mười luận văn** `PQ-01` … `PQ-10` trả lời các câu hỏi production (mục 7). Mỗi bài theo khung 10 điểm. Bốn bài có dấu ★ phải xong trước 08/11.

## 1. Vì sao không bê nguyên kiến trúc ZAIC

| | ZAIC (LifeMate / DataMate) | GreenScan |
|---|---|---|
| Đáp án | BTC cho gold, có bộ chấm tự động (`score_lifemate.py`, `answers.jsonl` 3 000 câu) | Chưa có gold người; nhãn Claude là **bạc** |
| Sai thì sao | Mất điểm | Quy kết sai một doanh nghiệp: hậu quả pháp lý và uy tín |
| Ràng buộc | Tham số < 6B / ≤ 15B, 30 s / mẫu | Laptop CPU ở chế độ ngoại tuyến; 10 bất biến kiến trúc |
| Thứ được tối ưu | Điểm trung bình | Độ chính xác **trên phần dám kết luận**, và biết lúc nào phải nhường người |

Vì vậy mượn **cách làm** (đo xem điểm mất ở đâu, lớp tất định, hai đường kiểm chéo, nhãn tìm bằng thực thi, kiểm định giữ hẳn một nhóm ra ngoài), còn **mục tiêu** thì giữ của GreenScan.

## 2. Lỗi đã đo của GreenScan (điểm xuất phát)

| # | Lỗi | Số đo | Nguồn |
|---|---|---|---|
| F1 | Kết luận phẳng: gần như mọi tuyên bố đều "khớp một phần" | HPG: 153 PARTIALLY_SUPPORTED, 2 SUPPORTED, 1 INSUFFICIENT trên 156; hàng đợi 9/172 | lượt `c892c13727c24bb9` (22/10), giống lượt demo `cd5a82e3` |
| F2 | Luật phủ thấp | 51 ca dựng: luật quyết định 8/32 (đúng 6) và 3/19 (đúng 3); LLM 29–32/32 | `docs/04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md` |
| F3 | Bảng PDF bị dàn phẳng, nên **mọi** model báo SUPPORTED sai trên cùng hai ca (N02, N05, bảng GHG trang 39) | 4/4 model ≥ 26B | như trên |
| F4 | Lỗi lớp chuẩn hoá: cường độ so với tuyệt đối (Q1), công ty mẹ so với tập đoàn (Q2), ngưỡng 0,35 che chênh 9–25 % (Q3), bỏ sót "sử dụng … nước" (Q4), không cộng ngang tổng của tuyên bố (Q5) | 5 lỗi | `ISSUES_REGISTER_2026-09.md` (10/10) |
| F5 | Pháp lý: 0 quy tắc áp được trên 156/156 tuyên bố | gói `vn-green-v0.1-draft` chưa có quy tắc cho phát thải, BVMT, phân loại xanh | lượt 22/10 |
| F6 | Bằng chứng chỉ có nguồn nội bộ (`has_independent: False`) | 2 nguồn nội bộ | lượt 22/10 |
| F7 | Không có gold người | 0/88 cặp, 0/79 câu | kiểm 31/10 |

Học trò T1 (e5-base) đạt macro-F1 0,71–0,73 trên **nhãn Claude**, kiểm định chéo theo công ty, n = 1 217, 3 seed (`training/runs/kaggle_t1_v3/results.json`), nhưng **chưa nối vào sản phẩm**.

## 3. Bản đồ mượn: thành phần ZAIC → lỗi GreenScan → thí nghiệm

| Thành phần ZAIC | Ý chính | Trị lỗi | Thí nghiệm |
|---|---|---|---|
| "Điểm đang mất ở đâu" + phép thử oracle (PIPE-T1-08 oracle, R2 ép gold tới lỗi đầu tiên) | Thay từng tầng bằng đáp án đúng để biết tầng nào làm mất nhiều nhất, **trước khi** chọn hướng sửa | chọn giữa F2 / F3 / F4 / truy xuất | **AG-0** |
| DataMate D1 đường A: LLM dịch câu hỏi → IR, thư viện luật tất định tính | Việc của LLM thu lại còn **hiểu câu**; số học, đơn vị, kỳ do code | F2, F4 | **AG-1** |
| LifeMate L1 lớp luật tất định: JSON ràng buộc, chuẩn hoá ngày giờ / tiền / số, đối chiếu tên | Phần dễ sai nhưng xác định được thì giao cho code | F4 | trong **AG-1** |
| DataMate D1 quyết định: hai đường độc lập, cổng đồng thuận, abstain khi P(đúng) ước trên OOF ≤ ngưỡng | Kiểm chéo hai đường khác nhau cho tín hiệu tin cậy tốt hơn tự nhất quán (text-to-SQL: AUROC 0,82 so với 0,61–0,68 [NGOÀI]) | F1 | **AG-2** |
| DS-STAR bộ phân tích file; DataMate chuẩn hoá shop (khoá nối, kiểu, kiểm tổng) | Dựng cấu trúc dữ liệu trước rồi mới hỏi | F3 | **AG-3** |
| LifeMate SFT trên quỹ đạo + DataMate "nhãn IR tìm bằng thực thi" | Model nhỏ tinh chỉnh vượt model lớn zero-shot (ZAIC T1_03: Qwen3-4B QLoRA 0,215 → 0,485, CI95 [0,19; 0,34] [ĐÃ THỰC NGHIỆM, ZAIC]) | ngoại tuyến hoàn toàn (L2) | **AG-4** |
| PIPE-T1-08: e5 tinh chỉnh + BM25, RRF, chọn k theo recall mục tiêu | Chọn k bằng số đo, không chọn theo cảm tính | truy xuất (v3 C1) | **AG-5** |
| LifeMate vòng ReAct, `validate()` trước `call()`, tối đa 8 bước | Agent tìm bằng chứng nhiều bước, mỗi lệnh gọi được kiểm | bằng chứng ở trang hoặc tài liệu khác | **AG-6** (có điều kiện) |
| LifeMate kiểm định leave-apps-out | Chọn theo nhóm **chưa thấy** | tổng quát hoá | mọi AG: **leave-company-out** |

**Không mượn:**
- RL / GRPO: không có phần thưởng kiểm được nếu thiếu gold, và quá tốn trên T4.
- Self-consistency bằng lấy mẫu: tín hiệu yếu [NGOÀI].
- Đa tác tử tự do: trái bất biến 5 (số học là của code) và mục "Những điều từ nay không được làm".
- Mọi phần về audio.

## 4. Thước đo khi chưa có gold người: bộ `GS-Bench v1`

| Tầng | Nội dung | Cỡ | Nhãn | Dùng để |
|---|---|---|---|---|
| B-a | 51 ca dựng của size ladder (32 sạch + 19 trên trang HPG thô) | 51 | đáp án theo cấu trúc | so với số đã có 10/10 |
| B-b | **Tuyên bố sinh từ bảng**: lấy một ô bảng thật (chỉ số, giá trị, đơn vị, kỳ, phạm vi) → dựng tuyên bố đúng → LLM diễn đạt lại → **nhiễu có kiểm soát** đổi giá trị / đơn vị / kỳ / Scope / mẹ–tập đoàn / mục tiêu–thành tích / cường độ–tuyệt đối | khoảng 600 (≥ 8 công ty, ≥ 3 ngành) | đáp án theo cấu trúc, kèm **IR gold** | AG-0, AG-1, AG-2, AG-4; v3 D2 |
| B-c | Cặp tuyên bố–đoạn thật, nhãn Claude 2 lượt mù + phân xử (`training/claude_pairs.py`) | khoảng 800 | bạc | AG-2, AG-5 |
| B-d | Gold người khi có (79 câu T1 lô 1; 88 cặp) | ≤ 167 | vàng | kết luận cuối, nếu kịp |

**Quy tắc đo** (lấy từ ZAIC và từ `MEASUREMENT_PROTOCOL_2026-09-29.md`):
- Chia theo **công ty**: train/dev không bao giờ chung công ty với test. Khoảng tin cậy dùng bootstrap theo công ty.
- Ngưỡng và dự đoán **ghi trước khi chạy** vào `configs/measurement_decisions.yaml`, khối `agentic_v1`.
- Số trên B-b ghi là "trên ca dựng"; số trên B-c ghi là "trên nhãn Claude". Không bao giờ gọi là "độ chính xác" trên slide. Câu "B-b đại diện cho tuyên bố thật" là **[GIẢ THUYẾT]**, kiểm bằng cách so thứ hạng các hệ trên B-b với thứ hạng trên B-c.
- Chỉ số chính, theo bất biến 8:
  - **precision trên phần dám kết luận** (SUPPORTED / CONTRADICTED);
  - **độ phủ**: tỷ lệ dám kết luận;
  - **số kết luận sai nguy hiểm**: CONTRADICTED sai (vu oan), SUPPORTED sai (bỏ lọt).
  - Không dùng một con số gộp.

## 5. Phiếu thí nghiệm

Mỗi phiếu nằm ở `experiments/AG-*/README.md`, ghi đủ dự đoán **trước** khi đẩy. Dưới đây là bản tóm tắt.

### AG-0 · Điểm mất ở đâu (CPU, máy nhà, 01–02/11)
- **Câu hỏi:** trên GS-Bench B-a + B-b, verdict sai đến từ tầng nào: tìm đoạn, cấu trúc bảng, ánh xạ tuyên bố ↔ số, hay so sánh?
- **Cách làm:** chạy verifier hiện tại 4 lần, mỗi lần thay một tầng bằng đáp án đúng: đoạn gold; bảng gold có cấu trúc; IR gold; cả ba. Đo độ phủ, precision và số kết luận sai.
- **Dự đoán:** phần lớn chênh nằm ở **bảng + ánh xạ** (F3, F4), không nằm ở truy xuất. Lý do: size ladder thấy mọi model cùng sai trên bảng dàn phẳng.
- **Cổng quyết định:** nếu "đoạn gold" chiếm ≥ 30 % phần chênh thì mở AG-6; nếu < 10 % thì hạ AG-5 xuống sau Chung kết.

### AG-1 · IR + thư viện so sánh tất định (Kaggle GPU, 01–04/11)
- **Cách làm:**
  - LLM nhỏ chạy tại chỗ sinh IR của tuyên bố bằng **giải mã JSON ràng buộc** (vLLM guided JSON). IR gồm: chỉ số, giá trị, đơn vị, kỳ, năm gốc, phạm vi tổ chức, Scope, loại (thành tích / mục tiêu / cường độ / tuyệt đối / tỷ trọng / thay đổi), hướng so sánh.
  - Bằng chứng lấy từ ô bảng (AG-3) hoặc câu có số.
  - Thư viện `compare()` áp bất biến 4–6: lệch một chiều thì **cấm** CONTRADICTED; mục tiêu không chứng minh thành tích; làm tròn theo độ chính xác đã công bố.
  - Bộ chuẩn hoá số tiếng Việt ("1.234,5", "triệu", "nghìn tấn", TOE, tCO₂e, kWh) viết bằng code và có test.
- **Thang model** (kiểm ngày + license qua HF API trước khi chạy): Qwen3-0.6B, Qwen3-1.7B, Qwen3-4B-Instruct-2507, Qwen3-8B, gemma-3-12b-it (hoặc bản gemma-4 nhỏ nếu có). Mốc so sánh: luật hiện tại; số GLM-5.2 / gemma-4-31B của size ladder.
- **Chỉ số:** độ đúng từng trường IR (B-b có IR gold); precision / độ phủ / kết luận sai theo loại nhiễu.
- **Dự đoán:**
  - 4B có độ phủ ≥ 2 lần luật, với số kết luận sai ≤ luật;
  - 1.7B kém 4B ≥ 10 điểm độ đúng IR;
  - không có hiệu ứng cỡ từ 8B trở lên.

### AG-2 · Hai đường + cổng đồng thuận + abstain hiệu chỉnh (CPU, 04–05/11)
- **Hai đường:** đường 1 là luật hiện tại hoặc che-số L1 (`OFFLINE_TUNG_PHAN_2026-10-10.md`); đường 2 là AG-1.
- **Bảng quyết định:**
  - hai đường cùng kết luận: giữ;
  - lệch nhau, hoặc chỉ một đường kết luận: tra P(đúng) của xô (loại tuyên bố × trạng thái khớp) ước trên OOF theo công ty. Kết luận khi cận dưới CI95 > 0,9 với CONTRADICTED, > 0,8 với SUPPORTED (theo ngưỡng D1 đã đăng ký); ngược lại thì chuyển người.
- **Đầu ra:** đường độ phủ – precision (v3 B6), so với luật một mình.
- **Dự đoán:** ở cùng precision, độ phủ tăng từ khoảng 25 % (luật) lên ≥ 50 %, và F1 bớt phẳng.
- **Vào sản phẩm trước Chung kết** chỉ dưới dạng: huy hiệu "hai đường khớp / lệch" và thứ tự hàng đợi. **Verdict không đổi** (D-2026-10-16-01).

### AG-3 · Dựng bảng có cấu trúc từ PDF (CPU trước, GPU nếu cần, 01–04/11)
- **So:** PyMuPDF `find_tables`, pdfplumber, Docling (GPU), Table Transformer. **Tự kiểm bằng cộng ngang/dọc:** tổng phải bằng tổng các thành phần; không qua thì không dùng bảng đó để kết luận.
- **Gold:** 12–15 bảng (GHG, năng lượng, nước, chất thải) của 4–5 công ty, kiểm bằng tay trên ảnh trang. Claude dựng bảng, người soát; nếu người không kịp thì 2 lượt Claude mù và ghi nhãn bạc.
- **Chỉ số:** độ đúng ô, đúng hàng–cột, tỷ lệ qua kiểm tổng; hạ nguồn là số SUPPORTED sai trên ca kiểu N02 / N05.
- **Dự đoán:** kiểm tổng chặn ≥ 80 % bảng dựng sai; SUPPORTED sai trên N02 / N05 về 0.

### AG-4 · Parser IR nhỏ chạy ngoại tuyến (Kaggle GPU, 04–07/11; **chỉ chạy nếu** AG-1 cho 1.7B kém 4B ≥ 10 điểm)
- **Dữ liệu:**
  - IR của thầy lớn (gemma-4-31B / GLM-5.2 qua FPT, chỉ tài liệu công khai, đã che số; hoặc Claude) **giữ lại khi chạy thư viện ra đúng đáp án theo cấu trúc** (nhãn tìm bằng thực thi);
  - IR gold của B-b.
- **Huấn luyện:** QLoRA Qwen3-1.7B và Qwen3-4B. Kiểm định leave-company-out và leave-sector-out.
- **Đo thêm:** tốc độ trên laptop i7-1355U với llama.cpp Q4.
- **Dự đoán:** 1.7B tinh chỉnh ≥ 8B zero-shot về độ đúng IR; ≤ 3 s / tuyên bố trên CPU.

### AG-5 · Truy xuất có số đo (Kaggle GPU, 03–06/11; ưu tiên theo AG-0)
- **So:** `lite` (BM25 + char n-gram, RRF) với + multilingual-e5 tinh chỉnh trên cặp bạc (B-c, chia theo công ty) và với + reranker gte-multilingual.
- **Chỉ số:** recall@k; k nhỏ nhất đạt recall 95 %.
- **Nối với v3 C1:** ngưỡng +10 điểm đã đăng ký.

### AG-6 · Agent tìm bằng chứng nhiều bước (có điều kiện, sau AG-0)
- **Công cụ:** `search(q, năm)`, `read_table(trang)`, `compare(IR)`.
- **Kiểm lệnh:** mỗi lệnh gọi qua `validate()` (trang tồn tại, năm hợp lệ).
- **Ngân sách:** tối đa 6 bước. Kết luận cuối vẫn đi qua thư viện AG-1.
- **Chỉ làm khi** AG-0 cho thấy tìm đoạn chiếm ≥ 30 % phần chênh; nhiều khả năng để sau Chung kết.

## 6. Kaggle: tài khoản và cách chạy

- **Tài khoản GreenScan** (người dùng 31/10: "chọn trong số acc rảnh và acc dự phòng trong các .env"):
  - GreenScan dùng **12 tài khoản dự phòng** trong `C:\Users\ASUS\.kaggle\acc_kaggle_du_phong.env`. ZAIC không dùng file này, nên hai project không tranh phiên GPU (mỗi tài khoản tối đa 2 phiên cùng lúc).
  - Kiểm 31/10: cả 12 token OK, mỗi tài khoản còn 30 giờ, đặt lại 07/11 07:00 giờ VN.
  - Phân vai:

    | Vai | Tài khoản |
    |---|---|
    | A (AG-1) | `thanhtruc02` |
    | B (AG-1) | `vantiennhuannguyen` |
    | C (AG-3, AG-5) | `lnguynmaiphng` |
    | D (AG-4) | `hdonqu` |
    | Dự phòng | `rehoanzun`, `letranchauanh`; 6 tài khoản còn lại để trống |

  - Chỉ khi cả 12 tài khoản đều bận mới mượn tài khoản ít dùng của `upar_accounts.env` (`berryyusilee`, `hthlin`), và phải ghi vào `Zalo AI challenge/docs/RUNS.md` trước khi đẩy.
  - Lượt đầu mỗi tài khoản là smoke test in `torch.cuda.is_available()`, vì có tài khoản từng chạy trên máy không GPU dù đẩy với `--gpu`.
- **Công cụ:** `tools/kaggle/kapi.py`, chép từ ZAIC 31/10.
  - Mặc định đọc file dự phòng; đổi file bằng biến `GREENSCAN_KAGGLE_ENV`.
  - Nhật ký ở `tools/kaggle/kapi_runs.jsonl`.
  - Token không bao giờ in hay ghi ra.
- **Dữ liệu đẩy lên:**
  - **chỉ** báo cáo công khai, ca dựng và nhãn Claude;
  - dataset luôn Private, chỉ share cho các tài khoản trong file env;
  - không bao giờ đẩy `.env` hay tài liệu người dùng.
- **Notebook:**
  - dòng đầu mỗi cell là `print("[cell] …", flush=True)`; cell dài in tiến độ;
  - lúc đẩy, ghi vào `docs/RUNS.md` mốc có log đầu (giờ đẩy + 10 phút) và mốc xong;
  - treo thì xoá theo luật chung, không cancel.
- **Kiểm lượt chạy đầu:** 1 subagent, tối đa 15 phút (ngoại lệ đã cho phép). Sau đó không ngồi chờ: người dùng gọi kiểm khi cần.

## 7. Luận văn cho câu hỏi production

Thư mục `docs/09-luan-van/`. Mỗi bài 1 500–3 000 từ, văn xuôi tiếng Việt, gồm:

1. Câu hỏi.
2. Trả lời ngắn (≤ 3 câu, đọc được trước BGK).
3. Lập luận, mỗi khẳng định gắn một nhãn: **[ĐÃ THỰC NGHIỆM]** (số của đội, kèm n và đường dẫn), **[KIẾN THỨC NỀN]**, **[NGOÀI]** (paper / tài liệu, kèm nguồn), **[GIẢ THUYẾT]**.
4. Với mỗi thí nghiệm được dẫn, đủ **khung 10 điểm**:
   1. vấn đề;
   2. giả thuyết + dự đoán ghi trước;
   3. phương pháp, vì sao chọn, phương án bỏ;
   4. cấu hình chính xác: model + số tham số, dữ liệu, tham số, notebook + tài khoản, file code;
   5. kết quả có số + đường dẫn;
   6. diễn giải + giới hạn;
   7. thất bại, lỗi và cách gỡ;
   8. khái niệm cho người mới (thêm vào `docs/00-project/GLOSSARY.md`, file này đóng vai TU_DIEN);
   9. hình nên vẽ + file dữ liệu;
   10. bài học, bước tiếp.
5. Câu hỏi vặn của BGK, kèm trả lời.
6. **Không được nói** (khẳng định vượt bằng chứng).

| # | Câu hỏi production | Trả lời bằng | Bằng chứng đã có |
|---|---|---|---|
| PQ-01 ★ | Khi GreenScan nói "khớp" hay "mâu thuẫn", tin được bao nhiêu, và nó có biết lúc nào không chắc không? | AG-2, AG-0 | 0 mâu thuẫn sai so với 357/419 ngày 17/09 |
| PQ-02 ★ | Hệ thống có bịa hoặc tính sai số liệu không? | AG-1, B-b nhiễu | che số L1: SUPPORTED sai = 0 trên 51 ca |
| PQ-03 ★ | Bảng PDF, OCR, cột gộp làm sai kết luận thế nào, và hệ chặn ra sao? | AG-3 | F3; OCR `vie` đã sửa 22/10 |
| PQ-04 | Chạy với doanh nghiệp / ngành chưa thấy có giữ chất lượng không? | AG-1, AG-4 leave-company-out | T1 CV theo công ty 0,71–0,73 (nhãn Claude) |
| PQ-05 ★ | Tài liệu có rời máy không? Ngoại tuyến thì mất bao nhiêu chất lượng? | AG-4, L1 | 0 kết nối ra ngoài ở chế độ offline; offline và cloud lệch 3/156 kết luận; che số không giấu được danh tính (5/20 câu) |
| PQ-06 | Chưa có nhãn người thì lấy gì để nói hệ thống đúng? | mục 4 | kế hoạch đo, κ, cổng đăng ký trước |
| PQ-07 | Hệ thống có kết luận vi phạm pháp luật không? Ai chịu trách nhiệm? | v3 G, gói luật | 0 quy tắc áp được; luật do người viết |
| PQ-08 | Tìm sót bằng chứng thì sao? | AG-5 | bất biến 6: không tìm thấy ≠ sai |
| PQ-09 | Chi phí, tốc độ, phần cứng khi triển khai thật? | đo sẵn + AG-4 | 107–121 s cho HPG; 1 331 MB RAM; CPU |
| PQ-10 | Tái lập và kiểm toán lại được không? Đổi model thì kết quả đổi ra sao? | manifest, thang model | hash đầu vào, phiên bản gói luật; offline và cloud lệch 3/156 |

## 8. Lịch (đường găng: AG-0 → AG-1 → AG-2 → tích hợp)

| Ngày | Việc | Ra gì |
|---|---|---|
| 31/10–01/11 | Duyệt kế hoạch; dựng GS-Bench B-a + B-b; đăng ký `agentic_v1`; chép `kapi.py`; smoke 4 tài khoản; viết PQ-06 | `benchmark/gs_bench_v1/`, `docs/RUNS.md` |
| 01–02/11 | AG-0 (CPU); AG-3 phần CPU; đẩy AG-1 (thang 5 model) | phiếu AG-0 có số |
| 03–04/11 | Đọc AG-1; AG-5; quyết AG-4 | phiếu AG-1, AG-3 |
| 04–05/11 | AG-2 trên đầu ra AG-1; viết PQ-01, PQ-02, PQ-03 | đường độ phủ – precision |
| 05–07/11 | **Cổng tích hợp 06/11:** qua thì đưa huy hiệu "hai đường" + bảng kiểm tổng vào sản phẩm sau cờ `QUANTUM_VERIFY=dual` (mặc định tắt); chạy lại 17 bẫy xanh, test bất biến và lượt HPG. AG-4 nếu mở | bản sản phẩm có cờ |
| 07–09/11 | Đóng băng; PQ-04, PQ-05, PQ-09, PQ-10; số cho slide | `docs/09-luan-van/` |
| 10/11 | Chung kết | |

**Cổng tích hợp 06/11** (đăng ký trước), trên B-b chia theo công ty:
- CONTRADICTED sai không tăng;
- SUPPORTED sai không tăng;
- độ phủ tăng, cận dưới CI > 0;
- 17 bẫy xanh và 14 test bất biến vẫn qua;
- lượt HPG ngoại tuyến ≤ 2 × thời gian hiện tại.

Không qua thì sản phẩm giữ nguyên, kết quả trình bày là **"nghiên cứu, chưa đưa vào sản phẩm"**.

## 9. Quyết định của người dùng (31/10)

1. **Tài khoản Kaggle:** chọn trong các tài khoản rảnh và tài khoản dự phòng. Áp dụng ở mục 6: dùng file dự phòng.
2. **Đưa vào sản phẩm:** phương án (b). Khi qua cổng 06/11, kết quả vào sản phẩm dưới dạng trợ giúp người soát, sau cờ `QUANTUM_VERIFY=dual`, **verdict không đổi**.
3. **API đám mây:** được dùng, trần **US$5**. Chỉ dùng báo cáo công khai, đã che số, ghi số token thật mỗi lần chạy. Dùng để diễn đạt lại B-b và làm thầy cho AG-4.
4. **Việc chỉ người làm được, giá trị cao nhất:**
   - Quỳnh, Thảo và Nhân gán lô 1 T1 (79 câu, khoảng 1 giờ mỗi người) và 40 trong 88 cặp, **trước 04/11**;
   - đó là cách duy nhất để PQ-01 có một con số trên nhãn người.

## 10. Tiến độ

### 31/10
- **Đã xong:**
  - **GS-Bench v1:** `benchmark/gs_bench_v1/`, 193 ca: 51 ca dựng B-a, 142 ca B-b sinh từ 26 số liệu thật của 5 doanh nghiệp.
    - Nhãn bạc: IR bằng chứng do Claude đọc một lượt và bộ kiểm tất định soát. Nhãn của từng họ nhiễu khớp `irlib` 142/142.
    - Soát tay 14 ca: nhãn đúng; 3 lỗi diễn đạt đã sửa trong `build.py`.
  - **Mốc luật (AG-0):** `experiments/AG-0/out/score_rules.json`.
    - B-a: 20/32 và 7/19, lặp lại đúng size ladder.
    - B-b: độ phủ 0,028 (4/142), precision 0,75, 0/44 ca mâu thuẫn bị bắt.
  - **Mốc IR gold + `irlib` (trần của AG-1):**
    - B-b: 140/142, độ phủ 0,528, precision 1,0, 0 kết luận sai.
    - 2 ca hụt là câu gộp hai nhiên liệu; thư viện thận trọng trả N.
  - **Đăng ký `agentic_v1`** trong `configs/measurement_decisions.yaml` (cổng + dự đoán AG-1).
  - **Công cụ Kaggle:** `tools/kaggle/kapi.py` và `tools/kaggle/build_nb.py`; notebook `experiments/AG-1/nb_a.ipynb` và `nb_b.ipynb`.
- **Phát hiện ngoài kế hoạch:**
  - **Khoá FPT bị 401** (31/10). Chế độ `cloud` của sản phẩm (GLM-5.2) hiện không chạy được; cần gia hạn khoá.
  - Trong `.env` không còn khoá API đám mây nào khác.
  - **Quyết định của người dùng (31/10, sau khi biết khoá hỏng):** không cần khoá trả phí.
    - Vai "thầy" và "người đọc thứ hai" chuyển sang **Qwen3-32B-AWQ chạy trên Kaggle** (`hdonqu/gs-ag1-c`).
    - Khoá miễn phí (Groq, Cerebras: có Qwen3-32B) chỉ dùng khi người dùng tự đăng ký, và chỉ cho báo cáo công khai, vì gói miễn phí có thể lưu dữ liệu.
    - Chế độ demo của sản phẩm vẫn là `offline`.
- **Lỗi trong quá trình:**
  - Bộ đọc thận trọng bỏ 75/109 số liệu, nên B-b nhỏ hơn dự kiến (khoảng 600 ca).
  - Mở rộng bằng bảng của doanh nghiệp phát thải cao (AG-3) và bằng các số liệu "không chắc" sau khi người soát.

### 31/10 11:45: AG-1 có số đầu, chưa qua cổng

Chi tiết ở `experiments/AG-1/README.md` mục 5.
- 4B: precision 1,0 nhưng độ phủ chỉ 0,134.
- 32B: độ phủ 0,423 nhưng 7 ca CONTRADICTED sai.
- Ghép "luật → 4B ∧ 32B": độ phủ 0,113, precision 0,94, 0 vu oan.

**GROQ-PROBE** (`experiments/GROQ-PROBE/`) đang thử ma trận 9 cấu hình × 3 model Groq: gpt-oss-120b, gpt-oss-20b, qwen3.8-27b. Groq không còn Qwen3-32B. Mục `groq` đã có trong sản phẩm (`GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_EXTRA_BODY`) và gắn nhãn "đám mây".

### 31/10 chiều: GS-Bench v1.1 và nguồn dữ liệu bổ sung

- **Nhãn Claude lô 2:** 800 câu mới (Haiku, `benchmark/gs_bench_v1/ir_claude_v2.jsonl`), đọc ra 94 số liệu.
  - Hai lô gộp lại có 203 số liệu đọc; giữ 77 sau bộ kiểm tất định.
- **`gs_bench_v1.jsonl`** (ghi đè, là tập cha của v1): 455 ca = 51 B-a + 404 B-b (S 95, C 125, N 184), trên 7 doanh nghiệp.
  - Mã ca của 193 ca cũ không đổi, nên điểm AG-1 cũ vẫn chấm được trên phần chung.
  - **THIẾU:** 2 ca `irlib` lệch nhãn họ nhiễu (`selfcheck_mismatches.jsonl`), phải đọc trước khi chạy lại AG-1.
  - **Bước kế:** cho Qwen3-32B trên Kaggle đọc lần hai `candidates_v2.jsonl`, rồi giữ thêm các số liệu "không chắc" mà hai bên đọc khớp.
- **Nguồn dữ liệu bổ sung:** `docs/07-presentation/nghien-cuu/B_NGUON_DU_LIEU_BO_SUNG.md` (agent Haiku, có mục "chưa xác minh").
  - P0: Climate TRACE, GEM thép, GEM xi măng, danh mục QĐ 13/2024, quan trắc tự động.

### 31/10 14:15: lỗi của model là lỗi định dạng; sửa tất định, kiểm ngoài mẫu đang chạy

Chi tiết ở `experiments/AG-1/README.md`, mục 5, phần "Kết quả 31/10 14:10".

**Việc 1 (lỗi 32B / 4B / 1.7B):** xong.
- 11/11 kết luận sai của 32B là bội số model tự thêm ("10.730 m3" → "10.730 ngàn m3").
- 4B mất 50 tuyên bố vì nhét "triệu tCO2e" vào `value_text`.
- Sửa bằng `irlib.ground()`: số liệu model đọc phải khớp với câu gốc. Có 9 test hồi quy ở `tests/test_irlib_ground.py`.
- Chấm lại từ đầu ra thô (`experiments/AG-1/rescore.py`), trong mẫu. 4B: độ phủ 0,134 → 0,437, precision 0,984. 32B: precision 0,817 → 0,985, CONTRADICTED sai 7 → 1. Mọi model ≥ 4B qua cổng `ag1_ir_path_usable`.
- Hiệu ứng cỡ trên 4B gần như biến mất.

**Việc 2 (lượt B):** xong. 14B: 0,254 / 0,944. gemma-12B sinh rỗng, đã loại.

**Việc 3 (GROQ-PROBE):** chọn `openai/gpt-oss-120b`, `reasoning_effort` low cộng `json_object`: 12/12 JSON, độ đúng trường 1,0, p50 1,0 s. `.env.example` đã sửa. `.env` của người dùng còn `qwen/qwen3-32b`, model mà Groq đã gỡ.

**GS-Bench v1.1:**
- Hai ca lệch `selfcheck` là lỗi của bộ sinh: C2 nhân "0" lên "0 nghìn" thì giá trị không đổi. `build.py` đã bỏ C2 khi giá trị bằng 0.
- Bộ còn 453 ca (51 B-a + 402 B-b, S 95 / C 123 / N 184), 0 ca lệch.

**Việc 4 (chạy lại AG-1, ngoài mẫu):**
- Đăng ký `agentic_v1_1` trước khi chạy, prompt giữ nguyên.
- Lượt D (4B, 1.7B), E (8B, 14B) và F (32B, kèm đọc lần hai 800 câu `candidates_v2`, tức việc 5) đã đẩy lúc 14:13. Mốc ở `docs/RUNS.md`.
- Khi xong: chạy `rescore.py` cho cả hai chế độ có và không có `ground`, chấm riêng 260 ca mới, rồi đối chiếu với `predictions_held_out_260`.

**14:20, lỗi nhãn của bộ sinh:** 14 ca PV Power có câu không viết phạm vi phát thải, nên S0 và N3 thành cùng một câu. Đã sinh lại (`errata_v1_1.txt`), và tập ngoài mẫu của D/E/F còn 246 ca. Luật trên v1.1: 0 CONTRADICTED sai, 9 SUPPORTED sai.

**14:35, lượt D ngoài mẫu:** xem `experiments/AG-1/README.md`, phần "ngoài mẫu".
- 4B có `ground`: precision 0,903, CONTRADICTED sai 2. Qua cổng an toàn sát nút.
- Độ phủ 0,126: dự đoán sai.
- Bản v1.2 (count = absolute, C-guard) đăng ký `agentic_v1_2`; trong mẫu cho 0 vu oan.

**22:40, E/F ngoài mẫu:** xem `experiments/AG-1/README.md`, phần "22:40".
- Dự đoán 32B và dự đoán `ground` giảm vu oan đều đúng. Dự đoán "không có hiệu ứng quy mô" sai: độ phủ 4B / 8B / 14B / 32B là 0,126 / 0,220 / 0,256 / 0,329.
- Sửa báo cáo 14:35: với v1.1, 4B, 14B và 32B **trượt** cổng `ag1_ir_path_usable` (vu oan ≤ luật + 1 = 1). Chỉ 8B qua.
- Với v1.2, 8B và 32B có 0 vu oan, 14B có 1. Đây là kết quả một phần ngoài mẫu.
- AG-2 (4 đường) trượt cổng sản phẩm: 9 SUPPORTED sai so với 7 của luật, vì luật nói S một mình. Xô OOF quá mảnh.
- Đã dựng tập ngoài mẫu v1.2 (162 ca, 9 công ty) và sửa đổi đăng ký lúc 22h50. Lượt G đang chạy.

**23:25, lượt G (tập ngoài mẫu v1.2, 162 ca):** xem `experiments/AG-1/README.md`, phần "23:25".
- Mọi dự đoán `agentic_v1_2` đều đúng: vu oan bằng 0 ở cả bốn model, C-guard có tác dụng một lần. Độ phủ của 4B là 0,093.
- 37 % số ca của tập là `other_env` không phải môi trường (lỗi tập, phát hiện hậu kiểm).

**23:50, AG-2 v1** (đăng ký `agentic_ag2_v1`; script `experiments/AG-2/policies.py`). Hiệu chỉnh trên 388 ca v1.1 rồi thử trên 162 ca G. Mỗi ô ghi độ phủ / precision / SUPPORTED sai / CONTRADICTED sai.
- **Luật + 4B, bỏ phiếu S đơn độc của luật:** trên G đạt 0,093 / 1,0 / 0 / 0, phần tăng độ phủ so với luật có CI [0,016, 0,185]. Trên tập hiệu chỉnh đạt 0,242 / 0,989 / 1 / 0, trong khi luật có 8 SUPPORTED sai. Phần thống kê của cổng `ag2_dual_path_to_product` **qua** trên cả hai tập.
- **Luật + 32B** và **luật + 4 model** trượt cổng trên G: lần lượt 1 và 2 SUPPORTED sai, trong khi luật có 0.
- Chính sách hợp mà giữ phiếu S đơn độc của luật thì giữ luôn 8 SUPPORTED sai của luật. Bỏ phiếu đó là điều kiện để đường kép an toàn.
- Lưu ý: trên G, 4B chỉ dám kết luận 15 ca và đúng cả 15, nên đây chưa phải một cận chặt.

**Còn mở (theo thứ tự):**
1. **Đưa bộ đọc vào sản phẩm.** Đây là các phần còn lại của cổng: 17/17 bẫy xanh, test bất biến, thời gian chạy HPG offline ≤ 2 lần.
   - Kiểm tra độ đáng thử: cổng ngày 06/11 cần mục này. Hiện chưa có bộ đọc Qwen3 nào trong profile offline.
   - Hai lựa chọn: Qwen3-4B chạy cục bộ (GGUF / llama.cpp, phải đo thời gian chạy), hoặc qwen/qwen3-32b qua Groq. Groq chỉ dùng cho báo cáo công khai. Lưu ý 32B có 1 SUPPORTED sai trên G.
   - Đầu tiên: chạy bộ đọc của sản phẩm trên G và v1.1 để kiểm nó cho cùng kết quả với Kaggle. Sau đó bật `QUANTUM_VERIFY=dual` và chính sách "luật + IR, bỏ S đơn độc của luật", chỉ làm công cụ hỗ trợ người duyệt.
2. Đọc câu bằng chứng nhiều số và đọc năm của bằng chứng (prompt có ví dụ, hoặc tách câu theo từng số). Đây là nguồn mất độ phủ chính.
3. Nếu cần thêm tập ngoài mẫu: loại `other_env` khỏi `build_heldout_v12.py`.
4. AG-4 (QLoRA 1.7B): làm sau mục 2.
5. Luận văn: thêm G và AG-2 vào PQ-06; tiếp theo là PQ-02 và PQ-01.

### 01/11 17:00: phiên này tiếp quản (người dùng: "chạy ngay trên phiên này")

- **Lỗi tập ngoài mẫu v1.2:** có năm bịa từ tiêu đề trang, tên chỉ số méo và `other_env`. Đã lọc thành tập sạch v1.3 (`clean_v13.py`, `errata_v13.txt`) và chấm lại không tốn GPU.
  - Ngoài mẫu sạch (87 ca): luật 0,011; 4B 0,138; 8B 0,115; 14B 0,115; 32B 0,253 độ phủ. Mọi model precision 1,0, 0 kết luận sai.
  - Kết luận "4B mất vì đọc năm" bị rút lại. Chi tiết ở `experiments/AG-1/README.md`, mục 01/11 17:00.
- **Việc 1 (bộ đọc trong sản phẩm, `agentic_ag2_product`) bị chặn vì thiếu RAM.**
  - `ir_reader.py` và `product_reader.py` của phiên trước đã có. Ollama báo "model requires 3.3 GiB, available 2.6 GiB": máy 15,6 GB nhưng trống 0,3 GB; `javaw` chiếm 3,3 GB, tiến trình ZAIC `dm3.py` đang chạy, 3 phiên Claude đang mở.
  - Cần người dùng tắt bớt (ví dụ `javaw`) để đo. Không tự tắt tiến trình của người dùng.
- **17:15, kiểm "cùng kết quả" của bộ đọc sản phẩm trên Kaggle** (`rehoanzun/gs-ag2-q4-parity`, cùng đường code Ollama + `ir_reader.py`):
  - Q4 khớp 0,963 và Q8 khớp 0,981 với 4B bf16.
  - Luật + 4B cục bộ, bỏ phiếu S đơn độc của luật, trên G: Q4 có 0 kết luận sai, độ phủ 0,080 (CI phần tăng [0,016; 0,175]).
  - Dự đoán `agentic_ag2_product` **đứng vững** (kết quả ghi trong yaml). Bộ đọc Q4 cục bộ đủ điều kiện đặt sau cờ.
  - Phần cổng 06/11 còn thiếu:
    - thời gian đọc trên laptop, cần RAM; trên T4 là 1,7 giây/câu;
    - 17 bẫy xanh và test bất biến khi bật `QUANTUM_VERIFY=dual`;
    - thời gian chạy HPG.
- **17:40, AG-3 v0** (`experiments/AG-3/`, đăng ký `agentic_ag3_v0`):
  - Dựng hàng bảng từ toạ độ chữ. HPG trang 39 cho đủ 10 hàng, cộng dọc 3/3 khớp.
  - Trên 7 ca trang 39 (bộ đọc Groq `gpt-oss-120b`): trang thô đúng 1/7 với 0 kết luận; hàng dựng lại đúng 3/7, 0 sai. Dự đoán "N02/N05 thành C, ≥ 5/7" **sai**.
  - Nguyên nhân: IR thiếu chiều `segment`, và C-guard hạ C khi số trùng nằm ở hàng của mảng khác.
  - Phát hiện phụ: tiêu đề trang 39 ghi "NĂM 2024", còn bảng ghi 2025.
- **Luận văn:** đã viết PQ-02 (bịa / tính sai số) và PQ-01 (tin được bao nhiêu) trong `docs/09-luan-van/`. PQ-06 có từ trước.
- **Còn mở, theo thứ tự:**
  1. Đo trên laptop khi có RAM: thời gian đọc, HPG ≤ 2 lần, 17 bẫy xanh, test bất biến. Sau đó cổng 06/11.
  2. IR v1.3: thêm `segment`, C-guard chỉ áp khi số trùng nằm ở số liệu so được, và gắn nhãn hàng tổng bằng kết quả cộng dọc. Đăng ký trước, chạy lại 7 ca trang 39 và GS-Bench.
  3. Lớp bảng cho GS-Bench (thép, xi măng, điện).
  4. AG-4 QLoRA 1.7B.
  5. Luận văn PQ-03 (bảng / OCR, dùng AG-3) và PQ-05 (riêng tư / ngoại tuyến, dùng kết quả cùng kết quả của bộ đọc cục bộ).

### 04–05/11: chuẩn bị Chung kết, GS-Eval v2, org pack, luận văn

Yêu cầu của Nhân (04/11): đọc tài liệu và paper, dựng dataset explain / gợi ý sửa / chấm rủi ro / quy tắc nội bộ / độ dễ dùng (nhãn Claude coi như dataset thường), đánh giá hệ thống, viết luận văn. Chi tiết ở `docs/10-chung-ket-2026-11/TRANG_THAI.md`.
- **Org pack** (quy tắc nội bộ người dùng thêm) vào sản phẩm sau cờ `QUANTUM_ORG_PACKS`, mặc định tắt. Gồm `src/quantum_gw/legal/org_pack.py`, CLI `org-validate` và `org-preview`, `docs/03-architecture/ORG_PACK.md`, 43 test mới. Toàn bộ khoảng 453 test qua. Tắt cờ thì result.json và manifest không đổi.
- **GS-Eval v2** (`benchmark/gs_eval_v2/`): explain 200, edit 200, score 200 × 2 lượt mù + phân xử, 14 pack với 237 ca, bộ UX. `evaluate.py` chấm mã hiện tại: đã chạy lại trên mọi tài liệu của các lượt cũ, 15 lượt từ 22/10 trở đi.
- **Phát hiện chính** (`docs/10-chung-ket-2026-11/DANH_GIA_HE_THONG_2026-11-05.md`):
  - CONTRADICTED trên câu thật đúng 3/38: 22 ca do luật từ phủ định (`configs/stance_cues.yaml`, cụm lành tính chỉ khớp nguyên văn), 13 ca do so khác đối tượng;
  - khoảng 30 % câu trích không phải tuyên bố;
  - điểm rủi ro ρ 0,23 so với trần đồng thuận 0,73;
  - **chiều 05/11 đã sửa (chốt chặn mâu thuẫn, cờ `self_evidence_can_contradict`):** CONTRADICTED 3/4, 0 vu oan trên tuyên bố thật, ρ 0,39; GS-Bench 453/453 và 4 ca án lệ không đổi;
  - gợi ý sửa 0/527 thêm số;
  - org pack đúng 0,945, đúng 45/45 ca an toàn.
  - Chưa sửa sản phẩm (D-2026-10-16-01). Đề xuất P0–P2 ở mục 4 của báo cáo.
- **Ngân hàng câu hỏi:** `docs/10-chung-ket-2026-11/NGAN_HANG_CAU_HOI_CHUNG_KET.md` (170 câu, gồm nhóm J từ đánh giá) và `KHAI_NIEM_CAN_NAM.md`.
- **Luận văn:** `docs/09-luan-van/LUAN_VAN_GREENSCAN/` (7 chương, ghép bằng `assemble.py`).

## 11. Hàng việc cho phiên sau (người dùng 31/10: "tận dụng Kaggle chạy nhiều thí nghiệm, sửa lỗi nhiều nhất có thể, rồi viết luận văn kỹ lưỡng")

Làm theo thứ tự. Mỗi việc có kết quả thì ghi phiếu theo khung 10 điểm.
1. **Lỗi của 32B và 1.7B (CPU):**
   - phân loại 7 ca CONTRADICTED sai và 4 ca SUPPORTED sai của 32B, các lỗi của 1.7B, và số ca 4B bỏ lỡ (độ phủ thấp);
   - sửa `irlib` (chuẩn hoá) và prompt;
   - thêm test hồi quy vào `benchmark/gs_bench_v1/`.
2. **Lượt B** (`vantiennhuannguyen/gs-ag1-b`): tải, chấm, điền bảng.
3. **GROQ-PROBE:** đọc `out/summary.json`, chọn model + cấu hình, đưa hai dòng `GROQ_MODEL` và `GROQ_EXTRA_BODY` cho người dùng dán vào `.env`.
4. **Chạy lại AG-1** với prompt và `irlib` đã sửa (thêm few-shot, ràng buộc enum).
   - Tài khoản: `thanhtruc02`, `vantiennhuannguyen`, `hdonqu`; dự phòng `rehoanzun`, `letranchauanh`.
   - Thêm cấu hình: 32B tự kiểm (đọc hai lượt, chỉ giữ IR khớp) và Qwen3-14B.
5. **Mở rộng GS-Bench v1.1:**
   - lấy số liệu mà Claude và Qwen3-32B cùng đọc giống nhau (`kaggle_out/c/**/q3-32b-awq_texts.jsonl` so với `ir_claude.jsonl`), gồm cả 75 số liệu "không chắc";
   - thêm 1 lượt Groq làm người đọc thứ ba nếu hạn mức cho phép;
   - mục tiêu ≥ 8 doanh nghiệp.
6. **AG-2 chính thức:**
   - xô xác suất trên OOF theo công ty, đường độ phủ – precision;
   - kiểm cổng `ag2_dual_path_to_product` trước 06/11.
7. **AG-3 bảng PDF:** HPG trang 39, đọc trên CPU trước.
8. **Luận văn:** PQ-06 (đo khi chưa có gold), PQ-02 (bịa / tính sai số), PQ-01 (tin được bao nhiêu), rồi PQ-03 và PQ-05. Dùng số của mục 5 AG-1.

## Liên quan
- ZAIC: `Zalo AI challenge/docs/NGHIEN_CUU_PIPELINE.md` (L1, D1), `PIPE_CAU_HOI_NGHIEN_CUU.md`, `RUNS.md`.
- GreenScan: `ARCHITECTURE_INVARIANTS.md`, `CHUONG_TRINH_THI_NGHIEM_VA_DU_LIEU_v3_2026-10-13.md` (ma trận A–H; AG-1 / AG-2 hiện thực D1, D2, B6; AG-5 hiện thực C1), `OFFLINE_TUNG_PHAN_2026-10-10.md`, `MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`, `CHON_MO_HINH_THEO_CONG_DOAN_2026-10-16.md`.
