import {
  Lock,
  UserX,
  Fish,
  Database,
  KeyRound,
  Bug,
  Cloud,
  Globe,
  type LucideIcon,
} from 'lucide-react'

export type Severity = 'Critical' | 'High' | 'Medium'

export type TimelineEvent = {
  time: string
  label: string
  detail: string
  kind: 'attacker' | 'ai' | 'system'
}

export type AttackPhase = {
  phase: 'Initial Access' | 'Lateral Movement' | 'Persistence' | 'Impact'
  technique: string
  detail: string
}

export type MitreTechnique = {
  id: string
  tactic: string
  technique: string
}

export type AffectedItem = {
  name: string
  type: string
  status: 'Compromised' | 'At Risk' | 'Contained' | 'Isolated'
}

export type Scenario = {
  id: string
  name: string
  icon: LucideIcon
  category: string
  severity: Severity
  tagline: string
  detectionSignal: string
  confidence: number
  detectedBy: string
  timeline: TimelineEvent[]
  investigationFindings: string[]
  iocs: { type: string; value: string }[]
  affectedSystems: AffectedItem[]
  affectedAccounts: AffectedItem[]
  attackChain: AttackPhase[]
  mitre: MitreTechnique[]
  rootCause: string
  execSummary: string
  containment: string[]
  recovery: string[]
  lessons: string[]
}

