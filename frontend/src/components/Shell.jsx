import { DISCLAIMER } from '../lib/labels.js'
import { Link } from '../lib/router.jsx'
import { shortId } from '../lib/format.js'
import { STEPS } from '../lib/flow.js'
import { Icon } from './icons.jsx'

/**
 * App shell: light sidebar, light content area (18/11: lighter, one accent colour).
 *
 * The sidebar is the process, not a menu: three numbered steps in the order
 * the work is done (documents → queue → working paper), then the screens one
 * visits occasionally. Steps that need a loaded run are shown disabled rather
 * than hidden, so the whole process stays visible from the first screen.
 */

const FLOW = STEPS   // one list for the sidebar and every “Việc tiếp theo” bar (lib/flow.js)
const MORE = [
  { key: 'guide', label: 'Hướng dẫn', to: '/guide', icon: 'help' },
  { key: 'claims', label: 'Tất cả tuyên bố', to: (id) => `/runs/${id}/claims`, icon: 'list', needsRun: true },
  { key: 'runs', label: 'Lịch sử phân tích', to: '/runs', icon: 'clock' },
  { key: 'legal', label: 'Thư viện pháp lý', to: '/legal', icon: 'scale' },
  { key: 'feedback', label: 'Học từ phản hồi', to: '/feedback', icon: 'list' },
  { key: 'settings', label: 'Cài đặt & chế độ chạy', to: '/settings', icon: 'settings' },
]

// Screens that show results carry the caution; the others (documents, settings, guide) have nothing to caution about.
const RESULT_PAGES = new Set(['queue', 'claims', 'export'])

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
  const cls = `flex items-center gap-3 rounded-xl px-3 py-[7px] text-[14.5px] transition ${
    isActive ? 'bg-emerald-50 font-semibold text-emerald-800 ring-1 ring-emerald-100'
      : disabled ? 'cursor-not-allowed text-slate-300'
        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
  }`
  const marker = item.step
    ? <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${isActive ? 'bg-emerald-600 text-white' : disabled ? 'bg-slate-100 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>{item.step}</span>
    : <span className={`flex w-6 justify-center ${isActive ? 'text-emerald-700' : 'text-slate-400'}`}><Icon name={item.icon} className="h-[18px] w-[18px]" /></span>
  const body = (
    <>
      {marker}
      <span className="flex-1">{item.label}</span>
      {badge > 0 && (
        <span className="min-w-5 rounded-full bg-amber-100 px-1.5 text-center text-xs font-bold leading-5 tabular-nums text-amber-800" title="Mục trong hàng đợi chưa chốt">
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
      <aside className="sticky top-[var(--gs-banner-h,0px)] hidden h-[calc(100vh-var(--gs-banner-h,0px))] w-65 shrink-0 flex-col border-r border-slate-200/80 bg-white md:flex">
        <Link to="/new" className="flex items-center gap-2.5 px-6 pb-4 pt-5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 ring-1 ring-emerald-100"><Leaf className="h-6 w-6 text-emerald-600" /></span>
          <span className="text-xl font-bold tracking-tight text-slate-900">GreenScan</span>
        </Link>
        <nav className="min-h-0 flex-1 space-y-0.5 overflow-y-auto px-3.5" aria-label="Quy trình">
          <p className="px-3 pb-1.5 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-400">Quy trình</p>
          {FLOW.map((item) => <NavItem key={item.key} item={item} runId={runId} active={active} badge={badges[item.key]} />)}
          <p className="px-3 pb-1.5 pt-4 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-400">Khác</p>
          {MORE.map((item) => <NavItem key={item.key} item={item} runId={runId} active={active} badge={badges[item.key]} />)}
        </nav>
        <div className="space-y-2 border-t border-slate-100 px-4 py-3 text-xs text-slate-500">
          <div className="rounded-xl bg-slate-50 px-3 py-2.5 ring-1 ring-slate-100">
            {runId ? (
              <>
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-slate-400">Phiên đang mở</p>
                <p className="mt-0.5 truncate font-medium text-slate-800" title={runLabel || runId}>{runLabel || 'Phiên chưa đặt tên'}</p>
                <p className="font-mono text-xs text-slate-400">{shortId(runId)}</p>
              </>
            ) : (
              <p>Chưa mở phiên phân tích nào.</p>
            )}
          </div>
          <Link to="/settings" className="flex items-center gap-3 rounded-xl px-1 py-1 transition hover:bg-slate-50" title="Đổi tên người soát xét trong Cài đặt">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-800">
              {(reviewer || '?').trim().split(/\s+/).map((w) => w[0]).slice(-2).join('').toUpperCase()}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-slate-800">{reviewer || 'Chưa có người soát xét'}</span>
              <span className="block text-xs text-slate-400">Người soát xét</span>
            </span>
          </Link>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
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
                  className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${active === item.key ? 'bg-[#047857] text-white' : 'bg-slate-100 text-slate-700'}`}
                >
                  {item.step ? `${item.step}. ` : ''}{item.label}
                </Link>
              )
            })}
          </nav>
        </header>

        {RESULT_PAGES.has(active) && (
          // The caution stays on every result page, as one quiet line rather than a banner.
          <p className="mx-8 mt-4 flex items-start gap-2 text-xs leading-relaxed text-slate-500" data-testid="disclaimer">
            <Icon name="info" className="mt-px h-4 w-4 shrink-0 text-amber-500" />
            <span>{DISCLAIMER}</span>
          </p>
        )}
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
