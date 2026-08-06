import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import type { ThreatSource } from '@/lib/threat-data'

type SourceRow = ThreatSource & { count: number; critical: number }

export function SourcesTable({ sources }: { sources: SourceRow[] }) {
  const max = Math.max(1, ...sources.map((s) => s.count))
  const rows = sources.slice(0, 8)

  return (
    <Table>
      <TableHeader>
        <TableRow className="border-border hover:bg-transparent">
          <TableHead className="text-xs">Origin</TableHead>
          <TableHead className="text-xs">Volume</TableHead>
          <TableHead className="w-16 text-right text-xs">Events</TableHead>
          <TableHead className="w-20 text-right text-xs">Critical</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((s) => (
          <TableRow key={s.code} className="border-border">
            <TableCell>
              <div className="flex items-center gap-2.5">
                <span className="flex size-7 items-center justify-center rounded-md bg-secondary/60 font-mono text-[10px] font-semibold text-muted-foreground">
                  {s.code}
                </span>
                <div className="leading-tight">
                  <div className="text-sm font-medium text-foreground">{s.country}</div>
                  <div className="text-xs text-muted-foreground">{s.city}</div>
                </div>
              </div>
            </TableCell>
            <TableCell>
              <Progress value={(s.count / max) * 100} className="h-1.5 w-28" />
            </TableCell>
            <TableCell className="text-right font-mono text-sm tabular-nums text-foreground">
              {s.count}
            </TableCell>
            <TableCell className="text-right font-mono text-sm tabular-nums">
              <span className={s.critical > 0 ? 'text-[color:var(--critical)]' : 'text-muted-foreground'}>
                {s.critical}
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
