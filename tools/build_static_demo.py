"""Bản trình diễn tĩnh của prototype: giao diện thật + phản hồi API đã xuất sẵn, chạy trên Hugging Face static Space (miễn phí).

Usage (thư mục gốc repo):
  .venv/Scripts/python.exe -I tools/build_static_demo.py --out <thư mục> [--demo-store <tmp của run_feedback_demo>]
  C:/Python314/python.exe tools/build_static_demo.py --deploy <user>/<space> --out <thư mục> --skip-build   # đẩy lên

Cách làm: cài các phiên mẫu (deploy/seed) và, nếu có, các phiên của tools/thuyet_minh/run_feedback_demo.py (Ca A có
quyết định soát và tiền lệ, Hòa Phát có bộ quy tắc "ngân hàng xanh") vào một kho tạm; gọi chính máy chủ GreenScan
(FastAPI TestClient) cho mọi endpoint GET mà giao diện dùng; ghi phản hồi ra `static-api/<đường dẫn>.json`; dựng ảnh
mọi trang PDF; chép giao diện đã build với VITE_STATIC=1 (frontend/src/staticApi.js chặn fetch và đọc các tệp này).
Không có số nào được viết tay: mọi thứ người xem thấy là đầu ra của hệ thống thật.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONT_MATTER = """---
title: GreenScan AI
emoji: 🌿
colorFrom: green
colorTo: gray
sdk: static
app_file: index.html
pinned: true
short_description: Sàng lọc rủi ro tẩy xanh, đội AQ2026-119
---

# GreenScan AI — bản trình diễn tĩnh (đội AQ2026-119)

