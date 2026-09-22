import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  analyzeFiles, analyzeText, checkHealth, exportGold, gatewayHealth, getRun, listReviews, setRunLabel, submitReview,
} from './api.js'
import { navigate, useHashRoute } from './lib/router.jsx'
import { buildRows, summarise } from './lib/claims.js'
import Shell from './components/Shell.jsx'
import Overview from './components/Overview.jsx'
import StartPage from './pages/StartPage.jsx'
import NewAnalysisPage from './pages/NewAnalysisPage.jsx'
import ClaimsPage from './pages/ClaimsPage.jsx'
import ClaimDetailPage from './pages/ClaimDetailPage.jsx'
import ReviewQueuePage from './pages/ReviewQueuePage.jsx'
import ExportPage from './pages/ExportPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import LegalLibraryPage from './pages/LegalLibraryPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

const REVIEWER_KEY = 'greenscan.reviewer'

/** Providers with a key/URL/model set. Liveness needs ?live=true, which costs a ping. */
function configuredProviders(gateway) {
  const providers = gateway?.providers
  if (!providers || typeof providers !== 'object') return []
  return Object.entries(providers).filter(([, v]) => v?.configured).map(([name, v]) => (v?.model ? `${name} (${v.model})` : name))
}

export default function App() {
  const route = useHashRoute()
  const [reviewer, setReviewer] = useState(() => localStorage.getItem(REVIEWER_KEY) || '')
  const [analysis, setAnalysis] = useState(null)
  const [runLabel, setLabel] = useState('')
  const [lastDocuments, setLastDocuments] = useState(null)
  const [loading, setLoading] = useState(false)
  const [runLoading, setRunLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState('checking')
  const [gateway, setGateway] = useState(null)
  const [reviewStates, setReviewStates] = useState({})
  const [reviewHistory, setReviewHistory] = useState({})
  const [reviewDecisions, setReviewDecisions] = useState([])
  const [reviewBusy, setReviewBusy] = useState(false)
  const [goldStats, setGoldStats] = useState(null)

  useEffect(() => {
    checkHealth().then(() => setApiStatus('online')).catch(() => setApiStatus('offline'))
    gatewayHealth().then(setGateway).catch(() => setGateway(null))
  }, [])

  const [seg0, seg1, seg2, seg3] = route.segments
  const routeRunId = seg0 === 'runs' && seg1 ? seg1 : null
  const runId = analysis?.run_id || null

  // A run named in the URL that is not in memory is loaded from disk — this
  // is what makes a reload, a shared link and the saved-run demo work.
  useEffect(() => {
    if (!routeRunId || routeRunId === runId || runLoading) return
    let alive = true
    setRunLoading(true)
    setError(null)
    getRun(routeRunId)
      .then((data) => {
        if (!alive) return
        setAnalysis(data)
        setLastDocuments(null)
        setLabel('')
      })
      .catch((exc) => alive && setError(exc.message || 'Không mở được phiên này.'))
      .finally(() => alive && setRunLoading(false))
    return () => { alive = false }
  }, [routeRunId, runId, runLoading])

  const refreshReviews = useCallback(async (id) => {
    if (!id) return
    try {
      const data = await listReviews(id)
      setReviewStates(data.states || {})
      setReviewDecisions(data.decisions || [])
      const byClaim = {}
      for (const d of data.decisions || []) (byClaim[d.claim_id] ||= []).push(d)
      setReviewHistory(byClaim)
    } catch {
      /* the trail is additive; a failed refresh must not block reviewing */
    }
    exportGold().then((g) => setGoldStats(g.stats)).catch(() => {})
  }, [])

  useEffect(() => { refreshReviews(runId) }, [runId, refreshReviews])

  const rows = useMemo(() => buildRows(analysis?.result), [analysis])
  const summary = useMemo(() => summarise(rows, analysis?.result), [rows, analysis])
  const suggestionsById = useMemo(() => new Map((analysis?.suggestions || []).map((s) => [s.claim_id, s])), [analysis])
  const legalById = useMemo(() => new Map((analysis?.result?.legal_checks || []).map((l) => [l.claim_id, l])), [analysis])

  const saveReviewer = (name, remember = true) => {
    setReviewer(name)
    if (remember && name) localStorage.setItem(REVIEWER_KEY, name)
    if (!name) localStorage.removeItem(REVIEWER_KEY)
  }

  const run = async (fn, label) => {
    setLoading(true)
    setError(null)
    try {
      const data = await fn()
      setAnalysis(data)
      setLabel(label || '')
      if (label) setRunLabel(data.run_id, label).catch(() => {})
      navigate(`/runs/${data.run_id}`)
    } catch (exc) {
      setError(exc.message || 'Không gọi được máy chủ phân tích.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeText = (documents, label) => {
    setLastDocuments(documents)
    return run(() => analyzeText(documents), label)
  }
  const handleAnalyzeFiles = (files, roles, sourceTypes, label) => {
    setLastDocuments(null)
    return run(() => analyzeFiles(files, roles, sourceTypes), label)
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
          evidenceDocs.push({ name: evidence.source_name, text: evidence.text, role: 'evidence', source_type: evidence.source_type })
        }
      }
      documents = [{ name: 'tuyen-bo-sua', text: editedText, role: 'claim_source', source_type: 'internal' }, ...evidenceDocs]
      setLastDocuments(documents)
    }
    return run(() => analyzeText(documents), runLabel ? `${runLabel} (sửa)` : 'Chạy lại sau khi sửa tuyên bố')
  }

  const handleDecide = async (row, { decision, comment, reviewer_status }) => {
    if (!runId || !reviewer.trim()) return
    setReviewBusy(true)
    setError(null)
    try {
      await submitReview({
        run_id: runId, claim_id: row.id, reviewer: reviewer.trim(), decision, comment, reviewer_status,
        ai_status: row.status, ai_risk_score: row.score, evidence: row.evidence, claim: row.claim,
      })
      await refreshReviews(runId)
    } catch (exc) {
      setError(exc.message || 'Không ghi được quyết định.')
    } finally {
      setReviewBusy(false)
    }
  }

  // ---------- routing ----------

  if (!reviewer || seg0 === 'start') {
    return <StartPage reviewer={reviewer} onStart={(name, remember) => { saveReviewer(name, remember); navigate(route.segments.length && seg0 !== 'start' ? route.path : '/new') }} />
  }
  if (!seg0) {
    navigate('/new', { replace: true })
    return null
  }

  const providers = configuredProviders(gateway)
  const modelLabel = providers.length ? `Mô hình: ${providers.join(', ')}` : 'Chạy bằng heuristic'
  const modelState = providers.length ? 'ok' : 'idle'
  const badges = { review: summary.needsConfirmation.length }

  let active = seg0
  let title = ''
  let subtitle = ''
  let body = null

  const needRun = (render) => {
    if (runLoading || (routeRunId && routeRunId !== runId)) {
      return <p className="text-sm text-slate-500">Đang mở phiên {routeRunId}…</p>
    }
    if (!analysis) return <p className="text-sm text-slate-500">Chưa có phiên nào được mở.</p>
    return render()
  }

  if (seg0 === 'new') {
    active = 'new'
    title = 'Phân tích mới'
    subtitle = 'Tải báo cáo hoặc dán tuyên bố → cấu hình → chạy'
    body = (
      <NewAnalysisPage
        onAnalyzeText={handleAnalyzeText}
        onAnalyzeFiles={handleAnalyzeFiles}
        loading={loading}
        error={error}
        gatewayInfo={providers.length ? providers.join(', ') : 'heuristic (không LLM)'}
      />
    )
  } else if (seg0 === 'runs' && !seg1) {
    active = 'runs'
    title = 'Lịch sử phân tích'
    subtitle = 'Mở lại phiên đã lưu — không chạy lại pipeline'
    body = <HistoryPage currentRunId={runId} onLabelChanged={(id, l) => id === runId && setLabel(l)} />
  } else if (seg0 === 'runs' && seg1 && !seg2) {
    active = 'overview'
    title = 'Tổng quan'
    subtitle = runLabel || `Phiên ${seg1}`
    body = needRun(() => (
      <Overview
        summary={summary}
        lastRunAt={analysis?.result?.manifest?.created_at ? new Date(analysis.result.manifest.created_at) : null}
        onOpenQueue={(q, arg) => navigate(`/runs/${runId}/claims?filter=${q}${arg ? `&arg=${encodeURIComponent(arg)}` : ''}`)}
      />
    ))
  } else if (seg0 === 'runs' && seg2 === 'claims' && !seg3) {
    active = 'claims'
    title = 'Danh sách tuyên bố'
    subtitle = `${rows.length} tuyên bố · ${runLabel || seg1}`
    body = needRun(() => (
      <ClaimsPage
        key={`${seg1}-${route.query.get('filter')}-${route.query.get('arg')}`}
        runId={runId}
        rows={rows}
        summary={summary}
        reviewStates={reviewStates}
        initialFilter={route.query.get('filter') || 'all'}
        initialArg={route.query.get('arg')}
      />
    ))
  } else if (seg0 === 'runs' && seg2 === 'claims' && seg3) {
    active = 'claims'
    title = 'Chi tiết tuyên bố'
    subtitle = runLabel || seg1
    body = needRun(() => {
      const idx = rows.findIndex((r) => r.id === seg3)
      const row = idx >= 0 ? rows[idx] : null
      return (
        <ClaimDetailPage
          runId={runId}
          rows={rows}
          row={row}
          index={idx}
          legal={legalById.get(seg3)}
          gates={analysis.result.quality_gates}
          suggestion={suggestionsById.get(seg3)}
          reviewStates={reviewStates}
          reviewHistory={reviewHistory}
          reviewer={reviewer}
          onReviewerChange={saveReviewer}
          onDecide={handleDecide}
          reviewBusy={reviewBusy}
          onRecheck={handleRecheck}
          loading={loading}
          initialTab={route.query.get('tab') || null}
        />
      )
    })
  } else if (seg0 === 'runs' && seg2 === 'review') {
    active = 'review'
    title = 'Xét duyệt'
    subtitle = 'Người xem xét chốt; AI chỉ đề xuất'
    body = needRun(() => (
      <ReviewQueuePage runId={runId} rows={rows} reviewStates={reviewStates} reviewHistory={reviewHistory} goldStats={goldStats} />
    ))
  } else if (seg0 === 'runs' && seg2 === 'export') {
    active = 'export'
    title = 'Xuất hồ sơ'
    subtitle = 'Gói bằng chứng của phiên hiện tại'
    body = needRun(() => (
      <ExportPage runId={runId} runLabel={runLabel} analysis={analysis.result} summary={summary} reviewStates={reviewStates} reviewDecisions={reviewDecisions} />
    ))
  } else if (seg0 === 'legal') {
    active = 'legal'
    title = 'Thư viện pháp lý'
    subtitle = 'Văn bản đã đăng ký cho lớp kiểm tra pháp lý'
    body = <LegalLibraryPage />
  } else if (seg0 === 'settings') {
    active = 'settings'
    title = 'Cài đặt'
    subtitle = 'Chỉ những gì hệ thống thực sự có'
    body = <SettingsPage reviewer={reviewer} onReviewerChange={(n) => saveReviewer(n)} onForget={() => { saveReviewer(''); navigate('/start') }} />
  } else {
    title = 'Không tìm thấy trang'
    body = <p className="text-sm text-slate-500">Đường dẫn không hợp lệ.</p>
  }

  return (
    <Shell
      active={active}
      runId={runId}
      runLabel={runLabel}
      reviewer={reviewer}
      apiStatus={apiStatus}
      modelLabel={modelLabel}
      modelState={modelState}
      title={title}
      subtitle={subtitle}
      badges={badges}
    >
      {error && seg0 !== 'new' && (
        <div className="mb-4 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          <b>Lỗi:</b> <code className="font-mono text-xs">{error}</code>
        </div>
      )}
      {body}
    </Shell>
  )
}
