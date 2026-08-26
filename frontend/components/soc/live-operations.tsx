'use client'

import useSWR from 'swr'
import { Activity, AlertTriangle, Crosshair, ShieldCheck } from 'lucide-react'
import { useTenant } from '@/components/providers/tenant-provider'
import { getAlerts } from '@/lib/api/alerts'

export function LiveOperations() {
  const { tenantId } = useTenant()
  const { data, error, isLoading } = useSWR(['command-center-alerts', tenantId], () => getAlerts({ limit: 100, offset: 0 }))
  const alerts = data?.items ?? []
  const open = alerts.filter((alert) => !['resolved', 'suppressed', 'false_positive'].includes(alert.status)).length
  const critical = alerts.filter((alert) => alert.severity === 'critical').length

  const metrics = [
    { label: 'Alert queue', value: data?.total, icon: AlertTriangle, detail: `${open} open` },
    { label: 'Critical alerts', value: critical, icon: ShieldCheck, detail: 'Current tenant' },
    { label: 'Production rules', value: '—', icon: Crosshair, detail: 'Registry view' },
    { label: 'Event stream', value: '—', icon: Activity, detail: 'Ingestion view' },
  ]

  return (
    <section aria-labelledby="live-operations-heading" className="glass p-4">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div><p id="live-operations-heading" className="text-xs font-mono uppercase tracking-widest text-cyber">Live operations</p><p className="mt-1 text-xs text-muted-foreground">Authenticated tenant telemetry</p></div>
        {error ? <span className="text-xs text-destructive">Unavailable</span> : <span className="flex items-center gap-2 text-xs text-success"><span className="size-1.5 rounded-full bg-success" />API connected</span>}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map(({ label, value, icon: Icon, detail }) => <div key={label} className="rounded-md border border-border bg-background/40 p-3"><div className="flex items-center justify-between"><span className="text-xs text-muted-foreground">{label}</span><Icon className="size-4 text-primary" /></div><p className="mt-2 text-2xl font-semibold tabular-nums">{isLoading ? '—' : value ?? '0'}</p><p className="mt-1 text-[11px] text-muted-foreground">{detail}</p></div>)}
      </div>
    </section>
  )
}
