import { exportUrl, workpaperUrl } from '../api.js'
import { ReleasePill, STATUS_LABELS } from '../components/badges.jsx'
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
  ['json', 'Kết quả đầy đủ (JSON)', 'result.json — mọi tuyên bố, bằng chứng, lập trường, rủi ro, pháp lý, hàng đợi.'],
  ['md', 'Gói bằng chứng (Markdown)', 'evidence_pack.md — bản đọc theo thứ tự tài liệu.'],
  ['manifest', 'Manifest tái lập', 'manifest.json — mã băm đầu vào, cấu hình, phiên bản bộ quy tắc và prompt.'],
  ['audit', 'Nhật ký chạy (JSONL)', 'audit.jsonl — từng bước pipeline đã làm gì, theo thứ tự.'],
]

export default function ExportPage({ runId, runLabel, analysis, summary, reviewStates = {}, reviewDecisions = [] }) {
  const finalized = Object.values(reviewStates).filter((s) => s === 'FINALIZED').length
  const queued = (analysis?.priorities || []).filter((p) => p.in_queue && p.item_type === 'claim').length
  const created = analysis?.manifest?.created_at

  const downloadReviews = () => {
    const blob = new Blob([JSON.stringify({ run_id: runId, states: reviewStates, decisions: reviewDecisions }, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `greenscan-${runId}-reviews.json`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        <section className="rounded-xl border-2 border-emerald-700/30 bg-white p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-800">Bước 3 · Giấy làm việc</p>
          <h3 className="mt-1 text-base font-semibold text-slate-900">Giấy làm việc tiếng Việt, in được</h3>
          <p className="mt-1 text-sm text-slate-600">
            Mục tiêu, phạm vi tài liệu, thủ tục đã làm, hàng đợi soát kèm kết quả và trang nguồn, những gì
            <b> không</b> được kiểm, quyết định của người soát xét và chỗ ký. Nội dung lấy từ phiên đã lưu và
            nhật ký quyết định ở thời điểm mở, nên quyết định vừa ghi sẽ có ngay trong bản in.
          </p>
          {queued > 0 && finalized < queued && (
            <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
              Mới chốt {finalized}/{queued} tuyên bố trong hàng đợi. Giấy làm việc vẫn in được; mục chưa xem sẽ ghi “chưa xem”.
            </p>
          )}
          <div className="mt-4 flex flex-wrap gap-2">
            <a href={workpaperUrl(runId)} target="_blank" rel="noreferrer" className="rounded-lg bg-[#0F3D2E] px-4 py-2 text-sm font-semibold text-white">Mở giấy làm việc</a>
            <a href={workpaperUrl(runId, true)} target="_blank" rel="noreferrer" className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">In / Lưu PDF</a>
          </div>
          <p className="mt-2 text-[11px] text-slate-500">Để có PDF: trong hộp thoại in chọn “Lưu dưới dạng PDF” (Save as PDF).</p>
        </section>

        <details className="rounded-xl border border-slate-200 bg-white p-5">
          <summary className="cursor-pointer text-sm font-semibold text-slate-900">Tệp kỹ thuật (để tái lập hoặc kiểm tra hệ thống)</summary>
          <ul className="mt-3 space-y-2">
            {FILES.map(([f, label, hint]) => (
              <li key={f} className="flex items-start gap-3 rounded-lg border border-slate-200 p-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">{label}</p>
                  <p className="text-xs text-slate-500">{hint}</p>
                </div>
                <a href={exportUrl(runId, f)} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700">Tải xuống</a>
              </li>
            ))}
            <li className="flex items-start gap-3 rounded-lg border border-slate-200 p-3">
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">Quyết định người soát xét (JSON)</p>
                <p className="text-xs text-slate-500">{reviewDecisions.length} quyết định · {finalized} tuyên bố đã chốt — nhật ký chỉ ghi thêm, là nguồn của bộ dữ liệu gold.</p>
              </div>
              <button type="button" onClick={downloadReviews} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700">Tải xuống</button>
            </li>
          </ul>
        </details>
      </div>

      <aside className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-1.5 text-[#0F3D2E]"><Leaf className="h-5 w-5" /><span className="text-sm font-bold">GreenScan</span></div>
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
          <ul className="mt-3 space-y-0.5 text-[11px] text-slate-600">
            {Object.entries(analysis?.summary?.status_counts || {}).map(([k, v]) => <li key={k} className="flex justify-between"><span>{STATUS_LABELS[k] || k}</span><span className="font-mono">{v}</span></li>)}
          </ul>
          <p className="mt-3 text-[10px] leading-relaxed text-slate-500">Kết quả ước lượng mức độ đầy đủ của bằng chứng, không phải kết luận pháp lý.</p>
        </div>
      </aside>
    </div>
  )
}
