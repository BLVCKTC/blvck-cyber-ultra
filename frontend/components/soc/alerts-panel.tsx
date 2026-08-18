import { Bell } from "lucide-react"
import { Panel } from "./panel"
import { alerts } from "@/lib/soc-data"
import { cn } from "@/lib/utils"

const dot = {
  critical: "bg-critical",
  high: "bg-high",
  warning: "bg-warning",
  info: "bg-info",
}

export function AlertsPanel() {
  return (
    <Panel
      title="Notifications"
      icon={<Bell className="h-4 w-4" />}
      bodyClassName="p-0"
      action={
        <span className="rounded bg-critical/15 px-2 py-0.5 font-mono text-[10px] font-semibold text-critical">
          5 NEW
        </span>
      }
    >
      <div className="divide-y divide-border/50">
        {alerts.map((a) => (
          <div key={a.id} className="flex items-start gap-3 px-4 py-3 hover:bg-accent/40">
            <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", dot[a.severity])} />
            <div className="min-w-0">
              <p className="text-xs leading-relaxed text-foreground">{a.message}</p>
              <span className="font-mono text-[10px] text-muted-foreground">{a.time}</span>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
