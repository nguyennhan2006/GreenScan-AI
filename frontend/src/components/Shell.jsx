import { Link } from '../lib/router.jsx'
import { shortId } from '../lib/format.js'
import { Icon } from './icons.jsx'

/**
 * App shell: dark-green sidebar, light content area.
 *
 * The sidebar is the process, not a menu: three numbered steps in the order
 * the work is done (documents → queue → working paper), then the screens one
 * visits occasionally. Steps that need a loaded run are shown disabled rather
 * than hidden, so the whole process stays visible from the first screen.
 */

const FLOW = [
  { key: 'new', step: 1, label: 'Tải tài liệu', to: '/new' },
  { key: 'queue', step: 2, label: 'Soát theo hàng đợi', to: (id) => `/runs/${id}`, needsRun: true },
  { key: 'studio', step: 3, label: 'Sửa báo cáo (Studio)', to: (id) => `/runs/${id}/studio`, needsRun: true },
  { key: 'export', step: 4, label: 'Giấy làm việc', to: (id) => `/runs/${id}/export`, needsRun: true },
]
const MORE = [
  { key: 'claims', label: 'Tất cả tuyên bố', to: (id) => `/runs/${id}/claims`, icon: 'list', needsRun: true },
  { key: 'runs', label: 'Lịch sử phân tích', to: '/runs', icon: 'clock' },
  { key: 'legal', label: 'Thư viện pháp lý', to: '/legal', icon: 'scale' },
  { key: 'settings', label: 'Cài đặt & chế độ chạy', to: '/settings', icon: 'settings' },
]

function Leaf({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M20 4c-8 0-14 4-14 12 0 1.5.3 2.8.8 4C9.5 15 13 11 18 9c-4 3-7 7-8.5 11.5C10.3 20.8 11.1 21 12 21c8 0 10-8 8-17z" fill="currentColor" />
    </svg>
  )
}

function Dot({ state, children, title }) {
  const tone = state === 'ok' ? 'bg-emerald-50 text-emerald-800 ring-emerald-200'
    : state === 'cloud' ? 'bg-sky-50 text-sky-800 ring-sky-200'
      : state === 'bad' ? 'bg-red-50 text-red-800 ring-red-200'
        : 'bg-slate-100 text-slate-600 ring-slate-200'
  return <span title={title} className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ring-1 ${tone}`}>{children}</span>
}

function NavItem({ item, runId, active, badge }) {
  const disabled = item.needsRun && !runId
  const to = typeof item.to === 'function' ? item.to(runId) : item.to
  const isActive = active === item.key
  const cls = `flex items-center gap-3 rounded-lg px-3 py-2.5 text-[14.5px] transition ${
    isActive ? 'bg-emerald-500/30 font-semibold text-white shadow-[inset_0_0_0_1px_rgba(110,231,183,.15)]'
      : disabled ? 'cursor-not-allowed text-emerald-50/35'
        : 'text-emerald-50/85 hover:bg-white/10 hover:text-white'
  }`
  const marker = item.step
    ? <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${isActive ? 'bg-emerald-300 text-[#0F3D2E]' : 'bg-white/15 text-white'}`}>{item.step}</span>
    : <span className="flex w-6 justify-center opacity-85"><Icon name={item.icon} className="h-[18px] w-[18px]" /></span>
  const body = (
    <>
      {marker}
      <span className="flex-1">{item.label}</span>
      {badge > 0 && (
        <span className="min-w-5 rounded-full bg-amber-400 px-1.5 text-center text-[11px] font-bold leading-5 tabular-nums text-slate-900" title="Mục trong hàng đợi chưa chốt">
          {badge}
        </span>
      )}
    </>
  )
  return disabled
    ? <span className={cls} title="Cần một phiên phân tích đang mở">{body}</span>
    : <Link to={to} className={cls}>{body}</Link>
}

