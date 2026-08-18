import { ArrowDownRight, ArrowUpRight, type LucideIcon } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export type StatTone = 'primary' | 'critical' | 'high' | 'warning' | 'info'

const toneMap: Record<StatTone, { icon: string; ring: string }> = {
  primary: { icon: 'text-primary', ring: 'bg-primary/12' },
  critical: { icon: 'text-[color:var(--critical)]', ring: 'bg-[color:var(--critical)]/12' },
  high: { icon: 'text-[color:var(--high)]', ring: 'bg-[color:var(--high)]/12' },
  warning: { icon: 'text-[color:var(--warning)]', ring: 'bg-[color:var(--warning)]/12' },
  info: { icon: 'text-[color:var(--info)]', ring: 'bg-[color:var(--info)]/12' },
}

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = 'primary',
  delta,
  deltaDirection,
  invertDelta,
}: {
  label: string
  value: string
  hint?: string
  icon: LucideIcon
  tone?: StatTone
  delta?: string
  deltaDirection?: 'up' | 'down'
  invertDelta?: boolean
}) {
  const tokens = toneMap[tone]
  // "good" is green unless invertDelta flips the meaning (e.g. more attacks = bad)
  const isGood = invertDelta ? deltaDirection === 'down' : deltaDirection === 'up'

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="flex items-start justify-between gap-4 p-5">
        <div className="min-w-0 space-y-2">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {label}
          </p>
          <p className="font-display text-3xl font-bold leading-none tracking-tight text-foreground">
            {value}
          </p>
          <div className="flex items-center gap-2">
            {delta ? (
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 text-xs font-semibold',
                  isGood ? 'text-primary' : 'text-[color:var(--critical)]'
                )}
              >
                {deltaDirection === 'up' ? (
                  <ArrowUpRight className="size-3.5" />
                ) : (
                  <ArrowDownRight className="size-3.5" />
                )}
                {delta}
              </span>
            ) : null}
            {hint ? <span className="truncate text-xs text-muted-foreground">{hint}</span> : null}
          </div>
        </div>
        <div className={cn('flex size-10 shrink-0 items-center justify-center rounded-lg', tokens.ring)}>
          <Icon className={cn('size-5', tokens.icon)} />
        </div>
      </CardContent>
    </Card>
  )
}
