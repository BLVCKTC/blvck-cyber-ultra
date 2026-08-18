"use client";

import { useMemo, useState } from "react";
import {
  Search,
  Play,
  Save,
  Download,
  Upload,
  Sparkles,
  Target,
  Code2,
  BookOpen,
  Grid3x3,
  Clock,
} from "lucide-react";

import { StatCard } from "@/components/shell/stat-card";
import { SeverityBadge } from "@/components/threat-intel/severity-badge";
import { MITRE_TACTICS } from "@/lib/mock-data";

const IOC_SAMPLES = [
  { type: "ip", value: "45.132.192.14", hits: 128, first: "2h ago", country: "Russia", tags: ["c2", "cobalt-strike"] },
  { type: "hash", value: "a1b2c3d4e5f6789...", hits: 42, first: "6h ago", country: "China", tags: ["lockbit", "loader"] },
  { type: "domain", value: "sec-update-mail[.]cc", hits: 316, first: "1d ago", country: "N/A", tags: ["phishing", "banking"] },
  { type: "url", value: "hxxps://ng-payslip[.]top/login.php", hits: 89, first: "4h ago", country: "N/A", tags: ["credential-theft"] },
];

const SIGMA_RULES = [
  { id: "SIG-0421", name: "Suspicious PowerShell base64 execution", tactic: "Execution", severity: "high" as const, hits: 14 },
  { id: "SIG-0512", name: "New service installed by non-admin", tactic: "Persistence", severity: "warning" as const, hits: 5 },
  { id: "SIG-0733", name: "Credential dump via LSASS access", tactic: "Credential Access", severity: "critical" as const, hits: 2 },
  { id: "SIG-0844", name: "DNS tunneling pattern detected", tactic: "Command & Control", severity: "high" as const, hits: 8 },
  { id: "SIG-0901", name: "Impossible travel login", tactic: "Initial Access", severity: "warning" as const, hits: 21 },
];

const AI_SUGGESTIONS = [
  "Show lateral movement from Nigerian offices in the last 24h",
  "Find PowerShell downloads followed by scheduled task creation",
  "Detect Kerberoasting attempts across domain controllers",
  "Users authenticating from 2+ countries within 1 hour",
];

