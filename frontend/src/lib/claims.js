/**
 * Derived views over an AnalyzeResponse.
 *
 * The claim is the unit of work. Everything here is shaped so a reviewer can
 * answer one question per claim: what is asserted, where it came from, which
 * mandatory attributes are present, what the evidence says, and what follows.
 */

/**
 * The five mandatory attributes — the design-system primitive.
 *
 * Each maps to scorer components (risk-rubric-v2). `components` lists every
 * component that must be satisfied; the attribute is only "present" when all
 * of them are, so Evidence/Methodology cannot pass on retrieval alone while
 * lacking any independent source.
 */
export const ATTRIBUTES = [
  {
    key: 'specific_metric',
    label: 'Specific metric',
    labelVi: 'Chỉ số cụ thể',
    components: ['specificity', 'quantitative_evidence'],
    hint: 'Một chỉ số xác định kèm giá trị và đơn vị, không phải mô tả chung.',
    fix: 'Nêu rõ chỉ số, con số và đơn vị đo.',
  },
  {
    key: 'baseline',
    label: 'Baseline',
    labelVi: 'Năm gốc',
    components: ['baseline'],
    hint: 'Mốc so sánh cho mọi tuyên bố tăng/giảm.',
    fix: 'Bổ sung năm gốc: “giảm 30% so với 2019”.',
  },
  {
    key: 'period',
    label: 'Period',
    labelVi: 'Kỳ báo cáo',
    components: ['period'],
    hint: 'Số liệu thuộc kỳ nào.',
    fix: 'Ghi rõ năm hoặc kỳ báo cáo của số liệu.',
  },
  {
    key: 'scope_boundary',
    label: 'Scope / Boundary',
    labelVi: 'Phạm vi áp dụng',
    components: ['scope_boundary'],
    hint: 'Một nhà máy, công ty mẹ hay toàn tập đoàn; Scope 1/2/3.',
    fix: 'Nêu phạm vi pháp nhân/cơ sở, hoặc phạm vi phát thải.',
  },
  {
    key: 'evidence_methodology',
    label: 'Evidence / Methodology',
    labelVi: 'Bằng chứng & phương pháp',
    components: ['evidence_support', 'independent_assurance'],
    hint: 'Có nguồn đối chiếu và phương pháp tính kiểm chứng được.',
    fix: 'Dẫn bảng số liệu, phương pháp tính hoặc assurance statement.',
  },
]

/** Penalties are signals, not mandatory attributes — kept visually separate. */
export const PENALTIES = [
  { key: 'contradiction', label: 'Mâu thuẫn với dữ liệu khác' },
  { key: 'vague_or_exaggerated_language', label: 'Ngôn ngữ mơ hồ hoặc phóng đại' },
]

