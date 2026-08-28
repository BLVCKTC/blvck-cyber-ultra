import Link from 'next/link'
import { Crosshair } from 'lucide-react'
import { Panel } from '@/components/soc/panel'

const tactics = [
  { name: 'Initial access', covered: 9, total: 12 },
  { name: 'Execution', covered: 14, total: 16 },
  { name: 'Persistence', covered: 7, total: 13 },
  { name: 'Credential access', covered: 11, total: 15 },
  { name: 'Lateral movement', covered: 5, total: 10 },
  { name: 'Exfiltration', covered: 8, total: 9 },
]

export function MitreCoverage() {
  const covered = tactics.reduce((sum, tactic) => sum + tactic.covered, 0)
  const total = tactics.reduce((sum, tactic) => sum + tactic.total, 0)

  return (
    <Panel
      title="MITRE coverage by tactic"
      icon={<Crosshair aria-hidden="true" />}
      action={<Link href="/dashboard/mitre" className="text-xs font-medium text-primary hover:underline">Open navigator</Link>}
    >
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <p className="text-3xl font-semibold tabular text-foreground">{Math.round((covered / total) * 100)}%</p>
          <p className="text-xs text-muted-foreground">{covered} of {total} techniques covered</p>
        </div>
        <p className="max-w-48 text-right text-xs leading-relaxed text-muted-foreground">Weakest areas are the fastest path to reducing blind spots.</p>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-3" aria-label="MITRE coverage by tactic">
        {tactics.map((tactic) => {
          const percent = Math.round((tactic.covered / tactic.total) * 100)
          return (
            <div key={tactic.name}>
              <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                <span className="truncate text-muted-foreground">{tactic.name}</span>
                <span className="tabular font-medium text-foreground">{percent}%</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary" style={{ width: `${percent}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
