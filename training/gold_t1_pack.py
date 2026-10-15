"""T1 gold: people label sentences independently, meet, agree, and the agreement is the gold.

Why this exists. The HPG queue check (04_HPG_Hang_doi_22muc.xlsx) asked one yes/no
question about 22 items the product had already picked: right for measuring the
queue, wrong for the T1 student, which predicts four classes on every sentence
and must be measured on sentences the rules missed. This tool turns labelling
into a protocol whose output can be trained on, evaluated against and reported:

  two sets      hpg    every environmental sentence of HPG BCPTBV 2025 (test:
                       Hòa Phát has no sentence in the training corpus, and the
                       text comes from the product's own PDF parser)
                audit  sentences the teacher already labelled, from the corpus
                       companies (dev: how good are the teacher labels the
                       student will be trained on; model selection)
  one form      the four T1 classes of teacher_label.py + UNSURE, the product's
                eight claim types, the reason for NOT_CLAIM, confidence 1–3,
                context needed, signals, AI-assisted
  one protocol  everyone labels every lot alone → `consensus` builds the meeting
                workbook (only the rows that differ) → the meeting decides and
                writes new conventions → `import-consensus` → later packs carry
                the updated codebook → `merge` → gold → `report` (κ with CI,
                teacher/rule quality, effort) for the jury

Lots are stratified random samples, so any number of finished lots is a fair
sample of the set: stopping early shrinks the gold, it does not bias it.

usage:
  python training/gold_t1_pack.py build --set hpg            # from the PDF
  python training/gold_t1_pack.py build --set audit          # from the teacher batch
  python training/gold_t1_pack.py export --set hpg --lots 1 --labelers quynh thao
  python training/gold_t1_pack.py export-xlsx --labelers nhan quynh thao [--lots 2]   # simplest form
  python training/gold_t1_pack.py export-csv --labeler nhan [--lots 2]   # same form as CSV + T1_cach_dien.md
  python training/gold_t1_pack.py import <filled.xlsx|filled.csv> [...]
  python training/gold_t1_pack.py consensus --set hpg [--lots 1]
  python training/gold_t1_pack.py import-consensus <meeting.xlsx>
  python training/gold_t1_pack.py merge --set hpg
  python training/gold_t1_pack.py report --set hpg
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from labeling_pack import CLAIM_TYPES, _minutes  # noqa: E402  (the product's eight claim types)

OUT = ROOT / "training/data/gold_t1"
REPORTS = ROOT / "benchmark/gold_t1"
PDF = ROOT / "data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf"
TEACHER = ROOT / "training/data/teacher_claim_gemma-4-31B-it.jsonl"
CLEAN = ROOT / "data/crawl/vn30/contract/clean.jsonl"
DECISIONS = ROOT / "configs/measurement_decisions.yaml"

# code — gloss; the code before " — " is what is stored. Classes and wording as
# CLAIM_PROMPT in teacher_label.py, plus UNSURE for people.
LABELS = [
    "QUANTIFIED_CLAIM — tuyên bố MT của DN, có số liệu",
    "QUALITATIVE_CLAIM — tuyên bố MT cụ thể của DN, không số",
    "VAGUE — chung chung, khẩu hiệu, không kiểm chứng được",
    "NOT_CLAIM — không phải tuyên bố MT của DN",
    "UNSURE — không chắc (bắt buộc ghi chú)",
]
WHY_NOT = [  # ordered by root cause: the first that applies is the one to pick
    "table_heading — tiêu đề, mục lục, dòng bảng, nhãn biểu đồ",
    "broken — câu bị cắt / ghép lỗi, mất nghĩa",
    "other_org — chủ thể là tổ chức khác (hiệp hội, Chính phủ, ngành, thế giới)",
    "general_knowledge — giải thích kỹ thuật / kiến thức chung",
    "non_env — xã hội, tài chính, quản trị, không liên quan MT",
    "other — khác (ghi chú)",
]
CONFIDENCE = ["3 — chắc chắn", "2 — khá chắc", "1 — phân vân (ghi chú)"]
FLAGS = [
    "OVERCLAIM — lời nói mạnh hơn số liệu",
    "INCONSISTENCY — mâu thuẫn với chỗ khác trong tài liệu",
    "FUTURE — cam kết / lợi ích tương lai, chưa có kết quả",
]
YES = ["Có"]
CLAIMS = {"QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE"}
SETS = {"hpg": "test", "audit": "dev"}

DEFINITIONS = [
    ("Câu hỏi", "Với CÂU CẦN GÁN (cột in đậm): đây có phải tuyên bố môi trường của CHÍNH doanh nghiệp không, loại nào, về chủ đề gì? Câu trước / câu sau chỉ để đọc ngữ cảnh. Không kiểm chứng đúng sai ở bài này."),
    ("QUANTIFIED_CLAIM", "DN tự nói về kết quả, hiện trạng hoặc mục tiêu MÔI TRƯỜNG của mình, có số liệu kiểm chứng được. Ví dụ: 'Trong năm 2025, tỷ lệ phối phế cùng gang lỏng tại KLH Hải Dương đã tăng từ 16% lên 22%.'"),
    ("QUALITATIVE_CLAIM", "DN tự nói về hành động hoặc kết quả môi trường CỤ THỂ của mình, không có số. Ví dụ: 'Các KLH gang thép của Hòa Phát đã triển khai các giải pháp chủ chốt về tiết kiệm năng lượng…'"),
    ("VAGUE", "Khẩu hiệu, cam kết chung chung, lời quảng bá không kiểm chứng được. Ví dụ: 'góp phần bảo vệ môi trường và phát triển bền vững', 'hướng tới tương lai xanh'."),
    ("NOT_CLAIM", "Không phải tuyên bố MT của DN: kiến thức chung, bối cảnh ngành/quốc gia, tổ chức khác, tiêu đề, mục lục, câu mất nghĩa, nội dung xã hội/tài chính/quản trị. Chọn lý do ở cột kế bên."),
    ("UNSURE", "Phân vân thật sự giữa hai nhãn. Bắt buộc ghi: phân vân giữa nhãn nào, vì sao. Câu UNSURE sẽ được đem ra họp."),
    ("Chủ đề", "Bắt buộc khi nhãn là QUANTIFIED / QUALITATIVE / VAGUE. Chọn chủ đề chính của tuyên bố; câu chỉ nói chung về 'xanh, bền vững' → generic_sustainability."),
    ("Độ chắc", "3 chắc chắn · 2 khá chắc · 1 phân vân (ghi chú). Câu có ai chọn 1 sẽ được xem lại khi họp, kể cả khi mọi người cùng nhãn."),
    ("Dấu hiệu", "Không bắt buộc. Gặp thì chọn và ghi một dòng có trang: OVERCLAIM (nói mạnh hơn số liệu), INCONSISTENCY (mâu thuẫn với trang khác), FUTURE (lợi ích tương lai chưa có kết quả)."),
    ("Ghi chú", "Tối đa một dòng (≤ 300 ký tự). Bắt buộc khi UNSURE, lý do 'other', có dấu hiệu, hoặc độ chắc 1. Không tìm bằng chứng ở bài này."),
    ("Làm độc lập", "Mỗi người làm file của mình, KHÔNG bàn với người khác trước khi tất cả cùng nộp. Bất đồng là thông tin có ích: nó cho biết quy tắc nào chưa rõ."),
    ("AI", "Không dùng chatbot để quyết định nhãn: nhãn này là thước đo cho mô hình, nhãn do AI gợi ý thì không đo được gì. Nếu đã lỡ dùng cho câu nào, đánh 'Có' ở cột 'AI hỗ trợ' của câu đó: câu sẽ được đem ra họp, không bị phạt."),
    ("Ô vàng", "Ô chuyển vàng là ô bắt buộc còn trống. Hết ô vàng là file nộp được."),
    ("Nhịp độ", "Khoảng 20–30 giây một câu; một lô 40–50 câu khoảng 20–25 phút. Ghi giờ bắt đầu / kết thúc ở dòng 1."),
]
BASE_CONVENTIONS = [
    ("Q1", "Chủ thể không phải DN", "Ai đang nói, nói về ai? Ô bảng mô tả hiệp hội (VSA…), mối quan tâm của Chính phủ, số liệu của thế giới → NOT_CLAIM / other_org.", "HPG tr.11, tr.33"),
    ("Q2", "Câu nói tác dụng chung", "Tác dụng CHUNG của công nghệ, nguyên liệu (EAF, thép phế, biogas) → NOT_CLAIM / general_knowledge. Tác dụng của biện pháp DN đang làm ('Biện pháp này', 'Qua đó' chỉ về việc của DN) → tuyên bố.", "HPG tr.37"),
    ("Q3", "Câu thiếu chủ ngữ", "'Đây là', 'Biện pháp này', 'Qua đó': đọc cột Câu trước (hoặc mở PDF) rồi gán; đánh 'Có' ở cột 'Phải đọc câu trước/sau'.", "HPG tr.36"),
    ("Q4", "Chữ rác đầu/cuối câu", "'ESG', 'HÒA PHÁT', số trang dính vào câu mà phần còn lại vẫn trọn nghĩa: bỏ qua chữ rác, gán theo nghĩa. Mất nghĩa → NOT_CLAIM / broken.", "HPG tr.7, tr.20"),
    ("Q5", "Câu trùng", "Hai câu giống nhau: cùng một nhãn.", "HPG tr.11"),
    ("Q6", "Mục tiêu chỉ có mốc năm", "'Trung hòa carbon 2050' (chỉ có năm, không có lượng) → QUALITATIVE_CLAIM. Có lượng ('thép phế đạt 30% năm 2030', '130 MWp đến 2027') → QUANTIFIED_CLAIM.", "HPG tr.7, tr.37"),
    ("Q7", "Số không tính là số liệu", "Năm, số hiệu tiêu chuẩn (ISO 14064), số văn bản (NĐ 06/2022), số thứ tự mục không làm câu thành QUANTIFIED.", "HPG tr.35"),
    ("Q8", "Nhiều lý do NOT_CLAIM", "Chọn lý do đứng trước trong danh sách (lý do gốc: vì sao máy nhặt nhầm).", "HPG tr.20"),
    ("Q9", "Câu tiếng Anh", "Báo cáo tiếng Anh của DN Việt Nam: gán y như câu tiếng Việt.", "SAB, PAN"),
]


def code(value) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return str(value).split(" — ")[0].strip()


def _sha(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


_VI = re.compile("[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]")


def _lang(text: str) -> str:
    return "vi" if _VI.search(text.lower()) else "en"


def conventions() -> list[tuple[str, str, str, str]]:
    extra = OUT / "conventions.jsonl"
    rows = [json.loads(line) for line in extra.open(encoding="utf-8")] if extra.exists() else []
    return BASE_CONVENTIONS + [(c["code"], c["situation"], c["rule"], c.get("example") or "") for c in rows]


def codebook_version() -> str:
    return f"codebook v1.{len(conventions()) - len(BASE_CONVENTIONS)}"


# ----------------------------------------------------------------------------- build
class _NullAudit:
    def write(self, *_args, **_kwargs):
        pass


def _extractor():
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.settings import load_settings
    settings = load_settings()
    extractor = ClaimExtractionAgent(settings.claim_extraction, _NullAudit())
    terms = sorted({t for section in (extractor.claim_types, extractor.metrics)
                    for by_lang in section.values() for lang_terms in by_lang.values() for t in lang_terms},
                   key=len, reverse=True)
    return settings, extractor, terms


def build_hpg(args) -> list[dict]:
    """Every sentence of the report through the product's parser and extractor."""
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import DocumentInput
    from quantum_gw.parsers.documents import DocumentParser
    from quantum_gw.utils.text import normalize_for_match, parse_numbers, split_sentences

    settings, extractor, terms = _extractor()
    settings.intake.extract_tables = False            # table rows are figures, not claims
    parser = DocumentParser(settings.intake)
    sentences, seen = [], set()
    for pdf in args.pdf:
        path = Path(pdf)
        chunks = parser.parse(DocumentInput(path=str(path), role=DocumentRole.CLAIM_SOURCE,
                                            source_type=SourceType.INTERNAL))
        for chunk in sorted(chunks, key=lambda c: (c.page or 0, c.block_index or 0)):
            if chunk.is_table:
                continue
            kept = {normalize_for_match(c.text): c.claim_type for c in extractor.run([chunk])}
            refused = {normalize_for_match(s): r for _c, _i, s, r in extractor.rejected_sentences}
            for raw in split_sentences(chunk.text):
                text = " ".join(raw.split())
                norm = normalize_for_match(text)
                if not (args.min_chars <= len(text) <= args.max_chars) or norm in seen:
                    continue
                seen.add(norm)
                sentences.append({
                    "id": _sha(args.company, path.name, norm), "company_id": args.company,
                    "doc": path.name, "page": chunk.page, "year": None, "text": text,
                    "rule_label": int(norm in kept), "rule_claim_type": kept.get(norm),
                    "rule_reason": refused.get(norm, ""),
                    "lexicon_hit": int(any(t and t in norm for t in terms)),
                    "has_figure": int(any(u is not None or not 1900 <= v <= 2100 for v, u in parse_numbers(text))),
                })
    # neighbours in reading order, same page only
    for i, s in enumerate(sentences):
        prev = sentences[i - 1] if i and sentences[i - 1]["page"] == s["page"] else None
        nxt = sentences[i + 1] if i + 1 < len(sentences) and sentences[i + 1]["page"] == s["page"] else None
        s["prev_text"], s["next_text"] = (prev or {}).get("text", ""), (nxt or {}).get("text", "")
        s["stratum"] = "rule_kept" if s["rule_label"] else "env_term_refused" if s["lexicon_hit"] else "other"

    rng = random.Random(args.seed)
    others = [s for s in sentences if s["stratum"] == "other"]
    sample = {id(s) for s in rng.sample(others, round(len(others) * args.random_share))}
    print(f"{len(sentences)} câu trong tài liệu; nhóm 'other' lấy {len(sample)}/{len(others)}")
    return [s for s in sentences if s["stratum"] != "other" or id(s) in sample]


