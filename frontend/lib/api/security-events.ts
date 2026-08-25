import { authenticatedFetch } from './client'

export type SecurityEventSeverity = 'low' | 'medium' | 'high' | 'critical'

export type SecurityEventStatus =
  | 'open'
  | 'processing'
  | 'processed'
  | 'failed'
  | 'suppressed'

export interface SecurityEvent {
  readonly id: string
  readonly tenant_id: string
  readonly source_event_id?: string | null
  readonly event_fingerprint?: string | null
  readonly correlation_id?: string | null
  readonly parent_event_id?: string | null
  readonly event_time: string
  readonly ingested_at: string
  readonly created_at: string
  readonly schema_version: number
  readonly event_category: string
  readonly source: string
  readonly source_type: string
  readonly event_type: string
  readonly severity: SecurityEventSeverity
  readonly status: SecurityEventStatus
  readonly action?: string | null
  readonly risk_score?: number | null
  readonly source_ip?: string | null
  readonly destination_ip?: string | null
  readonly source_port?: number | null
  readonly destination_port?: number | null
  readonly protocol?: string | null
  readonly hostname?: string | null
  readonly user_identifier?: string | null
  readonly process_name?: string | null
  readonly process_id?: number | null
  readonly mitre_tactic?: string | null
  readonly mitre_technique?: string | null
  readonly mitre_technique_id?: string | null
  readonly message?: string | null
  readonly raw_event?: Record<string, unknown> | null
  readonly normalized_data?: Record<string, unknown> | null
  readonly event_metadata?: Record<string, unknown> | null
}

export interface SecurityEventListResponse {
  readonly items: SecurityEvent[]
  readonly total: number
  readonly limit: number
  readonly offset: number
}

export interface SecurityEventFilters {
  readonly q?: string
  readonly tenantId?: string
  readonly severity?: SecurityEventSeverity
  readonly status?: SecurityEventStatus
  readonly event_category?: string
  readonly event_type?: string
  readonly source?: string
  readonly source_type?: string
  readonly hostname?: string
  readonly user_identifier?: string
  readonly mitre_technique_id?: string
  readonly start_time?: string
  readonly end_time?: string
  readonly limit?: number
  readonly offset?: number
}

export interface SecurityEventUpdate {
  readonly status?: SecurityEventStatus
  readonly severity?: SecurityEventSeverity
  readonly message?: string | null
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  const isJson = contentType.includes('application/json')

  if (response.ok) {
    if (!isJson) {
      throw new ApiError(
        response.status,
        'The API returned an unexpected response format.',
      )
    }

    return (await response.json()) as T
  }

  let detail = `API_ERROR_${response.status}`

  if (isJson) {
    try {
      const body: unknown = await response.json()

      if (isRecord(body)) {
        if (typeof body.detail === 'string') {
          detail = body.detail
        } else if (body.detail !== undefined) {
          detail = JSON.stringify(body.detail)
        }
      }
    } catch {
      // Preserve the status-based fallback.
    }
  }

  throw new ApiError(response.status, detail)
}

async function apiFetch(
  endpoint: string,
  options: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(options.headers)

  headers.set('Accept', 'application/json')

  if (options.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  return authenticatedFetch(`/api/security-events${endpoint}`, {
    ...options,
    headers,
  })
}

function buildQueryString(filters: SecurityEventFilters = {}): string {
  const params = new URLSearchParams()
  const queryFilters: Record<string, unknown> = {
    q: filters.q,
    tenant_id: filters.tenantId,
    severity: filters.severity,
    status: filters.status,
    event_category: filters.event_category,
    event_type: filters.event_type,
    source: filters.source,
    source_type: filters.source_type,
    hostname: filters.hostname,
    user_identifier: filters.user_identifier,
    mitre_technique_id: filters.mitre_technique_id,
    start_time: filters.start_time,
    end_time: filters.end_time,
    limit: filters.limit,
    offset: filters.offset,
  }
  for (const [key, value] of Object.entries(queryFilters)) {
    if (value === undefined || value === null) {
      continue
    }
    if (typeof value === 'string' && value.trim() === '') {
      continue
    }
    params.set(key, String(value))
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}
export async function getSecurityEvents(
  filters: SecurityEventFilters = {},
): Promise<SecurityEventListResponse> {
  const response = await apiFetch(buildQueryString(filters))
  return handleResponse<SecurityEventListResponse>(response)
}

export async function getSecurityEvent(
  eventId: string,
): Promise<SecurityEvent> {
  const response = await apiFetch(`/${encodeURIComponent(eventId)}`)

  return handleResponse<SecurityEvent>(response)
}

export async function updateSecurityEvent(
  eventId: string,
  updates: SecurityEventUpdate,
): Promise<SecurityEvent> {
  if (Object.keys(updates).length === 0) {
    throw new TypeError('At least one update field is required.')
  }

  const response = await apiFetch(`/${encodeURIComponent(eventId)}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })

  return handleResponse<SecurityEvent>(response)
}

export async function deleteSecurityEvent(eventId: string): Promise<void> {
  const response = await apiFetch(`/${encodeURIComponent(eventId)}`, {
    method: 'DELETE',
  })

  await handleResponse<void>(response)
}
