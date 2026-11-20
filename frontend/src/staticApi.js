/**
 * Bản trình diễn tĩnh (VITE_STATIC=1): giao diện thật chạy trên các phản hồi API đã xuất sẵn.
 *
 * tools/build_static_demo.py gọi chính máy chủ GreenScan (FastAPI) trên các phiên đã chạy và ghi mọi phản hồi
 * GET ra thư mục `static-api/` theo đúng đường dẫn endpoint. Lớp này chặn `fetch('/api/...')` và đọc tệp tương ứng.
 * Quyết định của người soát được ghi vào localStorage của trình duyệt (mỗi người xem một bản), theo đúng luật của
 * storage/reviews.py: chỉ ghi thêm, ghi đè phải có kết luận thay thế và lý do, đã chốt thì phải mở lại.
 * Các việc cần máy chủ (phân tích tài liệu mới, tải bộ quy tắc, xuất bản sửa) trả lời rõ là cần bản cài đặt.
 */

export const STATIC = import.meta.env.VITE_STATIC === '1'
const ROOT = 'static-api'
const NEED_SERVER = 'Bản trình diễn tĩnh không chạy được việc này vì cần máy chủ phân tích. Hãy cài bản đầy đủ theo Hướng dẫn (mục 2, khoảng 10 phút) hoặc xem video demo. Các phiên đã chạy sẵn vẫn xem và soát được đầy đủ.'
const LOCAL_KEY = 'gs.static.reviews'
const TRANSITIONS = { CONFIRM: 'FINALIZED', OVERRIDE: 'FINALIZED', ABSTAIN: 'HUMAN_REVIEWED', REQUEST_EVIDENCE: 'HUMAN_REVIEWED', REOPEN: 'HUMAN_REVIEWED' }
const RULE_REASONS = ['RULE_NOT_APPLICABLE', 'RULE_WRONG']

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
const fail = (detail, status = 400) => json({ detail }, status)

function localReviews() {
  try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]') } catch { return [] }
}
function saveLocal(rows) {
  try { localStorage.setItem(LOCAL_KEY, JSON.stringify(rows)) } catch { /* trình duyệt chặn lưu: quyết định chỉ còn trong phiên này */ }
}

async function staticJson(path) {
  const r = await fetch(`${ROOT}/${path}.json`)
  if (!r.ok) return null
  return r.json()
}

async function reviewsFor(runId) {
  const shipped = (await staticJson(`v1/reviews/${runId}`))?.decisions || []
  const decisions = [...shipped, ...localReviews().filter((r) => r.run_id === runId)]
  const states = {}
  for (const d of decisions) states[d.claim_id] = d.new_state
  return { run_id: runId, states, decisions }
}

function stageOf(body, evidence) {
  if (body.decision === 'CONFIRM') return 'none'
  if (body.decision !== 'OVERRIDE') return ''
  if (RULE_REASONS.includes(body.override_reason)) return 'rule'
  const shown = new Set((evidence || []).map((e) => e.chunk_id))
  if (body.decisive_chunk_ids?.length) return body.decisive_chunk_ids.some((c) => shown.has(c)) ? 'reading' : 'retrieval'
  if ((body.decisive_quote || '').trim()) return 'retrieval'
  if (body.override_reason === 'EVIDENCE_MISSED') return 'retrieval'
  if (body.override_reason === 'MODEL_MISREAD') return 'reading'
  return 'unknown'
}

