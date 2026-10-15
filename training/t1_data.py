"""The T1 example: the one record format every T1 training, dev and test row must have.

A row is trainable only if it says what the model reads, what the answer is,
who gave the answer and how sure that is, and which split it belongs to, so
that no company and no sentence leaks from training into evaluation. FIELDS
below is the single source of truth: the JSON Schema
(schemas/training/t1_example.schema.json), the field table in
docs/04-data-ai/QUY_TRINH_GAN_NHAN_T1_2026-10-11.md and the checks in `check`
are all derived from it.

  train  teacher labels on corpus companies: gemma (≥ 3 runs, majority, agreement
         kept) and Claude (two blind passes, disagreements re-read and decided)
  dev    audit gold: people's agreed labels on sentences the teacher also labelled
  test   HPG gold: a company with no sentence in the corpus, text from the PDF parser

usage:
  python training/t1_data.py schema                         # write the JSON Schema
  python training/t1_data.py fields                         # field table (markdown)
  python training/t1_data.py from-teacher <run.jsonl> [...] # → training/data/t1/train_teacher.jsonl
  python training/t1_data.py from-claude                    # → training/data/t1/train_claude.jsonl
  python training/t1_data.py from-gold --set audit|hpg      # → training/data/t1/{dev_audit,test_hpg}.jsonl
  python training/t1_data.py check [files...]               # schema + cross-row rules; default: all three
  python training/t1_data.py combine                        # → training/data/t1/t1_all.jsonl for train_classifier.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labeling_pack import CLAIM_TYPES  # noqa: E402
from masking import mask, residual_digits  # noqa: E402

DATA = ROOT / "training/data/t1"
GOLD = ROOT / "training/data/gold_t1"
SCHEMA = ROOT / "schemas/training/t1_example.schema.json"
VERSION = "t1-example-v1"
MASK_VERSION = "training/masking.py: numbers only, no entity names (= teacher-claim-v1)"

LABELS = ["QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE", "NOT_CLAIM"]
CLAIMS = set(LABELS[:3])
TOPICS = [t.split(" — ")[0] for t in CLAIM_TYPES]
WHY_NOT = ["table_heading", "broken", "other_org", "general_knowledge", "non_env", "other"]
SOURCES = ["teacher", "gold_consensus", "gold_agree", "gold_single"]

# name, JSON type, required when, allowed values, group, purpose
# "required when": always · gold · teacher · claim_gold (gold row whose label is a claim)
#                  · not_claim_gold · optional
FIELDS = [
    ("id", "string", "always", None, "1. Định danh", "Khóa câu (sha1 16 ký tự). Dùng để loại câu dev/test khỏi train và nối nhãn các nguồn."),
    ("company_id", "string", "always", None, "1. Định danh", "Mã công ty. Chia tập theo công ty: công ty ở test không được có câu nào ở train."),
    ("doc", "string", "always", None, "1. Định danh", "Tài liệu gốc (tên file PDF hoặc doc_id của kho)."),
    ("page", "integer|null", "optional", None, "1. Định danh", "Trang trong tài liệu gốc, để mở lại và kiểm."),
    ("reporting_year", "integer|null", "optional", None, "1. Định danh", "Năm báo cáo. Dùng để phân tích lệch theo thời gian."),
    ("source_kind", "string", "always", ["crawl_clean", "pdf_parser"], "1. Định danh", "Cách lấy chữ: kho crawl đã làm sạch, hay parser PDF của sản phẩm. Hai nguồn khác nhau là một phần của độ lệch miền."),
    ("text", "string", "always", None, "2. Đầu vào mô hình", "Câu gốc, 25–500 ký tự, cắt đúng như bộ tách câu của sản phẩm."),
    ("text_masked", "string", "always", None, "2. Đầu vào mô hình", "Câu mà mô hình đọc: số đã thay bằng <E1>…, năm giữ nguyên. Thầy cũng gán trên dạng này."),
    ("mask_version", "string", "always", None, "2. Đầu vào mô hình", "Cách che số đã dùng. Train và test phải cùng một cách che."),
    ("prev_text", "string", "always", None, "2. Đầu vào mô hình", "Câu liền trước (rỗng nếu không có). Dùng khi huấn luyện dạng cặp câu cho câu thiếu chủ ngữ."),
    ("next_text", "string", "always", None, "2. Đầu vào mô hình", "Câu liền sau (rỗng nếu không có)."),
    ("lang", "string", "always", ["vi", "en"], "2. Đầu vào mô hình", "Ngôn ngữ câu. Báo cáo kết quả tách theo ngôn ngữ."),
    ("rule_label", "integer", "always", [0, 1], "3. Đặc trưng phụ", "1 nếu bộ trích bằng luật giữ câu này. Là mốc so sánh (baseline), không phải nhãn."),
    ("lexicon_hit", "integer", "always", [0, 1], "3. Đặc trưng phụ", "1 nếu câu có thuật ngữ môi trường trong taxonomy. Dùng để phân tầng khi lấy mẫu."),
    ("has_figure", "integer", "always", [0, 1], "3. Đặc trưng phụ", "1 nếu câu có số (không tính năm)."),
    ("stratum", "string", "always", None, "3. Đặc trưng phụ", "Nhóm lấy mẫu của câu. Cần để tính lại tỷ lệ đúng khi mẫu không đều."),
    ("label", "string", "always", LABELS, "4. Nhãn", "Đích của T1: QUANTIFIED_CLAIM · QUALITATIVE_CLAIM · VAGUE · NOT_CLAIM. UNSURE không bao giờ vào dữ liệu."),
    ("is_claim", "boolean", "always", None, "4. Nhãn", "label ≠ NOT_CLAIM. Đích phụ: tuyên bố hay không."),
    ("topic", "string|null", "claim_gold", TOPICS + [None], "4. Nhãn", "Chủ đề (8 loại claim_type của sản phẩm). Bắt buộc với câu gold là tuyên bố; đo độ đúng loại tuyên bố của sản phẩm."),
    ("why_not", "string|null", "not_claim_gold", WHY_NOT + [None], "4. Nhãn", "Vì sao không phải tuyên bố. Dùng để phân tích lỗi và sửa bộ lọc."),
    ("label_source", "string", "always", SOURCES, "5. Nguồn và chất lượng nhãn", "teacher, hoặc gold_consensus (qua họp), gold_agree (mọi người cùng nhãn), gold_single (một người)."),
    ("labelers", "array", "gold", None, "5. Nguồn và chất lượng nhãn", "Người gán. Gold phải có ít nhất một người."),
    ("codebook_version", "string", "gold", None, "5. Nguồn và chất lượng nhãn", "Phiên bản bộ quy tắc lúc gán (codebook v1.x)."),
    ("confidence_min", "integer|null", "gold", [1, 2, 3, None], "5. Nguồn và chất lượng nhãn", "Độ chắc thấp nhất trong các người gán (1–3). Có thể dùng làm trọng số."),
    ("needs_context", "boolean", "gold", None, "5. Nguồn và chất lượng nhãn", "Có người phải đọc câu trước/sau mới quyết được. Đo riêng nhóm này."),
    ("ai_assisted", "boolean", "gold", [False], "5. Nguồn và chất lượng nhãn", "Luôn false: câu có AI hỗ trợ không được vào gold."),
    ("flags", "array", "optional", None, "5. Nguồn và chất lượng nhãn", "OVERCLAIM / INCONSISTENCY / FUTURE: tín hiệu tẩy xanh, dữ liệu cho bước sau."),
    ("teacher_model", "string", "teacher", None, "5. Nguồn và chất lượng nhãn", "Mô hình thầy (vd gemma-4-31B-it)."),
    ("prompt_version", "string", "teacher", None, "5. Nguồn và chất lượng nhãn", "Phiên bản prompt thầy (teacher-claim-v1, v2…). Phải khớp codebook đang dùng cho gold."),
    ("teacher_runs", "integer", "teacher", None, "5. Nguồn và chất lượng nhãn", "Số lần thầy gán câu này (cần ≥ 3, hoặc 2 lượt kèm `teacher_review`)."),
    ("teacher_agreement", "number", "teacher", None, "5. Nguồn và chất lượng nhãn", "Tỷ lệ lần gán trùng nhãn cuối (0–1). Không có `teacher_review` thì chỉ huấn luyện câu ≥ 0,67."),
    ("teacher_review", "string|null", "optional", ["agree", "adjudicated", None], "5. Nguồn và chất lượng nhãn", "Claude: hai lượt độc lập trùng nhau (agree), hoặc khác nhau / đáng ngờ nên được đọc lại và quyết (adjudicated)."),
    ("split", "string", "always", ["train", "dev", "test"], "6. Chia tập", "train = nhãn thầy · dev = gold kiểm định · test = gold HPG. Không còn review/unassigned."),
    ("set", "string", "always", ["corpus", "audit", "hpg"], "6. Chia tập", "Bộ dữ liệu gốc của câu."),
    ("contract_version", "string", "always", [VERSION], "6. Chia tập", "Phiên bản khung này."),
]
MIN_TEACHER_RUNS, MIN_TEACHER_AGREEMENT = 3, 0.67
CLAUDE = ROOT / "training/data/claude/claude_train.jsonl"


def usable_teacher(r: dict) -> bool:
    """R6: a teacher label is trained on only when it is stable — three or more runs
    agreeing, or two blind passes whose result was agreed or re-read and decided."""
    if r.get("teacher_review") in ("agree", "adjudicated"):
        return r.get("teacher_runs", 0) >= 2
    return r.get("teacher_runs", 0) >= MIN_TEACHER_RUNS and r.get("teacher_agreement", 0) >= MIN_TEACHER_AGREEMENT
MIN_PER_CLASS = {"train": 100, "dev": 15, "test": 15}


# ----------------------------------------------------------------------------- schema
def _json_type(t: str):
    parts = t.split("|")
    return parts[0] if len(parts) == 1 else parts


def schema() -> dict:
    props, required = {}, []
    for name, t, when, allowed, group, purpose in FIELDS:
        p = {"type": _json_type(t), "description": f"[{group}] {purpose}"}
        if allowed is not None:
            p["enum"] = allowed
        if name in ("labelers", "flags"):
            p["items"] = {"type": "string"}
        if name == "text":
            p.update(minLength=25, maxLength=500)
        if name == "teacher_agreement":
            p.update(minimum=0, maximum=1)
        props[name] = p
        if when == "always":
            required.append(name)
    gold_req = [n for n, _t, w, *_ in FIELDS if w == "gold"]
    teacher_req = [n for n, _t, w, *_ in FIELDS if w == "teacher"]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "t1_example.schema.json",
        "title": "T1Example",
        "description": "One sentence for the T1 claim detector: model input, target, label provenance and split. "
                       "Generated from training/t1_data.py FIELDS — edit there, not here.",
        "type": "object",
        "additionalProperties": False,
        "properties": props,
        "required": required,
        "allOf": [
            {"if": {"properties": {"label_source": {"const": "teacher"}}},
             "then": {"required": teacher_req}, "else": {"required": gold_req}},
            {"if": {"properties": {"label_source": {"enum": SOURCES[1:]}, "is_claim": {"const": True}}},
             "then": {"properties": {"topic": {"type": "string"}}}},
            {"if": {"properties": {"label_source": {"enum": SOURCES[1:]}, "label": {"const": "NOT_CLAIM"}}},
             "then": {"properties": {"why_not": {"type": "string"}}}},
        ],
    }


def fields_markdown() -> str:
    when_vi = {"always": "luôn", "gold": "gold", "teacher": "thầy", "claim_gold": "gold là tuyên bố",
               "not_claim_gold": "gold NOT_CLAIM", "optional": "không"}
    lines, group = [], None
    for name, t, when, allowed, g, purpose in FIELDS:
        if g != group:
            lines += ["", f"**{g}**", "", "| Trường | Kiểu | Bắt buộc | Giá trị | Để làm gì |", "|---|---|---|---|---|"]
            group = g
        values = ", ".join(str(a) for a in allowed if a is not None) if allowed else ""
        lines.append(f"| `{name}` | {t.replace('|', ' / ')} | {when_vi[when]} | {values} | {purpose} |")
    return "\n".join(lines).strip() + "\n"


# ----------------------------------------------------------------------------- convert
def _base(r: dict) -> dict:
    masked = mask(r["text"], "E", [])[0]
    return {"id": r["id"], "company_id": r["company_id"], "doc": r.get("doc") or r.get("doc_id"),
            "page": r.get("page"), "reporting_year": r.get("reporting_year") or r.get("year"),
            "text": r["text"], "text_masked": masked, "mask_version": MASK_VERSION,
            "prev_text": r.get("prev_text") or "", "next_text": r.get("next_text") or "",
            "lang": r.get("lang") or _lang(r["text"]),
            "rule_label": int(r["rule_label"]), "lexicon_hit": int(r["lexicon_hit"]),
            "has_figure": int(r["has_figure"]), "stratum": str(r.get("stratum") or ""),
            "contract_version": VERSION}


def _lang(text: str) -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gold_t1_pack import _lang as lang
    return lang(text)


def _write(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} dòng -> {out.relative_to(ROOT)} · {dict(Counter(r['label'] for r in rows))}")


def from_teacher(args) -> int:
    """Several teacher runs over the same sentences → one row per sentence, majority label."""
    runs: dict[str, list[dict]] = defaultdict(list)
    for f in args.files:
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            runs[r["id"]].append(r)
    held = set()
    exclude = GOLD / "exclude_from_training.txt"
    if exclude.exists():
        held = {line.strip() for line in exclude.open(encoding="utf-8") if line.strip()}
    hpg = {json.loads(line)["company_id"] for line in (GOLD / "hpg_candidates.jsonl").open(encoding="utf-8")} \
        if (GOLD / "hpg_candidates.jsonl").exists() else set()
    rows, dropped = [], Counter()
    for sid, rs in runs.items():
        if sid in held:
            dropped["câu của dev/test"] += 1
            continue
        if rs[0]["company_id"] in hpg:
            dropped["công ty của test"] += 1
            continue
        votes = Counter(r["teacher_label"] for r in rs)
        label, n = votes.most_common(1)[0]
        first = rs[0]
        row = {**_base(first), "label": label, "is_claim": label in CLAIMS, "topic": None, "why_not": None,
               "label_source": "teacher", "flags": [],
               "teacher_model": first.get("teacher_model"), "prompt_version": first.get("prompt_version"),
               "teacher_runs": len(rs), "teacher_agreement": round(n / len(rs), 3),
               "split": "train", "set": "corpus", "source_kind": "crawl_clean"}
        row["text_masked"] = first.get("sent_text") or row["text_masked"]   # exactly what the teacher read
        rows.append(row)
    print("loại:", dict(dropped))
    _write(rows, DATA / "train_teacher.jsonl")
    weak = sum(r["teacher_runs"] < MIN_TEACHER_RUNS or r["teacher_agreement"] < MIN_TEACHER_AGREEMENT for r in rows)
    if weak:
        print(f"  {weak} dòng chưa đủ {MIN_TEACHER_RUNS} lần gán hoặc đồng thuận < {MIN_TEACHER_AGREEMENT}: "
              "`check` sẽ báo, `combine` sẽ bỏ")
    return 0


def from_claude(_args) -> int:
    """Claude's training labels (training/claude_labels.py finalize) → the T1 frame."""
    rows = []
    for line in CLAUDE.open(encoding="utf-8"):
        r = json.loads(line)
        rows.append({**_base(r), "label": r["label"], "is_claim": r["label"] in CLAIMS,
                     "topic": r["topic"], "why_not": r["why_not"], "label_source": "teacher",
                     "flags": [r["flag"]] if r.get("flag") else [], "confidence_min": r["confidence"],
                     "needs_context": bool(r["needs_context"]),
                     "teacher_model": r["model"], "prompt_version": r["codebook"],
                     "teacher_runs": 2, "teacher_agreement": round(r["passes_agreeing"] / 2, 3),
                     "teacher_review": r["decided_by"], "split": "train", "set": "corpus",
                     "source_kind": "crawl_clean"})
    _write(rows, DATA / "train_claude.jsonl")
    return 0


