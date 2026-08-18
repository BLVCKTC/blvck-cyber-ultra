import {
  Cpu,
  FileWarning,
  Network,
  ScrollText,
  UserRound,
  type LucideIcon,
} from 'lucide-react'
import type { Evidence, MitreRef } from '@/lib/soc/mock'

export function MitreMapping({ mitre }: { mitre: MitreRef[] }) {
  return (
    <ul className="space-y-2">
      {mitre.map((m) => (
        <li
          key={m.techniqueId}
          className="flex items-center gap-3 rounded-md border border-border bg-background px-3 py-2"
        >
          <span className="rounded bg-intel/15 px-1.5 py-0.5 text-[11px] font-semibold text-intel">
            {m.techniqueId}
          </span>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">
              {m.techniqueName}
            </p>
            <p className="text-xs text-muted-foreground">{m.tactic}</p>
          </div>
        </li>
      ))}
    </ul>
  )
}

const evidenceIcon: Record<Evidence['kind'], LucideIcon> = {
  process: Cpu,
  network: Network,
  file: FileWarning,
  identity: UserRound,
  log: ScrollText,
}

export function EvidenceList({ evidence }: { evidence: Evidence[] }) {
  return (
    <ul className="divide-y divide-border">
      {evidence.map((e) => {
        const Icon = evidenceIcon[e.kind]
        return (
          <li key={e.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
            <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
              <Icon className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase tracking-wide text-muted-foreground">
                  {e.label}
                </span>
                <span className="ml-auto text-xs text-muted-foreground">
                  {e.at}
                </span>
              </div>
              <p className="mt-0.5 break-all font-mono text-xs text-foreground">
                {e.value}
              </p>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
