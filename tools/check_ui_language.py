"""Kiểm ngôn ngữ giao diện: tìm từ tiếng Anh, thuật ngữ chuyên ngành và mã nội bộ lọt vào chữ người dùng nhìn thấy.

Quét:
  - frontend/src/**/*.js, *.jsx: chữ giữa thẻ JSX và chuỗi có dấu tiếng Việt (bỏ chú thích code);
  - src/quantum_gw/**/*.py: chuỗi một dòng có dấu tiếng Việt (lời giải thích, giấy làm việc, thông báo);
    bỏ docstring và chú thích.
Phần nội suy (${...}, {...}), thẻ HTML, tên tệp, đường dẫn web được bỏ trước khi tách từ.

Chuẩn từ ngữ: docs/05-ui/CHUAN_NGON_NGU_GIAO_DIEN.md.

Chạy:  python tools/check_ui_language.py            # báo cáo theo từ
       python tools/check_ui_language.py --files    # báo cáo theo tệp
       python tools/check_ui_language.py --strict   # mã thoát 1 nếu còn lỗi (dùng cho kiểm thử)
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Từ được phép giữ nguyên: định dạng tệp, đơn vị, phím tắt, tên riêng, tên chuẩn mực, ký hiệu hoá học.
ALLOW = {
    "pdf", "docx", "html", "txt", "csv", "zip", "co2", "co2e", "tco2e", "kwh", "mwh", "gwh", "sha", "sha256",
    "greenscan", "cpu", "gpu", "ram", "gb", "mb", "ctrl", "shift", "enter", "esc", "tab", "alt", "f8",
    "iso", "gri", "sasb", "tcfd", "issb", "ifrs", "sdg", "sdgs",
    "hpg", "ctd", "dhg", "pan", "pnj", "sab", "tra", "klm", "hose", "hnx", "upcom",
    "localhost", "http", "https", "www", "utf",
    "ghg", "protocol", "corporate", "standard", "eu", "so2", "nox", "fpt", "marketplace", "word", "web",
    "json", "jsonl", "md", "yaml", "env",
}
VN_SYL = re.compile(
    r"^(ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|b|c|d|g|h|k|l|m|n|p|r|s|t|v|x)?"
    r"(uy|oa|oe|ua|uo|ia|ie|ye|ai|ao|au|ay|eo|eu|oi|ui|iu|uu|[aeiouy])+"
    r"(ch|ng|nh|c|m|n|p|t|i|o|u|y)?$")
# Viết tắt tiếng Việt khó với người mới: phải viết đủ, hoặc có chú thích ngay cạnh.
VN_ABBR = {"bcptbv", "bctn", "bctc", "knk", "ptbv", "ck", "tnhh", "tmcp"}
VN_CHARS = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
HAS_VN = re.compile(f"[{VN_CHARS}{VN_CHARS.upper()}]")

BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"(^|[\s;])//[^\n]*")
DOCSTRING = re.compile(r"(\"\"\"|''').*?\1", re.S)
PY_COMMENT = re.compile(r"#[^\n]*")
JSX_TEXT = re.compile(r">([^<>{}=;()&|`]*[A-Za-zÀ-ỹ][^<>{}=;()&|`]*)<")
JS_STR = re.compile(r"'((?:\\.|[^'\\\n]){2,300})'|\"((?:\\.|[^\"\\\n]){2,300})\"|`((?:\\.|[^`\\]){2,600})`")
REGEX_LIKE = re.compile(r"\(\?:|\\s|\\d|\[\^|\]\+|\\b")
# Tệp chỉ chứa lời nhắc gửi mô hình hoặc mẫu nhận dạng, không hiện cho người dùng.
SKIP_FILES = {"src/quantum_gw/verification/llm_judge.py"}
PY_STR = re.compile(r"'((?:\\.|[^'\\\n]){2,400})'|\"((?:\\.|[^\"\\\n]){2,400})\"")


def _blank(m: re.Match) -> str:
    return re.sub(r"[^\n]", " ", m.group(0))


def suspicious(tok: str) -> str | None:
    t = tok.lower()
    if t in ALLOW or len(t) < 2:
        return None
    if t in VN_ABBR:
        return "viết tắt"
    if "_" in t:
        return "mã nội bộ"
    if tok.isupper() and len(tok) <= 6:
        return "viết tắt"
    if len(t) < 3:
        return None
    if re.search(r"[fjwz]", t) or not VN_SYL.match(t):
        return "tiếng Anh"
    return None


def clean(s: str) -> str:
    s = re.sub(r"\$\{[^}]*\}", " ", s)
    s = re.sub(r"`[^`]*`", " ", s)  # tên trường cấu hình trong dấu `…`: được phép, kèm giải thích
    s = re.sub(r"(?<![\w])[.\w-]*/[\w./<>&;-]+", " ", s)  # đường dẫn tệp, thư mục
    s = re.sub(r"bquantum-agentb[^,;]*", " ", s)  # lệnh quản trị
    s = re.sub(r"bQUANTUM_[A-Z_]+b|\.envb", " ", s)  # biến cấu hình
    s = re.sub(r"\{[^{}]*\}", " ", s)
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"b[\w.-]+\.(json|yaml|yml|md|py|jsx?|csv|docx|pdf|html)b", " ", s)
    return s


def strings_js(text: str):
    text = BLOCK_COMMENT.sub(_blank, text)
    text = LINE_COMMENT.sub(lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), text)
    for m in JSX_TEXT.finditer(text):
        yield m.start(), m.group(1)
    for m in JS_STR.finditer(text):
        s = next(g for g in m.groups() if g is not None)
        if HAS_VN.search(s):
            yield m.start(), s


def strings_py(text: str):
    text = DOCSTRING.sub(_blank, text)
    text = PY_COMMENT.sub(_blank, text)
    for m in PY_STR.finditer(text):
        s = next(g for g in m.groups() if g is not None)
        if HAS_VN.search(s):
            yield m.start(), s


def scan():
    out = []
    targets = [(p, strings_js) for p in sorted((ROOT / "frontend/src").rglob("*.js*"))]
    targets += [(p, strings_py) for p in sorted((ROOT / "src/quantum_gw").rglob("*.py"))]
    for p, fn in targets:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES:
            continue
        seen = set()
        for pos, s in fn(text):
            line = text.count("\n", 0, pos) + 1
            if REGEX_LIKE.search(s):
                continue  # biểu thức chính quy, không phải chữ hiển thị
            for tok in re.findall(r"[A-Za-zÀ-ỹĐđ][A-Za-zÀ-ỹĐđ0-9_]*", clean(s)):
                if not tok.isascii():
                    continue  # từ tiếng Việt có dấu
                kind = suspicious(tok)
                if kind and (line, tok) not in seen:
                    seen.add((line, tok))
                    out.append((rel, line, tok, kind, " ".join(s.split())[:100]))
    return out


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    hits = scan()
    if "--files" in argv:
        c = collections.Counter(h[0] for h in hits)
        for f, n in c.most_common():
            print(f"{n:4d}  {f}")
    else:
        by = collections.defaultdict(list)
        for h in hits:
            by[h[2]].append(h)
        for tok, hs in sorted(by.items(), key=lambda kv: -len(kv[1])):
            rel, line, _, kind, s = hs[0]
            print(f"{len(hs):4d}  {tok:24s} [{kind}]  {rel}:{line}  «{s}»")
    print(f"TỔNG: {len(hits)} chỗ, {len({h[2] for h in hits})} từ, {len({h[0] for h in hits})} tệp")
    return 1 if ("--strict" in argv and hits) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
