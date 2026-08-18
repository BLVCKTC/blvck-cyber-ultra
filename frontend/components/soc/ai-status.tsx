"use client"

import { useEffect, useState } from "react"
import { Brain, TrendingUp } from "lucide-react"
import { Panel } from "./panel"

const risks = [
  { label: "Ransomware campaign", pct: 68, level: "high" },
  { label: "Credential phishing wave", pct: 54, level: "high" },
  { label: "DDoS on payment API", pct: 32, level: "warning" },
  { label: "Insider data misuse", pct: 19, level: "info" },
]

const levelColor: Record<string, string> = {
  high: "bg-high",
  warning: "bg-warning",
  info: "bg-info",
}

export function AIStatus() {
  const [patterns, setPatterns] = useState(1_284_902)

  useEffect(() => {
    const id = setInterval(() => setPatterns((p) => p + Math.floor(Math.random() * 40)), 2000)
    return () => clearInterval(id)
  }, [])

  return (
    <Panel title="AI Engine & Risk Prediction" icon={<Brain className="h-4 w-4" />}>
      <div className="space-y-4">
        <div className="rounded-md border border-primary/30 bg-primary/5 p-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              Detection Model
            </span>
            <span className="flex items-center gap-1.5 font-mono text-[11px] text-success">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-success" />
              Learning
            </span>
          </div>
          <p className="mt-1 font-mono text-sm font-bold text-foreground">Neural Threat Engine v4.2</p>
          <p className="font-mono text-xs text-muted-foreground">
            {patterns.toLocaleString()} patterns analyzed
          </p>
        </div>

        <div>
          <div className="mb-2 flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-primary" />
            <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              7-Day Threat Forecast
            </span>
          </div>
          <div className="space-y-2.5">
            {risks.map((r) => (
              <div key={r.label}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-foreground">{r.label}</span>
                  <span className="font-mono text-muted-foreground">{r.pct}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                  <div
                    className={`h-full rounded-full ${levelColor[r.level]}`}
                    style={{ width: `${r.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Panel>
  )
}