def from_gold(args) -> int:
    gold = [json.loads(line) for line in (GOLD / f"{args.set}_gold.jsonl").open(encoding="utf-8")]
    labels = defaultdict(list)
    for f in (GOLD / "labels").glob(f"{args.set}_lo*.jsonl"):
        for line in f.open(encoding="utf-8"):
            x = json.loads(line)
            labels[x["id"]].append(x)
    source = {"consensus": "gold_consensus", "agree": "gold_agree", "single": "gold_single"}
    rows = []
    for g in gold:
        books = sorted({x.get("codebook") or "" for x in labels.get(g["id"], [])})
        rows.append({**_base(g), "label": g["gold_label"], "is_claim": g["is_claim"], "topic": g["topic"],
                     "why_not": g["why_not"], "label_source": source[g["source"]], "labelers": g["labelers"],
                     "codebook_version": " + ".join(b for b in books if b) or "unknown",
                     "confidence_min": g["confidence_min"], "needs_context": g["needs_context"],
                     "ai_assisted": False, "flags": g["flags"],
                     "split": "dev" if args.set == "audit" else "test", "set": args.set,
                     "source_kind": "crawl_clean" if args.set == "audit" else "pdf_parser"})
    _write(rows, DATA / ("dev_audit.jsonl" if args.set == "audit" else "test_hpg.jsonl"))
    return 0


