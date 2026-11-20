"""GS-Issue lớp A: ca đột biến có đáp án. Mỗi ca = một câu sạch (đủ chỉ số, số, kỳ, năm gốc, phạm vi, nguồn)
bị đột biến đúng MỘT chỗ (hoặc hai, ở phần A-multi), nên mã vấn đề, chỗ cần sửa và bản sửa mẫu đều biết chắc.

    python -I -X utf8 benchmark/gs_issue/gen_cases.py                    # mặc định: 40 ca / mã, seed 20261111
    python -I -X utf8 benchmark/gs_issue/gen_cases.py --per-code 60 --seed 7 --out benchmark/gs_issue/data/extra.jsonl
    python -I -X utf8 benchmark/gs_issue/gen_cases.py --codes ABSOLUTE_CLAIM,OFFSET_NEUTRALITY --per-code 30 --out ...

Doanh nghiệp, nhà máy, đơn vị bảo đảm là tên hư cấu. Không có số nào lấy từ báo cáo thật.
Mỗi dòng: id, split (A-single | A-clean | A-multi), codes, claim, evidence, sector, company, template,
fix_kinds_ok, reference_fix, oracle (cách chấm bản sửa), span (cụm bị chèn, nếu có), seed_id.
Cách thêm mẫu câu, mã mới, kiểm cân bằng: docs/04-data-ai/HUONG_DAN_TAO_THEM_CASE.md.
"""
import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from taxonomy import CODES, KIND_OK  # noqa: E402

SECTORS = [
    # sector, company (full), short name, facilities, product (for intensity)
    ("thép", "Công ty Cổ phần Thép Phúc An", "Thép Phúc An", ["Nhà máy luyện thép Nghi Sơn 2", "Khu liên hợp gang thép Kỳ Long"], "thép thô"),
    ("xi măng", "Công ty Cổ phần Xi măng Đồng Lâm", "Xi măng Đồng Lâm", ["Nhà máy xi măng Lương Sơn", "Trạm nghiền Hiệp Phước"], "clinker"),
    ("điện", "Tổng Công ty Điện lực Sông Mây", "Điện lực Sông Mây", ["Nhà máy nhiệt điện Vĩnh Hảo 3", "Nhà máy thủy điện Đắk Rình"], "MWh điện"),
    ("sữa", "Công ty Cổ phần Sữa Đồng Xanh", "Sữa Đồng Xanh", ["Nhà máy sữa Bình Minh", "Trang trại bò sữa Mộc Châu Xanh"], "tấn sữa thành phẩm"),
    ("dệt may", "Tổng Công ty Dệt may Hồng Lĩnh", "Dệt may Hồng Lĩnh", ["Nhà máy nhuộm Phố Nối", "Nhà máy may Hòa Khánh"], "nghìn sản phẩm"),
    ("bán lẻ", "Công ty Cổ phần Bán lẻ Lạc Xuân", "Bán lẻ Lạc Xuân", ["Trung tâm phân phối Long Hậu", "hệ thống 120 cửa hàng phía Nam"], "tỷ đồng doanh thu"),
    ("ngân hàng", "Ngân hàng TMCP Phù Sa", "Ngân hàng Phù Sa", ["Hội sở chính tại Hà Nội", "khối chi nhánh phía Nam"], "nhân viên"),
    ("bất động sản", "Công ty Cổ phần Địa ốc An Cư", "Địa ốc An Cư", ["Khu đô thị Sông Hậu", "Tòa văn phòng An Cư Tower"], "m2 sàn"),
    ("hóa chất", "Công ty Cổ phần Hóa chất Đức Giang Nam", "Hóa chất Đức Giang Nam", ["Nhà máy xút clo Việt Trì Nam", "Nhà máy phân bón Lâm Thao Mới"], "tấn sản phẩm"),
    ("vận tải", "Công ty Cổ phần Vận tải Cánh Cò", "Vận tải Cánh Cò", ["đội xe tải Bắc – Nam", "cảng cạn Tân Cảng Bắc"], "tấn-km"),
]
METRICS = [  # metric phrase, needs GHG scope phrase
    ("phát thải khí nhà kính", True),
    ("lượng nước tiêu thụ", False),
    ("điện năng tiêu thụ", False),
    ("lượng chất thải rắn đưa đi chôn lấp", False),
    ("lượng nhiên liệu hóa thạch sử dụng", False),
    ("lượng nước thải xả ra môi trường", False),
]
# No year in a source: a year there would let a reader recover a dropped reporting period.
SOURCES = ["Báo cáo phát triển bền vững, trang {pg}", "Báo cáo kiểm kê khí nhà kính, bảng {tb}",
           "Báo cáo thường niên, trang {pg}", "Phụ lục số liệu môi trường, mục {tb}"]
