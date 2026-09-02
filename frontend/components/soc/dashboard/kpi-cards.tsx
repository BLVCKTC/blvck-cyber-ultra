'use client'

import { useEffect, useState } from 'react'
import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react'

import { cn } from '@/lib/utils'
import { API_URL, authenticatedFetch } from '@/lib/api/client'

type KpiCardsProps = {
  tenantId: string
}

type KpiTrend = 'up' | 'down' | 'flat'

type Kpi = {
  key: string
  label: string
  value: string | number
  delta?: string
  sub?: string
  trend: KpiTrend
  goodWhenUp?: boolean
}

type KpiResponse = {
  openAlerts?: {
    value: number
    delta?: number
    trend?: KpiTrend
  }
  activeIncidents?: {
    value: number
    unassigned?: number
    delta?: number
    trend?: KpiTrend
  }
  mitreCoverage?: {
    covered: number
    total: number
  }
  meanTimeToTriage?: {
    value: number
    unit?: string
    delta?: number
    trend?: KpiTrend
  }
}

function formatDelta(delta?: number, suffix = '') {
  if (delta === undefined || delta === null) return '—'

  const prefix = delta > 0 ? '+' : ''

  return `${prefix}${delta}${suffix}`
}

function formatDuration(minutes: number) {
  if (minutes < 60) {
    return `${Math.round(minutes)}m`
  }

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = Math.round(minutes % 60)

  if (remainingMinutes === 0) {
    return `${hours}h`
  }

  return `${hours}h ${remainingMinutes}m`
}

export function KpiCards({ tenantId }: KpiCardsProps) {
  const [data, setData] = useState<KpiResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadKpis() {
      try {
        setLoading(true)

        const response = await authenticatedFetch(
          `${API_URL}/v1/tenants/${tenantId}/dashboard/kpis`,
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load dashboard KPIs')
        }

        const result = await response.json()
        setData(result.data ?? result)
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadKpis()

    return () => controller.abort()
  }, [tenantId])

  const coverage = data?.mitreCoverage
    ? Math.round(
        (data.mitreCoverage.covered / Math.max(data.mitreCoverage.total, 1)) *
          100,
      )
    : 0

  const kpis: Kpi[] = [
    {
      key: 'open-alerts',
      label: 'Open alerts',
      value: data?.openAlerts?.value ?? 0,
      delta: formatDelta(data?.openAlerts?.delta),
      sub: 'vs. same time yesterday',
      trend: data?.openAlerts?.trend ?? 'flat',
      goodWhenUp: false,
    },
    {
      key: 'active-incidents',
      label: 'Active incidents',
      value: data?.activeIncidents?.value ?? 0,
      delta: formatDelta(data?.activeIncidents?.delta),
      sub: `${data?.activeIncidents?.unassigned ?? 0} unassigned`,
      trend: data?.activeIncidents?.trend ?? 'flat',
      goodWhenUp: false,
    },
    {
      key: 'mitre-coverage',
      label: 'MITRE coverage',
      value: `${coverage}%`,
      delta: 'Snapshot',
      sub: data?.mitreCoverage
        ? `${data.mitreCoverage.covered} of ${data.mitreCoverage.total} techniques`
        : 'Coverage unavailable',
      trend: 'flat',
    },
    {
      key: 'mean-time-to-triage',
      label: 'Mean time to triage',
      value: data?.meanTimeToTriage
        ? formatDuration(data.meanTimeToTriage.value)
        : '—',
      delta: formatDelta(data?.meanTimeToTriage?.delta, 'm'),
      sub: 'vs. trailing 7-day average',
      trend: data?.meanTimeToTriage?.trend ?? 'flat',
      goodWhenUp: false,
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi) => {
        const positive =
          kpi.trend === 'flat'
            ? null
            : (kpi.trend === 'up') === Boolean(kpi.goodWhenUp)

        const TrendIcon =
          kpi.trend === 'up'
            ? ArrowUpRight
            : kpi.trend === 'down'
              ? ArrowDownRight
              : Minus

        return (
          <div
            key={kpi.key}
            className="rounded-lg border border-border bg-card p-4"
          >
            <p className="text-sm text-muted-foreground">{kpi.label}</p>

            <div className="mt-2 flex items-baseline gap-2">
              <span
                className={cn(
                  'text-3xl font-semibold tracking-tight text-foreground',
                  loading && 'animate-pulse text-muted',
                )}
              >
                {loading ? '—' : kpi.value}
              </span>

              <span
                className={cn(
                  'inline-flex items-center gap-0.5 text-xs font-medium tabular',
                  positive === null && 'text-muted-foreground',
                  positive === true && 'text-success',
                  positive === false && 'text-high',
                )}
              >
                <TrendIcon className="h-3.5 w-3.5" />
                {kpi.delta}
              </span>
            </div>

            <p className="mt-1 text-xs text-muted-foreground">{kpi.sub}</p>
          </div>
        )
      })}
    </div>
  )
}
