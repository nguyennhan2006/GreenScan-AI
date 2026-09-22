# Mức sẵn sàng Vòng 2 — snapshot 2026-09-22

**Loại tài liệu:** snapshot tại một thời điểm. **Không sửa số trong tài liệu này về sau.** Lần rà soát tiếp theo tạo `ROUND2_READINESS_<ngày>.md` mới hoặc thêm mục "Progress since 22/09" ở cuối. Baseline số đo đi kèm: [`benchmark/baseline_2026-09-22.json`](../../benchmark/baseline_2026-09-22.json) — mọi tuyên bố "đã cải thiện" phải so với file đó.
**Người chạy đo:** Nhân (với Claude) · **Rubric:** Thể lệ cuộc thi, mục 11.2 Vòng 2 (6 tiêu chí) · **Mốc:** product freeze 10/10 · Bán kết 25/10 · Chung kết 10/11/2026
**Quyết định quản trị kèm theo:** `DECISIONS_LOG.md` D-2026-09-22-01 → 05 · Issue mới: `ISSUES_REGISTER_2026-09.md` mục N

---

## 0. Kết luận một đoạn

Hệ thống chạy end-to-end trên tài liệu Việt Nam thật, có UI, reviewer workflow, tầng pháp lý, test xanh, 4 case phán quyết khớp. **Vấn đề lớn nhất không còn là thiếu tính năng mà là verdict trên tài liệu Việt Nam thật chưa đủ đáng tin để đưa trước BGK**: trong run Hòa Phát hôm nay, 7/8 CONTRADICTED là sai (so hai chỉ số khác nhau trong cùng bảng), 3/3 SUPPORTED chỉ nhờ một cue, 93% claim ra PARTIAL với cùng một câu rationale, 36% claim bị gắn HIGH trên một doanh nghiệp control. Ba tiêu chí 1+3+4 (60% điểm) đều bị kéo xuống bởi cùng nguyên nhân này. Thứ tự ưu tiên vì thế là **N1–N5 trước product polish**; Case A không vào demo cho tới khi N1 xanh.

---

## 1. Số đo tại 22/09

Đường chạy mặc định: heuristic, LLM off, embedding `lite` (BM25 + n-gram), reranker `none`, không key, máy dev Windows CPU, không OCR.

| Phép đo | Kết quả | So với mục tiêu |
| --- | --- | --- |
| `pytest tests` | xanh toàn bộ (233 theo báo cáo 20/09), 21 trap xanh | ✅ |
| `quantum-agent evaluate` (golden 4 case) | recall 1.0 · status 1.0 · citation 1.0 · gate 1.0 | ✅ nhưng bộ này **không bắt được** N1–N5 |
| `run_case.py --all` (4 case phán quyết) | status 4/4 · stance 1.0 · **risk band 2/4** | B6 chưa hiệu chỉnh |
| HPG BCPTBV 2025 + BCTN 2024 (11 MB) | **79 s** wall, 3.234 chunk, **181 claim** | ≤ 80 claim: ✗ |
| HPG verdict | PARTIAL **168 (93%)** · CONTRADICTED 8 (4%) · SUPPORTED 3 · INSUFFICIENT 2 | CONTRADICTED ≤ 15% ✅ (nhưng 7/8 sai — N1/N2) |
| HPG severity | HIGH 65 (36%) · MEDIUM 110 · CRITICAL 1 · LOW 5 | trần MEDIUM cho PARTIAL: ✗ (N5) |
| HPG claim có số | 66/181 (36%) | ≥ 70%: ✗ |
| HPG legal finding | 181/181 INSUFFICIENT_EVIDENCE | ≥ 1 finding cụ thể: ✗ (B7) |
| Gold adjudicated | 5 cặp (+8 dòng trial 17/09) | ≥ 60 trước 10/10: ✗ |
| Repo | **159 file chưa commit**, chưa có tag baseline | A1 mở từ 17/09 |

---

## 2. Chấm thử theo rubric Vòng 2

