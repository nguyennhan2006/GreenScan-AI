"""Assemble the thesis: chapters -> LUAN_VAN_GREENSCAN.md (+ .docx via pandoc), merged references -> 99_TAI_LIEU_THAM_KHAO.md.

Run from anywhere: python -I docs/09-luan-van/LUAN_VAN_GREENSCAN/assemble.py
Each chapter's "## Tài liệu tham khảo ..." section is moved out of the body; entries are de-duplicated
by their text (case/space-insensitive) and listed once, alphabetically, in the merged list.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = ["00_TOM_TAT.md", "01_MO_DAU.md", "02_CO_SO_LY_THUYET.md", "03_BAI_TOAN_VA_THIET_KE.md",
         "04_DU_LIEU_VA_PHUONG_PHAP_DANH_GIA.md", "05_KET_QUA.md", "06_THAO_LUAN_HAN_CHE_HUONG_PHAT_TRIEN.md",
         "07_KET_LUAN.md"]
REF_HEAD = re.compile(r"^##\s+Tài liệu tham khảo.*$", re.I | re.M)


def split_refs(text: str) -> tuple[str, list[str]]:
    m = REF_HEAD.search(text)
    if not m:
        return text, []
    body, refs = text[:m.start()].rstrip() + "\n", text[m.end():]
    nxt = re.search(r"^#{1,2}\s", refs, re.M)
    if nxt:
        body += "\n" + refs[nxt.start():]
        refs = refs[:nxt.start()]
    items = [l.strip() for l in refs.splitlines() if re.match(r"^\s*(?:[-*]|\d+\.)\s+\S", l)]
    return body, [re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", x) for x in items]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    bodies, refs, seen, missing = [], [], set(), []
    for name in ORDER:
        p = HERE / name
        if not p.exists():
            missing.append(name)
            continue
        body, rs = split_refs(p.read_text(encoding="utf-8"))
        bodies.append(body.strip())
        for r in rs:
            key = re.sub(r"\W+", " ", r.casefold()).strip()[:120]
            if key and key not in seen:
                seen.add(key)
                refs.append(r)
    refs.sort(key=lambda r: re.sub(r"[^\w]", "", r.casefold()))
    ref_md = "# Tài liệu tham khảo\n\n*Gộp tự động từ danh mục cuối mỗi chương (assemble.py); trùng lặp đã loại.*\n\n" + \
             "\n".join(f"{i}. {r}" for i, r in enumerate(refs, 1)) + "\n"
    (HERE / "99_TAI_LIEU_THAM_KHAO.md").write_text(ref_md, encoding="utf-8")
    full = "\n\n---\n\n".join(bodies) + "\n\n---\n\n" + ref_md
    (HERE / "LUAN_VAN_GREENSCAN.md").write_text(full, encoding="utf-8")
    words = len(re.findall(r"\w+", full))
    print(f"chapters={len(bodies)} missing={missing} references={len(refs)} syllables~{words}")
    pandoc = shutil.which("pandoc") or "D:/anaconda3/Library/bin/pandoc.exe"
    r = subprocess.run([pandoc, "LUAN_VAN_GREENSCAN.md", "-o", "LUAN_VAN_GREENSCAN.docx", "--toc", "--toc-depth=2",
                        "--resource-path", str(HERE)], cwd=HERE, capture_output=True, text=True)
    print("docx", "OK" if r.returncode == 0 else r.stderr[:400])


if __name__ == "__main__":
    main()
