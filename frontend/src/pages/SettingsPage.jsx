import { useEffect, useState } from 'react'
import { checkHealth, exportGold, gatewayHealth, runtimeInfo } from '../api.js'
import { Chip } from '../components/badges.jsx'

/**
 * Settings, limited to what actually exists: the reviewer name kept on this
 * browser, what engine serves each task on this installation (and how to
 * change it), the model providers for whoever maintains the server, and the
 * gold-label statistics. Language, theme, retention and user management have
 * no backend and are not shown as toggles.
 */

const ENGINE = {
  rules: ['Luật tất định', 'emerald'],
  deterministic: ['Phép tính bằng mã', 'emerald'],
  lite: ['Từ khoá + n-gram (CPU)', 'emerald'],
  llm: ['Mô hình ngôn ngữ', 'sky'],
  fpt: ['Vector qua FPT', 'sky'],
  local: ['Vector trên máy', 'violet'],
  http: ['Dịch vụ nội bộ', 'violet'],
}

const PROFILES = [
  ['offline', 'Ngoại tuyến', 'Mọi laptop, không cần khoá API, tài liệu không rời máy. Đo 05/10: báo cáo HPG ~2 phút, RAM đỉnh 1,3 GB.'],
  ['cloud', 'Laptop + AI đám mây', 'Thêm khoá FPT AI Marketplace: mô hình chỉ đọc các cặp luật không quyết được; có bộ nhớ đệm nên chạy lại không tốn thêm.'],
  ['gpu', 'Máy chủ có GPU', 'Mô hình mở chạy bằng vLLM trên máy chủ của đơn vị; dùng cho tài liệu mật.'],
]

