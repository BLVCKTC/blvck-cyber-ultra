"use client"

import { useEffect, useState } from "react"
import { AlertTriangle, ShieldCheck, Bug, Brain, type LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface Stat {
  key: string
  label: string
  icon: LucideIcon
  accent: string
  format: (n: number) => string
  base: number
  drift: number
  sub: string
}

const stats: Stat[] = [
  {
    key: "threats",
    label: "Active Threats",
    icon: AlertTriangle,
    accent: "text-critical",
    format: (n) => n.toString(),
    base: 14,
    drift: 3,
    sub: "4 critical · 6 high",
  },
  {
    key: "blocked",
    label: "Attacks Blocked (24h)",
    icon: ShieldCheck,
    accent: "text-success",
    format: (n) => n.toLocaleString(),
    base: 8342,
    drift: 40,
    sub: "99.3% auto-mitigated",
  },
  {
    key: "vulns",
    label: "Open Vulnerabilities",
    icon: Bug,
    accent: "text-warning",
    format: (n) => n.toString(),
    base: 27,
    drift: 0,
    sub: "3 critical · exploit avail.",
  },
  {
    key: "ai",
    label: "AI Detection Accuracy",
    icon: Brain,
    accent: "text-info",
    format: (n) => `${n.toFixed(1)}%`,
    base: 99.2,
    drift: 0.4,
    sub: "Model v4.2 · learning",
  },
]

export function StatCards() {
  const [values, setValues] = useState(() => Object.fromEntries(stats.map((s) => [s.key, s.base])))

  useEffect(() => {
    const id = setInterval(() => {
      setValues((v) => {
        const next = { ...v }
        next.blocked = v.blocked + Math.floor(Math.random() * 6)
        next.ai = Math.min(99.9, 99.0 + Math.random() * 0.9)
        if (Math.random() > 0.6) next.threats = Math.max(8, v.threats + (Math.random() > 0.5 ? 1 : -1))
        return next
      })
    }, 3000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      {stats.map((s) => {
        const Icon = s.icon
        return (
          <div
            key={s.key}
            className="flex flex-col gap-3 rounded-lg border border-border bg-card/60 p-4 backdrop-blur-sm"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                {s.label}
              </span>
              <Icon className={cn("h-4 w-4", s.accent)} />
            </div>
            <span className={cn("font-mono text-3xl font-bold tabular-nums", s.accent)}>
              {s.format(values[s.key])}
            </span>
            <span className="text-[11px] text-muted-foreground">{s.sub}</span>
          </div>
        )
      })}
    </div>
  )
}
