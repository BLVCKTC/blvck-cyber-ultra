import { cn } from "@/lib/utils"
import type { Severity, ThreatStatus } from "@/lib/soc-data"
import { severityLabels } from "@/lib/soc-data"

const severityStyles: Record<Severity, string> = {
  critical: "border-critical/40 bg-critical/10 text-critical",
  high: "border-high/40 bg-high/10 text-high",
  warning: "border-warning/40 bg-warning/10 text-warning",
  info: "border-info/40 bg-info/10 text-info",
}

export function SeverityBadge({ severity, className }: { severity: Severity; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded border px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider",
        severityStyles[severity],
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {severityLabels[severity]}
    </span>
  )
}

const statusStyles: Record<ThreatStatus, string> = {
  detected: "text-critical",
  investigating: "text-warning",
  contained: "text-info",
  blocked: "text-success",
}

const statusLabel: Record<ThreatStatus, string> = {
  detected: "Detected",
  investigating: "Investigating",
  contained: "Contained",
  blocked: "Blocked",
}

export function StatusPill({ status }: { status: ThreatStatus }) {
  return (
    <span className={cn("font-mono text-[11px] font-medium", statusStyles[status])}>
      {statusLabel[status]}
    </span>
  )
}

export { severityStyles }
