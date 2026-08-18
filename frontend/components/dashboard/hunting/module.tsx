'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  Search,
  Sparkles,
  Target,
  Code2,
  BookOpen,
  Grid3x3,
  Clock,
  Play,
  Save,
  ChevronRight,
  Plus,
  FileText,
} from 'lucide-react'

import { StatCard } from '@/components/shell/stat-card'
import { SeverityBadge } from '@/components/threat-intel/severity-badge'

import {
  AI_ASSIST_SUGGESTIONS,
  IOC_SAMPLES,
  INITIAL_INVESTIGATIONS,
  MITRE_TACTICS,
  SIGMA_RULES,
  YARA_SAMPLE,
  type EvidenceItem,
  type InvestigationCase,
  type InvestigationStatus,
  type MitreTechnique,
  type Severity,
} from '@/lib/mock/hunting-mock-data'

type Tab =
  | 'assistant'
  | 'investigations'
  | 'queries'
  | 'iocs'
  | 'yara'
  | 'sigma'
  | 'attack'
  | 'timeline'
  | 'reports'

function severityTone(sev: Severity) {
  if (sev === 'critical') return 'cyber'
  if (sev === 'high') return 'warning'
  if (sev === 'warning') return 'success'
  return 'cyber'
}

function statusLabel(s: InvestigationStatus) {
  switch (s) {
    case 'CREATED':
      return 'CREATED'
    case 'PLANNING':
      return 'AI PLANNING'
    case 'RUNNING_QUERIES':
      return 'RUNNING QUERIES'
    case 'ANALYZING':
      return 'AI ANALYZING'
    case 'DONE':
      return 'DONE'
    case 'FAILED':
      return 'FAILED'
    default:
      return s
  }
}

function genInvestigationId(existing: InvestigationCase[]) {
  const max = existing
    .map((x) => parseInt(x.id.replace(/\D/g, ''), 10))
    .filter((n) => !Number.isNaN(n))
    .reduce((a, b) => Math.max(a, b), 42)
  const next = Math.max(43, max + 1)
  return `HUNT-2026-${String(next).padStart(4, '0')}`
}

