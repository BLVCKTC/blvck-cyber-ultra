import { authenticatedFetch } from './client'

const SECURITY_EVENTS_ENDPOINT = '/api/security-events'

function tenantSecurityEventsEndpoint(tenantId?: string): string {
  return tenantId
    ? `/api/v1/tenants/${encodeURIComponent(tenantId)}/security-events`
    : SECURITY_EVENTS_ENDPOINT
}

export type SecurityEventSeverity =
  | 'info'
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type SecurityEventStatus =
  | 'open'
  | 'processing'
  | 'processed'
  | 'failed'
  | 'suppressed'

type JsonObject = Record<string, unknown>

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

  readonly event_category?: string | null
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

  readonly raw_event?: JsonObject | null
  readonly normalized_data?: JsonObject | null
  readonly event_metadata?: JsonObject | null
}

export interface SecurityEventCreate {
  readonly source_event_id?: string | null
  readonly event_fingerprint?: string | null
  readonly correlation_id?: string | null
  readonly parent_event_id?: string | null

  readonly event_time: string
  readonly schema_version?: number

  readonly event_category?: string | null
  readonly source: string
  readonly source_type: string
  readonly event_type: string

  readonly severity?: SecurityEventSeverity
  readonly status?: SecurityEventStatus

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

  readonly raw_event?: JsonObject | null
  readonly normalized_data?: JsonObject | null
  readonly event_metadata?: JsonObject | null
}

export interface SecurityEventListResponse {
  readonly items: SecurityEvent[]
  readonly total: number
  readonly limit: number
  readonly offset: number
}

export interface SecurityEventFilters {
  readonly q?: string
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
  readonly event_metadata?: JsonObject | null
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

function isRecord(value: unknown): value is JsonObject {
  return typeof value === 'object' && value !== null
}

function getEventPath(eventId: string): string {
  return `/${encodeURIComponent(eventId)}`
}

function buildQueryString(filters: SecurityEventFilters = {}): string {
  const params = new URLSearchParams()

  const queryFilters: Record<string, unknown> = {
    q: filters.q,
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

    if (typeof value === 'string') {
      const normalizedValue = value.trim()

      if (!normalizedValue) {
        continue
      }

      params.set(key, normalizedValue)
      continue
    }

    params.set(key, String(value))
  }

  const query = params.toString()

  return query ? `?${query}` : ''
}

async function parseErrorMessage(response: Response): Promise<string> {
  const fallback = `API_ERROR_${response.status}`
  const contentType = response.headers.get('content-type') ?? ''

  if (!contentType.includes('application/json')) {
    return fallback
  }

  try {
    const body: unknown = await response.json()

    if (!isRecord(body) || body.detail === undefined) {
      return fallback
    }

    if (typeof body.detail === 'string') {
      return body.detail
    }

    return JSON.stringify(body.detail) || fallback
  } catch {
    return fallback
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  const isJson = contentType.includes('application/json')

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }

  if (!isJson) {
    throw new ApiError(
      response.status,
      'The API returned an unexpected response format.',
    )
  }

  try {
    return (await response.json()) as T
  } catch {
    throw new ApiError(response.status, 'The API returned invalid JSON.')
  }
}

async function apiFetch(
  tenantId: string | undefined,
  endpoint = '',
  options: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(options.headers)

  headers.set('Accept', 'application/json')

  if (options.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  return authenticatedFetch(`${tenantSecurityEventsEndpoint(tenantId)}${endpoint}`, {
    ...options,
    headers,
  })
}

function hasUpdateFields(updates: SecurityEventUpdate): boolean {
  return Object.values(updates).some((value) => value !== undefined)
}

export async function getSecurityEvents(
  filters: SecurityEventFilters = {},
  tenantId?: string,
): Promise<SecurityEventListResponse> {
  const response = await apiFetch(tenantId, buildQueryString(filters))

  return handleResponse<SecurityEventListResponse>(response)
}

export async function getSecurityEvent(
  eventId: string,
  tenantId?: string,
): Promise<SecurityEvent> {
  const response = await apiFetch(tenantId, getEventPath(eventId))

  return handleResponse<SecurityEvent>(response)
}

export async function createSecurityEvent(
  event: SecurityEventCreate,
  tenantId?: string,
): Promise<SecurityEvent> {
  const response = await apiFetch(tenantId, '', {
    method: 'POST',
    body: JSON.stringify(event),
  })

  return handleResponse<SecurityEvent>(response)
}

export async function updateSecurityEvent(
  eventId: string,
  updates: SecurityEventUpdate,
  tenantId?: string,
): Promise<SecurityEvent> {
  if (!hasUpdateFields(updates)) {
    throw new TypeError('At least one defined update field is required.')
  }

  const response = await apiFetch(tenantId, getEventPath(eventId), {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })

  return handleResponse<SecurityEvent>(response)
}

export async function deleteSecurityEvent(eventId: string, tenantId?: string): Promise<void> {
  const response = await apiFetch(tenantId, getEventPath(eventId), {
    method: 'DELETE',
  })

  await handleResponse<void>(response)
}
