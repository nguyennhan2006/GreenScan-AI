# Dữ liệu — bản đồ sáu vùng

```text
data/
├── sample/       Demo tổng hợp (tiếng Việt, chạy được ngay, không cần tải gì)
├── golden/       Bộ acceptance-test cho CI — `quantum-agent evaluate`
├── real_cases/   Pilot case THẬT: 4 case đã có phán quyết + 2 control Việt Nam
├── crawl/        Corpus doanh nghiệp VN: 670 tài liệu / 21 doanh nghiệp, 2021–2025
├── legal_cases/  29 target pháp lý quốc tế: 297 tài liệu (case pack + disclosure)
└── legal/        Văn bản pháp luật VN: bản gốc (raw/) + clause đã tách (clauses/)
```

| Vùng | Dùng khi nào | Lệnh |
| --- | --- | --- |
| `sample/` | Xem pipeline chạy end-to-end | `quantum-agent demo` |
| `golden/` | Kiểm tra hồi quy sau mỗi thay đổi | `quantum-agent evaluate` |
| `real_cases/` | Benchmark baseline với case thật, demo cho khách, chuẩn bị training | xem dưới |
| `crawl/` | Index/retrieval, chọn mẫu để gán nhãn, mở rộng bộ có nhãn | [crawl/README.md](crawl/README.md) |
| `legal_cases/` | Benchmark quốc tế, hard negatives | [../docs/greenscan-legal-case-crawl-pack/](../docs/greenscan-legal-case-crawl-pack/) |
| `legal/` | Kiểm tra pháp lý theo điều khoản | [../configs/legal/](../configs/legal/) |
| `gold/` | Gold set đang xây: phiên gán nhãn + quy ước | [gold/LABELING_CONVENTIONS.md](gold/LABELING_CONVENTIONS.md) |

**Hướng thu thập mới (2026-09-17):** [COLLECTION_PLAN_v2.md](COLLECTION_PLAN_v2.md) — DN phát thải cao có cơ sở trong QĐ 13/2024, mục môi trường + bảng chỉ số, nguồn đối chứng độc lập. Hàng đợi `crawl/vn30/curated/annotation_priority.jsonl` chỉ 26% on-topic — không gán nhãn thêm từ đó.

## Dùng nhanh real_cases

```bash
# Liệt kê case và kết quả kỳ vọng
python data/real_cases/scripts/run_case.py --list

# Chạy 1 case qua pipeline, so sánh kỳ vọng vs thực tế
python data/real_cases/scripts/run_case.py --case-id KDP-2024

# Chạy cả 4 case đã phán quyết
python data/real_cases/scripts/run_case.py --all

# Xuất request.json để gọi API / dán vào web UI
python data/real_cases/scripts/run_case.py --case-id KDP-2024 --to-request kdp.json
```

Chi tiết cấu trúc gói, giấy phép, quy tắc training: [real_cases/README.md](real_cases/README.md).

**Lưu ý pháp lý:** control Việt Nam **không** được gán nhãn greenwashing chỉ vì
thiếu dữ liệu; các case SEC là dàn xếp *without admission or denial* — giữ
nguyên qualifier khi trích dẫn.
