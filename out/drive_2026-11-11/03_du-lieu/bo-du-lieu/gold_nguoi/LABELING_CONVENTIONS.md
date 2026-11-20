# Quy ước gán nhãn gold set

Rút ra từ lô thử `sessions/2026-09-17_trial01.jsonl`. Mỗi quy ước có ví dụ thật.
Công cụ: `python tools/label_session.py {sample|show|set|stats}`.

## Nhãn là gì

Nhãn = **mức đầy đủ của bằng chứng cho một tuyên bố**, không phải "doanh nghiệp có greenwashing".
Control Việt Nam không bị gán nhãn xấu chỉ vì thiếu dữ liệu.

## Q1. `is_claim` — câu này có phải tuyên bố môi trường của doanh nghiệp không?

| Trả lời | Khi nào | Ví dụ từ lô thử |
| --- | --- | --- |
| `no` | Số liệu vĩ mô, thống kê quốc gia | DPR: "GDP Việt Nam 2022 tăng 8,02%" · DHG: "tỷ lệ bao phủ BHYT 92%" |
| `no` | Kế hoạch kinh doanh / tài chính | DHG: "tăng trưởng bình quân 2022–2025: 8–10%/năm" · PAN: business plan 2018 |
| `no` | Chỉ tiêu xã hội / quản trị (ngoài phạm vi MVP) | TRA: "thu nhập NLĐ tăng tối thiểu 8%" |
| `no` | Tiêu đề mục, mục lục, chú giải thuật ngữ | (thường gặp trong hàng đợi cũ) |
| `yes` | DN nói về **kết quả, mục tiêu hoặc trạng thái môi trường của chính mình** | PNJ: mục tiêu giảm KNK 2% cho 2 nhà máy · VNM: nhà máy đạt trung hoà carbon PAS 2060 |
| `unsure` | Không rõ chủ thể (DN hay ngành/quốc gia) | ghi notes, trọng tài quyết |

`no` thì dừng — không gán thuộc tính hay verdict.

## Q2. Năm thuộc tính — `present | partial | missing | na`

| Thuộc tính | present | partial | missing | na |
| --- | --- | --- | --- | --- |
| `metric` | chỉ số gọi tên rõ (KNK Scope 1+2, điện tiêu thụ, nước…) | trạng thái định tính ("trung hoà carbon", "xanh") | không có chỉ số | — |
| `value_unit` | có số **và** đơn vị | có số không đơn vị, hoặc đơn vị không chuẩn | không có số | claim trạng thái không cần số (ghi notes) |
| `period` | kỳ báo cáo / năm mục tiêu rõ | "hàng năm", "trong 1 năm" không nói năm nào | không có mốc thời gian | — |
| `baseline` | năm gốc rõ | nhắc "so với trước" không nói năm | claim tăng/giảm/mục tiêu **không có năm gốc** | claim trạng thái, không phải tăng/giảm |
| `scope` | Scope 1/2/3 **và** ranh giới tổ chức (hợp nhất/cơ sở) | chỉ một trong hai | không nói | — |

Ví dụ PNJ (mục tiêu 2%/năm, 2 nhà máy, tấn C/1.000 sp): metric present · value_unit present · period **partial** (không năm mục tiêu) · baseline **missing** · scope **partial** (có cơ sở, không Scope).

## Q3. Quan hệ từng đoạn bằng chứng

| Nhãn | Nghĩa |
| --- | --- |
| `supports` | xác nhận đúng chỉ số, cùng kỳ/phạm vi |
| `partial` | cùng chủ đề, xác nhận một phần (khác kỳ, khác chỉ số liên quan, chỉ xác nhận có chương trình) |
| `contradicts` | phủ định, hoặc số/xu hướng khác trên **cùng chỉ số cùng kỳ** |
| `context` | liên quan nhưng không xác nhận/bác bỏ — **kể cả khi đoạn đó chính là câu claim** (self-match) |
| `not_relevant` | không liên quan |

Quy ước: đoạn trùng chính câu claim luôn là `context`, không bao giờ `supports`.

## Q4. Verdict

| Verdict | Điều kiện |
| --- | --- |
| `SUPPORTED` | ≥ 1 đoạn `supports` từ nguồn khác câu claim, không còn `contradicts` |
| `PARTIALLY_SUPPORTED` | chỉ có `partial`; hoặc `supports` nhưng thiếu ≥ 2 thuộc tính bắt buộc |
| `CONTRADICTED` | ≥ 1 `contradicts` **cùng chỉ số**; mục tiêu khác chỉ số (ví dụ 1%/năm năng lượng vs 2% KNK) **không** đủ — ghi notes "mâu thuẫn nội bộ tiềm ẩn" |
| `INSUFFICIENT_EVIDENCE` | không có đoạn nào `supports`/`partial`/`contradicts` trong bộ ứng viên |
| `UNSUPPORTED` | đã tìm trong nguồn được cấp **và** nguồn đó lẽ ra phải chứa số liệu (ví dụ mục 6 TT 96) nhưng không có |

### Quy ước chờ chốt (từ lô thử, cần quyết định của nhóm)

- [ ] **Chứng nhận bên thứ ba** (PAS 2060, ISO 14064, "đầu tiên tại VN") khi bộ ứng viên chỉ có tài liệu của chính DN: `PARTIALLY_SUPPORTED` hay `INSUFFICIENT_EVIDENCE`?
  Đề xuất: `INSUFFICIENT_EVIDENCE` + notes "cần chứng chỉ công khai của tổ chức chứng nhận" — nhất quán với nguyên tắc "bằng chứng độc lập trước", và tạo yêu cầu thu thập lớp B.
- [ ] **Hai mục tiêu khác nhau trong cùng báo cáo** (PNJ: 2% KNK vs 1%/năm năng lượng): giữ `PARTIALLY_SUPPORTED` + notes, hay tạo nhãn phụ `internal_inconsistency=true`?
  Đề xuất: thêm trường notes có tiền tố `INCONSISTENCY:` để lọc được sau, chưa thêm nhãn mới.

## Ghi nhãn

```bash
python tools/label_session.py set <session> <idx> is_claim=no notes="số liệu vĩ mô" --labeler quynh
python tools/label_session.py set <session> <idx> is_claim=yes claim_type=emissions_reduction \
    attrs.metric=present attrs.value_unit=present attrs.period=partial attrs.baseline=missing attrs.scope=partial \
    evidence.1=context evidence.2=context evidence.3=partial evidence.4=partial \
    verdict=PARTIALLY_SUPPORTED notes="INCONSISTENCY: 2% KNK vs 1%/năm năng lượng" --labeler quynh
```

Hai người gán **độc lập** trên cùng session file bản sao (`_quynh`, `_thao`); trọng tài gộp; κ tính trên `is_claim`, `verdict` và từng thuộc tính.
