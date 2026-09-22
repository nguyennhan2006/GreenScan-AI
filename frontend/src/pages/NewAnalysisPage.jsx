import { useEffect, useMemo, useState } from 'react'
import { Chip } from '../components/badges.jsx'

/**
 * Three-step intake (mockup #2–#4): sources → configuration → run.
 *
 * Only what the API actually accepts is asked for. Role and source type change
 * the verdict (claims come only from `claim_source`; `legal/external/standard`
 * count as independent), so they sit next to each file with a one-line meaning.
 * Options the server does not take (analysis mode, e-mail on completion,
 * auto-delete) are not shown as if they did something.
 */

export const ROLES = [
  ['claim_source', 'Nguồn tuyên bố', 'Tuyên bố sẽ được trích từ tài liệu này.'],
  ['evidence', 'Chứng cứ', 'Dùng để đối chiếu; không trích tuyên bố.'],
  ['reference', 'Tham chiếu', 'Bối cảnh phụ, xếp sau chứng cứ.'],
]
export const SOURCE_TYPES = [
  ['internal', 'Nội bộ', 'Tài liệu do chính doanh nghiệp phát hành.'],
  ['financial', 'Tài chính', 'BCTC, BCTN, thuyết minh.'],
  ['environmental', 'Môi trường', 'Báo cáo phát thải, kiểm kê, ĐTM.'],
  ['legal', 'Pháp lý', 'Quyết định, kết luận thanh tra, bản án — nguồn độc lập.'],
  ['external', 'Bên ngoài', 'Bên thứ ba, báo chí, kiểm định — nguồn độc lập.'],
  ['standard', 'Tiêu chuẩn', 'ISO, GHG Protocol, quy chuẩn — nguồn độc lập.'],
]
const INDEPENDENT = new Set(['legal', 'external', 'standard'])

export const PLAN_STEPS = [
  ['validate_inputs', 'Tiếp nhận & kiểm tra đầu vào'],
  ['parse_and_ocr_documents', 'Đọc tài liệu & OCR'],
  ['extract_green_claims', 'Trích xuất tuyên bố'],
  ['build_hybrid_retrieval_index', 'Lập chỉ mục truy xuất lai'],
  ['retrieve_evidence_per_claim', 'Truy xuất bằng chứng theo tuyên bố'],
  ['verify_claim_evidence_pairs', 'Kiểm chứng tuyên bố – bằng chứng'],
  ['check_applicable_law', 'Đối chiếu văn bản pháp lý áp dụng'],
  ['score_greenwashing_risk', 'Chấm điểm rủi ro theo rubric'],
  ['apply_quality_gates', 'Cổng chất lượng G0–G7'],
  ['write_evidence_pack', 'Ghi gói bằng chứng'],
]

function Select({ value, onChange, options, className = '' }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`rounded-md border border-slate-300 bg-white px-2 py-1 text-xs ${className}`}
    >
      {options.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
    </select>
  )
}

