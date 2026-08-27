'use client'

import { useMemo, useState } from 'react'
import useSWR from 'swr'
import { Globe, ShieldAlert, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  vulnStatusLabel,
  severityRank,
  severityLabel,
  type Severity,
  type VulnStatus,
  type Vulnerability,
} from '@/lib/soc/mock'
import { getVulnerabilities, vulnerabilitiesKey, type ApiVulnerability } from '@/lib/api/vulnerabilities'
import { SeverityBadge, StatusChip } from '@/components/soc/primitives'

const severityAccent: Record<Severity, string> = {
  critical: 'text-critical',
  high: 'text-high',
  warning: 'text-warning',
  info: 'text-info',
}

const statusTone: Record<VulnStatus, Parameters<typeof StatusChip>[0]['tone']> =
  {
    open: 'critical',
    in_progress: 'warning',
    remediated: 'success',
    accepted: 'muted',
  }

const severityOrder: Severity[] = ['critical', 'high', 'warning', 'info']

function normalizeVulnerability(v: ApiVulnerability): Vulnerability {
  const metadata = v.metadata_json ?? {}
  return {
    id: v.id,
    cve: v.cve,
    title: v.title,
    severity: (['critical', 'high', 'warning', 'info'].includes(v.severity) ? v.severity : 'info') as Severity,
    cvss: Number(v.cvss_score ?? metadata.cvss ?? 0),
    epss: Number(metadata.epss ?? 0),
    status: (['open', 'in_progress', 'remediated', 'accepted'].includes(String(metadata.status)) ? metadata.status : 'open') as VulnStatus,
    asset: String(metadata.asset ?? 'Unassigned'),
    assetGroup: String(metadata.assetGroup ?? 'Unclassified'),
    exploitAvailable: Boolean(metadata.exploitAvailable),
    exposedToInternet: Boolean(metadata.exposedToInternet),
    discovered: v.created_at,
    due: String(metadata.due ?? 'Unscheduled'),
    fix: String(metadata.fix ?? 'Review remediation guidance'),
  }
}

