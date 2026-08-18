import { cn } from '@/lib/utils'
import type { ChainStep } from '@/lib/soc/mock'
import { StatusChip } from '@/components/soc/primitives'

const stepTone = {
  observed: 'warning',
  blocked: 'success',
  pending: 'critical',
} as const

const stepLabel = {
  observed: 'Observed',
  blocked: 'Blocked',
  pending: 'Ongoing',
} as const

const dotColor = {
  observed: 'bg-warning',
  blocked: 'bg-success',
  pending: 'bg-critical',
} as const

export function AttackChain({ steps }: { steps: ChainStep[] }) {
  return (
    <ol className="relative space-y-5 pl-6">
      <span
        className="absolute left-[7px] top-1.5 bottom-1.5 w-px bg-border"
        aria-hidden
      />
      {steps.map((s, i) => (
        <li key={i} className="relative">
          <span
            className={cn(
              'absolute -left-6 top-0.5 h-3.5 w-3.5 rounded-full ring-4 ring-card',
              dotColor[s.status],
            )}
            aria-hidden
          />
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-foreground">
              {s.label}
            </span>
            <StatusChip label={stepLabel[s.status]} tone={stepTone[s.status]} />
            <span className="ml-auto text-xs text-muted-foreground">{s.at}</span>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{s.detail}</p>
        </li>
      ))}
    </ol>
  )
}
