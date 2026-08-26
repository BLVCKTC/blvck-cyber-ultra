import { API_URL, authenticatedFetch } from './client'

export type AlertSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical'
export type AlertStatus = 'new' | 'open' | 'acknowledged' | 'investigating' | 'resolved' | 'suppressed' | 'false_positive'
export interface Alert { id: string; tenant_id: string; fingerprint: string; title: string; description?: string | null; severity: AlertSeverity; status: AlertStatus; detection_rule_id?: string | null; security_event_id?: string | null; confidence?: number | null; risk_score?: number | null; source?: string | null; first_seen_at: string; last_seen_at: string; created_at: string; updated_at: string; metadata_json: Record<string, unknown> }
export interface AlertList { items: Alert[]; total: number; limit: number; offset: number }
const path = '/alerts'
async function request<T>(url: string, init?: RequestInit): Promise<T> { const response = await authenticatedFetch(`${API_URL}${url}`, { headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) }, ...init }); if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`); return response.status === 204 ? (undefined as T) : response.json() }
export function getAlerts(params: Record<string, string | number | boolean | undefined> = {}) { const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined).map(([key, value]) => [key, String(value)])); return request<AlertList>(`${path}?${query}`) }
export function getAlert(id: string) { return request<Alert>(`${path}/${id}`) }
export function createAlert(payload: Omit<Alert, 'id' | 'tenant_id' | 'first_seen_at' | 'last_seen_at' | 'created_at' | 'updated_at'>) { return request<Alert>(path, { method: 'POST', body: JSON.stringify(payload) }) }
export function updateAlert(id: string, payload: Partial<Pick<Alert, 'title' | 'description' | 'severity' | 'status' | 'confidence' | 'risk_score' | 'metadata_json'>>) { return request<Alert>(`${path}/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }) }
export function deleteAlert(id: string) { return request<void>(`${path}/${id}`, { method: 'DELETE' }) }