ASSURERS = ["Công ty TNHH Kiểm định Sao Việt", "Công ty TNHH Đảm bảo Bền vững Hạ Long", "Viện Chứng nhận Chất lượng Trường Sơn"]
VAGUE = ["góp phần xây dựng hình ảnh doanh nghiệp xanh và thân thiện với môi trường", "khẳng định cam kết phát triển xanh, sạch và bền vững",
         "thể hiện nỗ lực không ngừng vì một tương lai xanh", "hướng tới mô hình sản xuất thân thiện với môi trường"]
ABSOLUTE = ["và hoàn toàn không gây tác động tiêu cực nào đến môi trường", "đạt mức hiệu quả môi trường tốt nhất toàn ngành",
            "giúp sản phẩm của Công ty sạch 100 %", "qua đó loại bỏ hoàn toàn rủi ro ô nhiễm"]
CERTS = [("ISO 14001:2015", "hệ thống quản lý môi trường"), ("ISO 50001:2018", "hệ thống quản lý năng lượng"),
         ("LEED Gold", "công trình"), ("EDGE Advanced", "công trình"), ("nhãn Sinh thái Việt Nam", "dòng sản phẩm chủ lực")]
ISSUERS = ["Tổ chức Chứng nhận Quốc tế Sao Mai", "Hội đồng Công trình Xanh Đông Dương", "Trung tâm Chứng nhận Phù Hợp Bắc Hải"]
SMALL_GOOD = [("giảm {v}% lượng túi ni-lông phát cho khách tại hệ thống cửa hàng", "phát thải khí nhà kính phạm vi 1 và 2"),
              ("lắp đặt hệ thống điện mặt trời áp mái công suất {k} kWp tại văn phòng", "điện năng tiêu thụ từ lưới điện than"),
              ("trồng {k} cây xanh tại khu vực nhà máy", "diện tích rừng tự nhiên bị chuyển đổi cho dự án mở rộng"),
              ("chuyển {v}% xe nâng trong kho sang chạy điện", "lượng dầu diesel tiêu thụ của đội xe vận tải")]
MANDATORY = ["không sử dụng môi chất làm lạnh CFC trong sản phẩm", "thực hiện đánh giá tác động môi trường trước khi xây dựng dự án mới",
             "lắp đặt hệ thống quan trắc nước thải tự động, truyền dữ liệu về Sở Tài nguyên và Môi trường",
             "nộp báo cáo công tác bảo vệ môi trường định kỳ hằng năm", "thu gom và chuyển giao chất thải nguy hại cho đơn vị có giấy phép"]
PIONEER = ["tự hào là doanh nghiệp tiên phong khi", "tự hào dẫn đầu ngành khi", "khẳng định vị thế tiên phong khi"]

