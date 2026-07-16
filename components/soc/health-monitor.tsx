import { HeartPulse, Server, Database, Wifi, MonitorSmartphone, Timer, ShieldAlert } from "lucide-react"
import { Panel } from "./panel"
import { healthMetrics } from "@/lib/soc-data"
import { cn } from "@/lib/utils"

const icons = [Server, Database, Wifi, MonitorSmartphone, Timer, ShieldAlert]

const statusColor = {
  healthy: "text-success",
  degraded: "text-warning",
  critical: "text-critical",
}
const barColor = {
  healthy: "bg-success",
  degraded: "bg-warning",
  critical: "bg-critical",
}

export function HealthMonitor() {
  return (
    <Panel title="Technology Health Monitoring" icon={<HeartPulse className="h-4 w-4" />}>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {healthMetrics.map((m, i) => {
          const Icon = icons[i % icons.length]
          return (
            <div key={m.label} className="rounded-md border border-border bg-background/40 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className={cn("h-4 w-4", statusColor[m.status])} />
                  <span className="text-xs font-medium text-foreground">{m.label}</span>
                </div>
                <span className={cn("font-mono text-sm font-bold", statusColor[m.status])}>
                  {m.value}
                  {m.label.includes("Uptime") ? "%" : ""}
                </span>
              </div>
              <div className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-secondary">
                <div className={cn("h-full rounded-full", barColor[m.status])} style={{ width: `${m.value}%` }} />
              </div>
              <p className="mt-2 font-mono text-[10px] text-muted-foreground">{m.detail}</p>
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
