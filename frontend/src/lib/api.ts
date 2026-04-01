import type { AnalyzeResponse, ApiError, HistoryResponse } from './types'

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  if (!text) return {} as T
  return JSON.parse(text) as T
}

export async function analyzeTongue(params: { patientId: string; file: File }): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('patient_id', params.patientId)
  form.append('file', params.file)

  const res = await fetch('/api/analyze', { method: 'POST', body: form })
  if (!res.ok) {
    const err = await parseJson<ApiError>(res).catch(() => undefined)
    throw new Error(err?.detail || `Request failed (${res.status})`)
  }
  return (await res.json()) as AnalyzeResponse
}

export async function fetchHistory(patientId: string): Promise<HistoryResponse> {
  const res = await fetch(`/api/history/${encodeURIComponent(patientId)}`)
  if (!res.ok) {
    const err = await parseJson<ApiError>(res).catch(() => undefined)
    throw new Error(err?.detail || `Request failed (${res.status})`)
  }
  return (await res.json()) as HistoryResponse
}

