import { SectionHeading } from '@/components/soc/shell'
import { IncidentsTable } from '@/components/soc/incidents/incidents-table'
import { incidents, type Severity } from '@/lib/soc/mock'

export const metadata = { title: 'Incidents — BLVCK CYBER' }

const severities: Severity[] = ['critical', 'high', 'warning', 'info']

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
    severity && severities.includes(severity as Severity)
      ? (severity as Severity)
      : 'all'

  const open = incidents.filter((i) => i.status !== 'resolved').length
  const p1 = incidents.filter((i) => i.priority === 'P1').length

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Incidents"
        sub={`${open} active · ${p1} P1 · consolidated response workspace linking alerts, evidence, and containment actions.`}
      />
      <IncidentsTable tenantId={tenantId} initialSeverity={initialSeverity} />
    </div>
  )
}
