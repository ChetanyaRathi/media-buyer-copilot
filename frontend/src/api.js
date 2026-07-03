const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function handle(response) {
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch (error) {
      void error
    }
    throw new Error(detail)
  }
  return response.json()
}

export async function analyze(files) {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  return handle(await fetch(`${BASE}/analyze`, { method: 'POST', body: form }))
}

export async function analyzeSample() {
  return handle(await fetch(`${BASE}/analyze/sample`, { method: 'POST' }))
}

export async function chat(question, context) {
  return handle(
    await fetch(`${BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context })
    })
  )
}
