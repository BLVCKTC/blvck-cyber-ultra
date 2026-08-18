// Central mock/seed data for the entire BLVCK CYBER platform.
import type { Organization } from '@/types/organization'

export const AFRICAN_COUNTRIES = [
  'Nigeria',
  'South Africa',
  'Kenya',
  'Egypt',
  'Ghana',
  'Morocco',
  'Ethiopia',
  'Tanzania',
  'Uganda',
  'Rwanda',
  'Senegal',
  'Ivory Coast',
  'Cameroon',
  'Zambia',
]

export const INDUSTRIES = [
  'Banking & Finance',
  'Government',
  'Healthcare',
  'Telecom',
  'Energy & Utilities',
  'Insurance',
  'Retail',
  'Manufacturing',
  'Education',
  'Logistics',
]

export const THREAT_TYPES = [
  'Ransomware',
  'Phishing',
  'Malware',
  'DDoS',
  'Zero-Day',
  'Botnet',
  'Insider Threat',
  'Data Exfiltration',
  'Cryptojacking',
  'Web Attack',
] as const

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
  'Command & Control',
  'Exfiltration',
  'Impact',
]

export type Severity = 'critical' | 'high' | 'medium' | 'low'

export interface ThreatEvent {
  id: string
  timestamp: string
  type: (typeof THREAT_TYPES)[number]
  severity: Severity
  country: string
  industry: string
  actor: string
  cve?: string
  mitreTactic: string
  description: string
  target: string
}

const ACTORS = [
  'APT-Silver',
  'Lazarus',
  'FIN7',
  'Turla',
  'SilentNight',
  'BlackBasta',
  'Cl0p',
  'LockBit',
  'Scattered Spider',
  'Kimsuky',
]

function rand<T>(a: T[]): T {
  return a[Math.floor(Math.random() * a.length)]
}
function pad(n: number) {
  return n.toString().padStart(2, '0')
}

let SEED = 1337
function seedRand() {
  SEED = (SEED * 9301 + 49297) % 233280
  return SEED / 233280
}
function srand<T>(a: T[]): T {
  return a[Math.floor(seedRand() * a.length)]
}
const SEV: Severity[] = ['critical', 'high', 'medium', 'low']

export function generateThreats(count = 60): ThreatEvent[] {
  const out: ThreatEvent[] = []
  const now = Date.now()
  for (let i = 0; i < count; i++) {
    const t = new Date(now - Math.floor(seedRand() * 1000 * 60 * 60 * 72))
    out.push({
      id: `THR-${(10000 + i).toString()}`,
      timestamp: t.toISOString(),
      type: srand(THREAT_TYPES as unknown as (typeof THREAT_TYPES)[number][]),
      severity: srand(SEV),
      country: srand(AFRICAN_COUNTRIES),
      industry: srand(INDUSTRIES),
      actor: srand(ACTORS),
      cve:
        seedRand() > 0.6
          ? `CVE-2025-${Math.floor(1000 + seedRand() * 9000)}`
          : undefined,
      mitreTactic: srand(MITRE_TACTICS),
      description: srand([
        'Anomalous outbound traffic to suspicious C2 server',
        'Credential stuffing attempt against admin portal',
        'Encrypted payload dropped via phishing attachment',
        'Lateral movement via SMB observed',
        'Privilege escalation exploit blocked by EDR',
        'Data exfiltration to unknown cloud storage',
        'Suspicious PowerShell invocation with obfuscation',
        'Ransomware indicator matched on file server',
      ]),
      target: srand([
        'mail.corp.local',
        'db-prod-03',
        'workstation-lagos-42',
        'api-gateway.finance',
        'ad-controller-01',
        'citrix-vda-14',
      ]),
    })
  }
  return out.sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1))
}

export const LIVE_TICKER_ITEMS = [
  'LockBit 4.0 targeting East African banks — 3 IOCs blocked',
  "New Android banking trojan 'AntSpider' detected in Kenya",
  'CVE-2025-4471 critical exploit active in the wild — patch now',
  'DDoS campaign against Nigerian telecom, 2.4 Tbps peak mitigated',
  'Phishing kit impersonating SARS in South Africa, 12k emails blocked',
  'Zero-day in enterprise VPN — Egyptian ministry advised',
  "Ransomware group 'Cl0p' claims Ghanaian retailer, negotiations underway",
  'Insider exfil detected at telco — 4.2 GB blocked at egress',
]

