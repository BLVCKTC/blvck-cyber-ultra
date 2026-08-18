import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { kpis } from '@/lib/soc/mock'

export function KpiCards() {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((k) => {
        const positive =
          k.trend === 'flat'
            ? null
            : (k.trend === 'up') === k.goodWhenUp
        const TrendIcon =
          k.trend === 'up'
            ? ArrowUpRight
            : k.trend === 'down'
              ? ArrowDownRight
              : Minus
        return (
          <div
            key={k.key}
            className="rounded-lg border border-border bg-card p-4"
          >
            <p className="text-sm text-muted-foreground">{k.label}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-semibold tabular tracking-tight text-foreground">
                {k.value}
              </span>
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 text-xs font-medium tabular',
                  positive === null && 'text-muted-foreground',
                  positive === true && 'text-success',
                  positive === false && 'text-high',
                )}
              >
                <TrendIcon className="h-3.5 w-3.5" />
                {k.delta}
              </span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">{k.sub}</p>
          </div>
        )
      })}
    </div>
  )
}
