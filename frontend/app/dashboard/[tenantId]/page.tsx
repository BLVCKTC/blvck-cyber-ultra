import Link from 'next/link'
import { Activity, Bot, Crosshair, Flame, Layers, Radar, ShieldAlert, ArrowUpRight } from 'lucide-react'

import { SectionHeading } from '@/components/soc/shell'
import { Panel } from '@/components/soc/panel'
import { KpiCards } from '@/components/soc/dashboard/kpi-cards'
import { AlertVolumeChart } from '@/components/soc/dashboard/alert-volume-chart'
import { PriorityQueue } from '@/components/soc/dashboard/priority-queue'
import { ActiveIncidents } from '@/components/soc/dashboard/active-incidents'
import { IncidentCorrelation } from '@/components/soc/dashboard/incident-correlation'
import { MitreCoverage } from '@/components/soc/dashboard/mitre-coverage'
import { AIAssistant } from '@/components/soc/ai-assistant'
import { SeverityBreakdown, DetectionSources } from '@/components/soc/dashboard/posture-breakdown'

export default async function DashboardPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params

  return (
    <div className="space-y-6">
      <SectionHeading
        title="Security operations"
        sub="Live posture across detection, response, and exposure for the last 24 hours."
        action={
          <div className="flex flex-wrap items-center gap-2">
            <Link href={`/dashboard/${tenantId}/ai-assistant`} className="group inline-flex items-center gap-2 rounded-md border border-primary/30 bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/15">
              <Bot aria-hidden="true" /> Ask AI analyst <ArrowUpRight aria-hidden="true" />
            </Link>
            <div className="flex items-center gap-2 rounded-md border border-success/25 bg-success/10 px-3 py-1.5 text-xs font-medium text-success"><span className="size-1.5 rounded-full bg-success" /> All collectors reporting</div>
          </div>
        }
      />

      <KpiCards />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel title="Alert volume" icon={<Activity aria-hidden="true" />} className="xl:col-span-2" bodyClassName="pt-3"><AlertVolumeChart /></Panel>
        <Panel title="Open by severity" icon={<Layers aria-hidden="true" />}><SeverityBreakdown /></Panel>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel title="Detections by source" icon={<Radar aria-hidden="true" />}><DetectionSources /></Panel>
        <div className="xl:col-span-2"><MitreCoverage /></div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel title="Priority queue" icon={<ShieldAlert aria-hidden="true" />} className="xl:col-span-2" bodyClassName="p-0" action={<Link href={`/dashboard/${tenantId}/alerts`} className="text-xs font-medium text-primary hover:underline">View all alerts</Link>}><PriorityQueue tenantId={tenantId} /></Panel>
        <Panel title="Active incidents" icon={<Flame aria-hidden="true" />} bodyClassName="p-0" action={<Link href={`/dashboard/${tenantId}/incidents`} className="text-xs font-medium text-primary hover:underline">View all</Link>}><ActiveIncidents tenantId={tenantId} /></Panel>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2"><Panel title="AI analyst workspace" icon={<Bot aria-hidden="true" />} bodyClassName="p-0" action={<Link href={`/dashboard/${tenantId}/ai-assistant`} className="text-xs font-medium text-primary hover:underline">Open full workspace</Link>}><AIAssistant /></Panel></div>
        <IncidentCorrelation tenantId={tenantId} />
      </div>
    </div>
  )
}