def corpus_neighbours(rows: list[dict]) -> dict[str, tuple[str, str]]:
    """(previous, next) sentence of each corpus sentence, inside its unit of the clean layer."""
    from quantum_gw.utils.text import split_sentences

    docs = {r["doc_id"] for r in rows}
    units = defaultdict(list)
    for line in CLEAN.open(encoding="utf-8"):
        if any(d in line[:600] for d in docs):
            u = json.loads(line)
            if u["doc_id"] in docs:
                units[u["doc_id"]].append(u.get("text") or "")
    out = {}
    for r in rows:
        out[r["id"]] = ("", "")
        for text in units.get(r["doc_id"], []):
            sents = [" ".join(s.split()) for s in split_sentences(text)]
            if r["text"] in sents:
                i = sents.index(r["text"])
                out[r["id"]] = (sents[i - 1] if i else "", sents[i + 1] if i + 1 < len(sents) else "")
                break
    return out


def build_audit(args) -> list[dict]:
    """Sentences the teacher labelled, stratified by the teacher's label (hidden from people)."""
    teacher = [json.loads(line) for line in TEACHER.open(encoding="utf-8")]
    rng = random.Random(args.seed)
    by = defaultdict(list)
    for r in teacher:
        by[r["teacher_label"]].append(r)
    # equal share per teacher class; a class too small to fill its share passes the rest on
    picked, remaining = [], args.n
    order = sorted(by, key=lambda k: len(by[k]))
    for i, label in enumerate(order):
        take = min(len(by[label]), remaining // (len(order) - i))
        picked += rng.sample(by[label], take)
        remaining -= take

    context = corpus_neighbours(picked)
    rows = []
    for r in picked:
        prev, nxt = context[r["id"]]
        rows.append({
            "id": r["id"], "company_id": r["company_id"], "doc": r["doc_id"], "page": r.get("page"),
            "year": r.get("reporting_year"), "text": r["text"], "prev_text": prev, "next_text": nxt,
            "rule_label": r["rule_label"], "rule_claim_type": None, "rule_reason": r.get("rule_reason", ""),
            "lexicon_hit": r["lexicon_hit"], "has_figure": r["has_figure"],
            "stratum": r["teacher_label"], "teacher_label": r["teacher_label"],
            "teacher_model": r.get("teacher_model"), "teacher_prompt": r.get("prompt_version"),
        })
    print(f"{len(rows)} câu từ {len(teacher)} câu thầy đã gán; có ngữ cảnh: {sum(bool(r['prev_text'] or r['next_text']) for r in rows)}")
    return rows


def build(args) -> int:
    rows = build_hpg(args) if args.set == "hpg" else build_audit(args)
    for r in rows:
        r["set"], r["split"], r["lang"] = args.set, SETS[args.set], _lang(r["text"])

    # lot 1 calibrates the codebook: stratified, labelled and discussed before the rest
    rng = random.Random(args.seed)
    by = defaultdict(list)
    for r in rows:
        by[r["stratum"]].append(r)
    lot1 = []
    for _stratum, items in sorted(by.items()):
        lot1 += rng.sample(items, min(len(items), round(args.kappa_size * len(items) / len(rows))))
    first = {r["id"] for r in lot1}
    # the rest dealt round-robin from a stratum-sorted shuffle: every lot is a fair sample
    rest = [r for r in rows if r["id"] not in first]
    rng.shuffle(rest)
    rest.sort(key=lambda r: r["stratum"])
    n_lots = max(1, round(len(rest) / args.lot_size))
    for r in lot1:
        r["lot"] = 1
    for i, r in enumerate(rest):
        r["lot"] = 2 + i % n_lots

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{args.set}_candidates.jsonl"
    rows.sort(key=lambda r: (r["lot"], str(r["company_id"]), r["page"] or 0))
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    held = sorted({json.loads(line)["id"] for f in OUT.glob("*_candidates.jsonl") for line in f.open(encoding="utf-8")})
    (OUT / "exclude_from_training.txt").write_text("\n".join(held) + "\n", encoding="utf-8")
    print(f"{len(rows)} câu ứng viên -> {out.relative_to(ROOT)}")
    print("  nhóm:", dict(Counter(r["stratum"] for r in rows)), "· ngôn ngữ:", dict(Counter(r["lang"] for r in rows)))
    print("  lô:", dict(sorted(Counter(r["lot"] for r in rows).items())))
    print(f"  {len(held)} id không được dùng để huấn luyện -> exclude_from_training.txt")
    return 0


def load_candidates(name: str) -> list[dict]:
    return [json.loads(line) for line in (OUT / f"{name}_candidates.jsonl").open(encoding="utf-8")]


def _source(r: dict) -> str:
    page = f"tr.{r['page']}" if r.get("page") else ""
    if r.get("doc_title"):                      # filled in by _with_sources
        return " · ".join(x for x in (str(r["company_id"]).upper(), r["doc_title"], page) if x)
    if r["set"] == "hpg":
        return f"{str(r['company_id']).upper()} {page}".strip()
    return " ".join(x for x in (str(r["company_id"]).upper(), str(r.get("year") or ""), page) if x)


# ----------------------------------------------------------------------------- where to read the source
ORIGINALS = ROOT / "data/real_cases/sources/originals"
CRAWL_RAW = ROOT / "data/crawl/vn30/contract/raw.jsonl"
CRAWL_OBJECTS = ROOT / "data/crawl/vn30/raw/objects/sha256"
HPG_TITLES = {"HPG_Sustainability_Report_2025.pdf": "Báo cáo phát triển bền vững 2025",
              "HPG_Annual_Report_2024.pdf": "Báo cáo thường niên 2024"}


def _find_page(pdf: Path, text: str) -> int | None:
    """First page whose text layer contains the sentence (probing shorter and shorter
    leading fragments, as storage.documents.highlight_rects does). The crawl's clean
    layer has no page numbers, so this is how a corpus sentence gets one."""
    import fitz

    cleaned = " ".join(text.split())
    probes = [cleaned[:n].strip() for n in (90, 60, 40) if len(cleaned[:n].strip()) >= 20]
    with fitz.open(pdf) as doc:
        for page in doc:
            if any(page.search_for(p) for p in probes):
                return page.number + 1
    return None


def _with_sources(rows: list[dict]) -> list[dict]:
    """Attach to each row the document it came from: title, page, local PDF, link on the web.
    Lookups are cached in training/data/gold_t1/sources.json (finding a page takes a few seconds)."""
    cache_path = OUT / "sources.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    raw, manifest = None, None
    for r in rows:
        if r["id"] not in cache:
            if r["set"] == "hpg":
                if manifest is None:
                    manifest = json.loads((ORIGINALS / "download_manifest.json").read_text(encoding="utf-8"))
                    manifest = manifest if isinstance(manifest, list) else manifest.get("files") or []
                url = next((m.get("final_url") or m.get("url") for m in manifest
                            if str(m.get("path", "")).replace("\\", "/").endswith(r["doc"])), None)
                pdf = ORIGINALS / r["doc"]
                cache[r["id"]] = {"title": HPG_TITLES.get(r["doc"], r["doc"]), "page": r["page"], "url": url,
                                  "pdf": pdf.relative_to(ROOT).as_posix() if pdf.exists() else None}
            else:
                if raw is None:
                    raw = {json.loads(line)["doc_id"]: json.loads(line) for line in CRAWL_RAW.open(encoding="utf-8")}
                u = raw.get(r["doc"], {})
                sha = u.get("sha256") or ""
                hits = sorted(CRAWL_OBJECTS.glob(f"{sha[:2]}/{sha}*")) if sha else []
                pdf = next((h for h in hits if h.suffix.lower() == ".pdf"), None)
                cache[r["id"]] = {"title": (u.get("title") or r["doc"]).splitlines()[0].strip(),
                                  "page": _find_page(pdf, r["text"]) if pdf else None,
                                  "url": u.get("final_url") or u.get("url"),
                                  "pdf": pdf.relative_to(ROOT).as_posix() if pdf else None}
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        s = cache[r["id"]]
        title = "trang web" if s["title"].startswith("http") else s["title"]      # untitled web pages
        r.update(doc_title=title, page=s["page"] or r.get("page"), url=s["url"], pdf=s["pdf"])
    return rows


def _page_image(r: dict, out: Path, longest_side: int = 2000) -> bool:
    """The page as the reader of the report sees it, with the sentence highlighted.

    The sentence is searched in runs of six words, not by its opening words as
    storage.documents.highlight_rects does: extracted sentences often start with
    a heading glued on ('SẢN XUẤT Năm 2025 là…'), which would make the whole
    search fail, and a sentence over several lines is then highlighted entirely."""
    import fitz
    from quantum_gw.storage.documents import highlight_rects

    if not (r.get("pdf") and r.get("page")):
        return False
    pdf = ROOT / r["pdf"]
    words = r["text"].split()
    runs = [" ".join(words[i:i + 6]) for i in range(0, len(words), 6)]
    with fitz.open(pdf) as doc:
        page = doc[r["page"] - 1]
        rects = [rect for run in runs if len(run) >= 12 for rect in page.search_for(run)]
        if not rects:
            rects = [fitz.Rect(*t) for t in highlight_rects(pdf, r["page"], r["text"])]
        for rect in rects:
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=(1, 0.85, 0.2))
            annot.update(opacity=0.5)
        zoom = longest_side / max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        out.write_bytes(pix.tobytes("jpg", jpg_quality=72))
    r["highlighted"] = bool(rects)
    return True


