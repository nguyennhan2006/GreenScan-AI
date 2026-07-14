import { useState } from 'react'

const SOURCE_TYPES = [
  ['internal', 'Nội bộ'],
  ['financial', 'Tài chính'],
  ['environmental', 'Môi trường'],
  ['legal', 'Pháp lý'],
  ['external', 'Bên ngoài'],
  ['standard', 'Tiêu chuẩn'],
]

const ROLES = [
  ['claim_source', 'Nguồn tuyên bố'],
  ['evidence', 'Chứng cứ'],
  ['reference', 'Tham chiếu'],
]

function Select({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-700 focus:border-emerald-500 focus:outline-none"
    >
      {options.map(([v, label]) => (
        <option key={v} value={v}>{label}</option>
      ))}
    </select>
  )
}

export function TextInputPanel({ onAnalyze, loading }) {
  const [claimText, setClaimText] = useState('')
  const [evidences, setEvidences] = useState([
    { name: 'chung-cu-1', text: '', source_type: 'environmental' },
  ])

  const updateEvidence = (index, patch) => {
    setEvidences((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)))
  }

  const submit = () => {
    const documents = [
      { name: 'tuyen-bo', text: claimText, role: 'claim_source', source_type: 'internal' },
      ...evidences
        .filter((e) => e.text.trim())
        .map((e) => ({ name: e.name || 'chung-cu', text: e.text, role: 'evidence', source_type: e.source_type })),
    ]
    onAnalyze(documents)
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-semibold text-slate-700">
          Câu tuyên bố (claim) hoặc đoạn văn bản cần kiểm tra
        </label>
        <textarea
          value={claimText}
          onChange={(e) => setClaimText(e.target.value)}
          rows={5}
          placeholder="Ví dụ: Công ty đã giảm 30% phát thải CO2 trong năm 2024 và cam kết đạt trung hòa carbon vào năm 2030..."
          className="w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-800 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
      </div>

      <div>
        <div className="mb-1 flex items-center justify-between">
          <label className="text-sm font-semibold text-slate-700">Tài liệu chứng cứ (tùy chọn)</label>
          <button
            type="button"
            onClick={() => setEvidences((prev) => [...prev, { name: `chung-cu-${prev.length + 1}`, text: '', source_type: 'environmental' }])}
            className="text-sm font-medium text-emerald-700 hover:text-emerald-900"
          >
            + Thêm chứng cứ
          </button>
        </div>
        <div className="space-y-3">
          {evidences.map((evidence, index) => (
            <div key={index} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <input
                  value={evidence.name}
                  onChange={(e) => updateEvidence(index, { name: e.target.value })}
                  placeholder="Tên tài liệu"
                  className="w-40 rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm focus:border-emerald-500 focus:outline-none"
                />
                <Select
                  value={evidence.source_type}
                  onChange={(v) => updateEvidence(index, { source_type: v })}
                  options={SOURCE_TYPES}
                />
                {evidences.length > 1 && (
                  <button
                    type="button"
                    onClick={() => setEvidences((prev) => prev.filter((_, i) => i !== index))}
                    className="ml-auto text-sm text-red-500 hover:text-red-700"
                  >
                    Xóa
                  </button>
                )}
              </div>
              <textarea
                value={evidence.text}
                onChange={(e) => updateEvidence(index, { text: e.target.value })}
                rows={3}
                placeholder="Dán nội dung tài liệu chứng cứ (số liệu, báo cáo, thông báo pháp lý...)"
                className="w-full rounded-lg border border-slate-300 bg-white p-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            </div>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={submit}
        disabled={loading || !claimText.trim()}
        className="rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Đang phân tích…' : 'Phân tích greenwashing'}
      </button>
    </div>
  )
}

export function FileInputPanel({ onAnalyze, loading }) {
  const [entries, setEntries] = useState([])

  const addFiles = (fileList) => {
    const added = Array.from(fileList).map((file) => ({
      file,
      role: 'claim_source',
      source_type: 'internal',
    }))
    setEntries((prev) => [...prev, ...added])
  }

  const updateEntry = (index, patch) => {
    setEntries((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)))
  }

  const submit = () => {
    onAnalyze(
      entries.map((e) => e.file),
      entries.map((e) => e.role),
      entries.map((e) => e.source_type),
    )
  }

  return (
    <div className="space-y-4">
      <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center hover:border-emerald-400 hover:bg-emerald-50">
        <span className="text-3xl">📄</span>
        <span className="mt-2 text-sm font-medium text-slate-600">
          Bấm để chọn tệp báo cáo (PDF, TXT, MD, JSON) — có thể chọn nhiều tệp
        </span>
        <input
          type="file"
          multiple
          accept=".pdf,.txt,.md,.json"
          className="hidden"
          onChange={(e) => {
            addFiles(e.target.files)
            e.target.value = ''
          }}
        />
      </label>

      {entries.length > 0 && (
        <div className="space-y-2">
          {entries.map((entry, index) => (
            <div key={index} className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-3">
              <span className="flex-1 truncate text-sm font-medium text-slate-800">{entry.file.name}</span>
              <Select value={entry.role} onChange={(v) => updateEntry(index, { role: v })} options={ROLES} />
              <Select
                value={entry.source_type}
                onChange={(v) => updateEntry(index, { source_type: v })}
                options={SOURCE_TYPES}
              />
              <button
                type="button"
                onClick={() => setEntries((prev) => prev.filter((_, i) => i !== index))}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Xóa
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={submit}
        disabled={loading || entries.length === 0}
        className="rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Đang phân tích…' : `Phân tích ${entries.length} tệp`}
      </button>
    </div>
  )
}
