import { severityBreakdown, detectionSources, severityLabel } from '@/lib/soc/mock'
import { cn } from '@/lib/utils'

const severityBar: Record<string, string> = {
  critical: 'bg-critical',
  high: 'bg-high',
  warning: 'bg-warning',
  info: 'bg-info',
}

export function SeverityBreakdown() {
  const total = severityBreakdown.reduce((s, x) => s + x.count, 0)
  return (
    <div className="space-y-3">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-muted">
        {severityBreakdown.map((s) => (
          <div
            key={s.severity}
            className={cn('h-full', severityBar[s.severity])}
            style={{ width: `${(s.count / total) * 100}%` }}
          />
        ))}
      </div>
      <ul className="grid grid-cols-2 gap-x-4 gap-y-2">
        {severityBreakdown.map((s) => (
          <li key={s.severity} className="flex items-center gap-2 text-sm">
            <span className={cn('h-2 w-2 rounded-full', severityBar[s.severity])} />
            <span className="text-muted-foreground">{severityLabel[s.severity]}</span>
            <span className="ml-auto tabular font-medium text-foreground">
              {s.count}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function DetectionSources() {
  const max = Math.max(...detectionSources.map((d) => d.value))
  return (
    <ul className="space-y-3">
      {detectionSources.map((d) => (
        <li key={d.name}>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{d.name}</span>
            <span className="tabular font-medium text-foreground">{d.value}</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: `${(d.value / max) * 100}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  )
}
