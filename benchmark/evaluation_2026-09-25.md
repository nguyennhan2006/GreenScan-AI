# Đánh giá trên gold — 2026-09-25

Phiên gán nhãn: ['2026-09-17_trial01.jsonl'] · hàng: 8 · **đã trọng tài: 0**

> **Chưa có hàng nào được trọng tài.** Khung đo đã dựng xong và chạy được; không có con số nào được tính, vì không có gì để tính. Đây là trạng thái đúng, không phải lỗi.

Việc cần làm: `python tools/label_session.py sample --name <tên>` rồi gán nhãn; mỗi hàng cần `labels.labeler`, `labels.verdict` và `labels.evidence`.

## Chia tập

- Doanh nghiệp: 7 · phân bố: `{'dev': 6, 'train': 2}`
- ✅ Không doanh nghiệp nào nằm ở hai split.

## 1. Truy xuất — bằng chứng đúng có nằm trong top-k không

Chưa có hàng nào gán nhãn bằng chứng.

## 2. Kiểm chứng — cho đúng bằng chứng, verdict có đúng không

Chưa có hàng nào có verdict đã trọng tài.

## 3. Hàng đợi — bao nhiêu phần trăm thật sự là tuyên bố

Chưa có hàng nào gán nhãn `is_claim`.

---

Truy xuất hỏng → sửa truy xuất. Truy xuất đúng mà verdict sai → sửa verifier. Một chỉ số end-to-end duy nhất không phân biệt được hai việc đó (`docs/00-project/ARCHITECTURE_INVARIANTS.md`).
