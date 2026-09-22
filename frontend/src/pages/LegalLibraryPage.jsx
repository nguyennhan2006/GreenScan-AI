import { useEffect, useMemo, useState } from 'react'
import { legalCorpus } from '../api.js'
import { Chip } from '../components/badges.jsx'
import { formatDate } from '../lib/format.js'

/**
 * Legal library (mockup #8): the registered instruments as the legal layer
 * sees them. The important column is not "in force" but "text usable" — an
 * instrument the layer cannot quote is reported as a coverage gap in every
 * finding it would govern.
 */

const DOC_TYPE = {
  luat: 'Luật', nghi_dinh: 'Nghị định', quyet_dinh: 'Quyết định', thong_tu: 'Thông tư', nghi_quyet: 'Nghị quyết',
}

export default function LegalLibraryPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')
  const [issue, setIssue] = useState('all')

  useEffect(() => {
    legalCorpus().then(setData).catch((e) => setError(e.message))
  }, [])

  const issues = useMemo(() => {
    const set = new Set()
    for (const d of data?.documents || []) for (const i of d.legal_issues || []) set.add(i)
    return [...set].sort()
  }, [data])

  const docs = useMemo(() => {
    let list = data?.documents || []
    if (issue !== 'all') list = list.filter((d) => (d.legal_issues || []).includes(issue))
    if (q.trim()) {
      const n = q.trim().toLowerCase()
      list = list.filter((d) => d.document_number.toLowerCase().includes(n) || d.title.toLowerCase().includes(n))
    }
    return list
  }, [data, issue, q])

  if (error) return <p className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800">Không tải được thư viện pháp lý: {error}</p>
  if (!data) return <p className="text-sm text-slate-500">Đang tải…</p>

  const usable = data.documents.filter((d) => d.usable).length

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
        <span>{data.documents.length} văn bản đăng ký · <b>{usable}</b> đã trích được toàn văn</span>
        <span>· lớp pháp lý: {data.enabled ? 'bật' : 'tắt'} · chế độ <code className="font-mono">{data.check_mode}</code></span>
        <span className="ml-auto font-mono text-[11px] text-slate-400">{data.registry_file}</span>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 p-3">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm số hiệu hoặc tên văn bản…" className="min-w-64 flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
          <select value={issue} onChange={(e) => setIssue(e.target.value)} className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm">
            <option value="all">Tất cả vấn đề pháp lý</option>
            {issues.map((i) => <option key={i} value={i}>{i}</option>)}
          </select>
        </div>
        <ul className="divide-y divide-slate-100">
          {docs.map((d) => (
            <li key={d.id} className="flex flex-wrap items-start gap-3 px-4 py-3">
              <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${d.usable ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'}`}>
                {DOC_TYPE[d.doc_type]?.[0] || '§'}
              </span>
              <div className="min-w-0 flex-1">
                <p className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm font-semibold text-slate-900">{d.document_number}</span>
                  <span className="text-xs text-slate-500">{DOC_TYPE[d.doc_type] || d.doc_type} · {d.authority}</span>
                </p>
                <p className="text-sm text-slate-800">{d.title}</p>
                <p className="mt-1 flex flex-wrap gap-1.5">
                  {(d.legal_issues || []).map((i) => <Chip key={i}>{i}</Chip>)}
                  {(d.relations?.amends || []).length > 0 && <Chip tone="amber">sửa đổi {d.relations.amends.join(', ')}</Chip>}
                </p>
                {!d.usable && d.text_acquisition_note && <p className="mt-1 text-[11px] text-slate-500">{d.text_acquisition_note}</p>}
              </div>
              <div className="text-right text-xs">
                <p className="text-slate-500">Hiệu lực <span className="font-mono text-slate-800">{formatDate(d.effective_from)}</span>{d.effective_to ? ` → ${formatDate(d.effective_to)}` : ''}</p>
                <p className="mt-1 flex justify-end gap-1.5">
                  <Chip tone={d.status === 'effective' ? 'emerald' : 'slate'}>{d.status === 'effective' ? 'Đang hiệu lực' : d.status}</Chip>
                  <Chip tone={d.usable ? (d.text_is_ocr ? 'amber' : 'emerald') : 'slate'}>{d.usable ? (d.text_is_ocr ? 'toàn văn (OCR)' : 'toàn văn') : 'chưa trích được'}</Chip>
                </p>
                {d.url && <a href={d.url} target="_blank" rel="noreferrer" className="mt-1 inline-block text-emerald-800 hover:underline">Nguồn ↗</a>}
              </div>
            </li>
          ))}
        </ul>
      </div>
      <p className="text-[11px] text-slate-500">Thư viện chỉ liệt kê văn bản và trạng thái trích xuất; việc “văn bản nào áp dụng cho tuyên bố nào” nằm ở panel Bối cảnh pháp lý của từng tuyên bố, chọn theo ngày hiệu lực.</p>
    </div>
  )
}
