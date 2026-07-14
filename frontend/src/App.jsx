import { useEffect, useState } from 'react'
import { analyzeFiles, analyzeText, checkHealth } from './api.js'
import { TextInputPanel, FileInputPanel } from './components/InputPanel.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'

export default function App() {
  const [tab, setTab] = useState('text')
  const [analysis, setAnalysis] = useState(null)
  const [lastDocuments, setLastDocuments] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    checkHealth()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))
  }, [])

  const run = async (fn) => {
    setLoading(true)
    setError(null)
    try {
      const data = await fn()
      setAnalysis(data)
    } catch (exc) {
      setError(exc.message || 'Không gọi được máy chủ phân tích.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeText = (documents) => {
    setLastDocuments(documents)
    return run(() => analyzeText(documents))
  }

  const handleAnalyzeFiles = (files, roles, sourceTypes) => {
    setLastDocuments(null)
    return run(() => analyzeFiles(files, roles, sourceTypes))
  }

  const handleRecheck = (claim, editedText) => {
    let documents
    if (lastDocuments) {
      documents = lastDocuments.map((doc) =>
        doc.role === 'claim_source' && doc.text.includes(claim.text)
          ? { ...doc, text: doc.text.replace(claim.text, editedText) }
          : doc,
      )
    } else {
      const seen = new Set()
      const evidenceDocs = []
      for (const verification of analysis.result.verifications) {
        for (const evidence of verification.evidence) {
          if (seen.has(evidence.chunk_id)) continue
          seen.add(evidence.chunk_id)
          evidenceDocs.push({
            name: evidence.source_name,
            text: evidence.text,
            role: 'evidence',
            source_type: evidence.source_type,
          })
        }
      }
      documents = [
        { name: 'tuyen-bo-sua', text: editedText, role: 'claim_source', source_type: 'internal' },
        ...evidenceDocs,
      ]
      setLastDocuments(documents)
    }
    return run(() => analyzeText(documents))
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-xl font-bold text-slate-800">🌿 GreenScan AI</h1>
            <p className="text-sm text-slate-500">
              Kiểm tra rủi ro greenwashing trong tuyên bố ESG & báo cáo tài chính
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              apiStatus === 'online'
                ? 'bg-emerald-100 text-emerald-800'
                : apiStatus === 'offline'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-slate-100 text-slate-600'
            }`}
          >
            {apiStatus === 'online' ? '● API sẵn sàng' : apiStatus === 'offline' ? '● API ngoại tuyến' : '● Đang kiểm tra API'}
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex gap-2">
            <button
              type="button"
              onClick={() => setTab('text')}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                tab === 'text' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              ✍️ Nhập câu claim
            </button>
            <button
              type="button"
              onClick={() => setTab('files')}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                tab === 'files' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              📄 Tải tài liệu báo cáo
            </button>
          </div>

          {tab === 'text' ? (
            <TextInputPanel onAnalyze={handleAnalyzeText} loading={loading} />
          ) : (
            <FileInputPanel onAnalyze={handleAnalyzeFiles} loading={loading} />
          )}
        </section>

        {error && (
          <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800">
            <b>Lỗi:</b> {error}
          </div>
        )}

        {loading && !analysis && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
            ⏳ AI agent đang phân tích: trích xuất claim → truy xuất chứng cứ → xác minh → chấm điểm rủi ro…
          </div>
        )}

        {analysis && <ResultsPanel analysis={analysis} onRecheck={handleRecheck} loading={loading} />}
      </main>
    </div>
  )
}
