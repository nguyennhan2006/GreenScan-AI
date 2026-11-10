# Luận văn GreenScan AI: dàn ý và quy ước viết

*Lập 05/11/2026. Người đọc: Hội đồng / giảng viên chấm (chuyên gia tài chính–kế toán, AI, pháp lý) và người đọc kỹ thuật muốn tái lập. Tác giả duyệt: Nhân.*

**Tên đề tài:** GreenScan AI: hệ thống kiểm chứng tuyên bố môi trường trong công bố của doanh nghiệp Việt Nam theo hướng "bằng chứng trước" — mô hình đọc, quy tắc quyết định, con người duyệt.

## Dàn ý (file / độ dài mục tiêu)
| File | Nội dung | Từ |
|---|---|---|
| `01_MO_DAU.md` | Bối cảnh (tài chính xanh, công bố ESG ở VN, tẩy xanh); vấn đề thực tiễn của kiểm toán viên / ngân hàng / doanh nghiệp; vì sao không hỏi "AI có phát hiện tẩy xanh không" mà hỏi "tuyên bố này có bằng chứng không"; câu hỏi nghiên cứu RQ1–RQ5; mục tiêu; phạm vi và giới hạn; đóng góp; cấu trúc luận văn | 2 000–2 800 |
| `02_CO_SO_LY_THUYET.md` | Tẩy xanh: định nghĩa, phân loại (TerraChoice, Delmas & Burbano, Lyon & Montgomery), án lệ; khung pháp lý VN và quốc tế; chuẩn mực đảm bảo (ISAE 3000, ISSA 5000) và công bố (IFRS S1/S2, GRI); NLP cho tuyên bố khí hậu (ClimateBERT, CLIMATE-FEVER, Environmental Claim Detection); kiểm chứng tuyên bố và lớp "không đủ bằng chứng"; truy xuất lai và RAG; số học trong văn bản tài chính; LLM làm thẩm định viên và thiên lệch; dự đoán có từ chối và hiệu chỉnh; người–máy trong kiểm toán; vị trí của lượng tử (trung thực) | 4 000–5 000 |
| `03_BAI_TOAN_VA_THIET_KE.md` | Phát biểu bài toán hình thức (đầu vào, đầu ra, 5 mức kết luận, rủi ro 9 thành phần); yêu cầu (đúng trên phần dám kết luận, biết nhường người, truy vết, riêng tư, chạy trên laptop); nguyên lý và 10 bất biến; kiến trúc 10 bước; bộ kiểm chứng (số học → cụm từ → mô hình); chấm rủi ro và hàng đợi; lớp pháp lý (policy-as-code); **bộ nhớ chuẩn và lớp quy tắc nội bộ của người dùng (org pack)**: các tầng nhớ, thứ bậc, luật an toàn, chống tiêm lệnh; GreenScan Studio (4 loại gợi ý sửa, không bịa số); chế độ offline và dữ liệu rời máy; kiểm thử | 4 000–5 000 |
| `04_DU_LIEU_VA_PHUONG_PHAP_DANH_GIA.md` | Kho VN30; nhãn T1; GS-Bench v1.x (ca dựng có đáp án theo cấu trúc); **GS-Eval v2** (5 bộ: explain, edit, score, rules, UX), cách lấy mẫu phân tầng "lệch nhẹ nhưng cân bằng", hướng dẫn gán nhãn, hai lượt mù + phân xử, kiểm định đối nghịch, bộ kiểm tất định; chỉ số (precision trên phần dám kết luận, độ phủ, số kết luận sai nguy hiểm, κ, QWK, Spearman, Wilson, bootstrap theo công ty); đăng ký trước | 3 000–4 000 |
| `05_KET_QUA.md` | T1; thang mô hình; AG-0 → AG-3; bộ đọc ngoại tuyến; GS-Eval v2: giải thích, chấm rủi ro, gợi ý sửa, quy tắc nội bộ, UX lint; độ đồng thuận giữa hai lượt nhãn | 4 000–5 000 |
| `06_THAO_LUAN_HAN_CHE_HUONG_PHAT_TRIEN.md` | Diễn giải; các lỗi đã đo và nguyên nhân gốc; đe doạ tính hợp lệ (nhãn Claude, mẫu, phiên bản mã, đơn vị phân tích); hạn chế; hướng phát triển có thứ tự ưu tiên | 2 500–3 500 |
| `07_KET_LUAN.md` + `00_TOM_TAT.md` + `99_TAI_LIEU_THAM_KHAO.md` | | |

## Quy ước (bắt buộc)
1. Văn xuôi tiếng Việt học thuật, rõ, không sáo rỗng; thuật ngữ chuẩn giữ nguyên (Scope 1, tCO2e, ISSA 5000). Bảng khi so sánh; hình mô tả bằng chữ (`**Hình X.Y.** …` + mô tả) khi chưa có ảnh; dẫn ảnh có sẵn trong `docs/07-presentation/paper/figures/` nếu phù hợp (đường dẫn tương đối từ thư mục luận văn: `../../07-presentation/paper/figures/...`).
2. Mỗi khẳng định thực nghiệm phải có số, n, tập dữ liệu, ngày và nguồn (đường dẫn file trong repo). Không bao giờ viết "độ chính xác X %" chung chung; nói "precision trên phần dám kết luận", "trên ca dựng", "trên nhãn Claude đã được tác giả đọc lại".
3. Nhãn do Claude gán là **dữ liệu của luận văn**: mô tả một lần quy trình (hướng dẫn, hai lượt mù, phân xử, kiểm định mẫu, tác giả đọc lại), sau đó dùng như dữ liệu bình thường; không gọi là "nhãn bạc" ở mọi câu.
4. Trích dẫn kiểu (Tác giả, năm) trong bài, danh mục cuối chương ghi đủ: tác giả, năm, tên, nơi công bố, URL nếu có. Chỉ dẫn tài liệu có trong ghi chú `docs/10-chung-ket-2026-11/doc-tai-lieu/R*.md` hoặc trong repo; tài liệu chưa kiểm được thì bỏ.
5. Không nói vượt bằng chứng: không "lượng tử giúp tăng…", không "đã chứng minh", không "phát hiện vi phạm". GreenScan chưa có dòng mã lượng tử nào.
6. Mỗi chương mở bằng 2–3 câu nêu chương trả lời câu hỏi gì, đóng bằng tóm tắt 3–5 ý.
