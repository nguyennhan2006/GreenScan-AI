"""What leaves Studio: the edited report and GreenScan's own review report.

Tracked changes are computed from the text, not replayed from the log: the
original paragraphs are aligned with the edited lines, and each changed
paragraph is diffed word by word into `w:del` / `w:ins`. The log only decides
the author of an insertion (an accepted AI suggestion or the reviewer), so the
export stays correct whatever the editor did in between.

DOCX in, DOCX out: unchanged paragraphs are copied byte for byte; a changed
paragraph keeps its paragraph properties and the formatting of its first run
(mixed formatting inside a changed paragraph is not kept -- the export notes
say so). PDF or text in: a new DOCX, one paragraph per line, with page markers.
PDF out is rebuilt from the edited text with an appendix of changes; the
original layout is not kept, and the UI says that before export.
"""

from __future__ import annotations

import difflib
import html
import io
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from quantum_gw.parsers.office import docx_paragraphs

AI_AUTHOR = "GreenScan AI (quy tắc)"
LLM_AUTHOR = "GreenScan AI (LLM)"
_TOKENS = re.compile(r"\s+|\w+|[^\w\s]", re.U)


# ---------- diff ----------

def word_ops(before: str, after: str) -> list[tuple[str, str]]:
    a, b = _TOKENS.findall(before), _TOKENS.findall(after)
    out: list[tuple[str, str]] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(("equal", "".join(a[i1:i2])))
            continue
        if i2 > i1:
            out.append(("del", "".join(a[i1:i2])))
        if j2 > j1:
            out.append(("ins", "".join(b[j1:j2])))
    return out


def align(base: list[str], new: list[str]) -> list[tuple[str, int | None, str | None]]:
    """(kind, base index, new text) in document order; kind is equal | change | delete | insert."""
    out: list[tuple[str, int | None, str | None]] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, new, autojunk=False).get_opcodes():
        if op == "equal":
            out.extend(("equal", i, base[i]) for i in range(i1, i2))
        elif op == "delete":
            out.extend(("delete", i, None) for i in range(i1, i2))
        elif op == "insert":
            out.extend(("insert", None, new[j]) for j in range(j1, j2))
        else:
            n, m = i2 - i1, j2 - j1
            for k in range(max(n, m)):
                if k < n and k < m:
                    out.append(("change", i1 + k, new[j1 + k]))
                elif k < n:
                    out.append(("delete", i1 + k, None))
                else:
                    out.append(("insert", None, new[j1 + k]))
    return out


def changes(base: list[str], new: list[str]) -> list[dict]:
    """Human-readable list of changed paragraphs, for the appendix and the review report."""
    out = []
    for kind, index, text in align(base, new):
        if kind == "equal":
            continue
        before = base[index] if index is not None else ""
        after = text or ""
        out.append({"kind": kind, "paragraph": index, "before": before, "after": after,
                    "ops": word_ops(before, after) if kind == "change" else None})
    return out


class Authors:
    """Who inserted a piece of text: an accepted AI suggestion, else the reviewer."""

    def __init__(self, log: list[dict], user: str):
        self.user = user or "Người soát xét"
        self.ai: list[tuple[str, str]] = []
        for entry in log:
            if entry.get("action") == "accept" and entry.get("actor") in {"ai-rule", "ai-llm"} and entry.get("after"):
                self.ai.append((entry["after"], LLM_AUTHOR if entry["actor"] == "ai-llm" else AI_AUTHOR))

    def of(self, inserted: str) -> str:
        piece = inserted.strip()
        if piece:
            for after, author in self.ai:
                if piece in after:
                    return author
        return self.user


# ---------- WordprocessingML ----------

_W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


class _Ids:
    def __init__(self, start: int = 9000):
        self.n = start

    def next(self) -> int:
        self.n += 1
        return self.n


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def _run(text: str, rpr: str) -> str:
    return f'<w:r>{rpr}<w:t xml:space="preserve">{_esc(text)}</w:t></w:r>'


def _del_run(text: str, rpr: str, ids: _Ids, author: str, date: str) -> str:
    return (f'<w:del w:id="{ids.next()}" w:author="{_esc(author)}" w:date="{date}">'
            f'<w:r>{rpr}<w:delText xml:space="preserve">{_esc(text)}</w:delText></w:r></w:del>')


def _ins_run(text: str, rpr: str, ids: _Ids, author: str, date: str) -> str:
    return (f'<w:ins w:id="{ids.next()}" w:author="{_esc(author)}" w:date="{date}">'
            f'{_run(text, rpr)}</w:ins>')


def _runs(before: str, after: str, rpr: str, tracked: bool, ids: _Ids, authors: Authors, date: str) -> str:
    if not tracked:
        return _run(after, rpr) if after else ""
    parts = []
    for op, text in word_ops(before, after):
        if op == "equal":
            parts.append(_run(text, rpr))
        elif op == "del":
            parts.append(_del_run(text, rpr, ids, authors.user, date))
        else:
            parts.append(_ins_run(text, rpr, ids, authors.of(text), date))
    return "".join(parts)


def _mark_paragraph(ppr: str, mark: str) -> str:
    """Put a `w:ins`/`w:del` mark on the paragraph mark (first child of the pPr's rPr)."""
    if not ppr:
        return f"<w:pPr><w:rPr>{mark}</w:rPr></w:pPr>"
    if ppr.endswith("/>"):
        return f"<w:pPr><w:rPr>{mark}</w:rPr></w:pPr>"
    if "<w:rPr>" in ppr:
        return ppr.replace("<w:rPr>", f"<w:rPr>{mark}", 1)
    return ppr.replace("</w:pPr>", f"<w:rPr>{mark}</w:rPr></w:pPr>")


def _new_docx(paragraphs_xml: list[str]) -> bytes:
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {_W_NS}><w:body>'
                + "".join(paragraphs_xml)
                + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" '
                  'w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
                  '</w:body></w:document>')
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
                     'officedocument.wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
    return buffer.getvalue()


_PAGE_RPR = '<w:rPr><w:color w:val="808080"/><w:sz w:val="16"/></w:rPr>'


