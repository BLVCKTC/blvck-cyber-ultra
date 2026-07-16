// Realistic AI-SOC mock data + live simulation helpers for BLVCK CYBER

export type Severity = "critical" | "high" | "warning" | "info"
export type ThreatStatus = "detected" | "investigating" | "contained" | "blocked"

export type ThreatType =
  | "Ransomware"
  | "Phishing"
  | "Brute Force"
  | "SQL Injection"
  | "DDoS"
  | "Malware"
  | "Insider Threat"
  | "Privilege Escalation"
  | "Data Exfiltration"
  | "Zero-Day Exploit"
  | "Botnet C2"
  | "Credential Stuffing"

export interface Threat {
  id: string
  type: ThreatType
  severity: Severity
  status: ThreatStatus
  sourceIp: string
  sourceCountry: string
  target: string
  timestamp: number
  aiConfidence: number
  description: string
  mitre: string
}

export interface Vulnerability {
  id: string
  cve: string
  title: string
  severity: Severity
  cvss: number
  asset: string
  status: "open" | "in-progress" | "remediated"
  discovered: string
  exploitAvailable: boolean
}

export interface HealthMetric {
  label: string
  value: number
  status: "healthy" | "degraded" | "critical"
  detail: string
}

export interface Alert {
  id: string
  message: string
  severity: Severity
  time: string
}

const COUNTRIES = [
  "Nigeria",
  "Russia",
  "China",
  "United States",
  "Kenya",
  "South Africa",
  "Brazil",
  "India",
  "Germany",
  "Iran",
  "North Korea",
  "Ghana",
]

const TARGETS = [
  "core-banking-db-01",
  "web-gateway-lb",
  "auth-service",
  "payment-api",
  "hr-fileshare",
  "mail-relay-02",
  "vpn-concentrator",
  "customer-portal",
  "swift-bridge",
  "k8s-prod-cluster",
]

const THREAT_TYPES: { type: ThreatType; sev: Severity; mitre: string; desc: string }[] = [
  { type: "Ransomware", sev: "critical", mitre: "T1486", desc: "Mass file-encryption behavior detected on endpoint" },
  { type: "Zero-Day Exploit", sev: "critical", mitre: "T1190", desc: "Unknown exploit signature against public-facing app" },
  { type: "Data Exfiltration", sev: "critical", mitre: "T1041", desc: "Anomalous outbound transfer to unknown host" },
  { type: "SQL Injection", sev: "high", mitre: "T1190", desc: "Malicious query pattern against database layer" },
  { type: "Privilege Escalation", sev: "high", mitre: "T1068", desc: "Unexpected privilege change on service account" },
  { type: "Malware", sev: "high", mitre: "T1204", desc: "Trojan dropper flagged by AI behavioral engine" },
  { type: "Botnet C2", sev: "high", mitre: "T1071", desc: "Beaconing to known command-and-control infra" },
  { type: "Brute Force", sev: "warning", mitre: "T1110", desc: "Repeated failed authentication attempts" },
  { type: "Credential Stuffing", sev: "warning", mitre: "T1110", desc: "Distributed login attempts with leaked credentials" },
  { type: "DDoS", sev: "warning", mitre: "T1498", desc: "Traffic volume spike from distributed sources" },
  { type: "Phishing", sev: "warning", mitre: "T1566", desc: "Suspicious email with credential-harvesting link" },
  { type: "Insider Threat", sev: "info", mitre: "T1078", desc: "Unusual data access outside normal hours" },
]

function randIp() {
  return `${rnd(11, 223)}.${rnd(0, 255)}.${rnd(0, 255)}.${rnd(1, 254)}`
}
function rnd(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}
function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

let counter = 0
export function makeThreat(now = Date.now()): Threat {
  const t = pick(THREAT_TYPES)
  const statuses: ThreatStatus[] = ["detected", "investigating", "contained", "blocked"]
  counter += 1
  return {
    id: `THR-${(now % 100000).toString().padStart(5, "0")}-${counter}`,
    type: t.type,
    severity: t.sev,
    status: pick(statuses),
    sourceIp: randIp(),
    sourceCountry: pick(COUNTRIES),
    target: pick(TARGETS),
    timestamp: now,
    aiConfidence: rnd(82, 99),
    description: t.desc,
    mitre: t.mitre,
  }
}

