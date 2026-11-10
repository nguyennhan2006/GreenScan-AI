import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { studioDoc, studioExportUrl, studioRestore, studioRun, studioSave } from '../api.js'
import { Link } from '../lib/router.jsx'
import {
  claimsField, createEditor, flash, gotoPage, lintFromClaims, loadClaims, pageAtTop, reveal, searchText, setClaims,
  setZoom, suggestionChange,
} from '../lib/studioEditor.js'
import { DocIcon, FormatBadge, Icon } from '../components/icons.jsx'
import { Leaf } from '../components/Shell.jsx'
import { labelOf } from '../lib/labels'

/**
 * GreenScan Studio: the report under review, linted by the analysis, edited like code.
 *
 * Left: documents and the Problems panel. Centre: a toolbar (page, zoom, search)
 * over the report, one paragraph per line, page of the original in the gutter,
 * claims tinted by severity with a hover card. Right: the Inspector -- suggested
 * edits as đánh dấu sửa đổi, the evidence (opened on the original page), attributes,
 * legal basis with its verification label. Bottom: change log, versions, export.
 * Evidence documents open read-only and stay that way.
 */

const API = import.meta.env.VITE_API_URL || '/api'
const SEV = {
  error: { label: 'Nghiêm trọng', dot: 'bg-red-500', text: 'text-red-700', chip: 'bg-red-50 text-red-700 ring-red-200', head: 'text-red-700' },
  warning: { label: 'Cần xem', dot: 'bg-amber-500', text: 'text-amber-700', chip: 'bg-amber-50 text-amber-800 ring-amber-200', head: 'text-amber-600' },
  info: { label: 'Thông tin', dot: 'bg-sky-500', text: 'text-sky-700', chip: 'bg-sky-50 text-sky-800 ring-sky-200', head: 'text-sky-700' },
}
const RELATION = {
  SUPPORTS: ['Ủng hộ', 'bg-emerald-50 text-emerald-800 ring-emerald-200'],
  PARTIAL: ['Một phần', 'bg-amber-50 text-amber-800 ring-amber-300'],
  CONTRADICTS: ['Mâu thuẫn', 'bg-red-50 text-red-700 ring-red-200'],
  CONTEXT: ['Bối cảnh', 'bg-slate-100 text-slate-600 ring-slate-200'],
}
const SOURCE_TYPE = {
  internal: 'Nội bộ doanh nghiệp', financial: 'Báo cáo tài chính', environmental: 'Dữ liệu môi trường',
  legal: 'Văn bản pháp luật', external: 'Bên thứ ba', standard: 'Tiêu chuẩn',
}
const ACTOR = { user: 'Người', 'ai-rule': 'máy · quy tắc', 'ai-llm': 'AI · LLM', system: 'Hệ thống' }
const ACTION = { accept: 'Chấp nhận', reject: 'Từ chối', edit: 'Sửa tay', ignore: 'Bỏ qua', save: 'Lưu phiên bản', restore: 'Khôi phục', rework: 'Sửa lại đề xuất' }
const ACTION_TONE = { accept: 'text-emerald-700', reject: 'text-red-700', ignore: 'text-slate-500', rework: 'text-emerald-700', edit: 'text-slate-700' }
const IGNORE_REASONS = ['Không phải tuyên bố môi trường', 'Đã có bằng chứng ở phần khác', 'Ngoài phạm vi soát xét', 'Câu bị cắt hoặc ghép sai']
const EXPORTS = [
  ['docx_tracked', 'DOCX có đánh dấu sửa đổi', 'Mở bằng Word: thấy từng chỗ gạch bỏ / chèn, ai sửa, lúc nào.'],
  ['docx_clean', 'DOCX bản sạch', 'Mọi thay đổi đã áp dụng, không còn dấu sửa.'],
  ['pdf', 'PDF bản sạch + phụ lục', 'Dựng lại từ văn bản đã sửa; kèm phụ lục rà soát.'],
  ['review_html', 'Báo cáo rà soát GreenScan', 'Phát hiện, quyết định, bằng chứng, căn cứ, nhật ký. In ra PDF được.'],
  ['audit_json', 'Nhật ký thao tác (tệp dữ liệu .json)', 'Mọi thao tác kèm mã băm của bản gốc và bản cuối.'],
]
const ZOOMS = [80, 90, 100, 110, 125, 150]
const BASE_FONT = 15
const TOUR = [
  ['explorer', 'Tài liệu và vấn đề phát hiện', 'Bên trái là các tài liệu của phiên. Báo cáo cần kiểm sửa được; tài liệu bằng chứng có ổ khóa, chỉ đọc. Danh sách vấn đề nhóm các tuyên bố theo mức độ.'],
  ['editor', 'Báo cáo như mã nguồn', 'Tuyên bố được tô màu: đỏ là nghiêm trọng, vàng là cần xem, xanh là thông tin. Di chuột vào để xem kết luận và bằng chứng. F8 / Shift+F8 để sang mục kế tiếp / trước đó. Thanh trên cùng: nhảy trang, phóng to, tìm chữ.'],
  ['inspector', 'Đề xuất sửa hiện như đánh dấu sửa đổi', 'Ctrl+. mở đề xuất. Phần đỏ gạch bỏ, phần xanh chèn thêm. Ctrl+Enter chấp nhận, Esc từ chối. Máy không bao giờ thêm số liệu: chỉ để chỗ trống “[bổ sung: …]”. Tab Bằng chứng mở thẳng trang gốc của nguồn.'],
  ['bottom', 'Nhật ký và xuất bản', 'Mọi thao tác được ghi lại: ai, lúc nào, quy tắc nào. Ctrl+S lưu phiên bản. Xuất DOCX có đánh dấu sửa đổi, PDF, và báo cáo rà soát.'],
]

const pageUrl = (doc, page, q, zoom) => `${API}/v1/documents/${doc}/page/${page}?q=${encodeURIComponent((q || '').slice(0, 80))}${zoom ? `&zoom=${zoom}` : ''}`
const initials = (name) => (name || '?').trim().split(/\s+/).map((w) => w[0]).slice(-2).join('').toUpperCase()
const pct = (x) => (x == null ? '—' : `${Math.round(x * 100)}%`)

function Btn({ onClick, title, children, tone = 'default', disabled, className = '', size = 'sm' }) {
  const tones = {
    default: 'border border-slate-300 bg-white text-slate-700 shadow-xs hover:border-emerald-600 hover:bg-emerald-50 hover:text-emerald-900',
    primary: 'border border-[#0F3D2E] bg-[#0F3D2E] text-white shadow-sm hover:bg-[#14533e]',
    danger: 'border border-red-300 bg-white text-red-700 hover:border-red-400 hover:bg-red-50',
    ghost: 'border border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900',
  }
  const sizes = { xs: 'gap-1 px-2 py-1 text-[11px]', sm: 'gap-1.5 px-3 py-1.5 text-xs', md: 'gap-1.5 px-4 py-2 text-[13px]' }
  return (
    <button type="button" title={title} disabled={disabled} onClick={onClick}
      className={`inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${sizes[size]} ${tones[tone]} ${className}`}>
      {children}
    </button>
  )
}

function IconBtn({ icon, title, onClick, disabled, active, className = '' }) {
  return (
    <button type="button" title={title} aria-label={title} onClick={onClick} disabled={disabled}
      className={`flex h-8 w-8 items-center justify-center rounded-lg transition disabled:cursor-not-allowed disabled:opacity-35 ${active ? 'bg-emerald-100 text-emerald-900' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'} ${className}`}>
      <Icon name={icon} className="h-4 w-4" />
    </button>
  )
}

function Card({ children, className = '' }) {
  return <section className={`rounded-xl border border-slate-200/80 bg-white shadow-[0_1px_2px_rgba(15,23,42,.04)] ${className}`}>{children}</section>
}

function SectionTitle({ children, right, className = '' }) {
  return (
    <div className={`flex items-center justify-between gap-2 ${className}`}>
      <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-slate-500">{children}</p>
      {right}
    </div>
  )
}

function Segments({ segments }) {
  return (
    <span className="leading-relaxed">
      {segments.map((s, i) => s.op === 'equal'
        ? <span key={i} className="text-slate-600">{s.text.length > 90 && i === 0 ? '…' + s.text.slice(-90) : s.text}</span>
        : s.op === 'del'
          ? <del key={i} className="rounded bg-red-100 px-0.5 text-red-800 decoration-red-500">{s.text}</del>
          : <ins key={i} className="rounded bg-emerald-100 px-1 py-px font-medium text-emerald-900 no-underline ring-1 ring-emerald-200">{s.text}</ins>)}
    </span>
  )
}

