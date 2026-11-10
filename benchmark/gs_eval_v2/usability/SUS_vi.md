# SUS tiếng Việt cho GreenScan (System Usability Scale)

*Soạn 04/11/2026 · labeler `claude-opus-5-5` · guide_version `gs-eval-v2.0` · review_status `pending_human_review` (Nhân đọc lại, đổi thành `human_reviewed` hoặc `human_corrected`).*

SUS là thang 10 câu đo **cảm nhận tổng thể về độ dễ dùng**, cho điểm 0–100 (Brooke 1996) [KIẾN THỨC NỀN — chưa đối chiếu bản gốc trong repo]. SUS không chỉ ra vấn đề nằm ở đâu; dùng cùng tỷ lệ hoàn thành, thời gian, lỗi trong `PROTOCOL.md` và danh sách vấn đề theo `heuristics.yaml`.

## 1. Khi nào phát phiếu

- Phát **một lần**, ngay sau khối nhiệm vụ trên sản phẩm thật (T02–T12, T15, T16 trong `tasks.yaml`), **trước** khối kiểm khái niệm org pack (T13, T14). Bản mẫu chưa phải sản phẩm, không được gộp vào SUS. T01 (tạo phiên mới) nếu làm thì làm sau SUS, theo `PROTOCOL.md` §4.
- Người tham gia tự điền, không thảo luận. Người điều phối không giải thích câu hỏi, chỉ nhắc lời dẫn.
- **Không** lấy SUS từ agent đóng vai persona (`persona_walkthrough.md`). SUS chỉ có nghĩa khi do người thật trả lời.

## 2. Lời dẫn (đọc nguyên văn)

> Dưới đây là 10 câu về GreenScan mà anh/chị vừa dùng. Với mỗi câu, hãy khoanh một số từ 1 (Hoàn toàn không đồng ý) đến 5 (Hoàn toàn đồng ý) theo cảm nhận đầu tiên, đừng nghĩ lâu. Nếu thấy không trả lời được một câu, hãy khoanh số 3.

## 3. Mười câu hỏi

Thang cho mọi câu: **1** Hoàn toàn không đồng ý · **2** Không đồng ý · **3** Trung lập · **4** Đồng ý · **5** Hoàn toàn đồng ý.

| # | Câu tiếng Việt (bản dịch của đội) | Câu gốc (Brooke 1996) | Chiều |
|---|---|---|---|
| 1 | Tôi nghĩ tôi sẽ muốn dùng GreenScan thường xuyên. | I think that I would like to use this system frequently. | + |
| 2 | Tôi thấy GreenScan phức tạp một cách không cần thiết. | I found the system unnecessarily complex. | − |
| 3 | Tôi thấy GreenScan dễ dùng. | I thought the system was easy to use. | + |
| 4 | Tôi nghĩ tôi sẽ cần người hỗ trợ kỹ thuật mới dùng được GreenScan. | I think that I would need the support of a technical person to be able to use this system. | − |
| 5 | Tôi thấy các chức năng của GreenScan gắn kết với nhau tốt. | I found the various functions in this system were well integrated. | + |
| 6 | Tôi thấy GreenScan có quá nhiều chỗ không nhất quán. | I thought there was too much inconsistency in this system. | − |
| 7 | Tôi nghĩ phần lớn mọi người sẽ học cách dùng GreenScan rất nhanh. | I would imagine that most people would learn to use this system very quickly. | + |
| 8 | Tôi thấy GreenScan rất rườm rà, khó thao tác. | I found the system very cumbersome to use. | − |
| 9 | Tôi cảm thấy rất tự tin khi dùng GreenScan. | I felt very confident using the system. | + |
| 10 | Tôi phải học nhiều thứ trước khi có thể bắt đầu dùng GreenScan. | I needed to learn a lot of things before I could get going with this system. | − |

Ghi chú cho câu 1: với kiểm toán viên, “thường xuyên” hiểu là “mỗi khi có việc rà soát báo cáo bền vững”. Người điều phối chỉ nói câu này khi người tham gia hỏi.

## 4. Cách tính điểm

