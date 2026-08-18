import Link from 'next/link'
import { incidents, incidentStatusLabel } from '@/lib/soc/mock'
import { SeverityBadge, StatusChip } from '@/components/soc/primitives'

const statusTone = {
  open: 'critical',
  investigating: 'warning',
  contained: 'info',
  resolved: 'success',
} as const

export function ActiveIncidents({ tenantId }: { tenantId: string }) {
  const active = incidents
    .filter((i) => i.status !== 'resolved')
    .slice(0, 4)

  return (
    <ul className="divide-y divide-border">
      {active.map((i) => (
        <li key={i.id}>
          <Link
            href={`/dashboard/${tenantId}/incidents/${i.id}`}
            className="block px-4 py-3 transition-colors hover:bg-accent/50"
          >
            <div className="flex items-center gap-2">
              <span className="rounded bg-muted px-1.5 py-0.5 text-[11px] font-semibold text-foreground">
                {i.priority}
              </span>
              <SeverityBadge severity={i.severity} />
              <StatusChip
                label={incidentStatusLabel[i.status]}
                tone={statusTone[i.status]}
              />
              <span className="ml-auto text-xs text-muted-foreground">
                {i.updatedAt}
              </span>
            </div>
            <p className="mt-2 truncate text-sm font-medium text-foreground">
              {i.title}
            </p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {i.id} · {i.alertCount} alerts · owner {i.owner}
            </p>
          </Link>
        </li>
      ))}
    </ul>
  )
}
