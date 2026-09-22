import Link from 'next/link'
import { Activity, Bot, Flame, GitBranch, ShieldAlert } from 'lucide-react'

import { Panel } from '@/components/soc/panel'
import { KpiCards } from '@/components/soc/dashboard/kpi-cards'
import { AlertVolumeChart } from '@/components/soc/dashboard/alert-volume-chart'
import { PriorityQueue } from '@/components/soc/dashboard/priority-queue'
import { ActiveIncidents } from '@/components/soc/dashboard/active-incidents'
import { IncidentCorrelation } from '@/components/soc/dashboard/incident-correlation'
import { MitreCoverage } from '@/components/soc/dashboard/mitre-coverage'
import { AIAssistant } from '@/components/soc/ai-assistant'
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
    <main className="soc-reference-dashboard">
      <header className="soc-reference-header">
        <div>
          <p className="soc-eyebrow">BLVCK CYBER</p>

          <h1>Security operations — Mining OT</h1>

          <p className="soc-subtitle">
            Correlated IT/OT posture across corporate systems and mine-site
            zones.
          </p>
        </div>

        <div className="soc-reporting" aria-label="System reporting status">
          <span aria-hidden="true" />
          All edge nodes reporting
        </div>
      </header>

      <nav className="soc-sitebar" aria-label="Site filters">
        <span className="soc-sitebar-label">Site:</span>

        <button type="button" className="is-selected" aria-pressed="true">
          All sites (4)
        </button>

        <button type="button" aria-pressed="false">
          Mine-07 Kalgoorlie
        </button>

        <button type="button" aria-pressed="false">
          Mine-12 Pilbara
        </button>

        <button type="button" aria-pressed="false">
          Mine-03 Sudbury
        </button>

        <div className="soc-legend" aria-label="Network zones">
          <span className="it" aria-hidden="true" />
          IT
          <span className="dmz" aria-hidden="true" />
          DMZ
          <span className="scada" aria-hidden="true" />
          SCADA
          <span className="control" aria-hidden="true" />
          Control
          <span className="safety" aria-hidden="true" />
          Safety
          <span className="autonomous" aria-hidden="true" />
          Autonomous
        </div>
      </nav>

      {/* Four cards:
          Open alerts
          Active incidents
          MITRE coverage
          Mean time to triage
      */}
      <KpiCards tenantId={tenantId} />

      {/* Donut trio */}
      <section
        className="soc-donut-grid"
        aria-label="Security posture breakdown"
      >
        <Panel title="Severity mix" icon={<ShieldAlert aria-hidden="true" />}>
          <SeverityBreakdown tenantId={tenantId} window="24h" />
        </Panel>

        <Panel
          title="Detections by source"
          icon={<Activity aria-hidden="true" />}
        >
          <DetectionSources tenantId={tenantId} window="24h" />
        </Panel>

        <Panel
          title="MITRE coverage"
          icon={<GitBranch aria-hidden="true" />}
          action={
            <Link href={`/dashboard/${tenantId}/mitre`}>View coverage</Link>
          }
        >
          <MitreCoverage tenantId={tenantId} />
        </Panel>
      </section>

      {/* The chart defaults to daily and owns the range tab interaction */}
      <Panel
        title="Alert volume"
        icon={<Activity aria-hidden="true" />}
        bodyClassName="soc-chart-body"
      >
        <AlertVolumeChart tenantId={tenantId} defaultRange="daily" />
      </Panel>

      {/* Alerts and incidents remain separate because they represent
          different investigation objects. */}
      <section className="soc-work-grid">
        <Panel
          title="Priority queue"
          icon={<ShieldAlert aria-hidden="true" />}
          className="soc-queue-panel"
          bodyClassName="p-0"
          action={
            <Link href={`/dashboard/${tenantId}/alerts`}>View all alerts</Link>
          }
        >
          <PriorityQueue tenantId={tenantId} limit={4} />
        </Panel>

        <Panel
          title="Active incidents"
          icon={<Flame aria-hidden="true" />}
          bodyClassName="p-0"
          action={
            <Link href={`/dashboard/${tenantId}/incidents`}>
              View all incidents
            </Link>
          }
        >
          <ActiveIncidents tenantId={tenantId} limit={3} />
        </Panel>
      </section>

      <Panel
        title="AI analyst workspace"
        icon={<Bot aria-hidden="true" />}
        bodyClassName="soc-ai-body"
        action={
          <Link href={`/dashboard/${tenantId}/ai-assistant`}>
            Open workspace
          </Link>
        }
      >
        <AIAssistant
          tenantId={tenantId}
          suggestedPrompts={[
            'Summarize the current active incidents and suggest next steps',
            'Which MITRE techniques have the weakest detection coverage right now?',
            'Explain the top priority alert and the affected asset',
          ]}
        />
      </Panel>

      <div className="soc-correlation">
        <IncidentCorrelation tenantId={tenantId} />
      </div>
    </main>
  )
}
