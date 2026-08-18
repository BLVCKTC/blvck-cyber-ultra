"use client"

import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2 } from "lucide-react"
import { PageHeader } from "@/components/shell/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { SEED_SUBSCRIBERS } from "@/lib/mock-data"

export default function SubscriptionHealthPage() {
  const active = SEED_SUBSCRIBERS.filter((s) => s.status === "active")
  const pastDue = SEED_SUBSCRIBERS.filter((s) => s.status === "past-due")
  const cancelled = SEED_SUBSCRIBERS.filter((s) => s.status === "cancelled")
  const mrr = active.reduce((a, s) => a + s.mrr, 0)
  const failedMrr = pastDue.reduce((a, s) => a + s.mrr, 0)
  const churnRate = ((cancelled.length / SEED_SUBSCRIBERS.length) * 100).toFixed(1)
  const failedRate = ((pastDue.length / SEED_SUBSCRIBERS.length) * 100).toFixed(1)

  const stats = [
    { label: "MRR", value: `$${(mrr / 1000).toFixed(1)}k`, delta: "+6.4%", good: true, icon: DollarSign },
    { label: "Active Subscriptions", value: String(active.length), delta: `${SEED_SUBSCRIBERS.length} total`, good: true, icon: CheckCircle2 },
    { label: "Churn Rate", value: `${churnRate}%`, delta: `${cancelled.length} cancelled`, good: false, icon: TrendingDown },
    { label: "Failed Payment Rate", value: `${failedRate}%`, delta: `$${(failedMrr / 1000).toFixed(1)}k at risk`, good: false, icon: AlertTriangle },
  ]

  const byPlan = ["Starter", "Business", "Enterprise"].map((plan) => {
    const items = active.filter((s) => s.plan === plan)
    return {
      plan,
      count: items.length,
      mrr: items.reduce((a, s) => a + s.mrr, 0),
    }
  })

  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Subscription Health"
        description="Payment health, churn, and at-risk accounts across the subscriber base."
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
              <CardTitle className="font-display text-base">Failed / Past-Due Subscriptions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {pastDue.length === 0 ? (
                <p className="text-sm text-muted-foreground">No accounts currently past due.</p>
              ) : (
                pastDue.map((s) => (
                  <div
                    key={s.id}
                    className="flex flex-col gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <div className="font-medium text-foreground">{s.org}</div>
                      <div className="text-xs text-muted-foreground">
                        {s.plan} · ${s.mrr.toLocaleString()}/mo · renewal {s.renewal}
                      </div>
                      <div className="mt-1 text-xs text-destructive">
                        {s.history[0]?.action ?? "Payment failed"}
                      </div>
                    </div>
                    <Badge variant="outline" className="w-fit border-destructive/30 text-destructive">
                      Past due
                    </Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="glass">
            <CardHeader>
              <CardTitle className="font-display text-base">By Plan Tier</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {byPlan.map((p) => (
                <div key={p.plan}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span className="text-foreground">{p.plan}</span>
                    <span className="font-mono text-xs text-muted-foreground">
                      {p.count} · ${(p.mrr / 1000).toFixed(1)}k
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${mrr > 0 ? (p.mrr / mrr) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card className="glass">
          <CardHeader>
            <CardTitle className="font-display text-base">At-Risk Accounts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {SEED_SUBSCRIBERS.filter((s) => s.score < 75 && s.status === "active").map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between rounded-lg border border-border/60 bg-secondary/30 px-4 py-3"
              >
                <div>
                  <span className="text-sm text-foreground">{s.org}</span>
                  <span className="ml-2 font-mono text-xs text-muted-foreground">
                    Security score {s.score}
                  </span>
                </div>
                <Badge variant="outline" className="border-warning/30 text-warning">
                  Watch
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