# Change-claim templates: (slot, text). Slots that may be dropped: period, baseline, scope, figure, source.
TEMPLATES = {
    "T1": [("period", "năm {P}, "), ("", "{metric}"), ("scope", " {scope}"), ("", " của {company}"), ("figure", " giảm {v}%"),
           ("baseline", " so với năm gốc {B}"), ("source", " ({source}{assur})"), ("", ".")],
    "T2": [("baseline", "so với năm gốc {B}, "), ("", "{company} đã"), ("figure", " giảm {v}%"), ("", " {metric}"), ("scope", " {scope}"),
           ("period", " trong năm {P}"), ("source", " ({source}{assur})"), ("", ".")],
    "T3": [("period", "trong năm {P}, "), ("", "{company} ghi nhận {metric}"), ("scope", " {scope}"), ("figure", " giảm {v}%"),
           ("baseline", " so với năm gốc {B}"), ("source", ", theo {source}{assur}"), ("", ".")],
}
NOFIG = {"T1": " đã giảm", "T2": " giảm", "T3": " giảm"}
PH = {"period": "[bổ sung: kỳ báo cáo]", "baseline": "[bổ sung: năm gốc]", "scope": "[bổ sung: phạm vi, ranh giới]",
      "source": "[bổ sung: nguồn xác minh]", "figure": "[bổ sung: giá trị cụ thể]"}
DROP_CODE = {"MISSING_PERIOD": "period", "MISSING_BASELINE": "baseline", "MISSING_SCOPE": "scope",
             "NO_FIGURE": "figure", "NO_EVIDENCE_REF": "source"}
INJECT = {"VAGUE_TERM": VAGUE, "ABSOLUTE_CLAIM": ABSOLUTE}


def cap(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;)])", r"\1", s)
    return s[:1].upper() + s[1:]


def draw(rng):
    sector, company, short, facs, product = rng.choice(SECTORS)
    metric, ghg = rng.choice(METRICS)
    fac = rng.choice(facs)
    P = rng.choice([2023, 2024, 2025])
    B = rng.choice([2018, 2019, 2020, 2021])
    scope = rng.choice(["phạm vi 1 và 2", "phạm vi 1, 2 và 3"]) + f" của {fac}" if ghg else f"tại {fac}"
    src = rng.choice(SOURCES).format(P=P, pg=rng.randint(12, 140), tb=f"{rng.randint(2, 9)}.{rng.randint(1, 6)}")
    assur = f"; số liệu đã được {rng.choice(ASSURERS)} bảo đảm độc lập" if rng.random() < 0.5 else ""
    return dict(sector=sector, company=company, short=short, fac=fac, product=product, metric=metric, P=P, B=B, scope=scope,
                source=src, assur=assur, v=rng.choice([3, 4.5, 6, 7.2, 8, 9.5, 11, 12, 15, 18, 21, 24]), tpl=rng.choice(list(TEMPLATES)))


def fmt_v(v):
    return str(v).replace(".", ",")


def render(s, drop=(), ph=(), nofig=False):
    out = []
    for slot, txt in TEMPLATES[s["tpl"]]:
        if slot in drop:
            continue
        if slot == "figure" and nofig:
            out.append(NOFIG[s["tpl"]])
            continue
        vals = dict(s, v=fmt_v(s["v"]))
        if slot in ph:  # reference fix: the slot's value becomes a placeholder
            vals = dict(vals, P=PH["period"], B=PH["baseline"], scope=PH["scope"], source=PH["source"], assur="")
            if slot == "figure":
                txt = NOFIG[s["tpl"]] + " " + PH["figure"]
        out.append(txt.format(**vals))
    return cap("".join(out))


def with_clause(text, clause):
    return cap(text[:-1] + ", " + clause + ".")


def case(cid, split, codes, s, claim, ref, kinds, oracle, evidence="", span=None, template=None):
    return dict(id=cid, split=split, codes=codes, claim=claim, evidence=evidence, sector=s["sector"], company=s["company"],
                template=template or s.get("tpl"), fix_kinds_ok=kinds, reference_fix=ref, oracle=oracle, span=span,
                needs_edit=bool(codes))


