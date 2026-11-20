const BASE = import.meta.env.VITE_API_URL || '/api'
import { STATIC, installStaticApi, staticUrls } from './staticApi.js'
installStaticApi(BASE)

async function handle(response) {
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (body.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* keep default detail */
    }
    throw new Error(detail)
  }
  return response.json()
}

export async function checkHealth() {
  return handle(await fetch(`${BASE}/health`))
}

/** Which model providers are reachable. Drives the header badge. */
export async function gatewayHealth() {
  return handle(await fetch(`${BASE}/v1/gateway/health`))
}

export async function analyzeText(documents) {
  return handle(
    await fetch(`${BASE}/v1/analyze/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ documents }),
    }),
  )
}

export async function analyzeFiles(files, roles, sourceTypes) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('roles', roles.join(','))
  form.append('source_types', sourceTypes.join(','))
  return handle(await fetch(`${BASE}/v1/analyze/files`, { method: 'POST', body: form }))
}

const base = () => BASE

/** Direct link to the stored original. `#page=N` is honoured by browser PDF viewers. */
export function documentUrl(docId, page) {
  if (STATIC) return staticUrls.document(docId, page)
  const anchor = page ? `#page=${page}` : ''
  return `${base()}/v1/documents/${encodeURIComponent(docId)}${anchor}`
}

/** Server-rendered page image with `snippet` highlighted. */
export function documentPageUrl(docId, page, snippet, zoom = 2) {
  if (STATIC) return staticUrls.page(docId, page)
  const params = new URLSearchParams({ q: (snippet || '').slice(0, 400), zoom: String(zoom) })
  return `${base()}/v1/documents/${encodeURIComponent(docId)}/page/${page}?${params}`
}

export async function documentMeta(docId) {
  return handle(await fetch(`${base()}/v1/documents/${encodeURIComponent(docId)}/meta`))
}

export async function submitReview(payload) {
  return handle(await fetch(`${base()}/v1/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}

export async function listReviews(runId) {
  return handle(await fetch(`${base()}/v1/reviews/${encodeURIComponent(runId)}`))
}

// ---------- saved runs ----------

export async function listRuns(limit = 50) {
  return handle(await fetch(`${base()}/v1/runs?limit=${limit}`))
}

export async function getRun(runId) {
  return handle(await fetch(`${base()}/v1/runs/${encodeURIComponent(runId)}`))
}

export async function setRunLabel(runId, label) {
  return handle(await fetch(`${base()}/v1/runs/${encodeURIComponent(runId)}/label`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label }),
  }))
}

/** Download link for one evidence-pack artifact: json | md | manifest | audit. */
export function exportUrl(runId, format) {
  if (STATIC) return staticUrls.exportFile(runId, format)
  return `${base()}/v1/runs/${encodeURIComponent(runId)}/export?format=${format}`
}

export async function orgPacks() {
  return handle(await fetch(`${base()}/v1/org-packs`))
}

export async function legalCorpus() {
  return handle(await fetch(`${base()}/v1/legal/corpus`))
}

export async function exportGold() {
  return handle(await fetch(`${base()}/v1/reviews-export/gold`))
}

// ---------- background analyses (progress instead of one long request) ----------

/** Start an analysis of uploaded files; resolves with the job status at once. */
export async function startAnalysisFiles(files, roles, sourceTypes, label = '', company = '', orgPacks = []) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('roles', roles.join(','))
  form.append('source_types', sourceTypes.join(','))
  form.append('label', label)
  form.append('company', company)
  // Uploaded org packs chosen for this run: "org_id" (latest approved) or "org_id@version".
  form.append('org_packs', orgPacks.join(','))
  return handle(await fetch(`${base()}/v1/jobs/analyze/files`, { method: 'POST', body: form }))
}

export async function startAnalysisText(documents, label = '', company = '', orgPacks = []) {
  return handle(await fetch(`${base()}/v1/jobs/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ documents, label, company, org_packs: orgPacks }),
  }))
}

// ---------- org packs sent over the API (org-pack-v1) ----------

/** Upload a zip of a pack folder, or pack.yaml with its documents. Always stored as a draft. */
export async function uploadOrgPack(files, uploadedBy, note = '') {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('uploaded_by', uploadedBy)
  form.append('note', note)
  return handle(await fetch(`${base()}/v1/org-packs/upload`, { method: 'POST', body: form }))
}

