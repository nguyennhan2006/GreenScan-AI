# Tài liệu GreenScan AI

Thư mục này trước đây có **hai hệ thống song song**: các thư mục đánh số
`00-…05-` và 10 file `.md` rời ở gốc mô tả cùng chủ đề nhưng ngắn hơn và cũ hơn
(`ARCHITECTURE.md` 2 KB cạnh `03-architecture/` 6 file). Các file gốc đã được
chuyển vào đúng nhóm; mọi liên kết trỏ tới chúng đã được cập nhật.

Quy ước: **một chủ đề một nơi**, đánh số theo thứ tự đọc từ bài toán tới vận hành.

## Cấu trúc

| Thư mục | Nội dung |
| --- | --- |
| [00-project/](00-project/) | Bài toán, phạm vi, thuật ngữ, roadmap, backlog, [báo cáo kiểm thử lõi 2026-09-20](00-project/CORE_FEATURE_TEST_REPORT_2026-09-20.md) |
| [01-domain-audit/](01-domain-audit/) | Taxonomy greenwashing, chuẩn bằng chứng, rubric chấm tay, checklist reviewer |
| [02-product/](02-product/) | MVP scope, personas, user stories, đặc tả đầu ra |
| [03-architecture/](03-architecture/) | Kiến trúc evidence-first, pipeline, API, ranh giới module, lưu trữ |
| [04-data-ai/](04-data-ai/) | Schema dữ liệu, trích xuất, retrieval, xác minh, chấm rủi ro, đánh giá |
| [05-ui/](05-ui/) | Dashboard, evidence card, luồng review, đánh giá UI, [đặc tả production backend→UI + prompt sinh ảnh](05-ui/PRODUCTION_UI_SPEC_2026-09-20.md) |
| [06-operations/](06-operations/) | Bảo mật & quản trị, quy trình nhóm, thiết lập GitHub |
| [07-presentation/](07-presentation/) | Tài liệu trình bày cho hội đồng: technical brief (LaTeX/PDF) |
| [decisions/](decisions/) | ADR |
| [research/](research/) · [reference/](reference/) | Ghi chú nghiên cứu, tham chiếu ngoài |

## Hai pack độc lập

Giữ nguyên dạng pack vì mỗi bộ tự chứa registry + schema + script và được dùng
như một đơn vị:

- [greenscan-legal-case-crawl-pack/](greenscan-legal-case-crawl-pack/) — 29
  target pháp lý quốc tế, kèm gate chất lượng và runbook crawl.
  Chạy: `python tools/crawl_legal_cases.py`
- [GreenScan_AI_Research_Source_Pack_2026-08-13/](GreenScan_AI_Research_Source_Pack_2026-08-13/) — nguồn nghiên cứu tham chiếu.

## Tài liệu nằm ngoài thư mục này

Có chủ đích — chúng đặt cạnh thứ chúng mô tả:

| Ở đâu | Nội dung |
| --- | --- |
| [../data/README.md](../data/README.md) | Bản đồ 5 vùng dữ liệu |
| [../data/crawl/README.md](../data/crawl/README.md) | Corpus VN30, cách tái lập, các bẫy đã gặp |
| [../data/crawl/COLLECTION_REPORT_20260807.md](../data/crawl/COLLECTION_REPORT_20260807.md) | Báo cáo thu thập + 7 lỗi đã sửa |
| [../data/real_cases/README.md](../data/real_cases/README.md) | Pilot case có phán quyết |
| [../configs/legal/](../configs/legal/) | Registry văn bản pháp luật + rule pack |
| [../schemas/legal/](../schemas/legal/) | Schema document / clause / rule / finding |