export function seedThreats(n: number): Threat[] {
  const now = Date.now()
  return Array.from({ length: n }, (_, i) => makeThreat(now - i * rnd(20000, 90000)))
}

export const vulnerabilities: Vulnerability[] = [
  { id: "V1", cve: "CVE-2024-3094", title: "XZ Utils backdoor in SSH auth path", severity: "critical", cvss: 10.0, asset: "vpn-concentrator", status: "in-progress", discovered: "2h ago", exploitAvailable: true },
  { id: "V2", cve: "CVE-2023-4863", title: "Heap buffer overflow in WebP decoder", severity: "critical", cvss: 9.6, asset: "customer-portal", status: "open", discovered: "5h ago", exploitAvailable: true },
  { id: "V3", cve: "CVE-2024-21762", title: "FortiOS out-of-bounds write RCE", severity: "critical", cvss: 9.8, asset: "web-gateway-lb", status: "open", discovered: "1d ago", exploitAvailable: true },
  { id: "V4", cve: "CVE-2023-34362", title: "MOVEit Transfer SQL injection", severity: "high", cvss: 8.8, asset: "core-banking-db-01", status: "in-progress", discovered: "1d ago", exploitAvailable: true },
  { id: "V5", cve: "CVE-2024-1709", title: "ConnectWise auth bypass", severity: "high", cvss: 8.4, asset: "auth-service", status: "remediated", discovered: "3d ago", exploitAvailable: false },
  { id: "V6", cve: "CVE-2023-46604", title: "Apache ActiveMQ RCE", severity: "high", cvss: 8.1, asset: "mail-relay-02", status: "open", discovered: "4d ago", exploitAvailable: true },
  { id: "V7", cve: "CVE-2024-27198", title: "TeamCity auth bypass", severity: "warning", cvss: 6.5, asset: "k8s-prod-cluster", status: "in-progress", discovered: "5d ago", exploitAvailable: false },
  { id: "V8", cve: "CVE-2023-38831", title: "WinRAR arbitrary code execution", severity: "warning", cvss: 6.1, asset: "hr-fileshare", status: "remediated", discovered: "1w ago", exploitAvailable: false },
]

export const healthMetrics: HealthMetric[] = [
  { label: "Server Health", value: 96, status: "healthy", detail: "42/44 nodes nominal" },
  { label: "Database Performance", value: 88, status: "healthy", detail: "Latency 12ms avg" },
  { label: "Network Stability", value: 72, status: "degraded", detail: "Packet loss on edge-3" },
  { label: "Device Security", value: 91, status: "healthy", detail: "1,204 endpoints managed" },
  { label: "System Uptime", value: 99.98, status: "healthy", detail: "99.98% 30-day SLA" },
  { label: "Data Protection", value: 64, status: "critical", detail: "3 unencrypted volumes" },
]

export const attackTrend = [
  { time: "00:00", detected: 42, blocked: 40 },
  { time: "03:00", detected: 31, blocked: 30 },
  { time: "06:00", detected: 58, blocked: 55 },
  { time: "09:00", detected: 124, blocked: 118 },
  { time: "12:00", detected: 168, blocked: 159 },
  { time: "15:00", detected: 142, blocked: 137 },
  { time: "18:00", detected: 96, blocked: 93 },
  { time: "21:00", detected: 74, blocked: 72 },
]

export const severityLabels: Record<Severity, string> = {
  critical: "Critical",
  high: "High",
  warning: "Medium",
  info: "Low",
}

export const alerts: Alert[] = [
  { id: "A1", message: "AI detected possible ransomware behavior on core-banking-db-01 and blocked the attack.", severity: "critical", time: "2 min ago" },
  { id: "A2", message: "Critical vulnerability (CVE-2024-3094) discovered on your VPN concentrator.", severity: "critical", time: "18 min ago" },
  { id: "A3", message: "Suspicious login detected from an unknown location (Iran).", severity: "high", time: "41 min ago" },
  { id: "A4", message: "New vulnerability detected during scheduled penetration test.", severity: "warning", time: "1 hr ago" },
  { id: "A5", message: "Your cybersecurity score decreased by 3 points.", severity: "info", time: "2 hr ago" },
]
