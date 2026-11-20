"""The change report: each paragraph edited in Studio, where it sits in the original, and why.

A PDF cannot be rebuilt from its extracted text. Extraction drops the layout,
and on a scanned page the text is only OCR's reading of an image. So for a PDF
Studio does not hand back a new PDF. It hands back a report the company can
apply to its own source file (Word, InDesign…): for each changed paragraph, the
page in the original, the original wording, the proposed wording with the
changes marked, the problem GreenScan found there, and the reason for the edit:
the rule and its basis for an accepted suggestion, the reviewer's own words for
an edit made by hand. A paragraph changed without a recorded reason is listed
as such; Studio asks for one before export (frontend StudioPage).

Built from three things: the original paragraphs, the current text and the
session log. Entries undone by a later "restore" are dropped, so a reason never
outlives the edit it explained.
"""

from __future__ import annotations

import io
import re
from bisect import bisect_right

from quantum_gw.labels_vi import DISCLAIMER_VI
from quantum_gw.utils.vn_format import vn_time  # noqa: F401 - re-exported for callers

from .export import _esc, _new_docx, align, find_font, word_ops
from .session import sha
from .suggest import basis_for

KIND_LABELS = {"change": "Sửa", "delete": "Xóa", "insert": "Thêm"}
ACTION_LABELS = {"accept": "Chấp nhận đề xuất", "rework": "Sửa lại đề xuất rồi áp dụng", "edit": "Sửa tay",
                 "note": "Lý do người soát ghi", "ignore": "Giữ nguyên"}
ACTOR_LABELS = {"user": "Người soát xét", "ai-rule": "Máy (quy tắc)", "ai-llm": "Mô hình ngôn ngữ", "system": "Hệ thống"}
SEVERITY_LABELS = {"error": "Nghiêm trọng", "warning": "Cần xem", "info": "Thông tin"}




def paragraph_key(index: int | None, text: str) -> str:
    """Stable id of a changed paragraph: its position in the original, or the hash of an inserted one."""
    return f"p{index}" if index is not None else f"n{sha(text)[:12]}"


def active_log(log: list[dict], versions: list[dict]) -> list[dict]:
    """The log without the entries a later restore undid."""
    saved_at = {v["version"]: v.get("log_seq", 0) for v in versions}
    active: list[dict] = []
    for entry in log:
        if entry.get("action") == "restore":
            version = entry.get("version")
            if version is None:  # sessions written before 11/11/2026 keep it only in the reason
                found = re.search(r"phiên bản (\d+)", entry.get("reason") or "")
                version = int(found.group(1)) if found else 0
            limit = saved_at.get(version, 0) if version else 0
            active = [e for e in active if (e.get("seq") or 0) <= limit]
            continue
        active.append(entry)
    return active


def _reason(entry: dict, kind_labels: dict[str, str]) -> dict:
    rule = entry.get("rule_code")
    return {
        "action": ACTION_LABELS.get(entry.get("action"), entry.get("action") or ""),
        "who": ACTOR_LABELS.get(entry.get("actor"), "Người soát xét"),
        "user": entry.get("user") or "",
        "title": kind_labels.get(entry.get("kind") or "", "") if rule else "",
        "text": (entry.get("reason") or "").strip(),
        "basis": [b["label"] for b in basis_for(rule)] if entry.get("action") in {"accept", "rework"} else [],
        "ts": entry.get("ts") or "",
    }


