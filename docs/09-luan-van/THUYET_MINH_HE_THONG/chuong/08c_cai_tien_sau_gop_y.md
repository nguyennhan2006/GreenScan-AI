# Chương 11. Cải tiến sau góp ý chuyên gia (14–15/11/2026)

Chương này ghi lại đợt cải tiến cuối trước hạn nộp vòng 2. Đội gửi bản liệt kê thiếu sót cho chuyên gia, nhận lại góp ý, rồi đo lại hệ thống bằng các bộ đo mới. Mọi số đều [ĐÃ THỰC NGHIỆM] trên mã cuối ngày 15/11/2026. Chi tiết nằm trong `docs/03-architecture/ABSOLUTE_AND_INTERNAL.md` và `docs/03-architecture/CAI_TIEN_SAU_GOP_Y_2026-11-15.md` (quyết định D-2026-11-14-05, D-2026-11-15-01, D-2026-11-15-02).

## 11.1. Các luật mới

| Mã chính sách | Nội dung | Vì sao |
|---|---|---|
| `absolute-share-v1` | Tuyên bố "hoàn toàn / toàn bộ / 100%" về vốn của một công cụ tài chính xanh được đối chiếu với tỷ trọng đã dùng / tổng tính từ một đoạn. Hệ thống đọc được cả bảng chỉ ghi đơn vị ở tiêu đề cột; khi bảng không ghi tổng thì tổng = đã phân bổ + chưa phân bổ | Ca A2 ("sử dụng hoàn toàn" trong khi 180/500 tỷ chưa phân bổ) trước đây bị bỏ lọt |
| `figure-consistency-v1` | Số khớp mà ngược hướng tăng/giảm là mâu thuẫn. Câu hai số mà một số lệch xa thì không được "ủng hộ". Cùng mức thay đổi nhưng khác năm gốc là PARTIAL. "100%" là số chính xác. Đoạn khớp số và đoạn lệch số cùng xuất hiện thì là "bằng chứng không thống nhất". Không kết luận mâu thuẫn khi chưa rõ chỉ số, hoặc chỉ dựa trên một khoản tiền | Mỗi điều đều xuất phát từ một lỗi mà bộ cài lỗi hoặc tập giữ riêng làm lộ ra |
| `claim-typing-v2` (taxonomy v4) | Khi câu không khớp loại tuyên bố nào, thử thêm các loại dự phòng: dùng tài nguyên (nước, điện, nhiên liệu), tuân thủ và quản lý môi trường, cây xanh và rừng, chỉ số + số liệu | 63/63 câu "ủng hộ" mà bộ trích bỏ sót đều vì không khớp loại nào |
| `claim-precision-v1` | Câu tiếng Việt thuộc loại "bền vững chung chung" phải có ít nhất một từ môi trường mới được coi là tuyên bố | 13/17 câu trích sai trên phần dev là "bền vững", "ESG" theo nghĩa xã hội hoặc quản trị |
| `units-v2` | Thêm các đơn vị m2, ha, MWp, cây. Phạm vi phát thải đọc theo từng số. Nhận "m3/tấn" là cường độ. Tách nước thải / khai thác / sử dụng. Thêm ranh giới "công ty mẹ". Số lũy kế so với số một kỳ là AMBIGUOUS | 24/26 câu đã trích mà không quyết được là do không đọc được đơn vị |
| `independent_support_v1` (bật) | Chỉ kết luận "ủng hộ" khi có nguồn pháp luật, bên ngoài hoặc chuẩn mực | Trên câu thật, "ủng hộ" sai giảm 5 → 0 |
| `assessment-v1` | Mỗi kết luận kèm hai trục (nhất quán; độc lập nguồn) và loại căn cứ (phép tính / cụm từ / chỉ tương đồng). Giao diện không hiện điểm 0–100 | Góp ý của chuyên gia: kiểm toán viên cần thứ tự và lý do, không cần một điểm số |
| `audit-sample-v1` | Mỗi phiên rút 5 tuyên bố ngoài hàng đợi cho người đọc, để ước lượng hàng đợi bỏ sót bao nhiêu (0 lỗi trên n mẫu → cận trên khoảng 3/n) | Góp ý Q4 của chuyên gia |

