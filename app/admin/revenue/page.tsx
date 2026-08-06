"use client"

import { DollarSign, TrendingUp, TrendingDown, Users, ArrowUpRight } from "lucide-react"
import { PageHeader } from "@/components/shell/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart"

const stats = [
  { label: "MRR", value: "$284,600", delta: "+8.2%", good: true, icon: DollarSign },
  { label: "ARR", value: "$3.42M", delta: "+8.2%", good: true, icon: TrendingUp },
  { label: "ARPU", value: "$1,247", delta: "+3.1%", good: true, icon: Users },
  { label: "Net Revenue Retention", value: "112%", delta: "-2pts", good: false, icon: ArrowUpRight },
]

const revenueTrend = [
  { month: "Feb", mrr: 198000 },
  { month: "Mar", mrr: 212000 },
  { month: "Apr", mrr: 227000 },
  { month: "May", mrr: 241000 },
  { month: "Jun", mrr: 263000 },
  { month: "Jul", mrr: 284600 },
]

const revenueByTier = [
  { tier: "Starter", revenue: 42300 },
  { tier: "Business", revenue: 118900 },
  { tier: "Enterprise", revenue: 123400 },
]

const trendConfig = {
  mrr: { label: "MRR", color: "var(--chart-1)" },
} satisfies ChartConfig

const tierConfig = {
  revenue: { label: "Revenue", color: "var(--chart-3)" },
} satisfies ChartConfig

export default function RevenueAnalyticsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Revenue Analytics"
        description="Recurring revenue performance across the customer base — trends, tier breakdown, and retention health."
      />

      <div className="space-y-6 p-4 lg:p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((s) => (
            <Card key={s.label} className="glass">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <s.icon className="size-5 text-primary" />
                  <span
                    className={
                      "inline-flex items-center gap-1 text-xs font-medium " +
                      (s.good ? "text-success" : "text-destructive")
                    }
                  >
                    {s.good ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                    {s.delta}
                  </span>
                </div>
                <div className="mt-4 font-display text-3xl font-bold text-foreground">{s.value}</div>
                <div className="mt-1 text-sm text-muted-foreground">{s.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="glass lg:col-span-2">
            <CardHeader>
              <CardTitle className="font-display text-base">MRR Trend (6 months)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={trendConfig} className="h-64 w-full aspect-auto">
                <AreaChart data={revenueTrend} margin={{ left: -12, right: 12 }}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="month" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => `$${v / 1000}k`} />
                  <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
                  <Area
                    type="monotone"
                    dataKey="mrr"
                    stroke="var(--color-mrr)"
                    fill="var(--color-mrr)"
                    fillOpacity={0.14}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>

          <Card className="glass">
            <CardHeader>
              <CardTitle className="font-display text-base">Revenue by Tier</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={tierConfig} className="h-64 w-full aspect-auto">
                <BarChart data={revenueByTier} margin={{ left: -12, right: 12 }}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="tier" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => `$${v / 1000}k`} />
                  <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
                  <Bar dataKey="revenue" fill="var(--color-revenue)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ChartContainer>
              <div className="mt-4 flex flex-wrap gap-2">
                {revenueByTier.map((t) => (
                  <Badge key={t.tier} variant="outline" className="font-mono text-xs">
                    {t.tier}: ${(t.revenue / 1000).toFixed(1)}k
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