export function HuntingModule() {
  const [tab, setTab] = useState<Tab>('assistant')

  // --- Assistant / investigations state ---
  const [investigations, setInvestigations] = useState<InvestigationCase[]>(
    () => INITIAL_INVESTIGATIONS,
  )
  const [activeInvestigationId, setActiveInvestigationId] = useState<string>(
    INITIAL_INVESTIGATIONS[0]?.id ?? '',
  )
  const activeInvestigation = useMemo(
    () => investigations.find((x) => x.id === activeInvestigationId) ?? null,
    [investigations, activeInvestigationId],
  )

  const [chatInput, setChatInput] = useState('')
  const [assistantLog, setAssistantLog] = useState<
    { id: string; role: 'analyst' | 'ai'; content: string }[]
  >([
    {
      id: 'm1',
      role: 'ai',
      content:
        'BLVCK AI HUNTING ASSISTANT ready.\n\nTell me what you want to investigate (e.g., “Find suspicious activity from finance department”).',
    },
  ])

  // --- Existing capability states (kept, but demoted under case-driven workflow) ---
  const [query, setQuery] = useState(
    'index=edr sourcetype=process EventCode=4688 CommandLine="*base64*"',
  )
  const [ioc, setIoc] = useState('')
  const [yara, setYara] = useState(YARA_SAMPLE)

  const iocRows = useMemo(
    () =>
      ioc ? IOC_SAMPLES.filter((r) => r.value.includes(ioc)) : IOC_SAMPLES,
    [ioc],
  )

  // --- Auto-switch to investigations center when a case is created ---
  useEffect(() => {
    if (tab === 'investigations' && activeInvestigationId) {
      // no-op: just to emphasize UX intent
    }
  }, [tab, activeInvestigationId])

  function pushAssistant(role: 'analyst' | 'ai', content: string) {
    setAssistantLog((prev) => [
      ...prev,
      { id: `${Date.now()}-${prev.length}`, role, content },
    ])
  }

  function buildCaseFromPrompt(prompt: string): InvestigationCase {
    const id = genInvestigationId(investigations)
    const nowLabel = 'Today 10:12'

    const financeBias = /finance/i.test(prompt)
    const ransomwareBias = /ransomware|encrypt|encryption/i.test(prompt)
    const credentialBias = /credential|kerberoast|lsass|password/i.test(prompt)
    const lateralBias = /lateral|remote service|psexec|wmi/i.test(prompt)

    const severity: Severity = ransomwareBias
      ? 'critical'
      : credentialBias || financeBias
        ? 'high'
        : 'warning'

    const planObjective = financeBias
      ? 'Investigate possible compromise of finance endpoints and determine whether execution + persistence is active.'
      : ransomwareBias
        ? 'Assess ransomware indicators and determine if encryption behavior is present.'
        : credentialBias
          ? 'Identify credential access signals and assess whether accounts are being compromised.'
          : lateralBias
            ? 'Detect lateral movement attempts and identify affected hosts and likely technique.'
            : 'Investigate suspicious activity patterns and correlate signals into a coherent attack story.'

    const mitre: MitreTechnique[] = ransomwareBias
      ? [
          {
            technique: 'T1486',
            name: 'Data Encrypted for Impact',
          },
          {
            technique: 'T1053.005',
            name: 'Scheduled Task',
          },
        ]
      : credentialBias
        ? [
            {
              technique: 'T1003.001',
              name: 'OS Credential Dumping: LSASS Memory',
            },
            {
              technique: 'T1059.001',
              name: 'PowerShell',
            },
          ]
        : lateralBias
          ? [
              {
                technique: 'T1021.002',
                name: 'Remote Services: SMB/Windows Admin Shares',
              },
              {
                technique: 'T1053.005',
                name: 'Scheduled Task',
              },
            ]
          : [
              {
                technique: 'T1059.001',
                name: 'PowerShell',
              },
              {
                technique: 'T1053.005',
                name: 'Scheduled Task',
              },
              {
                technique: 'T1071.001',
                name: 'Web Protocols',
              },
            ]

    const evidence: EvidenceItem[] = financeBias
      ? [
          {
            id: 'e1',
            type: 'process',
            signal: 'powershell.exe executed with encoded command',
            source: 'EDR',
            time: '10:13',
            assets: ['FIN-PC-04'],
            confidence: 92,
            mitre: [
              {
                technique: 'T1059.001',
                name: 'PowerShell',
              },
            ],
            severityHint: 'high',
          },
          {
            id: 'e2',
            type: 'network',
            signal: 'Connection to known C2 IP (45.132.192.14)',
            source: 'Proxy/Netflow',
            time: '10:15',
            assets: ['FIN-PC-04'],
            confidence: 89,
            mitre: [
              {
                technique: 'T1071.001',
                name: 'Web Protocols',
              },
            ],
            severityHint: 'critical',
          },
          {
            id: 'e3',
            type: 'scheduled_task',
            signal: 'schtasks.exe used to create persistence scheduled task',
            source: 'EDR',
            time: '10:17',
            assets: ['FIN-PC-04'],
            confidence: 91,
            mitre: [
              {
                technique: 'T1053.005',
                name: 'Scheduled Task',
              },
            ],
            severityHint: 'critical',
          },
        ]
      : ransomwareBias
        ? [
            {
              id: 'e1',
              type: 'file',
              signal:
                'mass file modifications consistent with encryption behavior',
              source: 'EDR/File Telemetry',
              time: '10:08',
              assets: ['FIN-NAS-01'],
              confidence: 86,
              mitre: [
                {
                  technique: 'T1486',
                  name: 'Data Encrypted for Impact',
                },
              ],
              severityHint: 'critical',
            },
          ]
        : credentialBias
          ? [
              {
                id: 'e1',
                type: 'process',
                signal:
                  'Suspicious LSASS memory access indicative of credential dumping',
                source: 'EDR',
                time: '10:19',
                assets: ['HR-LAPTOP-02'],
                confidence: 90,
                mitre: [
                  {
                    technique: 'T1003.001',
                    name: 'OS Credential Dumping: LSASS Memory',
                  },
                ],
                severityHint: 'high',
              },
            ]
          : [
              {
                id: 'e1',
                type: 'network',
                signal: 'Remote service connection spike across multiple hosts',
                source: 'Netflow',
                time: '10:20',
                assets: ['ENG-SRV-03', 'ENG-SRV-04'],
                confidence: 82,
                mitre: [
                  {
                    technique: 'T1021.002',
                    name: 'Remote Services: SMB/Windows Admin Shares',
                  },
                ],
                severityHint: 'warning',
              },
            ]

    const timeline: { time: string; event: string }[] = financeBias
      ? [
          {
            time: '10:12',
            event: 'Investigation started by assistant',
          },
          {
            time: '10:13',
            event: 'Encoded PowerShell execution detected',
          },
          {
            time: '10:15',
            event: 'External C2 connection observed',
          },
          {
            time: '10:17',
            event: 'Scheduled task created (persistence candidate)',
          },
        ]
      : [
          {
            time: '10:12',
            event: 'Investigation started by assistant',
          },
          {
            time: '10:18',
            event: 'Suspicious behavior mapped to MITRE techniques',
          },
        ]

    /*
     * IMPORTANT:
     * RecommendedAction expects:
     *
     * "Critical" | "High" | "Warning" | "Info"
     *
     * The explicit type prevents TypeScript from widening
     * impact to a generic string.
     */
    const recommendedActions: InvestigationCase['recommendedActions'] =
      severity === 'critical'
        ? [
            {
              id: 'a1',
              label: 'Isolate impacted assets immediately',
              impact: 'Critical',
            },
            {
              id: 'a2',
              label: 'Eradicate persistence + reset credentials',
              impact: 'Critical',
            },
            {
              id: 'a3',
              label: 'Block IOCs and monitor for reinfection',
              impact: 'High',
            },
          ]
        : [
            {
              id: 'a1',
              label: 'Triage affected endpoints and validate IOC hits',
              impact: 'High',
            },
            {
              id: 'a2',
              label: 'Review recent authentication activity',
              impact: 'Warning',
            },
            {
              id: 'a3',
              label: 'Deploy targeted detection rules (Sigma/YARA)',
              impact: 'Info',
            },
          ]

    const queriesToRun: InvestigationCase['plan']['queriesToRun'] = financeBias
      ? [
          {
            id: 'q1',
            title: 'Encoded PowerShell execution',
            engine: 'Elastic',
            query: 'event.category:process AND powershell.command_line:*enc*',
          },
          {
            id: 'q2',
            title: 'Scheduled task creation',
            engine: 'Elastic',
            query:
              'event.category:process AND process.name:("schtasks.exe" OR "taskeng.exe")',
          },
          {
            id: 'q3',
            title: 'External C2 correlation',
            engine: 'OpenSearch',
            query:
              'event.category:network AND destination.ip:("45.132.192.14")',
          },
        ]
      : [
          {
            id: 'q1',
            title: 'Core suspicious behavior search',
            engine: 'Splunk',
            query:
              'index=edr action=process_start AND action_field="suspicious"',
          },
          {
            id: 'q2',
            title: 'Enrichment correlation',
            engine: 'Elastic',
            query:
              'event.category:authentication OR event.category:network OR event.category:file',
          },
        ]

    return {
      id,
      title: prompt.length > 42 ? `${prompt.slice(0, 42)}…` : prompt,
      createdAt: nowLabel,
      status: 'CREATED',
      severity,

      plan: {
        objective: planObjective,

        steps: [
          'Generate a structured investigation plan',
          'Execute generated queries and collect evidence',
          'Analyze evidence to produce verdict + confidence',
          'Map findings to MITRE ATT&CK and recommend next actions',
        ],

        queriesToRun,
      },

      timeline,
      evidence,
      mitreCoverage: mitre,
      recommendedActions,
    }
  }
  function simulateInvestigationLifecycle(caseId: string) {
    const stages: InvestigationStatus[] = [
      'PLANNING',
      'RUNNING_QUERIES',
      'ANALYZING',
      'DONE',
    ]

    setInvestigations((prev) =>
      prev.map((c) =>
        c.id === caseId
          ? {
              ...c,
              status: 'PLANNING',
              timeline: [
                { time: '10:12', event: 'AI planning investigation steps…' },
                ...c.timeline,
              ],
            }
          : c,
      ),
    )

    const timers = [
      setTimeout(() => {
        setInvestigations((prev) =>
          prev.map((c) =>
            c.id === caseId
              ? {
                  ...c,
                  status: 'RUNNING_QUERIES',
                  timeline: [
                    {
                      time: '10:13',
                      event: 'Queries dispatched to log engines…',
                    },
                    ...c.timeline,
                  ],
                }
              : c,
          ),
        )
      }, 600),
      setTimeout(() => {
        setInvestigations((prev) =>
          prev.map((c) =>
            c.id === caseId
              ? {
                  ...c,
                  status: 'ANALYZING',
                  timeline: [
                    {
                      time: '10:15',
                      event: 'Evidence correlation in progress…',
                    },
                    ...c.timeline,
                  ],
                }
              : c,
          ),
        )
      }, 1300),
      setTimeout(() => {
        setInvestigations((prev) =>
          prev.map((c) => {
            if (c.id !== caseId) return c

            const confidence =
              c.severity === 'critical' ? 94 : c.severity === 'high' ? 90 : 82

            const verdict = {
              label:
                c.severity === 'critical'
                  ? 'In-progress intrusion suspected (execution + C2 + persistence evidence)'
                  : c.severity === 'high'
                    ? 'Likely compromise behavior; additional triage recommended'
                    : 'Suspicious activity found; validate scope and intent',
              confidence,
              risk: c.severity,
              rationale:
                c.severity === 'critical'
                  ? [
                      'Multiple correlated signals aligned with execution and persistence behavior',
                      'External indicator association increases likelihood of active threat',
                    ]
                  : [
                      'Evidence clusters to plausible attack behavior but lacks full kill-chain coverage',
                    ],
            }

            return {
              ...c,
              status: 'DONE',
              verdict,
              timeline: [
                { time: '10:17', event: 'Verdict produced by AI analyst' },
                ...c.timeline,
              ],
            }
          }),
        )
      }, 1900),
    ]

    return () => timers.forEach((t) => clearTimeout(t))
  }

  function onSendChat() {
    const prompt = chatInput.trim()
    if (!prompt) return

    pushAssistant('analyst', prompt)
    setChatInput('')

    // AI response + create a new investigation record (mock)
    const newCase = buildCaseFromPrompt(prompt)
    const caseId = newCase.id

    pushAssistant(
      'ai',
      [
        `I will investigate this like a case file.`,
        ``,
        `✓ Objective: ${newCase.plan.objective}`,
        `✓ Plan steps: ${newCase.plan.steps.length}`,
        `✓ Evidence collection: ${newCase.evidence.length} signals (mock)`,
        ``,
        `Investigation started…`,
      ].join('\n'),
    )

    setInvestigations((prev) => [newCase, ...prev])
    setActiveInvestigationId(caseId)
    setTab('investigations')

    // simulate progression to DONE
    simulateInvestigationLifecycle(caseId)
  }

  // --- Derived UI bits for active case ---
  const evidenceSummary = useMemo(() => {
    if (!activeInvestigation) return { events: 0, assets: 0, runtime: '0.42s' }
    const assets = new Set<string>()
    activeInvestigation.evidence.forEach((e) =>
      e.assets.forEach((a) => assets.add(a)),
    )
    return {
      events: activeInvestigation.evidence.length,
      assets: assets.size,
      runtime: activeInvestigation.status === 'DONE' ? '0.42s' : '—',
    }
  }, [activeInvestigation])

  const activeMitreNames = useMemo(() => {
    if (!activeInvestigation) return []
    return activeInvestigation.mitreCoverage.map(
      (m) => `${m.technique} ${m.name}`,
    )
  }, [activeInvestigation])

  function renderInvestigationList() {
    return (
      <div className="glass p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-muted-foreground">
              INVESTIGATION CENTER
            </div>
            <div className="text-2xl font-display font-bold text-cyber tabular mt-1">
              Cases
            </div>
          </div>
          <button
            onClick={() => setTab('assistant')}
            className="bg-cyber text-black px-4 py-2.5 rounded text-xs font-mono font-semibold inline-flex items-center gap-2"
          >
            <Plus className="h-3.5 w-3.5" />
            New investigation
          </button>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          {investigations.map((c) => {
            const selected = c.id === activeInvestigationId
            return (
              <button
                key={c.id}
                onClick={() => {
                  setActiveInvestigationId(c.id)
                  setTab('investigations')
                }}
                className={`text-left rounded-xl border p-4 transition ${
                  selected
                    ? 'border-cyber bg-cyber/10'
                    : 'border-white/10 bg-black/20 hover:bg-white/5'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                      {c.id}
                    </div>
                    <div className="mt-1 font-semibold">{c.title}</div>
                    <div className="text-xs text-muted-foreground font-mono mt-1">
                      {c.createdAt}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <SeverityBadge severity={c.severity} />
                    <div className="text-[10px] font-mono uppercase text-muted-foreground">
                      {statusLabel(c.status)}
                    </div>
                  </div>
                </div>

                <div className="mt-3 grid grid-cols-3 gap-2 text-xs font-mono">
                  <div>
                    <div className="text-[10px] uppercase text-muted-foreground">
                      Evidence
                    </div>
                    <div className="text-cyber font-semibold tabular">
                      {c.evidence.length}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase text-muted-foreground">
                      Mitre
                    </div>
                    <div className="text-cyber font-semibold tabular">
                      {c.mitreCoverage.length}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase text-muted-foreground">
                      Verdict
                    </div>
                    <div className="font-semibold tabular">
                      {c.verdict ? `${c.verdict.confidence}%` : '—'}
                    </div>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {activeInvestigation && (
          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-xs font-mono text-muted-foreground">
                  ACTIVE CASE
                </div>
                <div className="text-xl font-display font-bold text-cyber mt-1">
                  {activeInvestigation.id}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {activeInvestigation.title}
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap justify-end">
                <div className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-black/30 px-3 py-2">
                  <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                    {statusLabel(activeInvestigation.status)}
                  </span>
                </div>
                <button
                  className="border border-white/10 px-3 py-2 rounded-lg text-xs font-mono hover:bg-white/5"
                  onClick={() => setTab('timeline')}
                >
                  Evidence timeline
                </button>
                <button
                  className="bg-cyber text-black px-3 py-2 rounded-lg text-xs font-mono font-semibold"
                  onClick={() => setTab('reports')}
                >
                  <FileText className="h-3.5 w-3.5 inline-block mr-2 -mt-0.5" />
                  Generate report
                </button>
              </div>
            </div>

            <div className="mt-4 grid lg:grid-cols-3 gap-4">
              <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Plan objective
                </div>
                <div className="mt-2 text-sm">
                  {activeInvestigation.plan.objective}
                </div>
                <div className="mt-3 flex gap-2 flex-wrap">
                  {activeInvestigation.recommendedActions
                    .slice(0, 3)
                    .map((a) => (
                      <span
                        key={a.id}
                        className="inline-flex items-center gap-2 text-xs font-mono bg-white/5 border border-white/10 rounded-full px-3 py-1"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-cyber" />
                        {a.label}
                      </span>
                    ))}
                </div>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-4 lg:col-span-2">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                    Verdict
                  </div>
                  <div className="text-xs font-mono text-muted-foreground">
                    Confidence:{' '}
                    <span className="text-cyber font-semibold tabular">
                      {activeInvestigation.verdict
                        ? `${activeInvestigation.verdict.confidence}%`
                        : '—'}
                    </span>
                  </div>
                </div>

                {activeInvestigation.verdict ? (
                  <>
                    <div className="mt-2 flex items-start justify-between gap-4">
                      <div>
                        <div className="text-lg font-semibold">
                          {activeInvestigation.verdict.label}
                        </div>
                        <div className="mt-2 space-y-1">
                          {activeInvestigation.verdict.rationale.map((r, i) => (
                            <div
                              key={i}
                              className="text-sm text-muted-foreground"
                            >
                              • {r}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <SeverityBadge
                          severity={activeInvestigation.verdict.risk}
                        />
                        <button
                          className="text-xs font-mono text-cyber hover:underline"
                          onClick={() => setTab('assistant')}
                        >
                          Continue investigation →
                        </button>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/5">
                      <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        MITRE support
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {activeInvestigation.mitreCoverage.map((m) => (
                          <span
                            key={m.technique}
                            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-xs font-mono"
                          >
                            {m.technique} {m.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="mt-3 text-sm text-muted-foreground">
                    AI analyst is producing the verdict…
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  function renderAssistant() {
    const selectedCaseSeverity = activeInvestigation?.severity ?? 'warning'
    return (
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 glass p-5 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                BLVCK AI HUNTING ASSISTANT
              </div>
              <h2 className="text-2xl font-display font-bold text-cyber mt-1">
                AI security investigation
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                Investigations are case-based: chat → plan → evidence timeline →
                verdict → report.
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <SeverityBadge severity={selectedCaseSeverity} />
              <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                Active: {activeInvestigation?.id ?? '—'}
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/25 p-4 h-[420px] overflow-auto space-y-3">
            {assistantLog.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === 'ai' ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-[88%] whitespace-pre-wrap rounded-xl border p-3 text-sm font-mono ${
                    m.role === 'ai'
                      ? 'bg-black/40 border-white/10 text-cyber'
                      : 'bg-cyber/15 border-cyber/40 text-foreground'
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onSendChat()
              }}
              placeholder='e.g., "Find suspicious activity from finance department"'
              className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm font-mono"
            />
            <button
              onClick={onSendChat}
              className="bg-cyber text-black px-4 py-2.5 rounded-lg text-xs font-mono font-semibold inline-flex items-center gap-2"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Investigate
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-3 pt-2 border-t border-white/5">
            <div className="glass p-4">
              <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                AI Investigation prompts
              </div>
              <div className="mt-3 grid gap-2">
                {AI_ASSIST_SUGGESTIONS.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => setChatInput(s)}
                    className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="glass p-4">
              <div className="flex items-center gap-2 text-cyber">
                <Target className="h-4 w-4" />
                <span className="text-xs font-mono uppercase tracking-widest">
                  Case snapshot
                </span>
              </div>

              <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                <div>
                  <div className="text-[10px] font-mono uppercase text-muted-foreground">
                    Evidence
                  </div>
                  <div className="text-2xl font-display font-bold text-cyber tabular">
                    {evidenceSummary.events}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-muted-foreground">
                    Assets
                  </div>
                  <div className="text-2xl font-display font-bold tabular">
                    {evidenceSummary.assets}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-muted-foreground">
                    Runtime
                  </div>
                  <div className="text-2xl font-display font-bold text-success tabular">
                    {evidenceSummary.runtime}
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  MITRE coverage
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(activeInvestigation?.mitreCoverage ?? [])
                    .slice(0, 3)
                    .map((m) => (
                      <span
                        key={m.technique}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-xs font-mono"
                      >
                        {m.technique}
                      </span>
                    ))}
                </div>

                <div className="mt-3 text-xs text-muted-foreground font-mono">
                  Tip: open{' '}
                  <button
                    className="text-cyber hover:underline"
                    onClick={() => setTab('timeline')}
                  >
                    Evidence Timeline
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="glass p-5 space-y-4">
          <div className="flex items-center gap-2 text-cyber">
            <Search className="h-4 w-4" />
            <span className="text-xs font-mono uppercase tracking-widest">
              Fast actions
            </span>
          </div>

          <div className="space-y-2">
            <button
              onClick={() => setTab('investigations')}
              className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition"
            >
              Open Investigation Center →
            </button>
            <button
              onClick={() => setTab('iocs')}
              className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition"
            >
              IOC Intelligence →
            </button>
            <button
              onClick={() => setTab('attack')}
              className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition"
            >
              MITRE ATT&CK coverage →
            </button>
          </div>

          <div className="pt-3 border-t border-white/5">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              What the assistant does
            </div>
            <div className="mt-2 text-sm text-muted-foreground space-y-2">
              <div>• Creates an investigation case (not just a query)</div>
              <div>• Produces evidence → verdict → actions (mock workflow)</div>
              <div>
                • Keeps everything inside the case for reports + history
              </div>
            </div>
          </div>

          {activeInvestigation && (
            <div className="pt-3 border-t border-white/5">
              <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                Active case status
              </div>
              <div className="mt-2 flex items-center justify-between gap-3">
                <div className="text-sm font-semibold">
                  {activeInvestigation.id}
                </div>
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  {statusLabel(activeInvestigation.status)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  function renderQueriesCapability() {
    return (
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 glass p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono text-muted-foreground">
              CASE QUERIES // BLVCK-QL
            </div>
            <div className="flex gap-2">
              <select className="bg-black/40 border border-white/10 text-xs px-2 py-1 rounded font-mono">
                <option>Last 24 hours</option>
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>Custom range</option>
              </select>
              <button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold inline-flex items-center gap-1.5">
                <Play className="h-3 w-3" />
                Run
              </button>
              <button className="border border-white/10 px-3 py-1.5 rounded text-xs font-mono inline-flex items-center gap-1.5">
                <Save className="h-3 w-3" />
                Save
              </button>
            </div>
          </div>

          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={6}
            className="w-full bg-black/60 border border-white/10 rounded p-3 font-mono text-xs text-cyber leading-relaxed"
          />

          <div className="grid md:grid-cols-3 gap-3 pt-2 border-t border-white/5">
            <div>
              <div className="text-[10px] font-mono uppercase text-muted-foreground">
                Events matched
              </div>
              <div className="text-2xl font-display font-bold text-cyber tabular">
                1,284
              </div>
            </div>
            <div>
              <div className="text-[10px] font-mono uppercase text-muted-foreground">
                Assets involved
              </div>
              <div className="text-2xl font-display font-bold tabular">47</div>
            </div>
            <div>
              <div className="text-[10px] font-mono uppercase text-muted-foreground">
                Runtime
              </div>
              <div className="text-2xl font-display font-bold text-success tabular">
                0.42s
              </div>
            </div>
          </div>
        </div>

        <div className="glass p-5 space-y-3">
          <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
            AI suggestions
          </div>
          {AI_ASSIST_SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => setQuery(s)}
              className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition"
            >
              {s}
            </button>
          ))}
          <div className="pt-3 border-t border-white/5 text-xs text-muted-foreground font-mono">
            Note: In BLVCK AI HUNTING, these are supportive—evidence and verdict
            live in Investigation Workspace.
          </div>
        </div>
      </div>
    )
  }

  function renderIOCs() {
    return (
      <div className="glass p-5 space-y-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              value={ioc}
              onChange={(e) => setIoc(e.target.value)}
              placeholder="Search IP, hash (MD5/SHA1/SHA256), domain or URL…"
              className="w-full bg-black/40 border border-white/10 rounded pl-9 pr-3 py-2.5 text-sm font-mono"
            />
          </div>
          <button className="bg-cyber text-black px-4 py-2.5 rounded text-xs font-mono font-semibold">
            Enrich all
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              <tr className="border-b border-white/5">
                <th className="text-left py-2">Type</th>
                <th className="text-left py-2">Indicator</th>
                <th className="text-left py-2">Hits</th>
                <th className="text-left py-2">First seen</th>
                <th className="text-left py-2">Origin</th>
                <th className="text-left py-2">Tags</th>
              </tr>
            </thead>
            <tbody className="font-mono text-xs">
              {iocRows.map((r) => (
                <tr
                  key={r.value}
                  className="border-b border-white/5 hover:bg-white/5"
                >
                  <td className="py-3">
                    <span className="inline-block bg-cyber/15 text-cyber px-2 py-0.5 rounded uppercase text-[10px]">
                      {r.type}
                    </span>
                  </td>
                  <td className="py-3 text-cyber">{r.value}</td>
                  <td className="py-3 tabular">{r.hits}</td>
                  <td className="py-3 text-muted-foreground">{r.first}</td>
                  <td className="py-3">{r.country}</td>
                  <td className="py-3 flex gap-1 flex-wrap">
                    {r.tags.map((t) => (
                      <span
                        key={t}
                        className="bg-white/5 px-2 py-0.5 rounded text-[10px]"
                      >
                        {t}
                      </span>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  function renderYara() {
    return (
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 glass p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs font-mono text-muted-foreground">
              YARA RULE // LockBit_Loader.yar
            </div>
            <div className="flex gap-2">
              <button className="border border-white/10 px-3 py-1.5 rounded text-xs font-mono">
                Test sample
              </button>
              <button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold">
                Deploy
              </button>
            </div>
          </div>
          <textarea
            value={yara}
            onChange={(e) => setYara(e.target.value)}
            rows={16}
            className="w-full bg-black/60 border border-white/10 rounded p-3 font-mono text-xs text-success leading-relaxed"
          />
        </div>

        <div className="glass p-5 space-y-3">
          <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Test results
          </div>
          <div className="p-3 rounded bg-success/10 border border-success/30 text-xs font-mono text-success">
            ✓ Rule compiled successfully
          </div>
          <div className="p-3 rounded bg-warning/10 border border-warning/30 text-xs font-mono text-warning">
            ⚠ 3 samples in vault match this rule
          </div>
          <div className="pt-3 border-t border-white/5">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">
              Rule stats
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Deployed rules</span>
                <span className="text-cyber tabular">1,204</span>
              </div>
              <div className="flex justify-between">
                <span>Detections (7d)</span>
                <span className="text-warning tabular">89</span>
              </div>
              <div className="flex justify-between">
                <span>False positives</span>
                <span className="text-success tabular">0.4%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  function renderSigma() {
    return (
      <div className="glass p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              <tr className="border-b border-white/5">
                <th className="text-left py-2">Rule ID</th>
                <th className="text-left py-2">Name</th>
                <th className="text-left py-2">MITRE Tactic</th>
                <th className="text-left py-2">Severity</th>
                <th className="text-left py-2">Hits (24h)</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {SIGMA_RULES.map((r) => (
                <tr
                  key={r.id}
                  className="border-b border-white/5 hover:bg-white/5"
                >
                  <td className="py-3 font-mono text-xs text-cyber">{r.id}</td>
                  <td className="py-3">{r.name}</td>
                  <td className="py-3 text-xs font-mono text-muted-foreground">
                    {r.tactic}
                  </td>
                  <td className="py-3">
                    <SeverityBadge severity={r.severity} />
                  </td>
                  <td className="py-3 font-mono tabular">{r.hits}</td>
                  <td className="py-3 text-right">
                    <button className="text-xs font-mono text-cyber hover:underline">
                      Deploy →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  function renderMitre() {
    return (
      <div className="glass p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-xs font-mono text-muted-foreground">
            MITRE ATT&CK NAVIGATOR — Enterprise Matrix
          </div>
          <div className="flex items-center gap-3 text-[10px] font-mono uppercase text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              <span className="h-3 w-3 rounded-sm bg-success/60" />
              Covered
            </span>
            <span className="inline-flex items-center gap-1">
              <span className="h-3 w-3 rounded-sm bg-warning/60" />
              Partial
            </span>
            <span className="inline-flex items-center gap-1">
              <span className="h-3 w-3 rounded-sm bg-white/10" />
              Gap
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
          {MITRE_TACTICS.map((t, i) => {
            const cov = (i * 13) % 100
            const color =
              cov > 75
                ? 'bg-success/40 border-success/60'
                : cov > 40
                  ? 'bg-warning/30 border-warning/50'
                  : 'bg-white/5 border-white/10'

            return (
              <div key={t} className={`rounded-lg border p-3 ${color}`}>
                <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                  TA{String(i + 1).padStart(4, '0')}
                </div>
                <div className="text-sm font-semibold mt-1">{t}</div>
                <div className="mt-2 flex items-center justify-between text-[10px] font-mono">
                  <span className="text-muted-foreground">Coverage</span>
                  <span className="tabular">{cov}%</span>
                </div>
                <div className="mt-1 h-1 bg-black/40 rounded overflow-hidden">
                  <div
                    className="h-full bg-cyber"
                    style={{ width: `${cov}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono pt-2 border-t border-white/5">
          <Clock className="h-3 w-3" /> Last sync with MITRE: 42 minutes ago
        </div>
      </div>
    )
  }

  function renderTimeline() {
    if (!activeInvestigation) {
      return (
        <div className="glass p-5 text-sm text-muted-foreground">
          No active case.
        </div>
      )
    }

    const evidence = activeInvestigation.evidence

    return (
      <div className="glass p-5 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              EVIDENCE TIMELINE
            </div>
            <div className="text-2xl font-display font-bold text-cyber mt-1">
              {activeInvestigation.id}
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {activeInvestigation.title}
            </div>
          </div>
          <button
            className="border border-white/10 px-3 py-2 rounded-lg text-xs font-mono hover:bg-white/5"
            onClick={() => setTab('reports')}
          >
            Generate report →
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              Attack story
            </div>
            <div className="mt-3 space-y-2">
              {activeInvestigation.timeline
                .slice()
                .reverse()
                .map((t, idx) => (
                  <div
                    key={`${t.time}-${idx}`}
                    className="flex items-start gap-3"
                  >
                    <div className="mt-0.5 h-2 w-2 rounded-full bg-cyber" />
                    <div className="flex-1">
                      <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        {t.time}
                      </div>
                      <div className="text-sm">{t.event}</div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              Evidence cards
            </div>
            <div className="mt-3 space-y-3">
              {evidence.map((e) => (
                <div
                  key={e.id}
                  className="rounded-lg border border-white/10 bg-black/30 p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        {e.type}
                      </div>
                      <div className="text-sm text-cyber font-semibold mt-1">
                        {e.signal}
                      </div>
                    </div>
                    <div className="text-[10px] font-mono uppercase text-muted-foreground">
                      {e.source}
                    </div>
                  </div>

                  <div className="mt-2 text-xs text-muted-foreground font-mono">
                    Time: <span className="text-foreground">{e.time}</span> •
                    Confidence:{' '}
                    <span className="text-cyber">{e.confidence}%</span>
                  </div>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {e.assets.map((a) => (
                      <span
                        key={a}
                        className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-[10px] font-mono"
                      >
                        {a}
                      </span>
                    ))}
                  </div>

                  {e.mitre && e.mitre.length > 0 && (
                    <div className="mt-2">
                      <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                        MITRE
                      </div>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {e.mitre.map((m) => (
                          <span
                            key={m.technique}
                            className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-[10px] font-mono"
                          >
                            {m.technique}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {evidence.length === 0 && (
                <div className="text-sm text-muted-foreground">
                  No evidence yet.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  function renderReports() {
    if (!activeInvestigation) {
      return (
        <div className="glass p-5 text-sm text-muted-foreground">
          No active case.
        </div>
      )
    }

    const v = activeInvestigation.verdict

    return (
      <div className="glass p-5 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              AI GENERATED REPORT
            </div>
            <div className="text-2xl font-display font-bold text-cyber mt-1">
              {activeInvestigation.id}
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {activeInvestigation.title}
            </div>
          </div>
          <button
            onClick={() => {
              // mock "generate"
              pushAssistant(
                'ai',
                `Report generated for ${activeInvestigation.id} (mock).`,
              )
            }}
            className="bg-cyber text-black px-4 py-2.5 rounded-lg text-xs font-mono font-semibold inline-flex items-center gap-2"
          >
            <FileText className="h-3.5 w-3.5" />
            Generate Report
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              Summary
            </div>
            <div className="mt-2 text-sm">
              BLVCK CYBER Threat Hunting Report
              <div className="text-muted-foreground mt-2">
                {v
                  ? `AI verdict: ${v.label}`
                  : 'AI is currently analyzing evidence and will produce a verdict shortly.'}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/5">
              <div className="grid md:grid-cols-2 gap-3">
                <div className="rounded-lg border border-white/10 bg-black/30 p-3">
                  <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                    Severity
                  </div>
                  <div className="mt-1">
                    <SeverityBadge severity={activeInvestigation.severity} />
                  </div>
                </div>
                <div className="rounded-lg border border-white/10 bg-black/30 p-3">
                  <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                    Confidence
                  </div>
                  <div className="mt-1 text-cyber font-mono font-semibold tabular">
                    {v ? `${v.confidence}%` : '—'}
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Affected assets
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {Array.from(
                    new Set(
                      activeInvestigation.evidence.flatMap((e) => e.assets),
                    ),
                  ).map((a) => (
                    <span
                      key={a}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-xs font-mono"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-4">
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  MITRE techniques
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {activeMitreNames.map((m) => (
                    <span
                      key={m}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-xs font-mono"
                    >
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              Recommendations
            </div>
            <div className="mt-3 space-y-2">
              {activeInvestigation.recommendedActions.map((a) => (
                <div
                  key={a.id}
                  className="rounded-lg border border-white/10 bg-black/30 p-3"
                >
                  <div className="text-sm font-semibold">{a.label}</div>
                  <div className="text-xs text-muted-foreground font-mono mt-1">
                    Impact: <span className="text-cyber">{a.impact}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-3 mt-3 border-t border-white/5 text-xs text-muted-foreground font-mono">
              Actions are mocked for now—hook these to your case response
              playbooks later.
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-black/20 p-4">
          <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Evidence list
          </div>
          <div className="mt-3 grid md:grid-cols-2 gap-3">
            {activeInvestigation.evidence.map((e) => (
              <div
                key={e.id}
                className="rounded-lg border border-white/10 bg-black/30 p-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                      {e.type}
                    </div>
                    <div className="text-sm text-cyber font-semibold mt-1">
                      {e.signal}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                      Time
                    </div>
                    <div className="text-xs font-mono">{e.time}</div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-muted-foreground font-mono">
                  Source: <span className="text-foreground">{e.source}</span> •
                  Confidence:{' '}
                  <span className="text-cyber tabular">{e.confidence}%</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {e.assets.map((a) => (
                    <span
                      key={a}
                      className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-[10px] font-mono"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              </div>
            ))}
            {activeInvestigation.evidence.length === 0 && (
              <div className="text-sm text-muted-foreground">No evidence.</div>
            )}
          </div>
        </div>
      </div>
    )
  }

  const tabs: { k: Tab; label: string; icon: React.ComponentType<any> }[] = [
    { k: 'assistant', label: 'AI Hunting Assistant', icon: Sparkles },
    { k: 'investigations', label: 'Investigation Center', icon: Target },
    { k: 'queries', label: 'Hunt Queries', icon: Code2 },
    { k: 'iocs', label: 'IOC Intelligence', icon: Search },
    { k: 'yara', label: 'YARA Rules', icon: Code2 },
    { k: 'sigma', label: 'Sigma Rules', icon: BookOpen },
    { k: 'attack', label: 'MITRE ATT&CK', icon: Grid3x3 },
    { k: 'timeline', label: 'Evidence Timeline', icon: Clock },
    { k: 'reports', label: 'Reports', icon: FileText as any },
  ]

  return (
    <>
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs font-mono uppercase tracking-widest text-cyber">
            HUNT.MODULE // v3.2
          </div>
          <h1 className="text-3xl font-display font-bold mt-1">
            AI Threat Investigation Platform
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Case-first workflow: chat → investigation workspace → evidence
            timeline → verdict & report.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="border border-white/10 rounded-lg px-3 py-2 text-xs font-mono hover:bg-white/5 inline-flex items-center gap-1.5">
            Import STIX
          </button>
          <button className="border border-white/10 rounded-lg px-3 py-2 text-xs font-mono hover:bg-white/5 inline-flex items-center gap-1.5">
            Export CSV
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
        <StatCard
          label="Active Hunts"
          value={investigations.filter((i) => i.status !== 'DONE').length}
          tone="cyber"
          icon={Target}
          change="+3 this week"
          trend="up"
          detail="AI-assisted investigations in progress"
        />
        <StatCard
          label="IOCs Tracked"
          value="18,412"
          tone="warning"
          icon={Search}
          change="+412 24h"
          trend="up"
          detail="Threat indicators monitored"
        />
        <StatCard
          label="Sigma Rules"
          value="2314"
          tone="success"
          icon={Code2}
          change="Auto-synced"
          trend="up"
          detail="Detection rules active"
        />
        <StatCard
          label="ATT&CK Coverage"
          value="86%"
          tone="cyber"
          icon={Grid3x3}
          change="+4% MoM"
          trend="up"
          detail="Enterprise techniques mapped"
        />
      </div>

      <div className="flex gap-1 flex-wrap border-b border-white/10 mt-4">
        {tabs.map((t) => {
          const Icon = t.icon
          const selected = tab === t.k
          return (
            <button
              key={t.k}
              onClick={() => setTab(t.k)}
              className={`px-4 py-2.5 text-xs font-mono uppercase tracking-widest inline-flex items-center gap-2 border-b-2 -mb-px transition
                ${selected ? 'border-cyber text-cyber' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            >
              <Icon className="h-3.5 w-3.5" />
              {t.label}
            </button>
          )
        })}
      </div>

      <div className="mt-4">
        {tab === 'assistant' && renderAssistant()}
        {tab === 'investigations' && renderInvestigationList()}
        {tab === 'queries' && renderQueriesCapability()}
        {tab === 'iocs' && renderIOCs()}
        {tab === 'yara' && renderYara()}
        {tab === 'sigma' && renderSigma()}
        {tab === 'attack' && renderMitre()}
        {tab === 'timeline' && renderTimeline()}
        {tab === 'reports' && renderReports()}
      </div>
    </>
  )
}