def build(base: list[dict], new_lines: list[str], log: list[dict], versions: list[dict],
          base_diagnostics: list[dict], kind_labels: dict[str, str]) -> list[dict]:
    """One record per changed paragraph, in document order.

    `base` are the original paragraphs (`text`, `page`, `ocr`), `new_lines` the
    text as it reads now, `base_diagnostics` the findings located in the
    original (studio.document.diagnostics on the base text).
    """
    base_lines = [p["text"] for p in base]
    starts, position = [], 0
    for line in base_lines:
        starts.append(position)
        position += len(line) + 1
    claims_at: dict[int, list[dict]] = {}
    for d in base_diagnostics:
        first = bisect_right(starts, d["from"]) - 1
        last = bisect_right(starts, max(d["from"], d["to"] - 1)) - 1
        for i in range(max(first, 0), last + 1):
            claims_at.setdefault(i, []).append(d)

    by_claim: dict[str, list[dict]] = {}
    notes: dict[str, list[dict]] = {}
    for entry in active_log(log, versions):
        if entry.get("action") == "note" and entry.get("paragraph_key"):
            notes.setdefault(entry["paragraph_key"], []).append(entry)
        elif entry.get("claim_id") and entry.get("action") in {"accept", "rework", "edit"}:
            by_claim.setdefault(entry["claim_id"], []).append(entry)

    items: list[dict] = []
    page = None
    for kind, index, text in align(base_lines, new_lines):
        paragraph = base[index] if index is not None else None
        if paragraph is not None and paragraph.get("page") is not None:
            page = paragraph["page"]
        if kind == "equal":
            continue
        before = base_lines[index] if index is not None else ""
        after = text or ""
        key = paragraph_key(index, after)
        findings = claims_at.get(index, []) if index is not None else []
        reasons: list[dict] = []
        seen: set[tuple] = set()
        for d in findings:
            entries = by_claim.get(d["claim_id"], [])
            # Autosave logs one "edit" per save for a touched claim; the last says it all.
            last_edit = next((e for e in reversed(entries) if e.get("action") == "edit"), None)
            for entry in entries:
                if entry.get("action") == "edit" and entry is not last_edit:
                    continue
                reason = _reason(entry, kind_labels)
                mark = (reason["action"], reason["title"], reason["text"])
                if mark not in seen:
                    seen.add(mark)
                    reasons.append(reason)
        reasons.extend(_reason(e, kind_labels) for e in notes.get(key, []))
        items.append({
            "n": len(items) + 1, "key": key, "kind": kind, "kind_label": KIND_LABELS[kind],
            "paragraph": index, "page": page, "ocr": bool(paragraph and paragraph.get("ocr")),
            "ocr_confidence": (paragraph or {}).get("ocr_confidence"),
            "doubtful_numbers": list((paragraph or {}).get("doubtful_numbers") or []),
            "before": before, "after": after,
            "ops": word_ops(before, after) if kind == "change" else None,
            "findings": [{"claim_id": d["claim_id"], "status_label": d.get("status_label", ""),
                          "message": d.get("message", ""), "severity": d.get("severity", "info")} for d in findings],
            "reasons": reasons,
            "needs_reason": not any(r["text"] for r in reasons),
        })
    return items


def summary(items: list[dict]) -> dict:
    return {
        "changed": len(items),
        "needs_reason": sum(1 for i in items if i["needs_reason"]),
        "ocr_pages": sorted({i["page"] for i in items if i["ocr"] and i["page"] is not None}),
    }


# ---------- rendering ----------

def _diff_html(item: dict, side: str) -> str:
    """The paragraph with its changes marked: deletions on the original side, insertions on the proposed one."""
    e = _esc
    if item["ops"]:
        keep = "del" if side == "before" else "ins"
        return "".join(e(t) if op == "equal" else (f"<{op}>{e(t)}</{op}>" if op == keep else "")
                       for op, t in item["ops"])
    text = item[side]
    if not text:
        return "<i>(không có)</i>"
    return f"<del>{e(text)}</del>" if side == "before" else f"<ins>{e(text)}</ins>"


def _where(item: dict) -> str:
    where = f"Trang {item['page']} của tệp gốc" if item["page"] else "Vị trí trong văn bản gốc"
    if item["paragraph"] is not None:
        where += f", đoạn thứ {item['paragraph'] + 1}"
    else:
        where += ", đoạn chèn mới"
    return where + ocr_note(item)


def ocr_note(item: dict) -> str:
    """" · chữ đọc bằng OCR (độ tin cậy 84/100; số đọc chưa chắc: 30)": how far the original text can be trusted."""
    if not item.get("ocr"):
        return ""
    sure = f", độ tin cậy {item['ocr_confidence']:.0f}/100" if item.get("ocr_confidence") is not None else ""
    shaky = f"; số đọc chưa chắc: {', '.join(item['doubtful_numbers'][:5])}" if item.get("doubtful_numbers") else ""
    return f" · chữ đọc bằng OCR{sure}{shaky}, đối chiếu trang gốc"


def body_html(ctx: dict) -> str:
    """The report body, shared by the HTML page and the PDF."""
    e = _esc
    items, s = ctx["items"], summary(ctx["items"])
    out = [
        "<h1>Báo cáo chỉnh sửa</h1>",
        f"<p class='box'><b>{e(DISCLAIMER_VI)}</b></p>",
        f"<p class='meta'>Tài liệu: <b>{e(ctx['doc_name'])}</b> · Phiên phân tích {e(ctx['run_id'])} · "
        f"Xuất lúc {e(vn_time(ctx['exported_at']))} · Người soát xét: {e(ctx.get('user') or '—')}</p>",
        f"<p class='box'>{e(ctx['layout_note'])}</p>",
        f"<p class='box'><b>{s['changed']}</b> đoạn được sửa · <b>{s['needs_reason']}</b> đoạn chưa ghi lý do"
        + (f" · đoạn ở trang đọc bằng OCR: tr. {', '.join(map(str, s['ocr_pages']))}" if s["ocr_pages"] else "")
        + "</p>",
    ]
    if not items:
        out.append("<p>Chưa có đoạn nào được sửa so với bản gốc.</p>")
    for item in items:
        out.append(f"<h2>{item['n']}. {e(item['kind_label'])} · {e(_where(item))}</h2>")
        out.append(f"<p class='lab'>Đoạn gốc</p><p class='para'>{_diff_html(item, 'before')}</p>")
        out.append(f"<p class='lab'>Đoạn đề xuất</p><p class='para'>{_diff_html(item, 'after')}</p>")
        for f in item["findings"]:
            out.append(f"<p class='find'>Vấn đề GreenScan nêu ({e(SEVERITY_LABELS.get(f['severity'], ''))}"
                       f"{' · ' + e(f['status_label']) if f['status_label'] else ''}): {e(f['message'])}</p>")
        out.append("<p class='lab'>Lý do sửa</p>")
        if item["needs_reason"]:
            out.append("<p class='miss'>Chưa ghi lý do. Người soát xét cần bổ sung trước khi gửi báo cáo.</p>")
        for r in item["reasons"]:
            head = r["action"] + (f" «{r['title']}»" if r["title"] else "")
            who = r["who"] + (f" ({r['user']})" if r["user"] else "")
            text = r["text"] or "chưa ghi lý do"
            out.append(f"<p class='why'>{e(head)} — {e(text)} <span class='meta'>· {e(who)}"
                       f"{' · ' + e(vn_time(r['ts'])) if r['ts'] else ''}</span></p>")
            for label in r["basis"]:
                out.append(f"<p class='basis'>Căn cứ: {e(label)}</p>")
    kept = ctx.get("kept") or []
    if kept:
        out.append("<h2>Phát hiện người soát xét quyết định giữ nguyên</h2>")
        for k in kept:
            out.append(f"<p class='why'>Trang {e(str(k.get('page') or '—'))}: «{e(k['text'][:300])}» — "
                       f"{e(k['reason'] or 'không ghi lý do')}</p>")
    open_counts = ctx.get("open") or {}
    out.append("<h2>Giới hạn</h2><ul>"
               "<li>Đề xuất của máy sinh từ mẫu quy tắc, không bao giờ thêm số liệu không có trong câu gốc; "
               "chỗ cần số liệu để dạng «[bổ sung: …]» cho doanh nghiệp điền.</li>"
               "<li>Căn cứ mang nhãn «chưa có người xác minh» là căn cứ ứng viên, chưa phải kết luận pháp lý.</li>"
               f"<li>Phát hiện còn mở chưa sửa: {open_counts.get('error', 0)} nghiêm trọng, "
               f"{open_counts.get('warning', 0)} cần xem, {open_counts.get('info', 0)} thông tin "
               "(xem «Báo cáo rà soát GreenScan»).</li></ul>")
    out.append(f"<p class='meta'>Mã băm SHA-256 · tệp gốc: {e(ctx.get('source_sha256') or '—')} · văn bản gốc đã "
               f"trích: {e(ctx['base_sha256'])} · văn bản sau sửa: {e(ctx['final_sha256'])}</p>")
    return "".join(out)


_CSS = (
    "body{font-family:system-ui,'Segoe UI',Arial,sans-serif;color:#0f172a;max-width:900px;margin:24px auto;"
    "padding:0 16px;font-size:13.5px;line-height:1.5}h1{font-size:21px;margin:0 0 4px}h2{font-size:15px;"
    "margin:22px 0 6px;border-bottom:1px solid #e2e8f0;padding-bottom:3px}.meta{color:#64748b;font-size:12px}"
    ".box{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:8px 10px}"
    ".lab{margin:8px 0 2px;font-size:11.5px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.03em}"
    ".para{margin:0;padding:6px 10px;border-left:3px solid #cbd5e1;background:#fff}"
    "del{color:#b42318;text-decoration:line-through}ins{color:#067647;text-decoration:underline}"
    ".find{margin:6px 0 0;color:#92400e;font-size:12.5px}.why{margin:2px 0}.basis{margin:0 0 2px 14px;"
    "color:#475569;font-size:12px}.miss{margin:2px 0;color:#b42318;font-weight:600}"
    "@media print{body{margin:0}h2{break-after:avoid}}"
)


def render_html(ctx: dict) -> str:
    return (f"<!doctype html><html lang='vi'><head><meta charset='utf-8'><title>Báo cáo chỉnh sửa — "
            f"{_esc(ctx['doc_name'])}</title><style>{_CSS}</style></head><body>{body_html(ctx)}</body></html>")


def render_pdf(ctx: dict) -> bytes:
    import fitz

    font = find_font()
    if font is None:
        raise RuntimeError("Không tìm thấy phông chữ hỗ trợ tiếng Việt để dựng PDF; dùng bản Word hoặc in bản HTML.")
    directory, regular, bold = font
    css = (f"@font-face {{font-family: vn; src: url({regular});}} "
           f"@font-face {{font-family: vn; font-weight: bold; src: url({bold});}} "
           "* {font-family: vn;} body {font-size: 10pt; line-height: 1.4;} h1 {font-size: 16pt;} "
           "h2 {font-size: 11.5pt; margin-top: 12pt;} .meta {font-size: 8pt; color: #64748b;} "
           ".box {font-size: 9pt; color: #334155;} .lab {font-size: 8pt; font-weight: bold; color: #475569; "
           "margin-bottom: 1pt;} .para {margin: 0 0 4pt 8pt;} del {color: #b42318; text-decoration: line-through;} "
           "ins {color: #067647; text-decoration: underline;} .find {font-size: 9pt; color: #92400e;} "
           ".basis {font-size: 8.5pt; color: #475569; margin-left: 10pt;} .miss {color: #b42318; font-weight: bold;}")
    story = fitz.Story(html=body_html(ctx), user_css=css, archive=fitz.Archive(str(directory)))
    buffer = io.BytesIO()
    writer = fitz.DocumentWriter(buffer)
    mediabox = fitz.paper_rect("a4")
    where = mediabox + (50, 50, -50, -50)
    more = True
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()
    writer.close()
    # Embedding the whole font made a two-item report 2 MB; keep only the glyphs used.
    pdf = fitz.open(stream=buffer.getvalue(), filetype="pdf")
    pdf.subset_fonts()
    return pdf.tobytes(garbage=3, deflate=True)


# ---------- Word ----------



def _p(runs: str, ppr: str = "") -> str:
    return f"<w:p>{ppr}{runs}</w:p>"


def _r(text: str, *, bold=False, size=None, color=None, strike=False, underline=False, italic=False) -> str:
    rpr = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "") + ("<w:strike/>" if strike else "") \
        + ('<w:u w:val="single"/>' if underline else "") + (f'<w:color w:val="{color}"/>' if color else "") \
        + (f'<w:sz w:val="{size}"/>' if size else "")
    return f'<w:r>{f"<w:rPr>{rpr}</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{_esc(text)}</w:t></w:r>'


