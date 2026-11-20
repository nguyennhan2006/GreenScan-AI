"""Compare a person's labels on the 50-sentence kit with the merged Sonnet labels (and each Sonnet labeller).

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_claims_v1/human/score_human.py <filled .xlsx or .csv> [labeller name]
writes human/human_vs_sonnet.json and prints Cohen's kappa per field; disagreements are listed for discussion.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from score_labels import FIELDS, kappa  # noqa: E402


def read(path: Path) -> dict[str, dict]:
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True).active
        rows = list(ws.iter_rows(values_only=True))
        header = [str(h) for h in rows[0]]
        data = [dict(zip(header, r)) for r in rows[1:]]
    else:
        with path.open(encoding="utf-8-sig") as fh:
            data = list(csv.DictReader(fh))
    out = {}
    for r in data:
        if r.get("item_id"):
            out[r["item_id"]] = {f: (str(r.get(f) or "").strip().lower()) for f in FIELDS} | {"note": r.get("note") or ""}
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    human = read(Path(sys.argv[1]))
    who = sys.argv[2] if len(sys.argv) > 2 else "human"
    gold = {json.loads(line)["item_id"]: json.loads(line) for line in (BASE / "gold.jsonl").open(encoding="utf-8")}
    la = {json.loads(line)["item_id"]: json.loads(line) for line in (BASE / "labels" / "labels_sonnet-A.jsonl").open(encoding="utf-8")}
    lb = {json.loads(line)["item_id"]: json.loads(line) for line in (BASE / "labels" / "labels_sonnet-B.jsonl").open(encoding="utf-8")}
    ids = [i for i, r in human.items() if r["is_claim"] in ("yes", "no")]
    missing = [i for i, r in human.items() if r["is_claim"] not in ("yes", "no")]
    report = {"labeller": who, "n_labelled": len(ids), "n_unlabelled": len(missing), "kappa": {}, "disagreements": []}
    for f in FIELDS:
        pairs = [(human[i][f], gold[i][f]) for i in ids if human[i][f]]
        report["kappa"][f] = {
            "vs_merged": kappa([a for a, _ in pairs], [b for _, b in pairs]),
            "vs_sonnet_A": kappa([human[i][f] for i in ids if human[i][f]], [la[i][f] for i in ids if human[i][f]]),
            "vs_sonnet_B": kappa([human[i][f] for i in ids if human[i][f]], [lb[i][f] for i in ids if human[i][f]]),
            "n": len(pairs),
        }
    for i in ids:
        diff = {f: {"human": human[i][f], "merged": gold[i][f]} for f in FIELDS if human[i][f] and human[i][f] != gold[i][f]}
        if diff:
            report["disagreements"].append({"item_id": i, "text": gold[i]["text"][:200], "differ": diff, "note": human[i]["note"]})
    (HERE / "human_vs_sonnet.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{who}: {len(ids)} labelled, {len(missing)} empty")
    for f, k in report["kappa"].items():
        print(f"  {f:26s} kappa vs merged {k['vs_merged']}  (A {k['vs_sonnet_A']}, B {k['vs_sonnet_B']}, n={k['n']})")
    print(f"  {len(report['disagreements'])} sentences differ from the merged labels -> human_vs_sonnet.json")


if __name__ == "__main__":
    main()
