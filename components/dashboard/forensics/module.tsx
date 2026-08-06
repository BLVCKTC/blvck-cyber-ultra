"use client";

import { useState } from "react";
import {
  FolderOpen,
  ShieldCheck,
  HardDrive,
  Cpu,
  ScrollText,
  Clock,
  Bug,
  FileSignature,
  ChevronRight,
} from "lucide-react";

import { StatCard } from "@/components/shell/stat-card";
import { SeverityBadge } from "@/components/threat-intel/severity-badge";

const CASES = [
  { id: "IR-2026-0412", title: "Ransomware — First Bank Lagos Branch", severity: "critical" as const, status: "Active", lead: "K. Mensah", opened: "2d ago", evidence: 34, tags: ["LockBit", "banking"] },
  { id: "IR-2026-0411", title: "Insider data exfiltration — MTN Ghana", severity: "high" as const, status: "Analyzing", lead: "A. Okafor", opened: "5d ago", evidence: 18, tags: ["insider", "telecom"] },
  { id: "IR-2026-0409", title: "Phishing campaign — SA Revenue Service", severity: "warning" as const, status: "Contained", lead: "T. Dlamini", opened: "1w ago", evidence: 12, tags: ["phishing"] },
  { id: "IR-2026-0405", title: "Credential stuffing — Equity Bank KE", severity: "high" as const, status: "Reporting", lead: "J. Wanjiru", opened: "2w ago", evidence: 27, tags: ["auth", "banking"] },
];

const CUSTODY = [
  { time: "2026-07-20 09:14 UTC", actor: "K. Mensah", action: "Evidence collected", target: "DC01 — Memory image (16 GB)", hash: "sha256:af13…9c4e" },
  { time: "2026-07-20 09:47 UTC", actor: "System", action: "Hash verified", target: "DC01 — Memory image", hash: "sha256:af13…9c4e" },
  { time: "2026-07-20 11:02 UTC", actor: "A. Okafor", action: "Transferred to analysis vault", target: "vault://ir-2026-0412/mem", hash: "sha256:af13…9c4e" },
  { time: "2026-07-20 14:38 UTC", actor: "Volatility 3", action: "Analysis run", target: "malfind, pslist, netscan", hash: "—" },
  { time: "2026-07-21 08:11 UTC", actor: "K. Mensah", action: "Sealed for legal export", target: "case-package.ir-2026-0412.zip", hash: "sha256:be22…104a" },
];

const TIMELINE = [
  { t: "T-0", ts: "09:12:04", ev: "Initial phishing email delivered to accounts@firstbank.ng", sev: "warning" as const },
  { t: "T+00:03", ts: "09:15:22", ev: "Macro executed → PowerShell downloader", sev: "high" as const },
  { t: "T+00:11", ts: "09:23:41", ev: "Persistence: scheduled task 'Windows_Update_Svc' created", sev: "high" as const },
  { t: "T+00:34", ts: "09:46:10", ev: "LSASS memory dumped, credentials exfiltrated", sev: "critical" as const },
  { t: "T+01:12", ts: "10:24:03", ev: "Lateral movement to DC01 via SMB", sev: "critical" as const },
  { t: "T+02:44", ts: "11:56:19", ev: "LockBit encryptor deployed on 47 hosts", sev: "critical" as const },
];