function Problems({ claims, visible, unanchored, filter, setFilter, selectedId, onPick, onHover }) {
  const rows = useRef(null)
  useEffect(() => {
    rows.current?.querySelector('[data-selected="true"]')?.scrollIntoView({ block: 'nearest' })
  }, [selectedId])
  const number = new Map(visible.map((c, i) => [c.id, i + 1]))
  const groups = ['error', 'warning', 'info'].map((sev) => [sev, visible.filter((c) => c.severity === sev)])
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="space-y-2.5 px-4 pb-3">
        <label className="relative block">
          <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input value={filter.q} onChange={(e) => setFilter({ ...filter, q: e.target.value })} placeholder="Lọc theo chữ trong tuyên bố…"
            className="w-full rounded-lg border border-slate-200 bg-slate-50/60 py-2 pl-9 pr-3 text-[13px] placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" />
        </label>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(SEV).map(([k, v]) => (
            <button key={k} type="button" title={`Hiện/ẩn mức “${v.label}”`} onClick={() => setFilter({ ...filter, sev: { ...filter.sev, [k]: !filter.sev[k] } })}
              className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 transition ${filter.sev[k] ? v.chip : 'bg-white text-slate-400 ring-slate-200'} hover:ring-emerald-400`}>
              <span className={`h-2 w-2 rounded-full ${filter.sev[k] ? v.dot : 'bg-slate-300'}`} />{v.label}
              <span className="tabular-nums">{claims.filter((c) => c.severity === k && !c.resolved).length}</span>
            </button>
          ))}
          <button type="button" title="Hiện cả các mục đã xử lý" onClick={() => setFilter({ ...filter, resolved: !filter.resolved })}
            className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 transition hover:ring-emerald-400 ${filter.resolved ? 'bg-emerald-50 text-emerald-800 ring-emerald-200' : 'bg-white text-slate-500 ring-slate-200'}`}>
            <Icon name="check" className="h-3.5 w-3.5" strokeWidth={2.5} />Đã xử lý <span className="tabular-nums">{claims.filter((c) => c.resolved).length}</span>
          </button>
        </div>
      </div>
      <div ref={rows} className="gs-scroll min-h-0 flex-1 overflow-y-auto border-t border-slate-100">
        {visible.length === 0 && <p className="px-4 py-6 text-center text-xs text-slate-400">Không có mục nào khớp bộ lọc.</p>}
        {groups.map(([sev, list]) => list.length > 0 && (
          <div key={sev}>
            <p className={`sticky top-0 z-10 bg-white/95 px-4 pb-1.5 pt-3 text-[11px] font-bold uppercase tracking-[0.08em] backdrop-blur ${SEV[sev].head}`}>{SEV[sev].label} · {list.length}</p>
            {list.map((c) => {
              const on = selectedId === c.id
              return (
                <button key={c.id} type="button" data-selected={on} onClick={() => onPick(c.id)} onMouseEnter={() => onHover(c.id)} onMouseLeave={() => onHover(null)}
                  title="Bấm để nhảy tới tuyên bố; di chuột để tô sáng trong văn bản"
                  className={`group flex w-full items-start gap-2.5 border-l-[3px] py-2 pl-3 pr-4 text-left transition ${on ? 'border-emerald-600 bg-emerald-50' : 'border-transparent hover:bg-slate-50'} ${c.resolved ? 'opacity-55' : ''}`}>
                  <span className="w-5 shrink-0 pt-px text-right text-xs tabular-nums text-slate-400">{number.get(c.id)}</span>
                  <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${c.resolved ? 'bg-emerald-500' : SEV[c.severity].dot}`} />
                  <span className="min-w-0 flex-1">
                    <span className={`block truncate text-[13px] ${on ? 'font-semibold text-slate-900' : 'font-medium text-slate-800'}`}>{c.resolved ? '✓ ' : ''}{c.text}</span>
                    <span className="mt-0.5 block truncate text-xs text-slate-500">
                      {c.page ? `tr. ${c.page} · ` : ''}{c.in_queue ? <span className="font-medium text-emerald-700">Hàng đợi #{c.priority_rank} · </span> : ''}{c.message}
                    </span>
                  </span>
                </button>
              )
            })}
          </div>
        ))}
        {unanchored.length > 0 && (
          <details className="border-t border-slate-100 px-4 py-3 text-xs text-slate-500">
            <summary className="cursor-pointer font-semibold" title="Tuyên bố có trong kết quả phân tích nhưng không tìm thấy nguyên văn trong văn bản đã trích (thường do câu vắt qua hai khối của PDF)">
              Không neo được vào văn bản · {unanchored.length}
            </summary>
            <ul className="mt-1.5 space-y-1">{unanchored.map((u) => <li key={u.claim_id}>tr.{u.page ?? '—'} · {u.text.slice(0, 110)}…</li>)}</ul>
          </details>
        )}
      </div>
    </div>
  )
}

function Inspector({ claim, docId, tab, setTab, focused, setFocused, onAccept, onReject, onRework, onIgnore, editable, nav, onOpenEvidence }) {
  const [rework, setRework] = useState(null)
  const [ignoring, setIgnoring] = useState(false)
  const [reason, setReason] = useState('')
  useEffect(() => { setRework(null); setIgnoring(false); setReason('') }, [claim?.id])
  const header = (
    <SectionTitle className="px-4 pt-4" right={claim && (
      <div className="flex items-center gap-1">
        <IconBtn icon="chevronLeft" title="Mục trước (Shift+F8)" onClick={nav.prev} disabled={!nav.hasPrev} />
        <span className="min-w-[3.5rem] text-center text-xs tabular-nums text-slate-500">{nav.index > 0 ? `${nav.index} / ${nav.total}` : `— / ${nav.total}`}</span>
        <IconBtn icon="chevronRight" title="Mục kế tiếp (F8)" onClick={nav.next} disabled={!nav.hasNext} />
        <IconBtn icon="x" title="Bỏ chọn" onClick={nav.close} />
      </div>
    )}>Bảng chi tiết</SectionTitle>
  )
  if (!claim) {
    return (
      <div className="flex min-h-0 flex-1 flex-col">
        {header}
        <div className="m-4 rounded-xl border border-dashed border-slate-300 bg-slate-50/60 p-5 text-center">
          <span className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-700"><Icon name="file" className="h-5 w-5" /></span>
          <p className="mt-3 text-sm font-semibold text-slate-800">Chưa chọn tuyên bố</p>
          <p className="mt-1 text-[13px] leading-relaxed text-slate-500">Đặt con trỏ vào một câu được tô màu, bấm một dòng trong danh sách vấn đề, hoặc nhấn <kbd className="rounded border border-slate-300 bg-white px-1.5 font-mono text-[11px]">F8</kbd>.</p>
          {nav.total > 0 && <Btn tone="primary" className="mt-4" onClick={nav.first}>Mở mục đầu tiên <Icon name="arrowRight" className="h-3.5 w-3.5" /></Btn>}
        </div>
      </div>
    )
  }
  const tabs = [['fix', `Sửa nhanh (${claim.suggestions.length})`], ['evidence', `Bằng chứng (${claim.evidence.length})`], ['attrs', 'Thuộc tính'], ['legal', 'Pháp lý']]
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {header}
      <div className="px-4 pb-3 pt-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ring-1 ${SEV[claim.severity].chip}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${SEV[claim.severity].dot}`} />{SEV[claim.severity].label}
          </span>
          {claim.in_queue && <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 ring-1 ring-emerald-200" title={claim.priority_reasons.join('\n')}>Hàng đợi #{claim.priority_rank}</span>}
          {claim.resolved && <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold text-slate-600"><Icon name="check" className="h-3 w-3" strokeWidth={3} />đã xử lý</span>}
        </div>
        <h2 className="mt-2 text-lg font-bold leading-snug tracking-tight text-slate-900">{claim.status_label}</h2>
        <p className="mt-1 text-[13px] leading-relaxed text-slate-600">{claim.message}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {claim.page && (
            <a href={pageUrl(docId, claim.page, claim.text)} target="_blank" rel="noreferrer" title="Mở ảnh trang gốc, câu này được tô sáng"
              className="inline-flex items-center gap-1.5 rounded-md bg-sky-50 px-2 py-1 text-xs font-semibold text-sky-800 ring-1 ring-sky-100 transition hover:bg-sky-100">
              <Icon name="file" className="h-3.5 w-3.5" />Trang {claim.page} của bản gốc
            </a>
          )}
        </div>
        <p className="mt-2 text-xs leading-relaxed text-slate-500" title={claim.escalation?.reason}>
          LLM: {claim.escalation?.route === 'llm' ? 'được phép leo thang' : claim.escalation?.route === 'human' ? 'chuyển người duyệt' : 'không leo thang'} · {claim.escalation?.reason}
        </p>
      </div>
      <div className="flex gap-1 border-b border-slate-200 px-3" role="tablist">
        {tabs.map(([k, l]) => (
          <button key={k} type="button" role="tab" aria-selected={tab === k} onClick={() => setTab(k)}
            className={`-mb-px whitespace-nowrap border-b-[2.5px] px-2 py-2.5 text-[13px] font-semibold transition ${tab === k ? 'border-emerald-600 text-emerald-900' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>{l}</button>
        ))}
      </div>
      <div className="gs-scroll min-h-0 flex-1 space-y-3 overflow-y-auto bg-slate-50/50 p-3 text-[13px]">
        {tab === 'fix' && (
          <>
            {!editable && <p className="flex items-center gap-2 rounded-lg bg-slate-100 p-3 text-slate-600"><Icon name="lock" className="h-4 w-4" />Tài liệu bằng chứng: chỉ đọc.</p>}
            {claim.suggestions.length === 0 && <p className="rounded-lg border border-slate-200 bg-white p-4 text-center text-slate-500">Không còn đề xuất tự động cho tuyên bố này.</p>}
            {claim.suggestions.map((s, i) => (
              <div key={s.suggestion_id} onMouseEnter={() => setFocused(i)}
                className={`rounded-xl border bg-white p-3.5 transition ${focused === i ? 'border-emerald-500 shadow-md shadow-emerald-900/5 ring-1 ring-emerald-100' : 'border-slate-200 hover:border-emerald-300'}`}>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-semibold text-slate-900">{s.title}</span>
                  <span className="shrink-0 rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[10.5px] font-medium text-slate-600" title="Mã quy tắc sinh đề xuất">{s.rule_code}</span>
                </div>
                <div className="mt-2.5 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5 text-[13px]"><Segments segments={s.segments} /></div>
                <p className="mt-2.5 text-slate-700"><b className="font-semibold text-slate-900">Lý do:</b> {s.reason}</p>
                <ul className="mt-1.5 space-y-1">
                  {s.basis.map((b, j) => (
                    <li key={j} className="text-xs leading-relaxed text-slate-500">
                      § {b.label} — <span className={`font-medium ${/chưa|không ràng buộc/i.test(b.verification) ? 'text-amber-700' : 'text-emerald-700'}`}>{b.verification}</span>
                    </li>
                  ))}
                </ul>
                {rework === i ? (
                  <ReworkBox initial={s.after} onCancel={() => setRework(null)} onSave={(text) => { onRework(s, text); setRework(null) }} />
                ) : editable && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Btn tone="primary" onClick={() => onAccept(s)} title="Áp dụng đề xuất vào văn bản (Ctrl+Enter)"><Icon name="check" className="h-3.5 w-3.5" strokeWidth={2.5} />Chấp nhận</Btn>
                    <Btn tone="danger" onClick={() => onReject(s)} title="Bỏ đề xuất này, ghi vào nhật ký (Esc)"><Icon name="x" className="h-3.5 w-3.5" strokeWidth={2.5} />Từ chối</Btn>
                    <Btn onClick={() => setRework(i)} title="Sửa câu đề xuất trước khi áp dụng"><Icon name="pencil" className="h-3.5 w-3.5" />Sửa lại</Btn>
                  </div>
                )}
              </div>
            ))}
            {editable && !claim.resolved && (
              ignoring ? (
                <div className="rounded-xl border border-slate-300 bg-white p-3.5">
                  <p className="font-semibold text-slate-800">Bỏ qua tuyên bố này vì…</p>
                  <div className="mt-2 flex flex-wrap gap-1.5">{IGNORE_REASONS.map((r) => <button key={r} type="button" onClick={() => setReason(r)} className={`rounded-full px-2.5 py-1 text-xs transition hover:bg-emerald-100 ${reason === r ? 'bg-emerald-100 font-semibold text-emerald-900 ring-1 ring-emerald-300' : 'bg-slate-100 text-slate-600'}`}>{r}</button>)}</div>
                  <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Lý do (bắt buộc)" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-1.5 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100" />
                  <div className="mt-2 flex gap-2">
                    <Btn tone="primary" disabled={!reason.trim()} onClick={() => { onIgnore(claim.id, reason.trim()); setIgnoring(false) }} title="Ghi lý do vào nhật ký và đánh dấu đã xử lý">Xác nhận bỏ qua</Btn>
                    <Btn tone="ghost" onClick={() => setIgnoring(false)}>Hủy</Btn>
                  </div>
                </div>
              ) : (
                <button type="button" onClick={() => setIgnoring(true)} title="Đánh dấu đã xử lý mà không sửa văn bản; phải ghi lý do"
                  className="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-[13px] font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900">
                  Bỏ qua kèm lý do…<Icon name="chevronDown" className="h-4 w-4 text-slate-400" />
                </button>
              )
            )}
          </>
        )}
        {tab === 'evidence' && (claim.evidence.length === 0 ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-center text-slate-500">Không có bằng chứng nào được truy xuất.</p> : (
          <>
            <p className="px-1 text-xs text-slate-500">
              {claim.evidence.length} đoạn · {claim.evidence.filter((e) => e.relation === 'SUPPORTS').length} ủng hộ · {claim.evidence.filter((e) => e.relation === 'CONTRADICTS').length} mâu thuẫn
            </p>
            {claim.evidence.map((e, i) => {
              const rel = RELATION[e.relation] || [e.relation || '—', 'bg-slate-100 text-slate-600 ring-slate-200']
              return (
                <div key={i} className="rounded-xl border border-slate-200 bg-white p-3.5 transition hover:border-emerald-300">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ring-1 ${rel[1]}`}>{rel[0]}</span>
                    <span className="min-w-0 truncate text-xs font-medium text-slate-700">{e.source_name} · tr. {e.page ?? '—'}</span>
                  </div>
                  {e.relation_reason && <p className="mt-2 text-xs font-medium text-slate-600">{e.relation_reason}</p>}
                  <p className="mt-1.5 line-clamp-4 leading-relaxed text-slate-800">{e.text}</p>
                  <div className="mt-2.5 flex items-center justify-between gap-2">
                    <span className="text-[11px] text-slate-400">
                      <span className={e.independent ? 'text-emerald-700' : 'text-amber-700'}>{e.independent ? 'nguồn độc lập' : 'cùng doanh nghiệp'}</span>
                      {e.lexical_score != null && ` · từ khóa ${pct(e.lexical_score)} · ngữ nghĩa ${pct(e.semantic_score)}`}
                    </span>
                    {e.page && e.doc_id && <Btn size="xs" onClick={() => onOpenEvidence(i)} title="Xem trang gốc của bằng chứng, đoạn trích được tô (chỉ đọc)">Mở nguồn <Icon name="arrowRight" className="h-3 w-3" /></Btn>}
                  </div>
                </div>
              )
            })}
          </>
        ))}
        {tab === 'attrs' && (
          <div className="rounded-xl border border-slate-200 bg-white p-3.5">
            <p className="text-xs font-semibold text-slate-500">Thuộc tính bắt buộc</p>
            <ul className="mt-2 divide-y divide-slate-100">
              {['chỉ số', 'số liệu', 'kỳ', 'năm gốc', 'phạm vi'].map((a) => {
                const miss = claim.missing.includes(a)
                return (
                  <li key={a} className="flex items-center justify-between py-2">
                    <span className="flex items-center gap-2 capitalize text-slate-800"><span className={`h-2 w-2 rounded-full ${miss ? 'bg-red-500' : 'bg-emerald-500'}`} />{a}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${miss ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'}`}>{miss ? 'Thiếu' : 'Có'}</span>
                  </li>
                )
              })}
            </ul>
            {claim.vague_terms.length > 0 && <p className="mt-2 rounded-lg bg-amber-50 p-2 text-xs text-amber-900">Cụm mơ hồ: {claim.vague_terms.join(', ')}</p>}
            <dl className="mt-3 grid grid-cols-2 gap-y-1 text-xs">
              <dt className="text-slate-500">Loại tuyên bố</dt><dd className="text-right text-slate-800">{labelOf('claim_type', claim.claim_type)}</dd>
              <dt className="text-slate-500">Độ tin cậy trích</dt><dd className="text-right font-mono text-slate-800">{claim.confidence ?? '—'}</dd>
            </dl>
            {claim.rationale && <p className="mt-3 border-t border-slate-100 pt-3 text-xs leading-relaxed text-slate-600">{claim.rationale}</p>}
          </div>
        )}
        {tab === 'legal' && (!claim.legal ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-center text-slate-500">Không có kết quả pháp lý.</p> : (
          <div className="space-y-2.5">
            <div className="rounded-xl border border-slate-200 bg-white p-3.5">
              <p className="text-slate-800"><b className="font-semibold">Kết luận:</b> {labelOf('legal_finding', claim.legal.finding)} · rủi ro {labelOf('severity', String(claim.legal.risk || '').toUpperCase())}</p>
              <p className="mt-1 text-xs text-slate-500">Bộ quy tắc <code className="rounded bg-slate-100 px-1 font-mono">{claim.legal.rule_pack}</code></p>
            </div>
            {claim.legal.rules_applied.length === 0 && <p className="rounded-xl border border-sky-200 bg-sky-50 p-3 text-xs leading-relaxed text-sky-900">Chưa có quy tắc pháp lý nào áp dụng cho loại tuyên bố này; căn cứ dưới đây chỉ là văn bản cùng chủ đề — khoảng trống dữ liệu, không phải nhận định về doanh nghiệp.</p>}
            {claim.legal.sources.map((s, i) => (
              <div key={i} className="rounded-xl border border-slate-200 bg-white p-3">
                <a href={s.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-mono text-[13px] font-semibold text-slate-900 hover:text-emerald-800 hover:underline">{s.document}<Icon name="external" className="h-3 w-3" /></a>
                <p className="mt-0.5 text-slate-600">{s.title}</p>
                <p className={`mt-1 text-[11px] font-medium ${s.verified ? 'text-emerald-700' : 'text-amber-700'}`}>{s.verification_label} · hiệu lực {s.effective_from || '—'}</p>
              </div>
            ))}
            {claim.legal.notes && <p className="px-1 text-[11px] text-slate-500">{claim.legal.notes}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}

function ReworkBox({ initial, onSave, onCancel }) {
  const [text, setText] = useState(initial)
  return (
    <div className="mt-3">
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} className="w-full rounded-lg border border-emerald-400 p-2.5 text-[13px] focus:outline-none focus:ring-2 focus:ring-emerald-100" />
      <div className="mt-2 flex gap-2">
        <Btn tone="primary" onClick={() => onSave(text)} title="Thay câu trong văn bản bằng nội dung đã sửa; ghi là người sửa">Áp dụng</Btn>
        <Btn tone="ghost" onClick={onCancel}>Hủy</Btn>
      </div>
    </div>
  )
}

/** The original page of one evidence passage, with the quoted block highlighted by the server. */
function EvidenceModal({ items, index, setIndex, onClose, documents }) {
  const e = items[index]
  const [img, setImg] = useState({ url: null, rects: null, error: null })
  useEffect(() => {
    const onKey = (ev) => {
      if (ev.key === 'Escape') { ev.preventDefault(); ev.stopPropagation(); onClose() }
      if (ev.key === 'ArrowLeft' && index > 0) setIndex(index - 1)
      if (ev.key === 'ArrowRight' && index < items.length - 1) setIndex(index + 1)
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [index, items.length, onClose, setIndex])
  useEffect(() => {
    let alive = true
    let url = null
    setImg({ url: null, rects: null, error: null })
    fetch(pageUrl(e.doc_id, e.page, e.text, 2)).then(async (r) => {
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText)
      const rects = r.headers.get('X-Highlight-Rects')
      url = URL.createObjectURL(await r.blob())
      if (alive) setImg({ url, rects: rects == null ? null : Number(rects), error: null })
    }).catch((err) => alive && setImg({ url: null, rects: null, error: err.message }))
    return () => { alive = false; if (url) URL.revokeObjectURL(url) }
  }, [e.doc_id, e.page, e.text])
  const rel = RELATION[e.relation] || [e.relation || '—', 'bg-slate-100 text-slate-600 ring-slate-200']
  const doc = documents.find((d) => d.doc_id === e.doc_id)
  const block = /block (\d+)/.exec(e.citation || '')?.[1]
  const rows = [
    ['Tài liệu', e.source_name],
    ['Trang', e.page],
    ['Vị trí', block ? `khối văn bản ${block}${e.is_table ? ' · bảng' : ''}` : '—'],
    ['Loại nguồn', `${SOURCE_TYPE[e.source_type] || e.source_type || '—'}${e.independent ? ' · độc lập' : ''}`],
    ['Quan hệ', rel[0]],
    ['Điểm truy xuất', e.score != null ? e.score.toFixed(2) : '—'],
    ['Từ khóa / ngữ nghĩa', e.lexical_score != null ? `${pct(e.lexical_score)} / ${pct(e.semantic_score)}` : '—'],
    ['sha256', doc?.sha256 ? `${doc.sha256.slice(0, 4)}…${doc.sha256.slice(-4)}` : '—'],
  ]
  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center bg-slate-900/45 p-6 backdrop-blur-[2px]" onClick={onClose}>
      <div className="flex h-full max-h-[880px] w-full max-w-[1340px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl" onClick={(ev) => ev.stopPropagation()} role="dialog" aria-modal="true">
        <div className="flex items-center gap-3 border-b border-slate-200 px-5 py-3">
          <span className={`rounded-full px-3 py-1 text-xs font-bold ring-1 ${rel[1]}`}>{rel[0]}</span>
          <span className="truncate text-[15px] font-semibold text-slate-900">{e.source_name}</span>
          <span className="text-sm text-slate-500">trang {e.page}</span>
          {items.length > 1 && <span className="text-xs text-slate-400">· đoạn {index + 1}/{items.length}</span>}
          <div className="ml-auto flex items-center gap-2">
            <Btn onClick={() => setIndex(index - 1)} disabled={index === 0} title="Bằng chứng trước (←)"><Icon name="arrowLeft" className="h-4 w-4" /></Btn>
            <Btn onClick={() => setIndex(index + 1)} disabled={index >= items.length - 1} title="Bằng chứng sau (→)"><Icon name="arrowRight" className="h-4 w-4" /></Btn>
            <a href={`${API}/v1/documents/${e.doc_id}#page=${e.page}`} target="_blank" rel="noreferrer" title="Mở tệp PDF gốc ở trang này"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-emerald-600 hover:bg-emerald-50">
              Mở PDF gốc<Icon name="external" className="h-3.5 w-3.5" />
            </a>
            <Btn tone="primary" onClick={onClose} title="Đóng (Esc)">Đóng</Btn>
          </div>
        </div>
        <div className="flex min-h-0 flex-1">
          <div className="gs-scroll min-w-0 flex-1 overflow-auto bg-slate-100 p-5">
            {img.url && <img src={img.url} alt={`Trang ${e.page} của ${e.source_name}`} className="mx-auto w-full max-w-[860px] rounded-md bg-white shadow-lg ring-1 ring-slate-200" />}
            {!img.url && !img.error && <div className="mx-auto flex aspect-[1/1.35] w-full max-w-[860px] animate-pulse items-center justify-center rounded-md bg-white text-sm text-slate-400 shadow">Đang dựng trang {e.page}…</div>}
            {img.error && <div className="mx-auto max-w-md rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">Không dựng được ảnh trang: {img.error}. Dùng “Mở PDF gốc” để đối chiếu.</div>}
          </div>
          <aside className="gs-scroll w-[380px] shrink-0 overflow-y-auto border-l border-slate-200 p-5">
            <p className="text-[15px] font-semibold text-slate-900">Thông tin bằng chứng</p>
            <dl className="mt-3 space-y-2.5 text-[13px]">
              {rows.map(([k, v]) => (
                <div key={k} className="flex items-baseline justify-between gap-4">
                  <dt className="shrink-0 text-slate-500">{k}</dt>
                  <dd className={`min-w-0 truncate text-right text-slate-800 ${['Điểm truy xuất', 'Từ khóa / ngữ nghĩa', 'sha256'].includes(k) ? 'font-mono text-xs' : ''}`} title={k === 'sha256' ? doc?.sha256 : String(v)}>{v}</dd>
                </div>
              ))}
            </dl>
            {e.relation_reason && <p className="mt-4 rounded-xl bg-slate-50 p-3.5 text-[13px] leading-relaxed text-slate-700 ring-1 ring-slate-200">{e.relation_reason}</p>}
            <p className="mt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-slate-500">Đoạn trích</p>
            <blockquote className="mt-2 border-l-[3px] border-amber-400 bg-amber-50/70 py-2.5 pl-3.5 pr-3 text-[13px] leading-relaxed text-slate-800">“{e.text}”</blockquote>
          </aside>
        </div>
        <p className="border-t border-slate-200 bg-slate-50 px-5 py-2.5 text-xs text-slate-500">
          {img.rects === 0
            ? 'Không định vị được đoạn trích trên ảnh trang (có thể là trang quét hoặc đoạn trải qua nhiều khối bố cục) — đối chiếu bằng PDF gốc.'
            : 'Phần được tô vàng là đoạn hệ thống trích dẫn. Nếu không thấy vùng tô, đoạn trích có thể trải qua nhiều khối bố cục hoặc trang là bản quét — mở PDF gốc để đối chiếu.'}
        </p>
      </div>
    </div>
  )
}

export default function StudioPage({ runId, reviewer }) {
  const [info, setInfo] = useState(null)
  const [docId, setDocId] = useState(null)
  const [view, setView] = useState(null)
  const [claims, setClaimsUI] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [tab, setTab] = useState('fix')
  const [focused, setFocused] = useState(0)
  const [filter, setFilter] = useState({ q: '', sev: { error: true, warning: true, info: true }, resolved: false })
  const [bottom, setBottom] = useState('log')
  const [bottomOpen, setBottomOpen] = useState(true)
  const [saveState, setSaveState] = useState('saved')
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [tour, setTour] = useState(-1)
  const [help, setHelp] = useState(false)
  const [zoom, setZoomPct] = useState(100)
  const [pageNow, setPageNow] = useState(null)
  const [pageInput, setPageInput] = useState('')
  const [pageCount, setPageCount] = useState(null)
  const [query, setQuery] = useState('')
  const [focusMode, setFocusMode] = useState(false)
  const [evidenceAt, setEvidenceAt] = useState(null)
  const host = useRef(null)
  const editor = useRef(null)
  const pending = useRef([])
  const touched = useRef(new Set())
  const userEdits = useRef(false)
  const timer = useRef(null)
  const latest = useRef({})

  const say = (t) => { setToast(t); setTimeout(() => setToast(null), 3500) }

  useEffect(() => {
    studioRun(runId).then((r) => {
      setInfo(r)
      const first = r.documents.find((d) => d.role === 'under_review' && d.available) || r.documents.find((d) => d.available)
      setDocId(first?.doc_id || null)
    }).catch((e) => setError(e.message))
    try { if (!localStorage.getItem('gs.studio.tour')) setTour(0) } catch { /* no storage */ }
  }, [runId])

  const toClaims = (v) => v.diagnostics.map((d) => ({ ...d, id: d.claim_id }))

  const handlers = useMemo(() => ({
    quickFix: (id) => { setSelectedId(id); setTab('fix'); setFocused(0) },
    showEvidence: (id) => { setSelectedId(id); setTab('evidence') },
    ignore: (id) => { setSelectedId(id); setTab('fix'); say('Chọn lý do bỏ qua ở khung bên phải.') },
    accept: () => { latest.current.acceptFocused?.(); return true },
    reject: () => latest.current.rejectFocused?.() || false,
    save: () => latest.current.saveVersion?.(),
    select: (id) => { if (id) setSelectedId(id) },
    change: ({ user, touched: ids }) => {
      if (user) { userEdits.current = true; ids.forEach((id) => touched.current.add(id)) }
      latest.current.schedule?.()
    },
  }), [])

  // (Re)build the editor when the document changes.
  useEffect(() => {
    if (!docId || !host.current) return undefined
    let cancelled = false
    setView(null); setClaimsUI([]); setSelectedId(null); setPageCount(null)
    studioDoc(runId, docId).then((v) => {
      if (cancelled) return
      editor.current?.destroy()
      editor.current = createEditor(host.current, {
        doc: v.text, pages: v.paragraphs.map((p) => p.page), readOnly: !v.editable, handlers,
        fontSize: Math.round(BASE_FONT * latest.current.zoom / 100),
      })
      const list = toClaims(v)
      loadClaims(editor.current, list, handlers)
      setView(v); setClaimsUI(list); setSaveState('saved')
    }).catch((e) => setError(e.message))
    fetch(`${API}/v1/documents/${docId}/meta`).then((r) => (r.ok ? r.json() : null)).then((m) => { if (!cancelled && m?.page_count) setPageCount(m.page_count) }).catch(() => {})
    return () => { cancelled = true }
  }, [runId, docId, handlers])

  useEffect(() => () => editor.current?.destroy(), [])

  // Page of the original at the top of the viewport, for the toolbar.
  const pages = useMemo(() => view?.paragraphs.map((p) => p.page) || [], [view])
  useEffect(() => {
    const ed = editor.current
    if (!ed || !pages.length) return undefined
    const onScroll = () => setPageNow(pageAtTop(ed, pages))
    onScroll()
    ed.scrollDOM.addEventListener('scroll', onScroll, { passive: true })
    return () => ed.scrollDOM.removeEventListener('scroll', onScroll)
  }, [pages])
  const totalPages = pageCount || pages.reduce((m, p) => Math.max(m, p || 0), 0) || null

  useEffect(() => { if (editor.current) setZoom(editor.current, Math.round(BASE_FONT * zoom / 100)) }, [zoom])

  const applyServer = useCallback((v, sentText) => {
    setView(v)
    const list = toClaims(v)
    setClaimsUI(list)
    const ed = editor.current
    if (ed && ed.state.doc.toString() === sentText) loadClaims(ed, list, handlers)
  }, [handlers])

  const save = useCallback(async ({ snapshot = false, note = '', docClass } = {}) => {
    const ed = editor.current
    if (!ed || !view?.editable) return
    clearTimeout(timer.current)
    const text = ed.state.doc.toString()
    const fieldClaims = ed.state.field(claimsField)
    const entries = pending.current.splice(0)
    for (const id of touched.current) {
      const c = fieldClaims.find((x) => x.id === id)
      if (c) entries.push({ actor: 'user', action: 'edit', claim_id: id, before: c.text, after: ed.state.doc.sliceString(c.from, c.to), user: reviewer })
    }
    if (userEdits.current && touched.current.size === 0) entries.push({ actor: 'user', action: 'edit', reason: 'Sửa tay ngoài các tuyên bố', user: reviewer })
    touched.current = new Set(); userEdits.current = false
    setSaveState('saving')
    try {
      const v = await studioSave(runId, docId, { text, log: entries, snapshot, note, doc_class: docClass })
      applyServer(v, text)
      setSaveState('saved')
      if (snapshot) say(`Đã lưu phiên bản ${v.versions.length}.`)
    } catch (e) {
      pending.current.unshift(...entries)
      setSaveState('error'); setError(e.message)
    }
  }, [view, runId, docId, reviewer, applyServer])

  const schedule = useCallback(() => {
    setSaveState('dirty')
    clearTimeout(timer.current)
    timer.current = setTimeout(() => latest.current.save?.(), 1500)
  }, [])

  const markLocal = (claimId, ruleCode, resolve) => {
    const ed = editor.current
    const next = ed.state.field(claimsField).map((c) => {
      if (c.id !== claimId) return c
      const suggestions = c.suggestions.filter((s) => s.rule_code !== ruleCode)
      return { ...c, suggestions, resolved: resolve === undefined ? suggestions.length === 0 : resolve }
    })
    ed.dispatch({ effects: setClaims.of(next) })
    ed.dispatch(lintFromClaims(ed.state, handlers))
    setClaimsUI((prev) => prev.map((c) => {
      const n = next.find((x) => x.id === c.id)
      return n ? { ...c, suggestions: n.suggestions, resolved: n.resolved } : c
    }))
  }

  const accept = (claimId, s, customText) => {
    const ed = editor.current
    const claim = ed?.state.field(claimsField).find((c) => c.id === claimId)
    if (!claim) return
    const change = customText != null ? { from: claim.from, to: claim.to, insert: customText } : suggestionChange(ed.state, claim, s)
    if (!change) { say('Đề xuất đã cũ: câu đã thay đổi. Lưu lại để nhận đề xuất mới.'); return }
    ed.dispatch({ changes: change, userEvent: 'studio.accept' })
    pending.current.push({
      actor: customText != null ? 'user' : (s.source === 'llm' ? 'ai-llm' : 'ai-rule'),
      action: customText != null ? 'rework' : 'accept', claim_id: claimId, suggestion_id: s.suggestion_id,
      rule_code: s.rule_code, kind: s.kind, before: s.before, after: customText ?? s.after, reason: s.reason, user: reviewer, source: s.source,
    })
    markLocal(claimId, s.rule_code, customText != null ? true : undefined)
    setFocused(0)
    schedule()
  }

  const reject = (claimId, s) => {
    pending.current.push({ actor: 'user', action: 'reject', claim_id: claimId, suggestion_id: s.suggestion_id, rule_code: s.rule_code, kind: s.kind, reason: s.reason, user: reviewer })
    markLocal(claimId, s.rule_code)
    setFocused(0)
    schedule()
  }

  const ignore = (claimId, reason) => {
    pending.current.push({ actor: 'user', action: 'ignore', claim_id: claimId, reason, user: reviewer })
    markLocal(claimId, null, true)
    schedule()
  }

  const acceptAllOfKind = (kind) => {
    const ed = editor.current
    const targets = ed.state.field(claimsField).filter((c) => !c.resolved && c.suggestions.some((s) => s.kind === kind))
    if (!targets.length) return
    const label = info?.kinds?.[kind] || kind
    if (!window.confirm(`Chấp nhận ${targets.length} đề xuất loại “${label}”?\nCó thể hoàn tác bằng Ctrl+Z hoặc khôi phục một phiên bản đã lưu.`)) return
    const changes = []
    let lastEnd = -1
    for (const c of [...targets].sort((a, b) => a.from - b.from)) {
      const s = c.suggestions.find((x) => x.kind === kind)
      const ch = suggestionChange(ed.state, c, s)
      if (!ch || ch.from < lastEnd) continue
      lastEnd = ch.to
      changes.push(ch)
      pending.current.push({ actor: 'ai-rule', action: 'accept', claim_id: c.id, suggestion_id: s.suggestion_id, rule_code: s.rule_code, kind, before: s.before, after: s.after, reason: `${s.reason} (chấp nhận hàng loạt)`, user: reviewer })
    }
    ed.dispatch({ changes, userEvent: 'studio.accept' })
    const next = ed.state.field(claimsField).map((c) => {
      if (!targets.some((t) => t.id === c.id)) return c
      const suggestions = c.suggestions.filter((s) => s.kind !== kind)
      return { ...c, suggestions, resolved: suggestions.length === 0 }
    })
    ed.dispatch({ effects: setClaims.of(next) })
    ed.dispatch(lintFromClaims(ed.state, handlers))
    say(`Đã chấp nhận ${changes.length} đề xuất.`)
    save()
  }

  const selected = claims.find((c) => c.id === selectedId) || null
  const selectedLive = editor.current?.state.field(claimsField).find((c) => c.id === selectedId) || null
  const current = selectedLive ? { ...selected, ...selectedLive } : selected

  // The Problems list order, shared by the panel numbering and the Inspector's ‹ › buttons.
  const visible = useMemo(() => {
    const q = filter.q.toLowerCase()
    return ['error', 'warning', 'info'].flatMap((sev) => claims.filter((c) => c.severity === sev && (filter.resolved || !c.resolved) && filter.sev[sev] && (!q || c.text.toLowerCase().includes(q))))
  }, [claims, filter])

  latest.current = {
    zoom,
    save: () => save(),
    schedule,
    saveVersion: () => { const note = window.prompt('Ghi chú cho phiên bản này (không bắt buộc):', '') ; if (note !== null) save({ snapshot: true, note }) },
    acceptFocused: () => { const s = current?.suggestions?.[focused]; if (s && view?.editable) accept(current.id, s) },
    rejectFocused: () => { const s = current?.suggestions?.[focused]; if (s && view?.editable && tab === 'fix') { reject(current.id, s); return true } return false },
  }

  const pick = (id) => {
    const c = editor.current?.state.field(claimsField).find((x) => x.id === id)
    if (c) reveal(editor.current, c)
    setSelectedId(id)
  }
  const hover = (id) => {
    const c = id ? editor.current?.state.field(claimsField).find((x) => x.id === id) : null
    if (editor.current) flash(editor.current, c)
  }
  const at = visible.findIndex((c) => c.id === selectedId)
  const nav = {
    index: at + 1, total: visible.length, hasPrev: at > 0, hasNext: at >= 0 && at < visible.length - 1,
    prev: () => at > 0 && pick(visible[at - 1].id),
    next: () => at < visible.length - 1 && pick(visible[at + 1].id),
    first: () => visible[0] && pick(visible[0].id),
    close: () => setSelectedId(null),
  }

  const jumpPage = (n) => {
    if (!editor.current || !pages.length || !Number.isFinite(n)) return
    const target = Math.max(1, totalPages ? Math.min(n, totalPages) : n)
    gotoPage(editor.current, pages, target)
    setPageNow(target)
    setPageInput('')
  }
  const find = (backwards) => {
    if (!editor.current) return
    if (!searchText(editor.current, query, backwards) && query) say(`Không tìm thấy “${query}”.`)
  }

  const restore = async (version) => {
    if (!window.confirm(version ? `Khôi phục phiên bản ${version}? Văn bản hiện tại sẽ được thay.` : 'Khôi phục văn bản gốc? Mọi sửa đổi chưa lưu thành phiên bản sẽ mất khỏi văn bản (nhật ký vẫn giữ).')) return
    try {
      const v = await studioRestore(runId, docId, version)
      const ed = editor.current
      ed.dispatch({ changes: { from: 0, to: ed.state.doc.length, insert: v.text }, userEvent: 'studio.restore' })
      applyServer(v, v.text)
      say(version ? `Đã khôi phục phiên bản ${version}.` : 'Đã khôi phục văn bản gốc.')
    } catch (e) { setError(e.message) }
  }

  const kindCounts = useMemo(() => {
    const out = {}
    for (const c of claims) if (!c.resolved) for (const s of c.suggestions) out[s.kind] = (out[s.kind] || 0) + 1
    return out
  }, [claims])

  const endTour = () => { setTour(-1); try { localStorage.setItem('gs.studio.tour', '1') } catch { /* ignore */ } }
  const tourOn = (key) => (tour >= 0 && TOUR[tour][0] === key ? 'gs-tour-target' : '')
  const doc = view?.doc
  const log = view?.log || []
  const topBtn = 'inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-emerald-50 transition hover:bg-white/10'

  return (
    <div className="flex h-screen flex-col bg-[var(--color-canvas)] text-slate-900">
      {/* top bar */}
      <header className="flex h-[52px] shrink-0 items-center gap-3 bg-[#0F3D2E] px-3 text-white shadow-[0_1px_0_rgba(0,0,0,.15)]">
        <Link to={`/runs/${runId}`} className={topBtn} title="Về hàng đợi soát của phiên này"><Icon name="arrowLeft" className="h-4 w-4" />Hàng đợi</Link>
        <span className="h-6 w-px bg-white/15" />
        <span className="flex items-center gap-2"><Leaf className="h-6 w-6 text-emerald-300" /><span className="text-[17px] font-bold tracking-tight">GreenScan · Sửa báo cáo</span></span>
        <span className="min-w-0 truncate text-[13px] text-emerald-50/85" title={info?.label}>{info?.label || runId}</span>
        {doc && (
          <span className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${view.editable ? 'bg-emerald-400/20 text-emerald-200 ring-1 ring-emerald-300/40' : 'bg-white/10 text-white ring-1 ring-white/20'}`}
            title={view.editable ? 'Tài liệu đang được rà soát: sửa được' : 'Tài liệu bằng chứng: chỉ đọc, không bao giờ sửa'}>
            {view.editable ? <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" /> : <Icon name="lock" className="h-3 w-3" />}
            {view.editable ? 'Đang rà soát' : 'Bằng chứng · chỉ đọc'}
          </span>
        )}
        <div className="ml-auto flex shrink-0 items-center gap-1.5">
          {view?.editable && (
            <label className="flex items-center gap-2 text-xs text-emerald-50/80" title={'Lớp bảo mật quyết định có được gửi ca khó tới mô hình ngôn ngữ trên mạng hay không.\nA công khai: được (khi τ đã hiệu chỉnh và chế độ có mạng bật). B, C: không, chuyển người soát xét.'}>
              Lớp
              <select value={view.doc_class} onChange={(e) => save({ docClass: e.target.value })}
                className="rounded-lg border border-white/15 bg-white/10 px-2 py-1.5 text-xs font-semibold text-white hover:bg-white/15 focus:outline-none">
                {Object.entries(info?.doc_classes || {}).map(([k, l]) => <option key={k} value={k} className="text-slate-900">{k} · {l}</option>)}
              </select>
            </label>
          )}
          {view && (
            <span title={view.tau == null ? 'Ngưỡng τ chưa hiệu chỉnh: không ca nào được gửi tới mô hình ngôn ngữ.' : `τ = ${view.tau}`}
              className="rounded-lg border border-white/15 bg-white/10 px-2.5 py-1.5 text-xs font-semibold">
              Mô hình ngôn ngữ: {view.tau == null ? 'tắt' : view.cloud ? 'dùng khi ca khó' : 'ngoại tuyến'}
            </span>
          )}
          <span className={`inline-flex items-center gap-1 px-1.5 text-xs font-medium ${saveState === 'error' ? 'text-red-300' : saveState === 'saved' ? 'text-emerald-200' : 'text-amber-200'}`} title="Văn bản tự lưu sau 1,5 giây không gõ">
            {saveState === 'saved' && <Icon name="check" className="h-3.5 w-3.5" strokeWidth={2.5} />}
            {{ saved: 'Đã lưu', dirty: '● Chưa lưu', saving: 'Đang lưu…', error: '! Lỗi lưu' }[saveState]}
          </span>
          {view?.editable && (
            <button type="button" onClick={() => latest.current.saveVersion()} title="Lưu một phiên bản có tên để khôi phục sau (Ctrl+S)"
              className="rounded-lg border border-white/30 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-white/10">Lưu phiên bản</button>
          )}
          <button type="button" className={topBtn} onClick={() => setHelp(true)} title="Phím tắt"><Icon name="keyboard" className="h-4 w-4" />Phím tắt</button>
          <button type="button" className={topBtn} onClick={() => setTour(0)} title="Xem lại hướng dẫn"><Icon name="help" className="h-4 w-4" />Hướng dẫn</button>
          <span className="ml-1 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-300 text-xs font-bold text-[#0F3D2E] ring-2 ring-white/20" title={reviewer || 'Chưa có người soát xét'}>{initials(reviewer)}</span>
        </div>
      </header>

      {error && <div className="flex items-center justify-between border-b border-red-200 bg-red-50 px-4 py-2 text-xs text-red-800"><span className="flex items-center gap-2"><Icon name="alertCircle" className="h-4 w-4" /><b>Lỗi:</b> {error}</span><button type="button" onClick={() => setError(null)} aria-label="Đóng thông báo lỗi"><Icon name="x" className="h-4 w-4" /></button></div>}

      <div className="flex min-h-0 flex-1 gap-3 p-3">
        {/* explorer */}
        {!focusMode && (
          <aside data-tour="explorer" className={`flex w-[330px] shrink-0 flex-col gap-3 ${tourOn('explorer')}`}>
            <Card className="pb-2">
              <SectionTitle className="px-4 pb-2 pt-3.5">Tài liệu ({info?.documents?.length || 0})</SectionTitle>
              <ul className="space-y-0.5 px-2">
                {(info?.documents || []).map((d) => {
                  const on = docId === d.doc_id
                  return (
                    <li key={d.name}>
                      <button type="button" disabled={!d.available} onClick={() => setDocId(d.doc_id)}
                        title={!d.available ? 'Tệp không còn trên máy' : d.role === 'under_review' ? 'Đang rà soát: sửa được' : 'Bằng chứng: chỉ đọc'}
                        className={`flex w-full items-center gap-2.5 rounded-lg border-l-[3px] px-2 py-2 text-left transition disabled:opacity-40 ${on ? 'border-emerald-600 bg-emerald-50' : 'border-transparent hover:bg-slate-50'}`}>
                        <DocIcon kind={d.kind} locked={d.role !== 'under_review'} />
                        <span className="min-w-0 flex-1">
                          <span className={`block truncate text-[13px] ${on ? 'font-semibold text-emerald-950' : 'font-medium text-slate-800'}`}>{d.name}</span>
                          <span className="block text-[11px] text-slate-500">{d.role === 'under_review' ? `Đang rà soát${d.claims ? ` · ${d.claims} tuyên bố` : ''}` : 'Bằng chứng · chỉ đọc'}</span>
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            </Card>
            <Card className="flex min-h-0 flex-1 flex-col overflow-hidden">
              <SectionTitle className="px-4 pb-2.5 pt-3.5" right={view?.editable && Object.keys(kindCounts).length > 0 && (
                <select value="" onChange={(e) => e.target.value && acceptAllOfKind(e.target.value)} title="Chấp nhận mọi đề xuất cùng loại (có bước xác nhận)"
                  className="max-w-[10.5rem] rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-700 hover:border-emerald-500 focus:outline-none">
                  <option value="">Chấp nhận hàng loạt…</option>
                  {Object.entries(kindCounts).map(([k, n]) => <option key={k} value={k}>{info?.kinds?.[k] || k} ({n})</option>)}
                </select>
              )}>Vấn đề phát hiện</SectionTitle>
              <Problems claims={claims} visible={visible} unanchored={view?.unanchored || []} filter={filter} setFilter={setFilter} selectedId={selectedId} onPick={pick} onHover={hover} />
            </Card>
          </aside>
        )}

        {/* toolbar + editor + bottom */}
        <Card className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <div className="flex h-12 shrink-0 items-center gap-1 border-b border-slate-200 px-2">
            <IconBtn icon="chevronUp" title="Trang trước" onClick={() => jumpPage((pageNow || 1) - 1)} disabled={!pages.length || (pageNow || 1) <= 1} />
            <IconBtn icon="chevronDown" title="Trang sau" onClick={() => jumpPage((pageNow || 0) + 1)} disabled={!pages.length || (totalPages && pageNow >= totalPages)} />
            <label className="ml-1 flex items-center gap-1.5 text-xs text-slate-500" title="Gõ số trang của bản gốc rồi Enter">
              <span className="sr-only">Trang</span>
              <input value={pageInput} placeholder={pageNow ?? '—'} inputMode="numeric"
                onChange={(e) => setPageInput(e.target.value.replace(/\D/g, ''))}
                onKeyDown={(e) => { if (e.key === 'Enter') jumpPage(Number(pageInput)) }}
                className="h-8 w-12 rounded-lg border border-slate-200 text-center text-[13px] font-semibold text-slate-800 placeholder:text-slate-800 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100" />
              <span className="tabular-nums">/ {totalPages ?? '—'}</span>
            </label>
            <span className="mx-2 h-5 w-px bg-slate-200" />
            <IconBtn icon="minus" title="Thu nhỏ chữ" onClick={() => setZoomPct(ZOOMS[Math.max(0, ZOOMS.indexOf(zoom) - 1)])} disabled={zoom === ZOOMS[0]} />
            <button type="button" onClick={() => setZoomPct(100)} title="Về 100%" className="h-8 w-14 rounded-lg border border-slate-200 text-[13px] font-semibold tabular-nums text-slate-800 hover:border-emerald-500">{zoom}%</button>
            <IconBtn icon="plus" title="Phóng to chữ" onClick={() => setZoomPct(ZOOMS[Math.min(ZOOMS.length - 1, ZOOMS.indexOf(zoom) + 1)])} disabled={zoom === ZOOMS[ZOOMS.length - 1]} />
            <span className="mx-2 h-5 w-px bg-slate-200" />
            <IconBtn icon="expand" title={focusMode ? 'Hiện lại hai khung bên' : 'Chế độ tập trung: ẩn hai khung bên'} onClick={() => setFocusMode(!focusMode)} active={focusMode} />
            <div className="ml-auto flex items-center gap-1">
              <label className="relative">
                <Icon name="search" className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Tìm trong tài liệu…"
                  onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); find(e.shiftKey) } if (e.key === 'Escape') { setQuery(''); if (editor.current) searchText(editor.current, '') } }}
                  title="Enter: kết quả tiếp theo · Shift+Enter: kết quả trước"
                  className="h-8 w-56 rounded-lg border border-slate-200 bg-slate-50/60 pl-8 pr-2 text-[13px] placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" />
              </label>
              <IconBtn icon="download" title="Xuất báo cáo" onClick={() => { setBottom('export'); setBottomOpen(true) }} />
            </div>
          </div>
          {view && !view.editable && <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-4 py-1.5 text-xs text-slate-600"><Icon name="lock" className="h-3.5 w-3.5" />Tài liệu bằng chứng (BCTC, văn bản luật, dữ liệu bên thứ ba): chỉ đọc. Mọi sửa đổi chỉ áp dụng cho báo cáo đang rà soát.</div>}
          <div data-tour="editor" ref={host} className={`relative min-h-0 flex-1 overflow-hidden ${tourOn('editor')}`}>
            {!view && <p className="absolute inset-0 flex items-center justify-center text-sm text-slate-400">Đang mở tài liệu…</p>}
          </div>
          <section data-tour="bottom" className={`shrink-0 border-t border-slate-200 bg-white ${bottomOpen ? 'h-60' : 'h-11'} ${tourOn('bottom')}`}>
            <div className="flex h-11 items-center gap-1 border-b border-slate-100 px-3">
              {[['log', `Nhật ký thay đổi (${log.length + pending.current.length})`], ['versions', `Phiên bản (${view?.versions?.length || 0})`], ['export', 'Xuất báo cáo']].map(([k, l]) => (
                <button key={k} type="button" onClick={() => { setBottom(k); setBottomOpen(true) }}
                  className={`-mb-px h-11 border-b-[2.5px] px-3 text-[13px] font-semibold transition ${bottom === k && bottomOpen ? 'border-emerald-600 text-emerald-900' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>{l}</button>
              ))}
              <IconBtn icon={bottomOpen ? 'chevronDown' : 'chevronUp'} title={bottomOpen ? 'Thu gọn' : 'Mở rộng'} onClick={() => setBottomOpen(!bottomOpen)} className="ml-auto" />
            </div>
            {bottomOpen && (
              <div className="gs-scroll h-[calc(100%-2.75rem)] overflow-y-auto px-4 py-3 text-[13px]">
                {bottom === 'log' && (log.length === 0 ? <p className="text-slate-500">Chưa có thao tác nào.</p> : (
                  <table className="w-full">
                    <tbody>
                      {[...log].reverse().map((e) => (
                        <tr key={e.seq} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                          <td className="w-10 py-2 text-xs text-slate-400">#{e.seq}</td>
                          <td className="w-40 text-xs tabular-nums text-slate-500">{e.ts?.replace('T', ' ').slice(0, 19)}</td>
                          <td className="w-48"><span className={`rounded-md px-2 py-0.5 text-[11px] font-semibold ${e.actor === 'user' ? 'bg-slate-100 text-slate-700' : 'bg-violet-50 text-violet-800 ring-1 ring-violet-100'}`}>{ACTOR[e.actor] || e.actor}{e.user ? ` · ${e.user}` : ''}</span></td>
                          <td className={`w-28 font-semibold ${ACTION_TONE[e.action] || 'text-slate-800'}`}>{ACTION[e.action] || e.action}</td>
                          <td className="w-20">{e.rule_code && <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10.5px] text-slate-600">{e.rule_code}</span>}</td>
                          <td className="max-w-0 truncate text-slate-600" title={[e.reason, e.after].filter(Boolean).join('\n')}>{e.reason || e.after}</td>
                          <td className="w-16 text-right">{e.claim_id && <button type="button" className="inline-flex items-center gap-0.5 text-xs font-semibold text-emerald-800 hover:underline" onClick={() => pick(e.claim_id)}>mở<Icon name="external" className="h-3 w-3" /></button>}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ))}
                {bottom === 'versions' && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 rounded-lg border border-slate-200 px-3 py-2"><span className="font-semibold">Văn bản gốc</span><span className="text-slate-500">như khi phân tích</span>{view?.editable && <Btn className="ml-auto" onClick={() => restore(0)} title="Đưa văn bản về bản gốc; nhật ký vẫn giữ"><Icon name="undo" className="h-3.5 w-3.5" />Khôi phục</Btn>}</div>
                    {(view?.versions || []).map((v) => (
                      <div key={v.version} className="flex items-center gap-3 rounded-lg border border-slate-200 px-3 py-2 hover:border-emerald-300">
                        <span className="font-semibold">Phiên bản {v.version}</span><span className="tabular-nums text-slate-500">{v.saved_at?.replace('T', ' ').slice(0, 19)}</span><span className="truncate text-slate-600">{v.note}</span>
                        {view?.editable && <Btn className="ml-auto" onClick={() => restore(v.version)} title="Thay văn bản hiện tại bằng phiên bản này"><Icon name="undo" className="h-3.5 w-3.5" />Khôi phục</Btn>}
                      </div>
                    ))}
                  </div>
                )}
                {bottom === 'export' && view && (
                  <>
                    <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-2.5">
                      {EXPORTS.map(([fmt, label, hint]) => (
                        <a key={fmt} href={studioExportUrl(runId, docId, fmt, reviewer)} target={fmt === 'review_html' ? '_blank' : undefined} rel="noreferrer"
                          onClick={() => latest.current.save?.()} title={hint}
                          className="group flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-3 transition hover:-translate-y-0.5 hover:border-emerald-500 hover:shadow-md">
                          <FormatBadge format={fmt} />
                          <span className="min-w-0">
                            <span className="block text-[13px] font-semibold text-slate-900 group-hover:text-emerald-900">{label}</span>
                            <span className="mt-0.5 block text-xs leading-snug text-slate-500">{hint}</span>
                          </span>
                        </a>
                      ))}
                    </div>
                    {view.layout_note && (
                      <p className="mt-3 flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
                        <Icon name="alertCircle" className="h-4 w-4 text-amber-600" />{view.layout_note}
                      </p>
                    )}
                  </>
                )}
              </div>
            )}
          </section>
        </Card>

        {/* inspector */}
        {!focusMode && (
          <Card className={`flex w-[400px] shrink-0 flex-col overflow-hidden ${tourOn('inspector')}`}>
            <div data-tour="inspector" className="flex min-h-0 flex-1 flex-col">
              <Inspector claim={current} docId={docId} tab={tab} setTab={setTab} focused={focused} setFocused={setFocused}
                editable={!!view?.editable} nav={nav} onOpenEvidence={setEvidenceAt}
                onAccept={(s) => accept(current.id, s)} onReject={(s) => reject(current.id, s)}
                onRework={(s, text) => accept(current.id, s, text)} onIgnore={ignore} />
            </div>
          </Card>
        )}
      </div>

      {evidenceAt != null && current?.evidence?.[evidenceAt] && (
        <EvidenceModal items={current.evidence} index={evidenceAt} setIndex={setEvidenceAt} onClose={() => setEvidenceAt(null)} documents={info?.documents || []} />
      )}

      {toast && <div className="fixed bottom-5 left-1/2 z-50 -translate-x-1/2 rounded-xl bg-slate-900 px-4 py-2.5 text-[13px] font-medium text-white shadow-xl">{toast}</div>}

      {tour >= 0 && (
        <>
          {/* Nền mờ ở z-40, vùng được giới thiệu ở z-41 (.gs-tour-target), thẻ ở z-42 để luôn bấm được. */}
          <div className="fixed inset-0 z-40 bg-slate-900/30" />
          <div className="fixed left-1/2 top-24 z-[42] w-[28rem] -translate-x-1/2 rounded-2xl bg-white p-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-emerald-700">Hướng dẫn {tour + 1}/{TOUR.length}</p>
              <div className="flex gap-1">{TOUR.map((_, i) => <span key={i} className={`h-1.5 w-5 rounded-full ${i <= tour ? 'bg-emerald-500' : 'bg-slate-200'}`} />)}</div>
            </div>
            <p className="mt-2 text-base font-bold text-slate-900">{TOUR[tour][1]}</p>
            <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{TOUR[tour][2]}</p>
            <div className="mt-4 flex justify-between">
              <Btn tone="ghost" onClick={endTour}>Bỏ qua</Btn>
              <div className="flex gap-2">
                {tour > 0 && <Btn onClick={() => setTour(tour - 1)}><Icon name="arrowLeft" className="h-3.5 w-3.5" />Trước</Btn>}
                {tour < TOUR.length - 1 ? <Btn tone="primary" onClick={() => setTour(tour + 1)}>Tiếp<Icon name="arrowRight" className="h-3.5 w-3.5" /></Btn> : <Btn tone="primary" onClick={endTour}>Bắt đầu</Btn>}
              </div>
            </div>
          </div>
        </>
      )}

      {help && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/30" onClick={() => setHelp(false)}>
          <div className="w-[26rem] rounded-2xl bg-white p-5 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <p className="flex items-center gap-2 text-base font-bold"><Icon name="keyboard" className="h-5 w-5 text-emerald-700" />Phím tắt</p>
            <table className="mt-3 w-full text-[13px]">
              <tbody>
                {[['F8 / Shift+F8', 'Mục kế tiếp / trước đó'], ['Ctrl+.', 'Mở đề xuất sửa cho tuyên bố tại con trỏ'], ['Ctrl+Enter', 'Chấp nhận đề xuất đang chọn'], ['Esc', 'Từ chối đề xuất đang chọn'], ['Ctrl+Z / Ctrl+Y', 'Hoàn tác / làm lại'], ['Ctrl+S', 'Lưu phiên bản'], ['Ctrl+F', 'Tìm trong văn bản']].map(([k, v]) => (
                  <tr key={k} className="border-b border-slate-100 last:border-0"><td className="py-2"><kbd className="rounded-md border border-slate-300 bg-slate-50 px-1.5 py-0.5 font-mono text-xs">{k}</kbd></td><td className="text-slate-600">{v}</td></tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4 text-right"><Btn onClick={() => setHelp(false)}>Đóng</Btn></div>
          </div>
        </div>
      )}
    </div>
  )
}
