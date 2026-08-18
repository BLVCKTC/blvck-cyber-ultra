"use client"

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Activity } from "lucide-react"
import { Panel } from "./panel"
import { attackTrend } from "@/lib/soc-data"

export function AttackChart() {
  return (
    <Panel title="Attack Volume — 24h" icon={<Activity className="h-4 w-4" />}>
      <div className="mb-3 flex items-center gap-4">
        <Legend color="oklch(0.62 0.23 20)" label="Detected" />
        <Legend color="oklch(0.82 0.19 150)" label="Blocked" />
        <span className="ml-auto font-mono text-xs text-muted-foreground">
          Peak <span className="text-foreground">168</span> @ 12:00
        </span>
      </div>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={attackTrend} margin={{ top: 6, right: 6, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="detGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.62 0.23 20)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="oklch(0.62 0.23 20)" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="blkGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.82 0.19 150)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="oklch(0.82 0.19 150)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              tick={{ fill: "oklch(0.66 0.02 155)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "oklch(0.66 0.02 155)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
              width={44}
            />
            <Tooltip
              contentStyle={{
                background: "oklch(0.2 0.008 165)",
                border: "1px solid oklch(0.32 0.01 160)",
                borderRadius: 8,
                fontFamily: "var(--font-mono)",
                fontSize: 12,
              }}
              labelStyle={{ color: "oklch(0.66 0.02 155)" }}
            />
            <Area
              type="monotone"
              dataKey="detected"
              stroke="oklch(0.62 0.23 20)"
              strokeWidth={2}
              fill="url(#detGrad)"
            />
            <Area
              type="monotone"
              dataKey="blocked"
              stroke="oklch(0.82 0.19 150)"
              strokeWidth={2}
              fill="url(#blkGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      <span className="font-mono text-[11px] text-muted-foreground">{label}</span>
    </div>
  )
}
