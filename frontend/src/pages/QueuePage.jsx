import { useMemo, useState } from 'react'
import { workpaperUrl } from '../api.js'
import { Link, navigate } from '../lib/router.jsx'
import { Chip, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import Overview from '../components/Overview.jsx'
import NextStep from '../components/NextStep.jsx'
import { Icon } from '../components/icons.jsx'
import { labelOf } from '../lib/labels.js'
import { onward, stepPath } from '../lib/flow.js'
import SourceViewer from '../components/SourceViewer.jsx'
import { buildQueue, figureAsEvidence, formatFigure, reasonText, tagsFor, tensionOf } from '../lib/queue.js'

/**
 * Step 2 of the workflow, and the page a finished run opens on.
 *
 * Not a verdict table: the order in which an auditor should open things, with
 * the reason for each position, claims and disclosed figures in one list. What
 * this pass did not examine is stated at the bottom, because a work list
 * without its boundary is not something an auditor can sign.
 */

const TABS = [
  ['todo', 'Cần soát'],
  ['seen', 'Đã xem, chưa chốt'],
  ['done', 'Đã chốt'],
  ['rest', 'Ngoài hàng đợi'],
  ['audit', 'Mẫu kiểm ngẫu nhiên'],
]

function stateOf(item, reviewStates) {
  if (item.item_type !== 'claim') return 'AI_SUGGESTED'
  return reviewStates[item.item_id] || 'AI_SUGGESTED'
}

// Soft tinted cards: the colour says what kind of number it is, the number itself stays dark.
const STAT_TONE = {
  slate: ['bg-slate-50 ring-slate-200/70', 'text-slate-500'],
  amber: ['bg-amber-50/80 ring-amber-100', 'text-amber-600'],
  emerald: ['bg-emerald-50/80 ring-emerald-100', 'text-emerald-600'],
  red: ['bg-red-50/80 ring-red-100', 'text-red-600'],
  sky: ['bg-sky-50/80 ring-sky-100', 'text-sky-600'],
}

function Stat({ label, value, hint, icon, tone = 'slate' }) {
  const [card, ink] = STAT_TONE[tone] || STAT_TONE.slate
  return (
    <div className={`flex items-start gap-3 rounded-2xl px-4 py-3.5 ring-1 ${card}`}>
      {icon && <span className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white shadow-sm ${ink}`}><Icon name={icon} className="h-5 w-5" /></span>}
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-500">{label}</p>
        <p className="mt-0.5 text-2xl font-bold leading-tight tabular-nums text-slate-900">{value}</p>
        {hint && <p className="mt-0.5 text-xs leading-snug text-slate-500">{hint}</p>}
      </div>
    </div>
  )
}

export default function QueuePage({ runId, runLabel, result, rows, summary, reviewStates = {} }) {
  const [tab, setTab] = useState('todo')
  const [viewing, setViewing] = useState(null)
  const [openKey, setOpenKey] = useState(null)   // the one row shown expanded; the rest stay one line each
  const queue = useMemo(() => buildQueue(result, rows), [result, rows])

  const lists = useMemo(() => {
    const todo = []
    const seen = []
    const done = []
    for (const item of queue.queued) {
      const state = stateOf(item, reviewStates)
      if (state === 'FINALIZED') done.push(item)
      else if (state === 'HUMAN_REVIEWED') seen.push(item)
      else todo.push(item)
    }
    return { todo, seen, done, rest: queue.rest, audit: queue.items.filter((i) => i.audit_sample) }
  }, [queue, reviewStates])

  const list = lists[tab] || []
  const auditNote = tab === 'audit'
    ? 'Các tuyên bố này nằm ngoài hàng đợi, được rút ngẫu nhiên (chạy lại cho cùng mẫu). Đọc chúng để ước lượng hàng đợi bỏ sót bao nhiêu: '
      + 'đọc n mẫu mà không thấy mục nào lẽ ra phải soát thì tỉ lệ bỏ sót có cận trên khoảng 3/n.'
    : null
  // Only claims can be decided; a disclosed figure is looked up on its page and has no decision to record.
  const queuedClaims = queue.queued.filter((i) => i.item_type === 'claim')
  const finalized = lists.done.length
  const figures = (result?.disclosed_figures || []).length
  const entity = (result?.entity || []).join(', ')

  const open = (item) => {
    if (item.item_type === 'figure') setViewing(figureAsEvidence(item.figure, item.checks))
    else navigate(`/runs/${runId}/claims/${item.item_id}?from=queue`)
  }

  const openClaims = [...lists.todo, ...lists.seen].filter((i) => i.item_type === 'claim').sort((a, b) => a.rank - b.rank)
  const nextItem = openClaims[0] || null
  const left = openClaims.length

  return (
    <div className="space-y-4">
      {viewing && <SourceViewer evidence={viewing} onClose={() => setViewing(null)} />}

      {nextItem ? (
        <NextStep step={2} action={{ label: `Mở mục ${nextItem.rank} →`, onClick: () => open(nextItem) }}
          alt={finalized > 0 ? { label: 'hoặc sang bước 3 →', to: stepPath('studio', runId) } : null}>
          Còn <b>{left}</b> tuyên bố cần chốt. Mở từng mục, đọc đoạn bằng chứng, rồi chốt.
        </NextStep>
      ) : (
        <NextStep step={2} done action={onward('queue', runId)} alt={{ label: 'bỏ qua, tới bước 4 →', to: stepPath('export', runId) }}>
          {queuedClaims.length > 0 ? <>Đã chốt hết {queuedClaims.length} tuyên bố trong hàng đợi.</> : <>Hàng đợi không có tuyên bố nào cần chốt.</>}
          {' '}Bước 3 (tuỳ chọn): xem gợi ý sửa từng câu của báo cáo.
        </NextStep>
      )}

      <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <h2 className="truncate text-base font-semibold text-slate-900">{runLabel || 'Phiên chưa đặt tên'}</h2>
            <p className="text-xs text-slate-500">
              {entity ? <>Đơn vị: <b className="text-slate-700">{entity}</b> · </> : null}
              {summary.documents.length} tài liệu nguồn tuyên bố · {summary.total} tuyên bố · {figures} số liệu công bố
            </p>
            <p className="mt-1 text-xs" data-testid="run-model-stages">
              {result?.manifest?.model_stages ? (
                <span className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-sky-900">
                  Phiên này có mô hình cùng đọc: <b className="font-mono font-medium">{String(Object.values(result.manifest.model_stages.routes || {})[0] || '').split(':').slice(1).join(':')}</b>
                  {result.manifest.model_stages.mode === 'local' ? ' · chạy trên máy' : ' · trên đám mây'} · mô hình không tự kết luận “ủng hộ” hay “mâu thuẫn”
                </span>
              ) : (
                <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-slate-600">Phiên này chỉ dùng luật và phép tính</span>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <a href={workpaperUrl(runId)} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50">
              Xem giấy làm việc
            </a>
          </div>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-4">
          <Stat icon="file" tone="amber" label="Nên soát trước" value={queue.queued.length} hint={`trên ${queue.items.length} mục đã sàng lọc`} />
          <Stat icon="checkCircle" tone="emerald" label="Đã chốt" value={`${finalized}/${queuedClaims.length}`} hint="tuyên bố trong hàng đợi" />
          <Stat icon="alert" tone={summary.contradicted.length ? 'red' : 'slate'} label="Có đoạn mâu thuẫn" value={summary.contradicted.length} hint="cần đọc kỹ nguồn" />
          <Stat icon="database" tone="sky" label="Độ phủ kho tài liệu" value={summary.corpus ? `${Math.round((summary.corpus.coverage || 0) * 100)}%` : '—'} hint={summary.corpus?.sufficient_for_absence ? 'đủ để kết luận vắng bằng chứng' : 'chưa đủ để kết luận vắng bằng chứng'} />
        </div>
        {queue.legacy && (
          <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
            Phiên này được tạo trước khi có lớp xếp ưu tiên — thứ tự dưới đây chỉ theo mức rủi ro. Chạy lại tài liệu để có hàng đợi đầy đủ.
          </p>
        )}
      </section>

      <div className="flex flex-wrap items-center gap-2">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`rounded-full border px-3 py-1 text-xs font-medium ${tab === key ? 'border-[#047857] bg-[#047857] text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}
          >
            {label} <span className="tabular-nums opacity-70">({lists[key].length})</span>
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-500">Thứ tự là thứ tự nên mở, không phải mức độ “xấu”.</span>
      </div>

      {auditNote && (
        <p className="rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-900">{auditNote}</p>
      )}
      <div className="rounded-2xl border border-slate-200/70 bg-white shadow-sm">
        {list.length === 0 ? (
          <p className="p-6 text-center text-sm text-slate-500">
            {tab === 'todo' ? 'Đã soát hết các mục trong hàng đợi. Việc còn lại: xuất giấy làm việc.' : 'Không có mục nào ở đây.'}
          </p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {list.map((item) => {
              const key = `${item.item_type}-${item.item_id}`
              const expanded = openKey === key
              const state = stateOf(item, reviewStates)
              const page = item.row ? item.row.claim.source_page : item.figure.source_page
              const where = `${item.row ? item.row.claim.source_name : item.figure.source_name}${page ? ` · trang ${page}` : ''}`
              const tension = tensionOf(item)
              // the tension already has its own box in the expanded row, so it is not repeated in the list of reasons
              const reasons = reasonText(item).split('\n').filter((r) => r && r.trim() !== tension.trim())
              // Collapsed: only what is needed to pick the next item. Expanded: the reasons and the machine's suggestion.
              const topic = item.row ? labelOf('claim_type', item.row.claim.claim_type) : 'Số liệu công bố'
              const short = item.row ? item.row.claim.text : `${item.figure.label}: ${formatFigure(item.figure)}`
              return (
                <li key={key} data-testid="queue-row" className={expanded ? 'bg-emerald-50/50' : 'hover:bg-slate-50'}>
                  <div className="flex items-center gap-3 px-3 py-2.5">
                    <span className="w-7 shrink-0 text-right font-mono text-sm font-semibold text-slate-400">{item.rank}</span>
                    <button
                      type="button"
                      onClick={() => setOpenKey(expanded ? null : key)}
                      aria-expanded={expanded}
                      data-testid="queue-row-toggle"
                      title={expanded ? 'Thu gọn' : 'Xem lý do và gợi ý của máy'}
                      className="flex min-w-0 flex-1 items-center gap-3 text-left"
                    >
                      <span className="min-w-0 flex-1">
                        <span className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                          <span className="truncate text-sm font-semibold text-slate-900">{topic}</span>
                          {tension && <span className="shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800 ring-1 ring-amber-200">cần đối chiếu bảng</span>}
                        </span>
                        <span className="mt-0.5 block truncate text-[13px] text-slate-600">{short}</span>
                      </span>
                      {page ? <span className="hidden shrink-0 text-xs tabular-nums text-slate-500 sm:inline">tr. {page}</span> : null}
                      {/* phone: the verdict moves into the expanded row so the sentence keeps its width */}
                      <span className="hidden shrink-0 sm:inline-flex">{item.row ? <StatusBadge status={item.row.status} /> : <Chip tone="sky">Số liệu</Chip>}</span>
                      {item.item_type === 'claim' && state !== 'AI_SUGGESTED' && <WorkflowPill state={state} />}
                      <Icon name={expanded ? 'chevronUp' : 'chevronDown'} className="h-4 w-4 shrink-0 text-slate-400" />
                    </button>
                    <button type="button" onClick={() => open(item)} data-testid="queue-open" className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50">
                      {item.item_type === 'figure' ? 'Xem trang' : 'Mở'}
                    </button>
                  </div>
                  {expanded && (
                    <div data-testid="queue-detail" className="mx-3 mb-3 space-y-3 rounded-lg border border-slate-200 bg-white p-3.5 sm:ml-13">
                      {item.row ? (
                        <blockquote className="border-l-4 border-emerald-600 pl-3 text-sm leading-relaxed text-slate-900">{item.row.claim.text}</blockquote>
                      ) : (
                        <p className="text-sm text-slate-900">
                          {item.figure.label}: <b className="font-mono">{formatFigure(item.figure)}</b>
                          {item.figure.period ? <span className="text-slate-500"> · kỳ {item.figure.period}</span> : null}
                        </p>
                      )}
                      <p className="text-xs text-slate-500">{where}</p>
                      {tension && (
                        <p className="rounded-md bg-amber-50 px-2.5 py-1.5 text-xs leading-relaxed text-amber-950 ring-1 ring-amber-200" data-testid="queue-tension">{tension}</p>
                      )}
                      <div>
                        <p className="text-xs font-semibold text-slate-700">Vì sao nằm ở vị trí {item.rank}</p>
                        <div className="mt-1 flex flex-wrap gap-1">
                          {tagsFor(item).map((t) => <Chip key={t.text} tone={t.tone}>{t.text}</Chip>)}
                        </div>
                        {reasons.length > 0 && (
                          <ul className="mt-1.5 list-disc space-y-0.5 pl-5 text-xs leading-relaxed text-slate-600">
                            {reasons.map((r) => <li key={r}>{r}</li>)}
                          </ul>
                        )}
                      </div>
                      {item.row ? (
                        <div>
                          <p className="flex items-center gap-2 text-xs font-semibold text-slate-700">Máy gợi ý <StatusBadge status={item.row.status} /></p>
                          {item.row.rationale && <p className="mt-1 line-clamp-3 text-xs leading-relaxed text-slate-600">{item.row.rationale.replaceAll('**', '')}</p>}
                        </div>
                      ) : item.checks?.length ? (
                        <ul className="space-y-1 text-xs text-slate-600">
                          {item.checks.map((c) => <li key={c.check_id}><code className="font-mono text-slate-800">{c.calculation}</code> {c.note.replaceAll('**', '')}</li>)}
                        </ul>
                      ) : null}
                      <div className="flex items-center justify-between gap-3">
                        {item.priority_score != null
                          ? <span className="font-mono text-xs text-slate-400" title="Điểm ưu tiên (trên phần điểm tính được)">điểm ưu tiên {Math.round(item.priority_score)}/{Math.round(item.max_available || 100)}</span>
                          : <span />}
                        <button type="button" onClick={() => open(item)} className="rounded-lg bg-[#047857] px-3 py-1.5 text-xs font-semibold text-white hover:bg-brand-700">
                          {item.item_type === 'figure' ? 'Xem trang gốc →' : 'Mở để đọc bằng chứng và chốt →'}
                        </button>
                      </div>
                    </div>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {result?.scope_note && (
        <details className="rounded-xl border border-sky-200 bg-sky-50/60 p-4 text-xs leading-relaxed text-sky-950" data-testid="scope-note">
          <summary className="cursor-pointer text-sm font-semibold">
            Những gì lượt soát này chưa kiểm
            <span className="ml-2 text-xs font-normal">{queue.rest.length} mục nằm ngoài hàng đợi</span>
          </summary>
          <p className="mt-2">{result.scope_note.replaceAll('**', '')}</p>
          <p className="mt-1">Yếu tố “bất thường so với kỳ trước” chưa được tính: điểm ưu tiên không cộng phần này, và đó không có nghĩa là “không có bất thường”.</p>
          <Link to={`/runs/${runId}/claims`} className="mt-2 inline-block font-semibold text-sky-900 underline">Xem tất cả {summary.total} tuyên bố →</Link>
        </details>
      )}

      {(result?.figure_checks || []).length > 0 && (
        <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
          <h3 className="text-sm font-semibold text-slate-900">Thủ tục trên số liệu công bố</h3>
          <ul className="mt-2 space-y-1.5 text-xs">
            {result.figure_checks.map((c) => (
              <li key={c.check_id} className="flex flex-wrap items-baseline gap-2">
                <Chip tone={c.status === 'CONSISTENT' ? 'emerald' : 'red'}>{c.status === 'CONSISTENT' ? 'Khớp' : 'Không khớp'}</Chip>
                <code className="font-mono text-slate-800">{c.calculation}</code>
                <span className="text-slate-500">{c.note.replaceAll('**', '')}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <details className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
        <summary className="cursor-pointer text-sm font-semibold text-slate-900">Tổng quan kết quả sàng lọc (phân bố, thuộc tính thiếu, cổng chất lượng)</summary>
        <div className="mt-3">
          <Overview
            summary={summary}
            lastRunAt={result?.manifest?.created_at ? new Date(result.manifest.created_at) : null}
            onOpenQueue={(q, arg) => navigate(`/runs/${runId}/claims?filter=${q}${arg ? `&arg=${encodeURIComponent(arg)}` : ''}`)}
          />
        </div>
      </details>
    </div>
  )
}
