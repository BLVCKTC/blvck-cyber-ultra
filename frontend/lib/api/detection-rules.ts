import { authenticatedFetch, tenantApiPath } from './client'

export type DetectionRuleType = 'threshold' | 'query' | 'correlation' | 'behavioral' | 'sigma'
export type DetectionRuleSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical'
export type DetectionRuleStatus = 'draft' | 'testing' | 'backtested' | 'canary' | 'approved' | 'production' | 'monitored' | 'tuned' | 'retired'
export type DetectionRule = { id: string; tenant_id: string; name: string; description?: string | null; rule_type: DetectionRuleType; severity: DetectionRuleSeverity; status: DetectionRuleStatus; version: number; enabled: boolean; query?: string | null; configuration: Record<string, unknown>; tags: string[]; mitre_technique_ids: string[]; mitre_tactic_ids: string[]; author?: string | null; source?: string | null; created_at: string; updated_at: string; published_at?: string | null }
export type DetectionRuleList = { items: DetectionRule[]; total: number; limit: number; offset: number }
export type DetectionRuleInput = Omit<DetectionRule, 'id' | 'tenant_id' | 'created_at' | 'updated_at' | 'published_at' | 'status'> & { status?: 'draft' }
const endpoint = tenantApiPath('detection-rules')
async function request<T>(path = '', init?: RequestInit): Promise<T> { const response = await authenticatedFetch(`${tenantApiPath('detection-rules')}${path}`, init); if (!response.ok) throw new Error(await response.text() || `Request failed (${response.status})`); return response.status === 204 ? undefined as T : response.json() }
export function getDetectionRules(params: Record<string, string | number | boolean | undefined> = {}) { const query = new URLSearchParams(); Object.entries(params).forEach(([k,v]) => v !== undefined && query.set(k, String(v))); return request<DetectionRuleList>(query.size ? `?${query}` : '') }
export const getDetectionRule = (id: string) => request<DetectionRule>(`/${encodeURIComponent(id)}`)
export const createDetectionRule = (input: DetectionRuleInput) => request<DetectionRule>('', { method: 'POST', body: JSON.stringify(input), headers: { 'Content-Type': 'application/json' } })
export const updateDetectionRule = (id: string, input: Partial<DetectionRuleInput>) => request<DetectionRule>(`/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(input), headers: { 'Content-Type': 'application/json' } })
export const deleteDetectionRule = (id: string) => request<void>(`/${encodeURIComponent(id)}`, { method: 'DELETE' })
export const transitionDetectionRule = (id: string, target_status: DetectionRuleStatus) => request<DetectionRule>(`/${encodeURIComponent(id)}/transition`, { method: 'POST', body: JSON.stringify({ target_status }), headers: { 'Content-Type': 'application/json' } })
export const getProductionDetectionRules = () => request<DetectionRule[]>(`/production`)
