'use client'

import { useEffect, useState } from 'react'

import { API_URL, authenticatedFetch } from '@/lib/api/client'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export type AlertVolumeRange =
  | 'hourly'
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'yearly'

type AlertVolumeBucket = {
  label: string
  total: number
  escalated: number
}

type AlertVolumeChartProps = {
  tenantId: string
  defaultRange?: AlertVolumeRange
}

const ranges: Array<{
  label: string
  value: AlertVolumeRange
}> = [
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Yearly', value: 'yearly' },
]

const axisTick = {
  fill: 'var(--muted-foreground)',
  fontSize: 11,
}

export function AlertVolumeChart({
  tenantId,
  defaultRange = 'daily',
}: AlertVolumeChartProps) {
  const [range, setRange] = useState<AlertVolumeRange>(defaultRange)
  const [data, setData] = useState<AlertVolumeBucket[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    async function loadAlertVolume() {
      try {
        setLoading(true)

        const response = await authenticatedFetch(
          `${API_URL}/v1/tenants/${tenantId}/alerts/volume?range=${range}`,
          {
            signal: controller.signal,
            cache: 'no-store',
          },
        )

        if (!response.ok) {
          throw new Error('Failed to load alert volume')
        }

        const result = await response.json()
        const buckets = result.buckets ?? result.data ?? []

        setData(
          buckets.map((bucket: AlertVolumeBucket) => ({
            label: bucket.label,
            total: bucket.total ?? 0,
            escalated: bucket.escalated ?? 0,
            base: Math.max((bucket.total ?? 0) - (bucket.escalated ?? 0), 0),
          })),
        )
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error(error)
        setData([])
      } finally {
        setLoading(false)
      }
    }

    loadAlertVolume()

    return () => controller.abort()
  }, [tenantId, range])

  const max = Math.max(...data.map((item) => item.total), 0)

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-sm bg-primary" aria-hidden="true" />
            Total alerts
          </span>

          <span className="flex items-center gap-1.5">
            <span
              className="size-2 rounded-sm bg-critical"
              aria-hidden="true"
            />
            Escalated
          </span>
        </div>

        <div
          className="flex gap-1"
          role="tablist"
          aria-label="Alert volume range"
        >
          {ranges.map((item) => (
            <button
              key={item.value}
              type="button"
              role="tab"
              aria-selected={range === item.value}
              onClick={() => setRange(item.value)}
              className={
                range === item.value
                  ? 'rounded-md border border-primary bg-primary/10 px-2.5 py-1 text-xs text-primary'
                  : 'rounded-md border border-border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:text-foreground'
              }
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <p className="sr-only">
        Stacked bar chart showing total and escalated alert volume for the
        selected {range} range.
      </p>

      <div className="h-64 w-full">
        {loading ? (
          <div className="h-full w-full animate-pulse rounded-md bg-muted" />
        ) : data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            No alert volume data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 8, right: 8, left: -16, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--border)"
                vertical={false}
              />

              <XAxis
                dataKey="label"
                tick={axisTick}
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                domain={[0, max || 1]}
                tick={axisTick}
                axisLine={false}
                tickLine={false}
                width={40}
              />

              <Tooltip
                cursor={{
                  fill: 'var(--muted)',
                  opacity: 0.35,
                }}
                contentStyle={{
                  background: 'var(--popover)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  fontSize: 12,
                  color: 'var(--foreground)',
                }}
              />

              <Bar
                dataKey="base"
                name="Alerts"
                stackId="volume"
                fill="var(--primary)"
                radius={[4, 4, 0, 0]}
              />

              <Bar
                dataKey="escalated"
                name="Escalated"
                stackId="volume"
                fill="var(--critical)"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
