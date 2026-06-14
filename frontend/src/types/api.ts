// ── Query ──────────────────────────────────────────────────────────────────
export type QualityTier = 'brief' | 'standard' | 'detailed'

export interface QueryRequest {
  query: string
  quality_tier?: QualityTier
  language?: string
}

export interface QueryResponse {
  query: string
  response: string
  cache_hit: boolean
  similarity_score?: number
  quality_tier: QualityTier
  language: string
  tokens_saved: number
  water_saved_ml: number
  energy_saved_wh: number
  latency_ms: number
  cache_backend: string
}

// ── Stats ──────────────────────────────────────────────────────────────────
export interface StatsResponse {
  total_requests: number
  cache_hits: number
  cache_misses: number
  hit_rate: number
  total_tokens_saved: number
  entries_count: number
  backend: string
}

// ── Impact ─────────────────────────────────────────────────────────────────
export interface ImpactResponse {
  total_queries: number
  cache_hit_rate: number
  total_tokens_saved: number
  total_energy_saved_wh: number
  total_water_saved_ml: number
  total_water_saved_liters: number
  equivalent_cars_km: number
  equivalent_trees: number
}

// ── Health ─────────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string
  backend: string
}

// ── UI State ───────────────────────────────────────────────────────────────
export type NavView = 'query' | 'stats' | 'impact' | 'settings'

export interface QueryHistoryItem {
  id: string
  query: string
  cache_hit: boolean
  latency_ms: number
  timestamp: number
  response: string
  tokens_saved: number
  water_saved_ml: number
  energy_saved_wh: number
  similarity_score?: number
}

export interface AppSettings {
  apiBaseUrl: string
  similarityThreshold: number
  darkMode: boolean
  autoRefreshImpact: boolean
}
