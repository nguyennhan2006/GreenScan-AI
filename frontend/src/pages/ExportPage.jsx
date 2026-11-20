import { useState } from 'react'
import { exportUrl, workpaperUrl } from '../api.js'
import { onward, stepPath } from '../lib/flow.js'
import { ReleasePill, STATUS_LABELS } from '../components/badges.jsx'
import NextStep from '../components/NextStep.jsx'
import { Leaf } from '../components/Shell.jsx'
import { formatDateTime, shortId } from '../lib/format.js'

/**
 * Step 3: the working paper.
 *
 * What an auditor files is the working paper -- objective, scope, procedure,
 * the queue as worked, each result with its page, what was not examined and
 * who decided what. The server renders it in Vietnamese from the saved run and
 * the review trail; the browser's print dialog turns it into the PDF. The raw
 * artifacts stay available underneath for whoever needs to re-run or audit the
 * system itself.
 */

const FILES = [
  ['json', 'Kết quả đầy đủ (tệp dữ liệu .json)', 'result.json — mọi tuyên bố, bằng chứng, quan hệ bằng chứng – tuyên bố, mức cần chú ý, pháp lý, hàng đợi.'],
  ['md', 'Gói bằng chứng (bản văn bản .md)', 'evidence_pack.md — bản đọc theo thứ tự tài liệu.'],
  ['manifest', 'Phiếu tái lập kết quả', 'manifest.json — mã băm đầu vào, cấu hình, phiên bản bộ quy tắc và lời nhắc gửi mô hình.'],
  ['audit', 'Nhật ký các bước (.jsonl)', 'audit.jsonl — từng bước của quy trình phân tích đã làm gì, theo thứ tự.'],
]

export default function ExportPage({ runId, runLabel, analysis, summary, reviewStates = {}, reviewDecisions = [] }) {
  const finalized = Object.values(reviewStates).filter((s) => s === 'FINALIZED').length
  const queued = (analysis?.priorities || []).filter((p) => p.in_queue && p.item_type === 'claim').length
  const created = analysis?.manifest?.created_at
  const [opened, setOpened] = useState(false)   // the bar says “done” only after the working paper was actually opened

  const downloadReviews = () => {
    const blob = new Blob([JSON.stringify({ run_id: runId, states: reviewStates, decisions: reviewDecisions }, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `greenscan-${runId}-reviews.json`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const pending = queued > 0 && finalized < queued

  return (
    <div className="space-y-4">
    {opened ? (
      <NextStep step={4} done action={onward('export', runId)}>
        Đã đi hết 4 bước của một phiên. Muốn xem thêm: mở một phiên khác trong <b>Lịch sử phân tích</b>, ví dụ phiên có bộ quy tắc nội bộ của ngân hàng.
      </NextStep>
    ) : (
      <NextStep step={4} action={{ label: 'Mở giấy làm việc →', onClick: () => { window.open(workpaperUrl(runId), '_blank', 'noopener'); setOpened(true) } }}
        alt={pending ? { label: 'về hàng đợi soát nốt', to: stepPath('queue', runId) } : null}>
        Bước cuối: mở giấy làm việc (trang mới) để xem, hoặc <b>In / Lưu PDF</b> để lưu hồ sơ.
        {pending ? <> Mới chốt {finalized}/{queued} tuyên bố: mục chưa chốt sẽ ghi “chưa xem”.</> : null}
      </NextStep>
    )}
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        <section className="rounded-xl border-2 border-emerald-700/30 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-900">Giấy làm việc tiếng Việt, in được</h3>
          <p className="mt-1 text-sm text-slate-600">
            Gồm mục tiêu, phạm vi tài liệu, thủ tục đã làm, hàng đợi soát kèm kết quả và trang nguồn, những gì
            <b> không</b> được kiểm, quyết định của người soát xét và chỗ ký.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <a href={workpaperUrl(runId)} target="_blank" rel="noreferrer" onClick={() => setOpened(true)} className="rounded-lg bg-[#047857] px-4 py-2 text-sm font-semibold text-white">Mở giấy làm việc</a>
            <a href={workpaperUrl(runId, true)} target="_blank" rel="noreferrer" onClick={() => setOpened(true)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">In / Lưu PDF</a>
          </div>
          <p className="mt-2 text-xs text-slate-500">Để có PDF: trong hộp thoại in chọn “Lưu dưới dạng PDF” (Save as PDF).</p>
          <a href={exportUrl(runId, 'csv')} className="mt-3 inline-block rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Tải bảng hàng đợi (CSV, mở bằng Excel)</a>
        </section>

        <details className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-5">
          <summary className="cursor-pointer text-sm font-semibold text-slate-900">Tệp kỹ thuật (để tái lập hoặc kiểm tra hệ thống)</summary>
          <ul className="mt-3 space-y-2">
            {FILES.map(([f, label, hint]) => (
              <li key={f} className="flex items-start gap-3 rounded-lg border border-slate-200 p-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">{label}</p>
                  <p className="text-xs text-slate-500">{hint}</p>
                </div>
                <a href={exportUrl(runId, f)} download={`${runId}_${f === 'md' ? 'evidence_pack.md' : f === 'audit' ? 'audit.jsonl' : `${f}.json`}`} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700">Tải xuống</a>
              </li>
            ))}
            <li className="flex items-start gap-3 rounded-lg border border-slate-200 p-3">
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">Quyết định người soát xét (tệp dữ liệu .json)</p>
                <p className="text-xs text-slate-500">{reviewDecisions.length} quyết định · {finalized} tuyên bố đã chốt — nhật ký chỉ ghi thêm, là nguồn của bộ dữ liệu gold.</p>
              </div>
              <button type="button" onClick={downloadReviews} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700">Tải xuống</button>
            </li>
          </ul>
        </details>
      </div>

      <aside className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-5">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-1.5 text-[#047857]"><Leaf className="h-5 w-5" /><span className="text-sm font-bold">GreenScan</span></div>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Hồ sơ sàng lọc tuyên bố môi trường</p>
          <p className="mt-1 text-base font-semibold text-slate-900">{runLabel || 'Phiên chưa đặt tên'}</p>
          <p className="font-mono text-xs text-slate-500">phiên {shortId(runId, 16)}</p>
          <dl className="mt-3 space-y-1 text-xs">
            <div className="flex justify-between"><dt className="text-slate-500">Tạo lúc</dt><dd>{formatDateTime(created)}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Đơn vị</dt><dd>{(analysis?.entity || []).join(', ') || '—'}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tài liệu</dt><dd className="font-mono">{analysis?.summary?.total_documents}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Tuyên bố</dt><dd className="font-mono">{analysis?.summary?.total_claims}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Đã chốt</dt><dd className="font-mono">{finalized}/{queued || analysis?.summary?.total_claims}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Trạng thái</dt><dd><ReleasePill status={summary?.releaseStatus} /></dd></div>
          </dl>
          <ul className="mt-3 space-y-0.5 text-xs text-slate-600">
            {Object.entries(analysis?.summary?.status_counts || {}).map(([k, v]) => <li key={k} className="flex justify-between"><span>{STATUS_LABELS[k] || k}</span><span className="font-mono">{v}</span></li>)}
          </ul>
          <p className="mt-3 text-[11px] leading-relaxed text-slate-500">Kết quả ước lượng mức độ đầy đủ của bằng chứng, không phải kết luận pháp lý.</p>
        </div>
      </aside>
    </div>
    </div>
  )
}
