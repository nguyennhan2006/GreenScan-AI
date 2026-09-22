# GreenScan Legal-Case Crawl Pack

Bộ tài liệu này dùng trực tiếp cho **Claude Code** và crawler của GreenScan AI để mở rộng corpus hiện tại từ **21 doanh nghiệp đã thu được dữ liệu** bằng **29 target có hồ sơ pháp lý/quản lý chính thức về tuyên bố môi trường/ESG gây hiểu lầm**.

## Mục tiêu chính

- Giữ cửa sổ corporate corpus **2021–2025** để so sánh với corpus Việt Nam hiện tại.
- Với 29 target mới, thu **case pack pháp lý/quản lý** và disclosure doanh nghiệp/quỹ tương ứng.
- Tách tuyệt đối `case_entity` khỏi `reporting_entity` khi case thuộc công ty con, brand hoặc pháp nhân địa phương.
- Không biến `company_has_case=true` thành nhãn greenwashing cho toàn bộ doanh nghiệp, tài liệu hoặc claim.
- Chỉ claim/advertisement/product representation được authority xem xét mới có ground-truth pháp lý tương ứng.
- Mọi tài liệu phải có provenance, checksum, source URL, access time và collection status.

## Cấu trúc pack

- `CLAUDE_CRAWL.md` — instruction bắt buộc cho Claude Code.
- `docs/00_CURRENT_STATE_AND_BOUNDARIES.md` — hiện trạng corpus 2026-08-07 và các ranh giới không được phá.
- `docs/01_OBJECTIVES_AND_DEFINITION_OF_DONE.md` — mục tiêu, coverage và Definition of Done.
- `docs/02_TARGET_29_AND_MANDATORY_URLS.md` — 29 case + URL pháp lý + seed official.
- `docs/03_REQUIRED_DOCUMENTS_PER_PROFILE.md` — tài liệu bắt buộc tùy loại entity.
- `docs/04_CRAWL_RUNBOOK.md` — hướng dẫn crawl chi tiết.
- `docs/05_SOURCE_DISCOVERY_AND_FALLBACK.md` — quy tắc tìm link, fallback và 403/JS pages.
- `docs/06_GROUND_TRUTH_AND_LABEL_POLICY.md` — cách dùng phán quyết/ruling mà không tạo label sai.
- `docs/07_METADATA_PROVENANCE_AND_STORAGE.md` — schema lưu trữ và naming.
- `docs/08_DATA_QUALITY_RELEASE_GATES.md` — release gates trước parsing/annotation/benchmark.
- `docs/09_FAILURE_RECOVERY_PLAYBOOK.md` — xử lý lỗi đã gặp và lỗi dự kiến.
- `docs/10_REPORTING_REQUIREMENTS.md` — báo cáo bắt buộc sau mỗi run.
- `config/legal_case_targets.yaml` — registry machine-readable 29 target.
- `config/seed_urls.csv` — URL list để crawler/discovery dùng trực tiếp.
- `config/doc_family_profiles.yaml` — loại tài liệu yêu cầu theo entity profile.
- `config/source_registry.yaml` — regulator registry.
- `config/crawl_targets.yaml` — mục tiêu coverage.
- `templates/*.json` — schema metadata.
- `templates/*.csv` — trạng thái thu thập và review.
- `scripts/validate_registry.py` — validate đủ 29 target và trường bắt buộc.
- `prompts/CLAUDE_CODE_START.md` — prompt khởi động.

## Chạy trước khi crawl

```bash
python scripts/validate_registry.py
```

Sau đó Claude Code phải audit codebase và tạo `reports/PRE_CRAWL_AUDIT.md` trước khi tải bất kỳ tài liệu mới nào.

## Hai queue tách biệt

**Primary expansion:** 21 doanh nghiệp hiện có + 29 legal-case targets = 50 entities chính.

**VN30 recovery queue:** 9 doanh nghiệp Việt Nam chưa có tài liệu (`acg`, `bmp`, `chp`, `dmc`, `nt2`, `ocb`, `qns`, `tlg`, `tng`) vẫn là một queue riêng. Nếu thu hồi đủ 9 thì corpus có thể vượt 50 entities; không dùng 9 này để thay đổi label distribution một cách âm thầm.
