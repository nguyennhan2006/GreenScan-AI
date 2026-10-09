#!/usr/bin/env python3
"""Gold-set labelling sessions over the crawl corpus.

The annotation queue (`data/crawl/vn30/curated/annotation_priority.jsonl`)
holds claim *candidates*; `annotation_pairs.jsonl` holds the top retrieved
evidence for each. This tool turns a slice of that into a session file a
human fills in, and prints it as a reading sheet.

    python tools/label_session.py sample --n 10 --name trial01 [--seed 7]
        -> data/gold/sessions/<date>_<name>.jsonl  (labels empty)

       By default the sample is on-topic (COLLECTION_PLAN_v2 §5): a claim must
       name an environmental subject, evidence published after the claim and
       evidence that merely repeats the claim are dropped, and claims already in
       an earlier session are not drawn again. `--raw` restores the old
       informativeness-ranked draw, which was 74% off-topic.

    python tools/label_session.py show data/gold/sessions/<file>.jsonl
        -> reading sheet: claim + evidence candidates + what to decide

    python tools/label_session.py set <session> <idx> key=value ...
        -> records one label field; `attrs.metric=present`,
           `evidence.<rank>=contradicts`, `verdict=CONTRADICTED`, ...

    python tools/label_session.py stats <session>
        -> coverage and label distribution

Label semantics (see docs/01-domain-audit/MANUAL_SCORING_RUBRIC.md):

    is_claim      yes | no | unsure     -- a heading, ToC line, boilerplate,
                                           or a non-environmental sentence is `no`
    claim_type    one of configs/taxonomy.yaml claim_types
    attrs.*       present | partial | missing | na
                  metric, value_unit, period, baseline, scope
                  (`na` for baseline when the claim states no change/target)
    evidence.<r>  supports | partial | contradicts | context | not_relevant
    verdict       SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED |
                  CONTRADICTED | INSUFFICIENT_EVIDENCE
    notes         free text

The label is *evidence sufficiency for this claim*, never "company is
greenwashing". A control company is not greenwashing because data is missing.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CRAWL = REPO / "data" / "crawl" / "vn30"
SESSIONS = REPO / "data" / "gold" / "sessions"
# Per-labeller copies live one level down so evaluate_gold.py, which reads only
# the top level, never counts the same claim twice.
LABELER_COPIES = SESSIONS / "labelers"

# Taxonomy terms that do not make a sentence environmental on their own:
# "hệ sinh thái bán lẻ" and "sử dụng vốn" are business language, and short
# English stems like "saf" match "safety".
NOT_ON_TOPIC = {"hệ sinh thái", "ecosystem", "sử dụng vốn", "saf", "offset", "habitat"}
EXTRA_ON_TOPIC = [
    "nước thải", "tiêu thụ nước", "sử dụng nước", "khí thải", "rác thải", "năng lượng",
    "điện năng", "iso 14001", "iso 14064", "nhựa",
]

ATTRS = ["metric", "value_unit", "period", "baseline", "scope"]
ATTR_VALUES = {"present", "partial", "missing", "na"}
RELATIONS = {"supports", "partial", "contradicts", "context", "not_relevant"}
VERDICTS = {
    "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
}
IS_CLAIM = {"yes", "no", "unsure"}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_corpus():
    claims = {r["candidate_id"]: r for r in read_jsonl(CRAWL / "curated" / "annotation_priority.jsonl")}
    evidence = {r["candidate_id"]: r for r in read_jsonl(CRAWL / "normalized" / "evidence_candidates.jsonl")}
    pairs = defaultdict(list)
    for p in read_jsonl(CRAWL / "normalized" / "annotation_pairs.jsonl"):
        if p["claim_id"] in claims:
            pairs[p["claim_id"]].append(p)
    for lst in pairs.values():
        lst.sort(key=lambda p: p["rank"])
    return claims, evidence, pairs


def blank_labels() -> dict:
    return {
        "is_claim": None,
        "claim_type": None,
        "attrs": {a: None for a in ATTRS},
        "evidence": {},
        "verdict": None,
        "notes": "",
        "labeler": None,
        "labeled_at": None,
    }


def on_topic_terms() -> list[str]:
    """Environmental subject terms: the specific claim types, never the generic bucket."""
    tax = yaml.safe_load((REPO / "configs" / "taxonomy.yaml").read_text(encoding="utf-8"))
    terms = set(EXTRA_ON_TOPIC)
    for name, spec in tax["claim_types"].items():
        if name in {"generic_sustainability", "esg_process_integration"}:
            continue
        terms.update(t.lower() for t in spec.get("vi", []) + spec.get("en", []))
    return sorted(terms - NOT_ON_TOPIC)


def is_on_topic(text: str, terms: list[str]) -> bool:
    low = text.lower()
    # Left word boundary only, so stems such as "recycl" still match.
    return any(re.search(r"(?<!\w)" + re.escape(t), low) for t in terms)


def _squash(text: str) -> str:
    return " ".join(text.lower().split())


def clean_candidates(claim: dict, claim_pairs: list[dict], evidence: dict) -> list[dict]:
    """Drop evidence a labeller cannot use (ISSUES_REGISTER C5).

    Evidence that contains the claim sentence is the claim, not support for it;
    evidence published after the claim cannot have backed it when it was made.
    Retriever order is kept, so retrieval metrics still score the retriever.
    """
    head = _squash(claim["text"])[:80]
    year = claim.get("publication_year")
    kept = []
    for p in claim_pairs:
        e = evidence.get(p["evidence_id"])
        if not e:
            continue
        if head and head in _squash(e["text"]):
            continue
        if year and e.get("publication_year") and e["publication_year"] > year:
            continue
        kept.append(p)
    return kept


def already_sampled() -> set[str]:
    seen: set[str] = set()
    for path in list(SESSIONS.glob("*.jsonl")) + list(LABELER_COPIES.glob("*.jsonl")):
        seen.update(r["claim_id"] for r in read_jsonl(path))
    return seen


def cmd_sample(args) -> None:
    claims, evidence, pairs = load_corpus()
    splits = set(args.splits.split(","))
    pool = [
        c for c in claims.values()
        if c["split"] in splits
        and (c["has_number"] or not args.numeric_only)
        and c["candidate_id"] in pairs
    ]
    rng = random.Random(args.seed)
    if args.raw:
        pool.sort(key=lambda c: -c["informativeness"])
        # Take the informative head, then spread across companies so one issuer
        # (tra holds 30% of the queue) does not dominate a 10-claim session.
        head = pool[: max(args.n * 8, 80)]
        candidates = {c["candidate_id"]: pairs[c["candidate_id"]] for c in head}
    else:
        terms = on_topic_terms()
        seen = set() if args.allow_repeat else already_sampled()
        head, candidates = [], {}
        for c in pool:
            if c["candidate_id"] in seen or not is_on_topic(c["text"], terms):
                continue
            kept = clean_candidates(c, pairs[c["candidate_id"]], evidence)
            if len(kept) >= args.min_evidence:
                head.append(c)
                candidates[c["candidate_id"]] = kept
        # Informativeness ranks by number density, which is what made the old
        # queue off-topic; the on-topic draw is uniform within the pool.
        head.sort(key=lambda c: c["candidate_id"])
        print(f"on-topic pool: {len(head)} claims with >= {args.min_evidence} usable evidence")
    rng.shuffle(head)
    by_company = defaultdict(list)
    for c in head:
        by_company[c["company_id"]].append(c)
    picked, companies = [], sorted(by_company)
    while len(picked) < args.n and any(by_company.values()):
        for comp in companies:
            if by_company[comp] and len(picked) < args.n:
                picked.append(by_company[comp].pop())

    rows = []
    for i, c in enumerate(picked):
        ev_rows = []
        for p in candidates[c["candidate_id"]][: args.k]:
            e = evidence.get(p["evidence_id"])
            if not e:
                continue
            ev_rows.append({
                "rank": p["rank"],
                "evidence_id": e["candidate_id"],
                "retrieval_score": p["retrieval_score"],
                "document_type": e["document_type"],
                "publication_year": e["publication_year"],
                "unit_type": e["unit_type"],
                "unit_index": e["unit_index"],
                "text": e["text"],
            })
        rows.append({
            "idx": i,
            "claim_id": c["candidate_id"],
            "company_id": c["company_id"],
            "ticker": c["ticker"],
            "document_id": c["document_id"],
            "document_type": c["document_type"],
            "publication_year": c["publication_year"],
            "unit_type": c["unit_type"],
            "unit_index": c["unit_index"],
            "split": c["split"],
            "has_number": c["has_number"],
            "informativeness": c["informativeness"],
            "text": c["text"],
            "evidence_candidates": ev_rows,
            "sampling": "raw" if args.raw else "on-topic-v2",
            "labels": blank_labels(),
        })
    out = SESSIONS / f"{date.today().isoformat()}_{args.name}.jsonl"
    write_jsonl(out, rows)
    print(f"wrote {len(rows)} claims -> {out}")
    print("companies:", dict(Counter(r['company_id'] for r in rows)))


def cmd_show(args) -> None:
    rows = list(read_jsonl(Path(args.session)))
    sel = set(args.idx) if args.idx else None
    for r in rows:
        if sel is not None and r["idx"] not in sel:
            continue
        lab = r["labels"]
        print("=" * 88)
        print(f"[{r['idx']}] {r['ticker']} · {r['document_type']} {r['publication_year']} · "
              f"{r['unit_type']} {r['unit_index']} · split={r['split']} · info={r['informativeness']}")
        print(f"CLAIM: {r['text']}")
        print("-" * 88)
        for e in r["evidence_candidates"]:
            tag = lab["evidence"].get(str(e["rank"]), "·")
            text = e["text"].replace("\n", " ")
            if len(text) > args.width:
                text = text[: args.width] + "…"
            print(f"  E{e['rank']} [{tag}] {e['document_type']} {e['publication_year']} "
                  f"{e['unit_type']} {e['unit_index']} (score {e['retrieval_score']:.2f})")
            print(f"     {text}")
        if any(v for v in (lab["is_claim"], lab["verdict"])) or any(lab["attrs"].values()):
            print("-" * 88)
            print(f"  is_claim={lab['is_claim']} type={lab['claim_type']} verdict={lab['verdict']}")
            print(f"  attrs={lab['attrs']}")
            if lab["notes"]:
                print(f"  notes: {lab['notes']}")
    print("=" * 88)


def cmd_set(args) -> None:
    path = Path(args.session)
    rows = list(read_jsonl(path))
    row = next((r for r in rows if r["idx"] == args.idx), None)
    if row is None:
        sys.exit(f"no claim idx {args.idx}")
    lab = row["labels"]
    for item in args.assign:
        key, _, value = item.partition("=")
        value = value.strip()
        if key == "is_claim":
            assert value in IS_CLAIM, f"is_claim must be {IS_CLAIM}"
            lab["is_claim"] = value
        elif key == "claim_type":
            lab["claim_type"] = value
        elif key.startswith("attrs."):
            a = key.split(".", 1)[1]
            assert a in ATTRS and value in ATTR_VALUES, f"attrs.{a}={value} invalid"
            lab["attrs"][a] = value
        elif key.startswith("evidence."):
            rank = key.split(".", 1)[1]
            assert value in RELATIONS, f"relation must be {RELATIONS}"
            lab["evidence"][rank] = value
        elif key == "verdict":
            assert value in VERDICTS, f"verdict must be {VERDICTS}"
            lab["verdict"] = value
        elif key == "notes":
            lab["notes"] = value
        else:
            sys.exit(f"unknown key {key}")
    lab["labeler"] = args.labeler
    lab["labeled_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    write_jsonl(path, rows)
    print(f"[{args.idx}] {row['ticker']}: is_claim={lab['is_claim']} verdict={lab['verdict']} "
          f"attrs={lab['attrs']} evidence={lab['evidence']}")


def cmd_stats(args) -> None:
    rows = list(read_jsonl(Path(args.session)))
    done = [r for r in rows if r["labels"]["is_claim"]]
    print(f"{len(done)}/{len(rows)} labelled")
    print("is_claim:", dict(Counter(r["labels"]["is_claim"] for r in done)))
    real = [r for r in done if r["labels"]["is_claim"] == "yes"]
    print("verdict:", dict(Counter(r["labels"]["verdict"] for r in real)))
    print("claim_type:", dict(Counter(r["labels"]["claim_type"] for r in real)))
    for a in ATTRS:
        print(f"attr {a:10s}:", dict(Counter(r["labels"]["attrs"][a] for r in real)))
    rel = Counter(v for r in done for v in r["labels"]["evidence"].values())
    print("evidence relations:", dict(rel))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--k", type=int, default=5, help="evidence candidates per claim")
    s.add_argument("--name", required=True)
    s.add_argument("--seed", type=int, default=7)
    # The verifier is rule-based, so labelling the held-out companies trains
    # nothing; it is what makes `evaluate_gold.py --split test` possible at all.
    # `review` rows have no reliable year, so the evidence-year filter cannot run.
    s.add_argument("--splits", default="train,dev,test,future_holdout",
                   help="comma list; the split is kept on every row")
    s.add_argument("--numeric-only", action="store_true")
    s.add_argument("--min-evidence", type=int, default=3,
                   help="usable evidence a claim needs to be drawn")
    s.add_argument("--allow-repeat", action="store_true",
                   help="allow claims that are already in an earlier session")
    s.add_argument("--raw", action="store_true",
                   help="old informativeness-ranked draw, no topic or evidence filter")
    s.set_defaults(func=cmd_sample)

    s = sub.add_parser("show")
    s.add_argument("session")
    s.add_argument("--idx", type=int, nargs="*")
    s.add_argument("--width", type=int, default=420)
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("set")
    s.add_argument("session")
    s.add_argument("idx", type=int)
    s.add_argument("assign", nargs="+", help="key=value")
    s.add_argument("--labeler", default="unknown")
    s.set_defaults(func=cmd_set)

    s = sub.add_parser("stats")
    s.add_argument("session")
    s.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