Điểm là ước lượng nội bộ để xếp ưu tiên, không phải dự đoán điểm BGK.

| Tiêu chí | Trọng số | Hiện tại | Đạt được tới 10/10 | Bằng chứng đã có | Cái thiếu để lên bậc 90–100 |
| --- | --- | --- | --- | --- | --- |
| 1. Làm rõ và xử lý bài toán thực tiễn | 20% | ~75 | 85–90 | `PROBLEM_DEFINITION.md`, `AUDIT_PROTOCOL.md`, checklist 5 thuộc tính, nguyên tắc abstain, ADR 0004/0005, mỏ neo pháp lý QĐ 13/QĐ 21/TT 96 | **Chưa có case "đóng đinh"** trên DN VN được soát tay; 8 CONTRADICTED của HPG hiện sai → nếu hiện lên là mất điểm ngay |
| 2. Chất lượng dữ liệu | 15% | ~55–60 | 75–85 | 670 tài liệu/21 DN, SHA-256, provenance trang, 4 case phán quyết + 2 control, 11 văn bản/938 clause, `leakage_report.json`, `LABELING_CONVENTIONS.md` | Gold 5 cặp; hàng đợi cũ 26% on-topic; kế hoạch v2 chưa khởi động (A7); chưa có Dataset Card; chưa có split theo DN được dùng để báo số |
| 3. Tính hợp lý giải pháp, thuật toán | 20% | ~65–70 | 80–90 | Kiến trúc evidence-first có ADR, số học deterministic, 21 trap là regression gate, RRF, legal policy-as-code | LLM **tắt** trong đường mặc định; embedding `lite`, reranker `none`; **không có bảng baseline** (LLM-only / vector RAG / GreenScan); chưa có Recall@k; so số vẫn lệch metric (N1) |
| 4. Chất lượng prototype | 20% | ~65–70 | 85+ | Chạy E2E, API, UI 3 màn, render trang PDF + highlight, reviewer workflow (7/7 chuyển trạng thái), manifest tái lập có hash | Chưa có xuất PDF/JSON, RunStore, panel pháp lý, `docker compose` cả stack, video backup; **93% PARTIAL cùng một rationale** (N3) |
| 5. Khả năng ứng dụng, triển khai | 15% | ~60–65 | 75–85 | Local-first gateway, `SECURITY_AND_GOVERNANCE.md`, `ROADMAP.md` | Chưa có bảng chi phí/thời gian đo (79 s hôm nay là số đầu tiên); chưa có sơ đồ production; tenant isolation chỉ là ý định; chưa có đối tác pilot |
| 6. Trình bày, tài liệu | 10% | ~60 | 85 | `QA_BANK_100`, `QA_DRILL`, kịch bản 7 phút | Chưa có slide, chưa dry-run, chưa video; docs nhiều nhưng chưa cô đọng thành 8 artefact BGK cần |

Điểm gia quyền ước lượng: **~66–68 hiện tại → ~83–85 nếu làm đúng thứ tự mục 5.**

---

## 3. Lỗi mới phát hiện từ run HPG 22/09 (đã đưa vào `ISSUES_REGISTER_2026-09.md` mục N)

