"use client"

import { Globe2, Building2 } from "lucide-react"
import { Panel } from "./panel"
import { cn } from "@/lib/utils"

const regions = [
  { country: "Nigeria", level: "critical", incidents: 4821, top: "Banking Fraud / BEC" },
  { country: "South Africa", level: "critical", incidents: 3944, top: "Ransomware" },
  { country: "Kenya", level: "high", incidents: 2610, top: "Mobile Money Fraud" },
  { country: "Egypt", level: "high", incidents: 2188, top: "Phishing" },
  { country: "Ghana", level: "warning", incidents: 1402, top: "Credential Theft" },
  { country: "Morocco", level: "warning", incidents: 1187, top: "DDoS" },
  { country: "Tanzania", level: "info", incidents: 742, top: "Malware" },
]

const industries = [
  { name: "Banking & Fintech", pct: 34 },
  { name: "Government", pct: 24 },
  { name: "Telecommunications", pct: 18 },
  { name: "Healthcare", pct: 14 },
  { name: "Education", pct: 10 },
]

const levelDot = {
  critical: "bg-critical",
  high: "bg-high",
  warning: "bg-warning",
  info: "bg-info",
}

export function ThreatIntel() {
  return (
    <Panel title="African Cyber Intelligence Network" icon={<Globe2 className="h-4 w-4" />}>
      <div className="grid gap-5 lg:grid-cols-2">
        <div>
          <p className="mb-3 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            Regional Threat Activity · 24h
          </p>
          <div className="space-y-1">
            {regions.map((r) => (
              <div
                key={r.country}
                className="flex items-center gap-3 rounded-md px-2 py-2 hover:bg-accent/40"
              >
                <span className={cn("h-2 w-2 shrink-0 rounded-full", levelDot[r.level as keyof typeof levelDot])} />
                <div className="min-w-0 flex-1">
                  <span className="text-sm font-medium text-foreground">{r.country}</span>
                  <span className="block font-mono text-[10px] text-muted-foreground">{r.top}</span>
                </div>
                <span className="font-mono text-sm font-semibold tabular-nums text-foreground">
                  {r.incidents.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-3 flex items-center gap-1.5">
            <Building2 className="h-3.5 w-3.5 text-primary" />
            <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              Attacks by Sector
            </span>
          </div>
          <div className="space-y-3">
            {industries.map((ind) => (
              <div key={ind.name}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-foreground">{ind.name}</span>
                  <span className="font-mono text-muted-foreground">{ind.pct}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-secondary">
                  <div className="h-full rounded-full bg-primary/80" style={{ width: `${ind.pct * 2.5}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-md border border-info/30 bg-info/5 p-3">
            <p className="font-mono text-[10px] uppercase tracking-wider text-info">Shared Intelligence</p>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Anonymized indicators from <span className="text-foreground">2,400+</span> member organizations
              strengthen detection models across the network.
            </p>
          </div>
        </div>
      </div>
    </Panel>
  )
}
