import { Link } from '../lib/router.jsx'
import { shortId } from '../lib/format.js'

/**
 * App shell: dark-green sidebar (mockup v2 direction), light content area.
 *
 * Items that need a loaded run are disabled rather than hidden, so the map of
 * the product stays visible while the person is still on the intake step.
 */

const NAV = [
  { key: 'new', label: 'Phân tích mới', to: '/new', icon: '＋' },
  { key: 'overview', label: 'Tổng quan', to: (id) => `/runs/${id}`, icon: '◫', needsRun: true },
  { key: 'claims', label: 'Danh sách tuyên bố', to: (id) => `/runs/${id}/claims`, icon: '≡', needsRun: true },
  { key: 'review', label: 'Xét duyệt', to: (id) => `/runs/${id}/review`, icon: '✓', needsRun: true },
  { key: 'export', label: 'Xuất hồ sơ', to: (id) => `/runs/${id}/export`, icon: '⤓', needsRun: true },
  { key: 'runs', label: 'Lịch sử phân tích', to: '/runs', icon: '◷' },
  { key: 'legal', label: 'Thư viện pháp lý', to: '/legal', icon: '§' },
  { key: 'settings', label: 'Cài đặt', to: '/settings', icon: '⚙' },
]

function Leaf({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M20 4c-8 0-14 4-14 12 0 1.5.3 2.8.8 4C9.5 15 13 11 18 9c-4 3-7 7-8.5 11.5C10.3 20.8 11.1 21 12 21c8 0 10-8 8-17z" fill="currentColor" />
    </svg>
  )
}

function Dot({ state, children }) {
  const tone = state === 'ok' ? 'bg-emerald-100 text-emerald-800'
    : state === 'bad' ? 'bg-red-100 text-red-800'
      : 'bg-slate-100 text-slate-600'
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${tone}`}>{children}</span>
}

export default function Shell({
  active, runId, runLabel, reviewer, apiStatus, modelLabel, modelState, title, subtitle, badges = {}, children,
}) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="hidden w-60 shrink-0 flex-col bg-[#0F3D2E] text-emerald-50 md:flex">
        <Link to="/new" className="flex items-center gap-2 px-5 py-5">
          <Leaf className="h-7 w-7 text-emerald-300" />
          <span className="text-lg font-bold tracking-tight text-white">GreenScan</span>
        </Link>
        <nav className="flex-1 space-y-0.5 px-3">
          {NAV.map((item) => {
            const disabled = item.needsRun && !runId
            const to = typeof item.to === 'function' ? item.to(runId) : item.to
            const isActive = active === item.key
            const cls = `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition ${
              isActive ? 'bg-emerald-500/25 font-semibold text-white'
                : disabled ? 'cursor-not-allowed text-emerald-50/35'
                  : 'text-emerald-50/85 hover:bg-white/10 hover:text-white'
            }`
            const body = (
              <>
                <span className="w-4 text-center text-base leading-none opacity-80">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {badges[item.key] > 0 && (
                  <span className="rounded-full bg-amber-400 px-1.5 text-[11px] font-bold text-slate-900 tabular-nums">
                    {badges[item.key]}
                  </span>
                )}
              </>
            )
            return disabled
              ? <span key={item.key} className={cls} title="Cần một phiên phân tích đang mở">{body}</span>
              : <Link key={item.key} to={to} className={cls}>{body}</Link>
          })}
        </nav>
        <div className="border-t border-white/10 px-5 py-4 text-xs text-emerald-50/70">
          {runId ? (
            <>
              <p className="truncate font-medium text-white" title={runLabel || runId}>{runLabel || 'Phiên chưa đặt tên'}</p>
              <p className="font-mono">run {shortId(runId)}</p>
            </>
          ) : (
            <p>Chưa mở phiên phân tích nào.</p>
          )}
          <p className="mt-2 flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-300 text-[11px] font-bold text-[#0F3D2E]">
              {(reviewer || '?').slice(0, 2).toUpperCase()}
            </span>
            <span className="truncate">{reviewer || 'Chưa có người xem xét'}</span>
          </p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-3">
            <div className="min-w-0">
              <h1 className="truncate text-lg font-bold text-slate-900">{title}</h1>
              {subtitle && <p className="truncate text-xs text-slate-500">{subtitle}</p>}
            </div>
            <div className="flex items-center gap-2">
              <Dot state={modelState}>● {modelLabel}</Dot>
              <Dot state={apiStatus === 'online' ? 'ok' : apiStatus === 'offline' ? 'bad' : 'idle'}>
                {apiStatus === 'online' ? '● API sẵn sàng' : apiStatus === 'offline' ? '● API ngoại tuyến' : '● Đang kiểm tra'}
              </Dot>
            </div>
          </div>
          {/* Mobile nav: the sidebar collapses into a scrollable row. */}
          <nav className="flex gap-1 overflow-x-auto px-4 pb-2 md:hidden">
            {NAV.map((item) => {
              const disabled = item.needsRun && !runId
              const to = typeof item.to === 'function' ? item.to(runId) : item.to
              return disabled ? null : (
                <Link
                  key={item.key}
                  to={to}
                  className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${active === item.key ? 'bg-[#0F3D2E] text-white' : 'bg-slate-100 text-slate-700'}`}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </header>

        <main className="flex-1 px-6 py-5">{children}</main>

        <footer className="px-6 pb-6 pt-2">
          <p className="max-w-4xl text-xs leading-relaxed text-slate-500">
            Hệ thống ước lượng mức độ đầy đủ của bằng chứng cho từng tuyên bố. Kết quả không phải kết
            luận pháp lý về hành vi của doanh nghiệp, không thay thế kiểm toán viên hay cơ quan quản lý,
            và thiếu bằng chứng không đồng nghĩa vi phạm.
          </p>
        </footer>
      </div>
    </div>
  )
}

export { Leaf }
