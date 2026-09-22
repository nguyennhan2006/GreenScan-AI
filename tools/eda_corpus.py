#!/usr/bin/env python3
"""EDA + cleaning for the VN30 candidate corpus.

The 7,960 claim candidates come from keyword matching over PDF text. Spot-checking
showed the top hit was a Bao Viet navigation menu -- "Tầm nhìn - Chiến lược
Thương hiệu ... Đại hội đồng cổ đông" -- which contains "phát triển bền vững"
and therefore scored as an environmental claim. Feeding that to an LLM wastes
tokens and poisons any annotation sample.

This measures the corpus, then writes a filtered view. It does not delete
anything: `claim_candidates_clean.jsonl` is a new file and every dropped record
is accounted for by rule in the report.

    python tools/eda_corpus.py
    python tools/eda_corpus.py --report-only
    python tools/eda_corpus.py --out data/crawl/vn30/curated
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NORM = REPO / "data/crawl/vn30/normalized"

sys.path.insert(0, str(REPO / "src"))
from quantum_gw.utils.jsonl import read_jsonl as load, write_jsonl  # noqa: E402

# --- Boilerplate signatures, each traced to a real observed failure ------------

# Navigation menus: many short Title-Case fragments, no verb, no sentence end.
NAV_TERMS = [
    "trang chủ", "liên hệ", "tuyển dụng", "sơ đồ", "đăng nhập", "tìm kiếm",
    "quan hệ cổ đông", "quan hệ nhà đầu tư", "đại hội đồng cổ đông",
    "tầm nhìn", "sứ mệnh", "giải thưởng", "danh hiệu", "lĩnh vực hoạt động",
    "cơ cấu tổ chức", "ban lãnh đạo", "tin tức", "sự kiện", "thư viện",
    "điều lệ", "quy chế", "biểu mẫu", "xem thêm", "chi tiết", "tải về",
]
# Section headers / table-of-contents lines rather than assertions.
HEADER_RE = re.compile(
    r"^(mục lục|nội dung|chương|phần|phụ lục|báo cáo (của|về)|"
    r"table of contents|contents|appendix|section)\b", re.I)
# GRI/standard index rows: long runs of codes, not prose.
INDEX_RE = re.compile(r"(gri\s*\d{3}|sasb|tcfd)[\s\-:]*\d", re.I)
# Runs of dot leaders or pipes = layout artefact.
LAYOUT_RE = re.compile(r"(\.{4,}|\-{4,}|\|{2,}|…{2,})")

VERB_HINTS = [
    "đã", "sẽ", "là", "được", "có", "giảm", "tăng", "đạt", "cam kết", "thực hiện",
    "áp dụng", "triển khai", "sử dụng", "tiết kiệm", "phát thải", "chiếm",
    "we ", "our ", "is ", "are ", "was ", "were ", "will ", "has ", "have ",
    "reduced", "achieved", "committed", "increased",
]
CLAIMY = [
    "cam kết", "mục tiêu", "đến năm", "net zero", "trung hòa carbon", "giảm phát thải",
    "năng lượng tái tạo", "thân thiện môi trường", "kinh tế tuần hoàn",
    "tiết kiệm năng lượng", "tái chế", "net-zero", "carbon neutral",
    "renewable energy", "target", "by 2030", "sustainable",
]
NUM_RE = re.compile(r"\d")


def norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text or "").casefold().strip()


def title_ratio(text: str) -> float:
    words = [w for w in re.findall(r"[A-Za-zÀ-ỹ]+", text) if len(w) > 2]
    if not words:
        return 0.0
    return sum(1 for w in words if w[0].isupper()) / len(words)


def reasons(text: str) -> list[str]:
    """Every reason a record looks like boilerplate rather than a claim."""
    low = norm(text)
    out = []
    if len(text.strip()) < 40:
        out.append("too_short")
    if HEADER_RE.search(low):
        out.append("section_header")
    if INDEX_RE.search(low):
        out.append("standards_index_row")
    if LAYOUT_RE.search(text):
        out.append("layout_artifact")
    hits = sum(1 for t in NAV_TERMS if t in low)
    if hits >= 3:
        out.append("navigation_menu")
    elif hits >= 2 and title_ratio(text) > 0.45:
        out.append("navigation_menu")
    if not any(v in low for v in VERB_HINTS):
        out.append("no_predicate")
    if title_ratio(text) > 0.6 and "." not in text[:-1]:
        out.append("title_case_fragment")
    if len(set(re.findall(r"\b\w+\b", low))) < 6:
        out.append("too_few_unique_tokens")
    return out


def informativeness(rec: dict) -> float:
    """Cheap priority score for annotation sampling: specific > vague."""
    text = rec.get("text", "")
    low = norm(text)
    score = 0.0
    score += 2.0 if rec.get("has_number") else 0.0
    score += min(sum(1 for c in CLAIMY if c in low), 3) * 1.0
    score += 1.5 if re.search(r"\d+([.,]\d+)?\s*(%|tco2e|co2e|mwh|gwh|tấn|kwh)", low) else 0.0
    score += 1.0 if re.search(r"\b(20\d{2})\b", low) else 0.0
    score += 1.0 if rec.get("document_type") in {"sustainability_report", "integrated_report"} else 0.0
    score -= 1.0 if len(text) > 1200 else 0.0
    return round(score, 2)


def describe(name: str, rows: list[dict]) -> dict:
    lens = [len(r.get("text", "")) for r in rows]
    return {
        "file": name,
        "records": len(rows),
        "companies": len({r.get("company_id") for r in rows}),
        "documents": len({r.get("document_id") for r in rows}),
        "text_len_median": int(statistics.median(lens)) if lens else 0,
        "text_len_p95": int(sorted(lens)[int(len(lens) * 0.95)]) if lens else 0,
        "by_split": dict(Counter(r.get("split") for r in rows)),
        "by_doc_type": dict(Counter(r.get("document_type") for r in rows).most_common(8)),
        "with_number": sum(1 for r in rows if r.get("has_number")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalized", type=Path, default=NORM)
    ap.add_argument("--out", type=Path, default=REPO / "data/crawl/vn30/curated")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--min-score", type=float, default=2.0)
    args = ap.parse_args()

    claims = load(args.normalized / "claim_candidates.jsonl")
    evidence = load(args.normalized / "evidence_candidates.jsonl")
    docs = load(args.normalized / "documents.jsonl")

    report: dict = {"input": [describe("claim_candidates", claims),
                              describe("evidence_candidates", evidence)]}

    # --- duplication ---------------------------------------------------------
    seen: dict[str, int] = Counter(norm(r["text"]) for r in claims)
    dup_records = sum(v - 1 for v in seen.values() if v > 1)
    report["duplication"] = {
        "unique_texts": len(seen),
        "duplicate_records": dup_records,
        "duplicate_rate": round(dup_records / max(len(claims), 1), 4),
        "worst_offenders": [{"count": c, "text": t[:110]} for t, c in seen.most_common(5) if c > 1],
    }

    # --- boilerplate ---------------------------------------------------------
    tagged = []
    reason_counts: Counter = Counter()
    for r in claims:
        rs = reasons(r.get("text", ""))
        reason_counts.update(rs)
        tagged.append((r, rs))
    flagged = [r for r, rs in tagged if rs]
    report["boilerplate"] = {
        "flagged_records": len(flagged),
        "flagged_rate": round(len(flagged) / max(len(claims), 1), 4),
        "by_reason": dict(reason_counts.most_common()),
        "examples": [{"reasons": rs, "text": r["text"][:120]}
                     for r, rs in tagged if rs][:5],
    }

    # --- company concentration ----------------------------------------------
    per_co = Counter(r.get("company_id") for r in claims)
    total = sum(per_co.values()) or 1
    shares = [v / total for v in per_co.values()]
    hhi = sum(s * s for s in shares)
    report["concentration"] = {
        "companies": len(per_co),
        "top5": per_co.most_common(5),
        "hhi": round(hhi, 4),
        "effective_companies": round(1 / hhi, 1) if hhi else 0,
        "note": "HHI over claim counts. Low effective_companies means a benchmark "
                "mostly measures one issuer's writing style.",
    }

    # --- clean view ----------------------------------------------------------
    kept, dropped, seen_text = [], [], set()
    for r, rs in tagged:
        key = norm(r["text"])
        if rs:
            dropped.append((r, rs))
            continue
        if key in seen_text:
            dropped.append((r, ["duplicate_text"]))
            continue
        seen_text.add(key)
        r = dict(r)
        r["informativeness"] = informativeness(r)
        kept.append(r)

    priority = [r for r in kept if r["informativeness"] >= args.min_score]
    priority.sort(key=lambda r: -r["informativeness"])

    report["output"] = {
        "kept": len(kept),
        "dropped": len(dropped),
        "kept_rate": round(len(kept) / max(len(claims), 1), 4),
        "annotation_priority_pool": len(priority),
        "priority_by_company": dict(Counter(r["company_id"] for r in priority).most_common()),
        "priority_by_doc_type": dict(Counter(r["document_type"] for r in priority).most_common()),
        "priority_by_split": dict(Counter(r["split"] for r in priority).most_common()),
    }

    if not args.report_only:
        args.out.mkdir(parents=True, exist_ok=True)
        write_jsonl(args.out / "claim_candidates_clean.jsonl", kept)
        write_jsonl(args.out / "annotation_priority.jsonl", priority)
        write_jsonl(args.out / "dropped_with_reasons.jsonl",
                    [{**r, "drop_reasons": rs} for r, rs in dropped])
        (args.out / "EDA_REPORT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        write_markdown(args.out / "EDA_REPORT.md", report, args.min_score)

    print(json.dumps(report, ensure_ascii=False, indent=2)[:3000])
    if not args.report_only:
        print(f"\nWrote {args.out}")
    return 0


def write_markdown(path: Path, rep: dict, min_score: float) -> None:
    b, c, o, d = rep["boilerplate"], rep["concentration"], rep["output"], rep["duplication"]
    inp = rep["input"][0]
    path.write_text(f"""# EDA — VN30 claim candidates