// SOC Demo scenarios
export interface Scenario {
  id: string
  name: string
  severity: Severity
  category: string
  summary: string
  attackChain: {
    phase: string
    tactic: string
    description: string
    timestamp: string
  }[]
  affected: { type: string; name: string }[]
  mitre: string[]
  rootCause: string
  recommendations: string[]
  recovery: string[]
  lessons: string[]
}

export const SCENARIOS: Scenario[] = [
  {
    id: 'ransomware',
    name: 'Ransomware Outbreak',
    severity: 'critical',
    category: 'Malware',
    summary:
      'LockBit 4.0 payload deployed via compromised RDP credentials, encrypted 47 file servers before AI containment triggered network isolation.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1078 Valid Accounts',
        description: 'Compromised admin RDP creds from dark web dump',
        timestamp: 'T-00:42:11',
      },
      {
        phase: 'Execution',
        tactic: 'T1059 Command & Scripting',
        description: 'PowerShell loader executed',
        timestamp: 'T-00:38:04',
      },
      {
        phase: 'Persistence',
        tactic: 'T1547 Boot Autostart',
        description: "Scheduled task created 'WindowsSecUpdate'",
        timestamp: 'T-00:35:22',
      },
      {
        phase: 'Privilege Escalation',
        tactic: 'T1068 Exploit for PE',
        description: 'PrintNightmare exploit invoked',
        timestamp: 'T-00:31:17',
      },
      {
        phase: 'Lateral Movement',
        tactic: 'T1021 Remote Services',
        description: 'SMB spread to 47 hosts',
        timestamp: 'T-00:22:03',
      },
      {
        phase: 'Impact',
        tactic: 'T1486 Data Encrypted for Impact',
        description: 'LockBit encryption started',
        timestamp: 'T-00:04:12',
      },
    ],
    affected: [
      { type: 'Server', name: 'fs-prod-01, fs-prod-02, fs-hr-03' },
      { type: 'Account', name: 'svc-backup, admin-rdp-01' },
      { type: 'Endpoint', name: '47 Windows workstations' },
    ],
    mitre: ['T1078', 'T1059.001', 'T1547.005', 'T1068', 'T1021.002', 'T1486'],
    rootCause:
      'Reused admin RDP credential exposed in a 2024 third-party breach and lack of MFA on RDP gateway.',
    recommendations: [
      'Enforce MFA on all remote access (RDP, VPN, admin consoles)',
      'Rotate all privileged credentials, invalidate active sessions',
      'Deploy application allow-listing on file servers',
      'Isolate backup infrastructure on separate network segment',
    ],
    recovery: [
      'Restore affected file servers from immutable backups (RPO 4h)',
      'Rebuild compromised endpoints from golden image',
      'Reset all Kerberos tickets (twice with 10h gap)',
      'Threat-hunt for dormant persistence across the estate',
    ],
    lessons: [
      'Credential hygiene monitoring must include third-party dumps',
      'RDP gateway required MFA six months ago per policy — not enforced',
      'Mean time to contain: 4m 12s — AI segmentation prevented ~$8M in damages',
    ],
  },
  {
    id: 'insider',
    name: 'Insider Threat / Data Exfil',
    severity: 'high',
    category: 'Insider',
    summary:
      'Departing employee attempted to exfiltrate 4.2 GB of customer PII to personal cloud storage. Blocked at egress by DLP-AI.',
    attackChain: [
      {
        phase: 'Discovery',
        tactic: 'T1083 File and Directory',
        description: 'Unusual browsing of CRM exports',
        timestamp: 'T-04:11:00',
      },
      {
        phase: 'Collection',
        tactic: 'T1074 Data Staged',
        description: 'Files staged in ~/Downloads/archive.zip',
        timestamp: 'T-01:22:00',
      },
      {
        phase: 'Exfiltration',
        tactic: 'T1567 Exfil to Cloud',
        description: 'Upload to personal Dropbox attempted',
        timestamp: 'T-00:00:32',
      },
    ],
    affected: [
      { type: 'Account', name: 'j.davies@corp' },
      { type: 'Data', name: 'CRM.customers (4.2 GB, 118k records)' },
    ],
    mitre: ['T1083', 'T1074.001', 'T1567.002'],
    rootCause:
      'Departing employee retained full CRM access during 30-day notice period.',
    recommendations: [
      'Immediately revoke access; preserve endpoint for forensics',
      'Implement JIT/JEA access with expiring grants tied to HR events',
      'Enable session recording on privileged data stores',
    ],
    recovery: [
      'Notify Data Protection Officer per POPIA/NDPR',
      'Rotate any credentials the user could access',
      'Legal hold on mailbox and endpoint',
    ],
    lessons: ['HR offboarding automation not integrated with IAM — fix in Q1'],
  },
  {
    id: 'phishing',
    name: 'Targeted Phishing Campaign',
    severity: 'high',
    category: 'Social Engineering',
    summary:
      'Business Email Compromise targeting finance team. 3 users clicked; AI-mail-guard sandboxed payload and blocked credential harvest.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1566 Phishing',
        description: 'Spearphish impersonating CFO',
        timestamp: 'T-00:18:00',
      },
      {
        phase: 'Credential Access',
        tactic: 'T1056 Input Capture',
        description: 'Fake M365 login page delivered',
        timestamp: 'T-00:12:00',
      },
    ],
    affected: [
      { type: 'Account', name: '3 finance dept users' },
      { type: 'Domain', name: 'cfo-secure-verify.co' },
    ],
    mitre: ['T1566.001', 'T1056.003'],
    rootCause:
      'SPF/DMARC configured p=none — spoofed emails passed authentication.',
    recommendations: [
      'Enforce DMARC p=reject',
      'Mandatory phishing simulation training',
      'FIDO2 keys for finance team',
    ],
    recovery: ['Force password reset + MFA re-enrollment for exposed users'],
    lessons: [
      'Users reported within 4 minutes — awareness training is working',
    ],
  },
  {
    id: 'database',
    name: 'Database Compromise',
    severity: 'critical',
    category: 'Application',
    summary:
      'SQL injection on legacy customer portal allowed unauthenticated data read. AI-WAF blocked 12,400 subsequent probes.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1190 Public-Facing App',
        description: 'SQLi in /portal/search endpoint',
        timestamp: 'T-02:41:00',
      },
      {
        phase: 'Discovery',
        tactic: 'T1082 System Info Discovery',
        description: 'Schema enumeration via UNION queries',
        timestamp: 'T-02:35:00',
      },
      {
        phase: 'Collection',
        tactic: 'T1005 Data from Local System',
        description: 'Dump of users table (partial)',
        timestamp: 'T-02:12:00',
      },
    ],
    affected: [
      { type: 'Database', name: 'portal-db-01.customers' },
      { type: 'Data', name: '~2,400 email + hashed password records' },
    ],
    mitre: ['T1190', 'T1082', 'T1005'],
    rootCause:
      'Legacy portal not covered by WAF; parameterized queries missing on /search endpoint.',
    recommendations: [
      'Emergency WAF coverage for all public apps',
      'Code audit of legacy .NET portal',
      'Force password reset for affected users',
    ],
    recovery: ['Rotate DB creds', 'Notify affected users within 72h per GDPR'],
    lessons: ['Attack surface inventory missed the legacy portal'],
  },
  {
    id: 'privesc',
    name: 'Privilege Escalation',
    severity: 'high',
    category: 'Endpoint',
    summary:
      'Standard user exploited unpatched Print Spooler vulnerability to gain SYSTEM. Blocked before lateral movement.',
    attackChain: [
      {
        phase: 'Execution',
        tactic: 'T1059 Command & Scripting',
        description: 'PowerShell payload launched',
        timestamp: 'T-00:07:00',
      },
      {
        phase: 'Privilege Escalation',
        tactic: 'T1068 Exploit for PE',
        description: 'PrintNightmare CVE-2021-34527',
        timestamp: 'T-00:05:00',
      },
    ],
    affected: [
      { type: 'Endpoint', name: 'ws-lagos-088' },
      { type: 'Account', name: 'a.johnson (standard user)' },
    ],
    mitre: ['T1059.001', 'T1068'],
    rootCause: 'Endpoint missed May patch cycle due to disabled auto-updates.',
    recommendations: [
      'Enforce patch SLA (7 days critical)',
      'Disable Print Spooler on non-print servers',
    ],
    recovery: ['Reimage endpoint', "Investigate user's recent activity"],
    lessons: [
      'Patch compliance dashboard flagged this host 42 days ago — no action taken',
    ],
  },
  {
    id: 'malware',
    name: 'Malware Infection',
    severity: 'medium',
    category: 'Endpoint',
    summary:
      'Emotet dropper delivered via macro-enabled document. AI-EDR quarantined before beacon established.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1566 Phishing',
        description: 'Invoice-themed .docm attachment',
        timestamp: 'T-00:03:00',
      },
      {
        phase: 'Execution',
        tactic: 'T1204 User Execution',
        description: 'Macro executed on open',
        timestamp: 'T-00:02:00',
      },
    ],
    affected: [{ type: 'Endpoint', name: 'ws-nairobi-201' }],
    mitre: ['T1566.001', 'T1204.002'],
    rootCause: 'Office macros allowed by default policy for finance team.',
    recommendations: ['Block macros from internet by group policy'],
    recovery: ['Quarantine complete, endpoint clean'],
    lessons: ['Macro policy exception no longer justified'],
  },
  {
    id: 'cloud',
    name: 'Cloud Misconfiguration Attack',
    severity: 'high',
    category: 'Cloud',
    summary:
      'Exposed S3 bucket with API keys discovered by scanner. Keys used to spin up 40 crypto miners before AI-CSPM revoked.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1078.004 Cloud Accounts',
        description: 'Public S3 with .env file',
        timestamp: 'T-01:15:00',
      },
      {
        phase: 'Impact',
        tactic: 'T1496 Resource Hijacking',
        description: '40 EC2 instances launched for XMRig',
        timestamp: 'T-00:40:00',
      },
    ],
    affected: [
      { type: 'Cloud', name: 'AWS account 4241-xxxx-9012' },
      { type: 'Data', name: 's3://data-lake-staging/*' },
    ],
    mitre: ['T1078.004', 'T1496'],
    rootCause: 'Developer committed .env to public bucket during migration.',
    recommendations: [
      'Enable S3 Block Public Access org-wide',
      'Secrets scanning in CI',
    ],
    recovery: [
      'Rotate all AWS keys',
      'Terminate rogue instances',
      'Bill impact ~$2,400',
    ],
    lessons: ['Onboarding checklist missing secrets-hygiene training'],
  },
  {
    id: 'webapp',
    name: 'Web Application Attack',
    severity: 'high',
    category: 'Application',
    summary:
      'Authentication bypass via JWT algorithm confusion. AI-WAF signature updated within 90s of first probe.',
    attackChain: [
      {
        phase: 'Initial Access',
        tactic: 'T1190 Public-Facing App',
        description: "JWT 'none' algorithm accepted",
        timestamp: 'T-00:22:00',
      },
      {
        phase: 'Credential Access',
        tactic: 'T1550 Alternate Auth Material',
        description: 'Forged admin token used',
        timestamp: 'T-00:19:00',
      },
    ],
    affected: [{ type: 'App', name: 'admin-portal.corp' }],
    mitre: ['T1190', 'T1550.001'],
    rootCause: "JWT library accepted 'none' algorithm in header.",
    recommendations: [
      'Pin allowed algorithms in JWT validation',
      'Add authZ tests to CI',
    ],
    recovery: ['Patch deployed, all admin sessions invalidated'],
    lessons: ['Third-party library needs pinned config, not defaults'],
  },
]

