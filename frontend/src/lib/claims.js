import { labelOf } from './labels'
/**
 * Derived views over an AnalyzeResponse.
 *
 * The claim is the unit of work. Everything here is shaped so a reviewer can
 * answer one question per claim: what is asserted, where it came from, which
 * mandatory attributes are present, what the evidence says, and what follows.
 */

/**
 * The five attributes a claim must state: chỉ số, giá trị, kỳ, năm gốc, phạm vi.
 *
 * One definition for the queue tag, the attribute card, the filters and the
 * summary line, the same one the report gives (KHAI_NIEM_CAN_NAM.md) and the
 * backend checks (agents/verifier.py `missing_attributes`). The card used to be
 * built from risk-score components while the summary line used the claim's own
 * fields, so one claim read "thiếu 1/5" in the queue, "2/5" on its card and
 * "thiếu số liệu, kỳ, năm gốc" in its summary (seen in the demo video, 09/11).
 *
 * Năm gốc is required only of a claim that states a change or a target (scoring
 * v3); for any other claim it is "không áp dụng", never "thiếu".
 *
 * `assertion` names the audit assertion each one serves (ISA 315 vocabulary).
 * Evidence and methodology are not an attribute of the claim: they are what the
 * verdict and the evidence tab report.
 */
export const ATTRIBUTES = [
  {
    key: 'metric',
    label: 'Chỉ số',
    assertion: 'phân loại',
    hint: 'Tuyên bố nói về chỉ số nào: phát thải, điện tái tạo, nước, chất thải…',
    fix: 'Nêu rõ chỉ số đang nói tới.',
  },
  {
    key: 'values',
    label: 'Giá trị',
    assertion: 'chính xác',
    hint: 'Con số kèm đơn vị đo, không phải mô tả chung chung.',
    fix: 'Nêu con số và đơn vị đo.',
  },
  {
    key: 'period',
    label: 'Kỳ báo cáo',
    assertion: 'đúng kỳ',
    hint: 'Số liệu thuộc năm hoặc kỳ nào.',
    fix: 'Ghi rõ năm hoặc kỳ báo cáo của số liệu.',
  },
  {
    key: 'baseline',
    label: 'Năm gốc',
    assertion: 'chính xác (so sánh)',
    hint: 'Mốc để so sánh; chỉ bắt buộc khi tuyên bố nói tăng, giảm hoặc đặt mục tiêu.',
    fix: 'Bổ sung năm gốc: “giảm 30% so với 2019”.',
  },
  {
    key: 'scope',
    label: 'Phạm vi',
    assertion: 'đầy đủ',
    hint: 'Một nhà máy, công ty mẹ hay toàn tập đoàn; với phát thải là phạm vi 1, 2, 3.',
    fix: 'Nêu phạm vi pháp nhân/cơ sở, hoặc phạm vi phát thải.',
  },
]

const EMISSION_SCOPE = /(phạm vi|scope)\s*[123]/i

/** Mirror of agents/verifier.py `missing_attributes`: 'present' | 'missing' | 'not_applicable' per attribute. */
export function attributeStates(claim) {
  const changeOrTarget = Boolean(claim.direction || claim.is_future_commitment)
  return {
    metric: claim.metric ? 'present' : 'missing',
    values: claim.values?.length ? 'present' : 'missing',
    period: claim.period ? 'present' : 'missing',
    baseline: !changeOrTarget ? 'not_applicable' : claim.baseline ? 'present' : 'missing',
    scope: claim.scope || EMISSION_SCOPE.test(claim.text || '') ? 'present' : 'missing',
  }
}

/** Penalties are signals, not mandatory attributes — kept visually separate. */
export const PENALTIES = [
  { key: 'contradiction', label: 'Mâu thuẫn với dữ liệu khác' },
  { key: 'vague_or_exaggerated_language', label: 'Ngôn ngữ mơ hồ hoặc phóng đại' },
]

