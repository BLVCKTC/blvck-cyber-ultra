import { authenticatedFetch, tenantApiPath } from './client'

export type DetectionRuleType =
  | 'threshold'
  | 'query'
  | 'correlation'
  | 'behavioral'
  | 'sigma'

export type DetectionRuleSeverity =
  | 'info'
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type DetectionRuleStatus =
  | 'draft'
  | 'testing'
  | 'backtested'
  | 'canary'
  | 'approved'
  | 'production'
  | 'monitored'
  | 'tuned'
  | 'retired'

export type DetectionRule = {
  id: string
  tenant_id: string

  name: string
  description?: string | null

  rule_type: DetectionRuleType
  severity: DetectionRuleSeverity
  status: DetectionRuleStatus

  version: number
  enabled: boolean

  query?: string | null
  configuration: Record<string, unknown>

  tags: string[]

  mitre_technique_ids: string[]
  mitre_tactic_ids: string[]

  author?: string | null
  source?: string | null
  forked_from_id?: string | null

  created_at: string
  updated_at: string
  published_at?: string | null
  created_by_id?: string | null

  reviewed_by_id?: string | null
  reviewed_at?: string | null
  review_notes?: string | null

  approved_by_id?: string | null
  approved_at?: string | null
  approval_notes?: string | null
}

export type DetectionRuleInput = {
  name: string
  description?: string | null

  rule_type: DetectionRuleType
  severity: DetectionRuleSeverity

  version?: number
  enabled?: boolean

  query?: string | null
  configuration?: Record<string, unknown>

  tags?: string[]

  mitre_technique_ids?: string[]
  mitre_tactic_ids?: string[]

  author?: string | null
  source?: string | null

  status?: 'draft'
}

export type DetectionRuleUpdateInput = Partial<DetectionRuleInput>

export type DetectionRuleList = {
  items: DetectionRule[]
  total: number
  limit: number
  offset: number
}

export type DetectionRuleValidationWarning = {
  code: string
  message: string
  field?: string | null
}

export type DetectionRuleTransitionResult = {
  rule: DetectionRule
  warnings: DetectionRuleValidationWarning[]
}

type DetectionRuleListParams = Record<
  string,
  string | number | boolean | undefined
>

const buildRulePath = (id: string) => `/${encodeURIComponent(id)}`

const buildTransitionPath = (id: string) => `${buildRulePath(id)}/transition`

async function request<T>(
  tenantId: string,
  path = '',
  init?: RequestInit,
): Promise<T> {
  const response = await authenticatedFetch(
    `${tenantApiPath(tenantId, 'detection-rules')}${path}`,
    init,
  )

  if (!response.ok) {
    const message = await response.text()

    throw new Error(message || `Request failed (${response.status})`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

function jsonRequest(body: unknown): RequestInit {
  return {
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json',
    },
  }
}

export function getDetectionRules(
  tenantId: string,
  params: DetectionRuleListParams = {},
): Promise<DetectionRuleList> {
  const query = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      query.set(key, String(value))
    }
  }

  const queryString = query.toString()

  return request<DetectionRuleList>(
    tenantId,
    queryString ? `?${queryString}` : '',
  )
}

export function getDetectionRule(
  tenantId: string,
  id: string,
): Promise<DetectionRule> {
  return request<DetectionRule>(tenantId, buildRulePath(id))
}

export function createDetectionRule(
  tenantId: string,
  input: DetectionRuleInput,
): Promise<DetectionRule> {
  return request<DetectionRule>(tenantId, '', {
    method: 'POST',
    ...jsonRequest(input),
  })
}

export function updateDetectionRule(
  tenantId: string,
  id: string,
  input: DetectionRuleUpdateInput,
): Promise<DetectionRule> {
  return request<DetectionRule>(tenantId, buildRulePath(id), {
    method: 'PATCH',
    ...jsonRequest(input),
  })
}

export function deleteDetectionRule(
  tenantId: string,
  id: string,
): Promise<void> {
  return request<void>(tenantId, buildRulePath(id), {
    method: 'DELETE',
  })
}

export function transitionDetectionRule(
  tenantId: string,
  id: string,
  target_status: DetectionRuleStatus,
): Promise<DetectionRuleTransitionResult> {
  return request<DetectionRuleTransitionResult>(
    tenantId,
    buildTransitionPath(id),
    {
      method: 'POST',
      ...jsonRequest({
        target_status,
      }),
    },
  )
}

export function getProductionDetectionRules(
  tenantId: string,
): Promise<DetectionRule[]> {
  return request<DetectionRule[]>(tenantId, '/production')
}