def _diff_runs(item: dict, side: str) -> str:
    if item["ops"]:
        keep = "del" if side == "before" else "ins"
        out = []
        for op, t in item["ops"]:
            if op == "equal":
                out.append(_r(t))
            elif op == keep == "del":
                out.append(_r(t, strike=True, color="B42318"))
            elif op == keep == "ins":
                out.append(_r(t, underline=True, color="067647"))
        return "".join(out)
    text = item[side]
    if not text:
        return _r("(không có)", italic=True, color="64748B")
    return _r(text, strike=True, color="B42318") if side == "before" else _r(text, underline=True, color="067647")


def render_docx(ctx: dict) -> bytes:
    items, s = ctx["items"], summary(ctx["items"])
    indent = '<w:pPr><w:ind w:left="284"/><w:pBdr><w:left w:val="single" w:sz="12" w:space="6" w:color="CBD5E1"/></w:pBdr></w:pPr>'
    paras = [
        _p(_r("Báo cáo chỉnh sửa", bold=True, size=36)),
        _p(_r(DISCLAIMER_VI, bold=True, size=19)),
        _p(_r(f"Tài liệu: {ctx['doc_name']} · Phiên phân tích {ctx['run_id']} · Xuất lúc {vn_time(ctx['exported_at'])}"
              f" · Người soát xét: {ctx.get('user') or '—'}", size=18, color="64748B")),
        _p(_r(ctx["layout_note"], size=19)),
        _p(_r(f"{s['changed']} đoạn được sửa · {s['needs_reason']} đoạn chưa ghi lý do"
              + (f" · đoạn ở trang đọc bằng OCR: tr. {', '.join(map(str, s['ocr_pages']))}" if s["ocr_pages"] else ""),
              bold=True, size=19)),
    ]
    if not items:
        paras.append(_p(_r("Chưa có đoạn nào được sửa so với bản gốc.")))
    for item in items:
        paras.append(_p(_r(f"{item['n']}. {item['kind_label']} · {_where(item)}", bold=True, size=24),
                        '<w:pPr><w:spacing w:before="240"/></w:pPr>'))
        paras.append(_p(_r("Đoạn gốc", bold=True, size=17, color="475569")))
        paras.append(_p(_diff_runs(item, "before"), indent))
        paras.append(_p(_r("Đoạn đề xuất", bold=True, size=17, color="475569")))
        paras.append(_p(_diff_runs(item, "after"), indent))
        for f in item["findings"]:
            label = SEVERITY_LABELS.get(f["severity"], "") + (" · " + f["status_label"] if f["status_label"] else "")
            paras.append(_p(_r(f"Vấn đề GreenScan nêu ({label}): {f['message']}", size=19, color="92400E")))
        paras.append(_p(_r("Lý do sửa", bold=True, size=17, color="475569")))
        if item["needs_reason"]:
            paras.append(_p(_r("Chưa ghi lý do. Người soát xét cần bổ sung trước khi gửi báo cáo.", bold=True,
                               color="B42318")))
        for r in item["reasons"]:
            head = r["action"] + (f" «{r['title']}»" if r["title"] else "")
            who = r["who"] + (f" ({r['user']})" if r["user"] else "")
            paras.append(_p(_r(f"{head} — {r['text'] or 'chưa ghi lý do'}") + _r(f" · {who}"
                            + (f" · {vn_time(r['ts'])}" if r["ts"] else ""), size=16, color="64748B")))
            for label in r["basis"]:
                paras.append(_p(_r(f"Căn cứ: {label}", size=18, color="475569"), '<w:pPr><w:ind w:left="284"/></w:pPr>'))
    kept = ctx.get("kept") or []
    if kept:
        paras.append(_p(_r("Phát hiện người soát xét quyết định giữ nguyên", bold=True, size=24),
                        '<w:pPr><w:spacing w:before="240"/></w:pPr>'))
        for k in kept:
            paras.append(_p(_r(f"Trang {k.get('page') or '—'}: «{k['text'][:300]}» — {k['reason'] or 'không ghi lý do'}")))
    paras.append(_p(_r(f"Mã băm SHA-256 · tệp gốc: {ctx.get('source_sha256') or '—'} · văn bản gốc đã trích: "
                       f"{ctx['base_sha256']} · văn bản sau sửa: {ctx['final_sha256']}", size=14, color="64748B"),
                    '<w:pPr><w:spacing w:before="240"/></w:pPr>'))
    return _new_docx(paras)
