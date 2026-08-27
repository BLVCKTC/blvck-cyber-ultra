import { API_URL, authenticatedFetch } from './client'

export interface ApiAsset {
  id: string
  tenant_id: string
  canonical_name: string
  asset_type: string
  criticality: number
  metadata_json?: Record<string, unknown> | null
  last_seen_at?: string | null
  created_at: string
}

async function request<T>(path: string): Promise<T> {
  const response = await authenticatedFetch(`${API_URL}${path}`, {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${response.status})`)
  }
  return response.json()
}

export function getAssets() {
  return request<ApiAsset[]>('/intelligence/assets')
}

export const assetsKey = '/intelligence/assets'