# ----------------------------------------------------------------------------- forms
GREEN = "1F6B3A"
HEAD = ["#", "Nguồn", "Câu trước (chỉ để đọc)", "CÂU CẦN GÁN", "Câu sau (chỉ để đọc)",
        "Nhãn", "Chủ đề (nếu là tuyên bố)", "Nếu NOT_CLAIM: vì sao", "Độ chắc",
        "Phải đọc câu trước/sau?", "Dấu hiệu", "Ghi chú (1 dòng)", "AI hỗ trợ", "id"]


def _styles():
    from openpyxl.styles import Alignment, Font, PatternFill
    return (Alignment(wrap_text=True, vertical="top"), Font(color="7F7F7F", size=9),
            PatternFill("solid", fgColor=GREEN), PatternFill("solid", fgColor="FFF2CC"), Font, PatternFill)


def _lists_sheet(wb):
    lists = wb.create_sheet("DS")
    for col, values in zip("ABCDEF", (LABELS, CLAIM_TYPES, WHY_NOT, CONFIDENCE, FLAGS, YES)):
        for i, v in enumerate(values, 1):
            lists[f"{col}{i}"] = v
    lists.sheet_state = "hidden"
    return {"label": f"=DS!$A$1:$A${len(LABELS)}", "topic": f"=DS!$B$1:$B${len(CLAIM_TYPES)}",
            "why": f"=DS!$C$1:$C${len(WHY_NOT)}", "conf": f"=DS!$D$1:$D${len(CONFIDENCE)}",
            "flag": f"=DS!$E$1:$E${len(FLAGS)}", "yes": "=DS!$F$1:$F$1"}