// Demo requests / leads
export interface Lead {
  id: string
  company: string
  contact: string
  email: string
  phone: string
  industry: string
  country: string
  size: string
  challenges: string[]
  stage: 'new' | 'contacted' | 'demo-scheduled' | 'proposal' | 'won' | 'lost'
  createdAt: string
  value: number
  notes: { author: string; date: string; text: string }[]
}

export const SEED_LEADS: Lead[] = [
  {
    id: 'L-1001',
    company: 'Standard Bank SA',
    contact: 'Thabo Mokoena',
    email: 't.mokoena@stdbank.co.za',
    phone: '+27 82 111 2233',
    industry: 'Banking & Finance',
    country: 'South Africa',
    size: '10,000+',
    challenges: ['Ransomware', 'Insider Threat'],
    stage: 'proposal',
    createdAt: '2026-06-14',
    value: 480000,
    notes: [
      {
        author: 'You',
        date: '2026-07-01',
        text: 'Sent Enterprise proposal, awaiting CISO review.',
      },
    ],
  },
  {
    id: 'L-1002',
    company: 'Safaricom',
    contact: 'Wanjiru Kamau',
    email: 'w.kamau@safaricom.co.ke',
    phone: '+254 720 555 100',
    industry: 'Telecom',
    country: 'Kenya',
    size: '5,001-10,000',
    challenges: ['DDoS', 'API Security'],
    stage: 'demo-scheduled',
    createdAt: '2026-07-02',
    value: 320000,
    notes: [],
  },
  {
    id: 'L-1003',
    company: 'MTN Nigeria',
    contact: 'Chidi Obi',
    email: 'chidi.obi@mtn.ng',
    phone: '+234 803 222 4141',
    industry: 'Telecom',
    country: 'Nigeria',
    size: '10,000+',
    challenges: ['Fraud', 'Malware'],
    stage: 'contacted',
    createdAt: '2026-07-08',
    value: 540000,
    notes: [],
  },
  {
    id: 'L-1004',
    company: 'Ministry of Health Ghana',
    contact: 'Ama Owusu',
    email: 'a.owusu@moh.gov.gh',
    phone: '+233 24 111 8899',
    industry: 'Healthcare',
    country: 'Ghana',
    size: '1,001-5,000',
    challenges: ['Compliance', 'Data Protection'],
    stage: 'new',
    createdAt: '2026-07-14',
    value: 180000,
    notes: [],
  },
  {
    id: 'L-1005',
    company: 'Egyptian Electricity',
    contact: 'Youssef Fahmy',
    email: 'y.fahmy@egyptera.gov.eg',
    phone: '+20 100 555 8877',
    industry: 'Energy & Utilities',
    country: 'Egypt',
    size: '10,000+',
    challenges: ['OT Security', 'APT'],
    stage: 'won',
    createdAt: '2026-05-22',
    value: 640000,
    notes: [],
  },
  {
    id: 'L-1006',
    company: 'Access Bank',
    contact: 'Bola Adekunle',
    email: 'b.adekunle@accessbankplc.com',
    phone: '+234 809 411 5522',
    industry: 'Banking & Finance',
    country: 'Nigeria',
    size: '5,001-10,000',
    challenges: ['Phishing', 'Cloud Security'],
    stage: 'demo-scheduled',
    createdAt: '2026-07-10',
    value: 380000,
    notes: [],
  },
  {
    id: 'L-1007',
    company: 'Ethio Telecom',
    contact: 'Selam Bekele',
    email: 'selam@ethiotelecom.et',
    phone: '+251 911 445 001',
    industry: 'Telecom',
    country: 'Ethiopia',
    size: '10,000+',
    challenges: ['Network Security'],
    stage: 'contacted',
    createdAt: '2026-07-11',
    value: 290000,
    notes: [],
  },
  {
    id: 'L-1008',
    company: 'KCB Group',
    contact: 'Peter Njoroge',
    email: 'pnjoroge@kcbgroup.com',
    phone: '+254 722 998 100',
    industry: 'Banking & Finance',
    country: 'Kenya',
    size: '5,001-10,000',
    challenges: ['Ransomware'],
    stage: 'new',
    createdAt: '2026-07-15',
    value: 310000,
    notes: [],
  },
  {
    id: 'L-1009',
    company: 'Sonatel',
    contact: 'Aïssata Diop',
    email: 'aissata@sonatel.sn',
    phone: '+221 77 111 9922',
    industry: 'Telecom',
    country: 'Senegal',
    size: '1,001-5,000',
    challenges: ['DDoS', 'Fraud'],
    stage: 'lost',
    createdAt: '2026-06-01',
    value: 210000,
    notes: [],
  },
  {
    id: 'L-1010',
    company: 'Discovery Health',
    contact: 'Naledi Khumalo',
    email: 'naledi@discovery.co.za',
    phone: '+27 83 665 4477',
    industry: 'Healthcare',
    country: 'South Africa',
    size: '5,001-10,000',
    challenges: ['POPIA Compliance'],
    stage: 'proposal',
    createdAt: '2026-06-28',
    value: 420000,
    notes: [],
  },
]

