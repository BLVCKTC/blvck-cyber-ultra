'use client'

import { useMemo, useState } from 'react'
import useSWR from 'swr'
import Link from 'next/link'
import { ChevronRight, RefreshCw, Search } from 'lucide-react'
import { InvestigationDrawer } from '@/components/soc/investigation-drawer'
import { SeverityBadge, StatusChip } from '@/components/soc/primitives'
import { getAlerts, type Alert, type AlertSeverity, type AlertStatus } from '@/lib/api/alerts'

const severities: Array<AlertSeverity | 'all'> = ['all', 'critical', 'high', 'medium', 'low', 'info']
const statuses: Array<AlertStatus | 'all'> = ['all', 'new', 'open', 'acknowledged', 'investigating', 'resolved', 'suppressed', 'false_positive']
const statusTone: Record<AlertStatus, Parameters<typeof StatusChip>[0]['tone']> = {
  new: 'info', open: 'warning', acknowledged: 'warning', investigating: 'warning', resolved: 'success', suppressed: 'muted', false_positive: 'muted',
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

export function AlertsTable({ tenantId }: { tenantId: string }) {
  const [query, setQuery] = useState('')
  const [severity, setSeverity] = useState<AlertSeverity | 'all'>('all')
  const [status, setStatus] = useState<AlertStatus | 'all'>('all')
  const [offset, setOffset] = useState(0)
  const limit = 20
  const params = useMemo(() => ({ q: query || undefined, severity: severity === 'all' ? undefined : severity, status: status === 'all' ? undefined : status, limit, offset }), [query, severity, status, offset])
  const { data, error, isLoading, mutate } = useSWR(['alerts', params], () => getAlerts(params))

  function updateFilter(setter: (value: never) => void, value: string) {
    setter(value === 'all' ? 'all' as never : value as never)
    setOffset(0)
  }

  return (
    <section className="rounded-lg border border-border bg-card">
      <div className="flex flex-wrap items-center gap-3 border-b border-border p-3">
        <div className="relative min-w-56 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input aria-label="Search alerts" value={query} onChange={(event) => { setQuery(event.target.value); setOffset(0) }} placeholder="Search alerts" className="h-9 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none focus:border-primary" />
        </div>
        <select aria-label="Filter by severity" value={severity} onChange={(event) => updateFilter(setSeverity as (value: never) => void, event.target.value)} className="h-9 rounded-md border border-border bg-background px-3 text-sm capitalize text-foreground">
          {severities.map((value) => <option key={value} value={value}>{value === 'all' ? 'All severities' : value}</option>)}
        </select>
        <select aria-label="Filter by status" value={status} onChange={(event) => updateFilter(setStatus as (value: never) => void, event.target.value)} className="h-9 rounded-md border border-border bg-background px-3 text-sm capitalize text-foreground">
          {statuses.map((value) => <option key={value} value={value}>{value === 'all' ? 'All statuses' : value.replace('_', ' ')}</option>)}
        </select>
        <button type="button" onClick={() => mutate()} aria-label="Refresh alerts" className="inline-flex size-9 items-center justify-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-foreground"><RefreshCw /></button>
      </div>
      {error && <div className="flex items-center justify-between gap-3 border-b border-border p-4 text-sm text-destructive" role="alert"><span>Unable to load alerts: {error.message}</span><button type="button" onClick={() => mutate()} className="font-medium underline">Retry</button></div>}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead><tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground"><th className="px-4 py-3 font-medium">Alert</th><th className="px-3 py-3 font-medium">Severity</th><th className="px-3 py-3 font-medium">Status</th><th className="hidden px-3 py-3 font-medium lg:table-cell">Source</th><th className="hidden px-3 py-3 font-medium md:table-cell">Last seen</th><th className="px-2 py-3" /></tr></thead>
          <tbody>
            {isLoading && Array.from({ length: 5 }).map((_, index) => <tr key={index} className="border-b border-border/60"><td colSpan={6} className="px-4 py-5"><div className="h-4 w-2/3 animate-pulse rounded bg-muted" /></td></tr>)}
            {!isLoading && data?.items.map((alert: Alert) => <tr key={alert.id} className="border-b border-border/60 last:border-0 hover:bg-accent/40">
              <td className="px-4 py-3"><Link href={`/dashboard/${tenantId}/alerts/${alert.id}`} className="block"><span className="font-medium text-foreground">{alert.title}</span><span className="mt-1 block max-w-md truncate text-xs text-muted-foreground">{alert.description || alert.id}</span></Link></td>
              <td className="px-3 py-3"><SeverityBadge severity={alert.severity} /></td>
              <td className="px-3 py-3"><StatusChip label={alert.status.replace('_', ' ')} tone={statusTone[alert.status]} /></td>
              <td className="hidden px-3 py-3 text-muted-foreground lg:table-cell">{alert.source || '—'}</td>
              <td className="hidden px-3 py-3 text-xs text-muted-foreground md:table-cell">{formatDate(alert.last_seen_at)}</td>
              <td className="px-2 py-3 text-right"><div className="flex items-center justify-end gap-2"><InvestigationDrawer title={alert.title} alertId={alert.id} /><Link href={`/dashboard/${tenantId}/alerts/${alert.id}`} aria-label={`Open ${alert.title}`} className="text-muted-foreground hover:text-foreground"><ChevronRight /></Link></div></td>
            </tr>)}
            {!isLoading && !error && data?.items.length === 0 && <tr><td colSpan={6} className="px-4 py-14 text-center text-sm text-muted-foreground">No alerts match the current filters.</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between border-t border-border px-4 py-3 text-xs text-muted-foreground"><span>{data ? `${data.total} total alerts` : 'Loading alerts'}</span><div className="flex items-center gap-2"><button type="button" disabled={offset === 0 || isLoading} onClick={() => setOffset(Math.max(0, offset - limit))} className="rounded border border-border px-3 py-1.5 disabled:opacity-50">Previous</button><button type="button" disabled={!data || offset + limit >= data.total || isLoading} onClick={() => setOffset(offset + limit)} className="rounded border border-border px-3 py-1.5 disabled:opacity-50">Next</button></div></div>
    </section>
  )
}

export function AlertKpis({ data }: { data?: { items: Alert[]; total: number } }) {
  const open = data?.items.filter((alert) => !['resolved', 'suppressed', 'false_positive'].includes(alert.status)).length ?? 0
  const critical = data?.items.filter((alert) => alert.severity === 'critical').length ?? 0
  return <div className="flex gap-6 text-xs text-muted-foreground"><span><strong className="text-foreground">{data?.total ?? '—'}</strong> total</span><span><strong className="text-foreground">{open}</strong> open</span><span><strong className="text-foreground">{critical}</strong> critical</span></div>
}

void AlertKpis