| # | Lỗi | Bằng chứng trong run `d160226875ec4144` | Hệ quả với rubric |
| --- | --- | --- | --- |
| N1 🔴 | **So số vẫn lệch metric** — metric bucket quá thô, hai số trong cùng bảng bị coi là mâu thuẫn | "99% tổng phát thải là gang thép" vs "24%" (tăng sản lượng); "23.474.480 tCO2e toàn Tập đoàn" vs "90.846" (một công ty con); "0,70 tCO2/tấn (Scrap-EAF)" vs "1,43" (BOF); "4,5% điện lưới" vs "0,03% tái tạo" (cả hai chiều) → 5/8 CONTRADICTED | Chặn Case A; mất điểm tiêu chí 1 và 3 nếu lộ |
| N2 🔴 | Cue "thiếu" vẫn bắn trên nguồn "thẩm quyền" | "Duy trì cơ chế kê khai và nộp thuế… tuân thủ pháp luật" → CONTRADICTED vì "thiếu" | Cùng cơ chế B1 tưởng đã đóng |
| N3 🟠 | Extractor nhận câu không phải claim; rationale PARTIAL là một câu chung | "Tôi rất vinh dự giới thiệu Báo cáo…", "xanh hóa sản xuất… là ba ưu tiên" → PARTIAL; 168 PARTIAL cùng rationale tiếng Anh | UI đơn điệu; BGK đọc là "hệ thống nói maybe với mọi thứ" |
| N4 🟠 | SUPPORTED chỉ nhờ một cue ủng hộ | "Đào tạo lập Báo cáo kiểm kê KNK" SUPPORTED vì BCTN có "chứng nhận"; 3/3 SUPPORTED đều như vậy | False SUPPORTED — hướng nguy hiểm nhất |
| N5 🟠 | PARTIAL do thiếu thuộc tính mặc định ra HIGH | 65 HIGH + 1 CRITICAL trên DN control | BGK đọc là cáo buộc (G2), trái nguyên tắc P4 |

---

## 4. Điểm đã làm được (được phép đứng ở cột "Achieved")

- Pipeline 10 bước chạy trên PDF thật 11 MB trong 79 s; manifest ghi hash input/config/pipeline version → trả lời được "code có tái lập không".
- Nguyên tắc **abstain + không cáo buộc** được mã hoá thành ADR 0004/0005 và 21 trap test — không chỉ là slogan.
- 4 case có phán quyết thật (SEC/tòa) khớp status 4/4.
- Reviewer workflow append-only đúng máy trạng thái 7/7.
- Tầng pháp lý resolve đúng văn bản theo hiệu lực (NĐ 06 → 119/2025 → 83/2026), 11 văn bản / 938 clause.
- Model gateway local-first, routing theo task, chạy được không cần key.
- Quản trị dự án: DoD 15 mục, decisions log, issues register, test report có số đo.

---

## 5. "Huấn luyện thêm" — ba việc, không phải fine-tune

Giữ D-2026-09-18-02 (không fine-tune tới Bán kết). Với 5 cặp gold, fine-tune bất kỳ thứ gì cũng không đo được.

| Việc | Vì sao | Ai / khi | Nghiệm thu |
| --- | --- | --- | --- |
| **Gold ≥ 60 cặp, 2 người độc lập, κ, split theo DN** | Nút thắt duy nhất của tiêu chí 2; điều kiện để có bất kỳ số nào ở tiêu chí 3 | Quỳnh + Thảo, bắt đầu tuần 22–28/09, ~1,5 h/ngày | 20 cặp + κ thử cuối 27/09; 60 trước 10/10 |
| **Ablation LLM normalization** (S2.1) | Cuộc thi AI mà LLM tắt là câu hỏi chắc chắn; chỉ bật khi đo được hơn heuristic ≥ 15 điểm trên 30 claim Quỳnh soát | Nhân, tuần 29/09–05/10 | bảng heuristic vs LLM: F1 thuộc tính, thời gian, số call |
| **Bật + đo retrieval thật**: `embedding: local` (BGE-M3), reranker 30→5 | Để "hybrid retrieval + reranking" là số đo, không phải mô tả kiến trúc | Nhân, sau khi có ≥ 20 cặp gold | Recall@5/@10 theo k, thời gian/claim CPU, ghi version model |
| (Tuỳ chọn, R3) NLI tiếng Việt local cho stance | Chỉ nếu hơn heuristic ≥ 10 điểm trên trap + 30 cặp | Nhân, chỉ nếu 10/10 đã xanh | — |
| **Huấn luyện người**: 8 khối kiến thức G7, mock Q&A random member | Tiêu chí 6 và phần phản biện của tiêu chí 1/3 | Cả nhóm, 18–24/10 | mỗi người 60 s/câu |

---

## 6. Thứ tự làm tới 10/10 (điều chỉnh so với `EXECUTION_PLAN_2026-09.md`)

