"use client";

import Link from "next/link";
import { ParticleField } from "@/components/particle-field";
import { AfricaMap } from "@/components/AfricaMap";
import { LIVE_TICKER_ITEMS, INDUSTRIES } from "@/lib/mock-data";
import { track } from "@/lib/analytics";
import {
  Shield, Zap, Activity, Globe2, Lock, Cpu, Radar, Award,
  Check, ChevronDown, ArrowRight, Building2, Terminal, Bug,
} from "lucide-react";
import { useEffect, useState } from "react";

export default function Page() {
  return (
    <div className="min-h-screen">
      <TopNav />
      <Hero />
      <ThreatTicker />
      <Stats />
      <Features />
      <MapSection />
      <Industries />
      <Testimonials />
      <Pricing />
      <Compliance />
      <FAQ />
      <CTASection />
      <Footer />
    </div>
  );
}

function TopNav() {
  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-white/5 bg-black/60 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-cyber grid place-items-center">
            <span className="font-mono font-bold text-black">B</span>
          </div>
          <div>
            <div className="font-display font-bold tracking-tight leading-none">BLVCK CYBER</div>
            <div className="text-[10px] font-mono text-cyber tracking-[0.2em]">BY BLVCK ONE</div>
          </div>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm">
          <a href="#features" className="text-muted-foreground hover:text-cyber transition">Platform</a>
          <a href="#industries" className="text-muted-foreground hover:text-cyber transition">Industries</a>
          <a href="#pricing" className="text-muted-foreground hover:text-cyber transition">Pricing</a>
          <a href="#compliance" className="text-muted-foreground hover:text-cyber transition">Compliance</a>
          <Link href="/bug-bounty" onClick={() => track("bug_bounty_click", { location: "nav" })} className="text-muted-foreground hover:text-cyber transition inline-flex items-center gap-1.5">
            <Bug className="h-3.5 w-3.5" /> Bug Bounty
          </Link>
          <a href="#faq" className="text-muted-foreground hover:text-cyber transition">FAQ</a>
        </nav>
        <div className="flex items-center gap-2">
          <Link href="/login" className="hidden sm:inline text-sm text-muted-foreground hover:text-cyber px-3 py-2">Sign in</Link>
          <Link href="/demo" className="text-sm font-semibold bg-cyber text-black px-4 py-2 rounded-lg hover:brightness-110 flex items-center gap-1.5 shadow-[0_0_20px_rgba(0,212,255,0.25)]">
            Request Demo <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative pt-16 min-h-[92vh] flex items-center hud-grid overflow-hidden">
      <div className="absolute inset-0"><ParticleField density={80} /></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/30 to-black" />

      <div className="relative max-w-7xl mx-auto px-6 py-24 grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-cyber/30 bg-cyber/5 px-3 py-1 text-xs font-mono text-cyber">
            <span className="h-1.5 w-1.5 rounded-full bg-cyber animate-pulse" />
            AI SOC v4.2 — LIVE ACROSS 14 AFRICAN COUNTRIES
          </div>
          <h1 className="mt-6 text-5xl md:text-7xl font-display font-bold leading-[1.02] tracking-tight">
            Autonomous cyber<br /> defense for <span className="text-cyber text-glow">Africa</span>.
          </h1>
          <p className="mt-6 text-lg text-muted-foreground max-w-xl leading-relaxed">
            BLVCK CYBER detects, investigates and contains threats in seconds — purpose-built for African banks, governments, healthcare, telecoms and enterprises.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/demo" className="bg-cyber text-black font-semibold px-6 py-3 rounded-lg hover:brightness-110 flex items-center gap-2 shadow-[0_0_30px_rgba(0,212,255,0.3)]">
              Request live demo <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/app/soc-demo" className="border border-cyber/40 text-cyber px-6 py-3 rounded-lg hover:bg-cyber/5 flex items-center gap-2">
              <Terminal className="h-4 w-4" /> Try the AI-SOC
            </Link>
            <Link href="/bug-bounty" onClick={() => track("bug_bounty_click", { location: "hero" })} className="border border-white/10 text-muted-foreground hover:text-cyber hover:border-cyber/40 px-6 py-3 rounded-lg flex items-center gap-2 transition">
              <Bug className="h-4 w-4" /> Bug Bounty
            </Link>
          </div>
          <div className="mt-10 grid grid-cols-3 gap-6 max-w-md">
            {[
              ["4.2s", "MTTD"], ["47B+", "Events/day"], ["99.98%", "Uptime"],
            ].map(([v, l]) => (
              <div key={l}>
                <div className="text-2xl font-display font-bold text-cyber tabular">{v}</div>
                <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">{l}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative">
          <HeroDefenseVisualization />
        </div>
      </div>
    </section>
  );
}

function HeroDefenseVisualization() {
  const [events, setEvents] = useState<{ id: number; type: string; sev: string; blocked: boolean }[]>([]);
  useEffect(() => {
    let id = 0;
    const types = ["Ransomware", "Phishing", "DDoS", "Malware", "Zero-Day", "Botnet"];
    const sevs = ["critical", "high", "medium"];
    const t = setInterval(() => {
      setEvents((prev) => [
        { id: id++, type: types[Math.floor(Math.random() * types.length)], sev: sevs[Math.floor(Math.random() * sevs.length)], blocked: Math.random() > 0.1 },
        ...prev.slice(0, 6),
      ]);
    }, 1400);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="glass-strong p-6 relative animate-scan">
      <div className="flex items-center justify-between mb-4">
        <div className="font-mono text-xs text-cyber tracking-widest">AI THREAT MONITOR // LIVE</div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
          <span className="text-success">ACTIVE</span>
        </div>
      </div>

      <div className="relative h-48 mb-4 rounded-lg border border-cyber/20 overflow-hidden bg-black/40">
        <div className="absolute inset-0 hud-grid opacity-50" />
        <div className="absolute inset-0 grid place-items-center">
          <div className="relative">
            <div className="h-24 w-24 rounded-full bg-cyber/20 grid place-items-center animate-pulse-ring">
              <Shield className="h-10 w-10 text-cyber" />
            </div>
          </div>
        </div>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="absolute rounded-full border border-cyber/30" style={{
            inset: `${10 + i * 12}%`, animation: `pulse-ring ${2 + i * 0.5}s ease-out infinite`, animationDelay: `${i * 0.4}s`,
          }} />
        ))}
      </div>

      <div className="space-y-1.5 font-mono text-xs">
        {events.map((e) => (
          <div key={e.id} className="flex items-center justify-between px-3 py-1.5 rounded bg-black/40 border border-white/5">
            <div className="flex items-center gap-2">
              <span className={`h-1.5 w-1.5 rounded-full ${e.sev === "critical" ? "bg-critical" : e.sev === "high" ? "bg-warning" : "bg-cyber"}`} />
              <span className="text-muted-foreground">{e.type}</span>
            </div>
            <span className={e.blocked ? "text-success" : "text-critical"}>{e.blocked ? "BLOCKED" : "ALERT"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ThreatTicker() {
  const items = [...LIVE_TICKER_ITEMS, ...LIVE_TICKER_ITEMS];
  return (
    <div className="border-y border-cyber/20 bg-black/60 overflow-hidden">
      <div className="flex whitespace-nowrap animate-ticker py-3">
        {items.map((t, i) => (
          <div key={i} className="flex items-center gap-3 px-8 font-mono text-xs">
            <span className="text-critical">◉</span>
            <span className="text-muted-foreground">{t}</span>
            <span className="text-cyber opacity-30">//</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Stats() {
  const stats = [
    { v: "14", l: "African countries protected" },
    { v: "220+", l: "Organizations defended" },
    { v: "8.4M", l: "Threats blocked / month" },
    { v: "$2.1B", l: "Damages prevented in 2025" },
  ];
  const trusted = ["TIER-1 BANK", "PAN-AFRICAN TELCO", "FEDERAL MINISTRY", "NATIONAL INSURER", "HEALTH NETWORK", "FINTECH GROUP"];
  return (
    <section className="py-20 border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center text-[10px] font-mono uppercase tracking-[0.35em] text-muted-foreground">
          Trusted by security leaders across Africa
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-10 gap-y-3 opacity-70">
          {trusted.map((t) => (
            <div key={t} className="font-mono text-xs tracking-[0.25em] text-muted-foreground hover:text-cyber transition">
              {t}
            </div>
          ))}
        </div>
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((s) => (
            <div key={s.l} className="glass p-6 text-center">
              <div className="text-4xl font-display font-bold text-cyber tabular">{s.v}</div>
              <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mt-2">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Features() {
  const items = [
    { icon: Zap, title: "AI-Powered Detection", body: "Deep-learning models trained on African threat landscape catch novel attacks in <5 seconds." },
    { icon: Radar, title: "Autonomous Response", body: "Contain, isolate and remediate without waiting for humans. Adjustable auto-response tiers." },
    { icon: Globe2, title: "Regional Threat Intel", body: "Feeds correlated across Nigerian, South African, Kenyan and pan-African adversary campaigns." },
    { icon: Lock, title: "Compliance Ready", body: "POPIA, NDPA, Kenya DPA, PCI, ISO 27001, NIST CSF, HIPAA — mapped out of the box." },
    { icon: Cpu, title: "Cloud + OT + On-Prem", body: "Coverage across AWS/Azure/GCP, ICS/SCADA and legacy datacenter workloads." },
    { icon: Activity, title: "Executive Reporting", body: "Auto-generated board-ready reports, MTTR trends, security posture scores." },
  ];
  return (
    <section id="features" className="py-24">
      <div className="max-w-7xl mx-auto px-6">
        <SectionEyebrow>Platform</SectionEyebrow>
        <h2 className="text-4xl md:text-5xl font-display font-bold mt-2 max-w-3xl">
          A full AI security operations center, delivered as a service.
        </h2>
        <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((i) => (
            <div key={i.title} className="glass p-6 hover:border-cyber/40 transition group">
              <div className="h-10 w-10 rounded-lg bg-cyber/10 grid place-items-center group-hover:bg-cyber/20 transition">
                <i.icon className="h-5 w-5 text-cyber" />
              </div>
              <div className="mt-4 font-display font-semibold text-lg">{i.title}</div>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{i.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function MapSection() {
  return (
    <section className="py-24 border-t border-white/5 relative overflow-hidden">
      <div className="absolute inset-0 hud-grid opacity-30" />
      <div className="relative max-w-7xl mx-auto px-6 grid lg:grid-cols-5 gap-8 items-center">
        <div className="lg:col-span-2">
          <SectionEyebrow>Live threat map</SectionEyebrow>
          <h2 className="text-4xl font-display font-bold mt-2">Africa is the fastest-growing cyber battleground.</h2>
          <p className="mt-4 text-muted-foreground leading-relaxed">
            BLVCK CYBER correlates telemetry from 220+ organizations across 14 countries into one unified threat picture — updated every second.
          </p>
          <div className="mt-6 space-y-2 font-mono text-xs">
            <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-critical" /> High threat activity</div>
            <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-warning" /> Elevated</div>
            <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-cyber" /> Nominal / Monitoring</div>
          </div>
        </div>
        <div className="lg:col-span-3 glass-strong p-4 h-[520px]">
          <AfricaMap />
        </div>
      </div>
    </section>
  );
}

function Industries() {
  return (
    <section id="industries" className="py-24 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <SectionEyebrow>Industries served</SectionEyebrow>
        <h2 className="text-4xl font-display font-bold mt-2">Trusted across critical sectors.</h2>
        <div className="mt-10 grid grid-cols-2 md:grid-cols-5 gap-3">
          {INDUSTRIES.map((n) => (
            <div key={n} className="glass p-5 text-center hover:border-cyber/40 transition">
              <Building2 className="h-5 w-5 text-cyber mx-auto" />
              <div className="mt-3 text-sm font-medium">{n}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Testimonials() {
  const items = [
    { q: "BLVCK CYBER caught a LockBit intrusion before our analysts even opened Slack. Game-changing for African financial services.", a: "Chief Information Security Officer", o: "Tier-1 Nigerian Bank" },
    { q: "Cut our mean-time-to-respond from 4 hours to under 5 minutes. The African-context threat intel is unmatched.", a: "Head of Cybersecurity", o: "Pan-African Telecom" },
    { q: "Board reporting used to take a week. Now it's a click — and we're audit-ready for POPIA on demand.", a: "IT Governance Director", o: "South African Insurer" },
  ];
  return (
    <section className="py-24 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <SectionEyebrow>Customer stories</SectionEyebrow>
        <h2 className="text-4xl font-display font-bold mt-2">Built on trust from Cape Town to Cairo.</h2>
        <div className="mt-10 grid md:grid-cols-3 gap-4">
          {items.map((t) => (
            <div key={t.o} className="glass p-6">
              <div className="text-cyber text-3xl leading-none">"</div>
              <p className="mt-2 text-sm leading-relaxed">{t.q}</p>
              <div className="mt-6 pt-4 border-t border-white/5">
                <div className="text-sm font-medium">{t.a}</div>
                <div className="text-xs text-muted-foreground">{t.o}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    { name: "Starter", price: "$1,499", period: "/mo", desc: "For growing teams under 500 seats", feats: ["AI threat detection", "Managed 24/7 SOC", "Up to 500 endpoints", "Basic compliance reports", "Email support"] },
    { name: "Business", price: "$4,999", period: "/mo", desc: "For mid-market up to 5,000 seats", feats: ["Everything in Starter", "Autonomous response", "Threat intelligence feeds", "POPIA / NDPA / GDPR modules", "24/7 chat & phone support", "Quarterly threat hunts"], highlight: true },
    { name: "Enterprise", price: "Custom", period: "", desc: "Banks, governments, multi-country ops", feats: ["Everything in Business", "Dedicated AI-SOC pod", "Multi-tenant / MSSP mode", "On-prem / air-gap deployment", "Custom compliance frameworks", "Named CISO advisor"] },
  ];
  return (
    <section id="pricing" className="py-24 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <SectionEyebrow>Pricing</SectionEyebrow>
        <h2 className="text-4xl font-display font-bold mt-2">Simple plans, priced in USD.</h2>
        <div className="mt-10 grid md:grid-cols-3 gap-4">
          {plans.map((p) => (
            <div key={p.name} className={`glass p-8 relative ${p.highlight ? "border-cyber/50 ring-1 ring-cyber/30" : ""}`}>
              {p.highlight && <div className="absolute -top-3 left-8 bg-cyber text-black text-xs font-mono px-2 py-0.5 rounded">MOST POPULAR</div>}
              <div className="font-display text-xl font-bold">{p.name}</div>
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-4xl font-display font-bold tabular">{p.price}</span>
                <span className="text-muted-foreground text-sm">{p.period}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{p.desc}</p>
              <ul className="mt-6 space-y-2.5 text-sm">
                {p.feats.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-cyber mt-0.5 shrink-0" /> {f}
                  </li>
                ))}
              </ul>
              <Link href="/demo" className={`mt-8 block text-center py-2.5 rounded-lg font-semibold ${p.highlight ? "bg-cyber text-black" : "border border-cyber/40 text-cyber"}`}>
                {p.name === "Enterprise" ? "Talk to sales" : "Start with " + p.name}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Compliance() {
  const badges = ["ISO 27001", "SOC 2 Type II", "NIST CSF", "PCI DSS 4.0", "GDPR", "POPIA", "NDPA", "Kenya DPA", "HIPAA", "CIS v8"];
  return (
    <section id="compliance" className="py-16 border-t border-white/5 bg-black/40">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center text-xs font-mono uppercase tracking-[0.3em] text-muted-foreground">
          Certified & aligned with
        </div>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {badges.map((b) => (
            <div key={b} className="glass px-4 py-2 flex items-center gap-2">
              <Award className="h-3.5 w-3.5 text-cyber" />
              <span className="text-xs font-mono">{b}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQ() {
  const items = [
    { q: "How fast can BLVCK CYBER be deployed?", a: "Cloud-native customers are onboarded in 48 hours. Full-scale on-prem or air-gapped deployments for banks and governments typically take 2–4 weeks." },
    { q: "Do you have data residency in Africa?", a: "Yes. We operate regional data planes in South Africa (Cape Town), Nigeria (Lagos) and Kenya (Nairobi) with in-country storage." },
    { q: "What frameworks do you help us comply with?", a: "POPIA, NDPA, Kenya DPA, ISO 27001, NIST CSF, PCI DSS 4.0, SOC 2, GDPR, HIPAA and custom sector-specific frameworks." },
    { q: "Can BLVCK CYBER replace our existing SIEM?", a: "Yes — most customers retire their legacy SIEM within 90 days. We also support running alongside Splunk, Sentinel or QRadar." },
    { q: "What's the pricing model?", a: "Flat monthly per plan, plus optional per-endpoint / per-workload metering above plan limits. Enterprise pricing is custom." },
  ];
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="py-24 border-t border-white/5">
      <div className="max-w-4xl mx-auto px-6">
        <SectionEyebrow>Frequently asked</SectionEyebrow>
        <h2 className="text-4xl font-display font-bold mt-2">Questions we hear from CISOs.</h2>
        <div className="mt-10 space-y-2">
          {items.map((it, i) => (
            <div key={i} className="glass overflow-hidden">
              <button onClick={() => setOpen(open === i ? null : i)} className="w-full flex items-center justify-between p-5 text-left">
                <span className="font-medium">{it.q}</span>
                <ChevronDown className={`h-4 w-4 text-cyber transition-transform ${open === i ? "rotate-180" : ""}`} />
              </button>
              {open === i && <div className="px-5 pb-5 text-sm text-muted-foreground leading-relaxed">{it.a}</div>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="py-24 border-t border-white/5 relative overflow-hidden">
      <div className="absolute inset-0"><ParticleField density={40} /></div>
      <div className="relative max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-6xl font-display font-bold tracking-tight">
          Ready to see your <span className="text-cyber text-glow">threat landscape</span>?
        </h2>
        <p className="mt-6 text-lg text-muted-foreground">
          Book a 30-minute demo with our team. We'll walk your environment, tailored to your industry.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/demo" className="bg-cyber text-black font-semibold px-6 py-3 rounded-lg flex items-center gap-2 shadow-[0_0_30px_rgba(0,212,255,0.3)]">
            Request demo <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/app/soc-demo" className="border border-cyber/40 text-cyber px-6 py-3 rounded-lg flex items-center gap-2">
            <Terminal className="h-4 w-4" /> Try AI-SOC simulator
          </Link>
          <Link href="/bug-bounty" onClick={() => track("bug_bounty_click", { location: "cta" })} className="border border-white/10 text-muted-foreground hover:text-cyber hover:border-cyber/40 px-6 py-3 rounded-lg flex items-center gap-2 transition">
            <Bug className="h-4 w-4" /> Report a vulnerability
          </Link>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-white/5 py-12 bg-black/60">
      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-cyber grid place-items-center"><span className="font-mono font-bold text-black text-xs">B</span></div>
            <span className="font-display font-bold">BLVCK CYBER</span>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">A BLVCK One company. Building African digital sovereignty.</p>
        </div>
        {[
          { h: "Platform", links: [["AI SOC", "#features"], ["Threat Intel", "#features"], ["Compliance", "#compliance"], ["Pricing", "#pricing"]] },
          { h: "Company", links: [["About", "#"], ["Careers", "#"], ["Contact", "/demo"], ["Press", "#"]] },
          { h: "Security", links: [["Bug Bounty", "/bug-bounty"], ["Trust Center", "#compliance"], ["Threat Reports", "#"], ["Status", "#"]] },
        ].map((c) => (
          <div key={c.h}>
            <div className="text-xs font-mono uppercase tracking-widest text-cyber">{c.h}</div>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              {c.links.map(([label, href]) => (
                <li key={label}>
                  {href.startsWith("/") ? (
                    <Link
                      href={href}
                      onClick={href === "/bug-bounty" ? () => track("bug_bounty_click", { location: "footer" }) : undefined}
                      className="hover:text-cyber transition"
                    >
                      {label}
                    </Link>
                  ) : (
                    <a href={href} className="hover:text-cyber transition">{label}</a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="max-w-7xl mx-auto px-6 mt-8 pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between gap-2 text-xs text-muted-foreground">
        <div>© 2026 BLVCK One. All rights reserved.</div>
        <div className="font-mono">STATUS: <span className="text-success">● OPERATIONAL</span></div>
      </div>
    </footer>
  );
}

function SectionEyebrow({ children }: { children: React.ReactNode }) {
  return <div className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-[0.3em] text-cyber"><span className="h-px w-6 bg-cyber" />{children}</div>;
}