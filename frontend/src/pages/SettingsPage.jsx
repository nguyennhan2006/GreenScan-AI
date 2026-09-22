import { useEffect, useState } from 'react'
import { checkHealth, exportGold, gatewayHealth } from '../api.js'
import { Chip } from '../components/badges.jsx'

/**
 * Settings (mockup #12), limited to what actually exists: the reviewer name
 * kept on this browser, the model gateway (read-only, with a live ping), and
 * the gold-label statistics. Language, theme, retention and user management
 * have no backend and are not shown as toggles.
 */
export default function SettingsPage({ reviewer, onReviewerChange, onForget }) {
  const [name, setName] = useState(reviewer || '')
  const [gateway, setGateway] = useState(null)
  const [live, setLive] = useState(false)
  const [health, setHealth] = useState(null)
  const [gold, setGold] = useState(null)

  const loadGateway = (ping) => {
    setLive(ping)
    fetch(`${import.meta.env.VITE_API_URL || '/api'}/v1/gateway/health${ping ? '?live=true' : ''}`)
      .then((r) => r.json()).then(setGateway).catch(() => setGateway(null))
  }
  useEffect(() => {
    gatewayHealth().then(setGateway).catch(() => setGateway(null))
    checkHealth().then(setHealth).catch(() => setHealth(null))
    exportGold().then((g) => setGold(g.stats)).catch(() => setGold(null))
  }, [])

  const providers = Object.entries(gateway?.providers || {})

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Người xem xét</h3>
        <p className="text-xs text-slate-500">Tên được ghi vào mọi quyết định xét duyệt. Lưu trên trình duyệt này.</p>
        <form onSubmit={(e) => { e.preventDefault(); onReviewerChange(name.trim()) }} className="mt-3 flex gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
          <button type="submit" className="rounded-lg bg-[#0F3D2E] px-3 py-1.5 text-sm font-semibold text-white">Lưu</button>
          <button type="button" onClick={onForget} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700">Quên tên</button>
        </form>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="text-sm font-semibold text-slate-900">Mô hình AI (model gateway)</h3>
          <button type="button" onClick={() => loadGateway(true)} className="ml-auto rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700">Kiểm tra live</button>
        </div>
        <p className="text-xs text-slate-500">Cấu hình qua <code className="font-mono">.env</code> và <code className="font-mono">configs/routing.yaml</code> ở máy chủ; giao diện chỉ đọc. Không có key vẫn chạy bằng heuristic.</p>
        {gateway ? (
          <div className="mt-3 text-xs">
            <p>Provider mặc định: <b className="font-mono">{gateway.active_provider}</b> · thứ tự dự phòng: <span className="font-mono">{(gateway.fallback_order || []).join(' → ')}</span></p>
            <ul className="mt-2 grid gap-1 sm:grid-cols-2">
              {providers.map(([n, v]) => (
                <li key={n} className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-1.5">
                  <span className="font-mono">{n}{v?.model ? <span className="text-slate-400"> · {v.model}</span> : null}</span>
                  <span className="flex gap-1">
                    <Chip tone={v?.configured ? 'emerald' : 'slate'}>{v?.configured ? 'đã cấu hình' : 'chưa cấu hình'}</Chip>
                    {live && v?.configured && <Chip tone={v?.healthy ? 'emerald' : 'red'}>{v?.healthy ? 'live OK' : 'không phản hồi'}</Chip>}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : <p className="mt-2 text-xs text-slate-500">Không đọc được trạng thái gateway.</p>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Dữ liệu gold từ quyết định người xem xét</h3>
        {gold ? (
          <dl className="mt-2 grid gap-1 text-xs sm:grid-cols-2">
            <div className="flex justify-between"><dt className="text-slate-500">Tổng quyết định</dt><dd className="font-mono">{gold.total_decisions}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tuyên bố đã chạm</dt><dd className="font-mono">{gold.claims_touched}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Nhãn gold (CONFIRM/OVERRIDE)</dt><dd className="font-mono">{gold.gold_records}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tỷ lệ ghi đè AI</dt><dd className="font-mono">{Math.round((gold.ai_override_rate || 0) * 100)}%</dd></div>
            <div className="flex justify-between sm:col-span-2"><dt className="text-slate-500">Người xem xét</dt><dd className="font-mono">{(gold.reviewers || []).join(', ') || '—'}</dd></div>
          </dl>
        ) : <p className="mt-2 text-xs text-slate-500">Chưa có quyết định nào.</p>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 text-xs text-slate-600">
        <h3 className="text-sm font-semibold text-slate-900">Hệ thống</h3>
        <p className="mt-2">API phiên bản <span className="font-mono">{health?.version || '—'}</span> · rubric <span className="font-mono">risk-rubric-v2</span> · schema <span className="font-mono">analysis-result-v2</span></p>
        <p className="mt-1">Lưu trữ: <code className="font-mono">.quantum/runs</code> (phiên), <code className="font-mono">.quantum/documents</code> (tệp gốc), <code className="font-mono">.quantum/reviews</code> (quyết định). Không tự xoá.</p>
      </section>
    </div>
  )
}
