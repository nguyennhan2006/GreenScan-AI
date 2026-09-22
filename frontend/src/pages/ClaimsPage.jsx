import { useMemo, useState } from 'react'
import { Link } from '../lib/router.jsx'
import { PriorityBadge, STATUS_LABELS, STATUS_ORDER, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import { AttributeDots } from '../components/AttributeChecklist.jsx'

/**
 * Claim list (mockup #5): the queue, as a table.
 *
 * Filters are the backend's own enums plus the derived worklists from
 * lib/claims.js. Risk shows as a priority dot with a word, never a number —
 * the number belongs to the breakdown on the detail page.
 */

const EXTRA = [
  ['all', 'Tất cả'],
  ['unresolved', 'Chưa xử lý'],
  ['contradicted', 'Có mâu thuẫn'],
  ['noEvidence', 'Thiếu bằng chứng'],
  ['needsConfirmation', 'Cần người xác nhận'],
]

const PAGE = 25

export default function ClaimsPage({ runId, rows, summary, reviewStates = {}, initialFilter = 'all', initialArg = null }) {
  const [filter, setFilter] = useState(initialFilter)
  const [arg] = useState(initialArg)
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)

  const visible = useMemo(() => {
    let list = rows
    if (STATUS_ORDER.includes(filter)) list = rows.filter((r) => r.status === filter)
    else if (filter === 'attribute') list = rows.filter((r) => r.missing.some((m) => m.key === arg))
    else if (filter !== 'all') {
      const ids = new Set((summary[filter] || []).map((r) => r.id))
      list = rows.filter((r) => ids.has(r.id))
    }
    if (q.trim()) {
      const needle = q.trim().toLowerCase()
      list = list.filter((r) => r.claim.text.toLowerCase().includes(needle) || (r.claim.metric || '').includes(needle))
    }
    return list
  }, [rows, summary, filter, arg, q])

  const pages = Math.max(1, Math.ceil(visible.length / PAGE))
  const slice = visible.slice((page - 1) * PAGE, page * PAGE)
  const count = (key) => (STATUS_ORDER.includes(key) ? summary.byStatus[key] || 0 : key === 'all' ? rows.length : (summary[key] || []).length)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1.5">
        {[...EXTRA, ...STATUS_ORDER.map((s) => [s, STATUS_LABELS[s]])].map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => { setFilter(key); setPage(1) }}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
              filter === key ? 'border-[#0F3D2E] bg-[#0F3D2E] text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
            }`}
          >
            {label} <span className="tabular-nums opacity-70">({count(key)})</span>
          </button>
        ))}
        {filter === 'attribute' && <span className="self-center text-xs text-slate-500">Thiếu thuộc tính: <b>{arg}</b></span>}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 p-3">
          <input
            value={q}
            onChange={(e) => { setQ(e.target.value); setPage(1) }}
            placeholder="Tìm trong nguyên văn tuyên bố…"
            className="min-w-64 flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
          />
          <span className="text-xs text-slate-500">{visible.length} tuyên bố</span>
        </div>

        {slice.length === 0 ? (
          <p className="p-6 text-center text-sm text-slate-500">Không có tuyên bố nào trong bộ lọc này.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs text-slate-500">
              <tr>
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">Tuyên bố</th>
                <th className="px-3 py-2 font-medium">Chủ đề</th>
                <th className="px-3 py-2 font-medium">Trạng thái (AI)</th>
                <th className="px-3 py-2 font-medium">Thuộc tính</th>
                <th className="px-3 py-2 font-medium">Ưu tiên</th>
                <th className="px-3 py-2 font-medium">Xét duyệt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {slice.map((r, i) => (
                <tr key={r.id} className="align-top hover:bg-emerald-50/40">
                  <td className="px-3 py-2.5 font-mono text-xs text-slate-400">{(page - 1) * PAGE + i + 1}</td>
                  <td className="max-w-xl px-3 py-2.5">
                    <Link to={`/runs/${runId}/claims/${r.id}`} className="line-clamp-2 font-medium text-slate-900 hover:text-emerald-800 hover:underline">
                      {r.claim.text}
                    </Link>
                    <p className="mt-0.5 text-[11px] text-slate-500">
                      {r.claim.source_name}{r.claim.source_page ? ` · tr. ${r.claim.source_page}` : ''}
                      {r.contradicting.length > 0 && <span className="ml-2 text-red-700">{r.contradicting.length} đoạn mâu thuẫn</span>}
                      {r.evidence.length === 0 && <span className="ml-2 text-sky-700">chưa có đoạn nào</span>}
                    </p>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-700">
                    {r.claim.claim_type}
                    {r.claim.metric && <span className="block text-slate-400">{r.claim.metric}</span>}
                  </td>
                  <td className="px-3 py-2.5"><StatusBadge status={r.status} /></td>
                  <td className="px-3 py-2.5"><AttributeDots attributes={r.attributes} /></td>
                  <td className="px-3 py-2.5"><PriorityBadge severity={r.severity} /></td>
                  <td className="px-3 py-2.5"><WorkflowPill state={reviewStates[r.id] || 'AI_SUGGESTED'} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {pages > 1 && (
          <div className="flex items-center justify-end gap-1 border-t border-slate-200 p-3 text-xs">
            <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="rounded border border-slate-300 px-2 py-1 disabled:opacity-40">‹</button>
            <span className="px-2 font-mono">{page} / {pages}</span>
            <button type="button" disabled={page >= pages} onClick={() => setPage((p) => p + 1)} className="rounded border border-slate-300 px-2 py-1 disabled:opacity-40">›</button>
          </div>
        )}
      </div>
    </div>
  )
}