export default function Shell({
  active, runId, runLabel, reviewer, apiStatus, runtime, title, subtitle, badges = {}, children,
}) {
  const runtimeTitle = (runtime?.tasks || []).map((t) => `${t.label}: ${t.detail}`).join('\n')
  return (
    <div className="flex min-h-screen bg-[var(--color-canvas)]">
      <aside className="sticky top-0 hidden h-screen w-[264px] shrink-0 flex-col bg-[#0F3D2E] bg-[radial-gradient(120%_60%_at_0%_0%,rgba(52,211,153,.10),transparent_60%)] text-emerald-50 md:flex">
        <Link to="/new" className="flex items-center gap-2.5 px-6 pb-6 pt-6">
          <Leaf className="h-8 w-8 text-emerald-300" />
          <span className="text-xl font-bold tracking-tight text-white">GreenScan</span>
        </Link>
        <nav className="flex-1 space-y-1 overflow-y-auto px-3.5" aria-label="Quy trình">
          <p className="px-3 pb-1.5 text-[11px] font-bold uppercase tracking-[0.1em] text-emerald-50/45">Quy trình</p>
          {FLOW.map((item) => <NavItem key={item.key} item={item} runId={runId} active={active} badge={badges[item.key]} />)}
          <p className="px-3 pb-1.5 pt-6 text-[11px] font-bold uppercase tracking-[0.1em] text-emerald-50/45">Khác</p>
          {MORE.map((item) => <NavItem key={item.key} item={item} runId={runId} active={active} badge={badges[item.key]} />)}
        </nav>
        <div className="space-y-3 border-t border-white/10 px-4 py-4 text-xs text-emerald-50/70">
          <div className="rounded-lg bg-white/[.06] px-3 py-2.5">
            {runId ? (
              <>
                <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-emerald-50/45">Phiên đang mở</p>
                <p className="mt-0.5 truncate font-medium text-white" title={runLabel || runId}>{runLabel || 'Phiên chưa đặt tên'}</p>
                <p className="font-mono text-[11px] text-emerald-50/55">{shortId(runId)}</p>
              </>
            ) : (
              <p>Chưa mở phiên phân tích nào.</p>
            )}
          </div>
          <Link to="/settings" className="flex items-center gap-3 rounded-lg px-1 py-1 transition hover:bg-white/5" title="Đổi tên người soát xét trong Cài đặt">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-300 text-sm font-bold text-[#0F3D2E] ring-2 ring-white/10">
              {(reviewer || '?').trim().split(/\s+/).map((w) => w[0]).slice(-2).join('').toUpperCase()}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-white">{reviewer || 'Chưa có người soát xét'}</span>
              <span className="block text-[11px] text-emerald-50/55">Người soát xét</span>
            </span>
          </Link>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 px-8 py-4">
            <div className="min-w-0">
              <h1 className="truncate text-[22px] font-bold tracking-tight text-slate-900">{title}</h1>
              {subtitle && <p className="mt-0.5 truncate text-[13px] text-slate-500">{subtitle}</p>}
            </div>
            <div className="flex items-center gap-2">
              {runtime && (
                <Link to="/settings">
                  <Dot state={runtime.sends_documents_out ? 'cloud' : 'ok'} title={runtimeTitle}>{runtime.sends_documents_out ? <Icon name="cloud" className="h-3.5 w-3.5" /> : <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />}{runtime.label}</Dot>
                </Link>
              )}
              {apiStatus !== 'online' && (
                <Dot state={apiStatus === 'offline' ? 'bad' : 'idle'}>
                  {apiStatus === 'offline' ? '● Máy chủ chưa chạy' : '● Đang kiểm tra máy chủ'}
                </Dot>
              )}
            </div>
          </div>
          {/* Mobile nav: the sidebar collapses into a scrollable row. */}
          <nav className="flex gap-1 overflow-x-auto px-4 pb-2 md:hidden">
            {[...FLOW, ...MORE].map((item) => {
              const disabled = item.needsRun && !runId
              const to = typeof item.to === 'function' ? item.to(runId) : item.to
              return disabled ? null : (
                <Link
                  key={item.key}
                  to={to}
                  className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${active === item.key ? 'bg-[#0F3D2E] text-white' : 'bg-slate-100 text-slate-700'}`}
                >
                  {item.step ? `${item.step}. ` : ''}{item.label}
                </Link>
              )
            })}
          </nav>
        </header>

        <main className="flex-1 px-8 py-6">{children}</main>

        <footer className="px-8 pb-6 pt-2">
          <p className="max-w-4xl text-xs leading-relaxed text-slate-500">
            GreenScan ước lượng mức độ đầy đủ của bằng chứng cho từng tuyên bố. Kết quả không phải kết
            luận pháp lý về hành vi của doanh nghiệp, không thay thế kiểm toán viên hay cơ quan quản lý,
            và thiếu bằng chứng không đồng nghĩa vi phạm.
          </p>
        </footer>
      </div>
    </div>
  )
}

export { Leaf }
