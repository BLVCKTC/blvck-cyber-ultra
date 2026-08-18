"use client"

import { useEffect, useState } from "react"
import { Bug, ScanLine, ShieldAlert } from "lucide-react"
import { Panel } from "./panel"
import { SeverityBadge } from "./severity"
import { vulnerabilities } from "@/lib/soc-data"
import { cn } from "@/lib/utils"

const statusStyle = {
  open: "text-critical",
  "in-progress": "text-warning",
  remediated: "text-success",
}
const statusLabel = {
  open: "Open",
  "in-progress": "Remediating",
  remediated: "Remediated",
}

export function Vulnerabilities() {
  const [scanning, setScanning] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!scanning) return
    setProgress(0)
    const id = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(id)
          setScanning(false)
          return 100
        }
        return p + Math.floor(Math.random() * 8) + 2
      })
    }, 220)
    return () => clearInterval(id)
  }, [scanning])

  return (
    <Panel
      title="Security Testing Center"
      icon={<Bug className="h-4 w-4" />}
      bodyClassName="p-0"
      action={
        <button
          onClick={() => setScanning(true)}
          disabled={scanning}
          className="flex items-center gap-1.5 rounded border border-primary/40 bg-primary/10 px-2.5 py-1 font-mono text-[10px] font-medium uppercase tracking-wider text-primary hover:bg-primary/20 disabled:opacity-60"
        >
          <ScanLine className={cn("h-3.5 w-3.5", scanning && "animate-pulse")} />
          {scanning ? "Scanning…" : "Run Scan"}
        </button>
      }
    >
      {scanning && (
        <div className="border-b border-border px-4 py-3">
          <div className="mb-1.5 flex items-center justify-between font-mono text-[11px] text-muted-foreground">
            <span>Penetration test in progress · core-banking-db-01</span>
            <span className="text-primary">{Math.min(100, progress)}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${Math.min(100, progress)}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-px border-b border-border bg-border">
        <Stat label="Assets Scanned" value="1,204" />
        <Stat label="Open Findings" value="27" accent="text-critical" />
        <Stat label="Remediated (30d)" value="142" accent="text-success" />
      </div>

      <div className="max-h-[300px] overflow-y-auto">
        {vulnerabilities.map((v) => (
          <div
            key={v.id}
            className="flex items-center gap-3 border-b border-border/50 px-4 py-3 hover:bg-accent/40"
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="truncate text-sm font-medium text-foreground">{v.title}</span>
                {v.exploitAvailable && (
                  <span className="flex shrink-0 items-center gap-1 rounded bg-critical/10 px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase text-critical">
                    <ShieldAlert className="h-3 w-3" /> Exploit
                  </span>
                )}
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">
                {v.cve} · {v.asset} · {v.discovered}
              </span>
            </div>
            <div className="hidden text-right sm:block">
              <span className="font-mono text-sm font-bold text-foreground">{v.cvss}</span>
              <span className="block font-mono text-[9px] uppercase text-muted-foreground">CVSS</span>
            </div>
            <SeverityBadge severity={v.severity} />
            <span className={cn("hidden w-24 text-right font-mono text-[11px] font-medium md:block", statusStyle[v.status])}>
              {statusLabel[v.status]}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  )
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="bg-card px-4 py-3">
      <p className={cn("font-mono text-xl font-bold", accent ?? "text-foreground")}>{value}</p>
      <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
    </div>
  )
}
