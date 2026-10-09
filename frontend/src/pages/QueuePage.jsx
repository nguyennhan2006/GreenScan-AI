import { useMemo, useState } from 'react'
import { workpaperUrl } from '../api.js'
import { Link, navigate } from '../lib/router.jsx'
import { Chip, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import Overview from '../components/Overview.jsx'
import SourceViewer from '../components/SourceViewer.jsx'
import { buildQueue, figureAsEvidence, formatFigure, reasonText, tagsFor } from '../lib/queue.js'

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
]

function stateOf(item, reviewStates) {
  if (item.item_type !== 'claim') return 'AI_SUGGESTED'
  return reviewStates[item.item_id] || 'AI_SUGGESTED'
}

function Stat({ label, value, hint }) {
  return (
    <div className="rounded-lg bg-slate-50 px-3 py-2">
      <p className="text-[11px] font-medium text-slate-500">{label}</p>
      <p className="text-xl font-semibold tabular-nums text-slate-900">{value}</p>
      {hint && <p className="text-[11px] text-slate-500">{hint}</p>}
    </div>
  )
}

export default function QueuePage({ runId, runLabel, result, rows, summary, reviewStates = {} }) {
  const [tab, setTab] = useState('todo')
  const [viewing, setViewing] = useState(null)
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
    return { todo, seen, done, rest: queue.rest }
  }, [queue, reviewStates])

  const list = lists[tab] || []
  const finalized = lists.done.length
  const figures = (result?.disclosed_figures || []).length
  const entity = (result?.entity || []).join(', ')

  const open = (item) => {
    if (item.item_type === 'figure') setViewing(figureAsEvidence(item.figure, item.checks))
    else navigate(`/runs/${runId}/claims/${item.item_id}?from=queue`)
  }

  return (
    <div className="space-y-4">
      {viewing && <SourceViewer evidence={viewing} onClose={() => setViewing(null)} />}

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-800">Bước 2 · Soát theo thứ tự ưu tiên</p>
            <h2 className="mt-0.5 truncate text-base font-semibold text-slate-900">{runLabel || 'Phiên chưa đặt tên'}</h2>
            <p className="text-xs text-slate-500">
              {entity ? <>Đơn vị: <b className="text-slate-700">{entity}</b> · </> : null}
              {summary.documents.length} tài liệu nguồn tuyên bố · {summary.total} tuyên bố · {figures} số liệu công bố
            </p>
          </div>
          <div className="flex gap-2">
            <a href={workpaperUrl(runId)} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50">
              Xem giấy làm việc
            </a>
            <Link to={`/runs/${runId}/export`} className="rounded-lg bg-[#0F3D2E] px-3 py-1.5 text-xs font-semibold text-white">
              Bước 3 · Xuất →
            </Link>
          </div>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-4">
          <Stat label="Nên soát trước" value={queue.queued.length} hint={`trên ${queue.items.length} mục đã sàng lọc`} />
          <Stat label="Đã chốt" value={`${finalized}/${queue.queued.length}`} hint="mục trong hàng đợi" />
          <Stat label="Có đoạn mâu thuẫn" value={summary.contradicted.length} hint="cần đọc kỹ nguồn" />
          <Stat label="Độ phủ kho tài liệu" value={summary.corpus ? `${Math.round((summary.corpus.coverage || 0) * 100)}%` : '—'} hint={summary.corpus?.sufficient_for_absence ? 'đủ để kết luận vắng bằng chứng' : 'chưa đủ để kết luận vắng bằng chứng'} />
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
            className={`rounded-full border px-3 py-1 text-xs font-medium ${tab === key ? 'border-[#0F3D2E] bg-[#0F3D2E] text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}
          >
            {label} <span className="tabular-nums opacity-70">({lists[key].length})</span>
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-500">Thứ tự là thứ tự nên mở, không phải mức độ “xấu”.</span>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white">
        {list.length === 0 ? (
          <p className="p-6 text-center text-sm text-slate-500">
            {tab === 'todo' ? 'Đã soát hết các mục trong hàng đợi. Sang Bước 3 để xuất giấy làm việc.' : 'Không có mục nào ở đây.'}
          </p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {list.map((item) => {
              const state = stateOf(item, reviewStates)
              const where = item.row
                ? `${item.row.claim.source_name}${item.row.claim.source_page ? ` · tr. ${item.row.claim.source_page}` : ''}`
                : `${item.figure.source_name}${item.figure.source_page ? ` · tr. ${item.figure.source_page}` : ''}`
              return (
                <li key={`${item.item_type}-${item.item_id}`} className="flex gap-3 px-3 py-3 hover:bg-emerald-50/40">
                  <span className="mt-0.5 w-7 shrink-0 text-right font-mono text-sm font-semibold text-slate-400">{item.rank}</span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Chip tone={item.item_type === 'figure' ? 'sky' : 'emerald'}>{item.item_type === 'figure' ? 'Số liệu công bố' : 'Tuyên bố'}</Chip>
                      {item.row && <StatusBadge status={item.row.status} />}
                      {item.item_type === 'claim' && <WorkflowPill state={state} />}
                      <span className="text-[11px] text-slate-500">{where}</span>
                    </div>
                    <button type="button" onClick={() => open(item)} className="mt-1 block w-full text-left">
                      {item.figure ? (
                        <span className="text-sm text-slate-900">
                          {item.figure.label}: <b className="font-mono">{formatFigure(item.figure)}</b>
                          {item.figure.period ? <span className="text-slate-500"> · kỳ {item.figure.period}</span> : null}
                        </span>
                      ) : (
                        <span className="line-clamp-2 text-sm font-medium text-slate-900 hover:underline">{item.row.claim.text}</span>
                      )}
                    </button>
                    <div className="mt-1 flex flex-wrap gap-1" title={reasonText(item)}>
                      {tagsFor(item).map((t) => <Chip key={t.text} tone={t.tone}>{t.text}</Chip>)}
                    </div>
                  </div>
                  <div className="shrink-0 self-center text-right">
                    <button type="button" onClick={() => open(item)} className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-white">
                      {item.item_type === 'figure' ? 'Xem trang' : 'Mở'}
                    </button>
                    {item.priority_score != null && <p className="mt-1 font-mono text-[10px] text-slate-400" title="Điểm ưu tiên (trên phần điểm tính được)">{Math.round(item.priority_score)}/{Math.round(item.max_available || 100)}</p>}
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {result?.scope_note && (
        <section className="rounded-xl border border-sky-200 bg-sky-50/60 p-4 text-xs leading-relaxed text-sky-950">
          <h3 className="text-sm font-semibold">Phạm vi lượt soát này — những gì chưa được kiểm</h3>
          <p className="mt-1">{result.scope_note.replaceAll('**', '')}</p>
          <p className="mt-1">Yếu tố “bất thường so với kỳ trước” chưa được tính: điểm ưu tiên không cộng phần này, và đó không có nghĩa là “không có bất thường”.</p>
          <Link to={`/runs/${runId}/claims`} className="mt-2 inline-block font-semibold text-sky-900 underline">Xem tất cả {summary.total} tuyên bố →</Link>
        </section>
      )}

      {(result?.figure_checks || []).length > 0 && (
        <section className="rounded-xl border border-slate-200 bg-white p-4">
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

      <details className="rounded-xl border border-slate-200 bg-white p-4">
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
