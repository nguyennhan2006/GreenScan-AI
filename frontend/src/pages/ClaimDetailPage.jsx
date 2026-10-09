import { useEffect, useMemo, useState } from 'react'
import { Link, navigate } from '../lib/router.jsx'
import { Chip, PriorityBadge, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import AttributeChecklist from '../components/AttributeChecklist.jsx'
import EvidencePanel from '../components/EvidencePanel.jsx'
import SourceViewer from '../components/SourceViewer.jsx'
import DecisionBar from '../components/DecisionBar.jsx'
import { LegalPanel, NumericCheckCard, RiskBreakdown } from '../components/ClaimPanels.jsx'

/**
 * One claim, in audit order (mockup #6 + spec S3): verbatim → 5 attributes →
 * evidence → numeric check → legal context → risk breakdown → to-do → decision.
 *
 * Tabs only choose which block is scrolled into view; every block is always
 * rendered so a reviewer never has to hunt for the evidence behind a badge.
 */

const TABS = [
  ['attributes', 'Thuộc tính'],
  ['evidence', 'Bằng chứng'],
  ['numeric', 'Kiểm tra số'],
  ['legal', 'Pháp lý'],
  ['risk', 'Rủi ro & việc cần làm'],
  ['review', 'Xét duyệt'],
]

const ATTR_VALUE = {
  metric: 'Chỉ số', values: 'Giá trị', units: 'Đơn vị', period: 'Kỳ báo cáo', baseline: 'Năm gốc', scope: 'Phạm vi', direction: 'Xu hướng',
}

function Section({ id, title, meta, children }) {
  return (
    <section id={id} className="scroll-mt-24 rounded-xl border border-slate-200 bg-white p-4">
      <div className="mb-3 flex flex-wrap items-baseline gap-2">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {meta && <span className="text-xs text-slate-500">{meta}</span>}
      </div>
      {children}
    </section>
  )
}

function highlightVague(text, terms) {
  if (!terms?.length) return text
  const parts = []
  let rest = text
  const lower = () => rest.toLowerCase()
  // Simple sequential scan; enough for a handful of lexicon hits per sentence.
  let guard = 0
  while (rest && guard++ < 20) {
    let best = null
    for (const t of terms) {
      const idx = lower().indexOf(t.toLowerCase())
      if (idx >= 0 && (best === null || idx < best.idx)) best = { idx, len: t.length }
    }
    if (!best) break
    parts.push(rest.slice(0, best.idx))
    parts.push(<u key={parts.length} className="decoration-dotted decoration-amber-600 underline-offset-4" title="Từ ngữ mơ hồ/quảng bá theo taxonomy">{rest.slice(best.idx, best.idx + best.len)}</u>)
    rest = rest.slice(best.idx + best.len)
  }
  parts.push(rest)
  return parts
}

export default function ClaimDetailPage({
  runId, rows, row, index, legal, gates, suggestion,
  reviewStates = {}, reviewHistory = {}, reviewer, onReviewerChange, onDecide, reviewBusy, onRecheck, loading, initialTab,
  order = null,
}) {
  const [tab, setTab] = useState('attributes')
  const [viewing, setViewing] = useState(null)
  const [draft, setDraft] = useState('')

  useEffect(() => {
    setDraft('')
    setTab(initialTab || 'attributes')
    if (initialTab) setTimeout(() => document.getElementById(`sec-${initialTab}`)?.scrollIntoView({ block: 'start' }), 0)
    else window.scrollTo({ top: 0 })
  }, [row?.id, initialTab])

  // Opened from the queue, previous/next walk the queue; otherwise the document.
  const sequence = useMemo(() => (order?.length ? order : rows.map((r) => r.id)), [order, rows])
  const suffix = order?.length ? '?from=queue' : ''
  const pos = useMemo(() => sequence.indexOf(row?.id), [sequence, row?.id])
  const prev = pos > 0 ? { id: sequence[pos - 1] } : null
  const next = pos >= 0 && pos < sequence.length - 1 ? { id: sequence[pos + 1] } : null

  if (!row) {
    return <p className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">Không tìm thấy tuyên bố này trong phiên.</p>
  }

  const jump = (key) => {
    setTab(key)
    document.getElementById(`sec-${key}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  const state = reviewStates[row.id] || 'AI_SUGGESTED'
  const gateG7 = gates?.find((g) => g.gate_id === 'G7')
  const claim = row.claim

  return (
    <>
      {viewing && <SourceViewer evidence={viewing} onClose={() => setViewing(null)} />}
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <Link to={order?.length ? `/runs/${runId}` : `/runs/${runId}/claims`} className="hover:underline">{order?.length ? '← Hàng đợi soát' : '← Danh sách tuyên bố'}</Link>
          <span>·</span>
          <span>{order?.length ? `Mục ${pos + 1} / ${sequence.length} theo thứ tự ưu tiên` : `Tuyên bố #${(index ?? pos) + 1} / ${rows.length}`}</span>
          <span className="ml-auto flex gap-1">
            <button type="button" disabled={!prev} onClick={() => navigate(`/runs/${runId}/claims/${prev.id}${suffix}`)} className="rounded border border-slate-300 px-2 py-0.5 disabled:opacity-40">‹ trước</button>
            <button type="button" disabled={!next} onClick={() => navigate(`/runs/${runId}/claims/${next.id}${suffix}`)} className="rounded border border-slate-300 px-2 py-0.5 disabled:opacity-40">sau ›</button>
          </span>
        </div>

        {/* A. Claim header */}
        <article className="rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={row.status} size="md" />
            <WorkflowPill state={state} />
            <Chip>{claim.claim_type}</Chip>
            <Chip>{claim.language}</Chip>
            {claim.is_future_commitment && <Chip tone="violet">cam kết tương lai</Chip>}
            {row.flagged && <Chip tone="red">có dấu hiệu tiêm lệnh trong bằng chứng</Chip>}
            <span className="ml-auto"><PriorityBadge severity={row.severity} /></span>
          </div>
          <blockquote className="mt-3 border-l-2 border-emerald-700 pl-4 text-xl leading-relaxed text-slate-900">
            “{highlightVague(claim.text, claim.vague_terms_matched)}”
          </blockquote>
          <p className="mt-2 text-xs text-slate-500">
            {claim.source_name}{claim.source_page ? ` · tr. ${claim.source_page}` : ''} · id <span className="font-mono">{claim.claim_id}</span>
          </p>
          <p className="mt-3 text-sm text-slate-700">{row.rationale}</p>
          {row.isAbstain && (
            <p className="mt-2 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-900">
              Đây là kết quả hợp lệ, không phải lỗi — và không có nghĩa doanh nghiệp vi phạm. Tài liệu hiện có chưa đủ để kiểm chứng tuyên bố này.
            </p>
          )}
          {row.requiresReview && (
            <p className="mt-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
              Cần người xác nhận trước khi phát hành{row.risk?.requires_human_review && row.status === 'CONTRADICTED' ? ' — có mâu thuẫn' : ''}.
            </p>
          )}
        </article>

        {/* Tabs */}
        <nav className="sticky top-0 z-10 -mx-1 flex gap-1 overflow-x-auto border-b border-slate-200 bg-slate-50/95 px-1 py-2 backdrop-blur">
          {TABS.map(([k, l]) => (
            <button
              key={k}
              type="button"
              onClick={() => jump(k)}
              className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${tab === k ? 'bg-[#0F3D2E] text-white' : 'text-slate-700 hover:bg-slate-200'}`}
            >
              {l}
              {k === 'evidence' && ` (${row.evidence.length})`}
              {k === 'risk' && suggestion?.items?.length ? ` (${suggestion.items.length})` : ''}
            </button>
          ))}
        </nav>

        {/* B. Attributes */}
        <div id="sec-attributes" className="grid scroll-mt-24 gap-4 lg:grid-cols-[1fr_320px]">
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <AttributeChecklist attributes={row.attributes} penalties={row.penalties} variant="fix" />
          </section>
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-slate-900">Giá trị trích xuất</h3>
            <p className="text-[11px] text-slate-500">Heuristic theo taxonomy — nhãn “AI đề xuất” khi có LLM chuẩn hoá.</p>
            <dl className="mt-2 space-y-1 text-xs">
              {Object.entries(ATTR_VALUE).map(([k, l]) => {
                const v = claim[k]
                const shown = Array.isArray(v) ? (v.length ? v.join(', ') : null) : v
                return (
                  <div key={k} className="flex justify-between gap-3">
                    <dt className="text-slate-500">{l}</dt>
                    <dd className={`text-right font-mono ${shown == null ? 'text-red-700' : 'text-slate-900'}`}>{shown == null ? 'không nêu' : String(shown)}</dd>
                  </div>
                )
              })}
              <div className="flex justify-between gap-3"><dt className="text-slate-500">Độ tin cậy trích xuất</dt><dd className="font-mono">{claim.confidence?.toFixed(2)}</dd></div>
            </dl>
          </section>
        </div>

        {/* C. Evidence */}
        <Section id="sec-evidence" title="Bằng chứng" meta={`${row.evidence.length} đoạn · ${row.supporting.length} ủng hộ · ${row.contradicting.length} mâu thuẫn`}>
          <EvidencePanel evidence={row.evidence} onJumpToSource={setViewing} />
        </Section>

        {/* D. Numeric */}
        <Section id="sec-numeric" title="Kiểm tra số liệu" meta="phép so sánh do mã xác định, không do mô hình">
          <NumericCheckCard computed={row.computed} />
        </Section>

        {/* E. Legal */}
        <Section id="sec-legal" title="Bối cảnh pháp lý" meta="văn bản áp dụng theo ngày hiệu lực">
          <LegalPanel legal={legal} gate={gateG7} />
        </Section>

        {/* F+G. Risk & to-do */}
        <div id="sec-risk" className="grid scroll-mt-24 gap-4 lg:grid-cols-2">
          <Section title="Phân rã rủi ro" meta="gợi ý ưu tiên xem xét">
            <RiskBreakdown risk={row.risk} />
          </Section>
          <Section title="Việc cần làm để tuyên bố kiểm chứng được" meta={suggestion?.items?.length ? `${suggestion.items.length} mục` : 'không có'}>
            <ul className="space-y-2">
              {(suggestion?.items || []).map((it, i) => (
                <li key={i} className="rounded-lg border border-slate-200 p-2.5 text-xs">
                  <p className="font-semibold text-slate-900">☐ {it.issue}</p>
                  <p className="mt-0.5 text-slate-700">{it.recommendation}</p>
                  {it.example_fix && <p className="mt-1 rounded bg-emerald-50 px-2 py-1 font-mono text-[11px] text-emerald-900">{it.example_fix}</p>}
                  <p className="mt-1 font-mono text-[10px] text-slate-400">{it.code}</p>
                </li>
              ))}
            </ul>
            {onRecheck && (
              <form className="mt-3 border-t border-slate-200 pt-3" onSubmit={(e) => { e.preventDefault(); if (draft.trim()) onRecheck(claim, draft.trim()) }}>
                <label className="text-xs font-semibold text-slate-800">✎ Sửa tuyên bố và chạy lại (tạo phiên mới)</label>
                <textarea rows={3} value={draft} onChange={(e) => setDraft(e.target.value)} placeholder={claim.text} className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" />
                <button type="submit" disabled={!draft.trim() || loading} className="mt-2 rounded-lg bg-[#0F3D2E] px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40">{loading ? 'Đang chạy…' : 'Chạy lại'}</button>
              </form>
            )}
          </Section>
        </div>

        {/* H. Decision */}
        <div id="sec-review" className="scroll-mt-24">
          <DecisionBar
            row={row}
            state={state}
            history={reviewHistory[row.id] || []}
            reviewer={reviewer}
            onReviewerChange={onReviewerChange}
            onDecide={(d) => onDecide(row, d)}
            busy={reviewBusy}
          />
        </div>
      </div>
    </>
  )
}
