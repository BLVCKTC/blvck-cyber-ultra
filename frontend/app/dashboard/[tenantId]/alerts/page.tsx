import { SectionHeading } from '@/components/soc/shell'
import { AlertsTable } from '@/components/soc/alerts/alerts-table'
import { alerts } from '@/lib/soc/mock'

export const metadata = { title: 'Alerts — BLVCK CYBER' }

export default async function AlertsPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params

  const open = alerts.filter(
    (a) => a.status !== 'resolved' && a.status !== 'false_positive',
  ).length
  const critical = alerts.filter((a) => a.severity === 'critical').length

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Alerts"
        sub={`${open} open · ${critical} critical · triage queue prioritized by severity and confidence.`}
      />
      <AlertsTable tenantId={tenantId} />
    </div>
  )
}
