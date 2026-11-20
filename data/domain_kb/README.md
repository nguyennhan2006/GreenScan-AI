# Kho tri thức nền (domain KB), v1, 14/11/2026

Quyết định: D-2026-11-14-02. Code: `src/quantum_gw/knowledge/domain_kb.py`. Công cụ: `domain_lookup` (MCP + harness).

## Để làm gì

Trợ lý của GreenScan cần hiểu lĩnh vực: claim chuẩn trông thế nào, cần bằng chứng gì, dấu hiệu tẩy xanh nào, tính thế nào.
Trước đây LLM trả lời các câu này từ trí nhớ, không có nguồn. Kho này cho nó một nguồn có trích dẫn, chạy ngoại tuyến.

## Ranh giới (không được phá)

1. **Không phải bằng chứng.** Mọi kết quả mang `source_type: tri_thuc_nen` và câu nhắc "không phải bằng chứng trong tài liệu
   của doanh nghiệp". Số trong kho là ví dụ minh hoạ.
2. **Không đi vào kết luận.** Chỉ `mcp_tools.py` được import `quantum_gw.knowledge`; kiểm thử
   `test_background_knowledge_is_never_evidence` (tests/test_architecture_invariants.py) chặn mọi import khác. Harness bỏ
   câu trả lời của LLM nếu nó nêu một mã kết luận mà chỉ kho tri thức có, không công cụ sản phẩm nào đưa ra.
3. **Cách tính là code.** Trường `code` trỏ vào hàm thật (kiểm thử bắt hàm phải tồn tại); trường `check` là ví dụ số được
   kiểm thử tính lại. LLM giải thích, không tự tính.

## Nguồn, mỗi loại một chỗ

| Loại | Ở đâu | Mã mục |
|---|---|---|
| Khái niệm, dấu hiệu, cách tính, claim chuẩn | `entries_v1.yaml` (viết tay) | `C-…`, `SIG-…`, `F-…`, `P-…` |
| Vụ việc đã có phán quyết / dàn xếp | `data/real_cases/cases/*/case.json` | `CASE-<case_id>` |
| Văn bản pháp lý | `configs/legal/LEGAL_SOURCE_REGISTRY.yaml` | `LEGAL-<id>` |

Vụ việc và văn bản được nạp lúc chạy, không chép, để không lệch nguồn. Tài liệu đối chứng Việt Nam (`VN-*-CONTROL`)
không phải vụ việc nên không nạp.

## Một mục claim chuẩn gồm gì

`claim_good` (claim chuẩn, đủ thuộc tính) · `claim_weak` (cùng ý, thiếu thuộc tính) · `attributes` (thuộc tính bắt buộc) ·
`evidence` (bằng chứng cần tìm, ở đâu) · `signals` (mã các dấu hiệu rủi ro) · `method` + `code` + `check` (cách tính / kiểm) ·
`system` (sản phẩm hiện làm gì) · `codes` (mã lý do / kết luận để tra theo mã) · `sources` (gắn nhãn [NGOÀI] / [KIẾN THỨC NỀN]).

## Nguồn gốc và duyệt

Các mục viết tay do Claude soạn ngày 14/11 từ kiến thức nền và tài liệu của dự án (`labeler: claude-opus-5-5`,
`review_status: pending_human_review`). Người duyệt: Thảo (pháp lý, văn bản, nguồn), Quỳnh (nghiệp vụ, claim chuẩn,
dấu hiệu). Duyệt xong một mục thì đổi `review_status` của mục đó thành `reviewed` và ghi tên người duyệt vào `reviewer`.
Kỳ kiểm kê, hạn nộp, điều khoản pháp lý cụ thể **không** được viết từ trí nhớ: trỏ về sổ đăng ký pháp lý.

## Thêm hoặc sửa mục

```bash
.venv/Scripts/python.exe -m quantum_gw.knowledge.domain_kb validate          # 0 lỗi mới được commit
.venv/Scripts/python.exe -m quantum_gw.knowledge.domain_kb search "năm gốc là gì"
.venv/Scripts/python.exe -m pytest tests/test_domain_kb.py tests/test_architecture_invariants.py
```

Tắt kho khi cần: `QUANTUM_DOMAIN_KB=0`.

## Còn mở

- 52 mục viết tay chưa ai duyệt.
- Chưa có mục cho các ngành phát thải cao cụ thể (thép, xi măng, điện): hệ số, đơn vị sản lượng, công nghệ (BF-BOF / EAF).
- Dữ liệu router Claude ngày 13/11 chưa có nhãn `explain_concept` (scope-v1.1); dựng lại trước khi huấn luyện router.
- Tra cứu là từ khoá + idf; khi kho vượt vài trăm mục mới cần xét truy xuất ngữ nghĩa.
