import { useEffect, useState } from 'react'
import { orgPacks } from '../api.js'

/**
 * Internal rules (org packs): rules an organisation writes for itself, below the
 * law. They add findings beside the verdict and never change it. The notice
 * says so on every screen that shows them (docs/03-architecture/ORG_PACK.md).
 */

export const ORG_NOTICE = 'Quy tắc nội bộ do tổ chức tự đặt, đứng dưới luật: không phải kết luận pháp lý; không đổi kết luận kiểm chứng.'

const OUTCOME = {
  VIOLATION: ['Không đạt', 'bg-red-50 text-red-800 ring-red-200'],
  NEEDS_REVIEW: ['Cần người xem', 'bg-amber-50 text-amber-900 ring-amber-200'],
  COMPLIANT: ['Đạt', 'bg-emerald-50 text-emerald-800 ring-emerald-200'],
  NOT_APPLICABLE: ['Không áp dụng', 'bg-slate-50 text-slate-500 ring-slate-200'],
}
const ORDER = { VIOLATION: 0, NEEDS_REVIEW: 1, COMPLIANT: 2, NOT_APPLICABLE: 3 }
const PACK_STATUS = {
  approved: ['Đã duyệt, đang áp dụng', 'bg-emerald-100 text-emerald-800'],
  draft: ['Bản nháp: được nạp, không áp dụng', 'bg-amber-100 text-amber-900'],
  rejected: ['Bị từ chối khi nạp: không áp dụng', 'bg-red-100 text-red-800'],
}

export function OrgFindings({ findings }) {
  if (findings == null) {
    return <p className="text-xs text-slate-500">Phiên này chạy khi chưa bật quy tắc nội bộ. Khai báo bộ quy tắc ở trang Thư viện pháp lý rồi phân tích lại.</p>
  }
  const shown = [...findings].sort((a, b) => (ORDER[a.outcome] ?? 9) - (ORDER[b.outcome] ?? 9))
  const applied = shown.filter((f) => f.outcome !== 'NOT_APPLICABLE')
  return (
    <div className="space-y-2">
      <p className="rounded-lg bg-slate-50 px-3 py-2 text-[11px] text-slate-600">{ORG_NOTICE}</p>
      {applied.length === 0 && <p className="text-xs text-slate-500">Không quy tắc nội bộ nào áp dụng cho tuyên bố này ({shown.length} quy tắc đã xét).</p>}
      <ul className="space-y-2">
        {applied.map((f) => {
          const [label, cls] = OUTCOME[f.outcome] || [f.outcome, 'bg-slate-50 text-slate-600 ring-slate-200']
          return (
            <li key={`${f.org_id}-${f.rule_id}`} className="rounded-lg border border-slate-200 p-2.5 text-xs">
              <p className="flex flex-wrap items-center gap-2">
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ${cls}`}>{label}</span>
                <span className="font-semibold text-slate-900">{f.title}</span>
              </p>
              {f.reason && <p className="mt-1 text-slate-700">{f.reason}</p>}
              <p className="mt-1 font-mono text-[10px] text-slate-400">{f.org_id} · {f.rule_id} · {f.source_document}{f.source_clauses?.length ? ` ${f.source_clauses.join(', ')}` : ''}</p>
            </li>
          )
        })}
      </ul>
      {shown.length > applied.length && <p className="text-[11px] text-slate-400">{shown.length - applied.length} quy tắc khác không áp dụng cho tuyên bố này.</p>}
    </div>
  )
}

export function OrgPackLibrary() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  useEffect(() => { orgPacks().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <p className="text-xs text-red-700">Không đọc được quy tắc nội bộ: {error}</p>
  if (!data) return <p className="text-xs text-slate-500">Đang đọc quy tắc nội bộ…</p>
  return (
    <div id="org-packs" className="rounded-xl border border-slate-200 bg-white">
      <div className="flex flex-wrap items-baseline gap-2 border-b border-slate-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-900">Quy tắc nội bộ của tổ chức</h3>
        <span className="text-xs text-slate-500">{data.enabled ? `${data.packs.length} bộ đã khai báo` : 'chưa bật'}</span>
      </div>
      <div className="space-y-3 px-4 py-3 text-xs">
        <p className="text-[11px] text-slate-600">{ORG_NOTICE}</p>
        {!data.enabled && (
          <ol className="list-decimal space-y-1 pl-5 text-slate-700">
            <li>Chép thư mục mẫu <code className="font-mono">configs/org_packs/_template</code>, điền <code className="font-mono">pack.yaml</code> (quy tắc) và <code className="font-mono">internal_policy.md</code> (văn bản nội bộ).</li>
            <li>Kiểm cấu trúc: <code className="font-mono">quantum-agent org-validate &lt;thư mục&gt;</code>; thử trên một câu: <code className="font-mono">org-preview</code>.</li>
            <li>Bật: đặt <code className="font-mono">QUANTUM_ORG_PACKS=&lt;thư mục&gt;</code> rồi phân tích lại.</li>
          </ol>
        )}
        {data.packs.map((p, i) => {
          const [label, cls] = PACK_STATUS[p.status] || [p.status, 'bg-slate-100 text-slate-700']
          return (
            <div key={p.org_id || p.path || i} className="rounded-lg border border-slate-200 p-3">
              <p className="flex flex-wrap items-center gap-2">
                <span className="font-semibold text-slate-900">{p.org_name || p.org_id || p.path}</span>
                {p.pack_version && <span className="font-mono text-[11px] text-slate-500">{p.pack_version}</span>}
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${cls}`}>{label}</span>
              </p>
              {p.errors?.length > 0 && <ul className="mt-1 list-disc pl-5 text-red-700">{p.errors.map((e, j) => <li key={j}>{e}</li>)}</ul>}
              {p.rules?.length > 0 && (
                <ul className="mt-2 divide-y divide-slate-100">
                  {p.rules.map((r) => (
                    <li key={r.rule_id} className="flex flex-wrap gap-2 py-1.5">
                      <span className="font-mono text-[11px] text-slate-500">{r.rule_id}</span>
                      <span className="text-slate-800">{r.title}</span>
                      <span className="ml-auto text-[11px] text-slate-500">{r.source_clauses?.join(', ')}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