export interface Subscriber {
  id: string
  org: string
  contact: string
  industry: string
  country: string
  plan: 'Starter' | 'Business' | 'Enterprise'
  status: 'active' | 'past-due' | 'suspended' | 'cancelled'
  billing: 'current' | 'failed' | 'processing'
  renewal: string
  score: number
  devices: number
  lastScan: string
  mrr: number
  history: { date: string; action: string }[]
}

export const SEED_SUBSCRIBERS: Subscriber[] = [
  {
    id: 'S-4001',
    org: 'First Bank of Nigeria',
    contact: 'Amara Okafor',
    industry: 'Banking & Finance',
    country: 'Nigeria',
    plan: 'Enterprise',
    status: 'active',
    billing: 'current',
    renewal: '2027-03-14',
    score: 92,
    devices: 12400,
    lastScan: '2026-07-17T04:22:00Z',
    mrr: 48000,
    history: [
      { date: '2026-01-14', action: 'Upgraded from Business to Enterprise' },
      { date: '2025-03-14', action: 'Initial signup — Business' },
    ],
  },
  {
    id: 'S-4002',
    org: 'Nedbank',
    contact: 'Sipho Zulu',
    industry: 'Banking & Finance',
    country: 'South Africa',
    plan: 'Enterprise',
    status: 'active',
    billing: 'current',
    renewal: '2026-11-02',
    score: 88,
    devices: 9800,
    lastScan: '2026-07-17T05:11:00Z',
    mrr: 52000,
    history: [],
  },
  {
    id: 'S-4003',
    org: 'Airtel Kenya',
    contact: 'Grace Mwangi',
    industry: 'Telecom',
    country: 'Kenya',
    plan: 'Business',
    status: 'active',
    billing: 'current',
    renewal: '2026-10-19',
    score: 79,
    devices: 4200,
    lastScan: '2026-07-17T02:30:00Z',
    mrr: 18000,
    history: [],
  },
  {
    id: 'S-4004',
    org: 'Zenith Bank',
    contact: 'Emeka Nwosu',
    industry: 'Banking & Finance',
    country: 'Nigeria',
    plan: 'Enterprise',
    status: 'past-due',
    billing: 'failed',
    renewal: '2026-08-02',
    score: 71,
    devices: 7600,
    lastScan: '2026-07-16T18:45:00Z',
    mrr: 42000,
    history: [
      { date: '2026-07-14', action: 'Payment failed — insufficient funds' },
    ],
  },
  {
    id: 'S-4005',
    org: 'Netcare',
    contact: 'Rethabile Molefe',
    industry: 'Healthcare',
    country: 'South Africa',
    plan: 'Business',
    status: 'active',
    billing: 'current',
    renewal: '2026-12-01',
    score: 84,
    devices: 3100,
    lastScan: '2026-07-17T06:00:00Z',
    mrr: 22000,
    history: [],
  },
  {
    id: 'S-4006',
    org: 'Ecobank',
    contact: 'Kwame Asante',
    industry: 'Banking & Finance',
    country: 'Ghana',
    plan: 'Business',
    status: 'active',
    billing: 'current',
    renewal: '2026-09-15',
    score: 81,
    devices: 2900,
    lastScan: '2026-07-17T03:00:00Z',
    mrr: 19500,
    history: [],
  },
  {
    id: 'S-4007',
    org: 'Vodacom Tanzania',
    contact: 'Fatuma Hassan',
    industry: 'Telecom',
    country: 'Tanzania',
    plan: 'Starter',
    status: 'active',
    billing: 'current',
    renewal: '2026-08-30',
    score: 68,
    devices: 800,
    lastScan: '2026-07-16T22:15:00Z',
    mrr: 4500,
    history: [],
  },
  {
    id: 'S-4008',
    org: 'Egyptair',
    contact: 'Mona El-Sayed',
    industry: 'Logistics',
    country: 'Egypt',
    plan: 'Business',
    status: 'past-due',
    billing: 'failed',
    renewal: '2026-07-30',
    score: 63,
    devices: 1800,
    lastScan: '2026-07-15T10:00:00Z',
    mrr: 15000,
    history: [{ date: '2026-07-12', action: 'Payment failed — expired card' }],
  },
  {
    id: 'S-4009',
    org: 'Bank of Kigali',
    contact: 'Eric Habimana',
    industry: 'Banking & Finance',
    country: 'Rwanda',
    plan: 'Business',
    status: 'active',
    billing: 'current',
    renewal: '2027-01-11',
    score: 90,
    devices: 1500,
    lastScan: '2026-07-17T04:00:00Z',
    mrr: 16500,
    history: [],
  },
  {
    id: 'S-4010',
    org: 'Kenya Airways',
    contact: 'Jomo Kiprop',
    industry: 'Logistics',
    country: 'Kenya',
    plan: 'Enterprise',
    status: 'active',
    billing: 'current',
    renewal: '2026-10-05',
    score: 86,
    devices: 3400,
    lastScan: '2026-07-17T01:20:00Z',
    mrr: 38000,
    history: [],
  },
  {
    id: 'S-4011',
    org: 'Old Mutual',
    contact: 'Precious Dube',
    industry: 'Insurance',
    country: 'South Africa',
    plan: 'Enterprise',
    status: 'active',
    billing: 'current',
    renewal: '2026-11-22',
    score: 89,
    devices: 5200,
    lastScan: '2026-07-17T03:45:00Z',
    mrr: 41000,
    history: [],
  },
  {
    id: 'S-4012',
    org: 'Cairo Bank',
    contact: 'Ahmed Nasser',
    industry: 'Banking & Finance',
    country: 'Egypt',
    plan: 'Business',
    status: 'cancelled',
    billing: 'current',
    renewal: '2026-06-01',
    score: 55,
    devices: 0,
    lastScan: '2026-06-01T00:00:00Z',
    mrr: 0,
    history: [
      { date: '2026-06-01', action: 'Cancelled — moved to competitor' },
    ],
  },
]