# ----------------------------------------------------------------------------- check
def _type_ok(value, t: str) -> bool:
    ok = {"string": lambda v: isinstance(v, str), "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
          "number": lambda v: isinstance(v, int | float) and not isinstance(v, bool),
          "boolean": lambda v: isinstance(v, bool), "array": lambda v: isinstance(v, list), "null": lambda v: v is None}
    return any(ok[p](value) for p in t.split("|"))


def check_row(r: dict) -> list[str]:
    errors = []
    gold = str(r.get("label_source", "")).startswith("gold")
    known = {f[0] for f in FIELDS}
    errors += [f"trường lạ `{k}`" for k in r if k not in known]
    for name, t, when, allowed, *_ in FIELDS:
        needed = (when == "always" or (when == "gold" and gold) or (when == "teacher" and not gold)
                  or (when == "claim_gold" and gold and r.get("is_claim"))
                  or (when == "not_claim_gold" and gold and r.get("label") == "NOT_CLAIM"))
        if name not in r or (needed and r[name] in (None, "") and name not in ("prev_text", "next_text")):
            if needed:
                errors.append(f"thiếu `{name}`")
            continue
        if not _type_ok(r[name], t) and not (r[name] is None and not needed):
            errors.append(f"`{name}` sai kiểu ({type(r[name]).__name__}, cần {t})")
        elif allowed is not None and r[name] not in allowed:
            errors.append(f"`{name}` = {r[name]!r} không thuộc {allowed}")
    text = r.get("text") or ""
    if not 25 <= len(text) <= 500:
        errors.append(f"`text` dài {len(text)} ký tự (cần 25–500)")
    if r.get("label") is not None and r.get("is_claim") is not None and r["is_claim"] != (r["label"] in CLAIMS):
        errors.append("`is_claim` không khớp `label`")
    if gold and r.get("split") == "train":
        errors.append("gold không được nằm ở train (gold là thước đo)")
    return errors


