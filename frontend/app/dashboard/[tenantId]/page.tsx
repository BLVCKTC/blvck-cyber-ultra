import Link from 'next/link'
import { Activity, ShieldAlert, Radar, Layers } from 'lucide-react'

import { SectionHeading } from '@/components/soc/shell'
import { Panel } from '@/components/soc/panel'
import { KpiCards } from '@/components/soc/dashboard/kpi-cards'
import { AlertVolumeChart } from '@/components/soc/dashboard/alert-volume-chart'
import { PriorityQueue } from '@/components/soc/dashboard/priority-queue'
import { ActiveIncidents } from '@/components/soc/dashboard/active-incidents'
import {
  SeverityBreakdown,
  DetectionSources,
} from '@/components/soc/dashboard/posture-breakdown'

export default async function DashboardPage({
  params,
}: {
  params: Promise<{ tenantId: string }>
}) {
  const { tenantId } = await params

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Security operations"
        sub="Live posture across detection, response, and exposure for the last 24 hours."
        action={
          <div className="flex items-center gap-2 rounded-md border border-success/25 bg-success/10 px-3 py-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            <span className="text-xs font-medium text-success">
              All collectors reporting
            </span>
          </div>
        }
      />

      <KpiCards />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel
          title="Alert volume — 24h"
          icon={<Activity className="h-4 w-4" />}
          className="xl:col-span-2"
          action={
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-primary" /> Alerts
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-critical" /> Escalated
              </span>
            </div>
          }
        >
          <AlertVolumeChart />
        </Panel>

        <div className="space-y-6">
          <Panel title="Open by severity" icon={<Layers className="h-4 w-4" />}>
            <SeverityBreakdown />
          </Panel>
          <Panel title="Detections by source" icon={<Radar className="h-4 w-4" />}>
            <DetectionSources />
          </Panel>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel
          title="Priority queue"
          icon={<ShieldAlert className="h-4 w-4" />}
          className="xl:col-span-2"
          bodyClassName="p-0"
          action={
            <Link
              href={`/dashboard/${tenantId}/alerts`}
              className="text-xs font-medium text-primary hover:underline"
            >
              View all alerts
            </Link>
          }
        >
          <PriorityQueue tenantId={tenantId} />
        </Panel>

        <Panel
          title="Active incidents"
          icon={<ShieldAlert className="h-4 w-4" />}
          bodyClassName="p-0"
          action={
            <Link
              href={`/dashboard/${tenantId}/incidents`}
              className="text-xs font-medium text-primary hover:underline"
            >
              View all
            </Link>
          }
        >
          <ActiveIncidents tenantId={tenantId} />
        </Panel>
      </div>
    </div>
  )
}
