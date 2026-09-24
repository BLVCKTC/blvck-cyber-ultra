import { authenticatedFetch, tenantApiPath } from './client'

export type AlertSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical'

export type AlertStatus =
  | 'new'
  | 'open'
  | 'acknowledged'
  | 'investigating'
  | 'resolved'
  | 'suppressed'
  | 'false_positive'

export interface Alert {
  id: string
  tenant_id: string
  fingerprint: string
  title: string
  description?: string | null
  severity: AlertSeverity
  status: AlertStatus
  detection_rule_id?: string | null
  security_event_id?: string | null
  confidence?: number | null
  risk_score?: number | null
  source?: string | null
  first_seen_at: string
  last_seen_at: string
  created_at: string
  updated_at: string
  metadata_json: Record<string, unknown>
}

export interface AlertList {
  items: Alert[]
  total: number
  limit: number
  offset: number
}

const path = (tenantId: string) => tenantApiPath(tenantId, 'alerts')

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await authenticatedFetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => null)

    throw new Error(error?.detail ?? `Request failed (${response.status})`)
  }

  return response.status === 204 ? (undefined as T) : response.json()
}

export function getAlerts(
  tenantId: string,
  params: Record<string, string | number | boolean | undefined> = {},
) {
  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, value]) => value !== undefined)
      .map(([key, value]) => [key, String(value)]),
  )

  const queryString = query.toString()

  return request<AlertList>(
    queryString ? `${path(tenantId)}?${queryString}` : path(tenantId),
  )
}

export function getAlert(tenantId: string, id: string) {
  return request<Alert>(`${path(tenantId)}/${encodeURIComponent(id)}`)
}

export function createAlert(
  tenantId: string,
  payload: Omit<
    Alert,
    | 'id'
    | 'tenant_id'
    | 'first_seen_at'
    | 'last_seen_at'
    | 'created_at'
    | 'updated_at'
  >,
) {
  return request<Alert>(path(tenantId), {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateAlert(
  tenantId: string,
  id: string,
  payload: Partial<
    Pick<
      Alert,
      | 'title'
      | 'description'
      | 'severity'
      | 'status'
      | 'confidence'
      | 'risk_score'
      | 'metadata_json'
    >
  >,
) {
  return request<Alert>(`${path(tenantId)}/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deleteAlert(tenantId: string, id: string) {
  return request<void>(`${path(tenantId)}/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
}
