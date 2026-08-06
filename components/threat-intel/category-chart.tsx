'use client'

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'

const config = {
  value: { label: 'Events', color: 'var(--chart-1)' },
} satisfies ChartConfig

export function CategoryChart({
  data,
}: {
  data: { category: string; value: number }[]
}) {
  return (
    <ChartContainer config={config} className="h-[240px] w-full">
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid horizontal={false} stroke="var(--border)" strokeDasharray="3 3" />
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="category"
          tickLine={false}
          axisLine={false}
          width={104}
          className="text-[11px]"
          stroke="var(--muted-foreground)"
        />
        <ChartTooltip cursor={{ fill: 'var(--muted)', opacity: 0.4 }} content={<ChartTooltipContent />} />
        <Bar dataKey="value" fill="var(--color-value)" radius={4} barSize={16} />
      </BarChart>
    </ChartContainer>
  )
}
