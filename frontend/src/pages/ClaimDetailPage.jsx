import { useEffect, useMemo, useState } from 'react'
import { Link, navigate } from '../lib/router.jsx'
import { Chip, PriorityBadge, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import AttributeChecklist from '../components/AttributeChecklist.jsx'
import EvidencePanel from '../components/EvidencePanel.jsx'
import SourceViewer from '../components/SourceViewer.jsx'
import { stepPath } from '../lib/flow.js'
import DecisionBar from '../components/DecisionBar.jsx'
import { LegalPanel, NumericCheckCard, RiskBreakdown } from '../components/ClaimPanels.jsx'
import { OrgFindings } from '../components/OrgPackPanel.jsx'
import Precedents, { QueueReasons } from '../components/Precedents.jsx'
import NextStep from '../components/NextStep.jsx'
import { labelOf, vnDecimal } from '../lib/labels'

const READING_VI = { S: 'ủng hộ', C: 'mâu thuẫn', N: 'không kết luận' }

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
  ['org', 'Quy tắc nội bộ'],
  ['risk', 'Rủi ro & việc cần làm'],
  ['review', 'Xét duyệt'],
]

const VIEW_KEY = 'gs.detail.full'
function wantsFull() {
  try { return localStorage.getItem(VIEW_KEY) === '1' } catch { return false }
}

const ATTR_VALUE = {
  metric: 'Chỉ số', values: 'Giá trị', units: 'Đơn vị', period: 'Kỳ báo cáo', baseline: 'Năm gốc', scope: 'Phạm vi', direction: 'Xu hướng',
}

function Section({ id, title, meta, children }) {
  return (
    <section id={id} className="scroll-mt-24 rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
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
    parts.push(<u key={parts.length} className="decoration-dotted decoration-amber-600 underline-offset-4" title="Từ ngữ mơ hồ hoặc quảng bá (theo danh mục phân loại)">{rest.slice(best.idx, best.idx + best.len)}</u>)
    rest = rest.slice(best.idx + best.len)
  }
  parts.push(rest)
  return parts
}

