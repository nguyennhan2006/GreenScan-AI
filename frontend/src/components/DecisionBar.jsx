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
// Vai trò người soát (storage/reviews.py REVIEWER_ROLES). Nhãn của chính doanh nghiệp bị soát
// được lưu vào vết kiểm toán nhưng không bao giờ dùng để dạy hay chấm mô hình.
const ROLES = [
  { value: '', label: '— vai trò —' },
  { value: 'auditor', label: 'Kiểm toán viên' },
  { value: 'bank', label: 'Ngân hàng / tín dụng' },
  { value: 'internal_audit', label: 'Kiểm toán nội bộ' },
  { value: 'regulator', label: 'Cơ quan quản lý' },
  { value: 'greenscan', label: 'Đội GreenScan' },
  { value: 'reviewed_company', label: 'Doanh nghiệp bị soát' },
  { value: 'other', label: 'Khác' },
]
function loadRole() {
  try { return localStorage.getItem('gs.reviewer.role') || '' } catch { return '' }
}
function saveRole(value) {
  try { localStorage.setItem('gs.reviewer.role', value) } catch { /* không lưu được thì thôi */ }
}

const DECISION_LABEL = {
  CONFIRM: 'Xác nhận', OVERRIDE: 'Ghi đè', ABSTAIN: 'Chưa kết luận',
  REQUEST_EVIDENCE: 'Yêu cầu thêm bằng chứng', REOPEN: 'Mở lại',
}

export default function DecisionBar({ state, history, reviewer, onReviewerChange, onDecide, busy, ruleOptions = [], evidence = [] }) {
  const [comment, setComment] = useState('')
  // Nhãn chỉ chỗ: đoạn nào quyết định kết luận của người soát (feedback-loop-v1, tầng 0).
  const [decisive, setDecisive] = useState([])
  const [quote, setQuote] = useState('')
  const [showPointer, setShowPointer] = useState(false)
  const [role, setRole] = useState(loadRole)
  const [verdict, setVerdict] = useState('')
  const [reason, setReason] = useState('')
  const [ruleRef, setRuleRef] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [fixing, setFixing] = useState(false)

  const finalized = state === 'FINALIZED'
  const style = STATE_STYLE[state] || STATE_STYLE.AI_SUGGESTED
  const ruleReason = OVERRIDE_REASONS.find((r) => r.value === reason)?.rule || false
  const overrideReady = !!verdict && !!reason && (!ruleReason || !!ruleRef.trim())
  const uniqueRules = [...new Map(ruleOptions.map((r) => [r.id, r])).values()]

  const submit = (decision) => {
    if (!reviewer.trim()) return
    const override = decision === 'OVERRIDE'
    const labelled = decision === 'CONFIRM' || override
    onDecide({
      decision,
      comment: comment.trim(),
      reviewer_status: override ? verdict : null,
      override_reason: override ? reason : null,
      rule_ref: override && ruleReason ? ruleRef.trim() : '',
      decisive_chunk_ids: labelled ? decisive : [],
      decisive_quote: labelled ? quote.trim() : '',
      reviewer_role: role,
    })
    setDecisive([])
    setQuote('')
    setComment('')
    setVerdict('')
    setReason('')
    setRuleRef('')
    setFixing(false)
  }

  return (
    <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
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

      <details className="mt-2 text-xs" data-testid="decision-more">
        <summary className="cursor-pointer font-medium text-slate-600">Ghi thêm: vai trò của bạn, đoạn khiến bạn quyết định</summary>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        <select
          value={role}
          onChange={(e) => { setRole(e.target.value); saveRole(e.target.value) }}
          className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
          title="Nhãn của doanh nghiệp bị soát không bao giờ được dùng để dạy mô hình"
        >
          {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
        {!finalized && (
          <button
            type="button"
            onClick={() => setShowPointer((v) => !v)}
            className="text-xs font-medium text-emerald-700 underline-offset-2 hover:underline"
          >
            {showPointer ? 'Ẩn đoạn quyết định' : `Chỉ đoạn quyết định${decisive.length || quote.trim() ? ` (${decisive.length + (quote.trim() ? 1 : 0)})` : ''}`}
          </button>
        )}
      </div>

      {showPointer && !finalized && (
        <div className="mt-2 rounded-lg border border-emerald-200 bg-emerald-50/40 p-2.5 text-xs">
          <p className="text-slate-600">
            Đánh dấu đoạn khiến bạn kết luận như vậy. Hệ thống tự suy ra máy sai ở đâu: đoạn có trong danh sách mà máy vẫn
            kết luận sai là lỗi <b>đọc</b>; đoạn không có trong danh sách là lỗi <b>tìm</b>. Một cú bấm biến nhãn “sai” thành “sai ở đâu”.
          </p>
          <ul className="mt-2 max-h-56 space-y-1 overflow-y-auto">
            {evidence.map((e, i) => (
              <li key={e.chunk_id || i}>
                <label className="flex cursor-pointer gap-2 rounded px-1 py-0.5 hover:bg-white">
                  <input
                    type="checkbox"
                    checked={decisive.includes(e.chunk_id)}
                    onChange={(ev) => setDecisive((cur) => ev.target.checked ? [...cur, e.chunk_id] : cur.filter((c) => c !== e.chunk_id))}
                  />
                  <span className="text-slate-500">#{i + 1}</span>
                  <span className="text-slate-800">{(e.text || '').slice(0, 160)}{(e.text || '').length > 160 ? '…' : ''}</span>
                  <span className="ml-auto shrink-0 text-[11px] text-slate-400">{e.source_name}{e.page ? ` tr. ${e.page}` : ''}</span>
                </label>
              </li>
            ))}
            {evidence.length === 0 && <li className="text-slate-500">Máy không đưa ra đoạn bằng chứng nào cho tuyên bố này.</li>}
          </ul>
          <textarea
            value={quote}
            onChange={(e) => setQuote(e.target.value)}
            rows={2}
            placeholder="Đoạn quyết định không có trong danh sách? Dán trích dẫn (kèm nguồn, trang)."
            className="mt-2 w-full rounded-lg border border-slate-300 px-2 py-1.5 text-xs"
          />
        </div>
      )}
        <p className="mt-2 text-slate-500">
          Chỉ “Xác nhận” và “Ghi đè” trở thành nhãn chuẩn. “Chưa kết luận” và “Yêu cầu thêm bằng chứng” là
          kết quả hợp lệ của quy trình nhưng không phải nhãn. Khi ghi đè vì quy tắc không hợp, nhãn chỉ chuyển cho
          người giữ bộ quy tắc xem xét, không dùng để dạy mô hình.
        </p>
      </details>

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
            className={`rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-40 ${finalized || busy || !reviewer.trim() ? '' : 'gs-halo'}`}
          >
            Xác nhận gợi ý của máy
          </button>

          <button
            type="button"
            onClick={() => setFixing((v) => !v)}
            aria-expanded={fixing}
            className={`rounded-lg border px-3 py-1.5 text-sm font-semibold ${fixing ? 'border-slate-700 bg-slate-100 text-slate-900' : 'border-slate-400 text-slate-800 hover:bg-slate-50'}`}
          >
            Máy sai, tôi sửa
          </button>

          {fixing && (
          <div className="order-last flex basis-full flex-wrap items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 p-2">
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
          )}

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

    </section>
  )
}
