// Deterministic, credible SOC mock data for the BLVCK CYBER core workflow.
// No Math.random / Date.now at module scope so SSR and client markup match.

export type Severity = 'critical' | 'high' | 'warning' | 'info'

export const severityLabel: Record<Severity, string> = {
  critical: 'Critical',
  high: 'High',
  warning: 'Medium',
  info: 'Low',
}

export const severityRank: Record<Severity, number> = {
  critical: 0,
  high: 1,
  warning: 2,
  info: 3,
}

/* ---------------------------------- KPIs --------------------------------- */

export interface Kpi {
  key: string
  label: string
  value: string
  delta: string
  trend: 'up' | 'down' | 'flat'
  // whether an upward movement is good (true) or bad (false)
  goodWhenUp: boolean
  sub: string
}

export const kpis: Kpi[] = [
  {
    key: 'open-alerts',
    label: 'Open alerts',
    value: '38',
    delta: '+6',
    trend: 'up',
    goodWhenUp: false,
    sub: '4 critical · 11 high',
  },
  {
    key: 'active-incidents',
    label: 'Active incidents',
    value: '5',
    delta: '+1',
    trend: 'up',
    goodWhenUp: false,
    sub: '1 P1 · 2 P2',
  },
  {
    key: 'mttr',
    label: 'Mean time to respond',
    value: '11m',
    delta: '-3m',
    trend: 'down',
    goodWhenUp: false,
    sub: '30-day rolling average',
  },
  {
    key: 'coverage',
    label: 'Detection coverage',
    value: '92%',
    delta: '+2%',
    trend: 'up',
    goodWhenUp: true,
    sub: 'MITRE ATT&CK techniques',
  },
]

/* ------------------------------ Alert volume ----------------------------- */

export const alertVolume = [
  { time: '00:00', alerts: 21, escalated: 2 },
  { time: '03:00', alerts: 16, escalated: 1 },
  { time: '06:00', alerts: 28, escalated: 3 },
  { time: '09:00', alerts: 54, escalated: 6 },
  { time: '12:00', alerts: 71, escalated: 9 },
  { time: '15:00', alerts: 63, escalated: 7 },
  { time: '18:00', alerts: 44, escalated: 4 },
  { time: '21:00', alerts: 33, escalated: 3 },
]

export const severityBreakdown: { severity: Severity; count: number }[] = [
  { severity: 'critical', count: 4 },
  { severity: 'high', count: 11 },
  { severity: 'warning', count: 15 },
  { severity: 'info', count: 8 },
]

/* --------------------------- Detection sources --------------------------- */

export const detectionSources = [
  { name: 'EDR — endpoint', value: 34 },
  { name: 'Network IDS', value: 22 },
  { name: 'Identity / SSO', value: 18 },
  { name: 'Cloud posture', value: 14 },
  { name: 'Email gateway', value: 12 },
]

/* --------------------------------- Alerts -------------------------------- */

export type AlertStatus =
  | 'new'
  | 'investigating'
  | 'contained'
  | 'resolved'
  | 'false_positive'

export const alertStatusLabel: Record<AlertStatus, string> = {
  new: 'New',
  investigating: 'Investigating',
  contained: 'Contained',
  resolved: 'Resolved',
  false_positive: 'False positive',
}

export interface MitreRef {
  tactic: string
  techniqueId: string
  techniqueName: string
}

export interface ChainStep {
  label: string
  detail: string
  at: string
  status: 'observed' | 'blocked' | 'pending'
}

export interface Evidence {
  id: string
  kind: 'process' | 'network' | 'file' | 'identity' | 'log'
  label: string
  value: string
  at: string
}

export interface SocAlert {
  id: string
  title: string
  severity: Severity
  status: AlertStatus
  tactic: string
  source: string
  asset: string
  entity: string
  detectedAt: string
  confidence: number
  assignee: string | null
  description: string
  mitre: MitreRef[]
  chain: ChainStep[]
  evidence: Evidence[]
  aiSummary: string
  aiAssessment: string
  recommendedActions: { label: string; kind: 'contain' | 'investigate' | 'notify' }[]
  relatedIncidentId?: string
}

