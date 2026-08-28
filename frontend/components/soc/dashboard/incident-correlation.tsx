import Link from 'next/link'
import { GitBranch } from 'lucide-react'
import { incidents } from '@/lib/soc/mock'
import { Panel } from '@/components/soc/panel'

export function IncidentCorrelation({ tenantId }: { tenantId: string }) {
  const active = incidents.filter((incident) => incident.status !== 'resolved').slice(0, 3)

  return (
    <Panel
      title="Incident correlation"
      icon={<GitBranch aria-hidden="true" />}
      action={<span className="text-xs text-muted-foreground">{active.length} correlated groups</span>}
    >
      <p className="mb-4 text-xs leading-relaxed text-muted-foreground">
        Raw alerts rolled into assigned units of work, ranked by alert volume.
      </p>
      <ul className="flex flex-col gap-3">
        {active.map((incident) => (
          <li key={incident.id} className="flex items-center gap-3 rounded-md border border-border bg-muted/30 p-3">
            <div className="flex size-9 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
              <span className="text-sm font-semibold tabular">{incident.alertCount}</span>
            </div>
            <div className="min-w-0 flex-1">
              <Link href={`/dashboard/${tenantId}/incidents/${incident.id}`} className="truncate text-sm font-medium text-foreground hover:text-primary">
                {incident.id} · {incident.title}
              </Link>
              <p className="mt-0.5 text-xs text-muted-foreground">{incident.owner ? `Assigned to ${incident.owner}` : 'Unassigned'} · {incidentStatus(incident.status)}</p>
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  )
}

function incidentStatus(status: string) {
  return status === 'investigating' ? 'Investigating' : status === 'contained' ? 'Contained' : 'Open'
}
