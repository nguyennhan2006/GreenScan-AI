import { useState } from 'react'
import { STATUS_LABELS } from './badges.jsx'

/**
 * Where a human commits, and where the audit trail is written.
 *
 * Every decision is appended, never edited — so the bar shows the current state
 * and the full history rather than a single editable status. A finalized claim
 * must be reopened before it can be decided again, which is what stops a verdict
 * from quietly changing under an auditor.
 */

const STATE_STYLE = {
  AI_SUGGESTED: { label: 'Máy gợi ý', className: 'bg-slate-100 text-slate-700 border-slate-300' },
  HUMAN_REVIEWED: { label: 'Đã có người xem', className: 'bg-amber-100 text-amber-800 border-amber-300' },
  FINALIZED: { label: 'Đã chốt', className: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
}

const VERDICTS = [
  'SUPPORTED', 'PARTIALLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE',
]

// Vì sao máy sai. Lý do quyết định nhãn đi đâu: máy đọc sai thì dạy được mô hình;
// quy tắc không hợp thì chỉ là góp ý cho bộ quy tắc, không bao giờ thành nhãn dạy mô hình
// (storage/reviews.py OVERRIDE_REASONS).
const OVERRIDE_REASONS = [
  { value: 'MODEL_MISREAD', label: 'Máy đọc sai (số, đơn vị, phạm vi, chủ thể)', rule: false },
  { value: 'EVIDENCE_MISSED', label: 'Máy bỏ sót hoặc chọn sai bằng chứng có trong kho', rule: false },
  { value: 'RULE_NOT_APPLICABLE', label: 'Quy tắc đúng nhưng không áp dụng cho doanh nghiệp hoặc trường hợp này', rule: true },
  { value: 'RULE_WRONG', label: 'Quy tắc sai hoặc lỗi thời, cần sửa', rule: true },
]
const REASON_LABEL = Object.fromEntries(OVERRIDE_REASONS.map((r) => [r.value, r.label]))
function reasonNote(h) {
  if (!h.override_reason) return ''
  const reason = REASON_LABEL[h.override_reason] || h.override_reason
  const rule = h.rule_ref ? '; quy tắc ' + h.rule_ref : ''
  return ' (lý do: ' + reason + rule + ')'
}
const DECISION_LABEL = {
  CONFIRM: 'Xác nhận', OVERRIDE: 'Ghi đè', ABSTAIN: 'Chưa kết luận',
  REQUEST_EVIDENCE: 'Yêu cầu thêm bằng chứng', REOPEN: 'Mở lại',
}

export default function DecisionBar({ state, history, reviewer, onReviewerChange, onDecide, busy, ruleOptions = [] }) {
  const [comment, setComment] = useState('')
  const [verdict, setVerdict] = useState('')
  const [reason, setReason] = useState('')
  const [ruleRef, setRuleRef] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  const finalized = state === 'FINALIZED'
  const style = STATE_STYLE[state] || STATE_STYLE.AI_SUGGESTED
  const ruleReason = OVERRIDE_REASONS.find((r) => r.value === reason)?.rule || false
  const overrideReady = !!verdict && !!reason && (!ruleReason || !!ruleRef.trim())
  const uniqueRules = [...new Map(ruleOptions.map((r) => [r.id, r])).values()]

  const submit = (decision) => {
    if (!reviewer.trim()) return
    const override = decision === 'OVERRIDE'
    onDecide({
      decision,
      comment: comment.trim(),
      reviewer_status: override ? verdict : null,
      override_reason: override ? reason : null,
      rule_ref: override && ruleReason ? ruleRef.trim() : '',
    })
    setComment('')
    setVerdict('')
    setReason('')
    setRuleRef('')
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
              <span className="font-medium text-slate-800">{DECISION_LABEL[h.decision] || h.decision}</span>
              {h.reviewer_status ? ` → ${STATUS_LABELS[h.reviewer_status] || h.reviewer_status}` : ''}
              {reasonNote(h)}
              {' · '}{h.reviewer} ·{' '}
              {new Date(h.decided_at).toLocaleString('vi-VN')}
              <span className="text-slate-400"> ({STATE_STYLE[h.previous_state]?.label || h.previous_state} → {STATE_STYLE[h.new_state]?.label || h.new_state})</span>
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
            Tuyên bố đã chốt. Mở lại nếu có bằng chứng mới.
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
            Xác nhận gợi ý của máy
          </button>

          <div className="flex items-center gap-1.5">
            <select
              value={verdict}
              onChange={(e) => setVerdict(e.target.value)}
              className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
            >
              <option value="">— chọn kết luận thay thế —</option>
              {VERDICTS.map((v) => <option key={v} value={v}>{STATUS_LABELS[v] || v}</option>)}
            </select>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="max-w-[16rem] rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
              title="Lý do quyết định nhãn này có được dùng để dạy mô hình hay không"
            >
              <option value="">— vì sao máy sai —</option>
              {OVERRIDE_REASONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
            {ruleReason && (
              <>
                <input
                  value={ruleRef}
                  onChange={(e) => setRuleRef(e.target.value)}
                  list="decision-rule-options"
                  placeholder="Quy tắc nào? (mã hoặc mô tả)"
                  className="w-44 rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
                />
                <datalist id="decision-rule-options">
                  {uniqueRules.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}
                </datalist>
              </>
            )}
            <button
              type="button"
              disabled={busy || !reviewer.trim() || !overrideReady}
              onClick={() => submit('OVERRIDE')}
              className="rounded-lg border border-slate-400 px-3 py-1.5 text-sm font-semibold text-slate-800 hover:bg-slate-50 disabled:opacity-40"
              title="Ghi đè khi gợi ý của máy sai"
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
            Chưa kết luận
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
        Chỉ “Xác nhận” và “Ghi đè” trở thành nhãn chuẩn. “Chưa kết luận” và “Yêu cầu thêm bằng chứng” là
        kết quả hợp lệ của quy trình nhưng không phải nhãn — coi “chưa kết luận được” là một
        phán quyết sẽ dạy sai cho mô hình sau này. Khi ghi đè vì quy tắc không hợp, nhãn chỉ chuyển cho
        người giữ bộ quy tắc xem xét, không dùng để dạy mô hình, để một ngoại lệ của một doanh nghiệp không
        thành thói quen sai cho mọi doanh nghiệp.
      </p>
    </section>
  )
}