export default function SettingsPage({ reviewer, onReviewerChange, onForget }) {
  const [name, setName] = useState(reviewer || '')
  const [runtime, setRuntime] = useState(null)
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
    runtimeInfo().then(setRuntime).catch(() => setRuntime(null))
    gatewayHealth().then(setGateway).catch(() => setGateway(null))
    checkHealth().then(setHealth).catch(() => setHealth(null))
    exportGold().then((g) => setGold(g.stats)).catch(() => setGold(null))
  }, [])

  const providers = Object.entries(gateway?.providers || {})

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Người soát xét</h3>
        <p className="text-xs text-slate-500">Tên được ghi vào mọi quyết định và lên giấy làm việc. Lưu trên trình duyệt này.</p>
        <form onSubmit={(e) => { e.preventDefault(); onReviewerChange(name.trim()) }} className="mt-3 flex gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
          <button type="submit" className="rounded-lg bg-[#0F3D2E] px-3 py-1.5 text-sm font-semibold text-white">Lưu</button>
          <button type="button" onClick={onForget} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700">Quên tên</button>
        </form>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="text-sm font-semibold text-slate-900">Chế độ chạy của máy chủ này</h3>
          {runtime && <Chip tone={runtime.sends_documents_out ? 'sky' : 'emerald'}>{runtime.label}</Chip>}
        </div>
        {runtime ? (
          <>
            <table className="mt-3 w-full text-xs">
              <thead className="text-left text-slate-500"><tr><th className="pb-1 font-medium">Việc</th><th className="pb-1 font-medium">Ai làm</th><th className="pb-1 font-medium">Chi tiết</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {runtime.tasks.map((t) => {
                  const [label, tone] = ENGINE[t.engine] || [t.engine, 'slate']
                  return (
                    <tr key={t.task} className="align-top">
                      <td className="py-2 pr-3 font-medium text-slate-800">{t.label}</td>
                      <td className="py-2 pr-3"><Chip tone={tone}>{label}</Chip></td>
                      <td className="py-2 text-slate-600">{t.detail}</td>
                    </tr>
                  )
                })}
                <tr className="align-top">
                  <td className="py-2 pr-3 font-medium text-slate-800">Đọc trang scan (OCR)</td>
                  <td className="py-2 pr-3"><Chip tone={runtime.ocr?.available ? 'emerald' : 'amber'}>{runtime.ocr?.available ? 'Tesseract' : 'chưa cài'}</Chip></td>
                  <td className="py-2 text-slate-600">{runtime.ocr?.available ? `Ngôn ngữ ${runtime.ocr.languages}.` : 'Trang không có lớp chữ sẽ không đọc được; PDF có lớp chữ vẫn chạy bình thường.'}</td>
                </tr>
              </tbody>
            </table>
            <p className="mt-2 text-[11px] text-slate-500">
              Máy chủ: {runtime.hardware?.cpu_count ?? '?'} luồng CPU{runtime.hardware?.ram_gb ? ` · ${runtime.hardware.ram_gb} GB RAM` : ''} · hồ sơ <code className="font-mono">{runtime.profile}</code>
            </p>
          </>
        ) : <p className="mt-2 text-xs text-slate-500">Không đọc được chế độ chạy.</p>}

        <h4 className="mt-4 text-xs font-semibold text-slate-700">Đổi chế độ</h4>
        <p className="text-xs text-slate-500">Đặt một dòng trong tệp <code className="font-mono">.env</code> ở thư mục GreenScan rồi khởi động lại: <code className="font-mono">QUANTUM_PROFILE=offline</code> (hoặc <code className="font-mono">cloud</code>, <code className="font-mono">gpu</code>).</p>
        <ul className="mt-2 grid gap-2 sm:grid-cols-3">
          {PROFILES.map(([key, label, hint]) => (
            <li key={key} className={`rounded-lg border p-3 text-xs ${runtime?.profile === key ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200'}`}>
              <p className="font-semibold text-slate-900">{label} <code className="font-mono font-normal text-slate-500">{key}</code></p>
              <p className="mt-1 text-slate-600">{hint}</p>
            </li>
          ))}
        </ul>
      </section>

      <details className="rounded-xl border border-slate-200 bg-white p-5">
        <summary className="cursor-pointer text-sm font-semibold text-slate-900">Nhà cung cấp mô hình (cho người quản trị)</summary>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <p className="text-xs text-slate-500">Cấu hình qua <code className="font-mono">.env</code> và <code className="font-mono">configs/routing.yaml</code>; giao diện chỉ đọc.</p>
          <button type="button" onClick={() => loadGateway(true)} className="ml-auto rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700">Kiểm tra kết nối</button>
        </div>
        {gateway ? (
          <div className="mt-3 text-xs">
            <p>Mặc định: <b className="font-mono">{gateway.active_provider}</b> · dự phòng: <span className="font-mono">{(gateway.fallback_order || []).join(' → ')}</span></p>
            <ul className="mt-2 grid gap-1 sm:grid-cols-2">
              {providers.map(([n, v]) => (
                <li key={n} className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-1.5">
                  <span className="font-mono">{n}{v?.model ? <span className="text-slate-400"> · {v.model}</span> : null}</span>
                  <span className="flex gap-1">
                    <Chip tone={v?.configured ? 'emerald' : 'slate'}>{v?.configured ? 'đã cấu hình' : 'chưa cấu hình'}</Chip>
                    {live && v?.configured && <Chip tone={v?.healthy ? 'emerald' : 'red'}>{v?.healthy ? 'kết nối được' : 'không phản hồi'}</Chip>}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : <p className="mt-2 text-xs text-slate-500">Không đọc được trạng thái.</p>}
      </details>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Dữ liệu gold từ quyết định người soát xét</h3>
        {gold ? (
          <dl className="mt-2 grid gap-1 text-xs sm:grid-cols-2">
            <div className="flex justify-between"><dt className="text-slate-500">Tổng quyết định</dt><dd className="font-mono">{gold.total_decisions}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tuyên bố đã chạm</dt><dd className="font-mono">{gold.claims_touched}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Nhãn gold (xác nhận/sửa)</dt><dd className="font-mono">{gold.gold_records}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tỷ lệ người sửa kết quả AI</dt><dd className="font-mono">{Math.round((gold.ai_override_rate || 0) * 100)}%</dd></div>
            <div className="flex justify-between sm:col-span-2"><dt className="text-slate-500">Người soát xét</dt><dd className="font-mono">{(gold.reviewers || []).join(', ') || '—'}</dd></div>
          </dl>
        ) : <p className="mt-2 text-xs text-slate-500">Chưa có quyết định nào.</p>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 text-xs text-slate-600">
        <h3 className="text-sm font-semibold text-slate-900">Hệ thống</h3>
        <p className="mt-2">Phiên bản API <span className="font-mono">{health?.version || '—'}</span> · rubric <span className="font-mono">risk-rubric-v2</span> · schema <span className="font-mono">analysis-result-v2</span></p>
        <p className="mt-1">Lưu trữ: <code className="font-mono">.quantum/runs</code> (phiên), <code className="font-mono">.quantum/documents</code> (tệp gốc), <code className="font-mono">.quantum/reviews</code> (quyết định). Không tự xoá.</p>
      </section>
    </div>
  )
}
