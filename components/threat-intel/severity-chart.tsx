'use client'

import { useMemo } from 'react'
import { Cell, Label, Pie, PieChart } from 'recharts'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { severityMeta, type Severity } from '@/lib/threat-data'

const config = {
  value: { label: 'Events' },
  critical: { label: 'Critical', color: 'var(--critical)' },
  high: { label: 'High', color: 'var(--high)' },
  warning: { label: 'Medium', color: 'var(--warning)' },
  info: { label: 'Low', color: 'var(--info)' },
} satisfies ChartConfig

export function SeverityChart({
  data,
}: {
  data: { severity: Severity; label: string; value: number }[]
}) {
  const total = useMemo(() => data.reduce((sum, d) => sum + d.value, 0), [data])

  return (
    <ChartContainer config={config} className="mx-auto aspect-square h-[240px]">
      <PieChart>
        <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
        <Pie
          data={data}
          dataKey="value"
          nameKey="severity"
          innerRadius={62}
          outerRadius={92}
          strokeWidth={2}
          stroke="var(--card)"
          paddingAngle={2}
        >
          {data.map((entry) => (
            <Cell key={entry.severity} fill={severityMeta[entry.severity].chart} />
          ))}
          <Label
            content={({ viewBox }) => {
              if (viewBox && 'cx' in viewBox && 'cy' in viewBox) {
                return (
                  <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle" dominantBaseline="middle">
                    <tspan
                      x={viewBox.cx}
                      y={viewBox.cy}
                      className="fill-foreground font-display text-3xl font-bold"
                    >
                      {total.toLocaleString()}
                    </tspan>
                    <tspan
                      x={viewBox.cx}
                      y={(viewBox.cy ?? 0) + 22}
                      className="fill-muted-foreground text-xs"
                    >
                      Events
                    </tspan>
                  </text>
                )
              }
              return null
            }}
          />
        </Pie>
      </PieChart>
    </ChartContainer>
  )
}
