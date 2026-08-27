import { SectionHeading } from '@/components/soc/shell'
import { IncidentsTable } from '@/components/soc/incidents/incidents-table'
import type { IncidentSeverity } from '@/lib/api/incidents'

export const metadata = { title: 'Incidents — BLVCK CYBER' }

const severities: IncidentSeverity[] = ['critical', 'high', 'medium', 'low']

export default async function IncidentsPage({
  params,
  searchParams,
}: {
  params: Promise<{ tenantId: string }>
  searchParams: Promise<{ severity?: string }>
}) {
  const { tenantId } = await params
  const { severity } = await searchParams

  const initialSeverity =
    severity && severities.includes(severity as IncidentSeverity)
      ? (severity as IncidentSeverity)
      : 'all'

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Incidents"
        sub="Tenant-scoped response workspace linking alerts, evidence, and containment actions."
      />
      <IncidentsTable tenantId={tenantId} initialSeverity={initialSeverity} />
    </div>
  )
}
