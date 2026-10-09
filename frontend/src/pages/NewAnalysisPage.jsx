import { useEffect, useMemo, useRef, useState } from 'react'
import { jobStatus, startAnalysisFiles, startAnalysisText } from '../api.js'
import { Chip } from '../components/badges.jsx'

/**
 * Step 1 of the workflow: choose the documents, then watch the analysis run.
 *
 * Two screens, not three. The old middle step ("configuration") changed
 * nothing -- the pipeline is configured on the server -- so the session label
 * and the company name moved onto the first screen and the second screen is
 * now real progress from a background job, step by step, instead of a spinner
 * with a note saying progress could not be shown.
 *
 * Per file the reviewer answers one plain question -- is this the report to be
 * checked, or a document to check it against? -- and the source type is
 * guessed from the file name, editable. Both matter to the verdict: claims
 * come only from documents to be checked, and legal/external/standard sources
 * count as independent.
 */

const ROLES = [
  ['claim_source', 'Cần kiểm', 'Báo cáo chứa tuyên bố cần kiểm (BCPTBV, BCTN).'],
  ['evidence', 'Đối chiếu', 'Tài liệu để so (BCTC, báo cáo kiểm kê KNK, quyết định của cơ quan nhà nước…).'],
  ['reference', 'Tham khảo', 'Bối cảnh phụ, xếp sau tài liệu đối chiếu.'],
]
const SOURCE_TYPES = [
  ['internal', 'Doanh nghiệp tự phát hành', 'Báo cáo bền vững, báo cáo thường niên.'],
  ['financial', 'Báo cáo tài chính', 'BCTC, thuyết minh.'],
  ['environmental', 'Môi trường', 'Báo cáo kiểm kê KNK, ĐTM, quan trắc.'],
  ['legal', 'Pháp lý — độc lập', 'Quyết định, kết luận thanh tra, bản án.'],
  ['external', 'Bên thứ ba — độc lập', 'Báo cáo đảm bảo, kiểm định, báo chí.'],
  ['standard', 'Tiêu chuẩn — độc lập', 'ISO, GHG Protocol, quy chuẩn.'],
]
const INDEPENDENT = new Set(['legal', 'external', 'standard'])

const PLAN_STEPS = [
  ['validate_inputs', 'Tiếp nhận tài liệu'],
  ['parse_and_ocr_documents', 'Đọc chữ, bảng và trang quét'],
  ['extract_green_claims', 'Tìm tuyên bố môi trường'],
  ['build_hybrid_retrieval_index', 'Lập chỉ mục tìm kiếm'],
  ['retrieve_evidence_per_claim', 'Tìm bằng chứng cho từng tuyên bố'],
  ['verify_claim_evidence_pairs', 'So khớp tuyên bố với bằng chứng'],
  ['check_applicable_law', 'Kiểm chứng, đối chiếu pháp lý, chấm rủi ro'],
  ['score_greenwashing_risk', 'Đọc số liệu công bố, xếp hàng đợi soát'],
  ['apply_quality_gates', 'Kiểm tra cổng chất lượng'],
  ['write_evidence_pack', 'Lưu kết quả'],
]

const EXAMPLE = {
  claim: 'Năm 2024, Tập đoàn đã giảm 30% lượng phát thải khí nhà kính phạm vi 1 và 2 so với năm gốc 2020, đạt 1.250.000 tấn CO2e.',
  evidence: 'Báo cáo kiểm kê khí nhà kính năm 2024 (ISO 14064-1): tổng phát thải phạm vi 1 và 2 của Tập đoàn là 1.480.000 tấn CO2e; năm 2020 là 1.600.000 tấn CO2e.',
}

function fold(name) {
  return name.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/gi, 'd').toLowerCase()
}

/** A first guess from the file name; the reviewer can change it. */
function guessSourceType(name, isFirst) {
  const n = fold(name)
  if (/quyet.?dinh|nghi.?dinh|ket.?luan|thanh.?tra|ban.?an|xu.?phat|decision|judg|court|penalt/.test(n)) return 'legal'
  if (/kiem.?ke|khi.?nha.?kinh|ghg.?inventory|quan.?trac|dtm|danh.?gia.?tac.?dong/.test(n)) return 'environmental'
  if (/dam.?bao|assurance|kiem.?dinh|verification.?statement|bao.?chi|news/.test(n)) return 'external'
  if (/iso|tieu.?chuan|quy.?chuan|standard|protocol/.test(n)) return 'standard'
  if (/bctc|tai.?chinh|financial.?statement/.test(n)) return 'financial'
  return isFirst ? 'internal' : 'financial'
}