## Input

{inp['records']:,} claim candidates from {inp['documents']:,} documents across
{inp['companies']} companies. Median length {inp['text_len_median']} chars, p95
{inp['text_len_p95']}. {inp['with_number']:,} contain a number.

## Three problems that make the raw file unusable as-is

**1. Boilerplate — {b['flagged_rate']:.1%} of records ({b['flagged_records']:,}).**
Keyword matching cannot tell a claim from a navigation menu that happens to
contain "phát triển bền vững". Reasons:

{chr(10).join(f"- `{k}` × {v:,}" for k, v in b['by_reason'].items())}

**2. Duplication — {d['duplicate_records']:,} redundant records
({d['duplicate_rate']:.1%}).** The same boilerplate line repeats across pages and
report years. Annotating these spends budget re-labelling one sentence.

**3. Concentration — HHI {c['hhi']}, effective companies {c['effective_companies']}
out of {c['companies']}.** Top contributors: {', '.join(f"{k} ({v:,})" for k, v in c['top5'])}.
A benchmark drawn uniformly from this file mostly measures the largest issuer's
house style, not greenwashing.

## Output

| | |
| --- | ---: |
| Kept after filtering | {o['kept']:,} ({o['kept_rate']:.1%}) |
| Dropped (with reasons) | {o['dropped']:,} |
| Annotation priority pool (score ≥ {min_score}) | {o['annotation_priority_pool']:,} |

Priority pool by split: {o['priority_by_split']}

`informativeness` rewards a number with a unit, a target year, claim vocabulary
and sustainability-report provenance; it penalises very long passages. It is a
**sampling aid, not a label** — it says "worth a reviewer's time", never
"this is greenwashing".

## Files

- `claim_candidates_clean.jsonl` — filtered, deduplicated, scored
- `annotation_priority.jsonl` — the pool to annotate first
- `dropped_with_reasons.jsonl` — every exclusion, auditable and reversible
- `EDA_REPORT.json` — the numbers above, machine-readable

Nothing here is deleted from `normalized/`; this is an additive curated view.
""", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
