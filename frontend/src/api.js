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
