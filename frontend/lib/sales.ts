export type LeadStage = "new" | "qualified" | "demo" | "proposal" | "negotiation" | "won" | "lost"
export type LeadSource = "Inbound" | "Referral" | "Outbound" | "Event" | "Partner"

export type Lead = {
  id: string
  company: string
  contactName: string
  title: string
  email: string
  stage: LeadStage
  value: number
  source: LeadSource
  owner: string
  region: string
  probability: number
  createdAt: string
  lastActivityAt: string
  note: string
}

export const LEAD_STAGES: LeadStage[] = [
  "new",
  "qualified",
  "demo",
  "proposal",
  "negotiation",
  "won",
  "lost",
]

export const STAGE_LABEL: Record<LeadStage, string> = {
  new: "New",
  qualified: "Qualified",
  demo: "Demo",
  proposal: "Proposal",
  negotiation: "Negotiation",
  won: "Won",
  lost: "Lost",
}

// Pipeline stages considered "open" (still in play)
export const OPEN_STAGES: LeadStage[] = ["new", "qualified", "demo", "proposal", "negotiation"]

export const SOURCES: LeadSource[] = ["Inbound", "Referral", "Outbound", "Event", "Partner"]

export const leads: Lead[] = [
  {
    id: "LEAD-4001",
    company: "Silverline Payments",
    contactName: "Rebecca Cho",
    title: "CISO",
    email: "r.cho@silverlinepay.com",
    stage: "negotiation",
    value: 21600,
    source: "Referral",
    owner: "Devon Clarke",
    region: "North America",
    probability: 80,
    createdAt: "2026-05-12",
    lastActivityAt: "2026-07-14",
    note: "Security committee sign-off pending; contract in legal review.",
  },
  {
    id: "LEAD-4002",
    company: "Helios Grid Utilities",
    contactName: "Martin Feld",
    title: "VP Infrastructure",
    email: "m.feld@heliosgrid.com",
    stage: "proposal",
    value: 34800,
    source: "Outbound",
    owner: "Priya Nair",
    region: "Europe",
    probability: 60,
    createdAt: "2026-04-30",
    lastActivityAt: "2026-07-11",
    note: "Sent Enterprise proposal covering 6 OT sites. Awaiting budget approval.",
  },
  {
    id: "LEAD-4003",
    company: "Cobalt Gaming",
    contactName: "Tyler Brooks",
    title: "Head of IT",
    email: "tyler@cobaltgaming.gg",
    stage: "demo",
    value: 5400,
    source: "Inbound",
    owner: "Sasha Lin",
    region: "North America",
    probability: 45,
    createdAt: "2026-06-18",
    lastActivityAt: "2026-07-15",
    note: "Technical demo delivered; evaluating against incumbent EDR.",
  },
  {
    id: "LEAD-4004",
    company: "Meadowbrook Schools",
    contactName: "Angela Ruiz",
    title: "Director of Technology",
    email: "a.ruiz@meadowbrook.edu",
    stage: "qualified",
    value: 3600,
    source: "Event",
    owner: "Sasha Lin",
    region: "North America",
    probability: 30,
    createdAt: "2026-06-25",
    lastActivityAt: "2026-07-09",
    note: "Met at EDUSEC conference. Grant funding confirmed for Q4.",
  },
  {
    id: "LEAD-4005",
    company: "Nimbus Cloud Services",
    contactName: "Priyanka Rao",
    title: "SecOps Lead",
    email: "p.rao@nimbuscloud.io",
    stage: "negotiation",
    value: 15900,
    source: "Partner",
    owner: "Devon Clarke",
    region: "Asia Pacific",
    probability: 75,
    createdAt: "2026-05-02",
    lastActivityAt: "2026-07-13",
    note: "MSSP partner co-sell. Finalizing seat count.",
  },
  {
    id: "LEAD-4006",
    company: " Portside Freight",
    contactName: "Gunnar Holm",
    title: "IT Manager",
    email: "g.holm@portsidefreight.no",
    stage: "new",
    value: 4800,
    source: "Inbound",
    owner: "Priya Nair",
    region: "Europe",
    probability: 15,
    createdAt: "2026-07-10",
    lastActivityAt: "2026-07-12",
    note: "Downloaded ransomware readiness whitepaper; requested pricing.",
  },
  {
    id: "LEAD-4007",
    company: "Crestwood Capital",
    contactName: "Dana Wexler",
    title: "COO",
    email: "d.wexler@crestwoodcap.com",
    stage: "proposal",
    value: 27200,
    source: "Referral",
    owner: "Devon Clarke",
    region: "North America",
    probability: 55,
    createdAt: "2026-05-20",
    lastActivityAt: "2026-07-08",
    note: "Fortress tier proposal sent. Comparing against two competitors.",
  },
  {
    id: "LEAD-4008",
    company: "Vanta Logistics",
    contactName: "Sofia Marchetti",
    title: "CTO",
    email: "s.marchetti@vantalog.it",
    stage: "won",
    value: 12600,
    source: "Outbound",
    owner: "Priya Nair",
    region: "Europe",
    probability: 100,
    createdAt: "2026-03-14",
    lastActivityAt: "2026-06-30",
    note: "Closed-won. Guardian tier, 130 seats. Onboarding scheduled.",
  },
  {
    id: "LEAD-4009",
    company: "Aster Pharmaceuticals",
    contactName: "Dr. Owen Blake",
    title: "Head of Compliance",
    email: "o.blake@asterpharma.com",
    stage: "demo",
    value: 19800,
    source: "Event",
    owner: "Sasha Lin",
    region: "North America",
    probability: 40,
    createdAt: "2026-06-05",
    lastActivityAt: "2026-07-10",
    note: "HIPAA-focused eval. Second demo with security team next week.",
  },
  {
    id: "LEAD-4010",
    company: "Baywater Municipal",
    contactName: "Karen Ellison",
    title: "CIO",
    email: "k.ellison@baywater.gov",
    stage: "qualified",
    value: 16400,
    source: "Inbound",
    owner: "Devon Clarke",
    region: "North America",
    probability: 35,
    createdAt: "2026-06-12",
    lastActivityAt: "2026-07-07",
    note: "Public sector RFP expected in August. Strong fit.",
  },
  {
    id: "LEAD-4011",
    company: "Northgate Retail Group",
    contactName: "Felix Danko",
    title: "VP Security",
    email: "f.danko@northgateretail.com",
    stage: "lost",
    value: 8900,
    source: "Outbound",
    owner: "Sasha Lin",
    region: "Europe",
    probability: 0,
    createdAt: "2026-04-08",
    lastActivityAt: "2026-06-22",
    note: "Lost to incumbent renewal. Revisit in 12 months.",
  },
  {
    id: "LEAD-4012",
    company: "Quantum Dynamics Lab",
    contactName: "Aisha Bello",
    title: "Research IT Director",
    email: "a.bello@quantumdyn.org",
    stage: "won",
    value: 9600,
    source: "Referral",
    owner: "Priya Nair",
    region: "North America",
    probability: 100,
    createdAt: "2026-04-01",
    lastActivityAt: "2026-06-18",
    note: "Closed-won. Guardian tier. Expansion opportunity flagged.",
  },
  {
    id: "LEAD-4013",
    company: "Emberline Media",
    contactName: "Chris Nakamura",
    title: "Head of IT",
    email: "chris@emberline.media",
    stage: "new",
    value: 2400,
    source: "Inbound",
    owner: "Sasha Lin",
    region: "North America",
    probability: 10,
    createdAt: "2026-07-14",
    lastActivityAt: "2026-07-15",
    note: "Trial signup from website. Nurture sequence started.",
  },
  {
    id: "LEAD-4014",
    company: "Solaris Renewables",
    contactName: "Lena Fischer",
    title: "CISO",
    email: "l.fischer@solarisrenew.de",
    stage: "proposal",
    value: 22800,
    source: "Partner",
    owner: "Priya Nair",
    region: "Europe",
    probability: 65,
    createdAt: "2026-05-16",
    lastActivityAt: "2026-07-12",
    note: "OT + IT coverage proposal. Partner-sourced, high intent.",
  },
]

// Monthly closed revenue (new business booked), last 8 months
export type RevenuePoint = { month: string; booked: number; target: number }

export const revenueTrend: RevenuePoint[] = [
  { month: "Dec", booked: 41000, target: 45000 },
  { month: "Jan", booked: 52000, target: 48000 },
  { month: "Feb", booked: 47500, target: 50000 },
  { month: "Mar", booked: 61000, target: 55000 },
  { month: "Apr", booked: 58000, target: 58000 },
  { month: "May", booked: 72000, target: 62000 },
  { month: "Jun", booked: 68500, target: 66000 },
  { month: "Jul", booked: 79000, target: 70000 },
]

export type RepPerformance = {
  name: string
  bookedMrr: number
  dealsWon: number
  quotaAttainment: number
}

export const repPerformance: RepPerformance[] = [
  { name: "Devon Clarke", bookedMrr: 34200, dealsWon: 9, quotaAttainment: 118 },
  { name: "Priya Nair", bookedMrr: 28600, dealsWon: 7, quotaAttainment: 104 },
  { name: "Sasha Lin", bookedMrr: 16400, dealsWon: 11, quotaAttainment: 92 },
]

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatCompact(value: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value)
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}
