"use client"

import { useEffect, useState } from "react"
import { TrendingDown, TrendingUp } from "lucide-react"
import { Panel } from "./panel"

export function SecurityScore() {
  const target = 78
  const [score, setScore] = useState(0)

  useEffect(() => {
    let frame = 0
    const id = setInterval(() => {
      frame += 1
      setScore((s) => {
        const next = Math.min(target, Math.round(target * (frame / 30)))
        if (next >= target) clearInterval(id)
        return next
      })
    }, 24)
    return () => clearInterval(id)
  }, [])

  const radius = 78
  const circ = 2 * Math.PI * radius
  const dash = (score / 100) * circ

  const grade = score >= 85 ? "Strong" : score >= 70 ? "Moderate" : "At Risk"
  const gradeColor = score >= 85 ? "text-success" : score >= 70 ? "text-warning" : "text-critical"

  return (
    <Panel title="Cybersecurity Score" className="lg:row-span-1">
      <div className="flex flex-col items-center gap-4">
        <div className="relative h-48 w-48">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 180 180">
            <circle cx="90" cy="90" r={radius} fill="none" stroke="oklch(0.28 0.01 165)" strokeWidth="10" />
            <circle
              cx="90"
              cy="90"
              r={radius}
              fill="none"
              stroke="url(#scoreGrad)"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${dash} ${circ}`}
              style={{ transition: "stroke-dasharray 0.1s linear", filter: "drop-shadow(0 0 6px oklch(0.82 0.19 150 / 0.5))" }}
            />
            <defs>
              <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="oklch(0.75 0.15 195)" />
                <stop offset="100%" stopColor="oklch(0.82 0.19 150)" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-5xl font-bold text-foreground text-glow">{score}</span>
            <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">out of 100</span>
            <span className={`mt-1 font-mono text-xs font-semibold uppercase ${gradeColor}`}>{grade}</span>
          </div>
        </div>

        <div className="flex w-full items-center justify-between rounded-md border border-border bg-background/40 px-3 py-2">
          <div className="flex items-center gap-1.5 text-critical">
            <TrendingDown className="h-4 w-4" />
            <span className="font-mono text-sm font-semibold">-3</span>
            <span className="text-xs text-muted-foreground">this week</span>
          </div>
          <div className="flex items-center gap-1.5 text-success">
            <TrendingUp className="h-4 w-4" />
            <span className="font-mono text-sm font-semibold">+11</span>
            <span className="text-xs text-muted-foreground">this quarter</span>
          </div>
        </div>

        <p className="text-center text-xs leading-relaxed text-muted-foreground">
          Score dropped due to <span className="text-critical">3 unencrypted volumes</span> and a critical VPN CVE.
          Remediating both restores an estimated <span className="text-success">+9 points</span>.
        </p>
      </div>
    </Panel>
  )
}
