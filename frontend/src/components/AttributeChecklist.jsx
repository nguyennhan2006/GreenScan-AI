/**
 * The five-attribute checklist — a design-system primitive.
 *
 * One component, three densities, so the same rubric reads identically on a
 * claim card, in claim detail and in authoring mode. If these ever diverge,
 * a reviewer has to re-learn the rubric per screen.
 *
 *   variant="dots"  compact row for cards and lists
 *   variant="list"  full checklist with hints — claim detail
 *   variant="fix"   checklist plus the concrete remedy — authoring mode
 */

const STATE = {
  present: { dot: 'bg-emerald-500', ring: 'ring-emerald-500/30', text: 'text-slate-900', label: 'Có' },
  partial: { dot: 'bg-amber-500', ring: 'ring-amber-500/30', text: 'text-slate-900', label: 'Một phần' },
  missing: { dot: 'bg-red-500', ring: 'ring-red-500/30', text: 'text-red-900', label: 'Thiếu' },
  unknown: { dot: 'bg-slate-300', ring: 'ring-slate-300/30', text: 'text-slate-500', label: 'Chưa đánh giá' },
}

export function AttributeDots({ attributes, className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1 ${className}`}>
      {attributes.map((a) => (
        <span
          key={a.key}
          title={`${a.label} — ${STATE[a.state].label}`}
          className={`h-1.5 w-4 rounded-full ${STATE[a.state].dot}`}
        />
      ))}
    </span>
  )
}

export default function AttributeChecklist({ attributes, penalties, variant = 'list' }) {
  if (variant === 'dots') return <AttributeDots attributes={attributes} />

  const showFix = variant === 'fix'

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Thuộc tính bắt buộc</h3>
        <span className="text-xs text-slate-500">
          {attributes.filter((a) => a.state === 'present').length}/{attributes.length} đủ
        </span>
      </div>

      <ul className="mt-3 space-y-2.5">
        {attributes.map((a) => {
          const s = STATE[a.state]
          return (
            <li key={a.key} className="flex items-start gap-2.5">
              <span
                className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ring-4 ${s.dot} ${s.ring}`}
                aria-hidden="true"
              />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2">
                  <span className={`text-sm font-medium ${s.text}`}>{a.label}</span>
                  <span className="text-xs text-slate-400">{a.labelVi}</span>
                  <span className="ml-auto text-xs text-slate-500">{s.label}</span>
                </div>
                <p className="mt-0.5 text-xs text-slate-500">{a.hint}</p>
                {showFix && a.state !== 'present' && (a.action || a.fix) && (
                  <p className="mt-1 rounded bg-emerald-50 px-2 py-1 text-xs leading-relaxed text-emerald-900">
                    <b>Việc cần làm:</b> {a.action || a.fix}
                  </p>
                )}
              </div>
            </li>
          )
        })}
      </ul>

      {penalties?.some((p) => p.active) && (
        <div className="mt-4 border-t border-slate-100 pt-3">
          <h4 className="text-xs font-semibold text-slate-700">Tín hiệu cần lưu ý</h4>
          <ul className="mt-1.5 space-y-1">
            {penalties.filter((p) => p.active).map((p) => (
              <li key={p.key} className="flex items-center gap-2 text-xs text-slate-700">
                <span className="h-1.5 w-1.5 rounded-full bg-orange-500" aria-hidden="true" />
                {p.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
