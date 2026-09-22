import { useState } from 'react'

/**
 * Where a human commits, and where the audit trail is written.
 *
 * Every decision is appended, never edited — so the bar shows the current state
 * and the full history rather than a single editable status. A finalized claim
 * must be reopened before it can be decided again, which is what stops a verdict
 * from quietly changing under an auditor.
 */

const STATE_STYLE = {
  AI_SUGGESTED: { label: 'AI đề xuất', className: 'bg-slate-100 text-slate-700 border-slate-300' },
  HUMAN_REVIEWED: { label: 'Đã có người xem', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  FINALIZED: { label: 'Đã chốt', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
}

const VERDICTS = [
  'SUPPORTED', 'PARTIALLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE',
]

export default function DecisionBar({ state, history, reviewer, onReviewerChange, onDecide, busy }) {
  const [comment, setComment] = useState('')
  const [verdict, setVerdict] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  const finalized = state === 'FINALIZED'
  const style = STATE_STYLE[state] || STATE_STYLE.AI_SUGGESTED

  const submit = (decision) => {
    if (!reviewer.trim()) return
    onDecide({
      decision,
      comment: comment.trim(),
      reviewer_status: decision === 'OVERRIDE' ? verdict : null,
    })
    setComment('')
    setVerdict('')
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-sm font-semibold text-slate-900">Quyết định của người xem xét</h3>
        <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${style.className}`}>
          {style.label}
        </span>
        {history.length > 0 && (
          <button
            type="button"
            onClick={() => setShowHistory((v) => !v)}
            className="ml-auto text-xs font-medium text-slate-600 underline-offset-2 hover:underline"
          >
            {showHistory ? 'Ẩn lịch sử' : `Lịch sử (${history.length})`}
          </button>
        )}
      </div>

      {showHistory && (
        <ol className="mt-3 space-y-1.5 border-l-2 border-slate-200 pl-3">
          {history.map((h) => (
            <li key={h.decision_id} className="text-xs text-slate-600">
              <span className="font-medium text-slate-800">{h.decision}</span>
              {h.reviewer_status ? ` → ${h.reviewer_status}` : ''} · {h.reviewer} ·{' '}
              {new Date(h.decided_at).toLocaleString('vi-VN')}
              <span className="text-slate-400"> ({h.previous_state} → {h.new_state})</span>
              {h.comment && <div className="text-slate-500">“{h.comment}”</div>}
            </li>
          ))}
        </ol>
      )}

      <div className="mt-3 grid gap-2 sm:grid-cols-[150px_1fr]">
        <input
          value={reviewer}
          onChange={(e) => onReviewerChange(e.target.value)}
          placeholder="Tên người xem xét"
          className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        />
        <input
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Lý do quyết định (khuyến nghị — đây là phần người sau đọc lại)"
          className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        />
      </div>

      {!reviewer.trim() && (
        <p className="mt-1.5 text-xs text-amber-700">
          Cần tên người xem xét: một vết kiểm toán không có tác giả thì không phải vết kiểm toán.
        </p>
      )}

      {finalized ? (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <p className="text-sm text-slate-600">
            Claim đã chốt. Mở lại nếu có bằng chứng mới.
          </p>
          <button
            type="button"
            disabled={busy || !reviewer.trim()}
            onClick={() => submit('REOPEN')}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
          >
            Mở lại
          </button>
        </div>
      ) : (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button
            type="button"
            disabled={busy || !reviewer.trim()}
            onClick={() => submit('CONFIRM')}
            className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-40"
          >
            Xác nhận kết luận AI
          </button>

          <div className="flex items-center gap-1.5">
            <select
              value={verdict}
              onChange={(e) => setVerdict(e.target.value)}
              className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
            >
              <option value="">— chọn kết luận thay thế —</option>
              {VERDICTS.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
            <button
              type="button"
              disabled={busy || !reviewer.trim() || !verdict}
              onClick={() => submit('OVERRIDE')}
              className="rounded-lg border border-slate-400 px-3 py-1.5 text-sm font-semibold text-slate-800 hover:bg-slate-50 disabled:opacity-40"
              title="Ghi đè khi kết luận của AI sai"
            >
              Ghi đè
            </button>
          </div>

          <button
            type="button"
            disabled={busy || !reviewer.trim()}
            onClick={() => submit('ABSTAIN')}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            title="Bằng chứng thực sự chưa đủ để kết luận"
          >
            Abstain
          </button>
          <button
            type="button"
            disabled={busy || !reviewer.trim()}
            onClick={() => submit('REQUEST_EVIDENCE')}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            title="Có thể kết luận được, nhưng cần tài liệu chưa có trong kho"
          >
            Yêu cầu thêm bằng chứng
          </button>
        </div>
      )}

      <p className="mt-2 text-xs text-slate-500">
        Chỉ “Xác nhận” và “Ghi đè” trở thành nhãn gold. Abstain và Yêu cầu thêm bằng chứng là
        kết quả hợp lệ của quy trình nhưng không phải nhãn — coi “chưa kết luận được” là một
        phán quyết sẽ dạy sai cho mô hình sau này.
      </p>
    </section>
  )
}
