'use client'

import { useState } from 'react'
import { Play } from 'lucide-react'
import { scenarios, severityStyles, type Scenario } from '@/lib/soc-scenarios'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DetectionAnimation } from './detection-animation'
import { IncidentReport } from './incident-report'

type Phase = 'picker' | 'detecting' | 'report'

export function Simulator() {
  const [phase, setPhase] = useState<Phase>('picker')
  const [selected, setSelected] = useState<Scenario | null>(null)

  const launch = (scenario: Scenario) => {
    setSelected(scenario)
    setPhase('detecting')
  }

  const reset = () => {
    setSelected(null)
    setPhase('picker')
  }

  return (
    <div className="p-4 lg:p-6">
      {phase === 'picker' && (
        <>
          <div className="mb-5 flex items-center gap-2 text-sm text-muted-foreground">
            <span className="flex size-6 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">
              1
            </span>
            Select an attack scenario to simulate the BLVCK CYBER AI-SOC response.
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {scenarios.map((s) => (
              <Card
                key={s.id}
                className="glass group cursor-pointer transition-all hover:border-primary/50 hover:glow-primary"
                onClick={() => launch(s)}
              >
                <CardContent className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex size-11 items-center justify-center rounded-lg bg-primary/12 text-primary transition-colors group-hover:bg-primary/20">
                      <s.icon className="size-5.5" />
                    </div>
                    <Badge variant="outline" className={severityStyles[s.severity]}>
                      {s.severity}
                    </Badge>
                  </div>
                  <h3 className="mt-4 font-display text-base font-semibold text-foreground">
                    {s.name}
                  </h3>
                  <p className="mt-0.5 text-xs uppercase tracking-wider text-primary">
                    {s.category}
                  </p>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.tagline}</p>
                  <div className="mt-4 flex items-center gap-1.5 text-sm font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
                    <Play className="size-3.5" />
                    Run simulation
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      {phase === 'detecting' && selected && (
        <div className="py-6">
          <DetectionAnimation scenario={selected} onComplete={() => setPhase('report')} />
        </div>
      )}

      {phase === 'report' && selected && (
        <IncidentReport scenario={selected} onReset={reset} />
      )}
    </div>
  )
}
