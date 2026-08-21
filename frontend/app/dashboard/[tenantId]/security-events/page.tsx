import { SectionHeading } from '@/components/soc/shell'
import { Panel } from '@/components/soc/panel'
import { SecurityEventsTable } from '@/components/soc/security-events/security-events-table'
import { Activity, AlertTriangle, Clock3, ShieldAlert } from 'lucide-react'

export const metadata = {
  title: 'Security Events — BLVCK CYBER',
}

export default async function SecurityEventsPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Security Events"
        sub="Normalized security telemetry collected across your organization's security estate."
        action={
          <div className="flex items-center gap-2 rounded-md border border-success/25 bg-success/10 px-3 py-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            <span className="text-xs font-medium text-success">
              Live telemetry
            </span>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Panel title="Total Events" icon={<Activity className="h-4 w-4" />}>
          <div className="text-3xl font-semibold">System Wide</div>
          <p className="mt-1 text-xs text-muted-foreground">
            Aggregated across all telemetry
          </p>
        </Panel>
        <Panel title="Critical" icon={<ShieldAlert className="h-4 w-4" />}>
          <div className="text-3xl font-semibold text-critical">Urgent</div>
          <p className="mt-1 text-xs text-muted-foreground">
            Immediate action required
          </p>
        </Panel>
        <Panel title="High" icon={<AlertTriangle className="h-4 w-4" />}>
          <div className="text-3xl font-semibold text-warning">Priority</div>
          <p className="mt-1 text-xs text-muted-foreground">
            High probability of impact
          </p>
        </Panel>
        <Panel title="Medium / Low" icon={<Clock3 className="h-4 w-4" />}>
          <div className="text-3xl font-semibold">Routine</div>
          <p className="mt-1 text-xs text-muted-foreground">
            Standard operational telemetry
          </p>
        </Panel>
      </div>

      <Panel title="Event Stream">
        <SecurityEventsTable tenantId={tenantId} />
      </Panel>
    </div>
  )
}