function Stepper({ step }) {
  const steps = ['Tài liệu', 'Cấu hình', 'Chạy phân tích']
  return (
    <ol className="flex items-center gap-3 text-sm">
      {steps.map((label, i) => {
        const n = i + 1
        const state = n < step ? 'done' : n === step ? 'active' : 'todo'
        return (
          <li key={label} className="flex items-center gap-2">
            <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
              state === 'done' ? 'bg-emerald-600 text-white' : state === 'active' ? 'bg-[#0F3D2E] text-white' : 'bg-slate-200 text-slate-600'
            }`}>{state === 'done' ? '✓' : n}</span>
            <span className={state === 'active' ? 'font-semibold text-slate-900' : 'text-slate-500'}>{label}</span>
            {i < steps.length - 1 && <span className="mx-1 h-px w-8 bg-slate-300" />}
          </li>
        )
      })}
    </ol>
  )
}

function formatBytes(n) {
  if (!n && n !== 0) return ''
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

export default function NewAnalysisPage({ onAnalyzeText, onAnalyzeFiles, loading, error, gatewayInfo }) {
  const [step, setStep] = useState(1)
  const [mode, setMode] = useState('files')
  const [entries, setEntries] = useState([])
  const [claimText, setClaimText] = useState('')
  const [textDocs, setTextDocs] = useState([])
  const [label, setLabel] = useState('')
  const [startedAt, setStartedAt] = useState(null)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    if (!loading) return undefined
    const t = setInterval(() => setElapsed(Math.round((Date.now() - startedAt) / 1000)), 500)
    return () => clearInterval(t)
  }, [loading, startedAt])

  const addFiles = (list) => {
    const incoming = Array.from(list || []).map((file, i) => ({
      file,
      role: entries.length + i === 0 ? 'claim_source' : 'evidence',
      source_type: entries.length + i === 0 ? 'internal' : 'financial',
    }))
    setEntries((prev) => [...prev, ...incoming])
  }
  const update = (i, patch) => setEntries((prev) => prev.map((e, j) => (j === i ? { ...e, ...patch } : e)))
  const remove = (i) => setEntries((prev) => prev.filter((_, j) => j !== i))

  const documents = useMemo(() => {
    if (mode === 'files') return entries.map((e) => ({ name: e.file.name, role: e.role, source_type: e.source_type, size: e.file.size }))
    const docs = claimText.trim()
      ? [{ name: 'tuyen-bo.txt', role: 'claim_source', source_type: 'internal', size: claimText.length }]
      : []
    return docs.concat(textDocs.filter((d) => d.text.trim()).map((d) => ({ ...d, size: d.text.length })))
  }, [mode, entries, claimText, textDocs])

  const hasClaimSource = documents.some((d) => d.role === 'claim_source')
  const hasIndependent = documents.some((d) => INDEPENDENT.has(d.source_type))
  const canContinue = documents.length > 0 && hasClaimSource

  const run = () => {
    setStartedAt(Date.now())
    setElapsed(0)
    setStep(3)
    if (mode === 'files') {
      onAnalyzeFiles(entries.map((e) => e.file), entries.map((e) => e.role), entries.map((e) => e.source_type), label)
    } else {
      const docs = [
        { name: 'tuyen-bo.txt', text: claimText, role: 'claim_source', source_type: 'internal' },
        ...textDocs.filter((d) => d.text.trim()).map(({ name, text, role, source_type }) => ({ name: name || 'chung-cu.txt', text, role, source_type })),
      ]
      onAnalyzeText(docs, label)
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-slate-900">
          {step === 1 ? 'Bước 1. Tài liệu' : step === 2 ? 'Bước 2. Cấu hình phiên' : 'Bước 3. Đang phân tích'}
        </h2>
        <Stepper step={step} />
      </div>

      {error && (
        <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          <b>Lỗi từ máy chủ:</b> <code className="font-mono text-xs">{error}</code>
        </div>
      )}

      {step === 1 && (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <div className="mb-4 flex gap-2">
            {[['files', 'Tải báo cáo'], ['text', 'Dán tuyên bố']].map(([k, l]) => (
              <button
                key={k}
                type="button"
                onClick={() => setMode(k)}
                className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${mode === k ? 'bg-[#0F3D2E] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
              >
                {l}
              </button>
            ))}
          </div>

          {mode === 'files' ? (
            <>
              <label
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => { e.preventDefault(); addFiles(e.dataTransfer.files) }}
                className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center transition hover:border-emerald-400 hover:bg-emerald-50"
              >
                <span className="text-3xl text-emerald-700">⤒</span>
                <span className="mt-2 text-sm font-semibold text-slate-800">Kéo thả tệp vào đây</span>
                <span className="text-xs text-slate-500">hoặc</span>
                <span className="mt-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700">Chọn tệp từ máy tính</span>
                <span className="mt-2 text-[11px] text-slate-500">Hỗ trợ PDF (kể cả bản scan), TXT, MD, JSON, CSV · OCR chạy tự động khi trang không có lớp chữ</span>
                <input type="file" multiple className="hidden" accept=".pdf,.txt,.md,.json,.csv,.yaml,.yml" onChange={(e) => addFiles(e.target.files)} />
              </label>

              {entries.length > 0 && (
                <div className="mt-4 overflow-x-auto">
                  <p className="mb-2 text-sm font-semibold text-slate-800">Danh sách tệp đã chọn ({entries.length})</p>
                  <table className="w-full text-sm">
                    <thead className="text-left text-xs text-slate-500">
                      <tr><th className="pb-1">Tên tệp</th><th className="pb-1">Vai trò</th><th className="pb-1">Loại nguồn</th><th className="pb-1 text-right">Kích thước</th><th /></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {entries.map((e, i) => (
                        <tr key={`${e.file.name}-${i}`}>
                          <td className="py-2 pr-3">
                            <span className="mr-1.5 text-xs text-slate-400">{e.file.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'TXT'}</span>
                            <span className="text-slate-800">{e.file.name}</span>
                          </td>
                          <td className="py-2 pr-3"><Select value={e.role} onChange={(v) => update(i, { role: v })} options={ROLES} /></td>
                          <td className="py-2 pr-3"><Select value={e.source_type} onChange={(v) => update(i, { source_type: v })} options={SOURCE_TYPES} /></td>
                          <td className="py-2 text-right font-mono text-xs text-slate-500">{formatBytes(e.file.size)}</td>
                          <td className="py-2 pl-2 text-right"><button type="button" onClick={() => remove(i)} className="text-xs text-slate-400 hover:text-red-700">×</button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="space-y-4">
              <label className="block text-sm font-semibold text-slate-700">
                Nguồn tuyên bố
                <textarea
                  value={claimText}
                  onChange={(e) => setClaimText(e.target.value)}
                  rows={5}
                  placeholder='Dán đoạn hoặc báo cáo chứa tuyên bố. Ví dụ: "Năm 2024, Tập đoàn giảm 30% phát thải CO2 phạm vi 1 và 2 so với năm gốc 2020."'
                  className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
                />
              </label>
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-700">Tài liệu chứng cứ (tuỳ chọn)</span>
                <button type="button" onClick={() => setTextDocs((p) => [...p, { name: '', text: '', role: 'evidence', source_type: 'financial' }])} className="text-xs font-semibold text-emerald-800 hover:underline">+ Thêm tài liệu</button>
              </div>
              {textDocs.map((d, i) => (
                <div key={i} className="rounded-lg border border-slate-200 p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <input value={d.name} onChange={(e) => setTextDocs((p) => p.map((x, j) => (j === i ? { ...x, name: e.target.value } : x)))} placeholder="Tên tài liệu" className="min-w-40 flex-1 rounded-md border border-slate-300 px-2 py-1 text-xs" />
                    <Select value={d.role} onChange={(v) => setTextDocs((p) => p.map((x, j) => (j === i ? { ...x, role: v } : x)))} options={ROLES} />
                    <Select value={d.source_type} onChange={(v) => setTextDocs((p) => p.map((x, j) => (j === i ? { ...x, source_type: v } : x)))} options={SOURCE_TYPES} />
                    <button type="button" onClick={() => setTextDocs((p) => p.filter((_, j) => j !== i))} className="text-xs text-slate-400 hover:text-red-700">×</button>
                  </div>
                  <textarea value={d.text} onChange={(e) => setTextDocs((p) => p.map((x, j) => (j === i ? { ...x, text: e.target.value } : x)))} rows={3} placeholder="Dán nội dung (số liệu, báo cáo, quyết định…)" className="mt-2 w-full rounded-md border border-slate-300 p-2 text-xs" />
                </div>
              ))}
            </div>
          )}

          <div className="mt-4 space-y-2">
            {!hasClaimSource && documents.length > 0 && (
              <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-800">Chưa có tài liệu vai trò <b>Nguồn tuyên bố</b> — sẽ không trích được tuyên bố nào.</p>
            )}
            {canContinue && !hasIndependent && (
              <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
                <b>Chưa có nguồn độc lập</b> (pháp lý / bên ngoài / tiêu chuẩn). Rubric sẽ ghi “thiếu bằng chứng độc lập” cho mọi tuyên bố. Vẫn chạy được; nên thêm ít nhất một tài liệu đối chiếu.
              </p>
            )}
          </div>

          <div className="mt-5 flex justify-end">
            <button type="button" disabled={!canContinue} onClick={() => setStep(2)} className="rounded-lg bg-[#0F3D2E] px-5 py-2 text-sm font-semibold text-white disabled:opacity-40">Tiếp tục →</button>
          </div>
        </section>
      )}

      {step === 2 && (
        <section className="grid gap-4 lg:grid-cols-[1fr_300px]">
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold text-slate-900">Thiết lập chung</h3>
            <label className="mt-3 block text-sm text-slate-700">
              Tên phiên phân tích
              <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Ví dụ: HPG – BCPTBV 2025 + BCTN 2024" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
              <span className="mt-1 block text-[11px] text-slate-500">Chỉ là nhãn để tìm lại trong Lịch sử; không ảnh hưởng kết quả.</span>
            </label>

            <h3 className="mt-5 text-sm font-semibold text-slate-900">Tài liệu ({documents.length})</h3>
            <ul className="mt-2 divide-y divide-slate-100 text-sm">
              {documents.map((d, i) => (
                <li key={i} className="flex items-center gap-2 py-1.5">
                  <span className="flex-1 truncate text-slate-800">{d.name}</span>
                  <Chip tone={d.role === 'claim_source' ? 'emerald' : 'slate'}>{ROLES.find((r) => r[0] === d.role)?.[1]}</Chip>
                  <Chip tone={INDEPENDENT.has(d.source_type) ? 'sky' : 'slate'}>{SOURCE_TYPES.find((r) => r[0] === d.source_type)?.[1]}</Chip>
                </li>
              ))}
            </ul>

            <h3 className="mt-5 text-sm font-semibold text-slate-900">Các bước sẽ chạy trên máy chủ</h3>
            <p className="mt-1 text-xs text-slate-500">Theo cấu hình <code className="font-mono">configs/default.yaml</code> của máy chủ; giao diện không thay đổi được từng bước.</p>
            <ol className="mt-2 grid grid-cols-1 gap-1 text-xs text-slate-700 sm:grid-cols-2">
              {PLAN_STEPS.map(([k, l], i) => <li key={k} className="flex gap-2"><span className="w-4 text-right font-mono text-slate-400">{i + 1}.</span>{l}</li>)}
            </ol>

            <div className="mt-5 flex justify-between">
              <button type="button" onClick={() => setStep(1)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">← Quay lại</button>
              <button type="button" onClick={run} className="rounded-lg bg-[#0F3D2E] px-5 py-2 text-sm font-semibold text-white">▶ Bắt đầu phân tích</button>
            </div>
          </div>

          <aside className="rounded-xl border border-slate-200 bg-white p-5 text-sm">
            <h3 className="text-sm font-semibold text-slate-900">Thông tin phiên chạy</h3>
            <dl className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between"><dt className="text-slate-500">Số tệp</dt><dd className="font-mono">{documents.length}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Nguồn độc lập</dt><dd>{hasIndependent ? 'Có' : 'Không'}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Rubric</dt><dd className="font-mono">risk-rubric-v2</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Mô hình</dt><dd>{gatewayInfo}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Thời gian</dt><dd>vài giây (text) · vài phút (PDF lớn/OCR)</dd></div>
            </dl>
            <p className="mt-4 text-[11px] leading-relaxed text-slate-500">Mọi phiên được lưu tại <code className="font-mono">.quantum/runs/&lt;run_id&gt;</code> kèm manifest, nhật ký và gói bằng chứng — mở lại được từ Lịch sử.</p>
          </aside>
        </section>
      )}

      {step === 3 && (
        <section className="grid gap-4 lg:grid-cols-[1fr_300px]">
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold text-slate-900">{loading ? 'Đang phân tích…' : error ? 'Phân tích thất bại' : 'Hoàn tất'}</h3>
            <p className="mt-1 text-xs text-slate-500">
              Máy chủ chạy 10 bước theo thứ tự dưới và trả kết quả một lần khi xong; giao diện không nhận tiến độ từng bước nên không hiển thị tick giả.
            </p>
            <ol className="mt-4 space-y-1.5">
              {PLAN_STEPS.map(([k, l], i) => (
                <li key={k} className="flex items-center gap-3 text-sm">
                  <span className={`flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-bold ${loading ? 'bg-slate-200 text-slate-600' : error ? 'bg-red-100 text-red-700' : 'bg-emerald-600 text-white'}`}>
                    {loading ? i + 1 : error ? '!' : '✓'}
                  </span>
                  <span className={loading ? 'text-slate-700' : 'text-slate-900'}>{l}</span>
                  {loading && i === 0 && <span className="ml-auto animate-pulse text-xs text-emerald-700">đang chạy</span>}
                </li>
              ))}
            </ol>
            {error && (
              <button type="button" onClick={() => setStep(1)} className="mt-4 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">← Sửa đầu vào và chạy lại</button>
            )}
          </div>
          <aside className="rounded-xl border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold text-slate-900">Thông tin phiên chạy</h3>
            <dl className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between"><dt className="text-slate-500">Tên phiên</dt><dd className="truncate pl-2">{label || '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Bắt đầu lúc</dt><dd className="font-mono">{startedAt ? new Date(startedAt).toLocaleTimeString('vi-VN') : '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Đã chạy</dt><dd className="font-mono">{elapsed}s</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Tài liệu</dt><dd className="font-mono">{documents.length}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Trạng thái</dt><dd>{loading ? 'Đang chạy' : error ? 'Lỗi' : 'Xong'}</dd></div>
            </dl>
          </aside>
        </section>
      )}
    </div>
  )
}
