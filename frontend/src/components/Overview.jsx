import { ReleasePill, STATUS_BAR, STATUS_LABELS, STATUS_ORDER } from './badges.jsx'

/**
 * "Where do I continue?" — not "how good is the score".
 *
 * Every tile is a queue that opens the workbench filtered to those claims.
 * There is no aggregate risk headline, no risk-over-time series and no
 * per-company ranking: the first invites reading a number as a verdict, and the
 * other two describe the upload queue rather than any issuer.
 */

function WorkTile({ label, count, hint, tone = 'slate', onOpen, disabled }) {
  const tones = {
    slate: 'hover:border-slate-400',
    red: 'border-red-200 bg-red-50/60 hover:border-red-400',
    amber: 'border-amber-200 bg-amber-50/60 hover:border-amber-400',
  }
  return (
    <button
      type="button"
      onClick={onOpen}
      disabled={disabled || !count}
      className={`rounded-xl border border-slate-200 bg-white p-4 text-left transition disabled:cursor-default disabled:opacity-60 ${tones[tone]}`}
    >
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-slate-900">{count}</p>
      <p className="mt-1 text-xs text-slate-500">{hint}</p>
      {Boolean(count) && (
        <span className="mt-2 inline-block text-xs font-medium text-emerald-700">Mở danh sách →</span>
      )}
    </button>
  )
}

