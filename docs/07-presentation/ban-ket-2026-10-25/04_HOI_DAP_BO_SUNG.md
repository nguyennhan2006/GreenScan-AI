# Hỏi đáp bổ sung cho Bán kết — theo 6 tiêu chí vòng 2

**Ngày:** 09/10/2026 · **Dùng cùng:** [../QA_DRILL.md](../QA_DRILL.md) (24 câu) · [../QA_BANK_100_2026-09-20.md](../QA_BANK_100_2026-09-20.md) (100 câu)
**Khung trả lời** (giữ như QA_DRILL): *lỗi đã gặp / rủi ro → lựa chọn thiết kế → cách đo*. Mỗi câu ≤ 60 giây. Không có số trong [01 §4](01_NOI_DUNG_TRINH_BAY.md#4-số-liệu-được-phép-đưa-lên-slide) thì không nói số.

---

## 1. Sáu câu trả lời trong QA_DRILL đã lỗi thời — học bản này

| # QA_DRILL | Bản cũ nói | Sự thật 09/10 | Trả lời đúng |
| --- | --- | --- | --- |
| 3 | "Hybrid BM25 + semantic… reranker (30→5) giảm distractor" | Mặc định là **BM25 + n-gram ký tự, hợp nhất RRF**; dense (FPT Vietnamese_Embedding) và reranker có adapter nhưng **chưa bật** | "Mặc định là hai bộ truy xuất từ vựng: theo từ và theo cụm ký tự — chịu được lỗi chính tả, lỗi OCR. Bộ truy xuất ngữ nghĩa đã tích hợp, chỉ bật khi bộ gán nhãn cho thấy tăng độ phủ top-5 **ít nhất 10 điểm** mà không chậm quá **2 lần** — ngưỡng này ghi ra ngày 29/09, trước khi có nhãn." |
| 7 | "LLM giúp hiểu claim (normalization 5 thuộc tính)" | **Không có** bước chuẩn hoá bằng mô hình; 5 thuộc tính trích bằng luật | "Không. Năm thuộc tính trích bằng luật. Mô hình ngôn ngữ chỉ đọc những cặp tuyên bố–bằng chứng mà luật không quyết được, và không được tự đưa ra 'khớp' hay 'bị bác bỏ'. Số học luôn do mã." |
| 11 | "5 gold có đủ chưa?" | 88 cặp đã lấy mẫu; **số đã gán: điền 17/10** | "Chưa đủ để báo độ chính xác — chúng em đặt sàn 60 cặp và đồng thuận κ ≥ 0,7 mới được nói số. Hiện có [n] cặp đã gán." |
| 16 | "NĐ 83/2026 sửa NĐ 06/2022… registry giữ cả chuỗi" | NĐ 83/2026 (hiệu lực 23/03/2026) **chỉ sửa phần chất được kiểm soát (ô-dôn)**. Hệ thống từng trích nó cho mọi tuyên bố phát thải — đã sửa 06/10 | "Chuỗi văn bản chỉ kéo văn bản sửa đổi **đúng vấn đề** đang xét. NĐ 83 sửa phần ô-dôn nên không áp cho tuyên bố khí nhà kính — chúng em tự phát hiện lỗi trích sai này và sửa." *(Thảo xác nhận trước 17/10)* |
| 22 | "Local-first… cloud chỉ là optional fallback" | Ba chế độ; **mặc định ngoại tuyến**; đám mây chỉ cho tài liệu công khai | Dùng lời S12 file 01 + phân loại tài liệu A/B/C |
| 24 | "rerank 30 xuống 5" | Lấy 30 ứng viên, giữ 5 theo RRF (bộ rerank chưa bật) | "Lấy 30 ứng viên, giữ 5 — thêm đoạn nhiễu làm kết quả tệ đi. Bộ sắp xếp lại có sẵn, chưa bật." |

Sửa luôn trong QA_DRILL.md khi tập lần đầu (Quỳnh).

---

## 2. Câu hỏi mới theo tiêu chí chấm

### Tiêu chí 1 · Làm rõ bài toán (20%)

**"Vì sao người dùng là kiểm toán viên mà không phải nhà đầu tư?"**
→ "Vì người phải đọc từng trang và chịu trách nhiệm về kết luận là kiểm toán viên, chuyên viên đảm bảo, cán bộ thẩm định. Nhà đầu tư cần kết quả của họ. NĐ 119/2025 bắt thép, xi măng, nhiệt điện phải có **thẩm định độc lập** — tức là nhu cầu người làm việc này tăng, trong khi hôm nay chỉ 2/22 báo cáo bền vững có bên thứ ba đảm bảo."

**"Khác gì các bộ chấm điểm ESG như MSCI, Refinitiv?"**
→ "Họ chấm **doanh nghiệp** bằng một điểm tổng. Chúng em kiểm **từng tuyên bố**, chỉ ra trang, phép tính, thứ còn thiếu — và không xếp hạng doanh nghiệp. Hai thứ bổ sung nhau: một điểm ESG không nói được câu nào trong báo cáo cần soát."

**"Hệ thống có kết luận Hòa Phát tẩy xanh không?"** *(câu bẫy)*
→ "Không. Hòa Phát là ca kiểm tra vì có báo cáo dày và bảng khí nhà kính đầy đủ. Kết quả: không có mâu thuẫn nào, phép cộng bảng khớp, và phần lớn tuyên bố 'khớp một phần' — phản ánh cách công bố phổ biến, không phải nghi vấn."

**"153/156 'khớp một phần' — vậy hệ thống giúp được gì?"**
→ "Đúng là kết luận giống nhau thì không giúp ai. Vì vậy sản phẩm là **thứ tự**: 9 mục nên soát trước, kèm lý do, và nói rõ 163 mục không soát trong lượt này. Giá trị nằm ở chỗ kiểm toán viên bắt đầu từ đâu."

### Tiêu chí 2 · Dữ liệu (15%)

**"Dữ liệu có bản quyền không?" (thể lệ Điều 6.8)**
→ "Báo cáo thường niên và báo cáo bền vững là tài liệu doanh nghiệp **bắt buộc công bố** theo TT 96. Chúng em không phát tán lại bản PDF: repo chỉ lưu siêu dữ liệu, đường dẫn gốc, ngày truy cập và mã băm. Hồ sơ án lệ quốc tế cũng vậy — chỉ phần tóm tắt nhóm tự viết."

**"Gán nhãn thế nào, ai gán, sao tin được?"**
→ "Có quy ước gán nhãn thành văn bản. Lô đầu 20 cặp do hai người gán độc lập để đo đồng thuận κ, bất đồng thì họp hoà giải. Chia tập theo doanh nghiệp để không rò rỉ. Không dùng mô hình tự chấm làm nhãn. Ngưỡng đánh giá ghi ra **trước** khi có nhãn — ví dụ mô hình chỉ được tự kết luận 'bị bác bỏ' nếu độ chính xác ≥ 0,9 với ít nhất 10 trường hợp."

**"Dữ liệu có đại diện, có tránh overfitting không?"**
→ "Chưa đủ đại diện và chúng em nói thẳng: kho ban đầu lệch về ngân hàng, bán lẻ trong VN30 — chỉ khoảng một phần tư đoạn văn có thuật ngữ môi trường. Từ 17/09 chúng em đổi hướng sang doanh nghiệp phát thải cao. Về overfitting: hệ thống không huấn luyện mô hình, nhưng luật có thể 'khớp' quá mức với Hòa Phát — vì vậy bộ gán nhãn lấy từ **doanh nghiệp khác** và đánh giá giữ riêng theo doanh nghiệp."

**"Đặc trưng (feature engineering) là gì?"**
→ "Mỗi con số được biểu diễn bằng giá trị, đơn vị, độ chính xác công bố và sáu chiều ngữ cảnh — loại giá trị, ranh giới, công nghệ, chỉ số con, phạm vi phát thải, mục tiêu hay thực hiện. Mỗi tuyên bố có năm thuộc tính. Đó là đặc trưng; quyết định 'được so hay không' dựa trên chúng."

### Tiêu chí 3 · Giải pháp, thuật toán (20%)

**"Sao không dùng LLM đọc cả báo cáo và kết luận luôn?"**
→ "Chúng em đã thử có đối chứng, hai lần. Trên báo cáo Hòa Phát thật, cho mô hình tự quyết thì ra 10 'mâu thuẫn', phần lớn sai — một dòng bảng vỡ bị đọc thành '100% nam giới'. Trên 51 ca có đáp án biết trước, mô hình đọc từng cặp rất tốt, nhưng khi bằng chứng là bảng bị mất cấu trúc thì mọi cỡ mô hình, kể cả GLM-5.2, đều tự tin xác nhận sai. Đưa cả báo cáo vào thì còn tệ hơn: nghiên cứu cho thấy độ chính xác giảm mạnh khi thông tin nằm giữa ngữ cảnh dài. Nên mô hình đọc từng cặp ngắn, mã kiểm số, người chốt."

**"Mô hình của các em quá bé để xử lý bài toán phức tạp này?"** *(đã có giảng viên hỏi — 10/10)*
→ Dùng lời đáp 90 giây ở [`MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md`](../../04-data-ai/MO_HINH_CO_QUA_BE_KHONG_2026-10-10.md) §6. Ba ý: GLM-5.2 khoảng 750 tỷ tham số; thực nghiệm không thấy mô hình lớn hơn làm tốt hơn, lỗi nằm ở bảng mất cấu trúc; chỗ yếu thật là bộ luật phủ hẹp (20/32) và nhóm sửa bằng cách cho mô hình đọc, mã kiểm, người chốt.

**"Đã so GreenScan với một LLM chưa?"**
→ "Rồi, trên 51 ca có đáp án biết trước: mô hình đúng nhiều hơn bộ luật của chúng em (29–32/32 so với 20/32), vì luật phủ hẹp; nhưng luật gần như không bao giờ xác nhận sai, còn mô hình xác nhận sai trên bảng mất cấu trúc. Vì vậy chúng em kết hợp hai bên và đo trên bộ gán nhãn, không chọn một bên." — *nói con số kèm 'n = 51, ca do nhóm dựng'*.

**"Đã so sánh với phương pháp khác chưa?"**
→ "Ba phép so có số: (1) trước và sau cổng khả năng so sánh trên cùng tài liệu — 357/419 mâu thuẫn sai còn 0; (2) mô hình có chốt chặn và không có chốt chặn — 10 mâu thuẫn sai so với 0; (3) truy xuất từ vựng so với ngữ nghĩa — đã chuẩn bị, chờ nhãn, ngưỡng ghi trước."

**"Các tham số chính là gì, kiểm tra thế nào?"**
→ "Dung sai so số theo độ chính xác công bố, trần 10%; ngưỡng 'bị bác bỏ' 0,35 — đặt tên trong cấu hình, sẽ quét trên nhãn; lấy 30 ứng viên giữ 5; hàng đợi ngưỡng 55 điểm, tối đa 25 mục. Mỗi tham số nằm trong tệp cấu hình có phiên bản, và mỗi phiên phân tích ghi lại phiên bản đã dùng."

**"0 mâu thuẫn — có phải hệ thống không bắt được gì?"** → câu trả lời ở [01 S8](01_NOI_DUNG_TRINH_BAY.md#s8--cổng-khả-năng-so-sánh--045--nhân).

### Tiêu chí 4 · Prototype (20%)

**"Cho chạy thử một tài liệu khác ngay bây giờ được không?"**
→ Làm theo [03 §3](03_KICH_BAN_PROTOTYPE_DEMO.md#3-kịch-bản-demo-trực-tiếp--240) dòng cuối: *Tải tài liệu → Điền ví dụ → chạy*. Không chạy lại 264 trang trước hội đồng.

**"Có tuyên bố nào hệ thống kết luận sai không?"**
→ "Có, và chúng em biết. Trên Hòa Phát, một trong hai tuyên bố 'được ủng hộ' là chữ dính cột trong trang tóm tắt: con số 90% thuộc câu bên cạnh. Lỗi kiểu này là lý do chúng em xây bộ gán nhãn, và là lý do kết luận cuối luôn qua người soát."

**"Mã nguồn có chạy lại được không?"**
→ "Có hướng dẫn và một tệp khởi động; 359 kiểm thử tự động. Bản đóng gói Docker đã viết nhưng **chưa build thử trên máy sạch**" — *(cập nhật câu này nếu đã thử trước 25/10)*.

### Tiêu chí 5 · Triển khai (15%)

**"Chi phí vận hành bao nhiêu?"**
→ "Chế độ mặc định: 0 đồng ngoài máy tính. Chế độ đám mây: ước tính dưới 2 đô-la một bộ hồ sơ, và chạy lại cùng tài liệu không tốn lời gọi nào nhờ bộ nhớ đệm. Từ 06/10 hệ thống ghi số token thật mỗi lần chạy để thay số ước tính."

**"Bảo mật dữ liệu?"**
→ "Mặc định không gửi gì ra ngoài. Chia tài liệu ba loại: công khai được dùng đám mây; nội bộ chưa công bố chỉ ngoại tuyến hoặc máy chủ của đơn vị; giấy làm việc kiểm toán chỉ ngoại tuyến — Luật Kiểm toán độc lập cấm tiết lộ hồ sơ kiểm toán khi chưa có chấp thuận. Nhà cung cấp đám mây có thể xử lý ở Nhật khi quá tải, nên chỉ dùng cho tài liệu công khai."

**"Nói ngoại tuyến — làm sao chứng minh?"**
→ "Ba cách, từ mạnh đến yếu. Một: chúng em chạy cả 264 trang trong khi chặn mọi kết nối ra ngoài máy — 0 lần hệ thống cố kết nối; và để chắc bộ chặn hoạt động, bật mô hình đám mây thì nó bắt được 15 lần gọi ra máy chủ FPT. Hai: mỗi phiên tự ghi đã gọi mô hình hay chưa — phiên demo có phiên bản prompt rỗng và không có sự kiện gọi mô hình nào. Ba: tắt Wi-Fi ngay trước hội đồng và chạy."

**"Ngoại tuyến thì AI ở đâu? Có cần mô hình nhỏ chạy tại máy không?"**
→ "Chế độ ngoại tuyến **không chạy mô hình ngôn ngữ lớn**: phần AI là xử lý ngôn ngữ tiếng Việt và truy xuất thông tin chạy trên CPU. Thứ mất đi đã đo được: so với có mô hình, 3/156 kết luận khác và 13 gợi ý cho người soát; số mâu thuẫn bằng nhau. Mô hình 8B tại máy đo được 98 giây một lời gọi — 700 cặp mất khoảng 19 giờ — nên hướng đúng là một bộ phân loại nhỏ dưới 1B cho đúng một việc, chỉ thử sau khi có nhãn để kiểm."

**"Mở rộng được không?"**
→ "Mỗi bộ hồ sơ chạy độc lập, khoảng hai phút trên laptop; xử lý lô là chạy song song nhiều bộ. Giới hạn thật không phải tốc độ mà là quy tắc pháp lý theo ngành — phần đó cần chuyên gia luật viết, và chúng em đã có hạ tầng cho nó."

**"Đã có đối tác chưa?"**
→ Chỉ nói điều có thật tính tới 25/10. Chưa có thì: "Chưa có đối tác xác nhận. Chúng em đã mời [ai] dùng thử sau bán kết; mục tiêu là một buổi thử với kiểm toán viên thật để đo thời gian."

**"Thương mại hoá có vướng giấy phép không?"**
→ "Có hai điểm chúng em đã ghi lại: mô hình Vietnamese_Embedding có hai giấy phép khác nhau ở hai nơi công bố, và vài bộ dữ liệu tham khảo là phi thương mại — nên chúng chưa nằm trong cấu hình mặc định. Mã nguồn của nhóm dùng giấy phép Apache-2.0."

### Tiêu chí 6 · Trình bày, tài liệu (10%)

**"Nhóm dùng AI ở đâu trong quá trình làm?"** (thể lệ Điều 14 — trả lời đúng như slide P1)
→ "Chúng em khai báo đầy đủ ở slide phụ lục và trong báo cáo: công cụ AI hỗ trợ viết mã và tài liệu, công cụ sinh ảnh cho hình minh hoạ — có nhật ký từng ảnh. Thiết kế bài toán, quyết định kiến trúc, dữ liệu, gán nhãn và mọi con số đo được là của nhóm; mọi đoạn mã đều được nhóm đọc, kiểm thử và giải thích được."

### Đạo đức và trách nhiệm (thường được hỏi dù là tiêu chí vòng 3)

**"Nếu hệ thống kết luận sai làm hại uy tín một doanh nghiệp thì sao?"**
→ "Ba lớp chặn: hệ thống không có từ 'vi phạm' và không xếp hạng doanh nghiệp; 'bị bác bỏ' chỉ khi có mâu thuẫn số cùng điều kiện hoặc nguồn có thẩm quyền; mọi kết luận qua người soát và được ghi lại kèm tên người chốt."

**"Có thiên vị ngành nào không?"**
→ "Có rủi ro, và hạ tầng đã tính tới: mỗi quy tắc pháp lý có thể khai ngành và đối tượng áp dụng; lệch ngành thì quy tắc không áp. Ví dụ rõ nhất: ngân hàng được miễn công bố khí nhà kính theo TT 96, nên quy tắc mục 6 đang viết sẽ miễn đúng 6.1–6.3 cho bốn ngành tài chính. Hôm nay quy tắc đó **chưa có**, nên hệ thống chưa gắn cờ 'thiếu công bố' cho bất kỳ ai."