export default function ClaimDetailPage({
  runId, rows, row, index, legal, gates, suggestion, orgFindings, precedents = [], priority = null,
  reviewStates = {}, reviewHistory = {}, reviewer, onReviewerChange, onDecide, reviewBusy, onRecheck, loading, initialTab,
  order = null, queuedIds = [],
}) {
  const [tab, setTab] = useState('attributes')
  const [viewing, setViewing] = useState(null)
  const [draft, setDraft] = useState('')
  // Compact view: the claim, the passages that decide it, the decision. Everything else is one click away.
  const [full, setFullState] = useState(() => !!initialTab || wantsFull())
  const setFull = (value) => {
    setFullState(value)
    try { if (value) localStorage.setItem(VIEW_KEY, '1'); else localStorage.removeItem(VIEW_KEY) } catch { /* chỉ đổi trong lần mở này */ }
  }
  useEffect(() => { if (initialTab) setFullState(true) }, [initialTab])

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
    return <p className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-6 text-sm text-slate-500">Không tìm thấy tuyên bố này trong phiên.</p>
  }

  const jump = (key) => {
    setTab(key)
    document.getElementById(`sec-${key}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  const state = reviewStates[row.id] || 'AI_SUGGESTED'
  const gateG7 = gates?.find((g) => g.gate_id === 'G7')
  const claim = row.claim
  const decided = state === 'FINALIZED'
  const irNotes = row.assist?.ir || []
  const irDiffer = irNotes.filter((n) => n.dual !== n.rules).length
  const toDecision = () => document.getElementById('sec-review')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  // After a decision: the next claim of the queue that is still open, looking forward from this one, then from the top.
  const at = queuedIds.indexOf(row.id)
  const openNext = [...queuedIds.slice(at + 1), ...queuedIds.slice(0, Math.max(at, 0))]
    .find((id) => id !== row.id && reviewStates[id] !== 'FINALIZED') || null

  return (
    <>
      {viewing && <SourceViewer evidence={viewing} onClose={() => setViewing(null)} />}
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <Link to={order?.length ? `/runs/${runId}` : `/runs/${runId}/claims`} className="hover:underline">{order?.length ? '← Hàng đợi soát' : '← Danh sách tuyên bố'}</Link>
          <span>·</span>
          <span>{!order?.length ? `Tuyên bố #${(index ?? pos) + 1} / ${rows.length}`
            : priority?.in_queue ? `Mục ${priority.rank} trong hàng đợi` : 'Ngoài hàng đợi (xem thêm, không bắt buộc chốt)'}</span>
          <span className="ml-auto flex gap-1">
            <button type="button" disabled={!prev} onClick={() => navigate(`/runs/${runId}/claims/${prev.id}${suffix}`)} className="rounded border border-slate-300 px-2 py-0.5 disabled:opacity-40">‹ trước</button>
            <button type="button" disabled={!next} onClick={() => navigate(`/runs/${runId}/claims/${next.id}${suffix}`)} className="rounded border border-slate-300 px-2 py-0.5 disabled:opacity-40">sau ›</button>
            <button type="button" onClick={() => setFull(!full)} data-testid="detail-view-toggle" className="ml-2 rounded border border-slate-300 px-2 py-0.5 font-medium text-slate-700 hover:bg-slate-100">{full ? 'Xem gọn' : 'Xem đầy đủ'}</button>
          </span>
        </div>

        {decided ? (
          <NextStep step={2} done action={openNext
            ? { label: 'Mục tiếp theo →', onClick: () => navigate(`/runs/${runId}/claims/${openNext}?from=queue`) }
            : { label: 'Về hàng đợi →', to: `/runs/${runId}` }}
            alt={openNext ? { label: 'hoặc sang bước 3 →', to: stepPath('studio', runId) } : null}>
            Đã chốt mục này. {openNext ? 'Sang mục tiếp theo trong hàng đợi.' : 'Không còn tuyên bố nào trong hàng đợi chờ chốt.'}
          </NextStep>
        ) : (
          <NextStep step={2} action={{ label: 'Tới phần quyết định ↓', onClick: toDecision }}>
            Đọc đoạn bằng chứng bên dưới; bấm <b>Mở nguồn</b> nếu muốn xem trang gốc. Sau đó chốt: xác nhận gợi ý của máy, hoặc sửa nếu máy sai.
          </NextStep>
        )}

        {/* A. Claim header */}
        <article className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-5">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={row.status} size="md" />
            <WorkflowPill state={state} />
            <Chip>{labelOf('claim_type', claim.claim_type)}</Chip>
            <Chip>{labelOf('language', claim.language)}</Chip>
            {claim.is_future_commitment && <Chip tone="violet">cam kết tương lai</Chip>}
            {row.flagged && <Chip tone="red" className="cursor-help"><span title={(row.warnings || []).join('\n') || 'Tuyên bố hoặc bằng chứng chứa câu nhắn tới hệ thống chấm tự động.'}>nghi chèn lệnh nhắm vào máy chấm</span></Chip>}
            {row.misread && <Chip tone="amber" className="cursor-help"><span title={misreadNote(row)}>số đọc từ trang quét chưa chắc</span></Chip>}
            {row.suspect && <Chip tone="amber" className="cursor-help"><span title={`Máy gợi ý: ${labelOf('quality_flag', row.suspect)}. Câu vẫn giữ kết luận kiểm chứng nhưng không vào hàng đợi và không chấm điểm rủi ro; người soát xem trang gốc để quyết định.`}>có thể không phải tuyên bố</span></Chip>}
            <span className="ml-auto"><PriorityBadge severity={row.severity} /></span>
          </div>
          <blockquote className="mt-3 border-l-2 border-emerald-700 pl-4 text-xl leading-relaxed text-slate-900">
            “{highlightVague(claim.text, claim.vague_terms_matched)}”
          </blockquote>
          <p className="mt-2 text-xs text-slate-500">
            {claim.source_name}{claim.source_page ? ` · tr. ${claim.source_page}` : ''} · id <span className="font-mono">{claim.claim_id}</span>
          </p>
          <p className="mt-3 text-sm text-slate-700">{row.rationale}</p>
          {row.assessment && (
            <p className="mt-2 flex flex-wrap gap-2 text-xs">
              <Chip tone={row.assessment.consistency === 'conflict' ? 'red' : row.assessment.consistency === 'match' ? 'emerald' : 'slate'}>Nhất quán: {row.assessment.consistency_vi}</Chip>
              <Chip tone={row.assessment.source_independence === 'independent' ? 'emerald' : 'amber'}>Nguồn: {row.assessment.source_independence_vi}</Chip>
              <Chip tone="slate">Căn cứ: {row.assessment.basis_vi}</Chip>
            </p>
          )}
          {row.assist?.explanation?.text && (
            <div className="mt-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
              <p className="text-xs font-medium text-slate-500">Diễn giải bằng mô hình ngôn ngữ (để tham khảo; mô hình không tự kết luận “ủng hộ” hay “mâu thuẫn”)</p>
              <p className="mt-1">{row.assist.explanation.text}</p>
              {row.assist.explanation.next_action && <p className="mt-1 text-xs text-slate-600">Gợi ý bước tiếp: {row.assist.explanation.next_action}</p>}
            </div>
          )}
          {irNotes.length > 0 && (
            <details open={full} className="mt-2 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2 text-xs text-violet-900" data-testid="ir-notes">
              <summary className="cursor-pointer font-medium">
                Mô hình cũng đọc số liệu ở {irNotes.length} đoạn{irDiffer ? `: ${irDiffer} đoạn đọc khác luật, nên xem lại` : ': không đoạn nào đọc khác luật'}
              </summary>
              <p className="mt-1">Chỉ để người soát xem, không đổi kết luận.</p>
              <ul className="mt-1 list-disc pl-4">
                {irNotes.map((n, i) => (
                  <li key={i}>{n.citation}: quy tắc {READING_VI[n.rules] || n.rules}, mô hình {READING_VI[n.ir] || n.ir}{n.dual !== n.rules ? ' — khác quy tắc, nên xem lại' : ''}</li>
                ))}
              </ul>
            </details>
          )}
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
        {full && (
        <nav className="sticky top-0 z-10 -mx-1 flex gap-1 overflow-x-auto border-b border-slate-200 bg-slate-50/95 px-1 py-2 backdrop-blur">
          {TABS.map(([k, l]) => (
            <button
              key={k}
              type="button"
              onClick={() => jump(k)}
              className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${tab === k ? 'bg-[#047857] text-white' : 'text-slate-700 hover:bg-slate-200'}`}
            >
              {l}
              {k === 'evidence' && ` (${row.evidence.length})`}
              {k === 'risk' && suggestion?.items?.length ? ` (${suggestion.items.length})` : ''}
            </button>
          ))}
        </nav>
        )}

        {/* B. Attributes */}
        {full && (
        <div id="sec-attributes" className="grid scroll-mt-24 gap-4 lg:grid-cols-[1fr_320px]">
          <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
            <AttributeChecklist attributes={row.attributes} penalties={row.penalties} variant="fix" />
          </section>
          <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
            <h3 className="text-sm font-semibold text-slate-900">Giá trị trích xuất</h3>
            <p className="text-xs text-slate-500">Máy đọc theo danh mục phân loại; khi bật mô hình ngôn ngữ, giá trị được chuẩn hoá thêm.</p>
            <dl className="mt-2 space-y-1 text-xs">
              {Object.entries(ATTR_VALUE).map(([k, l]) => {
                const v = claim[k]
                const kind = k === 'units' ? 'unit' : k === 'scope' ? 'scope' : k === 'direction' ? 'direction' : k === 'metric' ? 'metric' : null
                const shown = Array.isArray(v) ? (v.length ? (kind ? labelOf(kind, v) : v.join(', ')) : null) : (kind ? labelOf(kind, v) : v)
                return (
                  <div key={k} className="flex justify-between gap-3">
                    <dt className="text-slate-500">{l}</dt>
                    <dd className={`text-right ${shown == null ? 'text-red-700' : 'text-slate-900'}`}>{shown == null ? 'không nêu' : String(shown)}</dd>
                  </div>
                )
              })}
              <div className="flex justify-between gap-3"><dt className="text-slate-500">Độ tin cậy trích xuất</dt><dd className="font-mono">{vnDecimal(claim.confidence)}</dd></div>
            </dl>
          </section>
        </div>
        )}

        {/* C. Evidence */}
        <Section id="sec-evidence" title="Bằng chứng" meta={`${row.evidence.length} đoạn · ${row.supporting.length} ủng hộ · ${row.contradicting.length} mâu thuẫn`}>
          <EvidencePanel key={row.id} evidence={row.evidence} onJumpToSource={setViewing} compact={!full} />
        </Section>

        {/* D. Numeric */}
        {(full || row.computed?.closest_pair) && (
        <Section id="sec-numeric" title="Kiểm tra số liệu" meta="phép so sánh do mã xác định, không do mô hình">
          <NumericCheckCard computed={row.computed} />
        </Section>
        )}

        {/* E. Legal */}
        {full && (
        <Section id="sec-legal" title="Bối cảnh pháp lý" meta="văn bản áp dụng theo ngày hiệu lực">
          <LegalPanel legal={legal} gate={gateG7} />
        </Section>
        )}

        {/* E2. Internal rules (org packs): beside the verdict, never on it */}
        {(full || (orgFindings || []).some((f) => f.outcome !== 'NOT_APPLICABLE')) && (
        <Section id="sec-org" title="Quy tắc nội bộ" meta={orgFindings ? `${orgFindings.filter((f) => f.outcome !== 'NOT_APPLICABLE').length} quy tắc áp dụng` : 'chưa bật'}>
          <OrgFindings findings={orgFindings} />
        </Section>
        )}

        {/* E3. Precedents: claims a person already decided (feedback-loop-v1), beside the verdict */}
        {(full || precedents.length > 0) && (
        <Section id="sec-precedents" title="Tiền lệ của người soát" meta={precedents.length ? `${precedents.length} tuyên bố tương tự` : 'chưa có'}>
          <div className="space-y-2">
            {full && <QueueReasons priority={priority} />}
            <Precedents cards={precedents} />
          </div>
        </Section>
        )}

        {/* F+G. Risk & to-do */}
        {full && (
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
                  {it.example_fix && <p className="mt-1 rounded bg-emerald-50 px-2 py-1 font-mono text-xs text-emerald-900">{it.example_fix}</p>}
                </li>
              ))}
            </ul>
            {onRecheck && (
              <form className="mt-3 border-t border-slate-200 pt-3" onSubmit={(e) => { e.preventDefault(); if (draft.trim()) onRecheck(claim, draft.trim()) }}>
                <label className="text-xs font-semibold text-slate-800">✎ Sửa tuyên bố và chạy lại (tạo phiên mới)</label>
                <textarea rows={3} value={draft} onChange={(e) => setDraft(e.target.value)} placeholder={claim.text} className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" />
                <button type="submit" disabled={!draft.trim() || loading} className="mt-2 rounded-lg bg-[#047857] px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40">{loading ? 'Đang chạy…' : 'Chạy lại'}</button>
              </form>
            )}
          </Section>
        </div>
        )}

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
            evidence={row.evidence || []}
            ruleOptions={[
              ...(legal?.rules_applied || []).map((id) => ({ id, label: `${id} · quy tắc pháp lý` })),
              ...(orgFindings || []).filter((f) => f.outcome !== 'NOT_APPLICABLE')
                .map((f) => ({ id: f.rule_id, label: `${f.rule_id} · ${f.title || 'quy tắc nội bộ'}` })),
            ]}
          />
        </div>

        {!full && (
          <p className="text-center text-xs text-slate-500">
            Còn nữa: thuộc tính của tuyên bố, bối cảnh pháp lý, phân rã rủi ro, việc cần làm.{' '}
            <button type="button" onClick={() => setFull(true)} className="font-semibold text-emerald-800 hover:underline">Xem đầy đủ</button>
          </p>
        )}
      </div>
    </>
  )
}

// Tooltip of the "số đọc từ trang quét chưa chắc" chip: which numbers, and how sure OCR was of the page.
function misreadNote(row) {
  const numbers = row.doubtfulNumbers.length ? `Số OCR đọc chưa chắc: ${row.doubtfulNumbers.join(', ')}. ` : ''
  const page = row.ocrConfidence != null ? `Trang đọc với độ tin cậy trung bình ${Math.round(row.ocrConfidence)}/100. ` : ''
  return `${numbers}${page}So khớp số liệu dựa trên các số này không được dùng để kết luận; đối chiếu trang gốc.`
}