1. Câu lẻ (1, 3, 5, 7, 9): điểm đóng góp = câu trả lời − 1.
2. Câu chẵn (2, 4, 6, 8, 10): điểm đóng góp = 5 − câu trả lời.
3. Cộng 10 điểm đóng góp (0–40), nhân **2,5** → điểm SUS 0–100.
4. Câu bỏ trống: tính là 3, theo hướng dẫn gốc của Brooke [KIẾN THỨC NỀN]. Ghi số câu bị bỏ trống vào kết quả; phiếu bỏ trống từ 3 câu trở lên thì loại khỏi phân tích.

**Ví dụ:** trả lời (4, 2, 4, 1, 4, 2, 5, 2, 4, 2).
Câu lẻ: 3 + 3 + 3 + 4 + 3 = 16. Câu chẵn: 3 + 4 + 3 + 3 + 3 = 16. Tổng 32 × 2,5 = **80,0**.

```python
def sus(r):
    """r: 10 câu trả lời 1..5 theo thứ tự câu 1..10; None = bỏ trống (tính là 3)."""
    r = [3 if x is None else x for x in r]
    assert len(r) == 10 and all(1 <= x <= 5 for x in r)
    le = sum(r[i] - 1 for i in range(0, 10, 2))
    chan = sum(5 - r[i] for i in range(1, 10, 2))
    return (le + chan) * 2.5

assert sus([4, 2, 4, 1, 4, 2, 5, 2, 4, 2]) == 80.0
```

## 5. Báo cáo và diễn giải

- Báo cáo: n, trung bình, độ lệch chuẩn, khoảng tin cậy 95 % theo t (trung bình ± t₀,₉₇₅;ₙ₋₁ × SD/√n), trung vị, min–max. Báo theo persona nếu mỗi nhóm có từ 3 người.
- Điểm SUS **không phải phần trăm**. Mốc tham chiếu thường dùng: trung bình các nghiên cứu khoảng 68 (Sauro 2011); thang tính từ của Bangor, Kortum & Miller (2009) xếp quanh 71 là “tốt”, quanh 85 là “rất tốt” [CHƯA XÁC MINH các con số mốc — đối chiếu bản gốc trước khi trích trong luận văn].
- Hai câu 4 và 10 thường được xem là thành phần “dễ học” (Lewis & Sauro 2009) [KIẾN THỨC NỀN]. Có thể báo riêng, nhưng với n nhỏ thì chỉ để tham khảo.
- Với n = 5 và độ lệch chuẩn giả định 12–16 điểm, khoảng tin cậy 95 % vào khoảng ± 15–20 điểm (tính: 2,776 × SD/√5 ≈ 1,24 × SD). Chỉ nói “sơ bộ, n nhỏ”; không so sánh hai phiên bản bằng SUS khi n < 8 mỗi bên.
- Ngưỡng đặt trước cho GreenScan (đề xuất, Nhân duyệt): trung bình ≥ 68 là đạt mục tiêu vòng A; không có người nào dưới 50 mà không có giải thích trong phỏng vấn cuối buổi.

## 6. Ghi chú về bản dịch

- Thay “hệ thống” bằng “GreenScan” để người tham gia không lẫn với hệ thống kế toán của họ. Giữ nguyên chiều tích cực / tiêu cực xen kẽ của bản gốc.
- Bản dịch này **chưa được kiểm định tâm trắc** cho tiếng Việt [CHƯA XÁC MINH có bản SUS tiếng Việt chuẩn hoá đã công bố]. Khi báo cáo, ghi “bản dịch của đội, chưa chuẩn hoá”.
- Trước vòng A: cho 2 người (không thuộc đội, không tham gia thử) đọc to từng câu và nói lại ý bằng lời của mình. Câu nào bị hiểu lệch thì sửa chữ, ghi lại thay đổi ở cuối tệp này.

## 7. Mẫu ghi kết quả

Một dòng cho mỗi người tham gia (ghi vào tệp kết quả của vòng thử, xem `PROTOCOL.md` §8):

```json
{"participant_id": "P01", "persona": "KTV", "sus_items": [4, 2, 4, 1, 4, 2, 5, 2, 4, 2], "missing_items": 0, "sus": 80.0, "date": "2026-11-0x", "app_build": "ghi ngày build hoặc mã phiên", "review_status": "pending_human_review"}
```

## 8. Thay đổi bản dịch

| Ngày | Câu | Đổi gì | Vì sao |
|---|---|---|---|
| 04/11/2026 | — | Bản đầu | — |
