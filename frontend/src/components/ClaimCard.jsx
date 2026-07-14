import { useState } from 'react'
import { StatusBadge, SeverityBadge, riskBarColor } from './badges.jsx'

export default function ClaimCard({ verification, risk, suggestion, onRecheck, loading }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editedText, setEditedText] = useState(verification.claim.text)

  const claim = verification.claim
  const items = suggestion?.items || []

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-start gap-3 p-4 text-left"
      >
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-slate-800">{claim.text}</p>
          <p className="mt-1 text-xs text-slate-500">
            Nguồn: {claim.source_name}
            {claim.source_page != null && ` · trang ${claim.source_page}`} · loại: {claim.claim_type}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={verification.status} />
            {risk && <SeverityBadge severity={risk.severity} />}
            {items.length > 0 && (
              <span className="inline-block rounded-full border border-sky-300 bg-sky-100 px-2.5 py-0.5 text-xs font-semibold text-sky-800">
                {items.length} gợi ý sửa
              </span>
            )}
          </div>
        </div>
        <div className="w-28 shrink-0 text-right">
          <div className="text-2xl font-bold text-slate-800">{risk ? risk.risk_score : '–'}</div>
          <div className="text-xs text-slate-500">điểm rủi ro /100</div>
          {risk && (
            <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                className={`h-full ${riskBarColor(risk.risk_score)}`}
                style={{ width: `${Math.min(100, risk.risk_score)}%` }}
              />
            </div>
          )}
        </div>
      </button>

      {expanded && (
        <div className="space-y-4 border-t border-slate-100 p-4">
          <div>
            <h4 className="mb-1 text-xs font-bold uppercase tracking-wide text-slate-500">Lý do đánh giá</h4>
            <p className="text-sm text-slate-700">{verification.rationale}</p>
          </div>

          {risk && (
            <div>
              <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">Chi tiết chấm điểm</h4>
              <div className="space-y-1.5">
                {risk.components.map((component) => (
                  <div key={component.name} className="flex items-center gap-2 text-sm">
                    <span className="w-56 shrink-0 truncate text-slate-600" title={component.reason}>
                      {component.name}
                    </span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={`h-full ${riskBarColor((component.score / component.max_score) * 100)}`}
                        style={{ width: `${(component.score / component.max_score) * 100}%` }}
                      />
                    </div>
                    <span className="w-14 shrink-0 text-right text-xs text-slate-500">
                      {component.score}/{component.max_score}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {verification.evidence.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                Chứng cứ truy xuất ({verification.evidence.length})
              </h4>
              <div className="space-y-2">
                {verification.evidence.map((evidence) => (
                  <div key={evidence.chunk_id} className="rounded-lg border border-slate-200 bg-slate-50 p-2.5">
                    <p className="text-xs font-semibold text-slate-600">
                      {evidence.citation} · điểm khớp {evidence.score.toFixed(2)}
                      {evidence.suspicious_instruction && (
                        <span className="ml-2 text-red-600">⚠ nghi ngờ prompt injection</span>
                      )}
                    </p>
                    <p className="mt-1 line-clamp-3 text-sm text-slate-700">{evidence.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {items.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                Lỗi phát hiện & gợi ý sửa chữa
              </h4>
              <div className="space-y-2">
                {items.map((item, index) => (
                  <div key={index} className="rounded-lg border border-sky-200 bg-sky-50 p-3">
                    <p className="text-sm font-semibold text-sky-900">⚠ {item.issue}</p>
                    <p className="mt-1 text-sm text-sky-800">💡 {item.recommendation}</p>
                    {item.example_fix && (
                      <p className="mt-1 text-xs italic text-sky-700">Ví dụ: {item.example_fix}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            {editing ? (
              <div className="space-y-2">
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-emerald-300 bg-white p-2 text-sm focus:border-emerald-500 focus:outline-none"
                />
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={loading || !editedText.trim()}
                    onClick={() => onRecheck(claim, editedText)}
                    className="rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {loading ? 'Đang kiểm tra…' : 'Kiểm tra lại bản sửa'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditing(false)}
                    className="rounded-lg border border-slate-300 px-4 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
                  >
                    Hủy
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="rounded-lg border border-emerald-300 px-4 py-1.5 text-sm font-semibold text-emerald-700 hover:bg-emerald-50"
              >
                ✏️ Sửa tuyên bố & kiểm tra lại
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
