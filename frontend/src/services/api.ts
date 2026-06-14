import type {
  QueryRequest,
  QueryResponse,
  StatsResponse,
  ImpactResponse,
  HealthResponse,
} from '../types/api'

let BASE_URL = 'http://localhost:8000'

export function setBaseUrl(url: string) {
  BASE_URL = url.replace(/\/$/, '')
}

export function getBaseUrl() {
  return BASE_URL
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export async function postQuery(req: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  return handleResponse<QueryResponse>(res)
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/stats`)
  return handleResponse<StatsResponse>(res)
}

export async function getImpact(): Promise<ImpactResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/impact`)
  return handleResponse<ImpactResponse>(res)
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/health`)
  return handleResponse<HealthResponse>(res)
}

export async function clearCache(): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/v1/cache`, { method: 'DELETE' })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${text}`)
  }
}