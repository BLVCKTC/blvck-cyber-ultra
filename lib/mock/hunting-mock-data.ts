// src/lib/mock/hunting-mock-data.ts

export const MITRE_TACTICS = [
  'Initial Access',
  'Execution',
  'Persistence',
  'Privilege Escalation',
  'Defense Evasion',
  'Credential Access',
  'Discovery',
  'Lateral Movement',
  'Collection',
  'Command and Control',
  'Exfiltration',
  'Impact',
] as const

/**
 * Keep this Severity type aligned with:
 * src/lib/threat-data.ts
 *
 * critical -> Critical
 * high     -> High
 * warning  -> Medium
 * info     -> Low
 */
export type Severity = 'critical' | 'high' | 'warning' | 'info'

export const IOC_SAMPLES = [
  {
    type: 'ip',
    value: '45.132.192.14',
    hits: 128,
    first: '2h ago',
    country: 'Russia',
    tags: ['c2', 'cobalt-strike'],
  },
  {
    type: 'hash',
    value: 'a1b2c3d4e5f6789...',
    hits: 42,
    first: '6h ago',
    country: 'China',
    tags: ['lockbit', 'loader'],
  },
  {
    type: 'domain',
    value: 'sec-update-mail[.]cc',
    hits: 316,
    first: '1d ago',
    country: 'N/A',
    tags: ['phishing', 'banking'],
  },
  {
    type: 'url',
    value: 'hxxps://ng-payslip[.]top/login.php',
    hits: 89,
    first: '4h ago',
    country: 'N/A',
    tags: ['credential-theft'],
  },
]

export const SIGMA_RULES = [
  {
    id: 'SIG-0421',
    name: 'Suspicious PowerShell base64 execution',
    tactic: 'Execution',
    severity: 'high' as const,
    hits: 14,
  },
  {
    id: 'SIG-0512',
    name: 'New service installed by non-admin',
    tactic: 'Persistence',
    severity: 'warning' as const,
    hits: 5,
  },
  {
    id: 'SIG-0733',
    name: 'Credential dump via LSASS access',
    tactic: 'Credential Access',
    severity: 'critical' as const,
    hits: 2,
  },
  {
    id: 'SIG-0844',
    name: 'DNS tunneling pattern detected',
    tactic: 'Command & Control',
    severity: 'high' as const,
    hits: 8,
  },
  {
    id: 'SIG-0901',
    name: 'Impossible travel login',
    tactic: 'Initial Access',
    severity: 'warning' as const,
    hits: 21,
  },
]

export const YARA_SAMPLE = `rule LockBit_Loader {
  meta:
    author = "BLVCK CYBER"
    description = "Detects LockBit 3.0 loader variant"
  strings:
    $s1 = "lockbit_bl3ck.exe" ascii wide
    $s2 = { 4D 5A 90 00 03 00 ?? ?? 04 }
    $s3 = "restore-my-files.txt" ascii
  condition:
    uint16(0) == 0x5A4D and 2 of them
}`

export const AI_ASSIST_SUGGESTIONS = [
  'Find suspicious activity from finance department',
  'Search for ransomware indicators (encryption + shadow copy behavior)',
  'Investigate potential credential abuse across AD logons',
  'Detect lateral movement using remote service creation',
]

export type EvidenceType =
  | 'authentication'
  | 'process'
  | 'network'
  | 'file'
  | 'scheduled_task'
  | 'yara'
  | 'sigma'
  | 'ioc'

export type MitreTechnique = {
  technique: string
  name: string
}

export type EvidenceItem = {
  id: string
  type: EvidenceType
  signal: string
  source: string
  time: string
  assets: string[]
  confidence: number
  mitre?: MitreTechnique[]
  severityHint?: Severity
  raw?: Record<string, unknown>
}

export type InvestigationStatus =
  | 'CREATED'
  | 'PLANNING'
  | 'RUNNING_QUERIES'
  | 'ANALYZING'
  | 'DONE'
  | 'FAILED'

export type Verdict = {
  label: string
  confidence: number
  risk: Severity
  rationale: string[]
}

export type RecommendedAction = {
  id: string
  label: string
  impact: 'Critical' | 'High' | 'Warning' | 'Info'
}

export type InvestigationCase = {
  id: string
  title: string
  createdAt: string
  status: InvestigationStatus
  severity: Severity
  verdict?: Verdict

  plan: {
    objective: string
    steps: string[]

    queriesToRun: {
      id: string
      title: string
      query: string
      engine: 'Elastic' | 'Splunk' | 'Wazuh' | 'Sentinel' | 'OpenSearch'
    }[]
  }

  timeline: {
    time: string
    event: string
  }[]

  evidence: EvidenceItem[]

  mitreCoverage: MitreTechnique[]

  recommendedActions: RecommendedAction[]

  notes?: string
}

