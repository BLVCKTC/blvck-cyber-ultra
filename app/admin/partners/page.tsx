"use client"

import { useState } from "react"
import { Building2, DollarSign, Users, Palette, ChevronRight, Award } from "lucide-react"
import { PageHeader } from "@/components/shell/page-header"
import { Card, CardContent } from "@/components/ui/card"

const PARTNERS = [
  { name: "Liquid C2 Africa", tier: "Platinum", subs: 42, mrr: 128400, comm: "22%", region: "Pan-Africa" },
  { name: "Dimension Data ZA", tier: "Platinum", subs: 31, mrr: 96200, comm: "22%", region: "Southern Africa" },
  { name: "MainOne Nigeria", tier: "Gold", subs: 18, mrr: 54300, comm: "18%", region: "West Africa" },
  { name: "Safaricom Business", tier: "Gold", subs: 14, mrr: 41800, comm: "18%", region: "East Africa" },
  { name: "Sonatel Cybersec", tier: "Silver", subs: 9, mrr: 22100, comm: "15%", region: "Francophone WA" },
]

const SUBS = [
  { name: "First Bank of Nigeria", industry: "Banking", plan: "Enterprise", mrr: 8400, status: "Active" },
  { name: "MTN Ghana", industry: "Telecom", plan: "Enterprise", mrr: 7200, status: "Active" },
  { name: "Ethiopian Airlines", industry: "Aviation", plan: "Growth", mrr: 3800, status: "Active" },
  { name: "KCB Kenya", industry: "Banking", plan: "Enterprise", mrr: 8100, status: "Trial" },
  { name: "Zambia Revenue Authority", industry: "Government", plan: "Growth", mrr: 3200, status: "Active" },
]

function StatBlock({
  label,
  value,
  icon: Icon,
  tone = "primary",
}: {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  tone?: "primary" | "success" | "warning"
}) {
  const toneClass = { primary: "text-primary", success: "text-success", warning: "text-warning" }[tone]
  return (
    <Card className="glass">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground">{label}</div>
            <div className={`mt-2 font-display text-3xl font-bold tabular-nums ${toneClass}`}>{value}</div>
          </div>
          <Icon className={`size-5 ${toneClass} opacity-70`} />
        </div>
      </CardContent>
    </Card>
  )
}

