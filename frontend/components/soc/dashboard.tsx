'use client'

import { useState } from 'react'

import { Sidebar } from '../shell/sidebar'
import { Topbar } from './topbar'

import { SecurityScore } from './security-score'
import { StatCards } from './stat-cards'
import { ThreatFeed } from './threat-feed'
import { AttackChart } from './attack-chart'
import { AIStatus } from './ai-status'
import { HealthMonitor } from './health-monitor'
import { Vulnerabilities } from './vulnerabilities'
import { ThreatIntel } from './threat-intel'
import { AlertsPanel } from './alerts-panel'
import { ReportsPanel } from './reports-panel'
import { AIAssistant } from './ai-assistant'
import { LiveOperations } from './live-operations'

/*
  BLVCK SHIELD FEATURES MERGED HERE
*/

import { AfricaMap } from '@/components/AfricaMap'
import { SeverityBadge } from '@/components/SeverityBadge'

import { Shield, Server, Activity, Gauge, TrendingUp } from 'lucide-react'

const regionalCoverage = [
  {
    country: 'South Africa',
    coverage: 95,
    assets: 4200,
  },
  {
    country: 'Nigeria',
    coverage: 91,
    assets: 3500,
  },
  {
    country: 'Kenya',
    coverage: 87,
    assets: 2100,
  },
  {
    country: 'Zimbabwe',
    coverage: 82,
    assets: 980,
  },
  {
    country: 'Ghana',
    coverage: 78,
    assets: 740,
  },
]

const threats = [
  {
    id: 'INC-001',
    severity: 'Critical',
    type: 'Ransomware Attempt',
    target: 'DC01 Server',
    country: 'Zimbabwe',
    timestamp: new Date(),
  },
  {
    id: 'INC-002',
    severity: 'High',
    type: 'Privilege Escalation',
    target: 'Admin Account',
    country: 'South Africa',
    timestamp: new Date(),
  },
  {
    id: 'INC-003',
    severity: 'Medium',
    type: 'Phishing Payload',
    target: 'Finance User',
    country: 'Nigeria',
    timestamp: new Date(),
  },
]

export function Dashboard() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />

      <div className="flex flex-1 flex-col min-w-0">
        <Topbar onMenu={() => setMenuOpen(true)} />

        <main
          className="
cyber-grid
flex-1
space-y-8
p-4
lg:p-6
"
        >
          {/* EXECUTIVE OVERVIEW */}

          <section className="space-y-4">
            <SectionHeading
              title="Security Operations Center"
              sub="Unified BLVCK CYBER + BLVCK SHIELD AI security platform"
            />

            <LiveOperations />

            <StatCards />

            <div className="grid lg:grid-cols-3 gap-4">
              <div className="glass p-6">
                <div className="text-xs font-mono uppercase text-cyber">
                  Security Posture
                </div>

                <div className="mt-3 flex items-end gap-2">
                  <div className="text-5xl font-bold text-cyber">94</div>

                  <div className="text-muted-foreground">/100</div>
                </div>
              </div>

              <div className="lg:col-span-2">
                <AttackChart />
              </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <AIStatus />
              </div>

              <AlertsPanel />
            </div>
          </section>

          {/* SHIELD REGIONAL INTELLIGENCE */}

          <section className="space-y-4">
            <SectionHeading
              title="African Threat Intelligence"
              sub="Regional visibility powered by BLVCK SHIELD"
            />

            <div className="grid lg:grid-cols-3 gap-4">
              <div className="glass p-6 lg:col-span-2">
                <div className="text-xs font-mono uppercase text-cyber">
                  Live Threat Feed
                </div>

                <div className="mt-4 space-y-2">
                  {threats.map((t) => (
                    <div
                      key={t.id}
                      className="
flex
items-center
gap-3
rounded-lg
p-3
hover:bg-white/5
"
                    >
                      <SeverityBadge severity={t.severity} />

                      <div className="flex-1">
                        <div className="text-sm">{t.type}</div>

                        <div className="text-xs text-muted-foreground">
                          {t.target}•{t.country}
                        </div>
                      </div>

                      <TrendingUp className="h-4 w-4 text-cyber" />
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass p-6">
                <div className="text-xs font-mono uppercase text-cyber">
                  Africa Coverage
                </div>

                <div className="mt-4 h-56">
                  <AfricaMap />
                </div>
              </div>
            </div>
          </section>

          {/* EXISTING MODULES */}

          <section className="space-y-4">
            <SectionHeading
              title="Threat Center"
              sub="Live attacks and response operations"
            />

            <ThreatFeed />
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="Security Testing"
              sub="Vulnerability management"
            />

            <Vulnerabilities />
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="Infrastructure Health"
              sub="System monitoring"
            />

            <HealthMonitor />
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="Threat Intelligence"
              sub="AI powered intelligence analysis"
            />

            <ThreatIntel />
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="Reports"
              sub="Executive reporting and compliance"
            />

            <ReportsPanel />
          </section>

          <section className="space-y-4">
            <SectionHeading
              title="AI Assistant"
              sub="Security analyst assistant"
            />

            <AIAssistant />
          </section>

          <footer
            className="
border-t
border-border
pt-6
pb-2
text-center
"
          >
            <p
              className="
font-mono
text-[10px]
uppercase
tracking-widest
text-muted-foreground
"
            >
              BLVCK CYBER + BLVCK SHIELD AI SOC PLATFORM
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
      <span className="h-4 w-1 rounded bg-primary" />

      <div>
        <h2
          className="
text-lg
font-semibold
"
        >
          {title}
        </h2>

        <p
          className="
text-xs
text-muted-foreground
"
        >
          {sub}
        </p>
      </div>
    </div>
  )
}