export const scenarios: Scenario[] = [
  {
    id: 'ransomware',
    name: 'Ransomware Attack',
    icon: Lock,
    category: 'Malware / Extortion',
    severity: 'Critical',
    tagline: 'Mass file encryption attempt across the finance file server.',
    detectionSignal: 'Rapid entropy spike across 4,200+ files with shadow-copy deletion',
    confidence: 98,
    detectedBy: 'BLVCK AI Behavioral Engine',
    timeline: [
      { time: 'T+00:00', label: 'Initial foothold', detail: 'Malicious macro executed from invoice.docm on FIN-WS-07.', kind: 'attacker' },
      { time: 'T+02:14', label: 'AI anomaly flagged', detail: 'Unusual child-process spawn (powershell → vssadmin) detected.', kind: 'ai' },
      { time: 'T+03:40', label: 'Lateral spread', detail: 'SMB propagation to FIN-SRV-02 using harvested credentials.', kind: 'attacker' },
      { time: 'T+04:05', label: 'Encryption begins', detail: 'Bulk file entropy spike + shadow copies deleted.', kind: 'attacker' },
      { time: 'T+04:12', label: 'AI auto-containment', detail: 'Affected hosts network-isolated, malicious process killed.', kind: 'ai' },
      { time: 'T+04:20', label: 'Snapshot recovery armed', detail: 'Immutable backups verified and staged for restore.', kind: 'system' },
    ],
    investigationFindings: [
      'Entry via a weaponized Office document delivered by a spoofed supplier email.',
      'Attacker used living-off-the-land binaries (vssadmin, wmic) to evade signature detection.',
      'Encryption throttled to ~4,200 files before AI isolation; no exfiltration confirmed.',
      'Ransom note (README_RESTORE.txt) matches the LockBit-style affiliate playbook.',
    ],
    iocs: [
      { type: 'SHA-256', value: 'a1b2c3…9f2e (encryptor.exe)' },
      { type: 'C2 Domain', value: 'update-sync-cdn[.]net' },
      { type: 'File', value: 'README_RESTORE.txt' },
      { type: 'Mutex', value: 'Global\\LB_lock_7731' },
    ],
    affectedSystems: [
      { name: 'FIN-WS-07', type: 'Workstation', status: 'Isolated' },
      { name: 'FIN-SRV-02', type: 'File Server', status: 'Contained' },
      { name: 'BACKUP-01', type: 'Backup Node', status: 'At Risk' },
    ],
    affectedAccounts: [
      { name: 'j.okafor', type: 'Finance User', status: 'Compromised' },
      { name: 'svc-backup', type: 'Service Account', status: 'At Risk' },
    ],
    attackChain: [
      { phase: 'Initial Access', technique: 'Phishing: Malicious Attachment', detail: 'Macro-enabled invoice opened by finance user.' },
      { phase: 'Lateral Movement', technique: 'SMB / Windows Admin Shares', detail: 'Spread to file server with stolen creds.' },
      { phase: 'Persistence', technique: 'Scheduled Task / Registry Run Key', detail: 'Autorun entry created for re-execution.' },
      { phase: 'Impact', technique: 'Data Encrypted for Impact', detail: 'Bulk encryption + shadow copy deletion.' },
    ],
    mitre: [
      { id: 'T1566.001', tactic: 'Initial Access', technique: 'Spearphishing Attachment' },
      { id: 'T1059.001', tactic: 'Execution', technique: 'PowerShell' },
      { id: 'T1490', tactic: 'Impact', technique: 'Inhibit System Recovery' },
      { id: 'T1486', tactic: 'Impact', technique: 'Data Encrypted for Impact' },
      { id: 'T1021.002', tactic: 'Lateral Movement', technique: 'SMB/Windows Admin Shares' },
    ],
    rootCause:
      'Macro execution was permitted from internet-sourced Office documents, and the finance file server lacked segmentation from user workstations, allowing rapid lateral movement.',
    execSummary:
      'At 04:05 a ransomware affiliate attempted mass encryption of the finance file share after gaining a foothold through a phishing attachment. The BLVCK CYBER AI-SOC detected the anomalous encryption behavior within 7 seconds and automatically isolated the affected hosts, limiting impact to roughly 4,200 files with no confirmed data exfiltration. Immutable backups were verified and staged for restore, and no ransom demand was actioned.',
    containment: [
      'Network-isolate FIN-WS-07 and FIN-SRV-02 (completed automatically).',
      'Terminate malicious encryptor process and remove autorun persistence.',
      'Disable compromised account j.okafor and rotate svc-backup credentials.',
      'Block C2 domain update-sync-cdn[.]net at the DNS and firewall layers.',
    ],
    recovery: [
      'Restore encrypted files from the verified immutable backup snapshot.',
      'Rebuild FIN-WS-07 from a known-good golden image.',
      'Validate integrity of restored data before returning systems to production.',
      'Force password reset for all finance-department accounts.',
    ],
    lessons: [
      'Enforce Group Policy to block macros from internet-sourced documents.',
      'Segment finance servers from general user VLANs.',
      'Adopt immutable, offline backups with regular restore drills.',
    ],
  },
  {
    id: 'insider-threat',
    name: 'Insider Threat',
    icon: UserX,
    category: 'Data Exfiltration',
    severity: 'High',
    tagline: 'Departing employee staging bulk downloads of customer records.',
    detectionSignal: 'Abnormal after-hours access to CRM export API by a single user',
    confidence: 91,
    detectedBy: 'BLVCK AI User Behavior Analytics',
    timeline: [
      { time: 'T-6d', label: 'Baseline shift', detail: 'User begins accessing records outside their normal team scope.', kind: 'attacker' },
      { time: 'T+00:00', label: 'After-hours burst', detail: '2,300 CRM records exported at 02:14 local time.', kind: 'attacker' },
      { time: 'T+00:03', label: 'AI risk score spike', detail: 'UBA risk score jumps from 22 to 88.', kind: 'ai' },
      { time: 'T+00:06', label: 'Egress to personal cloud', detail: 'Upload attempt to unmanaged Google Drive account.', kind: 'attacker' },
      { time: 'T+00:07', label: 'AI session hold', detail: 'DLP block enforced; session flagged for review.', kind: 'ai' },
    ],
    investigationFindings: [
      'User account is on a 30-day resignation notice period.',
      'Downloads focused on the full customer contact and pricing tables.',
      'Attempted transfer to a personal cloud storage account via browser upload.',
      'No malware involved — abuse of legitimate, over-provisioned access.',
    ],
    iocs: [
      { type: 'User', value: 'a.mensah' },
      { type: 'Endpoint', value: 'API /crm/export/v2' },
      { type: 'Destination', value: 'drive.google.com (unmanaged)' },
      { type: 'Volume', value: '2,300 records / 41 MB' },
    ],
    affectedSystems: [
      { name: 'CRM-APP-01', type: 'CRM Platform', status: 'At Risk' },
      { name: 'DLP-GW', type: 'Egress Gateway', status: 'Contained' },
    ],
    affectedAccounts: [{ name: 'a.mensah', type: 'Sales Employee', status: 'Compromised' }],
    attackChain: [
      { phase: 'Initial Access', technique: 'Valid Accounts', detail: 'Legitimate employee credentials.' },
      { phase: 'Lateral Movement', technique: 'N/A (single system)', detail: 'Access confined to CRM.' },
      { phase: 'Persistence', technique: 'Not observed', detail: 'No persistence mechanism used.' },
      { phase: 'Impact', technique: 'Exfiltration Over Web Service', detail: 'Bulk export to personal cloud.' },
    ],
    mitre: [
      { id: 'T1078', tactic: 'Initial Access', technique: 'Valid Accounts' },
      { id: 'T1530', tactic: 'Collection', technique: 'Data from Cloud Storage' },
      { id: 'T1567.002', tactic: 'Exfiltration', technique: 'Exfiltration to Cloud Storage' },
    ],
    rootCause:
      'The user retained broad CRM export privileges beyond their role requirements, and no time-of-day or volume-based access controls were enforced on bulk export operations.',
    execSummary:
      'A sales employee under resignation notice attempted to exfiltrate 2,300 customer records via the CRM export API during after-hours, then upload them to a personal cloud account. BLVCK CYBER User Behavior Analytics detected the deviation from the user baseline within 3 seconds and the DLP policy blocked the egress before any data left the organization. No customer data was successfully exfiltrated.',
    containment: [
      'Block the egress upload and place the user session on hold (completed automatically).',
      'Suspend a.mensah account access pending HR and legal review.',
      'Preserve forensic logs of all export activity for the investigation.',
      'Revoke bulk-export entitlement from the general sales role.',
    ],
    recovery: [
      'Complete HR/legal review and formalize offboarding controls.',
      'Notify data protection officer for regulatory assessment.',
      'Audit all recent bulk exports for similar anomalies.',
    ],
    lessons: [
      'Apply least-privilege and just-in-time access for bulk data operations.',
      'Trigger enhanced monitoring automatically for employees on notice.',
      'Enforce volume and time-of-day thresholds on export APIs.',
    ],
  },
  {
    id: 'phishing',
    name: 'Phishing Campaign',
    icon: Fish,
    category: 'Credential Theft',
    severity: 'High',
    tagline: 'Targeted credential-harvesting campaign against executives.',
    detectionSignal: 'Cluster of look-alike domain logins and MFA fatigue prompts',
    confidence: 94,
    detectedBy: 'BLVCK AI Email & Identity Correlation',
    timeline: [
      { time: 'T+00:00', label: 'Phishing wave', detail: '14 executives receive "Payroll Update" emails from a look-alike domain.', kind: 'attacker' },
      { time: 'T+00:08', label: 'Credential capture', detail: 'One user submits credentials on the fake portal.', kind: 'attacker' },
      { time: 'T+00:11', label: 'AI link detonation', detail: 'Sandbox flags the landing page as a credential harvester.', kind: 'ai' },
      { time: 'T+00:19', label: 'MFA push spam', detail: 'Attacker triggers repeated MFA prompts (fatigue attack).', kind: 'attacker' },
      { time: 'T+00:21', label: 'AI account lockdown', detail: 'Sessions revoked; adaptive MFA switched to number-matching.', kind: 'ai' },
    ],
    investigationFindings: [
      'Sender used a homoglyph domain (blvck-cyber[.]co vs blvck.cyber).',
      'Landing page cloned the Microsoft 365 login and captured one set of credentials.',
      'Attacker attempted MFA fatigue but failed against number-matching enforcement.',
      'No mailbox rules or forwarding were successfully created.',
    ],
    iocs: [
      { type: 'Domain', value: 'blvck-cyber[.]co' },
      { type: 'URL', value: 'hxxps://login.blvck-cyber[.]co/auth' },
      { type: 'Sender', value: 'payroll@blvck-cyber[.]co' },
      { type: 'IP', value: '185.234.219.44' },
    ],
    affectedSystems: [{ name: 'M365-TENANT', type: 'Identity Provider', status: 'Contained' }],
    affectedAccounts: [
      { name: 'c.dube', type: 'Executive', status: 'Compromised' },
      { name: '13 recipients', type: 'Executives', status: 'At Risk' },
    ],
    attackChain: [
      { phase: 'Initial Access', technique: 'Phishing Link', detail: 'Look-alike domain credential portal.' },
      { phase: 'Lateral Movement', technique: 'Not observed', detail: 'Contained at identity layer.' },
      { phase: 'Persistence', technique: 'Attempted mailbox rules', detail: 'Blocked before creation.' },
      { phase: 'Impact', technique: 'Account Takeover attempt', detail: 'MFA fatigue failed.' },
    ],
    mitre: [
      { id: 'T1566.002', tactic: 'Initial Access', technique: 'Spearphishing Link' },
      { id: 'T1078.004', tactic: 'Initial Access', technique: 'Cloud Accounts' },
      { id: 'T1621', tactic: 'Credential Access', technique: 'MFA Request Generation' },
    ],
    rootCause:
      'Legacy push-approval MFA was susceptible to fatigue attacks, and look-alike domains were not being proactively blocked at the secure email gateway.',
    execSummary:
      'A targeted phishing campaign impersonating payroll notifications reached 14 executives, harvesting one set of credentials. The BLVCK CYBER AI-SOC detonated the malicious link, correlated it with anomalous logins, and revoked the compromised sessions within 21 minutes while enforcing number-matching MFA. No account was successfully taken over and no persistence was established.',
    containment: [
      'Revoke active sessions and reset credentials for c.dube (completed automatically).',
      'Enforce number-matching MFA tenant-wide.',
      'Quarantine the phishing email across all 14 mailboxes.',
      'Block the homoglyph domain and sender at the email gateway.',
    ],
    recovery: [
      'Re-enroll affected user in MFA and verify no rogue app consents remain.',
      'Run a tenant-wide audit for suspicious OAuth grants and forwarding rules.',
      'Issue a targeted awareness briefing to the executive team.',
    ],
    lessons: [
      'Migrate all users to phishing-resistant MFA (FIDO2 / number-matching).',
      'Enable look-alike and homoglyph domain detection at the gateway.',
      'Run quarterly phishing simulations for high-value targets.',
    ],
  },
  {
    id: 'database-compromise',
    name: 'Database Compromise',
    icon: Database,
    category: 'Data Breach',
    severity: 'Critical',
    tagline: 'SQL injection leading to unauthorized database reads.',
    detectionSignal: 'Anomalous UNION-based queries and mass row reads from web tier',
    confidence: 96,
    detectedBy: 'BLVCK AI Database Activity Monitor',
    timeline: [
      { time: 'T+00:00', label: 'Injection probing', detail: 'Automated SQLi payloads hit the public web app.', kind: 'attacker' },
      { time: 'T+00:04', label: 'AI query anomaly', detail: 'UNION SELECT patterns flagged on customer DB.', kind: 'ai' },
      { time: 'T+00:09', label: 'Data staging', detail: 'Attacker reads user + hashed-password tables.', kind: 'attacker' },
      { time: 'T+00:12', label: 'AI query kill', detail: 'Malicious DB session terminated; WAF rule deployed.', kind: 'ai' },
      { time: 'T+00:15', label: 'Credential rotation', detail: 'App DB service account rotated automatically.', kind: 'system' },
    ],
    investigationFindings: [
      'Injection point was an unparameterized search field in the customer portal.',
      'Attacker enumerated the schema then read the users table (hashed passwords).',
      'No write or delete operations were performed.',
      'Hashes used bcrypt; brute-force risk is limited but rotation is advised.',
    ],
    iocs: [
      { type: 'Endpoint', value: '/portal/search?q=' },
      { type: 'Payload', value: "' UNION SELECT …--" },
      { type: 'IP', value: '45.146.164.110' },
      { type: 'User-Agent', value: 'sqlmap/1.7' },
    ],
    affectedSystems: [
      { name: 'WEB-APP-03', type: 'Web Application', status: 'Contained' },
      { name: 'CUST-DB-01', type: 'PostgreSQL DB', status: 'Contained' },
    ],
    affectedAccounts: [{ name: 'svc-webapp', type: 'DB Service Account', status: 'Compromised' }],
    attackChain: [
      { phase: 'Initial Access', technique: 'Exploit Public-Facing Application', detail: 'SQL injection in search field.' },
      { phase: 'Lateral Movement', technique: 'Not required', detail: 'Direct DB access from web tier.' },
      { phase: 'Persistence', technique: 'Not observed', detail: 'No persistence attempted.' },
      { phase: 'Impact', technique: 'Data from Information Repositories', detail: 'Read of user table.' },
    ],
    mitre: [
      { id: 'T1190', tactic: 'Initial Access', technique: 'Exploit Public-Facing Application' },
      { id: 'T1213', tactic: 'Collection', technique: 'Data from Information Repositories' },
      { id: 'T1005', tactic: 'Collection', technique: 'Data from Local System' },
    ],
    rootCause:
      'A user-supplied search parameter was concatenated directly into a SQL query without parameterization, and the web application service account had read access to sensitive tables beyond its needs.',
    execSummary:
      'An attacker exploited a SQL injection flaw in the customer portal search field to read the users table, including bcrypt-hashed passwords. The BLVCK CYBER AI Database Activity Monitor detected the anomalous UNION-based queries within 4 seconds, terminated the malicious session, deployed a virtual-patch WAF rule, and rotated the database service credentials. No data was modified and exposure was limited to hashed credentials.',
    containment: [
      'Terminate the malicious DB session (completed automatically).',
      'Deploy WAF virtual patch for the vulnerable endpoint.',
      'Rotate the svc-webapp database credentials.',
      'Restrict the service account to least-privilege table access.',
    ],
    recovery: [
      'Deploy parameterized queries / prepared statements for the search feature.',
      'Force a password reset for potentially exposed customer accounts.',
      'Conduct a full code review for other injection points.',
    ],
    lessons: [
      'Adopt parameterized queries and an ORM across all data access.',
      'Enforce least-privilege for application database accounts.',
      'Integrate SAST/DAST scanning into the CI/CD pipeline.',
    ],
  },
  {
    id: 'privilege-escalation',
    name: 'Privilege Escalation',
    icon: KeyRound,
    category: 'Identity Abuse',
    severity: 'High',
    tagline: 'Standard account elevating to domain admin via token abuse.',
    detectionSignal: 'Unexpected addition of a user to the Domain Admins group',
    confidence: 93,
    detectedBy: 'BLVCK AI Identity Threat Detection',
    timeline: [
      { time: 'T+00:00', label: 'Local exploit', detail: 'Attacker abuses an unpatched service for SYSTEM on WKS-22.', kind: 'attacker' },
      { time: 'T+00:05', label: 'Token theft', detail: 'Cached admin token stolen and impersonated.', kind: 'attacker' },
      { time: 'T+00:08', label: 'AI privilege alert', detail: 'Anomalous group change to Domain Admins detected.', kind: 'ai' },
      { time: 'T+00:10', label: 'AI rollback', detail: 'Group membership reverted; token session killed.', kind: 'ai' },
    ],
    investigationFindings: [
      'Initial SYSTEM access via an unpatched local service vulnerability.',
      'Attacker harvested a cached domain-admin token from memory.',
      'Added a controlled account to the Domain Admins group.',
      'AI reverted the change before the account was used for further action.',
    ],
    iocs: [
      { type: 'Host', value: 'WKS-22' },
      { type: 'Account', value: 'temp_admin2' },
      { type: 'Tool', value: 'mimikatz-like token dumper' },
      { type: 'Event', value: 'Windows Security 4728' },
    ],
    affectedSystems: [
      { name: 'WKS-22', type: 'Workstation', status: 'Isolated' },
      { name: 'DC-01', type: 'Domain Controller', status: 'At Risk' },
    ],
    affectedAccounts: [
      { name: 'temp_admin2', type: 'Attacker Account', status: 'Contained' },
      { name: 'da-admin', type: 'Domain Admin', status: 'Compromised' },
    ],
    attackChain: [
      { phase: 'Initial Access', technique: 'Valid Accounts', detail: 'Standard user foothold.' },
      { phase: 'Lateral Movement', technique: 'Token Impersonation', detail: 'Stolen admin token reused.' },
      { phase: 'Persistence', technique: 'Account Manipulation', detail: 'Added to Domain Admins.' },
      { phase: 'Impact', technique: 'Domain dominance attempt', detail: 'Reverted before abuse.' },
    ],
    mitre: [
      { id: 'T1068', tactic: 'Privilege Escalation', technique: 'Exploitation for Privilege Escalation' },
      { id: 'T1134', tactic: 'Privilege Escalation', technique: 'Access Token Manipulation' },
      { id: 'T1098', tactic: 'Persistence', technique: 'Account Manipulation' },
    ],
    rootCause:
      'A workstation was missing a critical local-privilege-escalation patch, and domain admin credentials were being cached on non-tiered endpoints, enabling token theft.',
    execSummary:
      'An attacker with a standard foothold exploited an unpatched local service to gain SYSTEM privileges, stole a cached domain-admin token, and added a controlled account to the Domain Admins group. The BLVCK CYBER AI Identity Threat Detection flagged the anomalous privileged group change within 8 seconds and automatically reverted the membership and killed the session before any domain-wide action occurred.',
    containment: [
      'Revert the Domain Admins group change and kill the token session (completed automatically).',
      'Isolate WKS-22 from the network.',
      'Disable the attacker-controlled temp_admin2 account.',
      'Force reset of the exposed da-admin credentials and krbtgt (twice).',
    ],
    recovery: [
      'Patch the local privilege-escalation vulnerability fleet-wide.',
      'Implement tiered administration to stop admin token caching on workstations.',
      'Review all privileged group memberships for unauthorized entries.',
    ],
    lessons: [
      'Enforce a tiered admin model with dedicated privileged access workstations.',
      'Prioritize patching of local privilege-escalation vulnerabilities.',
      'Enable credential guard to protect cached tokens.',
    ],
  },
  {
    id: 'malware-infection',
    name: 'Malware Infection',
    icon: Bug,
    category: 'Endpoint Compromise',
    severity: 'Medium',
    tagline: 'Info-stealer trojan beaconing from a marketing endpoint.',
    detectionSignal: 'Periodic beaconing to a known-bad host with browser credential access',
    confidence: 90,
    detectedBy: 'BLVCK AI Endpoint Detection & Response',
    timeline: [
      { time: 'T+00:00', label: 'Drive-by download', detail: 'Trojanized installer from a cracked-software site.', kind: 'attacker' },
      { time: 'T+00:06', label: 'AI beacon detection', detail: 'Regular 60s callbacks to a suspicious host flagged.', kind: 'ai' },
      { time: 'T+00:09', label: 'Credential access', detail: 'Malware reads browser-saved credentials.', kind: 'attacker' },
      { time: 'T+00:11', label: 'AI quarantine', detail: 'Process quarantined; host isolated for cleanup.', kind: 'ai' },
    ],
    investigationFindings: [
      'Infection originated from a trojanized "free" software installer.',
      'Malware is a commodity info-stealer targeting browser credential stores.',
      'Beaconed to a low-reputation host every 60 seconds.',
      'Isolated before confirmed data theft; browser vault likely accessed.',
    ],
    iocs: [
      { type: 'SHA-256', value: 'e7f4…11ac (setup.exe)' },
      { type: 'C2', value: 'stat-collect[.]top:443' },
      { type: 'Path', value: '%APPDATA%\\svchost32.exe' },
      { type: 'Registry', value: 'HKCU\\...\\Run\\Updater' },
    ],
    affectedSystems: [{ name: 'MKT-WS-14', type: 'Workstation', status: 'Isolated' }],
    affectedAccounts: [{ name: 'l.abara', type: 'Marketing User', status: 'Compromised' }],
    attackChain: [
      { phase: 'Initial Access', technique: 'Drive-by Compromise', detail: 'Trojanized installer download.' },
      { phase: 'Lateral Movement', technique: 'Not observed', detail: 'Single host.' },
      { phase: 'Persistence', technique: 'Registry Run Key', detail: 'Autorun updater entry.' },
      { phase: 'Impact', technique: 'Credentials from Web Browsers', detail: 'Browser vault access.' },
    ],
    mitre: [
      { id: 'T1189', tactic: 'Initial Access', technique: 'Drive-by Compromise' },
      { id: 'T1547.001', tactic: 'Persistence', technique: 'Registry Run Keys' },
      { id: 'T1555.003', tactic: 'Credential Access', technique: 'Credentials from Web Browsers' },
    ],
    rootCause:
      'The endpoint allowed installation of unapproved software and lacked web filtering for high-risk cracked-software sites, permitting the initial trojan download.',
    execSummary:
      'A marketing workstation was infected by a commodity info-stealer bundled with a cracked-software installer. The BLVCK CYBER EDR detected the regular C2 beaconing and browser credential access within 6 seconds, quarantined the malicious process, and isolated the host. The endpoint was contained before any credentials were confirmed exfiltrated, though a precautionary reset is recommended.',
    containment: [
      'Quarantine the malicious process and isolate MKT-WS-14 (completed automatically).',
      'Remove the registry autorun persistence entry.',
      'Block the C2 host stat-collect[.]top.',
      'Force credential reset for l.abara and any saved browser passwords.',
    ],
    recovery: [
      'Rebuild the endpoint from a clean image.',
      'Reset all credentials that were stored in the browser vault.',
      'Enable application allow-listing on the endpoint.',
    ],
    lessons: [
      'Enforce application allow-listing and remove local admin rights.',
      'Deploy web filtering to block high-risk download categories.',
      'Discourage browser-stored passwords in favor of a managed vault.',
    ],
  },
  {
    id: 'cloud-attack',
    name: 'Cloud Attack',
    icon: Cloud,
    category: 'Cloud Security',
    severity: 'High',
    tagline: 'Leaked access key used to enumerate and exfiltrate cloud storage.',
    detectionSignal: 'API calls from an unusual geography using a long-lived access key',
    confidence: 95,
    detectedBy: 'BLVCK AI Cloud Posture & Threat Detection',
    timeline: [
      { time: 'T+00:00', label: 'Key leak', detail: 'Access key committed to a public code repository.', kind: 'attacker' },
      { time: 'T+00:03', label: 'Recon', detail: 'ListBuckets / GetCallerIdentity from a new region.', kind: 'attacker' },
      { time: 'T+00:07', label: 'AI geo-anomaly', detail: 'Impossible-travel + new-ASN usage flagged.', kind: 'ai' },
      { time: 'T+00:10', label: 'Storage access', detail: 'Attempted bulk object download from a private bucket.', kind: 'attacker' },
      { time: 'T+00:12', label: 'AI key revocation', detail: 'Access key disabled; bucket policy tightened.', kind: 'ai' },
    ],
    investigationFindings: [
      'A long-lived access key was accidentally committed to a public repo.',
      'Attacker performed reconnaissance then targeted a private storage bucket.',
      'Bucket lacked a restrictive resource policy, relying only on key secrecy.',
      'AI revoked the key before a full bucket download completed.',
    ],
    iocs: [
      { type: 'Access Key', value: 'AKIA…J7QF' },
      { type: 'Source IP', value: '103.94.212.7 (new ASN)' },
      { type: 'API', value: 's3:ListBucket, s3:GetObject' },
      { type: 'Repo', value: 'github.com/…/config-backup' },
    ],
    affectedSystems: [
      { name: 'prod-data-bucket', type: 'Object Storage', status: 'Contained' },
      { name: 'iam-user/deploy', type: 'IAM Principal', status: 'Compromised' },
    ],
    affectedAccounts: [{ name: 'iam-user/deploy', type: 'Cloud IAM User', status: 'Compromised' }],
    attackChain: [
      { phase: 'Initial Access', technique: 'Valid Accounts: Cloud', detail: 'Leaked access key.' },
      { phase: 'Lateral Movement', technique: 'Cloud Service Discovery', detail: 'API enumeration.' },
      { phase: 'Persistence', technique: 'Not observed', detail: 'Key revoked quickly.' },
      { phase: 'Impact', technique: 'Data from Cloud Storage', detail: 'Bulk object read attempt.' },
    ],
    mitre: [
      { id: 'T1078.004', tactic: 'Initial Access', technique: 'Cloud Accounts' },
      { id: 'T1526', tactic: 'Discovery', technique: 'Cloud Service Discovery' },
      { id: 'T1530', tactic: 'Collection', technique: 'Data from Cloud Storage' },
    ],
    rootCause:
      'A long-lived static access key was committed to a public repository, and the sensitive storage bucket relied on key secrecy rather than a least-privilege resource policy.',
    execSummary:
      'A leaked long-lived cloud access key was used from an unusual geography to enumerate resources and attempt bulk download from a private storage bucket. The BLVCK CYBER Cloud Threat Detection engine identified the impossible-travel and new-ASN anomaly within 7 seconds, disabled the key, and tightened the bucket policy before a full download completed. Exposure was limited to partial object listing.',
    containment: [
      'Disable the leaked access key and tighten the bucket policy (completed automatically).',
      'Rotate all keys for the iam-user/deploy principal.',
      'Remove the secret from the public repository and its git history.',
      'Enable bucket-level block-public-access and require VPC endpoints.',
    ],
    recovery: [
      'Migrate to short-lived, role-based credentials (no static keys).',
      'Audit CloudTrail for any objects that were accessed.',
      'Enable secret scanning across all repositories.',
    ],
    lessons: [
      'Eliminate long-lived static keys in favor of federated, short-lived roles.',
      'Enforce least-privilege resource policies on all storage.',
      'Enable automated secret scanning and pre-commit hooks.',
    ],
  },
  {
    id: 'web-app-attack',
    name: 'Web Application Attack',
    icon: Globe,
    category: 'Application Security',
    severity: 'Medium',
    tagline: 'Automated credential stuffing and XSS probing on the portal.',
    detectionSignal: 'High-velocity login failures plus reflected script payloads',
    confidence: 89,
    detectedBy: 'BLVCK AI Web Application Firewall',
    timeline: [
      { time: 'T+00:00', label: 'Credential stuffing', detail: '18,000 login attempts from a botnet in 4 minutes.', kind: 'attacker' },
      { time: 'T+00:02', label: 'AI rate anomaly', detail: 'Login velocity + distributed source pattern flagged.', kind: 'ai' },
      { time: 'T+00:05', label: 'XSS probing', detail: 'Reflected <script> payloads injected in form fields.', kind: 'attacker' },
      { time: 'T+00:06', label: 'AI mitigation', detail: 'Adaptive rate-limit + WAF rules applied; CAPTCHA enforced.', kind: 'ai' },
    ],
    investigationFindings: [
      'Credential stuffing used a leaked-password list against the login endpoint.',
      'A small number of accounts matched reused passwords (forced reset).',
      'Reflected XSS probing targeted an unsanitized feedback form.',
      'AI applied adaptive rate-limiting and blocked the payloads at the WAF.',
    ],
    iocs: [
      { type: 'Endpoint', value: '/api/login' },
      { type: 'Payload', value: '<script>document.cookie…</script>' },
      { type: 'Sources', value: '1,240 distributed IPs (botnet)' },
      { type: 'Rate', value: '18k attempts / 4 min' },
    ],
    affectedSystems: [
      { name: 'WEB-PORTAL-01', type: 'Web Portal', status: 'Contained' },
      { name: 'WAF-EDGE', type: 'Edge WAF', status: 'Contained' },
    ],
    affectedAccounts: [{ name: '9 matched accounts', type: 'Portal Users', status: 'At Risk' }],
    attackChain: [
      { phase: 'Initial Access', technique: 'Brute Force: Credential Stuffing', detail: 'Leaked-password list.' },
      { phase: 'Lateral Movement', technique: 'Not applicable', detail: 'Edge-contained.' },
      { phase: 'Persistence', technique: 'Not observed', detail: 'No persistence.' },
      { phase: 'Impact', technique: 'Cross-Site Scripting attempt', detail: 'Blocked at WAF.' },
    ],
    mitre: [
      { id: 'T1110.004', tactic: 'Credential Access', technique: 'Credential Stuffing' },
      { id: 'T1190', tactic: 'Initial Access', technique: 'Exploit Public-Facing Application' },
      { id: 'T1059.007', tactic: 'Execution', technique: 'JavaScript (XSS)' },
    ],
    rootCause:
      'The login endpoint lacked adaptive rate-limiting and bot protection, and a feedback form rendered user input without output encoding, enabling reflected XSS attempts.',
    execSummary:
      'The customer portal faced an automated credential-stuffing campaign of 18,000 attempts alongside reflected XSS probing. The BLVCK CYBER AI-WAF detected the abnormal login velocity and script payloads within 2 seconds, applied adaptive rate-limiting, enforced CAPTCHA, and blocked the injection attempts. Nine accounts with reused passwords were flagged for forced reset; no XSS payload executed.',
    containment: [
      'Apply adaptive rate-limiting and enforce CAPTCHA on login (completed automatically).',
      'Block the botnet source ranges at the edge.',
      'Force password reset for the 9 matched accounts.',
      'Deploy WAF rules to strip and log XSS payloads.',
    ],
    recovery: [
      'Add output encoding / sanitization to the feedback form.',
      'Enforce MFA and breached-password checks on all portal logins.',
      'Review logs for any successful credential-stuffing hits.',
    ],
    lessons: [
      'Deploy bot management and adaptive rate-limiting on authentication.',
      'Enforce MFA and check credentials against breach corpora.',
      'Apply context-aware output encoding to prevent XSS.',
    ],
  },
]

export const severityStyles: Record<Severity, string> = {
  Critical: 'bg-destructive/15 text-destructive border-destructive/30',
  High: 'bg-warning/15 text-warning border-warning/30',
  Medium: 'bg-primary/15 text-primary border-primary/30',
}

export const statusStyles: Record<AffectedItem['status'], string> = {
  Compromised: 'bg-destructive/15 text-destructive border-destructive/30',
  'At Risk': 'bg-warning/15 text-warning border-warning/30',
  Contained: 'bg-primary/15 text-primary border-primary/30',
  Isolated: 'bg-success/15 text-success border-success/30',
}
