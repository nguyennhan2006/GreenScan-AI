import ClaimCard from './ClaimCard.jsx'
import { STATUS_LABELS, SEVERITY_LABELS } from './badges.jsx'

const RELEASE_LABELS = {
  RELEASABLE: ['Có thể công bố', 'bg-emerald-100 text-emerald-800 border-emerald-300'],
  PENDING_HUMAN_REVIEW: ['Chờ con người duyệt', 'bg-amber-100 text-amber-800 border-amber-300'],
  BLOCKED: ['Bị chặn', 'bg-red-100 text-red-800 border-red-300'],
}

function StatCard({ label, value, sub }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-sm text-slate-500">{label}</div>
      {sub && <div className="mt-1 text-xs text-slate-400">{sub}</div>}
    </div>
  )
}

export default function ResultsPanel({ analysis, onRecheck, loading }) {
  const { result, suggestions } = analysis
  const { summary } = result
  const [releaseLabel, releaseStyle] =
    RELEASE_LABELS[summary.release_status] || [summary.release_status, 'bg-slate-100 text-slate-700 border-slate-300']

  const riskByClaim = Object.fromEntries(result.risks.map((r) => [r.claim_id, r]))
  const suggestionByClaim = Object.fromEntries((suggestions || []).map((s) => [s.claim_id, s]))
  const totalIssues = (suggestions || []).reduce((acc, s) => acc + s.items.length, 0)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard label="Tài liệu đã phân tích" value={summary.total_documents} />
        <StatCard label="Tuyên bố phát hiện" value={summary.total_claims} />
        <StatCard label="Lỗi & gợi ý sửa" value={totalIssues} />
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <span className={`inline-block rounded-full border px-3 py-1 text-sm font-semibold ${releaseStyle}`}>
            {releaseLabel}
          </span>
          <div className="mt-1 text-sm text-slate-500">Trạng thái phát hành</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-slate-600">
        {Object.entries(summary.status_counts).map(([status, count]) => (
          <span key={status} className="rounded-full bg-slate-100 px-3 py-1">
            {STATUS_LABELS[status] || status}: <b>{count}</b>
          </span>
        ))}
        {Object.entries(summary.severity_counts).map(([severity, count]) => (
          <span key={severity} className="rounded-full bg-slate-100 px-3 py-1">
            {SEVERITY_LABELS[severity] || severity}: <b>{count}</b>
          </span>
        ))}
      </div>

      <div className="space-y-3">
        <h3 className="text-lg font-bold text-slate-800">Kết quả từng tuyên bố</h3>
        {result.verifications.map((verification) => (
          <ClaimCard
            key={verification.claim.claim_id}
            verification={verification}
            risk={riskByClaim[verification.claim.claim_id]}
            suggestion={suggestionByClaim[verification.claim.claim_id]}
            onRecheck={onRecheck}
            loading={loading}
          />
        ))}
      </div>

      <details className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">
          Cổng kiểm soát chất lượng ({result.quality_gates.filter((g) => g.passed).length}/{result.quality_gates.length} đạt)
        </summary>
        <div className="mt-3 space-y-2">
          {result.quality_gates.map((gate) => (
            <div key={gate.gate_id} className="flex items-start gap-2 text-sm">
              <span>{gate.passed ? '✅' : gate.status === 'PENDING_HUMAN_REVIEW' ? '⏳' : '❌'}</span>
              <div>
                <span className="font-medium text-slate-700">{gate.name}</span>
                <span className="ml-2 text-slate-500">{gate.details}</span>
              </div>
            </div>
          ))}
        </div>
      </details>

      <p className="text-xs text-slate-400">
        Run ID: {result.run_id} · pipeline {result.manifest.pipeline_version} · Hệ thống ước lượng rủi ro
        greenwashing, không phải kết luận pháp lý.
      </p>
    </div>
  )
}
