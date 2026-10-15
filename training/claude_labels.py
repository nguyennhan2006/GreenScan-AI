"""Claude as a labeller: training sentences in rounds, plus the lots people are labelling, for comparison.

Two sets, kept apart because they answer different questions:

  train    sentences from the corpus's training pool: never an id of dev/test
           (exclude_from_training.txt), never a company of test, never a sentence an
           earlier round already labelled. Stratified on the rules' weak signals so the
           rare classes are there (QUANTIFIED, claims the rules missed), with a cap per
           company. → training data, label_source "teacher", teacher_model claude.
  compare  the sentences of the human lots (r1: lot 1; r2: the remaining lots).
           Claude answers the question people answer, on the same text and page
           image. → never gold, never training; stored under gold_t1/ai/ and read
           by `gold_t1_pack.py report` once people have labelled. Do not open it
           before you have submitted your own labels for those lots.

Rounds: r1 (500 train, lot 1, files directly in training/data/claude/) and r2
(~3,000 train, lots 2+, files in training/data/claude/r2/). Each round keeps its
own pools, batches, passes and decisions; `publish` combines every finalized
round into claude_train.jsonl and gold_t1/ai/claude_compare.jsonl.

Protocol, the same discipline as for people:
  sample   → batches hold only what a labeller sees (id, source, previous
             sentence, sentence, next sentence, page image), mixed train+compare
  pass A, pass B → two separate Claude agents per batch, each reading
             CODEBOOK.md, writing out/A_bNN.jsonl and out/B_bNN.jsonl blind to the other;
             `validate` checks a pass file against its batch before it counts
  merge    → schema check, κ between passes, review list: every disagreement,
             every UNSURE / confidence-1 / flagged row, every QUANTIFIED without a
             figure or claim with a figure-free QUANTIFIED, plus a 10% random
             sample of agreed rows. r2 merges per batch (--batch bNN) and also
             writes audit/bNN_in.jsonl: the review rows again, blind, shuffled
  adjudicate → a third reading decides the review list (r1: adjudication.jsonl;
             r2: adj/bNN.jsonl, written by an agent that sees both passes)
  audit    → r2 only: a fourth reading labels audit/bNN_in.jsonl from scratch,
             seeing neither pass nor decision (audit/bNN_out.jsonl). A decision the
             audit contradicts is "contested" and kept out of training.
  finalize → the round's labels; then publish

usage:
  python training/claude_labels.py [--round r1|r2] sample [--n 500] [--lots 1] [--batches 10 | --batch-size 80]
  python training/claude_labels.py --round r2 validate --batch b07 --file out/A_b07.jsonl
  python training/claude_labels.py [--round r2] merge [--batch b07]
  python training/claude_labels.py [--round r2] finalize
  python training/claude_labels.py publish
  python training/claude_labels.py [--round r1|r2|all] stats
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gold_t1_pack as g  # noqa: E402

DIR = ROOT / "training/data/claude"
CODEBOOK = DIR / "CODEBOOK.md"
SENTENCES = ROOT / "training/data/claim_sentences.jsonl"
TEACHER = ROOT / "training/data/teacher_claim_gemma-4-31B-it.jsonl"
MODEL = "claude-opus-5-5"
LABELS = ["QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE", "NOT_CLAIM", "UNSURE"]
TOPICS = ["emissions_reduction", "renewable_energy", "resource_efficiency", "waste_and_circularity",
          "green_finance", "biodiversity", "esg_process_integration", "generic_sustainability"]
WHY = ["table_heading", "broken", "other_org", "general_knowledge", "non_env", "other"]
FLAGS = ["OVERCLAIM", "INCONSISTENCY", "FUTURE"]
CLAIMS = set(LABELS[:3])
FIELDS = ("label", "topic", "why_not", "confidence", "needs_context", "flag", "note")
# rule kept? names an environmental term? carries a figure? → share of the round's n
QUOTAS = {
    "r1": {"rule_fig": 110, "rule_nofig": 100, "env_fig": 80, "env_nofig": 110, "other_fig": 50, "other": 50},
    # r1 yields: QUANTIFIED is ~26% of rule_fig and ~11% of env_fig, VAGUE ~21% of rule_nofig,
    # other/other_fig are ~97% NOT_CLAIM. r2 takes rule_fig almost whole (816 left) for the rare classes
    # and keeps enough of the rest that NOT_CLAIM still looks like the corpus.
    "r2": {"rule_fig": 750, "rule_nofig": 800, "env_fig": 600, "env_nofig": 550, "other_fig": 150, "other": 150},
}


def stratum(r: dict) -> str:
    fig = "fig" if r["has_figure"] else "nofig"
    if r["rule_label"]:
        return f"rule_{fig}"
    if r["lexicon_hit"]:
        return f"env_{fig}"
    return "other_fig" if r["has_figure"] else "other"


def _readable(text: str) -> bool:
    letters = sum(ch.isalpha() for ch in text)
    return 40 <= len(text) <= 450 and letters / max(1, len(text)) >= 0.6


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def base(rnd: str) -> Path:
    return DIR if rnd == "r1" else DIR / rnd


def labels_path(rnd: str) -> Path:
    return DIR / "claude_labels.jsonl" if rnd == "r1" else DIR / rnd / "labels.jsonl"


def rounds() -> list[str]:
    return ["r1"] + sorted(p.name for p in DIR.glob("r[0-9]*") if p.is_dir())


def _lots(spec: str) -> set[int]:
    out = set()
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out |= set(range(int(a), int(b or a) + 1))
    return out


def _codebook() -> str:
    m = re.search(r"codebook v([\d.]+)", CODEBOOK.read_text(encoding="utf-8")[:300])
    return f"{CODEBOOK.name} v{m.group(1) if m else '?'} sha {_sha(CODEBOOK)}"


# ----------------------------------------------------------------------------- sample
def sample(args) -> int:
    rng = random.Random(args.seed)
    out_dir = base(args.round)
    quota = QUOTAS[args.round]
    held = {line.strip() for line in (g.OUT / "exclude_from_training.txt").open(encoding="utf-8") if line.strip()}
    held_text = {_norm(json.loads(line)["text"]) for f in g.OUT.glob("*_candidates.jsonl")
                 for line in f.open(encoding="utf-8")}
    test_companies = {json.loads(line)["company_id"] for line in (g.OUT / "hpg_candidates.jsonl").open(encoding="utf-8")}
    gemma = {json.loads(line)["id"]: json.loads(line)["teacher_label"] for line in TEACHER.open(encoding="utf-8")}
    # sentences an earlier round already holds, train or compare
    done = {r["id"] for rnd in rounds() if rnd != args.round
            for f in ("pool_train.jsonl", "pool_compare.jsonl") for r in _read(base(rnd) / f)}
    done_text = {_norm(r["text"]) for rnd in rounds() if rnd != args.round
                 for r in _read(base(rnd) / "pool_train.jsonl")}

    pool, seen = [], set()
    for line in SENTENCES.open(encoding="utf-8"):
        r = json.loads(line)
        key = _norm(r["text"])
        if (r["id"] in held or r["id"] in done or key in held_text or key in done_text or key in seen
                or r["company_id"] in test_companies or not _readable(r["text"])):
            continue
        seen.add(key)
        r["stratum"] = stratum(r)
        pool.append(r)
    rng.shuffle(pool)
    if args.round != "r1":
        # 17 training companies share the per-company cap; in random order the common strata used
        # it up and r2 got 127 of 740 rule_fig. Rare strata first (r1 kept as drawn).
        order = ["rule_fig", "env_fig", "rule_nofig", "env_nofig", "other_fig", "other"]
        pool.sort(key=lambda r: order.index(r["stratum"]))

    cap = max(1, round(args.company_cap * args.n))
    total = sum(quota.values())
    per_company, per_stratum, picked = Counter(), Counter(), []

    def take(r) -> bool:
        if per_company[r["company_id"]] >= cap or per_stratum[r["stratum"]] >= quota[r["stratum"]] * args.n / total:
            return False
        picked.append(r)
        per_company[r["company_id"]] += 1
        per_stratum[r["stratum"]] += 1
        return True

    overlap = [r for r in pool if r["id"] in gemma]
    n_gemma = 0
    for r in overlap:
        if n_gemma < args.gemma and take(r):
            n_gemma += 1
    chosen = {r["id"] for r in picked}
    for r in pool:
        if len(picked) >= args.n:
            break
        if r["id"] not in chosen:
            take(r)

    context = g.corpus_neighbours(picked)
    raw = {json.loads(line)["doc_id"]: json.loads(line) for line in g.CRAWL_RAW.open(encoding="utf-8")}
    train = []
    for r in picked:
        u = raw.get(r["doc_id"], {})
        title = (u.get("title") or "").splitlines()[0].strip() if u.get("title") else ""
        title = "trang web" if title.startswith("http") or not title else title
        prev, nxt = context[r["id"]]
        train.append({"id": r["id"], "set": "train", "company_id": r["company_id"], "doc": r["doc_id"],
                      "source": " · ".join(x for x in (str(r["company_id"]).upper(), title,
                                                       str(r.get("reporting_year") or "")) if x),
                      "text": r["text"], "prev_text": prev, "next_text": nxt, "page_image": None,
                      "rule_label": r["rule_label"], "lexicon_hit": r["lexicon_hit"], "has_figure": r["has_figure"],
                      "stratum": r["stratum"], "reporting_year": r.get("reporting_year"),
                      "gemma_label": gemma.get(r["id"])})

    lots = _lots(args.lots)
    compare_rows = [r for name in ("audit", "hpg") for r in g.load_candidates(name)
                    if r["lot"] in lots and r["id"] not in done]
    compare_rows = g._with_sources(compare_rows)
    images = DIR / "pages"
    images.mkdir(parents=True, exist_ok=True)
    compare = []
    for r in compare_rows:
        img = images / f"{r['id']}.jpg"
        has = img.exists() or g._page_image(r, img)
        compare.append({"id": r["id"], "set": f"compare_{r['set']}", "company_id": r["company_id"], "doc": r["doc"],
                        "source": g._source(r), "text": r["text"], "prev_text": r["prev_text"],
                        "next_text": r["next_text"], "page_image": img.relative_to(ROOT).as_posix() if has else None,
                        "rule_label": r["rule_label"], "lexicon_hit": r["lexicon_hit"], "has_figure": r["has_figure"],
                        "stratum": r["stratum"], "lot": r["lot"]})

    out_dir.mkdir(parents=True, exist_ok=True)
    _write(out_dir / "pool_train.jsonl", train)
    _write(out_dir / "pool_compare.jsonl", compare)
    # batches: only what a labeller sees, train and compare mixed so no pass knows which is which
    blind = [_blind(r) for r in train + compare]
    rng.shuffle(blind)
    for sub in ("batches", "out"):
        (out_dir / sub).mkdir(exist_ok=True)
    n_batches = -(-len(blind) // args.batch_size) if args.batch_size else args.batches
    size = -(-len(blind) // n_batches)
    for i in range(n_batches):
        _write(out_dir / "batches" / f"b{i + 1:02d}.jsonl", blind[i * size:(i + 1) * size])
    print(f"[{args.round}] train {len(train)} · compare {len(compare)} · {n_batches} batches × ~{size}")
    print("  train strata:", dict(Counter(r["stratum"] for r in train)), "· pool:", dict(Counter(r["stratum"] for r in pool)))
    print("  companies:", len({r["company_id"] for r in train}), "· max/company:",
          max(Counter(r["company_id"] for r in train).values()), f"(cap {cap})",
          "· gemma overlap:", sum(r["gemma_label"] is not None for r in train),
          "· vi/en:", dict(Counter(g._lang(r["text"]) for r in train)))
    print("  compare:", dict(Counter(r["set"] for r in compare)), "· lots:", sorted({r["lot"] for r in compare}),
          "· page images:", sum(r["page_image"] is not None for r in compare))
    print(f"  codebook: {_codebook()}")
    return 0


def _blind(r: dict) -> dict:
    return {"id": r["id"], "nguon": r["source"], "cau_truoc": r["prev_text"], "cau": r["text"],
            "cau_sau": r["next_text"], "anh_trang": r["page_image"]}


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()] if path.exists() else []


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12] if path.exists() else "-"


def _pool(rnd: str) -> dict[str, dict]:
    b = base(rnd)
    return {r["id"]: r for r in _read(b / "pool_train.jsonl") + _read(b / "pool_compare.jsonl")}


# ----------------------------------------------------------------------------- validate / merge
def check(x: dict) -> list[str]:
    e = []
    if x.get("label") not in LABELS:
        return [f"label {x.get('label')!r}"]
    if x["label"] in CLAIMS and x.get("topic") not in TOPICS:
        e.append(f"topic {x.get('topic')!r}")
    if x["label"] == "NOT_CLAIM" and x.get("why_not") not in WHY:
        e.append(f"why_not {x.get('why_not')!r}")
    if x["label"] != "NOT_CLAIM" and x.get("why_not"):
        e.append("why_not on a non-NOT_CLAIM")
    if x["label"] == "NOT_CLAIM" and x.get("topic"):
        e.append("topic on NOT_CLAIM")
    if x.get("confidence") not in (1, 2, 3):
        e.append(f"confidence {x.get('confidence')!r}")
    if x.get("flag") not in (None, *FLAGS):
        e.append(f"flag {x.get('flag')!r}")
    if not isinstance(x.get("needs_context"), bool):
        e.append("needs_context not bool")
    if (x["label"] == "UNSURE" or x.get("confidence") == 1 or x.get("flag") or x.get("why_not") == "other") \
            and not (x.get("note") or "").strip():
        e.append("note missing")
    return e


def validate(args) -> int:
    """A pass, decision or audit file against the rows it answers: same ids, once each, schema clean."""
    b = base(args.round)
    path = Path(args.file) if Path(args.file).is_absolute() else b / args.file
    source = (Path(args.expect) if Path(args.expect).is_absolute() else b / args.expect) if args.expect \
        else b / "batches" / f"{args.batch}.jsonl"
    expected = [r["id"] for r in _read(source)]
    if not expected:
        print(f"! no expected rows in {source}")
        return 1
    try:
        got = _read(path)
    except json.JSONDecodeError as e:
        print(f"! {path.name}: not JSON lines ({e})")
        return 1
    problems = [f"line {i} {x.get('id')}: {e}" for i, x in enumerate(got, 1) for e in check(x)]
    ids = [x.get("id") for x in got]
    missing = [i for i in expected if i not in set(ids)]
    extra = [i for i in ids if i not in set(expected)]
    dup = [i for i, n in Counter(ids).items() if n > 1]
    for p in problems[:30]:
        print("  !", p)
    print(f"{path.name}: {len(got)} rows for {len(expected)} expected · schema problems {len(problems)} · "
          f"missing {len(missing)} {missing[:3]} · extra {len(extra)} {extra[:3]} · duplicated {len(dup)} {dup[:3]}")
    return 1 if problems or missing or extra or dup else 0


def _passes(b: Path, batch: str | None = None) -> tuple[dict, dict, list[str]]:
    A, B, problems = {}, {}, []
    for f in sorted((b / "out").glob(f"[AB]_{batch or 'b*'}.jsonl")):
        target = A if f.name.startswith("A_") else B
        for i, x in enumerate(_read(f), 1):
            for e in check(x):
                problems.append(f"{f.name}:{i} {x.get('id')}: {e}")
            target[x["id"]] = x
    return A, B, problems


def _figure(text: str) -> bool:
    """A quantity that is not a year, a standard or a decree number."""
    t = re.sub(r"\b(ISO|TCVN|QCVN|GRI|SA|OHSAS)\s*[\d:.\-]+", " ", text, flags=re.I)
    t = re.sub(r"\b\d{1,4}/\d{4}/[A-ZĐ\-]+\w*", " ", t)
    return any(not re.fullmatch(r"(19|20)\d\d", n) for n in re.findall(r"\d[\d.,]*", t))


def merge(args) -> int:
    b = base(args.round)
    rows = _pool(args.round)
    A, B, problems = _passes(b, args.batch)
    if args.batch:
        ids = [r["id"] for r in _read(b / "batches" / f"{args.batch}.jsonl")]
        rows = {i: rows[i] for i in ids}
    for p in problems[:30]:
        print("  !", p)
    missing = [i for i in rows if i not in A or i not in B]
    both = [i for i in rows if i in A and i in B]
    print(f"[{args.round}{' ' + args.batch if args.batch else ''}] pass A {len(A)} · pass B {len(B)} · "
          f"both {len(both)}/{len(rows)} · schema problems {len(problems)}")
    if missing:
        print(f"  {len(missing)} câu thiếu ít nhất một lượt (ví dụ {missing[:3]})")
    pairs = [(A[i]["label"], B[i]["label"]) for i in both]
    claim_pairs = [(a in CLAIMS, b_ in CLAIMS) for a, b_ in pairs if "UNSURE" not in (a, b_)]
    print(f"  κ A–B 5 nhãn {g._kappa(pairs)} · tuyên bố/không {g._kappa(claim_pairs)} · "
          f"đồng ý {sum(a == b_ for a, b_ in pairs)}/{len(pairs)}")

    seed = args.seed + (int(args.batch[1:]) if args.batch else 0)
    rng = random.Random(seed)
    review = []
    for i in both:
        a, bb, r = A[i], B[i], rows[i]
        why = []
        if a["label"] != bb["label"]:
            why.append("nhãn khác")
        elif a["label"] in CLAIMS and a.get("topic") != bb.get("topic"):
            why.append("chủ đề khác")
        elif a["label"] == "NOT_CLAIM" and a.get("why_not") != bb.get("why_not"):
            why.append("lý do khác")
        if "UNSURE" in (a["label"], bb["label"]) or 1 in (a.get("confidence"), bb.get("confidence")):
            why.append("không chắc")
        if a.get("flag") or bb.get("flag"):
            why.append("có cờ")
        if "QUANTIFIED_CLAIM" in (a["label"], bb["label"]) and not _figure(r["text"]):
            why.append("QUANTIFIED mà câu không có số")
        if a["label"] == bb["label"] == "QUALITATIVE_CLAIM" and _figure(r["text"]):
            why.append("có số mà gán QUALITATIVE")
        if not why and rng.random() < args.spot:
            why.append("soát ngẫu nhiên")
        if why:
            review.append({"id": i, "why": why, "set": r["set"], "source": r["source"], "prev": r["prev_text"],
                           "text": r["text"], "next": r["next_text"], "page_image": r.get("page_image"),
                           "A": {k: a.get(k) for k in FIELDS}, "B": {k: bb.get(k) for k in FIELDS}})
    if args.batch:
        _write(b / "review" / f"{args.batch}.jsonl", review)
        audit = [_blind(rows[x["id"]]) for x in review]
        rng.shuffle(audit)
        _write(b / "audit" / f"{args.batch}_in.jsonl", audit)
        target = f"review/{args.batch}.jsonl + audit/{args.batch}_in.jsonl"
    else:
        _write(b / "review.jsonl", review)
        target = "review.jsonl"
    print(f"  cần đọc lại: {len(review)} · {dict(Counter(w for x in review for w in x['why']))} -> {target}")
    return 1 if missing or problems else 0


# ----------------------------------------------------------------------------- finalize / publish
def finalize(args) -> int:
    b = base(args.round)
    rows = _pool(args.round)
    A, B, problems = _passes(b)
    if args.round == "r1":
        decided = {x["id"]: x for x in _read(b / "adjudication.jsonl")}
        review = {x["id"]: x for x in _read(b / "review.jsonl")}
        audit = {}
    else:
        decided = {x["id"]: x for f in sorted((b / "adj").glob("b*.jsonl")) for x in _read(f)}
        review = {x["id"]: x for f in sorted((b / "review").glob("b*.jsonl")) for x in _read(f)}
        audit = {x["id"]: x for f in sorted((b / "audit").glob("b*_out.jsonl")) for x in _read(f)}
    bad = [f"decision {x['id']}: {e}" for x in decided.values() for e in check(x)]
    bad += [f"audit {x['id']}: {e}" for x in audit.values() for e in check(x)]
    open_ = sorted(set(review) - set(decided))
    # blind audit was run on b01 only once the user asked to save tokens (13/10); --audit-optional lets
    # unaudited batches through, and "contested" then exists only where an audit does
    unaudited = sorted(set(review) - set(audit)) if args.round != "r1" and not args.audit_optional else []
    if problems or bad or open_ or unaudited:
        for p in (problems + bad)[:20]:
            print("  !", p)
        if open_:
            print(f"  ! {len(open_)} câu cần đọc lại chưa có quyết định (ví dụ {open_[:3]})")
        if unaudited:
            print(f"  ! {len(unaudited)} câu cần đọc lại chưa có lượt soát mù (ví dụ {unaudited[:3]})")
        if not args.force:
            return 1
    book = _codebook()
    out = []
    for i, r in rows.items():
        a, bb = A.get(i), B.get(i)
        if not (a and bb):
            continue
        if i in decided:
            final, source = decided[i], "adjudicated"
            if i in audit and audit[i]["label"] != final["label"]:
                source = "contested"
        elif a["label"] == bb["label"]:
            final, source = a, "agree"
        else:
            continue
        keep = {k: final.get(k) for k in FIELDS}
        agree = sum(x["label"] == keep["label"] for x in (a, bb))
        out.append({**{k: r[k] for k in ("id", "set", "company_id", "doc", "source", "text", "prev_text", "next_text",
                                          "rule_label", "lexicon_hit", "has_figure", "stratum")},
                    "reporting_year": r.get("reporting_year"), "lot": r.get("lot"), **keep,
                    "pass_a": a["label"], "pass_b": bb["label"], "decided_by": source,
                    "passes_agreeing": agree, "audit_label": audit[i]["label"] if i in audit else None,
                    "round": args.round, "model": MODEL, "codebook": book if args.round != "r1" else
                    "CODEBOOK.md sha 49e1a64986b1",
                    "gemma_label": r.get("gemma_label")})
    _write(labels_path(args.round), out)
    print(f"[{args.round}] {len(out)} nhãn -> {labels_path(args.round).relative_to(ROOT)} · "
          f"decided: {dict(Counter(x['decided_by'] for x in out))}")
    if audit:
        # spot rows are agreed rows re-read at random: the audit there estimates the error left in "agree"
        for kind, keep_ in (("bất đồng/không chắc", lambda w: w != ["soát ngẫu nhiên"]),
                            ("soát ngẫu nhiên (ước lượng lỗi của câu hai lượt đồng ý)", lambda w: w == ["soát ngẫu nhiên"])):
            xs = [x for x in out if x["id"] in audit and keep_(review[x["id"]]["why"])]
            hit = sum(x["audit_label"] == x["label"] for x in xs)
            print(f"  soát mù · {kind}: khớp {hit}/{len(xs)}" + (f" = {hit / len(xs):.2f}" if xs else ""))
    return publish(args)


def publish(_args=None) -> int:
    """Every finalized round → claude_train.jsonl (training rows) and gold_t1/ai/claude_compare.jsonl."""
    out, seen = [], {}
    for rnd in rounds():
        for x in _read(labels_path(rnd)):
            x.setdefault("round", rnd)
            if x["id"] in seen:
                raise SystemExit(f"{x['id']} labelled in {seen[x['id']]} and {rnd}")
            seen[x["id"]] = rnd
            out.append(x)
    train = [x for x in out if x["set"] == "train" and x["label"] != "UNSURE" and x["decided_by"] != "contested"]
    compare = [x for x in out if x["set"].startswith("compare")]
    _write(DIR / "claude_train.jsonl", train)
    _write(g.OUT / "ai" / "claude_compare.jsonl", compare)
    print(f"publish: train {len(train)} -> claude_train.jsonl · compare {len(compare)} -> gold_t1/ai/claude_compare.jsonl")
    print("  train:", dict(Counter(x["label"] for x in train)), "· by round:", dict(Counter(x["round"] for x in train)))
    kept = {x["id"] for x in train}
    left_out = Counter("UNSURE" if x["label"] == "UNSURE" else x["decided_by"]
                       for x in out if x["set"] == "train" and x["id"] not in kept)
    if left_out:
        print("  kept out of train:", dict(left_out))
    return 0


def stats(args) -> int:
    which = rounds() if args.round == "all" else [args.round]
    out = [x for rnd in which for x in _read(labels_path(rnd))]
    if not out:
        print("chưa finalize")
        return 1
    train = [x for x in out if x["set"] == "train"]
    print(f"[{', '.join(which)}] {len(out)} nhãn ({len(train)} train)")
    for name, rows in (("train", train), ("compare", [x for x in out if x["set"] != "train"])):
        print(f"  {name}: nhãn {dict(Counter(x['label'] for x in rows))}")
        print(f"    chủ đề {dict(Counter(x['topic'] for x in rows if x['topic']))}")
        print(f"    lý do {dict(Counter(x['why_not'] for x in rows if x['why_not']))}")
    pairs = [(x["pass_a"], x["pass_b"]) for x in out]
    print(f"  κ A–B {g._kappa(pairs)} · cần ngữ cảnh {sum(bool(x['needs_context']) for x in out)} · "
          f"cờ {dict(Counter(x['flag'] for x in out if x['flag']))} · "
          f"quyết định {dict(Counter(x['decided_by'] for x in out))}")
    both = [(x["label"], x["gemma_label"]) for x in train if x.get("gemma_label") and x["label"] != "UNSURE"]
    if both:
        print(f"  Claude vs gemma ({len(both)} câu chung): đồng ý {sum(a == b for a, b in both)}/{len(both)} · "
              f"κ {g._kappa(both)} · tuyên bố/không κ {g._kappa([(a in CLAIMS, b in CLAIMS) for a, b in both])}")
        print("    khác nhau:", dict(Counter(f'{a}→{b}' for a, b in both if a != b).most_common(6)))
    rules = [(x["label"] in CLAIMS, bool(x["rule_label"])) for x in train if x["label"] != "UNSURE"]
    tp = sum(a and b for a, b in rules)
    print(f"  luật so với Claude (train): precision {tp}/{sum(b for _, b in rules)} · recall {tp}/{sum(a for a, _ in rules)}")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--round", default="r1", help="r1, r2, … (stats also takes 'all')")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=500)
    s.add_argument("--gemma", type=int, default=100, help="sentences the gemma teacher also labelled")
    s.add_argument("--company-cap", type=float, default=0.12, help="max share of one company")
    s.add_argument("--lots", default="1", help="human lots to label for comparison, e.g. 1 or 2-12")
    s.add_argument("--batches", type=int, default=10)
    s.add_argument("--batch-size", type=int, default=0, help="overrides --batches")
    s.add_argument("--seed", type=int, default=13)
    v = sub.add_parser("validate")
    v.add_argument("--batch", help="bNN: expected ids are batches/bNN.jsonl")
    v.add_argument("--expect", help="other file holding the expected ids (e.g. audit/b07_in.jsonl)")
    v.add_argument("--file", required=True, help="file to check, relative to the round folder")
    m = sub.add_parser("merge")
    m.add_argument("--batch", help="bNN: merge one batch (r2+)")
    m.add_argument("--spot", type=float, default=0.10, help="share of agreed rows re-read anyway")
    m.add_argument("--seed", type=int, default=13)
    f = sub.add_parser("finalize")
    f.add_argument("--force", action="store_true")
    f.add_argument("--audit-optional", action="store_true", help="r2+: batches without a blind audit may finalize")
    sub.add_parser("publish")
    sub.add_parser("stats")
    args = ap.parse_args()
    if args.cmd == "validate" and not (args.batch or args.expect):
        ap.error("validate needs --batch or --expect")
    return {"sample": sample, "validate": validate, "merge": merge, "finalize": finalize,
            "publish": publish, "stats": stats}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