async function orgPackDecision(orgId, version, action, by, comment = '') {
  return handle(await fetch(`${base()}/v1/org-packs/${encodeURIComponent(orgId)}/${encodeURIComponent(version)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ by, comment }),
  }))
}
export const approveOrgPack = (orgId, version, by, comment) => orgPackDecision(orgId, version, 'approve', by, comment)
export const retireOrgPack = (orgId, version, by, comment) => orgPackDecision(orgId, version, 'retire', by, comment)

export async function previewOrgPack(pack, text, sector = '') {
  return handle(await fetch(`${base()}/v1/org-packs/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pack, text, sector }),
  }))
}

/** Draft a pack from a policy text; stored as a draft that someone else must approve. */
export async function draftOrgPack({ orgId, orgName, uploadedBy, orgType = 'other', policyText = '', useLlm = false }) {
  const form = new FormData()
  form.append('org_id', orgId)
  form.append('org_name', orgName)
  form.append('uploaded_by', uploadedBy)
  form.append('org_type', orgType)
  form.append('use_llm', useLlm ? 'true' : 'false')
  form.append('policy_text', policyText)
  return handle(await fetch(`${base()}/v1/org-packs/draft`, { method: 'POST', body: form }))
}

// ---------- feedback loop (docs/03-architecture/FEEDBACK_LOOP.md) ----------

export async function feedbackSummary() {
  return handle(await fetch(`${base()}/v1/feedback/summary`))
}

export async function feedbackProposals() {
  return handle(await fetch(`${base()}/v1/feedback/proposals`))
}

export async function secondReviewSample(rate = 0.1) {
  return handle(await fetch(`${base()}/v1/feedback/second-review-sample?rate=${rate}`))
}

/** kind: second_review | adjudication | core_promotion */
export async function submitQA(payload) {
  return handle(await fetch(`${base()}/v1/feedback/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}

export async function jobStatus(jobId) {
  return handle(await fetch(`${base()}/v1/jobs/${encodeURIComponent(jobId)}`))
}

/** Which engine serves which task on this installation (header + settings). */
export async function runtimeInfo() {
  return handle(await fetch(`${base()}/v1/runtime`))
}

/** Turn the language-model stages on or off for the next runs: 'rules' | 'local' | 'cloud'. Returns the new runtime. */
export async function setModelMode(mode) {
  return handle(await fetch(`${base()}/v1/runtime/model-mode`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mode }),
  }))
}

/** One short live call to the model that is switched on. */
export async function testModel() {
  return handle(await fetch(`${base()}/v1/runtime/model-test`, { method: 'POST' }))
}

/** The Vietnamese working paper; `print` opens the browser's print dialog. */
export function workpaperUrl(runId, print = false) {
  if (STATIC) return staticUrls.workpaper(runId)
  return `${base()}/v1/runs/${encodeURIComponent(runId)}/workpaper${print ? '?print=true' : ''}`
}

// ---------- intake: preview, URL, demo samples ----------

/** What each file will give the pipeline: pages with text, scanned pages, OCR, sentences, time, a first guess. */
export async function intakePreview(files) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  return handle(await fetch(`${BASE}/v1/intake/preview`, { method: 'POST', body: form }))
}

async function asFile(response, fallbackName) {
  if (!response.ok) await handle(response)
  const name = decodeURIComponent(response.headers.get('X-File-Name') || '') || fallbackName
  return new File([await response.blob()], name)
}

/** The server downloads the report (the browser cannot); it comes back as an ordinary File. */
export async function intakeFetch(url) {
  return asFile(await fetch(`${BASE}/v1/intake/fetch?url=${encodeURIComponent(url)}`), 'tai-lieu')
}

export async function intakeSamples() {
  return handle(await fetch(`${BASE}/v1/intake/samples`))
}

export async function intakeSampleFile(sampleId, index, name) {
  return asFile(await fetch(`${BASE}/v1/intake/samples/${sampleId}/${index}`), name)
}

// ---------- GreenScan Studio ----------

export async function studioRun(runId) {
  return handle(await fetch(`${BASE}/v1/studio/${runId}`))
}

export async function studioDoc(runId, docId) {
  return handle(await fetch(`${BASE}/v1/studio/${runId}/doc/${docId}`))
}

export async function studioSave(runId, docId, body) {
  return handle(
    await fetch(`${BASE}/v1/studio/${runId}/doc/${docId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )
}

export async function studioRestore(runId, docId, version) {
  return handle(
    await fetch(`${BASE}/v1/studio/${runId}/doc/${docId}/restore`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version }),
    }),
  )
}

export function studioExportUrl(runId, docId, format, user) {
  return `${BASE}/v1/studio/${runId}/doc/${docId}/export?format=${format}&user=${encodeURIComponent(user || '')}`
}