/** Tên tiếng Việt của từng thành phần điểm rủi ro (backend trả mã kỹ thuật). */
export const RISK_COMPONENT_LABELS = {
  specificity: 'Mức cụ thể của câu',
  quantitative_evidence: 'Có số liệu định lượng',
  baseline: 'Năm gốc',
  period: 'Kỳ báo cáo',
  scope_boundary: 'Phạm vi / ranh giới',
  evidence_support: 'Bằng chứng đối chiếu',
  independent_assurance: 'Đảm bảo độc lập',
  contradiction: 'Mâu thuẫn với dữ liệu khác',
  vague_or_exaggerated_language: 'Ngôn ngữ mơ hồ, phóng đại',
  anomaly: 'Số liệu bất thường',
  evidence_gap: 'Khoảng trống bằng chứng',
  materiality: 'Mức trọng yếu',
  obligation: 'Nghĩa vụ pháp lý liên quan',
}

export const RELATIONS = {
  SUPPORTS: { label: 'Ủng hộ', labelVi: 'Ủng hộ', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
  CONTRADICTS: { label: 'Mâu thuẫn', labelVi: 'Mâu thuẫn', className: 'bg-red-100 text-red-800 border-red-300' },
  PARTIAL: { label: 'Một phần', labelVi: 'Một phần', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  CONTEXT: { label: 'Chỉ liên quan', labelVi: 'Chỉ liên quan', className: 'bg-slate-100 text-slate-700 border-slate-300' },
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
  const metric = labelOf('metric', claim.metric) || 'chỉ số đang nêu'
  const period = claim.period ? `kỳ đang nêu: ${claim.period}` : 'chưa nêu kỳ nào'
  const unit = labelOf('unit', claim.units?.[0])
  const value = claim.values?.[0]

  switch (attributeKey) {
    case 'metric':
      return value == null
        ? 'Nêu rõ chỉ số đang nói tới: phát thải, điện tái tạo, nước, chất thải…'
        : `Gắn ${value}${unit ? ` ${unit}` : ''} với một chỉ số có tên rõ ràng.`
    case 'values':
      return `Nêu con số và đơn vị cho ${metric} (ví dụ: 12.400 tấn CO2 tương đương), thay vì mô tả định tính.`
    case 'baseline':
      return `Nêu năm gốc để so sánh — “giảm so với năm nào?” (${period}).`
    case 'period':
      return `Xác định kỳ mà ${metric} áp dụng (năm tài chính hay năm dương lịch).`
    case 'scope':
      return 'Nêu phạm vi: công ty mẹ, toàn tập đoàn, nhà máy cụ thể, dòng sản phẩm, hay phạm vi phát thải 1 (trực tiếp), 2 (năng lượng mua vào), 3 (chuỗi giá trị).'
    default:
      return 'Bổ sung thông tin còn thiếu cho thuộc tính này.'
  }
}

export function buildRows(analysis) {
  if (!analysis) return []
  const risks = new Map((analysis.risks || []).map((r) => [r.claim_id, r]))
  return (analysis.verifications || []).map((v) => {
    const risk = risks.get(v.claim.claim_id)
    const evidence = v.evidence || []
    const states = attributeStates(v.claim)
    // risk-score components by name, for the penalty flags below (the attribute states above read the claim itself)
    const components = new Map((risk?.components || []).map((c) => [c.name, c]))
    const attributes = ATTRIBUTES.map((a) => ({
      ...a, state: states[a.key], action: states[a.key] === 'missing' ? actionFor(a.key, v.claim, evidence) : null,
    }))
    return {
      id: v.claim.claim_id,
      claim: v.claim,
      status: v.status,
      rationale: v.rationale,
      assessment: v.assessment || null,
      assist: v.assist || {},   // llm_stages_v1: model explanation / dual-reader notes, shown beside the rules, never instead
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
      // suspected_injection also covers passages the verifier dropped, which are not in `evidence`.
      flagged: Boolean(v.suspected_injection) || evidence.some((e) => e.suspicious_instruction),
      suspect: v.claim.quality_flag || null,
      // A number on a scanned page that OCR was unsure of (verifier _unless_misread).
      misread: Boolean(v.doubtful_reading),
      doubtfulNumbers: v.claim.doubtful_numbers || [],
      ocrConfidence: v.claim.ocr_confidence ?? null,
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
    return { key: a.key, label: a.label, assertion: a.assertion, fix: a.fix, claims, count: claims.length }
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