def _guide_sheet(wb, title: str):
    wrap, _grey, head_fill, _todo, Font, _pf = _styles()
    g = wb.create_sheet("Hướng dẫn", 0)
    g.column_dimensions["A"].width = 18
    g.column_dimensions["B"].width = 36
    g.column_dimensions["C"].width = 90
    g.column_dimensions["D"].width = 16
    g.append([title])
    g["A1"].font = Font(bold=True, size=13, color=GREEN)
    g.append([codebook_version()])
    for k, v in DEFINITIONS:
        g.append([k, v])
        g.merge_cells(start_row=g.max_row, start_column=2, end_row=g.max_row, end_column=3)
        g.cell(g.max_row, 1).font = Font(bold=True)
        g.cell(g.max_row, 2).alignment = wrap
        g.row_dimensions[g.max_row].height = 15 * (len(v) // 115 + 1) + 4
    g.append([])
    g.append(["Mã", "Tình huống", "Quy ước", "Ví dụ"])
    for c in g[g.max_row]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head_fill
    for row in conventions():
        g.append(list(row))
        for c in g[g.max_row]:
            c.alignment = wrap
        g.row_dimensions[g.max_row].height = 15 * (len(row[2]) // 85 + 1) + 4
    return g


def _pack(name: str, lot: int, who: str, items: list[dict], out: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.worksheet.datavalidation import DataValidation

    wrap, grey, head_fill, todo, Font, _pf = _styles()
    wb = Workbook()
    ws = wb.active
    ws.title = "Gán nhãn"
    ws.append(["Người gán", who, "Bộ", name, "Lô", lot, "Bộ quy tắc", codebook_version(),
               "Bắt đầu (giờ)", None, "Kết thúc (giờ)", None])
    ws.append(["Đã trả lời", f'=COUNTA(F4:F{3 + len(items)})&"/{len(items)}"'])
    ws.append(HEAD)
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head_fill
        c.alignment = wrap
    for i, r in enumerate(items, 1):
        ws.append([i, _source(r), r["prev_text"], r["text"], r["next_text"]] + [None] * 8 + [r["id"]])
        row = ws.max_row
        for c in ws[row]:
            c.alignment = wrap
        ws.cell(row, 3).font = grey
        ws.cell(row, 5).font = grey
        ws.cell(row, 4).font = Font(bold=True)
        longest = max(len(r["text"]) / 55, len(r["prev_text"]) / 42, len(r["next_text"]) / 42)
        ws.row_dimensions[row].height = min(170, 15 * (int(longest) + 1) + 4)
    last = ws.max_row
    refs = _lists_sheet(wb)
    for col, key in (("F", "label"), ("G", "topic"), ("H", "why"), ("I", "conf"),
                     ("J", "yes"), ("K", "flag"), ("M", "yes")):
        dv = DataValidation(type="list", formula1=refs[key], allow_blank=True)
        dv.add(f"{col}4:{col}{last}")
        ws.add_data_validation(dv)
    # a required cell left empty turns yellow
    claim = 'OR(LEFT($F4,5)="QUANT",LEFT($F4,5)="QUALI",LEFT($F4,5)="VAGUE")'
    for rng_, formula in ((f"F4:F{last}", '$F4=""'),
                          (f"G4:G{last}", f'AND({claim},$G4="")'),
                          (f"H4:H{last}", 'AND(LEFT($F4,3)="NOT",$H4="")'),
                          (f"I4:I{last}", 'AND($F4<>"",$I4="")'),
                          (f"L4:L{last}", 'AND($L4="",OR(LEFT($F4,6)="UNSURE",LEFT($H4,5)="other",'
                                          '$K4<>"",LEFT($I4,1)="1"))')):
        ws.conditional_formatting.add(rng_, FormulaRule(formula=[formula], fill=todo))
    for col, w in zip("ABCDEFGHIJKLMN", (4, 10, 32, 58, 32, 22, 22, 22, 12, 10, 18, 28, 7, 4)):
        ws.column_dimensions[col].width = w
    ws.column_dimensions["N"].hidden = True
    ws.freeze_panes = "F4"
    _guide_sheet(wb, f"Gán nhãn T1 — bộ {name} — lô {lot} — {len(items)} câu — {who}")
    wb.active = 0
    wb.save(out)


def export(args) -> int:
    rows = load_candidates(args.set)
    lots = [int(x) for x in args.lots.split(",")] if args.lots else sorted({r["lot"] for r in rows})
    if args.overlap == "all":
        plan = [(lot, who) for lot in lots for who in args.labelers]
    else:   # lot 1 for everyone, the others split
        plan = [(1, who) for who in args.labelers if 1 in lots]
        plan += [(lot, args.labelers[i % len(args.labelers)]) for i, lot in enumerate(l for l in lots if l != 1)]
    outdir = OUT / "packs"
    outdir.mkdir(parents=True, exist_ok=True)
    for lot, who in plan:
        items = sorted((r for r in rows if r["lot"] == lot), key=lambda r: (str(r["company_id"]), r["page"] or 0))
        out = outdir / f"T1_{args.set.upper()}_lo{lot:02d}_{who}.xlsx"
        _pack(args.set, lot, who, items, out)
        print(f"bộ {args.set} · lô {lot:>2} · {len(items):>3} câu · {who:<8} -> {out.relative_to(ROOT)}")
    print(codebook_version())
    return 0


# ----------------------------------------------------------------------------- import
def _cols(ws, row: int) -> dict[str, int]:
    return {str(ws.cell(row, c).value or "").strip(): c for c in range(1, ws.max_column + 1)}


YES_WORDS = {"có", "co", "x", "1", "yes", "y", "true"}
_CODES = {"label": {code(v) for v in LABELS}, "topic": {code(v) for v in CLAIM_TYPES},
          "why": {code(v) for v in WHY_NOT}, "flag": {code(v) for v in FLAGS}}


def _answer(sid: str, get, where: str, meta: dict) -> tuple[dict | None, list[str]]:
    """One person's answer for one sentence, from either form, checked the same way.
    `get(key)` returns the raw cell for label/topic/why/conf/flag/note/context/ai."""
    norm = lambda v, f: f(v) if v else v                                          # noqa: E731
    label, topic = norm(code(get("label")), str.upper), norm(code(get("topic")), str.lower)
    why, flag = norm(code(get("why")), str.lower), norm(code(get("flag")), str.upper)
    conf, note = code(get("conf")), str(get("note") or "").strip()
    if label is None:
        return None, [f"{where}: chưa gán nhãn"]
    problems = [f"{where}: {name} lạ {value!r}" for name, value, key in
                (("nhãn", label, "label"), ("chủ đề", topic, "topic"), ("lý do", why, "why"), ("dấu hiệu", flag, "flag"))
                if value is not None and value not in _CODES[key]]
    if problems:
        return None, problems
    if label in CLAIMS and topic is None:
        problems.append(f"{where}: {label} cần chọn chủ đề")
    if label == "NOT_CLAIM" and topic is not None:
        problems.append(f"{where}: NOT_CLAIM không có chủ đề")
    if label == "NOT_CLAIM" and why is None:
        problems.append(f"{where}: NOT_CLAIM cần chọn lý do")
    if label != "NOT_CLAIM" and why is not None:
        problems.append(f"{where}: có lý do NOT_CLAIM nhưng nhãn là {label}")
    if conf not in {"1", "2", "3"}:
        problems.append(f"{where}: độ chắc phải là 1, 2 hoặc 3")
    need = ("UNSURE" if label == "UNSURE" else "lý do other" if why == "other" else flag if flag
            else "độ chắc 1" if conf == "1" else None)
    if need and not note:
        problems.append(f"{where}: {need} cần một dòng ghi chú")
    if len(note) > 300:
        problems.append(f"{where}: ghi chú dài {len(note)} ký tự (tối đa một dòng)")
    yes = lambda v: str(v or "").strip().lower() in YES_WORDS                     # noqa: E731
    return {
        "id": sid, "label": label, "topic": topic, "why_not": why,
        "confidence": int(conf) if conf in {"1", "2", "3"} else None, "flag": flag, "note": note or None,
        "needs_context": yes(get("context")), "ai_assisted": yes(get("ai")),
        "labeler": meta["labeler"], "set": meta["set"], "lot": meta["lot"], "codebook": meta["codebook"],
    }, problems


XLSX_COLS = {"label": "Nhãn", "topic": "Chủ đề (nếu là tuyên bố)", "why": "Nếu NOT_CLAIM: vì sao",
             "conf": "Độ chắc", "flag": "Dấu hiệu", "note": "Ghi chú (1 dòng)",
             "context": "Phải đọc câu trước/sau?", "ai": "AI hỗ trợ"}


def read_pack(xlsx: Path) -> list[tuple[dict, list[dict], list[str]]]:
    from openpyxl import load_workbook

    ws = load_workbook(xlsx, data_only=True)["Gán nhãn"]
    meta = {"labeler": str(ws["B1"].value or "").strip(), "set": ws["D1"].value, "lot": ws["F1"].value,
            "codebook": ws["H1"].value, "file": xlsx.name, "minutes": _minutes(ws["J1"].value, ws["L1"].value)}
    col = _cols(ws, 3)
    labels, problems = [], []
    if not meta["labeler"]:
        problems.append(f"{xlsx.name}: chưa ghi tên người gán (ô B1)")
    for r in range(4, ws.max_row + 1):
        sid = ws.cell(r, col["id"]).value
        if not sid:
            continue
        answer, issues = _answer(sid, lambda k: ws.cell(r, col[XLSX_COLS[k]]).value,
                                 f"{xlsx.name} dòng {r} (#{ws.cell(r, 1).value})", meta)
        problems += issues
        if answer:
            labels.append(answer)
    return [(meta, labels, problems)]


# ----------------------------------------------------------------------------- csv form
# What a person fills comes first on the line, in short codes; what they only read
# (sentence, context) comes after; what the tool needs (id, labeller, codebook) is last.
CSV_HEAD = ["stt", "nhan", "chi_tiet", "chac", "ngu_canh", "ghi_chu", "nguon", "cau",
            "cau_truoc", "cau_sau", "id", "nguoi_gan", "bo_quy_tac"]
NHAN_SHORT = {"1": "QUANTIFIED_CLAIM", "2": "QUALITATIVE_CLAIM", "3": "VAGUE", "0": "NOT_CLAIM", "?": "UNSURE"}
TOPIC_SHORT = {"pt": "emissions_reduction", "nltt": "renewable_energy", "tk": "resource_efficiency",
               "ct": "waste_and_circularity", "tcx": "green_finance", "dd": "biodiversity",
               "qt": "esg_process_integration", "chung": "generic_sustainability"}
WHY_SHORT = {"bang": "table_heading", "cat": "broken", "tck": "other_org", "kt": "general_knowledge",
             "kmt": "non_env", "khac": "other"}
FLAG_IN_NOTE = re.compile(r"\s*(OVERCLAIM|INCONSISTENCY|FUTURE|AI)\s*:", re.IGNORECASE)
ID_PREFIX = "T1-"     # Excel turns a hex id such as 1234567890123456 or 12e4… into a number

LEGEND = """# Cách điền {file}

Mỗi dòng là một câu. Đọc cột `cau` (câu trước / câu sau ở cuối dòng nếu cần ngữ cảnh), rồi điền 4 ô đầu dòng.

| Cột | Gõ | Nghĩa |
|---|---|---|
| `nhan` | `1` | tuyên bố môi trường của DN, **có số liệu** |
| | `2` | tuyên bố môi trường **cụ thể**, không số |
| | `3` | **chung chung**, khẩu hiệu |
| | `0` | **không phải** tuyên bố môi trường của DN |
| | `?` | không chắc (ghi chú vì sao) |
| `chi_tiet` khi nhan là 1, 2, 3: **chủ đề** | `pt` | phát thải, khí nhà kính |
| | `nltt` | năng lượng tái tạo |
| | `tk` | tiết kiệm năng lượng, nước, tài nguyên |
| | `ct` | chất thải, tái chế, tuần hoàn |
| | `tcx` | tín dụng, trái phiếu xanh |
| | `dd` | đa dạng sinh học |
| | `qt` | quy trình ESG của DN |
| | `chung` | chung chung (xanh, bền vững) |
| `chi_tiet` khi nhan là 0: **lý do** (chọn cái đứng trước nếu nhiều cái đúng) | `bang` | tiêu đề, mục lục, dòng bảng |
| | `cat` | câu bị cắt / ghép lỗi, mất nghĩa |
| | `tck` | chủ thể là tổ chức khác (hiệp hội, Chính phủ, ngành, thế giới) |
| | `kt` | kiến thức chung, giải thích kỹ thuật |
| | `kmt` | không liên quan môi trường (xã hội, tài chính, quản trị) |
| | `khac` | khác (ghi chú) |
| `chac` | `3` / `2` / `1` | chắc chắn / khá chắc / phân vân (ghi chú) |
| `ngu_canh` | `x` | phải đọc câu trước/sau mới quyết được |
| `ghi_chu` | một dòng | bắt buộc khi `?`, `khac`, chac `1`; gắn cờ bằng cách mở đầu: `OVERCLAIM:` · `INCONSISTENCY:` · `FUTURE:` · `AI:` (nếu đã dùng AI) |

Ví dụ: `5,2,pt,3,,,…` · `6,0,kt,2,x,,…` · `7,?,,1,,"phân vân 2 hay 3",…`

Quy tắc nhanh (đầy đủ: docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md mục 5):
- Ai đang nói, nói về ai? Hiệp hội, Chính phủ, thế giới → `0` + `tck`.
- Tác dụng chung của công nghệ (EAF, thép phế) → `0` + `kt`; tác dụng của việc DN đang làm → tuyên bố.
- Mục tiêu chỉ có mốc năm (trung hòa carbon 2050) → `2`; có lượng (30% năm 2030) → `1`. Năm, số hiệu ISO, số văn bản không tính là số liệu.
- Không dùng chatbot. Không sửa các cột sau `ghi_chu`.

Lưu: Excel → Save As → **CSV UTF-8 (Comma delimited)**. Nhập: `python training/gold_t1_pack.py import {path}`
"""


def _cell(text: str) -> str:
    # a leading = + - @ makes Excel read the sentence as a formula
    return " " + text if text[:1] in "=+-@" else text


def export_csv(args) -> int:
    import csv

    lots = {int(x) for x in args.lots.split(",")}
    order = {name: i for i, name in enumerate(args.sets)}
    rows = [r for name in args.sets for r in load_candidates(name) if r["lot"] in lots]
    rows.sort(key=lambda r: (r["lot"], order[r["set"]], str(r["company_id"]), r["page"] or 0))
    out = OUT / "packs" / f"T1_{args.labeler}_lo{args.lots.replace(',', '-')}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    book = codebook_version()
    with out.open("w", encoding="utf-8-sig", newline="") as fh:          # BOM: Excel shows Vietnamese right
        w = csv.writer(fh)
        w.writerow(CSV_HEAD)
        for i, r in enumerate(rows, 1):
            w.writerow([i, "", "", "", "", "", _source(r), _cell(r["text"]),
                        _cell(r["prev_text"]), _cell(r["next_text"]), ID_PREFIX + r["id"], args.labeler, book])
    legend = out.with_name("T1_cach_dien.md")
    legend.write_text(LEGEND.format(file=out.name, path=out.relative_to(ROOT).as_posix()), encoding="utf-8")
    print(f"{len(rows)} câu -> {out.relative_to(ROOT)} · {book} · "
          f"{dict(Counter((r['set'], r['lot']) for r in rows))}")
    print(f"  cách điền -> {legend.relative_to(ROOT)}")
    return 0


TOPIC_VI = {"pt": "phát thải, khí nhà kính", "nltt": "năng lượng tái tạo",
            "tk": "tiết kiệm năng lượng, nước, tài nguyên", "ct": "chất thải, tái chế, tuần hoàn",
            "tcx": "tín dụng, trái phiếu xanh", "dd": "đa dạng sinh học", "qt": "quy trình ESG của DN",
            "chung": "chung chung (xanh, bền vững)"}
WHY_VI = {"bang": "tiêu đề, mục lục, dòng bảng", "cat": "câu bị cắt, mất nghĩa",
          "tck": "tổ chức khác (hiệp hội, Chính phủ, ngành)", "kt": "kiến thức chung, giải thích kỹ thuật",
          "kmt": "không liên quan môi trường", "khac": "khác (ghi chú)"}
NHAN_CHOICES = ["1 — tuyên bố có số liệu", "2 — tuyên bố cụ thể, không số", "3 — chung chung, khẩu hiệu",
                "0 — không phải tuyên bố MT của DN", "? — không chắc (ghi chú)"]
DETAIL_CHOICES = ([f"{k} — chủ đề: {v}" for k, v in TOPIC_VI.items()]
                  + [f"{k} — lý do: {v}" for k, v in WHY_VI.items()])
CHAC_CHOICES = ["3 — chắc chắn", "2 — khá chắc", "1 — phân vân (ghi chú)"]
XLSX_HELP = {
    "nhan": "Chọn: 1 có số · 2 cụ thể, không số · 3 chung chung · 0 không phải tuyên bố · ? không chắc",
    "chi_tiet": "Nhãn 1/2/3 → chọn một 'chủ đề'. Nhãn 0 → chọn một 'lý do'. Ô đỏ = chọn nhầm loại.",
    "chac": "3 chắc chắn · 2 khá chắc · 1 phân vân (khi đó phải ghi chú)",
    "ngu_canh": "x nếu phải đọc câu trước/sau mới quyết được",
    "ghi_chu": "Một dòng. Bắt buộc khi ?, 'khac' hoặc chắc 1. Gắn cờ: mở đầu bằng OVERCLAIM: / INCONSISTENCY: / FUTURE: / AI:",
}


def export_xlsx(args) -> int:
    """The CSV form as a workbook, plus where to read the source: every row links to an image
    of its page with the sentence highlighted, and to the document on the web. One zip per
    person holds the workbook, the page images and the HPG report, so it opens anywhere."""
    import zipfile

    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    lots = {int(x) for x in args.lots.split(",")}
    order = {name: i for i, name in enumerate(args.sets)}
    rows = [r for name in args.sets for r in load_candidates(name) if r["lot"] in lots]
    rows = _with_sources(rows)
    rows.sort(key=lambda r: (r["lot"], order[r["set"]], str(r["company_id"]), r["doc_title"], r["page"] or 0))
    tag = f"lo{args.lots.replace(',', '-')}"
    pages_dir = OUT / "packs" / f"trang_{tag}"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for old in pages_dir.glob("*.jpg"):              # numbering follows this export's row order
        old.unlink()
    images = {i: _page_image(r, pages_dir / f"{i:03d}.jpg") for i, r in enumerate(rows, 1)}
    print(f"ảnh trang: {sum(images.values())}/{len(rows)}, có tô câu: {sum(bool(r.get('highlighted')) for r in rows)} "
          f"-> {pages_dir.relative_to(ROOT)}")

    book = codebook_version()
    wrap, top = Alignment(wrap_text=True, vertical="top"), Alignment(vertical="top")
    yellow, red = PatternFill("solid", fgColor="FFF2CC"), PatternFill("solid", fgColor="F8CBAD")
    link_font = Font(color="0563C1", underline="single")
    head = ["stt", "nguon", "cau", "xem", "nhan", "chi_tiet", "chac", "ngu_canh", "ghi_chu",
            "cau_truoc", "cau_sau", "link_goc", "id", "nguoi_gan", "bo_quy_tac"]
    col = {h: i for i, h in enumerate(head, 1)}
    L = {h: chr(64 + i) for h, i in col.items()}                       # column letters (A–O)
    last = len(rows) + 1
    help_ = {**XLSX_HELP, "xem": "Bấm để mở ảnh trang gốc, câu cần gán được tô vàng.",
             "link_goc": "Tài liệu gốc trên web (mở cả báo cáo)."}
    for who in args.labelers:
        wb = Workbook()
        ws = wb.active
        ws.title = "Gán nhãn"
        ws.append(head)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=GREEN)
            c.alignment = Alignment(horizontal="center", vertical="center")
            if c.value in help_:
                c.comment = Comment(help_[c.value], "GreenScan", width=320, height=90)
        for i, r in enumerate(rows, 1):
            ws.append([i, _source(r), r["text"],
                       f"Xem trang {r['page']}" if images[i] else "không thấy trang — dùng link gốc",
                       None, None, None, None, None, r["prev_text"], r["next_text"],
                       "Mở bản gốc" if r.get("url") else "", ID_PREFIX + r["id"], who, book])
            n = ws.max_row
            for c in ws[n]:
                c.alignment = wrap if c.column in (col["nguon"], col["cau"], col["ghi_chu"],
                                                   col["cau_truoc"], col["cau_sau"]) else top
            ws.cell(n, col["cau"]).font = Font(bold=True)
            for h in ("cau_truoc", "cau_sau"):
                ws.cell(n, col[h]).font = Font(color="7F7F7F", size=9)
            if images[i]:
                ws.cell(n, col["xem"]).hyperlink = f"trang_{tag}/{i:03d}.jpg"   # relative to the workbook
                ws.cell(n, col["xem"]).font = link_font
            if r.get("url"):
                ws.cell(n, col["link_goc"]).hyperlink = r["url"]
                ws.cell(n, col["link_goc"]).font = link_font
            ws.row_dimensions[n].height = min(180, 15 * (len(r["text"]) // 58 + 2))

        lists = wb.create_sheet("DS")
        for c_, values in zip("ABCD", (NHAN_CHOICES, DETAIL_CHOICES, CHAC_CHOICES, ["x"])):
            for j, v in enumerate(values, 1):
                lists[f"{c_}{j}"] = v
        lists.sheet_state = "hidden"
        for h, ref in (("nhan", f"$A$1:$A${len(NHAN_CHOICES)}"), ("chi_tiet", f"$B$1:$B${len(DETAIL_CHOICES)}"),
                       ("chac", f"$C$1:$C${len(CHAC_CHOICES)}"), ("ngu_canh", "$D$1:$D$1")):
            dv = DataValidation(type="list", formula1=f"=DS!{ref}", allow_blank=True,
                                showErrorMessage=False)                      # typing the bare code stays allowed
            dv.add(f"{L[h]}2:{L[h]}{last}")
            ws.add_data_validation(dv)
        nh, ct, ch, gc = (f"${L[h]}2" for h in ("nhan", "chi_tiet", "chac", "ghi_chu"))
        claim = f'OR(LEFT({nh},1)="1",LEFT({nh},1)="2",LEFT({nh},1)="3")'
        for h, formula, fill in (
                ("nhan", f'{nh}=""', yellow),
                ("chi_tiet", f'OR(AND(LEFT({nh},1)="0",ISNUMBER(SEARCH("chủ đề",{ct}))),'
                             f'AND({claim},ISNUMBER(SEARCH("lý do",{ct}))))', red),
                ("chi_tiet", f'AND({nh}<>"",LEFT({nh},1)<>"?",{ct}="")', yellow),
                ("chac", f'AND({nh}<>"",{ch}="")', yellow),
                ("ghi_chu", f'AND({gc}="",OR(LEFT({nh},1)="?",LEFT({ch},1)="1",LEFT({ct},4)="khac"))', yellow)):
            ws.conditional_formatting.add(f"{L[h]}2:{L[h]}{last}", FormulaRule(formula=[formula], fill=fill))
        widths = {"stt": 5, "nguon": 18, "cau": 60, "xem": 13, "nhan": 22, "chi_tiet": 28, "chac": 14,
                  "ngu_canh": 9, "ghi_chu": 28, "cau_truoc": 40, "cau_sau": 40, "link_goc": 12}
        for h, w in widths.items():
            ws.column_dimensions[L[h]].width = w
        for h in ("id", "nguoi_gan", "bo_quy_tac"):
            ws.column_dimensions[L[h]].hidden = True
        ws.freeze_panes = f"{L['xem']}2"

        docs = wb.create_sheet("Tài liệu")
        docs.append(["Công ty", "Tài liệu", "Số câu trong lô", "Trang có câu", "Bản gốc trên web",
                     "Trên máy Nhân (repo GreenScan-AI)"])
        for c in docs[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=GREEN)
        grouped = defaultdict(list)
        for r in rows:
            grouped[(str(r["company_id"]).upper(), r["doc_title"], r.get("url"), r.get("pdf"))].append(r)
        for (company, title, url, pdf), rs in sorted(grouped.items()):
            pages = sorted({r["page"] for r in rs if r.get("page")})
            docs.append([company, title, len(rs), ", ".join(map(str, pages)) or "—", "Mở" if url else "—", pdf or "—"])
            if url:
                docs.cell(docs.max_row, 5).hyperlink = url
                docs.cell(docs.max_row, 5).font = link_font
        for c_, w in zip("ABCDEF", (10, 46, 14, 22, 12, 80)):
            docs.column_dimensions[c_].width = w

        g = wb.create_sheet("Cách điền", 0)
        g.column_dimensions["A"].width = 16
        g.column_dimensions["B"].width = 100
        g.append([f"Gán nhãn T1 — {who} — lô {args.lots} — {len(rows)} câu — {book}"])
        g["A1"].font = Font(bold=True, size=13, color=GREEN)
        g.append(["Đã gán", f"=COUNTA('Gán nhãn'!{L['nhan']}2:{L['nhan']}{last})&\" / {len(rows)} câu\""])
        g.append([])
        guide = [
            ("Cách làm", "Sang sheet 'Gán nhãn'. Mỗi dòng: đọc CÂU (cột cau, in đậm), rồi chọn 4 ô nhan, chi_tiet, chac, ngu_canh. "
                         "Ô vàng là ô còn thiếu, ô đỏ là chọn nhầm."),
            ("Đọc ở đâu", f"Câu nằm trong báo cáo ghi ở cột nguon (công ty · tên báo cáo · trang). Cột xem mở ẢNH TRANG GỐC, câu được "
                          f"tô vàng: thấy được câu nằm trong đoạn văn, bảng hay tiêu đề. Cột link_goc mở cả báo cáo trên web. "
                          f"Câu trước / câu sau (cột xám) là đoạn liền kề. Sheet 'Tài liệu' liệt kê mọi báo cáo của lô. "
                          f"Giữ thư mục trang_{tag} cạnh file Excel thì link mới mở được."),
            ("Khi nào mở trang", "Khi câu thiếu chủ ngữ ('Đây là', 'Biện pháp này'), khi nghi là ô bảng / tiêu đề, hoặc khi không rõ "
                                 "ai đang nói. Nếu phải mở mới quyết được thì chọn x ở ngu_canh."),
            ("nhan", "1 = tuyên bố môi trường của DN có số liệu · 2 = tuyên bố cụ thể, không số · 3 = chung chung, khẩu hiệu · "
                     "0 = không phải tuyên bố MT của DN · ? = không chắc (ghi chú vì sao)"),
            ("chi_tiet", "Nhãn 1/2/3: chủ đề — pt phát thải · nltt năng lượng tái tạo · tk tiết kiệm · ct chất thải · tcx tài chính xanh · "
                         "dd đa dạng sinh học · qt quy trình ESG · chung chung chung.  Nhãn 0: lý do — bang tiêu đề/bảng · cat câu cắt · "
                         "tck tổ chức khác · kt kiến thức chung · kmt không liên quan MT · khac khác (chọn lý do đứng trước nếu nhiều cái đúng)."),
            ("chac", "3 chắc chắn · 2 khá chắc · 1 phân vân (phải ghi chú)"),
            ("ngu_canh", "x nếu phải đọc câu trước / câu sau hoặc mở trang mới quyết được"),
            ("ghi_chu", "Một dòng. Bắt buộc khi ?, 'khac', chắc 1. Gắn cờ bằng chữ mở đầu: OVERCLAIM: (nói mạnh hơn số liệu) · "
                        "INCONSISTENCY: (mâu thuẫn chỗ khác) · FUTURE: (lợi ích tương lai) · AI: (nếu đã dùng AI cho câu này)"),
            ("Quy tắc nhanh", "Ai đang nói, nói về ai? Hiệp hội, Chính phủ, thế giới → 0 + tck.  Tác dụng chung của công nghệ → 0 + kt; "
                              "tác dụng của việc DN đang làm → tuyên bố.  Mục tiêu chỉ có năm (trung hòa carbon 2050) → 2; có lượng "
                              "(30% năm 2030) → 1.  Năm, số hiệu ISO, số văn bản không tính là số liệu."),
            ("Không", "Không dùng chatbot để ra nhãn. Không bàn với người khác trước khi nộp. Không sửa các cột ẩn."),
            ("Xong", "Lưu file (giữ định dạng .xlsx) và gửi lại. Nhập: python training/gold_t1_pack.py import <file>"),
            ("Đầy đủ", "docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md, mục 5"),
        ]
        for k, v in guide:
            g.append([k, v])
            g.cell(g.max_row, 1).font = Font(bold=True)
            g.cell(g.max_row, 2).alignment = wrap
            g.row_dimensions[g.max_row].height = 15 * (len(v) // 95 + 1) + 4
        wb.active = 1
        out = OUT / "packs" / f"T1_{who}_{tag}.xlsx"
        try:
            wb.save(out)
        except PermissionError:                      # the old copy is open in Excel, which locks it
            out = out.with_name(f"T1_{who}_{tag}_moi.xlsx")
            wb.save(out)
            print(f"  ! T1_{who}_{tag}.xlsx đang mở trong Excel — bản mới lưu thành {out.name}")

        # what to send: the workbook and its page images (whole reports stay behind link_goc)
        bundle = out.with_suffix(".zip")
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(out, out.name)
            for img in sorted(pages_dir.glob("*.jpg")):
                z.write(img, f"{pages_dir.name}/{img.name}")
        print(f"{len(rows)} câu -> {out.relative_to(ROOT)} · gửi: {bundle.relative_to(ROOT)} "
              f"({bundle.stat().st_size / 1e6:.1f} MB) · {book}")
    return 0


def _csv_get(r: dict):
    """Translate the short codes of the CSV/Excel form into the stored codes. A cell may hold
    the bare code ('2', 'pt') or a dropdown entry ('2 — tuyên bố cụ thể…', 'pt — chủ đề: …')."""
    raw_label = code(r.get("nhan")) or ""
    label = NHAN_SHORT.get(raw_label, raw_label)
    detail = (code(r.get("chi_tiet")) or "").lower()
    topic = TOPIC_SHORT.get(detail, detail if detail in _CODES["topic"] else None)
    why = WHY_SHORT.get(detail, detail if detail in _CODES["why"] else None)
    if detail and topic is None and why is None:      # unknown code: report it where it was expected
        topic, why = (detail, None) if code(label) != "NOT_CLAIM" else (None, detail)
    note = (r.get("ghi_chu") or "").strip()
    tag = FLAG_IN_NOTE.match(note)
    tag = tag.group(1).upper() if tag else None
    values = {"label": label, "topic": topic, "why": why, "conf": code(r.get("chac")) or "",
              "flag": tag if tag in ("OVERCLAIM", "INCONSISTENCY", "FUTURE") else None, "note": note,
              "context": r.get("ngu_canh"), "ai": "x" if tag == "AI" else ""}
    return values.get


def read_csv(path: Path) -> list[tuple[dict, list[dict], list[str]]]:
    """A filled CSV may hold several lots; a lot is submitted only when every sentence in it is answered."""
    import csv

    try:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            # Excel saves with the locale's list separator; the header has no quotes, so count there.
            # (csv.Sniffer guesses quoting from a sample and misreads sentences that contain "".)
            header = fh.readline()
            delimiter = max(",;\t", key=header.count)
            fh.seek(0)
            rows = list(csv.DictReader(fh, delimiter=delimiter))
    except UnicodeDecodeError:
        return [({"file": path.name}, [], [f"{path.name}: không đọc được UTF-8 — trong Excel chọn "
                                           "Save As → 'CSV UTF-8 (Comma delimited)'"])]
    return _short_rows(rows, path)


def read_short_xlsx(path: Path) -> list[tuple[dict, list[dict], list[str]]]:
    """The Excel twin of the CSV form (export-xlsx): same columns, header in row 1."""
    from openpyxl import load_workbook

    ws = load_workbook(path, data_only=True)["Gán nhãn"]
    head = [str(c.value or "").strip() for c in ws[1]]

    def text(v) -> str:
        if isinstance(v, float) and v.is_integer():
            v = int(v)                                   # a typed 2 comes back as 2 or 2.0, and 0 is falsy
        return "" if v is None else str(v).strip()

    rows = [{h: text(v) for h, v in zip(head, values) if h}
            for values in ws.iter_rows(min_row=2, values_only=True) if any(v is not None for v in values)]
    return _short_rows(rows, path)


def _is_short_xlsx(path: Path) -> bool:
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True)
    ok = "Gán nhãn" in wb.sheetnames and str(wb["Gán nhãn"]["A1"].value or "").strip() == "stt"
    wb.close()
    return ok


def _short_rows(rows: list[dict], path: Path) -> list[tuple[dict, list[dict], list[str]]]:
    missing = [h for h in ("nhan", "chi_tiet", "chac", "ghi_chu", "id", "nguoi_gan") if h not in (rows[0] if rows else {})]
    if missing:
        return [({"file": path.name}, [], [f"{path.name}: thiếu cột {missing}"])]
    where_is = {r["id"]: (r["set"], r["lot"]) for name in SETS if (OUT / f"{name}_candidates.jsonl").exists()
                for r in load_candidates(name)}
    groups, problems_file = defaultdict(list), []
    for i, r in enumerate(rows, 2):
        sid = (r.get("id") or "").strip().removeprefix(ID_PREFIX)
        if sid not in where_is:
            problems_file.append(f"{path.name} dòng {i}: id {sid!r} không có trong bộ nào (đừng sửa cột id)")
            continue
        groups[where_is[sid]].append((i, sid, r))
    results = [({"file": path.name}, [], problems_file)] if problems_file else []
    for (name, lot), items in sorted(groups.items()):
        answered = [(i, sid, r) for i, sid, r in items if (r.get("nhan") or "").strip()]
        if not answered:
            continue
        who = {(r.get("nguoi_gan") or "").strip() for _i, _s, r in items}
        meta = {"labeler": who.pop() if len(who) == 1 else "", "set": name, "lot": lot, "file": path.name,
                "codebook": (items[0][2].get("bo_quy_tac") or "").strip(), "minutes": None}
        labels, problems = [], []
        if not meta["labeler"]:
            problems.append(f"{path.name} bộ {name} lô {lot}: cột nguoi_gan trống hoặc không thống nhất")
        for i, sid, r in answered:
            answer, issues = _answer(sid, _csv_get(r), f"{path.name} dòng {i} (stt {r.get('stt')})", meta)
            problems += issues
            if answer:
                labels.append(answer)
        if len(answered) < len(items):
            problems.insert(0, f"{path.name} bộ {name} lô {lot}: mới gán {len(answered)}/{len(items)} câu — "
                               "lô chỉ được nhập khi gán đủ")
        results.append((meta, labels, problems))
    if not results:
        results.append(({"file": path.name}, [], [f"{path.name}: chưa có câu nào được gán"]))
    return results


def import_(args) -> int:
    status = 0
    for f in args.files:
        path = Path(f)
        reader = read_csv if path.suffix.lower() == ".csv" else read_short_xlsx if _is_short_xlsx(path) else read_pack
        for meta, labels, problems in reader(path):
            where = f"{path.name}" + (f" · bộ {meta['set']} lô {meta['lot']}" if "lot" in meta else "")
            for p in problems:
                print("  !", p)
            if problems and not args.force:
                print(f"{where}: {len(problems)} lỗi, chưa nhập (sửa file hoặc --force)")
                status = 1
                continue
            if not labels:
                continue
            stamp = dt.datetime.now().isoformat(timespec="seconds")
            out = OUT / "labels" / f"{meta['set']}_lo{int(meta['lot']):02d}_{meta['labeler']}.jsonl"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("".join(json.dumps({**x, "minutes_lot": meta["minutes"], "imported_at": stamp},
                                              ensure_ascii=False) + "\n" for x in labels), encoding="utf-8")
            print(f"{where}: {len(labels)} nhãn -> {out.relative_to(ROOT)} · {dict(Counter(x['label'] for x in labels))}")
    return status


def first_pass(name: str) -> dict[str, list[dict]]:
    by_id: dict[str, list[dict]] = defaultdict(list)
    for f in sorted((OUT / "labels").glob(f"{name}_lo*.jsonl")):
        for line in f.open(encoding="utf-8"):
            x = json.loads(line)
            by_id[x["id"]].append(x)
    return by_id


def agreed(name: str) -> dict[str, dict]:
    f = OUT / "labels" / f"{name}_consensus.jsonl"
    return {json.loads(line)["id"]: json.loads(line) for line in f.open(encoding="utf-8")} if f.exists() else {}


# ----------------------------------------------------------------------------- consensus
DISAGREEMENT = ["AI hỗ trợ", "tuyên bố / không", "UNSURE", "loại tuyên bố", "chủ đề", "lý do NOT_CLAIM", "độ chắc thấp"]


def disagreement(xs: list[dict]) -> list[str]:
    labels = [x["label"] for x in xs]
    sure = [x for x in xs if x["label"] != "UNSURE"]
    found = []
    if any(x["ai_assisted"] for x in xs):
        found.append("AI hỗ trợ")
    if len({x["label"] in CLAIMS for x in sure}) > 1:
        found.append("tuyên bố / không")
    if "UNSURE" in labels:
        found.append("UNSURE")
    if sure and all(x["label"] in CLAIMS for x in sure) and len({x["label"] for x in sure}) > 1:
        found.append("loại tuyên bố")
    if sure and all(x["label"] in CLAIMS for x in sure) and len({x["topic"] for x in sure}) > 1:
        found.append("chủ đề")
    if sure and all(x["label"] == "NOT_CLAIM" for x in sure) and len({x["why_not"] for x in sure}) > 1:
        found.append("lý do NOT_CLAIM")
    if any(x.get("confidence") == 1 for x in xs):
        found.append("độ chắc thấp")
    return found


def _say(x: dict) -> str:
    detail = x["topic"] if x["label"] in CLAIMS else x["why_not"] or ""
    bits = [x["label"], detail, f"chắc {x['confidence']}" if x.get("confidence") else "",
            "cần ngữ cảnh" if x["needs_context"] else "", "AI" if x["ai_assisted"] else "", x["note"] or ""]
    return " · ".join(b for b in bits if b)


def consensus(args) -> int:
    from openpyxl import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation

    rows = {r["id"]: r for r in load_candidates(args.set)}
    by_id, done = first_pass(args.set), agreed(args.set)
    lots = {int(x) for x in args.lots.split(",")} if args.lots else None
    who = sorted({x["labeler"] for xs in by_id.values() for x in xs})
    todo = []
    for sid, xs in by_id.items():
        if sid in done or len(xs) < 2 or (lots and rows[sid]["lot"] not in lots):
            continue
        kinds = disagreement(xs)
        if kinds:
            todo.append((DISAGREEMENT.index(kinds[0]), rows[sid]["lot"], rows[sid].get("page") or 0, sid, kinds, xs))
    todo.sort()

    wrap, grey, head_fill, _todo_fill, Font, _pf = _styles()
    wb = Workbook()
    ws = wb.active
    ws.title = "Họp thống nhất"
    pairs = _pairs(by_id)
    k = " · ".join(f"{a}–{b}: κ tuyên bố/không {_kappa(_claim_pairs(v))}"
                   f", κ 5 nhãn {_kappa(v)} (n={len(v)})" for (a, b), v in pairs.items())
    ws.append([f"Họp thống nhất — bộ {args.set} — {dt.date.today():%d/%m/%Y} — {len(todo)} câu cần quyết", None])
    ws["A1"].font = Font(bold=True, size=13, color=GREEN)
    ws.append([k or "chưa có hai người cùng gán một câu"])
    head = (["#", "Loại bất đồng", "Nguồn", "Câu trước", "CÂU", "Câu sau"] + [f"{w} đã chọn" for w in who]
            + ["Nhãn thống nhất", "Chủ đề thống nhất", "Lý do NOT_CLAIM thống nhất", "Vì sao (1 dòng)",
               "Quy ước mới (mã)", "id"])
    ws.append(head)
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head_fill
        c.alignment = wrap
    base = 7 + len(who)
    for i, (_p, _lot, _page, sid, kinds, xs) in enumerate(todo, 1):
        r = rows[sid]
        said = {x["labeler"]: _say(x) for x in xs}
        same = len({x["label"] for x in xs}) == 1 and "UNSURE" not in {x["label"] for x in xs}
        ws.append([i, " + ".join(kinds), _source(r), r["prev_text"], r["text"], r["next_text"]]
                  + [said.get(w, "—") for w in who]
                  + [next(v for v in LABELS if code(v) == xs[0]["label"]) if same else None,
                     None, None, None, None, sid])
        row = ws.max_row
        for c in ws[row]:
            c.alignment = wrap
        ws.cell(row, 4).font = grey
        ws.cell(row, 6).font = grey
        ws.cell(row, 5).font = Font(bold=True)
        ws.row_dimensions[row].height = min(200, 15 * (int(max(len(r["text"]) / 50, 2)) + 1))
    refs = _lists_sheet(wb)
    last = max(ws.max_row, 4)
    for offset, key in ((0, "label"), (1, "topic"), (2, "why")):
        letter = ws.cell(3, base + offset).column_letter
        dv = DataValidation(type="list", formula1=refs[key], allow_blank=True)
        dv.add(f"{letter}4:{letter}{last}")
        ws.add_data_validation(dv)
    widths = [4, 18, 10, 26, 50, 26] + [30] * len(who) + [22, 22, 22, 34, 10, 4]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(3, j).column_letter].width = w
    ws.column_dimensions[ws.cell(3, len(head)).column_letter].hidden = True
    ws.freeze_panes = ws.cell(4, base)

    q = wb.create_sheet("Sổ quy ước")
    q.append(["Mã", "Tình huống", "Quy ước", "Ví dụ (# dòng)", "Trạng thái"])
    for c in q[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head_fill
    existing = conventions()
    for row in existing:
        q.append(list(row) + ["đang dùng"])
    for n in range(len(existing) + 1, len(existing) + 11):
        q.append([f"Q{n}", None, None, None, "mới"])
    for row in q.iter_rows(min_row=2):
        for c in row:
            c.alignment = wrap
    for col, w in zip("ABCDE", (6, 30, 80, 16, 10)):
        q.column_dimensions[col].width = w

    h = wb.create_sheet("Cách họp")
    steps = [
        "1. Chỉ các câu có bất đồng (hoặc UNSURE, độ chắc 1, AI hỗ trợ) được đưa ra. Câu mọi người đã cùng nhãn không phải bàn.",
        "2. Mỗi câu: từng người nói lý do của mình trong 30 giây, dựa trên định nghĩa và quy ước (sheet 'Sổ quy ước').",
        "3. Chọn 'Nhãn thống nhất' (và chủ đề hoặc lý do), ghi 'Vì sao' một dòng. Không biểu quyết khi chưa hiểu lý do của nhau.",
        "4. Nếu bất đồng đến từ chỗ quy ước chưa nói: viết quy ước mới ở 'Sổ quy ước' (mã Q tiếp theo) và ghi mã đó ở cột 'Quy ước mới'. Quy ước mới tự vào các gói sau.",
        "5. Không thống nhất được: chọn UNSURE và ghi vì sao. Câu đó ra khỏi gold, không phải là lỗi.",
        "6. Họp xong: Nhân chạy import-consensus. Bất đồng giảm qua các lô là bằng chứng quy ước đang tốt lên.",
    ]
    h.column_dimensions["A"].width = 130
    for s in steps:
        h.append([s])
        h.cell(h.max_row, 1).alignment = wrap
    wb.active = 0
    out = OUT / "packs" / f"T1_{args.set.upper()}_HOP_THONG_NHAT_{dt.date.today():%Y-%m-%d}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"{len(todo)} câu cần thống nhất ({dict(Counter(t[4][0] for t in todo))}) -> {out.relative_to(ROOT)}")
    print(" ", k)
    return 0


def import_consensus(args) -> int:
    from openpyxl import load_workbook

    wb = load_workbook(args.file, data_only=True)
    ws = wb["Họp thống nhất"]
    name = re.search(r"bộ (\w+)", str(ws["A1"].value)).group(1)
    col = _cols(ws, 3)
    decided, problems, skipped = [], [], 0
    codes = {c[0] for c in conventions()}
    q = wb["Sổ quy ước"]
    new = []
    for row in q.iter_rows(min_row=2, values_only=True):
        c, situation, rule, example, _state = (list(row) + [None] * 5)[:5]
        if c and rule and c not in codes:
            new.append({"code": c, "situation": situation or "", "rule": rule, "example": example or "",
                        "set": name, "date": dt.date.today().isoformat()})
    codes |= {n["code"] for n in new}
    for r in range(4, ws.max_row + 1):
        sid = ws.cell(r, col["id"]).value
        if not sid:
            continue
        label = code(ws.cell(r, col["Nhãn thống nhất"]).value)
        topic = code(ws.cell(r, col["Chủ đề thống nhất"]).value)
        why = code(ws.cell(r, col["Lý do NOT_CLAIM thống nhất"]).value)
        because = str(ws.cell(r, col["Vì sao (1 dòng)"]).value or "").strip()
        rule = ws.cell(r, col["Quy ước mới (mã)"]).value
        where = f"dòng {r} (#{ws.cell(r, 1).value})"
        if label is None:
            skipped += 1
            continue
        if label in CLAIMS and topic is None:
            problems.append(f"{where}: {label} cần chủ đề thống nhất")
        if label == "NOT_CLAIM" and why is None:
            problems.append(f"{where}: NOT_CLAIM cần lý do thống nhất")
        if not because:
            problems.append(f"{where}: thiếu 'Vì sao'")
        if rule and rule not in codes:
            problems.append(f"{where}: quy ước {rule} chưa có trong 'Sổ quy ước'")
        decided.append({"id": sid, "label": label, "topic": topic if label in CLAIMS else None,
                        "why_not": why if label == "NOT_CLAIM" else None, "note": because or None,
                        "convention": rule, "kinds": str(ws.cell(r, col["Loại bất đồng"]).value or "").split(" + "),
                        "set": name, "decided_at": dt.date.today().isoformat()})
    for p in problems:
        print("  !", p)
    if problems and not args.force:
        print(f"{len(problems)} lỗi, chưa nhập")
        return 1
    current = agreed(name)
    current.update({d["id"]: d for d in decided})
    out = OUT / "labels" / f"{name}_consensus.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in current.values()), encoding="utf-8")
    if new:
        with (OUT / "conventions.jsonl").open("a", encoding="utf-8") as fh:
            for n in new:
                fh.write(json.dumps(n, ensure_ascii=False) + "\n")
    print(f"{len(decided)} câu đã thống nhất -> {out.relative_to(ROOT)} · {skipped} câu chưa quyết · "
          f"{len(new)} quy ước mới → {codebook_version()}")
    return 0


# ----------------------------------------------------------------------------- merge
def merge(args) -> int:
    rows = load_candidates(args.set)
    by_id, done = first_pass(args.set), agreed(args.set)
    gold, held = [], Counter()
    for r in rows:
        sid, xs = r["id"], by_id.get(r["id"], [])
        topic = None
        if sid in done:
            pick, source = done[sid], "consensus"
            topic = pick["topic"]
        elif not xs:
            held["chưa gán"] += 1
            continue
        elif disagreement(xs) and len(xs) > 1 and not set(disagreement(xs)) <= {"chủ đề", "lý do NOT_CLAIM", "độ chắc thấp"}:
            held["chờ họp thống nhất"] += 1
            continue
        else:
            pick, source = xs[0], "single" if len(xs) == 1 else "agree"
            topics = {x["topic"] for x in xs}
            topic = topics.pop() if len(topics) == 1 else None
            if xs[0]["ai_assisted"]:
                held["AI hỗ trợ, chờ họp"] += 1
                continue
        if pick["label"] == "UNSURE":
            held["UNSURE sau họp"] += 1
            continue
        gold.append({
            "id": sid, "set": args.set, "company_id": r["company_id"], "split": r["split"], "lang": r["lang"],
            "doc": r["doc"], "page": r["page"], "text": r["text"],
            "prev_text": r["prev_text"], "next_text": r["next_text"],
            "gold_label": pick["label"], "is_claim": pick["label"] in CLAIMS, "topic": topic,
            "why_not": pick.get("why_not") if pick["label"] == "NOT_CLAIM" else None,
            "needs_context": any(x["needs_context"] for x in xs),
            "flags": sorted({x["flag"] for x in xs if x["flag"]}),
            "confidence_min": min((x["confidence"] for x in xs if x.get("confidence")), default=None),
            "source": source, "labelers": sorted({x["labeler"] for x in xs}), "lot": r["lot"],
            "rule_label": r["rule_label"], "rule_claim_type": r.get("rule_claim_type"),
            "lexicon_hit": r["lexicon_hit"], "has_figure": r["has_figure"], "year": r.get("year"),
            "stratum": r["stratum"], "teacher_label": r.get("teacher_label"),
        })
    out = OUT / f"{args.set}_gold.jsonl"
    out.write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in gold), encoding="utf-8")
    print(f"gold {len(gold)}/{len(rows)} -> {out.relative_to(ROOT)}")
    print("  nhãn:", dict(Counter(g["gold_label"] for g in gold)), "· nguồn:", dict(Counter(g["source"] for g in gold)))
    print("  chưa vào gold:", dict(held))
    return 0


# ----------------------------------------------------------------------------- report
def _kappa(pairs) -> float | None:
    pairs = list(pairs)
    if not pairs:
        return None
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else round((po - pe) / (1 - pe), 3)


def _claim_pairs(pairs) -> list[tuple[bool, bool]]:
    """claim / not-claim on the pairs where neither person said UNSURE"""
    return [(x in CLAIMS, y in CLAIMS) for x, y in pairs if "UNSURE" not in (x, y)]


def _fleiss(items: list[list[str]]) -> float | None:
    items = [i for i in items if len(i) >= 2 and len(i) == len(items[0])]
    if not items or len(items[0]) < 3:
        return None
    n, cats = len(items[0]), sorted({c for i in items for c in i})
    p_i = [(sum(c * c for c in Counter(i).values()) - n) / (n * (n - 1)) for i in items]
    p_j = [sum(Counter(i)[c] for i in items) / (len(items) * n) for c in cats]
    pe = sum(p * p for p in p_j)
    return 1.0 if pe == 1 else round((sum(p_i) / len(items) - pe) / (1 - pe), 3)


def _boot(pairs, stat, n=1000, seed=13):
    pairs = list(pairs)
    if len(pairs) < 10:
        return None
    rng = random.Random(seed)
    vals = sorted(v for v in (stat([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(n)) if v is not None)
    return (round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)) if vals else None


def _pairs(by_id) -> dict[tuple[str, str], list[tuple[str, str]]]:
    out = defaultdict(list)
    for xs in by_id.values():
        first = {}
        for x in xs:
            first.setdefault(x["labeler"], x)
        for a, b in combinations(sorted(first), 2):
            out[(a, b)].append((first[a]["label"], first[b]["label"]))
    return out


def _prf(pairs, positive) -> dict:
    tp = sum(1 for t, p in pairs if t == positive and p == positive)
    fp = sum(1 for t, p in pairs if t != positive and p == positive)
    fn = sum(1 for t, p in pairs if t == positive and p != positive)
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else 0.0 if prec is not None and rec is not None else None
    return {"precision": _r(prec), "recall": _r(rec), "f1": _r(f1), "support": tp + fn}


def _r(x):
    return None if x is None else round(x, 3)


def _macro_f1(pairs) -> float | None:
    classes = sorted({t for t, _ in pairs})
    f = [_prf(pairs, c)["f1"] or 0.0 for c in classes]
    return round(sum(f) / len(f), 3) if f else None


def report(args) -> int:
    import yaml

    gates = yaml.safe_load(DECISIONS.read_text(encoding="utf-8"))["gates"]
    rows = load_candidates(args.set)
    by_id, done = first_pass(args.set), agreed(args.set)
    gold_path = OUT / f"{args.set}_gold.jsonl"
    gold = [json.loads(line) for line in gold_path.open(encoding="utf-8")] if gold_path.exists() else []
    labels = [x for xs in by_id.values() for x in xs]
    who = sorted({x["labeler"] for x in labels})
    rep: dict = {"set": args.set, "split": SETS[args.set], "generated": dt.datetime.now().isoformat(timespec="seconds"),
                 "codebook": codebook_version(), "candidates": len(rows), "labelers": who,
                 "labels": len(labels), "gold": len(gold)}

    # agreement, first pass only (before any meeting)
    agreement = {}
    for (a, b), v in _pairs(by_id).items():
        binary = _claim_pairs(v)
        agreement[f"{a}–{b}"] = {
            "n": len(v), "observed": _r(sum(x == y for x, y in v) / len(v)),
            "kappa_5": _kappa(v), "kappa_5_ci": _boot(v, _kappa),
            "kappa_claim": _kappa(binary), "kappa_claim_ci": _boot(binary, _kappa),
            "specific_agreement": {c: _r(2 * sum(x == y == c for x, y in v)
                                         / max(1, sum(x == c for x, _ in v) + sum(y == c for _, y in v)))
                                   for c in [code(l) for l in LABELS]},
        }
    rep["agreement"] = agreement
    multi = [[x["label"] for x in xs] for xs in by_id.values() if len({x["labeler"] for x in xs}) == len(who)]
    rep["fleiss_kappa_5"] = _fleiss(multi) if len(who) >= 3 else None
    kinds = Counter(k for xs in by_id.values() if len(xs) > 1 for k in disagreement(xs)[:1])
    rep["disagreements_first_pass"] = dict(kinds)
    rep["consensus"] = {"decided": len(done), "conventions_added": len(conventions()) - len(BASE_CONVENTIONS),
                        "by_kind": dict(Counter(k for d in done.values() for k in d.get("kinds", [])[:1]))}
    rep["gold_distribution"] = {
        "label": dict(Counter(g["gold_label"] for g in gold)), "topic": dict(Counter(g["topic"] for g in gold if g["topic"])),
        "why_not": dict(Counter(g["why_not"] for g in gold if g["why_not"])), "lang": dict(Counter(g["lang"] for g in gold)),
        "source": dict(Counter(g["source"] for g in gold)), "needs_context": sum(g["needs_context"] for g in gold),
        "flags": dict(Counter(f for g in gold for f in g["flags"])), "companies": len({g["company_id"] for g in gold}),
    }
    effort = defaultdict(lambda: [0.0, 0])
    for f in (OUT / "labels").glob(f"{args.set}_lo*.jsonl"):
        xs = [json.loads(line) for line in f.open(encoding="utf-8")]
        if xs and xs[0].get("minutes_lot"):
            effort[xs[0]["labeler"]][0] += xs[0]["minutes_lot"]
            effort[xs[0]["labeler"]][1] += len(xs)
    rep["seconds_per_sentence"] = {w: round(60 * m / n, 1) for w, (m, n) in effort.items() if n}

    if gold:
        truth_claim = [(g["is_claim"], bool(g["rule_label"])) for g in gold]
        rep["rules_vs_gold"] = {**_prf(truth_claim, True), "f1_ci": _boot(truth_claim, lambda p: _prf(p, True)["f1"])}
        typed = [(g["topic"], g["rule_claim_type"]) for g in gold if g["is_claim"] and g["topic"] and g["rule_claim_type"]]
        rep["product_claim_type_accuracy"] = {"n": len(typed), "accuracy": _r(sum(a == b for a, b in typed) / len(typed)) if typed else None}
        if args.set == "audit":
            tv = [(g["gold_label"], g["teacher_label"]) for g in gold if g.get("teacher_label")]
            tb = [(t in CLAIMS, p in CLAIMS) for t, p in tv]
            rep["teacher_vs_gold"] = {
                "n": len(tv), "accuracy": _r(sum(a == b for a, b in tv) / len(tv)) if tv else None,
                "accuracy_ci": _boot(tv, lambda p: sum(a == b for a, b in p) / len(p)),
                "macro_f1": _macro_f1(tv), "macro_f1_ci": _boot(tv, _macro_f1),
                "per_class": {c: _prf(tv, c) for c in sorted(CLAIMS | {"NOT_CLAIM"})},
                "claim_vs_not": _prf(tb, True),
                "confusion": {f"{t}→{p}": n for (t, p), n in sorted(Counter(tv).items())},
            }
    # Claude as a fourth labeller (training/claude_labels.py): measured, never part of gold
    ai_file = OUT / "ai" / "claude_compare.jsonl"
    if ai_file.exists():
        ai = {x["id"]: x for x in map(json.loads, ai_file.open(encoding="utf-8")) if x["set"] == f"compare_{args.set}"}
        cv = [(g_["gold_label"], ai[g_["id"]]["label"]) for g_ in gold if g_["id"] in ai]
        sure = [(t, p) for t, p in cv if p != "UNSURE"]
        per_person = {}
        for w in who:
            mine = {x["id"]: x["label"] for xs in by_id.values() for x in xs if x["labeler"] == w}
            pp = [(mine[i], ai[i]["label"]) for i in mine if i in ai]
            per_person[w] = {"n": len(pp), "kappa_5": _kappa(pp),
                             "kappa_claim": _kappa(_claim_pairs(pp))}
        rep["claude_vs_gold"] = {
            "n_labelled": len(ai), "n_with_gold": len(cv), "unsure": len(cv) - len(sure),
            "accuracy": _r(sum(a == b for a, b in sure) / len(sure)) if sure else None,
            "accuracy_ci": _boot(sure, lambda p: sum(a == b for a, b in p) / len(p)),
            "macro_f1": _macro_f1(sure), "macro_f1_ci": _boot(sure, _macro_f1), "kappa_5": _kappa(sure),
            "claim_vs_not": _prf([(t in CLAIMS, p in CLAIMS) for t, p in sure], True),
            "per_class": {c: _prf(sure, c) for c in sorted(CLAIMS | {"NOT_CLAIM"})},
            "confusion": {f"{t}→{p}": n for (t, p), n in sorted(Counter(sure).items()) if t != p},
            "kappa_with_each_person": per_person,
        }
    k_ok = all((v["kappa_claim"] or 0) >= gates["kappa_min"] for v in agreement.values()) if agreement else False
    n_ok = len(gold) >= gates["gold_rows_for_accuracy_claims"]
    rep["gates"] = {"kappa_min": gates["kappa_min"], "kappa_ok": k_ok,
                    "gold_min": gates["gold_rows_for_accuracy_claims"], "gold_ok": n_ok,
                    "reportable_to_jury": k_ok and n_ok}

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"{args.set}_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORTS / f"{args.set}_report.md").write_text(_markdown(rep), encoding="utf-8")
    print(_markdown(rep))
    return 0


def _markdown(rep: dict) -> str:
    g = rep["gates"]
    lines = [f"# Gold T1 — bộ `{rep['set']}` ({rep['split']})", "",
             f"Sinh lúc {rep['generated']} · {rep['codebook']} · ngưỡng đăng ký trước: `configs/measurement_decisions.yaml`", "",
             f"**Được báo cáo cho BGK: {'CÓ' if g['reportable_to_jury'] else 'CHƯA'}** — "
             f"κ (tuyên bố/không) ≥ {g['kappa_min']}: {'đạt' if g['kappa_ok'] else 'chưa'}; "
             f"gold ≥ {g['gold_min']} câu: {'đạt' if g['gold_ok'] else 'chưa'} ({rep['gold']}).", "",
             "## Dữ liệu", "",
             f"- Câu ứng viên: {rep['candidates']} · người gán: {', '.join(rep['labelers']) or '—'} · nhãn lượt 1: {rep['labels']}",
             f"- Gold: {rep['gold']} · phân bố: {rep['gold_distribution']['label']}",
             f"- Chủ đề: {rep['gold_distribution']['topic']}",
             f"- Lý do NOT_CLAIM: {rep['gold_distribution']['why_not']}",
             f"- Ngôn ngữ: {rep['gold_distribution']['lang']} · công ty: {rep['gold_distribution']['companies']} · "
             f"cần ngữ cảnh: {rep['gold_distribution']['needs_context']} · dấu hiệu: {rep['gold_distribution']['flags']}",
             f"- Nguồn nhãn gold: {rep['gold_distribution']['source']}", "",
             "## Đồng thuận lượt 1 (gán độc lập, trước khi họp)", "",
             "| Cặp | n | Đồng ý | κ 5 nhãn [95% CI] | κ tuyên bố/không [95% CI] |", "|---|---|---|---|---|"]
    for pair, v in rep["agreement"].items():
        lines.append(f"| {pair} | {v['n']} | {v['observed']} | {v['kappa_5']} {v['kappa_5_ci'] or ''} | "
                     f"{v['kappa_claim']} {v['kappa_claim_ci'] or ''} |")
    if rep.get("fleiss_kappa_5") is not None:
        lines.append(f"\nFleiss κ (5 nhãn, mọi người gán): {rep['fleiss_kappa_5']}")
    lines += ["", f"Bất đồng lượt 1 theo loại: {rep['disagreements_first_pass']}",
              f"Họp thống nhất: {rep['consensus']['decided']} câu đã quyết · {rep['consensus']['conventions_added']} quy ước mới",
              f"Thời gian: giây/câu {rep['seconds_per_sentence'] or '—'}", ""]
    if "rules_vs_gold" in rep:
        r = rep["rules_vs_gold"]
        lines += ["## Bộ trích bằng luật so với gold (tuyên bố / không)", "",
                  f"precision {r['precision']} · recall {r['recall']} · F1 {r['f1']} {r['f1_ci'] or ''} · "
                  f"loại tuyên bố đúng {rep['product_claim_type_accuracy']}", ""]
    if "teacher_vs_gold" in rep:
        t = rep["teacher_vs_gold"]
        lines += ["## Nhãn thầy so với gold (chất lượng dữ liệu huấn luyện)", "",
                  f"n {t['n']} · accuracy {t['accuracy']} {t['accuracy_ci'] or ''} · macro-F1 {t['macro_f1']} "
                  f"{t['macro_f1_ci'] or ''} · tuyên bố/không {t['claim_vs_not']}", "",
                  "| Lớp | P | R | F1 | n |", "|---|---|---|---|---|"]
        for c, m in t["per_class"].items():
            lines.append(f"| {c} | {m['precision']} | {m['recall']} | {m['f1']} | {m['support']} |")
        lines += ["", f"Nhầm lẫn (gold→thầy): {t['confusion']}", ""]
    if "claude_vs_gold" in rep:
        c = rep["claude_vs_gold"]
        lines += ["## Claude so với gold (mốc AI, không thuộc gold)", "",
                  f"Claude gán {c['n_labelled']} câu; {c['n_with_gold']} câu đã có gold ({c['unsure']} Claude để UNSURE) · "
                  f"accuracy {c['accuracy']} {c['accuracy_ci'] or ''} · macro-F1 {c['macro_f1']} {c['macro_f1_ci'] or ''} · "
                  f"κ 5 nhãn {c['kappa_5']} · tuyên bố/không {c['claim_vs_not']}", "",
                  "| Lớp | P | R | F1 | n |", "|---|---|---|---|---|"]
        for cls, m in c["per_class"].items():
            lines.append(f"| {cls} | {m['precision']} | {m['recall']} | {m['f1']} | {m['support']} |")
        lines += ["", f"Lệch (gold→Claude): {c['confusion']}",
                  f"κ giữa Claude và từng người (lượt 1): {c['kappa_with_each_person']}", ""]
    lines += ["CI: bootstrap 1.000 lần trên câu (seed 13). Gold chỉ gồm câu đã thống nhất; UNSURE và câu có AI hỗ trợ chưa qua họp bị loại."]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- main
def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--set", choices=sorted(SETS), required=True)
    b.add_argument("--company", default="hpg")
    b.add_argument("--pdf", nargs="+", default=[str(PDF)])
    b.add_argument("--n", type=int, default=160, help="audit: sentences taken from the teacher batch")
    b.add_argument("--min-chars", type=int, default=25)
    b.add_argument("--max-chars", type=int, default=500)
    b.add_argument("--random-share", type=float, default=0.10, help="hpg: share of non-environmental sentences kept")
    b.add_argument("--kappa-size", type=int, default=40)
    b.add_argument("--lot-size", type=int, default=50)
    b.add_argument("--seed", type=int, default=13)
    e = sub.add_parser("export")
    e.add_argument("--set", choices=sorted(SETS), required=True)
    e.add_argument("--labelers", nargs="+", default=["quynh", "thao"])
    e.add_argument("--lots", help="e.g. 1 or 2,3,4 (default: all)")
    e.add_argument("--overlap", choices=["all", "first"], default="all",
                   help="all: everyone labels every lot (default) · first: only lot 1, the rest split")
    ec = sub.add_parser("export-csv")
    ec.add_argument("--labeler", required=True)
    ec.add_argument("--sets", nargs="+", choices=sorted(SETS), default=["audit", "hpg"])
    ec.add_argument("--lots", default="1", help="e.g. 1 (default) or 2,3")
    ex = sub.add_parser("export-xlsx")
    ex.add_argument("--labelers", nargs="+", default=["nhan"])
    ex.add_argument("--sets", nargs="+", choices=sorted(SETS), default=["audit", "hpg"])
    ex.add_argument("--lots", default="1", help="e.g. 1 (default) or 2,3")
    i = sub.add_parser("import")
    i.add_argument("files", nargs="+")
    i.add_argument("--force", action="store_true", help="import even with problems")
    c = sub.add_parser("consensus")
    c.add_argument("--set", choices=sorted(SETS), required=True)
    c.add_argument("--lots")
    ic = sub.add_parser("import-consensus")
    ic.add_argument("file")
    ic.add_argument("--force", action="store_true")
    m = sub.add_parser("merge")
    m.add_argument("--set", choices=sorted(SETS), required=True)
    r = sub.add_parser("report")
    r.add_argument("--set", choices=sorted(SETS), required=True)
    args = ap.parse_args()
    return {"build": build, "export": export, "export-csv": export_csv, "export-xlsx": export_xlsx, "import": import_, "consensus": consensus,
            "import-consensus": import_consensus, "merge": merge, "report": report}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
