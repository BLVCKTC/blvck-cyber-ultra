'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  alerts as allAlerts,
  severityRank,
  alertStatusLabel,
  severityLabel,
  type Severity,
  type AlertStatus,
} from '@/lib/soc/mock'
import {
  SeverityBadge,
  StatusChip,
  ConfidenceMeter,
} from '@/components/soc/primitives'

const statusTone: Record<AlertStatus, Parameters<typeof StatusChip>[0]['tone']> = {
  new: 'info',
  investigating: 'warning',
  contained: 'neutral',
  resolved: 'success',
  false_positive: 'muted',
}

const severityFilters: (Severity | 'all')[] = [
  'all',
  'critical',
  'high',
  'warning',
  'info',
]

export function AlertsTable({ tenantId }: { tenantId: string }) {
  const [severity, setSeverity] = useState<Severity | 'all'>('all')
  const [openOnly, setOpenOnly] = useState(true)
  const [query, setQuery] = useState('')

  const rows = useMemo(() => {
    return [...allAlerts]
      .filter((a) => (severity === 'all' ? true : a.severity === severity))
      .filter((a) =>
        openOnly
          ? a.status !== 'resolved' && a.status !== 'false_positive'
          : true,
      )
      .filter((a) => {
        if (!query.trim()) return true
        const q = query.toLowerCase()
        return (
          a.title.toLowerCase().includes(q) ||
          a.id.toLowerCase().includes(q) ||
          a.asset.toLowerCase().includes(q) ||
          a.entity.toLowerCase().includes(q)
        )
      })
      .sort((a, b) => severityRank[a.severity] - severityRank[b.severity])
  }, [severity, openOnly, query])

  return (
    <div className="rounded-lg border border-border bg-card">
      {/* Filter bar */}
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
              {s === 'all' ? 'All' : severityLabel[s]}
            </button>
          ))}
        </div>

        <label className="flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={openOnly}
            onChange={(e) => setOpenOnly(e.target.checked)}
            className="h-3.5 w-3.5 accent-[var(--primary)]"
          />
          Open only
        </label>

        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter by title, asset, entity…"
          className="ml-auto h-8 w-full max-w-xs rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground">
              <th className="px-4 py-2.5 font-medium">Alert</th>
              <th className="px-3 py-2.5 font-medium">Severity</th>
              <th className="hidden px-3 py-2.5 font-medium lg:table-cell">
                Status
              </th>
              <th className="hidden px-3 py-2.5 font-medium md:table-cell">
                Asset / entity
              </th>
              <th className="hidden px-3 py-2.5 font-medium xl:table-cell">
                Confidence
              </th>
              <th className="px-3 py-2.5 text-right font-medium">Detected</th>
              <th className="px-2 py-2.5" />
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr
                key={a.id}
                className="border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40"
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/dashboard/${tenantId}/alerts/${a.id}`}
                    className="block"
                  >
                    <span className="font-medium text-foreground">
                      {a.title}
                    </span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {a.id} · {a.source} · {a.tactic}
                    </span>
                  </Link>
                </td>
                <td className="px-3 py-3">
                  <SeverityBadge severity={a.severity} />
                </td>
                <td className="hidden px-3 py-3 lg:table-cell">
                  <StatusChip
                    label={alertStatusLabel[a.status]}
                    tone={statusTone[a.status]}
                  />
                </td>
                <td className="hidden px-3 py-3 md:table-cell">
                  <span className="block text-foreground">{a.asset}</span>
                  <span className="block text-xs text-muted-foreground">
                    {a.entity}
                  </span>
                </td>
                <td className="hidden px-3 py-3 xl:table-cell">
                  <ConfidenceMeter value={a.confidence} />
                </td>
                <td className="px-3 py-3 text-right text-xs text-muted-foreground">
                  {a.detectedAt}
                </td>
                <td className="px-2 py-3 text-right">
                  <Link
                    href={`/dashboard/${tenantId}/alerts/${a.id}`}
                    aria-label={`Investigate ${a.id}`}
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
                  No alerts match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
