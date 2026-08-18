'use client'

import { useEffect, useState } from 'react'
import { Radar, Cpu, ShieldCheck } from 'lucide-react'
import type { Scenario } from '@/lib/soc-scenarios'

const stages = [
  'Ingesting telemetry from endpoints & network sensors...',
  'Correlating events across identity, cloud and email...',
  'Running behavioral models on anomalous activity...',
  'Matching TTPs against MITRE ATT&CK knowledge base...',
  'Threat confirmed — generating incident dossier...',
]

export function DetectionAnimation({
  scenario,
  onComplete,
}: {
  scenario: Scenario
  onComplete: () => void
}) {
  const [stage, setStage] = useState(0)
  const [confidence, setConfidence] = useState(0)

  useEffect(() => {
    const stageTimer = setInterval(() => {
      setStage((s) => {
        if (s >= stages.length - 1) {
          clearInterval(stageTimer)
          return s
        }
        return s + 1
      })
    }, 700)

    const confTimer = setInterval(() => {
      setConfidence((c) => {
        const next = c + Math.random() * 9
        return next >= scenario.confidence ? scenario.confidence : next
      })
    }, 90)

    const done = setTimeout(onComplete, 3900)

    return () => {
      clearInterval(stageTimer)
      clearInterval(confTimer)
      clearTimeout(done)
    }
  }, [scenario, onComplete])

  return (
    <div className="relative mx-auto flex max-w-3xl flex-col items-center overflow-hidden rounded-2xl border border-border glass p-8 sm:p-12">
      <div className="absolute inset-0 grid-hud opacity-40" aria-hidden="true" />
      <div className="absolute inset-0 scanline opacity-60" aria-hidden="true" />

      {/* Radar */}
      <div className="relative z-10 flex size-40 items-center justify-center">
        <span className="absolute inset-0 animate-ping rounded-full border border-primary/40" />
        <span className="absolute inset-3 rounded-full border border-primary/30" />
        <span className="absolute inset-8 rounded-full border border-primary/20" />
        <span
          className="absolute inset-0 rounded-full"
          style={{
            background:
              'conic-gradient(from 0deg, color-mix(in oklch, var(--primary) 45%, transparent), transparent 55%)',
            animation: 'spin 1.6s linear infinite',
          }}
          aria-hidden="true"
        />
        <div className="relative flex size-16 items-center justify-center rounded-full bg-primary/15 glow-primary">
          <Radar className="size-7 text-primary" />
        </div>
      </div>

      <div className="relative z-10 mt-6 text-center">
        <div className="flex items-center justify-center gap-2 text-xs font-medium uppercase tracking-[0.25em] text-primary">
          <Cpu className="size-3.5" />
          BLVCK AI-SOC · Live Analysis
        </div>
        <h3 className="mt-3 font-display text-xl font-bold text-foreground">
          Detecting: {scenario.name}
        </h3>
        <p className="mt-1 text-sm text-muted-foreground">{scenario.detectionSignal}</p>
      </div>

      {/* Confidence */}
      <div className="relative z-10 mt-6 w-full max-w-md">
        <div className="mb-1.5 flex items-center justify-between text-xs">
          <span className="text-muted-foreground">AI Confidence</span>
          <span className="font-mono font-semibold text-primary">
            {Math.round(confidence)}%
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-primary transition-all duration-100"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Streaming log */}
      <div className="relative z-10 mt-6 w-full max-w-md space-y-1.5">
        {stages.map((s, i) => (
          <div
            key={s}
            className={`flex items-center gap-2 font-mono text-xs transition-opacity duration-300 ${
              i <= stage ? 'opacity-100' : 'opacity-30'
            }`}
          >
            {i < stage ? (
              <ShieldCheck className="size-3.5 shrink-0 text-success" />
            ) : i === stage ? (
              <span className="size-1.5 shrink-0 animate-pulse rounded-full bg-primary" />
            ) : (
              <span className="size-1.5 shrink-0 rounded-full bg-muted-foreground/40" />
            )}
            <span className={i <= stage ? 'text-foreground' : 'text-muted-foreground'}>{s}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