| Khi | Việc | Phục vụ tiêu chí | Nghiệm thu |
| --- | --- | --- | --- |
| **22/09** | Commit 159 file (S0.1, chia theo chủ đề) + tag `demo-baseline-2026-09-22` + commit `benchmark/baseline_2026-09-22.json` | Tất cả | `git status` sạch; tag tồn tại |
| 22–28/09 | **N1–N5** + phần còn lại B9/B10, mỗi lỗi ≥ 1 trap mới; chọn **1 claim KNK HPG có bảng** làm Case A và soát tay end-to-end; Quỳnh bắt đầu gold; Thảo 3 rule pháp lý có điều kiện (S1.7) | 1, 3, 4 | HPG: 0 CONTRADICTED sai sau soát tay; PARTIAL không còn HIGH; ≥ 1 legal finding ≠ INSUFFICIENT; 20 cặp gold |
| 29/09–05/10 | RunStore + xuất JSON/PDF + panel pháp lý + `docker compose` cả stack; LLM normalization có nhãn "AI đề xuất"; **bảng chi phí đo** (trang/giây, RAM, có/không GPU, có/không LLM) | 4, 5 | mở lại run < 2 s; PDF mở được; bảng chi phí trong tài liệu tiêu chí 5 |
| 05–10/10 | Gold ≥ 60 + κ + **Dataset Card**; eval hold-out theo DN kèm CI; ablation 3 dòng (heuristic / +LLM / +BGE+rerank); sơ đồ production; video backup; tag `rc-2026-10-10` | 2, 3, 5 | `EVALUATION_REPORT_v1.md`; máy sạch chạy được |
| Sau 10/10 | Chỉ slide, 8 artefact, tập, mock Q&A | 6 | 2 dry-run bấm giờ |

Khác biệt so với plan 18/09: **N1–N5 lên trước S3** (product layer); **cắt ô bảng (S3.3) nếu N1 chưa xong** — trích dẫn trang + highlight đủ cho tiêu chí 4, sai ô bảng thì mất điểm tiêu chí 3.

---

## 7. Hard gate và quy ước ngôn ngữ (chốt 22/09 — xem `DECISIONS_LOG.md`)

1. **Case A không vào demo cho tới khi N1 xanh.**
2. **PARTIAL do thiếu thuộc tính: trần MEDIUM** cho tới khi calibration được chốt. HIGH/CRITICAL chỉ khi có numeric contradiction cùng metric, authoritative cue, hoặc legal/numeric violation.
3. **Không nói "Hybrid RAG + reranker" ở thì hiện tại** cho tới khi BGE-M3 và reranker được bật, đo và ghi version. Trước đó: *"kiến trúc hỗ trợ hybrid retrieval/reranking; cấu hình baseline hiện tại dùng BM25 + n-gram + RRF"*.
4. **Không nói "AI accuracy"** cho tới khi gold ≥ 60 và có hold-out theo DN. Với 5 gold chỉ báo regression/golden checks.
5. Mọi tuyên bố "đã cải thiện" phải so với `benchmark/baseline_2026-09-22.json`.

---

## 8. Bộ 8 artefact BGK cần — trạng thái

| # | Artefact | Trạng thái 22/09 | Nguồn/nơi sẽ đặt |
| --- | --- | --- | --- |
| 1 | Problem Case Sheet (1 case xuyên suốt claim → evidence → số → kết luận) | ✗ chờ N1 + Case A | `docs/07-presentation/CASE_SHEET.md` |
| 2 | Dataset Card | ✗ | `docs/04-data-ai/DATASET_CARD_v1.md` |
| 3 | Architecture Diagram (đang chạy, không phải tương lai) | một phần (`ARCHITECTURE.md`, `DATA_FLOW.md`) | cần 1 hình + ghi cấu hình baseline |
| 4 | Evaluation Report (baseline + metrics + error analysis) | ✗ chờ gold | `docs/04-data-ai/EVALUATION_REPORT_v1.md` |
| 5 | Demo Script (Supported / Insufficient / Contradicted) | có (EXECUTION_PLAN §4) | cần Case A xanh |
| 6 | Deployment & Security Diagram + chi phí | một phần (`SECURITY_AND_GOVERNANCE.md`) | cần bảng chi phí đo |
| 7 | Technical Q&A Book | ✅ `QA_BANK_100_2026-09-20.md`, `QA_DRILL.md` | cập nhật sau ablation |
| 8 | Backup package (video, screenshot, cached run, PDF mẫu) | ✗ | `demo_bundle/` (C9) |