export const alerts: SocAlert[] = [
  {
    id: 'ALRT-4821',
    title: 'Ransomware pre-encryption behavior on finance endpoint',
    severity: 'critical',
    status: 'investigating',
    tactic: 'Impact',
    source: 'EDR — CrowdStrike',
    asset: 'FIN-WKS-0473',
    entity: 'akin.obi@corp',
    detectedAt: '2m ago',
    confidence: 97,
    assignee: 'T2 · N. Mensah',
    description:
      'Rapid enumeration and modification of user documents combined with shadow-copy deletion, consistent with the staging phase of a ransomware payload.',
    mitre: [
      { tactic: 'Impact', techniqueId: 'T1486', techniqueName: 'Data Encrypted for Impact' },
      { tactic: 'Impact', techniqueId: 'T1490', techniqueName: 'Inhibit System Recovery' },
      { tactic: 'Execution', techniqueId: 'T1059', techniqueName: 'Command and Scripting Interpreter' },
    ],
    chain: [
      { label: 'Initial access', detail: 'Malicious macro opened from email attachment', at: '18m ago', status: 'observed' },
      { label: 'Execution', detail: 'powershell.exe spawned encoded command', at: '14m ago', status: 'observed' },
      { label: 'Defense evasion', detail: 'vssadmin delete shadows /all', at: '4m ago', status: 'blocked' },
      { label: 'Impact', detail: 'Bulk file rename in \\Users\\Documents', at: '2m ago', status: 'pending' },
    ],
    evidence: [
      { id: 'e1', kind: 'process', label: 'Process', value: 'powershell.exe -enc SQBFAF…', at: '14m ago' },
      { id: 'e2', kind: 'file', label: 'Command', value: 'vssadmin.exe delete shadows /all /quiet', at: '4m ago' },
      { id: 'e3', kind: 'network', label: 'C2 beacon', value: '45.155.205.233:443 (blocklist)', at: '9m ago' },
      { id: 'e4', kind: 'identity', label: 'User', value: 'akin.obi@corp · non-admin', at: '18m ago' },
    ],
    aiSummary:
      'High-confidence ransomware staging. Shadow-copy deletion was blocked by the tamper-protection policy, but file modification is ongoing. Host is still online.',
    aiAssessment:
      'Isolating FIN-WKS-0473 now prevents lateral movement to the finance file share. The parent email has 3 other recipients who should be checked.',
    recommendedActions: [
      { label: 'Isolate host', kind: 'contain' },
      { label: 'Kill powershell process tree', kind: 'contain' },
      { label: 'Sweep recipients of parent email', kind: 'investigate' },
      { label: 'Notify incident commander', kind: 'notify' },
    ],
    relatedIncidentId: 'INC-2098',
  },
  {
    id: 'ALRT-4817',
    title: 'Impossible-travel sign-in for privileged account',
    severity: 'high',
    status: 'new',
    tactic: 'Initial Access',
    source: 'Identity — Entra ID',
    asset: 'sso.corp',
    entity: 'grace.n@corp',
    detectedAt: '9m ago',
    confidence: 88,
    assignee: null,
    description:
      'Successful MFA sign-in from Lagos followed 22 minutes later by a sign-in from Kyiv — a physically impossible transit for the same session token.',
    mitre: [
      { tactic: 'Initial Access', techniqueId: 'T1078', techniqueName: 'Valid Accounts' },
      { tactic: 'Credential Access', techniqueId: 'T1621', techniqueName: 'MFA Request Generation' },
    ],
    chain: [
      { label: 'Valid sign-in', detail: 'Lagos, NG · trusted device', at: '31m ago', status: 'observed' },
      { label: 'MFA fatigue', detail: '9 push notifications in 4 minutes', at: '26m ago', status: 'observed' },
      { label: 'Anomalous sign-in', detail: 'Kyiv, UA · new device', at: '9m ago', status: 'observed' },
    ],
    evidence: [
      { id: 'e1', kind: 'identity', label: 'Account', value: 'grace.n@corp · Global Admin', at: '9m ago' },
      { id: 'e2', kind: 'network', label: 'Source IP', value: '176.36.241.10 (Kyiv, UA)', at: '9m ago' },
      { id: 'e3', kind: 'log', label: 'MFA', value: '9 push prompts, 1 approved', at: '26m ago' },
    ],
    aiSummary:
      'Pattern matches MFA-fatigue account takeover. The approved push after 8 denials suggests the user relented under pressure.',
    aiAssessment:
      'Revoking active sessions and forcing re-authentication will evict the attacker. Consider temporary conditional-access lock on the account.',
    recommendedActions: [
      { label: 'Revoke all sessions', kind: 'contain' },
      { label: 'Force password reset', kind: 'contain' },
      { label: 'Review admin activity since 09:00', kind: 'investigate' },
    ],
  },
  {
    id: 'ALRT-4809',
    title: 'Outbound data transfer to unrecognized storage bucket',
    severity: 'high',
    status: 'investigating',
    tactic: 'Exfiltration',
    source: 'Cloud posture — AWS',
    asset: 's3://corp-analytics',
    entity: 'svc-etl',
    detectedAt: '24m ago',
    confidence: 82,
    assignee: 'T2 · N. Mensah',
    description:
      '2.4 GB copied from an internal analytics bucket to an external S3 bucket outside the organization within a 6-minute window.',
    mitre: [
      { tactic: 'Exfiltration', techniqueId: 'T1537', techniqueName: 'Transfer Data to Cloud Account' },
      { tactic: 'Collection', techniqueId: 'T1530', techniqueName: 'Data from Cloud Storage' },
    ],
    chain: [
      { label: 'Credential use', detail: 'svc-etl key used from EC2 outside VPC', at: '41m ago', status: 'observed' },
      { label: 'Collection', detail: 'ListObjects across 3 prefixes', at: '32m ago', status: 'observed' },
      { label: 'Exfiltration', detail: '2.4 GB copied to external bucket', at: '24m ago', status: 'observed' },
    ],
    evidence: [
      { id: 'e1', kind: 'identity', label: 'Principal', value: 'svc-etl (access key AKIA…7Q2)', at: '41m ago' },
      { id: 'e2', kind: 'network', label: 'Destination', value: 's3://xfer-9931 (external acct)', at: '24m ago' },
      { id: 'e3', kind: 'log', label: 'CloudTrail', value: 'CopyObject × 1,184', at: '24m ago' },
    ],
    aiSummary:
      'Service-account key is being used from an unexpected location. Volume and destination indicate deliberate exfiltration rather than a misconfigured job.',
    aiAssessment:
      'Disabling the access key stops the transfer immediately. The key has not rotated in 384 days — rotate on remediation.',
    recommendedActions: [
      { label: 'Disable access key', kind: 'contain' },
      { label: 'Block destination bucket', kind: 'contain' },
      { label: 'Trace key usage 24h', kind: 'investigate' },
    ],
    relatedIncidentId: 'INC-2097',
  },
  {
    id: 'ALRT-4802',
    title: 'Brute-force against internet-facing VPN portal',
    severity: 'warning',
    status: 'contained',
    tactic: 'Credential Access',
    source: 'Network IDS — Suricata',
    asset: 'vpn-gw-02',
    entity: '185.220.101.44',
    detectedAt: '48m ago',
    confidence: 76,
    assignee: 'T1 · Automation',
    description:
      '3,900 failed authentication attempts across 210 usernames from a single Tor exit node. Auto-blocked at the WAF after threshold.',
    mitre: [
      { tactic: 'Credential Access', techniqueId: 'T1110', techniqueName: 'Brute Force' },
    ],
    chain: [
      { label: 'Recon', detail: 'Portal fingerprinting probes', at: '1h ago', status: 'observed' },
      { label: 'Brute force', detail: '3,900 attempts / 210 users', at: '52m ago', status: 'observed' },
      { label: 'Auto-containment', detail: 'Source IP blocked at WAF', at: '48m ago', status: 'blocked' },
    ],
    evidence: [
      { id: 'e1', kind: 'network', label: 'Source', value: '185.220.101.44 (Tor exit)', at: '52m ago' },
      { id: 'e2', kind: 'log', label: 'Attempts', value: '3,900 failed / 0 success', at: '48m ago' },
    ],
    aiSummary:
      'Opportunistic credential spraying. No successful authentication observed; WAF containment held.',
    aiAssessment:
      'No action required beyond confirming the block. Consider geo-fencing the VPN portal to reduce noise.',
    recommendedActions: [
      { label: 'Confirm WAF block', kind: 'investigate' },
      { label: 'Add to threat-intel blocklist', kind: 'contain' },
    ],
  },
  {
    id: 'ALRT-4795',
    title: 'Suspicious OAuth consent grant to third-party app',
    severity: 'warning',
    status: 'new',
    tactic: 'Persistence',
    source: 'Identity — Entra ID',
    asset: 'sso.corp',
    entity: 'dayo.a@corp',
    detectedAt: '1h ago',
    confidence: 71,
    assignee: null,
    description:
      'A user granted an unverified third-party application mailbox.read and offline_access permissions — a common mailbox-persistence technique.',
    mitre: [
      { tactic: 'Persistence', techniqueId: 'T1098', techniqueName: 'Account Manipulation' },
    ],
    chain: [
      { label: 'Consent phishing', detail: 'Link to attacker OAuth app', at: '1h ago', status: 'observed' },
      { label: 'Grant', detail: 'mailbox.read + offline_access', at: '1h ago', status: 'observed' },
    ],
    evidence: [
      { id: 'e1', kind: 'identity', label: 'App', value: 'DocuSyncPro (unverified)', at: '1h ago' },
      { id: 'e2', kind: 'log', label: 'Scopes', value: 'Mail.Read, offline_access', at: '1h ago' },
    ],
    aiSummary:
      'Consent-phishing pattern. The app is unverified and requests persistent mailbox access.',
    aiAssessment:
      'Revoke the grant and remove the enterprise app. Check for inbox rules created after the grant.',
    recommendedActions: [
      { label: 'Revoke OAuth grant', kind: 'contain' },
      { label: 'Audit inbox rules', kind: 'investigate' },
    ],
  },
  {
    id: 'ALRT-4788',
    title: 'Port scan from internal host to server subnet',
    severity: 'info',
    status: 'resolved',
    tactic: 'Discovery',
    source: 'Network IDS — Suricata',
    asset: 'ENG-WKS-0210',
    entity: '10.4.12.88',
    detectedAt: '2h ago',
    confidence: 64,
    assignee: 'T1 · K. Diallo',
    description:
      'Sequential TCP SYN scan across the 10.4.20.0/24 server subnet. Traced to an authorized vulnerability scan.',
    mitre: [
      { tactic: 'Discovery', techniqueId: 'T1046', techniqueName: 'Network Service Discovery' },
    ],
    chain: [
      { label: 'Scan detected', detail: 'SYN sweep 10.4.20.0/24', at: '2h ago', status: 'observed' },
      { label: 'Attribution', detail: 'Matches Nessus scan window', at: '1h ago', status: 'observed' },
    ],
    evidence: [
      { id: 'e1', kind: 'network', label: 'Source', value: '10.4.12.88 (scan-eng-01)', at: '2h ago' },
      { id: 'e2', kind: 'log', label: 'Change ticket', value: 'CHG-5521 approved', at: '2h ago' },
    ],
    aiSummary: 'Benign. Activity aligns with an approved authenticated vulnerability scan.',
    aiAssessment: 'Closed as expected. No further action.',
    recommendedActions: [{ label: 'Close as benign', kind: 'investigate' }],
  },
]

