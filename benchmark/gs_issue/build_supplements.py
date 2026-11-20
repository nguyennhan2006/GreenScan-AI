"""Bù dữ liệu cho các bộ cũ bị lệch (đo ở benchmark/data_card.py, 11/11/2026).

    python -X utf8 benchmark/gs_issue/build_supplements.py

1. supp_explain.jsonl: D-EXPLAIN có 4/200 CONTRADICTED và 25 SUPPORTED. Lấy từ GS-Bench v1 (đã có nhãn kết luận) 50 ca C và
   35 ca S, rải theo doanh nghiệp (trần 12 ca / doanh nghiệp / nhãn), ở định dạng lô D-EXPLAIN, kèm `key_numbers`
   (số của tuyên bố và của bằng chứng) để chấm lời giải thích một cách tự động: lời giải thích cho một ca C phải nêu
   cả số của tuyên bố lẫn số của bằng chứng.
2. supp_score_pairs.jsonl: D-SCORE có 7/200 mẫu dải "high". Sinh 80 cặp song sinh: cùng một câu sạch và bản đột biến
   mang lỗi nặng (ABSOLUTE_CLAIM, OFFSET_NEUTRALITY, FUTURE_AS_ACHIEVED, INTENSITY_VS_ABSOLUTE, HIDDEN_TRADEOFF,
   VAGUE_TERM, MISSING_BASELINE, NO_EVIDENCE_REF; 10 cặp mỗi mã). Độ đo: tỷ lệ cặp mà điểm ưu tiên của bản đột biến
   cao hơn bản sạch (thứ tự cặp), và tỷ lệ bản đột biến lỗi nặng vào dải high/critical.
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import gen_cases as G  # noqa: E402
from taxonomy import KIND_OK, numbers  # noqa: E402

SEVERE = {"ABSOLUTE_CLAIM", "OFFSET_NEUTRALITY", "FUTURE_AS_ACHIEVED", "INTENSITY_VS_ABSOLUTE", "HIDDEN_TRADEOFF"}


def explain_supp(rng):
    gb = [json.loads(line) for line in open(ROOT / "benchmark/gs_bench_v1/gs_bench_v1.jsonl", encoding="utf-8")]
    out = []
    for label, want in (("C", 50), ("S", 35)):
        pool = [r for r in gb if r["labels"] == [label]]
        rng.shuffle(pool)
        per = Counter()
        for r in pool:
            if len([o for o in out if o["ref_verdict_short"] == label]) >= want:
                break
            if per[r["company"]] >= 12:
                continue
            per[r["company"]] += 1
            out.append({"item_id": "X-" + r["id"], "company": r["company"], "sector": r["sector"], "layer": r["layer"],
                        "family": r.get("family"), "claim": {"text": r["claim"]},
                        "evidence": [{"chunk_id": "gsb-" + r["id"], "source_type": "external" if r["layer"] != "B-b" else "internal",
                                      "text": r["evidence"]}],
                        "ref_verdict_short": label, "ref_verdict": {"C": "CONTRADICTED", "S": "SUPPORTED"}[label],
                        "key_numbers": {"claim": sorted(numbers(r["claim"])), "evidence": sorted(numbers(r["evidence"]))},
                        "label_source": "GS-Bench v1 label", "review_status": "pending_human_review"})
    return out


def score_pairs(rng):
    out = []
    codes = ["ABSOLUTE_CLAIM", "OFFSET_NEUTRALITY", "FUTURE_AS_ACHIEVED", "INTENSITY_VS_ABSOLUTE", "HIDDEN_TRADEOFF",
             "VAGUE_TERM", "MISSING_BASELINE", "NO_EVIDENCE_REF"]
    for code in codes:
        for i in range(10):
            s = G.draw(rng)
            st = rng.getstate()
            if code in G.EVIDENCE_CODES:
                bad = G.EVIDENCE_CODES[code](s, rng, f"P-{code[:8]}-{i}", sorted(KIND_OK[code]), mutated=True)
                rng.setstate(st)
                good = G.EVIDENCE_CODES[code](s, rng, f"P-{code[:8]}-{i}", sorted(KIND_OK[code]), mutated=False)
                if code == "HIDDEN_TRADEOFF":  # the twin differs by its evidence only
                    pass
            elif code in G.DROP_CODE:
                clean = G.render(s)
                good = {"claim": clean, "evidence": ""}
                bad = {"claim": G.render(s, drop={G.DROP_CODE[code]}), "evidence": ""}
            else:
                clean = G.render(s)
                phrase = rng.choice(G.INJECT[code]) if code in G.INJECT else (
                    f"đồng thời đạt trung hòa carbon trong năm {s['P']} nhờ mua tín chỉ carbon")
                good = {"claim": clean, "evidence": ""}
                bad = {"claim": G.with_clause(clean, phrase), "evidence": ""}
            out.append({"pair_id": f"P-{code}-{i:02d}", "code": code, "severe": code in SEVERE, "sector": s["sector"],
                        "clean": {"claim": good["claim"], "evidence": good.get("evidence", "")},
                        "mutated": {"claim": bad["claim"], "evidence": bad.get("evidence", "")},
                        "expect": "risk(mutated) > risk(clean)" + ("; mutated band high or critical" if code in SEVERE else "")})
    return out


def main():
    rng = random.Random(20261111)
    d = HERE / "data"
    ex = explain_supp(rng)
    with open(d / "supp_explain.jsonl", "w", encoding="utf-8") as fh:
        for r in ex:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    sp = score_pairs(rng)
    with open(d / "supp_score_pairs.jsonl", "w", encoding="utf-8") as fh:
        for r in sp:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("supp_explain", len(ex), dict(Counter(r["ref_verdict"] for r in ex)), "companies", dict(Counter(r["company"] for r in ex)))
    print("supp_score_pairs", len(sp), dict(Counter(r["code"] for r in sp)))
    same = sum(p["clean"]["claim"] == p["mutated"]["claim"] for p in sp)
    print("pairs whose claim text is identical (differ by evidence only):", same)


if __name__ == "__main__":
    main()