def make_single(code, rng, i, seed_tag):
    s = draw(rng)
    cid = f"A-{code[:12].lower()}-{seed_tag}-{i:03d}"
    kinds = sorted(KIND_OK[code])
    if code in DROP_CODE:
        slot = DROP_CODE[code]
        if code == "NO_FIGURE":
            claim, ref = render(s, nofig=True), render(s, ph={"figure"})
        else:
            claim, ref = render(s, drop={slot}), render(s, ph={slot})
        return case(cid, "A-single", [code], s, claim, ref, kinds, {"type": "slot", "slot": slot})
    if code in INJECT:
        phrase = rng.choice(INJECT[code])
        clean = render(s)
        return case(cid, "A-single", [code], s, with_clause(clean, phrase), clean, kinds,
                    {"type": "phrase", "phrase": phrase, "slot": "figure"}, span=phrase)
    if code == "OFFSET_NEUTRALITY":
        clean = render(s)
        phrase = f"đồng thời đạt trung hòa carbon trong năm {s['P']} nhờ mua tín chỉ carbon"
        ref = with_clause(clean, f"đồng thời bù trừ một phần phát thải năm {s['P']} bằng tín chỉ carbon [bổ sung: tỷ lệ bù trừ, sổ đăng ký tín chỉ]")
        return case(cid, "A-single", [code], s, with_clause(clean, phrase), ref, kinds,
                    {"type": "phrase", "phrase": phrase, "slot": "offset"}, span=phrase)
    if code == "NO_EVIDENCE_REF":
        pass
    return EVIDENCE_CODES[code](s, rng, cid, kinds, mutated=True)


# ---- codes that need a second sentence (evidence) to be visible; each also yields a clean contrast case
def ev_future(s, rng, cid, kinds, mutated):
    T, v = rng.choice([2030, 2035]), rng.choice([20, 25, 30, 40])
    got = round(v * rng.choice([0.2, 0.3, 0.4]), 1)
    base = f"{s['company']} {{verb}} {v}% {s['metric']} {s['scope']} {{tail}} so với năm gốc {s['B']} ({s['source']})."
    target = cap(base.format(verb="đặt mục tiêu giảm", tail=f"vào năm {T}"))
    claim = cap(base.format(verb="đã giảm", tail=f", hoàn thành mục tiêu năm {T}")) if mutated else target
    ev = (f"Lộ trình giảm phát thải: mục tiêu giảm {v}% {s['metric']} vào năm {T} so với năm gốc {s['B']}. "
          f"Kết quả năm {s['P']}: giảm {fmt_v(got)}% so với năm gốc.")
    return case(cid, "A-single" if mutated else "A-clean", ["FUTURE_AS_ACHIEVED"] if mutated else [], s, claim, target, kinds,
                {"type": "phrase", "phrase": f"hoàn thành mục tiêu năm {T}", "forbid": r"đã giảm|hoàn thành",
                 "require": r"mục tiêu|cam kết|kế hoạch|phấn đấu|hướng tới|dự kiến"}, evidence=ev,
                span=f"đã giảm {v}%" if mutated else None, template="future")


def ev_cert(s, rng, cid, kinds, mutated):
    cert, what = rng.choice(CERTS)
    full = cap(f"năm {s['P']}, {s['fac']} của {s['company']} được {rng.choice(ISSUERS)} cấp chứng nhận {cert} cho {what}, "
               f"hiệu lực đến năm {s['P'] + 3}.")
    short = cap(f"năm {s['P']}, {s['fac']} của {s['company']} đạt chứng nhận {cert}.")
    ref = cap(f"năm {s['P']}, {s['fac']} của {s['company']} đạt chứng nhận {cert} [bổ sung: tổ chức cấp, phạm vi, hiệu lực].")
    return case(cid, "A-single" if mutated else "A-clean", ["UNVERIFIED_LABEL_OR_CERT"] if mutated else [], s,
                short if mutated else full, ref if mutated else full, kinds, {"type": "slot", "slot": "issuer"},
                span=f"đạt chứng nhận {cert}" if mutated else None, template="cert")


