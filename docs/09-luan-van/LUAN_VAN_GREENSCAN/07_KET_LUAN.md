# Chương 7. Kết luận

Luận văn xây dựng và đánh giá GreenScan AI, một hệ thống kiểm chứng **từng tuyên bố môi trường** trong công bố của doanh nghiệp Việt Nam. Hệ thống không chấm "doanh nghiệp có tẩy xanh không". Nguyên lý của nó là: mô hình đọc, quy tắc quyết định, con người duyệt. Chương này trả lời năm câu hỏi nghiên cứu nêu ở Chương 1.

**RQ1. Kiểm chứng từng tuyên bố và biết lúc nào dừng.**
- Kiến trúc mười bước với mười bất biến cho phép mỗi kết luận truy về trang, đoạn và quy tắc đã dùng. Kết luận chỉ có một trong năm mức, và "không đủ bằng chứng" là kết quả hợp lệ.
- Hệ thống dừng phán đoán đúng chỗ ở phần lớn trường hợp. Khi dừng, lời giải thích trung thực: 0,95 với PARTIALLY_SUPPORTED, 0,60 với INSUFFICIENT_EVIDENCE.
- Trên báo cáo thật, kết luận dứt khoát ban đầu chưa tin được: CONTRADICTED đúng 3/38, SUPPORTED 0/5. Hai nguyên nhân đã định vị được: luật từ phủ định, và cổng so sánh không kiểm cùng đối tượng. Chốt chặn mâu thuẫn (05/11) đưa CONTRADICTED về 3/4 và 0 vu oan trên tuyên bố thật, không đổi kết quả trên GS-Bench; SUPPORTED vẫn 0/5.
- Vì vậy mọi kết luận dứt khoát hiện phải qua người soát.

**RQ2. Số liệu kiểm tất định, mô hình không bịa số.**
- Phép so sánh số học do mã thực hiện.
- Trên ca dựng (GS-Bench), luật không kết luận sai lần nào. Bộ đọc IR kèm `irlib.ground()` loại các lỗi do mô hình tự thêm bội số (11/11 kết luận sai của 32B).
- Gợi ý sửa không thêm số nào: 0/527.
- Trên câu thật, so sánh số còn sai khi hai số thuộc hai đối tượng khác nhau. Đây là việc của tầng chuẩn hoá (IR có `segment`), không phải của phép tính.

**RQ3. Mô hình nhỏ chạy cục bộ.**
- Trên GS-Bench ngoài mẫu sạch (87 ca), bộ đọc 4B–32B nâng độ phủ từ 0,011 (luật) lên 0,115–0,253 mà vẫn có precision 1,0.
- Bộ đọc 4B lượng tử hoá Q4 qua Ollama khớp 0,963 với bản bf16. Chính sách hai đường cho 0 kết luận sai trên 162 ca.
- Mô hình nhỏ đủ để đọc câu thành cấu trúc. Chúng chưa được đưa vào sản phẩm vì chưa đo được thời gian trên laptop.

**RQ4. Người dùng thêm quy tắc nội bộ mà không làm yếu bảo đảm.**
- Org pack (YAML có cấu trúc + tài liệu nội bộ chỉ để dẫn chiếu, sau cờ, mặc định tắt) cho kết quả đúng 0,945 trên 237 ca cân bằng của 12 tổ chức giả lập, và 0,907 đầu–cuối.
- Đúng 45/45 ca an toàn (58/58 kể cả ca khác ngành). Không đổi kết luận kiểm chứng (test bất biến).
- Giới hạn còn lại nằm ở độ linh hoạt khi diễn đạt quy tắc.

**RQ5. Đo khách quan khi thiếu nhãn người.**
- Ba lớp đo bổ sung cho nhau: bộ có đáp án theo cấu trúc (GS-Bench); bộ câu thật gán nhãn theo hướng dẫn, hai lượt mù và phân xử (GS-Eval v2: giải thích, gợi ý sửa, chấm rủi ro, quy tắc nội bộ); kiểm tất định (số không có nguồn, UX lint).
- Cách đo này tìm ra lỗi mà bộ đo cũ che: điểm rủi ro chỉ tương quan 0,23 (0,39 sau chốt chặn) với đồng thuận của hai lượt chấm, trong khi trần đồng thuận là 0,73.
- Nó không thay được nhãn người và thử nghiệm với người dùng thật, hai việc còn thiếu.

**Đóng góp.**
1. Một kiến trúc kiểm chứng tuyên bố môi trường cho tiếng Việt, ưu tiên bằng chứng và truy vết, chạy ngoại tuyến trên laptop.
2. Lớp quy tắc nội bộ có thứ bậc, kiểm khi nạp và miễn nhiễm tiêm lệnh, cho phép tổ chức đưa chính sách của mình vào mà không đụng tới kết luận.
3. Bộ đánh giá GS-Eval v2 với năm bộ dữ liệu, hướng dẫn gán nhãn và bộ chấm tất định, tái lập được bằng một lệnh.
4. Một kết quả thực nghiệm trung thực: an toàn trên ca dựng không suy ra an toàn trên câu thật, và nguyên nhân cụ thể của khoảng cách đó.

**Hàm ý thực tiễn.** Ở trạng thái hiện tại, GreenScan phù hợp nhất với vai **trợ lý chuẩn bị hồ sơ soát**:
- trích tuyên bố;
- tìm bằng chứng có trang;
- chỉ ra thuộc tính còn thiếu;
- gợi ý sửa không bịa số;
- áp chính sách nội bộ của tổ chức;
- xếp hàng đợi.

Kết luận cuối cùng về một tuyên bố vẫn thuộc về kiểm toán viên. Thiết kế cũng nhằm đúng điều đó: máy làm phần lặp lại và truy vết được, người giữ phán đoán và trách nhiệm.
