export type Severity = "Critical" | "High" | "Medium" | "Low"
export type Status = "Open" | "Investigating" | "Contained" | "Resolved"

export const alerts = [
  { id:"ALT-9421", title:"Cobalt Strike beacon detected", severity:"Critical" as Severity, status:"Investigating" as Status, source:"CrowdStrike EDR", asset:"FIN-WS-044", assignee:"Maya Chen", mitre:"T1059.001", time:"2m ago", ioc:"185.220.101.34" },
  { id:"ALT-9418", title:"Impossible travel and token replay", severity:"High" as Severity, status:"Open" as Status, source:"Entra ID", asset:"Identity / j.hayes", assignee:"Unassigned", mitre:"T1078.004", time:"8m ago", ioc:"session:8f91a" },
  { id:"ALT-9414", title:"Sensitive S3 bucket policy modified", severity:"High" as Severity, status:"Investigating" as Status, source:"AWS GuardDuty", asset:"prod-finance-archive", assignee:"Noah Kim", mitre:"T1098", time:"19m ago", ioc:"arn:aws:s3:::prod-finance" },
  { id:"ALT-9409", title:"PowerShell encoded command", severity:"Medium" as Severity, status:"Contained" as Status, source:"Microsoft Defender", asset:"HR-LT-119", assignee:"Avery Singh", mitre:"T1027", time:"31m ago", ioc:"SHA256:7e5…c19" },
  { id:"ALT-9402", title:"Outbound DNS tunneling pattern", severity:"Medium" as Severity, status:"Open" as Status, source:"Corelight NDR", asset:"ENG-SRV-08", assignee:"Unassigned", mitre:"T1071.004", time:"46m ago", ioc:"updates-cdn[.]cloud" },
  { id:"ALT-9391", title:"Repeated privileged login failures", severity:"Low" as Severity, status:"Resolved" as Status, source:"Okta", asset:"Identity / svc_build", assignee:"Maya Chen", mitre:"T1110", time:"1h ago", ioc:"10.44.18.21" },
]

export const assets = [
  { id:"AST-0014", name:"FIN-WS-044", type:"Endpoint", os:"Windows 11", criticality:"Critical", owner:"Elena Ortiz", vulnerabilities:12, edr:"Protected", health:72, exposure:84, ip:"10.42.18.44", tags:["Finance","PCI"] },
  { id:"AST-0088", name:"prod-api-gateway", type:"Cloud", os:"Amazon Linux", criticality:"Critical", owner:"Platform SOC", vulnerabilities:4, edr:"Protected", health:91, exposure:48, ip:"10.20.4.18", tags:["AWS","Production"] },
  { id:"AST-0112", name:"ENG-SRV-08", type:"Server", os:"Ubuntu 22.04", criticality:"High", owner:"DevOps", vulnerabilities:28, edr:"Degraded", health:58, exposure:76, ip:"10.44.12.8", tags:["Engineering"] },
  { id:"AST-0192", name:"Salesforce", type:"SaaS", os:"Managed", criticality:"High", owner:"RevOps", vulnerabilities:2, edr:"N/A", health:87, exposure:36, ip:"External", tags:["Customer data","SOC2"] },
  { id:"AST-0235", name:"HR-LT-119", type:"Endpoint", os:"macOS 15", criticality:"Medium", owner:"People Ops", vulnerabilities:7, edr:"Protected", health:83, exposure:41, ip:"10.31.8.119", tags:["Remote"] },
]

export const frameworks = [
  { name:"ISO 27001", score:91, controls:93, failed:7, evidence:88 }, { name:"NIST CSF", score:87, controls:88, failed:12, evidence:84 },
  { name:"CIS Controls", score:82, controls:81, failed:19, evidence:79 }, { name:"SOC 2", score:94, controls:96, failed:4, evidence:92 },
  { name:"HIPAA", score:86, controls:89, failed:11, evidence:81 }, { name:"PCI DSS", score:78, controls:76, failed:24, evidence:74 },
]

export const reports = [
  { name:"Executive Risk Brief", type:"Executive", schedule:"Monthly", lastRun:"Jul 15, 2026", format:"PDF", status:"Delivered" },
  { name:"SOC Operations Review", type:"SOC", schedule:"Weekly", lastRun:"Jul 18, 2026", format:"PDF", status:"Delivered" },
  { name:"Critical Vulnerabilities", type:"Vulnerability", schedule:"Daily", lastRun:"Today, 06:00", format:"CSV", status:"Delivered" },
  { name:"Threat Landscape Q2", type:"Threat", schedule:"Quarterly", lastRun:"Jul 1, 2026", format:"PDF", status:"Delivered" },
]

export const team = [
  { name:"Maya Chen", initials:"MC", role:"SOC Lead", shift:"Day", availability:"Online", cases:8, workload:68, response:"4m", score:96 },
  { name:"Noah Kim", initials:"NK", role:"Senior Analyst", shift:"Day", availability:"In case", cases:11, workload:86, response:"6m", score:92 },
  { name:"Avery Singh", initials:"AS", role:"Threat Hunter", shift:"Swing", availability:"Online", cases:6, workload:51, response:"8m", score:94 },
  { name:"Omar Haddad", initials:"OH", role:"L2 Analyst", shift:"Night", availability:"Off shift", cases:4, workload:34, response:"11m", score:88 },
]

export const tenants = [
  { name:"Northstar Financial", plan:"Enterprise", users:4820, license:82, storage:68, health:94, alerts:14, region:"US East", isolation:"Enforced" },
  { name:"Helix Healthcare", plan:"Enterprise", users:3110, license:76, storage:54, health:89, alerts:23, region:"US Central", isolation:"Enforced" },
  { name:"Aperture Logistics", plan:"Business", users:1280, license:64, storage:41, health:81, alerts:31, region:"EU West", isolation:"Enforced" },
  { name:"Orion Retail Group", plan:"Business", users:2450, license:91, storage:83, health:76, alerts:47, region:"US West", isolation:"Review" },
]

export const settingsGroups = [
  { title:"Identity & access", items:["Authentication","SSO / SAML","MFA enforcement","OIDC providers","RBAC","Security policies"] },
  { title:"Platform", items:["API keys","Webhooks","Email notifications","Integrations","Secrets management","Feature flags"] },
  { title:"Data & experience", items:["Retention","Storage","Branding","Appearance","SOC preferences","Detection tuning","Audit logging"] },
]
