"""The working paper: what an auditor files, in Vietnamese, printable to PDF.

`evidence_pack.md` is a dump in document order and in English. An auditor files
something else: objective, scope and sources, the procedure and the policies
behind it, the work list in the order it was worked, the result of each item
with its page, what was deliberately NOT examined and why, who reviewed what,
and two signatures. ISA 230 asks a working paper to let an experienced auditor
with no connection to the engagement understand what was done, on what, and
what was concluded -- that is the test this page is written against.

The page is rendered by the API from a saved run plus the review trail, so a
decision recorded a minute ago is in the next print. "In / Lưu PDF" in the
browser turns it into the PDF the export screen used to promise; no PDF engine
is bundled because the browser already has a better one.
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from html import escape

from quantum_gw.domain.models import AnalysisResult

STATUS_VI = {
    "SUPPORTED": "Được ủng hộ",
    "PARTIALLY_SUPPORTED": "Ủng hộ một phần",
    "UNSUPPORTED": "Chưa được chứng minh trong kho đã kiểm",
    "CONTRADICTED": "Mâu thuẫn với nguồn",
    "INSUFFICIENT_EVIDENCE": "Chưa đủ bằng chứng",
}
RELATION_VI = {"SUPPORTS": "ủng hộ", "CONTRADICTS": "mâu thuẫn", "PARTIAL": "một phần", "CONTEXT": "bối cảnh"}
DECISION_VI = {
    "CONFIRM": "Xác nhận kết quả AI",
    "OVERRIDE": "Sửa kết quả AI",
    "ABSTAIN": "Chưa đủ căn cứ để quyết",
    "REQUEST_EVIDENCE": "Yêu cầu thêm tài liệu",
    "REOPEN": "Mở lại",
}
ROLE_VI = {"claim_source": "Nguồn tuyên bố", "evidence": "Chứng cứ", "reference": "Tham chiếu"}
CHECK_VI = {"cross_foot": "Cộng lại bảng (cross-foot)", "cross_document": "Đối chiếu giữa tài liệu"}
# The quality gates in the reviewer's language; G7's detail is generated per run
# and kept as the pipeline wrote it.
GATE_VI = {
    "G0": ("Nguồn gốc dữ liệu", "mọi đoạn văn phải giữ được tài liệu và vị trí gốc."),
    "G1": ("Trích tuyên bố", "mọi tuyên bố phải giữ được đoạn và tài liệu nguồn."),
    "G2": ("Bằng chứng truy xuất", "mỗi tuyên bố phải có bằng chứng hợp lệ hoặc ghi rõ “chưa đủ bằng chứng”."),
    "G3": ("So sánh số tất định", "mọi phép so số liệu phải chạy bằng mã."),
    "G4": ("Trích dẫn", "mọi bằng chứng quyết định phải có vị trí trong tài liệu."),
    "G5": ("Soát rủi ro", "có trường hợp rủi ro cao, xung đột pháp lý hoặc kết luận do mô hình đề xuất — "
                          "chỉ phát hành sau khi người soát xét phê duyệt."),
    "G6": ("Tái lập", "manifest phải ghi cấu hình, mã băm đầu vào và kế hoạch chạy."),
    "G7": ("Đối chiếu pháp lý", None),
}

_CSS = """
@page { size: A4; margin: 16mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Noto Sans", Arial, sans-serif; color: #1f2933; font-size: 10.5pt;
       line-height: 1.45; margin: 0 auto; max-width: 900px; padding: 24px; background: #fff; }
h1 { font-size: 17pt; margin: 0 0 2px; color: #0f3d2e; }
h2 { font-size: 12.5pt; margin: 22px 0 6px; padding-bottom: 3px; border-bottom: 1.5px solid #0f3d2e; color: #0f3d2e; }
h3 { font-size: 11pt; margin: 14px 0 4px; }
p { margin: 4px 0; }
table { width: 100%; border-collapse: collapse; margin: 6px 0; }
th, td { border: 1px solid #cbd2d9; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #f0f4f8; font-weight: 600; }
.meta td:first-child { width: 32%; color: #52606d; }
.muted { color: #616e7c; font-size: 9.5pt; }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.item { border: 1px solid #cbd2d9; border-radius: 6px; padding: 8px 10px; margin: 8px 0; page-break-inside: avoid; }
.quote { border-left: 3px solid #0f3d2e; padding-left: 8px; margin: 4px 0; }
.tag { display: inline-block; border-radius: 10px; padding: 0 7px; font-size: 9pt; background: #e4e7eb; }
.warn { background: #fff8e1; border: 1px solid #f0c36d; padding: 6px 9px; border-radius: 6px; }
.sign { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 18px; }
.sign div { border-top: 1px solid #52606d; padding-top: 4px; min-height: 70px; }
.toolbar { position: sticky; top: 0; background: #fff; padding: 8px 0; margin-bottom: 8px; border-bottom: 1px solid #e4e7eb; }
.toolbar button { background: #0f3d2e; color: #fff; border: 0; border-radius: 6px; padding: 7px 14px; font-weight: 600; cursor: pointer; }
@media print { .toolbar { display: none; } body { padding: 0; } a { color: inherit; text-decoration: none; } }
"""


def _e(value) -> str:
    return escape(str(value if value is not None else ""))


def _latest_decisions(decisions: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for record in sorted(decisions, key=lambda r: r.get("decided_at", "")):
        latest[record.get("claim_id", "")] = record
    return latest


def render_workpaper(
    result: AnalysisResult,
    decisions: list[dict] | None = None,
    label: str = "",
    auto_print: bool = False,
) -> str:
    decisions = decisions or []
    latest = _latest_decisions(decisions)
    verifications = {v.claim.claim_id: v for v in result.verifications}
    claims = {c.claim_id: c for c in result.claims}
    figures = {f.figure_id: f for f in result.disclosed_figures}
    legal = {item.get("claim_id"): item for item in result.legal_checks}
    queue = sorted((p for p in result.priorities if p.get("in_queue")), key=lambda p: p.get("rank", 0))
    manifest = result.manifest
    created = manifest.created_at.astimezone(UTC).strftime("%d/%m/%Y %H:%M UTC")
    entity = ", ".join(result.entity) or "(chưa xác định — điền tay)"
    statuses = Counter(v.status.value for v in result.verifications)
    reviewers = sorted({d.get("reviewer", "") for d in decisions if d.get("reviewer")})

    out: list[str] = [
        "<!doctype html><html lang='vi'><head><meta charset='utf-8'>",
        f"<title>Giấy làm việc — {_e(label or result.run_id)}</title>",
        f"<style>{_CSS}</style></head><body>",
        "<div class='toolbar'><button onclick='window.print()'>In / Lưu PDF</button> "
        "<span class='muted'>Chọn “Lưu dưới dạng PDF” trong hộp thoại in.</span></div>",
        "<h1>GIẤY LÀM VIỆC — Sàng lọc tuyên bố môi trường</h1>",
        f"<p class='muted'>GreenScan AI · phiên <code>{_e(result.run_id)}</code> · lập lúc {_e(created)}</p>",
        "<table class='meta'>",
        f"<tr><td>Đơn vị được xem xét</td><td><b>{_e(entity)}</b></td></tr>",
        f"<tr><td>Tên phiên</td><td>{_e(label or '—')}</td></tr>",
        "<tr><td>Mục tiêu thủ tục</td><td>Xác định các tuyên bố và số liệu môi trường trong tài liệu, "
        "mức độ đầy đủ của bằng chứng đi kèm, và thứ tự nên soát xét. "
        "<b>Không</b> nhằm kết luận doanh nghiệp vi phạm pháp luật hay “tẩy xanh”.</td></tr>",
        f"<tr><td>Người soát xét đã ghi nhận</td><td>{_e(', '.join(reviewers) or 'chưa có')}</td></tr>",
        "</table>",
    ]

    # 1. sources
    out.append("<h2>1. Phạm vi tài liệu</h2><table><tr><th>#</th><th>Tài liệu</th><th>Mã băm SHA-256 (rút gọn)</th></tr>")
    for index, (key, digest) in enumerate(manifest.input_hashes.items(), start=1):
        name = key.split(":", 1)[1] if ":" in key else key
        out.append(f"<tr><td class='num'>{index}</td><td>{_e(name)}</td><td><code>{_e(digest[:16])}…</code></td></tr>")
    out.append("</table>")
    corpus = result.corpus or {}
    if corpus:
        coverage = round(100 * float(corpus.get("coverage") or 0))
        missing = "; ".join(corpus.get("missing") or []) or "—"
        rule = ("Kho đủ để ghi “chưa được chứng minh trong kho đã kiểm” khi không tìm thấy bằng chứng."
                if corpus.get("sufficient_for_absence") else
                "Kho chưa đủ để suy ra “không có bằng chứng”: mọi trường hợp không tìm thấy dừng ở “chưa đủ bằng chứng”.")
        out.append(f"<p>Độ phủ kho tài liệu: <b>{coverage}%</b> · năm: {_e(', '.join(map(str, corpus.get('years') or [])) or '—')} · "
                   f"còn thiếu: {_e(missing)}.</p><p class='muted'>{_e(rule)}</p>")

    # 2. procedure
    out.append("<h2>2. Thủ tục đã thực hiện</h2><ul>")
    out.append(f"<li>Đọc {result.summary.total_documents} tài liệu thành {result.summary.total_chunks} đoạn có số trang.</li>")
    out.append(f"<li>Trích {result.summary.total_claims} tuyên bố và {len(result.disclosed_figures)} số liệu công bố "
               "bằng luật tất định (không dùng mô hình).</li>")
    out.append("<li>Tìm bằng chứng cho từng tuyên bố; so sánh số liệu bằng mã, chỉ khi cùng chỉ số, đơn vị, kỳ và phạm vi.</li>")
    if manifest.prompt_version:
        out.append(f"<li>Mô hình ngôn ngữ đọc các cặp luật chưa quyết được (<code>{_e(manifest.prompt_version)}</code>); "
                   "kết luận của mô hình không tự đứng một mình và luôn chuyển người xác nhận.</li>")
    else:
        out.append("<li>Không gọi mô hình ngôn ngữ trong phiên này (chế độ ngoại tuyến).</li>")
    out.append(f"<li>Thực hiện {len(result.figure_checks)} thủ tục trên số liệu công bố (cộng lại bảng, đối chiếu giữa tài liệu).</li>")
    out.append("<li>Đối chiếu văn bản pháp lý theo ngày hiệu lực; xếp thứ tự soát theo chính sách ưu tiên.</li></ul>")
    out.append("<table class='meta'>"
               f"<tr><td>Phiên bản pipeline · cấu hình</td><td><code>{_e(manifest.pipeline_version)}</code> · "
               f"<code>{_e(manifest.config_hash[:12])}</code></td></tr>"
               f"<tr><td>Bộ quy tắc pháp lý</td><td><code>{_e(manifest.rule_pack_version)}</code></td></tr>"
               f"<tr><td>Chính sách ưu tiên</td><td><code>{_e(queue[0].get('policy_version') if queue else '—')}</code></td></tr>"
               "</table>")
    dist = " · ".join(f"{STATUS_VI.get(k, k)}: {n}" for k, n in statuses.most_common())
    out.append(f"<p class='muted'>Phân bố kết quả trên toàn bộ tuyên bố: {_e(dist)}.</p>")

    # 3. queue and results
    out.append(f"<h2>3. Hàng đợi soát và kết quả ({len(queue)} mục)</h2>")
    out.append("<p class='muted'>Thứ tự là thứ tự nên mở, không phải mức độ “xấu”. Điểm ưu tiên ghép bốn yếu tố "
               "(trọng yếu, liên quan pháp lý, khoảng trống bằng chứng, bất thường so với kỳ trước).</p>")
    for item in queue:
        out.append(_queue_item(item, verifications, claims, figures, legal, latest))

    # 4. figure procedures
    if result.figure_checks:
        out.append("<h2>4. Thủ tục trên số liệu công bố</h2><table><tr><th>Thủ tục</th><th>Kết quả</th><th>Phép tính</th><th>Ghi chú</th></tr>")
        for check in result.figure_checks:
            outcome = "Nhất quán" if check.status == "CONSISTENT" else "Không nhất quán — cần người xem"
            out.append(f"<tr><td>{_e(CHECK_VI.get(check.kind, check.kind))}</td><td>{_e(outcome)}</td>"
                       f"<td><code>{_e(check.calculation)}</code></td><td>{_e(check.note)}</td></tr>")
        out.append("</table>")

    # 5. not examined
    out.append("<h2>5. Những gì KHÔNG được kiểm và vì sao</h2><ul>")
    if result.scope_note:
        out.append(f"<li>{_e(result.scope_note).replace('**', '')}</li>")
    out.append("<li>Yếu tố “bất thường so với kỳ trước” chưa được tính (chưa có thủ tục so sánh chéo kỳ); "
               "điểm ưu tiên không cộng phần này — đây <b>không</b> phải kết luận “không có bất thường”.</li>")
    rule_pack = (manifest.rule_pack_version or "").lower()
    if "draft" in rule_pack or "v0.1" in rule_pack:
        out.append("<li>Bộ quy tắc pháp lý đang ở bản nháp: lớp pháp lý chỉ xác định văn bản liên quan theo ngày hiệu lực, "
                   "chưa kết luận nghĩa vụ cụ thể đã được đáp ứng hay chưa.</li>")
    gate_notes = [g for g in result.quality_gates if g.status != "PASS"]
    for gate in gate_notes:
        name, detail = GATE_VI.get(gate.gate_id, (gate.name, None))
        out.append(f"<li>Cổng {_e(gate.gate_id)} ({_e(name)}): {_e(detail or gate.details)}</li>")
    out.append("<li>Thiếu bằng chứng trong kho <b>không</b> có nghĩa doanh nghiệp vi phạm; kết quả là sàng lọc, "
               "không phải kết luận pháp lý hay ý kiến kiểm toán.</li></ul>")

    # 6. review trail
    out.append("<h2>6. Quyết định của người soát xét</h2>")
    if decisions:
        out.append("<table><tr><th>Thời điểm</th><th>Người</th><th>Mục</th><th>Quyết định</th><th>Ghi chú</th></tr>")
        for record in sorted(decisions, key=lambda r: r.get("decided_at", "")):
            claim = claims.get(record.get("claim_id", ""))
            what = (claim.text[:90] + "…") if claim and len(claim.text) > 90 else (claim.text if claim else record.get("claim_id", ""))
            verdict = record.get("reviewer_status")
            decision = DECISION_VI.get(record.get("decision", ""), record.get("decision", ""))
            if verdict:
                decision += f" → {STATUS_VI.get(verdict, verdict)}"
            out.append(f"<tr><td class='num'>{_e(str(record.get('decided_at', ''))[:16].replace('T', ' '))}</td>"
                       f"<td>{_e(record.get('reviewer'))}</td><td>{_e(what)}</td><td>{_e(decision)}</td>"
                       f"<td>{_e(record.get('comment'))}</td></tr>")
        out.append("</table>")
    else:
        out.append("<p class='warn'>Chưa có quyết định nào được ghi. Giấy làm việc này chỉ là kết quả sàng lọc tự động "
                   "cho tới khi người soát xét xác nhận từng mục.</p>")

    out.append("<div class='sign'><div><b>Người thực hiện</b><br><span class='muted'>Họ tên, chữ ký, ngày</span></div>"
               "<div><b>Người soát xét</b><br><span class='muted'>Họ tên, chữ ký, ngày</span></div></div>")
    out.append(f"<p class='muted' style='margin-top:14px'>In lúc {_e(datetime.now(UTC).strftime('%d/%m/%Y %H:%M UTC'))}. "
               "Tái lập: chạy lại cùng tài liệu (mã băm ở mục 1) với cùng cấu hình cho cùng kết quả.</p>")
    if auto_print:
        out.append("<script>window.addEventListener('load', () => setTimeout(() => window.print(), 300))</script>")
    out.append("</body></html>")
    return "".join(out)


def _queue_item(item, verifications, claims, figures, legal, latest) -> str:
    rank = item.get("rank")
    score = item.get("priority_score", 0)
    reasons = "".join(f"<li>{_e(r).replace('**', '')}</li>" for r in item.get("reasons", []))
    if item.get("item_type") == "figure":
        figure = figures.get(item.get("item_id"))
        where = f"{_e(figure.source_name)} · tr. {_e(figure.source_page)}" if figure else ""
        body = (f"<div class='quote'>{_e(figure.label) if figure else ''}: <b>{figure.value:,.2f} {_e(figure.unit)}</b>"
                f"{(' · kỳ ' + _e(figure.period)) if figure and figure.period else ''}</div>") if figure else ""
        return (f"<div class='item'><p><b>#{rank}</b> <span class='tag'>Số liệu công bố</span> "
                f"<span class='muted'>ưu tiên {score:.0f} · {where}</span></p>{body}"
                f"<p class='muted'>Vì sao mở trước:</p><ul>{reasons}</ul></div>")

    claim_id = item.get("item_id")
    verification = verifications.get(claim_id)
    claim = claims.get(claim_id)
    if verification is None or claim is None:
        return ""
    status = STATUS_VI.get(verification.status.value, verification.status.value)
    page = f" · tr. {_e(claim.source_page)}" if claim.source_page is not None else ""
    parts = [
        f"<div class='item'><p><b>#{rank}</b> <span class='tag'>Tuyên bố</span> "
        f"<span class='muted'>ưu tiên {score:.0f} · {_e(claim.source_name)}{page}</span></p>",
        f"<div class='quote'>“{_e(claim.text)}”</div>",
        f"<p><b>Kết quả sàng lọc:</b> {_e(status)}. {_e(verification.rationale)}</p>",
    ]
    if verification.requires_llm_review:
        parts.append("<p class='muted'>Có phần do mô hình ngôn ngữ đề xuất — cần người xác nhận.</p>")
    evidence = [e for e in verification.evidence if e.relation in {"SUPPORTS", "CONTRADICTS", "PARTIAL"}][:3]
    if evidence:
        parts.append("<p class='muted'>Bằng chứng chính:</p><ul>")
        for e in evidence:
            where = f"{_e(e.source_name)}" + (f", tr. {_e(e.page)}" if e.page is not None else "")
            parts.append(f"<li><i>{_e(RELATION_VI.get(e.relation, e.relation))}</i> — {where}: "
                         f"“{_e(e.text[:260])}{'…' if len(e.text) > 260 else ''}”</li>")
        parts.append("</ul>")
    check = legal.get(claim_id)
    if check:
        sources = ", ".join(
            str(s.get("document") or s.get("id")) for s in (check.get("applicable_sources") or [])[:3] if isinstance(s, dict)
        )
        if sources:
            parts.append(f"<p class='muted'>Văn bản liên quan đang hiệu lực: {_e(sources)}.</p>")
    parts.append(f"<p class='muted'>Vì sao mở trước:</p><ul>{reasons}</ul>")
    decision = latest.get(claim_id)
    if decision:
        verdict = decision.get("reviewer_status")
        text = DECISION_VI.get(decision.get("decision", ""), decision.get("decision", ""))
        if verdict:
            text += f" → {STATUS_VI.get(verdict, verdict)}"
        parts.append(f"<p><b>Người soát xét:</b> {_e(decision.get('reviewer'))} — {_e(text)}"
                     f"{(': ' + _e(decision.get('comment'))) if decision.get('comment') else ''}</p>")
    else:
        parts.append("<p><b>Người soát xét:</b> <span class='muted'>chưa xem</span></p>")
    parts.append("</div>")
    return "".join(parts)