Đã thử nhưng để tắt: luật so lời văn với bảng trong cùng báo cáo (`internal-inconsistency-v1`). Trên câu thật, luật này chỉ cho một cờ, và cờ đó sai.

## 11.2. Bộ đo mới

| Bộ đo | Cỡ, cách làm | Nhãn |
|---|---|---|
| GS-Mutation v1 | 907 ca từ cặp thật của 8 doanh nghiệp, chia dev/test theo công ty. Mỗi ca cài đúng một lỗi: phóng đại số, đảo hướng, lùi năm gốc, xoá phạm vi, tuyệt đối hoá, chèn từ quảng bá, thay bằng chứng, đổi đơn vị, phóng to ranh giới, mục tiêu viết thành đã đạt. Ngưỡng đăng ký trước | Đáp án suy từ kiểu lỗi |
| GS-Claims v1 | 150 câu của 4 báo cáo (thép, dược, xây dựng, cảng), có 10 câu kiểm soát | Hai mô hình Sonnet gán độc lập (kappa "là tuyên bố" 0,92; câu kiểm soát đúng 29/29); mô hình Opus phân xử 29 câu lệch. **Đây là nhãn máy**. Đội đã chuẩn bị bộ 50 câu để một người gán lại (`benchmark/gs_claims_v1/human/`) |
| Tập giữ riêng v1 | PAN (tiếng Anh) và DPR (bản scan), hai ngành chưa dùng ở đâu; chạy đúng một lần | Không cần nhãn: đọc tay mọi kết luận "mâu thuẫn"; cài lỗi ngay trong văn bản báo cáo |
| Mốc LLM | gpt-oss-120b đọc thẳng cùng câu và cùng bằng chứng, 183 ca phần test, hỏi 2 lần | Như GS-Mutation |

## 11.3. Kết quả trước và sau

| | 14/11 | 15/11 |
|---|---|---|
| GS-Bench: số kết luận dứt khoát / chính xác | 35 / 0,74 | 123 / 0,85 |
| GS-Bench: "ủng hộ" sai / "mâu thuẫn" sai | 8 / 1 | 17 / 1 |
| GS-Mutation, phần test: vu oan / bắt phóng đại số / bắt đảo hướng | 0/234 / 9/72 / 5/16 | 0/234 / 50/72 / 13/16 |
| Câu thật (GS-Eval v2): chính xác / "ủng hộ" sai | 0,43 / 3 | 0,75 / 0 |
| Bộ trích tuyên bố trên GS-Claims: chính xác / độ phủ | 0,56 / 0,75 | 0,71 (0,65 trên 2 báo cáo không dùng để chỉnh) / 0,77 |
| Hòa Phát: tuyên bố / hàng đợi | 156 / 8 trên 172 mục | 179 / 10 trên 195 mục |
| Kiểm thử tự động | 743 | 759 |

**So với mốc LLM** (cùng 183 ca):

| | Luật | LLM | Kết hợp (luật quyết, LLM chỉ gắn cờ khi 2 lần hỏi cùng ý) |
|---|---|---|---|
| Bắt phóng đại số | 50/72 | 47/72 | 57/72 |
| Vu oan trên câu gốc | 0/75 | 1/75 | 0/75 |
| Đổi kết quả khi hỏi lại | 0% | 16% | 0% |

**Tập giữ riêng.** Lần chạy duy nhất cho 2 kết luận "mâu thuẫn" ở PAN, và cả hai đều sai khi đọc tay:
- tuyên bố không có chỉ số rõ, nên bị so với một câu bất kỳ;
- hai khoản tiền khác nhau bị đem so với nhau.