---

## 9. Chuẩn bị Chung kết (26/10–10/11) — làm song song, không tranh tài nguyên với Bán kết

**Nguồn rubric Vòng 3 hiện có:** chỉ tiêu chí 1 (ảnh chụp 22/09): *"Mức độ giải quyết bài toán thực tiễn — 20%: sản phẩm có giải quyết triệt để bài toán thực tế đã đặt ra ở vòng đầu hay không? Các kết quả định lượng (độ chính xác, sai số, tốc độ xử lý, lợi ích kinh tế ước tính…) được chứng minh… Thang: <40 không giải được · 40–70 giải một phần · 70–90 giải tốt, có số liệu · 90–100 giải triệt để, vượt trội."* Các tiêu chí còn lại của 11.3 **chưa có** — cần bổ sung vào tài liệu này khi có ảnh/văn bản đầy đủ.

Khác biệt cốt lõi Vòng 2 → Vòng 3 (theo tiêu chí 1 đã thấy): Vòng 2 chấm *"prototype chạy được, có căn cứ"*; Vòng 3 chấm *"đã giải quyết bài toán vòng 1 đặt ra chưa, chứng minh bằng số"*. Nghĩa là mọi thứ ở Vòng 2 được phép là "Achieved/Target/Hypothesis" thì ở Vòng 3 phải chuyển được sang cột Achieved.

### 9.1 Những gì Vòng 3 sẽ đòi mà Bán kết chưa cần

