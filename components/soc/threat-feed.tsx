"use client"

import { Fragment, useEffect, useRef, useState } from "react"
import { Radar, Pause, Play } from "lucide-react"
import { Panel } from "./panel"
import { SeverityBadge, StatusPill } from "./severity"
import { makeThreat, seedThreats, type Threat } from "@/lib/soc-data"
import { cn } from "@/lib/utils"

function timeAgo(ts: number) {
  const s = Math.floor((Date.now() - ts) / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  return `${Math.floor(m / 60)}h ago`
}

export function ThreatFeed() {
  // Seed after mount so SSR/client markup match (Math.random must not run during render).
  const [threats, setThreats] = useState<Threat[]>([])
  const [paused, setPaused] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const pausedRef = useRef(paused)
  pausedRef.current = paused

  useEffect(() => {
    setThreats(seedThreats(8))
    const id = setInterval(() => {
      if (pausedRef.current) return
      setThreats((prev) => [makeThreat(), ...prev].slice(0, 24))
    }, 4200)
    return () => clearInterval(id)
  }, [])

  // re-render for relative timestamps
  const [, force] = useState(0)
  useEffect(() => {
    const id = setInterval(() => force((n) => n + 1), 5000)
    return () => clearInterval(id)
  }, [])

  return (
    <Panel
      title="Threat Center — Live Feed"
      icon={<Radar className="h-4 w-4 animate-pulse" />}
      className="min-h-0"
      bodyClassName="p-0"
      action={
        <button
          onClick={() => setPaused((p) => !p)}
          className="flex items-center gap-1.5 rounded border border-border px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground"
        >
          {paused ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
          {paused ? "Resume" : "Pause"}
        </button>
      }
    >
      <div className="max-h-[420px] overflow-y-auto">
        <table className="w-full border-collapse text-left">
          <thead className="sticky top-0 z-10 bg-card/95 backdrop-blur">
            <tr className="border-b border-border font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-2 font-medium">Threat</th>
              <th className="hidden px-2 py-2 font-medium sm:table-cell">Source</th>
              <th className="hidden px-2 py-2 font-medium md:table-cell">Target</th>
              <th className="px-2 py-2 font-medium">Severity</th>
              <th className="hidden px-2 py-2 font-medium lg:table-cell">Status</th>
              <th className="px-4 py-2 text-right font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {threats.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center font-mono text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-2">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
                    Initializing live threat feed…
                  </span>
                </td>
              </tr>
            )}
            {threats.map((t, i) => (
              <Fragment key={t.id}>
                <tr
                  onClick={() => setSelected(selected === t.id ? null : t.id)}
                  className={cn(
                    "cursor-pointer border-b border-border/50 text-sm transition-colors hover:bg-accent/40",
                    i === 0 && !paused && "animate-flash-in",
                    selected === t.id && "bg-accent/40",
                  )}
                >
                  <td className="px-4 py-2.5">
                    <div className="flex flex-col">
                      <span className="font-medium text-foreground">{t.type}</span>
                      <span className="font-mono text-[10px] text-muted-foreground">
                        {t.id} · {t.mitre}
                      </span>
                    </div>
                  </td>
                  <td className="hidden px-2 py-2.5 sm:table-cell">
                    <span className="font-mono text-xs text-foreground">{t.sourceIp}</span>
                    <span className="block text-[10px] text-muted-foreground">{t.sourceCountry}</span>
                  </td>
                  <td className="hidden px-2 py-2.5 font-mono text-xs text-muted-foreground md:table-cell">
                    {t.target}
                  </td>
                  <td className="px-2 py-2.5">
                    <SeverityBadge severity={t.severity} />
                  </td>
                  <td className="hidden px-2 py-2.5 lg:table-cell">
                    <StatusPill status={t.status} />
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono text-[11px] text-muted-foreground">
                    {timeAgo(t.timestamp)}
                  </td>
                </tr>
                {selected === t.id && (
                  <tr className="border-b border-border/50 bg-background/60">
                    <td colSpan={6} className="px-4 py-3">
                      <div className="grid gap-3 text-xs sm:grid-cols-2 lg:grid-cols-4">
                        <Detail label="AI Confidence" value={`${t.aiConfidence}%`} accent />
                        <Detail label="MITRE ATT&CK" value={t.mitre} />
                        <Detail label="Source Country" value={t.sourceCountry} />
                        <Detail label="Target Asset" value={t.target} />
                        <div className="sm:col-span-2 lg:col-span-4">
                          <p className="text-muted-foreground">{t.description}</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            <ActionBtn>Isolate Asset</ActionBtn>
                            <ActionBtn>Block Source IP</ActionBtn>
                            <ActionBtn>Escalate to Tier 3</ActionBtn>
                            <ActionBtn>Ask AI Analyst</ActionBtn>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  )
}

function Detail({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className={cn("font-mono text-sm font-semibold", accent ? "text-primary" : "text-foreground")}>{value}</p>
    </div>
  )
}

function ActionBtn({ children }: { children: React.ReactNode }) {
  return (
    <button className="rounded border border-primary/40 bg-primary/10 px-2.5 py-1 font-mono text-[11px] font-medium text-primary transition-colors hover:bg-primary/20">
      {children}
    </button>
  )
}
