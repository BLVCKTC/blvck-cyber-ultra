export type SecurityEventSeverity = 'low' | 'medium' | 'high' | 'critical'

export interface SecurityEvent {
  readonly id: string
  readonly tenant_id: string
  readonly timestamp: string
  readonly source: string
  readonly source_type: string
  readonly event_type: string
  readonly severity: SecurityEventSeverity
  readonly hostname: string | null
  readonly source_ip: string | null
  readonly destination_ip: string | null
  readonly user_identifier: string | null
  readonly message: string | null
  readonly raw_event: Record<string, unknown>
  readonly normalized_data: Record<string, unknown>
  readonly created_at: string
  readonly status?: string
}

export interface SecurityEventListResponse {
  items: SecurityEvent[]
  total: number
  limit: number
  offset: number
}

export interface SecurityEventFilters {
  q?: string
  severity?: SecurityEventSeverity
  event_type?: string
  source?: string
  hostname?: string
  limit?: number
  offset?: number
}

export interface SecurityEventUpdate {
  status?: string
  severity?: SecurityEventSeverity
  message?: string
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return {} as T
    }

    return response.json()
  }

  switch (response.status) {
    case 401:
      throw new ApiError(401, 'not_authenticated')

    case 403:
      throw new ApiError(403, 'forbidden')

    case 404:
      throw new ApiError(404, 'not_found')

    default:
      throw new ApiError(response.status, `API_ERROR_${response.status}`)
  }
}

async function apiFetch(endpoint: string, options: RequestInit = {}) {
  return fetch(`/api/security-events${endpoint}`, {
    credentials: 'include',
    cache: 'no-store',
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
}

function buildQueryString(filters: SecurityEventFilters = {}): string {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      params.set(key, String(value))
    }
  })

  const query = params.toString()

  return query ? `?${query}` : ''
}

export async function getSecurityEvents(
  filters: SecurityEventFilters = {},
): Promise<SecurityEventListResponse> {
  const query = buildQueryString(filters)

  const response = await apiFetch(query, {
    method: 'GET',
  })

  return handleResponse<SecurityEventListResponse>(response)
}

export async function getSecurityEvent(
  eventId: string,
): Promise<SecurityEvent> {
  const response = await apiFetch(`/${encodeURIComponent(eventId)}`, {
    method: 'GET',
  })

  return handleResponse<SecurityEvent>(response)
}

export async function updateSecurityEvent(
  eventId: string,
  updates: SecurityEventUpdate,
): Promise<SecurityEvent> {
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

  return handleResponse<void>(response)
}
