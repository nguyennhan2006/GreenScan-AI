"""Check and produce the raw / clean / extract layers.

    python tools/data_contract.py schema                      # write schemas/data/*.schema.json
    python tools/data_contract.py validate <file.jsonl>       # layer read from the rows
    python tools/data_contract.py validate-run [--latest|<run_id>]
    python tools/data_contract.py migrate-crawl [--limit N]   # data/crawl/vn30/contract/
    python tools/data_contract.py report <dir>                # field coverage per layer

`validate` answers two different questions and keeps them apart:

    invalid    the row does not fit the contract at all (wrong type, unknown
               field, missing a field the model requires) -- a bug in whoever
               wrote it;
    incomplete the row fits but lacks a field its origin requires to be usable
               (a crawled file with no access date cannot be cited) -- a data
               gap, to be fixed by collection, not by code.

Exit code is 1 only for invalid rows: an incomplete corpus is the normal state
of a corpus being built, and the report says how incomplete it is.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pydantic import ValidationError  # noqa: E402

from quantum_gw.data.builders import (  # noqa: E402
    clean_from_crawl,
    extract_from_crawl_candidate,
    raw_from_crawl,
    write_jsonl,
)
from quantum_gw.data.layers import (  # noqa: E402
    CONTRACT_VERSION,
    LAYERS,
    ExtractType,
    missing_required,
)

SCHEMA_DIR = ROOT / "schemas" / "data"
CRAWL = ROOT / "data" / "crawl" / "vn30"


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if line:
                yield number, json.loads(line)


# ---------------------------------------------------------------- schema export


def cmd_schema(args) -> int:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for name, model in LAYERS.items():
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"https://greenscan.local/schemas/data/{name}.schema.json"
        schema["title"] = f"GreenScan {name} layer ({CONTRACT_VERSION})"
        path = SCHEMA_DIR / f"{name}.schema.json"
        path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{path.relative_to(ROOT)}  ({len(schema.get('properties', {}))} fields)")
    return 0


# -------------------------------------------------------------------- validate


def _layer_of(path: Path, row: dict) -> str:
    layer = row.get("layer")
    if layer in LAYERS:
        return layer
    stem = path.stem.lower()
    if stem in LAYERS:
        return stem
    raise SystemExit(f"{path}: cannot tell which layer this file is; no `layer` field")


def validate_file(path: Path) -> dict:
    invalid: list[tuple[int, str]] = []
    incomplete: collections.Counter = collections.Counter()
    layers: collections.Counter = collections.Counter()
    origins: collections.Counter = collections.Counter()
    total = 0
    for number, row in read_jsonl(path):
        total += 1
        layer = _layer_of(path, row)
        layers[layer] += 1
        origins[row.get("origin", "?")] += 1
        try:
            LAYERS[layer].model_validate(row)
        except ValidationError as error:
            first = error.errors()[0]
            invalid.append((number, f"{'.'.join(str(p) for p in first['loc'])}: {first['msg']}"))
            continue
        for field in missing_required(row, layer):
            incomplete[field] += 1
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "rows": total,
        "layers": dict(layers),
        "origins": dict(origins),
        "invalid": invalid,
        "incomplete": dict(incomplete),
    }


def _print_report(report: dict) -> None:
    print(f"\n{report['path']}: {report['rows']} rows {report['layers']} {report['origins']}")
    if report["invalid"]:
        print(f"  INVALID {len(report['invalid'])} row(s) — the writer is wrong:")
        for number, message in report["invalid"][:10]:
            print(f"    line {number}: {message}")
        if len(report["invalid"]) > 10:
            print(f"    ... {len(report['invalid']) - 10} more")
    else:
        print("  valid against the contract")
    if report["incomplete"]:
        print("  incomplete (data gaps, not code bugs):")
        for field, count in sorted(report["incomplete"].items(), key=lambda kv: -kv[1]):
            share = 100 * count / max(report["rows"], 1)
            print(f"    {field:<18} missing in {count} rows ({share:.0f}%)")


def cmd_validate(args) -> int:
    paths = [Path(p) for p in args.paths]
    files = []
    for path in paths:
        files.extend(sorted(path.glob("*.jsonl")) if path.is_dir() else [path])
    failed = False
    for path in files:
        report = validate_file(path)
        _print_report(report)
        failed = failed or bool(report["invalid"])
    return 1 if failed else 0


def cmd_validate_run(args) -> int:
    runs = ROOT / ".quantum" / "runs"
    if args.run_id and args.run_id != "--latest":
        directory = runs / args.run_id / "contract"
    else:
        candidates = sorted(runs.glob("*/contract"), key=lambda p: p.stat().st_mtime)
        if not candidates:
            raise SystemExit("no run has written a contract/ directory yet; run `quantum-agent demo`")
        directory = candidates[-1]
    print(f"run: {directory.parent.name}")
    args.paths = [str(directory)]
    return cmd_validate(args)


# --------------------------------------------------------------- migrate crawl


def cmd_migrate_crawl(args) -> int:
    normalized = CRAWL / "normalized"
    if not normalized.is_dir():
        raise SystemExit(f"{normalized} not found")
    out = CRAWL / "contract"
    version = args.producer_version
    limit = args.limit

    def rows(name: str):
        path = normalized / f"{name}.jsonl"
        if not path.exists():
            return
        for index, (_, row) in enumerate(read_jsonl(path)):
            if limit and index >= limit:
                return
            yield row

    digests: dict[str, str] = {}
    raw_rows = []
    for row in rows("documents"):
        record = raw_from_crawl(row, producer_version=version)
        digests[record.doc_id] = record.sha256
        raw_rows.append(record)
    counts = {"raw": write_jsonl(out / "raw.jsonl", raw_rows)}

    counts["clean"] = write_jsonl(
        out / "clean.jsonl",
        (
            clean_from_crawl(row, producer_version=version, doc_sha256=digests.get(str(row.get("document_id"))))
            for row in rows("chunks")
        ),
    )

    def extracts():
        for row in rows("claim_candidates"):
            yield extract_from_crawl_candidate(row, producer_version=version, extract_type=ExtractType.CLAIM)
        for row in rows("evidence_candidates"):
            yield extract_from_crawl_candidate(
                row, producer_version=version, extract_type=ExtractType.EVIDENCE_CANDIDATE
            )

    counts["extract"] = write_jsonl(out / "extract.jsonl", extracts())
    print(f"written to {out.relative_to(ROOT)}: {counts}")
    args.paths = [str(out)]
    return cmd_validate(args)


# --------------------------------------------------------------------- report


def cmd_report(args) -> int:
    directory = Path(args.directory)
    for path in sorted(directory.glob("*.jsonl")):
        rows = [row for _, row in read_jsonl(path)]
        if not rows:
            continue
        layer = _layer_of(path, rows[0])
        filled: collections.Counter = collections.Counter()
        for row in rows:
            for field, value in row.items():
                if value not in (None, "", [], {}):
                    filled[field] += 1
        print(f"\n{path.name}  ({layer}, {len(rows)} rows) — field coverage")
        for field in LAYERS[layer].model_fields:
            count = filled.get(field, 0)
            bar = "#" * int(20 * count / len(rows))
            print(f"  {field:<22} {100 * count / len(rows):5.1f}% {bar}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("schema", help="write JSON Schema for the three layers").set_defaults(func=cmd_schema)

    p = sub.add_parser("validate", help="validate JSONL files or a directory")
    p.add_argument("paths", nargs="+")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("validate-run", help="validate the layers a run wrote")
    p.add_argument("run_id", nargs="?", default="--latest")
    p.set_defaults(func=cmd_validate_run)

    p = sub.add_parser("migrate-crawl", help="rewrite the VN30 crawl corpus in the contract shape")
    p.add_argument("--limit", type=int, default=0, help="first N rows of each file (smoke test)")
    p.add_argument("--producer-version", default="vn30-crawl-2026-08-07")
    p.set_defaults(func=cmd_migrate_crawl)

    p = sub.add_parser("report", help="field coverage per layer")
    p.add_argument("directory")
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