def ev_tradeoff(s, rng, cid, kinds, mutated):
    good, bad = rng.choice(SMALL_GOOD)
    claim = cap(f"năm {s['P']}, {s['company']} " + good.format(v=rng.choice([15, 20, 30, 40]), k=rng.choice([120, 350, 800, 1500]))
                + f" ({s['source']}).")
    w = rng.choice([12, 18, 25, 34])
    ev = (f"Năm {s['P']}, {bad} của {s['short']} tăng {w}% so với năm {s['P'] - 1} do mở rộng công suất." if mutated else
          f"Năm {s['P']}, {bad} của {s['short']} giảm {w}% so với năm {s['P'] - 1}.")
    ref = claim[:-1] + "; [bổ sung: diễn biến tổng phát thải cùng kỳ để người đọc thấy bối cảnh]."
    return case(cid, "A-single" if mutated else "A-clean", ["HIDDEN_TRADEOFF"] if mutated else [], s, claim,
                ref if mutated else claim, kinds, {"type": "slot", "slot": "context"}, evidence=ev, template="tradeoff")


def ev_irrelevant(s, rng, cid, kinds, mutated):
    duty = rng.choice(MANDATORY)
    pioneer = rng.choice(PIONEER)
    claim = cap(f"{s['company']} {pioneer} {duty}.") if mutated else cap(f"{s['company']} {duty} theo quy định của Luật Bảo vệ môi trường 2020.")
    ref = cap(f"{s['company']} {duty} theo quy định của pháp luật về bảo vệ môi trường.")
    return case(cid, "A-single" if mutated else "A-clean", ["IRRELEVANT_CLAIM"] if mutated else [], s, claim, ref if mutated else claim,
                kinds, {"type": "phrase", "phrase": pioneer, "alt": r"theo quy định|bắt buộc|nghĩa vụ"},
                span=pioneer if mutated else None, template="irrelevant")


def ev_intensity(s, rng, cid, kinds, mutated):
    v, w = rng.choice([4, 5.5, 7, 9]), rng.choice([6, 11, 15, 22])
    phrase = f"qua đó cắt giảm tổng lượng phát thải của {s['short']}"
    base = (f"năm {s['P']}, cường độ phát thải khí nhà kính trên mỗi {s['product']} của {s['company']} giảm {fmt_v(v)}% "
            f"so với năm gốc {s['B']}")
    clean = cap(base + f" ({s['source']}).")
    claim = cap(base + f", {phrase} ({s['source']}).") if mutated else clean
    ev = f"Tổng phát thải khí nhà kính phạm vi 1 và 2 của {s['short']} năm {s['P']} tăng {w}% so với năm gốc {s['B']} do sản lượng tăng."
    return case(cid, "A-single" if mutated else "A-clean", ["INTENSITY_VS_ABSOLUTE"] if mutated else [], s, claim, clean, kinds,
                {"type": "phrase", "phrase": phrase, "slot": "context"}, evidence=ev, span=phrase if mutated else None, template="intensity")


def ev_entity(s, rng, cid, kinds, mutated):
    x = rng.randint(120, 980) * 1000 + rng.randint(100, 999)
    y = int(x * rng.choice([1.6, 2.3, 3.1]))
    f = lambda n: f"{n:,}".replace(",", ".")
    who = f"{s['short']}" if mutated else f"Công ty mẹ {s['short']}"
    claim = cap(f"năm {s['P']}, tổng phát thải khí nhà kính phạm vi 1 và 2 của {who} là {f(x)} tCO2e ({s['source']}).")
    ref = cap(f"năm {s['P']}, tổng phát thải khí nhà kính phạm vi 1 và 2 của {s['short']} [bổ sung: công ty mẹ hay hợp nhất] là {f(x)} tCO2e ({s['source']}).")
    ev = f"Bảng phát thải năm {s['P']} (tCO2e): Công ty mẹ: {f(x)}; Hợp nhất toàn tập đoàn: {f(y)}."
    return case(cid, "A-single" if mutated else "A-clean", ["ENTITY_SCOPE_AMBIGUOUS"] if mutated else [], s, claim,
                ref if mutated else claim, kinds, {"type": "slot", "slot": "scope"}, evidence=ev, template="entity")


