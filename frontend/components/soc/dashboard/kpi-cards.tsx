'use client'

import { useEffect, useState } from 'react'

import { cn } from '@/lib/utils'
import { authenticatedFetch, tenantApiPath } from '@/lib/api/client'

type KpiCardsProps = {
  tenantId: string
}

type DashboardKpis = {
  openAlerts: number
  activeIncidents: number
  mitreCoverage: number
  meanTimeToTriage: number | null
}

type KpiResponse = {
  data: DashboardKpis
}

function formatDuration(minutes: number | null) {
  if (minutes === null) {
    return 'Unavailable'
  }

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
  const [data, setData] = useState<DashboardKpis | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadKpis() {
      try {
        setLoading(true)

        const response = await authenticatedFetch(
          tenantApiPath(tenantId, 'dashboard/kpis'),
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load dashboard KPIs')
        }

        const result: KpiResponse = await response.json()

        setData(result.data)
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }

        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadKpis()

    return () => controller.abort()
  }, [tenantId])

  const coverage = data?.mitreCoverage ?? null

  const kpis = [
    {
      key: 'open-alerts',
      label: 'Open alerts',
      value: data?.openAlerts ?? 0,
      sub: 'Currently open',
    },
    {
      key: 'active-incidents',
      label: 'Active incidents',
      value: data?.activeIncidents ?? 0,
      sub: 'Currently active',
    },
    {
      key: 'mitre-coverage',
      label: 'MITRE coverage',
      value: coverage !== null ? `${Math.round(coverage)}%` : '—',
      sub: 'Coverage snapshot',
    },
    {
      key: 'mean-time-to-triage',
      label: 'Mean time to triage',
      value: formatDuration(data?.meanTimeToTriage ?? null),
      sub:
        data?.meanTimeToTriage === null
          ? 'Not currently calculated'
          : 'Measured triage duration',
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi) => (
        <div
          key={kpi.key}
          className="rounded-lg border border-border bg-card p-4"
        >
          <p className="text-sm text-muted-foreground">{kpi.label}</p>

          <div className="mt-2">
            <span
              className={cn(
                'text-3xl font-semibold tracking-tight text-foreground',
                loading && 'animate-pulse text-muted',
              )}
            >
              {loading ? '—' : kpi.value}
            </span>
          </div>

          <p className="mt-1 text-xs text-muted-foreground">{kpi.sub}</p>
        </div>
      ))}
    </div>
  )
}
