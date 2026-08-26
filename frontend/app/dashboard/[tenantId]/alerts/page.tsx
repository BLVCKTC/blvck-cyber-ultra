import { SectionHeading } from '@/components/soc/shell'
import { AlertsTable } from '@/components/soc/alerts/alerts-table'

export const metadata = { title: 'Alerts — BLVCK CYBER' }

export default async function AlertsPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params

  return (
    <div className="flex flex-col gap-6">
      <SectionHeading
        title="Alerts"
        sub="Tenant-scoped triage queue sourced from the authenticated alert API."
      />
      <AlertsTable tenantId={tenantId} />
    </div>
  )
}