export const COMPLIANCE_FRAMEWORKS = [
  {
    code: 'ISO 27001',
    name: 'Information Security Management',
    score: 87,
    controls: 114,
    passing: 99,
  },
  {
    code: 'NIST CSF',
    name: 'Cybersecurity Framework 2.0',
    score: 82,
    controls: 108,
    passing: 89,
  },
  {
    code: 'CIS Controls',
    name: 'CIS Critical Security Controls v8',
    score: 91,
    controls: 153,
    passing: 139,
  },
  {
    code: 'PCI DSS',
    name: 'Payment Card Industry DSS 4.0',
    score: 78,
    controls: 300,
    passing: 234,
  },
  {
    code: 'GDPR',
    name: 'EU General Data Protection Regulation',
    score: 84,
    controls: 47,
    passing: 39,
  },
  {
    code: 'POPIA',
    name: 'South Africa Protection of Personal Info',
    score: 89,
    controls: 42,
    passing: 37,
  },
  {
    code: 'NDPA',
    name: 'Nigeria Data Protection Act 2023',
    score: 76,
    controls: 38,
    passing: 29,
  },
  {
    code: 'Kenya DPA',
    name: 'Kenya Data Protection Act 2019',
    score: 81,
    controls: 40,
    passing: 32,
  },
  {
    code: 'SOC 2',
    name: 'SOC 2 Type II — Trust Services',
    score: 85,
    controls: 64,
    passing: 54,
  },
  {
    code: 'HIPAA',
    name: 'Health Insurance Portability',
    score: 72,
    controls: 78,
    passing: 56,
  },
]