export default function ForensicsPage() {
  const [tab, setTab] = useState<"cases" | "custody" | "disk" | "memory" | "timeline" | "sandbox">("cases");
  const [active, setActive] = useState(CASES[0]);

  return (
    <>
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs font-mono uppercase tracking-widest text-cyber">DFIR.MODULE // v2.4</div>
          <h1 className="text-3xl font-display font-bold mt-1">Digital Forensics</h1>
          <p className="text-sm text-muted-foreground mt-1">Court-defensible incident investigation with automatic chain of custody.</p>
        </div>
        <button className="bg-cyber text-black rounded-lg px-4 py-2 text-xs font-mono font-semibold inline-flex items-center gap-2"><FolderOpen className="h-3.5 w-3.5" />Open new case</button>
      </div>

<div className="grid grid-cols-2 md:grid-cols-4 gap-4">

  <StatCard
    label="Active Cases"
    value={String(CASES.filter((c) => c.status === "Active").length)}
    change="+1 critical"
    trend="up"
    icon={Bug}
    detail="Currently under investigation"
  />

  <StatCard
    label="Evidence Items"
    value="1,214"
    change="+34"
    trend="up"
    icon={HardDrive}
    detail="Collected this week"
  />

  <StatCard
    label="Avg MTTR"
    value="3.4 days"
    change="-0.8d"
    trend="down"
    icon={Clock}
    detail="Month over month"
  />

  <StatCard
    label="Chain of Custody"
    value="100%"
    change="0 breaks"
    trend="up"
    icon={ShieldCheck}
    detail="Evidence integrity verified"
  />

</div>

      <div className="flex gap-1 flex-wrap border-b border-white/10">
        {[
          { k: "cases", label: "Cases", icon: FolderOpen },
          { k: "custody", label: "Chain of Custody", icon: ShieldCheck },
          { k: "disk", label: "Disk Analysis", icon: HardDrive },
          { k: "memory", label: "Memory Analysis", icon: Cpu },
          { k: "timeline", label: "Timeline", icon: Clock },
          { k: "sandbox", label: "Sandbox", icon: Bug },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.k} onClick={() => setTab(t.k as typeof tab)}
              className={`px-4 py-2.5 text-xs font-mono uppercase tracking-widest inline-flex items-center gap-2 border-b-2 -mb-px
                ${tab === t.k ? "border-cyber text-cyber" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
              <Icon className="h-3.5 w-3.5" />{t.label}
            </button>
          );
        })}
      </div>

      {tab === "cases" && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 glass p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground bg-black/30">
                <tr><th className="text-left px-4 py-3">Case</th><th className="text-left py-3">Severity</th><th className="text-left py-3">Status</th><th className="text-left py-3">Lead</th><th className="text-left py-3">Evidence</th><th></th></tr>
              </thead>
              <tbody>
                {CASES.map((c) => (
                  <tr key={c.id} onClick={() => setActive(c)} className={`border-t border-white/5 cursor-pointer ${active.id === c.id ? "bg-cyber/5" : "hover:bg-white/5"}`}>
                    <td className="px-4 py-3"><div className="text-xs font-mono text-cyber">{c.id}</div><div className="text-sm">{c.title}</div><div className="mt-1 flex gap-1">{c.tags.map((t) => <span key={t} className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded">{t}</span>)}</div></td>
                    <td className="py-3"><SeverityBadge severity={c.severity} /></td>
                    <td className="py-3 text-xs font-mono">{c.status}</td>
                    <td className="py-3 text-xs">{c.lead}</td>
                    <td className="py-3 tabular text-xs">{c.evidence}</td>
                    <td className="py-3 pr-4"><ChevronRight className="h-4 w-4 text-muted-foreground" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="glass p-5 space-y-4">
            <div><div className="text-[10px] font-mono uppercase text-muted-foreground">Case</div><div className="text-xs font-mono text-cyber">{active.id}</div><h3 className="font-display font-bold text-lg mt-1">{active.title}</h3></div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div><div className="text-muted-foreground">Severity</div><SeverityBadge severity={active.severity} /></div>
              <div><div className="text-muted-foreground">Status</div><div className="font-mono">{active.status}</div></div>
              <div><div className="text-muted-foreground">Lead</div><div>{active.lead}</div></div>
              <div><div className="text-muted-foreground">Opened</div><div>{active.opened}</div></div>
            </div>
            <div className="pt-3 border-t border-white/5 space-y-2">
              <div className="text-xs font-mono uppercase text-muted-foreground">Evidence workflow</div>
              {["Collected — 34 items", "Hashes verified (SHA-256)", "Analysis in progress", "Report draft: 42%"].map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-xs"><div className={`h-2 w-2 rounded-full ${i < 2 ? "bg-success" : i === 2 ? "bg-warning animate-pulse" : "bg-white/20"}`} />{s}</div>
              ))}
            </div>
            <button className="w-full bg-cyber text-black rounded-lg py-2 text-xs font-mono font-semibold">Open full case →</button>
          </div>
        </div>
      )}

      {tab === "custody" && (
        <div className="glass p-5">
          <div className="text-xs font-mono uppercase text-muted-foreground mb-3">Chain of custody — {active.id}</div>
          <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-cyber/30">
            {CUSTODY.map((c, i) => (
              <div key={i} className="relative">
                <div className="absolute -left-6 top-1.5 h-3 w-3 rounded-full bg-cyber ring-4 ring-cyber/20" />
                <div className="flex justify-between items-start flex-wrap gap-2">
                  <div><div className="text-sm font-semibold">{c.action}</div><div className="text-xs text-muted-foreground">{c.target}</div></div>
                  <div className="text-right text-[10px] font-mono text-muted-foreground"><div>{c.time}</div><div className="text-cyber">{c.actor}</div></div>
                </div>
                <div className="mt-1 text-[10px] font-mono text-success">{c.hash}</div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex gap-2"><button className="border border-white/10 px-3 py-2 rounded text-xs font-mono">Export signed log</button><button className="border border-white/10 px-3 py-2 rounded text-xs font-mono">Verify hashes</button></div>
        </div>
      )}

      {tab === "disk" && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 glass p-5 space-y-3">
            <div className="text-xs font-mono uppercase text-muted-foreground">DC01 — sda1 (NTFS, 512GB)</div>
            <div className="grid grid-cols-4 gap-2 text-[10px] font-mono">
              {Array.from({ length: 64 }).map((_, i) => {
                const state = i % 11 === 0 ? "bg-critical/60" : i % 5 === 0 ? "bg-warning/40" : i % 3 === 0 ? "bg-cyber/40" : "bg-white/5";
                return <div key={i} className={`h-8 rounded ${state} border border-white/5 grid place-items-center`}>{i.toString(16).padStart(2, "0")}</div>;
              })}
            </div>
            <div className="pt-3 border-t border-white/5 text-xs text-muted-foreground">Sector view — highlighted blocks contain deleted files, suspicious PE headers, and encrypted regions matching the LockBit signature.</div>
          </div>
          <div className="glass p-5 space-y-3">
            <div className="text-xs font-mono uppercase text-muted-foreground">Recovered artifacts</div>
            {[
              { name: "$MFT — 12,441 records", tag: "filesystem" },
              { name: "prefetch\\WINWORD.EXE-*.pf", tag: "execution" },
              { name: "USRCLASS.DAT — ShellBags", tag: "user-activity" },
              { name: "SYSTEM\\CurrentControlSet\\Services\\W_Update_Svc", tag: "persistence" },
              { name: "$Recycle.Bin\\S-1-5-21…\\$IE9F2A1.docm", tag: "deleted" },
            ].map((f, i) => (
              <div key={i} className="p-2.5 rounded bg-black/40 border border-white/5">
                <div className="text-xs font-mono text-cyber truncate">{f.name}</div>
                <div className="text-[10px] font-mono text-muted-foreground mt-1">#{f.tag}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "memory" && (
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="glass p-5">
            <div className="text-xs font-mono uppercase text-muted-foreground mb-3">Process tree — Volatility 3 (pslist)</div>
            <pre className="text-[11px] font-mono text-success leading-relaxed overflow-x-auto">{`PID   PPID  Name                State
─── ─── ──────────────────── ─────────
  4     0  System              Running
548     4  wininit.exe         Running
620   548  services.exe        Running
812   620  svchost.exe         Running
1204  812  W_Update_Svc.exe    Running  ← FLAGGED
1338 1204  powershell.exe      Running  ← ENC PAYLOAD
1442 1338  rundll32.exe        Running  ← INJECTED
1580  620  lsass.exe           Running  ← ACCESSED
`}</pre>
          </div>
          <div className="glass p-5 space-y-3">
            <div className="text-xs font-mono uppercase text-muted-foreground">Findings</div>
            {[
              { sev: "critical" as const, t: "malfind", d: "Injected code in rundll32.exe (VAD 0x7ff8a1c00000)" },
              { sev: "critical" as const, t: "lsass access", d: "Handle to LSASS from W_Update_Svc.exe — credential dump" },
              { sev: "high" as const, t: "netscan", d: "Beacon to 45.132.192.14:443 (Cobalt Strike heartbeat)" },
              { sev: "warning" as const, t: "hollowfind", d: "PE section mismatch in powershell.exe" },
            ].map((f, i) => (
              <div key={i} className="p-3 rounded bg-black/40 border border-white/5">
                <div className="flex items-center gap-2 mb-1"><SeverityBadge severity={f.sev} /><span className="text-xs font-mono text-cyber">{f.t}</span></div>
                <div className="text-xs">{f.d}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "timeline" && (
        <div className="glass p-5">
          <div className="text-xs font-mono uppercase text-muted-foreground mb-4">Reconstructed attack timeline — {active.id}</div>
          <div className="space-y-3">
            {TIMELINE.map((e, i) => (
              <div key={i} className="grid grid-cols-[80px_100px_1fr_auto] gap-3 items-center p-2 rounded hover:bg-white/5">
                <div className="font-mono text-[10px] text-cyber">{e.t}</div>
                <div className="font-mono text-[10px] text-muted-foreground">{e.ts}</div>
                <div className="text-sm">{e.ev}</div>
                <SeverityBadge severity={e.sev} />
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "sandbox" && (
        <div className="grid md:grid-cols-3 gap-4">
          <div className="glass p-5 md:col-span-1">
            <div className="text-xs font-mono uppercase text-muted-foreground">Sample</div>
            <div className="text-xs font-mono text-cyber mt-1 break-all">sha256:af13c8ee902…d94e</div>
            <div className="mt-3 text-sm">payslip_july.docm</div>
            <div className="mt-2 text-xs text-muted-foreground">Detonated in Windows 10 x64 sandbox — 3m 42s</div>
            <div className="mt-4 flex flex-col gap-2 text-xs">
              <div className="flex justify-between"><span>Verdict</span><span className="text-critical font-mono">MALICIOUS</span></div>
              <div className="flex justify-between"><span>Family</span><span className="text-cyber font-mono">LockBit 3.0</span></div>
              <div className="flex justify-between"><span>Score</span><span className="font-mono">96 / 100</span></div>
            </div>
          </div>
          <div className="glass p-5 md:col-span-2 space-y-3">
            <div className="text-xs font-mono uppercase text-muted-foreground">Behavior</div>
            {[
              "Drops file: %APPDATA%\\Microsoft\\Update\\svc.exe",
              "Registers scheduled task 'Windows_Update_Svc' running every 15 min",
              "Injects into rundll32.exe via APC queueing",
              "Beacons to 45.132.192.14:443 with encrypted heartbeat",
              "Enumerates domain via LDAP query (Kerberoasting)",
              "Deploys ransom note 'restore-my-files.txt' in all mounted drives",
            ].map((b, i) => (
              <div key={i} className="flex items-start gap-2 text-sm"><FileSignature className="h-4 w-4 text-critical shrink-0 mt-0.5" />{b}</div>
            ))}
            <button className="mt-4 text-xs font-mono text-cyber hover:underline inline-flex items-center gap-1"><ScrollText className="h-3.5 w-3.5" />Download full sandbox report (PDF)</button>
          </div>
        </div>
      )}
    </>
  );
}
