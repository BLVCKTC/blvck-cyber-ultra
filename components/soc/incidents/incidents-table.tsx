'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  incidents as allIncidents,
  severityRank,
  severityLabel,
  incidentStatusLabel,
  type Severity,
  type IncidentStatus,
} from '@/lib/soc/mock'
import { SeverityBadge, StatusChip } from '@/components/soc/primitives'

const statusTone: Record<
  IncidentStatus,
  Parameters<typeof StatusChip>[0]['tone']
> = {
  open: 'critical',
  investigating: 'warning',
  contained: 'info',
  resolved: 'success',
}

const severityFilters: (Severity | 'all')[] = [
  'all',
  'critical',
  'high',
  'warning',
  'info',
]

const statusFilters: (IncidentStatus | 'all')[] = [
  'all',
  'open',
  'investigating',
  'contained',
  'resolved',
]

export function IncidentsTable({
  tenantId,
  initialSeverity = 'all',
}: {
  tenantId: string
  initialSeverity?: Severity | 'all'
}) {
  const [severity, setSeverity] = useState<Severity | 'all'>(initialSeverity)
  const [status, setStatus] = useState<IncidentStatus | 'all'>('all')
  const [query, setQuery] = useState('')

  const rows = useMemo(() => {
    return [...allIncidents]
      .filter((i) => (severity === 'all' ? true : i.severity === severity))
      .filter((i) => (status === 'all' ? true : i.status === status))
      .filter((i) => {
        if (!query.trim()) return true
        const q = query.toLowerCase()
        return (
          i.title.toLowerCase().includes(q) ||
          i.id.toLowerCase().includes(q) ||
          i.owner.toLowerCase().includes(q) ||
          i.assets.some((a) => a.toLowerCase().includes(q))
        )
      })
      .sort(
        (a, b) =>
          severityRank[a.severity] - severityRank[b.severity] ||
          a.priority.localeCompare(b.priority),
      )
  }, [severity, status, query])

  return (
    <div className="rounded-lg border border-border bg-card">
      <div className="flex flex-wrap items-center gap-3 border-b border-border p-3">
        <div className="flex items-center gap-1 rounded-md border border-border bg-background p-0.5">
          {severityFilters.map((s) => (
            <button
              key={s}
              onClick={() => setSeverity(s)}
              className={cn(
                'rounded px-2.5 py-1 text-xs font-medium capitalize transition-colors',
                severity === s
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {s === 'all' ? 'All severities' : severityLabel[s]}
            </button>
          ))}
        </div>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as IncidentStatus | 'all')}
          className="h-8 rounded-md border border-border bg-background px-2 text-xs text-foreground focus:border-primary/60 focus:outline-none"
        >
          {statusFilters.map((s) => (
            <option key={s} value={s}>
              {s === 'all' ? 'All statuses' : incidentStatusLabel[s]}
            </option>
          ))}
        </select>

        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter by title, owner, asset…"
          className="ml-auto h-8 w-full max-w-xs rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground">
              <th className="px-4 py-2.5 font-medium">Incident</th>
              <th className="px-3 py-2.5 font-medium">Severity</th>
              <th className="hidden px-3 py-2.5 font-medium lg:table-cell">
                Status
              </th>
              <th className="hidden px-3 py-2.5 font-medium md:table-cell">
                Owner
              </th>
              <th className="hidden px-3 py-2.5 text-center font-medium sm:table-cell">
                Alerts
              </th>
              <th className="px-3 py-2.5 text-right font-medium">Updated</th>
              <th className="px-2 py-2.5" />
            </tr>
          </thead>
          <tbody>
            {rows.map((i) => (
              <tr
                key={i.id}
                className="border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40"
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/dashboard/${tenantId}/incidents/${i.id}`}
                    className="block"
                  >
                    <span className="flex items-center gap-2">
                      <span className="rounded bg-muted px-1.5 py-0.5 text-[11px] font-semibold text-foreground">
                        {i.priority}
                      </span>
                      <span className="font-medium text-foreground">
                        {i.title}
                      </span>
                    </span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {i.id} · {i.tactics.join(' → ')}
                    </span>
                  </Link>
                </td>
                <td className="px-3 py-3">
                  <SeverityBadge severity={i.severity} />
                </td>
                <td className="hidden px-3 py-3 lg:table-cell">
                  <StatusChip
                    label={incidentStatusLabel[i.status]}
                    tone={statusTone[i.status]}
                  />
                </td>
                <td className="hidden px-3 py-3 text-foreground md:table-cell">
                  {i.owner}
                </td>
                <td className="hidden px-3 py-3 text-center tabular text-muted-foreground sm:table-cell">
                  {i.alertCount}
                </td>
                <td className="px-3 py-3 text-right text-xs text-muted-foreground">
                  {i.updatedAt}
                </td>
                <td className="px-2 py-3 text-right">
                  <Link
                    href={`/dashboard/${tenantId}/incidents/${i.id}`}
                    aria-label={`Open ${i.id}`}
                    className="inline-flex text-muted-foreground hover:text-foreground"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="px-4 py-12 text-center text-sm text-muted-foreground"
                >
                  No incidents match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