export default function Overview({ summary, lastRunAt, onOpenQueue }) {
  const s = summary

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold text-slate-900">Tiếp tục công việc</h2>
        {lastRunAt && (
          <p className="text-xs text-slate-500">
            Lần phân tích gần nhất: {lastRunAt.toLocaleString('vi-VN')} · {s.total} tuyên bố ·{' '}
            {s.chunks} đoạn
          </p>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <WorkTile
          label="Claim chưa xử lý"
          count={s.unresolved.length}
          hint="Thiếu ít nhất một thuộc tính bắt buộc"
          onOpen={() => onOpenQueue('unresolved')}
        />
        <WorkTile
          label="Claim thiếu bằng chứng"
          count={s.noEvidence.length}
          hint="Không truy xuất được đoạn nào để đối chiếu"
          onOpen={() => onOpenQueue('noEvidence')}
        />
        <WorkTile
          label="Claim có mâu thuẫn"
          count={s.contradicted.length}
          hint="Có bằng chứng ngược với tuyên bố"
          tone="red"
          onOpen={() => onOpenQueue('contradicted')}
        />
        <WorkTile
          label="Cần người xác nhận"
          count={s.needsConfirmation.length}
          hint="Hệ thống không tự phát hành các trường hợp này"
          tone="amber"
          onOpen={() => onOpenQueue('needsConfirmation')}
        />
      </div>

      {s.corpus && (
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-sm font-semibold text-slate-900">Độ phủ kho tài liệu</h3>
            <span className="font-mono text-sm text-slate-900">{Math.round((s.corpus.coverage || 0) * 100)}%</span>
            <span className="h-2 w-40 rounded-full bg-slate-100"><span className={`block h-2 rounded-full ${s.corpus.sufficient_for_absence ? 'bg-emerald-500' : 'bg-sky-400'}`} style={{ width: `${(s.corpus.coverage || 0) * 100}%` }} /></span>
            <span className="text-xs text-slate-500">{s.corpus.documents} tài liệu · năm {(s.corpus.years || []).join(', ') || '—'}</span>
          </div>
          <p className="mt-2 text-xs text-slate-600">
            {s.corpus.sufficient_for_absence
              ? 'Kho có tài liệu đối chiếu và nguồn độc lập: khi không tìm thấy bằng chứng, hệ thống được phép ghi “chưa được chứng minh trong kho đã kiểm”.'
              : 'Kho chưa đủ để suy ra “không có bằng chứng”: mọi trường hợp không tìm thấy sẽ dừng ở “chưa đủ bằng chứng”.'}
            {(s.corpus.missing || []).length > 0 && <span className="block text-sky-800">Thiếu: {s.corpus.missing.join(' · ')}</span>}
          </p>
        </section>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-900">Tài liệu đang review</h3>
          <ul className="mt-3 divide-y divide-slate-100">
            {s.documents.map((d) => (
              <li key={d.name} className="flex items-center gap-3 py-2">
                <span className="min-w-0 flex-1 truncate text-sm text-slate-800" title={d.name}>
                  {d.name}
                </span>
                <span className="shrink-0 text-xs tabular-nums text-slate-500">
                  {d.unresolved}/{d.total} chưa xong
                </span>
                {d.contradicted > 0 && (
                  <span className="shrink-0 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-800">
                    {d.contradicted} mâu thuẫn
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-900">Thuộc tính thiếu nhiều nhất</h3>
          <p className="mt-1 text-xs text-slate-500">
            Đây là việc có thể sửa ngay trong báo cáo, không phải một chỉ số để ngắm.
          </p>
          <ul className="mt-3 space-y-2.5">
            {s.missingByAttribute.filter((a) => a.count > 0).map((a) => (
              <li key={a.key}>
                <button
                  type="button"
                  onClick={() => onOpenQueue('attribute', a.key)}
                  className="w-full text-left"
                >
                  <div className="flex items-baseline justify-between text-xs">
                    <span className="font-medium text-slate-800">
                      {a.label} <span className="text-slate-400">{a.labelVi}</span>
                    </span>
                    <span className="tabular-nums text-slate-600">
                      {a.count}/{s.total}
                    </span>
                  </div>
                  <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full bg-red-400"
                      style={{ width: `${s.total ? (a.count / s.total) * 100 : 0}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{a.fix}</p>
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-slate-900">Kết quả kiểm chứng</h3>
          <ReleasePill status={s.releaseStatus} />
        </div>
        <ul className="mt-3 space-y-1.5">
          {STATUS_ORDER.filter((st) => s.byStatus[st]).map((status) => {
            const count = s.byStatus[status]
            const width = s.total ? (count / s.total) * 100 : 0
            return (
              <li key={status}>
                <button
                  type="button"
                  onClick={() => onOpenQueue('status', status)}
                  className="grid w-full grid-cols-[190px_1fr_44px] items-center gap-2 rounded px-1 py-0.5 text-left text-xs hover:bg-slate-50"
                >
                  <span className="truncate text-slate-700">{STATUS_LABELS[status] || status}</span>
                  <span className="h-2.5 rounded-full bg-slate-100"><span className={`block h-2.5 rounded-full ${STATUS_BAR[status]}`} style={{ width: `${width}%` }} /></span>
                  <span className="text-right font-mono text-slate-900">{count}</span>
                </button>
              </li>
            )
          })}
        </ul>
        <p className="mt-3 text-xs text-slate-500">
          Tỷ lệ dừng phán đoán: <b className="font-mono">{s.total ? Math.round((s.abstain.length / s.total) * 100) : 0}%</b> — “chưa đủ bằng chứng” là kết quả bình thường của quy trình evidence-first, không phải lỗi; hệ thống dừng lại thay vì suy đoán.
        </p>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-900">Cổng chất lượng</h3>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {s.gates.map((g) => (
            <span
              key={g.gate_id}
              title={`${g.name}: ${g.details}`}
              className={`rounded-md px-2 py-1 font-mono text-[11px] font-semibold ${
                g.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : g.status === 'FAIL' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
              }`}
            >
              {g.gate_id} {g.status === 'PASS' ? '✓' : g.status === 'FAIL' ? '✕' : '◐'}
            </span>
          ))}
        </div>
        <ul className="mt-2 space-y-1">
          {s.gates.filter((g) => g.status !== 'PASS' || g.gate_id === 'G7').map((g) => (
            <li key={g.gate_id} className="text-xs text-slate-600"><b className="font-mono">{g.gate_id}</b> · {g.name} · {g.details}</li>
          ))}
        </ul>
      </section>
    </div>
  )
}