| Yêu cầu Vòng 3 | Trạng thái 22/09 | Việc phải làm sau 25/10 | Việc **phải gieo từ bây giờ** (nếu không sẽ không kịp) |
| --- | --- | --- | --- |
| Đối chiếu với **bài toán đặt ra ở Vòng 1** (hồ sơ V1 mục IX, MVP_SCOPE) | Hồ sơ V1 hứa: ≥100 cặp gold, 6 ngưỡng V.5.1, trích dẫn tới ô bảng, xuất PDF, chatbot grounding, quantum "hướng Vòng 2" | Bảng **Hứa → Đã đạt → Chưa đạt + lý do** cho từng mục hồ sơ V1; không giấu mục chưa đạt | Giữ danh sách này cập nhật từ 10/10; mỗi mục chưa đạt phải có lý do đo được |
| **Độ chính xác, sai số** có hold-out | Gold 5 | Gold **100 → 150**, hold-out ≥ 3 DN chưa từng thấy, CI bootstrap, báo theo DN và theo loại claim | Gán nhãn **không dừng ở 60** sau 10/10; Quỳnh + Thảo giữ nhịp 1,5 h/ngày qua Bán kết |
| **Tốc độ xử lý** | 79 s / 2 PDF, 1 máy | Bảng: trang/giây, claim/giây, RAM/VRAM, có/không GPU, có/không LLM, batch 10 báo cáo | Script đo tự động (`tools/benchmark.py` mở rộng) chạy được trên máy sạch |
| **Lợi ích kinh tế ước tính** | Chưa có; hồ sơ V1 có "8–12 h → 2,5 h" là giả thuyết | Đo thật: 1 reviewer kiểm 20 claim tay vs với GreenScan (thời gian, số evidence tìm đúng) → quy ra giờ công/báo cáo; ghi rõ n nhỏ | Thiết kế bài đo với Quỳnh ngay (protocol 1 trang), chạy thử 5 claim trong tuần 29/09 |
| "Giải triệt để" trên **tài liệu VN** | Mới 1 DN control (HPG) + 1 BVH | **≥ 5 DN VN** phát thải cao chạy end-to-end, mỗi DN có bảng soát tay | Nhánh dữ liệu v2 (A7, C1–C5) khởi động **tuần này**, không đợi sau Bán kết |
| **Nguồn đối chứng độc lập** (lớp B) | 0 tài liệu | Phụ lục QĐ 13/2024 (tCO₂tđ/cơ sở) parse + khớp mã CK; registry xử phạt; CBTT bất thường | Parse Phụ lục QĐ 13 là việc kỹ thuật thuần, Nhân làm được song song |
| **Quantum** (hồ sơ V1: "hướng Vòng 2") | Công thức QUBO đã sửa (G5), chưa code | A6: SA + QAOA simulator, benchmark 4 cột (Top-k · Greedy/MMR · ILP · SA/QAOA) × (coverage, redundancy, #chunks, runtime); **kết quả âm vẫn báo** | Chuẩn bị bộ instance benchmark (claim × 30 chunk ứng viên, có 5 thuộc tính) từ gold — cần gold trước |
| **Pilot / đối tác** (Vòng 2 tiêu chí 5: 90–100 = "đã có đối tác tiềm năng") | Chưa có | 1 buổi dùng thử với người thật (kiểm toán viên / cán bộ tín dụng xanh / giảng viên kế toán), biên bản phản hồi | Gửi lời mời **trước 10/10** để có lịch sau Bán kết |
| Legal layer ra finding thật | 100% INSUFFICIENT | ≥ 5 rule chạy thật, ≥ 3 ngành demo (QĐ 21 Phụ lục I) | S1.7 (3 rule) làm ngay; mở rộng sau |
| Ô bảng (hồ sơ V1 hứa) | Chưa | 1 → ≥ 3 bảng KNK có kiểm tra tay, `confidence` | Chỉ sau khi N1 xanh |

### 9.2 Lịch Chung kết đề xuất (chỉ hiệu lực nếu vào Chung kết)

| Tuần | Việc | Nghiệm thu |
| --- | --- | --- |
| 26/10–01/11 | Rút kinh nghiệm Bán kết (ghi mọi câu hỏi BGK vào QA_BANK); gold → 100; ≥ 3 DN VN mới chạy E2E + soát tay; bài đo lợi ích kinh tế | bảng Hứa → Đạt; gold 100 |
| 02/11–06/11 | A6 QUBO benchmark; eval report v2 (hold-out theo DN, CI); pilot session + biên bản; bảng tốc độ đa cấu hình | `EVALUATION_REPORT_v2.md`; benchmark 4 cột |
| 07/11–09/11 | Đóng băng; slide Vòng 3 = slide Vòng 2 + 3 slide mới (Hứa→Đạt, số liệu v2, quantum benchmark); dry-run | slide đóng băng 08/11 |
| 10/11 | Chung kết | — |

### 9.3 Nguyên tắc chống "vỡ" khi làm song song

- Từ nay tới 25/10 **không** code cho Chung kết; chỉ gieo ba thứ không tốn code: gán nhãn liên tục, mời pilot, khởi động dữ liệu v2.
- Mọi số Vòng 3 đều phải có snapshot riêng (`benchmark/baseline_<ngày>.json`, `ROUND3_READINESS_<ngày>.md`) — không sửa số Vòng 2.
- Quantum chỉ được nói ở Vòng 3 **kèm số đo**; nếu SA/QAOA không thắng greedy, slide nói đúng như vậy.

---

## Phụ lục — Lệnh tái hiện số đo mục 1

```bash
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe -m quantum_gw.cli evaluate
.venv/Scripts/python.exe data/real_cases/scripts/run_case.py --all
.venv/Scripts/python.exe -m quantum_gw.cli analyze \
  data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf \
  data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf \
  --roles claim_source,evidence --source-types internal,internal
# kết quả chi tiết: .quantum/runs/<run_id>/result.json → benchmark/baseline_2026-09-22.json
```