function guessRole(name, isFirst) {
  const n = fold(name)
  if (/bcptbv|ben.?vung|sustainab|esg|thuong.?nien|annual/.test(n) && isFirst) return 'claim_source'
  return isFirst ? 'claim_source' : 'evidence'
}

function formatBytes(n) {
  if (!n && n !== 0) return ''
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

function Segmented({ value, onChange, options }) {
  return (
    <span className="inline-flex overflow-hidden rounded-lg border border-slate-300">
      {options.map(([v, label, hint]) => (
        <button
          key={v}
          type="button"
          title={hint}
          onClick={() => onChange(v)}
          className={`px-2.5 py-1 text-xs font-medium ${value === v ? 'bg-[#0F3D2E] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'}`}
        >
          {label}
        </button>
      ))}
    </span>
  )
}

function SourceSelect({ value, onChange }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs">
      {SOURCE_TYPES.map(([v, label, hint]) => <option key={v} value={v} title={hint}>{label}</option>)}
    </select>
  )
}

function Progress({ job, startedAt, onRetry }) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 500)
    return () => clearInterval(t)
  }, [])
  const index = job?.step_index || 0
  const total = job?.total_steps || PLAN_STEPS.length
  const failed = job?.state === 'failed'
  const elapsed = Math.round((now - startedAt) / 1000)
  const minutes = Math.floor(elapsed / 60)
  const seconds = String(elapsed % 60).padStart(2, '0')

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-sm font-semibold text-slate-900">
          {failed ? 'Phân tích thất bại' : job?.state === 'queued' ? 'Đang chờ đến lượt…' : 'Đang phân tích…'}
        </h3>
        <span className="font-mono text-xs text-slate-500">{minutes}:{seconds}</span>
      </div>
      {job?.state === 'queued' && job.queue_position > 0 && (
        <p className="mt-1 text-xs text-slate-500">Có {job.queue_position} phiên đang chạy trước; máy chủ xử lý lần lượt từng phiên.</p>
      )}
      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full transition-all ${failed ? 'bg-red-500' : 'bg-emerald-600'}`} style={{ width: `${Math.max(3, (index / total) * 100)}%` }} />
      </div>
      <ol className="mt-4 space-y-1.5">
        {PLAN_STEPS.map(([key, label], i) => {
          const n = i + 1
          const state = failed && n === index ? 'failed' : n < index || (n === index && job?.state === 'done') ? 'done' : n === index ? 'active' : 'todo'
          return (
            <li key={key} className="flex items-center gap-3 text-sm">
              <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                state === 'done' ? 'bg-emerald-600 text-white' : state === 'active' ? 'animate-pulse bg-[#0F3D2E] text-white' : state === 'failed' ? 'bg-red-600 text-white' : 'bg-slate-200 text-slate-500'
              }`}>{state === 'done' ? '✓' : state === 'failed' ? '!' : n}</span>
              <span className={state === 'todo' ? 'text-slate-400' : 'text-slate-900'}>{label}</span>
              {state === 'active' && job?.detail && <span className="ml-auto text-xs text-emerald-800">{job.detail}</span>}
            </li>
          )
        })}
      </ol>
      {failed && (
        <div className="mt-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800">
          <b>Lỗi:</b> <code className="font-mono text-xs">{job.error}</code>
          <div className="mt-2"><button type="button" onClick={onRetry} className="rounded-lg border border-red-300 bg-white px-3 py-1.5 text-xs font-semibold text-red-800">← Sửa đầu vào và chạy lại</button></div>
        </div>
      )}
      {!failed && <p className="mt-4 text-xs text-slate-500">Một báo cáo bền vững kèm báo cáo thường niên mất khoảng 2 phút trên laptop. Có thể mở trang khác; kết quả được lưu trong Lịch sử.</p>}
    </section>
  )
}