export const RELATIONS = {
  SUPPORTS: { label: 'Supports', labelVi: 'Ủng hộ', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
  CONTRADICTS: { label: 'Contradicts', labelVi: 'Mâu thuẫn', className: 'bg-red-100 text-red-800 border-red-300' },
  PARTIAL: { label: 'Partial', labelVi: 'Một phần', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  CONTEXT: { label: 'Context', labelVi: 'Ngữ cảnh', className: 'bg-slate-100 text-slate-700 border-slate-300' },
}

/** Abstain is a normal workflow outcome, not a failure. */
export const ABSTAIN_STATUSES = new Set(['INSUFFICIENT_EVIDENCE', 'UNSUPPORTED'])

/**
 * Turn a missing attribute into an instruction that names this claim's own
 * values. A generic "bổ sung năm gốc" makes the author work out what to write;
 * "so với năm nào? (kỳ đang nêu: 2025)" is something they can act on directly.
 *
 * This is the foundation the authoring mode will reuse, so the wording stays
 * about *evidence to add*, never about phrasing the claim more attractively.
 */
export function actionFor(attributeKey, claim, evidence = []) {
  const metric = claim.metric || 'chỉ số đang nêu'
  const period = claim.period ? `kỳ đang nêu: ${claim.period}` : 'chưa nêu kỳ nào'
  const unit = claim.units?.[0]
  const value = claim.values?.[0]

  switch (attributeKey) {
    case 'specific_metric':
      return value == null
        ? `Nêu con số và đơn vị cho ${metric} (ví dụ: 12.400 tCO2e), thay vì mô tả định tính.`
        : `Gắn ${value}${unit ? ` ${unit}` : ''} với một chỉ số có tên rõ ràng.`
    case 'baseline':
      return `Nêu năm gốc để so sánh — “giảm so với năm nào?” (${period}).`
    case 'period':
      return `Xác định kỳ mà ${metric} áp dụng (năm tài chính hay năm dương lịch).`
    case 'scope_boundary':
      return 'Nêu phạm vi: công ty mẹ, toàn tập đoàn, nhà máy cụ thể, dòng sản phẩm, hay Scope 1/2/3.'
    case 'evidence_methodology': {
      const parts = [`cùng chỉ số (${metric})`]
      if (claim.period) parts.push(`cùng kỳ (${claim.period})`)
      if (claim.scope) parts.push(`cùng phạm vi (${claim.scope})`)
      const near = evidence.filter((e) => e.relation === 'PARTIAL').length
      const tail = near
        ? ` Hiện có ${near} đoạn liên quan nhưng chưa khớp đủ ba điều kiện.`
        : ' Hiện chưa truy xuất được đoạn nào đủ gần.'
      return `Cần bằng chứng ${parts.join(' + ')}, kèm phương pháp tính.${tail}`
    }
    default:
      return 'Bổ sung thông tin còn thiếu cho thuộc tính này.'
  }
}

function componentMap(risk) {
  const out = new Map()
  for (const c of risk?.components || []) out.set(c.name, c)
  return out
}

/** 'present' | 'partial' | 'missing' | 'unknown' across all backing components. */
function attributeState(components, keys) {
  const present = keys.map((k) => components.get(k)).filter(Boolean)
  if (!present.length) return { state: 'unknown', detail: '' }
  // Components are penalties: 0 = attribute satisfied, max = absent.
  const ratios = present.map((c) => (c.max_score ? c.score / c.max_score : 0))
  const detail = present.map((c) => c.reason).join(' ')
  if (ratios.every((r) => r === 0)) return { state: 'present', detail }
  if (ratios.every((r) => r >= 0.99)) return { state: 'missing', detail }
  return { state: 'partial', detail }
}

export function buildRows(analysis) {
  if (!analysis) return []
  const risks = new Map((analysis.risks || []).map((r) => [r.claim_id, r]))
  return (analysis.verifications || []).map((v) => {
    const risk = risks.get(v.claim.claim_id)
    const components = componentMap(risk)
    const evidence = v.evidence || []
    const attributes = ATTRIBUTES.map((a) => {
      const s = attributeState(components, a.components)
      return { ...a, ...s, action: s.state === 'present' ? null : actionFor(a.key, v.claim, evidence) }
    })
    return {
      id: v.claim.claim_id,
      claim: v.claim,
      status: v.status,
      rationale: v.rationale,
      computed: v.computed_values || null,
      warnings: v.warnings || [],
      requiresLlmReview: Boolean(v.requires_llm_review),
      evidence,
      contradicting: evidence.filter((e) => e.relation === 'CONTRADICTS'),
      supporting: evidence.filter((e) => e.relation === 'SUPPORTS'),
      risk,
      score: risk?.risk_score ?? null,
      severity: risk?.severity ?? null,
      attributes,
      penalties: PENALTIES.map((p) => {
        const c = components.get(p.key)
        return { ...p, active: Boolean(c && c.max_score && c.score > 0) }
      }),
      missing: attributes.filter((a) => a.state === 'missing'),
      isAbstain: ABSTAIN_STATUSES.has(v.status),
      flagged: evidence.some((e) => e.suspicious_instruction),
      requiresReview: risk?.requires_human_review ?? false,
    }
  })
}

/**
 * Worklists, not vanity stats.
 *
 * The dashboard exists to let someone resume work, so every number here is a
 * queue you can open. No score leaderboard, no risk-over-time series: both
 * describe the upload queue rather than anything about the issuer.
 */
export function summarise(rows, analysis) {
  const byStatus = {}
  for (const r of rows) byStatus[r.status] = (byStatus[r.status] || 0) + 1

  const unresolved = rows.filter((r) => r.missing.length > 0 || r.isAbstain)
  const noEvidence = rows.filter((r) => r.evidence.length === 0)
  const contradicted = rows.filter((r) => r.contradicting.length > 0)
  const needsConfirmation = rows.filter(
    (r) => r.requiresReview || r.severity === 'HIGH' || r.severity === 'CRITICAL' || r.flagged,
  )

  const missingByAttribute = ATTRIBUTES.map((a) => {
    const claims = rows.filter((r) => r.missing.some((m) => m.key === a.key))
    return { key: a.key, label: a.label, labelVi: a.labelVi, fix: a.fix, claims, count: claims.length }
  }).sort((x, y) => y.count - x.count)

  const documents = [...new Set(rows.map((r) => r.claim.source_name))].map((name) => {
    const claims = rows.filter((r) => r.claim.source_name === name)
    return {
      name,
      total: claims.length,
      unresolved: claims.filter((c) => c.missing.length > 0 || c.isAbstain).length,
      contradicted: claims.filter((c) => c.contradicting.length > 0).length,
    }
  }).sort((a, b) => b.unresolved - a.unresolved)

  return {
    total: rows.length,
    byStatus,
    unresolved,
    noEvidence,
    contradicted,
    needsConfirmation,
    abstain: rows.filter((r) => r.isAbstain),
    missingByAttribute,
    documents,
    releaseStatus: analysis?.summary?.release_status ?? null,
    chunks: analysis?.summary?.total_chunks ?? 0,
    gates: analysis?.quality_gates || [],
    corpus: analysis?.corpus || null,
  }
}

export function locationOf(e) {
  const bits = []
  if (e.page != null) bits.push(`tr. ${e.page}`)
  if (e.is_table) bits.push('bảng')
  return bits.length ? `${e.source_name} · ${bits.join(' · ')}` : e.source_name
}
