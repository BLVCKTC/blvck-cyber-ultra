import Link from 'next/link'
import { Activity, Bot, GitBranch, ShieldCheck, Siren } from 'lucide-react'

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
    <main className="soc-reference-dashboard">
      <header className="soc-reference-header">
        <div>
          <p className="soc-eyebrow">BLVCK CYBER</p>
          <h1>Security operations — Mining OT</h1>
          <p className="soc-subtitle">Correlated IT/OT posture across corporate systems and mine-site zones.</p>
        </div>
        <div className="soc-reporting"><span /> All edge nodes reporting</div>
      </header>

      <div className="soc-sitebar" aria-label="Site filters">
        <span>Site:</span>
        <button className="is-selected">All sites (4)</button>
        <button>Mine-07 Kalgoorlie</button>
        <button>Mine-12 Pilbara</button>
        <button>Mine-03 Sudbury</button>
        <div className="soc-legend"><span className="it" /> IT <span className="dmz" /> DMZ <span className="scada" /> SCADA <span className="control" /> Control <span className="safety" /> Safety <span className="autonomous" /> Autonomous</div>
      </div>

      <KpiCards />

      <section className="soc-summary-grid">
        <Panel title="Open by severity" icon={<Siren aria-hidden="true" />}><SeverityBreakdown /></Panel>
        <Panel title="Detections by source" icon={<Activity aria-hidden="true" />}><DetectionSources /></Panel>
        <MitreCoverage />
      </section>

      <Panel title="Alert volume" icon={<Activity aria-hidden="true" />} bodyClassName="soc-chart-body"><AlertVolumeChart /></Panel>

      <section className="soc-work-grid">
        <Panel title="Priority queue" icon={<ShieldCheck aria-hidden="true" />} className="soc-queue-panel" bodyClassName="p-0" action={<Link href={`/dashboard/${tenantId}/alerts`}>View all alerts</Link>}><PriorityQueue tenantId={tenantId} /></Panel>
        <Panel title="Incidents" icon={<GitBranch aria-hidden="true" />} bodyClassName="p-0" action={<Link href={`/dashboard/${tenantId}/incidents`}>View all</Link>}><ActiveIncidents tenantId={tenantId} /></Panel>
      </section>

      <Panel title="AI analyst workspace" icon={<Bot aria-hidden="true" />} bodyClassName="soc-ai-body" action={<Link href={`/dashboard/${tenantId}/ai-assistant`}>Open workspace</Link>}><AIAssistant /></Panel>
      <div className="soc-correlation"><IncidentCorrelation tenantId={tenantId} /></div>
    </main>
  )
}
