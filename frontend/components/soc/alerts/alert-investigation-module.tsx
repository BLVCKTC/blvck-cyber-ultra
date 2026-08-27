'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import {
  ArrowLeft,
  CheckCheck,
  CircleAlert,
  GitBranch,
  Layers,
  ListChecks,
  Save,
  ShieldAlert,
} from 'lucide-react'
import { toast } from 'sonner'

import { Panel } from '@/components/soc/panel'
import {
  MetaItem,
  SeverityBadge,
  StatusChip,
} from '@/components/soc/primitives'
import { AttackChain } from '@/components/soc/alerts/attack-chain'
import {
  EvidenceList,
  MitreMapping,
} from '@/components/soc/alerts/mitre-evidence'
import { AiAnalyst } from '@/components/soc/alerts/ai-analyst'
import { updateAlert, type Alert, type AlertStatus } from '@/lib/api/alerts'

type Props = {
  tenantId: string
  alert: Alert
}

const statusTone: Record<
  AlertStatus,
  Parameters<typeof StatusChip>[0]['tone']
> = {
  new: 'info',
  open: 'warning',
  acknowledged: 'warning',
  investigating: 'warning',
  resolved: 'success',
  suppressed: 'muted',
  false_positive: 'muted',
}

function formatDate(value: string | null | undefined) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('en', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function statusLabel(status: AlertStatus) {
  return status.replace(/_/g, ' ')
}

export function AlertInvestigationModule({
  tenantId,
  alert: initialAlert,
}: Props) {
  const [alert, setAlert] = useState(initialAlert)
  const [isUpdating, setIsUpdating] = useState(false)
  const [note, setNote] = useState('')

  const metadata = useMemo(() => {
    return alert.metadata_json ?? {}
  }, [alert.metadata_json])

  const metadataString = (key: string) => {
    const value = metadata[key]

    if (typeof value === 'string' || typeof value === 'number') {
      return String(value)
    }

    return undefined
  }

  const asset =
    metadataString('asset') ??
    metadataString('asset_name') ??
    metadataString('hostname') ??
    '—'

  const entity =
    metadataString('entity') ??
    metadataString('user') ??
    metadataString('username') ??
    metadataString('ip_address') ??
    '—'

  const tactic =
    metadataString('tactic') ?? metadataString('mitre_tactic') ?? '—'

  const assignee =
    metadataString('assignee') ?? metadataString('assigned_to') ?? 'Unassigned'

  const relatedIncidentId =
    metadataString('related_incident_id') ?? metadataString('incident_id')

  async function changeStatus(status: AlertStatus) {
    if (isUpdating || status === alert.status) {
      return
    }

    setIsUpdating(true)

    try {
      const updated = await updateAlert(alert.id, { status })

      setAlert(updated)

      toast.success(`Alert marked as ${statusLabel(updated.status)}`)
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : 'Unable to update alert',
      )
    } finally {
      setIsUpdating(false)
    }
  }

  function saveNote() {
    const trimmed = note.trim()

    if (!trimmed) {
      toast.error('Enter an analyst note first')
      return
    }

    // We will connect this to the backend investigation/note API
    // once that endpoint is added.
    toast.success('Analyst note captured')

    setNote('')
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

      <div className="rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={alert.severity} />

          <StatusChip
            label={statusLabel(alert.status)}
            tone={statusTone[alert.status]}
          />

          <span className="font-mono text-xs text-muted-foreground">
            {alert.id}
          </span>

          {relatedIncidentId && (
            <Link
              href={`/dashboard/${tenantId}/incidents/${relatedIncidentId}`}
              className="ml-auto inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-xs font-medium text-foreground transition-colors hover:border-primary/50 hover:text-primary"
            >
              <ShieldAlert className="h-3.5 w-3.5" />
              {relatedIncidentId}
            </Link>
          )}
        </div>

        <h1 className="mt-3 text-balance text-xl font-semibold tracking-tight text-foreground">
          {alert.title}
        </h1>

        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
          {alert.description || 'No description provided.'}
        </p>

        <div className="mt-4 flex flex-wrap gap-2 border-t border-border pt-4">
          {alert.status === 'new' && (
            <button
              type="button"
              disabled={isUpdating}
              onClick={() => changeStatus('acknowledged')}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
            >
              <CheckCheck className="h-4 w-4" />
              Acknowledge
            </button>
          )}

          {!['resolved', 'suppressed', 'false_positive'].includes(
            alert.status,
          ) && (
            <button
              type="button"
              disabled={isUpdating}
              onClick={() => changeStatus('investigating')}
              className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-accent disabled:opacity-50"
            >
              <CircleAlert className="h-4 w-4" />
              Investigate
            </button>
          )}

          {!['resolved', 'suppressed', 'false_positive'].includes(
            alert.status,
          ) && (
            <button
              type="button"
              disabled={isUpdating}
              onClick={() => changeStatus('resolved')}
              className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-accent disabled:opacity-50"
            >
              <CheckCheck className="h-4 w-4" />
              Resolve
            </button>
          )}
        </div>

        <div className="mt-4 grid grid-cols-2 gap-4 border-t border-border pt-4 sm:grid-cols-3 lg:grid-cols-6">
          <MetaItem label="Asset">{asset}</MetaItem>

          <MetaItem label="Entity">{entity}</MetaItem>

          <MetaItem label="Source">{alert.source || '—'}</MetaItem>

          <MetaItem label="Tactic">{tactic}</MetaItem>

          <MetaItem label="Detected">
            {formatDate(alert.first_seen_at)}
          </MetaItem>

          <MetaItem label="Assignee">{assignee}</MetaItem>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Panel title="Attack chain" icon={<GitBranch className="h-4 w-4" />}>
            <AttackChain
              steps={
                Array.isArray(metadata.attack_chain)
                  ? metadata.attack_chain
                  : []
              }
            />
          </Panel>

          <Panel title="Evidence" icon={<ListChecks className="h-4 w-4" />}>
            <EvidenceList
              evidence={
                Array.isArray(metadata.evidence) ? metadata.evidence : []
              }
            />
          </Panel>

          <Panel title="Analyst notes" icon={<Save className="h-4 w-4" />}>
            <div className="space-y-3">
              <textarea
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Document findings, hypothesis, evidence, and next actions..."
                className="min-h-28 w-full rounded-md border border-border bg-background p-3 text-sm outline-none focus:border-primary"
              />

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={saveNote}
                  className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-accent"
                >
                  <Save className="h-4 w-4" />
                  Save note
                </button>
              </div>
            </div>
          </Panel>
        </div>

        <div className="space-y-6">
          {/*
            AiAnalyst currently depends on the old mock alert shape.
            We should convert it to use the real Alert type next.
          */}

          <Panel title="MITRE ATT&CK" icon={<Layers className="h-4 w-4" />}>
            <MitreMapping
              mitre={Array.isArray(metadata.mitre) ? metadata.mitre : []}
            />
          </Panel>

          <Panel title="Alert intelligence">
            <dl className="space-y-3 text-sm">
              <div className="flex items-center justify-between gap-4">
                <dt className="text-muted-foreground">Confidence</dt>
                <dd className="font-medium">
                  {alert.confidence != null
                    ? `${Math.round(alert.confidence)}%`
                    : '—'}
                </dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="text-muted-foreground">Risk score</dt>
                <dd className="font-medium">{alert.risk_score ?? '—'}</dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="text-muted-foreground">First seen</dt>
                <dd className="text-right">
                  {formatDate(alert.first_seen_at)}
                </dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="text-muted-foreground">Last seen</dt>
                <dd className="text-right">{formatDate(alert.last_seen_at)}</dd>
              </div>

              <div className="flex items-center justify-between gap-4">
                <dt className="text-muted-foreground">Updated</dt>
                <dd className="text-right">{formatDate(alert.updated_at)}</dd>
              </div>
            </dl>
          </Panel>
        </div>
      </div>
    </div>
  )
}
