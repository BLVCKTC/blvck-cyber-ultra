'use client'

import { useEffect, useMemo, useState } from 'react'

import { API_URL, authenticatedFetch } from '@/lib/api/client'

type BreakdownProps = {
  tenantId: string
  window?: '24h'
}

type SeverityItem = {
  severity: string
  count: number
}

type SourceItem = {
  name: string
  value: number
}

const severityColors: Record<string, string> = {
  critical: 'var(--fill-danger, var(--critical))',
  high: 'var(--fill-warning, var(--high))',
  medium: 'var(--fill-accent, var(--warning))',
  low: 'var(--fill-muted, var(--muted-foreground))',
  warning: 'var(--fill-warning, var(--warning))',
  info: 'var(--fill-accent, var(--info))',
}

const severityLabels: Record<string, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  warning: 'Warning',
  info: 'Informational',
}

const sourceColors: Record<string, string> = {
  EDR: 'var(--source-edr, #8b5cf6)',
  Cloud: 'var(--source-cloud, #06b6d4)',
  Network: 'var(--source-network, #3b82f6)',
  Identity: 'var(--source-identity, #14b8a6)',
}

const fallbackSourceColors = ['#8b5cf6', '#06b6d4', '#3b82f6', '#14b8a6']

function Donut({
  items,
  getLabel,
  getValue,
  getColor,
  summary,
}: {
  items: Array<SeverityItem | SourceItem>
  getLabel: (item: SeverityItem | SourceItem) => string
  getValue: (item: SeverityItem | SourceItem) => number
  getColor: (item: SeverityItem | SourceItem, index: number) => string
  summary: string
}) {
  const total = items.reduce((sum, item) => sum + getValue(item), 0)
  const radius = 38
  const circumference = 2 * Math.PI * radius

  let accumulated = 0

  return (
    <div className="flex items-center gap-5">
      <div className="relative h-32 w-32 shrink-0">
        <svg
          viewBox="0 0 100 100"
          className="h-full w-full -rotate-90"
          role="img"
          aria-label={summary}
        >
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="var(--muted)"
            strokeWidth="11"
          />

          {items.map((item, index) => {
            const value = getValue(item)
            const segment = total > 0 ? (value / total) * circumference : 0
            const offset = accumulated
            accumulated += segment

            return (
              <circle
                key={`${getLabel(item)}-${index}`}
                cx="50"
                cy="50"
                r={radius}
                fill="none"
                stroke={getColor(item, index)}
                strokeWidth="11"
                strokeDasharray={`${segment} ${circumference - segment}`}
                strokeDashoffset={-offset}
                strokeLinecap="butt"
              />
            )
          })}
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold tabular text-foreground">
            {total}
          </span>
          <span className="text-[10px] text-muted-foreground">total</span>
        </div>
      </div>

      <ul className="min-w-0 flex-1 space-y-2">
        {items.map((item, index) => (
          <li
            key={`${getLabel(item)}-${index}`}
            className="flex items-center gap-2 text-xs"
          >
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: getColor(item, index) }}
              aria-hidden="true"
            />

            <span className="truncate text-muted-foreground">
              {getLabel(item)}
            </span>

            <span className="ml-auto tabular font-medium text-foreground">
              {getValue(item)}
            </span>
          </li>
        ))}
      </ul>

      <p className="sr-only">{summary}</p>
    </div>
  )
}

export function SeverityBreakdown({
  tenantId,
  window = '24h',
}: BreakdownProps) {
  const [items, setItems] = useState<SeverityItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadSeverityBreakdown() {
      try {
        const response = await authenticatedFetch(
          `${API_URL}/v1/tenants/${tenantId}/alerts/severity-breakdown?window=${window}`,
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load severity breakdown')
        }

        const result = await response.json()
        setItems(result.data ?? result.segments ?? result)
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadSeverityBreakdown()

    return () => controller.abort()
  }, [tenantId, window])

  if (loading) {
    return <div className="h-32 animate-pulse rounded-md bg-muted" />
  }

  return (
    <Donut
      items={items}
      getLabel={(item) =>
        severityLabels[(item as SeverityItem).severity] ??
        (item as SeverityItem).severity
      }
      getValue={(item) => (item as SeverityItem).count}
      getColor={(item) =>
        severityColors[(item as SeverityItem).severity] ??
        'var(--fill-muted, var(--muted-foreground))'
      }
      summary={`Donut chart showing ${items.length} alert severity categories over the last ${window}.`}
    />
  )
}

export function DetectionSources({ tenantId, window = '24h' }: BreakdownProps) {
  const [items, setItems] = useState<SourceItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadDetectionSources() {
      try {
        const response = await authenticatedFetch(
          `${API_URL}/v1/tenants/${tenantId}/events/source-breakdown?window=${window}`,
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load detection sources')
        }

        const result = await response.json()
        setItems(result.data ?? result.segments ?? result)
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadDetectionSources()

    return () => controller.abort()
  }, [tenantId, window])

  const colors = useMemo(() => {
    return items.reduce<Record<string, string>>((result, item, index) => {
      result[item.name] =
        sourceColors[item.name] ??
        fallbackSourceColors[index % fallbackSourceColors.length]
      return result
    }, {})
  }, [items])

  if (loading) {
    return <div className="h-32 animate-pulse rounded-md bg-muted" />
  }

  return (
    <Donut
      items={items}
      getLabel={(item) => (item as SourceItem).name}
      getValue={(item) => (item as SourceItem).value}
      getColor={(item) => colors[(item as SourceItem).name]}
      summary={`Donut chart showing detection events by source over the last ${window}.`}
    />
  )
}
