# 07-presentation — Tài liệu trình bày

| Thư mục | Nội dung | Biên dịch |
| --- | --- | --- |
| [QA_DRILL.md](QA_DRILL.md) | 24 câu BGK gần như chắc chắn + khối kiến thức bắt buộc (60 giây/mục) | — |
| [QA_BANK_100_2026-09-20.md](QA_BANK_100_2026-09-20.md) | 100 câu đi sâu 4 mảng RAG · tài chính-kế toán · pháp lý · quantum: đáp án 30–60 giây theo *vấn đề → nguyên lý → triển khai → giới hạn*, câu truy vấn tiếp của BGK, nhãn ✅/🟡/📝 đã chạy / có hook / trên giấy | — |
| [technical_brief/](technical_brief/) | Tài liệu kỹ thuật tóm tắt 9 trang (LaTeX + PDF): công nghệ, phương pháp, logic kiểm chứng, dữ liệu, đánh giá, giới hạn, hướng phát triển (QUBO), giá trị | `xelatex GreenScan_Technical_Brief.tex` × 2 |

Yêu cầu: XeLaTeX (MiKTeX/TeX Live) và font Times New Roman, Arial, Consolas
(có sẵn trên Windows; trên Linux thay bằng `\setmainfont{Liberation Serif}`…).
Không dùng babel/polyglossia — nhãn tiếng Việt được đặt trực tiếp trong preamble.

Mọi con số trong tài liệu đo được từ kho mã tại thời điểm ghi trong tiêu đề;
khi cập nhật số liệu (gold set, bảng ngưỡng), sửa mục 6 và tăng số phiên bản.
Kế hoạch dẫn tới các số này: [../00-project/EXECUTION_PLAN_2026-09.md](../00-project/EXECUTION_PLAN_2026-09.md).
