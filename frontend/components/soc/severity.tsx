import { cn } from '@/lib/utils'
import type { Severity, ThreatStatus } from '@/lib/soc-data'
import { severityLabels } from '@/lib/soc-data'

export type SecurityEventSeverity = 'low' | 'medium' | 'high' | 'critical'

type BadgeSeverity = Severity | SecurityEventSeverity

const severityStyles: Record<BadgeSeverity, string> = {
  critical: 'border-critical/40 bg-critical/10 text-critical',
  high: 'border-high/40 bg-high/10 text-high',
  warning: 'border-warning/40 bg-warning/10 text-warning',
  info: 'border-info/40 bg-info/10 text-info',
  medium: 'border-warning/40 bg-warning/10 text-warning',
  low: 'border-info/40 bg-info/10 text-info',
}

const securityEventLabels: Record<SecurityEventSeverity, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

export function SeverityBadge({
  severity,
  className,
}: {
  severity: BadgeSeverity
  className?: string
}) {
  const label =
    severity in securityEventLabels
      ? securityEventLabels[severity as SecurityEventSeverity]
      : severityLabels[severity as Severity]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded border px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider',
        severityStyles[severity],
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  )
}

const statusStyles: Record<ThreatStatus, string> = {
  detected: 'text-critical',
  investigating: 'text-warning',
  contained: 'text-info',
  blocked: 'text-success',
}

const statusLabel: Record<ThreatStatus, string> = {
  detected: 'Detected',
  investigating: 'Investigating',
  contained: 'Contained',
  blocked: 'Blocked',
}

export function StatusPill({ status }: { status: ThreatStatus }) {
  return (
    <span
      className={cn('font-mono text-[11px] font-medium', statusStyles[status])}
    >
      {statusLabel[status]}
    </span>
  )
}

export { severityStyles }
