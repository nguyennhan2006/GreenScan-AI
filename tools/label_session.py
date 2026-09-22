#!/usr/bin/env python3
"""Gold-set labelling sessions over the crawl corpus.

The annotation queue (`data/crawl/vn30/curated/annotation_priority.jsonl`)
holds claim *candidates*; `annotation_pairs.jsonl` holds the top retrieved
evidence for each. This tool turns a slice of that into a session file a
human fills in, and prints it as a reading sheet.

    python tools/label_session.py sample --n 10 --name trial01 [--seed 7]
        -> data/gold/sessions/<date>_<name>.jsonl  (labels empty)

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
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CRAWL = REPO / "data" / "crawl" / "vn30"
SESSIONS = REPO / "data" / "gold" / "sessions"

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


def cmd_sample(args) -> None:
    claims, evidence, pairs = load_corpus()
    pool = [
        c for c in claims.values()
        if c["split"] in set(args.splits.split(","))
        and (c["has_number"] or not args.numeric_only)
        and c["candidate_id"] in pairs
    ]
    pool.sort(key=lambda c: -c["informativeness"])
    # Take the informative head, then spread across companies so one issuer
    # (tra holds 30% of the queue) does not dominate a 10-claim session.
    head = pool[: max(args.n * 8, 80)]
    rng = random.Random(args.seed)
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
        for p in pairs[c["candidate_id"]][: args.k]:
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
    s.add_argument("--splits", default="train,dev", help="comma list; keep test/future for hold-out")
    s.add_argument("--numeric-only", action="store_true")
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
