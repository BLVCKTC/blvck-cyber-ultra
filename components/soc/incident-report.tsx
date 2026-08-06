'use client'

import { useState } from 'react'
import {
  FileDown,
  RotateCcw,
  Clock,
  Search,
  Server,
  UserRound,
  Crosshair,
  ShieldCheck,
  Wrench,
  Lightbulb,
  Bot,
  ArrowRight,
  Loader2,
  ChevronRight,
} from 'lucide-react'
import {
  type Scenario,
  severityStyles,
  statusStyles,
} from '@/lib/soc-scenarios'
import { generateIncidentPdf } from '@/lib/generate-incident-pdf'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

function Section({
  icon: Icon,
  title,
  step,
  children,
}: {
  icon: typeof Clock
  title: string
  step: number
  children: React.ReactNode
}) {
  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-md bg-primary/12 text-primary">
          <Icon className="size-4.5" />
        </div>
        <div>
          <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Step {step}
          </div>
          <CardTitle className="font-display text-base">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

const kindStyles: Record<string, { dot: string; label: string }> = {
  attacker: { dot: 'bg-destructive', label: 'Adversary' },
  ai: { dot: 'bg-primary', label: 'BLVCK AI' },
  system: { dot: 'bg-success', label: 'System' },
}

export function IncidentReport({
  scenario,
  onReset,
}: {
  scenario: Scenario
  onReset: () => void
}) {
  const [downloading, setDownloading] = useState(false)

  const handleDownload = () => {
    setDownloading(true)
    // Defer so the spinner paints before the (synchronous) PDF build.
    setTimeout(() => {
      try {
        generateIncidentPdf(scenario)
      } finally {
        setDownloading(false)
      }
    }, 60)
  }

  return (
    <div className="space-y-6">
      {/* Header / detection summary */}
      <Card className="glass overflow-hidden">
        <div className="relative">
          <div className="absolute inset-0 grid-hud opacity-30" aria-hidden="true" />
          <CardContent className="relative flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex size-12 items-center justify-center rounded-lg bg-primary/15 glow-primary">
                <scenario.icon className="size-6 text-primary" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-display text-xl font-bold text-foreground">
                    {scenario.name}
                  </h2>
                  <Badge variant="outline" className={severityStyles[scenario.severity]}>
                    {scenario.severity}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{scenario.tagline}</p>
                <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-1.5">
                    <Bot className="size-3.5 text-primary" />
                    {scenario.detectedBy}
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <span className="font-mono font-semibold text-primary">
                      {scenario.confidence}%
                    </span>
                    confidence
                  </span>
                </div>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Button variant="outline" onClick={onReset}>
                <RotateCcw className="size-4" />
                New scenario
              </Button>
              <Button onClick={handleDownload} disabled={downloading} className="glow-primary">
                {downloading ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <FileDown className="size-4" />
                )}
                Download PDF report
              </Button>
            </div>
          </CardContent>
        </div>
      </Card>

      {/* 1. Executive Summary */}
      <Section icon={FileDown} title="AI-Generated Executive Summary" step={1}>
        <p className="text-sm leading-relaxed text-foreground/90">{scenario.execSummary}</p>
      </Section>

      {/* 2. Timeline */}
      <Section icon={Clock} title="Attack Timeline" step={2}>
        <ol className="relative space-y-4 border-l border-border pl-6">
          {scenario.timeline.map((t, i) => {
            const style = kindStyles[t.kind]
            return (
              <li key={i} className="relative">
                <span
                  className={`absolute -left-[27px] top-1 size-3 rounded-full ${style.dot} ring-4 ring-background`}
                />
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-primary">{t.time}</span>
                  <span className="text-sm font-medium text-foreground">{t.label}</span>
                  <Badge variant="outline" className="border-border text-[10px] text-muted-foreground">
                    {style.label}
                  </Badge>
                </div>
                <p className="mt-0.5 text-sm text-muted-foreground">{t.detail}</p>
              </li>
            )
          })}
        </ol>
      </Section>

      {/* 3. Investigation */}
      <Section icon={Search} title="AI Investigation Results" step={3}>
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Key Findings
            </h4>
            <ul className="space-y-2">
              {scenario.investigationFindings.map((f, i) => (
                <li key={i} className="flex gap-2 text-sm text-foreground/90">
                  <ChevronRight className="mt-0.5 size-4 shrink-0 text-primary" />
                  {f}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Indicators of Compromise
            </h4>
            <div className="space-y-2">
              {scenario.iocs.map((ioc, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between gap-3 rounded-md border border-border/60 bg-secondary/30 px-3 py-2"
                >
                  <span className="shrink-0 text-xs font-semibold text-primary">{ioc.type}</span>
                  <span className="truncate font-mono text-xs text-muted-foreground">
                    {ioc.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* 4. Affected systems */}
      <Section icon={Server} title="Affected Systems & Accounts" step={4}>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {scenario.affectedSystems.map((s) => (
            <div key={s.name} className="rounded-lg border border-border/60 bg-secondary/30 p-3">
              <div className="flex items-center justify-between">
                <Server className="size-4 text-primary" />
                <Badge variant="outline" className={statusStyles[s.status]}>
                  {s.status}
                </Badge>
              </div>
              <div className="mt-2 font-mono text-sm font-medium text-foreground">{s.name}</div>
              <div className="text-xs text-muted-foreground">{s.type}</div>
            </div>
          ))}
          {scenario.affectedAccounts.map((a) => (
            <div key={a.name} className="rounded-lg border border-border/60 bg-secondary/30 p-3">
              <div className="flex items-center justify-between">
                <UserRound className="size-4 text-primary" />
                <Badge variant="outline" className={statusStyles[a.status]}>
                  {a.status}
                </Badge>
              </div>
              <div className="mt-2 font-mono text-sm font-medium text-foreground">{a.name}</div>
              <div className="text-xs text-muted-foreground">{a.type}</div>
            </div>
          ))}
        </div>
      </Section>

      {/* 5. MITRE + attack chain */}
      <Section icon={Crosshair} title="MITRE ATT&CK Mapping" step={5}>
        <div className="mb-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {scenario.attackChain.map((p, i) => (
            <div key={i} className="relative rounded-lg border border-border/60 bg-secondary/30 p-3">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-primary">
                {p.phase}
              </div>
              <div className="mt-1 text-sm font-medium text-foreground">{p.technique}</div>
              <div className="mt-0.5 text-xs text-muted-foreground">{p.detail}</div>
              {i < scenario.attackChain.length - 1 && (
                <ArrowRight className="absolute -right-3 top-1/2 hidden size-4 -translate-y-1/2 text-muted-foreground lg:block" />
              )}
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {scenario.mitre.map((m) => (
            <div
              key={m.id}
              className="rounded-md border border-border/60 bg-secondary/30 px-3 py-1.5"
            >
              <span className="font-mono text-xs font-semibold text-primary">{m.id}</span>
              <span className="ml-2 text-xs text-foreground">{m.technique}</span>
              <span className="ml-2 text-[10px] text-muted-foreground">· {m.tactic}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* 6. Root cause + remediation */}
      <Section icon={ShieldCheck} title="Root Cause & Remediation" step={6}>
        <div className="rounded-lg border border-border/60 bg-secondary/30 p-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Root Cause
          </div>
          <p className="mt-1 text-sm leading-relaxed text-foreground/90">{scenario.rootCause}</p>
        </div>
        <Separator className="my-5" />
        <div className="grid gap-6 lg:grid-cols-3">
          <RemediationList
            icon={ShieldCheck}
            title="Containment"
            items={scenario.containment}
          />
          <RemediationList icon={Wrench} title="Recovery Steps" items={scenario.recovery} />
          <RemediationList icon={Lightbulb} title="Lessons Learned" items={scenario.lessons} />
        </div>
      </Section>

      <div className="flex justify-center pb-4">
        <Button size="lg" onClick={handleDownload} disabled={downloading} className="glow-primary">
          {downloading ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <FileDown className="size-4" />
          )}
          Download full incident report (PDF)
        </Button>
      </div>
    </div>
  )
}

function RemediationList({
  icon: Icon,
  title,
  items,
}: {
  icon: typeof ShieldCheck
  title: string
  items: string[]
}) {
  return (
    <div>
      <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
        <Icon className="size-4 text-primary" />
        {title}
      </h4>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-sm text-muted-foreground">
            <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
