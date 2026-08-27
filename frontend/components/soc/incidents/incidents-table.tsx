'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import useSWR from 'swr'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getIncidents, incidentsKey, type Incident, type IncidentSeverity, type IncidentStatus } from '@/lib/api/incidents'
import { SeverityBadge, StatusChip } from '@/components/soc/primitives'

const severityLabel: Record<string, string> = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' }
const severityRank: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }
const statusLabel: Record<string, string> = { open: 'Open', investigating: 'Investigating', contained: 'Contained', resolved: 'Resolved' }
const statusTone: Record<string, Parameters<typeof StatusChip>[0]['tone']> = { open: 'critical', investigating: 'warning', contained: 'info', resolved: 'success' }
const severityFilters = ['all', 'critical', 'high', 'medium', 'low']
const statusFilters = ['all', 'open', 'investigating', 'contained', 'resolved']

export function IncidentsTable({ tenantId, initialSeverity = 'all' }: { tenantId: string; initialSeverity?: IncidentSeverity | 'all' }) {
  const { data, error, isLoading } = useSWR<Incident[]>(`${incidentsKey}:${tenantId}`, getIncidents)
  const [severity, setSeverity] = useState<string>(initialSeverity)
  const [status, setStatus] = useState<string>('all')
  const [query, setQuery] = useState('')
  const rows = useMemo(() => (data ?? []).filter((i) => severity === 'all' || i.severity === severity).filter((i) => status === 'all' || i.status === status).filter((i) => !query.trim() || `${i.title} ${i.id} ${i.summary ?? ''}`.toLowerCase().includes(query.toLowerCase())).sort((a, b) => (severityRank[a.severity] ?? 9) - (severityRank[b.severity] ?? 9)), [data, severity, status, query])

  return <div className="rounded-lg border border-border bg-card">
    <div className="flex flex-wrap items-center gap-3 border-b border-border p-3">
      <div className="flex items-center gap-1 rounded-md border border-border bg-background p-0.5">{severityFilters.map((s) => <button key={s} onClick={() => setSeverity(s)} className={cn('rounded px-2.5 py-1 text-xs font-medium capitalize transition-colors', severity === s ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground')}>{s === 'all' ? 'All severities' : severityLabel[s]}</button>)}</div>
      <select value={status} onChange={(e) => setStatus(e.target.value)} className="h-8 rounded-md border border-border bg-background px-2 text-xs text-foreground"><option value="all">All statuses</option>{statusFilters.slice(1).map((s) => <option key={s} value={s}>{statusLabel[s]}</option>)}</select>
      <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter by title or summary" className="ml-auto h-8 w-full max-w-xs rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground" />
    </div>
    <div className="overflow-x-auto"><table className="w-full border-collapse text-left text-sm"><thead><tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground"><th className="px-4 py-2.5 font-medium">Incident</th><th className="px-3 py-2.5 font-medium">Severity</th><th className="px-3 py-2.5 font-medium">Status</th><th className="px-3 py-2.5 text-right font-medium">Updated</th><th /></tr></thead><tbody>
      {isLoading && <tr><td colSpan={5} className="px-4 py-12 text-center text-muted-foreground">Loading incidents…</td></tr>}
      {error && <tr><td colSpan={5} className="px-4 py-12 text-center text-destructive">Unable to load incidents.</td></tr>}
      {!isLoading && !error && rows.map((i) => <tr key={i.id} className="border-b border-border/60 last:border-0 hover:bg-accent/40"><td className="px-4 py-3"><Link href={`/dashboard/${tenantId}/incidents/${i.id}`} className="block"><span className="font-medium text-foreground">{i.title}</span><span className="mt-0.5 block text-xs text-muted-foreground">{i.id}{i.summary ? ` · ${i.summary}` : ''}</span></Link></td><td className="px-3 py-3"><SeverityBadge severity={i.severity as any} /></td><td className="px-3 py-3"><StatusChip label={statusLabel[i.status] ?? i.status} tone={statusTone[i.status] ?? 'info'} /></td><td className="px-3 py-3 text-right text-xs text-muted-foreground">{new Date(i.updated_at).toLocaleString()}</td><td className="px-2 py-3 text-right"><Link href={`/dashboard/${tenantId}/incidents/${i.id}`} aria-label={`Open ${i.id}`}><ChevronRight className="h-4 w-4 text-muted-foreground" /></Link></td></tr>)}
      {!isLoading && !error && rows.length === 0 && <tr><td colSpan={5} className="px-4 py-12 text-center text-sm text-muted-foreground">No incidents match the current filters.</td></tr>}
    </tbody></table></div>
  </div>
}
