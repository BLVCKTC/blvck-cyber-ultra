"use client"

import { useMemo, useState } from "react"
import { Search, Users, DollarSign, TriangleAlert, Activity } from "lucide-react"
import {
  subscribers as allSubscribers,
  TIERS,
  STATUSES,
  STATUS_LABEL,
  formatCurrency,
  formatDate,
  type Subscriber,
  type SubscriptionTier,
  type SubscriberStatus,
} from "@/lib/subscribers"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { SubscriberDetail } from "@/components/admin/subscriber-detail"

function StatusBadge({ status }: { status: SubscriberStatus }) {
  const styles: Record<SubscriberStatus, string> = {
    active: "border-primary/40 bg-primary/10 text-primary",
    trial: "border-sky-400/40 bg-sky-400/10 text-sky-300",
    past_due: "border-amber-400/40 bg-amber-400/10 text-amber-300",
    churned: "border-muted-foreground/30 bg-muted text-muted-foreground",
  }
  return (
    <Badge variant="outline" className={styles[status]}>
      {STATUS_LABEL[status]}
    </Badge>
  )
}

function HealthBar({ score }: { score: number }) {
  const color =
    score >= 80 ? "bg-primary" : score >= 60 ? "bg-amber-400" : "bg-destructive"
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground">{score}</span>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  hint,
}: {
  icon: typeof Users
  label: string
  value: string
  hint?: string
}) {
  return (
    <Card className="flex items-center gap-4 p-4">
      <div className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
        <Icon className="size-5" />
      </div>
      <div className="min-w-0">
        <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </div>
        <div className="font-display text-xl font-bold text-foreground">{value}</div>
        {hint ? <div className="text-xs text-muted-foreground">{hint}</div> : null}
      </div>
    </Card>
  )
}

export function SubscriberManagement() {
  const [query, setQuery] = useState("")
  const [tier, setTier] = useState<SubscriptionTier | "all">("all")
  const [status, setStatus] = useState<SubscriberStatus | "all">("all")
  const [selected, setSelected] = useState<Subscriber | null>(null)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return allSubscribers.filter((s) => {
      const matchesQuery =
        !q ||
        s.company.toLowerCase().includes(q) ||
        s.contactName.toLowerCase().includes(q) ||
        s.email.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q)
      const matchesTier = tier === "all" || s.tier === tier
      const matchesStatus = status === "all" || s.status === status
      return matchesQuery && matchesTier && matchesStatus
    })
  }, [query, tier, status])

  const stats = useMemo(() => {
    const active = allSubscribers.filter((s) => s.status === "active")
    const totalMrr = allSubscribers.reduce((sum, s) => sum + s.mrr, 0)
    const atRisk = allSubscribers.filter(
      (s) => s.status === "past_due" || (s.status !== "churned" && s.healthScore < 65),
    ).length
    const openIncidents = allSubscribers.reduce((sum, s) => sum + s.openIncidents, 0)
    return {
      activeCount: active.length,
      totalMrr,
      atRisk,
      openIncidents,
    }
  }, [])

  return (
    <div className="flex flex-col gap-6 p-4 lg:p-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Users}
          label="Active accounts"
          value={String(stats.activeCount)}
          hint={`${allSubscribers.length} total subscribers`}
        />
        <StatCard
          icon={DollarSign}
          label="Monthly recurring"
          value={formatCurrency(stats.totalMrr)}
          hint="Across all tiers"
        />
        <StatCard
          icon={TriangleAlert}
          label="At-risk accounts"
          value={String(stats.atRisk)}
          hint="Past due or low health"
        />
        <StatCard
          icon={Activity}
          label="Open incidents"
          value={String(stats.openIncidents)}
          hint="Currently under SOC review"
        />
      </div>

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-border p-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:max-w-xs">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search company, contact, email..."
              className="pl-9"
              aria-label="Search subscribers"
            />
          </div>
          <div className="flex items-center gap-2">
            <Select value={tier} onValueChange={(v) => setTier(v as SubscriptionTier | "all")}>
              <SelectTrigger className="w-[150px]" aria-label="Filter by tier">
                <SelectValue placeholder="Tier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All tiers</SelectItem>
                {TIERS.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={(v) => setStatus(v as SubscriberStatus | "all")}>
              <SelectTrigger className="w-[150px]" aria-label="Filter by status">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {STATUS_LABEL[s]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Company</TableHead>
                <TableHead>Tier</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">MRR</TableHead>
                <TableHead className="text-right">Endpoints</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Renewal</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((s) => (
                <TableRow
                  key={s.id}
                  className="cursor-pointer"
                  onClick={() => setSelected(s)}
                  tabIndex={0}
                  role="button"
                  aria-label={`View details for ${s.company}`}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault()
                      setSelected(s)
                    }
                  }}
                >
                  <TableCell>
                    <div className="font-medium text-foreground">{s.company}</div>
                    <div className="text-xs text-muted-foreground">{s.contactName}</div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-foreground">{s.tier}</span>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={s.status} />
                  </TableCell>
                  <TableCell className="text-right tabular-nums text-foreground">
                    {formatCurrency(s.mrr)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums text-muted-foreground">
                    {s.endpointsProtected.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <HealthBar score={s.healthScore} />
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(s.renewalAt)}
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 ? (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={7} className="py-12 text-center text-muted-foreground">
                    No subscribers match your filters.
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </div>
        <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
          Showing {filtered.length} of {allSubscribers.length} subscribers
        </div>
      </Card>

      <SubscriberDetail
        subscriber={selected}
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
      />
    </div>
  )
}
