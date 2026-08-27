"use client"

import { useMemo, useState } from "react"
import useSWR from "swr"
import { Cloud, Laptop, Network, Search, Server, ShieldCheck } from "lucide-react"
import { getAssets, assetsKey, type ApiAsset } from "@/lib/api/intelligence"
import { PageHeader, Panel, Score, StatCard, StatusBadge } from "@/components/dashboard/shared/ui"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

type AssetRow = ApiAsset & {
  name: string
  type: string
  os: string
  owner: string
  vulnerabilities: number
  edr: string
  health: number
  exposure: number
  ip: string
  tags: string[]
}

function mapAsset(asset: ApiAsset): AssetRow {
  const metadata = asset.metadata_json ?? {}
  return {
    ...asset,
    name: asset.canonical_name,
    type: asset.asset_type,
    os: String(metadata.os ?? metadata.operating_system ?? "Unknown"),
    owner: String(metadata.owner ?? "Unassigned"),
    vulnerabilities: Number(metadata.vulnerabilities ?? 0),
    edr: String(metadata.edr ?? "Unknown"),
    health: Number(metadata.health ?? 0),
    exposure: Number(metadata.exposure ?? 0),
    ip: String(metadata.ip ?? "Not reported"),
    tags: Array.isArray(metadata.tags) ? metadata.tags.map(String) : [],
  }
}

export function AssetsModule() {
  const [q, setQ] = useState("")
  const [type, setType] = useState("All")
  const [selected, setSelected] = useState<AssetRow | null>(null)
  const { data, error, isLoading } = useSWR(assetsKey, getAssets)
  const assets = useMemo(() => (data ?? []).map(mapAsset), [data])
  const shown = useMemo(
    () => assets.filter((a) => (type === "All" || a.type === type) && `${a.name} ${a.owner} ${a.os} ${a.ip}`.toLowerCase().includes(q.toLowerCase())),
    [assets, q, type],
  )

  return <div className="flex flex-col gap-6">
    <PageHeader eyebrow="Attack surface management" title="Asset inventory" description="Continuously discover, classify, and prioritize endpoint, server, cloud, and SaaS exposure." actions={<Button><Network data-icon="inline-start" />Run discovery</Button>} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><StatCard label="Managed assets" value={isLoading ? "—" : String(assets.length)} change="Live" icon={Laptop} detail="Tenant inventory" /><StatCard label="Critical exposure" value={String(assets.filter((a) => a.criticality >= 4).length)} change="Live" icon={Server} detail="Criticality score 4+" /><StatCard label="EDR coverage" value="—" change="Live" icon={ShieldCheck} detail="Reported by connectors" /><StatCard label="Cloud resources" value={String(assets.filter((a) => a.type.toLowerCase() === "cloud").length)} change="Live" icon={Cloud} detail="Tenant inventory" /></div>
    <Panel title="Enterprise inventory" description={error ? "Unable to load tenant assets." : `${shown.length} assets shown`} action={<Button variant="outline" size="sm">Export CSV</Button>}>
      <div className="mb-4 flex flex-col gap-3 md:flex-row"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input className="pl-9" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search hostname, owner, IP, or OS…" /></div><div className="flex flex-wrap gap-2">{["All", "Endpoint", "Server", "Cloud", "SaaS"].map((v) => <Button key={v} size="sm" variant={type === v ? "default" : "outline"} onClick={() => setType(v)}>{v}</Button>)}</div></div>
      {isLoading ? <p className="py-10 text-center text-sm text-muted-foreground">Loading tenant assets…</p> : error ? <p className="py-10 text-center text-sm text-destructive">Asset inventory is unavailable.</p> : <div className="overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Asset</TableHead><TableHead>Type / OS</TableHead><TableHead>Criticality</TableHead><TableHead>Owner</TableHead><TableHead>Vulnerabilities</TableHead><TableHead>EDR</TableHead><TableHead>Health</TableHead><TableHead>Exposure</TableHead></TableRow></TableHeader><TableBody>{shown.map((a) => <TableRow key={a.id} className="cursor-pointer" onClick={() => setSelected(a)}><TableCell><strong className="block text-sm">{a.name}</strong><span className="font-mono text-[11px] text-muted-foreground">{a.id} · {a.ip}</span></TableCell><TableCell><span className="block text-xs">{a.type}</span><span className="text-[11px] text-muted-foreground">{a.os}</span></TableCell><TableCell><Badge variant={a.criticality >= 4 ? "destructive" : "secondary"}>{a.criticality >= 4 ? "Critical" : a.criticality >= 3 ? "High" : "Standard"}</Badge></TableCell><TableCell className="text-xs">{a.owner}</TableCell><TableCell><span className={a.vulnerabilities > 10 ? "font-mono text-destructive" : "font-mono"}>{a.vulnerabilities}</span></TableCell><TableCell><StatusBadge value={a.edr} /></TableCell><TableCell><Score value={a.health} /></TableCell><TableCell><Score value={a.exposure} label="Risk" /></TableCell></TableRow>)}</TableBody></Table></div>}
    </Panel>
    <Sheet open={!!selected} onOpenChange={(open) => !open && setSelected(null)}><SheetContent className="w-full overflow-y-auto sm:max-w-xl"><SheetHeader><SheetTitle>{selected?.name}</SheetTitle><SheetDescription>{selected?.id} · last seen {selected?.last_seen_at ?? "not reported"}</SheetDescription></SheetHeader>{selected && <div className="flex flex-col gap-5 p-4"><div className="grid grid-cols-2 gap-3"><div className="rounded-md border p-4"><Score value={selected.health} label="Health score" /></div><div className="rounded-md border p-4"><Score value={selected.exposure} label="Exposure score" /></div></div><div className="flex flex-wrap gap-2">{selected.tags.map((tag) => <Badge key={tag} variant="outline">{tag}</Badge>)}</div><Tabs defaultValue="posture"><TabsList><TabsTrigger value="posture">Posture</TabsTrigger><TabsTrigger value="vulns">Vulnerabilities</TabsTrigger><TabsTrigger value="relations">Relationships</TabsTrigger></TabsList><TabsContent value="posture" className="pt-4"><dl className="grid grid-cols-2 gap-4 text-sm"><dt className="text-muted-foreground">Network location</dt><dd className="font-mono">{selected.ip}</dd><dt className="text-muted-foreground">Operating system</dt><dd>{selected.os}</dd><dt className="text-muted-foreground">Business owner</dt><dd>{selected.owner}</dd><dt className="text-muted-foreground">EDR agent</dt><dd>{selected.edr}</dd></dl></TabsContent><TabsContent value="vulns" className="pt-4"><p className="text-sm">{selected.vulnerabilities} open findings reported for this asset.</p></TabsContent><TabsContent value="relations" className="pt-4"><div className="rounded-md border p-4 text-sm">Relationship data is provided by the tenant asset connector.</div></TabsContent></Tabs><Button>Open remediation workflow</Button></div>}</SheetContent></Sheet>
  </div>
}
