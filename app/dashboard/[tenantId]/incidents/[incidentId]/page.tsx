import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'

import {
  SeverityBadge,
  StatusChip,
  MetaItem,
} from '@/components/soc/primitives'
import { IncidentWorkspace } from '@/components/soc/incidents/incident-workspace'
import {
  getIncident,
  getIncidentAlerts,
  incidentStatusLabel,
  type IncidentStatus,
} from '@/lib/soc/mock'

const statusTone: Record<
  IncidentStatus,
  Parameters<typeof StatusChip>[0]['tone']
> = {
  open: 'critical',
  investigating: 'warning',
  contained: 'info',
  resolved: 'success',
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ incidentId: string }>
}) {
  const { incidentId } = await params
  const incident = getIncident(incidentId)
  return {
    title: incident
      ? `${incident.id} — ${incident.title}`
      : 'Incident not found',
  }
}

export default async function IncidentPage({
  params,
}: {
  params: Promise<{ tenantId: string; incidentId: string }>
}) {
  const { tenantId, incidentId } = await params
  const incident = getIncident(incidentId)

  if (!incident) {
    notFound()
  }

  const relatedAlerts = getIncidentAlerts(incident.id)

  return (
    <div className="space-y-6">
      <Link
        href={`/dashboard/${tenantId}/incidents`}
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to incidents
      </Link>

      <div className="rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-muted px-2 py-0.5 text-xs font-semibold text-foreground">
            {incident.priority}
          </span>
          <SeverityBadge severity={incident.severity} />
          <StatusChip
            label={incidentStatusLabel[incident.status]}
            tone={statusTone[incident.status]}
          />
          <span className="text-xs text-muted-foreground">{incident.id}</span>
        </div>
        <h1 className="mt-3 text-balance text-xl font-semibold tracking-tight text-foreground">
          {incident.title}
        </h1>

        <div className="mt-4 grid grid-cols-2 gap-4 border-t border-border pt-4 sm:grid-cols-3 lg:grid-cols-5">
          <MetaItem label="Owner">{incident.owner}</MetaItem>
          <MetaItem label="Opened">{incident.openedAt}</MetaItem>
          <MetaItem label="Last update">{incident.updatedAt}</MetaItem>
          <MetaItem label="Linked alerts">{incident.alertCount}</MetaItem>
          <MetaItem label="Assets">{incident.assets.length}</MetaItem>
        </div>
      </div>

      <IncidentWorkspace
        incident={incident}
        relatedAlerts={relatedAlerts}
        tenantId={tenantId}
      />
    </div>
  )
}
