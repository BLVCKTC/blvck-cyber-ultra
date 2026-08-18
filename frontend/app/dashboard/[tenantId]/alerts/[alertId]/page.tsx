import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ArrowLeft, GitBranch, Layers, ListChecks, ShieldAlert } from 'lucide-react'

import { Panel } from '@/components/soc/panel'
import {
  SeverityBadge,
  StatusChip,
  MetaItem,
} from '@/components/soc/primitives'
import { AttackChain } from '@/components/soc/alerts/attack-chain'
import {
  MitreMapping,
  EvidenceList,
} from '@/components/soc/alerts/mitre-evidence'
import { AiAnalyst } from '@/components/soc/alerts/ai-analyst'
import { getAlert, alertStatusLabel, type AlertStatus } from '@/lib/soc/mock'

const statusTone: Record<AlertStatus, Parameters<typeof StatusChip>[0]['tone']> = {
  new: 'info',
  investigating: 'warning',
  contained: 'neutral',
  resolved: 'success',
  false_positive: 'muted',
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ alertId: string }>
}) {
  const { alertId } = await params
  const alert = getAlert(alertId)
  return { title: alert ? `${alert.id} — ${alert.title}` : 'Alert not found' }
}

export default async function AlertInvestigationPage({
  params,
}: {
  params: Promise<{ tenantId: string; alertId: string }>
}) {
  const { tenantId, alertId } = await params
  const alert = getAlert(alertId)

  if (!alert) {
    notFound()
  }

  return (
    <div className="space-y-6">
      <Link
        href={`/dashboard/${tenantId}/alerts`}
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to alerts
      </Link>

      {/* Header */}
      <div className="rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={alert.severity} />
          <StatusChip
            label={alertStatusLabel[alert.status]}
            tone={statusTone[alert.status]}
          />
          <span className="text-xs text-muted-foreground">{alert.id}</span>
          {alert.relatedIncidentId && (
            <Link
              href={`/dashboard/${tenantId}/incidents/${alert.relatedIncidentId}`}
              className="ml-auto inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-xs font-medium text-foreground transition-colors hover:border-primary/50 hover:text-primary"
            >
              <ShieldAlert className="h-3.5 w-3.5" />
              {alert.relatedIncidentId}
            </Link>
          )}
        </div>
        <h1 className="mt-3 text-balance text-xl font-semibold tracking-tight text-foreground">
          {alert.title}
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
          {alert.description}
        </p>

        <div className="mt-4 grid grid-cols-2 gap-4 border-t border-border pt-4 sm:grid-cols-3 lg:grid-cols-6">
          <MetaItem label="Asset">{alert.asset}</MetaItem>
          <MetaItem label="Entity">{alert.entity}</MetaItem>
          <MetaItem label="Source">{alert.source}</MetaItem>
          <MetaItem label="Tactic">{alert.tactic}</MetaItem>
          <MetaItem label="Detected">{alert.detectedAt}</MetaItem>
          <MetaItem label="Assignee">{alert.assignee ?? 'Unassigned'}</MetaItem>
        </div>
      </div>

      {/* Body */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Panel title="Attack chain" icon={<GitBranch className="h-4 w-4" />}>
            <AttackChain steps={alert.chain} />
          </Panel>

          <Panel title="Evidence" icon={<ListChecks className="h-4 w-4" />}>
            <EvidenceList evidence={alert.evidence} />
          </Panel>
        </div>

        <div className="space-y-6">
          <AiAnalyst alert={alert} />

          <Panel title="MITRE ATT&CK" icon={<Layers className="h-4 w-4" />}>
            <MitreMapping mitre={alert.mitre} />
          </Panel>
        </div>
      </div>
    </div>
  )
}
