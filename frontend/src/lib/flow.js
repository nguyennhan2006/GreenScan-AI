/**
 * The guided flow, in one place (flow-v2, 18/11/2026).
 *
 * The sidebar, every “Việc tiếp theo” bar and the Studio top bar read the steps from here, so the
 * number on a page can never disagree with the sidebar, and the chain of “next” buttons always moves
 * forward: 1 → 2 → 3 → 4 → another session. No button points back at the page it came from.
 *
 * Checked end to end by tools/check_flow.py (clicks the chain in a real browser and fails on a loop,
 * a dead end or a page error).
 */
export const STEPS = [
  { key: 'new', step: 1, label: 'Tải tài liệu', to: '/new' },
  { key: 'queue', step: 2, label: 'Soát theo hàng đợi', to: (id) => `/runs/${id}`, needsRun: true },
  { key: 'studio', step: 3, label: 'Sửa báo cáo', to: (id) => `/runs/${id}/studio`, needsRun: true },
  { key: 'export', step: 4, label: 'Giấy làm việc', to: (id) => `/runs/${id}/export`, needsRun: true },
]

export const TOTAL_STEPS = STEPS.length

export function stepPath(key, runId) {
  const s = STEPS.find((x) => x.key === key)
  return typeof s.to === 'function' ? s.to(runId) : s.to
}

/** The button that leads from one step to the one after it; after the last step, to another session. */
export function onward(fromKey, runId) {
  const next = STEPS[STEPS.findIndex((s) => s.key === fromKey) + 1]
  return next
    ? { label: `Bước ${next.step}: ${next.label} →`, to: stepPath(next.key, runId) }
    : { label: 'Mở phiên khác →', to: '/runs' }
}

// Sessions worth opening, most telling first: the real report, the same report under a bank's own
// rules, the session a model read along, then anything else.
const PREFER = [
  [(l) => l.startsWith('Hòa Phát (HPG)'), 'phiên Hòa Phát'],
  [(l) => l.startsWith('Hòa Phát +'), 'phiên Hòa Phát + bộ quy tắc ngân hàng'],
  [(l) => l.includes('mô hình'), 'phiên có mô hình cùng đọc'],
]

/** A session to open next. Never the one that is open now, so finishing a session cannot loop back into it. */
export function suggestRun(runs, currentRunId) {
  const others = (runs || []).filter((r) => r.run_id !== currentRunId)
  for (const [test, name] of PREFER) {
    const hit = others.find((r) => test(r.label || ''))
    if (hit) return { run: hit, name }
  }
  return null
}