export function HuntingModule() {
  const [query, setQuery] = useState('index=edr sourcetype=process EventCode=4688 CommandLine="*base64*"');
  const [ioc, setIoc] = useState("");
  const [tab, setTab] = useState<"queries" | "iocs" | "yara" | "sigma" | "attack">("queries");
  const [yara, setYara] = useState(`rule LockBit_Loader {
  meta:
    author = "BLVCK CYBER"
    description = "Detects LockBit 3.0 loader variant"
  strings:
    $s1 = "lockbit_bl3ck.exe" ascii wide
    $s2 = { 4D 5A 90 00 03 00 ?? ?? 04 }
    $s3 = "restore-my-files.txt" ascii
  condition:
    uint16(0) == 0x5A4D and 2 of them
}`);

  const rows = useMemo(() => (ioc ? IOC_SAMPLES.filter((r) => r.value.includes(ioc)) : IOC_SAMPLES), [ioc]);

  return (
    <>
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs font-mono uppercase tracking-widest text-cyber">HUNT.MODULE // v3.1</div>
          <h1 className="text-3xl font-display font-bold mt-1">Threat Hunting Platform</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-assisted queries, IOC lookup, YARA/Sigma libraries, MITRE ATT&CK coverage.</p>
        </div>
        <div className="flex gap-2">
          <button className="border border-white/10 rounded-lg px-3 py-2 text-xs font-mono hover:bg-white/5 inline-flex items-center gap-1.5"><Upload className="h-3.5 w-3.5" />Import STIX</button>
          <button className="border border-white/10 rounded-lg px-3 py-2 text-xs font-mono hover:bg-white/5 inline-flex items-center gap-1.5"><Download className="h-3.5 w-3.5" />Export CSV</button>
        </div>
      </div>

<div className="grid grid-cols-2 md:grid-cols-4 gap-4">

  <StatCard
    label="Active Hunts"
    value={12}
    tone="cyber"
    icon={Target}
    change="+3 this week"
    trend="up"
    detail="AI-assisted investigations running"
  />


  <StatCard
    label="IOCs Tracked"
    value="18,412"
    tone="warning"
    icon={Search}
    change="+412 24h"
    trend="up"
    detail="Threat indicators monitored"
  />


  <StatCard
    label="Sigma Rules"
    value={2314}
    tone="success"
    icon={Code2}
    change="Auto-synced"
    trend="up"
    detail="Detection rules active"
  />


  <StatCard
    label="ATT&CK Coverage"
    value="86%"
    tone="cyber"
    icon={Grid3x3}
    change="+4% MoM"
    trend="up"
    detail="Enterprise techniques mapped"
  />

</div>

      <div className="flex gap-1 flex-wrap border-b border-white/10">
        {[
          { k: "queries", label: "AI Hunt Queries", icon: Sparkles },
          { k: "iocs", label: "IOC Search", icon: Search },
          { k: "yara", label: "YARA Editor", icon: Code2 },
          { k: "sigma", label: "Sigma Library", icon: BookOpen },
          { k: "attack", label: "MITRE ATT&CK", icon: Grid3x3 },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.k} onClick={() => setTab(t.k as typeof tab)}
              className={`px-4 py-2.5 text-xs font-mono uppercase tracking-widest inline-flex items-center gap-2 border-b-2 -mb-px transition
                ${tab === t.k ? "border-cyber text-cyber" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
              <Icon className="h-3.5 w-3.5" />{t.label}
            </button>
          );
        })}
      </div>

      {tab === "queries" && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 glass p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-muted-foreground">HUNT QUERY // BLVCK-QL</div>
              <div className="flex gap-2">
                <select className="bg-black/40 border border-white/10 text-xs px-2 py-1 rounded font-mono">
                  <option>Last 24 hours</option><option>Last 7 days</option><option>Last 30 days</option><option>Custom range</option>
                </select>
                <button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold inline-flex items-center gap-1.5"><Play className="h-3 w-3" />Run</button>
                <button className="border border-white/10 px-3 py-1.5 rounded text-xs font-mono inline-flex items-center gap-1.5"><Save className="h-3 w-3" />Save</button>
              </div>
            </div>
            <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={6}
              className="w-full bg-black/60 border border-white/10 rounded p-3 font-mono text-xs text-cyber leading-relaxed" />
            <div className="grid md:grid-cols-3 gap-3 pt-2 border-t border-white/5">
              <div><div className="text-[10px] font-mono uppercase text-muted-foreground">Events matched</div><div className="text-2xl font-display font-bold text-cyber tabular">1,284</div></div>
              <div><div className="text-[10px] font-mono uppercase text-muted-foreground">Assets involved</div><div className="text-2xl font-display font-bold tabular">47</div></div>
              <div><div className="text-[10px] font-mono uppercase text-muted-foreground">Runtime</div><div className="text-2xl font-display font-bold text-success tabular">0.42s</div></div>
            </div>
          </div>
          <div className="glass p-5 space-y-3">
            <div className="flex items-center gap-2 text-cyber"><Sparkles className="h-4 w-4" /><span className="text-xs font-mono uppercase tracking-widest">AI Suggestions</span></div>
            {AI_SUGGESTIONS.map((s, i) => (
              <button key={i} onClick={() => setQuery(s)}
                className="w-full text-left text-sm p-3 rounded-lg border border-white/5 bg-black/30 hover:border-cyber/40 hover:bg-cyber/5 transition">
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {tab === "iocs" && (
        <div className="glass p-5 space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input value={ioc} onChange={(e) => setIoc(e.target.value)} placeholder="Search IP, hash (MD5/SHA1/SHA256), domain or URL…"
                className="w-full bg-black/40 border border-white/10 rounded pl-9 pr-3 py-2.5 text-sm font-mono" />
            </div>
            <button className="bg-cyber text-black px-4 py-2.5 rounded text-xs font-mono font-semibold">Enrich all</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                <tr className="border-b border-white/5"><th className="text-left py-2">Type</th><th className="text-left py-2">Indicator</th><th className="text-left py-2">Hits</th><th className="text-left py-2">First seen</th><th className="text-left py-2">Origin</th><th className="text-left py-2">Tags</th></tr>
              </thead>
              <tbody className="font-mono text-xs">
                {rows.map((r) => (
                  <tr key={r.value} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3"><span className="inline-block bg-cyber/15 text-cyber px-2 py-0.5 rounded uppercase text-[10px]">{r.type}</span></td>
                    <td className="py-3 text-cyber">{r.value}</td>
                    <td className="py-3 tabular">{r.hits}</td>
                    <td className="py-3 text-muted-foreground">{r.first}</td>
                    <td className="py-3">{r.country}</td>
                    <td className="py-3 flex gap-1 flex-wrap">{r.tags.map((t) => <span key={t} className="bg-white/5 px-2 py-0.5 rounded text-[10px]">{t}</span>)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "yara" && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 glass p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs font-mono text-muted-foreground">YARA RULE // LockBit_Loader.yar</div>
              <div className="flex gap-2">
                <button className="border border-white/10 px-3 py-1.5 rounded text-xs font-mono">Test sample</button>
                <button className="bg-cyber text-black px-3 py-1.5 rounded text-xs font-mono font-semibold">Deploy</button>
              </div>
            </div>
            <textarea value={yara} onChange={(e) => setYara(e.target.value)} rows={16}
              className="w-full bg-black/60 border border-white/10 rounded p-3 font-mono text-xs text-success leading-relaxed" />
          </div>
          <div className="glass p-5 space-y-3">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">Test results</div>
            <div className="p-3 rounded bg-success/10 border border-success/30 text-xs font-mono text-success">✓ Rule compiled successfully</div>
            <div className="p-3 rounded bg-warning/10 border border-warning/30 text-xs font-mono text-warning">⚠ 3 samples in vault match this rule</div>
            <div className="pt-3 border-t border-white/5">
              <div className="text-xs font-mono uppercase text-muted-foreground mb-2">Rule stats</div>
              <div className="space-y-1 text-xs"><div className="flex justify-between"><span>Deployed rules</span><span className="text-cyber tabular">1,204</span></div><div className="flex justify-between"><span>Detections (7d)</span><span className="text-warning tabular">89</span></div><div className="flex justify-between"><span>False positives</span><span className="text-success tabular">0.4%</span></div></div>
            </div>
          </div>
        </div>
      )}

      {tab === "sigma" && (
        <div className="glass p-5">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                <tr className="border-b border-white/5"><th className="text-left py-2">Rule ID</th><th className="text-left py-2">Name</th><th className="text-left py-2">MITRE Tactic</th><th className="text-left py-2">Severity</th><th className="text-left py-2">Hits (24h)</th><th></th></tr>
              </thead>
              <tbody>
                {SIGMA_RULES.map((r) => (
                  <tr key={r.id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 font-mono text-xs text-cyber">{r.id}</td>
                    <td className="py-3">{r.name}</td>
                    <td className="py-3 text-xs font-mono text-muted-foreground">{r.tactic}</td>
                    <td className="py-3"><SeverityBadge severity={r.severity} /></td>
                    <td className="py-3 font-mono tabular">{r.hits}</td>
                    <td className="py-3 text-right"><button className="text-xs font-mono text-cyber hover:underline">Deploy →</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "attack" && (
        <div className="glass p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono text-muted-foreground">MITRE ATT&CK NAVIGATOR — Enterprise Matrix</div>
            <div className="flex items-center gap-3 text-[10px] font-mono uppercase text-muted-foreground">
              <span className="inline-flex items-center gap-1"><span className="h-3 w-3 rounded-sm bg-success/60" />Covered</span>
              <span className="inline-flex items-center gap-1"><span className="h-3 w-3 rounded-sm bg-warning/60" />Partial</span>
              <span className="inline-flex items-center gap-1"><span className="h-3 w-3 rounded-sm bg-white/10" />Gap</span>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
            {MITRE_TACTICS.map((t, i) => {
              const cov = (i * 13) % 100;
              const color = cov > 75 ? "bg-success/40 border-success/60" : cov > 40 ? "bg-warning/30 border-warning/50" : "bg-white/5 border-white/10";
              return (
                <div key={t} className={`rounded-lg border p-3 ${color}`}>
                  <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">TA{(i + 1).toString().padStart(4, "0")}</div>
                  <div className="text-sm font-semibold mt-1">{t}</div>
                  <div className="mt-2 flex items-center justify-between text-[10px] font-mono"><span className="text-muted-foreground">Coverage</span><span className="tabular">{cov}%</span></div>
                  <div className="mt-1 h-1 bg-black/40 rounded overflow-hidden"><div className="h-full bg-cyber" style={{ width: `${cov}%` }} /></div>
                </div>
              );
            })}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono pt-2 border-t border-white/5"><Clock className="h-3 w-3" /> Last sync with MITRE: 42 minutes ago</div>
        </div>
      )}
    </>
  );
}
