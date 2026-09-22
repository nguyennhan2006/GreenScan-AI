import { Chip } from './badges.jsx'
import { ATTRIBUTES, PENALTIES } from '../lib/claims.js'
import { formatDate } from '../lib/format.js'

/**
 * The three panels that were missing from v1 (spec S3-D, S3-E, S3-F). Each
 * reads one backend structure and adds no logic of its own: the numbers, the
 * instruments and the component scores are exactly what the pipeline emitted.
 */

function Box({ label, value, tone = 'slate' }) {
  const tones = {
    slate: 'border-slate-200 bg-slate-50 text-slate-900',
    emerald: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    red: 'border-red-200 bg-red-50 text-red-900',
  }
  return (
    <div className={`min-w-28 rounded-lg border px-3 py-2 ${tones[tone]}`}>
      <p className="text-[11px] text-slate-500">{label}</p>
      <p className="font-mono text-sm font-semibold">{value}</p>
    </div>
  )
}

const fmt = (n) => (typeof n === 'number' ? (Number.isInteger(n) ? String(n) : n.toFixed(2)) : '—')

export function NumericCheckCard({ computed }) {
  const pair = computed?.closest_pair
  const claimNumbers = computed?.claim_numbers || []
  if (!claimNumbers.length) {
    return (
      <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        Tuyên bố không chứa số liệu để đối chiếu — kiểm chứng dựa trên cụm từ và ngữ cảnh.
      </p>
    )
  }
  if (!pair) {
    return (
      <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        Không có số liệu cùng chỉ số trong bằng chứng để so sánh.
      </p>
    )
  }
  const tone = computed.matched ? 'emerald' : computed.contradiction ? 'red' : 'slate'
  const err = pair.relative_error
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <Box label="Tuyên bố" value={fmt(pair.claim)} tone={tone} />
        <span className="text-slate-400">→</span>
        <Box label="Tài liệu" value={fmt(pair.evidence)} tone={tone} />
        <span className="text-slate-400">→</span>
        <Box label="Sai số tương đối" value={err == null ? '—' : `${(err * 100).toFixed(1)}%`} tone={tone} />
        <Chip tone={tone === 'slate' ? 'slate' : tone}>
          {computed.matched ? 'khớp trong dung sai' : computed.contradiction ? 'lệch đáng kể' : 'chưa kết luận'}
        </Chip>
      </div>
      <p className="mt-2 text-[11px] text-slate-500">
        nguồn: {pair.citation} · phương pháp: <code className="font-mono">{computed.calculation_method}</code>
        {computed.tolerance_used != null && <> · dung sai: <code className="font-mono">{Math.round(computed.tolerance_used * 100)}%</code></>}
        {computed.claim_scopes && <> · ranh giới: <code className="font-mono">Scope {computed.claim_scopes}</code></>}
        {' '}· số trong tuyên bố: <code className="font-mono">{claimNumbers.map(([v, u]) => `${v}${u || ''}`).join(', ')}</code>
        {(computed.skipped_boundary_mismatch || []).length > 0 && (
          <span className="block text-amber-800">Bỏ qua {computed.skipped_boundary_mismatch.length} đoạn khác ranh giới phát thải (Scope {computed.skipped_boundary_mismatch.map((b) => b.scopes).join(', ')}).</span>
        )}
      </p>
    </div>
  )
}

const FINDING = {
  MATCH: ['Phù hợp điều kiện đã kiểm', 'emerald'],
  PARTIAL_MATCH: ['Phù hợp một phần', 'amber'],
  NOT_MATCH: ['Chưa đáp ứng điều kiện đã kiểm', 'amber'],
  INSUFFICIENT_EVIDENCE: ['Chưa đủ dữ liệu pháp lý để kết luận', 'sky'],
}

