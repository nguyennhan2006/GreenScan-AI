# Bản đồ đường dẫn — cập nhật 2026-09-23

Một trang để biết **đọc gì, chạy gì, sửa ở đâu**. Mọi đường dẫn dưới đây đã kiểm tra tồn tại tại commit `b9b9cd6`.

## 1. Đọc theo thứ tự (người mới vào nhóm)

| # | Tài liệu | Trả lời câu hỏi |
| --- | --- | --- |
| 1 | [00-project/PROBLEM_DEFINITION.md](PROBLEM_DEFINITION.md) · [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Bài toán là gì, cho ai |
| 2 | [00-project/ARCHITECTURE_INVARIANTS.md](ARCHITECTURE_INVARIANTS.md) | **Hiến pháp kỹ thuật**: 10 bất biến, điều cấm, thứ tự làm việc — thi hành bằng `tests/test_architecture_invariants.py` |
| 3 | [00-project/ROUND2_READINESS_2026-09-22.md](ROUND2_READINESS_2026-09-22.md) | **Đang ở đâu** — snapshot số đo, chấm thử 6 tiêu chí, chuẩn bị Chung kết (§9). Không sửa số |
| 4 | [00-project/RESEARCH_PROGRAM_2026-09-22.md](RESEARCH_PROGRAM_2026-09-22.md) | **Cái gì đã chứng minh, cái gì là giả thuyết** — audit code 15 câu, RQ1–RQ10, 4 gate, câu được/không được nói trước BGK |
| 5 | [00-project/EXECUTION_PLAN_2026-09.md](EXECUTION_PLAN_2026-09.md) | Lịch tới 10/10 và 25/10, DoD D1–D15, kịch bản demo 7 phút |
| 6 | [00-project/ISSUES_REGISTER_2026-09.md](ISSUES_REGISTER_2026-09.md) | Sổ khúc mắc A–G + **mục N (N1–N5, đã đóng 23/09)** |
| 7 | [00-project/DECISIONS_LOG.md](DECISIONS_LOG.md) | Quyết định có hiệu lực (D-2026-09-18-01…08, D-2026-09-22-01…06) |
| 8 | [01-domain-audit/AUDIT_PROTOCOL.md](../01-domain-audit/AUDIT_PROTOCOL.md) · [MANUAL_SCORING_RUBRIC.md](../01-domain-audit/MANUAL_SCORING_RUBRIC.md) | Nghiệp vụ kiểm chứng |
| 9 | [07-presentation/QA_BANK_100_2026-09-20.md](../07-presentation/QA_BANK_100_2026-09-20.md) · [QA_DRILL.md](../07-presentation/QA_DRILL.md) | Bộ câu hỏi phản biện |
| 10 | [02-product/AUDITOR_WORKFLOW_POSITIONING.md](../02-product/AUDITOR_WORKFLOW_POSITIONING.md) | **Định vị sản phẩm (25/09)**: người dùng là kiểm toán viên thủ công; tự động hoá đọc·định vị·ghi chép; hàng đợi ưu tiên thay bảng verdict; ba lớp phải thêm |
| 11 | [07-presentation/PIPELINE_DIAGRAM_BRIEF.md](../07-presentation/PIPELINE_DIAGRAM_BRIEF.md) | **Pipeline tổng quan để vẽ sơ đồ**: 8 bước, input/output từng bước, 5 mô hình được huấn luyện, prompt sẵn cho AI sinh ảnh + bản Mermaid |

## 2. Dữ liệu

| Đường dẫn | Nội dung |
| --- | --- |
| [docs/04-data-ai/DATA_LAYERS.md](../04-data-ai/DATA_LAYERS.md) | **Contract 3 tầng raw · clean · extract** (`data-layers-v1`), trường bắt buộc theo `origin`, số đo khoảng trống |
| [docs/04-data-ai/TARGET_PIPELINE_AND_TRAINING.md](../04-data-ai/TARGET_PIPELINE_AND_TRAINING.md) | **Luồng đích đang nghiên cứu**: chỗ nào có mô hình, mô hình nào cho việc nào, dữ liệu thành dữ liệu huấn luyện ra sao, công thức QLoRA, thang B0–B4, việc cố ý không làm |
| [docs/04-data-ai/GreenScan_Mo_ta_truong_du_lieu_v1.pdf](../04-data-ai/GreenScan_Mo_ta_truong_du_lieu_v1.pdf) | Bản PDF cho khách hàng / thành viên không chuyên kỹ thuật (10 trang, tiếng Việt) |
| [src/quantum_gw/data/layers.py](../../src/quantum_gw/data/layers.py) | Nguồn sự thật của contract (pydantic) |
| [schemas/data/](../../schemas/data/) | JSON Schema sinh ra từ contract: `raw`, `clean`, `extract` |
| [data/README.md](../../data/README.md) | Bản đồ 6 vùng dữ liệu |
| [data/COLLECTION_PLAN_v2.md](../../data/COLLECTION_PLAN_v2.md) | Kế hoạch thu thập v2 (DN phát thải cao ∩ QĐ 13) |
| [data/gold/LABELING_CONVENTIONS.md](../../data/gold/LABELING_CONVENTIONS.md) | Quy ước gán nhãn gold |
| [data/crawl/README.md](../../data/crawl/README.md) | Corpus VN30: 670 tài liệu / 21 DN, chia split theo năm |
| [data/real_cases/README.md](../../data/real_cases/README.md) | 4 case có phán quyết + 2 control VN |
| [benchmark/baseline_2026-09-22.json](../../benchmark/baseline_2026-09-22.json) | **Baseline** — mọi tuyên bố "đã cải thiện" so với file này |
| [benchmark/progress_2026-09-23_p0-final.json](../../benchmark/progress_2026-09-23_p0-final.json) | Số đo sau khi đóng N1–N5 |

## 3. Code — nơi sửa khi verdict sai

| Vấn đề | File |
| --- | --- |
| Hai số có được so không | [verification/numeric_facts.py](../../src/quantum_gw/verification/numeric_facts.py) (`NumericFact`, `eligibility`) |
| Verdict và lý do | [agents/verifier.py](../../src/quantum_gw/agents/verifier.py) (`_status`, `_numeric_relation`, `missing_attributes`) |
| Cue ủng hộ / phủ định | [verification/stance.py](../../src/quantum_gw/verification/stance.py) + [configs/stance_cues.yaml](../../configs/stance_cues.yaml) |
| Câu nào thành claim | [agents/claim_extractor.py](../../src/quantum_gw/agents/claim_extractor.py) (`heading_reason`, `run`) |
| Điểm rủi ro, trần severity | [agents/scorer.py](../../src/quantum_gw/agents/scorer.py) + [configs/scoring_v1.yaml](../../configs/scoring_v1.yaml) |
| Tách câu, số, đơn vị | [utils/text.py](../../src/quantum_gw/utils/text.py) (`parse_quantities`, `split_sentences`, `join_wrapped_lines`) |
| Parse PDF, OCR, bảng | [parsers/documents.py](../../src/quantum_gw/parsers/documents.py) |
| Truy xuất BM25 + n-gram + RRF | [retrieval/hybrid.py](../../src/quantum_gw/retrieval/hybrid.py) · adapter [embeddings.py](../../src/quantum_gw/retrieval/embeddings.py), [rerank.py](../../src/quantum_gw/retrieval/rerank.py) |
| Tầng pháp lý | [legal/](../../src/quantum_gw/legal/) + [configs/legal/](../../configs/legal/) |
| Ghi 3 tầng dữ liệu mỗi run | [data/export.py](../../src/quantum_gw/data/export.py), [data/builders.py](../../src/quantum_gw/data/builders.py) |
| API · UI | [api.py](../../src/quantum_gw/api.py) · [frontend/src/](../../frontend/src/) |
| Cấu hình đường chạy mặc định | [configs/default.yaml](../../configs/default.yaml) · [configs/routing.yaml](../../configs/routing.yaml) |

## 4. Lệnh hay dùng

```bash
# chất lượng verdict
.venv/Scripts/python.exe -m pytest tests -q                      # toàn bộ suite
.venv/Scripts/python.exe -m pytest tests/test_verdict_traps.py   # lưới bẫy verdict
.venv/Scripts/python.exe -m quantum_gw.cli evaluate              # golden 4 case
.venv/Scripts/python.exe data/real_cases/scripts/run_case.py --all   # 4 case có phán quyết
.venv/Scripts/python.exe tools/hpg_progress.py --label <nhãn>    # chạy HPG, so với baseline

# dữ liệu
.venv/Scripts/python.exe tools/data_contract.py validate-run     # kiểm tra 3 tầng của run mới nhất
.venv/Scripts/python.exe tools/data_contract.py migrate-crawl    # dựng lại corpus theo contract (~15 s)
.venv/Scripts/python.exe tools/data_contract.py report <thư mục> # độ phủ từng trường
.venv/Scripts/python.exe tools/label_session.py sample --name <tên>   # tạo phiên gán nhãn

# chạy sản phẩm
.venv/Scripts/python.exe -m quantum_gw.cli demo
.venv/Scripts/python.exe -m quantum_gw.cli analyze <pdf...> --roles claim_source,evidence
uvicorn quantum_gw.api:app --reload ; cd frontend && npm run dev
```

## 5. Mốc và trạng thái

| Mốc | Ngày | Trạng thái |
| --- | --- | --- |
| Product freeze | 10/10/2026 | P0 correctness **xong 23/09**; tiếp theo P1 đo lường (gold) |
| Bán kết | 25/10/2026 | dùng release đã đóng băng |
| Chung kết | 10/11/2026 | chuẩn bị theo readiness §9 |

Gate A–D (thay cho "% sẵn sàng"): xem [RESEARCH_PROGRAM §6](RESEARCH_PROGRAM_2026-09-22.md).
