const BASE = import.meta.env.VITE_API_URL || '/api'

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
  const anchor = page ? `#page=${page}` : ''
  return `${base()}/v1/documents/${encodeURIComponent(docId)}${anchor}`
}

/** Server-rendered page image with `snippet` highlighted. */
export function documentPageUrl(docId, page, snippet, zoom = 2) {
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
  return `${base()}/v1/runs/${encodeURIComponent(runId)}/export?format=${format}`
}

export async function legalCorpus() {
  return handle(await fetch(`${base()}/v1/legal/corpus`))
}

export async function exportGold() {
  return handle(await fetch(`${base()}/v1/reviews-export/gold`))
}
