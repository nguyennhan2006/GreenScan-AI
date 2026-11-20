import { STATUS_LABELS } from './badges.jsx'

/**
 * Tiền lệ (feedback-loop-v1, tầng 2): những tuyên bố tương tự mà người soát đã chốt.
 * Hiện bên cạnh kết luận, không bao giờ đổi kết luận. Một tiền lệ mà người soát đã ghi đè máy
 * có thể đưa tuyên bố vào hàng soát (raised_by: precedent:...).
 */

const STAGE = {
  reading: 'máy có đoạn đúng nhưng đọc sai',
  retrieval: 'máy không tìm thấy đoạn quyết định',
  rule: 'quy tắc không hợp',
  none: 'máy đúng',
  unknown: 'chưa rõ chỗ sai',
}
const RAISED = {
  org_rule: 'quy tắc nội bộ yêu cầu nâng ưu tiên',
  precedent: 'người soát từng ghi đè máy ở tuyên bố rất giống',
  active_learning: 'nhãn của câu này dạy hệ thống nhiều nhất',
}

export function QueueReasons({ priority }) {
  if (!priority) return null
  const raised = priority.raised_by || []
  const learning = priority.learning
  if (!raised.length && !learning) return null
  return (
    <div className="space-y-1 rounded-lg border border-sky-200 bg-sky-50/60 px-3 py-2 text-xs text-sky-900">
      {raised.length > 0 && (
        <p>
          <b>Được đưa vào hàng soát vì:</b>{' '}
          {[...new Set(raised.map((r) => r.split(':')[0]))].map((k) => RAISED[k] || k).join('; ')}.
          <span className="text-sky-700"> Điểm ưu tiên và thứ hạng giữ nguyên; chỉ thêm chỗ trong hàng, không bỏ chỗ nào.</span>
        </p>
      )}
      {learning && (
        <p>
          <b>Giá trị học {Math.round(learning.value * 100)}%:</b> {learning.reasons.join('; ')}.
        </p>
      )}
    </div>
  )
}

export default function Precedents({ cards }) {
  if (!cards?.length) {
    return <p className="text-xs text-slate-500">Chưa có tuyên bố tương tự nào được người soát chốt. Quyết định của bạn ở dưới sẽ thành tiền lệ cho lần sau.</p>
  }
  return (
    <ul className="space-y-2">
      {cards.map((c) => (
        <li key={`${c.run_id}-${c.claim_id}`} className={`rounded-lg border p-2.5 text-xs ${c.overridden ? 'border-amber-300 bg-amber-50/50' : 'border-slate-200'}`}>
          <p className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">giống {Math.round(c.similarity * 100)}%</span>
            {c.overridden ? (
              <span className="font-semibold text-amber-900">
                Người soát đã sửa: {STATUS_LABELS[c.ai_status] || c.ai_status} → {STATUS_LABELS[c.label] || c.label}
              </span>
            ) : (
              <span className="font-semibold text-emerald-800">Người soát xác nhận: {STATUS_LABELS[c.label] || c.label}</span>
            )}
            {c.error_stage && c.error_stage !== 'none' && <span className="text-slate-500">({STAGE[c.error_stage] || c.error_stage})</span>}
          </p>
          <p className="mt-1 text-slate-800">“{c.claim_text}”</p>
          {c.comment && <p className="mt-1 text-slate-600">Lý do: {c.comment}</p>}
          {c.decisive?.length > 0 && (
            <p className="mt-1 text-slate-600">
              Đoạn quyết định: “{(c.decisive[0].text_preview || '').slice(0, 220)}”
              <span className="text-slate-400"> {c.decisive[0].source_name}{c.decisive[0].page ? ` tr. ${c.decisive[0].page}` : ''}</span>
            </p>
          )}
          <p className="mt-1 font-mono text-[11px] text-slate-400">
            {c.reviewer}{c.reviewer_role ? ` (${c.reviewer_role})` : ''} · {c.decided_at ? new Date(c.decided_at).toLocaleDateString('vi-VN') : ''} · phiên {c.run_id?.slice(0, 8)} · từ chung: {(c.shared_words || []).join(', ')}
          </p>
        </li>
      ))}
    </ul>
  )
}
