import { useEffect, useState } from 'react'
import { feedbackProposals, feedbackSummary, secondReviewSample, submitQA } from '../api.js'
import { STATUS_LABELS } from '../components/badges.jsx'

/**
 * Học từ phản hồi (feedback-loop-v1). Hệ thống khôn lên theo từng phiên bản đã đo và đã duyệt,
 * không theo từng cú bấm: trang này cho thấy nhãn đã có, chỗ máy sai, bộ đo GS-Feedback, độ đồng
 * thuận giữa hai người soát, phiếu đề xuất sửa luật và các mô hình đang thách đấu.
 */

const STAGE = {
  none: 'Máy đúng (xác nhận)',
  reading: 'Đọc sai: có đoạn đúng mà vẫn kết luận sai',
  retrieval: 'Tìm sai: không thấy đoạn quyết định',
  rule: 'Quy tắc không hợp',
  unknown: 'Chưa rõ chỗ sai',
}
const STATUSES = ['SUPPORTED', 'PARTIALLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE']

function Card({ title, children, note }) {
  return (
    <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4 text-xs">
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      {note && <p className="mt-1 text-slate-500">{note}</p>}
      <div className="mt-3">{children}</div>
    </section>
  )
}

export default function FeedbackPage({ reviewer }) {
  const [summary, setSummary] = useState(null)
  const [sheet, setSheet] = useState(null)
  const [sample, setSample] = useState(null)
  const [error, setError] = useState(null)
  const [qaMsg, setQaMsg] = useState(null)

  const load = () => feedbackSummary().then(setSummary).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  if (error) return <p className="text-sm text-red-700">Không đọc được dữ liệu phản hồi: {error}</p>
  if (!summary) return <p className="text-sm text-slate-500">Đang đọc…</p>
  const s = summary.stats
  const ag = summary.agreement

  return (
    <div className="space-y-4">
      <p className="rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
        Hệ thống <b>không tự học sau mỗi cú bấm</b>. Quyết định của người soát thành nhãn; nhãn thành bài kiểm, tiền lệ,
        đề xuất sửa luật và dữ liệu huấn luyện. Mọi thay đổi kết luận phải qua đo trước-sau và người duyệt ký (D-2026-10-16-01).
      </p>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Nhãn đã có" note="Chỉ “Xác nhận” và “Ghi đè” đã chốt là nhãn. Nhãn của doanh nghiệp bị soát và ca hai người soát bất đồng chưa phân xử bị loại khỏi huấn luyện.">
          <dl className="grid grid-cols-2 gap-2">
            <dt className="text-slate-500">Quyết định</dt><dd className="font-semibold">{s.total_decisions}</dd>
            <dt className="text-slate-500">Nhãn chuẩn</dt><dd className="font-semibold">{s.gold_records}</dd>
            <dt className="text-slate-500">Có chỉ đoạn quyết định</dt><dd className="font-semibold">{s.pointer_labels ?? 0}</dd>
            <dt className="text-slate-500">Dùng được sau khi lọc</dt><dd className="font-semibold">{summary.clean_labels}</dd>
            <dt className="text-slate-500">Tỷ lệ máy bị ghi đè</dt><dd className="font-semibold">{s.ai_override_rate == null ? '—' : `${Math.round(s.ai_override_rate * 100)}%`}</dd>
          </dl>
          <ul className="mt-3 space-y-1">
            {Object.entries(s.gold_by_stage || {}).map(([k, v]) => (
              <li key={k} className="flex justify-between"><span>{STAGE[k] || k}</span><span className="font-mono">{v}</span></li>
            ))}
          </ul>
        </Card>

        <Card title="GS-Feedback: bánh cóc chống quên" note="Mỗi quyết định đã chốt thành một ca kiểm trên đúng bằng chứng người soát đã thấy. Ca đã qua không được hỏng lại ở phiên bản sau. Chạy: quantum-agent feedback-bench.">
          <p><b>{summary.ratchet.size}</b> ca đang được bánh cóc giữ.</p>
          <ul className="mt-2 space-y-1">
            {summary.ratchet.history.map((h) => (
              <li key={h.at} className="text-slate-600">{new Date(h.at).toLocaleString('vi-VN')}: +{h.added.length} ca (tổng {h.size}){h.note ? ` — ${h.note}` : ''}</li>
            ))}
          </ul>
        </Card>

        <Card title="Hai người soát: độ đồng thuận" note="Mỗi tháng lấy mẫu 10% nhãn đã chốt cho người thứ hai soát mù. Ca bất đồng chờ trọng tài và không vào huấn luyện.">
          <p>Đã soát hai lần: <b>{ag.double_reviewed}</b> · đồng ý: <b>{ag.agree}</b> · kappa: <b>{ag.kappa ?? '—'}</b> · chờ trọng tài: <b>{ag.unresolved.length}</b></p>
          <button type="button" onClick={() => secondReviewSample().then(setSample).catch((e) => setQaMsg(e.message))}
            className="mt-2 rounded-lg border border-slate-400 px-3 py-1 font-semibold">Lấy mẫu tháng này</button>
          {qaMsg && <p className="mt-2 text-slate-700">{qaMsg}</p>}
          {sample && (
            <ul className="mt-2 space-y-1.5">
              {sample.sample.length === 0 && <li className="text-slate-500">Mẫu tháng này rỗng (chưa đủ nhãn).</li>}
              {sample.sample.map((x) => (
                <li key={`${x.run_id}-${x.claim_id}`} className="rounded border border-slate-200 p-2">
                  <p className="text-slate-800">“{x.claim_text}”</p>
                  <p className="mt-1 text-slate-500">Người soát đầu: {x.first_reviewer}. Kết luận của bạn (không xem kết luận đầu):</p>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {STATUSES.map((st) => (
                      <button key={st} type="button" disabled={!reviewer}
                        onClick={() => submitQA({ run_id: x.run_id, claim_id: x.claim_id, reviewer, status: st, kind: 'second_review' })
                          .then(() => { setQaMsg('Đã ghi lần soát thứ hai.'); load() }).catch((e) => setQaMsg(e.message))}
                        className="rounded border border-slate-300 px-2 py-0.5">{STATUS_LABELS[st] || st}</button>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          )}
          {ag.unresolved.length > 0 && (
            <ul className="mt-3 space-y-1">
              {ag.unresolved.map((d) => (
                <li key={`${d.run_id}-${d.claim_id}`} className="text-slate-700">
                  “{(d.claim_text || '').slice(0, 90)}”: {d.first_reviewer} → {STATUS_LABELS[d.first] || d.first}, {d.second_reviewer} → {STATUS_LABELS[d.second] || d.second}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Mô hình thách đấu" note="Mô hình mới chạy ngầm, chỉ thay mô hình cũ khi hơn trên tập giữ lại, không thêm lỗi vu oan hay bỏ lọt, và có người khác ký duyệt.">
          {summary.models.length === 0 && <p className="text-slate-500">Chưa có mô hình nào. Chạy quantum-agent feedback-dataset rồi feedback-train.</p>}
          <ul className="space-y-2">
            {summary.models.map((m) => (
              <li key={m.model_id} className="rounded border border-slate-200 p-2">
                <p className="font-semibold">{m.model_id} <span className="font-normal text-slate-500">({m.kind}, {m.status}{m.approved_by ? `, duyệt: ${m.approved_by}` : ''})</span></p>
                <p className="mt-1 text-slate-600">macro-F1: luật {m.champion?.macro_f1 ?? '—'} · mô hình {m.challenger?.macro_f1 ?? '—'} · SUPPORTS sai: {m.champion?.false_supports} → {m.challenger?.false_supports} · CONTRADICTS sai: {m.champion?.false_contradicts} → {m.challenger?.false_contradicts}</p>
                <ul className="mt-1 list-disc pl-5 text-slate-500">{(m.gate?.reasons || []).map((r) => <li key={r}>{r}</li>)}</ul>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card title="Phiếu đề xuất từ phản hồi" note="Máy đào luật gom các lần ghi đè thành đề xuất: cụm từ lập trường, ngoại lệ quy tắc, từ đồng nghĩa cho truy xuất, quy tắc nội bộ nháp. Không đề xuất nào tự có hiệu lực.">
        <button type="button" onClick={() => feedbackProposals().then(setSheet).catch((e) => setError(e.message))}
          className="rounded-lg border border-slate-400 px-3 py-1 font-semibold">Tạo phiếu</button>
        {sheet && <pre className="mt-3 max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 font-mono text-xs text-slate-800">{sheet.markdown}</pre>}
      </Card>
    </div>
  )
}
