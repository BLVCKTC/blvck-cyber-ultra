import { authenticatedFetch, tenantApiPath } from './client'

export type InvestigationStatus =
  | 'open'
  | 'investigating'
  | 'resolved'
  | 'closed'

export interface Investigation {
  id: string
  tenant_id: string
  alert_id?: string | null
  title: string
  summary?: string | null
  status: InvestigationStatus
  assignee_id?: string | null
  created_at: string
  updated_at: string
  metadata_json: Record<string, unknown>
}

export interface Evidence {
  id: string
  tenant_id: string
  investigation_id: string
  evidence_type: string
  title: string
  reference?: string | null
  notes?: string | null
  metadata_json: Record<string, unknown>
  created_at: string
}

export type CreateInvestigationPayload = Pick<
  Investigation,
  | 'tenant_id'
  | 'title'
  | 'summary'
  | 'alert_id'
  | 'status'
  | 'assignee_id'
  | 'metadata_json'
>

async function request<T>(
  tenantId: string,
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await authenticatedFetch(tenantApiPath(tenantId, path), {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    throw new Error(
      (await response.json().catch(() => null))?.detail ??
        `Request failed (${response.status})`,
    )
  }

  return response.json()
}

export const getInvestigation = (tenantId: string, id: string) =>
  request<Investigation>(tenantId, `/investigations/${encodeURIComponent(id)}`)

export const createInvestigation = (
  tenantId: string,
  payload: Pick<
    Investigation,
    | 'title'
    | 'summary'
    | 'alert_id'
    | 'status'
    | 'assignee_id'
    | 'metadata_json'
  >,
) =>
  request<Investigation>(tenantId, '/investigations', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const updateInvestigation = (
  tenantId: string,
  id: string,
  payload: Partial<
    Pick<
      Investigation,
      'title' | 'summary' | 'status' | 'assignee_id' | 'metadata_json'
    >
  >,
) =>
  request<Investigation>(
    tenantId,
    `/investigations/${encodeURIComponent(id)}`,
    {
      method: 'PATCH',
      body: JSON.stringify(payload),
    },
  )

export const getInvestigationEvidence = (tenantId: string, id: string) =>
  request<Evidence[]>(
    tenantId,
    `/investigations/${encodeURIComponent(id)}/evidence`,
  )

export const addInvestigationEvidence = (
  tenantId: string,
  id: string,
  payload: Omit<
    Evidence,
    'id' | 'tenant_id' | 'investigation_id' | 'created_at'
  >,
) =>
  request<Evidence>(
    tenantId,
    `/investigations/${encodeURIComponent(id)}/evidence`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )
