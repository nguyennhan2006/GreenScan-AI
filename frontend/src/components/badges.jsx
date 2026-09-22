/**
 * Semantic colours are fixed across the app (PRODUCTION_UI_SPEC §4.2):
 * emerald = supported, amber = partial, violet = unsupported, red = contradicted,
 * sky = insufficient evidence (a valid abstain, never red), slate = context.
 */
export const STATUS_STYLES = {
  SUPPORTED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  PARTIALLY_SUPPORTED: 'bg-amber-100 text-amber-800 border-amber-300',
  UNSUPPORTED: 'bg-violet-100 text-violet-800 border-violet-300',
  CONTRADICTED: 'bg-red-100 text-red-800 border-red-300',
  INSUFFICIENT_EVIDENCE: 'bg-sky-100 text-sky-800 border-sky-300',
}

export const STATUS_LABELS = {
  SUPPORTED: 'Được ủng hộ',
  PARTIALLY_SUPPORTED: 'Ủng hộ một phần',
  UNSUPPORTED: 'Chưa được chứng minh',
  CONTRADICTED: 'Mâu thuẫn với nguồn',
  INSUFFICIENT_EVIDENCE: 'Chưa đủ bằng chứng',
}

export const STATUS_LABELS_EN = {
  SUPPORTED: 'Supported',
  PARTIALLY_SUPPORTED: 'Partially supported',
  UNSUPPORTED: 'Unsupported',
  CONTRADICTED: 'Contradicted',
  INSUFFICIENT_EVIDENCE: 'Insufficient evidence',
}

export const STATUS_ORDER = [
  'SUPPORTED', 'PARTIALLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE',
]

/** Bar colour for the verdict distribution — same hue family as the badge. */
export const STATUS_BAR = {
  SUPPORTED: 'bg-emerald-500',
  PARTIALLY_SUPPORTED: 'bg-amber-400',
  UNSUPPORTED: 'bg-violet-400',
  CONTRADICTED: 'bg-red-500',
  INSUFFICIENT_EVIDENCE: 'bg-sky-400',
}

/** Severity is a review-priority hint, never a headline (spec P5). */
export const PRIORITY = {
  LOW: { label: 'Thấp', dot: 'bg-emerald-400', text: 'text-emerald-700' },
  MEDIUM: { label: 'Trung bình', dot: 'bg-amber-400', text: 'text-amber-700' },
  HIGH: { label: 'Cao', dot: 'bg-orange-500', text: 'text-orange-700' },
  CRITICAL: { label: 'Rất cao', dot: 'bg-red-500', text: 'text-red-700' },
}

export const WORKFLOW = {
  AI_SUGGESTED: { label: 'AI đề xuất', className: 'bg-slate-100 text-slate-700 border-slate-300' },
  HUMAN_REVIEWED: { label: 'Đã có người xem', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  FINALIZED: { label: 'Đã chốt', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
}

export const RELEASE = {
  RELEASABLE: { label: 'Có thể phát hành', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
  PENDING_HUMAN_REVIEW: { label: 'Chờ người duyệt', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  BLOCKED: { label: 'Bị chặn bởi cổng chất lượng', className: 'bg-red-100 text-red-800 border-red-300' },
}

export function StatusBadge({ status, size = 'sm' }) {
  const pad = size === 'md' ? 'px-3 py-1 text-sm' : 'px-2.5 py-0.5 text-xs'
  return (
    <span className={`inline-block whitespace-nowrap rounded-full border font-semibold ${pad} ${STATUS_STYLES[status] || STATUS_STYLES.INSUFFICIENT_EVIDENCE}`}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}

export function PriorityBadge({ severity, withLabel = true }) {
  const p = PRIORITY[severity]
  if (!p) return null
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium ${p.text}`}
      title="Ưu tiên xem xét — tín hiệu sắp xếp, không phải kết luận"
    >
      <span className={`inline-block h-2 w-2 rounded-full ${p.dot}`} />
      {withLabel && p.label}
    </span>
  )
}

export function WorkflowPill({ state }) {
  const s = WORKFLOW[state] || WORKFLOW.AI_SUGGESTED
  return (
    <span className={`inline-block whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold ${s.className}`}>
      {s.label}
    </span>
  )
}

export function ReleasePill({ status }) {
  const s = RELEASE[status]
  if (!s) return null
  return (
    <span className={`inline-block whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold ${s.className}`}>
      {s.label}
    </span>
  )
}

export function Chip({ children, tone = 'slate', className = '' }) {
  const tones = {
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    emerald: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    amber: 'bg-amber-50 text-amber-800 border-amber-200',
    red: 'bg-red-50 text-red-800 border-red-200',
    sky: 'bg-sky-50 text-sky-800 border-sky-200',
    violet: 'bg-violet-50 text-violet-800 border-violet-200',
  }
  return (
    <span className={`inline-block whitespace-nowrap rounded-full border px-2 py-0.5 text-[11px] font-medium ${tones[tone] || tones.slate} ${className}`}>
      {children}
    </span>
  )
}
