/**
 * The review queue, as the reviewer works it.
 *
 * The backend already ranks every claim and every disclosed figure by where an
 * auditor should look first (agents/prioritizer.py, `result.priorities`) and
 * says what the pass left out (`result.scope_note`). The UI used to ignore both
 * and sort by severity, which on a real report is one band: 154 of 156 claims
 * MEDIUM. This module joins the ranked records with the claim rows and the
 * figures so one list can show both kinds of item.
 */

export const METRIC_VI = {
  emissions: 'phát thải KNK',
  renewable_energy: 'năng lượng tái tạo',
  energy: 'năng lượng',
  water: 'nước',
  waste: 'chất thải',
  green_finance: 'tài chính xanh',
}

const SEVERITY_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

export function buildQueue(result, rows) {
  const rowsById = new Map(rows.map((r) => [r.id, r]))
  const figuresById = new Map((result?.disclosed_figures || []).map((f) => [f.figure_id, f]))
  const checksByFigure = new Map()
  for (const check of result?.figure_checks || []) {
    for (const id of check.figure_ids || []) {
      if (!checksByFigure.has(id)) checksByFigure.set(id, [])
      checksByFigure.get(id).push(check)
    }
  }

  const priorities = result?.priorities || []
  if (!priorities.length) {
    // A run saved before the priority layer existed (before 25/09): fall back
    // to the old ordering and say so, rather than show an empty queue.
    const items = [...rows]
      .sort((a, b) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9))
      .map((row, i) => ({ item_type: 'claim', item_id: row.id, rank: i + 1, in_queue: i < 25, row, figure: null, checks: [], reasons: [], components: [] }))
    return { items, queued: items.filter((i) => i.in_queue), rest: items.filter((i) => !i.in_queue), legacy: true }
  }

  const items = priorities
    .map((p) => ({
      ...p,
      row: p.item_type === 'claim' ? rowsById.get(p.item_id) || null : null,
      figure: p.item_type === 'figure' ? figuresById.get(p.item_id) || null : null,
      checks: p.item_type === 'figure' ? checksByFigure.get(p.item_id) || [] : [],
    }))
    .filter((i) => i.row || i.figure)
    .sort((a, b) => a.rank - b.rank)
  return { items, queued: items.filter((i) => i.in_queue), rest: items.filter((i) => !i.in_queue), legacy: false }
}

/** Short reasons a reviewer can scan; the full sentences stay in the tooltip. */
export function tagsFor(item) {
  const tags = []
  const comp = Object.fromEntries((item.components || []).map((c) => [c.name, c]))
  const metric = item.row?.claim?.metric || item.figure?.metric
  if (metric) tags.push({ text: METRIC_VI[metric] || metric })
  if (item.figure) {
    tags.push({ text: item.figure.is_total ? 'dòng tổng của bảng' : 'số liệu trong bảng' })
    if (item.checks.some((c) => c.status === 'INCONSISTENT')) tags.push({ text: 'cộng lại không khớp', tone: 'red' })
    else if (item.checks.length) tags.push({ text: 'đã đối chiếu, khớp', tone: 'emerald' })
    else tags.push({ text: 'chưa có thủ tục đối chiếu', tone: 'amber' })
  } else if (item.row) {
    const quantified = (item.row.claim.values || []).length > 0
    tags.push({ text: quantified ? 'có số liệu' : 'không có số liệu', tone: quantified ? undefined : 'amber' })
    if (item.row.contradicting.length) tags.push({ text: `${item.row.contradicting.length} đoạn mâu thuẫn`, tone: 'red' })
    if (item.row.missing.length) tags.push({ text: `thiếu ${item.row.missing.length}/5 thuộc tính` })
    if (item.row.requiresLlmReview) tags.push({ text: 'mô hình đề xuất — cần xác nhận', tone: 'violet' })
  }
  if (comp.obligation && comp.obligation.max_score && comp.obligation.score / comp.obligation.max_score >= 0.5) {
    tags.push({ text: 'có văn bản pháp lý liên quan', tone: 'sky' })
  }
  if ((comp.materiality?.reason || '').includes('không nêu chủ thể')) tags.push({ text: 'có thể là câu giải thích chung' })
  if ((comp.materiality?.reason || '').includes('dính cột')) tags.push({ text: 'chữ lỗi trình bày — xem trang gốc', tone: 'amber' })
  return tags
}

export function reasonText(item) {
  return (item.reasons || []).map((r) => r.replaceAll('**', '')).join('\n')
}

/** An evidence-shaped object so the page viewer can open a figure's row. */
export function figureAsEvidence(figure, checks = []) {
  return {
    doc_id: figure.source_doc_id,
    source_name: figure.source_name,
    page: figure.source_page,
    text: figure.raw_line || figure.label,
    is_table: true,
    relation: 'CONTEXT',
    relation_method: 'disclosed_figure',
    source_type: 'internal',
    relation_reason: checks.map((c) => `${c.calculation} — ${c.note}`.replaceAll('**', '')).join('\n')
      || 'Chưa có thủ tục nào đối chiếu được số này (cộng lại bảng hoặc so với tài liệu khác).',
  }
}

export function formatFigure(figure) {
  if (!figure) return ''
  const value = Number(figure.value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })
  return `${value} ${figure.unit === 'tan' ? 'tấn' : figure.unit}`
}
