# AI-QUANTUM Real Case Pilot v0.1.0

Bộ pilot dữ liệu thật phục vụ test, demo và thiết kế flow phát hiện rủi ro greenwashing.

## Thành phần

- 4 case đã có quyết định của cơ quan quản lý hoặc tòa án:
  - Keurig Dr Pepper 2024
  - BNY Mellon Investment Adviser 2022
  - DWS Investment Management Americas 2023
  - KLM 2024
- 2 control document Việt Nam chưa có nhãn greenwashing:
  - Hòa Phát
  - Bảo Việt
- Claim JSONL, evidence JSONL và case JSON.
- PDF case packet tiếng Việt cho từng case.
- Registry nguồn chính thức.
- Script tải PDF/HTML gốc, tạo checksum và manifest.
- Training view có qualifier và phạm vi pháp lý.

## Tải nguồn gốc

```bash
python scripts/download_sources.py --dry-run --all
python scripts/download_sources.py --case-id KDP-2024
python scripts/download_sources.py --all
```

Các tài liệu gốc được tải vào `sources/originals/`. Gói này không tái phân phối PDF bên thứ ba.

## Chạy validation

```bash
python scripts/validate_pack.py
python scripts/create_training_view.py
```

## Dùng cho demo

Khuyến nghị chạy trước hai case:

1. `KDP-2024`: claim về khả năng tái chế và omission.
2. `BNY-2022`: claim về quy trình ESG và execution gap.

Sau đó chạy `DWS-2023` và `KLM-2024` để kiểm tra claim mơ hồ, marketing cấp tổ chức, kiểm soát quy trình và giới hạn phạm vi phán quyết.

## Dùng cho huấn luyện

Bộ này chưa đủ lớn để fine-tune. Chỉ các record `gold_after_second_reviewer` mới có thể đưa vào tập gold sau một reviewer độc lập thứ hai. Record `silver` cần thu thập đủ nguồn claim gốc trước.

Control Việt Nam tuyệt đối không được chuyển thành nhãn greenwashing chỉ vì thiếu dữ liệu.
