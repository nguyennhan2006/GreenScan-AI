"""GS-Issue lớp B: câu THẬT, chọn có chủ đích để các loại vấn đề hiếm có đủ ca, và không để một doanh nghiệp áp đảo.

    python -I -X utf8 benchmark/gs_issue/build_real_pool.py [--per-family 90] [--per-company 150] [--seed 20261111]

Nguồn: benchmark/gs_eval_v2/inputs/pool_a.jsonl (1 589 câu thật GreenScan trích từ báo cáo của 12 doanh nghiệp,
kèm bằng chứng). Bỏ các câu đã nằm trong D-EDIT (để D-EDIT còn là tập kiểm riêng).
Bước 1 lọc theo từ khoá cho từng họ vấn đề hiếm (offset, absolute, future, cert, intensity, mandatory, entity, vague,
change); bước 2 lấy ngẫu nhiên tối đa --per-family câu mỗi họ, rồi bù câu ngẫu nhiên; mọi bước tôn trọng trần
--per-company. Từ khoá CHỈ dùng để chọn mẫu; nhãn đến từ hai người đọc độc lập (Qwen3-14B, Qwen3-32B trên Kaggle),
rồi người duyệt (docs/04-data-ai/HUONG_DAN_TAO_THEM_CASE.md, mục 4).
Ra: data/layer_b_all.jsonl (mọi câu đủ điều kiện, cho người đọc máy) và data/layer_b_pool.jsonl
(mẫu chọn theo họ, dùng khi chưa có nhãn; khi có nhãn, select_real.py chọn lại theo nhãn).
"""
import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILIES = {
    "offset": r"trung hòa|trung hoà|net.?zero|tín chỉ|bù trừ|carbon neutral|offset",
    "absolute": r"100 ?%|hoàn toàn|tuyệt đối|duy nhất|tốt nhất|hàng đầu|đầu tiên|không phát thải|zero",
    "future": r"mục tiêu|đến năm 20|cam kết|phấn đấu|hướng tới|target|by 20\d\d",
    "cert": r"chứng nhận|chứng chỉ|giải thưởng|nhãn |iso ?1|leed|edge|lotus|award|certif",
    "intensity": r"cường độ|trên mỗi|trên một|/ ?tấn|per tonne|intensity",
    "mandatory": r"tuân thủ|theo quy định|qcvn|đánh giá tác động môi trường|đtm|giấy phép|comply|complian",
    "entity": r"công ty mẹ|hợp nhất|toàn tập đoàn|consolidated|parent compan",
    "vague": r"xanh|thân thiện|bền vững|không ngừng|sustainab|eco-?friendly|green",
    "change": r"(giảm|tăng|tiết kiệm|reduc|increas|sav)[^.]{0,40}\d",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-family", type=int, default=90)
    ap.add_argument("--per-company", type=int, default=150)
    ap.add_argument("--fill", type=int, default=150, help="câu ngẫu nhiên thêm vào, không theo từ khoá")
    ap.add_argument("--seed", type=int, default=20261111)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    pool = [json.loads(line) for line in open(ROOT / "benchmark/gs_eval_v2/inputs/pool_a.jsonl", encoding="utf-8")]
    edit_ids = {json.loads(line)["item_id"] for f in sorted((ROOT / "benchmark/gs_eval_v2/edit/batches").glob("*.jsonl"))
                for line in open(f, encoding="utf-8")}
    rows = []
    for p in pool:
        if p["item_id"] in edit_ids:
            continue
        t = p["claim"]["text"].strip()
        if not (40 <= len(t) <= 420):
            continue
        fam = [f for f, rx in FAMILIES.items() if re.search(rx, t.lower())]
        ev = " ".join(e["text"] for e in (p.get("evidence") or [])[:2])[:700]
        rows.append({"id": "B-" + p["item_id"], "company": p["company"], "claim": t, "evidence": ev, "families": fam})
    with open(HERE / "data" / "layer_b_all.jsonl", "w", encoding="utf-8") as fh:  # everything eligible: the readers read all
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    rng.shuffle(rows)
    take, per_co = {}, Counter()
    for fam in sorted(FAMILIES, key=lambda f: sum(f in r["families"] for r in rows)):  # rarest family first
        n = 0
        for r in rows:
            if n >= a.per_family:
                break
            if fam in r["families"] and per_co[r["company"]] < a.per_company:
                if r["id"] not in take:
                    take[r["id"]] = r
                    per_co[r["company"]] += 1
                n += 1
    n = 0
    for r in rows:
        if n >= a.fill:
            break
        if r["id"] not in take and per_co[r["company"]] < a.per_company:
            take[r["id"]] = r
            per_co[r["company"]] += 1
            n += 1
    out = HERE / "data" / "layer_b_pool.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in take.values():
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} eligible real sentences -> {len(take)} chosen -> {out}")
    print("company", dict(per_co.most_common()))
    print("families", dict(Counter(f for r in take.values() for f in r["families"]).most_common()))


if __name__ == "__main__":
    main()
