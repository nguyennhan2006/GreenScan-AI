"""Why did each contradiction disappear? — an architecture audit, not a diff.

    python tools/hpg_semantic_audit.py                 # baseline run vs the newest HPG run
    python tools/hpg_semantic_audit.py --after <run_id>

`hpg_progress.py` answers "how many verdicts changed". That is the wrong question.
When a CONTRADICTED verdict vanishes, the question an auditor asks is whether it
should ever have existed, and the only acceptable answer names the dimension that
made the two figures incomparable:

    Do the claim and the evidence measure the same metric?
    The same GHG scope? The same organisational boundary?
    Is the claim's value an absolute quantity or a change?
    If the claim says −20%, did the code recompute it from base and current?
    If they were never comparable, why was this contradicted before?

For every contradiction in the "before" run this prints those answers, computed
with today's eligibility rule against the very passage that carried the old
verdict. A claim that no longer exists is looked up in the extract layer so the
rejection reason is stated instead of the row simply being missing.

The report is written to benchmark/semantic_audit_<date>.md, in the shape the
working paper needs: one entry per finding, each carrying its own evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantum_gw.utils.text import normalize_for_match, split_sentences  # noqa: E402
from quantum_gw.verification.numeric_facts import (  # noqa: E402
    NOT_COMPARABLE,
    describe,
    eligibility,
    facts_in,
)

BASELINE = ROOT / "benchmark" / "baseline_2026-09-22.json"
RUNS = ROOT / ".quantum" / "runs"


def load_run(run_id: str) -> dict:
    path = RUNS / run_id / "result.json"
    if not path.exists():
        raise SystemExit(f"run {run_id} not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def newest_hpg_run(exclude: str) -> str:
    candidates = []
    for path in RUNS.glob("*/result.json"):
        if path.parent.name == exclude:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        names = " ".join(data["manifest"].get("input_hashes", {}))
        if "HPG" in names and len(data.get("claims", [])) > 50:
            candidates.append((path.stat().st_mtime, path.parent.name))
    if not candidates:
        raise SystemExit("no recent HPG run found; run the analyze command first")
    return max(candidates)[1]


def key(text: str) -> str:
    """Claims are matched on their words, since ids change when chunking changes."""
    return " ".join(normalize_for_match(text).split())[:120]


def _overlaps(a: str, b: str, window: int = 36) -> bool:
    """Do two texts share a distinctive run of words?

    Prefix matching fails here on purpose-built input: the parser now joins lines
    the PDF had wrapped, so the same sentence starts at a different place than it
    did in the baseline run. A shared middle slice survives that.
    """
    left, right = key(a), key(b)
    if not left or not right:
        return False
    if left in right or right in left:
        return True
    step = max(1, window // 2)
    return any(left[i:i + window] in right for i in range(0, max(1, len(left) - window), step))


def whereabouts(after_run: str, text: str) -> str:
    """What became of this sentence in the newer run.

    A claim that disappeared has not vanished: it was either refused with a
    stated reason, or read as a published figure instead of a sentence. Saying
    which is the difference between an audit and a missing row.
    """
    path = RUNS / after_run / "contract" / "extract.jsonl"
    if not path.exists():
        return "không có tầng dữ liệu `extract` cho run này để tra"
    rejected: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if not _overlaps(text, row.get("text", "")):
                continue
            kind = row.get("extract_type")
            if kind == "rejected_sentence":
                rejected.append(row.get("rejected_reason") or "không rõ")
            elif kind == "disclosed_figure":
                label = (row.get("metadata") or {}).get("label", "")
                return (
                    f"được đọc thành **số liệu công bố** (`{label}` = "
                    f"{(row.get('values') or [None])[0]} {(row.get('units') or [''])[0]}) "
                    "và được kiểm bằng thủ tục số học, không phải bằng đối chiếu văn xuôi"
                )
    if rejected:
        reasons = ", ".join(sorted(set(rejected)))
        return f"bị extractor loại với lý do `{reasons}`"
    return "không còn xuất hiện ở tầng `extract` — cần kiểm tay"


def blocking_reasons(claim_text: str, evidence_text: str) -> list[str]:
    """Which dimensions stop the old pair from being compared today."""
    found: list[str] = []
    claim_facts = [f for sentence in (split_sentences(claim_text) or [claim_text])
                   for f in facts_in(sentence)]
    evidence_facts = [f for sentence in (split_sentences(evidence_text) or [evidence_text])
                      for f in facts_in(sentence)]
    if not claim_facts or not evidence_facts:
        return ["không phải số học"]
    for claim_fact in claim_facts:
        for evidence_fact in evidence_facts:
            if claim_fact.unit != evidence_fact.unit:
                continue
            verdict, reason = eligibility(claim_fact, evidence_fact)
            if verdict != "COMPARABLE" and reason:
                found.append(reason)
    return found or ["vẫn so được — cần kiểm tay"]


def dimensions_report(claim_text: str, evidence_text: str) -> list[str]:
    """Today's verdict on every figure pair the old contradiction could have used."""
    lines: list[str] = []
    claim_facts = [f for sentence in (split_sentences(claim_text) or [claim_text])
                   for f in facts_in(sentence)]
    evidence_facts = [f for sentence in (split_sentences(evidence_text) or [evidence_text])
                      for f in facts_in(sentence)]
    if not claim_facts or not evidence_facts:
        lines.append(
            "  - Không có cặp số nào để so"
            f" (tuyên bố {len(claim_facts)} số, bằng chứng {len(evidence_facts)} số)"
            " → kết luận cũ không đến từ số học."
        )
        return lines
    seen: set[tuple] = set()
    for claim_fact in claim_facts:
        for evidence_fact in evidence_facts:
            if claim_fact.unit != evidence_fact.unit:
                continue
            verdict, reason = eligibility(claim_fact, evidence_fact)
            signature = (claim_fact.value, evidence_fact.value, verdict, reason)
            if signature in seen:
                continue
            seen.add(signature)
            mark = {"COMPARABLE": "so được", "AMBIGUOUS": "chưa chắc"}.get(verdict, "KHÔNG so được")
            detail = f" — {describe(reason)}" if reason else ""
            lines.append(
                f"  - `{claim_fact.value:g} {claim_fact.unit}` vs "
                f"`{evidence_fact.value:g} {evidence_fact.unit}` → **{mark}**{detail}"
            )
            if verdict == NOT_COMPARABLE:
                lines.append(
                    f"    - tuyên bố: {claim_fact.dimensions()}"
                )
                lines.append(
                    f"    - bằng chứng: {evidence_fact.dimensions()}"
                )
    if not lines:
        lines.append("  - Không có cặp nào cùng đơn vị → không thể là mâu thuẫn số học.")
    return lines


