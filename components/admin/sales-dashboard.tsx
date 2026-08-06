"use client"

import { useMemo } from "react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts"
import {
  DollarSign,
  TrendingUp,
  Trophy,
  Target,
  ArrowUpRight,
  BrainCircuit,
  ShieldAlert,
  UserPlus,
  ChartNoAxesCombined,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  leads,
  revenueTrend,
  repPerformance,
  LEAD_STAGES,
  STAGE_LABEL,
  OPEN_STAGES,
  formatCurrency,
  formatCompact,
} from "@/lib/sales"

const chartConfig = {
  booked: { label: "Booked MRR", color: "var(--chart-1)" },
  target: { label: "Target", color: "var(--chart-2)" },
} satisfies ChartConfig

export function SalesDashboard() {
  const metrics = useMemo(() => {
    const won = leads.filter((l) => l.stage === "won")
    const openLeads = leads.filter((l) => OPEN_STAGES.includes(l.stage))
    const closedCount = leads.filter((l) => l.stage === "won" || l.stage === "lost").length

    const newBusinessMrr = won.reduce((sum, l) => sum + l.value, 0)
    const openPipeline = openLeads.reduce((sum, l) => sum + l.value, 0)
    const weightedPipeline = openLeads.reduce(
      (sum, l) => sum + (l.value * l.probability) / 100,
      0,
    )
    const winRate = closedCount > 0 ? Math.round((won.length / closedCount) * 100) : 0

    return { newBusinessMrr, openPipeline, weightedPipeline, winRate }
  }, [])

  const funnel = useMemo(() => {
    const openStages = LEAD_STAGES.filter((s) => OPEN_STAGES.includes(s))
    const max = Math.max(
      ...openStages.map((s) => leads.filter((l) => l.stage === s).length),
      1,
    )
    return openStages.map((stage) => {
      const stageLeads = leads.filter((l) => l.stage === stage)
      return {
        stage,
        count: stageLeads.length,
        value: stageLeads.reduce((sum, l) => sum + l.value, 0),
        pct: (stageLeads.length / max) * 100,
      }
    })
  }, [])

  const kpis = [
    {
      label: "New Business (MRR)",
      value: formatCurrency(metrics.newBusinessMrr),
      delta: "+14% QoQ",
      icon: DollarSign,
    },
    {
      label: "Open Pipeline",
      value: formatCurrency(metrics.openPipeline),
      delta: `${formatCurrency(metrics.weightedPipeline)} weighted`,
      icon: TrendingUp,
    },
    {
      label: "Win Rate",
      value: `${metrics.winRate}%`,
      delta: "Closed deals",
      icon: Trophy,
    },
    {
      label: "Quota Attainment",
      value: "104%",
      delta: "Team blended",
      icon: Target,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((k) => (
          <Card key={k.label} className="glass">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <k.icon className="size-5 text-cyber" />
                <span className="inline-flex items-center gap-1 text-xs font-medium text-success">
                  <ArrowUpRight className="size-3" />
                  {k.delta}
                </span>
              </div>
              <div className="mt-4 font-display text-3xl font-bold text-foreground">
                {k.value}
              </div>
              <div className="mt-1 text-sm text-muted-foreground">{k.label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="glass lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-display text-base">New Business Booked vs Target</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="aspect-auto h-[280px] w-full">
              <AreaChart data={revenueTrend} margin={{ left: 4, right: 4, top: 8 }}>
                <defs>
                  <linearGradient id="fillBooked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-booked)" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="var(--color-booked)" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                  className="text-xs"
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                  width={44}
                  tickFormatter={(v) => `$${formatCompact(v as number)}`}
                  className="text-xs"
                />
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      formatter={(value, name) => [
                        formatCurrency(value as number),
                        chartConfig[name as keyof typeof chartConfig]?.label ?? name,
                      ]}
                    />
                  }
                />
                <Area
                  type="monotone"
                  dataKey="booked"
                  stroke="var(--color-booked)"
                  strokeWidth={2}
                  fill="url(#fillBooked)"
                />
                <Area
                  type="monotone"
                  dataKey="target"
                  stroke="var(--color-target)"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  fill="none"
                />
              </AreaChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle className="font-display text-base">Pipeline Funnel</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {funnel.map((f) => (
              <div key={f.stage}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="text-foreground">{STAGE_LABEL[f.stage]}</span>
                  <span className="font-mono text-xs text-muted-foreground">
                    {f.count} · {formatCurrency(f.value)}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${Math.max(f.pct, 6)}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="glass">
        <CardHeader>
          <CardTitle className="font-display text-base">Account Manager Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {repPerformance.map((rep) => (
              <div
                key={rep.name}
                className="rounded-lg border border-border/60 bg-secondary/30 p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">{rep.name}</span>
                  <span
                    className={
                      rep.quotaAttainment >= 100
                        ? "font-mono text-xs text-success"
                        : "font-mono text-xs text-warning"
                    }
                  >
                    {rep.quotaAttainment}%
                  </span>
                </div>
                <div className="mt-3 font-display text-2xl font-bold text-foreground">
                  {formatCurrency(rep.bookedMrr)}
                </div>
                <div className="mt-0.5 text-xs text-muted-foreground">
                  booked MRR · {rep.dealsWon} deals won
                </div>
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-secondary">
                  <div
                    className={
                      rep.quotaAttainment >= 100
                        ? "h-full rounded-full bg-success"
                        : "h-full rounded-full bg-warning"
                    }
                    style={{ width: `${Math.min(rep.quotaAttainment, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      <Card className="glass">

<CardHeader>

<CardTitle className="font-display text-base flex items-center gap-2">

<BrainCircuit className="size-5 text-cyber"/>

AI Growth Intelligence

</CardTitle>

</CardHeader>


<CardContent>


<div className="grid grid-cols-1 md:grid-cols-3 gap-4">


<div className="rounded-lg border border-border/60 bg-secondary/30 p-4">

<div className="flex items-center gap-2 text-sm text-muted-foreground">

<ChartNoAxesCombined className="size-4 text-cyber"/>

Q3 Revenue Forecast

</div>


<div className="mt-3 text-3xl font-display font-bold">

$420K

</div>


<p className="mt-1 text-xs text-success">

↑ 18% predicted growth

</p>

</div>





<div className="rounded-lg border border-border/60 bg-secondary/30 p-4">

<div className="flex items-center gap-2 text-sm text-muted-foreground">

<ShieldAlert className="size-4 text-warning"/>

Customer Churn Risk

</div>


<div className="mt-3 text-3xl font-display font-bold">

7%

</div>


<p className="mt-1 text-xs text-warning">

3 accounts require attention

</p>


</div>






<div className="rounded-lg border border-border/60 bg-secondary/30 p-4">


<div className="flex items-center gap-2 text-sm text-muted-foreground">

<UserPlus className="size-4 text-success"/>

Upsell Opportunities

</div>


<div className="mt-3 text-3xl font-display font-bold">

24

</div>


<p className="mt-1 text-xs text-success">

High-value accounts identified

</p>


</div>


</div>


</CardContent>

</Card>

    </div>
  )
}
