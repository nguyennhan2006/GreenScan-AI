import { useEffect, useState } from 'react'
import { listRuns, setRunLabel } from '../api.js'
import { ReleasePill, STATUS_BAR, STATUS_LABELS, STATUS_ORDER } from '../components/badges.jsx'
import { Link } from '../lib/router.jsx'
import { formatDateTime, shortId } from '../lib/format.js'

/**
 * Saved runs (mockup #11). Every run the pipeline completed is on disk, so
 * this is also the demo insurance: open a prepared run instead of parsing a
 * report live.
 */

function MiniBar({ counts, total }) {
  if (!total) return <span className="text-xs text-slate-400">—</span>
  return (
    <span className="flex h-2 w-28 overflow-hidden rounded-full bg-slate-100" title={STATUS_ORDER.map((s) => `${STATUS_LABELS[s]}: ${counts[s] || 0}`).join(' · ')}>
      {STATUS_ORDER.map((s) => (counts[s] ? <span key={s} className={STATUS_BAR[s]} style={{ width: `${(counts[s] / total) * 100}%` }} /> : null))}
    </span>
  )
}

export default function HistoryPage({ currentRunId, onLabelChanged }) {
  const [runs, setRuns] = useState(null)
  const [error, setError] = useState(null)
  const [editing, setEditing] = useState(null)
  const [draft, setDraft] = useState('')

  const reload = () => listRuns(100).then((d) => setRuns(d.runs)).catch((e) => setError(e.message))
  useEffect(() => { reload() }, [])

  const save = async (runId) => {
    try {
      const r = await setRunLabel(runId, draft)
      setRuns((prev) => prev.map((x) => (x.run_id === runId ? { ...x, label: r.label } : x)))
      onLabelChanged?.(runId, r.label)
    } catch (e) {
      setError(e.message)
    }
    setEditing(null)
  }

  if (error) return <p className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800">{error}</p>
  if (!runs) return <p className="text-sm text-slate-500">Đang tải…</p>

  return (
    <div className="space-y-3">
      <p className="text-xs text-slate-500">{runs.length} phiên gần nhất trong <code className="font-mono">.quantum/runs</code>. Bấm tên để đổi nhãn; mở lại phiên không chạy lại pipeline.</p>
      <div className="rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs text-slate-500">
            <tr>
              <th className="px-3 py-2 font-medium">Phiên</th>
              <th className="px-3 py-2 font-medium">Tài liệu</th>
              <th className="px-3 py-2 font-medium">Tuyên bố</th>
              <th className="px-3 py-2 font-medium">Phân bố</th>
              <th className="px-3 py-2 font-medium">Trạng thái</th>
              <th className="px-3 py-2 font-medium">Tạo lúc</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {runs.map((r) => (
              <tr key={r.run_id} className={r.run_id === currentRunId ? 'bg-emerald-50/50' : ''}>
                <td className="px-3 py-2.5">
                  {editing === r.run_id ? (
                    <form onSubmit={(e) => { e.preventDefault(); save(r.run_id) }} className="flex gap-1">
                      <input autoFocus value={draft} onChange={(e) => setDraft(e.target.value)} className="rounded border border-slate-300 px-2 py-0.5 text-xs" />
                      <button type="submit" className="rounded bg-[#0F3D2E] px-2 text-xs text-white">Lưu</button>
                    </form>
                  ) : (
                    <button type="button" onClick={() => { setEditing(r.run_id); setDraft(r.label || '') }} className="text-left font-medium text-slate-900 hover:underline">
                      {r.label || <span className="text-slate-400">Chưa đặt tên</span>}
                    </button>
                  )}
                  <p className="font-mono text-[11px] text-slate-500">{shortId(r.run_id, 16)}{r.run_id === currentRunId ? ' · đang mở' : ''}</p>
                </td>
                <td className="px-3 py-2.5 text-xs text-slate-700" title={r.documents.join('\n')}>{r.total_documents} <span className="text-slate-400">({r.documents.slice(0, 2).join(', ')}{r.documents.length > 2 ? '…' : ''})</span></td>
                <td className="px-3 py-2.5 font-mono text-xs">{r.total_claims}</td>
                <td className="px-3 py-2.5"><MiniBar counts={r.status_counts} total={r.total_claims} /></td>
                <td className="px-3 py-2.5"><ReleasePill status={r.release_status} /></td>
                <td className="px-3 py-2.5 text-xs text-slate-600">{formatDateTime(r.created_at)}</td>
                <td className="px-3 py-2.5 text-right">
                  <Link to={`/runs/${r.run_id}`} className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50">Mở</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