export const INITIAL_INVESTIGATIONS: InvestigationCase[] = [
  {
    id: 'HUNT-2026-0042',

    title: 'Suspicious PowerShell activity (finance)',

    createdAt: 'Today 09:02',

    status: 'DONE',

    severity: 'critical',

    plan: {
      objective:
        'Identify suspicious execution patterns consistent with payload staging and possible persistence.',

      steps: [
        'Search for encoded PowerShell and abnormal parent/child chains',
        'Check for scheduled task creation and service installation',
        'Correlate with external C2 indicators and suspicious download events',
        'Map evidence to MITRE ATT&CK techniques and produce a verdict',
      ],

      queriesToRun: [
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
          title: 'External connections shortly after execution',
          engine: 'OpenSearch',
          query: 'event.category:network AND destination.ip:("45.132.192.14")',
        },
      ],
    },

    timeline: [
      {
        time: '09:01',
        event: 'Login from unusual country (FIN role) detected',
      },

      {
        time: '09:04',
        event: 'PowerShell encoded execution observed',
      },

      {
        time: '09:07',
        event: 'External IP connection to known C2',
      },

      {
        time: '09:10',
        event: 'New scheduled task created (persistence candidate)',
      },
    ],

    evidence: [
      {
        id: 'e1',
        type: 'process',
        signal: 'powershell.exe executed with encoded command',
        source: 'EDR',
        time: '09:04',
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
        time: '09:07',
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
        time: '09:10',
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
    ],

    mitreCoverage: [
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
    ],

    recommendedActions: [
      {
        id: 'a1',
        label: 'Isolate host: FIN-PC-04',
        impact: 'High',
      },

      {
        id: 'a2',
        label: 'Triage persistence: remove scheduled task + verify changes',
        impact: 'High',
      },

      {
        id: 'a3',
        label: 'Block/rotate C2 indicators and rotate affected credentials',
        impact: 'Critical',
      },
    ],

    verdict: {
      label: 'Possible in-progress intrusion with execution + C2 + persistence',

      confidence: 94,

      risk: 'critical',

      rationale: [
        'Encoded PowerShell strongly indicates payload execution',
        'C2 contact aligns with known hostile infrastructure',
        'Scheduled task creation suggests persistence behavior',
      ],
    },
  },

  {
    id: 'HUNT-2026-0041',

    title: 'IOC spike investigation (credential theft indicators)',

    createdAt: 'Yesterday 17:21',

    status: 'DONE',

    severity: 'high',

    plan: {
      objective:
        'Determine whether credential theft indicators correlate with suspicious auth and execution chains.',

      steps: [
        'Search for auth events correlated with suspicious domains/URLs',
        'Check for follow-up process execution on affected endpoints',
        'Map detections to MITRE techniques and produce a verdict',
      ],

      queriesToRun: [
        {
          id: 'q1',
          title: 'Auth events following suspicious URL click',
          engine: 'Splunk',
          query: 'index=auth event.action=login AND user.domain="N/A"',
        },

        {
          id: 'q2',
          title: 'Follow-up process execution',
          engine: 'Elastic',
          query:
            'event.category:process AND process.command_line:("rundll32" OR "regsvr32")',
        },
      ],
    },

    timeline: [
      {
        time: '17:25',
        event: 'Suspicious auth attempt correlated to phishing domain',
      },

      {
        time: '17:31',
        event: 'Follow-up execution observed on endpoint',
      },
    ],

    evidence: [
      {
        id: 'e1',
        type: 'authentication',
        signal:
          'Login event correlated to credential-theft indicator URL behavior',
        source: 'SIEM/Auth',
        time: '17:25',
        assets: ['FIN-LAPTOP-02'],
        confidence: 86,
        mitre: [
          {
            technique: 'T1566.002',
            name: 'Spearphishing Link',
          },
        ],
        severityHint: 'high',
      },
    ],

    mitreCoverage: [
      {
        technique: 'T1566.002',
        name: 'Spearphishing Link',
      },
    ],

    recommendedActions: [
      {
        id: 'a1',
        label: 'Review recent logins for FIN-LAPTOP-02',
        impact: 'Critical',
      },

      {
        id: 'a2',
        label: 'Reset credentials for impacted accounts',
        impact: 'High',
      },
    ],

    verdict: {
      label:
        'Likely phishing-to-credential-access attempt (needs endpoint triage)',

      confidence: 87,

      risk: 'high',

      rationale: [
        'Auth correlation to phishing infrastructure',
        'Process activity present after auth chain',
      ],
    },
  },
]
