import { Clock3, LocateFixed, Radio } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import type { ThreatEvent } from "@/lib/threat-data"
import { cn } from "@/lib/utils"
import { SeverityBadge } from "./severity-badge"

export function LiveFeed({ events, selected, onSelect }: { events: ThreatEvent[]; selected?: string; onSelect: (id: string) => void }) {
  return <ScrollArea className="h-[380px]"><div className="flex flex-col">{events.length === 0 ? <div className="flex h-72 flex-col items-center justify-center gap-3 text-center"><Radio className="size-6 text-muted-foreground" /><p className="text-sm font-medium">No matching signals</p><p className="text-xs text-muted-foreground">Adjust filters to expand the feed.</p></div> : events.map((e,i)=><div key={e.id}>{i>0&&<Separator/>}<button onClick={()=>onSelect(e.id)} className={cn("w-full p-3 text-left transition-colors hover:bg-muted/60", selected===e.id&&"bg-primary/10")}><div className="mb-2 flex items-center justify-between gap-2"><SeverityBadge severity={e.severity}/><span className="flex items-center gap-1 font-mono text-[10px] text-muted-foreground"><Clock3 className="size-3" />{e.time}</span></div><p className="text-sm font-medium leading-snug">{e.title}</p><p className="mt-1 text-xs text-muted-foreground">{e.actor} · {e.technique}</p><div className="mt-2 flex items-center justify-between text-[10px] uppercase tracking-wider text-muted-foreground"><span className="flex items-center gap-1"><LocateFixed className="size-3" />{e.country}</span><span>{e.confidence}% confidence</span></div></button></div>)}</div></ScrollArea>
}
