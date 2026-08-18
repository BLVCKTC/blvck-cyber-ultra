'use client'

import { useState } from 'react'
import {
  Sparkles,
  ShieldBan,
  Search,
  BellRing,
  Check,
  type LucideIcon,
} from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import type { SocAlert } from '@/lib/soc/mock'

const actionIcon: Record<string, LucideIcon> = {
  contain: ShieldBan,
  investigate: Search,
  notify: BellRing,
}

export function AiAnalyst({ alert }: { alert: SocAlert }) {
  const [done, setDone] = useState<Record<number, boolean>>({})

  return (
    <div className="rounded-lg border border-intel/30 bg-intel/[0.06]">
      <header className="flex items-center gap-2 border-b border-intel/20 px-4 py-3">
        <span className="flex h-7 w-7 items-center justify-center rounded-md bg-intel/15 text-intel">
          <Sparkles className="h-4 w-4" />
        </span>
        <h2 className="text-sm font-semibold text-foreground">AI analyst</h2>
        <span className="ml-auto rounded bg-intel/15 px-1.5 py-0.5 text-[11px] font-medium text-intel">
          {alert.confidence}% confidence
        </span>
      </header>

      <div className="space-y-4 p-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">
            Summary
          </p>
          <p className="mt-1 text-sm leading-relaxed text-foreground">
            {alert.aiSummary}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">
            Assessment
          </p>
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
            {alert.aiAssessment}
          </p>
        </div>

        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
            Recommended actions
          </p>
          <div className="space-y-2">
            {alert.recommendedActions.map((a, i) => {
              const Icon = actionIcon[a.kind] ?? Search
              const isDone = done[i]
              return (
                <button
                  key={i}
                  disabled={isDone}
                  onClick={() => {
                    setDone((d) => ({ ...d, [i]: true }))
                    toast.success(`Action queued: ${a.label}`, {
                      description: `${alert.id} · pending approval`,
                    })
                  }}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-md border px-3 py-2 text-left text-sm transition-colors',
                    isDone
                      ? 'border-success/30 bg-success/10 text-success'
                      : 'border-border bg-background text-foreground hover:border-primary/50 hover:bg-accent/50',
                  )}
                >
                  <span
                    className={cn(
                      'flex h-6 w-6 shrink-0 items-center justify-center rounded',
                      isDone ? 'bg-success/15' : 'bg-muted text-muted-foreground',
                    )}
                  >
                    {isDone ? (
                      <Check className="h-3.5 w-3.5" />
                    ) : (
                      <Icon className="h-3.5 w-3.5" />
                    )}
                  </span>
                  <span className="flex-1">{a.label}</span>
                  <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
                    {isDone ? 'Queued' : a.kind}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