/* ------------------------------- Incidents ------------------------------- */

export type IncidentStatus = 'open' | 'investigating' | 'contained' | 'resolved'
export type Priority = 'P1' | 'P2' | 'P3' | 'P4'

export const incidentStatusLabel: Record<IncidentStatus, string> = {
  open: 'Open',
  investigating: 'Investigating',
  contained: 'Contained',
  resolved: 'Resolved',
}

export interface IncidentEvent {
  at: string
  actor: string
  text: string
}

export interface Incident {
  id: string
  title: string
  severity: Severity
  status: IncidentStatus
  priority: Priority
  openedAt: string
  updatedAt: string
  owner: string
  alertCount: number
  assets: string[]
  tactics: string[]
  summary: string
  timeline: IncidentEvent[]
}

export const incidents: Incident[] = [
  {
    id: 'INC-2098',
    title: 'Ransomware staging on finance workstation',
    severity: 'critical',
    status: 'investigating',
    priority: 'P1',
    openedAt: '18m ago',
    updatedAt: '2m ago',
    owner: 'N. Mensah',
    alertCount: 4,
    assets: ['FIN-WKS-0473', 'fin-fileshare-01'],
    tactics: ['Initial Access', 'Execution', 'Impact'],
    summary:
      'A phishing attachment led to PowerShell execution and shadow-copy deletion on a finance workstation. Encryption behavior detected; host isolation in progress.',
    timeline: [
      { at: '18m ago', actor: 'Detection', text: 'Alert ALRT-4821 raised by EDR' },
      { at: '15m ago', actor: 'N. Mensah', text: 'Acknowledged and opened incident' },
      { at: '9m ago', actor: 'System', text: 'C2 beacon to 45.155.205.233 blocked' },
      { at: '4m ago', actor: 'Policy', text: 'Shadow-copy deletion blocked by tamper protection' },
      { at: '2m ago', actor: 'N. Mensah', text: 'Initiated host isolation for FIN-WKS-0473' },
    ],
  },
  {
    id: 'INC-2097',
    title: 'Cloud data exfiltration via service account',
    severity: 'high',
    status: 'investigating',
    priority: 'P2',
    openedAt: '41m ago',
    updatedAt: '20m ago',
    owner: 'N. Mensah',
    alertCount: 2,
    assets: ['s3://corp-analytics', 'svc-etl'],
    tactics: ['Collection', 'Exfiltration'],
    summary:
      'A long-lived service-account key was used from outside the VPC to copy 2.4 GB of analytics data to an external bucket. Key disabled; scope of access under review.',
    timeline: [
      { at: '41m ago', actor: 'Detection', text: 'Anomalous key usage flagged by cloud posture' },
      { at: '32m ago', actor: 'Detection', text: 'Bulk ListObjects across 3 prefixes' },
      { at: '24m ago', actor: 'Detection', text: 'Alert ALRT-4809 raised on exfiltration' },
      { at: '20m ago', actor: 'N. Mensah', text: 'Disabled access key AKIA…7Q2' },
    ],
  },
  {
    id: 'INC-2094',
    title: 'MFA-fatigue attempt on admin account',
    severity: 'high',
    status: 'contained',
    priority: 'P2',
    openedAt: '2h ago',
    updatedAt: '1h ago',
    owner: 'K. Diallo',
    alertCount: 1,
    assets: ['sso.corp'],
    tactics: ['Initial Access', 'Credential Access'],
    summary:
      'Repeated MFA push prompts against a Global Admin account. Sessions revoked and credentials reset before privileged actions were observed.',
    timeline: [
      { at: '2h ago', actor: 'Detection', text: 'Impossible-travel sign-in detected' },
      { at: '1h 40m ago', actor: 'K. Diallo', text: 'Revoked all active sessions' },
      { at: '1h ago', actor: 'K. Diallo', text: 'Forced password reset; contained' },
    ],
  },
  {
    id: 'INC-2089',
    title: 'Recurring brute-force from Tor exit nodes',
    severity: 'warning',
    status: 'resolved',
    priority: 'P3',
    openedAt: '1d ago',
    updatedAt: '20h ago',
    owner: 'Automation',
    alertCount: 6,
    assets: ['vpn-gw-02'],
    tactics: ['Credential Access'],
    summary:
      'Sustained credential spraying against the VPN portal from rotating Tor exits. Auto-contained by WAF; geo-fencing recommended and applied.',
    timeline: [
      { at: '1d ago', actor: 'Detection', text: 'Threshold breach on VPN auth failures' },
      { at: '23h ago', actor: 'Automation', text: 'Blocked 14 source IPs at WAF' },
      { at: '20h ago', actor: 'K. Diallo', text: 'Applied geo-fence; resolved' },
    ],
  },
  {
    id: 'INC-2081',
    title: 'Malware dropper quarantined on engineering laptop',
    severity: 'warning',
    status: 'resolved',
    priority: 'P3',
    openedAt: '2d ago',
    updatedAt: '2d ago',
    owner: 'K. Diallo',
    alertCount: 3,
    assets: ['ENG-WKS-0118'],
    tactics: ['Execution', 'Defense Evasion'],
    summary:
      'A trojan dropper was quarantined by EDR before execution. Host scanned clean; no persistence or network activity observed.',
    timeline: [
      { at: '2d ago', actor: 'Detection', text: 'EDR quarantined dropper on write' },
      { at: '2d ago', actor: 'K. Diallo', text: 'Full scan clean; resolved' },
    ],
  },
]