EVIDENCE_CODES = {"FUTURE_AS_ACHIEVED": ev_future, "UNVERIFIED_LABEL_OR_CERT": ev_cert, "HIDDEN_TRADEOFF": ev_tradeoff,
                  "IRRELEVANT_CLAIM": ev_irrelevant, "INTENSITY_VS_ABSOLUTE": ev_intensity, "ENTITY_SCOPE_AMBIGUOUS": ev_entity}
MULTI = [("MISSING_PERIOD", "MISSING_BASELINE"), ("MISSING_SCOPE", "NO_EVIDENCE_REF"), ("MISSING_BASELINE", "VAGUE_TERM"),
         ("MISSING_PERIOD", "ABSOLUTE_CLAIM"), ("NO_EVIDENCE_REF", "OFFSET_NEUTRALITY"), ("MISSING_SCOPE", "MISSING_PERIOD")]


def make_multi(pair, rng, i, seed_tag):
    s = draw(rng)
    drops = {DROP_CODE[c] for c in pair if c in DROP_CODE}
    claim, ref = render(s, drop=drops), render(s, ph=drops)
    oracles = [{"type": "slot", "slot": DROP_CODE[c]} for c in pair if c in DROP_CODE]
    span = None
    for c in pair:
        if c in INJECT:
            span = rng.choice(INJECT[c])
            claim = with_clause(claim, span)
            oracles.append({"type": "phrase", "phrase": span, "slot": "figure"})
        if c == "OFFSET_NEUTRALITY":
            span = f"đồng thời đạt trung hòa carbon trong năm {s['P']} nhờ mua tín chỉ carbon"
            claim = with_clause(claim, span)
            oracles.append({"type": "phrase", "phrase": span, "slot": "offset"})
    kinds = sorted(set().union(*(KIND_OK[c] for c in pair)))
    c = case(f"A-multi-{seed_tag}-{i:03d}", "A-multi", list(pair), s, claim, ref, kinds, {"type": "all", "parts": oracles}, span=span)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-code", type=int, default=40)
    ap.add_argument("--clean", type=int, default=60, help="câu sạch dạng thay đổi (ngoài các ca đối chứng có bằng chứng)")
    ap.add_argument("--contrast", type=int, default=10, help="ca sạch đối chứng cho mỗi mã cần bằng chứng")
    ap.add_argument("--multi", type=int, default=10, help="ca hai lỗi cho mỗi cặp")
    ap.add_argument("--codes", default="", help="chỉ sinh các mã này (phân cách bằng dấu phẩy)")
    ap.add_argument("--seed", type=int, default=20261111)
    ap.add_argument("--out", default=str(HERE / "data" / "layer_a.jsonl"))
    a = ap.parse_args()
    rng = random.Random(a.seed)
    tag = str(a.seed)[-4:]
    codes = a.codes.split(",") if a.codes else list(CODES)
    rows, seen = [], set()
    for code in codes:
        n = 0
        while n < a.per_code:
            c = make_single(code, rng, n, tag)
            if c["claim"] in seen:
                continue
            seen.add(c["claim"])
            rows.append(c)
            n += 1
    if not a.codes:
        for i in range(a.clean):
            s = draw(rng)
            t = render(s)
            if t not in seen:
                seen.add(t)
                rows.append(case(f"A-clean-{tag}-{i:03d}", "A-clean", [], s, t, t, [], {"type": "none"}))
        for code, fn in EVIDENCE_CODES.items():
            for i in range(a.contrast):
                rows.append(fn(draw(rng), rng, f"A-clean-{code[:8].lower()}-{tag}-{i:03d}", sorted(KIND_OK[code]), mutated=False))
        for j, pair in enumerate(MULTI):
            for i in range(a.multi):
                rows.append(make_multi(pair, rng, j * 100 + i, tag))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    cnt = Counter(c for r in rows for c in (r["codes"] or ["CLEAN"]))
    print(f"wrote {len(rows)} cases -> {a.out}")
    print("split", dict(Counter(r["split"] for r in rows)))
    print("codes", dict(sorted(cnt.items())))


if __name__ == "__main__":
    main()
