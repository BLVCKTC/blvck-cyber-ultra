import { authenticatedFetch, tenantApiPath } from './client'

export type IncidentStatus = 'open' | 'investigating' | 'contained' | 'resolved'
export type IncidentSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface Incident {
  id: string
  tenant_id: string
  title: string
  severity: IncidentSeverity | string
  status: IncidentStatus | string
  summary?: string | null
  owner_user_id?: string | null
  created_at: string
  updated_at: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await authenticatedFetch(tenantApiPath(path), {
    ...init,
    headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${response.status})`)
  }
  return response.json()
}

export function getIncidents() {
  return request<Incident[]>('/incidents')
}

export function getIncident(id: string) {
  return request<Incident>(`/incidents/${encodeURIComponent(id)}`)
}

export function createIncident(input: Pick<Incident, 'title' | 'severity' | 'summary'>) {
  return request<Incident>('/incidents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
}

export const incidentsKey = '/incidents'
