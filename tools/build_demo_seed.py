"""Copy chosen saved runs, and the documents they cite, into deploy/seed/ for a deployed prototype.

A jury opening the prototype should see finished analyses at once (Hòa Phát takes about 2.5 minutes
on a small server) and be able to open every cited page. This copies, for each run id given:
  .quantum/runs/<run_id>/                    -> deploy/seed/runs/<run_id>/
  every document the run cites (index rows) -> deploy/seed/documents/index.jsonl
  their stored files                        -> deploy/seed/documents/blobs/<sha[:2]>/<sha><ext>
deploy/entrypoint.sh copies the seed into the container's store on first start; nothing is overwritten.

Usage (repository root):
  .venv/Scripts/python.exe -I tools/build_demo_seed.py <run_id> [<run_id> ...] [--label "<run_id>=Nhãn hiển thị" ...]
  .venv/Scripts/python.exe -I tools/build_demo_seed.py --list          # recent runs with labels
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / ".quantum" / "runs"
DOCS = ROOT / ".quantum" / "documents"
SEED = ROOT / "deploy" / "seed"
# Runs made by data/real_cases/scripts/run_case.py read their PDFs straight from here, so their
# documents never entered the upload store; the parser's doc_id is stable_id(resolved path, name).
ORIGINALS = ROOT / "data" / "real_cases" / "sources" / "originals"


def originals_by_doc_id() -> dict[str, Path]:
    sys.path.insert(0, str(ROOT / "src"))
    from quantum_gw.utils.text import stable_id

    return {stable_id(str(f.resolve()), f.name): f for f in ORIGINALS.glob("*") if f.is_file()}


def doc_ids_of(result: dict) -> set[str]:
    ids = set()
    for v in result.get("verifications", []):
        ids.add(v["claim"].get("source_doc_id"))
        for e in v.get("evidence", []):
            ids.add(e.get("doc_id"))
    for d in result.get("manifest", {}).get("documents", []) or []:
        if isinstance(d, dict):
            ids.add(d.get("doc_id"))
    return {i for i in ids if i}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--label", action="append", default=[], help='"<run_id>=Nhãn hiển thị" (lặp lại được)')
    args = ap.parse_args()
    if args.list:
        rows = []
        for d in RUNS.iterdir():
            m = d / "manifest.json"
            if m.exists():
                man = json.loads(m.read_text(encoding="utf-8"))
                lf = d / "label.json"
                label = json.loads(lf.read_text(encoding="utf-8")).get("label", "") if lf.exists() else ""
                rows.append((man.get("created_at", ""), d.name, label))
        for created, rid, label in sorted(rows)[-40:]:
            print(created[:19], rid, label)
        return
    labels = dict(item.split("=", 1) for item in args.label if "=" in item)
    index = {}
    if (DOCS / "index.jsonl").exists():
        for line in (DOCS / "index.jsonl").read_text(encoding="utf-8").split("\n"):
            if line.strip():
                row = json.loads(line)
                index.setdefault(row["doc_id"], row)
    (SEED / "runs").mkdir(parents=True, exist_ok=True)
    (SEED / "documents" / "blobs").mkdir(parents=True, exist_ok=True)
    rows_out, missing, total = {}, set(), 0
    originals = originals_by_doc_id()
    for rid in args.runs:
        src = RUNS / rid
        if not (src / "result.json").exists():
            raise SystemExit(f"Không thấy phiên {rid} trong {RUNS}")
        dst = SEED / "runs" / rid
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        if rid in labels:
            (dst / "label.json").write_text(json.dumps({"label": labels[rid]}, ensure_ascii=False), encoding="utf-8")
        result = json.loads((src / "result.json").read_text(encoding="utf-8"))
        for doc_id in doc_ids_of(result):
            row = index.get(doc_id)
            if row is None and doc_id in originals:
                f = originals[doc_id]
                data = f.read_bytes()
                row = {"doc_id": doc_id, "sha256": hashlib.sha256(data).hexdigest(), "name": f.name,
                       "path": str(f), "content_type": mimetypes.guess_type(f.name)[0] or "application/octet-stream",
                       "bytes": len(data)}
            if row is None:
                missing.add(doc_id)
                continue
            raw = str(row["path"]).replace("\\", "/")
            suffix = Path(raw).suffix.lower() or ".bin"
            blob = Path(row["path"])
            if not blob.is_file():
                blob = DOCS / "blobs" / row["sha256"][:2] / f"{row['sha256']}{suffix}"
            if not blob.is_file():
                missing.add(doc_id)
                continue
            out = SEED / "documents" / "blobs" / row["sha256"][:2] / f"{row['sha256']}{suffix}"
            out.parent.mkdir(parents=True, exist_ok=True)
            if not out.exists():
                shutil.copy2(blob, out)
                total += out.stat().st_size
            rows_out[doc_id] = {**row, "path": f"blobs/{row['sha256'][:2]}/{row['sha256']}{suffix}"}
    existing = {}
    idx = SEED / "documents" / "index.jsonl"
    if idx.exists():
        for line in idx.read_text(encoding="utf-8").split("\n"):
            if line.strip():
                r = json.loads(line)
                existing[r["doc_id"]] = r
    existing.update(rows_out)
    idx.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in existing.values()), encoding="utf-8")
    print(f"Đã chép {len(args.runs)} phiên, {len(rows_out)} tài liệu ({total / 1e6:.1f} MB mới) vào {SEED}")
    if missing:
        print(f"Không tìm thấy tệp gốc của {len(missing)} tài liệu (trình xem trang sẽ báo thiếu): {sorted(missing)[:5]}")


if __name__ == "__main__":
    main()