export default function NewAnalysisPage({ onDone, runtime }) {
  const [mode, setMode] = useState('files')
  const [entries, setEntries] = useState([])
  const [claimText, setClaimText] = useState('')
  const [evidenceText, setEvidenceText] = useState('')
  const [label, setLabel] = useState('')
  const [company, setCompany] = useState('')
  const [job, setJob] = useState(null)
  const [startedAt, setStartedAt] = useState(0)
  const [error, setError] = useState(null)
  const timer = useRef(null)

  useEffect(() => () => clearInterval(timer.current), [])

  const addFiles = (list) => {
    setEntries((prev) => [
      ...prev,
      ...Array.from(list || []).map((file, i) => {
        const isFirst = prev.length + i === 0
        return { file, role: guessRole(file.name, isFirst), source_type: guessSourceType(file.name, isFirst) }
      }),
    ])
  }
  const update = (i, patch) => setEntries((prev) => prev.map((e, j) => (j === i ? { ...e, ...patch } : e)))
  const remove = (i) => setEntries((prev) => prev.filter((_, j) => j !== i))

  const documents = useMemo(() => {
    if (mode === 'files') return entries.map((e) => ({ name: e.file.name, role: e.role, source_type: e.source_type }))
    const docs = []
    if (claimText.trim()) docs.push({ name: 'tuyen-bo.txt', text: claimText, role: 'claim_source', source_type: 'internal' })
    if (evidenceText.trim()) docs.push({ name: 'doi-chieu.txt', text: evidenceText, role: 'evidence', source_type: 'environmental' })
    return docs
  }, [mode, entries, claimText, evidenceText])

  const hasClaimSource = documents.some((d) => d.role === 'claim_source')
  const hasEvidence = documents.some((d) => d.role !== 'claim_source')
  const hasIndependent = documents.some((d) => INDEPENDENT.has(d.source_type))
  const canStart = hasClaimSource && !job

  const poll = (jobId) => {
    clearInterval(timer.current)
    timer.current = setInterval(async () => {
      try {
        const status = await jobStatus(jobId)
        setJob(status)
        if (status.state === 'done') {
          clearInterval(timer.current)
          onDone(status.run_id, label)
        } else if (status.state === 'failed') {
          clearInterval(timer.current)
        }
      } catch (exc) {
        clearInterval(timer.current)
        setJob((j) => ({ ...(j || {}), state: 'failed', error: exc.message || 'Mất kết nối với máy chủ.' }))
      }
    }, 1000)
  }

  const start = async () => {
    setError(null)
    setStartedAt(Date.now())
    try {
      const status = mode === 'files'
        ? await startAnalysisFiles(entries.map((e) => e.file), entries.map((e) => e.role), entries.map((e) => e.source_type), label, company)
        : await startAnalysisText(documents, label, company)
      setJob(status)
      poll(status.job_id)
    } catch (exc) {
      setError(exc.message || 'Không gọi được máy chủ phân tích.')
    }
  }

  if (job) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-emerald-800">Bước 1 · Đang phân tích “{label || documents[0]?.name}”</p>
        <Progress job={job} startedAt={startedAt} onRetry={() => setJob(null)} />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-emerald-800">Bước 1 · Chọn tài liệu</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="block text-sm text-slate-700">
            Tên doanh nghiệp <span className="text-slate-400">(không bắt buộc)</span>
            <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Ví dụ: Hòa Phát" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            <span className="mt-1 block text-[11px] text-slate-500">Giúp phân biệt câu doanh nghiệp tự tuyên bố với câu giải thích chung; ghi lên giấy làm việc.</span>
          </label>
          <label className="block text-sm text-slate-700">
            Tên phiên <span className="text-slate-400">(không bắt buộc)</span>
            <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Ví dụ: HPG – BCPTBV 2025 + BCTN 2024" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            <span className="mt-1 block text-[11px] text-slate-500">Để tìm lại trong Lịch sử; không ảnh hưởng kết quả.</span>
          </label>
        </div>

        <div className="mt-4 flex gap-2">
          {[['files', 'Tải tệp PDF/TXT'], ['text', 'Dán văn bản']].map(([k, l]) => (
            <button key={k} type="button" onClick={() => setMode(k)} className={`rounded-lg px-4 py-2 text-sm font-semibold ${mode === k ? 'bg-[#0F3D2E] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>{l}</button>
          ))}
        </div>

        {mode === 'files' ? (
          <>
            <label
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => { e.preventDefault(); addFiles(e.dataTransfer.files) }}
              className="mt-3 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-7 text-center transition hover:border-emerald-400 hover:bg-emerald-50"
            >
              <span className="text-2xl text-emerald-700">⤒</span>
              <span className="mt-1 text-sm font-semibold text-slate-800">Kéo thả tệp vào đây hoặc bấm để chọn</span>
              <span className="mt-1 text-[11px] text-slate-500">PDF (kể cả bản scan), TXT, MD, JSON · tệp đầu tiên mặc định là báo cáo cần kiểm</span>
              <input type="file" multiple className="hidden" accept=".pdf,.txt,.md,.json,.csv" onChange={(e) => addFiles(e.target.files)} />
            </label>
            {entries.length > 0 && (
              <ul className="mt-3 divide-y divide-slate-100 rounded-lg border border-slate-200">
                {entries.map((e, i) => (
                  <li key={`${e.file.name}-${i}`} className="flex flex-wrap items-center gap-2 px-3 py-2">
                    <span className="min-w-0 flex-1 truncate text-sm text-slate-800" title={e.file.name}>{e.file.name}</span>
                    <span className="font-mono text-[11px] text-slate-400">{formatBytes(e.file.size)}</span>
                    <Segmented value={e.role} onChange={(v) => update(i, { role: v })} options={ROLES.slice(0, 2)} />
                    <SourceSelect value={e.source_type} onChange={(v) => update(i, { source_type: v })} />
                    <button type="button" onClick={() => remove(i)} className="px-1 text-sm text-slate-400 hover:text-red-700" aria-label={`Bỏ ${e.file.name}`}>×</button>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <div className="mt-3 space-y-3">
            <div className="flex justify-end">
              <button type="button" onClick={() => { setClaimText(EXAMPLE.claim); setEvidenceText(EXAMPLE.evidence) }} className="text-xs font-semibold text-emerald-800 hover:underline">Điền ví dụ để thử</button>
            </div>
            <label className="block text-sm font-semibold text-slate-700">
              Đoạn văn chứa tuyên bố cần kiểm
              <textarea value={claimText} onChange={(e) => setClaimText(e.target.value)} rows={4} placeholder="Dán đoạn văn từ báo cáo…" className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal" />
            </label>
            <label className="block text-sm font-semibold text-slate-700">
              Tài liệu đối chiếu <span className="font-normal text-slate-400">(không bắt buộc)</span>
              <textarea value={evidenceText} onChange={(e) => setEvidenceText(e.target.value)} rows={3} placeholder="Dán số liệu từ báo cáo kiểm kê, BCTC, quyết định…" className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal" />
            </label>
          </div>
        )}

        <div className="mt-4 space-y-2 text-xs">
          {documents.length > 0 && !hasClaimSource && (
            <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-red-800">Chưa có tài liệu nào là <b>Cần kiểm</b> — sẽ không có tuyên bố nào để kiểm.</p>
          )}
          {hasClaimSource && !hasEvidence && (
            <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-amber-900">Chưa có tài liệu <b>Đối chiếu</b>: hệ thống chỉ so tuyên bố với chính báo cáo đó nên phần lớn kết quả sẽ là “chưa đủ bằng chứng”. Vẫn chạy được.</p>
          )}
          {hasEvidence && !hasIndependent && (
            <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-slate-700">Chưa có nguồn <b>độc lập</b> (pháp lý / bên thứ ba / tiêu chuẩn): kết quả sẽ ghi “thiếu bằng chứng độc lập”.</p>
          )}
          {runtime && (
            <p className={`rounded-lg border px-3 py-2 ${runtime.sends_documents_out ? 'border-sky-200 bg-sky-50 text-sky-900' : 'border-emerald-200 bg-emerald-50 text-emerald-900'}`}>
              <b>{runtime.label}.</b>{' '}
              {runtime.sends_documents_out
                ? 'Đoạn tuyên bố và đoạn bằng chứng của những cặp khó được gửi tới nhà cung cấp mô hình. Không dùng chế độ này cho tài liệu mật.'
                : 'Toàn bộ xử lý chạy trên máy này.'}
            </p>
          )}
          {error && <p className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-red-800"><b>Lỗi:</b> {error}</p>}
        </div>

        <div className="mt-4 flex items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1">
            {documents.map((d, i) => (
              <Chip key={i} tone={d.role === 'claim_source' ? 'emerald' : INDEPENDENT.has(d.source_type) ? 'sky' : 'slate'}>{d.name}</Chip>
            ))}
          </div>
          <button type="button" disabled={!canStart} onClick={start} className="shrink-0 rounded-lg bg-[#0F3D2E] px-5 py-2 text-sm font-semibold text-white disabled:opacity-40">▶ Bắt đầu phân tích</button>
        </div>
      </section>

      <section className="grid gap-3 text-xs text-slate-600 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-3"><b className="text-slate-900">1 · Chọn tài liệu</b><p className="mt-1">Báo cáo cần kiểm và tài liệu để đối chiếu.</p></div>
        <div className="rounded-xl border border-slate-200 bg-white p-3"><b className="text-slate-900">2 · Soát theo hàng đợi</b><p className="mt-1">Mở các mục theo thứ tự ưu tiên; xác nhận hoặc sửa kết quả của AI.</p></div>
        <div className="rounded-xl border border-slate-200 bg-white p-3"><b className="text-slate-900">3 · Giấy làm việc</b><p className="mt-1">In hoặc lưu PDF, kèm quyết định của người soát xét.</p></div>
      </section>
    </div>
  )
}
