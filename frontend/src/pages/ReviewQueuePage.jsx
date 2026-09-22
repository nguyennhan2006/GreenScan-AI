import { useMemo, useState } from 'react'
import { Link } from '../lib/router.jsx'
import { PriorityBadge, StatusBadge, WorkflowPill } from '../components/badges.jsx'
import { formatDateTime } from '../lib/format.js'

/**
 * Human-review queue (mockup #9), keyed by the review store's state machine:
 * AI_SUGGESTED → HUMAN_REVIEWED → FINALIZED. The counts are the reviewer's
 * workload, not a score about the issuer.
 */

const TABS = [
  ['AI_SUGGESTED', 'Cần xem xét'],
  ['HUMAN_REVIEWED', 'Đã xem, chưa chốt'],
  ['FINALIZED', 'Đã chốt'],
]
const ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

export default function ReviewQueuePage({ runId, rows, reviewStates = {}, reviewHistory = {}, goldStats }) {
  const [tab, setTab] = useState('AI_SUGGESTED')
  const buckets = useMemo(() => {
    const b = { AI_SUGGESTED: [], HUMAN_REVIEWED: [], FINALIZED: [] }
    for (const r of rows) (b[reviewStates[r.id] || 'AI_SUGGESTED'] ||= []).push(r)
    for (const k of Object.keys(b)) {
      b[k].sort((x, y) => (ORDER[x.severity] ?? 9) - (ORDER[y.severity] ?? 9) || Number(y.requiresReview) - Number(x.requiresReview))
    }
    return b
  }, [rows, reviewStates])

  const list = buckets[tab] || []

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {TABS.map(([k, l]) => (
          <button
            key={k}
            type="button"
            onClick={() => setTab(k)}
            className={`rounded-full border px-3 py-1 text-xs font-medium ${tab === k ? 'border-[#0F3D2E] bg-[#0F3D2E] text-white' : 'border-slate-300 bg-white text-slate-700'}`}
          >
            {l} <span className="tabular-nums opacity-70">({buckets[k].length})</span>
          </button>
        ))}
        {goldStats && (
          <span className="ml-auto text-xs text-slate-500" title="Tỷ lệ quyết định người xem xét khác với AI — chỉ số về chất lượng AI">
            Ghi đè AI: <b className="font-mono">{Math.round((goldStats.ai_override_rate || 0) * 100)}%</b> · nhãn gold: <b className="font-mono">{goldStats.gold_records}</b>
          </span>
        )}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white">
        {list.length === 0 ? (
          <p className="p-6 text-center text-sm text-slate-500">Không còn tuyên bố nào ở trạng thái này.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs text-slate-500">
              <tr>
                <th className="px-3 py-2 font-medium">Tuyên bố</th>
                <th className="px-3 py-2 font-medium">Trạng thái AI</th>
                <th className="px-3 py-2 font-medium">Ưu tiên</th>
                <th className="px-3 py-2 font-medium">Vì sao cần xem</th>
                <th className="px-3 py-2 font-medium">Quyết định gần nhất</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((r) => {
                const last = (reviewHistory[r.id] || []).slice(-1)[0]
                const reasons = []
                if (r.contradicting.length) reasons.push(`${r.contradicting.length} đoạn mâu thuẫn`)
                if (r.missing.length) reasons.push(`thiếu ${r.missing.length} thuộc tính`)
                if (r.requiresLlmReview) reasons.push('lập trường do mô hình đề xuất')
                if (r.evidence.length === 0) reasons.push('chưa có bằng chứng')
                if (r.flagged) reasons.push('nghi tiêm lệnh')
                return (
                  <tr key={r.id} className="align-top">
                    <td className="max-w-md px-3 py-2.5">
                      <Link to={`/runs/${runId}/claims/${r.id}?tab=review`} className="line-clamp-2 font-medium text-slate-900 hover:underline">{r.claim.text}</Link>
                      <p className="text-[11px] text-slate-500">{r.claim.source_name}{r.claim.source_page ? ` · tr. ${r.claim.source_page}` : ''}</p>
                    </td>
                    <td className="px-3 py-2.5"><StatusBadge status={r.status} /></td>
                    <td className="px-3 py-2.5"><PriorityBadge severity={r.severity} /></td>
                    <td className="px-3 py-2.5 text-xs text-slate-600">{reasons.join(' · ') || '—'}</td>
                    <td className="px-3 py-2.5 text-xs text-slate-600">
                      {last ? (
                        <>
                          <WorkflowPill state={last.new_state} />
                          <span className="block text-[11px]">{last.decision}{last.reviewer_status ? ` → ${last.reviewer_status}` : ''} · {last.reviewer} · {formatDateTime(last.decided_at)}</span>
                        </>
                      ) : <WorkflowPill state="AI_SUGGESTED" />}
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <Link to={`/runs/${runId}/claims/${r.id}`} className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50">Mở</Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
