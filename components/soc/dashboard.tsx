"use client"

import { useState } from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"
import { SecurityScore } from "./security-score"
import { StatCards } from "./stat-cards"
import { ThreatFeed } from "./threat-feed"
import { AttackChart } from "./attack-chart"
import { AIStatus } from "./ai-status"
import { HealthMonitor } from "./health-monitor"
import { Vulnerabilities } from "./vulnerabilities"
import { ThreatIntel } from "./threat-intel"
import { AlertsPanel } from "./alerts-panel"
import { ReportsPanel } from "./reports-panel"
import { AIAssistant } from "./ai-assistant"

export function Dashboard() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />

      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenu={() => setMenuOpen(true)} />

        <main className="cyber-grid flex-1 space-y-8 p-4 lg:p-6">
          {/* Overview */}
          <section id="overview" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Security Overview" sub="Real-time posture across all monitored assets" />
            <StatCards />
            <div className="grid gap-4 lg:grid-cols-3">
              <SecurityScore />
              <div className="lg:col-span-2">
                <AttackChart />
              </div>
            </div>
            <div className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <AIStatus />
              </div>
              <AlertsPanel />
            </div>
          </section>

          {/* Threat Center */}
          <section id="threat-center" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Threat Center" sub="Live attacks, sources, severity and response status" />
            <ThreatFeed />
          </section>

          {/* Security Testing */}
          <section id="security-testing" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Security Testing" sub="Vulnerability scans, penetration tests and remediation" />
            <Vulnerabilities />
          </section>

          {/* Health */}
          <section id="health" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Health Monitoring" sub="Infrastructure, uptime and data protection status" />
            <HealthMonitor />
          </section>

          {/* Threat Intel */}
          <section id="threat-intel" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Threat Intelligence" sub="Regional attack patterns across the African network" />
            <ThreatIntel />
          </section>

          {/* Reports */}
          <section id="reports" className="scroll-mt-20 space-y-4">
            <SectionHeading title="Reports" sub="Executive summaries, compliance and AI insights" />
            <ReportsPanel />
          </section>

          {/* AI Assistant */}
          <section id="assistant" className="scroll-mt-20 space-y-4">
            <SectionHeading title="AI Assistant" sub="Ask questions and get plain-language security guidance" />
            <div className="max-w-3xl">
              <AIAssistant />
            </div>
          </section>

          <footer className="border-t border-border pt-6 pb-2 text-center">
            <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              BLVCK CYBER · AI-SOC Platform · Protecting African Digital Infrastructure
            </p>
          </footer>
        </main>
      </div>
    </div>
  )
}

function SectionHeading({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="h-4 w-1 rounded-full bg-primary" />
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-foreground text-balance">{title}</h1>
        <p className="text-xs text-muted-foreground">{sub}</p>
      </div>
    </div>
  )
}
