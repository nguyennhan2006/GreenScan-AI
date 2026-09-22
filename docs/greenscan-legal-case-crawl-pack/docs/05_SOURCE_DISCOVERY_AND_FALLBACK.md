# 05 — Source discovery và fallback

## Thứ tự ưu tiên nguồn

1. Authority/regulator/court official case source.
2. Official corporate investor/reporting hub.
3. Official fund/product disclosure hub.
4. Official securities filing portal for the entity/jurisdiction.
5. Official corporate newsroom/archive.
6. Third-party source chỉ để discover original URL; không tự động đưa vào primary corpus.

## Không được làm

- Không crawl Google/Bing result page như corpus.
- Không dùng URL đoán theo năm nếu chưa verify.
- Không bypass CAPTCHA/auth/paywall/access control.
- Không `verify=False`.
- Không đổi 403 thành retry vô hạn.
- Không dùng Internet Archive tự động như nguồn chính nếu chưa có policy/license review.

## Khi official listing là JavaScript

1. Inspect HTML for embedded JSON/state.
2. Inspect official XHR/fetch endpoint through existing JS harvester/browser tooling.
3. Add endpoint only after domain validation and a reproducible test.
4. Save discovery evidence in `source_discovery.json`.
5. Add regression fixture before bulk crawl.

## Khi robots.txt lỗi

Giữ policy đã regression-tested trong codebase:

- valid robots -> honor rules;
- 4xx -> không silently coi toàn site là disallow;
- 5xx / network / TLS transport failure -> fail-safe, queue review/retry;
- log exact outcome.

## Khi corporate entity đổi tên/merge

Không merge dữ liệu chỉ bằng string similarity. Tạo entity relation với effective date. Ví dụ Active Super → Vision Super sau 1/3/2025; historical 2021–2024 vẫn thuộc historical reporting entity.

## Khi không có đủ 5 năm

Ghi reason code thay vì tìm file thay thế kém tin cậy:

- `NOT_PUBLISHED`
- `ENTITY_NOT_EXISTING_THAT_YEAR`
- `REPORT_INTEGRATED_ELSEWHERE`
- `OFFICIAL_ARCHIVE_INCOMPLETE`
- `BLOCKED_BY_SOURCE`
- `NOT_FOUND_AFTER_OFFICIAL_SEARCH`

Mỗi reason phải kèm `checked_urls[]`, `checked_at`, `notes`.
