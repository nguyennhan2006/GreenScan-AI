# GreenScan AI: kiểm chứng tuyên bố môi trường trong công bố của doanh nghiệp Việt Nam theo hướng bằng chứng trước

*Luận văn · Đội Eco Nexus · AI-Quantum Challenge 2026 (Học viện Tài chính) · bản 05/11/2026*

## Tóm tắt

Công bố môi trường của doanh nghiệp Việt Nam tăng nhanh nhưng mỏng về định lượng và hiếm khi được đảm bảo độc lập. Trong khi đó, chưa có văn bản pháp luật nào định nghĩa "tẩy xanh". Luận văn vì vậy không hỏi "doanh nghiệp có tẩy xanh không", mà hỏi: *mỗi tuyên bố môi trường có bằng chứng không, thiếu gì, và khi nào máy phải nhường người?*

GreenScan AI trả lời bằng một hệ thống mười bước theo nguyên lý "mô hình đọc, quy tắc quyết định, con người duyệt":
- trích tuyên bố;
- truy xuất bằng chứng có trang;
- so sánh số học bằng mã;
- kết luận theo năm mức, trong đó "không đủ bằng chứng" là kết quả hợp lệ;
- chấm rủi ro chín thành phần;
- xếp hàng đợi cho kiểm toán viên;
- gợi ý sửa câu không bịa số.

Hệ thống chạy ngoại tuyến trên laptop và được ràng buộc bởi mười bất biến có test. Luận văn bổ sung lớp **quy tắc nội bộ (org pack)**: tổ chức dùng hệ thống chỉ cần thêm quy tắc và tài liệu nội bộ của mình. Quy tắc được kiểm cấu trúc khi nạp, đứng dưới luật và không bao giờ đổi kết luận kiểm chứng.

Để đo khi chưa có nhãn người, luận văn xây dựng **GS-Eval v2**, gồm năm bộ dữ liệu lấy mẫu phân tầng cân bằng, nhãn do Claude gán theo hướng dẫn viết trước và được tác giả đọc lại, kèm bộ chấm tất định:
- 200 giải thích tham chiếu;
- 200 gợi ý sửa;
- 200 mẫu chấm rủi ro, hai lượt mù và phân xử;
- 14 bộ quy tắc nội bộ với 237 ca kiểm;
- bộ kiểm độ dễ dùng.

**Kết quả cho thấy hai mặt.**

Các bảo đảm viết thành mã đứng vững:
- 0/527 gợi ý sửa thêm số mới;
- engine quy tắc nội bộ đúng 94,5 % (Wilson 95 % [90,8; 96,8]) và đúng 45/45 ca an toàn;
- trên bộ ca dựng có đáp án (GS-Bench), luật không kết luận sai lần nào. Bộ đọc 4B–32B chạy cục bộ nâng độ phủ từ 1,1 % lên 11,5–25,3 % mà vẫn giữ precision 1,0.

Trên 146 câu thật của 8 doanh nghiệp, chất lượng phán đoán dứt khoát còn yếu:
- CONTRADICTED chỉ đúng 3/38, do hai nguyên nhân đã định vị: luật từ phủ định coi "không ghi nhận vi phạm" là bác bỏ, và so số của hai đối tượng khác nhau; sau chốt chặn mâu thuẫn (05/11) còn 3/4 đúng và không còn vu oan trên tuyên bố thật, trong khi GS-Bench và bốn ca án lệ không đổi;
- khoảng 30 % câu được trích không phải tuyên bố;
- điểm rủi ro tương quan 0,23 với đồng thuận của hai lượt chấm (0,39 sau chốt chặn; trần 0,73).

Khi hệ thống dừng phán đoán, lời giải thích trung thực (0,95 với "khớp một phần"). Luận văn kết luận rằng GreenScan hiện phù hợp vai trợ lý chuẩn bị hồ sơ soát, và chỉ ra thứ tự sửa có đăng ký trước. Thành công trên ca dựng phải luôn được báo cáo cùng kết quả trên câu thật.

**Từ khoá:** tẩy xanh, kiểm chứng tuyên bố, ESG, kiểm toán, truy xuất bằng chứng, dự đoán có từ chối, policy-as-code, tiếng Việt, đánh giá không có nhãn người.

## Abstract

Environmental disclosures by Vietnamese companies are growing but are rarely quantified or independently assured, and Vietnamese law does not define greenwashing. Instead of asking whether a company greenwashes, this thesis asks whether each environmental claim is evidenced, what is missing, and when a machine should defer to a human.

GreenScan AI is a ten-step, evidence-first system built on the principle "models read, rules decide, humans review". It extracts claims, retrieves page-anchored evidence, does arithmetic in code, and assigns one of five verdicts, with "insufficient evidence" as a legitimate outcome. It also scores nine risk components, queues claims for auditors, and suggests edits that never invent numbers. The system runs offline on a laptop under ten tested invariants.

The thesis adds an "org pack" layer: organisations supply only their own rules and internal documents. The rules are validated on load, rank below the law, and never change a verification verdict.

Human gold labels are not yet available, so the thesis builds GS-Eval v2: five stratified, balanced sets with Claude-made labels that the author reviewed, scored by deterministic graders. The sets are 200 reference explanations, 200 edit suggestions, 200 risk scores (two blind passes with adjudication), 14 org packs with 237 test cases, and a usability kit.

The guarantees written into code hold:
- 0 of 527 suggestions introduce a number;
- the org-pack engine is right on 94.5% of cases and 45 of 45 safety cases;
- on constructed GS-Bench cases, the rules make no wrong decisive verdict.

On 146 real sentences from 8 companies, decisive verdicts are not yet reliable:
- only 3 of 38 CONTRADICTED verdicts are correct, traced to a negation-cue rule and to comparing figures about different objects;
- about 30% of extracted sentences are not claims;
- risk scores correlate at ρ = 0.23 with the annotators' consensus, against an inter-pass ceiling of 0.73.

The system is currently fit to assist with preparing review files. Results on constructed cases must always be reported alongside results on real text.

**Keywords:** greenwashing, claim verification, ESG, audit, evidence retrieval, selective prediction, policy-as-code, Vietnamese, evaluation without gold labels.
