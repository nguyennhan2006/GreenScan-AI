# 07-presentation — Tài liệu trình bày

| Thư mục | Nội dung | Biên dịch |
| --- | --- | --- |
| [ban-ket-2026-10-25/](ban-ket-2026-10-25/README.md) | **Bán kết 25/10 (dùng bộ này):** 14 slide + lời nói + thời lượng theo 6 tiêu chí vòng 2, prompt sinh ảnh, demo 2:40 trên phiên thật, gói nộp 10/10, hỏi đáp bổ sung, khai báo AI (Điều 14) | — |
| [PIPELINE_DIAGRAM_BRIEF.md](PIPELINE_DIAGRAM_BRIEF.md) · [diagrams/](diagrams/) | Sơ đồ pipeline 16:9 (vi + en), mô hình thông tin và bản dựng vector | `python tools/make_pipeline_diagram.py` |
| [SLIDES_11_16_IMAGE_PROMPTS.md](SLIDES_11_16_IMAGE_PROMPTS.md) | Slide 11–16: prompt sinh ảnh, kịch bản nói 40 giây/slide, câu BGK hỏi + trả lời, bảng kiểm 7 dòng | — |
| [QA_DRILL.md](QA_DRILL.md) | 24 câu BGK gần như chắc chắn + khối kiến thức bắt buộc (60 giây/mục) | — |
| [QA_BANK_100_2026-09-20.md](QA_BANK_100_2026-09-20.md) | 100 câu đi sâu 4 mảng RAG · tài chính-kế toán · pháp lý · quantum: đáp án 30–60 giây theo *vấn đề → nguyên lý → triển khai → giới hạn*, câu truy vấn tiếp của BGK, nhãn ✅/🟡/📝 đã chạy / có hook / trên giấy | — |
| [technical_brief/](technical_brief/) | Tài liệu kỹ thuật tóm tắt 9 trang (LaTeX + PDF): công nghệ, phương pháp, logic kiểm chứng, dữ liệu, đánh giá, giới hạn, hướng phát triển (QUBO), giá trị | `xelatex GreenScan_Technical_Brief.tex` × 2 |

Yêu cầu: XeLaTeX (MiKTeX/TeX Live) và font Times New Roman, Arial, Consolas
(có sẵn trên Windows; trên Linux thay bằng `\setmainfont{Liberation Serif}`…).
Không dùng babel/polyglossia — nhãn tiếng Việt được đặt trực tiếp trong preamble.

Mọi con số trong tài liệu đo được từ kho mã tại thời điểm ghi trong tiêu đề;
khi cập nhật số liệu (gold set, bảng ngưỡng), sửa mục 6 và tăng số phiên bản.
Kế hoạch dẫn tới các số này: [../00-project/EXECUTION_PLAN_2026-09.md](../00-project/EXECUTION_PLAN_2026-09.md).

- **Paper tổng hợp 15/10/2026:** [paper/GREENSCAN_PAPER_2026-10-15.md](paper/GREENSCAN_PAPER_2026-10-15.md) — nghiên cứu liên quan, nguyên lý, dữ liệu, kết quả đã đo (T1 Kaggle v3, thang kích thước, A/B stance, hàng đợi), hạn chế, kế hoạch A–H; 9 hình dựng bằng `paper/make_figs.py`; bản PDF 16 trang `paper/GREENSCAN_PAPER_2026-10-15.pdf` (pandoc → HTML + `paper.css` → Edge headless).