def docx_from_lines(base: list[str], new: list[str], pages: list[int | None], log: list[dict], user: str,
                    tracked: bool, title: str = "") -> bytes:
    """A new DOCX for a PDF/text source: one paragraph per line, a grey page marker at each new page."""
    ids, authors = _Ids(), Authors(log, user)
    date = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    if title:
        out.append(f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t xml:space="preserve">{_esc(title)}</w:t></w:r></w:p>')
    current_page = None
    for kind, index, text in align(base, new):
        page = pages[index] if index is not None and index < len(pages) else None
        if page is not None and page != current_page:
            out.append(f'<w:p><w:r>{_PAGE_RPR}<w:t xml:space="preserve">— Trang {page} (bản gốc) —</w:t></w:r></w:p>')
            current_page = page
        if kind == "equal":
            out.append(f"<w:p>{_run(text, '')}</w:p>")
        elif kind == "change":
            out.append(f"<w:p>{_runs(base[index], text, '', tracked, ids, authors, date)}</w:p>")
        elif kind == "delete":
            if tracked:
                mark = f'<w:del w:id="{ids.next()}" w:author="{_esc(authors.user)}" w:date="{date}"/>'
                out.append(f"<w:p>{_mark_paragraph('', mark)}{_del_run(base[index], '', ids, authors.user, date)}</w:p>")
        else:
            if tracked:
                author = authors.of(text)
                mark = f'<w:ins w:id="{ids.next()}" w:author="{_esc(author)}" w:date="{date}"/>'
                out.append(f"<w:p>{_mark_paragraph('', mark)}{_ins_run(text, '', ids, author, date)}</w:p>")
            else:
                out.append(f"<w:p>{_run(text, '')}</w:p>")
    return _new_docx(out)


_P_TAG = re.compile(r"<w:p(?=[\s>/])[^>]*?(/?)>|</w:p>")
_PPR = re.compile(r"\s*(<w:pPr\s*/>|<w:pPr>.*?</w:pPr>)", re.S)
_RPR = re.compile(r"<w:r(?=[\s>])[^>]*>\s*(<w:rPr>.*?</w:rPr>)", re.S)


def _paragraph_spans(xml: str) -> list[dict]:
    """Every `w:p` in pre-order (the order ElementTree's iter gives), with its span and nesting."""
    spans: list[dict] = []
    stack: list[dict] = []
    for match in _P_TAG.finditer(xml):
        token = match.group(0)
        if token == "</w:p>":
            node = stack.pop()
            node["end"] = match.end()
            continue
        node = {"start": match.start(), "open_end": match.end(), "open": token, "end": None, "nested": False}
        if stack:
            for parent in stack:
                parent["nested"] = True
        spans.append(node)
        if match.group(1) == "/":
            node["end"] = match.end()
        else:
            stack.append(node)
    return spans


def docx_in_place(source: Path, base: list[str], new: list[str], log: list[dict], user: str,
                  tracked: bool) -> tuple[bytes, list[str]]:
    """Edit the original DOCX: changed paragraphs rewritten, the rest untouched. Returns (bytes, notes)."""
    with zipfile.ZipFile(source) as z:
        entries = {info.filename: z.read(info.filename) for info in z.infolist()}
        infos = z.infolist()
    xml = entries["word/document.xml"].decode("utf-8")
    spans = _paragraph_spans(xml)
    in_table = [p["in_table"] for p in docx_paragraphs(source)]
    if len(spans) != len(base):
        raise ValueError("Số đoạn của DOCX không khớp mô hình tài liệu; không xuất tại chỗ.")
    ids, authors = _Ids(), Authors(log, user)
    date = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    notes: list[str] = []
    edits: list[tuple[int, int, str]] = []  # (start, end, replacement); applied from the end
    last_anchor = 0
    pending_inserts: list[str] = []

    def paragraph_parts(span: dict) -> tuple[str, str]:
        inner = xml[span["open_end"]:span["end"]]
        ppr_match = _PPR.match(inner)
        ppr = ppr_match.group(1) if ppr_match else ""
        rpr_match = _RPR.search(inner)
        return ppr, rpr_match.group(1) if rpr_match else ""

    def flush_inserts(position: int) -> None:
        if pending_inserts:
            edits.append((position, position, "".join(pending_inserts)))
            pending_inserts.clear()

    for kind, index, text in align(base, new):
        if kind == "insert":
            ppr, rpr = ("", "")
            if last_anchor:
                anchor = next((s for s in spans if s["end"] == last_anchor), None)
                if anchor and not anchor["open"].endswith("/>"):
                    ppr, rpr = paragraph_parts(anchor)
            if tracked:
                author = authors.of(text)
                mark = f'<w:ins w:id="{ids.next()}" w:author="{_esc(author)}" w:date="{date}"/>'
                pending_inserts.append(f"<w:p>{_mark_paragraph(ppr, mark)}{_ins_run(text, rpr, ids, author, date)}</w:p>")
            else:
                pending_inserts.append(f"<w:p>{ppr}{_run(text, rpr)}</w:p>")
            continue
        span = spans[index]
        flush_inserts(span["start"])
        last_anchor = span["end"]
        if kind == "equal":
            continue
        if span["nested"]:
            notes.append(f"Đoạn {index + 1} chứa hộp văn bản lồng nhau: giữ nguyên, không ghi thay đổi.")
            continue
        self_closing = span["open"].endswith("/>")
        open_tag = span["open"][:-2] + ">" if self_closing else span["open"]
        ppr, rpr = ("", "") if self_closing else paragraph_parts(span)
        if kind == "change":
            body = _runs(base[index], text, rpr, tracked, ids, authors, date)
            edits.append((span["start"], span["end"], f"{open_tag}{ppr}{body}</w:p>"))
        else:  # delete
            if tracked:
                mark = f'<w:del w:id="{ids.next()}" w:author="{_esc(authors.user)}" w:date="{date}"/>'
                body = _del_run(base[index], rpr, ids, authors.user, date) if base[index] else ""
                edits.append((span["start"], span["end"], f"{open_tag}{_mark_paragraph(ppr, mark)}{body}</w:p>"))
            elif index < len(in_table) and in_table[index]:
                edits.append((span["start"], span["end"], f"{open_tag}{ppr}</w:p>"))
            else:
                edits.append((span["start"], span["end"], ""))
    if pending_inserts:
        position = last_anchor or xml.find("<w:sectPr")
        flush_inserts(position if position > 0 else xml.rfind("</w:body>"))
    for start, end, replacement in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        xml = xml[:start] + replacement + xml[end:]
    entries["word/document.xml"] = xml.encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as out:
        for info in infos:
            out.writestr(info, entries[info.filename])
    if any(k == "change" for k, _, _ in align(base, new)):
        notes.append("Đoạn có thay đổi giữ định dạng đoạn và định dạng của lượt chữ đầu tiên; định dạng hỗn hợp trong đoạn đó không giữ.")
    return buffer.getvalue(), notes


# ---------- PDF ----------

_FONT_CANDIDATES = [
    ("C:/Windows/Fonts", "arial.ttf", "arialbd.ttf"),
    ("C:/Windows/Fonts", "times.ttf", "timesbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/noto", "NotoSans-Regular.ttf", "NotoSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation", "LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"),
]


def find_font() -> tuple[Path, str, str] | None:
    for directory, regular, bold in _FONT_CANDIDATES:
        if (Path(directory) / regular).is_file():
            return Path(directory), regular, bold if (Path(directory) / bold).is_file() else regular
    return None


def pdf_from_lines(new: list[str], change_list: list[dict], title: str, note: str) -> bytes:
    """Clean PDF rebuilt from the edited text, with an appendix listing every change."""
    import fitz

    font = find_font()
    if font is None:
        raise RuntimeError("Không tìm thấy phông chữ hỗ trợ tiếng Việt để dựng PDF; dùng bản DOCX hoặc in báo cáo HTML.")
    directory, regular, bold = font
    css = (f"@font-face {{font-family: vn; src: url({regular});}} "
           f"@font-face {{font-family: vn; font-weight: bold; src: url({bold});}} "
           "* {font-family: vn;} body {font-size: 10.5pt; line-height: 1.45;} "
           "h1 {font-size: 15pt;} h2 {font-size: 12.5pt; margin-top: 14pt;} "
           ".note {font-size: 8.5pt; color: #555;} del {color: #b42318;} ins {color: #067647;} "
           "p.c {font-size: 9pt; margin: 2pt 0 6pt 0;}")
    body = [f"<h1>{_esc(title)}</h1>", f"<p class='note'>{_esc(note)}</p>"]
    body.extend(f"<p>{_esc(line)}</p>" for line in new if line.strip())
    body.append(f"<h2>Phụ lục: {len(change_list)} thay đổi so với bản gốc</h2>")
    for n, change in enumerate(change_list, start=1):
        label = {"change": "Sửa", "delete": "Xóa", "insert": "Thêm"}[change["kind"]]
        if change["ops"]:
            rendered = "".join(
                _esc(t) if op == "equal" else f"<del>{_esc(t)}</del>" if op == "del" else f"<ins>{_esc(t)}</ins>"
                for op, t in change["ops"])
        elif change["kind"] == "delete":
            rendered = f"<del>{_esc(change['before'])}</del>"
        else:
            rendered = f"<ins>{_esc(change['after'])}</ins>"
        body.append(f"<p class='c'><b>{n}. {label}</b> — {rendered}</p>")
    story = fitz.Story(html="".join(body), user_css=css, archive=fitz.Archive(str(directory)))
    buffer = io.BytesIO()
    writer = fitz.DocumentWriter(buffer)
    mediabox = fitz.paper_rect("a4")
    where = mediabox + (56, 56, -56, -56)
    more = True
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()
    writer.close()
    return buffer.getvalue()


# ---------- review report ----------

_SEVERITY_LABEL = {"error": "Nghiêm trọng", "warning": "Cần xem", "info": "Thông tin"}
_ACTION_LABEL = {"accept": "Chấp nhận", "reject": "Từ chối", "edit": "Sửa tay", "ignore": "Bỏ qua",
                 "save": "Lưu phiên bản", "restore": "Khôi phục", "rework": "Sửa lại đề xuất"}
_ACTOR_LABEL = {"user": "Người", "ai-rule": "AI (quy tắc)", "ai-llm": "AI (LLM)", "system": "Hệ thống"}


def review_html(ctx: dict) -> str:
    """GreenScan's review report for one edited document: findings, decisions, evidence, basis, change log."""
    e = _esc
    diags = ctx["diagnostics"]
    gone = ctx.get("gone", [])
    log = ctx["log"]
    change_list = ctx["changes"]
    rows = []
    for d in diags:
        evidence = "<br>".join(
            f"{e(x['source_name'])}, tr. {x.get('page') or '—'} ({e(x.get('relation') or '')}{', độc lập' if x.get('independent') else ''})"
            for x in d["evidence"][:3]) or "—"
        legal = d.get("legal") or {}
        basis = "<br>".join(f"{e(s['document'] or '')} — {e(s['verification_label'])}" for s in legal.get("sources", [])[:3]) or "—"
        decided = [entry for entry in log if entry.get("claim_id") == d["claim_id"] and entry.get("action") in {"accept", "reject", "ignore", "edit"}]
        decision = "; ".join(f"{_ACTION_LABEL.get(x['action'], x['action'])} {e(x.get('rule_code') or '')}".strip() for x in decided) or "Chưa xử lý"
        rows.append(
            f"<tr class='{d['severity']}'><td>{_SEVERITY_LABEL[d['severity']]}</td><td>{e(d.get('text', ''))}"
            f"<div class='m'>{e(d['message'])}</div></td><td>{evidence}</td><td>{basis}</td><td>{decision}</td></tr>")
    for g in gone:
        decided = [entry for entry in log if entry.get("claim_id") == g["claim_id"]]
        rows.append(f"<tr class='done'><td>Đã sửa</td><td>{e(g['text'])}</td><td colspan='2'>Câu gốc không còn trong văn bản.</td>"
                    f"<td>{'; '.join(_ACTION_LABEL.get(x['action'], x['action']) for x in decided) or 'Sửa tay'}</td></tr>")
    log_rows = "".join(
        f"<tr><td>{x.get('seq')}</td><td>{e(x.get('ts', ''))}</td><td>{_ACTOR_LABEL.get(x.get('actor'), x.get('actor'))}"
        f"{' · ' + e(x['user']) if x.get('user') else ''}</td><td>{_ACTION_LABEL.get(x.get('action'), x.get('action'))}</td>"
        f"<td>{e(x.get('rule_code') or '')}</td><td>{e((x.get('reason') or '')[:200])}</td></tr>" for x in log)
    change_rows = "".join(
        f"<li><b>{ {'change': 'Sửa', 'delete': 'Xóa', 'insert': 'Thêm'}[c['kind']] }</b> — "
        + ("".join(e(t) if op == "equal" else f"<del>{e(t)}</del>" if op == "del" else f"<ins>{e(t)}</ins>" for op, t in c["ops"])
           if c["ops"] else (f"<del>{e(c['before'])}</del>" if c["kind"] == "delete" else f"<ins>{e(c['after'])}</ins>"))
        + "</li>" for c in change_list)
    counts = {k: sum(1 for d in diags if d["severity"] == k) for k in ("error", "warning", "info")}
    accepted = sum(1 for x in log if x.get("action") == "accept")
    rejected = sum(1 for x in log if x.get("action") == "reject")
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Báo cáo rà soát — {e(ctx['doc_name'])}</title>
<style>body{{font-family:system-ui,'Segoe UI',Arial,sans-serif;color:#0f172a;max-width:1100px;margin:24px auto;padding:0 16px;font-size:13px}}
h1{{font-size:20px;margin:0}}h2{{font-size:15px;margin-top:24px;border-bottom:1px solid #e2e8f0;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #e2e8f0;padding:6px;vertical-align:top;text-align:left}}
th{{background:#f8fafc}}tr.error td:first-child{{color:#b42318;font-weight:600}}tr.warning td:first-child{{color:#b54708;font-weight:600}}
tr.done td:first-child{{color:#067647;font-weight:600}}.m{{color:#475569;font-size:12px;margin-top:2px}}del{{color:#b42318}}ins{{color:#067647}}
.meta{{color:#475569}}.box{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px;margin-top:10px}}
@media print{{body{{margin:0}}}}</style></head><body>
<h1>Báo cáo rà soát GreenScan</h1>
<p class="meta">Tài liệu: <b>{e(ctx['doc_name'])}</b> · Phiên phân tích <code>{e(ctx['run_id'])}</code> · Xuất lúc {e(ctx['exported_at'])} · Người soát xét: {e(ctx.get('user') or '—')}</p>
<div class="box">Phát hiện còn mở: <b>{counts['error']}</b> nghiêm trọng, <b>{counts['warning']}</b> cần xem, <b>{counts['info']}</b> thông tin · Đã sửa khỏi văn bản: <b>{len(gone)}</b> · Đề xuất đã chấp nhận: <b>{accepted}</b>, đã từ chối: <b>{rejected}</b> · Thay đổi văn bản: <b>{len(change_list)}</b> đoạn</div>
<h2>1. Phát hiện và quyết định</h2>
<table><tr><th>Mức</th><th>Tuyên bố</th><th>Bằng chứng</th><th>Căn cứ (nhãn xác minh)</th><th>Quyết định</th></tr>{''.join(rows)}</table>
<h2>2. Thay đổi văn bản</h2><ol>{change_rows or '<li>Không có.</li>'}</ol>
<h2>3. Nhật ký thay đổi</h2>
<table><tr><th>#</th><th>Thời điểm (UTC)</th><th>Ai</th><th>Việc</th><th>Quy tắc</th><th>Lý do</th></tr>{log_rows or '<tr><td colspan=6>Trống.</td></tr>'}</table>
<h2>4. Giới hạn</h2><ul>
<li>Đề xuất sinh từ mẫu quy tắc, chạy offline; không đề xuất nào được thêm số liệu không có trong câu gốc (kiểm bằng <code>assert_no_new_numbers</code>).</li>
<li>Căn cứ pháp lý mang nhãn "Chưa có người xác minh" là căn cứ ứng viên, chưa phải kết luận pháp lý.</li>
<li>{e(ctx.get('layout_note') or '')}</li>
<li>Tài liệu bằng chứng (BCTC, văn bản pháp luật, dữ liệu bên thứ ba) chỉ được đọc, không bị sửa.</li></ul>
<p class="meta">SHA-256 bản gốc: <code>{e(ctx['base_sha256'])}</code> · bản đã sửa: <code>{e(ctx['final_sha256'])}</code></p>
</body></html>"""