async function postReview(body) {
  const decision = (body.decision || '').toUpperCase()
  if (!TRANSITIONS[decision]) return fail('Quyết định không hợp lệ.')
  if (!(body.reviewer || '').trim()) return fail('Cần tên người xem xét.')
  if (decision === 'OVERRIDE' && (!body.reviewer_status || !body.override_reason)) return fail('Ghi đè cần kết luận thay thế và lý do máy sai.')
  if (RULE_REASONS.includes(body.override_reason) && !(body.rule_ref || '').trim()) return fail('Lý do quy cho quy tắc cần ghi quy tắc nào.')
  const { states } = await reviewsFor(body.run_id)
  const previous = states[body.claim_id] || 'AI_SUGGESTED'
  if (decision === 'REOPEN' && previous !== 'FINALIZED') return fail('Chỉ mở lại được tuyên bố đã chốt.')
  if ((decision === 'CONFIRM' || decision === 'OVERRIDE') && previous === 'FINALIZED') return fail('Tuyên bố đã chốt; mở lại trước khi quyết định lại.')
  const record = {
    decision_id: Math.random().toString(16).slice(2, 18), run_id: body.run_id, claim_id: body.claim_id,
    reviewer: body.reviewer.trim(), decided_at: new Date().toISOString(), decision, previous_state: previous,
    new_state: TRANSITIONS[decision], comment: (body.comment || '').trim(), ai_status: body.ai_status,
    ai_risk_score: body.ai_risk_score, reviewer_status: body.reviewer_status || null,
    override_reason: body.override_reason || null, rule_ref: body.rule_ref || '',
    decisive_chunk_ids: body.decisive_chunk_ids || [], decisive_quote: body.decisive_quote || '',
    reviewer_role: body.reviewer_role || '', error_stage: stageOf({ ...body, decision }, body.evidence),
    evidence_snapshot: [], claim_snapshot: body.claim || {}, stored_in: 'trình duyệt (bản trình diễn tĩnh)',
  }
  saveLocal([...localReviews(), record])
  return json(record)
}

async function route(path, method, init) {
  if (method !== 'GET') {
    if (path === 'v1/reviews') return postReview(JSON.parse(init?.body || '{}'))
    return fail(NEED_SERVER)
  }
  let m = path.match(/^v1\/reviews\/([^/]+)$/)
  if (m) return json(await reviewsFor(m[1]))
  m = path.match(/^v1\/reviews\/([^/]+)\/([^/]+)$/)
  if (m) {
    const all = await reviewsFor(m[1])
    const history = all.decisions.filter((d) => d.claim_id === m[2])
    return json({ run_id: m[1], claim_id: m[2], state: all.states[m[2]] || 'AI_SUGGESTED', history })
  }
  m = path.match(/^v1\/documents\/([^/]+)\/page\/(\d+)$/)
  if (m) return fetch(`${ROOT}/v1/documents/${m[1]}/page/${m[2]}.jpg`)
  if (/^v1\/(jobs|intake\/preview|intake\/fetch|analyze)/.test(path)) return fail(NEED_SERVER)
  const body = await staticJson(path)
  return body == null ? fail('Bản trình diễn tĩnh không có dữ liệu này.', 404) : json(body)
}

export function installStaticApi(base) {
  if (!STATIC) return
  const real = window.fetch.bind(window)
  window.fetch = (input, init = {}) => {
    const url = typeof input === 'string' ? input : input.url
    if (!url.startsWith(`${base}/`)) return real(input, init)
    const path = decodeURIComponent(url.slice(base.length + 1).split('?')[0].split('#')[0]).replace(/\/$/, '')
    return route(path, (init.method || 'GET').toUpperCase(), init)
  }
  const bar = document.createElement('div')
  bar.textContent = 'Bản trình diễn tĩnh: xem và soát các phiên đã chạy sẵn bằng chính giao diện của GreenScan; quyết định soát lưu trong trình duyệt của bạn. Phân tích tài liệu mới cần bản cài đặt (Hướng dẫn mục 2).'
  bar.style.cssText = 'position:sticky;top:0;z-index:60;background:#047857;color:#fff;font:12px/1.4 Roboto Variable,Roboto,Segoe UI,system-ui,sans-serif;padding:6px 12px;text-align:center'
  document.body.prepend(bar)
  // The sidebar and the Studio page are one screen tall: they start below this banner, not under it.
  const measure = () => document.documentElement.style.setProperty('--gs-banner-h', `${bar.offsetHeight}px`)
  measure()
  window.addEventListener('resize', measure)
}

/** Static paths for links and images (not fetched, so the shim cannot see them). */
export const staticUrls = {
  document: (docId, page) => `${ROOT}/v1/documents/${encodeURIComponent(docId)}.pdf${page ? `#page=${page}` : ''}`,
  page: (docId, page) => `${ROOT}/v1/documents/${encodeURIComponent(docId)}/page/${page}.jpg`,
  exportFile: (runId, format) => `${ROOT}/v1/runs/${encodeURIComponent(runId)}/export/${format}.${format === 'md' ? 'md' : format === 'csv' ? 'csv' : 'json'}`,
  workpaper: (runId) => `${ROOT}/v1/runs/${encodeURIComponent(runId)}/workpaper.html`,
}
