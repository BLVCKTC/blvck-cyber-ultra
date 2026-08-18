'use client'

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import type { TimelinePoint } from '@/lib/threat-data'

const config = {
  detected: { label: 'Detected', color: 'var(--chart-2)' },
  blocked: { label: 'Blocked', color: 'var(--chart-1)' },
} satisfies ChartConfig

export function TimelineChart({ data }: { data: TimelinePoint[] }) {
  return (
    <ChartContainer config={config} className="h-[240px] w-full">
      <AreaChart data={data} margin={{ left: 4, right: 8, top: 8 }}>
        <defs>
          <linearGradient id="fillDetected" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--color-detected)" stopOpacity={0.4} />
            <stop offset="95%" stopColor="var(--color-detected)" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="fillBlocked" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--color-blocked)" stopOpacity={0.5} />
            <stop offset="95%" stopColor="var(--color-blocked)" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          minTickGap={16}
          className="text-[10px]"
          stroke="var(--muted-foreground)"
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          width={28}
          className="text-[10px]"
          stroke="var(--muted-foreground)"
        />
        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
        <Area
          dataKey="detected"
          type="monotone"
          fill="url(#fillDetected)"
          stroke="var(--color-detected)"
          strokeWidth={2}
        />
        <Area
          dataKey="blocked"
          type="monotone"
          fill="url(#fillBlocked)"
          stroke="var(--color-blocked)"
          strokeWidth={2}
        />
      </AreaChart>
    </ChartContainer>
  )
}
