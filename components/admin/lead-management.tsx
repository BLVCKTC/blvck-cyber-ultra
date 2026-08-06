"use client"

import { useMemo, useState } from "react"
import { Search, TrendingUp, Layers, Percent, X } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import {
  leads,
  LEAD_STAGES,
  STAGE_LABEL,
  SOURCES,
  OPEN_STAGES,
  formatCurrency,
  formatDate,
  type Lead,
  type LeadStage,
  type LeadSource,
} from "@/lib/sales"

const stageBadge: Record<LeadStage, string> = {
  new: "bg-muted text-muted-foreground border-border",
  qualified: "bg-primary/15 text-primary border-primary/30",
  demo: "bg-primary/15 text-primary border-primary/30",
  proposal: "bg-warning/15 text-warning border-warning/30",
  negotiation: "bg-warning/15 text-warning border-warning/30",
  won: "bg-success/15 text-success border-success/30",
  lost: "bg-destructive/15 text-destructive border-destructive/30",
}

export function LeadManagement() {
  const [query, setQuery] = useState("")
  const [stage, setStage] = useState<LeadStage | "all">("all")
  const [source, setSource] = useState<LeadSource | "all">("all")
  const [selected, setSelected] = useState<Lead | null>(null)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return leads.filter((l) => {
      if (stage !== "all" && l.stage !== stage) return false
      if (source !== "all" && l.source !== source) return false
      if (
        q &&
        !l.company.toLowerCase().includes(q) &&
        !l.contactName.toLowerCase().includes(q) &&
        !l.owner.toLowerCase().includes(q)
      )
        return false
      return true
    })
  }, [query, stage, source])

  const stats = useMemo(() => {
    const open = leads.filter((l) => OPEN_STAGES.includes(l.stage))
    const openValue = open.reduce((sum, l) => sum + l.value, 0)
    const avgProb =
      open.length > 0
        ? Math.round(open.reduce((sum, l) => sum + l.probability, 0) / open.length)
        : 0
    return { openCount: open.length, openValue, avgProb }
  }, [])

  const hasFilters = query !== "" || stage !== "all" || source !== "all"

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={Layers} label="Open Leads" value={String(stats.openCount)} />
        <StatCard
          icon={TrendingUp}
          label="Open Pipeline Value"
          value={formatCurrency(stats.openValue)}
        />
        <StatCard icon={Percent} label="Avg. Win Probability" value={`${stats.avgProb}%`} />
      </div>

      <Card className="glass">
        <CardContent className="p-0">
          <div className="flex flex-col gap-3 border-b border-border p-4 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Search leads"
                placeholder="Search company, contact, or owner..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={stage} onValueChange={(v) => setStage(v as LeadStage | "all")}>
              <SelectTrigger className="w-full sm:w-40" aria-label="Filter by stage">
                <SelectValue placeholder="Stage" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All stages</SelectItem>
                {LEAD_STAGES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {STAGE_LABEL[s]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={source} onValueChange={(v) => setSource(v as LeadSource | "all")}>
              <SelectTrigger className="w-full sm:w-40" aria-label="Filter by source">
                <SelectValue placeholder="Source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All sources</SelectItem>
                {SOURCES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {hasFilters ? (
              <button
                onClick={() => {
                  setQuery("")
                  setStage("all")
                  setSource("all")
                }}
                className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                <X className="size-4" />
                Clear
              </button>
            ) : null}
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Company</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead className="text-right">Value</TableHead>
                  <TableHead className="text-right">Prob.</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((l) => (
                  <TableRow
                    key={l.id}
                    onClick={() => setSelected(l)}
                    className="cursor-pointer"
                  >
                    <TableCell>
                      <div className="font-medium text-foreground">{l.company.trim()}</div>
                      <div className="text-xs text-muted-foreground">
                        {l.contactName} · {l.title}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{l.owner}</TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">{l.source}</span>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={stageBadge[l.stage]}>
                        {STAGE_LABEL[l.stage]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm text-foreground">
                      {formatCurrency(l.value)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm text-muted-foreground">
                      {l.probability}%
                    </TableCell>
                  </TableRow>
                ))}
                {filtered.length === 0 ? (
                  <TableRow className="hover:bg-transparent">
                    <TableCell colSpan={6} className="py-12 text-center text-muted-foreground">
                      No leads match your filters.
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </div>

          <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
            Showing {filtered.length} of {leads.length} leads
          </div>
        </CardContent>
      </Card>

      <Sheet open={selected !== null} onOpenChange={(open) => !open && setSelected(null)}>
        <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-md">
          {selected ? (
            <>
              <SheetHeader>
                <SheetTitle className="font-display text-xl">
                  {selected.company.trim()}
                </SheetTitle>
                <SheetDescription>
                  {selected.contactName} · {selected.title}
                </SheetDescription>
              </SheetHeader>
              <div className="space-y-6 px-4 pb-6">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className={stageBadge[selected.stage]}>
                    {STAGE_LABEL[selected.stage]}
                  </Badge>
                  <Badge variant="outline">{selected.source}</Badge>
                  <Badge variant="outline">{selected.region}</Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <DetailStat label="Deal Value" value={formatCurrency(selected.value)} />
                  <DetailStat label="Win Probability" value={`${selected.probability}%`} />
                  <DetailStat label="Owner" value={selected.owner} />
                  <DetailStat label="Lead ID" value={selected.id} mono />
                  <DetailStat label="Created" value={formatDate(selected.createdAt)} />
                  <DetailStat label="Last Activity" value={formatDate(selected.lastActivityAt)} />
                </div>

                <div>
                  <div className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Contact
                  </div>
                  <a
                    href={`mailto:${selected.email}`}
                    className="text-sm text-primary hover:underline"
                  >
                    {selected.email}
                  </a>
                </div>

                <div>
                  <div className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Notes
                  </div>
                  <p className="text-sm leading-relaxed text-foreground">{selected.note}</p>
                </div>
              </div>
            </>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: string
}) {
  return (
    <Card className="glass">
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
          <Icon className="size-5" />
        </div>
        <div>
          <div className="font-display text-2xl font-bold text-foreground">{value}</div>
          <div className="text-sm text-muted-foreground">{label}</div>
        </div>
      </CardContent>
    </Card>
  )
}

function DetailStat({
  label,
  value,
  mono,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className={mono ? "mt-0.5 font-mono text-sm text-foreground" : "mt-0.5 text-sm text-foreground"}>
        {value}
      </div>
    </div>
  )
}
