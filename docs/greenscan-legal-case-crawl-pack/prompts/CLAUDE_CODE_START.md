# Claude Code Start Prompt — Legal Case Crawl Expansion

Bạn đang làm việc trong repo GreenScan AI. Hãy dùng toàn bộ pack này làm specification.

## Mục tiêu

Mở rộng corpus hiện tại (670 docs / 21 companies / 2021–2025) bằng 29 legal/regulatory case targets trong `config/legal_case_targets.yaml`, giữ claim-level ground truth và provenance.

## Bước bắt buộc

1. Đọc `CLAUDE_CRAWL.md` và tất cả `docs/*.md`.
2. Chạy `python scripts/validate_registry.py`.
3. Audit codebase hiện tại đối chiếu 7 regression bugs trong `docs/00_CURRENT_STATE_AND_BOUNDARIES.md`.
4. Tạo `reports/PRE_CRAWL_AUDIT.md` gồm:
   - module/file nào chịu trách nhiệm discovery/download/robots/TLS/dedup/year-resolution/JSONL;
   - test nào đã có;
   - gap nào cần sửa trước crawl.
5. Không crawl bulk cho tới khi preflight tests pass.
6. Implement/load registry-driven queue, không hardcode 29 companies trong code.
7. Thu authority case pack trước, corporate disclosures sau.
8. Với mỗi target tạo coverage status 2021–2025 theo `profile`.
9. Không tự động gán greenwashing label từ company/case metadata.
10. Sau run tạo đủ các report trong `docs/10_REPORTING_REQUIREMENTS.md`.

## Acceptance

- registry 29/29 valid;
- 29/29 case URLs attempted and status logged;
- no silent zero-doc source;
- SHA-256 + provenance for every downloaded artifact;
- explicit year/status for each required year/family cell;
- 0 cross-split duplicates before annotation release;
- existing JSONL/robots/TLS regressions remain fixed.

Nếu một URL official đã đổi, không tự đoán direct PDF. Hãy discover lại từ official domain, cập nhật registry kèm evidence và ghi changelog.
