"""Thu kết quả các lượt Kaggle của offline_training_v1, gộp lại, vẽ biểu đồ; đẩy notebook học trò khi thầy đã xong.

    C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/thu_ket_qua.py            # trạng thái + tải + vẽ
    C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/thu_ket_qua.py --push-sft # thêm: đẩy notebook học trò 4B

Tài khoản Kaggle: tệp C:/Users/ASUS/.kaggle/acc_kaggle_du_phong.env (qua tools/kaggle/kapi.py, không in khoá).
Kết quả: deploy/vastai_a100/out_kaggle/<notebook>/ (tải nguyên), deploy/vastai_a100/out_kaggle/merged/ (gộp),
biểu đồ: docs/04-data-ai/hinh_mo_hinh/. Không tải mô hình lớn (gguf, safetensors) trừ khi có --models.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deploy" / "vastai_a100" / "out_kaggle"
FIG = ROOT / "docs" / "04-data-ai" / "hinh_mo_hinh"
ENV = dict(os.environ, FLAG_KAGGLE_ENV="C:/Users/ASUS/.kaggle/acc_kaggle_du_phong.env", PYTHONIOENCODING="utf-8")
KERNELS = {"t1": "phanththui/gs-off-t1-q13", "rerank": "nguyenlethaonhi123/gs-off-reranker-bge-v2",
           "stance_llm": "khanhnguyenm841/gs-off-stance-llm-4b", "panel": "phanvnhtrng/gs-off-llm-panel", "t1_v2": "letranchauanh/gs-off-t1-q13-v2",
           "stance_nli": "phanththui/gs-off-stance-nli-head", "stance_probe": "nguyntrquangtrung/gs-off-stance-nli-probe", "router": "phantrnhuyntrn/gs-off-router-v1", "sft_1p7b": "diuquinh/gs-off-explain-sft-1p7b-v2",
           "teacher": "nngocnh/gs-off-explain-teacher", "sft": "phannguyngiahuy11a5/gs-off-explain-sft-v2"}
SMALL = r"\.[jltpm][a-z]*$"   # json, jsonl, log, txt, png, md (kapi forbids "|")


def kapi(*args) -> str:
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/kaggle/kapi.py"), *args], env=ENV,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    return (r.stdout + r.stderr).strip()


def status(k: str) -> str:
    s = kapi("status", k).splitlines()
    line = next((x for x in reversed(s) if "status" in x), s[-1] if s else "")
    for word in ("COMPLETE", "RUNNING", "ERROR", "QUEUED", "CANCEL"):
        if word in line:
            return word
    return line[-80:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push-sft", action="store_true")
    ap.add_argument("--models", action="store_true", help="tải cả trọng số / GGUF (lớn)")
    a = ap.parse_args()
    merged = OUT / "merged"
    merged.mkdir(parents=True, exist_ok=True)
    states = {}
    for name, k in KERNELS.items():
        st = status(k)
        states[name] = st
        print(f"{name:8} {k:42} {st}")
        if st not in ("COMPLETE", "ERROR"):
            continue
        dest = OUT / name
        args = ["output", k, "--dest", str(dest)] + ([] if a.models else ["--pattern", SMALL])
        print("   ", kapi(*args).splitlines()[-1:])
        src = dest / "out"
        if src.exists():
            shutil.copytree(src, merged, dirs_exist_ok=True)
    if a.push_sft and states.get("teacher") == "COMPLETE" and states.get("sft") not in ("RUNNING", "COMPLETE", "QUEUED"):
        acct, slug = KERNELS["sft"].split("/")
        print(kapi("push", str(ROOT / "deploy/vastai_a100/kaggle/nb_explain_sft.ipynb"), "--account", acct, "--slug", slug,
                   "--title", "gs off explain sft", "--gpu", "--internet",
                   "--datasets", "phantrnanna/gs-train-bundle-v1,phantrnanna/gs-explain-teacher-v1").splitlines()[-1:])
        print("   ghi vào docs/RUNS.md: mốc log đầu = giờ đẩy + 10 phút, xong ≈ + 90 phút")
    r = subprocess.run([sys.executable, str(ROOT / "deploy/vastai_a100/gs_train/plots.py"), "--results", str(merged),
                        "--out", str(FIG)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip()[-600:] or r.stderr.strip()[-600:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