def leftover_digits(r: dict) -> list[str]:
    """Digits left after masking, slot tokens (<E1>) and years excluded. Usually labels
    ('Phạm vi 3', 'VN100', 'ISO 14064'); a figure here would be a masking leak."""
    return residual_digits(re.sub(r"<[A-Z]+\d+>", " ", r.get("text_masked") or ""))


def check(args) -> int:
    files = [Path(f) for f in args.files] or sorted(DATA.glob("*.jsonl"))
    files = [f for f in files if f.name != "t1_all.jsonl"]
    rows, bad = [], 0
    for f in files:
        errs = Counter()
        for i, line in enumerate(f.open(encoding="utf-8"), 1):
            r = json.loads(line)
            rows.append(r)
            for e in check_row(r):
                errs[e.split(" (")[0].split(": [")[0]] += 1
                if args.verbose:
                    print(f"  {f.name}:{i}: {e}")
        bad += sum(errs.values())
        print(f"{f.name}: {i if f.stat().st_size else 0} dòng · " + ("đạt khung" if not errs else f"{sum(errs.values())} lỗi"))
        for e, n in errs.most_common(8):
            print(f"   ! {e} × {n}")

    # cross-row rules
    problems = []
    # one sentence labelled by two teachers is expected (combine keeps Claude's); anything else is a clash
    ids = Counter((r["id"], r.get("teacher_model") or r.get("label_source")) for r in rows)
    problems += [f"id trùng: {k[0]} × {n}" for k, n in ids.items() if n > 1][:5]
    both = Counter(r["id"] for r in rows if r.get("label_source") == "teacher")
    two_teachers = sum(1 for n in both.values() if n > 1)
    split_of = defaultdict(set)
    for r in rows:
        split_of[r["id"]].add(r.get("split"))
    problems += [f"id {k} nằm ở nhiều tập: {sorted(v)}" for k, v in split_of.items() if len(v) > 1][:5]
    by_split = defaultdict(set)
    for r in rows:
        by_split[r.get("split")].add(r.get("company_id"))
    leak = by_split["train"] & by_split["test"]
    if leak:
        problems.append(f"công ty vừa ở train vừa ở test: {sorted(leak)}")
    exclude = GOLD / "exclude_from_training.txt"
    if exclude.exists():
        held = {line.strip() for line in exclude.open(encoding="utf-8") if line.strip()}
        n = sum(r["id"] in held for r in rows if r.get("split") == "train")
        if n:
            problems.append(f"{n} câu của dev/test nằm trong train")
    texts = defaultdict(set)
    for r in rows:
        texts[" ".join(str(r.get("text", "")).lower().split())].add(r.get("split"))
    dup = sum(1 for s in texts.values() if "train" in s and len(s) > 1)
    if dup:
        problems.append(f"{dup} câu trùng chữ giữa train và dev/test")
    weak = sum(1 for r in rows if r.get("label_source") == "teacher" and not usable_teacher(r))
    leftover = [r for r in rows if leftover_digits(r)]
    print("\nQuy tắc giữa các dòng:")
    for p in problems:
        print("   !", p)
    if weak:
        print(f"   · {weak} dòng thầy chưa ổn định (< {MIN_TEACHER_RUNS} lần gán hoặc đồng thuận < {MIN_TEACHER_AGREEMENT}, "
              "và không qua đọc lại) — bị bỏ khi combine")
    if two_teachers:
        print(f"   · {two_teachers} câu có nhãn của cả hai thầy (gemma và Claude) — combine giữ nhãn Claude")
    if leftover:
        top = Counter(d for r in leftover for d in leftover_digits(r)).most_common(6)
        print(f"   · {len(leftover)} dòng còn chữ số sau khi che (thường là nhãn: 'Phạm vi 3', 'VN100'); hay gặp: {top}")
    for split in ("train", "dev", "test"):
        c = Counter(r.get("label") for r in rows if r.get("split") == split)
        if not c:
            print(f"   · {split}: chưa có dữ liệu")
            continue
        thin = [k for k in LABELS if c.get(k, 0) < MIN_PER_CLASS[split]]
        print(f"   · {split}: {sum(c.values())} dòng {dict(c)}" + (f" — lớp mỏng (< {MIN_PER_CLASS[split]}): {thin}" if thin else ""))
    if not problems and not bad:
        print("   đạt")
    return 1 if problems or bad else 0