export function VulnerabilitiesView() {
  const { data, error, isLoading } = useSWR(vulnerabilitiesKey, getVulnerabilities)
  const allVulns = useMemo(() => (data ?? []).map(normalizeVulnerability), [data])
  const [severity, setSeverity] = useState<Severity | 'all'>('all')
  const [openOnly, setOpenOnly] = useState(true)
  const [query, setQuery] = useState('')

  const counts = useMemo(() => {
    const c: Record<Severity, number> = {
      critical: 0,
      high: 0,
      warning: 0,
      info: 0,
    }
    for (const v of allVulns) c[v.severity] += 1
    return c
  }, [])

  // Remediation priority: exploitable + internet-exposed + high EPSS first.
  const topPriority = useMemo(() => {
    return [...allVulns]
      .filter((v) => v.status === 'open' || v.status === 'in_progress')
      .sort(
        (a, b) =>
          Number(b.exploitAvailable) - Number(a.exploitAvailable) ||
          Number(b.exposedToInternet) - Number(a.exposedToInternet) ||
          b.epss - a.epss ||
          b.cvss - a.cvss,
      )
      .slice(0, 3)
  }, [])

  const rows = useMemo(() => {
    return [...allVulns]
      .filter((v) => (severity === 'all' ? true : v.severity === severity))
      .filter((v) =>
        openOnly ? v.status === 'open' || v.status === 'in_progress' : true,
      )
      .filter((v) => {
        if (!query.trim()) return true
        const q = query.toLowerCase()
        return (
          v.title.toLowerCase().includes(q) ||
          v.cve.toLowerCase().includes(q) ||
          v.asset.toLowerCase().includes(q) ||
          v.assetGroup.toLowerCase().includes(q)
        )
      })
      .sort(
        (a, b) =>
          severityRank[a.severity] - severityRank[b.severity] || b.epss - a.epss,
      )
  }, [severity, openOnly, query])

  if (isLoading) return <p className="py-10 text-center text-sm text-muted-foreground">Loading tenant vulnerabilities…</p>
  if (error) return <p className="py-10 text-center text-sm text-destructive">Vulnerability inventory is unavailable.</p>

  return (
    <div className="space-y-6">
      {/* Severity summary — clickable filters */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {severityOrder.map((s) => {
          const active = severity === s
          return (
            <button
              key={s}
              onClick={() => setSeverity(active ? 'all' : s)}
              className={cn(
                'rounded-lg border bg-card p-4 text-left transition-colors',
                active
                  ? 'border-primary/60'
                  : 'border-border hover:border-primary/30',
              )}
            >
              <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                {severityLabel[s]}
              </span>
              <p
                className={cn(
                  'mt-1 text-3xl font-semibold tabular tracking-tight',
                  severityAccent[s],
                )}
              >
                {counts[s]}
              </p>
            </button>
          )
        })}
      </div>

      {/* Remediation prioritization */}
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-intel" />
          <h2 className="text-sm font-semibold text-foreground">
            Remediation prioritization
          </h2>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Resolve these {topPriority.length} vulnerabilities first to reduce
          organizational risk by approximately 12%. Ranked by active exploit,
          internet exposure, and exploit-prediction score.
        </p>
        <ol className="mt-4 space-y-2">
          {topPriority.map((v, i) => (
            <li
              key={v.id}
              className="flex flex-wrap items-center gap-3 rounded-md border border-border bg-background p-3"
            >
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-semibold text-foreground">
                {i + 1}
              </span>
              <SeverityBadge severity={v.severity} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">
                  {v.title}
                </p>
                <p className="font-mono text-[11px] text-muted-foreground">
                  {v.cve} · {v.asset}
                </p>
              </div>
              {v.exploitAvailable && (
                <span className="inline-flex items-center gap-1 rounded bg-critical/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-critical">
                  <ShieldAlert className="h-3 w-3" /> Exploit
                </span>
              )}
              {v.exposedToInternet && (
                <span className="inline-flex items-center gap-1 rounded bg-high/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-high">
                  <Globe className="h-3 w-3" /> Exposed
                </span>
              )}
              <span className="font-mono text-xs text-muted-foreground">
                Fix: {v.fix}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-border bg-card">
        <div className="flex flex-wrap items-center gap-3 border-b border-border p-3">
          <div className="flex items-center gap-1 rounded-md border border-border bg-background p-0.5">
            {(['all', ...severityOrder] as (Severity | 'all')[]).map((s) => (
              <button
                key={s}
                onClick={() => setSeverity(s)}
                className={cn(
                  'rounded px-2.5 py-1 text-xs font-medium transition-colors',
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
            Unresolved only
          </label>

          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by CVE, asset, title…"
            className="ml-auto h-8 w-full max-w-xs rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-border text-[11px] uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-2.5 font-medium">Vulnerability</th>
                <th className="px-3 py-2.5 font-medium">Severity</th>
                <th className="hidden px-3 py-2.5 text-right font-medium sm:table-cell">
                  CVSS
                </th>
                <th className="hidden px-3 py-2.5 text-right font-medium lg:table-cell">
                  Exploitability
                </th>
                <th className="hidden px-3 py-2.5 font-medium md:table-cell">
                  Asset
                </th>
                <th className="hidden px-3 py-2.5 font-medium lg:table-cell">
                  Status
                </th>
                <th className="px-3 py-2.5 text-right font-medium">Due</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((v) => (
                <tr
                  key={v.id}
                  className="border-b border-border/60 transition-colors last:border-0 hover:bg-accent/40"
                >
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2">
                      <span className="font-medium text-foreground">
                        {v.title}
                      </span>
                      {v.exploitAvailable && (
                        <span className="inline-flex shrink-0 items-center gap-1 rounded bg-critical/10 px-1.5 py-0.5 text-[9px] font-semibold uppercase text-critical">
                          <ShieldAlert className="h-3 w-3" /> Exploit
                        </span>
                      )}
                    </span>
                    <span className="mt-0.5 block font-mono text-xs text-muted-foreground">
                      {v.cve} · {v.assetGroup}
                    </span>
                  </td>
                  <td className="px-3 py-3">
                    <SeverityBadge severity={v.severity} />
                  </td>
                  <td className="hidden px-3 py-3 text-right sm:table-cell">
                    <span
                      className={cn(
                        'font-mono text-sm font-bold',
                        severityAccent[v.severity],
                      )}
                    >
                      {v.cvss.toFixed(1)}
                    </span>
                  </td>
                  <td className="hidden px-3 py-3 lg:table-cell">
                    <div className="flex items-center justify-end gap-2">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                        <div
                          className={cn(
                            'h-full rounded-full',
                            v.epss >= 0.7
                              ? 'bg-critical'
                              : v.epss >= 0.4
                                ? 'bg-high'
                                : 'bg-warning',
                          )}
                          style={{ width: `${Math.round(v.epss * 100)}%` }}
                        />
                      </div>
                      <span className="w-9 text-right font-mono text-xs tabular text-muted-foreground">
                        {Math.round(v.epss * 100)}%
                      </span>
                    </div>
                  </td>
                  <td className="hidden px-3 py-3 font-mono text-xs text-foreground md:table-cell">
                    {v.asset}
                  </td>
                  <td className="hidden px-3 py-3 lg:table-cell">
                    <StatusChip
                      label={vulnStatusLabel[v.status]}
                      tone={statusTone[v.status]}
                    />
                  </td>
                  <td className="px-3 py-3 text-right text-xs text-muted-foreground">
                    {v.due}
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-12 text-center text-sm text-muted-foreground"
                  >
                    No vulnerabilities match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
