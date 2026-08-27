import { notFound } from 'next/navigation'

import { AlertInvestigationModule } from '@/components/soc/alerts/alert-investigation-module'
import { getAlert } from '@/lib/api/alerts'

type PageProps = {
  params: Promise<{
    tenantId: string
    alertId: string
  }>
}

export async function generateMetadata({ params }: PageProps) {
  const { alertId } = await params

  try {
    const alert = await getAlert(alertId)

    return {
      title: `${alert.id} — ${alert.title}`,
    }
  } catch {
    return {
      title: 'Alert not found',
    }
  }
}

export default async function AlertInvestigationPage({ params }: PageProps) {
  const { tenantId, alertId } = await params

  let alert

  try {
    alert = await getAlert(alertId)
  } catch {
    notFound()
  }

  if (!alert) {
    notFound()
  }

  /*
   * Keep this page intentionally thin.
   *
   * Server responsibilities:
   * - Resolve route params
   * - Load the real alert
   * - Handle not-found state
   *
   * Client responsibilities:
   * - Status changes
   * - Analyst notes
   * - Investigation UI
   * - MITRE/evidence rendering
   * - Interactive response actions
   */
  return <AlertInvestigationModule tenantId={tenantId} alert={alert} />
}
