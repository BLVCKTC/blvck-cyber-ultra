export type Severity = "critical" | "high" | "warning" | "info"

export const severityMeta: Record<
  Severity,
  { label: string; token: string; chart: string }
> = {
  critical: {
    label: "Critical",
    token: "critical",
    chart: "var(--critical)",
  },
  high: {
    label: "High",
    token: "high",
    chart: "var(--high)",
  },
  warning: {
    label: "Medium",
    token: "warning",
    chart: "var(--warning)",
  },
  info: {
    label: "Low",
    token: "info",
    chart: "var(--info)",
  },
}


export type ThreatCategory =
  | "Malware"
  | "Phishing"
  | "DDoS"
  | "Brute Force"
  | "Ransomware"
  | "Data Exfiltration"
  | "C2 Beacon"


export const threatCategories: ThreatCategory[] = [
  "Malware",
  "Phishing",
  "DDoS",
  "Brute Force",
  "Ransomware",
  "Data Exfiltration",
  "C2 Beacon",
]


export type ThreatSource = {
  country: string
  code: string
  city: string
  coordinates: [number, number]
}


export const threatSources: ThreatSource[] = [
  {
    country: "Russia",
    code: "RU",
    city: "Moscow",
    coordinates: [37.6, 55.75],
  },
  {
    country: "China",
    code: "CN",
    city: "Beijing",
    coordinates: [116.4, 39.9],
  },
  {
    country: "Nigeria",
    code: "NG",
    city: "Lagos",
    coordinates: [3.38, 6.52],
  },
  {
    country: "South Africa",
    code: "ZA",
    city: "Johannesburg",
    coordinates: [28.04, -26.2],
  },
  {
    country: "United States",
    code: "US",
    city: "Ashburn",
    coordinates: [-77.48, 39.04],
  },
]


export const targetNode = {
  name: "BLVCK CYBER SOC",
  coordinates: [-74, 40.71] as [number, number],
}


export type ThreatEvent = {
  id: string
  timestamp: number

  source: ThreatSource

  category: ThreatCategory
  severity: Severity

  targetAsset: string
  blocked: boolean
  ip: string


  // Threat intelligence fields
  title: string
  region: string
  country: string
  industry: string
  type: string
  technique: string
  tactic: string
  confidence: number

  latitude: number
  longitude: number
}


const targetAssets = [
  "edge-gateway-01",
  "auth-service",
  "payment-api",
  "k8s-prod-cluster",
  "mail-relay-02",
  "vpn-concentrator",
  "s3-customer-data",
]


const industries = [
  "Mining",
  "Finance",
  "Healthcare",
  "Government",
  "Technology",
]


const regions = [
  "Africa",
  "Europe",
  "Asia",
  "North America",
]


const techniques = [
  "T1486 Data Encrypted for Impact",
  "T1566 Phishing",
  "T1046 Network Service Scanning",
  "T1059 Command Execution",
]


const tactics = [
  "Initial Access",
  "Execution",
  "Discovery",
  "Impact",
]


function seededRandom(seed: number) {
  let s = seed % 2147483647

  if (s <= 0) s += 2147483646

  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}


function pick<T>(arr: T[], r: number): T {
  return arr[Math.floor(r * arr.length) % arr.length]
}


function randomIp(r: () => number) {
  return `${Math.floor(r() * 223) + 1}.${Math.floor(
    r() * 255
  )}.${Math.floor(r() * 255)}.${Math.floor(r() * 255)}`
}


function severityByRoll(r: number): Severity {
  if (r > 0.9) return "critical"
  if (r > 0.68) return "high"
  if (r > 0.38) return "warning"

  return "info"
}


export function generateThreatEvents(
  count: number,
  seed = 42
): ThreatEvent[] {

  const r = seededRandom(seed)

  const now = Date.UTC(
    2026,
    6,
    17,
    12,
    0,
    0
  )


  return Array.from(
    { length: count },
    (_, i) => {

      const source = pick(
        threatSources,
        r()
      )

      const severity = severityByRoll(
        r()
      )


      return {

        id: `evt-${seed}-${i}`,

        timestamp:
          now - i * (r() * 45000 + 5000),

        source,

        category: pick(
          threatCategories,
          r()
        ),

        severity,


        targetAsset: pick(
          targetAssets,
          r()
        ),


        blocked:
          r() > 0.18,


        ip:
          randomIp(r),


        title:
          `${pick(
            threatCategories,
            r()
          )} activity detected`,


        region:
          pick(
            regions,
            r()
          ),


        country:
          source.country,


        industry:
          pick(
            industries,
            r()
          ),


        type:
          pick(
            threatCategories,
            r()
          ),


        technique:
          pick(
            techniques,
            r()
          ),


        tactic:
          pick(
            tactics,
            r()
          ),


        confidence:
          Math.floor(
            70 + r() * 30
          ),


        latitude:
          source.coordinates[1],


        longitude:
          source.coordinates[0],

      }
    }
  )
}


// Required by ThreatIntelView

export const threatEvents = generateThreatEvents(80)



export const filterOptions = {

  severity: [
    "All severities",
    "Critical",
    "High",
    "Medium",
    "Low",
  ],


  region: [
    "All regions",
    ...regions,
  ],


  industry: [
    "All industries",
    ...industries,
  ],


  type: [
    "All threat types",
    ...threatCategories,
  ],


  technique: [
    "All techniques",
    ...techniques,
  ],


  tactic: [
    "All tactics",
    ...tactics,
  ],

}



export function randomThreatEvent(): ThreatEvent {

  return generateThreatEvents(
    1,
    Date.now()
  )[0]

}



export type TimeRange =
  | "1h"
  | "24h"
  | "7d"
  | "30d"



export const timeRanges = [
  {
    value: "1h" as TimeRange,
    label: "Last hour",
    points: 12,
  },
  {
    value: "24h" as TimeRange,
    label: "Last 24h",
    points: 24,
  },
  {
    value: "7d" as TimeRange,
    label: "Last 7 days",
    points: 7,
  },
  {
    value: "30d" as TimeRange,
    label: "Last 30 days",
    points: 30,
  },
]



export type TimelinePoint = {
  label: string
  blocked: number
  detected: number
}



export function generateTimeline(
  range: TimeRange
): TimelinePoint[] {

  const cfg =
    timeRanges.find(
      (t) => t.value === range
    )!


  const r =
    seededRandom(
      cfg.points
    )


  return Array.from(
    { length: cfg.points },
    (_, i) => {

      const detected =
        Math.round(
          40 + r() * 120
        )


      return {
        label:
          `${i}`,

        detected,

        blocked:
          Math.round(
            detected * 0.8
          ),
      }

    }
  )
}



export function summarize(
  events: ThreatEvent[]
) {

  return {

    total:
      events.length,


    blocked:
      events.filter(
        e => e.blocked
      ).length,


    critical:
      events.filter(
        e => e.severity === "critical"
      ).length,

  }

}

export const trendData = generateTimeline("24h")