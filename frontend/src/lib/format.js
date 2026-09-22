export function formatDateTime(value) {
  if (!value) return '—'
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleString('vi-VN', { hour12: false })
}

export function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleDateString('vi-VN')
}

export function shortId(id, n = 8) {
  return id ? String(id).slice(0, n) : '—'
}

export function pct(value) {
  return `${Math.round((value || 0) * 100)}%`
}
