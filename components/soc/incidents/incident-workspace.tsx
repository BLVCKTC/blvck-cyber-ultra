'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import {
  AlertTriangle,
  Bell,
  Boxes,
  Check,
  GitBranch,
  Layers,
  ListChecks,
  ShieldCheck,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Panel } from '@/components/soc/panel'
import {
  SeverityBadge,
  StatusChip,
} from '@/components/soc/primitives'
import { MitreMapping, EvidenceList } from '@/components/soc/alerts/mitre-evidence'
import {
  alertStatusLabel,
  type Incident,
  type SocAlert,
} from '@/lib/soc/mock'

type TabKey =
  | 'overview'
  | 'timeline'
  | 'evidence'
  | 'entities'
  | 'mitre'
  | 'actions'

const tabs: { key: TabKey; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'timeline', label: 'Timeline' },
  { key: 'evidence', label: 'Evidence' },
  { key: 'entities', label: 'Entities' },
  { key: 'mitre', label: 'MITRE ATT&CK' },
  { key: 'actions', label: 'Actions' },
]

export function IncidentWorkspace({
  incident,
  relatedAlerts,
  tenantId,
}: {
  incident: Incident
  relatedAlerts: SocAlert[]
  tenantId: string
}) {
  const [tab, setTab] = useState<TabKey>('overview')

  const evidence = useMemo(
    () => relatedAlerts.flatMap((a) => a.evidence),
    [relatedAlerts],
  )
  const mitre = useMemo(() => {
    const seen = new Set<string>()
    return relatedAlerts
      .flatMap((a) => a.mitre)
      .filter((m) => {
        if (seen.has(m.techniqueId)) return false
        seen.add(m.techniqueId)
        return true
      })
  }, [relatedAlerts])

  return (
    <div className="rounded-lg border border-border bg-card">
      <div className="flex gap-1 overflow-x-auto border-b border-border px-2">
        {tabs.map((t) => {
          const count =
            t.key === 'evidence'
              ? evidence.length
              : t.key === 'mitre'
                ? mitre.length
                : t.key === 'timeline'
                  ? incident.timeline.length
                  : undefined
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                'relative whitespace-nowrap px-3 py-3 text-sm font-medium transition-colors',
                tab === t.key
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {t.label}
              {count !== undefined && (
                <span className="ml-1.5 rounded bg-muted px-1.5 py-0.5 text-[10px] tabular text-muted-foreground">
                  {count}
                </span>
              )}
              {tab === t.key && (
                <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-primary" />
              )}
            </button>
          )
        })}
      </div>

      <div className="p-5">
        {tab === 'overview' && (
          <Overview incident={incident} relatedAlerts={relatedAlerts} tenantId={tenantId} />
        )}
        {tab === 'timeline' && <Timeline incident={incident} />}
        {tab === 'evidence' && (
          <div>
            {evidence.length > 0 ? (
              <EvidenceList evidence={evidence} />
            ) : (
              <Empty
                icon={<ListChecks className="h-5 w-5" />}
                title="No linked evidence"
                body="Evidence is aggregated from alerts correlated to this incident."
              />
            )}
          </div>
        )}
        {tab === 'entities' && <Entities incident={incident} />}
        {tab === 'mitre' && (
          <div>
            {mitre.length > 0 ? (
              <MitreMapping mitre={mitre} />
            ) : (
              <Empty
                icon={<Layers className="h-5 w-5" />}
                title="No mapped techniques"
                body="Techniques are inherited from correlated alert detections."
              />
            )}
          </div>
        )}
        {tab === 'actions' && (
          <Actions relatedAlerts={relatedAlerts} incident={incident} />
        )}
      </div>
    </div>
  )
}