export function LegalPanel({ legal, gate }) {
  if (!legal) {
    return (
      <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        Lớp pháp lý không chạy cho tuyên bố này{gate?.details ? `: ${gate.details}` : '.'}
      </p>
    )
  }
  const [findingLabel, findingTone] = FINDING[legal.legal_finding] || [legal.legal_finding, 'slate']
  const sources = legal.applicable_sources || []
  const blocked = legal.blocked_sources || []
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
        <span>Vấn đề pháp lý: <b className="text-slate-900">{legal.issue}</b></span>
        <span>· Tính đến <span className="font-mono">{formatDate(legal.as_of_date)}</span></span>
        <span>· Chế độ <code className="font-mono">{legal.check_mode}</code></span>
        <span>· Rule pack <code className="font-mono">{legal.rule_pack_version}</code></span>
      </div>

      <div className={`rounded-lg border px-3 py-2 text-sm ${
        findingTone === 'emerald' ? 'border-emerald-200 bg-emerald-50' : findingTone === 'amber' ? 'border-amber-200 bg-amber-50' : 'border-sky-200 bg-sky-50'
      }`}>
        <p className="font-semibold text-slate-900">{findingLabel}</p>
        {legal.notes && <p className="mt-1 text-xs text-slate-700">{legal.notes}</p>}
        {legal.legal_finding === 'INSUFFICIENT_EVIDENCE' && (
          <p className="mt-1 text-[11px] text-slate-600">Đây là khoảng trống dữ liệu (chưa có điều kiện kiểm được hoặc chưa trích được văn bản), không phải nhận định về doanh nghiệp.</p>
        )}
      </div>

      {sources.length > 0 && (
        <ol className="space-y-1.5 border-l-2 border-slate-200 pl-3">
          {sources.map((s) => (
            <li key={s.id} className="text-xs">
              <span className="font-mono text-slate-500">{formatDate(s.effective_from)}</span>
              <span className="ml-2 font-mono font-semibold text-slate-900">{s.document}</span>
              <Chip className="ml-2" tone={s.role === 'base' ? 'slate' : 'amber'}>{s.role === 'base' ? 'văn bản gốc' : 'sửa đổi đang hiệu lực'}</Chip>
              {s.source_url && <a href={s.source_url} target="_blank" rel="noreferrer" className="ml-2 text-emerald-800 hover:underline">↗</a>}
              <p className="text-slate-600">{s.title}</p>
            </li>
          ))}
        </ol>
      )}

      {blocked.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs">
          <p className="font-semibold text-slate-800">🔒 Có hiệu lực nhưng chưa trích được nội dung — cần thu thập</p>
          <ul className="mt-1 list-inside list-disc text-slate-600">
            {blocked.map((b, i) => <li key={i}><span className="font-mono">{b.document}</span>{b.reason ? ` — ${b.reason}` : ''}</li>)}
          </ul>
        </div>
      )}

      {(legal.conditions || []).length > 0 && (
        <ul className="space-y-1 text-xs">
          {legal.conditions.map((c, i) => (
            <li key={i} className="flex gap-2">
              <span className="font-mono">{c.status === 'MET' ? '✓' : c.status === 'NOT_MET' ? '✕' : '?'}</span>
              <span>
                <span className="text-slate-800">{c.criterion}</span>
                {c.source_clause && <span className="ml-1 font-mono text-slate-500">({c.source_clause})</span>}
                {c.reason && <span className="block text-slate-500">{c.reason}</span>}
              </span>
            </li>
          ))}
        </ul>
      )}

      {(legal.source_qualifiers || []).length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {legal.source_qualifiers.map((q, i) => <Chip key={i} tone="amber">🛡 {typeof q === 'string' ? q : q.label || JSON.stringify(q)}</Chip>)}
        </div>
      )}
    </div>
  )
}

export function RiskBreakdown({ risk }) {
  if (!risk) return null
  const byName = new Map(risk.components.map((c) => [c.name, c]))
  const groups = [
    { title: '5 thuộc tính bắt buộc', names: ATTRIBUTES.flatMap((a) => a.components) },
    { title: 'Tín hiệu cần lưu ý', names: PENALTIES.map((p) => p.key) },
  ]
  const maxWidth = Math.max(...risk.components.map((c) => c.max_score))
  return (
    <div className="space-y-4">
      {groups.map((g) => (
        <div key={g.title}>
          <p className="mb-1.5 text-xs font-semibold text-slate-700">{g.title}</p>
          <ul className="space-y-1.5">
            {g.names.map((name) => {
              const c = byName.get(name)
              if (!c) return null
              const ratio = c.max_score ? c.score / c.max_score : 0
              const color = ratio === 0 ? 'bg-emerald-400' : ratio >= 0.99 ? 'bg-red-400' : 'bg-amber-400'
              return (
                <li key={name} className="grid grid-cols-[150px_1fr_52px] items-center gap-2 text-xs" title={c.reason}>
                  <span className="truncate font-mono text-slate-600">{name}</span>
                  <span className="relative h-2 rounded-full bg-slate-100" style={{ width: `${(c.max_score / maxWidth) * 100}%` }}>
                    <span className={`absolute inset-y-0 left-0 rounded-full ${color}`} style={{ width: `${ratio * 100}%` }} />
                  </span>
                  <span className="text-right font-mono text-slate-500">{c.score}/{c.max_score}</span>
                </li>
              )
            })}
          </ul>
        </div>
      ))}
      <p className="text-[11px] text-slate-500">
        Tổng <span className="font-mono">{risk.risk_score}/100</span> · dải <span className="font-mono">{risk.severity}</span> · rubric <span className="font-mono">{risk.rubric_version}</span>
        {risk.requires_human_review && ' · cần người xem xét'} — điểm chỉ dùng để sắp thứ tự ưu tiên, không phải kết luận.
      </p>
    </div>
  )
}
