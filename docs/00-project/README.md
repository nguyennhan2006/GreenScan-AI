# 00-project — Project Foundation

Thư mục này là lớp tài liệu nền tảng cho dự án **Greenwashing Detection — Evidence-first Architecture**. Mục tiêu của thư mục `00-project` là đồng bộ cách hiểu giữa ChatGPT, Claude Code và team phát triển trước khi đi vào nghiệp vụ kiểm toán, schema dữ liệu, pipeline AI và triển khai phần mềm.

## Mục tiêu của bộ tài liệu 00

Bộ tài liệu này trả lời bốn câu hỏi nền tảng:

1. Dự án này là gì và giải quyết vấn đề nào?
2. Vì sao bài toán greenwashing trong tài chính Việt Nam có giá trị thực tiễn?
3. Các khái niệm chính cần hiểu giống nhau là gì?
4. Các nguồn nào đang được dùng làm nền tảng phân tích?

## File trong thư mục

| File | Vai trò | Người dùng chính |
|---|---|---|
| `PROJECT_BRIEF.md` | Tóm tắt dự án, mục tiêu, phạm vi, người dùng, output chính | Product owner, developer, reviewer |
| `PROBLEM_DEFINITION.md` | Định nghĩa vấn đề greenwashing trong bối cảnh tài chính Việt Nam | Research lead, reviewer, AI agent |
| `GLOSSARY.md` | Chuẩn hóa thuật ngữ nghiệp vụ, pháp lý, ESG, AI/RAG | Toàn team, ChatGPT, Claude Code |
| `README.md` | Hướng dẫn cách dùng thư mục 00 và danh mục nguồn ban đầu | Toàn team |
| `ROADMAP.md` · `IMPLEMENTATION_BACKLOG.md` | Lộ trình phiên bản và backlog ưu tiên | Product owner, developer |
| `ISSUES_REGISTER_2026-09.md` | Sổ khúc mắc A–G với phương án, chủ sở hữu, nghiệm thu; tick khi đóng | Toàn team |
| `EXECUTION_PLAN_2026-09.md` | **Kế hoạch 6 tuần tới sản phẩm trình bày được** — trạng thái đo được, Definition of Done, sprint, kịch bản demo | Toàn team |
| `ROUND2_READINESS_2026-09-22.md` | **Source of truth readiness Vòng 2** (snapshot 22/09, không sửa số): số đo, chấm thử 6 tiêu chí, N1–N5, thứ tự ưu tiên, hard gate, chuẩn bị Chung kết (§9). Số đo gốc: `benchmark/baseline_2026-09-22.json` | Toàn team |
| `RESEARCH_PROGRAM_2026-09-22.md` | **Đi kèm readiness:** audit code 15 câu (file:line), bảng research ↔ code ↔ test ↔ dữ liệu ↔ thí nghiệm ↔ nghiệm thu (RQ1–RQ10), 4 trạng thái năng lực, 4 gate, tuyên bố được/chưa được phép nói | Toàn team |
| `CORE_FEATURE_TEST_REPORT_2026-09-20.md` | Báo cáo kiểm thử tính năng cốt lõi 20/09 (D1–D9 đã sửa) | Nhân, reviewer |

## Nguyên tắc sử dụng

- Mọi tài liệu phía sau trong `/docs/01-domain-audit`, `/docs/03-architecture`, `/docs/04-data-ai` phải bám theo định nghĩa ở thư mục này.
- Claude Code không nên tự diễn giải lại greenwashing hoặc tự đặt lại thuật ngữ nếu chưa cập nhật `GLOSSARY.md`.
- Khi phát hiện nguồn mới hoặc luật mới, cập nhật phần “Source register” bên dưới trước, sau đó mới cập nhật nội dung chính.
- Nếu một thông tin pháp lý chưa được xác minh từ nguồn chính thức, đánh dấu là `TO_VERIFY` thay vì dùng như căn cứ cuối cùng.

## Source register ban đầu

| Nhóm nguồn | Nguồn | Cách dùng trong dự án | Trạng thái |
|---|---|---|---|
| Định nghĩa greenwashing tài chính | ESMA / ESAs — common understanding of greenwashing | Làm nền cho định nghĩa: tuyên bố/hành động/truyền thông bền vững không phản ánh rõ ràng và công bằng hồ sơ bền vững thực chất, có thể gây hiểu lầm cho nhà đầu tư/thị trường | Verified web |
| Chuẩn báo cáo bền vững cho nhà đầu tư | IFRS Sustainability Disclosure Standards / ISSB | Dùng để hiểu disclosure phục vụ quyết định của nhà đầu tư và yêu cầu thông tin so sánh toàn cầu | Verified web |
| Chuẩn báo cáo tác động | GRI Standards | Dùng làm tham chiếu về tác động kinh tế, môi trường, con người và material topics | Verified web |
| Taxonomy khu vực | ASEAN Taxonomy for Sustainable Finance | Dùng làm nguồn tham chiếu taxonomy khu vực, đặc biệt khi xây bộ đối chiếu “xanh” | Verified web, access hạn chế |
| Bối cảnh pháp lý Việt Nam | Luật BVMT 2020, Thông tư 17/2022/TT-NHNN, Quyết định 21/2025/QĐ-TTg | Dùng để xác định bối cảnh tín dụng xanh, trái phiếu xanh, quản lý rủi ro môi trường và phân loại xanh | Project-context; cần đối chiếu URL chính thức ở bước nguồn pháp lý |
| Tài liệu kiến trúc nội bộ | `greenwashing-detection-architecture.html` | Làm nền cho pipeline evidence-first: claim → evidence → verification → score → explanation | Local project file |

## Cách cập nhật nguồn

Khi thêm nguồn mới, ghi theo mẫu:

```md
### [Tên nguồn]
- URL:
- Loại nguồn: Official / Academic / Legal / News / Project-context
- Độ tin cậy: High / Medium / Low
- Dùng cho phần nào:
- Ghi chú:
```

## Quy tắc cho AI agents

Claude Code và các AI agent khác phải đọc theo thứ tự:

1. `README.md`
2. `PROJECT_BRIEF.md`
3. `PROBLEM_DEFINITION.md`
4. `GLOSSARY.md`

Sau khi đọc, agent phải giữ nguyên các enum/thuật ngữ cốt lõi:

- `Greenwashing risk`
- `Green claim`
- `Evidence-first`
- `Supported`
- `Partially supported`
- `Unsupported`
- `Contradicted`
- `Insufficient evidence`
- `Risk score 0–100`

## Next actions

- Tạo `docs/01-domain-audit/GREENWASHING_TAXONOMY.md` từ các nhóm claim trong `PROBLEM_DEFINITION.md`.
- Tạo `docs/01-domain-audit/AUDIT_PROTOCOL.md` để mô phỏng kiểm toán viên chấm thủ công.
- Tạo `docs/04-data-ai/DATA_SCHEMA.md` để Claude Code triển khai các object: Document, Claim, Evidence, VerificationResult, RiskScore.
