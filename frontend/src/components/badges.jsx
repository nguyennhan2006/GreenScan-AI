export const STATUS_STYLES = {
  SUPPORTED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  PARTIALLY_SUPPORTED: 'bg-amber-100 text-amber-800 border-amber-300',
  UNSUPPORTED: 'bg-orange-100 text-orange-800 border-orange-300',
  CONTRADICTED: 'bg-red-100 text-red-800 border-red-300',
  INSUFFICIENT_EVIDENCE: 'bg-slate-100 text-slate-700 border-slate-300',
}

export const STATUS_LABELS = {
  SUPPORTED: 'Được chứng minh',
  PARTIALLY_SUPPORTED: 'Chứng minh một phần',
  UNSUPPORTED: 'Không có chứng cứ',
  CONTRADICTED: 'Mâu thuẫn chứng cứ',
  INSUFFICIENT_EVIDENCE: 'Chứng cứ chưa đủ',
}

export const SEVERITY_STYLES = {
  LOW: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300',
  HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
  CRITICAL: 'bg-red-100 text-red-800 border-red-300',
}

export const SEVERITY_LABELS = {
  LOW: 'Rủi ro thấp',
  MEDIUM: 'Rủi ro trung bình',
  HIGH: 'Rủi ro cao',
  CRITICAL: 'Rủi ro nghiêm trọng',
}

export function StatusBadge({ status }) {
  return (
    <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STATUS_STYLES[status] || STATUS_STYLES.INSUFFICIENT_EVIDENCE}`}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}

export function SeverityBadge({ severity }) {
  return (
    <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${SEVERITY_STYLES[severity] || SEVERITY_STYLES.LOW}`}>
      {SEVERITY_LABELS[severity] || severity}
    </span>
  )
}

export function riskBarColor(score) {
  if (score >= 75) return 'bg-red-500'
  if (score >= 50) return 'bg-orange-500'
  if (score >= 25) return 'bg-amber-500'
  return 'bg-emerald-500'
}