export const mockOrganization: Organization = {
  id: 'BLVCK-CYBER',

  name: 'BLVCK CYBER',

  legalName: 'BLVCK CYBER Security Africa (Pty) Ltd',

  industry: 'Cyber Security',

  companySize: '51-200 Employees',

  country: 'South Africa',

  timezone: 'Africa/Johannesburg',

  website: 'https://blvckcyber.com',

  supportEmail: 'support@blvckcyber.com',

  supportPhone: '+27 10 000 0000',

  description:
    'Enterprise cybersecurity monitoring and threat intelligence platform.',

  security: {
    enforceMfa: true,

    passwordExpiryDays: 90,

    sessionTimeout: 60,

    idleTimeout: 15,

    ipRestrictions: false,

    deviceTrust: true,
  },

  branding: {
    primaryColor: '#000000',

    secondaryColor: '#111827',

    accentColor: '#00ff99',

    darkTheme: true,
  },

  domains: [
    {
      id: 1,

      domain: 'blvckcyber.com',

      verified: true,
    },

    {
      id: 2,

      domain: 'security.blvckcyber.com',

      verified: true,
    },
  ],

  locations: [
    {
      id: 1,

      name: 'Head Office',

      country: 'South Africa',

      city: 'Johannesburg',

      timezone: 'Africa/Johannesburg',
    },

    {
      id: 2,

      name: 'Operations Center',

      country: 'Zimbabwe',

      city: 'Bulawayo',

      timezone: 'Africa/Harare',
    },
  ],

  subscription: {
    plan: 'Enterprise',

    users: 200,

    activeUsers: 87,

    storage: '5TB',

    renewalDate: '2027-01-12',
  },
}