Giao diện thật của GreenScan chạy trên các phiên đã phân tích sẵn bằng hệ thống thật (đầu ra của máy chủ được xuất
nguyên văn). Xem hàng soát, kết luận, bằng chứng, trang gốc, giấy làm việc, quy tắc nội bộ của tổ chức, tiền lệ của
người soát; ghi quyết định soát (lưu trong trình duyệt của bạn). Phân tích tài liệu mới cần bản cài đặt đầy đủ:
xem tệp Hướng dẫn trong hồ sơ nộp, mục 2.
"""


def log(msg: str) -> None:
    print(f"[static] {msg}", flush=True)


def build(out: Path, demo_store: Path | None, overrides: dict[str, str] | None = None) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="gs-static-"))
    runs, docs = tmp / "runs", tmp / "documents"
    os.environ.update({"QUANTUM_RUNS_DIR": str(runs), "QUANTUM_DOCUMENTS_DIR": str(docs),
                       "QUANTUM_REVIEWS_FILE": str(tmp / "reviews" / "decisions.jsonl"),
                       "QUANTUM_ORG_PACK_STORE": str(tmp / "org_packs"), "QUANTUM_LLM_STANCE": "off",
                       "QUANTUM_ORG_PACKS": "", "QUANTUM_DEMO_USERS": ""})
    sys.path.insert(0, str(ROOT / "src"))
    from quantum_gw.storage.runs import RunStore
    from quantum_gw.storage.seed import install

    install(runs, docs)
    labels = {}
    if demo_store and demo_store.is_dir():
        # Runs of run_feedback_demo.py: Ca A (lượt 1 có quyết định soát, lượt 2 có tiền lệ), Hòa Phát + bộ quy tắc.
        for run in sorted((demo_store / "runs").iterdir()):
            result = run / "result.json"
            if not result.is_file():
                continue
            data = json.loads(result.read_text(encoding="utf-8"))
            if overrides and run.name in overrides:
                labels[run.name] = overrides[run.name]
            elif data.get("org_findings"):
                labels[run.name] = "Hòa Phát + bộ quy tắc nội bộ “Ngân hàng TMCP Xanh Demo” (đã duyệt bốn mắt)"
            elif data.get("precedents"):
                labels[run.name] = "Ca mẫu A – lượt 2: hiện tiền lệ từ quyết định của người soát"
            elif data["summary"]["total_claims"] == 5:
                labels[run.name] = "Ca mẫu A – lượt 1: người soát đã chốt và chỉ đoạn quyết định"
            else:
                continue
            shutil.copytree(run, runs / run.name, dirs_exist_ok=True)
        index = docs / "index.jsonl"
        known = {json.loads(line)["doc_id"] for line in index.read_text(encoding="utf-8").splitlines() if line.strip()} \
            if index.is_file() else set()
        src_docs = demo_store / "documents"
        if (src_docs / "index.jsonl").is_file():
            for line in (src_docs / "index.jsonl").read_text(encoding="utf-8").splitlines():
                if line.strip() and json.loads(line)["doc_id"] not in known:
                    with index.open("a", encoding="utf-8") as f:
                        f.write(line + "\n")
            shutil.copytree(src_docs / "blobs", docs / "blobs", dirs_exist_ok=True)
        for name in ("decisions.jsonl", "qa.jsonl"):
            if (demo_store / "reviews" / name).is_file():
                (tmp / "reviews").mkdir(parents=True, exist_ok=True)
                shutil.copy2(demo_store / "reviews" / name, tmp / "reviews" / name)
        if (demo_store / "org_packs").is_dir():
            shutil.copytree(demo_store / "org_packs", tmp / "org_packs", dirs_exist_ok=True)
    store = RunStore(runs)
    for run_id, label in {**labels, **{k: v for k, v in (overrides or {}).items() if (runs / k).is_dir()}}.items():
        store.set_label(run_id, label)

    from fastapi.testclient import TestClient

    from quantum_gw import api

    client = TestClient(api.app)
    api_dir = out / "static-api"

    def save(path: str, response, suffix: str = ".json") -> None:
        if response.status_code != 200:
            log(f"bỏ qua {path}: HTTP {response.status_code}")
            return
        target = api_dir / f"{path}{suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)

    for path in ("health", "v1/gateway/health", "v1/runtime", "v1/org-packs", "v1/legal/corpus",
                 "v1/reviews-export/gold", "v1/feedback/proposals", "v1/feedback/second-review-sample",
                 "v1/intake/samples"):
        save(path, client.get(f"/{path}"))
    summary = client.get("/v1/feedback/summary").json()
    registry = demo_store / "models" / "registry.json" if demo_store else None
    if registry and registry.is_file():  # the candidate trained in the demo, with the gate that blocked it
        summary["models"] = [{k: m.get(k) for k in ("model_id", "kind", "status", "registered_at", "approved_by",
                                                     "gate", "challenger", "champion", "data")}
                             for m in json.loads(registry.read_text(encoding="utf-8"))["models"]]
    (api_dir / "v1" / "feedback").mkdir(parents=True, exist_ok=True)
    (api_dir / "v1" / "feedback" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")

    run_list = client.get("/v1/runs?limit=200").json()
    save("v1/runs", client.get("/v1/runs?limit=200"))
    doc_ids = set()
    for run in run_list["runs"]:
        rid = run["run_id"]
        save(f"v1/runs/{rid}", client.get(f"/v1/runs/{rid}"))
        save(f"v1/reviews/{rid}", client.get(f"/v1/reviews/{rid}"))
        save(f"v1/runs/{rid}/workpaper", client.get(f"/v1/runs/{rid}/workpaper"), ".html")
        for fmt in ("json", "md", "manifest", "audit", "csv"):     # csv: nút "Tải bảng hàng đợi" trên trang giấy làm việc
            save(f"v1/runs/{rid}/export/{fmt}", client.get(f"/v1/runs/{rid}/export?format={fmt}"),
                 {"md": ".md", "csv": ".csv"}.get(fmt, ".json"))
        studio = client.get(f"/v1/studio/{rid}")
        save(f"v1/studio/{rid}", studio)
        for doc in (studio.json().get("documents") or []) if studio.status_code == 200 else []:
            did = doc.get("doc_id")
            if did:
                save(f"v1/studio/{rid}/doc/{did}", client.get(f"/v1/studio/{rid}/doc/{did}"))
        result = client.get(f"/v1/runs/{rid}").json()["result"]
        doc_ids.update(v["claim"].get("source_doc_id") for v in result["verifications"])
        doc_ids.update(e.get("doc_id") for v in result["verifications"] for e in v["evidence"])
        log(f"phiên {rid}: {run.get('label') or ''}")

    import fitz

    pages = 0
    for did in sorted(d for d in doc_ids if d):
        meta = client.get(f"/v1/documents/{did}/meta")
        if meta.status_code != 200:
            continue
        save(f"v1/documents/{did}/meta", meta)
        info = meta.json()
        original = client.get(f"/v1/documents/{did}")
        if original.status_code == 200 and original.content[:4] == b"%PDF":
            target = api_dir / "v1" / "documents" / f"{did}.pdf"
            target.write_bytes(original.content)
            for page in range(1, int(info.get("page_count") or 0) + 1):
                image = client.get(f"/v1/documents/{did}/page/{page}?q=&zoom=1.4")
                if image.status_code != 200:
                    continue
                pix = fitz.Pixmap(image.content)
                if pix.alpha:
                    pix = fitz.Pixmap(pix, 0)
                target = api_dir / "v1" / "documents" / did / "page" / f"{page}.jpg"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(pix.tobytes("jpg", jpg_quality=70))
                pages += 1
    log(f"{len(run_list['runs'])} phiên, {pages} ảnh trang")

    dist = ROOT / "frontend" / "dist-static"
    shutil.rmtree(dist, ignore_errors=True)      # no bundle of an earlier build may ride along into the public copy
    env = {**os.environ, "VITE_STATIC": "1"}
    subprocess.run("npm run build -- --outDir dist-static", cwd=ROOT / "frontend", shell=True, check=True, env=env,
                   stdout=subprocess.DEVNULL)
    for item in dist.iterdir():
        target = out / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    (out / "README.md").write_text(FRONT_MATTER, encoding="utf-8")
    log(f"đã thay đường dẫn máy: {scrub_paths(api_dir, demo_store)} chỗ")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    log(f"xong: {out} ({size / 1e6:.1f} MB)")


# Thư mục tạm của Windows trong văn bản JSON: dấu phân cách là "\\\\" (hai ký tự) hoặc "/".
_SEP = r"(?:\\\\|\\|/)"
TEMP_PATH = re.compile(rf"[A-Za-z]:{_SEP}Users{_SEP}[^\\\\/\"]+{_SEP}AppData{_SEP}Local{_SEP}Temp")
# Gốc của một kho phiên bất kỳ (phần trước runs/reviews/documents/org_packs), kể cả kho khác kho đang dựng.
STORE_PREFIX = re.compile(rf"(?<![A-Za-z])[A-Za-z]:{_SEP}[^\"\n]*?(?={_SEP}(?:runs|reviews|documents|org_packs)(?:{_SEP}|\"))")


def scrub_paths(api_dir: Path, demo_store: Path | None) -> int:
    """Bản tĩnh là trang công khai: đường dẫn thư mục trên máy dựng (kho demo, thư mục tạm) được thay bằng tên ngắn.

    Chỉ thay tiền tố đường dẫn trong các phản hồi JSON; không số liệu hay kết luận nào bị đụng tới.
    """
    variants = set()
    if demo_store is not None:
        text = str(demo_store.resolve())
        for drive in (text[0].lower(), text[0].upper()):
            base = drive + text[1:]
            variants |= {base, base.replace("\\", "/"), base.replace("\\", "\\\\")}
    changed = 0
    for f in api_dir.rglob("*.json"):
        raw = f.read_text(encoding="utf-8")
        new = raw
        for v in sorted(variants, key=len, reverse=True):
            changed += new.count(v)
            new = new.replace(v, "kho_demo")
        # A run copied from another store still names the store it was made in (output_directory,
        # feedback.store.path): replace any absolute prefix in front of runs/reviews/documents/org_packs.
        new, n = STORE_PREFIX.subn("kho_demo", new)
        changed += n
        new, n = TEMP_PATH.subn("tmp", new)
        changed += n
        if new != raw:
            try:
                json.loads(raw)
            except ValueError:
                pass                             # nhật ký nhiều dòng (mỗi dòng một JSON): không kiểm theo kiểu một khối
            else:
                json.loads(new)                  # tệp vốn là JSON thì sau khi thay vẫn phải là JSON hợp lệ
            f.write_text(new, encoding="utf-8")
    return changed


def deploy(out: Path, space: str) -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(space, repo_type="space", space_sdk="static", private=False, exist_ok=True)
    # delete_patterns: the Space must hold exactly this build. Without it every earlier deployment's
    # sessions and scripts stay online (found 18/11: 10 old sessions were still served).
    api.upload_folder(folder_path=str(out), repo_id=space, repo_type="space", delete_patterns="*",
                      commit_message="GreenScan AI: bản trình diễn tĩnh cho Vòng 2")
    owner, name = space.split("/", 1)
    log(f"đã đẩy: https://huggingface.co/spaces/{space}  ->  https://{owner.lower()}-{name.lower()}.static.hf.space")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--demo-store", default="")
    ap.add_argument("--deploy", default="")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--label", action="append", default=[], help='"<run_id>=Nhãn hiển thị" (ghi đè nhãn tự động)')
    args = ap.parse_args()
    out = Path(args.out)
    if not args.skip_build:
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        build(out, Path(args.demo_store) if args.demo_store else None,
              dict(item.split("=", 1) for item in args.label))
    if args.deploy:
        deploy(out, args.deploy)


if __name__ == "__main__":
    main()
