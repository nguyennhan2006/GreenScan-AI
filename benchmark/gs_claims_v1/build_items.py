"""GS-Claims v1: sentence-level labelling set for the claim extractor (is_claim + attributes).

Pool: the claim-source documents of four stored runs of four sectors (steel HPG, pharma DHG,
construction CTD, port GMD). Per report: 18 sentences the extractor kept as claims and 17 it did not
(sentences with a non-year figure or an environmental word, so recall is measured where misses
matter). Ten control items with a known answer are mixed in to check each labeller.

Labellers see only items.jsonl (text + short context). What the system did is kept in
_key/key.jsonl, which labellers must not open.

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_claims_v1/build_items.py
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quantum_gw.utils.text import normalize_for_match, parse_quantities, split_sentences  # noqa: E402

RUNS = {"HPG": "409344b041b64787", "DHG": "142d3b8153b44e11", "CTD": "529d9785f2f14680", "GMD": "a811b95099a24f23"}
PER_REPORT_CLAIMS, PER_REPORT_OTHER = 18, 17
ENV = re.compile(r"(?<!\w)(phat thai|khi nha kinh|carbon|co2|nang luong|dien|nuoc|chat thai|tai che|xanh|moi truong|"
                 r"net zero|trung hoa|tai tao|tiet kiem|esg|ben vung|emission|energy|water|waste|recycl)(?!\w)")

CONTROLS = [
    ("DANH MỤC TỪ VIẾT TẮT", {"is_claim": "no"}),
    ("Biểu đồ 3: Lượng chất thải rắn phát sinh qua các năm", {"is_claim": "no"}),
    ("Báo cáo của Ban Tổng Giám đốc", {"is_claim": "no"}),
    ("GRI 303-3, GRI 303-5", {"is_claim": "no"}),
    ("Lợi nhuận sau thuế năm 2024 đạt 1.250 tỷ đồng, tăng 9% so với năm 2023.", {"is_claim": "no", "has_figure": "no"}),
    ("Năm 2024, phát thải khí nhà kính phạm vi 1 của Nhà máy Phú Mỹ là 412.000 tCO2e.",
     {"is_claim": "yes", "claim_kind": "metric_disclosure", "has_figure": "yes", "has_period": "yes",
      "has_ghg_scope": "yes", "has_boundary": "yes"}),
    ("Lượng chất thải nguy hại phát sinh năm 2024 giảm 15% so với năm 2022.",
     {"is_claim": "yes", "claim_kind": "performance", "has_figure": "yes", "has_period": "yes", "has_baseline": "yes"}),
    ("Tập đoàn đặt mục tiêu đến năm 2030 sử dụng 30% điện từ năng lượng tái tạo.",
     {"is_claim": "yes", "claim_kind": "commitment", "has_figure": "yes", "has_period": "yes"}),
    ("Với sứ mệnh vì một hành tinh xanh, chúng tôi luôn tiên phong trong các giải pháp bền vững.",
     {"is_claim": "yes", "claim_kind": "promotional", "has_figure": "no", "promotional_language": "yes"}),
    ("Báo cáo kiểm kê khí nhà kính năm 2024 của Công ty đã được tổ chức chứng nhận độc lập thẩm định theo ISO 14064-3.",
     {"is_claim": "yes", "has_figure": "no", "has_period": "yes", "cites_independent_source": "yes"}),
]


def _sid(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]


def main() -> None:
    rng = random.Random(20261115)
    items, key = [], []
    for company, run in RUNS.items():
        rdir = ROOT / ".quantum" / "runs" / run / "contract"
        extract = [json.loads(line) for line in (rdir / "extract.jsonl").open(encoding="utf-8")]
        claims = [e for e in extract if e["extract_type"] == "claim"]
        rejected = {normalize_for_match(e["text"]): e.get("rejected_reason") for e in extract
                    if e["extract_type"] == "rejected_sentence"}
        claim_norm = {normalize_for_match(c["text"]) for c in claims}
        units = [json.loads(line) for line in (rdir / "clean.jsonl").open(encoding="utf-8")]
        units = [u for u in units if u.get("role") == "claim_source"]
        others, seen = [], set()
        for u in units:
            sents = split_sentences(u["text"]) or [u["text"]]
            for i, s in enumerate(sents):
                s = s.strip()
                n = normalize_for_match(s)
                if not (25 <= len(s) <= 450) or n in claim_norm or n in seen:
                    continue
                figure = any(not (1900 <= q[0] <= 2100) for q in parse_quantities(s))
                if not (figure or ENV.search(n)):
                    continue
                seen.add(n)
                ctx = " … ".join(x.strip()[:100] for x in (sents[i - 1] if i else "", sents[i + 1] if i + 1 < len(sents) else "") if x)
                others.append({"text": s, "context": ctx, "page": u.get("page"), "reason": rejected.get(n, "skipped_no_claim_type_or_filter")})
        pick_c = rng.sample(claims, min(PER_REPORT_CLAIMS, len(claims)))
        pick_o = rng.sample(others, min(PER_REPORT_OTHER, len(others)))
        for c in pick_c:
            iid = "C-" + _sid(company, c["text"])
            items.append({"item_id": iid, "company": company, "text": c["text"][:450], "context": ""})
            key.append({"item_id": iid, "company": company, "run_id": run, "page": c.get("page"),
                        "system_extracted": True, "system_claim_type": c.get("claim_type"), "control": None})
        for o in pick_o:
            iid = "C-" + _sid(company, o["text"])
            items.append({"item_id": iid, "company": company, "text": o["text"], "context": o["context"]})
            key.append({"item_id": iid, "company": company, "run_id": run, "page": o["page"],
                        "system_extracted": False, "system_reason": o["reason"], "control": None})
    for text, answer in CONTROLS:
        iid = "C-" + _sid("control", text)
        items.append({"item_id": iid, "company": "—", "text": text, "context": ""})
        key.append({"item_id": iid, "company": "control", "run_id": None, "system_extracted": None, "control": answer})
    rng.shuffle(items)
    (HERE / "_key").mkdir(exist_ok=True)
    with (HERE / "items.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    with (HERE / "_key" / "key.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for k in key:
            fh.write(json.dumps(k, ensure_ascii=False) + "\n")
    print(f"[gs-claims] {len(items)} items ({sum(1 for k in key if k['system_extracted'])} extracted, "
          f"{sum(1 for k in key if k['system_extracted'] is False)} not extracted, {len(CONTROLS)} controls)")


if __name__ == "__main__":
    main()
