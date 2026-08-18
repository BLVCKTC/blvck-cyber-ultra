import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { alerts, severityRank, alertStatusLabel } from '@/lib/soc/mock'
import { SeverityDot, ConfidenceMeter } from '@/components/soc/primitives'

export function PriorityQueue({ tenantId }: { tenantId: string }) {
  const top = [...alerts]
    .filter((a) => a.status !== 'resolved' && a.status !== 'false_positive')
    .sort((a, b) => severityRank[a.severity] - severityRank[b.severity])
    .slice(0, 5)

  return (
    <ul className="divide-y divide-border">
      {top.map((a) => (
        <li key={a.id}>
          <Link
            href={`/dashboard/${tenantId}/alerts/${a.id}`}
            className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-accent/50"
          >
            <SeverityDot severity={a.severity} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">
                {a.title}
              </p>
              <p className="mt-0.5 truncate text-xs text-muted-foreground">
                {a.id} · {a.asset} · {a.tactic} · {alertStatusLabel[a.status]}
              </p>
            </div>
            <div className="hidden shrink-0 sm:block">
              <ConfidenceMeter value={a.confidence} />
            </div>
            <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          </Link>
        </li>
      ))}
    </ul>
  )
}
