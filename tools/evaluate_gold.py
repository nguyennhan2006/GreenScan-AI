"""Two evaluations, kept apart on purpose.

    python tools/evaluate_gold.py                     # every session in data/gold/sessions
    python tools/evaluate_gold.py --split test        # one split only
    python tools/evaluate_gold.py --sessions a.jsonl b.jsonl

A single end-to-end number cannot say where a system is wrong. So retrieval and
verification are measured separately, against the same gold rows:

    retrieval      claim -> candidates: is the evidence a human chose in the top k?
                   Recall@k, MRR, nDCG@k
    verification   claim + the evidence a human chose -> is the verdict right?
                   macro-F1, confusion matrix, false-contradiction rate,
                   abstention coverage and selective accuracy

Retrieval fails -> fix retrieval. Retrieval is right and the verdict is wrong ->
fix the verifier. That distinction is the entire reason this file exists.

It runs before there is any gold, and says so instead of printing zeros: an
empty evaluation reports "0 adjudicated rows" and computes nothing. Numbers
appear only when a human has put them there.

Gold format: whatever `tools/label_session.py` writes -- `data/gold/sessions/*.jsonl`,
one row per claim, with `labels.evidence` mapping evidence_id to a relation and
`labels.verdict` holding the adjudicated verdict.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SESSIONS = ROOT / "data" / "gold" / "sessions"
OUT_DIR = ROOT / "benchmark"

# Relations a labeller may put on an evidence item; the first two count as
# "this is the evidence I would have wanted retrieved".
RELEVANT = {"supports", "contradicts", "partial"}
VERDICTS = [
    "SUPPORTED", "PARTIALLY_SUPPORTED", "CONTRADICTED",
    "UNSUPPORTED", "INSUFFICIENT_EVIDENCE",
]
ABSTAIN = {"INSUFFICIENT_EVIDENCE"}
KS = (1, 3, 5, 10, 30)


# ------------------------------------------------------------------- loading


def load_rows(paths: list[Path], split: str | None) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row["_session"] = path.name
            if split and row.get("split") != split:
                continue
            rows.append(row)
    return rows


def adjudicated(rows: list[dict]) -> list[dict]:
    """Rows a human actually decided. Everything else is a blank form."""
    return [r for r in rows if (r.get("labels") or {}).get("labeler")]


# ------------------------------------------------------------ retrieval side


def retrieval_metrics(rows: list[dict]) -> dict:
    """Scores the ranking stored in the session — the one the labeller saw.

    This measures the retriever that produced those candidates, not necessarily
    the one in the repository today. The report says so; re-scoring today's
    retriever needs the corpus the candidates came from and is a separate job.
    """
    usable = [
        r for r in rows
        if r.get("evidence_candidates")
        and any(rel in RELEVANT for rel in (r["labels"].get("evidence") or {}).values())
    ]
    if not usable:
        return {"rows": 0}

    recall = {k: [] for k in KS}
    reciprocal: list[float] = []
    ndcg: list[float] = []
    for row in usable:
        gold = {
            eid for eid, rel in (row["labels"].get("evidence") or {}).items()
            if rel in RELEVANT
        }
        ranked = sorted(row["evidence_candidates"], key=lambda c: c.get("rank", 10**6))
        hits = [1 if c.get("evidence_id") in gold else 0 for c in ranked]
        for k in KS:
            top = hits[:k]
            recall[k].append(sum(top) / len(gold) if gold else 0.0)
        first = next((i for i, hit in enumerate(hits, start=1) if hit), None)
        reciprocal.append(1.0 / first if first else 0.0)
        gain = sum(hit / math.log2(i + 1) for i, hit in enumerate(hits[:10], start=1))
        ideal = sum(1 / math.log2(i + 1) for i in range(1, min(len(gold), 10) + 1))
        ndcg.append(gain / ideal if ideal else 0.0)

    return {
        "rows": len(usable),
        "recall_at": {f"@{k}": _mean_ci(recall[k]) for k in KS},
        "mrr": _mean_ci(reciprocal),
        "ndcg_at_10": _mean_ci(ndcg),
    }


# --------------------------------------------------------- verification side


def verification_metrics(rows: list[dict], settings) -> dict:
    """Runs the verifier on the claim and the evidence a human chose.

    Retrieval is taken out of the picture on purpose: whatever this measures is
    the verifier's own behaviour, on the evidence it should have been given.
    """
    from quantum_gw.agents.orchestrator import OrchestratorAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import DocumentInput

    usable = [r for r in rows if (r["labels"].get("verdict") or "").upper() in VERDICTS]
    if not usable:
        return {"rows": 0}

    pairs: list[tuple[str, str]] = []
    for row in usable:
        gold_ids = {
            eid for eid, rel in (row["labels"].get("evidence") or {}).items()
            if rel in RELEVANT
        }
        chosen = [
            c for c in row.get("evidence_candidates", [])
            if not gold_ids or c.get("evidence_id") in gold_ids
        ]
        evidence_text = "\n".join(c.get("text", "") for c in chosen[:5]).strip()
        if not evidence_text:
            continue
        documents = [
            DocumentInput(name="claim.txt", text=row["text"], role=DocumentRole.CLAIM_SOURCE,
                          source_type=SourceType.INTERNAL),
            DocumentInput(name="evidence.txt", text=evidence_text, role=DocumentRole.EVIDENCE,
                          source_type=SourceType.EXTERNAL),
        ]
        result = OrchestratorAgent(settings).run(documents)
        predicted = (
            result.verifications[0].status.value if result.verifications
            else "INSUFFICIENT_EVIDENCE"   # nothing extracted: the system declined
        )
        pairs.append((row["labels"]["verdict"].upper(), predicted))

    if not pairs:
        return {"rows": 0}

    confusion: dict[str, Counter] = defaultdict(Counter)
    for gold, predicted in pairs:
        confusion[gold][predicted] += 1

    per_class = {}
    for label in VERDICTS:
        tp = confusion[label][label]
        fp = sum(confusion[g][label] for g in VERDICTS if g != label)
        fn = sum(confusion[label][p] for p in VERDICTS if p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(confusion[label].values())
        if support or tp + fp:
            per_class[label] = {"precision": round(precision, 4), "recall": round(recall, 4),
                                "f1": round(f1, 4), "support": support}

    # The error this product cares about most: asserting a contradiction that a
    # human did not. Reported on its own, never averaged away.
    false_contradiction = sum(
        1 for gold, predicted in pairs
        if predicted == "CONTRADICTED" and gold != "CONTRADICTED"
    )
    abstained = [p for _, p in pairs if p in ABSTAIN]
    decided = [(g, p) for g, p in pairs if p not in ABSTAIN]

    return {
        "rows": len(pairs),
        "accuracy": _mean_ci([1.0 if g == p else 0.0 for g, p in pairs]),
        "macro_f1": round(
            sum(v["f1"] for v in per_class.values()) / max(1, len(per_class)), 4
        ),
        "per_class": per_class,
        "confusion": {g: dict(c) for g, c in confusion.items()},
        "false_contradiction": {
            "count": false_contradiction,
            "rate": round(false_contradiction / len(pairs), 4),
        },
        "abstention": {
            "coverage": round(1 - len(abstained) / len(pairs), 4),
            "selective_accuracy": _mean_ci([1.0 if g == p else 0.0 for g, p in decided])
            if decided else None,
        },
    }


# --------------------------------------------------------------- claim side


def claim_metrics(rows: list[dict]) -> dict:
    """Is this sentence worth auditing at all — measured against the human answer."""
    labelled = [r for r in rows if (r["labels"].get("is_claim") or "") in {"yes", "no", "unsure"}]
    if not labelled:
        return {"rows": 0}
    counts = Counter(r["labels"]["is_claim"] for r in labelled)
    # Every row in a session reached the queue, so "predicted claim" is true for
    # all of them: precision is what this measures, recall needs negatives the
    # extractor rejected (RQ1's 100-sentence set).
    yes = counts.get("yes", 0)
    return {
        "rows": len(labelled),
        "queue_precision": _mean_ci(
            [1.0 if r["labels"]["is_claim"] == "yes" else 0.0 for r in labelled]
        ),
        "by_label": dict(counts),
        "note": (
            f"{yes}/{len(labelled)} hàng trong hàng đợi thật sự là tuyên bố môi trường. "
            "Đây là precision của hàng đợi; recall cần bộ câu có cả lớp âm (RQ1)."
        ),
    }


# --------------------------------------------------------------- leakage check


def split_report(rows: list[dict]) -> dict:
    """A company on both sides of a split makes every number above meaningless."""
    by_company: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        company = row.get("company_id") or row.get("ticker") or "?"
        by_company[company].add(row.get("split") or "unassigned")
    straddling = {c: sorted(s) for c, s in by_company.items() if len(s) > 1}
    return {
        "companies": len(by_company),
        "by_split": dict(Counter(r.get("split") or "unassigned" for r in rows)),
        "companies_in_more_than_one_split": straddling,
    }


# ------------------------------------------------------------------- helpers


def _mean_ci(values: list[float], samples: int = 2000) -> dict:
    """Mean with a bootstrap interval, because n here is small and will stay small."""
    if not values:
        return {"mean": None, "n": 0}
    mean = sum(values) / len(values)
    if len(values) < 3:
        return {"mean": round(mean, 4), "n": len(values), "ci95": None,
                "note": "quá ít mẫu để ước lượng khoảng tin cậy"}
    rng = random.Random(0)
    means = sorted(
        sum(rng.choice(values) for _ in values) / len(values) for _ in range(samples)
    )
    low = means[int(0.025 * samples)]
    high = means[int(0.975 * samples)]
    return {"mean": round(mean, 4), "n": len(values), "ci95": [round(low, 4), round(high, 4)]}


def _fmt(metric: dict | None) -> str:
    if not metric or metric.get("mean") is None:
        return "—"
    text = f"{metric['mean']:.3f}"
    if metric.get("ci95"):
        text += f" [{metric['ci95'][0]:.3f}–{metric['ci95'][1]:.3f}]"
    return f"{text} (n={metric['n']})"


# -------------------------------------------------------------------- report


def render(report: dict) -> list[str]:
    lines = [
        f"# Đánh giá trên gold — {report['date']}",
        "",
        f"Phiên gán nhãn: {report['sessions']} · hàng: {report['rows_total']} · "
        f"**đã trọng tài: {report['rows_adjudicated']}**",
        "",
    ]
    if not report["rows_adjudicated"]:
        lines += [
            "> **Chưa có hàng nào được trọng tài.** Khung đo đã dựng xong và chạy được; "
            "không có con số nào được tính, vì không có gì để tính. "
            "Đây là trạng thái đúng, không phải lỗi.",
            "",
            "Việc cần làm: `python tools/label_session.py sample --name <tên>` rồi gán nhãn; "
            "mỗi hàng cần `labels.labeler`, `labels.verdict` và `labels.evidence`.",
            "",
        ]

    split = report["splits"]
    lines += [
        "## Chia tập",
        "",
        f"- Doanh nghiệp: {split['companies']} · phân bố: `{split['by_split']}`",
    ]
    straddling = split["companies_in_more_than_one_split"]
    lines.append(
        f"- ⚠️ **Doanh nghiệp nằm ở nhiều split: {straddling}** — mọi con số bên dưới "
        "không dùng được cho tới khi xử lý xong."
        if straddling else
        "- ✅ Không doanh nghiệp nào nằm ở hai split."
    )

    retrieval = report["retrieval"]
    lines += ["", "## 1. Truy xuất — bằng chứng đúng có nằm trong top-k không", ""]
    if not retrieval["rows"]:
        lines.append("Chưa có hàng nào gán nhãn bằng chứng.")
    else:
        lines += [
            "> Chấm trên **thứ hạng đã lưu trong phiên gán nhãn** — tức là bộ truy xuất "
            "tại thời điểm đó, không nhất thiết là bộ trong repo hôm nay.",
            "",
            "| Chỉ số | Giá trị [KTC 95%] |",
            "| --- | --- |",
        ]
        for k in KS:
            lines.append(f"| Recall@{k} | {_fmt(retrieval['recall_at'][f'@{k}'])} |")
        lines.append(f"| MRR | {_fmt(retrieval['mrr'])} |")
        lines.append(f"| nDCG@10 | {_fmt(retrieval['ndcg_at_10'])} |")

    verification = report["verification"]
    lines += ["", "## 2. Kiểm chứng — cho đúng bằng chứng, verdict có đúng không", ""]
    if not verification["rows"]:
        lines.append("Chưa có hàng nào có verdict đã trọng tài.")
    else:
        lines += [
            f"- Độ chính xác: {_fmt(verification['accuracy'])} · macro-F1: {verification['macro_f1']}",
            f"- **Mâu thuẫn sai: {verification['false_contradiction']['count']} "
            f"({verification['false_contradiction']['rate'] * 100:.1f}%)** — sai lầm hệ thống "
            "này quan tâm nhất, báo riêng, không trung bình hoá",
            f"- Abstain: phủ {verification['abstention']['coverage'] * 100:.1f}% · "
            f"độ chính xác trên phần đã quyết: {_fmt(verification['abstention']['selective_accuracy'])}",
            "",
            "| Verdict | P | R | F1 | n |",
            "| --- | --- | --- | --- | ---: |",
        ]
        for label, value in verification["per_class"].items():
            lines.append(
                f"| {label} | {value['precision']:.3f} | {value['recall']:.3f} | "
                f"{value['f1']:.3f} | {value['support']} |"
            )

    claims = report["claims"]
    lines += ["", "## 3. Hàng đợi — bao nhiêu phần trăm thật sự là tuyên bố", ""]
    lines.append(
        f"- {_fmt(claims['queue_precision'])} · phân bố nhãn: `{claims['by_label']}`\n- {claims['note']}"
        if claims["rows"] else "Chưa có hàng nào gán nhãn `is_claim`."
    )
    lines += [
        "",
        "---",
        "",
        "Truy xuất hỏng → sửa truy xuất. Truy xuất đúng mà verdict sai → sửa verifier. "
        "Một chỉ số end-to-end duy nhất không phân biệt được hai việc đó "
        "(`docs/00-project/ARCHITECTURE_INVARIANTS.md`).",
    ]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", nargs="*", default=None)
    parser.add_argument("--split", default=None)
    parser.add_argument("--no-verifier", action="store_true",
                        help="bỏ qua phần chạy verifier (nhanh, chỉ đo truy xuất)")
    args = parser.parse_args()

    paths = [Path(p) for p in args.sessions] if args.sessions else sorted(SESSIONS.glob("*.jsonl"))
    rows = load_rows(paths, args.split)
    decided = adjudicated(rows)

    if args.no_verifier or not decided:
        verification = {"rows": 0}
    else:
        from quantum_gw.settings import load_settings
        settings = load_settings("configs/default.yaml")
        settings.runs_dir = str(ROOT / ".quantum" / "eval_runs")
        verification = verification_metrics(decided, settings)

    report = {
        "date": dt.date.today().isoformat(),
        "sessions": [p.name for p in paths],
        "rows_total": len(rows),
        "rows_adjudicated": len(decided),
        "splits": split_report(rows),
        "retrieval": retrieval_metrics(decided),
        "verification": verification,
        "claims": claim_metrics(decided) if decided else {"rows": 0},
    }

    OUT_DIR.mkdir(exist_ok=True)
    stem = f"evaluation_{report['date']}" + (f"_{args.split}" if args.split else "")
    (OUT_DIR / f"{stem}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = render(report)
    (OUT_DIR / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten: benchmark/{stem}.md · benchmark/{stem}.json")


if __name__ == "__main__":
    main()
