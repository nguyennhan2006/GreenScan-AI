import { useEffect, useState } from 'react'
import { Link } from '../lib/router.jsx'
import { TOTAL_STEPS } from '../lib/flow.js'

/**
 * One line that says what to do now, with the one button that does it (next-step-v1).
 *
 * Each page computes its own sentence from its own state, so the bar never describes a step the
 * reviewer has already taken. It can be hidden; the choice is kept on this browser and can be
 * undone on the Settings page.
 */

const KEY = 'gs.tips.off'
const EVENT = 'gs-tips-changed'

export function tipsHidden() {
  try { return localStorage.getItem(KEY) === '1' } catch { return false }
}

export function setTipsHidden(hidden) {
  try {
    if (hidden) localStorage.setItem(KEY, '1')
    else localStorage.removeItem(KEY)
  } catch { /* không lưu được thì chỉ ẩn trong lần mở này */ }
  window.dispatchEvent(new Event(EVENT))
}

export function useTipsHidden() {
  const [hidden, setHidden] = useState(tipsHidden)
  useEffect(() => {
    const sync = () => setHidden(tipsHidden())
    window.addEventListener(EVENT, sync)
    return () => window.removeEventListener(EVENT, sync)
  }, [])
  return hidden
}

const BUTTON = 'inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-[#047857] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#065f46] disabled:opacity-40'

/** Small animated arrow placed just before the button the reviewer should press next. */
export function ArrowHint({ label = 'bấm', dir = 'right', className = '' }) {
  const down = dir === 'down'
  return (
    <span className={`${down ? 'gs-nudge-y' : 'gs-nudge'} hidden items-center gap-1 text-xs font-semibold text-emerald-700 sm:inline-flex ${className}`} aria-hidden="true">
      {label}
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        {down ? <><path d="M12 4v14" /><path d="m6 13 6 6 6-6" /></> : <><path d="M4 12h14" /><path d="m13 6 6 6-6 6" /></>}
      </svg>
    </span>
  )
}

export default function NextStep({ step, total = TOTAL_STEPS, children, action = null, alt = null, done = false }) {
  const hidden = useTipsHidden()
  if (hidden) return null
  return (
    <div
      data-testid="next-step"
      className={`flex flex-wrap items-center gap-x-4 gap-y-2 rounded-2xl border px-4 py-3 shadow-sm ${done ? 'border-emerald-200 bg-emerald-50/70' : 'border-emerald-100 bg-linear-to-r from-emerald-50/80 via-white to-white'}`}
    >
      <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold ${done ? 'bg-emerald-500 text-white' : 'bg-emerald-600 text-white shadow-sm shadow-emerald-600/30'}`} title={`Bước ${step} trên ${total}`}>
        {done ? '✓' : step}
      </span>
      {/* basis-60: on a phone the sentence keeps a readable width and the button wraps below it */}
      <div className="min-w-0 flex-1 basis-60">
        <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">{done ? 'Đã xong bước này' : 'Việc tiếp theo'} · bước {step}/{total}</p>
        <p className="text-sm leading-snug text-slate-800">{children}</p>
      </div>
      {action && (
        // The arrow and the soft halo point at the one button to press next; both stop for reduced motion.
        <span className="flex shrink-0 items-center gap-2">
          {!action.disabled && <ArrowHint />}
          {action.to
            ? <Link to={action.to} className={`${BUTTON} gs-halo`} data-testid="next-step-action">{action.label}</Link>
            : <button type="button" onClick={action.onClick} disabled={action.disabled} className={`${BUTTON} ${action.disabled ? '' : 'gs-halo'}`} data-testid="next-step-action">{action.label}</button>}
        </span>
      )}
      {/* one quiet way to move on without finishing everything on this page */}
      {alt && <Link to={alt.to} className="shrink-0 text-xs font-medium text-slate-500 underline decoration-slate-300 underline-offset-2 hover:text-emerald-700" data-testid="next-step-alt">{alt.label}</Link>}
      <button
        type="button"
        onClick={() => setTipsHidden(true)}
        className="shrink-0 rounded px-1.5 text-lg leading-none text-slate-400 hover:bg-slate-100 hover:text-slate-700"
        title="Ẩn gợi ý này. Bật lại ở trang Cài đặt."
        aria-label="Ẩn gợi ý việc tiếp theo"
      >×</button>
    </div>
  )
}
