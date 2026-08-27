import { API_URL, authenticatedFetch } from './client'

export interface ApiVulnerability {
  id: string
  tenant_id: string
  cve: string
  title: string
  severity: string
  cvss_score?: number | null
  description?: string | null
  metadata_json?: Record<string, unknown> | null
  created_at: string
}

export async function getVulnerabilities(): Promise<ApiVulnerability[]> {
  const response = await authenticatedFetch(`${API_URL}/intelligence/vulnerabilities`, {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) throw new Error('Unable to load vulnerabilities')
  return response.json()
}

export const vulnerabilitiesKey = '/intelligence/vulnerabilities'
