import { useEffect, useState } from 'react'
import { listRuns, setRunLabel } from '../api.js'
import { ReleasePill, STATUS_BAR, STATUS_LABELS, STATUS_ORDER } from '../components/badges.jsx'
import { Link } from '../lib/router.jsx'
import NextStep from '../components/NextStep.jsx'
import { STATIC } from '../staticApi.js'
import { suggestRun } from '../lib/flow.js'
import { formatDateTime, shortId } from '../lib/format.js'

const NL = String.fromCharCode(10)   // tooltip: one document per line

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

  // Newest first, so the main Hòa Phát session leads the list whatever order the store returns.
  const reload = () => listRuns(100)
    .then((d) => setRuns([...(d.runs || [])].sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))))
    .catch((e) => setError(e.message))
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

  // The entry of the web demo, and where a finished session sends the reviewer: suggest a session
  // that is not the one open now, so the chain never loops back into the session just finished.
  const suggested = suggestRun(runs, currentRunId)

  return (
    <div className="space-y-3">
      {suggested && (
        <NextStep step={1} done action={{ label: `Mở ${suggested.name} →`, to: `/runs/${suggested.run.run_id}` }}>
          {currentRunId
            ? <>Muốn xem thêm: mở <b>{suggested.name}</b>. Các phiên dưới đây đã phân tích xong, mở lại không phải chạy lại.</>
            : (STATIC
              ? <>Bản xem trên web: bước 1 (tải và phân tích tài liệu) đã làm sẵn bằng hệ thống thật. Mở <b>{suggested.name}</b> để soát từ bước 2; quyết định của bạn chỉ lưu trong trình duyệt này.</>
              : <>Các phiên dưới đây đã phân tích xong. Mở <b>{suggested.name}</b> để soát từ bước 2, không phải chạy lại.</>)}
        </NextStep>
      )}
      <p className="text-xs text-slate-500">{runs.length} phiên đã phân tích. Bấm tên phiên để đổi nhãn; mở lại một phiên không chạy lại phân tích.</p>
      <div className="rounded-2xl border border-slate-200/70 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="whitespace-nowrap bg-slate-50 text-left text-xs text-slate-500">
            <tr>
              <th className="px-3 py-2 font-medium">Phiên</th>
              <th className="hidden px-3 py-2 font-medium md:table-cell">Tài liệu</th>
              <th className="px-3 py-2 font-medium">Tuyên bố</th>
              <th className="hidden px-3 py-2 font-medium sm:table-cell">Phân bố</th>
              <th className="hidden px-3 py-2 font-medium md:table-cell">Trạng thái</th>
              <th className="hidden px-3 py-2 font-medium md:table-cell">Tạo lúc</th>
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
                      <button type="submit" className="rounded bg-[#047857] px-2 text-xs text-white">Lưu</button>
                    </form>
                  ) : (
                    <button type="button" onClick={() => { setEditing(r.run_id); setDraft(r.label || '') }} className="text-left font-medium text-slate-900 hover:underline">
                      {r.label || <span className="text-slate-400">Chưa đặt tên</span>}
                    </button>
                  )}
                  <p className="font-mono text-xs text-slate-500">{shortId(r.run_id, 16)}{r.run_id === currentRunId ? ' · đang mở' : ''}</p>
                </td>
                <td className="hidden px-3 py-2.5 text-xs text-slate-700 md:table-cell" title={r.documents.join(NL)}>{r.total_documents} tệp <span className="hidden text-slate-400 2xl:inline">({r.documents.slice(0, 2).join(', ')}{r.documents.length > 2 ? '…' : ''})</span></td>
                <td className="px-3 py-2.5 font-mono text-xs">{r.total_claims}</td>
                <td className="hidden px-3 py-2.5 sm:table-cell"><MiniBar counts={r.status_counts} total={r.total_claims} /></td>
                <td className="hidden px-3 py-2.5 md:table-cell"><ReleasePill status={r.release_status} /></td>
                <td className="hidden px-3 py-2.5 text-xs text-slate-600 md:table-cell">{formatDateTime(r.created_at)}</td>
                <td className="px-3 py-2.5 text-right">
                  <Link to={`/runs/${r.run_id}`} className="whitespace-nowrap rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100">Mở →</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
