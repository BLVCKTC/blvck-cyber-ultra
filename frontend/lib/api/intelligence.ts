import { authenticatedFetch, tenantApiPath } from './client'

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

async function request<T>(tenantId: string, path: string): Promise<T> {
  const response = await authenticatedFetch(tenantApiPath(tenantId, path), {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${response.status})`)
  }
  return response.json()
}

export function getAssets(tenantId: string) {
  return request<ApiAsset[]>(tenantId, '/intelligence/assets')
}

export const assetsKey = '/intelligence/assets'
