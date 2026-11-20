import { useEffect, useMemo, useRef, useState } from 'react'
import ModelModeSwitch from '../components/ModelModeSwitch.jsx'
import NextStep, { ArrowHint } from '../components/NextStep.jsx'
import { STATIC } from '../staticApi.js'
import { intakeFetch, intakePreview, intakeSampleFile, intakeSamples, jobStatus, orgPacks, startAnalysisFiles, startAnalysisText } from '../api.js'
import { Icon } from '../components/icons.jsx'

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
  ['claim_source', 'Cần kiểm', 'Báo cáo chứa tuyên bố cần kiểm (báo cáo phát triển bền vững, báo cáo thường niên).'],
  ['evidence', 'Đối chiếu', 'Tài liệu để so (báo cáo tài chính, báo cáo kiểm kê khí nhà kính, quyết định của cơ quan nhà nước…).'],
  ['reference', 'Tham khảo', 'Bối cảnh phụ, xếp sau tài liệu đối chiếu.'],
]
const SOURCE_TYPES = [
  ['internal', 'Doanh nghiệp tự phát hành', 'Báo cáo bền vững, báo cáo thường niên.'],
  ['financial', 'Báo cáo tài chính', 'Báo cáo tài chính, thuyết minh.'],
  ['environmental', 'Môi trường', 'Báo cáo kiểm kê khí nhà kính, đánh giá tác động môi trường, quan trắc.'],
  ['legal', 'Pháp lý — độc lập', 'Quyết định, kết luận thanh tra, bản án.'],
  ['external', 'Bên thứ ba — độc lập', 'Báo cáo đảm bảo, kiểm định, báo chí.'],
  ['standard', 'Tiêu chuẩn — độc lập', 'Tiêu chuẩn ISO, hướng dẫn kiểm kê khí nhà kính, quy chuẩn.'],
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
          className={`px-2.5 py-1 text-xs font-medium ${value === v ? 'bg-[#047857] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'}`}
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

function PreviewLine({ p }) {
  if (!p) return <span className="text-xs text-slate-400">Đang đọc thử…</span>
  if (p.error) return <span className="text-xs text-red-700">{p.error}</span>
  const g = p.guess || {}
  const minutes = Math.max(1, Math.round((p.estimated_seconds || 0) / 60))
  return (
    <span className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-slate-500">
      {p.pages != null && <span title="Số trang có lớp chữ / tổng số trang">{p.text_pages}/{p.pages} trang có chữ</span>}
      <span title="Ước lượng số câu sẽ được đọc">~{p.sentences} câu</span>
      <span title="Ước lượng theo HPG: 264 trang ≈ 2 phút trên máy tính xách tay">≈ {p.estimated_seconds < 60 ? `${p.estimated_seconds} giây` : `${minutes} phút`}</span>
      {g.report_type_label && <span className="text-emerald-800" title="Đoán từ tên tệp và các trang đầu">{g.report_type_label}{g.year ? ` ${g.year}` : ''}</span>}
      {g.company && <span className="text-emerald-800" title="Tên doanh nghiệp đọc được ở các trang đầu">{g.company}</span>}
      {(p.warnings || []).map((w, i) => <span key={i} className={/không có OCR|Không đọc/.test(w) ? 'font-semibold text-red-700' : 'text-amber-700'}>⚠ {w}</span>)}
    </span>
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
    <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-5">
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
              <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                state === 'done' ? 'bg-emerald-600 text-white' : state === 'active' ? 'animate-pulse bg-[#047857] text-white' : state === 'failed' ? 'bg-red-600 text-white' : 'bg-slate-200 text-slate-500'
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
      {!failed && <p className="mt-4 text-xs text-slate-500">Một báo cáo bền vững kèm báo cáo thường niên mất khoảng 2 phút trên máy tính xách tay. Có thể mở trang khác; kết quả được lưu trong Lịch sử.</p>}
    </section>
  )
}

export default function NewAnalysisPage({ onDone, runtime, onRuntime }) {
  const [mode, setMode] = useState('files')
  const [entries, setEntries] = useState([])
  const [claimText, setClaimText] = useState('')
  const [evidenceText, setEvidenceText] = useState('')
  const [label, setLabel] = useState('')
  const [company, setCompany] = useState('')
  // Bộ quy tắc nội bộ đã duyệt chọn cho phiên này (org-pack-v1); không chọn = như trước.
  const [packOptions, setPackOptions] = useState([])
  const [chosenPacks, setChosenPacks] = useState([])
  useEffect(() => {
    orgPacks().then((d) => setPackOptions([...new Map((d.uploaded || []).filter((p) => p.status === 'approved')
      .map((p) => [p.org_id, p])).values()])).catch(() => setPackOptions([]))
  }, [])
  const [job, setJob] = useState(null)
  const [startedAt, setStartedAt] = useState(0)
  const [error, setError] = useState(null)
  const [url, setUrl] = useState('')
  const [fetching, setFetching] = useState(false)
  const [samples, setSamples] = useState([])
  const timer = useRef(null)

  useEffect(() => { intakeSamples().then((r) => setSamples(r.samples || [])).catch(() => {}) }, [])

  useEffect(() => () => clearInterval(timer.current), [])

  const addFiles = (list, preset = null) => {
    const files = Array.from(list || [])
    if (!files.length) return
    setEntries((prev) => [
      ...prev,
      ...files.map((file, i) => {
        const isFirst = prev.length + i === 0
        const p = preset?.[i]
        return { file, role: p?.role || guessRole(file.name, isFirst), source_type: p?.source_type || guessSourceType(file.name, isFirst), preset: !!p, preview: null }
      }),
    ])
    // Read each file the way the parser will, then fill in what the reviewer would otherwise type.
    intakePreview(files).then((r) => {
      setEntries((prev) => prev.map((e) => {
        const k = files.indexOf(e.file)
        if (k < 0) return e
        const p = r.files[k]
        const g = p?.guess || {}
        if (e.preset || e.touched || !g.suggested_role) return { ...e, preview: p }
        // Keep the first file as the report to check unless the preview is sure it is evidence.
        const keepClaim = e.role === 'claim_source' && g.suggested_role !== 'claim_source' && !g.report_type
        return { ...e, preview: p, role: keepClaim ? e.role : g.suggested_role, source_type: g.suggested_source_type }
      }))
      const first = r.files.find((p) => p?.guess?.company)
      if (first) setCompany((c) => c || first.guess.company)
      const main = r.files.find((p) => p?.guess?.report_type)
      if (main) setLabel((l) => l || [main.guess.ticker || main.guess.company, main.guess.report_type_label, main.guess.year].filter(Boolean).join(' – '))
    }).catch(() => {
      setEntries((prev) => prev.map((e) => (files.includes(e.file) && !e.preview ? { ...e, preview: { error: 'Không đọc thử được; vẫn chạy được.' } } : e)))
    })
  }

  const loadSample = async (sample) => {
    setFetching(true); setError(null)
    try {
      const files = await Promise.all(sample.files.map((f, i) => intakeSampleFile(sample.id, i, f.name)))
      setMode('files')
      addFiles(files, sample.files)
      setCompany((c) => c || sample.company)
      setLabel((l) => l || sample.label)
    } catch (exc) {
      setError(exc.message || 'Không mở được bộ mẫu.')
    } finally {
      setFetching(false)
    }
  }

  const fromUrl = async () => {
    const value = url.trim()
    if (!value) return
    const ticker = value.match(/^([A-Za-z]{3})\s+(20\d\d)$/)
    if (ticker) {
      const sample = samples.find((x) => x.id === ticker[1].toLowerCase())
      if (sample) { await loadSample(sample); setUrl(''); return }
      setError(`Chưa có danh mục báo cáo theo mã chứng khoán cho ${ticker[1].toUpperCase()} ${ticker[2]}. Dán đường dẫn tới tệp PDF/DOCX của báo cáo.`)
      return
    }
    setFetching(true); setError(null)
    try {
      const file = await intakeFetch(value)
      addFiles([file]); setUrl('')
    } catch (exc) {
      setError(exc.message || 'Không tải được tệp từ đường dẫn.')
    } finally {
      setFetching(false)
    }
  }
  const update = (i, patch) => setEntries((prev) => prev.map((e, j) => (j === i ? { ...e, ...patch, touched: true } : e)))
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
  const blind = entries.filter((e) => e.preview && !e.preview.ocr_available && (e.preview.scanned_pages || []).length > 0)

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
        ? await startAnalysisFiles(entries.map((e) => e.file), entries.map((e) => e.role), entries.map((e) => e.source_type), label, company, chosenPacks)
        : await startAnalysisText(documents, label, company, chosenPacks)
      setJob(status)
      poll(status.job_id)
    } catch (exc) {
      setError(exc.message || 'Không gọi được máy chủ phân tích.')
    }
  }

  if (job) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        {job.state !== 'failed' && (
          <NextStep step={1}>Đang phân tích “{label || documents[0]?.name}”. Bạn không cần làm gì: xong là hàng đợi soát tự mở.</NextStep>
        )}
        <Progress job={job} startedAt={startedAt} onRetry={() => setJob(null)} />
      </div>
    )
  }

  const sessionName = label || (mode === 'files' ? entries[0]?.file.name : '') || ''
  // One sentence per state, picked by index (kept as a list so no code sits between two pieces of text).
  const hints = [
    <>Thả báo cáo cần kiểm vào khung bên dưới. Chưa có tệp trong tay? Bấm một <b>bộ mẫu</b> để thử ngay.</>,
    <>Chưa có tệp nào được đánh dấu <b>Cần kiểm</b>. Chọn “Cần kiểm” cho báo cáo chứa tuyên bố.</>,
    <>Nếu có, thêm tài liệu để đối chiếu (báo cáo tài chính, quyết định của cơ quan nhà nước). Không có thì vẫn bấm <b>Bắt đầu phân tích</b> được.</>,
    <>Đủ tài liệu rồi. Bấm <b>Bắt đầu phân tích</b>.</>,
    <>Bản xem trên web không phân tích tài liệu mới, vì việc đó cần máy chủ. Mở một phiên đã chạy sẵn trong <b>Lịch sử phân tích</b>.</>,
  ]
  const hint = hints[STATIC ? 4 : !documents.length ? 0 : !hasClaimSource ? 1 : !hasEvidence ? 2 : 3]

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <NextStep step={1} action={STATIC ? { label: 'Mở Lịch sử phân tích →', to: '/runs' } : canStart && hasEvidence ? { label: 'Bắt đầu phân tích →', onClick: start } : null}>{hint}</NextStep>
      <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-5">
        {mode === 'files' ? (
          <>
            <label
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => { e.preventDefault(); addFiles(e.dataTransfer.files) }}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-emerald-300/70 bg-emerald-50/30 text-center transition hover:border-emerald-500 hover:bg-emerald-50 ${entries.length ? 'p-4' : 'p-8'}`}
            >
              <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-emerald-700 shadow-sm ring-1 ring-emerald-100"><Icon name="upload" className="h-6 w-6" /></span>
              <span className="mt-3 text-[15px] font-semibold text-slate-800">{entries.length ? 'Thêm tệp khác' : 'Kéo thả tệp vào đây hoặc bấm để chọn'}</span>
              {!entries.length && <span className="mt-1 text-xs text-slate-500">PDF (kể cả bản quét), DOCX, HTML, TXT</span>}
              <input type="file" multiple className="hidden" accept=".pdf,.docx,.html,.htm,.txt,.md,.json,.csv" onChange={(e) => addFiles(e.target.files)} />
            </label>
            {!STATIC && entries.length === 0 && samples.length > 0 && (
              <div className="mt-4" data-testid="samples">
                <p className="flex items-center gap-2 text-xs font-semibold text-slate-600">Hoặc thử ngay với bộ mẫu <ArrowHint label="bấm một bộ" dir="down" /></p>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {samples.map((s, i) => (
                    <button key={s.id} type="button" onClick={() => loadSample(s)} disabled={fetching} data-sample={s.id}
                      title={s.files.map((f) => f.name).join(' + ')}
                      className={`flex items-start gap-3 rounded-2xl border border-slate-200/70 bg-white shadow-sm p-3 text-left transition hover:border-emerald-500 hover:bg-emerald-50 disabled:opacity-40 ${i === 0 ? 'gs-halo' : ''}`}>
                      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800"><Icon name="star" className="h-4 w-4" /></span>
                      <span className="min-w-0">
                        <span className="block text-sm font-semibold text-slate-900">{s.title || `Mẫu ${s.id.toUpperCase()}`}</span>
                        <span className="block text-xs text-slate-500">{s.note || s.label}</span>
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {entries.length > 0 && (
              <ul className="mt-3 divide-y divide-slate-100 rounded-lg border border-slate-200">
                {entries.map((e, i) => (
                  <li key={`${e.file.name}-${i}`} className="flex flex-wrap items-center gap-2 px-3 py-2">
                    <span className="min-w-0 flex-1 truncate text-sm text-slate-800" title={e.file.name}>{e.file.name}</span>
                    <span className="font-mono text-xs text-slate-400">{formatBytes(e.file.size)}</span>
                    <Segmented value={e.role} onChange={(v) => update(i, { role: v })} options={ROLES.slice(0, 2)} />
                    <SourceSelect value={e.source_type} onChange={(v) => update(i, { source_type: v })} />
                    <button type="button" onClick={() => remove(i)} className="px-1 text-sm text-slate-400 hover:text-red-700" aria-label={`Bỏ ${e.file.name}`}>×</button>
                    <div className="basis-full"><PreviewLine p={e.preview} /></div>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <button type="button" onClick={() => setMode('files')} className="text-xs font-semibold text-slate-600 hover:underline">← Quay lại tải tệp</button>
              <button type="button" onClick={() => { setClaimText(EXAMPLE.claim); setEvidenceText(EXAMPLE.evidence) }} className="text-xs font-semibold text-emerald-800 hover:underline">Điền ví dụ để thử</button>
            </div>
            <label className="block text-sm font-semibold text-slate-700">
              Đoạn văn chứa tuyên bố cần kiểm
              <textarea value={claimText} onChange={(e) => setClaimText(e.target.value)} rows={4} placeholder="Dán đoạn văn từ báo cáo…" className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal" />
            </label>
            <label className="block text-sm font-semibold text-slate-700">
              Tài liệu đối chiếu <span className="font-normal text-slate-400">(không bắt buộc)</span>
              <textarea value={evidenceText} onChange={(e) => setEvidenceText(e.target.value)} rows={3} placeholder="Dán số liệu từ báo cáo kiểm kê, báo cáo tài chính, quyết định…" className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal" />
            </label>
          </div>
        )}

        {documents.length > 0 && runtime?.model_modes && (
          <div className="mt-4">
            <p className="mb-2 text-xs font-semibold text-slate-800">Ai đọc cùng luật trong phiên này?</p>
            <ModelModeSwitch runtime={runtime} onRuntime={onRuntime} compact />
          </div>
        )}

        <details className="mt-4 rounded-lg border border-slate-200 bg-slate-50/60 px-3 py-2" data-testid="more-options">
          <summary className="cursor-pointer text-xs font-semibold text-slate-700">
            Tuỳ chọn thêm <span className="font-normal text-slate-500">· tên phiên, lấy tệp từ đường dẫn web, dán văn bản{packOptions.length ? ', quy tắc nội bộ' : ''}</span>
          </summary>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <label className="block text-sm text-slate-700">
              Tên doanh nghiệp
              <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Ví dụ: Hòa Phát" className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm" />
              <span className="mt-1 block text-xs text-slate-500">Giúp phân biệt câu doanh nghiệp tự tuyên bố với câu giải thích chung.</span>
            </label>
            <label className="block text-sm text-slate-700">
              Tên phiên
              <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Ví dụ: Hòa Phát – báo cáo bền vững 2025" className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm" />
              <span className="mt-1 block text-xs text-slate-500">Để tìm lại trong Lịch sử; không ảnh hưởng kết quả.</span>
            </label>
          </div>
          {packOptions.length > 0 && (
            <div className="mt-3 text-sm text-slate-700">
              <p className="font-medium">Áp thêm quy tắc nội bộ của tổ chức <span className="text-xs font-normal text-slate-500">(đã duyệt; chỉ thêm phát hiện bên cạnh kết luận, không đổi kết luận)</span></p>
              <div className="mt-1 flex flex-wrap gap-3">
                {packOptions.map((p) => (
                  <label key={p.org_id} className="flex items-center gap-1.5 text-xs">
                    <input type="checkbox" checked={chosenPacks.includes(p.org_id)}
                      onChange={(e) => setChosenPacks((cur) => e.target.checked ? [...cur, p.org_id] : cur.filter((x) => x !== p.org_id))} />
                    {p.org_name || p.org_id} <span className="font-mono text-[11px] text-slate-400">{p.pack_version}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <input value={url} onChange={(e) => setUrl(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && fromUrl()}
              placeholder="Dán đường dẫn báo cáo (https://…pdf)"
              className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100" />
            <button type="button" onClick={fromUrl} disabled={!url.trim() || fetching} title="Máy chủ tải tệp về rồi thêm vào danh sách như tệp tải lên"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-[13px] font-semibold text-slate-700 transition hover:border-emerald-500 hover:bg-emerald-50 disabled:opacity-40">
              {fetching ? 'Đang tải…' : <><Icon name="download" className="h-4 w-4" />Lấy từ đường dẫn web</>}
            </button>
          </div>
          {mode === 'files' && (
            <button type="button" onClick={() => setMode('text')} className="mt-3 text-xs font-semibold text-emerald-800 hover:underline">Không có tệp? Dán văn bản thay cho tệp →</button>
          )}
        </details>

        <div className="mt-4 space-y-2 text-xs">
          {blind.length > 0 && (
            <p className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-red-800">
              <b>Sẽ mất chữ:</b> {blind.map((e) => `${e.file.name} (${e.preview.scanned_pages.length} trang quét)`).join(', ')}. Máy này không có OCR nên các trang đó không cho ra câu nào. Cài tesseract, hoặc dùng bản PDF có lớp chữ / DOCX.
            </p>
          )}
          {documents.length > 0 && !hasClaimSource && (
            <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-red-800">Chưa có tài liệu nào là <b>Cần kiểm</b> — sẽ không có tuyên bố nào để kiểm.</p>
          )}
          {hasClaimSource && !hasEvidence && (
            <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-amber-900">Chưa có tài liệu <b>Đối chiếu</b>: hệ thống chỉ so tuyên bố với chính báo cáo đó nên phần lớn kết quả sẽ là “chưa đủ bằng chứng”. Vẫn chạy được.</p>
          )}
          {hasEvidence && !hasIndependent && (
            <p className="px-1 text-slate-500">Chưa có nguồn độc lập (pháp lý, bên thứ ba, tiêu chuẩn): kết quả sẽ ghi “thiếu bằng chứng độc lập”.</p>
          )}
          {runtime?.sends_documents_out && runtime.model_mode !== 'cloud' && (
            <p className="rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-sky-900">
              <b>{runtime.label}.</b> Đoạn tuyên bố và đoạn bằng chứng của những cặp khó được gửi tới nhà cung cấp mô hình. Không dùng chế độ này cho tài liệu mật.
            </p>
          )}
          {error && <p className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-red-800"><b>Lỗi:</b> {error}</p>}
        </div>

        <div className="mt-4 flex items-center justify-between gap-3">
          <p className="min-w-0 truncate text-xs text-slate-500">
            {!documents.length ? 'Cần ít nhất một tệp để bắt đầu.'
              : !hasClaimSource ? 'Cần một tệp được đánh dấu “Cần kiểm”.'
                : sessionName ? <>Phiên: <span className="text-slate-700">{sessionName}</span></> : null}
          </p>
          <button type="button" disabled={!canStart} onClick={start} className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-[#047857] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#065f46] disabled:opacity-40"><Icon name="play" className="h-4 w-4" />Bắt đầu phân tích</button>
        </div>
      </section>
    </div>
  )
}