/* ---------------------------- Vulnerabilities ---------------------------- */

export type VulnStatus = 'open' | 'in_progress' | 'remediated' | 'accepted'

export const vulnStatusLabel: Record<VulnStatus, string> = {
  open: 'Open',
  in_progress: 'In progress',
  remediated: 'Remediated',
  accepted: 'Risk accepted',
}

export interface Vulnerability {
  id: string
  cve: string
  title: string
  severity: Severity
  cvss: number
  epss: number // exploit prediction score 0-1
  status: VulnStatus
  asset: string
  assetGroup: string
  exploitAvailable: boolean
  exposedToInternet: boolean
  discovered: string
  due: string
  fix: string
}

export const vulnerabilities: Vulnerability[] = [
  {
    id: 'V-3041',
    cve: 'CVE-2024-3094',
    title: 'XZ Utils backdoor in SSH authentication path',
    severity: 'critical',
    cvss: 10.0,
    epss: 0.94,
    status: 'in_progress',
    asset: 'vpn-gw-02',
    assetGroup: 'Network edge',
    exploitAvailable: true,
    exposedToInternet: true,
    discovered: '2h ago',
    due: 'Today',
    fix: 'Downgrade xz to 5.4.6; rebuild affected images',
  },
  {
    id: 'V-3038',
    cve: 'CVE-2024-21762',
    title: 'FortiOS out-of-bounds write leading to RCE',
    severity: 'critical',
    cvss: 9.8,
    epss: 0.9,
    status: 'open',
    asset: 'web-gw-lb-01',
    assetGroup: 'Network edge',
    exploitAvailable: true,
    exposedToInternet: true,
    discovered: '6h ago',
    due: 'Tomorrow',
    fix: 'Apply FortiOS 7.4.3 patch',
  },
  {
    id: 'V-3032',
    cve: 'CVE-2023-4863',
    title: 'Heap buffer overflow in WebP image decoder',
    severity: 'critical',
    cvss: 9.6,
    epss: 0.71,
    status: 'open',
    asset: 'customer-portal',
    assetGroup: 'Customer-facing',
    exploitAvailable: true,
    exposedToInternet: true,
    discovered: '1d ago',
    due: '3 days',
    fix: 'Update libwebp and redeploy portal',
  },
  {
    id: 'V-3025',
    cve: 'CVE-2023-34362',
    title: 'MOVEit Transfer SQL injection',
    severity: 'high',
    cvss: 8.8,
    epss: 0.66,
    status: 'in_progress',
    asset: 'fin-fileshare-01',
    assetGroup: 'Finance',
    exploitAvailable: true,
    exposedToInternet: false,
    discovered: '1d ago',
    due: '5 days',
    fix: 'Apply vendor hotfix; rotate service credentials',
  },
  {
    id: 'V-3019',
    cve: 'CVE-2023-46604',
    title: 'Apache ActiveMQ remote code execution',
    severity: 'high',
    cvss: 8.1,
    epss: 0.58,
    status: 'open',
    asset: 'mail-relay-02',
    assetGroup: 'Messaging',
    exploitAvailable: true,
    exposedToInternet: false,
    discovered: '4d ago',
    due: '7 days',
    fix: 'Upgrade ActiveMQ to 5.18.3',
  },
  {
    id: 'V-3007',
    cve: 'CVE-2024-1709',
    title: 'ConnectWise ScreenConnect authentication bypass',
    severity: 'high',
    cvss: 8.4,
    epss: 0.62,
    status: 'remediated',
    asset: 'auth-service',
    assetGroup: 'Identity',
    exploitAvailable: false,
    exposedToInternet: false,
    discovered: '3d ago',
    due: 'Closed',
    fix: 'Patched to 23.9.8',
  },
  {
    id: 'V-2994',
    cve: 'CVE-2024-27198',
    title: 'TeamCity authentication bypass',
    severity: 'warning',
    cvss: 6.5,
    epss: 0.34,
    status: 'in_progress',
    asset: 'k8s-prod-cluster',
    assetGroup: 'Platform',
    exploitAvailable: false,
    exposedToInternet: false,
    discovered: '5d ago',
    due: '10 days',
    fix: 'Upgrade TeamCity build server',
  },
  {
    id: 'V-2981',
    cve: 'CVE-2023-38831',
    title: 'WinRAR arbitrary code execution via crafted archive',
    severity: 'warning',
    cvss: 6.1,
    epss: 0.22,
    status: 'accepted',
    asset: 'hr-fileshare',
    assetGroup: 'HR',
    exploitAvailable: false,
    exposedToInternet: false,
    discovered: '1w ago',
    due: 'Accepted',
    fix: 'Compensating control: attachment sandboxing',
  },
]

/* ------------------------------ Aggregations ----------------------------- */

export function countBy<T, K extends string>(
  items: T[],
  key: (t: T) => K,
): Record<K, number> {
  return items.reduce(
    (acc, item) => {
      const k = key(item)
      acc[k] = (acc[k] ?? 0) + 1
      return acc
    },
    {} as Record<K, number>,
  )
}

export function getAlert(id: string) {
  return alerts.find((a) => a.id === id)
}

export function getIncident(id: string) {
  return incidents.find((i) => i.id === id)
}