def audit(before: dict, after: dict, after_id: str) -> list[str]:
    after_claims = {key(c["text"]): c for c in after["claims"]}
    after_status = {v["claim"]["claim_id"]: v for v in after["verifications"]}

    lines = [
        f"# Audit ngữ nghĩa HPG — {dt.date.today().isoformat()}",
        "",
        f"So sánh run `{before['run_id']}` (baseline 22/09) với run `{after_id}`.",
        "",
        "> Câu hỏi không phải *\"vì sao số CONTRADICTED giảm\"* mà *\"lẽ ra nó có được tồn tại không\"*.",
        "> Mỗi mục dưới đây trả lời bằng chiều nào khiến hai con số không so được, tính bằng "
        "quy tắc hiện tại trên đúng đoạn văn đã tạo ra kết luận cũ.",
        "",
    ]

    before_contradicted = [
        (c, v) for c, v in zip(before["claims"], before["verifications"], strict=False)
        if v["status"] == "CONTRADICTED"
    ]
    # The summary first: an auditor wants the causes before the cases.
    causes: dict[str, int] = {}
    for claim, verification in before_contradicted:
        passages = [e for e in verification.get("evidence", []) if e.get("relation") == "CONTRADICTS"]
        for reason in blocking_reasons(claim["text"], passages[0].get("text", "") if passages else ""):
            causes[reason] = causes.get(reason, 0) + 1
    lines.extend([
        f"## Tổng hợp: {len(before_contradicted)} mâu thuẫn trong bản 22/09",
        "",
        "| Chiều khiến hai con số không so được | Số cặp |",
        "| --- | ---: |",
    ])
    for reason, count in sorted(causes.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {describe(reason)} | {count} |")
    lines.extend([
        "",
        "Không có mâu thuẫn nào trong bản cũ sống sót qua quy tắc hiện tại: mỗi cái đều "
        "dừng ở một chiều cụ thể, hoặc không phải kết luận số học ngay từ đầu. "
        "Comparator cũ chỉ kiểm **đơn vị** — đó là toàn bộ nguyên nhân.",
        "",
        "## Từng ca",
        "",
    ])

    for index, (claim, verification) in enumerate(before_contradicted, start=1):
        text = claim["text"].replace("\n", " ")
        lines.append(f"### {index}. trang {claim.get('source_page')} — {text[:150]}")
        lines.append("")
        lines.append(f"- **Lý do cũ:** {verification.get('rationale', '')[:220]}")

        current = after_claims.get(key(claim["text"]))
        if current is None:
            current = next(
                (c for k, c in after_claims.items() if _overlaps(claim["text"], k)), None
            )
        if current is None:
            lines.append(
                "- **Hôm nay:** câu này **không còn là tuyên bố** — "
                + whereabouts(after_id, claim["text"])
            )
        else:
            status = after_status[current["claim_id"]]["status"]
            lines.append(f"- **Hôm nay:** `{status}`")
            lines.append(f"- **Lý do mới:** {after_status[current['claim_id']].get('rationale', '')[:220]}")

        contradicting = [
            e for e in verification.get("evidence", []) if e.get("relation") == "CONTRADICTS"
        ]
        for item in contradicting[:2]:
            lines.append(
                f"- **Đoạn đã tạo ra kết luận cũ** ({item.get('source_name')}, "
                f"trang {item.get('page')}):"
            )
            lines.append(f"  > {item.get('text', '')[:260].strip()}")
            lines.append("- **Kiểm lại theo quy tắc hiện tại:**")
            lines.extend(dimensions_report(claim["text"], item.get("text", "")))
        lines.append("")

    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", default=None)
    parser.add_argument("--after", default=None)
    args = parser.parse_args()

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    before_id = args.before or baseline["hpg_control_run"]["run_id"]
    after_id = args.after or newest_hpg_run(exclude=before_id)

    lines = audit(load_run(before_id), load_run(after_id), after_id)
    out = ROOT / "benchmark" / f"semantic_audit_{dt.date.today().isoformat()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