Bắt lỗi cài chỉ được 1/8, vì 9/11 số khớp nằm ngay trong chính báo cáo. Hai nguyên nhân vu oan đã được sửa **sau** lần chạy đó; con số ngoài mẫu vẫn được báo cáo nguyên như lần chạy duy nhất.

## 11.4. Báo cáo trái phiếu xanh thật

- **Techcombank, báo cáo sau phát hành 2024.** Hệ thống đọc bảng phân bổ (đơn vị ghi ở tiêu đề cột) và tính 399 / (399 + 51) = 89%. Với một tuyên bố giả định "toàn bộ vốn đã được phân bổ", kết luận là "ủng hộ một phần", kèm cờ và phép tính. Không ra "mâu thuẫn", vì độ lệch dưới ngưỡng 35%.
- **BIDV, báo cáo phân bổ 2025.** Tuyên bố thật "đã hoàn thành phân bổ 100%" khớp số, nhưng chỉ có tài liệu của chính ngân hàng xác nhận, nên là "ủng hộ một phần".

## 11.5. Giới hạn còn lại

1. Nhãn GS-Claims là nhãn máy. Mức trần do người đo vẫn chưa có.
2. Bộ trích tuyên bố vẫn để lọt khoảng 3/10 câu không phải tuyên bố: dòng dính chữ, câu bối cảnh ngành.
3. Nếu chỉ nhìn năm mức thì kết luận vẫn phẳng (Hòa Phát: 178/179 "ủng hộ một phần"). Hai trục giúp người đọc thấy rõ hơn: 40 câu khớp tài liệu của chính doanh nghiệp, 139 câu chưa so được.
4. Lỗi nằm trong chính một báo cáo (lời văn khác bảng) chưa được bắt, vì luật so lời văn với bảng đang tắt.

## 11.6. Bổ sung ngày 16/11/2026: công tắc mô hình và bộ lọc bảng giả

Hai thay đổi này được làm sau các bảng ở mục 11.3, nên số của Hòa Phát trong chương này (179 tuyên bố, hàng đợi 10 trên 195) là số của ngày 15/11. Số ngày 16/11: **171 tuyên bố, hàng đợi 7 trên 186 mục, 768 kiểm thử**.

- **Công tắc mô hình (`model-mode-v1`).** Trên giao diện có ba chế độ, đổi được khi máy chủ đang chạy: chỉ luật; mô hình chạy trên máy (Qwen3-4B qua Ollama, tài liệu không rời máy); mô hình trên đám mây, chỉ cho tài liệu đã công bố. Mô hình không tự ra “ủng hộ” hay “mâu thuẫn”; chỗ nó đọc khác luật thì tuyên bố được chuyển cho người xác nhận. Đo: một lượt gọi thử mất 32 giây trên máy và 1 giây trên đám mây; Ca mẫu A có mô hình trên máy mất 940 giây lần đầu và 1 giây khi chạy lại từ bộ nhớ đệm.
- **Bộ lọc bảng giả (`table-shape-v1`).** Thư viện đọc bảng coi khung trang trí của một trang infographic là bảng và ghép chữ hai cột vào nhau, tạo ra câu như “Hoàn thành kiểm kê khí nhà kính theo tiêu 90%” ở đầu hàng đợi. Bộ lọc chỉ giữ bảng có ít nhất hai dòng có hai ô có chữ. Trên Hòa Phát, 8 câu ghép sai bị bớt, không mất câu thật nào; phép cộng lại bảng khí nhà kính vẫn khớp.

Chi tiết: `docs/03-architecture/MO_HINH_BAT_TAT_VA_LOC_BANG_2026-11-16.md` (D-2026-11-16-01).

Số ngày 17/11, sau phân vùng trang (Chương 12): **186 tuyên bố, 55 số liệu đọc từ bảng, 15 phép kiểm bảng, hàng đợi 9 trên 241 mục, 784 kiểm thử**.

