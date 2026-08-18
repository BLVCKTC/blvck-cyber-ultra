import type { LucideIcon } from "lucide-react"
import { ArrowDownRight, ArrowUpRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow:string; title:string; description:string; actions?:React.ReactNode }) {
  return <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between"><div className="flex flex-col gap-1"><p className="font-mono text-[10px] uppercase tracking-[.24em] text-primary">{eyebrow}</p><h1 className="text-balance text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1><p className="max-w-3xl text-pretty text-sm leading-6 text-muted-foreground">{description}</p></div>{actions && <div className="flex flex-wrap gap-2">{actions}</div>}</header>
}

export function StatCard({ label, value, change, icon:Icon, detail }: { label:string; value:string; change?:string; icon:LucideIcon; detail?:string }) {
  const down=change?.startsWith("-")
  return <Card className="overflow-hidden bg-card/80"><CardHeader className="flex flex-row items-center justify-between pb-2"><CardDescription className="text-xs uppercase tracking-wider">{label}</CardDescription><span className="rounded-md bg-primary/10 p-2 text-primary"><Icon className="size-4"/></span></CardHeader><CardContent><div className="flex items-end gap-2"><strong className="font-mono text-2xl font-semibold">{value}</strong>{change && <span className={cn("mb-1 flex items-center text-xs", down ? "text-destructive" : "text-primary")}>{down?<ArrowDownRight className="size-3"/>:<ArrowUpRight className="size-3"/>}{change}</span>}</div>{detail && <p className="mt-2 text-xs text-muted-foreground">{detail}</p>}</CardContent></Card>
}

export function Score({ value, label }: { value:number; label?:string }) { return <div className="flex min-w-28 flex-col gap-2"><div className="flex items-center justify-between text-xs"><span className="text-muted-foreground">{label ?? "Score"}</span><span className="font-mono">{value}%</span></div><Progress value={value}/></div> }

export function SeverityBadge({ value }: { value:string }) { const variant=value==="Critical"?"destructive":value==="High"?"default":"secondary"; return <Badge variant={variant}>{value}</Badge> }
export function StatusBadge({ value }: { value:string }) { return <Badge variant={value==="Open"||value==="Review"?"outline":"secondary"} className={cn(value==="Investigating"||value==="Online"||value==="Delivered"||value==="Protected"||value==="Enforced" ? "text-primary" : "")}>{value}</Badge> }

export function Panel({ title, description, action, children, className }: { title:string; description?:string; action?:React.ReactNode; children:React.ReactNode; className?:string }) { return <Card className={cn("bg-card/75",className)}><CardHeader className="flex flex-row items-start justify-between gap-3"><div><CardTitle className="text-base">{title}</CardTitle>{description&&<CardDescription className="mt-1">{description}</CardDescription>}</div>{action}</CardHeader><CardContent>{children}</CardContent></Card> }

export function MiniBars({ values }: { values:number[] }) { const max=Math.max(...values); return <div className="flex h-28 items-end gap-2" aria-label="Activity chart">{values.map((v,i)=><div key={i} className="flex-1 rounded-sm bg-primary/20 transition-colors hover:bg-primary" style={{height:`${Math.max(12,(v/max)*100)}%`}}><span className="sr-only">{v}</span></div>)}</div> }