export default function PartnersPage() {
  const [selected, setSelected] = useState(PARTNERS[0])
  const [brand, setBrand] = useState({ name: "Liquid Cyber Defense", primary: "#00d4ff", secondary: "#0e1520", logo: "LC" })

  return (
    <div>
      <PageHeader
        eyebrow="Admin Portal"
        title="Partner & Reseller Portal"
        description="MSSPs and channel partners running BLVCK CYBER for their own sub-customers."
      />

      <div className="space-y-6 p-4 lg:p-6">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatBlock label="Active partners" value={String(PARTNERS.length)} icon={Building2} />
          <StatBlock label="Sub-customers" value={String(PARTNERS.reduce((a, p) => a + p.subs, 0))} icon={Users} />
          <StatBlock
            label="Channel MRR"
            value={`$${(PARTNERS.reduce((a, p) => a + p.mrr, 0) / 1000).toFixed(1)}k`}
            icon={DollarSign}
            tone="success"
          />
          <StatBlock label="Avg commission" value="19%" icon={Award} tone="warning" />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="glass overflow-hidden lg:col-span-2">
            <div className="border-b border-border/60 px-4 py-3 font-mono text-xs uppercase text-muted-foreground">
              Partners
            </div>
            <table className="w-full text-sm">
              <thead className="bg-black/20 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                <tr>
                  <th className="px-4 py-2 text-left">Partner</th>
                  <th className="py-2 text-left">Tier</th>
                  <th className="py-2 text-left">Sub-customers</th>
                  <th className="py-2 text-left">MRR</th>
                  <th className="py-2 text-left">Commission</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {PARTNERS.map((p) => (
                  <tr
                    key={p.name}
                    onClick={() => setSelected(p)}
                    className={`cursor-pointer border-t border-border/60 ${
                      selected.name === p.name ? "bg-primary/5" : "hover:bg-secondary/30"
                    }`}
                  >
                    <td className="px-4 py-3">
                      <div>{p.name}</div>
                      <div className="text-[10px] text-muted-foreground">{p.region}</div>
                    </td>
                    <td className="py-3">
                      <span
                        className={`rounded px-2 py-0.5 font-mono text-[10px] uppercase ${
                          p.tier === "Platinum"
                            ? "bg-primary/15 text-primary"
                            : p.tier === "Gold"
                              ? "bg-warning/15 text-warning"
                              : "bg-secondary"
                        }`}
                      >
                        {p.tier}
                      </span>
                    </td>
                    <td className="py-3 tabular-nums">{p.subs}</td>
                    <td className="py-3 font-mono text-success">${p.mrr.toLocaleString()}</td>
                    <td className="py-3 font-mono">{p.comm}</td>
                    <td className="py-3 pr-4">
                      <ChevronRight className="size-4 text-muted-foreground" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <Card className="glass space-y-3 p-5">
            <div>
              <div className="font-mono text-[10px] uppercase text-muted-foreground">Partner</div>
              <h3 className="font-display text-lg font-bold">{selected.name}</h3>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <div className="text-muted-foreground">MRR</div>
                <div className="font-mono text-success">${selected.mrr.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Commission (mo)</div>
                <div className="font-mono text-primary">
                  ${Math.round((selected.mrr * parseInt(selected.comm)) / 100).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Sub-customers</div>
                <div className="font-mono">{selected.subs}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Tier</div>
                <div className="font-mono">{selected.tier}</div>
              </div>
            </div>
            <div className="border-t border-border/60 pt-3">
              <div className="mb-2 font-mono text-xs uppercase text-muted-foreground">Recent commission payouts</div>
              {["Jul 2026 — $28,248", "Jun 2026 — $26,102", "May 2026 — $24,981"].map((p, i) => (
                <div key={i} className="flex justify-between border-b border-border/60 py-1.5 text-xs last:border-0">
                  <span>{p.split(" — ")[0]}</span>
                  <span className="font-mono text-success">{p.split(" — ")[1]}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="glass p-5 lg:col-span-2">
            <div className="mb-3 font-mono text-xs uppercase text-muted-foreground">
              {selected.name} — Sub-customers
            </div>
            <table className="w-full text-sm">
              <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                <tr className="border-b border-border/60">
                  <th className="py-2 text-left">Customer</th>
                  <th className="py-2 text-left">Industry</th>
                  <th className="py-2 text-left">Plan</th>
                  <th className="py-2 text-left">MRR</th>
                  <th className="py-2 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {SUBS.map((s) => (
                  <tr key={s.name} className="border-b border-border/60 hover:bg-secondary/30">
                    <td className="py-3">{s.name}</td>
                    <td className="py-3 text-xs text-muted-foreground">{s.industry}</td>
                    <td className="py-3 font-mono text-xs">{s.plan}</td>
                    <td className="py-3 font-mono text-success">${s.mrr.toLocaleString()}</td>
                    <td className="py-3">
                      <span
                        className={`font-mono text-[10px] uppercase ${
                          s.status === "Trial" ? "text-warning" : "text-success"
                        }`}
                      >
                        ● {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <Card className="glass space-y-4 p-5">
            <div className="flex items-center gap-2 text-primary">
              <Palette className="size-4" />
              <span className="font-mono text-xs uppercase tracking-widest">White-label branding</span>
            </div>
            <label className="block">
              <span className="text-xs text-muted-foreground">Product name</span>
              <input
                value={brand.name}
                onChange={(e) => setBrand({ ...brand, name: e.target.value })}
                className="mt-1 w-full rounded border border-border/60 bg-black/20 px-3 py-2 text-sm"
              />
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label>
                <span className="text-xs text-muted-foreground">Primary color</span>
                <input
                  type="color"
                  value={brand.primary}
                  onChange={(e) => setBrand({ ...brand, primary: e.target.value })}
                  className="mt-1 h-10 w-full rounded border border-border/60 bg-black/20"
                />
              </label>
              <label>
                <span className="text-xs text-muted-foreground">Background</span>
                <input
                  type="color"
                  value={brand.secondary}
                  onChange={(e) => setBrand({ ...brand, secondary: e.target.value })}
                  className="mt-1 h-10 w-full rounded border border-border/60 bg-black/20"
                />
              </label>
            </div>
            <div className="rounded-lg border border-border/60 p-4" style={{ background: brand.secondary }}>
              <div className="flex items-center gap-2">
                <div
                  className="grid size-8 place-items-center rounded text-xs font-bold text-black"
                  style={{ background: brand.primary }}
                >
                  {brand.logo}
                </div>
                <div className="text-sm font-bold" style={{ color: brand.primary }}>
                  {brand.name}
                </div>
              </div>
              <div className="mt-3 font-mono text-[10px] opacity-70" style={{ color: brand.primary }}>
                Live white-label preview
              </div>
            </div>
            <button className="w-full rounded-lg bg-primary py-2 font-mono text-xs font-semibold text-black">
              Publish branding
            </button>
          </Card>
        </div>
      </div>
    </div>
  )
}
