import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  analyzeText, checkHealth, getRun, listReviews, runtimeInfo, setRunLabel, submitReview,
} from './api.js'
import { navigate, useHashRoute } from './lib/router.jsx'
import { buildRows, summarise } from './lib/claims.js'
import { buildQueue } from './lib/queue.js'
import Shell from './components/Shell.jsx'
import StartPage from './pages/StartPage.jsx'
import NewAnalysisPage from './pages/NewAnalysisPage.jsx'
import ClaimsPage from './pages/ClaimsPage.jsx'
import ClaimDetailPage from './pages/ClaimDetailPage.jsx'
import QueuePage from './pages/QueuePage.jsx'
import ExportPage from './pages/ExportPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import LegalLibraryPage from './pages/LegalLibraryPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

const REVIEWER_KEY = 'greenscan.reviewer'

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
  const [runtime, setRuntime] = useState(null)
  const [reviewStates, setReviewStates] = useState({})
  const [reviewHistory, setReviewHistory] = useState({})
  const [reviewDecisions, setReviewDecisions] = useState([])
  const [reviewBusy, setReviewBusy] = useState(false)

  useEffect(() => {
    checkHealth().then(() => setApiStatus('online')).catch(() => setApiStatus('offline'))
    runtimeInfo().then(setRuntime).catch(() => setRuntime(null))
  }, [])

  const [seg0, seg1, seg2, seg3] = route.segments
  const routeRunId = seg0 === 'runs' && seg1 ? seg1 : null
  const runId = analysis?.run_id || null

  // A run named in the URL that is not in memory is loaded from disk — this
  // is what makes a reload, a shared link and the saved-run demo work.
  //
  // `runLoading` must not be a dependency: setting it re-ran the effect, whose
  // cleanup marked the request in flight as stale and whose new run returned
  // early because loading was already true — so a run opened from History, a
  // reload or a shared link stayed on "Đang mở phiên…" forever (found 06/10).
  useEffect(() => {
    if (!routeRunId || routeRunId === runId) return undefined
    let alive = true
    setRunLoading(true)
    setError(null)
    getRun(routeRunId)
      .then((data) => {
        if (!alive) return
        setAnalysis(data)
        setLastDocuments(null)
        setLabel(data.label || '')
      })
      .catch((exc) => alive && setError(exc.message || 'Không mở được phiên này.'))
      .finally(() => alive && setRunLoading(false))
    return () => {
      alive = false
      setRunLoading(false)
    }
  }, [routeRunId, runId])

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
  }, [])

  useEffect(() => { refreshReviews(runId) }, [runId, refreshReviews])

  const rows = useMemo(() => buildRows(analysis?.result), [analysis])
  const summary = useMemo(() => summarise(rows, analysis?.result), [rows, analysis])
  const suggestionsById = useMemo(() => new Map((analysis?.suggestions || []).map((s) => [s.claim_id, s])), [analysis])
  const legalById = useMemo(() => new Map((analysis?.result?.legal_checks || []).map((l) => [l.claim_id, l])), [analysis])
  const queue = useMemo(() => buildQueue(analysis?.result, rows), [analysis, rows])
  // Claim ids in the order the queue presents them: "next" on a claim opened
  // from the queue moves down the queue, not down the document.
  const queueOrder = useMemo(() => queue.items.filter((i) => i.item_type === 'claim').map((i) => i.item_id), [queue])

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

  // A background job finished: open its queue. The run is read back from
  // disk by the route effect above, exactly like a reload or a shared link.
  const handleDone = (id, label) => {
    setLastDocuments(null)
    setLabel(label || '')
    navigate(`/runs/${id}`)
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

  const openInQueue = queue.queued.filter((i) => i.item_type !== 'claim' || reviewStates[i.item_id] !== 'FINALIZED').length
  const badges = { queue: openInQueue }

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
    title = 'Tải tài liệu'
    subtitle = 'Chọn báo cáo cần kiểm và tài liệu đối chiếu, rồi chạy'
    body = <NewAnalysisPage onDone={handleDone} runtime={runtime} />
  } else if (seg0 === 'runs' && !seg1) {
    active = 'runs'
    title = 'Lịch sử phân tích'
    subtitle = 'Mở lại phiên đã lưu — không chạy lại pipeline'
    body = <HistoryPage currentRunId={runId} onLabelChanged={(id, l) => id === runId && setLabel(l)} />
  } else if (seg0 === 'runs' && seg1 && (!seg2 || seg2 === 'review')) {
    if (seg2 === 'review') navigate(`/runs/${seg1}`, { replace: true })  // old link to the review page
    active = 'queue'
    title = 'Soát theo hàng đợi'
    subtitle = 'Mở các mục theo thứ tự; xác nhận hoặc sửa kết quả của AI'
    body = needRun(() => (
      <QueuePage
        runId={runId}
        runLabel={runLabel}
        result={analysis.result}
        rows={rows}
        summary={summary}
        reviewStates={reviewStates}
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
    const fromQueue = route.query.get('from') === 'queue'
    active = fromQueue ? 'queue' : 'claims'
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
          order={fromQueue ? queueOrder : null}
        />
      )
    })
  } else if (seg0 === 'runs' && seg2 === 'export') {
    active = 'export'
    title = 'Giấy làm việc'
    subtitle = 'In hoặc lưu PDF kèm quyết định của người soát xét'
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
      runtime={runtime}
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
