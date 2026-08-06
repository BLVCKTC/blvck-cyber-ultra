"use client"

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart"

const data = [
  { day: "Mon", blocked: 342, investigated: 42 }, { day: "Tue", blocked: 481, investigated: 51 },
  { day: "Wed", blocked: 398, investigated: 36 }, { day: "Thu", blocked: 620, investigated: 74 },
  { day: "Fri", blocked: 552, investigated: 62 }, { day: "Sat", blocked: 318, investigated: 29 },
  { day: "Sun", blocked: 407, investigated: 45 },
]
const config = { blocked: { label: "Blocked", color: "var(--chart-1)" }, investigated: { label: "Investigated", color: "var(--chart-3)" } } satisfies ChartConfig

export function IncidentTrendChart() {
  return <ChartContainer config={config} className="h-64 w-full aspect-auto"><AreaChart data={data} margin={{ left: -12, right: 12 }}><CartesianGrid vertical={false} strokeDasharray="3 3" /><XAxis dataKey="day" tickLine={false} axisLine={false} /><YAxis tickLine={false} axisLine={false} /><ChartTooltip content={<ChartTooltipContent indicator="line" />} /><Area type="monotone" dataKey="blocked" stroke="var(--color-blocked)" fill="var(--color-blocked)" fillOpacity={0.14} strokeWidth={2} /><Area type="monotone" dataKey="investigated" stroke="var(--color-investigated)" fill="transparent" strokeWidth={2} /></AreaChart></ChartContainer>
}