function Overview({
  incident,
  relatedAlerts,
  tenantId,
}: {
  incident: Incident
  relatedAlerts: SocAlert[]
  tenantId: string
}) {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div className="space-y-5 lg:col-span-2">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Summary</h3>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            {incident.summary}
          </p>
        </div>

        <div>
          <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-foreground">
            <GitBranch className="h-4 w-4 text-muted-foreground" />
            Correlated tactics
          </h3>
          <div className="flex flex-wrap items-center gap-2">
            {incident.tactics.map((t, i) => (
              <span key={t} className="flex items-center gap-2">
                {i > 0 && (
                  <span className="text-muted-foreground" aria-hidden>
                    →
                  </span>
                )}
                <span className="rounded-md border border-border bg-background px-2.5 py-1 text-xs font-medium text-foreground">
                  {t}
                </span>
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-foreground">
            <Bell className="h-4 w-4 text-muted-foreground" />
            Correlated alerts
          </h3>
          {relatedAlerts.length > 0 ? (
            <ul className="divide-y divide-border rounded-md border border-border">
              {relatedAlerts.map((a) => (
                <li key={a.id}>
                  <Link
                    href={`/dashboard/${tenantId}/alerts/${a.id}`}
                    className="flex items-center gap-3 px-3 py-2.5 transition-colors hover:bg-accent/40"
                  >
                    <SeverityBadge severity={a.severity} />
                    <span className="min-w-0 flex-1 truncate text-sm text-foreground">
                      {a.title}
                    </span>
                    <StatusChip label={alertStatusLabel[a.status]} tone="muted" />
                    <span className="hidden text-xs text-muted-foreground sm:block">
                      {a.detectedAt}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">
              No alerts are currently correlated to this incident.
            </p>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className="rounded-lg border border-border bg-background p-4">
          <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Response posture
          </p>
          <div className="mt-3 space-y-3 text-sm">
            <Row label="Priority" value={incident.priority} />
            <Row label="Owner" value={incident.owner} />
            <Row label="Opened" value={incident.openedAt} />
            <Row label="Last update" value={incident.updatedAt} />
            <Row label="Alerts linked" value={String(incident.alertCount)} />
            <Row label="Assets impacted" value={String(incident.assets.length)} />
          </div>
        </div>
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </div>
  )
}

function Timeline({ incident }: { incident: Incident }) {
  return (
    <ol className="relative space-y-5 pl-6">
      <span
        className="absolute left-[7px] bottom-1.5 top-1.5 w-px bg-border"
        aria-hidden
      />
      {incident.timeline.map((e, i) => (
        <li key={i} className="relative">
          <span
            className="absolute -left-6 top-1 h-3.5 w-3.5 rounded-full bg-primary ring-4 ring-card"
            aria-hidden
          />
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-foreground">{e.actor}</span>
            <span className="ml-auto text-xs text-muted-foreground">{e.at}</span>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{e.text}</p>
        </li>
      ))}
    </ol>
  )
}

function Entities({ incident }: { incident: Incident }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {incident.assets.map((a) => (
        <div
          key={a}
          className="flex items-center gap-3 rounded-md border border-border bg-background px-3 py-3"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-muted text-muted-foreground">
            <Boxes className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <p className="truncate font-mono text-sm text-foreground">{a}</p>
            <p className="text-xs text-muted-foreground">Impacted asset</p>
          </div>
        </div>
      ))}
    </div>
  )
}

const actionTone = {
  contain: {
    label: 'Containment',
    className: 'border-critical/40 bg-critical/10 text-critical',
    danger: true,
  },
  investigate: {
    label: 'Investigation',
    className: 'border-info/40 bg-info/10 text-info',
    danger: false,
  },
  notify: {
    label: 'Notification',
    className: 'border-warning/40 bg-warning/10 text-warning',
    danger: false,
  },
} as const

function Actions({
  relatedAlerts,
  incident,
}: {
  relatedAlerts: SocAlert[]
  incident: Incident
}) {
  const actions = useMemo(() => {
    const seen = new Set<string>()
    return relatedAlerts
      .flatMap((a) => a.recommendedActions)
      .filter((a) => {
        if (seen.has(a.label)) return false
        seen.add(a.label)
        return true
      })
  }, [relatedAlerts])

  const [pending, setPending] = useState<string | null>(null)
  const [approved, setApproved] = useState<Record<string, boolean>>({})

  if (actions.length === 0) {
    return (
      <Empty
        icon={<ShieldCheck className="h-5 w-5" />}
        title="No response actions queued"
        body="Recommended actions surface here as correlated alerts generate them."
      />
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-md border border-intel/30 bg-intel/10 p-3">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-intel" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          Infrastructure-impacting actions require human approval before
          execution. BLVCK CYBER never auto-executes containment on{' '}
          <span className="font-medium text-foreground">{incident.id}</span>.
        </p>
      </div>

      <ul className="space-y-2">
        {actions.map((a) => {
          const tone = actionTone[a.kind]
          const isApproved = approved[a.label]
          return (
            <li
              key={a.label}
              className="rounded-md border border-border bg-background p-3"
            >
              <div className="flex flex-wrap items-center gap-3">
                <span
                  className={cn(
                    'inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide',
                    tone.className,
                  )}
                >
                  {tone.danger ? (
                    <AlertTriangle className="h-3 w-3" />
                  ) : (
                    <Zap className="h-3 w-3" />
                  )}
                  {tone.label}
                </span>
                <span className="min-w-0 flex-1 text-sm font-medium text-foreground">
                  {a.label}
                </span>
                {isApproved ? (
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-success">
                    <Check className="h-3.5 w-3.5" /> Approved
                  </span>
                ) : tone.danger ? (
                  <button
                    onClick={() => setPending(a.label)}
                    className="rounded-md border border-critical/40 bg-critical/10 px-2.5 py-1 text-xs font-medium text-critical transition-colors hover:bg-critical/20"
                  >
                    Review action
                  </button>
                ) : (
                  <button
                    onClick={() =>
                      setApproved((p) => ({ ...p, [a.label]: true }))
                    }
                    className="rounded-md border border-border px-2.5 py-1 text-xs font-medium text-foreground transition-colors hover:border-primary/50 hover:text-primary"
                  >
                    Run
                  </button>
                )}
              </div>

              {pending === a.label && (
                <div className="mt-3 rounded-md border border-critical/30 bg-critical/5 p-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-critical">
                    Confirm containment
                  </p>
                  <p className="mt-1.5 text-sm text-foreground">{a.label}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    This action can affect production infrastructure. Approval is
                    recorded in the audit log.
                  </p>
                  <div className="mt-3 flex items-center gap-2">
                    <button
                      onClick={() => setPending(null)}
                      className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => {
                        setApproved((p) => ({ ...p, [a.label]: true }))
                        setPending(null)
                      }}
                      className="rounded-md bg-critical px-3 py-1.5 text-xs font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                    >
                      Approve &amp; execute
                    </button>
                  </div>
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Empty({
  icon,
  title,
  body,
}: {
  icon: React.ReactNode
  title: string
  body: string
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-muted-foreground">
        {icon}
      </span>
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="max-w-xs text-xs text-muted-foreground">{body}</p>
    </div>
  )
}
