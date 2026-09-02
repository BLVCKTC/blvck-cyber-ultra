import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

export type Severity =
  | 'info'
  | 'low'
  | 'medium'
  | 'warning'
  | 'high'
  | 'critical'

const severityLabel: Record<Severity, string> = {
  critical: 'Critical',
  high: 'High',
  warning: 'Warning',
  medium: 'Medium',
  low: 'Low',
  info: 'Info',
}

const severityStyles: Record<Severity, string> = {
  critical: 'border-critical/40 bg-critical/10 text-critical',
  high: 'border-high/40 bg-high/10 text-high',
  warning: 'border-warning/40 bg-warning/10 text-warning',
  medium: 'border-warning/40 bg-warning/10 text-warning',
  low: 'border-info/40 bg-info/10 text-info',
  info: 'border-info/40 bg-info/10 text-info',
}

const severityDot: Record<Severity, string> = {
  critical: 'bg-critical',
  high: 'bg-high',
  warning: 'bg-warning',
  medium: 'bg-warning',
  low: 'bg-info',
  info: 'bg-info',
}

export function SeverityBadge({
  severity,
  className,
}: {
  severity: Severity
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide',
        severityStyles[severity],
        className,
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', severityDot[severity])} />

      {severityLabel[severity]}
    </span>
  )
}

export function SeverityDot({ severity }: { severity: Severity }) {
  return (
    <span
      className={cn('inline-block h-2 w-2 rounded-full', severityDot[severity])}
      aria-hidden="true"
    />
  )
}

export type Tone =
  | 'neutral'
  | 'info'
  | 'warning'
  | 'success'
  | 'critical'
  | 'muted'

const toneStyles: Record<Tone, string> = {
  neutral: 'border-primary/30 bg-primary/10 text-primary',
  info: 'border-info/30 bg-info/10 text-info',
  warning: 'border-warning/30 bg-warning/10 text-warning',
  success: 'border-success/30 bg-success/10 text-success',
  critical: 'border-critical/30 bg-critical/10 text-critical',
  muted: 'border-border bg-muted text-muted-foreground',
}

export function StatusChip({
  label,
  tone = 'muted',
  className,
}: {
  label: string
  tone?: Tone
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium',
        toneStyles[tone],
        className,
      )}
    >
      {label}
    </span>
  )
}

export function ConfidenceMeter({ value }: { value: number }) {
  const tone =
    value >= 90 ? 'bg-critical' : value >= 75 ? 'bg-high' : 'bg-warning'

  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div
          className={cn('h-full rounded-full', tone)}
          style={{
            width: `${Math.min(Math.max(value, 0), 100)}%`,
          }}
        />
      </div>

      <span className="text-xs tabular text-muted-foreground">{value}%</span>
    </div>
  )
}

export function MetaItem({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <div className="min-w-0">
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
        {label}
      </p>

      <div className="mt-0.5 truncate text-sm font-medium text-foreground">
        {children}
      </div>
    </div>
  )
}
