"use client"

import { useMemo, useState } from "react"
import { Activity, AlertTriangle, FilterX, Globe2, Radar, RadioTower, ShieldAlert } from "lucide-react"
import { PageHeader } from "@/components/shell/page-header"
import { StatCard } from "@/components/shell/stat-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { filterOptions, threatEvents } from "@/lib/threat-data"
import { CategoryChart, ThreatTrendChart } from "./threat-charts"
import { LiveFeed } from "./live-feed"
import { SourcesTable } from "./sources-table"
import { ThreatMap } from "./threat-map"

const initialFilters = {
  severity: "All severities",
  region: "All regions",
  industry: "All industries",
  type: "All threat types",
  technique: "All techniques",
  tactic: "All tactics",
}
type FilterKey = keyof typeof initialFilters

const severityMap = {
  Critical: "critical",
  High: "high",
  Medium: "warning",
  Low: "info",
} as const

type SourceAgg = {
  country: string
  code: string
  city: string
  coordinates: [number, number]
  count: number
  critical: number
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (value: string) => void
}) {
  return (
    <Select value={value} onValueChange={(v) => onChange(String(v))}>
      <SelectTrigger aria-label={label} className="w-full">
        <SelectValue>{value}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}

export function ThreatIntelView() {
  const [filters, setFilters] = useState(initialFilters)
  const [selected, setSelected] = useState<string>()

  const events = useMemo(
    () =>
      threatEvents.filter(
        (e) =>
          (filters.severity === "All severities" ||
            e.severity === severityMap[filters.severity as keyof typeof severityMap]) &&
          (filters.region.startsWith("All") || e.region === filters.region) &&
          (filters.industry.startsWith("All") || e.industry === filters.industry) &&
          (filters.type.startsWith("All") || e.type === filters.type) &&
          (filters.technique.startsWith("All") || e.technique === filters.technique) &&
          (filters.tactic.startsWith("All") || e.tactic === filters.tactic)
      ),
    [filters]
  )

  const sources = useMemo(() => {
    const map = new Map<string, SourceAgg>()

    events.forEach((event) => {
      const key = event.source.code
      if (!map.has(key)) {
        map.set(key, { ...event.source, count: 0, critical: 0 })
      }
      const item = map.get(key)!
      item.count++
      if (event.severity === "critical") {
        item.critical++
      }
    })

    return [...map.values()].sort((a, b) => b.count - a.count)
  }, [events])

  const update = (key: FilterKey, value: string) =>
    setFilters((current) => ({ ...current, [key]: value }))

  const critical = events.filter((e) => e.severity === "critical").length
  const countries = new Set(events.map((e) => e.country)).size
  const confidence = events.length
    ? Math.round(events.reduce((sum, e) => sum + e.confidence, 0) / events.length)
    : 0

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Threat intelligence"
        title="See the threat before it moves."
        description="Correlated global telemetry, adversary infrastructure, and African regional context in one operational picture."
        icon={Radar}
        actions={
          <Badge variant="outline" className="gap-2">
            <span className="size-1.5 animate-pulse rounded-full bg-primary" /> Ingesting 2,841 signals/min
          </Badge>
        }
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Signals in view" value={String(events.length)} change="12.4%" icon={RadioTower} detail="Filtered intelligence events" />
        <StatCard label="Critical signals" value={String(critical)} change="4.1%" icon={ShieldAlert} detail="Requiring immediate validation" />
        <StatCard label="Countries observed" value={String(countries)} change="3 new" icon={Globe2} detail="Active geographies in view" />
        <StatCard label="Confidence index" value={`${confidence}%`} change="1.8%" icon={Activity} detail="Weighted source confidence" />
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading">Intelligence filters</CardTitle>
          <CardDescription>Coordinate the entire workspace around the signals that matter.</CardDescription>
          <CardAction>
            <Button variant="ghost" size="sm" onClick={() => setFilters(initialFilters)}>
              <FilterX data-icon="inline-start" />
              Reset
            </Button>
          </CardAction>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <FilterSelect label="Severity" value={filters.severity} options={filterOptions.severity} onChange={(v) => update("severity", v)} />
          <FilterSelect label="Region" value={filters.region} options={filterOptions.region} onChange={(v) => update("region", v)} />
          <FilterSelect label="Industry" value={filters.industry} options={filterOptions.industry} onChange={(v) => update("industry", v)} />
          <FilterSelect label="Threat type" value={filters.type} options={filterOptions.type} onChange={(v) => update("type", v)} />
          <FilterSelect label="Technique" value={filters.technique} options={filterOptions.technique} onChange={(v) => update("technique", v)} />
          <FilterSelect label="Tactic" value={filters.tactic} options={filterOptions.tactic} onChange={(v) => update("tactic", v)} />
        </CardContent>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[1.7fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Threat activity map</CardTitle>
            <CardDescription>Click any signal to coordinate it with the live feed.</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="world">
              <TabsList>
                <TabsTrigger value="world">World view</TabsTrigger>
                <TabsTrigger value="africa">Africa focus</TabsTrigger>
              </TabsList>
              <TabsContent value="world">
                <ThreatMap events={events} selected={selected} onSelect={setSelected} />
              </TabsContent>
              <TabsContent value="africa">
                <ThreatMap events={events} focus="africa" selected={selected} onSelect={setSelected} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Live intelligence feed</CardTitle>
            <CardDescription>Prioritized by severity and confidence.</CardDescription>
            <CardAction>
              <span className="flex size-2 rounded-full bg-primary" />
            </CardAction>
          </CardHeader>
          <CardContent className="px-0">
            <LiveFeed events={events} selected={selected} onSelect={setSelected} />
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Attack timeline</CardTitle>
            <CardDescription>Severity-weighted signal volume · last 24 hours</CardDescription>
          </CardHeader>
          <CardContent>
            <ThreatTrendChart />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Threat categories</CardTitle>
            <CardDescription>Distribution for the current filtered view</CardDescription>
          </CardHeader>
          <CardContent>
            <CategoryChart events={events} />
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading">Intelligence source health</CardTitle>
          <CardDescription>Signal throughput, reliability, and collection status.</CardDescription>
          <CardAction>
            <Badge variant="outline">
              <AlertTriangle className="size-3" /> 1 elevated
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <SourcesTable sources={sources} />
        </CardContent>
      </Card>
    </div>
  )
}