def combine(_args) -> int:
    # Claude first: on a sentence both teachers labelled, the reviewed two-pass label wins
    rows, seen, dropped = [], set(), Counter()
    for name in ("train_claude.jsonl", "train_teacher.jsonl", "dev_audit.jsonl", "test_hpg.jsonl"):
        f = DATA / name
        if not f.exists():
            print(f"  (chưa có {name})")
            continue
        for line in f.open(encoding="utf-8"):
            r = json.loads(line)
            if r["label_source"] == "teacher" and not usable_teacher(r):
                dropped["thầy chưa ổn định"] += 1
                continue
            if r["id"] in seen:
                dropped[f"trùng id ({name})"] += 1
                continue
            seen.add(r["id"])
            rows.append(r)
    if dropped:
        print("  bỏ:", dict(dropped))
    _write(rows, DATA / "t1_all.jsonl")
    print("  huấn luyện: python training/train_classifier.py --data training/data/t1/t1_all.jsonl "
          "--label-field label --text-field text_masked --exclude training/data/gold_t1/exclude_from_training.txt")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("schema")
    sub.add_parser("fields")
    t = sub.add_parser("from-teacher")
    t.add_argument("files", nargs="+")
    sub.add_parser("from-claude")
    g = sub.add_parser("from-gold")
    g.add_argument("--set", choices=["audit", "hpg"], required=True)
    c = sub.add_parser("check")
    c.add_argument("files", nargs="*")
    c.add_argument("-v", "--verbose", action="store_true")
    sub.add_parser("combine")
    args = ap.parse_args()
    if args.cmd == "schema":
        SCHEMA.parent.mkdir(parents=True, exist_ok=True)
        SCHEMA.write_text(json.dumps(schema(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"-> {SCHEMA.relative_to(ROOT)}")
        return 0
    if args.cmd == "fields":
        print(fields_markdown())
        return 0
    return {"from-teacher": from_teacher, "from-claude": from_claude, "from-gold": from_gold, "check": check,
            "combine": combine}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
